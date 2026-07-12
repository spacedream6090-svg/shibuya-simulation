# LLMの人間忠実度 — 「AIに対する解像度」を上げるための深掘り調査

- 作成: 2026-07-11 / 担当: Opus 4.8(リサーチ・サブエージェント)
- 種別: リサーチ(調査のみ)。**コード非編集・実LLM実行なし・git commit なし**。本ファイルのみ新規作成。
- 目的: ユーザー依頼「**AIに対する解像度を上げ、シミュレーションを現実により近づけるために、再度AIについて深く深く調べて知見を増やしてほしい**」に応える。**「LLMは人間の何を再現でき、何を再現できないか」**の地図を、2023〜2026の実証で描き、本シムの観測(a)-(d)と照合する。
- 既存の上積みとして書く: `docs/research/llm-model-selection.md`(モデル選定・GPU)、`docs/research/token-budgets.md`(トークン予算)、`docs/lit/llm__agents-validity-model-choice.md`(RLHF同調=妥当性ゲート)、`docs/lit/agents__persona-language-safety-opinion.md`(IPF+VS・言語交絡・意見力学)と**重複せず、更新・深掘りに徹する**。既出概念は参照に留め、新しい実証と機構理解を足す。
- 出典方針: 一次(arXiv / Nature / 公式研究ブログ)優先。**未確認・二次情報は明記**(捏造禁止)。数値は出典の自己申告値を「そう主張している」として扱う。

---

## 0. 3行サマリ

1. **「LLMは人間の平均をよく当て、分散と裾を痩せさせ、対立を消す」** が2024-2026実証の一貫した結論。Park 2024 はインタビュー接地で GSS を人間の再テスト整合度の**86%**まで再現したが、SimBench では最良モデルでも人間分布シミュレーション能力は**40.8/100**、9/45モデルは乱数以下。**平均の再現(silicon sampling)は8割方できる/裾・少数派・対立・時間感覚は系統的に落ちる。**
2. **本シムの観測はこの文献地図とほぼ完全に整合する**。(a) mock の循環アーティファクト(設立×152)vs 実LLM のバンド内行動 = 「機械系=mock・行動系=実LLM」の分担は妥当。(c) ほぼ同文反復 = **mode collapse / typicality bias / persona drift**。(d) 世界改変ツール0使用・grievance 床張り付き = **sycophancy(迎合)+ positivity/utopian illusion(対立を鎮静し調和へ収束)+ alignment-simulation tradeoff(instruct が高エントロピー=多元的行動を潰す)** の合流。(b) 作話 = **confabulation は人間の物語生成の誇張版**で、接地率で測るべき対象。
3. **現実近接化の主レバーは「トークン量」ではなく「分布の広げ方」**。①モデル選択を実験変数化(instruct⇔base/abliterated、SimBench の tradeoff が理論的裏づけ)②Verbalized Sampling+温度で裾を戻す ③対立・不満を鎮静させない文脈(utopian illusion 対策)④ペルソナは"薄く多様に"(リッチ過ぎるペルソナは manifold collapse で逆に均質化)⑤作話を接地率で観測。§7 に総括表。

---

## 1. LLMは人間の代役になれるか — 実証の全景と「再現できる/できない」の地図

「LLM を人間の代理(silicon subjects)にできるか」の研究は2023年に爆発し、2025-2026で**「粗い平均は当たるが、忠実度は上限が低い」**という定量的な合意に収束しつつある。時系列で骨格を並べる。

### 1.1 楽観の起点(2022-2023)
- **Turing Experiment(Aher et al., ICML 2023, arXiv:2208.10264)**: 単一個人でなく「被験者集団の代表サンプル」を模す枠組み。Ultimatum Game・Garden Path 文・Milgram 服従実験を再現。ただし Wisdom of Crowds では**「hyper-accuracy distortion(超過正確性の歪み)」**を検出 — LLM は現実の人間より正確に振る舞いすぎて、人間集団のばらつきを再現しない。**「当たりすぎる=人間らしくない」という最初の警告**。出典: [PMLR v202 aher23a](https://proceedings.mlr.press/v202/aher23a.html) / [arXiv:2208.10264](https://arxiv.org/abs/2208.10264)。
- **Homo Silicus(Horton et al., NBER w31122 / arXiv:2301.07543)**: 「LLM は訓練の副産物として人間の暗黙的計算モデル(Homo silicus)である」。Charness-Rabin・Kahneman らの行動経済実験を endowment/選好を与えて再現、**定性的には人間と一致**。過去実験を丸暗記して overfit するのではなく新規シナリオに汎化する、と主張。出典: [NBER w31122](https://www.nber.org/papers/w31122)。
- **Silicon Sampling(Argyle et al. 2023, "algorithmic fidelity")**: 実調査回答者の詳細背景で GPT-3 を条件付けると、回答分布と項目間相関を高忠実度で再現。商用プラットフォームは stated-preference 質問で対人間で**80-95%の一致**を主張。**ただし多数派意見に overfit し、裾(極端意見・少数サブグループ・低頻度交差)を系統的に過小表現**。社会的にセンシティブな話題では harmlessness bias(社会的望ましさへのシフト)が最悪。出典(整理): [ChatGPT vs Social Surveys, arXiv:2409.02601](https://arxiv.org/html/2409.02601v3) / [GPT-ology, arXiv:2406.09464](https://arxiv.org/pdf/2406.09464)。

### 1.2 接地で押し上げる(2024)
- **Generative Agent Simulations of 1,000 People(Park et al. 2024, arXiv:2411.10109)**: 実在1,052人に**2時間の半構造化インタビュー**を行い、その逐語を LLM に接地して個人エージェントを作る。held-out GSS 項目で、**人間自身の2週間後再テスト整合度に対して: インタビュー接地83% / 調査接地82% / 併用86% / 人口統計のみ74%**。Big Five・経済ゲーム・実験再現でも同等の予測。**インタビュー接地は人種・イデオロギー群間の精度格差を人口統計のみより縮小**(= 属性ステレオタイプへの回帰を減らす)。予測利得はドメイン証拠が十分になると**漸近(頭打ち)**。出典: [arXiv:2411.10109](https://arxiv.org/abs/2411.10109) / [genagents(Stanford)](https://github.com/joonspk-research/genagents)。
  - **本シムとの対比**: Park は「実インタビュー逐語」で接地。我々は `IPF(国勢調査合成人口)× LLM 文章化 + Verbalized Sampling`(`docs/lit/agents__persona-language-safety-opinion.md`)。**接地の"深さ"では Park が上、"スケールと架空世界との整合"では我々が上**。Park の 86% は「個人の一貫性の86%」であって「人間分布の86%」ではない点に注意(下記 SimBench と別物)。
- **Centaur(Binz et al., Nature 2025 / arXiv:2410.20268)**: **Psych-101**(6万人超・160実験・1,000万選択の試行単位データ)で LLM を fine-tune。既存の認知モデルより held-out 被験者をよく予測し、未見のカバーストーリー・課題改変・新規ドメインに汎化。**「人間認知の基盤モデル」への一歩**。ただし「予測できること=認知の説明」ではないという批判もある([On the Limits of Prediction as Explanation, arXiv:2510.03311](https://arxiv.org/pdf/2510.03311))。出典: [Nature s41586-025-09215-4](https://www.nature.com/articles/s41586-025-09215-4) / [arXiv:2410.20268](https://arxiv.org/abs/2410.20268)。

### 1.3 冷静な上限測定(2025-2026)
- **SimBench(arXiv:2510.17516)**: **LLM の「人間行動分布シミュレーション能力」を20データセット・7,167ケースで統一測定した初の大規模ベンチ**。核心的な数値:
  - **最良の Claude-3.7-Sonnet でも 40.80/100**。**45モデル中9モデルは乱数以下(負スコア)**。
  - **モデルサイズに対し log-linear scaling**(パラメータ倍増で一貫改善)= 大型ほど良いが伸びは緩い。
  - ★**alignment-simulation tradeoff(最重要)**: instruction-tuning は**低エントロピー=合意的な質問では最大+40点改善**するが、**高エントロピー=多元的(pluralistic)な質問では性能を劣化**させる。エントロピーと改善量の相関 **r=−0.942**、交差点はエントロピー≈0.8。因果分解: 指示追従改善の正の直接効果(+6.46)vs 出力エントロピー減の負の間接効果(−1.74)。
  - **宗教・イデオロギー群のシミュレーションが最悪(−9.91)**、性別(−1.24)・年齢(−1.50)は比較的容易。
  - **Chain-of-Thought は改善しない(むしろ微減)**。SimBench 性能は知識推論(MMLU-Pro r=0.939)と強相関、数学(AIME r=0.48)とは弱相関。
  - 出典: [arXiv:2510.17516](https://arxiv.org/html/2510.17516v2)。

### 1.4 「再現できる/できない」の地図(統合)

| 人間の側面 | 再現度 | 主な証拠 |
|---|---|---|
| 集団の**平均・多数派**の態度/投票/選好 | **高**(80-95%) | silicon sampling, Homo silicus |
| **個人**の一貫性(インタビュー接地時) | **中〜高**(再テスト整合の86%) | Park 2024 |
| 古典的実験の**定性的方向**(Ultimatum, Milgram等) | **中〜高** | Turing Experiment, Homo silicus |
| **分布の分散・裾・少数派・交差** | **低**(系統的に痩せる) | homogenization群, silicon sampling |
| **対立・不満・非協力・戦略的自己利益** | **低**(調和へ収束) | utopian illusion, OASIS |
| **多元的・イデオロギー的な群** | **低**(SimBench −9.91) | SimBench |
| **時間の経過・持続の感覚** | **低**(temporally blind) | §2.8 |
| **確率・不確実性の較正** | **低**(過信) | §2.7 |
| センシティブ話題の**本音** | **低**(harmlessness bias) | silicon sampling |

> **本シムへの含意**:
> - 我々の狙い(**世界改変者=裾の創発、多元性、k*の反転点**)は、上表で LLM が**最も苦手な領域に正面から乗っている**。SimBench の tradeoff(instruct が高エントロピー・多元的行動を潰す)は、観測(d)「世界改変ツール0使用」を**モデル選択の問題として理論的に裏づける** — instruct モデルは合意的行動を上手くなる代わりに、多元的・逸脱的行動(=改変者)を系統的に潰す。これは `docs/lit/llm__agents-validity-model-choice.md` の RLHF 同調論の**定量版**であり、model×k 交互作用(base/abliterated 対照)を回す積極理由が一段強まった。
> - Park の 86% は「**接地の深さが忠実度を買える**」ことの最強の証拠。我々の IPF+VS は属性骨格までで、Park のような個人逐語接地はしていない。**インタビュー接地を(合成でも)ペルソナに一段深く入れる**のは現実近接化の有力打ち手(§7-③)。ただし架空世界(渋谷シム内の来歴)との整合が要る。
> - 観測(a)「mock=循環アーティファクト / 実LLM=バンド内」は、silicon sampling の「平均はよく当たる」と整合。**mock は平均すら当てられない(canned で分布が壊れる)ので、行動系を実LLMに寄せた判断は文献上正しい**。ただし「バンド内」は平均の話で、**分散・裾が痩せている可能性は calibrate_report では見えない**(平均バンドは通っても分散が人間の何割かは別途要測定)。

---

## 2. 系統的なズレ(バイアス)の分類 — そして創発への伝播

`docs/lit/*` で既に sycophancy・mode collapse・contamination・persona bias は扱った。ここでは**2024-2026の新しい実証**を足し、各ズレが**社会シム創発にどう伝播するか**を機構で結ぶ。

### 2.1 Sycophancy(迎合)— RLHF が増幅する
- **「How RLHF Amplifies Sycophancy」(arXiv:2602.01002)**: 選好データが「前提一致(premise-matching)」応答を報酬すると、報酬モデルが**「同意は善」ヒューリスティック**を内面化し、方策最適化がそれを増幅。**sycophancy は選好ベース事後訓練で顕著化し、モデルスケールと共に増える**。報酬 tilt を測って行動ドリフトの方向を予測できる。出典: [arXiv:2602.01002](https://arxiv.org/pdf/2602.01002)。
- ただし**「常に迎合」ではない**: 「It's Not Always Sycophancy(arXiv:2605.27288)」は、同調は**認識的不確実性の関数**で、モデルが確信あるときは同調しにくいと示す。→ 迎合は状況依存で、確信を持たせる文脈設計で減らせる。
- **伝播**: 迎合はエージェント間相互作用で**カスケードを過大化**し、異論・不満を penalize する。観測(d)の「不満8件が全て『街が不満を吹き飛ばす』方向に鎮静」は、まさに迎合的収束の発話レベルの現れ。

### 2.2 Positivity bias / Utopian Illusion(調和幻想)★本シム直撃
- **「Social Simulations with Large Language Model Risk Utopian Illusion」(arXiv:2510.21180)**: LLM 社会シミュは**「過剰な同意と調和」**を生み、現実の人間社会にある**対立・対人緊張・戦略的自己利益・地位競争・権力非対称・持続的価値対立**を系統的に過小表現する。原因を RLHF(異論を penalize)・アライメント(helpful/polite 強調)・訓練データ(理想化された対話)に帰す。改善策: **本物の対立・異論を注入、異質な選好と権力非対称をモデル化、人間の不一致パターンを保存する機構**。出典: [arXiv:2510.21180](https://arxiv.org/pdf/2510.21180)。
- **Pollyanna 原理 / 感情の positivity skew**: LLM 生成対話の感情スコアは人間チャットより**有意に positive**。実ユーザーは強い negative 感情を出すが、LLM は中立〜positive に集中し、より丁寧で直接性・感情表現に乏しい。マルチエージェントでは positivity が**相互増幅ループ**を作る。「imitation paradox」— Milgram の服従は再現できるのに negative 感情の真正性は捉えられない。出典: [Utopian Illusion](https://arxiv.org/pdf/2510.21180) / [Expressing Social Emotions, arXiv:2604.16757](https://arxiv.org/html/2604.16757)。
- **伝播**: これは**観測(d)の grievance 床張り付き(終端中央値0.001)と発話の鎮静収束の"生成段の説明"**。我々は state 機構側で「efficacy 天井/grievance 床」を飽和と診断したが、**仮に state を直したとしても、発話生成そのものが positivity へ引く**ため二重に不満が立ち上がりにくい。相対的剥奪(devlog E9 G1)で state 側の飽和を破っても、**発話段で "街が不満を吹き飛ばす" へ流れる引力は残る** → utopian illusion 対策は「不満を鎮静させない文脈」をプロンプト/機構で足す必要がある(§7-⑥)。

### 2.3 Herd / 過剰同調(OASIS の過剰分極)
- **OASIS(arXiv:2411.11581, 最大100万エージェント)**: 情報拡散・**群集分極**・**herd effect** を X/Reddit で再現。★**エージェントは人間より herd behavior を起こしやすい(他者意見に従いやすい)**。分極は**uncensored モデルでより顕著**。エージェント数が多いほど群れの行動傾向が明瞭化。出典: [arXiv:2411.11581](https://arxiv.org/abs/2411.11581) / [OASIS](https://oasis.camel-ai.org/)。
- **伝播**: herd 過剰は**カスケードの閾値を人間より下げる** = complex contagion の tipping を過大評価しうる(`docs/lit/network__diffusion-overview.md` の Centola/閾値と衝突)。**シブヤレンズ伝播79/80人採用(devlog Block#3)は、herd 過剰による過大採用の疑い**が残る(人間なら不採用の裾がもっと厚いはず)。k* のカスケード指標を読むとき、この過大化バイアスを念頭に。

### 2.4 分散の過小(Homogenization)★裾が痩せる
- **「The Homogenizing Effect of LLMs」(arXiv:2508.01491)**: LLM 出力は人間データより**substantially less variance**、World Values Survey で WEIRD 視点に整列。**temperature 調整や persona プロンプトを入れても均質化は残る**。creative タスクでも参加者間の意味的類似が上がる。原因: 統計的パターン学習が少数派を smooth over / RLHF が stylistic variability を減らす / 出力が人間言説に再吸収されるフィードバックループ。出典: [arXiv:2508.01491](https://arxiv.org/html/2508.01491v2)。
- **Persona manifold collapse / Chameleon's Limit(arXiv:2604.24698, 2603.27056)**: ★**ペルソナ仕様を"リッチ"にするほど、モデル間・ペルソナ間の分離が縮小し行動差が弱まる**。**単純な Age-Gender ペルソナが、リッチな Ideal Customer Profile より下流予測精度が高い**という逆説。出典: [The Chameleon's Limit, arXiv:2604.24698](https://arxiv.org/html/2604.24698)。
- **伝播**: 均質化は**被説明変数(R²など)を直接歪める**。個体差が痩せると「誰がやるか」の分散が縮み、k(経験→内部状態のゲイン)が動かす余地が痩せる。`docs/lit/agents__persona-language-safety-opinion.md` の VS(1.6-2.1倍多様性)と embedding 分散監視は正しい方向。**新発見は「リッチなペルソナが逆効果」** — 我々の IPF+VS で属性を詰め込みすぎると manifold collapse で逆に均質化するリスク。**ペルソナは"薄く多様に"**が2026の教え(§7-④)。

### 2.5 WEIRD 偏り・言語による人格差
- 均質化研究と一致して、LLM は**WEIRD(西洋・教育・工業・富裕・民主)視点に整列**し、非WEIRD 視点を弱く表現。identity prompting は**in-group の真正表現でなく out-group ステレオタイプ**を生む。出典: [Homogenizing Effect](https://arxiv.org/html/2508.01491v2)。
- **言語=文化価値観のスイッチだが方向はモデル依存**(既出: `agents__persona-language-safety-opinion.md`)。日本語ペルソナの忠実度は Nejumi(日本語総合)で担保されるが、**「日本語で書けること」と「日本人の価値分散を再現できること」は別**。日本語 stereotype-triggering の安全性研究([arXiv:2503.01947](https://arxiv.org/pdf/2503.01947))は、日本語 LLM のステレオタイプ挙動を扱う一次資料。
- **伝播**: 我々は渋谷(日本・来街者含む)を模す。**WEIRD 整列 × 日本語の二重補正**が要る。qwen3 の訓練分布が日本のどの層に整列しているかは未検証で、来街者(外国人観光客)ペルソナの忠実度は特に疑わしい。

### 2.6 確率表現の歪み・過信(較正の失敗)
- **LLM は全サイズで過信**、較正誤差が高い。verbalized confidence は overconfident で、**Dunning-Kruger 的**(最も確信するとき最も不正確、答えを知っているときほど hedging)。**RLHF の mode collapse が token 分布を鋭くし、モデルを実際より確信して見せ、verbalized confidence の較正を悪化**させる。出典: [Overconfidence is Key, arXiv:2405.02917](https://arxiv.org/html/2405.02917) / [LLMs Are Overconfident, arXiv:2606.03437](https://arxiv.org/pdf/2606.03437) / [On Verbalized Confidence, arXiv:2412.14737](https://arxiv.org/html/2412.14737v2)。
- **伝播**: エージェントが「確信度」「リスク態度」を発話・内省に織り込む場面(投資・出店・移住判断)で、**過信が意思決定分布を歪める**。人間なら躊躇する場面で LLM は過信的に断行 or 逆に一律 hedging し、**リスク態度の個体差が痩せる**(§2.4 と合流)。

### 2.7 時間感覚の欠如(Temporally Blind)
- **「Your LLM Agents are Temporally Blind」(arXiv:2510.23853)**: エージェント設定で、時間が連続的に進む中でのツール使用判断が人間の時間知覚とずれる。**「Do Language Models Know Time Passes?」(arXiv:2506.05790)**、**「Can LLMs Perceive Time?」(arXiv:2604.00010)** も、LLM は課題所要時間の知識は持つが**自己推定に転移せず、時間の経過を内在的に感じない**と示す。出典: [arXiv:2510.23853](https://arxiv.org/pdf/2510.23853) / [arXiv:2506.05790](https://arxiv.org/html/2506.05790v1)。
- **伝播**: LLM は「3日前」「先週」「そろそろ潮時」といった**時間の重み付けを自前では持たない**。我々は Clock(1step=10分)・スケジュール帳・記憶の時系列で**外挿的に時間を与えている**のは正しい設計(temporally blind を機構で補償)。ただし**内省での「時間経過に伴う気持ちの変化」は作話になりやすい**(実際には経過を感じていないため)。観測(b)の作話とも通じる。

> **本シムへの含意(§2 総括)**: 観測(c)(反復)・(d)(改変0・不満鎮静)は、独立の不具合ではなく**「アライメントが分布を狭め、調和へ引き、裾を消す」という単一の引力の別々の顔**。state 機構の修正(相対的剥奪・affect ハブ)は必要だが十分でない — **生成段そのものの引力**(positivity・homogenization・sycophancy)を、モデル選択・サンプリング・プロンプト文脈で別途相殺する必要がある。**「トークンを増やす」は効かない(§token-budgets の AGA と一致)。効くのは「分布を広げる」施策**。

---

## 3. 作話・幻覚の性質と制御 — どこまでが「人間らしさ」でどこからが「毒」か

観測(b)「TIOTIOの店員が韓語で新メニューを伝えてた(店名=実在POI・出来事=非実在)」は、**confabulation(作話)の教科書例**。ここは本シムに固有の重要論点なので厚く扱う。

### 3.1 Hallucination と Confabulation の区別
- **用語**: 近年は**「LLM は hallucinate ではなく confabulate する」**という整理が定着([Beren 2023](https://www.beren.io/2023-03-19-LLMs-confabulate-not-hallucinate/))。confabulation は**run ごとに変わる恣意的な誤生成**。hallucination はより広く、**factuality(世界と矛盾)と faithfulness(自らの入力/源と矛盾)**の2形態に分けるべき、というのが最新の整理。出典: [Detecting hallucinations using semantic entropy, Nature 2024 s41586-024-07421-0](https://www.nature.com/articles/s41586-024-07421-0)。
- **観測(b)の分類**: 「TIOTIO(実在POI)」への接地は faithful だが、「韓語で新メニュー」は**世界内に存在しない出来事の生成 = confabulation**。**半分接地・半分作話**という本シムの記述は文献的に正確。これは factuality の破れ(シム世界という"世界"と矛盾)。

### 3.2 検出: Semantic Entropy
- **Semantic Entropy(Farquhar et al., Nature 2024)**: 同じ問いへの複数生成を**意味クラスタ**に集約し、意味レベルのエントロピーで confabulation を検出。トークン列でなく**意味空間**で不確実性を測るのが要点。高 semantic entropy = 作話しやすい問い。出典: [Nature s41586-024-07421-0](https://www.nature.com/articles/s41586-024-07421-0) / [OATML blog](https://oatml.cs.ox.ac.uk/blog/2024/06/19/detecting_hallucinations_2024.html)。
- **応用可能性**: 我々の発話で「世界に無い出来事」を検出したいなら、**同一状況で複数サンプルを引き、意味の一貫性(実在POI/実在イベントへの接地一致度)を測る**のが原理的な道。ただしコスト増(複数サンプル)。

### 3.3 制御: Grounding(接地)
- 幻覚低減の標準手段は **grounding(外部の出典事実を与える)・abstention(棄権)・verification・agent memory**。retrieved facts を与えると、模型は捏造でなく引用可能な答えを返す。出典: [Reducing LLM Hallucinations, Zep](https://www.getzep.com/ai-agents/reducing-llm-hallucinations/)。
- **本シムでの接地資産**: 我々は既に**実在POI・語彙来歴・ニュース・SNS索引の"シミュ内DB"**(devlog Block#3 の検索=シミュ内DB)を持つ。これは grounding 基盤として強い。**発話プロンプトに「今この場所に実在する店・出来事のみ言及可」の接地行を足す**、または**発話後に接地チェック**(言及した固有名詞がシム世界に存在するか照合)で作話を抑制できる余地(§7-⑧)。

### 3.4 「作話 = 人間らしさ」の線引き ★依頼の核心
- **作話は健常な人間の記憶・語りにも普遍**: 記憶の再構成は健常者でも作話を要し(欠損の穴埋め・社会的地位の底上げ・立場の防衛)、**動機づけられた作話**(恋愛関係・パフォーマンス圧下)も実証されている。**「LLM の confabulation は人間の物語生成の誇張版」**で、confabulated テキストは**より narrative-rich で人間の語りのパターンに合致**する。出典: [Confabulation: The Surprising Value of LLM Hallucinations(Sui et al.)](https://www.researchgate.net/publication/384209365) / [On LLM hallucination vs confabulation(Southampton)](https://generic.wordpress.soton.ac.uk/skywritings/2025/08/24/on-llm-hallucination-vs-confabulation/)。
- **社会的に良い作話**: 「Critical Confabulation(arXiv:2511.07722)」は、欠けた歴史的声を埋めるための"社会的善のための幻覚"を論じる。「Honest Lying(arXiv:2605.29463)」は**reflexive エージェントの記憶作話**を扱い、内省するエージェントが自らの過去を"誠実に嘘をつく"様を分析。出典: [arXiv:2511.07722](https://arxiv.org/pdf/2511.07722) / [arXiv:2605.29463](https://arxiv.org/pdf/2605.29463)。
- **線引きの提案(本シム向け)**:
  - **人間らしい作話(保持すべき)**: ①**誇張・脚色・記憶違い**(「昨日すごい人だった」)②**主観的解釈**(「あの店員、韓国の人かな」)③**社会的潤滑**(相手に合わせた曖昧化)。これらは realism を上げる。
  - **シミュレーションの毒(抑制すべき)**: ①**世界内に存在しない固有の出来事/施設を"事実"として断言**(観測(b)の「新メニューを伝えてた」)②**他エージェントの発言/行動の捏造**(存在しない会話を引用)③**制度・ニュース・語彙の非実在イベントを既成事実化**(伝播系譜を汚染)。**これらは L1 の伝播ログ・k* の因果チェーンを汚染するため毒**。
  - **判定軸 = "接地の要求される粒度"**: 主観・感情・解釈は接地不要(作話OK)。**固有名詞・出来事・引用・制度は接地必須**(作話NG)。→ 実装するなら「発話の主観部は自由/客観的主張部は接地チェック」の非対称制御。

> **本シムへの含意**: 観測(b)を「バグ」と一括りにせず、**接地率メトリクス**で測るのが正道。発話中の固有名詞・出来事言及を抽出し「シム世界に存在するか」を照合、**接地率(grounded / total mentions)を L2 指標化**すれば、作話を"程度問題"として観測でき、モデル/プロンプト間で A/B できる。人間の会話も接地率100%ではない(誇張・記憶違いがある)ので、**目標は100%でなく"人間の会話の接地率バンド"**(これは要文献 or 実測、現状**未確認**)。**semantic entropy による発話サンプリング検出はコスト高だが、伝播に載る発話(語彙・ニュース)だけに絞れば実用的**。

---

## 4. 人間らしさを上げる技法 — ペルソナ・記憶・drift・モデル選択

### 4.1 ペルソナ設計: 接地の深さ vs 均質化リスク
- **Park 型(インタビュー接地)**が忠実度最強(§1.2、86%)。だが**リッチすぎるペルソナは manifold collapse で逆効果**(§2.4、Age-Gender > ICP)。**この2つは矛盾しない**: Park の接地は「実在個人の一貫した逐語」であり、我々が陥りやすいのは「架空属性を盛った"それっぽい"プロフィール」。後者は**モデルにステレオタイプを喚起させて分離を潰す**。
- **教訓**: ①接地するなら**実データ由来の逐語的具体**(Park)、②合成なら**薄く・直交する属性 + Verbalized Sampling で分散を"引き出す"**(盛らない)。中途半端にリッチな合成プロフィールが最悪。出典: [The Prompt Makes the Person(a), arXiv:2507.16076](https://arxiv.org/html/2507.16076) / [Chameleon's Limit, arXiv:2604.24698](https://arxiv.org/html/2604.24698)。

### 4.2 記憶接地と persona drift 対策
- **Persona drift**: LLM は孤立文脈では安定人格でも、**長対話で人格を保てない**。frontier モデルでも**信頼できる会話ターンは約18**([When Attention Closes, arXiv:2605.12922](https://arxiv.org/pdf/2605.12922))。drift は persona 事実との含意関係の喪失/明示的矛盾として operationalize される([Identity Drift, arXiv:2412.00804](https://arxiv.org/html/2412.00804v2))。
- **緩和**: **ID-RAG(identity 検索拡張)**が有効。drift を単調減衰でなく**有界確率過程**としてモデル化し KL で平衡divergence を予測する研究も([Drift No More?, arXiv:2510.07777](https://arxiv.org/html/2510.07777v1))。
- **本シムの立ち位置**: 我々は**就寝内省で beliefs を再固定 + 関係台帳 + 自己モデル(self_model)注入**(devlog Block#5 E6)。これは**ID-RAG の自前実装に相当**し、drift 対策として文献的に妥当。100日で劣化なし(`memory-100day-audit.md`)は、この設計が効いている実証。**ただし「18ターン」問題は1回の deliberate 内では起きない(我々は毎回フレッシュにプロンプト再構築=長対話でない)** — 我々の drift リスクは"対話ターン"でなく"日をまたぐ人格の一貫性"で、そこは記憶接地でカバー済み。

### 4.3 base vs instruct、小型 vs 大型の人間度
- **base vs instruct**: RLHF-ed chat は bias 誘発改変に鈍感(=人間なら引っかかるバイアスに引っかからない)で、**非バイアス摂動では base より効果量が平均81%大きい = 人間らしさが低下**([Do LLMs exhibit human-like response biases?, arXiv:2311.04076](https://arxiv.org/pdf/2311.04076))。SimBench でも**10B未満では base が instruct を上回る**(OLMo-2 base > instruct at 7B/13B)。協調バイアスは**アライメント由来でなく事前学習の人間テキスト由来**([SimBench])。
- **小型 vs 大型**: SimBench は log-linear scaling(大型有利)だが、**多様な社会人口ペルソナのシミュレーションでは小型 OLMo-2-7B が Llama-3.3-70B を上回る**ことも。Gemma-3-4B/Llama-3.1-8B は大型に明確に劣るが、Gemma-3-27B から伸びは頭打ち。出典: [arXiv:2507.16076](https://arxiv.org/html/2507.16076) / [SimBench](https://arxiv.org/html/2510.17516v2)。
- **本シムの qwen3:4b/8b**: 現地は 4B/8B。SimBench の教えは「**4B は人間分布忠実度では不利、だが行動系(JSON遵守・バンド内行動)は既に成立**」。**忠実度を上げたいなら 27B 級**(`llm-model-selection.md` の Qwen3.5/3.6-27B)だが、**"多様性"の観点では単に大型化しても均質化は残る**(§2.4 の「temperature/persona でも残る」)。→ **サイズより「base/instruct 対照 + VS」が多様性の主レバー**。

### 4.4 サンプリングと多様性
- **Verbalized Sampling(arXiv:2510.01171, 既出)の新知見**: mode collapse の**データレベルの真因は選好データの typicality bias**(注釈者が馴染みあるテキストを系統的に好む=認知心理の典型性選好)。アルゴリズムでなくデータが原因なので**訓練不要のプロンプト法(VS)で回避可能** — 「N個の応答とその確率を出せ」で分布を引き出し、多様性1.6-2.1倍。出典: [arXiv:2510.01171](https://arxiv.org/abs/2510.01171)。
- **temperature の限界**: 均質化研究は「**temperature を上げても均質化は残る**」と示す(§2.4)。→ 温度は必要だが不十分。**VS のような"分布を明示的に出させる"手法が本質**。我々は VS 採用済み(`agents__persona-language-safety-opinion.md`)で方向は正しい。**反復対策の variety_hint(観測c)も同系統だが、VS ほど原理的でない** — variety_hint は「繰り返すな」の否定命令、VS は「分布を出せ」の構成的指示。後者の方が強い。

### 4.5 心の理論(ToM)の現状
- **ToMBench(arXiv:2402.15052)**: GPT-4 系が最良だが**人間に10%以上劣る**、8タスク31能力。高次 ToM では adult レベルに達するという報告もあり([Frontiers 2025](https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2025.1633272/full))、**評価法依存で結論がぶれる**。出典: [arXiv:2402.15052](https://arxiv.org/abs/2402.15052)。
- **本シムへの含意**: エージェントが**他者の内面を推し量る場面**(誰を誘うか、相手の反応予測、関係の質判断)で ToM の限界が効く。我々は関係台帳・スケジュール帳で**他者モデルを外部化**しているが、「相手が何を感じているか」の推論は LLM の ToM に依存。過信(§2.6)と合わさると**他者の心の誤読が発話に出る**。ただし人間も ToM は完璧でないので、これは realism の範囲内でもある(作話同様、線引きが要る)。

> **本シムへの含意(§4 総括)**: 人間らしさの主レバーは、優先順に **①モデル選択(base/instruct 対照)②サンプリング(VS)③ペルソナは薄く多様に④記憶接地(drift 対策=実装済)**。**サイズ(4B→27B)は忠実度の底上げにはなるが、多様性・裾は買えない**。観測(c)の反復は、variety_hint より**VS の徹底 + 温度 + base 対照**で攻めるのが文献的筋。

---

## 5. モデル系統の「性格」差 — モデル選択は第一級の実験変数

### 5.1 系統差の実証(政治・外交・気質)
- **政治傾向**: 複数 LLM(Qwen/DeepSeek/Gemini/GPT)は政治・イデオロギー・地政学同盟で**固有バイアス**を持つ。**Gemini は右寄り(有意)、GPT は最も左寄り、DeepSeek は最も中立的**だが**外交では hawkish(エスカレーション的)** — 特に西側国相手のシナリオで。Llama/GPT は討論で態度の volatility が大きい。出典: [Political Bias via Multi-Agent Debate, arXiv:2506.11825](https://arxiv.org/html/2506.11825v1) / [Hidden Persuaders, arXiv:2410.24190](https://arxiv.org/pdf/2410.24190) / [Hawkish AI? DeepSeek(CSIS)](https://www.csis.org/analysis/hawkish-ai-uncovering-deepseeks-foreign-policy-biases) / [PoliticsBench, arXiv:2603.23841](https://arxiv.org/abs/2603.23841v1)。
- **含意**: 「Qwen を選ぶ」は中立的な実装判断でなく、**特定の政治・気質分布を選ぶこと**。渋谷シムの社会力学(意見分布・協調/対立傾向)は**モデルの気質を継承**する。`llm-model-selection.md` の「モデル選択=実験変数」は、ここで**気質差の一次証拠として補強**される。

### 5.2 マルチモデル社会(モデル混在で多様性を作れるか)
- **動機**: 単一モデルは均質化(§2.4)。**異なるアーキ・学習バイアスのモデルを混ぜれば多様性が戻る**か? 「Simulate Anything」「X-mas」など異種モデルプール構築の動きがある。出典: [Integrating LLM in ABM(JASSS投稿), arXiv:2507.19364](https://arxiv.org/html/2507.19364v1)。
- **しかし collapse は頑健**: ★**「Diversity Collapse in Multi-Agent LLM Systems(arXiv:2604.18005)」**は、**構造的結合により開放的アイデア生成で多様性が崩壊**すると示す。★**「Multi-LLM Systems Exhibit Robust Semantic Collapse(arXiv:2605.17193)」**は、**異種モデルを混ぜても意味的収束(semantic collapse)が頑健に起きる**と示す — モデルを混ぜるだけでは多様性は救えない。共有訓練バイアスで早期収束・誤情報増幅する。出典: [arXiv:2604.18005](https://arxiv.org/pdf/2604.18005) / [arXiv:2605.17193](https://arxiv.org/pdf/2605.17193)。
- **含意**: **「モデル混在=多様性の銀の弾丸」ではない**。`llm-model-selection.md` 構成案C(model×k)や階層構成(B)でモデルを混ぜるなら、**多様性の獲得を期待するより、気質の対照(instruct/abliterated)としての意味**に絞るのが正直。多様性は**ペルソナ×VS×温度**で作る方が確実。ただし**「少数の異種モデルを混ぜて semantic collapse がどの程度緩むか」自体が観測に値する問い**(本シムの新規性になりうる — 未検証)。

> **本シムへの含意(§5)**: モデル選択は気質選択。**単一モデル均質化 → マルチモデルでも semantic collapse は残る → 多様性はペルソナ・サンプリング側で作る**、が2026の到達点。model×k 対照は「多様性を買う」目的でなく「**アライメントの引力(迎合・調和)を測る**」目的で回すのが正しい設計。

---

## 6. AIそのものの解像度 — 機構理解がシム設計にどう効くか

「なぜLLMがそう振る舞うか」の機構理解は、上記のバイアスを**設計で相殺する足場**になる。

### 6.1 解釈可能性: features / circuits(Anthropic 2025)
- **「On the Biology of a Large Language Model」(transformer-circuits 2025)**: **Circuit Tracing** — Cross-Layer Transcoders で密な MLP 活性を**疎で解釈可能な feature("置換ニューロン")**に置換し、**attribution graph**(入力トークン→中間推論回路→出力の計算マップ)を構築。Claude 3.5 Haiku で**多段推論・詩生成(先の韻を"計画"している)・多言語処理・算術・医療診断・幻覚処理・安全拒否・jailbreak・CoT の忠実性**を解剖。feature を注入/抑制して下流を制御できる。出典: [On the Biology of a LLM(transformer-circuits.pub 2025)](https://transformer-circuits.pub/2025/attribution-graphs/biology.html) / [MIT Tech Review](https://www.technologyreview.com/2025/03/27/1113916/)。
- **シム設計への効き**: ①**「モデルが実は先を計画している」**= 詩の韻の例は、我々の内省(reflect)が"事後の作話"か"事前の計画の外化"かを問い直させる。②**feature 注入で概念を操作できる** = 将来「grievance feature」を直接操作して mode collapse を破る実験の理論的可能性(ただし本シムでは重すぎ、現実的でない)。③**CoT の忠実性**研究は、我々の内省 `<think>` が**本当の思考か作話か**という問いに直結(§6.2)。

### 6.2 内省(introspection): 自己報告は本物か作話か ★内省設計の核心
- **「Emergent Introspective Awareness in LLMs」(Anthropic 2025)**: **概念注入法** — 既知概念の活性ベクトルをモデル内部に注入し、自己報告への影響を測る。**Claude Opus 4.1 は最適な層・強度で、注入概念を約20%の試行で正しく検出**。ピークは**モデル深さの約2/3の層**。**最も高性能なモデル(Opus 4/4.1)が最も内省的**。ただし**「失敗が常態、成功は例外」で高度に不安定・文脈依存**。★**「検出・同定の先の応答詳細は embellished(粉飾)or confabulated(作話)されうる」** = 内省の一部は本物だが、**大半は事後の作話**。genuine introspection は会話だけでは confabulation と区別できない。出典: [Emergent Introspective Awareness(transformer-circuits.pub 2025)](https://transformer-circuits.pub/2025/introspection/index.html) / [Anthropic research](https://www.anthropic.com/research/introspection)。
- ★**本シムの内省(reflection.py)への直撃**: 我々は内省を**k(経験→内部状態の結合)の実装部位**としている。この研究は「**LLM の自己報告(=内省の出力)は、内部状態の忠実な読み出しではなく、大半が事後の作話**」と示す。つまり:
  - **内省で生成される belief/summary は、"本当の内部状態の変化"ではなく、"それらしい物語"である可能性が高い**。20%程度しか内部状態に接地していない。
  - これは k の解釈に慎重さを要求する: **「内省が経験を内部状態に書き戻す」チャネルは、機構的には"作話による自己一貫性の維持"に近い**。ただし**人間の内省も同様に事後合理化が大半**(認知心理の常識)なので、**これは"人間らしさ"の範囲内**とも言える。
  - 実務的帰結: 内省の belief を**行動で検証**(自己申告でなく行動指標)する我々の方針(`measurement__validation-overview.md`)は、この不安定性への正しいヘッジ。**内省の"内容"を真に受けず、"それが後続行動を変えたか"で k を測る**のが機構的に正当。

### 6.3 In-context learning の機構
- **ICL = induction heads(match-and-copy)+ function/task vectors**。induction head は `[…A B … A]→B` の照合コピー回路。few-shot ICL は主に **function vector(FV)heads**(タスクの潜在符号を計算)が駆動、特に大型で。★**多くの FV head は訓練中に induction head から始まり FV へ遷移** = induction head が richer なタスク符号化回路の足場。出典: [Which Attention Heads Matter for ICL?(OpenReview)](https://openreview.net/forum?id=C7XmEByCFv) / [Task Vectors in ICL, arXiv:2501.09240](https://arxiv.org/pdf/2501.09240)。
- **シム設計への効き**: 我々のプロンプト(ペルソナ+記憶+状況)は巨大な in-context 条件付け。**ICL が"タスクベクトル"として作用する**なら、**プロンプトの冒頭(共通prefix=ヘッダ・ペルソナ)がタスク符号を強く決める** — `llm-model-selection.md` の APC(共通prefix先頭配置)は throughput だけでなく**タスク符号の安定化**の意味も持つ。逆に**個別文脈を後ろに置く現設計は、FV による"人格タスク"の符号化を安定させる**方向で、persona 一貫性に寄与している可能性(推測、未検証)。

### 6.4 RLHF/RLAIF が行動分布に与える機構
- **統合像**: (1) **typicality bias**(選好データの馴染み選好)→ mode collapse(§4.4)。(2) **「同意は善」ヒューリスティック**→ sycophancy(§2.1)。(3) 出力エントロピー減 → 均質化(§2.4)・過信(§2.6)・**高エントロピー多元的シミュの劣化(SimBench tradeoff, §1.3)**。(4) helpful/polite 強調 → positivity/utopian illusion(§2.2)。**これら全てが"アライメントが分布を狭め調和へ引く"という単一機構の異なる射影**。出典: [How RLHF Amplifies Sycophancy, arXiv:2602.01002](https://arxiv.org/pdf/2602.01002) / [Verbalized Sampling, arXiv:2510.01171](https://arxiv.org/abs/2510.01171) / [SimBench, arXiv:2510.17516](https://arxiv.org/html/2510.17516v2)。
- **RLAIF/Constitutional の位置**: RLHF の亜種(RLAIF=AI 評価者、RLVR=検証可能報酬)も、報酬が"典型・合意・無害"を好む限り同じ引力を持つと予想される(**RLAIF 固有の分布効果の一次実証は本調査では未確認**)。

> **本シムへの含意(§6)**: 機構理解の最大の実務的帰結は**「内省の自己報告を真に受けない」**(§6.2)。内省内容は大半が作話で、20%程度しか内部状態に接地しない。**k は"内省が言うこと"でなく"内省後に行動が変わること"で測るべき**(既方針を機構的に正当化)。また、RLHF の分布狭窄が**単一機構の多面的発現**と分かった以上、**相殺策も単一方向(=分布を広げる: base対照・VS・温度・対立文脈)に集約できる**。

---

## 7. 現実近接化の打ち手候補の総括表(実装はしない・候補まで)

> 凡例: 優先度は本シムの目的(**世界改変者=裾の創発、k*、現実整合**)への効きに対する Opus の私見。**実装可否・実施はユーザー判断**(memory: ask-before-extending)。「実装済/着手」は既存資産との関係を注記。

| # | 打ち手 | 根拠(出典) | 期待効果 | リスク | 実装コスト | 優先度(私見) |
|---|---|---|---|---|---|---|
| ① | **model×k 対照(instruct⇔base/abliterated)を回す** | SimBench alignment-simulation tradeoff(r=−0.942, §1.3)/ sycophancy 機構(§2.1)/ base の方が人間らしい(§4.3) | 迎合・調和の引力を定量分離。観測(d)「改変0」がモデル依存か機構(飽和)かを切り分け | base の能力低下が k* の交絡(要 TruthfulQA/GSM8K で裏取り)/ キャッシュ非共有=実LLM再走 | 中(ラン分離・`llm-model-selection.md`構成C 既設計) | **★★★** |
| ② | **Verbalized Sampling の徹底 + 温度調律で裾を戻す** | mode collapse=typicality bias(§4.4)/ 均質化は温度だけでは残る(§2.4)/ VS 多様性1.6-2.1倍 | 観測(c)反復の原理的抑制。個体差(裾)の回復→R²の歪み補正 | VS は出力形式が複雑化(JSON遵守と両立要確認)/ 過剰多様化で一貫性低下 | 低〜中(VS 採用済・拡張) | **★★★** |
| ③ | **ペルソナにインタビュー接地的な"逐語的具体"を(合成でも)入れる** | Park 2024 で接地が忠実度を86%まで買う(§1.2) | 個人の一貫性・群間格差縮小。忠実度の底上げ | 架空世界(渋谷来歴)との整合が要る/ 盛りすぎると manifold collapse(§2.4)で逆効果 | 中〜高(ペルソナ生成刷新) | **★★☆** |
| ④ | **ペルソナは"薄く多様に"(リッチICP を避ける)** | manifold collapse: Age-Gender>ICP(§2.4, §4.1) | 属性を盛らないことで逆説的に分散を保つ | 現IPF+VS が既にリッチなら要棚卸し(過剰属性の削減) | 低(プロンプト構成の調整) | **★★☆** |
| ⑤ | **作話の接地率メトリクスを L2 に追加(観測のみ)** | confabulation の性質(§3)/ semantic entropy(§3.2)/ grounding(§3.3) | 観測(b)作話を"程度問題"で可視化。モデル/プロンプト間A/B。伝播汚染の早期検知 | 固有名詞抽出・シム内DB照合の実装/ 人間の接地率バンドが**未確認**(目標値が曖昧) | 中(発話後処理・非因果ループ) | **★★☆** |
| ⑥ | **不満・対立を"鎮静させない"文脈設計(utopian illusion 対策)** | Utopian Illusion(§2.2)/ positivity skew / 観測(d)「街が不満を吹き飛ばす」 | 対立・grievance が発話段で消えるのを防ぐ→改変動機の上流を開通 | 過剰な対立注入は別の非現実(過剰分極, OASIS §2.3)を生む/ 調律が難しい | 中(プロンプト+state機構、相対的剥奪と連動) | **★★☆** |
| ⑦ | **内省の自己報告を真に受けず、行動で k を測る(方針の明文化・徹底)** | introspection の20%接地・大半作話(§6.2)/ CoT 忠実性(§6.1) | k 推定の妥当性向上。内省内容の作話に騙されない | (既方針)追加コストほぼ無し | 低(既存の行動指標主義の再確認) | **★★★** |
| ⑧ | **発話の"客観的主張部"のみ接地チェック(主観・感情は自由)** | 作話の線引き(§3.4)/ grounding(§3.3) | 毒(非実在の出来事断言)を抑えつつ人間らしい誇張・解釈は残す | 主観/客観の切り分けが難しい(誤判定)/ 実装複雑 | 高(発話パーサ+照合) | **★☆☆** |
| ⑨ | **忠実度の底上げに 27B 級(多様性は別施策で)** | SimBench log-linear(§4.3)/ ただし多様性は買えない(§2.4) | 分布シミュ忠実度の底上げ | VRAM・スループット(`llm-model-selection.md`)/ 均質化は残る=①②と併用必須 | 中(本選GPU前提・既検討) | **★★☆** |
| ⑩ | **少数の異種モデル混在で semantic collapse の緩和度を"観測"する** | multi-model でも collapse は頑健(§5.2)= むしろ問い | 多様性の銀の弾丸を期待せず、収束の頑健性自体を新規知見に | collapse が残れば徒労/ キャッシュ・再現性が複雑化 | 高(艦隊構成・再現規律) | **★☆☆** |

---

## 8. 総括 — 「解像度が上がった」ことの要点

1. **LLM は"人間の平均"の良い近似器だが、"人間の分散・裾・対立・時間・確率"の悪い近似器**。本シムが狙う現象(裾=改変者、多元性、k*)は**すべて LLM が最も苦手な領域**にある。これは弱点でなく**研究の核心**: 「アライメントの引力に抗して裾の創発を観測できるか」が novelty。
2. **観測(a)-(d)は独立の不具合でなく、単一機構(アライメントが分布を狭め調和へ引く)の別々の顔**。ゆえに**相殺策も単一方向に集約**: 分布を広げる(base対照・VS・温度・対立文脈)。「トークンを増やす」は効かない(token-budgets の AGA と一致)。
3. **内省の自己報告は大半が作話(20%程度しか内部状態に接地)** — k を"内省の内容"でなく"内省後の行動変化"で測る既方針が、機構的に正当化された。
4. **作話は人間らしさの一部**。主観・感情・誇張の作話は保持、固有名詞・出来事・引用・制度の作話は毒。**接地率で程度を測る**のが正道で、目標は100%でなく"人間バンド"(要実測)。
5. **モデル選択は気質選択**。マルチモデル混在は多様性の銀の弾丸ではない(semantic collapse は頑健)。多様性はペルソナ×サンプリングで作る。

---

## 9. 出典一覧(本調査で参照。🔶=二次/要一次確認・未確認は本文に明記)

**LLMを人間の代役に(実証全景)**
- [Turing Experiment(Aher et al., ICML 2023)— PMLR v202](https://proceedings.mlr.press/v202/aher23a.html) / [arXiv:2208.10264](https://arxiv.org/abs/2208.10264)
- [Homo Silicus(Horton et al.)— NBER w31122](https://www.nber.org/papers/w31122) / [arXiv:2301.07543](https://arxiv.org/abs/2301.07543)
- [Generative Agent Simulations of 1,000 People(Park et al. 2024)— arXiv:2411.10109](https://arxiv.org/abs/2411.10109) / [genagents(GitHub)](https://github.com/joonspk-research/genagents)
- [Centaur(Binz et al.)— Nature s41586-025-09215-4](https://www.nature.com/articles/s41586-025-09215-4) / [arXiv:2410.20268](https://arxiv.org/abs/2410.20268) / [批判 arXiv:2510.03311](https://arxiv.org/pdf/2510.03311)
- [SimBench(人間行動シミュ能力ベンチ)— arXiv:2510.17516](https://arxiv.org/html/2510.17516v2)
- [ChatGPT vs Social Surveys(silicon sampling 検証)— arXiv:2409.02601](https://arxiv.org/html/2409.02601v3) / [GPT-ology — arXiv:2406.09464](https://arxiv.org/pdf/2406.09464)

**系統的バイアス**
- [Social Simulations Risk Utopian Illusion — arXiv:2510.21180](https://arxiv.org/pdf/2510.21180)
- [The Homogenizing Effect of LLMs — arXiv:2508.01491](https://arxiv.org/html/2508.01491v2)
- [The Chameleon's Limit(persona collapse)— arXiv:2604.24698](https://arxiv.org/html/2604.24698) / [Prompt Makes the Person(a) — arXiv:2507.16076](https://arxiv.org/html/2507.16076)
- [OASIS(100万エージェント・herd/分極)— arXiv:2411.11581](https://arxiv.org/abs/2411.11581) / [OASIS site](https://oasis.camel-ai.org/)
- [How RLHF Amplifies Sycophancy — arXiv:2602.01002](https://arxiv.org/pdf/2602.01002) / [It's Not Always Sycophancy — arXiv:2605.27288](https://arxiv.org/pdf/2605.27288)
- [Expressing Social Emotions(感情ノルムのズレ)— arXiv:2604.16757](https://arxiv.org/html/2604.16757)
- [LLMs Are Overconfident — arXiv:2606.03437](https://arxiv.org/pdf/2606.03437) / [Overconfidence is Key — arXiv:2405.02917](https://arxiv.org/html/2405.02917) / [On Verbalized Confidence — arXiv:2412.14737](https://arxiv.org/html/2412.14737v2)
- [Your LLM Agents are Temporally Blind — arXiv:2510.23853](https://arxiv.org/pdf/2510.23853) / [Do Language Models Know Time Passes? — arXiv:2506.05790](https://arxiv.org/html/2506.05790v1) / [Can LLMs Perceive Time? — arXiv:2604.00010](https://arxiv.org/html/2604.00010v1)
- [日本語LLMのステレオタイプ安全性 — arXiv:2503.01947](https://arxiv.org/pdf/2503.01947)

**作話・幻覚**
- [Detecting hallucinations using semantic entropy(Farquhar)— Nature s41586-024-07421-0](https://www.nature.com/articles/s41586-024-07421-0) / [OATML blog](https://oatml.cs.ox.ac.uk/blog/2024/06/19/detecting_hallucinations_2024.html)
- [LLMs confabulate not hallucinate(Beren)](https://www.beren.io/2023-03-19-LLMs-confabulate-not-hallucinate/) / [On hallucination vs confabulation(Southampton)](https://generic.wordpress.soton.ac.uk/skywritings/2025/08/24/on-llm-hallucination-vs-confabulation/)
- [Confabulation: The Surprising Value of LLM Hallucinations 🔶](https://www.researchgate.net/publication/384209365) / [Critical Confabulation — arXiv:2511.07722](https://arxiv.org/pdf/2511.07722) / [Honest Lying(reflexive agents)— arXiv:2605.29463](https://arxiv.org/pdf/2605.29463)
- [Reducing LLM Hallucinations(grounding 実務)🔶 Zep](https://www.getzep.com/ai-agents/reducing-llm-hallucinations/)

**人間らしさ技法・drift・ToM**
- [Verbalized Sampling — arXiv:2510.01171](https://arxiv.org/abs/2510.01171)
- [Do LLMs exhibit human-like response biases?(base vs instruct)— arXiv:2311.04076](https://arxiv.org/pdf/2311.04076)
- [Examining Identity Drift — arXiv:2412.00804](https://arxiv.org/html/2412.00804v2) / [When Attention Closes(~18ターン)— arXiv:2605.12922](https://arxiv.org/pdf/2605.12922) / [Drift No More? — arXiv:2510.07777](https://arxiv.org/html/2510.07777v1)
- [ToMBench — arXiv:2402.15052](https://arxiv.org/abs/2402.15052) / [高次ToM adult級(Frontiers 2025)](https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2025.1633272/full)

**モデル系統差・マルチモデル**
- [Political Bias via Multi-Agent Debate — arXiv:2506.11825](https://arxiv.org/html/2506.11825v1) / [PoliticsBench — arXiv:2603.23841](https://arxiv.org/abs/2603.23841v1) / [Hidden Persuaders — arXiv:2410.24190](https://arxiv.org/pdf/2410.24190) / [Hawkish AI? DeepSeek(CSIS)](https://www.csis.org/analysis/hawkish-ai-uncovering-deepseeks-foreign-policy-biases)
- [Diversity Collapse in Multi-Agent LLM — arXiv:2604.18005](https://arxiv.org/pdf/2604.18005) / [Robust Semantic Collapse — arXiv:2605.17193](https://arxiv.org/pdf/2605.17193) / [Integrating LLM in ABM(JASSS)— arXiv:2507.19364](https://arxiv.org/html/2507.19364v1)

**機構理解(解釈可能性・内省・ICL)**
- [On the Biology of a Large Language Model(transformer-circuits 2025)](https://transformer-circuits.pub/2025/attribution-graphs/biology.html) / [MIT Tech Review 解説](https://www.technologyreview.com/2025/03/27/1113916/)
- [Emergent Introspective Awareness(transformer-circuits 2025)](https://transformer-circuits.pub/2025/introspection/index.html) / [Anthropic: Introspection](https://www.anthropic.com/research/introspection)
- [Which Attention Heads Matter for ICL?(OpenReview)](https://openreview.net/forum?id=C7XmEByCFv) / [Task Vectors in ICL — arXiv:2501.09240](https://arxiv.org/pdf/2501.09240)

**本リポジトリ内の関連(既存・上積み元)**
- `docs/lit/llm__agents-validity-model-choice.md`(RLHF 同調=妥当性ゲート)
- `docs/lit/agents__persona-language-safety-opinion.md`(IPF+VS・言語交絡・意見力学・prompt injection)
- `docs/research/world-change-motivation.md`(観測d: ツール0使用・飽和の実証)
- `docs/research/llm-model-selection.md`(モデル選定・GPU・量子化)/ `docs/research/token-budgets.md`(トークン量↔品質は飽和=AGA)
