# storage layer(OPEN#5 の判断材料)+ 6×vLLM ルーティング + 個別睡眠
- 分野: infra, engine, config(OPEN#5) | 重要度: P0 | 実施: 2026-07-02、Opus 4.8 サブエージェント + Fable 5 検収

## A. storage layer(OPEN#5 の grounding — 決定はユーザー)
DB 機(A5000×1 + CPU)に集約する構成の選択肢比較(数千体・数百万イベント規模):
| 用途 | 第一候補 | 代替 | 選定基準 |
|---|---|---|---|
| agent state / セッション / キュー | **Redis** | — | 超低レイテンシ。ただし長期 system-of-record には不向き(永続化は AOF/RDB or 別DB) |
| ベクトル記憶 | **Qdrant** | PostgreSQL+pgvector | pgvector は ~50M vector 超で限界。Qdrant はスケール強い |
| **統合1本化(運用単純さ優先)** | **PostgreSQL+pgvector** | Redis+RediSearch | 単一ノードで構造化+ベクトル両立。**数千体・中規模なら十分 = ハッカソン10日間では有力** |
| ソーシャルグラフ | **NetworkX(in-proc)** | Neo4j | 数千体なら NetworkX で足りる。動的・大規模・常時 traversal なら Neo4j(supernode 劣化注意) |
| 埋め込みモデル | DB 機に小型 embedding 常駐 | — | 推論6機を汚さず retrieval を DB 機で完結(Gemini 案と整合✅) |
- **Fable 5 の見立て**(決定でなく推奨): 10日ビルドなら「**Redis(state)+ pgvector(記憶・ログ)+ NetworkX(グラフ)**」が運用最小。スケール限界が見えたら Qdrant/Neo4j へ差し替え(storage seam を抽象化しておく)。

## B. 6×vLLM インスタンスのルーティング
- 本命: **vLLM Router**(Rust 製・state-aware、consistent hashing / power-of-two)or **vLLM production-stack の prefix-aware routing**。代替: LiteLLM Router(多 provider 抽象)、nginx(自前 sticky)。
- ★ **セッション親和性が重要論点として実在**: **routing key = agent ID で同一エージェント→同一インスタンスに固定**すると、ペルソナ system プロンプト+履歴の **prefix cache ヒット率が単一機の天井(~96%)まで回復**する実測。
  - → [[infra__gemini-summary-verification]] の APC 修正(共通部を先頭に)と合わせ、**「共通指示を先頭+agent-ID sticky routing」が正しいキャッシュ戦略の全体像**。Gemini 案の「限定APC」は不要で、こちらが上位互換。
- **スループット含意**: sticky routing は課題A/B の重いプロンプト(ペルソナ+記憶)を安価にする鍵 → N 上限(90-480/step)を楽観側に寄せる主要手段。

## C. 個別睡眠スケジューリング(負荷平準化)
- Gemini 案「エージェントごとに睡眠時間をずらし重い要約を24hに分散」= ✅ 方向は正しい。先行: Generative Agents の睡眠サイクル、sleep-cycle 系(background で蒸留)、agentic workload scheduling(arXiv 2506.24045)。
- 定石: **foreground(反応・会話)と background(内省・要約)のフロー分離+優先度制御**。background は待機キューの谷に流す(連続バッチと相性良)。
- LOD と統合: 睡眠=cheap tier 滞在、覚醒中も発火制御で LLM 呼び出しを数百/step に間引く([[infra__gemini-summary-verification]] の N 上限)。

## 出典(検証済み)
- [vLLM Router リリース(公式ブログ)](https://blog.vllm.ai/2025/12/13/vllm-router-release.html) / [prefix-aware routing(vLLM production-stack docs)](https://docs.vllm.ai/projects/production-stack/en/latest/use_cases/prefix-aware-routing.html)
- [Qdrant vs Redis(Zilliz 比較)](https://zilliz.com/comparison/qdrant-vs-redis) / [pgvector vs Redis(Zilliz)](https://zilliz.com/comparison/pgvector-vs-redis) / [Neo4j social network(公式)](https://neo4j.com/use-cases/social-network/)
- [agentic workload scheduling(arXiv 2506.24045)](https://arxiv.org/abs/2506.24045)
- 🔶 ベンダー比較記事(Zilliz/PingCAP)は自社寄りバイアスに注意(相対比較のみ参照、絶対数値は依拠しない)

## 関連
[[infra__gemini-summary-verification]](APC/N 上限)/ [[engine__distributed-actor-overview]](actor 並列・再現性)/ [[infra__agentic-memory-reflection]](記憶アクセスパターン)/ OPEN#5(storage — 本メモは判断材料、決定はユーザー)
