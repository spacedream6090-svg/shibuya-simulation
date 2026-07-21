# 交通物理の「間接影響」分析 = 遅延伝播が LLM 発火に与える二次効果(第39バッチ / SUMO-INDIRECT)

作成日: 2026-07-21
体制: Opus 調査(**調査・分析のみ・コード/conf 変更なし・コミットなし**・本ファイル1本)
問い(ユーザー 2026-07-21): 「SUMO の交通シミュレーションについては、信号でタクシー到着が遅れた・
徒歩の移動で引っかかって遅れた等、**LLM を起動する瞬間に直接は関係なくても間接的に影響を与える
可能性**がありそうじゃない? この影響についても考えてまずはレポートを作ってほしい」。

> **本書は差分**。SUMO 連成の実装案(タクシー taxi device / pt バス / ハイブリッド構成 / 決定論の
> 落とし穴)は **[sumo-live-transit.md](sumo-live-transit.md)** と **[sumo-integration-research.md](sumo-integration-research.md)**
> に既述。ここでは重複を避け、**「到着遅延という物理量が、直接は無関係な LLM 発火の総量・内容・
> タイミングにどう間接波及するか」**と、それが**研究の掟(R1)を破らないか**の一点に絞る。
> タクシー配車 v1(sumo-live-transit.md の v-Ride-1)実装の前提分析。

---

## 0. 要旨(TL;DR)

- **問いは的を射ている。** 到着遅延は「LLM を呼ぶか/いつ/何を言わせるか」に**間接波及する経路が
  現行シムに既に多数存在**し(下記 §1 で全数棚卸し)、SUMO 遅延はその**既存経路に上乗せ**する。
  新種の魔物ではなく、**既に日常的に起きている物理→認知の摂動が一つ増える**という位置づけ。
- **しかも結論は既に確定している。** 「到着遅延で会う人が変わり、会話が変わり、発火の中身が変わる」
  のは **`career G5 / crowd G4 / 健康 H1 / 世帯 H2 / 商業 H3 / 災害 H4 / 内面`** と**構造的に同型**で、
  コードベースは既にこの一群に対する**掟(R1)と検収パターン(FixedLLM + compute_matched で呼数一致)**を
  確立している(§3)。SUMO 遅延は**この確立済みカテゴリにそのまま収まる**。
- **物理が行動・内容を変えるのは問題ない**(それが現実再現の目的=`ON!=OFF` は仕様)。**問題になるのは
  3点だけ**: (a) k 条件で物理の扱いが変わる、(b) SUMO 側の非決定論が CRN(同 seed 比較)を壊す、
  (c) LLM 呼数が k に依存する。**(a)(c) は既存の掟でカバー済み、(b) だけが SUMO が新たに持ち込む
  唯一の load-bearing リスク**(外部プロセス連成=純 Python の既存物理には無かった非決定論の窓)。
- **定量**: 既存の歩行者混雑減速は `runs/rehearsal_pool10k`(1万体1日)で **move_segment の 1.47% に発火・
  平均減速36%(最大70%)**。SUMO の信号待ち期待値は **1 基あたり 5.5〜13.6 秒**、タクシー配車待ちも
  分オーダーで、**大半は 10 分(600秒)step の量子化に吸収される**。観測に出るのは「遅延が step 境界を
  跨いだとき」だけ=既存混雑と同様に**疎で確率的**。呼数総量への一次効果は小さい。
- **設計勧告(§5)**: SUMO 側決定論(seed 固定・`--random` 禁止・TraCI 配車順を sim 状態の純関数化=
  id ソート)を **precondition** に置けば (a)(b)(c) は全て守れる。遅延を **観測イベント(`ride` payload に
  `wait_s`/`ride_s`/`delay_s`)として必ず記録**し、間接影響を事後に測れる状態で入れること。
  sumo-live-transit.md の go/no-go 4条件に **「遅延イベントの観測可能性」と「n_proportional 予算の
  present 依存性の点検」**を追記提案。

---

## 1. 既存の「物理 → 認知(LLM 発火)」間接チャネルの棚卸し

**現行シムには既に、物理量(移動・位置・時刻・混雑)が LLM 発火の総量・内容・タイミングへ間接波及する
経路が多数ある。** SUMO を語る前に、まずこれらが「ゴールデン/決定論の中でどう扱われているか」を確定する。

### 1.1 歩行者の混雑減速(最重要=SUMO 徒歩遅延と同じ穴)

`scheduler.py:_phase_move` が、同一有向エッジ上のエージェント数 `count` が `edge_capacity`(既定 **20**、
`conf/config.yaml:191`)を超えると減速係数 `factor = max(0.3, capacity/count)` を掛ける。**この 1 つの物理量が
5 本の認知チャネルへ分岐する**:

| # | 経路 | file:line | 発火への効き方 | 決定論/ゴールデン |
|---|---|---|---|---|
| C1 | **移動距離 → 到着 step** | `scheduler.py:825-828, 831` `budget_m = speeds[mode]*factor` | 減速で到着が遅れる → 会う人(co-location)が変わる → hear/会話/顕著性が変わる → **発火の内容とタイミング** | 純関数(占有数は当 step の状態から決定的に数える。乱数なし) |
| C2 | **混雑 → drive ゲージ** | `scheduler.py:868-869` `drive.add(agent,"congestion",scale=(1.0-factor))`(重み 0.30 = `drive.py:22`) | ゲージ蓄積 → 閾値超えで**熟慮発火そのものを誘発**(発火確率↑) | ゲージは観測量のみ入力(k 非依存)。発火は `_phase_drive` の共有予算抽選 |
| C3 | **混雑 → arousal(覚醒)** | `scheduler.py:870-871` `_arouse(...,congestion=(1.0-factor))` → `factors/affect.py:49-62` → `factors/update.py:145-172` | 覚醒 → `effective_threshold` を逆U字変調(`drive.py:88-98`, `scheduler.py:1638`)→ **発火閾値が動く** | affect OFF(gain=0)は完全 no-op=バイト一致。ON でも入力は観測量のみ |
| C4 | **混雑 → grievance → 深い内省** | `scheduler.py:865` `on_congestion`→`factors/update.py:116-122`→`_bump`(61-76)→`_impact_note`(79-107) | grievance↑ が `impact_today` ゲージに積まれ、閾値超えで **深い内省 LLM を incubation 後に予約**(`reflection_trigger`/`deep_due_day`) | `|Δstate|` は k 非依存近似。**内省呼数は compute_matched で off/free 一致**(§3) |
| C5 | **混雑 → 発火時のプロンプト内容** | `scheduler.py:1728-1729` → `deliberate.py:307` 「ひどい混雑に巻き込まれた」 | reason=`congestion` で発火すると**発話プロンプトの枠組みが変わる**(呼の中身) | 内容のみ=呼数不変。文脈選択は決定論 |

さらに C6: `scheduler.py:872-873` で `on_congestion` の `|Δgrievance|` を `drive.add("state_change")`(重み 0.50)
にも回す(状態変化=顕著な出来事 → ゲージ)。**混雑一つで C2/C3/C4/C6 の 4 系統がゲージ・閾値を叩く。**

### 1.2 新奇な場所(初訪問)

`scheduler.py:889-892`: 初訪問ノード到達で `drive.add("novel_place")`(0.35)+ `_arouse(novelty=1.0)`。
**到着 step が変われば「どこに初めて着くか・いつ着くか」が変わる** → novel_place の発火列が変わる。C1 の下流。

### 1.3 終電制約(公共交通の運行時間帯ゲート)

- 帰還: `scheduler.py:777-780` — 駅経由の帰還は `transit.has_service(sim_min)` が False(終電後)なら
  **その step は帰れない**(`continue`=始発待ち)。
- 退出: `routine.py:723` — 駅経由の退出も運行中のみ。
- 実体: `transit.py:106-109` `has_service`(`suspended`=災害運休 or 運行時間帯外で False)。

**含意**: 到着遅延で「終電に間に合う/間に合わない」が変わると、**帰宅不能 → 夜間の在場・行動列が丸ごと
変わる**。これは離散的で影響が大きい二次効果。既定は乱数なしの時刻純関数(`suspended` は disaster OFF で
常に False=バイト一致)。

### 1.4 背景交通の信号・車線容量(現状エージェント非接続=確認済み)

`traffic.py` の **od モード**は信号(`_signal_delay_m`, `traffic.py:257-262`)と車線容量減速
(`_step_od`, `traffic.py:293-296`)を持つが、**これは `TrafficFlow` 内部の通過車両リストにしか作用しない**。
モジュール冒頭に明記: 「このモジュールは走行の物理だけを扱い、**エージェントの内部状態には一切触れない**」
(`traffic.py:12`)。信号遅延・容量減速は `self.cars`(=非エージェント車両)の `budget` を削るだけで、
`log_extra`(`traffic.py:344-347`)も車位置を可視化に出すのみ。

- **確認**: 背景 od 車の期待遅延は**現状エージェントに一切接続していない**(監査 [traffic-signals-audit.md](traffic-signals-audit.md)
  の結論「od でも効くのは背景車両のみ・歩行者は信号で止まらない」と一致)。
- 既定は `mode: ambient`(`conf/config.yaml:203`)。ただし **`runs/rehearsal_pool10k` は `mode: od` で実行**
  済み(§4)= od でも R1 無風(車の遅延がエージェントに漏れないため)を実証している。
- **SUMO タクシー v1 が変えるのはまさにここ**: 背景車の遅延を**エージェントが乗る車の到着 step へ初めて
  接続する**。だから「間接影響」の問いが立つ。

### 1.5 交通機関の現行実装(タクシー/簡易バス=遅延ゼロのオーバーレイ)

`routine.py:_ride_extra`(505-541): 距離 > `min_dist_m`(既定 600m)かつ所持金充分で、`stream("taxi",id,step)`
< `prob` なら taxi(バスは停留所 <100m。`transit.py:BusNetwork.find_ride`)。**決定論・LLM 非関与**。
実行は `scheduler.py:880-883` `_charge_ride` で到着時に運賃を払うだけ。**乗車は `mode="car"` で通常ルートを
車速で走る=配車待ち・渋滞・遅延は現状ゼロ**(sumo-live-transit.md §1 の「背景の一種」)。
→ **SUMO v1 はこの `_ride_extra`→到着 step の間に「配車待ち + 渋滞込み乗車時間」を挿入する**のが本質。

### 1.6 その他の「物理が発火に間接影響する」前例(SUMO と同型の既存機構)

| 前例 | 機構 | file:line | 発火への間接効き |
|---|---|---|---|
| **天気** | 悪天 → grievance(C4 と同じ impact ゲージ経路)+ プロンプト1行注入 | `scheduler.py:3063-3064` `discomfort_delta`→factors hook / `deliberate.py:181` `weather_line` | 内省予約に間接寄与(呼数は compute_matched で担保)。プロンプトは内容のみ=呼数不変。全員共通 k 非依存 |
| **群集(年中行事 G4)** | 群集日に自由時間の行き先を集会ノードへ確率的に寄せる | `routine.py:563` `_crowd_dest`(専用 stream "crowd") | **物理位置 → co-location** を変える(=`ON!=OFF`)。呼数は compute_matched で k 不変(`annual.py:13`) |
| **確率的実行(S4)** | 寄り道=目的地手前で近傍 POI 立寄り / 中断=活動途中離脱 | `routine.py:173,181`(stream "detour")/ `199`(stream "interrupt") | 到着時刻・滞在をずらす → co-location。乱数は (id,step) 固定=CRN 安定。既定 OFF でバイト一致 |
| **退屈/好奇心(S5)** | 長居(物理入力)でゲージ蓄積 → 閾値で内発的探索(未訪問 POI へ move) | `drive.py:213-256` / `routine.py:266` `_maybe_boredom_explore`(stream "boredom") | 位置を変える(発話 LLM は増やさない=呼数不変)。入力は物理量のみ・k 非依存。既定 OFF |
| **健康 H1 / 商業 H3 / 世帯 H2 / 災害 H4 / キャリア G5** | 疲労で休息・閉店で行先変更・世帯同居・運休・失業=いずれも**物理位置を変える** | `health.py:15-19`/`commerce.py:22-26`/`household.py:19-24`/`disaster.py:22-27`/`scheduler.py:3183-3184` | **すべて「co-location を変えうる=`FixedLLM で ON!=OFF`」と明記**し、呼数不変は compute_matched で担保 |

**棚卸しの結論**: **「物理量が位置・時刻・混雑を変え、それが co-location・顕著性ゲージ・プロンプト内容を
介して LLM 発火の中身とタイミングに間接波及する」チャネルは、現行シムの中核設計そのもの**。SUMO 遅延は
新カテゴリではなく、**この確立済みの一群に到着 step を経由して合流する**。

---

## 2. SUMO 連成が加える新しい間接影響の分類

到着遅延(信号待ち・配車待ち・渋滞巻き込まれ)の伝播経路を体系化する。各経路を **[呼数総量]/[呼の内容]/
[呼のタイミング]/[k 非依存性]** の 4 軸で評価(◎=影響なし/健全, ○=変わるが仕様内, △=要監視)。

### 経路① 個体の行動列シフト(会う人が変わる)
到着が 1 step 遅れる → その step に居合わせる相手が変わる → `hearers_of`(`scheduler.py:1660`)が返す同席者
集合が変わる → **対面会話の確定発火(`social_face`)の相手・成否が変わる**。
- **呼数総量 ○**: 対面発火も共有予算 `sim.budget.take()` を消費(`scheduler.py:1665,1678`)。予算が律速なら
  総量は上限で頭打ち(§3.4)、非律速なら要求者数の変動で微増減しうる。
- **呼の内容 ○**: 相手が変わればプロンプトの同席者記述が変わる(仕様=現実再現)。
- **呼のタイミング ○**: co-location の step がずれる。
- **k 非依存性 ◎**: 同席判定は物理位置のみ入力(k・belief を見ない)。§1.6 の G4/H1 群と完全同型。

### 経路② 計画実行のズレ → S1「失敗の階段」/ S4 中断の発火率変化
到着遅延で計画アンカー(fixed 時刻)に間に合わない → S1 日課計画の**修復→再試行→前日流用の階段**が
より頻繁に起動 / S4 の per-move 中断・寄り道判定が別の状態文脈で起きる。
- **呼数総量 ◎**: 朝の計画は **k に依らず全員・毎朝 1 回**(`scheduler.py:649` 明記)=遅延で増減しない。
  失敗の階段(修復)も **非LLM の決定論**。S4 detour/interrupt も **非LLM**(専用 stream)。
- **呼の内容 ○**: 計画の実行結果が変わればその後の発話の文脈が変わる。
- **呼のタイミング ○**: 中断/寄り道の判定文脈がずれる。ただし乱数ドロー自体は (id,step) 固定=**CRN 安定**
  (物理は「どの文脈でドローを適用するか」だけを動かし、ドロー値は変えない)。
- **k 非依存性 ◎**: detour/interrupt/計画修復はいずれも k・belief 非参照。

### 経路③ C2/C3 構造化会話の相手・回数変化
到着遅延で同席ペアが変わる → `conversation.py`(C2/C3, `scheduler.py:1697-1704`)の決定論ペア列挙が変わる →
C2→C1 昇格で drive ゲージを押す相手・量が変わる。
- **呼数総量 ◎**: C2/C3 は **LLM を 1 本も足さない**(専用 stream c2_meet・非LLM)。C1 昇格は既存 drive 経路
  へ合流するだけ。
- **呼の内容/タイミング ○**: 会話相手が変われば下流の発火文脈が変わる(仕様)。
- **k 非依存性 ◎**: ペア列挙は空間索引=物理位置のみ。

### 経路④ 顕著性ゲージ蓄積の変化 → 熟慮/内省回数の個体差
遅延=混雑巻き込まれ(C2/C3/C4)や到着ズレが、drive ゲージ・arousal・impact_today ゲージの蓄積を変える →
**個体ごとの発火頻度・深い内省の予約タイミングが変わる**。
- **呼数総量 △→◎**: 熟慮(drive 発火)は**共有予算で頭打ち**(§3.4)。深い内省は**compute_matched で off/free
  呼数一致**(§3.3)。**両ゲート機構が呼数の k 依存を封じている**ため、蓄積が変わっても総量の k 依存は出ない。
- **呼の内容/タイミング ○**: 誰がいつ発火するかの並びは変わる(仕様)。
- **k 非依存性 ◎**: ゲージ入力(混雑量・`|Δstate|`・novelty)は**すべて観測量**(`factors/affect.py:53` 明記
  「belief/k を参照しない」)。SUMO 遅延量も同じく観測量。

### 経路⑤ 在場曲線の微小変化(タクシー/バス遅延で退出・帰宅が遅れる)
配車待ちで退出が遅れる/終電に乗り遅れて滞留 → **その step の在場人数 `len(sim.agents)` が変わりうる**。
- **呼数総量 △(唯一の要監視点)**: 既定は予算固定(`max_llm_per_step: 300`, `n_proportional.enabled: false`)
  なので**在場が変わっても予算=呼数上限は不変**。しかし **`n_proportional` を ON**(rehearsal 実績)にすると
  予算 = `ceil(density × len(agents))`(`simulation.py:885`)=**在場人数に比例**。SUMO 遅延が在場を系統的に
  押し上げると **予算(=呼数総量)が動く**。これは既存の全 co-location 機構でも原理的に起きる「下流分岐」
  だが、**遅延=退出時刻の直接操作なので在場感度が既存より高い**。§3.4 で k 依存性を精査。
- **k 非依存性 ○(条件付き)**: density 定数は k 非依存。予算が k 世界間で食い違うのは**軌道の下流分岐**
  であって機構が k を読むからではない(§3.4)。ただし n_proportional ラン限定で**要実測**。

### 経路⑥ イベント参加の遅刻
`scheduler.py:907-909` `tools.on_arrive`(到着時にイベント参加確定/ビラ閲覧/屋台購入)。到着遅延で
**イベント開始に間に合わない → 参加確定が別 step or 不成立**。
- **呼数総量 ◎**: on_arrive の処理は非LLM(参加記録・購入)。発火は既存 drive 経路で頭打ち。
- **呼の内容/タイミング ○**: 参加成否が下流の話題・co-location を変える(仕様)。
- **k 非依存性 ◎**: 到着 step・イベント時刻の純関数。

**§2 の総括表**:

| 経路 | 呼数総量 | 呼の内容 | 呼のタイミング | k 非依存性 |
|---|---|---|---|---|
| ① 行動列シフト | ○(予算律速で頭打ち) | ○ 仕様 | ○ 仕様 | ◎ |
| ② 計画/S1/S4 | ◎(計画は全員毎朝1回・修復/S4は非LLM) | ○ | ○(ドローは CRN 安定) | ◎ |
| ③ C2/C3 会話 | ◎(非LLM) | ○ | ○ | ◎ |
| ④ 顕著性ゲージ | ◎(予算+compute_matched で封) | ○ | ○ | ◎ |
| ⑤ 在場曲線 | **△ n_proportional 時のみ要監視** | ○ | ○ | ○(下流分岐) |
| ⑥ イベント遅刻 | ◎ | ○ | ○ | ◎ |

**要点**: **「内容」と「タイミング」は全経路で変わる(=これが現実再現の目的)。「呼数総量」の k 依存は
経路⑤(n_proportional 予算)を除き、予算上限と compute_matched の 2 つのゲート機構で構造的に封じられている。**

---

## 3. 研究の掟(R1)との整合分析(本レポートの核心)

### 3.0 R1 の正確な定式化と「k」とは何か

**k = `k.writeback` 処理**(`off` | `free` | `degraded` | `sham`、`config.py:226-229`, `scheduler.py:706-707`)。
深い内省の結果を belief に書き戻すか否か=「世界を変える個体」の認知能力の操作化。k 掃引は同 seed で
off/free 等を比較し、創発(k*)を測る。**R1 の要求は「物理が行動・内容を変えること」ではない**(それは
歓迎)。**R1 が守るべきは次の 3 つだけ**:

- **(a) k 条件によって物理の扱いが変わらない**(決定論チャネルに k が混入しない)。
- **(b) 非決定論が混入しない**(SUMO 側の再現性が崩れると同 seed 比較=CRN が死ぬ)。
- **(c) LLM 呼数が k に依存しない**(掃引の交絡を避ける)。

コードベースの標準文言がこれを正確に表す:
> 「物理位置=対面 co-location を変えうる(=**FixedLLM で `ON!=OFF` になりうる**=career G5 / crowd G4 /
> 健康 H1 / 世帯 H2 / 商業 H3 と同型)→ **呼数不変は compute_matched 下の k 不変性(k=free==k=off の
> 呼数一致)で担保する**」(`commerce.py:24-26`, `health.py:17-19`, 他多数)

つまり **`ON!=OFF`(物理を入れると挙動が変わる)は許容**、守るのは **`k=free の呼数 == k=off の呼数`** のみ。

### 3.1 (a) k 依存の混入 — SUMO 側で守るべき条件

**SUMO の物理(信号・配車・渋滞)は、エージェントの k や belief を一切入力にしてはならない。**
具体的には TraCI 配車(`dispatchTaxi`)の割当が**「世界を変える個体だから先に配車」等になってはいけない**。

- **既存物理は全て合格**: 歩行者混雑(占有数=物理)・od 信号(node ハッシュ=物理)・終電(時刻=物理)は
  k を読まない。
- **SUMO も設計次第で合格**: 配車・信号・渋滞の入力は**車両位置・予約・fleet 状態=すべて物理**。
  sumo-live-transit.md §4「決定論の勘所」が要求する**「配車の割当順がシミュ状態の純関数(dict 反復順・
  wall-clock 禁止、予約は id ソート)」**を守れば、k はどこにも入らない。**判定: (a) は達成可能。**

### 3.2 (b) 非決定論の混入 — SUMO が新たに持ち込む唯一の load-bearing リスク

**これが SUMO 固有の新しい危険。** §1 の既存物理は全て**純 Python・同一プロセス・RngHub.stream 由来の
決定論**だった。SUMO は**外部プロセス**で、これまで無かった非決定論の窓を開ける:

- スレッド並列ルーティングの順序非決定・`--random`・wall-clock 依存・libsumo/traci の呼び出し順ゆらぎ。
- これが混入すると**同 seed の 2 回のランで到着 step が食い違う → CRN(同 seed ペアで k を比較)が死ぬ**。
  CRN が死ぬと、k の効果と「たまたま SUMO が別の乱数を引いた」効果が分離不能=**掃引の統計が崩壊**。

**precondition(sumo-live-transit.md §4 の主張を継承)**: SUMO を `--seed` 固定・`--random` 禁止・
スレッド並列ルーティング禁止・TraCI 介入を sim 状態の純関数化。**検収**: 同 seed で ≤24-step を 2 回回し、
**乗車イベント列・到着 step・L1 が byte 一致**(OFF)。**判定: (b) は precondition 遵守が絶対条件。
これが v-Ride-1 の go/no-go の中核**(§5)。

### 3.3 (c) 呼数の k 依存 — 既存 2 ゲートで構造的に封じられている

呼数が k に依存しないことを、コードベースは**2 つの独立したゲート**で担保しており、**SUMO 遅延はどちらの
ゲートも迂回しない**:

1. **深い内省 = compute_matched**(`reflection.py:382-387`): `k.writeback=off` でも内省 LLM を実行し**結果を
   全破棄**(`discard=True`)。→ **off と free で `generate()` 呼数が完全一致**。SUMO 混雑が impact ゲージ
   (C4)を押しても、内省が予約されれば off/free 双方で同じく実行される=**呼数一致は保存**。
   検収パターン: `test_commerce.py` 等が `_FixedLLM` + `controls.mode=compute_matched` + `k.writeback` 掃引で
   generate 呼数の完全一致を assert。**SUMO 機構も同じテストで担保すべき**。
2. **熟慮発火 = 共有 step 予算**(`lod.py:80-92` `LodBudget`): 全発火(対面 `social_face`・媒体・独り言)が
   `sim.budget.take()` を消費し、`_phase_drive` は要求者を `(-drive, id)` 順にソートして予算が尽きるまで配る
   (`scheduler.py:1653,1665,1678`)。**総発火数 ≤ `max_per_step`**。SUMO 遅延は**「誰が発火するか」の並びを
   変えるだけで、総数は上限で頭打ち**(§3.4)。

**要点**: **belief(k が書き換える唯一の量)は発火・スケジューリング機構のどこにも入力されない**
(`policy_cache.py:87` は belief/k/writeback/opinion/drive をキャッシュキーから**明示排除**)。発火機構の入力は
**物理位置・出来事量・時刻・config・専用 stream=すべて k 非依存の観測量**。SUMO 遅延量も同じ観測量。
→ **物理を足しても「呼数が k を見て変わる」経路は生まれない。**

### 3.4 対照実験(k 掃引)への影響 — 「カオス的分岐はあってよいが k 非依存でなければならない」

**論理の確認**: 物理遅延が**全 k 条件に同一に効く**(同 seed ペア=CRN)なら、k の主効果と交絡しない。
SUMO 物理は k を読まない(§3.1)ので、同 seed の off 世界と free 世界に**同一の物理ルール**が適用される。
→ **交絡しない。**

**破れうるケース(正直な分析)**: off 世界と free 世界は、**k 処理(belief 書き戻し)の効果で軌道が
分岐する**。分岐すると 2 世界のエージェント位置が食い違い、**同じ物理ルールでも経験する混雑・遅延が
食い違う**。これは「呼数上限の奪い合いで内容が分岐 → 以後カオス的分岐」であり、**現行の歩行者混雑でも
既に起きている性質**(混雑は位置に依存し、位置は k で分岐するから)。

**整理(掟の核心)**:
- **カオス的分岐(downstream divergence)は許容**。2 世界が違う経験をすること自体は k 処理の帰結であって
  交絡ではない。**「k 非依存」が意味するのは「物理機構が k を入力にしない」であって「物理の結果が 2 世界で
  同一」ではない**(それは分岐する世界では原理的に不可能)。
- **禁じられるのは (a) 機構が k を読む・(b) 非決定論・(c) 呼数の系統的 k 依存**の 3 つだけ。SUMO 遅延は
  (a)(b) を precondition で回避し、(c) は 2 ゲートで封じる。
- **唯一の残存監視点 = 経路⑤ × n_proportional 予算**: 予算 = `density × len(agents)`。もし free 世界の
  方が(k 効果で)系統的に長く滞在し在場が多いと、**free の予算 > off の予算 → 呼数が k と相関**しうる。
  **これは SUMO 特有ではなく既存の全 co-location 機構が持つ性質**だが、**遅延は退出時刻の直接操作なので
  在場感度が高く、増幅しうる**。ただし: **(i) 既定は予算固定(300)なので無風**、**(ii) n_proportional ラン
  では compute_matched + FixedLLM で off/free の総呼数差を実測して監視すべき**(既存機構でも本来必要な点検。
  SUMO はそれを顕在化させるだけ)。

**§3 の結論**: **SUMO 到着遅延は R1 と整合可能。** 掟の観点で SUMO が既存物理と違うのは **(b) 非決定論
リスクただ 1 点**(外部プロセス)。(a)(c) は既存の掟・ゲート・テストパターンにそのまま乗る。到着遅延が
発話の相手・内容・タイミングを変えるのは **`ON!=OFF`=仕様**であり交絡ではない。**「呼数の k 一致」だけを、
既存と同じ FixedLLM + compute_matched スモークで守り続ければよい。**

---

## 4. 定量の見積もり

### 4.1 現行の歩行者混雑減速の実測(`runs/rehearsal_pool10k`)

実測対象: 1 万体・144 step(=1 日)・`mode: od`・affect ON・boredom ON・`n_proportional` ON(density 0.15)・
`edge_capacity: 20`。歩行 800m/step(=4.8km/h)・自転車 2000・車 3500。

| 指標 | 実測値 |
|---|---|
| move_segment 総数 | 230,571 |
| **congestion < 1.0 の件数 / 比率** | **3,387 件 / 全 move_segment の 1.47%** |
| 混雑時の平均減速係数 | **factor 平均 0.64(=36% 減速)**、中央値 0.61 |
| 減速の分布(混雑分の内訳) | [0.30,0.40) 18.7%(=最大 70% 減速=床 0.30)/ [0.40,0.60) 27.7% / [0.60,0.80) 21.6% / [0.80,0.95) 22.6% / [0.95,1.0) 9.3% |
| 到着あたり move_segment 数 | **1.63**(=大半の移動は 1〜2 step で完了。中央値移動 657m < 800m/step) |
| フル速度 step(≥790m)の比率 | 42.4% |
| ride イベント(現行オーバーレイ) | taxi 817・bus 579 |
| drive_request → llm_deliberate | 566,582 → 167,689(**発火率 ~29.6%**=予算/抽選で律速) |
| 深い内省系 | reflection_trigger 8,633 / reflect 10,615 / boredom_explore 4,871 / detour 20,997 / interrupt 17,652 |

**解釈**:
- 混雑は **move_segment の 1.47% にしか発火しない**が、発火すると**平均 36%・最大 70% の減速**=強い。
  移動が 1〜2 step で完了する(657m 中央値)ため、**1 step 分の減速は容易に到着 step を 1 つ後ろへ押す**
  (657m の trip が factor 0.64 で ~420m しか進めなければ 2 step に化ける)。**「疎だが効くときは step 境界を
  跨ぐ」**のが混雑の実像。SUMO 遅延も同じ疎・確率的プロファイルを取ると予測。
- **発火率 29.6% = 予算/抽選が律速**。llm_deliberate 167,689 / 144 step ≈ **1,164 呼/step** に対し、満場時
  予算 ≈ `0.15×present`。**予算が(少なくとも混雑ピーク時は)binding** → §3.4 の「総数は上限で頭打ち」が
  実データでも成立傾向。**混雑・遅延は主に「誰が発火するか」を並べ替える。**

### 4.2 SUMO 遅延の想定規模と 10 分 step 量子化による吸収

- **信号待ち期待値**(現行 od の式 `_signal_delay_m`, `traffic.py:257-262`): 待ち = `r²·C/2`、赤率
  r ∈ [0.35, 0.55](`traffic.py:104`)・周期 C=90s → **1 基あたり 5.5〜13.6 秒**。タクシー trip が 5〜10 基
  通過しても **28〜136 秒**。**600 秒 step に対し 5〜23%=大半が量子化で吸収される。**
- **タクシー配車待ち**: SUMO taxi の `dispatch-period` 既定 60s + 最寄り空車の pickup 走行 = 通常**分オーダー**。
  相乗り(greedyShared)の回り道でも数分。**多くは 1 step 内に収まる**。
- **到着 step の算式**(sumo-live-transit.md §2.2): `ceil((呼んだ時刻 + 配車待ち + 乗車時間)/600)`。
  **観測に出るのは合計遅延が step 境界を跨いだときだけ**。跨がなければ到着 step 不変=完全無風。
- **結論**: SUMO 遅延の**一次効果は既存混雑と同オーダーの疎さ**(数%の trip で 1 step ずれ)。**呼数総量への
  直接影響は小さく**、影響は主に「たまに 1 step 遅れて会う人が変わる」という §2 の間接経路を通る。
  ただし **終電境界(§1.3)を跨ぐ遅延だけは離散的に大きい**(帰宅不能=夜間行動列が丸ごと変わる)ので、
  タクシー/バスの遅延が終電前後に集中する時間帯は要監視。

---

## 5. 設計勧告 — タクシー v1 で「間接影響を健全に保つ」チェックリスト

### 5.1 実装時の設計条件(4 象限)

**① 決定論(b の回避)**
- [ ] SUMO を `--seed` 固定・`--random` 禁止・スレッド並列ルーティング禁止で起動。
- [ ] TraCI 配車ドライバの割当順を **sim 状態の純関数**に(予約は id ソート・dict 反復順非依存・wall-clock 非参照)。
- [ ] `getTaxiFleet`/`getTaxiReservations` の照会タイミングを **step 境界に固定**(照会の曖昧さを消す)。
- [ ] 満車/積み残しの分岐も決定論に(seed 固定で再現)。

**② k 非依存(a の回避)**
- [ ] 配車・信号・渋滞の入力は**車両位置・予約・fleet・時刻=物理量のみ**。**k/belief/writeback/opinion/drive を
      配車判断に一切食わせない**(`policy_cache.py:87` の排除リストと同じ規律)。
- [ ] 到着 step の算式に k を入れない(`ceil((t+wait+ride)/600)` は純物理)。

**③ ゴールデン保護(既定無風)**
- [ ] 新 conf ノブ・**既定 OFF**(sumo-live-transit.md 大原則 R1)。OFF で**乗車イベント列・到着 step・L1 が
      byte 一致**(SUMO を一切呼ばない)。
- [ ] 乗車判断は既存の非LLM `_ride_extra`(`routine.py:505`)のまま=**LLM 呼数を 1 本も足さない**
      (SUMO は待ち時間と到着 step だけを変える)。
- [ ] ON は「別ゴールデン」として明示管理(到着 step が実際に変わる=`ON!=OFF` は仕様)。

**④ 観測(間接影響を事後に測れる状態)**
- [ ] `ride` イベント payload(`scheduler.py:600-603`)に **`wait_s`(配車待ち)・`ride_s`(乗車時間)・
      `delay_s`(信号・渋滞由来の超過)・`shared`(相乗り相手数)** を追加。**遅延を必ず記録**し、
      「この遅延がどの発火の並べ替えに効いたか」を事後に L2 で追える状態にする。
- [ ] **未配車/積み残しイベント**(`taxi_unmatched` 等)を記録=「捕まらない」体験の観測可能化。
- [ ] **在場曲線の点検指標**を L2 に出す(遅延起因の退出遅れ=経路⑤の監視)。

### 5.2 検収スモーク(§3 の 3 リスクを byte/count で示す)

- [ ] **決定論**: 同 seed ≤24-step を 2 回 → 乗車列・到着 step・L1 が byte 一致(ON 同士 / OFF はさらに
      SUMO 無効ランと一致)。→ (b) 担保。
- [ ] **呼数 k 一致**: `_FixedLLM` + `controls.mode=compute_matched` + `k.writeback` 掃引で、SUMO ON 時の
      **generate 呼数が k=free==k=off で完全一致**(`test_commerce.py` 等と同型テスト)。→ (c) 担保。
- [ ] **n_proportional 点検**(該当ランのみ): SUMO 遅延 ON/OFF で present 曲線と総呼数の差を実測。
      系統差が出るなら density を固定予算に切替 or 補正を検討(経路⑤)。

### 5.3 sumo-live-transit.md go/no-go 4 条件への追記案

sumo-live-transit.md §5 の v-Ride-1 判断材料 (1)〜(4) に、間接影響の観点から **2 条件を追記提案**:

- **(5) 遅延の観測可能性**: `ride` payload に `wait_s`/`ride_s`/`delay_s` が記録され、間接影響(誰の発火が
  並べ替わったか)を L2 で事後に測れること。**測れないなら入れない**(影響が観測不能なブラックボックスに
  なる)。
- **(6) n_proportional 予算の present 非依存確認**: n_proportional ラン運用時に限り、SUMO 遅延が総呼数の
  k 依存(経路⑤)を生まないことを compute_matched スモークで確認。生むなら固定予算運用に限定。

**no-go 判定は据え置き**: (b) 非決定論が byte で示せない / Windows で libsumo 不安定 / 遅延を入れても k*・
観測が実質変わらない場合は、バス静的表のみ入れタクシーはライブ化せず(sumo-live-transit.md §5 no-go)。

---

## 6. 未確認事項(事実と推測の区別)

**事実(コード/実データで確認済み)**:
- §1 の全 file:line チャネル、背景 od 車がエージェント非接続(`traffic.py:12`)、compute_matched の
  discard 機構(`reflection.py:382-387`)、共有 step 予算(`lod.py:80-92`)、§4.1 の rehearsal 実測値、
  信号遅延の式(`traffic.py:257-262`)、既定値(`edge_capacity:20`/`traffic.mode:ambient`/
  `max_llm_per_step:300`/`n_proportional:false`/`controls.mode:none`)。

**推測・未確認**:
- **`lod.congestion_surprise`(既定 0.5, `config.py:31` の掃引キー)は本体コードに消費点が見つからない**
  (grep で config 定義以外ヒットなし)。宣言のみ/レガシーの可能性。もし将来 input-resolution で混雑を
  LLM 詳細度に接続する consumer が足されると、混雑→呼の内容の新チャネルになりうる=**要追跡**(現状は
  非 load-bearing)。
- **SUMO 遅延が終電境界(§1.3)を跨ぐ頻度**は未実測(タクシー/バスの遅延分布 × 終電時刻帯の重なり次第)。
  離散効果が大きいので v-Ride-1 スモークで測るべき。
- **n_proportional × SUMO 遅延の在場・総呼数への系統効果(経路⑤)の実規模**は未実測。既定固定予算では
  無風だが、n_proportional ラン(rehearsal 実績あり)では実測が要る。
- **TraCI `dispatchTaxi` の決定論**(seed 固定での再現)は SUMO 公式が TraCI コマンド順の決定論を明文保証
  せず、自前スモーク(§5.2)で担保する必要(sumo-live-transit.md §6 と同じ未確認)。
- **予算 binding の時間帯依存**: §4.1 は「混雑ピーク時に予算 binding 傾向」を示すが、深夜など要求者 <
  予算の時間帯では非 binding=経路①④の総量が微増減しうる(k 世界間では compute_matched が担保)。
  時間帯別の binding 率は未細分。

---

## 付録: 主要 file:line 索引

- 歩行者混雑減速: `src/society/engine/scheduler.py:817`(edge_capacity)・`825-828, 831`(factor)・
  `865`(on_congestion)・`868-869`(drive)・`870-871`(arouse)・`872-873`(state_change)。
- 到着処理/初訪問/ride 課金: `scheduler.py:874-909`(arrive)・`889-892`(novel_place)・`880-883`(_charge_ride)。
- 終電ゲート: `scheduler.py:777-780`・`routine.py:723`・`transit.py:106-109`。
- ride 決定(非LLM): `routine.py:505-541`(_ride_extra)・`config.yaml ride.taxi/bus`。
- 背景 od 車の信号/容量(エージェント非接続): `traffic.py:257-262`・`293-296`・`12`(docstring)。
- drive ゲージ/閾値: `drive.py:139-169`(add)・`88-98`(effective_threshold)・`22`(congestion 重み)。
- affect/arousal: `factors/affect.py:49-62`・`factors/update.py:116-122`(on_congestion)・`145-172`(on_arousal)。
- impact ゲージ→深い内省: `factors/update.py:79-107`(_impact_note)・`105-111`(reflection_trigger)。
- 発火配分/共有予算: `scheduler.py:1609-1694`(_phase_drive)・`lod.py:80-92`(LodBudget)・
  `simulation.py:81-82, 876-885`(n_proportional 予算)。
- compute_matched/k: `reflection.py:382-387`・`scheduler.py:706-707`・`config.py:226-229`・
  `tests/test_commerce.py`(FixedLLM+compute_matched 呼数一致テストの型)。
- プロンプト内容(congestion/weather): `deliberate.py:307`・`181`。
- S4/S5 逸脱: `routine.py:173,181,199`(detour/interrupt)・`drive.py:213-256`/`routine.py:266`(boredom)。

出典(SUMO 側実装・データ)は [sumo-live-transit.md](sumo-live-transit.md) / [sumo-integration-research.md](sumo-integration-research.md) に既述。
