# PLATEAU実形状化 計画(第36バッチ 2026-07-18)— UEガイド統合 + Webビューア実形状(D6-web)

ユーザー依頼: ①UE5経由で実験データを載せる方法の「まとめ」 ②現行Webビューア(viewer3d.html)も
PLATEAU実形状の渋谷にしたい。まず計画。体制 = Fable計画・検収 / Opus実行。

## 手元資産の実査(2026-07-18確認済み)

| 資産 | 状態 |
|---|---|
| CityGML 渋谷区2025 | **展開済み** `Desktop/13113_shibuya-ku_pref_2025_citygml_1_op/`(udx/bldg=29タイル・dem・tran他) |
| シミュ圏の建物タイル | 53393585(88.9MB)/86(77.7)/95(82.9)/96(97.6)= 中心1km圏をカバー(4タイル~347MB) |
| 3D Tiles版 | zip未展開(637MB)。今回は不使用(下記「不採用」参照) |
| PLATEAU SDK for Unreal v3.2.2 | zip未展開(1GB)。**手元UEは5.5系=対応一致** |
| 既存UE納品物 | viz/unreal/README_UE.md(手順書・実機未検証)・import_shibuya_sim.py・SimReplayActor_DESIGN.md・scripts/export_ue.py |
| 現行ビューア | make_viewer3d.py=scene.json footprintのExtrudeGeometry描画。**glb読込なし→メッシュ描画の追加が必要** |

## 成果物A: UE5実験データ搭載ガイド(ドキュメント・半日)

README_UE.mdは網羅的だが「初見で迷わない一本道」でない。**この環境の実パス・実バージョンを
埋め込んだクイックスタート** `docs/guides/ue5-quickstart.md` を新規作成:

1. SDK zip → プロジェクト`Plugins/`へ(手元UE 5.5・v3.2.2の組で確定記述)
2. PLATEAUインポート(ローカル=展開済みフォルダ・第9系・オフセット=スクランブル交差点の
   平面直角座標 E=-12015.952/N=-37768.576・建物LOD2/道路LOD1)
3. シミュ側1コマンド: `export_3d.py` → `export_ue.py`(→ sim_ue.json=UE cm座標)
4. **主経路=mode="sequence"**(≤300体・1体=1アクタ+Level Sequenceベイク)。
   **200体の現ランはBP/C++を一切書かずに再生ボタンだけで動く**のが決め手。
   ISM+SimReplayActor(BP実装が必要)は大規模用の付録に降格。
5. 初回の向き合わせ(heading×y_flipの8通り・ハチ公/渋谷駅ランドマーク法)・高さ合わせ・
   トラブルシュート(README_UE §8を継承)

## 成果物B: Webビューア実形状化(コード・W1-W5)

方針: **CityGML→自前抽出→scene3d契約の中で差し替え**。シミュ本体は無風(viz下流のみ)・
新規依存ゼロ(stdlib ElementTree iterparse + numpy)・PLATEAU大容量データはrepo外/gitignore圏に保持。

- **W1 抽出** `scripts/plateau_extract.py`: bldg 4タイルからLOD2(2.0優先)ポリゴン読取→
  緯度経度→local-m(局所接平面・原点=スクランブル)→高さ=T.P.−交差点標高(**udx/demから実測**・
  取れなければ定数+正直な縮退宣言)→ `scene3d/plateau_mesh.npz + plateau_index.json`
  (gml_id・LOD0 footprint・三角形群)。シミュ地図bbox+バッファでクリップ。
- **W2 照合** `scripts/match_plateau.py`: 重心k-NN(≤25m)→footprint IoU≥0.4→
  `plateau_match.json`(b<id>→gml_id・IoU付き)。未マッチ率・競合解決をレポート出力。
- **W3 exporter** `export_3d.py --plateau`: マッチ建物=実形状メッシュ・未マッチ=従来押出しの
  ハイブリッドでbuildings.glb生成+scene.jsonのheightをLOD2実測で上書き(**契約キー不変・追加専用**)。
- **W4 ビューア** `make_viewer3d.py`: scene3dにplateau_meshがあればBufferGeometry直描画
  (GLTFLoader不要・base64+int16量子化埋込み)。建物クリック名はmatch表経由で維持。
  **サイズゲート**: viewer3d.html目標≤80MB。超過時の縮退順=LOD2.2→2.0→簡略化→bbox縮小
  (縮退したら明記)。
- **W5 検収(Fable)**: demo_event_200a3dで export_3d --plateau → viewer3d 一気通し。
  ブラウザ起動・マッチ率・サイズ・体感fps・スクランブル周辺の目視(109・駅・ハチ公前の形状)を記録。
  既定(--plateauなし)は従来出力とバイト同一が合格条件。

体制: A=Opus(独立doc)/ W1・W2=Opus並列(新規独立ファイル)/ W3・W4=直列1バッチ(既存ファイル編集)/
W5=Fable。合計目安2日。

## 不採用の選択肢(理由の記録)

- **3D Tiles + 3DTilesRendererJS**: ライブラリvendor+file://でのタイルfetch不可=ローカルサーバ必須
  となり「ブラウザで開くだけ」の自己完結性を失う。棄却。
- **テクスチャ取込み**: サイズ爆発(数百MB)・写実はUE経路の担当。Webは単色+陰影+昼夜光。
- **全渋谷区の実形状**: シミュはbbox外に世界を持たない。bbox+バッファのみ実形状、圏外は現行の遠景箱。

## ユーザー決定(2026-07-18)

1. ビューア形式: **両方作る** — ①自己完結HTML(≤80MBゲート) ②分離版=軽量HTML+`plateau_mesh.js`
   サイドカー(`<script src>`読込はfile://でも動く=サーバ不要のまま2ファイル構成。fetch不可の
   制約をJSONP方式で回避)
2. 実形状の範囲: シミュbbox+150mバッファのみ(圏外は現行の遠景箱)
3. 着工順: AとB並行(Opus 3体=A・W1・W2同時起動)

## 追記: 3D品質修正バッチ(2026-08-02・観察レイヤのみ / src・conf 無変更)

W1〜W5 の実装後に残っていた「地面の乱れ」「エージェント筒の浮遊」を潰した。対象は
`viz/make_viewer3d.py` / `scripts/export_3d.py` / `scripts/plateau_extract.py` の3本だけ。

### 地形・地面
- **OSMドレープを地形サーフェスと同一 geometry へ**(平面UV投影)。旧実装は別平面を
  `min(240, …)` セグメントで作っており、実効間隔 14.5m ≫ 地形格子 2m のため
  **面積の 33.6%(最大 9.5m)が不透明な地形の下に潜って**地図が溶けていた。頂点を共有すれば
  交差は構造的に起こり得ない(残る同一平面の z-fight は polygonOffset + depthWrite:false で決着)。
  タイル合成キャンバスの外周に1pxの透明枠を置き、地図矩形の外(uv∉[0,1])は素の地形色にする。
- **地形ラスタ化を TIN の重心座標(barycentric)補間へ**(`plateau_extract.py`)。
  DEM の `gml:Triangle` を**三角形のまま**読む `collect_tin_triangles` を新設し、
  格子点は含有三角形の面上値で決める。旧 IDW(最近傍3頂点の距離加重)は面を無視するため、
  独立に評価した TIN 真値と比べて **最大 1.54m・10.9%のセルが >0.1m** ずれていた
  (新実装は最大 1e-6m = float32 保存の丸めのみ)。TIN 凸包外の 2,481セル(0.25%)だけ
  最近傍で埋め、その件数を `terrain.json` に明記する。
- **地上線路**は `groundAt+z+0.6`(旧: 絶対 0.6m で 717頂点中 310が地形に埋没・最大 20.4m)。
- **道路**は地形セル幅(2m)以下に再分割してから接地(頂点 20,376 → 196,890)。
- **建物**は `depth=(levels+below)*3.5` で押出し(地下階持ちの屋上沈み是正)+下方3mスカート。
  `gz` は重心1点ではなく footprint 頂点の**最小**地表高。
- **地下街(ubld)**は既定 OFF + 地表クリップ(3頂点とも地表より上の三角形 1,052/6,256 を除去)。
  歩道橋(brid)は地上構造物なのでクリップしない。地形注入時は GridHelper を常時非表示。

### エージェント
- **足元アンカー**へ統一(旧: 全高10.2mの筒を中心配置=足元が地表下 3.9m)。素寸法は人間比
  (半径0.45m・全高1.8m)で、**表示倍率スライダー**(既定 2.0倍)を追加。
- 屋内の接地面は `gz + (floor-1)*floorH`(建物基準)。`floorH = height/levels` を
  `export_3d --plateau` が scene.json へ追加(`levels` は sim 側の意味を保つため据え置き)。
- 書き出し側で `floor` を `1..min(levels,99)` にクランプし、未知の建物名は idx0 ではなく
  **路上(w=0)へ退避**して件数を報告する(demo_event_200a3d: クランプ14件・未知0件)。
  sim 側(`scheduler.py`)の floor はL1が変わるため触っていない=表示側の防御のみ。

検収(`runs/demo_event_200a3d` 再エクスポート): 屋根+0.5m超の屋内サンプル 531→0 /
floor>levels 575→0 / 線路埋没 310→0 / 屋外の足元と地表の差 3.90m→0.000m。

## 追記: テクスチャ経路(松 B-1)+ 地下街 LOD4.1 表示(梅 B-2)(2026-08-02・レーンB)

計画は [highfidelity-3d-physics-plan.md](highfidelity-3d-physics-plan.md) 第1段=梅・第3段=松。
データは**レーンA**(コミット 5ff56c4)の `data/plateau/tiles_lod2/` と
`data/plateau/ubld_lod4_mesh.npz`。本バッチは `viz/make_viewer3d.py` /
`scripts/export_3d.py` / テストのみを触る(src・conf ゼロタッチ)。

### テクスチャ経路(--plateau-tex)

```
python scripts/export_3d.py runs/<name> --plateau --plateau-tex   # → plateau_tex.js + tracks.bin
python viz/make_viewer3d.py runs/<name>                           # → viewer3d_lite.html が参照
```

`--plateau-tex` は **`--tracks-binary` を自動で立てる**(標準経路・縮退策②)。`make_viewer3d` は
`plateau_tex.js` と `scene3d/tracks.bin` が揃っているとき、**分離版だけ**軌跡をチャンク遅延ロードに
切り替える(埋め込み版 `viewer3d.html` は「単一ファイルで完結」が存在理由なので触らない)。

- **分離版だけがテクスチャを持つ**。埋め込み版 `viewer3d.html` はアトラス 1/2 で 80MB ゲートを
  必ず超えるため入れず、レイヤーパネルに「テクスチャ表示は viewer3d_lite.html で」と注記する。
- サイドカー `plateau_tex.js` は JSONP(`PLATEAU_TEX = {...};`・ASCII のみ)。中身はタイルごとに
  xyz(int16・広いタイルのみ int32 が 2 枚)・UV(uint16)・三角形索引(uint16/uint32)・
  WebP アトラス(`data:image/webp;base64,`)。file:// で `fetch` が使えないための JSONP は
  既存 `plateau_mesh.js` と同じ思想。
- **batch_shadowed を落とす**(refine=REPLACE の祖先重複)。707,452 → 596,386 三角形
  (除外 111,066 = 15.70%)。除外後の gml_id は 6,478 件で**重複ゼロ**=同じ建物が二重に
  描かれない(`tiles_batch_attrs.json` と突合して固定)。全 batch が影の 29 タイルは
  サイドカーから消え、148 → 119 タイルになる。
- 1 タイル = 1 ジオメトリ。テクスチャ付きプリミティブ由来の三角形(441,150)を前半、
  無地(155,236)を後半に並べ、`addGroup` 2 つ + マテリアル配列 `[map 付き, 無彩色]` で描く
  (タイルあたり最大 2 ドローコール)。UV は glTF 規約(原点=画像左上)のままで、
  テクスチャ側を `flipY=false`(three.js の GLTFLoader と同じ扱い)。
- **無テクスチャ `plateau_mesh` とは排他**。tex がある時は ①統合メッシュを作らない
  ②`PLATEAU_SKIP` を空にして押出し箱を全部作り、「テクスチャ」トグル OFF のときだけ見せる
  (照合済みだけ skip すると未照合の箱が実形状に突き刺さる)。

### 80MB ゲート対策(縮退策①②・2026-08-02 実施)

1. **`plateau_mesh.js` から統合メッシュ配列を落とす**(`positions_b64`/`indices_b64`/`colors_b64`)。
   tex がテクスチャ付きタイルで置換するので `buildPlateau` は一度も読まない。残すのは
   `matched_ids`・`extras`(歩道橋)・`ubld4`(地下街)・出典。何を落としたかは
   `merged_mesh_omitted` キーに書き残す。**tex が無い経路では呼ばないので従来のサイドカーは
   1 バイトも変わらない**。安全弁として `buildPlateau` は `!PLATEAU_DATA.positions_b64` でも
   退避する(サイドカーだけ残して `plateau_tex.js` を消しても例外を出さない)。
2. **分離版だけ軌跡をチャンク遅延ロード**(第76 の `tracks.bin`)。`--plateau-tex` が
   `--tracks-binary` を自動で立て、`make_viewer3d` は `viewer3d_lite.html` だけをバイナリ経路に
   する。埋め込み版は tracks.json 埋め込みのまま=単一ファイルで完結。

**サイズ実測**(runs/demo_event_200a3d・432 step・200体・2026-08-02):

| 成果物 | 縮退前 | **縮退後** |
|---|---|---|
| viewer3d.html(埋め込み・テクスチャ無し・自己完結) | 40.28 MiB | 40.28 MiB |
| viewer3d_lite.html | 20.15 | **5.54** |
| plateau_mesh.js | 20.13 | **2.90** |
| plateau_tex.js | 65.33 | 65.33 |
| tracks_bin/chunk_*.js(分離版が実際に読む) | — | **5.62** |
| **分離版合計** | **105.61**(超過) | **79.39 MiB(ゲート以内)** |

(参考: `scene3d/tracks.bin` 自体は 4.25 MiB。ブラウザが読むのは base64 JSONP のチャンクなので
上表は厳しい側の 5.62 MiB で計上した。`tracks.bin` 換算なら 78.03 MiB。)

残る縮退の選択肢(未実施): アトラス 1/4 再縮小(レーンA 見積 WebP 33.2→9.9MB)→ −23 MiB 前後。
ラン長が伸びるとチャンクだけが増える(テクスチャ 65.33 MiB はラン非依存)ので、
10日ランでは `--step-stride` か `--sample-agents` の併用が要る。

### 地下街 LOD4.1(plateau_web.ubld4)

- `--plateau` 時に `ubld_lod4_mesh.npz` があれば `plateau_web.json` に `ubld4` キーを足す
  (**追加専用**・+2.11 MiB)。旧ランの plateau_web には無い=読み手は従来経路のまま。
- 面種別(kind 11 種)を 5 群に塗り分け: 床/地面=不透明・内壁/壁/仕切=半透明 0.32・
  扉/窓=強調色・階段等(installation)=別色・天井/屋根=ごく薄い蓋。
- レーンA が床面 z のヒストグラムで分けた **4 層**(z = −13.25 / −10.25 / −6.75 / −4.75 m)ごとに
  表示チップ(全/B1..B4)。層は三角形重心 z の最近傍ピークで決める。
- 旧 `extras.ubld` の箱表示は置換(`ubld4` があれば描かない)。既定 OFF は維持。
  ON の間だけ地表を半透明(0.28)にし OSM ドレープを退避する(地下は不透明な地表の下にあるため)。
- **z 基準の検証**: 地表より上の頂点は 旧 extras 47.37% → 新メッシュ **2.85%**(最大 +1.19m)。
  残りは全て最上層の installation 894 枚 + closure 10 枚 = **地上への階段の天端**で、
  z 基準そのものは健全(旧 47% は粗い箱表現の産物)。ゼロではないので**地表クリップは維持**
  (実物 JS を QuickJS で実行して 908/51,889 = 1.75%・Python 再現 900 枚。差 8 枚は
  閾値ちょうどの同値が float32/float64 で割れる分)。

### 検収

- 既定(フラグなし)の再エクスポート+ビューワー再生成はレーンB 以前(5ff56c4)版と
  **全 8 ファイルがバイト同一**(縮退策の追加後も再確認済み)。
- `--plateau` は scene.json / buildings.glb / tracks.json / terrain_web.json が**バイト同一**、
  plateau_web.json の差分は `ubld4` キーの**追加のみ**(除去すると完全一致)。
  tex 無し経路の `plateau_mesh.js` は `plateau_web.json` の素の写しのまま。
- 新規テスト 21 本(`tests/test_viewer3d_texture.py`)。esprima 構文検査 + QuickJS で
  出荷 JS そのものを実行し、位置/UV/索引/グループ/層/クリップ数を Python と突合。
  縮退後は分離版のチャンクを QuickJS で復号し、tracks.json と**座標 |Δ|max 0.000m・
  w/mode/traffic 完全一致**(5 step × 200 体)を確認。
- **ブラウザ実機は未検証**(機械検査まで)。特に `flipY=false` の向きとアトラスの
  非 2 冪サイズ時のミップマップ挙動は実機で見る必要がある。
