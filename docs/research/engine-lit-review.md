# エンジン群アーキテクチャ文献レビュー

作成: 2026-07-14 / リサーチ担当(Opus実行役・コード変更なし・読み取りとWeb調査のみ)
Web出典のアクセス日はすべて 2026-07-14。一次ソース優先。一次確認が取れない値は本文で「(未確認)」と明記した。

## 本書のねらいと結論(先出し)

ユーザー仮説:**人の行動 = 「知覚 → 思考 → 意思決定 → 行動」の4層**。LLM は思考・意思決定が得意なので、
(a) 環境が情報を与える**知覚モジュール**と、(b) 思考から具体的行動を取り出す**行動抽出モジュール**を
LLM 本体から分離するのが現在のトレンドに合う——を文献で検証する。

**検証結果: 仮説はトレンドに強く合致する。** 主要な LLM 社会シミュは例外なく「LLM=思考/意思決定」を
中核に置き、その両側に「環境→観測(知覚)を配信する層」と「LLM 出力→検証済みの具体的行動へ落とす層」を
明示的に分離している。特に:

- **CoALA**(認知アーキテクチャの分類枠)は、エージェントを **記憶モジュール / 構造化された行動空間(action space)/
  意思決定手続き** の3要素に形式化し、「意思決定(思考)」と「行動空間(=環境接地と行動抽出)」を別物として扱う。
  ユーザーの4層はこの枠にほぼ一対一で写像できる。
- **Concordia**(DeepMind)の Game Master は「観測を配信(知覚)」と「自然言語の行動宣言を物理的妥当性で検証して
  具体的効果に翻訳(行動抽出+接地)」を GM 側に集約し、Agent 側は思考・意思決定に専念する。
- **PIANO**(Project Sid)は認知・記憶・計画・**高速行動(motor)**・発話を**並列モジュール化**し、
  遅い熟考と速い行動実行を分離する。
- **MobiVerse**は「非LLMの軽量ルーチン生成器 + LLM修正器 + シミュレーション環境」の3分割で、
  **日課(routine)は安価に生成し、LLM は適応・逸脱の判断にだけ使う**——本仮説の直接的な実証例。

**SUMO 導入の可否所見(先出し)**: SUMO は「車両・道路網・信号・鉄道級のダイヤ的移動」には有力だが、
**歩行者(特に渋谷スクランブルの高密度・双方向流)には不向き**(歩道・横断歩道に拘束され、逸脱・佇立を表現しにくい)。
LLM エージェント本体を SUMO に載せるのではなく、**「LLM が目的地・意図を決め、専用の群集/経路エンジンが物理移動を解く」**
分業が正しい。渋谷スクランブルの歩行忠実度が必要なら Social Force 系(PySocialForce/pedsim)か学習型
(ShibuyaSocial: LSTM+attention)を別部品として差すのが筋。SUMO は「必要なら車両・鉄道側の背景交通」に限定採用が妥当。

関連既存調査: 場所非依存の基盤/環境分離は `docs/research/framework-architecture.md` に詳しい(本書は重複を避け、
**エンジン層構成・行動抽出技術・外部エンジンの部品採否**に焦点を絞る)。

---

## §1. 先行アーキテクチャ比較表

「知覚(環境→観測)」「思考/意思決定(LLM)」「行動抽出(思考→具体的行動)」の3点で各システムを分解。
規模・行動取り出し方式・公開実装/ライセンスを併記する。

| システム | 知覚(環境→観測)の担い手 | 思考/意思決定の分割 | 行動抽出(思考→具体的行動)の方式 | 規模 | 公開/ライセンス |
|---|---|---|---|---|---|
| **Generative Agents** (Park et al. 2023, Stanford) | 環境ツリー(世界→エリア→物)の可視範囲を観測として記憶へ push | **Memory Stream / Reflection / Planning** の3部品。観測→反省→計画で人格が創発 | 自由記述の計画・発話を、環境の対象(オブジェクト/場所)へ写像。反省は「質問→高次洞察」の連鎖生成 | 25体(Smallville) | Apache-2.0(`joonspk-research/generative_agents`)|
| **AgentSociety** (Tsinghua FIB Lab 2025) | **Environment 層**が都市空間(道路網 + AOI/POI)・社会・経済を保持し、センシング/相互作用/メッセージを仲介 | Agent が **記憶・構造化ゴール集合・感情・行動プランナ**を持つ。Maslow 欲求段階・計画的行動理論(TPB)で明示モデル化。行動プランナは CoT で決定 | **Tool 層**が LLM 応答の**JSON/辞書パース・整形・結果解析**を担当(=行動抽出の専任層)。ゴールは外生ショックで進化 | 数千〜1万体級と報告(東京での実験は1,000体・GPT-4o-mini)(1万体は未確認) | Apache-2.0(`packages/agentsociety/commercial` を除く)|
| **OASIS** (CAMEL-AI 2024) | 環境サーバが**動的な SNS 状態**(ソーシャルグラフ/コンテンツ)+**推薦システム**(興味ベース/hot-score)で「何が見えるか」を制御 | LLM エージェント + ルールベースを併用。個々の判断は LLM、大規模挙動はルールで補完 | **21種の定義済み行動空間**(follow/comment/repost 等)へ落とす=構造化された行動集合から選択(function-calling 的) | 最大 **100万体** | Apache-2.0(`camel-ai/oasis`)|
| **Concordia** (Google DeepMind 2023) | **Game Master(GM)**が observation を各プレイヤに配信。`partial_state(player)` で「その人に見える範囲」だけ露出 | Agent = 再利用可能な **Component 群**(identity/plans/observations/physiological 等、各NL状態)。認知は March & Olsen「状況/自分は何者か/そういう者はどう振る舞うか」= **非最大化**(報酬最大化でない) | GM が**自然言語の行動宣言を物理的/社会的妥当性で検証**し、grounded world state(通貨/投票/在庫)へ翻訳。不正行動は却下。`ActionSpec` で行動要求を規定 | 小規模(数〜数十体。大規模化の記述なし=**スケール非対応**) | Apache-2.0(`google-deepmind/concordia`)|
| **Project Sid / PIANO** (Altera 2024) | 環境=Minecraft。観測は各並列モジュールへ配信(空間推論は弱点と自認) | **PIANO**(Parallel Information Aggregation via Neural Orchestration)= 認知・記憶処理・計画・**高速行動(motor)**・発話・社会認識を**異なる時間尺度で並列**に走らせ、中央意思決定が統合 | 高速行動モジュールが**遅い熟考と分離**され即応。中央意思決定の出力を各出力ストリームへ一貫性を保って配分 | 50〜1000体(Minecraft) | 部分公開(`altera-al/project-sid`。行動系の一部のみ・全再現コードでない。ライセンスは未確認) |
| **CoALA** (Sumers et al. 2023) — *分類枠であり実装でない* | 外部環境の grounding(観測)を「外部行動」の対と位置づけ | **記憶モジュール**(working/long-term/procedural)+ **一般化された意思決定手続き**(提案→評価→選択) | **構造化された行動空間**を「内部行動(推論/検索/学習)」と「外部行動(接地)」に二分。SOAR/ACT-R の系譜 | 該当なし(理論枠) | 論文のみ(arXiv 2309.02427) |
| **(古典) SOAR / ACT-R** | 知覚(perception)モジュールが独立 | 宣言的長期記憶 + 手続き的長期記憶 + 作業記憶 + **行動選択(action selection)**。ACT-R は逐次(ボトルネック)、SOAR は並列 | 行動選択→行動(action)モジュール。プロダクション規則で「状態→操作」を適用 | — | 各種(研究用実装) |

### 4層仮説へのマッピング(要点)

- ユーザーの「知覚 / 思考 / 意思決定 / 行動」は、CoALA の「(記憶で文脈化された観測)/ 意思決定手続き(提案→評価→
  選択)/ 構造化行動空間(外部行動=接地)」にほぼ一致。**「思考・意思決定=LLM」「知覚=環境が配信」「行動抽出=
  構造化行動空間への写像」という分業は、CoALA・Concordia・AgentSociety・PIANO で共通の設計軸**である。
- とくに **Concordia の GM = 「知覚配信 + 行動抽出/接地」を一手に引き受ける環境オブジェクト**という抽象が、
  本プロジェクトの「環境が情報を与えるモジュール」と「思考から行動を取り出すモジュール」を1つの環境側責務として
  実装する設計の直接の下敷きになる。
- **AgentSociety の Tool 層**(JSON パース・整形・結果解析)は、まさに「行動抽出モジュール」を独立層として切り出した
  実例であり、命名・責務の借用に値する。

---

## §2. action extraction(思考→行動の取り出し)技術メモ

「LLM の思考出力を、シミュレータが実行できる具体的行動へ確実に落とす」技術の選択肢を整理する。

### 2-1. 構造化出力(制約付きデコード)

- **仕組み**: JSON Schema / 正規表現 / 文脈自由文法でデコードを制約し、出力を必ずパース可能な形にする
  (guided/constrained/structured decoding)。
- **vLLM**: `guided_json`(JSON Schema)/ `guided_choice`(選択肢のいずれか)/ `guided_regex` / `guided_grammar`(CFG)を
  サポート。バックエンドは **outlines / lm-format-enforcer / XGrammar**。**XGrammar が現行の既定**で、
  プッシュダウンオートマトンでバッチ制約デコードを行い、文法を再利用(キャッシュ)すると出力トークンあたりのオーバヘッドが小さい。
- **Ollama**: `format` パラメータに JSON Schema を渡すと**制約付きデコード**が効く。ローカル実測で
  format 無し 31.84s → 有り 4.99s(**約6.4倍高速**)の報告。「文法制約が効くと小型モデルでも構文は完璧になり、
  差は**内容の正確さ**に移る」。`temperature=0`(決定論)推奨。Ollama 0.3.0 以降。
- **含意**: **行動抽出モジュールを「制約付きデコードの一段」として実装すれば、構文的に必ず実行可能な行動が得られる**。
  これはユーザー仮説の「行動抽出の分離」を最も安価に実現する手段。

### 2-2. 関数呼び出し(function calling)vs 自由記述からの抽出(ReAct)

- **function calling** = 「構造化出力にトレンチコートを着せたもの」(モデルが関数名+引数の JSON を吐く)。
  中間の思考(Thought)は隠れ、決定論的・高精度。**OASIS の21行動**や AgentSociety の行動プランナはこの系譜。
- **ReAct** = Thought→Action→Observation を明示ループ。**思考が可視化され柔軟**だが、行動抽出は別途パースが要る。
- **ハイブリッド**(現行の主流): ReAct 流に自由推論で計画→最後に function call / 制約付き JSON で確定。
  **「思考は自由記述、確定行動だけ構造化」**が、思考の豊かさと実行可能性を両立する定石。
- **本仮説への含意**: 「思考(自由記述・LLM の強み)」と「行動抽出(構造化・確定)」を**別ステップ**にするのは、
  ReAct+function calling ハイブリッドとして既に標準化している。ユーザー仮説はこの標準に一致。

### 2-3. 小型ローカルモデル(4B級)での JSON 遵守の実情

複数ベンチマークの報告(ドメイン差あり・数値は各ベンチの条件依存):

- あるベンチ(臨床ノート抽出)では **14B が 90.3% パース可能、8B 82.6%、3–4B 80.9%**。抽出関連エラーは
  14B 2.4% に対し 8B 21.0% / 3–4B 19.0% と**小型で急増**。
- モデル別: **Llama 3.2 3B は JSON パース率 47.8–56.5% にとどまり、3B規模は構造化出力に不十分**。
  **Gemma 3 4B は JSON パース率100%**(ただしスキーマ遵守は Q4_K_M で 87% に低下)。SmolLM2 1.7B は不安定。
- **ネスト penalty**: フラットなスキーマでは非遵守 2–3% だが、**JSON Schema の `$defs`(参照)が入ると非遵守が
  68–69% に跳ね上がる**という報告。
- **制約付きデコードの「税」**: 文法制約で構文妥当性は保証できるが、**妥当性↔内容正確さのトレードオフ
  (constraint tax)**が観測される(構文は通るが中身が劣化しうる)。
- **実務結論(本プロジェクト向け)**:
  1. 4B級ローカルなら **vLLM `guided_json` / Ollama `format` の制約付きデコードを必須化**して構文失敗をゼロに寄せる。
  2. **スキーマはフラットに**(`$defs`・深いネスト・巨大 enum を避ける)。行動空間は OASIS 流に**少数の定義済み行動**へ。
  3. function/tool 数は **3–5 に絞る**(小型は「整形」より「正しいツール選択」で失敗しやすい)。
  4. 残余リスクは「パース失敗」から「意味的正しさ」へ移るので、検証は **Concordia の GM 流の妥当性チェック**
     (存在しない対象・不能な行動を却下)で受ける。

### 2-4. 「思考が明示的でない場合」の行動取り出し

- **2コール分割**が定番: Concordia は「行動サンプリング1コール + component 更新1コール」、
  Generative Agents も 2 LLM 呼。**思考を出させる呼び出しと、行動を確定させる呼び出しを分ける**。
- 思考を明示させない場合は、**自由応答→別パスで構造化抽出**(抽出専用の軽量呼び出し or 制約付き再デコード)。
  AgentSociety の **Tool 層**がこの「応答→JSON/辞書へ解析」を専任化した実例。
- いずれも**「行動抽出は LLM 本体と別モジュール」**という本仮説の方向。

---

## §3. 部品として使える外部エンジン(SUMO 中心・結合コスト評価つき)

判定軸: 「何が得意か / LLM エージェントとの結合コスト / ライセンス / 渋谷(歩行者・スクランブル)への効き」。

### 3-1. 交通・都市モビリティ

| エンジン | 得意 | LLM 結合 | 結合コスト | ライセンス | 渋谷への効き |
|---|---|---|---|---|---|
| **SUMO** (Eclipse) | 微視的**車両**交通・道路網・信号・intermodal。大規模道路網 | **TraCI**(純Python API・ソケット経由・オンライン制御)/ **libsumo**(ライブラリ埋込・ソケット無し=**高速**だが単一クライアント・柔軟性減)。LLM連携先例: AgentSUMO / SUMO-MCP / OpenAI Agents SDK+MCP+TraCI digital twin / MobiVerse | **中〜高**: TraCI はステップ毎のPython往復がスケール時のボトルネック。libsumo で軽減可 | **EPL 2.0**(+副次GPL)。EPL は弱いコピーレフトで**自社コードを閉じたまま結合可** | **車両・背景交通は可**。**歩行者は striping モデルで歩道/横断歩道に拘束**され、逸脱・佇立・高密度双方向流を表現しにくい=**スクランブルには不向き** |
| **MATSim** | **活動ベース**需要・日次アクティビティ計画・共進化的 re-planning。大規模需要でSUMOより高スケール | 直接のLLM結合は薄い(**Java**) | **高**(JavaとPython LLMスタックの橋渡し) | GPL系 | 「**日課(activity chain)= routine層**」の概念モデルとして有用。実装採用はコスト高 |
| **Mesa / Mesa-Geo** | Python 汎用 ABM(スケジューラ+空間)。Mesa-Geo で GIS | **低**(同一Python) | **低** | Apache-2.0 | 交通/群集エンジンではない。本コードの自前 world 層と競合。参考どまり |
| **GAMA** | GAML DSL・GIS 重視 ABM | 中(外部) | 中〜高 | GPL | 参考どまり |
| **NetLogo** | 教育・プロトタイピング ABM | 低 | 低 | GPL | 規模не向き。参考どまり |

### 3-2. 群集モデル(渋谷スクランブルの歩行者流に効くか)

- **Social Force**(Helbing-Molnár 1995): 目標引力 + 社会的斥力の「心理的力」。**双方向流のレーン形成・
  自己組織化(stripe/lane)を再現**。実装: **PySocialForce**(Arena 3.0 の既定)、**pedsim_ros / libpedsim**(Gloor)。
- **ORCA / RVO2**(Reciprocal Velocity Obstacle): 幾何制約による**高速な衝突回避**。RVO2 に Python バインドあり。
  微視的な回避は速いが「群衆流の質感」は Social Force ほど自然でない。
- **Continuum crowds**: 群集を連続体(流体)扱い。**高密度**のマクロ流に強い。
- **交差流の物理**: 渋谷スクランブルのような双方向・斜め交差では**レーン形成・ストライプ模様**が創発する
  (実験・PNAS「lane formation in criss-crossing crowds」等)。Social Force / continuum はこれを再現できる。
- **ShibuyaSocial**(arXiv 2512.18550, 2025): 渋谷スクランブルの**実軌跡**(約407人追跡・推定約2000人)で学習した
  **LSTM+attention のデータ駆動モデル**。赤信号での停止・逆流でのレーン形成を再現、位置誤差 0.07m・エッジ精度>99%。
  **LLM は不使用**。→ 「歩行の物理は専用モデルに任せる」路線の直接の証拠。
- **結論**: 歩行忠実度が要るなら **PySocialForce(まず簡便)** か **学習型(ShibuyaSocial 系)** を
  「LLM が決めた目的地ノードを物理移動へ解く」下位エンジンとして差す。**LLM に足の運びを計算させない**。
  これは「知覚→思考(LLM: どこへ)→行動抽出(目的地ノード)→物理解決(群集エンジン)」の層分離そのもの。

### 3-3. 経路探索・ゲームAI(routine層=非LLM日課の高度化に使えるか)

- **経路探索**: A* / **階層的経路探索(HPA*)** で日課の移動を安価に。LLM 呼び出しゼロで routine を回す土台。
- **GOAP**(Goal-Oriented Action Planning): 各行動に前提条件/効果、**行動グラフ上の A***でゴール達成系列を探索。
  設計者が書いていない**多段プランが創発**。実行時コスト高=毎フレームでなく稀に計画。
- **HTN**(階層タスクネットワーク): タスクを階層分解。GOAP の親戚で構造化された分解に強い。
- **Behavior Tree**: sequence/selector/decorator の階層決定木。**可読・モジュラー**だが静的(動的適応は弱い)。
- **Utility AI**: 各行動を現在価値でスコア化し最大を選ぶ。**優先度が常に変わる動的世界**に強い。
- **ハイブリッド(GOBT等)**: BT の構造 + GOAP の動的計画 + Utility の選択、を融合。
- **本プロジェクトへの効き**: **routine層(非LLM日課)を Utility AI か GOAP/BT で駆動**し、LLM は逸脱・新規性・
  熟考にだけ使う——が定石。**LLM が GOAP のゴールや BT のノードを生成**する連携も可能(LLM=メタ計画、GOAP/BT=実行)。
  現行 `cognition/{drive,planning,routine}` はこの発想と整合。

### 3-4. 強化学習で日常行動を学ばせる系(LLM併用)

- **MobiVerse**(arXiv 2506.21784, UCLA 2025): (1) 社会人口統計から基礎アクティビティ連鎖を作る**軽量ドメイン特化生成器**、
  (2) 環境条件で活動を修正する**LLM修正器**、(3) 実行・監視の**可視化環境**、の3分割。
  **純LLMはスケールせず、純学習型は未知条件に適応できない→ハイブリッドが勝つ**。
  **軌跡認識の強化学習**で生成忠実度を報酬改善。日次「計画→実行→反省」で構造化JSON計画を生成。
- **GATSim**(arXiv 2506.23306): 生成エージェントによる都市モビリティ。活動計画+反省の系譜。
- **含意**: 「**日課は学習/軽量生成で安価に、適応・逸脱は LLM**」という分業は、本仮説(思考=LLM、日課=別モジュール)の
  実証。RL は routine層の忠実度を上げる補助として有効。

---

## §4. 「効く」の証拠(ablation・実証)

### 4-1. Generative Agents のアブレーション(最重要の直接証拠)

- **観測(observation)・計画(planning)・反省(reflection)は各々が信憑性に critical**。
- **反省を除くと、48シミュ時間以内に一貫した多日計画が崩れ、文脈無視の反復応答に退化**。
- 記憶(recency/importance/relevance の検索)も各要素が効く。
- 「**記憶あり vs なしの差は、LLM バックボーンの差より大きいことが多い**」=**モジュール設計への投資はモデル拡大に匹敵/凌駕しうる**。
- **本仮説への含意**: 「思考の周辺に置くモジュール(観測=知覚、反省、計画)」の有無が結果を左右する、という
  **モジュール分離そのものが効く**ことのアブレーション証拠。ユーザーの層分離方針を支持。

### 4-2. MobiVerse のハイブリッド実証

- 純LLM(適応的だが非スケール)・純学習型(スケールするが非適応)の**両極端がともに劣り、分業ハイブリッドが優位**。
- **知覚/環境(条件)を与える層 と 思考(LLM修正)を分けた**ことが、スケールと忠実度の両立に効いた。

### 4-3. AgentSociety の設計上の効き

- **Maslow 欲求段階・計画的行動理論(TPB)で意思決定を明示モデル化**し、構造化ゴールが外生ショックで進化。
- **エージェントと環境の進行を同期**させ、LLM 遅延がばらついても**再現性**を担保(=環境層と思考層の疎結合が
  再現性に効く設計)。定量的アブレーション数値は本調査では未確認。

### 4-4. 「人中心 ABM」vs「情報遷移システム(DES)」の設計論

- **ABM**: ボトムアップ。ミクロの主体の意思決定を書き、**マクロ構造(創発)**が主体間・環境との相互作用から立ち上がる。
  「世界を変える人」の創発を問う本課題は**本質的に主体(人)中心=ABM 側**が正しい枠。
- **DES**: システムを「資源可用性とイベントで遷移する**エンティティ**の集合」として、イベント待ち行列で駆動。
  entity/state/事象スケジューリング中心。
- **ODD プロトコル**(ABM 記述の標準): 「**Entities, state variables and scales**(どんな実体・状態変数・尺度)」と
  「**Process overview and scheduling**(どの実体が・いつ・どの順で・状態更新はいつ)」を分けて記述する。
  → **「実体+状態」と「過程+スケジューリング」を分ける規律**は、本プロジェクトの phase 群/状態更新則の
  再現性設計にそのまま借用できる(DES 的な明示スケジューリングの美点を ABM に取り込む)。
- **含意**: 主体中心(人=Actor)を基本に据えつつ、**状態更新と進行順序は DES/ODD 流に明示化**する折衷が、
  「創発を観るための人中心」と「再現性のための情報遷移規律」を両立させる。AgentSociety の同期設計はこの折衷の実例。

---

## §5. 出典一覧(URL + アクセス日 2026-07-14)

### 先行アーキテクチャ
- Generative Agents (Park et al. 2023, arXiv 2304.03442): https://arxiv.org/abs/2304.03442 — 実装: https://github.com/joonspk-research/generative_agents (Apache-2.0)
- Generative Agents (ACM DL 全文): https://dl.acm.org/doi/fullHtml/10.1145/3586183.3606763
- AgentSociety (Piao et al. 2025, arXiv 2502.08691): https://arxiv.org/abs/2502.08691 / HTML: https://arxiv.org/html/2502.08691v1
- AgentSociety (GitHub, Apache-2.0): https://github.com/tsinghua-fib-lab/AgentSociety — docs: https://agentsociety.readthedocs.io/en/latest/
- AgentSociety 解説 (MarkTechPost 2025-07-31): https://www.marktechpost.com/2025/07/31/agentsociety-an-open-source-ai-framework-for-simulating-large-scale-societal-interactions-with-llm-agents/
- OASIS (Yang et al. 2024, arXiv 2411.11581): https://arxiv.org/pdf/2411.11581 — 実装: https://github.com/camel-ai/oasis (Apache-2.0) / サイト: https://oasis.camel-ai.org/
- Concordia (DeepMind 2023, arXiv 2312.03664): https://arxiv.org/pdf/2312.03664 — 実装: https://github.com/google-deepmind/concordia (Apache-2.0)
- Concordia components README: https://github.com/google-deepmind/concordia/blob/main/concordia/components/README.md
- Concordia environment README: https://github.com/google-deepmind/concordia/blob/main/concordia/environment/README.md
- Project Sid / PIANO (Altera 2024, arXiv 2411.00114): https://arxiv.org/abs/2411.00114 / HTML: https://arxiv.org/html/2411.00114v1 — 実装(部分): https://github.com/altera-al/project-sid (ライセンス未確認)
- CoALA (Sumers et al. 2023, arXiv 2309.02427): https://arxiv.org/abs/2309.02427 / HTML: https://arxiv.org/html/2309.02427v3
- SOAR / ACT-R 比較 (arXiv 2201.09305): https://arxiv.org/abs/2201.09305 — 概説: https://roboticsbiz.com/comparing-four-cognitive-architectures-soar-act-r-clarion-and-dual/

### action extraction(構造化出力・関数呼び出し)
- vLLM Structured Outputs (docs): https://docs.vllm.ai/en/v0.8.2/features/structured_outputs.html
- vLLM Structured Decoding 入門 (blog): https://vllm.ai/blog/2025-01-14-struct-decode-intro
- Structured outputs in vLLM (Red Hat): https://developers.redhat.com/articles/2025/06/03/structured-outputs-vllm-guiding-ai-responses
- Guided Decoding 性能 (SqueezeBits): https://blog.squeezebits.com/guided-decoding-performance-vllm-sglang
- Ollama Structured Outputs (docs): https://docs.ollama.com/capabilities/structured-outputs / blog: https://ollama.com/blog/structured-outputs
- ReAct vs Function Calling (LeewayHertz): https://www.leewayhertz.com/react-agents-vs-function-calling-agents/
- 小型モデルの構造化出力頑健性 (arXiv 2507.01810): https://arxiv.org/html/2507.01810v1
- When Correct Isn't Usable: 小型モデルの構造化出力信頼性 (arXiv 2605.02363): https://arxiv.org/pdf/2605.02363
- The Constraint Tax (arXiv 2605.26128): https://arxiv.org/html/2605.26128

### 外部エンジン(交通・群集・ゲームAI・RL)
- SUMO TraCI (docs): https://sumo.dlr.de/docs/TraCI/index.html — traci (PyPI): https://pypi.org/project/traci/
- SUMO Libraries/Licenses (EPL 2.0): https://sumo.dlr.de/docs/Libraries_Licenses.html — LICENSE: https://github.com/eclipse-sumo/sumo/blob/main/LICENSE
- SUMO 歩行者モデリング (Erdmann & Krajzewicz): https://www.researchgate.net/publication/276253183_Modelling_Pedestrian_Dynamics_in_SUMO
- AgentSUMO (arXiv 2511.06804): https://arxiv.org/html/2511.06804v1
- SUMO-MCP (arXiv 2506.03548): https://arxiv.org/html/2506.03548v1
- LLM Digital Twin + SUMO (OpenReview): https://openreview.net/forum?id=vEZtmnqmtO
- MobiVerse (arXiv 2506.21784): https://arxiv.org/html/2506.21784v1 — 実装: https://github.com/ucla-mobility/MobiVerse
- GATSim (arXiv 2506.23306): https://arxiv.org/pdf/2506.23306
- MATSim vs SUMO 比較 (SUMO2020 paper): https://eclipse.dev/sumo/documents/2020/SUMO2020_paper_44.pdf
- Social Force Model (Helbing & Molnár 1995, arXiv cond-mat/9805244): https://arxiv.org/abs/cond-mat/9805244
- 自己組織化群集動力学 (Helbing et al., Transportation Science): https://pubsonline.informs.org/doi/10.1287/trsc.1040.0108
- PySocialForce を用いた社会ナビゲーション (Arena 3.0, arXiv 2406.00837): https://arxiv.org/pdf/2406.00837
- pedsim_ros (Social Force 実装): https://github.com/srl-freiburg/pedsim_ros
- 交差流のレーン形成 (PNAS): https://www.pnas.org/doi/10.1073/pnas.2505488122
- ShibuyaSocial (arXiv 2512.18550): https://arxiv.org/html/2512.18550v1
- Game AI Planning: GOAP/Utility/BT (Tono): https://tonogameconsultants.com/game-ai-planning/
- GOBT (GOAP+Utility+BT, JMIS): https://www.jmis.org/archive/view_article?pid=jmis-10-4-321

### 設計論(ABM/DES/ODD)
- ODD プロトコル (Grimm et al. 2020, JASSS): https://www.jasss.org/23/2/7.html / PDF: https://bio.uib.no/te/papers/Grimm_2020_The_ODD_protocol_for_describing_agent-based.pdf
- ABMS 入門(ODD スライド): https://www.uv.mx/personal/aguerra/files/2018/08/abms-slides-04.pdf

### 関連する既存プロジェクト内調査(重複回避のため参照)
- `docs/research/framework-architecture.md`(基盤/環境の場所非依存分離・環境自動生成)
- `docs/lit/mas__concordia2023_deepmind.md` / `mas__yang2024_oasis.md` / `mas__agentscope2024_largescale.md`
- `docs/lit/engine__distributed-actor-overview.md`(分散アクター)
