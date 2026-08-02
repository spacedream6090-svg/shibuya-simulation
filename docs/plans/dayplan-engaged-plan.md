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
| 第87 | **engaged モード**: AUTOPILOT/ENGAGED 状態機械・突入5条件(S>θ_in/社会的直接性バイパス/実行不能例外/欲求臨界/予定思考)・脱出4条件(解消/減衰=ヒステリシス/ターン上限12/プリエンプト→兆しメモリ1行)・不応期30分・両者 ENGAGED 会話成立・エピソードログ(トリガー/滞在/ターン/脱出理由/model_id) | 計画済み |
| 第88 | **心モデル固定+三層知能**: agent→model_id 誕生時固定(専用 stream・manifest/ログ必須=交絡の記録)+基底/思考/高解像度層の conf 配置(高解像度 1〜5%) | 計画済み |
| 第89 | **プラセボ L1 3種**(context_shuffle/persona_swap/context_sever): 呼数・フォーマット・乱数消費同一の中身破壊(第78 ablate 枠に追加・fingerprint_risk 正直宣言) | 計画済み |
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
