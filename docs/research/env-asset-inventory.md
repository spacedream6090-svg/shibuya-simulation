# 環境固有資産の全数棚卸し(EnvPack分離D1 / 環境自動生成D2 の前提)

作成: 2026-07-17(Opusサブエージェント調査)。**コード変更なし・読み取り実測のみ**。
目的: foundation-extraction.md の「混在(C)」既知リスト(2026-07-10時点)を実コードで検証し直し、
渋谷固有資産を file:line つきで全数列挙する。誠実性方針: 推測禁止・全項目に根拠 file:line。
「なし/未確認」は明示する。行番号は本調査時点(2026-07-17)の実ファイル値。

---

## 0. サマリ(最終報告)

### 直書きリテラル総数(カテゴリ別・src/society 内)
| カテゴリ | 実行時に効く箇所(プロンプト/ロジック/既定値) | コメント/docstringのみ |
|---|---|---|
| 地名・ランドマーク(プロンプト注入) | 7件(deliberate ×2, diversity ×1, persona ×4行=1ブロック, map ×1) | 多数(下記 §1.7) |
| メディア番組・ゲーム名 | 12タイトル(media.py の5+5+2=渋谷/スクランブル/ハチ公/センター街) | — |
| 予定パーサの地名ヒント辞書 | 13地名(schedule.py:49-51) | — |
| 群集集約先=地図原点=スクランブル(env仮定) | 1(annual.gathering_node のロジック仮定) | routine/simulation/scheduler 多数 |
| 駅名フィルタ | 1(transit.py:30-31 "渋谷"/"Shibuya") | — |
| 特定日付の行事 | 3(annual.py:29-31 正月/ハロウィン/年末) | — |
| 日本制度の数値既定(economy) | 賃金5種+価格5種+職業別所持金12種+口座/最賃 | — |
| 日本制度の数値既定(government) | 税率ブラケット6段+住民税6:4+消費税78:22+予算3種+給付 | — |
| 日本制度の数値既定(tools/rules) | 議席9・供託金・venture_cost・罰金 | — |
| 通貨(円)の仮定 | 10ファイル以上(§1.9) | — |
| 言語(日本語)の仮定 | calendar/values/sentiment/diversity(§1.10) | — |
| 気候(東京)の仮定 | 1(weather.py:22-27 月別気候テーブル) | — |

### 計画の既知リストとの差分(§5 詳細)
- foundation-extraction.md の既知リスト(deliberate「渋谷」・transit駅名・annual/routine原点+10/31・media局名・schedule・economy/government制度既定)は**すべて現存を確認**(行番号は更新)。
- **新発見(計画の既知リストに無い/第17バッチ以降に増えた分)= 8系統**:
  1. **街頭広告 ads の掲出地点** = daily.yaml:246-247 に `QFRONT / SHIBUYA 109 / ハチ公前広場 / 渋谷マークシティ`(第18バッチ)。base config.yaml:434-437 は空 seam 化済み。
  2. **diversity.py:142** 観光客プロンプト「あなたは観光で渋谷を訪れている」(H5・第16バッチ以降)。
  3. **weather.py:22-27** 東京の月別気候テーブル(env固有・計画未記載)。
  4. **world/map.py:164** place_label「地下通路(渋谷ちかみち)」。
  5. **synth_crowd.py**(scripts)「スクランブル交差点」ノード導出(群衆物理・第16バッチ以降)。
  6. **street.py:97** 掲出地点フォールバック説明に `QFRONT / ハチ公前広場`(第18バッチ)。
  7. **rules.py:41,127** 渋谷パートナーシップ条例/渋谷区(制度深化コメント)。
  8. **persona.py:147-152** の渋谷フォールバック文(persona_txt 未指定時)。
- **反証(計画の示唆に反する実測)**: 計画タスクは「worldview.py の新直書き」を示唆したが、**worldview.py に地名リテラルは無い**(プロンプトは generic「この街」「この場所」のみ=既にクリーン)。§1.7 に明記。

### data/ 分類集計(§2)
実体JSON 32個+odpt/odpt_challenge 各約29ファイル。地理7・交通(実体+ODPTキャッシュ)・人口/名簿8・組織/配属7・文化/イベント2・参照/その他5。**再配布制約あり=ODPT系(transit_odpt.json + odpt/ + odpt_challenge/)と OSM系(shibuya_osm*.json=ODbL)**。

### conf/ 分類集計(§3)
base config.yaml トップレベル44ブロック。機構トグル(場所非依存)が大多数。**環境固有の値**= data パス(map/transit/personas/organizations)・ads掲出地点・calendar.start_date・annual_events。**較正値(出典コメント付き)**= 最賃1226・taxi 0.02・crime/nuisance確率・career確率・議席9・供託金30000・eviction/bankruptcy日数。

---

## 1. src/society 内の「場所・文化・制度」直書きリテラル全数

### 1.1 プロンプトに注入される地名(=LLM入力=最優先で seam 化すべき)
| file:line | リテラル |
|---|---|
| src/society/cognition/deliberate.py:14 | ヘッダ「あなたは**渋谷**の街で暮らす一人の人間です。状況に対して自然に振る舞ってください。」(全発火プロンプト先頭・既定) |
| src/society/cognition/deliberate.py:247 | variety_hint「『この時間の**渋谷**は…』のような情景報告の決まり文句で始めない」(prompts.variety_hint=true 時) |
| src/society/diversity.py:142 | 観光客文脈「あなたは観光で**渋谷**を訪れている(この街の生活者ではなく、名所を見て回っている)。」(society_diversity ON かつ tourist) |
| src/society/agents/persona.py:147 | `where = residence_line or "渋谷の外"`(persona_txt 未指定の通勤者) |
| src/society/agents/persona.py:148 | `f"{where}に住んでいて、毎日渋谷に通勤・通学している"` |
| src/society/agents/persona.py:150 | `"渋谷の街の外に住んでいて、よく渋谷に来る"`(visitor) |
| src/society/agents/persona.py:152 | `"渋谷の街で暮らしている"`(居住者) |
| src/society/world/map.py:164 | place_label のフォールバック「地下通路(**渋谷ちかみち**)」(layer<0 のノード名) |

補足: map.py:166「ペデストリアンデッキ」は一般語(env非依存)。deliberate.py:14 は既定ヘッダ=キャッシュ整合の基準(`_COMMON_HEADER`)なので seam 化時はゴールデン注意。

### 1.2 メディア番組・ゲーム名(media.prompt_context=true でプロンプト注入)
| file:line | リテラル |
|---|---|
| src/society/media.py:60 | tv: 「夜の**スクランブル**」「**ハチ公**前ニュース9」「**渋谷**トークナイト」 |
| src/society/media.py:61 | tv: 「深夜の**センター街**劇場」(+「みんなの気象台」=generic) |
| src/society/media.py:64 | game: 「**スクランブル**・ラッシュ」「タワー・オブ・**シブヤ**」(+「パズル横丁」「ネオンレーサー2」=generic) |
| src/society/media.py:65 | game: 「**ハチ公**クエスト」 |
| src/society/media.py:52-56 | `_OCC_FREE` 日本語職業名キー(大学生/無職/フリーランス/…)= 言語・職業体系依存 |

video プール(63行)は generic(路地裏グルメ散歩 等)。

### 1.3 予定パーサの地名ヒント辞書(schedule.enabled=true で会話から地名抽出)
| file:line | リテラル |
|---|---|
| src/society/schedule.py:49 | `"スクランブル交差点","スクランブル","ハチ公前","ハチ公","センター街"` |
| src/society/schedule.py:50 | `"道玄坂","宮益坂","渋谷駅","渋谷","新宿","原宿","表参道","恵比寿"` |
| src/society/schedule.py:51 | `"代官山",…`(以降 図書館/美術館/映画館/… は generic 施設語) |
| src/society/schedule.py:281 | docstring 例「明日15:00に渋谷で会う約束」(コメント) |

### 1.4 群集の集約先=地図原点=スクランブル交差点(env仮定=ロジック上の直書き前提)
「地図ローカル原点(0,0)=スクランブル交差点」という**環境固有の座標系仮定**が群集ロジックに埋まっている。
| file:line | 内容 |
|---|---|
| src/society/annual.py:62-66 | `gathering_node` = 原点(0,0)最近傍ノード。docstring「集会ノード=スクランブル交差点(地図ローカル原点)」「地図の原点はスクランブル交差点(conf の座標系注記)」= **原点がランドマークである前提**が実ロジック |
| src/society/annual.py:5-6,27,65,104 | 「渋谷固有のハロウィン型群集」等(コメント) |
| src/society/engine/simulation.py:90,101 | 「スクランブル付近の集会ノード」(コメント+crowd_node 解決) |
| src/society/engine/scheduler.py:2464,2932 | 「群集(渋谷ハロウィン型)」(コメント) |
| src/society/cognition/routine.py:155,297,590,596 | 「ハチ公像等の landmark」「群集日(渋谷ハロウィン型)…スクランブル付近」(コメント+_crowd_dest ロジック) |
| src/society/observer/schema.py:136 | crowd_surge 説明「スクランブル等への集中」 |

### 1.5 駅名・路線名フィルタ
| file:line | 内容 |
|---|---|
| src/society/world/transit.py:30-31 | GTFS 読込時 `"渋谷" in stop_name or "Shibuya" in stop_name` で渋谷停車便のみ抽出(実行ロジック) |
| src/society/world/transit.py:4-9,26 | docstring: 渋谷駅・JR-East/TokyoMetro/Tokyu・ODPT(コメント) |

### 1.6 特定日付の行事
| file:line | リテラル |
|---|---|
| src/society/annual.py:29 | `{"name":"正月","month":1,"day":1,"crowd":False}` |
| src/society/annual.py:30 | `{"name":"ハロウィン","month":10,"day":31,"crowd":True}`(群集フラグ付き=渋谷ハロウィン) |
| src/society/annual.py:31 | `{"name":"年末","month":12,"day":31,"crowd":False}` |
| src/society/annual.py:100 | `f"今日は{e['name']}です。"`(プロンプト注入テンプレ・行事名は上記由来) |

### 1.7 モジュール docstring / コメント内の地名(実行時非注入だが env 前提を刻む)
| file:line | 内容 |
|---|---|
| src/society/__init__.py:1 | 「LLM 人工社会(渋谷)」 |
| src/society/diversity.py:3 | 「渋谷の街の多様性と…」 |
| src/society/street.py:3 | 「現実の渋谷は無数の広告…」 |
| src/society/street.py:97 | フォールバック説明「QFRONT=建物・ハチ公前広場=ノード」 |
| src/society/organizations.py:7 | 「data/organizations_shibuya.json は渋谷の産業構成に統計準拠」 |
| src/society/rules.py:41 | 「渋谷パートナーシップ条例 2015 のモデル化」 |
| src/society/rules.py:127 | 「現実の例: 渋谷区…」 |
| src/society/agents/agent.py:20 | 「渋谷昼間人口の~56%」(visitor 比の人口仮定) |
| src/society/agents/agent.py:22 | 「昼間就業者の~74%が区外流入」(docs/research/shibuya-inflow.md) |
| src/society/agents/persona.py:5 | 「IPF×e-Stat 渋谷 + LLM 文章化」 |
| src/society/economy.py:32,42 | 警視庁/東京消防庁/会社員=12000圧縮スケール |
| src/society/engine/scheduler.py:1839,2243 | 「渋谷で働く扱い」「東京都の公安職」 |

**反証(重要)**: `worldview.py` を全読(300行)したが**地名リテラルは1件も無い**。プロンプト行は「この場所、いつものこの時間より人が多い気がする。」(268)「この街では、新しく…」(296)等の generic のみ。計画タスクが示唆した「worldview.py の新直書き」は**実在しない**=既にクリーン。同様に `values.py:36` は明示的に「渋谷固有語を避けた一般語彙のみ(基盤層=場所非依存)」と設計されており env 非依存。

### 1.8 日本制度の数値既定(コード内デフォルト。conf 未指定時に効く)
**economy.py**
| file:line | 既定値 |
|---|---|
| economy.py:97-100 | wages: 会社員12000/自営10000/店員9000/part_time_hourly1100/区職員13000/警察官15000/消防士14000 |
| economy.py:103 | コメント: 東京都最低賃金 1,226円/時(2025-10-03 発効・東京労働局)。適用は `min_wage_hourly`(既定0.0=床なし) |
| economy.py:110-111 | 床適用対象カテゴリ 会社員/店員/区職員/警察官/消防士(×8h) |
| economy.py:112-113 | prices: food900/cafe500/shop2500/nightlife1800/leisure0 |
| economy.py:50-61 | MONEY_INIT 職業別所持金レンジ12種(会社員50000-150000 等) |
| economy.py:21-27 | WAGE_CAT(日本語職業名→賃金カテゴリ) |
| economy.py:35 | CIVIL_SERVANTS = {区職員:ward, 警察官:metro, 消防士:metro} |
| economy.py:65 | PART_TIME_OCC = {大学生,無職,バンドマン} |
| economy.py:78-81 | payday_dom25 / rent_share0.30 / card_threshold3000 / atm_withdraw20000 |
| economy.py:88 | bankruptcy_keep 10000(実法99万円を圧縮) |
| economy.py:120 | allowance_visitor 20000 |

**government.py**
| file:line | 既定値 |
|---|---|
| government.py:24 | 消費税 国:地方 = 78:22(`_CONSUMPTION_NATIONAL_SHARE=0.78`) |
| government.py:35-41 | 所得税 実効税率ブラケット6段(2M/3.3M/5M/7M/10M/上限→0.02〜0.20) |
| government.py:62 | ward_initial 60,000,000(渋谷区 1,468.73億÷24.4万×100) |
| government.py:63 | metro_initial 65,000,000(東京都 9.158兆÷1,400万×100) |
| government.py:64 | nation_initial 92,000,000(国 115兆÷1.25億×100) |
| government.py:66-67 | resident_rate0.10 / resident_ward_share0.6(住民税 区6:都4) |
| government.py:69 | annual_workdays 245 |
| government.py:72-74 | consumption_rate0.10 / reduced0.08 / reduced_cats=[food] |
| government.py:76-77 | benefit_threshold2000 / benefit_amount3000(区の生活困窮者支援) |

**tools.py / rules.py(制度パラメータ既定)**
| file:line | 既定値 |
|---|---|
| src/society/tools.py:108 | assembly `size` 既定9(議席数) |
| src/society/tools.py:42 | venture_cost 既定30000 |
| src/society/tools.py:79-80,377,395,828,921 | 供託金 deposit ロジック(既定0=不変。額は conf) |
| src/society/rules.py:47 | bonus_max 既定500(円) |
| src/society/rules.py:87(tools.py) | fine 既定1000(円・区の歳入) |
| src/society/cognition/deliberate.py:105 | venture_cost 引数既定30000.0 |
| src/society/engine/scheduler.py:866,2043-2044 | venture_cost フォールバック30000.0 |
| src/society/world/traffic.py:44 | cars_per_day 既定30000 |

### 1.9 通貨(円)の仮定箇所
円建て前提が全経済系に散在(通貨記号「円」の文字列連結)。
- src/society/cognition/planning.py:60 「今の所持金: 約{money}円」(プロンプト)
- src/society/cognition/deliberate.py:72-76 「所持金{money}円」(プロンプト)
- src/society/freedom_p2.py:50-54 「所持{total}円」「敷金{dep}円」(プロンプト)
- src/society/recursion.py:57-60 ルール描画「価格{delta}円」「{amount}円支給」(プロンプト/ニュース)
- src/society/engine/scheduler.py:2291,2359,2362 「罰金{penalty}円」(記憶テキスト)
- src/society/agents/agent.py:75,80 money/account コメント「(円)」
- src/society/llm/mock.py:53 「100〜500 円」
- src/society/values.py:35 cost=(円) コメント
- economy.py / government.py / tools.py 全般(金額の内部表現=円)

### 1.10 言語(日本語=ja)の仮定箇所
- src/society/world/calendar.py:14,49 曜日「月火水木金土日」(日本語1文字前提)
- src/society/lang/sentiment.py 全体: 日本語評価極性辞書(東北大 乾・岡崎研)前提の感情価採点。非日本語テキストは機能しない
- src/society/values.py:23 「LLM の自己申告(日本語/英語ゆらぎ)→正準タグ」
- src/society/diversity.py:56,145 languages=[英語,中国語,韓国語]=「非日本語話者」定義=**日本語が既定言語**という前提。145「日本語での会話は少し不自由」
- src/society/diversity.py:64 nuisance_kinds=[客引き,ナンパ,喧嘩,路上の騒ぎ](文化・言語依存)
- deliberate.py 等のプロンプトは全て日本語で構築(lang seam 未分離)

### 1.11 気候(東京)の仮定
| file:line | 内容 |
|---|---|
| src/society/weather.py:22-27 | `_MONTH_CLIMATE` 月別(最高/最低気温・雨重み・雪重み)= 「現実の東京の月別気候の近似」(梅雨6-7・盛夏7-8・冬の雪)。env固有・**計画未記載の新発見** |
| src/society/weather.py:29 | `_NEUTRAL_CLIMATE`(calendar OFF 時の季節なし既定)= env非依存フォールバック |

---

## 2. data/ ディレクトリ全ファイル分類

### 2.1 実体JSON(data 直下)
| ファイル | 分類 | 生成元 | 再配布制約 |
|---|---|---|---|
| shibuya_core.json | 地理 | 手作り近似(build_map 以前の旧版) | なし(自作) |
| shibuya_osm.json / _v3p / _v6 / _wide / _wide_20250401 / _wide_v7 | 地理 | scripts/build_map.py(Overpass/OSM)+patch_map.py | **OSM ODbL**(出典表示・継承) |
| floorguide_shibuya.json | 地理(フロア) | 手動調査(公式フロアガイド) | 概略・事実に限定(§meta) |
| poi_patch_shibuya.json | 地理(POI補完) | scripts/patch_map.py 入力(手動) | なし(自作) |
| traffic_features_shibuya.json | 交通(車道注釈) | scripts/build_traffic.py(Overpass/OSM) | **OSM ODbL** |
| transit_shibuya.json | 交通(ダイヤ近似) | 手作り(公表始発終電から) | なし(公表値の近似) |
| transit_odpt.json | 交通(実ダイヤ) | scripts/build_transit_odpt.py(ODPT由来) | **ODPT 利用規約・出典表示必須** |
| shibuya_population.json | 人口(IPF周辺分布) | 令和2年国勢調査 渋谷区(e-Stat) | 政府統計(出典表示) |
| persona_pool.json | 人口・名簿 | scripts/gen_personas.py(seed42・procedural) | なし(合成) |
| personas_40/60/80/100_inflow/100_civic/300_civic.json | 名簿 | scripts/build_personas.py / gen_personas.py | なし(合成) |
| personas_gen_100.json | 名簿 | gen_personas.py | なし(合成) |
| organizations_shibuya.json / _wide / _wide300.json | 組織台帳(架空) | scripts/build_orgs.py | なし(架空・統計準拠) |
| org_assignments_80/100_civic/100_civic_wide/100_inflow/300_civic_wide.json | 配属 | scripts/build_orgs.py | なし(合成) |
| events_demo.json | 文化・イベント(デモ) | 手作り(シナリオ例・シブヤレンズ) | なし(自作デモ) |
| icebreak_80.json | 参照(事前生成対話) | scripts/build_icebreak.py(qwen3:8b生成) | なし(LLM合成) |
| sentiment_lexicon.json | 参照(感情辞書) | 東北大 乾・岡崎研 日本語評価極性辞書を変換 | **クレジット明記で商用/再配布可** |

### 2.2 ODPT キャッシュ(data/odpt/ ・data/odpt_challenge/)
| 内容 | 分類 | 生成元 | 再配布制約 |
|---|---|---|---|
| _index.json / railway_*.json / stations_*.json / station_timetable_*.json / gtfs/ | 交通(実ダイヤ元データ) | scripts/fetch_odpt.py(ODPT API v4) | **ODPT 利用規約・出典表示必須・免責記載あり**(_index.json _meta に明記)。9路線: JR山手/埼京/湘南新宿・東急東横/田園都市・京王井の頭・メトロ銀座/半蔵門/副都心 |

odpt/_index.json:3-9 に attribution「公共交通オープンデータセンターのデータを利用して作成」「実行時 API 禁止=静的キャッシュのみ読む」規律あり。EnvPack 共有時は**実体でなく取得レシピ(fetch_odpt.py 参照)を同梱**する方針(foundation-extraction.md §リスク と整合)。

---

## 3. conf/ キー分類(3分類: 機構トグル / 環境固有の値 / 較正値)

base = conf/config.yaml(トップレベル44ブロック)、overlay = production.yaml / daily.yaml(差分)。

### 3.1 機構トグル(場所非依存=基盤A)※代表のみ
`factors, k, reflection, controls, model, tools, recursion, net, drive, planning, prompts, lod, freedom, worldview, crowd_visual, sns_geo, labeling, rewards, memory, relations, hierarchy, psych, opinion, storage, observer, needs, affect, inner_life, schedule, career(機構), health, household, commerce, info_env, disaster(機構), society_diversity(機構部)` — enabled トグルと機構パラメータは場所非依存。

### 3.2 環境固有の値(場所・国に依存)
| conf キー | 値 | file |
|---|---|---|
| world.map | data/shibuya_osm*.json | config.yaml:117 / production:31 / daily:33 |
| transit.file | data/transit_odpt.json | config.yaml:373付近 / production:42 / daily:41 |
| agents.personas_file | data/personas_*_civic.json | production:21 / daily:29 |
| organizations.book / assignments | data/organizations_shibuya*.json 等 | config.yaml:582 / production:63-64 / daily:75-76 |
| world.traffic.features_file | data/traffic_features_shibuya.json | config.yaml:145 |
| **ads.large / ads.slots** | base=空[]、daily=`["QFRONT","SHIBUYA 109","ハチ公前広場"]`/`["渋谷マークシティ"]` | config.yaml:436-437 / **daily.yaml:246-247** |
| world.calendar.start_date | "2026-04-01"(base)/ "auto"(prod/daily) | config.yaml:172 / production:34 |
| world.calendar.holidays | [](国の祝日リストは env 依存) | config.yaml:174 |
| annual_events.events(既定) | 正月/ハロウィン/年末(コード側 annual.py:29-31) | config.yaml:759 で enabled のみ |
| society_diversity.languages / nuisance_kinds | [英語,中国語,韓国語] / [客引き,…] | config.yaml:970,978 |

補足: base config.yaml:433「掲出地点(large/slots)は環境プロファイル側で与える(基盤=機構のみ・場所の値を持たない)」= **ads は既に seam 宣言済み**(空 base + overlay で値)。EnvPack 化の先行事例。

### 3.3 較正値(現実データに合わせた調律=出典コメント付き)
| conf キー | 値 | 出典コメント | file |
|---|---|---|---|
| economy.min_wage_hourly | 1226 | 「東京都最低賃金 1,226円/時(2025-10-03発効・東京労働局)」 | config.yaml:186-190 / production:103-106 / daily:115-118 |
| transit_ride.taxi.prob | 0.02 | 「東京のタクシー分担率~2%・0.03-0.05回/人日」 | production:44-49 / daily:43-46 |
| society_diversity.crime_prob | 0.000002 | 「渋谷区の認知件数~2.8e-5/人日…に締める」 | production:183-186 / daily:203-206 |
| society_diversity.nuisance_prob | 0.005 | 「渋谷中心部の体感として現実的」 | production:187 / daily:207 |
| career.layoff/switch/rehire_prob | 0.0002/0.0004/0.02 | 「雇用動向調査(非自発離職1-2%/年・転職5-10%/年)」 | production:141-145 / daily:157-161 |
| institution_routes.assembly.size | 9 | 「渋谷区議会34議席を100体スケールに圧縮」 | config.yaml:709 / production:133 / daily:148 |
| institution_routes.assembly.term_days | 30(prod)/1460(daily) | 「区議会4年任期=1460日」 | production:134 / daily:150 |
| institution_routes.vote.deposit | 30000 | 「区議選の供託金30万円を所持金スケールに圧縮」 | config.yaml:691 / production:125 / daily:140 |
| economy.accounts.eviction_days / bankruptcy_days | 30/60(prod)、90/240(daily) | 「実法の3ヶ月滞納で契約解除」 | production:110-111 / daily:123-124 |
| economy.accounts.bankruptcy_keep | 10000 | 「実法の99万円を所持金スケールに圧縮」 | config.yaml:226 |
| government(税率・予算) | §1.8 の government.py 既定 | docs/research/shibuya-government.md | config.yaml:560-563(enabled のみ) |
| weather 月別気候 | weather.py:22-27 | 「現実の東京の月別気候の近似」 | (コード側) |

補足: government の税率・予算・給付の実数は**config.yaml では上書きされず**(:562-563 は enabled のみ)、government.py の既定値がそのまま効く=較正値がコードに埋まっている。EnvPack manifest の institutions ブロックへ移すべき筆頭。

---

## 4. scripts の build_*/fetch_*/gen_* 場所依存パラメータ

| script:line | パラメータ | 引数化 or 直書き |
|---|---|---|
| build_map.py:38 | `DEFAULT_BBOX=(35.6560,139.6950,35.6625,139.7060)` | **--bbox で引数化済み**(:652-653 default) |
| build_map.py:40 | `ORIGIN=(35.65950,139.70062)` スクランブル交差点 | **直書き**(「bbox を変えても不変」=座標系原点がランドマーク固定) |
| build_map.py:57-70 | `CORE_POIS` 14件(スクランブル交差点/ハチ公前広場/渋谷駅ハチ公口/SHIBUYA109/センター街/道玄坂/文化村通り/スペイン坂/渋谷PARCO/公園通り/宮下公園/宮益坂下/渋谷ストリーム/渋谷マークシティ)緯度経度つき | **直書き** |
| build_map.py:79 | `LANDMARK_NAME_KWS=("忠犬","ハチ公","モヤイ","モアイ")` | **直書き** |
| build_map.py:83 | `HACHIKO_FALLBACK=("忠犬ハチ公像",35.6590,139.7005)` | **直書き** |
| build_traffic.py:246 | `--bbox`(default=core meta bbox) | **引数化済み** |
| patch_map.py:13-14,43,68 | bbox 判定(ノード座標範囲) | core 地図由来(相対) |
| fetch_odpt.py:88-121 | 対象9路線+渋谷駅 sameAs 識別子(JR山手/埼京/湘南新宿・東急東横/田園都市・京王井の頭・メトロ銀座/半蔵門/副都心) | **直書き**(live 取得時は自己修復あり) |
| fetch_odpt.py:234-241 | 渋谷駅 sameAs 探索(.Shibuya 末尾 or title=="渋谷") | **直書き**(駅名フィルタ) |
| build_transit_odpt.py:113 | `"渋谷" or "Shibuya" in stop_name` | **直書き** |
| build_transit_odpt.py:37,255 | ODPT路線キー→路線名対応 / station="渋谷駅" | **直書き** |
| build_personas.py:135 | `station_share=inflow.get("gateway_station_share",0.87)` | 名簿由来(渋谷 inflow) |
| build_personas.py:176-192 | 「渋谷の外/渋谷に通勤/渋谷の街」persona 文 | **直書き** |
| gen_personas.py:55 | 職業分布「渋谷の昼間人口」 | **直書き** |
| gen_personas.py:185-194 | 「毎日渋谷に通勤」「渋谷によく遊びに来る」等 persona 文 | **直書き** |
| build_orgs.py:56-289 | 架空組織台帳(スクランブル計画/ハチ公ラボ/渋谷○○ 等 約30社+渋谷区立学校9校) | **直書き**(渋谷テーマの架空組織) |
| synth_crowd.py:37,80-101 | 「スクランブル交差点」ノード導出(poi=="square" or 名前に"スクランブル"・原点最近傍) | **半直書き**(地図から導出だがキーワード直書き) |
| export_ue.py:20,26-28,46,104 | 原点=スクランブル交差点(35.6595,139.70062)・EPSG:6677(JGD2011 IX系=東京) | **直書き** |
| export_3d.py:331 | bbox(meta 由来) | 地図由来 |
| bench.py:196-212 | ベンチ用プロンプト「あなたは渋谷で暮らす30代の会社員」 | **直書き**(検証用) |
| pimmur_probe.py:259,295,336 | 「この渋谷の街」「渋谷駅の方へ」nearby_pois=[スクランブル交差点,ドン・キホーテ] | **直書き**(尋問テスト用) |
| detect_emergence.py:487 | 実在名ホワイトリストに「渋谷」 | **直書き**(固有名詞検出用) |
| calibrate_report.py:58,60 | 「渋谷区刑法犯~5千/年÷昼間人口54万」較正バンド | **直書き**(較正基準・出典つき) |

---

## 5. foundation-extraction.md 既知リストとの差分

### 5.1 計画の既知リスト(:15-18)= すべて現存を確認(行番号更新)
| 計画の記述 | 実測 file:line(2026-07-17) | 状態 |
|---|---|---|
| プロンプト内「渋谷」直書き(cognition/deliberate.py) | deliberate.py:14,247 | 現存 |
| 駅名フィルタ(world/transit.py) | transit.py:30-31 | 現存 |
| 原点=スクランブル・10/31群集(annual.py/routine.py) | annual.py:29-31,62-66 / routine.py:296-309 | 現存 |
| media.py の局名 | media.py:60-65 | 現存 |
| schedule.py | schedule.py:49-51 | 現存 |
| 日本の制度既定値(economy.py/government.py の最賃・住民税按分・区予算) | economy.py:97-113 / government.py:35-77 | 現存 |

### 5.2 新発見(計画の既知リストに無い/第17バッチ以降に増えた分)
| # | 新発見 | file:line | 備考 |
|---|---|---|---|
| 1 | ads 掲出地点(QFRONT/SHIBUYA109/ハチ公前広場/渋谷マークシティ) | daily.yaml:246-247(base config.yaml:434-437 は空 seam) | 第18バッチ。**production.yaml には ads ブロック自体が無い**(daily のみ) |
| 2 | diversity.py 観光客プロンプト「観光で渋谷を訪れている」 | diversity.py:142 | H5(現実ギャップ後続波) |
| 3 | weather.py 東京月別気候テーブル | weather.py:22-27 | 気候=env固有・計画完全未記載 |
| 4 | map.py place_label「地下通路(渋谷ちかみち)」 | map.py:164 | |
| 5 | synth_crowd.py「スクランブル交差点」導出 | synth_crowd.py:37,80-101 | 群衆物理(第16バッチ以降) |
| 6 | street.py 掲出地点コメント QFRONT/ハチ公前広場 | street.py:97 | 第18バッチ OOH |
| 7 | rules.py 渋谷パートナーシップ条例/渋谷区 | rules.py:41,127 | 制度深化コメント |
| 8 | persona.py 渋谷フォールバック文4行 | persona.py:147-152 | persona_txt 未指定時 |
| 追加 | export_ue.py / export_3d.py の原点・EPSG:6677(JGD2011 東京IX系) | export_ue.py:20,46,104 | 座標系が東京固定 |
| 追加 | pimmur_probe.py / bench.py / detect_emergence.py / calibrate_report.py の渋谷直書き | 各 §4 参照 | 検証・尋問・較正スクリプト群 |

### 5.3 反証(計画の示唆に反した実測)
- **worldview.py**: 計画タスクは「worldview.py の新直書き」を挙げたが、全読の結果**地名リテラルは存在しない**(プロンプトは「この街」「この場所」の generic のみ)。→ 既にクリーン。W2 の seam 化対象外。
- **values.py**: 意図的に「渋谷固有語を避けた一般語彙のみ(基盤層=場所非依存)」設計(:36)。env 非依存。
- **annual.py の位置づけ**: src/society 直下は静的検査(CHECKED_DIRS)対象外のため、行事名・群集ロジックは「置いてよい」設計(annual.py:9-11 の契約注記)。ただし EnvPack 化の観点では events(日付・行事名)と gathering_node(原点=ランドマーク仮定)は環境固有=pack へ移すべき。

---

## 6. EnvPack 化の実務メモ(調査から派生した所見)

- **最優先 seam(W2 プロンプト直書き)**: deliberate.py:14 ヘッダ / diversity.py:142 / persona.py:147-152 / map.py:164 / schedule.py:49-51 / media.py:60-65。いずれも `cfg.culture.lexicon.place_name` 等へ差し替え可能。deliberate.py:14 は `_COMMON_HEADER`=キャッシュキー基準なのでゴールデン・バイト一致に注意。
- **座標系仮定(env固有・要注意)**: 「地図原点(0,0)=ランドマーク」の前提が annual.gathering_node(:62-66)・synth_crowd・export_ue に共通。EnvPack manifest の `origin: {node: <スクランブルのノードid>}`(foundation-extraction.md:49)で吸収する設計と整合。
- **制度値(W3)**: government.py の税率・予算・給付は conf 未上書き=コード既定が本番で効く。institutions ブロック(min_wage/tax/council/deposit)へ集約すべき筆頭。
- **再配布制約**: ODPT(transit_odpt.json + odpt/ + odpt_challenge/)と OSM(shibuya_osm*.json=ODbL)は EnvPack に実体でなく取得レシピ(fetch_odpt.py / build_map.py 参照)を同梱する方針が既に確立。sentiment_lexicon.json は基盤(言語=ja)側の資産でクレジット明記により再配布可。
- **言語 seam(未着手)**: プロンプト・曜日(calendar.py)・感情辞書(sentiment.py)・「日本語が既定」前提(diversity.py)は lang=基盤設定として分離が必要(foundation-extraction.md:27 の「言語=基盤設定(lang)」方針)。W5 の別環境(下北沢/吉祥寺=同一言語圏)では露見しないため、真の多言語対応は別途検出器が要る。
