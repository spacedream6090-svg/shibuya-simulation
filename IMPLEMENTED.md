# IMPLEMENTED — シミュレーションの概要と完了済み実装の全リスト

> 本ファイルは **実装済みのもの**だけを持つ。未実装・計画のみ・ユーザー判断待ちは → **[PENDING.md](PENDING.md)**。
> 索引と最終更新は → **[STATUS.md](STATUS.md)**。
> 最終更新: **2026-08-03** / テスト **2687 緑**(xdist フルゲート)。
> バッチ履歴の全文は [docs/log/devlog.md](docs/log/devlog.md)(圧縮版 [devlog-compressed.md](docs/log/devlog-compressed.md) Block #0〜#15)。

---

# 第1部 — シミュレーションの概要(全体を見て大事なことだけ)

## 1. これは何か

渋谷を舞台にした**大規模 LLM 人工社会シミュレーション**。無数の AI 住民が自律的に生活・会話・関係形成を行い、
文化が進化する「生命のように変化する人工社会」を作る研究基盤([README.md](README.md))。

**第一目標(2026-08-02 に再定位)**: 「現実を再現するほどの**約25万人規模**でシミュレーションを回すこと」自体。
**日常が返ってくるだけで成功**であり、その中に面白い関係性を持つエージェントが発生することを期待する。
出典: [docs/plans/source/design-discussion-20260802.md](docs/plans/source/design-discussion-20260802.md) §2。

- **創発は「おまけ」**: 語彙専門化・関係変化・社会構造創発・world-changer(k*)・組織の自然形成・自然造語は
  「必ず見たいもの」ではなく、**複数ランの比較から確かめられればよい**位置づけ。創発は事後的に拾う。
- **検証対象は「日常の統計の再現」**: 生活時間統計・移動・遭遇パターン。
- **規模だけでは実績にならない**(OASIS が既に100万体を達成済み)。独自性は
  「**連続した生活・空間・関係の持続・驚き駆動発火・兆しメモリを持った25万人が数日間壊れずに続くこと**」にある。
- **制約はリアルタイム同期ではなく総予算**: 総発火数 = N(人数) × f(1人1シミュ日あたり発火数) × D(シミュ日数)
  が GPU 7枚 × 10日間に収まる必要がある。知能(モデルサイズ・思考頻度・文脈長)は発火単価に入る。
  **規模・知能・期間は同時には最大化できない**。

## 2. 研究の柱

| 柱 | 内容 |
|---|---|
| **R²(k) と k\*** | Y = 4層(空間/資源/象徴/social network)への連続的な**書き換え量**(客観カウント)。k = 経験→内部状態の結合強度(主軸=ソロ内省での**信念の書き戻し自由度** `free/degraded/sham/off`)。Y を初期 traits で回帰した **R²(k)** を k で掃引し、init-determined → path-dominated の**相転移点 k\*** を、R² 低下・seed 発散・早期警戒シグナル(EWS)の**三角測量**で探す。交絡を切るため sham/null/compute_matched 対照を必須で回す。→ [README.md](README.md) 研究課題節 |
| **環境軸 H** | 環境由来の指標に k の名は使わず **H(到達異質性)** と命名し、**k×H の2軸**に分離。→ [twin-physics-vision-affordance-plan.md](docs/plans/twin-physics-vision-affordance-plan.md) §0-8 |
| **驚き駆動発火** | S = Σ g_c·\|o−ô\|/σ_c + trigger > θ。**予測誤差が大きいときに起きるのは「単に考える」ではなく「世界モデルの書き換え」**(model-revision)。発火源4種 = periodic / salience / internal(内省)/ social(会話)。→ [cognition-physics-plan.md](docs/plans/cognition-physics-plan.md) §6-3 |
| **F/N/P 分散分解** | g の初期値条件(persona/flat/noise)を CRN で振り、「生まれつき(traits 由来)vs 創発(経験由来)」を**分散分解**する(analyze_g.py)。 |
| **検証の作法** | 「合った指標と合わなかった指標」の**両方を提示**する。**較正と検証を分離**し、パラメータ凍結後に検証期へ移る。事前登録 = [stationarity-preregistration.md](docs/plans/stationarity-preregistration.md)(U-10)。 |

## 3. アーキテクチャの本質

- **R1 ドクトリン(恒常制約6項)**: ①新機能はすべて**既定 OFF** ②既定 OFF で **golden L1 バイト一致**
  ③**k 非依存**(LLM 呼数が k で変わらない)④**no-fingerprint**(engine は因子を名指ししない)
  ⑤**用途別乱数 stream** ⑥**観測がシムを変えない**。
- **観測がシムを変えない構造**: シム本体は「起きたこと」を L1 に記録するだけ。測定・集計・指標定義はすべて
  事後に L1 から([src/society/observer/](src/society/observer/))。研究者 frame とエージェント frame の分離。
- **observe / verify の二重化**: 本選の**観察ランは再現性を厳密に求めない**(repro_tier=journal/none の機能も投入可)。
  **検証ラン(verify)は strict のみ**。registry.py + run.mode で構造化済み(第72)。既定値は現行動作のまま
  = golden 資産は verify 側の検収装置として恒久維持。
- **認知 = 予測誤差 + 慣れ/感作**: 観測チャンネル14本の予測誤差を σ_c で precision weighting して S を作り、
  θ を超えたら発火。感受性 g は**慣れ/感作/引き戻し**(Groves & Thompson 1970・適格性トレース)で可塑化し、
  θ 恒常性は日境界のみ。
- **物理 = ゾーン別ハイブリッド**: 既定 **SFM**(自前・Helbing 2000 完全形)+ **交差流は ORCA**。
  ゾーンは**排他所有**で、移籍はゲート経由のみ(TransiTUM 原子的移管に整合)。
  → [physics-engine-selection.md](docs/research/physics-engine-selection.md) P2 決定節。
- **天候 = 較正済み生成器**: 気象庁東京8月930日(1996-2025)に較正した WGEN 系生成器。
  年効果項が**連続猛暑の鍵**(猛暑連長 KS p=0.97 vs 現行合成 p=2e-5)。専用 stream で **strict 等級**。
- **DT = スナップショット型**: 「**ある時点の現実の切り取りが舞台・同期不要**・現実は解像度を高めるデータ収集ツール」
  というユーザー定義。Kritzinger 2018 分類で **事前凍結=Digital Model / 日次自動取り込み=Digital Shadow** と正確に自己記述する。
  **状態同化(シム状態の書き換え)は不採用**(決定論の都合ではなく内生性研究が壊れるため)。
- **決定と実行の分離**: 朝に LLM が1日の計画(実行可能なスクリプト)を生成し、日中はルールエンジンが無料で実行する。
  驚き・社会的接触が閾値を超えたときだけ LLM が再考する。**すべての行動が LLM の決定に由来し、ルールは実行者にすぎない**
  (day_plan v1 / engaged モードとして第86〜で実装中 → [PENDING.md](PENDING.md))。

## 4. 体制と運用

- **役割分担**: **Fable 5 = 計画・検収・コミット** / **Opus 5 = 実行役**(バックグラウンド並列・ファイル互いに素で 3〜5体)。
- **検収の型**(全バッチ共通): 既定 OFF = **golden L1 バイト一致**・**draw 数同一**・**k=free/off の LLM 呼数一致**・
  **resume == straight**・**no-fingerprint 静的検査**・**registry 宣言**・**xdist フルゲート緑(2回走)**。
  加えて**ディスク実在確認+検収側の自前 pytest**(実行役の偽完了対策として標準化)。
- **実 LLM フルランはローカル禁止**(mock または ≤24step スモークのみ)。
- **devlog プロトコル**: ユーザーとの1往復ごとに1エントリ → 10 で圧縮して devlog-compressed.md へ。
- **台帳更新**: 実装バッチのコミットごとに本ファイル / [PENDING.md](PENDING.md) / [STATUS.md](STATUS.md) を更新(検収の一部)。

## 5. 本選

- **会期 8/15 – 8/30**(提出 8/30)。**10日ラン 8/16 – 8/26**。**GPU は A5000 級 × 7枚**(単一ノード=ops トポロジA)。
- **8/12-14 = フリーズ期間**(新機能追加禁止・検証と微調整のみ・観察ラン ON 構成の確定)。
- **8/15-16 = 診断ラン**(GPU 開放初日): σ_c 再実測 → θ 再較正(watch ON の27倍差の解消)→
  U-10 の確定判定ラン → **発火数・呼数の実測から本選の人数を最終確定**(呼数/人/日は人数不変ではない=外挿でなく実測)。
- 本選中は毎日 checkpoint(いつ打ち切っても成果)・live_viewer 併走・watchdog 併走。

---

# 第2部 — 完了済み実装の全リスト(システム別)

> 新機能はすべて **既定 OFF**(R1)。以下は**システム別**の網羅リスト。括弧内はバッチ番号とコミット参照
> (git 化は 2026-07-13 の初回コミット `2727e91` からなので、第1〜24バッチ相当は初回コミットに同梱)。

## A. 世界基盤・地図・空間

| 項目 | 内容 |
|---|---|
| 実地図(OSM) | Overpass 実取得の渋谷広域地図 v7。**全建物1,181(住宅633)・実名POI 1,098・1,208交差点・1,677道路折れ線・渋谷ちかみち地下141本・デッキ148本・車ゲートウェイ158**。`build_map.py --osm-date` で基準日凍結(現行 osm_date=2025-04-01)。3,499ノードでも40体2日35秒 |
| PLATEAU 実形状 | CityGML 4タイル抽出 **6,311棟**(DEM ground0=15.18m・最高230.4m=スクランブルスクエアで実世界一致)→ wide_v7 照合 **3,531棟**(IoU 中央値0.633)。第36 (`2335870`)。巻き向き事故=ear clipping が表裏破壊 → Newell 法線照合+DoubleSide (`0096adc`) |
| 実高さ配線 | `building_heights`(3,531棟)を sim 側へ配線(既定 OFF)。第67 (`29c0984`) |
| 可視行列 | `build_visibility`(2.5D LOS 行列)= シム外 CLI で事前計算。第68 (`c894267`) |
| DEM 地形 | DEM 2m 地形(交差点=谷底0m)・地下街 z−14.3m・歩道橋39基。第37 (`c466e3b`)。z列=3D Phase0(`world/elevation.py` DEM 双一次 O(1)) (`0fa95e1`) |
| 建物階層・知覚 | 同建物同階のみ知覚。知覚半径40m・4チャネル。範囲外は計算しない |
| 反実仮想の器 | **world.mod** = `edges_closed` / `edge_speed_scale` / `open_hours`(+`gate_capacity` 予約枠)。ラン開始時固定・profile 指定。第67 (`29c0984`) |
| EnvPack(基盤抽出) | 環境分類3層(共通基盤/共有参照/EnvPack)。`env/shibuya/env.yaml`+`institutions_jp.yaml`・**基盤4ディレクトリから地名リテラル全数除去**+契約ガード。`--env env/shibuya` が従来ランと **L1 完全一致**。第35 (`18c9210`/`bfa6cc2`) |
| 環境自動生成 | `make_env` CLI(7-stage v0-v2)。**下北沢390m角で2つ目の街を実証**(`0b09130`) |
| シナリオイベント | `world.events_file`(day/time/title/word → coin_media+ニュース配信)。ダッシュボードにフォーム |

## B. 交通・移動

| 項目 | 内容 |
|---|---|
| 経路移動 | A* + OD キャッシュ + **道なり連続補間**(テレポート禁止をテスト固定)。移動手段別サブグラフ(walk 800 / bicycle 2000 / car 3500)。RDP 形状保存間引き(`geom.py`)。実測歩行速度 中央値 1.14 m/s(渋谷実測 1.0-1.5 と整合) |
| 実ダイヤ(ODPT) | ODPT 実ダイヤ **6路線**+近似3路線(チャレンジ2026キーでメトロ3+東急2+京王1解放)。キーは環境変数+winreg フォールバック(チャット/コード/ログに残さない原則)。限定データは `data/odpt_challenge/` を .gitignore。JR東 GTFS は未投入を悉皆プローブで確定・受け皿 `fetch_gtfs_odpt.py` 実装済み(投入後2コマンドで全9路線化)。終電後は帰れない=定刻ダイヤ制約 |
| 背景交通 | Poisson 発生・3万台/日(設定値と明記)。車 OD 個体化(信号=期待遅延近似・車線容量渋滞)。ambient 既定=バイト一致 |
| SUMO 連成 | 公式版 1.27.1 で v0 全段完走(net 5,575 エッジ → OD 6,460台 → 24h fcd → 144step parquet)(`7674877`)。**タクシー配車 v1**=ハイブリッド連成(TraCI ブリッジ・配車純関数・wait-hold 量子化・実 SUMO 同 seed バイト一致・k=free/off 67=67)(`6da6cfd`) |
| バス | 簡易バス + **実バスダイヤ静的表**(`bus_table.py` + `build_bus_table.py` = GTFS→待ち時間表)。第48 (`2d13d83`) |
| 相乗り | v-Ride 相乗り。第46-48 |
| 歩行者信号 | SFM 一斉横断(サイドカー 192/80/スクランブル7・赤縁石滞留→青一斉横断を目視検収)。OSM crossing=traffic_signals |
| 通勤 | `commute_to_poi`(職場・学校 POI へ実通勤)。流入通勤者 74%(朝二峰流入) |

## C. 経済・制度・組織

| 項目 | 内容 |
|---|---|
| 経済基盤 | 賃金/消費/バイト/逼迫→grievance。口座(月給・家賃・ATM)。家計調査較正消費・銀行与信・VC の3段。不足点融資→貸倒→既存破産サイクルへ接続。第37 (`2434d5a`) |
| 制度 DSL | 4型(fee / bonus / curfew / weekly_event)= 成立提案が実効ルール化。ホワイトリスト・降格安全 |
| 制度深化 | 勾留・解雇規制(退職金/不当解雇)・営業許可(却下+許可待ち)/**最低賃金の床**(東京都1,226円/時・2025-10発効・既定0=床なし・自営は対象外=現実の穴を保存)/**代表制議会**(FJ 意見の最近傍投票=決定論選挙)/**立退き**(滞納30日→路上就寝・完済で再入居)/**破産**(滞納60日→免責+自由財産1万+出店制限30日)= 滞納→立退き→破産→再入居のサイクルが決定論で閉じる |
| 選挙の現実化 | 自発立候補・SNTV・供託金。議員は**名簿制**(実定数34)。適正手続(審議・パブコメ段階=立場表明・否決可能)・declare 型=権利創設。第37/38 |
| 行政 | 区/都/国・源泉徴収・消費税78:22・公務員給与 |
| 組織台帳 | 架空42社10校 → **11,010組織**(経済センサス分布・従業者±2%)。実在企業・学校名なし=手続き生成の合成データ (`b62ceac`) |
| 物流 | 店舗在庫((s,S)方策・O(1)/POI)+日次補充トリップ+商品実体。**封鎖で欠品波及**=災害物流断絶の土台。乱数ゼロ (`9ff8abe`) |
| サービス実体 | 6種データ駆動(滞在+課金+効用)。宅配/フードデリバリー(注文→在庫減→最寄り配達)。L2 業務実体(serve/org_output・オフィス51.5%/接客48.5%)。第46-47 (`fdf8c82`/`bf1b9c9`) |
| 商業 | 営業時間・動的価格・在庫。街頭広告 OOH+群衆視覚(新 stream "ads")。**広告転換 94.1%→ target 照合+非接触対照で 5.9% に修正**(第18) |
| キャリア | 転換・雇用の較正(layoff 2e-4 / switch 4e-4 / rehire 0.02) |
| 職場束ね直し | pool L2 の work_node 穴を台帳直束ね(org_id→workplace_poi.node)。第49 (`166a697`) |

## D. 関係性・社会ネットワーク

| 項目 | 内容 |
|---|---|
| 世帯・家族 | 世帯の現実化(渋谷64.5%・続柄・夕食共食0.69)+共同行動。第44 (`dcb6e37`) |
| 友人グラフ | homophily+所属+Dunbar層(hashlib 純関数・run.seed 非依存)。関係風化。第45 (`1043bbb`) |
| 関係の質 | 関係 tier・断絶・評判。負の評判 gossip(内生の悪評タグ)。第61 (`0baabba`) |
| **関係性の内生化** | フェーズ1=承諾/拒否の内生(`relations_endo.py`=構造化決定論抽出)第62 (`d6731e5`) / フェーズ2=**treatment 実験一式**(`endogenous_accept`・比較実験プロトコル=CRN+sign-flip permutation)第63 (`385c4ca`) / フェーズ3=誘い相手の内生(`endogenous_invite`+弱い紐帯探索枠)第64 (`6ad4b12`) / フェーズ4=関係の質の内生化(`endogenous_quality`)第65 (`e1938c6`) |
| **ダンバー認知枠** | `relations.dunbar`(既定 OFF・strict・乱数/LLM ゼロ)。**最外層上限51**(素値5/15/50/150×scale 0.34・最外層のみ拘束・Lindenfors 2021 の150懐疑を明記し感度分析軸として conf 化)。**休眠 = closeness 退避の単一作用点**で可逆(下流消費者を1箇所も改変せず)。上限適用は日境界1回(接触時適用は振動5739件を実測して棄却)。再会は**弱い紐帯探索枠でのみ**(Levin, Walter & Murnighan 2011)・明示的意向は休眠でも通す。`relation_dormant`/`rekindle` 2kind+L2 3列。実測: 288step40体で dormant 1378 / rekindle 252 / active_mean 8.0。第75 (`387b0b4`) |
| 内部可動性 | 転居/同棲/求職=内生の構造変化トリガー。第60 (`9cf9fe6`) |
| コミュニティ検出 | min_weight 2.0 + louvain 正準・7-13コミュ/窓・ライフサイクル66件・**組織 NMI 0.35 = 自然コミュは会社の線から乖離**。第18 |
| 意見力学 | FJ(Friedkin-Johnsen)`opinion.py` = 検査外・プロンプト非注入・接点は face/dm/sns のみ |
| 地位・階層 | `status.py` = 合成地位スコア百分位。イベント参加/購買/フィード露出の閾値を機械変調(優先的選択)。乱数 draw 追加ゼロ・プロンプト非注入。L2 に status_gini 等。第11 |
| 群のオントロジー | 文化圏×経験の安定ハッシュ純関数(run.seed 非依存)・composition 割合ノブ・**多軸機構**(seed_offset 独立ハッシュ=軸間無相関 χ²=7.19)・情報行動軸・防災訓練経験・**第3軸=同行者構成**(party_size データ駆動・日替わり決定論)(`7d54147`/`b7f8019`/`97267b1`) |
| ペルソナ | IPF×LLM+Verbalized Sampling。**100万プール決定論生成**(L1住民3万/L2…の層構造・議員34=実定数・実体736MB は gitignore)(`b5e0edc`)。`build_personas.py` / `build_icebreak.py`(全 k 条件で同一ファイル=交絡排除) |
| プールとローテーション | **日次 presence 名簿制**(P3=presence 純関数・PoolStore 遅延読み・密 intID(観測同一性)・**DormantStore dehydrate/hydrate**(記憶を持った再来街)・resume 跨ぎ L1 一致)(`79fc293`)。プール=同時滞在の数倍(realism-first: 人数>時間) |

## E. 認知プログラム(第79〜85)

| バッチ | 項目 | 内容 |
|---|---|---|
| **第79** (`4cab5f6`) | **Δt 不変化** | 定数の毎分レート化。`run.dt_min`(既定10=構造分岐で**1バイト不変**・1440の約数強制)。`timeconv.py`=分類テーブル **130キー**(rate 13 / prob 26 / **steps 31=逆比例の第4分類を発見** / invariant 60)・棚卸し全載 CI。Δt=5/1 スモーク済み。load_config 一点変換 |
| **第80** (`f49d2a5`) | **観測チャンネル+σ** | `cognition.channels`(既定 OFF・ON でも **L1 不変=サイドカーのみ**)= **14チャンネル**(外界5/身体8/予測不成立1=第81枠)。`measure_sigma.py` → `data/calib/sigma_c.json` 凍結(**σ=0 は床でなく除外**)・較正テーブル外部化(provisional 宣言をテスト固定)。precision weighting+イベント分節理論の文献根拠(誤差大→世界モデル書き換えの直接根拠) |
| **第81** (`d45b2b2`) | **閾値発火+同期バリア** | `cognition.fire`(既定 OFF)= 認知イベントキュー((発火時刻, agent_id) の**2要素厳密全順序**)。発火源4種 = periodic / salience / internal / social(**会話・内省の第一級化**)。**単一作用点 = `_phase_drive` の requesters 決定を差し替え** → 後方互換は**厳密バイト一致**。T1 完了順序不変(workers=4 実並行含む)・T2 発火オラクル・S 寄与内訳を `cog_fire` に記録 |
| **第82** (`39d5b26`) | **watch spec + 可塑性** | `cognition.watch` / `g_update` / `experiment.g_init`(F/N/P)。LLM が期待値 ô + DSL トリガを出力(**チャンネル id は不透明記号 c01…= 因子名をプロンプトに出さない no-fingerprint 解**・不正は前回仕様維持)。g 更新 = 慣れ/感作/引き戻し(Groves & Thompson 1970。単一窓上書きで**感作死の退行を自己発見** → 適格性トレースで修正)。θ 恒常性 = 日境界のみ。model-revision 行(中立文言)。`analyze_g.py` = 分散分解(生まれつき vs 創発) |
| **第83** (`f2355c2`) | **θ較正+発火観測** | `calibrate_theta.py` = θ 全体スケールのみ掃引(**theta_scale=0.03125 で f=7.90/日・誤差1.2%**・凍結+dotlist 適用=**src 差分ゼロ**)。★**watch ON は27倍差 = 実 LLM 再較正が最重要**。`analyze_firing.py` = 間隔分布/原因内訳/Kleinberg バースト/**発火連鎖グラフ**(A→B 因果候補・確度3段)/的中率。推論量見積(salience/人/日は人数不変だが**総呼数は不変でない**=GPU 外挿注意) |
| **第84** (`616de2c`) | **環境フィードバック** | `env.feedback`(既定 OFF・strict・LLM/乱数ゼロ)= ①ホーム密度+乗降→停車延長→遅延(駅は乗降人数が主説明変数・回復運転 γ=0.7・**不動点 dwell_cap/(1−γ) = 10分に収束を実測**=T5)②改札飽和→入場規制(有限解除+クールダウン・`gate_capacity` を初消費)③POI 占有→待ち→filter_open 除外。**環の閉じを L1 実例で実証**(待たされた本人が密度に還る)。step 末一括・congestion 既存語彙のみ |
| **第85** (`de64571`) | **Perception/Intent 契約** | `cognition.contract`(既定 OFF・strict)= 世界→Perception→prompt / LLM→Intent→実行 の2型に結合面を限定。**ON/OFF で全プロンプト文字列まで完全一致**(`prompt_kwargs()` 再構成による無損失性の証明・sim を識別子として不参照)。build_prompt 49引数と契約の集合一致をテスト固定。直接参照の残置リスト明示(`planning.py` = 残置第一候補)。body/salience はプロンプトに出ない構造 = P3 no-fingerprint の前倒し |

## F. 認知・記憶・自己(基盤)

| 項目 | 内容 |
|---|---|
| LOD 発火 | 驚き/予測誤差ゲート。**発火率 4.1-11.4% ≒ LLM 呼数 1/12**。予算 N 比例化(`lod.n_proportional`) |
| 欲求駆動 | ゲージ→個人閾値申請→重み抽選→不発30%減衰。needs 5次元 |
| 記憶 v2 | 3層(統合は内省同居・書き戻しゲート=beliefs のみ=k 境界)。**ACT-R 記憶**(d=0.5, τ=−2・専用 stream・memory_fail)。100日実証で劣化なし・belief 線形蓄積 |
| 内省 | ソロ内省=k の operational 実装部位。個別就寝(22:00-25:50)→ LLM が自然分散。**深い内省 = 出来事誘発**(日内衝撃ゲージ ネガ2:ポジ1 加重+個人閾値(NFC/LOC 写像)+incubation 1-2晩+cooldown 3日)。R1 呼数完全不変。第12 |
| 自己モデル | `self_model_days`(N夜の内省を深い内省に格上げ→self/ties→プロンプト注入=自己認識の再帰)+**無意識層 implicit_self**(行動カウント EMA 逸脱→「最近の自分」1行を日次決定論合成=揮発的作動自己。核自己とフィールド分離・双方向結合)。第11-12 |
| 主観的世界モデル | `worldview.py` = C1 場所×時間帯の期待 EMA+誤差 / C2 可制御性(0.5起点・世界の応答のみで分岐=純経験の経路依存・日次キャップ)/ C6 開拓的行動の記述規範。第20 (`ec18648` 以前) |
| 朝の一日計画 | 起床1回 LLM・全 k 同数 → routine の行き先の土台。`planning.py` |
| 日課計画 FW | S1 = 型スキーマ(自由文 intent 先頭+アンカー先置きコンパイラ+失敗の階段)(`89f275b`) |
| 確率的実行 | S4 = motif 15% / ±30分ジッター / 寄り道0.153 / Gumbel 温度3分類 (`70a9628`) |
| 退屈ドライブ | S5 = 長居蓄積→閾値で未訪問 POI 探索(LLM なし発火・0.57〜3.6回/人日で較正可)(`2c0fb33`) |
| ナラティブ補間 | S2 = 有界リングバッファ30→機械ダイジェストを全 LLM 注入・夜内省の物語化 (`7e7fcb8`) |
| 会話3層 | S3 = C2 構造化会話 **30.9/人日**(Dialogue Act 決定論遷移→関係/FJ意見/語彙接触へ機械効果・**LLM ゼロ**)・C1 昇格は drive 経由・C3 すれ違いカウンタ (`713af7a`) |
| 方針キャッシュ | S7 = k 非依存物理キー・near-match(既定 OFF 運用=ユーザー決定)(`c7b09aa`) |
| LLM 一括発行 | S6b = `generate_many` 共有状態逐次・recall 2ラウンド+BufferSink 遅延放出で **ON=OFF バイト一致** (`61b4cad`) |
| 入力解像度 LOD | `cognition/lod.py` = 軸専用 stream 割当機構・5ノブ・OFF バイト一致・水準 narrow/mid/wide。Rational Inattention 接地。**R_input × D_output の2因子直交**(「多く見る vs 深く考える」を初分離)・取り下げ条件 K1-K4 事前登録。第30 (`70c78be`) |
| 心理プラグイン | 4種(SDT / 集団効力感 / Lynch / Searle)= 全て既定 OFF・因果構造のみ文献接地 |
| 価値 | `values.py` = 4軸(実用/感情/社会/認識)。辞書+自己申告・充足の限界効用逓減+日次中立回帰。価値3分類 / 3M 欲望ネットワーク |
| affect ハブ | arousal+salience 統一(感情・興味・注意は1回路という脳科学リサーチ由来)。飽和を破る第2駆動軸 |
| スケジュール帳 | 会話から決定論パーサで未来予定抽出→双方の帳簿→プロンプト注入(**追加 LLM ゼロ**) |
| 自由度 | **開放行動 "do"**(`freedom.open_actions` = LLM 自身が自由記述で行動決定・物理/所持金/拘束の客観ゲートのみ)第17。**自由度 P2**(move_home / buy / study / partnership / deviance・既定 OFF・検査外隔離)第34 (`5452710`) |
| 自助・運 | 自助努力 affordance(`self_dev` = 経験由来ストック・累積 gain/(1+x))第52 (`727031a`)。運・実力分解(関係 = 運 ΔR² 0.19 > 実力 0.17・収入 = 運 0.001)第51 (`5248109`) |
| 不確実性モード | `chance.py` = 偶発層 windfall 等。再現性実験 vs 純観察の選択制。第54 (`27095dd`) |
| spark treatment | `spark.py` = trait-blind 純関数選抜(traits 改変 / run.seed 変更で不変)。第53 (`54595c0`) |
| 健康・生活 | 健康疲労病気/世帯家族恋愛/災害・運休・停電/観光・多言語・犯罪/離散感情・長期目標・趣味(第8バッチ H1-H6) |
| 相対的剥奪ほか | G1-G6 = 相対的剥奪(飽和を破る)/関係の質 tier・断絶・評判/制度3ルート(労働争議・決定論投票・警察執行)/年中行事・ハロウィン群集/キャリア転換/情報環境(推薦・バイラル・炎上) |
| 宿泊 | Wave L = ホテル泊・連泊・reflect_step(k 処置同格)。POI パッチ12件 |
| 暦・行事 | `start_date` 設定可・weekday_work・年中行事 |

## G. 言語・ラベリング・伝播・真偽

| 項目 | 内容 |
|---|---|
| ラベル伝播 | 採用閾値2 = complex contagion。全員記録しない・drift する。vocab_coin / transmission(伝播系譜) |
| 伝播チャネル | face / sns / news / search / dm を transmission に記録 |
| 創発検出 | `detect_emergence` = 後付けテキスト検出(**架空イベント「ボードライブ」を12人が105回共有**・規範発話・語形ドリフト「パーラー→パーリー」伝播・coined 分離)。第22 |
| SNS 架橋 | `sns_geo`(既定 OFF)= SNS/DM 伝播に dist_m。**SNS 伝播の27%が500m超の遠距離架橋**。第22 |
| **場所の意味づけ** | `labeling.place_binding`(造語の場所束縛→知覚1行)。第69 (`df0c446`) |
| **エコー/自己反復計測** | `observer.echo`(L2 常設5列・`enabled:false` で退避可)= 同一話者の言い換え反復を Jaccard 系で検出し L1 マーキング。**伝播 KPI のエコー除外は新列並記**(既存列不変=ID-U3)。adopt_novel=相異なる2人=complex contagion 本来の趣旨。第70 (`2524da9`) |
| **未定義行動レジスタ+沈黙** | `freedom.undefined_register` / `explicit_nothing`(既定 OFF)= enum 外の行動出力を fallback 破棄せず `undefined_action` として記録(**行動空間の外へ出ようとする個体**の操作的定義候補)。fallback から排他振り分け・保存則。「関わらない」を受理動詞に明示。第70 (`2524da9`) |
| **真偽台帳ミニマル** | `beliefs.enabled` / `verify_actions`(既定 OFF・journal 等級)= **fact 8種**(conf 駆動・エージェント絶対不可視)・信念状態/伝播木・**検証行動3種**(現場確認・当事者に聞く・ネットで裏取り)・**漏洩3点ガード**(静的検査+CachedLLM 関門 canary+全プロンプト検査)・真値は `beliefs_ledger.json` へ分離・`analyze_beliefs.py`。第73 (`4257310`) |
| **規範化ステージ** | `labeling.norm_stage` = 4段検出(初出→他者引用→**S3 指示詞化**「例の」→**S4 合意参照**「さっき決めた」・markers=conf 単一源・観測のみ=プロンプト1バイト不変)。**coiner / definitizer / institutionalizer の分離**。下方因果解析 `analyze_norms.py`(閾値は引数必須)。第74 (`008d0db`) |
| コホート+ゼロ対照 | `observer.initial_frame`(初 presence は L1 導出=シム変更ゼロ)+`experiment.flat_traits`(traits 定数化ゼロ対照・**CRN 不変条件は「乱数消費本数一致」**=呼数不変は処置の性質上不成立と訂正)+`zero_traits.yaml` 4セル。第74 (`008d0db`) |
| インターネット層 | `net/internet.py` = SNS(投稿=LLM・タイムライン・フォロー)/ニュース/**検索=シミュ内DB**(語彙来歴+ニュース+実在POI+SNS索引。実 API は D13 再現性+架空世界の閉性で不採用)/DM |
| 再帰性 | norm_line / digest_line / repeal / impact_news = 監視→知覚→改変の閉ループ |
| 世界改変ツール | 5種 = 4軸(モノ/制度/人/虚構)。中立提示・R4 客観カウント。**初の行使を第31-32 夜間ランで観測**(ablit_free_s42 の flyer_post 2件・過去2,654提示で0件) |
| 造語の自然観察 | coin 文脈のみ記録(促進しない=`natural-coinage-observation` 方針) |

## H. 物理エンジン(P2 選定 / P3 縫合・竹系)

> 正典: [highfidelity-3d-physics-plan.md](docs/plans/highfidelity-3d-physics-plan.md)(**高精細渋谷 3D モデル × 物理シミュレーター接合**・
> 2026-08-02 に**松案で承認**=竹への縮退退路つき)+[cognition-physics-plan.md](docs/plans/cognition-physics-plan.md) §4。

| 項目 | 内容 |
|---|---|
| 自前 SFM | `sfm_core.py`(Helbing 式・文献値・希望速度=メゾ所要時間を厳密保存・スクランブル交差点を実データから自動導出)。オフライン合成(`84d034b`)→ 第58 で移設+壁斥力 |
| **P2 選定** | **ゾーン別ハイブリッド決定**(2026-08-02。ユーザー委任「ベンチをまわして君が決定して」→ ベンチ再実行=前回と**全指標ビット一致**)。既定 SFM(基本図 Weidmann 整合)/ 交差流は **ORCA**(0.924 vs 0.530)・条件6項。比較プロト (`fe802cc`)・決定文書 [physics-engine-selection.md](docs/research/physics-engine-selection.md) P2 決定節 (`da64b69`) |
| レーンA データ3本 | 松A-1 + 竹-1(tran LOD3 の歩道実ポリゴン+被覆マップ)+ 竹-2(ubld LOD4.1 → **壁2,834本/4層/188ゲート**)。Draco 148タイル1.1s・座標ミリ一致・GEOID 36.79 実測・影落とし15.7%発見・歩道被覆22.1%。新54テスト (`5ff56c4`) |
| **竹-3 f_iW** | `sfm_core.Crowd` に**対壁斥力 f_iW を追加**(既定 OFF)。壁最近点は空間ハッシュで **91倍速**・WallCrowd 薄型化。★**揺らぎ項 ξ 欠落バグを修正**(構造的に再発不能へ)。ξ 実測 = レーン形成改善なし → P2 文書の推測を実測訂正。新21テスト (`086dabe`) |
| **竹-4 P3 境界縫合** | `physics.zones` = conf 宣言(ポリゴン+engine sfm\|orca+dt_sub+壁/歩行面ソース・重複は構築時例外)。**単一作用点 = `_phase_move` 直前の `physics.phase()` 1行**。**排他所有**=`_phys_zone` 単一値がゲート経由のみの移籍を構造保証。`orca_core` 昇格(reference 不変)+半径マージン+決定論的分離パス(min_gap+0.100m・分離発火0回)。**guarded ゲート**=id 昇順・流入は現在座標(**瞬間移動が原理的に不可**)・信号ゾーンは SignalGate 青のみ入場。実測由来の設計変更2件 = ①出口直進で**跳び 41.4m → 通過点追跡で 2.25m** ②step 途中退場に10分予算を丸ごと与える**二重移動バグを発見**→ budget_scale 控除(回帰固定)。境界連続性 = gate accel p99 4.6 / interior 4.4 / 反転 0.000。**物理→知覚**=第85契約の body 欄(blocked/contact/local_density)注入・prompt_kwargs 非露出=**プロンプト文字列不変**。L1 `zone_gate`+L2 5列(OFF 時列なし)+checkpoint 中央管理(phys_state)+新 stream physics(stateless)。交差点スモーク(mock60体・実測信号 cycle 140)= 通過95件・縁石待ち p50 20s(赤93s と整合)・強制解放0。**目標 8/11 を9日前倒しで完了**。新36テスト (`f1024fc`) |
| 屋内 SFM | `_phase_indoor` = 2層タイムライン(認知10分+物理0.2s 遷移駆動)。第58 (`bcbc1b9`) |

## I. 天候・環境

| 項目 | 内容 |
|---|---|
| 天候(合成) | `weather.py`・stream "weather"・雨→grievance。第7 |
| **天候 W1** | 気象庁**東京8月930日(1996-2025・欠測0)を凍結**(公共データ利用規約=同梱可を確認)+WGEN 系生成器の較正。**年効果項が連続猛暑の鍵**(文献+実証)。猛暑連長 KS **p=0.97**(現行合成は p=2e-5)。**P(≥35℃) が 2015-25 で3倍**の発見 (`bd7b142`) |
| **天候 W2** | `weather.mode`: **synthetic(既定=不変)/ generated(較正生成器・"weather_gen" stream 一括生成=strict・resume 一致)/ table(実日付表引き)**。10日窓でも10連猛暑到達可。来歴 sha256 を summary/manifest へ。★**cal_day の checkpoint 欠落バグ(resume で weather 二重記録)を発見・修正** (`ba8ac2d`) |
| 環境フィードバック | → E 節 第84 を参照 |

## J. 屋内・ミクロ(第58 バッチ B0-B9)

| 項目 | 内容 |
|---|---|
| B0 間取り | Web 実データ間取り **21棟197階**(`floor_layouts.json`・店名不記載)(`bd53078`) |
| B1-B2 基盤 | マクロ⇄ミクロ観察基盤・**単一の真実**原則(マルチレゾリューション文献)・vision 休眠資産の正典化・SFM 移設+壁斥力 |
| B3 屋内エンジン | `_phase_indoor` = 区画割当 / フロア内 Markov / 階間実軌跡 (`bcbc1b9`) |
| B3b 接続 | ミクロ→マクロ動力学接続(遭遇観測→**返答相手優先**(1-step ラグ))・壁 LOS 知覚 (`32971a0`) |
| B4-B8 | 会社観察データ層(serve に org_id/floor 付与)・会社 UI タブ・在館観測列 (`119adf2`) |
| B5-B6 | **2D/3D セマンティックズーム**(旧ランバイト同一証明・JS パリティ)(`32971a0`) |
| B9 統合検収 | **観察不変性3点テスト化**(tracks トグル L1 バイト一致 ほか)・30日外挿+65min (`380413e`)。ゲート 1306 → **1626** |
| フロアガイド | 実フロアガイド10施設(`floorguide_shibuya.json`・カテゴリ事実のみ) |

## K. LLM 基盤

| 項目 | 内容 |
|---|---|
| バックエンド | Mock / Ollama / openai_compat / anthropic(temp/seed 送らない)。**RouterLLM** purpose 別 dispatch(子を各自 CachedLLM で包む = D13 維持・キャッシュは子 name 別ファイル・API キーは環境変数名のみ)。第23 (`89a3dd9` 以前) |
| 応答キャッシュ | `llm/cache.py` **CachedLLM**(D13)= `llm_cache.jsonl` = **応答の内容アドレスキャッシュ**(key=sha256(model+params+think+prompt))・永続化・run 間共有可 |
| vLLM / FleetLLM | sticky routing・キャッシュは URL 非依存 |
| 制約デコード | `model.format` none\|json(既定 json = 完全互換)・think 併用ガード・キャッシュキー互換。第33 (`105275a`) |
| トークン予算 | `plan_max_tokens 448` / `reflect_max_tokens 768`(2048 から右サイズ化)。実プロンプト実測 **1,014 入 / 41.5 出 tok** |
| **LLM 健全性 KPI** | fallback 率など L2 KPI・`watchdog_llm`・`observer.llm_health` 3列(既定 OFF)。第66/P0 (`5101b8a`) |
| **LLM 全文ジャーナル** | `model.journal`(既定 ON・**gz 11.5x = 1万体10日 ≈ 0.6-1.1GB**)。multi-member gzip・checkpoint mark/truncate で **resume 二重記録なし**・シム本体に読み経路ゼロを静的固定。第71 (`c75025b`) |
| **REPLAY fail-fast** | `model.cache_mode: free / replay`(miss 時に step/agent/key を明示して即例外・**フォールバック絶対禁止**)。T2 = FREE→REPLAY で L1 全行一致・T5 = 1行削除で即 fail。第71 (`c75025b`) |
| **run_manifest.json** | git SHA / config hash / run_seed / モデルID / 全トグル / history。第71 (`c75025b`) |
| watchdog | 自動再開・巻き戻し。`--stall-min` 運用 |

## L. 観測層(L1 / L2 / L3・registry・ablate・state_hash)

| 項目 | 内容 |
|---|---|
| 観測4層 | **L1 イベント**(append-only・part parquet + zstd・flush_segment)/ **L1b LLM** / **L2 metrics** / **L3 snapshot**。イベントレジストリ式。`vocab_coin`・`transmission`(伝播系譜) |
| ストリーミング | P4 = `stream_events` 逐次(合成2,000万件・ピーク 786MB < 2GB)(`64c9013`) |
| move_segment | 移動の経路ポリライン記録(「直線移動の正体」= ログが最終座標のみだった観測側の情報不足) |
| **機能レジストリ** | `registry.py` **175件**(strict 146 / journal 27 / none 2)に repro_tier / affects_k / fingerprint_risk を宣言。**未宣言は CI fail**(全 bool リーフ走査で宣言忘れが構造的に不可能)。第72 (`84450d8`) |
| **ランモード** | `run.mode`: **none(既定=同一オブジェクト返却で1バイト不変)/ observe / journal / verify**。モード超過機能の自動 OFF+manifest 記録+目立つ警告。**verify は planning/tools/rules を落とす**(= LLM 自由文が世界状態になる3機能の正直な宣言)。28件強制 ON でも完走。比較ガード3スクリプト。第72 (`84450d8`) |
| **ablate 4種** | `ablate.llm_off`(LLM 0本・ルール層のみ)/ **`propagation_off`**(発話生成するが他者文脈に不注入・**捏造プレースホルダ拒否**・`fingerprint_risk=known` を正直宣言・呼数差 **+1.61%** は間接ドライブ経路のみ)/ `cognitive_tier`(fleet 強制下位)/ `shuffle_partners`(always-draw = RngHub stateless で既存 draw 順不乱)。第78 (`e2e4a5f`) |
| **状態ハッシュチェーン** | `observer.state_hash`(既定 OFF)= 正準シリアライズ sha256 チェーン。T1 同 seed 一致・T6 workers 1 vs 4 一致・改竄3種検知・**3.5µs/agent/step**・片側検定と明記(厳密判定は L1 バイト比較のまま)。第78 (`e2e4a5f`) |
| **metrics_spec_hash** | 指標定義14ファイルの正規化ハッシュ → manifest(T7)。第78 (`e2e4a5f`) |
| 観測レンズ | `lens.py` = データ駆動 kind→軸・2段マッチ。資産分布/弱い紐帯/模倣連鎖(`assets.py` = L2 全体5列 gini 等)。第50/59 (`fd32dca`/`55d0e0e`) |
| 逸脱率・内生変動 | `deviation.py`(ペルソナ逸脱率=**裁量 0.333 vs 全時間 0.119** = 義務が従順度を3倍水増し)第55 (`2785c9f`) / `structure.py`(edge churn 4列・**順位 τ 0.54→0.88** = 7日で固着未確定 → 30日必要の直接裏づけ)第56 (`8ccde6b`) |
| 顕著イベント | ビューア顕著イベントパネル(抽出決定論・バイト同一ゲート)(`e882004`) |

## M. 検証装置・決定論基盤

| 項目 | 内容 |
|---|---|
| RngHub | PCG64・**named streams 68+**・順序非依存・用途別 stream(R1-⑤)。約60本の全数列挙監査済み |
| golden | 既定 OFF で **L1 バイト一致**。全バッチ共通の受入基準 |
| checkpoint / resume | 中央管理・**resume == straight で L1 全層バイト一致**。`--start-tod` 等の跨ぎも検証済み |
| CRN | 共通乱数。treatment 比較(sign-flip permutation)・compare_runs の CRN 健全性チェック |
| k 呼数一致 | `controls.mode=compute_matched`(off でも内省実行・全破棄=4条件で計算量一致)/ `null_series` / FSS 掃引(N×α 擬似連続 k 軸) |
| no-fingerprint | 静的チェック(engine が因子を名指ししない)。R9 |
| PIMMUR 準拠 | 6原則の準拠表(5 PASS / Unawareness PARTIAL)。C3 尋問テスト 126呼 = in-domain Unawareness ほぼ完全(S4 ツール提示対でも0%)・S5 第三者のみ ablit/8b が看破 = 条件付き不合格 (`6599604`) |
| judge | `judge.py` = LLM-judge ハーネス(**補助**指標)・Fleiss κ ≥ 0.7 でのみ採用・本体へ逆流しない(R4) |
| 並列ゲート | pytest-xdist 採用。直列 53:32 → 並列 5:33(**9.6倍**)・本数一致検証。第43 (`deb0d4e`)。第70 で 70分 → **4.5分**へ是正 |
| バックアップ | `ops/backup-daily.ps1` + タスクスケジューラ 23:30 = git + 日次 mirror + 日付 zip 14日保持の三重保全 (`4cc7fa5`) |
| 公開ミラー | `publish_public_mirror.ps1` で `shibuya-simulation-public` へ同期(git filter-repo で GPL 参照+主催メモを全履歴除去・noreply 書換・Secret scanning+branch protection・**決定論=fast-forward 1コマンド**)(`8092625`/`22fbbc7`) |

## N. 3D・可視化

| 項目 | 内容 |
|---|---|
| 2D ビューア | `viz/make_viewer.py` → `viewer.html`(地図)+`dashboard.html`(X 風 SNS・LINE 風 DM・SERP 風検索ログ・論文風グラフ5種・関係グラフ)。OSM タイル背景・レイヤーパネル・密度ヒートマップ・不透明度スライダー。軽量化 255MB→5.5MB / `--no-traffic` で 439MB→8.4MB |
| 3D ビューア | `export_3d`(手書き glb + Blender bpy)+ three.js 同梱 `viewer3d`。**≤80MB ゲート**運用。`--low-mem` = バイト同一 19/19 |
| PLATEAU 注入 | ハイブリッド glb 32.6MB + ビューア注入(既定はバイト同一)。ACES ライティング |
| UE5 | `export_ue.py`・PLATEAU 渋谷 2025年度 import script + README(mode="sequence" = BP 不要) |
| 語彙伝播の可視化 | transmission 辺をビューワーへ(語クリック=採用曲線+チャネル)(`aba9ec0`) |
| **DT P0 軌跡バイナリ化** | `--tracks-binary`(既定 OFF = 既存出力バイト同一 **31/31**)= GLB 同型(magic+JSONヘッダ+payload)・**int16×0.05m 量子化**+**状態は出現値パレット+uint16索引**(素 int16 は屋内 max 720,802 で不可と実測し設計変更=完全可逆)+base64 JSONP の chunk sidecar 遅延ロード+LRU4。**viewer3d 86.1MiB → 24.7MiB(ラン長非依存)**・sim_ue 10日 **0.23GB**。量子化往復誤差 厳密0。第76 (`cb7b5cd`) |
| **P6 追いかけ再生** | `scripts/live_viewer.py`(**読み取り専用の別プロセス・src ゼロタッチ**)= part parquet 増分読み(**parquet フッタ主判定**・payload 列は見せ場イベントのみ読み **311,218行/秒**)→ **ライブ風 HTML**(`_live/`・静的 HTML 1回書き+`live_data.js` JSONP 差し替え)。★**Windows 共有フラグ事故を発見・修正**(`open()` が FILE_SHARE_DELETE を立てず、読み中 part の unlink が PermissionError = 「読むだけ」でランが finalize 異常終了する経路が実在)→ `_open_shared`(CreateFileW SHARE_READ\|WRITE\|DELETE)。第77 (`957e9a5`) |
| **3D 品質修正** | 原因 = OSM ドレープ解像度が **240 セグメント頭打ち**(実効 14.5m vs 地形 2m 格子 = **解像度 1/7**)で **面積33%が地形下**・地下街メッシュ露出・IDW スパイク(max 4.2m)・線路/道路の非接地(67%埋没)・**sim floor 未クランプ**(2階建てに floor=42 → +138m)・カプセル中心配置。修正 = OSM を**地形メッシュ直貼り**(交差が構造的に不可能)・**TIN 重心座標補間**・表示側 w クランプ・建物参照 upOf/footY 足元アンカー+サイズスライダー。数値検証 = **屋根超え 531→0・線路埋没 310→0・足元Δ 3.9m→0.000m**。新19テスト・2555緑 (`da64b69`) |
| **レーンB テクスチャ統合** | 松テクスチャ表示(shadowed 除外 = gml_id 重複ゼロ)+梅の地下街塗り分け(z 問題 47%→2.85%)+縮退策で **105.61 → 79.39MiB = 80MB ゲート内**(余裕0.61MiB)。src/conf ゼロタッチ・既定バイト同一。新21テスト (`d996240`/`de2f684`) |

## O. 解析スクリプト群

`analyze.py`(単一 run: agent 特徴量/カスケード/network/EWS/R²/図・`report.md`)/ `analyze_sweep.py`(条件横断: R²(k) の seed 階層ブートストラップ CI・EWS・seed 発散・**計算量交絡監査**)/ `run_sweep.py`(k 掃引・FSS)/ `bench.py`・`bench_scaling.py`(N=10..10000)/ `estimate_runtime.py` / `judge.py` / `observe.py`(訪問・関心)/ `observe_flows.py`(金流+注意ネットワーク・被注意 gini)/ `calibrate_report.py`(**現実バンド表**=NHK 生活時間調査等の出典付き近似と照合)/ `flows_grid.py`(25m×1h ビン・Fruin の LOS)/ `panel_stats.py`(効果量主・BH-FDR)/ `analyze_od.py` / `compare_runs.py`(CRN 健全性)/ `network_ts.py` / `summarize_run.py`(数値照合ガード)/ `analyze_groups.py` / `analyze_luck.py` / `analyze_founders.py` / `analyze_resolution.py` / `diagnose_stationarity.py`(D0 診断)/ `detect_emergence.py` / `analyze_beliefs.py`(第73)/ `analyze_norms.py`(第74・閾値は引数必須)/ `analyze_specialization.py`(第78・**propagation_off 対照差分でのみ主張**・実装健全性と現象由来を別セクション化)/ `measure_sigma.py`(第80)/ `analyze_g.py`(第82・分散分解)/ `calibrate_theta.py`・`analyze_firing.py`(第83)/ `live_viewer.py`(第77)。

**モデル人間らしさバッテリー**(第90・2026-08-03): `scripts/model_battery/`(ハーネス/刺激/指標/対照統計/レポート・2,517行・21テスト)。
A層=社会生活基本調査(e-Stat・数値収載可を規約確認)/B層=摂動4種/C層=会話統計(NUCC は CC BY-NC-ND=記述統計のみ・
絶対評価は公表値なしで不可と正直登録)/D層=分散と裾(**生命線**・判定線は引数必須=ハードコード禁止)/E層=長期退行+プラセボ対照。
縮小版実測(qwen3:4b/8b/プラセボ・117呼・エラー0): ★**8b は A/B/C で勝つが D層分散が完全に潰れる**(6サンプル全同一)=
混成 fleet を「性能でなく多様性のため」に組む方針の実測裏づけ・4b は計画スキーマ遵守に難(day_plan 配置への警告)・
ollama seed 非再現(ハーネス層のみ決定論と宣言)・モデル切替時 VRAM 未解放で3.3倍遅延の運用事故を発見し unload 既定 ON。
→ [model-battery-design.md](docs/research/model-battery-design.md)

## P. データ資産

| 資産 | 内容・ライセンス |
|---|---|
| OSM 地図 | `data/shibuya_osm*.json` / `env/shimokita/*` — © OpenStreetMap contributors・**ODbL 1.0**(派生 DB は ODbL 継承) |
| 人流 | `data/jinryu/` — 国交省(Agoop 提供データより作成)・政府標準利用規約2.0。**平日昼ピーク 37.2万・24h 平均 23.5万**(「最大=週末夜」を「平日昼」に訂正)。144step 目標曲線 CSV |
| ODPT | `data/odpt/` — ODPT 利用規約。出典表示は各ファイル `_meta` に付与。限定データは `data/odpt_challenge/`(.gitignore) |
| PLATEAU | CityGML 4タイル・3D Tiles zip(テクスチャ付き LOD2.2 148タイル / 道路 LOD3 / 地下街 LOD4.1) |
| フロアガイド | `data/floorguide_shibuya.json` / `data/floor_layouts.json` — **カテゴリ事実のみ**(店名・ブランド名不記載) |
| 組織台帳 | `data/organizations_shibuya_wide11k.json` — 手続き生成の**合成データ**(実在企業・学校名なし)・11,010組織 |
| ペルソナ | `data/personas_*.json`・100万プール(実体 736MB は gitignore) |
| 天候 | 気象庁 東京8月 930日(1996-2025)凍結・来歴 sha256 |
| 較正値 | `data/calib/sigma_c.json`(σ_c 凍結・provisional 宣言)・theta_scale=0.03125 |
| three.js | `viz/vendor/` — MIT |
| 実人口統計 | 夜間 2.96万 / 同時滞在 20-30万 / 日次ユニーク 70-120万 / 従業者 25.7万 |

## Q. 実 LLM ラン実績(完了済み)

| ラン | 結果 |
|---|---|
| day80(80体×1日 qwen3:8b) | **LLM 1,327回・fallback 0**・発話849・投稿255・DM151・検索79。**シブヤレンズ伝播1,540回 → 79/80人採用**(sns 1172主導) |
| mem100(実 LLM 5体×100日) | 記憶劣化なし・belief 線形蓄積・3,805呼212分。変革モチベ分析 = efficacy 天井 / grievance 床に飽和し個体差消滅(最大の詰まり) |
| 現実較正(第13a) | 乖離3系統を較正(窃盗×554 → crime_prob 2.0e-6 / タクシー×13-20 → prob 0.02 / 雇用×80-100)。100日で全✅。**機械系=mock・行動系=実 LLM** の分担確立。不満 0.101→0.034 = k* 信号が外生ノイズから浄化 |
| R²(k) パイロット(第13b) | R²ext free 0.508/0.800 vs off 0.387/0.621(Δ+0.12/+0.18・両シード符号一致)。※**第20 で内省全滅バグ(reflect think=true で belief 書き戻し0件)が判明したため、この値は要再検証** |
| daily_llm_20a7d(20体7日) | 全項目 現実バンド内 |
| daily300_100d(mock 300体100日) | 較正が再調整なしでスケール。D0 診断 = **TRANSIENT_ONLY・burn-in 約18日後に定常化**(本選10日ランは丸ごと burn-in 内という要判断事項を検出) |
| 統合リハーサル 1万体 | 完走。熟慮 16.8/人日 ✓・RSS 14.5GB |
| 講演デモラン(200体×3日) | 238,993イベント・fallback 1件(0.008%)・viral_cascade 230・交際11組 |
| model×k 4セル×2-3シード | **初の世界改変ツール行使**(ablit_free_s42 の flyer_post 2件)。k 対照(free−off)は inst/ablit **同方向** = k* 信号のモデル横断保存の暫定示唆 |
| **夜間実 LLM 検証ラン**(night_llm_100a3d) | **完走**(2026-08-02。計画=100体×3 sim日 / 実績=**100体×288step = sim 2日**)・production+Ollama qwen3:4b・**checkpoint 毎日**・watchdog + live_viewer 併走・**3,759呼・fallback 0・plan retry 0・cache 27.6%・reflect 176 正常**(旧内省空バグの実 LLM 正常動作確認)・purpose 8種健全。**「LLM シミュレーションが回る」検証を達成**。`runs/night_llm_100a3d` に 2D/3D(テクスチャ74.45MB=ゲート内)ビューワー生成済み。★事故2種の発見と復旧 = watchdog stall 20分 < 初回 flush 間隔(設定ミス)で健全ラン2回殺害/**1呼び出しに 1時間47分張り付き = LLM 呼び出し全体ハードデッドライン欠落バグを発見**(→ [PENDING.md](PENDING.md) の保守バッチへ) |

## R. バッチ完了年表(検収済みの記録)

| バッチ | 内容 | 完了日 | 新テスト / 累計 |
|---|---|---|---|
| 第70 | IDEA①エコー計測+②未定義行動レジスタ+沈黙 | 2026-07-31 | +30 / 1876 |
| 第71 | LLM 入出力ジャーナル(プロンプト全文)+REPLAY fail-fast+run_manifest | 2026-07-31 | +26 / 1902(S0=入力来歴はユーザー承認後に manifest へ追補) |
| 第72 | 機能レジストリ(repro_tier)+ランモード observe/journal/verify | 2026-07-31 | +30 / 1932 |
| 第73 | 真偽台帳ミニマル(fact+信念+伝播木+検証行動+漏洩検査) | 2026-07-31 | +32 / 1964 |
| 第74 | 規範化ステージ+coiner/institutionalizer+コホートタグ+ゼロ対照(IDEA③④+Part E1) | 2026-07-31 | +38 / 2002 = **「記録しないと失われる」観測点はこれで全て投入済み** |
| 第75 | ダンバー維持コスト(IDEA⑤) | 2026-07-31 | +21 / 2023 |
| 第76 | DT P0 軌跡バイナリ化 | 2026-07-31 | +27 / 2050(ブラウザ実機の目視は未=成果物パスあり) |
| 第77 | DT P6 追いかけ再生 | 2026-07-31 | +37 / 2087 |
| 第78 | ablate 4種+状態ハッシュチェーン+metrics_spec_hash+指標凍結 | 2026-07-31 | +63 / 2150 = **統合実装順 9/9 完結(T1〜T8 全達成)**。見積 13.5-15日を1日で完走 |
| 天候 W1-W2 | 気象庁930日凍結+較正生成器+weather.py 統合 | 2026-08-01 | — / 2231 系 |
| 第79 | Δt 不変化(毎分レート化) | 2026-08-01 | — / 2231 |
| 第80 | 観測チャンネル14本+σ_c 実測凍結 | 2026-08-01 | — / 2302 |
| 第81 | 閾値発火+同期バリア+認知イベントキュー | 2026-08-01 | — / 2348 |
| 第82 | watch spec+g/θ 更新則+F/N/P | 2026-08-01 | — / 2430 |
| 第83 | θ較正パイロット+発火観測装置 | 2026-08-01 | — / 2458 |
| 第84 | 環境フィードバック3規則 | 2026-08-01 | — / 2479 |
| 第85 | Perception/Intent 契約 | 2026-08-01 | — / **2536** = cognition-physics-plan 第79-85 + 天候 W1/W2 **全完結** |
| 3D 品質修正 | ビューワー品質(観察レイヤのみ・src ゼロタッチ) | 2026-08-02 | +19 / 2555(sim 側クランプは判断待ち 3D-U0) |
| レーンA | 3D データパイプライン3本(松A-1+竹-1+竹-2) | 2026-08-02 | +54 |
| 竹-3 | SFM 対壁斥力 f_iW + ξ 欠落バグ修正 | 2026-08-02 | +21 |
| レーンB | テクスチャ統合+梅塗り分け+80MB ゲート内化 | 2026-08-02 | +21 |
| 竹-4 | **P3 境界縫合**(physics.zones+ORCA 昇格+guarded ゲート+知覚翻訳) | 2026-08-02 | +36 / 2687 = 高精細3D×物理(松案)**全レーン完結**・P3 目標 8/11 を9日前倒し |
| 第90 | モデル人間らしさバッテリー(A〜E層+プラセボ・qwen3 実測=8b の D層分散潰れを発見) | 2026-08-03 | +21 |
| 保守 | ①**LLM 呼び出しハードデッドライン**(`llm/deadline.py`=タイマースレッドでソケット shutdown・`model.call_deadline_s:300`・4バックエンド・病的生成スタブで実発火検証)②xdist **loadgroup 直列化**(`subproc_run` 42s・フレーク根治)③`pool.relations_cap/episodes_cap` conf 化(dunbar 干渉の解消口・既定不変)④ゾーン通過の L1 位置=zone_gate 直線補間(補間と明示宣言)+所有中 node 更新(同席キーの古さ解消)⑤**exit_building×open_actions クラッシュバグ修正**(本選構成+実 LLM の where で `_phase_move` KeyError=実害を再現実証→ `not agent.building` guard 1行+回帰テスト。mock は where を返さず完全潜在化していた) | 2026-08-03 | +30 / 2738 |
| 第86 | **day_plan v1**(`cognition/day_plan.py` 1,147行・`planning.day_plan.enabled` 既定 false): 構造化スキーマ(act 12/place 15/purpose 10/priority×flex・contingency≤3・**新語ゼロ**=既存語彙棚卸し・reason 先頭=生成順の根拠つき)+検証→決定的修復→フォールバック3段(**再試行ゼロの設計判断**=25万体で最悪呼数2倍を回避・SchemaBench 非適合率 18〜36% はフォールバック常用経路と宣言)+ルール実行(場所解決=習慣/距離/営業・could+droppable 無料削除・must 危機のみ plan_exception→第81 fire キュー)+修復/後退のモデル別集計(バッテリー追加指標)。作用点3つ全て単一・OFF=RNG 3176=3176/呼数 119=119/golden 緑。根拠=ALBATROSS/ActivitySim/Doherty(CHASE)/MATSim/Roorda 2005 実測 | 2026-08-03 | +50 / 2788 |
| 第87 | **engaged モード**(`cognition/engaged.py` 839行・`cognition.engaged.enabled` 既定 false・fire 前提): 発火=点→**エピソード=区間**。pre_tick/update の2作用点で fire キューの規約を1つも迂回せず(新 generate 呼び出しサイトゼロ=k 非依存)・突入5条件+**話しかける側**(実測補修=初版は会話が110→7件に枯れた)・脱出=解消(closing move 双方=Schegloff&Sacks/ISO 24617-2・end 欄新設)/減衰(θ_out=0.5θ_in ヒステリシス+**min_stay**=dithering 文献で穴を補修)/ターン上限12(CAMEL の無限 goodbye ループ根拠)/プリエンプト→兆しメモリ1行・不応期・**両者 ENGAGED 会話 gate**・定型応答(LLM 呼ゼロ)。実測(40体2日)=エピソード **7.38/人/日(目標帯内)**・滞在30.4%(超過=レバーと較正方針を文書化)・day_plan 併用で must 危機→例外→プリエンプト→兆しメモリが端まで通ることを確認 | 2026-08-03 | +47 / 2835 |
| 第88 | **心モデル固定+三層知能**(`mind.py`+`llm/mind_router.py`・`model.mind.enabled` 既定 false): 心=1体1モデル誕生時固定を **(master_seed, agent_id) の純関数**で割当(checkpoint に割当表不要=resume/pool 再入場で自然復帰・stream mind_model/mind_tier=stateless 無風)・MindRouter 解決層(新バックエンドゼロ・cache は backend.name でファイルごと分離)・高解像度層 1〜5% は **traits 非依存の一様抽選が既定**(事前選定は問いの自壊=S-08 整合・traits 選抜は ablate 専用に分離宣言+manifest 警告)・agent→model_id を manifest/agents.json/L1 に必須記録(交絡の記録)+summary.mind に**因果効果ではない旨の confound_note を自動同梱**。ON実測(mock3+1)=journal 全走査で単一モデル逸脱0件・比率誤差<0.01 | 2026-08-03 | +38 / 2873 |
| 第89 | **プラセボ L1 3種**(`ablate.py` +527行・全て既定 false・strict・fingerprint_risk=known): context_shuffle(節種別 FIFO 輪から専用 stream 抽選=自分は候補に入らない・自分由来/物理/指示文は不触の理由列挙)/persona_swap(**隣接ペア対合=全単射でペルソナ分布完全保存**・奇数は自己写像)/context_sever(プレースホルダは記号1文字=合成文は語彙指標を汚染するため棄却)。作用点=build_prompt 末尾3行(全経路単一)。★検収の切り分け=**プロンプト盲 LLM プロキシ下で3種とも呼数148=148・L1バイト一致**=影響経路は「応答」ただ1本と確定(実ランの呼数ドリフト<25%は間接経路)。実測=3種が別々の因果を切る(shuffle は伝播-86%・swap は伝播+27%=文脈は正しいままの設計どおり)。同一軸3種の併用は ValueError(節の帰属が失われる)。**L0〜L4 梯子文書**([ablation-ladder.md](docs/research/ablation-ladder.md))=単調性検証の実行レシピつき | 2026-08-03 | +55 / 2928 |
| 第91 | **退行シグナル監視+縦横煙**(`observer/regression.py`・`observer.regression.enabled` 既定 false=列ゼロ): L2 14列(①行動の個体間分散 ②訪問エントロピー ③語彙エントロピー+2-gram 重複=**engaged 定型応答を除外し件数開示**=第87申し送り解消 ④発火率張り付き=fire ON 時のみ)・L1 のみから導出(agent.* 不読=観測がシムを変えない)・方向表 `REGRESSION_DIRECTION` 単一源。`detect_regression.py`=Mann-Kendall/Theil-Sen(**rolling 窓の自己相関で p が張り付く罠**→窓幅間引き+720step 未満は INSUFFICIENT)+分散崩壊診断(N 依存プロット・**帯の向きの誤りを実装中に自己修正**=崩壊は小 N が帯の上)+`--quick`(完結 part のみ・第77 `_open_shared` 流用=ランを落とさない)。縮小縦煙実走(200体×6日)=verdict OK・エピソード 7.86/人/日。★**25万横煙の前提を実測で確定**: ペルソナ100万件=充足/**在場25万は presence cap で来街者ゼロ化=日常が回らない**/メモリ外挿 316〜363GB=**単ノード不成立**(→DP-U3 の核心材料)・指示前提の誤り(rehearsal_pool10k に RSS 記録なし)を訂正 | 2026-08-03 | +40 / **2968** |
| 第92 | **サーベイ反映 SV-U1 ◎5項目**(B1〜B4): B1=事前登録に**前文「主張の境界」**(Wu et al. 2025 の3基準対応表つき・承認対象)+報告書テンプレ `observation-report-template.md` 新設(ODD 2020 対応表・micro/macro/system(計算資源) 3節+「何と比較したか/できない理由と代替」必須欄・TRAILS 用語衝突注記・S-05/08/15/17 宣言空枠)。B2=事前登録 §3-F **stylized facts**(主判定=**入力に埋め込まれていない4法則**: F5バースト性/F6接触時間の裾/F4滞在時間の非指数性/F7次数の裾=dunbar OFF 条件・参考=EPR由来の移動系は循環と明記・F10/F11=N不足で**検定不能と明記**)。B3=`calibrate_report.py` に**個体間分散表**(CV/Gini/top10%+**分散比=sim CV/現実CV下界**・agent×day 単位・√((1-p)/p) 片側バンドの非対称性明記)+e-Stat 表1-1 を一次確認(p·m≒総平均の整合検査20分類)+provenance JSON 2件(未取得は values:null=捏造拒否)。★初検出=**移動の分散比 0.662<1=下界すら下回る「分散が確実に痩せた」行**。B4=`ablate.prompt_paraphrase`(S-16・既定 ""=OFF・**凍結ルックアップ表** data/prompt_paraphrase_sets.json 単一源=LLM生成禁止・v1語彙/v2文体/v3複合/v4+統語・単一パス同時置換・プラセボ3種と**相互排他**・propagation_off 併用 ValueError・fingerprint_risk=known・sha256 を manifest・summary に適用実績)。50新テスト(保護語検査・呼数完全一致・置換連鎖なし固定) | 2026-08-05 | +50 / 3018 |
| P4-1 | **歩行物理較正ハーネス**(reference/physics_bench・src ゼロタッチ=P2ベンチ決定論ハッシュ6件MATCH): Jülich 5データセット全取得(146MB→gitignore・派生CSV 1.44MBのみコミット・CC BY 4.0帰属・metadata JSON で corridor5=幅5m×長18m/HERMES published 5run/単位cm・m混在/25fps例外を一次決着)+Kladek当てはめ v_f=1.414/γ=1.656/ρ_max=5.055+ボトルネックシナリオ(w=0.8〜5.0m)+RiMEA T4/T16型指標+ExtendedSFM(長距離第2項+λ可変+C¹テーパー・a2=0で既存とSHA-256一致)+calibrate.py(粗36点→NM 26評価・33.4分)。★**λ先行実験=研究文書仮説を実験で棄却**(λ 0.5→0.12 で非単調性2倍以上悪化=λは絶対値に効き単調性に効かない→据え置き決定)。推奨 (A2,B2,λ)=(0.119, 1.890, 0.537)・dt=0.05=包絡線内率 0.60→**0.80 ✓** だが単調性・±20%帯・J/w は不合格=**P4-3(Tordeux型 V(s) 間隔ベース)が必要と分岐確定**。★新規発見=**壁斥力の過剰クリアランス**(WALL_A/B が片側+0.15m 要求→w≤0.9m 開口は単独歩行者でも通過不能・J/w 水準が実測の 1/2.2〜2.8 の主因候補)・受入は大域でなく局所測定密度(2×2m 区画・過渡20〜35s破棄) | 2026-08-05 | +0 / 3018(ベンチ内 self-check 3件) |
| IF-A | **因果対+穴2件**(`provlink.py` 新設・`observer.llm_link`/`planning.day_plan.use_contingency` とも既定 false): ①行為イベントへの **(llm_call_id, role) 刻印**=PROV wasInformedBy 辺(role 語彙は l1b の purpose と同一集合=**新語彙ゼロ**・logger 側刻印で tools/P2/verify/goods を**1行も改変せず**巻き込み・刻むのは行為者自身のイベントのみ=(call_id,agent_id,step) で 1:1 join・plan_block は朝計画の call_id を role="plan" で参照・OFF は一時キー不生成=バイト一致を構造保証)②day_plan contingency 消費(条件7種全実装=前提機構 OFF は「現象が存在しない」の False=片側倒し明記・対処5種=skip/postpone/go_home/swap_indoor 固定表/shorten・評価点は plan_action 1箇所のみ=_sweep 二重適用の振動回避・先頭一致1回)③_apply の plan/recall/reflect 明示分岐(ON のみ fallback{misrouted_action}=llm_health 分子に自然合流)。41新テスト(1:1 join parquet 検証・no-fingerprint OFF/ON プロンプトバイト一致・resume==straight) | 2026-08-05 | +41 / 3059 |
| P4-2/3 | **物理較正の本体昇格+V(s)+壁較正**(`physics.sfm.{far_field, v_of_s, wall}` 全て既定 OFF/現行値=**恒等5証明**: 既定は派生クラス自体を作らず type is Crowd/conf 3ブロック削除ランと L1 バイト一致/軌跡 SHA-256 一致/src とベンチのバイト一致/golden+P2ハッシュ6件MATCH): 較正 15.5分で最良 (T,ℓ)=(0.482s, 0.297m)・B_w≤0.06 で w=0.9m 単独通過。★**測定学の発見2件**=(i) RiMEA 2×2m 区画の物差し是正(流れ方向2m×全幅)だけで現行既定が C 0.60→1.00 (ii) **ρ_global≥2.0 の FD 点は壁貫通で個体が消えた系の測定だった**(ρ=3.0 で 90/180 脱出=P4-1 の+2.9倍は汚染込み・B_w 縮小では直らない=接触項/v_max クリップ再設計の別課題)。是正後 far_field ON で **A/B/C 合格・D(J/w 水準)未達**(壁主因仮説は部分否定・残候補=接触項不在/τ/v0分布)・**V(s) 限界効用ほぼゼロ=P4-3 起動条件は覆った**(実装は既定OFFで保全)。14新テスト | 2026-08-05 | +14 / 3073 |
| IF-B | **拒否通知の段階 conf 化**(`reject.py` 新設・`cognition.rejection_notify: "silent"` 既定=現行完全一致): 3水準 silent/memory(定型文1行を記憶+L1 `action_reject`)/engaged(+fire キュー INTERNAL 前倒し・engaged OFF は memory に L1 まで完全一致で縮退)。対象=監査 §2-C の無音拒否8種(出店資金不足×2経路/敷金不足/空き住戸なし/交際相手不在/経路不能/verify 空振り3種)・**verify は凍結 truth_ledger を1バイトも触らず** engine 側で belief_verify の outcome 1語だけを読む方式。定型文=(kind,reason) の純関数・数字/時刻/実験条件ゼロ(**7実験条件で文面同一バイト列**をテスト固定=no-fingerprint)。day_plan 失敗理由の REPLAN 1行注入+**降格**(再計画成功・日跨ぎで消える=Masicampo & Baumeister。根拠は Ovsiankina 効果=Zeigarnik は2025メタ分析で否定済み)。対象外3件の理由明記(envfeedback=明文規約/閉店=選択前フィルタ/config ゲート=機能 OFF の世界に矛盾)。★副産物=**第87 脱出条件(1)の実バグ発見**(`fallback=""` に `is None` 判定で note_resolved が恒久不発火)→ **Fable 直接修正1語**(`if not fallback:`)+回帰テスト(engaged ON の挙動が設計文書どおりに復元・第87実測値は 8/15-16 再較正で再測)。31+1新テスト | 2026-08-05 | +32 / 3105 |
| IF-C | **噂オブジェクトの一般化+stifler**(`rumors.py` 新設・`information.rumors.enabled: false` 既定・provenance/labels は**無変更**=既存 ItemStore API のみで実現し無変更自体をテスト固定): 誕生=公共の構造化イベント3種(event_host/venture_open/enforcement・当事者+同席目撃者が初期 knower・**源の自由文は1バイトも読まない**=(源種,場所名)の純関数文面・partner_formed/relation_break は gossip と二重になるため既定外)・伝播=既存会話相乗り(**発話本文に非注入**=聞き手の記憶1行のみ・on_talk が本文を引数に取らないことを AST 固定・ON/OFF で generate 呼数完全一致+プロンプト差分が記憶3欄に閉じることを機械固定)・**MT 型 stifler**=既知の相手に語った回数閾値で黙る(決定論・新確率ゼロ)・忘却 TTL。L1 rumor_born/rumor_stifle+`analyze_rumors.py`(OASIS 流 scale/depth/max_breadth+DK/MT 理論値比較)。★実測の発見=**stifler ON の方が総伝播量が増える**(208 vs 99=最古の噂が黙ることで語り枠が次の噂に回る「ポートフォリオ回転」)。36新テスト | 2026-08-05 | +36 / 3141 |
| IF-D | **痕跡=場所イベント履歴のスティグマジー**(`traces.py` 約460行・`world.traces.enabled: false` 既定): 演算は**集約と蒸発の2つだけ**(propagation はコード不在=`propagat|diffus|spread|neighbor` 識別子ゼロ+city/graph 不参照を AST 固定・Parunak factor=0)。源5種=enforcement/gathering(event_host)/opening・closing(venture・persistent)/trouble(crime・nuisance=transient 半減期18step)・**chance_event は源にしない**(私的事象=場所の性格でないと理由明記)・3階層すべて実使用をテスト固定(単一TTL退化防止)。蒸発=日境界1回(dunbar 前例)・経過 step から計算で resume 跨ぎ同値。観測=trace_line 1行(最強1件のみ・「場所:」行の直後・**当事者+同席目撃者には出さない**=名簿は集約時のみ記録・観測は状態を1ミリも動かさない)。ablate.propagation_off では遮断しない(誰の文でもない純関数テンプレ=crowd_line と同じ線引き・根拠明記)。契約列挙テストは追随不要(材料側=_gather_material 配置のため)。42新テスト | 2026-08-05 | +42 / 3183 |
| IF-E | **経済会計=検査先行**(`analyze_accounting.py`+39テスト・**src/conf/registry ゼロタッチ**=読み取り専用): Caiani 2016 流の検査①貨幣保存(部門別)+②フロー行列ゼロ和。実測=**家計の財布の中では金は消えていない**(残差 −0.5円=丸めノイズ)が、**ゼロ和の漏れ 71.8〜96.0%**=「財布から出た金の受け取り手が世界に存在しない」(spend の店舗側・org は残高の器を持たない)。revenue_est 乖離 **30.9倍**+serve の 220/222 がスタッフ不在で org 特定率が極端に低いことも発見。★**フェーズ2(接続)は実測を根拠に見送り**=漏れは5経路に分散し一意帰着せず・revenue_actual 列追加では残高が1円も動かず受入条件(保存則の改善)を原理的に満たせない→ 案A 観測のみ/案B org 会計主体化/案C rest-of-world 宣言 の3案を判断待ちへ(=IF-E2)。監視装置2本(漏れ族の既知リスト閉包+金額キー未分類種の検知=金の経路追加を fail で検知)・回帰固定2本 | 2026-08-05 | +39 / 3222 |
| OBS-U2 | **Δt=1分の準備完遂**(設計調査+実装・2実行役リレー): ★設計調査の実測=**Δt=10 では salience 発火0件=驚き駆動が原理的に観測不能**(Δt=1 で103件・CogQueue の基本周期<Δt が原因)・LLM 呼数は×2.2〜2.4(=抑圧の解放そのもの)。実装=①**resume 二重適用バグ根治**(load_config(apply_dt=False)・負の対照で有効性実証・Δt=10 はバイト無風)②A級焼き付き9件是正(調査7件+**同型の穴2件を実装中に追加発見**=venture_close×144・流入通勤者初日到着//10。全件「Δt=10 数値恒等」テスト固定・clock.day() 不使用で golden 保全)③registry run.dt_min affects_k=True 訂正 ④B級=scenario_params 変換+棚卸しCI拡張+checkpoint_every 未宣言の補完 ⑤conf/smoke_dt1.yaml(「変換される分類のキーは書かない」鉄則を機械検査化)。Δt=1 24step スモーク=salience 2>0。★最大の残リスク=σ_c は Δt=10 で測った値(Δt=1 の発火率絶対値は直接比較禁止と明記) | 2026-08-06 | +25 |
| SV2-A/B | **サーベイ残12項目**(S-11 は本選後・2実行役リレー): SV2-A=事前登録に §1.5(S-12 三層)/§3-E'(S-13 対応表)/§3-G(S-05 seed分散分解)/§3-H(S-08)/§3-I(S-09)を承認対象マーク付きで追記+報告テンプレ §7.2/7.3/7.4 充填+judge.py にサーベイ §4.4 引用。★実測訂正=**channel は6種**(event=4.3万件を発見・落とすと offline 伝播14%過小)・dm は全体の0.03%=「online 層の実体はほぼ SNS」。SV2-B=解析7本新設(seed_variance/persona_consistency/layers/org_form/mas_failures/ipf_fidelity/stereotype・全て凍結ゼロ抵触・77自己検定)。実走=S-14 SRMSE 年齢0.0107/性別0.0051/職業0.0203・S-10 は6/14様式判定(FM-3.1 発足後無加入48.8%)・測定学の罠2件を検知機構化(FM-2.6 の97.4%は語彙不一致=NAME_SPACE_MISMATCH・強連結グラフの GRC=0 は DEGENERATE 標識)。★**S-05 実測=既存ランで主張可能な指標 0/10**(seed 分散が条件差の12〜1000倍=反証条件④(a) が実発火→本選前に seed 本数の判断必要) | 2026-08-06 | +77 |
| IF-E2 | **org の会計主体化+RoW 概念部門(案B)**(`economy_sfc.py` 814行・`economy.org_accounting.enabled: false` 既定・[リサーチ](docs/research/ifE2-org-accounting-research.md)準拠): org 残高=**スカラー預金1本**(Lengnick 前例)・初期値=σ×月次賃金・賃金=残高から+**自動当座借越**(破綻なし=Poledna AND 条件は将来宣言)・**RoW=明示部門**(チャネル別分類・来街者財布=輸出・閉じた不変量 Σ残高+RoW=const)・税=public_budget 一本化・利息/供託金の対称化・FinanceLedger サイドカー+analyze_accounting 拡張(検査①が**全部門 PASS**)。★ON 実測=**ゼロ和の漏れ 96.04%/92.01% → 0.00%**・総マネー保存の振れ 2.3e-15。正直開示=金が閉じた≠街の自立(輸出代金が域内消費の38倍・帰属不能23万・UNCOVERED 4種を summary に必ず刻む)。受け手解決は**台帳静的索引**(スタッフ経由は実測 220/222 不在で機能せず=逸脱理由明記・多義は RoW 帰属で開示)。★同梱=**既存 checkpoint 欠陥3件の修復**(Government/Bank/VCFund 未保存+`_work_day` 未保存=mid-day resume で org_output 33→44 の二重記録バグを実測・修正)。32新テスト(プロンプト/呼数の ON/OFF バイト一致固定=no-fingerprint) | 2026-08-07 | +32 / 3357 |
| 第98小粒 | **持ち越し小粒7レーン並行**(実行役A〜G+R・新挙動は全て既定OFF or 解析側): **A=resume 整合の全数監査**(AST で `sim.*` 代入を全数走査→未保存の日/期ガード**15件**+付随状態**5族**(災害・議会・卸/宅配・OOH・内面起動)を発見し checkpoint 30キー追加=旧 ckpt 互換。★実測=chance_event が resume で **29→44件に二重発火**・worldview 規範窓消失→修復後 straight と全層一致。pool dehydrate に噂(知った順=決定論反復順を保持)+`_phys_body` を**非空時のみ**搬送・ゾーン所有は「その旅に固有」として意図的非搬送)・**B=IF-E2 UNCOVERED 4種の完全接続**(rule_bonus=区歳出化・★exec_ratio を事後記帳に掛けると差額が無から生まれる罠を回避/crime=SNA 2008 **§3.98 逐語**準拠の非取引 K5 部門=「窃盗は輸入だった」になるので RoW と混ぜない・加害者入金なし/chance=RoW 2チャネル/b2b=ON 時 org 預金の実移転・買い手一意率4.5%は正直開示。`UNCOVERED_KINDS`=空・検査①全部門 PASS)・**C=llm_health 3列の analyze_sweep 接続+噂混線オーバーレイ**(凍結関数そのものを2回呼んで差分=指標を再定義しない・metrics_spec_hash 前後一致を機械確認。★噂は transmission_novel_rate を**押し下げる**=混線は水増しとは限らず引き算補正は誤り)・**E=3D エクスポータのストリーミング化**(旧実装逐語コピーとの出力 SHA-256 一致 **12通り**・RSS −11〜14%・★既定経路のピークは JSON 文字列でなくイベント dict と実測)+**estimate_substeps 新設**(シム内真値との突合 0.0026%・★総サブステップは体数で伸びず**飽和**=実用上限 ゾーン数×1440×12000)・**F=3D-U0 floor クランプ**(`world.floor_clamp.enabled:false` 既定・表示側 encode_indoor_w の規則を1バイト単位で写して格子一致固定・AST で代入点網羅・golden 一字一句一致・ON はプロンプト loc 経由で世界分岐と明記)・**G=DP-U3 層別クォータ**(`pool.tier_quota.enabled:false` 既定・44行・純整数の最大剰余法=乱数追加ゼロ・OFF=旧実装逐語コピーと完全一致・ON=第91破綻ケースの再現→解消・resident も比率で切られる代償を明記)・**Fable 直修=cp932 実バグ**(`guard_or_die` の ⚠ が非TTY Windows で UnicodeEncodeError=解析落ち→`_safe_echo`)。**+RW-U1 リサーチ**([rw-data-acquisition.md](docs/research/rw-data-acquisition.md)=全ソース一次エンドポイント実接続・**無料のみで構成可**・★アメダス保持10日=本選中の日次取得がハードデッドライン・★渋谷区人流 Location Analyzer は CSV 機械取得可=既存文書の記述を覆す) | 2026-08-07 | +179 / **3536** |
| 第99 | **wave2=25万本線の基盤固め6レーン**(実行役W2-1〜6+Fable直修): **W2-1=RWフェッチャー実装**(`scripts/rw_fetch/` 9ファイル・HTTP出口1点集約・**鍵は全出口スクラブ**を機械検査・保持窓4段 URGENT/LOST・実疎通=アメダス/WBGT/ODPT/渋谷区人流・★**バックフィルでアメダス 7/28〜8/6 を消失前に回収**)・**W2-2=解析25万対応**(`l1_stream.py` 新設=kind の Arrow レベル絞り込み+step の row-group 枝刈り・5本移行=出力同値固定・実測 **252倍**・watchdog の 204 GiB 展開→定数化・凍結4本の破綻見積=beliefs **4.2〜6.4 TiB** HARD/specialization HARD/norms SOFT/stationarity SAFE)・**W2-3=Δt 対応31本**(`run_dt.py`=解析側 Δt の単一の源・「黙って仮定しない」・★HEAD 版との実ラン出力 **sha256 全一致16ファイル**・凍結2本の Δt 直書きは判断待ちへ)・**W2-4=計画遵守の突合レイヤ**(`analyze_plan_execution.py`=対応表を発明せず day_plan 実装を import・PROV join/解決テーブルの2経路・★台帳の「266中5」は**カテゴリ vs ノード名の測り違い**と判明・★**学業ブロックが本線地図で解決不能**(education 1件 vs school 68件)を発見→ **Fable 直修=MAP_FALLBACK_CATS**=fallback 無しカテゴリは照会1回のままを機械固定)・**W2-5=噂誕生の遅れ解消**(★指示の前提を訂正=遅れの正体は born_step でなく**伝播の可能開始点**・birth_scan を会話ループ各回直前へ=provenance スコープ外の構造保証で思考 ID の捏造を防止・min lag=0 実証)・**W2-6=finalize 有界化+会計25万**(`observer.finalize.streaming: false` 既定=parquet バイト一致・ON=行内容完全同値でピークが row-group 1個・実測 370→26 MB・★**ON の方がクラッシュ安全**(tmp+os.replace)=「25万×10日は OFF のままだと書き終わりで落ちる」の根治・会計は L3 全載せ 361→17 MB+座標 32 GB 分の復号全廃=**答えの dict 完全同値**を修正前実装との突合で固定) | 2026-08-07 | +251 / **3787** |
| 第100 W3 | **凍結3本の最小修正(ユーザー承認・8/15 凍結の正ハッシュ確定)**: analyze_beliefs=`l1_stream` の kind 絞り読みへ(25万で 4.2〜6.4 TiB→有界・旧述語 `belief_events` を**二重掛け**して絞る集合は旧定義が最終決定)・analyze_norms/analyze_specialization=Δt 直書き解除(W2-3 と同じ「定数は残し入口だけ run 由来」流儀=渡さなければ完全同値)。★**判定式ゼロタッチを AST で機械証明**(beliefs 9/9・norms 8関数・specialization 22/23 が dump 完全一致・`first_day_features` は定数→引数の機械置換で本体一致)・Δt=10 は逐語温存レガシーと **json バイト同値**・Δt=1 で norms 初日窓 1440(first_day 誤読 15→1 が直る)。新ハッシュ `79a2e549…010d0f`(Fable 独立再計算で一致確認)=**8/15 事前登録凍結の正・以後不触**。ハッシュのリテラル固定は tests/ に存在しないことを全数確認。副次=beliefs が part 群(走行中ラン)も読めるように。残=beliefs `--bin-steps` 既定24のみ(CLI 上書き可・任意)。**+RW 運用開始**=タスクスケジューラ `shibuya-rw-fetch-daily`(毎日12:00・StartWhenAvailable)登録 | 2026-08-07 | +17 / **3804** |
| 第101 wave4 | **持ち越し小粒の掃討6レーン(W4-A〜F)+直修2**: **A=resume 完遂**(spark_roster 二重記録・観測レンズ4本=mid-day resume で **L2 9列**が食い違っていたのを解消・worldview 走査+★**日中 flush で未走査区間が永久消失する既存欠陥**を HEAD A/B で確証し `absorb_before_flush` で根治=分割 straight が plain と全層一致・undefined_action 族はプロセス内カウンタ族として正直に見送り宣言)・**B=経済/物理/較正**(K5 日次 L1=`row_flow` に累積 `k5_total`・`max_sub_steps`=step_seconds 導出で Δt 追随=Δt=10 は厳密 12000・σ_c の dt 来歴照合=データ不触で読み手警告+manifest 3キー・★較正ラン `runs/zone_smoke_p99` 誕生=zone_gate 142件で**実測外挿モード初成立**=10日×1万体 13.59M サブステップ/壁時計 40.5h の見積が出せる)・**C=ビューア Δt**(make_viewer 15箇所+JS 21式=4トークン化で構成的バイト同一・実ラン5本 15/15 sha256 一致=**C級 Δt 対応これで完了**)+live_viewer 有界化(L1 part の payload 込み2回全読み→1回逐次・実測 RSS **1230→242MB**)・**D=研究解析 19/19 本 l1_stream 移行**(実ラン2本×成果物23本 sha256 全一致・WANT_KINDS ミューテーション16パターン検証・★build_panel の資産追跡=kind 非依存 payload 読みの**静かな破損を未然検出**し全 kind 1パスで回避)・**E=サイドカー finalize 横展開**(mixin 括り出しで既存18テスト無改変・conf キー増ゼロ=1判断で6ファイル同一モード・隔離ベースライン2ルートで既定バイト不変を実測・正直な実効性評価=indoor_tracks は OFF concat ピーク**約124GB=L1超え**)・**F=計画観測強化3点**(agents.json work_node=機構ゲート・`plan_block_start` に node・`plan_block_*` に添字→ work_unknown **8→0**・台帳再生の多義が構造的にゼロ)・**直修2**=detect_emergence の決定論バグ(タイブレーク欠落=同一ラン2回で 297 中 51 件の順序変動→ term 追加)+run_manifest に dt_min(run_dt の第2の源が実際に機能) | 2026-08-08 | +207 / **4011** |
| PUB-U1 | **公開ミラー同期完了**(Fable 直轄・ユーザーが Allow force pushes を一時 ON): `publish_public_mirror.ps1 -ForcePush` で新除外セット(docs/**・data/**・env/**・台帳3md・reference/2d-fire-sim)適用の履歴を forced update(`954ee76→260f2fa`)。検証=スクリプト内機械チェック(除外パス残存ゼロ・旧メール残存ゼロ)+公開側実物確認(ルートに docs/data/env/台帳/h.txt 不在・最新コミット sha 一致・作者/コミッタとも noreply)。以後は除外セット不変なら fast-forward push に戻る(force 不要) | 2026-08-08 | — |
| 第102 | **アクターモデル移行 Wave 1(4レーン並行・全て既定OFF=golden不変)**: **①因果台帳 P0+P1**=`observer/causality.py`(197 kind 全分類 device80/agent75/physics20/boundary18/schedule2/natural2・患者索引上書き・4分類射影)+`scripts/analyze_causality.py`(ゼロタッチ事後分類器=既存ランに適用可・l1_stream 経由)+Event に cause_type/actor_id 2列(`observer.causality.enabled:false`・provlink 構造=OFF 分岐到達不能)。★充填優先の精緻化=行為スコープは表も agent と言う場合の確認に限定(素朴なスコープ優先は行為内の制度イベントまで agent 帰属=**帰属率の水増し**を実測で発見・回避)。相互検証不一致0。**②デバイス層 P2 土台**=`devices.py`(DEVS 契約+__setattr__ 監査・`world.devices.enabled:false`)+**FaregateArray**(実測較正 60人/分/通路・決定論 FIFO・乱数ゼロ=AST 固定・envfeedback 規則2と排他を両方向テスト)+SignalGate に device_id(タイミング不変=既存16テスト無改変)。★車両/歩行者信号の3点矛盾を定量化(90s/hash 0.35-0.55 vs 実測140s/0.664)。**③性能回収 P5 前工程**=実測 **−11%/step**(c 0.000311→0.000276)。★networkx ディスパッチ回避が実は壊れていた(2層ラップ)・真犯人は A* ヒューリスティックの node_xy 75万回(float 完全一致証明で直読み化)・_lynch 事前計算・conf ホイスト。純リファクタ=conf 鍵ゼロ乱数ゼロ。**④店員被覆 P3b 前提**=★台帳記録の真因は半分(**本当の真因=org 台帳ノードが POI 非一致**・バインド済スタッフの76%が客の来ない場所に立っていた)→POI 保持ノードのみ受理+既存対応表再利用。実測=1,482人で非スタッフ serve **84%→66%**(少人数は密度問題と正直開示)。副作用開示=ON で spend 統計激変・pool 経路 org_id 永久 null(判断待ち登録)。**Fable 直修2**=timeconv 棚卸し1行+★viewer テスト2本(test_viewer_indoor/test_org_ui 同名テスト)の潜在欠陥(HEAD コピー実行ハーネスが 7b7072d コミット時点から壊れていた=コミット後初のフルゲートで発火)をリポ同形レイアウトで同型修正 | 2026-08-09 | +92 / **4103** |
| 第103 | **アクターモデル Wave 2(4レーン並行・全て既定OFF=golden不変)+README確定**(ミラー同期は保留): **A=P4境界計画**(`planning.day_plan.boundary` — 朝の計画ブロックに boundary 明示フィールド=despawn/respawn 予定表・新機構ゼロ・圏外通勤の blake2b 決定論指定・帰還 entry_min 誤差ゼロ・人日保存則・圧縮記憶1行。★圏外イベントゼロは既存フィルタで成立を行番号検証+「完全な L1 沈黙ではない」発見=受動イベント許容リスト+行為13種ゼロ固定)・**B=P3a 駅員車掌**(`transit_staff` — envfeedback 規則1を純関数5本へ括り出し**同じ関数を両者が呼ぶ**=定数重複ゼロ AST 固定・既定で遅延値 float 完全一致「誰が決めるかだけ変える」・unstaffed 正直記録・東京係数 +15人/車両≈+1s conf 化)・**C=因果×デバイス統合**(Event 第3列 device_id・デバイススコープ4種・★DEVICE_STAMPABLE=誤帰属38行を実測して防止・運休= TransitOperator δ_ext 経由でビット一致・**信号統一** `world.traffic.signal_from_crossings` 既定OFF=車両赤比率を横断歩道表から導出 140/37/10→0.664・OSMノードID厳密一致のみ 23/69 正直開示)・**D=SoA 基盤**(`engine/soa.py` 未配線・世代付きID 40+23bit・決定論 pending-writes 明示 seq・Philox 二重実装相互検証+チャンク11通りビット同一。★250k 実測=想定5演算 c≈4.0e-07=**目標の500分の1**=勝負は載せ替え範囲と確定・配線リスク3件を行番号特定)。レーン間相互修正(地名2・シーム数・分類先回り)+Fable 直修2(log_every_steps の timeconv 分類・plan_boundary の世界読取宣言登録) | 2026-08-10 | +185 / **4288** |
| 第104 | **アクターモデル Wave 3(3レーン・セッション上限中断→続投完遂)**: **①パルス流入**(`world.inflow_pulse.enabled:false`・conf キー1個 — 到着二峰 draw 不変で**時刻表スナップのみ追加**。★発見の連鎖=実ダイヤは3スカラーに潰れ9路線合成では無効→**路線別スナップ**(最長共通部分列≥3字・照合率12/28)で平均シフト14倍→小隊は人口/スロット比の問題= N=300 で最大6・本選規模で効く設計と結論。★副産物=8:30 フォールバックの計測汚染発見。プール経路+enter_area ペイロード接続)・**②device_id 完結**(7/7= traffic:ambient/pos:*/org:*/train_op 列化/commerce:pricing/gov:tax・payroll/bank:main。**タグ行 12→449・-1 行の 94.5% が装置名保持**・9列 L1 バイト同一=純観測の証明。★原則的スキップ明文化=家賃(RoW 宣言と矛盾する装置を発明しない)・関係力学・雇用主不明 wage。stamp() 自己検査=構造的に誤タグ不能)・**③境界較正データ**(rw_fetch 2本+`build_boundary_counts.py`+研究文書。★**駅別×時間帯の無料表は存在しない**→水準×形状分解を正直に文書化。★渋谷 JR 乗車の 65% は街に出ない乗換=45.3万人/日・ODPT includeAlighting で二重計上罠を構造的封じ。counts 1,050行・データは gitignore 内) | 2026-08-10 | +123 / **4411** |
| 第105 | **Wave 4-α 現実被覆 Day 1(4レーン並行・全て既定OFF=golden不変)**: **①夜間解禁**(`world.night_economy` — 深夜シフト構造解禁(close<open=日跨ぎ)+生成側=リビルドで **L2 の 7.0% が夜勤者**+終電後のネカフェ/サウナ避難動線。★v7 はコンビニ識別不能→subcat パススルー先行敷設=**v8 で自動活性**+トリップワイヤーテスト)・**②車内空間**(`transit_interior` — 路線別実編成(銀座線 6両16m別建て)+車両選択ロジット簡約の正直申告(恒等定数項は削除)+背景乗客=正直な整数(65%乗換客)+ゾーン埋まり実測 52/25/23% vs 研究 49/31/20+**会話ゼロを generate 呼数一致で機械固定**+車掌40人生成。★発見=familiar strangers が決定論的すぎる=ジッター発明拒否で判断待ち)・**③ゾーン実戦投入**(`conf/zones_shibuya.yaml` — スクランブル ORCA=実信号 140/37/10 と同一オブジェクト+ハチ公前+センター街 SFM・far_field のみ ON=ベンチ A/B/C 合格の唯一構成。★地下ノードが地上赤信号を待つ幾何罠→ layers フィルタ・待ち分布 {20,40,60,80}s=理論一致・ON コスト n=1000 で物理25分/日・L2 列意味論ズレを文書化=IF 判断待ち)・**④街路の顔**(`street_life` — 新職業149人・路上生活者80=公式調査側に固定・客引き=ナイトライフ L2 の決定論部分集合(条例の雇用主対象に整合)・警告→過料5万→冷却・**尊厳規約の機械固定**(語彙スキャン+crime/nuisance 不結線検証+支援→住居移行)。★測定が設計を2回修正(支援員固定ポストは接触0件→巡回化)。L1 負荷 0.05%) | 2026-08-11 | +168 / **4579** |
| 第106 | **Wave 4-β 現実被覆 Day 2(4レーン・セッション上限中断→続投完遂・全て既定OFF)+★救急のエージェント駆動化**(ユーザー新要件: 倒れる(physics・既存 sick 状態)→**近くの人が通報**(ems_call=行為が原因)→通報に応答して出動(不在は unstaffed)。健康OFF=救急ゼロの依存を正直宣言): **①都市運営**(`city_ops` — 交番=警察官を実在8箇所へ・ゴミ収集(区の曜日表)・納品運転手化(方針=device のまま・運転=agent の dwell_decision 線引き・数量バイト同一証明)・夜間清掃・自販機は v8 でも POI ゼロ実測でスキップ+トリップワイヤー)・**②地図v8**(★attic 再取得で**道路グラフ v7 バイト同一**=派生資産の破損ゼロ。dedupe 修正で **POI 2,337(+362)・コンビニ 9→93・全11サブカテゴリ非空**・ネカフェ=汎用名パッチ)・**③ビューア**(λ展開=街路固定フレーム+C0 ブレンド(横飛び8.7倍改善)・**屋内/車内非描画=新ランの既定**(トライステート・旧ランバイト不変)・建物クリックで内部表示)・**④センサス較正**(★最大の歪み=ビルメン・人材派遣が実態の 0.40 倍・`--census` で ±0.1pp 一致の較正台帳+ナイトライフ職場254社・新職業13種の賃金接続(演説者=公選法で無給))。**Fable 直修4**=lodging の love_hotel 除外・conf 注記実数化・serve_by_cat service 行(設計済み seam の完成)・★経年 mojibake「研究доク」3箇所を初検出→修正 | 2026-08-11 | +145 / **4724** |
| 第107 | **身体と事件レイヤー H1〜H5+H2 全6レーン(5並行+1続発・全て既定OFF=golden不変)**: ユーザー4決定(§6原文=①死は実装・現実量のみ ②chance廃止承認「運は世界のアルゴリズムでなく人の行動から」③全部実装・H4エージェントドリブン ④保険=命名RoW)を受けて即日実装。**H1 身体**(`health.severity` — S0〜S4状態機械=sick bool世代交代・発症5チャネル(急病/熱中症=WBGT閾値・都データ検証可/急アル=飲酒滞在時のみ/外傷/OHCA=年齢帯レート)を**1人日12本固定長uniform**の新stream 1本で(分岐が消費列を動かさない)・frailty=通院者率×seed純関数・presenteeism 0.45(S1は出勤)・EMSトリガ=`_collapse_gate`ハッシュ→**S3/S4遷移そのもの**へ世代交代(docstring予告の履行)・傍観者較正 P(行動)=n=3で0.87/危険はα=0・見かけvs確定重症度分離(搬送52.8%軽症)・**死=despawn同型退場+L1 1行**(現実量=搬送1.3%・OHCA生存10%)・★sick_untilプール回転バグ修正同梱)・**H3 遺失物**(`lost_property` — 完全内生ループ=確率事象は「落とす」1回だけ・拾う/届ける/着服は乱数ゼロの純関数・**品目別返還率が実測bandに着地**=傘1.15%(≈1%)/財布70.2%(60-80%)/携帯87.5%(87%)・監視者ありで届出率66.7→78.9%=RAT語彙・貨幣保存=holdバケツで毎step誤差<1e-6・報労金5-20%=遺失物法28条)・**H4 対人**(`incidents_interpersonal` — theftのRAT収束化=stream "crime"消費列1バイト不変で枝だけ差し替え・**「共在なければ事件なし」を4重固定**(AST2種+知覚半径0で発火確率1でも0件+監視者は制御フロー遮断)・喧嘩=酒×密度×閉店(+16%/h)・通報層=乱数ゼロ内生(被害者は盗られる瞬間を見ていない→非緊急39%)・場所集中HHI 4.8倍・反復被害77.5%が創発)・**H5 残族**(`incidents_env`+`facility_devices` — 火災=薄レート+73%器具帰属+**重度ぼや175:全焼0を同時較正**(既定で全焼は1件も起きない)・EV閉じ込め=DEVS摩耗+月1保守+保守員30-80分・群集=**生成しない**=SFM密度4/6/13閾値跨ぎ自体をincident化・交通=曝露積で実在横断者のみ・停電漏水=SAIDI 13分でskip宣言・既定較正の実測=60体1日で0件=「今日は何も起きない」が正しい)・**H2 搬送医療**(`medical` — v8病院7へ搬送・入院=lodgingテンプレ・**金の三本足**=①公費45,000円/件(区→RoW ems_operation)②3割=_spend払い先を実ノードへ是正(★黙ってRoWに漏れていた監査発見の修正=対照テストで機械固定)③保険7割=命名RoW `insurance_reimbursement`・貨幣保存drift 0件/200step・clinicヒント是正(v8で7病院が汎用serviceに落ちる)・**統合結線2**=health.on_injury公開API(H4喧嘩/H5火災交通の負傷が身体層へ・onset streamは不触)+city_ops.request_ems公開シーム(H5の私的ヘルパ依存を解消)・ひっ迫=既存当直機構で内生(全隊出動中はunstaffed))。**chance_event懸案=決着**: 機能代替完備→本選ONセットで`chance.enabled:false`運用退役・コード削除は本選後(golden保護)。**Fable直修4**=timeconv 3キー(H4)・floor契約に medical+_Probe番兵除外・kind "death"×analyze_communities共同体語彙の衝突=_NOT_A_KIND登録・★viewer HEADコピーハーネス自己矛盾化(第102と同族・epoch検出で恒久修正) | 2026-08-11 | +256 / **4980** |

> ※ 第1〜69バッチの詳細は [devlog-compressed.md](docs/log/devlog-compressed.md) Block #0〜#13 が正典。
> 主要な内容は本ファイル A〜Q 節にシステム別で収録済み。
