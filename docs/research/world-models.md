# 世界モデル(World Models)— 系譜・LLM での実在性・認知科学・エージェント行動要因の導出(調査、2026-07-11)

> 依頼(ユーザー): 「世界モデルについて深くリサーチしてほしい。世界モデルについて調べたら、
> 今回のシミュレーションでエージェントの行動に影響する要因の候補をいくつか挙げられると思う」。
> **担当: Opus。本バッチは調査のみ・コード変更なし**(本ファイル1つだけ作成)。
> 目的: (1) 世界モデルを機械学習・LLM・認知科学の3系譜で定義し直し、(2) そこから
> 「人間の行動を決める世界モデル的要因」を体系的に導出し、(3) 本シムの既実装と照合して
> **実装済みの対応物**と**欠けている候補**に仕分けし、各候補に **決定論・R1(LLM呼数不変)・
> no-fingerprint** の制約内で可能な実装スケッチと優先度を付す(実装はしない=設計まで)。

---

## §0. 要約(TL;DR)

- **世界モデルの本質は「次に何が起こるかの内的予測」**。ML では潜在空間での状態遷移予測
  (Ha & Schmidhuber → Dreamer → MuZero → JEPA → Genie/Cosmos)、認知科学では予測処理・
  メンタルモデル・認知地図・prospection(未来の心的シミュレーション)として現れる。共通核は
  **予測 → 予測誤差(=驚き)→ 行動/更新**のループ。本シムの `drive.py`(驚き駆動発火)・
  `implicit_self`(行動EMA逸脱=自己についての予測誤差)は、この核の**部分的**な実装。
- **LLM は「穴だらけの世界モデル」を持つ**。盤面(Othello-GPT)・空間/時間(Gurnee & Tegmark)は
  線形に符号化される一方、Vafa et al. のマンハッタン・タクシー研究は「次手予測は正しいのに一貫した
  地図を持たない」ことを示す。ToM も表層改変で崩れる(Ullman)。→ **LLM の内的世界モデルに
  依存せず、世界状態を外部化する(地図・ルータ・記憶・スケジュール帳)本シムの設計は正しい**。
  逆に、外部化していない要素(混雑の予想・他者の意図・行動結果の予期)は LLM の穴がそのまま出る。
- **本題(§5)**: 欠けている行動要因候補を文献接地つきで9件導出。特に高優先は
  **(1) 規範の予期(Bicchieri の empirical/normative expectations)**、
  **(2) 環境の可制御性/結果予期(Bandura の outcome expectancy vs efficacy・Seligman)**、
  **(3) 場所・時間の期待形成(予測地図/successor representation)**。
  (1)(2) は「efficacy が天井・grievance が床に飽和して個体差が消える」という devlog 記載の
  最大の詰まり(Block #4 E7)に直接効きうる = **世界改変を試みるか否か**の閾値を動かす要因。

---

## §1. 世界モデルの系譜と定義(機械学習側)

### 1.1 定義の核
「世界モデル」= エージェントが持つ**環境のダイナミクスの内的表現**であり、典型的には
「現在の(潜在)状態 + 行動 → 次の(潜在)状態(と報酬)」を予測する生成/予測モデルを指す。
用途は **想像上のロールアウトによる計画・方策学習**(実環境を叩かずに先読みする)。Sutton の
Dyna 以来の model-based RL の系譜に、深層生成モデルを載せたのが現代の world models。

### 1.2 系譜(各アプローチが「世界の何を・どう表現するか」)

| モデル(年) | 世界の表現 | 予測対象 | 計画/行動の作り方 | 出典 |
|---|---|---|---|---|
| **Ha & Schmidhuber "World Models"(2018)** | VAE 潜在 z(画像圧縮)+ MDN-RNN の隠れ状態 h | 次フレームの潜在 z の**分布**(確率的)| 小さな線形 Controller が (z,h) → 行動。RNN の「夢」の中で方策を鍛える | [arXiv:1803.10122](https://arxiv.org/abs/1803.10122) / interactive [worldmodels.github.io](https://worldmodels.github.io/) / [PDF](https://www.cl.cam.ac.uk/~ey204/teaching/ACS/R244_2022_2023/papers/ha_arXiv_2018.pdf) |
| **PlaNet → Dreamer v1–v3(2019–2025)** | RSSM = 決定論 h + 確率 z の**潜在状態**| 潜在での状態遷移 + 報酬 + 価値 | **潜在空間の imagination** 内で価値勾配を流し方策学習。v3 は150+タスクで安定 | Dream to Control [arXiv:1912.01603](https://arxiv.org/abs/1912.01603) / [ICLR2020 PDF](https://openreview.net/pdf?id=S1lOTC4tDS)。DreamerV3 = Hafner et al. 2023/Nature(arXiv:2301.04104、**exact ID 未再確認**) |
| **MuZero(2020)** | representation/dynamics/prediction の3ネット。潜在は**値等価(value-equivalent)**= 見た目でなく報酬・価値・方策を再現すればよい | 潜在での次状態 + 即時報酬 + 方策 + 価値 | **MCTS を学習済みモデル上で回す**(実環境の規則を知らずに Atari/囲碁/将棋/チェス) | Schrittwieser et al. 2020, *Nature* 588(arXiv:1911.08265、**exact ID 未再確認**)/ [NeurIPS2021 続報](https://papers.neurips.cc/paper_files/paper/2021/file/e8258e5140317ff36c7f8225a3bf9590-Paper.pdf) |
| **LeCun JEPA / I-JEPA / V-JEPA / V-JEPA 2(2022–2025)** | **抽象表現空間**での予測(ピクセル再構成を避ける)。生成しない = 予測すべきものだけ予測 | 潜在表現の**マスク部分**を予測(自己教師) | V-JEPA 2 は**ロボットの計画**に使える world model。「物理破れ」に予測誤差=驚きが上がる | [I-JEPA(Meta)](https://ai.meta.com/blog/yann-lecun-ai-model-i-jepa/) / [V-JEPA(Meta)](https://ai.meta.com/blog/v-jepa-yann-lecun-ai-model-video-joint-embedding-predictive-architecture/) / 概説 [Turing Post](https://www.turingpost.com/p/jepa) |
| **Genie 1/2/3(DeepMind 2024–2026)** | 動画から学ぶ**生成的**世界モデル(行動可能な潜在動作)| 次フレーム(操作入力に条件づけ)| プレイ可能な3D環境をその場生成。Genie 3 は 720p/24fps・数分間の**一貫性**。2026-01 に Project Genie で一般公開拡大 | [Genie 2(DeepMind)](https://deepmind.google/blog/genie-2-a-large-scale-foundation-world-model/) / [Wikipedia](https://en.wikipedia.org/wiki/Genie_(world_model)) / [Project Genie 2026](https://www.pymnts.com/google/2026/google-deepmind-introduces-project-genie-for-interactive-ai-world-building/) |
| **NVIDIA Cosmos(2025)** | **World Foundation Model** = 動画基盤モデル(トークナイザ+予測)| 未来映像(物理AI 向け、自動運転/ロボット)| 実データ + 合成データで post-training。Predict 2.5 で最大30秒生成 | [arXiv:2501.03575](https://arxiv.org/abs/2501.03575) / [NVIDIA Cosmos](https://www.nvidia.com/en-us/ai/cosmos/) |
| **World Labs "Marble"(Fei-Fei Li, 2025)** | **3D空間そのもの**を表現(フレーム列でなく空間オブジェクト=spatial intelligence)| 3D 世界の生成・編集・拡張 | テキスト/画像/動画/粗い3Dレイアウトから世界を作り編集 | [The Deep View 概説](https://www.thedeepview.com/articles/how-world-models-became-ai-s-next-frontier) |

### 1.3 系譜からの抽出(本シムに効く3つの核概念)
1. **潜在状態での予測**: 生ピクセルでなく、行動に効く抽象状態を予測する(MuZero の value-equivalence、
   JEPA の抽象表現)。→ **本シムのエージェントは「街の生の状態」でなく、記憶・信念・自己像・認知地図
   という抽象状態で行動を選ぶ**。設計思想は一致している。
2. **予測誤差=驚き=学習/行動の駆動力**(V-JEPA の「物理破れに驚く」)。→ `drive.py` の
   `novel_place`/`unknown_word`/`congestion`/`state_change` は「予測との食い違い」の粗い代理。
   ただし現状は**固定重み**で、文脈的な「予想」を持たない(§5-C1 で拡張候補化)。
3. **想像上のロールアウトによる計画**(Dreamer の imagination、MuZero の MCTS)。→ 本シムの
   `planning.py`(朝の一日計画)・`schedule.py`(未来予定)は「先読み」の弱い版。深い多段先読みは
   未実装(§5-C5)。

---

## §2. LLM は世界モデルを持つか(実証と反証)

### 2.1 肯定側 — 内部に一貫した状態表現が線形に載る
- **Othello-GPT**(Li et al. 2023; Nanda et al. 2023): 棋譜の次手予測だけで訓練した Transformer の
  内部に**盤面状態**が符号化される。当初 Li らは非線形と報告(線形プローブの誤り20%超)だが、Nanda らは
  **「自分の駒/相手の駒/空」という手番相対の表現**にすると**線形プローブで99%超**、しかもプローブ方向へ
  **介入すると合法手が変わる**(因果的)。→ 次トークン予測から**創発的な世界表現**が出うる証拠。
  出典: [arXiv:2309.00941](https://arxiv.org/abs/2309.00941) / [Neel Nanda 解説](https://www.neelnanda.io/mechanistic-interpretability/othello)
- **空間・時間の線形表現**(Gurnee & Tegmark 2024): LLM 活性から**実世界座標・年代**を線形回帰で復元でき、
  多スケール(世界/米国/NYC・歴史上人物/作品/見出し)で成立。モデルが大きいほど内部世界モデルも改善。
  出典: [arXiv:2310.02207](https://arxiv.org/abs/2310.02207)
- **エンティティ状態トラッキング**: 文脈中のエンティティの動的状態が線形プローブで取り出せる、という
  肯定報告がある一方、より難しい設定では否定報告もあり**結論は課題依存で割れている**。
  出典: NeurIPS 2024「Do LLMs Build World Representations? Probing Through the Lens of State Abstraction」
  [PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/b1b16c4b875eb84d3585cb70d23970ca-Paper-Conference.pdf) /
  「Exploring State Tracking Capabilities of LLMs」[arXiv:2511.10457](https://arxiv.org/abs/2511.10457)

### 2.2 反証側 — 一貫していない・脆い
- **Vafa et al. 2024「Evaluating the World Model Implicit in a Generative Model」**(NeurIPS): マンハッタンの
  タクシー走行(turn-by-turn)で訓練した Transformer は、**次の曲がり方はほぼ100%妥当**で状態も現在地を
  符号化しているように見えるのに、**復元した「街路地図」は本物とかけ離れて非整合**(実在しない道・
  一貫しない接続)。Myhill–Nerode 定理に着想した新指標で「良い次トークン予測 ≠ 一貫した世界モデル」を
  定量化。→ **表面の予測性能は世界モデルの一貫性を保証しない**。
  出典: [arXiv:2406.03689](https://arxiv.org/abs/2406.03689) / [NeurIPS2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/2f6a6317bada76b26a4f61bb70a7db59-Abstract-Conference.html)
- **心の理論(ToM)の脆さ**: Kosinski は GPT-4 が false-belief 課題の大半を解くと報告
  ([arXiv:2302.02083](https://arxiv.org/abs/2302.02083) / PNAS 2024)。しかし Ullman は**論理的に無関係な
  小改変**(語順・物の性質の微変更で信念構造は保つ)で GPT-3.5 が突然失敗することを示し、「まだ ToM を
  学んでいない — 成功は表層パターン依存」と結論。Sap らも同様の批判(Ullman 2023, arXiv:2302.08399、
  **exact ID 未再確認**)。

### 2.3 「穴」がエージェントシミュレーションにどう現れるか(本シムへの含意)
- **含意1 — 外部化した所は穴が出ない**: 本シムは空間(`world/map.py`・A* ルータ)・移動・記憶
  (`memory.py`)・未来予定(`schedule.py`)・暦/天気を**世界側で外部化**している。Vafa の地図非整合や
  LLM の空間推論の脆さは、これらを LLM の内部世界モデルに任せていない限り**表面化しない**。
  → **設計判断として正しい**(世界状態は LLM の頭の中でなく、決定論の世界オブジェクトが正典)。
- **含意2 — 外部化していない所に穴が出る**: 「明日の混雑予想」「店の営業予想」「相手が何を知っているか・
  どう反応するか」「自分の行動が結果を生むか」は**LLM の内部予測に暗黙依存**しており、Vafa/Ullman の
  非整合・脆さがそのまま出る。生成発話が「昨日と矛盾する街の像」を口にしうる。→ **§5 の欠けている
  要因候補は、まさにこの穴を世界側/因子側で外部化して塞ぐ提案**として位置づく。
- **含意3 — R1 との整合**: 世界モデルを外部化すればするほど、LLM 呼び出しに依存しない決定論の状態が増え、
  **R1(呼数不変)・決定論・再現性を守りやすい**。世界モデル強化はプロジェクトの絶対制約と相性が良い。

---

## §3. 認知科学側の世界モデル(人間の行動は内的予測からどう生まれるか)

### 3.1 予測処理 / 自由エネルギー原理 / 能動的推論(Friston, Clark)
- 脳は受動的な情報処理器でなく**予測機械**。内的生成モデルの予測と感覚入力の差(**予測誤差**)を最小化する。
  **能動的推論(active inference)**: 予測に感覚を合わせる=**知覚**、感覚を予測に合わせる=**行動**。
  行動は「驚き(自由エネルギー)を下げるために世界を変える」こととして統一的に説明される。
  出典: [Active Inference/FEP 概説](https://tasshin.com/blog/active-inference-and-the-free-energy-principle/)。
  canonical: Friston 2010 *Nat Rev Neurosci*「The free-energy principle: a unified brain theory?」/
  Clark 2013 *Behav Brain Sci*「Whatever next? Predictive brains, situated agents…」(**DOI 未再確認**)
- **本シムへの写像**: `drive.py` の驚き駆動発火は「予測誤差が閾値を超えると熟慮(LLM)を起動」という
  能動的推論の粗い実装。ただし**予測(期待)そのもの**は明示的に持っていない(誤差の元になる基準線が
  固定重み)。§5-C1(場所・時間の期待形成)は、この基準線を文脈化して能動的推論に近づける提案。

### 3.2 メンタルモデル(Johnson-Laird)
- 推論は論理規則の適用でなく、**可能性のメンタルモデルを心内で構築・操作**して結論を引く。モデルは
  イコン的(構造が対象の構造に対応)。空間・時間・条件・量化などに適用される。
  出典: [PNAS 2010「Mental models and human reasoning」](https://www.pnas.org/doi/10.1073/pnas.1012933107) /
  [Wikipedia](https://en.wikipedia.org/wiki/Mental_model_theory_of_reasoning)
- **含意**: 人は「状況の複数の可能世界」を並べて選ぶ。→ **反実仮想・先読み**(§5-C3/C5)の理論的支え。

### 3.3 認知地図(Tolman)+ successor representation(Stachenfeld)
- **Tolman 1948**: ラットは報酬なしの探索でも迷路の**認知地図**を作り(潜在学習)、動機が生じると使う。
  行動は刺激-反応でなく**内的な環境地図**を参照して柔軟に生成される。
  出典: [Simply Psychology](https://www.simplypsychology.org/tolman.html) /
  [潜在学習 PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8031467/)
- **successor representation(SR)/ 予測地図**(Stachenfeld et al. 2017): 海馬は各場所を「近い将来の
  期待滞在(将来どこに行きやすいか)」で符号化する = **報酬から独立に学べる予測的な地図**。
  出典: [The hippocampus as a predictive map(bioRxiv)](https://www.biorxiv.org/content/10.1101/097170v1.full)
- **含意**: 本シムには既に Lynch 認知地図(`psych.lynch` の `familiar_places`・馴染みの場所)があるが、
  それは「よく居た場所」の**静的**要約。SR は「**次にどこへ・いつ何が起きやすいか**」の**予測的**地図で、
  §5-C1(混雑・営業の期待形成)の理論骨格になる。lit ノート
  [`envpsych__cognitive-maps-affordance-overview.md`](../lit/envpsych__cognitive-maps-affordance-overview.md)
  に既に Tolman+Gibson の接地あり。

### 3.4 prospection / 未来の心的シミュレーション(Gilbert & Wilson, Schacter)
- **prospection**(未来を思い描く)と**episodic future thinking(EFT)**: 人は将来のエピソードを心内で
  シミュレートし、その**予感(prefeeling)**が far-sighted な意思決定・感情制御を動機づける。EFT と
  episodic counterfactual thinking(過去の反実)は海馬中心の**共通コアネットワーク**を使う。
  出典: [Schacter et al. 2015(PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4071128/) /
  [Schacter et al. 2017](https://scienceofbehaviorchange.org/wp-content/uploads/2017/11/Schacter_Benoit_Szpunar_2017.pdf)。
  canonical: Gilbert & Wilson 2007 *Science*「Prospection: Experiencing the future」(**DOI 未再確認**)
- **含意**: `planning.py`(朝の計画)は prospection の弱い実装。**予期される結果に対する感情(anticipated
  regret / prefeeling)**が行動選択に効く経路は未実装(§5-C7)。

### 3.5 シミュレーション・ヒューリスティック / 反実仮想 / 後悔(Kahneman & Tversky)
- **simulation heuristic**: 事象の起こりやすさ・後悔の強さを「その事象を**心内で描く容易さ**」で判断する
  (availability の構築版)。**norm theory**: 反実仮想の代替が思い浮かびやすいほど、実際の出来事は
  「異常」に感じられ後悔が増す。
  出典: [Simulation heuristic(Wikipedia)](https://en.wikipedia.org/wiki/Simulation_heuristic)。
  canonical: Kahneman & Tversky 1982「The simulation heuristic」
- **含意**: 「もし別の行動をしていたら」という**反実仮想的後悔**が次の行動を変える。本シムの内省
  (`reflection.py`)は事後の意味づけを持つが、**行動選択前の反実仮想/後悔**は未実装(§5-C3/C7)。

### 3.6 可制御性・効力・学習性無力感(Bandura, Seligman)— 世界改変の閾値に直結
- **Bandura**: **効力予期(efficacy expectancy=自分がその行動を遂行できるか)**と
  **結果予期(outcome expectancy=その行動が結果を生むか)**は**別次元**。前者が高くても、環境が応答しないと
  信じれば行動は起きない。
- **Seligman(学習性無力感)**: 「結果が自分の反応と独立」と学習すると、遂行能力があっても行動が枯れる
  (**可制御性の感覚**の欠如)。
  出典: [Self-efficacy(Wikipedia)](https://en.wikipedia.org/wiki/Self-efficacy) /
  [学習性無力感の再定式化(Abramson, Seligman & Teasdale 1978)PDF](https://ppc.sas.upenn.edu/sites/default/files/lhreformulation.pdf)
- **含意(重要)**: 本シムの `efficacy`(効力感)は Bandura の**効力予期側**に相当し、devlog(Block #4 E7)は
  「efficacy が天井・grievance が床に飽和して個体差が消える」= 変革モチベの最大の詰まりと記録。
  Bandura/Seligman の理論は「**足りないのは結果予期=環境の可制御性の感覚**」という別軸を指す。
  → §5-C2 の核。

### 3.7 規範の予期(Bicchieri)— 「人がどう反応するか」の内的モデル
- **社会規範 = 条件付き選好**。人が規範に従うのは (i)**経験的期待**(他人も従うと思う)+ (ii)**規範的期待**
  (他人が自分に従うことを期待していると思う)が揃うとき。期待が崩れれば規範も崩れる(逸脱・改変)。
  出典: [Grammar of Society 抜粋(Cambridge)](https://assets.cambridge.org/97805215/73726/excerpt/9780521573726_excerpt.pdf) /
  [Norms, preferences, and conditional behavior(Bicchieri 2010)PDF](https://www.sas.upenn.edu/~cb36/files/2010_norm.pdf)
- **含意**: 本シムには Searle 制度化・再帰性の `norm_line`(いま実効の取り決め)はあるが、**エージェント
  個々の「他人はこう反応するはず」という予期**は未実装。世界改変を**試みるか/抑制するか**は、まさにこの
  規範的期待の破れで決まる(committed minority が規範を破って相転移=k* と同型)。→ §5-C6 の核。

---

## §4. 世界モデル × LLMエージェントの直接交差

- **RAP(Reasoning via Planning; Hao et al. 2023)**: **同一の LLM を「世界モデル」と「推論エージェント」に
  二役**させ、LLM が状態と行動結果をシミュレートしながら **MCTS** で推論木を張る。報酬=行動尤度+状態
  確信度+自己評価。→ LLM に**明示的な先読み**を持たせる代表例。
  出典: [arXiv:2305.14992](https://ar5iv.labs.arxiv.org/html/2305.14992)
- **Text World Models for LLM agents(2026)**: LLM エージェントの行動計画のために、テキスト世界の遷移
  モデルを LLM に持たせて agent-world ギャップを埋める試み。
  出典: [arXiv:2606.09032](https://arxiv.org/pdf/2606.09032)
- **本シムへの含意**: RAP 型の「LLM に多段先読みさせる」は魅力的だが、**追加の generate() 呼び出しを大量に
  伴う** = R1(呼数不変)・LOD 予算・決定論・再現性と真っ向から衝突する。本シムでは
  **(a) 世界側の決定論モデルで先読みを外部化**(ルータ・スケジュール帳・混雑予測)し、
  **(b) LLM には既存1呼のプロンプトに「先読み結果」を注入するだけ**にするのが制約整合的。
  = RAP の「先読みを行動に効かせる」思想を、呼数を増やさず取り込む方向(§5 の実装スケッチはすべてこの型)。

---

## §5. 【本題】エージェント行動に影響する世界モデル的要因の導出

**方法**: §1–§4 の理論から「人間の行動を決める世界モデル的要因」を列挙し、本シムの既実装
(驚き駆動LOD・belief書き戻し・implicit_self・Lynch認知地図・スケジュール帳・FJ意見力学・self_model・
needs/values)と照合して **(a) 実装済みの対応物** と **(b) 欠けている候補** に仕分ける。
制約の記法: 【決】=決定論で可 / 【呼】=LLM 呼数不変(R1)で可 / 【指】=no-fingerprint 可
(因子/構成概念名を `src/society` 直下 or `factors/` に閉じ、engine/cognition/world へは不透明な
文字列・倍率・座標だけ渡す)。

### 5-A. 実装済みの対応物がある要因(世界モデル的機構の既存マッピング)

| 世界モデル的要因 | 理論 | 本シムの実装済み対応物 |
|---|---|---|
| **予測誤差=驚きによる行動起動** | 能動的推論 / V-JEPA | `drive.py`(novel_place/unknown_word/congestion/state_change → ゲージ → 閾値発火)。LOD=予測誤差時のみ熟慮 |
| **潜在状態での行動選択(生入力でなく抽象状態)** | MuZero value-equivalence / JEPA | 記憶・信念・自己像・気分という抽象状態を `build_prompt` に注入して行動を選ぶ |
| **内省の産物が行動に流入(信念の書き戻し)** | 予測誤差による信念更新 | `reflection.py` belief writeback → `build_prompt`「あなたの考え」(k のゲート) |
| **自己についての予測誤差(暗黙の自己)** | Bem 自己知覚 / working self-concept | `implicit_self`(行動カウント EMA 逸脱→「最近の自分」1行) |
| **物語的自己(核自己)** | narrative identity(McAdams) | `self_model`(深い内省の self/ties → プロンプト注入) |
| **空間の認知地図(馴染みの場所)** | Tolman / Lynch imageability | `psych.lynch` の `familiar_places` |
| **未来予定の保持(prospection の一部)** | EFT / prospection | `schedule.py`(会話から決定論抽出→帳簿→注入)・`planning.py`(朝の一日計画) |
| **他者の意見という社会状態(の一部)** | 意見力学 | `opinion.py`(Friedkin-Johnsen)・`relations.py`(tier/評判) |
| **何を予測して欲するか(価値・欲求)** | SDT / 価値論 | `needs`(5次元)・`values`(4軸: 実用/感情/社会/認識)・`sat_mods`(飢えた価値の感度倍率) |
| **効力予期(自分は遂行できるか)** | Bandura efficacy expectancy | `factors` の state `efficacy`(+ SIMCA/Bandura 更新則) |

**所見**: 予測誤差の「**検出**」側(驚き)と、行動の「**内的状態化**」側(信念・自己・欲求)は厚い。
一方で **予測の「生成」側**(明日どうなる・相手はどう出る・自分の行動は結果を生むか)= **前向きの世界
モデル**が薄い。§5-B はここを埋める。

### 5-B. 欠けている要因候補(前向きの世界モデル)

各候補: 理論的根拠 | 行動への影響経路 | 実装スケッチ(制約内)| 優先度(私見)。

---

#### C1. 場所・時間の期待形成(混雑・営業・イベントの予想)
- **理論**: successor representation / 予測地図(Stachenfeld)、能動的推論の予測基準線、Tolman 認知地図の
  予測的側面。人は「この時間のスクランブルは混む」「この店は夜閉まる」を**予想して**行動する。
- **影響経路**: (1) 行き先選択(混雑回避・営業時間内を狙う)、(2) **驚きの文脈化** — 予想と実際の差だけが
  予測誤差=驚きになる(いつも混む場所で混んでも驚かない)。現状 `drive.py` の congestion 重みは固定=
  「毎回同じだけ驚く」非現実。
- **実装スケッチ**: 世界側に**決定論の期待テーブル**(ノード×時間帯 → 期待混雑/営業フラグ)を、過去ステップの
  実測 or POI 営業時間から**決定論集計**で構築(乱数不要)。エージェントには (a) プロンプトに「この時間の
  ○○は混みそう/△△は閉まる頃」1行を注入【呼】、(b) `drive.py` の congestion 加算を `実測 − 期待` の
  逸脱に比例させる(既存 `implicit_self` の EMA 逸脱と同じ発想を**環境**へ拡張)。期待は全員共通 or
  個人の訪問履歴由来にできる。行き先バイアスに使うと物理位置=co-location が変わる(crowd/観光 G4/H5 と
  同型)ので、**compute_matched 下で free==off の呼数一致**で R1 を担保。因子名は出さない【指】。
- **優先度: 高**。安価(既存の混雑/営業データを流用)・決定論・驚きの現実性を上げ、行動の先読み性を出す。
  §3.1/§3.3 の中核概念を最小コストで入れられる。

#### C2. 環境の可制御性 / 結果予期(outcome expectancy・学習性無力感)
- **理論**: Bandura(効力予期 ≠ 結果予期)、Seligman(可制御性の感覚)。「自分がやれば**世界は応答する**か」。
- **影響経路**: **世界改変を試みるか否かの閾値**。効力(遂行できる)が高くても、結果予期(応答する)が低ければ
  提案・出店・イベント開催をしない。devlog 記載の「efficacy 天井・grievance 床への飽和で個体差消失」に対し、
  **飽和しない第2軸**として個体差・経路依存(k)を担いうる。
- **実装スケッチ**: `factors` に新 state `controllability`(or `outcome_expectancy`)を追加(psych プラグインと
  同型・**既定 OFF で snapshot/L2 バイト一致**)。更新則(`factors/update.py` レジストリ、**イベントのみ参照=
  R9**): 自分の提案が成立/却下、host_event の参加者数、propose→norm 化の成否、店の売上などの
  **客観結果イベント**で上下(反応が結果を生めば↑、無反応・却下続きで↓=学習性無力感)。行動側は、
  ツール提示(`tools.py`)や発火重みへ**不透明な倍率**として effに効かせる【指】。**LLM 呼数は不変**
  (state 更新は非LLM)【呼】、乱数不要 or 既定 draw を汚さない【決】。
- **優先度: 高**。研究の問い(世界改変者は生得か創発か・k*)に**理論的に最も近い**欠落。飽和の詰まりを
  破る第一候補。ただし R4(改変カウントは客観)・compute 交絡(sham/null 対照)との整合を要検証。

#### C3. 行動結果の予測 + 反実仮想的後悔
- **理論**: simulation heuristic / norm theory(Kahneman & Tversky)、episodic counterfactual thinking
  (Schacter)、後悔(Roese)。「もし別の行動をしていたら」で次の行動が変わる。
- **影響経路**: 期待した結果が外れたとき**後悔**が生じ、次の行動選択・drive・気分に効く(far-sighted 化 or
  回避学習)。現状の内省は事後の意味づけはするが、**期待 vs 実結果の差分としての後悔**を状態化していない。
- **実装スケッチ**: 行動時に**期待値(client-side・決定論)**を残し(例: host_event で期待参加者、venture で
  期待売上=過去平均)、結果イベントとの差を `regret`/`disappointment` として `factors` に集計。プロンプトに
  「先日の○○は思ったほど…だった」1行を注入【呼】し、`drive`/`affect` に不透明倍率で効かせる。全て
  観測イベントの決定論後処理=乱数なし【決】、追加 generate() なし【呼】、因子名非注入【指】。
- **優先度: 中**。理論的に豊かで prospection/EFT を閉じるが、「期待値の決定論的定義」に設計判断が要り、
  C1(期待テーブル)が先にあると実装が楽になる(C1 の下流)。

#### C4. 他者モデル(theory of mind = 相手の意図・知識・信念の推定)
- **理論**: ToM。§2.2 の通り LLM の ToM は表層改変で脆い(Ullman)→ **相手モデルを外部化**すべき。
- **影響経路**: 発話・DM・説得の内容が「相手が何を知っている/信じている/望むか」に条件づく。現状は
  `opinion.py`(相手のスカラ意見)・`relations.py`(tier)止まりで、**相手の知識状態・信念の推定**がない
  = 会話が「相手を知らないまま話す」LLM の穴が出やすい。
- **実装スケッチ**: `memory.py`/`relations.py` に、過去の対面・DM から**相手について観測した事実の決定論
  ダイジェスト**(例: 「○○は△△を知っている/□□に関心がある」)を蓄積し、会話プロンプトに
  「相手について: …」1行として注入【呼】。**信念の入れ子(相手が自分の信念をどう思うか)までは持たず**、
  「観測した相手の属性・既知語・関心」の一次近似に留める(looking-glass の正確性問題と同じ理由で過剰な
  「相手の真意」注入は避ける — self-concept-identity.md §2.6 と整合)。決定論・呼数不変・因子名なし。
- **優先度: 中**。会話の質・説得の現実性を上げ、伝播(k*)の素材になるが、相手モデルの粒度設計が要相談。

#### C5. 計画の先読み深さ(planning horizon / 多段プロスペクション)
- **理論**: Dreamer の imagination・MuZero/RAP の多段先読み、メンタルモデルの可能性展開(Johnson-Laird)。
  人・エージェントで先読みの深さに個体差がある。
- **影響経路**: 1日計画(現状)より長い horizon(数日〜数週の目標→中間計画)を持つと、行動の一貫性・
  keystone 行動(§ `inner_life` の `life_goal`)が強まる。RAP 型の多段 LLM 先読みは**呼数爆発で R1 違反**。
- **実装スケッチ**: **追加 LLM なし**で、既存の `inner_life.life_goal`(長期目標)+ `schedule` の horizon を
  接続し、朝の1呼の計画プロンプトに「長期目標 → 今日の一手」の橋渡し1行を注入【呼】。先読み「深さ」は
  trait 由来の**決定論パラメータ**(horizon_days・目標の粒度)として写像【決】【指】。RAP 的な木探索は
  採らない(制約非整合)。
- **優先度: 中〜低**。効果はあるが `inner_life`(目標)+ `schedule`(予定)+ `planning`(朝計画)の
  **接続**が主で、新規性は限定的。まず配線で取れる分を取る。

#### C6. 規範の予期(descriptive/injunctive norm・「人がどう反応するか」)
- **理論**: Bicchieri の empirical/normative expectations、Cialdini の descriptive/injunctive norms。
  「他人も普通そうしている(記述)」「他人は自分にこうあれと期待している(命令)」の内的推定。
- **影響経路**: **規範への同調 vs 逸脱=世界改変を試みるかの閾値**。committed minority が規範的期待を破って
  相転移(§ complexity の tipping ~25%)= **k* と同型**。現状 `norm_line`(実効の取り決め)はあるが、
  エージェント個々の「破ったら周囲はどう反応するか」の予期がない。
- **実装スケッチ**: 世界側で**記述的規範の決定論集計**(直近の街の行動分布=`recursion` の digest 素材の
  拡張。例: 「最近この街では○○する人が多い/少ない」)をプロンプトに1行注入【呼】。個人側は
  規範感受性を trait から写像し、逸脱(coin/propose/host 等)の発火重みに不透明倍率で効かせる【指】。
  命令的規範(他者の是認/非難の予期)は、対面イベントの反応(既存の返答・評判 `reputation`)から
  決定論で近似。乱数なし・呼数不変。
- **優先度: 高**。研究の問い(k*・改変者の創発・崩壊回避)に**直結**。C2(可制御性)と対の「社会側の
  可制御性/許容度」を与え、改変を試みる/抑える両方向の力を明示化できる。

#### C7. 予期的感情(anticipated regret / prefeeling)による行動バイアス
- **理論**: prospection の prefeeling(Gilbert & Wilson)、anticipated regret。将来の感情の**予感**が現在の
  選択を動かす(far-sighted 化・回避)。
- **影響経路**: 「行ったら後悔しそう/嬉しそう」で行き先・発話・改変行動が変わる。C3(事後の後悔)の
  **前向き版**。
- **実装スケッチ**: C1(期待)+ C3(後悔履歴)があれば、**過去の後悔/満足の決定論集計**を「この手の予定は
  以前○○だった」1行としてプロンプトに注入【呼】するだけで近似できる(新規 LLM なし)。affect の
  arousal/salience に不透明に効かせる余地。決定論・呼数不変・因子名なし。
- **優先度: 低〜中**。C1/C3 の上に乗る派生。単独では優先度低いが、prospection の環を閉じる仕上げ。

#### C8. 環境アフォーダンスの学習(「この場所で何ができるか」の獲得)
- **理論**: Gibson affordance + Tolman 認知地図(経験で更新)。現状 POI カテゴリで affordance は**所与**だが、
  人は「この店は○○に使える」を**経験から学ぶ**。lit
  [`envpsych__cognitive-maps-affordance-overview.md`](../lit/envpsych__cognitive-maps-affordance-overview.md)に接地あり。
- **影響経路**: 個人ごとに「行きつけの用途」が分化=行動の個体差・経路依存(k の素材)。
- **実装スケッチ**: `memory.py` に**場所×用途の決定論カウント**を持ち、`familiar_places` を「用途つき」に
  拡張(「○○(よく食事する)」)してプロンプト注入【呼】。乱数なし・因子名なし。既存 Lynch 地図の自然な拡張。
- **優先度: 低**。C1 と機構が近く(場所メモリの拡張)、単独価値は限定的。C1 と併せて設計するのが効率的。

#### C9. 予測誤差の精度重み付け(precision / 顕著性の学習)
- **理論**: 能動的推論の**precision weighting**(予測誤差にどれだけ注意=学習率を割くか)。§ `affect`(arousal/
  salience)が既にこの役割の一部を担う。
- **影響経路**: どの驚きを「効かせる」かの個人差・状態依存。現状 affect ハブ+E2 ドリフト(馴化/鋭敏化)で
  部分実装。
- **実装スケッチ**: 新規というより **`affect` + `drive` の E2 ドリフトの本番配線**と、C1 の期待テーブルを
  精度重みの入力に足す設計。追加機構は最小。
- **優先度: 低(既存機構の配線・調律が主)**。単独の新実装は不要。

---

## §6. 行動要因候補の総括表(次バッチの実装判断用)

| # | 要因 | 理論接地 | 既実装との対応 | 実装スケッチ(制約: 決/呼/指) | 優先度 |
|---|---|---|---|---|---|
| A | 予測誤差=驚きで発火 | 能動的推論・V-JEPA | **実装済** `drive.py` | — | 済 |
| A | 内的抽象状態で行動 | MuZero/JEPA | **実装済** `build_prompt` | — | 済 |
| A | 信念/自己/欲求の内的表現 | 予測誤差更新・narrative self・SDT | **実装済** belief/self_model/implicit_self/needs/values | — | 済 |
| A | 空間認知地図 | Tolman/Lynch | **実装済** `psych.lynch` familiar_places | — | 済 |
| A | 未来予定(prospection一部) | EFT | **実装済** schedule/planning | — | 済 |
| A | 効力予期 | Bandura efficacy | **実装済** state `efficacy` | — | 済 |
| **C1** | **場所・時間の期待形成(混雑/営業予想)** | SR/予測地図・能動的推論 | 部分(Lynch は静的・congestion 固定重み) | 世界側に決定論の期待テーブル→注入1行【呼】+ drive を「実測−期待」逸脱に【決】。行き先バイアスは compute_matched で free==off 担保 | **高** |
| **C2** | **環境の可制御性/結果予期** | Bandura outcome expectancy・Seligman | 欠落(efficacy は効力側のみ) | 新 state `controllability`(psych 型・既定OFFでバイト一致)。客観結果イベントで更新【決/呼】、発火重みへ不透明倍率【指】 | **高** |
| C3 | 行動結果の予測+反実仮想的後悔 | simulation heuristic・ECT・regret | 欠落(内省は事後意味づけのみ) | 行動時に決定論期待値を残し結果差=regret を集計→注入1行【呼】。C1 の下流 | 中 |
| C4 | 他者モデル(ToM=意図/知識推定) | ToM(LLMは脆い→外部化) | 部分(opinion スカラ・relations tier) | 相手の観測事実の決定論ダイジェスト→会話注入1行【呼】。信念入れ子は持たず一次近似【指】 | 中 |
| C5 | 計画の先読み深さ(horizon) | Dreamer/MuZero/RAP・メンタルモデル | 部分(1日計画のみ) | inner_life 目標+schedule horizon+朝計画の**接続**。深さは trait→決定論param【決】。RAP木探索は不採用(R1) | 中〜低 |
| **C6** | **規範の予期(記述/命令規範・反応予測)** | Bicchieri・Cialdini | 部分(norm_line は実効ルールのみ) | 記述規範を決定論集計→注入1行【呼】。規範感受性 trait→逸脱発火の不透明倍率【指】。k* に直結 | **高** |
| C7 | 予期的感情(anticipated regret/prefeeling) | prospection prefeeling | 欠落 | C1+C3 の上に過去後悔/満足の集計→注入1行【呼】。affect へ不透明結合 | 低〜中 |
| C8 | アフォーダンス学習(場所の用途獲得) | Gibson+Tolman | 部分(POIカテゴリは所与) | memory に場所×用途カウント→familiar_places を用途つきに拡張【呼/決/指】 | 低 |
| C9 | 予測誤差の精度重み付け | active inference precision | 部分(affect+E2ドリフト) | 新規でなく affect/drive-drift の本番配線+C1 を入力に | 低(配線主) |

**総括の私見**: 本シムの世界モデルは「予測誤差の**検出**と行動の**内的状態化**」が厚く、「**前向きの予測
生成**」が薄い、という非対称がある。次バッチで最も効くのは、研究の問い(改変者の生得/創発・k*)に
直結し、かつ既知の詰まり(efficacy 飽和)を破りうる **C2(可制御性/結果予期)と C6(規範の予期)**。
両者は「**やっても世界は応えるか(C2=個人×環境)**」と「**やったら周囲はどう出るか(C6=個人×社会)**」の
対で、世界改変を試みる/抑える閾値を新しい2軸で開く。安価で足回りの良い **C1(期待形成)**は C3/C7/C8/C9 の
共通土台になるため、C1 → C2/C6 → C3/C4 → C7/C8/C9 の順で入れると設計の依存関係がきれいに乗る。
**いずれも「世界側/因子側で外部化 → 既存1呼のプロンプトに不透明な1行を注入」**という同一の型で、
決定論・R1呼数不変・no-fingerprint を保てる(§4 の制約整合方針)。実装可否・粒度・対照設計(compute_matched・
sham/null、R4 客観カウント)は実装前に要すり合わせ。

---

## §7. 出典一覧(URL。本調査の Web 検索結果に出現したもの)

**ML 世界モデル**
- Ha & Schmidhuber (2018) World Models — [arXiv:1803.10122](https://arxiv.org/abs/1803.10122) / [worldmodels.github.io](https://worldmodels.github.io/) / [PDF](https://www.cl.cam.ac.uk/~ey204/teaching/ACS/R244_2022_2023/papers/ha_arXiv_2018.pdf)
- Hafner et al. Dream to Control (Dreamer, ICLR2020) — [arXiv:1912.01603](https://arxiv.org/abs/1912.01603) / [PDF](https://openreview.net/pdf?id=S1lOTC4tDS)
- Schrittwieser et al. (2020) MuZero, *Nature* — 続報 [NeurIPS2021 PDF](https://papers.neurips.cc/paper_files/paper/2021/file/e8258e5140317ff36c7f8225a3bf9590-Paper.pdf)
- LeCun JEPA — [I-JEPA(Meta)](https://ai.meta.com/blog/yann-lecun-ai-model-i-jepa/) / [V-JEPA(Meta)](https://ai.meta.com/blog/v-jepa-yann-lecun-ai-model-video-joint-embedding-predictive-architecture/) / [JEPA 概説(Turing Post)](https://www.turingpost.com/p/jepa)
- DeepMind Genie — [Genie 2](https://deepmind.google/blog/genie-2-a-large-scale-foundation-world-model/) / [Wikipedia](https://en.wikipedia.org/wiki/Genie_(world_model)) / [Project Genie 2026](https://www.pymnts.com/google/2026/google-deepmind-introduces-project-genie-for-interactive-ai-world-building/)
- NVIDIA Cosmos (2025) — [arXiv:2501.03575](https://arxiv.org/abs/2501.03575) / [NVIDIA](https://www.nvidia.com/en-us/ai/cosmos/)
- World Labs / Marble・世界モデル動向 — [The Deep View](https://www.thedeepview.com/articles/how-world-models-became-ai-s-next-frontier)

**LLM の世界モデル(実証と反証)**
- Nanda et al. (2023) Emergent Linear Representations (Othello-GPT) — [arXiv:2309.00941](https://arxiv.org/abs/2309.00941) / [Neel Nanda](https://www.neelnanda.io/mechanistic-interpretability/othello)
- Gurnee & Tegmark (2024) Language Models Represent Space and Time — [arXiv:2310.02207](https://arxiv.org/abs/2310.02207)
- Do LLMs Build World Representations? (NeurIPS 2024) — [PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/b1b16c4b875eb84d3585cb70d23970ca-Paper-Conference.pdf) / State tracking — [arXiv:2511.10457](https://arxiv.org/abs/2511.10457)
- Vafa et al. (2024) Evaluating the World Model Implicit in a Generative Model — [arXiv:2406.03689](https://arxiv.org/abs/2406.03689) / [NeurIPS2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/2f6a6317bada76b26a4f61bb70a7db59-Abstract-Conference.html)
- Kosinski (2024) Evaluating LLMs in ToM tasks — [arXiv:2302.02083](https://arxiv.org/abs/2302.02083)(批判: Ullman 2023 / Sap ら)

**認知科学の世界モデル**
- 予測処理/自由エネルギー/能動的推論(Friston, Clark)— [概説](https://tasshin.com/blog/active-inference-and-the-free-energy-principle/)
- Johnson-Laird メンタルモデル — [PNAS 2010](https://www.pnas.org/doi/10.1073/pnas.1012933107) / [Wikipedia](https://en.wikipedia.org/wiki/Mental_model_theory_of_reasoning)
- Tolman 認知地図/潜在学習 — [Simply Psychology](https://www.simplypsychology.org/tolman.html) / [潜在学習(PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8031467/)
- Stachenfeld et al. (2017) 予測地図/successor representation — [bioRxiv](https://www.biorxiv.org/content/10.1101/097170v1.full)
- Schacter et al. prospection/EFT/ECT — [2015(PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4071128/) / [2017](https://scienceofbehaviorchange.org/wp-content/uploads/2017/11/Schacter_Benoit_Szpunar_2017.pdf)
- Kahneman & Tversky simulation heuristic / norm theory — [Wikipedia](https://en.wikipedia.org/wiki/Simulation_heuristic)
- Bandura 自己効力/結果予期 — [Wikipedia](https://en.wikipedia.org/wiki/Self-efficacy)。Seligman 学習性無力感 — [Abramson, Seligman & Teasdale 1978(PDF)](https://ppc.sas.upenn.edu/sites/default/files/lhreformulation.pdf)
- Bicchieri 社会規範(経験的/規範的期待)— [Grammar of Society 抜粋](https://assets.cambridge.org/97805215/73726/excerpt/9780521573726_excerpt.pdf) / [Bicchieri 2010(PDF)](https://www.sas.upenn.edu/~cb36/files/2010_norm.pdf)

**世界モデル × LLM エージェント**
- Hao et al. (2023) Reasoning via Planning (RAP) — [arXiv:2305.14992](https://ar5iv.labs.arxiv.org/html/2305.14992)
- Text World Models for LLM Agents (2026) — [arXiv:2606.09032](https://arxiv.org/pdf/2606.09032)

**本シム内の関連ノート(既存)**
- [`envpsych__cognitive-maps-affordance-overview.md`](../lit/envpsych__cognitive-maps-affordance-overview.md)(Tolman 認知地図+Gibson affordance)
- [`urban__lynch1960_image-of-the-city.md`](../lit/urban__lynch1960_image-of-the-city.md)(Lynch 5要素)
- [`self-concept-identity.md`](./self-concept-identity.md)(二層自己・looking-glass の正確性問題= C4 の設計注意)
- [`world-change-motivation.md`](./world-change-motivation.md)(efficacy 飽和の詰まり= C2/C6 の動機)

---

## 未確認事項(事実と推測の区別)

- **一次PDFは全件は直接取得していない**。arXiv 番号のうち検索結果本文で確認したもの:
  1803.10122(Ha&Schmidhuber)/ 1912.01603(Dream to Control)/ 2309.00941(Nanda Othello)/
  2310.02207(Gurnee&Tegmark)/ 2406.03689(Vafa)/ 2302.02083(Kosinski)/ 2305.14992(RAP)/
  2501.03575(Cosmos)/ 2511.10457(state tracking)/ 2606.09032(Text World Models)。
- **exact ID を再確認していない**(標準的書誌からの記載): DreamerV3(arXiv:2301.04104 と一般に知られる)・
  MuZero(arXiv:1911.08265・*Nature* 588)・I-JEPA(arXiv:2301.08243)・Li et al. Othello 原著
  (ICLR2023「Emergent World Representations」arXiv:2210.13382)・Ullman ToM 批判(arXiv:2302.08399)。
  番号・巻号は要再確認。
- **DOI 未再確認**: Friston 2010 *Nat Rev Neurosci*・Clark 2013 *Behav Brain Sci*・Gilbert & Wilson 2007
  *Science*・Kahneman & Tversky 1982・Tolman 1948・Bandura 1977・Stachenfeld et al. 2017 *Nat Neurosci*
  は理論名・著者・年のみ検索で確認。原著の巻号頁は本調査では取得していない。
- **§5 の実装スケッチはすべて設計提案(推測)**であり、実証された数値・パラメータではない。特に
  C2(可制御性)・C6(規範の予期)を state 化する場合の **compute 交絡対策(sham/null・compute_matched)・
  R4 客観カウントとの整合・R1 の free==off 呼数一致**は実装前の要検証事項。優先度は Opus の私見であり、
  ユーザー判断・実装前アジェンダですり合わせる前提。
- **「efficacy が Bandura の効力予期側に相当」という対応づけ**は理論的解釈であり、本シムの `efficacy` 更新則が
  厳密に Bandura の効力予期の operationalization であることを検証したわけではない(SIMCA/Bandura 4源泉を
  入力にした複合 state=近似)。
