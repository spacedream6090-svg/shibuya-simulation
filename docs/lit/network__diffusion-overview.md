# 分野5 概観 — ネットワーク科学・拡散理論(伝播 = M1 指標b の構造)
- 分野: world/perception, propagation, factors | 重要度: P0
- 出典: Centola & Macy 2007(複雑contagion)/ Granovetter 1978(閾値モデル, AJS)/ Watts 2002(global cascades, PNAS)/ 複雑contagion レビュー(arXiv 1710.07606)

## 中核機構
- **simple vs complex contagion(Centola & Macy 2007)**: 情報・病気は **simple**(1接触で伝わる)。だが**行動・規範・運動は complex contagion**(採用に**複数の補強的接触**が必要 = 社会的正統化/信用/相補性)。
- **ネットワーク構造の効き方**: 弱い紐帯・small-world は simple には良いが **complex は遅くする**。complex には**クラスタリング/"wide bridges"** が要る(なければカスケードが起きない)。
- **閾値モデル(Granovetter 1978)**: 各人に**個人閾値**(何割が採用したら自分も採用するか)。閾値は**異質分布** → 集団的帰結。応用: 暴動・革新採用・噂・ストライキ・同調。
- **global cascades(Watts 2002)**: 小さな衝撃から稀に**巨大カスケード**。閾値ルール + 疎ランダムネットで**2つの感受性レジーム**。

## 我々への含意(設計を変える)
- **ラベル/運動/世界改変行動の伝播は complex contagion**。→ `labeling/propagation` を **単一接触の SI/SIR でなく閾値型(複数補強)** にする。「噂は接触で広がる」素朴モデルは誤り。
- **ネットワーク・トポロジーが伝播を左右**(クラスタリング/wide bridges)。→ `world` の社会network 構造を**パラメータ化**。
- **異質な採用閾値/感受性 = エージェント特性**(Granovetter)→ `factors`(感受性/同調)、初期分布は OPEN#3。
- **カスケードの2レジーム(Watts)= 相転移的**。→ 分野7(複雑系・k*)と直結。M1(d) 集団的高コスト行動も complex contagion + 閾値 + コミット少数派(分野4 Centola)で説明。

## no-fingerprint
- 閾値/感受性は**エージェント特性(異質初期分布)**であって台本でない。カスケードが起きるかは topology + 閾値 + コミット少数派 から**創発 → 観測**。

## 関連
[[labeling__cultural-evolution-overview]](分野4: tipping/naming)/ 分野7(複雑系・相転移=カスケードのレジーム)/ [[project-charter]]
