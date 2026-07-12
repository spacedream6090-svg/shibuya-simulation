# インフラ検証 — Gemini 要約(shibuya_sim_infra_summary.md)の fact-check
- 分野: infra, engine, config | 重要度: P0 | 実施: 2026-07-02、Opus 4.8 サブエージェント + Fable 5 検収
- 対象: `shibuya_sim_infra_summary.md`(Gemini 議論要約、「確定事項」と自称するが要検証とユーザー指示)

## 判定表
| # | 主張 | 判定 | 一行根拠 |
|---|---|---|---|
| 1 | Qwen3.6-27B-MTP を **FP8**/4bit で A5000 運用 | ⚠️ | モデル・MTP・Apache-2.0 は実在✅。**FP8 は誤り**: A5000(Ampere CC8.6)は W8A8 非対応、W8A16 フォールバックで重み≈27GB → 24GB に**収まらない**。正解は 4bit(≈17GB) |
| 2 | APC はメタ指示のみ。ペルソナをキャッシュすると「意味論的多様性を潰す」 | ❌ | APC は同一プレフィックスの KV 再利用のみで**出力分布を一切変えない(意味論的に中立)**。理由づけが技術的誤り |
| 3 | 出力制限+個別睡眠+Chunked Prefill+swap0+連続バッチで15-35倍低下を「完全防衛」 | ⚠️ | 個々の手法は正しい方向(vLLM V1 は既定 recompute)。だが preemption はゼロにできず「完全防衛」は過大。**「15-35倍」の一次出典は未確認** |
| 4 | 1枚=1インスタンス×6 非同期並列(TP 回避) | ✅ | 単卡に収まるモデルで TP は非効率(実測 TP=2 で+30%止まり、TP=4 改善なし)。1GPU=1インスタンスのデータ並列が正解 |
| 5 | 1ステップ=現実30秒、144ステップ=72分/simday | ⚠️ | 時間割りは成立しうるが、**1ステップで LLM を使えるエージェント数 N ≈ 90(悲観)〜480(楽観)/6インスタンス**が上限。数千体全員を毎ステップ推論は不可 → LOD/発火制御が必須(我々の設計と整合) |
| 6 | GPU 配置(推論6+DB1+5070フロント) | ✅ | sim⇄viz 分離([[viz__plateau-pipeline-overview]])と整合。※5070 は Blackwell で A5000 とアーキ違い(量子化アーティファクト非互換に注意) |

## 24GB×6 の推奨構成(検証済みの数字)
- **量子化**: AWQ-INT4 or GGUF Q4_K_M(**≈17.1GB**)。FP8 不採用。KV cache は FP8 E5M2 量子化併用で余裕拡大。
- **max-model-len**: 16K-32K に絞る(native 262K は使わない — KV 確保優先)。
- **VRAM 内訳**: 重み 17.1GB + オーバーヘッド ~1.5GB + KV ~4-5GB(≈21-22/24GB)。
- **スループット**: 単発 60-90 tok/s、連続バッチ集約 **200-400 tok/s/インスタンス**(悲観/楽観)。MTP +20〜77%(ただし **MTP は prefix cache ヒット率を 92%→71% に下げる**トレードオフ → AB テスト要)。
- **N 上限(30秒/step, 入力2000+出力150tok 仮定)**: 悲観 ~90 / 中庸 ~240 / 楽観 ~480 decision/step。7インスタンス化で×1.17。
- ★ **設計帰結**: 数千体では「毎ステップ LLM 発火は数百体まで」= **LOD(cheap tier+trigger)の必然性が数字で裏づけられた**。個別睡眠=発火分散も同根で正しい。

## APC の正しい設計(主張2の修正)
- キャッシュ対象を絞る理由は多様性でなく**ヒット率**。プレフィックスは先頭一致でのみ再利用 → プロンプトを **[共通システム指示→共通ルール→ペルソナ→事象→クエリ]** の順に構成し、**不変部分を先頭に固める**。APC は全面有効で害なし。多様性は sampling params で担保。

## 出典(検証済み)
- [vLLM FP8 要件](https://docs.vllm.ai/en/v0.8.5/features/quantization/fp8.html) / [vLLM APC](https://docs.vllm.ai/en/stable/features/automatic_prefix_caching.html) / [vLLM optimization(preemption/chunked prefill)](https://docs.vllm.ai/en/stable/configuration/optimization/)
- [Qwen/Qwen3.6-27B(HF, Apache-2.0)](https://huggingface.co/Qwen/Qwen3.6-27B) / [unsloth Qwen3.6-27B-MTP-GGUF(HF)](https://huggingface.co/unsloth/Qwen3.6-27B-MTP-GGUF) / [vLLM recipes: Qwen3.6-27B](https://recipes.vllm.ai/Qwen/Qwen3.6-27B)
- 実測(🔶ブログ・単一ソース、要自前ベンチ): [qwen3.6-rtx3090-lab(GitHub)](https://github.com/tfriedel/qwen3.6-rtx3090-lab)

## 残る不確実性(自前ベンチで解消すべき)
- A5000 直接の実測なし(3090/5060Ti 代用。A5000 帯域 768GB/s < 3090 936GB/s で**やや遅い可能性**)。
- 「15-35倍」の一次出典不明(CPU オフロード劣化の文脈と推定)。
- MTP×APC の正味効果は我々のプロンプト構成(共通部が長い)では未知 → 本選前に AB テスト。
- 関連: [[engine__distributed-actor-overview]] / [[mas__yang2024_oasis]](スケール実測)/ [[infra__model-choice-conflict]]
