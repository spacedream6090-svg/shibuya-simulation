# 経済活動の「物の移動」と「具体的なサービス」の実体化 — 調査と設計

> 目的: ユーザー要望「経済活動をしたときに **物の移動** だったり、**具体的なサービス** が受けられるように
> したい。webでリサーチし実装する方法を模索」に応える。現状は「**金は動くが、物・サービスの実体が
> 無い**」(spend で残高が減るだけ・在庫も商品も提供行為も存在しない)。本書はその穴を file:line で
> 棚卸しし、先行研究(供給網ABM・都市物流・LLM社会シム・ゲーム経済)から移植可能な最小機構を集め、
> 本シムの掟(**既定 OFF・非LLM・決定論+新stream・R1 呼数不変・OFF時バイト一致**)に整合する段階案を
> 提示する。
>
> **本書は調査のみ。コード変更・conf変更は含まない。** 取得日 2026-07-21(WebSearch/WebFetch)。
> 事実と推測は §9【未確認事項】で区別する。
>
> **既存 [`economy-abm-research.md`](economy-abm-research.md) との分担**: あちらは銀行/VC/消費構造/決済
> (**金の回路**)を扱った。本書は **物の流れ(在庫・補充・物流・B2B)と サービスの中身(体験・効果・
> 予約)** に集中する。重複しない。
> **並行バッチとの分担**: 別エージェントが「L2従業者の業務実体(`serve` イベント=接客の **提供側**)」を
> 実装中。本書は **物の流れ** と **サービスを受ける側(消費者体験・財の移転)** の設計に集中し、提供側の
> `serve` とは接続点(seam)だけ定義して重複を避ける(§7-③)。

---

## 1. 要旨(結論から)

- **現状の穴**: この街の経済は「口座間の数値移動」で閉じている。`_spend`(scheduler.py:496)は
  `agent.money` を減らして `spend` イベントを1件出すだけ。**買った物(商品実体)も、店の在庫も、
  補充(物流)も、サービスの提供行為・効果も存在しない**。`commerce.py` の `stock_out` は「在館数=混雑」
  の代理であって、**実在庫の枯渇ではない**(commerce.py:181)。orgs の `products_services`(例:「勤怠・
  労務管理SaaSの開発提供」)や venture の `offer` は **`production`/`venture_open` ログ用の飾り文字列** で、
  誰にも渡らない。
- **移植可能な最小機構**: 供給網ABM の標準は **在庫の (s,S) 補充方策**(下限 s を割ったら上限 S まで発注)。
  日本のコンビニ物流は **1日3回超の多頻度小口配送**(7-Eleven が確立)で、これが「物の移動=配送トリップ」
  の現実較正になる。ゲーム経済(EVE Online)は **財が物理的に存在し、生産チェーン(素材→製品)と地域市場で
  移動が必須** という設計を数十万規模で回している。LLM社会シム(Generative Agents 系)は逆に **経済を金銭
  移転に抽象化** しており、物の実体を持つものは少ない(=本シムの差別化余地)。
- **推奨スライス順**(詳細 §7、優先根拠 §8):
  **① 店舗在庫+日次補充(物流トリップ)** → **② 商品実体を spend に載せる** →
  **③ サービスの実体(滞在+効果+予約)** → **⑤ 会社間取引 B2B(卸→小売)** → **④ 宅配/フードデリバリー**。
  ①が全ての土台(在庫が無いと補充も B2B も宅配も意味を持たない)であり、かつ **災害時の物流断絶の
  表現力**(disaster が補充トリップを止める→実在庫が枯れる→品切れ→パニック買い→grievance)と **k\* 研究
  への寄与**(物理的な財ネットワークを伝播する外生ショック)が最大。
- **工数感**: ①≈2バッチ(2〜3人日)、②≈0.5バッチ(①に同梱可)、③≈1.5バッチ、⑤≈1.5バッチ、④≈2バッチ。
  いずれも既存の commerce/career/health/disaster と同じ「1機構=1モジュール+scheduler配線+conf+test+devlog」型。
- **R1 論点**: 物の流れは **全て非LLM・決定論で組める**(在庫・(s,S)補充・配送ルーティング・B2B 清算)。
  `generate()` を1本も足さない。ただし補充トリップ=**新しい移動体(配送員)** と 品切れ=**購入可否の変化** は
  物理位置・co-location を変えうる(FixedLLM で ON≠OFF になりうる)=commerce.filter_open / career / crowd と
  **同型の既知の性質**。発火・補充・品切れ判定に **k・内面構成概念(efficacy/grievance)を食わせず**、
  在庫量・時刻・config・在館数(観測量)のみ参照すれば compute_matched 下の k 不変性で担保できる(§7 各項・§10)。

---

## 2. 現状実査 — 「金は動くが物・サービスの実体が無い」箇所(file:line)

### 2.1 経済イベントの棚卸し(どこで金が動くか)

| 経済活動 | 実装箇所 | 金は動くか | 物/サービスの実体 | 穴 |
|---|---|:--:|:--:|---|
| 消費 spend(食事/買物/夜遊び/taxi/bus) | `scheduler.py:496` `_spend` | ○ | **×** | 残高減+`spend` ログのみ。商品も在庫も無い |
| 飲食 eating | `scheduler.py:572` `_charge_meal` | ○ | **×** | 価格を払うだけ。料理という財は生まれない |
| 交通 ride | `scheduler.py:592` `_charge_ride` | ○ | △ | 移動という便益はある(唯一「サービスの実体」に近い) |
| 賃金 wage | `scheduler.py:441` `_pay_wage` | ○ | **×** | 労働の産出物と無関係に支給 |
| 勤務産出 production | `scheduler.py:362` `_log_org_output` | 推計のみ | **×** | `products_services` を1件ログするだけ。誰にも渡らない |
| 出店 venture_open | `tools.py:776` `_open_venture` | ○(出店費) | **×** | `offer` は自由文字列。商品在庫は無い |
| 出店売上 venture_sale | `tools.py:1531` `_buy_at_ventures` | ○ | **×** | 通行人が確率で買い、双方が定型文を `remember` するだけ |
| 消費#7 buy(freedom P2) | `scheduler.py:2654` `_apply_buy` | ○ | **×** | cat を price に写して `_spend`。買った物は残らない |
| 受診 medical_visit | `scheduler.py:3223`,`health.py:151` | ○ | △ | 唯一「サービス→効果(回復)」がある。ただし病気起点のみ |
| 敷金/家賃/固定費/税/利息/融資/VC | economy.py・scheduler.py 各所 | ○ | **×**(金融=物不要) | 金融は物が無くて正しい(対象外) |

**結論**: 物・サービスの実体が要る経済活動(消費・飲食・出店売上・勤務産出)は **すべて「価格を残高から
引く」だけ**で完結している。実体があるのは ride(移動便益)と medical_visit(受診→回復効果)の2つのみ、
かつ後者は病気起点に限られる。

### 2.2 「在庫らしきもの」は実在庫ではない

`commerce.py` に `stock_out`/`is_stock_out` があるが、これは **在館数(occupancy=混雑)が閾値を超えたら
品切れ扱い** にする **需要側の代理** で、店が実際に何個持っているかという **供給側の在庫は存在しない**:

- `commerce.py:161` `occupancy(sim, node)` = そのノードの在館 agent 数(混雑)。
- `commerce.py:181` `is_stock_out(cfg, occ)` = `occ >= stock_threshold`(既定6)。
- `commerce.py:194` `on_purchase` = 混雑なら購入抑制(`stock_out` ログ+grievance)、そうでなければ
  混雑に応じた価格係数を掛ける。**在庫を減らす処理・補充する処理は一切無い**。

つまり「6人以上居たら品切れ」であって「商品が売り切れたら品切れ」ではない。**物の在庫と補充(物流)を
入れる余地がまるごと空いている**。

### 2.3 「物流(物の移動)」は存在しない

- 補充・仕入・配送・宅配のコードは無い(`grep inventory|物流|配送|delivery|仕入|卸|supply` の該当は
  commerce/disaster の **注記コメント** と本書関連のみ。実装ゼロ)。
- `_atm_withdraw`(scheduler.py:479)ですら「ATM はどこにでもある近似」で **移動を伴わない**。
- 交通(SUMO/traffic:`scheduler.py:958` `_phase_traffic`、`world/traffic.py`)は **人の移動** を扱うが、
  **貨物・配送トリップは無い**。→ 補充/宅配トリップを足せば **既存の traffic/SUMO と自然に接続** できる
  (物の移動が人流と同じレイヤに乗る)。

### 2.4 「サービスの実体」は薄い(POI は在るが使われていない)

地図データには **サービス系 POI が大量にあるのに、経済的な相互作用が付いていない**:

| cat | 件数(data/*.json) | 現状の経済的役割 |
|---|--:|---|
| `service`(理容/クリニック/塾/ジム/クリーニング等の器) | **1,994** | **ほぼ無し**。バイト割当先ですらない(part_time は shop/food のみ:economy.py:232) |
| `education`/`school` | 115 / 148 | 学生の登校(study ログ)。**塾・習い事としての有償サービスは無し** |
| `shop` / `food` / `nightlife` | 6,586 / 5,088 / 1,301 | 消費先。ただし §2.1 の通り物の実体は無い |

→ **理容・医療・塾・ジム等の「滞在して効果を受ける」サービス** を載せる **物理的な器(service POI 1,994件)は
既にある**。中身(滞在+効果+予約+課金)が空いているだけ。

### 2.5 既存の「接続の素地」(移植の宛先)

| 使いたい既存物 | 場所 | 用途 |
|---|---|---|
| 消費経路(残高分岐・税・決済) | `scheduler.py:496` `_spend` | 商品実体・サービス課金の課金口はここ1つに閉じる |
| 商業ダイナミクス(営業時間・在館数・品切れ枠) | `commerce.py` | **実在庫へ格上げする最有力の宿主**(stock_out の枠が既にある) |
| 出店 venture(offer 文字列・sales_total) | `tools.py` | venture に在庫・仕入を足す最小の起業実体 |
| 組織台帳(production_count・revenue_est) | `scheduler.py:388` `org_ledger` | B2B(卸→小売)の生産・出荷の宿主 |
| 交通/SUMO(人流) | `scheduler.py:958`,`world/traffic.py` | 補充・宅配トリップの走行レイヤ |
| 災害/物流断絶フック | `disaster.py`(suspend_transit 等) | 補充トリップ停止→実在庫枯渇の外生ショック |
| 乱数 stream(既存 draw 順不変) | `rng.py` `sim.hub.stream(用途,id,step)` | 補充/配送/仕入の抽選を既存 draw から隔離 |
| イベント種の追加 | `observer/schema.py` `register_event_kind` | 1行で新 kind(`restock`/`deliver`/`b2b_trade` 等)を追加 |

---

## 3. Web調査① — 供給網ABM・都市物流・在庫方策(物の流れの先行例)

### 3.1 供給網ABM の標準構成(retailer–wholesaler–distributor–manufacturer)

- 供給網ABM は **customer / retail / supply の3種エージェント**(または 小売・卸・流通・製造の **4層**)で
  構成し、各企業エージェントが在庫の意思決定モデルを持つ(AnyLogic 等での標準構成)。**情報共有** が
  在庫振幅(ブルウィップ効果)を抑えるという知見が繰り返し確認されている。
- **Amazon の実運用**: 自社の inbound 供給網を ABM でシミュレートし、確率的な輸送遅延・製造時間・修理時間を
  入れて大規模在庫制御を検証している(HPC 上の実運用事例)。**数万〜のノードでも回る**(計算コストは
  離散事象+単純ルールで軽い=LLM を使わないから)。

### 3.2 在庫補充の (s,S) 方策 = 最小で正しい在庫機構

- **(s,S) 方策**(別名 Min-Max): 在庫が **下限 s(reorder point)以下** に落ちたら、**上限 S(order-up-to
  level)まで補充発注** する。発注はリードタイム後に到着。周期レビュー版が **(R,s,S)**(R 周期ごとに確認)。
- 「在庫がどれだけ s を下回ったか」を見て発注量を決めるため、固定量発注 (R,Q) より無駄が少ない。
- **計算コスト**: 判定は「在庫 ≤ s か?」の比較1つ+「S − 在庫」の引き算1つ。**per-POI・per-tick で O(1)**、
  乱数不要(決定論)。最適な s,S の解析は難しいが、**運用(シミュ内で s,S を固定値で回す)は極めて軽い**
  =本シムの数千 POI でも問題にならない。近年は500万観測から s,S を閉形式回帰する研究もあるが、本シムは
  **s,S を config で与えて回すだけ** で足りる。

### 3.3 都市物流・ラストマイル配送ABM

- ラストマイル配送ABM は **配送車・顧客・交通要素** を相互作用エージェントとして表し、時間帯窓最適化・
  マイクロ配送ハブ・環境配慮ルーティングを評価する。**MATSim / MASS-GT** ベースの実装が代表的。
- 注文生成は **モンテカルロ**(人口・社会統計から parcel 需要を生成)、配送は **宅配ロッカー / クラウド
  配送 / 従来宅配** の3経路。ある事例では最適化で **走行km −59%・CO2 −44%**。
- **本シムへの含意**: 配送を「トリップ生成(depot→店/家)」として置けば、既存の traffic/SUMO レイヤに
  そのまま乗る。注文生成は「在庫が s を割った店」「宅配を選んだ買い手」から **決定論で生成** でき、
  モンテカルロすら不要(=R1 で新 stream 1本に閉じられる)。

### 3.4 日本(コンビニ)の物流較正 — 渋谷の現実再現に直結

- **7-Eleven Japan が確立した多頻度小口配送(cross-docking)**: 全店を **1日3回以上** 補充。ピーク販売の
  直前に配送を合わせる。**足の速い生鮮は24時間に3回、日持ちする品は1日1回〜週数回**。中継の
  クロスドック配送センターに惣菜工場を併設。
- **足元の逼迫(2025)**: ドライバー不足で FamilyMart はおにぎり/弁当を **1日3→2回**、7-Eleven は
  郊外で **4→3回** に削減。→ **物流の脆弱性そのものが災害/人手不足ショックの表現対象** になる。
- **較正の使い方**: 補充頻度は「生鮮(food)= 日3回相当・日用(shop)= 日1回」を s,S のリードタイム/
  レビュー周期の初期値に。渋谷はコンビニ密度が極端に高い=**補充トリップが街を絶えず走る** 絵になる。

### 出典(§3)
- Agent-Based Modeling in Supply Chain (SmythOS, 概説): https://smythos.com/managers/ops/agent-based-modeling-in-supply-chain/
- An agent-based simulation of Amazon's inbound supply chain (AWS HPC): https://aws.amazon.com/blogs/hpc/an-agent-based-simulation-of-amazons-inbound-supply-chain/
- Top 3 Most Common Inventory Control Policies((s,S)=Min/Max の実務解説, Smart Software): https://smartcorp.com/inventory-control/inventory-control-policies-software/
- Closed-Form Equations for the Reorder Point and Order-Up-To Level in a Lost-Sales Periodic-Review (R,s,S) Policy (2026): https://ideas.repec.org/a/gam/jmathe/v14y2026i13p2424-d1984694.html
- Supervised Learning for the (s,S) Inventory Model (arXiv 2601.12900): https://arxiv.org/pdf/2601.12900
- A Generic Modelling Framework for Last-Mile Delivery Systems (arXiv 2502.17633): https://arxiv.org/html/2502.17633v1
- Agent-Based Simulation for Last-Mile Delivery Optimization in Urban Environments (SSRN 5262092): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5262092
- The evolution of consumer preferences in last-mile delivery (Rotterdam-The Hague, ScienceDirect, −59%km/−44%CO2): https://www.sciencedirect.com/science/article/abs/pii/S0739885925001076
- How Convenience Stores Dominate in Japan(3回/日補充): https://www.ulpa.jp/post/how-convenience-stores-dominate-in-japan-a-complete-guide
- What Makes 7-Eleven Japan Unstoppable?(多頻度小口・クロスドック): https://globis.eu/what-makes-7-eleven-japan-unstoppable/
- Amid Driver Crisis, Japan… delivery adjustments(2025 配送回数削減): https://markets.financialcontent.com/clarkebroadcasting.mymotherlode/article/merxwire-2025-9-18-amid-driver-crisis-japan-turns-to-international-workers-and-delivery-adjustments-to-keep-services-running

---

## 4. Web調査② — LLM社会シムでの物・サービス表現(たいてい抽象=金銭移転)

### 4.1 予想どおり「金銭移転への抽象化」が主流

- **Generative Agents / Smallville**(Stanford, 2023): 記憶ストリーム+反省+計画の認知アーキが主眼で、
  **経済(物・在庫・生産)はほぼ扱わない**。店は「行ける場所」であって在庫のある売り場ではない。
- **EconAgent**(ACL 2024)/ **AgentSociety**(2025, 清華, 1万体超): 経済は入るが **抽象**。EconAgent の
  LLM が決めるのは「労働意欲」と「消費性向」の2つのみで、賃金・物価・税・金利は方程式。**財は
  「消費に使う金額」であって、個々の商品や在庫としては表現されない**(§既存 economy-abm-research.md §2)。
- **EconSimulacra**(2026, arXiv 2606.26883)/ 経済シム系: 企業エージェントが **需給に応じて価格と賃金を
  動かす**が、財は「market demand を満たす総量」で、**物理的な在庫・輸送は抽象**。

### 4.2 反例(物の実体を持たせた系)— 重要

- **MMO 経済 × 生成ABM**(KDD'25, arXiv 2506.04699「Empowering Economic Simulation for MMO Games through
  Generative Agent-Based Modeling」): ゲーム経済は **アイテムが実体を持つ**(生産・取引・消費される)前提で、
  LLM エージェントに **その財経済** をシミュレートさせる系。**「LLM の質的判断 × 実体を持つ財のルール経済」の
  組合せ** は本シムの狙いに最も近い(※本文 PDF は静的取得不可=題目・キーワード・要旨レベルで確認。
  実装値は未確認=§9)。
- **GATSim**(2506.23306): 生成エージェントの **都市モビリティ**。人の移動を LLM 意思決定で動かす系。
  貨物ではないが「移動を伴う経済活動」を LLM 社会シムに載せる先例。

### 4.3 含意 — 本シムの差別化余地

- LLM 社会シムの主流が **金銭移転への抽象** である以上、**物の実体(在庫・補充・物流)と 具体的サービス
  (滞在+効果+予約)を非LLMの機械層で載せる** ことは、既存研究に対する **明確な上積み** になる。
- ただし **LLM に経済判断を委ねすぎない**(貨幣錯覚・マクロ変数への鈍さ)という先行研究の教訓は堅持:
  物の流れ・在庫・補充・B2B・配送は **すべてルール/決定論**、LLM は既存の「buy を選ぶ」「起業する」等の
  **発火だけ** に留める(=R1 と両立、既存 economy-abm-research.md §2 の分業原則を踏襲)。

### 出典(§4)
- Generative Agents: Interactive Simulacra of Human Behavior: https://arxiv.org/abs/2304.03442 ・ 概説: https://www.emergentmind.com/topics/generative-agents-smallville
- AgentSociety (1万体超): https://arxiv.org/abs/2502.08691
- EconSimulacra: A Digital Twin Platform of Socio-Economic Systems Powered by LLM Agents (arXiv 2606.26883): https://arxiv.org/html/2606.26883v2
- Empowering Economic Simulation for MMO Games through Generative ABM (KDD'25, arXiv 2506.04699): https://arxiv.org/pdf/2506.04699
- GATSim: Urban Mobility Simulation with Generative Agents (arXiv 2506.23306): https://arxiv.org/pdf/2506.23306
- Integrating LLM in Agent-Based Social Simulation: Opportunities and Challenges (arXiv 2507.19364): https://arxiv.org/pdf/2507.19364

---

## 5. Web調査③ — ゲーム/経済シムの実装知恵(移植可能な最小機構)

### 5.1 EVE Online — 財が物理的に存在する player 駆動経済

- **ほぼ全アイテムがプレイヤー生産**: 原鉱の採掘→(設計図 blueprint + 素材)→製造→製品 という **生産チェーン**。
  素材を入れて製品が出る、という **入力→出力の物質収支** が明示的。
- **財の物理性(physicality)**: アイテムは **売られている station に物理的に存在** し、買ったら **自分で運ぶ** 必要が
  ある。市場は **地域(region)ごと** に分かれ、取引はその地域内に限られる。→ **「物は場所に在り、移動が要る」**
  という設計が、そのまま「渋谷の店に在庫があり、補充で運ばれてくる」に対応する。
- **移植する最小核**: ①**入力→出力のレシピ**(製造/調理は素材を消費して製品を作る)、②**在庫は場所に紐づく**
  (POI/venture が個数を持つ)、③**移動しないと物が届かない**(補充=トリップ)。この3つだけで「物の移動」の
  骨格になる。EVE の複雑さ(多段レシピ・研究)は要らない。

### 5.2 コロニーシム(RimWorld / Dwarf Fortress / Mountaincore)— 在庫・運搬・生産チェーン

- **ストックパイル(在庫置場)+ハウリング(運搬)**: 素材は場所に山積みされ、コロニストが **運搬労働** で
  ワークショップへ運び、加工して製品にする。**「生産の集約・専用倉庫・運搬距離の最小化」** が最適化の勘所
  (=物流コストが実際に効く)。
- **生産チェーン**: 原材(石・木)→加工(家具・機構)→交易品。DF は水・マグマまで含む深いチェーンを持つが、
  **本シムに要るのは1〜2段**(素材→商品、または卸→小売)で十分。
- **移植する最小核**: **在庫は物理位置に置かれ、運搬(労働=トリップ)で移動する**。これは §5.1 と同じ結論で、
  **「在庫+補充トリップ」** が最小単位という点で供給網ABM・コンビニ物流・EVE・コロニーシムが **全て一致** する。

### 5.3 価格形成

- EVE は完全な指値板(order book)。本シムはそこまで要らず、既存の **commerce.price_coef(在館数=需要で
  価格係数)** に **在庫希少度** を1項足すだけで「品薄で高い/在庫だぶつきでセール」を決定論で作れる。

### 出典(§5)
- Manufacturing – EVE Online(生産チェーン公式): https://support.eveonline.com/hc/en-us/articles/203210292-Manufacturing (※直接取得は 403。二次情報で内容確認)
- The Economy of EVE Online(player駆動・生産チェーン・地域市場): https://www.dailygame.net/the-economy-of-eve-online-a-journey-to-virtual-wealth/
- Mastering EVE Online's Player-Driven Economy(財の物理性・地域市場): https://entertainmentforbusiness.com/economy/mastering-eve-onlines-complex-player-driven-economy/
- RimWorld Colony Building Guide(ストックパイル・運搬・生産集約): https://rimworldwiki.com/wiki/Colony_Building_Guide
- Mountaincore's Intricate Production Chains(2D コロニーシムの生産チェーン): https://www.superjumpmagazine.com/mountaincore-draft/

---

## 6. 設計の共通土台(全スライス共通の掟)

先行研究(§3–5)が **一致して指す最小単位** は **「在庫は場所に在り、補充トリップで動く」**。本シムに移植する
にあたり、全スライス共通で以下を守る(既存 commerce/career/health/disaster と同型):

1. **既定 OFF**: 新 config ブロックは `enabled:false` 既定。OFF 時は新イベント0件・新 stream を引かない=
   **ゴールデン `golden_baseline_l1.json` とバイト一致**。
2. **非LLM・決定論(+隔離 stream)**: 在庫・(s,S)補充・配送・B2B・サービス効果は **全て機械層**。乱数が要る
   箇所は `sim.hub.stream("restock"/"deliver"/…, id, step)`(既存 draw 順に不干渉)。
3. **R1 呼数不変**: `generate()`(LLM呼)を1本も足さない。LLM は既存の発火(buy/routine/open_venture)のみ。
4. **配置**: 商業/物流ロジックは `src/society` 直下(commerce.py の隣)=engine/cognition/world の
   **no-fingerprint 契約に触れない**。grievance は factors 層 hook(既存 `on_scarcity` 等)へ **不透明 magnitude** を
   渡すのみ(発火系 drive には接続しない)。
5. **k 不変性**: 在庫枯渇=購入可否の変化、補充/配送=新しい移動体、はいずれも co-location を変えうる
   (FixedLLM で ON≠OFF)。これは commerce.filter_open・career・crowd と **同型の既知の性質**。判定に
   **在庫量・時刻・config・在館数(観測量)のみ** を使い、**k・内面状態を食わせない** ことで compute_matched の
   k 不変性(k=free==k=off の呼数一致)を守る(§10 で検収項目を明示)。

**新イベント種の候補**(schema.py に1行ずつ登録。既存と衝突しない新 kind):
`restock`(補充到着)・`deliver`(配送トリップ)・`stock_low`(在庫僅少)・`b2b_trade`(卸→小売の取引)・
`service_use`(サービス受給:滞在+効果)・`reservation`(予約)。
※ `stock_out`(品切れ)は commerce の既存 kind を **意味を「実在庫の枯渇」に拡張して再利用**(混雑代理から
実在庫へ格上げ)。

---

## 7. 設計提案 — 最小実行可能スライス(①〜⑤)

各スライスに **機構 / 対象ファイル見込み / 工数 / R1整合 / 計測(events) / 機械層でどこまで / エージェント体験
(prompt・digest)/ 観測に残るもの** を明記する。

### ① 店舗在庫 + 日次補充(物流トリップ)  ★土台・最優先

- **機構**: 各 shop/food POI(または venture)に **在庫 `stock`** を持たせる。購入(`_charge_meal`/
  `_buy_at_ventures`/#7 buy)で在庫を **1単位減らす**。在庫が下限 s を割ったら **(s,S) で補充発注** →
  リードタイム後に **補充トリップ(depot→店)が到着して在庫を S へ戻す**(`restock`)。在庫0で購入不可=
  **実在庫由来の `stock_out`**(現状の混雑代理を実在庫へ格上げ)。補充頻度は §3.4 で較正(生鮮=日3回・
  日用=日1回)。
- **対象ファイル**: `commerce.py`(在庫状態・(s,S)・補充ロジック=stock_out の枠を実在庫に格上げ)/
  `scheduler.py`(`_charge_meal`/`_buy_at_ventures` の購入点で在庫decrement+新 `_phase_restock` 日次フェーズ・
  補充トリップの traffic 接続)/ `economy.py` or `commerce.py`(conf `commerce.inventory`)/ `schema.py`
  (`restock`/`stock_low`)/ `tests/test_commerce.py`。
- **工数**: 約2バッチ(2〜3人日)。commerce.py に既に stock_out/occupancy の枠があるので純増は在庫状態と
  補充フェーズ+トリップ配線。
- **R1整合**: LLM呼 0 追加。在庫decrement・(s,S)判定・補充到着は決定論。補充トリップの経路生成に乱数が
  要れば新 stream `("restock", poi_id, step)`。品切れ→購入抑制は commerce.on_purchase の既存分岐を実在庫に
  差し替えるだけ(grievance は既存 `on_scarcity` hook 経由=不透明 magnitude)。**k注意**: 補充トリップ=
  新移動体・品切れ=購入可否変化 → §10 検収。判定は在庫量・時刻・config のみ(k非依存)。
- **計測(events)**: `restock`{poi, qty, from_depot}、`stock_low`{poi, level}、`stock_out`{poi, cat}(実在庫版)。
  → **物の移動が可視化**され、災害時に補充トリップが止まる/在庫が枯れる系列を追える。
- **機械層でどこまで**: **全部**(在庫・(s,S)・補充・品切れ・配送トリップ)。LLM 不要。
- **体験(prompt/digest)**: 品切れに遭遇した買い手のプロンプト文脈/記憶に「◯◯が品切れで買えなかった」
  (既存 `agent.remember` を実在庫理由に)。補充が滞る災害時は「棚がスカスカだ」的な街の文脈。
- **観測に残るもの**: 在庫時系列・補充トリップ数・品切れ率・(災害時)物流断絶による在庫枯渇曲線。

### ② 商品実体を spend に載せる(何を買ったか)  ★①に同梱可・低コスト

- **機構**: 消費カテゴリを **具体商品** へ解像度を上げる。`_spend`/venture の payload に **`item`(買った品:
  例「コーヒー」「Tシャツ」)** を載せる。商品リストは POI カテゴリ・org の `products_services`(既存の自由文字列
  資産!例「勤怠管理SaaS」)・venture の `offer` から **決定論で選ぶ**(日替わり巡回=organizations.daily_output と
  同型)。家計調査の費目(既存 economy-abm-research.md §5 の budget_shares)と整合。
- **対象ファイル**: `scheduler.py:496` `_spend`(payload に item)/ `commerce.py` or `organizations.py`
  (商品カタログの決定論選択)/ `schema.py`(spend の payload 拡張=新 kind 不要)。
- **工数**: 約0.5バッチ(①と同時が効率的)。会計不変(金額は変えない)。
- **R1整合**: LLM呼 0 追加・乱数 0(決定論の巡回選択)。**OFF時 payload 不変=バイト一致**。co-location も
  移動も変えない=k完全中立(最も安全)。
- **計測(events)**: `spend`{…, item}、`venture_sale`{…, item}。商品別売上・人気商品が集計可能に。
- **機械層でどこまで**: 全部(カタログ選択は決定論)。
- **体験(prompt/digest)**: 「◯◯で△△を買った」が記憶に残る(現状の定型文が具体化)。店主側は「△△が
  売れた」。→ 会話・反省の素材が具体化する(造語観察 `natural-coinage` の文脈も豊かに)。
- **観測に残るもの**: 商品別の売上分布・カテゴリ内訳(家計調査との整合検証に使える)。

### ③ サービスの実体(滞在 + 効果 + 予約)  ★service POI 1,994件を起こす

- **機構**: **理容/クリニック/塾/ジム/クリーニング等**(cat=`service`/`education`)で **「滞在して効果を受ける」**
  最小形。①予約(任意)→②来店・**滞在**(既存の在館/滞在機構)→③**課金(`_spend`)**→④**効果**(内部
  transient を少量更新:散髪=気分/外見・ジム=疲労回復や健康・塾=学習/効力感の素地)。**医療は既存
  `medical_visit` と整合**(病気起点の受診はそのまま、健康維持の任意受診をサービスとして追加)。
- **並行バッチとの seam**: 別エージェントの `serve`(接客の **提供側**=L2従業者の業務実体)が **供給** を、本
  スライスの `service_use` が **需要側の受給体験(滞在+効果+課金)** を担う。**同一のサービス接点で
  提供側=serve / 受給側=service_use が対** になる設計(重複せず接続)。予約 `reservation` は両者が参照。
- **対象ファイル**: 新 `src/society/services.py`(サービス定義・効果テーブル・予約=commerce/health と同型の
  直下モジュール)/ `scheduler.py`(サービス受給フェーズ or 到着hook・`_spend` 課金)/ `factors/update.py`
  (効果 hook=既存 on_work_done/on_scarcity と同型の不透明 magnitude)/ `schema.py`(`service_use`/
  `reservation`)/ `economy.py`(service 価格:既存 prices に理容/ジム/塾を追加)。
- **工数**: 約1.5バッチ(効果テーブルと予約の設計が要る)。
- **R1整合**: LLM呼 0 追加。サービス選択は既存の routine/#7 buy の発火に相乗り(新 generate なし)。効果は
  factors hook へ不透明 magnitude(発火系 drive には接続しない)。予約・課金・効果は決定論(乱数要れば新
  stream `("service", id, step)`)。**k注意**: サービスのための来店=移動先が変わる(co-location変化)=①と同型。
  判定は物理位置・時刻・config のみ。
- **計測(events)**: `reservation`{node, service, when}、`service_use`{node, service, cost, effect?}。
- **機械層でどこまで**: 課金・効果・予約は全部機械層。**「行くかどうか」だけ既存 LLM 発火**(新規呼び出し無し)。
- **体験(prompt/digest)**: 「髪を切って気分が上がった」「ジムで汗を流した」「塾で勉強した」等が記憶・
  プロンプト文脈に乗る。予約があれば「明日15時に美容室」(既存 appointment 機構と接続可)。
- **観測に残るもの**: サービス利用率・費目別支出(家計調査の保健医療/教養娯楽と整合)・効果の分布。

### ④ 宅配・フードデリバリー(配達員=業務接続)  ★①③依存・後段

- **機構**: 買い手が来店せず **注文**(在宅/職場)→ **配達員(L5来街者 or L2従業者=配達 gig)** が店で品を
  受取り(在庫decrement)→ **配送トリップ(店→注文者)** → 到着で受給+課金。§3.3 のラストマイルABM 構造
  (注文生成→トリップ→到着)をそのまま踏襲。配達員は既存の gig(配達員職=economy.py の「自営」)に
  **業務実体** を与える。
- **対象ファイル**: 新 `src/society/delivery.py`(注文・配車・トリップ)/ `scheduler.py`(注文生成フェーズ・
  配送トリップの traffic 接続・到着課金)/ 既存 `commerce.py` 在庫(①)を参照 / `schema.py`(`deliver`/`order`)/
  `world/traffic.py`(貨物トリップ)。
- **工数**: 約2バッチ(注文生成+配車+トリップ+到着の4段)。①(在庫)③(サービス化)が前提。
- **R1整合**: LLM呼 0 追加。注文生成は「在宅で空腹」等の観測量から決定論 or 新 stream `("order", id, step)`。
  配車・経路は決定論(最寄り配達員)。**k注意**: 配達員トリップ=新移動体=①補充トリップと同型。
- **計測(events)**: `order`{from, to_home}、`deliver`{courier, from_poi, to, item, fare}。
- **機械層でどこまで**: 注文発火は既存 routine/buy に相乗り、配車・トリップ・課金は全部機械層。
- **体験(prompt/digest)**: 「Uber的に頼んだ弁当が届いた」/ 配達員側「配達で稼いだ」(gig 収入に実体)。
- **観測に残るもの**: 配達トリップ数・配達員稼働・宅配比率(コロナ後の現実トレンドの再現)。

### ⑤ 会社間取引 B2B(卸→小売の仕入れ)  ★①依存・org創発に効く

- **機構**: ①の補充を **外生 depot からの供給** ではなく **org 間取引** に内生化する。卸/製造 org(既存
  organizations の `output_kinds`=素材/製品を持つ org)が **生産**(既存 `production` に在庫増を接続)→
  小売 POI/venture が在庫補充時に **卸から仕入れ**(org間で **金+物** が移転)。§5.1 EVE の「入力→出力の
  物質収支」を1段だけ写す。
- **対象ファイル**: `organizations.py`(生産→在庫・卸の出荷)/ `commerce.py`(小売の仕入=①補充の供給元を
  org に差替)/ `scheduler.py:388` `org_ledger`(取引の集計)/ `schema.py`(`b2b_trade`)/ 新 stream。
- **工数**: 約1.5バッチ(①の補充供給元を「depot」から「卸org」へ差し替える増分)。
- **R1整合**: LLM呼 0 追加。生産量・仕入・清算は決定論。org間の金は既存会計(org_ledger/wage と同じ流儀)。
  **k注意**: B2B トリップを物流化するなら④と同型(しなければ会計のみ=k中立)。
- **計測(events)**: `b2b_trade`{from_org, to_poi, item, qty, amount}、`production`(在庫増を追記)。
- **機械層でどこまで**: 全部。**組織の自然形成/ファウンダー成立**(MEMORY: org-emergence-goal)に効く=
  「卸が小売を支える供給網」が局所ルールから立ち上がる(nature-like)。
- **体験(prompt/digest)**: 直接は薄い(B2B は裏方)。ただし「仕入れが途絶えて店が回らない」等が店主体験に。
- **観測に残るもの**: 供給網グラフ(誰が誰に卸すか)・災害時の川上断絶の伝播(§3.1 の bankruptcy avalanche に
  接続=既存 economy-abm-research.md §1 の与信雪崩と合流)。

---

## 8. 優先順位の推奨(3軸で採点)

採点軸: **A=現実渋谷の再現** / **B=災害時の物流断絶の表現力** / **C=k\*研究への寄与** / D=工数(低いほど良)。

| 順 | スライス | A 現実再現 | B 物流断絶 | C k\*寄与 | D 工数 | 総評 |
|:--:|---|:--:|:--:|:--:|:--:|---|
| **1** | **① 在庫+補充(物流)** | ◎ | ◎ | ◎ | 中 | **全ての土台**。これ単独で「物の移動」と災害物流断絶が成立。最優先 |
| **2** | **② 商品実体** | ○ | – | ○ | 低 | ①に同梱。ほぼ無料で体験・観測・会話素材が具体化 |
| **3** | **③ サービス実体** | ◎ | ○ | ○ | 中 | service POI 1,994件を起こす=渋谷再現の解像度が跳ね上がる。並行 serve と対 |
| **4** | **⑤ B2B 卸→小売** | ○ | ◎ | ◎ | 中 | ①の供給元を org に内生化。**組織創発・供給網雪崩**に直結(研究目標に合致) |
| **5** | **④ 宅配/デリバリー** | ○ | ○ | △ | 高 | ①③依存。gig に業務実体・SUMO 接続。優先度は後段 |

**推奨実装順: ①(+②同梱) → ③ → ⑤ → ④。**

**根拠**:
- **①が唯一の必須土台**。在庫が無ければ補充も B2B も宅配も「物」が無く成立しない。かつ ① 単独で
  ユーザー要望の中核(「物の移動」)と、**災害時物流断絶の表現力**(disaster が補充トリップを止める→実在庫が
  枯れる→品切れ→パニック買い→grievance の連鎖。§3 の supply-disruption/panic-buying ABM の知見をそのまま
  適用)と、**k\* 研究への寄与**(物理的な財ネットワークを伝播する外生ショック=既存の情報/意見カスケードとは
  別種の伝播路)を同時に立てる。
- **②は①に同梱**が最も費用対効果が高い(会計不変・k完全中立・体験と観測が具体化)。
- **③は現実渋谷の再現に最も効く**(1,994件の service POI が経済的に眠っている)。並行 serve バッチと **需要=
  service_use / 供給=serve** の対で組めるため、タイミングを合わせる価値がある。
- **⑤は研究目標(組織の自然形成・ファウンダー成立・供給網の創発)に直結**。①の後なら増分実装で済む。
- **④は最後**(①③の在庫・サービスが揃ってから。工数も最大)。

---

## 9. 未確認事項(事実と推測の区別)

**一次/二次で確認済みの事実**:
- 現状コードに在庫・補充・物流・B2B・宅配の実装が無いこと(§2 の file:line は本リポジトリ実査で確認)。
- service POI 1,994件・education/school 263件が地図データに存在すること(`data/*.json` を grep で計数)。
- (s,S) 方策の定義・軽量性、供給網ABM の3〜4層構成、ラストマイルABM の構造(§3)。
- 7-Eleven Japan の多頻度小口配送(1日3回超)と 2025 の配送回数削減(§3.4)。
- LLM社会シムが経済を金銭移転に抽象化する傾向(§4.1)、EVE の生産チェーン・財の物理性・地域市場(§5.1)。

**推測 / 未確認(実装前に要検証)**:
- 数千 POI に per-tick 在庫decrement を載せた際の **実測計算コスト**。理論上 O(1)/POI で軽いはず(§3.2)だが、
  本シムの 200-300体・1step=10分・100日ランでの実測は未取得(mock で smoke 検証が必要=MEMORY
  `validation-runs-short`)。
- **MMO×生成ABM 論文(arXiv 2506.04699)の実装値**(agent数・計算コスト・LLM/ルール分担の詳細)は
  PDF 本文が静的取得不可のため **題目・キーワード・要旨レベルでの確認に留まる**(実数は未確認)。
- **EVE Manufacturing 公式ページ**は 403 で直接取得できず、生産チェーン・地域市場・財の物理性は **二次情報で
  確認**(一次の細目=素材消費係数等は未確認。本シムには不要な粒度)。
- サービス効果(散髪→気分・ジム→健康 等)の **magnitude 較正値** は未調査(実装時に既存 factors の
  magnitude 体系に合わせて決める=別途)。
- 並行 serve バッチの **正確な設計(イベント payload・接点)** は未確認。③の seam は「対で組む」方針の提示に
  留め、実装時にすり合わせが必要。

---

## 10. R1 論点(実装着手時の検収項目)

全スライス共通で、**pre-coding-alignment**(決定アジェンダ提示→合意)と **ask-before-extending** に従うこと
(MEMORY)。実装時の R1/k 検収:

1. **呼数不変(R1)**: 全機構が `generate()` を1本も足さないこと。在庫・(s,S)・補充・配送・B2B・サービス効果は
   非LLM。LLM は既存の buy/routine/open_venture の発火のみ。→ **OFF/ON とも LLM 呼数が baseline と一致** を
   pytest で確認。
2. **OFF時バイト一致**: 各 config 既定 `enabled:false` で新イベント0件・新 stream を引かない=ゴールデン
   `golden_baseline_l1.json` と **バイト一致**(commerce/career/health/disaster と同じ検収)。
3. **k 不変性(compute_matched)**: ①補充トリップ・④配達トリップ=**新しい移動体**、①③品切れ/サービス来店=
   **co-location の変化** は FixedLLM で ON≠OFF になりうる(commerce.filter_open/career/crowd と同型)。
   **k=free と k=off で LLM 呼数が一致** することを検収(判定に在庫量・時刻・config・在館数=観測量のみを
   使い、efficacy/grievance 等の **内面構成概念・k を発火判断に食わせない**)。
4. **no-fingerprint(R9)**: 商業/物流/サービスのロジックは `src/society` 直下(engine/cognition/world の
   CHECKED_DIRS 外)に閉じる。grievance は factors 層 hook(既存 `on_scarcity` 等)へ **不透明 magnitude** のみ
   渡し、発火系 drive には接続しない。
5. **会計保存**: ②商品実体・決済は金額を変えない(買い手支出=売り手売上)。⑤B2B・④宅配の金移転は既存の
   org_ledger/wage/spend と同じ流儀で二重計上を避ける。
6. **既存 kind 衝突回避**: 新 kind(`restock`/`deliver`/`b2b_trade`/`service_use`/`reservation`/`order`/`stock_low`)は
   既存と非衝突を確認(既存 economy-abm-research.md §7【要注意 A】の `deposit` 衝突のような轍を踏まない)。
   `stock_out` は commerce 既存 kind の意味拡張(混雑代理→実在庫)として再利用。

---

## 11. 参照(本リポジトリ内)

- 金の回路(銀行/VC/消費構造/決済)の先行調査: [`economy-abm-research.md`](economy-abm-research.md)
- 既存の商業ダイナミクス(営業時間・在館数・stock_out の枠): `src/society/commerce.py`
- 消費/賃金/口座/価格: `src/society/economy.py`、金の流れの配線: `src/society/engine/scheduler.py`
- 起業(venture): `src/society/tools.py`、組織/生産: `src/society/organizations.py`
- 災害/物流断絶フック: `src/society/disaster.py`、交通/SUMO: `src/society/world/traffic.py`
- 観察目標(組織の自然形成・ファウンダー成立): MEMORY `org-emergence-goal` / nature-like-systems /
  realism-first-scale
