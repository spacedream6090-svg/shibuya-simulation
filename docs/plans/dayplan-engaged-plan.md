# day_plan v1 + engaged モード + 25万人転換 統合実装計画

> ステータス: **実装中**(2026-08-03 着手)。原文書: [source/design-discussion-20260802.md](source/design-discussion-20260802.md)
> (2026-08-02 受領・**概念決定済み・実装詳細は Claude Code 委任**と明記)+ユーザー指示(2026-08-03)
> 「僕の判断が必要ない実装は進めてもらって構わない」。
> 関連: [cognition-physics-plan.md](cognition-physics-plan.md)(第79〜85 完結)・[observe-run-config-proposal.md](observe-run-config-proposal.md)(OBS-U1〜U3 は 25万転換を受けて要改訂)。

## 1. 受領文書の要点と本リポの現在地

| 文書の決定 | 現行資産 | 差分 |
|---|---|---|
| **目標再定位: 第一目標=25万人で日常が回ること・創発はおまけ**(複数ラン比較で確かめる) | realism-first-scale 方針と整合。rehearsal_pool10k=1万体実績 | 規模目標が 1万→25万へ。総発火数 N×f×D 予算式で設計 |
| 決定と実行の分離(朝 LLM 計画→ルール実行・実効 4〜8呼/人/日) | planning.py(朝計画・自由文)+routine.py(習慣)+POI 解決既存 | **day_plan v1 構造化スキーマ**+priority×flex 割り込み+検証/修復/フォールバック |
| engaged モード(AUTOPILOT/ENGAGED 状態機械・エピソード化) | 第81 fire(点の発火)+θ較正(第83)+reply 機構 | **エピソード持続**+ヒステリシス(θ_out<θ_in)+不応期+両者 ENGAGED 会話成立+エピソードログ |
| プラセボ・アブレーション梯子 L0〜L4(L1=呼数/形式/乱数同一で中身だけ壊す) | 第78 ablate 4種(propagation_off=文脈遮断に近い)+registry | **L1 3種**(文脈シャッフル/ペルソナ入れ替え/文脈遮断)の呼数・乱数不変版 |
| 心=1体1モデル誕生時固定(fleet 混成=分散崩壊への対抗)・機械的判断は共有小型/ルール | finals-vllm7 の tiers・cognitive_tier ablate | **agent→model_id 固定 binding+ログ**・三層知能配置(基底/思考/高解像度 1〜5%) |
| モデル人間らしさバッテリー(A〜E 層・プラセボ対照・D層=分散が生命線) | calibrate_report・judge.py・語彙系解析 | **共通ハーネス**(同一プロンプト/シード/温度)+名大会話コーパス記述統計(CEJC は契約判断待ち) |
| 縦煙(N=2,500 全期間)/横煙(N=25万 数シミュ時間)+退行シグナル監視 | bench_scaling(〜1万)・estimate_runtime・echo/専門化系列 | 退行シグナル列(行動分散・訪問エントロピー・語彙エントロピー・n-gram 重複・発火率張り付き)+煙プロファイル |
| 検証は「合った指標/合わなかった指標の両提示」・較正と検証の分離 | 事前登録(U-10)・calibrate_report | サーベイ反映 S-01〜S-04(SV-U1)と同方向=統合して報告テンプレへ |

**訂正**: 原文書 §9 の「GPU 申請 8/9 前」は**申請提出済みのため消滅**。スループット実測(prefix caching 込み)は 8/15-16 診断ランに統合。

## 2. 実装順(第86〜・全て既定 OFF=golden 無風・R1 準拠)

| バッチ | 内容 | 状態 |
|---|---|---|
| 第86 | **day_plan v1**: 構造化スキーマ(メタ+ブロック4〜8+contingency≤3・列挙型中心・reason=生成時説明)+スキーマ/物理検証→決定的修復→フォールバック3段+**ルール実行系**(場所解決はルール側・priority×flex 割り込み=could/droppable は無料で削り must 危機のみ再計画発火・空き時間=習慣ポリシー) | **完了**(2026-08-03。§4 参照) |
| 第87 | **engaged モード**: AUTOPILOT/ENGAGED 状態機械・突入5条件(S>θ_in/社会的直接性バイパス/実行不能例外/欲求臨界/予定思考)・脱出4条件(解消/減衰=ヒステリシス/ターン上限12/プリエンプト→兆しメモリ1行)・不応期30分・両者 ENGAGED 会話成立・エピソードログ(トリガー/滞在/ターン/脱出理由/model_id) | **完了**(2026-08-03。§5 参照) |
| 第88 | **心モデル固定+三層知能**: agent→model_id 誕生時固定(専用 stream・manifest/ログ必須=交絡の記録)+基底/思考/高解像度層の conf 配置(高解像度 1〜5%) | **完了**(2026-08-03。§6 参照) |
| 第89 | **プラセボ L1 3種**(context_shuffle/persona_swap/context_sever): 呼数・フォーマット・乱数消費同一の中身破壊(第78 ablate 枠に追加・fingerprint_risk 正直宣言) | **完了**(2026-08-03。§7 参照) |
| 第90 | **バッテリーハーネス**(scripts 系): 共通ハーネス(同一プロンプト/シード/温度)+A層(社会生活基本調査比較)/B層(摂動応答)/C層(会話統計・名大コーパス)/D層(分散比=生命線)/E層(長期退行)+プラセボ対照 | 計画済み |
| 第91 | **退行シグナル監視+縦横煙プロファイル**: L2 監視列(分散・エントロピー・n-gram・発火率)+縦煙(2,500全期間)/横煙(25万数時間)conf+判定基準 | 計画済み |
| 並行 | 保守バッチ: LLM 呼び出しハードデッドライン(本選前必須バグ)・serial マーカー・dunbar×pool 幅拡張・竹-4 持ち越し①②・exit_building 調査 | 実装中 |

## 3. ユーザー判断待ち(本計画から発生)

| # | 事項 | 補足 |
|---|---|---|
| DP-U1 | **CEJC(日本語日常会話コーパス)の有償契約**の可否と時期 | 間に合わなければ名大会話コーパス無償統計で C 層を回す(実装はその前提で先行) |
| DP-U2 | **心モデル候補の最終ショートリスト**(3B〜14B×5〜6本+プラセボ1本) | バッテリーハーネス完成後に候補リスト+実測を添えて提案する |
| DP-U3 | **観察ラン構成の 25万転換への改訂**(OBS-U1 の人数前提・fleet 構成・engaged/day_plan を本選 ON にするか) | 8/15-16 診断ラン前に改訂版提案書を出す |

## 4. 第86バッチ 実装記録(2026-08-03 完了)

**conf**: `planning.day_plan.enabled`(既定 **false**)。実装 `src/society/cognition/day_plan.py`。

### 4.1 スキーマ(列挙の棚卸し結果)

| 欄 | 型 | 値 | 既存資産との対応 |
|---|---|---|---|
| `act` | 列挙 12 | work, study, meal, shop, leisure, park, walk, home, visit, personal, escort, meetup | `plan_schema._DEFAULT_VOCAB`(11)+ `routine._WHAT_CAT` の meetup。**新語ゼロ** = 既存の what→cat3 / what→POI カテゴリ写像が 1 行も改変なしで効く。ActivitySim の目的列挙(work/school/escort/shopping/othmaint/othdiscr/eatout/social)へ 1 対 1 で写る |
| `place` | 列挙 15 | home, work, street + food, nightlife, shop, service, office, education, hotel, attraction, leisure, landmark, cinema, hall | 実地図が生む POI カテゴリ(`scripts/build_map.poi_category`)+ ルールだけで解ける 3 つ。**具体店名は書かせない** |
| `purpose`(prompt 上は `aim`) | 列挙 10 | livelihood, learning, sustenance, errand, care, health, rest, company, enjoyment, long_goal | 全メンバが mandatory/maintenance/discretionary へ決定論写像(`PURPOSE_CAT`)。`long_goal` は inner_life の `agent.life_goal` への紐づけ。★原文書の「7欲求」に相当する 7 次元は本リポに無い(factors 層の 5 次元は cognition から名指し禁止=no-fingerprint)ので、**cognition から見える体系**へ紐づけた |
| `priority` | 列挙 3 | must / should / could | 割り込みの心臓部(§7) |
| `flex` | 列挙 3 | fixed / slideable / droppable | 同上 |
| `if` / `then` | 列挙 7 / 5 | rain, crowded, closed, tired, no_money, late, invited / skip, postpone, go_home, swap_indoor, shorten | 既存機構(weather / envfeedback / commerce / health / economy / slide / joint)に対応する語だけ |
| 自由文 | 4 欄 | mood, carry, reason, note | **reason は各ブロックの先頭**(構造化出力は自己回帰=キー順が生成順) |

メタ: `agent_id`(イベントの agent_id)/ `day` / `model`(= backend 名。1体1モデル束縛は第88)/
`plan_version`(再計画で ++)/ `mood` / `carry`(昨日からの持ち越し)。ブロック 4〜8・contingency ≤3。

### 4.2 作用点(いずれも単一)

| 何 | どこ | OFF の保証 |
|---|---|---|
| 生成 | `planning.build_plan_request` / `apply_plan_response` の 1 分岐(逐次経路・`batch_llm` 一括経路の両方がここを通る) | `dpcfg is None` で従来経路=プロンプト 1 バイト不変 |
| 実行 | `routine.decide` の朝計画スロット 1 行(`_plan_move` と三項で差し替え) | `enabled(sim)` が False なら従来の `_plan_move` を素で呼ぶ |
| 例外→発火 | `day_plan.note_plan_exception` → 第81 `CogQueue.advance(INTERNAL)` | `cognition.fire` OFF(既定)で完全 no-op |

### 4.3 検収(mock のみ・実 LLM ランなし)

- **既定 OFF**: 純粋既定と L1 完全一致(144step)・**RNG stream 取得 3176 = 3176 で内訳も一致**・
  LLM 呼数 119 = 119・`_dayplan_state` 不在・L2 に 7 列なし・summary にキーなし・
  golden(`test_scenario`)緑。
- **ON(mock)**: 同 seed 2 ラン L1 バイト一致 / resume==straight(l1/l2/l3 parquet 一致・
  `_dayplan_state` と計画本体の round-trip)/ `compute_matched` 下で k=free と k=off の呼数一致 /
  朝の計画呼は **1 人 1 回**(`plan_retry` ゼロ=再試行を撃たない)/ no-fingerprint(機構語・
  実験条件語・因子名がプロンプトに出ない)。
- **実測**(mock・seed42・40体):

  | ラン | 計画 | ブロック | ブロック/計画 | 実行率 | 自動削除率 | 全修復率 | **矛盾修復率** | 後退率 | 再計画 |
  |---|---|---|---|---|---|---|---|---|---|
  | 24step(05:00 開始+natural_start) | 35 | 209 | 5.97 | 0.120 | 0.010 | 1.000 | **0.886** | 0.000 | 5 |
  | 288step(2 シミュ日) | 47 | 269 | 5.72 | 0.461 | 0.253 | 1.000 | **0.851** | 0.000 | 37 |

  読み方: 全修復率が 1.0 に張り付くのは時刻グリッドへの丸め(`round`)がほぼ毎回起きるため。
  バッテリー指標として意味があるのは **矛盾修復率**(ずらし/短縮/差し替え/削除/上限)。
  24step の実行率が低いのは窓が 4 時間しかないため(計画は一日ぶん立つ)。
  後退率 0 は mock が常に妥当 JSON を返すからで、**実 LLM(3B〜14B)では
  SchemaBench の非適合率(parse error 18〜36%)ぶんが後退経路に出る想定**。
  修復・後退の件数と率は `summary.json` の `day_plan.by_model` にモデル別で残る。
- **テスト**: `tests/test_day_plan.py` 新規 **50 本**。フルゲート `pytest tests -q -n auto` 緑。

### 4.4 やっていないこと(第87 以降)

engaged 状態機械本体・心モデル固定・`planning.py` の Perception 契約化は着手していない。
本バッチの「再計画」は**ルール内の作り直し**(低優先の削除+ずらし+`plan_version`++)であって
LLM エピソードではない。`plan_exception` は fire キューへの前倒し登録までで、
エピソードの持続・脱出条件は第87 の仕事。

## 5. 第87バッチ 実装記録(2026-08-03 完了)

**conf**: `cognition.engaged.enabled`(既定 **false**・**`cognition.fire` ON が前提**)。
実装 `src/society/cognition/engaged.py`。

第81(fire)が答えたのは「**いつ**考えるか」= **点**(発火時刻の全順序キュー)。
本バッチが足すのは「**いつまで**考えるか」= **区間**(エピソード)。

    AUTOPILOT … スクリプト実行・LLM 呼びゼロ
    ENGAGED   … 会話(talk)/ 再計画(replan)/ 内省(reflect)のエピソード

### 5.1 状態機械(既存 fire との関係)

| 位相 | 何をするか | どこ |
|---|---|---|
| `pre_tick` | 生きているエピソードの継続を `CogQueue` の「今」へ**繰り上げる**。これが点→区間の実体で、繰り上げた個体は `due_events` の通常経路(S 計算・ô 更新・plasticity・再スケジュール)を**そのまま**通る = fire の内部規約を 1 つも迂回しない | `_phase_drive` の `due_events` **直前** |
| `update` | **脱出 4 条件 → 突入 5 条件**の順に評価し、割込み権(id 集合)を返す。順序が脱出→突入なのは、プリエンプトが**同じ tick で**次のエピソードへ移れるようにするため | `_phase_drive` の `due_events` 直後(返り値は既存 `forced` に合流) |
| 割込み権 | ENGAGED の在場個体は `interrupt=True` 扱い = **抽選を飛ばす確定発火**(対面会話・驚き割込みと同格)。**新しい呼び出しサイトではない** | 既存 `requesters` の判定式 |

**突入 5 条件**(判定順 = 今この場の相手 > 例外 > 欲求 > 予定 > 驚き):

| # | §8 | 実装 | 種別 |
|---|---|---|---|
| (2) | 社会的直接性 | `_reply_to` あり = **S 計算をバイパスして即突入**。ただし親密度が閾値未満の相手からの定型接触は突入せず **1 ターンのテンプレ応答**(`_decide` で LLM を 1 本も呼ばず返す) | talk |
| (2') | 同上・**話す側** | この tick に認知イベントを迎え、同席者がいて会話クールダウン外 = 既存の「対面会話は確定発火」がまさに起きる場面 | talk |
| (3) | 実行不能例外 | 第86 `note_plan_exception` が立てる `_plan_exception` を読む | replan |
| (4) | 欲求臨界 | fire の `INTERNAL`(ニーズ閾値の**上向き横断**) | replan |
| (5) | 予定思考 | 朝計画 = 全員(`_fire_plan_due`)/ 夜内省 = **高解像度層のみ**(第88 の tier までは conf `reflect_frac` × `_stable_hash` の決定論選定)。どちらも既存機構がこの tick に 1 回考え済みなので `turns=1` から始める | replan / reflect |
| (1) | S > θ_in | fire の `SALIENCE` かつ `S > θ_in`(不応期中は θ_in を `refractory_mult` 倍) | 同席なら talk・他は replan |

**脱出 4 条件**:

| # | §8 | 実装 |
|---|---|---|
| (4) | プリエンプト | must 期限(`_plan_exception`)/ 欲求臨界が**別種の**エピソード中に来たら中断。中断内容を**1 行だけ**兆しメモリへ(`agent.remember(kind="sign")` = 既存記憶機構の再利用。新しい記憶機構は作らない) |
| (1) | 解消 | 会話は**双方**の別れ挨拶が揃ったとき / 思考系は `day_plan.apply` が**検証を通った**計画を作ったとき(後退した計画は解消ではない) |
| (3) | ターン上限 | 会話は `turn_cap`(12)に達したら**切り上げターンを 1 回挟んで**終わる(その 1 ターンだけプロンプトの節が「締めくくる」に変わる)。思考系の実効上限は `replan_cap`(3)= §8 の再計画試行上限 |
| (2) | 減衰 | `S < θ_out = ratio × θ_in`(**ヒステリシス**)。ただし ①返答義務(`_reply_to`)がある間 ②生きている会話の最中(最後のターンから `talk_idle_min` 以内)③最短滞在 `min_stay_min` 未満 は抜けない |

**補助規則**: 不応期(脱出後 `refractory_min` 分は**同種トリガ**の θ_in を倍率で引き上げ。
第82 の g 更新=慣れ ē とは**別の階層**で g を 1 バイトも書き換えない)/
**会話は両者 ENGAGED が成立条件**(`_apply(speak)` の返答権授与に gate。話者が AUTOPILOT なら
渡さない=挨拶で終わる)/ 全エピソードのログ(L1 `episode_start` / `episode_end`)。

### 5.2 リサーチ根拠(実装前・2026-08-03)

- **会話の終わり方**: Schegloff & Sacks 1973 *Opening up closings*(Semiotica 8(4):289-327)。
  pre-closing は**決定ではなく申し出**で、相手は新しい話題で開き直せる。終結は共同達成。
  → 「**双方**が closing move を出したときだけ解消」の根拠。ISO 24617-2 の SOM 次元が
  initialGoodbye / returnGoodbye を**対で**定義しているのも同じ構造。SWBD-DAMSL
  (Jurafsky+ 1997)は `fc`=Conventional-closing を持ち、注記で「fc の系列が始まったら
  実際に閉じるまで全て fc」= 終結は点でなく**区間**。
- **フラグ vs 分類器**: 実務は一貫して「**モデルに構造化フラグを吐かせる+外側で硬い上限**」。
  Generative Agents(Park+ 2023, UIST '23)は `iterative_convo_v1` で「この発話で会話は
  終わったか」を **JSON boolean** で要求し、ドライバは `for i in range(8): if end: break`。
  AutoGen は 4 系統の終了条件を持ち「終了条件が立っても即座に終わるとは限らない」と明記。
  → **フラグは助言・上限が権威**。本実装も `end` 欄 + `turn_cap` の二層。
  調査の結果、現行 `deliberate.parse_action` に**終了意思を表す欄は存在しなかった**ので新設した。
- **既知の失敗様式**: CAMEL(Li+ 2023, NeurIPS)の "infinite loop of messages … repeatedly
  thanking each other or saying goodbye"(**丁寧さの無限ループ**)。"Too Polite to Disagree"
  (SIGDIAL 2026)は追従がターンとともに**増幅**することを示す。ターン上限は飾りではない。
- **ヒステリシス**: Schmitt トリガの意味論(帯の中では状態を保持)。Gaudl & Bryson 2018
  *The extended ramp model*(Cognitive Systems Research 50:1-15)が軽量認知アーキテクチャの
  目標調停に latching を組み込んだ最も近い先例。正当化は「発振を止める」より強く
  **切替にコストがあるとき履歴依存が合理的方策**(McFarland & Sibly 1975 以来)。
- **★リサーチで見つかった設計の穴**: 閾値ギャップだけでは「駆動量がなめらかに境界を
  往復する」ばたつきは止まらない(O'Brien & Arkin 2020, *Adaptive Behavior* 28(5) の
  behavior dithering: "an agent might continuously leave and return to a charger")。
  対策は**最短実行時間**。→ `min_stay_min` を追加した(Δt=10 分では 1 tick に埋もれるが
  Δt を細かくしたとき効く保険)。
- **比率の値**: θ_out/θ_in の標準値は神経・動物行動・ABM のどの文献にも**無い**。
  唯一広く引かれる推奨は Canny 1986(TPAMI 8(6))のヒステリシス閾値 high:low = 2:1〜3:1
  (= 0.33〜0.5)で、§8 の 0.5 はその帯の端。**掃引対象**として宣言する。
- **不応期 vs 馴化**: 本 module の不応期は積分発火の絶対不応期(硬いロックアウト)側。
  刺激特異的で指数回復する馴化(Stanley 1976, *Nature* 261:146-148)は第82 の g 更新が
  すでに実装している別階層。文献の助言では「同じ**相手**に再突入しない」は相手特異的な
  馴化で表すのが筋だが、本バッチはトリガ種別ごとの倍率までに留めた(g 側の拡張は別バッチ)。

### 5.3 作用点(いずれも単一)

| 何 | どこ | OFF の保証 |
|---|---|---|
| 突入/脱出/持続 | `scheduler._phase_drive` の 3 行(`pre_tick` / `update` / `face_ids`) | `enabled(sim)` False で全部 no-op・`forced` は空集合の和 |
| ターン計上 | `_llm_speak` の generate 直後 1 行 | エピソード不在 = 即 return |
| 終結の宣言路 | `_gather_material` の 1 行 → `deliberate.build_prompt(engaged_section=…)` | `None` = 1 行も足さない(`watch_section` と完全同型) |
| 終結の検出 | `_apply(speak)` の `action.get("end")` 1 分岐 | `end` 欄が無ければ no-op |
| 両者 ENGAGED | `_apply(speak)` の返答権授与に `and handoff_ok(...)` | OFF は常に True |
| 定型応答 | `_decide` の返答保証の手前 1 分岐 | `reply_mode` が常に `"engage"` |
| 解消(思考系) | `day_plan.apply` 末尾 3 行 | `note_resolved` が即 return |
| S の共有 | `fire.due_events` 末尾 2 行(`sim._fire_s` / `_fire_ctx`) | fire OFF では `due_events` 自体が呼ばれない |

`parse_action` の `end` 欄は **ON/OFF に関わらず常に寛容受理**(= OFF は「提示されないだけ」。
P2 の `move_home` / `explicit_nothing` と同じ流儀)で、消費するのは engaged ON のときだけ。

### 5.4 検収(mock のみ・実 LLM ランなし)

- **既定 OFF**: 純粋既定と L1 完全一致(144 step)・新 kind 0 件・L2 に 5 列なし・
  manifest に `engaged` キーなし・`_engaged_state` 不在・LLM 呼数一致・
  **新 stream(`mock_end`)を 1 本も引かない**・`cognition.fire` OFF なら engaged ON でも
  完全 no-op・golden(`test_scenario`)緑。
- **ON(mock・fire ON)**: 同 seed 2 ラン L1 バイト一致 / resume==straight(l1/l2/l3
  parquet 一致 + `_engaged_state`・エピソード本体・不応期の round-trip)/
  `compute_matched` 下で k=free と k=off の呼数・エピソード数が完全一致(内容非依存 LLM で
  切り分け)/ **LLM 呼び出しサイト(purpose)の集合が増えない** / no-fingerprint。
- **機能**: ヒステリシスで境界発振ゼロ(θ_out<S<θ_in の帯で状態保持。対照=ratio≈1 では
  同じ系列で 20 回以上発振することも固定)/ 最短滞在 / 不応期は**同種刺激だけ** /
  両者 ENGAGED 会話成立(話者 AUTOPILOT なら不成立)/ テンプレ応答は **LLM 呼ゼロ** /
  ターン上限の切り上げターン 1 回 / プリエンプトの兆しメモリ**1 行** /
  closing は片方だけでは解消しない。
- **実測**(mock・seed42・40 体・288 step = 2 シミュ日。`cognition.fire` ON 対照つき):

  | 指標 | 実測 | §8 の較正目標 | 距離 |
  |---|---|---|---|
  | エピソード数 | 590 = **7.38 /人/日** | 4〜8 /人/日 | **目標帯の中**(上寄り) |
  | engaged 滞在 | 25,560 分 = 起床時間の **30.4%** | 起床時間の 1〜2 割 | **1.5〜3 倍の超過** |
  | LLM 呼数 | 955 → 1,484(**+55.4%**)= 18.6 呼/人/日 | §6 の実効 4〜8 呼/人/日 | 超過(下記) |

  種別内訳 talk 389 / replan 201。トリガ内訳 social 389 / need 125 / scheduled 49 / salience 27。
  脱出理由 decay 574 / resolved 11 / turn_cap 2 / preempt 0。
  滞在分布は 30 分以下に 60%・60 分以下に 82%・最長 280 分(裾は会話の長期化)。
  1 エピソードあたり talk 2.31 ターン・58.4 分 / replan 0.95 ターン・14.8 分。
  定型応答 104 件(= LLM 呼を 104 本**減らした**)・返答権の非授与 13 件。

  **読み方と正直な限界**:
  - エピソード数は目標帯に入ったが、**滞在時間は超過**している。主因は talk エピソードの
    長さ(58.4 分)で、レバーは `talk_idle_min`。感度: 20→10 分にすると滞在は
    30.4%→**23.6%**、エピソード数は 7.38→7.99(帯の上端)になる。両方を同時に帯へ
    入れる設定は mock では見つからなかった。
  - **θ_in の較正そのものは本バッチの範囲外**(§7 の「やらないこと」・8/15-16 の実 LLM 診断)。
    §8 が「最大のリスクは θ_in の較正」と書くとおり、ここが動けば両方が同時に動く。
  - 呼数 18.6/人/日 は §6 の「実効 4〜8 呼」を超えるが、これは engaged 以前からの水準
    (fire 単独 ON で 11.9/人/日)に +55% が乗ったもの。原文書は §6 で「4〜8 呼」、§8 で
    「4〜8 **エピソード**」と書いており、1 エピソード=1 呼ではない(実測 1.84 ターン)ので
    両者は同じ量ではない。この不整合は原文書側にあるので、較正時にどちらを制御量にするか
    を決める必要がある(**STATUS 持ち越し候補**)。
  - `preempt 0`(したがって兆しメモリ 0 件)は、この条件では「非 replan エピソードの最中に
    ニーズ閾値の上向き横断が来る」同時性が起きなかったため。**第86 day_plan も同時に ON に
    すると preempt 10 件・兆しメモリ 10 件が実際に立つ**(同条件 288 step: エピソード 567 /
    social 350・need 144・scheduled 48・salience 25 / decay 537・resolved 15・preempt 10・
    turn_cap 3 / `plan_replan` 37 件)= must 危機 → 実行不能例外 → 割り込み → 「あとで
    考えよう」の 1 行、という §8 の想定経路が端から端まで通っている。
  - `resolved 11 / 590` = 会話が別れの挨拶で閉じた割合は低い。mock の `end` は確率 0.2 の
    決め打ちで、**双方**が出す必要があるため。実 LLM では文献の言う「自分から終わらない」
    側に寄る想定で、そのとき効くのは `turn_cap` である。
  - 定型応答は**単一の固定文**なので、ON のランでは同じ文が発話分布に 104 件現れる。
    プロンプトの指紋ではない(世界に見える痕跡)が、語彙エントロピー・n-gram 重複率を
    読むときは機構由来の定数として除外が要る(**第91 の退行シグナル監視への申し送り**)。
    文面をペルソナ由来にすると LLM 呼が要り「定型で流す」意味が消えるので固定にした。

- **テスト**: `tests/test_engaged.py` 新規 **47 本**。フルゲート `pytest tests -q -n auto` 緑
  (2,788 → **2,835 本**)。既存 2 本の**宣言台帳**を更新した(機能変更ではなく宣言の追加):
  `test_perception_contract._NON_PROMPT_WORLD_READER_MODULES` に `engaged.py`
  (watch.py と同じ「プロンプトを組まないが世界を読む層」)、`test_physics_zones` の
  「`_llm_speak` が後から足す欄」に `engaged_section`。

### 5.5 やっていないこと(第88 以降)

心モデル固定(1 体 1 モデル束縛)は第88 — 本バッチの `model` は **backend 名**まで
(day_plan と同じ暫定)。高解像度層の指定も conf の割合指定のままで、第88 の
`cognitive_tier` が入ったらそちらへ委譲する。θ_in の実 LLM 較正は 8/15-16。
エピソード**間**の長期記憶統合は未着手(兆しメモリは既存 `remember` に 1 行書くだけで、
その再燃は既存の retrieve/query に任せてある)。相手特異的な馴化(同じ相手への再突入抑制)
は g 更新側の拡張として持ち越し。

> **第88 での解消**: `model` 欄は固定割当へ整合済み(§6.5)。高解像度層の権威も
> `model.mind.tiers.high` へ移った(`reflect_frac` は接続 OFF 時の後退先として残存)。

## 6. 第88バッチ 実装記録(2026-08-03 完了)

**conf**: `model.mind.enabled`(既定 **false**)。実装 `src/society/mind.py` +
解決層 `src/society/llm/mind_router.py`。

原文書 §5 の「心は 1 体 1 モデルを誕生時に固定/機械的判断はモデル不問/
モデルと人格の交絡は必ずログに残す/知能は均質に配置しない(三層)」をそのまま実装した。

### 6.1 割当機構(誕生時固定)

| 何 | どう決まるか |
|---|---|
| モデル | 専用 stream `mind_model`(agent_id キー)の一様値を pool の重みで累積分割。**name 昇順**の分割なので conf の並び順に依らない |
| 層 | 専用 stream `mind_tier` の一様値 < `tiers.high.frac`。**traits を 1 つも読まない**(k* と直交) |
| 作用点 | `Simulation.__init__` の名簿ループ 1 行 + `build_pool_agent` 1 行(`_apply_ontology` の直後=同じ「誕生時属性」の位置) |

RngHub の stream は stateless(キーから独立に派生)なので、**新 stream 2 本を足しても
既存 stream の draw 順は 1 つも動かない**(第75 dunbar / 第78 shuffle_partners と同じ根拠)。
割当は `(master_seed, agent_id)` の純関数なので **checkpoint に割当表を積む必要がない**
(resume でも pool 再入場でも同じモデルに戻る)。中央管理するのは「L1 に記録済みの id」
(`mind_logged`)だけで、これが無いと resume 直後に `mind_assign` を二重記録する。

★**高解像度層の選抜は traits 非依存の一様抽選を既定**にした。「あらかじめ賢い個体を
選んでおく」と『誰が世界を変えるか』(k*)という問い自体が自壊するため(サーベイ S-08)。
traits 依存選抜は `tiers.high.select: traits` として**アブレーション専用に分離宣言**し、
ON にすると manifest に「意図的な交絡・k* の主張には使えない」警告が残る。

### 6.2 解決層(agent_id → モデル)

`MindRouter` は **RouterLLM と同じ dispatcher** であって新しいバックエンドではない。

    sim.llm = MindRouter(
        default  = ここまでに組み上がった CachedLLM / RouterLLM(= 共有の既定=機械的判断・対照系列)
        children = {model_id: CachedLLM(子バックエンド)}   ← 子は **各自 CachedLLM に包む**
    )

dispatch 規則は 2 つだけ: ①`rng_key` の purpose が心の呼び(`deliberate`/`plan`/
`reflect`/`recall`)でなければ default ②agent_id が取れなければ default。
`null`(D7 対照系列)は内容非結合なので default 行き。

**キャッシュの分離**: キーは `sha256(backend.name + params + prompt)` なので、子の name が
違えば同一プロンプトでも別キーになる(D13 の既存構造をそのまま使う)。ファイルも
`llm_cache.<name>.jsonl` / `llm_journal.<name>.jsonl.gz` にモデル別で分かれる。
MindRouter 自身は `name="mind"`(モデル非依存)なので**絶対に CachedLLM で包まない**
(包むと全モデルが同一キーに潰れる。router.py と同じ罠)。

mock は `MockBackend(hub, name=...)` でサブモデル(`mock:a` / `mock:b` …)を立てられる
ようにした。**応答本文は名前に依存しない**ので、決定論を保ったまま「経路とキャッシュの
分離」だけを検証できる(name 無指定は従来どおり `"mock"`= 既存ランとバイト一致)。

### 6.3 三層知能

| 層 | 実体 | 本バッチがしたこと |
|---|---|---|
| 基底層 | 習慣・スケジュール・**経路選択・定型購買** | **1 バイトも触っていない**。既存の mobility / commerce / goods / routine は LLM を 1 本も呼ばない層で、これは実装ではなく**確認**(テストが静的に固定) |
| 思考層 | 発火時のみ LLM・混成 fleet | `model.mind.pool` の重み付き割当 |
| 高解像度層 | 1〜5% | ①`tiers.high.name` の大型モデル ②**夜内省の対象**(第87 `high_res` の権威を `reflect_frac` から引き継ぐ)③思考頻度の上限緩和(`cap_mult` を `turn_cap_of` にかける) |

`tiers.high.reflect: false` にすると②の接続だけを切って第87 の `reflect_frac` に戻せる
(対照条件)。

### 6.4 ログ = 交絡の記録(§5 の明示要求)

| 場所 | 何が残るか |
|---|---|
| L1 `mind_assign` | `{model, tier}` を個体ごと 1 件(誕生時=step0 / pool 途中入場はその step) |
| `agents.json` | `mind_model` / `mind_tier`(OFF ではキー自体が生えない) |
| `run_manifest.json` `mind` | pool 構成・三層の頭数・選抜方式・`by_model`・**交絡の注記** |
| `summary.json` `mind` | 上記 + モデル別の**呼数 / キャッシュ命中 / エピソード数 / 計画数 / 修復率**(第86 day_plan・第87 engaged の `by_model` を統合) |
| L2 | `mind_models_present` / `mind_high_agents` の 2 列(**列名にモデル名を出さない**= 列構成がランごとに変わらない。内訳は summary 側) |

第86 `day_plan.model_id` / 第87 `engaged.model_id` は **固定割当を返すよう整合**した
(`mind.log_model_id(sim, agent)` へ委譲。mind OFF のときだけ従来の backend 名へ後退)。

### 6.5 検収(mock のみ・実 LLM ランなし)

- **既定 OFF**: 純粋既定と L1 完全一致(48 step)・`agent.mind` 不在・L2 に 2 列なし・
  manifest / summary に `mind` キーなし・agents.json に欄なし・`sim.llm` が CachedLLM のまま
  (解決層が被さらない)・LLM 呼数一致・**新 stream(`mind_model` / `mind_tier`)を 1 本も
  引かない**・golden(`test_scenario`)緑。
- **ON(mock 3+1 サブモデル)**: 同 seed 2 ラン L1 バイト一致 / resume==straight
  (l1/l2/l3 parquet 一致 + `mind_logged`・割当・`_mind_binding` の round-trip)/
  `compute_matched` 下で k=free と k=off の**呼数・モデル別呼数・割当が完全一致** /
  呼び出しサイト(purpose)の集合が増えない / no-fingerprint(モデル名・層名・機構語が
  プロンプト全文に 1 文字も出ない)。
- **同一個体の全「心」呼が同一モデル**: 288 step ランの `llm_journal` **全走査**で、
  `(purpose ∈ 心) × agent_id` → backend が常に 1 つ、かつ誕生時属性と一致(逸脱 0 件)。
- **キャッシュ分離**: 同一プロンプトでもモデルが違えば別キー(2 回とも miss)・
  同一モデルの再訪は hit・`llm_cache.<name>.jsonl` がモデル別に生成される。
- **割当の統計**: `derive` の直接掃引 n=20,000 で重み 1:3 → 実測 0.2458(誤差 <0.01)、
  `high.frac=0.05` → 実測 0.0506(誤差 <0.005)。
- **実測**(mock・seed42・40 体・288 step = 2 シミュ日。pool 3 本 weight 1:2:1 +
  高解像度 `frac=0.05` の `mock:hi`。fire / engaged / day_plan も同時 ON):

  | モデル | 人数 | 呼数 | 内訳(deliberate/reflect/plan) | エピソード | エピソードターン | 滞在[分] | 計画 |
  |---|---|---|---|---|---|---|---|
  | mock:a | 10 | 331 | 303 / 16 / 12 | 138 | 234 | 5,290 | 12 |
  | mock:b | 23 | 847 | 775 / 44 / 28 | 336 | 620 | 15,430 | 28 |
  | mock:c | 4 | 123 | 109 / 8 / 6 | 57 | 89 | 1,980 | 6 |
  | **mock:hi**(高解像度) | 3 | 80 | 71 / 6 / 3 | 36 | 61 | 1,490 | 3 |
  | 合計 | 40 | **1,381** | — | **567** | 1,004 | 24,190 | 49 |

  **読み方と正直な限界**:
  - 人数 10:23:4 は重み 1:2:1(期待 10:20:10)に対し n=40 の統計誤差の内側
    (`mock:c` が 4 は −1.9σ)。高解像度 3/40 = 7.5% は frac=5%(期待 2)に対し +0.7σ。
    n=20,000 の直接掃引では比率が理論値に収束することを別途固定した。
  - **mind ON/OFF で LLM 呼数が完全一致(1,381 = 1,381)**。この条件では高解像度層の
    夜内省フックが**一度も発火しなかった**ため(`by_kind` は talk 350 / replan 217 で
    `reflect` エピソードは 0 件。第87 の実測でも同様)。したがって呼数一致は
    「機構が呼数を動かさない」ことの証明ではなく、**この条件で発火しなかった**だけである。
    registry の `affects_k=True` は取り下げない(明示的な作用点なので、
    `reflect_frac=1.0` の対照では選抜集合が実際に置き換わることを単体で固定した)。
  - 修復率が全モデル 1.0 なのは第86 と同じ理由(時刻グリッドへの丸めがほぼ毎回起きる)。
    後退率は全モデル 0(mock が常に妥当 JSON を返すため)。**モデル別の差が出るのは
    実 LLM(3B〜14B)を積んでから**で、mock 3 本は応答本文が同一なので現時点の
    モデル間差は「割当人数の差」しか映していない。ここが第90 バッテリーの出番。
  - モデル別のエピソード数・呼数は「そのモデルに割り当てられた個体の集計」であって
    **モデルの因果効果ではない**。割当が traits 非依存の決定論なので交絡は無いが、
    因果を主張するには同一個体を別モデルで走らせる対照(第89 / 第90)が要る。
    この注記は `summary.mind.confound_note` としてラン成果物にも残る。
- **テスト**: `tests/test_mind.py` 新規 **38 本**。フルゲート `pytest tests -q -n auto` 緑
  (2,835 → **2,873 本**)。

### 6.6 やっていないこと(第89 以降)

実モデルのショートリスト選定(**DP-U2 = ユーザー判断**)・バッテリー本走(第90)・
プラセボ L1 3 種(第89)は本バッチの範囲外。`model.mind.pool` は器だけで、
どのモデルを何本積むかは決めていない。`RouterLLM`(purpose 別 dispatch)を default に
据えたときの `generate_many` 未実装は**第88 以前からの既存ギャップ**でそのまま
(`engine.batch_llm` + `backend: router` の組は元から通らない)。

## 7. 第89バッチ 実装記録(2026-08-03 完了)

**conf**: `ablate.context_shuffle` / `ablate.persona_swap` / `ablate.context_sever`
(いずれも既定 **false**)。実装は第78 の `src/society/ablate.py` に追加した
`Placebo` クラス。梯子の全体像と実行レシピは新規 **`docs/research/ablation-ladder.md`**。

### 7.1 正典の要求と、それをどう満たしたか

原文書 §1 は L1 を「**呼び出し回数・フォーマット・乱数消費は同一のまま中身だけ壊した
プラセボ LLM**」と定義している。3 語をそれぞれ機械で固定した。

| 要求 | 実装 | 固定したテスト |
|---|---|---|
| 呼び出し回数が同一 | 作用点は `build_prompt` 末尾の 3 行だけ。`generate()` の呼び出し点は 1 つも増減しない | `test_llm_speak_still_calls_backend_exactly_once` / **`test_call_count_is_exactly_equal_under_prompt_blind_llm`** |
| フォーマットが同一 | 節の**位置・接頭辞・区切り・項目数**を保ち中身だけ差し替える(行数不変) | `test_prompt_line_count_is_preserved` / `test_context_sever_keeps_prefix_separator_and_item_count` / journal 全走査 3 本 |
| 乱数消費が同一 | 専用 stream `ablate_persona_swap` / `ablate_context_shuffle` のみ。RngHub はステートレスなので既存 draw 順に干渉しない | `test_off_draw_counts_identical` |

**★呼数完全一致の決着**: 実ランでは呼数が数 % 動く(下表)。これが「呼び出しサイトが
変わったせい」なのか「応答が変わったせい」なのかを切り分けるため、**プロンプト内容を捨てて
rng_key だけで応答を決める LLM プロキシ**(`_PromptBlindLLM`)を書いた。その下では 3 種とも
**呼数 148 = 148・L1 バイト一致**になる。つまり影響経路は *LLM の応答* ただ 1 本であり、
呼び出しサイト・乱数消費・観測経路への副作用はゼロだと確定した。実測ドリフトは全て
「応答が変わる → 発火ドライブが動く」の間接経路(第78 propagation_off / flat_traits と同構造)。

### 7.2 3 種の実装方式

| | 何を壊すか | 割当規則 | 保つもの |
|---|---|---|---|
| `context_shuffle` | 他者由来の文脈節を**同一ラン内の別エージェントの同種節**へ差し替え | 節種ごとの **FIFO 輪(上限32)** から、専用 stream `(agent_id, step, kind)` で 1 件抽選。**自分の中身は候補から除外**(引いてから押し込む) | ペルソナ・自分の状態・世界状態・書式 |
| `persona_swap` | ペルソナ節を別エージェントのものへ差し替え | 構築時の名簿を専用 stream で置換 → **隣接ペアを相互交換=対合**。全単射なので**人口のペルソナ分布が完全に保存される**。奇数人口は最後の 1 人だけ自己写像 | 文脈・世界状態・書式 |
| `context_sever` | 文脈節を中立プレースホルダへ | 決定論(乱数ゼロ)。項目数と区切りを保ったまま各項目を `…` に置換 | ペルソナ・自分の状態・世界状態・書式 |

**sever のプレースホルダ設計**: 記号 1 文字 `…` に限定した。「(記録なし)」「誰かが何か
言っていた」等の**文**は他条件に現れない新種の痕跡になり語彙指標(専門化スコア・n-gram・
エントロピー)を汚染する — 第78 が他者の記憶への合成文注入を棄却したのと同じ判断を、
今回は文字列の側で守った。`…` は既存プロンプト(memory_fail の「はっきりしない…」)に
既に現れる字なので、新しい字種も持ち込まない。項目数は保つので
`直近の出来事: … / … / …` のように**書式だけが残る**。

**触る節の一覧**(監査用の唯一の源 = `ablate.SECTIONS`): 知っている言葉 / 直近の出来事 /
記憶に残っていること / ふと思い出したこと / 間柄 / 同席の身近な人 / 近くにいる人 /
タイムライン / 直前のやりとり / 返答の状況行(話者名と発話文)。
**触らないもの**(理由つきで `ablate.py` に列挙): 自分由来(自分の理解・あなたの考え・日記・
さっき言ったこと・馴染みの場所)/ 物理世界(時刻・場所・気分・周りの店)/ 全員共通の環境放送 /
指示文(所持ツール・watch・engaged・状況の social/post/dm/solo・驚き)/ 中身の無い固定文(評判行)。

**第78 `propagation_off` との違い**(`ablate.py` の docstring と conf に明記):
あちらは**送り手側**の遮断で世界状態(他者の記憶・語彙・信念・TL)が変わり、受け手の節は
**消える**。こちらは**受け手側**で、世界状態は 1 バイトも変えずプロンプトを組む最後の一手前で
中身だけ潰すので節は**消えない**。前者は伝播の因果、後者は文脈利用の因果を測る。**併用不可**。

### 7.3 相互排他と正直な宣言

- 3 種は同じ節を書き換える**同一軸**なので**同時 ON は `build_cfg` が ValueError**。
  `propagation_off` との併用も ValueError(「消えた節」と「潰した節」を区別できないため)。
  `llm_off` との併用はプロンプトが 1 つも組まれず**プラセボが無効**になるので WARNING で告知。
- **fingerprint_risk = `known`**(registry / manifest / summary の 3 箇所に残す)。
  3 種とも「当人から観測できる差分」を**意図的に作る**条件である。**中身が入れ替われば
  応答は変わり世界も変わる。それが目的**(変わらなければプラセボとして無意味)。
  隠す方法は原理的に存在しないので隠さず宣言した。
- `summary.placebo` に「壊した量」を必ず出す。`sections_shuffled` / `persona_swapped` が
  **0 のランはプラセボとして無効**なので単調性の主張に使ってはいけない、が事後に判る。

### 7.4 実測(mock・40体288step・seed=42・OFF 比)

| 条件 | LLM 呼数 | Δ% | L1 総数 | speak | hear | transmission | label_adopt | vocab_use |
|---|---|---|---|---|---|---|---|---|
| OFF(既定) | 1,027 | — | 16,867 | 482 | 413 | 1,046 | 252 | 278 |
| L1a context_shuffle | 883 | **-14.0%** | 14,032 | 369 | 203 | **142** | **54** | **94** |
| L1b persona_swap | 1,009 | -1.8% | 16,509 | 426 | 273 | 1,334 | 174 | 249 |
| L1c context_sever | 995 | -3.1% | 15,303 | 454 | 485 | 350 | 96 | 93 |
| L0 llm_off | 0 | -100% | 6,412 | 0 | 0 | 0 | 0 | 0 |

壊した量: shuffle=節 2,638 件差し替え(枯渇後退 8 件)/ swap=1,009 呼・20 ペア・
対合成立(`involution: true`)/ sever=節 3,356 件潰し。

**読み取り(粗い比較)**: 4 条件は L1 イベント分布が明確に食い違う = **プラセボは実際に
世界を変えている**(検収 3 の要件)。とくに `context_shuffle` は語彙伝播系
(transmission -86% / label_adopt -79% / vocab_use -66%)を強く潰す。「知っている言葉」節が
他人のものに置き換わることで、未知語の驚き → 発火 → 採用の輪が切れるためで、
呼数の -14% もこの間接ドライブ経路の帰結(呼び出しサイトは不変)。
`persona_swap` は伝播を潰さない(transmission +27%)=**文脈は正しいまま**という設計どおりの
挙動で、3 種が別々の因果を切っていることが実測でも確認できた。
なお L0 は day_plan/reflect/speak が全て 0 になる一方 move/arrive はほぼ同数 =
ルール層だけで世界が完走している(第78 の性質は不変)。

### 7.5 実装の限界(隠さず記録する)

1. **ドナー枯渇**: `context_shuffle` はラン開始直後だけ輪が空で、`context_sever` と同じ
   プレースホルダへ後退する(40体288step で 8 件 = 全体の 0.3%)。
   件数は `summary.placebo.shuffle_starved` に出る。
2. **pool × persona_swap**: 対合表は構築時の名簿から組むので、`persona_pool` の日境界
   ローテーションで後から実体化した個体は一方向ドナーへ後退する
   (`summary.placebo.involution=false` で判る)。pool を使う梯子では対合性を保証しない。
3. **呼数の間接ドリフト**は消せない(消せたらプラセボとして無意味)。k を揃えたい比較では
   `k.compute_matched` 対照を併用すること。

### 7.6 検収

- **既定 OFF**: 純粋既定と L1 バイト一致・**ゴールデン `golden_baseline_l1.json` 一致**
  (15体144step)・**draw 数(stream 別)完全一致**(新 stream ゼロ)・個体に `placebo`
  属性が生えない・manifest / summary にキーが増えない。
- **各 ON**: プロンプト盲下で呼数 148=148 と L1 バイト一致 / 実ラン呼数ドリフト < 25% /
  journal 全走査でのプロンプト構造検査(行数分布・接頭辞・区切り・項目数・
  「自分の状態」は無傷)/ 同 seed 2 ラン一致 / mid-day resume == straight(L1/L2/L3)/
  checkpoint round-trip で輪が復元され復元個体が構築時の Placebo を指す /
  persona_swap の対合性(単体 + ラン内 + journal の突き合わせで「載っているのは対合相手の
  ペルソナ」)/ 相互排他 6 通りの ValueError。
- **テスト**: `tests/test_placebo.py` 新規 **55 本**(既存 `tests/test_ablate.py` の
  既定 dict 検査 1 本を新キー 3 つぶん更新)。フルゲート
  `pytest tests -q -n auto` 緑(2,873 → **2,928 本**)。

### 7.7 やっていないこと

実 LLM での単調性検証**本走**(本選 GPU。L2〜L4 のモデル選定は **DP-U2 = ユーザー判断**)・
第90 バッテリーハーネス・第91 退行監視は本バッチの範囲外。
`docs/research/ablation-ladder.md` には実行レシピ(conf 例)と読み方(禁止事項つき)まで
書いたが、走らせてはいない。
