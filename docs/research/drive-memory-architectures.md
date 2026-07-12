# 調査レポート: 欲求ゲージ発火アーキテクチャ + 記憶検索スコアリング/統合

対象設計:
- **欲求ゲージ**: 出来事でゲージが溜まり、個人別閾値超過で「申請」→ 申請時に個人重み(確率)で発火、不発ならゲージを数十%減衰させて重い推論(LLM呼び出し)を分散発火。
- **記憶**: Generative Agents 型 push 想起(recency×importance×relevance)+ 就寝時統合(要約・重要度採点・信念抽出)。ただし**埋め込み無し・非LLM想起・就寝時1回のLLM統合**という制約。

調査日: 2026-07-04 / 一次資料(公式論文・公式GitHub)優先。値の確度は「確認/未確認」を明記。

---

# RQ1: 欲求・動機による推論発火のアーキテクチャ

## 1-1. PSI理論 / MicroPsi (Dörner, Bach) — urge/motive の数理

**確認できた機構(概念レベルは確度高、具体数式は書籍/PDFに封じられ一部未確認):**

- **Demand(需要)→ Urge(衝動)→ Motive(動機)** の三段。Demand は目標セットポイントからの逸脱を表す内部変数。**Urge の強さ ∝ demand の逸脱量**(ホメオスタシス誤差信号)。時間経過・出来事で demand が満たされないと urge が増大、消費行動(consummatory event)で減少。[Psi-theory Wikipedia](https://en.wikipedia.org/wiki/Psi-theory)
- Demand の3系統: **生理**(energy/食/水、integrity=痛み回避)、**認知**(competence=有能感、certainty=不確実性低減、aesthetics)、**社会**(affiliation=親和、legitimacy/honor)。
- **Motive = urge + 目標/対象 + expectancy(達成見込み)**。支配的動機の選択は「**関連 urge を満たせる予測確率 × urge 信号の強さ**」で決まる = **期待価値(expectancy-value)ランキング**。[Dörner & Güss 2013, PSI: A Computational Architecture](https://journals.sagepub.com/doi/10.1037/a0032947)
- **Selection threshold(選択閾値)モジュレータ = ヒステリシス/不応期の理論的根拠(重要)**: 「現在の動機を保護し、**ライバル動機の強度が『現動機の強度+閾値』を超えない限り交代しない**」= フラッタリング(頻繁な切替)防止。この閾値は「**demand の緊急度 + 個体差(individual variance)に依存**」と明記されている → **我々の「個人別閾値の個体差分布」と「不応期」を同時に接地できる一次概念**。[検索確認: Modeling Motivation in MicroPsi 2, Bach 2015](https://agi-conf.org/2015/wp-content/uploads/2015/07/agi15_bach.pdf) / [Principles of Synthetic Intelligence, Bach 2009](https://archive.org/details/principlesofsynt0000bach)
- **モジュレータ4種**: arousal(覚醒/活性)、resolution level(認知の解像度=熟考の深さ)、selection threshold(現目標への固執度)、securing rate/sampling rate(環境チェック頻度)。demand の緊急度と competence で動的調整。
- **数式レベルの確度**: urge の leaky-integrator 減衰係数やゲインの**具体値は未確認**(Bach 2015 PDF はバイナリで本文抽出失敗、書籍 Bach 2009 に散在)。代替根拠として下記 LIF と GA の減衰桁を採用推奨。

## 1-2. BDI — desire→intention 昇格 / 熟考(deliberation)の起動条件

- BDI の熟考: option 生成(**desires**)→ フィルタリング → **intention** 確定。核心は「**intention reconsideration(再考をいつ起動するか)**」= メタレベル制御。[Schut & Wooldridge, Principles of Intention Reconsideration](https://www.cs.vu.nl/~schut/pubs/Schut/2001.pdf)
- **Bold vs Cautious(Kinny & Georgeff 1991)**: cautious=毎ステップ再考、bold=現プランを完遂するまで再考しない。**静的/変化の遅い環境では bold が優位、動的環境では cautious が優位**。→ 規範的含意: **世界の変化率が高いときだけ熟考(=LLM発火)頻度を上げる**。[Schut & Wooldridge, Intention Reconsideration as Discrete Deliberation Scheduling](https://www.cs.vu.nl/~schut/pubs/Schut/2001a.pdf)
- 「再考=離散的な deliberation scheduling 問題」として定式化(いつ計算資源を熟考に割くか)。我々のゲージ機構は、この「再考起動」を**確率的閾値ゲート**で近似したものと位置づけられる。

## 1-3. OCC appraisal / EMA / FAtiMA — 出来事→感情強度→行動傾向

- **OCC 22感情**。appraisal 変数: **desirability**(出来事 vs 目標)、**praiseworthiness**(行為者 vs 規範)、**appealingness**(対象 vs 好み)。[Bartneck, Integrating the OCC Model](https://www.bartneck.de/publications/2002/integratingTheOCCModel/bartneckHF2002.pdf)
- **感情強度のグローバル変数**: sense of reality, proximity(心理的近さ), **unexpectedness(予想外さ=サプライズ)**, arousal(覚醒)。appraisal→感情の連合重みは **[-1,1]**。→ **「サプライズ」「近接性」「覚醒」がゲージ入力の候補として理論的に正当化される**。
- **EMA(Marsella & Gratch 2009)**: appraisal frame の次元 = relevance, desirability, **likelihood**, expectedness, causal attribution, controllability, changeability。**感情強度 ≈ desirability × likelihood** の形。coping(problem-focused / emotion-focused)を経て**行動傾向(action tendency)**へ写像。[EMA: A process model of appraisal dynamics](https://cs.uky.edu/~sgware/reading/papers/marsella2009ema.pdf) / [Computational Models of Emotion (review), Marsella-Gratch-Petta](https://people.ict.usc.edu/gratch/public_html/papers/MarGraPet_Review.pdf)
- **FAtiMA**: FearNot 由来のモジュール型。appraisal 変数の計算に**シナリオ固有の事前ルール**を使う(ドメイン依存)。→ 我々も「出来事タイプ→重要度/感情」の軽量ルール表を持つ設計と親和。[Steunebrink, Formal Model of Emotion-based Action Tendency](https://people.idsia.ch/~steunebrink/Publications/EPIA09_action_tendency.pdf)

## 1-4. Generative Agents (Park 2023) の reflection トリガー — 正確な仕様(確認済)

一次資料 [arXiv:2304.03442](https://arxiv.org/abs/2304.03442) / [ar5iv 全文](https://ar5iv.labs.arxiv.org/html/2304.03442) + [公式GitHub joonspk-research/generative_agents](https://github.com/joonspk-research/generative_agents):

- **トリガー: 「直近に知覚した出来事の importance スコアの総和が閾値を超えたら reflection」。閾値 = 150(論文実装)**。実装コードでは `importance_trigger_curr` が出来事の重要度分だけ**減算されて 0 以下**になったら発火し、`importance_trigger_max` に**リセット**(= 累積のカウントダウン方式)。`reflect.py` 確認。
- 頻度: **1日およそ2〜3回**。
- 対象: **直近100件**のメモリレコード → **高レベル質問を3つ生成** → 各質問で検索 → **洞察を5件合成**(証拠ID引用付き)。
- (プロンプト文面は RQ2-2 に転記)
- **importance_trigger_max のコード既定の具体数値は未確認**(persona ごとに設定、論文本文は 150)。

## 1-5. metacontrol / cognitive effort 配分 — EVC (Shenhav 2013)

- **Expected Value of Control**: 制御(熟考)を割り当てるか否かを規範的に決める。**EVC = Σ P(outcome|control)·Value(outcome) − Cost(認知的努力)**。**期待便益が努力コストを上回るときだけ選択的に制御を動員**。dACC がこれを計算。[Shenhav, Botvinick & Cohen 2013, Neuron 79:217-240](https://www.cell.com/neuron/fulltext/S0896-6273(13)00607-7)
- 我々への含意: **「LLM発火=コストの高い制御動員」なので、期待便益(重要度×達成見込み)がコストを超えると期待されるときに確率的に発火」という設計は EVC で規範的に正当化される**。発火確率を `p ∝ logistic(EVC)` で表せる。

## 1-6. LLMエージェントの内発的動機・欲求起動(2024–2026)

- **D-MEM: Dopamine-Gated Agentic Memory via Reward Prediction Error Routing** — 「**内部予測モデルを裏切る入力(=RPE/サプライズ)だけがメモリ更新を起動**」。ドーパミン系の予測誤差ゲーティングの模倣。→ **サプライズ/新規性をゲージ入力にする直接の実装先例**。[arXiv:2603.14597](https://arxiv.org/pdf/2603.14597)
- **LLM-Driven Intrinsic Motivation for Sparse Reward RL**(好奇心/新規状態探索を内発報酬に)。[arXiv:2508.18420](https://arxiv.org/html/2508.18420v1)
- **MAGELLAN**(learning progress のメタ認知予測で autotelic に目標選択)。[arXiv:2502.07709](https://arxiv.org/pdf/2502.07709)
- **IMAGINE / Navigate the Unknown**(内発動機ガイドの探索報酬)。[arXiv:2505.17621](https://arxiv.org/html/2505.17621v6)
- 生物模倣の閾値・不応期の直接根拠 → **Leaky Integrate-and-Fire (LIF)**: 入力を積分し `V > 閾値` で発火、発火後 `V` をリセット、**絶対不応期(absolute refractory period)中は入力に関係なく発火不可**。最大発火率を制限。リセットは reset-to-zero か減算式(`V -= 閾値`)。[LIF+refractory, npj 2024](https://www.nature.com/articles/s44335-024-00013-1) / [NYU LIF notes](https://www.cns.nyu.edu/~eorhan/notes/lif-neuron.pdf)

## 【RQ1 成果物】欲求ゲージ設計への含意(表)

### (A) ゲージ入力候補と相対重み(接地根拠つき)

| 入力(ゲージを増やすもの) | 接地根拠 | 推奨相対重み | 備考 |
|---|---|---|---|
| **出来事の重要度/poignancy(1-10)** | GA importance | **高(基準1.0)** | LLM採点 or 軽量ルール |
| **サプライズ/新規性/予測誤差** | OCC unexpectedness; D-MEM(RPE); 内発好奇心 | **高(0.8-1.2)** | 予測外の出来事は熟考価値が高い |
| **自己目標との関連/desirability** | OCC desirability; MicroPsi 期待価値; EMA | **高(0.8-1.0)** | 目標に効く出来事を優先 |
| **社会的顕現性(重要他者の在/親和欲)** | MicroPsi 社会demand(affiliation) | 中(0.4-0.7) | 渋谷=対人接触が主イベント源 |
| **感情覚醒(arousal)** | OCC arousal; EMA | 乗数(×1.0-1.5) | 加算でなく全体を増幅する乗数が自然 |
| **前回熟考からの経過/微小出来事の蓄積** | leaky integrator; EVC 機会コスト | 低ベース(0.05-0.2/tick) | 「何もなくてもいつか考える」ドリップ |

> 重み付き和 `gauge += Σ w_i·x_i`(arousal だけ乗数)を推奨。GA が実装で relevance>importance>recency の順(後述 3:2:0.5)にしていることと整合的に、「**目標関連×サプライズ**を最上位、単なる時間経過を最下位」に。

### (B) 減衰の桁

| パラメータ | 推奨値 | 根拠 |
|---|---|---|
| **常時リーク(ambient leak)** | 約 **0.5–2%/時**(係数 0.98–0.995) | GA recency 0.99–0.995/時 |
| **不発時の減衰(申請したが発火せず)** | **30–50%(乗算 ×0.5–0.7)** | 「数十%」= LIF の部分リセットと full-reset の中間。完全放電(=毎回LLM)は避けたいので部分リセット |
| **発火成功時のリセット** | **大(70–100%)** or 減算式 `−閾値` | LIF reset。連続再発火を防ぐ |

### (C) 閾値の個体差分布の形

- MicroPsi の selection threshold は「**緊急度 + 個体差**」で変動(定性確認)。**個体差分布の canonical な特定形は未確認**。
- **推奨**: 閾値 `θ_i ~ TruncatedNormal(μ, σ)`(θ>0)を第一候補。正の歪みを入れたいなら `LogNormal` か `Gamma`。個体差の大きさ σ は「同一集団内で発火頻度が数倍ばらつく」程度(σ/μ ≈ 0.2–0.4)を初期値に。**理由**: 心理特性は集団内でほぼ正規、レート/閾値系パラメータは対数正規で近似されることが多い(標準的モデリング慣行)。
- 発火の**個人重み(確率)**は閾値と独立に、`p_i = logistic(k·(gauge−θ_i))` の傾き `k` と基準率で表現(EVC/ノイズ付き閾値の soft-WTA 近似)。

### (D) 不応期の根拠と推奨

| 種別 | 根拠 | 推奨 |
|---|---|---|
| **絶対不応期** | LIF absolute refractory | 発火後 N tick は再申請不可(N は個体差) |
| **相対不応期(ヒステリシス)** | MicroPsi selection threshold; BDI bold commitment | 発火直後は閾値を一時的に上げ、時間で元に戻す。頻繁な再熟考(フラッタリング)防止 |
| **環境依存の調整** | Kinny & Georgeff(動的環境ほど cautious) | 周囲の変化が激しい局面では不応期を短縮 |

---

# RQ2: 記憶検索スコアリングと統合の具体仕様

## 2-1. Generative Agents 検索式 — 正確な仕様(論文 vs 公式コードの差を明記)

### 論文の式(確認済) [ar5iv 全文](https://ar5iv.labs.arxiv.org/html/2304.03442)
```
score = α_recency · recency + α_importance · importance + α_relevance · relevance
論文: α_recency = α_importance = α_relevance = 1  (すべて等重み)
```
- **recency**: 「記憶が最後に取得されてからのサンドボックス内ゲーム時間」に対する**指数減衰、減衰係数 0.995**。
- **importance**: LLM が **1–10** で採点。プロンプト(原文): *"On the scale of 1 to 10, where 1 is purely mundane (e.g., brushing teeth, making bed) and 10 is extremely poignant (e.g., a break up, college acceptance), rate the likely poignancy of the following piece of memory."*
- **relevance**: 記憶テキストの埋め込みと**クエリ埋め込みの余弦類似度**。
- **正規化**: recency, importance, relevance を各々 **min-max スケーリングで [0,1]** に。

### 公式GitHub 実装の実値(確認済・論文と乖離あり=重要)
[retrieve.py](https://github.com/joonspk-research/generative_agents/blob/main/reverie/backend_server/persona/cognitive_modules/retrieve.py) / [scratch.py](https://github.com/joonspk-research/generative_agents/blob/main/reverie/backend_server/persona/memory_structures/scratch.py):
```python
# scratch.py 既定値
recency_w = 1 ; relevance_w = 1 ; importance_w = 1
recency_decay = 0.99            # 論文は 0.995、コード既定は 0.99

# retrieve.py
recency_vals = [recency_decay ** i for i in range(1, len(nodes)+1)]  # ← 時間でなく「順位 i」に対する減衰
recency_out   = normalize_dict_floats(recency_out,   0, 1)  # min-max [0,1]
importance_out= normalize_dict_floats(importance_out,0, 1)
relevance_out = normalize_dict_floats(relevance_out, 0, 1)

gw = [0.5, 3, 2]   # [recency, relevance, importance]
master = (recency_w  * recency_out  * gw[0]     # 0.5
        + relevance_w* relevance_out* gw[1]     # 3
        + importance_w*importance_out*gw[2])    # 2
```
- **実効重み = recency:relevance:importance = 0.5 : 3 : 2**(**relevance 支配**)。論文の「等重み」は実装と異なる。
- コードの recency は「**last-accessed でソートした順位 i に対する 0.99^i**」で、論文の「経過ゲーム時間に対する 0.995^Δt」とは実装が違う(順位ベース近似)。
- **含意**: 実運用チューニングでは **relevance を最重視、importance を中、recency を軽く**。埋め込み無しの我々は relevance を安価な代理で作る(下記)。

## 2-2. Reflection の仕様(確認済・プロンプト原文つき)

- **フロー**: 重要度総和が閾値(論文150)超過 → **直近100件** → **顕著な高レベル質問を3つ生成** → 各質問で記憶検索 → **洞察を5件**、各洞察に証拠ID引用。
- **質問生成プロンプト**(公式 `generate_focal_pt_v1.txt` 原文):
  ```
  !<INPUT 0>!   # 出来事/思考の番号付きリスト
  Given only the information above, what are !<INPUT 1>! most salient high-level
  questions we can answer about the subjects in the statements?
  1)
  ```
- **洞察合成プロンプト**(公式 `insight_and_evidence_v1.txt` 原文):
  ```
  Input:
  !<INPUT 0>!    # 番号付き statement 群
  What !<INPUT 1>! high-level insights can you infer from the above statements?
  (example format: insight (because of 1, 5, 3))
  1.
  ```
  → 証拠引用形式は **`insight (because of 1, 5, 3)`**(元 statement 番号を括弧で列挙)。

## 2-3. 近年の後継(2024–2026): 何を保存/要約/破棄するか + 埋め込み無し近似

| システム | 保存/要約/破棄の設計 | 我々への転用点 | 出典 |
|---|---|---|---|
| **Mem0** | 対話から「memory」を抽出・保存・後で取得。API で改訂/削除可(動的状態) | 「生ログ→抽出済み memory」の2層。就寝時抽出に相当 | [Mem0 vs Letta](https://vectorize.io/articles/mem0-vs-letta) |
| **Letta / MemGPT** | 3階層: core(文脈内=RAM)/ recall(検索可能履歴=disk)/ archival(長期=cold)。**tool call で自己編集**し「保存/要約/破棄」を自律決定 | 「今すぐ使う信念=core、想起対象=recall」の分離。就寝統合=recall→coreの昇格 | [MemGPT解説](https://informationmatters.org/2025/10/memgpt-engineering-semantic-memory-through-adaptive-retention-and-context-summarization/) |
| **A-MEM** | 動的知識グラフ、Zettelkasten式リンク、**新観測が過去メモリを遡及更新 + supersede(陳腐化)検出** | 就寝時に古い信念を「revised/invalidated」判定する枠組み | 検索: A-MEM |
| **Zep / Graphiti** | **bi-temporal グラフ**。各エッジに (t_valid, t_invalid)。**矛盾する事実は無効化するが削除しない**、episode 単位で来歴保持 | 信念の「いつ真だったか」を保持し、更新を invalidation で扱う設計 | [Zep arXiv:2501.13956](https://arxiv.org/abs/2501.13956) / [Graphiti(Neo4j)](https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/) |
| **D-MEM** | **RPE(予測誤差/サプライズ)ゲートで更新起動** | 「驚いた出来事だけ重く保存/統合」= importance と別軸の novelty | [arXiv:2603.14597](https://arxiv.org/pdf/2603.14597) |

**埋め込み無しの安価な relevance 近似(sparse retrieval):**
- **BM25 / TF-IDF** による語彙重なりスコア(古典的で頑健、日本語は形態素分割 or 文字bi-gram で近似)。
- **重み付き Jaccard**(見出し語/タグ集合の重なり)。
- **メタデータ・ブースト**: 同一 location / 同一 participant / 同一 topic タグの一致で加点(Zep のグラフ的近さの安価版)。
- 参考実装集: [NirDiamant/Agent_Memory_Techniques(BM25/keyword/graph 等30本)](https://github.com/NirDiamant/Agent_Memory_Techniques)。

## 2-4. 日本語での記憶要約プロンプトの注意

- **出力言語を明示**(「値は日本語、JSONキーは英字」)。矛盾指示を作らない(プロンプト本文・スキーマ description・型定義の3箇所で指示が食い違うと崩れる)。[Algomatic: LLMでJSON出力3選](https://tech.algomatic.jp/entry/2025/05/08/183000)
- **「最初の1文字を `{` にする」制約**で前置き(「はい、出力は…」)を封殺。可能なら Anthropic Tool Use / OpenAI Structured Outputs 等 API 側スキーマ強制を優先。[Zenn: JSON安定化3段防衛](https://zenn.dev/kewa8579/articles/74ead0adc4717b)
- **トークン**: 日本語は同義英文の約1.5–2倍。システムプロンプトは英語、出力のみ日本語指定でコスト削減。出力は「5件のみ」「N字以内」で明示制限。
- **1–10 の重要度アンカーを日本語で固定**(例: 1=歯磨き等の些事、10=失恋・重大な決断)。敬体/常体のブレ防止に文体も指定。

## 【RQ2 成果物】直接使える提案

### (A) スコア関数(埋め込み無し・非LLM想起)
```
score(m | q) = w_rel · rel(m,q) + w_imp · imp(m) + w_rec · rec(m)   [+ w_nov · nov(m)]

rec(m) = decay^(Δt_hours)            decay = 0.99〜0.995   (GA)   → min-max[0,1]
imp(m) = poignancy(1..10) / 10       就寝時にLLM一括採点 or 入力時に軽量ルール/感情辞書
rel(m,q) = BM25 または 重み付きJaccard(見出し語・タグ)
           + メタデータ一致ボーナス(同location/同人物/同topic)  → min-max[0,1]
nov(m) = サプライズ/予測誤差(任意, D-MEM流)  → min-max[0,1]

推奨初期重み  w_rel : w_imp : w_rec (: w_nov) = 3 : 2 : 0.5 (: 1)
  (GA 実装コードの実効比 0.5:3:2 に準拠し、relevance支配)
```
- 各成分は取得候補集合内で **min-max 正規化してから加重和**(GA と同じ)。
- 想起は上位 k 件を返すだけの**純関数(LLM不使用)**。importance のみ就寝時にまとめてLLM採点、日中は前回値/ルール値を使う。

### (B) 就寝時統合プロンプト骨子(1回のLLM呼び出し・JSON出力)
GA の reflection(3質問→5洞察+証拠ID)を**1バッチ呼び出しに畳んだ**もの。入力=その日の生イベント列(番号付き)+ 既存の主要信念。

```
System(英語): You consolidate one agent's day. Read the numbered event log and
current beliefs. Output ONLY valid JSON. First character MUST be '{'.
All string VALUES in Japanese; all KEYS in ASCII as specified.
Importance scale: 1=些事(歯磨き等) … 10=重大(失恋/合格等).

出力スキーマ:
{
  "daily_summary": "その日の1〜3文要約(日本語)",
  "events": [
    {"id": 12, "summary": "…", "importance": 1-10, "emotion": "…", "tags": ["…"]}
  ],
  "insights": [
    {"statement": "高レベルな洞察(日本語)",
     "evidence": [3, 12, 27],           // 元イベントのid
     "confidence": 0.0-1.0}
  ],
  "belief_updates": [
    {"subject": "対象(人/場所/自己)",
     "belief": "更新後の信念(日本語)",
     "change": "new | reinforced | revised | invalidated",   // A-MEM/Zep流
     "evidence": [5, 30]}
  ]
}
制約: insights は最大5件、events の importance は必須、証拠idは入力番号のみ参照。
```
- **importance 採点**をこの1回に含めることで、日中はLLM採点ゼロ(=非LLM想起制約を満たす)。
- **belief_updates.change** に `revised/invalidated` を持たせ、A-MEM の supersede / Zep の invalidation を軽量再現(古い信念を消さず「無効」フラグで上書き)。
- 証拠IDで洞察の追跡性を確保(GA の `(because of 1,5,3)` と同義)。

---

# 主要な確認事実の要約(値の確度)

| 項目 | 値 | 確度 | 出典 |
|---|---|---|---|
| GA recency 減衰係数(論文) | 0.995 / ゲーム時間 | 確認 | arXiv:2304.03442 |
| GA recency 減衰係数(コード既定) | 0.99 / 順位i | 確認 | scratch.py, retrieve.py |
| GA 検索重み(論文) | 全て1(等重み) | 確認 | ar5iv 本文 |
| GA 検索重み(コード実効) | recency:relevance:importance = 0.5:3:2 | 確認 | retrieve.py `gw=[0.5,3,2]` |
| GA importance 尺度 | 1–10 LLM採点 | 確認 | 論文プロンプト |
| GA reflection 閾値 | 重要度総和 > 150 | 確認 | 論文 |
| GA reflection 対象/質問/洞察 | 直近100件 / 質問3 / 洞察5 | 確認 | 論文 + reflect.py |
| MicroPsi selection threshold の個体差/緊急度依存 | 定性的に確認 | 確認(数式は未確認) | Psi-theory, Bach 2015 |
| MicroPsi urge の leaky係数/ゲイン具体値 | — | 未確認 | (PDF抽出失敗) |
| 閾値個体差の canonical 分布形 | — | 未確認(TruncatedNormal/LogNormal推奨) | 標準的モデリング慣行 |
| 不応期の生物学的根拠 | LIF absolute refractory | 確認 | npj 2024, NYU notes |

## 参考文献(主要URL)
- Generative Agents (Park 2023): https://arxiv.org/abs/2304.03442 / https://ar5iv.labs.arxiv.org/html/2304.03442 / 公式コード https://github.com/joonspk-research/generative_agents
- Psi-theory: https://en.wikipedia.org/wiki/Psi-theory ; Dörner & Güss 2013 https://journals.sagepub.com/doi/10.1037/a0032947 ; Bach 2015 https://agi-conf.org/2015/wp-content/uploads/2015/07/agi15_bach.pdf ; Bach 2009 (書籍) https://archive.org/details/principlesofsynt0000bach
- BDI 再考: Schut & Wooldridge https://www.cs.vu.nl/~schut/pubs/Schut/2001.pdf , https://www.cs.vu.nl/~schut/pubs/Schut/2001a.pdf
- OCC/EMA: EMA https://cs.uky.edu/~sgware/reading/papers/marsella2009ema.pdf ; Review https://people.ict.usc.edu/gratch/public_html/papers/MarGraPet_Review.pdf ; Bartneck https://www.bartneck.de/publications/2002/integratingTheOCCModel/bartneckHF2002.pdf ; Steunebrink https://people.idsia.ch/~steunebrink/Publications/EPIA09_action_tendency.pdf
- EVC: Shenhav et al. 2013 https://www.cell.com/neuron/fulltext/S0896-6273(13)00607-7
- LIF/refractory: https://www.nature.com/articles/s44335-024-00013-1 ; https://www.cns.nyu.edu/~eorhan/notes/lif-neuron.pdf
- 近年メモリ: Zep https://arxiv.org/abs/2501.13956 ; Graphiti https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/ ; Mem0/Letta https://vectorize.io/articles/mem0-vs-letta ; D-MEM https://arxiv.org/pdf/2603.14597 ; 実装集 https://github.com/NirDiamant/Agent_Memory_Techniques
- 内発動機LLM: https://arxiv.org/html/2508.18420v1 ; MAGELLAN https://arxiv.org/pdf/2502.07709 ; https://arxiv.org/html/2505.17621v6
- 日本語JSON: https://tech.algomatic.jp/entry/2025/05/08/183000 ; https://zenn.dev/kewa8579/articles/74ead0adc4717b
