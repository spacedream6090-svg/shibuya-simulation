# 開発ログ(ライブ)

> このプロジェクトを「作る側」の意思決定・節目の記録。シミュレーション内部の観測層ログとは別物。
> **プロトコル**: ユーザーとの1往復ごとに1エントリ追記。エントリが10に達したら圧縮して [devlog-compressed.md](./devlog-compressed.md) へ移し、本ファイルをリセット。設計の正典は [../design.md](../design.md)。
> **圧縮履歴**: devlog-compressed.md(Block #0: プロトコル前史 / #1: ログ機構〜分野1-3 / #2: リサーチ完走〜決定アジェンダ / #3: D0-D17決定→P0実装→世界v2-v5 / #4: 生態系→docs完遂→現実ギャップ全波→第9バッチ / #5: ODPT実ダイヤ→制度深化完遂→自己モデル→現実較正→実LLM初証拠→日常プロファイル(第10〜14バッチ) / #6: 開放行動→世界解釈の観察→マルチモデル対応(第15〜24バッチ) / #7: 復元→git化→入力解像度LOD→分析スイート→制約デコード→自由度P2(第25〜34バッチ) / #8: EnvPack→PLATEAU実形状→第37バッチ6トラック→現実スケール転換(第35〜38バッチ) / #9: 同時滞在実測→全員思考転換→行間レイヤS1-S5(第38バッチW2) / #10: W2完結→視覚F→オントロジー多軸→物流・乗れる交通→並列ゲート(第38W2後半〜第43バッチ) / **#11: 関係性→経済完結→観測レンズ→日常観察ABC→マクロ⇄ミクロズーム(第44〜58バッチ)**)。全文アーカイブ: devlog-block6-fulltext.md / devlog-block7to9-fulltext.md / devlog-block10-fulltext.md / devlog-block11-fulltext.md。

**ライブエントリ数: 2 / 10**(Entry 50 から=継続採番)

---

### Entry 50 — 2026-07-25 — 未実装要素候補一覧の精査(実装前レビュー)
ユーザー提示 docs/missing-elements-candidates.md(A内部可動性/B加齢/C対人の陰/D蓄積/E場所/F個人差)を
Explore 12項目のコード実査で裏取り。**主な訂正**: ①転職・異動は実装済み(_phase_career・lay_off/
rehire/switch_org・既定OFF=確率駆動。真のギャップは「選択由来化」と転居・世帯再編・既存org生死)
②資産ストックは口座E5で実装済み=残高永続・破産・免責・利子(欠けは残高Gini/時系列の観測列のみ)
③記憶は忘却まで実装済み(ACT-R冪乗減衰+日次間引き。未実装は「美化」のみ)④偶然の出会い→関係形成は
C2会話の基幹経路として既存(物理近接hearers_of→meet_prob→record_contact。第58バッチが屋内へ拡張。
属性類似は初期友人グラフのみ)⑤リスク選好はTRAITS={nfc,risk_tolerance,internal_locus}で既存構成概念
=R²(k)の核(時間割引は不在だが**persona_pool再生成禁止により新trait軸は実質封印**)。
**方針整合の指摘**: 模倣・嘘は「促進機構」でなく「観測レンズ」先行が natural-coinage/日常観察方針と
整合。B(加齢・生死)は実装せず限界明記とする文書の判断を支持。**優先提案**=(a)観測スライス
(資産分布・弱い紐帯・模倣連鎖検出=シム不変)(b)内部可動性(転居・bond→同棲・career選択由来化)
(c)負の評判伝播(語彙contagionの負方向再利用=コスト低)。既存機構のON構成(career等)で得られる
可動性が大きい点も明記。実装はユーザー承認待ち。候補一覧ドキュメントをリポジトリへ収録。

---
### Entry 51 — 2026-07-25 — 第59-61バッチ: 精査承認3スライス完走(観測/内部可動性/負の評判・1687緑)
ユーザー承認「提案通りに実装を進めていい」+候補一覧.mdの作業ツリー撤去(b57f468・履歴とEntry 50に保存)。
体制: Fable計画/検収/コミット・Opus実行(3コミット 55d0e0e→9cf9fe6→0baabba)。
- **第59 観測スライス(a)**: assets.py=L2全体5列(gini/top10/median/mean/前日比順位τ)+💰資産タブ(L3事後
  再構成=resume安全)・analyze_weak_ties.py=既存決定論LPA再利用でbridge辺/brokerage/語彙採用のbridge
  経由率(グラノヴェター検証観測)・analyze_imitation.py=接触→初行動の時差検出+非曝露ベースライン比
  (促進せず観測のみ=natural-coinage方針・因果断定しない注記)。mock実測: Gini 0.417→0.450・模倣RR7.34・
  bridge経由採用8.7%。**検収補修**: τ前日状態のcheckpoint非搭載(status.py前例踏襲)がassets ONの
  resume==straightを崩す欠陥を検収で発見→checkpoint中央管理へ搭載・260step境界跨ぎresumeテストで固定。
- **第60 内部可動性(b)**: mobility.py=転居(職場変更/家賃滞納rent_due起点・世帯全員一括・evicted対象外)・
  同棲(bond14日+closeness→move_in世帯併合/unbond→move_out)・career選択由来化(job_searchツールを
  LLM行動空間へ=既存tool選択枠内で呼数不変・決定論マッチング→既存switch_org再利用)。stream "housing"・
  イベント4種。mock576step: relocate10件=全件世帯単位。**支援修正2件**=既存resumeギャップの顕在化対応
  (_career_day保存=転職二重発火防止・_ensure_orgsのresume時再attach回避=agents pickleの配属が正典)。
- **第61 負の評判伝播(c)**: gossip.py=内生の悪評タグ(種=既存負イベントのみ・データ駆動マップ・LLM悪評文
  生成なし)・伝播=相異なる知人数の閾値2(labelsの延べ回数と意味論が異なるため独立実装・理由記録)・
  日次忘却=永続烙印にしない・制裁=相手選択後退+joint誘い低下+status負項(max_penalty安全弁・会話数/
  呼数不変)。mock288step: seed7/spread257/fade43・reach分布に準飽和と局所消滅の二峰性が自然発生。
  **検収補修**: gossipのresumeテストが既存relationsギャップ(_rel_day非保存=mid-day resumeで減衰/風化
  二重発火)を顕在化→checkpoint中央管理へ搭載・全層一致+round-trip直接検証で固定。
- 検収の型が結実した往復: 3バッチ連続で「新機能のresumeテストが既存の未検証ギャップを顕在化→中央管理へ
  補修」(assets τ・career/orgs・relations)。resume==straight保証の網羅が実質的に前進。
  ゲート1626→1656→1667→**1687**(全green・全既定OFF=ゴールデン維持)。
