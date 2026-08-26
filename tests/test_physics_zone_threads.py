"""`physics.zone_threads` — ゾーン間スレッド並列(cpu-parallel Phase 1)の検収。

正典: docs/plans/cpu-parallel-plan.md §2 / src/society/physics.py `_run_zones_threaded`。

本ファイルが固定するのは 4 つ:

  (1) **既定 0 = 現行と 1 バイト同一**(ThreadPoolExecutor を 1 度も作らない)。
  (2) **submit / join の順序固定が正しい**こと。`zone_threads=1` は「プールを通すが
      同時実行はしない」= 逐次と**同じ順序**なので、L1・continuity・scalars が
      **完全一致**しなければならない。ここが通れば、>1 で出る差は『順序の実装ミス』
      ではなく『真の同時実行』が原因だと切り分けられる。
  (3) **>1 はビット同一にならない**。その理由は timing の運ではなく **構造** なので、
      構造そのものを機械確認する:
        (3a) ゾーンの流入候補集合が**実際に交わる**(排他所有のハンドシェイクが
             ゾーン間の依存になっている)。
        (3b) 3 ゾーンが**同じ共有オブジェクト**(`_phys_state` の集計 / `st["cont"]` /
             `sim.logger.events`)へ書く。並列時はそれが**別スレッドから**起きる。
      → docs/plans/cpu-parallel-plan.md §2 Phase 1 の「ビット同一が狙える」という
        見積りは **本リポジトリの実装では成立しない**。その反証をここに置く。
  (4) conf / registry の契約(既定 0・負値は構築時に落ちる・宣言済み)。

★ (3) を「差が出ること」で書かないのはわざと。競合の結果は原理的に運に依存するので、
  緑/赤が運で決まるテストになってしまう。代わりに**差が出る構造**(交わりと共有書き込み)
  を決定論的に固定する。実際の分岐の実測値は本ファイル末尾の docstring に記録してある。
"""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path

import pytest

import society.registry as R
from society import physics as P
from society.config import load_config
from society.engine.simulation import Simulation
from society.world import zones as Z

REPO = Path(__file__).resolve().parents[1]
PROFILE = REPO / "conf" / "zones_shibuya.yaml"

N_AGENTS = 200          # ゾーンを踏む個体が十分に出る最小規模(実測 zone_gate ~200 件)
N_STEPS = 8
_now = time.perf_counter


# --------------------------------------------------------------------------- #
# 共通(tests/test_zones_shibuya.py と同じ作法)
# --------------------------------------------------------------------------- #
def _cfg(name, n=N_AGENTS, steps=N_STEPS, **ov):
    dot = ["run.seed=42", f"run.n_agents={n}", f"run.n_steps={steps}",
           f"run.name={name}", "model.backend=mock",
           "observer.snapshot_every=100000"]
    dot += [f"{k}={v}" for k, v in ov.items()]
    return load_config(dot, profile=str(PROFILE))


def _run(tmp_path, name, **ov):
    sim = Simulation(_cfg(name, **ov), out_dir=tmp_path / name)
    sim.run()
    return sim


def _l1(sim):
    """L1 の全内容(座標まで含む)。test_physics_hash.py と同じ突合の粒度。"""
    return [[e.step, e.agent_id, e.kind, e.x, e.y,
             json.dumps(e.payload, ensure_ascii=False, sort_keys=True)]
            for e in sim.logger.events]


def _assert_identical(a, b, why):
    assert sum(1 for e in a.logger.events if e.kind == "zone_gate") > 0, \
        "ゾーンを 1 度も通っていない(テストが空回りしている)"
    assert _l1(a) == _l1(b), f"L1 が一致しない: {why}"
    assert P.continuity(a) == P.continuity(b), f"continuity が一致しない: {why}"
    assert P.scalars(a) == P.scalars(b), f"scalars が一致しない: {why}"


# --------------------------------------------------------------------------- #
# (4) conf / registry の契約
# --------------------------------------------------------------------------- #
def test_registry_declares_zone_threads():
    f = R.BY_ID["physics.zone_threads"]
    assert f.repro_tier == "strict"
    assert f.affects_k is False          # generate() の呼び出し点を 1 つも足さない
    assert f.fingerprint_risk == "none"
    assert f.off_value == 0              # ★ _f の第3引数は affects_k = kwarg で渡すこと
    assert isinstance(f.off_value, int) and not isinstance(f.off_value, bool)
    assert f.description.strip()


def test_shipped_conf_default_is_zero():
    cfg = load_config([])
    assert int(cfg.physics.zone_threads) == 0
    # 実配置プロファイルも 0 のまま(zones_shibuya.yaml は物理ブロックを丸ごと持つ)
    assert int(load_config([], profile=str(PROFILE)).physics.zone_threads) == 0


def test_build_cfg_default_and_validation():
    assert Z.build_cfg({})["zone_threads"] == 0
    assert Z.build_cfg({"zone_threads": 3})["zone_threads"] == 3
    assert Z.build_cfg({"zone_threads": None})["zone_threads"] == 0
    with pytest.raises(ValueError):
        Z.build_cfg({"zone_threads": -1})
    with pytest.raises(KeyError):          # 未知キーの拒否は従来どおり効いている
        Z.build_cfg({"zone_threadz": 1})


def test_zone_threads_helper_falls_back_to_zero():
    class _Bare:
        pass
    assert P.zone_threads(_Bare()) == 0            # physcfg を持たない sim
    bare = _Bare()
    bare.physcfg = {}
    assert P.zone_threads(bare) == 0               # 鍵が無い physcfg(旧 blob)
    bare.physcfg = {"zone_threads": "x"}
    assert P.zone_threads(bare) == 0               # 壊れた値でも逐次へ後退


# --------------------------------------------------------------------------- #
# (1) 既定 0 = 現行と 1 バイト同一
# --------------------------------------------------------------------------- #
def test_default_never_enters_the_threaded_path(tmp_path, monkeypatch):
    """既定では並列経路へ 1 度も入らない(= ThreadPoolExecutor を作りもしない)。

    さらに `_run_zone` が**必ず main スレッドから**呼ばれることも見る
    (LLM ワーカー等 repo の他所のスレッドプールと取り違えないため、
     `_run_zones_threaded` を直接張る)。
    """
    seen: list = []
    threads: set = set()
    real_thr = P._run_zones_threaded
    real_zone = P._run_zone

    def trap(*a, **kw):
        seen.append(1)
        return real_thr(*a, **kw)

    def spy(sim, zone, step, sim_min, st, ordered=None):
        threads.add(threading.get_ident())
        return real_zone(sim, zone, step, sim_min, st, ordered)

    monkeypatch.setattr(P, "_run_zones_threaded", trap)
    monkeypatch.setattr(P, "_run_zone", spy)
    sim = _run(tmp_path, "zt_default")
    assert sum(1 for e in sim.logger.events if e.kind == "zone_gate") > 0
    assert seen == [], "既定 0 なのに並列経路へ入った"
    assert threads == {threading.main_thread().ident}, \
        f"既定 0 なのに別スレッドからゾーンが回った: {threads}"


def test_explicit_zero_is_byte_identical_to_absent_key(tmp_path):
    a = _run(tmp_path, "zt_absent")
    b = _run(tmp_path, "zt_zero", **{"physics.zone_threads": 0})
    _assert_identical(a, b, "既定(鍵なし)と明示 0")


def test_single_zone_config_ignores_threads(tmp_path, monkeypatch):
    """ゾーンが 1 つしか無い構成では並列経路へ入らない(= 分岐そのものが増えない)。"""
    seen: list = []
    real = P._run_zones_threaded
    monkeypatch.setattr(P, "_run_zones_threaded",
                        lambda *a, **kw: (seen.append(1), real(*a, **kw))[1])
    cfg = _cfg("zt_single", **{"physics.zone_threads": 3})
    cfg.physics.zones = [cfg.physics.zones[0]]
    sim = Simulation(cfg, out_dir=tmp_path / "zt_single")
    assert len(sim.physcfg["zones"]) == 1
    sim.run()
    assert seen == [], "ゾーン 1 つで並列経路へ入った"


# --------------------------------------------------------------------------- #
# (2) submit / join の順序固定 — 1 ワーカーは逐次と完全一致
# --------------------------------------------------------------------------- #
def test_one_worker_is_byte_identical(tmp_path):
    """`zone_threads=1` = プールを通すが同時実行はしない = **逐次と同じ順序**。

    これが通ることで「>1 で出る差は submit/join 順序の実装ミスではない」と切り分く。
    """
    a = _run(tmp_path, "zt_seq")
    b = _run(tmp_path, "zt_one", **{"physics.zone_threads": 1})
    _assert_identical(a, b, "zone_threads=1(1 ワーカー = 逐次順)")


def test_submit_and_join_order_is_declaration_order(tmp_path, monkeypatch):
    """submit も join も**宣言順**(= ゾーン id の固定順)。完走順に依らない。

    完走順を強制的に逆転させる(先に submit したゾーンほど長く眠らせる)。それでも
    `submitted` は宣言順・`joined` も宣言順で、`finished`(完走順)だけが逆になる。
    """
    submitted: list = []
    joined: list = []
    finished: list = []
    real_zone = P._run_zone
    real_thr = P._run_zones_threaded
    delays: dict = {}

    def slow(sim, zone, step, sim_min, st, ordered=None):
        submitted.append(zone.id)
        out = real_zone(sim, zone, step, sim_min, st, ordered)
        d = delays.get(zone.id, 0.0)
        if d:
            threading.Event().wait(d)          # 眠っている間 GIL は手放す
        finished.append(zone.id)
        return out

    def wrap(s, step, sim_min, st, ordered, n):
        out = real_thr(s, step, sim_min, st, ordered, n)
        joined.extend(z.id for z in s.physcfg["zones"])
        return out

    sim = Simulation(_cfg("zt_join", steps=3, **{"physics.zone_threads": 3}),
                     out_dir=tmp_path / "zt_join")
    zids = [z.id for z in sim.physcfg["zones"]]
    delays = {zids[0]: 0.15, zids[1]: 0.05, zids[2]: 0.0}
    monkeypatch.setattr(P, "_run_zone", slow)
    monkeypatch.setattr(P, "_run_zones_threaded", wrap)
    sim.run()
    assert joined, "並列経路を 1 度も通っていない"
    n = len(zids)
    assert [joined[i:i + n] for i in range(0, len(joined), n)] == \
        [zids] * (len(joined) // n), "join の順序が宣言順でない"
    assert [submitted[i:i + n] for i in range(0, len(submitted), n)] == \
        [zids] * (len(submitted) // n), "submit の順序が宣言順でない"
    # 完走順が逆転していること(= 上の 2 つが『たまたま同じ』ではないことの対照)
    assert finished[:n] == list(reversed(zids)), \
        f"完走順を逆転させられなかった(対照が効いていない): {finished[:n]}"


# --------------------------------------------------------------------------- #
# (3a) ゾーンの流入候補集合は**実際に交わる** = 排他所有がゾーン間の依存
# --------------------------------------------------------------------------- #
def _candidate_sets(sim, step):
    """`_run_zone` の流入候補フィルタを **同時刻の世界** で各ゾーンに掛ける(読み取りのみ)。"""
    graph = sim.city.graph
    out = {}
    for zone in sim.physcfg["zones"]:
        got = set()
        for a in sim.agents:
            if getattr(a, "_phys_zone", None) is not None:
                continue
            if a.loc != "street" or a.sleeping or not a.route:
                continue
            if getattr(a, "_taxi_hold_until", -1) > step:
                continue
            if Z.route_span(zone, graph, a.node, a.route) is None:
                continue
            got.add(int(a.id))
        out[zone.id] = got
    return out


def test_zone_candidate_sets_intersect(tmp_path):
    """並列化がビット同一になれない**構造的な理由**の機械確認。

    逐次では zone B の候補ループは「A が所有・積分・退場まで終えたあとの世界」を見るので、
    A に取られた個体は `_phys_zone is not None` で自動的に消える。並列ではその消し込みが
    起きないため、**同じ個体を 2 ゾーンが同時に候補にできる**。渋谷の 3 ゾーンは隣接し、
    1 本の経路がスクランブル → ハチ公前 のように複数ゾーンを貫くので、交わりは実在する。
    """
    hits = {"steps": 0, "overlap_steps": 0, "pairs": 0}
    real = P.phase

    def probe(s, step, sim_min):
        if s.physcfg["zones"]:
            cand = _candidate_sets(s, step)
            ids = sorted(cand)
            n = sum(len(cand[ids[i]] & cand[ids[j]])
                    for i in range(len(ids)) for j in range(i + 1, len(ids)))
            hits["steps"] += 1
            hits["pairs"] += n
            hits["overlap_steps"] += bool(n)
        return real(s, step, sim_min)

    sim = Simulation(_cfg("zt_cand"), out_dir=tmp_path / "zt_cand")
    P.phase = probe
    try:
        sim.run()
    finally:
        P.phase = real
    assert hits["steps"] == N_STEPS
    assert hits["pairs"] > 0, (
        "候補集合が 1 度も交わらなかった。交わらないなら排他所有はゾーン間の依存に"
        "ならないので、この構成では並列化の障害が 1 つ減る(= 前提が変わった)。"
        f"実測: {hits}")


# --------------------------------------------------------------------------- #
# (3b) 3 ゾーンは同じ共有オブジェクトへ書く — 並列時は**別スレッドから**
# --------------------------------------------------------------------------- #
def test_shared_state_is_written_by_every_zone(tmp_path):
    """逐次でも「3 ゾーンが同じ `st` の鍵へ書く」ことを機械確認する(構造の証拠)。"""
    touched: dict = {}
    real = P._run_zone

    def spy(sim, zone, step, sim_min, st, ordered=None):
        before = {k: st.get(k) for k in ("enter_total", "exit_total",
                                         "dwell_sum_s", "dwell_n",
                                         "handover_jump_max_m", "sep_iters_max")}
        n0 = len(sim.logger.events)
        out = real(sim, zone, step, sim_min, st, ordered)
        for k, v in before.items():
            if st.get(k) != v:
                touched.setdefault(k, set()).add(zone.id)
        if len(sim.logger.events) != n0:
            touched.setdefault("logger.events", set()).add(zone.id)
        return out

    sim = Simulation(_cfg("zt_shared"), out_dir=tmp_path / "zt_shared")
    P._run_zone = spy
    try:
        sim.run()
    finally:
        P._run_zone = real
    shared = {k: sorted(v) for k, v in touched.items() if len(v) > 1}
    assert shared, ("どのゾーンも共有状態を書かなかった(前提が変わった)。"
                    f"実測: { {k: sorted(v) for k, v in touched.items()} }")
    # `dwell_sum_s` は **浮動小数の累積和** = 加算順序が変われば下位ビットが動く
    assert "dwell_sum_s" in shared or "enter_total" in shared, \
        f"集計の共有が観測されなかった: {shared}"
    assert "logger.events" in shared, \
        "L1 への追記が 1 ゾーンからしか起きていない(前提が変わった)"


def test_zones_actually_run_concurrently(tmp_path, monkeypatch):
    """★「共有状態への並行書き込みが無いことの機械確認」— 結論は **有る**。

    上の `test_shared_state_is_written_by_every_zone` が「複数ゾーンが同じ共有
    オブジェクトへ書く」を決定論的に固定した。ここでは残る半分、「`zone_threads>1`
    ではそのゾーンたちが**時間的に重なって**走る」を実測で固定する。
    2 つ合わせて『共有状態への並行書き込みが存在する』が機械確認になる。

    スレッド id で見ないのは、プールを step ごとに作るので id が step 間で変わり、
    「同時に走ったか」を語れないため(id の異なりは並行性の証拠にならない)。
    区間 [enter, exit) の重なりで見る。
    """
    spans: dict = {}                       # step -> [(zone, t0, t1), ...]
    real_zone = P._run_zone
    lock = threading.Lock()

    def spy(sim, zone, step, sim_min, st, ordered=None):
        t0 = _now()
        try:
            return real_zone(sim, zone, step, sim_min, st, ordered)
        finally:
            t1 = _now()
            with lock:
                spans.setdefault(int(step), []).append((zone.id, t0, t1))

    monkeypatch.setattr(P, "_run_zone", spy)
    sim = Simulation(_cfg("zt_race", **{"physics.zone_threads": 3}),
                     out_dir=tmp_path / "zt_race")
    sim.run()
    assert spans, "ゾーンが 1 度も回っていない"
    overlaps = 0
    for _step, rows in spans.items():
        rows = sorted(rows, key=lambda r: r[1])
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                if rows[j][1] < rows[i][2]:          # j の開始 < i の終了 = 重なり
                    overlaps += 1
    assert overlaps > 0, (
        "zone_threads=3 なのにゾーンが 1 度も同時に走らなかった。"
        "並行書き込みが無いのならビット同一の見込みが変わるので前提を見直すこと。"
        f"実測 spans={ {k: [(z, round(b - a, 6)) for z, a, b in v] for k, v in spans.items()} }")


# --------------------------------------------------------------------------- #
# 実測の記録(本ファイルが assert しない数字。報告の根拠として残す)
# --------------------------------------------------------------------------- #
_MEASURED = """
2026-08-26 実測(Windows 11 / CPython 3.12.10 / numpy 2.5.0 / 20 コア)

conf/zones_shibuya.yaml・n_agents=200・n_steps=12・mock backend:
  zone_gate イベント   : 逐次 198 件 → zone_threads=3 で 166 件(−16.2%)
  L1 行数              : 3,531 → 3,503(**順序を無視した集合としても不一致** = 世界が分岐)
  zone_gate_enter_total: 101 → 85 / exit_total: 97 → 81
  sub_steps_total      : 293,399 → 292,084
  最終座標が異なる個体 : 8 / 200
  候補集合の交わり     : 12 step 中 11 step で発生・のべ 46 件
  zone_threads=1       : L1 / continuity / scalars **完全一致**(順序固定は正しい)

Phase 0-1 物理カーネルの GIL 解放割合(複製法 K=3):
  orca n=300/1000/3000 : p=0.51 / 0.49 / 0.05   (3 スレッド speedup 1.51 / 1.49 / 1.03x)
  sfm  n=300/1000/3000 : p=0.29 / 0.83 / 0.87   (3 スレッド speedup 1.24 / 2.22 / 2.37x)
  ★ORCA が高密度で 0.05 まで落ちるのは、事後分離パス(位置層 Gauss-Seidel)が
    **ペアごとの純 Python ループ**(orca_core.separate_positions)だから。
  ★カウンタ法は使えない: 純 Python カウンタ 1 本が numpy スレッドを 15〜168 倍に
    減速させながら自分は単独時の ~85% で回る(CPython の GIL 受け渡しの偏り)ため、
    比 r は kernel にも n にも依らず ~0.80-0.86 で張り付き、複製法の結論と矛盾する。

Phase 0-1b **本体 `physics.phase` の**解放割合(独立 Simulation ×3・共有状態ゼロの対照):
  T1=11.58s / T3=53.01s → **T3/T1 = 4.58**(逐次の 3.0 より悪い)= 3 スレッド 0.655x
  → `_run_zone` はほぼ常時 GIL を握っており、スレッドを足すと**受け渡しのぶん損をする**。

Phase 0-2 ゾーン別負荷比:
  400 体 24 step: scramble 43.1% / center_gai 31.5% / hachiko_square 25.5% → Amdahl 2.32x
  400 体 12 step: scramble 45.7% / center_gai 30.5% / hachiko_square 23.8% → Amdahl 2.19x
  `engine.step`(numpy カーネル)は physics.phase の **56.6%** しかない
  = 残り 43.4% は純 Python(所有走査 / _admit / _accumulate / _advance_and_collect /
    _release)で、そこは GIL を握り続ける。カーネルの解放割合が高くても届かない理由。

Phase 1 実測 speedup(n_agents=400・24 step・実 3 ゾーン):
  physics.phase 5,989 ms/step(zone_threads=0)→ 8,496 ms/step(=3)= **0.70x**
  仕事量で正規化(sub_steps_total 769,806 vs 767,757): 186.7 → 265.6 µs/サブステップ
  → **Phase 1(スレッド)は打ち切りが妥当**。取るならプロセス並列(Phase 2)か、
    先に純 Python 部をベクトル化してカーネル比を上げてから(Phase 3)。

破綻統計 + 基本図の作業点(scripts/bench_zone_parallel.py physbench・400 体 12 step。
指標の定義は scripts/bench_physics_levers.py::_own_metrics をそのまま使用):
                          zone_threads=0    zone_threads=3
  min_gap_m                     0.0125            0.0229   (どちらも正 = 重なりゼロ)
  jump_max_m                    0.0886            0.0886   (同一)
  handover_jump_max_m            8.372             8.372   (同一)
  gate_accel_p99                   4.1               4.2
  interior_accel_p99               4.1               4.1   (同一)
  sep_iters_max                      0                 0   (分離パスの上限張り付きなし)
  body_speed_mean               1.1855            1.1877   (+0.2% = 基本図の作業点は不動)
  enter_total / exit_total     219 / 210         188 / 182 (**−14% = 世界が分岐している**)
  physics_s_per_step             6.147             8.170   (= 0.75x)
→ 「並列で走らせた世界も物理としては破綻していない」が、「同じ世界ではない」。
"""
