# 入力解像度の個体差 — 「世界に対する解像度」を入力トークン量で再現できるか(討議材料)

- 作成: 2026-07-14 / 担当: Opus 4.8(リサーチ)/ 種別: **調査のみ**(コード非編集・実LLM実行なし・commit なし)
- 提案(ユーザー): エージェントへの **入力トークン量を個体ごとに増減** させ、現実の人々の「世界に対する解像度(=見えている世界の細かさ)」の個体差を再現する。
- 親エージェント(Fable)の仮説: 本提案の価値は **コスト削減ではなく実験軸** にある(入力削減はコスト削減に効きにくい=compute-efficiency の先行結論)。本書はこの仮説を検証し、実装計画に必要な理論的接地・ノブ候補・交絡/検証・スケール実効を揃える。
- 既読前提(重複を避け差分を書く):
  - [`compute-efficiency.md`](compute-efficiency.md) §1-A/§3.2/§3.5(**decode 支配=入力削減はコスト削減に効きにくい**・「情報量を削るより同じ計算を安く回せ」)
  - [`token-budgets.md`](token-budgets.md) §2.2(入力実測 530〜1,040 tok)・**§4.1(エージェント別ランダムトークン制限=ただし "出力側" の思考LOD)**
  - [`agent-lod-deepdive.md`](agent-lod-deepdive.md)(**推論量・モデル級**の個体軸LOD=本提案の「逆の視点」。共有する危険=trait 相関の裏口)
  - 実物: [`cognition/deliberate.py::build_prompt`](../../src/society/cognition/deliberate.py)・[`world/perception.py::salience_gate`](../../src/society/world/perception.py)・[`agents/memory.py`](../../src/society/agents/memory.py)・[`worldview.py`](../../src/society/worldview.py)
  - [`devlog-compressed.md`](../log/devlog-compressed.md) Block #6(**trait 由来割当=生得性の裏口** / **manifold collapse=属性を盛ると均質化**)
- 出典方針: 一次ソース URL 必須。二次情報は 🔶。未確認は「**要検証**」と明記(捏造禁止)。

---

## 0. 本シミュへの示唆(結論先出し・8行)

1. **入力解像度は実験軸として筋が良い**。理論的接地は強い: Rational Inattention(Sims 2003)は「経済主体は有限の Shannon 情報処理容量を持ち、注意を内生配分する」を定式化し、**個体別の入力トークン予算 = 個体別の情報処理容量 C_i** に素直に対応する。
2. **R1(呼数の k 非依存)には安全**。入力トークン量を変えても **LLM 呼数は 1 本も増減しない**(プロンプト内容/長さが変わるだけ)。これは token-budgets §4.1 の出力キャップと同型で、モデル級 LOD(agent-lod)や発火LODより **R1 を汚さない**。
3. ただし **これは token-budgets §4.1 とは別のノブ**。§4.1 は「出力予算=思考の深さ」(decode 側)。本提案は「入力量=世界の見え方」(prefill 側=知覚・記憶・内省の注入量)。両者は直交する 2 因子で、混同すると実験が濁る。
4. **入力を削ると行動は実際に歪む**(context rot / lost-in-the-middle は実証済み)。これは「機能」でもあり「危険」でもある: 現実の低注意個体を再現できる一方、**単なる情報飢餓を "個体差の再現" と誤称するリスク**を生む(§4 検証が必須)。
5. **最大の危険は "計算量/情報量そのものが交絡因子" になること**。入力予算が世界改変者になりやすさと相関すると、割当が Y_external の分散を製造する = agent-lod Q3 の第二の裏口が入力側でも再来する。
6. **10万体スケールでの実効はある(限定的)**。decode 支配なのでコスト主レバーではないが、KV キャッシュは文脈長×バッチに線形で、**メモリ律速域では入力半減がバッチ拡大→スループット改善**を買う(§3.6)。ただし絶対値は我々の短プロンプトでは小さい。
7. **既に半分実装済み**: `salience_gate`(Cowan 2001=約4チャンクの容量制約ゲート)が feed/news に効いている。**これを個体別 k にするのが最小の一歩**。
8. **触ってはいけない一線**: `beliefs`(内省の書き戻し=k の行動流入路 D7)を解像度ノブに含めない。ここを削ると k そのものを操作してしまう。

---

## 1. この提案は既存3書と何が違うのか(差分の明示)

| 観点 | token-budgets §4.1 | agent-lod-deepdive | **本提案(入力解像度)** |
|---|---|---|---|
| 変えるもの | **出力**予算(max_tokens=思考の深さ) | **モデル級/推論量**(誰を安く回すか) | **入力**の情報量(何がどれだけ見えるか) |
| 側 | decode | モデル選択+decode | **prefill(注入内容)** |
| 現実の対応物 | 思考の熟慮の深さ(System 2 の長さ) | 認知資源の総量 | **世界に対する解像度(知覚・記憶の細かさ)** |
| コスト効果 | 中(decode 支配なので効く) | 大 | **小**(prefill は安い=Fable 仮説を支持) |
| R1(呼数 k 非依存) | ◎ 呼数不変 | △ 割当で呼数/モデルが動く | **◎ 呼数不変(内容のみ変化)** |
| 主目的 | 予算の右サイズ化 | スケール確保 | **個体差の実験的再現** |

→ 本提案の独自価値は **「コスト」でも「スケール」でもなく、"世界の解像度の個体差" という現実整合の実験因子** を、R1 を汚さずに導入できる点にある。Fable 仮説(価値は削減でなく実験軸)は文献・コード両面から支持される。

---

## 2. 解像度ノブ候補の表(`build_prompt` の実構成要素ベース)

`build_prompt`(deliberate.py L92-268)が実際に注入する行を、**情報量をどう増減するか × 現実の何に対応するか × 危険度** で棚卸しする。現行の実スライスも併記。

| # | 注入要素(コード) | 現行の量 | 増減ノブ | 現実の対応物 | R1 | 危険度・注記 |
|---|---|---|---|---|---|---|
| 1 | `nearby_names`(近くにいる人) | 同席者を全列挙(company) | **列挙上限 N_people** | **注意の幅**(同時に把握できる人数=WMC/Cowan≈4) | ◎ | 低。`salience_gate` の k を人物へ拡張。**最有力** |
| 2 | `nearby_pois`(周りの店・場所) | 先頭 **3件**(`[:3]`) | 件数 N_poi | **環境走査の幅**(街をどれだけ見ているか) | ◎ | 低。既に定数スライス=個体別化しやすい |
| 3 | `feed_texts`(SNSタイムライン) | 先頭 **3件**(`[:3]`) | 件数 N_feed | **情報環境の帯域**(OASIS RecSys の可視件数) | ◎ | 低。先行例に最も直接対応(§3.4) |
| 4 | `mem.retrieve(n=3)`(想起) | **3件** | 想起件数 n | **記憶想起の解像度**(過去をどれだけ引けるか) | ◎ | 低〜中。GA は top-k 3〜5 が実効域(§3.4) |
| 5 | `mem.recent(4)`(直近の出来事) | **4件** | 件数 | 短期記憶の幅 | ◎ | 低 |
| 6 | `day_summaries[-1]`(昨日の日記) | 直近1日・要約 | 詳細度/日数 | **記憶の要約解像度**(memory-100day-audit の畳み) | ◎ | 中。要約の粗さ=記憶の解像度そのもの |
| 7 | `crowd_line`(群衆の視覚情報) | 実在集計1行 | 詳細度 ON/OFF | 視覚的な場の把握 | ◎ | 低 |
| 8 | `familiar_places[:3]`(認知地図) | 先頭 **3件** | 件数 | Lynch 認知地図の広さ | ◎ | 低 |
| 9 | worldview 3行(`wv_expect/self/norm`) | 閾値超のみ自然文 | 閾値/ON-OFF | **内省の言語化・世界への手応え** | ◎ | 中。閾値ゲート=量でなく質。個体別化は解釈が濁る |
| 10 | `self_model`/`implicit_self`(自己理解) | 内省の産物 | 詳細度 | 自己認識の解像度 | ◎ | 中。内省由来=k と近接、慎重に |
| — | **`beliefs[-3:]`(内省の書き戻し)** | 直近3件 | **触らない** | — | — | **★禁止**: k の行動流入路(D7)。解像度ノブに含めると k を直接操作してしまう |
| — | 全員共通1行群(`date/weather/norm/digest/institutions`) | 各1行 | 全員一律のみ | 環境の客観情報 | ◎ | 個体別化すると "全員共通=k非依存" の設計が崩れる。**個体差の対象外に保つ** |

**表からの読み**: 個体別化に **筋が良いのは "件数で量れる知覚・記憶チャネル"(#1〜#6)**。自然文の閾値ゲート(#9)や自己モデル(#10)は「量」でなく「質」なので解像度軸としては濁る。**`beliefs` と全員共通行は個体差の対象外に固定**するのが R1・k\* を守る前提。

---

## 3. 理論的接地(Web 一次ソース)

### 3.1 Rational Inattention(接地の主柱)— 使えるか: **強く使える(ただし1つ留保)**

- **Sims (2003) "Implications of Rational Inattention"**(JME): 経済主体は **有限の Shannon 情報処理容量(bits)** を持ち、その容量制約下で注意を配分する。容量が減ると「同じ問題で信号にノイズを増やしたのと同じ効果」= 反応が鈍く・遅く・ばらつく。[sims.princeton.edu PDF](http://sims.princeton.edu/yftp/Gerzensee/info.pdf) / [ScienceDirect JME](https://www.sciencedirect.com/science/article/abs/pii/S0304393203000291)
  - → **入力トークン予算 = 情報処理容量 C_i** の直接的な操作化。これが本提案の理論的背骨。「低容量個体は世界にノイズ越しに反応する」= 我々が入力を削った個体に期待する挙動そのもの。
- **Matějka & McKay (2015, AER)**: 情報コストを Shannon エントロピーで測ると、RI の選択確率が **多項ロジット** になる。= **情報を削ると選択がより確率的(ランダム)になる**を理論が予言。[AER](https://www.aeaweb.org/articles?id=10.1257%2Faer.20130047) / [PDF](http://home.cerge-ei.cz/matejka/logit_fm_am.pdf)
  - → 「入力を削ると行動がどう歪むか」= **選択のランダム性上昇**。§3.3 の LLM 実証(context rot で出力が不安定化)と同じ向き。
- **Fosgerau et al. (2020, IER)**: 離散選択と RI の一般同値。情報コストが一般化エントロピーなら、RI の選択確率は任意の加法的ランダム効用モデルと観測同値。[Wiley IER](https://onlinelibrary.wiley.com/doi/full/10.1111/iere.12469)
- **個人差の実証(接地の要)**: Princeton の psychometrics-of-RI 研究は **RI 容量の個人差を心理測定で推定可能**と示す。「均質な標本でも情報コストの個体差は圧倒的」。[Princeton: Leveraging Psychometrics of Rational Inattention](https://collaborate.princeton.edu/en/publications/leveraging-psychometrics-of-rational-inattention-to-estimate-indi)
  - → **C_i の個体差は実在し測れる** = 「入力予算を個体で振る」ことの現実整合の裏付け。

> **留保(重要)**: RI の核心は「固定容量を **内生的に最適配分** する(何に注意を割くか自体を選ぶ)」こと。単純なトークン切り詰めは **外生的な容量差**であって内生配分ではない。厳密には (a) 容量 C_i の個体差 = 入力予算、(b) 内生配分 = **どの情報を残すか**(=`salience_gate` の重み付け top-k が最も近い既存機構)、の2段で表現するのが正しい。ブラント(無差別切り詰め)は RI の "容量" 部分だけを近似し、"配分" 部分を放棄した粗いモデルである点を計画に明記すべき。

**操作化のメモ(実装計画者向け)**: RI の容量は bits だが、我々のノブは「注入する項目数/トークン数」。両者を無理に等式で結ぶ必要はなく、**「C_i を単調に反映する序数スカラ R_input_i」**として扱えば十分(RI は容量↓→反応のノイズ↑を予言する=順序さえ保てば定性は一致)。実装上は **1個体1スカラ(例 0〜1)を、ノブ#1-#3 の件数上限に単調写像**するのが素直(高解像=`salience_gate` の k 大 + retrieve n 大 + feed 件数大)。「良い配分」を近似したいなら **k を減らす際に `salience_gate`(score 上位を残す)を使う**ことで、RI の "重要な信号を優先的に残す" 内生配分を安価に代理できる — ブラント切り詰め(先頭 N 件)より現実的。

### 3.2 知覚・注意の個人差(心理学)— 「見えている世界の細かさが人で違う」は**実証あり**

- **Working Memory Capacity (WMC) の個人差**: 高 WMC 者は注意制御・更新・抑制・二次記憶からの手掛かり検索が優れる。WMC 差は流動性知能・高次認知課題成績を予測する。[Unsworth & Engle, WMC & search efficiency (Mem & Cogn)](https://link.springer.com/article/10.3758/s13421-018-0827-3) / [WMC & visual search while reading](https://link.springer.com/article/10.3758/s13421-022-01357-4)
  - → **同時に把握できる項目数(注意の幅)が人で違う** = ノブ#1(nearby_names)・#4-5(記憶想起件数)の心理学的裏付け。Cowan (2001) の「焦点は約4チャンク」は既にコード(`salience_gate` docstring)が引いている。
- **Need for Cognition (NFC)**: 高 NFC 者は **提示された情報を超えて能動的に情報を探索し、より深く精緻化**する。低 NFC 者は少ない情報でヒューリスティックに処理。[Need for cognition (Wikipedia/Cacioppo-Petty)](https://en.wikipedia.org/wiki/Need_for_cognition) / [NFC & external information search under time pressure](https://www.sciencedirect.com/science/article/abs/pii/S0092656683710172)
  - → **情報探索量の個人差** = 入力解像度を「特性」でなく「振る舞い」として動機づける。ただし NFC は trait なので **これを割当基準にすると裏口(§4)**。
- **注意の幅(attentional breadth)の個人差**: 注意の広さ(broad/narrow)には **気質的な個人差**があり、global/local 課題で測った拡散/集中の傾向が attentional blink の大きさを予測する。気分でも変わる(**ポジティブ低覚醒=広がる / ネガティブ=狭まる**=broaden-and-build)。[Dispositional focus predicts attentional blink (APP)](https://link.springer.com/article/10.3758/APP.72.3.602) / [Positive emotions broaden scope of attention (Fredrickson, Cognition & Emotion)](https://www.tandfonline.com/doi/abs/10.1080/02699930441000238)
  - → **ノブ#1(知覚の幅=`salience_gate` の k)の直接の心理学的対応物**。我々は既に `mood_text` を持つので、将来は「気分で注意幅が動く」動的版も seam としてありうる(ただし状態依存=R1 注意)。
- **認知スタイル(field dependence/independence, Witkin)**: 場依存型=**全体的・社会志向**(社会的手掛かり・人に注意を割く)、場独立型=**分析的**(対象を文脈から切り離す)。安定した trait とされる。[Witkin et al. 1977, Field-dependent/independent styles (Review of Educational Research)](https://journals.sagepub.com/doi/10.3102/00346543047001001) / [Global/local perceptual style & field-independence (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC2864999/)
  - → **ノブ#1(nearby_names=対人)vs #2(nearby_pois=対象)の配分**が場依存/独立に対応する示唆。ただし「安定した trait」なので **これを割当基準にすると生得性の裏口の教科書例**(§4-2)。
- **総括**: 「人によって見えている世界の細かさ・向き先が違う」は WMC(容量)・NFC(探索動機)・注意幅・認知スタイルの複数系統で実証されている。**本提案は心理学的に根拠のある個体差を再現しようとしている**(でっち上げの軸ではない)。同時に、これらの現実の源泉が **軒並み trait** である事実は、「割当を trait 由来にしたくなる誘惑」が強いこと=裏口リスクが高いことを意味する。

### 3.3 LLM の入力情報量と出力の関係 — 「入力を削ると行動は歪む」は**実証済み**

- **Lost in the Middle (Liu et al. 2024, TACL)**: 関連情報が文脈の**中央**にあると精度が >30% 低下(U 字)。モデルは入力を一様に使わない。[ACL Anthology TACL 2024.tacl-1.9](https://aclanthology.org/2024.tacl-1.9/)(arXiv:2307.03172)
- **Context Rot (Chroma 2025, 技術報告)**: 18 モデル(GPT-4.1/Claude 4/Gemini 2.5/**Qwen3** 含む)で、**入力が伸びるほど単純な検索・複製ですら信頼性が落ちる**。無関係トークンを空白に置換しても性能は落ちる = 文脈長そのものが劣化要因。[Chroma Research: Context Rot](https://research.trychroma.com/context-rot)
  - → 我々の本選候補 Qwen3 系が対象に含まれる点は重い。**入力の量・構成が行動選択を左右する**ことの直接証拠。
- **含意の両面性**: これは「入力を削ると行動が劣化する」を保証する。**低解像度個体を作れる**(=個体差の再現に使える)一方で、**その劣化が "現実の低注意個体の挙動" と一致する保証はない**(単なるモデル失敗かもしれない)。§4 検証の核心。
- **多様性の逆説**: 入力(persona)を **盛るほど多様性は増えない**。「fine-grained な persona 詳細を足しても、出力長カットオフを指定するのに比べ多様性の利得は僅少」。[Lexical diversity via persona prompting (arXiv:2505.17390)](https://arxiv.org/html/2505.17390v1)
  - → **入力を増やす方向は限界効用が早く飽和**(AGA の believability 飽和と同型)。**面白いのは削る側**(下限で行動がどう崩れるか)。本提案が「増減」のうち **減の側に実験的価値が偏る**ことを示唆。

### 3.4 マルチエージェント LLM シミュの知覚制限 — 「入力を絞る」は**既に標準。個体差をつけた例は乏しい**

- **Generative Agents (Park et al. 2023)**: perceive は範囲内の観測を拾い、retrieve は recency+importance+relevance で **top-k(実効3〜5件)** に絞って文脈窓に収める。「10件超はほぼ効かない」。[arXiv:2304.03442](https://arxiv.org/abs/2304.03442) / [top-k 3-5 の実効域(二次解説)🔶](https://agentpatterns.ai/agent-design/generative-agents-memory-stream/)
  - → **入力を絞るのは GA 以来の標準設計**。我々の `retrieve(n=3)` はこの相場どおり。
- **OASIS (100万体, camel-ai 2024)**: **RecSys が各エージェントに可視な投稿を選別**(interest/hot-score ベース)。「RecSys が各エージェントの情報可視性を決める」。[arXiv:2411.11581](https://arxiv.org/abs/2411.11581) / [camel-ai blog](https://www.camel-ai.org/blogs/oasis)
  - → **フィード可視件数の制御は SNS シミュの中核機構**。ノブ#3(feed_texts 件数)はこれに対応。ただし OASIS は RecSys で内容を選ぶが、**"可視件数を個体の認知容量として振る" 発想は前面に無い**(要検証)。
- **所見**: 「入力を絞る」設計は標準だが、**その絞り幅を個体の認知容量差として明示的に振った LLM-ABM は管見の限り見当たらない(要検証)**。= 本提案は既存機構(top-k / RecSys)の自然な拡張でありつつ、**"個体差の軸として使う" 点に新規性**がある。

### 3.5 System 1 / System 2 と思考深度の自己選択 — ユーザーの理想への接地

- **Thinking Fast and Slow in AI (Booch, Ganapini et al. 2021)**: メタ認知エージェントが「System 2 solver を使うべきか」を資源制約・過去経験・期待報酬から**内省的に裁定**。速く粗い第1相 → 必要なら熟慮の第2相。[arXiv:2110.01834](https://arxiv.org/pdf/2110.01834)
- **Metacognition in Generative Agents (2024)**: 生成エージェントに内省(metacognition)を持たせ目標指向行動を改善。[arXiv:2401.10910](https://arxiv.org/pdf/2401.10910)
- **Anytime algorithms / feedback-aware thinking depth**: 外部フィードバックで「思考の深さ(forward pass 数)」を動的スケール。難易度と資源で計算配分。
  - → ユーザーの理想「各エージェントが一貫した思考の深さ・回数を自分で選ぶ」= **メタ認知的な熟慮コスト裁定**の系譜。ただし **"自分で選ぶ"(内生・状態依存)は呼数/計算量を状態依存にする=R1 と正面衝突**(agent-lod §2-3 と同じ警告)。本提案の入力予算は **"自分で選ぶ" ではなく "初期化時固定の容量差"** に留めれば R1 安全。内生選択は将来 seam。
- **無意識的行動の割合(人間の実証)**: 日常行動の **約43〜45% が習慣的・自動的**に(別のことを考えながら)遂行される(Wood et al. 2002 の経験サンプリング)。[Wood & Neal 2007, Psych Review PDF](https://dornsife.usc.edu/wendy-wood/wp-content/uploads/sites/183/2023/10/wood.neal_.2007psychrev_a_new_look_at_habits_and_the_interface_between_habits_and_goals.pdf)
  - → **日常の約半分は熟慮を要しない**。我々の `routine.py`(非LLM日課)+発火LOD(4.1〜11.4%)は既にこの相場に整合。**入力解像度は "熟慮する残り半分" の中の個体差**を扱う位置づけ。

### 3.6 10万体スケールでの入力削減の実効 — **ある。ただし限定的で二次的**

- **compute-efficiency の先行結論を継承**: vLLM は **decode 支配**、prefill(入力)は安い。→ 入力削減はコスト主レバーではない(§1-A)。**本提案の主目的をコスト削減に置くのは筋が悪い**を再確認。
- **ただし KV キャッシュ経由の実効はある**: KV キャッシュのメモリは **バッチ×文脈長に線形**(`2·n·h·d·e·b·l`)。文脈長が伸びるとトークン間レイテンシも入力長に線形。**固定メモリ予算下で文脈 1,024→4,096 でスループット 66.7% 低下**の実測。[vLLM KV-cache tweaks 🔶](https://atul4u.medium.com/mastering-vllm-kv-cache-10-battle-tested-tweaks-for-maximum-token-throughput-9101a4917c5a) / [vAttention (arXiv:2405.04437)](https://arxiv.org/pdf/2405.04437)
  - → **メモリ律速域では入力半減 → KV 容量が空く → バッチ拡大 → スループット改善**。10万体で 7GPU に詰め込む局面では、入力削減が「呼あたりコスト」でなく「同時処理数」を買う。
- **我々での実効の見積り(正直に)**: 我々の入力は既に 530〜1,040 tok と短い(token-budgets §2.2)。半減しても ~500 tok の節約で、A5000 24GB の KV 予算に対する寄与は **中〜小**。**「10万体で入力半減が買えるのは、律速がメモリのときの限定的なバッチ余地」**であって、桁を動かすレバーではない。→ **スケール正当化としては弱い。実験軸としての正当化が主**。
- **概算(封筒裏・要 `bench.py` 実測)**: KV は文脈長に線形。生成中は各トークンが全 KV を見るので、**入力 1,040→520 tok の半減はプレフィル KV フットプリントも約半減**し、同一 VRAM でその分だけ concurrent なリクエスト(=バッチ)を増やせる。ただし我々の律速は decode(出力トークン生成)で、reflect の思考込み出力(token-budgets)が総トークンを支配する。**入力半減が効くのは "KV メモリがバッチ上限を決めている GPU 充填局面" に限られ、decode 律速局面では throughput をほぼ動かさない**。→ 「10万体で入力半減は何を買えるか」の答え=**メモリ律速時の中程度のバッチ拡大(体感で数%〜十数%オーダー、絶対値は本選機実測待ち)**であって、桁ではない。**この "小さいが個体差の実験に付いてくる副産物" という位置づけが、compute-efficiency の「入力削減は主レバーでない」を否定せず補完する**。

---

## 4. 交絡と検証(この提案の生死を分ける節)

### 4-1. R1(呼数の k 非依存)には安全 — ただし条件付き

- 入力トークン量を変えても **generate() の呼数は不変**(プロンプト内容/長さのみ変化)。token-budgets §4.1 の出力キャップと同じく **R1 を構造的に壊さない**。発火LOD・モデル級LOD より安全。
- 条件: 割当は **初期化時1回・run 全体で固定**(covariate としてログ)。**状態依存に振る(「難所で解像度を上げる」)と呼数が状態依存化して R1 が崩れる**(agent-lod §2-3 の budget-aware 系と同じ罠)。**内生的な自己選択は本版では入れない**。

### 4-2. 裏口(a): 割当が trait と相関すると生得性の注入

- **Block #6 / agent-lod Q3 の警告がそのまま該当**: 入力予算を trait(例: NFC・知能因子)由来で振ると、**R²(k) に「生得的に解像度が高い個体が世界を変えやすい」を裏口注入**する。The Sims の trait 条件付き背景イベントと同じ構造(agent-lod 2-1)。
- **回避**: 割当を **trait 非依存・k 非依存の独立決定論ストリーム 1 本**(token-budgets §4.1 と同じ流儀)、または **明示指定(実験条件として透明)**。trait 連動をやるなら「**生得性の効果を測る実験条件そのもの**」としてのみ(既定は無相関)。

### 4-3. 裏口(b): 情報量そのものが交絡因子(agent-lod Q3 の第二の裏口が入力側で再来)

- trait と無相関でも、**入力予算が高い個体ほど世界改変者になりやすい**なら、割当自体が Y_external の分散を製造する。これは「解像度の個体差の再現」ではなく「**実験デザインが結果を作る**」。
- **検証要件**: 入力予算を **k と直交な因子**として扱い、k を固定(または均衡)して掃引。**予算 → Y_external の用量反応を測り、"予算が世界改変を単調に決める" なら、それは個体差の再現でなく人工物**と判定する基準を事前登録。

### 4-4. 「入力を削った個体の行動劣化」を "個体差の再現" と主張するのに必要な検証

context rot(§3.3)は「入力を削れば行動は劣化する」を保証する。**劣化 ≠ 現実の低解像度個体の挙動**。主張には最低限:

1. **劣化の質の照合**: 低予算個体の劣化が「JSON 破綻・空応答・反復」(=モデル失敗)でなく「**話題の狭さ・環境無視・記憶の薄さ**」(=低注意者らしい行動)であることを、`parse_action` fallback 率 / distinct-n / 行動レパートリー曲線(AGA Fig.7 型)で分離する。fallback 率が予算で跳ねるなら **それは飢餓であって解像度でない**。
2. **用量反応の形**: 予算 → 行動品質が **なだらかな飽和曲線**(RI/AGA が予言する限界効用逓減)なら現実整合。**崖(ある閾値で急落)なら技術的破綻**の疑い。
3. **現実側のアンカー**: 「見えている世界の細かさ」の個体差を、可能なら人間データ(NFC・注意課題)の分布形と照合。少なくとも **分布形(高解像少数・中解像多数)を事前に決め**、事後の盛りを避ける。
4. **manifold collapse への注意**: 入力を "増やす" 側は多様性を増やさない(§3.3・E5 の自プロジェクト所見)。**増減の "増" に期待しすぎない**設計(離散水準で下限側を密にサンプル)。

### 4-5. 決定論・no-fingerprint への適合

- 件数スライス(#1-#8)は **既存機構の定数を個体別パラメータに変えるだけ**=新規乱数 draw 不要なら決定論に非干渉(token-budgets §4.1 と同じ「パラメータであって draw ではない」)。
- `salience_gate` は score 上位 K を **元の並び順で**返す決定論ゲート(perception.py L106)。**k を個体別にしても決定論・no-fingerprint(score は不透明 float)を保てる**。
- キャッシュ: 入力が変われば別プロンプト=別キー(cache.py)。予算水準ごとに独立キャッシュ=各 seed で決定論、比較ランは実LLM再走(token-budgets §3.3 と同じ)。

### 4-6. 実験設計スケッチ(token-budgets §4.1 との直交)

token-budgets §4.1 は **出力予算(思考の深さ=decode)** をエージェント別に振る設計を既に提案済み。本提案(入力解像度=prefill)は **それと直交する第2因子**なので、両者を **2因子直交デザイン**にすると「**世界を変えるのは "多く見ている" ことか "深く考える" ことか**」を初めて分離検定できる(これは §1 の表が示す本提案の独自価値の実験化)。

- **因子**:
  - **R_input(入力解像度)**: ノブ#1-#3 を束ねた 1 スカラ(例: 知覚/記憶/フィードの件数を同時に低・中・高)。RI の容量 C_i に対応。
  - **D_output(思考深度)**: token-budgets §4.1 の出力キャップ(低=128 / 高=512)。
- **割当**: 両因子を **個体ごとに独立・初期化時固定**(相関≈0)。**trait 非依存の独立決定論ストリーム**(§4-2)。k は固定または均衡(§4-3)。
- **分布候補**: **離散水準を主**(例 R_input ∈ {狭, 中, 広}、D_output ∈ {浅, 深})で用量反応をクリーンに。**下限側を密に**サンプル(§3.3: 増やす側は多様性が飽和・削る側に情報がある)。連続の対数一様を補助アームに。
- **従属変数**: Y_external 成分(transmission/label_adopt/sns_reach/世界改変アクション)+ `parse_action` fallback 率(飢餓の分離)+ distinct-n・行動レパートリー曲線(§4-4)。
- **読み**: **主効果** = 見る量 vs 考える深さのどちらが世界改変に効くか。**交互作用** = 「広く見て深く考える」が相乗か頭打ちか。**compute-matched アーム**(総トークン=入力×頻度をセル間で一致)を1本置くと「固定予算を入力に振るか出力に振るか」の純粋配分比較になる。
- **前提**: mock は入力量に反応しない部分がある(出力長は固定)ので、**R_input の効果は実LLM(ollama/vLLM)でしか出ない**。§4.1 と同じく **各水準は独立キャッシュ=決定論**、新 stream 不要=既定挙動に非干渉。**実装可否は実装前にユーザー合意**(本書は提案のみ)。

---

## 5. ノブ候補の上位3つ(実装計画者向けの絞り込み)

**選定基準**: 件数で量れる/現実の対応物が明確/R1 安全/beliefs(k 路)と分離可能/既存 seam がある。

1. **対人・環境知覚の幅**(`nearby_names` 列挙上限 + `nearby_pois` 件数, 現行 `[:3]`)
   — 現実対応=**注意の幅**(WMC/Cowan≈4・RI 容量)。**`salience_gate` の k を sim 全体(現 `affectcfg["salience_k"]`)から個体別に拡張する**のが最小改修。最有力。
2. **記憶想起の解像度**(`mem.retrieve(n=3)` + `mem.recent(4)` + `day_summaries` 詳細度)
   — 現実対応=**記憶想起・要約の細かさ**(WMC の二次記憶検索の個人差)。GA の top-k 3〜5 が実効域=個体別に 1〜5 で振れる。**`beliefs` は絶対に含めない**。
3. **情報フィードの帯域**(`feed_texts` 件数, 現行 `[:3]`)
   — 現実対応=**情報環境の可視量**(OASIS RecSys visibility)。先行例に最も直接対応し、SNS 経路の伝播(sns_reach)と Y_external の関係を解像度で変調できる。

補助: worldview 行(#9)・自己モデル(#10)は「質(自然文の閾値)」であって「量」でないため、解像度軸としては第2優先(個体別化すると解釈が濁る)。

### 5-1. 最小手→拡張の順序(実装の段階)

1. **最小手**: `affectcfg["salience_k"]`(現 sim 全体・既定0)を **個体別 k** に拡張し、feed に加え **nearby_names / nearby_pois にも適用**。1個体1スカラ R_input_i を件数上限へ単調写像(§3.1 操作化メモ)。**新規乱数なし=決定論非干渉**。
2. **第2手**: `retrieve(n)` / `recent(n)` を個体別に。**`beliefs` と全員共通行は固定のまま**(§2 表の禁止・対象外)。
3. **検証ラン**: §4-6 の 2因子(R_input × D_output)を実LLM で小規模(≤24step スモーク→数 seed)。fallback 率と distinct-n を必ず分離集計(§4-4)。
4. **拡張(将来 seam)**: 気分連動の動的注意幅(§3.2)や RI 内生配分の明示化。ただし **状態依存化は R1 を脅かす**ため、動的版は別提案として合意を取る。

### 5-2. 「やらない」と判断すべき条件(反証の事前設計)

以下のいずれかが検証ランで観測されたら、**「入力解像度=個体差の再現」という主張は取り下げるか設計をやり直す**:

- (K1) 低 R_input 個体の劣化が主に **`parse_action` fallback / 空応答 / 反復**(=技術的飢餓)で、話題の狭さ・環境無視(=低注意者らしさ)として現れない(§4-4-1)。
- (K2) 予算→Y_external が **飽和曲線でなく崖**(閾値急落)= モデル破綻の疑い(§4-4-2)。
- (K3) R_input が **k と交絡**(k を固定しても予算が世界改変を単調決定)= 割当が結果を製造(§4-3)。
- (K4) 現実アンカー(NFC/注意課題の分布形)と照合できず、**分布を事後に盛る**しかない(§4-4-3)。

→ これらを**事前登録**しておくことが、本提案を「現実整合の実験」に留め「都合の良い個体差の捏造」に堕とさない安全弁。

---

## 6. 出典リンク

**Rational Inattention(理論的接地の主柱)**
- Sims (2003) Implications of Rational Inattention (JME): [PDF](http://sims.princeton.edu/yftp/Gerzensee/info.pdf) / [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0304393203000291)
- Matějka & McKay (2015, AER) RI → Multinomial Logit: [AER](https://www.aeaweb.org/articles?id=10.1257%2Faer.20130047) / [PDF](http://home.cerge-ei.cz/matejka/logit_fm_am.pdf)
- Fosgerau et al. (2020, IER) Discrete Choice ↔ RI General Equivalence: [Wiley](https://onlinelibrary.wiley.com/doi/full/10.1111/iere.12469) / [arXiv:1709.09117](https://arxiv.org/pdf/1709.09117)
- Leveraging Psychometrics of RI to Estimate Individual Differences in Cognitive Control (Princeton): [collaborate.princeton.edu](https://collaborate.princeton.edu/en/publications/leveraging-psychometrics-of-rational-inattention-to-estimate-indi)

**知覚・注意の個人差(心理学)**
- Unsworth & Engle, WMC & search efficiency (Mem & Cogn): [Springer](https://link.springer.com/article/10.3758/s13421-018-0827-3)
- WMC & visual search while reading (Mem & Cogn 2022): [Springer](https://link.springer.com/article/10.3758/s13421-022-01357-4)
- Need for Cognition (Cacioppo & Petty ; overview): [Wikipedia](https://en.wikipedia.org/wiki/Need_for_cognition) / [NFC & external info search under time pressure](https://www.sciencedirect.com/science/article/abs/pii/S0092656683710172)
- 注意の幅の気質差(dispositional focus → attentional blink): [Springer APP](https://link.springer.com/article/10.3758/APP.72.3.602) / broaden-and-build [Fredrickson (Cognition & Emotion)](https://www.tandfonline.com/doi/abs/10.1080/02699930441000238)
- 認知スタイル(field dependence/independence, Witkin): [Witkin et al. 1977 (Rev. Educ. Res.)](https://journals.sagepub.com/doi/10.3102/00346543047001001) / [Global-local & field-independence (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC2864999/)
- 習慣=日常行動の約43〜45%(Wood & Neal 2007, Psych Review): [USC PDF](https://dornsife.usc.edu/wendy-wood/wp-content/uploads/sites/183/2023/10/wood.neal_.2007psychrev_a_new_look_at_habits_and_the_interface_between_habits_and_goals.pdf)

**LLM の入力情報量↔出力**
- Lost in the Middle (Liu et al. 2024, TACL): [ACL Anthology](https://aclanthology.org/2024.tacl-1.9/)(arXiv:2307.03172)
- Context Rot (Chroma 2025 技術報告 / Qwen3 含む): [Chroma Research](https://research.trychroma.com/context-rot)
- Lexical diversity via persona prompting(詳細を盛っても多様性は増えない): [arXiv:2505.17390](https://arxiv.org/html/2505.17390v1)
- Quantifying the Persona Effect in LLM Simulations: [arXiv:2402.10811](https://arxiv.org/html/2402.10811v2)

**マルチエージェント知覚制限**
- Generative Agents (Park et al. 2023, top-k 想起): [arXiv:2304.03442](https://arxiv.org/abs/2304.03442)
- OASIS (100万体, RecSys が可視性を制御): [arXiv:2411.11581](https://arxiv.org/abs/2411.11581) / [camel-ai](https://www.camel-ai.org/blogs/oasis)

**System 1/2・思考深度の自己選択**
- Thinking Fast and Slow in AI (Booch, Ganapini et al. 2021): [arXiv:2110.01834](https://arxiv.org/pdf/2110.01834)
- Metacognition in Generative Agents (2024): [arXiv:2401.10910](https://arxiv.org/pdf/2401.10910)

**スケール(KV キャッシュ / prefill vs decode)**
- vAttention: Dynamic Memory Management for Serving LLMs (arXiv:2405.04437): [PDF](https://arxiv.org/pdf/2405.04437)
- 🔶 vLLM KV-cache tweaks(文脈長×バッチ線形・66.7% スループット低下): [Medium](https://atul4u.medium.com/mastering-vllm-kv-cache-10-battle-tested-tweaks-for-maximum-token-throughput-9101a4917c5a)

**リポジトリ内(根拠の中心)**
- [`docs/research/compute-efficiency.md`](compute-efficiency.md) §1-A/§3.2/§3.5(decode 支配・入力削減の低効果)
- [`docs/research/token-budgets.md`](token-budgets.md) §2.2/§4.1(入力実測・出力側の個体別トークン制限)
- [`docs/research/agent-lod-deepdive.md`](agent-lod-deepdive.md)(モデル級/推論量の個体軸LOD・trait 裏口・計算量交絡)
- 実装: [`cognition/deliberate.py::build_prompt`](../../src/society/cognition/deliberate.py) / [`world/perception.py::salience_gate`](../../src/society/world/perception.py)(Cowan 2001) / [`agents/memory.py`](../../src/society/agents/memory.py)(retrieve top-k) / [`worldview.py`](../../src/society/worldview.py) / [`factors/affect.py`](../../src/society/factors/affect.py)(`salience_k`)
- [`docs/log/devlog-compressed.md`](../log/devlog-compressed.md) Block #6(trait 由来割当=生得性の裏口 / manifold collapse)

> 正直な記録(要検証): (i) RI は「容量」と「内生配分」の2部からなり、ブラントなトークン切り詰めは容量部の粗い近似で配分部を放棄している(§3.1 留保)。(ii) 「フィード可視件数を個体の認知容量として振った」LLM-ABM の先行例は管見の限り無い(§3.4)=新規性の裏返しで前例の安全網が無い。(iii) KV キャッシュ経由の入力削減の実効(§3.6)は 🔶 二次ソースの相対比較に依拠し、我々の A5000×7・短プロンプトでの絶対値は `bench.py` 実測で確定すること。(iv) 「入力削減による劣化が現実の低注意者らしいか」(§4-4)を直接測った研究は見当たらず、我々自身の検証(fallback 率 vs distinct-n の分離)が必須。
