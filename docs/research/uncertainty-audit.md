# 不確実性の監査 + 運/実力分解(第51バッチ)

外部指摘「**100% 予測可能な世界ではダイナミズムが失われる**」への回答。目的は 2 つ:

1. **監査**: いまのシムに *すでに* どれだけの揺らぎが、どこに、どれだけの頻度で入っているかを
   コード実査と完成ランの後処理で全数把握する。
2. **運/実力分解**: 住民の成果(収入・関係・評判)を「実力由来(本人属性)」と「運由来(偶発
   イベント曝露)」へ分散分解する observable を作る。

**このバッチでは揺らぎを一切追加しない**(採点列挙まで)。追加は後続の第54バッチ=不確実性モードが担当。
実装物はすべて `scripts/`(読み取り専用の後処理)+ `tests/` + 本書。シム本体(`src/society/`)・
`conf/config.yaml`・`viz/` は一切変更していない。

- 監査スクリプト: `scripts/audit_uncertainty.py`(+ `runs/<run>/audit/uncertainty.{json,txt}`)
- 分解スクリプト: `scripts/analyze_luck.py`(+ `runs/<run>/luck/decomposition.json`)
- 検証: `tests/test_audit_uncertainty.py` / `tests/test_analyze_luck.py`(22 件 緑)
- 依存: 標準ライブラリ + pyarrow + numpy(**pandas / duckdb / 実 LLM 不使用**)。

---

## 1. 監査手法

### 1.1 揺らぎ源の全数列挙(コード実査)

乱数はすべて中央集権シード `RngHub.stream(用途, agent_id, step, …)` 経由(`src/society/rng.py`)。
`grep -rn '\.stream(' src/society/` で **named stream を全数収集**した(下表)。各 stream は
「(master_seed, キー)から派生した独立系列」で、他者の実行順に依存しない=決定論リプレイの土台。
現状の設計思想は **既定 OFF・no-fingerprint**(揺らぎゲートに traits/beliefs=k を読ませない)+
**専用 stream で既存 draw 順を汚さない**(ゴールデン L1 バイト一致を守る)。

named stream を機能で分類(★=既定 OFF の機能。stream を引くのは ON 時のみ):

| 分類 | stream | 何に効くか | 大きさ | 発火頻度 |
|---|---|---|---|---|
| **A. 行動選択の確率化** | `motif`★ | 朝1回、その日の行動骨格を novelty 抽選 | novelty_prob=0.15 で「いつもと違う日」 | 1/人日 |
| | `jitter_time`★ | flexible 活動の開始/継続を一様 ±30分 | MATSim mutationRange 相当 | flexible 活動ごと |
| | `detour`★ | 目的地手前で近傍 POI に寄り道 | per-move 0.05–0.18(活動種別) | 移動ごと |
| | `interrupt`★ | 滞在中の活動を途中で離脱 | per-step 0.0–0.10 | 滞在 step ごと |
| | `gumbel`★ | 行き先 argmax を U=V+ε の確率選択へ | 温度で多様度可変 | 行き先決定ごと |
| | `boredom`★ | 退屈ゲージ閾値超え→未訪問 POI へ内発探索 | fire_prob=0.5、閾値0.6 | 閾値到達+cooldown明け |
| | `decide` / `drive` | 行動決定・欲求発火の抽選 | 閾値ゲート+個人重み | step ごと(発火は稀) |
| | `lynch`★ / `outside` / `curfew`★ / `crowd`★ | 認知地図目的地・圏外行動・夜間外出・混雑回避 | 小 | 条件成立時 |
| | `policy_cache`★ | 行動方針キャッシュ再利用の抽選 | relax 幅 | 再利用判定ごと |
| **B. 経済のゆらぎ** | `gig` | 日銭(gig 収入)を uniform(0.2,1.4) で乱す | ±ファクター(収入の 20–140%) | 1/人日 |
| | `payment`★ | 支払い手段の選択 | 分類 | 消費ごと |
| | `venture` / `permit`★ / `event`★ / `event_retry`★ | 出店売上(通行人購入)・営業許可・イベント参加 | 抽選 | 該当行動時 |
| | `service`★ / `delivery`★ / `ads`★ / `group`★ | サービス来店・宅配注文・広告接触・グループ加入 | 現実頻度に較正 | 自由時間 step |
| **C. 都市・環境ショック(世界)** | `disaster`★ | 災害 onset/clear・交通遅延/運休・インフラ障害 | onset_prob / delay_prob / outage_prob(日次) | 1/日(世界) |
| | `weather`★ | その日の天気(全員共通・k 非依存) | 決定論生成 | 1/日(世界) |
| **D. 生活の偶発** | `health`★ | 病気の発症・受診 | onset_prob(日次・居住者) | 1/人日 |
| | `crime`★ | 窃盗被害・迷惑行為 | crime_prob / nuisance_prob(per step) | step ごと(稀) |
| | `date`★ / `dinner`★ / `household`★ / `move_home`★ / `career`★ / `lodging`★ | デート・夕食共食・世帯編成・転居・転職失業・宿泊 | 抽選 | 日次/該当時 |
| **E. 社会・情報** | `sns_react` / `phone` / `media`★ / `info`★ / `c2_meet`★ / `party`★ / `joint`★ | SNS 反応(いいね/リシェア)・スマホ・娯楽・情報環境・構造化会話・来街者 party・共同行動 | 抽選 | step/日次 |
| **F. 基盤・背景** | `traffic` / `car_spawn` | 背景交通(通過車両)の生成 | 交通量 | step ごと |
| | `presence*`★ | 日次在場ローテーション(persona pool) | 在/不在の層別 | 1/日(世界) |
| | `persona` / `sdt` / `collective` / `needs` / `follows` / `lod_input_res` / `floor` / `inner` / `pov_salience`★ / `writeback` / `jitter` / `taxi` / `rule_boost`★ / `mock` | 生成・初期化・内部変調・LLM mock 等 | 各種 | 起動/step |

> `mock` stream は Mock LLM の疑似応答生成(実験用途で本番揺らぎではない)。`persona`/`sdt`/
> `collective`/`needs`/`follows` は起動時の個体初期化(1回)。**成果に効く「体験としての揺らぎ」は
> A–E**、とりわけ **A(行動選択の確率化)と C/D(外生ショック)** が本監査の主対象。

### 1.2 スクリプトが測るもの:「住民1人1日の想定外イベント数」

`audit_uncertainty.py` は完成ラン(`l1_events.parquet`)を入力に、**揺らぎ由来と分類できる L1 kind**
の per-agent-day 件数分布と、全イベントに占める比率を出す。分類の対応表 = `LUCK_KINDS`(スクリプト内)。
各 kind は schema(`society.observer.schema`)に登録済み(テストで担保)。帰属ルール:

- **agent スコープ**: 本人 `agent_id` へ。`crime` は例外で `payload.victim`(不運を被った側)へ帰属。
- **world スコープ**(`disaster`/`transit_delay`/`infra_outage`、`agent_id=-1`): 「その日 街に居た住民
  全員」へ 1 件ずつ **曝露** として帰属(= 有界・決定論。街に居なければ曝露しない)。
- **phase フィルタ**: `disaster`/`infra_outage` は `phase=="onset"` のみ、`illness` は `state=="onset"`
  のみ計上(onset+clear の二重計上を避ける)。

`LUCK_KINDS` は **1 kind = 1 行**。第54バッチが `chance_event` を足すときは 1 行追加するだけで
監査にも運分解にも自動反映される(§4 参照)。

---

## 2. 実測結果(mock ランで実走)

### 2.1 代表的な平常日 — `u51_audit_80a1d`(mock・80人・144step=1日・seed 51)

揺らぎ機能を実運用に近い組で ON(`routine.stochastic` / `drive.boredom` / `relations` /
`friend_graph` / `commerce.inventory` / `services` / `weather` / `health` / `society_diversity` /
`disaster`。確率は控えめ)。この seed では世界ショック(disaster/delay/outage)は発火せず=**平常日**。

- 総イベント **25,019** / agent 帰属 **24,866** / 住民 **80**
- 揺らぎ由来(帰属済み)**419 件 = 全 agent イベントの 1.7%**
- **想定外イベント / 住民1人1日**: 平均 **5.24** / 中央 5.0 / p90 10.0 / 最大 16
- **1件以上 揺らぎに遭遇した住民は 96.2%**(80人中 77人)。まったく揺らがない住民は 3人のみ。
- kind 別生件数: `detour` 201 / `interrupt` 143 / `boredom_explore` 48 / `crime` 19 / `illness` 8

読み取り: **既に「100% 予測可能」ではない**。平常日でも住民のほぼ全員(96%)が 1日に平均 5 件超の
想定外(寄り道・中断・退屈探索・被害・発症)を経験する。ただし揺らぎは **全イベントの 1.7%** に留まり、
骨格(通勤・勤務・睡眠・定型移動)が支配的=「予測可能性 ≈ 93%」という較正ターゲット
(`interstitial-life §4.1`)と整合する。**構造は安定しつつ縁で揺らぐ**状態。

### 2.2 世界ショック日 — `u51_shock_probe`(mock・40人・1日・disaster 強制)

world スコープの帰属経路を数値で確認するための probe(`disaster.days=[0]`・`delay_prob=1.0`・
`outage_prob=1.0`)。台風 onset 1 + 交通遅延 2 + 停電 onset 2 が day0 に発火。

- 揺らぎ由来 **354 件 = 全 agent イベントの 9.8%**、**世界ショック曝露 200 件**
- 想定外 / 人日: 平均 **8.85**(平常日の 1.7 倍)、**全員(100%)が遭遇**
- category: `shock` 120(=onset 3件×40人)/ `delay` 80(=2件×40人)/ `detour` 73 / `interrupt` 60

読み取り: 外生ショックは **街全員へ相関的に効く**(共通ショック)ため、per-agent 曝露が一気に底上げ
される。一方でショック日は在宅抑制で自発的な寄り道・探索(detour/boredom)がやや減る=**外生の揺らぎと
内発の揺らぎはトレードオフしうる**、という観察。

---

## 3. 運/実力分解の結果

`analyze_luck.py` は住民の成果を 3 段の階層 OLS(`numpy.linalg.lstsq`、`measure.r2_traits` と同流儀・
切片あり)で分解する。実力側 = **traits(load_traits を再利用: internal_locus/nfc/risk_tolerance/
drive_threshold/fire_weight)+ age + occupation ダミー**。運側 = **偶発曝露の per-agent 件数
(`audit_uncertainty.LUCK_KINDS` を共有 import)**。

- skill: `Y ~ traits + age + occupation` → R²_skill(実力)
- full: `Y ~ traits + age + occupation + luck_exposure` → R²_full
- ΔR²_luck = R²_full − R²_skill(運が **上乗せ** した説明力)/ 残差 = 1 − R²_full

### `u51_audit_80a1d`(n=80、実力列 17、最大 |共線| 0.23)

| 成果 | 実力 R²_skill | 運の追加 ΔR²_luck | 運単独 R² | 残差 | 読み取り |
|---|---|---|---|---|---|
| **収入** | **0.750** | 0.001 | 0.059 | 0.249 | ほぼ実力(職業・給与体系)で決まる。運の上乗せはほぼゼロ=**収入は運に鈍感** |
| **関係数** | 0.173 | **0.190** | 0.162 | 0.637 | **運が実力より説明する**。偶発曝露(寄り道/中断/退屈探索)が新しい出会いを生む |
| **評判** | 0.272 | 0.040 | 0.072 | 0.688 | 実力寄りだが運も少し効く。残差(内容・タイミング)が最大 |

**核心的な観察**: 成果の種類で運/実力の比重が違う。**収入は実力(職業構造)がほぼ決める**一方、
**関係数は運(偶発的な行き先の揺らぎ)が実力を上回って説明する**。「寄り道して知らない店に入ったら
新しい人と出会った」という *ダイナミズムの経路* が、関係形成において定量的に確認できる。これは外部指摘
への直接の反証材料になりうる — **揺らぎは既に成果(特に社会関係)へ流れ込んでいる**。

### 限界(出力にも docs にも正直に明記)

- **観測であって因果ではない**: R² は説明分散。「運が成果を生む」因果効果ではない。
- **小標本・単一 seed**: n=80、実力列 p=17。n が p に近いほど R² は過大(income の adj_R²=0.68・
  relations の adj_R²=−0.05 が示すとおり skill 側は過剰適合気味)。**単一ランの数値を一般化しない**
  =seed 反復・多日ランが必要。
- **運の内生性**: detour/interrupt/boredom など agent スコープの曝露は本人の行動選択と相関しうる
  (=純外生ではない)。純外生は world スコープ(disaster/transit_delay/infra_outage)側。分解では
  ΔR²(実力を入れた後の上乗せ)を採ることで実力との共有分散を実力側に寄せている(保守的)。
- **多重共線**: luck_exposure と実力列の |Pearson| 最大 = 0.23(この run では低い=分離は比較的安定)。
- **mock LLM**: 発話内容が定型で relations/reputation の変動が実 LLM より小さい=R² の *水準* は
  バックエンド依存。**傾向(収入=実力・関係=運)** の読み取りに留める。
- **1日ラン**: 収入/関係は日次で頭打ち。world ショックは日次発火のため単日 seed では 0 になりうる
  (§2.2 の probe で経路を確認)。

---

## 4. 揺らぎ追加候補の採点表(第54バッチへの引き継ぎ)

**このバッチでは追加しない**。以下は不確実性モード(第54バッチ)が検討すべき候補の採点。
軸: **現実らしさ**(1–5)/ **実装コスト**(低/中/高)/ **k\* 研究への安全性**(R²(k) 同定を汚さないか)。

k\* 安全性の原則(既存設計から継承):
- **外生**(traits=k と独立の world/物理ゲート抽選)であれば **安全**。R² を一様に下げるだけで
  trait 係数を偏らせない(むしろ「予測不能な残差」を足す=健全)。
- **traits でゲートすると危険**(例: risk_tolerance が高い人ほど宝くじを買う)。no-fingerprint 契約
  (揺らぎゲートに k/beliefs を読ませない)を破ると k\* の同定が汚れる。**必ず物理量/世界 RNG でゲート**。
- **専用 stream + 既定 OFF**(既存 draw 順を汚さない・ゴールデン L1 バイト一致)を厳守。

| 候補 | 内容 | 現実らしさ | 実装コスト | k\* 安全性 | 判定 |
|---|---|---|---|---|---|
| **臨時収入 / 財布紛失** | 低確率の windfall(+現金)/ loss(−現金)。世界 RNG or 物理位置ゲート | 4 | **低** | **高**(金額のみ・外生・traits 非参照で実装可) | ★**第一候補**。income の運感度(現状ほぼ0)へ外生分散を直接注入 |
| **偶然の出会い** | 普段の同僚/世帯以外との低確率の関係接触(近傍×低頻度で発火) | 5 | 低 | 高(近傍=物理ゲート。相手選択は距離/訪問回数=k 非参照) | ★**第一候補**。§3 で関係=運が既に主経路=最小コストで効く |
| **宝くじ的当選** | 明示的な宝くじ購入→稀な高額当選 | 3 | 中 | 中(購入をどうゲートするかが鍵。**risk で買わせると危険**→定額・全員一律購入なら安全) | 保留。購入ゲートを外生に設計できれば可 |
| **拾得 / 落とし物** | 路上で低確率に金品を拾う/落とす(位置ゲート) | 4 | 低 | 高(位置のみ) | 候補。財布紛失/臨時収入と同機構で相乗り可 |
| **予期せぬ抜擢/降格** | ランダムな昇進・配置転換(career 拡張) | 3 | 中 | 中(職場ゲート。評価に traits を混ぜると危険) | 保留。既存 `career` stream 拡張で外生分のみ足すなら可 |
| **偶発的バズ** | 投稿が稀に非対称拡散(viral_cascade は既存) | 3 | 低 | 中(拡散シードを外生にすれば安全) | 既存機構の較正で足りる見込み。新規性 低 |
| **天候起因の行動変化** | 雨で外出減・行き先変化(weather は既存) | 4 | 低(較正のみ) | 高(世界・k 非依存) | 既存 `weather` の grievance/行動係数較正で対応可 |

**推奨(第54バッチ 不確実性モード)**:

1. **`chance_event` を 1 kind で新設**(専用 stream `"chance"`・既定 OFF)。財布紛失/臨時収入/偶然の
   出会い/拾得を **単一の外生イベント種**に束ね、payload で `{kind: windfall|loss|encounter|found,
   amount?, other?}` を出す。schema に `register_event_kind("chance_event", …)` を 1 行、`society/` に
   新規モジュール(例 `chance.py`)を 1 本追加(第54バッチの担当領域)。
2. **本監査の対応表へ 1 行**: `audit_uncertainty.LUCK_KINDS` のコメント済み受け口
   `# "chance_event": _lk("chance", stream="chance", valence="mixed", …)` を **アンコメントするだけ**で、
   監査(per-agent-day 分布)にも運分解(luck_exposure・ΔR²)にも自動で入る。attr_field/phase も同枠で表現可。
3. **ゲートは物理量/世界 RNG のみ**(no-fingerprint)。金額・相手選択に traits を読ませない=k\* 同定を守る。
4. **検証**: ON で world/agent 両スコープの帰属が本書のテストにそのまま乗る。ゴールデン L1 は既定 OFF で
   バイト一致を維持。

これにより「収入は現状ほぼ実力で決まる(ΔR²_luck≈0)」という穴を、**外生の windfall/loss** で狙って
埋められる — ダイナミズム(運が成果に流れ込む度合い)を **設計変数として制御可能**にするのが第54バッチの狙い。

---

## 付録: 再現コマンド

```bash
# 代表的な平常日ラン(80人・1日)
python scripts/run.py model.backend=mock run.n_agents=80 run.n_steps=144 run.seed=51 run.name=u51_audit_80a1d \
  relations.enabled=true friend_graph.enabled=true routine.stochastic.enabled=true drive.boredom.enabled=true \
  commerce.enabled=true commerce.inventory.enabled=true services.enabled=true weather.enabled=true \
  health.enabled=true health.onset_prob=0.1 society_diversity.enabled=true society_diversity.crime_prob=0.01 \
  society_diversity.tourist_ratio=0.4 disaster.enabled=true disaster.delay_prob=0.5 disaster.onset_prob=0.2

# 世界ショック probe(disaster 強制)
python scripts/run.py model.backend=mock run.n_agents=40 run.n_steps=144 run.seed=51 run.name=u51_shock_probe \
  routine.stochastic.enabled=true drive.boredom.enabled=true society_diversity.enabled=true \
  society_diversity.crime_prob=0.01 disaster.enabled=true disaster.days=[0] disaster.delay_prob=1.0 disaster.outage_prob=1.0

# 監査 + 分解
python scripts/audit_uncertainty.py --run u51_audit_80a1d
python scripts/analyze_luck.py      --run u51_audit_80a1d
```
