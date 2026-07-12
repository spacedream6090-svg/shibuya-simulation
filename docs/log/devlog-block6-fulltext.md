# 開発ログ(ライブ)

> このプロジェクトを「作る側」の意思決定・節目の記録。シミュレーション内部の観測層ログとは別物。
> **プロトコル**: ユーザーとの1往復ごとに1エントリ追記。エントリが10に達したら圧縮して [devlog-compressed.md](./devlog-compressed.md) へ移し、本ファイルをリセット。設計の正典は [../design.md](../design.md)。
> **圧縮履歴**: devlog-compressed.md(Block #0: プロトコル前史 / #1: ログ機構〜分野1-3 / #2: リサーチ完走〜決定アジェンダ / #3: D0-D17決定→P0実装→世界v2-v5 / #4: 生態系→docs完遂→現実ギャップ全波→第9バッチ / **#5: ODPT実ダイヤ→制度深化完遂→自己モデル・出来事誘発内省→現実較正→実LLM初証拠→日常プロファイル(第10〜14バッチ)**)。

**ライブエントリ数: 7 / 10**

---

### Entry 1 — 2026-07-10 — 第15バッチ: 歩行速度の検証(結論: シムは既に現実準拠)+3Dビューワー
- **依頼**: ①歩行速度を現実の渋谷の人流と同じに(ビューワーで速すぎて見える) ②昨日のランの3D版ビューワー。
- **①検証(実測)**: world.modes.speeds.walk=800m/10分=1.33m/s(不動産表示の標準80m/分)。daily300_100d の move_segment 実測(27.8万歩行区間)=中央値683m/step(**1.14m/s**)・平均568m(0.95m/s・到着端数込み)・上限800m(1.33m/s)。現実の渋谷の歩行速度(自由1.3-1.5/混雑1.0-1.2m/s)と**既に同水準**→シム側は変更なし。「速すぎる」の正体=**ビューワーの時間圧縮**(既定×4=1秒に40シム分)。混雑減速(edge_capacity 20)は300体では一度も発動せず(密度不足=将来の群集イベントでのみ効く)。
- **①対処(ビューワー側)**: make_viewer.py の再生速度に ×0.5/×1 を追加し**既定を×4→×1**(1秒=1step=10分)へ。ツールチップに「歩行の実速度は中央値1.1m/s=現実の渋谷と同水準・速く見えるのは時間圧縮」と注記。JS は Number() 解釈で×0.5も安全。3D版は元から0.5-8×・既定1×で適切。
- **②3D版**: make_viewer3d.py(three.js 同梱・export_3d 自動実行)で生成。smoke300_1d=8.1MB・daily_llm_20a7d(実LLM日常20体×7日)=28.8MB を送付。**exp_llm_100d の3Dは368MBで断念**(14,400step のトラック埋込み。長期ランの3D化は日数スライスが今後の課題)。2D更新版(×1既定)も再送付。

---

### Entry 2 — 2026-07-10 — 第16バッチ: 計画専用バッチ(データ戦略・基盤抽出・環境自動生成・自由度)Fable計画→Opusリサーチ→Fable統合
- **依頼**: ①生データ最小+後処理 vs 加工重視を文献で比較し処理方法も設計 ②渋谷と切り離した基盤モデル抽出+環境モジュール分離の計画(渋谷シム本体は本番検証用に凍結) ③環境自動生成モジュールの要素分解と構築計画 ④エージェント自由度の現状監査と現実比ギャップの実装計画。**全て実装なし・.md のみ**。
- **Opusリサーチ3本(並列)**: docs/research/data-pipeline-lit.md / framework-architecture.md / agent-freedom-audit.md。
- **Fable統合計画4本**: docs/plans/data-strategy.md / foundation-extraction.md / environment-autogen.md / agent-freedom-plan.md。
- **主要な決定・発見**:
  - データ: 文献(event sourcing/tidy data/ODD/出力解析標準)は「生=正準・最小・追記専用、指標=派生」を支持=ユーザー直観は正しい。**本プロジェクトは既にほぼこの構造**(L1正準・観測系は全てL1のprojection)。L2の大半はL1から再導出可能=冗長で、非復元のin-situ量は4つ(drive/theta_drift/status系/窓カウント)のみ→「L2凍結・新指標は後処理へ」を方針化。パイプライン=warm-up7日除去→tidyパネル2枚(agent-day/run-day)→複数シードCI→研究量(R²/EWS/発散)。
  - 基盤分離: **コードは既に良い分離状態**(場所固有性はdata/とproduction.yamlに外出し済み・configパス束縛が切断面)。混在は行番号レベルで少数(deliberateの「渋谷」直書き・transitの駅名フィルタ・annual/routineの原点・economy/governmentの日本既定値)。→ **EnvPack(env.yaml manifest)方式**をW1-W5で計画(物理分割はせず論理境界から。各Waveゴールデン一致が検収条件。W5=2つ目の街での実証)。
  - 環境自動生成: 要素分解表(地理=容易/交通=低中/合成人口=中/制度表=中/文化・語彙=高・捏造ガード必須)→ make_env 7-stageパイプライン、v0(半自動)→v1(e-Stat IPF)→v2(一括生成)。本選の差別化=「渋谷で較正した基盤を他の街に即日展開」。
  - 自由度: 過去の議論は内的自由度(k・思考頻度)に集中し**行動的自由度の監査は初**。LLMが選べるのは発火時の発話系+改変5ツールのみで**move_toすら無く、生活の自己決定(退職・移住・欠勤・夜更かし・消費・家族)は全てルール強制**。「提示2,654回で行使0回」の実測より動機接続が対で必要。→ P1(quit_job/apply_job/move_to/skip_work/stay_up=呼数不変・既定OFF・freedom行使率をL2観測)→P2(移転・消費・学び・家族・軽微な逸脱)→P3見送り、の3段計画。
- 実装は全て別バッチ・ユーザー承認待ち。渋谷シム本体・ゴールデン・テストは無変更。

---

### Entry 3 — 2026-07-10 — ★第17バッチ: 開放行動("do")+価値の4軸 — LLM自身が行動を決める自由度(リサーチ→設計合意→実装)
- **依頼**: 自由度の実装。列挙型でなく「物理・現実の制約以外は何でもできる」開放型=行動選択をLLM自身に委ねる。土台として欲求・価値の分類設計(ユーザー仮説=世界2.0の価値3分類: 実用/感情/社会)。先に文献調査→まとめ→実装。Fable=メイン、Opus=サブ。
- **Opusリサーチ**(docs/research/desire-value-theory.md): needs.py に5潜在価値次元が既存(調査の上積みのみ)。3分類は SNG(functional/emotional/social)とほぼ同型で妥当、**多理論一致(SNG epistemic/Reiss好奇心/Schwartz)で認識的価値を第4軸に追加すべき**。タグは排他でなく多重分布。判定は決定論辞書+中立自己申告(LLM judge は R1違反で不採用)。充足力学は「感度=可・目標注入=不可」の線内で。
- **設計合意(ユーザー3決定)**: ①4軸(実用/感情/社会/認識) ②辞書+自己申告併用 ③needs接続する。
- **実装(Fable・認知コア)**:
  - **src/society/values.py 新設**(場所非依存の基盤層・CHECKED_DIRS外=価値名を知る層): 行動カテゴリ辞書13種(創作/学習/鑑賞/ゲーム/運動/散策/交流/飲食/買い物/向社会/家事/休養/探索。生活時間調査の3次活動を骨格・渋谷語なし)→4タグ重み+中央値価格(乱数なし)。自己申告の正準化(日英ゆらぎ吸収)→辞書と1:1ブレンド。5次元→4タグ写像で個体の素質 profile4・行動との一致度 match を観測。**充足 sat(4軸・限界効用逓減)→日次で中立0.5へ回帰(需要の再蓄積)→ sat_mods(reason→感度倍率)** = 飢えた価値に紐づく出来事ほどゲージに響く(Alderfer 飽和。目標注入なし)。
  - **deliberate**: freedom.open_actions=true のときだけヘッダに "do" 1行(what自由記述/where任意/minutes/value任意申告。中立提示・例なし)。parse_action に do/free/activity 分岐(寛容パース・minutes 10-240 クリップ)。
  - **scheduler**: _apply_free_action=物理・所持金・拘束(勤務/就寝中は移動不可)の客観ゲートのみで裁定。行き先は POI 名の決定論解決(完全一致→部分一致)→徒歩移動。消費カテゴリは中央値価格を _spend(cat=free_*)。記憶+L1 "free_action"{what, category, tags, match, report, minutes, cost, dest, sat}。日次 _phase_freedom_day で sat 回帰。
  - **drive.add**: 第3の倍率 sat_mods(drive_mods×needs_mods×sat_mods。None=OFF でバイト一致)。mock: do行マーカーがある時だけ25%で do を返す(OFF は draw も不変)。config: freedom ブロック(既定OFF。satiation_gain=0で純観測=k掃引用)。
- **検証**: 新規 tests/test_free_action.py 6本一発全緑(OFF=純既定L1一致/単体力学/パース/ON効果=カテゴリ・充足・spend連動/ON決定論/R1呼数不変)+ガード30本全緑(ゴールデン・契約・内省・drive)。**実LLM検証**(qwen3:4b・daily+freedom ON・15体×2日・17.6分): free_action 5件(deliberateの1.7%)—**世界改変ツールの0/2,654と対照的に開放行動は自然に行使される**。5件全てで自己申告あり・行き先解決成功・鑑賞1500円の支出も連動。カテゴリ=散策/運動/鑑賞/飲食/その他。match は申告 emotion の個体で+0.38=素質との一致も観測可能。
- **本番方針**: production/daily は据え置き(既定OFF)。k*実験に入れる場合は satiation_gain=0(純観測)から。

---

### Entry 4 — 2026-07-11 — ★第18バッチ: コミュニティ観察・データパイプライン+商業観点・街路の環境情報・計算量削減計画(Fable計画/Opus実行)
- **依頼**: ①自然形成コミュニティの動き・構造の観察分析(無理な組織化はしない) ②有用データを加工抽出するパイプライン(これまでの観点+Claudeが有用と思う観点+**商業的に重要な観点**) ③現実の渋谷の広告・視覚・聴覚などの環境情報を「大きな変化を与える×メリット>リソース」のもののみ実装 ④少ない計算量・推論量で現実を再現する案(**計画のみ・実装なし**)。Fable計画/Opus実行。
- **設計合意(ユーザー3決定)**: ③=街頭広告+群衆視覚(音環境は見送り=メリット<コスト)/②=商業4観点(人流商圏・広告ファネル・消費売上・トレンドROI)全部/①=レポート+ビューワー色分け。
- **Opusリサーチ3本**: docs/research/community-detection.md(Louvain/LPA決定論・Jaccardライフサイクル・E-I/NMI・nx Leidenはbackend必須で不可)/commercial-analytics.md(既存L1でKPI計算可・OOH効果量の現実バンド=視認0.3-0.6・転換×1.02-1.15・**接触の大半は無効果**・スクランブル交差点一次データ)/compute-efficiency.md(**decode支配=入力削減は効かない**・未回収のタダ飯=speculative decoding 2.8倍・**archetype 42,000倍は個体異質性を消しk*と正面衝突**)。
- **①コミュニティ観察(Opus実装→Fable検収で欠陥発見→Opus修正)**: scripts/analyze_communities.py=対面/DM/SNS反応/イベント共参加の合成グラフ(**組織所属・found_groupは検出に入れず参照分割**=E-I/NMIで乖離を測る)→週次窓→Jaccardマッチングで誕生/成長/合流/分裂/消滅。**検収で発見: LPAが密グラフで全300人を1コミュに潰す**(15窓全部1コミュ・原因=一回きりのすれ違いhearエッジ+チャネル内max正規化)→修正=**min_weight 2.0の足切り(反復相互作用=紐帯)+louvain(seed=0)を正準に昇格**+nx.pagerankのscipy欠如で全ラン leader=0.0 だった実バグも発見(純Python power-iterationに置換)。修正後 daily300_100d=**窓ごと7〜13コミュ・Q0.37-0.48・ライフサイクル66件**(誕生24/消滅26/合流7/分裂9)・組織NMI≈0.35/E-I≈0.98=自然コミュニティは会社・学校の線から乖離。達成帰属(主催・集客・設立・カスケード)も機能。ビューワー色分け=communities.jsonが有る時だけ埋め込み(窓境界で色が切替=集団の動きが見える)。tests/test_communities.py 5本。
- **②パイプライン+商業観点(Opus実装→Fable検収でファネルバグ発見→Opus修正)**: build_panel.py(stage0検証+tidyパネル: agent_day/run_day。日の切り方=step//144の活動日でagents×daysを保証)/panel_stats.py(シード横断CI+ペア比較+R²再利用)/commercial_report.py(footfall・dwell・回遊遷移・Huff商圏・カテゴリ×時間帯×客層売上・客単価・採用曲線・カスケード・イベントリフト正負両対応)。**検収で発見: 広告転換判定がtarget照合なし**=「3日以内にどこかの建物へ入った率」で94.1%と出る盛りすぎ→修正=target建物照合+**非接触対照+リフト**+target限定spend+footfall表の住宅除外。修正後 street_llm_2d_v2=**転換1/17=5.9%・対照0%・リフト5.9pt**(1件はground truth確認済みの実来店)。tests/test_pipeline.py 6本。
- **③街路の環境情報(Fable実装=シム本体)**: src/society/street.py新設=**街頭広告(OOH)**: 掲出枠(POI→建物→ノードの3名前空間解決。daily.yaml=QFRONT/SHIBUYA 109/ハチ公前広場/マークシティ)・週次キャンペーン=実在POIを決定論抽選(**ファネルがシミュ内で閉じる**)・視認判定=新stream "ads"(視認率0.45/0.20=現実バンド・cooldown 1h・日次上限4)・L1 ad_campaign/ad_exposure・発火時に中立1行(想起窓1日=adstock近似・3回以上で「何度も」)。**行動転換は決定論で押し込まない**(中立提示のみ=低転換の現実はLLMの自然な無視に委ねる)。**群衆視覚**: 同席者の実データ集計1行(人数の質感+年齢構成=記述的規範。乱数なし・捏造なし)。既定OFF=バイト一致・R1呼数不変。tests/test_ads.py 6本+ガード32本。**実LLM検証(qwen3:4b 15体×2日)**: 4キャンペーン・接触30件(10/15人)・**発話での広告言及38件**=「八虎」の広告のデザインが対話の話題として伝播(聞き手つき=広告の口コミ化を自然観察)・来店転換5.9%=現実的な低さ。
- **④計算量削減(計画のみ)**: docs/plans/compute-optimization.md=「入力を削らず同じ意味の計算を安く回す」。E1(speculative decoding・prefix cache疎通・reflect右サイズ化・step内バッチ=全て決定論/R1中立)→E2(INT4・routine cachingはブラインドA/B条件付き)→E3(階層化=本選後)。観察情報は「削らず的確に選ぶ」・非推奨=archetype/プロンプト圧縮/キャッシュヒット率向上。
- **検証**: 新規テスト17本(ads 6+communities 5+pipeline 6)全緑+ガード32本全緑。フルスイート(Opus中間時点で555本全緑)を最終状態で再実行中。devlog圧縮も実施(Entries1-10→Block #5)。
- **教訓**: Opus実装の検収は「テスト緑」で止めず**実データ規模での退化検査**が必須(1コミュ潰れ・転換94.1%・pagerank0.0の3件とも単体テストは通っていた=規模と現実値ではじめて露呈)。

---

### Entry 5 — 2026-07-11 — 第19バッチ: リサーチ専用(世界モデル・AIの解像度・Social Simulacra系譜+社会実装)Fable計画→Opus3本→Fable統合
- **依頼**: ①世界モデルを深くリサーチし「エージェント行動に影響する要因候補」を導出 ②AIの解像度を上げシムを現実に近づける知見の増強 ③Social Simulacra分野の先行研究を固有名詞に固執せず貪欲に網羅し、活かせる知見と**他プロジェクトの社会実装**を重点リサーチ。Fable計画/Opus実行。実装なし(候補列挙まで)。
- **Opusリサーチ3本(並列)**: docs/research/world-models.md / llm-human-fidelity.md / social-simulacra-survey.md。Fable統合: docs/plans/reality-levers.md。
- **①世界モデル**: 系譜(Ha&Schmidhuber→Dreamer→MuZero→JEPA→Genie3/Cosmos)・LLM内部世界モデルの実証(Othello-GPT/空間時間表現)と反証(**Vafaタクシー=次トークン予測は一貫した地図を持たない**)・認知科学(Friston予測処理/Tolman+SR/prospection/反実仮想/Bandura可制御性/Bicchieri規範予期)。**診断: 本シムは予測誤差の「検出」(驚きLOD)と内的状態化(belief/self_model/needs)が厚く「前向きの予測生成」が薄い**。欠落候補C1〜C9を導出、最優先=**C2可制御性/結果予期**(efficacy飽和を破る第2軸)+**C6規範の予期**(世界改変の閾値=k*と同型)+**C1期待形成**(共通土台)。全て「世界側で決定論外部化→既存1呼に不透明1行」の型でR1/決定論/指紋なしを保つ。
- **②AIの解像度**: 実証全景(silicon sampling 80-95%だが裾過小/Park2024接地86%/**SimBench最良40.8=シミュレーション能力は未熟**)・バイアス伝播(sycophancy/utopian illusion/herd/**homogenization=裾が痩せる・manifold collapse=属性を盛ると逆に均質化**)・作話の線引き(主観の作話=人間らしさ・出来事の作話=毒、接地率で計測)・機構(**introspectionの自己報告は約2割しか内部状態に接地→「行動でkを測る」既方針が機構的に正当化**)。うちの実観測4件(ツール0行使/発話反復/作話/mock逸脱)は「**アライメントが分布を狭め調和へ引き裾を消す単一機構の別々の顔**」と診断。打ち手①〜⑩(★★★=model×k対照/VS徹底/行動指標主義)。
- **③系譜+社会実装**: Park3部作の目的変遷(設計プロトタイピング2022→認知再現2023→実在proxy2024)・23+プロジェクト網羅・**PIMMUR 6原則(代表39論文の89.7%が違反。うちは既存資産でほぼ準拠=準拠表1枚が論文・本選両方に効く)**・商用分析(Aaru $1B評価等——**払われているのは「現実にコストを払う前のwhat-ifの答え」でQ&A型は物理的帰結を返せない=うちの空隙が商用の空隙**)・**最有望経路=PLATEAUの「行動レイヤー」**(幾何ツインに較正済み行動を載せる。国交省ユースケース募集中)+政策事前テスト+群衆安全(ハロウィン)+EnvPack段階展開(OSS→コンサル→都市パックSaaS)。
- **統合(reality-levers.md)**: 交差点=(1)飽和問題に状態(C2/C6)・文脈(⑥非鎮静)・モデル(LoRA)の3層解法が独立に収束 (2)k*測定の機構的正当化+PIMMUR準拠 (3)「身体を持つ都市」=商用の空隙。優先度: P1=C2/C6/C1+VS徹底+ペルソナ薄く+PIMMUR表、P2=model×k対照・作話メトリクス・既知結果較正、P3=接地サブ集団・27B・LoRA。やらないこと=RAP木探索(R1衝突)・内省自己報告のk証拠化・ペルソナリッチ化・Q&A型synthetic users参入。
- **実装なし・コード無変更**。着手は全て次バッチ以降のユーザー承認後。

---

### Entry 6 — 2026-07-12 — ★第20バッチ: 主観的世界モデル(C1/C2/C6+世界解釈の観察)・PIMMUR準拠・内省全滅バグの発見と修正(Fable計画/Opus実行)
- **依頼**: 前バッチのP1(C2可制御性・C6規範予期・C1期待形成・VS徹底・ペルソナ棚卸し・PIMMUR表)+model×k対照の実装、デモは案のみ。核心=「各エージェントには世界を各々の解釈で捉えた世界があり、仮説を立て検証しながら世界を知り、行動して変えていく。**エージェントの世界解釈と、その変化を観察できるようにしてほしい**。データの集め方・解釈の仕方はClaudeが深く考えて実装」。
- **src/society/worldview.py 新設(Fable・乱数ゼロ・既定OFF)**: C1期待形成=場所×4h帯の人出EMA(**検証可能な仮説**。誤差の記録=検証の観測)/C2可制御性=**全員0.5起点**・世界の応答(提案可決/否決・売上・閉店・ビラ閲覧・主催参加・賛同・許可却下)だけで分岐=**生得でなく純経験の経路依存**(k*の問いへの直接接地)。強/弱シグナル(0.3倍)+限界効用逓減+クリップ/C6規範予期=開拓的行動(出店・提案・主催・結成)の記述規範率→「新しいことを始める人が珍しくない/ほとんど見ない街」の全員共通1行。注入は3行とも自然文・閾値超えのみ(mood_text方式・因子語なし)。日次 L1 "worldview" イベント(agent: ctrl/期待規模/期待誤差、街: norm_rate)。R1呼数不変・L1増分走査(絶対位置)。
- **mock 30日×100体で飽和を発見→日次計上キャップ追加**: mockの開拓行動率(0.55/人日=実LLMの数百倍)で応答が洪水になり全員ctrl 0.9台へ=**efficacy天井と同型の飽和の再演**→ ctrl_daily_strong 2/weak 3(感覚更新の生理的上限)で減速(sd 0.05→0.10・中間帯9人)。根因はmockの行動分布=実LLMでは開拓が稀なので現実的分岐の見込み(機械系=mock・行動系=実LLMの分担どおり)。
- **scripts/analyze_worldview.py(Opus)**: ①世界解釈パネル(agent×日) ②仮説検証ループ=期待誤差の収束曲線(「誰が早く世界を学ぶか」) ③可制御性の分岐=0.5起点の分散拡大・行動との相関 ④**解釈の分岐**=共有事象(悪天・災害・提案成立・広告)前後24hの発話valenceの個体差(「同じ世界、違う理解」) ⑤belief世界観クラスタ(3-gramコサイン・決定論) ⑥世界観カード(「この人は世界をこう見ている」)。tests 5本。
- **★重大バグ発見: 実LLMの夜間内省が100%空**(第20バッチ検収で発覚)。ollamaのnum_predictは思考トークンを含むため、reflect_think=true では qwen3:4b の思考が2048を食い尽くし最終JSONゼロ——**wv_llm_2d/freedom_llm_2d/daily_llm_20a7d/exp_kfree_llm_s7(R²(k)パイロット)全てで written_back=0件**。belief書き戻し(kの作用チャネル本命)が実LLMで死んでいた。**daily.yaml に reflect_think:false → 15/15書き戻し成功**(belief例:「渋谷の街をより良くつなぎ、みんなが一緒に楽しむイベントを創出することが、自分自身の成長と地域の活性化につながると気づいた」)。**含意: R²(k)パイロットの free−off 差は belief 経由でなく呼数分岐・深い内省格上げ等の他経路の可能性=再検証が必要**(memory: reflect-think-starvation)。production.yaml は未修正=ユーザー判断待ち。
- **PIMMUR準拠(Opus)**: docs/research/pimmur-compliance.md=一次ソース実確認(正典 arXiv:2509.18052・違反率90.7%/母数42・看破率47.6%に訂正)。**6原則中5 PASS・Unawareness のみ PARTIAL**(5モデル尋問テスト未実施=宿題として手順提案)。k* robustness audit 観点も新設。
- **model×k対照(Opus調査→実行は保留)**: docs/research/model-contrast-setup.md=abliterated対照 `huihui_ai/qwen3-abliterated:4b-v2-q4_K_M`(2.5GB・209K pulls)実在確認・base版はJSON崩れ交絡リスクで第3条件に格下げ・SimBench r=−0.942は**未確認と訂正**(定性機構のみ確認)。1日スモークでJSON遵守/fallback/distinct-2の裏取り→4セル(15体×2日)の設計。**ollama pull が権限拒否→ユーザーの実行/許可待ち**。
- **VS徹底+ペルソナ棚卸し**: 診断の結果**変更なしが正解**(ペルソナ中央77文字=既に薄く多様・variety_hint はdaily/production ON済み・VS使用済み)=manifold collapse リスク低。reality-levers.md に記録。
- **デモ案(計画のみ)**: docs/plans/demo-plan.md=3幕構成(本物の渋谷が生きている→ライブ政策what-if→世界を変える人は生まれるのか)。ライブ介入は事前分岐ラン方式を主・介入キューをストレッチ。worldviewファンチャート(全員0.5からの分岐)が新しい絵の候補。
- **検証**: tests/test_worldview.py 8本+test_worldview_analysis.py 5本全緑・ガード(golden/contracts/free_action/ads/deep_trigger)全緑・フルスイート実行中。実LLM: 1日ラン(修正検証=書き戻し15/15)+7日本番観察ラン(20体・世界観クラスタ/解釈の分岐/ctrl分岐の本命データ)実行中。

---

### Entry 7 — 2026-07-12 — 第21バッチ: 旧・渋谷シム(shibuya-sim)のレビューと移植計画(計画のみ・実装なし)
- **依頼**: ユーザーが以前別の機会に作った渋谷シミュレーションを shibuya-sim/ に、現行実装を「新しいフォルダー/」に整理。旧実装に目を通し活かせる部分を実装案に(実装はしない)。Fable計画/Opus実行。
- **フォルダ移動**: リポジトリ直下が shibuya-sim/(旧MVP)と 新しいフォルダー/(現行一式)の2つに。以後のパスは 新しいフォルダー/ 基準。
- **Opus全読レビュー**(docs/research/legacy-sim-review.md): 旧=7モジュール+スクリプト群のMVP(OpenAI/ollama・A/B対照・創発指標の思想あり)。判定=**A(現行に無い)2件・B(学ぶ点あり)4件・C(現行が上位互換=採用不要)11系統**を根拠付きで明示。
- **Fable統合**(docs/plans/legacy-adoption.md): 採用候補3+保留3。
  - **P1 創発の後付けテキスト検出**(旧detect_emergence.py): 架空の場所・モノの析出/規範発話(〜すべき等)/語の共伝播をL1テキストから読み取り専用検出=「どんな種類の発話が現れたか」の器(現行定量指標の穴)。worldview分析・judge.py と合流。リスクゼロ・半日。
  - **P2 SNSが架橋した物理距離**: transmission へ None安全な dist_m/near 追記+sns_far_frac=SNS有無A/B の被説明変数。
  - **P3 ペルソナ深さ属性**(contradiction/past_setback): ★第20バッチ「薄く多様が正解」診断との緊張を明示→全面採用せず検証用サブ集団50人でA/Bしてから。
  - 保留=宛先選択重み付け(R1検証コスト比で効果不確か)・icebreak非対称・コスト見積り(bench.py拡張として本選前)。
- **実装なし・コード無変更**。着手は全て要承認。実施順推奨: P1→P2→P3(観測の器を先に)。

---

### Entry 8 — 2026-07-12 — 第22バッチ: マルチモデル/LOD計画・P1/P2実装・P3不採用判断・abliterated取得とスモーク合格(Fable計画/Opus実行)
- **依頼**: ①複数ローカルLLM+APIモデル対応とLOD再設計=リサーチ→計画のみ(実装なし) ②P1/P2は実装可 ③P3は現状比較でClaudeが採否判断 ④abliteratedはセキュリティ多重検証後にダウンロード可。
- **①リサーチ**(Opus: docs/research/multi-model-lod.md)+**Fable実装計画**(docs/plans/multi-model-lod.md):
  LODの第一軸=purpose別(reflect3.8%=大/deliberate92.7%=小。全員一様=R1無傷・既存FleetLLM tiers seamが原型)。
  動的エスカレーション不採用(呼数変動=R1違反)。**リサーチの「agent-tier割当=固定trait由来」案はFable判断で却下**
  (モデル能力×生得特性の相関はR²(k)に生得性を裏口注入=k*研究の自殺点)→trait非依存の決定論割当("model_tier"
  stream 1本)を本命に。コスト: 全API最安$139/ラン(Batch$70)だがk×seed掃引で破綻→本命=全ローカル・APIは
  前景/reflectのみ。Anthropic現行世代はtemp/seed撤廃=再現はllm_cache固定が唯一。M1(APIバックエンド)→
  M2(合成ルータ=子を各自CachedLLMで包みname別キャッシュ)→M3(agent-tier)→M4(運用)の4フェーズ・要承認。
- **②P1 創発の後付けテキスト検出**(Opus実装・Fable検収8テスト緑): scripts/detect_emergence.py=fiction(実在名
  WL2780件と照合)/norms(規範発話)/attention(共伝播・coined分離)。**初回観察: 架空イベント「ボードライブ」を
  12人が105回共有**(虚構の共有現実の芽)・架空スローガン「韓語とコーヒーの交差点」3人・語形ドリフト
  「資生堂パーラー→パーリー」伝播・規範発話9件(wv_llm_7d)/38件(daily_llm_20a7d)。
- **②P2 SNS架橋距離**(Fable直轄=scheduler中核): sns_geo.enabled(既定OFF)でSNS/DM伝播のtransmission
  payloadに送り手との物理距離dist_mを追記(_hear_words内で算出・乱数呼数不変・OFFバイト一致)。
  scripts/analyze_bridging.py+tests/test_bridging.py 5本緑。実データ(30体1日mock): SNS伝播153件全てに記録・
  平均365m・**500m超の遠距離架橋27%**=SNS有無A/Bの被説明変数の器が完成。
- **③P3 ペルソナ深さ属性=不採用**(ユーザー委任判断・legacy-adoption.mdに記録): (a)manifold collapse診断に抵触
  (b)既存較正・k実験系列の比較可能性を破壊 (c)全プロンプト+200字=最小推論量に逆行 (d)生成の非決定化。
  再訪条件=内省改善後も多様性頭打ち+50人A/Bで悪化しない見込み。
- **④abliterated取得**: セキュリティ4連検証(発行元評判/レジストリのmanifest+template+params層のダウンロード前
  直接検査=標準qwen3テンプレと同一・注入なし/ollama CVE照合=0.31.1>0.17.1でCVE-2026-7482修正済/取得後digest・
  modelfile照合一致)→pull完了。**1日スモーク合格**(15体seed7・daily.yaml): 188呼エラー0・日本語率0.88(instruct
  0.87と同等)・written_back 14/14・distinct-2 0.136(instruct 0.173=やや定型化強め、4セル解釈時に注意)。
  **model×k対照4セル(15体×2日×{instruct,ablit}×k{free,off})は実行可能状態=ユーザー承認待ち**。
- **検証**: test_bridging 5本+test_detect_emergence 8本+golden/contracts 10本 全緑。フルスイート退化検査
  **584本全緑(31分57秒)**=P2のエンジン変更による退化なし。

---

### Entry 9 — 2026-07-12 — 第23バッチ: マルチLLM/API対応の実装(M1-M2)・agent-LOD討議資料・判断待ち説明書(Fable計画/Opus実行)
- **依頼**: ①4セルラン=保留(シミュはまだ回さない) ②複数ローカルLLM・API対応は実装可、**エージェントLODは実装せず討議資料化**(ユーザーとFableで深く議論したい) ③判断待ち2件(production.yaml reflect_think/k再検証)をユーザーが把握できる文章に。
- **M1-M2実装**(Opus: llm/新規3+tests2+CLI、Fable: simulation.py配線+config.yaml):
  - llm/openai_compat.py(OpenAI互換chat/completions=OpenAI本家・Gemini互換口・ollama互換口・llama.cpp を1実装で)
    /llm/anthropic.py(Messages API・**temperature/seed送らない**=現行世代撤廃済み)/llm/router.py(purpose別dispatch・
    default必須・agent_tierはValueErrorガード・calls/hits をid()重複排除で集計)。
  - 配線: `model.backend: router` 分岐。**子を各自 CachedLLM で包む**(routerごと包むと name="router" でモデル別
    キーが潰れる=D13違反。キャッシュは llm_cache.<子name>.jsonl に分離・同一specの子は共有)。
    APIキーは環境変数名のみ config に書く(値はコード・conf・ログ・キャッシュに置かない=ODPT規律)。
  - **検収で実バグ1件発見・修正**: ollama互換口のqwen3は思考制御不可(2507系は/no_thinkソフトスイッチ廃止)→
    思考がmax_tokensを食い尽くし**content空**(reflect_think飢餓と同族)。openai_compat に「空content=
    __api_error__(成功扱いにしない)」の防御を追加し、ローカルqwen3はネイティブollama.pyを使う旨をdocstringへ。
  - テスト: 単体21+空content1+配線結合3(router(mock子)=素mockと**L1バイト一致**・呼数一致・default欠落
    ValueError・キャッシュファイル分離)。実LLMスモーク: router{default: ollama qwen3:4b}で5体12step完走・
    llm_cache.ollama_qwen3_4b.jsonl 生成確認。手動疎通CLI scripts/check_llm_backends.py(実API不使用・課金ゼロ)。
- **agent-LOD討議資料**(Opus: docs/research/agent-lod-deepdive.md 189行): 用語整理(発火LOD=実装済み・
  purpose LOD=M2で器完成・個体軸LOD=未導入が主題)。先行例=AC Unityの群衆LOD(背景個体のidentityを捨てる=
  **k*の測定単位を捨てられない我々には半分しか来ないタダ飯**)・The SimsのStory Progression(trait条件付き背景=
  **生得性裏口の完成した実物・避けるべき教科書**)・交通micro/meso境界整合・平均場。討議アジェンダ5問
  (誰のk*か/背景から世界改変者が出る経路/trait裏口+計算量そのものの交絡/動的昇格と決定論/どの規模から要るか)。
  事実の示唆: **300体では発火LOD(12倍削減済)+purpose LOD+Tier1タダ飯で足りる公算大**。個体軸LODは3k-10k規模の後段レバー。
- **判断待ち説明書**(Fable: docs/plans/pending-decisions.md): reflect_think の経緯と選択肢(推奨=production.yaml
  に1行)・k再検証の理由(パイロットの+0.12/+0.18はbelief死亡状態の測定)と**「4セルのinstruct側2セルが再検証を
  兼ねる」**一括実施の推奨・その他承認待ち一覧表。
- **検証**: 新規テスト25本+既存ガード全緑。フルスイート **609本全緑(34分02秒)**=配線変更(mkdir前倒し・
  raw is not None ガード)による退化なし。
