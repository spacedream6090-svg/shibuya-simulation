# 存在の内生化 — エージェントの生成・消滅を行動由来にする(人口動態の内生化)

作成日: 2026-08-12 / 種別: Webリサーチ+リポ実測(コード変更なし・実装しない)
対象: ユーザー構想(2026-08-12)「エージェントの存在(生成・消滅)は、エージェント自身の思考や行動によって決まるべきであり、世界側のプログラムが規定するものであってはならない」
姉妹文書: [presence-endogenization.md](presence-endogenization.md)(**在場**=「今日この街に誰が居るか」の内生化。日次スケール・PRES 計画として実装中)。
本文書はその一段深い層 = **存在**(「名簿そのものに誰が居るか」= プールへの登録と退場)を扱う。月次〜年次スケール。

> 検収の約束: 数値は出典 URL とセットで記す。推計(bbox 按分等)は推計と明記する。
> リポ内の実測(プール構成・機構の所在)は該当ファイル・行を示す。実在個人名をペルソナとして扱わない(文献著者名は通常の学術引用)。

---

## §1 構想の定式化(原文)

ユーザー原文(2026-08-12):

> 「シミュレーション内のエージェント数についてだが、ある程度現実世界の人数と同等になってほしいと考えている。ただし、エージェントの存在(生成・消滅)は、エージェント自身の思考や行動によって決まるべきであり、世界側のプログラムが規定するものであってはならない。初期条件としての人数は決める必要があると思うが、シミュレーションが進む中でおおよその人数は現実に沿う形で増減していくようにしたい。これもエージェントの思考・行動を通じて決まるようにする。たとえるなら、オープンワールドゲームに初期条件としてのエージェントが産み落とされ、時間が進むにつれてエージェントが自由に行動していく——そんなイメージ」

分解すると 4 つの要請になる:

| # | 要請 | 内容 |
|---|---|---|
| R-a | **規模の現実整合** | エージェント数 ≒ 現実の人数。増減も現実の人口動態に沿う |
| R-b | **生成・消滅の行動由来** | 誰かが生まれる・来る・去る・死ぬのは、エージェントの思考・行動の帰結。世界側のレート表・スポナーが決めない |
| R-c | **初期条件は許容** | t=0 の人数・構成は運営者が与えてよい(「産み落とす」) |
| R-d | **以後は自由** | 初期条件の後は世界が介入しない(オープンワールド像) |

この分解は在場内生化(PRES)のユーザー原理「世界のアルゴリズムがエージェント量を決めない」の**時間スケール拡張**である。PRES が扱ったのは日次(cap 切り・在場抽選)、本件が扱うのは月次〜年次(転入・転出・出生・死亡)。原理は同一で、対象となる「量」が違う。

なお R-c は学術側の標準初期化と完全に一致する(§3.1 SOCSIM: 初期人口ファイル+以後は個人イベントのみ)。つまり構想は「初期条件=運営者 / 以後の名簿の変化=全てイベント由来」という**契約**として定式化できる。

---

## §2 現状の存在機構 — 何が行動由来で、何が不在か

### 2.1 存在イベントの棚卸し(実測)

| 存在イベント | 機構(ファイル) | 由来 | 状態 |
|---|---|---|---|
| **名簿への登録(生成)** | `scripts/build_persona_pool.py` = ビルド時の決定論生成(seed 固定・SeedSequence 名前空間・LLM 不使用)。100 万人(L1 住民 30,000 / L2 従業者 224,240 / L3 定期来街 36,690 / L4 非定期 707,778 / L5 役割 1,292 = `data/persona_pool/meta.json`) | **初期条件(ラン外)** | ラン中に名簿へ行が増える経路は**存在しない** |
| **日次の実体化/退避** | `src/society/world/pool.py`(PoolStore 遅延読み+DormantStore 退避・dehydrate/hydrate)+`src/society/world/presence.py`(日次決定論選択・cap 250,000・平日資格者 306,716) | 世界側 cap+抽選 → **PRES で習慣内生化が実装中**(A1/B/C 承認済・A2 cap 撤去は 8/15 実測ゲート) | 実装済み |
| **日内の出入り(境界 despawn/respawn)** | `src/society/cognition/plan_boundary.py` = 朝の計画の `boundary` 欄が**そのまま despawn/respawn の時刻表**(境界機構は新設しない) | **行動由来(本人の計画)** | 実装済み(既定 OFF) |
| **死** | `src/society/health.py::_die`(第107)= 身体状態機械(発症チャネル→S3/S4→転帰)の帰結。境界 despawn と**同型の永続退場**(`loc="outside"` + `return_at=∞`・`sim.agents` から抜かない)。現実量較正(東京消防庁: 搬送死亡 1.3%・OHCA 生存退院 10%) | **行動・身体由来** | 実装済み。★ただし**急性転帰のみ**(§2.3) |
| **域内転居** | `src/society/mobility.py::relocate`(職場変更後の通勤閾値超・家賃逼迫 E5 滞納)+`freedom_p2.pick_home`(空き住戸の決定論選択) | **行動由来(職・金)** | 実装済み(既定 OFF) |
| **世帯形成・同棲・別居** | `src/society/household.py::form_partners`(relations closeness 相互高 → パートナー)→ `mobility.cohabit_day`(bond 継続 N 日 → move_in)/ unbond → move_out | **行動由来(関係)** | 実装済み(既定 OFF)。move_out は**域内での別居**であり街からの退場ではない |
| **相続(死→資産移転)** | `src/society/assets.py`(第109 O1 登記簿+O3 相続) | 死イベント由来 | 実装済み(既定 OFF) |
| **恒久転出(転出)** | — | — | **不在**。名簿からの実質退場は死のみ |
| **転入** | — | — | **不在**。プールは固定名簿 |
| **出生** | — | — | **不在**。`household.py` docstring が明示: 「childbirth/死別=**エージェント数が変わる重い機構は本波では作らない**」 |

要約: **消滅の片翼(死)と、存在の前段(世帯形成・転居・境界出入り)は既に行動由来化されている**。不在なのは「名簿そのものが増減する」3 イベント = **転入・恒久転出・出生**である。死も「急性転帰」に限られ、全死亡の一部しか表現していない(§2.3)。

### 2.2 受け皿となる既存資産(実測)

| 資産 | 本件への接続点 |
|---|---|
| `household.py`(世帯・パートナー・続柄・渋谷実分布 単身 64.5%) | 出生の前段(結婚→世帯)が既に行動由来で存在する |
| `relations.py` / `relations_endo.py`(closeness・承諾内生化) | パートナー形成の入力。「結婚による転入」(相手の呼び寄せ)の因果源になれる |
| `mobility.py` ③求職マッチ(「定員に空きがある会社 org を 1 つ返す」) | **企業の求人 → 就職転入**の域内側は実装済み。域外からの応募者に開くだけで転入の因果になる |
| `organizations`(センサス較正台帳 9,872 社・employees 定員) | 転入の需要源(空き定員)。学校 capacity は進学転入の需要源 |
| `assets.py` O1(住戸登記簿 = 住宅系 5,531 棟・延べ 11,948 階) | 空き住戸が**肯定形で**表現可能に(従来は「誰の home でもない」の否定条件)。転入の物理的受け皿 |
| IF-E 貨幣保存則+RoW 部門(`economy_sfc` 系)| 域外との金流の正典。**転入者の財産の流入経路**が既にある(§4.2-c) |
| 資産保存則(assets.py: 「行は **RoW からのみ生まれ**、K5 でのみ消える」) | 転入者の家財・車の登記はまさにこの宣言済み経路 |
| `pool.py` dehydrate/hydrate + DormantStore | **存在の物理表現は既にある**: 「名簿に居るが実体化していない」状態を毎日往復している |
| `build_persona_pool.py` の SeedSequence 名前空間(`[master_seed, layer_code, part_index]`) | 新レコードの**決定論生成**への拡張点(§4.2-a) |

### 2.3 工学的な不変条件(死の実装が既に教えていること)

1. **`sim.agents` から個体を抜かない**。第107 の死は「他レーンが持つ反復の前提を壊す」ため抜き取りを避け、`loc="outside"` + `return_at=∞` の**despawn 同型**で永続退場を表現した(health.py `_die` docstring)。→ 転出も同じ型で書ける(`dead=False` のまま帰還予定を無限へ)。逆に**生成**側も、実体の追加は既存 rotation の hydrate に任せ、「名簿への行追加+presence 資格」だけを新設するのが同型の解。
2. **id の安定性**: `PoolStore.id_of` はプール列挙順の密な整数(日跨ぎ不変・int32)。名簿追記は**末尾追加**なら既存 id を壊さない構造(シャード PART_SIZE=50,000 の末尾に足す)。ただし meta.json の件数・シャード一覧が動く = リビルド決定論・checkpoint/resume との境界条件になる(計画時の検証項目)。
3. **R1 規律**: 既定 OFF・golden L1 バイト一致・新 stream のみ・k 非依存・LLM 呼数増分ゼロ(存在イベントは日次数件=呼数影響ゼロ級。§4.2-e)。
4. **死の現在の守備範囲**: 第107 の死は街頭急変(OHCA 0.5〜0.7 件/日・区)の転帰であり、**全死亡(区 5.0 人/日)の 1〜2 割**に相当する層しか持たない。残りは病院・在宅での病死・老衰=シム未表現(§4.1 の拡張候補)。

---

## §3 文献・実数(URL)

### 3.1 動的マイクロシミュレーション — 「初期人口+個人イベント」の標準形と、レート表駆動の系譜

- **総覧**: [Li & O'Donoghue 2013, A survey of dynamic microsimulation models(International Journal of Microsimulation)](https://www.microsimulation.pub/articles/00082)。動的マイクロシミュレーションは個人に確率的イベント(死亡・出産・移動)の遷移確率を課して人口を前進させる枠組み。[Zagheni, Microsimulation in Demographic Research(PDF)](http://www.zagheni.net/uploads/3/4/4/7/34477700/microsimulation_in_demographic_research.pdf) は「エージェントは規定された確率イベントを課される placeholder」と要約する = **レート表駆動**の正直な自己定義。
- **SOCSIM**(Berkeley/MPIDR 系の人口動態シミュレータ): **初期人口ファイル+月次の年齢別出生率・死亡率**を入力に、以後は個人イベントだけで人口・親族網を前進させる。人口ファイル .opop は「シミュレーション中に生きた**全個体**を 1 行ずつ」保持する。[rsocsim PAA2023 ワークショップ(GitHub)](https://github.com/alburezg/rsocsim_workshop_paa)・[SOCSIM による系譜データのバイアス分析(European Journal of Population 2025)](https://link.springer.com/article/10.1007/s10680-025-09756-4)。→ ユーザー構想の「初期条件として産み落とし、以後はイベントのみ」は SOCSIM の初期化契約と**同型**。違いはイベントの決め方(レート表 vs 行動)だけ。
- **LIPRO**(オランダ NIDI の世帯動態モデル): 世帯内位置×遷移行列で出生・死亡・移出入を世帯状態別レートとして持つ完全動的モデル。[Flanders 応用例(IJM)](https://www.microsimulation.pub/articles/00167)。
- **SVERIGE**(スウェーデン全人口の空間マイクロシミュレーション): 全 900 万人・100m 解像度で出生・教育・結婚・離婚・離家・国内移動・移出入・死亡を動的に回す(約 90 秒/年)。[The SVERIGE Spatial Microsimulation Model(ResearchGate)](https://www.researchgate.net/publication/253561368_The_SVERIGE_Spatial_Microsimulation_Model)・[空間マイクロシミュレーションのレビュー(IJM)](https://microsimulation.pub/articles/00093)。
- **UrbanSim**: 世帯の「今年動くか」(転居確率)+「どこへ」(立地選択 MNL)をマイクロシミュレートする都市モデルの代表。[Waddell, Design and Implementation of UrbanSim(Networks and Spatial Economics)](https://link.springer.com/article/10.1023/A:1022049000877)・[公式ドキュメント](https://cloud.urbansim.com/docs/general/documentation/urbansim.html)。★正直ポイント: UrbanSim ですら**人口総数は外生のコントロールトータル**(転居・立地だけが選択モデル)。「総量=レート・配置=行動」が学術の多数派である。
- **ILUTE**(トロント圏。**意思決定駆動側の到達点**): 出生・死亡・転入出で個体が名簿に出入りし、**結婚は「結婚市場」**(相手探しの相互作用)、世帯分離は move-out モデルで駆動する統合都市モデル。[The ILUTE Demographic Microsimulation Model(Springer)](https://link.springer.com/chapter/10.1007/978-3-319-59511-5_10)。
- **系譜の整理**: レート表駆動(SOCSIM/LIPRO/SVERIGE)→ 意思決定駆動(UrbanSim の転居選択・ILUTE の結婚市場)→ 行動理論駆動(ABM)。移動 ABM のレビュー [Klabunde & Willekens 2016, Decision-Making in Agent-Based Models of Migration(European Journal of Population)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4803816/) は、移動の意思決定を random utility(離散選択)と計画的行動理論で内生化する系譜を整理し、「決定プロセスと社会ネットワークの設計こそが ABM の本体」と結論する。**ユーザー原理はこの系譜の最も行動側の極**にある。
- **open population ABM の先例**(在場リサーチ §3.4 から再掲): [Geard et al. 2013, Synthetic Population Dynamics: A Model of Household Demography(JASSS)](https://www.jasss.org/16/1/8.html) = 出生・死亡・転入出・世帯形成を個人イベントとして回し**人口規模を固定しない**標準形。

### 3.2 居住移動の行動モデル — 「引越しの決断」を個人の状態から導く前例

- **Wolpert 1965(stress-threshold)**: 人は居住ストレスが**閾値**を超えるまで転居を考えない。[Behavioral Aspects of the Decision to Migrate(ResearchGate)](https://www.researchgate.net/publication/229476798_Behavioral_Aspects_of_the_Decision_to_Migrate)。
- **Speare 1974(残余満足度)**: 個人・住居属性 → **居住満足度**(媒介変数)→ 閾値割れで探索開始 → 転居、の 2 段モデル。パネルデータで満足度が翌年の転居を予測。[Residential satisfaction as an intervening variable in residential mobility(Demography)](https://link.springer.com/article/10.2307/2060556)。
- **限界の正直な記録**: [Landale & Guest 1985, Speare's model reconsidered(Demography)](https://read.dukeupress.edu/demography/article/22/2/199/171575/Constraints-Satisfaction-and-Residential-Mobility) = 満足度は「転居を考えること」の良い予測子だが実転居の予測は弱く、構造変数(持ち家・年齢・家賃)が独立に効く。→ 満足度 1 変数に集約せず、**構造化状態(家賃滞納・持ち家・通勤距離)を直接読む**現行 `mobility.py` の形の方がむしろ文献整合。
- **転居理由の類型**: [Clark & Onaka 1983, Life Cycle and Housing Adjustment as Explanations of Residential Mobility(Urban Studies)](https://journals.sagepub.com/doi/10.1080/713703176) = ①ライフサイクル(結婚・出産・離婚・就職)②調整(広さ・家賃・環境)③非自発(立退き・取壊し)。ライフイベント→転居の実証: [The short- and long-term effects of life events on residential mobility(Advances in Life Course Research)](https://www.sciencedirect.com/science/article/abs/pii/S1040260815000519)。
- **ABM 実装例**: [Dynamic Urban Planning: an ABM coupling mobility mode and housing choice(arXiv)](https://arxiv.org/pdf/2106.14572)。
- **本シムとの対応**(接続点は全て既存状態にある):

| Clark & Onaka の類型 | 本シムの既存状態(トリガ候補) |
|---|---|
| ライフサイクル | `form_partners`/`unbond`(結婚・破局)・出生(§4)・`switch_org`/求職マッチ(就職・転職) |
| 調整 | E5 家賃滞納・`commute_threshold_m` 超の通勤・(O4 以降)lease 更新 |
| 非自発 | 立退き(O4 権利行)・死別(相続 O3 の裏面) |

### 3.3 人口動態イベントの行動由来化 — 結婚・出生を「レート表なし」で出す前例

- **Wedding Ring(Billari et al. 2007)**: 結婚を**社会的相互作用**(周囲の既婚者比率が結婚圧になる)から内生化し、外生の年齢別結婚レートなしで実測の年齢別結婚パターンを創発させた古典。[The "Wedding-Ring": An Agent-Based Marriage Model Based on Social Interaction(Semantic Scholar)](https://www.semanticscholar.org/paper/The-%22Wedding-Ring%22:-An-Agent-Based-Marriage-Model-Billari-Diaz/0d40d7fb6769d7a87d24c0efab37543b85cadf63)。→ 本シムの `relations closeness → form_partners` は**既にこの系譜の実装**である(相互作用由来・レート表なし)。
- **SAMP**: Wedding Ring に出生・死亡の動態を加えた半人工モデル。[Reforging the Wedding Ring(Demographic Research 29-27, PDF)](https://www.demographic-research.org/volumes/vol29/27/29-27.pdf)。
- **分野の教科書**: [Billari & Prskawetz, Introduction: Agent-Based Computational Demography(Springer)](https://link.springer.com/chapter/10.1007/978-3-7908-2715-6_1)・[結婚市場 ABM の設計レビュー(Springer 2019)](https://link.springer.com/chapter/10.1007/978-3-658-26042-2_3)。
- **出生の実数接続(日本)**: 国立社会保障・人口問題研究所「出生動向基本調査」= **夫婦完結出生児数 1.90 人**(第16回・2021。結婚持続 15-19 年夫婦の最終的な平均出生子ども数)。[第16回調査 結果概要](https://www.ipss.go.jp/ps-doukou/j/doukou16/doukou16_gaiyo.asp)・[概要 PDF](https://www.ipss.go.jp/ps-doukou/j/doukou16/JNFS16gaiyo.pdf)。調査自体が「結婚と出産に関する全国調査」= 日本の出生は結婚経由が支配的という構造を前提にしており、**世帯形成 → 出生**という因果連鎖の較正源になる。

### 3.4 実数アンカー — 渋谷区の人口動態

- **区の人口**: 住民基本台帳 231,402 人(令和7=2025 年 1 月)。[渋谷区 町丁目別世帯数及び人口](https://www.city.shibuya.tokyo.jp/kusei/tokei_shibuya/machi_setai_jimko/machi_setai_betsu_jinko.html)(bbox 内訳の按分は [shibuya-population.md](shibuya-population.md) が正典: bbox 夜間人口 ≒ 3 万 = プール L1 の 30,000 の根拠)。
- **転入・転出(2024 年・住民基本台帳)**: **転入 23,456 人 / 転出 21,898 人** = 転入超過 **+1,558 人/年**。出生 **1,669 人** / 死亡 **1,821 人** = 自然増減 **−152 人/年**。[生活ガイド.com 渋谷区統計(総務省 住民基本台帳人口・世帯数/人口動態調査に基づく)](https://www.seikatsu-guide.com/info/13/13113/1/)。
- **区公式の趨勢**: 社会動態は令和2(2020)年以降縮小したが転入超過は維持(令和4年 +752 人)。人口は令和2年以降減少 → 令和4年から増加へ。出生は減少傾向・死亡は微増で、**総人口を動かすのは自然増減より社会増減**。[渋谷区の状況(区資料 PDF)](https://files.city.shibuya.tokyo.jp/assets/12995aba8b194961be709ba879857f70/aa4669aef39c4c218b4c2ddeb1155363/sankou_shibuya_jyokyo.pdf)・[渋谷区人口ビジョン 令和2年度改定版(PDF)](https://files.city.shibuya.tokyo.jp/assets/12995aba8b194961be709ba879857f70/8184136c7f7b4b9897d709fcc9beccf8/assets_kusei_r2_shibuyajinkouvision.pdf)。
- **東京都全体(参照系)**: 2024 年の都内区市町村間移動者 1,323,660 人・**東京都の転入超過 79,285 人**(全国最多)。[東京都住民基本台帳人口移動報告](https://www.toukei.metro.tokyo.lg.jp/jidou/ji-index.htm)・[令和6年 結果のポイント(PDF)](https://www.toukei.metro.tokyo.lg.jp/jidou/2024/ji-point.pdf)・[総務省統計局 住民基本台帳人口移動報告 2024 年結果](https://www.stat.go.jp/data/idou/2024np/jissu/youyaku/index.html)(市区町村別の月次・年齢別の一次表は [e-Stat](https://www.e-stat.go.jp/stat-search/files?tstat=000000070001))。
- **移動理由**: 住民基本台帳人口移動報告は理由を採らないため、理由は調査系から。10〜20 代 = **進学・就職**、30 代以降 = **仕事(転職・独立・会社都合)と家族**が主因。[東京一極集中の動向と要因について(内閣官房 地方創生・PDF)](https://www.chisou.go.jp/sousei/meeting/senryaku_kensyou/h31-1-28-shiryou4.pdf)・[東京圏在住若年層の移動に関する意識調査(内閣官房 2025・PDF)](https://www.chisou.go.jp/sousei/pdf/01_houkokusyo_seihon_202502.pdf)。→ 転入の因果は**求人(職)・学校(進学)・世帯(結婚・家族)**の 3 本で現実の大半を覆う。
- **日次換算**(区全体 → bbox 常住按分 13% = L1 30,000/231,402):

| イベント | 区全体(人/日) | bbox 常住按分(人/日・推計) |
|---|---|---|
| 転入 | 64.3 | **8.4** |
| 転出 | 60.0 | **7.8** |
| 出生 | 4.6 | **0.59** |
| 死亡 | 5.0 | **0.65** |

按分の注意: bbox は商業核心で単身・若年比率が区平均より高い([shibuya-population.md](shibuya-population.md))ため、転入出はこの推計より**高め**・出生死亡は**低め**に出る可能性が高い(方向つきの概算と明記)。また死亡 0.65 人/日は**常住者の全死因**であり、第107 が較正した街頭急変(区 OHCA 0.5〜0.7 件/日 = `health.py` `ward_ohca_per_day`)とは母集団が違う(在場者全体 vs 常住者・急変のみ vs 全死因)。

### 3.5 オープンワールド/ゲーム AI の人口設計(参考・学術優先)

- **Watch Dogs: Legion「Play as Anyone」**: ロンドンの全 NPC にペルソナ・職業・日課・関係グラフを持たせ、視界外でも生活が継続する**永続個体群**を作った産業側の到達点(センサス的に生成した名簿+スケジュールシミュレーション)。[Ubisoft Toronto 公式解説](https://toronto.ubisoft.com/watch-dog-legions-play-as-anyone/)・[Game Developer: How Watch Dogs: Legion's 'Play as Anyone' Simulation Works](https://www.gamedeveloper.com/design/how-watch-dogs-legion-s-play-as-anyone-simulation-works)・[GamesRadar: 職業・勤務スケジュールのシミュレーション](https://www.gamesradar.com/watch-dogs-legion-simulation/)。
- **Dwarf Fortress**: 世界生成で数世紀の歴史・文明・人物(historical figures)をシミュレートし、以後のプレイでも世界の裏で出生・死亡・事件が継続する「永続世界+内生史」の代表。[PC Gamer: 42% towards simulating existence(Tarn Adams インタビュー)](https://www.pcgamer.com/dwarf-fortress-creator-on-how-hes-42-towards-simulating-existence/)・[開発者インタビュー集(DF Wiki)](https://dwarffortresswiki.org/index.php/List_of_Dwarf_Fortress_developer_interviews)。
- **読み取れる二層設計**: ゲームは「恒久 NPC(名簿制・履歴永続)」と「群衆 NPC(視界内で湧かせ視界外で消す)」の二層を使い分ける。本シムの L1〜L3/L5(名簿的・記憶持続)と L4(回転・DormantStore)は既にこの二層に相当する。ただしゲームの群衆は**世界側スポナー**そのものであり、ユーザー原理はそこを「名簿+本人の習慣」に置き換える方向(PRES が既に着手)。ゲーム側に「人口が現実統計に沿って増減する」機構は見当たらない = **R-a と R-b の同時達成はゲーム産業にも前例がない**。
- ユーザーの「産み落とされて自由に発展」像に最も近いのは Dwarf Fortress の世界生成(初期文明を置いて歴史を回す)だが、これも出生・死亡は世界側ルールである(行動理論由来ではない)。

### 3.6 LLM エージェント社会の現状 — 全て固定名簿

- [Generative Agents(Park et al. 2023, arXiv:2304.03442)](https://arxiv.org/abs/2304.03442): 25 人固定。
- [Project Sid(Altera 2024, arXiv:2411.00114)](https://arxiv.org/abs/2411.00114): 1,000+ エージェントの文明シミュレーション(経済・宗教・統治が創発)だが、個体の出生・転入出は扱わない。
- [AgentSociety(Piao et al. 2025, arXiv:2502.08691)](https://arxiv.org/abs/2502.08691): 1 万人規模・500 万相互作用の都市社会シミュレーションだが、人口は固定合成名簿。
- **含意**: LLM 社会シミュレーションで人口動態(名簿の増減)を行動由来で内生化した先行例は確認できなかった。実装すれば**空白領域**であり、k* データの副産物としても新規性がある(逆に言えば、参照実装なしで設計する必要がある)。

---

## §4 設計素材(実装はしない。判断材料のみ)

### 4.1 存在イベントのオントロジー — 「行動由来」表現の対応表

| 存在イベント | 現実の因果(§3.4 理由統計) | 行動由来のシム内表現(案) | 接続する既存資産 | 実数アンカー(bbox 常住/日) |
|---|---|---|---|---|
| **転入** | 就職(求人)・進学(入学)・結婚/家族 | **域内の受け皿への応答**として表現: ①org の空き定員への就職(求職マッチ ③ の応募元を域外へ開く)②学校 capacity への入学(年度境界)③既存個体との関係由来の呼び寄せ(partner の同居転入)。到着レートという世界ノブは持たず、**空き定員・空き住戸(O1 登記簿)・関係**という域内状態の関数にする | organizations(9,872 社)・求職マッチ・assets O1(空き住戸)・household/relations | 8.4 |
| **恒久転出** | 転職・結婚・住宅事情(§3.2 の類型そのまま) | `relocate` の行き先集合に**圏外**を追加(Wolpert/Speare の閾値型: E5 家賃滞納・立退き(O4)・unbond・switch_org 先が域外・通勤閾値超)。物理表現は**死と同型**(`loc="outside"`+`return_at=∞`・`dead=False`)= 新機構ゼロ | mobility・assets(lease)・plan_boundary の退場経路 | 7.8 |
| **出生** | 世帯形成 → 出生(完結出生児数 1.90) | partner/cohabit の**継続日数を入力とする決定論ハザード**(較正先= IPSS 1.90 と区の出生 1,669 人/年)。「結婚という行動の帰結」= Wedding Ring→SAMP の系譜。新生児 = 名簿への新レコード(§4.2-a) | household(世帯・続柄)・relations | 0.59 |
| **死(拡張)** | 全死因(急変は 1〜2 割) | 第107 の急性転帰に**慢性・老衰チャネル**(病院・在宅死)を追加して全死亡 0.65 人/日へ。frailty・age_band は実装済みの入力がそのまま使える | health(severity・frailty・EMS・H2 入院)・assets O3(相続) | 0.65 |
| **世帯形成・解消** | 結婚・離別 | **実装済み**(form_partners/cohabit/unbond)。存在イベントの前段としてそのまま使う | household・mobility | —(前段) |

- **因果台帳との整合**: 死は cause_type=physics で 1 行(演出ゼロ)の前例がある。転入・転出・出生も同じ流儀で L1 一行+因果台帳に**原因ノード**(求人 org・partner 形成・滞納イベント)を持たせる。「誰かの行動の結果として人が生まれる/来る」は、因果台帳では「存在イベントの親が別エージェントの行為イベントである」という機械的性質として観測できる = 検収可能な定義になる。
- **語彙の注意**: `move_in`/`move_out` は同棲の域内イベントとして既に使用済み。転入・転出には別語彙(例: `settle_in`/`settle_out` 等は計画時に決定)が要る。

### 4.2 生成の内生化の難所 — 5 課題と解の候補

**(a) 新エージェントのペルソナをどう作るか。**
`build_persona_pool.py` は SeedSequence([master_seed, layer_code, part_index]) の名前空間分離で「他パートの実行順に依存しない」決定論を既に確立している。ラン内生成はこの名前空間に**ラン内イベント用のコード**を足す(例: [master_seed, LC_RUNTIME, event_seq])だけで同じ決定論性が得られる。属性の源は 2 通り:
- **新生児**: 親レコードからの決定論導出(姓=世帯・年齢 0・home=世帯住戸・traits は親 2 人のブレンド+ハッシュ雑音)。ILUTE・SOCSIM が親子リンクを第一級で持つのと同型。深いペルソナ文は不要(子どもは長期ランでのみ意味を持つ)。
- **転入者**: **案A = L4 来街者の昇格**。プールに既に居る 70.8 万の非定期来街者から「この街に通ううち住む/働くことにした」遷移(layer/presence/org_id/home の書換え)。名簿サイズ不変・id 不変・レコード追記なし = 工学的に最軽量で、「来街 → 定着」という行動の履歴が転入の因果になる。ただし現実の転入者の大半が転入前に常連来街者だったという実証は無い(正直に: 因果の**演出**ではなく**近似**である)。**案B = 真の新レコード追記**(シャード末尾+meta 更新)。現実忠実だが checkpoint/resume・リビルド決定論の検証が重い。計画時に A/B を提示してユーザー判断。
**(b) 名簿と実体の二層を守る。**
存在の変更は「名簿(pool)の行の状態」だけで表し、日々の実体化は既存 rotation(hydrate/dehydrate)に任せる。死・境界が「新しい退場機構を作らない」で通した流儀の生成側対称形 = **spawn 機構を新設しない**。転出者・死者は名簿上「退役マーク」(presence 資格の永続喪失)であり、レコードは消さない(SOCSIM .opop が「生きた全個体」を保持するのと同じ。系譜・相続・観測が壊れない)。
**(c) 保存則との整合。**
- 貨幣: 転入者の持参財産は **RoW からの流入**として記帳(IF-E の域外部門は既存。Σ 検査は「Σ money + RoW 純流出累積 = 初期量」の形を既に持つ)。転出者は逆向きに RoW へ持ち出す。死者の財布は O3 相続が処理済み。
- 資産: assets.py の資産保存則は「行は RoW からのみ生まれ、K5 でのみ消える」と**既に宣言済み** = 転入者の家財・車両の登記はこの宣言の初の実運用になる。転出は所有行の RoW への付け替え(または売却 O5)。
- 出生: 新生児は財産ゼロで生まれる = どの保存則も破らない(世帯の支出構造だけが変わる)。
**(d) 転入の「完全な行動由来」は原理的に閉じない(最重要の正直ポイント)。**
転出・出生・死は**域内個体の行動**から完全に導出できる。しかし転入者の「来る」という決断はシミュレートしていない域外で起きる = どこかに到着過程が要る。ILUTE も in-migration は外生・SVERIGE は移入をレートで入れる(§3.1)= 学術も同じ壁を認めている。誠実な設計は「転入レートを世界のノブにしない」の最大化: **到着は域内状態(空き定員・空き住戸・関係)への応答としてのみ発生**させ、総量は較正**検証**目標(転入 8.4 人/日に合うか)であって駆動レートにしない(Cadyts 流 = ズレは個人パラメタへ帰す。PRES と同じ較正原理)。案A(L4 昇格)はこの妥協を最小化する(昇格の引き金を本人の来街履歴=行動に置ける)。
**(e) LLM 呼数・R1。**
存在イベントは日次 10 件台(§5)= 呼数影響ゼロ級。全機構は決定論+新 stream で書け、既定 OFF・golden 不変を守れる。新住民・新生児の深いペルソナ文が欲しい場合のみ llm_targets 流儀の任意上塗り(既存パイプラインの流用)。

### 4.3 初期条件の役割(R-c の契約化)

- **初期条件が決めるもの**: t=0 の名簿(100 万・センサス較正)と初期資産・関係。これは SOCSIM の初期人口ファイルと同じ「舞台の初期スナップショット」であり、DT 定義(ある時点の現実スナップショットが舞台)とも一致する。
- **初期条件が決めないもの**: t>0 の名簿の全変化。契約として「**ラン開始後、名簿の行の状態を変えられるのは存在イベント(転入・転出・出生・死)だけであり、各イベントは因果台帳上の親(行為イベント)を持つ**」と書ける = 検収可能(親を持たない存在イベント 0 件のテスト)。
- **burn-in の正直な注記**: 初期名簿の歪み(例: 世帯構成の機械束ね)がイベントで洗われるには年単位が要る。長期ランの序盤は「初期条件の残響」と「内生動態」が混ざる = 観測解釈の注意点として文書化しておく。

---

## §5 規模とタイムスケール — 本選では動かない設計であることを正直に

### 5.1 期待イベント数(bbox 常住 3 万人基準・§3.4 の按分値)

| ラン長 | 転入 | 転出 | 出生 | 死亡(全死因) | 名簿 100 万比 | 在場 25 万比 |
|---|---|---|---|---|---|---|
| **10 日(本選)** | 84 | 78 | 6 | 7 | 0.02% | 0.03〜0.07% |
| 30 日 | 252 | 234 | 18 | 20 | 0.05% | 0.1〜0.2% |
| **1 年** | 3,051 | 2,847 | 217 | 237 | 0.6% | 1.2〜2.4% |

- 1 年で常住 3 万人の**約 1 割が入れ替わる**(転入+転出の平均 ≒ 2,950 人/年 ÷ 30,000)一方、純増は +184 人/年(+0.6%)に過ぎない。渋谷の人口動態は「総量ほぼ静止・中身が高速入替」であり、これはプール規模(R-a)にはほぼ効かず、**誰が居るかの物語**(誰が去り誰が来たか)に効く。
- **10 日ラン(本選 8/16–8/26)では人口はほぼ不動**。転入 84・転出 78 は在場 25 万の 0.03% であり、k* 計測にも街の見えにも影響しない。渋谷区の転入出は月 2,000 人弱(区全体)= 本件は**本選の勝ち筋ではない**。
- ただし 10 日でも**予兆イベント**(E5 滞納 → 転居検討・求職マッチ・partner 形成)は日常的に起きるため、機構の縦煙(存在イベントが正しく発火し保存則が閉じること)は 10 日スケールの検証で可能。**較正の検定**(転入 8.4 人/日 ± に着地するか)は年単位ランでしか統計力が出ない。イベント強度を人工的に上げて短期検証する手はあるが、それは「世界がレートを盛る」ことと同義でユーザー原理と緊張する = やるなら検証専用ラン限定と明示すべき。

### 5.2 位置づけ

1. **本件は本選後(レーン3)の長期ラン向け設計**である。本選前に入れる理由は無い(動かないものを凍結前に足すリスクだけがある)。
2. 実装順の自然な提案(計画時の叩き台): ①死の全死因化(既存 health の拡張・最小)→ ②恒久転出(despawn 同型・機構ほぼ既存)→ ③転入(案A/B 判断・保存則結線)→ ④出生(新レコード+世帯接続・最重)。②までで「消滅」が完全に行動由来化し、③④で「生成」が閉じる。
3. 依存関係: PRES(在場内生化)の完成が前提(存在イベントは presence 資格の変更として表現されるため)。O4 権利行(lease/立退き)は転出トリガを豊かにするが必須ではない。
4. 学術的な位置: LLM 社会シムで人口動態を行動由来で内生化した先行例は未確認(§3.6)= 長期ラン論文の独立した貢献になりうる。「世界のアルゴリズムがエージェント量を決めない」を在場(日次)と存在(年次)の両スケールで貫徹した設計は、レート表駆動が標準の動的マイクロシミュレーション(§3.1)に対する明確な差別化点である。

---

## 出典一覧(主要 URL 再掲)

- 動的マイクロシミュレーション: [IJM survey](https://www.microsimulation.pub/articles/00082) / [SOCSIM workshop](https://github.com/alburezg/rsocsim_workshop_paa) / [SOCSIM 応用(EJP 2025)](https://link.springer.com/article/10.1007/s10680-025-09756-4) / [LIPRO 応用](https://www.microsimulation.pub/articles/00167) / [SVERIGE](https://www.researchgate.net/publication/253561368_The_SVERIGE_Spatial_Microsimulation_Model) / [UrbanSim](https://link.springer.com/article/10.1023/A:1022049000877) / [UrbanSim docs](https://cloud.urbansim.com/docs/general/documentation/urbansim.html) / [ILUTE](https://link.springer.com/chapter/10.1007/978-3-319-59511-5_10) / [Zagheni PDF](http://www.zagheni.net/uploads/3/4/4/7/34477700/microsimulation_in_demographic_research.pdf)
- 移動・転居の行動モデル: [Klabunde & Willekens 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC4803816/) / [Wolpert 1965](https://www.researchgate.net/publication/229476798_Behavioral_Aspects_of_the_Decision_to_Migrate) / [Speare 1974](https://link.springer.com/article/10.2307/2060556) / [Landale & Guest 1985](https://read.dukeupress.edu/demography/article/22/2/199/171575/Constraints-Satisfaction-and-Residential-Mobility) / [Clark & Onaka 1983](https://journals.sagepub.com/doi/10.1080/713703176) / [ライフイベントと転居](https://www.sciencedirect.com/science/article/abs/pii/S1040260815000519) / [住宅選択 ABM(arXiv)](https://arxiv.org/pdf/2106.14572) / [Geard et al. 2013(JASSS)](https://www.jasss.org/16/1/8.html)
- 結婚・出生: [Wedding Ring 2007](https://www.semanticscholar.org/paper/The-%22Wedding-Ring%22:-An-Agent-Based-Marriage-Model-Billari-Diaz/0d40d7fb6769d7a87d24c0efab37543b85cadf63) / [SAMP(Demographic Research)](https://www.demographic-research.org/volumes/vol29/27/29-27.pdf) / [ABCD 序章](https://link.springer.com/chapter/10.1007/978-3-7908-2715-6_1) / [結婚市場 ABM レビュー](https://link.springer.com/chapter/10.1007/978-3-658-26042-2_3) / [IPSS 第16回出生動向基本調査](https://www.ipss.go.jp/ps-doukou/j/doukou16/doukou16_gaiyo.asp)
- 渋谷・東京の実数: [渋谷区 町丁目別人口](https://www.city.shibuya.tokyo.jp/kusei/tokei_shibuya/machi_setai_jimko/machi_setai_betsu_jinko.html) / [渋谷区統計(生活ガイド)](https://www.seikatsu-guide.com/info/13/13113/1/) / [区の状況 PDF](https://files.city.shibuya.tokyo.jp/assets/12995aba8b194961be709ba879857f70/aa4669aef39c4c218b4c2ddeb1155363/sankou_shibuya_jyokyo.pdf) / [渋谷区人口ビジョン](https://files.city.shibuya.tokyo.jp/assets/12995aba8b194961be709ba879857f70/8184136c7f7b4b9897d709fcc9beccf8/assets_kusei_r2_shibuyajinkouvision.pdf) / [東京都 住基人口移動報告](https://www.toukei.metro.tokyo.lg.jp/jidou/ji-index.htm) / [令和6年ポイント PDF](https://www.toukei.metro.tokyo.lg.jp/jidou/2024/ji-point.pdf) / [総務省 2024 結果](https://www.stat.go.jp/data/idou/2024np/jissu/youyaku/index.html) / [e-Stat](https://www.e-stat.go.jp/stat-search/files?tstat=000000070001) / [移動理由(内閣官房)](https://www.chisou.go.jp/sousei/meeting/senryaku_kensyou/h31-1-28-shiryou4.pdf) / [若年層意識調査 2025](https://www.chisou.go.jp/sousei/pdf/01_houkokusyo_seihon_202502.pdf)
- ゲーム/LLM 社会: [Ubisoft Toronto: Play as Anyone](https://toronto.ubisoft.com/watch-dog-legions-play-as-anyone/) / [Game Developer 解説](https://www.gamedeveloper.com/design/how-watch-dogs-legion-s-play-as-anyone-simulation-works) / [GamesRadar](https://www.gamesradar.com/watch-dogs-legion-simulation/) / [PC Gamer: Dwarf Fortress](https://www.pcgamer.com/dwarf-fortress-creator-on-how-hes-42-towards-simulating-existence/) / [DF 開発者インタビュー集](https://dwarffortresswiki.org/index.php/List_of_Dwarf_Fortress_developer_interviews) / [Generative Agents](https://arxiv.org/abs/2304.03442) / [Project Sid](https://arxiv.org/abs/2411.00114) / [AgentSociety](https://arxiv.org/abs/2502.08691)
