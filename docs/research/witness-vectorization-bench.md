# witness走査の高速化×決定論: 実機ベンチ(WITリサーチ レーン4)

> 2026-08-20。開発機(Python 3.12.10 / numpy 2.5.0)での実測。N=25k・3km角・F=fact数。
> 検証スクリプトはセッションscratchpadのexact.py/bench*.py/verify.py(リポ外)。

## 1. 結論
**第一候補: 均一グリッド+二段フィルタ(二乗距離→境界帯のみmath.hypot再判定)。
実測72-93倍(F=200-500)。ビット同一性は6,620 fact試行でミスマッチ0を機械確認。**
ただし走査を93倍にしても律速は信念書込み側(57s/日)に移る=モデル再設計が主・高速化が従。

## 2. 浮動小数点の同一性(設計の分岐点)
- **np.hypotはmath.hypotとビット不一致(17.6%の入力で相違)**=使用禁止(numba#1570が独立裏付け)。
- 引き算・掛け算はnumpyとPythonで完全ビット一致→**二乗距離の前置判定は成立**。
- hypot(dx,dy)>R と dx²+dy²>R² の判定不一致は境界の相対1ulp帯のみ。ガード帯**BAND=2^-48**
  (R=60mで厚さ~2.7e-14m)で誤判定0/500,000・実運用ヒットほぼ0。境界候補のみ現行式で厳密再判定。
```python
s = dx*dx + dy*dy;  t = radius*radius
inside = (s <= t*(1.0-BAND))
境界帯 (t*(1-BAND) < s < t*(1+BAND)) → math.hypot で現行式そのまま再判定
```
- numexpr・FMA融合は一致を壊すので禁止。

## 3. 案の比較(実測・F=200/step)
| 案 | 時間 | 倍率 | 決定論リスク | 規模 |
|---|---|---|---|---|
| 現行(素朴二重ループ) | 660ms | 1.0x | — | — |
| _present巻上げ+タプル展開のみ | 159ms | 4.1x | なし | ~25行 |
| 全体ベクトル化+二段フィルタ | 13.9ms | 47x | 低 | ~60行 |
| **グリッド(cell=120m・stableソート)+二段** | **9.1ms** | **72x**(F=500で93x) | 低(順序完全保存) | ~100行 |
| 増分(候補縮小) | 悪化0.49x | — | 中 | 棄却 |
| 反転(fact索引+個体ループ) | 131ms | 5x | 低 | 棄却 |
| cKDTree | 同等 | — | 中(返却順未規定・scipy版差) | フォールバック |

- グリッド決定論: argsort(kind="stable")=セル内id昇順保存・searchsorted決定的・出力は昇順のまま。
- **250kスケール**: 全体ベクトル化576ms/step(Nに線形)に対しグリッド22.8ms(局所密度依存)=25倍差。
  本選規模ではグリッド一択。セル幅は60-240mで平坦(cell≈2rでよい・感度低)。

## 4. 書込み側(空間索引が効かない部分)
- _set_belief+Event+logger.log=1.78µs/件→32M件/日で57s。**テンプレートdict+.copy()で0.84µs(2.1倍)**
  (logger.logがpayload.setdefaultするため共有不可・copy必須)。
- recとpayloadは同一(fact,step)内で全受信者共通(個体差はEventのagent_id/x/yのみ)が根拠。
- 市域全体fact(radius<=0)は選択0.44msに対し書込み317,020件≈560ms=1,000倍非対称。
  →書込み体積を減らすのはチャネル/注意モデル側の仕事。

## 5. 段階導入
- Stage1(リスクゼロ・2.8-4.1倍): _present巻上げ(actorはid昇順位置に挿入しL1順序不変)・
  radius<=0の距離スキップ・テンプレコピー。
- Stage2(本命・72-93倍): xs/ys/present抽出(25k:2.75ms/250k:27.6ms)→グリッド+二段フィルタ。
- 検収: 同値6,620試行ミスマッチ0(実施済み)・順序昇順assert・境界人工点でフォールバック発火・
  L1バイト一致(フルゲート+24stepスモーク)・**np.hypot禁止をスキャンで機械固定**。

## 6. 参考
- AMBER (arXiv:2601.16292) Polars列指向でMesa比最大1118倍 / ABMax (arXiv:2508.16508)
- GriSPy (arXiv:1912.09585) 固定半径近傍のnumpy実装 / Müller spatial hashing (tenMinutePhysics)
- numba#1570 (math.hypot vs numpy.hypot) / bpo-41513 (高精度math.hypot)
- PySPH (arXiv:1909.04504) / BioDynaMo (arXiv:2301.06984) / Agents.jl vs Mesa
