# agentic memory + ソロ内省モード — 自発的 DB アクセスと信念書き戻し(★k の実装部位)
- 分野: agents/memory, cognition/lod, state-update, observer | 重要度: P0 | 実施: 2026-07-02、Opus 4.8 サブエージェント + Fable 5 検収

## A. agentic memory retrieval(ID ベース自発的 DB アクセス)
- Gemini 案: 「記憶を与えず、思考の第一段階でエージェント自身が tool use で自 ID から外部 DB を掘る」。
- 先行: **MemGPT/Letta**(function call で core/recall/archival メモリ階層を自己管理)、★ **ID-RAG(arXiv 2509.25299)**= ペルソナ/アイデンティティを外部知識グラフから retrieve — 我々の設計に最も近い直系。
- **pull vs push の実測比較**: agentic pull は pre-inject push 比で**コスト ~10x・レイテンシ+数秒**。単純な事実取得では無駄、多段・曖昧クエリでのみ品質が正当化。失敗様式: クエリ品質依存 / hallucinated ID / 検索 miss の自己検知不能。
- 27B 4bit の function calling は実用域だが完璧でない(BFCL ~68%級)→ **guided decoding(JSON 文法制約)で format 崩れを抑制**が定石。
- ★ **設計帰結(ハイブリッド)**: 日常 step = **pre-inject push**(安価・予測可能)/ **内省・重大判断 step のみ agentic pull**。これは LOD の tier 分割と自然に一致。hallucinated ID 対策: ID は検索クエリでなく**決定的キー(自 ID→DB 直引き)**で渡す。
- **研究価値**: 自発 pull は「記憶想起そのもの」をエージェントの内的意思決定としてログ化できる=**世界改変の芽(何を思い出そうとしたか)を観測可能**にする。

## B. ソロ内省モード(非対称 LOD)と信念書き戻し
- Gemini 案: 「単独 step で長文・複数回思考ループ(LOD最高値)を許可し、信念を DB へ直接書き戻す。世界観の変容はこのモードで発生する設計」。
- 先行: Generative Agents(Park 2023)の reflection(importance 累積閾値で発火→高次概念に統合)の**能動化・永続化拡張**。sleep-cycle 系(nightly に蒸留)、Letta self-editing memory。
- ★★ **両刃のリスク(実証報告あり)**:
  1. **平均回帰**: RLHF mode collapse が内省ループで増幅 → ペルソナ均質化(persona drift、echoing=他者への同調)。[[llm__agents-validity-model-choice]] の懸念がループで加速する。
  2. **誤信念の自己強化**: self-perceptive hallucination が固定化し、**エージェント間に伝播**する報告(ID-RAG が対象化)。
  - 緩和: identity KG への接地(ID-RAG)、安定ペルソナ手法(SPASM)、書き戻し前の整合チェック。**ただし接地を強めると「世界観の変容」まで抑えてしまう**。
- ★★★ **k との接続(本メモの核心)**: 「接地強度 vs 自由書き戻し」の綱引きの制御点は、まさに**k(経験→内部状態の結合強度)の operational 実装**である:
  - **内省の頻度 / 深さ(ループ回数)/ identity 接地強度 / 書き戻しの自由度** = k を構成する実装パラメータ群。k 掃引はこれらの掃引として実装できる。
  - persona drift は**バグでなく測定対象**: 「世界改変=望ましいドリフト」と「hallucination 崩壊=望まないドリフト」を区別する指標(コヒーレンス+drift トレース)を observer に。→ M2 の判定と接続。
- 先行にも「nightly / 閾値発火 / sleep-cycle overlay」の頻度・強度パラメータ化あり → k 掃引の実装参考。

## 出典(検証済み)
- [Letta / MemGPT agent memory(公式ブログ)](https://www.letta.com/blog/agent-memory/) / [letta-ai/letta(GitHub)](https://github.com/letta-ai/letta)
- [ID-RAG(arXiv 2509.25299)](https://arxiv.org/abs/2509.25299) — drift / mode collapse / self-reinforcing hallucination を明示的に対象化
- [SPASM 安定ペルソナ(arXiv 2604.09212)](https://arxiv.org/abs/2604.09212) / [one-shot vs iterative retrieval(arXiv 2509.04820)](https://arxiv.org/abs/2509.04820) / [reflection/summarization(arXiv 2305.01253)](https://arxiv.org/abs/2305.01253)
- 🔶 実務ブログ(信頼度中): Letta 系記事、sleep-cycle(Medium)— 概念参照のみ、数値は依拠しない

## 関連
[[state-update__open2-overview]](k=フィードバックゲイン → **実装部位が特定できた**)/ [[llm__agents-validity-model-choice]](RLHF 同調の増幅リスク)/ [[mas__li2026_moltbook]](崩壊=望まないドリフト)/ [[systems__gst-overview]](feedback)/ references クラスタ1(Park 2023 / MemGPT)
