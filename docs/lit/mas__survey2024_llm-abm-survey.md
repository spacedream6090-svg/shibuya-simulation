# LLM-ABM Survey 2024 — "LLMs Empowered Agent-based Modeling and Simulation: A Survey"
- リンク: https://arxiv.org/abs/2312.11970 (Nature HSSC 2024, s41599-024-03611-3)(検証済)| 分野: MAS | 重要度: P0
- 著者: 確認中(要検証)

- **主張**: LLMエージェントは従来ABMの限界(単純反応・環境間で汎化不能・記述/説明/予測/反実仮想を同時に扱えない)を超える新パラダイム。応用は 社会/物理/サイバー/ハイブリッド の4ドメイン。
- **機構(標準アーキ)**: Perception(一人称視点)→ Reasoning/Decision → Memory(経験ストリーム/スキルライブラリ)→ Reflection & Planning、の循環(plan→memory→reflection でフィードバック)。
- **効く seam**: `agents`/`cognition`(標準アーキの土台)、全体設計の地図。
- **"結論でなく seam として"の入れ方**: 標準アーキを土台にし、その上に我々の LOD/factors/labeling/observer を差し込む。どの応用が良い等の結論は採らない。
- **コスト/スケール含意** ★: 「Efficiency of Scaling Up」を**未解決問題**と明記。10万体超や長期ランのコスト指針は**存在しない**。= 我々の LOD/fleet が埋める空白(=貢献)。
- **批判・限界**: validation は micro(個体 believability)+ macro(集団現象 vs 実データ)だが**大半が定性的**。robustness / bias amplification も未解決。→ 我々の falsifiable 設計の位置づけを補強。
- **創発パターン**: wisdom-of-crowds、swarm、conformity、role specialization、debate、情報伝播(LLMは stereotype/negative/threat 寄りの content 選好 → drift 設計に注意)、path-dependence。
- **関連**: [[mas__yang2024_oasis]] / Generative Agents / [[project-charter]]
