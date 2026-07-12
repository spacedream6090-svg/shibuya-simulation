# 3D 可視化 リサーチ記録 — Blender / PLATEAU / Web3D

バッチE(3D 可視化)の技術調査。目的は「シミュ結果を 3DCG 化して視点をグリグリ動かして観察」+「ブラウザで即確認できる Web3D」+「将来の PLATEAU LOD2 差し替え」への設計。
調査日: 2026-07-05(Web 調査。出典は末尾)。関連: [`docs/lit/viz__plateau-pipeline-overview.md`](../lit/viz__plateau-pipeline-overview.md)(sim⇄viz 疎結合の設計核)。

---

## 0. 本バッチの実装(現状の到達点)

sim⇄viz 疎結合の原則(sim はログを吐くだけ・viz は読み取り専用の下流)に沿い、**中立 3D シーン契約**を新設した。

- `scripts/export_3d.py` … ラン → `runs/<name>/scene3d/{scene.json, tracks.json, buildings.glb}`。座標系は local-m(X=east, Y=north, Z=up)のまま。`buildings.glb` は依存追加なしで numpy+stdlib により手書き生成(footprint の ear clipping 自作・凹対応、kind 別頂点色、glTF 標準 Y-up)。
- `viz/make_viewer3d.py` … `scene3d/` を埋め込んだ自己完結 `viewer3d.html`。three.js r128(MIT, `viz/vendor/`)+ OrbitControls。建物押出し(ExtrudeGeometry)、道路ライン、地下鉄=半透明チューブ、エージェント=InstancedMesh のカプセル、昼夜(sim 時刻連動の DirectionalLight+空色)、クリックで人物情報。移動は 2D ビューアの `posAt`/`alongPath` を移植して連続補間。
- `viz/blender_import.py` … Blender 4.x 用(bpy のみ・pyarrow 非依存)。`scene.json` から建物押出し(または `--use-glb` で glb インポート)、道路/線路をカーブ、エージェント=カプセル+per-step キーフレーム(歩行はポリライン内サブキー)、太陽の日周、EEVEE 設定、オービット Empty+カメラ。

**この契約の要点**: LOD2 に差し替えても `scene.json` のキー(`id, kind, name, footprint, height, base`)は変えない。だから下流 viewer/blender を触らずに建物ソースだけ置換できる(→ §4)。

---

## 1. Blender への都市データ取込み

### 1.1 blosm(旧 blender-osm)
- 「数クリックで OpenStreetMap / Google 3D cities / 地形を DL & インポート」する Blender アドオン。**global coverage**。無償の base 版と有償 Pro(Gumroad)。
- 建物: OSM の `height` / `building:levels` から押出し、多様な屋根形状に対応。**base 版はテクスチャ無し**、Pro はデフォルトマテリアル+タイル状テクスチャ+UV+「夜の点灯窓」表現。地形(約 30m 解像度)、川・湖・森・植生をポリゴンで取込み、GPX 投影も可。GPL でソース付属。
- 位置づけ: 本プロジェクトの `export_3d`(OSM 箱押出し)と**同系統**。blosm を使えば Blender 単体で OSM 都市を作れるが、シミュ座標系(local-m 原点=スクランブル交差点)や建物 ID との対応は別途必要。→ 本実装は「sim の建物 ID と厳密一致する自前押出し」を優先し、blosm は"景観の厚み付け"の補完候補とする。

### 1.2 BlenderGIS
- QGIS 的な GIS レイヤ(shapefile/GeoTIFF/OSM/basemap)を Blender に取込む定番アドオン。CRS 指定・地形・OSM 建物取込みが可能。CityGML は直接非対応(→ 変換が要る)。PLATEAU の GeoTIFF 地形や GIS レイヤの読込みに有用。

---

## 2. PLATEAU LOD2 渋谷区の入手と変換

### 2.1 データ入手(G空間情報センター)
- 「3D都市モデル(Project PLATEAU)**渋谷区(2023年度)**」が G空間情報センターで公開。**商用利用可・翻案自由**(PLATEAU Site Policy、完全開放型)。
- 建築物モデルの提供形式:
  - **CityGML v4**: LOD0 / LOD1 / **LOD2.0** / **LOD2.2**(約 636 MB)。これが正準ソース。
  - **3D Tiles v4**: LOD1 / LOD2(Web ストリーミング用)。
  - 交通(道路): CityGML / MVT / 3D Tiles。都市設備・災害リスク(浸水/土砂)・植生・地形(DEM)・橋梁・地下街も同梱。
- 注意: **最新版では FBX/OBJ の直接配布は縮小**され、「CityGML を各自 SDK 等で FBX/OBJ/glTF に変換して使う」方針に移行。DL 元: G空間情報センター `plateau-13113-shibuya-ku-2023`、PLATEAU Portal / Open Data。

### 2.2 CityGML → Blender / three.js の変換経路

| ツール | 実装/形態 | 変換先 | 用途 | メモ |
|---|---|---|---|---|
| **Plateau-Blender-Importer**(nneri-hin) | Blender アドオン(Python) | Blender メッシュ | Blender で LOD2 建物/道路/橋 | 2023-05 公開。`.gml` を直接インポート。属性保持。 |
| **plateaukit** | Python ライブラリ/CLI | GeoJSON, glTF, 3D Tiles 等 | 前処理・変換・簡易ビューア | LOD2・標高対応。バッチ変換向き。 |
| **PLATEAU GIS Converter** | Rust 製 CLI/GUI | 一般 GIS/3D 形式 | CityGML→他形式の高速変換 | 公式系。大容量に強い。 |
| **PLATEAU SDK for Unity / Unreal** | ゲームエンジン SDK | OBJ/FBX/glTF 書出し | 高品質メッシュ化・テクスチャ | 緯度経度→平面直角変換内蔵。商用可。Blender へは glTF 経由。 |
| **py3dtiles / loaders.gl / 3DTilesRendererJS(NASA-AMMOS)** | Python / JS | 3D Tiles 読込・生成 | three.js/Web で 3D Tiles をストリーミング | three.js 側は 3DTilesRendererJS か CesiumJS で LOD 配信。 |
| **PLATEAU VIEW 3.0 / CesiumJS + 3DCityDB** | Web アプリ | 3D Tiles 表示 | すぐ閲覧・重畳 | 既存 lit ノート(Part B)の Web 経路と一致。 |

- **Blender 実務のコツ**(CrossRoad 記事): 旧来は FBX が最も位置精度が良く D&D で読込み(OBJ は高さがずれやすい)。子階層 `surfaceMember` を選び View → Frame Selected で建物にフォーカス。現行は CityGML→(SDK/plateaukit)→glTF/FBX が主経路。
- **Web 実務**: 渋谷区は **3D Tiles(LOD1/2)が既製**なので、three.js では 3DTilesRendererJS、あるいは CesiumJS に載せるのが最短。自前 glTF 化するなら plateaukit/GIS Converter でタイル化。

---

## 3. Unity / Unreal / NVIDIA Omniverse の位置づけ

- **PLATEAU SDK for Unity / Unreal**(国交省×Synesthesias、無料・商用可): CityGML を取込み、緯度経度→平面直角座標変換・メッシュ化・属性 API・OBJ/FBX/glTF 書出し。**渋谷駅・スクランブル交差点を範囲選択で高品質取得**。写実テクスチャや群衆・演出が要るならエンジン経路が有利。本プロジェクトからは「Web/Blender へ glTF を書き出す供給源」として使える。
- **NVIDIA Omniverse(USD)**: フォトリアルな 3D シミュレーション/デジタルツインの上位プラットフォーム。**Smart City AI Blueprint** では、**手続き的に生成した歩行者**を歩道・横断歩道に沿って移動させ、**OSM の道路網**を spawn zone として使う実験的挙動モデルを提供。交通流・エネルギー・混雑管理をリアルタイム可視化。ユーザー添付の「大規模人流シミュの 3D 化」文脈はここ。**位置づけ**: 数千〜数万体規模の写実的人流可視化の将来形。ただし GPU・USD パイプライン・学習コストが重く、ハッカソン段階では過剰。本実装の中立契約(scene.json/tracks.json)は将来 USD/Omniverse への書出しアダプタを足せば橋渡し可能(sim は非影響)。

---

## 4. 本プロジェクトへの導入設計

### 4.1 座標系の変換パラメータ(local-m → 平面直角 IX 系 → 緯度経度)
- **local-m**: 原点=スクランブル交差点 `origin_latlon = (35.6595, 139.70062)`、X=east, Y=north[m]。
- **緯度経度への近似逆変換**(1km 圏で十分な局所接平面近似):
  - `lat = lat0 + N / 111132.9`
  - `lon = lon0 + E / (111320 * cos(lat0))` … `cos(35.6595°) ≈ 0.8124` → 約 `90440 m/deg`
- **JGD2011 平面直角座標系 第9系(IX 系)= EPSG:6677**(東京・関東)。原点 `36°0'0"N, 139°50'0"E`。**注意: 日本の平面直角は X=北(northing), Y=東(easting)** で軸名が逆。厳密変換は pyproj で `EPSG:6668(緯度経度 JGD2011) → EPSG:6677`。
  - 手順: local-m →(上の近似で)緯度経度 → pyproj で EPSG:6677。逆も同様(PLATEAU→local-m はこの逆)。
  - 高さ: PLATEAU は標高(T.P.)基準。local-m は地面 z=0 基準なので、比較時は建物の相対高さ(`levels×3.5`)を使い、絶対標高は無視して整合を取る。

### 4.2 PLATEAU 建物 と `shibuya_osm.json` 建物 ID の照合方針
- 目的: LOD2 の実測フットプリント/屋根形状を、既存の OSM 建物 ID(`bXXXX`)に**一意対応**させる対応表 `plateau_match.json`(osm_id → gml_id)をオフラインで生成。
- アルゴリズム:
  1. PLATEAU LOD2 建物フットプリントを local-m に投影(§4.1 の逆変換)。
  2. **重心最近傍**で候補を絞る(k-NN、閾値 例 25m)。
  3. **footprint IoU**(多角形交差面積/和集合面積)で確定。IoU ≥ 0.4 を採用、複数競合は IoU 最大を採用、未マッチは OSM 押出しにフォールバック。
  4. 高さは LOD2 由来(実測)で上書き、名前/用途は OSM を優先(日本語名が豊富)。
- 実装は `scripts/` に別スクリプト(例 `match_plateau.py`)として追加する想定(本バッチ範囲外・要ユーザー合意)。

### 4.3 LOD2 差し替えでも `scene.json` 契約を変えない設計
- `export_3d` の `scene.json` 建物レコードは `{id, kind, name, footprint, height, base}` で固定。**差し替えは 2 段**:
  1. `buildings.glb` を PLATEAU LOD2 由来メッシュ(屋根形状付き)に置換 — viewer3d/blender の描画をリッチ化。glb は「id ごとの Node 名」を持たせれば per-building 選択も維持可。
  2. `scene.json` の `height`(と将来 `roof` 等の**追加**キー)を LOD2 実測で埋める — 押出しビューアも高さが正確に。
- どちらも**既存キーを削らない追加専用**の変更なので、`viewer3d.html` / `blender_import.py` は無修正で動く。ソース選択は exporter 側の差し替えに閉じ、sim には非影響(疎結合の徹底)。

---

## 5. 「今すぐ使える度」比較と推奨

| 手法 | 今すぐ度 | 精度(建物) | 対象 | 依存/コスト | 商用 |
|---|---|---|---|---|---|
| **OSM 押出し(本実装)** | ◎(完成) | 箱(levels×3.5) | Web+Blender | numpy/stdlib のみ | ○ |
| blosm(Blender アドオン) | ○ | 箱+屋根形状 | Blender | 有償Pro/無償base | ○(GPL) |
| PLATEAU LOD2 + Plateau-Blender-Importer | △ | 屋根形状+実測 | Blender | DL/変換/重い | ○ |
| PLATEAU LOD2 → glTF/3D Tiles → three.js(3DTilesRendererJS/Cesium) | △〜○ | 実測+LODストリーミング | Web | 前処理・タイル生成 | ○ |
| PLATEAU SDK for Unity/Unreal | ○ | 高品質・テクスチャ | エンジン | エンジン習熟 | ○ |
| NVIDIA Omniverse(USD) | ✕〜△ | 写実・大規模人流 | 専用 | GPU/USD/学習 | ○ |

**推奨(結論)**:
1. **今回は OSM 押出し(実装済み)を採用**。依存ゼロ・sim 建物 ID と厳密一致・Web/Blender 両対応で、ハッカソン段階の「グリグリ観察」「ブラウザ即確認」を満たす。
2. **将来 PLATEAU LOD2 差し替え**は §4 の matcher で ID 対応表を作り、`scene.json` 契約を保ったまま `buildings.glb`/`height` を LOD2 由来に置換。渋谷区は 3D Tiles(LOD1/2)が既製なので Web 大規模化は CesiumJS/3DTilesRendererJS が最短。
3. **写実・数千体規模の人流**が要件化したら Unity(PLATEAU SDK)→ glTF、その先で Omniverse(USD)を検討。中立契約があるので上流(sim)は据え置きで上位可視化へ段階移行できる。

---

## Sources
- blosm(旧 blender-osm): <https://github.com/vvoovv/blosm> / Wiki Import-OpenStreetMap <https://github.com/vvoovv/blosm/wiki/Import-OpenStreetMap-(.osm)> / <https://prochitecture.gumroad.com/l/blender-osm> / OSM Wiki <https://wiki.openstreetmap.org/wiki/Blender-osm>
- PLATEAU データ形式/入手: <https://www.mlit.go.jp/plateau/learning/tpc03-1/> / 渋谷区2023 <https://www.geospatial.jp/ckan/dataset/plateau-13113-shibuya-ku-2023> / 東京23区 <https://www.geospatial.jp/ckan/dataset/plateau-tokyo23ku> / Open Data <https://www.mlit.go.jp/plateau/opendata/>
- Blender 取込み: CrossRoad <https://www.crossroad-tech.com/entry/PLATEAU-Blender> / PLATEAU TOPIC8 <https://www.mlit.go.jp/plateau/learning/tpc08-1/> / Plateau-Blender-Importer <https://github.com/nneri-hin/Plateau-Blender-Importer> / Qiita <https://qiita.com/nneri/items/e101376b2c159c56b9c4>
- 変換ツール群: plateaukit <https://pypi.org/project/plateaukit/> / awesome-plateau <https://japan-opendata.github.io/awesome-plateau/> / PLATEAU GIS Converter <https://project-plateau.github.io/PLATEAU-GIS-Converter/manual/download_city_gml.html>
- Unity SDK: <https://project-plateau.github.io/PLATEAU-SDK-for-Unity/manual/ImportCityModels.html> / <https://github.com/Project-PLATEAU/PLATEAU-SDK-for-Unity>
- NVIDIA Omniverse: Smart City AI Blueprint <https://blogs.nvidia.com/blog/smart-city-ai-blueprint-europe/> / crowd sim フォーラム <https://forums.developer.nvidia.com/t/ho-to-simulate-crowd-in-omniverse/195681>
- 座標系(JGD2011 / IX 系 EPSG:6677): <https://situx.github.io/proj4rdf/data/def/crs/EPSG/0/6677/index.html> / EPSG 一覧 <https://lemulus.me/column/epsg-list-gis> / PLATEAU 座標・高さ <https://www.mlit.go.jp/plateau/learning/tpc03-4/> / WGS84→平面直角(pyproj) <https://qiita.com/XPT60/items/9aa41cab07ce6369fb99>
- Web 3D Tiles: three.js 3DTilesRendererJS(NASA-AMMOS) / loaders.gl / CesiumJS + 3DCityDB(cf. `docs/lit/viz__plateau-pipeline-overview.md`)

---

# 追記(2026-07-06): 可視化メインを Unreal Engine + PLATEAU SDK for Unreal に採用

ユーザー決定により、可視化の**メイン経路を Unreal Engine 5 + PLATEAU SDK for Unreal** に変更(Blender はコード維持の quick-look)。目的は PLATEAU の**実形状の渋谷**にシミュ結果(エージェント・車)をフォトリアルに載せ、視点を自由に動かすこと。UE はこの開発環境に無いため、以下は一次情報リサーチ + レビュー用コード/手順書の納品(実機未検証)。納品物: `viz/unreal/import_shibuya_sim.py`(UE エディタ Python)・`viz/unreal/SimReplayActor_DESIGN.md`(ランタイム再生設計)・`viz/unreal/README_UE.md`(ゼロからの手順)・`scripts/export_ue.py`(local-m→UE 変換 + 軌跡フラット化)。

## 6. 確定事実(一次情報)

### 6.1 PLATEAU 渋谷区データ(採用 = 2025年度)
- **3D都市モデル(Project PLATEAU)渋谷区(2025年度)** が G空間情報センターで公開。前回調査の 2023年度から**更新済み**。ID `plateau-13113-shibuya-ku-2025`。
- 建築物: **CityGML v5 仕様、LOD0 / 1 / 2.0 / 2.2**。**3D Tiles / MVT** も同梱。DL ファイル: `13113_shibuya-ku_pref_2025_citygml_1_op.zip`(CityGML)・`13113_shibuya-ku_pref_2025_3dtiles_mvt_1_op.zip`(3D Tiles)・`13113_shibuya-ku_2025_related.zip`。
- **FBX/OBJ は配布しない**方針(SDK で各自変換)。UE には CityGML を SDK で直接読ませる。
- ライセンス: **PLATEAU Site Policy(商用可・翻案自由・無償)**。地図情報レベル2500相当。
- **原典撮影/基準日**: カタログ頁に**明記なし**(カタログ作成 2026-03-16 / 更新 2026-04-03 の UTC タイムスタンプのみ。年度=2025年度、航空測量由来)。厳密な撮影年月は CityGML のメタデータを DL 後に確認する必要がある(§6.4 の日付整合に影響)。

### 6.2 PLATEAU SDK for Unreal
- **対応 UE**: SDK **v3.2.0〜v3.2.2(2025-03〜06)= UE 5.5.4**。v3.1.1 以前は **UE 5.3.2**。→ **UE 5.5 + SDK v3.2.x** を採用推奨。
- CityGML **v2 以降 / v3 まで対応**(v5 の渋谷2025 も読込可)。導入は Fab 版 or GitHub Releases の zip を `Plugins/` へ。
- インポート UI: **基準座標系の選択**(平面直角 9 系から選ぶ = 渋谷は**第9系 EPSG:6677**)・**基準座標系からのオフセット値**(東西/南北/高さ [m] で原点を指定。緯度経度直接入力は不可)・**最小/最大 LOD**・**モデル結合単位**。取り込み時に CityGML をポリゴンメッシュへ変換。
- **単位**: UE 既定 **1uu = 1cm**。PLATEAU/CityGML は **m** 基準 → **メートル値 ×100** で UE 配置(FBX 経由でも 100 倍が定石)。

### 6.3 座標変換の結論(sim ↔ UE ↔ PLATEAU)
- sim(local-m, ENU, Z-up 右手系, m, 原点=スクランブル交差点 35.65950,139.70062)→ UE(cm, Z-up, 左手系)。
- 変換は **`scripts/export_ue.py` に一本化**(UE 側 C++/BP は素直な再生器に保つ)。基本写像 `ux=east, uy=-north(y_flip で鏡像回避), uz=up` → heading 回転 → ×100 → +offset[uu]。
- **原点合わせの決定値**: スクランブル交差点の **JGD2011 平面直角第9系(EPSG:6677)= 北距 X≈-37768.576 m / 東距 Y≈-12015.952 m**(Kawase 2011 の TM 級数で自算、GSI 準拠)。SDK インポートのオフセットにこの値を入れれば **PLATEAU 原点 = スクランブル交差点 = sim 原点** が自動一致し、`export_ue.py` は `--offset 0 0 0`(既定)でよい。
- **向き(heading)と鏡像(y_flip)**は SDK の平面直角→UE 軸割当のバージョン差があるため、**初回のみエディタで非対称ランドマーク(ハチ公/渋谷駅)と実測合わせ**(90°刻み×反転の 8 通りで必ず一致)。高さは PLATEAU が標高基準・sim が地面基準なので交差点標高ぶんを 1 回 offset 調整。

### 6.4 日付整合(OSM 取得日を PLATEAU 基準日に合わせる)= 後続の地図バッチへの結論
- **課題**: シミュの街は OSM 由来(`data/shibuya_osm.json`)。PLATEAU 実形状と整合させるには **OSM のスナップショット日を PLATEAU の撮影基準日に寄せる**。
- **手段**: Overpass の **attic(過去日)クエリ**。ヘッダに `[date:"YYYY-MM-DDThh:mm:ssZ"]`(ISO 8601 UTC)を付けるとその時点の DB 状態を返す。公開インスタンス(overpass-api.de 等)が attic 対応。2012-09-12 以前は不可。Geofabrik の履歴(`.osh.pbf`)からローカル再構築も可。
- **推奨取得日(暫定)**: PLATEAU 渋谷2025 の**撮影基準日がカタログ非公開**のため、**確定は DL 後に CityGML メタデータの撮影日を読んで最終決定**する。それまでの実務既定は **`2025-04-01T00:00:00Z`**(2025年度の起点、街並みの大改変が無い渋谷中心部では十分な近似)。撮影日が判明したらその年月に差し替える(例: 撮影が 2024年秋なら `2024-10-01T00:00:00Z`)。
- **Overpass クエリ例**(渋谷中心 bbox・建物。地図再生成バッチが使う雛形):
  ```
  [out:json][timeout:60][date:"2025-04-01T00:00:00Z"];
  (way["building"](35.653,139.694,35.665,139.706);
   relation["building"](35.653,139.694,35.665,139.706););
  out body geom;
  ```
  道路・鉄道も同 bbox・同 `[date:]` で `highway`/`railway` を取得すれば、建物と時点を揃えられる。

## 7. Blender / Web3D の位置づけ(更新)
- **UE = メイン**(フォトリアル・自由視点・大規模人流の本命)。
- **Web3D(`viewer3d.html`)= quick-look 維持**(依存ゼロ・ブラウザ即確認)。**Blender = コード維持**(EEVEE レンダの補助)。
- 中立契約(`scene.json`/`tracks.json`)は不変。UE 経路は `export_ue.py` を**下流に足しただけ**で、sim も既存 exporter/viewer/blender も無改変(疎結合を徹底)。

## 8. UE 未検証項目(実行不可のため正直に)
- `add_component_by_class` での ISM 追加可否(UE/SDK バージョン差)。不可なら BP で ISM 保持アクタを用意。
- `BatchUpdateInstancesTransforms` の引数・ISM 原点(シリンダ中心 vs 足元)補正の符号。
- SDK の平面直角→UE 軸割当(heading/y_flip の確定値)と交差点標高オフセット。
- Sequencer 方式は ISM インスタンス個別キー不可のため小規模(1体=1アクタ)限定であること。
- 数千体超は Niagara+VAT / AnimToTexture へ切替(README_UE §9)。

## 追記ソース(一次情報)
- 渋谷2025: <https://www.geospatial.jp/ckan/dataset/plateau-13113-shibuya-ku-2025>
- SDK for Unreal: <https://github.com/Synesthesias/PLATEAU-SDK-for-Unreal> / Releases <https://github.com/Project-PLATEAU/PLATEAU-SDK-for-Unreal/releases> / インポート <https://project-plateau.github.io/PLATEAU-SDK-for-Unreal/manual/ImportCityModels.html> / TOPIC17 <https://www.mlit.go.jp/plateau/learning/tpc17-2/> / 単位(TOPIC10) <https://www.mlit.go.jp/plateau/learning/tpc10-1/>
- 製品仕様書 第5版: <https://www.mlit.go.jp/plateau/file/libraries/doc/plateau_doc_0001_ver05.pdf>
- Overpass 日付指定: QL <https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL> / Attic Data <https://wiki.openstreetmap.org/wiki/Attic_Data>
- UE 大量群集: <https://vrealmatic.com/unreal-engine/crowds> / OverCrowd(Niagara+VAT) <https://jettelly.com/blog/simulate-massive-crowds-in-unreal-engine-5-with-overcrowd>
