# 開発ログ(ライブ)

> このプロジェクトを「作る側」の意思決定・節目の記録。シミュレーション内部の観測層ログとは別物。
> **プロトコル**: ユーザーとの1往復ごとに1エントリ追記。エントリが10に達したら圧縮して [devlog-compressed.md](./devlog-compressed.md) へ移し、本ファイルをリセット。設計の正典は [../design.md](../design.md)。
> **圧縮履歴**: devlog-compressed.md(Block #0: プロトコル前史 / #1: ログ機構〜分野1-3 / #2: リサーチ完走〜決定アジェンダ / #3: D0-D17決定→P0実装→世界v2-v5 / #4: 生態系→docs完遂→現実ギャップ全波→第9バッチ / #5: ODPT実ダイヤ→制度深化完遂→自己モデル→現実較正→実LLM初証拠→日常プロファイル(第10〜14バッチ) / #6: 開放行動→世界解釈の観察→マルチモデル対応(第15〜24バッチ) / #7: 復元→git化→入力解像度LOD→分析スイート→制約デコード→自由度P2(第25〜34バッチ) / #8: EnvPack→PLATEAU実形状→第37バッチ6トラック→現実スケール転換(第35〜38バッチ) / #9: 同時滞在実測→全員思考転換→行間レイヤS1-S5(第38バッチW2) / **#10: W2完結→視覚F→オントロジー多軸→物流・乗れる交通→並列ゲート(第38W2後半〜第43バッチ)**)。全文アーカイブ: devlog-block6-fulltext.md / devlog-block7to9-fulltext.md / devlog-block10-fulltext.md。

**ライブエントリ数: 4 / 10**(Entry 40 から=継続採番)

---
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
