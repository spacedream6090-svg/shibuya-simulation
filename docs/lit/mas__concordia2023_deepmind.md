# Concordia 2023 (DeepMind) — Generative Agent-Based Modeling library
- リンク: https://arxiv.org/abs/2312.03664 (github.com/google-deepmind/concordia, CC-BY 4.0 / Apache)(検証済)| 分野: MAS | 重要度: P0

- **主張**: tabletop RPG の Game Master 型で生成エージェント社会を作る Python ライブラリ。
- **機構**:
  - **Game Master (GM)**: agent の NL 行動を解決、**grounded world state(money/votes/resource stocks)を維持・検証**(不正行動を却下)、observation を配信。同時行動 / 入れ子ゲーム対応。
  - **agent = modular components**(identity/plans/observations/physiological、各 NL 状態)。2 LLM 呼(action sampling + component update)。連想記憶(Park 2023)。
  - **認知 = March & Olsen**「どんな状況か / 自分は何者か / そういう者はどう振る舞うか」= **非最大化(RL でない、reward 最大化でない)。文化的パターン補完**。
- **効く seam**: `cognition/deliberate`、`agents`(component型)、`world`(grounded 変数=資源/評判)。
- **"seam として"の入れ方**: **非最大化の意思決定は指紋最小化と親和**(world_change_drive を最大化させない方針に合致)。熟考 tier の認知に借用。
- **コスト/スケール含意** ★弱点: batch/caching/並列の記述なし、O(N×T×C) LLM 呼、100+/1000step で prohibitive。**スケール非対応**。
- **批判・限界**: 空間都市/移動/資源地理の例なし。grounded 変数は反応的(創発でない)。validation 課題を著者自ら明記(train-test 汚染 / stereotype / 個体 fidelity)。
- **build-vs-reuse**: 認知・world-grounding の**借用候補**。スケール層は我々が足す必要。
- **関連**: [[mas__agentscope2024_largescale]] / [[mas__yang2024_oasis]] / Generative Agents
