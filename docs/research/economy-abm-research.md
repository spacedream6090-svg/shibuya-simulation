# 経済の深化に向けた調査 — ABM経済回路・LLM経済エージェント・与信/VC・日本の消費と決済

> 目的: 渋谷シミュ(200-300体・1step=10分)の経済に **銀行(預金/融資)・VC/出資・決済手段・
> 消費行動の構造** を足すための実装根拠。ユーザー方針=「自然界のような仕組み(中央制御でなく
> 局所ルールから創発)」+ 観察目標「**組織の自然形成とファウンダーの成立条件**」。
> 現状の実装(既実装): 賃金・消費(spend)・税(源泉/住民/消費)・動的価格・在庫/品切れ・
> 立退き/破産・固定費・口座(現金/カード/ATM)・キャリア転換(失業/転職/起業転換)。
> 取得日: 2026-07-19(WebSearch/WebFetch)。**一次資料が PDF バイナリ/JS描画で静的取得できなかった
> 箇所は二次資料の値+オーダーで代替し、その旨を明記**(実数と偽装しない)。数値は出典つき。
> 本ドキュメントは調査のみ。コード変更は含まない(実装は別バッチ・**既定 OFF** 前提)。

---

## 0. 既存モジュールの見取り図(写像の宛先)

写像案が指す既存のフックを先に整理する(この街の経済はここに閉じている)。

| 領域 | ファイル | 要点 |
|---|---|---|
| 賃金・価格・口座 | `src/society/economy.py` | `build_economy`(wages/prices)、`build_accounts_cfg`(**預金 account・card_threshold・ATM・立退き eviction・破産 bankruptcy が既に存在**)、`build_career_cfg` |
| 金の流れ | `src/society/engine/scheduler.py` | `_pay_wage` / `_spend`(card 閾値で現金↔口座を分岐)/ `_settle_work` / 月次 payday・家賃引落フェーズ / `_atm_withdraw` |
| 起業(観察の核) | `src/society/tools.py` | `open_venture`(venture に `sales_total`・`fulltime`)、`buy_prob`、`_ventures_fulltime` |
| 組織 | `src/society/organizations.py` | `org_ledger`(売上集計)、`go_fulltime_venture`(起業転換)、`is_employee` |
| 需要の観測量 | `src/society/commerce.py` | `occupancy(node)`(在館数=足元の需要/人流。**VC の「市場」代理に流用可**) |
| 行政会計 | `src/society/government.py` | `Government`(ward/metro/nation の残高・`collect`/`expense`)。銀行会計の雛形に流用可 |
| 関係網 | `src/society/relations.py`, `agent.mem.relations` | 中心性(次数)= VC の「ネットワーク」代理 |
| 乱数 | `src/society/rng.py` | `sim.hub.stream(用途, id, step)` = **新 stream は既存 draw 順を乱さない**(R1/ゴールデンの要) |
| ログ種 | `src/society/observer/schema.py` | `register_event_kind("kind", "説明")` を1行足すだけで新イベント種を追加できる |

**R1 の鉄則(全モジュール共通)**: 追加機構は `generate()`(LLM呼び出し)を1本も足さない。
非LLM=ルール+決定論+新 stream で閉じる。既存の career/commerce/government はすべてこの流儀で
「呼数不変・OFF=バイト一致(ゴールデン `golden_baseline_l1.json` を守る)」を実現している。

---

## 1. ABM経済の標準設計(EURACE / Delli Gatti / CATS)の bank–firm–household 回路

### 要点
- **Delli Gatti ら『Macroeconomics from the Bottom-up』**(2011, Springer): マクロ経済を「単純で
  経験的に妥当な rule of thumb に従って適応・自律行動する異質な相互作用個体の複雑系」として
  ボトムアップに組む。関心の中心は**企業と銀行の財務脆弱性(financial fragility)が景気変動を生む**こと。
- **ネットワーク型 金融アクセラレータ**(Delli Gatti et al. 2010): 経済を3部門
  (川下企業・川上企業・**銀行**)が「生産関係+信用関係」で結ばれたネットワークとして表す。
  企業の**レバレッジ(負債/純資産)を倒産確率の代理**に置く。ある企業が破綻すると、その取引先
  (川上)と貸手(銀行)が損失を被る。銀行が生き残っても**信用供給を絞り・全借手の金利を上げる**
  (credit rationing)ので、**小さなショックが倒産の雪崩(bankruptcy avalanche)へ増幅**する。
  借手による貸手/取引先の選択がネットワーク構造を進化させる。
- **EURACE / EURACE@Unibi**(Cincotti–Raberto–Teglio / van der Hoog–Dawid): 企業も家計も貨幣を
  **銀行預金として保有**(現金でなく)。非金融主体間の取引はすべて**銀行間取引**に翻訳される。
  日次で各主体が流動資産を銀行に通知し、銀行間で純差額を清算、準備が負なら**中央銀行が貸す
  (最後の貸手)**。景気循環は「実体活動 × その信用による資金調達」の相互作用から**内生的に**生じ、
  企業が借入制約を強く受けるほど循環の振幅が増す。EURACE@Unibi は倒産処理と信用市場金利を精緻化。

### 数百体規模での簡略化(そのまま流用できる「信用回路」骨格)
1. **資金需要**: 企業(=この街では venture 所有者)が、内部留保(手持ち)で固定費・仕入を賄えない
   **資金ギャップ**のときだけ借入を申請する(常時借りない)。
2. **与信/金利**: 銀行は**企業別金利 = 基準金利 + リスクプレミアム(レバレッジ増で上昇)**。
   銀行資本比率(Basel 的な床)が binding のとき **credit rationing**(貸さない)。
3. **倒産**: 純資産<0 で破綻 → 貸手銀行の資産に貸倒(write-off)。破綻が**貸手経由で伝播**する。
4. スケール圧縮: 上流/下流の二層を作らず「venture 所有者 ↔ 単一銀行 ↔ 預金者(全員)」の
   一層でも雪崩の本質(貸手を介した連鎖・信用引締め)は再現できる。

### シミュへの写像案 → **E-W1(銀行)**(詳細は §7)
- **`economy.py` の `build_accounts_cfg` を拡張**: 預金(`agent.account`)は既存。ここに
  `agent.debt`・信用スコア・貸倒フックを足す。「預金として保有」は口座 E5 の思想と一致済み。
- **`government.py` の `Government` を雛形に `Bank` 会計主体**(残高・貸出・貸倒)を遅延構築
  (`scheduler._gov` と同型の `_bank`)。中央銀行=最後の貸手は「銀行残高が負なら nation 予算が補填」で近似。
- 倒産連鎖は**既存の破産サイクル(accounts の `bankruptcy_days`/`eviction_days`)に接続**する
  (借入返済の滞納 → 既存の破産処理 → venture 強制閉店 `force_close_venture` まで一直線)。

### 出典
- Macroeconomics from the Bottom-up (Springer): https://link.springer.com/book/10.1007/978-88-470-1971-3
- JASSS 書評(モデルの位置づけ): https://www.jasss.org/14/4/reviews/8.html
- The financial accelerator in an evolving credit network (Delli Gatti et al. 2010, JEDC): https://www.sciencedirect.com/science/article/abs/pii/S0165188910001491
- Business fluctuations and bankruptcy avalanches in an evolving network economy: https://link.springer.com/article/10.1007/s11403-009-0054-x
- Credit Money and Macroeconomic Instability in EURACE (Cincotti–Raberto–Teglio): https://www.degruyter.com/document/doi/10.5018/economics-ejournal.ja.2010-26/html ・ SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1753514
- The Eurace@Unibi Model (van der Hoog): https://yildizoglu.fr/macroabm1/docs/vanderHoog-Eurace.pdf

> 注: **CATS**(Complex Adaptive Trivial System; Gaffeo–Delli Gatti–Desiderio–Gallegati「Adaptive
> microfoundations for emergent macroeconomics」)は労働・財・信用の分散市場を探索/マッチングで回す
> 系譜。上記ネットワーク雪崩論文と同一著者群で、信用回路の連鎖倒産の設計思想は共通。CATS 単独の
> 静的取得できる一次 URL を今回確認できなかったため、検証できた上記論文群を典拠とする(実数と偽装しない)。

---

## 2. LLMエージェント経済の先行(何をLLM/何をルールに割るか・既知の失敗)

### 要点
- **EconAgent**(Li et al., ACL 2024。家計マクロ): **LLM が毎月決めるのは2つだけ** —
  ①**労働意欲 propensity(0〜1)** ②**消費性向 propensity(0〜1、貯蓄+所得のうち使う割合)**。
  それ以外の**マクロ環境はすべてルール/方程式**:
  - 賃金: 需給不均衡 φ=(D−G)/max(D,G) から w←w(1+φ) で調整(フィリップス曲線的)。
  - 税/再分配: **累進所得税(2018 米連邦ブラケット)+ 全員均等再分配**。
  - 物価: P←P(1+φ) で財価格が需給から変動(インフレ)。
  - 金利: **テイラー則** r=max(rⁿ+πᵗ+απ(π−πᵗ)+αu(uⁿ−u),0)。
  - 失業: 非労働者比率の年平均。
  - Perception / Memory(過去経験と市場動態の反省)/ Action の3モジュール。基盤は AI Economist / Foundation。
  - **既知の限界**(論文が明記): 家計しかモデル化せず**企業エージェント不在**、再現できるのは
    stylized facts のみで**正確な予測は不可**、微妙な政策変化への**行動応答が過度に鈍い/要精緻化**、
    LLM 推論コストで**都市規模に届かない**。
- **AgentSociety**(Piao et al. 2025, 清華): **1万体超**の LLM 個体・500万相互作用。職場・世帯・店・
  交通・公共空間・SNS を備えた仮想社会。個体は目標/感情/記憶/推論を持つ。並列エンジンで社会・
  経済行動を生成。→ この街と最も近い「LLM 都市社会シミュ」。
- **TwinMarket**(2025, CUHK-Shenzhen/南京大): **最大1000体**の LLM 投資家が売買判断+SNS で相互作用。
  **バブル・急変・情報カスケード(オピニオンリーダーが増幅)**が創発。ルールベース ABM の
  単純化を批判し、LLM で認知バイアス/感情を入れる立場。

### 設計原則の含意(この街の分業)
- **LLM = 主観的判断・性向・質的意思決定**(働くか/買うか/起業するか、造語・提案の内容)。
- **ルール/方程式 = 市場清算・会計・価格・税・金利・与信の「物理」**。銀行/VC の判定は**ルール側**に
  置くのが先行研究の共通解 = **R1(LLM呼数不変)と両立**する(既存 tools/rules/government と同じ流儀)。
- 既知の失敗を this-sim へ移すと: ①LLM は**マクロ変数に鈍い/貨幣錯覚**→ 経済判断を LLM に委ねすぎない、
  ②**一貫性の欠如**→ memory+reflection で補う(既実装の reflect と整合)、③SNS を入れると**群集/バブル**が
  出やすい(既実装の opinion/SNS と要注意)、④**compute 天井**→ 経済回路は非LLMで軽く保つ。

### シミュへの写像案
- 銀行の与信・VC の出資判定は**非LLM の決定論スコア関数**にする(§3・§4・§7)。LLM は既存の
  `open_venture`/`propose` のように「起業する/しない」の**発火**だけ担い、資金供給側はルールが評価する。
- 観察目標「ファウンダーの成立条件」は、**LLM 発火(起業意図)× ルール評価(資金がつくか)**の
  交差として自然に立ち上がる = EconAgent 流(propensity は LLM・環境はルール)の踏襲。

### 出典
- EconAgent (ACL 2024): https://aclanthology.org/2024.acl-long.829/ ・ arXiv: https://arxiv.org/abs/2310.10436 ・ コード: https://github.com/tsinghua-fib-lab/ACL24-EconAgent
- AgentSociety: https://arxiv.org/abs/2502.08691 ・ コード: https://github.com/tsinghua-fib-lab/AgentSociety
- TwinMarket: https://arxiv.org/abs/2502.01506

---

## 3. 与信・信用スコアの最小実装(標準形+マイクロファイナンス)

### 要点
- **信用判断の標準枠 = 5 C's of credit**: **Character**(返済履歴・評判)、**Capacity**(所得対返済比 DTI)、
  **Capital**(資産・純資産)、**Collateral**(担保)、**Conditions**(景況)。最小スコアはこの重み付き和。
- **マイクロファイナンスの credit scoring**(Accion 実務ツール): 使う変数は**属性・借入額・返済頻度
  (週/月)・残高・返済回数・延滞日数(days in arrears)**。初期モデルは**線形/ロジスティック回帰**で
  **デフォルト確率 PD** を出す。
- **グループ融資/連帯保証(グラミン型)**: 物的担保でなく**社会的担保**。ピア圧力+地域情報が
  情報の非対称を克服し**返済率を上げる**。返済成績の決定要因=制度設計・グループ内リスク分散・
  **社会的結束(social cohesion)**。空間ランダム効果を入れるとデフォルト予測が改善。

### 最小の関数形(この街用)
```
score = w1·norm(income_history) + w2·norm(assets/net_worth)
      + w3·norm(repayment_record) − w4·norm(days_in_arrears)   # 5C を4項に圧縮
PD    = 1 / (1 + exp(score))                # ロジスティック(倒産確率の代理)
approve  ⇔ score ≥ θ                         # 与信可否(客観条件のみ = R1: k非依存)
rate     = base_rate + premium·(1 − norm(score))   # レバレッジ/低スコアで金利上昇(§1)
```
- **社会的担保を this-sim に写す**: グループ融資 → **既存の `found_group`/`member_of` を連帯保証集団**に
  流用(グループ成員がいると score にボーナス)= 「街のつながりが与信を生む」局所ルール(創発的)。

### シミュへの写像案 → **E-W1 の与信部**
- `income_history` = 既存 **`agent.period_income`**(前回家賃日からの入金累計=月収相当)を使う。
- `assets` = `agent.money + agent.account`。`repayment_record`/`days_in_arrears` = 既存の
  **家賃滞納/破産サイクル(accounts)の滞納日数**を再利用。→ **新規状態はほぼ不要**、既存量の合成で組める。
- スコアは**決定論(乱数なし)**。承認閾値・金利は `economy.bank` の config 値(§7)。

### 出典
- Accion「Credit Scoring」リスク管理ツール(2024更新。使用変数の実務解説): https://www.accion.org/wp-content/uploads/2024/01/Risk-Tool-3_Credit-Scoring_Jan-2024.pdf
- A Machine Learning Approach for Micro-Credit Scoring (MDPI Risks): https://www.mdpi.com/2227-9091/9/3/50
- A Credit Scoring Model for MFI under Basel II: https://ideas.repec.org/a/ris/joefas/0017.html

---

## 4. VC/エンジェル投資の判定要素 → シミュ観測可能な代理変数への写像

### 要点(シード投資の実務判断軸)
- **チーム(最重要・最早期)**: 実行力、創業者の実体験・胆力(grit)・粘り(resilience)。
- **トラクション**: 動く製品・初期売上(MRR)・パイロット契約・成長の兆し。
- **市場**: TAM(狙える市場規模)。ベンチャー規模(概ね $10B+)を好む。
- **プロダクト検証**: 実ユーザーのいる MVP・需要の実証。
- 規模感: **エンジェル** $25k–100k(個人・人脈と知見)/ **シード VC** 1社$500k–2M(機関投資)。

### 観測可能な代理変数への写像(この街で既に測れる量)
| 実務の判断軸 | この街の代理変数(既存の観測量) | 取得元 |
|---|---|---|
| チーム/創業者の質 | **効力感 efficacy・grievance**、過去の venture 累計売上、勤務完遂の一貫性、org 役割 | `agent.states`, `venture.sales_total` |
| トラクション | **venture 累計売上 `sales_total`**・売上頻度(`venture_sale` 件数)・生存日数 | `tools.py` の venture |
| 市場(需要規模) | **出店ノードの在館数 `commerce.occupancy(node)`**(人流=足元需要)・カテゴリ需要 | `commerce.py` |
| ネットワーク/社会資本 | **関係網の中心性(`agent.mem.relations` の次数)**・グループ所属・SNS リシェア到達 | `relations.py`, `net` |
| 創業者の確信/動機 | **grievance/効力感**(世界を変える駆動源) | `agent.states` |

→ 実務の「チーム・トラクション・市場」は、それぞれ **効力感 × 売上履歴 × 人流/中心性**に素直に対応する。
**すべて既に観測している量**なので、VC 判定は「これらの重み付きスコアが閾値超で出資」という**決定論
ルール**で組める(新たな LLM 審判は不要 = R1)。

### シミュへの写像案 → **E-W2(VC/出資)**(詳細は §7)
- VC を**中央制御でない「局所の資金供給者(institution/agent)」**として置く。定期(review_period)に
  **開店中の全 venture をスコアリング**し、閾値超の上位に資金注入。資金は `owner.account` に入り、
  **既存の起業転換 `go_fulltime_venture` を早める**(=ファウンダー成立を観察)。
- 観察目標「**ファウンダーの成立条件**」= どの agent が「起業意図(LLM)× 売上/人流/中心性(ルール)」の
  交差で資金を得て本業化するか、を `venture_fulltime`+新 `investment` イベントで追跡できる。

### 出典
- What VCs Look for in Early-Stage Startups (Forum VC): https://www.forumvc.com/thought-pieces/what-vcs-look-for-early-stage-investment
- A VC's Playbook: Seed Investing (Alumni Ventures): https://www.av.vc/blog/mastering-seed-stage-investing-a-playbook-for-success
- How to Raise Seed Funding (CRV): https://www.crv.com/content/seed-funding
- Seed Funding vs Angel Investment: https://qubit.capital/blog/seed-funding-vs-angel-investment

---

## 5. 日本の家計消費構造(総務省 家計調査 2024)→ 個体差ある消費配分の較正

### 要点(2024年平均)
- **二人以上の世帯**: 消費支出 **300,243 円/月**(名目 +2.1% YoY)。**エンゲル係数 28.3%**(2024)。
- **単身世帯**: 消費支出 **169,547 円/月**(実質 −2.0%)。費目別割合は公表値で
  **食料(外食を除く)18.8% が最大 → 住居 16.1% → 交通・通信 14.2%** の順。
- **エンゲルの法則**: 所得が上がると食料費の**割合が下がる**。→ **個体差の較正**は「低所得個体ほど
  食料シェアを厚く(〜30-35%)・高所得個体ほど薄く(〜22-25%)、可処分(教養娯楽・交際)を厚く」。

### 費目別 月額(2024・単身世帯) — **この街の個体較正に最適**(agent は個人 = 単身世帯構造)
> 単身世帯の内訳(下表)は内部整合(合計≒169,547円)を確認済み。二次資料(家計調査からの派生)の
> ため、公表シェア(上記 食料除外食18.8%/住居16.1%/交通通信14.2%)とは集計差で数 pt ずれる。両方併記。

| 費目 | 月額(円) | 概算シェア | この街での消費カテゴリ対応(既存 prices) |
|---|--:|--:|---|
| 食料 | 48,203 | 28.4% | food / cafe(外食分)+ 日々の食費 |
| 住居 | 23,372 | 13.8% | rent(既存の家賃機構) |
| 光熱・水道 | 12,816 | 7.6% | **fixed_cost_daily**(既存の固定費に対応) |
| 家具・家事用品 | 5,937 | 3.5% | shop |
| 被服及び履物 | 5,175 | 3.1% | shop |
| 保健医療 | 8,501 | 5.0% | (H1 医療 `medical_visit` に対応) |
| 交通・通信 | 20,563 | 12.1% | ride(taxi/bus)+ 通信固定費 |
| 教育 | 9 | 0.0% | (単身はほぼ0。学生 org で別途) |
| 教養娯楽 | 20,375 | 12.0% | nightlife / leisure |
| その他の消費支出(**交際費等**含む) | 24,591 | 14.5% | 交際(共在時の奢り/贈与)・雑費 |

- 参考: **二人以上世帯**は食料 75,374円・交通通信 35,314円・教養娯楽 26,776円・その他 55,070円…等
  (同二次資料)。ただし合計が公表総額と噛み合わない費目(教育571円等)があり**単身世帯表より
  精度が落ちる**ため、この街(個人 agent)は**単身世帯表を主較正**に用いるのが妥当。

### シミュへの写像案 → **E-W3(消費)**(詳細は §7)
- `economy.py` に **`budget_shares`(単身世帯の費目シェア)**を持たせ、`initial_money` と同様に
  **build 時に個体ごと consumption profile を rng で1回サンプル**(所得帯で食料シェアを可変=エンゲル)。
  → 個体差が持続し、per-step の LLM 追加はゼロ。
- 現状の一律価格 spend に、**個体の budget_shares と所得(period_income)で重み付け**した消費配分を掛ける
  (低所得ほど food 厚め・discretionary 薄め)。交際費は**共在(co-location)時の spend** に写す。

### 出典
- 家計調査報告 2024年 概況(一次・PDF): https://www.stat.go.jp/data/kakei/sokuhou/tsuki/pdf/fies_gaikyo2024.pdf
- 統計局 エンゲル係数 FAQ(28.3%の定義): https://www.stat.go.jp/library/faq/faq19/faq19a12.html
- 総務省 報道資料 家計調査 2024年平均: https://www.soumu.go.jp/menu_news/s-news/01toukei07_01000267.html
- 費目別内訳(二次・家計調査からの派生。単身/二人以上の月額): https://moneiro.jp/media/article/living-expenses-average

---

## 6. 決済手段の実態(経産省 2024)→ 決済選択の確率モデル

### 要点(2024・経産省)
- **キャッシュレス決済比率 42.8%**(政府目標40%を突破)。残り約 **57.2% が現金等**。
- キャッシュレス内訳(金額): **クレジットカード 82.9%(116.9兆円)**・電子マネー 4.4%(6.2兆円)・
  **コード決済(QR)9.6%(13.5兆円)**・デビット 3.1%(4.4兆円)。
- **QR は +23.9% YoY** の急伸で、クレカに次ぐ第2の手段に定着。
- 注意: 上記は**金額シェア**。**件数(回数)ベースでは少額決済が多く現金が依然多い** —
  金額42.8%キャッシュレスでも「1回あたりの選択」では現金・QR/電子マネーの比重が上がる。

### 決済選択の確率モデル案
```
P(method | amount, cat, agent) :
  amount 大(≥ card_threshold)     → クレジット寄り
  amount 小 / conbini・食 → 現金 or QR/電子マネー寄り
  個体嗜好(agent の payment preference)で重みを個体差化
```
- 既存 `_spend` は既に **card_threshold(=3000円)で現金↔口座(カード)を分岐**している = 決済選択の
  最小骨格が既にある。ここに **QR/電子マネー**を中間層として足し、経産省の金額比を**初期重み**に
  金額×カテゴリ×個体嗜好で method を選ぶ。

### シミュへの写像案 → **E-W3 の決済部**
- **決済手段は spend の payload に `method` を付けるだけ**(現金/カード/QR/電子マネー)。**新たな貨幣は
  生まれない**(現金 `money` か 口座 `account` のどちらから引くかを分けるのみ)= 会計不変・R1安全。
- method 選択は**新 stream `("pay", agent.id, step)`** か決定論閾値。個体嗜好は build 時 rng で1回固定。

### 出典
- 2024年のキャッシュレス決済比率(経産省 報道): https://www.meti.go.jp/press/2024/03/20250331005/20250331005.html
- 経産省 キャッシュレス 政策ページ: https://www.meti.go.jp/policy/mono_info_service/cashless/index.html
- キャッシュレス・ロードマップ2024(キャッシュレス推進協議会): https://paymentsjapan.or.jp/wp-content/uploads/2024/12/roadmap2024.pdf

---

## 7. 実装スケッチ — E-W1 銀行 / E-W2 VC / E-W3 消費(conf設計・新イベントkind・R1安全性)

> 3つとも既存の流儀(**既定 OFF・非LLM・決定論+新stream・OFF時バイト一致**)で組む前提。
> **R1 総括**: いずれも `generate()`(LLM呼び出し)を1本も足さない → **呼数不変**。判定は observables
> (money/account/period_income/sales_total/occupancy/relations)と config のみ参照し、**k・内面構成概念を
> 発火判断に食わせない** → `compute_matched` 下の k 不変性を守る(commerce/career と同型)。

### 【要注意 A】イベント種の命名衝突
既存 `deposit` kind は**供託金(政治の供託金)**で使用済み。**銀行預金の利息などに `deposit` は使えない**。
銀行系は新種 `loan` / `repay` / `interest`、VC系は `investment` を新設すること。

### 【要注意 B】k 不変性(FixedLLM で ON≠OFF になり得る経路)
資金注入で venture の生存が延びる → 人流(co-location)が変わる → 誰が誰と会うかが変わり得る。
これは commerce の `filter_open`・career と**同型の既知の性質**で、判定を observables に限れば
compute_matched の k 不変性(k=free と k=off で呼数一致)で担保できる。判定に efficacy/grievance 等の
**内面状態を混ぜる設計は避ける**(混ぜると R9/no-fingerprint と k 不変性の両方に触れる)。

---

### E-W1 銀行(預金/融資) — `economy.py` + 新 `bank`(scheduler の `_gov` 同型)

**conf 設計**(`economy.bank`。既定 `enabled:false`):
```yaml
economy:
  bank:
    enabled: false
    base_rate: 0.02            # 基準金利(§1 テイラー則の簡略=固定でも可)
    deposit_rate: 0.001        # 預金利息(任意。0で無利息)
    score_weights: {income: 0.4, assets: 0.3, repayment: 0.2, arrears: 0.1}  # §3 の5C→4項
    approve_threshold: 0.0     # score ≥ これ で承認
    premium_slope: 0.05        # 低スコア/高レバレッジで金利上乗せ
    max_loan_ratio: 3.0        # 与信上限 = 月収相当(period_income)× これ
    group_guarantee_bonus: 0.1 # グループ所属(連帯保証)でスコア加点(§3 社会的担保)
    installment_days: 30       # 返済周期(既存 payday/家賃フェーズに相乗り)
    ration_on_default: true    # 貸倒発生で街全体の premium を一段引上げ(§1 信用引締め=雪崩)
```
**新イベント kind**(schema.py に1行ずつ登録):
- `loan`「融資の実行 {amount, rate, score, balance}」
- `repay`「返済(分割){amount, remaining, arrears?}」
- `interest`「預金/融資利息 {kind, amount}」(任意)
- 貸倒/破綻は**既存 `bankruptcy`/`eviction`/`venture_close` に接続**(新種不要)。

**流れ**: 資金ギャップの venture 所有者/困窮者が申請 → 決定論スコア(§3、既存 `period_income`・
`money+account`・滞納日数の合成)で承認/金利決定 → `owner.account` へ入金(`loan`)→ 月次返済
フェーズで `account` から引落(`repay`)→ 滞納 → **既存の破産サイクル**へ。銀行会計は `Bank`(残高・
貸出・貸倒)を遅延構築、最後の貸手は nation 予算補填で近似。

**R1 安全性**: **LLM 呼数 0 追加**。与信・返済・金利はすべて非LLM・決定論。承認/金利に乱数を使うなら
新 stream `("loan", agent.id, step)`(既存 draw 順不変)。OFF で `loan/repay/interest` は0件・money 不変=
バイト一致。判定は observables のみ(k非依存)。

---

### E-W2 VC/出資 — `tools.py`(venture の隣)+ 定期スコアリング

**conf 設計**(`tools.vc` または `economy.vc`。既定 `enabled:false`):
```yaml
tools:
  vc:
    enabled: false
    review_period_days: 5      # 定期審査の周期
    ticket: 50000              # 1件の出資額(§4 エンジェル規模を圧縮スケール)
    n_deals_per_review: 1      # 1周期の出資件数(希少=競争を作る)
    weights: {traction: 0.4, market: 0.3, network: 0.2, conviction: 0.1}  # §4 の代理変数
    threshold: 0.6             # 正規化スコア ≥ これ で出資
    equity_share: 0.2          # 出資と引換の持分(将来 exit 配当の素地。任意)
    fund_initial: 1000000      # ファンド原資(枯れると出資停止=希少性)
```
**新イベント kind**:
- `investment`「VC/エンジェル出資 {venture, investor, amount, equity, score}」
- `vc_exit`「回収・配当(任意){venture, amount}」

**流れ**: `Tools.phase` の日次に **VC 審査フェーズ**を足す(`_ventures_fulltime` の隣)。開店中の全 venture を
§4 の代理変数(`sales_total`=traction / `commerce.occupancy(node)`=market / `relations` 次数=network /
efficacy=conviction ※k注意)で**決定論スコアリング** → 閾値超の上位 `n_deals` に `ticket` を `owner.account`
へ注入(`investment`)。資金は固定費/仕入の耐久を上げ、**既存 `venture_fulltime_sales` 到達を早める**。

**R1 安全性**: **LLM 呼数 0 追加**。VC は「起業意図(LLM の `open_venture`)」を**評価するだけ**の
ルール主体。同点処理に乱数を使うなら新 stream `("vc", owner_id, day)`。OFF で `investment` 0件=バイト一致。
**【要注意 B】に従い、conviction(efficacy)を判定に混ぜるなら k 不変性の検収を必須**とする(混ぜない
設計=traction/market/network のみが最も安全)。

**観察の要**: ユーザーの観察目標「組織の自然形成・ファウンダー成立条件」は、`venture_open →(売上・人流・
中心性の蓄積)→ investment → venture_fulltime` の系列で**局所ルールから創発**する。中央が誰を founder に
するかを決めず、**街の需要と関係網が資金を呼ぶ** = 「自然界のような仕組み」に合致。

---

### E-W3 消費(構造)— `economy.py` + `_spend`(payment)

**conf 設計**(`economy.consumption` / `economy.payment`。既定 `enabled:false`):
```yaml
economy:
  consumption:
    enabled: false
    budget_shares:             # §5 単身世帯 2024(較正の初期値)
      food: 0.28
      shop: 0.07               # 家具+被服
      nightlife: 0.12          # 教養娯楽
      social: 0.15             # その他(交際費等)
      transport: 0.12
    engel_income_slope: -0.15  # 所得↑で食料シェア↓(エンゲルの法則)
  payment:
    enabled: false
    methods: [cash, credit, emoney, qr]
    value_weights: {credit: 0.83, qr: 0.10, emoney: 0.04, debit: 0.03}  # §6 経産省 金額比
    card_threshold: 3000       # 既存キー流用(これ以上はカード寄り)
```
**新イベント kind**: 原則**不要**(既存 `spend` の payload に `method` と、消費配分の観測が要れば
`cat` を活用)。観測を厚くするなら任意で `consume_budget`「日次の費目別消費スナップ」1種のみ。

**流れ**: ①build 時に `initial_money` と同様、**個体ごと consumption profile を rng で1回サンプル**
(所得帯で food シェアを可変)→ 個体差が持続。②`_spend` の金額を個体 budget_shares と `period_income` で
重み付け。③決済は `_spend` 内で `(amount, cat, 個体嗜好)` から method を選び payload に付与、現金/口座の
どちらから引くかを分ける。

**R1 安全性**: **LLM 呼数 0 追加**。profile は build 時 rng(per-step draw を足さない)、method は決定論閾値
か新 stream `("pay", agent.id, step)`。**決済 method は貨幣を新たに生まない**(現金↔口座の振替のみ)ので
会計不変。OFF で従来の一律 spend とバイト一致。

---

## 8. まとめ(実装順の提案)

1. **E-W3 消費**が最小リスク(既存 `_spend`/accounts の拡張・新 kind ほぼ不要・会計不変)。較正値は §5 に揃った。
2. **E-W1 銀行**は accounts(預金/破産サイクル)が既にある土台の上に「融資+与信スコア+返済」を足す。
   与信スコアは既存量(`period_income`・money+account・滞納日数)の合成でほぼ組める(§3)。
3. **E-W2 VC**は観察目標の核。判定の代理変数(`sales_total`/`occupancy`/`relations`)は全て既存。
   **traction/market/network のみで判定すれば k 不変性が最も安全**(conviction を足すなら検収必須)。
4. 3つとも **既定 OFF・非LLM・決定論+新stream** で R1 呼数不変・OFF時ゴールデン一致を守れる。
   実装着手前に **pre-coding-alignment(決定アジェンダ提示→合意)** と **ask-before-extending** に従うこと。
