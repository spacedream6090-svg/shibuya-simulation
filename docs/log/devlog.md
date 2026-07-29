# 開発ログ(ライブ)

> このプロジェクトを「作る側」の意思決定・節目の記録。シミュレーション内部の観測層ログとは別物。
> **プロトコル**: ユーザーとの1往復ごとに1エントリ追記。エントリが10に達したら圧縮して [devlog-compressed.md](./devlog-compressed.md) へ移し、本ファイルをリセット。設計の正典は [../design.md](../design.md)。
> **圧縮履歴**: devlog-compressed.md(Block #0: プロトコル前史 / #1: ログ機構〜分野1-3 / #2: リサーチ完走〜決定アジェンダ / #3: D0-D17決定→P0実装→世界v2-v5 / #4: 生態系→docs完遂→現実ギャップ全波→第9バッチ / #5: ODPT実ダイヤ→制度深化完遂→自己モデル→現実較正→実LLM初証拠→日常プロファイル(第10〜14バッチ) / #6: 開放行動→世界解釈の観察→マルチモデル対応(第15〜24バッチ) / #7: 復元→git化→入力解像度LOD→分析スイート→制約デコード→自由度P2(第25〜34バッチ) / #8: EnvPack→PLATEAU実形状→第37バッチ6トラック→現実スケール転換(第35〜38バッチ) / #9: 同時滞在実測→全員思考転換→行間レイヤS1-S5(第38バッチW2) / #10: W2完結→視覚F→オントロジー多軸→物流・乗れる交通→並列ゲート(第38W2後半〜第43バッチ) / #11: 関係性→経済完結→観測レンズ→日常観察ABC→マクロ⇄ミクロズーム(第44〜58バッチ) / **#12: 精査3スライス→関係内生化→GitHub公開→第1回分析→4系統拡張始動(第59〜66バッチ)**)。全文アーカイブ: devlog-block6-fulltext.md / devlog-block7to9-fulltext.md / devlog-block10-fulltext.md / devlog-block11-fulltext.md / devlog-block12-fulltext.md。

**ライブエントリ数: 0 / 10**(Entry 61 から=継続採番)

---

---
### Entry 61 — 2026-07-29 — 第67バッチ: A1環境条件スキーマ+実высさ配線(レーン1第2波a・1808緑)
- **実高さ**: scripts/build_heights.py→data/building_heights_shibuya.json(215KB・3,531棟・再生成バイト一致)。
  world.heights(既定OFF)ONでCityMapが建物にheight_m/height_src付与(既定地図1,181棟=plateau971/levels210/不明0)。
  高さ定義はheight−base(zmax−zmin)を採用=plateau_index.heightはground0基準頂部標高で坂上過大
  (corr 0.681>0.628で裏付け)。属性付与のみ=消費者ゼロ(C0/B-L1が後続消費)・ON/OFFともL1バイト一致。
- **world.mod**(既定OFF・profile=conf/worldmod/*.yaml): 反実仮想の条件パラメータ化。①edges_closed=既存closed
  フラグ経由でrouting迂回(通過ゼロ実測)②edge_speed_scale=実効長写像でA*と移動予算の両方に効く
  (cost_scaleでxy_alongが幾何位置を保持)③open_hours.cats=filter_open両向き④gate_capacity=予約フィールド
  (現行に容量概念なし=未消費と正直明記)。summary.jsonにworld_mod 2キー(ON時のみ)。乱数ゼロ・R1契約明記。
- 正直な限界: open_hoursのPOI単位未消費(commerce.is_open_poiがcat単位)・world.modとscenario.shock_closureは
  併用不可(同じclosedフラグ共有)・speed_scale ON時はmove_segment.dist_mが走行コスト長になる(x,yは幾何位置)。
- 検収(Fable): golden+draw数一致+新規36テスト+フル1808緑(251s)。検収59本再走緑。
