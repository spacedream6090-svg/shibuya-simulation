# 推論と推論の間を生きる — 「全員思考」下の間隙生活(interstitial life)設計

作成: 2026-07-20 / 種別: **リサーチ+設計文書**(コード変更なし・本書1本のみ) / 執筆: Opus 4.8(Web調査)
前提文書: [`../plans/w2-execution-plan.md`](../plans/w2-execution-plan.md) §1(全員思考モデル) /
[`token-budgets.md`](token-budgets.md) / [`compute-efficiency`](compute-efficiency.md) /
[`../plans/compute-optimization.md`](../plans/compute-optimization.md) / [`memory-cognitive-research.md`](memory-cognitive-research.md) /
[`reflection-drift.md`](reflection-drift.md) / [`../design-candidates/schedule-book-spec.md`](../design-candidates/schedule-book-spec.md)

> 依頼(研究責任者): 全員思考モデルでは LLM 推論が「朝計画1+夜内省1+日中の顕著性熟慮~6=計~8回/人日」。
> (1) 6回/日は少なすぎる。200体較正(日中~21.6呼/人日)になるべく近づけたい。
> (2) 推論と推論の空白を、朝の予定・会った人・出来事のログから「簡単なストーリー」で埋めたい。
> (3) 計画に沿うだけでは決定論的な半死のシミュになる。計画実行中のランダム性を前向きに実装したい。
> (4) 現実の人は一日に何十回も会話・思考する。重要な会話は毎回LLMでなくてよいが、記録に残る形にしたい。

---

## 0. 結論(主要発見5点+設計推奨の要約)

### 0.1 主要発見(いずれも 2024-2026 文献に基づく)

1. **先行研究はほぼ全て「詳細度の階層化(LOD)」に収束する**。100万〜1万体級を回した OASIS・AgentSociety・
   Project Sid は、**全相互作用を LLM で回さず、大多数をルール/軽量処理・一部だけを LLM** に差す構成で規模を達成
   している。「間隙を埋める」問題の業界的正解は「間隙の大半を LLM 以外で埋める」であり、主計画者の設計方針
   (①②③)はこの収束点と整合する。

2. **AGA(Affordable Generative Agents, TMLR 2024)は本件の直接の設計図**。(a) Lifestyle Policy=行動系列を
   embedding 近傍+実行条件で**キャッシュ再利用**し LLM 呼をスキップ、(b) Social Memory=関係(0-10 スコア)・印象・
   要約イベントで**対話補助情報を圧縮**。25人町で総トークン **42.7%**(=呼数・トークンを半分以下)に削っても、
   人間らしさ Likert は 3.13→3.21・3.97→4.01 と**むしろ微増**。「トークンを盛るほど良い」は否定され、
   「believability は行動の有限性で決まる」= **削減の余地は大きく、質は落ちない**。
   出典: [arXiv:2402.02053](https://arxiv.org/abs/2402.02053)。

3. **会話の中身を生成せずに「型・スタンス・トーン・帰結」だけを状態から決める手法が確立している**
   (Dialogue Acts/Agenda-Based Simulator 2007、話題×スタンス ABM 2025、意見・関係共進化 ABM)。
   これが主計画者の C2(構造化会話・LLMなし)の実装済み前例に相当し、25万規模で「誰が誰とどんな会話をしたか」を
   **LLMコスト0で大量に記録に残せる**。既存の `schedule.py`(会話テキストからの決定論抽出)は既にこの型の縮小版。

4. **意見力学は FJ(Friedkin-Johnsen)を土台に、対面=FJ・SNS=情報カスケードで重み分けするのが定石**
   (FJC モデル 2025)。既存 `opinion.py`(FJ 実装済み)はこの潮流の中核であり、C2 の「機械的効果」の数値エンジンに
   そのまま使える。LLM 対話は FJ より急峻・分極寄りの変化を示すため、**FJ を骨格に LLM を分極の増幅項に限定**する
   のが 2024-2026 の共通所見。

5. **「書き込み時に要約すると異なるエピソードが意味的一般化に潰れ、エピソード信号が失われる」**という 2025-2026 の
   警告がある(Beyond Static Summarization 他)。主計画者の②(ダイジェスト→物語記憶)は正しい方向だが、
   **生ログの過圧縮は禁物**。ダイジェストは「機械的な客観カウント(既存 `digest_line` と同型)」に留め、
   一人称の物語化・意味の付与は夜内省の LLM に委ねる二段構えが妥当。出典:
   [arXiv:2601.04463](https://arxiv.org/pdf/2601.04463) / [Position:Episodic Memory 2025](https://arxiv.org/pdf/2502.06975)。

### 0.2 設計推奨の要約(詳細は §4-§6)

- **①確率的実行**: 改良して採用。既存 `hub.stream()` を使い、**新 stream 4本**(出発ゆらぎ・経路ゆらぎ・寄り道・中断)を
  routine の計画実行部(`_plan_move`/`decide`)に追加。MATSim の再計画ミューテーション(時刻 ±30分級・確率的経路/手段)と
  活動の day-to-day variability 実証を根拠に、逸脱の**頻度と幅**を conf 化。LLMコスト **0**・エンジンコスト**微増**(乱数数本/agent-step)。
- **②ナラティブ補間**: 改良して採用。ただし「圧縮ログ→物語」は**機械ダイジェスト(LLM0)**と**夜内省の物語化(既存LLM)**に
  分離。新 `interstitial_digest` 行を build_prompt に追加(既存 `date_line`/`digest_line` と同じ注入 seam・既定 None=バイト一致)。
  LLMコスト **0**(追加呼なし)・各 LLM 呼のプロンプトに +2〜4行。
- **③会話3層**: 全面採用+精緻化。C1=フルLLM(既存)/ C2=構造化会話(LLMなし・FJ+関係+語彙接触+イベント記録)/
  C3=挨拶・すれ違い(集計のみ)。C2 が「記録に残る会話数」を **6→20〜40/人日**へ引き上げる主レバー。C2→C1 昇格は
  顕著性ゲート(既存 drive)に接続。
- **第4機構(新提案)= 好奇心/退屈の内発ドライブ + AGA Lifestyle Policy キャッシュ**。前者は「計画にない自発行動」を
  ボトムアップに生む(ユーザーの自然界志向と整合)。後者は**同じ GPU 予算内で LLM 呼を実質的に増やす**回収策で、
  「6→21.6 に近づける」問いへの正面回答(speculative decoding 2.8x と併用で日中熟慮を ~6→~14-16/人日に押し上げ可能)。
- **「6回/日を21.6に近づける」への回答**: LLM 呼そのものを 21.6 まで上げると 4.7M 呼/日=予算超過。**現実解は二本立て**:
  (A) *記録に残る認知・社会イベント*を C2+②で **20〜40/人日**に上げ(現実の会話数十回に到達)、
  (B) *LLM 呼*自体は speculative decoding(無損失2.8x)+AGA 再利用(呼-40〜57%)+中位帯の小モデル化で
  同一予算内の**実効呼数を ~6→~14-16/人日**へ引き上げる。両者で「21.6 相当の密度」に到達する。
- **R1 整合**: 全機構が「新 stream のみ・既定 OFF でゴールデン L1 バイト一致・呼数 k 非依存・no-fingerprint」を満たす設計
  (§7 で全数確認)。

---

## 1. 問題の定式化 — 何が「間隙」か

全員思考モデル(w2-execution-plan §1.4)の1人・1シミュ日の LLM 発火は:

| 発火 | 呼数/人日 | 契機 |
|---|---:|---|
| 朝計画 | 1 | 起床時刻(自然に時間分散) |
| 夜内省 | 1 | 就寝時刻(自然に時間分散) |
| 日中の顕著性熟慮 | ~6(N比例予算の平均) | drive ゲージが閾値超え(発話量・関係変化・造語接触・地位変化等) |
| **計** | **~8** | |

- 1日=144 step(10分/step)。起きている ~100 step のうち、LLM が触るのは **~8 step**。残り **~92 step(約92%)が「間隙」**
  = 現状はエンジンの routine(移動・勤務・食事・帰宅)が純機械的に埋める。
- 較正済み200体ランの日中熟慮は **21.6呼/人日**(w2 §1.5)。全員思考の日中 ~6 はその **28%**。この差が「6回は少なすぎる」の実体。
- 現実の人間は 1日に **13,000〜16,000語**を話し(Mehl らの EAR 研究。近年は減少傾向)、擦れ違いの短い会話を含めれば
  **数十回**の相互作用がある(出典: [UA/Mehl 2007・2026](https://news.arizona.edu/news/are-we-talking-less-qa-psychologist-matthias-mehl))。
  現状の「8回のLLM思考+機械移動」はこの密度に遠く及ばない。

**間隙を埋める3つの独立した目標**(混同しないこと):
1. **行動の非決定性**(目標③): 計画実行が機械的すぎる → ランダム性の注入。
2. **認知の連続性**(目標2): LLM が飛び飛びの瞬間しか見ず、間の物語を持たない → ナラティブ補間。
3. **社会的相互作用の密度と記録**(目標4): 会話が LLM 発火時しか起きない → 軽量会話層で数十回/日を記録に残す。

以下、先行研究(§2-§3)→ 設計批判・改良(§4)→ コスト試算(§5)→ イベント量試算(§6)→ R1整合(§7)。

---

## 2. リサーチ(a) 先行 LLM 社会シミュは「呼び出し間の時間」をどう埋めるか

各システムの手法要約と、**在場25万・A5000×7・LLM予算~200万呼/日**という制約下での適用可否。

### 2.1 Stanford Generative Agents (Park et al. 2023)
- **手法**: 計画を**再帰的に階層分解**する。まず「その日の大まかな計画」を粗く生成 → より細かい時間帯(1時間単位)へ分解
  → さらに 5〜15分単位の行動へ再帰分解。実行中に**知覚した出来事に反応(react)**して、必要なら**その時点から計画を作り直す
  (replan)**。記憶ストリームから recency×importance×relevance で想起、importance 累積>150 で reflection 発火(1日2〜3回)。
- **間隙の埋め方**: 「計画の階層分解」そのものが間隙充填機構。粗い計画を細かい行動列に**決定論的に展開**し、
  各 5-15分スロットを埋める。LLM を呼ぶのは (i) 初回の計画生成、(ii) 予期せぬ知覚での react/replan、(iii) reflection のみ。
- **適用可否**: △→○。**計画の階層分解の思想は本プロジェクトの `planning.make_plan`→`routine._plan_move` に既に部分移植済み**
  (朝計画の {when,what,place} を時間帯で消化)。ただし GA は 25体×2日で「数千ドル」・O(N×T)で 25万には非現実的。
  借用すべきは「粗計画→細行動列の決定論展開」と「react/replan を顕著性で絞る」考え方(=既存 drive ゲート)。
  出典: [arXiv:2304.03442](https://arxiv.org/abs/2304.03442)。

### 2.2 Concordia (DeepMind, Vezhnevets et al. 2023)
- **手法**: テーブルトーク RPG の **Game Master (GM)** 型。GM が各エージェントの自然言語行動を解決し、grounded world state
  (money/votes/resource stocks)を維持・検証(不正行動を却下)、observation を配信。認知は March & Olsen の
  「どんな状況か/自分は何者か/そういう者はどう振る舞うか」= 非最大化(報酬最大化でない・文化的パターン補完)。
- **間隙の埋め方**: GM が**ナラティブ的に**世界を進める(間隙は GM の物語生成が埋める)。ただし GM 自体が LLM で、
  O(N×T×C) 呼のため**スケール非対応**(batch/cache/並列の記述なし)。
- **適用可否**: 借用限定。**「非最大化の意思決定は指紋最小化と親和」**(world_change_drive を最大化させない方針に合致)。
  GM のナラティブ駆動を**LLM無しの機械ダイジェスト**(②)に置換するのが本プロジェクトの解。grounded 変数(資源/評判)の
  検証思想は既存 tools/economy に既にある。出典: [arXiv:2312.03664](https://arxiv.org/abs/2312.03664)、
  既存メモ [`../lit/mas__concordia2023_deepmind.md`](../lit/mas__concordia2023_deepmind.md)。

### 2.3 Project Sid / PIANO (Altera 2024)
- **手法**: **PIANO(Parallel Information Aggregation via Neural Orchestration)**=1エージェントに **~10 個の並行モジュール**
  (記憶・社会認知・目標生成・行動・発話等)を非同期並列で走らせ、cognitive controller が整合を取る。social goal を **5〜10秒ごと**
  再生成。500体×2.5h の文化・宗教・経済の伝播ランを GPT-4o で実施。
- **間隙の埋め方**: 「並行モジュール」により、行動と発話と社会認知が**別クロックで**進む(間隙が生じにくい)。ただし
  トークン/コストは非開示・GPT-4o 必須で、7×A5000 の 4B 級では並行10モジュールは予算的に不可能。
- **適用可否**: △。並行モジュール数=LLM呼上限の目安にはなるが、本プロジェクトは**モジュールを LLM でなく機械層に**持たせる
  (drive・factors・opinion・relations が「並行モジュール」の役割を LLM 無しで担う)。思想の借用のみ。
  出典: [arXiv:2411.00114](https://arxiv.org/abs/2411.00114) / [repo](https://github.com/altera-al/project-sid)。

### 2.4 AgentSociety (清華 FIB-Lab 2025)
- **手法**: **1万超(同時最大3万)エージェント・500万相互作用・平均500相互作用/体/日・実時間より高速**の都市社会シミュ
  (※「100万規模」は v1 arXiv では未実証。設計文書に引くなら**実証値 1万〜3万**を基準にするのが安全)。
  Ray(分散)+ asyncio(I/Oレイテンシ秘匿)+ MQTT で規模を達成(=モデル最適化でなく**配線最適化**)。
- **間隙の埋め方 = 2重**: (i) **移動を重力モデル(gravity model, 数式)で代替**し「LLM 計算オーバーヘッドを削減しつつ
  人間の空間パターンに整合」。(ii) **マズロー欲求階層**が動機ドライバとなり、**計画行動理論(Theory of Planned Behavior)**で
  意図を行動サブタスク列に分解 → LLM を絶えず呼ばずに計画済みサブタスクを実行。GA の階層分解と同系だが**心理モデルで駆動**する点が特徴。
  エージェントの閉ループ = 行動決定 → イベントフィードバック → 記憶更新 → 感情/認知分析。
- **適用可否**: ◎(思想が本プロジェクトと同型)。(i) の移動=非LLM は既存 routine そのもの。(ii) の Maslow+TPB は既存
  `needs.py`/`factors`/`drive` と `planning`(意図→サブタスク)に対応。500相互作用/体/日は §6 の「記録に残る会話数十回/日」目標の
  先行到達例(ただし内訳の LLM/軽量比は非開示)。配線面は既存 `llm/fleet`+非同期発行(P2 重畳要件)が相当。
  出典: [arXiv:2502.08691](https://arxiv.org/abs/2502.08691) / [repo](https://github.com/tsinghua-fib-lab/AgentSociety)。

### 2.5 OASIS (2024)
- **手法**: 最大100万体の SNS シミュ。**Time Engine** が 24次元・時間帯別の活動ベクトルで各エージェントを**確率的に活性化**
  (=LOD 的機構。全員が毎 step 動くのでなく、時間帯別の確率で「今アクティブか」を決める)。行動空間は SNS 特化の 21種。
  実測: **100万体×60step=A100×24枚で1週間**、Reddit 10k は A100×4枚で 1step=15分・1393コメント/step 生成。
  活性化確率は**コアユーザ 0.1・一般ユーザ 0.01**(=大多数は各 step で沈黙し LLM を呼ばない)。
- **間隙の埋め方**: **確率的活性化そのものが間隙充填**。「今この step でこの人は行動するか」を確率で決め、非活性なら LLM を呼ばない
  (=イベント駆動スキップの実用テンプレート)。
- **適用可否**: ○(機構流用)。**既存の drive ゲート+顕著性予算がこの確率的活性化に相当**。OASIS のドメイン(SNSフィード/RecSys)は
  非採用だが、Time Engine の「時間帯別活性化確率」は本プロジェクトの presence 曲線(在場ローテーション P3)と自然に接続する。
  出典: [arXiv:2411.11581](https://arxiv.org/abs/2411.11581)、既存メモ [`../lit/mas__yang2024_oasis.md`](../lit/mas__yang2024_oasis.md)。

### 2.6 Lyfe Agents (2023) / Humanoid Agents (2023)
- **Lyfe Agents**: **option-action 階層**(LLM は高レベル option=「話す」等を選ぶだけ。以後の低レベル行動と**終了判定は非LLM**の
  安価な手段=時間トリガ・会話の繰り返し検出・埋め込み検索で回す)+ **非同期自己監視** + **Summarize-and-Forget 記憶**。
  コストは **$0.50/体/人間時間 vs Park 原実装の推定 $25 = 50倍安**。呼び出し間は決定論的行動(会話継続・衝突回避ナビ・近傍検索)で埋める。
  出典: [arXiv:2310.02172](https://arxiv.org/abs/2310.02172)。
- **Humanoid Agents**: 基本欲求・感情・親密さの **System-1 層**を追加し、System-2(LLM)の発火を絞る。
  出典: [arXiv:2310.05418](https://arxiv.org/abs/2310.05418)。
- **間隙の埋め方**: 両者とも「安価な下位層(option 内の行動列/System-1)が間隙を埋め、高価な LLM は要所だけ」。
- **適用可否**: ◎(思想が本プロジェクトと同一)。Lyfe の option-action は**朝計画(option)→ routine 実行(action列)**に、
  Humanoid の System-1 は **drive/factors/needs** に既に対応。Summarize-and-Forget は既存 memory の 3層+夜内省の consolidate に対応。

### 2.7 AGA (Affordable Generative Agents 2024) — §0.1-2 の詳細
- **機構1 Lifestyle Policy**: 計画を「計画→サブ計画→行動列+実行条件(環境要件)」のグラフで保存。新計画は embedding の
  **コサイン類似度**で既存を検索し、類似度が閾値超 かつ 環境が実行条件を満たすなら **LLM をスキップして保存済み行動列を直接実行**。
- **機構2 Social Memory**: 会話補助情報を圧縮。Relationship(双方向 0-10 スコア)、Feeling(相手への印象)、
  Summary Events(記憶から検索→重複フィルタ→dense compression で要約統合)。生の記憶断片をそのまま詰めず密圧縮。
- **数値**: 3人町 31.1%、25人町 **42.7%**(規模が上がるほど再利用が効く)、VirtualHome 単体 3.4%。品質 Likert は微増。
- **適用可否**: **◎ 最重要・直接採用候補**(§4-第4機構)。渋谷の生活動線(通勤・買い物・飲食の反復)は Lifestyle Policy に極めて適合。
  Social Memory の 0-10 関係スコアは既存 `relations.py` と表現統一でき、C2(§4-③)の共通データモデルになる。
  **注意**: AGA 評価は最大25人・単一機種 GPT-3.5。25万・多様ペルソナでの類似度閾値チューニングと**ポリシー汚染(誤った再利用で
  行動レパートリーが痩せる)**の管理は自前検証が必須。これは compute-optimization.md の E2-2(routine caching)の採用条件
  「distinct-n・行動レパートリー曲線が痩せない」と同一の関門。出典: [arXiv:2402.02053](https://arxiv.org/abs/2402.02053)。

### 2.8 時間抽象化・イベント駆動スキップの一般手法
- 収束点は「**イベントが起きない step は LLM を呼ばず、機械層(routine/factors/opinion)で決定論的に進める**」。
  本プロジェクトは既にこの構造(routine が間隙を埋め、drive が LLM 発火を絞る)。先行研究が足すのは:
  (i) OASIS の時間帯別確率活性化、(ii) AGA の行動キャッシュ、(iii) Lyfe の option-action と Summarize-and-Forget。
  いずれも本プロジェクトの既存 seam に載る。
- **離散イベントシミュ(DES)**: タイムスタンプ付きイベントを優先度キューで管理し、内部時計を「次イベントの時刻」まで直接進める
  =イベントの無い時間帯を丸ごとスキップ。最も古典的で確実な「何も起きない時間の圧縮」。ただし本プロジェクトは固定 step の
  同期シミュ(混雑・在圏の一括ベクトル演算が step 同期前提)なので、DES 全面採用でなく**深夜低活動帯の step を粗くする**部分適用が現実的
  (Concordia v2 の「1 step=任意時間長」と同じレバー)。
- **Concordia v2(2025)**: 「**ステップ間に経過する時間の量は完全に任意**」と明記。1 step を 1分〜1日で可変にできる=時間抽象化の
  設計レバー。ただしシーン終了の自動判定・退屈期間の要約早送りは**シナリオ設計者の実装に委ねられ**、自動機構は本文にない。
  出典: [arXiv:2507.08892](https://arxiv.org/html/2507.08892v1)。

### 2.9 スループット/スケール手法 — 25万規模で効く2つ+1つの緊張
- **AI Metropolis(MLSys 2025)= 最有力のスループット原理**: LLM エージェントシムの逐次 LLM 待ちアイドルを、
  **out-of-order execution + 依存グラフ追跡**で解消。空間時間的依存の無いエージェント同士を**異なるシミュ時刻のまま並列前進**させ、
  同期ベースライン比 **スループット2-3倍**。相互作用しないエージェント数に比例してスピードアップ。→ 25万のうち大多数が互いに無関係な
  本プロジェクトに直接効く。**P2 の「LLM/エンジン重畳(非同期発行)」要件の理論的裏づけ**であり、重畳の設計指針として引くべき。
  出典: [MLSys 2025](https://proceedings.mlsys.org/paper_files/paper/2025/file/4f31327e046913c7238d5b671f5d820e-Paper-Conference.pdf)。
- **Agentic Plan Caching(2025)**: 計画段階の構造化プランテンプレを抽出・保存・適応・再利用。意味的に類似したタスク間で
  **コスト -50.31%・レイテンシ -27.28%**。§4.4 の④-b(AGA Lifestyle Policy)と同系で、朝計画の再利用の裏づけ。
  出典: [arXiv:2506.14852](https://arxiv.org/abs/2506.14852)。
- **⚠️ 緊張: AgentTorch / LLM Archetypes(MIT Media Lab, AAMAS 2025)**: **アーキタイプ(行動クラスタ)単位でのみ LLM を問い合わせ**、
  同型エージェントに展開して数百万規模を少数推論で回す。**これは本プロジェクトの「全員思考(ルールベース専用層をゼロにする)」方針と
  真っ向から相反する**トレードオフ軸(個の主体性 vs 集団スケール)を体現。compute-optimization.md が archetype 近似を
  「個体の異質性と稀な逸脱=世界改変者を潰す」として非推奨にしたのと同じ理由で、**本プロジェクトは archetype を採らない**。
  この対立の存在を明記することが、①②③④の設計選択(=個を保ったまま LLM 以外で間隙を埋める)の正当化になる。
  出典: [arXiv:2409.10568](https://arxiv.org/html/2409.10568v1)。

---

## 3. リサーチ(b) 軽量/LLMなしの会話・(c) 実行ランダム性・(d) 圧縮ログ→記憶

### 3.1 (b) LLMなし/軽量の会話シミュレーション
先行研究群は「**3層 LOD**」に収束する:

| 層 | 手法 | 出典 | 本プロジェクトの対応 |
|---|---|---|---|
| 背景(大多数) | FJ/bounded confidence(B-4)+関係共進化ABM(B-3)+IC/LT拡散(B-5)。会話生成なし・行列演算のみ | [FJC:2506.16302](https://arxiv.org/abs/2506.16302) / [共進化:2407.00145](https://arxiv.org/html/2407.00145v2) / [BCサーベイ:Automatica2023](https://www.sciencedirect.com/science/article/pii/S0005109823004661) | 既存 `opinion.py`(FJ)+`relations.py`。**C3(集計のみ)** |
| 中間(定型相互作用) | Dialogue Acts 系列(挨拶→話題→スタンス→同意/反論→別れ)+話題/スタンス/トーン/帰結ABM。LLM不要 | [Agenda-Based:2007](https://aclanthology.org/2007.sigdial-1.48.pdf) / [Hidden Agenda:2009](http://mi.eng.cam.ac.uk/~sjy/papers/scyo09.pdf) / [話題×スタンスABM:EPJDS2025](https://link.springer.com/article/10.1140/epjds/s13688-025-00593-3) | **C2(構造化会話)** = 主計画者の設計 |
| 注目(観察対象) | AGA でLLM呼をキャッシュ再利用+EcoLANG で1呼トークン-20% | [AGA:2402.02053](https://arxiv.org/abs/2402.02053) / [EcoLANG:2505.06904](https://arxiv.org/abs/2505.06904) | **C1(フルLLM発話)** = 既存 `_llm_speak` |

- **意見力学の要点**: FJ を土台に、**対面=FJ・SNS=情報カスケードで重み分け**(FJC モデル)。LLM 対話は FJ/BC より
  **急峻・分極寄り**の変化を示すため(He et al. 2026、Chuang et al. 2024)、FJ を骨格に LLM を「非線形な急変・分極の増幅項」に限定。
  → 既存 `opinion.py` の「対面/DM/SNS 別重み」がまさに FJC 的構成。C2 の意見更新は FJ、C1 の LLM 発話が急変項。
- **EcoLANG(EMNLP2025)**: 語彙を進化圧縮(WordNet 同義語クラスタリングで高頻度・短語のみ残す)+文レベル規則を GA 最適化。
  生成トークン **20%超削減**・精度維持。AGA(呼数削減)と**直交**するので併用可。C1 の出力語彙制限に安価に効く。
  出典: [arXiv:2505.06904](https://arxiv.org/abs/2505.06904)。
- **重要な含意**: 既存 `schedule.py`(発話テキストからの決定論パーサで予定を抽出→帳簿記入・LLM0)は、**C2 の縮小前例**。
  C2 は「発話を生成してから抽出」でなく「発話を生成せず両者の状態から話題・スタンス・帰結を直接決定」へ進める点が新しい。

### 3.2 (c) 活動実行のランダム性 — 計画からの逸脱の実証(数値確定済み)
主計画者①の設計を「実証パラメータ付き」に落とすための根拠。**逸脱率の較正ターゲットが複数の独立研究から一致して得られる**のが収穫。

- **人間移動の予測可能性(ランダム性の"量"のマスターノブ)**: Song et al. (2010, Science) は5万人の位置データで
  **理論的最大予測可能性 Πmax の分布は 93% にピーク**(移動距離によらずほぼ一定)= 理想的予測器でも **~7% は不可避のランダム成分**。
  さらに **規則性 R ≈ 0.7**(平均して時間の約70%は「最も訪れる場所」にいる)= **1日の約30%が routine から外れる**。
  Schneider et al. (2013) は日々の移動を**17種の motif で人口の約90%を説明**(個人は日ごとに少数の motif 間を行き来)。
  出典: [Song 2010, Science](https://www.science.org/doi/10.1126/science.1177170) / [Schneider 2013, J.R.Soc.Interface](https://royalsocietypublishing.org/doi/10.1098/rsif.2013.0246)。
- **MATSim の再計画ミューテーション(①の既製レシピ)**: `TimeAllocationMutator` の検証済みデフォルトは
  **`mutationRange=1800秒(=±30分)`・一様分布・`mutationAffectsDuration=true`**(開始時刻をずらすと継続時間も連動=玉突き遅延が伝播)。
  戦略重みの経験的配分は `ChangeExpBeta`(既存計画保持)0.5〜0.8 に対し `ReRoute`/`TimeAllocationMutator`/`SubtourModeChoice` 各 0.1
  = **毎回実際に計画を変えるのは1割前後のエージェントだけ**。注意: MATSim は**正規でなく一様分布**(裾を重くしたければラプラス/正規に差し替え可)。
  出典: [TimeAllocationMutatorConfigGroup (doxygen)](https://www.matsim.org/doxygen/classorg_1_1matsim_1_1core_1_1config_1_1groups_1_1_time_allocation_mutator_config_group.html)。
- **day-to-day variability(個人内変動の寄与率)**: 日々のトリップ数変動のうち **個人内(intrapersonal)が Seattle ~38%・Reading ~50%**。
  = 人間行動の約4〜5割は「同じ人でも日によって違う」成分。**活動種別で反復率が異なる**(Susilo & Axhausen 2014, HHI 適用:
  通勤・通学=高反復=決定論寄り、買い物・レジャー=低反復=ランダム寄り)。→ ①は `activity_type → deviation_probability` のテーブルを持つべき。
  出典: [Susilo & Axhausen 2014, Transportation](https://link.springer.com/article/10.1007/s11116-014-9519-4)。
- **計画外の立ち寄り(寄り道 detour の実測)**: **トリップの約44.3%が計画外の目的地立ち寄りを含む**(Hwang 2010 系)。
  消費では**購買決定の76%が店内**・計画外購買はベースライン46%〜文脈次第で最大93%。→ 寄り道確率は**周辺スポットの魅力度・密度に依存**させるのが実証的
  (渋谷=繁華街なので上限寄りが妥当)。**注意: 日/トリップ集計の44%をそのまま per-step 確率にしない**(集計単位で数倍ずれる)。
  per-move 10〜20% で発火させれば1日累積で40%台に届く。
  出典: [Theory of Unplanned Travel Decisions](https://www.researchgate.net/publication/220542959_A_Theory_of_Unplanned_Travel_Decisions_Implications_for_Modeling_On-the-Go_Travelers) / [POPAI 2014](https://www.en.nvc.nl/news/item/popai-76-purchase-decisions-made-in-store/)。
- **ABM の確率成分(選択の非決定化の理論核)**: ランダム効用 `U = V(決定論) + ε(Gumbel)` → ロジット選択。
  **`ε = -log(-log(uniform))` で一様乱数から Gumbel を生成でき再現性を保つ**。温度パラメータ1つで「計画通り⇔気まぐれ」を制御。
  必須活動=低ノイズ・裁量活動=高ノイズ を温度で表現。出典: [Bhat, ABM handbook](https://www.caee.utexas.edu/prof/bhat/abstracts/tshandbk.pdf)。
- **3つの較正ターゲット(①のパラメータをこれに同時に合わせる)**: (a) 予測可能性 ≈93% / 規則性 R≈0.7、
  (b) 個人内変動が総分散の 40〜50%、(c) 日次逸脱率 25〜35%。3点同時整合で「人間らしいランダム性」の"量"が定まる。
- **含意(①への根拠)**: 逸脱は「一様乱数を毎 step」でなく「**高反復性(R≈0.7)に、活動種別で重み付けた少量の構造化ノイズ(~30%)を重ねる**」。
  「昨日と同じ日」を仮定する routine caching(compute-optimization E2-2)はこの中程度変動を潰すため、①がその対抗策になる。

### 3.3 (d) 圧縮ログ→内省→物語記憶
- **エピソード記憶の5要件**(Position Paper 2025): 長期保存・明示的推論・単発学習・インスタンス固有・文脈束縛(who/when/where/why)。
  ②が目指す「物語記憶」はこの文脈束縛を満たす方向。出典: [arXiv:2502.06975](https://arxiv.org/pdf/2502.06975)。
- **書き込み時要約の罠**: 「書き込み時に要約するとエピソードが意味的一般化に潰れ、エピソード信号を使う前に破壊する」
  (Beyond Static Summarization 2026)。→ ②のダイジェストは**生ログを潰さず**、機械的な客観カウント(差分・会った人・出来事)に留め、
  意味づけ(なぜ印象に残ったか)は夜内省の LLM に委ねる。出典: [arXiv:2601.04463](https://arxiv.org/pdf/2601.04463)。
- **既存資産との整合**: [`memory-cognitive-research.md`](memory-cognitive-research.md) は ACT-R(基礎活性化・fan干渉・閾値τ+ノイズによる
  想起失敗)で「忘れる・思い出せない」を第一級化する設計を既に持つ。②のダイジェストは**この記憶系の入力**であって置換ではない。
  ダイジェストが夜内省で consolidate され、ACT-R 活性化を持つ episode になる、という直列関係が正しい。
  既存 `reflection.py` の `consolidate(summary, salient)` がこの受け皿。
- **既存の前例**: `recursion.py::digest_line`(「昨日の街の動き」を客観カウントで1行化し build_prompt に注入)は、
  **②の街レベル版が既に実装・稼働している**。②は「街の digest」を「個人の一日の digest」に拡張するもの=前例に完全に載る。

---

## 4. 設計批判と改良 — ①②③+第4機構

### 4.1 ①確率的実行 — 採用(精緻化)
**主計画者の案**: 計画は骨格。seed付き乱数stream で出発遅延・経路ゆらぎ・衝動的寄り道・中断確率を注入。偶発的遭遇はシミュ物理から創発。

**批判と改良**:
- 現状 `routine._plan_move`/`decide` は既に多数の乱数を引く(`choose_destination`・`_choose_mode`・`stay_steps`)が、
  これらは**既定 stream に相乗り**しているため R1 上「新機能=新 stream のみ」を守るには**専用 stream を分離**する必要がある。
  既存の良い前例: `_crowd_dest`(stream `"crowd"`)・`_curfew_suppressed`(stream `"curfew"`)・`_media_action`(stream `"media"`)は
  いずれも**専用 stream+既定OFFで draw順を汚さない**作法を確立済み。①はこの作法を4本に拡張する。
- 逸脱は**一様乱数でなく構造化ノイズ**であるべき(§3.2、Song 93%)。発火確率は小さく保つ。

**改良版① = 実証に基づく3層構成**(§3.2 の交通行動研究に基づく L1/L2/L3。すべて `hub.stream(name, agent.id, day/step)`・既定 OFF=バイト一致):

| 層 | stream | 挿入点 | 効果 | 実証パラメータ |
|---|---|---|---|---|
| **L1 骨格** | `motif` | `planning.make_plan` 後(朝1回) | その日の移動 motif/計画テンプレを確率抽選(routine motif に高確率)。「今日はいつもと違う一日」の上位ゆらぎ | Schneider: 17 motif で90%説明。routine に高確率配分 |
| **L2 時刻ジッター** | `jitter_time` | `_plan_move` の予定消化・`_choose_mode` | 各活動の開始/終了・継続時間を **一様[−30分,+30分]** ずらす(継続時間も連動)。経路・手段も確率変更 | MATSim `mutationRange=1800s`・一様・`affectsDuration=true` |
| **L3 逸脱イベント** | `detour` / `interrupt` | `decide` 自由行動枝 / `stay_until` 判定 | ①寄り道(目的地手前で近傍POIに立ち寄り)②中断(活動途中で離脱)。**活動種別で確率可変**(通勤=低・買い物/娯楽=高)、周辺スポット魅力度でスケール | per-move **10〜20%**(1日累積で ~44% が立ち寄りを含む) |

- **選択の非決定化(任意の上物)**: routine の行き先 argmax を、`U=V+ε`(Gumbel `ε=-log(-log(uniform))`)の**ロジットサンプリング**に置換可能。
  温度1つで「計画通り⇔気まぐれ」を制御。必須活動=低温(決定論寄り)・裁量活動=高温。既存 `choose_destination`(EPR)の自然な確率化。
- **較正ターゲット**(実装後の検証で合わせる): (a) エージェント行動の予測可能性 ≈93%/規則性 R≈0.7、(b) 個人内変動が総分散の 40〜50%、
  (c) 日次逸脱率 25〜35%。3点同時整合で「注入量が適正か」を一発で測れる(R が 0.9 に張り付けば弱すぎ・0.5 を割れば強すぎ)。
- **既存の作法との整合**: L2/L3 の stream 分離は `_crowd_dest`(stream `"crowd"`)・`_curfew_suppressed`(`"curfew"`)・`_media_action`(`"media"`)が
  確立した「専用 stream+既定OFFで draw 順を汚さない」作法の踏襲。既存 routine の乱数(`choose_destination` 等)は**既定 stream のまま触らず**、
  ①の摂動だけを新 stream に載せる(=OFF 時バイト一致を保証)。
- **偶発的遭遇は物理から創発**(主計画者の指摘は正しい): ①が経路・滞在・時刻をゆらすと、`hearers_of`(空間索引)経由で
  知り合いとの同位置確率が自然に変わる。①は遭遇を直接生成せず、**遭遇の分布を非決定化する**だけ。これが C2(§4.3)の入力になる。
- **コスト**: LLM **0**。エンジン=agent-step あたり乱数 0〜数本追加(既定OFFなら0)。イベント量=`detour`/`interrupt` を任意で記録するなら
  在場25万×~40%×~1-2機会/日 ≈ 100万〜200万 event/日(既存の route_start/move_segment の桁に対し軽微・構造化payload)。
- **R1**: 入力は物理量・時刻・活動種別のみ(beliefs/k を見ない)。新 stream は既存 draw 順を汚さない。no-fingerprint(routine は因子名を知らない・地名は envpack)。

### 4.2 ②ナラティブ補間 — 採用(二段分離)
**主計画者の案**: イベントログから「計画との差分+会った人+起きたこと」を機械圧縮したダイジェスト(LLM0)を各 LLM 推論プロンプトに注入。
夜内省がダイジェストを一人称の物語記憶に変換。

**批判と改良**:
- **正しい。ただし「圧縮」を過度にしない**(§3.3 の書き込み時要約の罠)。ダイジェストは**意味づけをせず客観カウント/列挙に留める**。
  意味の付与(なぜ印象に残ったか・自分がどう動いたか)は**夜内省の LLM の仕事**(既存 `_REFLECT_TASK` が既にこれを問うている)。
- 実装 seam は**既存 `digest_line` と完全に同型**。`build_prompt` に `interstitial_digest: str | None = None` を追加
  (既定 None=1行も足さない=バイト一致)。`date_line`/`weather_line`/`schedule_line`/`digest_line` と同じ注入場所。
- **ダイジェストの生成源**: 各 LLM 発火時に、`engine` がその個体の**前回 LLM 発火以降のイベントログ**(move/arrive/speak/hear/
  spend/appointment/C2会話 等)を決定論的に走査し、テンプレで数行に整形。例:

  ```
  この間のこと: 朝の予定「センター街で買い物」は済ませた。宮下公園にも寄った。
  田中さんと立ち話をした(挨拶)。雨で人が少なかった。
  ```
- **物語化は夜内省**: 夜の `maybe_reflect` が1日分のダイジェスト+salient episode を受け、既存の summary/belief に加えて
  「一人称の物語」を紡ぐ(プロンプト微修正のみ・**追加呼なし**)。物語は day_summary として consolidate され、翌日以降の
  `recent`/`retrieve` に載る。

- **コスト**: LLM **0**(追加呼なし)。プロンプト長 +2〜4行(token-budgets.md によれば入力は律速でないので影響軽微)。
  エンジン=発火時にイベントログ走査(個体あたり前回発火以降の ~10-15 step 分。row-group 局所)。イベント量=補間そのものは
  イベントを増やさない(既存ログの読み出しのみ)。任意で `interstitial_digest` を 1 event/発火として残すなら 25万×8=200万/日。
- **R1**: ダイジェストは客観イベントのみ入力(beliefs/k を見ない)。乱数不使用=決定論(ON同士2回一致テスト)。
  既定 None=バイト一致。no-fingerprint(テンプレに因子名/地名リテラルを置かず envpack 経由)。

### 4.3 ③会話3層 — 全面採用+精緻化
**主計画者の案**: C1=重要会話フルLLM / C2=構造化会話(LLMなし・話題/スタンス/トーン/帰結を状態から決定論生成・関係値/意見(FJ)/語彙接触に
機械効果・イベント記録)/ C3=挨拶・すれ違いは集計のみ。C2→C1 昇格あり。将来 C2 の一部を小型モデル。

**批判と改良**(§3.1 の軽量会話文献で全面的に裏づけ):
- **C2 の設計図は既に文献にある**: Dialogue Acts(挨拶→話題提示→スタンス表明→同意/反論→別れ)を有限状態機械 or 決定論遷移で回し、
  中身は生成しない(§3.1)。話題・スタンス・帰結は両者の状態(関係 tier・意見ベクトル・共有語彙・気分)から決定論写像。
- **C2 の機械的効果**は既存資産で全部揃う: 関係更新(`relations.py`)・意見更新(`opinion.py` の FJ)・語彙接触
  (`labeling/labels.py` の complex contagion 2回)・drive ゲージ加算(`drive.add(agent,"addressed")`)。C2 はこれらを
  **LLM 発話なしで駆動する薄いオーケストレータ**。
- **C2 の発火**: `_phase_drive` とは別の新フェーズ `_phase_c2`(既定OFF)。空間索引 `hearers_of` で「近くに知り合いがいて、
  双方が会話可能(sleeping でない・cooldown 明け)」の対を決定論列挙し、専用 stream `c2_meet` で会話成立を抽選。
  会話成立したら Dialogue Act 列を決定論生成し、上記の機械効果を適用、`conversation` イベント(新kind)を1件記録。
- **C2→C1 昇格**(顕著性ゲート接続): C2 の帰結が「強い意見差・関係の転機・未知語の接触・地位変化」を含むとき、
  `drive.add` でゲージを押し上げる。ゲージが閾値超えれば既存 `_phase_drive` が**その相手への C1 発話(フルLLM)**を発火。
  = C2 は「会話の大量の下地」、C1 は「その中で顕著な会話だけ LLM で肉付け」。これが Lyfe の option-action・OASIS の確率活性化と同型。
- **C3**: 挨拶・すれ違いは会話イベントすら作らず、**日次カウンタ**(「今日 N 人とすれ違った」)のみ。集計は L2 の非LLM後処理。
  C3 は②のダイジェストに「人混みだった/閑散としていた」の材料を供給する。
- **将来の C2 小型モデル化**: EcoLANG(§3.1・語彙圧縮-20%)+ w2 §1.5(a) の qwen3-1.7b 級ブラインドA/B が採用条件。
  本ラウンドは C2=完全 LLM無しで実装し、小型モデルは後続の条件付き実験(過去の「<2B不採用」の再訪)。

- **データモデル統一**(軽量会話文献の鍵所見): AGA の関係 0-10 スコアを共通表現にし、エージェントを **C3↔C2↔C1 で昇格/降格**させる。
  既存 `relations.py` を 0-10 正規化に合わせれば、3層が1つの関係台帳を共有する。
- **コスト**: C1=既存の日中熟慮に含まれる(新規呼なし)。C2/C3=LLM **0**。エンジン=C2 は対の列挙(空間索引の近傍走査、既存 `hearers_of` を再利用)
  +数本の numpy 更新/会話。イベント量=**C2 が主レバー**(§6 で試算。~5〜30 会話/人日 → 125万〜750万 event/日、構造化 payload で軽量)。
- **R1**: C2 の話題/スタンスは状態の決定論写像(乱数は会話成立の抽選=新 stream `c2_meet` のみ)。意見更新は既存 FJ(k非依存)。
  既定OFF=`conversation` イベント0件=バイト一致。no-fingerprint(C2 オーケストレータは opinion/relations の不透明値のみ扱う)。

### 4.4 第4機構(新提案)— 好奇心/退屈ドライブ + AGA Lifestyle Policy
主計画者の①②③は「間隙を**埋める**」機構だが、2つの見落としがある。

**(4-a) 好奇心/退屈の内発ドライブ**(ユーザーの「自然界を模した仕組み」志向・ボトムアップ創発と整合):
- ①は計画からの**外挿的**ゆらぎ(遅延・寄り道)だが、「**計画にない行動を内側から生む**」機構がない。現実の間隙は
  「手持ち無沙汰→SNS を見る/ふらっと歩く/知らない店に入る」といった**内発的探索**で埋まる。
- 既存 `drive.py` は既に `silence`(沈黙の継続で微増)を持つ。これを**好奇心/退屈の明示ドライブ**に拡張:
  「同じ場所に長居・単調な入力が続く」と退屈ゲージが溜まり、閾値超えで**探索行動**(近傍の novel_place へ移動・SNS 閲覧・
  知らない店に入る)を**LLM なしで**発火。novel_place 到達は既存 drive の鋭敏化(reflection-drift.md の脱馴化)に接続し、
  そこで顕著性が上がれば C1 熟慮へ。= ボトムアップに「何かが起きる」種を撒く。
- 文献接地: Loewenstein の情報ギャップ好奇心(reflection-drift.md で既に参照)・内発的動機(SDT、既存 `factors/psych`)。
- コスト: LLM 0(探索の**発火**は機械層。到達先で顕著性が上がれば既存予算内で C1)。新 stream `boredom`。既定OFF。

**(4-b) AGA Lifestyle Policy キャッシュ**(「6→21.6」への直接回答の主レバー):
- §2.7 の通り、行動系列を embedding 近傍+実行条件でキャッシュ再利用し、**朝計画・日中熟慮の LLM 呼を 40〜57% 削減**できる
  (25人町で 42.7%)。Agentic Plan Caching(§2.9)も類似タスク間で **コスト -50%・レイテンシ -27%** を報告。
  削減で浮いた GPU 予算を**より多くの日中熟慮**に回せば、同一ハードで実効呼数を増やせる。
- これは compute-optimization.md の E2-2(routine caching)の一般化。**採用条件は同一**: 再利用ゲートが決定論・k非依存、
  distinct-n/行動レパートリー曲線が痩せない(ポリシー汚染で観察対象の稀な逸脱=世界改変者を潰さないこと)。
- **背景個体限定**を推奨(前景=フルLLM で k* を測る/背景=キャッシュ再利用で街を充填。分布一致検定が採用条件。
  compute-optimization E3 と同じ関門)。

---

## 5. 設計推奨とコスト試算(呼数/日・エンジン・イベント量)

在場25万・予算~200万呼/日の下での各機構のコスト。**基準**: 全員思考の現状 = 朝計画25万+夜内省25万+日中熟慮~150万 = **~200万呼/日**。

| 機構 | LLM呼数/日への影響 | エンジンコスト | イベント量/日 | 密度への効き |
|---|---|---|---|---|
| ①確率的実行 | **0** | 乱数 0〜数本/agent-step(既定OFF=0) | detour/interrupt 任意 ~100〜200万(既存の route系より軽微) | 行動の非決定化(遭遇分布を変える) |
| ②ナラティブ補間 | **0**(プロンプト +2〜4行) | 発火時にイベントログ局所走査 | 補間自体は0(任意 digest event ~200万) | 認知の連続性(全LLM呼が一日の物語を見る) |
| ③-C1 フルLLM | 既存の日中熟慮に内包(新規0) | 既存 | 既存 speak | 既存 |
| ③-C2 構造化会話 | **0** | 対の近傍列挙+数本numpy/会話 | **~125万〜750万**(構造化payload・軽量) | **記録に残る会話数の主レバー** |
| ③-C3 挨拶集計 | **0** | カウンタ加算のみ | 0(日次カウンタ) | ②へ材料供給 |
| ④-a 好奇心ドライブ | **0**(到達先で既存予算内C1) | drive ゲージ1本 | 探索移動は既存 move | ボトムアップ創発の種 |
| ④-b AGA キャッシュ | **-40〜57%**(浮いた分を熟慮増に転用可) | embedding近傍検索+条件判定 | 0 | **実効LLM呼を増やす回収策** |

**「6→21.6 に近づける」の定量シナリオ**(A5000×7・prefix cache 実効 ~38req/s 前提。P7 実測で置換):
- 現状: 日中熟慮 ~150万呼 = ~6/人日 = ~9-11h。
- + speculative decoding(E1-1・無損失2.8x): 同一 wall 時間で ~2.8倍の呼が可能 → 日中 ~6→~16/人日 圏内(要実測)。
- + AGA キャッシュ(背景個体で呼-40%): 浮いた予算を前景近傍の熟慮に集中 → 前景近傍は 200体密度(21.6)へ接近、背景は薄いまま。
- 結果: **「顕著性の高い個体(組織形成核・ファウンダー前駆・その近傍)は ~20/人日(200体密度相当)、静かな個体は薄い」**という
  w2 §1.5 の「現実の注意配分と同型」を、density の絶対値を上げつつ実現。**一様に21.6にするのは予算的にも研究的にも不適切**
  (k掃引の交絡・注意配分の非現実性)。目標は「**観察対象で21.6相当・全体平均は予算内**」。

---

## 6. 「記録に残る認知・社会イベント数/人日」の試算

現実(Mehl の EAR: 数十回の相互作用/日)にどこまで近づくか。1人・1シミュ日の**記録に残るイベント**を積算:

| 種別 | 機構 | 件数/人日(概算) |
|---|---|---:|
| 朝計画 | LLM | 1 |
| 夜内省(物語化) | LLM(②) | 1 |
| 日中の顕著性熟慮(C1 発話・投稿・DM・造語) | LLM | ~6 |
| **C2 構造化会話** | ③(LLM0) | **~5〜30**(在場密度・知人数依存) |
| 予定の設定(会話由来) | 既存 schedule(LLM0) | ~0.5 |
| 寄り道 detour/中断 | ①(LLM0) | ~1-2(実証: 1日の~44%が立ち寄りを含む) |
| 探索行動(退屈ドライブ) | ④-a(LLM0) | ~1-2 |
| **記録に残る認知・社会イベント計** | | **~15〜43/人日** |
| (参考)C3 すれ違い | ③(日次カウンタのみ) | 数十〜数百(集計値) |

- **現実の「数十回の会話」に、C2 を主レバーとして到達する**。LLM 生成の会話は ~6/日に留まるが、
  **記録に残る会話・相互作用の総数は 15〜42/日**で現実レンジに入る。質の内訳は「大半が構造化(C2)、要所が LLM(C1)」で、
  これは AGA(削減しても believability 不変)・AgentSociety(500相互作用/体日の大半が軽量)の先行知見と整合。
- **C2 件数の制御**: `c2_meet` の成立確率と cooldown で調整。5/日(控えめ)〜30/日(密)を conf 掃引可能。
  在場密度(昼ピーク37.2万)では知人との同位置機会が多く、上限側に振れる。イベント量とのトレードオフ(§5)で決める。
- **honest note**: C2 は「会話の**型と帰結**の記録」であって逐語のテキストではない。「将来的に何気ない会話もシミュレーション」
  (ユーザー要望4)の完全形は C2 の小型モデル実文生成(§4.3 の後続実験)。本ラウンドは「記録に残る/機械効果は本物/テキストは要所のみ」。

---

## 7. R1ドクトリン整合確認

R1 = **①新機能=新streamのみ ②既定OFFでゴールデンL1バイト一致 ③呼数はk非依存(k-blind) ④no-fingerprint**
(出典: w2 §2、schedule-book-spec §0)。各機構を全数確認:

| 機構 | 新streamのみ | 既定OFF=バイト一致 | 呼数k非依存 | no-fingerprint |
|---|---|---|---|---|
| ①確率的実行 | ✅ `jitter_depart`/`jitter_route`/`detour`/`interrupt` の4本。既存draw順不変(crowd/curfew/media と同作法) | ✅ enabled=false で乱数を一切引かない | ✅ 入力は物理量・時刻のみ(beliefs/k を見ない)。LLM呼を増減しない | ✅ routine は因子名を知らない・地名は envpack 経由 |
| ②ナラティブ補間 | ✅ 乱数不使用(決定論パーサ) | ✅ `interstitial_digest=None` で1行も足さない(digest_line と同型) | ✅ 追加LLM呼ゼロ。ダイジェストは既存ログ読み出し | ✅ テンプレに構成概念名を置かない・地名 envpack |
| ③-C2/C3 | ✅ `c2_meet` の1本のみ(会話成立の抽選) | ✅ enabled=false で `conversation` イベント0件 | ✅ C2はLLM呼を増やさない。C2→C1昇格は既存drive経由(kと無関係な観測量) | ✅ C2は opinion/relations の不透明値のみ・因子名なし |
| ④-a 好奇心 | ✅ `boredom` の1本 | ✅ enabled=false でゲージ据置 | ✅ 発火は機械層。到達先C1は既存予算内 | ✅ drive は reason 文字列のみ見る |
| ④-b AGAキャッシュ | ⚠️ embedding近傍は乱数でないが**キャッシュヒットで呼が減る**=呼数がキャッシュ状態依存 | ✅ enabled=false で常にLLM生成 | ⚠️ **要注意**: キャッシュゲートがk依存量(beliefs)を見ると呼数がkで乖離。→**ゲート入力を物理量・計画テキストのみに限定**し、k非依存を担保(compute-optimization E2-2/E3 の採用条件と同一)。前景/背景の割当はk非依存・決定論固定 | ✅ ゲートは因子名を見ない |

- **最大の注意点は④-b**: キャッシュ再利用は呼数を状態依存に変えるため、R1(呼数k非依存テスト)を通すには
  **再利用ゲートの入力から k 由来量(beliefs・writeback成否・Y_internal)を完全排除**し、物理量・計画骨格・環境条件のみにする。
  reflection-drift.md §3 の R1 監査(k∈{free,off} で n_fires ±20%)と同じ検証を、**呼数**についても行う
  (`tests/test_aga_cache` 相当で k による呼数乖離がないことを固定)。通らない設計なら見送り(compute-optimization の姿勢に従う)。
- ①②③-C2/C3・④-a は R1 に自然に収まる(既存の crowd/curfew/media/schedule/digest_line が確立した作法の踏襲)。

---

## 8. 実装の入口(seam の所在・実装は別バッチ・要ユーザー承認)

> 本書は設計文書。実装着手前に pre-coding-alignment(決定アジェンダ提示→ユーザー合意)が必要。

| 機構 | 主な編集/新規ファイル | 既存の同型前例 |
|---|---|---|
| ① | `cognition/routine.py`(`_plan_move`/`decide` に4 stream)・`conf` の `routine.jitter` ブロック | `_crowd_dest`/`_curfew_suppressed`/`_media_action` |
| ② | `cognition/deliberate.py::build_prompt`(`interstitial_digest` 引数)・`engine/scheduler.py`(発火時のログ走査→整形)・`reflection.py`(物語化プロンプト) | `recursion.py::digest_line`・`schedule.py` |
| ③ | 新規 `conversation.py`(C2 オーケストレータ+Dialogue Act遷移)・`engine/scheduler.py`(新 `_phase_c2`)・`observer/schema.py`(`conversation` kind 登録)・`relations.py`(0-10正規化) | `schedule.py`・`_phase_drive`・`opinion.py`(FJ) |
| ④-a | `cognition/drive.py`(boredom ドライブ)・`routine.py`(探索発火) | `drive.add(...,"silence")`・reflection-drift の脱馴化 |
| ④-b | 新規 `policy_cache.py`(embedding近傍+条件判定)・`planning.py`/`_phase_drive`(キャッシュ照会) | compute-optimization E2-2/E3(要 blind A/B) |

- 検収は毎回 **フルpytest green + 既定OFFゴールデンL1バイト一致 + mock ≤24step スモーク**(validation-runs-short 準拠・実LLMフルランはしない)。
- 実装優先度の目安: ②(最も安全・即効・前例完備)→ ③-C2/C3(密度の主レバー)→ ①(非決定化)→ ④-a(創発の種)→ ④-b(要 blind A/B・条件付き)。

---

## 9. 出典一覧(URL・APIキー/シークレットは一切含まない)

**先行 LLM 社会シミュ**
- Generative Agents (Park+ 2023): https://arxiv.org/abs/2304.03442
- Concordia (DeepMind 2023): https://arxiv.org/abs/2312.03664 / repo https://github.com/google-deepmind/concordia
- Project Sid / PIANO (Altera 2024): https://arxiv.org/abs/2411.00114 / repo https://github.com/altera-al/project-sid
- AgentSociety (2025): https://arxiv.org/abs/2502.08691
- OASIS (2024): https://arxiv.org/abs/2411.11581 / repo https://github.com/camel-ai/oasis
- Lyfe Agents (2023): https://arxiv.org/abs/2310.02172
- Humanoid Agents (2023): https://arxiv.org/abs/2310.05418
- **Affordable Generative Agents (AGA, TMLR 2024)**: https://arxiv.org/abs/2402.02053 / html https://arxiv.org/html/2402.02053v1 / https://openreview.net/forum?id=7tlYbcq5DY
- Concordia v2(game engine, 2025): https://arxiv.org/html/2507.08892v1

**スループット/スケール手法**
- AI Metropolis(out-of-order execution, MLSys 2025): https://proceedings.mlsys.org/paper_files/paper/2025/file/4f31327e046913c7238d5b671f5d820e-Paper-Conference.pdf
- Agentic Plan Caching (2025): https://arxiv.org/abs/2506.14852
- AgentTorch / LLM Archetypes(AAMAS 2025・全員思考との緊張): https://arxiv.org/html/2409.10568v1

**軽量/LLMなし会話・意見力学・拡散**
- EcoLANG (EMNLP 2025 Findings): https://arxiv.org/abs/2505.06904 / https://aclanthology.org/2025.findings-emnlp.284/
- Agenda-Based User Simulator (Schatzmann+ 2007): https://aclanthology.org/2007.sigdial-1.48.pdf
- Hidden Agenda Model (Schatzmann & Young 2009): http://mi.eng.cam.ac.uk/~sjy/papers/scyo09.pdf
- 話題×スタンス ABM 会話 (EPJ Data Science 2025): https://link.springer.com/article/10.1140/epjds/s13688-025-00593-3
- 実データ較正 SNS 会話 (2025): https://arxiv.org/html/2509.18985v2
- 意見・関係 共進化 ABM: https://arxiv.org/html/2407.00145v2
- bounded confidence サーベイ (Automatica 2023): https://www.sciencedirect.com/science/article/pii/S0005109823004661
- FJC (Friedkin-Johnsen on Cascade, 2025): https://arxiv.org/abs/2506.16302
- 情報拡散×LLM (MDPI Systems 2025): https://www.mdpi.com/2079-8954/13/1/29

**記憶・エピソード・要約**
- Position: Episodic Memory is the Missing Piece (2025): https://arxiv.org/pdf/2502.06975
- Beyond Static Summarization: Proactive Memory Extraction (2026): https://arxiv.org/pdf/2601.04463
- Memory for Autonomous LLM Agents サーベイ (2026): https://arxiv.org/html/2603.07670v1

**活動ランダム性・人間移動・計画からの逸脱**
- Song et al., Limits of Predictability in Human Mobility (Science 2010・予測可能性93%/R≈0.7): https://www.science.org/doi/10.1126/science.1177170
- Schneider et al., Unravelling daily human mobility motifs (J.R.Soc.Interface 2013・17 motif で90%): https://royalsocietypublishing.org/doi/10.1098/rsif.2013.0246
- MATSim TimeAllocationMutator(±30分・一様分布・doxygen): https://www.matsim.org/doxygen/classorg_1_1matsim_1_1core_1_1config_1_1groups_1_1_time_allocation_mutator_config_group.html
- Susilo & Axhausen 2014, Repetitions in individual daily activity (HHI・活動種別反復率): https://link.springer.com/article/10.1007/s11116-014-9519-4
- day-to-day variability(個人内変動38-50%): https://link.springer.com/article/10.1007/BF00165547
- A Theory of Unplanned Travel Decisions(トリップの44.3%が計画外立ち寄り): https://www.researchgate.net/publication/220542959_A_Theory_of_Unplanned_Travel_Decisions_Implications_for_Modeling_On-the-Go_Travelers
- POPAI 2014(購買決定76%が店内): https://www.en.nvc.nl/news/item/popai-76-purchase-decisions-made-in-store/
- Bhat, Activity-Based Modeling handbook chapter(ランダム効用・Gumbel): https://www.caee.utexas.edu/prof/bhat/abstracts/tshandbk.pdf

**現実の会話頻度**
- Mehl ら EAR 研究(会話頻度・語数): https://news.arizona.edu/news/are-we-talking-less-qa-psychologist-matthias-mehl

**自プロジェクト内部参照**
- w2-execution-plan §1(全員思考・予算検算): `docs/plans/w2-execution-plan.md`
- token-budgets.md(AGA/Sid/AgentSociety のトークン相場・decode支配): `docs/research/token-budgets.md`
- compute-optimization.md(speculative decoding・routine caching・archetype の危険): `docs/plans/compute-optimization.md`
- memory-cognitive-research.md(ACT-R 活性化・想起失敗): `docs/research/memory-cognitive-research.md`
- reflection-drift.md(馴化/鋭敏化・好奇心ドライブの接地): `docs/research/reflection-drift.md`
- schedule-book-spec.md(R1 作法・決定論パーサの前例): `docs/design-candidates/schedule-book-spec.md`
