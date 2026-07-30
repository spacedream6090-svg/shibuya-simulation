# スナップショット型デジタルツイン — DT統合案の再導出(調査ノート)

> 作成: 2026-07-31。担当: Opus リサーチ(実行役)。**本ノートは調査結果であり実装計画ではない**
> (計画化・着手はユーザー承認後。standing rule)。
> 発端: ユーザーによる DT 定義の提示(2026-07-31)と、**観察ランは再現性を厳密に求めない**という方針確定
> ([devlog Entry 65](../log/devlog.md) / [STATUS.md](../../STATUS.md) §3)。
> 前回結論([dt-integration-plan.md](../plans/dt-integration-plan.md) / [dt-landscape.md](dt-landscape.md) /
> [dt-integration-deep.md](dt-integration-deep.md))=「リアルタイム同化は決定論と非整合なので不採用・一方向/事後のみ」を、
> 新定義と repro_tier 二重化のもとで**再検討する**のが本ノートの目的。

---

## §0 結論の先出し(10点)

1. **「日付を指定して現実を切り取る」機構はリポに既にある**。`scripts/build_map.py --osm-date`(Overpass attic query)で
   道路・建物・POI は**基準日つきスナップショット**として取得済み(現行 `meta.osm_date = 2025-04-01`)。
   さらに「外界の非決定論をロード時に1回解決して config へ凍結する」作法も既に2箇所で使われている
   (`config.py:216-219` の `start_date: auto`、`run.py` の `seed: auto`)。**再提案は新機構の発明ではなく横展開である。**
2. **最大の空白は天候**。`weather.py` は**100% 合成**で、8月は `(32, 25, 雨0.30, 雪0.0)` に ±3℃ の一様ゆらぎを足すだけ。
   実測(東京平年値 31.3/23.5℃)との差より深刻なのは、**「連続する猛暑」という現象自体が構造的に出せない**こと。
   本選10日ラン(8/16–8/26)は、2025年に東京都心が**10日連続猛暑日**となった 8/18–8/27 とほぼ完全に重なる。
3. **journal 等級で復活するのは「一方向強制」だけ**。ラン中に実天候を読んで**全員共通の環境変数として与える**型は、
   読んだ値を全記録すれば再生できる=journal。一方 **EnKF 等の状態同化は復活しない**(決定論ではなく研究設計の理由)。
4. **推奨設計は「案A(事前 materialization・strict)を土台に、本選ランでは案B(日次 materialization+resume・journal)」**。
   ラン中に core が直接 API を叩く案Cは**案Bへ縮退させるのが正しい**(core のネットワーク出口を LLM の1本に保つ)。
5. **P0–P7 は1つも取り消しにならない**。P 系列は「シム→外(見せ方)」、本ノートは「外→シム(入れ方)」で直交する。
   新規は S0–S8 の系列(§6.2)。
6. **本選前に入れる価値が高いのは S0/S1/S2/S5 の計約1.3日**(入力来歴の記録・観察ラン profile の是正・バス表生成・実イベント表)。
   **天候の実データ化 S3+S4(3.5–4.5日)はユーザー判断事項**(第75/第78 と正面から競合)。
7. **忠実度は2軸(frequency=on-demand スナップショット / fidelity=§5 の KPI)で数字で言う**。
   前回の DT-U3(「Digital Model と名乗る」)は廃止でよい。Kritzinger の判定基準は**「自動データフローの向き」だけ**なので、
   案A(人手で凍結)=**Digital Model**、案B(日次自動)=**Digital Shadow** と正確に言える。
8. **2026年8月中旬の渋谷は「祭りの谷」**。神宮外苑花火(8/8)も渋谷盆踊り(8/8)も窓の外。
   中旬にあるのはタイフェア(代々木公園 8/15–16)・MIYASHITA PARK のクールシェルター(〜8/19)程度。
   **モデル化すべきは賑わいではなく「オフィスワーカーが消えて来街者比率が上がり、路上飲酒が18時以降禁止された、猛暑の街」**。
   8/11 が山の日、お盆 8/13–16、**8/13(木)・8/14(金)は「平日なのにオフィスが空」という非対称日**。
9. **渋谷区が CC BY 4.0 で人流データを公開している**(本調査の新発見)。ArcGIS Hub の DCAT フィードに122データセット・
   うち120件が CC BY 4.0、**6件が KDDI 由来の通行/滞在人口(2018-10〜2024-09・月次)**。
   ただし **2019→2024 で通行人口がほぼ半減する一方、滞在人口は横ばい**という不整合があり、
   **絶対水準の年跨ぎ比較は不可・使えるのは属性構成比(来街者89%)と地点間比率のみ**。
10. **ライセンス上の地雷が2つある**。(a) 商業施設6館と渋谷区サイトは「私的利用を超える複製は事前許諾要」=
    **成果物・公開ミラーへの転載不可**。(b) OSM 由来の店舗テーブルは ODbL の Derivative Database で、
    **配布した瞬間に share-alike が発動**する。いずれも `STATUS.md` §3 の **PUB-U1** に直接効く。

---

## §1 ユーザー定義の含意

### 1.1 提示された定義(原文)

> 「建物や建造物などの物理的なものや地形、乗り物、天気や気温などの環境、人を、現実世界のある時点でコピー作成し、
> それを舞台にシミュレーションを回す。ある時点の現実を切り取ってデジタル上に持ってくるイメージ。
> 必ずしも現実と同期させる必要はない。**現実はシミュレーションの解像度を高めるためのデータを集めるツール**として
> 存在している認識。」

### 1.2 この定義が業界定義とどこで一致し、どこで離れるか

| 定義 | 同期の要求 | 本プロジェクトの位置 |
|---|---|---|
| **Kritzinger et al. (2018)**(*IFAC-PapersOnLine* 51(11):1016–1022. DOI `10.1016/j.ifacol.2018.08.474`。**著者5名**=Kritzinger, Karner, Traar, Henjes, **Sihn**。Sihn を落とした4名表記が流通しているので注意) | 逐語: 「**When there is no automated information flow between both entities, the system is a Digital Model.**」「**When the flow from the physical object to the virtual model is automated, it is called a Digital Shadow.**」「**The Digital Twin only appears when all connections (within the range of operation) are automated.**」 | **判定基準は「自動データフローの向き」だけであり、「どれだけ現実に似ているか」ではない**。→ 案A(人手で凍結)は **DM のまま**、案B(日次自動取得)は **DS**。前回調査の結論([dt-integration-deep.md §7.1](dt-integration-deep.md))と整合 |
| **Digital Twin Consortium**(2020) | 「*integrated data-driven virtual representation of real-world entities and processes, with **synchronized interaction at a specified frequency and fidelity***」。FAQ は更新頻度を「seconds to weeks to **on-demand**」と説明 | 「on-demand」まで頻度スペクトルに含めるなら、**スナップショット=頻度1回の同期**として DT 定義の端に収まる。【未確認】公式ページが **HTTP 403** で再取得できず、**検索結果由来の引用**である |
| **ISO/IEC 30173:2023**(Digital twin — Concepts and terminology) | 用語規格。全文は有償で本調査では**未確認** | 断言しない |
| **ECMWF DestinE**(参考=同じ発想の先行例) | ツインは連続同期ではなく「**Digital twin simulations are initialized using operational (re-)analyses** … through data assimilation techniques」。Extremes DT は「**on-demand** … a timescale of a few days ahead」 | **「実データで初期化し、その後は自律に走らせて現実から乖離させる」は気象学では標準作法**。ユーザー定義の正当化に最も強い先行例 |

**含意1: 用語問題は「名乗るか否か」から「どの軸で正確に言うか」へ移る。**
ユーザー定義は「同期頻度=1回(または低頻度)・忠実度=可能な限り高く」という点で DTC 定義の *frequency / fidelity* 2軸に
そのまま乗る。前回の DT-U3(「Digital Model と正確に名乗る」)は**廃止でよい**が、代わりに
「**同期頻度=スナップショット(on-demand)/忠実度=下記 §5 の KPI で測る**」と**2軸で数字を言う**のが最も強い言い方になる。
Kritzinger の分類は捨てるのではなく「我々は DM/DS 軸の議論ではなく frequency-fidelity 軸で自己記述する」と位置づける。

**含意2: 「現実はデータ収集ツール」= 実データの役割が“検証対象”から“初期条件・境界条件”へ格上げされる。**
現行の実データ利用は主に**事後照合**(`scripts/calibrate_report.py` の REALITY 帯)である。新定義では
実データは (a) **初期条件**(ある時点の建物・人・店・ダイヤ)と (b) **境界条件/強制項**(その期間の天気・気温・イベント)
として**ランの入力側**へ入る。これは ABM 文献でいう *forcing*(外部強制)であり、*data assimilation*(状態の逐次補正)とは
**別物**である。前回却下したのは後者(同化)であって、前者(強制)は決定論と両立しうる — ここが再検討の核心。

**含意3: 「必ずしも同期させる必要はない」= 乖離は失敗ではなく観測対象。**
スナップショットから出発したシムは時間とともに現実から乖離する。同期型 DT ではこれが劣化だが、
本プロジェクトでは**乖離そのものが「その社会が別の道を歩みうる」証拠**であり、反実仮想実験の前提である。
よって §5 の忠実度 KPI は「乖離ゼロを目指す指標」ではなく「**t=0 でどれだけ合っていたか / 何日で系統的に離れるか**」を
測る指標として設計すべき。

**含意4: repro_tier 二重化が選択肢集合を実際に広げる。**
[dual-mode-observe-verify-plan.md](../plans/dual-mode-observe-verify-plan.md) §2 の第72バッチで
`repro_tier=strict/journal/none` と `run.mode=observe/journal/verify` が入る。
「ラン中に外部データを読む」機能は **strict にはなり得ないが journal にはなり得る**
(=読んだ値を全部記録すれば事後に完全再生できる)。前回「決定論と非整合」で一律却下した ④センサー実データ同化 のうち、
**「ラン中に外部データを読むが、シムの状態は書き換えない(強制項として与えるだけ)」型は journal 等級として復活する。**
一方、**「シムの状態を観測で書き換える」真の同化(EnKF/粒子フィルタ)は復活しない** — 決定論の問題ではなく、
「創発の観察を実データへのフィッティングにすり替える」という研究設計上の理由で不可(この論点は前回の
[dt-integration-deep.md §8.3](dt-integration-deep.md) が正しく、方針変更の影響を受けない)。

### 1.3 再検討で「復活する/しない」の切り分け(結論の先出し)

| 型 | 内容 | 前回 | 今回 | 理由 |
|---|---|---|---|---|
| **A. 事前スナップショット固定** | ラン前に実データを取得・凍結してリポ/キャッシュへ。ランは静的ファイルのみ読む | 採用(類型②) | **採用・大幅拡張** | strict 等級を維持したまま忠実度を上げられる。**最優先** |
| **B. ラン中の一方向強制(read-only forcing)** | ラン中に実天候等を読み、全員共通の**環境変数**として与える。シムの内部状態は書き換えない | 不採用 | **journal 等級で条件付き復活** | 記録すれば再生可能。ただし §4 の制約を満たす場合のみ |
| **C. ラン中の状態同化** | 観測でエージェント位置/状態を補正(EnKF・粒子フィルタ) | 不採用 | **不採用のまま** | 決定論以前に研究設計として不可(創発の観察が消える) |
| **D. 双方向連成** | シムが現実へ介入 | 不採用 | **不採用のまま** | 実行手段が存在しない |

---

## §2 現状資産の実査結果(file:line)

2026-07-31 時点のリポジトリ実査。**「実データ」と「合成」の境界を正確に記述する**ことを目的とする。

### 2.1 幾何(建物・地形・道路)= **実データ・スナップショット済み・最も強い**

| 資産 | 実体 | 出自・鮮度 |
|---|---|---|
| 建物実形状 | `data/plateau/plateau_mesh.npz`(5.4MB)・`plateau_index.json`(1.5MB) | PLATEAU CityGML **渋谷区 2025年度版**から `scripts/plateau_extract.py` が抽出。`data/plateau/` は `.gitignore:15` で除外(再生成レシピ運用) |
| 建物実高さ | `data/building_heights_shibuya.json`(215KB・**追跡対象**) | `scripts/build_heights.py`。meta 実測: PLATEAU 側 6,311棟中 **3,531棟を照合**(iou_min=0.4・knn 25m)、高さ中央値 14.3m・最大 231.0m。定義は `h = height − base`(`build_heights.py:18-25` に根拠つきで明記) |
| 地形 | `data/plateau/terrain.npz`(3.4MB)・`terrain.json` | PLATEAU DEM 由来 |
| 道路 | `data/shibuya_osm*.json`(0.8–3.1MB) | OSM(ODbL) |
| 交差点 | `data/crossings_shibuya.json` | — |
| **建物内部(フロア構成)** | `data/floorguide_shibuya.json`(**10棟**)+ `data/floor_layouts.json` | **公式フロアガイドを人手で調査した実データ・調査時点 2026-07**。meta に**出典 URL 15件**を列挙(スクランブルスクエア/ヒカリエ/109/マークシティ/ストリーム/PARCO/マルイ/MIYASHITA PARK/フクラス/渋谷ちかみち 等)。meta 自身が「テナントは入替があり得る概略」「詳細な間取り(区画配置)は**非公開のため収録せず**、フロア構成と接続の実在事実に限定」と限界を明記 |
| 消費側 | `conf/config.yaml:212-216` `world.heights`(既定 OFF)→ `src/society/world/map.py:178 attach_heights` | 高さ不明は `None`(`map.py:218`「欠測を 0 と偽らない」) |

> **★ 補足**: `floorguide_shibuya.json` は「**人手でその時点の現実を調べ、出典と限界を書いて凍結する**」という
> スナップショット作法の既存の実例であり、しかも**調査時点が 2026-07 と最も新しい**。
> §3 のイベント表・営業時間表も、API が無い領域ではこの方式(人手調査+出典列挙+限界明記)を踏襲するのが正しい。

ライセンス: PLATEAU は「政府標準利用規約2.0 / CC BY 4.0 / ODC BY / ODbL から利用者選択、商用含め無償」
([PLATEAU Site Policy](https://www.mlit.go.jp/plateau/site-policy/)。リポ側実査記録は
[plateau-2025-update-notes.md:70-71](plateau-2025-update-notes.md))。

#### ★ 「日付を指定して現実を切り取る」機構は**既に実装済み**である

`scripts/build_map.py` は Overpass の **attic query** に対応している。

```
scripts/build_map.py:7      python scripts/build_map.py --osm-date 2023-04-01 --out data/shibuya_osm_2023.json
scripts/build_map.py:88-92  """…osm_date 指定時は attic query(過去スナップショット)。"""
                            date_setting = f'[date:"{osm_date}T00:00:00Z"]'
scripts/build_map.py:660-661 meta["osm_date"] = osm_date        ← 取得基準日が成果物に残る
```

実際に使われている: `data/shibuya_osm_wide_20250401.json` と `data/shibuya_osm_wide_v7.json` の
`meta.osm_date = "2025-04-01"`(実測)。**ユーザー定義の「現実世界のある時点でコピー作成」は、
道路・建物・POI については既にこの形で成立している。** 再提案は「新機構の発明」ではなく
「**この機構を天候・店・人へ横展開し、取得基準日をラン成果物に一元記録する**」問題として立てられる。

| 地図ファイル | `meta.osm_date` | POI 数 | 建物数 | 使う profile |
|---|---|---:|---:|---|
| `data/shibuya_osm.json`(基底) | **なし**(=最新取得時点が不明) | 1,098 | 1,181 | `conf/config.yaml:188`(=既定・**observe.yaml もこれ**) |
| `data/shibuya_osm_wide_20250401.json` | 2025-04-01 | 1,965 | 7,210 | 生成中間物 |
| `data/shibuya_osm_wide_v7.json` | **2025-04-01** | 1,975 | 7,210 | `production.yaml:31` / `daily.yaml:33` / `longrun30.yaml:86` |

**評価: ユーザー定義の「建物・地形」は既にスナップショット型 DT として成立している。ただし基準日は 2025-04-01
=本選(2026-08)から約16か月前**。渋谷は再開発の進行が速い区域なので、`snapshot_age` として明示すべき数字。

### 2.2 乗り物 = **鉄道は実ダイヤ・バスは未接続・タクシーは合成物理**

3つを混同しないこと。**`transit_live.py` は ODPT ではない。**

| 系統 | 実体 | 実データか |
|---|---|---|
| **鉄道ダイヤ** | `data/transit_odpt.json`(meta/lines/bus_lines)。生成=`scripts/fetch_odpt.py` → `scripts/build_transit_odpt.py`。`conf/production.yaml:52`・`conf/daily.yaml:44`・`conf/longrun30.yaml:95` が指定 | **9路線中6路線(67%)が実ダイヤ**(実測): `ODPT実ダイヤ(…オープン枠)` **3**・`ODPT実ダイヤ(…チャレンジ限定)` **3**・`近似(公表の始発終電・間隔)` **3**。※チャレンジ限定の3路線は `data/odpt_challenge/`(`.gitignore:9` 除外)由来なので**再生成にはチャレンジ枠のアクセスが要る**。一方 `data/transit_shibuya.json`(基底 profile が読む方)は**9路線すべて `source` フィールドなし=完全に合成近似** |
| **バス静的表** | `src/society/bus_table.py`(実装済み・純ロジック)。`conf/config.yaml:702-705` `transit_ride.bus_table`(既定 OFF)、`path: data/odpt/bus_table_shibuya.json` | **データが存在しない**。実査: `data/odpt/bus_table_shibuya.json` は**未生成**(`scripts/build_bus_table.py` は存在)。=**読み手だけあって表が無い** |
| **タクシー** | `src/society/transit_live.py`。**これは SUMO ライブ連成のタクシー配車**であって ODPT とは無関係(`transit_live.py:1-9`)。既定 backend=`mock`=`MockBridge`(`transit_live.py:78-107`)は「(seed, from_node, to_node, call秒)の安定ハッシュだけから待ち/乗車秒を決める**純関数**」=**渋谷の実測ではない**と自己申告(`transit_live.py:83-84`) | **合成**(traci backend で実 SUMO に差し替え可) |

ODPT の運用規律(重要): `data/odpt/.gitkeep` が「シミュ本体はこのキャッシュのみ読む。**実行中の API 呼び出しは禁止**(決定論保護)」と明記。
`data/odpt_challenge/` は `.gitignore:9` で除外(再配布制限)。出典表示義務は `scripts/build_bus_table.py:31,49-52,286` と
`build_transit_odpt.py:19-20,298` に埋め込み済み。
【未確認】ODPT 利用規約全文は本調査で再取得できず(`https://developer.odpt.org/terms` は本文取得不可)。リポ既存記載に従う。

**評価: 「乗り物」は鉄道のみ部分的に実スナップショット。バス表の未生成は最も安い忠実度改善の候補。**

### 2.3 天気・気温 = **完全に合成。実データはゼロ。最大の伸びしろ**

```
src/society/weather.py:22-27   _MONTH_CLIMATE = 月→(最高気温中心, 最低気温中心, 雨の重み, 雪の重み)
                               8月 = (32, 25, 0.30, 0.0)  ← 「現実の東京の月別気候の近似」(コメント)
src/society/weather.py:55-72   _sample(): rng.random() 1回で 雪/雨/曇/晴 を決め、
                               temp_hi = hi_c + rng.integers(-3,4) / temp_lo 同様 = ±3℃ の一様ゆらぎ
src/society/weather.py:75-87   weather_for(): sim.hub.stream("weather", day_index) から 1日1回だけ引く
src/society/weather.py:90-97   weather_line(): 「今日の天気: 雨、最高14℃。」の1行をプロンプトへ
src/society/weather.py:100-107 discomfort_delta(): 雨・雪の日に rain_grievance を factors へ渡すだけ
```

- 消費経路: `engine/scheduler.py:3428-3452`(日境界で確定 → `weather` イベントを `agent_id=-1` で1件ログ → 全員の
  発火/計画/内省プロンプトへ1行注入 `scheduler.py:856,883,895,1904,4508`・`cognition/planning.py:138`・`reflection.py:242-412`)。
- 設定: `conf/config.yaml:1441-1443`(既定 OFF)。`conf/daily.yaml:52-54`・`conf/production.yaml:64-66`・`conf/observe.yaml:44-45` で ON。
- 気候テーブルの供給元: `env/shibuya/env.yaml:83-97` `climate:` → `src/society/envpack.py:63-93` → `engine/simulation.py:274-276`。
- **粒度は「1日1回・全市共通・{天気カテゴリ4種, 最高気温, 最低気温} のみ」**。時刻別の気温変化・降水量[mm]・
  湿度・風・WBGT(暑さ指数)は**存在しない**。
- 現実側との唯一の接点は較正表の1行のみ: `scripts/calibrate_report.py:73-74`
  `("rainy_share", "降雨日の割合(7-8月)", 0.25, 0.55, "", "東京7月の降水日(1mm以上)~11-15日/月")`。

**評価: ユーザー定義が名指しした「天気や気温などの環境」は、現状 100% 合成である。しかも渋谷の 8月中旬は
気温・WBGT が行動を最も強く支配する時期(→ §5)。ここが再提案の主戦場。**

### 2.4 人 = **分布は実統計ベース・在場曲線の実測は未接続**

| 資産 | 実体 |
|---|---|
| ペルソナプール | `data/persona_pool/`(`.gitignore:17` 除外)+ `data/persona_pool.json`。設計=[persona-pool.md](../plans/persona-pool.md)。流入の統計根拠=[shibuya-inflow.md](shibuya-inflow.md)(国勢調査 従業地・通学地集計ほか・検証済み URL 付き) |
| 日次 presence | `src/society/world/presence.py`。層別純関数・**k 非依存/trait 非依存**を明示設計(`presence.py:8-11`) |
| 人流実測 | `data/jinryu/shibuya_mesh1km_2019_2021.csv`(生データ 1,944行)・`shibuya_concurrent_144step_curve.csv`(派生 144step 曲線)。出所=国交省「全国の人流オープンデータ」(Agoop GPS 由来換算人口値)、**政府標準利用規約2.0=CC BY 4.0 互換・再配布可**(`data/jinryu/SOURCE.md:18-20`) |

**★ 実測曲線は今も接続されていない**: `src/` から `data/jinryu` を読む箇所は
`presence.py:16` の「在場実測曲線(…)は **v1 では使わない(将来拡張点)**」という**コメント1行のみ**(grep 実査で確認)。
144step の実測曲線が 144step のシムの隣に置かれたまま使われていない状態は前回調査(§8.1)から変わっていない。

### 2.5 較正 = 事後照合の枠組みは完成している

`scripts/calibrate_report.py:44-106` の `REALITY` が (key, ラベル, lo, hi, 単位, **出典**) のバンド表。
第62バッチ以降「直接統計が不在なら捏造せず**出典つきプロキシ帯**を置く」流儀が確立(`:93-96` の `joint_accept` が典型)。
**天候・環境系の行は `rainy_share` の1行だけ**(`:73-74`)。§5 はこの表への追加として設計するのが自然。

### 2.6 環境改変の器 = `world.mod` が既にスナップショット注入点になっている

`src/society/world/worldmod.py`(第67バッチ)。`conf/config.yaml:234-236` `world.mod`(既定 OFF・プロファイル
`conf/worldmod/<name>.yaml`)。**ワールド構築時に一度だけ・決定論・乱数ゼロで適用**(`worldmod.py:3-6`)。

- 実効するもの: `edges_closed` / `edge_speed_scale` / **`open_hours.cats`**(営業時間のカテゴリ単位上書き・`worldmod.py:189-205`)
- **予約フィールド(未消費)**: `gate_capacity`(`worldmod.py:172-177`)・`open_hours.pois`(POI 単位・`worldmod.py:206-215`)。
  `summary` に `reserved_not_consumed` として記録(`worldmod.py:232`)
- 営業時間の本体側: `src/society/commerce.py:37-48,102-147`(カテゴリ別の決定論スケジュール。既定 OFF=全 POI 常時営業)

**評価: 「ある時点の店の開閉」をスナップショットとして流し込む配管は `open_hours.cats` として既に通っている。
POI 単位は予約のまま=実店舗の実営業時間を入れるには `open_hours.pois` の実装が要る。**

### 2.7 記録・再生基盤(§4 の土台)

- L1 は append-only Parquet+zstd。checkpoint 連携で `flush_segment()` が `l1_events.part-NNNN.parquet` を書く
  (`src/society/observer/logger.py:1-8`)。
- LLM 応答は content-addressed キャッシュ済み(`src/society/llm/cache.py` CachedLLM・`llm_cache.jsonl`)。
  **プロンプト全文の永続化と REPLAY fail-fast は第71バッチで実装予定**(未実装)。
- **入力データファイルのハッシュは現在どこにも記録されていない**(実査: `src/society/engine/` で `hashlib` を使うのは
  `checkpoint.py:24,49` のみ=checkpoint 用)。`summary` に載るのは `world_mod`(`simulation.py:1453`)と
  `building_heights`(`:1455`)の統計だけ。→ **§4 の必須要件になる。**
- `seed=auto` の採取と記録は実装済み(`scripts/run.py:47-80,116-129`・`conf/observe.yaml:26-28`)=「選ばないだけで失わない」。
- 名前衝突注意: `src/society/observer/provenance.py` は**伝播系譜**(誰から誰へ語が伝わったか)であって
  データ来歴ではない。§4 の provenance と混同しないこと。

### 2.8 実査で見つかった具体的な穴(いずれも安価)

1. **`conf/observe.yaml` は `world.map` も `transit:` も上書きしていない**(grep 実査でヒット 0)。
   `--profile conf/observe.yaml` 単独で回すと、基底 `conf/config.yaml` の
   **`data/shibuya_osm.json`(1,098 POI・1,181 建物・`osm_date` なし)** と
   **`data/transit_shibuya.json`(合成寄り)** を読む。実ダイヤ・広域実地図を使うのは
   `production/daily/longrun30` だけ。
   ※ `observe.yaml:18-21` のヘッダ自身が「本番の厚い再現と併せるなら **production.yaml を土台に本ファイルの
   chance ブロックだけを足す運用でもよい**」と書いており、想定運用では回避される。だが
   **「観察ランのプロファイル」という名前と実際の忠実度が乖離している**のは事実で、本選前に潰す価値がある。
2. `data/odpt/bus_table_shibuya.json` が未生成(§2.2)。読み手だけがある。
3. jinryu 144step 実測曲線が未接続(§2.4)。
4. 入力データのハッシュ・取得日時がラン成果物に残らない(§2.7)。
5. **POI から `opening_hours` が落ちている**。実査: `data/shibuya_osm_wide_20250401.json` の
   `pois[]` のキーは `{building, cat, floor, id, name, node, x, y}` のみ。
   一方 Overpass クエリは `out body;`(`build_map.py:109`)で**全タグを取得している**ので、
   `opening_hours` は生応答には含まれている。=**再取得は不要で、抽出側を通すだけ**で実営業時間が入る。
   受け皿の `world.mod.open_hours.pois` は**予約フィールドで未消費**(`worldmod.py:206-215`)なので、
   そちらの実装とセットになる。

---

## §3 データ源カタログ

> 各項目は公式ページを実取得して検証した。**確認できなかったものは「未確認」と明記**し、推測で埋めていない。
> 調査日 2026-07-31。**今日時点で 2026年8月のデータは存在しない**ため、
> 「8/15–8/30 の本選期間中に**その場で**取らないと永久に失われるもの」と「後から取れるもの」を各行で区別する。

### 3.1 気象・環境(気温・降水・暑さ指数)

| # | 正式名称 | URL(検証済み) | 形式 | 時間粒度 | 最寄地点 | ライセンス | キー/料金 | 8月中旬に使えるか |
|---|---|---|---|---|---|---|---|---|
| W1 | **気象庁 過去の気象データ・ダウンロード** | https://www.data.jma.go.jp/risk/obsdl/ | Web UI → CSV | **10分/1時間/日/月** | 東京(44132) | **公共データ利用規約1.0**(CC BY 4.0 互換・**商用可**・出典明示必須) | 不要/無料 | **◎ 使える**。ただし**翌日以降**の取得(検定済み値) |
| W2 | **気象庁 過去の気象データ検索(etrn)** | https://www.data.jma.go.jp/stats/etrn/ | HTML(URL 構造が安定) | **10分値**〜年 | 同上 | 同上 | 不要/無料 | **◎**。当日分も表示=逐次取得可。10分値の提供開始年は**未確認** |
| W3 | **気象庁 bosai アメダス JSON**(準公式) | https://www.jma.go.jp/bosai/amedas/data/latest_time.txt / .../data/map/YYYYMMDDHHMMSS.json / .../const/amedastable.json | JSON `{値, 品質フラグ}` | **10分・ほぼリアルタイム** | 全国1,286地点 | 気象庁サイト規約(PDL1.0)配下と解されるが**API としての明示的提供表明は未確認**=**将来変更リスクあり** | 不要/無料 | **◎ ライブ取得の最有力**。本番は W3(ライブ)+W1(事後の正式CSVで上書き検証)の**二重取り**が安全 |
| W4 | **気象庁 防災情報XML** | https://xml.kishou.go.jp/xmlpull.html(フィード: https://www.data.jma.go.jp/developer/xml/feed/regular.xml 他) | XML・**PULL のみ**(PubSubHubbub は2020-09-01廃止) | 高頻度フィードは毎分更新・直近10分入電 | 全国 | PDL1.0 | 不要/無料。**1日10GB 超で IP 遮断** | **○ イベント駆動用**。熱中症警戒アラート・気象警報の電文。**過去電文は数日で流れる**=期間中に取らないと失う |
| W5 | **環境省 熱中症予防情報サイト(暑さ指数 WBGT)** | https://www.wbgt.env.go.jp/ (規約 /tos.php・DL /wbgt_data_download.php・API 仕様 PDF /man15NH/wbgt_data_api_service_manual.pdf) | **CSV + WebAPI(JSON)**。実況 `GET /api/v1/getSurveyData`(返却: `wbgt_WI, wbgt_WO, wbgt_Tw, wbgt_Tg`=屋内/屋外WBGT・湿球・**黒球温度**)、予測 `/api/v1/getForecastData` | **実況=毎時 / 予測=3時間** | 東京44132(東京都内で唯一の**実測**地点。全国は実測47+推定794) | PDL1.0(出典明示+**加工した旨の記載**必須) | **申請不要・無料** | **◎ 8月渋谷には必須級**。ただし**サービス稼働は4月第4水曜〜10月21日**=8月中旬は期間内だが**10/22以降は当年分のリアルタイム提供が止まる**→期間内に必ず取得。遡及=実況2010年〜/予測2021年〜 |
| W6 | **Open-Meteo**(Historical Weather / JMA / Historical Forecast) | https://open-meteo.com/en/docs/historical-weather-api / /jma-api / /historical-forecast-api(規約 /en/terms・料金 /en/pricing) | JSON API・**任意の緯度経度** | 毎時。ERA5=0.25°(約25km)・**JMA MSM=0.05°(約5km)**・ERA5-Land=0.1° | 渋谷駅座標をそのまま投げられる | **CC BY 4.0** | **無料枠はキー不要**。制限 600/min・5,000/h・10,000/日・300,000/月。**無料枠は商用不可**(研究・公的機関の公開研究は可と明記)。有料実額は**未確認** | **○ 補助**。ERA5 は**5日遅延**+25km 格子=渋谷のヒートアイランドを表現できない。`/v1/jma`(MSM 5km)と Historical Forecast は即時 |
| W7 | 気象業務支援センター(JMBSC) | https://www.jmbsc.or.jp/jp/online/c-onlineF.html | 専用配信 | **1分値**あり | 全国 | 契約 | 開設5万円+月額 約1.1万円〜(基本4,200+アメダス5,400+インターネット1,500・税別) | **× 今回は不要**。1分値が唯一の強みだがシムの粒度(10分)には過剰 |
| W8 | OpenWeatherMap / WeatherAPI.com / Visual Crossing | https://openweathermap.org/price / https://www.weatherapi.com/pricing.aspx / https://www.visualcrossing.com/weather-data-editions/ | JSON | 毎時 | 任意座標 | 各社規約 | 各社無料枠あり | **× 不要**。OWM は**無料枠に履歴なし**。WeatherAPI は公式に「historical weather data is made up of **forecast data and not from actuals**」=**実測ではない**ので検証用途に不適 |
| W9 | **東京都 大気汚染常時監視**(気象項目=風向・風速・**温度・湿度・日射量**を含む) | https://www.taiki.kankyo.metro.tokyo.lg.jp/taikikankyo/guid/index.html / 月報CSV https://www.kankyo.metro.tokyo.lg.jp/air/air_pollution/torikumi/result_measurement/ | 速報(Web)+月報CSV(ZIP) | **1時間値** | **渋谷区本町局(A111)**。※旧「渋谷区宇田川町局」(センター街至近)は2025年10月末に測定休止、11月下旬から本町局として再開 | **未確認**(当該ページに明示なし。東京都オープンデータカタログ掲載分の規約は別途要確認) | 不要・無料 | **△ 条件付き**。**渋谷区内で唯一の公的な毎時気象観測になりうる**が、①当該局が気温/日射を測っているか**未確認** ②局移転で渋谷駅周辺の代表性が低下 ③ライセンス未確認 |
| W10 | 東京都環境科学研究所 METROS(都市ヒートアイランド観測網) | https://www.kankyo.metro.tokyo.lg.jp/climate/heat_island/ | 報告書中心 | — | **区部100地点で気温・湿度**、20地点でフル要素(2002-07-15〜) | **未確認** | — | **× オープンデータとしては使えない**。公開DL窓口・API・ライセンスを確認できず。空間密度は理想的なので、余裕があれば研究所への**直接照会**が最も費用対効果が高い |

#### ★ 渋谷の気温を語るときの構造的な落とし穴(本調査の最重要発見のひとつ)

- **渋谷区内に気象庁の気温観測点は存在しない。** 最寄の官署「東京」(44132 / block_no 47662)は
  **皇居の緑地=北の丸公園**にあり、渋谷駅から約 5.8km NE。
- 次に近い**世田谷(44126)は降水量しか測っていない**(リアルタイム観測値で実確認)。=**渋谷の気温源は事実上「東京」一択**。
- **東京は 2014年12月2日に大手町から北の丸公園へ移転**している
  ([気象庁 2014-12-02 のお知らせ](https://www.jma.go.jp/jma/kishou/know/kansoku/info/20141202_tokyo_rojo.html))。
  報道ベースで移転距離約900m・年平均気温が大手町比 **約 −0.9℃**、日最低気温 **約 −1.4℃**。
- **含意**: 公式値をそのまま渋谷スクランブル交差点の気温として使うと**系統的に低く**なる(特に夜間)。
  スナップショットを名乗る以上、**都市バイアス補正を明示的にモデル化し、その根拠を書く**必要がある。
  根拠候補 = WBGT の**黒球温度 Tg**(W5)と**渋谷区本町局の気温**(W9)の突き合わせ。
- 【要確認】WBGT 地点マスタでは 44132 の所在地欄が「文京区白山 小石川植物園」だが緯度経度は北の丸公園と一致する。
  **実測器の設置場所と推定に使う気象庁観測点が食い違う可能性があり、本調査では解消できなかった**(環境省へ要照会)。

#### 熱中症警戒アラート(= `world.events_file` にそのまま流せるイベント)

- 発表基準(公式ページ原文): 「**翌日・当日の日最高暑さ指数(WBGT)が33(予測値)に達する場合に発表**」
  ([環境省 熱中症予防情報サイト 熱中症警戒アラートとは](https://www.wbgt.env.go.jp/about_alert.php))。
- 発表単位: 「**府県予報区等内において、いずれかの暑さ指数情報提供地点における**」(同上)。
- アラート一覧ページ([/alert.php](https://www.wbgt.env.go.jp/alert.php))には「日最高暑さ指数(予測値)31以上発表中」
  「14時発表予定」「17時発表予定」の表示があるが、**発表時刻・運用期間・特別警戒アラートとの基準差は
  当該ページに明記がなく未確認**(数値 31 と 33 の使い分けも本調査では確定できなかった)。
- **シムでの使い道**: アラート発表日を `world.events_file` の1行にして `publish_news`(既存経路・
  `scheduler.py:2688-2703`)へ流せば、**エージェントが「今日は危険だ」という情報を受け取る**。
  実装ゼロで「現実の8月の空気」が入る、最も安い1手。



### 3.2 イベント・暦(→ `world.events_file` / `annual_events`)

#### ★ 2026年8月中旬の渋谷は「祭りの谷」である(調査の結論)

渋谷の夏の大型行事は**すべて 8/8 までに終わる**。「8月中旬の渋谷」を再現するとき、
**賑わいのイベントを足すのは事実に反する**。

| イベント | 日程 | 中旬(8/10–8/20)に入るか |
|---|---|---|
| 神宮外苑花火大会(第45回) | **2026年8月8日(土)** 19:30–20:30(予備日 8/9) | **入らない** |
| 第7回 渋谷盆踊り(道玄坂・文化村通り 16:30–22:30 交通規制・例年6万人超) | **8月8日(土)** | **入らない** |
| 恵比寿駅前盆踊り / 代々木上原 / 大原北町会 ほか | 7/17〜8/2 に分散 | 入らない |
| **タイフェア in 東京 2026**(代々木公園・入場無料) | **8月15–16日** | **入る**(中旬の区内最大級) |
| KAWAII FRIENDS PUKA PUKA PARK(渋谷サクラステージ) | 8月13–25日 | 入る |
| SKY-HIGH BON ODORI(東急プラザ渋谷 17-18F・小規模) | 8月12日 | 入る |
| コミックマーケット C108(東京ビッグサイト) | 8月15–16日 | 渋谷外だが**若年層を湾岸へ吸う** |
| 商業施設: ヒカリエ「My Place, My Art 展」 | 8/15–8/30 | 入る |
| 商業施設: MIYASHITA PARK「クールシェルタープロジェクト」 | 7/23–**8/19** | **入る=猛暑避難所。街の滞留行動に直結** |
| 商業施設: SCSQ「渋谷宙間学校」 | 7/10–8/23 | 入る |
| (陰性確認)渋谷ハロウィン=10月 / 区民まつり=11月 / 金王八幡宮・代々木八幡宮 例大祭=9月 | — | 入らない |

**暦の構造(2026年)**: **8/11(火)が山の日**、お盆は 8/13(木)–8/16(日)。
8/10 と 8/12 に休暇を挟めば **8/8–8/16 の9連休**。
→ **8/13(木)・8/14(金)は「平日なのにオフィスが空」という非対称日**になる。
機械可読の祝日 CSV: <https://www.cao.go.jp/syukujitsu.csv>(1955–2027・22KB・無料)。
**【未確認】お盆期間の渋谷の通勤者減少率を示す公開統計は発見できなかった**
(東京都の COVID 期人流ダッシュボードは 2023-12-31 で更新終了)。

**★ したがって「8月中旬の渋谷」のモデル化対象は、賑わいではなく
「オフィスワーカーが消えて来街者比率が上がり、路上飲酒が18時以降禁止された、猛暑の街」である。**

#### 渋谷区 路上飲酒禁止条例(**通年施行・罰則なし**)

- 正式名称: **渋谷駅周辺地域の安全で安心な環境の確保に関する条例**
  <https://www.city.shibuya.tokyo.jp/kusei/shisaku/jorei-toshin/sbykankyo.html>
- 2024年6月17日改正可決 → **2024年10月1日施行**。ハロウィン・年末年始限定から**通年**へ拡大。
- **午後6時〜翌朝5時**、公共の場所での飲酒禁止。区域は渋谷駅周辺(改正で東側拡大=宮益坂・円山町・宮下公園・ヒカリエ周辺)。
- **罰則なし**。警備員パトロール+周辺店舗への酒類販売自粛要請で担保。区域図は PDF で、**GIS データではない**。
- **シムへの含意**: 摘発リスクではなく「注意される・社会的圧力」としてモデル化すべき。
  **18:00 という境界が夜間の路上滞留を非連続に変える**=既存の `commerce.hours` / `world.mod.open_hours` とは別の軸。

#### イベントカレンダーのデータ源

| 源 | URL | 形式 | ライセンス | 判定 |
|---|---|---|---|---|
| 渋谷区 イベント情報 | https://www.city.shibuya.tokyo.jp/contents/event/calendar/ | **HTML のみ**(CSV/JSON/ICS/RSS なし) | **区 HTML サイトのサイトポリシーは「転載・複製はこれを禁じます」** | **× 自動取得不可**。人手で読み取り、成果物へ転載しない |
| 自治体標準データセット「イベント一覧」 | 標準命名 `.../shibuya/131130_012_event.csv` | CSV | CC BY 4.0 | **× 渋谷区は未公開**(実測: 渋谷区 **404** / 江東区 `131083_012_event.csv` は **200・335KB**)。文京・中央・中野・墨田・江東ほかは公開中 |
| 東京都オープンデータカタログ(CKAN API・キー不要) | `https://catalog.data.metro.tokyo.lg.jp/api/3/action/package_search?fq=organization:t131130` | JSON | CC BY 4.0 | **△** 渋谷区分17件は施設・宿泊・公園・町会等。**人流・通行量・イベントは無し**。※HTML の組織ページは 403(WAF)だが **API は通る** |
| **渋谷スクランブルスクエア 公開 JSON** | `https://tacsis-cdn-endpoint.azureedge.net/cms-web/scsq_news_event_web.json`(121KB・85件)/ `shop.json`(566KB)/ `open_hours.json` | **JSON・認証不要・HTTP 200 実測** | 施設サイト規約(下記) | **◎ 最良**。`period_start`/`period_end` が構造化済み。**実装注記: UTF-8 と Shift-JIS が混在**しておりエンコーディングのフォールバックが必要 |
| MIYASHITA PARK | wp-json REST API | JSON | 同上 | ○ |
| 渋谷PARCO | `Allow: /` 全面許可・サーバーレンダ HTML | HTML | 同上 | ○ |
| 渋谷ヒカリエ / 渋谷ストリーム | robots.txt は全面許可 / 404 | HTML パース要 | 同上 | △ |
| **SHIBUYA109** | **robots.txt が ClaudeBot / GPTBot / CCBot 等を名指しで `Disallow: /`+`ai-train=no`** | — | — | **× 自動取得不可**。本調査でも本文を一切取得していない。営業時間 10:00–21:00 は第三者サイト経由の**間接情報** |
| 内閣府 国民の祝日 CSV | https://www.cao.go.jp/syukujitsu.csv | CSV(22KB・1955–2027) | 政府標準利用規約 | **◎** |

> **★ ライセンス上の共通制約(重要)**: 商業施設6館と渋谷区サイトはいずれも「私的利用を超える複製は事前許諾要」。
> → **シム内部の入力としての利用と、成果物への転載/公開は分けて扱う**必要がある。
> **公開ミラー(`publish_public_mirror.ps1`)への同梱は不可**。PUB-U1 の判断材料になる。

#### SNS 由来イベント検知 — **組まないことを推奨**

| 手段 | 2026年の状況 | 判定 |
|---|---|---|
| X API | **従量課金のみ・無料枠の記載なし**。$0.005/post read・月200万 reads 上限 | 1日1万件で月 $1,500。中旬14日で約 $700 |
| Yahoo!リアルタイム検索 | **公式 API 無し**。規約がクロール/スクレイピングを明示禁止 | 使用不可 |
| Google Trends API | **限定 alpha・申請制**(2025年7月発表)。`pytrends` は **2025年4月アーカイブ済** | 使えない |
| Instagram Graph API | ハッシュタグ**ローリング7日で30個まで・位置フィルタ無し** | 設計が合わない |
| イベントバンク API | 月額2万円〜・**法人/団体限定** | 個人研究では契約不可 |

**理由は費用だけではない**: 目的が「**過去日付の再現**」である以上、リアルタイム検知は定義上不要。
8月中旬の確定イベントは上表のとおり**手作業で列挙できる規模**である。

### 3.3 歩行者数・人流

#### ★ 渋谷区が CC BY 4.0 で人流データを公開している(本調査で新たに確認)

`https://city-shibuya-data.opendata.arcgis.com/api/feed/dcat-us/1.1.json`
→ HTTP 200 / 514,783 bytes / **122データセット・うち120件が CC BY 4.0**。
うち **6件が人流データ**(Location Analyzer = KDDI 提供)。ArcGIS REST API で中身を実取得済み。

- スキーマ: `名称, 種別, 年, 月, 属性, 人数_の合計, ObjectId`
- **通行人口 3地点**: 宮益坂 / 道玄坂 / 表参道
- **滞在人口 5エリア**: 渋谷駅中心(スクランブル交差点含む)/ 北西 / 北東 / 南東 / 南西
- 属性: **居住者 / 勤務者 / 来街者**
- 期間: **2018年10月 → 2024年9月(84ヶ月・月次)**

実測値(人数_の合計・人/月):

| 通行人口 | 2019年8月 | 2023年8月 | 2024年8月 |
|---|---:|---:|---:|
| 道玄坂 | 2,398,000 | 1,905,000 | 1,312,000 |
| 表参道 | 1,543,000 | 995,000 | 673,000 |
| 宮益坂 | 921,000 | 658,000 | 412,000 |

2024年8月の属性内訳(道玄坂): 来街者 1,172,000 / 勤務者 79,000 / 居住者 61,000 = **来街者が 89%**。
滞在人口 2024年8月: 中心エリア 7,738,000(来街者 6,193,000 / 勤務者 1,177,000 / 居住者 368,000)、
北西 22,469,000、北東 8,289,000、南西 4,845,000、南東 4,331,000。

> **★ 重大な注意**: 通行人口は 2019→2024 でほぼ半減しているが、滞在人口の中心エリアはほぼ横ばい(8.4M→7.7M)。
> この不整合は実際の減少ではなく **KDDI パネル構成の変更**を示唆する。
> **絶対水準を年跨ぎで比較してはならない。使ってよいのは属性構成比(来街者89%等)と
> 地点間比率(道玄坂:表参道:宮益坂 ≒ 3.2:1.6:1)に限る。**
> また 2025/2026年分は無く、**時間帯別も無い**。

#### 生きている無料ソース(3つだけ)

| 源 | URL | 粒度 | 保持 | 判定 |
|---|---|---|---|---|
| **渋谷区 SHIBUYA CITY DASHBOARD** | https://www.city.shibuya.tokyo.jp/kusei/tokei_shibuya/shibuya-data/shibuya_city_dashboard_peopleflow_KDDI.html (**更新日 2026-07-22**=生きている) | Power BI 埋め込みのみ・CSV 無し | — | **同じ元データが上記 ArcGIS API で CC BY 4.0 で取れる**のでそちらを使う。時間帯粒度の有無は**未確認**(Power BI をレンダリングできず)。窓口=グローバル拠点都市推進課 |
| **東京メトロ Metro CrowdNavi** | https://tmcawebapp1.tokyometro.jp/ (リリース https://www.tokyometro.jp/news/2026/224561.html ) | **駅ごと・時間ごと・列車ごと**(直近5日間の平均)+路線混雑ヒートマップ | **直近5日のみ** | **◎ 唯一「駅×時間帯」を無料でくれる現行ソース**。**2026年6月16日 全路線で本格提供開始**。渋谷は銀座線・半蔵門線・副都心線。**8月中旬に自分で取得しないと消える**。二次利用条件は**未確認** |
| モバイル空間統計 人口マップ | https://mobakumap.jp/ | **500mメッシュ・1時間ごと**・無償閲覧 | **過去24時間のみ** | **当日実施必須**。商用は有償・外部埋め込み禁止 |

#### 死んでいる/使えないもの(COVID 由来の凍結が実際に起きている)

| 源 | 状況 |
|---|---|
| **MLIT/Agoop 全国の人流オープンデータ**(=リポの `data/jinryu/` の出所) | カタログ notes に「コロナウイルス対策調査の一環で公開したもので、**2022年以降の公開予定はございません**」と明文。**2019–2021 で確定停止**・1kmメッシュ・月次の昼/夜3区分のみ。→ **`data/jinryu/SOURCE.md` の記述と整合。更新は望めない**ことが確定した |
| RESAS API | **2025年3月24日 全サービス提供終了** |
| V-RESAS | 2024年3月31日 公開終了(後継 RAIDA) |
| 道路交通センサス | **自動車のみ・歩行者は対象外** |
| 東京都 COVID 人流ダッシュボード | 2023-12-31 更新終了 |

#### 絶対水準のアンカー(唯一の公的実測)

- **東京都における繁華街利用実態調査**(平成13年3月)
  <https://www.sangyo-rodo.metro.tokyo.lg.jp/toukei/pdf/monthly/chusho/hankagai.pdf>
  **渋谷センター街入口=全165地点で最多、平日 113,568人/12時間**。
  PDF 末尾に「本調査以降、同様の調査は行っていません」と明記。**26年前だが桁を較正できる唯一の公的実測値**。
- 「スクランブル交差点1日50万人」は出典が弱く(Wikipedia 経由・記事自身が「諸説ある」と注記)**そのまま使うべきではない**。

#### Google Popular Times — **公式 API は存在しない(確定)**

- Places API の Place Data Fields 全89フィールドを確認 → **popular times / busyness 系は1つも無い**。
- Google Maps Platform 規約 **§3.2.3(a) No Scraping** が "pre-fetch, index, store, reshare, or rehost"・
  "bulk download ... places information" を明示禁止。`populartimes` 系ライブラリは明確な違反で
  **論文用データとして採用不可**。
- **BestTime.app**(https://besttime.app/subscription/pricing): 現在「During the BestTime.app beta all plans are FREE.」と明記。
  日本カバレッジあり。**時間単位・0–100% の相対値・店舗単位**(街全体ではない)。ベータ=継続性リスク。
- Placer.ai=価格非公開・**日本への言及なし**→使えない。SafeGraph=Patterns は Advan Research へ売却済・**米国のみ**→使えない。
  Foursquare=混雑度としては不可だが POI マスタとしては有用。

#### 鉄道の乗降・混雑

- **ODPT に `odpt:PassengerSurvey` は存在**(14事業者)。ただしフィールドは `odpt:surveyYear` / `odpt:passengerJourneys` のみ
  = **年度単位の1日平均・時間分解能ゼロ**。かつ **JR東・東急は Challenge 2026 限定ライセンス**。東京メトロは基本ライセンス。
  GTFS-RT の `occupancy_status` は日本の鉄道事業者は概ね未提供。東京メトロ独自の開発者サイトは 2022-03-31 終了・ODPT へ移管済み。
- 東急電鉄(自社公開・FY2025)<https://www.tokyu.co.jp/railway/company/business/passengers/2025/>:
  東横線渋谷 **425,889人/日**、田園都市線渋谷 **619,956人/日**。
  **「相互乗換人員及び相互直通運転による通過人員を含む」と明記=渋谷で降りた人ではない**。補正必須。
- 東京メトロ FY2024 渋谷 **191,505人/日**。
- **JR東日本「各駅の乗車人員」は取得できなかった**(ブラウザ UA 付きでも **HTTP 403**。データセンタ IP を遮断している模様)。
  渋谷 FY2024 = 324,414人(全体5位)は検索結果経由の**間接情報=一次未確認**。**利用規約も未確認**。
- 国交省 都市鉄道の混雑率調査 **令和7年度実績が 2026-07-28 公表**
  <https://www.mlit.go.jp/report/press/tetsudo04_hh_000139.html>(東京圏平均143%)。PDF のみ。
  ただし**朝ピーク1時間のみ・調査は10-11月平日**=**8月中旬とは別物**。
- 大都市交通センサスは第13回・令和3年度が最新=**COVID 第4-6波の最中**。時間帯別 OD という構造は唯一無二だが、
  **水準には使えず形状のみ借用可**。

#### 有償プロバイダ(前提の訂正2点を含む)

- **GEOTRA はソフトバンク系ではない。三井物産と KDDI の合弁**
  (<https://news.kddi.com/kddi/corporate/newsrelease/2022/06/09/6106.html>)。
  合成データで個人単位トリップを生成する技術は本プロジェクトと設計思想が同型だが、仕様・価格・渋谷カバーは**全て未確認**。
- **unerry の現行プラットフォーム名は「Beacon Bank」**。「LOCATION AI PLATFORM」は公式サイト上で確認できず=**未確認**。

| プロバイダ | 空間 | 時間 | 遅延 | 費用 | 学術枠 |
|---|---|---|---|---|---|
| **KDDI Location Analyzer** | 最小125mメッシュ | 時間帯別・曜日別 | **最新3日前** | 非公開・**2週間無料トライアル** | 技研商事に「アカデミック向けキャンペーン」記載(条件未確認) |
| **モバイル空間統計** | 500m〜都心125m | **1時間ごと** | 未確認 | 非公開 | **公式に学術パッケージあり** <https://mobaku.jp/academic/> |
| Agoop | 最小50mメッシュ | 1時間〜数分 | 未確認 | 要問合せ | 未確認 |
| ソフトバンク 全国うごき統計 / ジオテクノロジーズ | 相談ベース / 125mメッシュ | 時間帯別 | 未確認 / 2021年〜月次 | 要問合せ / 要見積 | 未確認 |

**第一候補=KDDI Location Analyzer**(3日遅れ・125m・時間帯別で 2026年8月中旬を直接カバーでき、
かつ**渋谷区の公開値と突合できる**)。次点=モバイル空間統計(**学術枠が公式に明示されている唯一のプロバイダ**)。

### 3.4 店舗・テナント

| # | 源 | 実測/検証結果 | ライセンス | 判定 |
|---|---|---|---|---|
| 14 | **経済センサス** | 最新の**活動調査は令和3年(2021年6月)=5年前**。令和8年調査は**まさに今実施中(2026-06-01)だが公表は最速2027年5月末=間に合わない**。令和6年基礎調査(確報 2025-12-24)は「**雇用者のいない個人経営の事業所」が調査対象外**=渋谷の個人経営バー・カフェが相当数欠落 | 政府標準利用規約2.0=**CC BY 4.0 互換・商用可** | **○**。特に**町丁・大字レベルの産業中分類別事業所数**が最重要: <https://www.e-stat.go.jp/stat-search/files?page=1&layout=dataset&stat_infid=000040068156>(東京都全域 Excel)。「道玄坂1丁目に飲食店が何軒あるべきか」が取れる。e-Stat API は v3.0・登録必須・無料(レート制限**未確認**) |
| 15 | **OpenStreetMap**(Overpass で実測) | `area["name"="渋谷区"]["admin_level"="7"]`・`timestamp_osm_base = 2026-07-30T17:15Z`(**当日鮮度**): `shop=*` 1,747件中 `opening_hours` あり 446(**25.5%**)/ `amenity=restaurant` 1,048中 236(**22.5%**)/ cafe,fast_food,bar,pub 1,134中 291(**25.7%**)/ **合計 3,929中 973 = 24.8%** | **ODbL** | **○ 唯一の当日鮮度ソース**。※この 24.8% は「**OSM に載っている店の** 25%」であって「実在する店の 25%」ではない。**OSM 欠落率との突合は未実施=未確認**(上記 e-Stat 町丁・大字表で確定できる) |
| 16 | 国土数値情報 | **「商業施設」「大規模小売店舗」という名称のデータセットは存在しない**(一覧実査)。近い **P33 集客施設は 2014年度・非商用限定**(「有償刊行物を使用し作成したものですので商用利用はできません」)=使えない。営業時間属性を持つ点だけは注目に値する | — | **×**。使えるのは背景レイヤのみ(N03 行政区域 2025・CC BY 4.0 / A29 用途地域 / A55 都市計画決定情報) |
| 16b | 東京都 土地利用現況調査 GIS | 区部最新は**令和3年(2021)・371MB Shapefile** <https://data.storage.data.metro.tokyo.lg.jp/toshiseibi/R03.zip> | **カタログ上「その他」=条項未確認** | **△**。建物用途・延床面積の骨格としては最良だが属性スキーマも**未確認** |

> **★ ODbL の share-alike 問題(公開ミラーに直結)**: OSM から抽出した店舗テーブルは**ほぼ確実に Derivative Database**。
> 内部保持は「公に使用」に当たらないが、**配布した瞬間に §4.4 share-alike が発動**する。
> シム実行結果は Produced Work 寄りだが **§4.6 により Produced Work 公開時も元DBまたは差分の提供義務が生じ得る**
> 明確なグレーゾーンで、OSMF 自身も formal guideline の外に議論を置いている。
> **実務的安全策 = OSM 由来データを別ディレクトリへ隔離し ODbL 表記を付し、公開ミラーには含めない。**
> これは `STATUS.md` §3 の **PUB-U1(公開ミラーの除外範囲)** に直接効く材料である。
>
> 取得インフラ: Geofabrik `kanto-latest.osm.pbf` **458MB・2026-07-29 更新・ODbL 1.0**。
> Overpass は1日約10,000req・1GB 上限で、**実際に連続2リクエストで HTTP 429 が出たので並列は避けること**。

### 3.5 どのデータ源も埋めてくれない穴(正直な記載)

1. **お盆(8/13–16)の個人経営店の休業**。OSM の `opening_hours` に `PH off` はあってもお盆休業はほぼタグされていない。
   → **8月中旬スナップショットは通常週とは別モデルが必要**。
2. **時間帯別の絶対人数**を直接くれる公開ソースは存在しない(§3.3)。
3. **お盆期間の渋谷の通勤者減少率**の公開統計が見つからない。
4. 商業施設の正確な営業時間(SHIBUYA109 は robots.txt により取得せず)。

### 3.6 本調査で確認できなかった事項(未確認リスト)

渋谷区ダッシュボードの時間帯粒度(Power BI をレンダリングできず)/ JR東日本の乗車人員一次値・利用規約(403)/
Metro CrowdNavi の二次利用条件 / ODPT 基本ライセンス原文(SPA でレンダリング不可・`developer.odpt.org/terms` も本文取得不可)/
東京都 土地利用現況調査のライセンス条項と属性スキーマ / デジタル庁の自治体標準データセット完全項目リスト(e-Gov 404)/
各商業施設の正確な営業時間 / お盆期間の渋谷通勤者減少率 / GEOTRA・Agoop・unerry の価格と粒度 /
e-Stat API のレート制限 / SHIBUYA109 のイベントカレンダー有無(robots.txt 遵守のため未取得)/
JMA 10分値の提供開始年 / 熱中症警戒アラートの発表時刻・運用期間・特別警戒との基準差 /
Open-Meteo 有料プランの実額 / ISO/IEC 30173:2023 の定義原文(有償)/
Digital Twin Consortium の定義原文(公式ページが **HTTP 403** で再取得できず、検索結果由来の引用)

---

## §4 journal 等級リアルデータ注入の設計案

### 4.0 前提: いま core が外界に触れる経路(実査)

`src/society/` 配下で外部を読むのは次だけである(grep 実査)。

| 経路 | 場所 | タイミング |
|---|---|---|
| シナリオイベント JSON | `engine/simulation.py:680-693`(`world.events_file`・既定 null=`conf/config.yaml:266`) | **init 時のみ** |
| ペルソナ名簿・icebreak 語彙・感情辞書 | `simulation.py:772,1099`・`lang/sentiment.py:69` | **init 時のみ** |
| バス静的表 | `bus_table.py:123`(`load_bus_table`) | **init 時のみ** |
| checkpoint gzip | `engine/checkpoint.py:144,152`・`simulation.py:1298,1317` | 保存/復元時 |
| **ネットワーク** | **`llm/anthropic.py:25-26,50-52`(urllib)だけ** | LLM 呼び出し時 |

**= 現在、シム本体がラン中にネットワークへ出る唯一の経路は LLM である。**
「ラン中に実データを読む」を入れるということは、**非決定論の侵入口を1つから2つに増やす**という意味であり、
これは設計上の重大な変更として扱うべき。以下の3案はこの点で明確に分かれる。

### 4.1 案A(推奨・**strict 等級を維持**): 事前スナップショット materialization

**考え方**: ラン中は外部を一切読まない。ラン**前**に「その期間の現実」を1枚のテーブルへ焼き込み、
既存の静的ファイル読み込み経路に流す。**外部の非決定論はラン開始前に消える。**

```
[ラン前・オフライン]
  scripts/fetch_snapshot.py(新規)
    ├ 気象:  JMA obsdl/etrn 10分値 or bosai AMeDAS JSON → 日次+時刻別へ集約
    ├ 暑さ:  環境省 WBGT getSurveyData(毎時・Tg/Tw 付き)
    ├ 予報/警報: JMA 防災情報XML(熱中症警戒アラート等)→ world_event 行へ
    ├ 店:    OSM opening_hours(既存 Overpass 応答に既に含まれる=§2.8-5)
    └ イベント: 手作業で確定した渋谷の実イベント表(§3.2)
                        ↓
  data/snapshot/shibuya_<期間>.json   ← 単一の凍結ファイル(SHA-256 を manifest に記録)
                        ↓
[ラン中]  既存経路だけを使う:
   天候      → weather.py に「表引きモード」を1本足す(現行 _sample と排他・既定は現行)
   店の開閉  → world.mod.open_hours(cats は実効・pois は要実装=§2.6)
   イベント  → world.events_file(既存・init 時読み込み・news/SNS へ配信=scheduler.py:2688-2703)
   ダイヤ    → transit_odpt.json(既存)+ bus_table(表を生成すれば既存の読み手が動く)
```

- **repro_tier = strict を維持できる。** 乱数を引かない表引きなので、`weather` stream の draw が消える。
  → **既存ゴールデンとの L1 バイト一致は「表引きモード OFF のとき」に限り成立**(R1 の通常の作法どおり)。
  表引き ON は別ゴールデン。
- **記録すべきもの**: スナップショットファイルの **SHA-256・取得日時・各データ源の URL とライセンス文字列・
  対象期間・欠測の埋め方**。現在これらは**どこにも記録されていない**(§2.7)ので新規。
  第71バッチの `run_manifest.json` に `inputs: [{path, sha256, source_url, license, fetched_at, coverage}]` を
  足すのが最も安い。
- **★ この設計にはリポ内に先例がある(重要)**: 「外界の非決定論を**ロード時に1回だけ解決し、具体値として
  config スナップショットへ凍結する**」というパターンを既に2箇所で使っている。
  ```
  src/society/config.py:216-219   world.calendar.start_date == "auto" → datetime.date.today() へ解決し
                                  「以後は具体日付として凍結(config スナップショットに具体日付が残る=
                                   resume/再現が安定。tests は "auto" を使わない)」
  scripts/run.py:47-80,116-129    run.seed=auto → OS エントロピーから採取し config.yaml/summary.json へ記録
                                  =「選ばないだけで失わない」
  ```
  **スナップショットデータも全く同じ作法に乗せればよい**(=解決して凍結し、記録する)。
  新しい設計思想を導入する必要はなく、**既存パターンの第3の適用先**として提案できる。
  なお `start_date: "auto"` は `production/daily/longrun30` で既定(`production.yaml:34` 他)なので、
  8/16 開始なら暦は自動的に 2026-08-16 になり、`weather.py` の月別バイアスも 8月になる。
- **弱点**: 本選期間(8/15–8/30)の天候は**事前に確定できない**。10日ラン(8/16–8/26)を回しながら
  「昨日までの実天候」を使うには、日次でスナップショットを継ぎ足す運用(=案Bの弱版)になる。

### 4.2 案B(**journal 等級**): 日次 materialization + ラン内 resume(現実的な折衷)

**考え方**: ラン中にネットワークへは出ない。しかし**1日1回、checkpoint 境界でスナップショット表を差し替える**。
既存の checkpoint/resume 機構(バイト一致 resume が検収済み)にそのまま乗る。

```
毎朝(人手 or cron):
  1. scripts/fetch_snapshot.py --day 2026-08-17   → data/snapshot/day_2026-08-17.json(SHA-256 記録)
  2. ランは前夜の checkpoint から resume。resume 時に当日ぶんの表を読む
  3. 読んだ表の {sha256, 取得時刻, 全値} を **journal へ丸ごと追記**
事後:
  journal から表を復元 → 同じ seed + 同じ表列 → 完全再生
```

- **repro_tier = journal。** 「seed だけからは再現できないが、記録から完全に再生できる」の教科書的な形。
  [dual-mode-observe-verify-plan.md](../plans/dual-mode-observe-verify-plan.md) 第71/第72バッチの
  ジャーナル+ランモードに**そのまま乗る**(新機構が要らない)。
- **REPLAY 時の規律**: 表が journal に無ければ**即 fail**(silent fallback 禁止)。
  これは第71バッチの LLM キャッシュ fail-fast と**同じ規律を同じ場所に適用するだけ**。
- **記録すべきもの(これが揃えば再生可能)**:
  1. 各日の表の**全内容**(ハッシュだけでは不可。外部 URL は消える・改訂される)
  2. 取得時刻(JST)と取得元 URL・API パラメータ
  3. 欠測時に何で埋めたか(合成フォールバックの発火記録)
  4. 表を読んだ **sim step / sim_min**(いつ効き始めたか)
  5. 表のスキーマバージョン
- **弱点**: 運用に人手または cron が要る。**10日間、毎朝失敗せずに回す必要**があり、失敗時のフォールバック
  (=合成天候へ後退し、その旨を記録)を必ず設計しておくこと。

### 4.3 案C(**journal 等級・非推奨だが検討対象**): ラン中の直接 fetch(read-only forcing)

**考え方**: scheduler の日境界フック(`scheduler.py:3428-3452`)から直接 API を叩き、返り値を journal へ書く。

- **repro_tier = journal**(記録すれば再生できる点は案Bと同じ)。
- **なぜ非推奨か**:
  1. §4.0 のとおり **core のネットワーク出口が2つになる**。`Clock`/`RandomSource` を core から締め出した
     設計思想(T8 が既に成立している)と逆行する。
  2. API 障害・レート制限・タイムアウトが**シムの進行を止めうる**。10日ランの途中で落ちる理由を1つ増やす。
  3. 案Bと比べて得られるものが「粒度が10分になる」だけで、**シムの step が10分**なので実利益がほぼ無い。
- **もし採るなら**: fetch は必ず**別スレッド/別プロセスで先読みし、core は既に materialize 済みの表を読むだけ**にする。
  = 実質的に案Bへ収束する。**この検討の結論は「案Cは案Bへ縮退させるのが正しい」。**

### 4.4 3案の比較

| | 案A 事前 | 案B 日次+resume | 案C ラン中 fetch |
|---|---|---|---|
| repro_tier | **strict** | **journal** | journal |
| core のネットワーク出口 | 1(LLM のみ) | 1(LLM のみ) | **2** |
| 本選期間の実天候を使えるか | ✕(事前確定不可) | **○** | ○ |
| 既存機構への乗り方 | 静的ファイル読み(既存) | **checkpoint/resume+journal(既存/実装予定)** | 新規 |
| 実装量 | 小(fetch スクリプト+表引き) | 中(+journal 連携) | 中〜大(+障害設計) |
| 10日ラン中の運用リスク | なし | 中(毎朝の取得) | **高** |
| 推奨 | **本命**(過去日の再現・対照ラン) | **本選ランの本命** | **案Bへ縮退させる** |

**結論(§4)**: 「**A を土台に、本選ランでは B を使う**」。C は採らない。
これにより、**verify ラン(過去日を凍結スナップショットで再現)は strict、観察ラン(本選期間のライブ天候)は journal**
という二重化が、[dual-mode-observe-verify-plan.md](../plans/dual-mode-observe-verify-plan.md) の
`repro_tier` 設計にそのまま収まる。

### 4.5 どのデータをどのレイヤへ入れるか(注入点の対応表)

| 現実の要素 | 注入点(既存/要実装) | 等級 | 備考 |
|---|---|---|---|
| 建物形状・高さ・地形 | `data/plateau/*` + `world.heights`(既存) | strict | 更新は年1回で十分 |
| 道路・POI 位置 | `build_map.py --osm-date`(既存 attic query) | strict | **基準日を本選近くへ更新する価値あり**(現 2025-04-01) |
| **店の営業時間** | `world.mod.open_hours.cats`(実効)/ `.pois`(**予約・未消費**) | strict | OSM `opening_hours` は既に生応答にある(§2.8-5) |
| 鉄道ダイヤ | `data/transit_odpt.json`(既存) | strict | **観察ランが読んでいない**(§2.8-1) |
| バスダイヤ | `bus_table`(読み手のみ・表が未生成) | strict | `build_bus_table.py` を1回走らせるだけ |
| **天候・気温・WBGT** | `weather.py` に表引きモードを追加(要実装) | strict(過去日) / **journal(本選期間)** | **最大の空白**(§2.3) |
| 気象警報・熱中症アラート | `world.events_file`(既存・news/SNS 配信) | strict / journal | 既存機構でそのまま入る |
| 実イベント(花火・セール等) | 同上 + `annual_events`(群集バイアス) | strict | §3.2 |
| 人流(在場曲線) | 較正のみ(`presence` の conf 値) | **ラン中注入しない** | 前回 §8.3 の結論を維持 |
| エージェントの位置・状態 | **注入しない** | — | §1.3 の C。研究設計上の禁止 |

### 4.6 先行研究・先行実装(この設計は独創ではなく、既存の4パターンの組み合わせである)

本ノートの案A/案Bは、業界横断で**すでに名前がついている4つのパターン**の組み合わせに過ぎない。
これは弱点ではなく強みで、**「我々はこの分野の標準作法に従った」と引用つきで言える**。

#### パターン1: 境界での副作用記録(Side-Effect Recording / Logging Gateway)

> 外部世界に触れる関数を1箇所に集約し、**その戻り値を実行ログに書き込む**。リプレイ時はその関数を呼ばず、ログから値を返す。

- **Martin Fowler "Event Sourcing"(2005)** の **External Queries** 節が最も直接的な先行文献。逐語:
  「The primary problem with external queries is that the data that they return has an effect on the results on handling an event.」
  「**One approach is to design the gateway to the external system so that it remembers the responses to its queries and uses them during replay.**」
  例示が「12月5日に取得した為替レートを12月20日に再生するとき、**当時のレート**が要る」= **気象データ取得と完全に同型**。
  <https://martinfowler.com/eaaDev/EventSourcing.html>
- **Temporal**: `workflow.SideEffect`「executes the provided function once, records its result into the workflow history.
  **The recorded result on history will be returned without executing the provided function during replay.**」/
  `workflow.Now`「**Now returns the time when the workflow task was first started, even during replay.**」/
  Workflow Definition「Workflow code must be deterministic to support replay. To handle non-deterministic operations
  like API calls, **LLM/AI invocations**, database queries … put them in Activities.」
  <https://pkg.go.dev/go.temporal.io/sdk/workflow> / <https://docs.temporal.io/workflow-definition> / <https://docs.temporal.io/develop/go/side-effects>
  - **★ 設計に効く発見**: Temporal は「毎回記録する `SideEffect`」と「**値が変わったときだけ記録する `MutableSideEffect`**」を分けている。
    天候のように**更新が疎な外部入力**にはログサイズの観点で後者の考え方が効く。
- Alvaro, P. & Quinn, A. (2024) "Deterministic Record-and-Replay." *ACM Queue* 22(4):120–129. DOI `10.1145/3688088`
  — 「実行状態の大半は保存せず、プロセスの**非決定的アクションの情報だけ**を保存する」。
- **本プロジェクトへの含意**: 気象 API 取得も **LLM 呼び出しも同じ扱い**になる。
  LLM はホスト推論の性質上 temperature=0 でも bit 再現しないため「還元不能な非決定的入力」として応答を記録するほかない
  (この点の**査読付き一次ソースは未確認**・技術記事レベルでは複数一致)。
  = **第71バッチの LLM ジャーナルと、S3/S4 の天候ジャーナルは同じ機構でよい。**

#### パターン2: 時刻も入力として journal する(Full Input Trace)

- **John Carmack, .plan 1998-10-14**(Quake 3 のイベントジャーナリング)逐語:
  「I settled on combining all forms of input into a single system event queue」
  「**Journaling of time along with other inputs turns a realtime application into a batch process,
  with all the attendant benefits for quality control and debugging.**」
  <https://github.com/ESWAT/john-carmack-plan-archive/blob/master/by_day/johnc_plan_19981014.txt>
  / 解説 <https://fabiensanglard.net/quake3/>(`sysEvent_t eventQue[256]`)
- O'Callahan, R. et al. (2017) "Engineering Record And Replay For Deployability." *USENIX ATC 2017*. arXiv 1705.05937 —
  OS レベルで同じことをやる(`rr`)。
- Chen, Y. et al. (2015) "Deterministic Replay: A Survey." *ACM Computing Surveys* 48(2):1–47. DOI `10.1145/2790077`
- **本プロジェクトへの含意**: **リポは既にこの規律を満たしている**。
  `src/` に `datetime.now()`・グローバル乱数が grep ゼロ(= 指示書の T8 が現行で既に成立)であり、
  外界への口は LLM の1本だけ(§4.0)。**「入力の口を1つに絞る」という構造的規律は達成済みで、
  だからこそパターン1の追加が自明に安く済む。**

#### パターン3: 入力ログ vs 状態ログの選択

| | 入力再生(極A) | 状態記録(極B) |
|---|---|---|
| 例 | DOOM demo / Age of Empires recorded game / Quake 3 journal | Quake DEM / **Unreal Engine Replay System** / **CARLA recorder** |
| 容量 | 極小 | 大(CARLA: 車両100・信号50で**約200MB/時**) |
| 頑健性 | **極めて脆い** | バージョン差を吸収可(UE 4.13 以降はプロパティ追加/削除を吸収) |
| 決定性要求 | **必須** | 不要 |

- Bettner, P. & Terrano, M. (2001) "1500 Archers on a 28.8." *Game Developer* 逐語:
  「run the exact same simulation on each machine, passing each an identical set of commands」
  「**Because our simulation is deterministic … a game recording gave us a great way of passing around repro cases**」
  脆さの実例:「**A deer slightly out of alignment when the random map was created would forage slightly differently
  — and minutes later a villager would path a tiny bit off.**」
  <https://www.gamedeveloper.com/programming/1500-archers-on-a-28-8-network-programming-in-age-of-empires-and-beyond>
- Unreal Replay System は極B(レプリケーションデータを記録=**シミュレーションの決定性を要求しない**)。
  <https://dev.epicgames.com/documentation/en-us/unreal-engine/using-the-replay-system-in-unreal-engine>
- CARLA の決定性要件(一次ドキュメント): 同期モード+fixed delta seconds / 同期を有効にしてから world をロード /
  試行ごとに world をリロード / コマンドは batch 発行。<https://carla.readthedocs.io/en/latest/adv_synchrony_timestep/>
  **recorder ページには決定論的リプレイの保証が書かれていない**のが示唆的。
- **本プロジェクトの現在地**: L1 は**極A寄り**(意思決定の記録)+**checkpoint という極B**の併用=
  rr や CARLA が示す実務的折衷(**定期チェックポイント+その間の入力ログ**)に既に到達している。
  第71バッチの LLM ジャーナルはここに「還元不能な非決定的入力」を足す作業である。

#### パターン4: 取り込んだデータを成果物として凍結し、以後はそれで駆動する(**業界標準・案Aの正体**)

**記録すべきもの(この4点が揃って初めて再生できる)**:
1. 凍結した強制データファイル本体(**内容ハッシュで固定**)
2. **RNG シード** — ★ 天候ファイルだけでは軌道は決まらない。
   EMOD(疫学 ABM)の `Enable_Rainfall_Stochasticity` は「daily rainfalls drawn from an exponential distribution
   with the same daily mean」であり、**気候ファイル+シードの両方が要る**。
   <https://emod.idmod.org/emodpy-malaria/emod/software-climate/>
3. コード/モデルのバージョン
4. **プロヴェナンス**: 出所・取得時刻・シム時刻との対応・単位・既知のバイアスと不確かさ

**この形が業界標準であることの証拠**:

- **★ ODD プロトコル Element 6「Input data」が、まさに本件のための正式な記述枠である。**
  Grimm, V. et al. (2010) *Ecological Modelling* 221(23):2760–2768. DOI `10.1016/j.ecolmodel.2010.08.019` 逐語:
  「dynamics are often driven in part by a time series of environmental variables, sometimes called **external forcings**…
  these environmental variables are not themselves affected by the internal variables of the model」
  「**Obviously, to replicate an ABM, any such input has to be specified and the data or models provided**」
  「If a model does not use external data, this element should nevertheless be included, using the statement:
  **"the model does not use input data to represent time-varying processes."**」
  Grimm, V. et al. (2020) "The ODD Protocol … A Second Update." *JASSS* 23(2):7. DOI `10.18564/jasss.4259` 逐語
  (<https://www.jasss.org/23/2/7/S1-ODD.pdf>):
  「Often, the input data are values observed in reality (**e.g., from a weather station** or stock market records)」
  「**To make an ABM reproducible, we need to define any input data that drive it. To reproduce specific model results,
  we need to provide the input data; and to fully justify the results we need to explain where the data came from
  and document their uncertainties, biases, and other limitations.**」
  - **境界線(重要)**: ODD は「外部か否か」ではなく「**いつ入るか**」で分ける。
    t=0 のセットアップにしか使わない外部データは **Element 5 Initialization** 側、
    時間変化する強制項は **Element 6 Input data** 側。
    → **案A(事前凍結・全期間の表)は Element 6、幾何スナップショットは Element 5** と書き分けるのが正しい。
  - 遵守率の実測(ODD 2010 逐語):「The element 'Input' was included correctly in only **62%** of the publications」。
    = **ここを丁寧に書くだけで上位38%に入る。**
- 天候ファイル駆動の実装例(すべて「実測年の気象を1ファイルに凍結して駆動」する形):
  **DSSAT** Weather Module(欠測は WGEN で生成)<https://dssat.net/weather-module/> /
  **APSIM** Met module(毎日 `newmet` をブロードキャストする純粋な一方向日次ドライバ)
  <https://www.apsim.info/documentation/model-documentation/infrastructure-and-management-documentation/met/> /
  **EnergyPlus EPW**(ヘッダ8行+8,760行=1時間×1年。**TMY(典型年)と AMY(Actual Meteorological Year=実測年)の
  使い分けが制度化されている**)<https://designbuilder.co.uk/cahelp/Content/EnergyPlusWeatherFileFormat.htm>
- **Microsoft Flight Simulator** — 「ライブ=非決定的 / ファイル=決定的」の**二値が設計に埋め込まれている**:
  `.FLT` のフラグ `UseWeatherFile` / `UseLiveWeather` / `WeatherPresetFile` / `FixedClouds`
  <https://docs.flightsimulator.com/html/Content_Configuration/Flights_And_Missions/Flight_Definitions.htm> /
  決定的な天候ファイル `.WPR` XML プリセット
  <https://docs.flightsimulator.com/msfs2024/html/5_Content_Configuration/Mission_XML_Files/Weather_XML_Properties.htm>。
  ライブ天候のプロバイダは **meteoblue**(更新は日次→時間毎→**15分間隔**、地表を約2.5億の格子、大気60層)
  <https://www.meteoblue.com/en/blog/article/show/40088_meteoblue+live+weather+data+in+Microsoft+Flight+Simulator>。
  **ライブ天候のスナップショット保存機能は存在しない**(`.FLT` が保存するのは天候「モード/参照」であって「状態」ではない)。
  実務での回避策は「we have a standardised set of WPR preset files and all our pilots install those as a Community package」
  <https://devsupport.flightsimulator.com/t/were-really-struggling-the-weather-api/17455>。
  【未確認】METAR 直接取り込みの公式言明・Asobo による決定性への公式言及。
- **X-Plane — 非決定性を公式に明言している(最も正直な先行例)**:
  「The sim's weather is made up of many more datasources than a single METAR entry. … There is a certain amount of
  randomness involved too.」「**This randomness is different for each airport, and for each launch of the sim**」
  <https://developer.x-plane.com/article/a-metar-does-not-tell-you-the-sims-weather/>。
  そのうえで再現手段を4つ用意している: **weather dump**(「**reproduce the exact conditions, including all data
  and randomness**」= 乱数込みの状態シリアライズ)/ サーバ側リプレイ(12.1.0)/
  **Historic Weather(12.3.0・2025年9月・過去1年まで遡及)**
  <https://www.x-plane.com/kb/x-plane-12-3-0-release-notes/> / situation file。
  → **「ライブ天候ランは再現不可能。再現したいなら凍結ファイルへ切り替える」という結論に、
  2つの主要フライトシムが独立に到達している。**
- **Cities: Skylines / II は実天候を取り込まない**(正直な陰性確認)。緯度経度から**手続き的生成**。
  <https://www.paradoxinteractive.com/games/cities-skylines-ii/features/climate-seasons>
  **「ライブ天候フィードで駆動される都市シミュレーション」の一次ソースは発見できなかった(未確認)**。
  ライブフィード駆動が実在するのは**交通センサ層のみ**(下記)。
- **交通センサの実カウント流でシムを駆動する実例(=案Cの唯一の成功例)**:
  Kušić, K., Schumann, R., Ivanjko, E. (2022) "Building a Motorway Digital Twin in SUMO: Real-Time Simulation of
  Continuous Data Stream from Traffic Counters." *ELMAR 2022*, 71–76. DOI `10.1109/ELMAR55880.2022.9899796` /
  雑誌版 (2023) *Advanced Engineering Informatics* 55:101858. DOI `10.1016/j.aei.2022.101858`。
  ジュネーブ高速道路の実カウンタ流を SUMO の **Calibrator** へ **TraCI** 経由で流す。
  コード <https://github.com/SiLab-group/DigitalTwin_GenevaMotorway>。
  SUMO の3層(オフライン需要生成 `routeSampler.py` / ラン中の流量補正 `Calibrator`(**ファイル駆動**)/
  オンライン制御 `TraCI`)は**そのまま我々の案A/案B/案Cの3層に対応する**。
- プロヴェナンス層: **W3C PROV-O**(Recommendation 2013-04-30。`prov:Entity` / `prov:Activity` / `prov:used` /
  `prov:wasGeneratedBy` / `prov:wasDerivedFrom` / `prov:generatedAtTime` の実在を公式 Turtle で照合済)
  <https://www.w3.org/TR/prov-o/> / 梱包層 **RO-Crate**(Soiland-Reyes et al. 2022, *Data Science* 5(2):97–138.
  DOI `10.3233/DS-210053`)。
- **★ ABM 特化の直接の先行研究: ODD+P**
  Reinhardt, O., Ruscheinski, A., Uhrmacher, A.M. (2018) "ODD+P: Complementing the ODD Protocol with Provenance
  Information." *WSC 2018*, 727–738. DOI `10.1109/WSC.2018.8632481`
  (PDF <https://www.informs-sim.org/wsc18papers/includes/files/060.pdf>)逐語:
  「Model documentation standards such as the ODD protocol … are mostly concerned with **'what has been generated',
  and less with 'how it has been generated'**. … **simulation experiments play a crucial role, and are treated as
  first class artifacts, as are simulation models, data sources, and theories.** … The approach is of particular value
  for models that are **based on various data sources**」
  ※ Crossref のメタデータ自体が "Andreas Rucheinski" と誤植。正しくは **Ruscheinski**。
  ※ ODD+P の土台は PROV ではなく OPM。**ABM に SED-ML 相当の機械可読標準は存在しない(発見できず=未確認)**。

#### 補助的な概念装備(命名が有用なもの)

| 概念 | 内容 | 出典 |
|---|---|---|
| **スナップショット初期化→自由走行は標準作法** | ECMWF DestinE のツインは連続同期ではなく「**解析(analysis)からの初期化→自由走行予報**」。「Digital twin simulations are **initialized using operational (re-)analyses** … through data assimilation techniques」。Extremes DT は「**on-demand** … a timescale of a few days ahead」 | <https://www.ecmwf.int/en/about/what-we-do/environmental-services-and-future-vision/destination-earth> / <https://destine.ecmwf.int/digital-twins/> |
| **「乖離」には固有名詞がある** | **"pose divergence" / "simulation drift"**「the deviation between the AV's behavior in driving logs and its behavior during simulation」。さらに**バイアスの向きまで特定済み**:「**log-playback agents tend to heavily overestimate the aggressiveness of real actors, as they are unwilling to deviate from their planned route under any circumstances**」 | Montali, N. et al. (2023) "The Waymo Open Sim Agents Challenge." arXiv **2305.12032**, NeurIPS 2023 D&B |
| **評価モードの階段** | `open-loop`(採点のみ・相互作用なし)→ `closed-loop non-reactive`(自分だけ動く・**他者はログ再生**)→ `closed-loop reactive`(他者も反応するが、反応モデルの妥当性が新たな未検証点になる) | nuPlan devkit 公式 <https://nuplan-devkit.readthedocs.io/en/latest/competition.html>(Caesar, H. et al. arXiv 2106.11810) |
| **摂動の3分類** | Behavior permutation / Content permutation / **Style permutation(天候・照明・時刻・地理の差し替え)** | NVIDIA <https://www.nvidia.com/en-us/use-cases/autonomous-vehicle-simulation/> |
| **再構成型シムの原理的限界** | 「reconstruction-based neural simulators … are **fundamentally constrained by their initial captured data** and struggle to generalize to highly dynamic or novel scenes」 | NVIDIA OmniDreams (2026) arXiv **2606.03159** |
| **社会シムの DT 化という潮流** | Social Digital Twins を "high-fidelity, data-driven representations of real-world socio-technical systems" と定義 | Cau, E., Failla, A., Pansanella, V., Rossetti, G. (2026) "Social Simulations: from Agent-Based Modeling to Digital Twins." arXiv **2607.13693**(2026-07-15) |

#### 混同してはいけない先行研究(**復活しない側**の文献)

以下は**すべて二方向(同化=実データが内部状態を書き換える)**であり、§1.3 の C に該当する。
本ノートの案A/案Bとは**別カテゴリ**なので、引用時に混ぜないこと。

- Ward, J.A., Evans, A.J., Malleson, N.S. (2016) "Dynamic calibration of agent-based models using data assimilation."
  *Royal Society Open Science* 3(4):150703. DOI `10.1098/rsos.150703`
- Malleson, N. et al. (2020) "Simulating Crowds in Real Time with Agent-Based Modelling and a Particle Filter."
  *JASSS* 23(3):3. DOI `10.18564/jasss.4266` 逐語:「there are no established mechanisms for incorporating real-time
  data into simulations」
- Clay, R. et al. (2021) *Simulation Modelling Practice and Theory* 113:102386. DOI `10.1016/j.simpat.2021.102386`
- Suchak, K. et al. (2024) "Coupling an agent-based model and an ensemble Kalman filter for real-time crowd modelling."
  *Royal Society Open Science* 11(4):231553. DOI `10.1098/rsos.231553` 逐語:
  「**even a perfectly calibrated model will diverge from a real system over time**」
- Ghorbani, A. et al. (2023) "Data Assimilation for Agent-Based Models." *Mathematics* 11(20):4296. DOI `10.3390/math11204296`

**一方向強制(forcing)側の実例**(=我々が引くべき側):
- Singh, D.E. et al. (2020) "Evaluating the impact of the weather conditions on the influenza propagation."
  *BMC Infectious Diseases* 20:265. DOI `10.1186/s12879-020-04977-w` — EpiGraph に**スペイン気象庁 AEMET の
  2011年実測(気温・気圧・相対湿度、10分間隔)を92都市分投入**し R0 を時間依存化。**天候→疫学の一方向**。
- Pascoe, L. et al. (2022) "Review of Importance of Weather and Environmental Variables in Agent-Based Arbovirus Models."
  *IJERPH* 19(23):15578. DOI `10.3390/ijerph192315578`

---

## §5 スナップショット忠実度 KPI 案

### 5.0 設計方針

**測るのは「乖離ゼロ」ではない**(§1 含意3)。測るのは次の3つ。

1. **入力忠実度(t=0 の切り取り精度)**: 建物・ダイヤ・店・天候の**入力そのもの**が現実とどれだけ一致しているか。
   ここは決定論的に検証でき、乱数も LLM も関与しない。**最も正直に数字が言える層。**
2. **応答忠実度(強制項→行動の弾性)**: 「気温が1℃上がると外出がどれだけ減るか」等の**反応の傾き**が現実の実測と同符号・同オーダーか。
   ここが合っていないと「実天候を入れた」ことに意味が無い。
3. **乖離の追跡(t>0)**: 何日目でどの指標が系統的に離れるか。**離れること自体は失敗ではない**が、
   「いつ・どの指標が・どちらへ」離れるかは報告義務がある。

方法論の枠組みとしては **Pattern-Oriented Modeling**(複数スケール・複数パターンで同時に当てにいく)を採る。
単一指標のフィッティングを避けるための標準的作法である
([Grimm et al. 2005, *Science* 310(5750):987-991, DOI 10.1126/science.1116681](https://www.science.org/doi/10.1126/science.1116681))。
実装形式は既存の `scripts/calibrate_report.py:44-106` の `REALITY` バンド表への**行追加**とし、
「直接統計が無いならプロキシ帯+出典を書き、捏造しない」既存流儀(`:93-96`)を踏襲する。

**用語を借りる**: 3 の「乖離」には既に固有名詞がある — **"pose divergence" / "simulation drift"**
(Montali et al. 2023, *The Waymo Open Sim Agents Challenge*, arXiv 2305.12032)。
同論文は**バイアスの向きまで特定**しており、「**log-playback agents tend to heavily overestimate the aggressiveness
of real actors, as they are unwilling to deviate from their planned route under any circumstances**」=
**ログ再生する他者は現実より「頑固」に見える**。我々が実イベント表や実ダイヤを固定して回すとき、
同型のバイアス(「街が予定どおりに動きすぎる」)が入りうる。**この既知バイアスを引用して限界を明記できる。**

**報告の枠を借りる**: 忠実度の記載は **ODD プロトコル Element 6「Input data」**に載せると規格準拠になる
(§4.6・Grimm et al. 2020 *JASSS* 23(2):7)。逐語要求は
「**we need to provide the input data; and to fully justify the results we need to explain where the data came from
and document their uncertainties, biases, and other limitations.**」= §5.3 と §3.5/§3.6 がそのまま該当する。

### 5.1 いま既に分かっている乖離(実査+一次統計の突き合わせ)

これは本調査で**実際に計算した**もので、KPI 以前の「現状値」である。

| 項目 | シムの値 | 現実の値 | 乖離 |
|---|---|---|---|
| 8月の日最高気温の中心 | **32℃**(`weather.py:26` `8: (32, 25, 0.30, 0.0)`) | **31.3℃**(東京・平年値 1991-2020) | +0.7℃。良好 |
| 8月の日最低気温の中心 | **25℃**(同上) | **23.5℃**(同上) | **+1.5℃**。やや高い |
| 8月の日々のゆらぎ | `rng.integers(-3,4)` = **一様 ±3℃**(`weather.py:68-69`) | 実際の日々変動は一様分布ではない(連続する猛暑・梅雨明け直後の階段状変化) | **分布形が違う** |
| 8月の猛暑日(35℃以上)の出現率 | シムの最高気温は 29–35℃ の一様7値 → **35℃ちょうどが 1/7 ≈ 14%**。36℃以上は**出現不可能** | 東京 2025年8月: **8/23 時点で月12回目**=8月として統計開始以来最多。**8/18–27 は10日連続猛暑日** | **構造的に過小**。「連続猛暑」という現象がシムでは原理的に起きない |
| 8月の雨の重み | **0.30**(同上) | `calibrate_report.py:73-74` の帯「降雨日の割合(7-8月) 0.25–0.55」の下端寄り。東京8月の月降水量平年値 **154.7mm** | 帯内だが下端。降水量[mm]の概念自体がシムに無い |
| 天候の空間・時間粒度 | **1日1回・全市共通・カテゴリ4種+最高/最低気温** | 実測は10分値/毎時値・降水量[mm]・湿度・風・WBGT | **粒度が2桁足りない** |

> **★ 最重要**: 本選の10日ラン想定期間は **8/16–8/26**([dual-mode-observe-verify-plan.md](../plans/dual-mode-observe-verify-plan.md) 冒頭)。
> 2025年に東京都心で10日連続猛暑日となった **8/18–8/27** とほぼ完全に重なる。
> 現行の合成天候では、この期間の渋谷で最も支配的な環境要因(連続する極端な暑さ)が**再現されない**。
> 「8月中旬の渋谷をスナップショットする」という目的に対して、天候は単に粗いのではなく**現象を落としている**。

出典: [気象庁 平年値(東京・47662)](https://www.data.jma.go.jp/stats/etrn/view/nml_sfc_ym.php?prec_no=44&block_no=47662)
(統計期間 1991–2020)/ [tenki.jp 2025-08-23 「東京都心で今月12回目の35℃以上 8月の猛暑日日数が統計開始以来最多に」](https://tenki.jp/forecaster/deskpart/2025/08/23/35353.html)/
[tenki.jp 2025-08-26 「東京都心で猛暑日日数が過去最多・最長タイ記録 猛暑日は9日連続・年間22日目」](https://tenki.jp/forecaster/deskpart/2025/08/26/35397.html)/
[気象庁 2025年の猛暑日・真夏日などの日数](https://www.data.jma.go.jp/stats/stat/202515/tem_ctg_days_202515.html)
(本調査の読み取りでは東京の8月=猛暑日18日・真夏日29日・熱帯夜24日だが、上記報道値との突き合わせは未実施=**要再確認**)。
なお東京の観測地点は2014年12月に大手町から**北の丸公園**へ移転しているため、長期比較には不連続がある(【未確認】移転補正の扱い)。

### 5.2 KPI 候補(REALITY 表への追加案)

#### (A) 入力忠実度 — 決定論的に検証できる層

| key(案) | 指標 | 判定基準の考え方 | 現実側データ |
|---|---|---|---|
| `wx_tmax_mae` | 日最高気温の MAE[℃](シム日次 vs 実観測日次) | 実データ注入時は **0**(恒等)。合成時は現状 3–5℃ 級と推定 | 気象庁 日別値 |
| `wx_hotday_share` | 猛暑日(35℃以上)の日割合 | 実期間の実測値と ±0.1 以内 | 同上 |
| `wx_rain_day_share` | 降水日(1mm以上)の割合 | 既存 `rainy_share` 帯 0.25–0.55 を実期間値へ差し替え | 同上 |
| `transit_real_share` | ダイヤ行のうち `source` が「実ダイヤ」の割合 | **実測: `transit_odpt.json` = 6/9 = 66.7%**(`transit_shibuya.json` = **0/9**)。§2.2 | 自己検査 |
| `poi_hours_real_share` | 営業時間が実店舗由来の POI の割合 | **実測: 0%**。現状は 1,975 POI に対し **3種類の営業時間**しか無い(`commerce.py:39-43` food 11-23 / shop 10-21 / nightlife 18-5)。内訳 food 730・shop 596・nightlife 235 = **1,561 POI が3スケジュールを共有**、残り **414 POI は常時営業扱い** | OSM `opening_hours` 等 |
| `bldg_height_match_rate` | 実高さが照合できた建物の割合 | 実測 **3,531 / 6,311 = 55.9%**(§2.1・PLATEAU 側母数)。OSM 側母数(7,210 建物)なら **49.0%**。**どちらの母数か必ず明記すること** | 自己検査 |
| `snapshot_osm_age_days` | 地図の `meta.osm_date` からラン日までの日数 | **実測: 2025-04-01 → 2026-08-16 で 502日** | 自己検査 |

**★ この (A) 群は「デジタルツインの忠実度」を最も誠実に語れる。**「我々は建物の55.9%に実高さを持ち、
ダイヤの N% が実ダイヤで、天候は実観測と MAE 0℃」と数字で言える。プレゼン価値も高い。

#### (B) 応答忠実度 — 実測の弾性と符号・オーダーを合わせる

| key(案) | 指標 | 現実側のアンカー(検証済み) |
|---|---|---|
| `heat_daytime_shift` | 最高気温 31℃ 超の日に、日中(9–16時台)の外出率が下がり夕方(18時以降)へシフトするか | **電通×unerry「猛暑下における生活者の外出行動調査」(2026-07-24 発表・2025年6–9月の全国人流ビッグデータ Beacon Bank)**: 変化は35℃を待たず**31℃前後から始まる**。猛暑日の土曜は日中外出率が **14時台で最大 −1.9pt**、**19時台で最大 +1.3pt**。公共交通利用度が高い都市ほど夕方シフトは**起きにくい**(渋谷は該当) |
| `rain_footfall_corr` | 日降水量と在場人数の相関(負) | **技研商事インターナショナル note 記事(2025-06-06)**: KDDI Location Analyzer(2024/4–2025/3・9–22時・滞在180分以下・20歳以上)で武蔵小山パルム **r=0.397(R²=0.158)**、戸越銀座 **r=0.431(R²=0.186)**。**アーケード有無で差は小さい**(=屋根の有無より「出かけるか否か」が支配的) |
| `rain_indoor_share` | 雨天日の屋内 POI 滞在割合の増分 | 【直接統計なし】商用ツールに「天候別来訪者数算出機能」がある(データワイズ Area Marketer)ことから需要は確認できるが、公開された数値が無い。**プロキシ帯として置き、捏造しない** |
| `wx_mood_delta` | 悪天候日の grievance 増分 | 現行 `rain_grievance=0.01`(`conf/daily.yaml:54`)。**設計値であって実測ではない**と明記すべき |

**注意(過剰適合の禁止)**: (B) は「合わせにいく」対象ではなく「**符号とオーダーが合っているか**」の確認に留めるべき。
1kmメッシュ/全国集計の弾性を10分・個体粒度のパラメータ調整に使うと、前回調査 §8.4 が警告した過剰適合になる。
較正するパラメータは事前に列挙して固定する(事前登録の作法= [stationarity-preregistration.md](../plans/stationarity-preregistration.md))。

#### (C) 乖離の追跡

| key(案) | 指標 |
|---|---|
| `presence_curve_rmse_by_day` | jinryu 144step 実測曲線(正規化形状)とシム在場曲線の日別 RMSE の**時系列**。増加傾向=系統的乖離 |
| `snapshot_age_days` | スナップショット取得日からシム日までの経過(=「切り取りの古さ」)。全図表に併記する |
| `forcing_coverage` | その日の環境強制項のうち実データで埋まった割合(欠測日は合成にフォールバック=その旨を記録) |

### 5.3 忠実度を語るときの正直な限界(必ず併記)

1. jinryu は **1kmメッシュ×月次平均・2019–2021**。シム bbox は約 2.9km²=**空間解像度が桁で足りず、年も古い**
   (前回調査 §8.3 の指摘は有効)。144step 曲線は公表形状での**内挿による派生物**であって実測10分値ではない(`data/jinryu/SOURCE.md:38`)。
2. 建物高さの照合率 56% は「PLATEAU に存在する建物のうち OSM と対応が取れた割合」であって
   「渋谷の建物のうち実高さを持つ割合」ではない。母数の定義を明記すること。
3. 天候を実データ化しても、**エージェントの反応係数(暑さ→行動)は依然として設計値**である。
   入力が実になったことと、応答が実になったことは別物 — この区別を潰さない。

---

## §6 前回計画(P0–P7)との統合

### 6.1 P0–P7 は「見せ方」の系列、本ノートは「入れ方」の系列 — 直交する

前回計画の P0–P7 を新定義で分類し直すと、**ほぼ全部が「シム→外」(出力・可視化)であり、
ユーザー定義の中心である「外→シム」(スナップショット取り込み)は P7 の一部にしかない**ことが分かる。

| # | 前回項目 | 向き | スナップショット定義との関係 | 今回の扱い |
|---|---|---|---|---|
| **P0** | 軌跡バイナリ化 | sim→出力 | 無関係(再生の前提工事) | **変更なし**(第76バッチのまま) |
| **P6** | 追いかけ再生 | sim→出力 | 無関係。前回自身が「Digital Shadow ではない・自分の計算を遅延つきで見ているだけ」と正直に注記済み | **変更なし**(第77バッチのまま) |
| **P5** | SUMO 反実仮想 | sim↔物理 | 間接的。信号計画の A/B を `world.mod.edge_speed_scale` へ供給 | **変更なし**(本選後) |
| **P4'** | USD 書き出し | sim→出力 | 無関係 | **変更なし**(本選後) |
| **P1** | Cesium/3D Tiles | sim→出力 | 無関係 | **変更なし**(本選後) |
| **P2** | UE5 リプレイ | sim→出力 | 無関係 | **変更なし**(DT-U2 保留) |
| **②(類型)** | 幾何/環境データ源 | **外→sim** | **これがスナップショットの本体**。既に PLATEAU+OSM attic query で成立(§2.1) | **拡張対象**(下記 S1–S6) |
| **P7** | 人流実データ同化(較正限定) | 外→sim(較正) | **関係する**。ただし「較正に閉じ込める」判断は維持 | **維持+前倒し検討** |
| **④/⑤(類型)** | センサー同化 / リアルタイム連成 | 外→sim(ラン中) | **ここが再検討の核心** | **④の一部が journal 等級で復活**(§1.3 B)。**⑤は不採用のまま** |

**★ 結論: P0–P7 は1つも取り消しにならない。** 新定義が要求するのは**新しい系列の追加**であって、
既存の優先順位の否定ではない。これは重要で、[dt-integration-plan.md](../plans/dt-integration-plan.md) §3 の
順位表と `STATUS.md` §2 の第76-77バッチはそのまま維持できる。

### 6.2 新規に加わる項目(S 系列・「スナップショット忠実度」の系列)

前回の P 系列と区別するため **S(Snapshot)** で番号を振る。工数は Opus 実行役の目安。

| # | 項目 | 内容 | 工数目安 | 等級 | 価値 |
|---|---|---|---:|---|---|
| **S0** | **入力来歴の記録** | `run_manifest.json` に `inputs[]`(path・SHA-256・取得元 URL・ライセンス・取得日時・対象期間)を追加。**現在は入力ファイルのハッシュがどこにも残らない**(§2.7) | 0.5日 | — | **これが無いと「いつの現実を切り取ったか」を後から言えない**。第71バッチの manifest に相乗りすれば実質ゼロ |
| **S1** | **観察ラン profile の忠実度是正** | `conf/observe.yaml` に `world.map`(広域 v7)・`transit.file`(ODPT)を明示。または production 土台運用を正典化 | 0.2日 | strict | §2.8-1。**最も安く忠実度が上がる** |
| **S2** | **バス静的表の生成** | `scripts/build_bus_table.py` を1回走らせ `data/odpt/bus_table_shibuya.json` を作る(読み手は実装済み) | 0.3日 | strict | §2.8-2。ODPT 再配布制限の確認が要る |
| **S3** | **天候の実データ化** | `weather.py` に表引きモード(既定 OFF)。`data/snapshot/weather_<期間>.json` を読み、`cond/temp_hi/temp_lo` に加え **時刻別気温・WBGT・降水量** を提供。`weather_line` を「今日の天気: 猛暑日、最高36℃、暑さ指数 危険」等へ拡張 | **2-3日** | strict(過去)/journal(本選) | **§2.3・§5.1 の最大の空白**。8月中旬の渋谷では支配的要因 |
| **S4** | **スナップショット取得スクリプト** | `scripts/fetch_snapshot.py`(JMA/WBGT/防災XML/OSM opening_hours を1コマンドで凍結+SHA-256+ライセンス文字列を記録) | 1.5日 | — | S3/S5 の供給元。**10月21日で WBGT が止まる**ので期間内取得の運用も含める |
| **S5** | **実イベント表の投入** | 本選期間の渋谷の実イベントを `world.events_file` 形式で用意(既存機構・実装ゼロ) | 0.3日+調査 | strict | §3.2。`annual_events.crowd` との併用で群集も出せる |
| **S6** | **実営業時間** | POI 抽出に `opening_hours` を通す(Overpass 応答には既にある)+`world.mod.open_hours.pois` の消費実装 | 1-1.5日 | strict | §2.8-5。現状 1,975 POI が **3種類の営業時間**しか持たない(food/shop/nightlife。残り 414 POI は常時営業) |
| **S7** | **忠実度レポート** | `calibrate_report.py` に §5.2(A)群を追加し「入力忠実度」の表を出す | 0.5日 | — | **プレゼンで最も効く1枚**。「建物の55.9%に実高さ / ダイヤの N% が実ダイヤ / 天候 MAE 0℃」 |
| **S8** | jinryu 実測曲線の接続(=前回 P7) | `scripts/calibrate_presence.py`(前回 §8.3 の設計そのまま) | 2-3日 | — | **前回どおり本選後**。ただし S7 の枠に「未較正」と明記して穴を可視化しておく。**※ MLIT/Agoop は「2022年以降の公開予定なし」と明文=このデータは 2019–2021 で確定停止**(§3.3)。代替は渋谷区 CC BY 4.0 の通行/滞在人口(構成比のみ) |
| **S9** | **ODD Element 6「Input data」節の作成** | 論文・提出物に、使用した外部入力(何を表すか・単位・出所・前処理・不確かさ・バイアス)を ODD 規格の枠で1節書く。**外部入力が無い場合も「the model does not use input data to represent time-varying processes.」と書くのが規格の要求** | 0.5日 | — | 実装ゼロ。**ODD 2010 の実測では Input 要素を正しく書けている論文は 62% しかない**=ここを丁寧に書くだけで上位に入る。査読対策として費用対効果が最大 |
| **S10** | **お盆モデル**(§3.5-1) | 8/13–16 の個人経営店休業・オフィス空室・来街者比率上昇を `world.mod.open_hours` + presence の条件で表現 | 0.5-1日 | strict | **8月中旬スナップショットは通常週とは別モデルが要る**。ただし**減少率の公開統計が存在しない**ので、設計値であることを明記して帯で置く |

### 6.3 本選日程への当てはめ(提案・**判断はユーザー**)

現行の確定順は 第70→78(8/1–8/14)で計 13.5–15日 vs 暦14日=**既に余裕がない**
([dual-mode-observe-verify-plan.md](../plans/dual-mode-observe-verify-plan.md) §2)。したがって S 系列は
**「ほぼゼロコストのもの」と「天候だけ」に絞る**のが現実的。

| レーン | 提案 | 理由 |
|---|---|---|
| **本選前(〜8/14)に入れる価値が高い** | **S0(0.5日・第71へ相乗り)・S1(0.2日)・S2(0.3日)・S5(0.3日)・S9(0.5日・文書のみ)** = 計 **約1.8日** | いずれも実装がほぼ無く、忠実度と説明可能性が跳ね上がる。S0 は「記録しないと永久に失われる」型なので第71と同時が最適。S9 は実装ゼロ |
| **本選期間中にしか取れないもの(=逃すと永久に失われる)** | **Metro CrowdNavi(直近5日しか保持しない)・モバイル空間統計人口マップ(過去24時間のみ)・JMA 防災情報XML の高頻度フィード(過去電文は数日で流れる)・環境省 WBGT(10月21日でサービス停止)** | §3.3/§3.1。**コード実装が間に合わなくても、データだけは 8/15–8/30 に取っておく価値がある**。取得スクリプトは L1 に触れないのでレーン2 の凍結原則に抵触しない |
| **本選前に入れるか要判断** | **S3+S4(合計 3.5-4.5日)** | **8月中旬の渋谷を名乗るなら天候の実データ化は本丸**。だが 4日は第75(ダンバー)や第78(ablate)と正面から競合する。**ユーザー判断事項(DT-S1 として提起)** |
| 本選中(8/15–8/30) | S4 の**取得運用のみ**(コード凍結下でも `scripts/` の新規追加は L1 に触れないので原則適合)。S3 が入っていれば案B(日次 materialization)で実天候ランを回せる | 前回レーン2 の「main に入れてよいのは L1 を読むだけの観測系のみ」と整合(fetch は sim を読まない・書かない) |
| 本選後(9月〜) | S6(実営業時間)・S7(忠実度レポート)・**S8=旧 P7**・P5・P4'・P1 | 研究価値は高いが 10日ランの成立には不要 |

### 6.4 前回の結論のうち**訂正が必要**なもの

| 前回の記述 | 訂正 |
|---|---|
| [dt-integration-plan.md](../plans/dt-integration-plan.md) §2 表「④センサー実データ同化 = **較正フェーズ限定のみ**。ラン中同化は不採用」 | **「ラン中の *状態同化* は不採用」に限定して書き直す**。「ラン中の *一方向強制*(天候等・シム状態を書き換えない)」は journal 等級で採用しうる(§1.3 B / §4.2) |
| 同 §4 DT-U3「『Digital Model(一方向・事後)』の用語を採用するか」 | **廃止**(`STATUS.md` で既に「再提案タスクへ置換」と決定済み)。代わりに **frequency(=on-demand スナップショット)/ fidelity(=§5 の KPI)の2軸で自己記述する**(§1.2) |
| [dt-integration-deep.md](dt-integration-deep.md) §7.1「本線の10日ランは Digital Model(較正で一度取り込むだけ)」 | 案Bを採るなら **Digital Shadow(物理→デジタルの一方向自動)** に上がる。ただし「自動」の頻度は日次で、人手トリガを含む。**曖昧に言わず「日次・一方向・状態非書き換え」と書く** |
| 同 §8.1「jinryu 144step 曲線は接続されていない(将来拡張点)」 | **2026-07-31 時点でも未接続**(再実査で確認)。訂正不要=**事実として据え置き** |

---

## §7 出典 URL 一覧

> 原則: 本ノートの主張には出典を付け、**確認できなかったものは「未確認」と書いた**(§3.6 に一覧)。
> 実在しない出典は記載していない。以下は分野別の一覧。DOI があるものは DOI を併記した。

### 7.1 気象・環境

- 気象庁 過去の気象データ・ダウンロード: <https://www.data.jma.go.jp/risk/obsdl/>
- 気象庁 過去の気象データ検索(etrn): <https://www.data.jma.go.jp/stats/etrn/>
- 気象庁 平年値(東京・block_no 47662・統計期間 1991–2020): <https://www.data.jma.go.jp/stats/etrn/view/nml_sfc_ym.php?prec_no=44&block_no=47662>
- 気象庁 bosai アメダス(準公式 JSON): <https://www.jma.go.jp/bosai/amedas/const/amedastable.json> / <https://www.jma.go.jp/bosai/amedas/data/latest_time.txt>
- 気象庁「東京」の北の丸公園への移転(2014-12-02): <https://www.jma.go.jp/jma/kishou/know/kansoku/info/20141202_tokyo_rojo.html>
- 気象庁 2025年の猛暑日・真夏日などの日数: <https://www.data.jma.go.jp/stats/stat/202515/tem_ctg_days_202515.html>
- 気象庁防災情報XML(取得方法): <https://xml.kishou.go.jp/xmlpull.html>
- 公共データ利用規約(第1.0版)(=CC BY 4.0 互換・商用可): <https://www.digital.go.jp/resources/open_data/public_data_license_v1.0>
- 環境省 熱中症予防情報サイト: <https://www.wbgt.env.go.jp/> / 利用規約 <https://www.wbgt.env.go.jp/tos.php> / データDL <https://www.wbgt.env.go.jp/wbgt_data_download.php> / 電子情報提供サービス <https://www.wbgt.env.go.jp/data_service.php> / WebAPI 仕様 PDF <https://www.wbgt.env.go.jp/man15NH/wbgt_data_api_service_manual.pdf> / 熱中症警戒アラートとは <https://www.wbgt.env.go.jp/about_alert.php>
- Open-Meteo: <https://open-meteo.com/en/docs/historical-weather-api> / <https://open-meteo.com/en/docs/jma-api> / <https://open-meteo.com/en/docs/historical-forecast-api> / 規約 <https://open-meteo.com/en/terms> / 料金 <https://open-meteo.com/en/pricing>
- 気象業務支援センター オンライン提供: <https://www.jmbsc.or.jp/jp/online/c-onlineF.html>
- OpenWeatherMap 料金: <https://openweathermap.org/price> / WeatherAPI.com 料金: <https://www.weatherapi.com/pricing.aspx> / Visual Crossing: <https://www.visualcrossing.com/weather-data-editions/>
- 東京都 大気汚染常時監視(解説): <https://www.taiki.kankyo.metro.tokyo.lg.jp/taikikankyo/guid/index.html> / 月報CSV: <https://www.kankyo.metro.tokyo.lg.jp/air/air_pollution/torikumi/result_measurement/>
- 東京都 ヒートアイランド対策(METROS): <https://www.kankyo.metro.tokyo.lg.jp/climate/heat_island/>
- tenki.jp 2025-08-23(東京都心 8月の猛暑日日数が統計開始以来最多): <https://tenki.jp/forecaster/deskpart/2025/08/23/35353.html>
- tenki.jp 2025-08-26(猛暑日9日連続・年間22日目): <https://tenki.jp/forecaster/deskpart/2025/08/26/35397.html>

### 7.2 イベント・暦・条例

- 渋谷区 イベントカレンダー: <https://www.city.shibuya.tokyo.jp/contents/event/calendar/>
- 渋谷駅周辺地域の安全で安心な環境の確保に関する条例(路上飲酒): <https://www.city.shibuya.tokyo.jp/kusei/shisaku/jorei-toshin/sbykankyo.html>
- 東京都オープンデータカタログ CKAN API: <https://catalog.data.metro.tokyo.lg.jp/api/3/action/package_search?fq=organization:t131130>
- 内閣府 国民の祝日 CSV: <https://www.cao.go.jp/syukujitsu.csv>
- 渋谷スクランブルスクエア 公開 JSON: `https://tacsis-cdn-endpoint.azureedge.net/cms-web/scsq_news_event_web.json` / `shop.json` / `open_hours.json`
- X API 料金: <https://docs.x.com/x-api/getting-started/pricing>

### 7.3 人流・歩行者・鉄道

- 渋谷区オープンデータ DCAT フィード(122データセット・120件が CC BY 4.0): <https://city-shibuya-data.opendata.arcgis.com/api/feed/dcat-us/1.1.json>
- 渋谷区 SHIBUYA CITY DASHBOARD(人流): <https://www.city.shibuya.tokyo.jp/kusei/tokei_shibuya/shibuya-data/shibuya_city_dashboard_peopleflow_KDDI.html>
- 東京メトロ Metro CrowdNavi: <https://tmcawebapp1.tokyometro.jp/> / リリース <https://www.tokyometro.jp/news/2026/224561.html>
- モバイル空間統計 人口マップ: <https://mobakumap.jp/> / 学術利用: <https://mobaku.jp/academic/>
- MLIT/Agoop 全国の人流オープンデータ(**2022年以降の公開予定なし**): <https://www.geospatial.jp/ckan/dataset/mlit-1km-fromto>
- 東京都における繁華街利用実態調査(平成13年3月・センター街入口 平日113,568人/12h): <https://www.sangyo-rodo.metro.tokyo.lg.jp/toukei/pdf/monthly/chusho/hankagai.pdf>
- 東急電鉄 駅別乗降人員(FY2025): <https://www.tokyu.co.jp/railway/company/business/passengers/2025/>
- 国交省 都市鉄道の混雑率調査 令和7年度実績(2026-07-28 公表): <https://www.mlit.go.jp/report/press/tetsudo04_hh_000139.html>
- KDDI×三井物産 GEOTRA 設立リリース(**ソフトバンク系ではない**): <https://news.kddi.com/kddi/corporate/newsrelease/2022/06/09/6106.html>
- BestTime.app 料金(現在ベータで全プラン無料): <https://besttime.app/subscription/pricing>
- 技研商事インターナショナル「雨が降れば屋根屋は儲かる?」(2025-06-06・KDDI Location Analyzer・r=0.397/0.431): <https://note.com/gsi_note/n/nb8ce357d5080>
- unerry「電通とunerry、『猛暑下における生活者の外出行動調査』を実施」(2026-07-24・31℃で変化・14時台 −1.9pt/19時台 +1.3pt): <https://prtimes.jp/main/html/rd/p/000000147.000016301.html>

### 7.4 店舗・地図・土地利用

- PLATEAU Site Policy(政府標準利用規約2.0 / CC BY 4.0 / ODC BY / ODbL から選択・商用含め無償): <https://www.mlit.go.jp/plateau/site-policy/>
- e-Stat 経済センサス 町丁・大字別 産業中分類別事業所数(東京都): <https://www.e-stat.go.jp/stat-search/files?page=1&layout=dataset&stat_infid=000040068156>
- 東京都 土地利用現況調査 GIS(令和3年・区部): <https://data.storage.data.metro.tokyo.lg.jp/toshiseibi/R03.zip>
- ODPT: <https://www.odpt.org/>(**利用規約全文は本調査で再取得できず=未確認**)

### 7.5 デジタルツイン分類・スナップショット初期化

- Kritzinger, W., Karner, M., Traar, G., Henjes, J., Sihn, W. (2018) "Digital Twin in manufacturing: A categorical literature review and classification." *IFAC-PapersOnLine* 51(11):1016–1022. DOI `10.1016/j.ifacol.2018.08.474`(**原文 PDF は Elsevier 403 で一次照合未達**。定義はオープンアクセス二次文献で逐語一致を確認)
- Digital Twin Consortium 定義(2020): <https://www.digitaltwinconsortium.org/2020/12/digital-twin-consortium-defines-digital-twin/>(**本調査では HTTP 403・検索結果由来の引用**)
- ISO/IEC 30173:2023 Digital twin — Concepts and terminology: <https://www.iso.org/standard/81442.html>(**有償・未確認**)
- ECMWF Destination Earth: <https://www.ecmwf.int/en/about/what-we-do/environmental-services-and-future-vision/destination-earth> / <https://destine.ecmwf.int/digital-twins/>
- Augusto, V. et al. (2023) "An Agent-Based Architecture of the Digital Twin for an Emergency Department." *Sustainability* 15(4):3412(Digital Shadow / Synchronised DT / **Exploratory DT** の三分。**逐語一次確認は未達**): <https://www.mdpi.com/2071-1050/15/4/3412>
- Cau, E., Failla, A., Pansanella, V., Rossetti, G. (2026) "Social Simulations: from Agent-Based Modeling to Digital Twins." arXiv **2607.13693**: <https://arxiv.org/abs/2607.13693>
- Malleson, N. et al. (2022) "Agent-Based Modelling for Urban Analytics: State of the Art and Challenges." *AI Communications* 35:393–406. arXiv 2210.06955
- Virtual Singapore の連続同期の有無: **引用に耐える一次ソースなし=未確認**(NRF 公式ページ 404)

### 7.6 決定性・record&replay・イベントソーシング

- Fowler, M. (2005) "Event Sourcing"(**External Queries / Logging Gateway** 節): <https://martinfowler.com/eaaDev/EventSourcing.html>
- Temporal: <https://docs.temporal.io/workflow-definition> / <https://docs.temporal.io/develop/go/side-effects> / <https://pkg.go.dev/go.temporal.io/sdk/workflow>
- Carmack, J. (1998-10-14) .plan(イベントジャーナリング): <https://github.com/ESWAT/john-carmack-plan-archive/blob/master/by_day/johnc_plan_19981014.txt> / 解説 <https://fabiensanglard.net/quake3/>
- O'Callahan, R. et al. (2017) "Engineering Record And Replay For Deployability." *USENIX ATC 2017*. arXiv 1705.05937: <https://www.usenix.org/conference/atc17/technical-sessions/presentation/ocallahan>
- Chen, Y. et al. (2015) "Deterministic Replay: A Survey." *ACM Computing Surveys* 48(2):1–47. DOI `10.1145/2790077`
- Alvaro, P. & Quinn, A. (2024) "Deterministic Record-and-Replay." *ACM Queue* 22(4):120–129. DOI `10.1145/3688088`
- Bettner, P. & Terrano, M. (2001) "1500 Archers on a 28.8." *Game Developer*: <https://www.gamedeveloper.com/programming/1500-archers-on-a-28-8-network-programming-in-age-of-empires-and-beyond>
- DOOM/Quake DEM の入力再生 vs 状態記録: <https://www.gamers.org/dEngine/quake/Qdem/dem-1.0.2-3.html>
- Unreal Engine Replay System: <https://dev.epicgames.com/documentation/en-us/unreal-engine/using-the-replay-system-in-unreal-engine>
- CARLA 同期モードと決定性: <https://carla.readthedocs.io/en/latest/adv_synchrony_timestep/> / recorder <https://carla.readthedocs.io/en/latest/adv_recorder/>
- SUMO Randomness(既定シード 23423): <https://sumo.dlr.de/docs/Simulation/Randomness.html> / Calibrator <https://sumo.dlr.de/docs/Simulation/Calibrator.html> / TraCI <https://sumo.dlr.de/docs/TraCI/index.html> / routeSampler <https://sumo.dlr.de/docs/Demand/Routes_from_Observation_Points.html>
- Mesa best practices(same seed = same results): <https://mesa.readthedocs.io/stable/best-practices.html>
- MASON: Luke, S. et al. (2005) *SIMULATION* 81(7):517–527. DOI `10.1177/0037549705058073`
- ※ **Mesa/Repast/MASON いずれも「same seed + same *version* = same results」というバージョン限定形は公式に述べていない(未確認)**

### 7.7 天候ファイル駆動・ライブ天候

- Singh, D.E. et al. (2020) "Evaluating the impact of the weather conditions on the influenza propagation." *BMC Infectious Diseases* 20:265. DOI `10.1186/s12879-020-04977-w`
- Pascoe, L. et al. (2022) *IJERPH* 19(23):15578. DOI `10.3390/ijerph192315578`
- Kušić, K., Schumann, R., Ivanjko, E. (2022) "Building a Motorway Digital Twin in SUMO." *ELMAR 2022*:71–76. DOI `10.1109/ELMAR55880.2022.9899796` / (2023) *Advanced Engineering Informatics* 55:101858. DOI `10.1016/j.aei.2022.101858` / コード <https://github.com/SiLab-group/DigitalTwin_GenevaMotorway>
- DSSAT Weather Module: <https://dssat.net/weather-module/>
- APSIM Met module: <https://www.apsim.info/documentation/model-documentation/infrastructure-and-management-documentation/met/>
- EMOD climate(`Enable_Rainfall_Stochasticity`=天候ファイルだけでは軌道が決まらない): <https://emod.idmod.org/emodpy-malaria/emod/software-climate/>
- EnergyPlus EPW 形式(TMY / **AMY**): <https://designbuilder.co.uk/cahelp/Content/EnergyPlusWeatherFileFormat.htm>
- MSFS: Flight Definitions(`UseLiveWeather` 等) <https://docs.flightsimulator.com/html/Content_Configuration/Flights_And_Missions/Flight_Definitions.htm> / Weather XML(`.WPR`) <https://docs.flightsimulator.com/msfs2024/html/5_Content_Configuration/Mission_XML_Files/Weather_XML_Properties.htm> / meteoblue 提携 <https://www.meteoblue.com/en/blog/article/show/40088_meteoblue+live+weather+data+in+Microsoft+Flight+Simulator>
- X-Plane: "A METAR does not tell you the sim's weather"(非決定性の明言+weather dump) <https://developer.x-plane.com/article/a-metar-does-not-tell-you-the-sims-weather/> / 12.3.0 リリースノート(**Historic Weather**) <https://www.x-plane.com/kb/x-plane-12-3-0-release-notes/>
- Cities: Skylines II の気候(**実天候を取り込まない**): <https://www.paradoxinteractive.com/games/cities-skylines-ii/features/climate-seasons>

### 7.8 sim2real・ログ再生・乖離

- Montali, N. et al. (2023) "The Waymo Open Sim Agents Challenge."(**pose divergence / simulation drift**) arXiv **2305.12032**
- Caesar, H. et al. (2021) "nuPlan." arXiv **2106.11810** / devkit(open-loop / closed-loop non-reactive / reactive の定義) <https://nuplan-devkit.readthedocs.io/en/latest/competition.html>
- Gulino, C. et al. (2023) "Waymax." arXiv **2310.08710**
- Yang, Z. et al. (2023) "UniSim: A Neural Closed-Loop Sensor Simulator." arXiv **2308.01898**(CVPR 2023 Highlight) / <https://waabi.ai/research/unisim>
- NVIDIA 自動運転シミュレーション(Behavior / Content / **Style** permutation): <https://www.nvidia.com/en-us/use-cases/autonomous-vehicle-simulation/>
- NVIDIA OmniDreams (2026) arXiv **2606.03159**

### 7.9 データ同化(**我々が採らない側**・混同禁止)

- Ward, J.A., Evans, A.J., Malleson, N.S. (2016) *Royal Society Open Science* 3(4):150703. DOI `10.1098/rsos.150703`
- Malleson, N. et al. (2020) *JASSS* 23(3):3. DOI `10.18564/jasss.4266`
- Clay, R. et al. (2021) *Simulation Modelling Practice and Theory* 113:102386. DOI `10.1016/j.simpat.2021.102386`
- Suchak, K. et al. (2024) *Royal Society Open Science* 11(4):231553. DOI `10.1098/rsos.231553`
- Ghorbani, A. et al. (2023) *Mathematics* 11(20):4296. DOI `10.3390/math11204296`

### 7.10 モデル記述・再現性・プロヴェナンス標準

- Grimm, V. et al. (2005) "Pattern-Oriented Modeling of Agent-Based Complex Systems." *Science* 310(5750):987–991. DOI `10.1126/science.1116681`
- Grimm, V. et al. (2006) *Ecological Modelling* 198(1–2):115–126. DOI `10.1016/j.ecolmodel.2006.04.023`
- Grimm, V. et al. (2010) "The ODD protocol: A review and first update."(**Element 6 Input data**) *Ecological Modelling* 221(23):2760–2768. DOI `10.1016/j.ecolmodel.2010.08.019`
- Grimm, V. et al. (2020) "The ODD Protocol … A Second Update." *JASSS* 23(2):7. DOI `10.18564/jasss.4259` / Supplement S1 <https://www.jasss.org/23/2/7/S1-ODD.pdf>
- **★ 訂正**: 「TRACE: TRAnsparent and Comprehensive model Evaludation」(TiEE 2010)という論文は**存在しない**。実物は Schmolke, A., Thorbek, P., DeAngelis, D.L., Grimm, V. (2010) "**Ecological models supporting environmental decision making: a strategy for the future**." *Trends in Ecology & Evolution* 25(8):479–486. DOI `10.1016/j.tree.2010.05.001`。"evaludation" は別論文の造語=Augusiak, J., Van den Brink, P.J., Grimm, V. (2014) *Ecological Modelling* 280:117–128. DOI `10.1016/j.ecolmodel.2013.11.009`
- Grimm, V. et al. (2014) "Towards better modelling and decision support: … TRACE." *Ecological Modelling* 280:129–139. DOI `10.1016/j.ecolmodel.2014.01.018`
- Axtell, R., Axelrod, R., Epstein, J.M., Cohen, M.D. (1996) "Aligning simulation models." *CMOT* 1(2):123–141. DOI `10.1007/BF01299065`
- Edmonds, B. & Hales, D. (2003) "Replication, Replication and Replication." *JASSS* 6(4):11: <https://www.jasss.org/6/4/11.html>(**DOI なし=JASSS の DOI 以前の時代**)
- Janssen, M.A., Pritchard, C., Lee, A. (2020) *Environmental Modelling & Software* 134:104873. DOI `10.1016/j.envsoft.2020.104873`
- Janssen, M.A. (2017) *JASSS* 20(1):2. DOI `10.18564/jasss.3317`
- **W3C PROV-O**(Recommendation 2013-04-30): <https://www.w3.org/TR/prov-o/> / **PROV-DM**: <https://www.w3.org/TR/prov-dm/>
- **RO-Crate**: Soiland-Reyes, S. et al. (2022) "Packaging research artefacts with RO-Crate." *Data Science* 5(2):97–138. DOI `10.3233/DS-210053` / <https://www.researchobject.org/ro-crate/>
- **★ ODD+P**(ABM 特化の直接の先行研究): Reinhardt, O., Ruscheinski, A., Uhrmacher, A.M. (2018) *WSC 2018*:727–738. DOI `10.1109/WSC.2018.8632481` / PDF <https://www.informs-sim.org/wsc18papers/includes/files/060.pdf>(※ Crossref メタデータが "Rucheinski" と誤植)
- SED-ML(再現可能なシミュレーション実験記述の成熟標準): <https://sed-ml.org/> / Waltemath, D. et al. (2011) *BMC Systems Biology* 5:198. DOI `10.1186/1752-0509-5-198`。**ABM に SED-ML 相当の機械可読標準は存在しない(発見できず=未確認)**
- ABM 可視化の警告(前回調査から継承): JASSS 12(2)1 <https://www.jasss.org/12/2/1.html> / JASSS 27(1)11 <https://www.jasss.org/27/1/11.html>

### 7.11 リポジトリ内の関連文書

- [dt-integration-plan.md](../plans/dt-integration-plan.md) / [dt-landscape.md](dt-landscape.md) / [dt-integration-deep.md](dt-integration-deep.md)(前回の DT 調査3本)
- [dual-mode-observe-verify-plan.md](../plans/dual-mode-observe-verify-plan.md)+[source/dual-mode-requirements.md](../plans/source/dual-mode-requirements.md)(repro_tier / ランモードの正典)
- [plateau-2025-update-notes.md](plateau-2025-update-notes.md)(PLATEAU 2025年度版とライセンス)
- `data/jinryu/SOURCE.md`(人流一次データの出所・ライセンス・定義)
- [shibuya-inflow.md](shibuya-inflow.md)(昼間流入の一次統計・検証済み URL 集)
- [shibuya-concurrent-population.md](shibuya-concurrent-population.md)(同時滞在人口の分析本体)
- [stationarity-preregistration.md](../plans/stationarity-preregistration.md)(事前登録の作法)
- [STATUS.md](../../STATUS.md)(現況台帳・PUB-U1 ほか)

---

## §8 本ノートの調査上の限界(正直な記載)

1. **WebSearch のセッション予算(200件)を使い切った**ため、調査の後半は WebFetch(直接取得)のみで進めた。
   追加で潰したい未確認項目(§3.6)が残っている。
2. **2026年8月のデータはまだ存在しない**(調査日 2026-07-31)。§5.1 の乖離は 2025年の実績と平年値に基づく
   **推定**であり、本選期間の実際の天候で再計算する必要がある。
3. **ODPT・Digital Twin Consortium・ISO/IEC 30173・JR東日本**の一次規約/原文を取得できなかった(403 / 有償 / SPA)。
   これらに依拠した記述には「未確認」を付した。
4. **§6.3 の工数見積りは Opus 実行役の目安**であり、実測ではない。
5. 本ノートは**調査であって計画ではない**。S 系列の実装着手は、standing rule どおり
   **ユーザーの承認を得てから**(計画書化 → 承認 → 着手)。
