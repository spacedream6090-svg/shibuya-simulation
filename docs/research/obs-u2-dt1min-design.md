# OBS-U2 — Δt(1 step の分数)を 1 分にできる状態にするための設計調査

> ステータス: **調査報告(実装なし・コミットなし)**。2026-08-06 作成。
> 発端: [観察ラン ON 構成提案書](../plans/observe-run-config-proposal.md) §3 **OBS-U2**
> (推奨=本選本線は Δt=10 維持・GPU 余剰があれば Δt=1 の**並行小規模ラン**)。
> ユーザー指示: 「Δt を 1 分にできる準備はしておいてほしい」。
> 正典: [cognition-design-record.md](../plans/source/cognition-design-record.md) §3.1 / §5.1-5.3、
> 実装本体: `src/society/timeconv.py`(第79バッチ)/ `src/society/world/clock.py`。

---

## 0. 3 行サマリ

1. **Δt=1 は「作る」のではなく「もう動く」**。第79バッチの `run.dt_min` + `timeconv.TABLE`(130 キー)+ `Clock` 単一源化で土台は完成済みで、`run.dt_min=1` は実際に完走する(本調査で 1 シミュ日を実測)。準備作業は**新機構の追加ではなく、残った穴を塞ぐこと**である。
2. **ただし今 Δt=1 の並行小ランを走らせると、運用初日に落ちる**。`scripts/run.py --resume` が Δt≠10 で `apply_dt` を**二重適用**し、checkpoint 照合で `ValueError` になる(本調査で再現・Δt=10 では成功=Δt 固有)。観察ランの運用規約が「毎日 checkpoint」である以上、これが唯一の**確定ブロッカー**。
3. **設計上の推奨は案1(Δt を conf で通す既存路線の完遂)**。案2(移動だけ 1 分サブ刻み)は OBS-U2 の科学的動機を満たさない — 第83 が見つけた人工物は**思考**層(talking の基本周期 2 分 < Δt=10)にあり、実測でも **salience 発火が Δt=10 では 0 件、Δt=1 で 103 件**と、驚き駆動という主張そのものが Δt=10 では原理的に観測できない。移動だけ細かくしてもこれは救えない。

---

## 1. 「1 step = 10 分」の焼き付き全数表

### 1.0 既に吸収済みの中央機構(= 数えなくてよいもの)

| 機構 | 場所 | 役割 |
|---|---|---|
| `run.dt_min` | `conf/config.yaml:19`(既定 10)/ `src/society/registry.py:107-111`(off_value=10) | Δt の唯一の宣言点 |
| 分類テーブル | `src/society/timeconv.py:146-428`(130 キー: RATE / PROB / KEEP / **STEPS** / INVARIANT) | conf 定数の毎分レート化 |
| 唯一の変換点 | `src/society/config.py:239-240`(`load_config` 末尾で `apply_dt`) | 下流数百箇所は Δt を知らない |
| 恒等パス | `src/society/timeconv.py:532-533` | **Δt=10 ではテーブルを走査すらしない**(golden 担保) |
| 派生量の単一源 | `src/society/world/clock.py:26-53`(`steps_per_day` / `steps_per_hour` / `step_seconds` / `dur_steps` / `min_to_steps`) | 144 / 6 / 600 の直書き禁止 |
| 網羅性 CI | `tests/test_timeconv.py:200-238`(棚卸し正規表現 → TABLE 全載検査) | 宣言忘れの構造的防止 |
| Δt≠10 の実走 | `tests/test_timeconv.py:296-331`(Δt=5/1 完走・1 日統計が同オーダー) | 既に緑 |

**★重要な訂正(調査中に確認)**: 「モジュール既定値 `raw.get(key, N)` が `apply_dt` の外にあるので 20 件以上の穴が残る」という一次所見は**過大**だった。`conversation.c2.cooldown_steps` / `services.free_steps_ref` / `beliefs.fact_ttl_steps` / `ads.recall_steps` / `world.traces.half_life_steps` / `information.rumors.max_per_step` / `media.min_steps` / `indoor.markov.dwell_steps` / `commerce.inventory.lead_time_steps` / `drive.refractory_steps` / `env.feedback.gate.hold_steps` / `observer.echo.window_steps` / `observer.regression.window_steps` / `services.services.*.stay` はいずれも **`conf/config.yaml` に実在する**ため `apply_dt` が変換する(実測確認済み)。モジュール既定値は「部分 config を組む test / tool 経路」でしか到達せず、本番ランでは死んでいる。**残る本物の穴は下表に限られる。**

### 1.1 A 級 — Δt=1 で世界の因果が壊れる(Clock を経由していない直書き)

| # | 場所 | 式 | 時間量 | Δt=1 で起きること |
|---|---|---|---|---|
| A1 | `src/society/engine/scheduler.py:161` | `return delta // 10` | 分 → step 換算 | `clock.min_to_steps` 不使用。流入通勤者の翌朝到着(`:1145`)・宿のチェックアウト(`:4456`)までの待ちが **1/10 の実時間**になる |
| A2 | `src/society/engine/scheduler.py:3160` | `block_day = step // 144` | 口座 E5 の会計日境界 | **144 分(=2.4 時間)ごとに「1 日」**が回る。給料日・家賃引落・`block_day % 30` が 1 日 10 回発火 |
| A3 | `src/society/world/transit.py:140` | `((sim_min // 10) % self.headway) == 0` | バス便の有無 | `sim_min` が 1 ずつ進むのに 10 で割るため**同じ便判定が 10 step 連続** = headway が実質 10 倍 |
| A4 | `src/society/engine/scheduler.py:4876` + `:4678` | `_indoor_cell_offset(building, floor, step)`(第4引数省略)/ 既定引数 `float(STEP_MINUTES * 60)` | step 内オフセット秒 | 既定 600.0 秒が使われ、step 長 60 秒を超えるオフセットになる。**同関数の `:4906` は `sim.clock.step_seconds` を渡しており、同一ファイル内で不整合** |
| A5 | `src/society/tools.py:1150` | `(step - v["opened_step"]) // 144 < min_days` | 露店の開業経過日数 | 経過日数が 10 倍に数えられ、フルタイム化条件が即成立 |
| A6 | `src/society/engine/scheduler.py:3230` | `step + int(acc["bankruptcy_restrict_days"]) * 144` | 破産制限期間 [日→step] | 制限期間が 1/10(30 日 → 3 日相当) |
| A7 | `src/society/agents/memory.py:286` + `:51` | `max(1, step - t) ** (-d)` / `tau = -2.0`(コメント「単一参照が ≈55step≈9h で τ 割れ」) | ACT-R 基礎活性化 | step 差を時間単位に使うので冪乗則忘却が実時間で ≈3.2 倍速。**同じ Episode を評価する `recency_decay` は `src/society/engine/simulation.py:1421-1425` で `scale_keep` 済み** = 記憶モジュール内に二重基準が生じる |

### 1.2 B 級 — 変換の網の外(dormant だが Δt=1 の実験条件で踏む)

| # | 場所 | 内容 |
|---|---|---|
| B1 | `src/society/world/scenario.py:65-66` | `p.get("at_step")` / `p.get("duration_steps")`。**`world.scenario_params` は `conf/config.yaml:302` で `{}`** なので `apply_dt` の `_iter_targets`(実在キーのみ走査)にも、CI の棚卸し走査(`tests/test_timeconv.py:205-224` はコメント行を飛ばす)にも掛からない。scenario を使うランでのみ顕在化 |
| B2 | CI 走査の範囲 | `tests/test_timeconv.py:206` が読むのは `conf/config.yaml` のみ。`conf/production.yaml` / `daily.yaml` / `observe.yaml` / `profiles/*.yaml` は**走査対象外** = プロファイル固有の step 単位キーは宣言漏れが検出されない |
| B3 | `src/society/agents/agent.py:99` | `fire_weight: float = 0.5`(per-step Bernoulli。`scheduler.py:2354` で消費)。**persona 派生属性なので conf キーではなく TABLE に載らない** → Δt 未変換。生成は `src/society/factors/registry.py:53` |
| B4 | `src/society/world/traffic.py:55-57` | `steps_per_hour` / `steps_per_day` / `step_seconds` を Clock ではなく自前で再導出。**追随はするが Δt 由来量の第2の源**(`clock.py:26` の「単一源」設計に反する) |
| B5 | `src/society/world/zones.py:113` | `max_sub_steps: 12000`(= 600s/0.05s の直書き)。Δt=1 では過大で無害だが、**Δt>10 では `physics.py:331` の `n_sub = min(max_sub_steps, step_seconds/dt)` が積分を打ち切る** |
| B6 | `src/society/engine/scheduler.py:3895` | 記憶テキスト `f"取り締まりで{det * 10}分間…"`。**プロンプト入力なので、Δt=1 では実際の 10 倍の分数をエージェントが信じる**(認知汚染) |

### 1.3 C 級 — 解析・観測側(世界は壊れないが、Δt=10 ランとの比較で結論が歪む)

`STEPS_PER_DAY = 144` / `MIN_PER_STEP = 10` / `STEP_MINUTES = 10` / `SIM_MIN_PER_DAY = 1440` をモジュール定数として持つファイルが **30 本**(`scripts/` 29 + `viz/make_viewer.py` 1)。並行小ランの目的が「Δt=10 ランとの比較」である以上、ここは**必ず通る**。

主なもの: `scripts/observe.py:36-37` / `scripts/build_panel.py:43-45` / `scripts/calibrate_report.py:49-51` / `scripts/summarize_run.py:66` / `scripts/measure_sigma.py:88` / `scripts/detect_emergence.py:43` / `scripts/analyze_structure.py:57` / `scripts/analyze_flows_grid.py:54-55` / `scripts/commercial_report.py:46-47` / `scripts/diagnose_stationarity.py:92` / `scripts/live_viewer.py:92` / `scripts/export_3d.py:86` ほか。

**既に正しい 2 つの前例**があり、これがそのまま処方箋になる:
- `scripts/analyze_firing.py:306` — `cfg.run.dt_min` を run dir の `config.yaml` から読む。
- `scripts/analyze_structure.py:85-88` — **`sim_min // 1440` を第一手段とし、欠損時のみ `step // STEPS_PER_DAY` へ後退**。L1 は固定列に `sim_min` を持つ(`docs/research/data-pipeline-lit.md:61`)ので、この形なら Δt に一切依存しない。

観測側の純粋直書き(conf 経路すら無いもの): `src/society/observer/measure.py:35`(`ECHO_WINDOW_STEPS = 144`)・`measure.py:831` / `observer/stream.py:394`(`window: int = 24`)・`observer/norms.py:298-299`(規範成立の遅れを step 単位のまま L2 へ出力 = ラン横断比較で 10 倍ずれる)。

### 1.4 D 級 — 既に Clock 経由(良い実装例。触らない)

`src/society/tools.py:656-661`(`steps_per_hour` / `step_minutes`)・`src/society/cognition/routine.py:488,873,918,960` と `scheduler.py:1148,3727`(`clock.dur_steps` 経由)・`src/society/physics.py:329-331`(`clock.step_seconds` からサブステップ数を自動決定)・`src/society/agents/persona.py:194-198`(**draw を一切動かさず step 単位だけ読み替える**イディオム)・`src/society/envfeedback.py:198,403`(`_dt_min(sim)` 経由)・`src/society/observer/initial_frame.py:41-45` / `health.py:130` / `rules.py:154`(既定引数は正準だが呼び出し側が `clock.*` を渡す)。

---

## 2. Δt を変えると壊れるものの分類

### (a) 決定論・golden — **無風(証明済み)**

`run.dt_min` は conf キーであり、Δt=10 では `apply_dt` が config を 1 バイトも触らない(`timeconv.py:532-533`)。golden(`tests/data/golden_baseline_l1.json`)は Δt=10 の世界なので不変。`tests/test_timeconv.py:138-160` が「明示 `dt_min=10` でも L1 バイト一致」を固定済み。
**Δt≠10 は明示的に「別の世界」**(乱数消費列が変わる)であり、要求されるのは同一性ではなく 1 日あたり統計量の同オーダー(`timeconv.py:45-46`)。

### (b) LLM 呼数 — **×1 ではない。実測 ×2.2〜2.4**(かつそれは**バグではなく目的**)

正典 §5.1 は「LLM 呼び出し ∝ 総発火数 → **×1**」と主張する(`cognition-design-record.md:251-266`)。実装はその方向に設計されている:

| 経路 | 粒度 | 証拠 |
|---|---|---|
| 周期発火 `periodic` | **分**(較正表 `base_period[ctx].mean_min`) | `src/society/cognition/fire.py:355-381`・再予約は `sim_min + _period_min`(`:553-554,:574`)・分類 INVARIANT(`timeconv.py:285-288`) |
| 朝計画 / 夜内省 | per-day / per-sleep(予算外の無条件呼び出し) | `scheduler.py:809,1149,2805,4457`・`docs/research/finals-llm-budget.md:25-49` |
| `lod.max_llm_per_step` | RATE = 線形 → 300 → 30。**1 日 cap 総量 43,200 は保存** | `timeconv.py:197`・`tests/test_timeconv.py:272-279` |

**しかし実測は ×1 にならない**(mock backend・12 体・1 シミュ日・seed 42・本調査で採取):

| 条件 | Δt=10 (144 step) | Δt=1 (1440 step) | 比 |
|---|---|---|---|
| 既定(cognition OFF) LLM 呼数 | 102 | 227 | **×2.23** |
| 既定 L1 イベント総数 | 1,716 | 6,296 | ×3.67 |
| cognition ON: LLM 呼数 | 100 | 244 | **×2.44** |
| cognition ON: `cog_fire` | 1,020 | 1,840 | ×1.80 |
| cognition ON: L1 イベント総数 | 2,628 | 8,230 | ×3.13 |
| cognition ON: `cog_fire.reason` 内訳 | periodic 997 / internal 23 / **salience 0** | periodic 1,586 / internal 151 / **salience 103** | — |

**★この増分の正体**(調査で切り分け済み):

1. **主因は「Δt=10 が発火を潰していた」ことの解放**。`CogQueue` は 1 エージェントにつき生きたイベントを高々 1 個しか持たず(`fire.py:163-164`)、`advance()` は**より早い時刻へのみ**繰り上げる(`fire.py:185-190`)。文脈別基本周期は talking 2.0 分 / walking 8.0 分(`conf/cognition/calib_default.yaml:49-61`)で、**どちらも Δt=10 より短い**。したがって Δt=10 では常に periodic が先に due になり、**salience 割込みが構造的に一度も表に出ない**(実測 0 件)。これは第83 が実測した「talking の CV≈0 / B≈−1」の同じ現象の別の顔である。
2. **`fire_weight` の未変換は主因ではない**。`scheduler.py:2354` の per-step Bernoulli(`fire_weight`≈0.5)は TABLE の網外だが、これを `scale_prob` で Δt 補正して再実測すると **LLM 呼数 244 → 231・`cog_fire` 1,840 → 1,898** とほぼ動かない。**呼数増は未変換バグの副作用ではなく、驚き駆動が本来の解像度で動き出したことそのもの。**

> **結論**: Δt=1 の並行小ランでは **LLM 呼数を「同規模で ×2〜2.5」と見積もる**。「×1 だから人数据え置きで走る」は誤り。逆に「per-step 発火だから ×10」も誤り(周期が分単位・plan/reflect が per-day なので 10 倍にはならない)。

### (c) 営業時間・ダイヤ・天候・日次境界 — **概ね無風。例外 3 件**

- 営業時間は `open_min` / `close_min`(分 of day)基準(`src/society/world/worldmod.py:190,208`)= Δt 非依存。
- 天候は**日次確定**(`timeconv.py:404-409` で INVARIANT 宣言・理由付き)= 無風。
- 日境界の正準定義は `clock.day(step) = sim_min // 1440`(`clock.py:61-67`)で `start_tod` にも追随する = 無風。
- **例外**: A2(`step // 144` の会計日)・A3(バスの `sim_min // 10`)・A6(破産日数 `* 144`)。
- ★A2 の是正には注意: `start_tod="07:00"` では `step // 144` の境界(step 144)と `sim_min // 1440` の境界(step 102)は**一致しない**。`clock.day()` に置き換えると Δt=10 でも挙動が変わり golden を壊す。**`step // clock.steps_per_day` に置き換える**のが唯一のバイト一致経路(A5 も同様)。

### (d) 較正済みパラメータ — **σ_c は再測が必須。θ はその従属**

- `cognition.fire.*`(周期・θ 倍率)は全て**分・無次元**なので INVARIANT(`timeconv.py:280-294`)= 形式上は Δt 非依存。
- **しかし σ_c は違う**。観測チャンネルの一部は「**この step の件数**」というカウント量(`src/society/cognition/channels.py:106-113` の `ext.heard` / `ext.signage`)であり、`data/calib/sigma_c.json` は Δt=10 で測った母集団の分散。Δt=1 では 1 step あたりの件数が減るので σ_c が過大になり、S = Σ g|o−ô|/σ が系統的に小さくなる → **salience 発火が減る方向にバイアス**する。
- **照合機構が無い**。`sigma_c.json` の meta は `n_agents / n_steps / seed` のみで `dt_min` を持たず、`src/society/cognition/calib.py` に Δt 検査はゼロ。`data/calib/theta_scale.json:77` は `dt_min: 10` を記録するが**助言的で実行時チェックが無い**。
- θ 較正(`scripts/calibrate_theta.py:548`)は `MINUTES_PER_DAY // base.run.dt_min` で steps_per_day を導いており **Δt 対応済み**。σ_c を測り直せば θ もそのまま再較正できる。

### (e) checkpoint / resume — **★確定ブロッカー(本調査で新規発見)**

**症状**: `scripts/run.py --resume` は Δt≠10 で**必ず失敗する**。

**機序**: `scripts/run.py:109` が `load_config(overrides=overrides, path=run_dir / "config.yaml")` を呼ぶ。保存済み `config.yaml`(`config.py:244-246` / `simulation.py:1646,1741`)は**既に `apply_dt` 済み**なのに `run.dt_min: 1` を保持しているため、`load_config` 末尾の `apply_dt`(`config.py:239-240`)が**二重適用**される。`apply_dt` は冪等ではない。

```
run.dt_min=1 の実測(本調査):
  walk 速度        800.0 → 80.0(正)→ 8.0(誤・二重)
  refractory_steps    3 →   30(正)→ 300(誤・二重)
  max_llm_per_step  300 →   30(正)→   3(誤・二重)
```

**顕在化の仕方**: 幸い silent corruption ではなく**ハードエラー**になる。`run.dt_min` は `checkpoint.py:34-40` の `_VOLATILE_KEYS` に含まれないので `config_hash` に入り、`checkpoint.py:308-313` が不整合を検知して `ValueError` を投げる。ただし**エラー文は「seed/n_agents/因子など resume 対象外のキーが変わっている可能性」**であり、真因(二重変換)を全く指さない。

**再現(本調査で実行)**:
```
run.py run.dt_min=1  … 20 step + checkpoint → rc=0、--resume → rc=1(ValueError)
run.py run.dt_min=10 … 同一手順          → rc=0、--resume → rc=0   ← Δt 固有
```

**なぜ既存テストが緑なのか**: `tests/test_timeconv.py:334-357` の Δt=5 resume テストは `load_config([... "run.dt_min=5" ...])` を**両方 dotlist から新規に組む**ため、保存済み config を読み直す `scripts/run.py` の経路を一度も通らない。`load_config(path=<run dir>/config.yaml)` を使う場所はリポジトリ全体で `scripts/run.py:109` の**1 箇所だけ**である。

**観察ランの運用規約は「毎日 checkpoint(いつ打ち切っても成果)」**(提案書 §5)なので、これを直さない限り Δt=1 の並行小ランは 1 日で詰む。

### (f) L1 の量と観測系 — **素で ×3〜4(理論上限 ×10)。間引きキーは手動 ×10 が前提**

実測は上表のとおり **L1 総数 ×3.1〜3.7**(理論の ×10 に届かないのは、大半のイベントが event-driven だから)。増分の支配項は **1 step につき 1 行出る観測行**:

| 出力 | 粒度 | Δt=1 |
|---|---|---|
| `move_segment`(`scheduler.py:1055`・schema「経路に沿った1stepの前進」) | per-移動者 per-step | 実測 240 → 2,655 |
| `traffic_flow`(`scheduler.py:1174`・schema「背景交通の1step分の軌跡」) | **1 行/step** | 実測 144 → 1,440(厳密 ×10) |
| `drive_request`(`scheduler.py:2363`) | per-申請者 per-step | ×2 前後(申請者数に依存) |
| L2 metrics(`scheduler.py:5122`) | **毎 step 1 行(無条件)** | ×10 |
| L3 snapshot(`observer.snapshot_every`) | STEPS 分類 = 逆比例(`timeconv.py:222`) | **×1**(実時間粒度を保つ) |

**観測間引きキーは意図的に INVARIANT**(実験者が指定する量): `observer.flush_every_steps`(`timeconv.py:272-273`)/ `observer.state_hash.interval`(`:274`)/ `cognition.channels.every_steps`(`:275-279`)/ `cognition.g_update.log_every_steps`(`:330-332`)/ `env.feedback.log_every_steps`(`:334-335`)。**Δt=1 では実験者がこれらを手で 10 倍にしないと出力が 10 倍になる** — 実時間粒度を保つのは `snapshot_every` だけである。これは設計判断であって不具合ではないが、**プロファイルとして固めておかないと必ず踏む**。

---

## 3. 選択肢の比較と推奨

### 案1 — `run.dt_min` を通す既存路線の**完遂**(残った穴を塞ぐ)

| 項目 | 評価 |
|---|---|
| 実体 | 新機構ゼロ。§1.1 の A 級 7 件 + §2(e) の resume 修正 + §1.3 の解析側 dt 対応 |
| 工数 | 中(下記 §4 で 6 バッチ・うち B1+B2 の 2 本で「走る」状態になる) |
| golden リスク | **ゼロにできる**。全修正が Δt=10 で恒等になる形に書ける(`clock.steps_per_day` 置換・`dur_steps` 置換・`scale_*` は `dt==10` で早期 return) |
| 得られるもの | Δt が**実験パラメータ**になる(Δt 掃引が条件として使える)。恒久資産 |
| リスク | σ/θ 再較正が必要(§2(d))。Δt=1 は別世界なのでラン間比較のみ |

### 案2 — 移動・物理だけ 1 分サブ刻み(認知は 10 分固定)

| 項目 | 評価 |
|---|---|
| 既存足場 | **無い**。物理サブステップは `physics.py:329-331` にあるが**宣言済みゾーンの内側限定**で、`engine/scheduler.py:5008` の `physics_mod.phase()` 1 行呼び出しに閉じている。`_phase_move` の内側ループ(`scheduler.py:1025-1040`)は**距離予算のループであって時間サブステップではない** — 1 step ぶんの移動距離を一括で消費する |
| 工数 | **大**。`physics.phase` と同型の第2の中立フックを `_phase_move` に新設し、遭遇判定・混雑度・チャンネル観測をサブステップ側へ移す = 時間軸が 2 本になる |
| **致命的な問題** | **OBS-U2 の動機を満たさない。** 第83 の人工物は思考層(talking の基本周期 2 分 < Δt=10)にあり、実測でも salience 発火が Δt=10 で **0 件**。認知を 10 分に固定したまま移動だけ細かくしても、**驚き駆動という主張の中核が観測できないまま**である |
| 設計正典との関係 | §3.1 の三層表は「移動・遭遇 Δt=1 分 / 思考はクロックなし」。実装では思考層は既に `sim_min` ベースのイベントキュー(`fire.py:157-217`)= **クロックなしは達成済み**で、それを Δt が量子化しているだけ。つまり `run.dt_min=1` こそが §3.1 の「Δt_move=1 分」そのもの。**案2 は既にある時間軸の隣にもう 1 本作る重複投資** |

### 案3 — 1 分ネイティブの専用プロファイル(cognition 発火を 1/10 に RATE 換算)

| 項目 | 評価 |
|---|---|
| 工数 | 小 |
| **致命的な問題** | 呼数を据え置くために発火を人工的に間引くことになり、**案2 と同じく salience 発火の解放を潰す**。「Δt を細かくしても思考の総量は変わらない」(§5.1)は*結果として*そうなるべき性質であって、*強制して*作る性質ではない。強制した瞬間、Δt=1 ランは「何も新しく見えないラン」になる |
| 部分的に有用な点 | **観測間引きキーの ×10 と `n_steps` の ×10 をプロファイル化する**という部分だけは必要(§2(f))。ただしそれは認知の抑制とは無関係 |

### ★推奨: **案1 を完遂し、案3 の「プロファイル」部分だけを薄く採る**

理由:
1. 土台は既に 9 割完成しており、案2/案3 は**新しい時間軸か新しい抑制機構を足す** = 第79 の投資を捨てる方向。
2. OBS-U2 の学術的価値は「**Δt=10 では原理的に見えなかったものが見える**」ことにある。実測で示された唯一の質的差分が **salience 発火 0 → 103** であり、これを保存する案は案1 だけ。
3. 呼数は実測 **×2.2〜2.4**。並行小ランは規模を落として走らせる前提(提案書 §3「GPU 余剰があれば並行小規模ラン」)なので、この倍率は十分に飲める。
4. 案1 の副産物として **Δt が実験条件になる**(Δt 掃引 = ABM 検証の標準段。第79 のリサーチ根拠)。並行小ランが失敗しても資産が残る。

**並行小ランで何が観察できるようになるか**(P4 較正との接続):
- **驚き駆動の直接証拠**: salience 発火(Δt=10 では観測不能)と、第83 の発火連鎖グラフ(lag=1)が 1 分解像度になる。「A の行動 → B のチャンネル → B の発火」の因果経路が 10 分の丸めなしで辿れる。
- **思考頻度分布の真値**: talking の CV≈0 / バースト指標 B≈−1 は Δt=10 の丸め人工物だった。1 分解像度なら CV とバースト性が**世界の性質として**測れる(第83 の宿題の回収)。
- **交差点レベルの人流検証(P4 接続)**: 現行の `move_segment` は 10 分ぶんの直線補間で、`physics.py` のゾーン外は Δt 粒度のまま。1 分刻みなら OD 通過・信号周期(`world.traffic.signal_cycle_s` は INVARIANT = 実秒)との突き合わせが意味を持ち、P4-2 で是正した RiMEA 物差し(流れ方向 2m ×全幅)と**同じ土俵**で街路スケールの流量を検証できる。ただし**ゾーン外の移動が 1 分刻みになるだけで SFM にはならない**点は明示しておくこと(P4 の較正結果をそのまま街路へ外挿はできない)。

---

## 4. 推奨案のバッチ分解

**全バッチ共通の受入条件**: ① `run.dt_min=10`(既定)で **L1 バイト一致**(golden 無風)、② `apply_dt` の恒等パス(`timeconv.py:532-533`)を壊さない、③ 新規キーを足したら `timeconv.TABLE` と `registry.py` の両方に宣言(既存 CI が落ちる形)。

### B1 — resume の二重変換を塞ぐ(**最優先・これだけで「走る」**)

- 対象: `scripts/run.py:109` / `src/society/config.py:203-241`。
- 方針: `load_config` に `apply_dt: bool = True` を足し、resume 経路だけ `False` を渡す(**config のバイト列を一切変えない**ので Δt=10 は完全無風)。代替案は `apply_dt` が適用済みマーカーを書く形だが、こちらは config の中身が変わるので不採用を推奨。
- 副次: `checkpoint.py:311-313` のエラー文に「`run.dt_min` が checkpoint と異なる場合はここに出る」旨を 1 行足す(現状の文言は真因を指さない)。
- テスト: (1) Δt=1 で `run → checkpoint → --resume` が完走し、一気通しと L1 バイト一致。(2) Δt=10 の同テスト(回帰)。(3) `load_config(path=保存済み config)` が二重変換しないことの単体検査(walk 速度・`refractory_steps`・`max_llm_per_step` の 3 キー)。

### B2 — A 級直書き 7 件の Clock 化

- `scheduler.py:161` → `sim.clock.min_to_steps(delta)`(Δt=10 で `delta // 10` と同値)。
- `scheduler.py:3160` → `step // sim.clock.steps_per_day`(**`clock.day()` にしない** — `start_tod` 起因で Δt=10 でも境界が動き golden が壊れる)。
- `scheduler.py:3230` → `* sim.clock.steps_per_day`。
- `scheduler.py:4876` → 第4引数に `sim.clock.step_seconds` を渡す(`:4906` と同形)。ついでに `:4678` の既定引数を必須引数に昇格すると再発を防げる。
- `tools.py:1150` → `// sim.clock.steps_per_day`。
- `transit.py:140` → `((sim_min // clock.step_minutes) % self.headway) == 0`(`Bus` が Clock を持たないなら `step_minutes` をコンストラクタで受ける。`traffic.py:55-57` と同じ配線)。
- `memory.py:286` → 経過 step を正準 step へ読み替える(`(step - t) * dt / 10`。Δt=10 で恒等)。`:51` のコメントの τ 根拠も更新。
- テスト: 各修正点について「Δt=10 で従来値と厳密一致」+「Δt=1 で実時間が保たれる」の 2 本ずつ。`scheduler.py:3895` の記憶テキスト(B6)は `det * sim.clock.step_minutes` に直して**プロンプト文字列テスト**で固定(Δt=10 で 1 バイト不変)。

### B3 — 較正テーブルの Δt 来歴と照合

- `data/calib/sigma_c.json` の meta に `dt_min` を追加。`src/society/cognition/calib.py` のロード時に config の `run.dt_min` と突き合わせ、不一致なら **WARNING + manifest 記録**(エラーにはしない — Δt 掃引そのものを塞いでしまうため)。`theta_scale.json:77` の `dt_min` も同じ検査に乗せる。
- `scripts/measure_sigma.py:88` の `STEPS_PER_DAY = 144` を run config 由来に。
- Δt=1 用の σ_c 再測は**実 LLM 診断日(8/15-16)の枠外**に置く。mock で先に手順だけ通しておく。

### B4 — 解析側の Δt 対応(比較の土台)

- 共通ヘルパ 1 本(例 `scripts/_runmeta.py`)に `dt_min_of(run_dir)`(`analyze_firing.py:306` の形)と `day_of(row, dt)`(`analyze_structure.py:85-88` の **sim_min 優先 + step 後退**の形)を切り出す。
- **並行小ランの比較に実際に使うものだけ**を先に移す: `summarize_run.py` / `observe.py` / `build_panel.py` / `calibrate_report.py` / `detect_emergence.py` / `measure_sigma.py` / `analyze_flows_grid.py`。残り 23 本は「Δt=10 前提」を冒頭コメントで**明示**するだけに留め、必要になった順に移す(全数一括は費用対効果が悪い)。
- `observer/norms.py:298-299` の `norm_steps_to_agreement` に**分換算列**を併記(step 列は残す = 既存 L2 契約を壊さない)。

### B5 — 並行小ラン用プロファイル `conf/profiles/dt1-parallel.yaml`

- `run.dt_min: 1` / `run.n_steps` を ×10 / 観測間引きキーを ×10(`observer.flush_every_steps` / `observer.state_hash.interval` / `cognition.channels.every_steps` / `cognition.g_update.log_every_steps` / `env.feedback.log_every_steps`)/ 規模は小(人数は実測で決める)。
- **ON セットは観察ラン本線と同一**にする(提案書 §1)。比較対象が Δt だけになるように、他の条件を 1 つも動かさない。
- 冒頭コメントに「これは**別の世界**であり、Δt=10 ランと step 単位では対応づかない。比較はラン間の統計量のみ」と明記。

### B6 — `fire_weight` の Δt 変換(**低優先・科学的判断を要する**)

- `agent.py:99` の per-step Bernoulli は TABLE の網外(§1.2 B3)。修正するなら `persona.py:194-198` の既存イディオム(**draw を動かさず値だけ読み替える**)に沿って `scale_prob(fire_weight, dt_min)`。
- ただし実測では **修正しても呼数は 244 → 231 とほぼ動かない**。「Δt 不変性の形式的完成」以上の実利は無く、逆に `drive.on_reject` の per-event 減衰(`timeconv.py:383`)との相互作用で挙動が変わる。**入れる/入れないをユーザー判断に上げる**のが正しい。

### B7 — 網羅性 CI の穴埋め(小)

- `tests/test_timeconv.py:206` の走査対象に `conf/production.yaml` / `daily.yaml` / `observe.yaml` / `conf/profiles/*.yaml` を追加(§1.2 B2)。
- `world.scenario_params.at_step` / `.duration_steps` を TABLE に載せる(§1.2 B1)。値が `{}` でも `covers()` は宣言として意味を持つ。

**依存関係**: B1 → (B2 と並行可) → B5 で走る。B3/B4 は結果を読むために必要。B6/B7 は独立。
**最小構成で「並行小ランが走る」のは B1 + B2 + B5**。

---

## 5. 残リスク

| # | リスク | 深刻度 | 備考 |
|---|---|---|---|
| R1 | **σ_c の再測が必須**。`channels.py:106-113` の per-step カウント量が Δt で変わるため、Δt=10 の σ_c を流用すると salience 発火が系統的に過小になる | **高** | B3 で検知はできるが、値そのものは測り直すしかない。実 LLM 枠(8/15-16)が埋まっているなら mock 較正で暫定を置き、その旨を manifest に残す |
| R2 | **Δt=1 は別の世界**(乱数消費列が変わる)。step 単位・個体単位の対応づけは原理的に不可能 | 高(仕様) | `timeconv.py:45-46` の明文規約。比較は必ず**ラン間の統計量**で。査読で問われる点なので論文側の書き方を先に決めておく |
| R3 | **実測は mock backend・12 体・1 日**。実 LLM では発話長・返答率が変わるので呼数比 ×2.2〜2.4 は動きうる | 中 | 第83 の教訓「呼数/人/日は人数不変でない」がそのまま効く。**外挿でなくパイロット実測で決める** |
| R4 | 案1 を完遂しても **ゾーン外の移動は 1 分刻みの直線補間**であって SFM ではない | 中 | P4 の較正値を街路スケールへそのまま外挿できない。並行小ランの主張範囲を「遭遇・思考の時間解像度」に限定するのが安全 |
| R5 | **L1 が ×3〜4**。10 日 × 本線規模ではなく小ランなので絶対量は小さいが、`flush_every_steps` を上げ忘れると part 数が 10 倍になる | 中 | B5 のプロファイルで固定する。`state_hash` は観察ランで OFF 推奨(提案書 §2)なので影響外 |
| R6 | `traffic.py:55-57` が Clock を経由しない**第2の Δt 源**。今は追随するが、将来 Clock 側だけ直すと不整合になる | 低 | B2 の範囲外。TODO コメントで固定するのが妥当 |
| R7 | `zones.py:113` の `max_sub_steps: 12000` は **Δt>10 で物理積分を打ち切る** | 低(Δt=1 では無害) | Δt 掃引を上方向にもやるなら要修正 |
| R8 | 観測間引きキーが INVARIANT なのは**設計判断**であり、Δt を変えるたびに実験者が手で調整する運用が前提 | 低 | B5 で明文化。忘れると「ログが 10 倍で気づかない」形で出る |
| R9 | `scripts/run.py:109` 以外に保存済み config を読み直す経路が将来増えると B1 の修正が漏れる | 低 | `load_config(path=...)` の docstring に「保存済み config を読むときは `apply_dt=False`」と明記 + grep テストで固定 |

---

## 付録: 本調査で新規に判明した事実(既存文書に無いもの)

1. **`scripts/run.py --resume` は Δt≠10 で必ず失敗する**(`apply_dt` 二重適用 → `config_hash` 不一致 → `ValueError`)。Δt=10 では成功することを対照で確認。既存の Δt=5 resume テストは `scripts/run.py` の経路を通らないため検出できていなかった。
2. **salience 発火は Δt=10 では構造的に 0 件**(`CogQueue` の「生きたイベントは高々 1 個」+ 基本周期 2〜8 分 < Δt)。Δt=1 で 103 件。**驚き駆動という設計の中核が、現行 Δt では原理的に観測できない。**
3. **LLM 呼数は ×1 でも ×10 でもなく実測 ×2.2〜2.4**。正典 §5.1 の「×1」は周期・plan・reflect については正しいが、Δt による発火の抑圧が解ける分を勘定していない。
4. **`fire_weight` の Δt 未変換は呼数増の主因ではない**(補正しても 244 → 231)。増分は抑圧の解放そのもの。
5. **「モジュール既定値が変換の網の外」は過大な所見**。該当キーの大半は `conf/config.yaml` に実在し `apply_dt` が変換する。本物の穴は §1.1 の A 級 7 件と §1.2 の B 級 6 件に限られる。
6. `registry.py:107-111` は `run.dt_min` を **`affects_k=False`** と宣言しているが、`affects_k` の定義は「`generate()` の呼び出し点を足す/減らす/**予算を変える**か」(`registry.py:25-30`)であり、Δt は `lod.max_llm_per_step` を 300 → 30 に変え、呼数を実測 ×2.4 にする。**`affects_k=True` へ訂正すべき**(B2 に同梱可)。
