# エージェントの自由度 監査 — 現行行動空間の棚卸しと現実とのギャップ

> 調査依頼(2026-07-10): 「以前、文献でエージェントの自由度が重要だという話をしていた。今の
> シミュレーションでどれぐらいエージェントに自由度が与えられているか調べてまとめてほしい。現実と
> 比べて足りていない分野があればまとめてほしい。」
>
> **本ドキュメントは読み取り調査のみ**。コード・schema・config は一切変更していない。採否と優先順位は
> 主エージェント/ユーザーが決める。既読の把握元は `src/society/cognition/{deliberate,routine,planning}.py` /
> `src/society/{tools,economy,household}.py` / `src/society/engine/scheduler.py` / `conf/{config,production}.yaml` /
> 既存調査 [`rights-institutions-gap.md`](./rights-institutions-gap.md) / [`world-change-motivation.md`](./world-change-motivation.md)。

---

## 0. 要旨(3行)

1. **「自由度」には2軸ある**。①**内的自由度**=思考頻度・信念書き戻し(本プロジェクトが「agency」「k」として操作化してきた軸)。
   ②**行動的自由度**=選べる action の広さ。本監査は主に②を棚卸しする。
2. **世界改変の行動空間は先行研究より厚い**(制度提案→署名/投票/議会、起業、組織化、SNS)。一方で
   **生活基盤の自己決定(職業選択・退職・移住・家族形成・消費・逸脱・無為)はほぼ全てルールベースで、エージェントに拒否権がない**。
3. LLM がアクションを選べるのは**「発火」したときの発話系+改変ツールだけ**。移動・出退勤・就寝・家賃・消費・
   キャリア変化・家族形成は `routine.py`/日次機構が**乱数と物理情報だけで**決めており、LLM の選択肢に入っていない。

---

## 1. 過去の議論(自由度・agency・自律)

コードベースの docs を横断検索した結果、**「行動空間の広さ」を正面から棚卸しした文書は無かった**が、隣接する
設計判断・文献調査が複数存在する。関連度の高い順:

| 出典 | 論点 | 現行設計への含意 |
|---|---|---|
| `artificial_society_sim_handoff.md` L31 | **「主体性(agency)= 思考頻度」=認知の"量"** | 本プロジェクトの「agency」は**行動空間の広さではなく、自発的に思考を始める頻度**として操作化されている。今回ユーザーが問う「自由度」は**別軸(行動的自由度)**であり、これまで正面から扱われていない。 |
| `decision-agenda.md` / `design.md` §66,236 | **k の主軸=内省の「信念書き戻し自由度」**(free/degraded/sham/off) | 「自由度」を**内面(信念更新)側**で操作化してきた。`conf/config.yaml` の `k.writeback: free` 既定。**行動側の自由度は k とは別の座標**。 |
| `rights-institutions-gap.md`(Opus 2026-07-07) | 現実の権利・適正手続とシムの差分 | **本監査の直接の先行調査**。「世界を変える行為は厚いが、それを可能にし制約する権利の層が薄い」。移動=あり/住居移転=なし/解雇=無条件確率、等を既に列挙済み(§4 で引用)。 |
| `world-change-motivation.md`(バッチA 2026-07-06) | 5改変ツールが実LLMランで**0回**使用 | **自由度が"ある"ことと"行使される"ことは別**。ツールを合計2,654回提示しても選ばれなかった。「選択肢が隠れていた」のではなく「提示されても選ばれない」。→ 行動空間を広げるだけでは足りず、動機(不満・興味)との接続が課題。 |
| `lit/motivation__sdt-flow-overview.md` / `lit/needs__individual-differences.md` | SDT の**自律(autonomy)/有能感/関係性** | 標準ルール「**動機は注入せず、充足"可能"な affordance として置く**」。自律の感受性を trait 個体差に写像(`needs.py`)。=「自由を保障する」より「自由を求める個体差を作る」方針。 |
| `lit/gamedesign__emergent-systemic-overview.md` | MDA framework・**player agency = agent agency** | **Mechanics(=affordance / verb registry / 4層基層)だけ設計し、Dynamics(世界改変・文化)は創発させる**。「行動空間=Mechanics の広さ」が創発の可能性空間を規定する、という設計哲学(no-fingerprint の工学版)。 |
| `lit/ontology__searle1995_institutional-facts.md` | **deontic power = 制度が action space を動的に拡縮** | 創発した規範が新 verb を解禁/禁止する seam(現状 verb registry は静的)。 |
| `research-scope.md` L57 | open-ended evolution / **開放アクション空間** を P1 として `actions`/vision に紐付け | 「開放的な行動空間」は研究スコープに明示されているが、実装は改変ツール5種+発話系に留まる。 |

**結論**: 過去に「自由度」を論じたのは主に**①内的自由度(思考頻度=agency、信念書き戻し=k)**と
**②権利・制度の層(rights-gap)**。今回問われている**行動的自由度(選べる行動の広さ)そのものの棚卸しは未実施**であり、本監査が初出。

---

## 2. 行動空間の棚卸し表(LLM が選択できる action)

### 2.1 発動の前提 — LLM はいつ選べるのか

`engine/scheduler.py::_decide` の流れ(agent 1体 / 1step):

1. **勾留中**(`detained_until`、production では enforcement 執行時に3step)→ `stay`(何もできない)。
2. **話しかけられた**(`_reply_to`)→ 抽選なしで**必ず LLM 返答**(予算があれば)。
3. **発火権を得た**(`_fire_reason`。`_phase_drive` で drive ゲージ≥閾値 → 個人重み抽選 → 予算ゲートを通過)→ **LLM 発火**(下表のアクションを1つ選べる)。
4. **上記いずれでもない**→ `routine.decide`(§3 のルールベース身体行動)。`stay` かつ携帯所持なら SNS 閲覧を挟む。

つまり **LLM が「行動」を選べるのは、話しかけられた時 or drive 発火した時だけ**。それ以外は身体が routine に支配される。
発火は「drive ≥ 閾値 かつ 抽選当選 かつ 予算残」の三重ゲート(`_phase_drive`)。

### 2.2 選択できるアクション一覧(`deliberate.parse_action` + プロンプト行動メニュー)

| action | 内容 | 提示経路 | 発動条件・制約(場所・金・許可・時間) | 効果(客観カウント) |
|---|---|---|---|---|
| `speak` | 近くの人に話す/独り言 | 常時(ヘッダ) | 発火権。対面は同席者+会話クールダウン外で確定発火 | 発話ログ・知覚伝播 |
| `post` | SNS 投稿 | 常時(ヘッダ) | `has_phone`。発火 reason=news/post で誘発 | タイムライン伝播 |
| `dm` | DM 送信 | 常時(ヘッダ) | `has_phone`+相手(contacts/直近DM元) | 相手の記憶・drive |
| `coin_label` | 状況に新しい呼び名を付ける | 常時(ヘッダ) | `labeling_mode`(constrained/open)。**促進しない=観察対象** | 語の発生・伝播 |
| `wander` | その場に留まる(=`stay`) | 常時(ヘッダ) | なし | no-op |
| `plan` | 朝の一日計画(2〜5件)| 起床直後1回(`planning.make_plan`)| 全員毎朝1回。**非拘束**(routine 行き先の「土台」で強制でない) | day_plan(routine が消化) |
| `reflect` | 内省(信念/自己像/関係の書き戻し)| 就寝直後(`maybe_reflect`)| **k.writeback ゲート**(free/degraded/sham/off)。深い内省は強い出来事が誘発 | beliefs / self_model 更新 |
| `recall` | 内省の agentic pull(何を思い出すか)| 内省中 | agentic_pull=true 時 | 記憶想起1回 |
| **`host_event`** | イベント/勉強会を主催 | ツール(`equip_all` or `offer_text`)| **条件なし**。深夜開始は翌朝繰延 | 参加者集客・教育(語の複雑感染) |
| **`post_flyer`** | 今いる場所に貼り紙 | ツール | **条件なし**。1ノード最大3枚・TTLあり | 通行人の閲覧・語伝播 |
| **`found_group`** | コミュニティ結成 | ツール | **条件なし** | 知人が確率加入・相互フォロー |
| **`propose`** | 街の取り決めを提案 | ツール | 既定なし。**production では投票ルート ON で供託金30000円**(払えねば演説どまり)。制度DSL rule 併記可(fee/bonus/curfew/weekly_event/declare/repeal)| 署名25% or 決定論投票で成立→実効ルール自動制定 |
| **`open_venture`** | 屋台・店を開く | ツール | **所持金30000円以上**。production では**営業許可待ち6step+却下15%**、破産直後は制限 | 通行人が buy_prob で購入・売上 |

**補足**: `move_to`(移動)は `actions/registry.py` に verb 定義があるが、**`parse_action` の発火アクションには存在しない**。
移動は routine と day_plan(非拘束)だけが決める。すなわち**LLM は「どこへ行くか」を発火時に直接選べない**。

---

## 3. ルール強制領域(エージェントに拒否権がない)

`cognition/routine.py` は冒頭コメントどおり「**移動・滞在・日課(通勤/食事/帰宅/就寝)のみ。すべて乱数と物理情報だけで決める(因子は見ない)**」。
以下は LLM の選択肢に入らず、エージェントが「嫌だ」「やらない」を選べない領域。

| 領域 | 挙動 | 根拠コード | 拒否権 |
|---|---|---|---|
| **就寝** | `bedtime_reached`(個体別就寝時刻+4時間窓)で自宅へ強制帰宅→就寝 | `routine.decide` L445-470 | **なし**(イベント/在宅メディアで開始遅延のみ。夜更かしの能動選択不可) |
| **出退勤・勤務** | `in_work_window` で職場へ強制移動・勤務中は `stay` | `routine.decide` L484-525 | **なし**(欠勤は `health` の病気=確率発症時のみ。「行きたくない」で休めない) |
| **通勤経路・交通手段** | `router.route` が経路決定、`_choose_mode` が距離×保有×確率で徒歩/自転車/車、`_augment_ride` がタクシー/バス | `routine._choose_mode` L119-128 / `_ride_extra` | **なし**(手段は乱数、LLM 非選択) |
| **食事** | `in_meal_window`×`meal_prob` の抽選で飲食店へ | `routine.decide` L546-560 | **なし**(食べる/食べないも確率) |
| **消費・買い物** | 屋台購入=`buy_prob` 抽選、POI 消費=カテゴリ固定価格。残高不足なら候補から除外されるだけ | `tools._buy_at_ventures` L1073 / `routine._poi_price` | **なし**(「買う」意思決定が存在しない) |
| **自由時間の行き先** | `choose_destination`(EPR)/day_plan(soft)/群集/趣味/Lynch 等の乱数選択 | `routine.decide` L577-616 | **限定的**(day_plan で朝に希望を出せるが非拘束・上書きされうる) |
| **家賃・固定費** | 給料日25日に月給→翌日家賃(月収×0.3)自動引落。固定費 `fixed_cost_daily` 日次控除 | `conf/production.yaml` accounts / economy | **なし** |
| **就労状態の変化(解雇/転職/再就職/起業転換)** | `career` の**日次確率イベント**(layoff/switch/rehire/venture_fulltime) | `economy.build_career_cfg` / `scheduler` career 機構 / `tools._ventures_fulltime` | **なし**(「辞める」「転職する」「応募する」を選べない。全て確率) |
| **家族形成** | `form_partners` が近接×確率でパートナー成立 | `household.form_partners` L190 | **なし**(結婚/しないの選択なし。**離婚・出産・死別は未実装**=世帯は初期化でほぼ固定) |
| **健康行動・受診** | `health` の発症 `onset_prob`・受診 `medical_prob` は確率。慢性不満で `withdrawn`(引きこもり) | `conf/production.yaml` health / `routine._sick_home` L132 | **なし**(通院を拒む・セルフケアの選択なし) |
| **災害時の外出抑制** | `disaster.is_homebound` で在宅へ強制(`stay_home_bias`) | `routine.decide` L480 | **なし** |
| **勾留** | enforcement 執行で `detained_until` まで行動停止 | `scheduler._decide` L1104 | **なし**(当然) |
| **法を破る/逸脱** | 犯罪は `society_diversity` の**被害イベント**(受け身)。**加害・規範違反を agent が選ぶ経路がない** | `society_diversity` crime | **なし**(逸脱行動を能動選択できない) |

---

## 4. 現実との自由度ギャップ表

**参照軸**: 生活時間調査(NHK/総務省 生活時間の行動分類=1次[睡眠/食事]・2次[仕事/家事/通勤]・3次[自由行動])/
WHO ICF「活動と参加」(d5 セルフケア・d6 家庭生活・d7 対人関係・d8 主要な生活領域[教育・仕事・経済]・d9 コミュニティ生活)/
SDT の autonomy(自己決定)。凡例 — **シム現状**: あり / 制限つき / なし。**研究関連度**(世界を変える者の創発への効き): 高/中/低。

| 自由の項目 | 現実の自由 | シム現状 | 根拠コード | 関連度 |
|---|---|---|---|---|
| **職業選択・就職の自発性** | 職業選択の自由(憲法22条) | **なし** | org 配属は初期固定、`career.rehire` は確率 | **高**(職業分化=創発の主要指標。Project Sid の role specialization) |
| **退職・転職の自発性** | 自由に退職・転職 | **なし** | `career.layoff/switch` は日次確率イベント | **高** |
| **起業・出店** | 資金+許可で開業 | **あり** | `open_venture`(所持金+production は許可制) | 高 |
| **住居移転** | 移転の自由(憲法22条) | **なし** | home ノード初期固定。移転イベントなし(rights-gap §B も「なし」) | 中 |
| **家族形成/解消の主体性** | 婚姻・離婚の自由 | **なし** | `form_partners` 確率。離婚・出産・死別 未実装 | 中 |
| **消費の選択幅** | 何を買うか自由 | **制限つき** | `buy_prob`/`meal_prob` 抽選、カテゴリ固定価格 | 中 |
| **貯蓄・投資・資産形成** | 貯蓄/投資は自由 | **なし** | money/account は自動増減。投資・資産運用なし | 低〜中 |
| **教育を受ける・学び直し** | 進学・学習の自由 | **なし** | 学生 role 固定、進学/学び直し選択なし(唯一の学習=`host_event` 聴講の語習得) | 中 |
| **創作・表現(作品制作)** | 自由 | **制限つき** | 言語表現(speak/post/coin_label/found_group)は自由だが、**造形・芸術・永続する作品の制作物なし** | 中 |
| **宗教・思想** | 信教・思想の自由 | **なし** | opinion は1次元スカラー(FJ 力学で更新)。信条・世界観の多次元表現なし | 低〜中 |
| **服装・外見** | 自由 | **なし** | 概念が存在しない | 低 |
| **健康行動(通院拒否・セルフケア)** | 自由 | **なし** | `medical_prob` 確率。拒否・自己治療の選択なし | 低 |
| **移動手段の選択** | 自由 | **制限つき** | 距離×保有×確率で決定、LLM 非選択 | 低 |
| **範囲外への旅行** | 自由 | **制限つき** | `exit_prob` で街の外へ出るが行き先・目的なし=単なる退出 | 低 |
| **深夜行動・夜更かし** | 自由 | **制限つき** | `bedtime` 強制。深夜滞在は来街者の終電待ちのみ、`curfew` rule で抑制可 | 中(逸脱・世界改変者の行動として) |
| **法を破る自由(結果を負う)** | 可能(処罰を伴う) | **なし** | 犯罪は被害イベント=受け身。加害を agent が選べない | **高**(逸脱・抵抗=keystone のドラマ。rights-gap も指摘) |
| **無為に過ごす自由** | 自由 | **制限つき** | `wander`=stay はあるが、routine が常に次の目的地/仕事へ動かす。「何もしない」の能動選択が弱い | 中 |
| **集会・デモを開く** | 届出・許可制(公安条例)| **制限つき** | `host_event`/群集 crowd はあるが、当局の不許可・届出がない(rights-gap A) | **高** |
| **制度を作る・変える** | 請願→パブコメ→議会(多段・否決可)| **あり(厚い)** | `propose`→署名/投票/production では審議・議会・供託金 | 高 |
| **政治参加(投票・立候補)** | 選挙権・被選挙権 | **制限つき** | production は決定論投票+代表制議会+供託金。立候補・選挙運動は簡略 | 高 |

**総合所見**: 現実の人間が持つ「生活の自己決定(職業・退職・移住・家族・消費・教育・逸脱・無為)」のほぼ全てが、
本シムでは**確率イベント or ルール強制**として実装され、エージェント自身の選択に開かれていない。一方で**「世界を変える行為」
(制度・起業・組織化)だけは選択肢として厚く用意されている**。これは意図的な設計(研究の焦点が世界改変)だが、
結果として「不満の源泉になるはずの生活選択の剥奪」自体がエージェントに体験されにくい構造になっている
(例: 嫌な仕事を辞められない不満、住み続けたい家を追われる不満は、**agent の意思決定としては生じない**)。

---

## 5. 先行研究の示唆(行動空間の広さと創発)

| 研究 | 行動空間 | 創発への効き | 出典(docs 内) |
|---|---|---|---|
| **Generative Agents**(Park 2023) | 移動・会話・オブジェクト操作の**自由な行動**+memory/reflection/planning | バレンタインパーティの**自発企画・招待伝播**など長期一貫の社会創発。本シムの reflection/planning の直系の祖 | `research/llm-model-selection.md` L139 / `references.md` |
| **Project Sid / PIANO**(Altera 2024) | 500体×GPT-4o、**10並行モジュール**・social goal を5〜10秒毎に再生成 | **職業分化(role specialization)・集団ルール・文化伝播が創発**。広い行動空間+社会目標の動的再生成が専門分化を生んだ | `research/token-budgets.md` L26,162 |
| **Voyager**(Wang 2023) | Minecraft・**スキルライブラリで無限に拡張**するオープンエンド行動 | 自己検証ループで新規アイテム63発見。**行動空間が開いていること自体が探索の駆動源** | `research/token-budgets.md` L27,163 |
| **OASIS**(2024) | SNS特化**21行動**(post/repost/follow/like/comment/do_nothing…) | 狭くとも群分極・herd・誤情報拡散は創発。ただしドメイン限定 | `lit/mas__yang2024_oasis.md` L12 |
| **LLM-ABM Survey**(2024) | — | 創発パターンに **role specialization** を列挙。**行動の有限性が believability を決める**(Affordable Generative Agents) | `lit/mas__survey2024_llm-abm-survey.md` L11 |
| **MDA / systemic design** | Mechanics=affordance の広さ | **Mechanics だけ設計し Dynamics は創発**。行動空間の広さが可能な創発の空間を規定 | `lit/gamedesign__emergent-systemic-overview.md` |

**含意(1-2段)**: 先行研究で創発(特に **role specialization / 職業分化 / 文化伝播**)を生んだのは、
**移動・操作・職業・オープンエンドな行動の自由**だった。本シムは**世界改変ツール(制度・起業・組織化)を先行研究より厚く
実装している**点で novelty があるが、**生活基盤の自己決定(職業選択・退職・移住・家族・消費・逸脱)がほぼ全てルールベースで
拒否権がない**。とりわけ Project Sid が「専門分化は agent 自身の職業選択・目標再生成から創発した」ことを踏まえると、
本シムの**職業=初期固定・キャリア変化=確率イベント**という設計は、創発しうる分化の幅を上流で絞っている可能性がある。
ただし `world-change-motivation.md` の実測(ツール2,654回提示で0回使用)が示すとおり、**行動空間を広げるだけでは行使されず、
動機(不満・興味)との接続と、選択に開く"生活の自己決定"の設計が対で要る**というのが、既存知見と整合する読みである。

---

## 6. 出典

**コード(把握元)**
- `src/society/cognition/deliberate.py` — 発火プロンプト行動メニュー・`parse_action`(選択可能アクションの正準)
- `src/society/cognition/routine.py` — ルール強制の身体行動(就寝/出退勤/食事/移動/災害在宅)
- `src/society/cognition/planning.py` — 朝の一日計画(非拘束の itinerary)
- `src/society/tools.py` — 5改変ツール(host_event/post_flyer/found_group/propose/open_venture)+制度3ルート+消費/購入
- `src/society/engine/scheduler.py` — 発火ゲート(`_phase_drive`/`_fire_llm`/`_decide`)
- `src/society/economy.py`(career/wage)・`src/society/household.py`(form_partners)
- `conf/config.yaml`(既定 OFF・k.writeback=free)/ `conf/production.yaml`(本番 ON トグル一覧)

**docs(過去の議論・文献)**
- `docs/artificial_society_sim_handoff.md`(agency=思考頻度)
- `docs/decision-agenda.md` / `docs/design.md`(k=信念書き戻し自由度)
- `docs/research/rights-institutions-gap.md`(権利・適正手続ギャップ=本監査の先行調査)
- `docs/research/world-change-motivation.md`(改変ツール0回使用の実測)
- `docs/lit/motivation__sdt-flow-overview.md` / `docs/lit/needs__individual-differences.md`(SDT autonomy)
- `docs/lit/gamedesign__emergent-systemic-overview.md`(MDA・player agency=agent agency)
- `docs/lit/ontology__searle1995_institutional-facts.md`(deontic power=action space の動的拡縮)
- `docs/research-scope.md`(open-ended / 開放アクション空間)
- `docs/research/llm-model-selection.md` / `docs/research/token-budgets.md`(Generative Agents / Project Sid / Voyager)
- `docs/lit/mas__yang2024_oasis.md`(OASIS 21行動)/ `docs/lit/mas__survey2024_llm-abm-survey.md`(role specialization)

> **注**: 現実側の生活行動分類(生活時間調査・ICF・SDT)は本監査では既存 docs 内の記述(SDT overview 等)と
> 一般的枠組みに依拠した参照軸であり、統計値の一次確認は行っていない。数値較正が要る項目は `rights-institutions-gap.md`
> §3(捏造回避)と同様、立案前に一次資料の確認を推奨する。
