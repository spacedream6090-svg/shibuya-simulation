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
- **計画B完了(Opus実装・Fable検収12本緑)**: viz/sfm.py(自前SFM: τ緩和・対向すれ違い・決定論をテスト証明)+
  scripts/synth_crowd.py(入口時刻は実データの弧長時間構造から導出=乱数散布を排除・希望速度=区間距離/メゾ
  所要時間で平均移動時間を厳密保存・窓別seed byte一致)。実データ検証: daily300 夕方2h=13窓/通過199人/
  軌跡点35,396・中心は地図の実在ノード「スクランブル交差点」(-4.3,-2.0) 自動導出。src/conf 差分ゼロ確認。
  限界の明記: 壁力・接触項なし=低中密度の揉まれ方の視覚実証(群集規模の再現ではない)。コミット済み。

### Entry 9 — 2026-07-15 — 第34バッチ: 未実装棚卸しの実装ウェーブ1(A2-A5+A1ローカル分)
- **依頼**: 「unimplemented-inventory.md の未実装リストの実装を進めて。プランを決め、文献リサーチしながら実装」。
  計画=Wave0: A2 / Wave1: A3・A4・A1+A5(Opus3体並列)/ Wave2: C3 / Wave3: D3 / D1-D2はスケール戦略の確認待ち。
- **A2**: production.yaml に model.reflect_think:false(+A1実測を受け reflect_max_tokens:768)。マージ検証済み。
- **A3(接地率)**: detect_emergence 拡張=発話の固有名詞を実在名/シミュ内創発名/作話の3値分類・日次系列
  (panel/grounding_rate.parquet)。実データ: wv_llm_7d 74.9%・modelk 52.3%(カタカナ一般名詞の混入で
  過大な作話率=既知の限界を明記・抽出器拡充はフォローアップ)。作話実例=「ボードライブ」×105等。テスト16緑。
- **A4(内省プロンプト改善)**: prompts.reflect_variety ノブ(既定OFF=ゴールデン緑)・4バリアント決定論
  ローテーション。実LLM検収: 復唱17.9%→0%だが**丸写し(placeholder echo)33%発生=正味悪化**
  → **Fable判断で daily/production とも OFF に戻す**(knob・テストは残置。再ON条件=丸写しガード or
  reflect のみ8b)。エージェントの正直な報告が機能した好例。
- **A1+A5**: bench.py に --lod(真のdecode tok/s=eval_count由来・実測~175tok/s・fallback0%)と
  --analyze-runs(実ラン応答長の分布復元)。conf/profiles 3例(local-ollama/finals-vllm7/mixed-api)・
  ops/launch-vllm-finals.ps1(dry-run既定)・finals-compute-checklist.md。**reflect_max_tokens 2048→768**
  (実測 max=459字≈247tok の~2.2倍余裕・think=false前提・vLLMのKVスロット削減が本命)を daily/production に適用。
- フルではなく対象テストで検収(計45本緑+ゴールデン)。棚卸しに現況更新節を追記。

### Entry 10 — 2026-07-15 — 第34バッチ続き: D3自由度P2完遂+C3 PIMMUR尋問テスト実施
- **D3(Opus実装・Fable検収)**: freedom.p2=move_home(敷金障壁・新stream)/buy(既存spend+chosen)/
  study(記録のみ=Skill討議に抵触せず)/partnership(bond/unbond抽出・片側closeness判定)/
  deviance(無許可出店→既存enforcement摘発)。全て既定OFF=ゴールデンL1一致・R1呼数不変(_FixedLLM証明)・
  P2ロジックは検査外 freedom_p2.py に隔離。検収54本緑+独立シードONスモークで全経路発火
  (move_home5・declined14・study1・venture11)。コミット 5452710。
- **C3(Opus実装・本走はセッション跨ぎでFableが再実行)**: scripts/pimmur_probe.py=in-domainの実プロンプト
  (build_prompt出力そのまま)に尋問1行を付す方式・S1間接→S2/S3直接→S4メタ(ツール有無対)→S5第三者。
  3モデル×4ペルソナ×温度2=126呼。**途中でablitが簡体字「谁」を出力→cp932進捗printが死ぬ**バグを
  reconfigure(errors=replace)で修正して完走。
- **C3結果**(docs/research/pimmur-results.md・全原文保存): in-domainのUnawarenessはほぼ完全
  (S2直接8%・S4メタ0%・**S4ツール提示対でも0%=メニューは実験をtelegraphしていない**)。
  S5第三者視点のみablit/8bが調査目的を言い当て(社会学・都市研究等を列挙)、**PIMMUR暫定=条件付き不合格**
  (3/5モデル法の残り2枠は未導入=保留。看破判定語彙は広め=上限寄りと明記)。qwen3:4bのS5は英語生CoTが
  content に漏れる別問題を記録。分類器テスト20本緑。

### Entry 11 — 2026-07-18 未明 — 第35バッチ: D1+D2実装(EnvPack完成・下北沢実証)+講演デモラン
- **依頼**: ①D1/D2実装(前段で「共通要素vs生成要素」の分類。地理vs抽象=制度・職・精度。分類の仕方は任せる)
  ②プレイベント講演(人工生命・生態系)用に100-200体のシミュを朝9時まで回す(試算を伝えてから・
  中断なし・定期異常チェック)。
- **分類設計(Fable)**: docs/plans/env-classification.md=2分類でなく**3層**(①共通基盤=機構 ②**共有参照**=
  国・都道府県スコープの表〈最賃1226は渋谷でなく東京都の値〉 ③環境固有=EnvPack)×(地理⇔抽象)。
  「精度」は 汎用バンド(②)/場所アンカー(③)/用途プリセット(③)の3箇所に分けて位置づけ。
  Opus棚卸し(env-asset-inventory.md)=計画リスト全現存+新発見8系統(東京月別気候・ads地点・
  原点=スクランブル仮定の横断・**government制度値のコード埋没**)。
- **D1完成(W1-W4・コミット18c9210/bfa6cc2)**: env/shibuya/env.yaml+ref/institutions_jp.yaml(②の実体)+
  envpack.py正準化。W2=基盤4ディレクトリから地名リテラル全数除去(10系統→envpack.*)+**契約テストに
  地名禁止ガード**。W3=government埋没13値をinstitutionsブロックへ(ref一致テストがW1時点の所得税率
  不一致を実検出→訂正=ズレ検知の設計が初仕事)。W4=--envローダ(基底<env<profile<dotlist)。
  **検収の核心: --env env/shibuya が従来ランとL1完全一致**(government ONでも一致)。全てゴールデン
  バイト一致維持・計180+85本緑。
- **D2-v0(コミット0b09130)**: build系の渋谷定数全数引数化(既定=現行)+make_env CLI(stage独立再実行・
  縮退宣言=捏造ガード)。**実証: 下北沢390m角をOverpass実取得→連結性1.0→--envでmockスモーク成功**
  =2つ目の街(W5相当)が同夜に回った。交通は「徒歩の街」縮退・文化語彙はv1/v2へ。
- **講演デモラン**: demo_event_200a3d=200体×3日・daily・seed42・日次checkpoint(23:47開始)。
  健全性: 0:36=967呼/3.05s/呼/エラー0、2:13=2,715呼/エラー0。ペース再計算で総~8,400呼≈7.4h・
  完走見込み~7:10(9時に十分)。完走後に分析スイート+ビューア一式を生成して納品予定。

### Entry 12 — 2026-07-18 昼 — 第35バッチ完結: デモラン3日完走+チェックポイント部分納品の実運用
- **試算ズレと運用判断**: 実測は~4,200呼/日(200体では社会的発火が15体比1.5倍)で当初試算~2,500を超過し、
  3日完走は9時に間に合わないと日1チェックポイント(3:42)で判明。ユーザー指示「承認待ちで中断しない・
  異常値のみ定期確認」に従い**ランは無停止続行**、納品はcheckpointのpart結合(scratchpad/assemble_parts.py)
  による部分データ方式へ切替。日1(76,483イベント)で全パイプライン予行→日2(8:01到着・158,813イベント)で
  講演用差し替え6点を8:25送付=**9時講演に2日分(昼夜リズム2周期)で間に合わせた**。
- **3日完走(12:18)**: 432step・**238,993イベント**・LLM 13,161呼(deliberate 12,229+reflect 513)・
  **fallbackわずか1件(0.008%)**・日別76,483/82,330/80,180=崩壊なし。reflect 513件全てbelief書き戻し。
  社会指標: speak 11,315・hear 24,502・opinion_shift 33,185・relation_tier 13,170・交際成立11組・
  sns_like 1,789・reshare 352・**viral_cascade 230**・議会選出1・転職1・病気7。
- **最終納品**: フルデータからheatmap/OD/crowd(SFM)/summary_ja(忠実性0.947・決定論フォールバック=正常)/
  viewer/dashboard(26.6MB)の6点を再生成し差し替え送付。監視はMonitor(summary.json出現orプロセス死)で
  自動検知=手動ポーリング廃止。
- **教訓**: 体数スケール時の呼数試算は「1体あたり」でなく発火率の非線形(関係密度↑→speak/deliberate↑)を
  織り込む。checkpoint_every=日次+part flushの設計が「走行中ランからの納品」を可能にした(D4本選デモの
  事前分岐ラン方式にも同じ機構を流用予定)。

### Entry 13 — 2026-07-18 昼 — 第36バッチ計画: PLATEAU実形状化(UEガイド+Webビューア=D6-web)
- **依頼**: ①UE5で実験データを載せる方法のまとめ ②現行Webビューアも実形状の渋谷に。まず計画。
- **実査**: Desktop に CityGML渋谷2025展開済み(bldg 29タイル・シミュ圏4タイル~347MB・dem有)+
  SDK for Unreal v3.2.2 zip+**手元UE 5.5=SDK対応と一致**。現行viewer3dはfootprint押出し描画=
  メッシュ描画の追加が必要と特定。
- **計画**(docs/plans/plateau-3d.md): A=UEクイックスタート(200体は mode="sequence" でBP不要が主経路)/
  B=W1抽出(stdlib+numpy・dem実測で標高基準化)→W2照合(重心+IoU≥0.4)→W3 export_3d --plateau
  (ハイブリッドglb・契約キー不変)→W4 viewer(BufferGeometry直描画・≤80MBゲート)→W5検収
  (既定はバイト同一)。3D Tiles経路・テクスチャ・全区域は理由付きで不採用。OPEN 3点を提示し合意待ち。

### Entry 14 — 2026-07-18 午後 — 第36バッチ完遂: PLATEAU実形状化(UEガイド+Webビューア)
- **成果物A(Opus・検収合格)**: docs/guides/ue5-quickstart.md=実機情報(UE 5.5.4実読・SDK zip・
  CityGML展開済みパス)埋込みの一本道6ステップ。200体は mode="sequence"=BP/C++不要が主経路。
  検収でリポジトリ側2コマンドを実走し sim_ue.json(18.8MB・200体×432step)生成済み=UE側3手順のみの状態。
- **W1抽出(Opus)**: plateau_extract.py=bbox→3次メッシュ自動選定(想定通り4タイル)・iterparse・
  軸順sniff・GroundSurface優先footprint・DEM実測ground0=15.18m・6,311棟(LOD2 3,061/LOD1 3,250)・
  npz 5.07MB・最高230.4m=スクランブルスクエアで実世界サニティ一致。railways除外のbbox判断も適切。
- **W2照合(Opus)**: match_plateau.py=重心k-NN25m→0.5mラスタIoU≥0.4・貪欲1対1。
  **地図食い違いを検収で検出**: ランの地図は wide_v7(7,210棟)で既定 shibuya_osm.json(1,181棟)と別物
  → wide_v7 で照合し直し **3,531棟マッチ(IoU中央値0.633)**。周辺部はPLATEAU側に相手なし=箱のまま(設計通り)。
- **W3/W4(Fable直轄)**: export_3d --plateau=照合建物を実測メッシュに置換したハイブリッドglb(53万三角形・
  32.6MB)+scene.json height実測上書き(追加専用キーplateau:1)+plateau_web.json(int16×0.05m量子化・17.3MB)。
  make_viewer3d=plateau_web自動検知→アンカー一意置換で描画注入(既定はバイト同一)・埋込版34.6MB(≤80MBゲート)
  +分離版(lite 17.3MB+sidecar 17.3MB=JSONP方式でfile://のまま2ファイル構成)・PLATEAU出典をHUDに表示。
- **W5検収**: 既定経路4ファイルのSHA256完全一致(バイト同一達成)・glTF構造/量子化ラウンドトリップ/注入マーカー
  全合格・全pytest 819+34本緑。**既存バグ1件発見・修正**: test_daily_profile の reflect_max_tokens 期待値が
  2048のまま(第34バッチで768に右サイズ化済み=テスト側の陳腐化。0bda751以来フルスイート未実行で潜伏)。
- ブラウザでの目視(実形状の見え方・fps)のみユーザー確認待ち。3形式(埋込/分離/glb)納品済み。

### Entry 15 — 2026-07-18 午後 — 表示崩れの原因特定と修正(巻き向き)
- **報告**: ユーザーから「表示が崩れてる」。ブラウザ非所持のため、matplotlibで両面/FrontSide模擬の
  オフラインレンダを自作して自分の目で再現→**壁が抜けて内部が透ける崩れを確認**。
- **原因**: triangulate_3dの2D ear clippingが投影面CCWに正規化し、CityGML由来の表裏を破壊。
  面法線が「外向き」でなく「正軸向き」に揃い、約半数が内向き殻(符号付き体積 正2,813/負3,498)
  →three.js既定の背面カリングで方角依存に壁が消滅。ジオメトリ自体は無傷(両面レンダで正常を確認)。
- **修正**: ①抽出側=元リングのNewell法線と三角形法線を照合し反転時にスワップ→全6,311棟で体積正
  ②ビューア=PLATEAU材質をDoubleSide化(データ由来の局所不整合への保険)。回帰テスト4本
  (床・南北壁の表裏保存)。FrontSide模擬レンダで修正後の正常表示を実証し、修正版3点を再納品。
  コミット 0096adc。教訓: **表裏情報は幾何検証(頂点数・範囲・面積)には現れない**→3D系の検収に
  符号付き体積チェックとオフラインレンダを標準化する。

### Entry 16 — 2026-07-19 — 第37バッチ受領: 大型要望12件→監査3本+6トラック計画
- **依頼**(要約): ビューア(ライティング/地形起伏/駅・地下/無彩色/移動手段判別/ダッシュボード統合)・
  OFF機能リスト化と本番ON選定・研究目標追加(組織の自然形成+ファウンダー条件)・経済深化(銀行/VC/決済/
  消費・リサーチ→実装)・実行時間試算ツール・会話品質の質問・記憶の人間化(忘却/想起失敗・リサーチ→実装可)・
  会話アルゴリズムまとめ・議員選出の現実性検証・信号確認+SUMO真剣検討・世界観=自然界のような仕組み。
- **監査(Opus3体並列)**: ①信号=実装済みだが全72ラン設定でambient=未結線・odでも背景車のみ・歩行者無関係
  ②OFF機能=判断対象23件/実験ノブ11件/ON済み30超/未実装2件(agent-tier LOD等)を全数化
  ③議員選出=全住民自動候補・隣接2候補比較・議会権限は住民提案採決のみ(現実の供託金/SNTV/25歳/
  予算条例権と乖離)・会話=返答保証の往復はあるが対話履歴なし/宛先は最寄りのみ/グループ会話なし。
- **成果物**: docs/research/ に監査3本+off-features-inventory.md、docs/plans/batch37.md(6トラック:
  V ビューア5件・S 忠実化(選挙/交通+SUMO車オフライン/会話強化)・E 経済3wave・M 記憶(ACT-R活性化)・
  T 試算ツール・A ファウンダー観測)。回答: 会話品質は「大モデルで半分解消・構造要因(履歴/宛先)は
  パイプライン修正が必要」。メモリに org-emergence-goal / nature-like-systems を記録。
- OPEN 3点(ON機能セット・選挙現実化の深さ・SUMOオフライン方式)をユーザーへ提示。

### Entry 17 — 2026-07-19 — 第37バッチ W1+W2完遂・コミット(893本全緑)
- **W1(8体並列)**: ビューア4体(V-A抽出=DEM 2m格子地形〈交差点=谷底0m・道玄坂+12.2m〉+渋谷駅地下街
  z-14.3m+歩道橋39基 / V-B=terrain_web+gz接地+移動手段判別〈タクシー33区間・電車圏外177件〉/
  V-C=ACESライティング+無彩色既定+分類色トグル+地形接地+地下橋描画+手段グリフ / V-D=hub統合)+
  T試算ツール(300体×7日≈50時間・α=1.209実測)+リサーチ3本(経済ABM/ACT-R記憶/SUMO)。
- **W2(3体)**: S1選挙フル現実化(自発立候補=propose経路のrule marker方式・SNTV・供託金没収・
  議会予算承認)/ S3会話強化(対話履歴リングバッファ=動的属性でOFF時構造的バイト同一・closeness宛先)/
  E経済3段(消費=家計調査較正・銀行=与信/融資/利息・VC=観測可能変数のみのスコア)。
- **契約調整**: V-A/V-B間のterrain.npz形式不一致をSendMessageで走行中に修正(スチュワード介入)。
  schema.py新kind 9種は事前登録で競合回避。E報告のtools.py一時破損はS1完了で自然解消。
- **統合検収**: フルパイプライン一気通し(37.97MB埋込版)・全マーカー確認・**フル回帰893本全緑**・
  コミット済み。ビューア4点+hub納品。
- **SUMO v0**: パイプライン完成・pip版SUMOはWindows wheelのXML I/O不具合で実行不能と診断
  (公式MSI版で回避可=ユーザー判断待ち)。ファウンダー観測装置も完成(ハブ型26人検出)。
- **最終ウェーブ起動**: 経済配線(schedulerフック5点)+M-W記憶(ACT-R活性化・memory_fail)。

### Entry 18 — 2026-07-19 — 第37バッチ完遂: 最終ウェーブ+本番プロファイル編成
- **経済配線(Opus)**: TODOリスト5点を全配線(家賃/敷金/出店費の不足点融資・与信は収入ゼロ化前の
  値でスコア・貸倒→rent_due経由で既存破産サイクル接続・売買保存則維持)。65本緑。
- **M-W記憶(Opus)**: ACT-R活性化(d=0.5,τ=-2,s=0.5)・refs=動的属性でOFF時バイト同一・
  専用streamで既存draw順無風・memory_failは内省側で発火。25本緑。
- **スチュワード(Fable)**: actrのconfig配線(dotlistの+プレフィックスがOmegaConf非対応と判明→
  素キーで解決)・本番プロファイル編成でYAML重複トップレベルキーの後勝ち事故を検出→既存ブロック
  統合方式に修正(world/prompts/assembly/economyの既存設定を保全)。
- **検収**: production全ONの24stepモックスモーク=fallback 0・決済method全付与・交通od稼働・
  day0選挙は候補0→従来方式fallback(設計通り。立候補の観察はday85-90の告示期間)・議会予算承認
  1件。**フル回帰945本全緑**(唯一の失敗=term_days 30期待の陳腐化を90に追随)。コミット済み。
- **バッチ残**: SUMOは公式インストーラ導入待ち(ユーザー判断)・ライブ連成v1はgo/no-go基準
  文書化済み。D2 v1/v2・B1討議・A4再ON条件などは棚卸し表の従来どおり。

### Entry 19 — 2026-07-19 — 第38バッチ受領: 現実忠実再現へのスケール計画(人数>時間)
- **ユーザー方針**: ①選挙は本番ラン内で行わない=議員はペルソナ事前決定(名簿制) ②背景車両は
  「人が乗っている」べき(現行=幻の車と監査済み・エージェント化へ) ③運転士・店員・配信者など
  域内サービス提供者は全員エージェント ④本番=現実渋谷の忠実再現が土台(組織/ファウンダー観察は
  その上) ⑤来街者は同時存在の数倍のペルソナプール+作成方法の検討 ⑥平均/最大の必要人数を試算→
  本番環境(7GPU)で回せる日数を試算。**人数の確保>実行時間**。メモリ realism-first-scale に記録。
- **W1起動(Opus4体)**: P1=渋谷実人口リサーチ(bbox内の夜間/昼間/同時滞在/日次ユニーク/従業者・
  公的統計)→ shibuya-population.md / P2=ペルソナプール設計(層構造・ローテーション・IPF/需要駆動/
  LLM生成の使い分け)→ persona-pool.md / P3=スケール実行可能性(vLLM 7GPUスループット実測リサーチ+
  estimate_runtime に--fleetプリセット+LOD前景比率→N×方式の日数表)→ scale-feasibility.md /
  P4=議員名簿制の実装(assembly.from_roster・production切替=realism OFF温存)。
- 車のエージェント化は「現実スケールでは背景交通そのものがエージェントの移動に置き換わる」が
  本筋=人口試算とLOD設計が前提のため、P1/P3の結果を受けて設計する。

### Entry 20 — 2026-07-19 — 第38バッチW1完遂: 人数と日数の突き合わせが完成
- P1実人口(一次統計・xlsx直接パース): bbox 3.8km2=夜間~2.96万/平均同時滞在~20-30万/
  ピーク~30-40万/日次ユニーク~70-120万/従業者~25.7万。組織台帳は現実の1/230(52 vs ~1.1万)。
- P2プール設計: ローテーション機構は新規agent-core実装が必要(現行は起動時固定・余剰名簿は
  実体化されない)。プレゼンス=stream(presence,persona,day)の純関数設計でresume/k非交絡が両立。
- P3実行可能性: **LLMは律速でない**(deliberate 92.9%はlod.max_llm_per_step=300で頭打ち・
  plan/reflectのみ線形)。**真の壁=非LLMのPythonエンジン**(本番プロファイル0.060s/agent-step
  =リーンmockの33倍)。spec decodingは飽和時x1.0-1.3(2.8xはQPS1の値)・prefix cacheがx1.8-3.0。
  1万体: リーンで~1h/シミュ日(~22日/24h)・本番プロファイル素のままだと~24h/シミュ日。
  5万体: リーン+フルLLMで~4.4h/シミュ日(~5.5日/24h)。→優先順=エンジン最適化>LOD。
- P4名簿制: from_roster実装・production切替・40本緑(所有外テストの陳腐化2行はFableが追随)。
- 全コミット済み。次: スケール段階の決定(1/10 vs 1/100)+W2(ローテーション実装・組織台帳拡充・
  エンジン最適化・議員含む役割ペルソナ生成)の合意をユーザーへ。

### Entry 21 — 2026-07-19 — 第38バッチW2準備完遂: 同時滞在の実測確定+100万体計画+本選ハード計画
- **同時滞在(ユーザーの核心質問)**: 国交省人流オープンデータ(1kmメッシュ・時間按分=同時滞在の
  実測定義・OGL再配布可)をDL・パース。**平日昼ピーク~37.2万・24h平均~23.5万・週末ピーク~22.7万・
  深夜最小~8.5万**。従来推計(平均25万/ピーク35万)をほぼ検証しつつ「最大=週末夜」を「平日昼
  (オフィス駆動)」に訂正。144step目標曲線CSVをローテーション機構用に納品。
- **100万体計画**: N比例思考密度は現行cap 300と非連続(x12.7)→「思考層(FG+MID)にN比例上限・
  背景は統計行動」で整合。成立ライン=背景SoA 0.0002s/体step。100万プールSoA~2.3GB。
  イベント量4.68億/10日=flush必須。W2メニュー8パッケージ化。
- **本選ハード**: ハッカソン資料に168GB VRAM=24GB級x7(A5000級)と記載済みと発見=ほぼ確定。
  A5000x7実効~21req/s(prefix cachex1.8で~38)→思考層10万なら10シミュ日≈7-9壁日で成立見込み。
  Day-0ベンチ→当日規模決定のプロトコル・縮退線・期間前宿題リストを整備。
- 全コミット済み。次: ユーザーへ統合報告+W2パッケージと在場/思考層構成の決定を仰ぐ。

### Entry 22 — 2026-07-19 — 設計転換「全員思考」+W2実行計画書(実行前レビュー用)
- **ユーザー差し戻し**: 「個々人の思考は全体に大きく関係する。可能ならルールベースでしか動かない
  エージェントはなくしたい。もう一度打開策がないのか深く考えてほしい」→ 旧3tier(背景=統計行動)を
  廃止し**全員思考モデル**へ: ①在場全員に朝計画+夜内省(LLM保証) ②日中は自己計画駆動実行
  (ルールでなく本人の思考の産物) ③顕著性駆動の追加熟慮(driveゲート全員適用・予算N比例)
  ④SoAは状態表現でありhydrateで認知と直交。million-scale §8改訂として記録済み。
- **副次的な理論的利得**: 「動的昇格のk*交絡」(旧§7-5の未解決の核)が構造的に解消——全員が連続した
  認知履歴を持つため、無名からのファウンダー立ち上がり経路が実験デザインで殺されない。
- **W2実行計画書を作成**(docs/plans/w2-execution-plan.md・ユーザー読了→承認→着手のフロー):
  パッケージ番号P0-P7を正典化(英字IDの混乱を解消)。予算=A5000x7でLLM~2.0M呼/シミュ日=12-15h・
  10日≈5.5-6.5壁日(重畳前提)。トレードオフ=日中熟慮~6回/人日(200体密度の~28%)を明記。
  影響分析: 全員が記憶を持つためRAM試算をC案2.3GB→10-15GB目標に改訂・重畳実行が新必須要件・
  観測テキスト保存ポリシーが新論点。確認事項4件(観察ラン位置づけ/小型モデルA/B/保存ポリシー/継続保留)。
- 検証: test_daily_profile 8本green(フルスイートの1失敗は更新前に走った古いランの残骸と確認)。
- 次: ユーザーの計画書読了・承認待ち → Wave1(P0実測+P6台帳+P4観測ストリーミングの3並列)起動。

### Entry 23 — 2026-07-20 — W2計画承認+「行間レイヤ」設計着手+Wave1起動+SUMO公式版導入
- **ユーザー決定**: W2計画の大部分を実装承認。§7確認事項は 1(本番=観察ラン)・2(小型モデルA/B)・
  3(保存ポリシー=前景+サンプル全文)を承認、4=SUMOは公式ダウンロード方針で承認。
- **追加要望(P2の設計深化)**: ①日中熟慮~6回/人日は少なすぎる=200体較正に近づけたい ②ユーザー案=
  推論間の空白を「計画との差分・会った人・出来事」のログから簡単なストーリーで埋める ③計画駆動実行の
  ランダム性(半決定論への懸念)を前向きに実装 ④会話は重要なもの以外LLM不要だが記録に残る形に・
  将来は何気ない会話も ⑤3D地理情報を反映した詳細移動のリサーチ・構想・計画 ⑥日課計画の
  フレームワーク化の要否をリサーチ・計画。
- **Fable設計案(行間レイヤ3機構)**: ①確率的実行(seed付きstreamで逸脱・寄り道・偶発遭遇=再現可能な
  ゆらぎ) ②ナラティブ補間(イベントログ→機械的ダイジェストを全LLM推論に注入=LLMコスト0で連続した
  一日の文脈・夜内省で一人称の物語記憶化) ③会話3層(C1=重要会話フルLLM/C2=構造化会話・LLMなしで
  話題/トーン/帰結を決定論生成し関係値・意見・語彙接触へ機械的効果+記録/C3=すれ違い集計。C2→C1
  顕著性昇格・将来はC2の一部を小型モデルで実文化)。リサーチ3体の結果と統合して設計文書化→承認後P2実装。
- **起動**: リサーチ3体(interstitial-life/3d-movement/daily-plan-framework)+Wave1実装3体
  (P0エンジン実測/P6組織台帳1.1万/P4観測ストリーミング)=Opus6体並列。
- **SUMO**: winget公式版インストール開始(ガイドのID誤記 Eclipse.SUMO→EclipseFoundation.SUMO を修正)。
- 次: 6体の検収→行間レイヤ設計文書→ユーザー承認→P1(SoA・Fable直営)+P2実装。

### Entry 24 — 2026-07-20 — SUMO v0パイプライン初完走(公式版1.27.1・数ヶ月来のブロッカー解消)
- winget公式版(EclipseFoundation.SUMO 1.27.1)導入完了。pip版のXML読込クラッシュは公式バイナリで
  発生せず=pip範囲の既知バグと確定。
- 互換修正3点: ①sumo_home()の優先順位を「環境変数→公式既定パス→pip」に反転(pip版exeを掴む事故を
  防止) ②pyproj 3.7.2導入(公式sumolibの経緯度→net座標変換に必須・ガイドへ追記) ③od2trips 1.27が
  interval id(h0..h23)を車種type=に書き未知車種エラーになる問題→trips.xmlからtype属性を除去する
  決定論的後処理を追加。
- **v0全段完走**: net(エッジ5,575・信号61)→demand(OD 7,719行→車両6,460台)→run(24h走行・
  fcd 16.4MB)→convert(車両6,449・軌跡点99,662・144step→panel/sumo_traffic.parquet+segs.json)。
  seed固定=再現可能。ビューアでの目視確認は未(ユーザーのビューア確認待ちリストに追加)。
- 次: ライブ連成v1のgo/no-go判断材料が揃った。リサーチ3体+Wave1実装3体は進行中。

### Entry 25 — 2026-07-20 — Wave1完遂(P0/P4/P6)+リサーチ3本+P2詳細設計書(フルスイート997緑)
- **P0エンジン実測(前提の書き換え2件)**: ①旧「本番プロファイル0.060s/agent-step」は実LLMランのwall
  残差による誤帰属で、実測はN=300で0.00042(1/140) ②ただし超線形(c∝N^0.6-0.73・300→3000で
  0.00042→0.00166)。主犯=SNSタイムライン順位付けO(閲覧者×投稿)。純オーバヘッド(networkx
  バックエンド走査・OmegaConfアクセス・dict.get)がstep時間の3-4割=SoA以前に削れる。
  → P1の主戦場は「SoA化+密度結合アルゴリズムの有界化+純オーバヘッド除去」の3本柱に修正。
- **P6組織台帳**: 52→11,010組織(経済センサス分布駆動・従業者総和252,311=目標±2%・規模帯は
  小規模支配の現実形・POI割付100%・roles/shift付き・seed決定論・テスト11本)。P5の需要源が完成。
- **P4観測ストリーミング**: stream_events(row-group逐次)+有界Counter/dict集計で全解析経路を
  置換。新旧バイト同一を小ランで担保(テスト26本)。「回せても測れない」リスクを解消。
- **リサーチ3本**: interstitial-life(行間レイヤ・実証較正値=Song93%/±30分/寄り道44%・C2会話の
  設計図・第4機構提案)/daily-plan-framework(結論=型スキーマ+差替語彙+自由文intent・
  社会生活基本調査で較正)/3d-movement(推奨=連続2.5D+層状グラフ・zはO(1)サンプリング・
  駅構内データは自作要=最大リスク)。
- **P2詳細設計書**(docs/plans/p2-interstitial-design.md): S1-S7スライス化・追加LLM呼ゼロで記録
  イベント15-43/人日・実効熟慮~14-16/人日・R1整合表・ユーザー決定4件(C2密度/方針キャッシュ/
  Gumbel/3D Phase0同梱)。
- 運用メモ: サブエージェントが「バックグラウンド検証待ち」で停止する事象が3回(3D/P6/P4)→
  検収をFableが引き取り自走pytestで確定する運用が正解。孤児化した検証プロセスはkillしてよい。
- フルスイート997 passed(26:37)。全成果コミット済み。次: ユーザーのP2設計承認→実装Wave2。
- Entry 25追補: P4のスケール検収をFable自走で完遂——合成20,000,160件(25万体・1440step)を
  ストリーミング集計4種(count/item_cascades/agent_features/collective_series)で完走、
  **外部実測ピークWorkingSet=786MB(<2GB目標PASS)**。状態は行数でなくエージェント数・語彙数に
  有界=4.68億件でも同水準の見込み。所要外挿~38分/パス。エージェント版slowテストは15万件のみ
  だったため実スケールはFableが補完(検収の教訓: 受け入れ数値は自分で測る)。
