# 在場の内生化 — 「範囲内に居る人の数」を個人の行動・予定・習慣から導く

> **ステータス: リサーチ文書(実装なし・判断待ち)** / 作成 2026-08-12
> 目的 = ユーザーの設計原理「在場は指定するものではない」をコード実測と文献・実データで裏付け、
> cap 切りと visit_rate 単純抽選を「個人由来の決定論関数」へ置き換えるための設計素材を揃える。
> **数値の規律**: 「実測」= 本リポジトリ内のコード・データの実値(出典つき)。「引用」= 文献の数値(URL つき)。
> 「推定」= 実測からの外挿(式を明記)。未測定を推定で埋めない。

---

## §1 原理の定式化

ユーザーの原文(2026-08 指示。強調は引用者):

> 「範囲内にいる人の数も**こちらが指定するものではない**かなって思っている。エージェントの移動についても
> エージェントの推論で決めたり、もしくは**予定に従って行動し**、範囲内に存在するのか、範囲内に存在しないのか
> 判別したりできるようにしてほしい。とにかく**世界のアルゴリズムによって結果が左右されたり、エージェントの
> 量が決まったりすることはなく**、エージェントの行動や思考、推論によって結果が現れるような状態にしたい。」

これを機構の言葉に定式化すると、要求は 2 つに分解できる:

1. **在場判別の個人化**: 「今日この街に居るか」は、各個人の**予定・習慣・推論**から決まる述語
   `present(person, day) = f(その人の属性・予定・習慣, 暦, 環境)` であるべきで、
   集計量(総在場数)はその**合算として創発**する。総数を直接指定する変数(cap・クォータ)は最終的に消える。
2. **決定論関数は原理違反ではない**: LLM 推論を 100 万人に回すのは呼数予算上不可能なので、
   大多数の個人については「行動・予定・習慣の**決定論関数(個人属性由来)**」が現実解。
   これは原理と矛盾しない — シフト表で平日に来る従業者は「予定に従って行動」している。
   原理が排除するのは「**誰の行動にも帰属できない世界側の切断・抽選**」であって、個人に帰属する規則性ではない。

現行機構をこの物差しで測ると(§2 で実測)、5 層のうち 4 層(resident/duty/workday_shift/cadence)+
stochastic 層の revisit 部分は**既に個人の暦・習慣の決定論関数**である。原理に反して残っているのは
**(a) present_cap による当日ランキング切り**(切られる理由がその人の行動に帰属できない・顔ぶれが日替わり)と
**(b) stochastic 層の visit_rate × 当日乱数の Bernoulli 抽選**(レートは個人属性だが「今日行くか」は世界のコイン)
の 2 点だけである。

---

## §2 現状機構の実測

### 2.1 presence 純関数(`src/society/world/presence.py`)

- 5 層の優先度: `_TIER = {resident:0, duty:1, workday_shift:2, cadence:3, stochastic:4}`(presence.py:57)。
- 資格判定 `_eligible`(presence.py:105-127):
  - `resident` → 常に True(:108-109)。
  - `duty` → `duty_pattern.days` の曜日一致(:110-111)。
  - `workday_shift` → `work_days` の曜日一致(:112-113)。
  - `cadence` → `school_day` は平日、`weekly_N` は週固有 stream で当週の n 曜日を確定(:114-121、`_weekly_days` :87-91)。
  - `stochastic` → revisit 個体は個体固定の周期(period 3..10 日・phase、`_revisit_present` :94-102)、
    それ以外は `hub.stream("presence", pid, day).random() < visit_rate` の **Bernoulli 抽選**(:123-126)。
- 曜日仕様の照合 `_days_match`(:78-84)は **未知仕様を平日扱いに後退**させる(:84)。
  ★機構的事実(本文書で発見): v8 プールの L2 には `work_days="mon-sat"` が **44,486 人**居るが(§2.3)、
  この後退規則により**土曜は失格**になる=名簿は土曜出勤を書いているのに presence は読めていない。
- 総数の決め方 `present_for_day`(:176-222):
  - `tier_quota=False`(旧既定)= 層優先で埋めて cap で break(:208-219)。第91 実測で cap 25万を
    workday_shift が食い切り**来街者ゼロ**の破綻(module docstring :33-36)。
  - `tier_quota=True`(本選 ON)= `quota_by_ratio`(:137-173、最大剰余法・乱数ゼロ)で cap を
    当日資格者の層別比率に分配し、**溢れた層だけ当日ランキングで切る**(:197-206)。
  - どちらの経路でも、切る順序は `_ranked`(:130-134)= `presence_rank` stream の**当日乱数**
    → **切られる個体は日替わり**。「なぜ自分は今日入れなかったのか」を個人の行動に帰属できない。
- スリム記述子は `pool.py::_slim`(src/society/world/pool.py:26-38)が P5 レコードから抽出
  (visit_rate/revisit/work_days/cadence/duty_days のみ。k・trait は読まない)。
- 本選 conf: `present_cap: 250000`・`tier_quota.enabled: true`(conf/finals_observe.yaml:65, 70-71)。
- docstring 自身が「在場実測曲線は v1 では使わない(**将来拡張点**)」と拡張余地を明記(presence.py:16)。

### 2.2 在場中個体の圏外判別は既にある(P4 境界)

`src/society/cognition/plan_boundary.py`(docstring :1-72)= 朝の計画のセグメントに場所を与え、
**場所が圏外のセグメントが despawn/respawn の時刻表そのもの**(新しい境界機構ゼロ・退出/帰還は既存機構・
`payload["boundary"]=="plan"` で機械分離・圏外個体はエンジンが構造的に素通り= LLM 呼もイベントも 0)。
つまり「範囲内に存在するかの**判別**」は在場者側には計画駆動で実装済み。**欠けているのは
「プールの 100 万人が今日来るかどうか」の決定が個人の行動由来でなく cap 切りである点**に絞られる。

### 2.3 v8 プール(第108 リビルド)の全数実測 — 本文書のための新規集計

`data/persona_pool`(meta.json: 総数 1,000,000・seed 42・night_shifts true)を**全数**読み取り、
`_eligible` と同じ規則で平日/週末の資格確率を合算した(読み取りのみ・シム本体無変更)。

| 層 | 名簿件数 | 平日の期待資格者 | 週末の期待資格者 | 実測の内訳 |
|---|---:|---:|---:|---|
| resident | 30,034 | 30,034 | 30,034 | L1 30,000 + 議員 34 |
| duty | 1,258 | 1,258 | 1,218 | L5(第108 で +227=street_life/車掌/city_ops 等) |
| workday_shift | 224,240 | 224,240 | 69,411 | `work_days`: mon-fri 110,343 / **all 69,411(夜勤等)** / **mon-sat 44,486** |
| cadence | 36,690 | 25,238 | 8,548 | school_day 16,690 / weekly_2〜4 計 20,000 |
| stochastic | 707,778 | 25,946 | 25,946 | visit_rate 平均 **0.01902**・revisit **10.07%**・E[1/period]=0.1786 |
| **合計** | **1,000,000** | **306,716** | **135,157** | |

- 第108 の実走実測(平日 306,846・週末 135,030)と**差 ±0.05%** = 期待値計算として整合
  (差は Bernoulli の実現値ゆらぎ)。v7 時点の 336,962/62,849(docs/plans/proposal-dp-u3-observe-250k.md §1.1)から、
  リビルドで**週末が 2.15 倍**に改善している(夜勤 `all` 化 69,411 + cadence 週末増)。
- 現実照合(国交省人流・docs/research/shibuya-concurrent-population.md、コア4メッシュ):
  平日ピーク同時滞在 371,829 に対し資格者 306,716 = **0.82**。週末ピーク 227,361 に対し 135,157 = **0.59**。
- ★週末の workday_shift 69,411 は全員 `"all"` 個体。`mon-sat` の 44,486 人は §2.1 の後退規則で
  土曜も日曜も失格(名簿の意図と機構がズレている)。
- stochastic 層の内部構造: revisit 10.07%(周期 3〜10 日=ヘビー来街者)+ 非 revisit 89.93%
  (visit_rate 0.003〜0.06、平均 0.019 ≈ 53 日に 1 回)— 「少数のヘビー+多数のライト」の
  二相構造を**既に持っている**(§3.3 の returners/explorers・NBD と同型)。

### 2.4 原理との照合(§1 の物差し)

| 機構 | 個人に帰属できるか | 判定 |
|---|---|---|
| resident 常在・duty 当番・workday_shift シフト暦 | ✅ 予定(暦)の決定論関数 | 原理適合 |
| cadence weekly_N(個体×週 stream) | ✅ 習慣の決定論関数 | 原理適合 |
| stochastic revisit(個体固定 period/phase) | ✅ 習慣(「6日ごとに来る常連」) | 原理適合 |
| stochastic 非revisit の Bernoulli 抽選(:126) | ❌ レートは個人属性だが当日の来否は世界のコイン | **要置換 (b)** |
| present_cap の当日ランキング切り(:130-134, :204, :219) | ❌ 切られる理由が個人に帰属せず・日替わり | **要廃止 (a)** |

---

## §3 文献・実データ

### 3.1 活動ベース交通需要モデル — 「人口合成→個人の活動計画→トリップが創発」の正統性

トリップ(=在場)を**ゾーン別レート表からでなく個人の活動スケジュールから導く**のは、交通需要モデルの
30 年来の主流転換であり、本設計原理の直接の先行系譜である。

- **総説**: 活動ベースモデル(ABM)は四段階法(レート表ベース)の限界を克服するために生まれ、
  世帯・個人の活動選択からツアー・トリップを導出する。
  [IntechOpen: Recent Progress in Activity-Based Travel Demand Modeling](https://www.intechopen.com/chapters/73240) /
  [大規模活動ベース需要生成のレビュー(ScienceDirect, 2025)](https://www.sciencedirect.com/science/article/pii/S2666691X25000296)
- **MATSim**: 合成人口の各個人が日次活動プログラムを持ち、それを反復実行・再計画して交通が創発する。
  公式書籍(Horni, Nagel, Axhausen 編 2016, オープンアクセス):
  [Ubiquity Press](http://www.ubiquitypress.com/books/e/10.5334/baw) / [matsim.org/the-book](https://matsim.org/the-book/)。
  計算量管理は**人口サンプリング+容量スケーリング**が定石(10% サンプル等):
  [Springer: An improvement in MATSim computing time for large-scale travel behaviour microsimulation](https://link.springer.com/article/10.1007/s11116-019-10048-0)
- **ActivitySim**: 米国 MPO コンソーシアム(MTC・SANDAG・ARC・PSRC 等)が共同開発する
  オープンソース活動ベースモデル。個人の日次活動パターン→ツアー→トリップのパイプライン。
  [公式ドキュメント](https://activitysim.github.io/activitysim/v1.5.1/) /
  [GitHub](https://github.com/activitysim/activitysim) /
  [コンソーシアム](https://softwarecollaborative.org/cooperatives/activitysim/)
- **TASHA**(トロント): 活動生成・場所選択・スケジューリングの 3 部構成で世帯の 1 日を合成。
  [Miller: The Toronto Case(TAC 発表資料)](http://conf.tac-atc.ca/english/annualconference/tac2015/s9/miller.pdf)
- **CEMDAP**: 計量経済モデル群で各合成個人の終日活動・トリップ列を生成。MATSim と接続して
  「活動計画→エージェントシミュレーション」の二段構成にした例:
  [Integration of Activity-Based with Agent-Based Models: Tel Aviv Model and MATSim(ResearchGate)](https://www.researchgate.net/publication/274410172_Integration_of_Activity-Based_with_Agent-Based_Models_an_Example_from_the_Tel_Aviv_Model_and_MATSim)
- **較正の作法(Cadyts)**: 観測交通量に合わせるとき、レート表を直接いじるのではなく
  **各個人の計画選択(選択肢集合内の選好)を観測と整合する方向に更新**する= 較正が個人行動の枠内に留まる。
  [Cadyts 公式](https://people.kth.se/~gunnarfl/cadyts.html) /
  [Flötteröd, Bierlaire, Nagel 2011: Bayesian Demand Calibration for Dynamic Traffic Simulations(Transportation Science)](https://pubsonline.informs.org/doi/10.1287/trsc.1100.0367)
- **日本の全国規模実装(Pseudo-PFLOW)**: PT 調査+公的統計から**全国 1.3 億人の合成個人の日次活動流**を
  生成した公開データセット。活動ベース合成が日本の統計環境で成立する実証。
  [arXiv:2205.00657](https://arxiv.org/abs/2205.00657) /
  [Wiley CACAIE 2024](https://onlinelibrary.wiley.com/doi/10.1111/mice.13285)

**含意**: 「在場数を指定せず、個人の活動計画の合算として街の人出が決まる」は交通工学では
**確立された標準形**であり、較正手法(観測量との整合を個人選択の枠内で取る)まで含めて先例がある。

### 3.2 東京の実データ — 目的構成・来街頻度・滞在人口変動

- **東京都市圏パーソントリップ調査(第6回・2018 実施)**:
  [調査本体](https://www.tokyo-pt.jp/person/01) / [e-Stat 統計トップ](https://www.e-stat.go.jp/statistics/00600550) /
  [目的種類別×代表交通手段別 OD 表(e-Stat)](https://www.e-stat.go.jp/stat-search/files?layout=dataset&toukei=00600550&tstat=000001151670&stat_infid=000032066127)
  - 総トリップは 7,066 万→6,579 万(約 −7%)、通勤 −10%・通学 −17%
    ([さいたま市の第6回調査解説](https://www.city.saitama.lg.jp/001/010/018/015/006/p061184.html)、引用)。
  - 目的別トリップ数(H20→H30、[広報誌 vol.35 PDF](https://www.tokyo-pt.jp/static/hp/file/publicity/vol35.pdf) から抽出、単位=万トリップ):
    通勤 1,372→1,365 / 通学 520→497 / 業務 690→326(−53%) / 私事 2,407→2,011(−16%) / 帰宅 3,350→3,113。
    **私事の内訳**(同): 買物 861→627 / 食事・社交・娯楽 418→263 / 観光・行楽・レジャー 112→76 /
    通院等 192→160 / 送迎 224→238 / 他の私用 455→522。外出率は 86.4%→**76.6%**(過去最低)。
    → H30 構成比(帰宅込み・5 目的計 7,312 万に対する推定): 通勤 18.7% / 通学 6.8% / 業務 4.5% /
    私事 27.5% / 帰宅 42.6%。**L3/L4 の目的マージン(通勤通学系 : 業務 : 私事 ≈ 26 : 5 : 28)の較正アンカー**になる。
    [第6回調査 記者発表 PDF](https://www.tokyo-pt.jp/static/hp/file/press/0324press.pdf)
- **東京都・繁華街利用実態調査(2001 年 3 月、都内 12,000 世帯配布+街頭 17,703 票+通行量 165 地点)**:
  [調査 PDF](https://www.sangyo-rodo.metro.tokyo.lg.jp/toukei/pdf/monthly/chusho/hankagai.pdf)(数値は PDF から抽出)
  - 「ふだん最も利用する繁華街」= 新宿 19.3% / 池袋 11.8% / 銀座 7.7% / **渋谷 7.5%**(区部住民に限ると渋谷 9.9%)。
  - **渋谷センター街入口の 12 時間通行量 = 平日 113,568 人・休日 約 11.2 万人**(全 165 地点中最大)。
    渋谷は**平日≒休日**の稀有な街=週末較正の重要性の傍証。
- **来街頻度の帯域化の先例(神宮前来街者調査)**: 来街頻度を「週1回以上/月1回以上4回未満/月1回未満」の
  3 帯に分けて行動圏を分析(JILA ランドスケープ研究 63(5), 2000)。
  [J-Stage PDF](https://www.jstage.jst.go.jp/article/jila1994/63/5/63_5_809/_pdf/-char/ja)
  → L4 の visit_rate 帯(週1超=revisit 相当/月1-4=0.03-0.13/月1未満=現行平均 0.019)と直接対応づけ可能。
- **モバイル空間統計(滞在人口の日変動)**:
  - [渋谷 2019/2022 比較(公式分析)](https://mobaku.jp/analysis/2022/1102_849.html): 平日勤務人口はピーク時
    約 2,000 人減で未回復・**休日来訪は 2019 水準まで回復**=平日と週末で别の母集団が動く実証。
  - [日経クロストレンド: 渋谷など主要 27 地点の年間人口推移](https://xtrend.nikkei.com/atcl/contents/18/00390/00006/)
  - [宙畑: モバイル空間統計で人の動きを可視化](https://sorabatake.jp/13070/):
    **渋谷スクランブル交差点はハロウィン(2016)に最大 +15,000 人** / GINZA SIX 開店日 +7,000 人超 /
    USJ 周辺は晴天日が雨天日より最大 +8,000 人。
- **リポジトリ内の一次実測(再掲)**: `data/jinryu/shibuya_concurrent_144step_curve.csv` =
  平日ピーク 371,829(14:00)・深夜最小 84,671(03:00)・休日ピーク 227,361・日内比 4.39 倍・平均/ピーク 0.633
  (docs/research/shibuya-concurrent-population.md・docs/plans/proposal-dp-u3-observe-250k.md §1.2)。

### 3.3 来訪頻度の個人差モデル — Bernoulli より現実的な habit 表現

- **NBD(負の二項分布)**: 反復購買・反復来店の古典。個人のレート λ が Gamma 分布で異質、
  個人内は Poisson → 集計が NBD。「平均レート 1 本」でなく**個人差の分布**で表すのが 60 年来の標準。
  [Monash Business School: NBD model(Ehrenberg 1959 系)](https://www.monash.edu/business/marketing/marketing-dictionary/n/negative-binomial-distribution-nbd-model)
- **Pareto/NBD・BG/NBD**: 非契約的な再来訪の「レート異質性+離脱」モデル(Schmittlein et al. 1987 →
  Fader-Hardie-Lee 2005)。RFM 集計と数理的に接続され、実装も枯れている。
  [pymc-marketing: Pareto/NBD 解説(原典参照つき)](https://www.pymc-marketing.io/en/latest/notebooks/clv/pareto_nbd.html)
- **普遍来訪法則**: 都市の任意の場所への来訪者数は ρ(r, f) ∝ (r·f)^−2(r=距離, f=来訪頻度/月)に従う
  — **来訪頻度分布はべき則**であり、一様な visit_rate や単峰の抽選では出ない形。
  [Schläpfer et al. 2021, Nature 593:522(The universal visitation law of human mobility)](https://www.nature.com/articles/s41586-021-03480-9) /
  [Nature 解説記事](https://www.nature.com/articles/d41586-021-01355-7)
- **returners / explorers 二分**: 個人の移動は「少数の場所に規則的に戻る群」と「新規探索群」に定量的に分かれる。
  [Pappalardo et al. 2015, Nature Communications 6:8166](https://www.nature.com/articles/ncomms9166)
  → 現行 L4 の revisit 10%(周期 3-10 日)+非 revisit 90% は**この二分の粗い離散化**として既に読める。

**含意**: visit_rate の「個人ごとに違うレート」は NBD の Gamma 異質性に相当し方向は正しい。
足りないのは (i) 当日の実現を**個人の周期・習慣**として表すこと(コインでなくカレンダー)、
(ii) レート分布の裾(ヘビー来街者)を f^−2 / NBD 形に較正すること、(iii) 目的・曜日・天候への感応。

### 3.4 ABM における open population — cap を置かない人口の先例

- **世帯人口の内生動態**: 出生・死亡・転入出・世帯形成を個人イベントとして回し、
  **人口規模を固定せず創発させる** ABM の標準形。
  [Geard et al. 2013: Synthetic Population Dynamics: A Model of Household Demography(JASSS 16(1)8)](https://www.jasss.org/16/1/8.html)
- **移動(migration)ABM レビュー**: 流入・ネットワーク形成・帰還の意思決定を個人の行動理論
  (計画的行動理論・random utility)で内生化する系譜の整理。
  [Klabunde & Willekens 2016, European Journal of Population](https://link.springer.com/article/10.1007/s10680-015-9362-0)
- **大規模実例**: ウクライナ避難民 ABM = 流出入が個人意思決定から創発する国規模シミュレーション。
  [PNAS Nexus 2024](https://academic.oup.com/pnasnexus/article/3/3/pgae080/7624910)
- **計算量との両立**: MATSim 系は「cap で切る」のではなく**標本率を下げて容量をスケール**する
  (10% 標本+flow capacity 0.1 等)。[Springer 2019(再掲)](https://link.springer.com/article/10.1007/s11116-019-10048-0)
  → 本シムの語彙では「present_cap で切る」ではなく「pool `--fraction` を下げる」(DP-U3 案 B と同型)が
  文献側の縮退線。**総量制約は世界側の切断でなく標本設計として置く**のが先例の答え。

### 3.5 天候・イベント感応 — 決定論関数の共変量にできる係数

| 共変量 | 係数(引用) | 出典 |
|---|---|---|
| 降雨(歩行者数) | **−5% 〜 −27%**(降雨有無・複数研究レンジ) | [Effects of Weather Variables on Pedestrian Volumes(eScholarship PDF)](https://escholarship.org/content/qt3zn9f4cr/qt3zn9f4cr.pdf?t=lpo18t) |
| 降雨 5mm/h(都市規模スマホ GPS・Boston/SF) | **週末トリップ −29%**(平日より週末の弾性が大) | [PMC5555086: Effect of weather on pedestrian trip count and duration](https://pmc.ncbi.nlm.nih.gov/articles/PMC5555086/) |
| 冬季・気温(モントリオール歩行者) | 弾性は**週末>平日**・雨が最大要因 | [Miranda-Moreno & Lahti(ResearchGate)](https://www.researchgate.net/publication/256116534_Temporal_Trends_and_the_Effect_of_Weather_on_Pedestrian_Volumes_A_Case_Study_of_Montreal_Canada) |
| 気温 +5°C | トリップ **+6.5〜8%**(夏の極端高温は逆に減) | 同上 PMC5555086 |
| 雨×小売チャネル | 路面店 footfall 減・モール増(行き先の付け替え) | [Here Comes the Sun: Fashion Goods Retailing under Weather Fluctuations(EJOR)](https://www.sciencedirect.com/science/article/abs/pii/S0377221720301028) |
| イベント日(渋谷ハロウィン 2016) | スクランブル交差点 **最大 +15,000 人** | [宙畑(モバイル空間統計)](https://sorabatake.jp/13070/) |
| 施設開業(GINZA SIX 初日) | 昼 +7,000 人超 | 同上 |
| 晴/雨の日差(USJ 周辺) | 最大 −8,000 人 | 同上 |

**含意**: 天候感応は「私事・娯楽目的のみに掛かる −10〜−30% の乗数・週末に強く効く」という
**目的別×曜日別の係数**として決定論関数に載せられる(通勤・duty には掛けない)。渋谷の
WBGT 実働(weather=generated・第108)が既に日次共変量の供給源として存在する。

---

## §4 設計素材(実装はしない。判断材料のみ)

### 4.1 cap を外したとき何人になるか(実測ベース)

- **平日 306,716 人・週末 135,157 人**(§2.3 全数集計。第108 実走 306,846/135,030 と ±0.05%)。
  - cap 250,000 比: 平日 **×1.227(+22.7%)**・週末は元々 cap 未達(×0.54)= 週末は**既に内生**。
  - 本選 10 日(8/16-26、週末 3 日)の平均在場(推定): cap 廃止 (7×306,716+3×135,157)/10 = **255,248**、
    現行 cap 250k (7×250,000+3×135,157)/10 = 215,547 → **平均 +18.4%**。
  - 現実照合: 平日 0.82(/ピーク 371,829)・週末 0.59(/ピーク 227,361)。cap 廃止は平日を現実に**近づける**
    (250k = 現実比 0.67 → 306.7k = 0.82)。週末 0.59 は cap と無関係の名簿較正問題(§5-3)。

### 4.2 stochastic 層の「目的関数化」— コインをカレンダーに置き換える 3 段階

**段階 1(最小・分布不変)**: 非 revisit 個体の Bernoulli(presence.py:126)を、revisit と同じ
**個体固定の period/phase 決定論**(:94-102 の一般化)に置換する。
`period_i = round(1/visit_rate_i)`(clamp [3, 365])・`phase_i` は個体固定 stream から。
→ 集計来訪率は保存(E[present] = 1/period ≈ visit_rate)・追加乱数ゼロ・k 非依存/resume 不変は不変。
個体の在場が「53 日ごとに来る人」という**説明可能な習慣**になり、「今日は行く日だから居る」が成立する。
係数の較正アンカー: 帯域は神宮前調査の 3 帯(§3.2)、分布形は f^−2 / NBD(§3.3)。

**段階 2(目的×曜日×天候)**: 各 L4 個体は既に `visit_purpose`(買い物/飲食/エンタメ等)を持つ
(data/persona_pool L4 レコード実測)。習慣カレンダーに個人属性由来の変調を載せる:
- 曜日プロファイル: 私事・娯楽目的は週末位相を優先(PT 調査の目的構成 §3.2 でマージン較正)。
  → 週末 0.59 問題の**名簿側の直し方**そのもの(週末だけ visit_rate を上げる「世界の乗数」ではなく、
  「週末に来る習慣の人」を目的構成比に合わせて置く)。
- 天候: 雨日は私事系の在場確率に −10〜−30% の乗数(§3.5)。weather は day の純関数(generated)なので
  R1(共通乱数・k 掃引間で同一)を壊さない。判定は「その人が雨に感応する目的で来る予定だったか」に帰属。
- イベント暦: ハロウィン等の既知イベント日は該当目的の個体の phase を引き寄せる(+1.5 万人規模のアンカー)。

**段階 3(cap 廃止)**: `present_for_day` の cap 切り(:204, :219)を撤去し、資格者=在場者にする。
較正は Cadyts 流(§3.1)= 総量の観測(jinryu 曲線)とのズレを **cap でなく個人の習慣パラメタ側**
(L4 の period 分布・週末位相比率)へ帰す。縮退線は cap でなく `--fraction`(標本設計、§3.4)。

### 4.3 計算量見積り(推定・式明記)

| 項目 | 現行(cap 250k) | cap 廃止(平日 306.7k) | 根拠 |
|---|---:|---:|---|
| presence 判定 | O(pool)=100 万/日 | 同じ(cap 切りソートが消える分だけ軽い) | presence.py:190-222。判定自体は既に全プール走査 |
| エンジン(active 比例) | 基準 | **+22.7%(平日)・平均 +18.4%** | §4.1 の在場比 |
| メモリ(live agents) | 316 GB | **388 GB(+72 GB)** | 勾配 1.2645 MB/agent(docs/plans/dayplan-engaged-plan.md:632 実測)× 在場 |
| L1 解析側 | 42.7 GB/10日 | **≈50.6 GB(+18.4%)** | DP-U3 §2-4 実測 × 平均在場比 |
| LLM 呼数 | step 予算 300 で頭打ち | ほぼ不変(予算制)。day_plan 系のみ active 比例 | conf/finals_observe.yaml・DP-U3 §2 |
| 段階 1〜2 の追加コスト | — | ほぼゼロ(整数演算の period 判定・乱数本数は減る) | :126 の draw が消える |

### 4.4 既存資産との整合

- P4 境界(§2.2)と同じ思想で閉じる: **境界機構を新設しない**。presence の `_eligible` が
  「個人の予定表」になるだけで、`present_for_day` の枠組み・PoolStore・resume 決定論はそのまま。
- `_days_match` の mon-sat 後退(:84)の解消は段階 1 と独立に可能(名簿の意図どおり土曜 +44,486 人)。
- tier_quota(quota_by_ratio)は cap 廃止と同時に自然退役(cap ≥ Σ eligible なら全層まるごと :142-143)。

---

## §5 リスク

1. **計算資源 +22.7%(平日)**: メモリ推定 388 GB(§4.3)は単ノード RAM の既存懸念(DP-U3 §2-4 の
   RSS 88-110 GB は別項目=PoolStore/解析側)をさらに押す。8/15-16 の実測なしに cap 廃止を本選投入しない。
   L1 も +18% で `load_events` 全件展開の破綻リスクが増幅。
2. **縮退線の再設計が必要**: 現行の縮退は「present_cap 25万→10万→5万」(docs/spec.md:236)。cap を
   廃止すると この操作点が消える。文献整合の代替は `--fraction`(標本設計、§3.4)だが、プール再ビルドを
   伴い当日縮退には向かない。**非常弁としての cap は残す(既定 ∞)**が現実解 — ただし「使えば原理から
   一時離脱」であることを conf に明記する規律が要る。
3. **較正の壊れ方が変わる**: cap は名簿の較正誤差を吸収する安全弁でもあった(資格者がいくら多くても
   250k で頭打ち)。廃止後は**名簿の誤差が在場に直結**する: (i) プール再ビルドで資格者数が跳ねれば在場も
   跳ねる(第108 で週末が一晩で 2.15 倍になった実例)。(ii) 週末 0.59 は cap 廃止では直らず、
   段階 2 の目的較正を先にやらないと「平日だけ現実的な街」になる。(iii) mon-sat 修正(+44,486 人)や
   夜勤 all 層の扱いなど**一つ直すたびに総在場が万人単位で動く** → 変更は 1 レバーずつ・jinryu 曲線との
   照合を毎回挟む。
4. **R1(k 非交絡)・resume 決定論の維持**: 段階 1 は乱数が減る方向で安全。段階 2 の共変量(天候・
   イベント)は day の純関数である限り「同 seed・全 k 条件で同じ人が同じ日に present」を保つが、
   天候を実測フィード等の**run 外部入力**に切り替えた瞬間に共通乱数性が壊れる。共変量の入力源は
   generated(seed 決定論)に限定する。
5. **二重計上と観測解釈**: 天候感応は envfeedback・夜間経済・H1(WBGT)と重なる領域があり、
   同じ現象に二重の係数を掛けない棚卸しが要る。また cap 切りの「日替わりの顔ぶれ」が消えると
   在場集合の分散が減る=「日常が回る」観測には利点だが、L4 の総在場が確率的に揺れる幅(±√np ≈ ±160 人/日)
   まで消えるのは段階 1 の決定論化の副作用(phase が散っていれば日次総数はほぼ一定)。現実の日次揺らぎを
   再現したければ、それは乱数でなく**天候・イベント共変量**(段階 2)で入れるのが原理適合の道。

---

*本文書はリサーチのみ。src・conf・データは無変更(§2.3 の集計は読み取りのみ)。*
