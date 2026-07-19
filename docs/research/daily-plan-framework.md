# 一日計画フレームワーク — 活動プリミティブを用意すべきか(リサーチ+設計案)

- 作成: 2026-07-20 / 担当: Opus 4.8(リサーチ) / 種別: **調査・設計のみ**(src非編集・実LLM実行なし・commit なし)
- 問い(ユーザー): 「エージェントの一日の計画に**書ける活動の種類**をフレームワークとして用意しておくべきか。もしそうなら、その実装に必要なリサーチと計画をしてほしい。」
- 位置づけ: [`docs/plans/w2-execution-plan.md`](../plans/w2-execution-plan.md) §1「全員思考」モデルの **P2パッケージ(計画→スケジュール コンパイラ)** の実装前調査。並行設計中の「確率的実行」(逸脱・寄り道・偶発遭遇)への接続も扱う。
- 出典方針: 公式ドキュメント/一次論文/政府統計を優先。既存の社内調査([`constrained-decoding.md`](constrained-decoding.md) / [`token-budgets.md`](token-budgets.md) / [`agent-freedom-audit.md`](agent-freedom-audit.md))と重複する部分は**差分のみ**を書き相互参照する。未確認は「未確認」と明記(捏造禁止)。
- 鉄則の継承: R1(新機能=新stream・既定OFFでゴールデンL1バイト一致・呼数k非依存・no-fingerprint)/ 決定論 / mock ≤24step スモーク検証。

---

## 0. 結論(先に4行)

1. **「用意すべき」— ただし "語彙を固定する枠" ではなく "型(スキーマ)を定め、活動タイプ語彙は差し替え可能な設定値として持つ" 形で。** 現行の 8 種 what 語彙(`work/meal/shop/leisure/park/walk/home/visit`)は**プロンプト+mock+ゴールデンに直結した暗黙のフレームワーク**として既に存在する。問いの本質は「これを明示的な**活動プリミティブのスキーマ**へ昇格し、全員思考(25万人)の計画→スケジュール コンパイラが機械実行できる形にすべきか」であり、答えは Yes。
2. **枠の設計軸は活動ベース交通需要モデル(ActivitySim/MATSim 系)の合意=`mandatory / maintenance / discretionary` の3分類**と、それに直交する**柔軟性属性(固定予定 vs 裁量活動)**。この柔軟性属性が、並行設計中の**確率的実行の逸脱確率の入力**になる(mandatory=逸脱しにくい / discretionary=寄り道・スキップされやすい)。
3. **自由記述の `intent` フィールドを必ず残す**。文献(Let Me Speak Freely 論争の落とし所=「封筒は強制・中身は自由」)と社内 [`agent-freedom-audit.md`](agent-freedom-audit.md) の両方が、**語彙を enum で固く縛ると思考の自由度=創発余地を殺す**と警告する。枠は「時間窓・場所意図・所要・柔軟性」を構造化しつつ、活動の意味は自由文 `intent` に開いておく。
4. **較正の当て先が確定した**: 総務省 社会生活基本調査の**時間帯別行動者率(15分×96区分・機械可読)**を正解分布とし、シミュの時刻別活動分布を分布距離で照合する設計が `calibrate_report.py` にそのまま乗る(§3.4)。

---

# 第I部 リサーチ

## 1a. 活動分類の標準(activity-based travel demand models)

### 核となる合意: mandatory / maintenance / discretionary の3分類 + アンカー-充填構造

4つの代表モデル(ActivitySim / MATSim / CEMDAP / TASHA)は、一日の活動を**目的**で3群に分け、**固定アンカーを先に置き、その周囲の残り時間窓に柔軟な活動を詰める**という同一の骨格を共有する。分類軸は「スケジュール上の固定性(fixity-flexibility)」:

| 分類 | 別名 | メンバー | 空間-時間の性質 |
|---|---|---|---|
| **Mandatory(義務的)** | subsistence / 一次 / 固定 | 仕事・就学・大学 | 場所も時刻も固定 = 一日の**アンカー** |
| **Maintenance(維持的)** | secondary | 買い物・送迎(escort)・用足し(personal business) | 世帯維持。半固定 |
| **Discretionary(裁量的)** | leisure | 社交・娯楽・外食・訪問・運動 | 個人選好。**最も柔軟・スキップ/順序入替可** |

時間地理学の言葉では、**home / work / school が「プリズムのアンカー」**で、それ以外(維持・余暇・買い物)は「アンカー間の時間予算の中に配置される柔軟な活動」として扱われる([固定 vs 柔軟活動とアンカー, PMC9761654](https://pmc.ncbi.nlm.nih.gov/articles/PMC9761654/))。この**fixity-flexibility 二分法**が、本シミュの計画コンパイラと確率的実行に共通する最重要の設計概念。

### 各モデルの活動語彙と柔軟性の表現

- **ActivitySim**(tour ベース)。**CDAP(Coordinated Daily Activity Pattern)** が各人へ 3 パターン(**Mandatory / Non-Mandatory / Home**)を世帯協調で割当([CDAP docs](https://activitysim.github.io/activitysim/develop/dev-guide/components/cdap.html))。非義務 tour 目的は **6種**: `escort, shopping, othmaint, othdiscr, eatout, social`([non-mandatory tour freq](https://activitysim.github.io/activitysim/develop/dev-guide/components/non_mandatory_tour_frequency.html))。うち Maintenance = {escort, shopping, othmaint}、Discretionary = {eatout, social, othdiscr}。**義務 tour を先にスケジュールし、非義務は残りの時間窓に詰める**(「discretionary より work/school を優先」)。時間は**30分刻み**で、tour は `tdd`(開始30分区分, 終了30分区分)を選び、person 単位の**空きスロット配列**で重複を禁じる。
- **MATSim**。plan = `activity → leg → activity …` の厳密交替。活動タイプは**ユーザー定義文字列**(標準 home/work/leisure/shopping/education)。各タイプに `priority / typicalDuration / openingTime / latestStartTime / earliestEndTime / closingTime / minimalDuration`。**Charypar-Nagel スコア**で活動効用は所要の対数(`S_dur = β_perf · t_typ · ln(t_perf/t_0)`)、時刻ずれ(待ち/遅刻/早退/最小未満)にペナルティ。→ **柔軟性=ペナルティ係数の急峻さ+窓の狭さ+priority で連続的に表現**([Charypar-Nagel scoring class](https://www.matsim.org/doxygen/classorg_1_1matsim_1_1deprecated_1_1scoring_1_1functions_1_1_charypar_nagel_activity_scoring.html))。
- **CEMDAP**(Bhat ら)。stop → tour → pattern の3層。**明示的な優先順位順**: `work → school → escort → personal business → shopping → meal → social/rec`([CEMDAP, TRR 1894-07](https://journals.sagepub.com/doi/10.3141/1894-07))。この順序自体が柔軟性ランク(義務を先に確約、裁量を最後に交渉)。成人は約11活動タイプ。
- **TASHA / ILUTE**。**project(共通目的の活動コンテナ)**で組織。**ボトムアップ生成→挿入時に shift/shorten で重複解消**する規則ベース。work/school を相対的固定アンカーとし、裁量の "other"/shopping がスケジュール衝突を吸収([TASHA, TRR 1831-13](https://journals.sagepub.com/doi/10.3141/1831-13))。

### 柔軟性の2つの表現方式(本シミュは両方を採る)

1. **離散: 優先順位/挿入順**(ActivitySim・CEMDAP・TASHA)。柔軟性 = 優先順位順の位置 + 「動かせる/縮められる/落とせる」資格。
2. **連続: 活動ごとのペナルティ係数**(MATSim・Pougala/OASIS)。最新研究は各活動に **4係数 β_early, β_late(時刻), β_short, β_long(所要)** を推定し、「**昼食は最高ペナルティ(硬い)、二次活動は低ペナルティで逸脱しやすい(柔軟)**」を実証([Pougala 柔軟性推定, PMC9569421](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9569421/))。この "活動ごとの数値 flexibility フィールド" は、本シミュの**確率的実行の逸脱確率の直接の入力形**として最も綺麗なテンプレート。

### 時間窓の失敗モード(コンパイラ設計に直結)

義務 tour が最後の時間区分を奪うと、後続 tour に可行窓がなくなり全代替が -999(不成立)になる([ActivitySim #121](https://github.com/activitysim/activitysim/issues/121))。→ **計画コンパイラは「窓を使い切って裁量活動が入らない」ケースを正常系として扱う**(=詰められなければ落とす。§3.2)。

### シフト労働者の非標準性(→ §1d)

HTS はシフト労働の早朝・深夜始業を過小評価する(早朝始業 HTS 7.3% vs GPS 18.5%)([Beyond 9-to-5, arXiv:2507.19510](https://arxiv.org/html/2507.19510))。渋谷は非標準勤務が濃く、**mandatory アンカーの始業を 9-to-5 に固定してはならない**。日本の合成人流の先行例 Pseudo-PFLOW([arXiv:2205.00657](https://arxiv.org/pdf/2205.00657))は §3.4 較正の姉妹参照。

---

## 1b. 総務省 社会生活基本調査 — 計画の現実性の較正指標として

**結論: 較正の当て先として第一級。** 粒度(15分刻み)・層別(曜日/性/年齢/ライフステージ)・機械可読性(Excel/CSV/e-Stat API)のいずれも、シミュの時刻別活動分布を照合するのに理想的な形式で揃っている。

### 行動分類: 3区分 + 20分類(調査票A・プリコード方式)

生活時間は **15分刻み**で記録され、行動は 3 区分・計 20 分類に整理される([茨城県:令和3年社会生活基本調査 用語と分類](https://www.pref.ibaraki.jp/kikaku/tokei/fukyu/tokei/betsu/syakai/syakaichor3/furoku.html)):

- **1次活動(生理的に必要)= 3**: 睡眠 / 身の回りの用事 / 食事
- **2次活動(社会生活上の義務的)= 7**: 通勤・通学 / 仕事 / 学業 / 家事 / 介護・看護 / 育児 / 買い物
- **3次活動(自由時間活動)= 10**: 移動(通勤・通学を除く)/ テレビ・ラジオ・新聞・雑誌 / 休養・くつろぎ / 学習・自己啓発・訓練(学業以外)/ 趣味・娯楽 / スポーツ / ボランティア活動・社会参加活動 / 交際・付き合い / 受診・療養 / その他

調査票B(アフターコード方式・2001年〜)はこれをさらに細分化した**詳細行動分類**を持ち、**同時行動(ながら行動)**も把握する([統計センター:社会生活基本調査 匿名データ](https://www.nstac.go.jp/use/archives/anonymity/shakai/)、[JILPT](https://www.jil.go.jp/kokunai/statistics/shozai/html/s03.html))。

### ABM 3分類との対応(§1a と接続)

| 社会生活基本調査 | ABM 分類 |
|---|---|
| 1次活動(睡眠・身の回り・食事) | 在宅アンカー(直接対応なし。外食は一部 discretionary へ) |
| 2次活動 | **Mandatory**(仕事・学業・通勤通学)+ **Maintenance**(家事・買い物・介護・育児)+ 受診療養は maintenance |
| 3次活動 | **Discretionary**(趣味・娯楽・スポーツ・交際・休養・視聴・学習) |

軸は「生理/義務/自由」対「スケジュール固定性」で完全一致ではないが、実用上の対応は妥当。**本シミュの活動プリミティブ語彙をこの 20 分類へマッピングする対応表**を整備すれば較正が成立する(§3.4)。

### 時間帯別行動者率は 15 分粒度で公開・機械可読

- **e-Stat 表6-2**「曜日,男女,ライフステージ,行動の種類,時刻区分別行動者率(10歳以上)－全国」([statdisp_id=0003457693](https://www.e-stat.go.jp/stat-search/database?page=1&statdisp_id=0003457693))。時刻区分は `0:00〜0:15` から `23:45〜24:00` まで **96 区分(24時間フルカバー)**、行動 約21区分、曜日(平日/土/日)・性・ライフステージ別。値=行動者率(%)。
- **表10**「時間帯,行動の種類別主行動の行動者率－平日,15歳以上」は Excel でダウンロード可([stat_infid=000032261706](https://www.e-stat.go.jp/stat-search/files?stat_infid=000032261706))。
- 「その時刻にその活動をしている人の割合」= 本シミュの**瞬時活動状態の集計と定義が一致**。KL/EMD による分布照合にそのまま乗る。

### 周期・最新性

昭和51年(1976)以降**5年ごと**。最新確定 = **令和3年(2021)調査(10回目)**。次回 = **令和8年(2026)調査(11回目・50周年)**、結果公表は概ね 2027–2028 見込み([令和3年概要](https://www.stat.go.jp/data/shakai/2021/gaiyou.html)、[令和8年概要](https://www.stat.go.jp/data/shakai/2026/gaiyou.html))。現時点で使うのは**令和3年**。COVID 禍(2021は緊急事態宣言下)の年次固有バイアスに留意し、令和3+平成28 の併用が頑健。

### 較正指標としての制約(2点)

1. **空間解像度は都道府県止まり** — 渋谷区/エリア単位の時間帯別行動者率は出ない。渋谷ローカル補正はパーソントリップ調査等の別ソース併用が望ましい。
2. **母集団は居住者(10歳以上)** — 昼間流入する**来街者・観光客は対象外**。渋谷は昼間人口が大きいので、居住者ベンチマークと来街者行動を分けて扱う([realism-first-scale の来街者=全員エージェント方針と整合])。

---

## 1c. Generative Agents 系の計画表現 + 構造化出力(vLLM guided decoding)

### Generative Agents(Park+ 2023): トップダウン + 再帰的詳細化

計画は**トップダウンで大枠を作り、再帰的に細かくする**([Generative Agents, arXiv:2304.03442](https://arxiv.org/abs/2304.03442))。

- **第1層(大枠)**: エージェントの要約記述(名前・特性・直近経験の要約)+前日の要約を与え、**5〜8 個の日課アジェンダ**を生成(例: 「8時起床→10時に大学で授業→13〜17時に作曲→…→23時就寝」)。これを記憶ストリームに保存。
- **第2層(1時間チャンク)**: 各大枠項目を1時間単位の行動へ分解。
- **第3層(5〜15分)**: 各時間をさらに 5〜15 分刻みへ再帰分解。この再帰の深さは「望む粒度に合わせて調整できる」設計選択。
- **計画の格納形式**: 記憶ストリーム上の**自然文レコードだが、各エントリは実質 (場所, 開始時刻, 所要) の3フィールドを持つオブジェクト**(例: 「2023-02-12 9時から180分間、Oak Hill College 寮の机で、論文のために読んでメモを取る」)。**厳格な JSON ではなく、スケジューリング用メタデータ付きの NL**。
- **日中の反応・再計画**: 行動ループの各 step で知覚→記憶。顕著な観測は「反応すべきか、するなら何を?」という反応判断プロンプトを起動し、反応する場合は**「反応が起きた時刻から、既存の計画を再生成する」**(=残りスケジュールを現在時刻から部分再生成。全日やり直しではない)。

→ **本シミュの現行実装(§2)は GA の第1層のみ(5個の大枠)に相当**し、第2〜3層の再帰詳細化を持たない。GA の (場所, 開始時刻, 所要) 3フィールドは、本シミュが guided-JSON 化する際の自然な構造化ターゲットと一致する(§3.1)。

### 大規模系の計画表現の分岐

| 系統 | 計画の持ち方 | スケール手法 |
|---|---|---|
| **GA / AgentSociety / Concordia / GATSim** | NL アジェンダ + (場所,開始,所要)。イベント駆動で現在時刻から再生成 | AgentSociety は Need→Plan→行動列、10k+体を**エージェントグループ(1プロセス多数体)+Ray+MQTT**で([arXiv:2502.08691](https://arxiv.org/abs/2502.08691)) |
| **OASIS** | **計画を持たない**。各体に**24次元の時間帯別活動確率ベクトル**(実ユーザー行動から学習)。Time Engine が確率で活性化。行動空間=21 離散行動。1体1M体まで([arXiv:2411.11581](https://arxiv.org/abs/2411.11581)) | 分散非同期推論 |

**含意**: 「全員思考」で 25 万人を回す本シミュにとって、**OASIS の "計画=時間帯別活性化確率" は §3.4 の較正(社会生活基本調査の時間帯別行動者率)と同じ形**であり、"背景の薄い人には確率ベクトル、渦中の人には GA 型の詳細計画" という LOD の当て所を示唆する。ただしユーザー方針は「全員が自分の計画を生きる」なので、確率ベクトルは**フォールバック/背景の下限**として位置づけ、主軸は GA 型の本人計画とする。

### guided decoding のスループット(vLLM/xgrammar)— 本選環境の実測材料

社内 [`constrained-decoding.md`](constrained-decoding.md) の結論(既定 `format:json` は現状維持・schema モードは単一行動狙い撃ちのみ・think 境界を尊重)を前提に、**計画の schema 化に効く新しい定量値**を足す:

- **xgrammar の per-token マスク < 40 マイクロ秒**= 定常デコード(TPOT)への上乗せはほぼゼロ([XGrammar, arXiv:2411.15100](https://arxiv.org/abs/2411.15100))。文法エンジン単体で JSON schema 3x・JSON grammar 100x、E2E 出力トークンレート最大 80x。
- **コストは1回きりの文法コンパイル(≈20〜50ms、TTFT に乗る)**。**同一 schema を使い回すとキャッシュが効く**(vLLM V1 は init を非ブロッキング化)。→ **全員の計画が同一 schema = xgrammar のキャッシュが最も効く使い方**(constrained-decoding.md §3.2 と同じ結論を計画側でも再確認)。
- **vLLM 固有の注意**: バッチ≥8 でマスク計算が同期的にスループットを落とす報告([SqueezeBits](https://blog.squeezebits.com/guided-decoding-performance-vllm-sglang))。全員思考のバッチ発行(P2)ではここが効くので、schema 再利用と V1 エンジンを前提にする。
- **jump-forward decoding**: 文法上次トークンが確定するとき LLM forward をスキップ=構造化が**素の生成より速く**なりうる。
- **ベストプラクティス**: schema は浅く・境界つき(配列長/文字列長を無制限にしない)、schema をプロンプトにも書く(構造化は形を保証するが中身は保証しない)、whitespace を制御。**具体トークン/秒は本選実機で `scripts/bench.py` 実測**(ops 方針=未測定値は書かない)。

---

## 1d. 役割者の勤務シフト表現

### 現行実装の把握(組織台帳 × agent 勤務窓)

- **組織台帳** `data/organizations_shibuya.json`: companies は `size.employees` / `roles` / `generalist_roles` / `workplace_poi` を持つが、**フルタイム役割のシフトパターンは持たない**。schools は `timetable`(`period_min` / `periods_per_day` / `start`)を持つ。
- **勤務窓は agent 側**: `work_start_min` / `work_end_min`(本業)と `part_time`(`{days, start_min, end_min, building, node}`= 曜日つきシフト)が個体属性として実行を駆動する(`cognition/routine.py::in_work_window` / `in_part_time_window`)。
- つまり**シフトの「型」は既にある**(本業窓 + 曜日つきバイト窓)が、**組織台帳が役割別シフトパターンを供給していない**(agent 生成時に persona/economy から窓が決まる)。

### 文献・実務の知見

- 勤務スケジューリング(rostering)は医療・小売・接客・製造で確立した領域。**ローテーション勤務(rotating shift)**= 各エージェントに日ごとのシフトを割り当て、週/月単位で交替させるのが接客業の標準([shift scheduling 実務](https://optimoroute.com/shift-work-scheduling/))。
- §1a のとおり HTS はシフト労働の早朝・深夜始業を過小評価する([Beyond 9-to-5, arXiv:2507.19510](https://arxiv.org/html/2507.19510))。**渋谷再現では非標準始業を明示的に注入する**必要がある。

### 設計含意(§3 の役割スロットへ)

役割者(店員・駅員・運転士・配信者)の勤務は**「シフト = mandatory アンカーの供給源」**として計画コンパイラの上流に置く:

- 組織台帳の役割に **shift パターン**(例: `早番 06:00–15:00 / 遅番 14:00–23:00`、曜日巡回)を持たせ、配属時に agent の `work_start_min/end_min` を**そのシフトから決定論で導出**(現行の `commute_to_poi` seam と同型の拡張)。
- 計画コンパイラは「本人のシフト窓 = 固定 mandatory 予定」を最初に置き、**残りの時間窓に本人の裁量活動(LLM 計画)を詰める**。運転士・駅員は運行ダイヤ(既存 `transit` 機構)との整合が要る。
- **個人裁量との混合**: シフトは固定だが、休憩・退勤後の裁量活動は本人の LLM 計画に開く。配信者のように「勤務=裁量活動そのもの」(配信を始める/やめる)の職種は、mandatory 窓を持たず discretionary 側で表現する。

---

## 1e. 計画の失敗モード(LLM 構造化出力の破損・再試行・fallback)

25万人が毎朝 plan-JSON を出すと、**1% の破損でも 2,500 件/朝**。文献の合意は「**構造化デコードで構文を保証し、トークンを余裕を持って確保し、LLM 再試行に頼らず安価な決定論フォールバック(修復+前日/既定計画)を持て**」。

### 破損率と「構文 vs 意味」

- 非制約 JSON は**現場で ~5〜15% 失敗**([tensoria](https://tensoria.fr/en/blog/structured-outputs-llm-production))。良モデル×単純 schema では < 2% だが、**複雑/入れ子 schema では非制約の schema 適合が激減**(JSONSchemaBench の "GitHub Hard" で非制約カバレッジ **13%**)([JSONSchemaBench, arXiv:2501.10868](https://arxiv.org/abs/2501.10868))。古典的破損は**JSON の周りに散文が付く chatty 出力**。**構文は良くても値が間違う**方が大きく難しい問題(値正解率は構文適合率より 15〜25pt 低い)。
- 本シミュの `deliberate.parse_action` の**寛容正規化**(別名キー吸収 `text/content/message`・数値クリップ・`_loads_lenient` の末尾補完)は、まさにこの chatty/末尾切れに効く既存の防波堤。

### 構造化デコードは 100% ではない(残る穴)

制約デコードは**対応 schema について構文適合を ~100%** にする(OpenAI Structured Outputs は 100% vs 素プロンプト <40%)が、次は保証しない([Aidan Cooper](https://www.aidancooper.co.uk/constrained-decoding/)):

1. **truncation**: max_tokens 到達で途中切れ。文法は**トークン数を強制できない**([TruncProof, arXiv:2605.13076](https://arxiv.org/pdf/2605.13076))。→ `finish_reason=="length"` を毎回検査(length を成功扱いしない)。
2. **refusal / 空**: 拒否・空応答は「403 扱い」(再試行しない)。
3. **engine が複雑 schema をコンパイルできず reject**(hard schema で XGrammar カバレッジ 28% など)。→ **schema は浅く保つ**。
4. **hallucinated free-text 値**: enum を文法に入れない限り自由文字列に幻覚カテゴリが入る。
5. **推論劣化**: 文法で最終回答だけ縛ると分布がずれ推論が落ちる。

### Let Me Speak Freely 論争の落とし所(スキーマ設計の指針)

「format 制約は推論を下げる」(Tam+ 2024: GSM8K 76.6%→49.25%)([arXiv:2408.02442](https://arxiv.org/abs/2408.02442))vs 「プロンプトを揃えれば構造化が勝つ」(dottxt)([Say What You Mean](https://blog.dottxt.ai/say-what-you-mean.html))。**和解**: **自由文の `reasoning`/`intent` フィールドを schema の *先頭* に置き、その後に構造化フィールド**を並べれば、Tam のペナルティを避けつつ構文保証を得る。→ **本シミュの活動プリミティブでも `intent`(自由文)を各項目の先頭に置く**(§3.1)。これは constrained-decoding.md §2.3「封筒は強制・中身は自由」と完全一致。

### 再試行・fallback の階段(安い順)

1. **決定論修復(LLM 呼ばない)**: `json_repair` 相当([json_repair](https://github.com/mangiucugna/json_repair))。**本シミュは `_loads_lenient` で実装済み** = 第1段は既にある。
2. **error 付き再プロンプト(LLM 1回)**: LangChain `OutputFixingParser` / Instructor `max_retries`。**上限 1〜2**(トークン×25万倍の増幅に注意)。
3. **transport backoff+jitter**: 429/5xx/timeout に指数バックオフ+ジッタ(サンダリングハード回避)。schema エラーには使わない。
4. **error 分類**: transient(429/瞬断)は再試行 / persistent(拒否・破損・障害)は再試行せずフォールバック。
5. **graceful degradation**: 全再試行枯渇時は**既定値 or 前日計画を再利用**。日次計画エージェントの自然なフォールバックは「**昨日の計画の流用**」。
6. **冪等性**: (agent, day) 単位の冪等キーで二重計画を防ぐ。**本シミュは `plan_step/plan_day` で 1人1日1回を既に強制済み**。

→ **w2-plan §6 の「再試行1回→失敗時は前日計画を流用し翌朝再計画(恒久ルール化しない)」は、この文献合意と一致**する。現行実装は「破損→`day_plan=[]`→routine フォールバック」で、**前日計画の流用は未実装**(§3.2 で足す)。

---

# 第II部 現行実装の把握

## 2. 現状の計画表現 — 既に "暗黙のフレームワーク" が存在する

問いの「フレームワークを用意すべきか」は、正確には**「既にある暗黙の枠を明示スキーマへ昇格すべきか」**。現状を棚卸しする。

### 2.1 計画スキーマ(`cognition/planning.py`)

起床(来街者は帰還)直後の step に 1 回、`make_plan` が LLM で当日計画を生成する(`_phase_planning`)。既定 **ON**(`planning.enabled: true`)。出力スキーマ:

```
{"action":"plan","items":[{"when":"朝|昼|午後|夕方|夜",
  "what":"work|meal|shop|leisure|park|walk|home|visit","place":"任意"}, ...]}
```

- **when(時間帯)= 5 バンド**(朝/昼/午後/夕方/夜)。`routine._time_band` が現在時刻をバンドへ写す(朝5-11/昼11-14/午後14-17/夕方17-19/夜else)。
- **what(内容)= 8 語彙**: `work, meal, shop, leisure, park, walk, home, visit`。これが**現行の活動タイプ・フレームワーク**(プロンプト `_WHATS`・mock・ゴールデンに直結)。
- **place = 場所名**(自由文字列。POI 名の部分一致で解決)。
- `_normalize` が各項目へ `done:False` を付け、最大 5 件(`max_items`)に丸める。
- **自由記述の intent フィールドは無い**(what は 8 enum に閉じ、place のみ自由)。→ §3.1 の主要な改善点。

### 2.2 計画→行動の消化(`cognition/routine.py`)

`_plan_move` が「現在バンドに一致する未消化(`done=False`)項目」を1つ取り、`_resolve_plan_dest` で行き先ノードを解いて `move_to` を組む:

- `_PLAN_CAT`: `meal→food, shop→shop, leisure→leisure, park→leisure, work→office, meetup→landmark, visit→landmark`(`home→home_node` は特別扱い、`walk` は非対応=EPR へ)。
- 解決順: **place の POI 名部分一致 → what カテゴリの POI サンプル → EPR の行き先**。有料カテゴリは残高で除外、閉店中 POI は除外。
- **1項目は1回だけ消化**(解決可否に関わらず `done=True`)。計画は routine 行き先の**「土台」であって強制ではない**([agent-freedom-audit.md](agent-freedom-audit.md) §2.2「非拘束」)。
- day_plan が空なら**乱数を一切引かず None**(既定挙動の再現性=R1)。

### 2.3 失敗時フォールバック(現行)

`parse_action` が None(破損)または非 plan なら `day_plan=[]` → **従来 routine(EPR等)へフォールバック**。`day_plan` イベントは**必ず1件出す**(1人1日1回の観測・R1監査)。**前日計画の流用は無い**(翌朝 `make_plan` が上書き)。`_loads_lenient` が末尾切れ JSON を救済(§1e 第1段に相当)。`plan_max_tokens` seam あり(既定 0=`max_tokens` 共用。[token-budgets.md](token-budgets.md) は plan が 320 天井に当たるため 384〜512 を推奨)。

### 2.4 スケジュール帳との関係(`schedule.py`)

会話由来の予定(決定論パーサで抽出)を `agent.schedule` に記入し、**当日分を `today_line` として計画プロンプトに1行注入**(`_today_schedule_line`、schedule 有効時のみ)。予定 dict は `{day, when, what, place, with, src_step}`。**LLM 呼び出しを増やさない**(R1)。これは「未来の約束→当日計画への反映」の既存経路で、フレームワーク化する計画スキーマと**同じ when/what/place 語彙**を使うべき接合点。

### 2.5 組織台帳・勤務窓(§1d と接続)

`work_start_min/end_min`(本業)+ `part_time{days,start_min,end_min}`(曜日つきシフト)が agent 側の**固定 mandatory アンカー**。組織台帳 `roles` はフルタイムのシフトパターンを供給していない(schools のみ `timetable`)。→ **計画コンパイラは既存の勤務窓を mandatory 予定として先に置く**べき(§3.2)。

### 2.6 現行 vs フレームワーク化で埋まるギャップ

| 観点 | 現行 | フレームワーク化で | ABM 対応(§1a) |
|---|---|---|---|
| 活動タイプ | 8 enum(what) | 3分類(mandatory/maintenance/discretionary)+語彙は設定値・**自由文 intent** | ActivitySim 目的語彙 |
| 時間 | 5 バンドのみ | バンド維持 + 任意の start/所要(時間窓) | MATSim typicalDuration/latestStart |
| 柔軟性 | 無し(全項目一律「土台」) | **fixed/flexible フラグ**(=逸脱確率の入力) | Pougala β係数 / CEMDAP 優先順位 |
| 同伴者 | 無し(schedule の with のみ) | 任意 with | ActivitySim escort/joint |
| 失敗時代替 | routine へ落ちるだけ | **前日計画流用 + 項目ごとの fallback** | — |
| コンパイル | バンド一致で逐次消化 | **アンカー先置き→残り窓に充填**の明示コンパイル | 全モデル共通 |

---

# 第III部 計画 —「フレームワークを用意すべきか」への答えと設計

## 3.0 結論: 用意すべき。ただし「語彙を固く縛る枠」ではなく「型を定め、語彙は差し替え可能・intent は自由」

**Yes**。理由:

1. **全員思考(25万人)の計画→スケジュール コンパイラ(P2 の中核)は、機械実行できる計画表現を必須とする**。現行の「バンド一致で逐次消化」は最小版で、時間窓・柔軟性・同伴者・失敗代替を持たない。w2-plan §1 が言う「機械実行可能な日課スケジュールにコンパイル」を成立させるには、計画項目を**構造化プリミティブ**へ昇格する必要がある。
2. **ABM 4モデルが完全収束した設計(3分類+アンカー先置き+残り窓充填)が既製の正解**として存在する(§1a)。車輪の再発明は不要。
3. **確率的実行(並行設計中)は "逸脱可否" の入力を計画側に要求する**。柔軟性属性を計画プリミティブに持たせるのが唯一の自然な置き場(§3.3)。
4. **較正の当て先(社会生活基本調査の時間帯別行動者率)が、活動を分類ラベル付きで持つことを要求する**(§3.4)。

**ただし枠のかけ方に3つの鉄則**(文献+社内監査の合意):

- **A. intent は自由文で残す**。what を enum で固く縛ると思考の自由度=創発余地を殺す([agent-freedom-audit.md](agent-freedom-audit.md):「語彙を狭めるほど creativity が落ちる」/ §1e:自由文 reasoning を先頭に置くと推論が落ちない)。**枠は "時間窓・分類・柔軟性・場所意図" を構造化し、"何を・なぜ" は自由文 `intent` に開く**。
- **B. 語彙は基盤に焼かず設定値(EnvPack/config)にする**。地名リテラル除去(devlog Entry 直下の EnvPack 化)と同じ思想。活動タイプ語彙は街ごとに差し替え可能に。
- **C. 既定 OFF で現行と完全一致**。フレームワークは新 stream・新 config ブロックとして足し、OFF 時は現行 8-what・バンド消化のまま(ゴールデン L1 バイト一致)。mock の `whats` 配列(golden 依存)を**変えない**。

## 3.1 活動プリミティブのスキーマ設計案

現行 `{when, what, place, done}` を拡張した**活動プリミティブ**。**`intent` を各項目の先頭**に置く(§1e の Tam ペナルティ回避)。すべて任意フィールドは「無ければ現行相当にデグレード」する後方互換設計。

```jsonc
{"action":"plan","items":[
  {
    "intent":  "自由文(先頭・必須) — 何をなぜしたいか。例: 授業のあと友達とセンター街で買い物",
    "cat":     "mandatory|maintenance|discretionary",   // 3分類(§1a)。任意=what から既定導出
    "what":    "work|study|meal|shop|leisure|...",       // 活動タイプ語彙(EnvPack 差し替え可)
    "place":   "場所名(任意・自由文字列。現行と同じ POI 部分一致解決)",
    "when":    "朝|昼|午後|夕方|夜",                       // 現行バンド(後方互換の主キー)
    "start":   "HH:MM(任意) — あれば時刻窓、無ければ when バンド",
    "dur_min": 60,                                        // 標準所要(任意。既定=カテゴリ別定数)
    "flex":    "fixed|flexible",                          // 柔軟性(任意。cat から既定導出)
    "with":    ["同伴者(任意) — 相手の呼び名 or 役割"],
    "alt":     "この予定が不可なら代わりに何をするか(任意・自由文 or what)"
  }, ...]}
```

設計判断:

- **`cat`(3分類)は柔軟性・優先度・較正ラベルの土台**。LLM に明示させても良いし、`what`→`cat` の決定論マップ(既存 `_PLAN_CAT` の拡張)で導出しても良い。**mandatory は勤務窓(§2.5)から自動生成し LLM 計画に混ぜない**(=LLM は裁量活動を主に計画)。
- **`flex` は 2値で開始**(fixed/flexible)。将来 Pougala 型の連続 4 係数(β_early/late/short/long)へ拡張可能だが、**まず 2値で確率的実行に接続**(§3.3)。`cat` から既定導出: mandatory→fixed, maintenance→中間, discretionary→flexible。
- **`when` を後方互換の主キーに残す**。`start`/`dur_min` は任意の上乗せ(MATSim の時間窓相当)。OFF or 省略時は現行のバンド消化と1バイト一致。
- **`what` 語彙**は現行 8 種を含む上位集合を EnvPack が供給(例: `study`(学業)・`personal`(用足し)・`escort`(送迎)を追加)。ActivitySim の目的語彙(§1a)を日本語生活行動に翻訳。**schema は浅く・enum は短く**(§1c ベストプラクティス)。
- **`alt`(失敗時代替)**は項目単位のフォールバック(§3.2 の "詰められなければ落とす" を LLM 意図で上書き可能に)。

**guided_json への載せ方**: constrained-decoding.md §5.2 の第2段(単一 schema 狙い撃ち)として、**plan だけ**に guided_json/xgrammar を適用する候補。`intent` は自由文字列フィールド(縛らない)。**全員が同一 plan schema = xgrammar キャッシュが最も効く**(§1c)。ただし既定は現行 `format:json`(構文のみ)維持、schema 強制は opt-in(think 境界は plan=think:False なので抵触しない)。

## 3.2 計画コンパイラの契約(LLM 出力 → スケジュール → エンジン実行)

**入力**: 上記 plan-JSON。**出力**: 時刻順に整列した実行可能スケジュール(現行 `day_plan` の拡張)。**契約**(ABM のアンカー先置き+残り窓充填を踏襲):

1. **正規化**: `_normalize` を拡張。各項目に既定を補完(`cat`←`what`、`flex`←`cat`、`dur_min`←カテゴリ定数)。`intent` 必須・他は任意。上限 `max_items`。
2. **mandatory アンカーの先置き**: 勤務窓(`work_start/end_min`・`part_time`・組織シフト §1d)を**固定予定**としてスケジュールの骨格に置く(LLM 計画とは別系統・既存 routine が実行)。
3. **裁量活動の窓充填**: LLM 由来の maintenance/discretionary 項目を、アンカーの**残り時間窓**へバンド/時刻順に配置。窓が埋まっていれば**その項目を落とす**(ActivitySim #121 の -999 を正常系として扱う=§1a)。衝突は flexible 側を shift/shorten(TASHA 流)。
4. **エンジン実行**: 現行 `_plan_move`(バンド一致で未消化項目を消化)を拡張し、`start`/`dur_min` があれば時刻窓で、無ければバンドで消化。**非拘束の "土台" 性は維持**(強制ルーティングにしない=自由度・確率的実行の余地)。
5. **失敗時(契約の核)**:
   - parse 破損 → `_loads_lenient`(決定論修復・既存)。
   - なお破損/空、または `finish_reason=="length"`(truncation 検知) → **再試行 1 回**(error 付き再プロンプト)。
   - 再試行も失敗 → **前日計画を流用**(`day_plan` を翌日へ持ち越し。現在は未実装=新設)。それも無ければ現行どおり `day_plan=[]`→routine。
   - **恒久ルール化はしない**(w2-plan §6: ルール専用層の再発防止)。**冪等性は `plan_step/plan_day` で担保済み**。
   - `day_plan` イベントは必ず1件(観測・R1監査)。fallback 種別(retry/prev_day/empty)を payload に記録し較正で可視化。

## 3.3 確率的実行との接続(柔軟性属性が逸脱確率の入力)

並行設計中の「確率的実行(逸脱・寄り道・偶発遭遇)」は、**計画プリミティブの `flex` を逸脱確率の入力に取る**:

- **fixed(mandatory=勤務・就学・約束)**: 逸脱確率 ≈ 0(寄り道しても遅刻ペナルティ的に戻る)。
- **flexible(discretionary)**: 逸脱・スキップ・順序入替が起きやすい(Pougala:二次活動は逸脱しやすい=§1a)。
- 実装: 確率的実行の**専用 stream**(例 `deviate`)が `flex` と個体差(SDT autonomy trait 等)を読み、逸脱抽選する。**新 stream・既定 OFF**(R1)。`flex` を持たない旧計画(OFF 時)は逸脱抽選を一切引かない=バイト一致。
- これにより「計画どおり実行」と「計画からの逸脱」が**単一の柔軟性軸で連続的に**制御でき、偶発遭遇(路上ライブに立ち止まる等)は flexible 項目の窓でのみ差し込まれる。将来 `flex` を連続 4 係数へ拡張すれば逸脱確率を活動ごとに精密化できる。

## 3.4 較正: 社会生活基本調査との時間帯別活動分布比較

**設計(`scripts/calibrate_report.py` への追加。sim⇄観測は疎結合・schema 非改変)**:

1. **対応表**: sim の活動ラベル(`cat`/`what`・routine の在圏状態)→ 社会生活基本調査の**20分類**へマッピング(§1b の対応表)。`build_panel.reconstruct_activity`(既存の活動復元)の出力カテゴリを 20 分類へ橋渡し。
2. **正解分布**: e-Stat 表6-2「時刻区分別行動者率(15分×96区分)」を `data/` に取り込み(平日/土/日・可能なら年齢層別)。**居住者ベンチマーク**として使い、来街者は別集計(§1b 制約2)。
3. **sim 側指標**: 各 step(=10分。96区分の15分とは resample で整合)で「その時刻に各活動をしている agent の割合」を集計 → **時刻×活動の行動者率行列**。calibrate_report は既に `ride_hist`(時間帯分布)や活動別分/日を出しており、**同じ枠に "時刻別行動者率" を1枚足す**。
4. **距離**: 既存の自作 `ks_stat`/`emd_1d`(scipy 非依存・決定論)を時刻別分布へ適用。加えて活動構成には **KL divergence** を追加候補(§1b が推奨)。REALITY バンド表に「時間帯別活動分布の乖離」を1指標追加。
5. **解釈**: 「12時台に食事している人の割合」等が統計と乖離すれば、計画の現実性(meal_prob・バンド定義・語彙マップ)の調律候補。**バンド外=即誤りではなく調律候補**(既存 calibrate の流儀)。

**注意**: 社会生活基本調査は「移動」を活動として計上する定義差(§1b Q2)があるので、sim の `move` 状態のマッピングに吸収層を1枚要する。空間解像度は都道府県止まり=渋谷ローカル補正はパーソントリップ調査で(§1b 制約1)。

## 3.5 実装フェーズ・対象ファイル・工数

**P2(全員思考)の一部として段階実装**。各段は独立に mock ≤24step スモークで検収。

| 段 | 内容 | 主対象ファイル | 工数 |
|---|---|---|---|
| **F1 スキーマ拡張** | plan-JSON に `intent/cat/flex/start/dur_min/with/alt` を任意追加。`_normalize` 拡張(既定補完で後方互換)。`what` 語彙を EnvPack 化 | `cognition/planning.py`・`cognition/deliberate.py`(parse plan 分岐)・`conf` envpack | 小〜中 |
| **F2 コンパイラ** | mandatory アンカー先置き→残り窓充填。`_plan_move` を時刻窓対応に拡張。`_PLAN_CAT` を 3分類へ拡張 | `cognition/routine.py`・`cognition/planning.py` | 中 |
| **F3 失敗時契約** | 再試行1回+`finish_reason` 検知+前日計画流用。fallback 種別を day_plan payload へ | `cognition/planning.py`・`engine/scheduler.py`・`observer/schema.py` | 小〜中 |
| **F4 確率的実行接続** | `flex`→逸脱確率(新 stream `deviate`・既定 OFF) | 確率的実行モジュール(別設計)・`cognition/routine.py` | 中(別設計に従属) |
| **F5 較正** | 社会生活基本調査 表6-2 取込+時刻別行動者率比較+KL/EMD | `scripts/calibrate_report.py`・`scripts/build_panel.py`・`data/` | 中 |
| **F6 guided_json** | plan schema を xgrammar に狙い撃ち(opt-in・本選 bench) | `llm/vllm.py`・`conf`・`scripts/bench.py` | 小(本選現物待ち) |

依存: F1→F2→F3。F4 は確率的実行の別設計に従属。F5 は F1(cat ラベル)完了後。F6 は本選環境。**まず F1〜F3 で "明示フレームワーク+堅牢な失敗処理" を成立させ、F4/F5 を順に載せる**のが最小リスク。

## 3.6 R1 ドクトリン整合

- **新 stream のみ**: 逸脱抽選は新 stream `deviate`(F4)。計画生成自体は既存の `plan/{agent.id}/{step}` rng を使い**新規 draw を増やさない**。
- **既定 OFF でゴールデン L1 バイト一致**: 拡張フィールドは任意で、未指定なら現行 `{when,what,place,done}` と同一挙動。**mock の `whats` 8語・バンド生成ロジックを変えない**(golden 依存)。新語彙/新スキーマは新 config フラグ(例 `planning.framework: false` 既定)配下に置き、OFF で現行 mock 出力=ゴールデン一致。
- **呼数 k 非依存**: 計画は全員毎朝1回のまま(`plan_step/plan_day`)。再試行1回は**破損時のみ**で k と無関係(破損は k 由来でない)。フレームワーク化で呼数式(2N+顕著性予算)は不変。[test_planning.py](../../tests/test_planning.py) の `test_day_plan_count_is_k_invariant` を維持。
- **no-fingerprint**: `cat`/`flex` の既定導出は `what`・勤務窓・職業由来のみで**性格特性を読まない**(組織台帳の no-fingerprint 契約と同型)。`flex` の個体差は確率的実行側で trait を読む(そこは既に freedom/SDT が扱う領域)。
- **検証**: 既存 `test_planning.py`(5本)を全 green 維持+ F1〜F3 に新規(スキーマ後方互換の L1一致・コンパイラのアンカー先置き・失敗時前日流用・finish_reason 検知)。mock ≤24step スモーク・実LLM フルランはしない([validation-runs-short])。

---

## 4. 出典

**活動分類(ABM・§1a)**
- ActivitySim CDAP(3日次パターン): https://activitysim.github.io/activitysim/develop/dev-guide/components/cdap.html
- ActivitySim 非義務 tour 目的(escort/shopping/othmaint/othdiscr/eatout/social): https://activitysim.github.io/activitysim/develop/dev-guide/components/non_mandatory_tour_frequency.html
- ActivitySim 義務 tour 目的(work/school): https://activitysim.github.io/activitysim/develop/dev-guide/components/mandatory_tour_frequency.html
- ActivitySim 時間窓 -999 失敗(#121): https://github.com/activitysim/activitysim/issues/121
- ARC ABM データ辞書(実装 tour purpose 語彙): https://cdn.atlantaregional.org/wp-content/uploads/abm-data-dictionary-feb-2022.pdf
- MATSim Charypar-Nagel 活動スコアリング: https://www.matsim.org/doxygen/classorg_1_1matsim_1_1deprecated_1_1scoring_1_1functions_1_1_charypar_nagel_activity_scoring.html
- MATSim ユーザーガイド(plan/activity 構造): https://svn.vsp.tu-berlin.de/repos/public-svn/publications/vspwp/2014/14-20/user-guide-0.6.0-2014-09-12.pdf
- CEMDAP(Bhat ら, TRR 1894-07・優先順位順): https://journals.sagepub.com/doi/10.3141/1894-07
- TASHA(Miller & Roorda, TRR 1831-13): https://journals.sagepub.com/doi/10.3141/1831-13
- 固定 vs 柔軟活動・プリズムアンカー: https://pmc.ncbi.nlm.nih.gov/articles/PMC9761654/
- 柔軟性推定(Pougala/OASIS・β_early/late/short/long): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9569421/
- Beyond 9-to-5(シフト労働過小評価, arXiv:2507.19510): https://arxiv.org/html/2507.19510
- Guidebook on ABM for Planners(Bhat, mandatory/maintenance/discretionary): http://caee.webhost.utexas.edu/prof/bhat/REPORTS/Guidebook_4080.pdf
- Pseudo-PFLOW(日本合成人流, arXiv:2205.00657): https://arxiv.org/pdf/2205.00657

**社会生活基本調査(§1b)**
- 統計局 令和3年 概要: https://www.stat.go.jp/data/shakai/2021/gaiyou.html / 結果: https://www.stat.go.jp/data/shakai/2021/kekka.html
- 統計局 令和8年(次回・2026): https://www.stat.go.jp/data/shakai/2026/gaiyou.html
- 茨城県 用語と分類(3区分・20分類の一覧): https://www.pref.ibaraki.jp/kikaku/tokei/fukyu/tokei/betsu/syakai/syakaichor3/furoku.html
- e-Stat 表6-2 時刻区分別行動者率(15分×96区分): https://www.e-stat.go.jp/stat-search/database?page=1&statdisp_id=0003457693
- e-Stat 表10 時間帯別行動者率(平日・Excel): https://www.e-stat.go.jp/stat-search/files?stat_infid=000032261706
- 統計センター 調査票A/B の説明: https://www.nstac.go.jp/use/archives/anonymity/shakai/
- JILPT 社会生活基本調査(分類解説): https://www.jil.go.jp/kokunai/statistics/shozai/html/s03.html

**Generative Agents 系・guided decoding(§1c)**
- Generative Agents(Park+ 2023): https://arxiv.org/abs/2304.03442 / HTML: https://ar5iv.labs.arxiv.org/html/2304.03442
- AgentSociety(Need→Plan→行動列, arXiv:2502.08691): https://arxiv.org/abs/2502.08691
- OASIS(時間帯別活性化確率・21行動, arXiv:2411.11581): https://arxiv.org/abs/2411.11581
- Concordia(entity-component・イベント駆動再計画): https://arxiv.org/abs/2312.03664
- XGrammar(per-token mask <40µs, arXiv:2411.15100): https://arxiv.org/abs/2411.15100
- vLLM structured decoding intro: https://blog.vllm.ai/2025/01/14/struct-decode-intro.html
- vLLM structured outputs docs: https://docs.vllm.ai/en/latest/features/structured_outputs/
- Red Hat / vLLM V1 structured outputs: https://developers.redhat.com/articles/2025/06/03/structured-outputs-vllm-guiding-ai-responses
- SqueezeBits guided decoding bench(vLLM vs SGLang, batch≥8): https://blog.squeezebits.com/guided-decoding-performance-vllm-sglang

**失敗モード・再試行(§1e)**
- Let Me Speak Freely?(Tam+ EMNLP2024, arXiv:2408.02442): https://arxiv.org/abs/2408.02442
- Say What You Mean(dottxt 反論): https://blog.dottxt.ai/say-what-you-mean.html
- JSONSchemaBench(arXiv:2501.10868): https://arxiv.org/abs/2501.10868
- Structured Output Benchmark(構文 vs 値, arXiv:2604.25359): https://arxiv.org/html/2604.25359v1
- TruncProof(トークン予算つき制約, arXiv:2605.13076): https://arxiv.org/pdf/2605.13076
- OpenAI Structured Outputs(finish_reason・refusal): https://developers.openai.com/api/docs/guides/structured-outputs
- 制約デコード解説(Aidan Cooper): https://www.aidancooper.co.uk/constrained-decoding/
- json_repair(決定論修復): https://github.com/mangiucugna/json_repair
- Instructor 再試行: https://python.useinstructor.com/learning/validation/retry_mechanisms/
- LangChain RetryOutputParser: https://api.python.langchain.com/en/latest/output_parsers/langchain.output_parsers.retry.RetryOutputParser.html

**社内(把握元・整合先)**
- [`docs/plans/w2-execution-plan.md`](../plans/w2-execution-plan.md) §1(全員思考)・§6(再試行1回→前日流用)
- [`docs/research/constrained-decoding.md`](constrained-decoding.md)(format ノブ・think 境界・xgrammar)
- [`docs/research/token-budgets.md`](token-budgets.md)(plan が 320 天井・384〜512 推奨)
- [`docs/research/agent-freedom-audit.md`](agent-freedom-audit.md)(自由度・plan は非拘束・OASIS 21行動)
- [`docs/design-candidates/schedule-book-spec.md`](../design-candidates/schedule-book-spec.md)(会話由来の予定→計画注入)
- `src/society/cognition/planning.py`・`routine.py`(現行の計画表現・消化)/ `schedule.py`(予定帳)/ `organizations.py`(役割・シフト)
- `scripts/calibrate_report.py`・`build_panel.py`(較正・活動復元)/ `tests/test_planning.py`(R1 契約テスト)


