"""ゾーン並列(cpu-parallel Phase 0 / Phase 1)の計測ハーネス。

    python scripts/bench_zone_parallel.py gil       [--sizes 300,1000,3000] [--secs 2.0]
    python scripts/bench_zone_parallel.py gilphase  [--agents 400] [--warm 6] [--steps 2]
    python scripts/bench_zone_parallel.py zones     [--agents 400] [--steps 24]
    python scripts/bench_zone_parallel.py speedup   [--agents 400] [--steps 24]
    python scripts/bench_zone_parallel.py physbench [--agents 400] [--steps 24]

正典: docs/plans/cpu-parallel-plan.md §2(Phase 0 計測 / Phase 1 ゾーン間スレッド並列)。

**判断材料を出すだけで合否は判定しない**(この repo の他のベンチと同じ流儀)。

--- mode `gil`(Phase 0-1: 物理カーネルの GIL 解放割合)-------------------------
本体エンジン(`orca_core.OrcaCrowd` = スクランブル / `physics._CalibratedCrowd` =
ハチ公前・センター街)を実ゾーン相当の構成で作り、`engine.step(dt)` を回しながら
**2 通り**で解放割合を測る:

  A. カウンタ法 … 別スレッドで純 Python の空回しカウンタを走らせ、単独時 C0 に対する
     同時実行時 C1 の比 r = C1/C0 を測る。物理が GIL を握っている間はカウンタが
     進まない(最悪)〜半分進む(スイッチ間隔で分け合う)ので、解放割合 p は
     **2r−1 ≤ p ≤ r** に挟まれる。片側だけを断言しない。
  B. 複製法(**こちらが本命**)… 同じ仕事を 1 スレッドで 1 部 / K スレッドで K 部
     同時に流し、T_K/T_1 から p を解く。仕事の p の部分だけが重なると仮定すると
     T_K/T_1 = K − (K−1)·p → **p = (K − T_K/T_1)/(K − 1)**。
     Phase 1 の期待値そのもの(3 ゾーン = K=3)なので、この数字を採用する。

--- mode `gilphase`(Phase 0-1b: **本体 `physics.phase` の**解放割合)-----------
`gil` はカーネル(`engine.step`)だけを測る。実際に並列化するのは `_run_zone` 全体で、
そこには純 Python のループが混ざっている。**独立した Simulation を 4 つ**同じ状態に
置き、1 つを単独 / 3 つを 3 スレッドで回して T3/T1 から p を解く(sim 同士は
何も共有しないので、劣化の原因は GIL だけに絞られる)。

--- mode `physbench`(破綻統計 + 基本図の作業点を 0 / 3 で並べる)---------------
指標は `scripts/bench_physics_levers.py::_own_metrics` をそのまま呼ぶ(コピーを持たない)。

--- mode `zones`(Phase 0-2: ゾーン別負荷比 → Amdahl 上限)---------------------
`conf/zones_shibuya.yaml` の実 3 ゾーンを mock LLM で回し、`_run_zone` を包んで
**ゾーンごとの実測秒**を積む。並列の理論上限は 律速ゾーン で決まる:

    speedup_amdahl = Σ_z t_z / max_z t_z      (完全並列・オーバーヘッドゼロの上限)

--- mode `speedup`(Phase 1: 実装後のマイクロベンチ)---------------------------
同じ実 3 ゾーンのランを `physics.zone_threads=0`(逐次)と `=3`(並列)で回し、
`physics.phase` の実測秒 / step を比べる。**軌跡とログの一致判定は tests 側**
(tests/test_physics_zone_threads.py)。ここは速度だけを見る。
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import sys
import threading
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)
for _p in (_REPO, os.path.join(_REPO, "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from society import physics as P                              # noqa: E402
from society.world import orca_core                           # noqa: E402
from society.world.indoor_flow import body_radius, desired_speed  # noqa: E402

OWN_PROFILE = os.path.join(_REPO, "conf", "zones_shibuya.yaml")

# 実ゾーンの作業点(conf/zones_shibuya.yaml / finals_observe.yaml)
DT_SUB = 0.05
CAP = 12
FAR_KW = dict(far_a2=0.119, far_b2=1.890, far_cutoff_factor=2.5, far_taper_m=1.0)
CROSS_L = 29.0              # スクランブル相当の正方(840 m²)
CORR_W = 9.0                # センター街の実幅
CORR_L = 840.0 / CORR_W


# =========================================================================== #
# 合成ゾーン(本体エンジンそのもの。ベンチ専用の派生クラスは作らない)
# =========================================================================== #
def _lattice(n, w, h, margin=0.4):
    """格子の初期配置(乱数ゼロ・決定論)。bench_physics_levers.py と同一の作法。"""
    iw, ih = w - 2 * margin, h - 2 * margin
    cols = max(1, int(round(math.sqrt(n * iw / ih))))
    xs = margin + (np.arange(cols) + 0.5) * (iw / cols)
    rows = int(math.ceil(n / cols))
    ys = margin + (np.arange(rows) + 0.5) * (ih / rows)
    out = np.zeros((n, 2))
    for i in range(n):
        out[i] = (xs[i % cols], ys[i // cols])
    return out


def _params(n):
    v0 = np.array([desired_speed(i) for i in range(n)], dtype=np.float64)
    rad = np.array([body_radius(i) for i in range(n)], dtype=np.float64)
    return v0, rad


def make_orca(n):
    """スクランブル相当(ORCA・壁なし・4 方向交差流)。"""
    v0, radius = _params(n)
    pos = _lattice(n, CROSS_L, CROSS_L)
    dirs = np.array([[1.0, 0.0], [-1.0, 0.0], [0.0, 1.0], [0.0, -1.0]])
    e = dirs[np.arange(n) % 4].copy()
    return orca_core.OrcaCrowd(
        pos, e * v0[:, None], pos + e * 60.0, v0, radius, walls=(),
        neighbor_cap=CAP, tau=2.0, tau_obst=2.0, neighbor_dist=10.0,
        wall_range=2.0, v_max_factor=1.3, arrive_radius=1.0,
        pref_noise=0.0, rng=None, radius_margin=0.05, separation_iters=64)


def make_sfm(n):
    """センター街 / ハチ公前相当(SFM + 較正済み長距離項・両側に壁・対向流)。"""
    v0, radius = _params(n)
    pos = _lattice(n, CORR_L, CORR_W)
    e = np.zeros((n, 2))
    e[::2, 0] = 1.0
    e[1::2, 0] = -1.0
    walls = (((-10.0, 0.0), (CORR_L + 10.0, 0.0)),
             ((-10.0, CORR_W), (CORR_L + 10.0, CORR_W)))
    return P._CalibratedCrowd(
        pos, e * v0[:, None], pos + e * 60.0, v0, radius=radius, rng=None,
        noise=0.0, arrive_radius=1.0, walls=walls, wall_range=2.0,
        neighbor_cap=CAP, v_max_factor=1.3, **FAR_KW)


KERNELS = {"orca": make_orca, "sfm": make_sfm}


# =========================================================================== #
# mode gil
# =========================================================================== #
class _Counter:
    """純 Python の空回しカウンタ(GIL を握らないと 1 も進まない仕事)。"""

    def __init__(self):
        self.n = 0
        self._stop = threading.Event()
        self._t = None

    def _loop(self):
        n = 0
        stop = self._stop.is_set
        while not stop():
            for _ in range(1000):
                n += 1
            self.n = n

    def start(self):
        self._stop.clear()
        self.n = 0
        self._t = threading.Thread(target=self._loop, daemon=True)
        self._t.start()

    def stop(self):
        self._stop.set()
        self._t.join()
        return self.n


def _work(kind, n, k):
    """**毎回まっさらなエンジン**から k サブステップ。3 つの位相で 1 バイト同じ仕事。

    エンジンを作り直すのは、群衆の状態が進むとサブステップ単価が動く(密集→分散で
    近傍探索も分離パスも軽くなる)ためで、状態を持ち回ると「単独 1 部」と「同時 3 部」が
    **違う仕事**になってしまい比が意味を失う。構築費は 3 位相すべてに等しく乗る。
    """
    e = KERNELS[kind](n)
    for _ in range(k):
        e.step(DT_SUB)


def _calibrate_k(kind, n, secs):
    """1 部あたり `secs` 秒前後になるサブステップ数(下限 4・上限 400)。"""
    _work(kind, n, 2)                                      # ウォームアップ(import/確保)
    t0 = time.perf_counter()
    _work(kind, n, 4)
    one = (time.perf_counter() - t0) / 4.0
    return int(min(400, max(4, secs / max(one, 1e-9))))


def gil_probe(kind, n, secs):
    k = _calibrate_k(kind, n, secs)

    # ---- 単独実行(基準)----
    t0 = time.perf_counter()
    _work(kind, n, k)
    t1 = time.perf_counter() - t0

    # ---- A. カウンタ法 ----
    c = _Counter()
    c.start()
    time.sleep(0.30)
    c0 = c.stop() / 0.30                                   # 単独カウンタ速度 [回/s]
    c = _Counter()
    c.start()
    t0 = time.perf_counter()
    _work(kind, n, k)
    t_cnt = time.perf_counter() - t0
    c1 = c.stop() / t_cnt
    r = c1 / c0 if c0 else float("nan")

    # ---- B. 複製法(K = 3 ゾーン)----
    ths = [threading.Thread(target=_work, args=(kind, n, k)) for _ in range(3)]
    t0 = time.perf_counter()
    for t in ths:
        t.start()
    for t in ths:
        t.join()
    t3 = time.perf_counter() - t0
    ratio = t3 / t1
    p_rep = (3.0 - ratio) / 2.0                            # T_K/T_1 = K −(K−1)p

    return {
        "kernel": kind, "n": n, "substeps": k,
        "solo_s": round(t1, 4),
        "ms_per_substep": round(1000.0 * t1 / k, 4),
        "counter_ratio_r": round(r, 4),
        "gil_free_lo_2r_minus_1": round(max(0.0, 2 * r - 1), 4),
        "gil_free_hi_r": round(min(1.0, r), 4),
        "rep_t1_s": round(t1, 4), "rep_t3_s": round(t3, 4),
        "rep_t3_over_t1": round(ratio, 4),
        "rep_speedup_x": round(3.0 / ratio, 4),
        "gil_free_p_replication": round(max(0.0, min(1.0, p_rep)), 4),
    }


def mode_gil(args):
    sizes = [int(s) for s in args.sizes.split(",") if s.strip()]
    rows = []
    for kind in ("orca", "sfm"):
        for n in sizes:
            r = gil_probe(kind, n, args.secs)
            rows.append(r)
            print(f"  {kind:5s} n={n:5d} substep={r['ms_per_substep']:8.3f} ms "
                  f"| counter r={r['counter_ratio_r']:.3f} "
                  f"(p in [{r['gil_free_lo_2r_minus_1']:.2f},"
                  f"{r['gil_free_hi_r']:.2f}]) "
                  f"| rep T3/T1={r['rep_t3_over_t1']:.3f} "
                  f"speedup={r['rep_speedup_x']:.3f}x "
                  f"p={r['gil_free_p_replication']:.3f}", flush=True)
    return rows


# =========================================================================== #
# 実 3 ゾーンのラン(zones / speedup 共通)
# =========================================================================== #
def build_sim(n, steps, seed=42, dots=(), name="zp"):
    from society.config import load_config
    from society.engine.simulation import Simulation
    cfg = load_config([f"run.seed={seed}", f"run.n_agents={n}",
                       f"run.n_steps={steps}", f"run.name={name}",
                       "model.backend=mock", "observer.snapshot_every=100000"]
                      + list(dots), profile=OWN_PROFILE)
    return Simulation(cfg, out_dir=os.path.join(_REPO, "experiments",
                                                "_zone_parallel", name))


def run_steps(sim, steps, per_zone=None, phase_box=None):
    from society.engine import scheduler
    real_zone = P._run_zone
    real_phase = P.phase

    def timed_zone(s, zone, step, sim_min, st, ordered=None):
        t = time.perf_counter()
        try:
            return real_zone(s, zone, step, sim_min, st, ordered)
        finally:
            if per_zone is not None:
                per_zone[zone.id] = per_zone.get(zone.id, 0.0) + (
                    time.perf_counter() - t)

    def timed_phase(s, step, sim_min):
        t = time.perf_counter()
        try:
            return real_phase(s, step, sim_min)
        finally:
            if phase_box is not None:
                phase_box["s"] += time.perf_counter() - t

    if per_zone is not None:
        P._run_zone = timed_zone
    if phase_box is not None:
        P.phase = timed_phase
    try:
        t0 = time.perf_counter()
        for step in range(steps):
            scheduler.run_step(sim, step)
        return time.perf_counter() - t0
    finally:
        P._run_zone = real_zone
        P.phase = real_phase


def _time_engine_steps(box):
    """`engine.step()`(= numpy カーネル本体)の実測秒を積む。返り値は復元用の callable。

    `_run_zone` のうち**どれだけがカーネルか**を出すため。カーネルの外側は
    `_advance_and_collect` / `_admit` / `_accumulate` の純 Python(= GIL を握る)なので、
    ここの比がスレッド並列の上限をカーネルの p より厳しく縛る。
    """
    from society.world import orca_core as _oc, sfm_core as _sc
    targets = [(_sc.Crowd, "step"), (_oc.OrcaCrowd, "step"),
               (P._CalibratedCrowd, "step")]
    saved = []
    for cls, name in targets:
        if name not in cls.__dict__:          # 継承しているだけなら張らない(二重計上防止)
            continue
        real = cls.__dict__[name]
        saved.append((cls, name, real))

        def wrap(self, *a, __real=real, **kw):
            t = time.perf_counter()
            try:
                return __real(self, *a, **kw)
            finally:
                box["kernel_s"] += time.perf_counter() - t
        setattr(cls, name, wrap)

    def restore():
        for cls, name, real in saved:
            setattr(cls, name, real)
    return restore


def mode_zones(args):
    per_zone: dict = {}
    box = {"s": 0.0, "kernel_s": 0.0}
    sim = build_sim(args.agents, args.steps, name="zones")
    restore = _time_engine_steps(box)
    try:
        wall = run_steps(sim, args.steps, per_zone=per_zone, phase_box=box)
    finally:
        restore()
    tot = sum(per_zone.values()) or 1e-12
    top = max(per_zone.values()) if per_zone else 0.0
    rows = [{"zone": z, "s": round(v, 4), "share": round(v / tot, 4),
             "s_per_step": round(v / args.steps, 5)}
            for z, v in sorted(per_zone.items(), key=lambda kv: -kv[1])]
    for r in rows:
        print(f"  {r['zone']:16s} {r['s']:8.3f} s  share={r['share']:6.2%}  "
              f"{r['s_per_step'] * 1000:8.2f} ms/step", flush=True)
    out = {
        "agents": args.agents, "steps": args.steps,
        "wall_s": round(wall, 3),
        "phase_s": round(box["s"], 3),
        "zone_s_total": round(tot, 4),
        "zone_share": rows,
        "amdahl_speedup_x": round(tot / top, 4) if top else None,
        "phase_overhead_s": round(box["s"] - tot, 4),
        "kernel_s": round(box["kernel_s"], 3),
        "kernel_share_of_phase": (round(box["kernel_s"] / box["s"], 4)
                                  if box["s"] else None),
    }
    print(f"  -> Amdahl 上限 = {out['amdahl_speedup_x']}x "
          f"(phase={out['phase_s']}s / zones={out['zone_s_total']}s / "
          f"wall={out['wall_s']}s)", flush=True)
    print(f"  -> engine.step(numpy カーネル)= {out['kernel_s']}s "
          f"= physics.phase の {out['kernel_share_of_phase']} "
          f"(残りは純 Python = GIL を握る)", flush=True)
    return out


def mode_speedup(args):
    """★正直な但し書き: `zone_threads=3` は**軌跡が分岐する**(tests/test_physics_zone_threads.py)。

    分岐すると「入場した個体数 = 積分すべき仕事量」まで変わるので、素の秒数比は
    speedup ではなく「別の仕事をした 2 ラン」の比になってしまう。そこで
    `continuity()["sub_steps_total"]`(= 積分したサブステップの総数)で割った
    **仕事量あたりの秒**も並べて出す。どちらの数字も報告する。
    """
    out = {}
    for label, dots in (("seq(0)", []),
                        ("par(3)", ["physics.zone_threads=3"])):
        box = {"s": 0.0}
        sim = build_sim(args.agents, args.steps, dots=dots,
                        name=f"sp_{label.split('(')[0]}")
        wall = run_steps(sim, args.steps, phase_box=box)
        cont = P.continuity(sim) or {}
        subs = int(cont.get("sub_steps_total") or 0)
        out[label] = {"phase_s": round(box["s"], 4),
                      "phase_ms_per_step": round(1000.0 * box["s"] / args.steps, 3),
                      "wall_s": round(wall, 3),
                      "sub_steps_total": subs,
                      "us_per_substep": (round(1e6 * box["s"] / subs, 2)
                                         if subs else None)}
        print(f"  {label:8s} phase={out[label]['phase_ms_per_step']:9.2f} ms/step "
              f"wall={wall:8.2f} s sub_steps={subs} "
              f"({out[label]['us_per_substep']} us/substep)", flush=True)
    a, b = out["seq(0)"]["phase_s"], out["par(3)"]["phase_s"]
    out["phase_speedup_raw_x"] = round(a / b, 4) if b else None
    ua = out["seq(0)"]["us_per_substep"]
    ub = out["par(3)"]["us_per_substep"]
    out["phase_speedup_per_substep_x"] = (round(ua / ub, 4) if (ua and ub) else None)
    print(f"  -> physics.phase speedup raw={out['phase_speedup_raw_x']}x / "
          f"仕事量あたり={out['phase_speedup_per_substep_x']}x", flush=True)
    return out


def mode_gilphase(args):
    """★Phase 0 の本命: **本体の `physics.phase` そのもの**の GIL 解放割合。

    `gil` モードが測るのは `engine.step()` = 物理カーネル**だけ**。実際に並列化するのは
    `_run_zone` 全体で、そこには純 Python のループ(`_advance_and_collect` の在場者走査・
    `_admit` の占有判定・`_accumulate` の個体別集計・ORCA `separate_positions` の
    ペア解消)が混ざっている。だからカーネルの p と `_run_zone` の p は別物である。

    測り方(共有状態を 1 バイトも持たない = 正しさの問題を完全に切り離す):
      同一 conf・同一 seed の **独立した Simulation を 4 つ**作り、同じ回数だけ暖機して
      まったく同じ状態に置く。1 つを単独で K step 回して T1、残り 3 つを 3 スレッドで
      同時に K step 回して T3。sim 同士は何も共有しないので、T3/T1 の劣化は
      **GIL(と割り込み)だけ**が原因になる。p = (3 − T3/T1)/2。
    """
    from society.engine import scheduler

    n_sim, warm, k = 4, args.warm, args.steps
    sims = [build_sim(args.agents, warm + k, name=f"gp{i}") for i in range(n_sim)]
    for i, s in enumerate(sims):                      # 暖機(4 つを同じ状態へ)
        for step in range(warm):
            scheduler.run_step(s, step)
        print(f"  warmed sim{i}", flush=True)

    def phase_loop(s):
        for step in range(warm, warm + k):
            P.phase(s, step, step * int(s.clock.step_seconds) // 60)

    t0 = time.perf_counter()
    phase_loop(sims[0])
    t1 = time.perf_counter() - t0
    ths = [threading.Thread(target=phase_loop, args=(s,)) for s in sims[1:]]
    t0 = time.perf_counter()
    for t in ths:
        t.start()
    for t in ths:
        t.join()
    t3 = time.perf_counter() - t0
    ratio = t3 / t1
    out = {"agents": args.agents, "warm": warm, "k": k,
           "t1_s": round(t1, 3), "t3_s": round(t3, 3),
           "t3_over_t1": round(ratio, 4),
           "speedup_x": round(3.0 / ratio, 4),
           "gil_free_p": round(max(0.0, min(1.0, (3.0 - ratio) / 2.0)), 4)}
    print(f"  phase(独立 sim ×3): T1={t1:.2f}s T3={t3:.2f}s T3/T1={ratio:.3f} "
          f"speedup={out['speedup_x']:.3f}x p={out['gil_free_p']:.3f}", flush=True)
    return out


def mode_physbench(args):
    """破綻統計 + 基本図の作業点を `zone_threads=0 / 3` で並べる(判定はしない)。

    指標の定義と抽出は `scripts/bench_physics_levers.py::_own_metrics` を**そのまま呼ぶ**
    (コピーを持たない = ベンチ同士が食い違いようがない)。
    ★ zone_threads=3 は軌跡が分岐するので、これは「同じ世界の前後比較」ではなく
      **「並列で走らせた世界も物理として破綻していないか」**の確認である。
    """
    sys.path.insert(0, _HERE)
    from bench_physics_levers import _own_metrics                     # noqa: E402

    rows = {}
    for label, dots in (("seq0", []), ("par3", ["physics.zone_threads=3"])):
        per_zone: dict = {}
        box = {"s": 0.0}
        sim = build_sim(args.agents, args.steps, dots=dots, name=f"pb_{label}")
        wall = run_steps(sim, args.steps, per_zone=None, phase_box=box)
        for zid, z in (getattr(sim, "_phys_state", None) or {}).get("by_zone", {}).items():
            per_zone.setdefault(zid, {"occ": [], "dens": [], "wait": [], "sub": []})
            per_zone[zid]["occ"].append(float(z["occupancy_mean"]))
            per_zone[zid]["dens"].append(float(z["density"]))
            per_zone[zid]["wait"].append(int(z["waiting"]))
            per_zone[zid]["sub"].append(int(z["sub_steps"]))
        m = _own_metrics(sim, box["s"], wall, per_zone, args.steps)
        m.pop("_final_xy", None)
        m.pop("_exit_step", None)
        rows[label] = m
    keys = ("min_gap_m", "jump_max_m", "handover_jump_max_m", "gate_accel_p99",
            "interior_accel_p99", "gate_reversal_rate", "interior_reversal_rate",
            "sep_iters_max", "body_speed_mean", "body_density_mean",
            "body_density_max", "v_eff_mean", "enter_total", "exit_total",
            "zone_dwell_mean_s", "sub_steps_total", "physics_s_per_step")
    print(f"  {'指標':24s} {'seq0':>14s} {'par3':>14s}", flush=True)
    for k in keys:
        print(f"  {k:24s} {str(rows['seq0'].get(k)):>14s} "
              f"{str(rows['par3'].get(k)):>14s}", flush=True)
    return rows


# =========================================================================== #
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=("gil", "gilphase", "zones", "speedup",
                                     "physbench"))
    ap.add_argument("--warm", type=int, default=6)
    ap.add_argument("--sizes", default="300,1000,3000")
    ap.add_argument("--secs", type=float, default=2.0)
    ap.add_argument("--agents", type=int, default=3000)
    ap.add_argument("--steps", type=int, default=24)
    ap.add_argument("--out", default=os.path.join(_REPO, "experiments",
                                                  "_zone_parallel"))
    args = ap.parse_args(argv)

    env = {"python": platform.python_version(), "numpy": np.__version__,
           "cpu_count": os.cpu_count(),
           "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS"),
           "switch_interval_s": sys.getswitchinterval()}
    print(f"[env] {env}", flush=True)
    res = {"gil": mode_gil, "gilphase": mode_gilphase, "zones": mode_zones,
           "speedup": mode_speedup, "physbench": mode_physbench}[args.mode](args)
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, f"{args.mode}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"env": env, "mode": args.mode, "result": res}, fh,
                  ensure_ascii=False, indent=2)
    print(f"[out] {path}", flush=True)


if __name__ == "__main__":
    main()
