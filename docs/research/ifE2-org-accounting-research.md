# IF-E2 案B — org の会計主体化 + rest-of-world(渋谷域外)概念実装 の実装前リサーチ

> 作成 2026-08-06 / 対象判断 = `PENDING.md:13` **IF-E2 案B**(2026-08-06 ユーザー決定)
> 前提の実測 = `scripts/analyze_accounting.py` docstring(第95バッチ)+ `tests/test_accounting.py`(39テスト)
> 既存の関連リサーチ = `docs/research/if-lane-research.md` §5(Caiani の検査2本)/ `docs/research/economy-abm-research.md` §1(EURACE・Delli Gatti の信用回路)/ `docs/research/llm-world-interface-audit.md` §3(revenue_est の断絶)
> **本書は設計候補の提示までで、実装・コミットは含まない。**
> 表記規約: 【実測】= このリポジトリのランまたはコードから直接確認 / 【一次】= 論文・公式文書で確認 / 【推定】= 本書の推論。

---

## §0. 3行サマリ

1. **文献の答えは一意**: SFC-ABM(Caiani 2016 ほか)では企業は「銀行預金という**スカラー残高**」を持ち、**賃金は生産の前に確保した預金/信用から支払われ**、払えない企業は**倒産して雇用を失う**。二重簿記の完全な貸借対照表は 1.1万社スケールでは不要で、**残高1つ+支払不能規則**があればゼロ和検査は閉じる。実装の単一点(`_spend` / `_pay_wage`)と保存が成立している唯一のテンプレ(venture の `_buy_at_ventures`)は既に本シムに存在し、案B はその横展開である。
2. **渋谷域外(RoW)は装飾ではなく必須**。台帳を全数集計した結果【実測】、**全 org の 36.5%(4,025社)・全従業者の 51.5%(129,872人)は、域内のどの消費カテゴリからも1円も受け取れない**(POI 種別 `office`)。彼らの賃金は「域外への輸出代金」でしか賄えず、これは地域会計(SAM/産業連関/観光サテライト勘定)で標準の扱い。ユーザーの「域外取引は概念のみでよい」という決定は、この 51.5% を成立させる**必要条件**である。
3. **最大の技術的発見: 現行の受け手解決規則は 11k スケールで 0% になる**【実測】。11,010社が 1,008ノードに乗っており(平均 10.9社/node・最大 117社)、**「node が一意なら org を付ける」現行規則で一意に決まるノードは1つも無い**。`(building, floor, POI種別)` を鍵にすると **56.8%(接客業種で 58.8%)が一意**・候補数の平均 1.5 まで落ちる。→ **`indoor` ON が org 単位の売上帰属の事実上の前提**であり、残りは決定論的な配分規則1つで閉じる。

---

## §1. SFC-ABM の設計表 — 企業はどう会計主体になっているか

### §1-1. 基準モデル: Caiani et al. (2016) — 一次資料から直接確認【一次・全34頁を本文抽出 2026-08-06】

`docs/research/if-lane-research.md` §5 で既に検査法2本を移植済み。本節はその**企業側の設計**を初めて精読した結果。

**(a) 企業が持つ残高 = 銀行預金**。フローの基本操作は次の一文に集約されている(§3.1.6 直後の flow 分類):

> **"Deposit transfers: If agents involved hold their deposits at the same bank, payer's deposit is decreased and receiver's increased."**

→ **「支払者の残高を減らし、受取者の残高を増やす」が同じ1操作である**。本シムの `_spend` は前半しか実装していない。これが漏れの正体そのものであり、**修正の方向は文献が1文で与えている**。

**(b) 賃金の資金源 = 事前に確保した預金 + 銀行信用**。企業は「**予想賃金支払額の一定割合 σ を予備的動機で預金として保有したい**」と明記:

> **"We therefore assume that firms desire to hold a certain amount of deposits, expressed as a share σ of the expected wages disbursement, for precautionary reasons."**

信用需要は式(3.11) `L^D_ct = max{ I^D_ct + Div^e_ct + σ·W^e_ct·N^D_ct − OCF^e_ct − D_ct , 0 }`(投資 + 配当 + **目標預金(=σ×予想賃金支払)** − 予想営業CF − 現在の預金)。
**時系列の順序が決定的**: > "After the credit market interaction between banks and firms has taken place, firms interact with unemployed households on the labor market. Production then takes place."
→ **信用市場 → 労働市場 → 生産**。**賃金の原資は生産の前に確保される**。

**(c) 売上 → 残高**: 財市場での取引が上記 deposit transfer として買い手→売り手の預金を動かす。売り手側に別式は無い(**推定値で売上を作る仕組みは存在しない**=本シムの `revenue_est` に相当するものが文献側に無い)。

**(d) 支払不能時の規則**(§3.3 Firms' and banks' bankruptcy):

> **"In each period of the simulation, firms may default when they run out of liquidity to pay wages or to honor the debt service if their net wealth turns negative."**
> **"For simplicity reasons, we assume defaulted firms and banks to be bailed in by households (who are the owners of firms and banks and receive dividends) and depositors in order to maintain the number of firms and banks constant."**

→ **判定基準は2つ**: ①賃金/債務を払う流動性が尽きた(フロー支払不能) ②純資産が負(ストック支払不能)。
→ **★決定的**: 基準モデルですら「**企業数を一定に保つため、破綻企業は救済(bail-in)される**」という簡略化を採っている。**§3-b で推奨した「既定=RoW 補填」は、基準モデルと同型の簡略化であり、文献的に正当**(資金の出所が家計か域外かの違いだけ)。
消費財企業の破綻時のみ、債権者へ所有権が移り、物的資本の投げ売り(fire sales、価値を割合 ι だけ毀損)で回収する。資本財企業は担保が無いので損失は全額銀行が負う。

**(e) 初期資本の与え方 = 定常状態のストック・フロー規範から導出**。恣意性を減らすため t=0 で**全主体を完全に均質**にし、異質性は累積効果から創発させる。パラメータ表(Table 3)では各値が `pre-SS`(定常状態を決めるため外生設定)/ `SS-given`(定常状態から導出)/ `free`(独立の論理)のどれかに分類されている。
→ **本シムへの含意**: §3-a で推奨した「配属者の日給合計 × バッファ日数」は、まさに (b) の σ×予想賃金支払 の離散版であり、**文献の慣行そのまま**。

**(f) 検査2本(§5.2 Validation)【一次・逐語】**:

> "Compliance with **Copeland's quadruple entry principle** requires that **every row and column of the matrices sum up to zero in every single moment of the simulation**."
> "checking that **the sum of the net worth of all the agents in the economy (including government and central bank) is exactly equal to the values of real assets** in every simulation round."
> "in practice **it is not unusual to observe leakages during the model implementation**. This is often the case for large complex AB models…"

(この3文は `scripts/analyze_accounting.py` の docstring が既に引用している内容と一致。**本リサーチで新たに得たのは (a)〜(e) の企業側設計**。)

### §1-2. モデル別 比較表

> 【一次】= 論文本文で確認 / 【二次】= レビュー・解説で確認 / 【未検証】= 一次確認に至らず

| モデル | (a) 企業の残高 | (b) 賃金の資金源 | (c) 売上→残高 | (d) 支払不能規則 | (e) 初期資本 |
|---|---|---|---|---|---|
| **Caiani et al. 2016**(基準)【一次】 | **銀行預金**(deposit)。負債側に loans | **事前に確保した預金 + 銀行信用**。目標預金 = σ×予想賃金支払。順序 = 信用市場→労働市場→生産 | 財市場の deposit transfer(**買い手減・売り手増を同一操作**) | 流動性枯渇(賃金/債務が払えない)**or** 純資産<0 → **家計/預金者による bail-in で企業数を一定に保つ**。消費財企業は債権者へ所有権移転+fire sale(毀損率 ι)、資本財企業の損失は全額銀行負担 | 定常状態のストック・フロー規範から導出。t=0 は完全均質にして異質性を創発させる |
| **EURACE / EURACE@Unibi**(Cincotti–Raberto–Teglio / Dawid ら)【二次・`docs/research/economy-abm-research.md` §1 で確認済み】 | **銀行預金**(現金でなく)。非金融主体間の取引はすべて銀行間取引に翻訳される | 銀行預金 + 借入。企業が借入制約を強く受けるほど景気循環の振幅が増す | 日次で各主体が流動資産を銀行に通知し、銀行間で純差額を清算 | 準備が負なら**中央銀行が貸す(最後の貸手)**。EURACE@Unibi は倒産処理と信用市場金利を精緻化 | 【未検証】 |
| **Delli Gatti ら / CATS 系**(financial accelerator, bankruptcy avalanche)【二次・同上】 | **純資産(net worth)**。レバレッジ(負債/純資産)を倒産確率の代理に置く | 銀行信用(川下企業↔川上企業↔銀行の3部門ネットワーク) | 生産関係のネットワーク上の取引 | **純資産<0 で破綻** → 取引先(川上)と貸手(銀行)が損失。銀行は生き残っても**信用供給を絞り全借手の金利を上げる**(credit rationing)→ **倒産の雪崩** | 【未検証】 |
| **Lengnick 2013**(baseline macro ABM) | 【未検証】(本セッションの WebSearch 予算上限に到達。実装着手前に一次確認すること) | 【未検証】 | 【未検証】 | 【未検証】 | 【未検証】 |
| **Poledna et al.**(economic forecasting ABM。国民経済計算で較正) | 【未検証】 | 【未検証】 | 【未検証】 | 【未検証】 | 【未検証】(「国民経済計算/産業連関表から初期化する」という主張自体を一次確認できていない) |
| **ASPEN**(Basu, Pryor & Quint 1998)【一次(書誌・要旨のみ)】 | 銀行システムと債券市場を含む「詳細な金融部門」を持つ | 【未検証】 | 【未検証】 | 【未検証】 | 【未検証】 |

### §1-3. 大規模スケールでの簡略化 — 本シムに効く3点

1. **「企業=スカラー1つ+支払不能規則」で検査は閉じる**【推定(Caiani の (a)(d) からの演繹)】。Caiani の企業が持つ金融ストックは**預金と借入の2つだけ**で、複式の完全な貸借対照表を明示的に構築しているわけではない(貸借対照表行列は**集計の検査装置**として事後に導出される)。→ **本シムの org は `balance: float` 1つで足りる**。借入は段階3(§3-b B-3)まで不要。
2. **倒産を「企業数一定の救済」に置き換える簡略化は基準モデル自身が採用している**【一次】。→ §3-b の既定 B-1(RoW 補填)は文献的に防御可能。
3. **検査は部門集計で行う**【一次・既に `if-lane-research.md` §5 で確認済み】。Caiani の行列も部門別(家計・消費財企業・資本財企業・銀行・政府・中央銀行)であり、**25万体でエージェント別 N×N 行列を作る前例は無い**。本シムの 6+1 部門は文献と同じ粒度。

### §1-4. LLM 経済シムはどこまで企業会計を持つか

**EconAgent**(Li/Yang et al., arXiv:2310.10436, ACL 2024)【本リポジトリで確認済み・`docs/research/if-lane-research.md` §5 / `economy-abm-research.md` §2】: LLM 家計が毎月決めるのは**労働意欲と消費性向の2つの実数だけ**で、ルールベース環境が中央政府(徴税)と中央銀行(金利)を兼ねる。**著者自身が限界として「企業(価格設定・雇用)が未実装」であることを挙げており、SFC 的な会計整合の検査についての記述は無い。**

→ **本シムの位置づけ**: 既に venture と B2B で保存が成立しており(`analyze_accounting.py` の実測)、案B で org へ拡張すれば「**LLM 社会シミュレーションで SFC 会計整合を機械検査した最初の例**」を主張しうる(`if-lane-research.md` §5 の既存判断を踏襲)。**この主張の価値は案B の実装可否とは独立に、既に IF-E の検査だけで半分成立している**。

> 【未検証・要追調査】Concordia(DeepMind)・AgentSociety(2025)・OASIS・TwinMarket など 2024-2026 の LLM 社会シムが貨幣保存を検査しているかは、本セッションでは一次確認に至らなかった(WebSearch 予算上限)。**「先行例なし」を論文で主張する前に必ず一次確認すること。**

---

## §2. rest-of-world(域外)部門の設計と文献的防御

### §2-1. 会計側の防御 — 「域外勘定に対して閉じる」は地域会計の標準

**(i) SAM(社会会計行列)の均衡規約**【一次(Wikipedia 経由の定義確認)・2026-08-06】: SAM は正方行列で、列 = 支出(買い手)・行 = 受取(売り手)。制度部門は Firms / Households / Government / **"Rest of Economy"** の4つで、**"each column is added up to equal each corresponding row"**(各列の合計が対応する行の合計に等しい)。域外勘定は純貿易(X−M)を記録する。**すなわち「域外」は SAM の設計に最初から組み込まれた第4の制度部門であり、後付けの逃げ道ではない。**

**(ii) 地域 SAM では域外勘定がさらに分割される**【二次・2026-08-06】: 地域版 SAM の慣行では RoW 勘定を「**rest of the nation(国内他地域)**」と「**rest of the world(海外)**」の2つに分け、地域間フローと国際フローを区別する。地域から域外へ出る流れは "leakage"(漏出)と呼ばれ、**測定対象であって欠陥ではない**。
→ **渋谷の場合、圧倒的に重要なのは前者(=東京都の他区・首都圏・日本国内)**。本シムの RoW は「rest of the nation」に相当し、海外との区別は不要。将来インバウンドを分けたくなったら2分割すればよい(SAM の慣行どおり)。

**(iii) 域外勘定に残高制約を課さないのは標準**: SAM/産業連関の単一地域モデルにおいて、域外勘定は**残差として行と列を閉じる役割**を担う。域外側の予算制約を内生的に解くのは多地域モデル(MRIO/多国 SFC)の仕事であり、単一地域モデルでは域外は外生である。
→ **ユーザー決定「域外取引は概念のみの実装でいい」は、単一地域モデルの標準的な閉じ方そのもの**であり、簡略化ではあっても逸脱ではない。

**(iv) Caiani の要求との整合**【一次・§1-1(f)】: 検査①②が要求するのは「**あらゆる時点で行列のすべての行と列がゼロに合計される**」(Copeland の四重記入原則)であって、「すべての部門が内生的に決定される」ことではない。**残高制約のない部門が1つあっても、その部門の行と列がゼロになる限り検査は成立する**。むしろ域外部門が無いと `void`(相手方不在)が残り、検査は**必ず落ちる**。

**(v) 観光客支出の扱い**【二次】: 観光サテライト勘定(UNWTO/国連 TSA RMF 2008)の枠組みでは、非居住者の域内消費は当該地域から見て**サービスの輸出**として計上される。本シムの `visitor`(来街者・渋谷昼間人口の ~56%)の消費は**域外から域内への資金流入 = RoW → 家計 → 域内 org** であり、`home_refill`(`scheduler.py:962-979`)は既にその第1段を実装している。**名前を付けていないだけ**。

### §2-2. 他シミュレーションの前例(ユーザー要望「他のシミュレーションの例も参考に」)

| 事例 | 域外の扱い | 本件への示唆 |
|---|---|---|
| **ASPEN**(Basu, Pryor & Quint 1998, *Computational Economics* 12(3):223-241。Sandia 国立研究所の米国経済マイクロシミュレーション)【一次(書誌・要旨)】 | 多数の個別経済主体を詳細に表現し、**銀行システムと債券市場を含む金融部門**を持つ大規模 ABM | **1990年代から「1.1万社規模で各主体に金融勘定を持たせる」ことは実行可能**という前例。本シムの 11,010社は特異な規模ではない |
| **Cities: Skylines**(Colossal Order/Paradox)の "outside connections"【二次・公式Wiki 2026-08-06】 | 都市の外は**制約のない供給源/吸収先**。過不足はすべて域外との輸出入で処理される。「プレイヤーが外部経済全体を詳細にシミュレートせずに経済バランスを管理できるようにする抽象化」 | **「概念のみの域外」の最も直接的な前例**。ただし**重要な反面教師**でもある: 公式Wikiは「**輸出によって市の予算に直接計上される収入は無く、輸入にも市庫の費用は発生しない**」と明記しており、**物の流れはあるが金の流れが閉じていない**。本シムが避けるべきはまさにこれで、**RoW を置くだけでは不十分・RoW との金額を必ず両建てで記録すること**が要件になる |
| **MMO/仮想世界経済の faucet-sink モデル**(Lehdonvirta & Castronova, *Virtual Economies: Design and Analysis*, MIT Press 2014)【二次】 | 通貨は**faucet(蛇口=クエスト報酬・NPC売却)から生まれ、sink(排水=修理費・手数料・NPC購入)で消える**。faucet > sink ならインフレ。EVE Online は 2007年に専属エコノミスト(Dr. Eyjólfur Guðmundsson)を雇い、貨幣供給を能動管理した | **本シムの現状はまさに「faucet と sink が制御されていない状態」**(wage/rule_bonus/interest = faucet、spend/rent/theft = sink)。案B の本質は **faucet と sink を RoW という1つの明示的な口へ束ねて計測可能にすること**。「制御しない」ことと「計測しない」ことは別であり、計測だけでも大きな前進 |

### §2-3. 本シムにおける RoW の設計要件(上記からの帰結)

1. **残高を持たない**(制約なしの吸収/放出部門)。— (iii)(iv) より正当。
2. **ただし累計は必ず両建てで記録する**(`row_in` / `row_out`)。— Cities: Skylines の失敗を回避。**これが無いと「漏れを RoW と改名しただけ」になる**。
3. **意思決定を持たない**(エージェントではない・LLM を呼ばない)。— k 完全不変。
4. **窓口の種別を必ず payload に持つ**(`home_refill` / `unknown_payee` / `rescue` / `export` / `procurement` / `escrow` / `shock`)。— 「どの経路で域外に依存しているか」が研究上の主結果になる(§3-b)。
5. **将来 2分割できる形にしておく**(rest of the nation / rest of the world)。— (ii) の SAM 慣行。今は分けない。

---

## §3. 本シムへの写像(a〜f)

### §3-0. 現状の「金の経路」完全目録【実測】

案B の設計はこの目録の上でしか決まらない。**残高を動かすコード行**を全数列挙した(サブエージェント検証済み・行番号は `83329e9`)。

| # | 経路 | 出所 | 現在の相手方 | 案B 後の相手方(推奨) |
|---|---|---|---|---|
| 1 | 消費 `spend` | `scheduler.py:571` `_spend`(**全消費の唯一の通過点**) | **無し(VOID)**。`cat=="venture"` のみ venture 所有者 | **org / venture / RoW**(§3-c) |
| 2 | 賃金 `wage` | `scheduler.py:510` `_pay_wage`(**全賃金の唯一の通過点**) | `civil`=行政歳出のみ実在。`salary`/`gig`/`severance`/無印は**無からの創出** | **org 残高 / RoW**(§3-b) |
| 3 | 来街者補充 `wage(source=home_refill)` | `scheduler.py:962-979` | 解析上 EXTERNAL(sim には主体なし) | **RoW → 家計**(§3-f。命名のみ) |
| 4 | 家賃 `rent` | `scheduler.py:3174, 3190` | **家主が居ない(VOID)** | **RoW(不在家主)** or 将来 org(不動産業 RE=990社) |
| 5 | 転居敷金 `move_home.deposit` | `scheduler.py:3602-3604` | **VOID** | **RoW**(escrow 主体なし。§3-e) |
| 6 | 供託金 `deposit`(議案) | `tools.py:777-782` / 精算 `tools.py:1349` | **VOID(escrow 不在)** | **行政の預り金**(§3-e) |
| 7 | 供託金 `candidacy.deposit`(立候補30万) | `tools.py:591-597` / 精算 `tools.py:309` | **VOID**(没収時のみ `gov.collect`) | **行政の預り金**(§3-e) |
| 8 | 出店費用 `venture_open.cost` | `tools.py:855-860`(既定 30,000円) | **VOID** | **RoW(域外の内装業者・仕入)**(§3-f) |
| 9 | 預金利息 `interest_paid` | `scheduler.py:3311-3319` | `agent.account += itr` のみ。**`Bank.capital` を減らさない=貨幣創出** | **`bank.capital -= itr` の1行**(§3-e) |
| 10 | 融資 `loan_grant` / 返済 `loan_repay` | `scheduler.py:290, 324` + `economy.py:592, 600` | **保存済み**(`Bank.capital` が増減) | 変更なし |
| 11 | 屋台売上 `venture_sale` | `tools.py:1618` `_buy_at_ventures` | **保存済み**(買い手 `_spend` → 売り手入金を同一箇所で記述) | 消費税分の精算のみ(§3-c 注) |
| 12 | 税 `tax` | `_withhold_wage` 477 / `_record_consumption_tax` 498 | **行政へ実入金**(government ON 時) | 変更なし。ただし源泉の**支払側**が org になる(§3-d) |
| 13 | 罰金 `enforcement` | `scheduler.py:3795, 3855` | government ON なら行政。OFF は VOID | government OFF 時は **RoW**(§3-d) |
| 14 | 制度ボーナス `rule_bonus` | `rules.py:333` | **財源なし(VOID)** | **行政歳出**(§3-d) |
| 15 | 窃盗 `crime(theft)` | `diversity.py:296` | 被害者から減るだけ。**加害者は受け取らない** | 加害者へ入金(§3-e。挙動変化を伴うため別判断) |
| 16 | 破産の資産圧縮 `bankruptcy.seized` | `scheduler.py:3228-3229` | **消滅** | **Bank(貸倒回収)** or RoW(§3-e) |
| 17 | 偶発事 `chance_event` | `chance.py:126, 129` | 解析上 EXTERNAL | **RoW**(命名のみ) |
| 18 | 実験報酬 `reward` / 資本注入 `spark` | `scheduler.py:1241` / `spark.py:240` | 解析上 EXTERNAL(ablation 用の外生) | **RoW**(命名のみ。実験装置として正当) |
| 19 | B2B `b2b_trade` | `b2b.py:144-176` | **帳簿 dict のみ**(`revenue`/`procurement`)。残高は存在しない | **org 残高間の実移動**(§3-b) |
| 20 | VC 出資 `vc_investment` / 配当 | `tools.py:1209` / `commerce.py:296-312` | **保存済み**(`VCFund.balance` が増減) | 変更なし |
| 21 | 現金⇄口座 `withdraw` | `scheduler.py:554-568` | 家計内部の資産振替(行列に出ない) | 変更なし |

**重要な構造的事実【実測】**:
- 非エージェントの残高を持つのは **`Government.balance`・`Bank.capital`・`VCFund.balance` の3つだけ**。L1 に出るのは `Government` のみ(`public_budget`)。
- **その3つとも checkpoint に入っていない**(`checkpoint.py:66-282` に `government`/`bank`/`vc_fund` キーが無い)。resume で残高が初期値に戻る**既存の欠陥**。`tests/test_resume.py` はこれを検査していない。→ **案B は「org 残高を足す」前に「非エージェント残高の checkpoint 規約」を確立する必要がある**(§4 バッチ0)。
- `sim.org_ledger`(dict)は `scheduler.py:410` で初期化されるが、この行は `_resumed` 早期 return(414行)**より前**にあるため resume で必ず `{}` に潰れる。**現状の器のままでは残高を持てない**。読み手も存在しない(デッド状態)。
- `tests/test_indoor_invariance.py`(検査③・128行)は**静的テキスト検査**で、`src/society/engine` と `src/society/world` が `org_ledger_sc` から `.rows` を読むことを禁じている。→ **org 残高は観測サイドカーではなく sim 状態(checkpoint 対象)に置くしかない**。

---

### §3-a. org 残高の初期化

**文献の慣行**(§1): 企業は「**予想賃金支払額の一定割合**を予備的動機で預金として保有する」(Caiani et al. 2016)。初期値は「賃金支払 n 期分」で与えるのが標準。

**本シムで直接使える材料【実測】**:
- 台帳 `data/organizations_shibuya_wide11k.json` = **11,000社 + 学校10校**。従業者総和 **252,311人**(平均 22.94人/社)。規模帯は 1-4人が 43.7%、300人以上が 0.9% の裾長分布(`docs/research/org-book-11k.md`)。
- 賃金は `conf/config.yaml:559-563` の日給表(会社員 12,000 / 自営 10,000 / 店員 9,000 / バイト時給 1,100)。
- 支給は**月まとめ**(`scheduler.py:3177-3181` 給料日 `payday_dom`: 日給 × 勤務日数)。→ **org 残高は約20営業日ぶんの賃金を溜めてから一括流出する**。初期残高が薄いと初回給料日に全社同時倒産する。

**設計案(3択)**

| 案 | 初期残高の式 | 得 | 失 |
|---|---|---|---|
| **a-1 賃金倍数(推奨)** | `balance0 = Σ(配属者の日給) × wage_buffer_days`(既定 `wage_buffer_days: 45`) | 文献の慣行そのまま。**実際に配属された agent だけ**を数えるので、40体 mock でも 25万体本番でも自動でスケールする。決定論(乱数ゼロ) | 台帳の名目従業者数(252,311)ではなく実配属数に依存 → 台帳上の大企業でも配属0なら残高0 |
| a-2 台帳従業者数ベース | `balance0 = employees × 日給 × 日数` | 台帳の規模分布(裾長)がそのまま残高分布になり、現実の企業規模格差を再現 | 実際に払う賃金は実配属者ぶんだけなので、**大半の org が過剰資本**になり支払不能規則が一度も発火しない=倒産機構が死ぬ |
| a-3 一律定数 | `balance0 = const` | 最も単純 | 規模格差が消える。大企業が真っ先に潰れる(反現実) |

**推奨 = a-1**、ただし**下限**を置く(`max(実配属賃金×45日, min_initial)`)。理由: 配属0の org(mock の小ラン・pool ローテーションで在場者が居ない org)が残高0で即倒産扱いになるのを防ぐ。**上限は置かない**(裾長を潰さない)。

**RoW との関係**: a-1 の初期残高は「創業時に域外から持ち込まれた資本」であり、**RoW → org の期首フロー**として行列に明示的に載せる。こうすると t=0 でもゼロ和が成立する(§2 の SAM 慣行どおり)。

---

### §3-b. 賃金の資金源 = org 残高 / 不足時の規則

**単一点の存在【実測】**: `_pay_wage`(`scheduler.py:510`)は docstring に「**全 wage 源(本業/バイト/日銭 gig/月給/公務員)がこの唯一の支給点を通る**」と明記されている。しかも `fund_level` 引数(公務員給与)が既に「**支払側の残高を減らしてから受け手へ入れる**」テンプレになっている(`scheduler.py:531-532` `sim.government.expense(fund_level, gross)`)。

→ **設計 = `_pay_wage(..., payer_org: str | None = None)` を足し、`payer_org` 指定時に org 残高から `gross` を引く。** `fund_level` と完全に同型で、既存経路(`payer_org=None`)はバイト一致。

**支払側を決めるべき呼び出し元は4箇所しかない【実測】**

| 呼び出し元 | 何の賃金 | 案B での支払側 |
|---|---|---|
| `scheduler.py:647` | 本業の勤務完遂 / バイトのシフト完遂(口座 OFF 経路) | **配属 org**(`agent.org_id`)。無配属なら RoW |
| `scheduler.py:3181` | 月給まとめ(給料日。日給×勤務日数) | **配属 org**。**流出が月1回まとまるので初期残高の設計(§3-a)が効く** |
| `scheduler.py:3309` | 自営の日銭 `gig`(`daily_base × uniform(0.2,1.4)`) | **RoW(域外の顧客)**。フリーランス/写真家/配達員は街の中に客が居ない。「域外のクライアントからの入金」という**概念のみの実装がそのまま正解になる代表例** |
| `scheduler.py:3345` | 公務員給与 `civil` | **行政**(既に `gov.expense(fund_level, gross)` 済み=変更なし) |

**併せて発見した第2の断絶【実測】**: `org_ledger.wage_paid` は **org の `wage_tier`** から引いた日給(`scheduler.py:449-451`)を積むが、実際に `_pay_wage` が払うのは **agent の occupation 由来の `agent.wage`**(`economy.wage_amount`)。両者は一致するとは限らない(例: `店員` の occupation を持つ agent が `wage_tier=会社員` の org に配属されると 9,000 vs 12,000 でズレる)。案B で org 残高から引くのは**実際に払った額(`gross`)**であるべきで、`wage_paid` 列はそれに置き換える(または `wage_actual` を並置する)。

**支払不能時の規則(文献の4流儀・§1)と本シムでの得失**

| 規則 | 文献 | 本シムでの帰結 | 判定 |
|---|---|---|---|
| **B-1 RoW 自動補填**(「域外本社からの送金」と宣言) | 地域 SAM の域外勘定(§2) | 保存は**必ず**閉じる。倒産が起きないので雇用喪失も起きない。**観察対象(組織の生死)が消える** | **既定に推奨**(段階1)。ユーザーの「概念のみでよい」に合致し、金額を L1 に出せば「域外依存度」という新しい観察量になる |
| **B-2 倒産機構**(残高<0 で org 閉鎖・従業員解雇) | Caiani / Delli Gatti の bankruptcy avalanche | **雇用喪失 → 求職 → 転職**という既存機構(`career` / `switch_org`)に接続でき、**創発の観察動線としては最も濃い** | **段階2で ON 可能な独立トグル**。ただし挙動が大きく変わる(k にも波及しうる)ので既定 OFF |
| B-3 信用線(銀行が自動融資) | EURACE の企業向け信用市場 | `Bank` は既に `grant`/`write_off` を持つ。ただし現状は **agent_id キー**(`economy.py:587` `loans: dict[int, dict]`)なので org 用の別辞書が要る | 段階3。B-2 の前提として自然(借りられなくなって初めて倒産する)が、工数は最大 |
| B-4 比例配分(払える分だけ払う) | 一部の ABM | 賃金が減る=家計側の挙動が変わる。**「働いたのに全額もらえない」は L1 に出さないと不可解** | 非推奨(観察動線が濁る) |

**★ 既定を B-2(倒産)にしてはいけない定量的理由【実測+推定】**: IF-E の実測で `revenue_est` は「org 帰属店舗で実際に起きた spend」の **30.9倍**(`tests/test_accounting.py:511` が `ratio > 5.0` で固定)。つまり **域内消費は域内賃金を賄うには桁で足りない**。案B で接客業種 6,985社を「域内 `spend` だけ」で回すと、**初日から全社が支払不能に落ちる**。これは案B のバグではなく、**案B が初めて可視化する実測事実**である(いままでは漏れとして消えていたので誰も気づけなかった)。
したがって既定は「補填して観測する」でなければならず、`org_rescue` の総額こそが **「この街の経済が域外にどれだけ依存しているか」という研究上の主結果**になる。倒産機構(B-2)は、消費側の較正(価格・消費頻度)が済んだ**後**に初めて意味を持つ。

**推奨**: 既定 = **B-1(RoW 補填)**。理由は3つ。(i) ユーザー決定「域外取引は概念のみでよい」に一致。(ii) **保存が無条件に閉じる**ので、`analyze_accounting` の検査①②が「全部門で成立」という受入条件を確実に満たせる(B-2 単独だと倒産の瞬間の残余処理が新しい漏れになる)。(iii) 補填額そのものが**「この街の経済が域外にどれだけ依存しているか」という研究上有意味な観測量**になる。
その上で **B-2 を `economy.org.insolvency: rescue | bankrupt` の2水準として用意**し、既定 `rescue`。`bankrupt` は既存の `force_close_venture`(`tools.py:1115`)/ `organizations.switch_org` に接続する。

---

### §3-c. spend の受け手解決(最重要かつ最も難しい)

**問題の実測**: `serve` の **220/222 がスタッフ不在**で org 特定率が極端に低い。根本原因は3段【実測】:
1. `_phase_work_service`(`scheduler.py:1774`)は「**客と同一 node を work_node とし、勤務時間帯に在場している agent**」を探す。
2. `commute_to_poi` の既定が **false**(`conf/config.yaml:2092`)なので、配属者の `work_node` は台帳の `workplace_poi` ではなく persona 側の職場になる。→ 客が行く店に org 従業員が立っていない。
3. フォールバックの `_org_node_org_ids`(`scheduler.py:1621-1632`)は「**その時点で在場している agent の org_id**」から node→org を作る。台帳を読んでいないので、在場0の店は解決不能・複数社同居 node は `None`(正直に unknown)。

**決定的な設計転換**: 受け手を **`serve` の事後突合ではなく `_spend` のその場で解決する**。`_spend` は客の `agent.node`(+ indoor ON なら `building`/`floor`)を持っており、**支払の瞬間に受け手を確定できる**。venture が既にこの流儀(`tools.py:1633-1648`: 同じ関数の中で買い手を引き落とし売り手へ入金)で**唯一保存が成立している**。

#### ★ 本リサーチの最重要実測 — 解決鍵の一意性を台帳 11,010社で全数測定した

`data/organizations_shibuya_wide11k.json` を直接集計した【実測・2026-08-06】。**この数字が案B の受け手解決の設計を一意に決める。**

| 解決鍵 | 相異なる鍵の数 | **一意に決まる割合** | 候補数の平均 | 最大 |
|---|---:|---:|---:|---:|
| `node` のみ(= **現行 `_org_node_org_ids` の鍵**) | 1,008 | **0.0 %** | 10.9 | 117 |
| `node` + POI 種別 | 1,524 | 4.5 % | 7.2 | 69 |
| `node` + `building` | 1,576 | 0.0 % | 7.0 | 117 |
| **`building` + `floor` + POI 種別** | 7,585 | **56.8 %** | **1.5** | **3** |
| 接客業種のみ(POI 種別 = food/shop/service = **6,985社**)で `building`+`floor`+POI種別 | 4,918 | **58.8 %** | **1.42** | 3 |
| 同上・`node`+POI種別だけ(= indoor OFF 相当) | 1,024 | 4.8 % | 6.82 | — |

**この表から直ちに従う4つの結論**:
1. **現行の「node が一意なら org_id を付ける」規則は、11k 台帳では原理的に 0 件しか解決しない。** 1,008ノードに 11,010社が乗っており(平均 10.9社/node・最大 117社/node)、**一意なノードは1つも存在しない**。IF-E で観測された「220/222 スタッフ不在 → org 特定率が極端に低い」は、小ランのスタッフ配置問題であると同時に、**スケールさせると必ず 0% に落ちる構造的な問題**である。
2. **`floor` を鍵に入れた瞬間に 56.8% が一意になる**(候補数の平均が 10.9 → 1.5 へ)。つまり **`indoor` を ON にすることが、org 単位の売上帰属の事実上の前提条件**。`_spend` の時点で客の `agent.building` / `agent.floor` は既に確定している(`_phase_work_service` の `floor_gate` が同じ値を使っている=`scheduler.py:1826-1829`)。
3. **POI 単位まで降ろす道は無い**: `workplace_poi.poi_id` を持つのは**学校10件のみ**(会社 11,000件は `cat/node/building/floor/x/y` だけ)。よって鍵の上限は `(building, floor, POI種別)`。
4. **残り 41% の多義(候補2〜3社)は「解決不能」ではなく「候補が少数に絞れている」状態**。候補数の平均が 1.42 なので、**決定論的な配分規則を1つ決めれば足りる**。

**受け手解決器の設計(4段)**

| 段 | 鍵 | 効果【実測】 | 実装 |
|---|---|---|---|
| **c-1** | `(building, floor, POI種別)` の台帳静的表 | 接客業種の **58.8%** が一意 | `organizations.load_book` の結果から起動時に1回だけ構築(乱数ゼロ・決定論)。`sim.orgs` は既に読み込み済み |
| **c-2** | 上で決まらない候補2〜3社 → **決定論的に1社へ配分** | 残り 41% を解決 | 下記の2案から選ぶ |
| **c-3** | indoor OFF ラン / 候補0件 | `(node, POI種別)` で 4.8% + 残りは c-2 | 縮退経路。**精度が落ちることを L2 に開示する** |
| **c-4** | それでも決まらない | **RoW(域外資本の店)** | **保存を無条件に閉じる最後の受け皿** |

**c-2 の2案(候補が複数のときどうするか)**

| 案 | 規則 | 得 | 失 |
|---|---|---|---|
| **c-2A 比例配分** | 候補社へ `size.employees` 重みで**金額を分割**する | **乱数を1粒も引かない**。地域 SAM 構築の標準手法(比例配分)と同型で文献的に防御可能(§2)。保存は厳密 | 1回の買い物が2〜3社に分かれる。**「誰が受け取ったか」の観察動線が濁る**(ユーザー要求と摩擦) |
| **c-2B 単一先を決定論抽選** | `sim.hub.stream("payee", agent.id, step)` で候補から1社を employees 重みで抽選 | **1取引=1受け手**。個人→会社→個人の追跡がそのまま繋がる(ユーザーの「観察できる動線」に一致)。集計量は c-2A と一致 | 新しい named stream を1本足す(既定 OFF なら1粒も引かないので `test_placebo` の stream 別 draw 数パリティは無風) |

**推奨 = c-2B**。理由: (i) ユーザーの設計思想「範囲内の取引なら個人と企業・組織が存在するので観察できるようにできる」は**個々の取引に受け手が1つ立つこと**を要求している。(ii) 候補数の平均が 1.42 しかないので、抽選の影響は小さく、58.8% では抽選自体が発生しない。(iii) RNG ハブの stream 分離規約(`sim.hub.stream`)が既に確立しており、新 stream の追加は既存 stream の系列を1粒も動かさない。
c-2A は「乱数を絶対に増やしたくない」場合の代替として conf 値 `payee_split: proportional | single` で選べるようにしておく。

**この4段なら spend 族の漏れは定義上ゼロになる**(必ずどこかへ着地する)。段ごとの解決件数を L2 に出し、**「どの精度で受け手を特定できたか」を正直に開示する**(第58の掟=多義 node は unknown と開示、と同じ流儀)。

#### ★ 第2の実測 — 全 org の 36.5% は「街の中に客が居ない」

台帳を全数集計した【実測・2026-08-06】。**従業者ベースで見ると事態はもっと極端**:

| `workplace_poi.cat` | 社数 | 従業者数 | 従業者シェア | 域内 `spend` から売上を得られるか |
|---|---:|---:|---:|---|
| `office` | 4,015 | 129,872 | **51.5 %** | **不可**(客が街の中に居ない) |
| `shop` | 3,850 | 68,149 | 27.0 % | 可(`spend.cat=shop`) |
| `service` | 1,485 | 36,625 | 14.5 % | 可(`free_*` / サービス消費) |
| `food` | 1,650 | 17,665 | 7.0 % | 可(`food`/`cafe`/`nightlife`) |
| `education` | 10 | 0 | 0.0 % | 不可 |
| **合計** | **11,010** | **252,311** | 100 % | 接客系 **48.5%** / 非接客系 **51.5%** |

→ **接客業種 6,985社(63.4%・従業者 48.5%)** は域内の `spend` から売上を得られるが、**`office`+`education` = 4,025社(36.5%)・従業者 129,872人(51.5%)は、域内のどの消費カテゴリからも1円も受け取れない**。IT(880社・44,538人)・専門技術(1,100社)・金融(220社)・不動産(990社)などは、案B で賃金だけが残高から出ていき、**必ず枯渇する**。
(この 51.5/27/14.5/7 の内訳は `conf/config.yaml:2098` のコメントおよび `docs/research/l2-work-reality.md` の設計値と一致する=台帳生成が設計どおりであることの追認)

**この 36.5% の解は RoW しかない、そしてそれは現実に正しい。** 渋谷のIT・専門サービス・金融の企業は、**顧客が渋谷の外に居る**。地域会計ではこれは「**域外への輸出**」であり(§2 の観光サテライト勘定と同じ論理を逆向きに適用)、RoW → org の受取として計上するのが標準。

しかも**受け皿は既に世界に存在する**: `_log_org_output`(`scheduler.py:422-461`)が勤務完遂ごとに `production` イベントを出し、同じ場所で `revenue_est = 日給 × revenue_margin` を積んでいる。**案B ではこの `revenue_est` を「漏れ」から「RoW からの輸出代金」へ格上げするだけでよい**——式も発火点も1つも変えず、**相手方を `void` から `rest_of_world` へ付け替える**。これで org 族の漏れ(mock org ON ランで漏れの 56.4〜78.2%)が**シムの挙動を1バイトも変えずに解消する**。

> **設計の帰結**: org の収入源は業種で2系統に分かれる。
> **(i) 接客業種 6,985社** = 域内 `spend` の受け手(§3-c の4段解決)。
> **(ii) office/education 4,025社** = `production` に紐づく **RoW からの輸出代金**(既存 `revenue_est` の式をそのまま使う)。
> ユーザーの「域外取引は**概念のみの実装でいい**」という決定は、この 36.5% を成立させるために**必須**であり、装飾ではない。

**c-4 の対応表の素案**(`spend.cat` → 台帳の産業大分類。件数は `docs/research/org-book-11k.md` 実測)

| `spend.cat`【実測の呼び出し元】 | 産業大分類 | 台帳の件数 |
|---|---|---|
| `food` / `cafe` / `nightlife` / `lodging`(`lodging.py`) | **FB** 宿泊業・飲食サービス業 | 1,650 |
| `shop` | **WR** 卸売業・小売業 | 3,080 |
| `leisure` / `free_*`(`services.py` の自由行動) | **LS** 生活関連サービス業・娯楽業 | 770 |
| `medical`(`scheduler.py:4278`) | **MW** 医療・福祉 | 440 |
| `taxi` / `bus`(`_charge_ride`) | **TR** 運輸業・郵便業 | 165 |
| `fixed_cost`(光熱費・サブスク) | — | **RoW**(域外のインフラ事業者。既定でここへ) |
| `venture` | — | venture(既存の保存経路。変更なし) |

**注(精度の落とし穴)【実測】**: 消費税は**内税**(`government.py:161-176`: 税額 = `price × rate/(1+rate)`)。買い手は `price` を払い、行政が `ct` を取るので、**売り手が受け取るべきは `price − ct`**。現行の venture は `sale` 全額を所有者へ渡しており(`tools.py:1644-1648`)、venture 部門が正味で `ct` だけマイナスになる。venture は残高を持たないので不可視だったが、**org は残高を持つので必ず露見する**。案B では `org.balance += amount − consumption_tax` とすること。

**`serve` はどうするか**: `serve` は**業務の実体の観測**(L2)であって会計ではない。会計を `_spend` 側で閉じれば、`serve` の役割は「誰が接客したか」に純化する。`revenue_est`(日給×margin)は**残す**(推定値として)が、新列 `revenue_actual` を並べて**両方を出す**(乖離30.9倍が縮むかを観測できる)。

---

### §3-d. 税の行き先 = 行政残高への一本化

**現状は既にほぼ正しい【実測】**: `Government.balance`(`government.py:86-90`)は ward/metro/nation の3レベルを持ち、`collect`/`expense` で増減し、**日次で `public_budget` イベントに (revenue, expense, balance) を出す**(`scheduler.py:3387-3392`)。`analyze_accounting` の検査①が「観測可能」と判定できる唯一の非家計部門。

案B で足すのは3点だけ:
1. **消費税の支払側が org になる**。現状 `resolve_tax_sources`(解析側)は `spend_destination(cat)` を源にしており、org 帰属が付けば自動で org→government になる。**シム側の変更は不要**。
2. **`rule_bonus` の財源化**(`rules.py:333`)。制度DSL の bonus が無から出ている。`gov.expense("ward", amt)` を1行足せば漏れが1族消える。**ただし行政予算が枯渇する挙動変化があるので独立トグル**。
3. **government OFF 時の罰金**(`scheduler.py:3795, 3857`)。現状 VOID。**RoW へ落とす**のが正しい(行政が存在しない世界では域外の徴収主体、と宣言する)。

**供託金 escrow との一本化(§3-e と接続)**: 議案供託(`tools.py:777`)・立候補供託(`tools.py:591`)・転居敷金(`scheduler.py:3602`)はいずれも「預かり金」で受け手が居ない。前2者は**行政の預り金**(`Government` に `escrow: dict[str,float]` を足し、`balance` とは別勘定にする)、敷金は**家主=RoW**が素直。

---

### §3-e. interest_paid・供託金・その他の単発主体

| 項目 | 現状【実測】 | 修正 | 規模 |
|---|---|---|---|
| **`interest_paid`** | `scheduler.py:3315` が `agent.account += itr` するだけ。`Bank.capital` は**減らない**=貨幣創出 | `bank.capital -= itr` の**1行** | 極小。ただし `Bank.capital` の既定が 0.0(`economy.py:583`)なので**マイナスに沈む**。`Bank` docstring は「最後の貸手=capital が負でも貸せる」と既に宣言しているので**理論的には整合**だが、初期資本を conf で与えるのが正直(`economy.bank.initial_capital` は既に存在する) |
| **議案供託 / 立候補供託** | 払込先が VOID。没収時のみ `gov.collect` | `Government.escrow` 勘定を新設(payer_id → 額)。払込=家計→行政escrow、返還=escrow→家計、没収=escrow→balance | 小。既に3フェーズ(paid/refund/forfeit)が payload に出ているので**解析側の写像だけで閉じる可能性もある** |
| **転居敷金** | VOID | RoW(不在家主) | 極小 |
| **窃盗 `crime(theft)`** | 被害者から減るだけ | 加害者へ入金 | **挙動変化あり**(加害者の消費余力が増える)。既定 OFF の独立トグル推奨 |
| **破産 `bankruptcy.seized`** | 消滅 | `Bank.write_off` と接続して銀行の回収へ、残りは RoW | 小。ただし `bank` OFF ランでは受け手が居ない → RoW |
| **`venture_open.cost`** | 消滅(30,000円/件) | **RoW(域外の内装業者・仕入)**。ユーザー決定「域外取引は概念のみ」の代表例 | 極小 |
| **`b2b_trade`** | `b2b.py:165-176` が帳簿 dict を動かすだけ | org 残高間の実移動(買い手 org の残高 → 売り手 org の残高)。**org が残高を持って初めて実装できる** | 中。`commerce.inventory.b2b.enabled` の既存トグル配下 |
| **`VCFund` / `Government` / `Bank` の checkpoint 不在** | `checkpoint.py` にキーが無い=resume で残高消失 | `runtime` ブロックへ3つとも追加(既存の `assets_state` と同流儀の `.get` 互換) | **案B の前提条件**(§4 バッチ0) |

---

### §3-f. RoW 部門 = 観光客の財布・域外仕入れ・域外通勤

**「概念のみの実装」の具体的な意味【推定+§2の文献】**: RoW は**残高制約を持たない吸収/放出部門**であり、実装としては
- **状態を1つも持たない**(残高変数すら持たない。持つとしても**観測用の累計カウンタ**だけ)、
- **意思決定を1つも持たない**(エージェントではない。LLM を呼ばない=**k 完全不変**)、
- **行列上の相手方ラベルとしてのみ存在する**。

これは §2 の地域 SAM 慣行(域外勘定に制約を課さない)と一致し、**Godley & Lavoie の取引フロー行列で「行と列がゼロになるよう最後の列が閉じる」役割**そのもの。

**RoW が担う本シムの5つの窓口**

| 窓口 | 既存の実装 | 案B での扱い |
|---|---|---|
| ① **来街者の財布**(観光客・買物客) | `wage(source=home_refill)` `scheduler.py:962-979`。来街者は **`split_account` で口座を持たない=現金のみ**(`economy.py:185-194`) | **RoW → 家計**。地域会計では「域内での観光客支出 = 域外への輸出」(§2)。**命名のみで既存挙動は不変** |
| ② **域外通勤者の賃金** | `agent.commute`(`agents/agent.py:23`)。ただし通勤者も**街の org に配属される**ので賃金は org から出る | 域内 org 発 → 域外居住者の消費は域外へ流出。**現状の `visitor` は域内で使い切る近似**。RoW への流出は将来課題(概念だけ宣言) |
| ③ **域外本社/域外資本の店** | 無し | **§3-c の三段解決の最終受け皿**。「受け手 org を特定できなかった消費」= 域外資本の店とみなす。**この解釈が案B の保存を無条件に閉じる鍵** |
| ④ **域外からの仕入れ** | `venture_open.cost`・`b2b` の川上端 | RoW → 家計/org の逆向きフロー(仕入=域内から域外への支払) |
| ⑤ **外生ショック** | `chance_event`(`chance.py:126,129`)・`reward`(`scheduler.py:1241`)・`spark`(`spark.py:240`) | 既に解析側で EXTERNAL 扱い。**RoW として正式に部門化**(ablation 装置であることを明記) |

**重要**: ①③⑤は**既に世界に存在するフロー**であり、案B の RoW 実装は**新しい金の経路を1本も足さない**。足すのは「相手方の名前」と「その額の観測」だけ。→ **`analyze_accounting.unclassified_money_kinds` の監視装置(新しい金の経路の検知)を発火させない**=既存の会計検査の網羅性が構造的に保たれる。

---

### §3-g. R1 との整合(既定OFF・golden・checkpoint/resume・25万スケール)

| R1 の要求 | 案B での満たし方 |
|---|---|
| **既定 OFF** | 新トグル `economy.org_accounting.enabled: false`(+ `rest_of_world.enabled: false`)。OFF では `_spend`/`_pay_wage` の追加分岐が一切走らない。**`registry.py` へ `_f(...)` 登録が必須**(`tests/test_registry_modes.py:91` `test_no_undeclared_toggles_in_shipped_config` が未登録の bool leaf で CI を落とす) |
| **golden 無風** | `tests/data/golden_baseline_l1.json`(15体×144step)とバイト一致。**先例どおり各レーンが自前で `test_off_matches_golden` を1本持つ**(`test_rumors.py:243` / `test_rejection_notify.py:256` / `test_traces.py` と同型)。org 残高の増減は L1 payload に出さない限り golden に触れない |
| **checkpoint / resume** | **最大のリスク**。org 残高は新しい可変状態 → `checkpoint.py` の `runtime` へ `org_balance`(dict)を追加。**同時に既存欠陥(`government`/`bank`/`vc_fund` 未保存)も塞ぐ**必要がある(塞がないと「org は resume で残るが行政は戻る」という非対称なバグになる)。`resume == straight` テストを新設 |
| **25万体スケール** | org 残高は **`dict[str, float]` × 11,010 エントリ**。メモリ ≒ 1MB 未満。`_spend` あたりの追加コストは **dict 参照1回**(node→org 表は起動時に1回構築して固定)。**O(1)/イベント**で、部門行列は §1 どおり O(部門²)=定数 |
| **k 不変(LLM 呼数)** | RoW も org 残高も **プロンプトに1文字も出さない**なら k は完全不変。**推奨=出さない**(段階1)。将来「自社の資金繰り」を経営者エージェントのプロンプトへ出すなら `affects_k` の再評価が要る |
| **決定論** | 初期残高(§3-a)・`(building,floor,POI種別)`→org 表(§3-c)ともに**乱数ゼロ**(台帳は事前計算データ)。`Bank`/`Government` と同じ遅延構築(`_gov`/`_bank` パターン)で `sim` にキャッシュ。候補が複数のときの単一先抽選(c-2B)だけが新 stream を1本使う |
| **`indoor` への依存** | **org 単位の売上帰属は `indoor.enabled: true` を事実上の前提とする**(§3-c 実測: 鍵に `floor` を入れないと一意率 4.8% → 入れると 58.8%)。ただし**依存を必須にはしない**: indoor OFF では `(node, POI種別)` へ縮退し、決まらない額は RoW へ落ちるので**保存は OFF でも閉じる**。落ちるのは精度だけで、それを L2 に開示する |
| **観察動線**(ユーザー要求) | §5 |

---

## §4. バッチ分解案(既定OFF・golden 無風の昇格経路)

**基本方針**: 「検査を先に、接続を後に」(Caiani の順序)は IF-E で既に済んでいる。案B は**閉じる漏れの族を1つずつ潰し、そのたびに `analyze_accounting` の漏れ比率が下がることを実測で固定する**。各バッチは単独で緑にでき、単独で revert できる。

| # | バッチ | 内容 | 閉じる漏れ族 | 規模(推定) | golden |
|---|---|---|---|---|---|
| **0** | **非エージェント残高の永続化**(前提工事) | `Government`/`Bank`/`VCFund` を `checkpoint.py` の `runtime` へ。`resume==straight` テスト新設。**org には触らない** | 0族(既存欠陥の修復) | 小(~150行・新テスト6本) | 無風(状態の保存であって挙動変化なし。ただし**resume 経路の L1 は変わる=これは修正**) |
| **1** | **RoW 部門の宣言**(概念実装) | `analyze_accounting` の `EXTERNAL` を `rest_of_world` として正式部門化 + シム側に `RestOfWorld` 観測カウンタ(残高制約なし)。`home_refill`/`chance`/`reward`/`spark` を登録。**シムの金の動きは1円も変えない** | 0族(命名) | 小(~200行・新テスト8本) | 完全無風 |
| **2** | **org 残高の新設 + 賃金の資金源**(案B の核①) | `sim.org_balance: dict[str,float]`(遅延構築・checkpoint 対象)。§3-a の初期化。`_pay_wage(payer_org=...)`。不足時 = **RoW 補填(既定)**。L1 に `org_pay`(または wage payload の追加キー)+ `rw_transfer` | **wage 族(mock org ON で漏れの 21.5%)** | 中(~400行・新テスト15本) | 無風(既定 OFF) |
| **3** | **spend の受け手解決**(案B の核②) | §3-c の4段(`(building,floor,POI種別)` 台帳表 → 候補が複数なら決定論配分 → node 縮退 → RoW)。`_spend` で受け手へ入金(**消費税控除後**)。段ごとの解決件数を L2 へ。**`indoor` OFF ランでは自動的に縮退経路へ落ち、精度低下を開示する** | **spend 族(実LLM ランで漏れの 74.3%・mock org ON で 12.8〜17.0%)** | 中〜大(~500行・新テスト18本) | 無風(既定 OFF) |
| **4** | **org 族の解消 = 域外輸出の計上** | `revenue_est`(既存の式・発火点とも不変)の相手方を `void` → `rest_of_world` に付け替える。`revenue_actual`(バッチ3 の実測)を org_ledger に並置し、乖離30.9倍の推移を観測。**非接客系 4,025社の唯一の収入源**(§3-c) | **org 族(mock org ON で漏れの 56.4〜78.2%)** | 小(~150行・新テスト8本) | 無風 |
| **5** | **単発主体の始末** | `interest_paid` の `bank.capital -= itr`(1行)/ 供託 escrow / 敷金・出店費・罰金 OFF 時 → RoW / `rule_bonus` の財源化 | **tax・rent・deposit・candidacy・move_home・venture_setup_cost 族** | 小〜中(~300行・新テスト12本) | 要注意(`interest_paid`・`rule_bonus` は既定 ON 経路に触る → **既定 OFF トグルの下に置く**) |
| **6** | **検査①の全部門成立**(受入条件) | org/bank/RoW/government 残高を L2 サイドカーへ(§5)。`analyze_accounting` の `UNOBSERVABLE_REASON` を全部消す。既存の**現状固定テスト2本を反転**(下記) | — | 中(~350行・新テスト14本) | 無風 |
| **7**(任意) | **倒産機構**(観察動線の本命) | `economy.org.insolvency: bankrupt` で残高<0 → org 閉鎖 → 従業員解雇 → 既存 `career`/`switch_org` へ接続。L1 に `org_bankrupt` | — | 大 | 無風(既定 `rescue`) |
| **8**(任意) | **B2B の実移動** | `b2b.py` の帳簿 dict を org 残高へ接続 | b2b の名目性 | 中 | 無風 |

**合計見積り(推定)**: バッチ0〜6 で **本体 ~2,000行・新テスト ~80本**(現行 3,222 → ~3,300)。バッチ7〜8 を含めると ~2,800行・~110本。

**必ず更新が要る既存テスト(「現状固定」テストの反転)【実測】**:
- `tests/test_accounting.py:486` `test_measured_leak_families_are_closed_under_the_known_list` — 493-494行が「既知の漏れが**まだ存在すること**」を assert している。バッチ2以降で意図的に落ちる。**同じコミットで更新すること**(`KNOWN_LEAK_FAMILIES` :394 / `KNOWN_LEAK_FAMILIES_ALL` :403 の縮小として書くと差分が読みやすい)。
- `tests/test_accounting.py:505` `test_measured_revenue_est_is_disconnected_from_customer_spend` — テスト本文が既に「接続が実装されたなら本テストを更新すること」と明記。
- `tests/test_accounting.py:517` `test_measured_leak_share_is_large_and_dominated_by_multiple_paths` — 「漏れが単一経路に一意帰着している(=フェーズ2の接続条件が満たされた)」で落ちる設計。
- `tests/test_accounting.py:497` `test_measured_no_unclassified_money_carrying_kind` — **新しい金を運ぶ L1 種を足した瞬間に落ちる**。`MONEY_KINDS`(`analyze_accounting.py:126`)へ追加が必須。**これは監視装置として正しく機能している証拠なので、落ちたら喜んで追加する**。
- `tests/test_org_data.py:112, 136` — `unstaffed_unique` / `ambiguous_null` の現行 node→org 解決セマンティクスを固定。バッチ3で台帳由来の解決に替えるなら更新。

**受入条件(案B 完了の定義)**: `python scripts/analyze_accounting.py runs/<mock org ON ラン>` で
(i) **`leak_share` < 0.01**(丸め誤差のみ)、(ii) **`checks` の全部門が `observable: true`** かつ相対残差が `rel_tol` 以内、(iii) `void` 行・列の絶対額 = 0、(iv) golden バイト一致 + `resume == straight`。

---

## §5. 観察動線(ユーザー設計思想「活動を観察できる動線をしっかり」)

**原則**: 記録と動力学の分離(`observer/indoor_tracks.py` と同じ設計原則③)。**動力学は残高を動かし、観測層はそれを読むだけ**。`tests/test_indoor_invariance.py` の静的検査③がこれを機械的に強制する。

### 5-1. L1(イベント = 何が起きたか)

| 新 kind | 発火 | payload | 目的 |
|---|---|---|---|
| `org_pay` | org が賃金を払った | `{org_id, amount, balance, n_workers}` | 「会社が人にいくら払ったか」 |
| `org_revenue` | org が売上を受け取った | `{org_id, amount, balance, cat}` — **高頻度なので日次集計に畳むのが現実的**(§5-2) | 「会社にいくら入ったか」 |
| `rw_transfer` | 域外との資金移動 | `{direction: in\|out, reason: home_refill\|unknown_payee\|rescue\|procurement\|escrow\|shock, amount}` | **「街が域外にどれだけ依存しているか」= 案B 固有の新しい研究量** |
| `org_rescue` | 支払不能で RoW 補填が発生 | `{org_id, shortfall, balance_before}` | 支払不能の可視化(倒産 OFF でも「危なかった」が見える) |
| `org_bankrupt`(バッチ7) | 残高<0 で閉鎖 | `{org_id, n_dismissed, debt}` | 倒産 → 失職 → 転職の連鎖の起点 |

`schema.py` への `register_event_kind` 呼び出し1行ずつ(`observer/schema.py:11-14`)。**すべて既定 OFF のトグル配下**なので golden は無風。

### 5-2. L2(サイドカー = 誰がどれだけ持っているか)

**検査①が全部門で成立するための最小要件**は「**各部門の期首残高と期末残高が観測できること**」。現状 `UNOBSERVABLE_REASON`(`analyze_accounting.py:117-123`)が挙げる4部門を潰す:

| 部門 | 現在の理由 | 潰し方 |
|---|---|---|
| `org` | 「revenue_est/wage_paid の集計のみで残高列を持たない」 | **`org_ledger.parquet` に列追加**: `balance_open, revenue_actual, wage_out, rw_in, rw_out, balance_close`。**注意: このスキーマは会社UIタスク B7 が読む契約**(`observer/org_ledger.py:12-21` に「厳守」と明記)。既存7列は順序含め不変にし、**末尾に追加**する |
| `venture` | 「sales_total だけ・通過部門」 | 屋台は**通過部門のままでよい**(売上は即座に店主=家計へ)。ただし消費税分(§3-c 注)を精算すれば行/列が厳密に閉じる |
| `bank` | 「Bank.capital / VCFund が L1・L3 のどこにも出ない」 | **新サイドカー `finance.parquet`(日次1行)**: `day, bank_capital, bank_loans_outstanding, bank_write_offs, vc_balance, vc_invested, gov_ward, gov_metro, gov_nation, gov_escrow, row_in, row_out`。1日1行 × 100日 = 100行の極小ファイル |
| `external`(→`rest_of_world`) | 「定義上の無限の源/シンク」 | **残高は持たないが累計は出す**。上の `row_in`/`row_out` が「域外依存度」の時系列になる |

**L2 集計列(既存の `@register_aggregator` パターン)**: `observer/aggregate.py` の慣行(OFF なら `None` を返して列を出さない=L2 バイト不変)で、`org_balance_mean` / `org_insolvent_count` / `row_dependency`(= 当 step の RoW 流入 ÷ 総フロー)を足す。

### 5-3. 解析(`scripts/analyze_accounting.py` 側)

- **読み取り専用の掟は維持**(`analyze_accounting.py:21-24`: シム本体を呼ばない・乱数を引かない・依存は標準ライブラリ+pyarrow)。
- `EXTERNAL` を `rest_of_world` へ改名し、`SECTORS` に残高観測を追加。`conserve_*` を **6部門すべてに対して**書く(現在 household と government のみ)。
- **`void` 部門は消さない**。「相手方が存在しない金」を検知する装置として残し、**額が 0 であることをテストで固定する**(装置を残したまま値をゼロにするのが、検査の網羅性を将来にわたって守る唯一の方法)。

### 5-4. 人が見る動線(ユーザー要求「観察できる動線」)

1. **1社の一生**: `org_ledger.parquet` を org_id で引くと、日次で「入った金・出た金・残高」が並ぶ → 会社UI(B7)の既存動線にそのまま乗る。
2. **街全体の資金循環**: `analyze_accounting.py` の出力 markdown が**部門間フロー行列**を印字する(既存)。案B 後は `void` が空になり、**代わりに `rest_of_world` 行/列に「域外依存」が数字で立つ**。
3. **個人 → 会社 → 個人の追跡**: `spend`(誰が払った)→ `org_revenue`(どの会社が受けた)→ `org_pay`(その会社が誰に払った)が **org_id で繋がる**。これが「範囲内の取引なら個人と企業・組織が存在するので観察できる」というユーザー要求の実体。
4. **危機の可視化**: `org_rescue` / `org_bankrupt` が「どの会社がいつ危なくなったか」を時系列で残す。

---

## §6. リンク集(アクセス日 = 2026-08-06)

### SFC-ABM(企業の会計主体化)
- **Caiani, A., Godin, A., Caverzasi, E., Gallegati, M., Kinsella, S. & Stiglitz, J. E. (2016)** "Agent based-stock flow consistent macroeconomics: Towards a benchmark model", *Journal of Economic Dynamics and Control* 69:375-408.
  本文PDF(全34頁を抽出して §3.1.5 / §3.1.6 / §3.3 / §5.2 を精読): https://business.columbia.edu/sites/default/files-efs/imce-uploads/Joseph_Stiglitz/Agent%20based-stock%20flow.pdf
  ScienceDirect: https://www.sciencedirect.com/science/article/abs/pii/S0165188915301020 / SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2664125
  別ホスト版(SIE): https://www.siecon.org/sites/default/files/oldfiles/uploads/2015/10/Caiani.pdf
- **Godley, W. & Lavoie, M. (2007)** *Monetary Economics: An Integrated Approach to Credit, Money, Income, Production and Wealth*, Palgrave Macmillan.(取引フロー行列の原典。開放経済は第6章 OPEN モデル/第12章の2国モデル) https://link.springer.com/book/10.1007/978-1-137-08599-3
- **Basu, N., Pryor, R. & Quint, T. (1998)** "ASPEN: A Microsimulation Model of the Economy", *Computational Economics* 12(3):223-241.(Sandia。大規模 ABM に銀行システム+債券市場) https://ideas.repec.org/a/kap/compec/v12y1998i3p223-41.html / OSTI: https://www.osti.gov/biblio/399684
- 既存の本リポジトリ内リサーチ(EURACE / Delli Gatti / CATS の信用回路・倒産雪崩): `docs/research/economy-abm-research.md` §1
- 既存の本リポジトリ内リサーチ(Caiani 検査2本の移植・25万体での部門別行列): `docs/research/if-lane-research.md` §5

### 地域会計と域外部門
- **Social accounting matrix** の構造と均衡規約(行=列、"Rest of Economy" 勘定): https://en.wikipedia.org/wiki/Social_accounting_matrix
- 地域 SAM で RoW を「rest of the nation」と「rest of the world」に分ける慣行(東アジア地域間 SAM 構築マニュアル): https://www.researchgate.net/publication/387739744_Construction_of_An_East_Asia_Inter-_regional_Social_Accounting_Matrix_A_Manual
- 多地域 SAM と乗数分析(地域間の資金の leakage): http://etd.lib.metu.edu.tr/upload/12613566/index.pdf
- FAO『Social Accounting Matrix (SAM) for analysing agricultural and rural development』(地域 SAM の実務): https://openknowledge.fao.org/server/api/core/bitstreams/9afdc700-0666-4f76-b3ed-56dc353d0da5/content
- **Tourism Satellite Account: Recommended Methodological Framework 2008**(国連/UNWTO。非居住者の域内消費の計上): https://unstats.un.org/unsd/publication/SeriesF/SeriesF_80e.pdf / https://www.e-unwto.org/doi/book/10.18111/9789211615203

### 他シミュレーションの域外・貨幣供給設計
- **Cities: Skylines** 公式Wiki "Supply chain"(outside connections = 制約なしの供給源/吸収先。**輸出入は市の予算に計上されない**=金が閉じていない反面教師): https://skylines.paradoxwikis.com/Supply_chain
- Cities: Skylines Dev Diary 5 "Outside Connections": https://cslcentral.tumblr.com/devdiaries/5
- **Lehdonvirta, V. & Castronova, E. (2014)** *Virtual Economies: Design and Analysis*, MIT Press.(faucet/sink による貨幣供給の設計と管理) https://mitpress.mit.edu/9780262535069/virtual-economies/
- Castronova, E. (2002) "On Virtual Economies"(CESifo WP 752): https://www.econstor.eu/bitstream/10419/76069/1/cesifo_wp752.pdf
- "Market Interventions in a Large-Scale Virtual Economy"(大規模仮想経済への介入の実証): https://arxiv.org/pdf/2210.07970

### 本リポジトリ内の一次資料(実装・実測)
- 検査スクリプト(漏れの実測・部門定義・分類器): `scripts/analyze_accounting.py`(docstring 1-89行に第95バッチの実測3ラン)
- 検査テスト39本(現状固定テストの所在): `tests/test_accounting.py`
- 組織台帳 11,010社の生成レポート(産業・規模帯の分布): `docs/research/org-book-11k.md`
- 台帳の実体: `data/organizations_shibuya_wide11k.json`(本書 §3-c の一意性測定はこのファイルの全数集計)
- L2 業務の実体(接客27%/対人14.5%/飲食7%/オフィス51.5%の設計値): `docs/research/l2-work-reality.md`
- 判断台帳: `PENDING.md:13`(IF-E2 案B)・`PENDING.md:42`(2026-08-06 の決定行)


---

## §4. 補遺 — 委任調査の完全報告(2026-08-06 到着分・主導執筆停止後)からの確定事項

主導エージェント停止後に委任先2本(RoW/LLM経済シム調査・SFC-ABM企業会計調査)の完全報告が到着した。本文と重複しない確定事項のみ追記する。

### §4-1. RoW の規範的設計(一次検証済み)
- **SNA 2008 §26.2/26.5/26.6(逐語確認)**: RoW は「あたかも国内のもう一つの部門であるかのように」記帳し(§26.2)、RoW が受け取った財・サービスを内部で何に使うかは**記録しないと標準自身が明言**(§26.5)、RoW 勘定には勘定別バランス項目を置かない(§26.6)。= **「行動方程式なし・残高制約なしの明示部門」は国際統計標準そのもの**。
- **Zezza (2026) OPENSIMPLEST(Levy WP 1105・逐語確認)**: 「**residual RoW column が会計構造に無いこと**」を欠陥として名指し。= 案C/案Bの RoW は「不在」ではなく**明示の名前付き列**でなければならない。
- **検査の空虚化防止(設計上の要点)**: 何でも吸収する RoW はゼロ和検査を空虚に通す。防止策=(a) 吸収をチャネル別に分類(域外居住者への賃金/域外仕入れ/来街者の財布補充=**輸出**(IRTS 2008 §4.21+SNA §9.80)/利益送金)(b) **Σ(全主体残高)+RoW 累積=一定** の閉じた不変量をテスト固定 (c) RoW 累積残高を L1/summary の一級市民として公表。前例=OPENSIMPLEST の NIIP・ポスト自動化ABM(arXiv 2606.20649)の machine-precision 検査。
- **通勤流出は正常な統計**: Eurostat 地域家計所得統計(逐語確認)=ブリュッセルの域内発生所得のうち**約62%が域外へ**(primary income/GDP 38.2%)。渋谷の賃金流出は「バグ」ではなく公表される通常の地域統計の形。

### §4-2. 最小限の企業会計(一次検証済み)
- **スカラー預金1本の前例=Lengnick 2013(LEN)**。Dawid & Delli Gatti (2018) の比較表で **LEN は Stock-flow consistent = Y と分類**。同章脚注70(逐語)=「**労働のみで生産する企業なら、流動性 M は賃金支払のみを賄う: M = wN**」→ 資産側はスカラー1本で会計的に十分という公刊された明示言明。
- **ゼロ和検査の2系統**: フル行列(Caiani §5.2)と**スカラー総マネー保存**(伊中銀 ABCredit.jl の test/stock_flow_consistency.jl=`isapprox(init_money, tot_money, atol=1e-5)` を100step回すだけ・Mark-0 の S+ΣE=M)。**25万体では後者が実用**(331Mエージェントの Gill et al. 2021 ですら企業会計は「銀行支店へのスカラー預金」)。
- **支払不能規約の5分類**: 最頻出=**自動当座借越+利息**(Poledna/Mark-0/CATS)。最も洗練=Poledna の **AND 条件**(D<0 は許容=有利子当座借越・**D<0 かつ E<0 の同時成立でのみ破綻**=資金繰りと債務超過の分離)。Lengnick は賃金按分カット(唯一)。
- **初期資本**: Caiani=**σ×賃金支払1期分(σ=1)**。Poledna=国民経済計算から機械配分(規模はべき分布指数−2)。
- **新規性主張(確度=中〜高)**: LLM ベース社会/経済シムで**システム全体の貨幣保存監査を実装した例は「見つからなかった」**(EconAgent=企業不在で消費の受け手なし・SimCity=検査なし・Concordia=保存は LLM への提案文であって検査でない・AI Economist=建築コインを「モデル外の経済から来る」と明示宣言=本シムの RoW と同型)。書き方は「we found none」(金融シム系サーベイ1本が有料壁で未読のため)。

### §4-3. 実装への確定ディレクティブ(§3 の設計を上書き・確定)
1. org 残高=**スカラー預金1本**(`org.deposit`)。複式簿記なし(Lengnick 前例)。初期値=σ×月次賃金支払(σ は conf・既定1)。
2. 賃金=org 残高から支払。不足時=**自動当座借越(残高が負に振れるのを許す)**+L1 `org_overdraft` 記録。**破綻処理は本選前は入れない**(概念のみ=Poledna AND 条件を将来の拡張として docstring 宣言)。
3. spend/serve の受け手解決=IF-E の突合鍵を流用(スタッフ経由が主・多義 node は RoW 帰属で正直開示)。
4. **RoW=明示部門**(`sim.row_balance`)。チャネル別分類(§4-1)+閉じた不変量テスト+累積残高を summary/L2 サイドカーへ。来街者の財布補充=RoW からの輸出フローとして記帳。
5. 税=既存 public_budget へ一本化。interest_paid=Bank.capital 減で対称化。供託金=行政 escrow。
6. 検査=既存 analyze_accounting.py の部門別行列に org/RoW 列を追加+**スカラー総マネー保存テスト**(ABCredit 流)を tests に常設。

## §5. バッチ分解(実装計画)

| # | 内容 | 規模 |
|---|---|---|
| E2-1 | org 残高+賃金/売上の記帳+当座借越(`economy.org_accounting.enabled: false` 既定)+初期化 σ | 中 |
| E2-2 | RoW 部門(チャネル分類・不変量・来街者財布=輸出)+税/利息/供託金の対称化 | 中 |
| E2-3 | 観測動線: org/Bank/RoW 残高の L2 サイドカー+analyze_accounting 拡張(検査①が全部門で成立)+保存則テスト常設 | 小〜中 |

検収条件: 既定 OFF=golden バイト一致・ON で総マネー保存 atol 検査緑・resume==straight・25万スケールの計算量は O(取引数) のみ(行列は部門別)。
