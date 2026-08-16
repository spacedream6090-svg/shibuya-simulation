# 群衆物理の認知二層化リサーチ — 「オブジェクト注意 / 人としての注意」と物理ゾーン痩身

作成: 2026-08-16(リサーチのみ・実装なし)。
対象: `physics.zones_enabled` 系(SFM+ORCA・3ゾーン)の超線形コスト(prof10k6 で実行時間の 74%)。
発注: ユーザー設計指示「人は周りにいるすべての人にオブジェクトとしての注意は無意識に持つが、
関係性が発生する“人”としての注意を向ける相手は少数。多くの場合、世界の物理状態や
オブジェクトとしての認識の方が優位。その認知の二層を反映した実装にしてほしい」。

関連: `docs/plans/codex-review-triage.md` A10 / PENDING「★物理ゾーン痩身の方式」/
`docs/research/physics-engine-selection.md`(P2 決定)/ `docs/research/p4-calibration-research.md`(P4 較正)。

---

## 0. TL;DR(結論先出し)

- ユーザーの二層仮説は文献と**方向が一致**する。ただし実証はさらに強い主張をしている:
  「オブジェクトとしての注意」ですら**視野内・遮蔽されていない・主に前方の少数近傍**(第一近傍殻、
  鳥群なら 6–7 体、人混みなら影響重みが距離で指数減衰)に限られ、**全員への全ペア相互作用は
  認知モデルとしても過剰実装**である。遠方はさらに個体ですらなく**統計量(密度・流れ)として知覚**される。
- 現実装の全ペア計算は既に距離カットオフを持つ(対人 2.0 m・far 項 4.7 m・知覚 2.0 m・ORCA 10 m)のに、
  **候補列挙だけが O(N²)** で残っている。つまり第一段は「意味論を 1 ビットも変えずに」セル法
  (自前 `WallField` と同型・in-repo 前例あり)で痩せられる。
- prof10k6 の最大項 `_accumulate` 166 s は**力ですらなく知覚・観測の集計**。ここはセル法+ベクトル化
  (+任意で人間の知覚時定数 ~0.5 s への間引き)で 1 桁以上落ちる。
- 推奨: **案A(同値なセル法+観測層痩身)→ 必要なら案B(近傍数の認知的上限=topological cap)** の
  段階投入。案C(遠方=密度場ハイブリッド)はゾーン拡張・飽和密度でなお足りないときの保険。

---

## 1. ユーザーの認知二層仮説と文献の対応(正直な突合)

仮説の分解:
1. 「周りのすべての人にオブジェクトとしての注意は無意識に持つ」
2. 「“人”としての注意(関係性が発生する相手)は少数」
3. 「多くの場合、世界の物理状態・オブジェクト認識の方が優位」

### 支持される点

- **二層構造そのもの**は文献と一致する。歩行の操舵は視覚誘導の低次過程(意識的な対人認知を要しない
  ヒューリスティクス)で説明でき(Moussaïd 2011)、一方で「人として」追跡・認識できる対象は
  数個に限られる(多重物体追跡の容量 4–5 個: Pylyshyn & Storm 1988)。維持できる関係の数にも
  認知上限がある(Dunbar 1992)。**上層(人としての注意)が少数選抜であることは強く支持される。**
- 「物理状態・オブジェクト認識が優位」も歩行時の注視実測と整合する: 歩行者の注視の大半は
  **地面・進路上の障害**に向かい、他者への注視は少数・短時間である(Kitazawa & Fujiyama 2010;
  Fotios et al. 2015 は他歩行者への注視は距離 ~10–15 m・1 回 ~500 ms 程度と実測)。
  他者を注視するかはタスク依存で、衝突回避だけなら対人注視はさらに減る(Hessels et al. 2020)。

### 文献が仮説を「修正」する点(実装に効く)

- **修正1: 「すべての人に」は成立しない。** オブジェクトレベルの(無意識の)相互作用ですら、
  実証的には (a) 影響重みが距離とともに指数減衰する局所近傍(Rio et al. 2018)、
  (b) 数としては 6–7 体程度のトポロジカル近傍(鳥群: Ballerini et al. 2008)、
  (c) 決定的なのは**視覚的遮蔽** — 近くの人が遠くの人を隠すため、密な群衆では第一近傍殻より
  外はそもそも網膜に届かない(Wirth et al. 2023 は metric/topological/visual を直接比較して
  **visual が最良、topological は棄却**と結論)。
  → **全ペア力積算は「オブジェクト注意」の実装としても過剰**であり、近傍制限は近似ではなく
  むしろ実証に近づく方向。
- **修正2: 遠方は「オブジェクト」でもなく統計量。** 視覚系は集団を個体の列挙でなく
  **アンサンブル統計(平均・分散)として要約知覚**する(Whitney & Yamanashi Leib 2018)。
  工学側もこれに対応する近似系譜を持つ: 群衆を密度・流れの連続体として扱う
  (Hughes 2002; Treuille et al. 2006)、近距離=個体・遠距離=連続体のハイブリッド(Narain et al. 2009)。
  → ユーザーの「世界の物理状態が優位」は、**遠方場を密度場で置換する**方向へ素直に翻訳できる。
- **整合の確認: 上層は本リポジトリで実装済み。** 「人としての注意」レーンは物理と別系統で既に
  少数選抜になっている(`src/society/dunbar.py` のダンバー枠+休眠/再会、closeness 台帳、
  同席・遭遇ベースの関係形成)。今回の対象はあくまで**下層(物理)の痩身**であり、
  二層の境界(物理は位置と混雑だけを上層へ渡す: `Perception.body` の 3 欄)は現行のまま保てる。

---

## 2. 文献ごとの要点(URL は Web で実在確認済みのもののみ)

### 系譜1: 視覚・認知ベースの歩行者モデル

| 文献 | 要点 | 本件で使える点 |
|---|---|---|
| Moussaïd, Helbing & Theraulaz (2011) *How simple rules determine pedestrian behavior and crowd disasters*, PNAS 108(17):6884-6888. [PNAS](https://www.pnas.org/doi/full/10.1073/pnas.1016507108) / [arXiv](https://arxiv.org/abs/1105.2152) | 操舵を力の重ね合わせでなく**視覚ヒューリスティクス 2 本**(視野内の候補視線ごとの「最初の障害までの距離」で方向と速さを選ぶ)で説明。身体接触は別途物理力で扱い、極端密度では両者の組合せが crowd turbulence を生む | 「操舵=視覚(視野内・有限視程)/接触=物理」という**二層分離の正当化**。相互作用は視野内の遮蔽物までで打ち切ってよい(後方・遠方は操舵に寄与しない)という理論的根拠 |

### 系譜2: 歩行者の注視・注意の実証

| 文献 | 要点 | 本件で使える点 |
|---|---|---|
| Kitazawa & Fujiyama (2010) *Pedestrian Vision and Collision Avoidance Behavior: Investigation of the Information Process Space of Pedestrians Using an Eye Tracker*, PED2008, Springer, pp.95-108. [Springer](https://link.springer.com/chapter/10.1007/978-3-642-04504-2_7) / [UCL Discovery](https://discovery.ucl.ac.uk/19121) | 頭部装着アイトラッカー実験。注視の大半は**地表面**(直近の環境ハザード検出)、注視は半円でなく**前方の円錐状領域**に集中 | 情報処理空間(IPS)は前方円錐+近距離 = SFM の異方性 λ と近距離カットオフの実証的裏付け。「全方位・全員」への注意は注視レベルで存在しない |
| Fotios, Yang & Uttley (2015) *Observing other pedestrians: Investigating the typical distance and duration of fixation*, Lighting Res. Technol. [SAGE](https://journals.sagepub.com/doi/10.1177/1477153514529299) / [PDF](https://eprints.whiterose.ac.uk/id/eprint/89559/1/fotios%20et%20al%202015%20pedestrian%20distance.pdf) | 他歩行者への注視は距離 ~10.3 m(補正後 ~15 m)・持続 ~480-500 ms | 対人の「見る」行為の時定数は **~0.5 s**。知覚量(密度・接触)を 0.05 s ごとに全ペア再計算する現行観測層が知覚モデルとして過剰である根拠(観測間引きの正当化) |
| Hessels, van Doorn, Benjamins, Holleman & Hooge (2020) *Task-related gaze control in human crowd navigation*, Atten. Percept. Psychophys. 82:2482-2501. [Springer](https://link.springer.com/article/10.3758/s13414-019-01952-9) | 群衆内歩行の注視はタスク依存。衝突回避のみが課題のとき対人注視は少なく、社会的情報(アイコンタクト)探索の課題を足すと増える | 「オブジェクト回避」と「人としての注意」が**注視配分レベルで分離可能**という実証 = 二層仮説の直接的な支持。物理層は前者だけ担えばよい |

### 系譜3: 相互作用近傍の実証(いくつまで・どこまで効くか)

| 文献 | 要点 | 本件で使える点 |
|---|---|---|
| Rio, Dachner & Warren (2018) *Local interactions underlying collective motion in human crowds*, Proc. R. Soc. B 285:20180611. [Royal Society](https://royalsocietypublishing.org/doi/10.1098/rspb.2018.0611) | 実群衆+VR 群衆で近傍追随を実測。個人は近傍の**重み付き平均**に整列し、重みは**距離とともに指数減衰**(ソフトな計量近傍)。応答遅れは半径 1.5-2 m 内で ~1 s、3-4 m で 1-3 s | 物理層の対人結合は「近距離ほど強い重み+数 m で実質消滅」でよいという定量根拠。現行 far 項カットオフ(体表間 4.7 m)はこの範囲と整合 |
| Warren (2018) *Collective Motion in Human Crowds*, Curr. Dir. Psychol. Sci. 27(4):232-240. [SAGE](https://journals.sagepub.com/doi/full/10.1177/0963721417746743) | 上記系列のレビュー。群衆の集団運動は「近傍の重み付き平均」への追随という局所則から創発 | 近傍平均モデルの総説。改修の設計語彙(neighborhood of interaction)の出典 |
| Dachner, Wirth, Richmond & Warren (2022) *The visual coupling between neighbours explains local interactions underlying human 'flocking'*, Proc. R. Soc. B 289:20212089. [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8889174/) | 距離減衰を自由パラメータにせず**光学(角速度・光学的膨張のキャンセル)から導出**。完全可視の相手なら 9-15 m 先まで結合しうるが、**遮蔽が距離減衰の主因**(近い人が遠い人を隠す二重減衰) | 「減衰は光学+遮蔽の帰結」= 密な群衆ほど実効近傍が縮む。**高密度ゾーンほど近傍 cap が正当化される**(cap は低密度でこそ効かせすぎに注意) |
| Wirth, Dachner, Rio & Warren (2023) *Is the neighborhood of interaction in human crowds metric, topological, or visual?*, PNAS Nexus 2(5):pgad118. [OUP](https://academic.oup.com/pnasnexus/article/2/5/pgad118/7160859) / [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10187661/) | 3 仮説を直接比較。**topological(固定 k 体)は棄却**、metric は部分的、**visual(距離+遮蔽)が最良**。近傍範囲は固定半径でなく「手前の人が奥を完全に遮蔽する距離」で決まる | 近傍選抜の理想は「可視性重み」。実装近似としては「距離カットオフ+各方位で手前優先」が visual の一次近似、固定 k は二次近似(ただし高密度では両者はほぼ一致する) |
| Ballerini et al. (2008) *Interaction ruling animal collective behaviour depends on topological rather than metric distance*, PNAS 105:1232-1237. [arXiv](https://arxiv.org/abs/0709.1916) | ムクドリ群の 3D 実測。各個体は距離によらず**平均 6-7 羽の最近傍**とだけ相互作用(密度非依存) | 「相互作用相手の数は 1 桁」という古典的定量。ORCA の `neighbor_cap=12` の妥当性の傍証。ただし人間では Wirth 2023 が topological を棄却している点は正直に記す(人では遮蔽=visual が本命) |

### 系譜4: SFM の異方性・視野(現実装が既に持つもの)

| 文献 | 要点 | 本件で使える点 |
|---|---|---|
| Helbing & Molnár (1995) *Social force model for pedestrian dynamics*, Phys. Rev. E 51:4282-4286. [APS](https://link.aps.org/doi/10.1103/PhysRevE.51.4282) | SFM 原典。知覚の方向依存(視野内の刺激を強く受ける)を重み c(λ) で表す | 現実装の異方性 w = λ+(1-λ)(1+cosφ)/2(`sfm_core.py:357-360`)の出典。**後方の相手は既に弱められている**が、計算自体は全ペア分やってから捨てている |
| Helbing, Farkas & Vicsek (2000) *Simulating dynamical features of escape panic*, Nature 407:487-490. [Nature](https://www.nature.com/articles/35035023) | 確定パラメータ(A=2000 N, B=0.08 m 等)。B=0.08 m の指数斥力は**数十 cm で実質ゼロ** | 現実装の対人項カットオフ 2.0 m(`sfm_core.py:69`)は既に保守的に広い = 近傍リスト化しても切り捨てる寄与は元々 0 |

### 系譜5: 近傍数制限の実装前例

| 文献/実装 | 要点 | 本件で使える点 |
|---|---|---|
| van den Berg, Guy, Lin & Manocha (2011) *Reciprocal n-Body Collision Avoidance* (ORCA) + 参照実装 RVO2. [RVO2 サイト](https://gamma.cs.unc.edu/RVO2/) / [パラメータ文書](https://gamma.cs.unc.edu/RVO2/documentation/2.0/params.html) | RVO2 は `maxNeighbors`(例題 10)+`neighborDist` を**kd-tree** で選抜するのが標準。「maxNeighbors が大きいほど遅く、小さすぎると安全でない」と文書に明記 | **本家ですら全ペアは参照実装ではない**。現行 `orca_core.py` は cap=12 を持ちながら選抜を O(N² log N) の全体 argsort でやっている = kd-tree/セル法に置換して意味論そのまま |
| 分子動力学のセル法(linked-cell)・Verlet リスト(標準教科書事項; 例: [MOLDY 論文](https://arxiv.org/pdf/1107.2619)) | カットオフ付きペア相互作用は格子セルに登録して隣接セルのみ走査 = O(N) | **本リポジトリに前例あり**: 壁項の `WallField` 空間ハッシュ(`sfm_core.py:82-200`)は「候補は上位集合 → 寄与 0 が混ざるだけで力はビット一致」+同値性テストという移植可能な設計をすでに確立している |

### 系譜6: 遠方場の連続体近似

| 文献 | 要点 | 本件で使える点 |
|---|---|---|
| Hughes (2002) *A continuum theory for the flow of pedestrians*, Transp. Res. B 36:507-535. [Univ. Melbourne](https://findanexpert.unimelb.edu.au/scholarlywork/255366-a-continuum-theory-for-the-flow-of-pedestrians) | 歩行者流を密度場・ポテンシャル場の連続体として定式化 | 遠方の他者を個体でなく密度として扱う理論的原型 |
| Treuille, Cooper & Popović (2006) *Continuum Crowds*, ACM TOG 25(3):1160-1168 (SIGGRAPH). [ACM DL](https://dl.acm.org/doi/10.1145/1179352.1142008) | 動的ポテンシャル場で大域誘導+他者回避を**個体ペア計算なし**で解く。数千体をリアルタイム | 「遠方はペアでなく場」の実装実証。ただし完全連続体は個体の異質性(v0・半径・目的地)を殺すので、本シムでは**遠方項のみ**の置換に留めるのが適合 |
| Narain, Golas, Curtis & Lin (2009) *Aggregate Dynamics for Dense Crowd Simulation*, ACM TOG 28(5) (SIGGRAPH Asia). [ACM DL](https://dl.acm.org/doi/10.1145/1618452.1618468) / [プロジェクト+PDF](http://gamma.cs.unc.edu/DenseCrowds/) | **離散個体+連続体の二重表現**。連続体側の unilateral incompressibility で高密度の詰まりを扱い、個体ペア回避を加速。10 万体級 | 「近距離=個体/遠距離・高密度=場」のハイブリッドの直接の前例。案C の設計指針 |

### 系譜7: 人としての注意(社会的認知の容量制限)

| 文献 | 要点 | 本件で使える点 |
|---|---|---|
| Pylyshyn & Storm (1988) *Tracking multiple independent targets*, Spatial Vision 3:179-197. [PDF (Rutgers)](https://ruccs.rutgers.edu/images/personal-zenon-pylyshyn/docs/storm88.pdf) | 同時に「個体として」追跡できる動目標は **4-5 個** | 群衆の中で「人として」同時に注意を向けられる相手の上限。物理近傍 cap(~12)より人注意レーンの同時対象の方がさらに少ない、という層の分離の定量 |
| Whitney & Yamanashi Leib (2018) *Ensemble Perception*, Annu. Rev. Psychol. 69:105-129. [Annual Reviews](https://www.annualreviews.org/doi/10.1146/annurev-psych-010416-044232) / [PDF](https://whitneylab.berkeley.edu/PDFs/Ensemble_perception_2018.pdf) | 視覚系は集団を**要約統計量**(平均方向・平均速度・群れの気分まで)として一瞥で知覚する。個体表現の容量限界を回避する機構 | 「遠方・多数はオブジェクトの集合ですらなく統計量」= 遠方場の密度場近似(案C)と観測層の集約値化の認知的正当化 |
| Dunbar (1992) *Neocortex size as a constraint on group size in primates*, J. Hum. Evol. 22:469-493. [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/004724849290081J) / [解説](https://en.wikipedia.org/wiki/Dunbar's_number) | 維持できる関係の数は認知容量で上限(人間 ~150) | 本リポジトリでは実装済み(`src/society/dunbar.py`)。二層の上層は既に有界 = 今回触らない、の確認 |

---

## 3. 現実装の構造と計算量の内訳(ファイル:行 + prof10k6 突合)

### 3.1 構成(読んだ範囲の要約)

- ゾーンは 3 つ(`conf/zones_shibuya.yaml` / `conf/finals_observe.yaml:372-413`):
  scramble(ORCA・840 m²・信号ゲート)/ hachiko_square(SFM・~1,100 m²)/ center_gai(SFM・~500 m²)。
  いずれも `dt_sub: 0.05` s、世界 step 600 s → **1 世界 step あたり最大 12,000 サブステップ**
  (`physics.py:23,331`。ゾーンが空になれば打ち切り)。`neighbor_cap` 既定 12(`world/zones.py:133`)。
  finals は SFM の較正 far 項 ON(`a2=0.119, b2=1.890, cutoff_factor=2.5` → 体表間 4.725 m で打ち切り)。
- 実行の作用点は `physics.phase → _run_zone`(`src/society/physics.py:309-450`)。サブステップごとに
  (3b) `engine.step(dt)` → `_accumulate`(観測)→ (3c) 通過点前進・退場、の順(`physics.py:386-423`)。

### 3.2 全ペア計算の所在(発注 (a))

| # | 箇所 | 形 | 計算量/サブステップ | 備考 |
|---|---|---|---|---|
| 1 | SFM 対人斥力 `sfm_core.Crowd.forces` (`sfm_core.py:346-371`) | `diff (N,N,2)`→`d (N,N)`→exp/異方性 | O(N²) | **カットオフは既にある**(体表間 2.0 m: `sfm_core.py:69,362`)が、候補列挙が全ペア |
| 2 | SFM 近傍 cap の適用 (`sfm_core.py:365-368`) | `argsort(d)` ×2(順位行列) | O(N² log N) | cap=12 を効かせるためだけに**全体を 2 回 argsort** — prof の `argsort 26 s` の一因 |
| 3 | 較正 far 項 `_CalibratedCrowd._far_forces` (`physics.py:626-649`) | `diff (N,N,2)` 全ペア | O(N²) | 体表間 4.725 m + taper 1 m で打ち切り。**cap は意図的に掛けない**(`physics.py:602-604`: ρ=3/m² では最近傍 12 体が ~1.1 m 内で cap が far を殺す=P4-1 実測)→ **prof の `_far_forces 53 s`** |
| 4 | 観測 `_accumulate` (`physics.py:772-826`) | ①帯・ヒスト・反転の **Python ループ** (781-800) ②`min_gap` の O(N²) triu (`orca_core.py:350-359`, 呼び出し 803) ③**全ペア距離行列** (810-813) ④密度・接触の **Python ループ** (818-825) | O(N²) + O(N) Python | **prof 最大項 166 s / 総 577 s**。力ですらなく知覚(density_radius 2.0 m・contact_gap 0.05 m)と診断(min_gap)の集計。毎 0.05 s 実行 |
| 5 | ORCA 近傍選抜 `OrcaCrowd.step` (`orca_core.py:515-520`) | 全ペア距離 + `argsort(stable)` | O(N² log N) | cap=12・neighbor_dist=10 m を**全体 argsort で**選抜。本家 RVO2 は kd-tree |
| 6 | ORCA LP 本体 (`orca_core.py:534-544`) | 個体ごと Python で LP2/LP3 | O(N·k) だが**純 Python** | prof の `ORCA 98 s` の主体(近傍選抜+LP+`.tolist()` 変換) |
| 7 | ORCA 事後分離 `separate_positions` (`orca_core.py:362-424`, 呼び出し 549-551) | `triu_indices` 全ペア検出 | O(N²)/サブステップ | 解消は逐次だが**検出が毎回全ペア** |
| 8 | 入場ゲート判定 `_admit` (`physics.py:486-499`) | 待機×在場の総当たり | O(W·M)/サブステップ | 信号青のときのみ。赤解放直後の scramble で W が膨らむ |
| 9 | 入場候補の全個体走査 (`physics.py:337,351` + `_by_id`=`physics.py:1000-1001`) | 全 agent の sort+走査 ×2/ゾーン | O(N_total log N_total)/step | ペア計算ではないが 25 万体では 1 step に 6 回の 25 万体 sort。route 保持者だけの事前索引で線形化可能(付記) |

### 3.3 遠方場と近接場の現在の分かれ方(発注 (b))

現実装は既に「二層」に**なりかけている**:

- **近接場** = Helbing 標準項(体表間 ≤2.0 m・異方性 λ=0.5 で後方減衰)+ ORCA(≤10 m・cap 12)。
- **遠方場** = P4-2 較正で足した長距離 social 項(体表間 ≤4.725 m・`_far_forces`)。
  「遠方」と呼んでいるが実体は**中距離のペア項**であり、真の遠方(ゾーン外・視程外)は
  もともとグラフ層の混雑係数(`_graph_speed` の `_congestion`)が担っている。
- **知覚への翻訳** = `blocked/contact/local_density` の 3 欄のみ(`physics.py:980-997`)。
  上層(発火・LLM)へは集約値しか渡らない = **二層の境界面はすでに細い**。

つまり不足しているのは層の設計ではなく、**下層内部の候補列挙が全ペアである**こと、および
**観測が力学と同じ 20 Hz で全ペア再計算される**ことの 2 点。

### 3.4 prof10k6 との突合(発注 (c))

prof10k6(cProfile・10k 体×6 step・`docs/log/devlog.md` Entry 134): 総 577 s・**物理 74%(≈427 s)**。

| prof 項目 | 実測 | 対応する表 3.2 の # | 置換できる文献系譜 |
|---|---|---|---|
| `_accumulate` | 166 s(総の 29%・物理の 39%) | #4 | 知覚は局所(系譜2: 注視は前方円錐・対人固視 ~0.5 s)+集約統計で足りる(系譜7: ensemble perception)→ セル法+ベクトル化+(任意)間引き |
| ORCA 一式 | 98 s | #5,6,7 | 近傍選抜は kd-tree/セル法が本家標準(系譜5: RVO2 `maxNeighbors`)。LP は認知と無関係の実装コスト(numba/ベクトル化は付記) |
| `_far_forces` | 53 s | #3 | 中距離結合は距離減衰+遮蔽で局所(系譜3: Rio 2018 指数減衰・Wirth 2023 visual)→ セル法(同値)or 密度場(系譜6) |
| `argsort` | 26 s | #2,5 | cap 選抜は k 近傍問題(系譜5)→ セル法で候補を絞ってから選抜 |
| (残余 ≈84 s) | SFM 基本項 #1・writeback・admit 等 | #1,8,9 | #1 はカットオフ 2.0 m の局所項(系譜4: B=0.08 m で数十 cm スケール)→ セル法(同値) |

规模感の補足: ペア項は N_z²(N_z=ゾーン在場数)。ゾーン在場は総人口 N に比例して増えるが、
面積×物理密度で頭打ちになる(3 ゾーン計 ~2,450 m²・LOS E 級 2-3 人/m² で N_z 上限 ~5-7 千)。
つまり 25 万体では **N_z² 項は 10k 比でさらに 1-2 桁悪化してから飽和**する。全体走査 #9 だけは
飽和せず N_total に比例し続ける。

---

## 4. 改修候補 3 案

共通の前提: `physics.zones_enabled=false`(既定 OFF)では全案とも完全 no-op = golden 無風。
乱数は増やさない(セル法・場の構築は純関数)。resume 追加状態なし(位置の純関数)。

### 案A: 同値セル法 + 観測層痩身(「オブジェクト注意」の意味論を変えず計算だけ痩せる)

- **認知的解釈**: 変更なし。現行の近接場(カットオフ済み)がそのまま「オブジェクト注意」であり、
  カットオフ外の寄与はもともと 0。**認知モデルの主張を 1 つも動かさない**。
- **アルゴリズム**:
  1. `WallField` と同型の一様格子(セル辺 = 各項のカットオフ)を個体位置に張り、
     候補ペア (i,j) を「距離 ≤ カットオフを必ず含む上位集合」として列挙(`sfm_core.py:82-200` の
     設計・同値性テスト方式をそのまま移植)。合算は (i,j) 昇順の `np.bincount` = 決定論。
     対象: #1(r≈2.7 m)・#3(r≈5.4 m)・#4③(r=2.0 m)・#7 検出(r=体径+slack)。
  2. cap 選抜(#2,#5)は「セル近傍候補 → (距離, index) 昇順で k 選抜」に置換。現行の
     stable argsort と同じタイブレークを守れば**選抜集合も力もビット一致**。
  3. `_accumulate` の Python ループ 2 本(#4①④)を `np.digitize`/`bincount` でベクトル化。
  4. (任意・conf 既定 1=無変更)知覚サンプリング間引き `perception.sample_every_n_sub`:
     density/contact/min_gap を m サブステップに 1 回に。m=10 で 0.5 s 周期 = 対人固視の
     実測時定数(Fotios 2015)と同桁。`blocked`(速度平均)は O(N) なので毎サブステップ維持。
- **計算量**: ペア項 O(N_z²) → O(N_z·k̄)(k̄=カットオフ円内の平均人数 = ρπr²)。
  ρ=2 人/m² で #1 k̄≈46(N_z=1000 なら 22 倍減)・#3 k̄≈183(5.5 倍減)・#4 k̄≈25(40 倍減)。
  低密度ほど利得は大きい(夜間・平日はほぼ線形になる)。
- **期待 speedup(prof 実測からの見積り・10k 時点)**: `_accumulate` 166→~10-20 s
  (セル法+ベクトル化。間引き併用なら ~5 s)・`_far_forces` 53→~5-10 s・`argsort` 26→~2 s・
  SFM 基本項も同率減。ORCA は近傍選抜のみ改善(LP 本体は残る)で 98→~70 s。
  **物理計 427 s → ~120-160 s(約 3 倍)**。より重要なのはスケーリングが O(N_z²)→O(N_z·k̄) になり、
  25 万体で N_z が数倍になっても増分が線形で収まること。
- **軌跡品質への影響**: 力はビット一致(同値変換)。間引きを ON にしたときだけ L2/`Perception.body` の
  `local_density/contact` と `min_gap_m` の値がサンプリング粒度分変わる(力学は不変)。
  min_gap は「カットオフ内にペアが無い疎な瞬間」に値が出ない → 重なり検出という本来目的には十分だが
  記録意味論の変更として明記が必要。
- **検収指標**: (1) 全ペア参照実装との force **ビット一致テスト**(`tests/test_sfm_walls.py` 方式)
  (2) `physics.continuity()`(gate/interior accel_p99・reversal・jump_max・min_gap)の不変
  (3) 既定 OFF ランのバイト一致・resume==straight (4) mock10k での step 単価と RSS。
  基本図の再較正は**不要**(力が同値のため)。
- **工数**: 中(セル法本体+同値性テスト+ベクトル化。`WallField` の設計流用で 2-4 日級)。

### 案B: 認知的近傍への明示的制限(「オブジェクト注意」を文献値で有界化)

- **認知的解釈**: オブジェクト注意=**視野内・可視な少数近傍**という実証(Rio 2018 の指数減衰、
  Ballerini 2008 の 6-7 体、Wirth 2023 の遮蔽支配、RVO2 の maxNeighbors)を実装に昇格させる。
  遠方個体は遮蔽されて見えない=力を及ぼさない。仮説の「すべての人に」を文献に合わせて
  「見えている近傍に」へ修正する案。
- **アルゴリズム**(案A のセル法の上に):
  1. SFM 基本項にも cap を常時適用(現行は引数はあるが finals conf 未使用)。k は 10-16 を
     FD ベンチで選ぶ。選抜は「距離昇順+前方優先」(異方性 λ と整合する視野重み付き距離)。
  2. far 項は cap ではなく**可視性近似**で絞る: 方位を 16-32 セクターに割り、各セクター
     最前の 1-2 体だけ残す(Wirth 2023 の「手前が奥を遮蔽する」の一次近似)。
     ★cap をそのまま far に掛けてはならない(P4-1 実測: ρ=3 で cap が far を短距離項化する。
     `physics.py:602-604`)。セクター法なら「遠くても見えている相手」は残る。
  3. ORCA は現行 cap=12 のまま(既に認知的近傍で運用中)。
- **計算量**: O(N_z·k)、k は**密度に依らず有界**(セル法の k̄=ρπr² が高密度で膨らむ問題への防波堤。
  ρ=3 の far 項は k̄≈275 → セクター法で ≤64 に固定)。
- **期待 speedup**: 高密度時間帯(青信号パルス・イベント時)に案A 比でさらに far 項 4-8 倍・
  基本項 3-5 倍。低密度では案A とほぼ同じ(cap が効かないため)。**最悪ケースの上界が立つ**のが本質。
- **軌跡品質への影響**: 力が変わる(非同値)。文献的には全ペアより実証に近づく方向だが、
  P4 較正(far ON で A/B/C 受入合格)の**前提が変わるため再較正必須**。低密度で cap が
  効きすぎると希薄流の追従が変わりうる → 距離カットオフとの AND で守る。
- **検収指標**: (1) 基本図: `reference/physics_bench/calibrate.py` + Jülich データ
  (`data/juelich_fd_binned*.csv`)で A(±20%帯)/B(単調性)/C(包絡線)を再判定
  (2) ボトルネック流量(`data/juelich_bottleneck_flow.csv`) (3) 対向流レーン形成・交差流
  速度効率/立往生率/反転率(`run_bench.py` の既存シナリオ) (4) `continuity()` 指標
  (5) 見た目: 軌跡 png(`out/traj_*.png` と同型)の目視。
- **工数**: 案A 完了後に +1-2 日 + ベンチ再較正(P4-1 と同規模の較正ランが必要)。

### 案C: 近接=個体 / 遠方=密度場のハイブリッド(遠方のオブジェクト認識を統計量で置換)

- **認知的解釈**: 遠方の群衆は個体でなく**アンサンブル統計(密度・流れ)として知覚される**
  (Whitney & Yamanashi Leib 2018)。ユーザーの「世界の物理状態・オブジェクト認識が優位」の
  最も文字通りの実装。工学的前例は Hughes 2002 / Treuille 2006 / Narain 2009。
- **アルゴリズム**:
  1. ゾーンを ~2 m 格子に離散化し、`np.add.at` で密度場 ρ(x) を O(N_z) で構築。box blur で平滑化。
  2. `_far_forces`(ペア項)を密度勾配力 f_far = −c·m·∇(K*ρ) に置換(K は far 項の
     指数カーネルを径方向に積分したもの → 係数 c は「一様流中でペア版と同じ合力」になるよう解析的に接続)。
  3. 近接場(#1 の 2.0 m・ORCA)は現行のまま(個体性・決定論・重なり禁止を保つ)。
  4. `_accumulate` の local_density は同じ場の読み出しに一本化(全ペア距離行列の完全廃止)。
  5. Narain 2009 の unilateral incompressibility(高密度の非圧縮)までは**やらない**
    (本シムは LOS F の圧潰を再現対象外と宣言済み: `sfm_core.py:33-41` と整合)。
- **計算量**: O(N_z + G)(G=格子セル数 ~数百)。**密度に対して完全に平坦**。
- **期待 speedup**: `_far_forces` 53→~1-2 s・`_accumulate` の密度側もほぼ消える。
  ただし ORCA・SFM 近接項は残るため、単独では物理計 427→~200 s 止まり。案A と併用で最大。
- **軌跡品質への影響**: far 項の意味が「ペアの和」→「場の勾配」に変わる(非同値)。
  一様密度では接続係数により一致させられるが、勾配の粗さ(格子)が低密度で目に見える
  アーティファクトになりうる。P4 受入(A/B/C)の再判定必須。レーン形成など中距離秩序への
  影響は要実測(far 項は元々レーン形成を担っていないので影響は限定的と予想するが、未検証)。
- **検収指標**: 案B と同じ一式 + 「ペア版 far との合力差」を密度帯別に測る新テスト。
- **工数**: 大(場の構築・接続係数の導出・較正やり直しで 1 週間級)。

---

## 5. 推奨案と根拠

**推奨: 案A を第一段(即)、案B を第二段(高密度の上界固定・FD ベンチ再較正込み)。案C は保険**
(ゾーン増設・大面積化や、25 万体実測で案A+B でも予算超過のときに far 項だけ場化)。

根拠:

1. **prof の最大項は力ですらない。** `_accumulate` 166 s(物理の 39%)は観測・知覚の集計であり、
   セル法+ベクトル化は意味論を変えずに 1 桁落とせる。「まず一番太い項を、検収が最も軽い方法で」
   に合致する。
2. **案A は同値変換なので凍結期に適合する。** force ビット一致テスト(`WallField` 前例)+
   既定 OFF バイト一致で検収でき、golden・P4 較正・FD 受入のいずれもやり直し不要。
   R1 規律(仮フリーズ中も検収可能な修正)に収まる。
3. **文献の向きが「近傍制限=近似で品質劣化」ではない。** 実証(Rio/Wirth/Ballerini/注視研究)は
   むしろ「全ペアの方が非実証的」を支持する。案B まで進めても科学的品質は落ちず、
   realism-first の方針と両立する。二層仮説の実装としても、
   下層=視覚的近傍(案A/B)・遠方=統計量(グラフ混雑+将来の案C)・上層=少数の人注意
   (実装済みの dunbar/encounter レーン)ときれいに割り付く。
4. **スケーリングの質が変わる。** 25 万体では N_z がゾーン物理密度の上限まで張り付くため、
   O(N_z²) のままだと 10k 実測からさらに 1-2 桁悪化する。案A で O(N_z·k̄)、案B で k の上界固定、
   と段階的に最悪ケースを閉じられる。

段階投入の順序(提案):
A-1 `_accumulate` ベクトル化+セル法(最大項・同値)→ A-2 SFM 基本項+far 項のセル法(同値・
ビット一致テスト)→ A-3 ORCA 近傍選抜のセル法化(同値)→ [ここで mock10k144 再実測・GO/NO-GO]
→ B(cap+セクター遮蔽近似・FD 再較正)→ 必要時のみ C。

---

## 6. 付記(物理層の周辺で同時に拾える小物)

- **全個体走査の線形項**(#9・`physics.py:337,351`): ゾーン入場候補は `route` を持つ street 在場者
  だけなので、`_phase_move` 側の既存集合から事前索引を渡せば 25 万体 sort×6/step が消える。
  ペア項とは独立に効く(follower_count 逆引き索引と同型の手筋)。
- **ORCA LP の Python コスト**(#6): 認知とは無関係の実装コスト。`.tolist()` 廃止+LP の
  ベクトル化 or numba 化で 98 s の過半が落ちる余地。ただし float 演算順が変わり ORCA ゾーンの
  軌跡はビットレベルで変わりうる(決定論自体は保てる)ので、案A と同じ PR に混ぜないこと。
- **`_admit` の総当たり**(#8): 入口ゲート近傍のセルだけ見れば O(W·M)→O(W·k)。
  信号青の解放パルス時のみ効く小物。
- **知覚チャンネル接続**(`physics.perception.channels`)を将来 ON にする場合も、本リサーチの
  観測層痩身(セル法の local count)がそのまま供給源になる = σ 再較正の判断とは独立。

## 7. 本ドキュメントの確認方法(検収)

- 文献 URL は 2026-08-16 に WebSearch/WebFetch で実在確認済み(PNAS・Royal Society 本体は
  403 のため arXiv/PMC/出版社別ページで代替確認したものがある。表中の URL がその確認先)。
- 実装参照はすべて本日時点のワークツリー(`src/society/physics.py` / `src/society/world/sfm_core.py` /
  `src/society/world/orca_core.py` / `src/society/world/zones.py` / `conf/zones_shibuya.yaml` /
  `conf/finals_observe.yaml`)の行番号。
- prof 実測は `docs/log/devlog.md` Entry 134(prof10k6)と発注文の追加内訳
  (_accumulate 166 s / 総 577 s・_far_forces 53 s・argsort 26 s)に拠る。
