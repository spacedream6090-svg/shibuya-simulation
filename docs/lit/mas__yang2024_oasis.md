# OASIS 2024 — "Open Agent Social Interaction Simulations with One Million Agents"
- リンク: https://arxiv.org/abs/2411.11581 (github.com/camel-ai/oasis)(検証済)| 分野: MAS | 重要度: P0
- 著者: camel-ai(確認中)

- **主張**: 最大100万体のLLMエージェントSNSシミュ。情報伝播・群分極・herd効果・誤情報拡散を再現。
- **アーキ(5モジュール)**:
  1. **Environment Server** — 関係DBで全状態(users/posts/comments/relations/traces)を保持・更新
  2. **RecSys** — フィード順位付け(X: TwHIN-BERT 興味+新しさ+superuser / Reddit: hot-score)
  3. **Agent Module** — CAMEL 基盤。memory(遭遇post/行動履歴/reasoning)+ action 実行
  4. **Time Engine** — 24次元・時間帯別 活動ベクトルで**確率的に活性化**(=LOD的機構)
  5. **Scalable Inferencer** — 分散async、vLLM、GPUマネージャ
- **行動空間**: 21種(sign_up/create_post/repost/follow/like/comment/search/trend/refresh/do_nothing 等)= SNS特化
- **スケール実測** ★: **1M×1step=18h / A100×27**、**100k×1step=3h / A100×5**。async並列 + vLLM + scale-free network 生成(0.2で core をfollow)。
- **効く seam**: `llm/fleet`(vLLM+GPUマネージャ)、`world`(env-server状態)、`cognition/lod`(Time Engine の確率的活性化)、`engine/scheduler`。
- **"seam として"の入れ方**: **インフラ様式を流用**(async+vLLM+time-engine活性化+env-server)。ただし**ドメイン(SNSフィード/RecSys/21行動)は非採用** — 我々は空間・経済の都市。
- **コスト/スケール含意** ★: 我々=A5000×7(A100より弱)+リッチ認知+k掃引×seed → 現実的規模 **~1k–10k、LOD必須**。100万は「小モデル1呼出/step+巨大GPU+確率活性化」の産物で我々には不可能。
- **批判・限界**: RecSys 単純で中間ユーザ表現が弱い、agentは人間より herd/分極が**過剰**(uncensored)、合成プロフィールの多様性が独立変数仮定で限定、プラットフォーム毎に prompt/action チューニング要。
- **build-vs-reuse**: OSS(camel-ai/oasis, Llama-3-8B, vLLM, Neo4j可視化)。スケール・インフラの**参照/流用候補**。ドメインは自作。
- **関連**: [[mas__survey2024_llm-abm-survey]] / [[project-charter]]
