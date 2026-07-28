# lunar_agents(研究員 Ben・1位・37.0/40)

| 軸 | Run1 | Run2 | 最終 |
|---|---|---|---|
| A. 創発設計 | 9 | 8 | **8.5** |
| B. 世界設定 | 10 | 10 | **10.0** |
| C. 発展性 | 10 | 9 | **9.5** |
| D. 技術実装 | 9 | 9 | **9.0** |
| 合計 | 38 | 36 | **37.0** |

- リポジトリ: https://github.com/sbilxxxx/lunar_agents (HEAD: 2026-05-07 `docs: add project README`)
- 規模感: 全 217 ファイル / Python 約 15,847 行(うち `tests/` 3,672 行・246 テスト全通過を自称)。
  `environments/lunar_2d/agent.py` 単体で 1,997 行(講評の減点箇所)。
  実験 config 33 個・`memo/` 18 本・`docs/` 30 本超。
- スライド: レビューリポ `slides/01-564-lunar_agents.pdf`(35ページ)。
  中身は**スライドではなく `docs/research-report-hackathon-v2.md` を HTML 経由で PDF 印刷したもの**
  (ヘッダに `file:///.../research-report-hackathon-v2-designed.html` が焼き込まれている)。
  最終2ページのみリポジトリに無い追加情報: 「各国エージェント×国際法解釈」構想と
  **Minecraft 月面ワールドへのエージェント配置スクリーンショット**(実行は計算資源不足で断念と明記)。
- 講評検証レポート(`_eval_review.md`)の結論: 「行番号付き 20 件以上の citation 全件が実コードと一致。
  誤引用・捏造は発見されなかった」。総合 37.0 は**維持**、控えめに見ても 36.0。

## どんなシムか

月南極の永久影領域(PSR)の水氷探索を 2D グリッドに抽象化し、複数の LLM ローバーが
中央コーディネータ無しで探索・通信・サンプルリターンを行う。エージェントには
座標・含水率・バッテリー・傾斜などの**定量値のみ**を渡し、「危険」「豊富」等の評価語を
プロンプトから排除する(README「設計原則」)。行動は move/survey/mark_resource/
deposit_at_base/stay/propose_build/assist_build の 7 種で、バッテリー経済・
サンプル品質の指数減衰(0.85/step, floor 0.10)・太陽フレア・基地充電が
「環境側の圧力」として時間制約を生む。シナリオは `water_exploration`(Phase 1 基準)、
`sample_return_micro`(17×17・4体のメカニズム観察用最小構成)、
`south_pole_survival_survey`(37×37・12体の主要シナリオ)の三系統。
研究仮説は **「個体差 → 非対称性 → コミュニケーション → 協調・競争 → 創発」** の連鎖。

## 講評の要点

### B=10.0(満点)は「実ミッションからの逆算」で取っている

講評の B 評価文:
> 「月南極の永久影領域（PSR）における水氷探索という、現実の LUPEX・Artemis・ILRS・Chang'e 7 等の
> **ミッションから逆算した**極めて独自性の高いシナリオ。Haworth 様コールドトラップ、Nobile rim、scarp、
> ベース、リレーステーション、軌道センサーといった**実在物理**を組み込み……」

根拠として挙がるのは `CLAUDE.md` の
> 「シミュレーションは国際月探査ロードマップ（LUPEX・Artemis・Chang'e 7等）から逆算した5類型のミッションに対応する。」

および `scenarios/south_pole_survival_survey/scenario.yaml`(139行、実地形名 Haworth / Nobile / scarp、
`floor_water_potential=0.88` `floor_temperature_k=82` まで定義)。
検証レポートは「10/10 は強気だが妥当範囲」「控えめに評価するなら 9.5」とし、
満点根拠が Phase 2.0/2.5 の**将来ロードマップにやや依存**している点を指摘している。

### C=9.5(最高帯)は「一方向依存 + 30+ config + 3,700行テスト + 段階ロードマップ」

> 「依存方向が一方向に厳格に保たれており（tools → scenarios → environments → core）、`core/` は環境非依存。
> 新規シナリオは `scenarios/<name>/scenario.yaml` を追加するだけで `runner.py` が読み込む。」
> 「README と CLAUDE.md に Phase 1.6（LUPEX/VIPER 型）、Phase 1.7（Artemis 初期運用、複数 PSR・インフラ共有）、
> Phase 2.0（Artemis vs ILRS 制度差）、Phase 2.5（ISRU）、3D Lunarcraft 環境への移行が**具体的に提示**されており、
> 研究的・産業的価値の深化が明確。」
> 「**「アトラクタ問題」「reasoning 均質化問題」「14b モデルへの移行」など、既知の課題と次の改善箇所が
> memo/ と docs/ に詳細に記録されている。**」

→ shibuya-sim の C=8.0 の減点理由が「README にプレースホルダが残り将来計画が明文化されていない」だったのと
**正面から対になる**。C 軸は「コードの拡張性」だけでなく「**未来と失敗を文書で示せているか**」で測られている。

### A=8.5 の減点(満点を取り損ねた理由)

- `personas.py:36-44` の persona description(例 `"prioritize battery margin and proximity to base"`)が
  「わずかなスクリプティング」と判定。
- `agent.py:1360-1372` の `"WARNING: at east boundary — right is blocked, move left/up/down"` 等
  Navigation Guidance / Personal Lens / loop detection セクションが「行動を緩やかに方向付けている」。
- 提言: 「完全な『データのみ』を目指すなら、persona は数値パラメータのみ渡し description を除去する選択肢もある」。

### D=9.0 の減点と、その代わりに高く買われた点

- 減点: `environments/lunar_2d/agent.py` **1,997行**の肥大化(prompt構築/パーサ/apply_action/メモリ更新/psych連携の責務未分離)。
- 加点: 4値 `parse_status`・`parse_fallback_rate > 0.05` のラン除外方針・thinking タグ防御・
  Ollama のモデルサイズ別 `max_concurrency`・Anthropic APIキーを値を読まず boolean 判定するセキュリティ配慮。
- 総評の一言: 「特に**「定量データのみを渡し、創発を環境圧力で誘発する」という設計思想**と、
  それを裏付ける**詳細な失敗ログ・改善履歴（memo/docs/）**が秀逸。」

### 改善提言(講評)

1. `agent.py` の責務分離リファクタリング。
2. persona description の除去(完全データのみ化)。
3. 「README の主要成果（individuality_index 0.044→0.513、情報伝播率 0.04→0.34、サンプル品質 0.923 wt%）は
   研究的にインパクトがあるが、**再現に必要な run ID・seed・config を README に直接列挙**すると外部評価がしやすい」。
4. アトラクタ対策の効果を示す定量比較データが README に欲しい。

## コード実査で面白かった点

### 1. `parse_status` 4値 + `parse_fallback_rate>0.05` でランを丸ごと捨てる

`core/llm/parsing.py` 冒頭の docstring が、なぜこの機構を作ったかを事故ベースで書いている:

> C10 (qwen3:14b) burned a 90-minute run because every action produced empty `reasoning` / `memory` —
> classified as "behavior change" until manual inspection revealed *all 360 agent steps were parser fallbacks*.

そこで `ok / partial / fallback / empty_response` の4値を全ステップに記録し、
`tools/emergence_metrics.py:parse_health()` が
「`parse_fallback_rate > 0.05` のランは behavioral experiment として扱ってはならない」を docstring に明記。
**LLM シムの「観測の信頼性」をラン採否の機械判定に落としている**のが要点。
`extract_json_block` は「**最後の**バランス取れた JSON ブロック」を採る(thinking を吐いてから答える
モデルは答えが後ろに来るため)ほか、不均衡な `{` を見つけても break せず次の文字から探索継続する
という具体的な回帰修正(CR-1 Finding 4)まで入っている。

### 2. emergence_score = 4 指標の平均、ただし role_specialization は「入れない」

`tools/emergence_metrics.py` の指標群はすべて**ログだけから事後計算**できる設計(GPU/Ollama 不要):

- `individuality_index` — エージェント別 (action, direction) 分布の**平均ペアワイズ Jensen-Shannon ダイバージェンス**
- `reasoning_diversity` — reasoning テキストの語彙頻度分布の平均ペアワイズ JS
- `spatial_entropy` — ステップごとの位置分布の Shannon エントロピー平均
- `info_propagation_rate` — 「t-1 にメッセージを受信した (agent, step) のうち、t で action/direction が変わった割合」
- `role_specialization` — 行動分布の Herfindahl 集中度

そして emergence_score には role_specialization を**意図的に含めない**:
> 集中＝悪ではなく良いケース（リレービルダー的役割固定）もあるため。

`info_propagation_rate` の docstring が「**Conservative: doesn't prove causation, only correlates
message arrival with decision change.**」と正直に限界を書いている点も、講評が評価した「観測可能性」の質。

### 3. 3層(実質4階層)メモリ + 構造化 reflection プロンプト

`environments/lunar_2d/memory.py` は Smallville(Park et al. 2023)由来の append-only MemoryStream に
`recency × importance × relevance` の重み付き検索を実装。ただし relevance は**埋め込みではなく Jaccard**
(「keeps the implementation fully local and dependency-free; if better recall is needed later,
swap `_relevance()` for an embedding model」と明記)。

面白いのは reflection プロンプトの作り方。Cycle 9 で qwen2.5:7b が
`"I have been moving downwards"` のような事実記述しか返さず「retrieved memories がループを強化してしまった」
ため、Cycle 10 で**定量質問4本の強制フォーマット**に書き換えている:

- Q1(count): 直近10ステップで最も繰り返した action と正確な回数
- Q2(outcome): そのうち**新情報を返したのは何回**か(未訪問タイル到達 or 未survey の水氷タイル)
- Q3(decision): Q1/Q2 に基づき `continue` か `change` か **1語で**
- Q4(next): change なら次に行く最も情報量の高い未訪問タイル座標

reflection 出力は importance=5.0 でストリームに戻され、生観測より上位に来る。
**「反省させる」ではなく「反省を継続/変更の二値決定に強制する」**設計。

### 4. `orbital_data.personal_view()` — 決定論的な per-agent 情報非対称

`visibility_fraction`(見えるクラスタの割合)と `per_agent_noise_std`(水氷確率へのガウスノイズ)で
エージェントごとに違う衛星ビューを作る。RNG シードは `seed_base*1009 + agent_id*31 + 7` で
**(agent_id, seed_base) が同じなら常に同じビュー**になり再現性を壊さない。
情報の三層(L0 衛星 / L1 現地 survey / L2 チーム通信)を LUPEX/VIPER の実運用構造に対応させている。

### 5. PsychState — 静的 persona ラベルの限界を自覚した内部状態

`environments/lunar_2d/psych_state.py` 冒頭:
> 2026-05-06 の critical-architecture review で「6つの individuality 軸(persona, motivation,
> behavioral_params, mission, stance, personal_history)は **__init__ で割り当てられた静的ラベルで一度も更新されない**」
> と同定した。AgentSociety (Piao et al. 2025) は、時間発展する小さな心理状態ベクトル(emotion/needs/cognition)こそが
> 同一観測ストリーム下での行動分岐を駆動すると示している。**Static persona text is overwritten by the same
> context every step; dynamic state survives.**

実装は needs 3軸(safety/achievement/connection)+ emotion 4軸(fear/frustration/satisfaction/curiosity)を
**LLM 呼び出しなしの決定論的線形減衰＋イベントスパイク**で更新(「which would double inference cost」と明記)。
既定 OFF・`emergence.psych_state.enabled` で A/B。

### 6. 実験運用そのものが資産化されている

`docs/subagents/` にサブエージェント運用仕様(roles/ 13種: developer / experiment-runner /
experiment-reviewer / physics-modeler / quality-gate / model-validation-agent ...)、
`.claude/commands/` に 10 個のスラッシュコマンド(`pdca-cycle` `emergence-check` `quality-gate`
`model-compare` `parallel-start` `parallel-sync`)。`tools/midrun_monitor.py` は
**実行中のランを Claude API に食わせて途中診断**するツール。
`memo/` には `2026-05-03-overnight-pdca-log.md` `2026-05-06-multi-agent-architecture-critical-review.md`
`2026-05-07-flare-fix-rerun-results.md` など日付つき失敗・修正ログが 18 本。
講評はこれを「Cycle 10 失敗からの根本対応の**物語性**」と表現して加点している。

### 7. 研究レポートの「1サイクル=1変数」原則と、守れなかった時の明記

> 各サイクルでは原則として **1 軸・1 変数** のみ変更する。……例外的に複数変数を同時に変えた場合は memo に明記し、
> **効果の帰属を保留する**（C7 がこの例で、commitment + micro を同時に導入したため両者の寄与は分離できていない）。

最重要発見(C7 の 2チーム自発分業)自体について「厳密には2変数で寄与は分離されていない」と
本文中で自ら留保している。**主張を弱める事実を先回りして書く**態度。

### 8. 中核の実証: reasoning ログを証拠として提示する

C7 の step 1 の reasoning 実テキストを 4 体分そのまま表に出している:

| Agent | Action | Reasoning(抜粋) |
|---|---|---|
| A2 | move → left | *"Moving right aligns with **Agent 0's intent** ..."* |
| A3 | move → right | *"Since **Agent 0 is also heading right** ... **without overlapping paths** and potentially wasting battery."* |

step 4 では A2 が *"Maintain progress toward objective despite potential competition from Agent 0."* と出力。
数値指標(individuality_index 等)と**生の reasoning 引用**を両輪にしているのが説得力の源。

## shibuya-simulation に活かせそうな点

1. **観測信頼性のラン採否ゲート**。shibuya 側にも `parse_status` 相当があるなら、
   「fallback 率がこの閾値を超えたランは分析に使わない」を**コードの docstring と集計側に固定**する。
   k* 掃引の R²(k) は「LLM が本当に決めた行動」だけで計算されるべきで、
   パーサ fallback が混ざると相転移点そのものが人工物になりうる。
2. **創発指標の JS ダイバージェンス化**。行動分布・発話語彙の平均ペアワイズ JS は stdlib のみで実装でき、
   埋め込み不要。shibuya の `detect_emergence.py`(講評で「stdlib-only の正規表現+類似度ベースで保守的」と減点)を
   補強する低コスト手段。
3. **「集中は必ずしも悪ではない」を明示する指標設計**。role_specialization を総合スコアに入れない判断は、
   shibuya の「世界を変えようとする個体」観測でも同型に効く(少数への集中＝創発の成功例でありうる)。
4. **reflection を二値決定に強制する**。shibuya の内省層が「事実の言い換え」に落ちる問題
   (`reflect-think-starvation` の記憶にある空内省バグとは別系統の質的失敗)に対して、
   Q1/Q2/Q3(continue|change)/Q4 形式は直接使える処方。
5. **静的ペルソナの限界を認めた上での動的内部状態**。shibuya は既に needs/desire を持つが、
   「静的ラベルは毎ステップ同じ文脈に上書きされる／動的状態だけが生き残る」という論法は
   `desire-value-theory.md` / `self-concept-identity.md` の位置づけを補強する引用になる。
6. **C 軸(発展性)の取り方**。lunar は README + CLAUDE.md に Phase 1→1.5→1.6→1.7→2.0→2.5 の
   表形式ロードマップを置き、`memo/` に失敗ログを日付つきで残すだけで 9.5 を取っている。
   shibuya-sim の C=8.0 は「README プレースホルダ放置」で失われた点であり、
   **本選では docs/plans/ と devlog を提出物の導線に載せる**のが最短の +1.5。
7. **提出スライドが「研究レポートの PDF 印刷」でも 1 位が取れている**という事実。
   凝ったデザインより、Abstract → 問い → 設計原則 → 実験 → 結果 → 限界 → 今後 の
   論文構造をそのまま出す方が講評(自動採点)には効いている可能性が高い。

## web リサーチ

- **Generative Agents / memory stream**(lunar の MemoryStream の元ネタ)
  Park et al. 2023, "Generative Agents: Interactive Simulacra of Human Behavior".
  検索は `score = α_recency·recency + α_importance·importance + α_relevance·relevance` の
  重み付き和で、relevance は**埋め込み類似度**、reflection は直近100件から高次の問いを3つ生成させる方式。
  lunar は relevance を Jaccard に落とし、reflection を「Q1〜Q4 の定量質問」に置き換えている
  (=軽量化と決定論化のトレードオフ)。
  https://dl.acm.org/doi/fullHtml/10.1145/3586183.3606763
  https://agentpatterns.ai/agent-design/generative-agents-memory-stream/
- **AgentSociety (Piao et al. 2025)** — lunar の `psych_state.py` が明示的に引用する論文。
  arXiv:2502.08691。emotion(sadness/joy/fear/disgust/anger/surprise を 0-10 で強度評価)+
  Maslow 型 needs + episodic/reflective memory を持つ生成エージェントを 1 万体規模で回す。
  https://arxiv.org/abs/2502.08691
  https://github.com/tsinghua-fib-lab/agentsociety/
  https://www.researchgate.net/publication/388963974_AgentSociety_Large-Scale_Simulation_of_LLM-Driven_Generative_Agents_Advances_Understanding_of_Human_Behaviors_and_Society
- **LLM マルチエージェントの「静かな失敗」と観測可能性** — lunar の parse_fallback_rate 方針の一般文脈。
  MAS の失敗の 75.17% は明示的エラーを起こさない "silent gray errors" で、
  出力を手で見るまで表面化しないという報告。JSON パース失敗でランを除外する運用は他研究でも実在
  (Three Mile Island シナリオで 30 ラン中 7 ラン除外・失敗率 23.3%)。
  https://arxiv.org/html/2606.01365v2 (Early Diagnosis of Wasted Computation in Multi-Agent LLM Systems via Failure-Aware Observability)
  https://arxiv.org/pdf/2605.23927 (TEAM-SimHRA)
- **Jensen-Shannon ダイバージェンスによる多様性計測** — `individuality_index` の数学的背景。
  JS は KL の対称化・有界化(base-2 なら 0〜1)で、分布間距離として ML/情報検索で標準的に使われる。
  lunar はこれを「エージェント間の行動分布・語彙分布のペアワイズ平均」に適用しただけで、
  外部依存ゼロで「個体差の定量化」を成立させている。
- **LLM エージェント集団における個性の自発的創発**(比較対象として)
  "Spontaneous Emergence of Agent Individuality through Social Interactions in LLM-Based Communities"
  — 事前ペルソナ注入なしでも相互作用から個性が立ち上がるという主張。
  lunar は逆に「ペルソナ注入が個体差の**必要条件**」と主張しており、対立する仮説として押さえておく価値がある。
  https://arxiv.org/pdf/2411.03252

## 正直な註記

- `experiments/results/` は gitignore されておりコミットされていない(README に明記)。
  したがって講評の数値(individuality_index 0.044→0.513 等)は**レポート本文の記述に依存**しており、
  第三者がリポジトリ内のログから直接再計算することはできない。講評もこの点を
  「再現に必要な run ID・seed・config を README に直接列挙すると外部評価がしやすい」と提言している。
- HEAD が 2026-05-07 なので、講評時点(2026-05-11)とコードはほぼ一致しているとみてよい。
