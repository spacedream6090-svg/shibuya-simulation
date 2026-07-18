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
