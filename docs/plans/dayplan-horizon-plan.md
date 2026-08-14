# 日課計画の地平・昼寝・推論の時間集中(DPH) — 現状診断と設計案

> 入力: ユーザーの問い(2026-08-14)
> 「朝に一日のスケジュールを立てていると思うが、それは日をまたぐことでリセットされないか?
>  朝のスケジュール制定を起床時から次の睡眠時までの予定に変更したほうがいいかな? 昼寝の扱いは?
>  推論が特定の時間帯に集中するような実装になっていないか? またなっていたとしても、それによって
>  実験の結果が変わったり実験自体が止まるようなことを防げる設計になっているか?」
>
> **本書は診断+設計案であり、実装は 1 行も行っていない(ユーザー承認待ち)。**
> src / tests / conf は 1 バイトも触れていない。実測は mock ラン 2 本(§1.5)。
> **行番号は 2026-08-14 時点の作業ツリー**(HEAD `3a64044` + 未コミット差分)で検証した。
> 本書執筆中に別セッションが src / conf を編集しているため、**記号名(関数名・キー名)を一次の
> 参照とし、行番号は二次**として読むこと。

---

## 0. 一行の結論(4 つの問いへの直答)

| 問い | 答 | 一行根拠 |
|---|---|---|
| **① 日をまたぐとリセットされるか** | **Yes(本選 ON 経路では確実にリセットされる)** | `day_plan.py:1025-1029` が `plan["day"] != sim_min//1440` で計画を捨てる。実測: 深夜 0 時以降に実行された計画ブロックは **3 日ラン 4,888 件中 0 件**。一方、就寝は **61% が 0 時以降**。 |
| **② 起床→次の就寝へ変えるべきか** | **Yes。ただし「計画の地平」と「計画の再生成トリガ」は別問題で、両方直す必要がある** | 地平だけ延ばしても `_schedule_plan` の暦日ガード(`scheduler.py:947`)が残ると「1 暦日 1 計画」の制約が別の穴を開ける。§3.1 案 A+。 |
| **③ 昼寝の扱いは** | **昼寝の概念は存在しない(実装ゼロ)。ただし「昼寝が無い」より深刻なのは、就寝が `bedtime_min` 固定の帰宅トリガでしかなく、疲労・徹夜・二度寝が睡眠へ一切結線されていないこと** | `nap`/`昼寝`/`仮眠` の全文検索で該当機構ゼロ。`transit_interior.ACT_DOZE` は活動ラベルのみ(`sleeping` を立てない)。 |
| **④ 推論の時間集中はあるか / 止まらないか** | **集中は Yes(plan=04-12 時、reflect=22-03 時)。「止まる」は No(安全弁は多層で機能する)。しかし「歪む」は Yes** | 実測: plan 呼の 97% が 05-10 時、reflect 呼の 100% が 22-06 時。**この 2 つは LOD 予算の外**(`scheduler.py:2565,2581,2701` の 3 箇所しか `budget.take()` を呼ばない)。予算が binding するランでは**返答保証(reply)が 08-23 時に完全に 0 件へ落ち**、しかもその枯渇は L1 に 1 件も残らない。 |

---

## 1. 現状の正確な記述

### 1.1 計画のライフサイクル — 経路は 2 本ある

| | 旧経路(`planning.day_plan.enabled=false`・基底既定) | **day_plan v1**(`=true`・**本選 ON**) |
|---|---|---|
| 格納先 | `agent.day_plan`(平坦な list) | `agent._dayplan`(day 番号つき dict) |
| 生成 | `planning.py:183` `agent.day_plan = items` | `day_plan.py:984` `agent._dayplan = plan` |
| 時刻表現 | 帯ラベル `朝/昼/午後/夕方/夜`(`routine.py:477-488`) | 分 of day の `start`/`end`(`day_plan.py:490-495`) |
| **日境界の扱い** | **リセットしない**。翌朝の生成で上書きされるまで生き続ける。しかも `_time_band` は **0-5 時を「夜」に畳む**ので、未消化の「夜」予定は翌 0-5 時に消化されうる(=事実上 wake-to-wake) | **深夜 0 時に無条件失効**(`day_plan.py:1025-1029`) |
| 日跨ぎブロック | 概念なし | **表現不能**(§1.2) |

- **本選 conf は day_plan v1 が ON**: [`conf/finals_observe.yaml:400-405`](../../conf/finals_observe.yaml)(`enabled: true` / `use_contingency: true` / `boundary.enabled: true`)。したがって**ユーザーの懸念は本選経路にそのまま当たる**。
- 生成トリガは**起床イベント駆動で、絶対時刻のハードコードは 1 つも無い**:
  `_phase_wake_and_returns`([`scheduler.py:1079-1087`](../../src/society/engine/scheduler.py))が `wake_up` を出した直後に `_schedule_plan`([`:940-950`](../../src/society/engine/scheduler.py))が `plan_step = step+1` を予約 → `_phase_planning`([`:953-976`](../../src/society/engine/scheduler.py))が 1 呼だけ発行。来街者は `enter_area`(`:1118-1119`)でも予約される。
- **`plan_day` ガード**(`scheduler.py:947`): `agent.plan_day == sim_min//1440` なら再予約しない = **1 暦日 1 計画**。倒れて起きた・退院した・チェックアウトした等で同じ暦日に 2 回起きても 2 本目は立たない(`registry.py:716` が明記)。
- **`carry`(「昨日から気にしていること」)は機構としては書き込み専用**: `day_plan.py:975-976` で格納されるが、**世界の動きを決める側で読む行が 1 つも無い**。第93 バッチで `cont` が同じ状態(デッドデータ)から救出されたが、`carry`/`mood` は未救出。したがって「昨日からの持ち越し」は**機構としては存在しない**(LLM が前日の記憶をプロンプト経由で見ているだけ)。
  **★2026-08-14 追記**: 並行レーン G7(`observer.gt_extras`・**本選 conf で ON** = [`conf/finals_observe.yaml:835-837`](../../conf/finals_observe.yaml))が `plan_created` の payload へ `mood` / `carry` / ブロックの `with` を**記録として**足した([`observer/gt_extras.py`](../../src/society/observer/gt_extras.py) の穴①)。これで **「事後に読めない」は解消**したが、**「翌朝の計画がそれを読む」は依然として無い**(G7 は読み取り専用でプロンプトを 1 バイトも変えない)。P7 の判定は「観測の穴」から「**機構の穴のみ**」へ降格する。
- 修復不能時の階段: 前日計画(`_dayplan_prev`)→ 職業別骨格(`skeleton`)([`day_plan.py:951-971`](../../src/society/cognition/day_plan.py))。**世界は止まらない**。
- 日中の再計画(`_replan`, [`:1103-1165`](../../src/society/cognition/day_plan.py))は **must が脅かされたときだけ**鳴り、**LLM を 1 本も呼ばない**(ルール内の作り直し)。`plan_retry` は framework 経路(P2 S1)専用で、day_plan v1 経路には存在しない(`planning.py:210-219`・day_plan ON では framework を `None` に落とす `planning.py:126-128`)。
- **プール回転で計画は失われる**: `dehydrate`([`world/pool.py:429-464`](../../src/society/world/pool.py))は `_dayplan` を運ばない(`day_plan.py:119` が自認)。再入場個体は次に眠って起きるまで無計画。

### 1.2 日跨ぎブロックの実挙動(プローブ実測)

`_hhmm`([`day_plan.py:408-425`](../../src/society/cognition/day_plan.py))は `0 <= h < 24` しか受けず、`day_end_min` の既定は 1440(`:274`)。実際に食わせて確認した:

```
'23:00' -> 1380   '02:00' -> 120    '24:00' -> None   '26:00' -> None

[23:00-02:00 と書いた場合]  schema errors: なし(start=1380,end=120 で通る)
                            after repair : 23:00-23:10     ops={'round': 1}
[23:00-26:00 と書いた場合]  schema errors: ['bad_end:b0']
                            after repair : 23:00-23:10     ops={'round': 1}
[22:00-23:30(日内・対照)] after repair : 22:00-23:30     ops={}
```

- **「23 時から深夜 2 時まで飲む」は書けない。書いても 10 分に潰される。**
  潰す実体は `repair` の `round` 演算子(`day_plan.py:697-698`: `if e - s < lo_dur: e = s + lo_dur`)で、**`slide`/`truncate`/`drop` のどれとしても数えられない**(`round` は「ほぼ全計画で起きる正規化」として `conflict_repair_rate` からも除外されている `:886-890`)。**つまり現在この事故は 1 つの指標にも現れない。**
- 仮に `day_end_min` を 1440 超に上げても直らない。`_hhmm` が 24 時超え表記を弾き、`current_block`(`:1408-1414`)と `_sweep`(`:1056`)が `now = sim_min % 1440` で判定するので、`start=1380, end=1560` のブロックは翌 1:00 に**一致しない**。**3 箇所同時に直す必要がある。**

### 1.3 日境界の実挙動(3 日 mock ラン実測)

`runs/_dph_probe_dpon`(600 体 × 432 step = 3 日・mock・seed 42・`start_tod="00:00"`・`natural_start=true`・day_plan v1 ON + contingency ON)。

```
plan_created  時刻分布  04時 8 / 05時 168 / 06時 352 / 07時 392 / 08時 410 / 09時 286 / 10時 38 / 11時 9 / 12時 1
sleep_start   時刻分布  00時 355 / 01時 417 / 02時 151 / 03-05時 11 / 22時 232 / 23時 360
plan_block_start 時刻分布  06時 84 …… 22時 85 / 23時 18 / 【00-05時 = 0 件】
drive_request 時刻分布  00時 1220 / 01時 609 (= その時間に確かに起きて活動している)
LLM 呼(social) 00時 643 / 01時 325
```

- **就寝の 61%(934/1526)が深夜 0 時以降**。ペルソナ生成器の `bedtime_min` は `22:00 + U{0..23}×10 分`([`persona.py:122`](../../src/society/agents/persona.py))= **22:00〜01:50 の一様**で、実際の `sleep_start` は帰宅移動のぶんさらに遅れる。
- **本番プールでも同じ**: `data/persona_pool/meta.json` の各層 shard を集計すると **L1/L3/L4/L5 の 49.8% が `bedtime_min` 00:00-01:59**(L1 30,000・L3 36,690・L4 707,778・L5 1,292 = 775,760 人の約半分)。L2(通勤者 224,240)だけは `bedtime_min` = 退勤時刻 16-23 時なので該当しない。
- 結果: **計画の有効寿命(生成 → 当日 24:00)の中央値は 16.3 時間**(p10 = 14.7h / 最短 11.7h)。一方 `wake_up` 中央値 07:10-07:40、`sleep_start` は半数が 00:00-02:00。
  → **中央的な住民は、計画が消えたあと 1〜2 時間、無計画で街に居る**。
  → 3 日ラン中、**深夜 0 時をまたいで覚醒していた個体×日は 741 件**(観測個体 599)。その全件で計画が黙って消えている。
- 一方で **`wake_up` 件数 = `plan_created` 件数 = 1,664 で完全一致**。起きた個体は必ず計画を貰えており、計画の取りこぼしはこのランでは 0 件。日別の計画取得者は 589 / 545 / 530 人(600 人中)で、貰えなかった分は「その暦日に一度も起床しなかった個体」。
- **起床時刻のドリフトは 3 日では暴走しない**: `wake_up` p50 = 07:10 → 07:40 → 07:40、p90 = 09:10 で安定。ただし 10 日ランでの確認は未実施。

### 1.4 睡眠・起床・昼寝

- **`wake_min` に相当する属性は無い**。起床は `sleep_until = 就寝した step + sleep_steps`(`scheduler.py:3043`)の導出量 = **帰宅が遅れれば起床も遅れる**(位相が自由に流れる)。
- `bedtime_min` / `sleep_steps` は**誕生時に 1 回固定**(`persona.py:107-108,122-123`。名簿経路も同じ)。日次の再抽選は 1 箇所も無い。
- 就寝トリガ `bedtime_reached`([`routine.py:327-331`](../../src/society/cognition/routine.py)): `((now - bedtime_min) % 1440) < 240` = **就寝時刻から 4 時間の窓**。円環演算なので日跨ぎは正しく効く。
- **`routine.decide` では就寝が計画より上位**([`routine.py:792`](../../src/society/cognition/routine.py) vs [`:944`](../../src/society/cognition/routine.py))。したがって 22 時以降のブロックは `bedtime_reached` に食われて実行されない個体が出る(実測 `plan_block_start` 22時=85 / 23時=18 と急落)。
- **`sleeping = True` の経路は 7 本**: 通常就寝(`scheduler.py:3040`)/ 宿泊(`:4957`)/ 終電後の夜間避難(`night.py:332`)/ 救急搬送中(`medical.py:497`)/ 入院中(`:692`)/ 路上で倒れる(`city_ops.py:1325`)/ 初日コールドスタート(`simulation.py:1615`)。
  **`sleeping = False` は 4 本**: 正規の起床(`scheduler.py:1079-1087`)/ チェックアウト(`:4969-4988`)/ 退院(`medical.py:707-716`)/ 退場・死亡(`health.py:1129-1141`)。
- **昼寝(nap)の機構は 1 行も存在しない**。`transit_interior.ACT_DOZE`(`:171`)は「車内でうとうとしていた」という**活動ラベルだけ**で `sleeping` も `fatigue` も触らない。`values.py:81` の「昼寝」は自由文の価値分類辞書。日中の在宅は `routine._sick_home`(`:446-466`)の**覚醒滞在**。
- **疲労は睡眠へ結線されていない**: `fatigue` は `collapse_fatigue >= 0.95` で**路上で倒れる**(`city_ops.py:1084`)経路しか持たず、「疲れたから早く寝る/仮眠する」経路は無い。逆に `day_plan` の `cond=tired` は `fatigue_high` を読むが、対処は `skip/postpone/go_home/…` で睡眠ではない(`day_plan.py:1249-1254`)。
- **夜勤**: `world.night_economy.enabled` が **本選 ON**([`conf/finals_observe.yaml:126-127`](../../conf/finals_observe.yaml))。`work._window`([`work.py:318-336`](../../src/society/work.py))が `close < open` のとき `wraps=True` を返し、`agent.work_wraps` が立つ(`work.py:413-416`)。`in_work_window`(`routine.py:347-352`)は `m >= start or m < end` で日跨ぎ勤務を正しく判定する。
  睡眠側は `_fix_night_commute`(`work.py:421-438`)が `bedtime_min = (work_end + 30) % 1440` に直すので**昼に寝る**。長さ・機構は昼勤と同一(専用の split sleep / anchor sleep は無い)。
  **本選台帳での実数**: `data/organizations_shibuya_census.json` の 9,872 社を集計すると
  **日跨ぎシフト(`close < open`)は 254 社 = 2.57%、従業者 4,984 人 = 全 222,849 人の 2.24%**。
  パターンは全件 **18:00→02:00**(次点は非日跨ぎの 07:00-23:00 が 1,620 社)。
  → **この 4,984 人は、計画が 00:00 に消えたあと 2 時間働き、02:30 に寝る**。
  つまり**勤務の最後の 2 時間 + 帰宅 + 就寝までの 2.5 時間が、毎日必ず無計画**。
  (`city_ops.py:63-72` が別途「名簿の就寝時刻が一般住民と同じなので深夜巡回は 1 件も立たない」
   と自認しているが、それは **L5 の役割束ね**の話で、上の L2 台帳由来の夜勤とは別経路。)
- **睡眠中に走る唯一の LLM は夜の内省**。`reflect_step` は就寝の直後 step に予約される(`scheduler.py:3044` / 宿泊 `:4961` / 来街者の帰路 `:1326`)。`_phase_drive` の `active` も `_decide` のループも `sleeping` を除外している(`scheduler.py:2479-2480` / `:5640-5641`)。

### 1.5 推論の時間分布 — 実測

**実測ラン 2 本**(いずれも 600 体 × 3 日・mock・seed 42・day_plan v1 ON):

| | `runs/_dph_probe_dpon`(cap 300 = 非拘束) | `runs/_dph_probe_cap60`(cap 60 = 拘束) |
|---|---:|---:|
| 総呼数 | 59,979 | 23,978 |
| **plan** | **1,664** | **1,647**(−1.0%) |
| **reflect** | **1,505** | **1,522**(+1.1%) |
| social | 28,345 | 17,454(−38%) |
| **reply** | **16,722** | **618(−96%)** |
| unknown_word | 8,482 | 1,652(−81%) |
| 予算内呼/step 最大 | 249 | **64** |
| 予算外呼/step 最大 | 35 | **36** |
| **合計呼/step 最大** | 249 | **96 = cap 60 + 予算外 36** |
| cap 到達 step | 0 / 432 (0.0%) | **313 / 432 (72.5%)** |
| drive_request の granted 率 | 76.9%(予算枯渇 0 件) | **22.3%(予算枯渇 59,180 件 = 65.3%)** |
| 0 呼 step | 19 | 18 |
| ラン完走 | ✅ | ✅ |

**時刻集中(cap 非拘束ラン)**

```
plan     04時 0.5% / 05時 10.1% / 06時 21.2% / 07時 23.6% / 08時 24.6% / 09時 17.2% / 10-12時 2.9%
         → 97% が 05-10 時。ピーク 08 時。12 時以降は 0 件。
reflect  22時 10.8% / 23時 23.9% / 00時 23.3% / 01時 26.8% / 02時 14.6% / 03-05時 0.7%
         → 100% が 22-06 時。06-21 時は 0 件。
全 purpose 合計のピークは 18-21 時(夕方の対面会話)で、朝の計画ピークではない。
```

**cap 拘束ランの時刻別 cap 到達率**

```
07時 83% / 08-23時 100% / 00時 50% / 01時 6% / 02-06時 0%
```

**cap 拘束ランの reply 時刻分布(致命的)**

```
00時 98 / 01時 215 / 02時 19 / 03-06時 5 / 07時 143 / 【08時〜23時 = すべて 0】
```

### 1.6 予算と安全弁の現状

- `LodBudget`([`cognition/lod.py:80-92`](../../src/society/cognition/lod.py))は step ごとにリセットされる単純カウンタ 1 本。`reset()` は `run_step` の**最初の 1 行**(`scheduler.py:5484`)。
- **`take()` を呼ぶのは 3 箇所だけ**: 対面/割込みの確定発火(`scheduler.py:2565`)/ 媒体・独り言の抽選当選(`:2581`)/ 返答保証(`:2701`)。
  **plan / plan_retry / reflect / recall / null は予算外**([`conf/config.yaml:1425-1429`](../../conf/config.yaml) が既にこれを明記。正典 [`docs/research/finals-llm-budget.md`](../research/finals-llm-budget.md) §1)。
- **配分順序**: `requesters.sort(key=lambda a: (-a.drive, a.id))`(`scheduler.py:2551`)= **ゲージ降順、同値は agent_id 昇順**。round-robin もランダムシャッフルも「前回いつ呼ばれたか」を見る cooldown も無い。フェアネスは (a) 呼ばれなかった個体はゲージが減らないので次 step 順位が上がる(暗黙の aging)、(b) 不応期 3 step、(c) 会話クールダウン 6 step の 3 つに依存。
- **枯渇時の挙動**: 発火側は `drive.on_fire` を呼ばない = ゲージ維持で次 step へ持ち越し + `routine.decide`(ルール駆動)へ後退。L1 に `drive_request{granted:false}` が残る。
  **返答保証だけは違う**: `agent._reply_to` は `take()` の**直前 `:2700` で既に None にクリア済み**なので、落ちた返答は**黙って消える**(L1 に痕跡ゼロ・`conv_turns_left` も減らない)。**観測できない飢餓**。
- **止まらない設計は多層で存在する**(実 LLM 側):
  ソケット timeout 120s(`config.yaml:218`)→ 絶対時限 `call_deadline_s: 300`(`llm/deadline.py`。実測「1 呼が 1 時間 47 分張り付いた」への対処)→ 艦隊フェイルオーバ(`llm/fleet.py:109-132`・失敗サーバを 30s 隔離)→ backend が例外でなくエラー文字列を返す(`vllm.py:107-119` 等)→ パース失敗 → `fallback` イベント + `routine.decide` へ後退。
  **例外は `cache_mode=replay` のみ**(キャッシュミスで `RuntimeError`。silent fallback 禁止の意図的設計)。
- **正直な穴**: `fallback` イベントを出すのは発話系だけ。**計画・内省の失敗は L1 に 1 件も出ない**(`scripts/watchdog_llm.py:25-30` が自認)。`fallback_rate` は真のパース失敗率の下限。

---

## 2. 判定 — ユーザーの懸念それぞれに Yes/No

| # | 懸念 | 判定 | 根拠(実測/コード) | 深刻度 |
|---|---|---|---|---|
| **P1** | 朝の計画が日をまたいでリセットされる | **Yes(確定)** | `day_plan.py:1025-1029`。実測: 00-05 時の `plan_block_start` = 0 件 / 就寝の 61% が 0 時以降 / 深夜 0 時に覚醒していた個体×日 741 件 | **高**(本選 ON 経路) |
| **P2** | 日跨ぎの計画ブロック(23:00-02:00)が書けない | **Yes(確定)** | プローブ: 23:00-02:00 → 23:00-23:10 に潰れる。`_hhmm`/`day_end_min`/`current_block` の 3 重ロック | **高**(渋谷=夜の街なのに夜が計画できない) |
| **P3** | その潰れが指標に出ない | **Yes(確定)** | `round` 演算子として計上され、`conflict_repair_rate` からも除外(`day_plan.py:886-890`) | **中**(観測の穴) |
| **P4** | 夜勤者の主要活動時間が常に無計画 | **Yes(人数も確定)** | `work_wraps` ON(本選)+ 暦日境界。台帳実測: **18:00→02:00 シフトが 254 社・従業者 4,984 人(L2 の 2.24%)**。この全員が「勤務末尾 2 時間 + 帰宅 + 就寝(02:30)まで」を毎日無計画で過ごす | **中**(人数は少ないが 100% 再現する構造的欠落) |
| **P5** | 「1 暦日 1 計画」ガードで計画を貰えない日が出る | **条件付き Yes** | `scheduler.py:947`。実測ランでは `wake_up == plan_created` で取りこぼし 0。ただし (a) 同暦日に 2 回起きた個体は 2 本目なし (b) `plan_step` の step に `sleeping`/`outside` だと**その日の計画は永久に失われる**(`:971-972` で `plan_step` は消費済み) | **中** |
| **P6** | プール回転で計画が失われる | **Yes(既知・自認済み)** | `pool.py:429-464` の `dehydrate` に `_dayplan` なし | **低**(次の起床で立て直る) |
| **P7** | `carry`(昨日からの持ち越し)を翌朝の計画が読まない | **Yes(ただし観測穴は 8/14 に閉じた)** | 機構として読む行ゼロ。並行レーン G7(`observer.gt_extras`・本選 ON)が L1 payload への**記録**だけ足した = 事後解析では読めるが、翌朝のプロンプトには入らない | **低**(第93 の `cont` と同型の未回収) |
| **P8** | 昼寝の概念が無い | **Yes** | 全文検索でゼロ | **低〜中**(§3.2 で「入れない」を推奨) |
| **P9** | 疲労 → 睡眠の結線が無い | **Yes** | `fatigue` は倒れる経路しか持たない | **中**(「世界のアルゴリズムでなく本人の状態が決める」原理への違反) |
| **P10** | 推論が特定時刻に集中する | **Yes(確定)** | plan 97% が 05-10 時 / reflect 100% が 22-06 時。**両方とも予算外** | **高** |
| **P11** | 「朝しか内省できない → 夜の出来事が内省されない」 | **No** | 内省は**就寝直後**(`scheduler.py:3044`)= 22-03 時。夜の出来事は内省に載る。逆向きの懸念(§P12)が正しい | — |
| **P12** | 日中の出来事で計画を練り直せない | **Yes** | `_replan` は**ルール内**で LLM ゼロ(`day_plan.py:1105`)。`plan_retry` は day_plan v1 経路に存在しない(`planning.py:126-128` が day_plan ON で framework を落とすため)。`cognition.fire` が ON なら `plan_exception` で「いま考える」へ繰り上がるが、**本選 conf では `watch` / `fire` / `engaged` の 3 行が未承認でコメントアウトのまま**([`conf/finals_observe.yaml:394-397`](../../conf/finals_observe.yaml))。`g_update` だけ `enabled: true` になっているが、同 conf 自身が「**`fire` が ON でなければ 1 行も走らない = 現状では無効な宣言**」と正直申告している(`:387-393`) | **中** |
| **P13** | 集中で実験が**止まる** | **No** | cap 60(72.5% の step が飽和)でも完走。timeout/deadline/fleet/fallback の 4 層。`replay` モード以外に停止経路なし | — |
| **P14** | 集中で実験結果が**歪む** | **Yes(重大)** | cap 拘束下で **reply が 08-23 時に 100% 消滅**(実測)。しかもこの枯渇は L1 に 1 件も残らない(`scheduler.py:2700`)。=「話しかけたのに誰も返さない街」が**観測不能なまま**成立する | **最高** |
| **P15** | LOD cap が per-step 呼数の上限として機能していない | **Yes** | 実効上限 = `cap + 予算外呼`。実測 cap 60 のランで **1 step 96 呼**。予算外呼のピークは全人口の約 6%/step(600 体で 36 呼) → **25 万在場なら朝のピーク step で 1.5 万呼**(cap 300 の 50 倍) | **高**(本選の壁時計リスク) |

---

## 3. 設計案

### 3.1 計画地平の変更 — 4 案の比較

| 案 | 内容 | 長所 | 短所 | 判定 |
|---|---|---|---|---|
| **A. 起床→次の就寝**(ユーザー案) | 計画の有効期間を「生成時刻 → 本人の次の就寝」にする。`plan["day"]` を捨て `plan["from_min"]`/`plan["until_min"]`(絶対分)に置換 | 人間の主観的な「1 日」と一致。夜勤者も自然に扱える。P1/P2/P4 が一挙に解ける | 「次の就寝」は生成時点で未知(`bedtime_min` からの予測値でしかない)。徹夜・二度寝で外れる | **本命** |
| **B. 3 時境界**(NHTS/ATUS 流) | `plan["day"]` の定義を `(sim_min - 180)//1440` に変える | 変更が 1 箇所で済む。日次機構(暦・天気・会計・pool 回転)は暦日のままにできる | 3 時を選ぶ根拠が渋谷にはない(実測就寝ピークは 00-02 時)。夜勤者は依然として救えない。「境界をずらしただけ」で原理は同じ | 次善 |
| **C. 日跨ぎブロック許容のみ** | `_hhmm` を 24-30 時表記に拡張・`day_end_min` を 1800 等へ・`current_block`/`_sweep` を絶対分判定に | P2 が直る。表現力が上がる | P1(計画そのものの失効)は残る。3 箇所の同時改修が要る | **A/B のどちらでも必須の同伴作業** |
| **D. 現状維持 + 観測だけ足す** | `round` による日跨ぎ潰しを専用カウンタで数え、`plan_expired_while_awake` を L1 に出す | R1 リスクゼロ・本選直前でも安全 | 何も直らない | **最低ライン(必ずやる)** |

**推奨 = A+C(「A+」と呼ぶ)。ただし段階投入。**

#### A+ の具体形

1. **地平の記述を絶対分にする**
   `plan["day"]` → `plan["from_min"]`(生成時の絶対分)/ `plan["until_min"]`(生成時に確定する予測就寝時刻)。
   `_plan_of` は `from_min <= sim_min < until_min` で判定(`% 1440` を使わない)。
   `until_min` = `生成時刻` から円環で次に来る `bedtime_min` + `grace`(たとえば +240 分 = `bedtime_reached` の窓幅)。
   → 夜勤者(生成 13:30 / bedtime 06:30)は `until_min` = 翌 06:30(+4h) = **17 時間の地平が日跨ぎで張れる**。

2. **時刻表現を「起床からの相対」ではなく「絶対分」で持つ**
   LLM には **HH:MM のまま書かせる**(プロンプトは変えない = no-fingerprint 維持・実 LLM の素直な出力形)。
   `_hhmm` を **24-29 時表記も受ける**ように拡張(`24:30` → 1470)。**さらに `end < start` なら `end += 1440` と解釈する**(「23:00-02:00」を素直に読む)。この 2 つで P2 が閉じる。
   `validate_schema` が返す `start`/`end` を `plan["from_min"]` 基準の絶対分へ持ち上げ、`current_block`/`_sweep`/`repair` は絶対分だけを見る。`day_end_min` は `until_min` からの導出量にする(config キーは残し、`0` = 「until_min まで」の意味を足す)。

3. **再生成トリガを暦日ガードから外す**(P5 の根治)
   `_schedule_plan` の `agent.plan_day == day` を `agent.plan_until_min > sim_min`(= まだ有効な計画がある)に置き換える。
   これで「同暦日に 2 回起きたら 2 本目が立つ」「深夜 0 時をまたいだだけでは立たない」の両方が正しくなる。
   **呼数への影響を必ず実測すること**(§4)。二度寝・倒れる・退院が多いランでは呼数が増えうる。増分に上限を掛ける seam(`min_replan_interval_min`)を同時に置く。

4. **日次機構は暦日のままにする**(暦・天気・会計・pool 回転・L2 集計)。
   計画の地平だけを個人時間軸に移す。**これは「世界の日」と「人の日」を分ける設計**で、MATSim の 24h plan と ActivitySim の tour time window の関係に対応する(§5)。

#### 副作用として直る/直さないもの

- 直る: P1 / P2 / P4 / P5。
- **直らない**: P6(pool 回転)は `dehydrate` に `_dayplan` を積むかどうかの別判断(積むとメモリが増える。25 万 × 8 ブロック)。P7(`carry`)は独立の小改修。

### 3.2 昼寝の扱い — 「昼寝機構は入れない。疲労→睡眠の結線を入れる」を推奨

**理由:**

1. **`nap` という新しい状態を足すのは本プロジェクトの原理に反する。** ユーザー原理は「世界のアルゴリズムがエージェント量/結果を決めない」。昼寝を確率テーブルで撒くのは典型的な「世界側のノブ」。
2. **必要なのは昼寝そのものではなく、`sleeping` が本人の状態の関数になっていないこと**(P9)。現状 `bedtime_min` は誕生時固定の定数で、その日どれだけ働いたか・徹夜したか・疲れているかを一切読まない。
3. **既存機構だけで昼寝は表現できる**: `day_plan` のブロックに `act="home", place="home", aim="rest"` が既にある(`day_plan.py:137-140,160-171`)。LLM が「14:00-15:00 家で休む」と書けば、それが昼寝である。**新しい語彙も新しい状態も要らない。**

**推奨する最小の結線(既定 OFF・専用トグル):**

- `bedtime_min` を**その日の疲労で前後させる**(誕生時固定値を基準にした決定論写像。乱数ゼロ)。
  例: `effective_bedtime = bedtime_min - k × max(0, fatigue - fatigue_high)`(前倒し上限 90 分)。
  → 「疲れた日は早く寝る」が本人の状態から出る。R1 上は位置経由の間接効果のみ(`affects_k=False`)。
- `sleep_steps` も同様に疲労で伸ばす(上限つき)。
- **昼の在宅ブロック(`act="home"` かつ `aim="rest"`)の間だけ `fatigue` の回復レートを上げる**。`sleeping` は立てない(倒れる判定・知覚除外・LLM 除外を巻き込まない)。これが「昼寝の効果」の全部で、状態は 1 つも増えない。
- **夜勤者の split sleep / anchor sleep は入れない**。文献は明確(夜勤者の睡眠は昼勤者より 1 日 2〜4 時間短い・morning/delayed/split/mixed の 4 型・anchor sleep が最推奨。§5.3)だが、**対象は台帳実測で 4,984 人 = L2 の 2.24%** と小さく、渋谷固有の較正データも無い。**入れるより「地平を直す(§3.1)」ほうが同じ 4,984 人に対して効果が大きい**。正直に「未実装」と申告する。

### 3.3 推論呼の平滑化

**現状の問題を分解すると 3 つある。**

| 問題 | 現状 | 対策案 |
|---|---|---|
| **S1. 予算外呼が per-step 上限を突き抜ける** | 実効上限 = `cap + 予算外`。実測 1 step 96 呼(cap 60)。25 万在場のピーク step で**推定 1.5 万呼** | **plan / reflect を予算の中に入れる**。ただし単純に `take()` を足すと「計画を貰えない個体」が出て R1(呼数の k 非依存)は保たれるが**日次計画の欠落**が起きる。→ **二層予算**(下記) |
| **S2. cap 枯渇で reply が完全に消える** | `_phase_drive` が先に食い切り、`_decide` の返答保証が残りカスを取る。実測 08-23 時で reply = 0 | **予算を purpose 別に予約(reservation)する**。例: `reply` に cap の 20% を先取りで確保。加えて**枯渇した reply を L1 に必ず 1 件残す**(観測の穴を塞ぐ) |
| **S3. 集中そのもの** | plan 97% が 05-10 時 / reflect 100% が 22-06 時 | **平滑化しない**のが正しい。人が朝起きて夜寝る以上、認知の負荷が朝夕に寄るのは**現象であって欠陥ではない**。直すべきは「その山でシステムが壊れないこと」(S1/S2)であって、山を均すことではない |

**推奨する二層予算(`lod.budget.tiers`・既定 OFF)**

```
step 予算 C を 3 つのバケツに分ける(合計 = C):
  reserved_life   = 生活基盤(plan / reflect)。上限 C_life。溢れた分は次 step へ FIFO キュー。
  reserved_reply  = 返答保証。上限 C_reply。
  general         = 残り(発火・独り言・投稿)。現行の drive 降順ソートのまま。
未使用の reserved は同 step 内で general へ流す(遊ばせない)。
```

- **plan/reflect が溢れたら翌 step へ持ち越す(キュー)**。現状は「予約された step で撃つか、`sleeping`/`outside` なら永久に失う」の 2 択(P5)。FIFO キューにすれば **10 分遅れて計画が立つだけ**で、失われない。キューは `(予約 sim_min, agent_id)` の全順序 = 決定論。
- **キューの上限と最大遅延を持つ**: `max_defer_steps`(例 18 = 3 時間)を超えたら**骨格計画(`skeleton`)へ落とす**(LLM ゼロ)。これで「朝の計画が 15 時に立つ」を防ぐ。既存の fallback 階段に 1 段足すだけで、新しい概念を作らない。
- **`purpose` 別の枯渇カウンタを L2 に出す**(`llm_budget_denied_by_purpose`)。現在は `drive_request{granted:false}` しか無く reply の枯渇が見えない。

---

## 4. 実験を止めない / 歪めないための保証設計

### 4.1 止めない(現状で概ね達成済み。追加は 2 点)

| レイヤ | 現状 | 追加提案 |
|---|---|---|
| 呼レベル | timeout 120s → deadline 300s(`llm/deadline.py`) | — |
| サーバレベル | fleet フェイルオーバ + 30s 隔離(`llm/fleet.py:109-132`) | — |
| パースレベル | エラー文字列 → `_loads_lenient` 失敗 → 検証 → 修復 → 前日計画 → 骨格(`day_plan.py:951-971`) | — |
| step レベル | **無し**(1 step にいくつ呼が積もっても待つだけ) | **step の壁時計上限**(`engine.step_wall_budget_s`。超過したら残りの予算外呼をキューへ倒して次 step へ)。25 万のピーク step で 1.5 万呼が直列に走ると**単一 step が数十分〜数時間**になりうる(`engine.batch_llm` は本選 conf で OFF = 完全直列) |
| ラン レベル | watchdog(`scripts/watchdog.py` / `watchdog_llm.py`)+ checkpoint/resume | **朝ピーク step の壁時計を watchdog の監視項目に足す**(現在はディスクと呼数) |

### 4.2 歪めない(ここが本丸)

**原則: 「削るなら、削ったことを必ず記録する」。**

1. **reply 枯渇の記録**(最優先・小改修)
   `scheduler.py:2700-2701` で `_reply_to` をクリアする前に `take()` を試し、落ちたら `Event(kind="reply_dropped")` を 1 件出す。現状は**痕跡ゼロ**で、「話しかけられたのに誰も返さない街」が観測不能なまま成立する。
2. **日跨ぎ潰しの記録**(小改修)
   `repair` の `round` が `e - s < 0`(= 日跨ぎ表記)で潰したケースを `ops["wrap_clipped"]` として別立てで数える。現在は `round` に埋もれ、`conflict_repair_rate` からも除外されている。
3. **計画欠落の記録**(小改修)
   `_phase_planning` が `sleeping`/`outside` でスキップした個体を `Event(kind="plan_skipped", reason=...)` で残す。現在は静かに消える。
4. **k 不変の再証明**(R1)
   予算の作り替え・地平の変更はどちらも「呼数の構造」を触るので、**`compute_matched` 下で k=free と k=off の呼数完全一致**を再取得する(`docs/agent-implementation-summary.md:120-123` の型 2)。
5. **ゴールデン**: 全レーンを**既定 OFF で着地**させ、OFF ランの L1 バイト一致 + `golden` 緑を検収条件にする。地平変更(A+)は既定 OFF が原理的に不可能なので(挙動が変わる)、**`planning.day_plan.horizon: "calendar"`(既定 = 現行と完全同値)/ `"wake_to_sleep"` の 2 値トグル**にして、`"calendar"` でバイト一致を機械固定する。

### 4.3 「歪み」の事前登録(pre-registration)

本選前に以下を**予測として書き留めて**から実測する(事後解釈を防ぐ):

- H1: 地平を wake_to_sleep にすると `plan_block_start` が 00-02 時に出現する(現在 0 件)。
- H2: 同時に 22-23 時の `plan_block_drop`(`reason=fixed_past`/`grace`)が減る。
- H3: 呼数は **plan だけ +α%**(α = 同暦日 2 回起床の割合)増える。それ以外の purpose は不変。
- H4: 予算の二層化で `reply` の時刻分布が平坦化し、L2 の `n_replies` が cap 拘束下でも 0 にならない。

---

## 5. 文献的接地

> リサーチは軽量(既存の repo 内リサーチ資産 + 追加のウェブ検索 4 本)。
> **先行がどう解いているか**を確認するのが目的で、較正データの取得ではない。

### 5.1 「1 日」の境界 — 先行はどれも 0 時境界を採っていない

| 先行 | 「1 日」の定義 | 日跨ぎ活動の扱い |
|---|---|---|
| **MATSim** | plan は 24 時間ぶんだが、**シミュレーション日は最長の活動連鎖ぶん 24 時間を超えて回る** | **first activity と last activity を「同じ 1 つの活動」として合体して採点する**(例: 最初の活動が 07:00 に終わり最後の活動が 23:00 に始まるなら、合体して 8 時間の活動として scoring)。開始時に居る活動は `startTime` 未定義、終了時に居る活動は `endTime` 未定義で、実装側が "wrap around" する |
| **ActivitySim / CT-RAMP** | tour の time window は離散選択肢 `tdd` の表。時間帯区分の実装は地域ごとで、**夕方帯を「3:00 AM の前」で切る**構成が使われる | tour が翌未明に食い込むケースを時間帯定義側で吸収 |
| **NHTS(米・全国世帯交通調査)** | **travel day = 04:00 〜 翌 03:59 の 24 時間**。理由が明記されている:「**4 AM は最も移動している人が少ない時刻**なので、トリップのデータがより一貫して取れる」 | 境界そのものを人の少ない時刻へ逃がす |

- **本シムの day_plan v1 だけが 0 時境界を採っている**([`day_plan.py:1025-1029`](../../src/society/cognition/day_plan.py))。しかも渋谷の実測就寝分布は **00:00-02:00 がピーク**(§1.3)= **境界を最も人が活動している時刻に置いている**。NHTS の 4 時境界の設計意図と真逆。
- MATSim の wrap-around(first と last の合体)は、**§3.1 案 A+ が目指すもの**とほぼ同じ発想である: 「暦日の切れ目にある活動を、切らずに 1 つとして扱う」。ただし MATSim は**採点のため**に合体するのに対し、本シムでは**実行のため**に地平を延ばす必要がある(採点機構が無い)。
- 旧経路(`planning.framework` OFF の帯ラベル方式)は `_time_band` が 0-5 時を「夜」へ畳んでいる(`routine.py:477-488`)ので、**偶然にも先行の作法に近い**(境界が実質 05:00)。**day_plan v1 への移行で、この性質が失われている**。

### 5.2 LLM 社会シムの日課計画

- **Generative Agents (Park et al. 2023, arXiv:2304.03442)**: ペルソナ + **「昨日の出来事」**から**5〜8 個の粗い日課**を生成し、記憶ストリームへ保存 → 再帰的に時間単位 → 行動単位へ分解する 3 層。
  - 本シムの day_plan v1 の「4〜8 ブロック」はこの層に対応する(`day_plan.py` の DEFAULTS `min_blocks:4 / max_blocks:8`)。
  - **「昨日の出来事」を明示的に計画の入力にしている**のが Generative Agents の特徴で、本シムの `carry`(「昨日から気にしていること」)は**同じ意図で作られたが読み手が居ない**(§P7)。
  - Generative Agents の例示計画は「23:00 に宿題を終えて寝る」で終わっており、**日跨ぎブロックの扱いは論文が扱っていない**(Smallville は 0 時境界での失効を持たない = 計画は次の朝に上書きされるまで生き続ける)。**つまり本シムの 0 時失効は先行にも無い独自の制約**である。
- 大規模 LLM エージェントシムの呼数スケジューリング(AgentSociety / OASIS 等)については、**「時間帯集中に対するバックプレッシャー設計」の先行を今回の軽量サーチでは見つけられなかった**。本シムの二層予算(§3.3)は既存の先行の借用ではなく、離散イベントシミュレーションのフェアネス一般論(予約バケツ + FIFO + aging)からの構成である。**正直に「借り先が無い」と申告する。**

### 5.3 睡眠・昼寝

- **交代勤務者の睡眠**: 夜勤者の睡眠は昼勤者より **1 日あたり 2〜4 時間短い**。連続夜勤の間の睡眠は 5.74 ± 1.30 時間。交代勤務者は **morning / delayed / split / mixed sleeper** に分類され、**anchor sleep**(ローテーションに関わらず毎日同じ時間帯に取る睡眠)が最も推奨される戦略。
  → **本シムは `sleep_steps` が誕生時固定なので、夜勤者も昼勤者と同じ長さ眠る**。実態(2〜4 時間短い)とはズレる。ただし較正データを持たないので、**本書では「未実装」を正直に申告する方針**(§3.2)。
- **日本の生活時間統計**: NHK 放送文化研究所「国民生活時間調査」が 15 分刻みの**時刻別行為者率**(睡眠を含む)を 5 年ごとに公表している。総務省「社会生活基本調査」も e-Stat 表 6-2 で **0:00〜24:00 を 96 区分**で持つ(既に [`docs/research/daily-plan-framework.md:84`](../research/daily-plan-framework.md) が正典として引いている)。
  → **就寝時刻分布と昼寝の行為者率は、この 2 つで較正できる**。現行の `bedtime_min = 22:00 + U{0..23}×10 分`(一様)は較正されていない仮置き値であり、**本書の実測「就寝の 61% が 0 時以降」はこの仮置きの帰結**であって、渋谷の実態を測ったものではない。**較正は別レーン(本書の範囲外)。**

### 5.4 この節から出る設計上の含意

1. **0 時境界は先行のどれも採っていない。** 境界を動かすだけ(案 B)でも先行に沿う。
2. **MATSim は「合体」で解いている。** 案 A+ の `until_min` は同じ問題への別解で、**個人ごとに境界が違う**ぶん MATSim より人間らしい。
3. **昼寝は先行の活動ベースモデルでも独立の状態にしていない**(ActivitySim の非義務目的にも nap は無い)。§3.2 の「新しい状態を作らない」判断は先行と整合する。

**Sources:**
- [MATSim scoring: first/last activity wrap-around(matsim.org doxygen / MATSim book)](https://www.matsim.org/doxygen/interfaceorg_1_1matsim_1_1core_1_1scoring_1_1_scoring_function.html)
- [ActivitySim white paper (RSG)](https://rsginc.com/activitysim-white-paper/) / [ActivitySim tour scheduling notebooks](https://github.com/activitysim/activitysim/blob/main/activitysim/examples/example_estimation/notebooks/16_nonmand_tour_scheduling.ipynb)
- [NHTS FAQ: travel day = 4:00 AM–3:59 AM](https://nhts.ornl.gov/faq)
- [Park et al. 2023, Generative Agents (ACM DL full text)](https://dl.acm.org/doi/fullHtml/10.1145/3586183.3606763) / [arXiv:2304.03442](https://ar5iv.labs.arxiv.org/html/2304.03442)
- [Evaluation of sleep strategies between night shifts in actual shift workers (Sleep Health)](https://www.sciencedirect.com/science/article/abs/pii/S2352721823002024)
- [Anchor sleep for shift work (Sleep Review)](https://sleepreviewmag.com/sleep-disorders/circadian-rhythm-disorders/shift-work/anchor-sleep-survive-shift-work/)
- [The Impact of Shift Work on Sleep, Alertness and Performance in Healthcare Workers (PMC6420632)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6420632/)
- [総務省統計局 統計FAQ 23E-Q01 睡眠時間](https://www.stat.go.jp/library/faq/faq23/faq23e01.html) / [e-Stat 社会生活基本調査 表6-2](https://www.e-stat.go.jp/stat-search/database?page=1&statdisp_id=0003457693)

---

## 6. レーン分割・規模・R1 準拠

| レーン | 内容 | 規模 | R1 | 既定 | 投入判断 |
|---|---|---|---|---|---|
| **DPH-O(観測のみ)** | ① `reply_dropped` イベント ② `wrap_clipped` 演算子 ③ `plan_skipped` イベント ④ L2 に `llm_budget_denied_by_purpose` | **小**(src 3 ファイル・新 kind 2・L2 列 1) | 記録のみ・分岐ゼロ・乱数ゼロ・呼数不変 | **ON でも世界不変**(記録専用) | **本選前・即日可**。これだけでも §2 の P3/P14 の観測穴が閉じる |
| **DPH-C(日跨ぎブロックの表現)** | `_hhmm` の 24-29 時受理 + `end<start → end+1440` + `current_block`/`_sweep`/`repair` の絶対分化 | **中**(day_plan.py 1 ファイル・約 60 行) | プロンプト 1 バイト不変(HH:MM のまま)・乱数ゼロ・呼数ゼロ増 | トグル `day_plan.wrap_blocks`(既定 false = 現行バイト一致) | **本選前推奨**。C 単独でも「夜の街が計画できない」が直る |
| **DPH-A(地平の wake→sleep 化)** | `plan["day"]` → `from_min`/`until_min`・`_schedule_plan` のガード置換・`min_replan_interval_min` | **中〜大**(scheduler + day_plan・resume/checkpoint の state 追加) | **呼数が動きうる** → `compute_matched` で k 不変を再証明必須 | `day_plan.horizon: "calendar"`(既定)/ `"wake_to_sleep"` | **要ユーザー判断**。C の後 |
| **DPH-B(予算の二層化 + キュー)** | `LodBudget` → `TieredBudget`・予算外呼の FIFO 繰り越し・`max_defer_steps` 超過で骨格へ | **中**(lod.py + scheduler 3 箇所) | 呼の**総量**は不変(時間分布だけ変わる)。k 非依存は自明 | `lod.budget.tiers.enabled: false`(既定) | **本選前推奨**(25 万のピーク step 対策として P15 に直結) |
| **DPH-N(疲労→睡眠の結線)** | `effective_bedtime` の疲労写像 + 在宅 rest ブロックの回復レート | **小**(routine + health) | 位置経由の間接効果のみ(`affects_k=False`) | `health.sleep_feedback.enabled: false`(既定) | **本選後で可**。原理適合の改善であって、本選の観測を壊す穴ではない |
| **DPH-P(`carry` の回収)** | `plan["carry"]` を翌朝の計画プロンプトへ 1 行だけ差し込む | **小** | プロンプトが変わる = **APC prefix・mock・golden に影響** | `day_plan.use_carry: false`(既定) | **本選後**。第93 の `cont` 回収と同型だが、本選直前にプロンプトを触るのは避ける |

**規律(全レーン共通)**

- 既定 OFF または完全同値着地。OFF ランの **L1 バイト一致 + golden 緑**を検収条件にする。
- 新 stream のみ(既存 stream の draw 順に触らない)。
- `resume == straight` のバイト一致。**per-agent 属性(`plan_until_min` など)は agents の pickle に自然同梱される**ので追加作業不要(`checkpoint.py:171` が day_plan v1 について同じことを明記)。一方 **DPH-B の FIFO キューは sim 級の状態**なので `checkpoint.py:176 / 609-611` の `dayplan_state` と同じ作法で明示登録が要る(第109「回転搭載 8 族」と同型)。
- no-fingerprint: プロンプトに機構語を 1 語も出さない。DPH-C は HH:MM 表記のままなのでプロンプト不変。
- 凍結 14 本不触。

**推奨投入順**: `DPH-O` → `DPH-C` → `DPH-B` →(ユーザー判断)→ `DPH-A` →(本選後)→ `DPH-N` / `DPH-P`

---

## 7. 決定アジェンダ(ユーザー判断が要る点)

1. **DPH-O(観測 4 点)を即日入れるか。** 世界を 1 バイトも動かさない記録専用。入れないと本選の reply 枯渇と日跨ぎ潰しが**事後に検出できない**。
2. **DPH-C(日跨ぎブロック)を本選前に入れるか。** 渋谷は夜の街であり、「23 時から 2 時まで」が書けないのは現象の側の欠落。
3. **DPH-A(地平の wake→sleep)を本選前に入れるか、本選後に回すか。** 効果は大きいが呼数が動くので R1 の再証明が要る。**代替の最小案**として「`plan["day"]` の境界を 0 時から `04:00` へずらすだけ」(案 B)も残す — 1 箇所の改修で、実測就寝分布(00-02 時ピーク)の外側に境界を逃がせる。
4. **DPH-B(二層予算)を本選前に入れるか。** 25 万在場でのピーク step 推定 1.5 万予算外呼(cap 300 の 50 倍)への唯一の構造的対策。8/15-16 の R_eff 実測とセットで判断するのが自然。
5. **`cognition.fire`(+ `watch` / `engaged`)を開けるか**(`conf/finals_observe.yaml:394-397` の 3 行)。ON にすると `plan_exception` 経由で「計画が破綻したときに考え直す」が動く = P12 が部分的に閉じる。**同時に `g_update`(既に `enabled: true`)が初めて実効になる**(conf 自身が「fire が OFF なら 1 行も走らない = 現状では無効な宣言」と申告済み)。ただし `fire` は `affects_k=True`(LLM 呼の発生点そのものが変わる)なので、**§3.3 の予算問題と不可分**: 割込み発火が増えれば予算内呼の競合が悪化し、cap 拘束下では reply の枯渇(P14)がさらに深刻になる。**DPH-B と同時に判断するのが筋。**
6. **昼寝は入れない**という方針でよいか(§3.2)。入れるなら「新しい状態を作らず、既存の `act=home / aim=rest` ブロックの効果として表す」形に限る。

---

## 8. 再現手順(本書の実測)

```bash
# 実測ラン A(cap 非拘束)
python scripts/run.py run.seed=42 run.n_agents=600 run.n_steps=432 \
  run.start_tod="00:00" run.natural_start=true \
  planning.day_plan.enabled=true planning.day_plan.use_contingency=true \
  run.name=_dph_probe_dpon

# 実測ラン B(cap 拘束)
python scripts/run.py ... lod.max_llm_per_step=60 run.name=_dph_probe_cap60
```

集計は `l1b_llm.parquet`(`step`/`purpose`)と `l1_events.parquet`(`sim_min`/`kind`)から。
**注意: `l1b_llm` には `sim_min` 列が無い**ので `sim_min = start_tod + step × dt_min` で換算する。
日跨ぎブロックのプローブは `society.cognition.day_plan` の `validate_schema` / `validate_physical` /
`repair` / `_plan_of` を直接呼んで確認した(src 不触)。

夜勤者の実数は `data/organizations_shibuya_census.json` の `companies[].shift_pattern`
(`close < open` の社数と `size.employees` の合計)から。プールの就寝分布は
`data/persona_pool/L*/part-0000.jsonl` の `bedtime_min` から。

> **ディスク**: 上の 2 ラン(`runs/_dph_probe_dpon` 56 MB / `runs/_dph_probe_cap60` 29 MB)は
> 検証済みなので**削除してよい**(`runs/` は gitignore 配下)。再現は上のコマンドで足りる。

---

## 9. 正直な限界

- 実測は **mock LLM** であり、mock の `_day_plan` 生成器([`llm/mock.py:120-151`](../../src/society/llm/mock.py))は **`start >= 23:00` で break する**ので、**日跨ぎブロックを 1 件も生成しない**。したがって「実 LLM が実際に 23:00-02:00 と書く頻度」は本書では測れていない。§1.2 は**コードの受理能力**を直接プローブして示したものであって、発生頻度の実測ではない。
- 600 体 × 3 日の値であり、25 万体 × 10 日への外挿は「予算外呼のピークは全人口の約 6%/step」という 1 つの比だけに依っている。**8/15-16 の診断ランで per-step 呼数の実測が要る**。
- 夜勤者の人数は**台帳側(254 社 / 4,984 人)は確定**したが、**実ランで何人が実際に `work_wraps` を立てるか**は未測定(`bind_workplace` の解決成功率・当日の在場・pool の tier_quota に依る)。P4 の実効人数はこの縦煙が要る。
- 起床時刻のドリフトは 3 日で安定していたが、10 日ランでの確認は未実施。
- `engine.batch_llm` は本選 conf に無い = OFF = 計画呼は**完全直列**。並列化(`workers`)の seam は存在する(`scheduler.py:978-1004`)が、本選での採否は本書の範囲外。
