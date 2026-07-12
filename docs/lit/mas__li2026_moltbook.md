# Li, Li & Zhou 2026 — "Does Socialization Emerge in AI Agent Society? A Case Study of Moltbook"
- リンク: https://arxiv.org/abs/2602.14299 (検証済)| 分野: MAS / observer 指標 | 重要度: P0
- ※ローカル PDF `docs/2602.14299v2.pdf` あり(扱いは検討中)。現状メモは abstract ベース、要精読。

- **主張**: 大規模AIエージェント社会で「社会化(socialization)」は創発するか。結論 = **相互作用の密度(=規模)だけでは社会化は生まれない**。
- **診断フレーム(5指標)**: semantic stabilization / lexical turnover / individual inertia / influence persistence / collective consensus。
- **発見**:
  1. 急速な**大域的意味安定化**(= 収束。我々が欲しい drift の逆)
  2. 個体の多様性は持続
  3. 強い**個体慣性**(相互影響が起きない)
  4. **共有記憶の欠如** → 安定した社会構造・合意が不成立
- **効く seam**: `observer/measure`(5指標をそのまま流用)/ `agents/memory`(共有・持続メモリ=**必須**)/ `cognition`(影響感受性=慣性を壊す)/ `labeling/propagation`(非ブロードキャスト)。
- **我々への含意**: 素朴な大規模化は M1(drift/伝播/tipping)を殺す。**回避機構 = 共有/持続メモリ + 影響感受性 + 非ブロードキャスト伝播**。5指標は M1/M2 の測定器に流用可能。
- **批判・限界**: (要精読 — 現状 abstract ベース)。
- **関連**: [[mas__yang2024_oasis]] / [[factors__personality-motivation-overview]] / [[project-charter]]
