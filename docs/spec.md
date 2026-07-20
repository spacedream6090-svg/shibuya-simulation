# shibuya-simulation 仕様書(全体像・階層マップ)

> 本書は「これまで実装したもの」と「これから実装するもの」を一枚に束ね、**いま実装がどこを
> 進めているのかを階層的に**示すための仕様書。読者=プロジェクトオーナー(研究責任者)。
> 正典は [`design.md`](./design.md)・[`log/devlog.md`](./log/devlog.md)(全 Entry)・[`risk-register.md`](./risk-register.md)。
> 本書は根拠(ソース・conf キー・テスト・plans/research)へのリンクを添える。推測箇所は「要確認」と明記した。
> 最終更新の基準: devlog Entry 30(2026-07-20)/ フルスイート **1065 緑**。

## 状態マーカーの凡例

| 記号 | 意味 |
|---|---|
| ✅ | 実装済み・**既定 ON**(`conf/config.yaml` の既定挙動) |
| ☑ | 実装済み・**既定 OFF**(本番 `production.yaml` / 実験プロファイルで切替。OFF 時はゴールデン L1 バイト一致) |
| 🔨 | 実装中(現在の主戦場) |
| 📋 | 計画済み・未着手(設計文書あり) |
| 💤 | 保留(発動条件・ユーザー判断待ち) |

---

## 1. プロジェクト概要

### 1.1 研究目的
> **世界を変えようとする個体は、生まれつき存在するのか、環境から創発するのか。** [`README.md`](../README.md) / [`design.md`](./design.md)

- **被説明変数 Y** = 4層(空間 / 資源 / 象徴 / social network)への**連続的な書き換え量**(客観カウント)。
- **k** = 経験→内部状態の結合強度。主軸=ソロ内省での**信念の書き戻し自由度** `k.writeback`(`free | degraded | sham | off`)。
- **R²(k)**: Y を初期 traits で回帰した決定係数を k で掃引。高 R²=初期条件支配(生得寄り)/ 低 R²+経路依存=創発レジーム。
- **相転移点 k\***: R² 低下・seed 発散・早期警戒シグナル(EWS)の三角測量で探す。実装=[`observer/measure.py`](../src/society/observer/measure.py) `r2_traits()` / `ews()`。
- **追加研究目標**(2026-07-19): 組織の自然形成+**ファウンダー成立条件**の観察(memory: org-emergence-goal)。観測装置=[`scripts/analyze_founders.py`](../scripts/analyze_founders.py)。

### 1.2 体制・運用方針
- **本番方針**: 現実渋谷の忠実再現が土台(人数 > 実行時間)。選挙=名簿制。サービス提供者も全員エージェント(memory: realism-first-scale)。
- **世界観**: 自然界を模したボトムアップ創発を第一候補に(memory: nature-like-systems)。
- Fable 5 主(agent-core・エンジン中核)/ Opus サブ(並列リサーチ・独立ファイル)。検収は Fable が自走 pytest で確定(memory: agent-operating-mode)。

### 1.3 R1 ドクトリン(不変原則)— 全機能が守る
| 原則 | 内容 | 担保 |
|---|---|---|
| **既定 OFF=ゴールデン一致** | 新機能は既定 OFF。OFF 時に L1 イベント列が**バイト一致**する | [`tests/data/golden_baseline_l1.json`](../tests/data/golden_baseline_l1.json) / [`tests/test_scenario.py`](../tests/test_scenario.py) |
| **新機能=新 stream** | 追加乱数は専用 stream で引き、既存 draw 順を汚さない | 各機能の `stream(...)` |
| **呼数 k 非依存** | 追加 LLM 呼び出しゼロ(= k 掃引で交絡しない) | `_FixedLLM` 回帰テスト |
| **no-fingerprint(R9)** | engine は因子名を見ず、factors から不透明値のみ受け取る | [`tests/test_contracts.py`](../tests/test_contracts.py) |
| **k-blind / compute-matched** | co-location を変える機能でも `free==off` の k 不変性で担保(sham/null/compute 一定対照) | [`conf/config.yaml`](../conf/config.yaml) `controls` |
| **判定の循環回避(R4)** | 世界改変=客観カウント。LLM-judge は補助(κ≥0.7)・本体へ逆流しない | [`scripts/judge.py`](../scripts/judge.py) |

### 1.4 決定論
- 中央集権シード [`rng.py`](../src/society/rng.py)(PCG64・順序非依存)+ 応答キャッシュ [`llm/cache.py`](../src/society/llm/cache.py)。
- 1 step = 10 分・144 step = シミュ内 1 日 [`world/clock.py`](../src/society/world/clock.py)。scheduler は agent_id 昇順適用 [`engine/scheduler.py`](../src/society/engine/scheduler.py)。
- 実験条件はコードでなく `conf/experiments/*.yaml` で宣言(D11)。

---

## 2. 世界層(world)— [`src/society/world/`](../src/society/world/)

| 機能 | 状態 | 説明 / 根拠 |
|---|---|---|
| 地図(OSM 実道路網) | ✅ | 基底=`data/shibuya_osm.json`(渋谷駅中心 約1.0×0.7km・建物1,181)。[`world/map.py`](../src/society/world/map.py)。垂直レイヤ(-1 地下街 / 0 地上 / 1 デッキ)・車ゲートウェイ |
| 広域地図 wide_v7 | ☑ | 本番=`data/shibuya_osm_wide_v7.json`(2.0×2.0km・POI≈1,965・建物7,210・hotel/cinema/hall/landmark/school)。`world.map`(production.yaml) |
| 経路探索 A* + OD キャッシュ | ✅ | [`world/routing.py`](../src/society/world/routing.py)。mode 別サブグラフ(walk/bicycle/car)・封鎖 invalidate・到達不能は徒歩フォールバック |
| 知覚(空間ハッシュ) | ✅ | [`world/perception.py`](../src/society/world/perception.py) `PerceptIndex`(cell=perception_radius・近傍9セル走査・legacy O(n²) とバイト一致)。会話可聴=半径40m×同一階 |
| 擬似視覚 LOS(壁遮蔽) | ☑ | [`world/vision.py`](../src/society/world/vision.py)。建物 id+階から手続き生成した壁+開口部で視線判定。`world.vision.enabled`(本番 ON)/ `outdoor` は重く据え置き。設計=[`research/vision-los.md`](./research/vision-los.md) |
| 交通 ambient モード | ✅ | [`world/traffic.py`](../src/society/world/traffic.py)。通過車両を実規模で流す(`cars_per_day: 30000`)。`world.traffic.mode: ambient` |
| 交通 od モード(車個体化) | ☑ | 各車が起終点ゲートウェイ・一方通行尊重・**信号**(ノード別期待待ち)・**車線容量**(超過で渋滞減速)。要 `data/traffic_features_shibuya.json`。`world.traffic.mode: od`(本番 ON=信号69基・一方通行295区間が初結線) |
| 交通機関(定刻ダイヤ) | ✅ | [`world/transit.py`](../src/society/world/transit.py)。退出/帰還の運行時間制約(終電後は帰れない)。基底=近似ダイヤ `data/transit_shibuya.json` |
| GTFS/ODPT 実ダイヤ | ☑ | `transit.gtfs_dir` 指定で実ダイヤ化。本番=`data/transit_odpt.json`(メトロ3路線=ODPT実ダイヤ+他6路線近似)。取得=[`fetch_odpt.py`](../scripts/fetch_odpt.py)/[`build_transit_odpt.py`](../scripts/build_transit_odpt.py)。JR東 GTFS は未投入(受け皿実装済み) |
| タクシー / 簡易バス | ✅/☑ | [`transit_ride`](../conf/config.yaml)。taxi=既定 ON(本番は現実較正で `prob 0.02`)。bus=既定 OFF(本番 ON・fare 230) |
| 信号 | ☑ | od モード内で決定論的赤率→期待待ち。**歩行者は信号に無関係**(監査済み・batch37)。ambient では未結線 |
| 摂動シナリオ | ☑ | [`world/scenario.py`](../src/society/world/scenario.py)。baseline(no-op)/ shock_closure(道路封鎖→迂回)/ shock_event(ニュース注入)。`world.scenario` |
| 暦・天気 | ☑ | [`world/calendar.py`](../src/society/world/calendar.py) + [`weather.py`](../src/society/weather.py)。`world.calendar`(平日勤務)・`weather`(雨→grievance)。本番 ON |
| PLATEAU 実形状(建物LOD2/地形DEM/地下街/橋) | ☑ | 抽出=[`plateau_extract.py`](../scripts/plateau_extract.py)(LOD2/LOD1・DEM ground0・地下街/橋 extras)。照合=[`match_plateau.py`](../scripts/match_plateau.py)(重心k-NN→ラスタ IoU≥0.4)。wide_v7 で 3,531棟マッチ(IoU中央値0.633)。テスト: [`test_plateau_extract.py`](../tests/test_plateau_extract.py)/[`test_match_plateau.py`](../tests/test_match_plateau.py)。**ビューア統合は §7**。世界ジオメトリとしての in-sim 利用(D6)は 📋 |
| SUMO 車交通連携 v0 | ☑ | [`sumo_pipeline.py`](../scripts/sumo_pipeline.py)。**5段**(check→net→demand→run→convert)オフライン合成。公式版 1.27.1 で v0 全段完走(車6,449・軌跡99,662)。テスト: [`test_sumo_pipeline.py`](../tests/test_sumo_pipeline.py)。ガイド=[`guides/sumo-setup.md`](./guides/sumo-setup.md)。**歩行者は不採用**(striping 不向き)。ライブ連成 v1 は 📋(go/no-go 文書化済み) |

---

## 3. 認知層(cognition)— [`src/society/cognition/`](../src/society/cognition/)・[`factors/`](../src/society/factors/)

| 機能 | 状態 | 説明 / 根拠 |
|---|---|---|
| LOD 発火ゲート(驚き/予測誤差) | ✅ | [`cognition/lod.py`](../src/society/cognition/lod.py)。`lod.max_llm_per_step: 300`・発火率≈4-11%(≈LLM 呼数 1/12) |
| routine(非LLM 実行) | ✅ | [`cognition/routine.py`](../src/society/cognition/routine.py)。EPR 移動則+計画駆動の行き先。テレポート禁止(道なり連続移動) |
| deliberate(LLM 熟慮) | ✅ | [`cognition/deliberate.py`](../src/society/cognition/deliberate.py)。JSON 構造化出力。発話は**必ず LLM**(定型文なし・予算切れ=沈黙) |
| 内省=k の実装部位 | ✅ | [`cognition/reflection.py`](../src/society/cognition/reflection.py)。書き戻しゲート=beliefs のみ=k 境界。`reflect` イベント。`reflect_think: false`(思考モードは belief 全滅バグのため本番 OFF) |
| 朝の一日計画 | ✅ | [`cognition/planning.py`](../src/society/cognition/planning.py)。`planning.enabled: true`。起床時1回 LLM→routine の行き先の土台。呼数 k 非依存 |
| **S1 日課計画フレームワーク** | ☑ | 型スキーマ(自由文 intent 先頭+3分類 cat+flex)+アンカー先置きコンパイラ+失敗の階段(修復→再試行→前日流用)。[`cognition/plan_schema.py`](../src/society/cognition/plan_schema.py)。`planning.framework.enabled`。`day_plan_compiled` イベント。設計=[`research/daily-plan-framework.md`](./research/daily-plan-framework.md) |
| **S2 ナラティブ補間** | ☑ | イベントログ→機械ダイジェスト(有界リングバッファ30件)を全 LLM 推論へ注入+夜内省で物語化。`prompts.interstitial.enabled`。追加呼ゼロ |
| **S4 確率的実行(行動のゆらぎ)** | ☑ | L1 motif(novelty 15%)/L2 ±30分ジッター/L3 寄り道 per-move(実測0.153)/中断/Gumbel ロジット化(温度=活動3分類固定)。`routine.stochastic`。専用 stream 5本。較正=[`research/interstitial-life.md`](./research/interstitial-life.md) §4.1 |
| **S5 退屈/好奇心ドライブ** | ☑ | 同一ノード長居で退屈ゲージ蓄積→閾値+cooldown で内発的探索(未訪問優先=脱馴化→novel_place 鋭敏化)。[`cognition/drive.py`](../src/society/cognition/drive.py)。`drive.boredom`。stream `boredom` 1本 |
| 欲求駆動発火(drive) | ✅ | [`cognition/drive.py`](../src/society/cognition/drive.py)。出来事→ゲージ→個人閾値→重み抽選→不発30%減衰。`drive_request` イベント |
| 内省ドリフト E2(馴化/鋭敏化) | ☑ | 実効閾値が経験で動く。`drive.drift`(本番 ON)。設計=[`research/reflection-drift.md`](./research/reflection-drift.md) |
| 出来事誘発の深い内省 + 無意識自己 | ☑ | 日内衝撃ゲージ→侵入的→熟慮的の遅延二段+行動ベースライン逸脱の「最近の自分」。`reflection.deep` / `reflection.implicit_self`(本番 ON)。[`research/deep-reflection-triggers.md`](./research/deep-reflection-triggers.md) |
| 記憶(push 型日常) | ✅ | [`agents/memory.py`](../src/society/agents/memory.py)。Generative Agents 式検索・consolidate |
| 記憶 agentic pull | ☑ | 発火・内省で能動想起1行(固定2段=呼数 k 不変)。`memory.agentic_pull`(本番 ON) |
| 記憶 ACT-R 活性化(忘却/想起失敗/fan干渉) | ☑ | 基礎活性化 d=0.5・τ=-2・fan 干渉・忘却下限。`memory.actr.enabled`(本番 ON)。`memory_fail` イベント。[`research/memory-cognitive-research.md`](./research/memory-cognitive-research.md) |
| affect(覚醒+顕著性の統一ハブ) | ☑ | arousal スカラ+salience 上位K ゲート+逆U字閾値変調。`affect`(本番 ON)。[`lit/neuroscience__emotion-interest-attention.md`](./lit/neuroscience__emotion-interest-attention.md) |
| 内面本格版(感情ラベル/長期目標/趣味) | ☑ | [`inner_life.py`](../src/society/inner_life.py)。`inner_life`(本番 ON・hobbies.leisure_bias 0.3)。長期目標=keystone 駆動源 |
| 主観的世界モデル(期待/可制御性/規範予期) | ☑ | [`worldview.py`](../src/society/worldview.py)。C1 期待EMA / C2 可制御性 / C6 規範予期。`worldview.enabled`(本番 ON)。`worldview` イベント。[`research/world-models.md`](./research/world-models.md) |
| 欲求プロファイル個人差(needs) | ☑ | traits/年齢/職業→5次元価値→感度倍率。`needs`(本番 ON)。[`lit/needs__individual-differences.md`](./lit/needs__individual-differences.md) |
| 心理プラグイン(SDT/集団効力感/Lynch/Searle) | ☑ | [`factors/psych.py`](../src/society/factors/psych.py)。`psych.*`(本番 sdt/collective/lynch ON) |
| 入力解像度 LOD(世界への解像度の個体差) | ☑ | [`cognition/lod.py`](../src/society/cognition/lod.py) 共通軸機構。知覚/記憶/フィード注入件数を水準別に。`lod.input_res`(本番 ON)。設計=[`plans/input-resolution-lod.md`](./plans/input-resolution-lod.md) |
| state 更新則(no-fingerprint) | ✅ | [`factors/update.py`](../src/society/factors/update.py)(因果構造)+ `conf.factors`(量)。8ルール・Bandura4源泉。SIMCA 接地 |

---

## 4. 社会層

| 機能 | 状態 | 説明 / 根拠 |
|---|---|---|
| 会話(発話・返答保証・非ブロードキャスト) | ✅ | [`conversation.py`](../src/society/conversation.py)。対面=確定発火+返答保証(`conv_max_turns`) |
| **S3 会話3層(C1/C2/C3)** | ☑ | C2=構造化会話(Dialogue Act 決定論遷移・実文なし)→関係/意見/語彙/drive へ機械効果。既定密度 **30.9会話/人日**。C2→C1 昇格=drive 経由。[`conversation.py`](../src/society/conversation.py)。`conversation.c2`。stream `c2_meet`・`conversation` イベント |
| SNS(投稿/TL/いいね/リシェア/フォロー) | ✅ | [`net/internet.py`](../src/society/net/internet.py)。`net.enabled: true`。投稿=LLM・like/reshare=非LLM専用stream。DM・ニュース・検索(シミュ内DB) |
| SNS 推薦/バイラル/炎上(情報環境の非対称) | ☑ | [`net/infoenv.py`](../src/society/net/infoenv.py)。推薦=意見整合バイアス(エコーチェンバー)/influence=高フォロワー reach 加重/misinfo=誤情報・訂正・炎上。`info_env.*`(本番 ON) |
| 意見力学(Friedkin-Johnsen) | ✅ | [`opinion.py`](../src/society/opinion.py)。`opinion.enabled: true`。face/dm/sns 別の説得重み。`opinion_shift` |
| 関係の質(tier/断絶/評判/派閥) | ☑ | [`relations.py`](../src/society/relations.py)。closeness weight→tier(見知らぬ/知人/友人/親友)・評判・faction。`relations.enabled`(本番 ON) |
| 社会的ヒエラルキー(地位=信用) | ☑ | [`status.py`](../src/society/status.py)。客観カウント百分位→合成地位 status→集客/加入/購買/露出を変調(injection 禁止=可視化のみ)。`hierarchy.enabled`(本番 ON) |
| 語彙/造語の伝播(自然観察) | ✅ | [`labeling/labels.py`](../src/society/labeling/labels.py)。complex contagion(採用閾値2)。`labeling.mode: constrained`。造語は促進せず coin 文脈を記録(memory: natural-coinage-observation) |
| 「世界を変える」ツール群(4軸) | ✅ | [`tools.py`](../src/society/tools.py)。モノ=open_venture / 制度=propose / 人=host_event / 虚構=flyer・group。`tools.enabled: true`。R4 客観カウント。本番=`equip_all`+営業許可 permit |
| 制度DSL(ホワイトリスト rule 自動制定) | ✅ | [`rules.py`](../src/society/rules.py)。fee/bonus/curfew/weekly_event の4型+declare(本番 ON)。署名25%成立→実効ルール化 |
| 再帰性(監視→知覚→改変の閉ループ) | ☑ | [`recursion.py`](../src/society/recursion.py)。実効ルール/前日の街の動きを注入・repeal・執行のニュース化。`recursion.enabled`(本番 ON) |
| 組織/団体(職場・学校台帳・配属) | ☑ | [`organizations.py`](../src/society/organizations.py)。配属→production/study・所属1行・org会計。`organizations.enabled`(本番 ON・commute_to_poi)。台帳=`data/organizations_shibuya_wide11k.json`(11,010組織) |
| 行政(区/都/国の税・給付・公務員給与) | ☑ | [`government.py`](../src/society/government.py) + [`institutions.py`](../src/society/institutions.py)(制度値外出し)。所得税/住民税/消費税・生活困窮者給付。`government.enabled`(本番 ON) |
| 議会(名簿制=本番 / 選挙=実験) | ☑ | [`tools.py`](../src/society/tools.py) `elect_assembly`/SNTV/供託金/議会予算承認。**本番=名簿制**(`assembly.from_roster: true`・persona occupation=議員を据える)。**選挙 realism**(自発立候補・供託金没収・告示期間)は実験用に温存(`assembly.realism.enabled: false`)。決定=memory / devlog Entry 18-20 |
| 制度改変の3ルート(労働争議/投票/執行/審議) | ☑ | [`institution_routes`](../conf/config.yaml)。labor/vote(供託金)/enforcement(罰金・拘束)/deliberation(否決可能な熟議)。本番 ON |
| 経済 v0(賃金/消費/バイト/逼迫→心理) | ✅ | [`economy.py`](../src/society/economy.py)。`economy.enabled: true`。職業→賃金・消費価格・money_pressure→grievance |
| 経済深化(口座/決済/銀行/VC/家賃/自営) | ☑ | accounts(月給・家賃引落・ATM・立退き・破産)/consumption(家計調査較正)/payment(キャッシュレス42.8%)/bank(利息・与信・融資→破産接続)/vc(出資・持分・配当)。本番 ON。[`research/economy-abm-research.md`](./research/economy-abm-research.md) |
| キャリア転換(転職/失業/起業転換) | ☑ | `career`(本番 ON・現実較正で低確率)。解雇規制(退職金・不当解雇) |
| 世帯・家族・恋愛 | ☑ | [`household.py`](../src/society/household.py)。世帯グループ化・同居 co-location・パートナー形成(要 relations)。`household.enabled`(本番 ON) |
| 商業ダイナミクス(営業時間/動的価格/在庫) | ☑ | [`commerce.py`](../src/society/commerce.py)。`commerce.enabled`(本番 ON) |
| 健康(疲労/病気/メンタル) | ☑ | [`health.py`](../src/society/health.py)。`health.enabled`(本番 ON) |
| 都市ショック(災害/運休/停電) | ☑ | [`disaster.py`](../src/society/disaster.py)。`disaster.enabled`(本番 ON / **daily は OFF**=日常を壊さない) |
| 観光/多言語/犯罪・治安 | ☑ | [`diversity.py`](../src/society/diversity.py)。tourist/foreign/crime/nuisance/危険地帯回避。`society_diversity`(本番 ON・現実較正) |
| 娯楽メディア(TV/動画/ゲーム) | ☑ | [`media.py`](../src/society/media.py)。在宅娯楽・気分修復。`media.enabled`(本番 ON) |
| 宿泊・ホテル滞在 | ☑ | [`lodging.py`](../src/society/lodging.py)。来街者の夜間泊。`lodging.enabled`(本番 ON) |
| 街頭広告 OOH / 群衆視覚 / SNS地理 | ☑ | [`media.py`](../src/society/media.py)ads・`crowd_visual`・`sns_geo`(本番 ON) |
| 生活の自己決定 P2(転居/消費意思/聴講/交際/逸脱) | ☑ | [`freedom_p2.py`](../src/society/freedom_p2.py)。`freedom.p2.*`(本番 ON=ファウンダー前駆の観察) |
| 開放行動 "do" + 価値4軸 | ☑ | [`values.py`](../src/society/values.py)。LLM 自由記述行動+実用/感情/社会/認識で観測。`freedom.open_actions`(本番 ON) |

---

## 5. スケール基盤(W2)— 正典 [`plans/w2-execution-plan.md`](./plans/w2-execution-plan.md)

**設計転換(2026-07-19)**: 旧3-tier(背景=統計行動)を廃し**全員思考モデル**へ。在場全員に朝計画+夜内省を LLM 保証、日中は自己計画駆動、顕著性駆動の追加熟慮(drive ゲート全員適用・予算 N 比例)。副次的利得=動的昇格の k\* 交絡が構造的に解消(devlog Entry 22)。

### 5.1 パッケージ P0〜P7

| P | 内容 | 状態 | 根拠 |
|---|---|---|---|
| **P0** | エンジン実測ベースライン(規模別 c・ホットスポット特定) | ✅ | devlog Entry 25。N=300 で c=0.00042・**超線形** c∝N^0.6-0.73・主犯=SNS TL 順位付け O(閲覧者×投稿) |
| **P1** | 背景 SoA + hydrate 基盤(★可否ライン) | 🔨 | 純オーバヘッド除去は着地(devlog Entry 27: 300体 0.00042→0.000238 / N=3000 **4倍改善** 0.00166→0.000418=超線形を線形圏へ)。10000体深夜帯 c=0.000528=線形圏(devlog Entry 33 前後の実測)。**hydrate/dehydrate は P3 の DormantStore が実装**(Entry 33)・**z列(3D Phase 0)は着地**([`world/elevation.py`](../src/society/world/elevation.py)=DEM 双一次 O(1)・`world.elevation.enabled` 既定 OFF・ON で move_segment/arrive に z)。SoA 配列化本体は P3 のスリム化で要否再評価。Fable 直営 |
| **P2** | 全員思考機構(=行間レイヤ S1-S7) | 🔨 | §5.2 参照。S1-S5+S6a 完了・S6b 実装中・S7 並行実装中 |
| **P3** | ローテーション(日次入替・純関数 presence・resume 決定論) | 📋 | 全 devlog で「残」留置・着手記録なし。src に `presence`/`present_cap` 不在。[`plans/persona-pool.md`](./plans/persona-pool.md) §1.3 |
| **P4** | 観測ストリーミング(row-group 逐次・保存ポリシー) | ✅ | devlog Entry 25。合成2,000万件で検収・ピーク 786MB(<2GB PASS)・4.68億件でも同水準見込み。[`observer/stream.py`](../src/society/observer/stream.py) |
| **P5** | ペルソナ100万生成(層分担・議員名簿投入) | ✅ | devlog Entry 27。内訳=§5.3。実体736MB は gitignore・LLM 上塗り対象 24,020 件出力 |
| **P6** | 組織台帳 52→1.1万 | ✅ | devlog Entry 25。11,010組織・従業者総和252,311(目標±2%)・POI 割付100% |
| **P7** | 本選ベンチ+段階昇圧(vLLM bench serve・1万→5万→10万→25万) | 📋 | 現物待ち。[`plans/finals-hardware-plan.md`](./plans/finals-hardware-plan.md) §2 Day-0 プロトコル。ハッカソン期間中に実施 |

**P1 可否ライン**(要確認): go/no-go は「背景 c ≤0.0002〜0.0006」([`plans/w2-execution-plan.md`](./plans/w2-execution-plan.md) §5)。「0.0002 目標が射程」と記録するが SoA 本体未実装のため**最終確定は未**。

### 5.2 行間レイヤ S1〜S7 — 正典 [`plans/p2-interstitial-design.md`](./plans/p2-interstitial-design.md)

| S | 内容 | 状態 | 根拠(緑本数) |
|---|---|---|---|
| **S1** | 日課計画フレームワーク(型スキーマ+コンパイラ+失敗の階段) | ☑ | devlog Entry 29(1041緑)。`planning.framework` |
| **S2** | ナラティブ補間(機械ダイジェスト全注入) | ☑ | devlog Entry 27(1019緑)。`prompts.interstitial` |
| **S3** | 会話3層(C2 構造化会話=30.9/人日) | ☑ | devlog Entry 28(1034緑)。`conversation.c2` |
| **S4** | 確率的実行(motif/ジッター/寄り道/Gumbel) | ☑ | devlog Entry 29(1052緑)。`routine.stochastic` |
| **S5** | 退屈/好奇心ドライブ | ☑ | devlog Entry 30(1065緑)。`drive.boredom` |
| **S6a** | 顕著性予算の N 比例化(cap=ceil(0.15×N) 置換) | ☑ | [`lod.n_proportional`](../conf/config.yaml)・[`test_lod_proportional.py`](../tests/test_lod_proportional.py)。P3 導入後に N=思考層在場数へ拡張 |
| **S6b** | LLM/エンジン重畳実行(非同期バッチ発行・apply 順序保存) | 🔨 | Fable 直営で実装中。day_schedule→実行の精緻配線も同時。scheduler 側未配線 |
| **S7** | 方針キャッシュ(k非依存 near-match 再利用で呼数-40〜57%) | 🔨 | 並行実装中(Opus)。ユーザー承認=実装するが**既定 OFF 運用**・本番採否は比較実験(devlog Entry 26)。関門=呼数 k 非依存+ブラインド A/B |

> 記録に残る認知・社会イベント(ON 時)= 朝計画1+夜内省1+熟慮~6+C2会話~30+寄り道等 ≈ **~40/人日**(現実の「1日数十回の相互作用」レンジ・devlog Entry 28)。全スライス既定 OFF=ゴールデン L1 バイト一致・呼数 k 非依存。

### 5.3 ペルソナ100万プール(実生成内訳)— [`data/persona_pool/meta.json`](../data/persona_pool/meta.json)

| 層 | 人数 | 内容 |
|---|---|---|
| L1 住民 | 30,000 | 夜間人口(回転しない) |
| L2 域内従業者 | 253,702 | 組織台帳需要と整合 |
| L3 定期来街 | 36,690 | 通勤・常連 |
| L4 非定期来街(回転主層) | 678,588 | 観光・単発 |
| L5 役割ペルソナ | 1,020 | 議員34(渋谷区議会実定数)含む |
| **合計** | **1,000,000** | seed 42 決定論・生成器 [`build_persona_pool.py`](../scripts/build_persona_pool.py) |

---

## 6. 観測・解析層(observer)— [`src/society/observer/`](../src/society/observer/)

| 機能 | 状態 | 説明 / 根拠 |
|---|---|---|
| L1 イベント(正準スキーマ+レジストリ) | ✅ | [`observer/schema.py`](../src/society/observer/schema.py) `register_event_kind`。route_start/speak/hear/vocab_coin/transmission/reflect/... Parquet+zstd |
| L1b LLM / L2 metrics / L3 snapshot | ✅ | [`observer/logger.py`](../src/society/observer/logger.py)。`observer.snapshot_every: 12`。D16 セグメント化(checkpoint 連携) |
| 伝播系譜(transmission) | ✅ | [`observer/provenance.py`](../src/society/observer/provenance.py)。item ごとの from→to チャネル→カスケード木の完全再構成 |
| 集計プラグイン(崩壊検知/均質化ドリフト) | ✅ | [`observer/aggregate.py`](../src/society/observer/aggregate.py)。type-token 比・文字3-gram・Jaccard |
| ストリーミング集計(有界メモリ) | ✅ | [`observer/stream.py`](../src/society/observer/stream.py)(P4)。measure とバイト同一 |
| 計測(agent/item/network/collective) | ✅ | [`observer/measure.py`](../src/society/observer/measure.py) |
| **R²(k)**(世界改変量を traits で回帰) | ✅ | [`observer/measure.py`](../src/society/observer/measure.py) `r2_traits()`(external/internal) |
| **EWS**(分散・lag1自己相関・Kendall τ) | ✅ | [`observer/measure.py`](../src/society/observer/measure.py) `ews()` |
| カスケード深さ | ✅ | `item_cascades()` |
| k 掃引 / FSS | ✅ | [`run_sweep.py`](../scripts/run_sweep.py)(単一N/複数N=有限サイズスケーリング)→[`analyze_sweep.py`](../scripts/analyze_sweep.py)(R²(k) seed 階層ブートストラップCI・EWS・seed 発散・計算量交絡監査) |
| founder 検出 | ✅ | [`analyze_founders.py`](../scripts/analyze_founders.py)(後処理)。venture / political / hub(媒介中心性・次数・到達)founder を行動から検出 |
| 較正(calibrate_report) | ✅ | [`calibrate_report.py`](../scripts/calibrate_report.py)(後処理)。現実一次統計の近似バンドと対比。原則=production.yaml 重ね書きのみ(基底ゴールデン不変) |
| 人流ヒート/OD/混雑(W1-W2) | ✅ | [`analyze_flows_grid.py`](../scripts/analyze_flows_grid.py)(25mメッシュ×1h・FruinのLOS)/[`analyze_od.py`](../scripts/analyze_od.py)(OD行列)/[`compare_runs.py`](../scripts/compare_runs.py)(CRN+DiD・置換検定・BH-FDR) |
| 創発検出 / LLM要約(W4) | ✅ | [`detect_emergence.py`](../scripts/detect_emergence.py)(作話/創発名/実在名の3値・接地率)/[`summarize_run.py`](../scripts/summarize_run.py)(数値照合ガード=R4防壁) |
| 実行時間試算 | ✅ | [`estimate_runtime.py`](../scripts/estimate_runtime.py)(体数×日数→LLM所要外挿・--fleet プリセット) |
| LLM-judge(補助) | ✅ | [`judge.py`](../scripts/judge.py)。Fleiss κ・本体逆流なし |

---

## 7. 可視化 — [`viz/`](../viz/)

| 機能 | 状態 | 説明 / 根拠 |
|---|---|---|
| 2D ビューア(地図+ダッシュボード) | ✅ | [`viz/make_viewer.py`](../viz/make_viewer.py)。OSM タイル・レイヤー・再生・フロアビュー・X風SNS/LINE風DM/SERP風検索/論文風グラフ |
| 3D ビューア(自己完結 HTML・three.js) | ✅ | [`viz/make_viewer3d.py`](../viz/make_viewer3d.py)。ACES ライティング・**無彩色既定**+分類色トグル・地形接地・地下橋描画・**移動手段グリフ** |
| PLATEAU 実形状統合 | ☑ | [`export_3d.py`](../scripts/export_3d.py) `--plateau`(ハイブリッド glb・実測メッシュ置換)。巻き向き修正済み(符号付き体積・DoubleSide)。埋込/分離/glb の3形式(≤80MB ゲート)。出典を HUD 表示 |
| 地形起伏(DEM 2m格子)・地下街・歩道橋 | ☑ | V-A 抽出=交差点谷底0m・道玄坂+12.2m・地下街 z-14.3m・歩道橋39基(devlog Entry 17) |
| ハブ統合ビューア | ✅ | [`viz/make_hub.py`](../viz/make_hub.py)。3D/2D/ダッシュ/ヒート/OD/群集/要約を1枚に集約 |
| 群衆物理(SFM オフライン) | ☑ | [`viz/sfm.py`](../viz/sfm.py)(Helbing 式・自前実装)+[`synth_crowd.py`](../scripts/synth_crowd.py)。低中密度の揉まれ方の視覚実証 |
| Blender 取込 | ☑ | [`viz/blender_import.py`](../viz/blender_import.py)(bpy 遅延 import) |
| UE5 ガイド | ☑ | [`guides/ue5-quickstart.md`](./guides/ue5-quickstart.md)+[`viz/unreal/`](../viz/unreal/)([`export_ue.py`](../scripts/export_ue.py) `sim_ue.json`・ISM 配置)。200体は mode="sequence"=BP不要 |

---

## 8. 本番計画 — [`plans/million-scale.md`](./plans/million-scale.md) / [`plans/finals-hardware-plan.md`](./plans/finals-hardware-plan.md)

| 項目 | 計画値 | 根拠 / 注 |
|---|---|---|
| 在場人数(同時 present) | 平均 **~23.5万**(24h平均)/ 平日昼ピーク **~37.2万** | 国交省人流オープンデータ実測(devlog Entry 21)。従来推計(平均25万/ピーク35万)をほぼ検証 |
| ペルソナプール | **100万**(present と分離) | §5.3。区外流入≈74% |
| シミュ日数 | **10 シミュ日** | million-scale 確定方針 |
| 本選ハード | VRAM 総 **168GB**=24GB級×7(A5000級)・**単一ノード(構成A)**・**10日間** | 主催公表値。実効~21req/s(prefix cache×1.8で~38)。ops=[`launch-vllm-finals.ps1`](../ops/launch-vllm-finals.ps1) / プロファイル=[`profiles/finals-vllm7.yaml`](../conf/profiles/finals-vllm7.yaml) |
| 段階昇圧 | **1万→5万→10万→25万**(各段で wall/RAM/観測を実測) | [`plans/w2-execution-plan.md`](./plans/w2-execution-plan.md) P7 |
| 縮退線 | **まずシミュ日数を削る**(体数維持=人数>時間)。OOM/observer 破綻時のみ present_cap 25万→10万→5万→2.5万 | [`plans/finals-hardware-plan.md`](./plans/finals-hardware-plan.md) §3.1 |
| Day-0 プロトコル | ベンチ→当日規模決定→縮退線 | [`plans/finals-hardware-plan.md`](./plans/finals-hardware-plan.md) §2 |

> **未踏性**: 「25万同時 × 全員 LLM 思考」は公開最大(OASIS 10万・小モデル)を超える(両計画明記)。バックエンド=vLLM 艦隊 [`llm/fleet.py`](../src/society/llm/fleet.py)(agent_id sticky→prefix cache)。マルチモデル=[`llm/router.py`](../src/society/llm/router.py)(purpose 別・API 混載可)。

### 8.1 実行済みラン(実測の最大規模)
- **講演デモ**: 200体×3日・実LLM=238,993イベント・13,161呼・fallback 0.008%(devlog Entry 12)。
- **日常較正**: mock 300体×100日 / 実LLM 20体×7日=全項目現実バンド内(devlog compressed Block #5)。
- → **25万規模は計画段階(未実行)**。実スケール検証は P4 の合成2,000万件のみ(要確認)。

---

## 9. 付録

### 9.1 主要 conf キー(既定値 → 本番値)

| キー | 既定(config.yaml) | 本番(production.yaml) | 意味 |
|---|---|---|---|
| `run.n_agents` / `n_steps` | 10 / 144 | 100 / 14400(100日) | 規模・期間(daily は300体) |
| `model.backend` | mock | vllm(profile) | LLM バックエンド |
| `model.reflect_think` | true | **false** | 思考モード(true=belief 全滅バグ) |
| `k.writeback` | free | (実験で掃引) | k 主軸=内省書き戻し自由度 |
| `world.map` | shibuya_osm.json | wide_v7 | 地図 |
| `world.traffic.mode` | ambient | od | 車=幻→個体化 |
| `world.calendar.enabled` | false | true | 暦 |
| `planning.enabled` | **true** | true | 朝計画(既定 ON) |
| `economy.enabled` / `tools` / `rules` / `net` / `opinion` | **true** | true | 中核(既定 ON) |
| `organizations` / `government` / `relations` / `hierarchy` / `recursion` / `media` / `needs` / `affect` / `inner_life` / `worldview` / `health` / `household` / `commerce` / `disaster` / `career` / `info_env` / `lodging` | false | **true** | リアリズム機能(本番 ON) |
| `institution_routes.assembly.from_roster` | (false) | **true** | 名簿制議会(選挙しない) |
| `prompts.reflect_variety` | false | **false** | 丸写し悪化のため本番も OFF |
| `planning.framework` / `prompts.interstitial` / `conversation` / `routine.stochastic` / `drive.boredom` | false | (未投入) | 行間レイヤ S1-S5(実装済み・既定 OFF) |

> 実験ノブ(`controls` / `rewards` / `k.writeback` / `world.scenario` / `labeling.mode` / `observer.y_weights`)は production でも据え置き=k 掃引でラン毎に統制。

### 9.2 テスト・規模
- フルスイート **1065 緑**(devlog Entry 30)。テストファイル 121本([`tests/`](../tests/))。ゴールデン=[`tests/data/golden_baseline_l1.json`](../tests/data/golden_baseline_l1.json)。
- 依存(最小)=numpy / networkx / omegaconf / pyarrow([`pyproject.toml`](../pyproject.toml))。解析に matplotlib、実LLM に Ollama/vLLM。

### 9.3 文書マップ
- **設計正典**: [`design.md`](./design.md) / [`risk-register.md`](./risk-register.md)(R1-R19) / [`decision-agenda.md`](./decision-agenda.md)(D0-D17)。
- **開発ログ**: [`log/devlog.md`](./log/devlog.md)(ライブ)/ [`log/devlog-compressed.md`](./log/devlog-compressed.md)(Block #0-#6)。
- **計画(plans/)**: [`w2-execution-plan.md`](./plans/w2-execution-plan.md) / [`million-scale.md`](./plans/million-scale.md) / [`finals-hardware-plan.md`](./plans/finals-hardware-plan.md) / [`p2-interstitial-design.md`](./plans/p2-interstitial-design.md) / [`persona-pool.md`](./plans/persona-pool.md) / [`engine-architecture.md`](./plans/engine-architecture.md) / [`unimplemented-inventory.md`](./plans/unimplemented-inventory.md) / [`plateau-3d.md`](./plans/plateau-3d.md) / [`batch37.md`](./plans/batch37.md)。
- **リサーチ(research/, lit/)**: 63本 + 文献コーパス。主要=[`research/interstitial-life.md`](./research/interstitial-life.md) / [`research/3d-visualization.md`](./research/3d-visualization.md) / [`research/world-change-motivation.md`](./research/world-change-motivation.md) / [`research/off-features-inventory.md`](./research/off-features-inventory.md)。

### 9.4 保留・討議待ち・不採用 — [`plans/unimplemented-inventory.md`](./plans/unimplemented-inventory.md) / [`plans/pending-decisions.md`](./plans/pending-decisions.md)

| 項目 | 状態 | 注 |
|---|---|---|
| agent-tier LOD(M3・エージェント階層別モデル) | 💤 | 討議待ち。示唆=300体では不要・3k体級の後段([`research/agent-lod-deepdive.md`](./research/agent-lod-deepdive.md)) |
| 計算量削減 E2(INT4量子化・routine キャッシュ) | 💤 | E1 実測後(保留) |
| reality-levers P3(接地サブ集団・27B・LoRA) | 💤 | GPU 依存で保留 |
| A4 内省プロンプト改善(reflect_variety) | 💤 | 実装済みだが**当面 OFF**(丸写し33%で正味悪化・devlog Entry 9)。再ON条件=丸写し棄却ガード or reflect のみ8b |
| 本選デモ(3幕構成 D4) | 📋 | 本選前・中に実施 |
| 環境自動生成 make_env v1/v2 | 📋 | v0 完了(下北沢実証)。残=e-Stat IPF・LLM 一括+人手確認 |
| 3D 詳細移動(連続2.5D+層状グラフ) | 🔨 | リサーチ完了([`research/3d-visualization.md`](./research/3d-visualization.md))。**Phase 0(z列)は実装済み**(`world/elevation.py`・既定 OFF)・Phase 1 以降(歩行NW/SoA/前景SFM)は本選後 |
| ペルソナ深さ属性(P3) | — | **不採用決定済み**(manifold collapse 抵触)。他に archetype 集約 / RAP 木探索 / 動的モデルカスケード / <2B 背景利用も不採用 |

### 9.5 エンジン群アーキテクチャ(参考)— [`plans/engine-architecture.md`](./plans/engine-architecture.md)
5層再構成案(Agent / World / Society / Dynamics / Meta)。61エンジン照合で**約90%実装済み**(自己評価・要確認)。コード再編はせず対応表を [`architecture-layers.md`](./architecture-layers.md) に固定。**SUMO=車限定 P2**・**RL=不採用**(決定論と非整合)・**Ecology=作らない**。OPEN 4件はユーザー回答済み(Skill 蓄積の討議のみ後回し)。

---

## 10. 「要確認」項目一覧(捏造を避けるための正直な注記)

1. (解消済み 2026-07-20)S7 方針キャッシュは本書作成と並行して実装着手済み=🔨。S6a(N比例cap)も同日コミット済み=☑(§5.2 に反映)。
2. **P1 SoA 可否ライン**: 純オーバヘッド除去・z列・hydrate(P3 DormantStore)は着地。10000体深夜帯 c=0.000528=線形圏で 25万外挿~5-10h/シミュ日=予算圏内。SoA 配列化本体は**P3 スリム化で RAM 問題の大半が解決したため要否再評価**(昼帯大 N の再計測が残)。
3. **本選ハードの正確な世代**: 168GB=24GB×7 は確度高いが、A5000 24GB か RTX 5000 Ada 32GB かは**銘板未確認**([`plans/finals-hardware-plan.md`](./plans/finals-hardware-plan.md) [要確定])。占有/共有・ホスト RAM も未確認。
4. **在場25万規模は未実行**: 実測の最大は 200体(実LLM)/300体(mock)。25万×全員思考はスケール計画上の目標値で、実スケール検証は P4 の合成2,000万イベントのみ。
5. **人口周辺分布の一部が暫定**: 年齢5歳階級×性別・職業大分類の渋谷区実数は静的取得不成立([`data/shibuya_population.json`](../data/shibuya_population.json) `status: partially-real`)。性比・昼夜比・来街者比0.56は国調由来。
6. **エンジン90%実装は自己評価**([`research/engine-coverage-map.md`](./research/engine-coverage-map.md) の照合結果)。
7. **P3 ローテーション**は全 devlog で「残」留置・着手記録なし・src に実体なし=**未着手**と判断。
