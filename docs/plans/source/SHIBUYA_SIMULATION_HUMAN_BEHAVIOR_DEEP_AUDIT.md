# SHIBUYA SIMULATION — Human Behavior Deep Audit
## 実世界の人間行動を再現するための全方位監査・実装提案・検証計画

**対象リポジトリ:** `spacedream6090-svg/shibuya-simulation`  
**監査スナップショット:** `main @ 5a7df6573cf6f75f076b2900829930df548bc233`  
**作成:** 2026-08-16  
**位置づけ:** 前回の「世界・環境・計算資源・現実接地」を主眼とした改善計画とは別の、**人間そのものの行動生成・認知・生活・社会関係の忠実度を主対象にした追加監査**。  
**主目的:** 「渋谷の中に25万人の点が動いている」のではなく、**現実の人間に近い制約・習慣・欲求・思考・社会関係・生活時間を持つ人々が都市を生き、その相互作用から都市現象が生まれる**状態へ近づける。

---

# 0. 最初に — 「現実を完璧に再現する」の意味を定義する

このプロジェクトの最終目標を高く置くことには賛成だが、研究・ハッカソン双方で最も強い主張は、

> 「人間を完璧に再現した」

と無検証で言うことではない。

強い状態は、

> **人口、生活時間、移動、社会接触、情報行動、消費、睡眠、会話、関係形成など複数の独立した実データに対して、エージェント集団の行動分布がどこまで一致するかを測定し、較正に使っていないデータでも一致を確認した。さらに、LLMを増減した場合・認知機構を外した場合に何が変わるかまで示せる。**

という状態である。

したがって本書では、完成度を次の4段階に分ける。

| レベル | 定義 |
|---|---|
| L0: Believable | 見た目・文章・デモ上で人間らしく見える |
| L1: Distributionally Grounded | 行動時間・移動・接触・消費等の**周辺分布**が現実と合う |
| L2: Jointly Grounded | 年齢×職業×時刻×場所などの**条件付き・結合分布**まで合う |
| L3: Behaviorally Predictive | 較正に使っていない日・場所・集団・介入に対しても現実的な応答を出す |
| L4: Individual Digital Twin | 特定個人の履歴・選好・回答を再現する |

**この14日で狙うべきは L2〜L3。**  
L4は実在個人のインタビュー・行動履歴が必要で、このプロジェクトの目的ともデータ条件とも異なる。

StanfordのParkらの1,052人研究では、単なる属性ペルソナではなく、実在個人への詳細な質的インタビューを与えて初めて、本人のGSS回答を本人自身の2週間後再回答に対して約85%の精度で再現した。これは逆に、**「年齢・職業・性格・一枚のpersona文を与えれば、その人を再現できる」という仮定を置いてはいけない**ことを示す重要な比較対象である。

---

# 1. エグゼクティブサマリー

## 1.1 現在のエージェントは「かなり高度」だが、「人間モデルとして完成」ではない

現行コードには、一般的なLLMマルチエージェントよりはるかに多くの人間行動要素がすでにある。

実装を確認できた主要要素:

- `Agent` に年齢、職業、persona、traits、states、訪問履歴、家庭、勤務、睡眠、金銭、記憶、信念、drive、arousal、疲労、健康、社会関係等が存在
- 日常行動は `cognition/routine.py`
- 1日計画は `cognition/planning.py` + `cognition/day_plan.py`
- 自発思考の入口は `cognition/drive.py`
- 記憶は `agents/memory.py` に3層構造 + ACT-Rオプション
- 感情・注意は `factors/affect.py`
- 欲求差は `needs.py`
- 内面・長期目標・趣味は `inner_life.py`
- 関係の深化/悪化は `relations.py`
- 自由行動価値は `values.py`
- 本選候補設定では `needs/affect/inner_life/routine.stochastic/day_plan/ACT-R/relations/Dunbar/freedom` の多くがON
- EPR（Exploration and Preferential Return）を移動に利用
- 生活予定には固定活動と裁量活動の区別がある
- 寄り道、時間ジッター、中断など「予定どおりに動かない」揺らぎがある

これは強い。

ただし、現在の最大の問題は、

> **「人間らしい機構の名前や状態変数が多数ある」ことと、「それらが現実の人間と同じ頻度・相関・因果関係で行動を変えている」ことがまだ同義になっていない**

ことにある。

---

## 1.2 本監査の結論

### 現時点で特に強い部分

1. **移動の骨格**
   - home/work anchor + EPRという方向は文献にかなり整合的。
   - 人間移動が「ランダムウォーク」ではなく、少数の場所への反復と新規探索の混合であるというGonzález 2008 / Song 2010の結果に沿う。

2. **日課と計画の二層構造**
   - routineとLLM planを分けている点は良い。
   - 人間は毎瞬LLM的に熟考するのではなく、習慣と計画を混ぜて生きるため、この方向は正しい。

3. **記憶**
   - episodic buffer / consolidated memories / beliefs-relations という分離は良い。
   - ACT-Rの活性化・忘却・fan effectまでオプションで持つのは高度。

4. **欲求・感情・注意を単なるprompt文だけでなく状態として持つ**
   - `drive`, `arousal`, fatigue, needs profile などが世界の状態変化から更新される。
   - 「LLMの中だけに人格がある」より圧倒的に再現性を作りやすい。

5. **自由行動**
   - open action / move home / buy / study / partnership / deviance が本選候補でONなのは、創発を観測する上で良い。

### 現時点で最も弱い部分

1. **人間の習慣が「学習されない」**
2. **身体的欲求が不足している**
3. **帰宅後の家庭生活がほぼ欠落している**
4. **LLM認知頻度が25万人規模に対して薄すぎる**
5. **`cognition.fire` が本選候補でまだOFF**
6. **長期目標・趣味が固定辞書から決まる部分が大きい**
7. **会話・関係形成を現実の接触時間・社会容量に対して較正していない**
8. **グループ会話・集団行動が二者関係中心になりやすい**
9. **家族/同居人による共同意思決定が弱い**
10. **現実の日本人の生活時間、メディア時間、消費、外出率等との自動比較が不足**
11. **LLMそのものが日本人の人間行動を再現できるかの外部検証が不足**
12. **多くの係数が“文献に着想を得た手設定値”であり、データから推定されたパラメータではない**

---

## 1.3 完成度の暫定スコア

以下は統計的測定値ではなく、**コード監査上のengineering judgment**。  
5 = 現実データに直接較正され、複数軸で検証済み、を意味する。

| 行動領域 | 現在 | 14日で狙える | 主な理由 |
|---|---:|---:|---|
| 人口属性 | 3.0 | 4.2 | v2で大幅改善可能 |
| 生活時間 | 2.0 | 4.0 | 帰宅=睡眠問題が大きい |
| 移動先選択 | 3.4 | 4.3 | EPR良、実データvalidation不足 |
| 移動時間/OD | 3.0 | 4.2 | PT接地で伸ばせる |
| 習慣 | 2.0 | 4.0 | static routineはあるが学習が弱い |
| 計画 | 3.5 | 4.2 | day_plan v1がかなり良い |
| 自発思考 | 2.1 | 4.0 | driveは良いがfireとLLM密度 |
| 注意 | 3.0 | 3.8 | salience実装済、較正が必要 |
| 感情 | 2.5 | 3.7 | valence×arousalは有用だが粗い |
| 身体欲求 | 2.0 | 3.8 | fatigue/healthあり、hunger等弱い |
| 記憶 | 3.7 | 4.2 | ACT-Rが強い、retrieval validation必要 |
| 長期目標 | 2.3 | 3.8 | 固定テンプレ依存を減らす |
| 社会接触 | 2.8 | 4.0 | co-locationはあるが実分布validation不足 |
| 関係形成 | 3.0 | 4.0 | closeness/tier/Dunbarあり |
| 家族/家庭 | 1.8 | 3.8 | 夜の家庭生活の欠落 |
| 会話 | 2.8 | 3.8 | LLM会話はあるが頻度/長さ/拒否が要較正 |
| 集団行動 | 2.2 | 3.6 | group/hyperedge表現を強化 |
| 仕事 | 3.2 | 4.0 | org/work配線は強い |
| 消費 | 2.5 | 3.8 | 固定価格/簡略カテゴリが課題 |
| SNS/メディア | 2.5 | 3.8 | 機構はあるが現実利用時間差 |
| 健康 | 3.0 | 3.8 | health/fatigueは良、因果簡略化あり |
| 規範/文化 | 2.2 | 3.6 | 日本固有の行動規範の実証が必要 |
| 学習・適応 | 2.2 | 3.7 | habit/choice learningを追加 |
| LLM人間忠実度 | 2.3 | 3.8 | model batteryと高解像度shadow runが必要 |
| 行動validation | 2.0 | 4.5 | 14日で最も伸ばすべき領域 |

**総評:**  
現在は「非常に機能豊富なhybrid generative ABM」。  
14日で目指すべきは「機能をさらに100個追加したABM」ではなく、

> **既存機構を人間行動データへ接続し、欠落している日常生活・習慣・認知密度を埋め、各層のズレを数値として示せる行動デジタルツイン候補**

である。

---

# 2. 人間行動をどう分解して評価するか

本書では人間の行動を次の因果チェーンに分ける。

```text
社会人口属性・人生履歴
        ↓
価値観・性格・役割・身体
        ↓
長期目標 / 義務 / 関係
        ↓
習慣・日課
        ↓
その日の予定
        ↓
環境知覚・刺激・情報
        ↓
注意 / 感情 / 欲求 / 疲労
        ↓
「考える必要があるか」
        ↓
選択肢の生成
        ↓
意思決定
        ↓
物理行動
        ↓
他者・組織・環境からの反応
        ↓
結果・報酬・感情
        ↓
記憶
        ↓
習慣・価値・関係・期待の更新
        └──────────→ 次の行動
```

**重要:**  
このループが閉じて初めて「生きた人間」になる。

単に以下が存在するだけでは不足する。

- personaがある
- memoryがある
- emotion変数がある
- LLMが呼ばれる
- friend graphがある

必要なのは、

> **環境で起きた経験が内部状態を変え、その状態が次の選択を変え、その結果がさらに内部モデルを書き換えること**

である。

---

# 3. 現在の行動アーキテクチャ監査

## 3.1 Agent state — 状態の豊富さはかなり高い

`src/society/agents/agent.py`

現在のAgentは少なくとも以下を持つ。

- demographic: age, gender, occupation
- persona / traits / states
- residence / commute / workplace
- route / visits / mode
- home / building / floor
- bedtime / sleeping
- day_plan / schedule
- money / account / wage / rent
- beliefs
- episodic memory
- social relationship ledger
- drive
- arousal
- fatigue
- health/severity
- conversation reply state
- opinion dynamics

これは非常に良い基盤である。

### ただし重要な監査原則

今後は全stateについて、次を機械的に検査するべき。

```text
STATE
  ├─ Writer: 誰が更新する?
  ├─ Reader: 誰が読む?
  ├─ Behavior effect: 行動を変える?
  ├─ Persistence: pool/checkpoint/resumeで維持?
  ├─ Observation: ログで追える?
  └─ Validation target: 現実の何と比較できる?
```

**Readerがないstateは「飾り」。**  
Writerがないstateは「初期値固定」。  
Behavior effectがないstateは「表示用人格」。  
Persistenceがないstateは「記憶喪失」。  
Validation targetがないstateは「現実的か判定不能」。

### 提案: `scripts/audit_state_causality.py`

AST/grepベースで、

```json
{
  "state": "fatigue",
  "writers": ["health.py", "..."],
  "readers": ["routine.py", "drive.py"],
  "checkpointed": true,
  "pool_transport": true,
  "logged": true,
  "behavior_affecting": true
}
```

を出す。

これを**全Agent state**へ行う。

本番前の「機構はあるのに実際には何も効いていなかった」を減らせる。

---

# 4. 習慣 — 現状の最大級の認知ギャップ

## 4.1 現在

`routine.py` はかなり良い。

- 通勤
- 勤務
- 食事
- 帰宅
- 睡眠
- EPR自由移動
- novelty day
- time jitter
- detour
- interruption

まである。

人間の行動が完全な最適化ではなく、定型行動と逸脱の混合である点を表現している。

## 4.2 文献との比較

Wood & Rünger (2016) の習慣レビューでは、

- 同じcontextで同じresponseを繰り返すことでhabitが形成
- habitは効率的なdefault
- deliberate goal pursuitとhabitは競合・協調する

と整理されている。

現在のroutineは「人間は習慣的」という**形**は持っている。

しかし、

> **シミュレーション内の経験によって新しい習慣が形成される**

部分が弱い。

つまり現在は、

```text
persona/config
    ↓
routine
```

が中心。

理想は、

```text
context
  ↓
action
  ↓ repeated success
habit_strength +=
  ↓
future action more automatic
```

である。

---

## 4.3 実装提案: Contextual Habit Memory

Agentに巨大なstateを足す必要はない。

```python
agent.habits = {
    habit_key: {
        "strength": float,
        "count": int,
        "last_step": int,
        "reward_ema": float
    }
}
```

`habit_key`例:

```text
(time_band, weekday_type, context_type, action, destination_class)
```

例:

```text
("weekday_morning", "workday", "home", "commute", work_node)
("evening", "weekday", "station", "buy", "convenience_store")
("night", "weekday", "home", "media", "video")
```

### 更新

成功した反復:

```python
strength += alpha * (1 - strength)
```

長期不使用:

```python
strength *= exp(-lambda * elapsed_days)
```

大きなnegative outcome:

```python
strength -= beta * surprise
```

### 行動選択

```text
habit_strength 高
かつ
salience/conflict/stakes 低
        ↓
LLM不要
habit実行

habit弱い
or novelty
or conflict
or high stakes
        ↓
LLM / deliberate policy
```

これは**LLM節約ではなく人間らしさのためのLOD**になる。

---

# 5. 身体・生理的欲求

## 5.1 現在

良い部分:

- fatigue
- sickness
- severity
- sleep
- health
- heatstroke/trauma等
- eatingというroutine行動

本選候補では `health.enabled: true` かつ fatigue gainも有効。

## 5.2 欠けている重要なSystem 1

コード検索上、`hunger`は主要な継続状態として存在していない。

現状の食事は時間窓主体。

しかし現実では、

```text
時刻
＋
前回食事
＋
身体状態
＋
仕事中か
＋
金
＋
同行者
＋
周辺店舗
＋
習慣
```

の組合せで食事が決まる。

同様に、

- sleep pressure
- hunger/satiety
- thirst（必要なら簡略）
- caffeine/alcohol
- physical comfort
- toilet urgency

などは人間の日常行動を強く制約する。

全部は要らない。

### P0で追加する最低限

1. `hunger`
2. `sleep_pressure`
3. `fatigue`（既存を改善）

これだけでよい。

---

## 5.3 Hunger model

```python
hunger ∈ [0, 1]

hunger += basal_rate * dt
hunger += activity_factor
hunger -= meal_satiety
```

食事のtrigger:

```text
hunger
× time-of-day prior
× social context
× available money
× POI opportunity
× work constraints
```

「12時だから全員食べる」を避ける。

### validation

- 朝食欠食率
- 昼食/夕食時刻分布
- 外食率
- meal duration
- 年齢/就業別

厚労省「国民健康・栄養調査」を利用可能。

---

# 6. 睡眠・帰宅・家庭生活 — 現時点の最重要行動バグ

既存リポジトリ自身の100日ラン再集計で、

- `enter_building{home:true}` の100%が同じ分に `sleep_start`
- 帰宅→睡眠 gap = 0分
- 21時の在宅率が現実より大幅に低い
- 夜の家庭内mediaが少ない

ことが既に確認されている。

これは単なる「夜の見た目」の問題ではない。

## 6.1 波及する歪み

帰宅即睡眠にすると、

- 家族会話
- 恋人との会話
- 夕食
- 家事
- 入浴
- SNS
- TV/動画
- ゲーム
- 読書
- 勉強
- 持ち帰り仕事
- 趣味
- 子どもの世話
- 一人時間
- 翌日の準備
- reflection/mind wandering

がほぼ消える。

結果として、

**家庭 → 感情 → 関係 → 翌日の行動**

という巨大な因果経路が落ちる。

---

## 6.2 必須実装

`go_home` と `go_to_bed` を完全に分離する。

```text
work/outside
 ↓
commute
 ↓
HOME_AWAKE
 ├─ eat
 ├─ household_interaction
 ├─ media
 ├─ bath
 ├─ chores
 ├─ study
 ├─ hobby
 ├─ online_social
 ├─ relax
 └─ sleep
```

### Home Activity Scheduler

家庭行動を固定タイムテーブルにしない。

候補utilityを計算:

```text
U(activity) =
  habit
+ need
+ social affordance
+ goal relevance
+ time prior
+ fatigue effect
+ media availability
+ stochastic shock
```

LLMは毎10分呼ばない。

通常は軽量choice。

葛藤時だけLLM。

---

## 6.3 睡眠

現行 `bedtime_min` の個体差は良い。

ただしより人間的には、

```text
sleep_probability =
f(
    circadian_time,
    sleep_pressure,
    next_day_obligation,
    fatigue,
    current_activity,
    media_use,
    social_context
)
```

にする。

**就寝予定時刻 = 強制時刻ではなくhazard peak**として扱う。

---

## 6.4 内省の配置

既存の「就寝前に一日の出来事を順に思い出し、明日への影響まで考える」型は全人口に毎晩適用すると人工的。

Lemyre et al. (2020)のsystematic reviewでは、正常な入眠への移行は高次認知の脱活性化・感覚的imageryを伴い、planning/problem-solvingの就寝前思考はinsomnia側に多い。

一方、Smallwood & Schooler (2015)が整理するmind wanderingは、日中の低外的負荷時にも広く起こる。

### 新設

```text
microthought
reflection
rumination
planning
memory_replay
```

を分ける。

### 発生しやすい状態

- 徒歩
- 電車
- 一人で待つ
- 家事
- 入浴
- 食事後
- 就寝前
- boring work
- SNSを閉じた直後
- emotional event後

### LLMコスト

`microthought` は16–64 output tokens。

長いreflection 300–600 tokensより圧倒的に安い。

**GPUを使って認知密度を上げるならここが最適。**

---

# 7. 人間の「考える頻度」 — LLM callは増やすべきだが、毎step長文は違う

## 7.1 現状問題

25万人、144 step/dayで `max_llm_per_step=300` なら、単純上限は43,200 calls/day。

1人あたり平均:

```text
43,200 / 250,000 = 0.1728 calls/person/day
```

計画・会話・反省・応答で共有する。

この密度では、

> 「25万人全員の認知から社会が創発した」

という主張は弱い。

---

## 7.2 しかし「25万人 × 144step × LLM」は不要

人間も毎10分、

> 「現在の状況を説明してください。次の行動をJSONで出してください」

とは考えない。

人間行動は多くが自動化されている。

正しい設計は、

```text
System 1
  habit / routine / motor / simple choice
          ↓
conflict/surprise/stakes
          ↓
System 2
  LLM deliberation
```

である。

---

## 7.3 Cognition LODを4段階にする

### C0 — Automatic
LLMなし。

- habitual commute
- familiar walking
- routine work
- known meal
- ordinary phone checking

### C1 — Micro cognition
小モデル/短output。

16–64 tokens。

例:

```json
{
  "focus":"疲れている",
  "intent":"帰宅したい",
  "next":"home"
}
```

### C2 — Deliberation
8B class。

64–256 tokens。

- plan deviation
- shopping
- social approach
- unusual event
- argument
- news reaction

### C3 — Deep cognition
高価なモデル/長context。

- major conflict
- breakup
- job loss
- crime victimization
- policy shock
- strong moral decision
- major plan revision
- rare long reflection

---

## 7.4 AdaptiveLLMBudgetController

固定:

```yaml
max_llm_per_step: 300
```

ではなく、

```python
budget = f(
    measured_req_per_sec,
    gpu_queue,
    step_deadline,
    remaining_wall_time,
    predicted_future_load
)
```

にする。

### 条件

1. GPU idleを作らない
2. step deadlineを破らない
3. replyを飢餓させない
4. cognition debtを持つ
5. high salienceを優先
6. 一部agentへの集中を防ぐ

---

## 7.5 Cognition debt

```python
agent.cognition_debt += dt

if agent gets LLM:
    debt = 0
```

優先度:

```text
priority =
  salience
+ reply_urgency
+ plan_exception
+ emotional_intensity
+ novelty
+ cognition_debt
+ fairness_bonus
```

これにより、

> 事件に巻き込まれた同じ50人だけが毎日LLMを使い、残り24万9950人が永遠にroutine

を防げる。

---

## 7.6 推奨call密度の目標

「1人1日何callが人間らしい」という自然定数は存在しない。

したがって、call数自体を現実へ合わせるのではなく、

**高解像度shadow modelに対して低LODの行動がどれだけ一致するか**

で決める。

運用目標としては段階的に:

```text
0.2 semantic calls/person/day  現状近辺
0.5
1.0
1.5
2.0+
```

を実測。

短いmicro-cognitionを含めれば、1〜2 semantic call/人/dayでもかなり違う。

---

# 8. `cognition.fire` — 人間行動の中核なので本番判断を最優先

本選候補configでは、

- `g_update` はON
- `fire/watch/engaged` はコメントアウト

になっている。

コード側自身も、fire OFFでは `g_update` が実効にならないと認識している。

これは本質的。

## 8.1 なぜ重要か

人間は、

```text
朝に予定を立てた
↓
その予定を12時間実行する
```

存在ではない。

途中で、

- 人に会う
- 混雑する
- ニュースを見る
- 疲れる
- 財布が減る
- 雨が降る
- 電車が遅れる
- 嫌なことを言われる
- 面白いものを見る

と内部状態が変わり、

**その場で考え直す**。

fireはまさにこの入口。

---

## 8.2 必須条件

fireをただONにするのではなく、

```text
event
↓
salience
↓
attention bottleneck
↓
fire request
↓
global LLM budget
↓
deliberation
↓
action/plan update
```

にする。

### 実測ゲート

- calls/person/day
- response starvation
- plan completion
- wall time
- GPU utilization
- entropy of triggered agents
- unique agents receiving cognition
- distribution by age/job/tier
- state_hash/replay

---

# 9. Drive — 良いが「1本のゲージ」に集約しすぎる

`cognition/drive.py` は、

```text
event
→ drive += weight
→ threshold
→ probabilistic fire
```

という構造。

これは計算効率が良い。

現在weight例:

- novel_place 0.35
- congestion 0.30
- unknown_word 0.40
- addressed 0.25
- dm_received 0.35
- news 0.15
- sns 0.08
- company 0.10
- silence 0.015
- state_change 0.50

## 9.1 問題

すべてを同じ`drive`へ足すと、

```text
寂しい
腹が減った
知らない言葉
大混雑
ニュースを見た
疲れた
```

が**同じ「考えたい度」**に圧縮される。

発火判定のためのscalarはあってよいが、その前段にmotivational channelsを残すべき。

---

## 9.2 提案

```python
drive_channels = {
    "social": 0.2,
    "novelty": 0.1,
    "homeostasis": 0.5,
    "threat": 0.0,
    "goal_conflict": 0.4,
    "information": 0.3
}
```

最終fire urgencyだけscalarにする。

```python
fire_urgency = max(channel) + conflict_bonus
```

これでLLM promptにも、

> 「なぜ考え始めたか」

を正しく渡せる。

---

# 10. Needs — 理論的には良いが、現在は“手製の理論融合”

`needs.py` は、

- stimulation
- security
- relatedness
- competence
- autonomy

という5軸を持つ。

SDT, Schwartz, Reiss, sensation seeking等に着想。

これは有用なlatent space。

しかし係数は、

```text
novel_place: stimulation +1.0, autonomy +0.5, security -0.6
...
```

のように設計者が決めている。

## 問題

「論文を引用している」ことは、

> その係数が日本の高校生/会社員/高齢者の実際の行動を再現する

ことを意味しない。

---

## 10.1 提案 — latent traitは残し、係数を較正対象にする

hard-code:

```python
0.7
0.4
1.0
```

ではなく、

```yaml
behavior_params:
    need_to_novelty: ...
    need_to_social: ...
```

へ出す。

### fitting

ABC / Bayesian optimization / Optunaでもよい。

目的:

```text
simulated activity distribution
vs
real activity distribution
```

を最小化。

人間行動モデルのパラメータを**人間データから推定**する。

---

# 11. Affect / emotion

`factors/affect.py` には、

- arousal leaky integrator
- novelty/arousal → memory importance
- salience
- Yerkes-Dodson型 threshold変調

がある。

本選候補ではON。

これは非常に良い。

## 11.1 現在の限界

core affectを低次元化すること自体は妥当。

しかし、

```text
valence × arousal
→ fixed discrete label
```

だけでは、

- anger
- fear
- shame
- guilt
- envy
- pride
- loneliness
- relief

の**行動傾向**が異なることを十分表せない。

同じnegative-high-arousalでも、

```text
fear → avoid
anger → approach/confront
```

が違う。

---

## 11.2 14日向け実装

巨大なemotion ontologyは不要。

最低限、

```python
action_tendency = {
    "approach": float,
    "avoid": float,
    "affiliate": float,
    "withdraw": float
}
```

を追加。

感情名ではなく**行動への力**にする。

例:

```text
threat + low control → avoid
threat + high control → confront
loss → withdraw
social acceptance → affiliate
novel positive → explore
```

これがdestination/social action/fireへ影響。

---

# 12. Long-term goals — 現在は人間の「人生」よりテンプレに近い

`inner_life.py` の長期目標は、dominant dimensionから決定論的に、

- 刺激のある毎日
- 安定した暮らし
- 仲間を増やす
- スキルを磨く
- 自由に生きる

等を割当。

趣味も職業→少数カテゴリのdictionary。

### 良い点
promptに長期方向性を与えられる。

### 問題
**人生経験によって目標が生まれる/消える/変わる**経路が弱い。

---

## 12.1 Goal memory

Agent:

```python
goals = [
    {
      "text": "...",
      "priority": 0.7,
      "progress": 0.3,
      "created_from": event_id,
      "deadline": ...,
      "status": "active"
    }
]
```

### goal生成条件

毎日生成しない。

- repeated dissatisfaction
- major success/failure
- new relationship
- job event
- health event
- strong reflection
- new opportunity

のみ。

LLM callを既存deep cognitionと共用。

### goal decay

何日も行動に現れないgoalは弱まる。

### validation

現実データでgoalを直接検証しにくいので、

- behavior consistency
- goal/action alignment
- persistence
- revision after shocks

を内部妥当性として測る。

---

# 13. Day Plan — かなり良い。改善は“合理的すぎる”点

`day_plan.py` はActivity-Based Model文献をかなり丁寧に取り入れている。

- mandatory/flexible
- start/end
- location
- companion
- priority
- repair
- conflict resolution

は良い。

## 13.1 人間は予定を守らない

既存stochastic layerの、

- jitter
- detour
- interrupt

は非常に重要。

さらに必要なのは、

- procrastination
- forgetfulness
- overrun
- underestimation
- social interruption
- opportunity capture
- sunk cost
- fatigue-induced cancellation

。

---

## 13.2 Plan adherence model

予定ごとに、

```text
P(execute) =
f(
  priority,
  habit,
  fatigue,
  mood,
  social invitation,
  travel cost,
  lateness,
  money,
  weather,
  current reward
)
```

を軽量モデルで計算。

LLMが「計画した」から必ず合理的に消化しない。

---

# 14. 人間の限定合理性

LLMはしばしば、

- 説明しすぎる
- 一貫しすぎる
- socially desirable
- altruistic
- reflective
- 知識が多すぎる

傾向がある。

2026年のdictator game評価でも、**human-like personaを与えただけではhuman-like behaviorにならず、モデル・promptによって人間との一致方向が不安定**という結果が報告されている。

したがって、

> LLMに「あなたは25歳会社員です。人間のように行動してください」

だけでは不足。

---

## 14.1 Decision architecture

普通の選択は、

```text
bounded opportunity set
↓
limited attention
↓
habit + utility + noise
```

で決める。

LLMは、

- choice set generation
- unusual preference
- high-stakes deliberation
- dialogue
- interpretation

に使う。

---

## 14.2 Choice setを現実に限定

人は「渋谷の全店舗」を比較しない。

```python
choice_set =
    familiar_places
  + nearby_visible_places
  + recommendations
  + social suggestions
  + a few exploration candidates
```

これが重要。

LLMに全POI情報を与えると超人的に最適化する。

---

# 15. Mobility — 現状の強い部分と追加検証

## 15.1 文献

González, Hidalgo & Barabási (Nature, 2008):
- 100,000人の携帯データ
- 個人移動は高い時間的・空間的規則性
- 少数の頻出場所へ戻る

Song et al. (Nature Physics, 2010):
- random CTRWでは不十分
- exploration + preferential return

Alessandretti et al. (Nature Human Behaviour, 2018):
- 約4万人の複数年軌跡
- familiar location setは入れ替わるが、典型的サイズは約25

Miritello等の社会容量研究と合わせると、

**人間は移動場所も社会関係も無限に増やさない。**

---

## 15.2 現状

routineのEPRは方向として非常に良い。

しかし「EPRを実装している」だけでは不足。

### 必須validation

個人ごとに:

- radius of gyration
- unique places/day
- unique places/10d
- familiar-place capacity
- rank-frequency of visits
- return probability
- exploration probability
- dwell time distribution
- trip distance
- trip duration
- departure time
- home/work share
- mobility entropy
- trip chaining
- mode share

を計測。

---

## 15.3 Returner / Explorer heterogeneity

全員に同じ `RHO/GAMMA` を与えるより、

```python
rho_i
gamma_i
```

をpersona/age/occupation/learned-historyから持たせる。

**個体差の分布そのものを較正**する。

---

# 16. 社会接触 — 「同じ場所にいた」≠「交流した」

人間の都市社会では、

```text
co-presence
→ perceptual opportunity
→ recognition
→ approach/avoid
→ interaction
```

という段階がある。

25万人都市で、近くにいる人全員が会話対象になるのは不自然。

---

## 16.1 Attention bottleneck

相手に気づく確率:

```text
P(notice) =
f(
 distance,
 orientation,
 crowd,
 relationship,
 goal,
 phone_use,
 urgency,
 novelty
)
```

人がスマホを見ていれば周囲へのattentionが落ちる。

---

# 17. Conversation — 内容より「誰と、いつ、どれだけ」が重要

LLM conversation textはデモで目立つ。

しかし社会シミュレーションではまず、

- 会話開始率
- 応答率
- ターン数
- duration
- known vs stranger
- age mix
- location
- group size
- emotional valence
- repetition
- interruption

の分布が現実的である必要がある。

---

## 17.1 現在の課題

`Agent`には `_reply_to`, `conv_turns_left`, cooldownがある。

「話しかけられた→必ず返答」という思想は、LLM starvation対策としては分かるが、人間としては強すぎる。

現実では、

- 聞こえない
- 無視する
- 会釈だけ
- 急いでいる
- social anxiety
- stranger avoidance

がある。

---

## 17.2 Replyを二段階にする

まず**behavioral responseは必ず発生**:

```text
acknowledge
ignore
short_reply
full_reply
```

そのうちfull_replyだけLLM。

これなら「返答飢餓」をなくしつつ、人間的な非応答も表現できる。

---

# 18. Social network — 関係の量と質

`relations.py`には、

- closeness
- acquaintance/friend/close friend
- negative interaction
- decay
- reputation
- group/faction

がある。

本選候補ではrelations + DunbarもON。

方向はかなり良い。

## 18.1 問題: closenessが「会話スコア」に寄りすぎる

実際の関係は、

- interaction duration
- intimacy
- reciprocity
- support
- shared activity
- conflict
- relationship role
- absence
- disclosure

等で変わる。

---

## 18.2 Social capacity

Miritello et al. 2013の約2,000万人×19か月通信データでは、個人がactiveに維持できるtieには有限のcommunication capacityがあり、tie activation/deactivationのバランスがある。

したがって、

```python
social_attention_budget_i
```

を導入。

親しい人が増えれば、全員と毎日同じ親密度を維持できない。

### 実装

毎日:

```text
available_social_minutes
→ tiesへ配分
→ contact不足のtieは自然減衰
```

これだけでsocial networkがかなり人間的になる。

---

# 19. 関係の形成

初期friend graphだけに依存すると、創発ではなく初期グラフが結果を支配する。

## 19.1 Endogenous formation

関係形成hazard:

```text
P(new tie) =
f(
 repeated co-presence,
 shared organization,
 mutual friends,
 shared interests,
 interaction valence,
 age similarity,
 spatial proximity
)
```

### triadic closure

```text
A friend B
B friend C
→ A-C interaction probability ↑
```

を軽量に入れる。

---

# 20. Group interaction — 二者会話だけでは都市社会にならない

現実は、

- 3人の友達
- 同僚グループ
- 家族
- 会議
- 飲み会
- 学校
- 行列
- イベント

などhyperedge interactionが多い。

## 20.1 Lightweight group object

```python
InteractionEpisode:
    participants: tuple[int, ...]
    start_step
    end_step
    context
    dominant_speaker
    topic
    valence
```

全員分のLLMを呼ばない。

### 発言者選択

turn-taking policy + salience。

### listener update

同じ発話をgroup全員へmemory/heardとして流す。

---

# 21. 日本の社会接触へ接地

日本の職場でウェアラブルを使った研究では、複数企業の従業員についてface-to-face interaction networkが長期間計測されている。

この種のデータから、

- degree
- clustering
- interaction duration
- repeated contacts
- team structure

を較正ターゲットにできる。

少なくとも「会話回数」という単一指標ではなく、

```text
contact duration distribution
degree distribution
clustering
reciprocity
tie persistence
```

を見るべき。

---

# 22. Household / family — 大幅強化が必要

家庭は社会シミュレーションの最大のhidden network。

現在のhouseholdは存在しても、帰宅後覚醒時間が不足すると機能しない。

## 22.1 Household joint decisions

- dinner
- shopping
- escort child
- shared leisure
- care
- household chores
- sleep disruption
- money transfer

を共同制約にする。

### 重要

「夫婦2人がそれぞれ独立したLLMとして勝手に夕食場所を決める」のは不自然。

---

## 22.2 Shared household state

```python
household:
    food_stock
    shared_budget
    chores
    shared_schedule
    dependents
    home_events
```

全てを実装する必要はない。

P0:

- shared dinner
- partner/child co-presence
- evening conversation
- simple shared budget

---

# 23. 年齢・ライフステージ

persona v2で0–14歳等が入ることは大きな改善。

しかし「年齢分布が正しい」だけでなく、

**年齢が行動を変える必要がある。**

### 子ども
- school
- parent escort
- curfew-like constraints
- phone/social patterns
- spending constraints

### 学生
- timetable
- club/social
- part-time

### working age
- commute/work
- family care

### elderly
- lower mobility radius
- health
- daytime activity
- social isolation risk

### validation

社会生活基本調査・PTをage bandで直接比較。

---

# 24. Work — 組織が行動へ効く必要がある

組織台帳とworkplace bindingは強み。

次は、

- role
- shift
- manager/peer
- workload
- break
- overtime
- workplace social network

へ接続。

## 24.1 “working”を黒箱にしすぎない

10分stepの全勤務中に具体タスクをシミュレートする必要はない。

しかし、

```text
focused work
meeting
break
customer interaction
idle
social chat
```

程度のmacro-stateは必要。

これが、

- fatigue
- social relation
- phone use
- reflection
- stress

へ影響する。

---

# 25. Media / SNS — 現実の利用時間へ合わせる

本選候補では `media.enabled: true`。

しかし既存リポジトリの実測では家庭mediaが少ない。

総務省「令和6年度情報通信メディアの利用時間と情報行動に関する調査」では、全年代の平均で平日のインターネット利用は181.8分、休日183.7分と報告されている。

したがってmediaは「ニュースイベントを受ける装置」だけでなく、

**人間の1日の大きな時間占有行動**

である。

---

## 25.1 Media session model

```text
phone_check: 1–5 min
social_scroll: 5–30
video: 10–90
message: burst
news: short
game: session
```

10分stepでもsession stateを持てる。

### age-specific

総務省の年代別集計を使う。

### context

- commute
- home evening
- work break
- waiting
- meal
- bedtime

---

## 25.2 Feed exposure

SNSを単純broadcastにしない。

```text
exposure_score =
follow_relation
+ interest
+ popularity
+ recency
+ algorithmic_noise
```

ただし本選で複雑な推薦AIは不要。

---

# 26. 情報伝播 — 「聞いた」から「信じる」まで

情報伝播は、

```text
exposure
→ attention
→ comprehension
→ credibility
→ memory
→ belief update
→ share
```

を分ける。

LLMに全部任せると不安定。

### lightweight states

```text
familiarity
credibility
alignment
emotion
source_trust
```

LLMは曖昧な解釈や自然言語反応。

---

# 27. Opinion dynamics — FJだけでは規範を表しきれない

AgentにはFriedkin–Johnsen型opinionがある。

これは集団意見のmacro dynamicsには使いやすい。

しかし人間の社会規範は、

- descriptive norm（みんな何をしている）
- injunctive norm（何をすべきと思われている）
- reference group
- sanction
- reputation
- conformity
- reactance

を含む。

---

## 27.1 Norm state

topicごとに:

```python
perceived_descriptive_norm
perceived_injunctive_norm
personal_attitude
public_expression
```

を分ける。

これにより、

**本音と公的発言が違う**

状態を表現できる。

社会現象として重要。

---

# 28. Culture / Japanese behavior

LLMはinternet textから学習しており、日本社会を均等に代表するわけではない。

さらにpersonaに日本語名・職業を与えたからといって、

- stranger interaction
- indirect refusal
- hierarchy
- service norms
- workplace speech
- family role
- privacy distance

まで自動で現実的になる保証はない。

## 28.1 Japanese Behavioral Battery

LLMをsimulationに入れる前に、独立テスト。

例:

```text
駅で知らない人に話しかけられた
上司から急な残業を頼まれた
友人から飲みに誘われた
財布が厳しいのに新商品を見た
混雑した電車
店員のミス
SNSで意見が対立
```

同一scenarioを、

- age
- gender
- job
- income
- relationship
- model

で数百〜数千回。

### 比較

可能なら日本のsurvey/実験研究。

無ければ最低でも、
- model間
- prompt間
- temperature間
の感度を測る。

---

# 29. LLM fidelity — personaだけを信用しない

Park et al. 2024/2025の1,052人agent研究が重要なのは、

**demographic vignetteよりinterview-conditioned agentsの方が個人再現に優れた**

点。

このsimのpersona poolは統計的一貫性を作る上では有用。

しかし、

```text
age + job + traits + generated persona
```

は特定個人のlife historyではない。

したがって、本プロジェクトではindividual twinではなく、

**population behavior distribution**を狙う。

---

# 30. Personaに「人生履歴」を少量追加する

25万人全員に巨大文章は不要。

structured life context:

```json
{
  "household_role": "...",
  "recent_life_event": "...",
  "financial_pressure": 0.4,
  "job_satisfaction": 0.7,
  "social_support": 0.5,
  "commute_burden": 0.3,
  "local_familiarity": 0.8
}
```

程度でよい。

これが、

- goal
- mood
- risk
- leisure
- consumption
- social behavior

に使える。

---

# 31. 記憶 — 現行は強い

`agents/memory.py` は本プロジェクトの強い部分。

- buffer
- episodes/day summaries
- beliefs
- relations
- ACT-R
- power-law forgetting
- activation threshold
- fan effect
- retrieval strengthening

がある。

本選候補ではACT-R ON。

---

## 31.1 最大の改善点: semantic relevance

default retrievalではembeddingの代わりに語包含でrelevance代理する部分がある。

日本語では表記ゆれが多い。

```text
渋谷駅
駅前
ハチ公前
あの場所
さっきの駅
```

を同じcontextと認識しにくい。

### 14日案

重いembedding serverを追加しなくても、

- entity IDs
- person IDs
- place IDs
- topic IDs

をmemory metadataに持つ。

```python
Episode.entities = {
  "people": [...],
  "places": [...],
  "topics": [...]
}
```

relevanceをID overlapで計算。

自然文embeddingより決定論・高速。

---

# 32. Memory capacity

`buffer_cap=30`, `store_cap=120` のような上限は計算上必要。

ただし全員一律は不自然。

### 個人差

- age
- salience
- cognitive style

で細かく変える必要は薄い。

むしろ重要なのは、

**何が残るか**

。

emotion/salienceがimportanceへ入っている現在の設計を活かす。

---

# 33. Learning — 10日でも起きる変化を増やす

10日では人生が根本的に変わる必要はない。

しかし、

- familiar route
- store preference
- relationship
- source trust
- habit
- opinion
- daily timing
- short-term goals

は10日で十分変わる。

### 全てに共通する更新則

```text
prior
+ experience
→ posterior/preference
```

を持つ。

---

# 34. Consumption / economy

現在のeconomyは保存則が強い。

一方、人間行動としての消費は粗いところがある。

`values.py`にはカテゴリごとの固定cost例がある。

- food 900
- social 1200
- shopping 2500
- etc.

これは行動を生かすにはよいが、現実再現には弱い。

---

## 34.1 家計調査を使う

総務省家計調査2025には、

- 世帯属性
- 年齢
- 所得
- 品目
- 購入頻度

の統計がある。

特に**単身世帯**は渋谷の行動較正に重要。

### calibration

Agentを、

```text
age × income × household type
```

で分け、

- food
- eating out
- transport
- clothing
- recreation
- communication

等のspend distributionを合わせる。

---

## 34.2 Price distribution

店舗カテゴリごとに価格帯を持つ。

```text
convenience meal ~ distribution
cafe ~ distribution
restaurant ~ distribution
apparel ~ distribution
```

固定中央値を少し崩す。

---

# 35. Risk / deviance / crime

freedom.p2でdevianceがONなのは創発上面白い。

ただしLLMはalignmentにより、
人間よりprosocial/規範遵守へ偏る場合がある。

したがって犯罪・逸脱をLLM任せにすると、

**モデルのalignment policyを「人間の道徳性」と誤認する**可能性がある。

---

## 35.1 Risk propensity + opportunity

```text
behavior =
risk_tolerance
× economic pressure
× grievance
× opportunity
× peer norm
× perceived enforcement
```

の軽量behavioral layerを通す。

LLMは「どう考えたか・何をするか」の自然言語選択。

---

# 36. Health and behavior

health ONは良い。

次に必要なのはhealthをイベント終端にせず、

```text
health
→ mobility
→ work absence
→ money
→ social contact
→ mood
→ future health
```

へ閉じること。

### audit
全health stateが、
- routine
- work
- consumption
- cognition
へ本当に流れているか確認。

---

# 37. Human error

人間は間違える。

LLMはとくに日常タスクで「有能すぎる」可能性。

軽量なerrorを導入。

- forget item
- miss train
- wrong turn
- misremember
- arrive late
- abandon plan
- overlook message

ただしランダムノイズだけにしない。

```text
error probability ↑:
fatigue
stress
multitasking
crowd
unfamiliar place
```

---

# 38. 10分stepの限界

10分stepは大規模都市には合理的。

しかし、

- 30秒会話
- 信号
- 駅乗換
- 行列
- 一時的な接触

は潰れる。

### 解決

global dtを1分にする必要はない。

**event-time substep**。

```text
通常: 10 min
interaction episode内部: 1 min equivalent timestamps
```

observerだけ細粒度を持つ方法でもよい。

---

# 39. 人間の行動分布を直接合わせる — 最重要新規サブシステム

新規:

```text
src/society/validation/
scripts/behavior_validation.py
```

---

## 39.1 Ground Truth Registry

```yaml
targets:
  time_use:
    source: stat_japan_2021
    dimensions:
      - age
      - sex
      - employment
      - weekday
  mobility:
    source: tokyo_pt
  media:
    source: soumu_media_2024
  spending:
    source: family_expenditure_2025
  health:
    source: national_health_nutrition_2024
```

---

# 40. 社会生活基本調査を正典にする

総務省統計局「2021年社会生活基本調査」は約19万人を対象とし、

- 1日のtime use
- leisure
- 詳細行動分類
- 年齢等属性

を持つ。

このsimの**人間行動validationの正典**にすべき。

### 比較するもの

15分/30分bucketで:

```text
sleep
personal care
meal
commute
work
study
housework
childcare
shopping
move
TV/media
rest
social
hobby
sports
volunteer
```

---

# 41. Person Trip調査を正典にする

東京圏PT / 全国都市交通特性調査から、

- 外出率
- trips/person
- purpose
- mode share
- trip length
- duration
- age
- employment
- departure time

を比較。

**ODだけでは不十分。**

人間行動の条件付き分布が重要。

---

# 42. Media validation

総務省情報通信政策研究所のmedia surveyを利用。

比較:

- internet minutes/day
- TV
- social media
- video
- email
- mobile device
- age band
- weekday/weekend
- time band

---

# 43. Consumption validation

家計調査:

- household type
- income
- age
- category
- purchase frequency

へ比較。

---

# 44. Health validation

厚労省「国民健康・栄養調査」:

- meal
- physical activity
- sleep
- alcohol
- smoking
- health status

をbehavior targetに。

---

# 45. Validation metrics

単純meanだけではダメ。

## distribution distance

- MAE
- RMSE
- Jensen-Shannon divergence
- Wasserstein distance
- KS statistic

## conditional

```text
age × time
occupation × time
weekday × activity
income × consumption
age × mobility
```

## sequence

- transition matrix
- activity n-gram
- trip chain
- dwell duration

## network

- degree
- weighted degree
- clustering
- assortativity
- reciprocity
- tie persistence
- inter-contact time

---

# 46. CalibrationとValidationを絶対に分ける

### Calibration set
パラメータ調整に使う。

### Validation set
最後まで見ない。

例:

```text
CAL:
平均睡眠時間
平均通勤
mode share
平均internet時間

HOLDOUT:
21時在宅率
age-specific activity profile
trip-chain distribution
social contact network
spending category mix
```

holdoutまで合えば、主張が一気に強くなる。

---

# 47. Behavioral Fidelity Score

審査用に1つの指標へまとめてもよい。

ただし内部では分解。

```text
BFS =
w_time * TimeUseScore
+ w_mobility * MobilityScore
+ w_social * SocialScore
+ w_media * MediaScore
+ w_economy * EconomyScore
+ w_health * HealthScore
```

各score 0–100。

**総合点だけ見せずレーダーチャートも出す。**

---

# 48. High-Fidelity Shadow Simulation — GPUを使う最大の方法

これは本書の最重要提案の1つ。

25万人全員を最高解像度LLMで動かすのは難しい。

そこで同じ世界状態で、

### Main
250k agents  
adaptive LOD

### Shadow
代表5k〜20k agents  
**ほぼ全decision pointでLLM**

を並行/短期で走らせる。

---

## 48.1 何を比較するか

同じ初期状態・eventに対して、

```text
low-LOD decision
vs
high-LLM decision
```

を比較。

- action agreement
- destination class
- conversation decision
- plan revision
- spending
- emotion response

---

## 48.2 意義

これにより、

> 「LLM callを何回にすれば十分か」

を勘で決めなくてよい。

LLM budgetを増やし、

**behavioral convergenceが飽和する点**

を探す。

---

# 49. Behavioral Distillation — 時間が許せば非常に強い

Shadowのhigh-LLM decisionを集める。

```text
state/context → LLM action
```

datasetにする。

次に軽量surrogate:

- gradient boosting
- small MLP
- table / conditional distribution

で近似。

これをbackground agentへ使う。

### 注意

これは「人間」を蒸留するのではなく**LLM policyを蒸留**する。

したがってhuman ground truth validationは別途必要。

ただしGPUによる成果として非常に説明しやすい。

---

# 50. Model Battery — Qwen 8Bをそのまま信用しない

本番候補モデルについて、

### Battery A: everyday choice
### Battery B: social interaction
### Battery C: altruism/self-interest
### Battery D: Japanese social norm
### Battery E: memory consistency
### Battery F: plan realism
### Battery G: emotional reaction

を作る。

各scenarioを数百sample。

---

## 50.1 比較モデル

可能な範囲で:

- Qwen 8B
- Qwen larger
- alternative open model
- one stronger reference model

### 選定基準

「ベンチマークIQ」ではなく、

**human behavior distributionへの距離**。

---

# 51. LLM bias audit

見る項目:

- too cooperative
- too polite
- too rational
- too risk-averse
- too verbose
- too consistent
- too knowledgeable
- too morally aligned
- demographic stereotypes
- refusal rate
- repeated phrase

これを`behavioral_model_card.json`として保存。

---

# 52. Prompt design

promptに、

> 「人間らしくしてください」

と書きすぎない。

それ自体がモデルの“人間らしさ演技”を誘発する。

渡すべきは具体的状態。

```text
あなたは...
今...
所持金...
疲労...
相手...
予定...
直近の出来事...
知っている範囲...
```

### 知識制約

Agentが知らないことをpromptに入れない。

これはworld fidelityより**behavior fidelity**の中心。

---

# 53. Information boundary

人間はglobal stateを知らない。

Agent promptへ入る情報を監査。

```text
Global truth
↓ perception
Local observation
↓ memory
Believed world
↓ decision
Action
```

Global truthを直接LLMへ渡すと超人になる。

---

# 54. Perception errors

軽量に、

- crowded sceneで見落とす
- distant personを認識しない
- rumor sourceを忘れる
- priceを概算する

などを入れる。

完全なsensor simulationは不要。

---

# 55. 社会規範の内生化

現在norm関連機構は存在する。

次は規範を世界側が固定するのではなく、

```text
observed behaviors
→ perceived norm
→ behavior
→ more observations
```

へ。

これこそ創発。

---

# 56. Reputation

relationsのreputationは良い。

ただし「話した回数」だけでなく、

- trust
- reliability
- helpfulness
- norm violation
- public visibility

へ分解する余地。

14日では、

```text
trust
visibility
```

2軸で十分。

---

# 57. 役割・制度と人間行動

人は同じ性格でも、

```text
customer
employee
parent
friend
stranger
citizen
```

で行動が変わる。

Agentにrole contextを明示。

### situation role

```python
current_role = infer_role(context)
```

LLM promptへ自然文で渡す。

---

# 58. 同じ人の一貫性と状況依存性を両立する

良いhuman modelは、

- 全状況で同じ性格ではない
- 毎回ランダムでもない

必要がある。

### decomposition

```text
behavior =
stable trait
+ role
+ relationship
+ state
+ habit
+ context
+ noise
```

この分解をログに残す。

---

# 59. Trait validity

現在のtraitsが行動へどう影響するかを測る。

例:

```text
risk_tolerance ↑
→ risky actions実際に増える?

nfc ↑
→ deliberate cognition増える?

internal_locus ↑
→ autonomy action増える?
```

### Trait-behavior monotonicity test

1000 agentsでcounterfactual trait sweep。

意図した方向が出ないtraitは削るか配線修正。

---

# 60. 人格多様性の測定

persona textが違うだけでは多様性ではない。

見る:

- action entropy across agents
- conditional entropy given context
- destination diversity
- language diversity
- social strategy diversity
- schedule diversity
- spending diversity

### collapse detector

同じcontextで70%以上が同じ行動なら警告。

ただし通勤など本来同じものは除外。

---

# 61. 反応の多様性

同じ雨でも、

- 帰る人
- 傘を買う人
- カフェに入る人
- 気にしない人

がいる。

**aggregate response elasticity**をデータへ合わせる。

---

# 62. Event response validation

政策や事件の反応を現実データで完全検証できなくても、

最低限、

```text
shock magnitude
→ behavioral change
```

が単調・妥当か確認。

---

# 63. Emergenceとartifactを区別する

創発らしいものを見つけたら、

### Counterfactual A
LLM OFF

### B
social network OFF

### C
memory OFF

### D
habit OFF

### E
media OFF

### F
same world, different seed

を比較。

「創発」がどの機構から出たかを示す。

---

# 64. Causal provenance

既存のprovenance/loggerを活かす。

各重要行動に:

```json
{
  "action": "...",
  "trigger": "...",
  "state_before": {...},
  "decision_mode": "habit|rule|micro_llm|deep_llm",
  "llm_call_id": "...",
  "state_after": {...}
}
```

を持たせる。

審査デモで、

> 「この人がなぜここへ来たか」

を説明できる。

---

# 65. Observerは行動を変えない

既存方針を絶対維持。

validation用loggerを追加しても、Agent decisionでそれを読まない。

---

# 66. 本選候補configのBehavior Readiness

現在確認できるON:

- `media.enabled: true`
- `needs.enabled: true`
- `affect.enabled: true`
- `inner_life.enabled: true`
- hobbies leisure bias
- drive boredom
- drive drift
- routine stochastic
- conversation
- planning.day_plan
- memory.agentic_pull
- memory.actr
- worldview
- relations
- dunbar
- endogenous relations
- freedom.open_actions
- move_home
- buy
- study
- partnership
- deviance
- health
- fatigue
- starvation observer

これはかなり攻めた設定。

一方で:

- cognition fire / watch / engagedはまだコメントアウト
- sleep task rewrite OFF
- persona pool v2は切替待ち
- vLLM backendはfinals_observeへ直結していない

という重要な未確定がある。

---

# 67. 「全機能ON」は正解ではない

人間忠実度の観点では、

> 実装済み機能を全部ON

より、

> 現実データで改善した機能だけON

が正しい。

### Gate

各機能:

```text
OFF
vs ON
```

で、

1. human validation score
2. compute
3. stability

を見る。

human scoreが悪化したfeatureは本選から外す。

---

# 68. 14日ロードマップ — 人間行動版

以下は「環境構築」ではなく、人間忠実度だけを基準にした優先順。

---

## Day 1 — Behavioral baselineを測る

**実装前に測る。**

10k × 1 dayまたは利用可能な既存runから、

- time use
- home rate
- trip metrics
- media
- social contacts
- LLM calls
- cognition coverage
- activity transitions

を出す。

成果:

```text
behavior_baseline.json
behavior_baseline.html
```

---

## Day 2 — 家庭生活を修正

- enter_home ≠ sleep
- HOME_AWAKE
- evening activities
- shared dinner
- media
- chores
- hobby
- household interaction

これが最優先。

---

## Day 3 — Human Time-Use Validator

社会生活基本調査と比較。

- age
- employment
- weekday
- 15/30min time bands

自動score化。

---

## Day 4 — Habit learning

Contextual Habit Memory。

- repeated context-action
- strength
- decay
- automatic action
- deliberate override

---

## Day 5 — Physiology

- hunger
- sleep pressure
- fatigue integration
- meal trigger
- bedtime hazard

---

## Day 6 — Cognition.fire + microthought

- fire gate
- micro-cognition tier
- reply priority
- cognition debt
- queue fairness

---

## Day 7 — Adaptive LLM Budget

7GPU実測から、

- req/s
- token/s
- queue
- step time

を用いbudget動的化。

---

## Day 8 — Social realism

- social attention budget
- no/short/full reply
- interaction duration
- endogenous tie formation
- triadic closure

---

## Day 9 — Media / SNS

総務省調査へtime-use合わせ。

- session
- age effect
- commute/home contexts

---

## Day 10 — Mobility validation

PT + mobility literature。

- trip rate
- mode
- duration
- EPR
- familiar place capacity
- mobility entropy

---

## Day 11 — Consumption + lifestyle validation

家計調査 + health/nutrition。

- consumption categories
- meal
- sleep
- activity

---

## Day 12 — LLM Behavioral Battery

Qwen等を実験。

- persona sensitivity
- social behavior
- Japanese scenarios
- action diversity
- model bias

---

## Day 13 — Shadow high-cognition run + ablation

代表subpopulation:

- low LOD
- high LLM
- no memory
- no habit
- no social
- multiple seeds

---

## Day 14 — Freeze / evidence package

作る:

```text
behavior_fidelity_report.json
behavior_fidelity_report.html
radar.svg
timeuse_comparison.png
mobility_comparison.png
social_network_comparison.png
agent_causal_trace.json
```

---

# 69. P0 — 本番前に絶対検討するHuman Behavior blockers

## HB-P0-01
**帰宅=睡眠を分離**

## HB-P0-02
**Persona v2 + age/life-stage behavioral wiring**

## HB-P0-03
**cognition.fireを実測評価して可能ならON**

## HB-P0-04
**Adaptive LLM budget**

## HB-P0-05
**Cognition debt / fairness**

## HB-P0-06
**microthought tier**

## HB-P0-07
**Human time-use validation**

## HB-P0-08
**Mobility validation**

## HB-P0-09
**Social contact validation**

## HB-P0-10
**LLM behavioral battery**

## HB-P0-11
**Contextual habit learning**

## HB-P0-12
**hunger + sleep pressure**

---

# 70. P1 — かなり価値が高い

- social capacity
- tie formation
- triadic closure
- group interactions
- household coordination
- media sessions
- spending calibration
- action tendencies
- dynamic goals
- memory entity indexing
- choice-set restriction
- human error
- norm perceptions
- role context

---

# 71. P2 — 余力があれば

- full hypergraph social model
- detailed emotion taxonomy
- sophisticated household finance
- longitudinal life-course
- skill learning
- citywide fine-grained indoor behavior
- complex recommender
- high-resolution language sociolinguistics

---

# 72. Acceptance Criteria — 「人間行動が現実的」と言うための最低条件

## A. Time use

- activity minutes/dayの主要カテゴリが現実と近い
- 21時在宅率の明白な乖離が解消
- return-home → sleep gapが非ゼロで現実的
- age/employment別profileが合理的

## B. Mobility

- trips/person
- mode split
- trip duration
- destination revisit
- unique place count
- familiar set
- time-of-day OD

## C. Social

- contact degree
- interaction duration
- tie persistence
- closeness distribution
- clustering
- stranger/friend interaction mix

## D. Cognition

- unique agents receiving LLM
- calls/person/day distribution
- starvation ≈ 0
- cognition not concentrated excessively
- deep cognition triggered by high-salience states
- micro-cognition widely distributed

## E. Daily behavior

- meal timing
- sleep
- media
- leisure
- household time

## F. Diversity

- behavior does not collapse to identical templates
- demographics/traits actually correlate with relevant behaviors

## G. Robustness

- at least 2+ seeds
- major conclusions survive seed
- LLM model sensitivity reported
- holdout validation reported

---

# 73. 「人間の社会を完璧に再現した」に最も近い発表表現

避ける:

> 25万人のAIが現実の人間を完全再現します。

より強く、科学的に defensible:

> **実在の渋谷を基盤に、25万人規模のエージェントが生活する生成型社会シミュレーションを構築しました。単にLLMに人格を与えただけではなく、生活時間、移動、習慣、記憶、感情、社会関係、情報行動、消費などを独立した実データへ接地し、現実との乖離を定量的に測定しています。高解像度LLM認知は必要な意思決定点へ動的に割り当て、日常の自動行動と熟考を分離しています。**

さらにvalidationが成功したら:

> **較正に使っていない行動指標でも現実の分布を再現できた。**

これが非常に強い。

---

# 74. ハッカソンで見せるべきHuman Behavior Demo

## Scene 1: 1人を見る

画面:

```text
17:40 退勤
18:07 電車
18:34 買物
19:02 帰宅
19:15 家族と夕食
20:03 SNS
20:26 友人DM
20:40 散歩
21:18 入浴
22:10 microthought
23:31 就寝
```

クリックすると、

```text
habit
need
social
LLM
```

どのdecision modeだったか見える。

---

## Scene 2: 1万人を見る

現実 vs sim:

- time use curves
- home presence
- commute
- media
- mobility

を重ねる。

---

## Scene 3: 25万人を見る

都市全体の、

- crowd
- social
- economy
- information

が動く。

---

## Scene 4: 介入

1つだけ世界条件を変える。

そして、

> **人がどう行動を変えた結果、都市全体がどう変わったか**

をcausal traceで見せる。

---

# 75. Claude Codeへの実装方針

Claudeには「この文書を全部一気に実装して」と渡さない。

以下の順で渡す。

```text
1. 現HEADを読む
2. 既存機構と重複していないか検索
3. 各issueごとに現状のwriter/reader/config/testを報告
4. 人間忠実度validation targetを先に定義
5. 最小実装
6. unit test
7. behavioral smoke
8. OFF/ON comparison
9. validation score
10. 次issue
```

---

# 76. Claude向け最上位指示

```text
このリポジトリでは「機能数を増やすこと」を目標にしない。

最優先は、現実の人間行動との一致度を高めることである。

各実装について必ず:
- 現行挙動
- 現実の根拠
- 仮説
- 変更コード
- 因果経路
- 計算量
- 現実比較指標
- regression test
- OFF/ON実測
を示すこと。

既に同等機構がある場合、新規モジュールを作らず既存機構を接続・較正する。

「文献に書いてあったから係数を0.4にした」は不可。
値は可能なら実データへ較正し、無理ならuncalibrated parameterとして明示する。

LLMを増やす際は:
- 長文callを無差別に増やさない
- cognition LODを使う
- GPU idleを減らす
- unique agent coverageを測る
- reply starvationをゼロに近づける
- high-resolution shadow runと比較する

人間行動を変えるstateにはwriter/reader/persistence/log/validationの5点を必ず確認する。
```

---

# 77. 推奨Issue一覧

### ISSUE-HB-001 — Home Awake State
帰宅と就寝を分離。

### ISSUE-HB-002 — Time Use Validator
社会生活基本調査比較。

### ISSUE-HB-003 — Contextual Habit Learning
習慣の学習。

### ISSUE-HB-004 — Hunger/Sleep Pressure
基本身体欲求。

### ISSUE-HB-005 — Cognition Fire Production Gate
fire実装接続と実測。

### ISSUE-HB-006 — Adaptive LLM Budget
GPU-aware。

### ISSUE-HB-007 — Cognition Debt
認知公平性。

### ISSUE-HB-008 — Microthought
低コスト日常思考。

### ISSUE-HB-009 — Social Attention Capacity
有限社会容量。

### ISSUE-HB-010 — Response Type
ignore/ack/short/full。

### ISSUE-HB-011 — Endogenous Tie Formation
共在・共通友人。

### ISSUE-HB-012 — Group Interaction
hyperedge episode。

### ISSUE-HB-013 — Media Session Calibration
総務省調査。

### ISSUE-HB-014 — Mobility Fidelity Suite
PT/EPR metrics。

### ISSUE-HB-015 — Consumption Calibration
家計調査。

### ISSUE-HB-016 — Behavioral LLM Battery
日本人行動bench。

### ISSUE-HB-017 — High Fidelity Shadow
代表subpopulation。

### ISSUE-HB-018 — State Causality Audit
飾りstate検出。

### ISSUE-HB-019 — Entity-indexed Memory
人/場所/topic ID retrieval。

### ISSUE-HB-020 — Dynamic Goals
経験から人生目標。

### ISSUE-HB-021 — Household Joint Activity
共同生活。

### ISSUE-HB-022 — Norm Perception
descriptive/injunctive分離。

### ISSUE-HB-023 — Action Tendencies
approach/avoid/affiliate/withdraw。

### ISSUE-HB-024 — Human Error
疲労等に依存したミス。

---

# 78. 今回の監査で最も重要な10個の結論

1. **このsimulationは既に単純なLLM agent sandboxではない。**
2. **EPR、ACT-R、day-plan、affect、needsなど方向性はかなり良い。**
3. しかし**機構の存在 ≠ 人間行動の再現**。
4. 最大の不足は**現実行動データへの体系的validation**。
5. 現在の**帰宅=睡眠**は人間社会再現に重大。
6. **習慣を実行する仕組みはあるが、習慣を形成する学習が弱い。**
7. **LLM cognition密度は増やす価値が高い。**
8. ただし毎step長文LLMではなく、**automatic / micro / deliberate / deep** の4層がよい。
9. `cognition.fire`はこの設計の中心で、計算ゲートを通れば本番投入価値が高い。
10. 最後に勝つのは「25万人」という数字だけではなく、**25万人の行動が現実データとどれだけ一致したかを証拠として見せられること**。

---

# 79. 参考文献・データソース

以下は本監査の主要な一次/公的資料。実装時は各データの利用条件・対象範囲・調査年を確認すること。

## Human time use / Japan

1. Statistics Bureau of Japan, **2021 Survey on Time Use and Leisure Activities**  
   https://www.stat.go.jp/english/data/shakai/  
   - 約19万人、日々のtime allocation、leisure、詳細行動分類。
   - 本simulationのtime-use validationの最優先正典。

2. Statistics Bureau, Outline of the 2021 Survey  
   https://www.stat.go.jp/english/data/shakai/2021/gaiyo.htm

3. Statistical tables  
   https://www.stat.go.jp/english/data/shakai/2021/r3kekka.html

## Mobility / transport

4. 国土交通省, **全国都市交通特性調査**  
   https://www.mlit.go.jp/toshi/tosiko/toshi_tosiko_tk_000033.html

5. 集計データ  
   https://www.mlit.go.jp/toshi/tosiko/toshi_tosiko_fr_000024.html

6. González, M. C., Hidalgo, C. A., Barabási, A.-L. (2008).  
   **Understanding individual human mobility patterns. Nature 453, 779–782.**  
   https://doi.org/10.1038/nature06958

7. Song, C., Koren, T., Wang, P., Barabási, A.-L. (2010).  
   **Modelling the scaling properties of human mobility. Nature Physics 6, 818–823.**  
   https://doi.org/10.1038/nphys1760

8. Alessandretti, L. et al. (2018).  
   **Evidence for a conserved quantity in human mobility. Nature Human Behaviour 2, 485–491.**  
   https://doi.org/10.1038/s41562-018-0364-x

9. Pappalardo, L. et al. (2015).  
   **Returners and explorers dichotomy in human mobility. Nature Communications 6, 8166.**  
   https://doi.org/10.1038/ncomms9166

## Habit / cognition

10. Wood, W., Rünger, D. (2016).  
    **Psychology of Habit. Annual Review of Psychology 67, 289–314.**  
    https://doi.org/10.1146/annurev-psych-122414-033417

11. Smallwood, J., Schooler, J. W. (2015).  
    **The Science of Mind Wandering: Empirically Navigating the Stream of Consciousness. Annual Review of Psychology 66, 487–518.**  
    https://doi.org/10.1146/annurev-psych-010814-015331

12. Lemyre, A. et al. (2020).  
    **Pre-sleep cognitive activity in adults: A systematic review. Sleep Medicine Reviews 50, 101253.**  
    https://doi.org/10.1016/j.smrv.2019.101253

## Social networks / contact

13. Miritello, G. et al. (2013).  
    **Limited communication capacity unveils strategies for human interaction. Scientific Reports 3, 1950.**  
    https://doi.org/10.1038/srep01950

14. 日本企業のface-to-face networkを用いた研究  
    **Universal association between depressive symptoms and social-network structures in the workplace.**  
    https://pmc.ncbi.nlm.nih.gov/articles/PMC9205889/

15. 日本の地域コミュニティでのlongitudinal wearable proximity研究  
    https://pmc.ncbi.nlm.nih.gov/articles/PMC8908302/

## LLM / Generative agents

16. Park, J. S. et al. (2023).  
    **Generative Agents: Interactive Simulacra of Human Behavior.**  
    https://arxiv.org/abs/2304.03442

17. Park, J. S. et al. (2024).  
    **Generative Agent Simulations of 1,000 People.**  
    https://arxiv.org/abs/2411.10109

18. Wang, Z. et al. (2023).  
    **Humanoid Agents: Platform for Simulating Human-like Generative Agents.**  
    https://arxiv.org/abs/2310.05418

19. Ma, J. (2026).  
    **Can Machines Think Like Humans: A Behavioral Evaluation of LLM Agents in Dictator Games.**  
    Cambridge / Voluntas.  
    - personaを付けるだけではhuman-like decisionにならないこと、
      model/prompt依存性が大きいことを示す比較対象。

## Media / information behavior

20. 総務省情報通信政策研究所  
    **情報通信メディアの利用時間と情報行動に関する調査**  
    https://www.soumu.go.jp/iicp/research/results/media_usage-time.html

21. 令和6年度調査公表  
    https://www.soumu.go.jp/menu_news/s-news/01iicp01_02000125.html

## Consumption

22. Statistics Bureau of Japan  
    **Family Income and Expenditure Survey — 2025 Yearly Average**  
    https://www.stat.go.jp/english/data/kakei/156n.html

23. One-person households, 2025  
    https://www.stat.go.jp/english/data/tanshin/et25.html

24. National Survey of Family Income, Consumption and Wealth  
    https://www.stat.go.jp/english/data/zenkokukakei/index.html

## Health / lifestyle

25. 厚生労働省  
    **令和6年 国民健康・栄養調査**  
    https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/kenkou/eiyou/r6-houkoku_00001.html

26. 調査概要  
    https://www.mhlw.go.jp/toukei/itiran/gaiyo/k-eisei_2.html

---

# 80. 最終提言

前回の環境・都市側改善と今回の人間行動側改善を合わせたとき、このプロジェクトの本当に強い形は、

```text
REAL CITY
  建物
  道路
  交通
  店舗
  組織
  天候
  制度
      ↓
REALISTIC HUMAN
  人口
  家庭
  仕事
  習慣
  身体
  計画
  感情
  注意
  記憶
  社会関係
  情報
  消費
  LLM認知
      ↓
INTERACTION
      ↓
EMERGENCE
      ↓
VALIDATION AGAINST REAL WORLD
      ↓
COUNTERFACTUAL
```

である。

**環境だけを精密にしても足りない。**  
**LLMだけを増やしても足りない。**  
**Agent数だけを増やしても足りない。**

必要なのは、

> **現実の環境の中で、現実の人間と似た制約・習慣・生活時間・認知・関係を持つagentが行動し、その集積が現実の都市統計へ戻ってくること。**

ここまで閉じたとき、このsimulationは単なるデモから、

> **「まだ存在しない社会状態を先に走らせる装置」**

へ近づく。

そしてハッカソンで最も説得力がある証拠は、派手な3Dだけでも、25万人という数字だけでもなく、

> **「このグラフが現実。このグラフがsimulation。これだけ一致した。そして条件を1つ変えると、この差が未来の候補として現れた。」**

を見せることである。
