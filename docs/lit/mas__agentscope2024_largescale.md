# AgentScope 2024 — Very Large-Scale Multi-Agent Simulation
- リンク: https://arxiv.org/abs/2407.17789 (github.com/modelscope/agentscope)(検証済)| 分野: MAS | 重要度: P0

- **主張**: actor 分散 + 自動並列で超大規模 MAS を実行するプラットフォーム。
- **機構**:
  - **actor ベース分散** + communication graph(頂点=agent、辺=message)。依存の無い agent を**自動で並列実行**。
  - **多層 environment**(timeline / location 次元で group-wise 同期、RPC で高頻度アクセス)。
  - 異質 agent: 人口分布指定 + LLM で背景自動生成。
  - **vLLM 多モデル fleet**: 8×8B / 2×70B / 1×176B(MoE) per device。各 agent 2 LLM 呼/round(応答 + 形式抽出)。
- **スケール実測**: **1M=12分/4台**(Llama3-8B basic)、detailed prompt で85分、10k=5.6分/4台。**線形スケール**。
- **効く seam**: `llm/fleet`(vLLM 多モデル)、`engine/scheduler`(actor 並列・依存グラフ)、`world`(多層 env、RPC)。
- **"seam として"の入れ方**: **スケール/fleet 様式を借用**(認知は薄いので我々の LOD + Concordia 認知で補う)。
- **コスト/スケール含意** ★最良のスケール様式。ただしデモは "guess 2/3 average" 等の単純ゲーム(認知負荷が軽い条件での数字である点に注意)。
- **批判・限界**: LLM 事前知識の混入、極端ロールプレイ失敗、計算ミス、モデル感受性差。
- **build-vs-reuse**: **スケール/fleet の借用候補**。
- **関連**: [[mas__concordia2023_deepmind]] / [[mas__yang2024_oasis]]
