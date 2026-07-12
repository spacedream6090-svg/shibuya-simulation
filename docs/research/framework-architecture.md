# 基盤モデル/環境モジュール分離アーキテクチャ調査

作成: 2026-07-10 / リサーチ担当(コード変更なし・読み取りのみ)

本書のねらいは、ユーザー構想「渋谷など具体的な場所と切り離した『LLM社会シミュレーションの
基盤モデル』を作る」を実装計画に落とすための土台をつくることである。すなわち:

- **(a) 基盤モデルの抽出** — 場所非依存の認知・社会・観測モジュール群を1つのコアにまとめる。
- **(b) 環境モジュール** — 渋谷を含むあらゆる環境を差し替え可能にする「環境パック」化。
- **(c) 環境要素の分解と自動生成** — 環境を階層分解し、各要素の自動生成経路を定める。

結論を先に言うと、**本コードベースは既に「場所固有性の大半を `data/` と `conf/` に外出しして
config パス束縛で読む」という良い切断面を持っている**。残る課題は、少数のモジュールにハード
コードされた「渋谷」文字列・日本制度デフォルト・スクランブル前提を**環境パック側へ移す**こと。
(b) は config 束縛の延長で 8 割方到達可能、真の作業は (c) の環境自動生成にある。

---

## 1. 先行アーキテクチャ比較表

### 1-A. 「認知・社会の基盤」と「環境・場所」の分離方式(一次ソース優先)

| 事例 | 基盤(認知/社会)の分離方式 | 環境・場所の記述形式 | 再利用性/切断面 | 本プロジェクトへの示唆 |
|---|---|---|---|---|
| **DeepMind Concordia** (v2.0) | **Entity-Component + Game Master(GM)**。Entity は識別子だけの器、Component が記憶・物理状態・目標などの「1側面」を担う再利用モジュール。行動生成は「LLM呼び出し × 連想記憶検索」を Component 系が仲介 | GM という特別な Entity が**環境そのものを演じる**。プレイヤは自然言語で意図を宣言し、GM が物理的妥当性を判定して結果に翻訳 | 環境が「GM+その Component 群」として**エージェントと完全に同型**に表現される=環境も部品の組換えで作れる。最も参考になる抽象 | 我々の `world/` を「環境 GM」に、`cognition/`+`factors/` を「Actor Component」に再編する設計の直接の下敷き |
| **AgentSociety** (Tsinghua) | **4層(Model / Environment / LLM / Tool)**に明示分離。Agent は心理・記憶・感情・意思決定を持つ | **Environment 層**が都市・社会・経済の多層空間を保持。都市空間は道路網 + **AOI(Area of Interest)/POI**。環境センシング/相互作用/メッセージを Environment 層が仲介 | Ray 分散で数千体スケール。環境を「読む/書く/メッセージ」の3インタフェースに閉じている | 我々の `observer/`(読む)・engine の phase(書く)・`net/`(メッセージ)にほぼ対応。層の名付けを借りると疎結合の議論がしやすい |
| **Generative Agents** (Stanford, Park 2023) | **Memory Stream / Reflection / Planning** の3部品。観測→反省→計画の層が人格を創発 | **環境ツリー**(root=世界 → area=家/カフェ/店 → leaf=机/本棚)。各エージェントは見た部分木だけを記憶。サーバは全体を JSON で保持し差分更新 | 環境が**木構造の状態**として言語化され、LLM が読み書きできる。Phaser の sprite/collision map は描画専用で本体と分離 | 我々の `map.py` はグラフ(木ではない)だが、「見た範囲だけを記憶」は `agents/memory.py`+知覚半径と同思想。環境の**言語化された木**は自動生成の出力形式候補 |
| **Mesa / Mesa-Geo** | Mesa の `Agent`/`Model`。Mesa-Geo は `GeoAgent`(= Agent + geometry + CRS) | **GeoSpace** が GIS ベクタ(shapefile/GeoJSON/GeoDataFrame)をホスト。任意のベクタデータから GeoAgent を生成 | 「空間(GeoSpace)」と「主体(GeoAgent)」が別クラス=**地理データを丸ごと差し替え可能**な最も明快な分離 | 我々の `world/`(空間)/ `agents/`(主体)分離はこの系譜。GeoJSON 入力互換にすれば任意都市が載る |
| **AgentTorch** | ABM 全体を**テンソル化・微分可能**に。DNN と勾配統合、国規模を数秒 | 環境も状態テンソル。物理/生物/デジタル領域横断 | 微分可能=キャリブレーション自動化。ただし LLM 認知の豊かさは持たない | 我々の k* 掃引の**較正自動化**の参考(規模側)。認知の質は別路線 |
| **Project Sid / PIANO** (Altera) | **PIANO(並列情報集約)**= 記憶処理・行動認識・高速行動・目標設定・社会認識を**並列ストリーム**で走らせ中央意思決定が統合 | Minecraft を環境に使用(空間推論は弱点と自認) | 認知の**並列モジュール化**が最大の学び。環境は既製ゲームに委譲 | 我々の `cognition/`(drive/reflection/planning/deliberate)を**並列ストリーム**として整理する指針。基盤=認知ストリーム束、という括りが取れる |
| **VirtualHome / ALFWorld** | タスク実行エージェント(埋込 or テキスト) | **プログラム/シーングラフ**で家庭環境を記述。ALFWorld はテキスト記述と埋込環境を整合 | 環境が**宣言的記述(シーングラフ/テキスト)**=生成・編集しやすい | 環境の**テキスト/グラフ記述**は (c) 自動生成の出力スキーマの候補。屋内(フロア)記述に近い |

**共通パターン**: 優れた事例は例外なく「主体(認知・社会)」と「環境(空間・制度)」を**別の型・別の層**に置き、
環境を**宣言的データ(グラフ/ツリー/GISベクタ/シーングラフ)**として差し替え可能にしている。
Concordia の「環境も Entity-Component で作る」対称性が、我々の目標に最も近い。

### 1-B. 環境の自動生成の先行事例

| 事例 | 生成対象 | 入力 | 自動化度 | 本プロジェクトでの位置 |
|---|---|---|---|---|
| **OSMnx** | 街路網(歩行/自動車/自転車)+ 建物 + POI + 標高 + 交通停留所 | OpenStreetMap(Overpass) | **高**(市名/境界/bbox から1コマンドで位相簡約済み有向マルチグラフ) | 我々の `scripts/build_map.py` は既に Overpass を直叩き。OSMnx 化で任意都市に一般化可 |
| **PLATEAU** (国交省) | **3D都市モデル**(建物/道路を意味情報付きで構造化。用途・築年・都市計画) | CityGML 2.0。250都市超を G空間情報センターでオープンデータ公開 | **高**(日本の都市に限れば)。建物の**用途・高さ・フロア**が semantic で入る | 建物・フロア・用途の自動供給源。屋内(フロア)以外はほぼ自動化。**日本限定**が制約 |
| **GTFS 取込** | 公共交通ダイヤ(stops/trips/routes/stop_times) | 交通事業者の GTFS フィード | **中〜高**(標準フォーマットのグラフ化は確立。TransitGPT 等 LLM 解析も登場) | 我々の `scripts/fetch_odpt.py`+`build_transit_odpt.py` は ODPT(GTFS/API)→静的キャッシュ→実ダイヤ化を既に実装 |
| **LLM text-to-environment** | シーンレイアウト/シーングラフ/2Dゲーム環境/交通シーン | 自然言語記述 | **中**(研究段階。SimWorld はシーングラフを RAG で参照し編集、TSG-Bench で評価) | (c) の「長い裾」= OSM/統計で埋まらない要素(架空店の内装・組織の物語)を LLM で補完する経路 |
| **e-Stat / IPF** | 人口・世帯・産業の周辺分布に整合したペルソナ | 国勢調査等の周辺統計 | **中〜高**(IPF で周辺整合、文章化は LLM) | 我々の `persona.py` 冒頭が「IPF×e-Stat 渋谷 + Verbalized Sampling」を seam として明記。`docs/research/lexicon-ipf-shibuya.md` |

---

## 2. 自コードベースの3分類表

分類基準:
- **(A) 基盤** = 場所非依存。人格・記憶・内省・drive/LOD・関係・情報環境・経済/制度の**機構**・観測系。
- **(B) 場所固有** = 渋谷依存。地図・POI・ダイヤ・組織台帳・ペルソナ名簿・制度の**渋谷具体値**。
- **(C) 混在** = 基盤ロジックに渋谷固有の語・値・仮定が埋まっている(§2-C で行番号つき列挙)。

**重要な観察**: **場所固有性(B)の実体はほぼ全て `data/` と `conf/production.yaml` に外出し済み**で、
`src/` の大半は (A) 基盤である。ソースコードに残る場所依存は (C) の少数モジュールに限られる。
これは「基盤/環境の分離」がかなり進んだ状態を意味する(あとひと押しで (a)(b) に届く)。

### 2-A. 基盤(場所非依存)= コアに抽出すべき src/ モジュール

| モジュール | 役割 | 備考 |
|---|---|---|
| `src/society/rng.py` | 決定論 RNG(RngHub/stream) | 完全に基盤 |
| `src/society/config.py` | config ローダ・REPO_ROOT・save_config | 基盤 |
| `src/society/cognition/drive.py` | 欲求ゲージ発火(閾値+個人重み) | 基盤(発火機構) |
| `src/society/cognition/reflection.py` | 内省・自己モデル・出来事誘発の深い内省 | 基盤 |
| `src/society/cognition/planning.py` | 朝の一日計画 | 基盤 |
| `src/society/cognition/lod.py` | LLM 発火の LOD 予算 | 基盤 |
| `src/society/factors/*` (mood/psych/affect/registry/update) | state 更新則・traits・SDT/集団効力感/Lynch/Searle・arousal/salience | 基盤(no-fingerprint 契約の中核) |
| `src/society/agents/memory.py` | 記憶(push/agentic pull) | 基盤 |
| `src/society/agents/validate.py` | エージェント検証 | 基盤 |
| `src/society/llm/*` (base/ollama/vllm/mock/cache/fleet) | LLM バックエンド・キャッシュ・艦隊 | 基盤(モデル非依存の seam) |
| `src/society/net/internet.py` `net/infoenv.py` | SNS/ニュース/DM・情報環境の非対称(推薦/バイラル/炎上) | 基盤 |
| `src/society/observer/*` (logger/provenance/measure/aggregate/schema) | L1-L3 観測・出所・集計・イベントスキーマ | 基盤(観測系) |
| `src/society/labeling/labels.py` | 造語の複雑接触・採用閾値 | 基盤 |
| `src/society/actions/registry.py` | 行動レジストリ | 基盤 |
| `src/society/relations.py` | 関係の質(親密度/tier/評判/派閥) | 基盤 |
| `src/society/opinion.py` | 意見力学(Friedkin-Johnsen) | 基盤 |
| `src/society/status.py` | 社会的地位・累積優位・優先的選択 | 基盤 |
| `src/society/tools.py` | 「世界を変える」affordance(出店/提案/イベント/ビラ) | 基盤 |
| `src/society/recursion.py` | 規範監視→知覚→フィードバック→改変(repeal) | 基盤 |
| `src/society/needs.py` | 欲求プロファイルの個人差 | 基盤 |
| `src/society/health.py` | 疲労・病気・メンタル | 基盤 |
| `src/society/household.py` | 世帯・家族・恋愛 | 基盤 |
| `src/society/commerce.py` | 営業時間・動的価格・在庫(hours 既定は汎用) | 基盤 |
| `src/society/inner_life.py` | 離散感情ラベル・長期目標・趣味 | 基盤 |
| `src/society/lodging.py` | ホテル泊(hotel POI があれば作用) | 基盤 |
| `src/society/weather.py` | 決定論天気(季節バイアスは汎用) | 基盤 |
| `src/society/world/clock.py` `world/calendar.py` `world/geom.py` | 時計・暦・幾何 | 基盤 |
| `src/society/world/routing.py` | グラフ最短路(Dijkstra) | 基盤(任意グラフに作用) |
| `src/society/world/traffic.py` | 背景交通(ambient/od) | 基盤(グラフに作用。※コメントに渋谷) |
| `src/society/world/vision.py` `world/perception.py` | 擬似視覚(LOS)・知覚 | 基盤 |
| `src/society/world/scenario.py` | 摂動カタログ(baseline/shock_closure/shock_event) | **基盤**(座標は地図ローカル m・宣言的・場所非依存に設計されている。良いお手本) |
| `src/society/engine/checkpoint.py` | チェックポイント/resume | 基盤 |
| `src/society/engine/simulation.py` `engine/scheduler.py` | 構築・実行ループ・phase 群 | 基盤(オーケストレータ。※一部コメント/前提に渋谷=§2-C) |

### 2-B. 場所固有(渋谷依存)= 環境パックへ束ねるべき資産

**ソースコードにはほぼ存在せず、`data/` と `conf/production.yaml` に集中している。** これが環境モジュール
(b) の実体。以下を1つの「Shibuya 環境パック」として括り出せる。

| カテゴリ | 具体ファイル/値 | 供給元 |
|---|---|---|
| 地図(道路網/建物/POI/フロア) | `data/shibuya_osm*.json`(v3/wide/v6/v7)、`data/floorguide_shibuya.json`、`data/poi_patch_shibuya.json`、`data/traffic_features_shibuya.json` | OSM/Overpass(`build_map.py`)+ 手作業パッチ |
| 鉄道ダイヤ/路線/駅 | `data/transit_shibuya.json`、`data/transit_odpt.json`、`data/odpt/*`・`data/odpt_challenge/*`(山手/埼京/湘南新宿/東横/田園都市/井の頭/銀座/半蔵門/副都心) | ODPT API・GTFS(`fetch_odpt.py`/`build_transit_odpt.py`) |
| 組織台帳・配属 | `data/organizations_shibuya*.json`、`data/org_assignments_*` | e-Stat 産業構成→架空台帳(`build_orgs.py`, R17 で実名禁止) |
| ペルソナ名簿 | `data/personas_40/60/80/100_*.json`、`data/personas_300_civic.json`、`data/personas_gen_100.json`、`data/persona_pool.json`、`data/icebreak_80.json` | IPF×e-Stat 渋谷 + 語彙テンプレ(`gen_personas.py`/`build_personas.py`) |
| 人口・流入 | `data/shibuya_population.json`(出入口配分・到着二峰・沿線タグ) | 統計 + 手作業 |
| 感情辞書 | `data/sentiment_lexicon.json` | 日本語辞書(言語固有) |
| イベント暦 | `data/events_demo.json` | 手作業 |
| 制度・経済の**渋谷具体値**(config) | `conf/production.yaml`: 地図 v7 束縛、`transit.file`、名簿、組織台帳、供託金 30000、議会 size 9(渋谷区議会34→圧縮)、最低賃金 1226、犯罪率較正 等 | 東京労働局/区財政/公選法 等の一次値 |

### 2-C. 混在(基盤ロジックに渋谷固有の語・値・仮定が埋込)= 疎結合化で剥がす対象

**具体行番号・内容つき。ここが「基盤抽出 (a)」で最初に手を入れる箇所。**

| ファイル:行 | 埋め込まれた渋谷固有物 | 現状の性質 | 剥がし方 |
|---|---|---|---|
| `cognition/deliberate.py:14` | プロンプトヘッダ `"あなたは渋谷の街で暮らす一人の人間です。…"` | **コードに直書き**(キャッシュ整合のため一字一句固定と明記) | `"{city_name}の街で暮らす"` へ環境変数化。ただし既定再現性の維持に注意 |
| `cognition/deliberate.py:208` | `"「この時間の渋谷は…」のような情景報告"` の抑制注意文 | コード直書き | 都市名を環境から差す |
| `world/transit.py:30-31` | GTFS の駅名フィルタ `"渋谷" / "Shibuya"` で停車判定 | **基盤ローダに固有駅名が直書き** | 対象駅名を環境設定(transit.station_names)に外出し |
| `agents/persona.py:147-152` | `"渋谷の外" / "渋谷に通勤・通学" / "渋谷の街で暮らしている"` の居住文 | 手続き生成経路のみ(名簿があれば名簿優先) | 都市名テンプレ化。名簿(B)経路は既に疎 |
| `agents/persona.py:18-31` | 日本人名リスト・日本語職業リスト・職業→POIカテゴリ写像 | 手続き生成のデフォルト(名簿で上書き可) | 名前/職業辞書を環境パックへ(言語・文化依存) |
| `diversity.py:142` | `"あなたは観光で渋谷を訪れている"` プロンプト、`languages:[英語,中国語,韓国語]` 既定 | 機構は汎用・語だけ渋谷/日本 | 都市名・言語リストを環境から差す |
| `annual.py:5-6,27,63-66,104` / `cognition/routine.py:297,596` | **渋谷ハロウィン型群集**・集会ノード=**スクランブル交差点(地図原点 (0,0) 最近傍)** | 機構は汎用だが「原点=スクランブル」の座標規約と「10/31=群集」既定が渋谷前提 | 集会ノード・群集日を環境設定(gathering_point, crowd_events)へ。config `annual_events.events` で上書きは可能 |
| `media.py:60-65` | 架空メディア題(`夜のスクランブル`/`ハチ公前ニュース9`/`渋谷トークナイト`/`ハチ公クエスト` 等) | 渋谷世界に閉じた造語(R17 順守) | 題プールを環境パックへ(文化色) |
| `schedule.py:49-50` | 地名レキシコン(`スクランブル交差点/ハチ公前/道玄坂/宮益坂/渋谷駅/新宿/原宿/表参道/恵比寿`) | 会話パーサの地名辞書 | 地名辞書を環境(地図由来の地名集合)から生成 |
| `economy.py:21-27,35,97-111` | 日本語職業→賃金写像 `WAGE_CAT`、公務員(区職員/警察官/消防士)、**東京都最低賃金 1226**、公務員日給 | 機構は汎用・**値/職業名が日本/東京** | 職業辞書・賃金表・最低賃金を「制度パック」へ。build_economy は既に config 上書き対応=seam あり |
| `government.py:1,22-24,27-41,62-78` | ward=渋谷区/metro=東京都/nation=国、住民税6:4、消費税10%/8%(78:22)、所得税実効率、区予算 60,000,000(=1,468.73億÷24.4万×100) | 機構は汎用・**税率/予算が日本/渋谷** | 税制・予算を「制度パック(JP-Shibuya)」に。build_government_cfg は config 上書き対応=seam あり |
| `rules.py:41,127` | `渋谷パートナーシップ条例 2015` を宣言型 rule のモデルとして言及 | コメント/例示中心 | 例示の脱渋谷(制度は汎用の declare 型) |
| `engine/scheduler.py:1780,1935,2112,2576` | 「渋谷で働く扱い」「警察官=東京都公安職(警視庁)」「渋谷ハロウィン型群集」 | オーケストレータのコメント+群集 phase | 群集は annual 側の環境化に従属。他はコメント主体 |
| `agents/agent.py:20` | `visitor` の説明「渋谷昼間人口の~56%」 | **コメントのみ**(挙動非依存) | 影響なし(記述の更新のみ) |
| `world/map.py:20-21,164` | 既定フロアガイド `data/floorguide_shibuya.json`、`"地下通路(渋谷ちかみち)"` の表示名 | 既定パスが渋谷固定・表示名に渋谷 | 既定パスを環境設定へ・表示名は地図データ由来に |
| `society/__init__.py:1` / `observer/schema.py:127` | docstring・イベント説明に「渋谷」「スクランブル」 | ドキュメント文字列のみ | 影響なし |

**基盤/環境の判定(ユーザー問い: ハードコードされた日本語プロンプト・日本制度は基盤か環境か)**:

- **日本語という言語**はモデル層の選択(`model.lang: ja|en`)=**基盤の設定項目**。プロンプトの
  *構造*(JSON スキーマ・役割定義)は基盤。しかしプロンプト内の**「渋谷」という語**は**環境**であり、
  `{city}` として環境から注入すべき(現状 deliberate.py に直書き=(C))。
- **日本制度(最低賃金1226・供託金30000・議会・住民税6:4・消費税)**は**環境(制度レイヤ)**である。
  ただし**累進課税・最低賃金の床・供託金による参入障壁・代表制議会という"機構"は基盤**。
  値と機構が既に分離され(`build_economy`/`build_government_cfg`/`institution_routes` は config 上書き対応)、
  **デフォルト値だけが日本固定**なので、デフォルトを「JP 制度パック」に移せば完全に環境化できる。

---

## 3. 結合点と切断面(A が B に依存する箇所)

### 3-1. きれいな切断面(config パス束縛 = そのまま (b) 環境モジュールの境界)

`engine/simulation.py` は場所固有資産をすべて**config のパス経由**で読む。ここが最良の切断面:

- `simulation.py:31-34` — `cfg.world.map` → `CityMap(map_path)`(地図 JSON)
- `simulation.py:45-49` — `cfg.transit.file` / `cfg.transit.gtfs_dir` → `Transit(...)`(ダイヤ)
- `agents.personas_file`(config)→ `build_agent(entry=…)`(名簿)
- `organizations.book` / `organizations.assignments`(config)→ 組織台帳・配属
- `world.scenario` / `scenario_params`(config)→ `build_scenario`(摂動)
- `annual_events.events` / `weather` / `calendar.start_date`(config)→ 暦・行事・天気

いずれも**コードを触らず conf 差し替えで別環境に切替可能**。`CityMap` は OSM 形式 JSON を読む汎用
ローダ(`map.py:24-81`)、`Router` は任意グラフ、`scenario.py` は地図ローカル座標=**既に脱渋谷設計**。
→ **(b) 環境モジュールは「この config 束縛群を1つの env pack マニフェストに束ねる」だけで骨格が立つ。**

### 3-2. 汚れた切断面(コードに直書きの場所依存 = (a) 基盤抽出で除去)

§2-C の (C) 群がこれ。優先度順:

1. **`cognition/deliberate.py`** のプロンプト「渋谷」直書き(:14,:208)— 最頻出の場所結合。`{city}` 化。
2. **`world/transit.py:30-31`** の駅名フィルタ「渋谷/Shibuya」直書き — GTFS ローダの一般化を阻む。
3. **`annual.py`/`routine.py`** の「原点(0,0)=スクランブル」座標規約 + 「10/31=群集」既定 — 集会点/群集日を環境設定へ。
4. **`economy.py`/`government.py`** の日本制度デフォルト値 — 「JP 制度パック」へ(機構は残す)。
5. **`persona.py`/`media.py`/`schedule.py`** の日本語名・題・地名辞書 — 言語/文化パックへ。

### 3-3. import 結合(A→B の直接 import は無い=良好)

`grep` の結果、`src/` から `data/` を**直接パスで固定 import している基盤モジュールは無い**
(すべて config 経由 or 既定パス定数)。唯一 `world/map.py:20-21` が既定フロアガイドを
`data/floorguide_shibuya.json` に**ハード既定**しているのみ(存在すれば遅延ロード)。
基盤同士の import(`simulation → agents/cognition/world/observer/llm/factors`)は健全な方向依存で、
**環境データへの依存はすべて実行時 config 注入に閉じている**。これは分離作業を著しく楽にする。

### 3-4. 推奨する層構成(Concordia/AgentSociety を参考にした落とし所)

```
core/(基盤・場所非依存)                     env/(環境パック・差し替え可能)
  cognition/  factors/  agents(memory,traits)   geo/       (map JSON: 道路/建物/POI/フロア)
  llm/  net/  observer/  labeling/  actions/     transit/   (ダイヤ/路線/GTFS)
  relations opinion status tools recursion       society/   (組織台帳/ペルソナ名簿/人口)
  needs health household commerce inner_life     institution/(税/賃金/条例/経済定数=制度パック)
  world/{clock,calendar,geom,routing,             culture/   (イベント暦/言語/名前/題プール/地名辞書)
         vision,perception,scenario,traffic}      prompts/   (都市名・文体の環境差分)
  engine/{simulation,scheduler,checkpoint}      ─────────────────────────────────────
                                                env pack manifest(1ファイルで上記を束ねる)
```

`world/map.py`(汎用ローダ)は core に残し、読む**データ**を env/geo に置く、が自然な線引き。

---

## 4. 環境要素の階層分解と自動化難易度

現渋谷環境を構成要素に分解し、各要素の入力データ源と自動化難易度を示す。
難易度は「そのまま任意都市へ一般化する」観点(高=手作業/都市個別、低=1コマンド)。

| 階層 | 要素 | 入力データ源 | 自動化難易度 | 理由 |
|---|---|---|---|---|
| **地理** | 道路網(歩行/車/自転車・地上/地下/デッキ) | OSM/Overpass(`build_map.py`)。OSMnx で一般化可 | **低** | 市名/bbox から位相簡約グラフを自動取得。地下・デッキも level/layer タグから取れる |
| | 建物フットプリント(用途 kind) | OSM。日本は **PLATEAU**(CityGML)で用途・高さ・築年つき | **低〜中** | OSM 建物は網羅的だが用途タグに粗密。PLATEAU があれば semantic で高品質(日本限定) |
| | POI(実名の店/会社/施設) | OSM POI(name/amenity/shop) | **中** | カテゴリ分類・命名にノイズ。**R17 で実名不可**→匿名化/架空化の後処理が必須 |
| | フロア/垂直レイヤー(館内フロア構成) | `floorguide_shibuya.json`(**手作業**)+ OSM level タグ | **高** | 屋内フロアガイドは公開データが乏しく主に手作業。PLATEAU LOD4(屋内)は稀 |
| **交通** | 鉄道ダイヤ(始発/終電/間隔) | ODPT API・**GTFS**(`fetch_odpt.py`→`build_transit_odpt.py`) | **中** | GTFS は標準フォーマットで取込確立。ただし API キー・事業者網羅・地域差(ODPT は首都圏) |
| | 路線・駅(駅順・位置) | ODPT `Railway`/`Station` | **低〜中** | メタは構造化済み。停車判定に固有駅名フィルタ(transit.py の (C) を要一般化) |
| | 背景交通(信号/車線/一方通行/ゲートウェイ) | OSM タグ(`build_traffic.py`) | **中** | signal/lane/oneway タグは疎で、既定補完(default_lanes 等)が要る |
| | バス/タクシー | GTFS(バス)/ 合成・運賃モデル(タクシー) | **中** | バス GTFS は取込可。タクシーは分担率較正(2026-07-09 の production.yaml で 0.02 に較正済) |
| **社会** | 組織台帳(会社/学校の規模・産業・時間構造) | e-Stat 産業構成統計 → **架空台帳**(`build_orgs.py`) | **中** | 統計→合成の写像は決定論化済み。**R17 で実名不可**=匿名合成が前提 |
| | 職・勤務時間・就学課程 | 統計 + テンプレ | **中** | 職業→勤務窓/POIカテゴリの写像はテンプレ。文化差(日本の職種)を要差替 |
| | ペルソナ分布(属性・性格・価値観) | **IPF × e-Stat 渋谷** + 語彙テンプレ(`gen_personas.py`/`persona.py`) | **中〜高** | IPF は周辺統計(国勢調査)が要る。文章化に LLM(Verbalized Sampling)。名前/職業は言語固有 |
| | 人口・流入(昼間人口・出入口配分) | `shibuya_population.json`(統計 + **手作業**) | **中〜高** | 昼間人口・沿線流入は都市個別調査。二峰到着等はチューニング要素 |
| **制度** | 経済定数(最低賃金/物価/賃金表) | 東京労働局・統計(**手入力**。config) | **中** | 公表値だが都市/国個別。値は少数=手入力で足りる(機構は基盤) |
| | 税・予算(所得税/住民税/消費税/区財政) | 国税庁・区財政資料(**手入力**。`government.py` 既定) | **中〜高** | 税率・配分・予算は法域個別。スケール換算も要設計 |
| | 法・条例(参入許可/供託金/議会/執行) | 制度調査(**手作業**。config `institution_routes`/`rules`) | **高** | 条例・選挙制度は法域固有(例: パートナーシップ条例・供託金30万・区議会34)。汎用化は機構のみ |
| **文化** | イベント暦(正月/ハロウィン/年末) | 手作業/文化知識(`annual_events.events`) | **中** | 命名行事は curation。渋谷ハロウィン型群集は**地域固有**(集会点も地図個別) |
| | 言語 | config(`society_diversity.languages`) | **低** | ラベルリスト。ただし感情辞書(`sentiment_lexicon.json`)は言語固有で別途要る |
| | 名前/語彙/メディア題/地名辞書 | 手作業/LLM(`persona.py`/`media.py`/`schedule.py`) | **中** | 言語・文化色。LLM text-to-environment で半自動化余地 |

### 4-1. 自動環境生成の設計指針(要素別の生成経路)

- **ほぼ全自動化できる層(地理・交通)**: `OSMnx/Overpass →(建物用途は PLATEAU 補強)→ map JSON` /
  `GTFS(ODPT等)→ transit JSON`。既存 `build_map.py`/`fetch_odpt.py` を任意都市パラメータ化するのが最短。
  ボトルネックは**屋内フロア**(公開データ薄=手作業 or LLM 生成 or PLATEAU LOD4)。
- **半自動化の層(社会)**: `e-Stat 周辺統計 → IPF → ペルソナ` / `産業統計 → 合成組織台帳`。
  周辺分布さえ用意すれば決定論生成できる。**R17(実名禁止)の匿名化**が共通の後処理。
- **手作業が残る層(制度・文化)**: 値は少数で手入力が現実的。**機構は基盤に既存**(税/最賃/供託金/議会/条例declare)。
  「制度パック(例: JP-Shibuya, JP-Osaka, US-generic)」を YAML で用意する運用が妥当。
- **LLM 生成の使いどころ**: OSM/統計で埋まらない「長い裾」— 架空店の内装・組織の物語・地名/題プール・
  ペルソナ文章化。SimWorld 流の**シーングラフ + RAG 編集**、VirtualHome/ALFWorld 流の**テキスト環境記述**が
  出力スキーマの候補。生成物は決定論キャッシュ化して実行時の再現性を守る(既存 ODPT キャッシュと同方針)。

### 4-2. (c) 自動環境生成パイプライン(素案)

```
都市名/bbox ─┬─ OSMnx/Overpass ───────────→ geo(道路/建物/POI)      ┐
             └─ PLATEAU(CityGML, 日本) ───→ 建物用途/高さ/フロア     │
GTFS/ODPT ──── build_transit ──────────────→ transit(ダイヤ/路線)   ├─→ env pack
e-Stat 周辺分布 ── IPF + Verbalized Sampling ─→ personas/organizations │   manifest
制度パック(手作業 YAML: 税/最賃/供託金/条例) ─→ institution           │  (1ファイル)
文化 curation + LLM(題/地名/イベント) ────────→ culture               ┘
```

各段は**決定論・オフライン生成→静的キャッシュ**を守り(`fetch_odpt.py` の設計思想)、
シミュ本体は生成済み JSON を読むだけ=実行時ネット/LLM 依存ゼロで再現性を保つ。

---

## 5. 出典

一次ソース優先。アクセス日 2026-07-10。個別数値の一次確認が未了の箇所は本文で「(要確認)」と明記した。

**アーキテクチャ分離の先行事例**
- DeepMind Concordia (GitHub): https://github.com/google-deepmind/concordia
- Concordia components README: https://github.com/google-deepmind/concordia/blob/main/concordia/components/README.md
- Concordia v2.0 解説(Cooperative AI): https://www.cooperativeai.com/post/google-deepmind-releases-concordia-library-v2-0
- Concordia 論文 "Generative agent-based modeling…"(DeepMind): https://deepmind.google/research/publications/64717/
- AgentSociety 論文 (arXiv 2502.08691): https://arxiv.org/html/2502.08691v1
- AgentSociety (GitHub): https://github.com/tsinghua-fib-lab/AgentSociety
- AgentSociety docs: https://agentsociety.readthedocs.io/en/latest/
- Generative Agents (Park 2023, PDF): https://3dvar.com/Park2023Generative.pdf
- Generative Agents (ACM DL): https://dl.acm.org/doi/fullHtml/10.1145/3586183.3606763
- Mesa-Geo (docs): https://mesa-geo.readthedocs.io/stable/index.html
- Mesa-Geo (GitHub): https://github.com/mesa/mesa-geo
- AgentTorch (OpenReview PDF): https://openreview.net/pdf?id=JlBBoZBOeF
- AgentTorch (site): https://agenttorch.github.io/AgentTorch/
- Project Sid / PIANO (arXiv 2411.00114): https://arxiv.org/abs/2411.00114
- Project Sid (GitHub): https://github.com/altera-al/project-sid
- ALFWorld (arXiv PDF): https://arxiv.org/pdf/2010.03768
- VirtualHome: https://www.researchgate.net/publication/329750393_VirtualHome_Simulating_Household_Activities_Via_Programs
- SimWorld(シーングラフ+RAG 編集, arXiv PDF): https://arxiv.org/pdf/2512.01078

**環境の自動生成**
- OSMnx (GitHub): https://github.com/gboeing/osmnx
- OSMnx (docs): https://osmnx.readthedocs.io/
- Project PLATEAU (国交省, EN): https://www.mlit.go.jp/plateau/en/
- PLATEAU 概説(ArchDaily): https://www.archdaily.com/1040412/from-data-to-digital-twins-japans-plateau-project-offers-open-access-models-of-more-than-250-cities
- GTFS 仕様: https://gtfs.org/resources/producing-data/
- GTFS グラフ化(Transit network analysis): https://www.sciencedirect.com/science/article/pii/S1077291X22001151
- LLM Meets Scene Graph (arXiv 2505.19510): https://arxiv.org/abs/2505.19510

**本コードベース(読み取り・行番号は本文参照)**
- `conf/config.yaml` / `conf/production.yaml`(実験ノブ・本番プロファイル)
- `src/society/engine/simulation.py`(config パス束縛=切断面)
- `src/society/world/{map,scenario,transit,routing}.py`(環境ローダ)
- `src/society/{economy,government,rules}.py`(制度機構+日本デフォルト値)
- `src/society/cognition/{deliberate,routine}.py`・`src/society/{annual,media,schedule,diversity}.py`(混在=(C))
- `src/society/agents/persona.py`(ペルソナ生成 seam)
- `scripts/{build_map,build_orgs,gen_personas,fetch_odpt,build_transit_odpt,build_traffic}.py`(環境生成パイプライン)
- 関連調査: `docs/research/lexicon-ipf-shibuya.md` / `shibuya-organizations.md` / `shibuya-government.md` / `odpt-integration.md` / `shibuya-buildings-traffic-odpt.md`
