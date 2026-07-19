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
