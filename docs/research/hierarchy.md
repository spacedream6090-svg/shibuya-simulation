# 社会的ヒエラルキー(地位・信用・名声)— 概念リサーチと実装候補メニュー(2026-07-08)

> 依頼(Fable): 渋谷 LLM エージェント社会シミュにおける「社会的ヒエラルキー(地位・信用・名声)」を
> web リサーチし、概念の柱・既存部品との対応・実装候補・観測指標を整理する **調査文書**。
> ユーザー仮説: ヒエラルキーは (a) 組織・コミュニティを **存続させる** 要因であり、(b) 世界を変えようとする
> **動機** にもなる。「信用がある人」にリソースと人員が集まる(マタイ効果的な集中)。
>
> ⚠️ 本稿は **調査のみ**。実装可否・採否は依頼元(Fable)が決める。「実装済み」を述べる箇所は無い
> (§2 で既存モジュールを対応づけるが、ヒエラルキー力学そのものが実現済みという意味ではない。
> 既存の relations/info_env は評判・影響力の **骨組み** を持つが既定 OFF で、地位の分布・移動・
> マタイ効果的集中を生成する力学は未検証)。研究課題「keystone は生得か創発か」との接続を各所で明示する。

---

## 0. 要旨(3行)

1. 地位には理論的に **2系統**(prestige=自発的に贈られる敬意 / dominance=強制による服従)と **3次元**
   (Weber: 階級=経済・身分=名誉・党派=権力)があり、いずれも「信用がある人に人が従う」機構を別経路で説明する。
2. 「信用がある人にリソースと人員が集まる」= **累積優位/マタイ効果/優先的選択** という、地位を状態変数とする
   **正のフィードバック**。これは決定論・非LLMで実装しやすく、べき則・ジニ係数として観測可能(§4)。
3. ヒエラルキーは (a) 調整費用を下げて組織を **安定** させる一方(機能理論)、(b) **相対的剥奪・地位不整合** を通じて
   変革動機を生む(SIMCA)。同じ変数が「秩序」と「反乱」の両方を駆動する両義性が、本シミュの keystone 問題に直結する。

---

## §1. 概念の柱

### 柱1. 地位の3類型と基礎理論 — 「なぜ人は特定個体に従うのか」

**要旨.** 地位差の発生を説明する3つの基礎枠組み。(a) Weber の **3次元** 論(経済的地位=階級・威信=身分・権力=党派は
互いに独立しうる)、(b) 進化人類学の **prestige/dominance 二経路** 論(敬意は「強制」と「自発的服従」の別機構から生じる)、
(c) 社会心理の **期待状態理論/地位特性理論**(集団は課題遂行の期待に基づき序列を即興生成する)。共通点は「地位は
個体属性でなく **他者の評価・服従という関係** から生じる」こと=シミュでは agent の内部特性でなく相互作用の集計として
創発させるべき対象(no-fingerprint 方針と整合)。

**代表文献.**
- Weber, M. (1922/1978) *Economy and Society*「Class, Status, Party」— 階級/身分(Stände)/党派の3次元。概説: https://en.wikipedia.org/wiki/Three-component_theory_of_stratification
- Henrich, J. & Gil-White, F. (2001) "The evolution of prestige." *Evolution and Human Behavior* 22(3):165–196. DOI: https://doi.org/10.1016/S1090-5138(00)00071-4 (著者版: https://henrich.fas.harvard.edu/publications/evolution-prestige-freely-conferred-deference-mechanism-enhancing-benefits )
- Berger, J., Cohen, B.P. & Zelditch, M. (1972) "Status Characteristics and Social Interaction." *American Sociological Review* 37(3):241–255. 概説: https://en.wikipedia.org/wiki/Expectation_states_theory
- Anderson, C., Hildreth, J.A.D. & Howland, L. (2015) "Is the desire for status a fundamental human motive?" *Psychological Bulletin* 141(3):574–601. DOI: https://doi.org/10.1037/a0038781 (PubMed: https://pubmed.ncbi.nlm.nih.gov/25774679/ )

**実証知見.**
- **prestige と dominance は別軸**: prestige は「模倣したい熟練者」への自発的敬意(文化伝達を促進)、dominance は
  「コストを課せる相手」への恐怖由来の服従。両者は経験的に分離可能(視線・声・姿勢の差、生理指標)。
  → シミュでは prestige ≒ 語の被採用・被傾聴、dominance ≒ 罰・所持金・執行力、という **別チャネル** に写せる。
- **地位は少数属性から即興生成される**(地位特性理論): 職業・年齢等の「拡散的地位特性」が課題無関係でも発言量・
  影響力の配分を決める。→ occupation/org_role がプロンプトで序列の手がかりになりうる(観測対象)。
- **status は普遍的動機**(Anderson 2015): 文化・性・年齢・性格を越えて「尊敬・自発的服従の獲得」を志向する。ただし
  「金銭・安全そのもの」ではなく「他者からの評価」が独立の報酬になる点が肝。→ 柱4の変革動機と接続。

---

### 柱2. 蓄積優位 — 「信用がある人にリソースと人員が集まる」(ユーザー仮説の中核)

**要旨.** 初期のわずかな地位差が、**地位を資源に変換 → その資源が次の地位を生む** 正のフィードバックで拡大する。
社会学の **マタイ効果/累積優位**、ネットワーク科学の **優先的選択(preferential attachment)**、経済学の
**winner-take-all** は、同じ「rich-get-richer」機構を異なる語彙で述べたもの。帰結は **べき則/重い裾** の地位分布と
高いジニ係数。本シミュの「マタイ効果的集中」仮説はここに直接対応し、**決定論・非LLMで最も実装しやすい柱**。

**代表文献.**
- Merton, R.K. (1968) "The Matthew Effect in Science." *Science* 159(3810):56–63. DOI: https://doi.org/10.1126/science.159.3810.56 (概説: https://en.wikipedia.org/wiki/Matthew_effect )
- DiPrete, T.A. & Eirich, G.M. (2006) "Cumulative Advantage as a Mechanism for Inequality." *Annual Review of Sociology* 32:271–297. DOI: https://doi.org/10.1146/annurev.soc.32.061604.123127
- Barabási, A.-L. & Albert, R. (1999) "Emergence of Scaling in Random Networks." *Science* 286(5439):509–512. DOI: https://doi.org/10.1126/science.286.5439.509 (PubMed: https://pubmed.ncbi.nlm.nih.gov/10521342/ )
- Frank, R.H. & Cook, P.J. (1995) *The Winner-Take-All Society*. Free Press. 概要: https://books.google.com/books/about/The_Winner_take_all_Society.html?id=iD5PSFkoOCwC

**実証知見.**
- **優先的選択でべき則が創発**(Barabási–Albert): 「新ノードは既に多く繋がるノードへ優先的に接続」だけで次数分布が
  スケールフリー(P(k)~k^-3)になる。→ SNS フォロー・グループ加入・関係形成に同型の規則を入れれば、少数ハブへの
  集中が **設計者が指定せずとも** 生じる(創発の観測対象)。既存 `net/internet` のフォロー、`tools._group_joins`
  (「関係者がいる相手のグループに加入」)は優先的選択の骨組みに近いが、集中が生じるかは未検証。
- **累積優位は複数機構をまとめる傘概念**(DiPrete & Eirich): (i) 直接の rich-get-richer、(ii) 初期優位が別領域の
  優位へ波及(地位の互換性)、(iii) しきい値効果。→ 「金→評判→フォロワー→提案の通りやすさ」の **領域横断変換** が
  効くかは観測で切り分けられる(§4 の地位整合)。
- **winner-take-all は相対業績で報酬が決まる市場で発生**(Frank & Cook): わずかな差が莫大な報酬差に増幅。注意・
  観客が有限(柱5)なほど強い。→ 「観客が有限で相対順位が報酬を決める」構造(イベント集客・出店売上)で
  上位集中が起きるかを見る。
- ⚠️ **注意**: マタイ効果は放置すると **意味収束・単一ハブへの崩壊**(研究の敵)を招きうる。project-charter の
  「崩壊を防ぐ機構(LOD/memory/感受性)」との緊張がある。集中の強度は **実験変数** にすべき(単に強くしない)。

---

### 柱3. ヒエラルキーの機能と逆機能 — 「組織・コミュニティを存続させる」(ユーザー仮説 (a))

**要旨.** ヒエラルキーは **調整・意思決定コストを下げ** 集団を存続させる(機能理論)。分業→専門化→少数への
権限集中は大規模組織の技術的必然(Michels)。しかし同じ機構が **寡頭制の鉄則** として民主的組織すら少数支配へ
固定化する **逆機能** を持つ。地位・権力は自己強化的で、一度上位に立つと心理・機会の両面で優位が持続する
(Magee & Galinsky)。→ 「安定化」と「固定化・不動性」は表裏。keystone が **固定した支配者** か **創発する変革者** かの
弁別は、この移動性(§4)にかかる。

**代表文献.**
- Magee, J.C. & Galinsky, A.D. (2008) "Social Hierarchy: The Self-Reinforcing Nature of Power and Status." *Academy of Management Annals* 2(1):351–398. DOI: https://doi.org/10.5465/19416520802211628 (PDF: https://web.mit.edu/curhan/www/docs/Articles/15341_Readings/Power/Magee,%20J.%20C.,%20&%20Galinsky,%20A.%20D.%20(2008).%20Social%20hierarchy-%20The%20self%E2%80%90reinforcing%20nature%20of%20power%20and%20status..pdf )
- Michels, R. (1911) *Political Parties* — 寡頭制の鉄則。概説: https://en.wikipedia.org/wiki/Iron_law_of_oligarchy
- (機能理論の古典対比: Davis & Moore 1945 の階層機能論 vs Tumin 1953 の批判。概説: https://en.wikipedia.org/wiki/Davis%E2%80%93Moore_hypothesis )

**実証知見.**
- **分業→階層化は組織規模の関数**(Michels): 大集団は日々の決定を全員では下せず、中央化と専門家層が生じる。専門家は
  情報と手続きを独占し、大衆の惰性・敬意を背景に権力を保持する。→ シミュで組織(`organizations`)や議会
  (`institution_routes.assembly` の代表制)が **規模とともに** 少数集中へ向かうかは観測できる。
- **地位・権力は自己強化**(Magee & Galinsky): 権力は「資源統制」で保持行動を誘発し、地位は「他者からの敬意」で
  さらなる敬意・機会を呼ぶ(=柱2の心理版)。→ プロンプトに評判/所属を載せる経路(`relations.social_lines`)は
  この自己強化の入口になりうる(観測対象)。
- **「鉄則」は必然ではない**(反証研究): 一部の民主的組織は制度設計で寡頭化を回避できる。→ 逆機能を hardcode せず、
  制度提案(`propose`)・改選(`assembly.term_days`)・廃止(`recursion.repeal`)で **移動性が回復するか** を見る。

---

### 柱4. 地位と社会変革の動機 — 「世界を変えようとする動機」(ユーザー仮説 (b))

**要旨.** 地位は「秩序」だけでなく「反乱・起業・イノベーション」も動機づける。鍵は **絶対水準でなく相対・不整合**:
自分が「得るべき」と思う地位と実際の乖離(**相対的剥奪**)、複数次元の地位の食い違い(**地位不整合**)が緊張を生む。
社会運動論の **SIMCA** は、集合行為への動員を「(不正義への)怒り × 集団同一化 × 集団効力感」の合成として定式化する
——これは本シミュの既存 **統一チェーン**(grievance→命名→伝播→tipping→制度創発)と同型で、地位はその各項に効く。

**代表文献.**
- Gurr, T.R. (1970) *Why Men Rebel*. Princeton UP — 相対的剥奪と集合的暴力。概説: https://www.beyondintractability.org/bksum/gurr-men
- Lenski, G. (1954) "Status Crystallization: A Non-Vertical Dimension of Social Status." *American Sociological Review* 19(4):405–413. 概説: https://www.oxfordreference.com/display/10.1093/oi/authority.20110803100529529
- van Zomeren, M., Postmes, T. & Spears, R. (2008) "Toward an integrative social identity model of collective action (SIMCA)." *Psychological Bulletin* 134(4):504–535. DOI: https://doi.org/10.1037/0033-2909.134.4.504 (PDF: https://research.vu.nl/ws/portalfiles/portal/2391519/Van%20Zomeren%20Psychological%20Bulletin%20134(4)%202008.pdf )

**実証知見.**
- **反乱は絶対的貧困でなく期待と現実の乖離で起こる**(Gurr): 「得るべき」と「得られる」の知覚差が怒り→暴力を駆動。
  乖離は客観でなく **知覚** でよい。→ シミュの `grievance` を「絶対的欠乏」でなく「期待−現状」で更新すると、地位上昇後の
  停滞(=高い期待の不充足)が変革動機になりうる。現状ログでは grievance が床に張り付き変革語が出ない
  (docs/research/world-change-motivation.md)ため、この相対化は仮説として妥当性がある(採否は依頼元)。
- **地位不整合が緊張源**(Lenski): 「高学歴・低収入」等、次元間の食い違いが不快と変化志向を生む。→ シミュで
  「評判は高いが所持金が低い/職位は低い」個体が提案・出店に向かうか(§4 の地位整合分散を説明変数に)。
- **動員は怒り×同一化×効力感の合成**(SIMCA, 182 効果のメタ分析): 3項とも中程度の因果効果。地位は各項に接続——
  相対的剥奪=不正義項、グループ所属(`found_group`/faction)=同一化項、過去の成功=効力感項。→ 既存
  `factors`(grievance/efficacy)と `tools`(group)を SIMCA 3項として観測フレームで束ねられる。
- **地位追求は起業・イノベーションの駆動因の一つ**(Anderson 2015 と起業研究): 尊敬・承認欲求(esteem needs)が
  リスクテイク・新規性追求を促す。ただし内発的動機・自己実現の寄与も大きく、status **単独** の効果は過大視しない。
  → 「地位追求 → 変革ツール使用」は観測仮説であって、injection してはならない(中立提示のまま創発を見る)。

---

### 柱5. 現代の名声力学 — 注意経済・インフルエンサー・フォロワーのべき則

**要旨.** 現代の名声は **有限な注意** を巡る競争で配分される(注意経済)。SNS のフォロワー・影響力は経験的に
**べき則/重い裾** に従い、上位少数(インフルエンサー)に到達・影響が集中する。ただし「フォロワー数=影響力」ではない
(million follower fallacy)——リツイート・言及で測る実影響は別分布。これは柱2(優先的選択)の現代デジタル版であり、
本シミュの `net/internet`(SNS)+`info_env.influence`(フォロワー非対称)が写す対象。

**代表文献.**
- Simon, H.A. (1971) "Designing Organizations for an Information-Rich World" — 「情報の富は注意の貧困を生む」。
  概説: https://en.wikipedia.org/wiki/Attention_economy
- Goldhaber, M.H. (1997) "The Attention Economy and the Net." *First Monday* / Wired. https://firstmonday.org/ojs/index.php/fm/article/view/519
- Cha, M., Haddadi, H., Benevenuto, F. & Gummadi, K. (2010) "Measuring User Influence in Twitter: The Million Follower Fallacy." *ICWSM*. https://www.aaai.org/ocs/index.php/ICWSM/ICWSM10/paper/view/1538 (PDF 経由: https://www.researchgate.net/publication/221298004_Measuring_User_Influence_in_Twitter_The_Million_Follower_Fallacy )

**実証知見.**
- **注意は希少資源**(Simon): 情報が増えるほど注意が制約になり、その配分が価値を決める。→ シミュの TL 表示枠・
  イベント集客・発話の被傾聴が「有限の注意」を巡る競争であり、そこに集中が生じるかを見る。
- **フォロワー分布はべき則/重い裾**(複数実証): 影響指標は 75%以上のユーザーでほぼ 0。少数が発信し多数が観察する。
  ジニ・Lorenz・Pareto で特徴づく構造的不平等。→ §4 でフォロワー・被いいね・被リシェア分布のべき則性・ジニを測る。
- **フォロワー数 ≠ 実影響**(million follower fallacy): 到達(フォロワー)と、実際に語を採用させる影響は別。
  高フォロワーでも語が広まらない/低フォロワーでも局所で強い、が起こる。→ 既存 `measure.agent_features` の
  `c_transmission`(伝播)/`sns_reshares_received` と follower を **別々に** 測り、乖離(=fallacy)自体を観測できる。
- **アルゴリズム推薦が集中を増幅**: エコーチェンバー・バイラル増幅は分極と上位集中を加速。既存
  `info_env.recommendation`/`influence`/`misinfo` はこの加速器の骨組み(既定 OFF・非LLM・決定論)。

---

## §2. シミュ既存部品との対応表

> 目的: 各概念が **どの既存モジュールの affordance に写せるか** を示す。「実装済み」ではなく「対応先の seam」の同定。
> 既存の relations/info_env/tools は多くが **既定 OFF の骨組み**(no-fingerprint 方針で `src/society/` 直下=検査対象外に
> 置かれ、engine から因子名を見せない)。ヒエラルキー力学が実際に創発・集中するかは未検証(§4 で測る対象)。

| 概念(柱) | 対応する既存モジュール / フィールド | 現状の粒度と穴 |
|---|---|---|
| prestige(自発的敬意)柱1 | `relations.py`: `_reputation`(語採用 `rep_adopted`・被傾聴 `rep_mention` で増、日次 `rep_decay`)、`social_lines` の「街で名が知られている」注入 | 骨組みあり・既定 OFF。評判が資源・人員動員へ **変換** される経路が無い(観測スコア+プロンプト文脈に留まる=設計上 factors 非結合) |
| dominance(強制的服従)柱1 | `institution_routes.enforcement`(罰金 `fine`・勾留 `detention_steps`・不満 `grievance`)、`economy`(所持金=資源統制)、`labor` 争議 | 罰・拘束の affordance はあるが「強制で服従を得る=他者行動を曲げる」ループは未形成 |
| 地位特性(拡散的地位)柱1 | `agents/persona`: occupation / `organizations.org_role`(職場・役割)/ 年齢 | 序列の手がかりとしてプロンプトに載るが、期待→発言量・影響配分の偏りは未計測 |
| 3次元(階級/身分/党派)柱1 | 階級=`economy`(wage/money)、身分=`relations._reputation`、党派=`institution_routes`(propose/vote/assembly/`tools.groups`) | 3次元が **別々に** 存在するが、次元間の整合/不整合(柱4 Lenski)は未測定 |
| マタイ効果/累積優位 柱2 | `info_env.influence`(高フォロワーの reach 加重 `reach_weight`)、`relations` 評判の gain、`net.follower_count` | reach 増幅の骨組みはあるが、地位→資源→さらなる地位の **閉ループ** と分布の重い裾化は未検証 |
| 優先的選択 柱2 | `net/internet`(フォロー/リシェア/priority feed)、`tools._group_joins`(「関係者がいる相手のグループに加入」)、`set_priority` | 「既に繋がる相手へ優先接続」に近い規則はあるが、スケールフリー化するかは未観測 |
| winner-take-all 柱2 | `tools`: `open_venture` 売上(有限の客)、`host_event` 集客(`attend_relation_bonus`=関係者ほど来る) | 相対順位で報酬が決まる構造の萌芽。上位集中の測定は未 |
| 機能(組織安定)柱3 | `organizations`(役割・org_ledger 売上)、`government`(ward/metro 予算→ペイロール階層)、`schedule` | 役割・給与階層はあるが「階層が調整費用を下げ存続を助ける」効果の検証は未 |
| 逆機能(寡頭制)柱3 | `institution_routes.assembly`(代表制議会・`term_days` 改選・`size` 議席)、`sim.council` | 代表への権限集中の骨組みあり。少数固定 vs 改選での回復は観測課題 |
| 相対的剥奪 柱4 | `factors`(grievance)、`economy`(所持金圧・立退き/破産 grievance)、`career`(失業 grievance) | grievance は現状「絶対的欠乏」寄りで床張り付き。**期待−現状** の相対化は未(world-change-motivation.md) |
| 地位不整合 柱4 | 上記 3次元(money × reputation × org_role × followers)の食い違い | 各次元は取得可能。不整合スコア(次元間分散)の算出は §4 提案 |
| SIMCA(動員)柱4 | 不正義=`grievance` / 同一化=`found_group`・faction / 効力感=`efficacy`・`on_group_success` → 変革=`propose`/`host_event` | 3項が別モジュールに散在。SIMCA として束ねる観測フレームは未(既存「統一チェーン」と同型) |
| 注意経済/名声べき則 柱5 | `net/internet`(SNS 投稿/TL/いいね/RT/フォロー)、`info_env.recommendation`/`influence`/`misinfo`、`viral_cascade` | SNS 基盤と加速器の骨組みあり(既定 OFF)。フォロワー/影響のべき則・ジニ・fallacy 測定は §4 提案 |
| 意見の非対称影響 柱2/5 | `opinion.py`(FJ 力学)、`measure.c_opinion_moved`(他者意見を動かした量) | 意見を動かす力=影響力の一形態として既に観測列がある。地位との相関は未分析 |

---

## §3. 実装候補メニュー(採否は依頼元 Fable が決定)

> 各候補: **何を** / **どの理論** / **決定論・非LLMで可能か** / どちらのループに効くか(**集中ループ**=リソース・人員が
> 集まる / **変革ループ**=変革動機)/ **優先度 A/B/C**。トレードオフを正直に記す。
> 全候補は本リポの標準契約を満たす前提で評価: **既定 OFF・R1(LLM 呼数不変)・R9(factors は traits を見ない)・
> no-fingerprint(engine に因子名を見せない)・決定論(乱数 stream を分離)**。injection(創発を仕込む)への該当が
> 最大のリスク軸——「地位が可視化 **できる**」までは affordance、「地位が高い個体を変革させる」は injection。

| # | 候補 | 理論(柱) | 決定論/非LLM | 効くループ | 優先度 | 主なトレードオフ・リスク |
|---|---|---|---|---|---|---|
| 1 | **評判→動員の変換ループ**(評判が高いほど event 集客・DM 到達・group 加入が起きやすい) | マタイ/優先的選択(2)、prestige(1) | ○ 完全に決定論(既存 `_reputation` を確率係数に乗せる) | 集中(主) | **A** | 最小コストで「信用に人が集まる」を可視化。ただし係数を上げすぎると単一ハブ崩壊(project-charter の敵)。強度を実験変数化必須 |
| 2 | **地位分布・移動性の観測層**(§4 を measure に純関数追加。べき則・ジニ・移動性・地位整合) | 全柱の測定 | ○ 純関数・乱数不使用 | 両方(測定) | **A** | 副作用ゼロ・研究の核に直結。実装より「何を Y の説明変数に入れるか」の設計が本体。まず観測から入るのが安全 |
| 3 | **優先的選択のフォロー則**(新規フォロー/RT が高被参照者へ確率的に偏る) | 優先的選択(2)、注意経済(5) | ○ 決定論(既存 follower_count を重みに) | 集中(主) | **A** | スケールフリーが **創発するか** を見る中核実験。R1 注意: 「誰をフォローするか」は SNS 内容層なので k 不変性で担保(info_env と同型) |
| 4 | **相対的剥奪版 grievance**(grievance を「絶対欠乏」でなく「期待−現状」で更新。期待は過去の地位水準から) | 相対的剥奪(4)、地位不整合(4) | ○ 決定論(状態更新則の変更) | 変革(主) | **A** | world-change-motivation.md の「grievance 床張り付きで変革語ゼロ」への直接の仮説。ただし grievance→発火の結合は既存で保留中——結合可否も含め要検討。過度だと不満駆動を injection しかねない |
| 5 | **地位不整合スコア**(money/評判/org_role/followers の次元間分散を観測+任意でプロンプト文脈) | 地位不整合(4, Lenski) | ○ 決定論(各次元の z 化と分散) | 変革(主)+測定 | **B** | 「高評判・低収入」個体が変革に向かうかの検証装置。プロンプト注入は injection 寄り——観測のみに留めるのが安全 |
| 6 | **SIMCA 観測フレーム**(grievance×同一化×efficacy を3項として束ね、変革ツール使用を予測) | SIMCA(4) | ○ 純関数(既存 factors/tools の集計) | 変革(主)+測定 | **B** | 新規力学を足さず既存量の束ね直し=低リスク・高説明力。既存「統一チェーン」の定量版。効果が出なければ 3項の欠落を特定できる |
| 7 | **winner-take-all な集客/売上**(相対順位で集客率・購買が決まる。観客・客が有限) | winner-take-all(2, Frank&Cook)、注意経済(5) | ○ 決定論(順位ベースの確率) | 集中(主) | **B** | 上位集中を強める。現実的だが「格差を作る」設計の色が濃く、injection 批判に注意。強度は config 変数に |
| 8 | **prestige/dominance 二経路の分離観測**(被傾聴・語採用=prestige / 罰・所持金・執行=dominance を別スコア化) | 二経路(1, Henrich&Gil-White) | ○ 純関数(既存イベントの再集計) | 両方(測定) | **B** | keystone が prestige 型か dominance 型かを弁別=研究上の novelty。力学は足さず観測のみなので安全。定義の妥当性(operationalization)が論点 |
| 9 | **代表制の寡頭化観測**(assembly ON 時の議席占有・改選での入れ替わり=移動性を測る) | 寡頭制の鉄則(3, Michels) | ○ 純関数(council イベントの集計) | 集中(主)+測定 | **B** | 「安定 vs 固定」の弁別。assembly 自体が既定 OFF のため、実験条件としての ON が前提 |
| 10 | **組織階層の存続効果**(org 役割の有無で調整コスト=会話衝突/計画失敗が減るかを観測) | 機能理論(3) | ○ 純関数(既存 org_role × 行動ログ) | 集中(存続)+測定 | **C** | ユーザー仮説 (a) の直接検証だが「調整コスト」の操作化が難しく、効果が薄い可能性。優先度低め |
| 11 | **地位の減衰・可搬性パラメータ**(評判/影響の減衰率・領域間変換率を config 化=累積優位の強度掃引) | 累積優位(2, DiPrete&Eirich) | ○ 決定論(既存 decay の一般化) | 集中(主) | **C** | k 掃引と同様「集中強度」を実験軸にできる。ただし候補1/3/7 が入って初めて意味を持つ従属的パラメータ |
| 12 | **注意の有限化**(TL 表示枠・発話被傾聴の総量に上限=注意の希少性) | 注意経済(5, Simon) | △ 決定論だが SNS 表示順を変える=R1 注意 | 集中(主) | **C** | べき則を強める現実的機構だが、表示変更は info_env と同じ FixedLLM 非一致リスク。k 不変性で担保する設計が要る。効果は候補3と重複しうる |

**選定の指針(正直なトレードオフ).**
- **まず A の #2(観測)から**。力学を足す前に「現状の分布に集中/移動性があるか」を測らないと、#1/#3/#7 の効果を評価できない。
  観測は副作用ゼロ・研究の核直結で、最もリスクが低い。
- **集中ループ**を見たいなら #1・#3 が最小コストで核心。両者は「地位→資源→地位」の閉ループを作るが、**強度の実験変数化が必須**
  (強すぎると単一ハブ崩壊=研究無効化)。#7・#11・#12 は #1/#3 の増幅・掃引であり、単独では優先度が下がる。
- **変革ループ**は #4(相対的剥奪 grievance)が最有力仮説だが、world-change-motivation.md の知見どおり「不満は鎮静方向へ
  自然収束」するため、#4 単独で変革語が増える保証はない。#6(SIMCA 観測)で 3項のどれが欠けているかを先に特定する方が安全。
- **injection 回避の線引き**: 「地位が可視化・変換 **できる**」(#1/#3/#7)は affordance で可。「地位が高い個体を変革へ
  向かわせる」直接結合は injection なので不可——変革は中立提示のまま創発を観測する(既存ツールの中立性方針を踏襲)。
- **novelty 観点**: #8(prestige/dominance 分離)と #6(SIMCA 定量)は「keystone は生得か創発か・どの型か」に直接答える
  観測装置で、力学追加なしに研究価値が高い。実装リスクと研究価値の比が最良。

---

## §4. Measurement — 観測層で測るべき指標

> 方針: research の核は「Y(世界改変量)を traits で回帰した R²(k) の低下・seed 発散・EWS の三角測量で k* を探す」
> (`observer/measure.py`)。地位指標は **その Y の説明変数** かつ **独立した創発の観測対象** として足す。すべて
> 決定論・純関数で `measure` に追加可能(既存 `agent_features`/`network_windows` が土台)。地位変数は Y に直接
> 合成しない(既存 `c_opinion_moved` 等と同様、`y_weights` 経由でのみ研究者が合成可)。

### 4.1 地位分布の集中度(べき則・不平等)
- **べき則適合**: フォロワー数・被いいね/被リシェア(`sns_likes_received`/`sns_reshares_received`)・評判・出店売上
  (`venture_revenue`)・署名獲得(`signatures_gathered`)・会話次数(`network_windows.degree`)・Y_external の分布に対し、
  裾指数 α の推定(Clauset–Shalizi–Newman 法の簡易版=対数ビン回帰 or MLE)と、対数正規/指数との適合比較。
  → 「少数ハブへの集中」が創発したかの主指標。柱2/5。
- **ジニ係数・Lorenz 曲線・上位シェア**: 上記各量の Gini と「上位1%/10% が占める割合」。時系列で集中の進行を追う。
  純関数で容易(ソート+累積)。
- **注意配分の集中**: 被傾聴回数(hearers 集計)・TL 露出・イベント集客の Gini。柱5(注意経済)。

### 4.2 地位移動性(mobility)— 「安定 vs 固定」の弁別
- **上位者の入れ替わり**: 既存 `network_windows.centrality_churn`(top5 の窓間入替)を評判・フォロワー・所持金にも拡張。
  churn が高い=移動性あり(創発する keystone)/ 低い=固定(寡頭化)。柱3。
- **地位遷移行列**: 評判(or 所持金)の分位を時点間で追い、分位間遷移確率行列を作る。対角優勢=不動、非対角厚い=流動。
- **順位相関の時間減衰**: t0 と t の地位順位の Spearman ρ を lag ごとに。減衰が遅い=マタイ効果的固定。
- **代表制の占有**(assembly ON 時): `council_elected` イベントから議席の再選率・新規参入率。柱3(寡頭制)。

### 4.3 累積優位(マタイ効果)の直接検定
- **初期地位 → その後の獲得** の回帰: 「t までの地位」を説明変数、「t→t+Δ の地位増分」を被説明変数にした OLS。
  正で有意=rich-get-richer(DiPrete&Eirich の操作化)。既存 `r2_traits` の枠組みを流用可。
- **優先的選択の検証**: 新規フォロー/加入イベントの相手次数を、次数比例の帰無モデルと比較(Barabási–Albert 型検定)。

### 4.4 地位の整合/不整合(次元横断)
- **次元間相関行列**: money × 評判 × org 役職 × フォロワー × Y_external の相関。全て高相関=整合的階層 /
  低相関=多次元で独立(Weber 的)。柱1(3次元)。
- **個体別 地位不整合スコア**: 各次元を z 化し、個体内の分散(or 最大−最小)。柱4(Lenski)。この不整合が
  変革ツール使用・提案・出店の **説明変数** になるかを検定(仮説: 不整合が高い個体ほど変革的)。
- **million follower fallacy 検定**: フォロワー(到達)と `c_transmission`/`c_opinion_moved`(実影響)の乖離を測る。
  相関が低い=fallacy 再現。柱5。

### 4.5 keystone・研究課題との接続
- **地位 → 変革の時間的先行**: 高地位が変革ツール使用(`event_host`/`proposal`/`venture_open`/`group_found`)に
  **先行** するか(グレンジャー的な時間前後)。仮説 (b) の検証。ただし相関≠因果、injection でないことの担保に注意。
- **SIMCA 3項の合成予測**: grievance(不正義)× グループ所属(同一化)× efficacy(効力感)で変革行動を予測する
  ロジスティック/OLS。3項の交互作用が効くか、どれが律速かを見る。柱4。
- **k との交互作用**: 上記すべての集中度・移動性・地位→変革効果を **k(思考頻度/writeback)掃引** で描き、k* 近傍で
  集中や移動性が相転移するかを EWS(既存 `ews`)と併せて見る。地位力学が k* の位置を動かすなら、それ自体が発見。

### 4.6 実装メモ(観測のみ・力学非追加)
- 追加先: `observer/measure.py` に純関数(`status_distribution`, `status_mobility`, `cumulative_advantage_test`,
  `status_consistency`)。既存 `agent_features`/`network_windows`/`collective_series` が入力を供給する。
- 既存イベントで概ね賄える: `reputation_update`・`viral_cascade`・`sns_like`/`sns_reshare`・`venture_sale`・
  `proposal_support`・`group_join`・`arrive`・`speak`(hearers)。**新規ログ stream はほぼ不要**(=既定挙動不変で導入可)。
- 分布のべき則検定・Gini は numpy のみで実装可(現行 measure は scipy/pandas を使わない方針)。

---

### 付録: 出典一覧(URL)
- Weber 3次元: https://en.wikipedia.org/wiki/Three-component_theory_of_stratification
- Henrich & Gil-White 2001(prestige/dominance): https://doi.org/10.1016/S1090-5138(00)00071-4
- Berger et al. 1972(地位特性/期待状態): https://en.wikipedia.org/wiki/Expectation_states_theory
- Anderson et al. 2015(status=根源的動機): https://doi.org/10.1037/a0038781
- Merton 1968(マタイ効果): https://doi.org/10.1126/science.159.3810.56
- DiPrete & Eirich 2006(累積優位): https://doi.org/10.1146/annurev.soc.32.061604.123127
- Barabási & Albert 1999(優先的選択): https://doi.org/10.1126/science.286.5439.509
- Frank & Cook 1995(winner-take-all): https://books.google.com/books/about/The_Winner_take_all_Society.html?id=iD5PSFkoOCwC
- Magee & Galinsky 2008(地位の自己強化): https://doi.org/10.5465/19416520802211628
- Michels 1911(寡頭制の鉄則): https://en.wikipedia.org/wiki/Iron_law_of_oligarchy
- Gurr 1970(相対的剥奪): https://www.beyondintractability.org/bksum/gurr-men
- Lenski 1954(地位不整合): https://www.oxfordreference.com/display/10.1093/oi/authority.20110803100529529
- van Zomeren et al. 2008(SIMCA): https://doi.org/10.1037/0033-2909.134.4.504
- Simon 1971 / 注意経済: https://en.wikipedia.org/wiki/Attention_economy
- Goldhaber 1997(注意経済 web): https://firstmonday.org/ojs/index.php/fm/article/view/519
- Cha et al. 2010(million follower fallacy): https://www.researchgate.net/publication/221298004_Measuring_User_Influence_in_Twitter_The_Million_Follower_Fallacy

> 関連内部文書: docs/research/world-change-motivation.md(変革動機の既存ログ分析)/ docs/research-scope.md
> (組織社会学・社会階層 = P2 observable)/ docs/lit/collective-action__institutions-framing-overview.md(統一チェーン)。
