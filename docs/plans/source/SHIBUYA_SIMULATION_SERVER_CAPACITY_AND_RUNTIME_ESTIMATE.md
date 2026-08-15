# Shibuya Simulation — Server Capacity & Runtime Estimate

> 作成日: 2026-08-16  
> 対象: `gpu-sv-002` 上での渋谷25万人LLM社会シミュレーション  
> 目的: 現在のサーバー構成と、人間行動・認知・都市環境の高解像度化案を含めた場合に、  
> **何シミュレーション日を現実的に回せるか**を整理し、本番ラン設計の判断材料にする。

---

# 0. 結論

現在のサーバーは以下の構成である。

- CPU: 64 logical CPU / 2 NUMA nodes
- RAM: 251 GiB
- 実利用可能 RAM: 約242 GiB
- GPU: NVIDIA RTX A5000 24GB × 7
- 総VRAM: 約168GB
- `/home`: 約3.7TB空き
- OS: Ubuntu 22.04.5 LTS

この構成で、25万人を同時在場させ、

- Persona v2
- 現実的な日課
- 帰宅後生活
- 家族・世帯
- hunger / fatigue / sleep pressure
- 感情 / salience
- ACT-R型記憶
- 社会関係
- SNS / メディア
- cognition.fire
- PLATEAU由来空間属性
- Adaptive LLM Budget
- multi-level cognition
- Reality / Human Behavior Validation

などを入れた高解像度版を動かす場合、

## 推奨する本線

**25万人 × 10 simulation days**

を本番の基本構成とする。

現時点の推定では、高解像度版で

**1 simulation day ≒ 18〜24 wall hours**

程度を中心レンジとして見るのが安全。

したがって、

- 8 wall days → 約8〜11 simulation days
- 10 wall days → 約10〜14 simulation days
- 14 wall days → 約12〜20 simulation days

程度が現実的な帯になる。

ただし、14日をすべて1本の長期ランに使うことは推奨しない。

最も価値が高い構成は例えば、

- 10日 baseline
- seed 2 の短縮ラン
- checkpointからのcounterfactual分岐
- 最終解析・可視化

である。

---

# 1. 実サーバー構成

取得結果:

```text
OS:
Ubuntu 22.04.5 LTS

CPU:
64 logical CPUs
2 NUMA nodes

RAM:
251 GiB total
242 GiB available
8 GiB swap

Disk:
/home 約3.7 TB available

GPU:
RTX A5000 24GB × 7
total VRAM ≈ 168GB

Python:
3.10.12
```

---

# 2. この構成から分かること

## 2.1 RAM

従来最大の不確定要素だったRAM問題は大きく改善した。

以前の25万人時RSS推定には大きく2系統あった。

### 楽観側

```text
88〜110 GB
```

### 悲観側

```text
316〜363 GB
```

さらに在場・状態保持機構の一部を入れると、

```text
+ 約72 GB
```

程度の追加推定も存在している。

今回実機で

```text
242 GiB available
```

であることが確定したため、

```text
110 + 72 ≈ 182 GB
```

程度なら十分入る。

つまり、楽観〜中間推定が正しければ25万人はRAM上成立する可能性が高い。

一方で、悲観推定316GB以上が正しければ成立しない。

したがって最優先実測は、

```text
10,000 agents × 144 steps
```

のpeak RSSである。

この実測から25万人への傾きを取り直す。

---

# 3. LLM呼数についての重要な訂正

以前の単純計算では、

```text
max_llm_per_step = 300
300 × 144 / 250,000
≈ 0.173 calls / agent / day
```

としていた。

しかしこれは**全LLM呼数ではない**。

`max_llm_per_step`が直接制御しているのは主に、

- spontaneous cognition
- social fire
- reply
- deliberate系

の一部であり、

- 朝の計画
- 内省
- その他のlife系呼び出し

などは別経路を持つ。

既存の実測では、

```text
約14〜25 LLM calls / agent / simulation day
```

が小〜中規模ランで観測されたケースもある。

ただし25万人ではbudgetがbindingするため、そのまま線形には増えない。

---

# 4. 25万人向けのLLM密度

本番では、単純にLLM呼数を最大化するより、

**人間行動上価値の高いタイミングに再配分する**

方が重要。

推奨はmulti-level cognition。

```text
C0 Automatic
    ルール・習慣・身体行動
    LLMなし

C1 Micro cognition
    短い内的思考
    16〜64 token程度

C2 Normal deliberation
    会話、迷い、判断、再計画

C3 Deep cognition
    大きな意思決定、人生判断、強い葛藤、重大事件
```

25万人全員を毎step長文LLMで回すのではなく、

**必要な人・必要な瞬間だけ認知解像度を上げる。**

これは計算節約だけでなく、人間のattention allocationにも近い。

---

# 5. 目標LLM密度

25万人本番で狙う総LLM密度は、

```text
約4.5〜5.5 calls / agent / simulation day
```

程度をひとつの目標帯とする。

既存設計では、

```text
約4.51 calls / agent / day
```

相当の構成がすでに検討されている。

25万人なら、

```text
250,000 × 4.51
≈ 1,127,500 calls / simulation day
```

10日なら、

```text
≈ 11.3 million calls
```

となる。

これは十分巨大なLLM社会シミュレーションである。

---

# 6. max_llm_per_step の考え方

25,000人時に

```text
cap = 300
```

で得られるspontaneous cognition密度を25万人でも維持する場合、

約10倍の

```text
cap ≈ 3,000 / step
```

が目安になる。

つまり本番では、

```text
300固定
```

ではなく、

```text
実測R_eff
残りwall time
残りsteps
現在queue
GPU utilization
```

から自動調整するAdaptive LLM Budgetを使う方が望ましい。

概念式:

```python
remaining_budget_s = deadline - now
remaining_steps = total_steps - step

target_wall_per_step = remaining_budget_s / remaining_steps

llm_allowance = (
    target_wall_per_step
    - estimated_non_llm_time
    - io_reserve
)

budget = floor(
    llm_allowance
    * effective_requests_per_second
    * safety_factor
)
```

これに、

```text
min_budget
max_budget
purpose quota
fairness debt
```

を加える。

---

# 7. A5000 × 7 のLLM性能仮定

現時点ではR_effはまだ実測していない。

既存見積りには、

```text
18.3 req/s
21.0 req/s
46.2 req/s
```

などがある。

考え方は以下。

### 18.3 req/s
保守側。

### 21 req/s
現時点のplanning valueとして使いやすい。

### 30 req/s
かなり良好。

### 46 req/s前後
Automatic Prefix Cachingなどが非常によく効いた場合の楽観域。

本番計画では46 req/sを前提にしない。

まずは、

```text
21 req/s
```

程度を基準にする。

30を超えれば成功。

40〜46を安定して出せれば非常に良い。

---

# 8. 高解像度版の壁時計推定

以下は、

- N = 250,000
- dt = 10 min
- 約4.5 calls/person/day
- 人間行動追加によるCPUコスト +10〜30%
- checkpoint / restart / I/O等の15%安全余裕

を含めた概算。

| R_eff | 状態 | 1 sim-day / wall | 8 wall days | 10 wall days | 14 wall days |
|---:|---|---:|---:|---:|---:|
| 18.3 req/s | 保守 | 約27.5 h | 約7.0 sim days | 約8.7 | 約12.2 |
| 21 req/s | 基準 | 約22.7 h | 約8.5 | 約10.6 | 約14.8 |
| 30 req/s | 良好 | 約17.6 h | 約10.9 | 約13.7 | 約19.1 |
| 46.2 req/s | 非常に良好 | 約11.3 h | 約17.0 | 約21.2 | 約29.7 |

46.2 req/sのケースは楽観値なので、本番計画には使わない。

---

# 9. 中心予測

最も現実的な中心レンジは、

```text
1 simulation day
≈ 18〜24 wall hours
```

程度。

つまり概ね、

```text
simulation time : wall time
≈ 1 : 1
```

前後。

この規模としては十分速い。

---

# 10. 人間行動改善案のCPUコスト

前回提案した改善の多くはLLMを必要としない。

例:

- hunger
- fatigue
- sleep pressure
- home-awake lifecycle
- habits
- family state
- relationship decay
- social attention
- activity-time distribution
- routine probability
- household behavior
- human error
- schedule conflict
- time-use calibration

これらは主に、

```text
float更新
状態遷移
確率抽選
small lookup
```

なので、適切に実装すればGPUではなくCPU側の追加負荷になる。

本見積りでは安全側に、

```text
CPU +10〜30%
```

を仮置きしている。

ただしO(N²)処理を入れると一気に破綻するため、

**25万人では全機構をO(N)またはO(N log N)程度に抑える。**

禁止対象例:

```text
全agent pair比較
全agent間距離
global social pair enumeration
全POI総当たり
毎step巨大DataFrame再構築
```

---

# 11. PLATEAU追加の負荷

PLATEAU 2025由来の詳細都市データを使っても、

**engineが3D meshそのものを持つ必要はない。**

推奨:

```text
Viewer:
    PLATEAU 3D Tiles

Engine:
    simplified building table
```

engine側は例えば、

```text
building_id
centroid
footprint
height
storeys
usage
capacity
entrance
```

程度。

したがってPLATEAU導入そのものは25万人実行速度の主律速にはしない。

---

# 12. 物理シミュレーションのLOD

全渋谷を高精細pedestrian physicsで解くのは避ける。

推奨:

```text
都市全体:
    graph/routing

混雑地点:
    crowd approximation

重点ゾーン:
    SFM / pedestrian microphysics
```

例:

- スクランブル交差点
- 駅改札
- 大型イベント会場
- 駅前広場

だけをmicrophysicsにする。

---

# 13. dtについて

本番25万人では、

```text
dt = 10 min
```

を基本とする。

5分化すると認知側よりengine側のstep数増加が支配的になる。

過去実測ではdt=5でengine wallが約1.65倍に増えたケースがある。

したがって、

**人間の思考を細かくするためにglobal dtを細かくするのではなく、**

```text
world = 10 min macro step
cognition = event-driven
physics = local substep
```

にする。

これが最も計算効率が良い。

---

# 14. 10日を推奨する理由

14日間GPUを使えるとしても、

```text
14 simulation daysを1回
```

だけ回すのは最善ではない。

より価値が高いのは、

```text
Main:
25万人 × 10日

Residual GPU:
seed 2
counterfactual
ablation
reality validation
```

である。

例えば、

```text
Seed 1
Day 0 ───────────── Day 10
                  │
                  ├─ intervention A
                  ├─ intervention B
                  └─ intervention C
```

のようにcheckpointをforkする。

これなら、

```text
同じ都市
同じ人間
同じ履歴
```

から施策だけを変えられる。

社会デジタルツインとして非常に強い。

---

# 15. Hackathon的にも「長さ」より「比較可能性」

発表では、

```text
25万人を14日間回した
```

だけより、

```text
25万人の渋谷を10日間連続実行
↓
現実統計と照合
↓
別seedでも主要特性を確認
↓
同一checkpointから施策をfork
↓
世界の違いを比較
```

の方が強い。

つまりGPU時間は、

**single longest run**

ではなく、

**validated executable society**

を作るために使う。

---

# 16. 最優先で取るべき実測

今後の推定誤差を最も減らす値は2つ。

## 16.1 R_eff

A5000×7で、

```text
effective requests / second
```

を測る。

本番相当prompt長を使う。

最低でも、

```text
input ≈ 1000 token
output ≈ 64 token
```

程度を使う。

測るもの:

```text
req/s
input tok/s
output tok/s
P50 latency
P95 latency
GPU utilization
VRAM
prefix cache hit
```

---

## 16.2 10k × 144 step

本番ONセットに近い設定で、

```text
10,000 agents
144 steps
1 simulation day
```

を実走する。

必須記録:

```text
elapsed_sec
peak_rss_mb
run directory size
LLM calls
events
checkpoint size
checkpoint save time
CPU utilization
```

---

# 17. この2値から25万人を再計算する

実測後は、

```text
engine_sec_per_agent_step
=
elapsed_non_llm
/
(N × steps)
```

を求める。

LLM側は、

```text
T_llm
=
total_calls
/
R_eff
```

engine側は、

```text
T_engine
=
c × N × steps
```

さらに、

```text
T_io
T_checkpoint
safety margin
```

を加える。

これで初めて、

```text
25万人で何simulation day回せるか
```

をかなり正確に出せる。

---

# 18. GO / NO-GOの目安

## RAM

### GO

```text
250k projected peak RSS
< 180 GiB
```

かなり余裕あり。

### CONDITIONAL

```text
180〜215 GiB
```

checkpoint peakやPython一時オブジェクトを確認。

### NO-GO

```text
> 220 GiB
```

かなり危険。

251GiB totalでもOS・vLLM・filesystem cache等が必要。

---

# 19. R_effの目安

### R_eff < 15

25万人高認知版はかなり厳しい。

LLM密度を下げるかNを下げる。

### 15〜20

10日は可能性あり。

かなり慎重なbudgetが必要。

### 20〜30

25万人×10日が十分現実的。

### 30〜40

かなり良好。

seed2 / counterfactualまで狙える。

### >40

非常に良い。

GPUが十分活かせている。

---

# 20. 推奨最終構成

現時点での第一候補:

```yaml
agents_present: 250000
persona_pool: 1000000

dt_min: 10

duration_days: 10

persona_v2: true

home_awake: true
household: true
needs: true
affect: true
actr_memory: true
relations: true
media: true

cognition:
  adaptive_budget: true
  fire: true  # 実測GOの場合
  microthought: true
  deliberation: true
  deep_cognition: event_only

llm:
  fleet_gpus: 7
  target_calls_per_agent_day: 4.5-5.5

observer:
  streaming: true

checkpoint:
  atomic: true
  streaming: true
```

---

# 21. 最終判断

現在のサーバーは、

**25万人の高解像度生成型社会シミュレーションを本気で狙える構成**

である。

特に、

```text
RAM 251 GiB
GPU 24GB × 7
/home 3.7TB
```

は非常に大きい。

最大の未知数はもう「理論上GPUが足りるか」ではなく、

```text
R_eff
250k RSS
```

の2つ。

この2値を実測したあとで、

```text
LLM density
duration
checkpoint cadence
counterfactual budget
```

を最終決定する。

---

# 22. 一行戦略

> **25万人という規模を落とさず、人間行動は非LLM機構で高解像度化し、LLMは重要な認知だけに集中させ、10日baselineを確実に完走させた上で残りGPUをseed・反実仮想・検証に使う。**

---

# 23. 次に実行すること

1. A5000×7で本番相当vLLM benchmark
2. 10k×144stepのpeak RSS / elapsed測定
3. 25万人への外挿
4. Adaptive LLM Budget上限決定
5. 50k → 100k → 250kのscale rehearsal
6. final config freeze
7. 25万人×10日 main run
8. seed / counterfactual / reality validation
9. viewer・解析・発表資料生成

この順序を崩さない。
