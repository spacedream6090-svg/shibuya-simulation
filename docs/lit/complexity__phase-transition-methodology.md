# 分野7 概観 — 複雑系・統計物理(相転移・臨界・経路依存)= k* 測定の方法論
- 分野: engine/metrics, analyze, observer | 重要度: P0
- 出典: 社会系の相転移(集団形成)/ 臨界と early-warning signals(critical slowing down; Scheffer 2009)/ 分散分解の限界(heritability 批判, PNAS 2020 / SEP)

## 中核機構
- **相転移(社会系)**: 集団形成・解散は有限系の相転移に類似。**パラメータ(相互作用/結合強度)が閾値を越えると急変**。→ **k が k* を越える = 相転移**(分野3の k= フィードバックゲインと接続)。
- **秩序変数(order parameter)**: ABM では臨界パラメータ(コスト便益/社会的影響)が「一大集団 vs 共存」を決める。→ 我々も**秩序変数が必要**(改変者割合 / consensus / R²)。
- **経路依存 / 多安定**: 複数の安定レジームが鋭い閾値で分離。閾値超で**正のフィードバックが微小摂動を増幅**し反転困難(hysteresis)。= **init-determined vs path-dominated**。path-dominated = 初期微差が増幅 → 経路依存。
- **early-warning signals(critical slowing down)** ★: 転移直前に**揺らぎの振幅と持続が増大**(分散・自己相関の上昇)。→ **k を掃引しながら k* を検出する具体ツール**。

## ★ 分散分解(R²)の限界 — 方法論の重要 caveat
heritability 文献: **「nature/nurture の分散分解は、nature と nurture が結合(gene-environment correlation / 文化伝達)する系では ill-defined」**。
→ 我々の R²(初期条件での回帰)も、**k が高い(結合が強い)ほど init-vs-path 分解が破綻**しうる(まさに k が両者を結合するから)。
→ **R² 単独に依存しない**。k* を**三角測量**する:
  1. R²(k) の低下(init 支配の喪失)
  2. **seed 間の発散**(同一条件・異 seed の軌跡分散 = 経路依存)
  3. **early-warning signals**(分散・自己相関のピーク)
の3つが揃う点を k* とする。※ R² の破綻それ自体も転移のシグナル。

## 効く seam / no-fingerprint
- `engine/metrics` / `analyze`: 秩序変数・R²(k)・seed 発散・early-warning を算出。k は掃引パラメータ(分野3のゲイン)。
- すべて観測者frame。結果を hardcode しない。

## 関連
[[state-update__open2-overview]](k= フィードバックゲイン)/ [[network__diffusion-overview]](カスケード2レジーム)/ 分野8(計測・validation)/ [[project-charter]]
