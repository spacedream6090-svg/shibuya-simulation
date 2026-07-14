# 開発ログ(ライブ)

> このプロジェクトを「作る側」の意思決定・節目の記録。シミュレーション内部の観測層ログとは別物。
> **プロトコル**: ユーザーとの1往復ごとに1エントリ追記。エントリが10に達したら圧縮して [devlog-compressed.md](./devlog-compressed.md) へ移し、本ファイルをリセット。設計の正典は [../design.md](../design.md)。
> **圧縮履歴**: devlog-compressed.md(Block #0: プロトコル前史 / #1: ログ機構〜分野1-3 / #2: リサーチ完走〜決定アジェンダ / #3: D0-D17決定→P0実装→世界v2-v5 / #4: 生態系→docs完遂→現実ギャップ全波→第9バッチ / #5: ODPT実ダイヤ→制度深化完遂→自己モデル・出来事誘発内省→現実較正→実LLM初証拠→日常プロファイル(第10〜14バッチ) / **#6: 開放行動→世界解釈の観察→マルチモデル対応(第15〜24バッチ)**)。

**ライブエントリ数: 6 / 10**

---

### Entry 1 — 2026-07-13 — 第25バッチ: フォルダ構成の復元(実装を直下へ・移動途中状態の修復)
- **依頼**: 直下・shibuya バックアップ・新しいフォルダーに分散した状態を整理し、今までの実装を直下に復元。
- **診断**: 直下=手動移動の途中状態(1,587件・conf/.gitignore/pyproject.toml/worldview.py 等168件が欠落)/
  shibuya バックアップ=最も完全(1,755件・07-12 21:27頃)/新しいフォルダー=残骸14件(全てバックアップと
  ハッシュ一致 or 旧版)。曖昧2件を diff で判定: devlog.md=バックアップ側が正(圧縮後リセット版)・
  unimplemented-inventory.md=直下が正(バックアップ側は改行混入のみ)。
- **実施**: バックアップから欠落162件を補充コピー(既存1,588件は一切上書きなし・mtime保持)→全1,750件の
  ハッシュ照合で欠落0・内容差は意図した1件のみ→圧縮前devlog全文を docs/log/devlog-block6-fulltext.md に
  退避→新しいフォルダー削除。shibuya バックアップは無傷で保持。shibuya-sim はユーザーがデスクトップ直下へ
  退避済み(リポジトリ外)。
- **検証**: 直下から golden/contracts/router_wiring/bridging/detect_emergence 26本緑・.gitignore 機能確認
  (data/odpt_challenge・runs は除外維持=ODPT再配布制限の防壁)・フルスイート実行中。
- **注意(要ユーザー判断)**: リポジトリは**コミットが1件も無く**、現行実装は全て未追跡。今回の復元を救ったのは
  git でなく手動バックアップだった。初回コミットの実施を推奨(ユーザー承認待ち)。

### Entry 2 — 2026-07-13 — 第26バッチ: 初回コミット+GitHub非公開リポジトリ作成(ユーザー承認済み)
- **依頼**: 「GitHubの新しいリポジトリを作ってコミットする理解でいい?それなら実行して」→ 実行。
- **コミット前検査**: .gitignore に手動バックアップ(shibuya バックアップ/)と .claude/settings.local.json を追加/
  staged 410件に対しシークレットスキャン(sk-/ghp_/AKIA/ODPTキー直書き)=検出なし・40MB超=なし・
  runs/・odpt_challenge/・バックアップの除外を確認。
- **実施**: 初回コミット 2727e91 → gh CLI 導入(winget)→ デバイスフロー認証(ユーザーがブラウザで承認)→
  `gh repo create shibuya-simulation --private --source=. --push`。
  リポジトリ: https://github.com/spacedream6090-svg/shibuya-simulation(**非公開**・main)。
- **これで手動バックアップ(shibuya バックアップ/)は git が代替**=ユーザー判断でいつでも削除可。

### Entry 3 — 2026-07-13 — 第27バッチ: 手動バックアップをリポジトリ外へ退避
- ユーザー指示で「shibuya バックアップ」をデスクトップへ移動(→ `Desktop/shibuya バックアップ_20260712`・日付を付与)。
  git が保全を代替済み(初回コミット 2727e91)。.gitignore の除外行は再発防止として残置。リポジトリ直下は実装+runs のみに。

### Entry 4 — 2026-07-13 — 第28バッチ: 日次自動バックアップの仕組み(シミュ実装から独立)
- **依頼**: 一日の終わりに作業内容を shibuya バックアップへ自動バックアップする仕組み(シミュ実装とは別の部分で)。
- **実装**: ops/backup-daily.ps1(新設・PowerShell・UTF-8 BOM)+ タスクスケジューラ
  「shibuya-simulation-daily-backup」(毎日23:30・PCが寝ていれば次の機会に実行=StartWhenAvailable)。
  出力= Desktop\shibuya バックアップ\ ①mirror(robocopy /MIR 増分完全鏡像・runs/.git込み)
  ②snapshots/code-YYYY-MM-DD.zip(runs/.git除く軽量日付版・14日分保持で自動削除)③backup-log.txt(1行/回)。
- **検証**: 初回手動実行=9秒で完走(mirror 1,752ファイル・zip 6.3MB・exit 0)。次回自動実行 2026-07-13 23:30。
- 三重の保全体制が完成: git(コミット履歴)+日次mirror(完全鏡像)+日付zip(14日ロールバック)。

### Entry 5 — 2026-07-14 — 第29バッチ: 入力解像度LOD+分析スイート8点の計画(計画のみ・承認待ち)
- **依頼**: ①推論量LODの逆=入力トークン増減で「世界に対する解像度」の個体差を再現する計画(論文接地・一度見せる)
  ②人流ヒートマップ/OD行列/混雑ランキング/行動統計/ネットワーク変化/介入比較/有意性/LLM要約の実装計画。
  Fable計画/Opusリサーチ2本並列。
- **①入力解像度**(research/input-resolution.md 252行 → plans/input-resolution-lod.md):
  理論接地=Rational Inattention(Sims 2003・容量の個体差は実証あり)。**価値はコスト削減でなく実験軸**
  (decode支配の既決と整合・R1安全=呼数不変)。ノブ上位3=知覚の幅(salience_gate個体別k)/記憶想起件数/
  フィード帯域。beliefs(k路)と全員共通行は不変域。R_input×D_output の2因子直交で
  **「多く見る vs 深く考える」を初分離**が独自価値。取り下げ条件K1-K4を事前登録(飢餓と解像度の分離が核心)。
  ユーザーの理想(全員LLM・思考自己選択)は「人間も日常43-45%が自動的=認知構造自体がLOD」と整理し、
  自己選択はR1衝突のため将来seam。
- **②分析スイート**(research/analytics-methods.md 259行 → plans/analytics-suite.md):
  8項目とも既存に接木可・**純新規は汎用グリッド器とLLM要約器の2本だけ**。鍵=①→③→②が同一の
  空間グリッド集計を共有(25m×1hビン→ヒートマップ→FruinのLOS→ODゾーン)。⑥は同seedペア+置換検定+
  **CRN健全性チェック**(介入前L1突合=rng_stream分離設計の優位)。⑦は効果量・BH-FDR・「pはseed数で任意に
  小さくできる」免責。⑧は「計算はPython・LLMは言語化のみ+数値exact-match照合ガード」でR4防壁維持。
  W1-W4の4ウェーブ・工数2〜3バッチ。
- **実装なし・コード無変更**。両計画ともユーザー確認待ち。

### Entry 6 — 2026-07-14 — 第30バッチ: 入力解像度LOD実装(I1+I2)+分析W1実装(Fable計画・①Fable直轄/②Opus実行)
- **依頼**: 両計画とも提案どおり進めて可。追加要件=①は**既存LOD機構に準拠**(LOD側の変更が波及する一貫設計)
  +**モジュール切り離し可能**な実装。
- **①入力解像度LOD(Fable直轄=cognition/perception中核)**:
  - **cognition/lod.py に共通のLOD軸割当機構を新設**(assign_axis=軸専用stream・trait非依存・share累積で
    決定論割当)。入力解像度が最初の消費者・将来のモデル級LOD(M3)も同機構を使う=**割当設計の変更は
    ここ1箇所で全軸に波及**(準拠要件の実装)。軸ごとに独立stream=直交実験を保証。
  - 5ノブ配線: nearby_pois/nearby_names/recent/retrieve/feed の件数を agent.input_res から読む
    (OFF=属性なし→既定値=現行定数=バイト一致)。salience_k はゲート有効時のみ個体上書き。
    beliefs(k路)と全員共通行は対象外。水準 narrow/mid/wide(mid=現行定数の契約をテスト固定)。
    config は lod.input_res.enabled 1キーで切り離し。agents.json に水準を共変量記録。
  - テスト5本+ガード(golden/contracts/determinism/firing)全緑。**発見: mockはプロンプト内容に反応する**
    (行き先候補・doマーカーをプロンプトから拾う)→「ON=内容差→行動差」はmockでも出る=不変量は
    「OFF=バイト一致」+「ONの同seed再現」として固定。実LLMマイクロスモーク(6体24step)成功
    (narrow×2/mid×1/wide×3割当・11呼・安定)。
- **②分析W1(Opus実装・Fable検収18本自前緑)**:
  - scripts/analyze_flows_grid.py=25mメッシュ×1hビン(pass/present/unique)→ heatmap_grid.parquet+
    **自己完結heatmap.html(時間スライダ)**+**FruinのLOS**(閾値はFHWA HCM Ch.13のTABLE 3を一次確認して
    確定: A>3.2〜F<0.5 m²/人)。実データ: daily300_100d(12Mイベント73秒)で**最混雑セル=スクランブル
    交差点直近(25,-75)m・夕18-20時ピーク**=現実の渋谷と整合。LOS全Aは在圏proxyの疎性による=相対密度と
    正直に明記。÷n_days正規化はFable承認(ラン長の異なる比較に必須)。
  - panel_stats拡張=paired Cohen's d・Cliff's δ・置換検定p・**BH-FDR q**・t分布CI+p値限界の免責。
    実演: n=3ではd=-2.3の大効果もq=1.0に洗われる=「効果量主・p従」の主張をデータで示した。
- **検証**: フルスイート **626本全緑(31分34秒)**(+17本: input_res 5・flows_grid 6・panel_stats_ext 6)。
- 次: W2(OD行列+介入比較)→W3→W4、①はI3(実LLM検証ラン)とI4(R×D 2因子実験)がシミュ解禁待ち。

### Entry 7 — 2026-07-14 未明 — 第31バッチ: 分析W2-W4完遂+夜間実験ラン(シミュ解禁7:30まで)
- **依頼**: 「シミュレーションは7時30分まで可能。実装の続きが終わった後に回し始めて」。
- **実装(Opus 3体並列・Fable検収)**: 環境にpandas無し→pyarrow+純Python流儀を全体に徹底。
  - W2: analyze_od.py(トリップ=route_start→arrive・ゲートウェイ=域外ゾーン・目的帰属spend/建物/day_plan・
    自己完結flowmap.html)+compare_runs.py(CRNペア+置換検定・DiD・**CRN健全性チェック**=L1突合。
    セルフチェック=同一ラン→全37指標差ゼロp=1.0確認)。daily300 1200万イベント38.7秒。
  - W3: analyze_communities増設(network_ts=密度/平均次数/クラスタ係数/次数gini/最大成分比/紐帯重み・
    tie_decay・community_flows=alluvial)+build_panel増設(time_budget・tempogram=睡眠が00-06hに集中を確認)+
    calibrate_report増設(生活時間配分表+KS/EMD自作。**参照分布は発明しない**=平日/休日比較に適用)。
  - W4: summarize_run.py(KPI表=kpi_tables.json単一真実→制約プロンプト→**数値照合ガード**=正規表現抽出→
    exact-match・不一致は破棄→再生成→全滅で決定論フォールバック・忠実性スコア記録・R4防壁)。
    mock実行はガードで弾かれフォールバック=設計どおり(忠実性1.000)。
  - I3分析器: analyze_resolution.py(Fable直轄)=水準別に飢餓チャネル(fallback/空応答)と低注意チャネル
    (distinct-n/訪問先エントロピー)を分離集計・K1判定材料・OFFランは明示拒否。
  - テスト新規46本+後方互換全緑。コミット 89a3dd9 プッシュ済(シークレットスキャン清)。
- **夜間ラン**(実行順・GPU逐次):
  1. ablit品質スモーク15体×1日: fallback 0%・空0・日本語崩れ0・belief 15/15。distinct-2は標本量補正で
     instruct 0.190 vs ablit 0.148(やや低・プロファイル違いの参考値)→ 一次失格条件なし=**ゲート合格**。
     多様性の本判定はセル内ペア比較で。単発疎通: think=true だと思考飢餓が再現(既知)・think=false 正常。
  2. model×k 4セル×2シード(42,7)= 15体×2日×8ラン(conf/experiments/modelk_4cell.yaml・条件優先展開=
     時間切れでもinstructペア=k再検証から確保)実行中(~03:10開始・予定~2.5h)。
  3. 待機: I3実LLM 30体×1日(input_res ON)→ analyze_resolution。
- **並列リサーチ依頼(ユーザー・実行中に追加)**: エンジン群分類(Human/Economy/Information/Organization/
  City/Society/Environment/Time/Integration+将来枠)の妥当性検証。Fable追加=Perception-Attention・
  Belief-Worldview・Language-Dialogue・Space-Map・Demography・Tourism-Visitor・**Meta層**(Observer/
  Reproducibility/Scenario/Calibration)。Opus2体起動: ①リポジトリ被覆照合(engine-coverage-map.md)
  ②文献・外部実装(engine-lit-review.md: GA/AgentSociety/OASIS/Concordia/PIANO/CoALA・action extraction・
  SUMO/群衆モデル/GOAP/RL)。**計画のみ・実装なし**=統合計画 docs/plans/engine-architecture.md はFableが起草。

### Entry 7 追記 — 2026-07-14 早朝 — 夜間ラン結果+エンジン群リサーチ(第32バッチ)
- **model×k 4セル×2シード(42,7)完走**(02:54-05:32・各1,065-1,293秒・計8ラン)+第3シード(instruct
  free/off×s3)を追加実行。品質: **全セル fallback 0%・空応答0・日本語崩れ0**。belief書き戻しは
  free セルで 28/29・27/27(inst)・29/29・28/28(ablit)=**reflect_think修正後の初のk比較が成立**
  (旧パイロットは書き戻し全滅のまま測っていた)。
- **発見(質的・n=2シードは方向のみ)**:
  1. **初の世界改変ツール行使**: ablit_free_s42 で flyer_post 2件(agent 8・「渋谷の夜、新しいアイデアを
     みんなと分かち合おう」)。過去の実LLM全ラン2,654回提示で0件だったものが **abliterated×k自由でのみ**発生。
  2. k対照(free−off)は inst/ablit **同方向**(belief_diversity +0.64/+0.69・speech_diversity +0.025/+0.028)
     = k*信号がモデルを跨いで保存される暫定示唆(アライメント固有アーティファクト説に不利)。
  3. モデル対照(ablit−inst @free): SNS投稿 −6.7件/日・発話多様性 +0.013・ツール行使 2 vs 0 =
     entropy-reduction 除去と整合する方向。distinct-2 同プロファイル比較で ablit≧inst 3/4 組=能力劣化の交絡なし。
  4. CRN警告(compare_runs): 実LLMはラン間で応答が再現しない→ペアは独立2群として解釈(ツールが正しく警告)。
- **I3(入力解像度・実LLM 30体×1日・narrow14/mid7/wide9)**: **K1 不発動**(fallback 0%・空0=飢餓なし)。
  発話多様性(個体平均d2)は narrow 0.430 < mid 0.505 < wide 0.514 と**単調=仮説方向**。訪問先の広さは
  逆方向(narrowがやや広い)=1日30体では未確定・I4へ進む価値あり。written_back率 全水準1.00=不変域健全。
- **エンジン群リサーチ(ユーザー依頼・Opus2体→Fable統合)**: docs/research/engine-coverage-map.md
  (61エンジン全数照合: ◎34/○21/△5/×1=90%実装済み・「将来枠」Politicalが実は最厚・parse_actionは
  寛容な正規化+routine後退)+docs/research/engine-lit-review.md(4層分離はCoALA/Concordia/AgentSociety/
  PIANOと合致・MobiVerse=routine+LLM修正の実証・SUMOは歩行者不向き・4B級JSON遵守の文献値)
  → **docs/plans/engine-architecture.md**(計画のみ): 5層再構成案・P0-P3優先度+実装不要層(Ecology等)・
  制約付きデコードノブ提案・SUMO/RL不採用所見・OPEN 4点(ユーザー判断待ち)。

### Entry 8 — 2026-07-15 — 第33バッチ: エンジン計画の決定反映+制約付きデコード実装(計画A)
- **ユーザー決定**(engine-architecture §6 に記録): ①P1=B採用(制約付きデコード+群衆物理)・実装前リサーチ必須
  ②5層案採用(docs/architecture-layers.md に対応表を固定・コード再編なし) ③SUMO=使うとしても車限定(P2)
  ④Skill討議は後回し。
- **リサーチ(Opus2本)**: constrained-decoding.md=**現行 ollama.py は既に format=json を全呼び出しに無条件付与**
  (計画Aの実体はノブ化+ガード+キャッシュ整備)・format+think は事実上併用不可(GBNFが<think>を禁じ
  思考を殺す/破損実測)・品質文献は「封筒は強制・中身は自由」が落とし所・キャッシュキーへの format 追加必須。
  social-force-crowd.md=推奨は**案a(オフライン合成)**・現行歩行速度1.333m/s はWeidmann 1.34m/sと既に一致・
  ShibuyaSocial(arXiv 2512.18550・位置誤差0.07m)を一次確認(コード未公開)・渋谷較正値(平日26万人・1青1,000人以上)。
- **計画A実装(Fable直轄=LLM配管は中核)**: `model.format: none|json`(**既定json=従来挙動・payload/キャッシュキー
  とも完全互換**)。think=True の呼には format を送らない**境界ガード**(ollama/vLLM対称・reflectの思考殺し防止)。
  cache._key は backend.cache_extra 参照方式(json→None=旧キー互換・noneのみ別キー=切替誤再生防止)。
  fleet/router 子へも透過。テスト10本新規+API/router回帰+**ゴールデン(test_scenario)全緑=41本**+
  実LLM 24stepスモーク正常(6体・23呼)。
- **計画B(群衆物理・案a)**: PySocialForce の vendoring が権限クラシファイアに拒否されたため、
  **文献公開のHelbing式+確定パラメータから最小SFMを自前実装**する方式に切替(外部取得なし・出典コメント必須)。
  Opus実行中: viz/sfm.py+scripts/synth_crowd.py(メゾ所要時間を保存する希望速度設計=平均移動時間不変)+
  crowd_demo.html(自己完結)。シミュ本体・conf は差分ゼロが検収条件。
