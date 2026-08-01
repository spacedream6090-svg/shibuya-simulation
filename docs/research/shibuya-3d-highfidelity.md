# 高精細な渋谷 3D モデル — 入手可能性・ライセンス・統合方法の調査

作成: 2026-08-02 / 調査役: Opus 5(実行役リサーチャー)
対象: ①three.js ビューア(`viz/make_viewer3d.py` → `viewer3d.html`・完全自己完結 static HTML・外部 CDN/fetch 不可)
②自前 Social Force Model(`src/society/world/sfm_core.py`)への幾何供給
関連: [`plateau-2025-update-notes.md`](plateau-2025-update-notes.md) / [`../plans/plateau-3d.md`](../plans/plateau-3d.md) /
[`social-force-crowd.md`](social-force-crowd.md) / [`dt-integration-deep.md`](dt-integration-deep.md)

> 本書の数値には **本調査で手元データを実測した値**(🔬印)と **Web 出典の値**(URL 付き)が混在する。
> 実測は 2026-08-02 に `C:\Users\<user>\Desktop\13113_shibuya-ku_pref_2025_citygml_1_op{,.zip}` および
> `13113_shibuya-ku_pref_2025_3dtiles_mvt_1_op.zip`(未展開のまま zipfile で走査)に対して行った。
> **本調査ではコードもデータも一切変更していない**(読み取りのみ)。

---

## 0. 先に結論

1. **「高精細な渋谷」を無償・再配布可で得る道は実質 PLATEAU 一本**。Google Photorealistic 3D Tiles は
   *オフライン保存・キャッシュ・ジオデータ抽出が明示的に禁止*で、本プロジェクトの
   「HTML 1枚に全部埋め込んで GitHub 公開ミラーに置く」形態とは**原理的に両立しない**。
2. **すでに手元にある `13113_shibuya-ku_pref_2025_3dtiles_mvt_1_op.zip`(608 MiB・未展開)が最大の未使用資産**。
   この中に **テクスチャ付き LOD2.2 建築物**(シム bbox 内 180.9 MB/148タイル)・**道路 LOD3**(11.8 MB)・
   **地下街 LOD4.1**(15.7 MB・渋谷駅周辺全域)が **すでにタイル化+アトラス化済み**で入っている。🔬
   `docs/plans/plateau-3d.md` で「3D Tiles は不採用」としたのは*ランタイムでタイルを fetch する方式*の話で、
   **ビルド時に Python で読んで既存の自前コーデックへ焼き込む用途は不採用理由に当たらない**。
3. **物理シムにとっての本命は「見た目」ではなく `ubld` LOD4.1 と `tran` LOD3.0**。
   実測で地下街に **内壁 1,934 面 / 床 145 面 / 扉 188 / 階段・スロープ 5** が入っており、🔬
   これは `sfm_core.Crowd` に現在**意図的に省略されている対壁斥力 `f_iW`** の入力そのものである。
4. 圧縮の制約(外部 wasm 不可)は **回避できる**。`meshopt_decoder.cjs` は wasm を base64 で
   **ファイル内にインライン内蔵**し `WebAssembly.instantiate(bytes)` するため `file://` でも動く(29.4 KB・MIT)。
   ただし**推奨は既存の自前 int16 量子化コーデックの継続**(依存ゼロ・すでに `plateau_web.json` /
   `tracks_bin.py` で実績)。Draco と KTX2 は **不可**(理由は §4.2)。
5. 推奨は **竹案(物理シム接合を先)**。松案(テクスチャ写実)は見栄えの投資であり、
   研究目標(k\* データ)への寄与は薄い。ただし本選デモの説得力には効く。

---

## 1. 現状の実測(ベースライン)

### 1.1 ビューア成果物 🔬 (`runs/rehearsal_pool10k/`)

| ファイル | サイズ | 備考 |
|---|---:|---|
| `viewer3d.html`(埋め込み版) | **90,401,652 B (86.2 MiB)** | 80 MB ゲート**超過中** |
| `viewer3d_lite.html`(分離版) | 71,505,492 B (68.2 MiB) | + サイドカー |
| `plateau_mesh.js`(サイドカー) | 18,896,156 B (18.0 MiB) | JSONP |
| `scene3d/plateau_web.json` | 18,896,140 B | int16×0.05m 量子化・**テクスチャなし** |
| `scene3d/tracks.json` | 65,809,842 B | 第76バッチで `tracks_bin` 化済 |
| `scene3d/buildings.glb` | 34,235,520 B | **Blender/UE 向け**。Web ビューアは読んでいない |
| `scene3d/terrain_web.json` | 2,672,215 B | |
| `viz/vendor/three.min.js` | 603,445 B | **r128(2021年)**。`GLTFLoader` は未 vendor |
| `viz/vendor/OrbitControls.js` | 26,375 B | |

現行 PLATEAU メッシュ = **V 1,107,132 / F 590,670 / 6,311棟**(`plateau_index.json`)、
bbox = 1.87 km × 1.54 km ≈ **2.9 km²**、原点 = スクランブル交差点 `(35.6595, 139.70062)`。

### 1.2 手元 PLATEAU データセット 🔬

| アーカイブ | サイズ |
|---|---:|
| `13113_shibuya-ku_pref_2025_citygml_1_op.zip` | 649,322,807 B (619 MiB) |
| 同 展開後 | **4,620 MB** |
| `13113_shibuya-ku_pref_2025_3dtiles_mvt_1_op.zip` | 637,073,925 B (608 MiB) **未展開** |
| `PLATEAU-SDK-for-Unreal-v3.2.2.0.zip` | 1,059,258,744 B **未展開** |

`udx/` サブディレクトリ別(展開後 MB)🔬:
`bldg 1775` / `luse 879` / `dem 834` / `fld 532` / **`tran 184`** / `veg 125` / **`frn 119`** /
`brid 50` / `urf 46` / **`ubld 33`** / `wtr 16` / `lsld 1`

### 1.3 SFM の現状

`sfm_core.py` は Helbing&Molnár(1995)/ Helbing et al.(2000) の最小実装で、
docstring に明記のとおり **対壁斥力 `f_iW` と物理接触項を意図的に省略**している。
理由も明記: 「案a は開放円領域だけを扱い、**建物外壁・車道縁石などの障害物ジオメトリを持ち込まない**」。
つまり **幾何が来れば `f_iW` を入れる余地は設計上すでに空けてある**。

---

## 2. 選択肢の棚卸し

### 2.1 PLATEAU 渋谷区 2025年度(CityGML)— 現行採用

- データセット: <https://www.geospatial.jp/ckan/dataset/plateau-13113-shibuya-ku-2025>
  公開 2026-03-16 / 最終更新 2026-04-03 / 標準製品仕様書 **第5.0版**
- 建築物 **LOD0/1/2.0/2.2**。**LOD3・LOD4 の建築物は渋谷区には無い**
  (LOD4 建築物の公開例は「東京都23区 ポートシティ竹芝(2022年度)」など別データセット)。
- 整備範囲(README 実測値・[`plateau-2025-update-notes.md`](plateau-2025-update-notes.md) §2 より):
  建物 LOD1 15.11 km²/41,626棟 ・ LOD2.0 1.16 km²/1,917棟 ・ **LOD2.2 1.41 km²/2,658棟**(都市再生緊急整備地域)、
  道路 LOD1 15.11 / LOD2 2.57 / **LOD3.0 1.41 km²**、都市設備 **LOD3.0 0.08 km²**(渋谷駅・代々木駅周辺)、
  **地下街 LOD1 / LOD4.1 各 0.04 km²**(渋谷駅周辺地下街)。

**テクスチャは CityGML にも同梱されている** 🔬 —
`udx/bldg/<meshcode>_bldg_6697_appearance/` に JPEG が入る。シム bbox の4タイル実測:

| タイル | appearance サイズ | ファイル数 |
|---|---:|---:|
| 53393585 | 27 MB | 2,611 |
| 53393586 | 26 MB | 2,079 |
| 53393595 | 30 MB | 2,493 |
| 53393596 | 36 MB | 2,634 |
| **計** | **119 MB** | **9,817** |

JPEG 1枚あたり: 中央値 3 KB / 平均 11 KB / 最大 736 KB。
寸法は 64×64・128×128・256×256 が中心で**最大 512×512**。🔬
→ **1枚ずつは小さいが枚数が致命的**(9,817マテリアル = 描画コール爆発)。**アトラス化が必須**。

### 2.2 PLATEAU 3D Tiles 版(手元 zip・**最重要の未使用資産**)🔬

zip 内 9,666 エントリ・`.b3dm` 2,524 / `.mvt` 6,420 / `.glb` 115 / `.json` 27。
タイルセット別の**非圧縮サイズ**と、**シム bbox `[35.65260,139.68931]–[35.66645,139.71002]` と
交差するタイルだけを合計した値**(`tileset.json` の `boundingVolume.region` 判定):

| タイルセット | 全域 raw | 全域 タイル数 | **bbox 内 raw** | bbox 内タイル数 |
|---|---:|---:|---:|---:|
| `bldg_3dtiles_..._lod2`(**テクスチャ付き**) | 449.1 MB | 730 | **180.9 MB** | 148 |
| `bldg_3dtiles_..._lod2_no_texture` | 338.7 MB | 730 | 86.3 MB | 148 |
| `bldg_3dtiles_..._lod1` | 278.3 MB | 217 | 50.5 MB | 48 |
| **`tran_3dtiles_lod3`**(道路 LOD3) | 23.8 MB | 97 | **11.8 MB** | 51 |
| **`ubld_3dtiles_lod4`**(地下街 LOD4) | 15.7 MB | 122 | **15.7 MB**(全部) | 122 |
| `frn_3dtiles_lod3`(都市設備) | 23.6 MB | 222 | 14.4 MB | 141 |
| `brid_3dtiles_lod2` | 21.1 MB | 116(`.glb`) | — | — |
| `luse_mvt`(土地利用) | 2,672 MB | 1,297 | — | 本用途では不要 |

> 注: bbox 判定は「タイルの bounding region が bbox と交差するか」なので、境界タイルは丸ごと算入される
> = **やや過大**。実際に必要な範囲はこれより小さい。

**b3dm の中身**(`bldg lod2` の最大タイルを実測)🔬:

```
glTF 2.0 / generator = "FME 2024.1.3.0"
extensionsUsed = ["CESIUM_RTC", "EXT_texture_webp", "KHR_draco_mesh_compression"]
1タイル = images 1(image/webp)/ materials 2 / meshes 1 / primitives 2
batchTable = meshcode, feature_type, city_code, city_name, gml_id, attributes,
             gml:name, core:creationDate, bldg:class, bldg:usage, bldg:measuredHeight,
             bldg:storeysAboveGround, bldg:storeysBelowGround, bldg:address,
             uro:BuildingIDAttribute_uro:buildingID, uro:BuildingDetailAttribute_* …
```

含意が3つある:

1. **テクスチャはすでに 1タイル = 1枚の WebP アトラスに統合されている**。
   CityGML 側の 9,817枚バラ JPEG を自前でアトラス化する工程が**丸ごと不要**になる。
   全 730タイルの WebP 合計 = **94.7 MB(b3dm 総量の 21%)**、
   うち bbox 内テクスチャ分 ≈ 180.9 − 86.3 = **94.6 MB**
   → **テクスチャ付きタイルはほぼ全部シム bbox 内に落ちている**
   (LOD2.2 の整備範囲=都市再生緊急整備地域=渋谷駅周辺 と bbox が一致するため)。
2. **`KHR_draco_mesh_compression` がかかっている** → ブラウザで直読みするには Draco デコーダが要る(§4.2 で不可)。
   ただし **Python 側でオフラインにデコードして自前コーデックへ焼き直す**なら何の問題もない。
3. **`batchTable` の属性が POI 照合の副産物になる**。
   `gml_id` に加え `bldg:usage`・`bldg:class`・`storeysAboveGround/BelowGround`・`address` が付いており、
   現行 `match_plateau.py`(重心 kNN + footprint IoU)の**用途一致による補強**に使える。

### 2.3 地下街 LOD4.1 の中身(実測)🔬 — 物理シムの本命

`udx/ubld/53393596_ubld_6697_op.gml`(34,004,254 B・**この1ファイルのみ**):

```
gml:name           = 渋谷駅周辺エリア
UndergroundBuilding = 1
Envelope (EPSG:6697) = 35.65835012 139.69851499 0.9042  –  35.66133443 139.70304957 17.9742
                     ≈ 南北 332 m × 東西 410 m、標高 T.P. 0.90–17.97 m
                       (交差点地表 ground0 = 15.18 なので 地表基準で −14.3 m 〜 +2.8 m)
```

| 地物 | 個数 | 物理シムでの用途 |
|---|---:|---|
| `bldg:Room` | 3 | 空間の区画(フロア/エリア) |
| **`bldg:InteriorWallSurface`** | **1,934** | **`f_iW` 対壁斥力の壁セグメント** |
| `bldg:WallSurface` | 1,860 | 外殻(地下構造体の外壁) |
| **`bldg:FloorSurface`** | **145** | **歩行可能面ポリゴン** |
| `bldg:CeilingSurface` | 255 | 高さ拘束・描画 |
| **`bldg:Door`** | **188** | **ゲート/出入口(SignalGate と同型の通過制御)** |
| `bldg:ClosureSurface` | 218 | 仮想的な閉鎖面 = **開口部の境界**(接続グラフに使える) |
| `bldg:Window` | 23 | 描画のみ |
| `bldg:RoofSurface` / `GroundSurface` | 275 / 214 | 上下端 |
| **`bldg:IntBuildingInstallation`** | **5** | **階段・スロープ = 階層接続** |
| `lod4MultiSurface` / `lod4Solid` / `lod4Geometry` | 4,980 / 4 / 5 | ジオメトリ本体 |

これは PLATEAU 標準製品仕様書の 地下街モデル(LOD4)定義
(<https://www.mlit.go.jp/plateaudocument/toc4/toc4_16/toc4_16_01/toc4_16_01_05/>)
の必須地物(Room ● / CeilingSurface ● / InteriorWallSurface ● / FloorSurface ● /
ClosureSurface ● / Window ● / Door ●、階段・スロープ ◎条件付必須、家具 ○任意)と一致する。

**現行パイプラインはこれを LOD1 でしか読んでいない**
(`extras.json` の `counts = {lod1:1, lod2:0}`)= 地下街が「箱1個」になっている。

### 2.4 道路 LOD3.0(`udx/tran`)

すでに [`plateau-2025-update-notes.md`](plateau-2025-update-notes.md) §4 で実査済み。要点のみ再掲:
シム bbox の4タイルに `lod3MultiSurface` 5,782面 / `TrafficArea` 8,106 / `AuxiliaryTrafficArea` 238。
`TrafficArea_function` コードで **2000=歩道部・2010=自転車歩行者道・2020=歩道・2030=自転車道**、
車道側は 1000=車線・1010=車道交差部。`AuxiliaryTrafficArea` は 3000=島・3010=交通島・3020=分離帯。
→ **歩道の実ポリゴン(面)が取れる**。現行は OSM の折れ線(幅なし)しかない。

**未解決(前回から継続)**: LOD3.0 の被覆は 1.41 km² でシム bbox 2.9 km² の**約半分**。
被覆マップを先に作り、被覆外は OSM 線分にフォールバックする二層設計が要る。
`13113_indexmap_op.pdf` と `metadata/udx_13113_pref_2025_op.xml` で範囲確定できる。

### 2.5 3dcel(3D City Experience Lab.)— **PLATEAU 以外で唯一 再配布可の高精細渋谷**

<https://3dcel.com/opendata/> (Presented by Rhizomatiks / WIRED、経済産業省協力)

| データ | 範囲 | 形式 | サイズ | 取得 | ライセンス |
|---|---|---|---:|---|---|
| 渋谷駅周辺 | **750 m × 750 m** | **テクスチャ付き OBJ+MTL+JPG** | 3 MB(S) / 42 MB(M) / **539 MB(L)** | 2014年10月・地上分解能 **7 cm** | **CC BY 4.0**(権利者 = 株式会社パスコ) |
| 渋谷駅地下 | 350 m × 400 m | PTS 点群 | 437 MB | 2017年3月・点間隔 10 cm | **CC BY 4.0**(権利者 = 3D City Experience Lab.) |

- **PLATEAU LOD2.2(建物単位の面+テクスチャ)より写実的**(航空写真からの実測メッシュ = 樹木・車・看板まで入る)。
- **CC BY 4.0 なので GitHub 公開リポジトリへの同梱再配布が可能**(出典表示のみ)。
- **弱点**: (a) 2014年取得 = **渋谷スクランブルスクエア(2019)・渋谷フクラス(2019)・宮下パーク(2020)が存在しない**。
  本プロジェクトの「2026年の渋谷のスナップショット」という DT 定義([`dt-snapshot-definition`](../../STATUS.md))と**大きく食い違う**。
  (b) 建物単位に分かれていない一枚岩メッシュなので、`plateau_match.json` のような**建物 ID 照合ができない** =
  シムの POI/建物クリックと結線できない。(c) 座標系情報がタイル名依存で、局所メートル系への合わせ込みに実測が要る。
- **前例あり**: [ShibuyaCrowd (mattatz, 2017)](https://github.com/mattatz/ShibuyaCrowd) =
  three.js + WebGL の渋谷群衆デモが**まさにこの 3dcel データ**を使っている(データはリポに同梱せず別途 DL する方式)。
  Google の Experiments に掲載: <https://experiments.withgoogle.com/shibuyacrowd>

### 2.6 Google Photorealistic 3D Tiles — **本プロジェクトでは採用不可**

- 精細度は最高(航空写真フォトグラメトリ・世界中の都市)。しかし **Map Tiles API Policies** が明示的に禁じている:
  - 「you must not **pre-fetch, index, store, or cache** any Content except under the limited conditions stated in the terms」
  - 「You may not use Map Tiles API for any non-visualization use cases, such as:
    Image analysis, Machine interpretation, Object detection or identification,
    **Geodata extraction or resale**, **Offline uses**, including for any of the above」
  - Photorealistic 3D Tiles は「aggregate, sort, and display in a line, all attributions for displayed tiles」が必須。
  <https://developers.google.com/maps/documentation/tile/policies>
- **API キー + 課金必須**(無料枠なし)。root tileset リクエスト上限 10,000/日(2026年に 300→10,000 へ増枠)。
  <https://developers.google.com/maps/documentation/tile/3d-tiles>
- 結論: 「HTML に焼き込む」= 保存・キャッシュ・オフライン利用 = **規約違反**。
  「実行時に fetch する」= 外部 fetch 不可の自己完結制約と衝突 + 公開ミラーに API キーを置けない。
  **どちらの経路も塞がっている。検討対象から外す。**

### 2.7 Cesium OSM Buildings

- 3D Tiles として Cesium ion からストリーミング提供。**Asset Depot のアセットはダウンロード不可**
  (ion にアップロードした自前アセットのみ Archive 機能で DL 可)。<https://cesium.com/learn/unreal/unreal-faq/>
- 元データは OSM = **ODbL**(派生 DB の share-alike)。
- 精細度は **押し出しプリズム(LOD1 相当)** で、**本プロジェクトが現在 PLATEAU LOD2 で持っているものより粗い**。
- 結論: **採用理由なし**。

### 2.8 ゼンリン 3D 地図データ

- 国内 21都市対応。専用計測車両ベースで**現実の街を忠実に 3D モデル化**。
- **商用ライセンス**: 3D都市モデル 単価 **195,360円/単位(税込)**、
  年間契約オプション、**年額 500万円の使い放題(Sプラン)**。<https://www.zenrin.co.jp/product/category/gis/contents/3d/index.html>
- **再配布不可**(公開ミラーへの同梱は当然不可)。
- 結論: 予算・再配布の両面で不可。**検討対象外**。

### 2.9 東京都デジタルツイン実現プロジェクト 区部点群

- 航空レーザ測量による **16点/m² 以上**の高密度点群。1/500 図郭単位で LAS 等を ZIP で DL 可。
  <https://info.tokyo-digitaltwin.metro.tokyo.lg.jp/3dmodel/>
- **⚠ ライセンス未確認**: 東京都オープンデータカタログ(`catalog.data.metro.tokyo.lg.jp`)は本調査時に **HTTP 403** で取得できず、
  CC BY 4.0 かどうかを一次資料で確認できていない。採用前に要確認。
- 用途: **点群はビューア/SFM のどちらにも直接は使えない**(メッシュ化が必要)。
  地形 DEM はすでに `udx/dem` から取れているので**追加価値は薄い**。

### 2.10 その他(Sketchfab 等の個別モデル)

- [Shibuya Scramble Crossing, Tokyo](https://sketchfab.com/3d-models/shibuya-scramble-crossing-tokyo-3ad869e9b8b94651896eb9e323a7bdd7)
  (Teppei Utsunomiya / Skytone Co., Ltd)— 196.9k三角形 / 102k頂点、**CC BY-NC**。
  → **NC = 非商用限定**。研究用途でも「公開ミラーへの同梱」は NC 解釈のリスクがあり、
  ハッカソン/商用文脈が混じる本プロジェクトでは**避けるべき**。
- RenderHub 等の有償ローポリモデルは精細度・ライセンスとも本用途に不適。

---

## 3. 選択肢比較表

| 選択肢 | 精細度 | bbox 内容量 | ライセンス | GitHub 公開リポへの同梱再配布 | 統合工数 | 建物ID照合 | 2026年の街並み |
|---|---|---:|---|---|---|---|---|
| **PLATEAU CityGML LOD2(現行)** | 面(屋根/壁分離)・無地 | 18.9 MB(量子化後) | PDL1.0 / CC BY 4.0 選択可 | **可** | 済 | **可** | **○** |
| **PLATEAU 3D Tiles LOD2.2 テクスチャ付** | 面+写真テクスチャ | 180.9 MB(生)→ 推定 50–75 MB(再エンコード後) | 同上 | **可** | 中(2–3週) | **可**(batchTable) | **○** |
| **PLATEAU `tran` LOD3.0** | 歩車道の**面** | 11.8 MB(3DTiles)/ 41 MB(CityGML 4タイル) | 同上 | **可** | 中(3–5日) | — | **○** |
| **PLATEAU `ubld` LOD4.1** | **屋内 室/内壁/床/扉/階段** | 15.7 MB(3DTiles)/ 34 MB(CityGML) | 同上 | **可** | 小〜中(2–4日) | — | **○** |
| **PLATEAU `frn` LOD3.0** | 都市設備(標識・サイネージ) | 14.4 MB | 同上 | **可** | 小 | — | **○** |
| **3dcel 渋谷駅周辺 OBJ** | **写実メッシュ 7cm** | 42 MB(M)/ 539 MB(L) | **CC BY 4.0** | **可** | 中(座標合わせが要実測) | **不可**(一枚岩) | **× 2014年** |
| **3dcel 渋谷地下 点群** | 点群 10cm | 437 MB | **CC BY 4.0** | 可(容量的に非現実的) | 大(メッシュ化) | 不可 | × 2017年 |
| Google Photorealistic 3D Tiles | **最高** | — | Map Tiles API 規約 | **不可**(保存・オフライン・抽出 禁止) | — | — | ○ |
| Cesium OSM Buildings | LOD1 プリズム | — | ODbL / ion 経由のみ | **不可**(DL 不可) | — | — | △ |
| ゼンリン 3D 地図 | 高(車載計測) | — | 商用(195,360円/単位〜) | **不可** | — | ○ | ○ |
| 東京都 区部点群 | 16点/m² | — | **⚠未確認**(403) | 未確認 | 大 | 不可 | ○ |
| Sketchfab 個別モデル | 中(196.9k tri) | 小 | **CC BY-NC** | **不可相当**(NC) | 小 | 不可 | △ |

---

## 4. three.js への取り込みパイプライン

### 4.1 現行ビューアの実際の制約

`docs/plans/plateau-3d.md` の設計判断どおり、ビューアは **`file://` でダブルクリックして開く**ことが要件。
そこから来る制約を正確に切り分けると:

| 制約 | 実態 |
|---|---|
| `fetch()` / `XHR` で**ローカルファイル**を読む | **不可**(`file://` は CORS で全部 opaque) |
| `<script src="plateau_mesh.js">` で読む | **可** ← 現行の JSONP サイドカー方式 |
| `data:` URI を `<img>` / `THREE.Texture` に渡す | **可**(JPEG/PNG/**WebP** はブラウザネイティブデコード) |
| Blob URL から `new Worker()` | **不可**(`file://` は opaque origin) ← Draco/KTX2 が詰まる主因 |
| **base64 をデコードして `WebAssembly.instantiate(bytes)`** | **可**(fetch を経由しないため) |

つまり **「外部 wasm 不可」は正確には「外部ファイルの fetch と Blob Worker が不可」**であり、
**wasm バイト列を JS 内に埋め込んでしまえば wasm 自体は動く**。

### 4.2 圧縮方式の可否

| 方式 | `file://` 自己完結 | 判定 | 根拠 |
|---|---|---|---|
| **自前 int16 量子化(現行)** | **○** | **★推奨・継続** | 依存ゼロ。`plateau_web.json`(0.05 m 量子化)・`tracks_bin.py`(0.05 m + パレット)で実績。往復誤差厳密0を実測済み(第76バッチ) |
| **meshopt(`EXT_meshopt_compression`)** | **○** | 可(だが不要) | `meshopt_decoder.cjs` = **29,400 B**・**wasm を base64 でファイル内に内蔵**し `WebAssembly.instantiate` する(fetch なし)。`new Worker` は**任意の並列経路のみ**。MIT。three.js は r122+ で対応 = 手元 r128 で足りる |
| **Draco(`KHR_draco_mesh_compression`)** | **×** | **不可** | three.js `DRACOLoader` は `setDecoderPath` の**外部 fetch** + **Blob Worker** が前提。`mrdoob/draco.js`(pure JS)という代替はあるが未保守・低速 |
| **KTX2/Basis** | **×** | **不可** | `KTX2Loader` は `basis_transcoder.wasm` を**外部から読む**設計。インライン化の公式手段なし |
| **WebP テクスチャ + `data:` URI** | **○** | **★推奨** | ブラウザネイティブ。**PLATEAU 3D Tiles がすでに WebP アトラスを持っている**ので再エンコードすら省ける(縮小はしたい) |
| **JPEG + `data:` URI** | ○ | 可 | WebP より 25–35% 大きい |

**結論**: ランタイムに新しいデコーダを一切入れない。
**Draco は「Python 側でオフラインに解いて、既存の自前 int16 コーデックへ焼き直す」**。
これで三者(依存ゼロ・`file://` 自己完結・容量)を同時に満たせる。

### 4.3 変換ツール(ビルド時・Python/CLI 側)

| ツール | 用途 | ライセンス | 備考 |
|---|---|---|---|
| **`scripts/plateau_extract.py`(自前)** | CityGML → npz | 本リポ | **`SURFACE_TAGS` が建物半題面固定** = `tran`/`ubld` LOD4 には**新規抽出器が要る** |
| [PLATEAU GIS Converter](https://github.com/Project-PLATEAU/PLATEAU-GIS-Converter) | CityGML → 3D Tiles 1.1 / **glTF** / OBJ / MVT / GeoPackage | **MIT** | Rust 実装・GUI + **CLI**。`atlas-packer` でテクスチャアトラス生成。令和5年度 PLATEAU 成果 |
| [smtk_draco](https://github.com/Simumatik/smtk_draco) | Python から Draco decode | — | Blender の Draco ブリッジの Cython ラッパ(Python ≥3.8) |
| `draco_decoder` CLI | 同上 | Apache-2.0 | <https://github.com/google/draco> |
| [Auto-Create-bldg-lod2-tool](https://github.com/Project-PLATEAU/Auto-Create-bldg-lod2-tool) | LOD1→LOD2 自動生成 | PLATEAU | **本件では不要**(LOD2 は既に整備済み) |

> **b3dm → glTF は自前で足りる**: b3dm は 28 B ヘッダ + featureTable(JSON/BIN) + batchTable(JSON/BIN) + **生の GLB**。
> ヘッダ長を読んでオフセットを進めるだけで GLB が取り出せる(本調査で実証済み 🔬)。
> 残るのは `KHR_draco_mesh_compression` の解凍と `CESIUM_RTC` の原点オフセット適用のみ。

### 4.4 容量予算(松案の見積り)

| 内訳 | 生 | 施策 | 見積り |
|---|---:|---|---:|
| ジオメトリ(bbox 内 LOD2.2) | 86.3 MB(Draco 圧縮済 b3dm) | Draco 解凍 → **既存 int16×0.05 m コーデック** | **≈ 19 MB**(現行 `plateau_web.json` 実績と同等) |
| UV 座標(新規) | — | uint16 正規化 ×2 / 頂点 × 1.1M頂点 | **≈ 4.4 MB**(base64 で ≈ 5.9 MB) |
| テクスチャアトラス | 94.6 MB(WebP 148枚) | **1/2 解像度で再エンコード**(面積 1/4) | **≈ 24 MB** |
| 既存(tracks_bin・terrain・scene) | | 第76バッチ後 | ≈ 25 MB |
| **合計(埋め込み版)** | | | **≈ 74 MB** ← 80 MB ゲート**ぎりぎり内** |

**リスク**: base64 は 4/3 に膨らむ。上表の「合計」は膨張後で見ているが余裕がない。
→ **分離版(`viewer3d_lite.html` + サイドカー)を主経路に据える**のが安全。
1/4 解像度なら テクスチャ ≈ 6 MB まで落ちるので、**縮退順 = 1/2 → 1/4 → LOD2.2 のみテクスチャ**を先に決めておく。

---

## 5. 物理シムとの接合

### 5.1 `ubld` LOD4.1 → SFM 対壁斥力 `f_iW`(**最も費用対効果が高い**)

`sfm_core.py` に現在ないのは Helbing の壁項:

```
f_iW = A · exp((r_i − d_iW)/B) · n_iW      (n_iW = 壁から歩行者へ向かう法線)
```

入力に必要なのは **「壁の線分集合」と「歩行可能面」**。LOD4.1 からの写像は素直:

| CityGML 地物 | 実測数 | → シム側 |
|---|---:|---|
| `InteriorWallSurface` | 1,934 | **鉛直面を水平投影 → 2D 線分**(SFM の壁セグメント) |
| `FloorSurface` | 145 | **歩行可能ポリゴン**(フロア別・z でグルーピング) |
| `Door` | 188 | **ゲート**(既存 `SignalGate` と同型の通過制御に接続可能) |
| `ClosureSurface` | 218 | **開口部の境界** = フロア間/エリア間の接続グラフ辺 |
| `IntBuildingInstallation` | 5 | **階段・スロープ** = 高低差のある移動コスト |
| `Room` | 3 | エリア区画(L2 指標の集計単位に使える) |

**注意点(honest)**:
- 屋内は **多層**(T.P. 0.90〜17.97 m の範囲に床が重なる)。SFM は 2D なので**フロア分離が前提**。
  `FloorSurface` の z 分布でクラスタリングして層を切る前処理が要る。
- `InteriorWallSurface` は面であって「厚みのある壁」ではない。**両面が別ポリゴンで来る可能性**があり、
  線分に落とすと二重になる。重複除去が要る。
- 範囲は **332 m × 410 m の渋谷駅周辺地下街のみ**。bbox 全体(2.9 km²)の屋内は**存在しない**。
  屋内 SFM を回せるのはこの一角だけ = **「屋内 SFM = 地下街ユースケース」と明示的に限定する**べき。

### 5.2 `tran` LOD3.0 → 歩行可能面(前回調査から継続)

- **B-L2(屋外 SFM)**: `Crowd` に渡す「歩ける面」の実形状。現行は `crossings_shibuya.json` + OSM 線分のみ。
- **A1 `world.mod.歩道幅係数`**: 歩道ポリゴンから**実幅**を算出でき、係数の**原点(実測 1.0)**が定義できる。
- **H_B(時空間プリズム)**: 到達可能領域が「線」から「面」になり PPA の面積計算が実測ベースに。
- **C0(可視行列)**: 視点グリッドを「歩行可能面 2 m 格子」で切る要件を実ポリゴンで満たせる。
- **被覆の穴**(§2.4)への二層フォールバックが必須。

### 5.3 `frn` LOD3.0 → サイネージ実位置

`udx/frn` は渋谷駅・代々木駅周辺 0.08 km² のみだが、シム 4 タイルのうち 53393586(14.6 MB)と
53393596(53.3 MB)の 2 枚が該当 🔬。C0(可視行列)の**実サイネージ位置**の一次候補。中身は未確認のまま。

### 5.4 建物 footprint の精密化

現行 `plateau_match.json` は matches 3,531 / unmatched_osm 3,679 / unmatched_plateau 2,780 =
**照合率が約 49%** にとどまる。3D Tiles の `batchTable` にある `bldg:usage` / `bldg:class` /
`bldg:address` / `storeysAboveGround` を照合の第2キーに加えれば改善余地がある(要検証)。

---

## 6. ライセンス — GitHub 公開リポジトリへの同梱再配布の可否

| データ | 規約 | 同梱再配布 | 条件 |
|---|---|---|---|
| **PLATEAU(CityGML / 3D Tiles とも)** | [PLATEAU サイトポリシー §3](https://www.mlit.go.jp/plateau/site-policy/): 政府標準利用規約(PDL1.0)を基本とし、**CC BY 4.0 での利用を許諾**、ODC BY / ODbL も妨げない | **可**(商用含む) | ①出典表示 ②**加工した旨の記載** ③「国が作成したかのような態様」での公表禁止 |
| **3dcel 渋谷 OBJ / 地下点群** | **CC BY 4.0** | **可** | 出典表示。OBJ の権利者は **株式会社パスコ**、点群は **3D City Experience Lab.** |
| **地理院タイル** | [国土地理院コンテンツ利用規約](https://www.gsi.go.jp/kikakuchousei/kikakuchousei40182.html) | **可**(申請不要) | 出典「国土地理院」または「地理院タイル」。加工した旨の記載必要。基本測量成果は測量法上の別扱いあり |
| **Google Photorealistic 3D Tiles** | [Map Tiles API Policies](https://developers.google.com/maps/documentation/tile/policies) | **不可** | pre-fetch / cache / store 禁止、offline uses 禁止、geodata extraction 禁止 |
| **Cesium OSM Buildings** | ion Asset Depot(DL 不可)/ 元データ ODbL | **不可** | — |
| **ゼンリン 3D 地図** | 商用ライセンス | **不可** | — |
| **Sketchfab(該当モデル)** | **CC BY-NC** | **不可相当** | 非商用限定 |
| **東京都 区部点群** | **⚠ 未確認**(403) | 未確認 | 採用前に一次資料の確認が必要 |

**現行の帰属表記** `scripts/export_3d.py:159 PLATEAU_ATTRIBUTION`
=「…3D都市モデル(Project PLATEAU)渋谷区(2025年度)を加工」は上記①②を満たしている。
3dcel を採用する場合は**別の帰属表記の追加が必要**(権利者がパスコ/3dcel で国交省ではない)。

---

## 7. 推奨案(松・竹・梅)

### 梅 — 地下街を「箱」から「部屋」へ(0.5〜1日 / +2〜4 MB)

**やること**: 既存の `--extras` 経路(現在 `ubld` を **LOD1 でしか読んでいない**)を LOD4.1 に拡張。

1. `plateau_extract.py --extras` の ubld 読み取りを `lod4MultiSurface` 対応にする
   (`SURFACE_TAGS` に `InteriorWallSurface` / `FloorSurface` / `CeilingSurface` / `Door` / `ClosureSurface` を追加)。
2. `plateau_web.json` の `extras` に **面種別のタグ**を持たせる(現行は種別なし)。
3. `make_viewer3d.py` の `_EXTRAS_BUILD` で床=不透明・内壁=半透明・扉=強調色に塗り分け。
4. 既定(`--plateau` なし)出力の**バイト同一**を確認。

**得るもの**: 「地下街の中で人が動いているのが見える」。物理シムは未変更。
**リスク**: 低。既存の extras 契約に**追加専用**で乗る。

### 竹 — 物理シムへの幾何供給(3〜5日 / +10〜20 MB)★ **推奨**

梅に加えて:

1. **新規抽出器 `scripts/plateau_tran_extract.py`**
   `udx/tran` の `lod3MultiSurface` を読み、`TrafficArea_function` コード(2000/2010/2020/2030 = 歩行系、
   1000/1010 = 車道系)で分類して **歩行可能面ポリゴン**を出力。
   座標系は `bldg` と同じ EPSG:6697 なので**局所接平面変換をそのまま流用**できる。
   同時に **LOD3 被覆マップ**(どのエリアが LOD3 被覆内か)を出力する ← 二層フォールバックの前提。
2. **`ubld` LOD4.1 → 壁線分 + フロア面**
   `InteriorWallSurface` 1,934 面を鉛直判定 → 水平投影 → **2D 線分**(重複除去つき)。
   `FloorSurface` 145 面を z クラスタリングで**層に分離**。`Door` 188 をゲート点に。
3. **`sfm_core.Crowd` に対壁斥力 `f_iW` を追加**(既定 OFF)
   docstring の「意図的に省略」節を**設計変更として正直に書き換える**。
   壁セグメントへの最近点距離を空間ハッシュで引く(全ペアは不可)。
   **既定 OFF = 既存ゴールデン無風**を検収条件にする。
4. `world.mod.歩道幅係数` の**原点(実測 1.0)を歩道ポリゴン実幅から定義**。

**得るもの**: 「人が壁を突き抜けない」「歩道の上を歩く」= DT としての最低限の物理妥当性。
研究目標(k\* データ)への寄与が最も大きい。
**リスク**: 中。`sfm_core` はシム本体なので**既定 OFF + 決定論の維持**が必須。
LOD3 被覆の境目で歩行モデルが不連続になる問題は設計で吸収する必要がある。

### 松 — テクスチャ付き写実 LOD2.2(2〜3週 / 埋め込み版 ≈ 74 MB・分離版推奨)

竹に加えて:

1. **手元 zip から bbox 内 148 タイルを取り出す**(展開不要・`zipfile` で直読み)。
2. **b3dm ヘッダを剥がして GLB を取り出す**(28 B + featureTable + batchTable のオフセット計算のみ・実証済み 🔬)。
3. **`KHR_draco_mesh_compression` を Python 側でデコード**(`smtk_draco` または `draco_decoder` CLI)。
   **`CESIUM_RTC` の原点オフセット**を適用して局所メートル系へ。
4. **既存の int16×0.05 m コーデックへ再エンコード** + **UV を uint16 で追加**。
   → `plateau_web.json` の契約に**追加専用**で乗せる(`uv` キーと `atlas_index` を追加)。
5. **WebP アトラス 148 枚を 1/2 解像度で再エンコード**(Pillow・WebP は標準対応)し **`data:` URI で埋め込む**。
   ブラウザネイティブデコード = **ランタイム依存ゼロ**。three.js は r128 のままでよい。
6. `make_viewer3d.py` に **`THREE.MeshLambertMaterial({map})` のアトラス別マテリアル**(148個)を追加。
   1タイル = 1ドローコール = **148ドローコール** ← 現実的。
7. **副産物**: `batchTable` の `gml_id` / `bldg:usage` / `storeysAboveGround` を
   `plateau_match.json` の第2キーに使い、照合率 49% の改善を試す。
8. **縮退順を先に決める**: テクスチャ 1/2 → 1/4 → LOD2.2 のみテクスチャ → テクスチャ全廃。
   埋め込み版が 80 MB を超えたら**分離版を正式な主経路に格上げ**する。

**得るもの**: 本選デモの見栄え。**研究データへの寄与はゼロ**。
**リスク**: 高。容量ゲートが厳しく、Draco デコードに**新規 Python 依存**が入る
(現行 `plateau_extract.py` は stdlib + numpy のみという設計原則を破る)。
→ **緩和策**: Draco デコードは**ビルド時の一度きり**なので、
`scripts/` の外(`tools/` など)に隔離し、成果物(再エンコード済み npz)だけをリポに置けば
本線パイプラインの依存は増えない。

### 採らない案

- **3dcel 写実メッシュ**: CC BY 4.0 で再配布可・7 cm と魅力的だが、**2014年取得**で
  スクランブルスクエア/フクラス/宮下パークが無く、**DT のスナップショット定義と矛盾する**。
  建物 ID 照合もできない。「渋谷らしさの絵作り」だけが目的なら候補に戻せる。
- **Google / Cesium / ゼンリン**: ライセンス上、公開ミラーへの同梱が不可能。
- **Draco / KTX2 のランタイム導入**: `file://` 制約で不可(§4.2)。

---

## 8. 未確認・要検証(honest)

1. **東京都区部点群のライセンス** — カタログが 403 で一次確認できず。
2. **LOD3.0 の被覆マップ** — `13113_indexmap_op.pdf` / `metadata/udx_13113_pref_2025_op.xml` 未読。
   bbox 2.9 km² に対し LOD3 は 1.41 km² = **約半分しかない**という前提のまま。
3. **`udx/frn` の中身** — サイズ(14.6/53.3 MB)だけ見て地物の内訳は未確認。
4. **3dcel の実ダウンロード** — `/opendata/` は生存確認したが、個別 DL リンク(`/opendata/shibuya/` は 404)と
   実ファイルの座標系は未検証。
5. **Draco デコードの Python 実測** — `smtk_draco` の導入可否・速度は未検証。
   148 タイルの解凍時間が非現実的でないかは要実測。
6. **ブラウザ実機検証** — 148 マテリアル + 24 MB テクスチャでの実 fps は未測定。
   第76・77バッチと同様、本書も**機械検査までで実機未検証**。
7. **`InteriorWallSurface` の両面重複** — 1,934 面が実際に何本の一意な壁線分になるかは未計測。

---

## 9. 出典 URL 一覧

### PLATEAU
- 渋谷区(2025年度)データセット — <https://www.geospatial.jp/ckan/dataset/plateau-13113-shibuya-ku-2025>
- PLATEAU サイトポリシー(著作権/ライセンス) — <https://www.mlit.go.jp/plateau/site-policy/>
- Open Data ポータル — <https://www.mlit.go.jp/plateau/open-data/>
- G空間情報センター PLATEAU ポータル — <https://front.geospatial.jp/plateau_portal_site/>
- 地下街モデル(LOD4)の概要(標準製品仕様書) — <https://www.mlit.go.jp/plateaudocument/toc4/toc4_16/toc4_16_01/toc4_16_01_05/>
- 建築物モデル(LOD4)の概要 — <https://www.mlit.go.jp/plateaudocument/toc4/toc4_02/toc4_02_01/toc4_02_01_05/>
- LOD レベルによる表現の違い — <https://www.mlit.go.jp/plateau/learning/tpc03-3/>
- ユースケース uc24-13 地下街データを活用したナビゲーションシステム v2.0(渋谷/札幌/高松) — <https://www.mlit.go.jp/plateau/use-case/uc24-13/>
- 東京都23区 ポートシティ竹芝 建築物モデル(LOD4)(2022年度) — <https://www.geospatial.jp/ckan/dataset/plateau-tokyo23ku-2023-lod4>

### 変換ツール
- PLATEAU-GIS-Converter(MIT・CityGML → 3D Tiles/glTF/OBJ/MVT) — <https://github.com/Project-PLATEAU/PLATEAU-GIS-Converter>
- 同 マニュアル — <https://mierune.github.io/plateau-gis-converter/index.html>
- PLATEAU-IFC-to-CityGML2.0-LOD4 — <https://github.com/Project-PLATEAU/PLATEAU-IFC-to-CityGML2.0-LOD4>
- Auto-Create-bldg-lod2-tool — <https://github.com/Project-PLATEAU/Auto-Create-bldg-lod2-tool>
- Auto-Create-tran-lod1-2-tool — <https://github.com/Project-PLATEAU/Auto-Create-tran-lod1-2-tool>
- plateau-streaming-tutorial(3D Tiles 仕様) — <https://github.com/Project-PLATEAU/plateau-streaming-tutorial/blob/main/3d-tiles/specification.md>
- google/draco — <https://github.com/google/draco>
- smtk_draco(Python バインディング) — <https://github.com/Simumatik/smtk_draco>
- meshoptimizer / gltfpack — <https://github.com/zeux/meshoptimizer/blob/master/gltf/README.md> / <https://meshoptimizer.org/gltf/>
- three.js GLTFLoader `EXT_meshopt_compression` 対応 PR(r122+) — <https://github.com/mrdoob/three.js/pull/20508>
- three.js DRACOLoader ドキュメント — <https://threejs.org/docs/pages/DRACOLoader.html>
- three.js KTX2Loader ドキュメント — <https://threejs.org/docs/pages/KTX2Loader.html>
- mrdoob/draco.js(pure JS Draco ローダ) — <https://github.com/mrdoob/draco.js>

### PLATEAU 以外のデータ
- 3D City Experience Lab. オープンデータ(渋谷 750m OBJ / 地下点群・CC BY 4.0) — <https://3dcel.com/opendata/>
- 同 Study#1(ShibuyaCrowd が参照) — <https://3dcel.com/study/case01/>
- 東京都デジタルツイン実現プロジェクト 3Dモデル — <https://info.tokyo-digitaltwin.metro.tokyo.lg.jp/3dmodel/>
- 東京都オープンデータカタログ 区部点群データ(**本調査時 403**) — <https://catalog.data.metro.tokyo.lg.jp/dataset/t000029d0000000024>
- 国土地理院コンテンツ利用規約 — <https://www.gsi.go.jp/kikakuchousei/kikakuchousei40182.html>
- 地理院地図 利用規約 — <https://maps.gsi.go.jp/help/termsofuse.html>
- 地理院タイル一覧 — <https://maps.gsi.go.jp/development/ichiran.html>

### 商用・不採用
- Google Map Tiles API Policies(**保存/オフライン/抽出 禁止**) — <https://developers.google.com/maps/documentation/tile/policies>
- Google Photorealistic 3D Tiles — <https://developers.google.com/maps/documentation/tile/3d-tiles>
- Map Tiles API Usage and Billing — <https://developers.google.com/maps/documentation/tile/usage-and-billing>
- Cesium OSM Buildings — <https://cesium.com/platform/cesium-ion/content/cesium-osm-buildings/>
- Cesium Unreal FAQ(Asset Depot は DL 不可) — <https://cesium.com/learn/unreal/unreal-faq/>
- ゼンリン 3D 地図データ — <https://www.zenrin.co.jp/product/category/gis/contents/3d/index.html>
- ゼンリン 3D地図データオンライン提供サービス 料金プラン — <https://www.zenrin.co.jp/product/category/pdf/3d_3dsolution_priceplan.pdf>
- Sketchfab: Shibuya Scramble Crossing(**CC BY-NC**) — <https://sketchfab.com/3d-models/shibuya-scramble-crossing-tokyo-3ad869e9b8b94651896eb9e323a7bdd7>

### 先行事例・論文
- ShibuyaCrowd(mattatz・three.js + 3dcel データ) — <https://github.com/mattatz/ShibuyaCrowd> / <https://experiments.withgoogle.com/shibuyacrowd>
- ShibuyaSocial: Multi-scale Model of Pedestrian Flows in Scramble Crossing — <https://www.themoonlight.io/en/review/shibuyasocial-multi-scale-model-of-pedestrian-flows-in-scramble-crossing>
- PLATEAU Journal j016-1(渋谷区でのデジタルツイン合意形成事例) — <https://www.mlit.go.jp/plateau/journal/j016-1/>
- デジタルツイン渋谷プロジェクト — <https://digital-shift.jp/flash_news/FN211110_3>
