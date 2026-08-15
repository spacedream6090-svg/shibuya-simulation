# 渋谷社会シミュレーション — Reality Maximization / Finals Master Plan

> **目的**: 残り14日間と本選GPUクラスタを最大限使い、`shibuya-simulation` を「大人数が動くデモ」から、**現実データに接地し、再現度を定量検証でき、反実仮想を比較できる生成型都市社会シミュレーション**へ引き上げる。  
> **対象リポジトリ**: `spacedream6090-svg/shibuya-simulation`  
> **監査基準コミット**: `5a7df6573cf6f75f076b2900829930df548bc233`（2026-08-16 時点）  
> **計算資源**: 単一ノード / RTX A5000級 24GB × 7 / 合計VRAM 168GB  
> **本番目標**: 100万ペルソナプール / 同時最大25万人 / 10シミュレーション日 / Δt=10分（144 step/day）  
> **提出期限**: 2026-08-30  
> **実装主体**: Claude Code  
> **レビュー**: Codex read-only review → Claudeによる検証・修正 → Codex再レビュー  
> **この文書の位置づけ**: 既存の `STATUS.md`、`PENDING.md`、`docs/plans/finals-endgame-plan.md`、`ops/codex-review-pack.md` を置き換えるのではなく、**「現実再現度とハッカソン成果を最大化する観点」で横断的に優先順位を付け直した上位計画**。

---

# 0. 最初に: 何を「完成」と呼ぶか

14日で「現実そのもの」を完全複製することは科学的には証明できない。実在25万人全員の内部状態、交友関係、建物内部、購買、会話、判断を観測できないからである。

したがって、このプロジェクトの最終目標は次の表現に置く。

> **実在の渋谷の空間・人口・移動・生活時間・交通・組織・気象・社会関係の統計的制約に接地し、25万人規模の異質なエージェントが、LLM認知と内生的相互作用によって動く、検証可能な生成型都市デジタルツイン。**
>
> さらに、現実データとの誤差を項目別に表示し、「どこまで現実を再現でき、どこからがモデル仮定なのか」を明示する。

ハッカソンで強いのは「完璧です」と言うことではなく、

1. **本当に25万人が動く**
2. **実在の2025年度渋谷3D都市モデル上で動く**
3. **人口・移動・生活時間などを現実統計と比較している**
4. **LLMが必要な局面で個人ごとに意思決定する**
5. **介入前/介入後の2つの世界を比較できる**
6. **結果の因果経路を追える**
7. **再現できている部分と誤差を定量表示する**

という「証拠」である。

---

# 1. 現在のシミュレーションを一言で理解する

現状は、

> **25万人の全員が毎step LLMで思考するシステムではなく、25万人のABM（Agent-Based Model）の身体・制度・経済・移動の上に、重要な場面だけLLM認知を発火するHybrid LLM-ABM**

である。

これは欠点ではない。25万人では、歩行・待機・睡眠・通勤などの低レベル動作までLLMで生成するのは計算資源の使い方として非効率であり、人間の「意味のある意思決定」をLLMへ集中させる方が合理的である。

ただし現在は、**LLM認知の密度が低すぎる**。

`conf/finals_observe.yaml` では `lod.max_llm_per_step = 300` 系の設計があり、単純上限だけを見ると

- 300 call/step
- 144 step/day
- 43,200 call/day
- 250,000人で割ると **0.173 call/person/day**

程度しかない。

つまり「25万人の社会」であるのに、平均すると一人が高レベルLLM推論をする頻度が極めて低い。

**ここは本選前に必ず改修する。**

---

# 2. 現在の強み — 捨てずに使うもの

このリポジトリはすでに非常に多くの資産を持っている。全面書き直しは絶対にしない。

特に残すべき強み:

- 10分Δt、144 step/day の一貫した時間軸
- 決定論的 RNG / seed 管理
- 100万件 persona pool / presence rotation
- 25万人同時在場設計
- 実地図・道路・POI
- 組織台帳
- 通勤・交通・GTFS
- 経済・賃金・家賃・企業間フロー
- household / partner / relation
- SNS / rumor / conversation
- health / fire / crime / incidents
- memory / reflection / belief / cognition
- provenance / causality logging
- L1/L2/L3 observer
- checkpoint / resume
- vLLM fleet / sticky routing / prefix cache 設計
- 本番向け watchdog / backup / Discord reporting
- 5,000本超のテスト資産
- feature flag / R1（OFF時不変）ドクトリン
- Codex review pack

**14日間は「新しい機能の数」を競うのではなく、既存機構を本当に接続し、現実データで校正し、計算資源を使い切る期間にする。**

---

# 3. 現HEADで本番前に潰すべき重大問題

## E0-1. `agent_by_id` が退場Agentのfull objectを保持する問題

### 問題
pool rotationでAgentを退場させても、`agent_by_id` が「これまで実体化した全個体」への強参照を保持する設計が残っている。

`dormant_cap=50000` で休眠データを制限しても、別の辞書がfull Agentを保持すればRAMは減らない。

### 影響
25万人×複数日ローテーションで、RAM使用量が「現在人数」ではなく「過去に一度でも実体化した人数」に近づく可能性がある。

### 実装
- `agent_by_id`: **live Agent only**
- 過去Agent参照用に `AgentRef` / `DormantAgentRef` を導入
- relation / provenance / journal が必要とする最小属性だけ保持
- deceased / emigrated / departed はIDベースの照会へ
- checkpoint sidecarもfull Agentを複製しない

### Acceptance
- 50k present / pool rotation 10日相当で peak RSS が日数に比例して増えない
- 退場者を参照する全テスト green
- relation/provenanceの過去ID参照が壊れない

---

## E0-2. checkpointの全量 `pickle.dumps()` をやめる

### 問題
巨大なstateを一度 `bytes` にしてから圧縮すると、保存時に巨大な一時RAMが発生する。

### 実装
最小:
```python
with gzip.open(tmp_path, "wb") as f:
    pickle.dump(blob, f, protocol=pickle.HIGHEST_PROTOCOL)
```

さらに可能なら:
- Agent state
- relation state
- economy state
- observer watermarks

をshard化。

### Acceptance
- checkpoint save時のpeak RSS増分を測定
- 250k rehearsalでOOMしない
- straight run vs resume run の主要hash一致

---

## E0-3. checkpointとログをtransaction化する

### 現状リスク
checkpointが保存されたあとlogger flush前に電源断すると、

- world state: step N
- logs: step N未満

となり得る。

### 実装
`checkpoint-N/` を一時ディレクトリに作り、

1. observer flush
2. sidecar flush
3. state checkpoint
4. manifest + hashes
5. fsync
6. `COMPLETE` marker
7. atomic rename

の順にする。

resumeは**最新のCOMPLETE checkpointだけ読む**。

### Acceptance
人工的に各段階でkillし、必ず直前の整合checkpointへ戻れる。

---

## E0-4. finals profile単独実行でMockになり得る問題を消す

### 実装
本番用に**完全resolved configを1枚生成**する。

例:
`conf/finals_2026_08_22_frozen.yaml`

含める:
- world
- pool v2
- vLLM fleet
- LLM budget
- fire
- observer
- watchdog thresholds
- population switches
- seed policy

さらに:

```python
if cfg.run.n_agents >= 10_000 and cfg.model.backend == "mock":
    raise RuntimeError("Large production run cannot use mock backend")
```

`--allow-mock-production` のような明示的overrideがない限り失敗させる。

### Acceptance
`python scripts/run.py --profile conf/finals_2026_08_22_frozen.yaml --dry-run`
で
- backend=vllm
- servers=7
- persona=v2
- expected present cap
- LLM scheduler=adaptive
を標準出力へ表示。

---

## E0-5. `engine.batch_llm` を本番配線する

現在のエンドゲーム計画にも「本選confに無く、計画呼び出しが完全直列」と記録されている。

### 実装
- workers 1/4/8/16 A/B benchmark
- state hashがworkers数で変わらないことを確認
- 7 vLLM replicaへの同時送信
- backpressure
- timeout retry
- purpose別queue

### Acceptance
- R_effが直列より明確に改善
- workers 1 vs 本番値で simulation semantic state一致
- 失敗requestはログされ、静かに消えない

---

# 4. 最大の新規クイックウィン: PLATEAU 2025 渋谷区を入れる

## 4.1 重要な事実

2025年度版のProject PLATEAU渋谷区データが公開されている。

含まれるもの:

- 建築物: LOD0 / LOD1 / **LOD2.0 / LOD2.2**
- 道路: LOD1 / LOD2 / **LOD3.0**
- 都市設備: LOD1 / **LOD3.0**
- 地下街: LOD1 / **LOD4.1**
- 橋梁: LOD2.1
- 植生: LOD1 / LOD3
- 地形
- 土地利用
- 都市計画
- 浸水・土砂災害リスク
- 駅・鉄道・公園・避難施設などの関連GeoJSON

CityGML版は圧縮約649MB、3D Tiles/MVT版も提供される。

**「Claudeが建築物データを一軒ずつ集める」必要はない。**

---

## 4.2 実装を2系統に分ける

### A. Viewer
3D Tilesを直接Cesium/Re:Earth等へ読み込む。

変換しない。

メリット:
- 最速
- LOD2建物をすぐ表示
- simulation engineと表示を分離できる

### B. Simulation Engine
CityGMLから必要属性だけ抽出し、軽量Parquetへ変換する。

例:

`data/plateau/shibuya_buildings.parquet`

```text
building_id
centroid_lat
centroid_lon
footprint_wkb
height_m
storeys_above
usage
name
address
floor_area_est
capacity_est
entrance_x
entrance_y
source_year
source_lod
```

属性が存在しない場合はNULLにし、**作話しない**。

---

## 4.3 新規スクリプト案

### `scripts/fetch_plateau.py`
- PLATEAU catalog API
- municipality code `13113`
- 最新yearを自動選択
- checksum
- metadata保存

### `scripts/build_plateau_world.py`
- CityGMLをstream parse
- bbox crop
- building polygon/height/use抽出
- existing OSM POIとspatial join
- organizationsとbuildingを紐付け
- entrances生成
- capacity推定
- Parquet化

### `src/society/world/plateau.py`
- spatial index (`STRtree` / rtree)
- nearest building
- building capacity
- use/category
- entrance
- indoor archetype ID

---

## 4.4 建物内部は「実データがないから諦める」ではなく、2層構造にする

全建物の実フロアプランは取得できない。

そこで:

### 層1: 実在データ
- footprint
- 高さ
- 用途
- 階数（ある場合）
- 道路との接続
- 実在POI
- 実在組織

### 層2: archetype interior
用途ごとの簡易内部グラフ:

- residence
- office
- retail
- restaurant
- school
- hospital
- station
- entertainment
- government
- hotel

各archetype:
```text
entrance
lobby
room/floor zones
service zone
toilet
vertical circulation
capacity
typical dwell time
interaction affordance
```

**嘘の実フロアプランを作らない。**
「形は実在、内部行動空間は用途別モデル」と明示する。

---

## 4.5 地下街LOD4.1はデモ価値が非常に高い

渋谷の「都市の縦方向」を見せるうえで、

- 地上
- 駅
- 地下街
- 建物

を区別できるだけで、従来の2D OSM押し出しよりデモ品質が大きく上がる。

14日ですべての室内を物理シミュレーションする必要はない。

**viewer上では高精細PLATEAU、engine上では簡略zone graph**でよい。

---

# 5. Persona v2を本番へ切り替え、engineへ完全接続する

現状、v2は生成済み/生成可能だがfinalsがv1を参照する状態。

v2で改善済み:
- 0–14歳
- 85+
- 年齢分布
- 教職員
- 来街者構成
- 非通勤来街者
- 外国人比率等

## 必須実装

### P-1
`pool.dir = data/persona_pool_v2`

### P-2
`workplace_scope` を `plan_boundary` / work scheduleへ接続

### P-3
`at_home` を存在/日課/在宅行動へ接続

### P-4
子ども:
- 未就学
- 小学生
- 中学生
- 高校生

のschool/daycare/home scheduleを持たせる。

### P-5
高齢者:
- 就業しない
- 通院
- 買い物
- 散歩
- 在宅
の行動分布を別にする。

### Acceptance
- 人口構成比較レポートが自動生成
- 年齢層×時刻×場所のクロス集計
- v1/v2差分を出す
- v2 switchでcrash/LLM starvationが増えない

---

# 6. 「帰宅 = 即就寝」を本番前に直す

これは現実再現上の最重要バグの一つ。

既存研究ノートで、
`enter_building{home:true}` の直後に同じ分で `sleep_start`
が100%近く起きる構造が確認されている。

その結果:
- 夜の在宅
- 家族会話
- 夕食
- 風呂
- 家事
- SNS
- TV/動画/ゲーム
- 勉強
- 副業
- 恋人
- 一人の時間
- 内省

が大きく消える。

## 実装

状態を分離:

```text
OUTSIDE
TRAVEL
AT_HOME_AWAKE
SLEEP_PREP
SLEEPING
```

### 在宅activity vocabulary
- meal
- cooking
- cleaning
- bath
- media
- game
- reading
- study
- remote_work
- childcare
- household_talk
- partner_time
- social_media
- hobby
- rest
- reflection
- sleep_prep

### 発火
帰宅後に`home_session`を開始。

その中で:
- 年齢
- 職業
- 世帯
- 曜日
- 帰宅時間
- 疲労
- 翌日の予定
- 子どもの有無
- partner/housemate presence

からactivityを選ぶ。

## LLMとの関係
全部をLLMに聞かない。

- routine: rule/statistical
- 葛藤/選択/会話/出来事: LLM

### Acceptance
Reality report:
- 帰宅→就寝 gap
- 21:00 home rate
- awake-at-home hours/day
- media/leisure minutes
- household interaction count

を現実統計と比較。

---

# 7. LLM呼数を根本設計から増やす

## 7.1 300/step固定上限をやめる

`max_llm_per_step=300` のような静的上限は、7 GPUが余っていても呼数を増やせない。

新しく

`AdaptiveLLMBudgetController`

を作る。

入力:

```text
R_eff              # 実測 req/s
step_wall_time
gpu_utilization
queue_latency
remaining_wall_s
remaining_sim_steps
present_agents
purpose_backlog
```

出力:

```text
step_call_budget
purpose_budgets
max_inflight
```

---

## 7.2 基本方針

**全員に毎10分LLMを呼ぶ必要はない。**

人間の行動の多くはルーチンである。

LLMは以下に使う:

1. 朝/開始時の方針
2. 予定変更
3. 他者との重要な会話
4. 予期しない事件
5. 購買/移動/関係の意味ある選択
6. SNS投稿/反応
7. 内省
8. grievance / belief / value更新
9. キャリア/恋愛/転居等ライフイベント

---

## 7.3 目標呼数

現在:
**約0.17 call/person/day相当の上限**

本番目標:

### Minimum
`0.5 semantic LLM calls / present agent / sim-day`

### Target
`1.0–1.5 / agent / sim-day`

### Stretch
`2.0+ / agent / sim-day`

250k人なら:

| 平均 | calls/sim-day | calls/10days |
|---|---:|---:|
| 0.5 | 125k | 1.25M |
| 1.0 | 250k | 2.50M |
| 1.5 | 375k | 3.75M |
| 2.0 | 500k | 5.00M |

144stepで均すと:

- 1.0/day → 約1,736 calls/step
- 1.5/day → 約2,604 calls/step
- 2.0/day → 約3,472 calls/step

**まず1,500–2,500 calls/step級を実測可能な帯として検討し、固定値ではなくR_effと残りwall timeから制御する。**

---

## 7.4 人ごとに公平にする

salienceだけで選ぶと、派手なAgentだけが何度も考え、普通の人が永久にLLMを使わない。

各Agentに:

```text
last_llm_step
llm_calls_today
cognition_debt
salience
event_urgency
social_urgency
```

を持たせる。

priority:

```text
priority =
  event_urgency
+ salience
+ social_urgency
+ fairness_age
+ cognition_debt
- recent_call_penalty
```

これで「重要人物だけLLM」という偏りを抑える。

---

## 7.5 人口層ごとの呼数

全員同一頻度ではなく、**その日に世界で起きていること**に応じて配分する。

例:

### L1 residents
- 2–4 semantic calls/day目標
- 家庭、仕事、人間関係、長期記憶が重要

### L2 workers/students
- 1–2/day

### L3 regular visitors
- 0.5–1.5/day

### L4 stochastic visitors
- 0.25–1/day
- ただしevent遭遇時は増加

### L5 city operators
- incident時は高優先

これを**quotaとして結果を固定するのではなく、scheduler priorityのinitial weight**として使う。

---

# 8. `cognition.fire` を開ける

現在は `g_update` がONでも、`cognition.fire` OFFなら主要経路が実質no-opになる構成がある。

本当に「人が環境に反応して考える」世界を作るなら、周期タイマーだけでなく**event-driven cognition**が必要。

### fire triggers
- unexpected crowd
- conflict
- direct speech
- friend encounter
- danger
- weather discomfort
- advertisement
- price shock
- train delay
- job issue
- health symptom
- relationship event
- rumor
- policy/news exposure
- unusual place
- goal obstruction

## 条件
fireをONにする前に既存の
- defer bug
- call count explosion
- starvation
をfix。

### Acceptance
- OFF/ONでcalls増分測定
- T10 +15%程度以内を初期gateにする
- call増だけでなく、**意味のある行動変化率**を測る

`LLM fired but action unchanged`率も出す。

---

# 9. cognitionを3時間スケールに分ける

## Fast: 10分〜30分
LLM不要中心。

- route
- queue
- move
- wait
- routine task

## Medium: 数十分〜数時間
LLM対象。

- where next
- who to talk to
- buy or not
- leave event
- change plan
- react to incident

## Slow: 1日〜数日
LLM対象。

- beliefs
- satisfaction
- relationship
- work attitude
- spending strategy
- life decisions
- migration
- partner/family

これにより、「人間らしさ」をLLMで作りながら、全step推論を避ける。

---

# 10. LLMモデル配置

現在のrepoは7本のvLLM replicaとpurpose routingを想定している。

まずは**同一8Bモデル7 replicaでthroughputを最大化**するのが安全。

### Phase A
7× 8B AWQ/INT4

- sticky agent routing
- prefix cache
- continuous batching
- JSON structured output
- `reflect_think=false`
- right-sized max tokens

### Phase B（実測余力がある場合のみ）
quality tierを作る。

例:
- 5 GPU: fast/default cognition
- 2 GPU: deeper reflection / high-stakes decisions

ただし大モデル導入は、
- req/s低下
- VRAM
- model behavior変化
-検証追加
が発生するため、**8B全艦隊が安定してから**。

---

# 11. vLLM生成seedをRNGへ接続する

engine側が再現可能でも、実LLM samplingがfresh runで非決定的なら世界の分岐が変わる。

### 実装
`rng_key`からstable 32-bit/64-bit seedを生成し、可能なbackend requestへ渡す。

```python
request_seed = stable_hash(run_seed, agent_id, step, purpose, ordinal)
```

journalに:
- model
- temperature
- seed
- prompt_hash
- response_hash

を記録。

### 注意
並列GPU推論の完全bitwise reproducibilityが保証できない場合でも、少なくとも**乱数条件を明示・保存**する。

---

# 12. memoryを「全文蓄積」ではなく人間的にする

25万人×10日ではmemoryはRAM/LLM prompt双方の律速。

## 3層memory

### episodic
最近の具体的出来事。TTL/重要度付き。

### semantic
「この人はこういう人」「この店が好き」など圧縮されたbelief。

### social
人物ごとの関係記憶。

## consolidation
睡眠時だけでなく、
- 電車
- 一人歩き
- 在宅休息
- 低認知負荷
でもcandidateを作る。

ただしLLM reflectionは全candidateで実行せず、budget controllerへ送る。

---

# 13. 内省のタイミングを現実化する

既存研究ノートでも、夜固定の内省に偏りがある。

### 候補
- 帰宅後一人
- 電車移動
- 歩行
- 入浴
- 待ち
- 就寝前
- 事件後
- 会話後
- 大きな意思決定後

内省を「毎晩全員」ではなく、

```text
cognitive_load low
AND external_attention low
AND accumulated_salience high
```

で発火。

この変更はLLM呼数を増やすのではなく、**同じ呼数をより現実的な瞬間へ配置する**効果もある。

---

# 14. 初期friend graphをO(N²)から外す

現行friend graphの初期生成は25万人で性能上危険であり、人工的初期networkが創発結果を支配する危険もある。

## 新しい生成法

### 強いtie
- household
- partner
- school/class
- workplace/team

### 中tie
- same workplace
- same school
- neighborhood
- recurring place

### weak tie
- degree distributionからconfiguration/Chung-Lu系で生成
- homophily（age/occupation/location）をweightへ

**全ペア比較は禁止。**

bucket index:

```text
home cell
work org
school
age band
interest cluster
```

からcandidateを作る。

### Acceptance
- O(N log N)〜O(E)
- 250kで数分以内
- degree distribution
- clustering coefficient
- connected components
- household/work tie share
をreport。

---

# 15. 関係は「初期値」より形成過程を重視する

本当に創発を見るなら、初期friend graphを強くしすぎない。

関係更新要因:
- repeated co-presence
- conversation
- reciprocity
- shared activity
- trust
- conflict
- online interaction
- introduction by friend
- household/work context

新規tie形成とdecayを両方ログする。

**13日程度で初期関係が大量消滅する既知較正ズレは修正対象。**

---

# 16. 移動を東京都市圏PTデータで校正する

東京都市圏パーソントリップ調査には:

- どんな人
- いつ
- 目的
- 交通手段
- OD
- 滞留人口
- 平均所要時間

などをクロス集計できる仕組みがある。

## 使う指標
- 小ゾーンOD
- 時刻別発生/集中
- purpose share
- mode share
- trip/day/person
- travel time
- station use
- daytime population curve

### 新規
`scripts/calibrate_mobility_pt.py`

出力:
`reports/reality/mobility_report.json`

### CalibrationとValidationを分ける
例:
- calibration: 平日AM/昼
- holdout validation: PM/夜

同じ値を合わせたデータで「再現できた」と判定しない。

---

# 17. 交通機関

repoにはGTFS実発車機構がある。

## 本番前に確認
- 渋谷駅関連路線
- 実時刻
- weekday/weekend
- last train
- transfer time
- capacity approximation
- delay handling

ODPTはAPI登録が必要で、登録完了に日数がかかる可能性があるため、**今すぐ申請して、間に合えば追加**。

ただし本選をODPT依存にしない。

### データ優先順位
1. 既存GTFS/静的時刻表
2. ODPT realtime（利用可能なら）
3. deterministic simulated delay

---

# 18. 現実の気象を入れる

気象庁の過去観測データをworld inputとして使う。

最低:
- temperature
- humidity
- rain
- wind

影響:
- walking
- outdoor dwell
- heat stress
- shopping
- park usage
- transport
- event attendance

## 方針
simulation出力に合わせて天気を作らない。

**外生観測値として入力し、社会側がどう応答するかを見る。**

---

# 19. 現実の都市イベントを入れる

14日で効果が高い。

例:
- train disruption
- heavy rain
- heat
- large event
- road closure
- store campaign
- emergency drill
- policy intervention

「現実ベースライン」と「介入世界」を同じseed/cache条件からforkする。

これが最終デモの中心。

---

# 20. population/presenceを「計算cap」と「社会現象」に分離する

ユーザー方針:
> 人数自体も世界のアルゴリズムが勝手に決めるのではなく、個人の行動から出てほしい。

これは正しい。

ただし25万人の`present_cap`は計算制約として必要になる場合がある。

したがって概念を分離する。

### world demand
「本来この時刻に渋谷へ来るべき人」

### embodied agents
GPU/CPU上でfull simulationする人

### shadow agents
軽量状態だけ更新し、必要時にembody

毎step:

```text
desired_presence
embodied_presence
truncated_presence
```

を必ずログ。

`truncated_presence / desired_presence > 5%`
なら「計算capが社会を歪めている」と警告。

これでcapを隠さない。

---

# 21. 100万persona poolをもっと活かす

25万人同時でも、世界全体は100万人。

off-scene Agentにも軽量更新:

- work/home status
- finances coarse
- relationship decay
- media/news exposure coarse
- health coarse

を日次で行う。

入場した瞬間だけ10日間停止していた人のようにならないようにする。

ただしfull LLMは禁止。

---

# 22. 経済 — 機能追加よりvalidationを優先

現状、貨幣保存などの会計整合性は強い。

14日では住宅ローン等を増やすより、次を確認:

- wage distribution
- spending/day
- rent burden
- store revenue distribution
- unemployment
- savings
- B2B concentration
- visitor spending

現実統計が取れるものだけ比較。

**「保存則が通る」+「分布も現実に近い」**を目標にする。

---

# 23. 店舗/組織とPLATEAU建物を接続する

現在のorganizationを実在建物へspatial join。

### priority
- station
- convenience store
- restaurant
- retail
- school
- hospital
- office
- hotel
- government
- entertainment

### capacity
実床面積がない場合:
`footprint × storeys × utilization_factor`

用途別に:
- persons/m²
- opening hours
- worker density

を設定。

値は**推定値**としてmetadataへ出す。

---

# 24. 歩行空間を道路LOD3へ寄せる

完全なpedestrian digital twinは14日では難しい。

しかし:
- sidewalk
- road
- crossing
- station entrance
- underground transition

をPLATEAU/OSMから分けるだけでも改善する。

### やらない
25万人全員にSocial Force Modelを常時適用。

### やる
混雑zoneだけmicro simulation。

LOD:
- ordinary street: graph flow
- scramble/intersection/station: crowd micro
- building: zone graph

---

# 25. 社会会話を現実的にする

LLM呼数を増やす場合、会話ばかりがGPUを食わないようにする。

## 会話発火
- co-presence
- relation
- shared context
- free time
- reason-to-talk

## conversation session
1回の会話を毎10分独立callにせず、sessionとして持つ。

```text
start
turns
topic_state
relationship_effect
end
```

### LLM
重要turnのみ生成。
相槌や短いroutineは低コスト化可。

### 指標
- conversations/person/day
- duration
- stranger/friend ratio
- reciprocity
- relation delta
- topic diversity

---

# 26. SNS / インターネット

現代都市で現実再現を目指すなら不可欠。

ただし全員のSNS投稿をLLM生成すると破綻する。

### 層
- passive exposure
- reaction
- repost
- original post
- DM

大半はpassive。

original postと重要DMだけLLM。

news/ad/rumorが
online → offline behavior
へ流れる経路を検証する。

---

# 27. Health / Crime / Fireは「完全実装」より境界を明示

既存機構には、
- 病床
- 救急細部
- 警察物理移動
- 延焼
などの縮約がある。

14日で全てを精密化すると中心テーマがぼける。

### 本選でやる
- 既知限界をReality Dashboardへ表示
- 基本保存則
- response time
- staffing
- spatial plausibility
を検証

### 後回し
- フル病院capacity model
- 火災CFD
- 犯罪学の全面再構築

---

# 28. Reality Validation Harnessを作る

これが「現実を再現している」と言うための最重要実装。

新規:

`scripts/reality_score.py`

出力:
- `reality_score.json`
- `reality_score.md`
- dashboard data

---

## 28.1 6カテゴリ

### A. Population
- age
- sex
- worker/student
- resident/visitor
- foreign
- household

### B. Mobility
- occupancy by hour
- OD
- trip counts
- purpose
- mode
- travel time

### C. Time use
- sleep
- work/school
- travel
- home awake
- leisure
- media
- meal

### D. Spatial
- building occupancy
- station flow
- street density
- POI visits

### E. Social
- conversation
- relation degree
- household contact
- workplace contact
- online activity

### F. Economy
- income
- spending
- rent
- store revenue
- unemployment

---

## 28.2 指標

データ型に応じて:
- MAE
- RMSE
- MAPE
- Jensen-Shannon divergence
- Wasserstein distance
- correlation
- KS statistic

**すべてを1個の謎スコアへ潰さない。**

トップ画面には総合indexを出してよいが、必ずcomponentを見せる。

---

## 28.3 内部目標値

これは「学術標準」ではなく、本プロジェクトの実装gate。

### Population
JSD < 0.05を目標

### mode share
主要手段 ±5 percentage pointsを目標

### hourly presence
主要時間帯 MAPE < 20%を目標

### time use
主要カテゴリ ±30–60min/dayを目標

### trip count
±20%程度を目標

達成できないものは隠さず赤表示。

---

# 29. 必ずholdout validationをする

calibrationした同じデータだけで精度を示すと弱い。

例:

### calibration
- 平日
- 06–16時
- resident population

### validation
- 16–24時
- weekend
- visitor flow

または地理的に:
- 渋谷駅東
- 西側holdout

**「合わせた」ではなく「未知部分でも再現した」を1個作る。**

これは審査で非常に強い。

---

# 30. seedを複数回す

1 seedの面白い創発は偶然かもしれない。

### 最低
- final 250k main seed × 1
- 50k〜100k validation seed × 2–4

### 余力
同じ介入を複数seed。

表示:
```text
mean
p10
p50
p90
```

「予言」ではなく「結果分布」にする。

---

# 31. ablationを必ず取る

本当にLLMが価値を生んでいるかを示す。

最低4条件:

1. Full
2. LLM cognition reduced/off
3. social graph reduced
4. intervention off

見る:
- mobility
- social clustering
- belief spread
- satisfaction
- spending
- emergent events

**LLMを増やしたことで何が変わったか**を説明できる。

---

# 32. 因果トレースをデモ可能にする

すでにprovenance資産がある。

ViewerでAgentを1人クリック:

```text
09:10 電車遅延を認識
09:20 予定変更をLLM判断
09:40 別店舗へ移動
10:00 友人Aと遭遇
10:20 SNS投稿
11:30 投稿を見たBが来店
...
```

というtimelineを出す。

25万人の集計だけでは「生きている社会」が伝わりにくい。

**macro → micro drilldown**
が重要。

---

# 33. 最終Viewer

## 必須画面1: 3D Shibuya
PLATEAU 3D Tiles

overlay:
- agent density
- traffic
- crowd
- events
- buildings

25万人を全員3D humanoidで描かない。

LOD:
- zoom out: heatmap/particles
- mid: sampled points
- close: selected individuals

---

## 必須画面2: Reality Dashboard

```
Population     94/100
Mobility       87/100
Time Use       82/100
Spatial        91/100
Social         74/100
Economy        80/100
```

数字は実測から生成。

「何がまだ違うか」も表示。

---

## 必須画面3: Counterfactual Compare

左右:

```text
BASELINE        INTERVENTION
```

同じseedからfork。

グラフ:
- crowd
- travel delay
- store revenue
- satisfaction
- rumor
- health
- social response

---

## 必須画面4: Agent Inspector

- persona
- home/work
- current plan
- recent memory
- relationship
- current thought
- why action changed
- provenance

---

# 34. 最終デモのシナリオ

3つ作り、発表では1つ主役にする。

## A. 渋谷駅の交通障害
例:
- 一部路線停止
- station capacity低下

観察:
- rerouting
- crowd
- missed appointments
- store demand shifts
- SNS
- satisfaction
- propagation

### 強み
交通×社会×経済が全部見える。

---

## B. 猛暑 / 豪雨

観察:
- outdoor movement
- heat illness
- shopping
- indoor migration
- transport
- vulnerable populations

### 強み
実気象を使える。

---

## C. 都市開発 / 新施設 / 歩行者空間介入

「まだ存在しない都市状態」を実行。

- road closure
- pedestrian plaza
- new building / retail
- station exit changes

### 強み
このプロジェクトの事業価値に直結。

**最終発表の主役はCを推奨。**
A/Bを「現実応答の検証」、Cを「未来の反実仮想」に使う。

---

# 35. GPUを「必然」にする

ハッカソンの審査ではGPU利用の必然性が重要。

説明:

> CPU上のABMだけなら25万人を動かすことはできる。しかし本プロジェクトでは、25万人が同じルールで動くのではなく、現実データに接地した個別の履歴・関係・環境刺激から、毎シミュレーション日数十万回規模のLLM意思決定を生成する。7 GPUは「人数」ではなく「認知の異質性」を実時間内に維持するために必要。

示すベンチ:
- 1 GPU
- 7 GPU
- LLM calls/day
- req/s
- GPU utilization
- wall time
- quality tier

これでGPUの必然性を数字で示す。

---

# 36. 14日間の実行計画

## 8/16 — Day 0: 測る・凍結点を作る

### 必須
- current main tag
- full tests
- server inventory
- 2k benchmark
- 10k×144 mock RSS
- vLLM7起動
- `R_eff`
- disk write
- checkpoint size/time
- PLATEAU 2025 download開始
- persona v2 build
- ODPT申請（使えるなら）

### 成果
`reports/bench/day0.json`

**この日まで推測だった数字を実測へ変える。**

---

## 8/17 — Day 1: Engineering P0

Claude parallel tasks:
1. live-only `agent_by_id`
2. streaming checkpoint
3. transactional checkpoint
4. frozen finals config / mock fail-fast
5. batch_llm
6. vLLM seed
7. adaptive LLM controller skeleton

### 夜
10k×144 + 50k短煙

---

## 8/18 — Day 2: Reality Core Freeze

### 必須
- persona v2
- workplace_scope / at_home wiring
- home != sleep
- cognition.fire safety fix
- initial relationship calibration
- PLATEAU building extraction v1
- Reality Score harness skeleton

**この日でβの構造変更を凍結。**

以降の高リスク機能はfeature flagのまま。

---

## 8/19 — Day 3: Mobility / Spatial

- PLATEAU↔OSM↔org join
- building capacity
- entrance
- PT calibration
- time-use validation
- viewer PLATEAU
- 50k×1 day real LLM

### Gate
- RSS
- calls/day
- R_eff
- home rate
- mobility error

---

## 8/20 — Day 4: Cognition / Social

- adaptive budget tune
- fairness
- fire ON/OFF
- scalable friend graph
- relation formation
- conversation session
- memory consolidation

### 実測
LLM:
- 0.5/person/day
- 1.0
- 1.5

短A/B。

---

## 8/21 — Day 5: 250k rehearsal + Codex Review 1

- 250k×144step
- real backend
- checkpoint/resume
- full observer
- watchdog
- disk
- Discord

Codex 6-pass。

### merge条件
P0/P1のみ。

---

## 8/22 — Day 6: Fix + Freeze + Main Run Start

- Codex findings fix
- tests
- config hash
- data manifest
- reality baseline report
- final tag

**本番開始を優先。**

実験中にmain engineを変更しない。

---

## 8/23–8/28 — Main Run

並行作業:
- viewer
- analysis
- pitch
- counterfactual branch
- smaller seed runs
- figures
- causal stories

本番プロセス:
- watchdog
- Discord
- checkpoint
- backup
- telemetry

---

## 8/28–8/29 — Analysis / Counterfactual

- final reality score
- baseline vs intervention
- seed bands
- ablation
- macro plots
- 5〜10 representative agents
- demo recording

---

## 8/30 — Submit

- GitHub
- reproducibility instructions
- final LT
- 2–3 minute backup video
- architecture diagram
- result plots
- reality validation table

---

# 37. 実装の優先順位

## P0 — 絶対にやる
1. finals mock fail-fast + resolved config
2. batch_llm
3. adaptive LLM budget
4. lifecycle RAM leak
5. checkpoint streaming/atomic
6. 10k×144 / 250k rehearsal
7. persona v2 + missing wiring
8. home != sleep
9. PLATEAU 2025 viewer + engine building layer
10. Reality Score
11. final 3D compare viewer
12. main run

---

## P1 — 強く推奨
13. cognition.fire
14. LLM seed plumbing
15. scalable friend graph
16. relationship calibration
17. PT mobility calibration
18. time-use calibration
19. building capacity
20. agent inspector
21. baseline/intervention fork
22. multi-seed small/medium runs
23. ablation

---

## P2 — 時間が余れば
24. richer indoor archetype
25. ODPT realtime
26. event calendar ingestion
27. deeper SNS
28. deeper household activities
29. quality LLM tier
30. station microphysics expansion

---

## P3 — 本選前にやらない
- 全建物の実フロアプラン作成
- 25万人全員の毎10分LLM
- 火災CFD
- 医療制度完全再現
- 警察組織完全再現
- Unreal級3D rendering
- model architecture全面変更
- Δt=1分への全面移行
- engineの大規模rewrite
- 「新機能100個追加」

---

# 38. 完成判定 Gate

## Engineering
- 250k×144step rehearsal完走
- OOMなし
- RSSが時間とともに無制限上昇しない
- checkpoint→resume成功
- log/state整合
- backend実LLM確認
- 7 GPU利用
- no silent fallback

## LLM
- target calls/person/day達成
- starvation率を出す
- GPU利用率/queue latency可視化
- failure rate < 1%目標
- timeout/retry可視化

## Spatial
- PLATEAU buildings loaded
- agents outside navigable world比率を測定
- org→building join率
- station/road/underground layer

## Population
- v2
- age distribution
- resident/worker/visitor
- school/child/elderly

## Daily life
- home awakeが存在
- evening home population
- leisure
- sleep distribution

## Mobility
- PT reality report
- OD/time/mode

## Scientific
- calibration vs holdout
- seed variation
- ablation
- data provenance

## Demo
- 3D city
- 25万人規模を視覚化
- click agent
- intervention compare
- reality score

---

# 39. 重要: Reality Scoreは「出力を現実へ強制する装置」にしない

悪い実装:

```python
if current_station_count < real_target:
    spawn_agents_until_target()
```

これでは結果を再現しているのではなく、答えを入れているだけ。

正しい:

```text
initial conditions
behavior parameters
transport schedule
building capacity
persona distribution
```

をcalibrateして、

**出力は自由に出させる。**

そして誤差を測る。

---

# 40. データprovenance manifest

全外部データに:

```text
source
source_version/year
retrieved_at
license
sha256
bbox
transform_script
output_hash
```

を付ける。

`data/manifest.yaml`

例:
```yaml
plateau_shibuya_2025:
  municipality_code: 13113
  spec: v5
  retrieved_at: ...
  sha256: ...
  transform: scripts/build_plateau_world.py
```

発表時に「データをどこから持ってきた？」へ即答できる。

---

# 41. 外部データ優先順位

## 1. Project PLATEAU 2025 Shibuya
最優先。

検索対象:
- PLATEAU 配信サービス
- municipality code: `13113`
- year: `2025`
- spec: V5

## 2. 東京都市圏パーソントリップ調査
- 第6回
- 小ゾーン
- OD
- 滞留
- purpose
- mode
- travel time

## 3. e-Stat / 国勢調査
- demographic
- work
- household

## 4. 社会生活基本調査 2021
- time use
- sleep
- leisure
- work
- household

## 5. 気象庁
- actual weather

## 6. GTFS / ODPT
- transit

## 7. 渋谷区/東京都open data
必要な施設・行政情報。

---

# 42. Claude Codeへ渡す実装ルール

この計画をClaudeへ渡したら、以下を最優先ルールにする。

## Rule 1
**大きなrewriteをしない。**

## Rule 2
新規機能は原則feature flag付き。
既定OFFで既存世界を壊さない。

## Rule 3
1機能につき必ず:
- test
- benchmark（性能影響がある場合）
- logging
- acceptance metric

## Rule 4
「実装した」ではなく、
**本番configから到達可能か**まで確認。

## Rule 5
設定に存在してもengineが読まない「dead config」を禁止。

## Rule 6
silent fallback禁止。

実LLMが落ちたら、Mockへ静かに切り替えず、
- fail
- explicit degraded mode
のどちらか。

## Rule 7
外部データ欠損をLLMで勝手に作らない。

## Rule 8
reality featureには必ず:
```text
source
target statistic
calibration metric
validation metric
```

を付ける。

## Rule 9
25万人向けコードはO(N²)禁止。

## Rule 10
毎回:
```bash
pytest
```
だけでなく、対象のscale smokeを走らせる。

---

# 43. Claude向け task template

各実装はこの形式で進める。

```markdown
## Task
[機能名]

### Why
現実再現/信頼性/性能の何を改善するか

### Existing code
関連ファイルと現在の挙動

### Change
最小変更

### Invariants
壊してはいけないもの

### Tests
unit / integration / resume / R1

### Performance
Big-O / RSS / wall impact

### Reality metric
何を現実と比較するか

### Gate
merge条件

### Result
実測値
```

---

# 44. Codexレビューの使い方

Claudeが実装したら:

1. Claude: tests + benchmark
2. Git diffを残す
3. Codex read-only review
4. Claudeは指摘を**検証してから**修正
5. tests
6. Codex再レビュー
7. merge

### review観点
- correctness
- hidden dead path
- config wiring
- race/concurrency
- memory
- N²
- checkpoint
- fallback
- reproducibility
- realism bias
- testing gaps

---

# 45. 自動で調べるべき性能telemetry

毎step/日:

```text
step_wall_s
cpu_percent
rss_gb
gpu_util[7]
gpu_vram[7]
llm_queue
llm_req_s
llm_input_tok_s
llm_output_tok_s
calls_by_purpose
calls_by_tier
agents_with_0_calls_today
checkpoint_s
checkpoint_gb
l1_events
disk_free
```

Dashboardに出す。

これがadaptive schedulerの入力になる。

---

# 46. GPU呼数の自動制御式のたたき台

```python
remaining_budget_s = deadline_monotonic - now
remaining_steps = n_steps - step

target_wall_per_step = remaining_budget_s / remaining_steps

non_llm_est = ema_non_llm_step_s
llm_wall_allowance = max(
    0,
    target_wall_per_step - non_llm_est - io_reserve_s
)

budget = floor(
    llm_wall_allowance
    * ema_effective_req_per_s
    * safety_factor
)
```

`safety_factor ≈ 0.7–0.85`から開始。

さらに:
```python
budget = clamp(budget, min_budget, max_budget)
```

GPU queueが空なら増やす。
deadlineが危なければ減らす。

これなら「300」という人為的固定値を捨て、**与えられたGPUを最後まで使う**。

---

# 47. LLM purpose budget

step budgetを:

```text
deliberate/action    35%
conversation         25%
plan/replan          15%
reflection           10%
social/sns           8%
life decisions        5%
reserve                2%
```

の初期weightで持つ。

これはhard quotaではない。

unused budgetは別queueへborrow。

事件時はincident queueがreserveを取る。

---

# 48. Tokenを短くする

呼数を増やしたいなら、1callを短くする。

### action
100–200 output tokens

### plan
200–350

### conversation
80–200

### reflection
200–500

長文人格説明を毎回promptへ入れない。

sticky prefix / static persona prefixを利用。

memoryはtop-k relevantのみ。

**「質を落とさず1 requestを軽くする」ことが、モデルを小さくするより先。**

---

# 49. structured outputを徹底

LLMの自由文をengineが再解釈する量を減らす。

例:

```json
{
  "intent": "go_home",
  "target": "home",
  "confidence": 0.81,
  "reason_short": "...",
  "social_target": null,
  "memory_write": [...]
}
```

発表用にはreasonを見せられる。

engineはenumを処理。

---

# 50. 「現実らしさ」の最大の敵は作話より内部不整合

以下のような状態を全数検査する:

- job exists but workplace invalid
- at home but location street
- sleeping outside
- child working
- dead agent transacting
- emigrated agent appearing
- org closed but customers inside
- train rider not on route
- building overcapacity
- conversation beyond audible distance
- fire responder nonexistent
- money transfer to missing owner

新規:
`scripts/audit_world_invariants.py`

250k rehearsal後に実行。

---

# 51. Sanity invariantをL2に出す

毎日:

```text
invalid_location
invalid_home
invalid_workplace
overcapacity
impossible_speed
sleep_outside
age_role_violation
duplicate_agent
money_residual
dangling_relation
missing_org
llm_starved
```

0であるべきものと、許容値があるものを分ける。

---

# 52. 完成度を5段階で評価する

## Level 1 — Runs
動く。

## Level 2 — Coherent
内部矛盾がない。

## Level 3 — Grounded
現実データを初期条件に使う。

## Level 4 — Validated
出力が現実と比較される。

## Level 5 — Counterfactual
現実を再現したbaselineから、未実施の介入を比較できる。

**ハッカソン終了時の目標はLevel 5。**

---

# 53. この14日で最も避けるべき罠

### 罠1
「もっと機能を実装すればリアルになる」

違う。
未較正機能はノイズを増やす。

### 罠2
「25万人ならすごい」

人数だけでは弱い。
25万人×同じルールは大規模なだけ。

### 罠3
「LLMを毎step呼べばリアル」

違う。
低レベルルーチンまでLLM化すると遅く、再現性も落ちる。

### 罠4
「3Dが綺麗ならdigital twin」

違う。
見た目と行動検証は別。

### 罠5
「現実値へ出力を強制する」

それはsimulationではない。

### 罠6
「本番run中にもengineを変更」

再現性を失う。

---

# 54. 優勝を狙う発表構成

## 1. 問い
> 都市の政策や空間を変える前に、その都市をもう一度実行できないか？

## 2. 既存手法の限界
- 交通モデルは移動
- 経済モデルは経済
- synthetic usersはQ&A
- LLM societyは小規模

## 3. 解
> 実在渋谷を、空間・人・交通・経済・社会関係・LLM認知を統合した25万人の人工社会として実行する。

## 4. GPU
7 GPUで数百万件規模のsemantic cognition。

## 5. Reality proof
現実統計 vs simulation。

## 6. Live city
PLATEAU Shibuya。

## 7. One person
Agentの人生を追う。

## 8. Counterfactual
都市介入。

## 9. 結果
世界AとBの違い。

## 10. 意義
> 予測値を1個返すのではなく、「別の都市を先に実行して観察する」。

---

# 55. 最終的に言える状態

理想的な最終説明:

> 私たちは「このシミュレーションが現実と完全に同一」と仮定していません。  
> そこで、人口、移動、生活時間、空間利用、社会関係、経済の各レイヤを現実データと別々に検証しました。  
> このダッシュボードが、その一致度と残る誤差です。  
> この検証済みbaselineを同じ初期状態からforkし、まだ現実には存在しない都市介入を実行しました。  
> 25万人の各個人は、同一のスクリプトではなく、属性・記憶・関係・環境刺激に応じて必要な局面でLLM推論を行います。  
> だからこれは静的なデジタルツインではなく、**実行可能な社会のデジタルツイン**です。

この方が、
「完璧に現実です」
と断言するより遥かに強い。

---

# 56. Claude Codeへの最初の指示文

以下をそのままClaude Codeへ渡す。

```text
このファイルを本選までの上位実装計画として読んでください。

目的は新機能の数を増やすことではありません。
残り期間で以下を最大化します。

1. 25万人×10日が壊れず完走すること
2. 実在渋谷の空間・人口・移動・生活時間へ接地すること
3. LLM認知密度をGPU実測能力まで引き上げること
4. 出力を現実統計と定量比較すること
5. baselineとcounterfactualを比較できること
6. 審査で技術・GPU必然性・社会実装価値が一目で伝わること

まずP0を実装順へ分解し、
各Taskについて
- 現状コード
- 問題
- 最小修正
- テスト
- 性能影響
- Reality metric
- merge gate
を提示してください。

大規模rewriteは禁止です。
既存feature flag/R1/reproducibilityを守ってください。
O(N^2)は禁止です。
外部データ欠損をLLMで捏造しないでください。
本番configから到達不能な実装を「完了」と数えないでください。
silent fallbackは禁止です。

各実装が終わったら、必ずテストとscale smokeの実測結果を報告してください。
Codex reviewに渡せる単位で変更を区切ってください。
```

---

# 57. 最初にClaudeへ切る具体的issue

## ISSUE-01: Production config safety
- resolved finals config
- vLLM required
- mock fail-fast
- startup manifest

## ISSUE-02: Lifecycle memory
- `agent_by_id`
- departed refs
- checkpoint

## ISSUE-03: Checkpoint transaction
- streaming
- atomic marker
- kill tests

## ISSUE-04: Batch LLM + telemetry
- workers
- concurrency
- req/s

## ISSUE-05: Adaptive LLM budget
- dynamic calls
- fairness
- purpose queues

## ISSUE-06: Persona v2 activation
- pool
- workplace_scope
- at_home

## ISSUE-07: Home awake lifecycle
- home != sleep
- evening activities

## ISSUE-08: PLATEAU 2025 ingestion
- fetch
- extract
- building parquet
- 3D viewer

## ISSUE-09: Reality Score
- population
- mobility
- time use

## ISSUE-10: 250k rehearsal
- RSS
- LLM
- checkpoint
- disk
- invariants

この10 issueを8/16–8/21の主軸にする。

---

# 58. 最終チェックリスト

## World
- [ ] PLATEAU 2025
- [ ] real roads
- [ ] buildings
- [ ] station/underground
- [ ] weather
- [ ] transit

## Population
- [ ] v2
- [ ] children
- [ ] elderly
- [ ] residents/workers/visitors
- [ ] workplace/home wired

## Life
- [ ] home awake
- [ ] leisure
- [ ] meal
- [ ] household
- [ ] realistic sleep

## Cognition
- [ ] adaptive budget
- [ ] fire
- [ ] fairness
- [ ] memory
- [ ] reflection timing
- [ ] 7 GPU batching

## Social
- [ ] scalable initial graph
- [ ] endogenous tie formation
- [ ] conversations
- [ ] SNS

## Reliability
- [ ] no agent leak
- [ ] checkpoint streaming
- [ ] atomic resume
- [ ] frozen config
- [ ] fail-fast
- [ ] telemetry

## Validation
- [ ] population
- [ ] mobility
- [ ] time use
- [ ] spatial
- [ ] social
- [ ] economy
- [ ] holdout
- [ ] seeds
- [ ] ablation

## Demo
- [ ] 3D city
- [ ] reality dashboard
- [ ] counterfactual
- [ ] agent inspector
- [ ] causal trace
- [ ] backup recording

---

# 59. 参考にするリポジトリ内文書

- `STATUS.md`
- `PENDING.md`
- `conf/finals_observe.yaml`
- `conf/profiles/finals-vllm7.yaml`
- `docs/plans/finals-endgame-plan.md`
- `docs/plans/finals-hardware-plan.md`
- `docs/plans/persona-pool-v2-plan.md`
- `docs/plans/age-diversity-plan.md`
- `docs/plans/reflection-leisure-plan.md`
- `docs/research/scale-feasibility.md`
- `docs/research/finals-llm-budget.md`
- `docs/research/initial-relations-improvement.md`
- `docs/research/relations-formation-map.md`
- `docs/research/off-features-inventory.md`
- `ops/codex-review-pack.md`
- `ops/finals-compute-checklist.md`

---

# 60. 外部一次データ / 公式データ

## Project PLATEAU
2025年度渋谷区データ。自治体コード13113。V5。  
建築物LOD2、道路LOD3、都市設備LOD3、地下街LOD4.1等。

取得はPLATEAU配信サービスのcatalog APIから最新datasetを解決する方式にする。
固定URLをコードへ埋め込まず、metadataとhashを保存。

## 東京都市圏交通計画協議会
第6回東京都市圏パーソントリップ調査。
個人属性、目的、交通手段、OD、滞留人口、平均所要時間等。

## 総務省統計局
令和3年社会生活基本調査。
生活時間、自由時間活動。

## 気象庁
過去の気象データ。

## ODPT
公共交通オープンデータセンター。
API利用は登録が必要なため、本番の必須依存にはしない。

---

# 61. この計画の最終原則

> **リアルに見えることではなく、現実と比較できること。**  
> **人数が多いことではなく、一人一人が異なる理由で動くこと。**  
> **LLMを多く呼ぶことではなく、社会を変える意思決定へGPUを使うこと。**  
> **機能が存在することではなく、本番設定から実際に発火すること。**  
> **面白い結果が1回出ることではなく、seedを変えても説明できること。**  
> **未来を当てたと言うことではなく、別の未来を実行して比較できること。**

この6点を守れば、残り14日間でやるべきことはかなり明確になる。

---

# Appendix A — 実装後に必ず出す最終数値

```text
N_persona_pool
N_present_peak
N_distinct_agents_10days

wall_time_total
sim_day_per_wall_day

peak_rss_gb
checkpoint_gb
disk_total_gb

gpu_util_mean[7]
gpu_vram_peak[7]
llm_total_calls
llm_calls_per_agent_day
llm_calls_by_purpose
llm_req_per_sec
llm_failure_rate
agents_zero_llm_share

population_JSD
hourly_presence_MAPE
mode_share_error_pp
trip_count_error
home_awake_error_min
sleep_error_min

relation_degree
relation_clustering
conversations_per_agent_day

money_conservation_residual
spending_distribution_error

reality_score_components

baseline_vs_intervention_effects
seed_uncertainty
```

---

# Appendix B — 「優勝」のための成果物パッケージ

```text
README.md
ARCHITECTURE.png
REALITY_VALIDATION.md
REPRODUCIBILITY.md
DATA_MANIFEST.md
FINAL_RESULTS.md

viewer/
  plateau city
  reality dashboard
  counterfactual compare
  agent inspector

runs/
  baseline
  intervention
  ablations
  seeds

figures/
  reality radar
  mobility curves
  time use
  LLM GPU scaling
  intervention effects
  causal trace
```

---

# Appendix C — やる順番を1行で

> **壊れない → GPUを使い切る → PLATEAU/v2で現実へ接地 → 帰宅/生活を直す → cognitionを増やす → PT/生活時間で検証 → 25万リハ → freeze → 本番 → 反実仮想 → 発表**

