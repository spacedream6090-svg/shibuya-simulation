# 長期予定・スケジュール帳 実装仕様(第7バッチ 2026-07-07)

> 依頼(ユーザー 2026-07-07): 日付を実装したので、エージェントが長期の予定を立てられるように
> したい。予定を企画する仕組み = **会話に未来の日付や時間が入っていれば推論する**、もしくは
> **エージェント同士の会話からどこに予定が入るのかを自動的にスケジュール帳に記入する**。
> 設計者: Fable 5。W7-core の日付 API(`world/calendar.py`)の上に載せる。実装は Opus(感情バッチ後に直列化)。

## 0. 位置づけと鉄則
- **既定 OFF でバイト一致**(`schedule.enabled=false` → 解析なし・注入なし・イベントなし=従来と1バイトも変わらない)。
- **追加 LLM 呼び出しゼロ**(R1): 予定抽出は、既に生成済みの発話テキストに対する**決定論パーサ**(正規表現)。呼数を変えない。
- **決定論・RNG不要**: パーサは乱数を引かない。決定論テストは ON 同士2回一致で書く。
- **no-fingerprint**: パーサは `src/society/schedule.py`(src/society 直下=検査対象外)に置き、因子語を書かない。
- k 非依存: 機構は k.writeback を参照しない(発話テキストが k 由来で変わるのは正当な因果=beliefs 経由と同じ)。

## 1. データ構造
`agent.schedule: list[dict]`。各予定 = 
```
{"day": int,        # 絶対 day_index(calendar で解決済み)
 "when": str,       # 時間帯("朝|昼|午後|夕方|夜")または "HH:MM"
 "what": str,       # 行動("会う|食事|遊び|買い物|勉強会|イベント" 等、抽出できれば)
 "place": str,      # 場所名(抽出できれば。無ければ "")
 "with": list[int], # 相手のエージェント id(会話相手)
 "src_step": int}   # 記入元 step(観測用)
```
上限(例 8件)+ 過去の予定は当日経過で自動失効(GC)。

## 2. 予定の抽出(会話 → スケジュール帳)
発話(`speak`)/ DM が **ログされた直後**に、`schedule.extract(text, base_day, base_min, cal)` を呼ぶ。
決定論の日本語時間表現パーサ:
- **相対日**: 明日/あした(+1)・明後日/あさって(+2)・今夜/今晩(=当日夜)・週末(次の土)・来週(+7目安)・「今度の◯曜」・「◯日後」。
- **絶対日**: 「◯月◯日」・「◯日」(calendar ON 時は現在日以降で直近の該当日へ解決)。
- **時刻**: 「◯時」「◯時半」「午前/午後◯時」→ "HH:MM"。無ければ時間帯語(朝/昼/夕方/夜)。
- **行動・場所**: 時間表現の近傍語から `what`/`place` を推定(取れなければ空)。
- 相対表現は **calendar で絶対 day_index に解決**(base_day 起点)。calendar OFF なら経過日 base_day 起点で解決(祝日概念なし)。
- 未来の日時が1つも無ければ **[](記入しない)**。

## 3. 記入と両者共有
- 抽出できたら、**話者本人**と**聞き手全員**(speak の hearers / DM の to)の `agent.schedule` に同じ予定を追加(`with` に相手 id)。= 「エージェント同士の会話から自動的に記入」。
- 重複(同じ day/when/what/相手)は追加しない。
- 記入時に新イベント **`appointment`** を1件ログ(payload: {day, when, what, place, with})。

## 4. 行動への影響(人間らしさ)
- **プロンプト注入**: 近い将来の予定があれば、発火・計画プロンプトに1行注入(既存 date_line/weather_line と同じ seam、既定 None=不変):
  例 「予定: 4月8日(火)夕方に○○さんと会う約束。」→ エージェントが会話でその予定に言及でき、継続性が出る。
- **朝の計画への反映**: `planning.make_plan` のプロンプトに「今日の予定」を差し込むと、LLM が自然にその予定を1日計画へ組み込む(強制ルーティングはしない=最小版はプロンプト認識まで)。
- (任意・後続)予定日の当該時間帯にその場所へ居たら `appointment_kept` をログ(遵守率の観測)。routine の行き先バイアスは重いので本格版。

## 5. config(既定=現行挙動)
```
schedule:
  enabled: false          # ★ON推奨: true(会話からの予定抽出・スケジュール帳)
  max_items: 8
  horizon_days: 14        # 何日先まで抽出・注入するか
  inject_prompt: true     # 近い予定をプロンプトに1行(ON時のみ効く)
```

## 6. ファイル所有(感情バッチ後に直列実行)
- **新規** `src/society/schedule.py`(パーサ+帳簿操作+予定1行)、`tests/test_schedule.py`。
- **編集** `agents/agent.py`(schedule フィールド)、`cognition/deliberate.py`(予定1行の省略可能注入)、`cognition/planning.py`(当日予定を計画プロンプトへ)、`engine/scheduler.py`(speak/dm 後に extract→記入→appointment ログ、注入配線)、`engine/simulation.py`(cfg 構築)、`observer/schema.py`(`appointment`(+任意 `appointment_kept`)登録)、`conf/config.yaml`(schedule ブロック既定OFF)。

## 7. テスト(mock・実LLM禁止)
- OFF 既定 == 純粋既定の L1 完全一致。
- extract 単体: 「明日15時に渋谷で会おう」→ day=+1・when="15:00"・place 渋谷系。相対/絶対/時刻の各パターン。
- 両者共有: speak の hearer と話者の双方に同一予定が入る。
- 決定論: ON 同士2回で L1 一致。呼数不変(FixedLLM で ON==OFF)。
- 既存全テスト green。
