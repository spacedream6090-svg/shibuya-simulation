# エンジン被覆マップ(現実再現エンジン群 × 実装 全数照合)

作成: 2026-07-14。目的: ユーザー提示の「現実を再現するためのエンジン群」分類リストに対し、
本シミュレーションに**既にどのエンジンが実装されているか**をコード根拠つきで全数照合する。

- 照合対象コード: `conf/config.yaml`(全機能ブロックの索引)/ `conf/daily.yaml`・`conf/production.yaml`
  (本番プロファイル=既定ONの実体)/ `src/society/`(engine/ cognition/ world/ factors/ observer/
  llm/ と直下モジュール群)/ `docs/plans/unimplemented-inventory.md`(計画済み未実装)/ `README.md`。
- 誠実性の約束: 存在しないものを「ある」と書かない。確認できなかったものは「未確認」と明記。
  各行に根拠ファイルパス(行番号なし)を付す。推測で被覆度を上げない。
- 被覆度の凡例:
  - **◎ 完全** = 独立モジュール + config ノブ + 専用テストあり
  - **○ 実装あり(部分的)** = 実装はあるが、構成要素の一部のみ / 別機能に相乗り
  - **△ 萌芽** = 関連コード・イベントはあるが専用機構が無い
  - **× なし** = 実装なし(または明示的に「作らない」と決定済み)

重要な前提(既定ON/OFF の読み方): 基底 `conf/config.yaml` は**再現性のゴールデン基準**として
大半のリアリズム機能を既定 OFF に固定してある(バイト一致を守るため)。現代生活の再現は
`conf/production.yaml` / `conf/daily.yaml` が `OmegaConf.merge` の差分上書きで ON にする。
よって本表の「既定ON/OFF」は原則 **基底=OFF・本番=ON** の二層で書く。

---

## 1. Human 層

| エンジン | 被覆 | 実装の在り処(モジュール・config・代表イベント) | 既定ON/OFF | ギャップ |
|---|---|---|---|---|
| Reasoning(推論) | ◎ | `src/society/cognition/deliberate.py`(build_prompt→LLM→parse_action)。config `model`。イベント `llm_deliberate` / `fallback`。テスト `tests/test_conversation.py`・`test_e2e_mock.py`・`test_contracts.py` | ON(LLM発火経由) | 推論は LLM 内部にありコードで構造化されない=思考連鎖の可観測性は JSON 出力のみ |
| Memory(記憶) | ◎ | `src/society/agents/memory.py`(3層: buffer/episodes/beliefs + relations台帳、GA型 push 想起 recency:relevance:importance=0.5:3:2)。config `memory`(agentic_pull/relations_max)。イベント `reflect`(consolidate)・`memory_recall`。テスト `test_memory.py`・`test_memory_pull.py` | push常時ON / pull OFF | 埋め込み検索なし(文脈語包含で近似)。長期意味記憶は beliefs のみ |
| Planning(計画) | ◎ | `src/society/cognition/planning.py`(朝の一日計画 make_plan)。config `planning`(enabled: true)。イベント `day_plan`。テスト `test_planning.py`・`test_plan_tokens.py` | ON | 計画は1日粒度・行き先の土台のみ。多階層プランニングなし |
| Goal(目標) | ○ | `src/society/inner_life.py`(goals=価値/traits から長期目標を決定論導出しプロンプト注入)+ 欲求ゲージ(短期)。config `inner_life.goals`。イベント `long_goal`。テスト `test_inner_life.py` | 基底OFF / 本番ON | 目標は決定論生成の1行で、LLM 自身の自律的目標形成・目標追跡はなし(現状は1日計画のみに作用) |
| Emotion(感情) | ○ | ベースライン: `src/society/factors/mood.py`(states→気分文、常時注入)。拡張: `factors/affect.py`(arousal 覚醒度)+ `inner_life.py`(離散感情ラベル)。config `affect`・`inner_life.emotion`。イベント `affect_update`・`emotion_label`。テスト `test_affect.py`・`test_inner_life.py` | 気分文=常時ON / arousal・ラベル=基底OFF・本番ON | 感情は core affect(valence×arousal)の低次元。感情の対人伝染は heard_valence 経由のみ |
| Personality(人格) | ○ | `src/society/factors/registry.py`(TRAITS=nfc/risk_tolerance/internal_locus の**3特性**)+ `agents/persona.py`。config `factors.threshold_dist`。イベントなし(trait は DATA=no-fingerprint 原則)。テスト `test_personas_gen.py`・`test_contracts.py` | 常時ON(trait 常時サンプル) | Big Five ではなく3特性。人格は不変(発達・変化なし)。engine は因子名を見ない設計 |
| Relationship(関係) | ◎ | `src/society/relations.py`(closeness/tier/評判/派閥)+ `agents/memory.py` relations 台帳 + `net` フォローグラフ。config `relations`。イベント `relation_tier`・`relation_break`・`reputation_update`。テスト `test_relations.py` | 基底OFF(count ベースの間柄行のみ) / 本番ON | ネガ/ポジ符号での増減。深い分極(faction 対立)は軽量止まり |
| Learning(学習) | ○ | 内部状態学習: `cognition/reflection.py`(belief 書き戻し=k)+ `opinion.py`(FJ 意見更新)+ `labeling`(語の採用=complex contagion)。イベント `reflect`・`opinion_shift`・`label_adopt`。テスト `test_opinion.py`・`test_labeling_open.py` | belief=k条件依存 / opinion=ON | belief/意見/語彙の学習はあるが、**技能(skill)の蓄積機構は無い**(Skill 行参照) |
| Health(健康) | ◎ | `src/society/health.py`(疲労 fatigue・病気 illness・メンタル引きこもり)。config `health`。イベント `illness`・`medical_visit`・`health_update`。テスト `test_health.py` | 基底OFF / 本番ON | 病気は確率発症の抽象モデル。慢性疾患・加齢による健康低下なし |
| Identity(自己同一性) | ○ | `cognition/reflection.py`(深い内省の産物 self_model=自己像/ties)+ implicit_self(無意識の作動自己 Bem)+ persona。config `reflection.deep`・`reflection.implicit_self`。イベント `reflect`(self_model_updated)・`reflection_trigger`。テスト `test_selfmodel.py`・`test_deep_trigger.py` | 基底OFF / 本番ON | 核自己は深い内省の夜のみ更新。アイデンティティ危機・役割葛藤の明示機構なし |
| **Perception-Attention(知覚・注意)** | ◎ | 知覚: `src/society/world/perception.py`(hearers_of=同一文脈・半径内、4チャネル face/sns/dm/search/news)+ `world/vision.py`(壁 LOS 遮蔽)。注意: `factors/affect.py` salience_gate(Cowan 上位K)+ `cognition/lod.py` input_res(解像度LOD)。config `world.perception_radius_m`・`world.vision`・`affect.salience_k`・`lod.input_res`。イベント `hear`・`search`。テスト `test_vision.py`・`test_affect.py`・`test_input_res.py` | 知覚=常時ON / 注意ゲート・LOS・LOD=基底OFF | 注意の容量制約は記憶符号化のみに作用(反応・呼数は不変) |
| **Belief-Worldview(信念・世界観)** | ◎ | `src/society/worldview.py`(C1 期待形成の人出EMA・C2 可制御性・C6 規範予期)+ agent.beliefs(内省の書き戻し先)+ `opinion.py`。config `worldview`。イベント `worldview`・`opinion_shift`。テスト `test_worldview.py` | 基底OFF / 本番ON(beliefs は k 条件依存) | 主観的世界モデルは3成分に限定。因果的世界モデル・反実仮想推論はなし |
| **Language-Dialogue(言語・対話)** | ◎ | `src/society/labeling/`(coin/adopt/transmission、drift、constrained/open)+ `lang/sentiment.py`(日本語感情価)+ deliberate の speak/reply/dm/post + 会話ターン制御(drive.conv_max_turns/cooldown)。config `labeling`・`drive.conv_*`・`opinion`。イベント `speak`・`hear`・`label_coin`・`vocab_coin`・`transmission`・`dm`。テスト `test_conversation.py`・`test_sentiment.py`・`test_sns_social.py` | ON | 新語生成の自然観察は充実。文法・多義性・言語獲得のモデルはなし |

---

## 2. Economy 層

| エンジン | 被覆 | 実装の在り処 | 既定ON/OFF | ギャップ |
|---|---|---|---|---|
| Economy(経済) | ◎ | `src/society/economy.py`(賃金/持ち金/バイト/口座)+ scheduler の `_pay_wage`/`_spend`/`_phase_daily`/`_phase_accounts_day`。config `economy`(accounts 含む)。イベント `wage`・`spend`・`withdraw`・`rent`・`bankruptcy`。テスト `test_economy.py`・`test_accounts.py`・`test_econ_pressure.py` | economy=ON / accounts=基底OFF・本番ON | 貨幣・賃金・消費・口座・立退き・破産まで。金融市場・投資は無い |
| Consumption(消費) | ◎ | `_spend`/`_charge_meal`/`_charge_ride`(食事/買物/nightlife/交通)+ 動的価格 `commerce.py`。config `economy.prices`・`commerce`。イベント `spend`・`price_change`・`stock_out`。テスト `test_commerce.py` | 消費=ON / 動的価格・在庫=基底OFF・本番ON | 需給連動価格・品切れまで。ブランド選好・消費者異質性は needs 経由の間接のみ |
| Entertainment(娯楽) | ○ | `src/society/media.py`(TV/動画/ゲームのセッション、時間置換)+ net の SNS 閲覧 + leisure POI + tools `host_event`。config `media`・`net`。イベント `media_use`。テスト `test_media.py` | 基底OFF / 本番ON | 在宅メディア消費は年齢・職業別プロファイル。作品内容・娯楽産業の生産側は無し |
| Labor(労働) | ◎ | `src/society/organizations.py`(配属/産出/会計)+ `_settle_work` + `career.py`(失業/転職/再就職)+ institution_routes.labor(労働争議)。config `organizations`・`career`・`institution_routes.labor`。イベント `production`・`study`・`wage`・`job_change`・`unemployment`・`labor_action`。テスト `test_organizations.py`・`test_career.py`・`test_institution_routes.py` | 基底OFF / 本番ON | 雇用・失業・転職・起業転換・労働争議まで。労働生産性の内生成長はなし(org_ledger は集計のみ) |
| Skill(技能) | △ | 登校完遂→`study`(教科名を記録)+ 勤務完遂→`production`。needs.competence(静的な価値次元)。イベント `study`・`production`。学習は belief/opinion 側(Learning 行) | 学習イベントは本番ON | **技能の蓄積状態が無い**。study は教科名の記録に留まり、熟達・スキルツリー・生産性向上に接続しない |
| Innovation(革新) | ○ | 世界改変 affordance: `tools.py`(open_venture=新店舗、propose=新制度、found_group)+ labeling coin_label(新語)+ freedom "do"(開放行動)。イベント `venture_open`・`label_coin`・`proposal`・`free_action`。テスト `test_tools.py`・`test_free_action.py` | tools=ON / freedom=基底OFF | 革新=新店・新語・新制度の創出として存在。R&D・技術進歩・特許の生産関数はなし |
| Resource(資源) | ○ | 貨幣資源: economy money・org_ledger・public_budget・出店売上。観測の Y「資源」層 `observer/measure.py`。イベント `venture_sale`・`public_budget`。テスト `test_measure.py` | ON(合成重みは研究者が事後決定) | 資源プール=金銭・予算・売上。自然資源・原材料・エネルギー収支のモデルはなし |

---

## 3. Information 層

| エンジン | 被覆 | 実装の在り処 | 既定ON/OFF | ギャップ |
|---|---|---|---|---|
| Information(情報) | ◎ | `src/society/net/internet.py`(SNS/ニュース/検索)+ scheduler `_search_index`(世界内検索エンジン、実API不使用)+ `_phone`。config `net`。イベント `sns_post`・`sns_read`・`news_read`・`search`・`world_event`。テスト `test_sns_social.py` | ON | 情報探索・拡散・検索が閉じた架空世界内で完結(再現性のため実 API を使わない) |
| Social Network(社会ネットワーク) | ◎ | net.contacts(対面→フォロー化)+ relations 台帳 + `observer/measure.py` の network_windows / コミュニティ検出。config `net.follow_k`・`relations`。イベント `transmission`・`sns_reshare`・`dm`。テスト `test_communities.py`・`test_bridging.py` | ON | 対面・SNS 二層のネットワーク。Y「network」層で新規関係・到達を計量 |
| Rumor(噂・流言) | ○ | 語の伝播: `labeling`(transmission、complex contagion 閾値2)+ 誤情報 `net/infoenv.py`(misinfo=フェイク/訂正/炎上)。config `info_env.misinfo`・`labeling`。イベント `transmission`・`misinfo`・`viral_cascade`。テスト `test_info_env.py` | 語伝播=ON / 誤情報=基底OFF・本番ON | 噂=語彙伝播 + 誤情報拡散。信憑性評価・訂正の心理は簡易(確率抽選) |
| Media(メディア) | ◎ | net publish_news(公式発表→ニュース+SNS で伝播の根)+ world_events + `media.py`(受け手側)+ recursion impact_news(制度帰結の報道)+ rules 定期イベントのニュース化。config `media`・`net.news_prob`・`recursion.impact_news`。イベント `world_event`・`news_read`・`media_use`。テスト `test_media.py`・`test_recursion.py` | 発信=ON / 受け手メディア=基底OFF・本番ON | マスメディアの発信・受信両面。編集方針・メディア産業の内部構造はなし |

---

## 4. Organization 層

| エンジン | 被覆 | 実装の在り処 | 既定ON/OFF | ギャップ |
|---|---|---|---|---|
| Government(政府) | ◎ | `src/society/government.py`(区/都/国の税・給付・公務員給与・予算)+ scheduler `_phase_government`/`_gov_payroll`/`_gov_benefits`。config `government`。イベント `tax`・`civic_service`・`public_budget`。テスト `test_government.py` | 基底OFF / 本番ON | 3階層の行政・所得税/住民税/消費税・生活保護・公務員ペイロールまで |
| Company(企業・組織) | ◎ | `src/society/organizations.py`(台帳 data/organizations_*.json・配属・org_ledger)+ open_venture(個人事業)。config `organizations`。イベント `production`・`venture_open`・`venture_sale`・`venture_close`。テスト `test_organizations.py`・`test_tools.py` | 基底OFF / 本番ON | 職場実態・産出・会計集計。企業間取引・市場メカニズムは B 段送り(org_ledger は集計のみ) |
| Education(教育) | ○ | organizations の学校 org(persona 大学生・_WORK_CAT education/school)+ 登校完遂 study。config `organizations`。イベント `study`。テスト `test_organizations.py` | 基底OFF / 本番ON | 学校=職場と同型の配属。カリキュラム進行・成績・学習成果の蓄積は無し(Skill 行と連動) |
| Healthcare(医療) | ○ | `health.py` の受診 medical_visit(医療費 spend)+ 医療 POI。config `health.medical_prob`。イベント `medical_visit`・`illness`。テスト `test_health.py` | 基底OFF / 本番ON | 受診と医療費のみ。病院の収容力・治療転帰・医療従事者の稼働モデルはなし |
| Security(治安・警察) | ○ | 執行: scheduler `_phase_enforcement`(警察官が近傍違反者を執行+勾留 detention)+ `diversity.py` 犯罪抑止。config `institution_routes.enforcement`・`society_diversity`。イベント `enforcement`・`detention`・`crime`・`nuisance`。テスト `test_institution_routes.py`・`test_diversity.py` | 基底OFF / 本番ON | 条例執行・罰金・勾留・窃盗/迷惑行為まで。警察組織の指揮系統・捜査プロセスはなし |

---

## 5. City 層

| エンジン | 被覆 | 実装の在り処 | 既定ON/OFF | ギャップ |
|---|---|---|---|---|
| Transportation(交通) | ◎ | `src/society/world/transit.py`(電車 定刻/ODPT実ダイヤ)+ `transit_ride`(タクシー/バス)+ `world/traffic.py`(背景交通 ambient/OD)+ modes(walk/bike/car)。config `transit`・`transit_ride`・`world.traffic`・`world.modes`。イベント `ride`・`traffic_flow`・`move_segment`。テスト `test_transit_ride.py`・`test_transit_odpt.py`・`test_traffic.py` | 電車/タクシー/交通=ON / バス/OD=基底OFF・本番一部ON | 実ダイヤ・実道路網に忠実。GTFS 駅構内高度化は API 待ちで保留 |
| Infrastructure(インフラ) | ○ | `world/map.py`(OSM 実道路網)+ edge_capacity 混雑減速 + `disaster.py` infra_outage(停電/通信断/断水)。config `world.edge_capacity`・`disaster.outage`。イベント `infra_outage`・`move_segment`(congestion)。テスト `test_map.py`・`test_disaster.py` | 道路=ON / 障害=基底OFF・本番ON | 道路容量・混雑・インフラ障害フラグまで。電力/上下水/通信網の常時稼働モデルはなし(障害時のみ表現) |
| Housing(住宅) | ○ | home_building(実在住宅建物への割当 persona.py)+ 家賃/口座 economy.accounts + 立退き `_eviction_bankruptcy_day` + ホテル `lodging.py`。config `economy.accounts`・`lodging`。イベント `rent`・`eviction`・`lodging_checkin`。テスト `test_accounts.py`・`test_lodging.py` | 住宅割当=ON / 家賃・立退き・宿泊=基底OFF・本番ON | 住居割当・家賃・立退き・宿泊まで。住宅市場・地価・売買・引越しはなし(Migration 行と連動) |
| Urban Development(都市開発) | △ | 空間の世界改変: open_venture(新 POI 創出)+ scenario shock_closure(区間封鎖)。観測の Y「spatial」層。イベント `venture_open`・`scenario_shock`。テスト `test_scenario.py` | tools=ON / scenario=実験時 | **地図が時間で変わる再開発機構は明示的に未実装**(`docs/plans/unimplemented-inventory.md` / 各 H 波の注記で「地図が変わる機構は本波では作らない」)。屋台の新設が空間改変の代理 |
| **Space-Map(空間・地図)** | ◎ | `src/society/world/map.py`(OSM 実道路・建物・POI・階)+ `geom.py`・`routing.py`(経路探索)+ `world/vision.py`(LOS)。config `world.map`。データ data/shibuya_osm_wide_v7.json。テスト `test_map.py`・`test_router.py`・`test_vision.py` | ON | 渋谷駅中心の実地図(建物押出し・階・POI・ゲートウェイ)。PLATEAU LOD2 実建物は設計記録のみ |

---

## 6. Society 層

| エンジン | 被覆 | 実装の在り処 | 既定ON/OFF | ギャップ |
|---|---|---|---|---|
| Culture(文化) | ○ | `src/society/annual.py`(文化カレンダー: 正月/ハロウィン/年末、群集)+ labeling(創発的語彙文化)+ tools のグループ。config `annual_events`。イベント `annual_event`・`crowd_surge`。テスト `test_annual_crowd.py` | 基底OFF / 本番ON | 年中行事と創発語彙。深い文化進化(価値体系の世代間継承)は labeling の範囲まで |
| Community(コミュニティ) | ◎ | tools `found_group`/`group_join` + `observer` コミュニティ検出 + relations.faction。config `tools.group_*`・`relations.faction`。イベント `group_found`・`group_join`。テスト `test_tools.py`・`test_communities.py` | ON | グループ結成・加入・検出。オンライン/オフライン混在のコミュニティ形成 |
| Trust(信頼) | ○ | relations の評判 reputation/親密度 closeness/tier + `status.py`(社会的地位)+ opinion。config `relations`・`hierarchy`。イベント `reputation_update`・`relation_tier`。テスト `test_relations.py`・`test_status.py` | 基底OFF / 本番ON | 信頼=評判 + 親密度で表現。制度信頼・一般化信頼(social capital 指標)の直接測定はなし |
| Norm(規範) | ◎ | `src/society/recursion.py`(規範監視→知覚→フィードバック→改変 repeal の閉ループ)+ `rules.py`(制度DSL)+ worldview C6 記述規範 + psych.searle(制度化)。config `recursion`・`rules`・`worldview.norm_line`・`psych.searle`。イベント `norm_digest`・`institution_rule`・`rule_repealed`・`institution`。テスト `test_recursion.py`・`test_rules.py` | rules=ON / recursion=基底OFF・本番ON | 規範の自己観測・制定・廃止の再帰ループまで。逸脱への非公式サンクションは軽量 |
| Creativity(創造性) | ○ | labeling coin_label(新語・constrained/open)+ freedom.open_actions "do"(自由記述行動)+ host_event。config `labeling.mode`・`freedom.open_actions`。イベント `label_coin`・`free_action`。テスト `test_labeling_open.py`・`test_free_action.py` | 語彙=ON / 開放行動=基底OFF | 創造=新語 + 開放行動。芸術作品・創作物の内容生成・評価はなし(自然観察に徹する方針) |

---

## 7. Environment 層

| エンジン | 被覆 | 実装の在り処 | 既定ON/OFF | ギャップ |
|---|---|---|---|---|
| Weather(天気) | ◎ | `src/society/weather.py`(日次決定論生成、季節バイアス、雨天不快感)+ scheduler `_phase_calendar_weather`。config `weather`。イベント `weather`。テスト `test_calendar_weather_commute.py` | 基底OFF / 本番ON | 日次天気・気温・雨天 grievance。局地気象・降水量・時間解像度は日粒度 |
| Disaster(災害) | ◎ | `src/society/disaster.py`(台風/地震/大雪・交通遅延運休・インフラ障害)+ scenario 摂動。config `disaster`・`world.scenario`。イベント `disaster`・`transit_delay`・`infra_outage`・`scenario_shock`。テスト `test_disaster.py`・`test_scenario.py` | 基底OFF / production ON・**daily は OFF**(日常プロファイルは全ショック除去) | 外生ショックとして充実。災害の物理伝播(浸水域・延焼)はモデル化せず抽象 |
| Ecology(生態) | × | 実装なし。`docs/ecosystem-design.md` の「生態系」は**比喩**(ビジネス/社会エコシステム)で生物生態系ではない。grep で ecology/生態の実装機構は不在(household.py が birth/death を**明示的に作らない**と注記するのみ) | — | 生態系・環境収容力・種間相互作用のエンジンは無い(研究目的が人工社会=対象外) |

---

## 8. Time 層

| エンジン | 被覆 | 実装の在り処 | 既定ON/OFF | ギャップ |
|---|---|---|---|---|
| Time(時間進行・ライフステージ) | ○ | 時間進行: `src/society/world/clock.py`(sim_min, 1step=10分, 144step=1日)+ `world/calendar.py`(実日付/曜日/祝日, weekday_work)。config `world.calendar`。イベント `weather`(日付を搭載)。テスト `test_calendar_weather_commute.py` | 時計=常時ON / 暦=基底OFF・本番ON | **時間進行は◎だがライフステージは△**: 年齢は静的で加齢・ライフサイクル進行はなし(100日ラン想定) |
| **Demography(人口統計)** | △ | 人口合成: `scripts/build_personas.py`(IPF 骨格×尺度分布×LLM 文章化)+ 流入通勤者(commute)+ visitor/居住者区分。データ data/personas_*.json。テスト `test_personas_gen.py`・`test_inflow.py` | 名簿ロードで有効 | 静的合成人口 + 通勤流入まで。**出生・死亡・人口移動の動態は未実装**(household.py が childbirth/死別を明示的に作らないと注記) |
| **Tourism-Visitor(観光・来街)** | ◎ | `src/society/diversity.py`(観光客=landmark 回遊 tourist_ratio・多言語)+ visitor ペルソナ + `lodging.py`(ホテル泊)+ 通勤流入。config `society_diversity.tourist_ratio`・`lodging`。イベント `tourist_visit`・`lodging_checkin`。テスト `test_diversity.py`・`test_lodging.py`・`test_inflow.py` | 基底OFF / 本番ON | 観光回遊・非日本語話者・宿泊まで。観光消費の産業連関は economy 一般に相乗り |

---

## 9. Integration 層

| エンジン | 被覆 | 実装の在り処 | 既定ON/OFF | ギャップ |
|---|---|---|---|---|
| World Model(世界モデル) | ◎ | 主観: `src/society/worldview.py`(期待/可制御性/規範予期)。客観(世界状態): `engine/simulation.py` + `observer/measure.py` の Y 4層(空間/資源/象徴/network)。config `worldview`・`observer.y_weights`。イベント `worldview`・`world_event`。テスト `test_worldview.py`・`test_measure.py` | 主観=基底OFF・本番ON / 客観=常時 | 主観世界モデルと客観世界状態の両輪。統合的因果世界モデルは持たない |
| Action(行動) | ◎ | `src/society/actions/registry.py`(動詞プリミティブ)+ `tools.py`(世界改変ツール)+ scheduler `_apply`(move/speak/post/dm/coin_label/tools 適用)。config `tools`。イベント: 全 action kind。テスト `test_tools.py`・`test_stay.py` | ON | 行動プリミティブ + 世界改変 affordance が体系化。物理操作の粒度は step(10分)単位 |
| Reflection(内省) | ◎ | `src/society/cognition/reflection.py`(k 書き戻し free/degraded/sham/off・深い内省・無意識層・agentic_pull)。**研究の主軸 k**。config `k`・`reflection`・`controls`。イベント `reflect`・`memory_recall`・`reflection_trigger`。テスト `test_deep_trigger.py`・`test_selfmodel.py`・`test_controls.py` | 内省=ON(k で結合度を掃引) | 経験→内部状態の結合強度 k を実験変数として制御可能=本研究の核。過去に reflect_think=true で内省空振りのバグ(daily で修正済) |
| Social Dynamics(社会力学) | ◎ | `opinion.py`(Friedkin-Johnsen)+ labeling(complex contagion)+ `net/infoenv.py`(エコーチェンバー/バイラル)+ `status.py`(マタイ効果/優先的選択)。config `opinion`・`info_env`・`hierarchy`。イベント `opinion_shift`・`feed_rank`・`viral_cascade`。テスト `test_opinion.py`・`test_info_env.py`・`test_status.py` | opinion=ON / info_env・hierarchy=基底OFF・本番ON | 意見力学・伝播・地位集中まで。マクロ相転移(k*)は observer/analyze 側で事後計測 |

---

## 10. 将来枠(リストは「将来枠」だが実装状況を照合)

| エンジン | 被覆 | 実装の在り処 | 既定ON/OFF | ギャップ |
|---|---|---|---|---|
| Family(家族) | ○ | `src/society/household.py`(世帯グループ化・同居・恋愛パートナー形成・デート)。config `household`(恋愛は relations.enabled 前提)。イベント `partner_formed`・`life_event`。テスト `test_household.py` | 基底OFF / 本番ON | 世帯・同居・恋愛まで実装済み(名目は「将来枠」だが H2 で実装)。出産・育児・死別は明示的に未実装 |
| Migration(移住) | △ | career の職場変更(job_change)+ 通勤流入(inflow)。**居住地の移転(residential migration)は未実装**(`docs/plans/unimplemented-inventory.md` D3 自由度P2「移転」= コード未着手) | 職場変更=本番ON | 職の移動のみ。住居の移転・地域間人口移動の機構はなし |
| Political(政治) | ◎ | `institution_routes`(労働争議/選挙投票/条例執行)+ deliberation(審議・パブコメ)+ assembly(代表制議会・council 改選)+ 供託金 + propose/rules/recursion。config `institution_routes`・`rules`・`recursion`。イベント `vote_cast`・`vote_result`・`council_elected`・`proposal_*`・`labor_action`・`deposit`。テスト `test_institution_routes.py`・`test_institutions_deep.py`(deep2/deep3)。 | 基底OFF / 本番ON | **「将来枠」だが実際は最も厚く実装**: 3ルート制度改変・熟議・議会・供託金まで |
| Financial(金融) | ○ | economy.accounts(口座・ATM・カード払い・給料日・家賃引落し)+ 破産免責。config `economy.accounts`。イベント `withdraw`・`rent`・`bankruptcy`。テスト `test_accounts.py` | 基底OFF / 本番ON | 銀行口座・現金管理・破産まで。金融市場・信用・利子・投資の機構はなし |
| Supply Chain(供給網) | △ | organizations の産出集計(org_ledger)+ commerce の品切れ stock_out。イベント `production`・`stock_out`。テスト `test_commerce.py` | 本番ON | 産出カウントと品切れのみ。企業間の投入産出・在庫連鎖・物流のモデルはなし |
| Communication(媒体特性) | ○ | net の複数チャネル(SNS/DM/ニュース/検索)+ opinion のチャネル別説得重み(w_face/w_dm/w_sns)+ sns_geo(物理距離記録)。config `net`・`opinion`・`sns_geo`。イベント `dm`・`sns_post`・`transmission`。テスト `test_sns_social.py` | net/opinion=ON / sns_geo=基底OFF | 媒体ごとに説得力を差別化。媒体の帯域・遅延・信頼性の細かな特性化は部分的 |
| Reputation(評判) | ◎ | relations の reputation(語採用/被傾聴で集計)+ `status.py`(威信 prestige/被フォロー/資産の合成地位)。config `relations.rep_*`・`hierarchy`。イベント `reputation_update`・snapshot の status。テスト `test_relations.py`・`test_status.py` | 基底OFF / 本番ON | 「将来枠」だが評判 + 地位まで実装済み。評判の多次元性(能力vs誠実さ)は単一スコア |
| Governance(統治) | ◎ | `rules.py`(制度DSL のホワイトリスト自動制定)+ `recursion.py`(規範の自己観測ループ)+ government + assembly。config `rules`・`recursion`・`government`。イベント `institution_rule`・`norm_digest`・`rule_expired`・`rule_weekly_fire`。テスト `test_rules.py`・`test_recursion.py` | rules=ON / recursion=基底OFF・本番ON | 機械可読ルールの制定→実効化→失効まで自動制定。統治の正統性・執行能力の内生化は部分的 |

---

## 11. Meta 層(追加)

| エンジン | 被覆 | 実装の在り処 | 既定ON/OFF | ギャップ |
|---|---|---|---|---|
| Observer(観測・L1/L2/L3) | ◎ | `src/society/observer/`(logger=L1イベント・aggregate=L2メトリクス・log_snapshot=L3スナップ・schema=種レジストリ・measure=事後計測・provenance)。config `observer`(snapshot_every/checkpoint_every/flush_every_steps/y_weights)。出力 Parquet。テスト `test_observe.py`・`test_measure.py`・`test_resume.py` | 常時ON | 観測と本体の frame 分離が徹底(シム本体は記録のみ、計測は事後)。checkpoint/resume・part flush まで |
| Reproducibility(乱数stream/CRN/ゴールデン) | ◎ | `src/society/rng.py`(中央集権 RngHub・stream キーに用途/agent/step・sha256 安定ハッシュ)+ `llm/cache.py`(応答キャッシュ)+ golden_baseline_l1.json + icebreak 共通ファイル(条件間 CRN)。config `model.cache`・`run.seed`。テスト `test_determinism.py` | 常時ON | ストリーム分離乱数 + CRN + ゴールデンで完全決定論リプレイ。新機能は「既定OFF=バイト一致」で導入 |
| Scenario-Intervention(実験マニフェスト) | ◎ | `conf/experiments/*.yaml`(modelk_4cell 等)+ `scripts/run_experiment.py`・`run_sweep.py` + `world/scenario.py`(shock_closure/shock_event)。config `world.scenario`・`world.scenario_params`。イベント `scenario_shock`・`world_event`。テスト `test_experiment.py`・`test_scenario.py`・`test_sweep.py` | scenario=baseline(no-op)/ 実験時に指定 | 実験の全条件を宣言的に管理(コードは書き換えない)。介入キュー(demo 用)は計画段階 |
| Calibration-Validation(現実照合) | ◎ | `scripts/calibrate_report.py`(L1/L2/summary から現実一次統計バンドとのズレを表化)+ `docs/calibration/`・`docs/research/*` の較正値。production/daily の較正コメント(タクシー分担率・犯罪率・失業率等を現実バンドに合わせて調律)。テスト系: 較正は疎結合(シム本体不変) | 常時利用可 | 現実バンド(lo..hi)+ 出典注記で照合。mock ラン では LLM 依存行動を別扱い。自動較正ループはなし(手動調律) |

---

## 12. 最難関: 思考→行動の取り出しモジュール(deliberate.py の parse_action)

ユーザーが最難関と指摘した「思考→行動の取り出し」の現実装は、
`src/society/cognition/deliberate.py` に集約される。経路は
**deliberate のプロンプト(build_prompt)→ LLM 生成 → parse_action(JSON 解釈)→ 失敗時 fallback(routine)**。

### 12.1 プロンプトが要求する出力契約

ヘッダ `_HEADER_HEAD` / `_HEADER_TAIL`(deliberate.py)は「**次のいずれかの JSON 1個のみ(キー名は厳守)**」と
指示し、`speak` / `coin_label` / `post` / `dm` / `wander` を提示する。`freedom.open_actions=true` のときだけ
`do`(自由記述行動)を1行足す。tools.equip_all=true なら `propose`/`host_event`/`post_flyer`/`found_group`/`open_venture`
の中立告知節(`_equip_section`)を客観条件(所持金)つきで足す。**中立提示に徹し使用は勧めない**(自然使用の観察)。

### 12.2 parse_action の JSON 検証(何キーをどう検証するか)

`parse_action(response)` は次の順で寛容に検証する:

1. **`_loads_lenient`(途中で切れた JSON の軽修復)**: `response` そのまま / strip / `+"}"` / `+'"}'` / `+'"}}'` の
   5 候補を順に `json.loads` し、最初に `dict` になったものを返す。**トークン上限で閉じ括弧が欠けた出力を救う**。
2. `dict` でない or `"action"` キーが無ければ **`None`**(=解釈失敗)。
3. `kind = data["action"]` で分岐。各 kind は内部ヘルパ `_text_of(*keys)` で**キー名の別名を吸収**する
   (寛容性の核):
   - `speak`: `text`/`content`/`message`/`say`/`speech` のいずれか。空でなければ `{"type":"speak","text":…,"use_items":[…]}`。無ければ `None`。
   - `coin_label`: `word`/`label`/`name` を必須。text は `text`/`content`/`message` か、無ければ word 自身。
   - `post` / `dm`: `text`/`content`/`message`。
   - `host_event`: `title`/`name`/`text` 必須。`hours_later` は int 化し **max(1,min(6,…))** にクリップ。
   - `post_flyer` / `found_group` / `propose` / `open_venture`: それぞれ必須キー(text/name 等)を `_text_of` で取り、
     `propose` は任意の機械可読 `rule`(dict)を通す(深い検証は rules.RuleBook が成立時に行う)。
   - `do`/`free`/`activity`: `what` 必須、`minutes` を **max(10,min(240,…))**、`where`/`value`(自己申告価値)を任意で拾う → `{"type":"free_action",…}`。
   - `plan`: `items`(dict のリスト)→ planning が消費。
   - `wander`: 引数なしで `{"type":"stay"}`(=その場に留まる)。
   - `recall` / `reflect`: 内省経路用(reflect は `belief`/`summary`/`salient` を検証し、深い内省の `self`/`ties` があれば通す)。
4. どの分岐にも当てはまらない/必須キーが空 → **`None`**。

**要点**: 検証は厳格な schema 検証ではなく**寛容な正規化**(別名吸収 + 数値クリップ + 途中切れ修復)。
LLM が多少キー名を外しても意味が通れば拾い、意味が取れなければ静かに `None` を返す。

### 12.3 fallback がどう働くか(失敗時の routine 後退)

`None`(解釈不能)になったとき、呼び出し側 `src/society/engine/scheduler.py` の `_llm_speak` は
`fallback`(payload `{"reason":"parse_error"}`)イベントを1件記録して **`None` を返す**(=LLM 層では沈黙)。
その後の意思決定は `_decide` で:

1. 返答保証・発火権(`_fire_llm`)の各経路は「`if action is not None: return action`」なので、`None` は素通り。
2. 最終的に **`routine.decide(...)`(非LLM のルールベース行動)**へ後退する
   (`src/society/cognition/routine.py`)。これが「失敗時 fallback(routine)」の実体。
3. routine が `stay` を返し、かつスマホ所持なら `_phone`(閲覧系)へ二段フォールバックする。

つまり「思考(LLM)→行動」の取り出しに**失敗しても世界は止まらない**: 発話は消え、行動は
ルールベース(移動・勤務・帰宅・スマホ閲覧など)に置き換わる(設計原則 D16「壊れたら沈黙して続行」)。

---

## 13. 4層(知覚→思考→意思決定→行動)への対応

現実装の 1 step(`src/society/engine/scheduler.py` の `run_step`)は、多数の日次/毎step フェーズを経た後、
中核の意思決定ループでこの4層に対応する。

- **① 知覚(Perception)**: `_phase_move` 等で全 agent の位置が確定した後、`build_index`(`world/perception.py`)で
  空間索引を張る。`_decide`/`_llm_speak` 内で `hearers_of` が同一文脈・半径内の同席者(company)を集め、
  `_feed_texts`(SNS TL)・memory.retrieve(想起)・当日の日付/天気/年中行事/広告/世帯/観光/世界観の各行を集約する。
  これらを `deliberate.build_prompt` が1本のプロンプト(共通部先頭+個別部後方=APC 効率)に組み立てる=**知覚の器**。
- **② 思考(Thinking)**: いつ考えるかは `_phase_drive`(欲求駆動発火)。出来事がゲージを溜め、個人別閾値
  (traits + drift + 覚醒 + 疲労で変調)で「申請」→ 抽選 → **発火権**を配る(予算 lod.max_llm_per_step 内)。
  発火権を得た者だけが `deliberate` へ進み、`sim.llm.generate(prompt)` が実際の思考(=LLM 生成)を行う。
  夜は `maybe_reflect`(内省=k)が「今日一日」を深く思考し belief を書き戻す。
- **③ 意思決定(Decision)**: `parse_action`(§12)が LLM の JSON を構造化行動 dict に変換する。
  失敗すれば `routine.decide`(非LLM)がルールベースで意思決定を代替する。**思考が具体的な行動選択に変わる継ぎ目**。
- **④ 行動(Action)**: `_apply` が行動 dict を世界状態に反映する(move_to で経路生成、speak で hearers に配信+意見更新、
  post/dm で net 反映、coin_label で語彙創出、tools.apply で世界改変)。反映後に `factors/update.py` が
  **経験→state(効力感・不満・当事者意識)**を更新し(no-fingerprint: engine は因子名を見ない)、L1 イベントを記録する。

この 知覚→思考→意思決定→行動 の一巡が終わると、観測フェーズ(`collect`→L2 メトリクス、snapshot_every ごとに L3)で
研究者 frame の計測が事後に走る。**本体は「起きたこと」を記録するだけ**で、k*・R² の測定は observer/analyze 側に分離されている。

---

## 14. 最終報告(集計・厚薄・意外な発見)

### 被覆度の集計(全 61 エンジン)

| 被覆度 | 数 | 内訳(層) |
|---|---|---|
| ◎ 完全 | **34** | Human 8・Economy 3・Information 3・Organization 2・City 2・Society 2・Environment 2・Time 1・Integration 4・将来枠 3・Meta 4 |
| ○ 部分 | **21** | Human 5・Economy 3・Information 1・Organization 3・City 2・Society 3・Time 1・将来枠 3 |
| △ 萌芽 | **5** | Skill・Urban Development・Demography・Migration・Supply Chain |
| × なし | **1** | Ecology |

◎+○ = 55/61(90%)が何らかの形で実装済み。純粋に未実装は Ecology の1つのみ。

### 特に厚い層

- **Integration 層(4/4 が◎)** と **Meta 層(4/4 が◎)**: 世界モデル・行動・内省・社会力学、そして観測・再現性・
  実験マニフェスト・較正まで研究基盤として完備。本プロジェクトが「観測・再現性・実験統制」を最優先にした結果。
- **Human 層(13 中 8 が◎)**: 知覚/記憶/計画/関係/健康/注意/世界観/言語が◎。LLM 認知 + 決定論の内面機構が厚い。
- **Information 層(4 中 3 が◎)**: SNS/検索/ニュース/ネットワーク/メディアが閉じた架空世界内で完結。

### 特に薄い層

- **Environment 層**: Weather/Disaster は◎だが **Ecology が唯一の×**(研究目的が人工社会=生物生態系は対象外)。
- **△ が集まる継ぎ目**: Skill(技能蓄積の状態が無い)・Urban Development(地図が変わる再開発が未実装)・
  Demography(出生死亡移動の動態が無い)・Migration(住居移転が無い)・Supply Chain(企業間投入産出が無い)。
  共通項は「**状態が時間とともに構造的に変わる長期動態**」(100日ラン想定で優先度が下げられている)。

### 意外な発見 3 つ

1. **「将来枠」の Political が実は最も厚く実装されている(◎)**。分類上は未着手枠のはずが、実際には
   3ルート制度改変(労働争議/選挙投票/条例執行)+ 審議パブコメ + 代表制議会(council 改選)+ 供託金まで
   `institution_routes` に完備し、`conf/production.yaml`・`conf/daily.yaml` で全 ON。同様に Reputation・Governance・
   Family も「将来枠」ながら実装済み。分類リストの「将来」区分は本コードの実態より保守的。

2. **思考→行動の取り出し(parse_action)は「厳格 JSON 検証」ではなく徹底した「寛容な正規化」**。
   別名キー吸収(text/content/message/say/speech…)・数値クリップ・**途中で切れた JSON の閉じ括弧補完**
   (`_loads_lenient`)まで備え、それでも駄目なら `None`→routine 後退。ユーザーが「厳格JSON」と想定した箇所は、
   実装では「壊れても止めない」哲学(D16)で意図的に緩められている。fallback は routine への後退であって
   エラー停止ではない(世界は必ず進む)。

3. **ほぼ全リアリズム機能が「基底=既定OFF、本番=ON」の二層構造**。基底 `conf/config.yaml` は再現性の
   ゴールデン(バイト一致)を守るため約30ブロックを OFF に固定し、`production.yaml`/`daily.yaml` が差分 merge で
   一括 ON にする。しかも各ブロックの config コメントには「現実較正」の一次出典(東京都最低賃金1,226円・
   タクシー分担率・渋谷区犯罪認知件数・雇用動向調査の失業率など)が明記され、現実バンドに合わせて数値が
   調律済み。「実装の有無」と「既定の有効性」を分けて読まないと被覆度を誤読する。
