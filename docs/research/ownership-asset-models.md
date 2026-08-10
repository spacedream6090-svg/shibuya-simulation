# 所有・資産モデル — 「所有されるもの」を世界の第一級オブジェクトにするための実装前リサーチ

> 作成 2026-08-10 / 対象 = ユーザー構想「エージェントの所有物が活動によって流通し、所有権が移り変わる状態」
> 前提の実測 = `src/society/lost_property.py`(第107)・`src/society/economy_sfc.py`(IF-E2)・`src/society/goods.py` / `b2b.py` / `delivery.py`(物流①〜⑤)・`src/society/tools.py`(venture)ほか本文中の各ファイル
> 既存の関連リサーチ = `docs/research/economy-goods-services.md`(物流・商品実体)/ `docs/research/ifE2-org-accounting-research.md`(貨幣保存・RoW)/ `docs/research/economy-abm-research.md` / `docs/research/agent-lod-deepdive.md`(LoD)
> **本書は設計候補の提示までで、実装・コミットは含まない。**
> 表記規約: 【実測】= このリポジトリのコード・データから直接確認 / 【一次】= 論文・公式文書・制度で確認 / 【推定】= 本書の推論。

---

## §0. 3行サマリ

1. **ユーザーの「物にタグ」案は意味論として正しく、本リポには既に3つの実働先行例がある**【実測】: `lost_property` の遺失物レコード(owner/finder 属性+状態機械+移転+貨幣保存の hold バケツ)、`tools.py` の venture(owner タグ+permitted=許認可)、`observer/provenance.py` の ItemStore(情報オブジェクトの出所台帳)。いずれも「**レコード自体は owner タグを持ち、格納は中央 dict+索引**」= タグ案(object-centric)と登記簿案(registry-centric)は対立せず**同じものの2つの面**である。現実の制度(Torrens 登記・日本の動産/債権譲渡登記・ISO 19152 LADM)も全て「中央台帳に (資産, 主体, 権利種別, 期間) の行を置く」形で、これが観測・保存則検査・checkpoint 中央管理(本リポの既存流儀)と最も整合する。
2. **「資産保存則」は貨幣保存則(IF-E)の完全な双対として設計できる**【一次+実測】: SNA 2008 は資産の増減を「取引(売買・贈与)/境界フロー(生産・輸出入)/その他資産変動 K.5(滅失・盗難)」に三分しており、本リポは貨幣側で既に同じ三分(部門間移転 / RoW / K5)を実装済み。物の側も「資産は製造・輸入(RoW)からのみ生まれ、廃棄・滅失(K5)でのみ消え、それ以外は所有者間の移転のみ」という閉じた不変量が立つ。物理側の保存則を持つ SFC モデル(stock-flow-fund)が学術的前例。
3. **25万×家財数十点=数百万レコードは「全個体 dict」では成立しない**【推定・裏付けあり】。答えは階層 LoD: **不動産・事業資産・車両=全個体**(万の桁=登記簿レコード)/ **家電・家財=世帯単位のカテゴリ集計+イベント時だけ代表個体に実体化**(lost_property・goods の遅延実体化の既存流儀)/ **消耗品=フローのみ**(現行 spend のまま)。これは MATSim の「目的に必要な粒度まで削る」哲学と ECS/SoA(`engine/soa.py` の移行契約)に整合する。

---

## §1. 構想の定式化(ユーザー原文)

> 「エージェントが所有しているものもエージェントの活動によって流通したり、所有権が移り変わるような状態にしたい。一部の例として、不動産であったり家電など実存するものや、権利などの目に見えないものがそれらに当てはまると思うし、その概念をシミュレーションに組み込みたいと思っている。個人の所有のものと企業であったりの組織が所有するものなどあるけど、範囲内に存在するあらゆるものを実装できればしたいと思っている。僕の考えでは所有されているもの自体にタグをつけて観察、管理をするような方式でいいかなって思っているんだけどどう?」

要件に分解すると:

| # | 要件 | 本書の対応節 |
|---|------|------------|
| R-a | 所有物が**流通**する(活動による移転) | §3-4(移転語彙)・§4 |
| R-b | 対象は**実物**(不動産・家電)と**無形**(権利) | §3-2(制度)・§3-3(権利) |
| R-c | 所有主体は**個人と組織**の両方 | §2(org 台帳・venture が既に主体)・§4 |
| R-d | **範囲内のあらゆるもの**をできれば全部 | §6(規模と LoD = 「全部」の実装可能な形) |
| R-e | 方式は「**物にタグをつけて観察・管理**」 | §4・§5(正面から評価) |

補助線として、ユーザー世界観(MEMORY: nature-like-systems = ボトムアップ創発第一・natural-coinage = 観察装置であって促進しない)から、この層も「**所有の動きを観察する装置**」であって「エージェントに売買を勧める機構」ではない、という R1 的な線引きが導かれる【推定】。

---

## §2. リポ内の「所有」の現状棚卸し【実測】

### §2-1. 金銭(最も成熟。保存則・検査・部門会計まで完備)

| 実装 | 場所 | 内容 |
|------|------|------|
| 現金・口座 | `src/society/agents/agent.py:75-84` | `money`(現金)・`account`(口座 E5)・`rent_due`(家賃未払い)。属性=エージェント側タグ |
| 会計主体 | `src/society/economy.py` / `government.py` / `commerce.py:314-347` | Government(ward/metro 予算)・Bank(融資)・VCFund。**VCFund.equity = `dict[owner_id → 持分]` は無形資産(持分)の最初の実働例** |
| org 預金+RoW+K5 | `src/society/economy_sfc.py`(IF-E2) | org にスカラー預金 1 本。受け手不在の金は RoW(渋谷域外)へ**チャネル別**に、窃盗など非取引は K5 へ。**閉じた不変量「Σ(全主体残高)+RoW 累積+K5 累積=一定」をテストで固定** |
| 貨幣保存検査 | `scripts/analyze_accounting.py` + `tests/test_accounting.py` | Caiani 流の①部門別貨幣保存②フロー行列ゼロ和。未分類の金経路を検知する監視装置つき |

### §2-2. 住居(居住権の状態機械は実質既にあるが、「所有者」が世界に居ない)

| 実装 | 場所 | 内容 |
|------|------|------|
| 住まい | `agent.py:48-50` | `home_node` / `home_building` / `home_floor` = **人が住戸を指す片方向タグ**。住戸側に居住者名簿はなく、建物はただの地物(所有者不在) |
| 転居 | `src/society/mobility.py`・`freedom_p2.py:84`・`engine/scheduler.py:3805-3834` | 空き住戸=「**他エージェントの home でない** residential 建物」を決定論選定。= 登記簿が無いので「空き」の判定は全 agent の home の否定条件でしか書けない(登記簿不在の実費)。敷金は現金障壁、**敷金の受け手=不在家主として RoW へ**(`scheduler.py:3834`) |
| 滞納・立退き | `agent.py:163-165` | `arrears_days` / `evicted` / `bankrupt_until` = **賃借権の得喪の状態機械が暗黙に実装済み**(権利オブジェクトとして名指しされていないだけ) |
| ホテル泊 | `src/society/lodging.py` | `lodging_*` 属性(チェックイン=一時的な滞在権) |
| 入院 | `src/society/medical.py`(第107) | `hospital_admit` = 在院という状態+会計。病床という資源の占有 |

### §2-3. 職場・組織(組織は既に「所有主体」の器を持つ)

| 実装 | 場所 | 内容 |
|------|------|------|
| org 台帳 | `src/society/organizations.py` + `data/organizations_shibuya*.json` | 架空 org の中央台帳(wide11k = **11,010 社**)+決定論配属。org_ledger(revenue/wage の集計)→ IF-E2 で預金主体化 |
| venture | `src/society/tools.py:496,884-891` | `{owner, node, name, offer, price, permitted, sales_total, …}` = **owner タグ付き事業オブジェクト**+`ventures_by_node` 索引。`permitted: false` は警官が摘発(`scheduler._enforce_ventures`)= **許認可(無形の権利)の最初の実働例** |
| グループ | `tools.groups` / `member_of` | group_found による集団。所属=関係の台帳 |

### §2-4. 物品(先行例は揃っているが、**買った物は消える**)

| 実装 | 場所 | 内容 |
|------|------|------|
| **遺失物** | `src/society/lost_property.py:437-451,668-695` | `st["items"][iid] = {id, item, owner, node, x, y, loc, building, floor, cash, step, status, noticed, finder, turn_step}` = **本リポで最も完全な「資産レコード」**。owner タグ+位置+状態機械(遺失→拾得→届出→返還/着服/時効取得)+**所有権移転**(owner→finder・報労金 5-20%=遺失物法 28 条・3 か月時効=同 7 条)+**hold バケツ**(誰の残高でもない現金=貨幣保存の第 3 項)。格納は `sim._lost_state` の中央 dict、checkpoint は runtime 中央管理 |
| 店舗在庫 | `src/society/goods.py` | POI(node×cat)別の実在庫+(s,S) 補充+配送トリップ。**遅延実体化**(購入が起きた POI だけ在庫が実体化=有界)。商品実体は spend payload の `item` +「直近購入の有界リスト」= **買った物は記録には残るが資産としては消える**(耐久財・中古・廃棄の概念なし) |
| org 在庫・B2B | `src/society/b2b.py` | 卸 org の在庫と `b2b_trade` = **org 間で金+物が同時に移転**する唯一の実装(買い側支出=売り側売上の保存流儀) |
| 配送 | `src/society/delivery.py` | 注文→配達員→配送→受給+課金(物の物理移動) |
| 情報オブジェクト | `src/society/observer/provenance.py:16-46` | `Item {item_id, kind, text, creator, born_step, transmissions}` + ItemStore = **無形物の出所・伝播台帳**(rumors IF-C が使用)。「作られたものに id を振り移動履歴を刻む」ひな型 |
| 耐久財タグ | `agent.py:37-38` | `has_bicycle` / `has_car` = **最古の所有表現(bool タグ)**。移転・売買・個体性なし |

### §2-5. 権利・土地・相続(不在の部分)

- **土地・建物の所有者は世界に居ない**: 建物は地物、家賃・敷金の受け手は RoW の「不在家主」。
- **免許・許認可の一般機構は無い**(venture の `permitted` bool が唯一)。
- **相続は存在しない**【実測】: `health.py:1118` で `dead=True` になるだけで、死者の `money` はエージェントオブジェクトに凍結されたまま。Σ 不変量上は「死者の財布」という暗黙部門が生まれている(会計上は漏れではないが、観測上は流通から消える)。
- **関連規律**: R1(既定 OFF・golden L1 バイト一致・OFF ではキー自体を作らない・LLM 呼数不変)/ traces(場所履歴)/ causality(devices の因果刻印)/ registry.py(conf 宣言)/ `engine/soa.py`(SoA 移行契約: array=truth・世代付き ID・counter-based RNG)。

**棚卸しの結論**: 「金は完全・住居は権利の状態機械だけある・組織は主体の器がある・物は事件(遺失)と在庫(店)だけ実体があり家財が無い・権利は venture の bool 1 個・土地所有者と相続が空白」。つまり**ゼロから作る話ではなく、lost_property が事件のために作った資産レコードを、平時の所有一般へ昇格させる話**である【実測に基づく推定】。

---

## §3. 文献・制度の発見(番号付き・URL)

### §3-1. ABM・計算経済学の資産モデル

1. **英国住宅市場 ABM(中央銀行の実務モデル)**【一次】 — Baptista, Farmer, Hinterschweiger, Low, Tang, Uluc (2016) "Macroprudential Policy in an Agent-Based Model of the UK Housing Market", Bank of England SWP 619。first-time buyer / 持ち家 / **buy-to-let 投資家** / 賃借人の 4 役が売買・賃貸市場で相互作用し、住宅は**個体**(価格・質・抵当つき)として保有される。buy-to-let(投資目的の所有)が価格循環を増幅するという結果は「誰が所有しているか」を個体で持つからこそ出る観測。
   https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2850414 (行動版の公開実装解説: https://www.jasss.org/27/4/5.html)
2. **ワシントン DC 住宅市場 ABM**【一次】 — Geanakoplos, Axtell, Farmer, Howitt et al. (2012) "Getting at Systemic Risk via an Agent-Based Model of the Housing Market", AER 102(3)。全世帯・全住宅を個票データから 1:1 で再現(=「現実スナップショットが舞台」という本プロジェクトの DT 定義と同型)。バブルの主因は金利でなくレバレッジと示した。
   https://www.aeaweb.org/articles?id=10.1257/aer.102.3.53
3. **AB-SFC ベンチマーク**【一次】 — Caiani et al. (2016)。既に IF-E の正典。資本財(耐久・減耗つき)も貸借対照表の行として持ち、**実物資産の増減も取引フロー行列で検査される**= 資産版ゼロ和検査の直接の手本。
   https://www.sciencedirect.com/science/article/abs/pii/S0165188915301020
4. **EURACE(大規模 AB-SFC)**【一次】 — 貸借対照表アプローチで stock-flow 整合を検証。資本財企業・耐久消費財を含む多部門。「balance sheet = 事後の検査装置」という本リポ IF-E と同じ思想の大規模前例。
   https://link.springer.com/chapter/10.1007/978-3-642-14746-3_74 / https://www.sciencedirect.com/science/article/abs/pii/S0096300308003019
5. **Sugarscape(富の分布と相続の古典)**【一次】 — Epstein & Axtell (1996)。資源ストックの保有+相続ルールだけで Lorenz 曲線・Gini の実測的な富分布が創発。**相続の有無を切り替えて格差への効果を観察する**という、本層が可能にする観測の原型。
   https://jasss.soc.surrey.ac.uk/12/1/6/appendixB/EpsteinAxtell1996.html (実装例: https://modelingcommons.org/browse/one_model/2758)
6. **世代重複+地域相互作用+世代間移転の富格差 ABM**【一次】 — 相続・近隣効果が長期の富分布を決めるという系譜(RAND のワーキングペーパー含む)。
   https://www.researchgate.net/publication/341290690_An_Agent-Based_Model_of_Wealth_Inequality_with_Overlapping_Generations_Local_Interactions_and_Intergenerational_Transfers / https://www.rand.org/pubs/working_papers/WRA1259-8.html / https://www.sciencedirect.com/science/article/pii/S0167268122000580
7. **耐久財・中古市場の ABM**【一次】 — 家電の買い替えは「寿命分布(三角分布等)+故障時に購入」で世帯単位にモデル化するのが通例。中古(リユース)市場 ABM は消費者・製造者・回収業者・中古小売の 4 主体で二次流通を作る。**家電を全個体で持たず「世帯×カテゴリ+寿命」で持つ前例**。
   https://link.springer.com/article/10.1007/s11573-021-01046-9 / https://doi.org/10.3390/su17156885 / https://www.sciencedirect.com/science/article/abs/pii/S0959652619305177

### §3-2. 所有権の表現方式(制度・工学の設計)

8. **ISO 19152 LADM(土地行政ドメインモデル)**【一次】 — 所有表現の国際標準。中核は 3 クラス: **Party(人・組織)— RRR(Rights / Restrictions / Responsibilities)— BAUnit/SpatialUnit(資産)**。所有は「Party と資産の間の **RRR オブジェクト**」であり、資産の属性でも Party の属性でもない。権利・制限・責務が同格の第一級オブジェクトである点が bundle of rights(§3-3)の実装形。Part 2 (2025) は登記そのもの。
   https://www.iso.org/standard/81263.html / https://www.iso.org/standard/81264.html / 解説論文: https://www.sciencedirect.com/science/article/pii/S0264837715000174
9. **Torrens 登記(title by registration)**【一次】 — 「登記簿への記載が所有権を**構成**する」方式。mirror principle(登記簿は現在の権利関係を完全に映す)・curtain principle(過去の証書を遡らなくてよい=現在状態だけで完結)・indefeasibility(登記の確定力)。**シミュレーション実装に直訳すると「台帳が唯一の真実(single source of truth)で、履歴はイベントログ側にある」**= 本リポの「状態は台帳・履歴は L1」と同型。
   https://en.wikipedia.org/wiki/Torrens_title
10. **日本の登記制度(不動産登記・動産譲渡登記・債権譲渡登記)**【一次】 — 日本法は Torrens と違い登記は**対抗要件**(権利の成立は意思表示で、登記は第三者に対する優劣を決める)。動産譲渡登記は「登記=引渡しの擬制」、**二重譲渡の優劣は登記の先後で決まる**。債権(=無形資産)も同じ枠組みで登記できる。= 「所有権の移転イベント」と「それを世界に公示する記録」が別レイヤであるという設計の教材。ただしシム内では紛争解決を作らない限り、この二層は 1 層(台帳=真実)に潰してよい【推定】。
    https://www.moj.go.jp/MINJI/DOUSANTOUKI/seido.html / https://www.moj.go.jp/MINJI/saikenjouto-01.html
11. **BODS(実質的支配者データ標準)**【一次】 — 企業の所有・支配を **ownership-or-control statement**(主体ステートメントと客体ステートメントを結ぶ**エッジオブジェクト**、持分率・直接/間接・出典・時点つき)で表現する公開スキーマ。**関係エッジ方式 (c) の最も洗練された実例**であり、「所有=属性ではなくメタデータ付きの主張(statement)」という見方を与える。
    https://standard.openownership.org/en/0.3.0/schema/concepts.html
12. **IFC / BIM の所有メタデータ(IfcOwnerHistory)+ COBie**【一次】 — 建物のデジタルツイン標準では、全オブジェクトが `IfcOwnerHistory`(作成者・所有アプリ・変更履歴)を**オブジェクト自身に**持つ。ただし IFC2x3 で必須だったこの「物にタグ」方式は **IFC4 で任意化され、次世代では廃止が提案されている**(全オブジェクトへの重複貼付が肥大と不整合を生んだ)。= **object-centric タグの実運用上の弱点が標準化コミュニティで実証された**事例。COBie は竣工時の資産台帳(スプレッドシート=registry 形式)。
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcOwnerHistory.htm / https://github.com/buildingSMART/NextGen-IFC/issues/16 / https://en.wikipedia.org/wiki/COBie
13. **ECS(entity-component-system)**【一次】 — ゲーム/シミュレーション工学の標準。entity は**ただの id**、データは component(列指向 SoA)、所有のような関係は「entity 間 relationship」または owner_id component で表す。archetype 型 ECS は数百万 entity を毎フレーム処理できる。本リポ `engine/soa.py` は既に同系(世代付き ID・array=truth)【実測】。
    https://github.com/SanderMertens/ecs-faq / https://ajmmertens.medium.com/flecs-4-1-is-out-fab4f32e36f6

### §3-3. 権利=無形資産のモデル化

14. **SNA 2008「契約・リース・免許」= 無形の非生産資産**【一次】 — 国民経済計算(本リポが RoW/K5 で既に採用している体系)は、**マーケタブルな営業リース・資源利用許可・特定活動の許可(タクシー免許等)・のれん**を資産分類 AN.22(contracts, leases and licences)として貸借対照表に計上する。条件は「契約価格が市場価格と乖離し、その差が譲渡可能な価値を持つこと」。= **権利を「所有オブジェクト」として扱う会計標準が既にあり、貨幣・K5 と同じ語彙体系で拡張できる**。
    https://unstats.un.org/unsd/statcom/doc08/BG-SNA-Chapter13.pdf / https://ec.europa.eu/eurostat/esa2010/chapter/view/15/ / https://www.abs.gov.au/statistics/detailed-methodology-information/concepts-sources-methods/australian-system-national-accounts-concepts-sources-and-methods/2020-21/chapter-17-balance-sheet/non-financial-non-produced-assets
15. **Bundle of rights(権利の束)理論**【一次】 — 所有権は単一の関係ではなく、Honoré の 11 の incidents(占有・使用・管理・収益・資本・保全・譲渡可能性・無期限性・有害使用の禁止・強制執行への服属・残余性)に分解できる束。**「lease = 使用+収益の stick だけが移転し、資本の stick は家主に残る」のように、移転を stick の部分集合の付け替えとして統一的に書ける**。LADM の RRR はこの計算表現である。
    https://lawreview.vermontlaw.edu/wp-content/uploads/2012/02/johnson2.pdf / https://iep.utm.edu/prop-con/

### §3-4. 移転イベントの語彙と「資産保存則」

16. **SNA の資産変動の三分法**【一次】 — 資産の増減は (i) **取引**(売買・贈与=相互合意)、(ii) **境界フロー**(生産・輸出入=総資本形成と RoW)、(iii) **その他資産変動 K.5**(災害滅失・盗難・無主物化=非取引)に完全分割される。本リポの貨幣側は既にこの三分(部門間 / RoW / K5)を実装済み【実測】なので、**資産側は同じ枠の写像**: 製造・輸入=RoW からの流入、廃棄・滅失=K5、それ以外は所有者間移転のみ=「資産は無から生まれない」不変量。2025 SNA 改訂の資本勘定章が現行の整理。
    https://unstats.un.org/unsd/nationalaccount/snaupdate/2025/2025SNA_CH11_V5.pdf
17. **物理的 stock-flow 整合(資産保存則の学術前例)**【一次】 — Dafermos, Nikolaidi, Galanis の stock-flow-fund 生態マクロモデルは、貨幣のフロー行列に加えて**物質収支・エネルギー収支の物理フロー行列**を持ち、「物質・エネルギーは無から生まれず消えない」(熱力学第一法則)を会計恒等式としてモデルに埋め込む。= **貨幣ゼロ和検査と資産ゼロ和検査を並走させる設計の直接の前例**。
    https://www.sciencedirect.com/science/article/pii/S0921800916301343
18. **移転語彙の既存実装との対応**【実測】 — 売買(`spend`+goods の在庫減)・貸借(rent_due/evicted の状態機械)・遺失/拾得/時効取得(`lost_drop/lost_pickup/lost_return/lost_keep/lost_expire`)・担保(Bank 融資はあるが無担保)・贈与/相続/廃棄/製造=未実装。窃盗は `crime`(金銭のみ・K5 分類済み)。

### §3-5. 規模の工学

19. **MATSim(数百万エージェントの前例)**【一次】 — スイス全国 600 万 agent を回す設計原則は「対象機能に必要な水準まで全機構を削る」(車両追従を捨てて待ち行列モデルにする等)。= **「あらゆるものを実装」は「あらゆるものを同じ粒度で実装」を意味しない**という工学的根拠。
    https://www.ivt.ethz.ch/en/research/matsim.html / https://github.com/matsim-org/matsim-libs
20. **ECS の記憶効率**【一次+実測】 — archetype/SoA 格納は数百万 entity を扱える(§3-2 #13)。Python の dict レコードは 1 件数百バイト〜1KB なので、数百万件を dict で持つと GB 級+GC 負荷【推定】。`engine/soa.py` の「配列が真実・世代付き ID・step 境界での昇格/降格」は資産にもそのまま適用できる【実測=土台のみ配線前】。

### §3-6. 観察面

21. **貨幣の統計力学と保有時間分布**【一次】 — 保存則のある閉鎖系での交換は Boltzmann-Gibbs 分布を生む(Drăgulescu & Yakovenko)。**流通速度は平均保有時間の逆数**として微視的に定義できる(Wang らの holding time distribution)。= 資産の「流通速度」も**保有期間分布**として同型に観測できる。
    https://physics.umd.edu/~yakovenk/papers/money.pdf / https://arxiv.org/abs/physics/0507147
22. **所有ネットワークの構造解析**【一次】 — 世界の企業所有ネットワークは bow-tie 構造と支配の集中(super-entity)を示した(Vitali, Glattfelder, Battiston 2011)。= agent–asset–org の**二部所有グラフ**を作れば、同じ解析(支配の集中・連結成分・コア)が街スケールで可能。
    https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0025995

---

## §4. 表現方式の比較

### §4-1. 4 方式の定義と正体

| 方式 | 定義 | 現実/工学の対応物 | リポ内の先行例 |
|------|------|------------------|---------------|
| (a) object-centric(**ユーザー案**) | 各資産レコードが `owner` 属性(タグ)を持つ | IFC IfcOwnerHistory(物にメタデータ) | lost_property の item(owner/finder)・venture(owner)・has_car(bool) |
| (b) registry-centric | 中央台帳が `(asset_id, owner_id, 権利種別, 期間)` の行を持つ | Torrens 登記・日本の登記(対抗要件)・LADM・COBie | org 台帳・org_assignments・`sim._sfc_state`・`sim._lost_state` |
| (c) 関係エッジ | 所有= agent–asset 間のグラフエッジ(メタデータ付き) | BODS の ownership-or-control statement・所有ネットワーク研究 | ItemStore の transmissions(情報の移動エッジ)・VCFund.equity |
| (d) ECS 流 | entity=id、owner は component(または relationship)、列指向格納 | flecs / EnTT / soa.py | `engine/soa.py`(土台のみ) |

**最重要の観察**: この 4 つは**排他的な選択肢ではなく、レイヤが違う**【推定・§3 の全事例が支持】。

- (a) と (b) の違いは「レコードをどこに**置く**か」だけ: lost_property は既に「owner タグ付きレコード(=a)を中央 dict `sim._lost_state["items"]` に置く(=b)」というハイブリッドで動いている【実測】。エージェントの属性として資産リストを持たせる純粋 (a) は、転居の「空き住戸」判定が全 agent 走査になっている現状【実測 `freedom_p2.py:84`】と同じ逆引き問題を資産の数だけ再生産する。
- (b) と (c) は**同型**: 登記簿の 1 行は「メタデータ付きエッジ」そのものであり、違いは運用(単一の書き手・索引・不変量検査を持つか)にある。BODS が「statement の束=台帳」であることがこの同型の証明。
- (d) は意味論ではなく**格納方式**: (a)〜(c) のどれを選んでも、数が増えたら列指向に落とす話で、`soa.py` の移行契約がそのまま使える。

### §4-2. 権利の表現 — 「owner 1 個」では家賃も入院も書けない

ユーザー要件 R-b(権利)は、owner フィールド 1 個の (a) では表現できない。本リポの実測がそれを示している: 同じ住戸に「住んでいる人(agent)」「家主(不在=RoW)」「敷金という担保的地位」が既に併存し、ホテルは「泊まる権利(一時)」、病床は「占有(在院)」である【実測 §2-2】。LADM の RRR / bundle of rights(§3 #8, #15)に倣い、**行を「所有」ではなく「権利」にする**のが一般解:

```
(asset_id, party_id, right_kind, since_step, until_step)
  right_kind ∈ {own(所有), lease(賃借), permit(許認可), lien(担保), custody(占有=拾得者・在院)}
```

- 「所有」= `own` の行が 1 本ある状態。「賃貸中」= 同じ asset に `own`(家主)と `lease`(借主)が並ぶ状態。venture の `permitted` bool は `permit` 行の有無に一般化される。
- 遺失物の「hold(誰の残高でもない)」は「`own` は元 owner のまま・`custody` が無い」状態として自然に書ける = lost_property の状態機械はこのスキーマの特殊例【推定】。
- ただし**最初から 5 種を作る必要はない**。既定 ON にする観測最小核は `own` 1 種+期間なしで足り、`right_kind` は列挙を conf/registry に宣言して段階的に増やせる(IF-B の 3 水準 conf 化と同じ流儀)。

### §4-3. 移転の統一語彙(貨幣保存則との対)

すべての変化を「台帳への行の追加・削除・付け替え」+ L1 イベント 1 種に正規化できる:

| イベント | 台帳操作 | 貨幣側 | 分類(SNA 三分法) |
|----------|----------|--------|-------------------|
| 売買 | own を A→B に付け替え | B→A に `spend`(既存) | 取引 |
| 贈与 | own を A→B | なし | 取引(移転) |
| 相続 | own を故人→相続人(世帯 household_id が既にある) | money も同時に | 取引(移転)。現状は「死者の財布」に凍結【実測】 |
| 貸借 | lease 行を追加(own は不変) | 家賃 `rent`(既存) | 取引(サービス) |
| 担保 | lien 行を追加 | 融資(Bank 既存) | 取引(金融) |
| 遺失/拾得 | custody の消失/発生(既存 lost_*) | hold バケツ(既存) | K5→取引(返還) |
| 窃盗 | own はそのまま・custody が加害者へ | K5(既存) | K5(非取引) |
| 製造・輸入 | 行の新規作成(源=RoW) | 仕入(b2b 既存) | 境界フロー |
| 廃棄・滅失 | 行の削除(先=K5) | なし | K5 |

**資産保存則**: 「台帳の行は RoW(製造・輸入)からのみ生まれ、K5(廃棄・滅失)でのみ消え、それ以外の全変化は party の付け替えである」。IF-E の Σ 不変量の完全な双対で、カテゴリ別の枚数勘定「Σ(所有者別保有数)+K5 累積 − RoW 累積 = 初期ストック」がテストで固定できる【推定・§3 #16, #17 が前例】。

---

## §5. 評価表と推奨の素材

### §5-1. 評価軸ごとの比較

| 評価軸 | (a) 物にタグ(純粋 object-centric) | (b) 登記簿(中央台帳+権利行) | (c) グラフエッジ | (d) ECS 格納 |
|--------|----------------------------------|------------------------------|-----------------|--------------|
| R1 適合(既定 OFF・golden・観測がシムを変えない) | agent 属性に生やすと OFF 時の「キー自体を作らない」規約と衝突しやすい(属性は checkpoint に載る) | ◎ `sim._asset_ledger` を OFF では**作らない**だけで完結(lost_property/sfc の実証済み流儀) | (b) と同じ | 格納の話で軸に中立 |
| 貨幣/資産保存則 | 検査に全資産走査が要る(タグは分散している) | ◎ 台帳=検査対象そのもの。Σ 不変量・未分類種の監視装置(IF-E 流)が 1 か所で書ける | 検査可能だがエッジ列挙が要る | — |
| 25万性能 | 逆引き(この住戸は誰の物か)が O(agents)。IFC4 が実運用で任意化→廃止提案に至った肥大の轍 | ◎ 双方向索引(by_owner / by_asset)を台帳が一元管理= O(1)/取引。venture の `ventures_by_node` が前例 | 索引を張れば同等(=実装すると (b) になる) | ◎ 数百万件時の格納先(§6) |
| 既存資産との整合 | lost_property のレコード形式と同じ(=タグは残る) | ◎ lost_property・org 台帳・sfc_state・checkpoint runtime 中央管理と完全同型。housing の「空き住戸」全走査も台帳索引で置換可能 | ItemStore.transmissions と同型(履歴側) | soa.py の移行契約に整合 |
| 観測価値 | 資産ごとの現況は読めるが、分布・ネットワーク観測に全走査 | ◎ Gini・所有ネットワーク・保有期間分布が台帳の純関数(観測がシムに触らない) | ◎ ネットワーク解析はエッジ表現が直接材料 | — |
| 実装コスト | 小(属性を足すだけ)だが、移転・検査・観測のたびに費用を払い続ける | 中(台帳 module 新設)だが lost_property のコピーで骨格が立つ | (b) に含まれる | 大(が、必要になるまで不要=§6) |

### §5-2. ユーザーのタグ案への正面回答(素材)

- **タグ案の核心「所有されているもの自体に id と属性を持たせて観察・管理する」は正しい**。資産が第一級レコードであること自体は全先行例(住宅 ABM の住宅個体・LADM の BAUnit・lost_property の item)が支持する。
- ただし「タグを**どこに**持つか」で費用が分かれる。物・agent に分散して貼る(純粋 object-centric)と、(i) 逆引きの全走査、(ii) 保存則検査の分散、(iii) OFF 時の不侵襲性、(iv) checkpoint の一元性で毎回費用を払う。IFC の IfcOwnerHistory が「全オブジェクトにタグ」を必須→任意→廃止提案と辿った経緯(§3 #12)は、この費用が実運用で顕在化した事例。
- **推奨の形(ハイブリッド)= 「タグ付きレコードを登記簿に置く」**: ユーザー案のタグ(資産レコードの owner/right 属性)をそのまま採り、レコードの**置き場と書き手を中央台帳 1 つに限定**する(Torrens の「台帳が真実」+ 履歴は L1 イベント= curtain principle)。これは lost_property が既に採っている形の一般化であり、リポの流儀(単一の書き手・runtime 中央管理・Σ 不変量・未分類監視)と完全に噛み合う。
- 権利(R-b)は owner 1 個ではなく **RRR 流の権利行**(§4-2)に半歩広げる。既定 ON の最小核は `own` 1 種でよい。

### §5-3. R1 との整合(実装形の素材)

- `world.assets.enabled: false` 既定。OFF では台帳オブジェクト自体を作らない(キーも state も L1 も生えない)= golden 維持。lost_property・IF-E2 と同じ受入条件が書ける。
- 移転イベント(`asset_transfer` 等)は L1 の新 kind として schema 登録。**エージェントのプロンプトには出さない**(観測層に閉じる)のを第 1 段とし、「自分の持ち物」をプロンプト・記憶に見せる段は独立トグル(affects_k 再評価つき)= IF-E2 の「経営者に資金繰りを見せるのは将来の拡張」と同じ線引き。
- 初期配賦(誰が何を持って始まるか)は台帳の事前計算データ+決定論(org 配属と同型)。乱数を引くなら named stream 1 本。
- 自然主義(MEMORY: natural-coinage / nature-like)との整合: 売買・贈与を**勧めない**。既存の行為(spend・転居・出店・遺失)が台帳に写像されるだけで、新しい行動候補の提示は最小(または 0)から始める。

---

## §6. 規模と LoD の素材

### §6-1. 量の見積り【推定】

25 万 agent × 家財 5〜30 点 = **125 万〜750 万レコード**。Python dict 1 件 ≈ 数百 B〜1KB として素朴実装は **GB 級 + GC 負荷**で成立しない。一方、不動産(建物・住戸)は地図由来の有限個(数千〜万の桁)、org は 11,010、車両は保有率から万の桁 = **「登記簿に全個体で載せる資産」は合計しても数万行 ≈ lost_property/org 台帳と同じ桁**で、現行流儀のままで足りる。

### §6-2. 階層 LoD(判断材料)

| 層 | 資産 | 表現 | 根拠・前例 |
|----|------|------|-----------|
| L-full(全個体=登記簿の行) | 不動産(住戸・建物)・事業(venture/org 持分)・車両・自転車 | `(asset_id, party, right, term)` 行+属性レコード | 住宅 ABM は住宅を常に全個体で持つ(§3 #1, #2)。数万行= O(既存台帳)。`has_car` bool の個体昇格 |
| L-agg(世帯集計+代表個体) | 家電・家具・家財 | 世帯×カテゴリの計数+寿命(耐久財 ABM の通例 §3 #7)。**イベントが触れた瞬間だけ個体に実体化**(遺失・売却・譲渡・災害) | goods の「購入が起きた POI だけ在庫が実体化」・lost_property の「落ちた物だけレコード化」= **遅延実体化の既存流儀そのまま**【実測】 |
| L-flow(フローのみ) | 食料・消耗品 | 現行 spend+在庫のまま(資産化しない) | SNA も消耗品は資産境界の外。現行実装と一致 |

- 昇格/降格の規律は `soa.py` の移行契約(step 境界のみ・決定論)と同文でよい【実測】。
- MATSim の「目的の観測に要る粒度まで削る」原則(§3 #19)がこの階層の学術的根拠。**「範囲内のあらゆるもの」は「あらゆるものが観測に応答できる」ことで満たし、「あらゆるものが常時個体」では満たさない**。
- 将来数百万個体が本当に要る場合(例: 全家財の個体追跡)、(d) ECS/SoA 列(owner_id 列・category 列・state 列)へ台帳の格納だけ差し替える。意味論(§4)は不変。

### §6-3. 計算量の規約(素材)

- 取引 1 件あたり台帳操作 O(1)(dict 2 索引)。毎 step の全資産走査ゼロ(蒸発・寿命は日次境界で該当カテゴリのみ=traces の蒸発と同じ前例)。
- 観測(Gini・ネットワーク)は解析スクリプト側(`scripts/analyze_*` 系)で台帳スナップショットから計算= シム本体に走査を足さない。

---

## §7. この層が可能にする観測

1. **総資産 Gini・Lorenz 曲線**: 現金のみ(現状 status の資産順位が使う)→ 現金+不動産+事業持分の**総資産**へ。住宅資産は現実の家計資産の過半を占めるため、資産格差の観測はこの層なしには原理的に歪む【一次 §3 #1】。Sugarscape 以来の標準観測(§3 #5)。
2. **所有ネットワーク**: agent–asset–org の二部グラフ。支配の集中(bow-tie / super-entity §3 #22)、家主–借家人ネットワーク、org 持分の連鎖。ファウンダー観察(MEMORY: org-emergence-goal)に「創業者が何を所有して始めたか」の軸が加わる。
3. **流通速度・保有期間分布**: 貨幣の holding time(§3 #21)と同型に、資産の保有期間分布・回転率(住み替え頻度・家電の買い替え周期・中古流通率)。較正アンカーは実測統計(住宅の平均保有年数・家電の平均使用年数)に取れる。
4. **相続と世代間伝播**: 死亡時の資産移転(household_id が受け皿として既にある)を入れると、富格差の世代間持続(§3 #6)が観測可能になる。現状の「死者の財布への凍結」【実測】は観測上の盲点。
5. **資産保存則の検査そのもの**: 「無から生まれた資産ゼロ・行方不明の資産ゼロ」の Σ 検査+未分類移転種の監視装置(IF-E の双対)。会計検査が二重(金と物)になり、b2b_trade のような「金と物が同時に動く」イベントの整合が初めて機械検証できる。
6. **場所と所有の相互作用**: 空き住戸率・地区別の持ち家/賃貸比・立退きの空間分布。traces(場所の性格)と重ねると「所有の地理」が観測できる。
7. **事件レイヤの拡張**: 遺失・窃盗の対象が現金以外の資産に広がる(自転車盗は現実の刑法犯認知件数の最大品目)。返還率検証(lost_property の実測アンカー方式)を品目資産へ一般化できる。

---

## 付録: 本書が推す既定 OFF の最小スライス(判断待ち・実装しない)

1. **AssetLedger 新設**(`world.assets.enabled: false` 既定): 行= `(asset_id, party_id, right_kind="own", …)`+双方向索引+checkpoint runtime 中央管理。初期配賦は不動産(住戸→現居住者 or 不在家主=RoW)と車両(has_car の昇格)だけ。
2. **移転写像**: 既存イベント(転居・venture 開閉・遺失系・死亡)を台帳操作へ写像(挙動は 1 バイトも変えない=分類の追加だけ、の IF-E2 UNCOVERED 方式)。
3. **資産保存則テスト**: Σ 検査+未分類種監視(IF-E の雛形コピー)。
4. **解析スクリプト**: `analyze_assets.py`(Gini・保有期間・所有ネットワーク)。
家財の L-agg(世帯集計)・相続・中古市場・権利種別の拡張(lease/permit の行化)は、それぞれ独立の後続スライスとして PENDING に登録するのが本リポの流儀に合う。
