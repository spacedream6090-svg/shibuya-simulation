# 開発ログ(ライブ)

> このプロジェクトを「作る側」の意思決定・節目の記録。シミュレーション内部の観測層ログとは別物。
> **プロトコル**: ユーザーとの1往復ごとに1エントリ追記。エントリが10に達したら圧縮して [devlog-compressed.md](./devlog-compressed.md) へ移し、本ファイルをリセット。設計の正典は [../design.md](../design.md)。
> **圧縮履歴**: devlog-compressed.md(Block #0: プロトコル前史 / #1: ログ機構〜分野1-3 / #2: リサーチ完走〜決定アジェンダ / #3: D0-D17決定→P0実装→世界v2-v5 / #4: 生態系→docs完遂→現実ギャップ全波→第9バッチ / #5: ODPT実ダイヤ→制度深化完遂→自己モデル→現実較正→実LLM初証拠→日常プロファイル(第10〜14バッチ) / #6: 開放行動→世界解釈の観察→マルチモデル対応(第15〜24バッチ) / #7: 復元→git化→入力解像度LOD→分析スイート→制約デコード→自由度P2(第25〜34バッチ) / #8: EnvPack→PLATEAU実形状→第37バッチ6トラック→現実スケール転換(第35〜38バッチ) / #9: 同時滞在実測→全員思考転換→行間レイヤS1-S5(第38バッチW2) / #10: W2完結→視覚F→オントロジー多軸→物流・乗れる交通→並列ゲート(第38W2後半〜第43バッチ) / #11: 関係性→経済完結→観測レンズ→日常観察ABC→マクロ⇄ミクロズーム(第44〜58バッチ) / **#12: 精査3スライス→関係内生化→GitHub公開→第1回分析→4系統拡張始動(第59〜66バッチ)**)。全文アーカイブ: devlog-block6-fulltext.md / devlog-block7to9-fulltext.md / devlog-block10-fulltext.md / devlog-block11-fulltext.md / devlog-block12-fulltext.md。

**ライブエントリ数: 0 / 10**(Entry 61 から=継続採番)

---

---
### Entry 61 — 2026-07-29 — 第67バッチ: A1環境条件スキーマ+実高さ配線(レーン1第2波a・1808緑)
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

---
### Entry 62 — 2026-07-29 — 第68-69バッチ: C0可視行列基盤+D1場所の意味づけ最小版=レーン1全6バッチ完了(1846緑)
- **C0(c894267)**: build_visibility.py=視点グリッド×広告面のO(n·m) 2.5D LOS(扇の要変換で視点×辺の一回
  行列演算・frac 0/0.5/1・自建物除外・背面カリング・--heights/--dem/--chunk)。実測=500m四方33,249視点
  ×12面1.7s/可視率4.83%・スケール検証1,331万ペア37.5s/RSS211MB・決定論2回走バイト一致。面スキーマ
  visibility-faces-1.0見本(実測サイネージでない旨明記)。既存ファイル変更ゼロ・新20テスト。
- **D1(df0c446)**: labeling.place_binding(既定OFF)=造語を発生ノードへ束縛→同所滞在者の熟慮プロンプトに
  中立1行(min_adoptersゲート・決定論1語)。乱数消費ゼロ・呼数不変・checkpointはLabelSystem pickle既存経路で
  追加配線不要と判明・resume全層一致。ONスモークで「ジリワサら化」の場所知覚行の実注入を捕捉。
  限界=熟慮coin経路のみ・ノード粒度。新18テスト。
- **レーン1総括**: 計画(twin-physics-vision-affordance-plan.md)の6バッチを同日完了(第66-69バッチ・
  1739→1846テスト)。全て既定OFF=本選10日ランへのリスクゼロで、A環境改変・C可視計算・D痕跡の器が仕込み済み。
  計画書ステータス更新。持ち越し=analyze_sweepへのllm_health接続・U-10承認(閾値+診断日数)・B-L1以降(レーン2/3)。
