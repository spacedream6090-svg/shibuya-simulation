# step 時間監査(250k・夕方18時帯・mock LLM)

- 作成 2026-08-23 / 読み取り専用監査(コード変更ゼロ・実行ゼロ)
- 入力: py-spy 火炎図(init 4分 + step0-2・71.5万サンプル)+ `conf/finals_observe.yaml` のコード読解
- 実測事実: step0=22分 → step1=33分 → step2=86分 → step3=99分超(在街 ~19万へ流入)
- 対象既定: `dt_sub 0.1` / `physics.adaptive_dt` ORCA限定 `[[500,2.0],[2000,4.0]]` /
  `physics.neighbor_cap 7` / `physics.separation_iters 16` / `world.perception_cell_m 5.0` /
  `world.perception_fine_gate 500` / `world.c2_neighbors_max 15` / `world.attention_hearers_max 20` /
  `world.speech_levels` ON / `world.perception_radius_m 40.0`

---

## §1 run_step 全フェーズの棚卸し

記号: **N** = 全個体数(25万・固定) / **P** = 在街かつ非睡眠の人数(夕方 ~19万まで増える) /
**ρ** = 局所密度(知覚セル1個あたりの人数 K) / **M** = 物理ゾーンの所有中人数 /
**W** = 物理ゲートの待機列長 / **S** = 実行された物理サブステップ数(上限 6000/ゾーン/step)

### 1-A 火炎図に出ているフェーズ

| 位置 | フェーズ | 計算量クラス | 火炎図実測 | 備考 |
|---|---|---|---|---|
| `src/society/engine/scheduler.py:6487` | `physics_mod.phase` | **O(Z·N) + O(Z·S·M)** | **51.3%** | Z=3ゾーン。下表で分解 |
| `src/society/engine/scheduler.py:6546` | `incidents_mod.phase`(対人事件 H4) | O(N)×2走査 + O(候補数·ρ·r²) | **3.0%**(内 2.9% が本体) | ★火炎図の「正体不明 :6546」= これ |
| `src/society/engine/scheduler.py:6555` | `_phase_drive` | O(P) + O(requester数·ρ·r²) | **5.9%**(内 5.7% が本体) | ★火炎図の「正体不明 :6555」= これ |
| `src/society/engine/scheduler.py:6556` | `_phase_c2` → `conversation.run_phase` | O(N log N) + O(P·ρ·r²) | **11.1%** | `conversation.py:341` の `hearers_of` が 10.7% |
| `src/society/engine/scheduler.py:6570` | `_phase_decide_batched` | O(P) × (知覚 + ルール層) | **12.5%** | `_decide_g:3074` の `count_hearers` が 7.5% |
| `src/society/engine/scheduler.py:6731-6737` | 観測チャンネル `o_c(t)`(第80/G観測) | **O(N) index 構築 + O(N·ρ·r²)** | **9.1%** | ★火炎図の「正体不明 :6734」= これ(実体は `:6733` の `channels.observe`。火炎図の行番号は ±1 ずれ。`channels.observe:324` の 9.0% と同一物) |

**:6734 の正体の確定根拠**: `:6555` は `_phase_drive`(5.9% ≒ `_phase_drive:2929` 系の 5.7%)、
`:6546` は `incidents_mod.phase`(3.0% ≒ `incidents_interpersonal.phase:998` の 2.9%)と
1:1 で一致する。同様に 9.1% と一致する子フレームは `channels.observe:324` の 9.0% しかなく、
`:6733` が `_rows = _channels_mod.observe(...)` である。`:6734` の `if getattr(sim,"channels_sat",...)`
自体はほぼゼロコスト(その先の `append_sat` は `observer/channels.py:78` で O(N) のタプル再構築)。

### 1-B physics.phase(51.3%)の内訳

| 行 | 何をしているか | 計算量 | 実測 |
|---|---|---|---|
| `src/society/physics.py:562` | `engine.step(dt_eff)` | O(S·M·k) | **27.1%** |
| `src/society/physics.py:565` | `_accumulate`(連続性指標 + 身体観測) | O(S·M) 純Python列内包3本 + numpy | **10.3%** |
| `src/society/physics.py:545` | `_admit`(入場判定) | O(S·(M+W)) | **5.8%** |
| `src/society/physics.py:571` | `_advance_and_collect` | O(S·M) 純Python | **3.2%** |
| `src/society/physics.py:544` | `_writeback`(waiting が空でない限り毎サブステップ) | O(S·M) 純Python | **2.5%** |
| `src/society/physics.py:471` / `:485` | 所有回収 + 新規流入候補(**ゾーンごとに全 N 走査**) | O(Z·N) + O(Z·P·経路長) | 残余 ~2.4% |
| `src/society/physics.py:548` / `:584` | `_build_engine`(入場/退場のたびに全配列を作り直す) | O(M)×イベント回数 | 上記残余に含む |

`engine.step` の中身:

| 行 | 内容 | 実測 |
|---|---|---|
| `src/society/world/sfm_core.py:874` ← `physics.py:1443/1452` | SFM `_repulsion_cognitive`(視覚セクタ近傍) | 8.2%(forces 全体 9.4%) |
| `src/society/world/sfm_core.py:681` | `_visual_fill`(visual_neighbors のリング拡大ループ内。2回分) | 2.3 + 1.7% |
| `src/society/world/sfm_core.py:389` | `neighbor_pairs` → `PointField.candidates` | 1.8 + 1.8% |
| `src/society/world/orca_core.py:631` | ORCA `visual_neighbors` | **8.3%** |
| `src/society/world/orca_core.py:676` → `:477` → `:436` | `separate_positions` → `_overlap_pairs` → `neighbor_pairs` | 3.9% → 3.0% → 2.5% |
| `src/society/world/orca_core.py:656` | `a_lines.tolist()`(LP へ渡すための (n,k,3) → Python list) | 2.3% |
| `src/society/world/orca_core.py:660-670` | LP 本体 `_lp2/_lp3` の **純Python 個体ループ** | (残余) |
| `src/society/physics.py:1697` → `orca_core.py:411` | `min_gap`(**L2 診断専用**) | 2.3% → 2.0% |
| `src/society/physics.py:1710` | `_sfm.neighbor_pairs`(**身体観測専用**) | 2.5% |

### 1-C 火炎図に出ていないフェーズ(= 現状 <1% だが構造を確認したもの)

| 位置 | フェーズ | 計算量 | 夕方 19-21 時に伸びるか |
|---|---|---|---|
| `scheduler.py:6393-6396` | memory/relations 日次サイドカー | O(1)(日境界のみ) | いいえ |
| `scheduler.py:6397` | `_phase_pool_rotation` | 日境界のみ O(N) | いいえ(**日境界 step だけ跳ねる**) |
| `scheduler.py:6426-6427` | `agent.now_step = step`(全 N) | O(N) | 人口固定=一定 |
| `scheduler.py:6434` | `_phase_relations_day` → `relations.py:231/287` + `dunbar.day_phase` | **日境界のみ O(N × relations_max=2000)** | **日境界 step だけ最大 5 億操作の別スパイク**。18 時台の 22→99 分の説明にはならない |
| `scheduler.py:6483` | `commerce.step_counts`(混雑表) | O(N) | 一定 |
| `scheduler.py:6488` | `_phase_move` | O(N)×2 + O(移動者·経路長) + RDP | 移動者数に比例(線形) |
| `scheduler.py:6510` | `_phase_traffic` | O(エッジ数) | いいえ |
| `scheduler.py:6512` | `_phase_diversity` → `diversity.py:145/148/448` | **O(N log N) の sorted を 3 回** | 一定(ただし固定費が重い) |
| `scheduler.py:6517` / `:6524` | `street_life.phase` / `city_ops.phase` | O(担い手数) + 担当ノード表 | 軽微 |
| `scheduler.py:6538-6540` | `build_index`(唯一の共在索引) | O(N) 純Python `idx.add` | 一定 |
| `scheduler.py:6553` | `lost_mod.phase` → `lost_property.py:582` の `hearers_of` | O(落し物件数·ρ·r²) | 件数×密度で伸びる(現状小) |
| `scheduler.py:6596-6599` | `_apply` ループ + `rumors.birth_scan`(**個体ごとに1回**) | O(P) 関数呼び + L1 watermark | 線形 |
| `scheduler.py:3946/3949`(`_apply` の speak) | `hearers_of(agent, **sim.agents**, ...)` | **1発話あたり O(N=25万) の素の全走査** | **発話数に比例。現状は発話数が少ないので <1% だが、夕方に発火が増えると急伸する潜在爆弾** |
| `scheduler.py:6602` | `_phase_indoor` | `sim.indoor` 不在=即 return | いいえ |
| `scheduler.py:6603` | `_phase_jitter` | O(N) | 一定 |
| `scheduler.py:6605-6612` | infoenv / work_service / org_accumulate / gossip / beliefs | 各 O(N) 走査 or watermark | 一定〜線形 |
| `scheduler.py:6616-6636` | traces / incidents_env / facilities / assets | すべて L1 watermark(その step 分だけ) | 線形 |
| `scheduler.py:6643` / `:6652` | roster / gathering サイドカー | 1日1回 or int 比較2回 | いいえ |
| `scheduler.py:6658` | `reflect_timing.arm_moments` → `reflect_timing.py:242` | **O(N) 全走査**(先頭2条件でほぼ即脱出)+ 通過分だけ `hearers_of`(**上限なし**) | 通過数に比例(小) |
| `scheduler.py:6667-6698` | 夜内省(batched) | 対象者数のみ | 夜間のみ |
| `scheduler.py:6703-6704` | `_isl_accumulate` | O(この step の L1 件数) | 線形 |
| `scheduler.py:6711` / `:6720` / `:6726` | envfb / transit_interior / transit_staff | watermark + 路線数 | 線形 |
| `scheduler.py:6745-6746` | `plasticity.rows`(`cognition.g_update` ON) | `due()` の周期で O(N) | 周期依存 |
| `scheduler.py:6752` | `collect(sim)`(L2 集計) | O(N)×集計器数 | 一定(固定費は大きい) |
| `scheduler.py:6753-6779` | L3 スナップショット | `snapshot_every: 144` = **1日1回だけ O(N)** | その step だけ跳ねる |

---

## §2 「step が進むほど重くなる」機構の判定(最重要)

### 判定サマリ

| # | 候補 | 効く項 | 一定人口でも単調に伸びるか | 人口に対する次数 | 22→99分への寄与 |
|---|---|---|---|---|---|
| G1 | 物理サブステップ数 S の 6000 への張り付き | `physics.py:562/565/544/545` | **いいえ**(6000 で頭打ち) | 閾値的(占有が途切れなくなった瞬間に 1.5〜2 倍の跳び) | **大** |
| G2 | 物理所有人数 M の増加 | 同上 × S | いいえ | ほぼ線形(ただし G1 との積で超線形) | **大** |
| G3 | 知覚 9 セル走査の ρ² | `scheduler.py:3074/2929`, `conversation.py:341`, `channels.py:324`, `incidents_interpersonal.py:998` | いいえ | **2 次**(セル人口 K の 2 乗) | **大** |
| G4 | ゲート待機列 W の成長 | `physics.py:544/545` | いいえ(`max_hold_steps: 3` で強制解放) | 線形で頭打ち。ただし「W>0 の時間割合」が 1 に張り付くと G1 と同じ跳び | 中 |
| G5 | `separate_positions` の反復数 × 重なりペア数 | `orca_core.py:474-494` | いいえ | **超線形**(密度が上がると反復も対数も増える) | 中(19-21時に伸びる) |
| G6 | `route_span` の point-in-polygon | `physics.py:492` → `zones.py:757/717` | いいえ | 線形(在街数 × 経路長 × 3ゾーン) | 小〜中 |
| G7 | 関係台帳 / 会話 / パーティ / 記憶の蓄積 | 日境界フェーズのみ | **いいえ**(cap が効いている) | — | **ゼロ**(18時台の説明にはならない) |
| G8 | イベント journal バッファ走査 | `channels.py:263`, `scheduler.py:1971` | **いいえ**(`flush_every_steps: 6` で `logger.events` が空に戻る) | — | **ゼロ** |

### G1 物理サブステップ数の張り付き(根拠行)

- `src/society/physics.py:461` `n_sub = min(zone.max_sub_steps, round(600/0.1)) = 6000`
  (`max_sub_steps` 既定 12000 = `src/society/world/zones.py:187`)。
- while ループ `src/society/physics.py:532` は **早期打ち切りを 2 か所持つ**:
  - `:551-553` `if not members and not waiting: break`(ゾーンが空)
  - `:587-588` `if engine is None and not waiting: break`
- したがって閑散時の実サブステップ数 S は 6000 より **桁で小さい**。夕方に「ゾーンが 1 サブステップも
  空にならない」状態へ移行した瞬間、S が 6000 に張り付く。これは**人口に対して連続でない跳び**であり、
  step0→step2 の 4 倍近い悪化の初段を最もよく説明する。
- 計測手段: L2 の `physics.sub_steps`(`physics.py:613 st["sub_steps_total"]`)と
  `by_zone[*].sub_steps`(`physics.py:626`)。**step ごとの S を見れば張り付きが即判る**。
- ★ORCA(scramble)には `adaptive_dt` が効くので S は 1/2〜1/4 になるが、
  **SFM の hachiko_square / center_gai は `engines: [orca]` の対象外**(`conf/finals_observe.yaml:583`)
  なので、この 2 ゾーンは占有が続く限り常に 6000 サブステップを回す。

### G2 所有人数 M の増加(根拠行)

- `src/society/physics.py:485-499`: 所有開始の条件は **「残り経路がゾーン内ノードを 1 つでも通る」だけ**。
  `zones.route_span`(`src/society/world/zones.py:757`)は `[現在ノード] + route` を先頭から見て
  最初のゾーン内ノードを探すので、**数百 m 手前の個体もその場で `waiting` に入る**。
- `_admit`(`physics.py:762-804`)の入場条件は「その位置で他人と `min_gap 0.10 m` 以内に重ならないこと」
  だけで、**ゲートからの距離条件は無い**。遠方の個体は誰とも重ならないので即 `members` へ入る。
- 結果として M は「polygon 内の人数」ではなく「そのゾーンを経路に含む在街者の総数」。
  `conf/finals_observe.yaml:568-571` が自ら「所有中の人数であって polygon 内ではない・数百 m 手前から
  始まる」と自認している。**夕方の帰宅流はスクランブル/センター街を通るので M は在街人口にほぼ比例**。
- 1 サブステップの費用は O(M)〜O(M·k·log):
  `sfm_core.py:698` の `argsort`、`:705` の `lexsort`、`orca_core.py:660` の純Python LP ループ、
  `physics.py:1674/1677/1696` の Python 列内包 3 本、`physics.py:1720` の Python ループ。
- ⇒ **physics ≈ S(占有) × O(M)** の積。G1 の跳びと G2 の線形増が掛かって超線形になる。

### G3 知覚 9 セル走査の 2 次項(根拠行)

- `src/society/world/perception.py:360` `self._inv = 1/radius` — **索引のセル辺は常に
  `world.perception_radius_m = 40 m` 固定**。近傍は 3×3 セル = 120×120 m = 14,400 m²。
- `PerceptIndex._count`(`perception.py:624-681`)は近傍連結配列 `(xs, ys, ids)` を
  `_count_arrays`(`:683`)でセル単位にキャッシュするが、**話者ごとに全長 |近傍| の numpy 演算を撃つ**
  (`:657-668` の `xs - sx` / `np.abs` / `np.maximum` / `flatnonzero`)。
- 1 セルに K 人居ると、そのセルの話者 K 人 × 近傍 ~9K ⇒ **セルあたり 9K²**。
  総費用 = Σ_cells 9K² = **人口の 2 乗**(集中が進むほど加速する)。
- 呼び手は 5 系統(すべて同じ 40 m 粗格子):
  | 呼び手 | 行 | 呼ぶ回数/step | 実測 |
  |---|---|---|---|
  | `_decide_g` の `has_company` | `scheduler.py:3074` | active 全員(~19万) | 7.5% |
  | `_phase_drive` の `face` 判定 | `scheduler.py:2929` | requester 全員 | 5.7% |
  | G観測 `ext.encounter` | `cognition/channels.py:324` | **全 25 万体** | 9.0% |
  | 対人事件の共在 | `incidents_interpersonal.py:998` | 動機のある候補全員 | 2.9% |
  | C2/C3 会話 | `conversation.py:341` | active 全員 | 10.6%(細格子経由) |
- **`conversation.py:341` だけは細格子(`perception_cell_m: 5.0`)へ回る余地がある**が、門は
  `perception.py:590` の `_coarse_load × (1−ratio) < fine_gain(=500)` で、**粗格子 9 セルの総人数が
  508 人未満なら粗格子のまま**。中密度帯は 40 m 走査のまま残っている。
- 残り 4 系統は **`_count` / 既定 `hearers()` = 常に粗格子**。特に `scheduler.py:2929` は
  `hearers_of` の **純Python 三重ループ + `sorted()`**(`perception.py:728-739`)で、
  返り値を `bool()` にしか使っていない(第152 が `_decide_g:3074` で潰したのと**同型のバグが残存**)。

### G4 待機列 W(根拠行)

- `physics.py:542-546`: `if waiting:` のあいだ **毎サブステップ** `_writeback`(O(M) 純Python)+ `_admit`。
- `_admit` は毎回 `queue = list(waiting)`(`:738`)と `_admit_blocked`(`:749` → `:978-987` で
  numpy 配列 4 本 + `PointField` 構築)を作り直す。**W と M の両方に毎サブステップ比例**。
- 信号赤のあいだ `_admit` は `:734-735` で即 False を返すが、**その手前の `_writeback` は既に走り終えている**
  (= 完全な無駄。scramble は cycle 140 s / green 37 s + flash 10 s なので **約 66% のサブステップが無駄**)。
- W 自体は `gate.max_hold_steps: 3`(`zones.py:68`)で 3 step 後に強制解放されるので**無限には伸びない**。
- ⇒ 判定: **蓄積ではなく人口比例で頭打ち**。ただし「W>0 の時間割合」が 1 へ張り付くと G1 と同じ閾値的な跳び。

### G5 `separate_positions`(根拠行)

- `orca_core.py:474` `for _ in range(max_iters=16)` … 各反復で `_overlap_pairs`(`:477`)が
  `PointField` を作り直し、`:494` `for p in range(iu.shape[0])` の **純Python Gauss-Seidel ループ**を回す。
- 重なりペア数は密度の超線形関数(六方最密 3.22 人/m² 付近で発散)。反復数も密度とともに増える。
- ⇒ **19-21 時の密度帯で最も伸びる項**。監視は `st["sep_iters_max"]`(`physics.py:1700`)。

### G6 `route_span` の point-in-polygon(根拠行)

- `physics.py:492` は **在街かつ経路持ちの全個体 × 3 ゾーン** に対して `route_span` を呼ぶ。
- `zones.py:768-769` `ins = [node_in(zone, graph, n) for n in seq]` — **経路の全ノードに対して**
  `node_in`(`zones.py:717-730`)= `graph.nodes[node]` 辞書引き + `Zone.contains`(`zones.py:242`)の
  ray casting。**キャッシュが一切無い**(地図は静的なので純関数なのに)。
- 費用 = 在街者数 × 経路長 × 3。夕方の帰宅流で線形に伸びる。

### G7/G8 状態蓄積は 18 時台の説明にならない(根拠行)

- `conversation.py:292-293` `_c3_pass` / `_c3_greet` は日内単調増加だが `c3_distinct_cap: 2000` で飽和
  (`conversation.py:353/355/384/386`)。`set.add` は O(1) なので**走査コストは増えない**。
- `net.contacts_hard_max: 2000` / `follows_hard_max: 4000` / `memory.relations_max: 2000`(第141)。
  これらを舐めるのは **日境界の `relations.decay_day`(`relations.py:231/287`)と `dunbar.day_phase` だけ**。
- `sim.logger.events` は `observer.flush_every_steps: 6` ごとに `self.events = []`
  (`src/society/observer/logger.py:283`)。`channels._event_counts`(`channels.py:263`)・
  `_isl_accumulate`(`scheduler.py:1971`)・envfb / work / rumors / traces / facilities / assets の
  watermark 走査は **すべてその step 分の増分だけ**。
- `party.form_parties`(`party.py:117-130`)は日境界のみ。
- ⇒ **(ii) 状態蓄積で step 内が単調に伸びる項は見当たらない**。22→99 分は **(i) 流入増**が主因で、
  その効き方が G1(閾値的な跳び)× G2(線形)と G3(2 次)である。
- ★ただし **日境界 step だけは別種のスパイク**がある(relations/dunbar の全ペア走査 25万×2000 +
  L3 スナップショット + pool ローテーション)。10 日ランの day boundary は個別に監視すること。

---

## §3 最適化候補ランク表

リスク級: **A** = 出力バイト同一(L1/L2/L3/乱数/LLM呼数のすべて) /
**B** = 力学バイト同一で観測値のみ変化(数値誤差レベル以下) / **C** = 力学が変わる

| # | 候補 | 作用点 | 期待削減(step全体) | リスク | 実装規模 | 検証方法 |
|---|---|---|---|---|---|---|
| **A1** | `face = bool(hearers_of(...))` → `count_hearers(...) > 0` | `scheduler.py:2929` | **−4%** | **A** | 15分(1行) | 既存 `tests/test_count_hearers.py`(bool 同値を機械照合済み)+ ゴールデン L1 差分ゼロ |
| **A2** | `count_hearers` に存在判定モード(最初の 1 件で打ち切り)を足し、`:3074` と A1 から使う | `perception.py:624-681` / `scheduler.py:3074,2929` | **−5%** | **A** | 2〜3時間 | 「exists == (count>0)」を総当たりで固定する新テスト + ゴールデン |
| **A3** | `_accumulate` の `np.array([r["radius"] …])` を `engine.radius` へ | `physics.py:1696` | **−0.8〜1.5%** | **A**(両エンジンとも `self.radius = np.asarray(radius,f64).copy()`。`sfm_core.py:804` / `orca_core.py:554`。以後不変) | 15分(1行) | `np.array_equal` 断言テスト + physics ゴールデン |
| **A4** | 信号ゲートを `_writeback` の**前**へ前倒し(赤のサブステップで O(M) writeback と `_admit` の numpy 一式を作らない) | `physics.py:542-546` | **−2〜3%** | **A**(`_admit` は `:734-735` で即 False。`_writeback` の結果を読むのは `_admit` だけ) | 1時間 | 同一 seed で `zone_gate` L1 と `continuity` が完全一致することを確認 |
| **A5** | `zones.node_in` をゾーン別 frozenset へメモ化(`inside_nodes` は既に存在) | `zones.py:717` / `physics.py:492` | **−1〜2%**(かつ在街数比例の伸びを平坦化) | **A** | 1時間 | `node_in` 新旧の全ノード突合テスト |
| **A6** | `world.perception_fine_gate` を 500 → 64 前後へ(**conf 1 行**) | `conf/finals_observe.yaml` / `perception.py:590` | **−1〜3%** | **A**(`perception.py:785` と `registry.py:179` が「返り値に一切影響しない」を宣言・粗/細どちらでも同一集合同一順序) | 5分 | 既存の粗/細同値テスト + 短尺 mock で L1 バイト一致 |
| **A7** | `min_gap` を n サブステップに 1 回へ(消費先は L2 診断のみ) | `physics.py:1697-1699` → `orca_core.py:388` | **−2%** | **A**(力学/L1/L3)/ **B**(L2 の `min_gap_m` が上界化) | 1時間 | `physics.scalars()` の他項が不変・`min_gap_m` の差が ≤ v_max·dt であることを短尺で確認 |
| **A8** | 身体観測(`neighbor_pairs` + 密度/接触)を n サブステップに 1 回へ | `physics.py:1706-1727` | **−2%** | **B**(`_phys_body` は `scheduler.py:2586` が「`prompt_kwargs()` に出ない」= プロンプト不変を保証済み。消費先は Perception contract の body 3 欄と `pool.py:802` の持ち越しのみ) | 2時間 | `tests/test_physics_zones.py` の no-fingerprint 固定 + body 3 欄の相対差 |
| **A9** | `_run_zone` の 2 本の全 N 走査(`:471` / `:485`)を phase 側の 1 パスへ集約 | `physics.py:447-449,471,485` | **−0.5〜1%** | **A**(走査順・集合とも不変) | 2時間 | 所有列の id 列を新旧で突合 |
| **A10** | `channels.observe` の対象を `loc != "outside"` で先に絞る | `cognition/channels.py:290,313` | **−0.5〜1%** | **A**(`_count` は `perception.py:632` で outside を即 0 で返す。行は全員分必要なので値だけ先に 0.0 を入れる) | 1時間 | 行数・列値の全数突合 |
| **A11** | `incidents_interpersonal` の `sorted(sim.agents)` + `police_nodes` 集合を 1 パス化 | `incidents_interpersonal.py:973,986` | **−0.3〜0.5%** | **A** | 1時間 | 候補列の id 列突合 |
| **A12** | `_accumulate` の `seg_dir` / `sign` を engine 側の numpy 配列で持つ(列内包 2 本を消す) | `physics.py:1674,1677,1693-1694` | **−1〜2%** | **A**(値は同一 float64) | 4時間 | 配列突合 + physics ゴールデン |
| **A13** | `speed_sum` / `dens_sum` / `contact_n` を numpy アキュムレータへ(個体内の加算順序は保存) | `physics.py:1720-1727` | **−1〜2%** | **A**(個体ごとの逐次加算順は不変 = IEEE754 でビット一致) | 4時間 | `_finish_body` の出力を新旧突合 |
| **B1** | `cognition.channels.every_steps` を 2〜3 へ(conf 1 行) | `scheduler.py:1950` | **−4.5〜6%** | **C**(観測の時間解像度が落ちる。`cognition.g_update` が読む値の粒度に影響) | 5分 | G観測の下流(plasticity / 第80 σ 較正)への影響評価が先 |
| **B2** | `_apply` の speak で `sim.agents` 全走査をやめ、`_apply` 用の索引を張る | `scheduler.py:3946,3949,3912,4941` | 現状 <1%・**夕方の発火増で急伸する潜在爆弾**。潰せば 5-10% の伸びを予防 | **C**(位置が動く途中の索引 = 聞き手集合が変わりうる) | 1日 | 聞き手集合の差分件数を短尺で実測してから判断 |
| **C1** | **物理ゾーン所有の距離有界化**(ゲートから X m 以内でのみ `waiting` へ入れる) | `physics.py:485-499` | **−15〜25%**(M が 1/3 なら `:562/:565/:545/:544` がすべて比例して落ちる) | **C**(軌跡が変わる) | 半日 + ベンチ | `reference/physics_bench` の基本図 ±20% 帯・破綻統計(重なり/壁貫通/逆走/立往生)・`zone_occupancy` の再測 |
| **C2** | `separation_iters` を 16 → 8 | conf 1 行 | −1.5%(19-21時はもっと) | **C** | 5分 | 既存ベンチ表(ρ=3.57 で −0.15m のめり込みが更に悪化する帯の再測) |
| **C3** | SFM ゾーンへ `adaptive_dt` を拡張 | conf | — | **却下** | — | 実測済み(係数2で重なり −0.171m・壁貫通 −0.105m。`conf/finals_observe.yaml:572-577`) |
| **C4** | ゾーン並列(threading) | `physics.py:448-449` | 見込み薄 | **却下寄り** | — | 支配項が純Python(`orca_core.py:660` の LP ループ・`physics.py:1720` の集計ループ・`separate_positions` の Gauss-Seidel)で GIL を握りっぱなし。numpy 部分だけ解放されても取り分が小さい |
| **C5** | ORCA の LP ループ(`orca_core.py:656-670`)の numpy 化 | `orca_core.py` | 2〜4% | **B/C** | 数日 | LP の逐次半平面法はベクトル化が難しく、費用対効果が悪い。**今回は非推奨** |

### ランク付けの読み方

- **A 級の合計は −19〜22%**。これだけで step が 99 分 → 78 分前後に落ちる見込み(バイト同一)。
- **最大の単一レバーは C1(物理所有の距離有界化)で −15〜25%**。ただし力学が変わるので
  `reference/physics_bench` の再測が前提。今夜は触らない。
- G1(サブステップの 6000 張り付き)を直接殺すレバー(`max_sub_steps` を下げる等)は
  **積分時間の総量が減る = 世界時計と物理時計がずれる**ので C 級ですらなく破壊的。触らない。

---

## §4 今夜適用可能な安全レバー(A 級のみ)

適用順(上から。各レバーは独立に戻せる):

| 順 | レバー | 変更箇所 | 期待削減 | 検収 |
|---|---|---|---|---|
| 1 | **A1** `_phase_drive` の `bool(hearers_of(...))` → `count_hearers(...) > 0` | `src/society/engine/scheduler.py:2929`(1行) | **−4%** | 既存 `tests/test_count_hearers.py` + 短尺 mock のゴールデン L1 バイト一致 |
| 2 | **A2** `count_hearers` の存在判定モード(早期脱出)を追加し `:3074` と A1 の両方から使う | `src/society/world/perception.py:624-681` + 呼び手 2 か所 | **−5%** | exists == (count>0) の総当たり同値テスト(新規)+ ゴールデン |
| 3 | **A4** `_run_zone` の信号ゲート前倒し(赤のサブステップで `_writeback` と `_admit` の numpy を作らない) | `src/society/physics.py:542-546` | **−2〜3%** | `zone_gate` L1 と `physics.continuity/scalars` の完全一致 |
| 4 | **A7 + A3** `_accumulate` の `min_gap` 間引き + `radius` 配列の使い回し | `src/society/physics.py:1696-1699` | **−3%** | 力学バイト一致(A3)/ `min_gap_m` 以外の scalars 不変(A7) |
| 5 | **A6** `world.perception_fine_gate` 500 → 64(**conf 1 行・コード不触**) | `conf/finals_observe.yaml` | **−1〜3%** | 粗/細同値テスト + 短尺で L1 バイト一致(返り値は仕様上不変) |
| 6 | **A5** `zones.node_in` のメモ化 | `src/society/world/zones.py:717` | **−1〜2%** | 全ノード突合テスト |

合計見込み **−16〜20%**(99 分 → 79〜83 分)。すべて出力バイト同一なので、
既存のフルゲート(6,782 緑)+ 短尺 mock のゴールデン L1/L2/L3 比較で検収できる。

### 適用前に必ず採っておく計測(コード変更ゼロ)

1. **L2 `physics.sub_steps` と `by_zone[*].sub_steps` を step ごとにプロット**
   (`src/society/physics.py:613,626`)。G1 の「6000 張り付き」が実際に起きているかの唯一の直接証拠。
2. **`by_zone[*].occupancy_mean` と `waiting`**(`physics.py:621-626`)= G2/G4 の実測。
   `occupancy_mean` が「polygon 内の人数」より桁で大きければ C1 の効果見積りがそのまま裏付けられる。
3. **`continuity.sep_iters_max`**(`physics.py:1700`)= G5 が上限 16 に張り付いているかの監視。

---

## 付録: 監査中に見つかった「バグに近い」構造(判断待ち)

1. **`scheduler.py:2929` の `hearers_of` は第152 が `_decide_g:3074` で潰したのと同型の残存**。
   返り値を `bool()` にしか使っていないのに 40 m 圏を全列挙して id 昇順に整列している(A1)。
2. **`physics.py:544` の `_writeback` が信号赤のサブステップで完全に捨てられている**(A4)。
   scramble は約 66% のサブステップが赤。
3. **`zones.node_in` にキャッシュが無い**(A5)。地図は静的なので純関数であり、
   `inside_nodes()`(`zones.py:733`)という「答えの集合を返す関数」が既に存在する。
4. **物理ゾーンの所有に距離条件が無い**(C1)。`conf/finals_observe.yaml:568-571` が自認しているとおり
   「数百 m 手前から所有が始まる」= ゾーン外を歩いている個体を 0.1 s 刻みで 600 s ぶん積分している。
   **これが物理 51.3% の最大の構造的原因**であり、同時に「ゾーン外を SFM/ORCA で歩かせている」という
   モデル上の疑問点でもある(有界化は速度だけでなく妥当性の面からも検討に値する)。
5. **`scheduler.py:3946/3949` の `_apply` speak が `sim.agents`(25 万)を素で全走査する**。
   現状は発話数が少ないので火炎図に出ないが、夕方の発火増でそのまま線形に伸びる潜在爆弾(B2)。
