# 天候の生成型実データ化 — 生成器の較正結果と `weather.py` 統合設計

> 作成: 2026-08-01。担当: Opus(実行役)。**本ノートの §1–§3 は実施済みの成果、§4 以降は設計案であり未実装**
> (`src/` と `conf/` は本バッチで1行も触っていない)。
> 発端: ユーザー決定 —
> 「**天候は現実と必ず同期する必要はない。データからサンプリングしたもの、もしくはこれまでのデータを
> 反映した天気を生成する形でよい**」。
> 前提調査: [dt-snapshot-reproposal-notes.md](dt-snapshot-reproposal-notes.md) §2.3(天候は100%合成)/ §3.1(データ源カタログ)。

---

## §0 結論の先出し(7点)

1. **東京の8月の実測日別データ 30年分(1996–2025・930日・欠測0)を凍結した**。
   `data/snapshot/weather_tokyo_aug.json`(331KB・`payload_sha256=98d251b4…`)。
   出典 = 気象庁「過去の気象データ検索(日ごとの値)」・ライセンス = **公共データ利用規約1.0**(商用可・出典明示必須)。
2. **現行モデルの欠陥は数字で確定した**。`weather.py` の8月は `32 + U{−3..+3}` なので
   **上限が 35℃ ちょうど・36℃以上は確率0**、35℃の出現率は 1/7 = **14.4%** で固定、
   **日間自己相関は −0.04(=ゼロ)**、年ごとの差もほぼ無い(年平均のSD 0.37℃)。
   実測(2015–2025)は P(≥35℃) **23.5%**・P(≥36℃) **7.3%**・lag-1 自己相関 **0.52**・年平均のSD **1.45℃**。
3. **連続猛暑を出すのに要るのは2つ**: (a) 日間の **AR(1)**、(b) **年効果(低周波成分)**。
   (a) だけでは足りない — 実証: 年効果を外すと「年内に5連以上の猛暑日が出る確率」が有意に下がる
   (テストで固定: `test_year_effect_is_what_creates_long_spells`)。
4. **較正済み生成器は猛暑連長分布を再現する**。猛暑連長の KS 距離 **D=0.081**(現行合成は **D=0.392**)。
   「年内最長連の平均」実測 3.55 日 / 生成器 3.16 日 / 現行合成 1.49 日。
   **2025年8月に実際に起きた10日連続猛暑**も生成器では到達可能(現行合成では構造的に不可能)。
5. **統合は `mode: synthetic(既定)/ generated / table` の3モードで、既定 OFF ならバイト一致**。
   `generated` は **strict 等級を維持できる**(ラン中のネットワーク呼び出しゼロ・静的ファイルのみ)。
6. **checkpoint に手を入れずに済む設計がある**。AR(1) の状態を `sim` に持たせると resume で復元が要るが、
   **「マスターシードから全系列を一度に決定論生成してメモ化する」**方式なら状態を持たないので
   `checkpoint.py` は無改修(実査: checkpoint.py に weather 由来の状態は現在ゼロ)。
7. **残る未達を隠さない**: 生の日別系列の lag-1 自己相関は 実測 0.52±0.05 に対し**生成器 0.39**。
   原因は WGEN 系が「天気状態の連鎖」と「気温残差の AR(1)」を独立に置くこと(§3.4)。
   猛暑連長には効いていないので本バッチでは採用したが、`weather_gen_params.json` の
   `validation.known_gaps` に数値ごと記録してある。

---

## §1 リサーチ結果(実装前調査・出典 URL つき)

> 調査日 2026-08-01。**取得できなかったものは「一次未確認」と明記**し、推測で埋めていない。

### 1.1 確率的天候生成器(stochastic weather generator)の標準設計

| 何 | 内容 | 出典 |
|---|---|---|
| **WGEN の原型** | Richardson (1981) が日別の降水・気温・日射の確率生成を定式化。Richardson & Wright (1984) が **WGEN** として実装公開。降水の発生は**1次マルコフ連鎖**、降水量は**ガンマ分布**、他の変数(最高気温・最低気温・日射)は**lag-1 自己相関と変数間相互相関をもつ1次自己回帰**で生成する。「モデルは各変数の**持続性(persistence)**、変数間の依存、各変数の季節性を扱う」 | [WGEN: A Model for Generating Daily Weather Variables](https://2e769f3d3f5b8fb1e525-3dcd56c3560bcd90dd22a85e7e925b21.ssl.cf1.rackcdn.com/WGEN.pdf)(USDA-ARS ARS-8)。**【一次未確認】PDF のテキスト層が壊れており式そのものは本文から抽出できなかった**(検索結果由来の記述) |
| **降水の2状態1次マルコフ連鎖** | 「A first-order Markov chain is used to describe the occurrence of wet or dry days and **the probability of rain on a given day is conditioned on the wet or dry status of the previous day**」= P(wet\|dry)=p01, P(wet\|wet)=p11。定常確率 π = p01/(1+p01−p11) | 同上 / [Wilks & Wilby (1999) *The weather generation game*](https://perso.univ-rennes1.fr/valerie.monbet/doc/Wilks&Wilby.pdf)(**【一次未確認】PDF が 10MB 超で本文取得に失敗**) |
| **気温の残差モデル(Matalas 型)** | 「Other required variables are calculated using a **first-order auto-regressive model with lag-1 auto-correlation and cross-correlation between all variables**」。この弱定常過程は **Matalas (1967)** による。実装は lag-0 / lag-1 の交差相関行列 M0・M1 を月ごとに求めて解く | [Applications of the MVWG Multivariable Stochastic Weather Generator (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3745989/) — 「the weakly stationary generating process proposed by Matalas」「auto- and cross-correlations … by calculating lag-0 and lag-1 cross-correlation matrices monthly」。**【一次未確認】χ(t)=A·χ(t−1)+B·ε(t) と A=M1·M0⁻¹ / B·Bᵀ=M0−M1·M0⁻¹·M1ᵀ の逐語式は、本調査で取得できた文献のどれにも本文として載っていなかった**(標準形として実装し、`tests/test_weather_gen_offline.py::test_matalas_ab_solves_the_defining_equations` で定義式を満たすことを機械検査している) |
| **wet/dry 条件付け** | 気温の平均・標準偏差を「その日が雨か否か」で分ける(雨の日は最高気温が低く分散が大きい)。MVWG も「calculations are **conditioned on the dry or wet status of the day**」 | 同 PMC |

### 1.2 連続猛暑(persistence)を再現するために何が要るか — **本調査の核**

| 知見 | 逐語/要旨 | 出典 |
|---|---|---|
| **weather generator は持続性を過小評価する** | 「Weather generators generally **underestimate persistence**, and while the incorporation of annual cycle of correlations improves persistence in winter, **it further lowers it in summer**」 | [Time Structure of Observed, GCM-Simulated, Downscaled, and Stochastically Generated Daily Temperature Series, *J. Climate* 14(20)](https://journals.ametsoc.org/view/journals/clim/14/20/1520-0442_2001_014_4047_tsoogs_2.0.co_2.xml) |
| **AR(1) 単体では分布形を再現できない** | 「The **AR(1) model is not able to reproduce the multimodality** of temperature distributions」 | [Stochastic weather generators: an overview of weather type models (Numdam / JSFS 156(1))](https://www.numdam.org/item/JSFS_2015__156_1_101_0/) |
| **★ 低周波(年々)変動を入れないと月・年スケールの分散が足りない** | 「A problem with daily weather generators is that **they underestimate monthly and inter-annual variances because they do not take into account the low-frequency component of climate variability**」。対策は複数の時間スケールで生成した気候時系列で日別出力を補正すること | [Chen, Brissette & Leconte (2010) *A daily stochastic weather generator for preserving low-frequency of climate variability*, J. Hydrology 388(3–4):480–490](https://www.sciencedirect.com/science/article/abs/pii/S0022169410003082) |
| **自己相関が高いほど熱波は長く・多くなる** | 「Positive autocorrelation results in the **clustering of similar conditions** … corresponding to phenomena like **longer and more frequent heatwaves**」 | [Temporal autocorrelation increases temperature-driven extinction risk by clustering stressful conditions (bioRxiv 2025)](https://www.biorxiv.org/content/10.1101/2025.07.29.667527.full.pdf) |

> **→ 設計への落とし込み**: 「日間 AR(1)」だけを入れると**月内の粒度は改善するが、暑い年/涼しい年の差が消える**。
> 東京8月の実測では**年平均のばらつき(SD 1.45℃)が日々のばらつき(SD 3.23℃)の 45% を占める**。
> よって **AR(1) + 年効果(ラン開始時に1回だけ引く低周波成分)** の2段構えにした。
> 年効果を外した対照実行を `validation.generated_no_year_effect` に併記してある。

### 1.3 気象庁 過去の気象データ — 取得方法とライセンス

| 項目 | 内容 |
|---|---|
| **使った窓口** | 「過去の気象データ検索(日ごとの値)」 `https://www.data.jma.go.jp/stats/etrn/view/daily_s1.php?prec_no=44&block_no=47662&year=YYYY&month=M&day=&view=`。**URL 構造が安定・年月をパラメータで指定できる**ので自動取得に向く。実測: 文字コードは **UTF-8**、日別表は **1976年〜2025年の8月すべてで 21 セル固定**(レイアウト検証をパーサに入れた) |
| **別窓口(手動)** | 「過去の気象データ・ダウンロード」 <https://www.data.jma.go.jp/risk/obsdl/>。地点・項目・期間を選んで **CSV(Shift_JIS / CRLF)**。自動取得が壊れたときの手順書として `--emit-schema` の `manual_entry_instructions` に埋めてある |
| **ライセンス** | 気象庁のコンテンツは権利表記のない限り「コンテンツは、権利表記の記載がない限り**「公共データ利用規約(第1.0版)」に準拠した利用条件の下で、利用することができます**」。**商用可・CC BY 4.0 互換・出典明示必須**、加工した場合はその旨を別記。出典表記の例示は「出典:気象庁ホームページ(当該ページのURL)」 <https://www.jma.go.jp/jma/kishou/info/coment.html> / 規約本体 <https://www.digital.go.jp/resources/open_data/public_data_license_v1.0> |
| **robots** | `https://www.jma.go.jp/robots.txt` / `https://www.data.jma.go.jp/robots.txt` とも **HTTP 404 = クロール制限の宣言なし**(2026-08-01 実測)。それでも要求間隔 1.5 秒・1回の実行で30要求に限った |
| **地点の落とし穴** | **渋谷区内に気象庁の気温観測点は無い**。最寄官署「東京」(prec_no=44 / block_no=47662 / アメダス 44132)は**北の丸公園**で渋谷駅から約 5.8km NE。しかも **2014-12-02 に大手町から北の丸公園へ移転**している(<https://www.jma.go.jp/jma/kishou/know/kansoku/info/20141202_tokyo_rojo.html>)。→ 30年一括の較正は**低温側へ系統的に引かれる**ので、既定の較正窓は**移転後の 2015–2025** にした(全期間は感度分析として併記) |

### 1.4 WBGT(暑さ指数)の気温・湿度からの近似式

環境省 熱中症予防情報サイト「当サイトで提供する暑さ指数(WBGT)について」<https://www.wbgt.env.go.jp/wbgt_detail.php> より**逐語**:

- **実測地点(全国47点)の定義式**: `WBGT = 0.7×Tw + 0.2×Tg + 0.1×Ta`(Tw=湿球温度・Tg=**黒球温度**・Ta=気温)
- **推定値・予測値(794点以上)の推定式**:
  `WBGT = 0.735×Ta + 0.0374×RH + 0.00292×Ta×RH + 7.619×SR − 4.557×SR² − 0.0572×WS − 4.064`
  (Ta[℃] 気温 / RH[%] 相対湿度 / **SR[kW/m²] 全天日射量** / WS[m/s] 平均風速)
- 出典表記: 「**小野雅司ら(2014)** 通常観測気象要素を用いたWBGTの推定.日生気誌,50(4),147-157.」
- 注記: 気象庁の観測は**強制通風条件下**であり、実際の生活環境は「より厳しい暑熱環境」になる
- **熱中症警戒アラート**の発表基準は「翌日・当日の**日最高暑さ指数(WBGT)が33(予測値)に達する場合**」
  <https://www.wbgt.env.go.jp/about_alert.php>

**本バッチでの扱い(★重要な限界)**: 凍結データに**全天日射量は無い**(日別値に含まれない)。
そこで `SR ≈ 0.75 × min(1, 日照時間 / 13.3)` という**代理**を置き、日最高 WBGT の代理として
`Ta = 日最高気温`・`RH = 日最小湿度`(最高気温と近い時刻に起きるため)を入れている。
係数と仮定は `weather_gen_params.json` の `wbgt` ブロックに全部書き出した。
**これは公式の暑さ指数ではない**。環境省の実測 WBGT(東京 44132・実況2010年〜)との突合は**未実施**
(CSV は POST フォーム経由、WebAPI `https://www.wbgt.env.go.jp/api/v1/getSurveyData` は
**HTTP 400** を返し引数仕様を確定できなかった=エンドポイントは存在する)。**次バッチの課題**。

---

## §2 凍結した実測(`data/snapshot/weather_tokyo_aug.json`)

| 項目 | 値 |
|---|---|
| 地点 | 東京(prec_no 44 / block_no 47662 / アメダス 44132 / 北の丸公園) |
| 期間 | **1996–2025年の8月・930日**(30年・**欠測0日**) |
| 列 | 最高/最低/平均気温・降水量・平均/最小湿度・日照時間・平均風速・降雪・天気概況(昼/夜) |
| `payload_sha256` | `98d251b4ff558ea507ba120b84e541d79650f2c14cedbaaa49b9549273c2bd23` |
| 再現性 | ハッシュは**取得日時を含まない**ので、同じ年月を取り直せば同じ値になる(`--verify` で機械検査) |

### 2.1 年ごとの実測(抜粋)— 何が起きているか

| 年 | 平均最高気温 | 最高値 | 猛暑日(≥35℃) | **最長連続** |
|---|---:|---:|---:|---:|
| 2015 | 30.5 | 37.7 | 8 | **7** |
| 2019 | 32.8 | 35.6 | 10 | 4 |
| 2020 | 34.1 | 37.3 | 11 | 4 |
| 2023 | 34.3 | 36.7 | 9 | 3 |
| 2024 | 33.6 | 35.9 | 7 | 2 |
| **2025** | **34.5** | **38.5** | **18** | **10** |

**2025年8月に東京で10日連続の猛暑日が実際に起きた**ことがデータで確認できた
([dt-snapshot-reproposal-notes.md §0-2](dt-snapshot-reproposal-notes.md) の記述と整合)。
本選10日ラン(8/16–8/26)はこの期間とほぼ重なる。

### 2.2 レジームシフト(観測点移転 + 温暖化)

| 窓 | 日数 | 平均最高気温 | P(≥35℃) | 平均湿度 |
|---|---:|---:|---:|---:|
| 1996–2014(移転前) | 589 | 31.47 | **7.6%** | ≈70% |
| 2015–2025(移転後) | 341 | 32.53 | **23.5%** | ≈78% |
| 1996–2025(全期間) | 930 | 31.86 | 13.4% | — |

**P(≥35℃) が 7.6% → 23.5% と3倍になっている。**
この差には温暖化と観測点移転(大手町→北の丸公園)が**分離できない形で混ざっている**。
湿度の +8 ポイントも移転(緑地への移設)の影響が疑われる。
→ **較正の既定窓は 2015–2025**(移転後のみ)。全期間の較正結果は
`weather_gen_params.json` の `sensitivity_alt_window` に併記した。

---

## §3 較正結果(`data/snapshot/weather_gen_params.json`)

較正窓 **2015–2025 の8月(341日・11年)**。`payload_sha256=b912c745…`。**同入力→バイト同一**(検証済み)。

### 3.1 パラメータ

**天気状態の1次マルコフ連鎖(3状態。行=前日, 列=当日)**

| 前日\当日 | 晴 | 曇 | 雨 |
|---|---:|---:|---:|
| 晴 | **0.598** | 0.197 | 0.205 |
| 曇 | 0.245 | **0.459** | 0.296 |
| 雨 | 0.229 | 0.267 | **0.505** |

周辺分布 = 晴 0.378 / 曇 0.293 / 雨 0.328。
**WGEN 原型の2状態表現**(雨 = 日降水量 ≥ 1.0mm = 気象庁の降水日の定義):
`P(wet|dry) = 0.2444` / `P(wet|wet) = 0.5048` / 定常確率 π = 0.3305(実測の湿日率 0.3284 と整合)。

**気温**

| 天気状態 | n | 最高気温 平均 | SD | 最低気温 平均 | SD |
|---|---:|---:|---:|---:|---:|
| 晴 | 129 | **34.00** | 1.74 | 25.48 | 1.43 |
| 曇 | 100 | 32.86 | 2.45 | 25.06 | 1.99 |
| 雨 | 112 | **30.55** | 2.99 | 23.81 | 1.68 |

- 月内トレンド: 最高 **−0.0827 ℃/日**・最低 −0.0460 ℃/日(基準日 = 8/16)。8月は下旬ほど涼しい。
- **年効果**(ラン開始時に1回だけ引く): SD 最高 **1.352℃** / 最低 0.890℃ / 両者の相関 **0.957**。
  (年内 SD は 最高 2.864 / 最低 1.866)
- **AR(1)**(Matalas 2変量): `M0 = [[1, 0.7319],[0.7319, 1]]`, `M1 = [[0.5268, 0.5453],[0.5407, 0.6320]]`
  → `A = [[0.2749, 0.3441],[0.1682, 0.5089]]`, `B = [[0.8170, 0],[0.4477, 0.6221]]`(Cholesky)
- **物理ガード** `clip`: 最高 19.2–39.7℃ / 最低 16.6–31.4℃(凍結実測**全期間**のレンジ ±1℃)。
  **モデルではなく箍**。生成値の **0.65% しか触れていない**(触れる割合は `share_clipped` に出る)。

**降水量(湿日)**: ガンマ shape **0.502** / scale **35.18**(平均 17.67mm・実測最大 138.5mm)。
**湿度**: 状態別平均 晴 73.0 / 曇 76.0 / 雨 86.9(SD 5.6–6.5)、最高気温偏差への回帰係数 **−0.729 %/℃**、残差SD 5.66。
**WBGT 代理**: 実測日に当てはめると 平均 29.2 / p90 32.2 / 最大 33.7、**31以上が 32.0%・33以上が 0.9%**。

### 3.2 ★ 検収の中心 — 実測 / 生成器 / 現行合成の対比

モンテカルロ 3,000年 × 31日(seed 20260801)。実測は 2015–2025 の 341日。

| 指標 | **実測** | **較正生成器** | **現行合成 weather.py** |
|---|---:|---:|---:|
| 平均最高気温 [℃] | 32.53 | **32.50** | 32.00 |
| 最高気温 SD [℃] | 3.23 | **3.20** | 2.00 |
| 歪度 | −1.21 | −0.39 | −0.00 |
| 期間最高値 [℃] | 38.5 | 39.7 | **35.0(上限)** |
| **P(最高 ≥ 35℃)** | **23.46%** | **22.12%** | 14.38% |
| **P(最高 ≥ 36℃)** | **7.33%** | 12.92% | **0.00%(構造的に不可能)** |
| **lag-1 自己相関** | **0.521** | **0.393** | **−0.036** |
| 年平均のSD [℃] | 1.447 | 1.607 | 0.368 |
| P(最低 ≥ 25℃) 熱帯夜 | 54.5% | 46.9% | 57.5% |
| P(雨) | 32.8% | 33.2% | 30.0% |
| **猛暑連長 平均 [日]** | **2.22** | **2.05** | 1.16 |
| **年内最長連の平均 [日]** | **3.55** | **3.16** | 1.49 |
| P(年内に5連以上) | 18.2% | 22.6% | **0.17%** |
| P(年内に10連以上) | 9.1%(11年中1年) | 3.7% | **0%** |
| **KS(最高気温)** | — | **D = 0.0913** | D = 0.2509 |
| **KS(猛暑連長)** | — | **D = 0.0813 (p=0.97)** | D = 0.3919 (p=2e-5) |

**読み方**:
- 気温分布の KS 距離は **0.25 → 0.091**(2.7倍改善)、猛暑連長の KS 距離は **0.39 → 0.081**(4.8倍改善)。
- 現行合成では「年内に5日連続の猛暑」が **0.17%** の年にしか起きない。実測は **18%**。生成器は 23%。
- **P(≥36℃) は生成器が出しすぎる**(12.9% vs 実測 7.3%)。正規 AR(1) が対称なのに実測が
  左に歪んでいる(歪度 −1.21)ため。`clip` は上限 39.7℃で切っているが分布形までは直せない。

### 3.3 感度分析(較正窓を全期間 1996–2025 にした場合)

| 量 | 2015–2025(既定) | 1996–2025 |
|---|---:|---:|
| 平均最高気温 [℃] | 32.53 | **31.86** |
| P(≥35℃) | 23.5% | **13.4%** |
| P(wet\|wet) | 0.505 | 0.448 |
| P(wet\|dry) | 0.244 | 0.213 |
| 年効果 SD [℃] | 1.352 | 1.286 |
| lag-1(標準化残差) | 0.527 | 0.525 |

**マルコフ連鎖と AR(1) はほぼ同じ**(気候の構造は変わっていない)が、**気温の水準が 0.67℃ 違う**。
2026年の8月を再現したいなら移転後の窓を使うべき、というのが本ノートの立場。

### 3.4 ★ 再現できていないこと(隠さない)

| 未達 | 実測 | 生成器 | 原因と判断 |
|---|---:|---:|---|
| **生の系列の lag-1 自己相関** | 0.521 ± 0.048 | 0.393 | 標準化残差 χ の lag-1 は**設計どおり合っている**(実測 0.517 / 生成 0.509 を実測)。差は WGEN 系が「天気状態の連鎖」と「気温残差の AR(1)」を**独立**に置くため `Cov(状態_t, 残差_{t−1})` が 0 になることに由来する(現実には「今日が平年より暑い→明日も晴れやすい」結合がある)。**気温の条件付けを wet/dry 2状態(WGEN 原型)にすると 0.374 でむしろ悪化**、状態別SDをプールしても 0.409。よって3状態条件付けのまま採用した。文献も「weather generators generally underestimate persistence」と一致(§1.2) |
| **分布の歪度** | −1.21 | −0.39 | 正規 AR(1) は対称。結果として **P(≥36℃) を 1.8倍に過大評価**する。改善するには残差を経験分位でマッピングする半ノンパラ型が要る=**次バッチ以降の選択肢** |
| **熱帯夜(最低≥25℃)** | 54.5% | 46.9% | 最低気温の年効果 SD が小さめ(0.89℃)。都市キャノピー補正(北の丸公園は夜間が特に低い・移転で日最低 約−1.4℃)を入れていないことと同じ根 |

いずれも `weather_gen_params.json` の `validation.known_gaps` に**数値と診断つきで機械可読に記録**してある。

---

## §4 `weather.py` への統合設計案(★未実装・次バッチ)

> **本節の file:line は 2026-08-01 の作業ツリー実査**。別エージェントが `src/` を並行改修中のため、
> `scheduler.py` / `simulation.py` の行番号は着手時に再確認すること(`weather.py` 自体は本バッチ中は無改変を確認済み)。

### 4.1 3モードの定義

| mode | 何をするか | 等級 | 8月以外 |
|---|---|---|---|
| **`synthetic`(既定)** | 現行のまま(`_MONTH_CLIMATE` + ±3℃ 一様)。**1バイトも挙動を変えない** | strict | そのまま動く |
| **`generated`** | `weather_gen_params.json` から §3 の生成器で日別系列を作る | **strict**(静的ファイル + マスターシードの純関数。ラン中のネットワーク呼び出しゼロ) | **較正済みの月が無ければ `synthetic` へフォールバック**(params の `months` にキーが無い月) |
| **`table`(任意)** | `weather_tokyo_aug.json` の実日付を引く(例: 2025-08-16〜26 をそのまま使う) | strict(乱数を1つも引かない=完全決定論) | 凍結済みの年月のみ |

`table` は「ある時点の現実を切り取る」というユーザーの DT 定義に**最も忠実**だが、
1つの実現しか出せない(反実仮想ができない)。**`generated` を主、`table` を対照**に置くのが素直。

### 4.2 決定論の設計 — **checkpoint を触らずに済ませる**

生成器は AR(1) とマルコフ連鎖なので「昨日の状態」が要る。素直に `sim` へ状態を持たせると
**resume で復元が必要になり `checkpoint.py` の改修が発生する**(実査: 現在 `checkpoint.py` に
weather 由来の状態は**1つも無い**)。

**推奨: 状態を持たず、全系列を1本のストリームから決定論生成してメモ化する。**

```
weather_for(sim, day_index):
    if mode != "generated": …現行どおり…
    series = getattr(sim, "_weather_series", None)
    if series is None or len(series) <= day_index:
        rng = sim.hub.stream("weather_gen", 0)      # ★新キー。既存 "weather" の draw 順は不変
        series = _generate_series(rng, params, month_of(day0), n_days=day_index + 1 + margin)
        sim._weather_series = series                 # 純粋なメモ化(状態ではない)
    return series[day_index]
```

- **resume 安全**: 再構築は `(master_seed, params)` だけの関数なので、途中から再開しても同じ系列になる。
- **既存 stream 不変**: 新キー `"weather_gen"` を使うので、`synthetic` モードの `stream("weather", day)` の
  draw 順・値は完全に不変(= golden 不変)。
- **年効果**は「そのランに1回」= 系列生成の冒頭で1回だけ引く(§3 の設計と一致)。
- コストは1ラン数十日ぶんで無視できる。

### 4.3 統合時に変更が必要な点(file:line 列挙・**読み取りのみで作成**)

| # | 場所 | 現状 | 要る変更 | 既定OFFでバイト一致か |
|---|---|---|---|---|
| 1 | `src/society/weather.py:35-52` `build_cfg` | `enabled` / `rain_grievance` / `monthly` / `neutral` の4キー | `mode`(既定 `"synthetic"`)、`gen_params`(パス。**envpack 経由で受ける**=下記7)、任意 `heat_grievance` を追加 | ○(既定値で従来と同一 dict になるようキー追加のみ) |
| 2 | `src/society/weather.py:55-72` `_sample` | 合成サンプラ | **無改変**。`generated` は別関数 `_sample_generated` / `_generate_series` を新設 | ○ |
| 3 | `src/society/weather.py:75-87` `weather_for` | `sim.hub.stream("weather", day_index)` から毎日引く | mode 分岐 + §4.2 のメモ化。**`synthetic` 経路は1行も変えない** | ○ |
| 4 | `src/society/weather.py:90-97` `weather_line` | `f"今日の天気: {cond}、最高{temp_hi}℃。"` | **文言を変えないこと**(変えると全エージェントの発火/計画/内省プロンプトが変わり LLM 出力が全滅する)。湿度・WBGT を足したいなら**別フラグ(既定 OFF)**で末尾追加にする | ○(既定 OFF なら) |
| 5 | `src/society/weather.py:100-107` `discomfort_delta` | `_BAD_CONDS = {"雨","雪"}`(`:32`)のみ。**暑さは不快感に入っていない** | 猛暑を入れるなら `heat_grievance`(例: `temp_hi ≥ 35` で加算)。**別論点なのでユーザー承認を分けて取る** | ○(既定 0.0) |
| 6 | `src/society/engine/scheduler.py:3568,3578-3588` `_phase_calendar_weather` | payload は `{"cond","temp_hi"}`(+ 暦ONで `date`/`weekday`/`holiday`) | `generated` のときだけ `temp_lo`/`precip_mm`/`humid`/`wbgt` を追加。**`synthetic` では payload を増やさない**(L1 バイト一致のため) | ○(mode 分岐すれば) |
| 7 | `src/society/engine/simulation.py:281-293` | `_weather_mod.build_cfg(raw_wea, monthly=envpack.climate.monthly, neutral=…)` | **params ファイルのパスは `envpack.climate` から渡す**。`src` に東京固有のパスを書かない原則(`simulation.py:290` のコメント「基盤に東京の気候を残さない」)を守る | ○ |
| 8 | `src/society/envpack.py:63,79-93` | `climate` は `monthly` / `neutral` の2キー | `gen_params: "data/snapshot/weather_gen_params.json"` を通す(`_monthly` と同様の正準化) | ○(未指定なら None) |
| 9 | `env/shibuya/env.yaml:83-98` `climate:` | 月別テーブルのみ | `gen_params:` の行を足す(**渋谷の env パックにだけ**書く) | ○ |
| 10 | `conf/config.yaml:1695-1697` `weather:` | `enabled` / `rain_grievance` | `mode: synthetic` を追加 + コメントで3モードと等級を説明 | ○ |
| 11 | `conf/observe.yaml:55-56` / `production.yaml:64-66` / `daily.yaml:52-54` | `enabled: true`(+`rain_grievance: 0.01`) | 本選で使うなら `mode: generated` を**プロファイル側で**指定 | — |
| 12 | `src/society/observer/schema.py:109` | `weather` イベントの説明が `{date, weekday, cond, temp_hi, holiday?}` | #6 で payload を増やすなら説明も更新 | ○ |
| 13 | `src/society/engine/simulation.py:1569-1574` summary | `world_mod` と `building_heights` だけ | **`weather_params_sha256` / `weather_source_sha256` を summary に載せる**。[dt-snapshot-reproposal-notes.md §2.8-4](dt-snapshot-reproposal-notes.md)「入力データのハッシュがラン成果物に残らない」への最初の回答になる | ○(mode≠synthetic のときだけ足す) |
| 14 | `src/society/engine/checkpoint.py` | weather 由来の状態はゼロ | **§4.2 の設計なら無改修** | ○ |
| 15 | `src/society/rng.py:22` `stream()` | キー任意 | 新キー `"weather_gen"` を使うだけ。**RngHub 側は無改修** | ○ |

### 4.4 conf スキーマ案

```yaml
weather:
  enabled: false
  mode: synthetic        # synthetic(既定・現行と完全同一) / generated(較正生成器) / table(実日付引き)
  rain_grievance: 0.0
  # mode: generated / table のときだけ効く。パスは envpack.climate.gen_params から来る。
  # generated: 較正済みの月(現状 8月のみ)以外は synthetic へ自動フォールバックし、
  #            フォールバックした事実を summary に記録する(黙って落とさない)。
  # table:     実日付を引く。world.calendar.start_date が凍結範囲外なら fail-fast。
  extra_prompt_fields: false   # true で weather_line に湿度・暑さ指数を足す(★プロンプトが変わる)
```

### 4.5 次バッチの検収基準(案)

1. `mode: synthetic`(既定)で **L1/L2/L3・agents・traits・llm_cache がバイト一致**(既存 golden)。
2. `mode: generated` で同 seed 2ラン一致・**resume 跨ぎ一致**(§4.2 の設計の実証)。
3. `mode: generated` の 31日ランで 天気イベントが 31件・`cond` が4種の語彙に収まる・
   `temp_lo ≤ temp_hi` が全日成立。
4. summary に `weather_params_sha256` が載る。
5. 較正済みでない月(例: 3月)を指定すると `synthetic` にフォールバックし、それが summary に出る。
6. フルスイート緑。

---

## §5 成果物一覧

| ファイル | 中身 | 追跡 |
|---|---|---|
| `scripts/fetch_weather_history.py` | 気象庁 日別データの取得・凍結・検証(`--verify` / `--emit-schema` / `--from-dir`) | 新規 |
| `scripts/fit_weather_gen.py` | 較正・モンテカルロ自己検証・WBGT ブロック生成 | 新規 |
| `data/snapshot/weather_tokyo_aug.json` | 実測 930日(1996–2025年8月)+ 出典・ライセンス・限界注記 + SHA-256 | 新規(331KB) |
| `data/snapshot/weather_gen_params.json` | 較正パラメータ + 実測要約 + 生成器の検証結果 + `known_gaps` + SHA-256 | 新規(17KB) |
| `tests/test_weather_gen_offline.py` | 32テスト(パース・スキーマ・改竄検知・決定論・統計検証・現行合成の欠陥固定) | 新規 |
| `docs/research/weather-generator-design.md` | 本ノート | 新規 |

再現手順(ネットワークが要るのは1行目だけ):

```
python scripts/fetch_weather_history.py --years 1996-2025 --months 8   # 約1分・30要求
python scripts/fit_weather_gen.py                                       # 約1分・決定論
python -m pytest tests/test_weather_gen_offline.py -q                   # 32 passed
```

---

## §6 既知の限界・未確認事項(まとめ)

1. **地点が渋谷ではない**。北の丸公園(渋谷駅から 5.8km NE・緑地内)。都市キャノピー補正は**入れていない**。
   夜間の低温バイアスが特に効く(移転で日最低 約 −1.4℃)。補正の根拠候補は
   [dt-snapshot-reproposal-notes.md §3.1](dt-snapshot-reproposal-notes.md) の W5(黒球温度)と W9(渋谷区本町局)。
2. **較正窓が 11年 = 341日**。年効果 SD は 11 標本からの推定で不確かさが大きい。
   30年窓は観測点移転を跨ぐので使わなかった(感度分析としては併記済み)。
3. **窓の中にも強い上昇トレンドがある**(2015年 猛暑日8日 → 2025年 18日)。
   生成器はこれを「年効果の分散」として吸収する。**2026年の予報ではない**。
4. **8月しか較正していない**。他月は `synthetic` フォールバックが要る(§4.1)。
   他月を足すには `--months 6,7,9` などで再取得すればよい(スクリプトは対応済み)。
5. **WBGT は近似**。全天日射量が無く日照時間からの代理。環境省の実測との突合は未実施。
   `getSurveyData` は HTTP 400(エンドポイントは存在・引数仕様は**一次未確認**)。
6. **文献の逐語式を一次確認できていないものがある**: Matalas (1967) の A/B 行列式、
   Richardson (1981) 原論文、Wilks & Wilby (1999) 本文(§1.1 の表に個別に明記)。
   実装は標準形として書き、**定義式を満たすことをテストで機械検査**して代替している。
7. **`src/` は未改修**。本ノート §4 は設計案であり、統合は次バッチ(ユーザー指示待ち)。
