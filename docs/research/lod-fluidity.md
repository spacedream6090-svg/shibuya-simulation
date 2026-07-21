# 思考リソースLOD 棚卸し — 流動性の確証と計算リソース比較

作成: 2026-07-21 / 担当: 実行(Opus)/ 検収: Fable(親)
関連: [`multi-model-lod.md`](multi-model-lod.md) · [`compute-efficiency.md`](compute-efficiency.md) · [`interstitial-life.md`](interstitial-life.md) · [`input-resolution.md`](input-resolution.md) · [`../plans/input-resolution-lod.md`](../plans/input-resolution-lod.md) · [`../plans/p2-interstitial-design.md`](../plans/p2-interstitial-design.md)

---

## 0. TL;DR(ユーザー方針への回答)

ユーザー方針(2026-07-20): **「LOD は 1step ごとに層を移り変わる流動的なものにしたい。背景に思考を割かず前景に割きすぎるのは非現実的。全員にまんべんなくリソースを割き、各エージェントのパラメータに応じて上位 LOD に入る確率を調整。他の実験用 LOD は導入せず、これまで実装した思考タイミングの実装のみにする。それぞれの計算リソースとシミュ時間を比較できる状態にしてほしい。」**

3 点、コードで確認した結論:

1. **流動性は既に実装済み。** 現行の「顕著性(欲求)駆動発火ゲート + step 予算」は **固定の前景/背景 tier を持たない**。毎 step、budget をリセットし([`scheduler.py:3470`](../../src/society/engine/scheduler.py))、全在場個体の欲求ゲージを更新し([`scheduler.py:1528-1534`](../../src/society/engine/scheduler.py))、その step にゲージが閾値を超えた者だけが「申請」して予算内で発火する([`scheduler.py:1550-1583`](../../src/society/engine/scheduler.py))。**誰が上位 LOD(=思考)に入るかは step ごとに入れ替わる**。旧来の「即時トリガー surprise_of による固定判定」は Phase A(2026-07-04)で **全員思考への転換** として廃止済み([`lod.py:3-6`](../../src/society/cognition/lod.py))。

2. **「パラメータに応じて上位 LOD 確率を調整」は正道が既に採られている。** 個体差は **経験由来の状態量**(欲求ゲージ・顕著性・状況)を経由して入る。**生得 traits を LOD 確率へ直結させる裏口は設計上却下済み**(§4)。これは k\*(世界改変の作用性研究)の交絡防止のための必須条件。

3. **実測比較ハーネスを新規追加**([`scripts/bench_lod.py`](../../scripts/bench_lod.py))。構成別に **壁時間・LLM 呼数(purpose 別)・エージェント別 熟慮回数の分布(Gini + ヒスト = 「まんべんなさ」の定量)・イベント総数・ピーク RSS(外部 PowerShell)** を 1 表に揃える。実測結果は §6。

---

## 1. 用語

- **LOD(Level of Detail)** = 1 個体・1 step に割く **思考(LLM 推論)リソースの水準**。上位 LOD = フル LLM 熟慮/発話/計画/内省。下位 LOD = ルールベース routine(決定論・LLM 呼ゼロ)。
- **本番採用候補 = 思考タイミング系**: 「いつ・誰が・どれだけ LLM を撃つか」を **時間分散**で決める機構群。ユーザーが残すと明言した対象。
- **実験用 LOD 系**: 「世界の見え方の解像度」「モデルの大小」「行動の再利用」など **本番では使わない**と決まっている実験軸(既定 OFF 運用)。

---

## 2. 思考タイミング系(本番採用候補)— file:line と 流動性判定

| 機構 | 役割 | 主要 file:line | config キー(既定) | 毎-step 流動性 |
|---|---|---|---|---|
| **顕著性(欲求)駆動発火ゲート** | 出来事→欲求ゲージ→個人閾値で申請→個人重みで確率発火。上位 LOD の入場口 | ゲート本体 [`scheduler.py:1509`](../../src/society/engine/scheduler.py) `_phase_drive` / ゲージ機構 [`drive.py`](../../src/society/cognition/drive.py) 全体 / 呼び出し [`scheduler.py:3518`](../../src/society/engine/scheduler.py) | `drive.*`([`config.yaml:376-429`](../../conf/config.yaml)) | **○ 完全に毎-step 流動**。申請者集合を毎 step 再計算・ゲージ順に抽選 |
| **LodBudget(step 予算)** | 1 step あたり LLM 発火の上限。インフラ律速 | クラス [`lod.py:80`](../../src/society/cognition/lod.py) / 構築 [`simulation.py:75-82`](../../src/society/engine/simulation.py) / reset [`scheduler.py:3470`](../../src/society/engine/scheduler.py) / take [`scheduler.py:1565,1578,1673`](../../src/society/engine/scheduler.py) | `lod.max_llm_per_step`=300([`config.yaml:560`](../../conf/config.yaml)) | **○ 毎-step リセット**。予算の受益者は step ごとに変わる |
| **N 比例予算(S6a)** | 固定 cap を `ceil(density×N)` に置換。全員思考の密度を N に比例維持 | 構築 [`simulation.py:75-79`](../../src/society/engine/simulation.py) / 在場数追随 [`simulation.py:844-853`](../../src/society/engine/simulation.py) `_pool_update_budget` | `lod.n_proportional`(enabled=false, density=0.15)([`config.yaml:567`](../../conf/config.yaml)) | **○** 予算値は N 追随・配分は drive ゲートに委譲=流動 |
| **朝計画(planning)** | 起床/帰還直後に 1 回、当日の予定を LLM 生成 | フェーズ [`scheduler.py:644`](../../src/society/engine/scheduler.py) `_phase_planning`(呼び出し [`scheduler.py:3504`](../../src/society/engine/scheduler.py)) / 生成 [`planning.py`](../../src/society/cognition/planning.py) | `planning.enabled`=**true**([`config.yaml:457`](../../conf/config.yaml)) | △ 個体別起床時刻で **時間分散**(step 固定でなく個体イベント駆動)。1 日 1 回=全員一様 |
| **夜内省(reflection)** | 就寝直後/帰路に 1 回、当日を LLM 内省・k ゲートで書き戻し | ループ [`scheduler.py:3538-3557`](../../src/society/engine/scheduler.py) / 予約 [`scheduler.py:947,1912,3362`](../../src/society/engine/scheduler.py) `reflect_step` / 本体 [`reflection.py`](../../src/society/cognition/reflection.py) | `k.writeback`=free / `model.reflect_*`([`config.yaml:34-38,139-141`](../../conf/config.yaml)) | △ 個体別就寝時刻で **時間分散**。1 日 1 回=全員一様 |
| **出来事誘発 深い内省(第12バッチ)** | 固定周期でなく **日内衝撃ゲージ**が閾値超えの日を深い内省へ格上げ | 設計 [`config.yaml:40-61`](../../conf/config.yaml) / 日次 [`scheduler.py:2503`](../../src/society/engine/scheduler.py) `_phase_reflect_day`(呼び出し 3498)/ [`reflection.py`](../../src/society/cognition/reflection.py) | `reflection.deep`(enabled=false, ★本番 ON 推奨)/ `reflection.implicit_self`([`config.yaml:50-61`](../../conf/config.yaml)) | △ 誘発は個体の経験量依存=**内容的に流動**(誰が深く考えるかが日で変わる) |
| **行間レイヤ S2 ナラティブ補間** | 前回発火以降の客観ダイジェストを計画/発話/内省プロンプトに 1 行注入(LLM 呼ゼロ) | 判定 [`scheduler.py:1220`](../../src/society/engine/scheduler.py) `_interstitial_on` / 蓄積 `_isl_accumulate`・取出 `_isl_take`([`scheduler.py:3559-3563`](../../src/society/engine/scheduler.py)) | `prompts.interstitial.enabled`=false([`config.yaml:537`](../../conf/config.yaml)) | ― 呼数不変(内容のみ)。発火の質を上げる補助 |
| **行間レイヤ S3 会話3層 C2/C3** | 同席対を決定論列挙し **LLM 呼ゼロ**の構造化会話を大量生成。顕著な帰結は drive を押し上げ次 step の C1 昇格 | フェーズ [`scheduler.py:1597`](../../src/society/engine/scheduler.py) `_phase_c2` / [`conversation.py`](../../src/society/conversation.py) | `conversation.enabled`=false(★本番 ON 推奨)([`config.yaml:444-452`](../../conf/config.yaml)) | **○** 昇格経路が drive ゲート経由=毎-step 流動に接続 |
| **行間レイヤ S4 確率的実行** | routine 実行に実証較正の揺らぎ(motif/±30分ジッター/寄り道/中断/Gumbel)。LLM 呼ゼロ | [`routine.py`](../../src/society/cognition/routine.py) / 専用 stream(motif/jitter_time/detour/interrupt/gumbel) | `routine.stochastic.enabled`=false([`config.yaml:495-519`](../../conf/config.yaml)) | ― 下位 LOD(routine)側の忠実度向上。呼数不変 |
| **行間レイヤ S5 退屈/好奇心ドライブ** | 長居で退屈ゲージ蓄積→閾値で内発的探索(未訪問優先)。脱馴化で novel_place=drive 鋭敏化に自然接続 | ゲージ [`drive.py:213-256`](../../src/society/cognition/drive.py) `boredom_tick`/`boredom_ready`/`boredom_fire`(毎-step tick は [`drive.py:182`](../../src/society/cognition/drive.py))/ 発火 routine._maybe_boredom_explore | `drive.boredom.enabled`=false([`config.yaml:420-429`](../../conf/config.yaml)) | **○** 毎-step ゲージ更新。探索の帰結が drive ゲートへ戻る |
| **S6b 一括発行(batch_llm)** | 計画/内省を id 順に組んで並行発行。逐次経路とバイト一致 | 計画 [`scheduler.py:667`](../../src/society/engine/scheduler.py) `_phase_planning_batched` / 内省 [`scheduler.py:696`](../../src/society/engine/scheduler.py) `_phase_reflect_batched` | `engine.batch_llm.enabled`=false([`config.yaml:596-597`](../../conf/config.yaml)) | ― 実行効率の seam(実 LLM のスループット向上)。認知経路は不変 |
| **内省しやすさの時間ドリフト E2** | 実効閾値を馴化/鋭敏化で時変。入力は出来事量・発火経験のみ(k 非依存) | [`drive.py:88-136`](../../src/society/cognition/drive.py) `effective_threshold`/`_drift_*` | `drive.drift.enabled`=false([`config.yaml:404-409`](../../conf/config.yaml)) | **○** 誰が上位 LOD に入りやすいかを **経験で時変**=正道の確率調整ノブ |

> **時間分散 vs 毎-step 流動の区別**: 計画/内省は「1 日 1 回・全員一様」だが起床/就寝時刻の個体差で **step には分散**する(id 順バイアスなし)。日中の熟慮(drive ゲート)は「その step にゲージが立った者」で **毎-step 入れ替わる** = ユーザーの言う「1step ごとに層を移り変わる」に一致。

---

## 3. 実験用 LOD 系(本番では使わない=ユーザー方針)— file:line

| 機構 | 何の LOD か | 主要 file:line | config キー(既定) | 本番不採用の根拠 |
|---|---|---|---|---|
| **入力解像度 LOD(input_res)** | 「世界の見え方」の個体差(知覚/記憶/フィード注入件数を narrow/mid/wide に振る) | 既定 [`lod.py:26-36`](../../src/society/cognition/lod.py) / 構築 [`lod.py:39`](../../src/society/cognition/lod.py) / **軸共通割当** [`lod.py:55-77`](../../src/society/cognition/lod.py) `assign_axis` | `lod.input_res.enabled`=false([`config.yaml:574-575`](../../conf/config.yaml)) | 別軸の実験機構。**割当は trait 非依存の専用 random stream**(生得性の裏口を封じる設計、[`lod.py:14-16`](../../src/society/cognition/lod.py)) |
| **agent_tier(前景/背景の個体階層)** | 個体を上位/下位モデルへ固定振り分け | **未実装**。[`router.py:22-23,44-47`](../../src/society/llm/router.py) が `agent_tier` キーで `ValueError` | コメントのみ([`config.yaml:163`](../../conf/config.yaml)「未実装=ユーザー討議後」) | ユーザー方針で不採用。仮に入れるなら固定 trait・k 非依存が必須(k\* 交絡回避、[`multi-model-lod.md:271`](multi-model-lod.md)) |
| **モデル級 LOD / purpose 別 Router** | purpose(reflect/deliberate…)で大小モデルを混載 | [`router.py`](../../src/society/llm/router.py) `RouterLLM` / [`fleet.py`](../../src/society/llm/fleet.py) / 構築 [`simulation.py:416-445`](../../src/society/engine/simulation.py) | `model.tiers` / `model.router`(既定 null)([`config.yaml:155-169`](../../conf/config.yaml)) | 「計算削減」軸であって思考タイミングではない。本番は単一モデルで良い(コスト最適化は別途) |
| **S7 方針キャッシュ** | 行動系列を **k 非依存の物理量キー**でキャッシュし類似状況で LLM 呼をスキップ | [`policy_cache.py`](../../src/society/cognition/policy_cache.py) / 配線 [`planning.py:120,168`](../../src/society/cognition/planning.py) | `cognition.policy_cache.enabled`=false([`config.yaml:602-608`](../../conf/config.yaml)) | 既定 OFF 運用は決定済み(本番採否はブラインド A/B 比較で判断)。再利用は多様性を削るリスク |
| **構造化シーン記述の件数(scene_n)** | 視界記述の注入件数を input_res LOD に連動 | [`config.yaml:224-235`](../../conf/config.yaml) `world.scene_desc` | `world.scene_desc.enabled`=false | input_res 軸の従属。本番不採用 |

> **共通設計**: 実験用 LOD 軸はすべて **config 1 キー(enabled)で完全に切り離せ、OFF=バイト一致**([`lod.py:16`](../../src/society/cognition/lod.py))。ゴールデン L1 を壊さない。

---

## 4. 重要な設計論点(R1)— 「パラメータで上位 LOD 確率を調整」の正道

ユーザー要望「**各エージェントのパラメータに応じて上位 LOD に入る確率を調整**」には 2 つの実装ルートがあり、片方は **既に却下済み**:

### ❌ 却下: 生得 traits を LOD 確率へ直結
「開放性の高い個体は常に前景」のような **静的 trait → LOD-tier 直マップ**。却下理由は 2 つ:

1. **生得性実験の裏口になる。** 「誰が世界改変者になれるか」を生得 trait が事前決定する構造は、それ自体が独立した研究仮説(nativism)。LOD 機構に紛れ込ませると、意図しない生得性の刷り込みになる。
2. **k\* を交絡する。** k\*(内省の書き戻し自由度が世界改変に効くか)の測定で、上位 LOD 割当が固定 trait で決まると「どの個体が Y_external を動かせるか」が処置と独立に固定され、分散を消す([`multi-model-lod.md:16,271`](multi-model-lod.md) / [`compute-efficiency.md`](compute-efficiency.md) の「階層化=Tier3=研究目的と衝突」)。

この却下を **コードで体現**しているのが input_res の割当機構: [`lod.py:14-16`](../../src/society/cognition/lod.py) が明示的に「**割当は trait 非依存・k 非依存・初期化時 1 回固定(生得性の裏口と R1 を守る)**」とし、[`assign_axis`](../../src/society/cognition/lod.py) は trait でなく **軸専用の決定論 random stream** で振る。

### ✅ 正道(現行): 経験由来の状態量を経由
上位 LOD に入る確率は **経験で動く状態量**で調整する:

- **欲求ゲージ(drive)** — 観測可能な出来事のみで蓄積([`drive.py:1-13,139-169`](../../src/society/cognition/drive.py))。信念・k を一切読まない(R1 対策の明文規定)。
- **顕著性・状況** — top_reason([`drive.py:185`](../../src/society/cognition/drive.py))が発火の「きっかけ」を選ぶ。
- **時変の閾値ドリフト E2** — 馴化/鋭敏化も入力は出来事量・発火経験のみ([`drive.py:106-136`](../../src/society/cognition/drive.py))。

個体差は **trait 由来の閾値/重みを「定数」として持つ**(`drive_threshold`/`fire_weight` は persona traits から `factors/` 内で写像、[`drive.py:9-11`](../../src/society/cognition/drive.py))。ただし **発火するか否かは動的な欲求ゲージが閾値を跨ぐか**で決まる。つまり「trait は閾値の高さを決めるが、いつ跨ぐかは経験が決める」ハイブリッド。ここが「静的 trait 直結(却下)」と決定的に違う:trait は入場の **難易度**を与えるだけで、**入場の可否は経験(観測イベント)が握る**。だから k\* は汚れない。

### 💡 ユーザーへの提案(状態由来の確率調整の追加ノブ)
現行で既に「経験由来の確率調整」は効いているが、本番プロファイルで **状態由来のノブ**を明示的に開けられる(いずれも trait 直結でなく状態/経験由来なので R1 安全):

1. **E2 ドリフト ON**(`drive.drift.enabled=true`): 「乗ってきた個体はより考えやすく、単調な個体は考えにくく」を **経験で**時変させる。まんべんなさは保ちつつ、状況に応じた確率調整が入る。
2. **退屈/好奇心 ON**(`drive.boredom.enabled=true`): 長居・単調で内発探索を起こし、脱馴化で顕著性へ再接続。下位 LOD 個体が自発的に上位へ戻る経路。
3. **状況重みの再調律**(`drive.weights`): 出来事種別の顕著度を較正。どの経験が上位 LOD を引くかの設計ノブ(全員一様=R1 安全)。
4. **(要新規実装・討議事項)** 「直近顕著性による fire_weight の状態変調」= 現状 `fire_weight` は定数。これを **直近の観測顕著性(状態量)**で乗算変調すれば、trait を触らずに「今この個体は上位に入りやすい/にくい」を毎-step 動かせる。src 変更を伴うため、実装前に §pre-coding-alignment に従い決定アジェンダを立てる。

---

## 5. 流動性の確証(コード根拠の要約)

「現行は既に毎-step 流動(固定前景/背景 tier は廃止済み)」の直接根拠:

1. **予算は毎 step リセット** — `run_step` 冒頭 [`scheduler.py:3470`](../../src/society/engine/scheduler.py) `sim.budget.reset()`。前 step の受益者は引き継がれない。
2. **全在場個体のゲージを毎 step 更新** — [`scheduler.py:1519`](../../src/society/engine/scheduler.py) で active を再計算し、[`scheduler.py:1528-1529`](../../src/society/engine/scheduler.py) で全員 `drive.step_tick`(自然減衰+沈黙蓄積+退屈 tick)。
3. **申請者はその step のゲージで決まる** — [`scheduler.py:1550-1552`](../../src/society/engine/scheduler.py) `a.drive >= _eff_thr(a) and step >= a.refractory_until`。[`scheduler.py:1553`](../../src/society/engine/scheduler.py) で **ゲージ降順**にソート(id 順バイアスなし)。
4. **固定の前景/背景リストが存在しない** — 上位 LOD の受益者は「ゲージが立った順に予算が尽きるまで」。[`lod.py:3-6`](../../src/society/cognition/lod.py) が明記: 発火判定は v1 の即時トリガー surprise_of から **欲求駆動発火へ移行(Phase A)** = 全員思考への転換で固定 tier を撤廃。
5. **発火後は不応期+ゲージリセット** — [`drive.py:192-196`](../../src/society/cognition/drive.py) `on_fire`(不応期 refractory_steps・ゲージ×0.20)。→ 直近発火した個体は次数 step は退き、他の個体に順番が回る = **まんべんなさの機構的担保**。
6. **抽選落ちはゲージを数十%減衰して再蓄積** — [`drive.py:199-201`](../../src/society/cognition/drive.py) `on_reject`。落ちても消えず、後の step で再挑戦 = 背景個体も見捨てられない。

→ §6 の実測で、この機構が生む熟慮回数分布の **Gini(まんべんなさ)** を定量する。

---

## 6. 計算リソース × シミュ時間の実測比較

ハーネス: [`scripts/bench_lod.py`](../../scripts/bench_lod.py)(テスト [`tests/test_bench_lod.py`](../../tests/test_bench_lod.py))。

### 6.1 測り方
- **backend=mock・cache=false**(純計算時間)・**同一 seed=42 を全構成で共有**・**直列実行**(並列にしない=計測が汚れる)。
- **wall** = `Simulation` 構築 + `sim.run()`(python 起動/import は除外、`time.perf_counter`)。
- **LLM 呼数(purpose 別)** = L1b(`sim.logger.llm_calls`)を purpose で集計。
- **エージェント別 熟慮回数** = L1b の `agent_id` 別件数(= その個体が実際に上位 LOD=思考へ入った回数)。分布は **在場全個体(思考 0 回を含む)** で採り、**Gini↓ = まんべんなさ↑**。
- **ピーク RSS** = 子プロセスで 1 構成を走らせ、親が **外部 PowerShell `Get-Process -Id <pid>` の WorkingSet64** をポーリングした最大値(ctypes は Windows で黙って 0 を返すため不可)。
- **構成**: (a) 現行フル=全員思考+行間+N比例0.15 / (b) 固定cap300(旧来) / (c) density 0.05/0.15/0.30 / (d) drive 感度 強(decay0.01)/弱(decay0.05) / (e) S7 ON(参考)。

<!-- BENCH_RESULTS_START -->
### 6.2 計算リソース × シミュ時間

mock・n=1000・144step・seed=42・直列・cache=false。wall=Simulation 構築+run(python 起動/import 除外)。
peakRSS=子プロセスの WorkingSet64 を親が外部 PowerShell `Get-Process` でポーリングした最大値。

| 構成 | budget/step | run(s) | ms/step | LLM呼 | LLM/step | peakRSS(MB) | events/step |
|---|---:|---:|---:|---:|---:|---:|---:|
| 固定cap300(旧来) | 300 | 68.99 | 479.1 | 32581 | 226.26 | 661.32 | 4294.7 |
| 現行フル(全員思考+行間+N比例0.15) | 150 | 54.18 | 376.3 | 18164 | 126.14 | 578.66 | 3357.5 |
| N比例 density0.05 | 50 | 35.39 | 245.8 | 7334 | 50.93 | 480.10 | 2467.4 |
| N比例 density0.15 | 150 | 56.37 | 391.5 | 18289 | 127.01 | 624.80 | 3612.0 |
| N比例 density0.30 | 300 | 63.58 | 441.5 | 32581 | 226.26 | 679.11 | 4294.7 |
| drive高感度(decay0.01) | 300 | 64.82 | 450.2 | 32585 | 226.28 | 685.87 | 4469.7 |
| drive低感度(decay0.05) | 300 | 67.20 | 466.7 | 32188 | 223.53 | 689.22 | 4432.7 |
| S7方針キャッシュON(参考) | 150 | 43.78 | 304.0 | 9528 | 66.17 | 575.11 | 3109.0 |

### 6.3 熟慮回数の分布(在場全1000個体・思考0回を含む。**Gini↓ = まんべんなさ↑**)

| 構成 | 平均 | 中央 | p90 | p99 | 最大 | coverage | 思考0の人数 | **Gini** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 固定cap300(旧来) | 32.58 | 34 | 45 | 52 | 57 | 0.998 | 2 | **0.190** |
| 現行フル(全員思考+行間+N比例0.15) | 18.16 | 19 | 27 | 33 | 36 | 0.998 | 2 | **0.218** |
| N比例 density0.05 | 7.33 | 4 | 19 | 26 | 30 | 0.944 | 56 | **0.518** |
| N比例 density0.15 | 18.29 | 19 | 27 | 33 | 36 | 0.997 | 3 | **0.227** |
| N比例 density0.30 | 32.58 | 34 | 45 | 52 | 57 | 0.998 | 2 | **0.190** |
| drive高感度(decay0.01) | 32.59 | 34 | 46 | 51 | 57 | 0.998 | 2 | **0.185** |
| drive低感度(decay0.05) | 32.19 | 34 | 45 | 50 | 57 | 0.998 | 2 | **0.182** |
| S7方針キャッシュON(参考) | 9.53 | 10 | 14 | 18 | 22 | 0.998 | 2 | **0.210** |

### 6.4 熟慮回数ヒストグラム(バケット別 人数、合計=1000)

| 構成 | 0 | 1 | 2 | 3-5 | 6-10 | 11-20 | 21+ |
|---|---:|---:|---:|---:|---:|---:|---:|
| 固定cap300(旧来) | 2 | 0 | 4 | 22 | 27 | 89 | 856 |
| 現行フル | 2 | 1 | 8 | 32 | 111 | 460 | 386 |
| N比例 density0.05 | 56 | 123 | 136 | 301 | 93 | 223 | 68 |
| N比例 density0.15 | 3 | 2 | 8 | 46 | 114 | 414 | 413 |
| N比例 density0.30 | 2 | 0 | 4 | 22 | 27 | 89 | 856 |
| drive高感度(decay0.01) | 2 | 0 | 6 | 16 | 31 | 79 | 866 |
| drive低感度(decay0.05) | 2 | 1 | 4 | 17 | 21 | 85 | 870 |
| S7方針キャッシュON(参考) | 2 | 7 | 12 | 121 | 474 | 382 | 2 |

### 6.5 LLM 呼数の purpose 内訳(kind別)

| 構成 | 総LLM呼 | 上位 purpose 内訳(呼数) |
|---|---:|---|
| 固定cap300(旧来) | 32581 | social=17600, reply=8142, unknown_word=3901, reflect=856, solo=755 |
| 現行フル | 18164 | social=14722, unknown_word=1195, reflect=850, reply=563, plan=243 |
| N比例 density0.05 | 7334 | social=5278, reflect=865, unknown_word=442, plan=273, solo=165 |
| N比例 density0.15 | 18289 | social=14840, unknown_word=1081, reflect=855, reply=632, plan=253 |
| N比例 density0.30 | 32581 | social=17600, reply=8142, unknown_word=3901, reflect=856, solo=755 |
| drive高感度(decay0.01) | 32585 | social=17945, reply=7860, unknown_word=3928, reflect=873, solo=677 |
| drive低感度(decay0.05) | 32188 | social=17656, reply=8075, unknown_word=3538, reflect=858, solo=782 |
| S7方針キャッシュON(参考) | 9528 | social=6593, reflect=864, unknown_word=718, reply=428, solo=251 |

### 6.6 読み取り(まんべんなさ・計算リソース)

1. **まんべんなさ(Gini)は「step 予算が需要に対してどれだけ締まっているか」でほぼ決まる。**
   - 予算が滅多に律速しない域(budget≈300: cap300 / dens0.30 / drive_hi / drive_lo)= **Gini 0.18–0.19・思考0は 2 人・21回以上思考が 856–870 人**。極めて均等。
   - 中庸(budget=150: full / dens0.15)= Gini 0.22・思考0は 2–3 人。まだ十分均等。
   - きつい(budget=50: dens0.05)= **Gini 0.52・思考0が 56 人**に急増。予算が強く律速し、需要の高い個体へ思考が集中する。
   → 「全員にまんべんなく」を Gini で担保したいなら **予算を需要に対して痩せさせない**のが要点。**refractory + 抽選落ちゲージ減衰**([§5](#5-流動性の確証コード根拠の要約))が働き、budget≥150 では **coverage 0.998(思考0は終日 outside の来街者 2 人のみ)** = 恒久的に無視される個体はいない。

2. **N 比例 density0.30 は N=1000 で固定 cap300 と完全一致**(Gini・LLM 呼・ヒストが同一)。n_proportional の価値は「同一 N での均等化」ではなく、**N が増えても密度(1人あたり思考量)を一定に保つ**こと。固定 cap は N が増えると 1 人あたりが痩せ、Gini が悪化する側に働く。

3. **drive 感度(decay)の効果は budget が緩い域では小さい**(drive_hi 0.185 vs drive_lo 0.182・LLM 32585 vs 32188)。予算が律速しないと「考えたい人はほぼ全員考えられる」ため decay の差が埋もれる。感度ノブが効くのは **予算がきつい域**(そこで誰が枠を取るかが変わる)。

4. **壁時間・RSS は LLM 呼数とイベント量にほぼ比例。** 35秒(dens0.05, 7334 呼)〜69秒(cap300, 32581 呼)。ピーク RSS 480–689MB は **イベントのメモリ蓄積**(events/step×144)が主因。1 構成 n=1000×144 は **1 分前後**で回る(全 8 構成 直列で ~7 分)。

5. **S7 方針キャッシュ(参考)は総 LLM 呼を 18164→9528(約 48% 減)**と大きく削るが、**social も 14722→6593 と激減**している。これは plan の再利用が **当日の行動計画→軌跡→同席機会を変える間接効果**を含むため(直接のキャッシュ・スキップだけではない)。=「同一世界での純粋なコスト削減」として読めない。本番採否を **既定 OFF・ブラインド A/B 待ち**にしている根拠と整合。

> 実測 JSON: `runs/_bench_lod/comparison.json`(gitignore 対象=非コミット)。再現: `PYTHONIOENCODING=utf-8 python scripts/bench_lod.py --agents 1000 --steps 144`。
<!-- BENCH_RESULTS_END -->

---

## 7. 本番プロファイルの思考リソース構成 推奨

ユーザー方針(実験用 LOD を全 OFF・思考タイミング系のみ ON)に沿った推奨:

### 7.1 ON にする(思考タイミング系)
| キー | 値 | 理由 |
|---|---|---|
| `planning.enabled` | true(既定) | 朝計画=当日行動の土台。全員一様・R1 安全 |
| `k.writeback` | free | 夜内省の書き戻し(k\* 研究の主処置) |
| `reflection.deep.enabled` | **true** | 出来事誘発の深い内省=固定周期より現実的。誰が深く考えるかが経験で流動 |
| `reflection.implicit_self.enabled` | **true** | 無意識の自己更新(裏で回る系) |
| `lod.n_proportional.enabled` | **true**(density=0.15) | **N に比例して全員思考の密度を維持** = 「まんべんなく」の本丸。固定 cap は N が増えると 1 人あたりが痩せる |
| `prompts.interstitial.enabled` | **true** | 行間 S2=発火の質を上げる(呼数不変) |
| `conversation.enabled` | **true** | 行間 S3=記録に残る会話密度を LLM 呼ゼロで確保。C2→C1 昇格が drive ゲートへ流入 |
| `routine.stochastic.enabled` | **true**(要ユーザー判断) | 行間 S4=下位 LOD(routine)の忠実度。呼数不変 |
| `drive.boredom.enabled` | **true**(要ユーザー判断) | 行間 S5=下位 LOD 個体の自発的な上位復帰(脱馴化) |
| `drive.drift.enabled` | **true 推奨(討議)** | E2=上位 LOD 確率の **経験由来**の時変調整(§4 の正道ノブ) |

### 7.2 OFF に保つ(実験用 LOD)
| キー | 値 | 理由 |
|---|---|---|
| `lod.input_res.enabled` | false | 入力解像度は別軸の実験機構 |
| `model.tiers` / `model.router` | null | モデル級 LOD は計算削減軸。本番は単一モデルで可 |
| `cognition.policy_cache.enabled` | false | S7=既定 OFF 運用は決定済み(再利用は多様性を削る) |
| `world.scene_desc.enabled` | false | input_res 従属 |
| agent_tier | (未実装) | 固定 trait 階層は k\* 交絡・生得性裏口(§4) |

### 7.3 予算(N 比例)の指針
- 固定 `lod.max_llm_per_step` は N が動くと 1 人あたりの思考密度が変わる。**本番は `n_proportional`(density で密度を宣言)**が「全員にまんべんなく」の趣旨に合う。
- density=0.15 は 200 体較正 day1 実測(4,293 呼/144step/200 体)由来([`config.yaml:562-566`](../../conf/config.yaml))。実 GPU スループットで上限が決まるため、**実機 tok/s 実測(`scripts/bench.py --lod`)で density を右サイズ**する。
- ピーク RSS / 壁時間の density 依存は §6 の実測表で判断する。

### 7.4 「上位 LOD 確率をパラメータ調整」の本番実装方針
- **trait 直結は入れない**(§4 却下)。
- 状態由来ノブ(E2 ドリフト・退屈・drive.weights 再調律)で調整する。**さらなる状態変調(fire_weight の直近顕著性変調)を入れたい場合は src 変更を伴うため、実装前に決定アジェンダで合意する**([ask-before-extending] / [pre-coding-alignment])。
