# P4 = 歩行物理層の較正 — 実装前文献リサーチ

第80バッチ(2026-08-05・Opus 実行役)。`docs/research/physics-engine-selection.md` **§7.2 の条件 A/B/C**(= P4 の作業定義)に対する、**実装着手前の文献調査**です。

**本書は調査のみ。`src/` `conf/` `reference/` は 1 バイトも変更していません。**書き込んだファイルは本書 1 本だけです。
実装方針は §6 に「提案」まで書き、**決定はしません**(ユーザー承認事項)。

**記法の約束**: 各数値に出典区分を付けます。
**[実測]** = リポジトリ内のベンチで測った値 / **[文献]** = リンク先に書かれている値 / **[推定]** = 本書での換算・推論。
アクセス日はすべて **2026-08-05**(§7 に一括)。

---

## §0 3 行サマリ

1. **較正データは揃う。** Jülich の Pedestrian Dynamics Data Archive は **CC BY 4.0・DOI 付き・ZIP 直リンク**で、一方向流 / ボトルネック / 90°交差の**軌跡テキスト(`ID, frame, x[cm], y[cm], z[cm]` @16fps)**がそのまま落ちます。「合わせ込み用 CSV」は**作れます**(§1)。
2. **受入閾値 ±X% は「±20%」が文献的な下限で、しかも ±X% 単独では現行の失敗を検出できません。** 研究間のばらつきは capacity で 1.2–1.8 (m·s)⁻¹ = 中央値まわり **±20%**[文献]。だが現行 SFM は ρ=1.5 で誤差 1%・ρ=3.0 で 195% [実測] なので、**「複数密度点 + 単調性 dv/dρ ≤ 0」を併記しないと帯を素通りします**(§2)。
3. **最大の発見: 現行 SFM は VISSIM 製品版 SFM の「短距離項」だけを持ち、「長距離項」を丸ごと欠いています。** VISSIM の実運用値は A_social=0.5 m/s² / B=2.8 m(長距離)+ **A_isotropic=25 m/s² / B=0.2 m(短距離)**[文献]。本リポジトリは A=2000 N ÷ m=80 kg = **25 m/s²**・B=0.08 m [実測] で、**短距離項の A が偶然ぴったり一致**します。→ **P4-B は「A・B を振り直す」のではなく「第 2 項を足す」が正しい**(§6.1)。
   **併せて λ(異方性)= 0.5 は、較正済み文献値 0.06–0.12 の 4〜8 倍**[実測 vs 文献]。既存 §5.6(a) が非単調性の原因とした「後方からの押し出し」を直接支配する係数であり、**`src/` を触らずに検証できる最安の先行実験**です(§6.1a)。

---

## §1 較正データセット

### 1.1 一次ソース: Forschungszentrum Jülich — Pedestrian Dynamics Data Archive

- アーカイブ本体 DOI: **10.34735/ped.da**、個別実験にも DOI(例 `10.34735/ped.2013.6`)。
- **ライセンス: CC Attribution 4.0 International**(サイト明記)。アーカイブ側の文言は "You are very welcome to use our data for further research, as long as you name the source of the data."[文献]
- 軌跡は **PeTrack** で動画から自動抽出。多くの実験で動画も同梱。
- **URL の注意**: 同一 wiki が `/da/` `/db/` `/database/` の 3 プレフィックスで引けます。本書は `/database/` に統一。

### 1.2 P4 で使える実験(ダウンロード可否を判定済み)

| # | 実験 | ページ id | DOI | 形式 | 使えるか |
|---|---|---|---|---|---|
| (i) | **一方向流・開/閉境界**(HERMES) | `corridor3` | 開 `10.34735/ped.2009.14` / 閉 `10.34735/ped.2009.13` | 軌跡 txt 17.0 / 17.3 MB・HDF5・動画 WMV・16 fps | **◎ 基本図の主データ** |
| (ii) | **一方向流コリドー**(BaSiGo) | `corridor5` | `10.34735/ped.2013.6` | 軌跡 **txt 23.6 MB** / txt+ID 22.5 MB / **HDF5 37.7 MB**・metadata JSON 11.8 KB・動画 MP4・参加者 XLS | **◎ 高密度側の主データ** |
| (iii) | **ボトルネック**(HERMES, 2009-05 Düsseldorf) | `hermes_bottleneck` | `10.34735/ped.2009.6` | **軌跡 txt 5.5 MB** / HDF5 8.5 MB・metadata JSON 8.1 KB・動画 WMV・16 fps・16 run | **◎ 未実装シナリオ用** |
| (iv) | **90°交差流**(BaSiGo, 2013-06) | `crossing_90` | `10.34735/ped.2013.4` | **軌跡 txt 82 MB** / HDF5 84.5 MB・metadata JSON 47 KB・動画 1.5 GB・16 fps | **○ 交差流(ORCA ゾーン)の検証用** |
| (v) | 120°交差流 | `crossing_120` | — | 同型 | ○(優先度低) |
| (vi) | 双方向流 | `corridor4` / `corridor6` | — | 同型 | △(対向流の参考) |

**(iii) の直リンク**(ページに掲載の実 URL):
```
http://ped.fz-juelich.de/experiments/2009.05.12_Duesseldorf_Messe_Hermes/data/zip/2009bottleneck_trajectories_txt.zip
http://ped.fz-juelich.de/experiments/2009.05.12_Duesseldorf_Messe_Hermes/data/zip/2009bottleneck_metadata.json
```
**(iv) の直リンク**:
```
http://ped.fz-juelich.de/experiments/2013.06.19_Duesseldorf_Messe_BaSiGo/data/2013crossing_90/2013crossing_90_trajectories_txt.zip
http://ped.fz-juelich.de/experiments/2013.06.19_Duesseldorf_Messe_BaSiGo/data/2013crossing_90/2013crossing_90_metadata.json
```

### 1.3 軌跡フォーマット(ここが「CSV を作れるか」の答え)

**txt 版の列は `ID, frame, x-coordinate [cm], y-coordinate [cm], z-coordinate [cm]`**、フレームレート **16 fps**(= Δt 0.0625 s)[文献・(iii)(iv) のページに明記]。

→ **合わせ込み用 CSV は作れます。** 必要な変換は 3 段だけで、すべて決定論的:
1. cm → m(÷100)、frame → t(÷16)。
2. 速度 = 位置の中心差分(または Steffen & Seyfried 2010 の「同位相の差分商」)。
3. 密度 = 測定矩形内人数 ÷ 面積(古典法)、または **Voronoi 法**(§5.3)。

**注意点(実装前に潰すもの)**:
- **z 列がある**(3D 追跡=頭部高さ)。**2D 較正では捨てる**が、身長由来の追跡誤差が x,y に乗っている可能性は残る。
- **メタデータ JSON に幾何(通路幅・入口幅 b₁/b₂・run 対応表)が入る**。ジオメトリは**必ず JSON から読む**こと。本書では (ii) の通路長について**ページ要約が「5 m」、検索要約が「8 m × 3 m・最大 350 名」と食い違っており、未確定**[要確認]。**ハードコードせず metadata JSON を一次情報にしてください。**
- (iii) は run 数 16、幅の一覧が実験ページ本文に出ていない[要確認 → metadata JSON で確認]。

### 1.4 もう 1 本の「そのまま使える」参照データ

**RiMEA Test 16 の参照包絡線**(§5)は独立に配布されています。

| 資源 | URL | 形式 | ライセンス |
|---|---|---|---|
| 生データ(単列歩行 FD の集成) | `https://doi.org/10.5281/zenodo.8378592` | ZIP 83.9 MB(`PedestrianDynamics/SingleFileComparator` v1.0.0) | Other (Open)、GitHub 側は **MIT** |
| 10%/90% パーセンタイル | `https://rimea.de/wp-content/uploads/2025/01/test_16_percentiles.xlsx` | XLSX | RiMEA(CC BY-ND 4.0) |
| 比較ツール(オンライン) | `https://go.fzj.de/validator` → `rimea-richtlinie.streamlit.app` | Streamlit アプリ | MIT |

**中身は「文献中の複数実験から事前計算した基本図の集成 + KS 検定による突合」**(Chraibi & Subaih)[文献]。
**= 目的関数(KS 距離)と参照データが公式にセットで配られている。**これは §3 の推奨に直結します。
なお **streamlit アプリ本体は認証リダイレクトで機械取得できず、画面内容は未検証**[要確認]。GitHub 側(MIT)を読むのが確実です。

### 1.5 判定

| 課題 | 判定 |
|---|---|
| (i) 単方向流の基本図データ | **入手可**(corridor3 / corridor5) |
| (ii) ボトルネック(開口幅 vs specific flow) | **入手可**(hermes_bottleneck)。参照値は §2.4 |
| (iii) 交差流 | **入手可**(crossing_90 / 120) |
| 合わせ込み用 CSV を作れるか | **作れる**。列定義・fps が明記され、CC BY 4.0 で再配布制約も軽い |

**ただし**: 総計で **数百 MB〜2 GB** 規模。**動画は落とさず軌跡 txt だけ**にすれば (i)(iii)(iv) 合計 **約 105 MB** で足ります。`.gitignore` の除外掟に従い、**リポジトリには入れず `reference/` 外の作業ディレクトリに置き、派生 CSV とそのハッシュだけを成果物にする**のが安全です。

---

## §2 参照曲線と、受入閾値 ±X% の根拠

### 2.1 Weidmann (1993) / Kladek 式(現行ベンチが使っている式)

```
v(ρ) = v_f · [ 1 − exp( −γ · (1/ρ − 1/ρ_max) ) ]
v_f = 1.34 m/s,  γ = 1.913 m⁻²,  ρ_max = 5.4 m⁻²
```
Weidmann 自身は **25 件の調査を統合した review** としてこの関係を出しており、原典で **ρ_max = 5.4 /m²**、ただし「より高い密度を報告した著者もいる」と注記[文献: Seyfried et al. 2005 が Weidmann p.52 を引用]。
**Weidmann は一方向流と双方向流を区別していない**(Seyfried et al. 2005 の脚注が明示)。**スクランブル交差点(多方向)に直接当てるのは、この時点で 1 段の外挿です。**

Weidmann 曲線の**傾きが変わる 4 領域**[文献]:

| 領域 | 密度 | 速度低下の主因 |
|---|---|---|
| I | ρ < 0.7 | 自由速度が支配。追い越しによる小さな低下 |
| II | 0.7 ≤ ρ < 2.3 | **ほぼ線形に低下**。追い越し不能に。接触はまだ回避可能 |
| III | 2.3 ≤ ρ < 4.7 | 曲率反転。**速度低下がむしろ緩む**(内部摩擦は増えるのに) |
| IV | ρ ≥ 4.7 | 急落。剛体的な限界 |

→ **スクランブル交差点の作業域は領域 I–II(ρ ≲ 2.3)**。P4 の較正は**ここに重みを置くべき**で、領域 III–IV は「壊れていないこと」を見るだけで十分です。

### 2.2 研究間のばらつき = ±X% の直接の根拠

**Seyfried らが planning handbook の 3 仕様(SFPE / Predtechenskii-Milinskii / Weidmann)と実測を突き合わせた結果**[文献]:

| 量 | 研究間の範囲 | 中央値まわりの幅 [推定] |
|---|---|---|
| capacity(最大 specific flow) | **1.2 – 1.8 (m·s)⁻¹** | 中央 1.5 に対し **±20%** |
| 速度が 0 になる密度(jam density) | **3.8 – 10 m⁻²** | 中央 6.9 に対し **±45%**(2.6 倍幅) |
| 最大流量に達する密度 | **1.75 – 7 m⁻²**(一部文献は 1.7) | 中央 4.4 に対し **±60%**(4 倍幅) |

**ETRR のレビュー**(Vanumu, Rao & Tiwari 2017, オープンアクセス)も同じ結論を文章で述べています:
"in spite of extensive research in this area, the results from various studies shows that there exist wide variations in FDs. Even though the shape of the FDs remains same, the values of flow parameters vary immensely."[文献]
ばらつきの原因として **測定法・人口構成(高齢者・荷物)・文化差・施設種別・実験 vs 実地**を挙げています。

**文化差の定量**: Chattaraj, Seyfried & Chakroborty (2009) はインド人とドイツ人の単列歩行 FD を比較し、
**「基本形は似ているが、与えられた密度に対する速度は常にインドの方が高い」「インド人の速度は密度への依存が弱い」**[文献]。
→ **Weidmann(欧州中心)を渋谷にそのまま当てることには、文献が認める系統誤差が乗ります。**これは ±X% を**狭くできない**理由です。

**測定法の寄与**: Zhang & Seyfried らは 4 種の測定法を比較し、**ρ < 3.5 m⁻² では測定法の影響は小さい**が、**Voronoi 法だけが基本図の微細構造を解像できる**としています[文献]。
本ベンチは古典法のみ → 既存 §8.3 の「絶対値は ±10% 幅で読むべき」[実測ベースの自己申告] と整合。

### 2.3 推奨する受入基準(±X% だけでは足りない)

**理由**: 現行 SFM(dt=0.02)の実測は **ρ=1.5 で 0.698 vs 再スケール Weidmann 0.704 = 誤差 0.9%** [実測]。
**±20% の帯なら、この点は余裕で「合格」します。**しかし同じモデルが **ρ=3.0 で 0.976 vs 0.293 = 誤差 +233%** [実測]、しかも **ρ 増加で速度が上がる**(非単調)。
→ **単一密度点の ±X% 判定は、現行の失敗様式をまったく捕まえません。**

**提案する 3 本立て**(すべて機械判定可能):

| 判定 | 内容 | 根拠 |
|---|---|---|
| **A. 帯** | ρ ∈ **[0.5, 2.0] /m²** の各点で `|v_sim(ρ) − v_ref(ρ)| / v_ref(ρ) ≤ **0.20**` | capacity の研究間ばらつき 1.2–1.8 = ±20%[文献]。**これより狭い値を置くのは、文献が持っていない精度を主張すること** |
| **B. 単調性(ハード)** | ρ の掃引全域(0.2–5.0)で `v(ρ_{k+1}) ≤ v(ρ_k) + ε`(ε は seed 間 sd) | Weidmann の 4 領域はすべて非増加[文献]。**現行の非単調は「較正のずれ」ではなくモデル項の欠落**[既存 §5.6 の判断] |
| **C. 包絡線(1D のみ)** | RiMEA Test 16 の **10%/90% パーセンタイル帯**の内側 | RiMEA 4.1.1 が定める公式基準。**±X% ではなく実データの包絡線**を使う(§5.2) |

**なぜ ±20% で、±10% でも ±30% でもないか**:
- **下限**: capacity の研究間範囲 1.2–1.8 (m·s)⁻¹ が ±20%[文献]。**±10% にすると、Weidmann 以外のどの実測研究にも通らない基準になる**(= 参照曲線の選択に結果が支配される)。
- **上限**: ±30% にすると、領域 II で v が 0.6→0.42 まで許され、**「歩ける」と「詰まった」の区別がつかなくなる**[推定]。
- 加えて古典密度法の自己申告誤差 ±10%[既存 §8.3] を含んでも ±20% は残ります。

**ρ の範囲を [0.5, 2.0] に限る理由**: 領域 I–II がスクランブルの作業域[文献の領域区分 + 既存 §5.4 の「ピーク密度はこの領域」]。領域 III–IV は判定 B(単調性)だけを課し、絶対値は問わない。

### 2.4 ボトルネックの参照値(未実装シナリオ用)

**開口幅 b = 0.6–2.5 m の範囲で specific flow ≈ 1.9 (m·s)⁻¹** [文献: Seyfried et al. 2009 / Rupprecht et al. 2011]。
**流量は幅に対して段階状ではなく線形に増える**(b > 0.6 m)[文献: Kretz, Hengst & Vortisch]。
→ **受入基準案**: `J_s ∈ [1.5, 2.3] (m·s)⁻¹`(1.9 の ±20%)かつ `J(b)` が b に対し単調増加・線形性の決定係数 R² ≥ 0.9 [推定した閾値]。

### 2.5 多方向流(スクランブルそのもの)の参照

Duives, Sparnaaij, Daamen & Hoogendoorn (CrowdLimits) の結論[文献]:
**「シナリオが難しくなる(単方向→双方向→交差)ほど、また流量比が 50:50 に近づくほど、最大 global flow rate は下がる」「歩行空間の容量は複雑さとともに減少する」**。
また **極高密度でも流れが止まりきらない現象は文化特有のアーティファクトではない**(欧州の異質群衆でも再現)ことも示しています。

日本のデータ点: **Alhajyaseen & Nakamura の信号交差点横断歩道(双方向・日本)**は
**「方向分割比がほぼ均等のとき容量低下が最大」「高齢者が混ざると容量が最大 30% 低下しうる」**[文献]。

→ **P4 の含意**: 交差流ゾーンに一方向流の Weidmann をそのまま当ててはいけない。
**交差流の受入は「単方向 FD より下に来ること」を示す相対判定にとどめる**のが、文献が支持する範囲です。

---

## §3 較正手法の推奨(目的関数 + 探索法 + 実装コスト)

### 3.1 先行手法の実際

#### (a) Johansson, Helbing & Shukla (2007) — 進化的調整

- **データ**: 実動画のトラッキング軌跡 3 本(低・中・高密度)。
- **目的関数**: 予測ホライズン T 後の**相対距離誤差**
  ```
  ‖r_sim(t+T) − r_track(t+T)‖ / ‖r_track(t+T) − r_track(t)‖
  ```
  を全歩行者・全開始時刻で平均し、**fitness = 1 − その平均**(最良 = 1)[文献]。
- **探索法**: 進化的最適化。
- **結果**[文献・Helbing & Johansson の Table 1。**単位は m/s²(= 力/質量)であって N ではない**]:

| 仕様 | A [m/s²] | B [m] | λ | fitness |
|---|---|---|---|---|
| 外挿(等速)ベースライン | 0 | — | — | 0.34 |
| **円形(circular)** | **0.42 ± 0.26** | **1.65 ± 1.01** | 0.12 ± 0.07 | 0.40 |
| **楕円形 II(elliptical)** | **0.04 ± 0.01** | **3.22 ± 0.67** | 0.06 ± 0.04 | **0.61** |

- **P4 に効く 2 つの警告**:
  1. **「各動画について、ほぼ同等に良く効く A・B の組合せが広い範囲で存在する」**[文献]。
     → **(A,B) の 2 次元探索は平坦な谷を持ち、点推定が定まりません。**
     Johansson らは**複数動画にわたる joint fitness**(各動画の fitness を等重みで合成)で初めて一意化しています。
     → **P4 では「複数密度点にわたる joint 誤差」= まさに基本図そのものを目的関数にすべき**(単一密度点で合わせてはいけない)。
  2. **「良いモデル性能に達するには、相互作用力を速度依存に指定する必要がある」**(楕円形が円形より fitness 0.61 vs 0.40)[文献]。
     → **現行 SFM は距離のみ依存(速度非依存)。**楕円形化は将来の選択肢だが、P4 のスコープ外に置くのが妥当[推定]。

#### (b) Kretz, Hengst & Vortisch — VISSIM 製品版 SFM のボトルネック較正

- **シナリオ**: 6 種の開口幅(40/50/60/70/80/100 cm)× 各 100 名 × **8 パラメータセット × 10 反復**。
- **探索法**: **OAT(one-at-a-time)**。P0 を基準に 1 パラメータずつ振る(P1–P7)。
- **観察**: 「異なるパラメータを振っても、結果はほぼ定数倍でスケールした」[文献]。
  → **スケール因子と形状因子が分離している**。**P4 でも「まず形状(B)を決め、次に高さ(A)で合わせる」2 段が効く可能性が高い**[推定]。
- **P0(製品出荷値・§6 の核心)**:

| パラメータ | 値 |
|---|---|
| 半径 | 0.15 m |
| **A_social** | **0.5 m/s²** |
| **B_social** | **2.8 m** |
| **A_social,isotropic** | **25 m/s²** |
| **B_social,isotropic** | **0.2 m** |
| τ | 0.4 s |
| λ | 0.1 |
| 速度依存 | 2 s |
| 考慮する近傍数 | n = 5 |
| 摩擦力 | 0 |

#### (c) 公式 KS 検定ツール

RiMEA 4.1.1 が Test 16 の参照として指す **SingleFileComparator**(Chraibi & Subaih, MIT)は、
**文献由来の基本図コレクションに対して KS 検定で突合する**設計[文献]。
**閾値・p 値の運用は README に明記されておらず未確認**[要確認]。

### 3.2 推奨(P4 でどう組むか)

| 項目 | 推奨 | 理由 |
|---|---|---|
| **目的関数** | **基本図上の重み付き相対誤差**<br>`L = Σ_ρ w(ρ) · [ (v_sim(ρ) − v_ref(ρ)) / v_ref(ρ) ]²`<br>ρ ∈ {0.5, 1, 2, 3, 4, 5, 6}(RiMEA Test 4 の指定密度)、w は領域 I–II を重く | Johansson の教訓 1(単一条件では一意化しない)への直接の対処。**RiMEA Test 4 と密度点が一致するので、較正と検収が同じ格子で回る** |
| **副目的(ハード制約)** | 単調性 `v(ρ_{k+1}) ≤ v(ρ_k) + ε`、および `v ≈ |v|`(churn 検出) | 帯だけでは現行の失敗を検出できない(§2.3)。既存 §5.6(c) の churn 指標をそのまま昇格 |
| **軌跡レベルの誤差** | **使わない**(Johansson 型の相対距離誤差) | 実軌跡との 1 対 1 対応が要る = Jülich の初期条件を厳密再現する必要があり、コストが跳ねる。**P4 の目的(外部実測への釘付け)には基本図で足りる** |
| **KS 距離** | **1D 基本図の検収でのみ使う**(RiMEA Test 16 経路) | 公式ツールがその形で配られているため。較正のループには入れない(勾配がない) |
| **探索法** | **2 段**: ① 粗いグリッド(対数格子 5×5 程度)で谷の位置と**平坦さ**を可視化 → ② その周辺で **Nelder-Mead**(`scipy.optimize.minimize(method="Nelder-Mead")`) | 変数が 2〜3 個なら CMA-ES は過剰。**平坦な谷が予想される**(Johansson の教訓 1)ので、**点推定の前に必ずグリッドで谷を見る**こと。CMA-ES/GA は「収束が遅く時間がかかる」との指摘もある[文献] |
| **dt の扱い** | **最適化変数に入れない。離散水準 {0.02, 0.05} で外側ループ** | dt は数値精度パラメータであって物理量ではない。**ORCA で dt が事実上の較正パラメータになってしまう**問題[既存 §5.6(c)]を SFM で繰り返さないため |
| **決定論** | 保てる。目的関数は seed 固定の 1 ラン評価 = 決定論的関数。Nelder-Mead も決定論的 | R1 の「乱数は用途別専用 stream」の枠内。**較正器そのものは `reference/` 側に置き、`src/` は触らない** |

### 3.3 探索コストの見積り [推定]

既存実測[§5.2]: SFM 約 3.8 万 agent·step/s。
FD 1 点 = 200 体 × 50 s ÷ dt。dt=0.02 なら 200×2500 = 50 万 agent·step ≈ **13 秒**。

| 段 | 内容 | 評価回数 | 時間 [推定] |
|---|---|---|---|
| ① 粗グリッド | 5×5 = 25 組 × 7 密度 × dt 2 水準 | 350 ラン | **約 75 分** |
| ② Nelder-Mead | 2 変数で 60〜100 評価 × 7 密度 | 約 700 ラン | **約 2.5 時間** |
| 合計 | | | **約 4 時間**(単一コア) |

→ **並列化なしで一晩に収まる**。`xdist` で 4 プロセスなら 1 時間強。**GPU は不要**(既定方針どおり)。

---

## §4 密度依存希望速度 v₀(ρ) の文献的防御

条件 C(§7.2)への批判は「SFM の純度を落とす」ですが、**文献は逆に、力ベースから速度ベースへ移行することを推奨しています。**

### 4.1 速度ベースモデルは確立した一群である

**Tordeux, Chraibi & Seyfried (2015) "Collision-free speed model"**[文献]は、
**速度そのものを前方間隔 s の関数として与える**モデルです:

```
ẋ_i = V(s_i) · e_i
V(s) = min{ v0 , max{ 0 , (s − ℓ)/T } }
使用値: v0 = 1.2 m/s,  ℓ = 0.3 m,  T = 1 s
方向モデル: e_i ∝ e0 + Σ_j R(s_ij)·e_ij ,  R(s) = a·exp((ℓ−s)/D) ,  a = 5, D = 0.1 m
```

**これは JuPedSim の製品モデルの 1 つ**(Collision-Free Speed Model)として実装・運用されています[文献]。
つまり **「速度を局所間隔/密度の関数にする」は場当たりの回避策ではなく、Jülich 自身が主流の代替案として提示・実装している設計**です。

論文は力ベースの欠点を名指ししています[文献・原文]:
> "this model class describes particles with inertia and does not exclude particle collision and overlapping. **This is especially problematic at high densities.** Moreover, the force-based approach may lead to numerical difficulties resulting in **small time steps and high computational complexity**"

**= 本リポジトリが実測した 3 つの症状(重なり・高密度破綻・dt を 0.05 以下に落とす必要)が、そのまま力ベース一般の既知の欠点として書かれています。**

### 4.2 「dt を小さくすれば直る」は文献が否定している

**Köster, Treml & Gödel (2013) "Avoiding numerical pitfalls in social force models"** (Phys. Rev. E 87, 063305)[文献]:
- **「振動・衝突・不安定性は、非常に小さいステップ幅でも起きる」**
- **「微分方程式の右辺は微分不可能で、臨界位置では不連続ですらある」**
- 古典的な 2 次モデルは **後退運動・振動・重なり**という非現実的挙動を持ち、**これらは離散化由来ではなく力学に内在する**

→ **既存 §5.6(b) の実測(ρ≥2 で群れが −1.4 m/s 後退し、dt=0.02 でも消えない)は、文献既知の現象です。**
「実装のバグ」でも「dt 不足」でもない。**§7.2 条件 A(dt を下げる)には天井があり、条件 C が要る**ことの文献的裏づけになります。

### 4.3 防御線のまとめ(そのまま反論に使える形)

| 想定される批判 | 応答 |
|---|---|
| 「SFM の純度を落とす」 | 純度を保った場合の失敗様式(高密度の重なり・後退・小 dt 強制)は **Tordeux 2015 が力ベース一般の欠点として明記**。純度の維持自体が目的にならない |
| 「dt をもっと下げれば済む」 | **Köster 2013 が「非常に小さいステップ幅でも振動・不安定が起きる」「離散化由来ではない」と明示**。実測(dt=0.02 でも −1.42 m/s)と一致 |
| 「アドホックな後付け」 | **JuPedSim が製品として速度ベースモデルを実装**。v0(ρ) はその方向への**最小限の一歩**(方向モデルは SFM のまま) |
| 「較正テーブルは再現性を壊す」 | conf 外部化 + **ハッシュを manifest に載せる**(P3(4) の既存枠)。テーブルは決定論的な純関数 |
| 「文献に v0(ρ) そのものの前例があるか」 | **Tordeux の V(s) は「前方間隔の関数としての速度」= 実質同じ発想**。ρ と s は逆数関係にある[推定]。ただし **v0(ρ) を「密度」で引く形の前例は本調査では特定できず**、間隔ベース V(s) の前例のみ確認[要確認] |

**正直な限界**: §4.3 最終行のとおり、**「近傍密度 ρ を測って v0 を下げる」形そのものの一次文献は見つけていません。**
文献が支持しているのは **「間隔 s の関数としての速度」**です。
→ **実装は ρ ではなく「前方最小間隔 s」で引くほうが文献的に強い**[推定・§6 に反映]。

---

## §5 RiMEA 適用表

### 5.1 現行版(既存資料の更新が必要)

**既存 `physics-engine-selection.md` §2.3 は「15 個のテストケース」と書いていますが、これは v3.0 の記述です。**

| 項目 | 現行 |
|---|---|
| 版 | **4.1.1(2025-09-11 発行)**。前版 4.0.0(2022-04-28) |
| 言語 | 独英併記(**ドイツ語版が正**と明記) |
| ライセンス | **CC BY-ND 4.0**(改変不可) |
| PDF | `https://rimea.de/wp-content/uploads/2025/09/rimea-4.1.1-d-e-1.pdf`(56 ページ) |
| テストケース数 | **16**(Test 16「1D 基本図」が追加。Test 12 は 4 変種に分割) |
| 検証の枠組 | ISO/TR 13387-8:1999 の 4 段(構成要素試験 / 機能検証 / 定性検証 / **定量検証**) |
| 定量検証の扱い | **「信頼できる実験データが十分でないため、最初の 3 段で十分とみなす」**と明記[文献] |

### 5.2 適用可否表

| # | テスト(英題) | 内容 | P4 適用 |
|---|---|---|---|
| **4** | **Measurement of the fundamental diagram** | **通路 1000 m × 10 m。2×2 m の測定区画 3 つ(主 1・対照 2)。密度 0.5 / 1 / 2 / 3 / 4 / 5 / 6 P/m² を作り、各密度で 60 秒の平均速度を測る。最初の 10 秒は「過渡」として無視してよい。flow = speed × density。加えて、追い越し不能な幅まで狭めた「線状移動」でも FD を再現すること** | **◎ 最優先。P4 の中核そのもの** |
| **16** | **1D Fundamental Diagram** | リング(推奨・幾何境界の影響なし)または長さ 200 m の 1 体幅通路。**参照は実試験データの 10%/90% パーセンタイル包絡線**。生データ Zenodo、パーセンタイル XLSX 配布 | **◎ 受入閾値の外部根拠として採用** |
| **1** | Maintaining the specified walking speed in a corridor | 指定した自由歩行速度を通路で保つか | **○ 安価。既存 v₀∈[1.0,1.4) の検算に使える** |
| **12** | Effect of bottlenecks(12a–12d) | 2 室 + 開口。12a は目標位置と最終開口の距離 a を 0–10 m で振り、150 名の退室時間を測る | **△ 部分適用。「開口幅 vs specific flow」は RiMEA ではなく §2.4 の Seyfried/Kretz を使うほうが直接的** |
| **6** | Movement around a corner | 角の曲がり | **○ 地下通路ゾーンに適用可** |
| **15** | Movement of a large crowd around a corner | 大群衆の角曲がり | **○ 同上** |
| **8** | Parameter analysis(機能検証) | パラメータ感度の体系的提示 | **○ §5.6(d) の感度表がそのまま該当。P4 の成果物として整形するだけ** |
| 2, 3, 13 | 階段(上り/下り/階段 FD) | — | **✗ 対象外**(階段を物理層で扱っていない) |
| 5 | Premovement time | 反応時間 | ✗ 避難固有 |
| 7 | 人口統計パラメータの割当 | — | △(persona 側の話。物理層外) |
| 9, 10, 11, 14 | 避難・経路選択系 | — | ✗ 避難固有 |

### 5.3 Voronoi 密度法の要否

**Steffen & Seyfried (2010)**(Physica A 389(9), 1902–1910 / arXiv:0911.2165)は、**各歩行者に Voronoi セルを個人空間として割り当てて密度を求める**方法で、**散らばりを大幅に減らす**[文献]。

**要否の判断**:
- Zhang & Seyfried らの比較では **ρ < 3.5 m⁻² では 4 種の測定法の差は小さい**[文献]。
- **P4 の作業域は ρ ≲ 2.3(§2.1 の領域 I–II)** → **必須ではない**。
- ただし **RiMEA Test 4 は 2×2 m という小さい測定区画**を指定しており、**小面積 = 古典法の散らばりが大きい**。
- **推奨**: **P4-1 で Voronoi 密度を「追加の指標」として実装**(古典法は残す)。**両方を出して差が ±10% 以内なら古典法で押し通す**、という判定にすれば、実装コストを払う前に必要性を機械的に判断できます[推定]。

---

## §6 実装への具体的示唆(P4 バッチ分解案)

> **以下はすべて提案です。ユーザー承認前に `src/` へは着手しません。**

### 6.1 ★ 最重要の発見: 現行 SFM は「2 項構造の片方」しか持っていない

VISSIM の製品出荷値[文献・§3.1(b)]と本リポジトリの既定値[実測・`src/society/world/sfm_core.py`]を、**同じ単位に揃えて**並べます。
本リポジトリは A を **N** で持ち、加速度は `f/m` で作るので、**加速度換算 A/m = 2000/80 = 25 m/s²**。

| 項 | VISSIM P0 | 本リポジトリ | 一致度 |
|---|---|---|---|
| **短距離・等方** | A = **25 m/s²**、B = **0.2 m** | A = 2000 N ÷ 80 kg = **25 m/s²**、B = **0.08 m** | **A が完全一致。B は 2.5 倍短い** |
| **長距離・異方(速度依存 2 s)** | A = **0.5 m/s²**、B = **2.8 m**、λ = 0.1 | **存在しない** | **丸ごと欠落** |
| **λ(異方性)** | **0.1** | **0.5**(`LAMBDA_DEFAULT`) | **4〜8 倍大きい**(§6.1a) |
| τ | 0.4 s | 0.5 s | 近い |
| 半径 | 0.15 m | 0.25–0.35 m | 本リポジトリのほうが大きい |
| 近傍数 | n = 5 | cap 12(`indoor_flow`) | 近い |

#### 6.1a λ = 0.5 は、較正済みのどの文献値からも 4〜8 倍外れている

λ は「後方からの相互作用の強さとともに増える」係数で、**λ=1 が等方(後ろも前と同じだけ効く)**、λ→0 が「後ろを完全に無視」[文献: Helbing & Johansson 式(11) `w(φ) = λ + (1−λ)(1+cos φ)/2`。本リポジトリの `sfm_core.py` の重みも**同一式**]。

| 出典 | λ | 由来 |
|---|---|---|
| **本リポジトリ** | **0.5** | Helbing & Molnár 1995 の視野係数 c≈0.5[コメント記載] |
| VISSIM P0(製品出荷値) | 0.1 | [文献] |
| Johansson 円形(実動画較正) | 0.12 ± 0.07 | [文献] |
| Johansson 楕円形 II(実動画較正・最良 fitness) | **0.06 ± 0.04** | [文献] |

**実測データから較正された 3 つの値はいずれも 0.06–0.12 に収まり、本リポジトリの 0.5 はその 4〜8 倍**です。

**これは既存 §5.6(a) の診断と正確に噛み合います。**既存文書は基本図が非単調になる原因を
「異方性重み付きで**前方から押し返すより後方から押し出す方が強く効く**ため、高密度では結晶状に詰まった群れが一体で流れる」
と書いています[既存・実測]。**λ こそがその「後方からの押し出し」の強さを直接決めるパラメータ**であり、
**λ=0.5 は後方からの力を較正値の 4〜8 倍に増幅している**ことになります。

→ **提案: λ を探索変数に入れる優先度は、当初想定より高い。**
ただし A_far・B_far と同時に 3 変数を振るとコストが約 5 倍[推定]なので、
**まず λ を 0.1 に固定した対照ラン 1 本**(A・B は既定のまま)を撃って、
**λ 単独でどれだけ非単調性が改善するかを先に測る**のが安上がりです[推定]。
これは既存ベンチの `engine_kw` で **`src/` を触らずに**実行できます(`Crowd.__init__` が `lambda_aniso` を受け取るため)。

**この 1 枚が、既存の 2 つの実測結果を同時に説明します**[推定・ただし各行の数値は文献/実測]:

1. **なぜ基本図が非単調になるか**[既存 §5.6(a)]
   → **長距離項がないので「混んできたら早めに減速する」機構が存在しない**。B=0.08 m は接触するまで何もしないため、高密度では群れが結晶化して一体で流れる。
2. **なぜ A=560 / B=0.3 の振り直しが「低密度で遅すぎ・高密度で速すぎ」の逆傾斜になったか**[既存 §7.2 条件 B]
   → **1 本の指数関数に 2 つの役割を兼ねさせたから。**B を伸ばせば低密度で効きすぎ、A を下げれば高密度で効かなくなる。**VISSIM が 2 項に分けているのは、まさにこの兼務が不可能だからだ**と読めます。

**→ 提案: P4-B は「A・B の 2 次元探索」ではなく「第 2 項(長距離)の追加 + その 2 パラメータの探索」にする。**
既存の短距離項は**凍結**(A=25 m/s² は VISSIM と一致しており動かす理由がない)。

**探索範囲の事前分布**(2 つの独立ソースが囲んでいる):

| パラメータ | 下限 | 上限 | 出典 |
|---|---|---|---|
| A_far | 0.04 m/s² | 0.5 m/s² | Johansson 楕円 0.04 / 円形 0.42・VISSIM 0.5[文献] |
| B_far | 1.6 m | 3.2 m | Johansson 円形 1.65 / 楕円 3.22・VISSIM 2.8[文献] |

**2 変数・両方とも 1 桁未満の範囲**に閉じ込められています。**§3.3 の 4 時間見積りはこの箱の中の話**です。

#### 6.1b 実装上の落とし穴: `CUTOFF_M = 2.0` が長距離項を切り落とす

`sfm_core.py` の斥力カットオフは **体表間隔 2.0 m**(`valid = active & (d <= rr + CUTOFF_M)`)[実測]。
コメントは「B=0.08 で数 m 先は無視できる」ため、と正しく説明しています。

**しかし B_far = 2.8 m の項を足すと、この前提が崩れます**[推定・算術]:

```
exp(−2.0 / 2.8) = 0.49    ← カットオフ地点で、まだ接触時の 49% の強さが残る
```

**= 力を約半分の高さで垂直に切り落とすことになり、`d = rr + 2.0` に不連続が生じます。**
これは Köster 2013 が指摘する「右辺の不連続」[文献]をこちらから作り込む行為で、**振動の新たな発生源になりえます**。

**対処案**(P4-2 で必ずどれかを選ぶこと):
1. **項ごとにカットオフを分ける** — 短距離項は 2.0 m のまま、長距離項は `5·B_far`(≈14 m)まで。**近傍探索コストが増える**(§8-8)。
2. **長距離項を滑らかにゼロへ落とす**(テーパー窓を掛ける)— 不連続を作らない。カットオフは短くできる。
3. **近傍数 cap で抑える**(VISSIM は n=5、`indoor_flow` は cap 12)— 距離ではなく人数で切る。**VISSIM の実運用に最も近い**。

**推奨は 3 + 2 の併用**[推定]。距離カットオフだけで長距離項を扱おうとすると、
「切ると不連続・切らないと O(N²) が重い」の板挟みになります。

### 6.2 バッチ分解案

| バッチ | 内容 | `src/` 変更 | 検収 |
|---|---|---|---|
| **P4-1**<br>参照データ整備 | ① Jülich (i)(iii)(iv) の軌跡 txt を取得(約 105 MB・リポジトリ外)→ 決定論的に CSV 化(cm→m, frame→s, 速度=中心差分)。**派生 CSV とその sha256 だけを成果物に**。<br>② `reference/physics_bench/metrics.py` に **Voronoi 密度**を追加(古典法は残す)。<br>③ **RiMEA Test 4 の幾何**(1000 m × 10 m・2×2 m 測定区画 3 つ・60 s / 先頭 10 s 破棄)をシナリオ化。<br>④ **ボトルネックシナリオ**(既存 §8.2 の欠落)を追加。<br>⑤ RiMEA Test 16 の 10/90 パーセンタイル XLSX を取り込み。<br>⑥ **λ=0.1 の対照ラン**(`engine_kw={"lambda_aniso": 0.1}`・既定 0.5 との差分)= §6.1a の安価な先行実験 | **なし**(`reference/` のみ) | 古典法 vs Voronoi の差が ±10% 以内か[§5.3 の判定] / 実データ CSV の行数・時間範囲・fps の整合 / λ 単独で非単調性がどれだけ改善するか |
| **P4-2**<br>2 項化 + 探索 | ① `sfm_core.py` に**長距離項を conf ゲートで追加**(`physics.sfm.far_field: {enabled: false, a: …, b: …}`)。**既定 OFF = golden L1 バイト一致**。<br>② 粗グリッド 5×5 → Nelder-Mead で (A_far, B_far) を決定。dt は {0.02, 0.05} の外側ループ。<br>③ **平坦な谷の可視化を必ず成果物に**(Johansson の教訓 1) | **あり**(既定 OFF・追加のみ) | §2.3 の判定 A(±20%)+ B(単調性)+ churn(v ≈ \|v\|) |
| **P4-3**<br>v₀ 較正テーブル<br>(**P4-2 が判定 B を通らなかったときのみ**) | **密度 ρ ではなく「前方最小間隔 s」で引く**形にする(§4.3 の正直な限界)。`V(s)=min{v0, max{0,(s−ℓ)/T}}` 型[文献: Tordeux 2015]。conf 外部化 + **ハッシュを manifest へ**(P3(4) の既存枠) | **あり**(既定 OFF) | 同上 + テーブルのハッシュが manifest に載ること |
| **P4-4**<br>受入テストの固定 | §2.3 の A/B/C を pytest に固定。ボトルネックは §2.4 の `J_s ∈ [1.5, 2.3]`。RiMEA Test 4 / 16 / 1 / 8 を「適合表」として文書化 | なし | フルゲート緑 |

### 6.3 実装前に決めておくべきこと(OPEN 項目)

1. **参照曲線を Weidmann のままにするか、Jülich 実データに差し替えるか。**
   Weidmann は 25 研究の統合レビューで**一方向/双方向を区別していない**[文献]。
   実データ(corridor3/corridor5)なら「一方向流の実測」に釘付けできるが、**渋谷は多方向**なのでどちらも外挿が残ります。
   → **提案: 主参照 = Jülich 一方向流の実測、副参照 = Weidmann 解析曲線(既存の図をそのまま残す)。**
2. **自由速度をどこで揃えるか。** シミュの v₀ 平均は 1.133 m/s[実測]、Weidmann は 1.34 m/s[文献]。
   既存ベンチは「再スケール版」を併記して回避しているが、**P4 では v₀ 分布そのものを較正対象にするかを決める**必要があります。
   文化差の文献[Chattaraj 2009]を踏まえると、**日本の自由速度を別途調べる価値があります**(本調査では未取得[要確認])。
3. **λ(異方性)を探索変数に入れるか。** VISSIM 0.1・Johansson 0.06–0.12[文献]に対し、**本リポジトリは `LAMBDA_DEFAULT = 0.5`**[実測]= **4〜8 倍大きい**(§6.1a)。
   **入れると 3 変数になりコストが約 5 倍**[推定]なので、**P4-1 の段階で λ=0.1 の対照ラン 1 本を先に撃つ**ことを推奨(`src/` 変更不要)。
4. **交差流ゾーン(ORCA)を P4 の較正対象にするか。**
   ORCA は較正のレバーがない[既存 §5.6(d)]ので、**較正はせず「単方向 FD より下」の相対判定だけ**にするのが文献的に妥当[§2.5]。

### 6.4 既存資料に対する訂正候補

| 箇所 | 現行の記述 | 訂正 |
|---|---|---|
| `physics-engine-selection.md` §2.3 | 「RiMEA は…**15 個のテストケース**」 | **v4.1.1(2025-09-11)で 16 個**。Test 16「1D 基本図」追加、Test 12 は 4 変種に分割 |
| 同 §7.2 条件 B | 「A・B の 2 次元探索 + dt の 3 変数最適化が P4 の主作業」 | **2 項構造(長距離項の追加)を先に検討すべき**(§6.1)。単一項の振り直しが逆傾斜になったのは構造的理由がある |
| 同 §9 | Weidmann 原典未確認 | **依然として未確認**(独語レポート)。ただし **Seyfried et al. 2005 が Weidmann p.52 の図と ρ_max=5.4 を直接引用**しており、二次引用としての信頼度は上がった |

---

## §7 リンク集(アクセス日: すべて 2026-08-05)

### 較正データ
- Pedestrian Dynamics Data Archive(トップ / DOI 10.34735/ped.da) — https://ped.fz-juelich.de/database
- 一方向流 開/閉境界(HERMES) — https://ped.fz-juelich.de/database/doku.php?id=corridor3
- 一方向流コリドー(BaSiGo, DOI 10.34735/ped.2013.6) — https://ped.fz-juelich.de/database/doku.php?id=corridor5
- ボトルネック(HERMES, DOI 10.34735/ped.2009.6) — https://ped.fz-juelich.de/database/doku.php?id=hermes_bottleneck
- 90°交差(BaSiGo, DOI 10.34735/ped.2013.4) — https://ped.fz-juelich.de/database/doku.php?id=crossing_90
- re3data レジストリ項目 — https://www.re3data.org/repository/r3d100013370
- PeTrack(軌跡抽出ソフト) — https://www.fz-juelich.de/ias/ias-7/EN/Expertise/Software/PeTrack/petrackNode.html

### 参照曲線・ばらつき
- Seyfried, Steffen, Klingsch & Boltes (2005) "The Fundamental Diagram of Pedestrian Movement Revisited"(Weidmann 4 領域・実験設定) — https://arxiv.org/abs/physics/0506170
- Vanumu, Rao & Tiwari (2017) "Fundamental diagrams of pedestrian flow characteristics: A review", ETRR 9:49(オープンアクセス) — https://doi.org/10.1007/s12544-017-0264-6 / PDF ミラー https://d-nb.info/1145310427/34
- Chattaraj, Seyfried & Chakroborty (2009) "Comparison of Pedestrian Fundamental Diagram Across Cultures"(印独差) — https://arxiv.org/pdf/0903.0149
- Zhang & Seyfried (2012) "Empirical characteristics of different types of pedestrian streams" — https://arxiv.org/abs/1207.5931
- Duives, Sparnaaij, Daamen & Hoogendoorn "How Many People Can Simultaneously Move Through a Pedestrian Space?"(CrowdLimits・多方向流) — https://arxiv.org/pdf/1908.07208
- Steffen & Seyfried (2010) "Methods for measuring pedestrian density, flow, speed and direction with minimal scatter"(Voronoi 法) — https://arxiv.org/pdf/0911.2165
- Alhajyaseen & Nakamura "Quality of pedestrian flow and crosswalk width at signalized intersections"(日本・横断歩道) — https://www.sciencedirect.com/science/article/pii/S0386111210000038
- Cao, Seyfried, Zhang, Holl & Song (2017) "Fundamental diagrams for multidirectional pedestrian flows" — https://doi.org/10.1088/1742-5468/aa620d

### SFM 較正手法
- Johansson, Helbing & Shukla (2007) "Specification of the Social Force Pedestrian Model by Evolutionary Adjustment to Video Tracking Data", Adv. Complex Syst. 10(supp02), 271–288 — https://www.worldscientific.com/doi/abs/10.1142/S0219525907001355
- Helbing & Johansson "Pedestrian, Crowd and Evacuation Dynamics"(**Table 1 の較正値 A/B/λ の出典**) — https://arxiv.org/abs/1309.1609
- Kretz, Hengst & Vortisch "Pedestrian Flow at Bottlenecks — Validation and Calibration of Vissim's Social Force Model"(**VISSIM P0 パラメータの出典**) — https://arxiv.org/pdf/0805.1788
- Köster, Treml & Gödel (2013) "Avoiding numerical pitfalls in social force models", Phys. Rev. E 87, 063305 — https://doi.org/10.1103/PhysRevE.87.063305
- Kretz (2015) "On Oscillations in the Social Force Model" — https://arxiv.org/pdf/1507.02566
- Kretz (2015) "The Social Force Model and its Relation to the Kladek Formula" — https://arxiv.org/abs/1512.01426

### 速度ベースモデル(v₀(ρ) の防御)
- Tordeux, Chraibi & Seyfried (2015) "Collision-free speed model for pedestrian dynamics" — https://arxiv.org/abs/1512.05597
- Chraibi et al. (2019) "Generalized collision-free velocity model for pedestrian dynamics" — https://arxiv.org/pdf/1908.10304
- JuPedSim Pedestrian Models(Collision-Free Speed Model の製品実装) — https://www.jupedsim.org/stable/pedestrian_models/

### 検証プロトコル
- RiMEA e.V. — https://www.rimea.de/
- **RiMEA Guideline 4.1.1(2025-09-11・独英・56 p・CC BY-ND 4.0)** — https://rimea.de/wp-content/uploads/2025/09/rimea-4.1.1-d-e-1.pdf
- RiMEA Test 16 生データ(Zenodo, SingleFileComparator v1.0.0) — https://doi.org/10.5281/zenodo.8378592
- RiMEA Test 16 10/90 パーセンタイル — https://rimea.de/wp-content/uploads/2025/01/test_16_percentiles.xlsx
- SingleFileComparator(MIT・KS 検定ツール) — https://github.com/PedestrianDynamics/SingleFileComparator
- オンライン validator — https://go.fzj.de/validator(**認証リダイレクトのため画面未検証**)
- ISO/TR 13387-8:1999(RiMEA が採る 4 段検証の枠組)

### リポジトリ内の既存資料
- `docs/research/physics-engine-selection.md` §5.6 / §7.2 / §8(P4 の前提)
- `docs/research/social-force-crowd.md` §1(SFM パラメータ 2 系統)
- `reference/physics_bench/`(`run_bench.py` の `section_calibration_probe` / `section_fundamental_diagram` が P4 の土台。`run_fd_periodic` は既に `engine_kw` で A・B を差し替えられる)
- `src/society/world/sfm_core.py`(A_DEFAULT=2000.0 N, B_DEFAULT=0.08 m, MASS_DEFAULT=80.0 kg, TAU_DEFAULT=0.5 s, **LAMBDA_DEFAULT=0.5**, V_MAX_FACTOR=1.3, RADIUS_MIN=0.25, CUTOFF_M=2.0, WALL_A/B=2000.0/0.08)

---

## §8 この調査で言えないこと(限界)

1. **実データを 1 バイトもダウンロードしていません。**ファイル URL・列定義・ライセンスは**実験ページの記載を読んだだけ**で、実ファイルの中身は未検証[要確認]。
2. **corridor5 の通路寸法が資料間で食い違います**(5 m 説と 8 m×3 m 説)。**metadata JSON を一次情報にしてください**[要確認]。
3. **hermes_bottleneck の開口幅一覧を特定できていません**[要確認]。
4. **RiMEA の streamlit validator は認証で開けず、閾値・p 値の運用は未確認**[要確認]。
5. **「密度 ρ で引く v₀ テーブル」そのものの一次文献は特定できませんでした。**確認できたのは**間隔 s で引く V(s)**(Tordeux 2015)。§6.2 の P4-3 はこれを反映して s ベースを提案しています。
6. **日本人の自由歩行速度分布を取得していません。**文化差が存在すること[Chattaraj 2009]は確認しましたが、渋谷に当てる数値は未取得[要確認]。
7. **§6.1 の「VISSIM の A が本リポジトリと完全一致」は、両者の力の定義が同一である前提**です。本リポジトリは `exp((r_i+r_j − d)/B)`(**体表間隔ベース**)、VISSIM の定義式は論文に明示されていません。**一致は示唆的ですが、等価性の証明ではありません**[推定]。
8. **§3.3 のコスト見積りは既存スループット実測からの外挿**で、2 項化による計算量増加(カットオフ半径が B=0.08→2.8 m で伸びる分)を織り込んでいません。**近傍探索のコストは増えます**[推定・未測定]。
