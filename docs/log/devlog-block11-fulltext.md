# devlog Block #11 全文アーカイブ(Entries 40–49・2026-07-21 〜 07-24)

> devlog.md のライブエントリ10本到達に伴う圧縮時の全文退避。要約は devlog-compressed.md の Block #11。

### Entry 40 — 2026-07-21 — run.start_tod着地=コールドスタート完全解(1306緑・並列ゲート3:13)
- **start_tod**(Opus実装・Fable検収・コミット本件): Clock start_min の一点配線+開始時刻仮定の
  全数監査(修正=Clock既定/simulation生成/world events逆算の3箇所・検証=day境界/presence/resume/
  checkpoint/時刻機構は sim_min 由来で自動一般化)。day=「開始起点の経過simulated day」規約を明文化。
  OmegaConfの60進coercion対策(引用符+頑健parser)。**00:00開始+natural_start=初日朝計画0→19/20
  (95%)の実証**=統合リハーサルで発見したコールドスタートの完全解。既定07:00=バイト一致。
- 並列ゲートの実効: 1306本を**3分13秒**(同期実行可能に=バックグラウンド待ち自体が不要化)。
- 残(小・cosmetic): viz/make_viewer の壁時計表示が07:00固定=非07:00ランでラベルずれ(エンジン無関係)。
  分析系の step//144「活動日」規約は00:00開始でエンジンdayと一致。

---
### Entry 41 — 2026-07-22 — 第44バッチ: 関係性S-R1+S-R3着地(世帯の現実化+共同行動エンジン・1321緑)
- **S-R1 世帯の現実化**(household.py拡張・新キー realistic 既定false=現行束ねとバイト同一):
  渋谷実数の size_weights_realistic(単身64.5%=令和2国勢調査)+(地理×年齢)整合束ね+続柄
  household_role(2人=年齢近接の夫/妻・3-4人=年長2人が親/年少が子・同性/不明は同居人)。
  context_line が続柄を具体化(「夫の○○」)。**夕食の共食** family_dinner(prob 0.69=農水省食育調査・
  18-21時帯に世帯homeへ収束=date_dest同型・新stream "dinner")。
- **S-R3 共同行動エンジン**(新規 src/society/joint.py=検査外・新トップレベル joint: 既定OFF):
  友人(relations tier≥2)/同居人と**外食・カフェ/映画/カラオケ/買い物**。日次編成(新stream
  "joint"・(agent,day)個体別キー=編成順非依存)→誘い→承諾(base0.5+親友bonus0.3)→ランデブー
  POI((グループ最小id,day,活動)純関数=date_destの一般化)→band内の行き先収束→**実同席の最初の
  stepで joint_activity 1件**(1グループ1日1回・S-R1夕食と共用)。重みはレジャー白書較正
  (外食39.2>映画33.7>カラオケ20.2)+年代倍率(渋谷若年=友人遊び高)。休眠だった計画の同伴者
  `with` を初接続(名前→closeness最大の決定論解決・追加LLM呼ゼロ)。meal_cafe は activity=eating で
  既存 _charge_meal 課金に自然接続。R1=compute_matched 下の k 不変(co-location変化系の正契約)。
- **viewer壁時計のstart_tod追随**(並列小粒・1a76bca): sim_min列から原点復元→--start-tod明示上書き
  →既定07:00の3段priority。07:00ランはバイト同一(sha256検証)。
- 検収: 対象27本+viewer47本を自前再実行→**フルゲート1321本green・3:42**。コミット dcb6e37/1a76bca。
- 較正メモ: family_dinner.prob=0.69 は統計上「日単位の共食率」だが実装は帯内毎stepバイアス=実効
  日次率は高めに出る(joint_activity 実測→calibrate で調整可。機構は正)。同性2人family世帯の続柄は
  同居人へ後退(正直な簡略化)。残スライス: S-R2友人グラフ(homophily)・S-R4職場会食(階層依存)・
  S-R5来街者party(party_size実体化)。

---
### Entry 42 — 2026-07-22 — 第45バッチ: 関係性パッケージ完結(S-R2/S-R4/S-R5)+語彙伝播の可視化(1340緑)
- **S-R2 友人グラフ**(新規 friends.py・新ブロック friend_graph 既定OFF): homophily(McPherson=
  年齢>職業)+共有所属(同work org=34.0%・学生同士=31.6%)+同住建物近接をスコア化し、Dunbar層
  (親友3-5=tier3/友人7-12=tier2/知人20=tier1)の次数で relations closeness/tier へ直接注入
  (二重辺は代入で防止)。**乱数streamゼロ=(pidペア,seed)のblake2b純関数=run.seed非依存**
  (比較実験の要。地理項のみ直接ランでrun.seed感応=名簿+w_same_area=0で厳密実証)。観測kind
  friend_graph_built{n_edges,mean_degree}。
- **S-R4 職場会食の階層依存**(joint.py拡張): activities に companion_type(friend/housemate/
  colleague)+hierarchical を追加、accept_prob = base+tier_bonus−hierarchy_penalty(0.35)。
  組織台帳に役職(rank)データ無し(org_role=職種名)→**上司判定は年齢差>10歳の代理指標**と正直に
  明記。colleague_lunch(0.02)/colleague_dinner(0.03・hierarchical)は**コメントアウト同梱**
  (activitiesマップに足すと語順=POIハッシュが動くため既定4種を保護)。
- **S-R5 来街者party実体化**(新規 party.py・新ブロック party 既定OFF): プール未使用だった
  party_size(1-5)を初使用。present判定の**後**にid昇順グループ化=同一初期ノード・相互relations
  (tier2/closeness5.0)・共有回遊POI(party_dest・新stream "party"・帯10-22時)。presence純関数
  無風=test_pool_rotation(resume バイト一致)green。観測は joint_activity{type:"party"} 再利用。
- **語彙伝播の可視化**(aba9ec0・viz のみ・ユーザー要望「どのように語彙が広がっていくのか」):
  L1に全データ実在(vocab_coin+発生文脈context/transmission{from,channel}=聴取1辺ごと/
  label_adopt)。build_data に trans[[step,from,to,channel]]+ctx+caps(1語2000辺・採用者の
  第一聴取辺を最優先で残す決定論間引き=実測で採用者270人全員生存)。💬語彙タブ=語クリック→
  採用曲線(s0連動)+伝播ネットワーク(黄金角スパイラル・チャネル色分け=対面緑/DM桃/SNS青/
  メディア琥珀)+伝播ログ(🌱誕生行に発生文脈)。地図に「語彙(語別)」mode=採用済濃/聴取済中間/
  未接触灰=時間スライダーで街への広がりが見える。
- 検収: 対象34本自前→**フルゲート1340本green・3:57**。コミット 1043bbb(関係性)/aba9ec0(語彙viz)。
- メモ: friend_graph の acq_extra=20 は小集団では密(スケール前提較正)。colleague系の有効化は
  organizations.enabled=true が前提。関係性パッケージ(S-R1〜S-R5)これで完結。

---
### Entry 43 — 2026-07-22 — 第46-49バッチ: 自走キュー完走(経済①-⑤完結・v-Ride-2/3・職場束ね直し・1391緑)
ユーザー指示「次の実装に進もう。最後まで通していい」で4バッチを順次自走(Opus実行/Fable検収・各バッチで
フルゲート+コミット)。
- **第46(fdf8c82)経済③+⑤**: services.py=サービス実体6種(理美容/任意受診/塾/ジム/クリーニング/汎用・
  滞在+課金+効果hook on_service[mood/vitality/learning→不透明magnitude]・新stream service・k不変273一致)。
  b2b.py=補充供給元を卸orgへ内生化(最寄り決定論選定・生産→org在庫→仕入=金+物の保存則テスト・
  卸枯渇=補充失敗の欠品波及=供給網雪崩の観測基盤・乱数ゼロ)。現行地図のservice POIは70件
  (1,994件は広域地図由来)=名ヒント特化は疎・データ駆動でPOI増に自動スケール。
- **第47(bf1b9c9)経済④宅配**: delivery.py=注文(食事帯在宅・外食代替=二重課金なし・新stream delivery)
  →在庫減→最寄りgig配達員を決定論配車(実体は物理移動・不在は抽象トリップgraceful)→到着課金+gig収入。
  会計恒等式(注文者支出=店売上+配達員収入+手数料)をテストで検証。**経済スライス①-⑤全完結**。
- **第48(2d13d83)v-Ride-2/3**: bus_table.py+build_bus_table.py=GTFS→静的表(停留所/系統/発時刻/累積所要)
  →実ダイヤ近似乗車(待ち+区間所要→到着hold量子化=taxi-live同型)。**実GTFS未fetch=正直記録**
  (匿名403・キー404・ckanはHTML=手動DL→build_bus_table.pyで即機能)。合成GTFS(中立名)で全経路検証。
  相乗り=自前決定論greedyShared(同方向内積+回り道上限1.4・束ごと1予約=SUMOに真の相乗りは委ねない)・
  並行配車=id昇順。SUMO実走テストも通過。
- **第49(166a697)職場束ね直し**: pool L2のwork_node穴(occupation∉_WORK_CAT=serve/org_output/colleague
  から漏れ)を2段束ね=①org_id→台帳workplace_poi.node直束ね ②地図に無い/org無しは決定論POIマッチ
  (hashlib純関数・run.seed非依存・乱数ゼロ)。present L2の職場保有**17/57→57/57**。hydrate再入同一・
  rotation resumeバイト一致。既定地図は台帳ノード4014/11000のみ=多くはカテゴリ近似(wide地図で全直束ね)。
- **統合スモーク**(mock 144step・新機能ON): 完走23,545イベント・joint_activity 19・friend_graph_built・
  service_use・partner_formed発火。宅配は率を上げた確認ランで注文12→配達12全件成立。b2b/restockの0件は
  前提疎(org従業者=personas_file要/1日では発注点未達)=各専用テストでE2E検証済みの正常挙動。
- ゲート推移: 1370→1382→**1391本**(全バッチgreen・3分強/回)。全既定OFF=ゴールデンL1バイト一致維持。
- 残(ユーザー/環境待ち): ビューア目視(語彙タブ)・実バスGTFS手動DL・P7本選ベンチ・LLM上塗り(D7)・
  family_dinner/daily_rate等の較正(calibrate実測後)。

---
### Entry 44 — 2026-07-22 — 実装総覧ドキュメント作成
- ユーザー要望「今までの実装を文章にまとめて」→ docs/implementation-summary.md(a0ac7de)を新規作成。
  14章構成: 目的と問い/R1ドクトリン/世界(渋谷再現)/人(プール100万人)/認知(LOD+行間S1-S7)/
  内面/社会(関係性S-R1〜R5・制度)/オントロジー多軸/経済①-⑤/交通(乗れるタクシー・バス)/
  観測と可視化(語彙伝播含む)/実験プロトコル/倫理・セキュリティ/現在地と残り。
  設計正典(design.md)・devlog圧縮履歴・直近バッチ報告から集約。数値は実測値のみ(1391緑・
  17/57→57/57 等)・未達事項(実バスGTFS未fetch等)も正直に記載。

---
### Entry 45 — 2026-07-23 — 外部アドバイス由来6タスク案の精査(実装前レビュー)
- ユーザー持込の実装案(価値3分類/3M欲望/不確実性・運/自助努力/spark介入/信用可視化)を
  コード照合で精査。**翻訳方針(observable/affordance/treatment化)はプロジェクト方針と完全整合**。
- 主発見=重複3件: ①タスク1の価値3分類は **values.py(第17バッチ)が既に実用/感情/社会+認識の
  4軸を実装済み**(『世界2.0』3分類が出発点・TAGS=utility/emotion/social/epistemic)→新規でなく
  「全イベント種への拡張+L2/ダッシュボード集計」として実装すべき。②タスク6の信用スコアは
  **status.py(第11バッチ)の合成地位スコアがほぼ同物**(評判/フォロワー/資産/制度実績/商い/主催の
  百分位blend)→内訳・Gini・地位相関の観測拡張のみが新規。③タスク3の運/実力分解は
  **measure.py の OLS R²(Y~traits)の自然拡張**=既存分析スイートに残差分解を足す形。
- 修正提案: 住民ごと時系列はL2でなく事後分析層へ(人数>時間)/T1・T2・T6は共通レンズ機構1本で/
  spark選抜の既定は**trait-blind純関数**(trait狙い撃ちはk*研究の交絡=別条件として明示時のみ)/
  sparkのdecayはメニュー別に意味を定義((a)(b)=初期条件一発・(c)アンカーのみ減衰)/イベント毎の
  sparkタグでなく名簿イベント+transmission追跡の事後トレーサ。
- 計画: 第50バッチ(レンズ=T1+T2+T6+viz)∥第51(T3監査+運実力=scripts/docsのみ=並列可)→
  第52(T4自助努力)→第53(T5 spark+D13追記)。実装はユーザー承認後。

---
### Entry 46 — 2026-07-23 — 第50-54バッチ: アドバイス翻訳5本+不確実性モード完走(1474緑)
ユーザー承認(バッチ間許可不要・昼まで)で5バッチ連続自走。Entry 45 の精査どおり「重複3件は既存拡張」
「spark=trait-blind既定」「住民別は事後層」で実装。
- **第50(fd32dca)観測レンズ3本**: 新規 observer/lens.py=kind→軸のデータ駆動2段マッチ共通機構。
  T1価値4軸(values.TAGS正準を再利用=新分類なし)・T2 3M欲望(earn/love/recognition・love軸の疎と
  理美容代理の判断を正直註記)・T6信用内訳(status.material_breakdown純関数追加=新スコアなし)。
  L2は全体スカラー9列のみ・住民別/遷移/シフトはviewer build_dataの事後計算。ダッシュボードに
  価値/欲望/信用タブ(データ有時のみ注入=既存ランバイト同一)。行動への逆流ゼロ(lens OFF==ON L1不変)。
- **第51(5248109)不確実性監査+運/実力**: named stream約60本を全数列挙・機能分類。mock実測=
  想定外5.24件/人日・96.2%遭遇・揺らぎは全イベントの1.7%。**運/実力分解(既存OLS資産再利用)の発見:
  関係=運ΔR²0.19>実力R²0.17(寄り道が出会いを生む既存主経路)・収入=実力0.75/運0.001(職業構造が
  ほぼ決定)**→第54の較正の狙い所を定量特定。LUCK_KINDS共有表にchance_event受け口。
- **第52(727031a)自助努力affordance**: agent.self_dev(経験由来・states監査外)。塾→skill・ジム→fitness、
  累積 gain/(1+x)=練習冪乗則+日次減衰で有界均衡。経済経路は_pay_wage単一点×(1+coef×skill)の
  1本のみ(既定coef=0=会計不変・fitnessは観測のみ)。k呼数一致・resume自動保存。
- **第53(54595c0)spark treatment**: 新規spark.py。**trait-blind純関数選抜**(traits全面改変・run.seed変更
  でも名簿不変をテストで実証=生得vs創発への交絡ゼロ)。3メニュー=(a)初期関係束(friends._inject流儀)
  (b)資本・在庫上乗せ (c)集会アンカー(bias×exp(-decay·step)=(a)(b)はt0一発・減衰は(c)のみ)。
  spark_roster 1件+事後トレーサtrace_spark.py(sparked発transmissionのBFS波及・活動量比)。D13追記
  (縮退既定=OFF・純観察優先)。
- **第54(27095dd)不確実性モード**(ユーザー追加要望「再現性 vs 純観察の選択」): 決定論エンジンは不変の
  まま3本柱=①chance.py偶発層(windfall/loss/encounter・(agent,day)個体別stream "chance"・効果は
  money/relations/記憶のみ=発火非接続・encounterのclose1.5は第51の「関係=運」主経路へ、金額帯は
  収入の運無感応ギャップを埋める設計レバーと明記)②run.seed=auto/seed_auto=OSエントロピー採取+
  config/summary記録=**「選ばないが失わない」**(採れたseedで再実行=バイト再現をテスト済)
  ③conf/observe.yaml観察プロファイル(chance/確率的実行/退屈/天候/関係を束ねON)。LUCK_KINDS
  1行接続で運/実力分解が自動で拾う。D14追記(縮退既定=再現性実験モード)。
- ゲート推移: 1435→1448→1463→**1474本**(全バッチgreen・3分強/回)。全既定OFF=ゴールデン維持。
- 検収条件5項目(OFFバイト一致・compute_matched・no-fingerprint・ダッシュボード目視可・devlog記録)
  すべて充足。アドバイス→observable/affordance/treatment翻訳の設計判断はEntry 45+各コード註に記録。

---
### Entry 47 — 2026-07-23 — 閉じた世界・日常観察方針の精査(実装前レビュー)
- ユーザー持込 docs/closed-world-daily-observation.md(世界2.0フレームの外部アドバイス検討まとめ+
  新タスクA/B/C)をコード照合で精査。**設計判断の記録**: 閉じた世界+ペルソナ維持(組織形成の再現に
  積極的に適合)・危機トリガー不採用(=指紋。日常からの創発かの区別を守る)・日常スケール観察を軸に。
- 整合確認: (1)「日常は既に揺らぎに満ちている」は**第51監査が定量裏付け済み**(想定外5.24件/人日・
  96.2%遭遇・関係=運が主経路)。(2)§2.1 spark縮退は**ほぼ充足済み**(第53実装が既定OFF・D13縮退既定=
  OFF・純観察優先)=D13文言の微修正のみ。(3)タスク1〜4・6は第50〜52で実装完了済み。第54の
  observe.yaml も日常観察方針とそのまま整合。
- 新タスクA/B/Cの精査: A(ペルソナ逸脱率)=実装可・**逸脱は自由裁量時間に限定して測るべき**
  (義務ルーチンはペルソナ由来=従順度を水増しする)・住民別はL2でなく事後層(確立済み方針)。
  B(内生変動)=Louvainでなく**既存の決定論コミュニティ検出を再利用**(新依存なし)・日次churnスカラーは
  in-sim、順位相関(Kendall τ)・固着検知は事後層(L3スナップ活用=シム側に前日状態を持たない)。
  C(30日ラン)=resume分割は既存バイト一致保証で可・**ビューアの長期ラン軽量化(間引き/週次ロール
  アップ)が必要**・実行時間/ストレージ見積もりベンチ込み・D15追記。
- 計画: 第55バッチ(D13微修正+タスクA)→第56(タスクB)→第57(タスクC+D15)。実装はユーザー承認後。

---
### Entry 48 — 2026-07-24 — 第55-57バッチ: 日常観察方針タスクA/B/C完走(1520緑)
閉じた世界・日常観察方針(Entry 47精査済み)の新タスク3本を連続自走(Opus実行/Fable検収)。
- **第55(2785c9f)タスクA ペルソナ逸脱率**: observer/deviation.py。**裁量時間限定が主軸**=初回実測で
  裁量0.333 vs 全時間0.119(義務ルーチンが従順度を約3倍水増しする構図を実証=精査条件の正しさ)。
  構造化軸のみ(職業→趣味期待POI)・自由文性格/traits/ontology群は比較不能と正直に対象外。
  L2全体4列・🎭逸脱タブ(分布/裁量vs全時間推移/最逸脱者ドリルダウン)・deviation_meanをsweep接続
  (k関係の材料)。D13文言を「spark既定で回さない・日常ベースライン優先」に整合。
- **第56(8ccde6b)タスクB 内生変動**: observer/structure.py=当日イベントのみのedge churn 4列
  (形成=tier1到達/断絶=break非absence/風化=absence/率。**前日状態をシムに持たない**)。
  analyze_structure.py=Kendall τ順位固着・中心性turnover・コミュニティ変化(**Louvainでなく既存の
  決定論LPA=measure.communities再利用・新規依存ゼロ**)・3信号の固着期間検知(観測記録=介入なし)。
  🏛社会構造タブ(固着帯・レースチャート)。L3追記不要とコード実査で確認(L1から完全再構成)。
- **第57(471fd05)タスクC 30日ランプロトコル**: conf/longrun30.yaml(100体・4320step・checkpoint10日
  分割・observe土台+生活機構+観測レンズ全系ON)。**resume結合の最小補修**=logger._resumedフラグで
  「10日×3チャンク各finalize == straight 4320」のl1/l2/l3バイト一致を実証(freshラン完全不変)。
  viewer --daily-rollup=17.9KBの軽量集約ビュー(--thinはstep依存チャート群を壊すため不採用と正直記録)。
  bench_longrun.py 7日実測→30日外挿: mock18分・L1 48MB・RAM 2GB(ckpt分割時)=外挿精度±7%。
  **構造指標の7日検証: 順位τ 0.54→0.88=固着の兆しだが閾値未達=「固着確定には30日級が必要」の
  直接的裏づけ**(D15の判断材料)。D15追記(縮退既定=7-14日短縮・30日は余剰枠)。
- 運用メモ: 第57は「バックグラウンド検証待ち」停止が再発→SendMessageで有界ポーリング・
  フォアグラウンド完結を指示し完遂(既知パターン・agent-operating-mode)。ベンチ初版のtracemalloc
  実時間5倍歪みを子プロセス+working-set測定に是正(正直な実測)。
- ゲート推移: 1495→1513→**1520本**(全green)。全既定OFF/既定不変=ゴールデン維持。
  closed-world-daily-observation.md の実装タスクはこれで全完了。

---
### Entry 49 — 2026-07-24 — 第58バッチ: マクロ⇄ミクロ・シームレスズーム観察 B0-B9 完走(1626緑)
ユーザー要望: 会社ごと・建物内の人の動きなどミクロ視点の観察を、マクロと切り離さず「マクロを注視
したらミクロが現れる」形で。計画リサーチは論文深掘り必須。実装開始時に方針3点追加: ①間取りは
できるだけWeb実データ ②ミクロ重視=マクロはミクロの結果から生じる ③step10分はLLM節約都合=物理は
見直し可・ただし計算増に見合う情報を。体制: Fable計画/検収/コミット・Opus実行(5コミット
bd53078→bcbc1b9→32971a0→119adf2→380413e)。
- **設計原則(論文基盤)**: 屋内ミクロ状態を単一の真実としてシムが全建物で常時決定論保持・マクロは
  常にその集約・ズームは表現の切替(Davis&Hillestad/Reynolds のマルチレゾリューション整合・
  Pad/Shneiderman セマンティックズーム・Helbing SFM・LBNL在室ABM・Lopes間取り生成)。観察対象を
  選ぶconfを存在させない=観測がシムを変えない構造保証(B9で3点テスト化)。
- **B0**: 公式フロアガイド21棟197階→data/floor_layouts.json(shops79階・店名不記載=ETHICS・出典
  27URL・欠測は欠測のまま)。幾何は非公開=手続き生成へ実データ制約(区画数/用途構成/アンカー)を渡す分担。
- **B1/B2**: vision.py休眠資産を正典昇格(n_override=POI経路同型で乱数消費不変・doors_from_layout)・
  IndoorSpace(SpaceType=conf型優先順位表=コードに業種名なし)・SFMコアをviz→world/sfm_core逐語移設
  (既存28テスト無修正緑)・WallCrowd=壁斥力Helbing2000+ドアウェイポイント+BFS退避+接触ペア抽出。
- **B3**: _phase_indoor(区画割当/フロア内Markov/階間実軌跡=draw順不変/会議(group,day))・2層タイム
  ライン=認知10分不変+物理dt0.2sサブステップ(遷移駆動=常時ミリング不採用)・遭遇はsim一時状態→
  観測が読む一方向・tracksサイドカー・LLM呼数41=41一致。24step100体 OFF2.0s→ON30.4s=SFM支配。
- **B3b**: 遭遇→返答相手優先(phase順実測に基づく1-stepラグ・per-agent属性でresume==straight)・
  VisionOccluder初配線=同席文脈の壁LOSゲート。会話発生数・呼数不変=相手だけ変わる(co-location契約)。
- **B5-B8**: 2Dセマンティックズーム(cam.s≥2.6で間取り平面クロスフェード+実座標+階チップ+遭遇
  パルス・旧ランHTMLバイト同一3層証明・JS側n_overrideパリティ実21棟一致)・3D接近フェード+フロア板
  LRU8棟・serve org_id(多義ノードnull=unknown率89%正直開示)・org_ledger.parquet日次サイドカー・
  agents.json org_id欠落バグ発見修正・🏢会社タブ(org card=L1検算固定)・🏙在館タブ+build_occupancy。
- **B9**: 観察不変性3点テスト化(tracksトグルL1バイト一致/事後処理無影響/動力学がobserver読まない
  機械検査)・SFM較正=推奨msub300+samp10(時間−24%軌跡−78%・dt増は遭遇偽増で不採用・既定変更は
  ユーザー判断待ちでコメント記載)・7日40体実測307s→30日100体外挿=屋内+65min/追加5MB級・resume
  3日4系列バイト一致・D16追記(本選での屋内ON判断)。
- 運用: B3b/B5/B6がサブ側セッション制限で中断→SendMessage再開で完遂(既知パターン)。B5製テストの
  自己参照設計(コミットでHEAD側にトークン混入し恒久赤化)をFableが自己完結不変量へ補修。
  ゲート1520→1545→1553→1589→1622→**1626**(全green・全既定OFF=ゴールデン維持)。
