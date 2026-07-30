# 第1回ハッカソンIDEA台帳 → シム本体組み込み候補の選定(リポ実査つき)

調査日: 2026-07-30 / 対象: `docs/research/hackathon1-analysis/ideas-ledger.md` + `ideas/*.md` 8本(228件)
方針: **提出物・審査対策系は対象外**。シミュレーション本体の機構(世界・認知・観測)に絞る。
照合基準: 第64バッチ以降の実装(第66-69バッチ = LLM健全性KPI・world.mod・実高さ・可視行列・
`labeling.place_binding`)を反映。`docs/plans/twin-physics-vision-affordance-plan.md` は
**レーン1実装完了(2026-07-29)**・持ち越し=analyze_sweep へのllm_health 3列接続 / D0閾値のU-10承認 /
D1のON判断 / B-L1以降。直近git log 5件(f128c34…5101b8a)確認済み。

---

## 0. 実査の総括

- 台帳の「シム機構系」候補を **28件**まで絞って全件リポ実査した結果:
  - **既に実装済み(そのまま重複)= 8件**(下記 §3-A)
  - **部分的にあり、拡張で足りる = 13件**
  - **無い(新規) = 7件**
- 重要な発見: 台帳が「shibuya に無いはず」と書いた項目のうち、**mood_text による数値隠蔽**
  (all-in-smoke)・**屋内外の情報遮断**(good_echo)・**伝播辺リスト**(ebiyama)・
  **通信グラフからの役割induction**(柴田fire)・**不完全記憶**(my-social-agents)は**既に実装済み**。
  台帳の適用案は「点検せよ」と書いているものが多く、点検の結論は「ある」。
- 逆に、台帳が軽く扱っていた **「LLM の自己反復が伝播率を汚染する」(ebiyama 事象F)** は
  リポに対策がゼロで、**自然造語 = coin_label の主張を丸ごと無効化しうる最大の穴**だった。

---

## 1. 候補一覧と採点

採点: ①世界再現度への寄与 / ②研究課題への直結(R²(k)・k*・H到達異質性・組織形成・関係内生化・
自然造語・誤情報伝播)…各 5 点満点。③実装コスト = Opus 実働日。④整合 = 既定OFF/決定論/
no-fingerprint/R1(呼数不変)との相性 ○△×。⑤レーン = 前(本選前〜8/14に安全)/ 後(本選後)。

| # | 候補 | 現状(file:line) | ① | ② | ③ | ④ | ⑤ | 判定 |
|---|---|---|---|---|---|---|---|---|
| 1 | **未定義行動(enum外出力)の計測** | **部分**: `cognition/deliberate.py:363-511` の `parse_action` は未知 `action` を **None** で捨て、`engine/scheduler.py:1942-1945` が `fallback{reason:"parse_error"}` に一括計上(=JSON崩れと同一カテゴリ)。自由記述の器は `deliberate.py:465-476` の `free_action`(`freedom.open_actions` 既定OFF・`conf/config.yaml:789`)に既にある | 3 | **5** | 0.5 | ○ | 前 | **採用①** |
| 2 | **規範化の言語形式検出器(4段階)** | **部分**: `scripts/detect_emergence.py:440-470` に規範**発話**パターン10種(〜べき/普通/should…)。ただし**語ごとの段階**(無冠詞初出→他者初引用→定冠詞化/「例の」→合意参照「さっき決めた」)は無い。素材は `labeling/labels.py:3-4`(coin/transmission/adopt)に揃う | 3 | **5** | 1.5 | ○ | 前 | **採用②** |
| 3 | 命名者 vs 制度化者の分離観測 | **部分**: coiner は `labeling/labels.py:68`(place_bind)と provenance Item に、採用者は `label_adopt` にあるが、「規範文脈で再利用した個体」が未分離 | 2 | **5** | (②に同梱) | ○ | 前 | **採用②に統合** |
| 4 | **エコー指標(echo_max / self_similarity)常設** | **無い**: grep 0件。近縁は `observer/aggregate.py:505,517` の `speech_diversity` / `speech_pairwise_var`(集団の多様性であって**同一話者の反復**ではない) | 2 | **5** | 1.0 | ○ | 前 | **採用③** |
| 5 | ground_truth / rumor ペア + truth_status 5分類 | **部分(骨格のみ)**: `net/infoenv.py:176-200` の misinfo は「新規投稿を確率で誤情報判定 → 訂正/炎上」= **真実側の対がなく二値**。`gossip.py:1-35` の悪評は**内容を持たない匿名タグ**(意図的設計) | **5** | 4 | 2.0 | ○ | 前 | **採用④** |
| 6 | ラベルごとの信念強度を感情と別チャネルに | **無い**: `labeling/labels.py` は「語を使ったか/採用したか」のみ。信じているかの軸なし | 4 | **5** | 1.5 | ○ | 前 | **採用④に統合** |
| 7 | 情報源別減衰 + ユニーク報告者追跡 | **無い**: gossip の `adopt_threshold=2` は既に「相異なる知人数」で数える真の complex contagion(`gossip.py:13-15`)= 二重計上防止の思想はあるが、**情報源別の減衰率**は無い | 4 | 3 | 0.5 | ○ | 前 | **採用④に統合** |
| 8 | **初期個体差ゼロの N 体対照実験** | **無い**: 対照は `k.writeback=sham/off`(`tests/test_contracts.py:53-58`)と `controls.mode=null_series/compute_matched`(`engine/simulation.py:404-405`・`config.py:19`)のみ。**traits 分散ゼロのセルが無い** | 2 | **5** | 1.0 | ○ | 前 | **採用⑤** |
| 9 | 初期フレームのラン単位共変量化 | **無い**: summary.json に初日の解釈状態を残す経路なし | 2 | 4 | 0.5 | ○ | 前 | **採用⑤に統合** |
| 10 | cheap talk 検出(自己申告 vs 実挙動) | **部分**: `observer/aggregate.py:773` `joint_fulfill_rate`(承諾したが同席せず=0.337)が既に同型。ペルソナ逸脱は `observer/deviation.py`。**発話⇄行動一般**の乖離は無い | 3 | 4 | 1.0 | ○ | 前 | 保留(②③の後) |
| 11 | プラセボ介入(動いてはならない対照) | **部分**: sham/null は上記のとおり有るが、「効いてはならないと事前宣言し、効いたら実装リークを疑う」機械判定が無い。`docs/plans/stationarity-preregistration.md` が事前登録の器 | 1 | 4 | 0.3 | ○ | 前 | **第9候補(保険)** |
| 12 | **「沈黙・何もしない」を選択肢/スキーマに明記** | **部分**: ヘッダの選択肢は speak/coin_label/post/dm/wander(`deliberate.py:15-30`)。`wander` は `{"type":"stay"}` に写るだけ(`deliberate.py:482-483`)で、**「誰とも関わらない」を選ぶ意思表示ではない** | 4 | 4 | 0.5 | ○ | 前 | **採用⑥** |
| 13 | silent_agent_rate / unused_rate | **無い**: 沈黙個体率・施設/組織/SNS の未使用率の L2 列なし | 2 | 4 | 0.5 | ○ | 前 | **採用⑥に統合** |
| 14 | ダンバー数 LRU 忘却 + 再会イベント | **部分**: `agents/memory.py:137-142` に `relations_max` LRU 退避(**既定 0 = 無制限**・`conf/config.yaml:990`)。`friends.py:12` は Dunbar 入れ子(3-5/10-15)で初期辺を較正済み。**退避イベント・再会イベント(gap_days)は無い** | 4 | 4 | 1.5 | ○ | 前 | **採用⑦** |
| 15 | perceive_pass / perceive_enter 二層知覚 | **部分**: 屋内/屋外の情報遮断は `world/perception.py:1-5`(非ブロードキャスト原則)で実装済み。**POI ごとの「通りすがりに見える/入って初めて分かる」記述の二層**は `world/scene_desc.py` に無い | **5** | 3 | 1.5 | ○ | 前 | **採用⑧** |
| 16 | 場所依存の一斉配信チャネル(館内放送・電光掲示) | **無い**: 掲示は `flyer_post/flyer_view/flyer_expire`(`observer/schema.py:72-74`)= 通行人が個別に見る型。OOH は `street.py`(ads・既定OFF)。**その場の全員へ同時到達**するチャネルは無い | **5** | 3 | 1.0 | ○ | 前 | **採用⑧に統合** |
| 17 | 「死」を第一級イベントに | **無い**: `health.py` は疲労/病気/メンタルのみで死亡なし。退出は visitor の帰宅・`lodging.py` のみ | 4 | 2 | 1.5 | △(倫理註記が要る=実在渋谷) | 後 | 落選(§3-B) |
| 18 | 行動カテゴリ/役割の分布エントロピー監視 | **部分**: 語彙側は `observer/measure.py:695-712` `vocab_entropy` 有り。行動・役割側は無い | 2 | 3 | 0.5 | ○ | 前 | 第9候補群 |
| 19 | LLM 方向バイアス監査 + 選択肢シャッフル null | **無い**: `shuffle` grep 0件。誘い先候補の並べ替えは `(agent,day)` 安定ハッシュ(第64バッチ)で既に決定論 | 2 | 3 | 1.0 | ○ | 前 | 保留 |
| 20 | 温度を下げない per-call シード | **無い**: mock は `rng_key` で決定論(`llm/base.py:9-16`)だが、`llm/openai_compat.py` / `vllm.py` に `seed` パラメータの受け渡しが無い | 1 | 3 | 0.5 | ○ | 前 | 保留(vLLM は seed 対応=本選運用で再検討) |
| 21 | 数値を隠し気分ラベルだけ渡す | **既にある**: `factors/mood.py:8-24` `mood_text`(構成概念の名前も数値も LLM に見せない) | — | — | — | — | — | 重複 |
| 22 | 死んだ状態変数の検出 | **無い**: プロンプト掲載変数が実際に動くかの検査テストなし | 1 | 3 | 0.3 | ○ | 前 | **第9候補(保険)** |
| 23 | 相補的 KPI(線形従属列)の検出 | **無い**: L2 列は登録アグリゲータ 85+ 件(`observer/aggregate.py:76-908`)まで膨張。相関行列検査なし | 1 | 3 | 0.3 | ○ | 前 | **第9候補(保険)** |
| 24 | 個体の固着(stuck)KPI | **部分**: `scripts/analyze_structure.py:1-30` は**構造**固着(Kendall τ・中心性 turnover・edge churn)。**個体の最長連続同一place滞在**は無い | 2 | 4 | 0.5 | ○ | 前 | 保留(D0診断と重複気味) |
| 25 | 制度転換 transitions / k のヒステリシス双方向掃引 | **無い**: `world/scenario.py` の `shock_closure` と `world.mod`(第67)が近縁だが run 途中の制度切替は無い | 3 | 4 | 2.0 | △(mid-run 状態差替=checkpoint 検収が重い) | 後 | 落選(§3-B) |
| 26 | public / private 乖離(3層発話) | **部分**: 内心は `inner_life.py`、公開は SNS post。**同一 step の同時生成と乖離指標**は無い | 3 | 4 | 1.5 | △(出力フィールド増=作為性上昇) | 後 | 落選(§3-B) |
| 27 | 屋内/屋外の情報遮断 | **既にある**: `world/perception.py:1-5` | — | — | — | — | — | 重複 |
| 28 | 伝播の辺リスト(from/to/label/channel) | **既にある**: `observer/schema.py:29` `transmission{item_id, from, channel}` | — | — | — | — | — | 重複 |

---

## 2. 上位8件のミニ設計

### 相互依存(先に読む)

```
③エコー/自己反復の除去 ──→ ②規範化ステージ ──→ (自然造語 k* の主張)
                       └──→ ④誤情報の構造化(伝播カウントの母数を共有)
①未定義行動 ─┬→ ⑥沈黙の明示   (どちらも parse_action の受理層=同一バッチが得)
⑤初期個体差ゼロ ── 第63バッチ CRN 実験基盤にセル追加のみ(シム本体は traits 生成1点)
⑦ダンバー枠  ── 第62-64バッチ relations/joint の直系。closeness 蓄積と表裏
⑧場所の二層知覚+放送 ── 第69バッチ labeling.place_binding(D1)の自然な延長
```

**③を①②④より先に入れる**こと。エコー(同一話者の言い換え反復)を伝播から分離しない限り、
②の「規範化が何 step で起きたか」も④の「誤情報がどこまで広がったか」も**LLM の反復癖の関数**に
なる。ebiyama 事象F(「LLM は自分の発話を内省できず微妙な言い換えで同テーマを連投」)は
1725→1846テストのどこにも対策が無い。

---

### ① 未定義行動レジスタ(undefined_action)

- **狙い**: 「与えられた行動空間で目的が達成できないとき空間そのものを拡張しようとする個体」=
  **「世界を変えようとする個体」の操作的定義の最有力候補**を、現在**捨てている**データから作る。
  kibo_crew_sim の `interact` 発明(3回)は行動空間突破の実例。
- **触るモジュール**: `cognition/deliberate.py`(`parse_action` の末尾 `return None` 直前に分岐)/
  `engine/scheduler.py:1942-1945`(fallback とは別イベント)/ `observer/schema.py` / `observer/aggregate.py`。
- **設計**: `parse_action` を `(action, reject_reason)` の2値返しにせず、**別関数
  `classify_reject(data) -> "unknown_action" | "missing_field" | "broken_json"`** を足す
  (既存の戻り値契約は不変=呼び出し側の分岐を壊さない)。scheduler は
  `reason` が `unknown_action` のとき `fallback` **ではなく** 新イベント
  `undefined_action{action, keys, trigger}` を出す。**フリーテキストは `action` 名と
  トップレベルのキー名のみ**を記録(発話本文は既存の別経路にあるので二重化しない)。
- **conf キー(既定OFF)**: `observer.undefined_action.enabled: false`。
  OFF = `parse_action` の戻り値・イベント列・L2 列がバイト一致(`fallback` に落ちる従来経路のまま)。
- **新イベント/L2**: `undefined_action`(ON時のみ)/ L2 `undefined_action_rate`
  (= undefined_action 件数 ÷ `llm_calls_total`。第66バッチの llm_health と同じ分母を使い、
  `llm_fallback_rate` と**分子が排他**になるよう scheduler 側で振り分ける)。
- **乱数**: **ゼロ**(新 stream なし・既存 draw の追加消費なし)。LLM 呼数不変。
- **テスト**: (a) OFF で golden `tests/data/golden_baseline_l1.json` 一字一句一致 +
  draw 数一致、(b) 未知 kind の JSON を食わせて `undefined_action` 1件・`fallback` 0件、
  (c) 壊れた JSON は従来どおり `fallback`、(d) `free_action` の "do"/"free"/"activity" は
  従来どおり受理され undefined に落ちない(既存 `tests/test_free_action.py` を回帰)。
- **検収条件**: mock 3日ランで `undefined_action_rate` が算出され、
  `llm_fallback_rate + undefined_action_rate` が旧 `llm_fallback_rate` と一致(振り分けの保存則)。
- **工数**: 0.5日。**正直な限界**: mock は enum 内しか返さないので発火は実LLM ラン限定
  (第62バッチの「材料は day2 から効く」と同型の正直註記を出力に入れる)。

---

### ② 規範化ステージ検出器 + 命名者/制度化者の分離

- **狙い**: `coin_label`(自然造語)の**下流**に「その語が規則になったか」を段階で測る。
  lunar_simulation の実観測(無冠詞命名 → 複製 → 全体放送 → 定冠詞つき既存ルール化、4〜20 step)。
  **k* が二層化する**(発案の k* と制度化の k* が別値)なら論文級。
- **触るモジュール**: `labeling/labels.py`(語ごとの段階台帳)/ `observer/aggregate.py`(L2)/
  `scripts/detect_emergence.py`(既存の規範パターンを語単位へ拡張)。
- **設計(全決定論・観測のみ)**: 語 w について4段階を記録。
  - S1 初出 = 既存 `label_coin` の step(そのまま)
  - S2 他者初引用 = 既存 `transmission` の最初の `from != coiner` イベント(そのまま)
  - S3 **定冠詞化相当**(日本語)= その語が「例の/あの/いつもの/おなじみの」+ w の形で現れた初出
  - S4 **合意参照**= 「さっき決めた/前に決めたとおり/いつもの通り/決まりだから」+ w の共起初出
  S3/S4 の判定は**既存の speak/post テキストに対する決定論正規表現**(パターン表は
  `conf/labeling.norm_markers` にデータとして置き、コードに固有名詞を書かない=envpack 流儀)。
- **命名者/制度化者**: S1 の主が coiner、**S3/S4 の初出発話の主が institutionalizer**。
  両者の属性(tier・closeness・組織所属・k)を `scripts/analyze_norm_stage.py` が突き合わせ、
  「別人である割合」を出す。beyond-badminton の実例(命名=Casual ペルソナ、形式化=分析志向ペルソナ)。
- **conf キー(既定OFF)**: `labeling.norm_stage.enabled: false` / `labeling.norm_markers: {definite: [...], agreement: [...]}`。
- **新イベント/L2**: `norm_stage{word, stage, agent}`(ON時のみ)/ L2 2列
  `norm_stage_max`(当日到達した最大段階)・`norm_steps_to_agreement`(S1→S4 の step 差の中央値)。
  `scripts/analyze_sweep.py:55 _EXTRA_L2_SERIES` へ接続(第64バッチの invite 2列と同じ配線)。
- **乱数**: ゼロ。LLM 呼数不変(プロンプトも1バイト不変=**観測側だけの追加**なので
  no-fingerprint を一切壊さない)。
- **テスト**: 合成発話列で S1→S4 が順に立つ / 逆順・飛び段は記録しない /
  OFF で golden 一致・L2 列不在 / marker 表を空にすると S3/S4 が 0 件。
- **検収条件**: mock で S1・S2 が立ち(mock は造語する)、S3/S4 は 0 件でよい
  (=**正直註記**: mock の語彙には合意参照表現が無い)。
- **工数**: 1.5日。**統合先**: 第69バッチ `place_binding` の束縛台帳と同じ `LabelSystem` 内に閉じ、
  checkpoint("labels") へ自然同梱(配線追加不要=第69の先例をそのまま踏襲)。

---

### ③ エコー/自己反復の計測と「伝播カウントからの除外」

- **狙い**: 「同じ語が繰り返し出た」が伝播なのか LLM の反復癖なのかを切り分ける。
  **世界は歪めず、観測側の規則だけで交絡を除く**(ebiyama は類似度フィルタで強制 silent 化して
  「深掘りまで消える」副作用を自認した=同じ轍を踏まない)。
- **触るモジュール**: `observer/measure.py`(echo/self-similarity の算出。`_entropy` の隣)/
  `observer/aggregate.py`(L2)/ `labeling/labels.py`(**採用判定は一切変えず**、
  「新規伝播」カウンタだけ別に持つ)。
- **設計**:
  - `echo_max` = 直近 N step(既定 144=1日)における**同一文の最大反復率**。
  - `self_similarity_mean` = 同一話者の連続発話間 Jaccard 4-gram 平均。
  - `transmission_novel` = 既存 `transmission` のうち、**同一話者が過去 N step 内に既出の語を
    再使用した分を除いた**件数。**`adopt_threshold` の判定には一切影響させない**
    (=世界のダイナミクスは不変。除外は L2 の分子だけ)。
- **conf キー(既定OFF)**: `observer.echo: {enabled: false, window_steps: 144, repeat_window_steps: 144}`。
- **新イベント/L2**: 新イベントなし。L2 3列 `echo_max` / `self_similarity_mean` / `transmission_novel_rate`。
- **乱数**: ゼロ。LLM 呼数不変。
- **テスト**: 同一文を10回積んで `echo_max=1.0` / 全部違う文で低値 /
  `transmission_novel_rate` が「同一話者の再使用のみ」を落とす(他者からの再伝播は落とさない)/
  OFF で golden 一致。
- **検収条件**: `echo_max == 1.000` のランは k* 推定から**除外または別扱い**する判断基準を
  D0 の事前登録文書(`docs/plans/stationarity-preregistration.md`)へ 1 行追記。
- **工数**: 1.0日。**これが上位8件で最も「入れないと他の数字が信用できない」項目**。

---

### ④ 誤情報の構造化(ground_truth / truth_status 5分類 / ラベル別信念強度 / 情報源別減衰)

- **狙い**: 「広まったか」しか測れない現状を「**どちらへどれだけ歪んだか**」に上げる。
  Alberia のスライド実測では **UNVERIFIED(未確認)が最も伸び、FALSE はほぼ横ばい**だった
  = 二値設計では観測対象の大半が分類不能になる。
- **触るモジュール**: `net/infoenv.py`(misinfo ブロックの拡張)/ `gossip.py`(悪評タグとの統合点)/
  `labeling/labels.py`(語 ⇄ 事実の対応)/ `observer/aggregate.py`。
  **新モジュールは作らない**(既存3者の統合点を明示するのが本設計の主眼)。
- **設計**:
  1. **ground_truth の外出し**: `conf/rumors/*.yaml`(envpack 流儀 = 機構は基盤・値は環境側)に
     「事象 → ground_truth 文 / rumor 文 / truth_status / spread_radius / online_reach」を持つ。
     **観測側だけが ground_truth を知る**(エージェントには曖昧なまま届く)。
  2. **truth_status 5分類**: `TRUE / FALSE / UNVERIFIED / CORRECTION / MISLEADING`。
     `net/infoenv.py:186-195` の現行 misinfo イベント(`kind: post|correction|flame`)を
     `truth_status` つきに拡張(旧値は `post→UNVERIFIED` へ写す互換写像)。
  3. **訂正は特権チャネルにしない**: 現行 `amplify_reshare` による訂正拡散(`infoenv.py:190`)を
     **一投稿として競合**させ、`correction_delay_steps` を掃引軸にする。
     **バックファイア効果は実装しない**(Wood & Porter 2019 が 10,100 名超でほぼ検出せず)。
     代わりに **CIE**(訂正で信念強度は下がるが行動は変わらない)を表現する = 信念と行動の分離が要る → 4.
  4. **ラベル別信念強度**: agent の動的属性 `_belief{item_id → float}`(OFF時は属性を生やさない=
     pickle/checkpoint バイト一致。先例=`relations` の closeness 動的キー)。
     更新は**非LLM の決定論**(聴取回数・情報源種別・訂正接触)= 呼数不変。
  5. **情報源別減衰 + ユニーク報告者**: `direct`(減衰なし)/ `hearsay`(中速)/ `sns`(高速)。
     報告者は**ユニーク集合**で保持(既存 gossip の `adopt_threshold` が既に相異なる知人数で
     数える設計= `gossip.py:13-15`。同じ規律をラベル側へ移す)。
- **conf キー(既定OFF)**: `info_env.misinfo.structured: {enabled: false, catalog: "", statuses: [...],
  correction_delay_steps: 0, decay_by_source: {direct: 0.0, hearsay: 0.05, sns: 0.15}}`。
- **新イベント/L2**: `rumor_belief{item_id, agent, strength, source}`(ON時のみ)/
  L2 4列 `rumor_unverified_share` / `rumor_belief_mean` / `rumor_correction_lag` /
  `rumor_distortion`(= ground_truth と流通文の語彙距離。観測側のみ)。
- **乱数**: 既存 stream `"info"` を再利用(種の抽選のみ)。**always-draw conditionally-use** を
  踏襲して CRN 共分散を壊さない(第62-63バッチの流儀)。
- **テスト**: OFF で golden・draw 数一致 / 5分類の写像が旧イベントと互換 /
  ユニーク報告者で確信度が発散しない(A←B,C・B,C←A の循環で count=1) /
  訂正が特権化していない(全員に届かない)。
- **検収条件**: mock で `rumor_unverified_share` が最大の分類になること(Alberia 実測と同型)。
- **工数**: 2.0-2.5日(上位8件で最大)。**世界再現度への寄与は最大**(渋谷の情報環境の主成分)。

---

### ⑤ 初期個体差ゼロの N 体対照 + 初期フレームのラン単位共変量化

- **狙い**: 研究課題「生まれつきか環境から創発か」に対する**最強の対照条件**。
  traits 分散をゼロにすれば R² の分母が消え、観測された分化は**全て環境と履歴から**と言い切れる。
  workplace の実測は「完全分化でも完全収束でもなく、環境の空隙(ニッチ)の形に従う」。
- **触るモジュール**: `scripts/build_personas.py` / `gen_personas.py`(traits 生成)/
  `engine/simulation.py`(読み込み時の定数化フック)/ `conf/experiments/` にセル追加。
  **シム本体のロジックは1行も触らない**(traits の値を定数にするだけ)。
- **設計**:
  - `agents.traits_uniform: false`(既定)。true で全個体の traits を**プール中央値**に固定
    (乱数ゼロ・決定論)。ペルソナ文(職業・年齢・履歴)は**変えない**
    (=「生まれつきの傾性だけ」を消す。ebiyama 講評の「属性は履歴とパラメータで与える」と整合)。
  - **初期フレーム共変量**: `observer.initial_frame.days: 0`(既定)。>0 で初日 N 日の
    (a) 行動種別の分布、(b) 規範発話の有無(②の検出器を再利用)、(c) 発話数を
    **run 単位のラベル**として `summary.json` の追加キーへ書く(L1/L2 は不変)。
    → `analyze_endo_treatment.py` / `analyze_sweep.py` が層別・共変量として使う。
- **conf キー(既定OFF)**: 上記2つ。新セルは `conf/experiments/homogeneous_traits.yaml`
  (第63バッチ `endogenous_accept.yaml` の6セル形式・CRN 同一 seed 列をそのまま複製)。
- **新イベント/L2**: なし(run 単位の summary キーのみ)。
- **乱数**: **ゼロ**。traits を定数にすると `k` 由来の draw が減るのでは? → **減らない**:
  traits は生成時に固定される静的値で、実行時の draw は個体IDと step から決まる
  (`rng.py:23-30`)。ただし **k 呼数の交絡**は第66バッチの `controls.mode=compute_matched` を
  併用して潰す(endo7 の 9.5% 乖離の再発防止)。
- **テスト**: traits_uniform ON で全個体の traits が同値 / 同一 seed で2回走らせてバイト一致 /
  OFF で golden 一致 / summary の初期フレームキーが決定論。
- **検収条件**: mock 3日 × 2セル(uniform ON/OFF)で **draw 数が完全一致**することを直接固定。
- **工数**: 1.0日。**②③の後に回してよい**(実験セルなので本選前の余裕枠に収まる)。

---

### ⑥ 沈黙・不参加・不使用の第一級化

- **狙い**: 「関わらない自由」が選べないシムは現実から乖離する(ICE 環境研究では
  「社会的相互作用の量を自分で調節できること」が最重要設計要素)。
  workplace の最大の発見は「拾えなかった声 136 件 > 拾えた声 107 件」だった。
- **触るモジュール**: `cognition/deliberate.py`(ヘッダ1行 + parse)/ `engine/scheduler.py`(適用)/
  `observer/aggregate.py`(L2)。
- **設計**:
  - `freedom.explicit_nothing: false`(既定)。true のときだけヘッダに1行を足す:
    `{"action": "nothing"}` +(中立記述のみ・理由や推奨は書かない)。
    **既存 `freedom.open_actions` が "do" 1行を足す前例(`deliberate.py:41-46`)と完全同型**
    なので、ゴールデン保護の作法がそのまま流用できる。
  - `parse_action` は `nothing` / `none` / `stay` を **常に寛容受理**(OFF時は提示されないだけ=
    P2 の `move_home` 等と同じ「提示されないが解釈は受ける」流儀・`deliberate.py:451`)。
  - `wander → stay` との違いを L1 で区別する(`stay{reason:"chosen_nothing"}`)。
- **conf キー(既定OFF)**: `freedom.explicit_nothing: false`。
- **新イベント/L2**: 新イベントなし(既存 stay の payload 拡張)。L2 3列
  `silent_agent_rate`(当日 speak/post/dm が 0 件の個体率)/ `chosen_nothing_rate` /
  `unused_facility_rate`(POI・組織・SNS のうち当日 1 度も使われなかった割合)。
- **乱数**: ゼロ。**LLM 呼数不変**(選択肢が1つ増えるだけ=呼数は同じ)。
- **テスト**: OFF でヘッダ・golden バイト一致 / ON で "nothing" が受理され stay へ写る /
  `silent_agent_rate` が沈黙個体を正しく数える / 既存 `test_free_action.py` 回帰。
- **検収条件**: ON/OFF で **LLM 呼数が完全一致**(FixedLLM)。
- **工数**: 0.5日。①と同一バッチにすると parse 層を1回だけ触ればよい。

---

### ⑦ ダンバー認知枠(維持コスト)+ 忘却/再会イベント

- **狙い**: Granovetter の弱い紐帯理論の要点は「**維持コストが低いから多く持てる**」。
  維持コスト(=認知枠の消費)を実装して初めて強い/弱い紐帯の非対称性が**内生的に**出る。
  第64バッチの `invite_weak_tie_rate` と相補的な指標になる。
- **触るモジュール**: `agents/memory.py:126-143`(既存 LRU を拡張)/ `relations.py`(tier 別上限)/
  `observer/schema.py` / `observer/aggregate.py`。
- **設計**:
  - 既存 `memory.relations_max`(既定 0 = 無制限)を残しつつ、`relations.cognitive_cap` を新設:
    **tier 別の入れ子上限**(親友 5 / 友人 15 / 知人 50。`friends.py:12` が既に使っている
    Dunbar 入れ子と同じ値を単一の源にする=SSoT)。
  - 超過時は **LRU 退避 + `relation_evict{other, gap_days}` イベント**(現行は無言で削除)。
  - 退避先を `_evicted{other → last_step}` に保持し、再接触で
    `re_encounter{other, gap_days}` を発火(**忘却 → 再会**を型を持ったイベントにする)。
  - **数値は必ず config 化**(Lindenfors 2021 が 150 という値自体を否定している=感度分析対象)。
- **conf キー(既定OFF)**: `relations.cognitive_cap: {enabled: false, close: 5, friend: 15, acquaint: 50}`。
- **新イベント/L2**: `relation_evict` / `re_encounter`(ON時のみ)/ L2 2列
  `relation_evict_rate` / `reencounter_rate`。
- **乱数**: **ゼロ**(LRU は last_step 最古・同点は id 昇順の決定論。既存 `memory.py:139-141` と同型)。
- **テスト**: 上限超過で最古が落ちる / いま触れた相手は落ちない(既存不変条件) /
  再接触で `gap_days` が正しい / OFF で golden・pickle バイト一致(動的属性を生やさない)。
- **検収条件**: resume(mid-day)で退避台帳が復元されること(第62バッチ joint 状態の
  checkpoint 中央管理と同じ検収=**この種のギャップが過去に実際に出ている**)。
- **工数**: 1.5日。

---

### ⑧ 場所の知覚二層化(pass / enter)+ 場所単位の一斉配信

- **狙い**: **移動が情報獲得の意味を持つ**ようにする(「なぜそこへ行くのか」の内生化)。
  第69バッチ D1 が「命名 → 場所 → 他者の知覚 → 採用」の経路を開いたが、
  **場所そのものが持つ情報**はまだ「店名と人」しかない。渋谷は館内放送・駅の電光掲示板・
  街頭ビジョン・防災無線が**実在する**ので realism-first-scale と完全に整合する。
- **触るモジュール**: `world/scene_desc.py`(pass/enter 二層の記述)/ `street.py`(放送チャネル。
  OOH と同じ層に置く=CHECKED_DIRS 外)/ `observer/schema.py` / `observer/aggregate.py`。
- **設計**:
  1. **二層知覚**: POI ごとに `pass`(通りすがりに見える事実)と `enter`(入って初めて分かる事実)を
     **EnvPack 側のデータ**として持つ(基盤 conf は空=機構のみ。第18バッチ ads の
     `large: [] / slots: []` と同じ流儀)。プロンプトへは**状態記述のみ**を注入し、
     評価語・推奨語は書かない(D1 の `_PLACE_LINE` と同じ規律・`labeling/labels.py:26`)。
     `stay`/`arrive` イベントで enter 側、通過で pass 側を選ぶ(既存の在館判定を再利用)。
  2. **一斉配信**: `street.pa`(館内放送・電光掲示)。指定ノードに**在館中の全員**へ
     同一の1行が同時に届く。個体間伝播とは**独立した経路**なので、
     Katz & Lazarsfeld の two-step flow を検証枠組みに乗せられる。
     内容は `conf` のカタログから(LLM に生成させない=呼数不変・指紋回避)。
- **conf キー(既定OFF)**: `world.scene_desc.two_layer.enabled: false` /
  `street.pa: {enabled: false, nodes: [], schedule: [], ttl_steps: 1}`。
- **新イベント/L2**: `pa_broadcast{node, text_id}` / `pa_hear{node, agent, text_id}`(ON時のみ)/
  L2 2列 `pa_reach_rate` / `perceive_enter_share`(enter 由来の知覚行が出た割合)。
- **乱数**: **ゼロ**(放送は暦・config の純関数。視認確率を入れない=**距離だけの ads と対照的に、
  同一場所内は全員到達が現実**)。LLM 呼数不変。
- **テスト**: OFF でプロンプト1バイト不変・golden 一致 / 在館者全員に届き非在館者に届かない /
  pass/enter の切替が滞在種別で決まる / envpack を空にすると 0 件。
- **検収条件**: 「同一情報が放送経由と口伝経由で別々に到達した件数」を分離して数えられること
  (=two-step flow の寄与分離が成立する最小条件)。
- **工数**: 1.5-2.0日。**B-L1(可視行列の配線)とは独立**に入る(C0 の LOS を待たない)。

---

### 第9候補: 観測健全性3点セット(保険・0.5日)

上位8には入れないが**極めて安い**ので、いずれかのバッチに同梱を推奨。

- **死んだ状態変数検出**: プロンプトに載る全状態変数について、mock 3日ランで値が一度も変化しない
  ものを警告するテスト(意図的定数は allowlist)。psychology-simulation の `stress_level=0.3` 固定が実例。
- **相補的 KPI 検出**: L2 CSV の列間相関 |r|>0.98 のペアを警告するスクリプト。
  登録アグリゲータは既に 85+ 件(`observer/aggregate.py`)まで膨張しており、
  「率とその補集合の率」を別々の発見として書く事故のリスクが実在する。
- **プラセボ介入の事前宣言**: 「このセルは**効いてはならない**」を
  `docs/plans/stationarity-preregistration.md` に日付つきで宣言し、
  `analyze_endo_treatment.py` のゲート判定に「プラセボが動いたら実装リークを疑う」行を足す。

---

## 3. 落選・保留の候補(理由つき)

### 3-A. 既に実装済み(そのまま重複)= 8件

| 台帳の候補 | 実装箇所 |
|---|---|
| 数値を隠して気分ラベルだけ渡す(all-in-smoke) | `factors/mood.py:8-24` `mood_text` — 構成概念名も数値も LLM に出さない |
| 屋内/屋外の情報遮断(good_echo) | `world/perception.py:1-5`「非ブロードキャスト原則」 |
| 伝播の辺リストを独立系統に(ebiyama) | `observer/schema.py:29` `transmission{item_id, from, channel}` |
| 通信グラフからの役割 induction(柴田fire) | `scripts/analyze_founders.py`(次数/媒介中心性・発信超過)+ `scripts/analyze_structure.py` |
| 不完全記憶=鮮明度 decay + 確率的欠落(my-social-agents) | `agents/memory.py:19-36` ACT-R(冪乗則忘却・fan effect・想起失敗 `query_ex.failed`・既定OFF) |
| パース失敗の隔離 + fallback 率 KPI(psychology / lunar_agents) | 第66バッチ `observer/aggregate.py:843-910` `llm_fallback_rate` + `scripts/watchdog_llm.py` |
| sham/null 対照(meta-pop / near-future) | `k.writeback=sham/off` + `controls.mode=null_series/compute_matched` |
| 保存量と参照量の分離(fire-public / mars) | `agents/memory.py` buffer_cap(保存)⇄ retrieve 上位N(参照)が既に別 |

※ このほか **complex contagion の閾値設計**(labels `adopt_threshold=2` / gossip の
「相異なる知人数」)、**語彙エントロピー**(`measure.py:695-712`)、**ペルソナ逸脱率**
(`observer/deviation.py`)、**規範発話検出**(`detect_emergence.py:440-470`)も既存。

### 3-B. 明確に落選

| 候補 | 落選理由(1行) |
|---|---|
| 「死」を第一級イベントに(near-future) | 実在渋谷が舞台のため倫理註記が不可分で、機構コストより**説明コスト**が大きい。組織の解散/役職喪失で同型の観測が取れるので本選後 |
| 制度転換 transitions / k ヒステリシス双方向掃引 | mid-run の状態差し替えは checkpoint 検収が重く(第62バッチで joint 状態の未保存ギャップが実際に出た)、本選前レーンに入れると 10日ランのリスクになる |
| public/private 3層発話(singulab) | 出力フィールドを増やすほど LLM が「埋めるための思考」に引かれる=作為性上昇。まず ablation セルで検証すべきで、既定投入は不可 |
| 非同期エージェント別スレッド(ebiyama) | **決定論・CRN・ゴールデンテストと真っ向から衝突**。当プロジェクトは意識的に別の道を選んでいる(トレードオフの明示だけを提出物へ) |
| バックファイア効果の実装 | Wood & Porter (2019) が 10,100 名超でほぼ検出せず。**実証知見に反する機構は入れない**(代わりに CIE を④で表現) |
| 非対称クランプ `max(new, old×r)` | 下降経路を機械的に消す。当方の変化率クランプは上下対称を維持する |
| 発話のコピー禁止指示 | **語が逐語で伝わること自体が観測対象**。禁止すると測っているものが伝播か禁止の効きか分からなくなる(③で観測側から解く) |
| プロンプトによるエコー抑制 | singulab の実例で A が下がった。③の「観測側で数えて除外」が正しい解 |
| タスク成功率を KPI に据える | 成功率を目標に置いた時点で創発研究ではなくなる(A9.0→A4.0 の直接原因) |

### 3-C. 保留(価値はあるが今回の上位に入れない)

| 候補 | 保留理由 |
|---|---|
| cheap talk(発話⇄実挙動の乖離、一般版) | `joint_fulfill_rate` が既に同型の1本を持つ。②③で発話側の測定精度が上がってから一般化する方が設計が固まる |
| LLM 方向バイアス監査 + 選択肢シャッフル null | 誘い先候補の並べ替えは既に `(agent,day)` 安定ハッシュ(第64)。屋内 SFM の移動方向は物理で決まるため露出面が小さい。監査スクリプトのみ後日 |
| per-call シード(温度維持) | mock は `rng_key` で決定論済み。API 経路の seed は本選のローカル推論(vLLM は seed 対応)で再検討する方が実測に基づく |
| 個体の固着(stuck)KPI | 第66バッチ D0(`diagnose_stationarity.py`)が「burn-in 約18日」を既に検出しており、目的が一部重複。②③の後に差分だけ足す |
| 行動カテゴリ分布エントロピー | 語彙側 `vocab_entropy` の写しで実装は容易だが、単独では判断材料にならない。第9候補群に同梱 |
| 圧力フィールド→閾値→状況ラベルの3段変換 | 屋内 SFM の密度・待ち時間から状況文を作る型。**魅力的だが B-L1(屋外SFM)の後**の方が素材が揃う |
| 係数の YAML 外部化(ミクロ↔マクロ) | 較正対象が明確になる利点はあるが、第62-64バッチの Python 実装を動かすリスクに見合わない。conf 化は新規機構から順次 |

---

## 4. 推奨投入順(本選前レーン想定)

| 順 | 候補 | 工数 | 根拠 |
|---|---|---|---|
| 1 | ③エコー/自己反復 | 1.0日 | **他の全ての伝播数字の前提**。入れないと②④の主張が反復癖の関数 |
| 2 | ①未定義行動 + ⑥沈黙の明示 | 1.0日 | parse 層を1回だけ触る。①は研究直結度が最も高い(操作的定義) |
| 3 | ②規範化ステージ + 命名者/制度化者 | 1.5日 | 自然造語の下流。観測側のみ=no-fingerprint を1バイトも触らない |
| 4 | ⑤初期個体差ゼロ + 初期フレーム | 1.0日 | 実験セル追加のみ。CRN 基盤に素直に乗る |
| 5 | ⑦ダンバー枠 + 忘却/再会 | 1.5日 | 第62-64 の直系。resume 検収に注意 |
| 6 | ⑧場所の二層知覚 + 一斉配信 | 2.0日 | 世界再現度は最大級。D1 の延長で B-L1 を待たない |
| 7 | ④誤情報の構造化 | 2.5日 | 最大の作業。3モジュール統合のため設計レビューを先に |
| — | 第9候補(健全性3点) | 0.5日 | どこかのバッチに同梱 |

合計 約11日。**全て既定 OFF・決定論・LLM 呼数不変**で設計してあるため、
10日ランへのリスクは第66-69バッチと同じくゼロ(OFF = golden バイト一致)。
