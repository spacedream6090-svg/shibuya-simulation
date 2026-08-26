# 成果ビューワー計画「Shibuya Chronicle」— 俯瞰と物語の両立

> 起案 2026-08-26。ユーザー要望: 「多すぎて俯瞰しか見えない」の打破=①マクロ: 語彙・話の広がり
> ②ミクロ: 関係構築の物語 ③Run A(ルール支配)vs Run B(フル認知)の対照を魅せる。
> 根拠: Webリサーチ(story sifting/Kyrix/Segue/Gleicher比較分類/等時線)+生データ全棚卸し
> (L1=260種・L2=140列・サイドカー20種・結合キー総覧)。**着手はユーザー確認後**。

## 0. 設計原則(棚卸しの教訓)

1. **単一HTML全埋込は捨てる**: 既存2Dビューワーの失敗(125.7MB・L1全件展開・無間引き)を、
   3D側で実証済みのパイプライン(int16量子化・8MBチャンク遅延ロード・step-stride/agent-sample)へ統一。
2. **run_manifest駆動**: どのkind/列/サイドカーが在るかはmanifestで判定・無いものは静かに非表示(既存流儀)。
3. 位置の正典はL1(`move_segment.pts`+arrive系)。L3は本選1日1点=使わない。
4. `hear`に本文なし=同stepの`speak`へjoin。llm_call_idはcontent-addressed=`(agent_id,step)`併用。
5. 集計はビルド時に事前計算(Kyrix式LODピラミッド)・ビューワーは描画に徹する。
6. 共通基盤: `l1_stream.py`(有界メモリ)・`run_dt.py`(144非ハードコード)・A/B両ランを同一パイプラインで。

## 1. 画面構成(4画面+基盤)

### 基盤 P0: ビルドパイプライン(全画面の前提)
- `scripts/build_chronicle.py`(新規): run dir→事前集計(hexbin LODピラミッド・指標時系列・
  抽出済み物語データ)→量子化バイナリ+チャンク→`chronicle.html`(自己完結・遅延ロード)。
- A/B両対応: `--runs A_dir B_dir` で対照データを同梱。

### 画面1: A/B対照「認知を与えると街に何が起きるか」(提出の背骨)
- **スワイプ地図**(Gleicher: superposition): 同一シミュ時刻のA/Bを同期再生・ドラッグ仕切りで出し分け
  (Canvas clip矩形・数十行)。
- **差分ヘックス**(explicit encoding): B−Aの発話密度・関係形成・語彙到達を発散配色で1枚。
- **全指標connected-dot**(juxtaposition): 語彙数/関係形成/会話/発火/沈黙率…のA/B対を1画面(FEWSim式)。
- **同一人物カードA/B対比**(決定打): 同seed=同名簿を利用し、同じidの「ルールで生きた土曜」vs
  「自分で考えて生きた土曜」を計画・行動・会話・関係の4段で並置。評価軸はGenerative Agentsの
  アブレーション3軸(情報拡散・関係形成・協調)を踏襲=学術的通りが良い。

### 画面2: 関係の伝記(ミクロの主役)
- データ: `relation_tier`遷移(離散)×`relations.parquet` closeness(連続・日次)×`speak`/`dm`**実文**×
  `conversation`{topic,tone,outcome}×`joint_activity`×場所。partner_formed(24cで12,601件)・
  acquaint(via=reply/encounter)・train_copresence(familiar strangers)を出会い文脈の分類に使用。
- 表現: **storylineリボン**(2本の線が接近→合流・太さ=closeness・色=tone)+下段に会話ログ
  (実文・クリックで地図の現場へ)。ペア自動抽出=「他人→知人→友人(→パートナー)」到達ペアを
  昇格速度・会話数でランキング。
- 1人向け: egoSlider式micro view(alter別の関係推移帯)+`channels.parquet`の内部状態帯
  (疲労・不満・覚醒=どのビューワーも未使用の全時系列)。

### 画面3: 語の一生(マクロ伝播)
- データ: `vocab_coin`/`label_coin`{text}→`transmission`{item_id,from,channel,dist_m}(系譜の辺)→
  `label_adopt`→`place_label_bind`{word,node}→L2 `norm_stage_max`。belief系(`belief_update.from/hop`)も同型。
- 表現: **等時線マップ**(語の地区別初到達stepを1枚に=A/B比較可能)+**採用S字曲線**(離陸step/飽和率)+
  **カスケード木**(タンポポ型/双星型の分類)+再生モードでは発生POIから波紋アニメ。
- 「どの経路(対面/SNS/DM)が運んだか」のチャネル分解(Granovetter弱紐帯の実証図)。

### 画面4: 物語ピン+今日のハイライト(story sifting)
- **siftingパターン**(宣言的・合成可能): 出会い→再会→昇格/語の誕生→3ホップ伝播/計画崩壊→リカバリ/
  遺失物の完全連鎖(落とす→拾う→交番→返還 or 横領)/不発の集会(`gathering_intent`=臨界まであと
  N人・現実では観測不能な量)/信念の誤解→検証→訂正。
- **surpriseスコア**(Select the Unexpected式): −log P(そのパターンがその参加者構成で生起)+
  複数信号同時スパイク(発話密度×新語×関係遷移×移動集中)で格付け→俯瞰地図にピン留め→
  クリックで現場・当事者へズーム。
- フォーカスパネルに**思考→行為→結果チェーン**: `llm_journal`(プロンプト・応答全文)×`l1b_llm`×
  L1のllm_call_id join=「何を見て・どう考えて・何をして・世界がどう変わったか」の一本鎖
  (未使用資産の最強格)。

## 2. 作る順序(提案)

| 順 | 対象 | 理由 | データ |
|---|---|---|---|
| 1 | P0基盤+画面1のA側 | 全ての土台。Run Aデータで今日から作れる | A確定済み |
| 2 | 画面2 関係の伝記 | ミクロの主役・Aデータで成立・Bが進むほど自動で豊かに | A即・B追記 |
| 3 | 画面1のB側+対照合成 | Run Bの序盤データが揃い次第 | B day-1 |
| 4 | 画面3 語の一生 | Bの語彙イベントが溜まってから本領 | B day-1後半 |
| 5 | 画面4 物語ピン | 全画面への導線として最後に結線 | A+B |

## 3. 成果物の形

- `chronicle.html`(自己完結・チャンク遅延ロード・80MBゲート厳守)+ hub.htmlへのタブ追加。
- 既存viewer/dashboard/3Dは不触で温存(退行ゼロ)。新規はbuild_chronicle.py+viz/chronicle/系のみ。
- エンジン不触(観察不変性の原則)=走行中のRun Bに影響ゼロ・コミットも自由。

## 4. リスクと正直な限界

- Run Bのイベント量はAの数倍見込み(発話・会話の増加)→チャンク設計はB基準で余裕を取る。
- storylineリボン・等時線は自前Canvas実装(CDN不可)=既存ビューワーの描画資産を流用して圧縮。
- 「面白さ」の主観品質はsurpriseスコアでは保証されない→ハイライトは常に「母集団N件→掲載M件」を
  明示し、ユーザーが閾値を動かせるようにする(既存イベントフィードの流儀)。
