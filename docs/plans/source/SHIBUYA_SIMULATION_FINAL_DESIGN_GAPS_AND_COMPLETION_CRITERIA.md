# Shibuya Simulation — Final Design Gaps & Completion Criteria

> 作成日: 2026-08-16  
> 対象: 渋谷25万人LLM社会シミュレーション  
> 目的: 現在の設計が「十分か」を判定し、残っている設計上の穴と、  
> **何を満たせば“設計完了”と呼べるか**を明文化する。

---

# 0. 結論

現状の設計はかなり進んでいるが、まだ「十分」とは言い切れない。

現在までに主に以下の3領域はかなり整理されている。

1. 世界・環境・現実再現の設計
2. 人間行動・認知の高解像度化
3. サーバー資源・実行可能日数

一方で不足しているのは、

**各設計要素を1つの因果システムとして統合する最終仕様**

である。

現在は、

```text
部品設計
↓
かなり揃っている
```

状態。

しかし最終的に必要なのは、

```text
部品
↓
責任分界
↓
更新順序
↓
因果接続
↓
観測
↓
較正
↓
検証
↓
本番条件
↓
主張可能範囲
```

までを一本の正典として固定すること。

---

# 1. 現在ある設計文書の役割

既存文書は大きく以下の役割を持つ。

## 1.1 Reality / Environment

```text
SHIBUYA_SIMULATION_REALITY_MAXIMIZATION_PLAN.md
```

主に扱うもの:

- 都市空間
- PLATEAU
- 人口
- 移動
- 組織
- 観測
- Reality Score
- 実験
- 大規模実行
- 本番日程

---

## 1.2 Human Behavior

```text
SHIBUYA_SIMULATION_HUMAN_BEHAVIOR_DEEP_AUDIT.md
```

主に扱うもの:

- 習慣
- needs
- emotion
- physiology
- home life
- memory
- cognition
- social interaction
- media
- relationship
- human behavior validation

---

## 1.3 Runtime / Hardware

```text
SHIBUYA_SIMULATION_SERVER_CAPACITY_AND_RUNTIME_ESTIMATE.md
```

主に扱うもの:

- CPU
- RAM
- VRAM
- A5000 × 7
- LLM throughput
- wall-clock estimate
- Adaptive LLM Budget
- 25万人×10日
- 本番ラン長
- RAM / R_eff判定

---

# 2. それでも残っている最大の問題

現在不足しているのは、

> **「全部をどう接続するのか」**

である。

例えば、

```text
fatigue
sleep_pressure
arousal
needs
emotion
habit
goal
memory
social pressure
money
weather
plan
```

が同時に行動へ影響する。

しかし、

- 誰がどの状態を書くのか
- 何stepごとに更新するのか
- 更新順序は何か
- どの状態が優先されるのか
- 同じ原因を二重計上していないか
- 行動へ何%効くのか
- checkpointに保存されるか
- 不在時に変化するか
- どのログで観測するか

が最終的に一本化されていないと、

**複雑だが因果的には曖昧なシミュレーション**

になる。

---

# 3. 不足1 — Agent State Contract

最重要。

人間1人の状態を完全に定義する。

例:

```text
Agent
├─ demographics
├─ life_stage
├─ household
├─ occupation
├─ money
├─ health
├─ physiology
│  ├─ hunger
│  ├─ fatigue
│  └─ sleep_pressure
├─ affect
│  ├─ valence
│  └─ arousal
├─ needs
│  ├─ stimulation
│  ├─ security
│  ├─ relatedness
│  ├─ competence
│  └─ autonomy
├─ goals
├─ plans
├─ habits
├─ beliefs
├─ memory
├─ relations
├─ media_state
└─ current_action
```

各stateについて最低限以下を固定する。

| Field | 意味 |
|---|---|
| owner | 誰が持つか |
| writer | どのmoduleが書くか |
| reader | どのmoduleが読むか |
| update timing | いつ更新するか |
| persistence | checkpoint / rotationで残るか |
| unit | 単位 |
| range | 値域 |
| decay | 減衰 |
| behavior effect | 行動へどう影響するか |
| logging | 何を記録するか |
| validation | どう検証するか |

---

# 4. State Causality Audit

推奨ツール:

```text
scripts/audit_state_causality.py
```

出力例:

```text
state: fatigue

writers:
  health.py
  sleep.py

readers:
  planning.py
  routine.py
  cognition/fire.py

behavior effects:
  work interruption
  sleep hazard
  leisure reduction
  cognition threshold

persistent:
  yes

checkpoint:
  yes

logged:
  yes

ground_truth:
  sleep/time-use statistics
```

重要state全てに対してこの表を生成する。

---

# 5. 二重計上の防止

特に注意する状態:

```text
fatigue
sleep_pressure
arousal
stress
security need
threat drive
negative emotion
```

例えば、

```text
睡眠不足
↓
fatigue +0.4
↓
arousal +0.2
↓
security need -0.1
↓
stress +0.3
↓
全てが外出確率を下げる
```

となると、

**同じ原因を4回行動へ反映**

する可能性がある。

したがって、

```text
cause
→ latent state
→ behavior
```

の経路を明示する。

---

# 6. 不足2 — Simulation Causal Loop

1 step内の更新順序を正典化する。

推奨例:

```text
00 Clock
01 Exogenous world
02 Infrastructure
03 Physiology
04 Schedule / obligations
05 Perception
06 Information exposure
07 Social perception
08 Affect / salience
09 Needs / conflict
10 Cognition trigger
11 LLM budget allocation
12 Deliberation
13 Action selection
14 Movement
15 Physical interaction
16 Social interaction
17 Economy
18 Information propagation
19 Relationship update
20 Memory encoding
21 Habit learning
22 World feedback
23 Observer / provenance
24 Checkpoint
```

---

# 7. なぜphase順が重要か

例えば、

```text
conversation
→ emotion update
```

なのか、

```text
emotion
→ conversation decision
```

なのかで因果が変わる。

同じstepで両方起こる場合、

```text
old_state
new_state
```

を分離する。

可能なら、

```text
double buffer
```

または、

```text
event queue
```

を使用し、

module実行順の偶然で結果が決まらないようにする。

---

# 8. Event Provenance

主要な行動には、

```text
action_id
agent_id
step
cause_type
cause_event_id
decision_mode
perception_snapshot_id
memory_ids
goal_id
plan_id
llm_call_id
```

を持たせる。

これにより、

> なぜこの人はこの行動をしたのか

を後から追える。

---

# 9. 不足3 — Calibration / Validation Separation

現実データを使うだけでは不十分。

必要なのは、

```text
Calibration data
≠
Validation data
```

である。

---

# 10. Validation Registry

例:

| Layer | Ground Truth | Calibration | Holdout Validation |
|---|---|---|---|
| Population | Census | age/job | another census slice |
| Mobility | Person Trip | EPR parameters | trip distributions |
| Time Use | Time Use Survey | activity timing | home/work/leisure |
| Media | media survey | session rates | age×time-use |
| Consumption | household survey | spending propensity | category shares |
| Social | contact/network studies | tie rates | degree/clustering |
| Sleep | health/time-use survey | sleep timing | age distribution |

---

# 11. Validation Metrics

最低限:

```text
MAE
RMSE
MAPE
Jensen-Shannon Divergence
Wasserstein Distance
KS statistic
correlation
```

ただし単一Reality Scoreだけに隠さない。

必ず、

```text
Population score
Mobility score
Time-use score
Social score
Economy score
Cognition score
```

を別表示する。

---

# 12. Calibration Leakageの防止

悪い例:

```text
実測の外出回数 = 3.2
↓
シムも強制的に3.2回にする
```

良い例:

```text
habit
travel cost
weather sensitivity
schedule
social invitation
↓
パラメータ較正
↓
結果として外出回数分布が近づく
```

つまり、

**output countを直接駆動しない。**

---

# 13. Holdout Validation

較正に使っていない条件を残す。

例:

```text
weekdayで較正
↓
weekendで検証
```

または、

```text
summer weekdays calibration
↓
rain day validation
```

など。

---

# 14. 不足4 — LLM Role Contract

LLMの役割を明確に固定する。

推奨定義:

> LLMは「人間そのもの」ではなく、  
> **bounded semantic decision engine**である。

---

# 15. Multi-Level Cognition

```text
C0 Automatic
C1 Microthought
C2 Deliberation
C3 Deep cognition
```

---

## C0 — Automatic

例:

- habitual commute
- routine meal
- route following
- automatic reply
- familiar purchase

LLMなし。

---

## C1 — Microthought

例:

```text
「混んでるな」
「少し疲れた」
「あとで寄ろう」
```

短いsemantic cognition。

必要なら16〜64 tokens程度。

---

## C2 — Deliberation

例:

- 行き先を変える
- 会話内容
- 予定変更
- 迷い
- SNS投稿
- 大きめの購入

---

## C3 — Deep Cognition

例:

- 転職
- 引越し
- パートナーシップ
- 強い葛藤
- 重大な事件
- 世界観修正

長いLLM reasoningを許可。

---

# 16. 各Cognition Levelの必須仕様

各levelに対し、

```text
trigger
token limit
input state
memory access
allowed actions
cooldown
budget priority
fairness
fallback
logging
```

を固定する。

---

# 17. 「LLMを呼ばない」と「考えていない」を区別する

重要。

```text
LLM call = 0
```

は、

```text
cognition = 0
```

ではない。

LLMが呼ばれなくても、

```text
habit
heuristics
microthought surrogate
emotion
needs
goal conflict
```

は動いているべき。

---

# 18. Cognition Debt

LLM予算が不足したagentが永遠に無視されないよう、

```text
cognition_debt
```

を導入する。

例:

```text
priority =
salience
+ urgency
+ social_pressure
+ cognition_debt
```

---

# 19. Adaptive LLM Budget

budgetは固定値だけでなく、

```text
remaining wall time
remaining steps
R_eff
queue depth
GPU utilization
I/O reserve
```

から適応させる。

---

# 20. 不足5 — What Does This Simulation Prove?

最終的な主張を限定する。

---

# 21. Claim 1 — Baseline Fidelity

主張:

> 渋谷の人口・移動・時間利用・社会接触・消費などを  
> 複数の現実データに対して同時に再現する。

---

# 22. Claim 2 — Emergent Dynamics

主張:

> 個々のルールとして直接指定していないマクロ構造が  
> agent間相互作用から生成される。

例:

```text
crowding
communities
rumor diffusion
social polarization
store concentration
habit clustering
```

---

# 23. Claim 3 — Counterfactual Capability

主張:

> 検証済みbaseline checkpointをforkし、  
> 未実施の都市介入を仮想的に実行して差分を観測できる。

---

# 24. Non-Claim

主張しないもの:

```text
25万人それぞれの未来を正確に予測できる
```

これは現段階では言わない。

---

# 25. 推奨する第4正典

新しく、

```text
SHIBUYA_SIMULATION_FINAL_DESIGN_SPEC.md
```

を作る。

役割:

> Claude / Codex / 人間が  
> 「ここから逸脱してはいけない」と参照する最終仕様。

---

# 26. Final Design Specの推奨章構成

```text
0. System objective / claims / non-claims

1. World ontology

2. Agent state contract

3. Simulation causal loop

4. Time model

5. Human behavior model

6. Cognition architecture

7. Social architecture

8. Spatial architecture

9. Economy / institutions

10. Population / presence lifecycle

11. Calibration registry

12. Validation protocol

13. Counterfactual experiment protocol

14. Logging / provenance

15. Performance / scaling contract

16. Determinism / checkpoint / resume

17. Failure modes / invariants

18. Final 250k configuration

19. Acceptance gates

20. Submission claims
```

---

# 27. World Ontology

最低限:

```text
Person
Household
Organization
Place
Building
Transport
Vehicle
Information
Money
Relationship
Event
Institution
```

各entityに、

```text
ID
lifecycle
owner
state
event interface
persistence
```

を定義する。

---

# 28. Human Behavior Pipeline

正典として以下を固定する。

```text
Demographics / life history
↓
Traits / values / roles
↓
Needs / body
↓
Goals / obligations
↓
Habits
↓
Plan
↓
Perception
↓
Attention / salience
↓
Emotion / need conflict
↓
Cognition trigger
↓
Choice
↓
Action
↓
Social/world response
↓
Memory
↓
Habit/value/relation update
```

---

# 29. Social Architecture

最低限:

```text
co-presence
≠
interaction
```

を守る。

必要な段階:

```text
co-presence
↓
perception
↓
attention
↓
interaction opportunity
↓
interaction choice
↓
conversation
↓
relationship update
```

---

# 30. Social Attention Budget

人間は無限に関係を維持できない。

agentごとに、

```text
social_attention_budget
```

を持たせる。

それを、

- family
- close friends
- friends
- colleagues
- acquaintances

へ配分。

---

# 31. Endogenous Tie Formation

関係形成は、

```text
repeated co-presence
shared organization
mutual friends
shared interest
conversation valence
age similarity
spatial proximity
```

などから発生させる。

triadic closureも考慮。

---

# 32. Household

householdを単なるID共有にしない。

最低限:

```text
shared schedule
shared dinner
chores
childcare
joint spending
family interaction
conflict
support
```

を持つ。

---

# 33. Home-Awake

```text
home
≠
sleep
```

を絶対条件にする。

帰宅後:

```text
dinner
media
bath
chores
family
hobby
study
relaxation
SNS
```

を発生させる。

---

# 34. Physiology

P0:

```text
hunger
fatigue
sleep_pressure
```

長期的には:

```text
stress
illness
intoxication
pain
```

なども候補。

---

# 35. Mobility

検証指標:

```text
radius of gyration
unique places
familiar place capacity
rank-frequency
return/explore
trip distance
trip duration
dwell time
trip chains
mode share
mobility entropy
```

---

# 36. Restricted Choice Set

agentが世界中のPOIを知っている状態を避ける。

行動候補は、

```text
known places
nearby places
recommendations
social information
search result
```

から構成。

---

# 37. Media Model

単純な「internet use」ではなく、

```text
phone check
messaging
social feed
video
news
game
search
```

などsession単位で扱う。

---

# 38. Information Pipeline

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

に分ける。

---

# 39. Economy

最低限:

```text
income
spending
rent
organization accounting
store inventory
purchase
financial pressure
```

を因果接続する。

---

# 40. Health Feedback Loop

```text
health
↓
mobility
↓
work
↓
income
↓
social activity
↓
mood
↓
health
```

のループを持たせる。

---

# 41. Population Lifecycle

```text
birth
immigration
emigration
employment change
household change
partnership
relocation
```

などをeventとして扱う。

---

# 42. Presence

```text
population
≠
present population
```

を分離する。

在場は、

```text
resident
worker
student
visitor
duty
tourist
```

などの生活理由から決める。

---

# 43. Time Architecture

推奨:

```text
Macro world:
10 min

Cognition:
event-driven

Physical microzones:
substep
```

global dtを無理に1分へ下げない。

---

# 44. Performance Contract

25万人本番では、

```text
O(N²)
```

を禁止。

許容:

```text
O(N)
O(N log N)
localized O(k²)
```

程度。

---

# 45. Determinism Contract

重要イベントは、

```text
rng_key
agent_id
event_id
step
seed
```

から再現可能にする。

LLMも可能ならstable seedを渡す。

---

# 46. Checkpoint Contract

checkpointには、

```text
agent states
world states
relations
memory
habits
plans
population state
random state
budget state
policy cache
observer watermark
```

など必要stateを保存。

---

# 47. Resume Contract

条件:

```text
straight run
==
checkpoint + resume
```

可能な範囲でstate hashや主要統計が一致。

少なくとも、

```text
resumeでLLM呼数や行動が意味なく変わらない
```

こと。

---

# 48. Failure Invariants

例:

```text
money < impossible lower bound
agent in two places
sleeping while commuting
dead/emigrated agent acting
relationship with nonexistent agent
negative inventory
unknown building reference
time going backward
orphan household
```

を検出。

推奨:

```text
scripts/audit_world_invariants.py
```

---

# 49. Reality Validation

推奨:

```text
scripts/reality_score.py
```

ただし単一scoreだけでなく、

```text
Population
Mobility
Time Use
Spatial
Social
Economy
Human Behavior
```

のcomponent scoreを必ず表示。

---

# 50. Behavioral Validation

別途、

```text
Human Behavior Validation
```

を用意。

例えば:

```text
daily activity timing
home time
sleep timing
media minutes
social contacts
work duration
shopping frequency
trip count
habit persistence
```

を現実と比較する。

---

# 51. LLM Behavioral Battery

モデル自体のhuman-likenessを検証する。

見るもの:

```text
too cooperative
too polite
too rational
too risk-averse
too verbose
too consistent
too knowledgeable
too moral
stereotype bias
refusal bias
repetition
```

---

# 52. Shadow Simulation

25万人mainとは別に、

```text
5k〜20k agents
```

程度のhigh-LLM shadowを走らせる。

比較:

```text
main adaptive LOD
vs
dense cognition
```

見るもの:

```text
action agreement
distribution agreement
social behavior
mobility
decision quality
```

これで、

> LLM密度をどこまで下げても挙動が変わらないか

を実測できる。

---

# 53. Counterfactual Protocol

baseline:

```text
validated checkpoint
```

からfork。

例:

```text
baseline
├─ intervention A
├─ intervention B
└─ intervention C
```

seed、initial state、historyを共有する。

---

# 54. Counterfactualの強み

差分が、

```text
different initial conditions
```

ではなく、

```text
intervention
```

に由来すると説明しやすい。

---

# 55. Emergenceの検証

「何か面白いことが起きた」だけでは弱い。

必要:

```text
baseline
ablation
multiple seeds
null model
```

比較。

例:

```text
social propagation ON
vs
OFF
```

など。

---

# 56. Ablation

最低限候補:

```text
LLM off
relations off
memory off
habit off
social propagation off
persona shuffle
context shuffle
```

---

# 57. Emergence Artifactの排除

見るべきもの:

```text
scheduler artifact
random seed artifact
cap artifact
LLM prompt artifact
population rotation artifact
logging artifact
```

---

# 58. Submission Claims

最終発表では、

```text
Real City
↓
Realistic Humans
↓
Interaction
↓
Emergence
↓
Validation
↓
Counterfactual
```

の順に説明する。

---

# 59. 推奨プロダクト表現

> 実在渋谷の空間・人口・移動・生活時間・組織等に接地し、  
> 各層を現実データで検証した25万人の生成型社会デジタルツイン。  
> 検証済みbaselineをforkして、未実施の都市介入を先に実行する。

---

# 60. 強い一文

> **予測値を1個返すのではなく、別の都市を先に実行して観察する。**

---

# 61. 「設計完了」の条件

以下を全て満たしたら、

**simulation design complete**

と判断する。

```text
□ 重要stateのwriter / readerが決まっている

□ update timingが決まっている

□ 1 stepの因果順序が固定されている

□ LLM発火理由が全経路で定義されている

□ C0〜C3の責任分界がある

□ 非LLM行動との責任分界がある

□ 各realism機能にground truthがある

□ calibrationとvalidationが分離されている

□ baseline合格基準が数値である

□ holdout validationがある

□ seed差の扱いが決まっている

□ counterfactual protocolが固定されている

□ impossible state invariantsがある

□ 250kでO(N²)が残っていない

□ checkpoint/resumeの意味論が固定されている

□ final configが1つに完全解決する

□ Mockへのsilent fallbackがない

□ LLM model/version/seedがmanifestに残る

□ 全重要行動にprovenanceがある

□ 本番前scale rehearsalを通る

□ 発表で言ってよいclaimが固定されている

□ 言ってはいけないnon-claimが固定されている
```

---

# 62. 現時点の状態

現在は、

```text
アイデア不足
```

ではない。

むしろ、

```text
実装候補が多い
```

状態。

したがって、ここからの優先順位は、

```text
新機能追加
```

より、

```text
統合
因果整合性
validation
performance
freeze
```

である。

---

# 63. ここから避けるべきこと

本番直前に、

```text
面白そうな新機能を大量追加
```

すること。

理由:

```text
validation不足
interaction bug
performance regression
resume failure
unexplained behavior
```

を増やす。

---

# 64. 推奨開発フェーズ

```text
Phase 1
Final Design Spec完成

Phase 2
State causality audit

Phase 3
Implementation gap closure

Phase 4
Validation

Phase 5
Scaling

Phase 6
Codex review

Phase 7
Final config freeze

Phase 8
Main run
```

---

# 65. 最終判断

現時点のシミュレーションは、

**かなり強い設計素材を持っている。**

しかし、

> 「機能が豊富だから設計が完成している」

とは言えない。

設計完成とは、

```text
何が存在し
なぜ動き
何が原因となり
どう状態が変わり
どう観測され
何と比較され
何を主張できるか
```

が全てつながった状態。

---

# 66. 次に作るべき正典

最終的には、

```text
SHIBUYA_SIMULATION_FINAL_DESIGN_SPEC.md
```

を作成し、

現在の

```text
Reality plan
Human Behavior audit
Server Runtime estimate
Design gaps / completion criteria
```

の内容を統合する。

このファイルを、

**simulation designのsingle source of truth**

とする。

---

# 67. 一行結論

> **今足りないのは新しいアイデアではなく、既にある世界・人間・認知・社会・計算・検証を、一つの因果システムとして固定する最終統合仕様である。**
