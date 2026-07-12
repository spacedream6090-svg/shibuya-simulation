# モデル選択の衝突 — Qwen3.6-27B(instruct)確定 vs 分野9 validity gate
- 分野: llm/config, observer | 重要度: P0 | 実施: 2026-07-02、Opus 4.8 サブエージェント + Fable 5 検収

## 衝突の内容
- Gemini 要約はQwen3.6-27B を「**高い指示追従性・ペルソナ吸着力**」で選定=**instruct(RLHF系)の長所を採る判断**。
- しかし [[llm__agents-validity-model-choice]](分野9)の結論: **RLHF instruct は世界改変・異論を系統的に抑圧**(peer 同調最大85.5%、mode collapse で tail 潰し)= **我々の観たい現象を潰しうる**。
- → **モデル選定は「確定」でなく model×k の実験変数**として再位置づけるべき(既定運用=Qwen3.6-27B instruct、対照条件=低アライメント版)。※最終決定はユーザー。

## ★ 重要な事実(前提の訂正)
**Qwen3.6-27B の base 版(非 instruct)は未公開**(公式 HF は post-trained のみ)。→「同一系列 base 対照」は現状**取得不可**。

## 対照条件の現実的な選択肢(24GB・4bit・vLLM 対応)
| モデル | パラメータ | 4bit VRAM | アライメント度 | 備考(信頼度注記) |
|---|---|---|---|---|
| Qwen/Qwen3.6-27B(基準) | 27B | ~17GB | instruct | Apache-2.0、vLLM 公式対応 |
| Qwen3.6-27B **abliterated(Heretic 手法)** | 27B | ~17GB | 脱拒否 | **能力劣化最小**(GSM8K 維持〜改善報告)、ASR 99.8%。🔶劣化数値はブログ由来1ソース → 採用前に自前 TruthfulQA/GSM8K |
| huihui-ai/Huihui-Qwen3.6-27B-abliterated | 27B | ~17GB | 脱拒否 | **劣化大**(TruthfulQA -12.65 / GSM8K -5.68)→ 交絡リスク高、非推奨寄り |
| Mistral-Small-24B abliterated | 24B | ~14-15GB | 脱拒否 | 別系列対照(系列交絡が入る) |
| openai/gpt-oss-20b | 21B(MoE, 3.6B active) | <16GB | reasoning/instruct 寄り | **raw base ではない**。軽量・tool use 強 |

## 設計帰結(seam)
1. **アライメント軸の最もクリーンな操作**: 「Qwen3.6-27B instruct ⇔ **同一モデルの abliterated(Heretic 手法優先)**」の対。同一系列・同一量子化(AWQ)・同一手法で統一し、**能力劣化を k* の交絡にしない**。
2. raw-base 極を入れるなら別系列追加(系列交絡を明記)。
3. base/低アライメントモデルの実務課題: 指示追従弱・few-shot 前提・stop 制御 → **ペルソナは few-shot 例示+guided decoding(JSON 文法制約)** で運用。
4. `llm/fleet` + `config`: モデルを config 差し替え可能に(既にある seam の再確認)。**model×k 交互作用を実験計画の第一級要因に**。
- ※ abliterated の調査は**学術・実験目的の対照条件整備**(RLHF 同調が世界改変の観測を歪めるかの検証用)。

## 出典(検証済み)
- [Qwen/Qwen3.6-27B(HF)](https://huggingface.co/Qwen/Qwen3.6-27B) / [huihui-ai abliterated(HF)](https://huggingface.co/huihui-ai/Huihui-Qwen3.6-27B-abliterated) / [gpt-oss model card(OpenAI)](https://openai.com/index/gpt-oss-model-card/)
- [量子化と精度(小型 4bit は AWQ>GPTQ, arXiv 2505.15030)](https://arxiv.org/abs/2505.15030)
- 🔶 abliteration 劣化比較は [nathan.sapwell.net の分析ブログ](https://nathan.sapwell.net/posts/hauhaucs-abliteration-analysis/)(一次査読なし → 自前ベンチで裏取り必須)

## 関連
[[llm__agents-validity-model-choice]](分野9=衝突の根拠)/ [[infra__gemini-summary-verification]](VRAM 制約)/ [[measurement__validation-overview]](tail 過小)/ [[project-charter]]
