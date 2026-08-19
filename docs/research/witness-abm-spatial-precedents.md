# 空間ABM・大規模シムの情報伝播/知覚の先行(WITリサーチ レーン2)

> 2026-08-20。witness再設計の計算構造とモデル構造の先行調査。

## 1. 転用アイデア上位5(計算量付き)

### ★1 factを「場所」に紐づけ人×factの直積を消す(EpiSimdemics/Loimos型)
- 疫学の超大規模ABM(米3億人・15億辺・352,000コアで120日12秒)は人×人を一切走査せず
  **person-location二部グラフ**=場所ごとの局所処理で暴露を計算。
- 現行O(F×N)/step → **O(F×n̄_place)**。全体はO(延べ訪問数)でN×Fの積が現れない。
  L=2,000箇所ならfact1件あたり250,000→125人=**2,000倍削減**。
- 「半径60m×1時間」は「同一場所への訪問区間の重なり」(Loimos流)として再定義するのが素直。

### ★2 チャネル側で到達領域を1度だけ焼く(VCA sign-centric / FLAME GPU)
- 避難シムの標識可視域VCA(buildingEXODUS): 標識ごとに可視領域を事前計算し実行時は
  エージェント側O(1)判定。「大人口ではoccupant-centricより効率的」と明言。
- FLAME GPUのspatial partitioned messagingは局所クエリO(n)→O(1)・数億体実績。
- 店内系は「店舗=チャネル」で領域自明(事前計算すら不要)。

### ★3 「全員にサイコロ」でなく「当選者数を先に引きK人選ぶ」(rejection sampling+counter-based RNG)
- K~Binomial(n,p)を1回引きK人だけ選ぶ: O(n)→O(K)。p≪1なら1-2桁削減。
- **決定論との両立**: hash(seed,step,fact_id,agent_id)のcounter-based乱数(Philox/Threefry型)は
  状態レス=走査順・並列度・分割に非依存。既存の乱数stream 0本のまま確率化できる。
- Composition & Rejection(St-Onge 2018)は1イベントO(log log N)・標準SSA比最大1000倍。

### ★4 注意ゲート=有限スロットk+顕著性top-k+減衰(Weng/Moussaïd/MIDSim/Weyns)
- 数値アンカー: MIDSim注意予算**B_att=10**(超過サンプリング・フィード長は打切り幾何K_max=5)・
  Weng 2012の注意確率p_r=0.016・Moussaïd 2009の容量配分(100%×1 or 70+10×3)・SFM相互作用はk≈12で飽和。
- 学術語彙: Weyns (2004)のfocus(何を見るか宣言)/filter(絞る)/perceptual law(制約)がそのまま使える。
- 第142 ATT層A(priority+top-k_i∧θ)は本文献群と同型=fact側にも同機構で一貫。

### ★5 毎step全走査をやめる(イベント駆動+Verlet skin)
- MATSim/HERMES(スイス520万体)「大規模では全グラフ走査は無駄」。
- Verlet skin: 候補半径r+s(s=再構築間隔中の最大移動距離)でリストを数step使い回し。
- 補助: 優先度キュー(Next Reaction Method)・読み/書きダブルバッファ(krABMaga・決定論に有利)。

## 2. 「全員が全てを知る」モデルの弊害(実証)
- **Weng, Flammini, Vespignani & Menczer (2012)** Sci Rep 2:335: 有限注意への競争なしでは
  実測ミーム人気分布を再現できない(p_r=0.016, t_w=1.0で実データ一致)。
- **Hunter, Mac Namee & Kelleher (2020)** JASSS 23(4)14: 均質混合は感染規模を過大評価
  (ABM対比 Wilcoxon p≈2.2e-16)。
- **Li & Tao (2026)** arXiv:2603.00113: 集合的帰結はagent-environment co-dynamicsに支配される。
  「明示的なexposure機構とスケジューリングを持つ環境込みMarkov gameとして再定式化せよ」。
- **Kotseruba & Rasouli (2023)**: 全方位・瞬時知覚の仮定は歩行者挙動を系統的に歪める。
- 「半径内全員目撃」を名指しで批判した文献は無し(上記の組合せで論拠十分)。

## 3. その他の先行(要点)
- **stigmergy/Digital Pheromone**(Parunak & Brueckner): 場所側が濃度場(aggregation/propagation/
  evaporation)を保持・移動体は局所読取のみ=O(場所数)/stepでN非依存。
- **チャネル分離のLLM時代先行=MIDSim**(CIKM 2026): social stream(フォロー)とalgorithmic stream(推薦)を明示分離。
- **Bass二経路**(外部p=マスメディア/内部q=口コミ)・Rogersのmass media(知識段階)vs interpersonal(説得段階)。
- **HLA/DDM interest management・MMOのArea of Interest管理**: 「誰にこのイベントを届けるか」の
  専門分野が丸ごと存在(fact=update region・注意範囲=subscription region)。見落とされやすい転用元。
- 犯罪ABM(awareness space=部分観測の明示モデル)はあるが**目撃確率の関数形の先行なし**。
  津波避難ABMレビュー53本は情報獲得モデル化が未成熟(借りるべき先行なし)。

## 4. 主要出典
- Barrett, Bisset, Eubank, Marathe et al. EpiSimdemics (SC'08) / Kitson et al. Loimos (IPDPS 2025, arXiv:2401.08124)
- FSEG Greenwich, Visibility Catchment Area (buildingEXODUS) / FLAME GPU (NVIDIA) / BioDynaMo (arXiv:2301.06984)
- St-Onge, Young, Hébert-Dufresne & Dubé (2018) arXiv:1808.05859 / Salmon et al. (2011) Random123/Philox
- Weng et al. (2012) Sci Rep 2:335 / Moussaïd, Helbing & Theraulaz (2009) arXiv:0909.2757
- Hunter et al. (2020) JASSS 23(4)14 / Li & Tao (2026) arXiv:2603.00113
- Weyns, Steegmans & Holvoet (2004) Applied AI 18 / Parunak & Brueckner digital pheromones
- Liu et al. MIDSim (CIKM 2026, arXiv:2606.13140) / Rand et al. (2015) JASSS 18(2)1
- MATSim HERMES / krABMaga (JASSS 27(2)4) / Turner et al. (2001) isovist/VGA
- Antelmi et al. (2024) / Malleson et al. 犯罪ABM / 津波避難ABM系統的レビュー(PMC9533266)
