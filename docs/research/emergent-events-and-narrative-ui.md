# 創発イベントの内生化と物語UI — 前例調査+設計案

作成: 2026-08-17(リサーチのみ・コード変更なし)
発端: ユーザーの問い「エージェントの行動から自ずとイベントが発生することはありえないか?」
+ 承認済みの観察強化3案(①ビューアのイベントフィード層 ②任意エージェントの1日トレース ③表現力底上げ)。

制約の正典: R1 ドクトリン(docs/plans/finals-day1-decisions.md)= 新機能は新streamのみ・
既定OFF=ゴールデンL1バイト一致・LLM呼数 k-blind・no-fingerprint・観測がシムを変えない
(PENDING.md §5.1 ⑥)。本書の全設計案はこの枠内で呼数影響を明記する。

---

## 0. 結論(先に要旨)

1. **「イベント」はトップダウンに発生させる必要がない。** 前例(Generative Agents のパーティ、
   Project Sid の宗教伝播)はいずれも「種→伝播→閾値→同時同所の到達」をボトムアップに辿り、
   *集まった事実を事後に計測*している。本リポには既にその部品が全部ある(§2)。
   欠けているのは (a) **主催者宣言なしの集合**(event_host は宣言が起点)と
   (b) **「集まった事実」を一般の場所・日で検出する観測器**(crowd_surge は年中行事日限定)。
2. 推奨は §3 の **案A(集合検知器=純観測)を最優先**、次いで **案B(意図台帳)**。
   どちらも LLM 呼ゼロ・乱数ゼロ・読み取り専用で R1 完全適合。**案C(Granovetter 閾値動員)**は
   世界を動かす内生機構として価値が最大だが既定OFF+finals判断。
3. イベントフィードは **NOTABLE_KINDS(viz/notable_events.py)と HIGHLIGHT_KINDS
   (scripts/live_viewer.py)の二重管理を単一レジストリへ統合**し、
   ランキング= importance(事前値)+希少度(自己較正)+magnitude+連鎖長+初回ボーナス
   −同一ストーリー重複ペナルティ、で層化する(§4)。
4. 1日トレースは L1(行為)+ l1b/llm_journal(思考全文)+ memory.parquet + day_plan 台帳を
   **「計画 vs 実行の突合」を骨格**に束ね、物語文はランの外の事後 LLM 1呼で生成する(§5)。

---

## 1. 前例調査(文献+GitHub・URL実在確認済み)

(子レーン3本の結果を §1-1〜§1-3 に統合する — 統合待ちプレースホルダ)

### 1-1. LLM 社会シムの創発イベント機構

(統合待ち)

### 1-2. 集合行為の閾値理論・群衆科学・ゲームAIの物語設計

(統合待ち)

### 1-3. ビューア/イベントフィード/トレースUIの実装実例

(統合待ち)

---

## 2. 本リポの現状棚卸し — 「もうイベントは起きている」部分と欠落

### 2-1. 既にある内生イベントのパイプライン(実装確認済み)

| 機構 | 実装 | 流れ | 集合性 |
|---|---|---|---|
| **イベント開催** | `src/society/tools.py`(host_event) | LLM が開催宣言 → 自動SNS告知(event_id付き)→ `sns_read`/DM で `_known_events` 伝播(scheduler.py L3346・tools.py L766)→ 開始時に全認知者を id 昇順で抽選 p = attend_base + 関係ボーナス + **status.attract**(status.py `attract_bonus` = attract_gain×主催者status)→ `event_attend` + 記憶 + 制度DSL bonus | **N者**(招待拡散→抽選→到達の完全なパイプライン。Generative Agents のパーティ伝播と同型) |
| **噂** | `src/society/rumors.py` | 構造化イベント5種(event_host / venture_open / enforcement / partner_formed / relation_break)→ `rumor_born`{item_id, **node**, knowers} → 既存 `transmission` に乗って伝播 → `rumor_stifle`(Maki-Thompson の stifler 化) | 伝播のみ(場所は持つが時刻を持たない) |
| **待ち合わせ** | appointment(会話からの自動記入) | `appointment`{day, when, what, place, **with**} → `appointment_kept`(時間帯×場所の在場で遵守判定) | **2者まで**(with が単数) |
| **共同行動** | `src/society/joint.py` ほか | `joint_invite`{invitee, verdict, p_calib, p_final, source(plan_with/dialog_cue/weak_tie/closeness/housemate/colleague)} → `joint_activity`{type, with, place} | グループ(同伴・世帯・同僚会食・party) |
| **群集検出** | `src/society/annual.py` `check_surge` | 年中行事の crowd 日のみ・固定集会ノード・半径 crowd_radius_m 内の在場数 ≥ crowd_threshold → `crowd_surge`(agent_id=-1・1日1回・乱数ゼロ・発火系非接続) | **検出器だが行事日+固定ノード限定** |
| **環境フィードバック** | `src/society/envfeedback.py` | 集約物理量(ホーム密度/改札飽和/POI占有)の閾値超過 → コード側発火 `env_feedback` | 「集約量→閾値→世界イベント」の**社内前例** |
| **痕跡** | `src/society/traces.py` | 行為の副産物が場所に残る `trace_mark`{node, kind(**gathering**含む), tier} — 集約+蒸発のみ(Parunak/Heylighen) | 場所の履歴(gathering という語彙が既に予約済み) |
| **カスケード** | SNS層 | `sns_post/read/like/reshare` → `viral_cascade`{reach} / `feed_rank`(エコーチェンバー) / `misinfo` | 情報のみ(物理的集合に接続しない) |
| **選挙・制度** | rules.py / 議会 | proposal → 署名(露出2回)→ `proposal_passed` → 制度DSL 自動制定 / `council_elected` / `election_result` | 名簿制(集会を伴わない) |

**含意**: 「イベントが自ずと発生する」ための材料 —— 種(噂 Item・造語・SNS投稿)・伝播
(transmission・reshare・flyer)・場所参照(rumor_born.node・place_label_bind{word,node})・
動員変調(status.attract)・到達判定(crowd_surge / appointment_kept)—— は**全て既存**。
欠けている接続は2本だけ:
- **(i) 種に「時刻」が無い**(rumor は node を持つが time を持たない。event_host だけが start_step を持つ)
- **(ii) 検出器が一般化されていない**(crowd_surge は行事日+固定ノード限定。「昨日の夜、
  普段は誰もいない公園に 40 人いた」を拾う器が無い)

### 2-2. 観測・可視化インフラ(実装確認済み)

| 部品 | 場所 | 内容 |
|---|---|---|
| L1 イベントログ | `src/society/observer/schema.py` | 約200 kind の正準レジストリ(固定列+payload)。`register_event_kind` 1行で追加 |
| ライブビューア | `scripts/live_viewer.py` | 追いかけ再生(part parquet を読むだけ)。地図・時計・**ティッカー(HIGHLIGHT_KINDS 約35種)**・L2スパークライン。読み取り専用の規律が確立済み(_open_shared) |
| 3D/通常ビューア | `viz/make_viewer.py` / `make_viewer3d.py` | リプレイ。**顕著イベントパネル**あり |
| 顕著イベント抽出 | `viz/notable_events.py` | NOTABLE_KINDS(kind→日本語ラベル・**重要度1..5**・text用キー)+ MAGNITUDE_KEYS(reach/supporters/amount/debt)で上位N間引き・PER_KIND_CAP=50・間引きは caps に必ず記録 |
| 思考ログ | `l1b_llm.parquet` + `src/society/llm/journal.py` | 呼メタ{llm_call_id, purpose, cached} + **プロンプト/応答全文**(append-only gzip・観測専用・シム非読) |
| 行為→思考リンク | `src/society/provlink.py`(既定OFF) | 行為イベントに (llm_call_id, role) を刻印(PROV-DM wasInformedBy)。role=plan は「朝の計画の実行」、他は「その場の熟慮」 |
| 因果台帳 | `src/society/observer/causality.py`(既定OFF) | cause_type 6語(agent/device/schedule/physics/natural/boundary)+ actor_id |
| 記憶・関係サイドカー | observer/memory.py・relations.py(G4/G5・finals ON) | 記憶本文+importance 日次 / closeness 差分 |
| 日課計画台帳 | day_plan(plan_created.blocks[] + plan_block_start/drop/slide/replan/cont_fire) | 「計画 vs 実行」の突合が block 添字で機械的に可能(W4-F で添字追加済み) |
| 会話エピソード | episode_start/end/closing(第87) | シーン境界(トリガ種別・ターン数・脱出理由) |

**発見(統合対象)**: 「注目イベントの選定表」が **2系統で別管理**になっている
(live_viewer.HIGHLIGHT_KINDS と notable_events.NOTABLE_KINDS は集合も性質も不一致。
前者は集合のみ・後者は重要度+magnitude 持ち)。フィード層を作るならここを単一レジストリに
統合するのが第一歩(§4-3)。

### 2-3. 実ランの kind 別頻度(希少度の実測根拠)

runs/_b4_finals_before(60体×432step≈3日・finals全ON リハーサル)の event_kinds 実測:
総数 59,881 件。上位は transmission 5,453 / opinion_shift 5,433 / state_update 5,067 /
drive_request 4,195 / affect_update 3,912(=毎step級の配管イベント)。一方
council_elected 1 / partner_formed 2 / life_event 2 / venture_open 10 / joint_activity 12 /
event_host 36 / rumor_born 46 / viral_cascade 59 / event_attend 64(=物語級は3日で数件〜数十件)。
→ **「配管:物語 = 1000:1」**の比が実測で確認できる。フィードの仕事はこの 1000:1 の選別である。

---

## 3. 集合イベント内生化の設計案(3系統)

共通の設計思想: **「イベント」をトップダウンの宣言でなく、「同時刻・同場所への意図(または
在場)が閾値を超えた事実」としてボトムアップに定義する。** 案A/B は観測のみ(シム不変)、
案C は世界を動かす(既定OFF)。3案は排他ではなく積層である(A⊂B⊂C の順に情報が増える)。

### 案A: 集合検知器(gathering detector)— crowd_surge の全ノード・全日一般化

- **何を状態に持つか**(observer 側のみ): ノード×時間帯スロット(例: 30分)の在場人数
  ベースライン。曜日×時刻プロファイルの EMA(初日〜数日はウォームアップ=検出保留)。
  在場数は L1 の位置イベント(arrive/enter_building/stay)から観測側で復元(live_viewer が
  既に同じ意味論で位置を持っている)。
- **閾値**: n(node, slot) ≥ n_min(例10) かつ n / baseline ≥ τ(例3.0)。持続 d_min スロット。
  ヒステリシス(開始閾値>終了閾値)で1回の集合=1イベント。
- **帰属(なぜ集まったかの事後分類)**: 参加者集合の共通因子を優先順で照合 —
  ①同一 event_id(event_attend)→「開催イベント」 ②appointment の (place, when) 一致
  ③day_plan blocks の place 一致 ④共通の噂/語 item_id(rumor_born.node=当該ノード or
  place_label_bind の語を採用済み)⑤joint_invite の連結成分 ⑥それ以外=**unattributed
  (=最も面白い箱。誰も企画していないのに集まった)**。causality と同じ「観測側で分類を
  1箇所に集める」流儀。
- **何が記録されるか**: 新kind `gathering`(agent_id=-1)
  `{node, slot, n_peak, baseline, ratio, dur, via(event|appointment|plan|rumor|invite|none), refs[], sample_ids[]}`
  + 終了時に `gathering_end`。※新streamは不要(乱数を引かない)。
- **呼数影響**: **LLM 0・乱数 0・シム状態への書き込み 0**(純観測)。R1 完全適合。
  既定OFFで L1 バイト一致(OFF時は kind 自体出ない)。
- **工数**: 小(annual.check_surge の一般化+ベースライン保持。engine フックは envfeedback と
  同じ観測点に相乗り可)。事後版(スクリプトで L1 から検出)なら**シム本体に1行も触れず**作れる
  → **まず事後版を scripts/detect_gatherings.py として作り、閾値を較正してから
  ライブ版(フィード用)に昇格する2段構え**を推奨。
- **限界**: 意図でなく結果しか見ない。電車遅延の滞留も「集合」に見える(→ via=none の中で
  transit_delay/env_feedback との時間相関を照合して "congestion" ラベルに落とす)。

### 案B: 意図台帳(assembly ledger)— appointment の N 者一般化(観測のみ)

- **何を状態に持つか**: (place_norm, day, when_bin) → 意図保持者集合。ソースは既存 L1 のみ:
  ①appointment{place, day, when} ②plan_created.blocks の (place, start) ③event の
  _attending_event(=event_attend 予備軍)。place の正規化(語→ノード束縛は
  place_label_bind が既にある)が主要な実装作業。
- **閾値**: |意図保持者| ≥ M(例5)で「**集合予定の成立**」を記録。当日は
  (place, when±Δ) の実在場と突合して**到達率**を出す(appointment_kept の N 者版)。
- **何が記録されるか**: `assembly_formed`{place, day, when, n_intent, via{appointment, plan, event}}
  → `assembly_outcome`{n_arrived, rate, arrivals[], no_shows[]}。
- **呼数影響**: ゼロ(読み取りのみ)。R1 完全適合。事後スクリプトでも実装可。
- **工数**: 小〜中(place 正規化+ビン集計)。
- **価値**: Generative Agents がバレンタインパーティで行った計測(招待を知った12人→来た5人
  →来なかった理由)を**常設の観測量**にする。「集合が予定されたのに崩れた」(no_show 率)も
  物語であり、較正指標(計画遵守・関係強度)にもなる。**案Aの帰属②③の実装と共通部品**。

### 案C: 閾値動員(Granovetter 層)— 主催者なし集合の内生機構(世界を動かす・既定OFF)

- **種(seed)**: 「(場所, 時刻) が付いた情報オブジェクト」。実装は既存の3経路のどれでも:
  ①噂 Item に time を足す(rumor_born は node を既に持つ)②SNS 投稿の (node, time) 付き
  variant ③flyer(既に node を持つ)。**event_host との違いは「主催者の開催宣言・会場管理・
  開始抽選を持たない」こと** — 誰かが「金曜の夜、○○(造語の場所)で」と言った、それだけが種。
- **何を状態に持つか**: 個体ごとの参加閾値 θ_i(persona から決定論ハッシュで異質分布を張る。
  **Granovetter: 結果を決めるのは平均でなく分布の形**)+ 認知した参加シグナル数
  s_i(その種を reshare/発話/参加表明した知人・フォロイーの数。transmission と reshare の
  既存配管で数えられる)。
- **遷移(全て決定論・LLM 呼ゼロ)**: s_i ≥ θ_i → 参加意図(day_plan への組込 or
  event_attend と同型の移動+stay)。**参加表明自体が SNS/会話に乗る**(既存の伝播に相乗り)
  ので s が再帰的に増える=カスケード。臨界に達しなければ不発(それも観測量。
  Granovetter の「1人欠けると不発」の再現器になる)。
- **何が記録されるか**: `gather_intent`{seed_item, node, time, s, theta}(専用stream)+
  実際の集合は**案Aの検出器が拾う**(via=rumor/invite で帰属)。
- **呼数影響**: LLM 増分ゼロ(閾値判定は決定論。event_attend の抽選と同じ流儀で専用 stream)。
  ただし**移動という世界改変を起こす**ので R1 の「観測がシムを変えない」枠の外=
  既定OFF・golden不変・finals で ON 判断(fire B案・POP と同じ運用)。
- **工数**: 中(種の time 付与+θ/s の台帳+event_attend パイプラインの host なし版)。
- **段階導入**: C-0 として「θ/s を**数えるだけ**で遷移させない」(=カスケードが起きたはずの
  地点を記録する counterfactual 観測)から入れば、観測のみで案Cの較正データが取れる。

### 3-4. 3案の比較表

| | 案A 検知器 | 案B 意図台帳 | 案C 閾値動員 |
|---|---|---|---|
| 性格 | 結果の検出 | 意図の集計 | 行動の内生化 |
| シムへの影響 | ゼロ(純観測) | ゼロ(純観測) | あり(移動を生む)=既定OFF |
| LLM 呼数 | 0 | 0 | 0(決定論) |
| 乱数 | 0 | 0 | 専用stream |
| 事後スクリプト版 | 可(推奨の入り口) | 可 | 不可(ライブのみ) |
| 新kind | gathering(+end) | assembly_formed/outcome | gather_intent |
| 工数 | 小 | 小〜中 | 中 |
| 拾えるもの | 誰も企画しない集合・偶発群集 | 崩れた集合・no-show | **カスケードの発生と不発** |

---

## 4. イベントフィード層の設計(承認案①)

### 4-1. ランキング関数(注目イベントの選定)

score(e) = w₁·importance(kind) + w₂·rarity(kind) + w₃·magnitude_z(e) + w₄·chain(e) + w₅·first(e) − dedup(e)

- **importance**: 既存 NOTABLE_KINDS の 1..5 事前値をそのまま正典に(§2-2)。
- **rarity(自己較正の希少度)**: −log₂(count(kind, 直近窓)/total)。§2-3 の実測が示す通り
  kind 頻度は 1000:1 で歪むので、固定表でなく**ラン自身の分布で較正**する(60体スモークでも
  25万本選でも同じ式が働く)。
- **magnitude_z**: MAGNITUDE_KEYS(reach/supporters/amount/debt…)の kind 内 z 値。
- **chain(連鎖長・影響半径)**: ライブでは payload 内の数値(viral_cascade.reach・
  belief hop・proposal supporters)を代理に。事後フィードでは transmission 系譜の深さ/幅を
  item_id で復元(provenance が既に持つ)。
- **first(初回ボーナス)**: その kind・その語・そのペアの**ラン内初出現**に加点
  (最初の partner_formed は2件目より物語価値が高い。決定論: 出現済み集合を持つだけ)。
- **dedup(ストーリー折りたたみ)**: storyline key = item_id / event_id / proposal_id /
  ペア(sorted ids) / org_id。同一 key は時間窓内 1 カード+件数バッジ(「+12件」)。
  notable_events の PER_KIND_CAP(kind 単位の間引き)より物語の連続性が保たれる。

### 4-2. UI(live_viewer への層追加)

- ティッカー(時系列流し)→ **ランク付きフィード**に置換: 重要度フィルタ(★3以上のみ等)・
  storyline 折りたたみ・クリックで地図ジャンプ(notable_events が has_pos/frame を既に持つ)。
- **日次ダイジェスト行**: 日境界で「昨日の街」1行(top-k イベント+初出語+集合検知数)。
  norm_digest(客観カウント)の観測側拡張として。
- ペーシング(RimWorld 的緊張と緩和)は**表示制御**として実装: 1画面あたりの重大度予算を設け、
  静かな時間帯は低ランクも流す(シムに触れない=演出はビューアの仕事)。
- 案A/B の新 kind(gathering / assembly_formed)は importance 4〜5 でフィード直結。
  **via=none の gathering(誰も企画していない集合)は最上位固定**を推奨(本プロジェクトの
  観察目的「世界を変える者の創発」に最も近い信号)。

### 4-3. 実装配置(統合の一手)

1. `viz/notable_events.py` の NOTABLE_KINDS を**単一レジストリに昇格**(importance・magnitude・
   text_keys・storyline_key を1表で保守)。
2. `scripts/live_viewer.py` の HIGHLIGHT_KINDS はそのレジストリから導出(二重管理の解消)。
3. ランキングはどちらも同じ純関数(新規 `viz/feed_rank.py`)を読む。
4. 全て読み取り専用スクリプト側=R1 の枠外(シム本体変更ゼロ)。

### 4-4. kind 希少度×フィード価値の候補表(§2-3 実測+設計頻度に基づく)

| 層 | 期待頻度 | kind(代表) | フィード扱い |
|---|---|---|---|
| S: ラン一大事 | ≲1/ラン〜1/日 | council_elected, election_result, disaster, scenario_shock, bankruptcy, institution, rule_repealed, partner_formed, life_event, venture_fulltime, **gathering(via=none)** | 無条件掲載・地図ジャンプ・プッシュ級 |
| A: 物語級 | 数件/日 | venture_open, group_found, event_host, labor_action, proposal_passed, crime, eviction, detention, move_home, long_goal, job_change, illness, **assembly_formed**, joint_activity, misinfo, viral_cascade(reach上位) | 既定掲載(storyline 折りたたみ) |
| B: 顕著な社会活動 | 数十件/日 | label_coin/vocab_coin, place_label_bind, rumor_born, event_attend, flyer_post, proposal, relation_break, chance_event, undefined_action, free_action(match低=逸脱のみ) | ランク上位のみ掲載 |
| C: 普及・反復 | 数百件/日 | label_adopt, group_join, relation_tier, belief_transmit, sns_reshare, gossip_spread | 集約バッジのみ(「新語○○が今日+38人」) |
| D: 配管 | 毎step級 | transmission, opinion_shift, state_update, drive_request, affect_update, move_segment | フィード非掲載(スパークライン行き) |

---

## 5. 1日トレース=物語抽出の設計(承認案②)

### 5-1. 素材(全て既存・§2-2)

L1(行為)・l1b_llm+llm_journal(思考の入出力全文)・memory.parquet(記憶本文+importance)・
plan_created.blocks(朝の計画)・provlink(行為→思考の llm_call_id+role。ON時)・
causality(cause_type)・episode_start/end(会話シーン境界)・relations.parquet(closeness差分)。

### 5-2. 抽出(決定論・呼数ゼロ)

1. **主イベント**: agent_id = 対象 の L1 行。
2. **受動側の逆引き**: 対象が payload に現れる行(hear.speaker / speak.hearers / dm.to /
   joint_invite.invitee / serve.customer / crime.victim…)。kind→payload キーの対応表を
   1箇所に持つ(causality の actor_of と同じ流儀。相当部分は流用可)。
3. **時系列整列**: step 順。同 step 内は「計画→移動→行為→会話→内省」の kind 優先順。

### 5-3. 物語の骨格=「計画 vs 実行」の突合

朝の plan_created.blocks[] を章立てに、plan_block_start(実行)/ plan_block_drop(断念)/
plan_slide(遅延)/ plan_replan / plan_cont_fire(「もし〜なら」発動)を**逸脱注記**として
重ねる。物語の緊張は逸脱に宿る(「15時に○○へ行くはずだった。だが—」)。W4-F の block 添字で
機械的に突合できる(推測不要)。シーン分割は enter/exit_building・episode_start/end・
sleep/wake を境界に。

### 5-4. 因果リンク

- 行為→思考: provlink ON なら (llm_call_id, role) で曖昧性ゼロ。OFF ランでは
  (step, agent_id) join の近似(同 step 複数呼は多義と明示=捏造しない)。
- 状態変化→原因: state_update.cause・belief_update{from, hop}(伝播の親)・
  relation_tier/break の cause。
- **語り手の声**: 夜の reflect と llm_journal の応答全文=その日の総括を**本人の言葉**で引用
  できる(物語の一人称素材。生成不要で既に在る)。

### 5-5. 出力の3層

| 層 | 生成 | 内容 |
|---|---|---|
| L0 生タイムライン | 決定論 | 整列済み全行(検証用・リンク付き) |
| L1 シーンカード | 決定論テンプレ | 時間帯・場所・同席者・行為・計画逸脱・関係変化(1日=10〜20枚) |
| L2 物語文 | **ランの外**の事後 LLM 1呼/agent日 | シーンカード+内省引用を渡して800字の一人称記(シムに一切触れない=R1安全。llm_journal と同じ「観測専用」) |

実装: `scripts/trace_agent_day.py`(読み取り専用。trace_spark.py と同じ流儀)。
ビューア統合: フィードのイベントカード→当事者の1日トレースへリンク(ドリルダウン)。

### 5-6. 表現力底上げ(承認案③)との接続

トレースが痩せる最大要因は「行為はあるが中身が無い」kind(stay・home_activity 等)。
③の投資先は新規イベントでなく **payload の記述性**(free_action の what/category は既に良い
前例)と、L2 物語生成時に memory.parquet の記憶本文を挿入する後段結合で埋まる。
シム側の表現力改修より**観測側の結合を先に**やるのが安い。

---

## 6. 推奨の組み合わせ(工数順のロードマップ)

| 順 | 施策 | 種別 | 呼数/R1 | 工数 |
|---|---|---|---|---|
| 1 | 事後スクリプト版 案A+B(detect_gatherings.py: 検知+帰属+到達率) | 観測(ラン外) | 影響ゼロ | 小 |
| 2 | フィードレジストリ統合+ランキング関数(feed_rank.py)+live_viewer 層 | 観測(ラン外) | 影響ゼロ | 小〜中 |
| 3 | 1日トレース(trace_agent_day.py: L0/L1 決定論層まで) | 観測(ラン外) | 影響ゼロ | 小〜中 |
| 4 | L2 物語文(事後 LLM)+フィード⇄トレースのドリルダウン | 観測(ラン外) | ラン外呼のみ | 小 |
| 5 | ライブ版 gathering 検知(observer 内・既定OFF) | 観測(ラン内) | 呼0・乱数0 | 小 |
| 6 | 案C-0(θ/s を数えるだけの counterfactual 観測・既定OFF) | 観測(ラン内) | 呼0 | 中 |
| 7 | 案C 本体(閾値動員=世界を動かす。finals ON 判断) | **内生機構** | 呼0(決定論)・既定OFF | 中 |

1〜4 は本選前でも安全に入る(ラン外のみ)。5〜7 は R1 手続き(既定OFF・golden不変・
専用stream)で実装し、ON は fire B案と同じ GO/NO-GO 運用に載せる。

---

## 7. 出典(実在確認済みURL)

(子レーン結果の統合時に §1 と併せて記載)
