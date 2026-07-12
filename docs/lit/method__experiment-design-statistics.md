# 実験計画・統計・M2運用・実験管理 — 第4フェーズ課題1(Opus 委譲 2026-07-02)
- 分野: analyze, observer/measure, engine, infra | 重要度: P0(M3=論文級データの成否を直接決める)

## A. k 掃引の DOE
- 標準: Lorscheid 2012 の systematic DOE(応答定義→factorial/LHS→**replication は CV 収束で決定**→標準報告)。
- **2段階掃引が定石**: 粗掃引 k 8-12点(seed 5-10)→ 急落帯に細掃引 +4-8点(**seed 15-25 に増強** — 相転移帯は分散自体が信号なので厚く)。予算が厳しければ GP 代理モデル+active learning で細掃引を代替。
- ★ **finite-size scaling(FSS)を使うならエージェント数 N 3水準(例 300/1000/3000)は死守**。

## B. R²(k) と相転移の統計
- R² の CI: **(k,seed) 単位の block/hierarchical bootstrap**(naive bootstrap は seed 相関で CI 過小)。混合モデルなら partR2。
- changepoint: **PELT**(exact・O(n))+ segmented 回帰で R² break 推定。
- ★ **k* の主推定は FSS 推奨**: R²(k;N) を N 3水準で取り、交差/data collapse から k_c。「真の相転移 vs 単なるノイズ増」を分ける学術的最低ライン(naming game の FSS 前例: arXiv:1609.02869)。
- EWS(Dakos protocol): detrend(Gaussian kernel)→ 窓幅 ~系列長50% → 分散・lag-1自己相関の Kendall τ → **surrogate で有意性**。detrend 無しは偽陽性。**時間軸 CSD と k軸 R² 崩落は別物**: 各 k の run 内時系列に CSD を当て、k* 近傍で立ち上がるかを第3脚に。
- researcher degrees of freedom: **pre-registration + multiverse analysis**(判定閾値・窓幅・detrend・judge モデルの分岐を全列挙し頑健性を可視化。RobustiPy)。

## C. M2(世界改変者判定)の運用プロトコル
- LLM-judge バイアス対策: **position**(順序スワップ)/ **verbosity**(length 正規化)/ **self-preference**(judge は被評価と**別ファミリ**、ensemble 可)。
- **行動ログ(trajectory)からの操作的判定**が主流(AgentRewardBench 等)。自己申告除外。
- **IRR**: 層化サンプル 100-300件(**陽性=改変者を oversampling**)を人手二重判定、judge-人手 **Cohen κ ≥0.7 目標(下限0.6)**。exact-match 一致率でなく κ/α を主指標に(Reliability without Validity 問題)。

## D. 実験管理・再現性・ログ
- スタック定石: **Hydra**(k×seed×N sweep を config 宣言)+ **MLflow**(run 追跡)+ **DVC**(大容量ログ・パイプライン版管理)。
- ログ3層: L1 個体 trajectory(LLM入出力+内部状態+行動)/ L2 集団集約(規範分布・EWS用時系列)/ L3 世界スナップショット。**Parquet+zstd**。
- ★ **決定論リプレイ: temperature=0 でも完全再現は保証されない**(GPU/バッチ非決定性)→ **LLM 応答キャッシュ(prompt+model+params キー)が最も確実**。+seed 記録+logprobs 保存+**エージェント ID で決定論的順序付け・per-agent RNG**。vLLM reproducibility ガイド準拠。

## 統合テンプレート(10日 GPU、詳細は原レポート)
Phase 0(0.5日): パイロット 3-5 seed×3k で CV 収束→seed 数確定、rubric 固定、**pre-register** / Phase 1(3日): 粗掃引 k10点×N1000×seed8 / Phase 2(3.5日): 細掃引+**FSS(N 3水準)**、急落帯 seed20 / Phase 3(2日): judge+κ 校正+multiverse / Phase 4(1日): 予備・アーカイブ。

## 出典(検証済み)
[Lorscheid 2012(Springer)](https://link.springer.com/article/10.1007/s10588-011-9097-3) / [JASSS 23/1/12](https://www.jasss.org/23/1/12.html) / [PELT(arXiv 1101.1438)](https://arxiv.org/abs/1101.1438) / [FSS naming game(arXiv 1609.02869)](https://arxiv.org/abs/1609.02869) / [EWS 検出限界(arXiv 1204.6231)](https://arxiv.org/abs/1204.6231) / [multiverse CSS(arXiv 2605.19745)](https://arxiv.org/abs/2605.19745) / [self-preference bias(arXiv 2410.21819)](https://arxiv.org/abs/2410.21819) / [AgentRewardBench(arXiv 2504.08942)](https://arxiv.org/abs/2504.08942) / [Hydra](https://hydra.cc) / [MLflow](https://mlflow.org) / [vLLM reproducibility](https://docs.vllm.ai/en/latest/usage/reproducibility/)

## 関連
[[complexity__phase-transition-methodology]](三角測量の具体化)/ [[measurement__validation-overview]](κ・operational validity の運用化)/ [[risk-register]](k 交絡 → null/sham 対照が本メモの DOE に追加必須)/ [[infra__gemini-summary-verification]](ラン時間)
