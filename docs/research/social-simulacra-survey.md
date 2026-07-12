# Social Simulacra 分野サーベイ — 先行研究・社会実装・本プロジェクトへのヒント

作成: 2026-07-11 / 担当: Opus(リサーチ・コード変更なし・読み取りのみ)

## この文書の目的

ユーザーの問い —「本シミュレーションは *Social Simulacra* という分野に分類されるらしい。ほかにどんな
先行研究があり、どんな知見が活かせるか。固有名詞に固執せず『LLM で社会がどう変化するかを観察する
プロジェクト』を貪欲に集め、特に **他プロジェクトがどんな社会実装を検討しているか / 本プロジェクトを
進める大きなヒント** を重点的に」——に答えるための調査。

既存の文献メモ(`docs/lit/mas__yang2024_oasis.md` 等、`docs/research/framework-architecture.md`、
`docs/lit/measurement__validation-overview.md`)と重複する部分は**既読の上積み**にとどめ、
未カバーの発掘(Park の系譜の目的変遷 / 中国「世界モデル」群 / 商用 synthetic users 市場 /
日本のデジタルツイン・PLATEAU / 2025–2026 の妥当性フレームワーク)と、**社会実装・ビジネス形態**の
分析に紙幅を割く。一次ソース優先。未確認は本文で明記した(捏造禁止)。

結論の要旨を先に:

- **系譜**: Social Simulacra(Park 2022)は「**ソーシャルコンピューティングの設計プロトタイピング道具**」
  として生まれた。Park 2023(Smallville)で「認知の忠実な再現」へ、Park 2024(実在1,000人接地)で
  「**実在個人の proxy = 予測・代理実験の道具**」へと、目的が「設計支援 → 認知研究 → 予測/代替実験」と
  重心移動している。
- **社会実装のカネの流れ**: 支払われているのは「シミュレーションそのもの」ではなく、**現実に金・時間・
  倫理コストを払わずに済ませる "what-if" への答え**(広告/製品/選挙の賭けの事前検証、政策の事前テスト、
  募集不能な母集団へのアクセス、反実仮想)。速さ・安さ・安全性・アクセス不能性がプレミアム。
- **本プロジェクトの位置**: 物理接地(実地図・実ダイヤ・経路移動)・現実バンド較正・決定論リプレイ・
  compute-matched null 対照は、**2025–2026 の妥当性批判(PIMMUR / 平均ペルソナ収束 / 再現性危機)に
  対して既に先行**している。借りるべきは (a) 実インタビュー接地(Park 2024, +14–15pt)、(b) PIMMUR
  自己監査の明示、(c) 多アダプタ LoRA による異質性(飽和問題の技術的打開)。

---

## 1. 系譜の起点 — Park の3部作と「何のために社会を模擬するのか」の変遷

「Social Simulacra」という固有名詞は Joon Sung Park(Stanford HCI / のち Google DeepMind)の一連の
研究に由来する。この3部作の**目的の変遷**を正確に押さえることが、本分野の座標軸になる。

### 1.1 Social Simulacra(Park et al., UIST 2022)= 原点は「設計プロトタイピング道具」

- **何のため**: **ソーシャルコンピューティングシステム(オンラインコミュニティ)の設計を、実ユーザーを
  集める前にプロトタイプする**ため。新しいコミュニティ/掲示板を作る設計者は「クリティカルマスの
  ユーザーを集めないと、どんな社会力学(荒らし・対立・話題の偏り)が起きるか分からない」というジレンマを
  抱える。Social Simulacra は、設計者が与えた**コミュニティの目的・ルール・メンバーのペルソナ**から、
  LLM(当時 GPT-3)が**投稿・返信・反社会的行動まで**を自動生成し、設計者が**デプロイ前に創発的な
  社会力学を予見**できるようにする。
- **具体物 SimReddit**: Reddit 型コミュニティのプロトタイピング・ツール。設計者は数行の設計仕様から
  「もしこのルールなら、どんな会話・荒らし・炎上が起きるか」を対話的に探索できる。設計を具体的な
  アーティファクトに翻訳し、設計空間の反復探索を支援する。
- **本プロジェクトにとっての含意**: 分野の**原初的な目的は「予測」でも「認知研究」でもなく「設計支援
  (プロトタイピング)」**だった。=「作る前に、社会がどう動くかを安く試す」。この原点は、後述する
  商用 synthetic users / policy sandbox のビジネス価値と直結している(§4)。
- 出典: [Stanford HCI PDF](https://hci.stanford.edu/publications/2022/Park_SocialSimulacra_UIST22.pdf) /
  [ACM DL](https://dl.acm.org/doi/10.1145/3526113.3545616)

### 1.2 Generative Agents / Smallville(Park et al., UIST 2023)= 「認知の忠実な再現」へ

- **何のため**: 個体の**信じられる行動(believable behavior)**を長期に生成する認知アーキテクチャの提案。
  25体のエージェントが Smallville で日常を送り、バレンタインパーティの企画が**自発的に伝播・創発**した。
- **機構**: Memory Stream(タイムスタンプ付き自然言語ログ)+ recency/importance/relevance の検索 +
  **Reflection**(生観測から高次の洞察を後段生成)+ **Planning**。→ 本プロジェクトの `agents/memory.py` +
  `cognition/reflection.py` + `cognition/planning.py` はこの系譜。
- **目的のシフト**: 「設計プロトタイプ(2022)」から「**個体認知を信じられる形で再現する(2023)**」へ。
  評価軸も「設計に役立つか」から「人間らしいか(believability)」へ移った。
- 既存メモに詳細は無いが `docs/research/data-pipeline-lit.md` §4 に memory stream の記述あり。
  出典: [arXiv:2304.03442](https://ar5iv.labs.arxiv.org/html/2304.03442)

### 1.3 Generative Agent Simulations of 1,000 People(Park et al., 2024)= 「実在個人の proxy = 予測・代替実験」へ

- **何のため**: **実在する1,052人**を各2時間の**質的インタビュー**で接地し、その人の**態度・行動を
  当てるエージェント**を作る。「**募集できない/繰り返せない人間実験の代替**」を狙う。
- **検証(★重要な数字)**: 生成エージェントは **General Social Survey(GSS)を 85% の一致率**で再現。
  これは「**同じ本人が2週間後に自分の回答を再現する一致率**」を基準にした 85%(=人間の自己再現と
  ほぼ同等)。実験の複製(personality trait 予測・行動実験)でも同等。**デモグラフィック/ペルソナ接地の
  エージェントより 14–15 ポイント高精度**。人種・イデオロギー群をまたぐ**精度バイアスも低減**。
- **著者**: Park, Zou, Shaw, Hill, Cai, Morris, Willer, Liang, Bernstein(Stanford + Google DeepMind +
  Northwestern)。Stanford の "AI for Public Benefit Lab" が公開。
- **目的の最終形**: 「設計支援(2022)→ 認知再現(2023)→ **実在個人の忠実な proxy(2024)=予測・
  代替実験のインフラ**」。これが商用(Aaru / Synthetic Users)と地続きになった転換点。
- **本プロジェクトへの含意(重要)**: **インタビュー接地が +14–15pt** という事実は、本プロジェクトの
  ペルソナ生成(IPF×e-Stat + Verbalized Sampling)に対する**強い改善示唆**。ただし彼らは「実在個人の
  再現」を目的にするのに対し、**本プロジェクトは架空世界の閉性を重視**(実 API 不採用・R17 実名禁止)する
  ので、そのまま輸入はできない。§3.4・§5 で扱う。
- 出典: [Stanford AI4PB](https://ai4pb.stanford.edu/projects/generative-agent-simulations-of-1,000-people) /
  [arXiv 2411.10109(要確認)](https://arxiv.org/abs/2411.10109)

> **系譜のまとめ**: この分野の「社会を模擬する目的」は、**設計(prototype)→ 認知(believability)→
> 予測/代替(proxy)** と拡張してきた。本プロジェクトの `k*`(世界改変者の創発)は、この三系のどれとも
> 異なる第4の目的——**「創発そのものの相転移を測る科学装置」**——であり、系譜の空白を突いている。

---

## 2. 同種プロジェクトの網羅表

「LLM で社会がどう変化するかを観察する」プロジェクトを貪欲に収集。既存 `docs/lit/` にメモがあるものは
「既存」と付記。規模・検証・**社会実装**列を重視。

| 名称 | 年 | 規模 | 目的 / ドメイン | 検証 | 社会実装(想定/実施) | 出典 |
|---|---|---|---|---|---|---|
| **Social Simulacra / SimReddit**(Park) | 2022 | 小(コミュニティ単位) | オンラインコミュニティ**設計のプロトタイピング** | 設計者評価(有用性)+ 多世界生成 | プラットフォーム設計・モデレーション方針の事前検証 | [UIST22](https://dl.acm.org/doi/10.1145/3526113.3545616) |
| **Generative Agents / Smallville**(Park) | 2023 | 25体 | 個体認知の**believable 再現** | 人手 believability 評価・アブレーション | 認知アーキの基盤・ゲームNPC | [arXiv:2304.03442](https://ar5iv.labs.arxiv.org/html/2304.03442) |
| **Generative Agents of 1,000 People**(Park) | 2024 | 1,052(実在人物) | **実在個人の proxy**・態度/行動予測 | **GSS 85%**・実験複製・バイアス低減 | 人間実験の代替・世論/政策の事前予測 | [Stanford AI4PB](https://ai4pb.stanford.edu/projects/generative-agent-simulations-of-1,000-people) |
| **OASIS**(camel-ai)【既存】 | 2024 | **最大100万** | SNS の情報伝播・群分極・誤情報 | 実SNSのマクロ現象と定性照合 | プラットフォーム政策・誤情報対策の testbed | [arXiv:2411.11581](https://arxiv.org/abs/2411.11581) |
| **AgentSociety**(清華 FIB)【一部既存】 | 2025 | 1万+(500万相互作用) | 都市社会の**汎用ラボ**(心理/経済/都市) | 4実験を再現(分極・扇動拡散・**UBI**・**ハリケーン**) | **政策事前テスト**基盤(現 v2 はプラットフォーム化) | [arXiv:2502.08691](https://arxiv.org/abs/2502.08691) / [GitHub](https://github.com/tsinghua-fib-lab/agentsociety) |
| **SocioVerse**(復旦 DISC) | 2025 | エージェント + **実在1,000万人プール** | 「世界モデル」・政治/ニュース/経済 | **州別得票 >90%**・実データ4engine整合 | 世論/選挙予測・マクロ社会予測 | [arXiv:2504.10157](https://arxiv.org/abs/2504.10157) |
| **S3**(Gao et al., 清華) | 2023 | ネットワーク規模 | 感情/態度/行動の**伝播** | 実SNSデータと2水準で照合 | 世論・情報拡散の分析(ジェンダー/原発) | [arXiv:2307.14984](https://arxiv.org/abs/2307.14984) |
| **Project Sid / PIANO**(Altera)【既存】 | 2024 | 10〜1000+ | AI 文明の創発(役割/統治/宗教) | 創発を事後計測 | **デジタルヒューマン**製品・ゲーム | [arXiv:2411.00114](https://arxiv.org/abs/2411.00114) |
| **Concordia**(DeepMind)【既存】 | 2023 | 小(GM律速) | Game Master 型 生成 ABM ライブラリ | grounded 変数の検証・著者が妥当性課題を明記 | 協調AI研究・実験基盤 | [arXiv:2312.03664](https://arxiv.org/abs/2312.03664) |
| **TinyTroupe**(Microsoft) | 2024–25 | 小〜中(ペルソナ群) | **業務インサイト用ペルソナ模擬** | 事例ベース(定量検証は限定) | **市場調査・広告事前評価・ソフトウェアテスト** | [GitHub](https://github.com/microsoft/TinyTroupe) / [arXiv:2507.09788](https://arxiv.org/html/2507.09788v1) |
| **Sotopia**(CMU 他) | 2023–24 | 2体対話×90シナリオ | 社会知能の**評価ベンチマーク** | 人手+LLM 多次元採点 | 社会的に有能な agent の学習/評価 | [ICLR/Sotopia](https://www.emergentmind.com/topics/sotopia-social-interaction-benchmark) |
| **EconAgent**(清華, ACL 2024) | 2024 | 中 | **マクロ経済**(労働/消費/税) | 経済スタイライズド事実の再現 | 経済政策・課税の in-silico 実験 | [ACL 2024](https://aclanthology.org/2024.acl-long.829/) |
| **TwinMarket** | 2025 | スケーラブル | **金融市場**の行動/社会シム | バブル/景気後退の創発を再現 | 市場設計・システミックリスク | [arXiv:2502.01506](https://arxiv.org/abs/2502.01506) |
| **WarAgent**(AGI Research) | 2023–24 | 国=エージェント | 歴史的国際紛争(WWI/WWII/戦国) | 同盟形成・宣戦順序の macro 再現 | 外交・紛争解決の思考実験 | [arXiv:2311.17227](https://arxiv.org/abs/2311.17227) |
| **VacSim** | 2025 | 100体 | **公衆衛生政策**(ワクチン忌避) | 態度変化を政策シナリオ別に | ワクチン政策の事前評価 | [arXiv:2503.09639](https://arxiv.org/html/2503.09639v2) |
| **PolicySim**(Web Conf 2026) | 2026 | — | **プロアクティブな政策最適化** sandbox | A/B より前段でフィードバック最適化 | プラットフォーム介入政策の事前最適化 | [arXiv:2603.19649](https://arxiv.org/html/2603.19649) |
| **MOSAIC** | 2025 | 多体 | コンテンツ拡散/**規制**のモデル化 | 露出制御機構の実験 | モデレーション・推薦の事前設計 | [arXiv:2504.07830](https://arxiv.org/pdf/2504.07830) |
| **CitySim / OpenCity** | 2024–25 | 大規模 | **都市行動**シム(人流/活動) | 移動距離・施設利用で照合 | 都市計画・小売戦略・公共安全の what-if | [CitySim](https://arxiv.org/pdf/2506.21805) / [OpenCity](https://arxiv.org/html/2410.21286v1) |
| **Aaru**(商用) | 2024–26 | 数千〜約200万 | **選挙/消費者行動の予測** | 実選挙結果との誤差(後述) | **世論/選挙/市場予測**(EY/Accenture 等) | [Dealroom](https://app.dealroom.co/news/feed/ai-startup-aaru-hits-1b-valuation-simulating-voters-and-consumers-to-predict-real-world-behavior) |
| **Synthetic Users**(商用) | 2023–26 | 任意 | **UX/市場調査の synthetic 回答者** | (社内)実回答との整合を主張 | プロダクト/価格/コンセプトテスト | [syntheticusers.com](https://www.syntheticusers.com/) |
| **Remesh / Black Swan / Zappi 等**(商用) | 2024–26 | 任意 | 合成回答者・質的拡張 | 実サンプルとの併用が推奨 | 市場調査の高速化・低コスト化 | [Remesh](https://www.remesh.ai/resources/audience-data) |
| **PLATEAU**(国交省)【インフラ】 | 2020– | 250+都市 3D | **3D都市デジタルツイン**の整備・OSS化 | 実測地物ベース | 交通/人流シム・防災・都市管理・観光 | [mlit.go.jp/plateau](https://www.mlit.go.jp/plateau/) |
| **Fujitsu 社会デジタルツイン**(商用JP) | 2024–26 | — | 社会政策向けデジタルツイン・agentic AI | (公開限定) | 政策検討・パブコメ業務自動化(Takane) | [Fujitsu Uvance](https://global.fujitsu/ja-jp/uvance/data-ai-strategy/agentic-ai) |
| CAMEL / AgentVerse / RecAgent 等 | 2023–24 | 各種 | マルチエージェント基盤・推薦シム | 各論 | OASIS 等の土台・推薦システム評価 | [CAMEL](https://github.com/camel-ai) |

---

## 3. 重要クラスタの深掘り

### 3.1 中国「世界モデル(world model)」群 — スケールと実データ接地の最前線

清華 FIB Lab・復旦 DISC を中心に、「**実世界データに接地した大規模社会シミュレータ**」が急速に整備されて
いる。本プロジェクトの直接の競合/参照先であり、**社会実装の意図が最も明確**な群。

- **AgentSociety(清華, 2025)**: 1万+体・各体1日500相互作用。**Maslow 欲求階層**で行動駆動、環境は
  道路網+AOI/POI、Ray 分散。★ **4つの実社会実験を再現**——分極化・扇動的メッセージ拡散・**UBI(ユニバーサル
  ベーシックインカム)政策効果**・**ハリケーン等の外的ショック**。現行 `AgentSociety 2` は「社会科学研究と
  実験計画のためのプラットフォーム」を標榜し、**政策事前テスト基盤**として製品化に向かっている。
  → 本プロジェクトの制度DSL(fee/bonus/curfew/weekly_event)・災害/運休 scenario・行政B層は、
  **UBI/ハリケーン実験と同型の受け皿**を既に持つ。彼らが「政策ラボ」を掲げる事実は、渋谷シムの
  社会実装の裏付けになる。
- **SocioVerse(復旦, 2025)**: エージェントを**実在1,000万人プール**(社会メディアデータ)に整列。
  4engine(Social Environment / User / Scenario / Behavior)。**大統領選の州別得票を >90% 予測**
  (Qwen2.5-72B, DeepSeek-V3)。「world model」を明示的に名乗る。
  → 「**実在人物プールに整列**」は Park 2024(インタビュー接地)と同じ思想の**大規模版**。本プロジェクトの
  IPF×e-Stat ペルソナは「周辺統計整列」で、この中間。予測精度を狙うなら接地を深める余地(§5)。
- **OASIS(2024)【既存メモ有】**: SNS 特化・最大100万体。**RecSys を持つ**のが特徴で、誤情報・分極の
  **プラットフォーム設計 testbed**。本プロジェクトの `net/internet.py`(SNS/推薦/バイラル/炎上)が対応部。
- **S3(Gao, 2023)**: 感情/態度/行動の**3伝播**を測る初期作。ジェンダー差別・原発という**世論トピック**で検証。
- **EconAgent(ACL 2024)/ TwinMarket(2025)**: 経済ドメイン。EconAgent は労働・消費・課税のマクロ、
  TwinMarket は板寄せ(order-driven matching)で**バブル/景気後退の創発**。本プロジェクトの経済v0
  (賃金/消費/口座/税)・金融は無いが、**創発する集団現象を測る**姿勢は共通。

> **この群からの学び**: (1) 検証は「**実データのマクロ量との照合**」に収斂(得票率・移動半径・行動意図分布)。
> (2) スケールの誇示(1万〜1000万)が競争軸だが、**忠実度と両立していない**(RecSys 単純・herd 過剰)。
> (3) 「world model / 社会ラボ / 政策プラットフォーム」という**製品ナラティブ**が定着しつつある。
> → 本プロジェクトは規模では勝てないが、**物理接地の深さ(実地図・実ダイヤ・経路移動)と較正の厳密さ**で
> 差別化できる。彼らの多くは SNS テキスト空間で、**身体を持つ都市**を彼らは持たない。

### 3.2 商用 synthetic users / 予測市場 — 「シミュレーションの何にカネが払われているか」

ここが本調査の核心。**支払われているのは「シミュレーション」ではなく "what-if の答え"**。

- **Aaru(2024–26)**: 創業者 Ned Koh ら。約$88M 調達・**$1B(headline)評価**(Redpoint リード、要確認=
  headline valuation)。★ **survey の回答ではなく「行動アウトカム」で学習**するのが差別化。数千体(典型5,000)の
  エージェントに年齢・所得・郵便番号・性別を割り当て、**ネットを巡回して媒体接触(media diet)を模し、
  投票選好が変わる**。NY市長予備選を約200万人規模で模擬し**実結果と約2,000票差**。1回30秒〜1.5分・
  **従来調査の 1/10 未満のコスト**。顧客に **EY・Accenture・McDonald's・Bayer**。
  ★★ 創業者の営業ピッチが「**Do not trust us. Do not trust our model**(我々を信用するな)」——
  = **不確実性の明示を売りにする**という、方法論的にも示唆的な姿勢(§4 で再論)。
  出典: [Semafor](https://www.semafor.com/article/09/20/2024/ai-startup-aaru-uses-chatbots-instead-of-humans-for-political-polls) /
  [Fortune](https://fortune.com/2026/06/17/aaru-cofounder-ned-koh-ai-startup-sales-pitch-do-not-trust-us/)
- **Synthetic Users(2023–26)**: 「調査参加者のリクルート代行を、より速く」。OCEAN(ビッグ5)でペルソナを
  作り、面接文脈を保持。**1面接あたり単価が従来($100+/人)より桁違いに安い**——「従来4テストの価格で
  40テスト」と訴求。プロダクト/価格/コンセプトテストが用途。
- **Microsoft TinyTroupe(2024–25, OSS)**: `TinyPerson`(ペルソナ agent)+ `TinyWorld`(環境)。
  **仮想フォーカスグループ・広告の事前評価(Bing Ads をオフラインで評価)・検索/チャットボットのテスト入力**を
  標榜。OSS で無償——「道具を配って業務に浸透させる」戦略。
- **市場規模**: synthetic data 生成市場は**$267M(2023)→ $4.6B(2032予測)**(要確認=二次ソース)。
  Remesh・Black Swan Data・Zappi 等が「合成回答者+実サンプル併用」で参入。
- **批判(NN/g・NIQ 等)**: 「平均ペルソナ」への収束で**異質性・少数派・非西洋市場を系統的に誤représentation**。
  NN/g は「**単独では研究の代替にするな、実データと併用せよ**」と警告。→ 妥当性は未解決のまま商用化が先行。

> **カネの分析(重要)**: 4社に共通する価値は「**現実に金・時間・倫理コストを払う前の、安く速く安全な
> what-if の答え**」。内訳は (1) **リスク低減**(広告/製品/選挙/政策の賭けを打つ前に外す)、(2) **速度と
> コスト**(週→秒、1/10)、(3) **募集不能な母集団へのアクセス**(Social Simulacra の原点)、
> (4) **反実仮想**(UBI・ハリケーン・封鎖は現実に走らせられない)。**Q&A 型の合成回答者は "態度"は
> 出せても "空間・時間・政策の物理的帰結" は出せない**——ここが本プロジェクト(身体を持つ渋谷+較正+
> 決定論)の商用的な空隙になりうる(§5.3)。

### 3.3 日本・都市デジタルツイン — PLATEAU 接続とローカルの社会実装

- **PLATEAU(国交省)**: 全国250+都市の**3D都市モデルをオープンデータ化**する「日本のデジタルツイン」国家
  プロジェクト。用途として **交通シミュレーション・人流・防災・エリアマネジメント・観光**を掲げ、**ユースケース
  創出を明示的に募集**している。★ 本プロジェクトは既に **PLATEAU 渋谷2025年度を UE 取込済み**
  (devlog E5)であり、**PLATEAU の幾何デジタルツインに "行動レイヤー" を載せる**という座組みが自然に成立する。
- **Fujitsu 社会デジタルツイン / agentic AI(Watomo)・LLM Takane**: 社会政策向けデジタルツインと、
  **中央省庁でのパブコメ業務自動化(意見分類・要約)**の実証(2025)。→ 日本の大手 SIer が「政策 × 生成AI」に
  資源投下している事実は、渋谷シムの政策ユースケースに追い風。
- **群衆/避難シミュレーション(渋谷ハロウィン文脈)**: 渋谷のハロウィン人出はピーク時**約4万人(2019)**、
  当局は最大6万人を警戒し、**警備員125名+区職員90名**を投入。専門家は「先の混雑を知らせる電子標識」を提言。
  既存の MassMotion 等は**物理(流体/力学)ベースで意思決定の異質性を持たない**。→ **LLM 駆動で "誰が
  『来ないで』を無視するか" を含む群衆シム**は空隙。本プロジェクトは実地図+ハロウィン群集 phase
  (`annual.py`)+封鎖 scenario を既に持ち、**この用途に最短距離**。

### 3.4 方法論・妥当性フレームワーク群(2025–2026)— 本分野の「作法」が急速に標準化

本プロジェクトの `docs/lit/measurement__validation-overview.md` は 2025 前半までを押さえるが、
**2025 後半〜2026 に妥当性の批判的フレームワークが一気に出た**。ここは未カバーで、かつ本プロジェクトの
売りに直結する。

- **PIMMUR 原則(2025)**: LLM 社会シムの妥当性の**初の体系的基準**。**P**rofile / **I**nteraction /
  **M**emory(ミクロ)+ **M**inimal-Control / **U**nawareness / **R**ealism(マクロ)。★ 代表39論文の
  **89.7% が1つ以上の原則に違反**。原則を強制すると**既報の社会現象の多くが消える**。
  さらに **GPT-4/Qwen3 は53%のケースで "背後の実験を推測"**(=demand characteristics / Unawareness 違反)。
  出典: [arXiv:2509.18052](https://arxiv.org/pdf/2509.18052)
- **The Silicon Society Cookbook(2026)**: 設計選択の系統分析。★ **ベースLLMの選択が結果に最も効く変数**。
  異質性は**共有ベース + 多数の LoRA アダプタ(多アダプタ構成)**で効率的に実現——「平均ペルソナ収束」の
  技術的打開策。出典: [arXiv:2605.00197](https://arxiv.org/pdf/2605.00197)
- **"Validation is the central challenge"(Springer AI Review 2025)** / **operational validation の複製
  (arXiv:2508.21740, Reddit 型フォーラム)** / **"LLM-Based Social Simulations Require a Boundary"
  (2506.19806)** / **EASE 設定管理で再現性(2605.30258)** / **"Stop Drawing Scientific Claims … Without
  Robustness Audits"(2605.18890)**。共通の指摘: (a) LLM は**人間と異質な機構で人間らしい答え**に至りうる
  =因果研究の代理として危険、(b) **平均ペルソナ**が異質性を潰す、(c) 西洋データ偏りで**非西洋世論を歪める**、
  (d) **再現性(seed/config/prompt版)の固定**が中心論点。

> **この群の含意(本プロジェクトの通信簿)**: 分野が今まさに「作法」を作っている最中で、**本プロジェクトの
> 既存手法の多くが先取り**している——決定論リプレイ+応答キャッシュ(再現性)、no-fingerprint 契約
> (Minimal-Control / Unawareness)、compute-matched null(交絡除去)、現実バンド較正(Realism)。
> **PIMMUR 準拠表を明示的に出すだけで、89.7% が落第する土俵で "受かる" ことを示せる**(§5.1)。

---

## 4. 方法論的知見の抽出 — 「借りるべきもの / 先行しているもの」判定

本プロジェクトの既存手法(現実バンド較正・R²(k)・mock 対照・決定論リプレイ・LOD・EWS・
finite-size scaling・別ファミリ LLM-judge・no-fingerprint)と照合する。

### (a) validation の作法

| 論点 | 先行研究の水準 | 本プロジェクト | 判定 |
|---|---|---|---|
| マクロ量照合 | 得票率・移動半径・訪問地点数(AgentSociety/SocioVerse) | 現実バンド較正(睡眠/労働/家賃/貯蓄/事件率)を**一次統計出典付き**で | **先行**(照合の一次接地が厚い) |
| 既知結果の再現(sanity) | Turing Experiments(Ultimatum/Milgram) | Centola tipping・naming game の再現を**計画済み・未実行** | 借りる(**実行して calibrate**) |
| 再現性 | EASE/PIMMUR が「危機」と指摘 | 決定論 bit 一致 + 応答キャッシュ + config 保存 | **大きく先行** |
| LLM-judge 循環 | 自己favoring 警告 | 別ファミリ judge + κ≥0.7 + 行動指標 | **先行** |
| PIMMUR 準拠 | 89.7% が違反 | 未自己監査(だが機構は多く準拠) | 借りる(**準拠表を作る**) |

### (b) 創発の測定法

- 先行の大半は「**創発を定性記述**」(役割分化・宗教・炎上)。定量は伝播カスケード・分極指標にとどまる。
- 本プロジェクトの **R²(k) の低下 + seed 発散 + EWS(分散/AC1↑)+ finite-size scaling** の**多測度三角測量**は、
  「**創発の相転移点 k\* を測る**」という点で**明確に先行**(誰も k\* を測っていない)。
- ★ ただし PIMMUR/robustness 群の警告「**現象は原則違反のアーティファクトかもしれない**」は本プロジェクトにも
  刺さる。→ null/sham/compute-matched 対照は既にこの防御(先行)だが、**"k\* は本物か" を robustness audit
  形式で自己反証する節**を分析に足すと盤石(借りる=作法の輸入)。

### (c) 較正の作法

- 先行: SocioVerse は「実在プール整列」、Aaru は「行動アウトカムで学習」。**態度ではなく行動で接地**する
  流れが強まっている。→ 本プロジェクトの較正が**行動統計(訪問・移動・消費・事件)ベース**である点は
  この潮流と**整合**し、Aaru 型の「行動接地」を**既に実践**(先行)。
- 借りるべき: Park 2024 の **インタビュー接地(+14–15pt)**。周辺統計 IPF より個体接地が精度を上げるのは
  一般則。ただし架空世界の閉性と両立させる工夫が要る(§5.1)。

### (d) 人間実験との対応づけ(倫理含む)

- Aaru の「Do not trust us」、NN/g の「単独で使うな」= **合成結果を人間の代替として過信しない**という倫理
  規範が業界内で形成中。本プロジェクトの `ETHICS.md`・「造語を促進しない/自然観察」・R4 客観カウントは
  この規範と整合。
- 借りる: **人間データとの対応づけを "できる範囲で" 明示**(GSS 85% のような "何に対して何%一致か" の
  基準線)。本プロジェクトは架空世界ゆえ直接の人間照合は限定的だが、**較正バンドが "人間の何に対応するか" を
  明記**すると訴求力が上がる。

### (e) スケールと忠実度のトレードオフ

- 先行の教訓: 100万体(OASIS)は「小モデル1呼/step + 巨大GPU + 確率活性化」の産物で、**中間ユーザ表現が
  貧弱・herd 過剰**。スケールと忠実度は明確にトレードオフ。
- 本プロジェクトは **~1k–10k + LOD 1/12 + リッチ認知**で「**忠実度側に振る**」設計。これは正しい選択で、
  上記妥当性批判(平均ペルソナ・アーティファクト)への耐性が高い。Silicon Society Cookbook の
  「**ベースモデル選択が最重要変数**」は、本プロジェクトの「**モデル選択=実験変数 / RLHF 対照**」の方針を
  **外部から追認**している。

---

## 5. 本プロジェクトへのヒント総括

3分類(研究面 / デモ・訴求面 / 社会実装面)で、優先度(★★★=最優先)つきの私見。

### 5.1 研究面(k\* ・較正・データパイプラインに直接効く)

- ★★★ **PIMMUR 準拠表を分析成果物に追加**。39論文の89.7%が落第する6原則(Profile/Interaction/Memory/
  Minimal-Control/Unawareness/Realism)に対し、本プロジェクトがどう各原則を満たすかを1枚の表で示す。
  ほぼコード変更なしで「妥当性の土俵で受かる」ことを可視化でき、**論文・本選の両方で効く**。既存の
  no-fingerprint/決定論/較正がそのまま各原則の証拠になる。
- ★★★ **k\* の robustness audit を自己適用**。「k\* 信号は原則違反や compute 交絡のアーティファクトでないか」を
  null/sham/compute-matched に加えて **"実験を推測されていないか(Unawareness)"** の観点で点検する節を足す。
  2605.18890 の作法を輸入。これは詰まり(k\* 確定の低確率)への保険にもなる。
- ★★ **既知結果の較正を実行**(Centola tipping ~25% / naming game 収束)。計画済みだが未実行。通れば
  「新規 k\* を信じてよい土台」になる(Turing Experiments 型 sanity check)。
- ★★ **インタビュー接地の部分導入を検討**(Park 2024, +14–15pt)。全ペルソナは無理でも、**検証用サブ集団**を
  半構造化インタビュー風テキストで接地し、IPF ペルソナとの behavior 差を測れば「接地深度 → 忠実度」の
  内部エビデンスになる。架空世界の閉性は「実在人物でなく合成インタビュー」で保てる。
- ★ **多アダプタ LoRA で異質性を強化**(Silicon Society Cookbook)。本プロジェクトの最大の詰まり
  「efficacy 天井 / grievance 床への飽和 → 個体差消失」(devlog E7)への**技術的打開策の候補**。
  共有ベース + 個性 LoRA で平均ペルソナ収束を割る。ただし決定論・キャッシュ整合との両立検証が要る(実装判断は Fable)。

### 5.2 デモ・訴求面(本選で何を見せると刺さるか)

- ★★★ **"身体を持つ都市" を主役に**。競合(OASIS/SocioVerse/S3)は SNS テキスト空間、Sid は Minecraft、
  Concordia は抽象。本プロジェクトの **実渋谷地図 + 実ダイヤ + 経路移動(テレポート無し)+ 較正された日常**は
  **唯一無二の絵**。ビューア(地図)+ dashboard(X風SNS/LINE風DM/SERP/論文風グラフ)をそのまま前面に。
- ★★★ **ライブ政策 what-if デモ**。dashboard から scenario/制度DSL(fee/curfew/weekly_event/封鎖/ハロウィン
  群集)を注入 → 伝播チャネル(face/sns/news/search/dm)を通じた波及と **k\* 信号 / 較正バンド**の変化を
  その場で見せる。これは AgentSociety(UBI/ハリケーン)・PolicySim・CitySim が売る価値と**同型**だが、
  **実在の街+較正表**を持つのは本プロジェクトだけ。
- ★★ **決定論 = 信頼の演出**。Aaru が "Do not trust us" と言わざるを得ない中で、本プロジェクトは
  「**同じ街を bit 単位で再生できる**」を見せられる。再現性は妥当性批判への直接の回答であり、審査員に効く。
- ★★ **自然な語彙創発の物語**(シブヤレンズ伝播1,540回→79/80採用, devlog E5)。「促進せず観察した」
  文化創発は Sid の宗教創発に対抗できる**創発ストーリー**。
- ★ **現実バンド較正表をそのまま提示**(calibrate_report)。「睡眠7.33h・労働7.07h・家賃比0.28…が現実と
  一致」を見せると、競合が持たない**較正の厳密さ**が一目で伝わる。

### 5.3 社会実装面(渋谷シムが売り物になる用途 / EnvPack 他都市展開の市場性)

- ★★★ **PLATEAU の "行動レイヤー" として位置づける**。国交省 PLATEAU は**幾何のデジタルツインで、
  ユースケースを募集中**。本プロジェクトは PLATEAU 渋谷を取込済みで、**そこに較正済みの人間行動を載せる**
  という座組みが最も自然かつ差別化が明確。「PLATEAU に足りない "人がどう動き・どう反応するか" を供給する」は
  国家プロジェクトへの明快な提案になる。**最有望の社会実装経路**。
- ★★★ **政策事前テスト(自治体・行政向け)**。制度DSL・決定論投票・審議/パブコメ段階・行政B層
  (区/都/国・住民税/消費税/区予算)を既に持ち、**AgentSociety の UBI/ハリケーン実験と同型の受け皿**が
  実在の渋谷の財政値で動く。渋谷区/東京都/国交省・大手SIer(Fujitsu が既に "政策×生成AI" に投資)への
  提案余地。**"渋谷パートナーシップ条例" 型の条例事前評価**は具体的な入口。
- ★★ **群衆・イベント安全(ハロウィン/年末/災害避難)**。実地図+群集 phase+封鎖 scenario+個体の
  意思決定異質性(LLM)は、物理オンリーの群衆シム(MassMotion 等)にない付加価値。渋谷ハロウィンは
  毎年4–6万人・区が警備に実支出する**具体的で切実な地元課題**=刺さりやすい。
- ★★ **商業・小売の what-if**(commerce.py: 営業時間/動的価格/在庫 + 実POI + 人流)。CitySim/OpenCity が
  掲げる小売戦略・出店の in-silico 検証。「この通りに店を出したら人流はどう変わるか」は渋谷の事業者に直接価値。
  既存の商業データ提案(devlog E9/E10)の延長。
- ★ **日本市場向け synthetic users(市場調査)**。IPF×e-Stat ペルソナ + 較正行動は、Aaru/Synthetic Users/
  TinyTroupe 市場($267M→$4.6B 予測)の**日本語・行動接地版**になりうる。差別化は「Q&A の態度でなく
  **物理世界での行動**を返す」点。ただし NN/g・PIMMUR の妥当性批判(平均ペルソナ・非西洋偏り)を正面から
  扱う必要があり、**"単独の代替でなく実データ併用" を前提に**。優先度は上記より下(妥当性リスクが商用で顕在化)。
- ★★ **EnvPack = スケールする事業形態**。`docs/research/framework-architecture.md` の通り core/env 分離は
  8割到達。**「任意都市を OSM+PLATEAU+GTFS+e-Stat から較正済み行動ツインに落とす」パイプライン**が
  製品の芯。ビジネス形態は「研究ツール(OSS)→ 自治体/事業者向けコンサル → 都市パック SaaS」の順で
  段階展開が現実的(TinyTroupe=OSS浸透、AgentSociety=プラットフォーム、Aaru=予測サービスの各型を参照)。

---

## 6. 出典(アクセス日 2026-07-11・一次ソース優先。未確認は本文に明記)

**Park の系譜**
- Social Simulacra (UIST 2022): https://dl.acm.org/doi/10.1145/3526113.3545616 / PDF https://hci.stanford.edu/publications/2022/Park_SocialSimulacra_UIST22.pdf
- Generative Agents (2023): https://ar5iv.labs.arxiv.org/html/2304.03442
- Generative Agent Simulations of 1,000 People (2024): https://ai4pb.stanford.edu/projects/generative-agent-simulations-of-1,000-people / arXiv 2411.10109(要確認)

**大規模・世界モデル群**
- OASIS: https://arxiv.org/abs/2411.11581
- AgentSociety: https://arxiv.org/abs/2502.08691 / https://github.com/tsinghua-fib-lab/agentsociety
- SocioVerse: https://arxiv.org/abs/2504.10157 / https://github.com/FudanDISC/SocioVerse
- S3: https://arxiv.org/abs/2307.14984
- EconAgent (ACL 2024): https://aclanthology.org/2024.acl-long.829/
- TwinMarket: https://arxiv.org/abs/2502.01506
- Project Sid / PIANO: https://arxiv.org/abs/2411.00114 / https://github.com/altera-al/project-sid
- Concordia: https://arxiv.org/abs/2312.03664

**評価・ドメイン特化**
- Sotopia: https://www.emergentmind.com/topics/sotopia-social-interaction-benchmark
- WarAgent: https://arxiv.org/abs/2311.17227 / https://github.com/agiresearch/WarAgent
- VacSim(ワクチン忌避): https://arxiv.org/html/2503.09639v2
- PolicySim(政策最適化 sandbox): https://arxiv.org/html/2603.19649
- MOSAIC(コンテンツ拡散/規制): https://arxiv.org/pdf/2504.07830
- CitySim: https://arxiv.org/pdf/2506.21805 / OpenCity: https://arxiv.org/html/2410.21286v1
- CityBench/USTBench(都市ベンチ): https://arxiv.org/pdf/2505.17572 / UGI レビュー https://arxiv.org/pdf/2402.01749

**商用 synthetic users / 予測**
- TinyTroupe(Microsoft): https://github.com/microsoft/TinyTroupe / https://arxiv.org/html/2507.09788v1
- Synthetic Users: https://www.syntheticusers.com/
- Aaru: https://app.dealroom.co/news/feed/ai-startup-aaru-hits-1b-valuation-simulating-voters-and-consumers-to-predict-real-world-behavior / https://www.semafor.com/article/09/20/2024/ai-startup-aaru-uses-chatbots-instead-of-humans-for-political-polls / https://fortune.com/2026/06/17/aaru-cofounder-ned-koh-ai-startup-sales-pitch-do-not-trust-us/
- Remesh(合成回答者): https://www.remesh.ai/resources/audience-data
- NN/g(synthetic users への警告): https://www.nngroup.com/articles/synthetic-users/
- 市場規模($267M→$4.6B, 要確認=二次): https://developmentcorporate.com/saas/synthetic-responses-market-research-2025/

**日本・デジタルツイン**
- PLATEAU(国交省): https://www.mlit.go.jp/plateau/ / G空間 https://front.geospatial.jp/plateau_portal_site/
- Fujitsu agentic AI / 社会デジタルツイン: https://global.fujitsu/ja-jp/uvance/data-ai-strategy/agentic-ai
- 渋谷ハロウィン群衆対策: https://www.cbsnews.com/news/spooked-by-halloween-mayhem-tokyos-famous-shibuya-district-tells-revelers-please-do-not-come/

**方法論・妥当性フレームワーク(2025–2026)**
- PIMMUR 原則: https://arxiv.org/pdf/2509.18052
- Silicon Society Cookbook(設計空間): https://arxiv.org/pdf/2605.00197
- Validation is the central challenge (Springer AI Review 2025): https://link.springer.com/article/10.1007/s10462-025-11412-6
- Operational validation の複製(Reddit型): https://arxiv.org/pdf/2508.21740
- LLM-Based Social Simulations Require a Boundary: https://arxiv.org/pdf/2506.19806
- EASE(再現可能な設定管理): https://arxiv.org/pdf/2605.30258
- Robustness Audits(2605.18890): https://arxiv.org/pdf/2605.18890
- LLM×ABSS レビュー(JASSS 投稿): https://arxiv.org/html/2507.19364v1

**本プロジェクト内部参照**
- 既存メモ: `docs/lit/mas__yang2024_oasis.md` / `mas__concordia2023_deepmind.md` / `mas__survey2024_llm-abm-survey.md` / `measurement__validation-overview.md`
- 既存調査: `docs/research/framework-architecture.md`(core/env 分離)/ `data-pipeline-lit.md`(記録層・EWS)
- 開発ログ: `docs/log/devlog-compressed.md`(k*・較正・制度DSL・PLATEAU取込・シブヤレンズ伝播 等)
