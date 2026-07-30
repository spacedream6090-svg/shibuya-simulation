# 開発ログ(ライブ)

> このプロジェクトを「作る側」の意思決定・節目の記録。シミュレーション内部の観測層ログとは別物。
> **プロトコル**: ユーザーとの1往復ごとに1エントリ追記。エントリが10に達したら圧縮して [devlog-compressed.md](./devlog-compressed.md) へ移し、本ファイルをリセット。設計の正典は [../design.md](../design.md)。
> **圧縮履歴**: devlog-compressed.md(Block #0: プロトコル前史 / #1: ログ機構〜分野1-3 / #2: リサーチ完走〜決定アジェンダ / #3: D0-D17決定→P0実装→世界v2-v5 / #4: 生態系→docs完遂→現実ギャップ全波→第9バッチ / #5: ODPT実ダイヤ→制度深化完遂→自己モデル→現実較正→実LLM初証拠→日常プロファイル(第10〜14バッチ) / #6: 開放行動→世界解釈の観察→マルチモデル対応(第15〜24バッチ) / #7: 復元→git化→入力解像度LOD→分析スイート→制約デコード→自由度P2(第25〜34バッチ) / #8: EnvPack→PLATEAU実形状→第37バッチ6トラック→現実スケール転換(第35〜38バッチ) / #9: 同時滞在実測→全員思考転換→行間レイヤS1-S5(第38バッチW2) / #10: W2完結→視覚F→オントロジー多軸→物流・乗れる交通→並列ゲート(第38W2後半〜第43バッチ) / #11: 関係性→経済完結→観測レンズ→日常観察ABC→マクロ⇄ミクロズーム(第44〜58バッチ) / **#12: 精査3スライス→関係内生化→GitHub公開→第1回分析→4系統拡張始動(第59〜66バッチ)**)。全文アーカイブ: devlog-block6-fulltext.md / devlog-block7to9-fulltext.md / devlog-block10-fulltext.md / devlog-block11-fulltext.md / devlog-block12-fulltext.md。

**ライブエントリ数: 6 / 10**(Entry 61 から=継続採番)

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

---
### Entry 63 — 2026-07-30 — DT統合計画+ハッカソンIDEA組込計画(Opus5×3調査→計画書2本・実装は承認待ち)
ユーザー指示: ①企業DT/3Dシムとの組み合わせを大枠→深掘り→実装案まで ②第1回IDEAからシム組込で面白い/
世界再現度が上がるものの分析と実装計画。
- **調査**: Opus5×3=DT業界大枠(dt-landscape.md 446行)/技術深掘り=リポ照合つき(dt-integration-deep.md
  822行)/IDEA選定=リポ照合つき(hackathon1-analysis/ideas-shortlist.md 28候補採点+上位8ミニ設計)。
- **DT計画**(dt-integration-plan.md): 一般則=「一方向・事後」結合のみ原則と整合(リアルタイム同化は全て
  非整合=差別化)・商用DTに「なぜ行くか」の内生層は不在・社会エージェント状態の交換標準は世界に存在しない
  →「Digital Model」を正確に名乗る方が強い。優先順=P0軌跡バイナリ化(1万体1日でviewer90.4MB=ゲート超過・
  UE10日9.8GBが前提で折れる)→P6追いかけ再生(flush_segmentのpart parquetを読むだけ=ライブ風・ドクトリン
  無傷)→P5 SUMO反実仮想(信号A/B→edge_speed_scale注入=H_Bの実測供給)→P4' USD書き出しのみ→P7較正限定
  同化→P1 Cesium/3D Tiles→P2 UE5(バージョン三竦み=PLATEAU SDK5.5.4/City Sample5.6+/MetaHuman5.8+
  日本語パスビルドエラーに注意)。却下=Unity本体(歩道RnSideWalk非export→官製RoadNetwork-Generator+既製
  歩行空間ネットワークで代替)・Isaac Sim本体(RTコア必須+本選GPU余剰ゼロ+CPU決定論POV既存)。
- **IDEA計画**(hackathon1-ideas-implementation-plan.md): 28候補中8件実装済み/13部分/7新規。採用8=
  ①エコー/自己反復の計測と伝播カウント除外(grep0件の完全な穴=他候補の前提)②未定義行動レジスタ+沈黙
  第一級化(enum外をfallbackに捨てている→「行動空間の外へ出る個体」の操作的定義)③規範化ステージ4段+
  命名者/制度化者分離(観測のみ・k*二層化なら論文級)④ゼロ対照+初期フレーム共変量⑤ダンバー維持コスト
  ⑥場所二層知覚+館内放送⑦誤情報構造化(ground_truth/rumor・5分類・信念別チャネル)⑧健全性3点。
  バッチ編成=第70(①②)第71(③④)第72(⑤)+本選後(⑥⑦)・計約11日・全て既定OFF。
- 未決=DT-U1(P0/P6を本選前に入れるか=推奨入れる)・ID-U1(第70-71まで本選前=推奨)ほか。実装着手は
  standing rule通りユーザー承認後。

---
### Entry 64 — 2026-07-31 — 二重化指示書3本の受領+一次実査・STATUS.md(現況台帳)新設
ユーザー指示: ①リポ直下の claude-code-instructions{,-instruments,-instruments 1}.md と
~/Downloads/dual-mode-requirements.md を読む ②「計画のみ/実装済み/判断待ち」一覧の.mdを**リポ直下**に置き
毎実装で更新 ③R1制約も柔軟に変更可としてよい。
- **指示書の中身**: 観察/検証ランの二重化=FREE/REPLAY/STRICT 3モード・content-addressedキャッシュ・
  ジャーナル(LLM入出力全文)・状態ハッシュチェーン・metrics_spec_hash・機能レジストリ(repro_tier=
  strict/journal/none+ランモード自動取捨)・真偽台帳+信念/伝播木/検証行動(Part B最優先)・コホートタグ(Part E)・
  アブレーション4種+env.variant_id。受入基準T1-T8。※instruments 1はinstrumentsと**バイト同一の重複**。
- **一次実査(grep+cache.py読解)**: T8は現行で既に成立(src/にdatetime.now/グローバル乱数ゼロ)。
  CachedLLM(D13)=content-addressed応答キャッシュ既存(llm_cache.jsonl・key=sha256(model+params+think+prompt))
  だが**REPLAYのfail-fastとプロンプト全文の永続化が無い**(L1bはcall_id/agent/purpose/step/cachedのみ)。
  world.mod≈env.variant_id(第67でほぼ実装済み)・Part E≈IDEA③④(第71バッチ計画と重複)・
  Part B≈IDEA⑦だが**投入時期が衝突**(指示書=本選前必須 vs IDEA計画=本選後)。新規性が高いのは
  機能レジストリ・状態ハッシュチェーン・metrics_spec_hash・ablate.llm_off/propagation_off/shuffle_partners。
  日程の食い違い(指示書=本選8/8-8/23 vs 現行認識=8/15-8/30)は要ユーザー確認。
- **STATUS.md新設**(リポ直下): §1実装済み/§2計画のみ/§3判断待ち(U-10・DT-U*・ID-U*・NEW-1〜3)/
  §4 R1柔軟化の現況/§5受領文書の処遇。**毎バッチのコミット手順に更新を組み込む**(メモリ
  status-ledger-protocol にも保存)。実装はNEW-1判断後(検証→統合計画→承認→着手のいつもの順)。

---
### Entry 65 — 2026-07-31 — ユーザー全決定→統合実装順確定(第70-78)・第70着手・DT再提案調査開始
ユーザー決定: 本選8/15-8/30確定(指示書8/8は誤り)・GPU申請/ODPT確認完了・NEW-1/NEW-3承認(検証→計画→実装)・
ID-U1=ダンバーまで本選前・DT-U1=P0+P6本選前・DT-U4/ID-U2/ID-U3は推奨どおり・U-10タイミング委任・
ファイル処遇委任・**観察ランは再現性を厳密に求めない方針**・実装順は Fable 決定に委任。
- **DT定義の転換**(ユーザー): DT=「物理・地形・乗り物・天気/気温・人を現実のある時点でコピーし舞台にする
  スナップショット。現実はシムの解像度を高めるデータ収集ツール。同期不要」→ DT-U3(用語)は廃止し
  **スナップショット型DTとしての統合案の再導出**を Opus リサーチに投入(journal等級ならラン中実データ注入も
  復活しうる=前回「決定論と非整合」で却下した選択肢の再検討が核心)。天候は weather.py で合成済み=実データ化候補。
- **統合計画書** dual-mode-observe-verify-plan.md 作成: 検証結果=既成立(T8/キャッシュ/L1ジャーナル/world.mod
  ≈variant_id/mock=STRICT相当)vs 欠け(REPLAY fail-fast・プロンプト全文永続化・レジストリ・Part B/E1・ablate・
  hash chain・metrics_spec_hash)。訂正5点(日程・閾値検査は解析時へ・Part B=IDEA⑦統合・Part E=IDEA③④統合・
  モード新造せず)。**統合順=第70(IDEA①②)→71(LLMジャーナル+REPLAY+manifest)→72(レジストリ+ランモード)→
  73(真偽台帳ミニマル)→74(規範化+コホート)→75(ダンバー)→76-77(DT P0/P6)→78(ablate+hash chain+指標凍結
  →U-10承認依頼8/12-14)**。観測点(失われるもの)優先=指示書の思想を維持。
- 原指示書3本は docs/plans/source/ へ原文保存・重複1本削除。計画書2本のステータス行更新。
  第70バッチ実装(Opus)と DT 再提案調査(Opus)をバックグラウンド起動。PUB-U1(公開ミラー.md除外+適宜同期)は
  新規相談事項として STATUS §3 に登録。

---
### Entry 66 — 2026-07-31 — DTスナップショット再提案完成(調査1,177行→提案書・DT-S1判断待ち)
Opus調査(dt-snapshot-reproposal-notes.md・出典URL付き・未確認事項は§3.6に正直列挙)をFableが検分し
提案書 dt-snapshot-integration-proposal.md に統合。要点:
- **切り取り機構は既存**(build_map.py --osm-date=Overpass attic query・osm_date=2025-04-01凍結済み・
  start_date:auto/seed:autoの「ロード時1回解決」作法も既出)=再提案は発明でなく横展開。
- **最大の空白は天候**: weather.pyの8月は合成(32,25,雨30%)±3℃で35℃出現率14.5%・36℃以上出現不可・
  「連続する猛暑」が構造的に出せない。本選10日ラン(8/16-8/26)は2025年の都心10日連続猛暑日(8/18-8/27)と
  ほぼ重なる=DT-S1(S3+S4=3.5-4.5日・第75/78と競合)として判断提起。
- **journal等級で復活するのは一方向強制のみ**(状態同化は研究設計上の理由で不採用のまま)。推奨=案A(事前
  materialization・strict)土台+本選は案B(日次+resume・journal)・案Cは案Bへ縮退(coreのネット出口はLLM1本維持)。
- 用語問題(旧DT-U3)解消: Kritzinger分類は自動データフローの向きだけで決まる→案A=Digital Model・
  案B=Digital Shadowと正確に自己記述。前回計画へ訂正2点反映(④は「状態同化のみ不採用」に限定・DT-U3廃止)。
- 安価な穴5件(observe.yamlが広域地図/実ダイヤを読まない・バス表未生成・jinryu未接続・入力ハッシュ未記録・
  opening_hoursが抽出で落ちている=生応答には在る)→S-quick(S0/S1/S2/S5/S9≈1.8日・S0は第71相乗り)として承認待ち。
- 本選中にしか取れない消えるデータ(Metro CrowdNavi=5日保持・人口マップ=24h・WBGT=10/21終了)は取得運用のみ提案。
- ライセンス地雷2件(商業施設/区サイト転載不可・OSM由来テーブルのODbL share-alike)をPUB-U1に接続。
- 新判断事項: DT-S1(天候・選択肢a/b/c)・S-quick承認。第70バッチ(Opus)は実装続行中。
