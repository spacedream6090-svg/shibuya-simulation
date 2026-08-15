# Shibuya Simulation — Resource-Aware Maximum Improvement Audit

> 作成日: 2026-08-16  
> 対象リポジトリ: `spacedream6090-svg/shibuya-simulation`  
> 再監査基準HEAD: `12970725818aa34d0e6eb7bd4e5ba1d2f7562dd0`  
> 対象サーバー: `gpu-sv-002` — RTX A5000 24GB × 7 / RAM 251 GiB / 64 logical CPU / 2 NUMA / `/home` 約3.7TB空き  
> 提出期限: 2026-08-30  
> β凍結目標: 2026-08-18  
> 本番開始目標: 2026-08-22  
>
> 目的: 既存の4監査文書を踏まえつつ、もう一度ゼロベースで  
> **「まだ抜けている必須事項」と「入れられるなら明確に価値がある改善」を、現在の実装・残り期間・実機リソース・2025–2026年の研究/公式データから再評価する。**
>
> 本文書は新機能のwishlistではない。  
> **本番前にやる / 並行解析でやる / 尾部でやる / 本選後に送る**を明確に分離する。

---

# 0. Executive verdict

結論から言うと、**改善余地はまだある**。

ただし、現在の最大のボトルネックは「社会機能の数」ではない。

今のシミュレーションには既に、

- 人口・在場ローテーション
- ペルソナ
- 家族/世帯
- 組織
- 通勤・日課
- day plan
- 会話
- 記憶
- belief
- relation
- media/SNS
- economy
- health
- crime
- disasters
- public transport
- affect / needs / drive
- LOD
- provenance
- checkpoint / resume
- observer

など大量の機構が存在している。

ここからハッカソン提出品質を最も上げるのは、

```text
機能追加
```

ではなく、

```text
1. 実LLMが25万人に十分届いていること
2. そのLLMが人間行動として妥当であること
3. 日常生活の大きな構造誤差を消すこと
4. 現実データとの一致を数値で示すこと
5. 結果がseed / prompt / model / parameterの偶然ではないこと
6. 250k本番が落ちず、同じ条件で再現できること
7. baselineからcounterfactualをforkできること
```

である。

本再監査の最終優先順位は次。

## Tier S — 本番前に閉じるべきもの

1. 実LLMモデル・sampling・revisionの完全凍結
2. `max_llm_per_step` の再導出
3. LLM coverage / fairness の測定
4. DPH-B予算の実効利用率測定
5. `engine.batch_llm` 実機A/B
6. HOME_AWAKE最小版
7. mock production fail-fast
8. checkpoint streaming / fsync / COMPLETE
9. 10k×144 → 50k → 100k → 250k scale validation
10. Reality Score + Human Behavior Score + world invariants

## Tier A — 入れられるなら非常に価値が高い

11. 8B / 14B / 32B-AWQ Behavioral Tournament
12. purpose別 multi-model LOD
13. vLLM JSON Schema structured outputs
14. request-level stable seed
15. prompt prefix/cache efficiency measurement
16. 5k程度のHigh-Cognition Shadow Simulation
17. time-of-day concurrent population validation
18. latest official data refresh
19. model/prompt sensitivity mini-suite
20. paired checkpoint counterfactual analysis

## Tier B — 尾部・解析側で入れると強い

21. parameter sensitivity mini-ensemble
22. seed2短縮版
23. component confidence intervals
24. Data Vintage Ledger
25. Spatial Support Crosswalk
26. model behavior card
27. intervention fork 1本
28. PLATEAU 2025 viewer更新
29. GPU/vLLM utilization report

## Tier C — 価値は高いが今の本線には入れない方が良い

30. contextual habit learning全面版
31. hunger / sleep pressure全面版
32. microthought C1 scheduler
33. dynamic goal memory
34. social attention budget
35. group/hyperedge conversation
36. household joint decision
37. workplace substates
38. restricted choice-set再設計
39. full information processing pipeline
40. CVA/value-verifier型認知
41. fine-tuned human behavior policy
42. online data assimilation
43. ABC / Bayesian calibration本格版
44. surrogate/distillation
45. PLATEAU engine-side full building/interior graph
46. global dt=1min

---

# 1. まず訂正 — LLM呼数の現状

以前のサーバー容量メモでは、25万人で総LLM密度を約4.5–5.5 call/person/dayとする想定を書いた。

**これは現行finals configの説明としては誤り。**

最新コードでは第115 DPH-Bにより、

```yaml
lod:
  max_llm_per_step: 300
  budget:
    tiers:
      enabled: true
```

となり、`plan` / `reflect`も総budget内へ入った。

したがって、

```text
300 calls/step
× 144 steps/day
= 43,200 calls/day
```

25万人で割ると、

```text
43,200 / 250,000
= 0.1728 calls/person/day
```

となる。

つまり現行値は本当に

**約0.17 LLM call / person / simulation day**

しかない。

10日でも最大43.2万calls。

現行の250k本線では、大多数のagentのplan / reflectがLLMではなくfallbackへ落ちる。

## 推奨cap候補

| cap/step | 10日総call上限 | call/person/day |
|---:|---:|---:|
| 300 | 432,000 | 0.173 |
| 1,000 | 1,440,000 | 0.576 |
| 1,500 | 2,160,000 | 0.864 |
| 2,000 | 2,880,000 | 1.152 |
| 2,500 | 3,600,000 | 1.440 |
| 5,000 | 7,200,000 | 2.880 |

現段階の第一候補は、

**1,500–2,500 / step**

である。

ただし値は思想ではなく、A5000×7上で得る`R_eff`で決める。

---

# 2. 「LLM呼数を増やす」だけでは不十分

LLM社会シミュレーションの近年研究は、重要な警告を出している。

ACL 2026のLu et al.は、31,865件の実オンライン購買セッション・230,965行動でLLM agentを評価し、prompt-onlyモデルのstep-by-step action accuracyが11.86%だったと報告している。

つまり、

```text
believable
≠
behaviorally accurate
```

である。

さらにFindings ACL 2026のContext-Value-Action研究では、**reasoningを強くするほどbehavioral fidelityが上がるとは限らず、むしろvalue polarizationとpopulation diversity collapseを悪化させるケース**が示されている。

したがって本シムでは、

> LLMを多く呼ぶ

ではなく、

> **どのLLMを、どの認知イベントで、どの深さで呼ぶか**

が重要。

---

# 3. Tier S-1 — 実LLMを完全に凍結する

現在のrepoのvLLMプロファイル例は`qwen3:8b`表記。

本番では曖昧なaliasではなく、少なくとも以下までmanifestに残す。

```text
model_repo
model_revision
model_file SHA / revision
quantization
tokenizer revision
tokenizer_config SHA256
chat_template SHA256
generation_config SHA256
vLLM version
transformers version
CUDA version
driver version
launch arguments
sampling params
```

## 推奨候補

Qwen公式Hugging Faceでは以下のAWQモデルがvLLM serveに対応。

| Model | HF repository size | 用途候補 |
|---|---:|---|
| Qwen3-8B-AWQ | 約6.11 GB | main cognition |
| Qwen3-14B-AWQ | 約9.99 GB | high-value cognition / reflect |
| Qwen3-32B-AWQ | 約19.3 GB | deep cognition実験 |

A5000は1枚24GB級。

14B AWQはweightsだけ見ればかなり余裕がある。

32B AWQはweightsだけで約19.3GBなので、**単GPUでweightは入り得るがKV cache・runtime overheadを含めて安定運用できるとは限らない**。

したがって32Bは、

```text
single GPU smoke
↓
無理なら TP2
```

で判断する。

---

# 4. Tier S-2 — sampling contract

現状`VllmBackend`は、

```text
temperature
max_tokens
think
```

を送るが、request-level seedは送っていない。

vLLMの現行SamplingParamsにはrequestごとの`seed`がある。

## 推奨

```python
seed = stable_hash(rng_key) & 0x7fffffff
```

をrequestへ入れる。

意味は、

> 同じagent / same step / same purposeならsame sampling seed

という契約。

GPU kernelまで含む完全bit determinismを保証するものではないが、再現性は明確に改善する。

---

# 5. generation_configの固定

vLLM現行仕様では、

```text
--generation-config auto
```

がdefault。

`auto`ではmodel repositoryにある`generation_config.json`を読む。

したがって本シム側でtemperatureを指定していても、指定していないsampling parameterがmodel側defaultへ依存する余地がある。

本番は、

```bash
--generation-config vllm
```

でmodel-side generation defaultsを切り、

必要なsampling parametersを本シム側で明示する方が再現性は高い。

例:

```text
temperature
top_p
top_k
min_p
presence_penalty
frequency_penalty
repetition_penalty
seed
max_tokens
```

すべてを明示。

---

# 6. Tier S-3 — DPH-Bの隠れた利用率問題

現在のbudgetは概ね、

```text
life    30%
reply   20%
general 50%
```

の予約式。

重要な仕様:

- reply/lifeはgeneralの余りを借りられる
- generalはreply/lifeの余りを借りられない

つまり、

```text
cap=2500
```

としても、そのstepで2500call全部使うとは限らない。

朝:

```text
plan需要 ↑
```

昼:

```text
social/general需要 ↑
```

夜:

```text
reflect需要 ↑
```

と需要構造が違うため、固定quotaが遊ぶ可能性がある。

## まず測る

各step:

```text
cap
used
used/cap
life granted/denied
reply granted/denied
general granted/denied
unused life reservation
unused reply reservation
```

## 判断

```text
mean used/cap >= 0.90
```

なら現状でよい。

```text
0.75–0.90
```

ならlane share再調整。

```text
< 0.75
```

ならunused reservation reclaimを検討。

本番直前に新しいAdaptive Controllerを書くのではなく、まず現行DPH-Bのcapacity utilizationを測る。

---

# 7. Tier S-4 — LLM coverage fairness

平均call数だけでは社会全体にLLMが届いているか分からない。

例えば、

```text
Case A:
25万人 × 1回

Case B:
2.5万人 × 10回
22.5万人 × 0回
```

は同じ総callsでも全く別物。

## 必須指標

```text
calls/person/day
zero-call rate
P50/P90/P99 calls/person/day
Gini(calls/person/day)
LLM plan coverage
LLM reflect coverage
reply success
fallback rate
```

さらに、

```text
age
occupation
resident/worker/visitor
household type
time of day
input LOD
```

で分解する。

## Acceptance例

厳密値は実測後に決めるが、最低でも、

```text
zero-call % が極端な属性偏りを持たない
reply denied が特定層へ偏らない
life coverageがresidentだけに集中しない
```

を確認。

---

# 8. Tier S-5 — `engine.batch_llm`

repoでは`CachedLLM.generate_many()`があり、workers>1でcache missを並行発行できる。

一方、finals configではbatch LLMが本番ONになっていない。

これは7GPUを持っているのにHTTP発行側がserialになり得るという問題。

## 実機A/B

同じseed、同じ2000体程度で、

```text
workers=1
workers=4
workers=8
workers=16
```

を比較。

見るもの:

```text
req/s
wall time
state hash
event distribution
cache results
server queue
P95 latency
```

決定論が守られ、workers=8が明確に速ければ本番ON。

---

# 9. Tier S-6 — HOME_AWAKE

現在確認済みの最大級の生活時間誤差。

```text
arrive home
≈
sleep_start
```

となる経路があり、帰宅後覚醒時間がほぼ消える。

これは、

- 食事
- 入浴
- SNS
- 動画
- 家事
- 家族会話
- 趣味
- 勉強
- 翌日準備
- 買い物後処理

の時間を丸ごと消す。

2021社会生活基本調査は生活時間・時間帯別活動を提供しており、HOME_AWAKE較正に使える。

## 本選前の最小版

大規模な認知改修をせず、

```text
HOME_AWAKE
↓
home activity rule
↓
bedtime hazard
↓
sleep
```

だけ入れる。

在宅活動候補:

```text
meal
bath
housework
family
media
hobby
study
rest
```

LLM不要。

## 理由

これは「nice to have」というより、現実再現の構造欠陥修正。

---

# 10. bedtime hazard

就寝を固定stepではなく、

```text
circadian time
sleep pressure
fatigue
next-day obligation
age
current activity
social interaction
media session
```

から決める。

ただし本選前は簡易式でよい。

例:

```python
p_sleep = sigmoid(
    b0
    + b1 * circadian
    + b2 * fatigue
    + b3 * sleep_pressure_proxy
    + b4 * next_day_early
    - b5 * active_social
    - b6 * media_active
)
```

hungerや正式sleep_pressure stateを追加しなくても、既存stateから近似可能。

---

# 11. Tier S-7 — checkpoint memory spike

最新repo監査でも、

```python
pickle.dumps(...)
```

による全量bytes一時生成が残っている。

250k checkpointでは、

```text
live state
+
serialized bytes
```

の二重メモリピークになり得る。

## 推奨

```text
pickle.dumps -> pickle.dump(stream)
gzip/file stream
fsync
atomic rename
COMPLETE marker
```

にする。

RAM251GiBがあるとはいえ、checkpoint瞬間ピークで落とすのは最悪の失敗。

---

# 12. Tier S-8 — mock production fail-fast

`finals_observe.yaml`のbase backendはmock用途を残している。

本番でprofile mergeをミスると、

```text
25万人
数日
mock
```

を走らせる事故が起こり得る。

推奨:

```python
if n_agents >= 10000 and backend == "mock" and not allow_mock_production:
    raise RuntimeError(...)
```

加えて起動時に大きく表示:

```text
FINAL MODEL BACKEND = vllm
MODEL = ...
SERVERS = ...
CAP = ...
```

---

# 13. Tier S-9 — fully resolved frozen config

複数profile + dotlist mergeではなく、本番前に、

```text
conf/finals_20260821_frozen.yaml
```

を生成。

その中に全値を解決済みで保存。

manifest:

```text
git SHA
config SHA256
persona pool SHA256
org data SHA256
PLATEAU/data SHA256
model revision
vLLM version
```

を保存。

---

# 14. Tier A-1 — LLM Behavioral Tournament

現在の7GPU環境だからできる高ROI実験。

単なるMMLU的性能ではなく、

**本シムの行動schema上で8B / 14B / 32Bを比較する。**

## Scenario battery

100–500ケース程度。

例:

```text
late for work + rain
tired + invitation
low money + purchase temptation
argument with close friend
crowded route + alternative
unexpected train delay
childcare obligation
job dissatisfaction
misinformation exposure
minor theft victim
stranger requests help
social norm violation
```

## 指標

```text
JSON/schema success
valid action %
fallback %
latency
tokens
human-likeness target score
persona sensitivity
context sensitivity
action diversity
social desirability bias
conflict avoidance
risk preference
repetition
```

## モデル比較

```text
8B AWQ
14B AWQ
32B AWQ
```

32BはTP2でもよい。

## 決定ルール

大きいモデルを採る理由は、

```text
quality gain / compute cost
```

が明確な場合だけ。

---

# 15. Tier A-2 — purpose別 multi-model LOD

repoには既に`RouterLLM`が実装されている。

したがって新規巨大architectureは不要。

候補:

## Configuration A

```text
GPU0-5: Qwen3-8B-AWQ
GPU6:   Qwen3-14B-AWQ
```

routing:

```text
plan/face/reply/media -> 8B
reflect/deep          -> 14B
```

## Configuration B

```text
GPU0-4: Qwen3-8B-AWQ
GPU5-6: Qwen3-32B-AWQ TP2
```

routing:

```text
general cognition -> 8B
rare deep cognition -> 32B
```

Configuration Bは魅力的だが、throughputの主力GPUが5枚になるので**Behavioral Tournamentで差が大きい場合のみ**。

---

# 16. 大きいモデルを全員に使わない理由

Findings ACL 2026は、

> more reasoning intensity does not necessarily increase behavioral fidelity

という重要な結果を示している。

したがって、

```text
32B + thinking
```

を全callへ使うことは「高精度」ではない。

本シムでは、

```text
C0 rule
C1 simple/non-thinking
C2 normal deliberation/non-thinking
C3 deep/optional thinking
```

が合理的。

---

# 17. Tier A-3 — JSON Schema structured outputs

現状は、

```json
response_format: {"type": "json_object"}
```

中心。

vLLMの現行OpenAI互換serverはJSON Schema structured outputsをサポートする。

## 改善案

purpose別schema:

```text
plan.schema.json
conversation.schema.json
reflection.schema.json
decision.schema.json
```

を作り、

```json
response_format:
{
  "type": "json_schema",
  ...
}
```

で制約。

## 利点

```text
malformed JSON減少
unknown action減少
repair/fallback減少
schema違反の静かな混入減少
```

## 注意

constrained decoding自体がoutput distributionを変える。

したがって、

```text
json_object
vs
json_schema
```

でaction distribution / fallback率をA/BしてからON。

---

# 18. Tier A-4 — prompt cache efficiency

現行FleetLLMはagent_id sticky routingを持っている。

これは非常に良い。

同じagentを同じGPUへ寄せることでprefix cache localityを高められる。

ただし本当に効いているかは未実測。

vLLM `/metrics`には、

```text
prefix_cache_hits
prefix_cache_queries
prompt_tokens_cached
kv_cache_usage_perc
num_requests_running
num_requests_waiting
queue_time
TTFT
E2E latency
```

などがある。

## 本番前に必ず記録

各GPU:

```text
prefix hit ratio
queue length
KV usage
prompt tokens
cached prompt tokens
P95 queue time
P95 TTFT
```

---

# 19. prompt canonicalization

prefix hitが低い場合のみ検討。

promptを、

```text
STATIC SYSTEM
STATIC SCHEMA
STABLE PERSONA
SEMI-STABLE LONG MEMORY
DYNAMIC CURRENT STATE
LATEST EVENTS
```

の順に配置すると、shared/stable prefixが長くなりやすい。

ただしprompt順序は行動にも影響するため、**性能だけを理由に本番直前に変えない**。

A/Bでaction distributionが許容範囲なら採用。

---

# 20. Tier A-5 — queue-aware sticky routing

現行FleetLLM:

```text
agent_id sticky
```

はprefix cacheに有利。

しかし、

```text
GPU A: queue 100
GPU B: queue 3
```

でもsticky先を優先する。

vLLM公式もdata-parallel routingで、

- scheduled/waiting queue
- KV cache state

を考慮する価値を説明している。

## まず測る

```text
per-GPU req count
waiting queue
P95 latency
prefix hit
```

## 介入条件

GPU間queue skewが小さければ**触らない**。

大きい場合だけ、

```text
preferred sticky GPU
if queue > threshold:
    fallback GPU
```

を検討。

deadline直前に無条件導入しない。

---

# 21. Tier A-6 — speculative decoding

vLLMは現在、

- n-gram
- suffix
- EAGLE
- draft model
- MTP

等のspeculative decodingをサポート。

本repoの起動スクリプトにもngram speculative seamがある。

## 本シムとの相性

JSON短出力が多いので、長文generationほど利益が大きいとは限らない。

また高QPSでは方法によりgainが変わる。

## 採用条件

```text
same action distribution
same JSON success
req/s +15%以上
P95 latency改善
```

を満たす場合だけ。

speculativeを使うために本番安定性を落とさない。

---

# 22. Tier A-7 — High-Cognition Shadow Simulation

これは最も科学的価値が高い「余力があれば」案の1つ。

## Main

```text
250k
cap 1500–2500
adaptive sparse cognition
```

## Shadow

```text
2k–5k representative agents
much denser LLM
```

同じ人口属性・シナリオを使う。

## 比較

```text
action agreement
trip count
destination category
conversation rate
purchase rate
relationship change
mood distribution
plan deviation
```

目的:

> **どこまでLLMを間引いても挙動が壊れないか**

を実証する。

これは「計算量の都合でLLMを減らした」という弱い説明を、

> 高認知referenceと比較し、必要密度を実測した

へ変える。

---

# 23. Shadowの設計

agentを単純random sampleにせず、

```text
age
occupation
resident/visitor
income
household
social degree
LOD
```

でstratified sample。

少なくとも500×複数層、理想2k–5k。

---

# 24. Tier A-8 — current data refresh

今のデータソースの中には、2026-08時点で更新可能なものがある。

## Media

総務省は2026-06-26に**令和7年度（2025年度）情報通信メディア利用調査**を公表済み。

全年代平均:

```text
weekday internet: 183.9 min
holiday internet: 192.9 min
```

したがってmedia validationは2024年度版ではなく**2025年度版へ更新可能**。

---

# 25. Time Use

2026年社会生活基本調査は2026-10-17〜10-25に行動調査予定。

つまり8/30提出時点では結果は存在しない。

したがって本選では、

**2021 Survey on Time Use and Leisure Activities**

が正当な最新published baseline。

これは「古いデータを使っている」のではなく、

> 2026 survey結果がまだ存在しない

とData Vintage Ledgerへ明記する。

---

# 26. Household consumption

家計調査は2025年平均が2026-02-06公表済み。

単身世帯では、

- age
- sex
- income
- occupation
- industry
- housing tenure
- commodity purchase frequency

までtableがある。

これはかなり強い。

## nice-to-have

consumption validationを、

```text
overall spend
```

だけでなく、

```text
age × category
single household × category
purchase frequency
```

まで分解。

---

# 27. Health

厚労省の令和6年（2024年）国民健康・栄養調査報告が利用可能。

生活習慣調査を、

```text
sleep
exercise
smoking
alcohol
diet
```

等のvalidation anchorとして使える。

本番前にhealth mechanismを大改修する必要はない。

**結果がどの程度現実範囲にあるかを測るだけでも価値が高い。**

---

# 28. PLATEAU 2025

PLATEAUポータルは渋谷区2025データを掲載。

2026年3月31日時点の標準製品仕様書はV5.1。

## 本選前にやるならviewer側

```text
PLATEAU 2025 3D Tiles
+
simulation overlays
```

engine dynamicsに触れない。

## 本選後

CityGMLから、

```text
building footprint
height
storeys
use
entrance
capacity proxy
```

をParquetへ落としengineへ。

---

# 29. Tier A-9 — time-of-day concurrent population validation

`presence.py`自体が、

```text
shibuya_concurrent_144step_curve.csv
```

を将来拡張としており、v1では直接使わない。

したがって、

**「今日誰が来るか」**
と
**「この時刻に何人いるか」**

は別問題。

## まず解析

```text
sim concurrent population[144]
vs
observed concurrent population[144]
```

について、

```text
MAPE
RMSE
correlation
peak time error
minimum time error
```

を出す。

## 本番前の判断

合っているなら触らない。

大きくズレる場合でも、日内presence engineの全面追加は高リスク。

まずvisitor entry/exit timingのparameter側を確認。

---

# 30. Tier B-1 — parameter uncertainty

今のuncertainty auditは、

```text
randomness / shocks / luck
```

をよく測っている。

しかし、

```text
model parameter uncertainty
```

は別。

例:

```text
relation decay
habit novelty probability
boredom threshold
weather elasticity
social interaction probability
plan interruption
```

の値自体が不確か。

## nice-to-have sensitivity run

25万でやる必要はない。

```text
N=1k–5k
1–3 days
```

で、

重要parameterを±10–20%。

## 出すもの

```text
elasticity:
Δoutput / Δparameter
```

大きく効くparameterだけを明示。

---

# 31. さらに良い方法 — small Latin Hypercube

余裕があれば、

```text
5–10 high-impact parameters
20–50 parameter sets
N=1k
1 day
```

程度。

outputs:

```text
mobility
time-use
social contact
consumption
media
LLM call pattern
```

これだけでも、

> 結果が1つの手調整parameterに依存していない

ことを示せる。

---

# 32. 本格ABCは今はやらない

2025–2026のABM研究では、

- Approximate Bayesian Computation
- history matching
- random-forest surrogate
- ML-assisted ABC

などが大規模ABMのcalibrationに使われている。

これは将来的に非常に価値がある。

ただし現在の250k本線と8/30締切では重すぎる。

今は、

```text
small sensitivity
+
holdout validation
```

でよい。

---

# 33. Tier B-2 — seed2

seed1のみだと、

```text
interesting phenomenon
```

がseed偶然か分からない。

本線10日をもう1本回す必要はない。

推奨:

```text
seed1: 250k × 10d
seed2: reduced duration / smaller N
```

で、

```text
direction
rank order
major distributions
```

が保存されるか見る。

---

# 34. Tier B-3 — paired counterfactual

最もデモ価値が高い。

同一checkpoint:

```text
baseline checkpoint
├─ no intervention
└─ intervention
```

に分ける。

同じagent historyを持つのでvariance reductionが大きい。

## 解析

agent iについて、

```text
Δ outcome_i
=
intervention_i - baseline_i
```

を取る。

例:

```text
travel time
happiness
spending
contacts
route
store visits
```

paired bootstrapでCIを作る。

---

# 35. intervention候補

本プロジェクトのコンセプトに最も合うもの:

## 第一候補

```text
新しい歩行空間 / pedestrian intervention
```

理由:

- 渋谷らしい
- 3D viewerで分かりやすい
- mobility/social/economyに波及
- 「まだない都市を先に実行」と一致

## 第二候補

```text
鉄道障害
```

理由:

- 外生eventが明確
- displacementが見える
- recoveryを見ることができる

---

# 36. Tier B-4 — LLM model sensitivity

同じscenario batteryについて、

```text
8B
14B
32B
```

のaction distribution差を出す。

これは単なるmodel selectionだけでなく、

**model-form uncertainty**

として報告できる。

もしmodelで結論が大きく変わるなら、それ自体が重要な限界。

---

# 37. prompt sensitivity

prompt paraphraseで同じ意味の指示を2–3形作る。

見るもの:

```text
action agreement
distribution JSD
JSON validity
risk preference
sociality
```

差が大きければ、

> 結果がprompt artifact

の可能性。

repoにはすでにprompt paraphrase ablation seamがあるため、利用価値が高い。

---

# 38. persona sensitivity

既存ablation候補:

```text
persona_swap
context_shuffle
context_sever
```

を小規模で使う。

目的:

> Personaやcontextが本当に行動へ効いているか

を見る。

もしpersona_swapしても結果が同じなら、

```text
250k distinct personas
```

の科学的意味が弱い。

---

# 39. Tier B-5 — Behavioral Model Card

最終提出物にかなり効く。

例:

```text
Model: Qwen3-8B-AWQ
Observed tendencies:
- politeness: high
- conflict avoidance: ...
- risk aversion: ...
- negative social acts: ...
- repeat rate: ...
- persona sensitivity: ...
- prompt sensitivity: ...
- JSON failure: ...
```

## なぜ必要か

2025–2026研究では、

- belief-behavior mismatch
- excessive cohesion
- positivity/social desirability bias
- persona prompt aloneではhuman baselineに揃わない

という結果が相次いでいる。

モデルの弱点を隠さず数値化する方が研究として強い。

---

# 40. Tier B-6 — Reality Score v1

単一scoreに潰さない。

minimum:

```text
Population
Mobility
Time Use
Media
Social
Economy
```

各componentで、

```text
target
sim
error
source
year
spatial support
calibration or holdout
```

を出す。

---

# 41. Confidence intervals

Reality Scoreの各指標に、

```text
bootstrap CI
seed range
```

を付けられるとさらに良い。

例:

```text
trip count mean:
sim 3.08 [3.02, 3.14]
observed 3.15
```

「近そう」から「不確実性込みで近い」になる。

---

# 42. Tier B-7 — Data Vintage Ledger

現実データは同一年ではない。

例:

```text
PT: 2018
Time Use: 2021
Health: 2024
Family Expenditure: 2025
Media: 2025
PLATEAU: 2025
```

これは避けられない。

## ファイル

```text
data/ground_truth/registry.yaml
```

例:

```yaml
time_use:
  source: "Survey on Time Use and Leisure Activities"
  year: 2021
  spatial_support: Japan/Tokyo
  role: calibration
  reason_latest: "2026 survey results unavailable before submission"
```

---

# 43. Tier B-8 — Spatial Support Crosswalk

データごとに分母が違う。

```text
Shibuya Ward
simulation bbox
station core
4 mesh area
Tokyo
Japan
```

を同一視しない。

registry:

```text
metric
geometry
source geometry
conversion
population denominator
uncertainty
```

を残す。

---

# 44. Tier B-9 — PLATEAU viewer refresh

2025版を使えるなら、

```text
building LOD2
roads
urban furniture
vegetation
underground mall
```

をviewerへ。

engineを変えず見せ方を強化できるので、deadline前の「入れられたら良い」候補として優秀。

---

# 45. Tier B-10 — system utilization report

A5000×7を使ったこと自体を「GPU7枚使いました」で終わらせない。

提出資料に:

```text
GPU utilization
VRAM use
R_eff
prefix cache hit
LLM requests
tokens
wall time
peak RAM
event count
disk output
```

を載せる。

大規模性の証拠になる。

---

# 46. OS / host側で改善できること

実機:

```text
64 CPUs
2 NUMA
251 GiB RAM
8 GiB swap
ulimit -n = 1024
```

## 46.1 File descriptor

1024は本番長期運用として余裕が小さい。

vLLM7 server + sockets + Parquet + logs + watchdog等を考え、

許可されるならランshellで、

```bash
ulimit -n 65535
```

相当へ上げる。

少なくとも本番前に`lsof -p`等でピークFDを測る。

---

# 47. NUMA

2 NUMA node。

必ず:

```bash
nvidia-smi topo -m
lscpu -e
numactl --hardware
```

を取得。

GPUとCPU/PCIe topologyが偏っているなら、

```text
vLLM process
CPU workers
simulation process
```

のaffinityを検討。

ただしtopology未確認でblind pinningしない。

---

# 48. disk throughput

3.7TB空きは容量として十分。

しかし容量とthroughputは別。

本番前に、

```text
sequential write
checkpoint write
Parquet flush
```

がsim stepを止める時間を測る。

特にcheckpoint:

```text
size
save seconds
peak RSS
```

を計測。

---

# 49. sustained thermal test

A5000×7を数日回す。

短いbenchだけでなく30–60分程度連続推論し、

```text
temperature
power
clock
throttle
VRAM
req/s drift
```

を見る。

最初35 req/sでも1時間後25ならruntime estimateが壊れる。

---

# 50. vLLM metrics collection

各port 8000–8006の`/metrics`を30–60秒間隔で保存。

必要:

```text
num_requests_running
num_requests_waiting
kv_cache_usage_perc
prefix_cache_hits
prefix_cache_queries
prompt_tokens_cached
time_to_first_token
e2e_request_latency
queue_time
preemptions
spec acceptance
```

これをrun artifactに含める。

---

# 51. Tier C — contextual habit learning

価値: 高い。

人間行動の多くはstable contextでの反復から自動化される。

現repoにもroutine stochasticはあるが、経験からhabit strengthを更新する全面設計はまだ弱い。

候補:

```python
habit_key = (
    time_band,
    weekday_type,
    context,
    action,
    destination_class
)

habit.strength
habit.count
habit.reward_ema
last_step
```

## ただし

β凍結直前に入れると、

```text
mobility
time use
LLM fire
plan adherence
```

全部が変わる。

本選後に実装。

---

# 52. Tier C — hunger / sleep pressure

価値: 高い。

食事がscheduleだけで起こるより、

```text
hunger
```

が蓄積し食事を駆動する方が現実的。

sleepも、

```text
sleep_pressure
```

がある方が良い。

## 本選前

HOME_AWAKE最小だけ。

## 本選後

正式なhomeostatic statesへ。

---

# 53. Tier C — microthought C1

価値: 非常に高い。

LLMを0.17–1.4回/日しか呼べないと、

```text
thinking
```

がほぼ存在しないように見える。

C1を、

```text
短いsemantic state
```

として持つ設計は理にかなう。

ただし本選直前に新しい発火schedulerを作るのはリスク。

Shadow runでまず必要性を測る。

---

# 54. Tier C — Context-Value-Action型 architecture

ACL 2026 CVA研究は、

```text
Context
↓
Value activation
↓
Action
```

を明示的に分離し、human dataでvalue verifierを学習。

現在repoにはvalues/needs/driveが既にあるので、思想的には近い。

将来:

```text
current context
→ active values
→ restricted actions
→ LLM choice
```

へ整理する価値がある。

## 今やらない理由

Value Verifierを人間dataで学習しないまま形だけ真似ると、論文の強みを再現できない。

---

# 55. Tier C — human behavior fine-tuning

ACL 2026購買行動研究では、prompt-onlyよりhuman behavior tracesでfine-tuneしたモデルが改善した。

将来は、

```text
Japanese mobility/time-use/action traces
```

から小型behavior policyを学習する余地がある。

ただし現在の公式統計はaggregate表が多く、個票利用条件もある。

8/30前に無理に行わない。

---

# 56. Tier C — social attention budget

現在relationは多機能だが、人間が維持できる関係数は有限。

将来:

```text
social attention/day
```

を、

```text
family
close friends
friends
coworkers
acquaintances
```

へ配分。

これによりtie decayが「固定減衰」から、

> 注意を割けなかったので疎遠になった

へ変わる。

---

# 57. Tier C — group interaction / hyperedges

社会相互作用をpairだけでなく、

```text
meeting
family dinner
friend group
class
party
```

のInteractionEpisodeとして持つ。

network emergenceには価値が高い。

しかしlogging/stateが増えるため本選後。

---

# 58. Tier C — workplace substates

現実の勤務8時間は単一actionではない。

将来:

```text
focused work
meeting
break
customer
idle
coworker chat
```

へ。

特にsocial contact validationが改善する。

---

# 59. Tier C — information processing pipeline

理想:

```text
exposure
↓
attention
↓
comprehension
↓
credibility
↓
memory
↓
belief
↓
share
```

現在もbelief/info機構は強いが、各stageの独立validationを持てるとさらに良い。

---

# 60. Tier C — restricted choice set

agentが全POIを知っているようなglobal choiceは人間らしくない。

将来:

```text
known places
habit places
nearby perception
friends recommendation
search/media
```

だけからcandidate setを作る。

mobility fidelityに大きく効く可能性。

---

# 61. Tier C — online data assimilation

Digital Twinとして将来非常に価値がある。

例:

```text
毎日実人流観測
↓
latent world state correction
↓
翌日sim
```

ただしcounterfactual purityと再現性を壊しやすい。

baseline assimilationとcounterfactual forecastを明確に分ける必要がある。

今大会ではやらない。

---

# 62. Tier C — surrogate / distillation

高認知Shadowから、

```text
state -> action distribution
```

を小型modelへdistill。

25万人へ高LLM policyを近似展開できる可能性。

ただしこれは、

**human behavior ground truthではなくLLM policyのdistillation**

であることを明記する。

---

# 63. Tier C — full Bayesian calibration

将来:

```text
History Matching
ABC
ABC-SMC
Random Forest surrogate
GP emulator
```

が候補。

2026年にもHPC-ABC-SMCやML-assisted ABCで大規模ABM calibrationを効率化する研究が出ている。

本シムにも相性は良い。

しかし今大会では、

```text
small sensitivity
+
holdout
+
seed
```

で十分。

---

# 64. global dt=1 minは依然非推奨

人間の思考が10分単位ではないという問題は正しい。

しかし解決方法は、

```text
global 1min tick
```

ではなく、

```text
macro world 10min
event-driven cognition
local physical substeps
```

。

既存実測でもdt=5はengine wallを増やす。

25万人の全員scan回数を増やすのは現在のリソースの使い方として悪い。

---

# 65. 今の7GPUを最大限価値へ変える構成

本番候補を3つ用意してbenchmark。

## S0 — Throughput baseline

```text
7 × Qwen3-8B-AWQ
```

長所:

```text
最大throughput
単純
sticky routing
```

---

## S1 — Quality-balanced

```text
6 × Qwen3-8B-AWQ
1 × Qwen3-14B-AWQ
```

purpose:

```text
reflect/deep -> 14B
others -> 8B
```

**現時点の最有力nice-to-have。**

14B weightsは約9.99GBなのでA5000 1枚で十分なKV余地を持てる可能性が高い。

---

## S2 — Deep-cognition experiment

```text
5 × Qwen3-8B-AWQ
2 GPUs × Qwen3-32B-AWQ TP2
```

purpose:

```text
rare C3 only -> 32B
```

32Bの品質差が明確なときだけ。

---

# 66. Model Tournamentの採用基準

例:

```text
behavior score    40%
schema validity   15%
persona sensitivity 10%
diversity         10%
req/s             15%
P95 latency        5%
VRAM robustness    5%
```

「大きいから採用」は禁止。

---

# 67. reasoning policy

推奨:

```text
plan      no-think
reply     no-think
face      no-think
media     no-think
reflect   no-think or short-think A/B
C3        think
```

理由:

- throughput
- human behavior fidelityはreasoning量に単調増加しない
- population diversity collapseの可能性
- Qwen3はthinking/non-thinkingを切替可能

---

# 68. Qwen3 think制御のrepo注意

現`VllmBackend`はcompletions endpointを優先。

コードコメント自身が、

```text
think=trueの完全強制はchat経路のみ
```

と認識している。

現在finalsは`reflect_think=false`なので致命的ではない。

将来C3でthinkを本当に使うなら、

```text
chat endpoint強制
```

または専用backendを使う。

---

# 69. nice-to-have判定マトリクス

| 改善 | 科学価値 | Demo価値 | 実装リスク | Compute | 今やる? |
|---|---:|---:|---:|---:|---|
| cap再導出 | 5 | 5 | 1 | 3 | **必須** |
| LLM coverage | 5 | 4 | 1 | 1 | **必須** |
| model freeze | 5 | 3 | 1 | 0 | **必須** |
| request seed | 4 | 2 | 2 | 0 | **強く推奨** |
| HOME_AWAKE | 5 | 5 | 3 | 1 | **推奨** |
| checkpoint stream | 5 | 2 | 2 | 0 | **必須** |
| batch_llm | 4 | 3 | 2 | - | **推奨** |
| 8B/14B tournament | 5 | 4 | 1 | 2 | **推奨** |
| 32B tournament | 3 | 4 | 1 | 2 | 余力 |
| multi-model LOD | 4 | 5 | 2 | 2 | **推奨候補** |
| JSON Schema | 3 | 2 | 2 | 0 | A/B後 |
| shadow run | 5 | 4 | 1 | 2 | **強く推奨** |
| parameter sensitivity | 5 | 3 | 1 | 2 | 尾部 |
| seed2 | 5 | 3 | 1 | 2 | **尾部必須級** |
| paired fork | 5 | 5 | 1 | 2 | **強く推奨** |
| PLATEAU viewer 2025 | 2 | 5 | 1 | 0 | 余力 |
| habit learning | 5 | 3 | 5 | 2 | 本選後 |
| hunger | 4 | 2 | 4 | 1 | 本選後 |
| microthought | 5 | 4 | 5 | 3 | 本選後 |
| CVA verifier | 5 | 3 | 5 | 3 | 本選後 |
| ABC calibration | 5 | 2 | 5 | 5 | 本選後 |

---

# 70. 8/16–8/22 推奨実行順

## 8/16

```text
vLLM install/freeze
8B-AWQ起動
7GPU metrics取得
2k benchmark
10k×144
RSS/IO/checkpoint
batch_llm A/B
cap sweep preliminary
```

## 8/17

```text
50k×1day
cap 1500/2000/2500 short comparison
coverage/fairness
HOME_AWAKE validation
v2
fire
POP
```

## 8/18

```text
100k×1day
model tournament
sampling/revision freeze
β freeze
Codex review #1
```

## 8/19

```text
review fixes only
250k rehearsal
```

## 8/20

```text
Codex #2
Reality Score
world invariants
reliability rehearsal
```

## 8/21

```text
final config
U-10
manifest
no new dynamics
```

## 8/22

```text
250k × 10d start
```

---

# 71. 本番中に並行できること

engineを触らない作業:

```text
Reality Score
Human Behavior Score
Data Vintage Ledger
Spatial Crosswalk
viewer
Behavior Model Card
intervention scenario design
analysis scripts
presentation
```

これらはmain runを止めない。

---

# 72. 完走後のGPU尾部

優先:

```text
1. seed2
2. intervention fork
3. shadow high-cognition
4. model sensitivity
5. parameter mini sensitivity
```

PLATEAU viewerはGPUをほぼ必要としないので別レーン。

---

# 73. 最終提出で示すべき5枚の証拠

## Evidence 1 — Scale

```text
250,000 agents
10 days
events
LLM calls
GPU7
wall time
```

## Evidence 2 — Reality

```text
population
mobility
time use
media
social
economy
```

## Evidence 3 — Cognition

```text
LLM calls/person
coverage
model
fallback
shadow agreement
```

## Evidence 4 — Robustness

```text
seed
prompt
model
parameter
invariants
```

## Evidence 5 — Counterfactual

```text
same checkpoint
different intervention
paired difference
```

---

# 74. 「入れられたら良い」ものの最終選別

現時点で、実際に**大会前に追加してよいnice-to-have**は以下まで。

```text
A. 14B purpose tier
B. JSON Schema outputs
C. request stable seed
D. shadow run
E. latest official validation data
F. time-of-day population validation
G. parameter mini sensitivity
H. model/prompt sensitivity
I. paired intervention fork
J. PLATEAU 2025 viewer
```

これより大きいbehavior engine変更は、本番前ではROIが逆転する。

---

# 75. なぜこの線なのか

2025–2026のgenerative social simulation文献で繰り返し指摘される問題は、

```text
"looks human"
```

ことではなく、

```text
validation
behavioral fidelity
reproducibility
calibration
environment coupling
```

である。

Artificial Intelligence Review 2026のsystematic reviewも、generative ABM研究では主観的なface validityが依然多く、**目的に直接対応するempirical validationが不足している**と指摘している。

したがって、このプロジェクトが他のLLM agent demoより強くなる場所は、

> agentが喋ること

ではなく、

> **25万人が動く都市を現実データ・再現性・実験設計まで含めて検証していること**

である。

---

# 76. 最終設計の完成条件 — 更新版

```text
□ model repo/revision固定
□ sampling policy固定
□ request seed固定または理由明記
□ resolved final config 1枚
□ mock production fail-fast
□ 10k×144 RSS実測
□ checkpoint peak安全
□ batch_llm実測
□ cap実測決定
□ used/cap測定
□ calls/person fairness測定
□ HOME_AWAKE
□ v2 switch検収
□ time-of-day population検証
□ Reality Score
□ Human Behavior Score
□ LLM Behavioral Battery
□ world invariants
□ seed2設計
□ parameter sensitivity最小版
□ model/prompt sensitivity
□ paired counterfactual
□ provenance manifest
□ Data Vintage Ledger
□ Spatial Crosswalk
□ no O(N²) hot path at 250k
□ Codex 2-pass review
□ 250k rehearsal
```

ここまで閉じれば、

**設計の追加より実行・解析へ移るべき状態**

と言える。

---

# 77. 現時点の推奨final architecture

```text
REAL WORLD DATA
    │
    ├── PLATEAU / OSM / GTFS / organizations
    ├── population / PT / time use
    ├── media / health / expenditure
    │
    ▼
WORLD + POPULATION
    │
    ▼
250k AGENTS
    │
    ├── body / affect / needs
    ├── role / household / money
    ├── memory / beliefs / relations
    ├── routine / plan / habit
    │
    ▼
COGNITION LOD
    │
    ├── automatic rules
    ├── sparse LLM
    ├── purpose model routing
    └── deep tier if validated
    │
    ▼
ACTION + INTERACTION
    │
    ▼
WORLD FEEDBACK
    │
    ▼
OBSERVATION / PROVENANCE
    │
    ├── Reality Score
    ├── Behavioral Score
    ├── LLM coverage
    ├── invariants
    └── uncertainty
    │
    ▼
VALIDATED CHECKPOINT
    │
    ├── baseline
    └── counterfactual fork
```

---

# 78. 一行結論

> **現在のリソースで最大の改善は、機能をさらに増やすことではない。LLMを適切な密度・適切なモデルで全人口へ配り、現実データで検証し、seed/model/prompt/parameter不確実性を測り、同一checkpointから反実仮想を実行できる状態まで閉じることである。**

---

# 79. Sources / Research Basis

## Repository / internal design basis

- `conf/finals_observe.yaml`
- `src/society/cognition/lod.py`
- `src/society/llm/vllm.py`
- `src/society/llm/fleet.py`
- `src/society/llm/router.py`
- `src/society/llm/cache.py`
- `src/society/world/presence.py`
- `src/society/engine/checkpoint.py`
- `docs/plans/external-audit-triage.md`
- `docs/plans/finals-endgame-plan.md`
- `docs/plans/multi-model-lod.md`
- `docs/research/uncertainty-audit.md`

Repository inspected at:
`12970725818aa34d0e6eb7bd4e5ba1d2f7562dd0`

## Generative social simulation / validation

1. Larooij, M. & Törnberg, P. (2025/2026).  
   **Validation is the central challenge for generative social simulation: a critical review of LLMs in agent-based modeling.**  
   Artificial Intelligence Review.  
   DOI: https://doi.org/10.1007/s10462-025-11412-6

2. Lu, Y. et al. (2026).  
   **Can LLM Agents Simulate Multi-Turn Human Behavior? Evidence from Real Online Customer Behavior Data.**  
   ACL 2026.  
   DOI: https://doi.org/10.18653/v1/2026.acl-long.2034

3. Wang, Z. et al. (2026).  
   **OPeRA: A Dataset of Observation, Persona, Rationale, and Action for Evaluating LLMs on Human Online Shopping Behavior Simulation.**  
   ACL 2026.  
   DOI: https://doi.org/10.18653/v1/2026.acl-long.2033

4. Zhang, T. et al. (2026).  
   **Context-Value-Action Architecture for Value-Driven Large Language Model Agents.**  
   Findings ACL 2026.  
   DOI: https://doi.org/10.18653/v1/2026.findings-acl.248

5. Park, J. S. et al. (2024).  
   **Generative Agent Simulations of 1,000 People.**  
   https://arxiv.org/abs/2411.10109

6. Piao, J. et al. (2025).  
   **AgentSociety: Large-Scale Simulation of LLM-Driven Generative Agents Advances Understanding of Human Behaviors and Society.**  
   https://arxiv.org/abs/2502.08691

7. Taillandier, P. et al. (2025).  
   **Integrating LLM in Agent-Based Social Simulation: Opportunities and Challenges.**  
   https://arxiv.org/abs/2507.19364

## vLLM

8. vLLM — SamplingParams (`seed`)  
   https://docs.vllm.ai/en/latest/api/vllm/sampling_params/

9. vLLM — Engine Arguments (`--generation-config`)  
   https://docs.vllm.ai/en/latest/configuration/engine_args/

10. vLLM — Production Metrics  
    https://docs.vllm.ai/en/latest/usage/metrics/

11. vLLM — Data Parallel Deployment  
    https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/

12. vLLM — Speculative Decoding  
    https://docs.vllm.ai/en/latest/features/speculative_decoding/

13. vLLM — Structured Outputs  
    https://docs.vllm.ai/en/latest/api/vllm/config/structured_outputs/

## Qwen model artifacts

14. Qwen3-8B-AWQ  
    https://huggingface.co/Qwen/Qwen3-8B-AWQ

15. Qwen3-14B-AWQ  
    https://huggingface.co/Qwen/Qwen3-14B-AWQ

16. Qwen3-32B-AWQ  
    https://huggingface.co/Qwen/Qwen3-32B-AWQ

## Japanese empirical ground truth

17. 総務省統計局 — 2021 社会生活基本調査  
    https://www.stat.go.jp/data/shakai/2021/

18. 総務省統計局 — 2026 社会生活基本調査概要  
    https://www.stat.go.jp/data/shakai/2026/gaiyou.html

19. 東京都市圏交通計画協議会 — 第6回東京都市圏パーソントリップ調査  
    https://www.tokyo-pt.jp/person/04_01

20. 総務省情報通信政策研究所 — 情報通信メディアの利用時間と情報行動に関する調査  
    https://www.soumu.go.jp/iicp/research/results/media_usage-time.html

21. 総務省統計局 — 家計調査 2025年平均  
    https://www.stat.go.jp/data/kakei/

22. 厚生労働省 — 令和6年国民健康・栄養調査  
    https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/kenkou/eiyou/r6-houkoku_00001.html

23. Project PLATEAU / G空間情報センター  
    https://front.geospatial.jp/plateau_portal_site/

24. PLATEAU API — CityGML stable latest endpoint  
    https://docs.plateauview.mlit.go.jp/api/rest/operations/datacatalogcitygmlspeccitygmlzip/

## ABM calibration / uncertainty

25. ML-ABC (2026), Epidemics 54, 100881.  
    https://doi.org/10.1016/j.epidem.2025.100881

26. Robertson et al. (2025).  
    **Bayesian Calibration of Stochastic Agent Based Model via Random Forest.**  
    Statistics in Medicine.  
    https://doi.org/10.1002/sim.70029

27. Li et al. (2026).  
    **Calibrating a Global Trade Agent-Based Model with an HPC–ABC–SMC Framework.**  
    JASSS 29(3)5.  
    https://doi.org/10.18564/jasss.6072

---

# 80. Supersession note

本書は以下の過去文書を削除するものではない。

- `SHIBUYA_SIMULATION_REALITY_MAXIMIZATION_PLAN.md`
- `SHIBUYA_SIMULATION_HUMAN_BEHAVIOR_DEEP_AUDIT.md`
- `SHIBUYA_SIMULATION_SERVER_CAPACITY_AND_RUNTIME_ESTIMATE.md`
- `SHIBUYA_SIMULATION_FINAL_DESIGN_GAPS_AND_COMPLETION_CRITERIA.md`

ただし、以下は本書を最新正とする。

1. **現行finalsのLLM密度 = 約0.173 call/person/day**
2. **本番cap候補 = 1,500–2,500/stepを実機測定で選定**
3. **4.5–5.5 call/person/dayを本線前提にはしない**
4. **more LLM reasoning = more human fidelityとは仮定しない**
5. **nice-to-haveの優先はmodel/validation/uncertainty/counterfactual**
6. **大規模behavior mechanism追加はβ凍結後にしない**
