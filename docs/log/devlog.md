# 開発ログ(ライブ)

> このプロジェクトを「作る側」の意思決定・節目の記録。シミュレーション内部の観測層ログとは別物。
> **プロトコル**: ユーザーとの1往復ごとに1エントリ追記。エントリが10に達したら圧縮して [devlog-compressed.md](./devlog-compressed.md) へ移し、本ファイルをリセット。設計の正典は [../design.md](../design.md)。
> **圧縮履歴**: devlog-compressed.md(Block #0: プロトコル前史 / #1: ログ機構〜分野1-3 / #2: リサーチ完走〜決定アジェンダ / #3: D0-D17決定→P0実装→世界v2-v5 / #4: 生態系→docs完遂→現実ギャップ全波→第9バッチ / #5: ODPT実ダイヤ→制度深化完遂→自己モデル→現実較正→実LLM初証拠→日常プロファイル(第10〜14バッチ) / #6: 開放行動→世界解釈の観察→マルチモデル対応(第15〜24バッチ) / #7: 復元→git化→入力解像度LOD→分析スイート→制約デコード→自由度P2(第25〜34バッチ) / #8: EnvPack→PLATEAU実形状→第37バッチ6トラック→現実スケール転換(第35〜38バッチ) / #9: 同時滞在実測→全員思考転換→行間レイヤS1-S5(第38バッチW2) / #10: W2完結→視覚F→オントロジー多軸→物流・乗れる交通→並列ゲート(第38W2後半〜第43バッチ) / #11: 関係性→経済完結→観測レンズ→日常観察ABC→マクロ⇄ミクロズーム(第44〜58バッチ) / #12: 精査3スライス→関係内生化→GitHub公開→第1回分析→4系統拡張始動(第59〜66バッチ) / **#13: レーン1完了→DT/IDEA計画→二重化転換→統合実装順第70-78始動(第67〜72バッチ)**)。全文アーカイブ: devlog-block6-fulltext.md / devlog-block7to9-fulltext.md / devlog-block10-fulltext.md / devlog-block11-fulltext.md / devlog-block12-fulltext.md / devlog-block13-fulltext.md。

**ライブエントリ数: 8 / 10**(Entry 71 から=継続採番)

---
### Entry 71 — 2026-07-31 — 第73バッチ検収: 真偽台帳ミニマル=fact+信念+伝播木+検証行動+漏洩3点(1964緑)
(日付訂正: 当初 08-01 と誤記=実際は 07-31 深夜〜朝の作業)
Opus実装をFable検収。新規3(truth_ledger.py・analyze_beliefs.py・test_beliefs.py=32テスト)+9変更。
- **fact 8種**(conf データ駆動マップ・コードに固有名詞なし): event_host/venture_open/flyer_post/group_found/
  crime/stock_out/price_change(唯一の連続量真値)/disaster=「場所と時刻が確定したL1既存イベント」のみ。
  shop_state(x,y=0,0)とscenario_shock(エッジ対)は場所が点にならず不採用と正直記録。**新乱数streamゼロ**。
- **信念/伝聞**: 話題一致=場所名+topic_keyの部分文字列(L1を読むだけ=発話生成不干渉・呼数不変・journal等級の
  根拠)。変形は最小(Bartlett型の無情報方向劣化+確信度減衰のみ)。288step mockで belief_update183/transmit41・
  伝播木11本/枝70/最大ホップ3・検証率96%→68%(伝聞拡散で低下)を実測。真値はL1に出さず
  beliefs_ledger.jsonサイドカーへ分離(行間ダイジェスト等の消費経路から構造的に遮断)。
- **検証行動3種**(go/ask/net・ON時のみ_VERIFY_LINE 1行=誘導語彙なしをテスト固定・新規LLM呼なし=k不変)。
  対象特定失敗時はrecent後退=検証率水増しリスクをby_matchで分離可能に(正直設計)。
- **漏洩3点**: 静的=cognition/に台帳識別子ゼロをgrepテスト固定・実行時=CachedLLM generate/generate_many両関門で
  check_prompt(台帳空なら1命令return=既定コストゼロ)・canary=共通接頭辞1本を実ラン全プロンプト(llm_journal)
  不出現で検証。検収時にcache.py別名importでgrep空振り→diff実査で配置確認(報告と一致)。
- 検収: OFF/ON呼数88=88/506=506/1027=1027・golden緑・resume=信念状態一致(checkpoint中央管理+canary再武装)・
  registry 2件journal宣言・verify モードで自動OFF確認・フルゲートxdist **1964緑**(284s)。
- 申し送り: exit_buildingのnode張り替えと_route_to/_apply_free_actionの整合=**潜在バグ疑い**(既存・スコープ外)
  →STATUS持ち越しに登録。→第74バッチ(規範化ステージ+コホートタグ+ゼロ対照)起動。

---
### Entry 72 — 2026-07-31 — 第74バッチ検収: 規範化4段+コホート+ゼロ対照=「記録しないと失われる」観測点が完了(2002緑)
Opus実装をFable検収。新規6(observer/norms.py・initial_frame.py・analyze_norms.py・zero_traits.yaml・テスト2本=38)+9変更。
- **③規範化ステージ**(labeling.norm_stage・観測のみ=cognition/にnorm参照ゼロをgrep確認): S1初出→S2他者引用→
  S3指示詞化(日本語に冠詞が無いため「例の/あの/いつもの」等8語で代替・語の直前max_gap2)→S4合意参照
  (「さっき決めた/ルール」等12語・同一発話共起)。マーカーはconf単一源=コード内ゼロ語。coiner/definitizer/
  institutionalizerを役割分離。mock 288step実測=語63・S2到達7・S3/S4は0件(表層一致の過小検出=mockでは正常と
  正直記録)。norm_stateはcheckpoint中央管理・resume L2一致。
- **Part E1**: 初presence stepは既存L1から導出可能=シム変更ゼロ(在場中は毎stepイベントが出る構造を実査確認)。
  下方因果=規範成立step前後の初参入コホートの初日行動分布比較+置換検定。**閾値は引数必須・未指定エラー**=
  U-10事前登録の枠組みに従い既定値を埋め込まない。配線実測=3コホート・use_rate 0.067→0.203(p≈0.02)だが
  「語の可用性交絡があるためmockの数値は配線確認であって証拠ではない」をレポート末尾に明記(正直設計)。
- **④ゼロ対照**(experiment.flat_traits): 実装点=build_agentの合流点1箇所(名簿/pool両経路)・下流7経路を実査し
  presence選抜はtraits非依存を確認。**実行役の重要な訂正: 「ON/OFFで呼数不変」は原理的に不成立**(発火閾値を
  潰す=誰が発火するかが変わるのが処置そのもの)→保持すべき不変条件は「build_agentの乱数消費本数一致」=
  CRN共分散維持(counting RNGプロキシでテスト固定)。k交絡はzero_traits.yaml(4セルCRN・compute_matched)で
  切り分け。initial_frame=初日N stepの決定論集計をsummaryへ=ラン単位共変量。
- 検収: golden・L1/呼数不変(③観測のみ+④既定OFF)・registry 3件strict宣言・フルゲートxdist **2002緑**(306s)。
  日付誤記の訂正(Entry 71は07-31)。→第75バッチ(ダンバー維持コスト)起動。U-10承認依頼の材料はこれで完備。

---
### Entry 73 — 2026-07-31 — 第75バッチ検収: ダンバー認知枠=維持コスト+忘却/再会(2023緑)
Opus実装をFable検収。新規2(dunbar.py・test_dunbar.py=21テスト)+10変更。乱数/LLMゼロ=strict等級。
- **設計の要**: 休眠=closenessを退避して0にする単一の作用点。tierはclosenessの純関数なので、プロンプト間柄行/
  joint候補/partnership閾値などの下流消費者を**1箇所も改変せず**「維持していない関係」化。OFFではdormantキー
  自体が生えない=バイト一致の構造(relations.py/relations_endo.pyのゲートを実物確認)。
- **層の縮約**: 素値5/15/50/150×scale0.34→最外層51のみ拘束(内側層拘束はcloseness書き換え=不可逆なので宣言に
  留める・Lindenfors 2021の150懐疑も明記し感度分析軸としてconf化)。上限適用は日境界1回=接触時適用は振動を
  実測(5739件)して棄却した過程を正直記録。keep_days=当日接触保護。
- **再会規則**(一貫した1規則): 休眠はcloseness降順経路から自動的に外れ(tier0=コード変更ゼロ)・**弱い紐帯
  探索枠でのみ再会し得る**(Levin, Walter & Murnighan 2011=休眠紐帯は新規性弱/信頼強)・明示的意向(計画with/
  発話キュー)は休眠でも通す(名指しは淘汰より上位)。
- 実測(288step・40体): dormant1378/rekindle252・active_relations_mean=8.0=上限ちょうど。同seed2ラン一致・
  resume(日境界跨ぎ)L1+L2+L3一致・draw内訳1312完全一致・呼数37=37。フルゲートxdist **2023緑**(291s)。
- **相互作用の発見**: pool dehydrateが関係台帳をcount上位20件に切るため、pool ONでは休眠が再会前に消えやすい
  (dormant_events239→dormant_total117・rekindle0)。本選でdunbar ONにするなら要検討→STATUS持ち越し登録。
  →第76バッチ(DT P0軌跡バイナリ化)起動。

---
### Entry 74 — 2026-07-31 — 第76バッチ検収: DT P0軌跡バイナリ化=10日ランの3D再生が成立(2050緑)
Opus実装をFable検収。新規2(scripts/tracks_bin.py 456行・test_tracks_bin.py=27テスト)+4変更。**src/はゼロタッチ**。
- **形式**: GLB同型(magic+JSONヘッダ+payload)・int16×0.05m量子化(PLATEAU_QUANTと同一)・状態wは
  出現値パレット+uint16索引(素int16は屋内エンコードmax720,802で不可と実測して設計変更=完全可逆)。
  sidecar=base64 JSONPチャンク(fetchはfile://でCORS不可のためplateau_mesh.js前例踏襲)・再生追従の動的script挿入
  +LRU4常駐=1万体10日でもブラウザ常駐数十MB。
- **実測**: viewer3d.html 86.1MiB(ゲート超過)→**24.7MiB=ラン長非依存**(10日でも同じ・chunkはディスク側242MB)。
  sim_ue 84.7→22.3MiB(10日外挿0.23GB)。既定フラグなしは既存出力と**バイト同一31/31**(5ラン×全成果物)。
  量子化往復=tracks.jsonが0.1m丸め済みのため**誤差厳密0**(5万点array_equal)・JSデコーダ式のPython再現で
  1万体ラン全一致(最大誤差2.3e-13m=IEEE754ノイズ)。
- **調査数値の訂正**: deep §1.2の「UE 10日≈9.8GB」は基準ランstep数誤記(432を144と記載)で**3倍過大=正しくは
  0.89GB**(実行役が発見・私がdeep 3箇所+計画書P0行に訂正注記)。結論(JSON不可・バイナリ必須)は不変。
- 限界の正直記録: -0.0→0.0のJSON文字列差(数値は同一・テストで差分がこれだけと固定)・**ブラウザ実機未検証**
  (node/ブラウザ不在環境=機械検査まで・成果物パスをユーザーに提示)・エクスポータ側の全展開メモリは別課題
  →STATUS持ち越し。検収=フルゲートxdist **2050緑**(294s)。→第77バッチ(P6追いかけ再生)起動。

---
### Entry 75 — 2026-07-31 — 第77バッチ検収: P6追いかけ再生+Windows共有フラグ事故の発見修正(2087緑)+U-10前倒し提示
Opus実装をFable検収。新規2のみ(live_viewer.py 1,185行・test_live_viewer.py=37テスト)・**src/ゼロタッチ**をgit diffで確認。
- **追いかけリーダー**: part完結判定はparquetフッタ(PAR1先頭末尾+footer長整合)を主・index規則は残骸スキップ専用に
  降格(deep§7.3の「次partで確定」より1flush分低遅延)。L1はpayload列を見せ場イベントのみ読む=311,218行/秒。
- **ライブ画面**: 静的HTML1回書き+live_data.js(JSONP)差し替え(全再生成+meta refreshは10日で1.4万フルリロード
  =pan/zoom喪失のため棄却)。script src方式(file://でfetch CORS不可=第76知見)・?v=キャッシュ回避・--refresh meta退避。
- **★事故の発見**: Windowsのopen()はFILE_SHARE_DELETE を立てない→追いかけ側がpartを開いている最中に本体の
  _finalize_streamのunlinkがPermissionError=**「読むだけ」でランが異常終了する経路が実在**(フルスイート並列で
  実際に踏みトレースバック採取)。_open_shared(CreateFileW SHARE_READ|WRITE|DELETE)で解決・回帰テスト3本固定・
  統合テスト5連続緑。10日ランの監視を安全化する価値ある発見。
- 検収: 観察不変(live併走あり/なしでL1/L2/L3/agents/traits/llm_cacheバイト一致)・途中参加/終了検知/書き込み中
  非読込/レース固定・フルゲートxdist **2087緑**(335s)。限界=最終flush分は地図に出ない(series_stepで明示)・
  ブラウザ実機未検証。
- **U-10前倒し**: 事前登録ドラフトにE節(規範成立=stage≥3+3名・E1-E5)を追記し承認パッケージとして提示済み
  (b792df6)。→第78バッチ(ablate4種+状態ハッシュ+指標凍結=最終)起動。

---
### Entry 76 — 2026-07-31 — 第78バッチ検収=統合実装順 第70〜78 全9バッチ完結(2150緑・T1〜T8全達成)
Opus実装をFable検収。新規7(ablate.py・state_hash.py・metrics_spec.py・analyze_specialization.py・テスト4本=63)+9変更。
- **ablate 4種**(全既定OFF・registry宣言): llm_off=LLM 0本でルール層のみ(既存ニーズ充足+POI選好・新ヒューリスティック
  なし)・propagation_off=発話生成するが他者文脈に一切入らない(**fingerprint自己点検を必須節で報告**: 話者の
  自己連続性は保持・聞き手側の内容だけ切除・**捏造プレースホルダは拒否**=中立文自体が強い指紋になるため。
  残存リスク=「誰も何も言わない世界」は原理的に消せない→fingerprint_risk=known を正直宣言)・
  cognitive_tier=fleet強制下位(非fleetランの縮退をmanifestに宣言)・shuffle_partners(always-draw=RngHub
  statelessなので新streamは既存draw順を乱さない=golden無風)。
- **propagation_offの呼数**: 189vs186(+1.61%)。**呼び出しサイトの追加/削除/ゲートはゼロ**(ユニットテスト固定)
  で、差は「聞かない→unknown_wordドライブが立たない→発火ゲートが変わる」という処置本来の間接経路のみ=
  flat_traits(第74)と同じ構造。厳密一致はcompute_matchedの役目。<10%でテスト固定。
- **state_hash**(既定OFF): 正準シリアライズ→sha256チェーン。T1=同seed一致・T6=workers1vs4一致・改竄3種検知。
  3.5µs/agent/step(1万体≈50s/sim日→interval退避)。片側検定である事実を明記(不一致⇒確実に分岐・一致⇏完全同一
  =厳密判定はL1バイト比較のまま)。
- **metrics_spec_hash**: 指標定義14ファイルの正規化ハッシュ→manifest(T7=1バイト検知・実装中に自分で踏んで実証)。
  metrics/への移動は「ついでのリファクタリング禁止」原則で不採用=コード内定数リスト(リスト自体もハッシュ対象)。
- **専門化スコア**(凍結3指標の最後): analyze_specialization.py=語彙の狭まり/役割分化/時間持続をL1から決定論計算・
  **propagation_off対照との差分でしか主張しない**構造・閾値は引数必須。mock実測=NOT_INTERACTION_DRIVEN
  (Δ+0.008=テンプレ駆動のmock発話の期待どおり)。実装健全性と現象由来の検証を別セクション化(Part G要求)。
- 副産物: build_prompt(reply_to=None)のKeyError潜在バグ修正(reply_to有りの出力は不変=golden維持)。
- 検収: 既定OFF=golden・全OFF明示==素既定・フルゲートxdist **2150緑**(335s)。**同日で第70〜78=見積13.5-15日分を
  完走**(1846→2150テスト・+304本)。残=観察ランON構成の提案(プロファイル変更はユーザー承認後)・
  未決判断(U-10/DT-S1/S-quick/取得運用/PUB-U1)。

---
### Entry 77 — 2026-07-31 — 認知・物理・DT定義の3文書受領→一次実査→統合計画ドラフト(NEW-4承認待ち)
ユーザー指示: claude-code-instructions-physics / shibuya-sim-cognition-design / digital-twin-alignment の3本を読む。
- **統括**: cognition-design(設計決定の正典=チャット結論)が本命=**驚き(予測誤差)駆動の思考発火**
  S=Σg|o−ô|/σ+trigger>θ(LLMはôと宣言的トリガのみ出力・発火判定/g/θはコード)・g更新則(慣れ/感作/
  ペルソナ引き戻し)・θ恒常性(日オーダー)・F/N/P初期値条件=**「生まれつきvs創発」をg(0)分散vsΔg累積の
  分散分解で答える=k掃引より安い**・時間三層(物理1/60s・移動1分・思考クロックなし)・同期バリア+
  ダブルバッファ・環境FB(集約物理量閾値のみ=LLMはイベント宣言不可)。驚き駆動の最大の実利=LLM総呼数が
  Δtに非依存(×1)。**物理の扱いは矛盾を解消**: physics指示書のP2-P4はcognition-design§7「境界IFスタブで本選」
  +dt-alignment§6「剛体導入しない・可視性本気/力学最小限」が支配→本選後レーンへ。
- **一次実査**: イベントキュー無し(P0新規)・perception.py既存(P1土台)・sfm_core/WallCrowd自前(P2はSFM vs
  RVO2に絞れる)・定数per-step直書き(毎分レート化は実作業)・環境FB素材=gate_capacity予約/物流在庫/ODPT・
  k非依存再定義はregistry(journal+affects_k=true+新不変量「スケジュール列同一→世界同一」)で表現可。
  dt-alignment方針1-7は大半実装済み=新規採用は「系譜的同一性」の語彙のみ。
- **訂正**: テスト数1391→2150・GPU申請ゲート消滅(提出済み)・較正用LLMオラクルは本選GPUで(ローカル禁止則)。
- **統合計画** cognition-physics-plan.md: 第79毎分レート化→80σ実測→81閾値発火+バリア→82 watch spec+g/θ+F/N/P→
  83θ較正パイロット+観測装置化→84環境FB3規則→85 Perception契約→86 physics.zonesスタブ(≈8バッチ・実速度2-3日)。
  原本3本はdocs/plans/source/へ。**着手はNEW-4承認後**(本選ONの前提確認込み)。

---
### Entry 78 — 2026-07-31 — NEW-4大枠承認+ユーザー修正3点→計画反映・3並列で実装開始
ユーザー決定: ①**天候=現実同期不要・サンプリング/生成型で可**(DT-S1この形で決着=較正済み天候生成器を
主モードに設計変更→専用streamでstrict等級化可能) ②**物理=できれば本選前**・直前数日(8/12-14)は本番前
検証/微調整に確保(フリーズ) ③**発火アーキテクチャ修正=内省・会話も第一級の発火源**・人の思考は予測誤差
だけで起きるのではない・**予測誤差が大きいときは「世界モデルの書き換え」が起きる**(驚き発火はmodel-revision
モードとして設計) ④実装前のwebリサーチ必須 ⑤体制=Fable5計画/Opus5実行を継続。
- 計画書に§6(修正3点)を追記・物理P2/P3を前倒しレーン化(P2比較→承認→P3縫合〜8/11)・天候生成器行を追加・
  STATUS決定済み履歴更新。U-10承認・S-quick・PUB-U1は引き続き未決。
- **3並列起動**: A=第79毎分レート化(リサーチ=確率のΔt不変変換p=1-exp(-λΔt)等の落とし穴)・
  B=天候(JMA東京8月統計の取得凍結+生成器較正の設計=Richardson/WGEN系weather generatorのリサーチ・
  weather.py/confには触れない=統合は次バッチ)・C=物理P2比較プロト(SFM自前vs RVO2・reference/physics_bench/
  隔離・src不変・決定論/速度/基本図較正性の実測→選定提示)。ファイル互いに素の3体並列=レーン1の運用型。