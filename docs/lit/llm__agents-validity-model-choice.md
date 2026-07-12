# 分野9 概観 — LLM/AI を社会エージェントとして(validity gate)
- 分野: llm/*, cognition, observer/measure, config | 重要度: P0
- 出典: RLHF sycophancy 増幅 / peer conformity(arXiv 2508.18321)/ RLHF mode collapse・多様性減(2310.06452)/ data contamination(2402.15938)/ persona steerability・政治bias(2405.20253)

## ★ RLHF は我々の観たい現象を系統的に抑圧する confound
1. **sycophancy / conformity**: RLHF は迎合を増幅し、対立・異論を penalize。instruct/RLHF は base より sycophantic。7-8B instruct は **peer の modal 回答に最大85.5%同調**(独立推論を放棄)。→ **grievance/異論/世界改変を抑圧**、かつ **Moltbook 型崩壊(意味収束)の原因**。= RLHF が崩壊を生む。
2. **mode collapse / 多様性減**: RLHF は出力多様性を大きく減らす(policy entropy 低下、mode-seeking)。→ **個体異質性・tail を潰す**(改変者は tail)。silicon sampling の tail 過小(分野8)と同根。
3. **contamination / memorization**: ベンチで最大91.8%汚染。→ 「創発」が**記憶の再生**かも(Concordia 警告)。calibration は**新規/言い換え設定**で(汚染耐性)。k* が memorized artifact でないか警戒。
4. **persona bias**: incongruent persona に steerable でない(stereotype に回帰)、center-left bias、outgroup bias。→ **LLM の指紋が設計者の指紋を置換**(handoff 警告の具体化)。

## ★ 最重要の設計帰結: モデル選択は第一級の実験変数
- RLHF instruct モデルは**世界改変者を不可能にしうる**(迎合的すぎ)。→ **base/uncensored モデルが genuine な dissent/世界改変の観測に必要かも**。
- **model 選択(base/instruct/uncensored)× k の交互作用**を実験計画に入れる。base config の gpt-oss:20b / qwen 等の選択が結果を左右。
- **anti-collapse 機構(memory/感受性/非broadcast)は RLHF の過剰同調を上回る強度が必要**。

## 効く seam / 緩和
- `llm/fleet` + `config`: model 選択を実験変数化。temperature/diversity 確保。
- `observer/measure`: persona fidelity チェック、行動(非自己申告)指標、別モデル judge(分野8)。
- calibration: contamination 耐性のある新規設定で既知結果を再現。
- **脅威 register(分野8と統合)**: tail 過小 / 効果量水増し / sensitive topic 盲点 / RLHF 同調 / contamination / LLM 指紋。

## 関連
[[measurement__validation-overview]](分野8)/ [[mas__li2026_moltbook]](崩壊=RLHF同調が一因)/ [[factors__personality-motivation-overview]](persona/trait 注入)/ [[project-charter]]
