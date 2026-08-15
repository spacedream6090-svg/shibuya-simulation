# 計画: 本番ランの途中経過報告(Discord)+ 途中取り出し + ビューア落とし込み

> 2026-08-15。ステータス: **計画のみ・実装未着手**(承認待ち)。
> 入力(ユーザー指示 2026-08-15): 「本番のシミュレーションを回していく中で、途中経過を discord などで
> 報告できるようにできればしたい。途中のシミュレーションの中身を取り出す機構、それをビューワーに
> 落とし込む機構が必要になってくると思う」。
> 接続: [finals-reliability-plan.md](finals-reliability-plan.md)(watchdog / backup_run / 8-15 確認項目)・
> [dt-reduction-plan.md](dt-reduction-plan.md) §5.4(壁時計の外挿=報告頻度の根拠)・
> [observation-report-template.md](observation-report-template.md)(最終報告書。本計画は**その速報版**)。
> 制約: **R1 ドクトリン ⑥「観測がシムを変えない」**([PENDING.md](../../PENDING.md) §5.1)/ [ETHICS.md](../../ETHICS.md) §2-4。

---

## 0. 結論(5 行)

1. **新規に作るのは 1 プロセスだけ**。`scripts/report_progress.py`(新規)= run-dir を**読むだけ**の
   サイドカー。シム本体にも watchdog にも 1 行も触らない。ラン側から見て存在しないのと同じ。
2. **最小構成は L1 を一切読まない**。`status.json`(watchdog)+ `l2_metrics.part-*.parquet`(1 step 1 行 =
   全部読んでも 1,440 行)+ ファイルの mtime/個数だけで、日次ダイジェストとハートビートは全部書ける。
   **pyarrow 以外の依存ゼロ・数百 ms**。これなら本選に確実に間に合う。
3. **ビューアは新規に書かない**。`viz/make_viewer.py --daily-rollup` は **L2 と structure だけ**で
   `rollup.html` を作る([make_viewer.py:1441,4462](../../viz/make_viewer.py))。走行中の L2 part を
   別ディレクトリへ結合してこれに食わせれば、**新規コード 0 行で日次ビューアが出る**。地図つきの
   ライブ画面は既存の `scripts/live_viewer.py` がすでに完成している。
4. **危険は 3 つだけで、3 つとも既知**: ①Windows の素の `open()` は `FILE_SHARE_DELETE` を立てず
   **ラン本体を落とす**(実測事故・`_open_shared` が唯一の源) ②書きかけ part を読まない(footer 判定)
   ③resume で part 番号が振り直され**同じ step を二重計上**しうる(→ step で dedupe)。
5. **webhook URL は環境変数のみ**。このリポジトリは**公開ミラーへ push される**
   ([ops/publish_public_mirror.ps1](../../ops/publish_public_mirror.ps1))ので、conf・docs・コードに
   1 文字も書かない。投稿失敗は握りつぶしてログのみ(**観測がランを殺してはならない**)。

---

## 1. 前提となる本選の数字(頻度設計の根拠)

| 量 | 値 | 出典 |
|---|---|---|
| n_steps | **1,440**(10 シミュ日 × 144 step) | [conf/finals_observe.yaml:38](../../conf/finals_observe.yaml) |
| L1/L2 の flush 間隔 | **6 step**(= 1 シミュ時間)→ **part 240 本** | 同 :893 `observer.flush_every_steps` |
| checkpoint 間隔 | **72 step**(半日)→ **20 世代** | 同 :895 `observer.checkpoint_every` |
| 総壁時計(エンジン+LLM) | **72〜164 h** | [dt-reduction-plan.md](dt-reduction-plan.md) §5.4 |
| → **1 step の壁時計** | **約 3〜7 分** | 上記 ÷ 1,440 |
| → **1 part が生える間隔** | **約 18〜41 分** | 上記 × 6 |
| → **1 シミュ日が終わる間隔** | **約 7〜16 実時間** | 上記 × 144 |

**設計への含意**:
- 「シミュ内 1 日ごとの日次ダイジェスト」= 実時間で **7〜16 時間おき・全 10 通**。人が読める頻度で、
  かつ「今日の渋谷はこうだった」という自然な単位になる。**壁時計の日次(24h)より、シミュ日の境界で切る方がよい**。
- ハートビート(生存確認)は **10〜15 分**間隔で十分(part が生えるより速く更新しても新しい情報が無い)。
- 1 poll で新しく現れる L1 part は**多くても 1 本**。読み取り負荷は構造的に小さい。

---

## 2. 既存資産の棚卸し(= 新規に書かなくてよいもの)

### 2.1 非侵襲な読み口(**この 3 つは絶対に借りる。自前で書き直さない**)

| 資産 | 場所 | 何を保証するか |
|---|---|---|
| `_open_shared(path)` | [scripts/live_viewer.py:174](../../scripts/live_viewer.py) | Windows で `CreateFileW` に `SHARE_READ\|SHARE_WRITE\|SHARE_DELETE` を立てて開く。★**素の `open()` だと、読んでいる最中に `logger._finalize_stream` の `p.unlink()` が `PermissionError [WinError 32]` で失敗し、シム本体が finalize で落ちる**(第77バッチで実際に踏んだ事故。docstring [live_viewer.py:23](../../scripts/live_viewer.py) に一次記録)。POSIX は素の open で同義 |
| `is_complete_parquet(path)` | [scripts/live_viewer.py:230](../../scripts/live_viewer.py) | 先頭 magic `PAR1`・末尾 magic・footer 長の整合だけで「書き終わっているか」を判定(pyarrow を起動しない)。**parquet は footer を最後に書く**ので、この 3 点が揃えば以後サイズは変わらない |
| `list_parts(run_dir, stem)` | [scripts/live_viewer.py:224](../../scripts/live_viewer.py) | `<stem>.part-NNNN.parquet` を index 昇順で |

これらは既に `scripts/l1_stream.py:79`・`scripts/detect_regression.py:109`・`scripts/backup_run.py:112` の
3 箇所が借りている(= リポジトリ内で確立した作法)。**新規スクリプトも同じ借り方をする**。

### 2.2 そのまま食える入力

| 入力 | 生成者 | 中身(報告に使う欄) |
|---|---|---|
| `<run>/status.json` | [watchdog.py:209 `write_status`](../../scripts/watchdog.py) | `state`(running/restarting/failed/done)・`restarts`/`max_restarts`・`last_progress{checkpoint,step,mtime}`・`last_backup_step`・`pid`・`updated`・`llm_health{step,llm_calls_total,llm_fallback_rate,llm_cache_hit_rate,source}`(:286)・`disk{free_gb,state,warn_gb,crit_gb}`(:358)。**tmp→`os.replace` の原子的書き込み**なので途中を読むことがない |
| `<run>/l2_metrics.part-*.parquet` | `ObserverLogger.flush_segment` ([logger.py:273](../../src/society/observer/logger.py)) | **1 step 1 行**。列は約 37 + llm_health 3 + reg_* 群(実測例: `n_moving` `n_inside_buildings` `n_sleeping` `n_working` `mean_money` `opinion_var` `distinct_vocab_in_use` `total_adoptions` `n_groups` `n_ventures` `n_proposals` `status_gini` …) |
| `<run>/l1_events.part-*.parquet` | 同上 | 1 part ≈ **1,690 万行**(25万×10日の外挿 40.6 億行 ÷ 240)。**kind 列だけ**なら `l1_stream.kind_counts` が Python 文字列を 1 個も作らずに数える([l1_stream.py:346](../../scripts/l1_stream.py)) |
| `<run>/config.yaml` / `agents.json` | ラン起動時 | Δt・start_min・n_steps(`live_viewer.read_run_config`:345)・名簿 |
| `<run>/watchdog.log` | watchdog | 直近の WARN 行(disk / llm_fallback)。**テキストの tail は 1 行ずつ持ってくればよい** |
| `detect_regression.py --quick` | [detect_regression.py:738,759](../../scripts/detect_regression.py) | **走行中のランに対して 1 行 JSON**(`verdict` / `flagged` / signal ごとの p・rel_slope)。**ファイルを 1 つも書かず・絶対に非ゼロ終了しない**と docstring で明言済み = そのまま異常検知の入力にできる |

### 2.3 出力側(ビューア)

| 資産 | 走行中に使えるか | 根拠 |
|---|---|---|
| `scripts/live_viewer.py`(追いかけ再生) | **使える(唯一の地図つきライブ画面)** | part を増分で読み `<run>/_live/live.html` + `live_data.js` を生成。`--once` / `--max-polls` / `--out-dir` あり([:947 main](../../scripts/live_viewer.py)) |
| `viz/make_viewer.py`(通常ビューア) | **使えない** | `build_data` が canonical `l1_events.parquet` を要求([:701](../../viz/make_viewer.py))。canonical は finalize でしか生えない |
| `viz/make_viewer.py --daily-rollup` | **条件つきで使える** | `build_rollup_data` が読むのは `l2_metrics.parquet` + `structure.json` + `summary.json` だけ([:1441,1221,4462](../../viz/make_viewer.py))。**L2 さえ用意すれば走る**(§6) |
| `viz/notable_events.py` `NOTABLE_KINDS`(:23) | 表だけ流用 | kind → 日本語ラベル・重要度 1..5 の対応表。**「見どころ」の日本語化を再発明しない**単一の源 |
| `live_viewer.HIGHLIGHT_KINDS`(:137) / `SERIES_PREF`(:157) | 表だけ流用 | 「payload を読む価値がある kind」と「画面に出す L2 列の優先順」が既に選定済み |

### 2.4 取り出し(転送)側 — **すでに完成している**

`scripts/backup_run.py`(909 行)が「**確定分のみ**を走行中のランから抜く」作法を確立済み
([:16-40 docstring](../../scripts/backup_run.py)):

1. **footer 完結判定**(pyarrow があれば footer の実パースまで)
2. **最新 checkpoint の mtime 以前**に書かれた part だけを対象にする。理由は footer ではなく
   **watchdog の巻き戻し**: `_restore_from_backup` は run-dir の part を消して世代から復元するため
   ([watchdog.py:494](../../scripts/watchdog.py) が `PART_GLOB` を unlink)、**checkpoint より先の part は
   同じ名前で中身が変わりうる**。境界の内側なら append-only と見なせる。
3. copy 系のみ・削除非伝播・増分(size+mtime_ns)・BagIt 式 sha256・再圧縮しない。

→ **本計画は転送機構を作らない**。§5 の「報告のための取り出し」は、この 2 条件(footer + checkpoint 境界)を
**そのまま借りる**。

### 2.5 運用の前例

- [ops/backup-daily.ps1](../../ops/backup-daily.ps1): Windows タスクスケジューラ常駐の前例(毎日 23:30・
  1 行ログ・失敗しても続行)。RW-U1(`shibuya-rw-fetch-daily` 毎日 12:00)も同型で稼働中。
- **本選機は Linux + tmux/systemd の可能性がある**([finals-reliability-plan.md](finals-reliability-plan.md) §5-④が
  8/15 の確認項目)。→ 新規スクリプトは **常駐ループ(`--interval`)と 1 発実行(`--once`)の両方**を持たせ、
  タスクスケジューラ / cron / tmux のどれでも回るようにする。

---

## 3. 設計原則(R1 整合。ここを外したら実装しない)

| # | 原則 | 実装上の具体 |
|---|---|---|
| P1 | **ラン本体のプロセスに一切触れない** | 別プロセス。signal も送らない・stdin も持たない・watchdog の子にもしない。watchdog に投稿機能を足すのは**却下**(監督ループにネットワーク I/O を持ち込むと、Discord の遅延が **ストール検知と resume 判断を遅らせる**) |
| P2 | **run-dir へは読み取りしかしない**(唯一の例外は自分の出力サブディレクトリ) | 書くのは `<run>/_progress/` 配下だけ(`--out-dir` で run-dir の外へも出せる)。`_live/` の前例に揃える。**run-dir 直下には 1 バイトも書かない**(logger の `_next_seg`・watchdog の `PART_GLOB`・backup_run の走査は全て**非再帰**なので、サブディレクトリは構造的に無害) |
| P3 | **書きかけを読まない** | `is_complete_parquet` を通った part だけ。未完結の最新 part は**待つ**(読んで先へ進まない) |
| P4 | **開くときは必ず `_open_shared`** | `is_complete_parquet` の一瞬の read すら例外を作らない(既存実装がそうなっている) |
| P5 | **失敗してもランに影響ゼロ** | あらゆる例外を握りつぶし `<out>/reporter.log` に 1 行残すだけ。**終了コードは常に 0**(`detect_regression --quick` と同じ方針)。投稿の HTTP 失敗も同様 |
| P6 | **観測の負荷そのものを絞る** | 最小構成は L1 を読まない。L1 を読む段でも **kind 列だけ・新しい part だけ**。ディスク I/O はランの part 書き込みと競合する資源であることを忘れない |
| P7 | **欠測を偽の値で埋めない** | 読めなかった指標は `null` として「測れなかった」と表示する(`disk_state` の `"unknown"`・`read_llm_health` の `None` と同じ流儀) |

> **文献上の裏付け**: 計測をジョブ本体に埋め込むと、**3% 未満のオーバーヘッドでも結論が覆るほどの摂動**が
> 起こりうる(Mytkowicz et al., *Observer Effect and Measurement Bias in Performance Analysis*,
> https://scholar.colorado.edu/downloads/2v23vv18b )。したがって「別プロセスが成果物ディレクトリを
> 追いかける」= **サイドカー方式**が正しい(Azure Architecture Center, *Sidecar pattern*,
> https://learn.microsoft.com/en-us/azure/architecture/patterns/sidecar / Kubernetes のログ収集
> サイドカーは「アプリが書いたログファイルを tail する」形が正典:
> https://kubernetes.io/docs/concepts/cluster-administration/logging/ )。
> **本計画のアーキテクチャは、既に live_viewer / backup_run が採っている形の踏襲である。**

---

## 4. (a) アーキテクチャ

### 4.1 プロセス構成

```
  [GPU 機]
   watchdog.py ──起動/監督──> run.py(シム本体)
        │                        │
        │ status.json            │ l1_events.part-NNNN.parquet
        │ watchdog.log           │ l2_metrics.part-NNNN.parquet
        ▼                        ▼ checkpoint/ckpt-NNNNNN.pkl.gz
   ┌──────────────  <run-dir>  ──────────────┐
   └──────────────────┬───────────────────────┘
        読むだけ       │        読むだけ
   ┌──────────────────┴─────────────┬──────────────────────┐
   │ scripts/live_viewer.py         │ scripts/report_progress.py(新規)
   │  → <run>/_live/live.html       │  → <run>/_progress/{digest,state,log}
   │    (地図つきライブ画面・既存)   │  → Discord webhook(HTTPS 送信のみ)
   └────────────────────────────────┴──────────────────────┘
                                                   │
                                        [ローカル PC / スマホ] Discord
```

- **report_progress.py は live_viewer と独立に動く**(片方だけ起動してもよい・両方でもよい)。
  2 プロセスが同じ part を同時に読むのは安全(どちらも `_open_shared` = 共有読み)。
- **外向き HTTPS が塞がっている場合の退路**: run-dir をローカル PC へ日次 pull した先(`backup_run.py --dest`)を
  `--run-dir` に指定して**ローカル PC 側から投稿**する。報告は 1 日遅れになるが機構は同一。
  → **8/15 の環境確認に「GPU 機から `discord.com:443` へ出られるか」を 1 項目足す**(§12)。

### 4.2 1 サイクルでやること(擬似コード)

```
poll():
    st   = read_status_json()            # 原子的書き込み済み。JSON 1 本
    l2   = read_all_l2_parts()           # 完結 part のみ・step で dedupe(§4.4)
    fs   = scan_filesystem()             # part 個数・最新 mtime・checkpoint 世代・自由容量
    reg  = maybe_run_detect_regression() # 任意・日次のみ(サブプロセス・--quick)
    now  = build_state(st, l2, fs, reg)  # 小さな dict(数十 KB)

    if is_new_sim_day(now):    post_daily_digest(now)      # 新規メッセージ
    elif alerts := diff(prev, now):  post_alerts(alerts)   # 新規メッセージ(条件つき)
    else:                      edit_heartbeat(now)         # 既存メッセージを PATCH

    save(prev := now)          # <out>/reporter_state.json(原子的)
```

### 4.3 報告の 3 系統

| 系統 | 形 | 頻度 | 中身 |
|---|---|---|---|
| **H ハートビート** | **1 通を編集し続ける**(`?wait=true` で得た message_id を PATCH) | 10〜15 分 | 進捗バー(step/1440・day/10・シム内時刻)・最終 part からの遅延・state・空き容量・次の日次予定。**チャンネルを汚さない** |
| **D 日次ダイジェスト** | 新規メッセージ(embed) | シミュ内 1 日の境界(実時間 7〜16 h・全 10 通) | §4.5 |
| **A アラート** | 新規メッセージ(必要なら本人メンション) | 状態遷移時のみ(§7) | 何が・いつ・どの値が閾値のどちら側か・**推奨アクション 1 行** |

### 4.4 ★正確さのための 3 つの掟(見落とすとバグる)

1. **L2 は毎回**全部**読み直し、step で dedupe(後勝ち)する。** 240 part × 6 行 = 1,440 行しかない。
   カーソルを持たないので、**resume で part 番号が振り直されても**(`logger._next_seg` は既存 part の
   max+1 から採番)**構造的に二重計上が起きない**。live_viewer の docstring が警告している
   「既に読んだ step を含む part が新しい index で現れる」問題を、最小構成は**設計で回避する**。
2. **L1 を読む段(レーン4)では、part 単位ではなく step 単位で進む。** `max_step_seen` を持ち、
   `step <= max_step_seen` の行は捨てる(`l1_stream` の `step_min` 枝刈りがそのまま使える:
   [l1_stream.py:191,405](../../scripts/l1_stream.py))。part 単位のカウンタは resume で壊れる。
3. **「確報」と「速報」を分ける。** checkpoint 境界より先の part は**巻き戻しで中身が変わりうる**
   (§2.4-2)。したがって:
   - 画面・ハートビート・日次ダイジェストの本文 = **速報**(境界外も読む。**「暫定」と明記する**)
   - `digest.json` に**残す**数字 = **確報**(checkpoint mtime 以前の part のみ)
   これは backup_run が既に採っている判断の、報告側への持ち込みである。

### 4.5 日次ダイジェストの中身(embed 1 通・案)

```
┌ 渋谷シム finals — Day 3/10 が終わりました            [青=正常/黄=警告/赤=異常]
│ 進捗    432 / 1440 step (30.0%)   シム内 8/19 07:00
│ 状態    running・再起動 0 回・最終 checkpoint step 432(12 分前)
│ ── 街のようす(その日の平均 / 前日比) ──
│ 在場        249,880 (±0)      屋内 61.2% (+1.8pt)    就寝 24.9% (−0.4pt)
│ 所持金平均  ¥182,430 (−0.7%)  意見の分散 0.281 (+0.9%)
│ 使用中の語彙 1,204 語 (+37)   語の採用 累計 8,912 (+412)
│ 組織/催し   ベンチャー 12 (+2) 議案 3 (+1) グループ 87 (+5)
│ ── 装置の健康 ──
│ LLM       呼 1,240,881 / fallback 3.1% / cache 22.4%
│ 退行判定   OK(4 群 8 指標すべて非有意)
│ ディスク   free 1.42 TB (ok)   バックアップ確定 step 432
│ ── 添付 ──
│ rollup.html(日次ロールアップ・自己完結)  metrics.png(主要 6 系列)
└ ※ 本シミュレーションの人物・組織・発言はすべて架空です / 数字は暫定(確報は step 432 まで)
```

- **前日比を必ず添える**(絶対値だけだと人は異常に気づけない)。
- **どの step の値か**を必ず書く(live_viewer が `series_step` で守っている規律と同じ = 黙って混ぜない)。
- 「街のようす」の列選定は `live_viewer.SERIES_PREF`(:157)を出発点にする(既に選定済みの資産)。

---

## 5. (b) 途中取り出し機構

### 5.1 用途が 2 つある(混ぜない)

| 用途 | 機構 | 状態 |
|---|---|---|
| **転送・保全**(結果を確実に持ち帰る) | `scripts/backup_run.py`(増分 tar + BagIt 式 sha256) | **実装済み**(第110)。本計画は触らない。★本選は `--ckpt-generations 999` |
| **報告・可視化**(途中の中身を人が見る) | **新規**: `report_progress.py --extract` | 本計画 §5.2 |

### 5.2 「報告のための取り出し」の仕様

```
python scripts/report_progress.py <run-dir> --extract --day 3 [--out-dir DIR]
```

出力(既定 `<run>/_progress/day-03/`):

| 生成物 | 作り方 | サイズ |
|---|---|---|
| `l2_metrics.parquet` | 完結 L2 part を**step 昇順で結合**して 1 本に(day 0..3 の全 step) | 数百 KB |
| `digest.json` | その日の集計(平均・最終値・前日比・kind 件数・見どころ)+ **来歴**(どの part まで・確報 step・生成時刻) | 数十 KB |
| `summary.json`(最小) | `n_agents` / `n_steps` のみ(**ビューアが読むため**。本物の summary は finalize でしか出ない) | < 1 KB |
| `rollup.html` | §6 | 数十 KB |
| `metrics.png`(任意) | レーン3 | < 500 KB |

**規律**:
- 読むのは `is_complete_parquet` を通った part のみ(P3)。開くのは `_open_shared`(P4)。
- `digest.json` に書く数字は **checkpoint 境界の内側のみ**(§4.4-3)。境界より先は `provisional` 節へ分けて
  「暫定」と明示する。**同じキーに確報と速報を混ぜない**。
- **run-dir 直下には書かない**(P2)。`_progress/` は `backup_run` の走査対象外(`TRAVERSE_DIRS=("checkpoint",)`・
  `DEFAULT_EXCLUDE` に `*.html`)なので、バックアップを汚さない = 派生物として正しい扱いになる。
- L1 を読む場合(レーン4)も **kind 列 + 見どころ kind の payload だけ**。`l1_stream.iter_record_batches(kinds=…)` が
  Arrow レベルで filter してから実体化するので、捨てる行の Python オブジェクト生成費が 0 になる
  ([l1_stream.py:405](../../scripts/l1_stream.py))。

### 5.3 なぜ part を「そのまま結合してよい」と言えるか

parquet は `PAR1 …データ… フッタ フッタ長(int32,LE) PAR1` の順で書かれ、**メタデータは最後に書かれる**
(Apache Parquet, File Format: "File metadata is written after the data to allow for single pass writing" —
https://parquet.apache.org/docs/file-format/ )。よって末尾 magic + footer 長が整合する part は書き終わっている。
`flush_segment` は `pq.write_table` = open→write→close の一括で、次の flush は **part N+1 という別ファイル**へ行く
([logger.py:273](../../src/society/observer/logger.py))。

> **補足(採らなかった案)**: 業界標準は「`_tmp` 名で書いて完成時に rename」+ 読み側は
> PyArrow の `ignore_prefixes=['.','_']` 既定で未完成を**見えなくする**
> ( https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetDataset.html )や
> Hive の `_SUCCESS` マーカー。**本選前にシム側の書き込み経路を変えることになるので採らない**(R1)。
> リポジトリは既に footer 判定という等価な保証を持っており、そこに乗るのが正しい。

---

## 6. (c) ビューアへの落とし込み

### 6.1 3 段構え(新規のビューアコードは書かない)

| 段 | 何を出すか | 実装 | 見る場所 |
|---|---|---|---|
| **V1 日次ロールアップ**(推奨・主線) | `rollup.html`(位置を一切埋め込まない軽量ページ。L2 の日次平均 + structure) | **既存**: `viz/make_viewer.py --daily-rollup` に §5.2 の抽出ディレクトリを食わせるだけ | Discord に**添付**(数十 KB)/ ローカルで開く |
| **V2 ライブ地図** | `live.html` + `live_data.js`(追いかけ再生) | **既存**: `scripts/live_viewer.py`(常駐 or `--once`) | GPU 機のブラウザ / 転送して開く |
| **V3 静止画** | `metrics.png`(主要 6 系列のスパークライン) | 新規・小(レーン3) | Discord embed に**インライン表示**される唯一の形 |

### 6.2 V1 が成立する理由(実装前に確認済み)

`build_rollup_data`([make_viewer.py:1441](../../viz/make_viewer.py))が読むのは:
- `l2_metrics.parquet`(**canonical 名。§5.2 で結合して置く**)
- `structure.json`(事後解析の産物。**無ければ `None`** = 走行中は素通り、`load_structure`:1221)
- `summary.json`(`n_agents`/`n_steps` のみ。**無ければ `None`**)
- `l1_events.parquet` の先頭 row-group(**start_min の復元だけ**。無ければ既定 07:00 へフォールバック
  `_rollup_start_min`:1422)→ **抽出側で `config.yaml` から正しい start_min を知っているので、
  `--start-tod HH:MM` 相当を渡すか、`digest.json` 側に真値を書いて画面注記に出す**(黙って 07:00 にしない)。

→ **走行中でも成立する。新規ビューアコードは 0 行**。`rollup.html` は `positions` を持たないので
30 日級でも数十 KB([make_viewer.py:4258](../../viz/make_viewer.py) の設計注記)= Discord 添付に載る。

### 6.3 自己完結 HTML であること

`rollup.html` も `live.html` も **外部 URL ゼロ・単一ファイル**で開ける必要がある(添付して転送するため)。
- `live.html` は**現状 2 ファイル**(`live.html` + `live_data.js` の JSONP)なので、添付するときは
  **データを 1 本にインライン化した静止スナップショット**を作る(`<script>LIVE_DATA({...})</script>` を
  埋め込むだけ・レーン3)。既存の `render_html` / `write_data`([:920,892](../../scripts/live_viewer.py))を
  借りれば数十行。**`live_viewer.py` 本体は改変しない**(凍結資産の扱いは既存の借り方に揃える)。
- 自己完結 HTML の一般解(データ URI で全て埋め込む)は Quarto `embed-resources` / Plotly
  `include_plotlyjs=True` と同じ考え方( https://quarto.org/docs/output-formats/html-basics.html )。
- **ヘッドレス Chrome で live.html を撮る案は非推奨**: Chrome 132 以降、旧 headless は
  `chrome-headless-shell` という**別バイナリ**になり( https://developer.chrome.com/docs/chromium/headless )、
  JS 描画待ちに使う `--virtual-time-budget` は**公式ドキュメントに存在しない**フラグ。本選機に
  ブラウザを用意する前提を持ち込むより、**matplotlib で数値から直接 PNG を描く**方が確実に安い(レーン3)。

---

## 7. 頻度・アラート設計(通知疲れを作らない)

### 7.1 何を「アラート」にするか(症状ベース)

Google SRE Book の規律(症状で鳴らす・原因では鳴らさない・鳴ったら必ずやることがある:
https://sre.google/sre-book/monitoring-distributed-systems/ / Ewaschuk *My Philosophy on Alerting*)を採る。

| # | 条件(**遷移**したときだけ) | 出典の値 | 推奨アクション(本文に書く) |
|---|---|---|---|
| A1 | `status.state` が `running` 以外へ(`restarting`/`failed`) | status.json | failed なら即対応・restarting は 2 回連続で注意 |
| A2 | **進捗が止まった**: 最新 part / checkpoint の mtime が閾値(既定 45 分 = part 間隔上限 41 分 + 余裕)を超えて更新されない | ファイル mtime | watchdog の `--stall-min`(既定20分)より**後**に鳴る = 二重に騒がない |
| A3 | `disk.state` が `warn` / `critical` へ | status.json `disk`(watchdog.py:358) | 何を消すかは**人間の判断**(checkpoint/dormant は剪定禁止) |
| A4 | `llm_fallback_rate` が閾値を上抜け(既定 0.20・**復帰も 1 通**) | status.json `llm_health` | モデル/プロンプト/バックエンド点検 |
| A5 | 退行判定が `REGRESSION` へ | `detect_regression --quick` の `verdict` | 事前登録の判断へ(**止めない**) |
| A6 | 再起動回数が `max_restarts` の 50% / 80% を超えた | status.json | |
| A7 | **レポーター自身が長時間投稿できていない**(復帰時に「N 時間ぶり」を明記) | reporter_state.json | 監視の監視 |

**鳴らさないもの**: L2 指標の日々の揺れ(= 日次ダイジェストで見る)・単発の warn(次サイクルで戻るもの)。

### 7.2 抑制(dedup / hysteresis)

- **状態遷移でのみ発火**(同じ状態が続く間は鳴らさない)。Alertmanager の dedup/inhibition と同じ考え方
  ( https://prometheus.io/docs/alerting/latest/alertmanager/ )。
- **クールダウン**: 同一 alert key は既定 30 分以内に再送しない(W&B `run.alert(wait_duration=300)` と同型:
  https://docs.wandb.ai/models/runs/alert )。
- **ヒステリシス**: 閾値の上抜け/下抜けに別の値を使う(例 fallback 0.20 で発火・0.15 で復帰)。
  2 サイクル連続で条件成立してから鳴らす(単発スパイクを弾く。SRE Workbook の multiwindow の最小形:
  https://sre.google/workbook/alerting-on-slos/ )。
- **上限**: 1 時間あたり最大 6 通。超えた分は次の日次ダイジェストに「抑制した N 件」として**必ず数を出す**
  (silent cap 禁止 = リポジトリの既存規律)。

### 7.3 API 側の実務(数字の出典と注意)

| 事項 | 値 | 備考 |
|---|---|---|
| エンドポイント | `POST /api/webhooks/{id}/{token}` | https://docs.discord.com/developers/resources/webhook |
| `content` | **2000 文字** | 超えると 400 |
| `embeds` | **10 個**まで / description **4096** / fields **25** / field value **1024** / footer **2048** / **全 embed 合計 6000 文字** | https://docs.discord.com/developers/resources/message |
| 添付 | `multipart/form-data`(`payload_json` + `files[0]`)・embed からは `attachment://<name>.png` で参照 | 公式の既定上限は **10 MiB**。ただし webhook はユーザー層の引き上げに追随しない履歴があり(issue #6058 で 8MB のまま `413`/40005)、直近に 20MB とする非公式情報もある。→ **1 添付 8 MB 以下で設計すれば全変種で安全** |
| レート制限 | グローバル **50 req/s**。**per-webhook の具体値は公式に無い**(「5 req/2s」「30 msg/min」は非公式で、しかも guild 共有の可能性が discord-api-docs #6753 で報告され未回答) | → **数字を焼き込まない**。`X-RateLimit-Remaining` / `Retry-After`(**秒**・小数)を読んで従う。API v8+ で `retry_after` は秒(v6 のミリ秒と混同しない) |
| **404 が返ったら二度と叩かない** | 公式に明記(繰り返すと一時制限) | webhook 削除/再生成後の暴走を止める安全弁 |
| ハートビートの更新 | `?wait=true` で POST → 返る `message.id` を保存 → `PATCH /webhooks/{id}/{token}/messages/{message_id}` | **`wait=true` を付けないと 204 で id が返らない**。編集時 `attachments` は**残すもの全部**を並べ直す必要あり |
| スレッド | `?thread_id=` / フォーラムは `thread_name` | 日次はスレッドに束ねると読みやすい(任意) |
| メンション抑止 | `allowed_mentions` を**明示指定**する | 既定では本文中の `@everyone` 等が解釈される。エージェント発話を引用する場合の必須防具(§9)。実装時に Allowed Mentions オブジェクトの仕様を確認して「何も ping しない」既定にすること |

**Python 側**: `requests` は**この環境に入っていない**(実測)。`urllib.request` だけで JSON POST は完結する。
multipart は stdlib に encoder が無いので**手書き(約 20 行・決定論)**。watchdog / backup_run の
「stdlib 限定 + pyarrow だけ関数内 import」方針と一致する。外部ライブラリ(`discord-webhook` 等)は
**本選前に依存を増やさない**という理由で採らない。

---

## 8. (d) 実装レーンと規模見積

> **レーン1 だけで「本選に間に合う版」として成立する。** 2〜4 は独立に足せる(順序も自由)。

| レーン | 内容 | 新規/変更 | 規模 | 依存 | 推奨 |
|---|---|---|---|---|---|
| **L1 最小(テキストのみ)** | `scripts/report_progress.py`: status.json + L2 part + fs スキャン → ハートビート(PATCH)+ 日次 embed + アラート。`--once` / `--interval` / `--dry-run`(投稿せず標準出力) | 新規 1 本 | **約 450 行**(docstring 込み)+ テスト **約 20 ケース / 300 行** | stdlib + pyarrow(任意 import) | ★★★ **本選前** |
| **L2 取り出し + ロールアップ** | `--extract --day N`: L2 part 結合 + `digest.json` + `summary.json`(最小)→ `make_viewer.py --daily-rollup` をサブプロセス起動 → `rollup.html` を添付 | 同ファイルに +約 180 行 | +テスト 6 ケース | +`viz/make_viewer.py`(**読み出しのみ・改変なし**) | ★★★ **本選前** |
| **L3 画像 + 静止スナップショット** | `metrics.png`(matplotlib・Agg 固定・6 系列)/ `live_data.js` をインライン化した自己完結 `live_snapshot.html` | +約 140 行 | +テスト 4 ケース | matplotlib(**pyproject に無い** → 任意 import・無ければ静かに省略) | ★★ 余裕があれば |
| **L4 見どころ(L1 を読む)** | 完結 L1 part を kind 絞りで増分読み → 日次「今日の事件」10 件(`NOTABLE_KINDS` の重要度順)。step dedupe 必須 | +約 160 行 | +テスト 6 ケース | +`scripts/l1_stream.py`・`viz/notable_events.py`(表のみ) | ★★ **面白さは全部ここにある**が、まず 1-2 を通す |
| **L5 運用** | `ops/report-progress.ps1`(タスクスケジューラ登録)/ systemd unit の雛形 / 手順を `finals-compute-checklist.md` に 1 節追加 | 約 60 行 + docs | — | — | ★★ 本選前(実行手段は必要) |

**工数の目安**: L1+L2 = **1 日**(実装 + テスト + 縦煙)。L3+L4 = **もう 1 日**。L5 = 半日。
**8/15-16 の診断ランに相乗りして実測できる**(mock ラン相手でも全経路が動く)。

### 8.1 CLI(案)

```
python scripts/report_progress.py <run-dir> [--interval 900] [--once]
    [--out-dir DIR]            # 既定 <run-dir>/_progress
    [--dry-run]                # 投稿せず、送る本文を標準出力へ(★既定でこれを勧める初回確認)
    [--webhook-env NAME]       # 既定 SHIBUYA_DISCORD_WEBHOOK。★URL そのものは受け取らない
    [--daily-only]             # ハートビートを出さず日次+アラートだけ
    [--no-alerts] [--no-attach]
    [--stall-min 45] [--fallback-warn 0.20] [--cooldown-min 30] [--max-posts-per-hour 6]
    [--with-l1]                # レーン4(見どころ)を有効化
    [--extract --day N]        # 取り出しのみ(投稿しない)
    [--quotes off|on]          # 既定 off(§9)
```

---

## 9. (e) セキュリティ・倫理

### 9.1 webhook URL の扱い(**URL そのものが認証情報**)

Discord の webhook は**認証を一切必要としない**(公式: "They do not require a bot user or authentication to use")。
URL を持つ者は ①任意の `username` / `avatar_url` で**なりすまし投稿** ②webhook の**改名・削除** ③過去の
自分の投稿の**編集・削除** ができる。**自動失効の保証は無い**(GitHub の secret scanning パートナー一覧に
"Discord Bot Token" はあるが **"Discord Webhook URL" は無い**)。

| 規則 | 理由 |
|---|---|
| **環境変数のみ**(`SHIBUYA_DISCORD_WEBHOOK`)。`--webhook-url` のような**CLI 引数は実装しない** | 引数はシェル履歴・タスクスケジューラの XML・`ps`/タスクマネージャの一覧に残る |
| リポジトリに 1 文字も書かない(conf/ docs/ コード/ テスト fixture すべて) | **本リポジトリは公開ミラーへ push される**([ops/publish_public_mirror.ps1](../../ops/publish_public_mirror.ps1))。`.gitignore` は `runs/` を除いているので run-dir 経由の流出は無いが、**そもそも入れない**のが唯一安全 |
| **ログ・標準出力・エラーメッセージに URL を出さない**(id も token も) | 例外の `repr` に URL が載る事故が典型。投稿系の例外は**自前のメッセージに詰め替えてから**記録する |
| チャットにも貼らない(Claude との会話も含む) | ユーザーのセキュリティ規約 |
| ファイルで渡す場合は **リポジトリ外**(例 `%USERPROFILE%\.shibuya\discord_webhook.txt`)+ 読み取り権限を自分だけに | タスクスケジューラで環境変数が扱いづらい場合の退路。**リポジトリ内は不可** |
| **404 を受けたら以後の投稿を恒久停止**し、ローカルログにだけ残す | 公式が「404 の webhook を叩き続けると一時制限」と明記 |
| 失効時の手順を運用メモに 1 行(チャンネル設定で再生成 → 環境変数を差し替え → レポーター再起動) | 旧 URL は即死する = 事故時の封じ込めが速い |

### 9.2 投稿内容(**ETHICS.md の直接の帰結**)

[ETHICS.md:33](../../ETHICS.md): 「これらのモデルの**生出力は公開しない**。公開するのは集計・指標・可視化などの
派生物に限る。」 Discord チャンネルは(たとえ非公開でも)**リポジトリ外への配布経路**なので、この規則が効く。

| 規則 | 具体 |
|---|---|
| **既定は集計・指標のみ**(`--quotes off`) | 発話・DM・SNS 本文・内省本文・日課の自由文は**出さない**。出すのは件数と分布 |
| **生プロンプト / LLM 応答全文は絶対に読まない・出さない** | `llm_journal.jsonl.gz` は**入力に含めない**(そもそもレポーターが開かない設計にする) |
| 引用を有効化する場合(`--quotes on`)の条件 | ①人間が**そのラン単位で**明示的に有効化 ②**abliterated / 無検閲モデルのランでは不可**(ETHICS §2-4) ③1 件 120 文字上限・最大 3 件 ④「架空である」注記を**必ず**同じメッセージに含める |
| **サニタイズ必須**(引用する場合) | `@`・マークダウン記法・URL・コードフェンスを無効化 + `allowed_mentions` で**何も ping しない**。エージェント発話は R15 で「注入経路になりうる」と既に扱われている入力である。**`@everyone` を含む発話が 1 件でもあればサーバ全員に通知が飛ぶ**(発話は生成物なので、いつか必ず出る) |
| **絶対パスを出さない** | `summary.json` の `out_dir` / `files` は `C:\Users\塚本翔太\…` を含む = **実名(個人情報)**。投稿するのは**ラン名だけ**。`status.json` の `run_dir` / `backup_dir` も同様にマスクする |
| フィクション注記を全メッセージのフッタに固定 | 「本シミュレーションの人物・組織・発言はすべて架空です」(ETHICS §2-1,2)。**組織台帳は R17 で実在企業名を含まない**ことは確認済み([data/organizations_shibuya_wide11k.json](../../data/organizations_shibuya_wide11k.json) の meta)が、注記は常に付ける |
| 数値の性質を明示 | 「暫定(速報)」「確報 step N まで」を毎回書く(§4.4-3) |

### 9.3 レポーター自身の安全弁

- **タイムアウト**: HTTP は接続 10 秒 / 読み取り 20 秒。ぶら下がってもサイクルを止めない。
- **リトライ**: 429 は `Retry-After`(秒)に従って最大 3 回。5xx は指数バックオフ 3 回。それ以外は 1 回で諦める。
- **投稿は 1 サイクル最後**にまとめて行う(読み取りが投稿の失敗に巻き込まれない)。
- **状態は原子的に保存**(`tmp` → `os.replace`。`live_viewer.write_data` と同流儀)。
- **二重起動しても壊れない**(state ファイルは pid つき tmp・最悪は同じ内容を 2 回投稿するだけ)。

---

## 10. 検収(テスト設計・約 36 ケース)

`tests/test_report_progress.py`(新規)。既存 `tests/test_live_viewer.py`(40 ケース)/ `test_backup_run.py` の作法に揃える。

| 群 | 内容 |
|---|---|
| **R 読み取り専用**(最重要) | ①レポーター併走あり/なしで**本体ランの出力がバイト一致**(mock ランを別プロセスで実走)②run-dir 直下に新規ファイルが 1 つも増えない(`_progress/` 以外)③`_open_shared` 経由であることを**実際に unlink して**確認(素の open だと落ちることの回帰固定は live_viewer 側に既存) |
| **P part 規律** | ④切り詰めた part を読まない ⑤より新しい part が現れた不完全 part の扱い ⑥読む直前に消えた part(finalize レース)で例外を出さない |
| **D dedupe** | ⑦**resume 模擬**(part 番号の振り直し + step の重複)で日次集計が二重計上しない ⑧確報/速報の境界が checkpoint mtime で切れている |
| **A アラート** | ⑨状態遷移でのみ発火 ⑩クールダウン中は再送しない ⑪ヒステリシス(上抜け/下抜けが別値) ⑫1 時間上限を超えたら抑制数を数える ⑬復帰通知が出る |
| **N ネットワーク**(実 Discord を叩かない) | ⑭`--dry-run` で 1 バイトも送らない ⑮429 + `Retry-After` に従う(**秒**として解釈) ⑯404 で恒久停止 ⑰タイムアウト/接続失敗で**終了コード 0・例外を外へ出さない** ⑱multipart の組み立てがバイト単位で正しい(境界・`payload_json`・`files[0]`)⑲2000 / 4096 / 6000 文字の切り詰めが働く |
| **S セキュリティ** | ⑳webhook URL がログ・stdout・例外文字列の**どこにも現れない**(全出力を正規表現で走査)㉑絶対パス(ユーザー名)が投稿本文に現れない ㉒`--quotes off` 既定で発話本文が本文に 1 文字も入らない ㉓`@everyone` を含む合成発話を食わせても `allowed_mentions` が抑止形になる |
| **V ビューア** | ㉔抽出ディレクトリで `make_viewer.py --daily-rollup` が実際に走り `rollup.html` が生える ㉕自己完結(外部 URL ゼロ)㉖start_min が 07:00 フォールバックでなく真値になっている |
| **E 欠測** | ㉗status.json が無い/壊れている ㉘L2 に llm_health 列が無い ㉙part が 1 本も無い ㉚pyarrow 不在 — いずれも**落ちず・捏造せず・"測れなかった" と出す** |

---

## 11. 実装しないもの(意図的)

- **watchdog への機能追加**(P1)。status.json に欄を足す必要も無い(既に足りている)。
- **シム本体・observer への計装**(R1 ⑥・観測者効果)。
- **転送機構**(`backup_run.py` が完成済み)。
- **Discord からの操作**(bot・スラッシュコマンド)。**受信は攻撃面**であり、送信だけなら webhook で足りる。
- **外部ライブラリの追加**(`requests` / `discord-webhook` / `playwright`)。
- **ヘッドレスブラウザでの撮影**(§6.3)。

---

## 12. 8/15 に確認すること(§5 の環境確認へ 3 項目追加)

1. **GPU 機から `discord.com:443` へ出られるか**(出られない場合はローカル PC 側で運用 = 報告が日次 pull 待ちになる)。
2. **GPU 機の OS と常駐手段**(tmux / systemd / それ以外)= レーン5 の形が決まる。
3. **Discord サーバのブースト段(添付上限)**。8 MB 設計なら確認不要だが、`rollup.html` + PNG を同送するなら一応。
4. (ユーザー作業)**投稿先チャンネルを 1 本作り、webhook を 1 個発行して環境変数に入れる**。
   → 実装完了後に `--dry-run` で本文を確認 → 本番投稿 1 回、の順で通す。

---

## 13. リサーチ出典

**Discord API**: [Webhook resource](https://docs.discord.com/developers/resources/webhook) ・
[Message / embed 上限](https://docs.discord.com/developers/resources/message) ・
[Rate limits](https://docs.discord.com/developers/topics/rate-limits) ・
[Uploading files](https://docs.discord.com/developers/reference) ・
[Intro to Webhooks](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) ・
[issue #6753(webhook バケット共有の報告・未回答)](https://github.com/discord/discord-api-docs/issues/6753) ・
[issue #6058(webhook の添付上限が本体に追随しなかった件)](https://github.com/discord/discord-api-docs/issues/6058) ・
[GitHub secret scanning パターン一覧](https://docs.github.com/en/code-security/secret-scanning/introduction/supported-secret-scanning-patterns)

**先行実装(長時間ジョブ→チャット)**: [W&B `run.alert`(`wait_duration` = 最小送信間隔)](https://docs.wandb.ai/models/runs/alert) ・
[knockknock(12 バックエンド・Discord 含む)](https://github.com/huggingface/knockknock) ・
[whos-there(完了と**クラッシュ**の両方で通知)](https://pypi.org/project/whos-there/) ・
[MLflow webhooks(レジストリイベント限定・実験的)](https://mlflow.org/docs/latest/ml/webhooks/)

**サイドカー / 非侵襲監視**: [Azure: Sidecar pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/sidecar) ・
[Kubernetes ログ収集サイドカー](https://kubernetes.io/docs/concepts/cluster-administration/logging/) ・
[Mytkowicz et al. 観測者効果(<3% の計装でも結論が覆る)](https://scholar.colorado.edu/downloads/2v23vv18b)

**書きかけを読まない**: [Apache Parquet File Format(メタデータは最後)](https://parquet.apache.org/docs/file-format/) ・
[PyArrow `ignore_prefixes`](https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetDataset.html) ・
[`os.replace`(同一 FS で原子的)](https://docs.python.org/3/library/os.html#os.replace)

**Windows 共有フラグ**(リポジトリの実測事故の一次裏付け): [CreateFile / ERROR_SHARING_VIOLATION](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea) ・
[bpo-15244: CPython の `open()` は `FILE_SHARE_READ|WRITE` のみで **`FILE_SHARE_DELETE` を立てない**(未解決)](https://bugs.python.org/issue15244) ・
[CRT の共有定数 `_SH_DENYNO`](https://learn.microsoft.com/en-us/cpp/c-runtime-library/sharing-constants)

**HTML スナップショット / 撮影**: [Quarto `embed-resources`](https://quarto.org/docs/output-formats/html-basics.html) ・
[Plotly `write_html(include_plotlyjs=True)`](https://plotly.com/python/interactive-html-export/) ・
[Chrome headless(132 以降は `chrome-headless-shell` が別バイナリ)](https://developer.chrome.com/docs/chromium/headless) ・
[Playwright screenshots](https://playwright.dev/python/docs/screenshots)

**アラート設計**: [SRE Book: Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/) ・
[SRE Workbook: Alerting on SLOs(multiwindow / multi-burn-rate)](https://sre.google/workbook/alerting-on-slos/) ・
[Ewaschuk, My Philosophy on Alerting](https://gist.github.com/msgodf/86a3fc7fcd3ce663ff37) ・
[Prometheus Alertmanager(dedup / grouping / inhibition / silences)](https://prometheus.io/docs/alerting/latest/alertmanager/)

---

## 14. 承認をお願いしたい点(3 つ)

1. **レーン 1+2 を本選前に実装してよいか**(新規 1 ファイル・src/conf/tests 既存分は不触・既定は投稿しない `--dry-run`)。
2. **報告の粒度**: ハートビート(1 通を編集し続ける)+ シミュ日ごとの日次ダイジェスト、で合っているか。
   壁時計の日次(24h ごと)に変えることもできる。
3. **引用(エージェントの発話)を出すか**。既定 OFF を推奨(ETHICS §2-4 / 注入・メンション事故の面)。
   出すなら「本線モデルのランに限り・3 件・120 文字・架空注記つき・サニタイズ済み」を提案する。
