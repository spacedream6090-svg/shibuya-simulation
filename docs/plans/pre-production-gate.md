# 本番前ゲート一覧 — 25万体×10日ランを起動してよいかの1枚

> 2026-08-16作成([external-audit-triage.md](external-audit-triage.md) **§R6「完了ゲートの統合」**の実施。
> 予定は「β凍結時(8/18)」だったが、散在したままだと起動直前に読み合わせが間に合わないため前倒しした)。
> **この1枚だけ読めば起動判断ができる**ことを設計目標にしている。したがって他文書と重複する判定値は
> **転記して自足させ、出典パスを各行に併記**した(値が食い違ったら出典側が正典。食い違いを見つけたら §3 へ足す)。
>
> **この文書がやらないこと**: 開いている判断を勝手に閉じること。判断待ちは `⬜判断待ち` のまま残し、
> 誰が何の数字を見て決めるかだけを書く(記憶則 `ask-before-extending`)。
> **数値を捏造しない**: source に無い値は「未実測」と書き、空欄にしない。

## 0. 読み方

| 記号 | 意味 |
|---|---|
| ✅ | 済み(実装・実測・確認のいずれかが完了し、根拠が出典にある) |
| ⬜ | 待ち(未実施・未実測) |
| ⬜判断待ち | **ユーザーが決める**。Fable は数字と推奨を出すが、勝手に閉じない |
| 担当 | **F**=Fable(判定・検収・コミット) / **U**=ユーザー(手動作業・承認) / **S**=サーバー(gpu-sv-002 で実行) |

- **区分**: A 環境 / B conf・起動 / C 性能・資源 / D 正しさ・保存則 / E 観測・判定指標 / F 運用(保全・報告) / G 提出物・事前登録。
- コマンド列は**そのまま貼れる1行**にした。`<run>` はラン名、`<frozen>` は §B3 で作る凍結 conf。
- 本番の骨格日程(不変): **β動力学凍結 8/18 → 250kリハ 8/19-20 → conf確定+U-10承認 8/21 → 本番開始 8/22(遅くとも8/23)→ 提出 8/30**
  ([finals-endgame-plan.md](finals-endgame-plan.md) §1・[external-audit-triage.md](external-audit-triage.md) §6)。

---

## 1. ゲート表

### A. 環境(サーバー gpu-sv-002)— 11項

| # | 項目 | 判定値・線 | 確認方法(1行) | 担当 | 状態 |
|---|---|---|---|---|---|
| A1 | **Linux フルゲート緑** | 全緑。SFM wall golden 4件の Linux 不一致は**第126で恒久処置済み**=定数照合のみ `skipif(非Windows)`(Windows 値が正典・Linux 値で上書きしない)・プラットフォーム非依存の不変量(引数無視バイト一致等)は全 OS で検収維持。d2553f8 実測 = **5,901 passed / 15 skipped / 4 failed(全部 test_sfm_walls.py の定数照合=第126で解消)**・15分53秒。Windows 静止木は 5,919緑+1skip(第122) | `cd ~/projects/shibuya-simulation && git pull --ff-only && source ~/venvs/sim/bin/activate && ulimit -n 65535 && python -m pytest tests -q -n auto 2>&1 \| tail -3` | S | ⬜(β凍結版で再実行) |
| A2 | **ulimit -n 65535** | 実測既定 **1024 = 本番不足**(vLLM7本+parquet+sockets)。ランを張る tmux シェルで 65535 へ。vLLM プロセス側は soft/hard とも 65535 実測済み | `ulimit -n` (不足なら同シェルで `ulimit -n 65535`) | U/S | ⬜ |
| A3 | **RAM 判定線** | 実機 **251 GiB**(available 242)+ swap 8 GiB。250k 外挿 peak RSS が **GO < 180 GiB / CONDITIONAL 180〜220 / NO-GO > 220**(§3-⑦の未定義帯 215〜220 は 2026-08-16 に CONDITIONAL 側で確定=triage R2 も同時修正)。A2(PRES-A2)ON なら +72 GiB(楽観外挿 110+72=182=CONDITIONAL 境界) | `free -h; swapon --show` → 判定入力は C3 の 10k×144 peak RSS | S/F | ⬜(入力未実測) |
| A4 | ディスク | /home **3.7 TB 空き**。本番 run 本体 67〜70 GB+checkpoint 累積 50〜150 GB 級+退避先。今夜線=50 GB 以上 | `df -h / /home /tmp` | S | ✅(3.7TB) |
| A5 | GPU | RTX A5000 24GB **×7** 認識・Driver 595.84 / CUDA 13.2 / CC 8.6・全7枚 PyTorch matmul 成功 | `nvidia-smi --query-gpu=index,name,memory.total,driver_version --format=csv` | S | ✅ |
| A6 | NUMA トポロジ取得 | 64 logical CPU / **2 NUMA**。出力を保存し、**偏りが大きい時だけ** affinity を検討(盲目的 pinning はしない) | `nvidia-smi topo -m; numactl --hardware` | S | ⬜(未取得) |
| A7 | **持続熱試験** | 30〜60分連続推論で req/s のドリフトを確認。**最初 35 → 1時間後 25 なら壁時計見積りが壊れる**(閾値は未設定=実測してから置く) | 30-60分の連続推論中に `/metrics` を定期保存し req/s 系列を見る | S | ⬜(未実施) |
| A8 | vLLM `/metrics` 収集 | 全7ポートを 30〜60 秒間隔で保存(prefix hit / queue / KV 使用率 / TTFT)→ run artifact へ | `for p in 8000 8001 8002 8003 8004 8005 8006; do curl -s localhost:$p/metrics > metrics_$p_$(date +%s).txt; done` を watch で回す | S | ⬜ |
| A9 | egress 疎通 | huggingface.co / discord.com / github.com が 200 系。**Discord に出られない場合の退路**=ローカル PC へ日次 pull した先から投稿(機構は同一・報告が1日遅れるだけ) | `for h in huggingface.co discord.com github.com; do printf "%s: %s\n" "$h" "$(curl -sI --max-time 5 https://$h -o /dev/null -w '%{http_code}')"; done` | S | ⬜ |
| A10 | 実日付 | `run.start_date="auto"` が実日付を拾う。サーバー時計がずれていると天候・カレンダーがずれる | `date` | S | ⬜ |
| A11 | tmux | 長時間ランは tmux 内(セッション切断でランを殺さない)。ulimit は tmux シェル側で効かせる | `tmux -V` → `tmux new -s finals` | U/S | ⬜ |

### B. conf・起動 — 14項

| # | 項目 | 判定値・線 | 確認方法(1行) | 担当 | 状態 |
|---|---|---|---|---|---|
| B1 | **mock fail-fast ガード** | `run.n_agents >= 10,000` ∧ `model.backend == "mock"` ∧ `run.allow_mock_production == false` → **起動時 RuntimeError**。逃し弁は `run.allow_mock_production=true`(スケールスモーク用)。**打ち間違い1つで25万体 mock ラン**を防ぐ保険(監査 E0-4 / F5) | `python scripts/run.py --profile conf/finals_observe.yaml run.n_agents=10000 run.n_steps=1` が即 raise すること | F | ✅ 第121(`tests/test_launch_guard.py`) |
| B2 | **起動バナー目視** | 2行が stdout に出る: `backend / model / servers / n_agents / n_steps / seed` と `pool / pool_dir / present_cap / max_llm_per_step`。**本番起動の1秒目視で条件を確かめる** | 起動直後の `[launch]` 2行を読む(`scripts/run.py::banner_lines`) | U | ✅実装 / ⬜本番時に目視 |
| B3 | **freeze_config 生成+sha256 記録** | 「基底 < env < profile < dotlist」の4段を**解決し切った1枚**+`.sha256`。以降は `--profile <frozen>` の1行で起動(dotlist ゼロ=打ち間違いようがない)。**生成物はコミットしない**(.gitignore 済み・公開ミラー除外域でもない)。★`run.dt_min=10` 正準なら apply_dt は恒等パスで1バイトも変わらないが、**Δt≠10 の凍結ファイルは二重変換**になる | `python scripts/freeze_config.py --profile conf/finals_observe.yaml model.backend=vllm run.n_agents=250000 pool.present_cap=250000` | F/U | ⬜(本番直前) |
| B4 | **★present_cap を n_agents と同時指定** | **在場人口は `pool.present_cap` 側が効く**。`run.n_agents=2000` のまま `present_cap=250000` で起動して **CPU高負荷・RSS 2.5GB・GPU 0%・run dir 空** の実地事故が起きている(2026-08-16)。B3 の凍結 conf 方式なら構造的に踏めない | 起動バナー2行目の `present_cap=` が nominal N と一致していること | U | ⬜(運用線) |
| B5 | **model / revision / sampling 凍結** | model repo/revision/quantization(第一候補 Qwen3-8B-AWQ 6.11GB・14B-AWQ 9.99GB)・tokenizer/chat_template SHA・vLLM 版(実機 0.27.1)・sampling 全明示 + **`--generation-config vllm`**(既定 `auto` はモデル側 default に依存する)。**backend から取れない値は manifest の「起動側申告」欄**へ(捏造しない) | ラン後 `python -c "import json;print(json.load(open('runs/<run>/run_manifest.json'))['launch'])"` | F/U | ✅β10実装 / ⬜本番値記入 |
| B6 | **request_seed ON** | `llm.request_seed.enabled: true`(finals conf に投入済み・第121)。blake2b 安定 seed をリクエストへ付与。**プロンプト・呼数・キャッシュキーは1バイト不変**=「乱数条件の明示・保存」であって bit 決定論の保証ではない。実送出値は `llm_journal` の seed 欄 | `grep -n "request_seed" -A2 conf/finals_observe.yaml` → ラン後 journal の seed 欄が非空 | F | ✅ |
| B7 | **呼数 cap 再導出(β8/A1)** | 現行 `lod.max_llm_per_step: 300` = 43.2万呼/10日 = **0.173 回/人/日**。推奨帯 **1,500〜2,500**(0.86〜1.44 回/人/日・GO線140h に余裕)。★この表は **R_eff 悲観 18.3 呼/s 前提**であり、実機 end-to-end は **1.68 calls/s**(2k×20・batch_llm ON w8)=**前提が実機で未成立**。C4(deliberate batch)後に R_eff を取り直してから確定 | `python scripts/run.py ...` の summary から R_eff を出し、triage §2 の表を引き直す(Fable が返す) | U(決定)/F(表) | ⬜判断待ち |
| B8 | **fire 3行の解凍(D1)** | `cognition.fire / watch / engaged` をコメントアウト状態で待機中。**GO = T10 ≤ 140h ∧ 呼数増分 ≤ +15%** / CONDITIONAL = T10 140〜167h(`(166.96−T10)/T_llm` をその場で計算)/ NO-GO = fire OFF ですら T10 > 167h。★**triage §2-4 による再解釈**: tiers ON 下では fire は総呼数を増やせない(cap 内 general レーンの需要が増えるだけ)ので、判定主眼は「呼数増分」から**レーン飢餓カウンタ+行動品質**へ移る。**どちらの線で判定するかが未確定**(§3-②) | D1-a の mock 2ラン比較(`run.name=_fire_off` / `_fire_on`)+ `summary.json` の `starvation` | U(決定)/F(判定) | ⬜判断待ち |
| B8b | fire 事前チェック 8項 | #1 rotation 搬送 ✅ / #2 g_update 従属 ✅ / #3 watch・engaged 従属 ✅ / #4 DPH-B 相互作用(**tiers と必ず両方 ON**)✅ / #4b 繰り越し×周期発火の先送り ✅(第121 β1 `_at_first_reservation`)/ #5 予算外呼の消滅 ✅ / **#6 観測 ✅** / **#7 k 不変の再証明 ⬜** / **#8 U-10 閾値表への反映 ⬜** | 解凍を決めた直後に #7(`compute_matched` 下で k=free/k=off の呼数一致)と #8 を実施 | F | ⬜(#7・#8 のみ) |
| B9 | **POP 転出/転入 2行 ON** | 1〜2日ランの `summary.population.per_day` を現実レート **転出 7.8 / 転入 8.4 件・日** と照合し、合えば conf 2行 ON(PRES-A2 と同じ実測ゲート方式)。出生は既に finals ON(10日で約3.4件=現実の0.57倍) | `python -c "import json;print(json.load(open('runs/<run>/summary.json'))['population']['per_day'])"` | F(判定) | ⬜ |
| B10 | PRES-A2(emergent presence)1行 | RSS/R_eff 実測後に判定。ON なら RAM **+72 GiB**(A3 の線に直撃) | C3 の peak RSS と A3 の線を突き合わせる | F(判定) | ⬜ |
| B11 | **v2 ペルソナプール切替** | ①生成 ②tier_quota 再計算 ③縦煙48step 緑 ④conf 待機ブロックの1行。**LLM 生成は不採用が確定**(多様性崩壊を実証済み・台帳駆動が正) | `python scripts/build_persona_pool.py --seed 42 --v2 --childcare --out data/persona_pool_v2` | S/F | ⬜ |
| B12 | home_awake(β9)解凍 | `daily.home_awake.enabled` + `lead.mode: per_agent` + `evening_talk.enabled`。60体 mock 実測=帰宅→就寝 gap **257.3分(実264分に対し MAPE 2.5%)**・在宅覚醒 5:22(実 4:24)。**evening_talk は affects_k=True**(social/reply が +12.7% @60体mock=tiers cap 内の配分変化)。縦煙ゲート待ち | v2 縦煙と同便で 48step を回し、gap 分布・21時台在宅覚醒率・呼数を見る | F | ⬜ |
| B13 | `engine.batch_llm` | `enabled=true workers=8`。**未配線なら計画呼が完全直列 = T10 直撃**。決定論は workers 1 vs 4 の state_hash 一致で証明済み。workers 8/16/32 の tuning は C4 の後 | `python scripts/run.py ... engine.batch_llm.enabled=true engine.batch_llm.workers=8` の短 A/B | F(判定) | ⬜ |
| B14 | 未宣言トグルなし | finals conf の全トグルが基底 conf に宣言済み(全プロファイル走査の再発防止テスト) | フルゲート(D1)に同梱 | F | ✅ 第114 |

### C. 性能・資源(実測)— 9項

| # | 項目 | 判定値・線 | 確認方法(1行) | 担当 | 状態 |
|---|---|---|---|---|---|
| C1 | **R_eff / c の実機値** | 既知の実測点: Fleet 直叩きマイクロベンチ **default tier(GPU1-6)w8 = 54.64 calls/s** / **reflect tier(GPU0)w8 = 46.38 calls/s**(errors 0)。**実走 end-to-end = 1.68 calls/s**(2k×20・970呼/577.7秒・batch_llm ON w8)。**c(エンジン秒/体/step)は未実測** | `python scripts/run.py --profile <vllm7> run.seed=42 run.n_agents=2000 run.n_steps=144 pool.present_cap=2000 run.name=night0_smoke` | S/F | ⬜(2k×144 未実施) |
| C2 | **T10(25万×10日の総壁時計)** | 実効枠 **W = 192h**(保守)/ 216h(楽観)・運用余裕 15% → **W/1.15 = 166.96h**。GO 線 **≤ 140h**。旧外挿 72 / 139.7 / 164.3h は **DPH-B 以前(738万呼前提)= 古い**。cap 300 の新表では 34〜59h | C1 の R_eff/c を triage §2 と dashboard D1-b の両表へ代入(Fable が引き直す) | F | ⬜ |
| C3 | **10k × 144step peak RSS** | **RAM 線(A3)の決定量**。傾き候補が2本併存: **0.362 MB/体(→88〜110GB)** vs **1.265 MB/体(→316〜363GB)**。実測点は 2k×20 で **peak_rss_mb = 994.7**(=0.497MB/体・ただし20step) | `python scripts/run.py --profile <frozen> run.n_agents=10000 pool.present_cap=10000 run.n_steps=144 run.name=scale1_10k` → `summary.json` の `peak_rss_mb` | S/F | ⬜(**最重要の未実測**) |
| C4 | **deliberate の step 単位 batch 化(B5レーン)** | 実走で `deliberate = 450 呼 / 20 step`(**最大 88 呼/step**)が **batch 対象外の逐次経路**に残っている(batch 済みは planning / reflection のみ)。**逐次完全一致(OFF / w1 / w8)**が着地条件 | 着地後に Step3 回帰(2k×20・baseline `llm_calls=970 / elapsed 577.689s / peak_rss 994.7MB` と比較) | F | ⬜(発注済み・未着地) |
| C5 | checkpoint 1個の実サイズ・保存実時間 | **未実測**。実測後に Young/Daly で `checkpoint_every` を確定(信頼性リハ #1)。β7 で stream 書き+fsync+COMPLETE マーカー化済み(保存ピーク −35%・時間同等) | 250k リハ中に `ls -l runs/<run>/checkpoint/` と保存前後の時刻差を記録 | S | ⬜ |
| C6 | `--stall-step-sec` の実測値 | 25万の 1 step 実時間(想定 ~10分)。判定は **max(--stall-min, step_sec × factor 6)** = **必ず待つ側へ倒れる**。未測定なら引数を渡さず従来の `--stall-min 20` で動く(退路つき) | 診断ランの壁時計 ÷ step 数 | F | ⬜ |
| C7 | `reflect_max_tokens = 768` の効果 | conf/profiles/finals-vllm7.yaml に **768 で投入済み**(2048 は think=true 時代の名残で約8倍過大・実測 p95 ≈ 247 tok)。**vLLM は max_tokens 分の KV スロットを予約**するので高並列時のスループットに効く。**前後比較は未実測** | 高並列時の tok/s を 2048 と 768 で比較(`/metrics` の generation throughput) | S | ⬜ |
| C8 | prefix cache / speculative | prefix cache は**文献値ヒット率 ~96%**(実機未実測)。speculative は任意=**greedy(temperature=0)で出力バイト一致**を無損失判定に使う(0.7 ではバイト一致を判定に使わない) | `curl -s localhost:8000/metrics \| grep prefix_cache` | S | ⬜ |
| C9 | 転送 drill | 実サイズ tar → ローカル pull → sha256 照合の所要時間(信頼性リハ #5)。日次増分 5〜15GB 想定=100Mbps で 30分未満 | `python scripts/backup_run.py --run-dir runs/<run> --dest <退避先> --ckpt-generations 999` の実測時間 | U/S | ⬜ |

### D. 正しさ・保存則 — 8項

| # | 項目 | 判定値・線 | 確認方法(1行) | 担当 | 状態 |
|---|---|---|---|---|---|
| D1 | **静止木フルゲート(Windows 正典)** | 第121 時点 **5,904 緑 + 1 skip**(12分42秒)。β凍結版で回し直す | `python -m pytest tests -q -n auto` | F | ⬜(凍結後に再実行) |
| D2 | **golden L1 バイト一致** | 既定 conf の L1 バイト一致。**Linux の SFM wall 4件不一致は宣言済み例外**(Windows が正典・Linux 値で上書きしない) | D1 に同梱(`tests/` の golden 群) | F | ✅規律 / ⬜再実行 |
| D3 | **resume == straight** | サイドカー含め完全一致(機械検収済み・DPH 38緑にも同型テスト)。**実ランでの kill→自動復帰 drill は別**(信頼性リハ #2) | D1 に同梱 + 実ラン drill(watchdog に kill を食わせる) | F/S | ✅テスト / ⬜実ラン |
| D4 | 保存則(金・人数) | 金と人数の Σ 整合・幽霊書き込みゼロ・row_flow 残差 0。**ラン中に日次で回せる**(U5 の流し見) | `python scripts/analyze_accounting.py runs/<run>` | F | ⬜(ラン中運用) |
| D5 | **事後・全数の世界整合検査(V2)** | 22 検査(位置/階・node と xy・在館の閉じ・年齢×職業・死の永続性・幽霊書込み・転出規約…)。60体 mock で **VIOLATION 0**。250k リハ後に実行する前提の O(イベント数) 実装 | `python scripts/audit_world_invariants.py runs/<run>` | F | ✅実装 / ⬜250kリハ後 |
| D6 | **信頼性リハーサル 7本** | ①C 実測(checkpoint 書き込み時間・世代サイズ@25万)②resume drill ③**restore drill**(バックアップコピーだけで解析が回るか)④障害注入3種(ディスク僅少・vLLM 停止・プロセス kill)⑤転送 drill ⑥無人運用 drill(夜間8h 放置)⑦vLLM 計画再起動 drill | 手順書どおり([finals-reliability-plan.md](finals-reliability-plan.md) §4) | U/S | ⬜ |
| D7 | 新 kind の二重登録 | 新 kind は **schema と causality の2箇所**に登録。未登録だと `logger.log()` が KeyError で即死し、**本選ランが最初の1件で落ちる**(第115 の実例)。登録網羅テストで機械固定 | D1 に同梱 | F | ✅ |
| D8 | 凍結14本不触 | `metrics_spec_hash` の SPEC_FILES は **コメント1文字でもハッシュが動く**。解析側の新規スクリプトは SPEC_FILES に含めない | スキャン+D1 | F | ✅規律 |

### E. 観測・判定指標 — 9項

| # | 項目 | 判定値・線 | 確認方法(1行) | 担当 | 状態 |
|---|---|---|---|---|---|
| E1 | **used/cap** | **≥ 0.90 維持 / 0.75〜0.90 は lane share 再配分 / < 0.75 で reclaim 検討**。理由=DPH-B の general は reply/life の**予約の余りを借りられない**設計なので、cap を上げても used/cap < 1 がありうる | `python -c "import json;print(json.load(open('runs/<run>/summary.json'))['starvation']['llm_budget'])"` | F | ✅実装(第121)/ ⬜実測 |
| E2 | **zero-call 率 / calls/person P50・P90・Gini / 属性別 coverage** | 「平均だけでは25万人に届いたか分からない」への回答。reality_score の Cognition 節が `cog_calls_per_person_day` / `cog_zero_call_share` / `cog_calls_distribution`(P50・P90・Gini)/ `cog_lane_coverage` / `cog_attr_coverage`(=その属性で1回以上呼ばれた割合)を出す。**単一の合否線は置かない**(総合1点に潰さない設計をテストで固定済み)。**基準帯は registry.yaml のアンカーに従い、実測後に成分表示** | `python scripts/reality_score.py runs/<run>` | F | ✅実装 / ⬜実測 |
| E3 | 飢餓カウンタ(DPH-O) | `summary.json` の `starvation`: `reply_dropped` / `plan_skipped` / `reflect_dropped` / purpose 別 denied / `plan_expired_awake`。**DPH-B ON で返事保証は 2.6% → 100%**(落ちた返事 74 → 0・総呼数 502 → 218)。**`reply` の denied が増えたら二層予算が効いていない** | E1 と同じ `summary.json` の `starvation` ブロック | F | ✅実装 / ⬜実測 |
| E4 | **POP per_day 照合** | 転出 **7.8** / 転入 **8.4** 件・日(現実レート換算)。合えば B9 の 2行を ON | B9 と同じ | F | ⬜ |
| E5 | **presence 較正** | v2 で presence 資格 306,716 → **270,255**(L2 出勤率 0.62)= **非通勤来街 74,947 人日が較正目標 6〜13万** に着地。**present_cap 250,000 に対し資格者 270,255 なので cap はまだ binding**(=在場が cap で決まっている状態) | `python scripts/calibrate_report.py runs/<run>` の presence 節 | F | ⬜(本番規模で再確認) |
| E6 | reality_score v1 + Data Vintage + Crosswalk | カテゴリ別に **JSD/MAPE/KS を成分表示**(総合1点を作らない)・calibration/holdout 分離・アンカー 31件(holdout 20 / calibration 6 / diagnostic 5)。**社会生活基本調査 2026 は提出前に未公表 = 2021 が正当な最新**・メディアは令和7年度版(平日183.9分)・家計調査2025年平均。空間分母(bbox/区/都)は Crosswalk に明記 | E2 と同じコマンド(`--out runs/<run>/reality`) | F | ✅実装 / ⬜実測 |
| E7 | GT ロガー G1-G7 が生えていること | G1 入力3件 sha256 → manifest / G2 剪定禁止 / G4 memory.parquet / G5 relations.parquet / G6 sat 4列(observer 列=σ_c 凍結を無効化しない) / G7 小物束。**finals ON** | ラン後 `ls runs/<run>/*.parquet runs/<run>/run_manifest.json` | F | ✅実装 / ⬜ラン後確認 |
| E8 | 観測非侵襲 | 観測 ON/OFF で **行動列・LLM 呼数・乱数・世界の最終状態が完全一致**(機械固定済み)。**ラン中に見て conf を触らない** | D1 に同梱 | F | ✅ |
| E9 | ラン中の「流し見」8件 | U1 伝播木の深さ / U2 `verify` 件数 / U4 計画突合 / U5 保存則 / U7 `undefined_action` / U10 造語 / U11 規範段到達 / U14 記憶行数。**見るだけ**(★造語は促進しない=`natural-coinage-observation`) | 日次ダイジェスト(F5)+ `python scripts/report_progress.py runs/<run> --extract --day <n>` | U/F | ⬜(運用) |

### F. 運用(保全・報告)— 7項

| # | 項目 | 判定値・線 | 確認方法(1行) | 担当 | 状態 |
|---|---|---|---|---|---|
| F1 | **watchdog 本選値(E3)** | 停滞 = `--stall-step-sec <実測>` + `--stall-factor 6`(= max(20分, step_sec×6))/ ディスク **warn 50GB・crit 20GB**。**コードの既定値は1つも変えていない**=CLI で明示上書きする。★**`--run-dir` は必須フラグ**(位置引数ではない=§3-⑤) | `python scripts/watchdog.py --run-dir runs/finals1 --stall-step-sec <実測> --stall-factor 6 --disk-warn-gb 50 --disk-crit-gb 20 -- run.out_dir=runs run.name=finals1 --profile <frozen>` | U/S | ⬜ |
| F2 | **backup 本選値** | **`--ckpt-generations 999`**(既定 2 のままだと 20 世代のうち 18 世代が手元に残らない)。★**`--run-dir` / `--dest` はフラグ**(位置引数ではない=§3-⑤) | `python scripts/backup_run.py --run-dir runs/finals1 --dest <退避先> --ckpt-generations 999` | U/S | ⬜ |
| F3 | **E0 剪定禁止** | `ckpt-NNNNNN.pkl.gz` と同 step の `dormant-NNNNNN.pkl.gz` を**必ず対で**残す。**半日粒度の完全状態は checkpoint にしかない**(GT ロガーは日境界粒度)。逼迫時に落とす順序 ① `indoor_tracks_*` ② `llm_journal` ③ ユーザー判断。**checkpoint と dormant は最後**・`rm checkpoint/*` は絶対禁止 | `ls runs/<run>/checkpoint/ \| wc -l` を日次で見る(減っていないこと) | U/S | ✅規律 / ⬜運用 |
| F4 | **Discord webhook env(M3)** | 環境変数 `SHIBUYA_DISCORD_WEBHOOK`。**URL はリポジトリにもチャットにも CLI 引数にも書かない**(ps に残る)。退路 = `%USERPROFILE%\.shibuya\discord_webhook.txt`(1行・リポ外) | (Windows) `[Environment]::SetEnvironmentVariable('SHIBUYA_DISCORD_WEBHOOK','<URL>','User')` / (Linux) tmux 内で `export SHIBUYA_DISCORD_WEBHOOK=<URL>` | U | ⬜(ユーザー作業) |
| F5 | 進捗報告(初回は必ず dry-run) | ハートビート=1通を編集し続ける(既定10分)/ 日次ダイジェスト=シミュ日境界(本選=実時間7〜16h おき・全10通強)+ rollup.html 添付 / アラート=状態遷移時のみ。抑制した件数は**次の日次に必ず数を出す**(silent cap 禁止)。**L1 は1バイトも読まない別プロセス・終了コードは常に0** | `python scripts/report_progress.py runs/<run> --dry-run` → 中身目視 → `python scripts/report_progress.py runs/<run> --interval 900` | U/S | ⬜ |
| F6 | 走行中の禁止事項 | 走行中 run-dir への `cp -r`/`robocopy` 直がけ禁止(backup_run 経由=共有フラグ読み)・走行中の conf 編集は次のランから(実行中ランは run-dir 内の conf コピーが正)・`rm checkpoint/*` 禁止 | — (運用規律) | U | ✅規律 |
| F7 | 公開ミラー衛生 | **ops/ はミラー対象**。サーバー識別子(hostname / 内部IP / SSH ユーザー)を含むファイルは除外リスト+全履歴の識別子検査。監査・引き継ぎ文書は `docs/plans/source/`(ミラー除外域)へ | `powershell -File ops/publish_public_mirror.ps1` 実行前に除外リストを確認 | F | ✅ 第123 |

### G. 提出物・事前登録 — 5項

| # | 項目 | 判定値・線 | 確認方法(1行) | 担当 | 状態 |
|---|---|---|---|---|---|
| G1 | **U-10 事前登録の承認** | 閾値表(§4-A/B/C・E・F・G・H・I)+ **本書 §4 のドラフト**をセットで承認。**本番開始直前(8/21-22)に Fable から依頼**。承認後は変更禁止=変更したら §7 変更履歴に記録し**変更前後の判定を両方報告** | 本書 §4 を読み、`承認` / 修正指示 を返す | U | ⬜判断待ち |
| G2 | **提出要件の確認** | ハッカソン要項の**形式・分量・データ添付可否**をユーザーが確認して共有 → 逆算して 8/28-29 に組む。**未取得**(数値・条件とも source に無い) | 要項を確認して共有 | U | ⬜判断待ち |
| G3 | **尾部(8/26-30)の配分** | 推奨 = **seed 2本目(短縮可)+ 介入 fork 1本 + shadow 高認知ラン**の3点セット。★**seed 2本目が無いと10日ランの量的主張がほぼ全部「1標本」に落ちる**(事前登録 G3 = 条件内 seed 3本要求に届かない) | 本書 §4.6 の配分案を承認 or 修正 | U | ⬜判断待ち |
| G4 | 観察ラン報告書の骨格 | ODD 2020 対応表・§micro/§macro/§system/§頑健性・宣言欄(S-05/S-08/S-15/S-17)。**「何と比較したか / 比較できないならなぜできないかと代替」欄は必須** | [observation-report-template.md](observation-report-template.md) に沿って組む | F | ✅テンプレ有り |
| G5 | 解析の再現性 | 解析スクリプトは全部**読み取り専用・src ゼロタッチ**。提出物に載せる図表は**どのランのどのコマンドから出たか**を併記 | 各スクリプトの `--out` 先を run-dir 配下に固定 | F | ✅設計 |

**ゲート項目数(合計 64行)**: A 環境 11 / B conf・起動 **15**(B1〜B14 + fire 事前チェックの B8b)/ C 性能・資源 9 / D 正しさ・保存則 8 / E 観測・判定指標 9 / F 運用 7 / G 提出物・事前登録 5。
状態の内訳: **完全に済み ✅ = 12 / 一部済み(✅実装・⬜実測など)= 11 / 待ち ⬜ = 36 / ユーザーの判断待ち ⬜判断待ち = 5**
(ゲート表に現れない判断=A5 PLATEAU・A8 モデル構成・A9 structured outputs 等を足した全体の判断待ちは **§2 の 13 件**)。

---

## 2. 判断待ち一覧(⬜判断待ち = ユーザーが決める)

| # | 事項 | 決めるのに要る数字 | 期限 | 出典 |
|---|---|---|---|---|
| J1 | **呼数 cap の値**(β8/A1: 300 → 1,500〜2,500?) | 実機 R_eff(★C4 の deliberate batch 後)・used/cap | 実測後 | triage §2・§5 A1 |
| J2 | **fire 3行を開けるか**(D1) | T10・呼数増分・レーン飢餓カウンタ。**判定線を旧 D1-b(T10/増分)で引くか、triage の再解釈(飢餓+品質)で引くか自体が未確定** | 実測後 | dashboard D1・triage §2-4 |
| J3 | POP 転出/転入 ON | `summary.population.per_day` vs 7.8 / 8.4 | リハ後 | dashboard・runbook Phase3-2 |
| J4 | PRES-A2 ON(RAM +72GiB) | 10k×144 peak RSS と A3 の線 | 実測後 | endgame §3.2 |
| J5 | v2 プール切替 / home_awake 解凍 | 縦煙48step の結果 | 8/17-18 | endgame §4・conf 13b |
| J6 | **A5: PLATEAU 2025 の viewer 側だけやるか** | **✅決定済み(2026-08-16)=今やる**(C4レーン実行中・engine 側は NO で確定) | — | triage §5 A5 |
| J7 | **A8: モデル構成 S0(7×8B)vs S1(6×8B+1×14B)** | ミニ行動トーナメント(8B vs 14B・数百シナリオ・半日) | 8/18 | triage §R4 |
| J8 | **A9: JSON Schema structured outputs** | constrained decoding の A/B(出力分布を変えるため) | 8/18 | triage §R4 |
| J9 | **尾部の配分**(seed2 / 介入 fork / shadow) | — | 8/20 | triage §3.4・§5 A6 |
| J10 | **U-10 事前登録の承認**(閾値表+本書 §4) | 実 LLM 診断ランの結果(★どこで取るかが未定=§3-④) | 8/21-22 | dashboard D4・G1 |
| J11 | **本番開始日**(推奨 8/22・遅くとも 8/23) | 250k リハの完走 | 8/21 | endgame §1・§7-9 |
| J12 | 提出物の構成 | ハッカソン要項(形式・分量・データ添付可否) | 8/25頃 | endgame §7-11 |
| J13 | 賃金の残り2点(最賃集積・家賃窓) | — (推奨=現状維持・記録済み) | 任意 | dashboard D7 |
| J14 | **長プロンプトの予防**(2k×144実測: プロンプト+max_tokensがmax_model_len 8192超過らしき1リクエストが全サーバー400。第131でfailover汚染は止血済み=当該呼はエラー→骨格fallback)。選択肢: (a)何もしない(発生率をjournalで監視・250kで率を見て再判断) (b)max_tokensを残余に合わせ縮める(切り詰めなし・応答が短くなるだけ) (c)vLLMのtruncate_prompt_tokens(プロンプト頭が落ちる=persona喪失・非推奨)。**推奨=(a)で観測→10k×144の発生率で(b)を再判断** | 発生率(l1b/journalの`__vllm_error__: HTTP 400`件数) | 10k×144後 | 本書§3実測・fleet.py第131 |

---

## 3. ★統合中に見つけた source 間の食い違い(要確認)

**この節は「見つけた」だけで、直していない**(勝手に閉じない)。①〜⑤は起動前に潰す価値が高い。

| # | 食い違い | 詳細 | 影響 |
|---|---|---|---|
| ① | **fire 判定に使う T10 表が2つ併存** | dashboard D1-b の T10 表(72 / 139.7 / 164.3h)は **DPH-B(tiers)以前=738万呼前提**。triage §2 は cap 300 で総呼 43.2万・LLM 6.6h・**T10 34〜59h**。endgame §1 にも「古い」旨の改訂注がある | **GO 線 140h をどちらの表で引くかで判定が変わる**。Fable が実測後に1本へ引き直す必要がある |
| ② | **fire の判定基準そのものが二重** | dashboard D1-b =「呼数増分 ≤ +15%」/ triage §2-4 =「tiers ON 下では fire は総呼数を増やせないので、主眼は飢餓カウンタと行動品質へ移る」 | 増分基準は tiers ON 下では**原理的に常に満たされる**(cap 内の配分変化)=基準が空振りする恐れ |
| ③ | **実機 R_eff が cap 再導出表の前提と桁で食い違う** | triage §2 の cap 表は **R_eff 悲観 18.3 呼/s** 前提。実機の end-to-end は **1.68 calls/s**(Fleet 直叩きは 54.6 calls/s)。真因は deliberate が batch 対象外(C4) | **cap 1,500〜2,500 は C4 の着地前に確定できない**。先に確定すると本番が壁時計で破綻しうる |
| ④ | **U-10 の「実 LLM 診断ラン」が本選日程に無い** | 事前登録 §4「適用スケジュール」は「GPU 開放初日(8/15-16)の実 LLM 診断ラン(数百体×20 sim日相当)= **これが確定判定に使うラン**」と書くが、endgame §1 の日程表・runbook の Phase 0-3 に**この診断ランが1行も無い**(Phase 1 は 2k×144 の性能スモーク) | **U-10 の確定判定に使うランが存在しないまま承認する**ことになる。代替=本番10日ランに同じ CLI を事後適用(§4.4 に記載)だが、それは事前登録の「ラン前に固定」の趣旨と別物 |
| ⑤ | **runbook / checklist のコマンドが実 CLI と合わない** | runbook Phase 2 の `python scripts/watchdog.py runs/scale1_10k` → 実際は **`--run-dir` が required**(位置引数を受けない)。runbook 完走後の `python scripts/backup_run.py runs/scale1_10k <退避先> ...` と checklist E0 の `backup_run.py <run_dir> <dest> ...` → 実際は **`--run-dir` / `--dest` がフラグ**(位置引数を受けない) | **✅解消(2026-08-16)**: argparse 実物で裏取り(watchdog.py:796=required・backup_run.py:870/872=フラグ)の上、runbook 2行+checklist E0 の 1行を実 CLI へ修正 |
| ⑥ | **10日ランの日付が文書間でずれている** | PENDING.md §台帳と事前登録 §4 は「10日ラン **8/16-8/26**」・runbook Phase3 も「本番10日ラン開始の直前」/ endgame §1 と triage §6 は「**本番開始 8/22**・完走〜8/27-28・提出 8/30」 | 旧日程が残っている文書を読むと**承認タイミングを1週間早く見積もる**。正典は endgame §1(8/22) |
| ⑦ | **RAM 判定線に未定義の帯がある** | triage R2 = 「GO < 180GiB / CONDITIONAL 180〜215 / **NO-GO > 220**」→ **215〜220 GiB が どの区分でもない** | **✅解消(2026-08-16)**: CONDITIONAL を 180〜220 に拡張して帯を閉じた(220 超は宣言どおり NO-GO・triage R2 と本書 A3 を同時修正) |
| ⑧ | **dashboard D2 の選択肢に見送り済み項目が残る** | D2-(a) は「seed2本目を最優先→**残りで反実仮想U15**」だが、**U15 は 2026-08-15 に見送り決定済み**。triage §5 A6 は「seed2短縮+**介入 fork 1本**+shadow」 | 尾部配分(J9)の選択肢が2文書で違う。本書 G3・§4.6 は triage 側(fork)で書いた |
| ⑨ | **β5(sleep_task_rewrite 実 LLM 検収)の行方** | endgame §2(i) は「GPU 到着で初めて可能・良ければ ON・時間切れなら OFF のまま」と β に数えるが、第121 の β 実装波の着地報告に**この項目が出てこない**。conf は `daily.sleep_task_rewrite: false`(finals も OFF 据え置き=ユーザー判断待ちと明記)・PENDING も「実LLM検収待ちOFF」 | 実質 **OFF 据え置きで確定**しており、落ちてもリスクゼロ(退路つき)。ゲート表には落とさず、ここに記録するに留めた |
| ⑩ | Discord 手順の参照先が節番号までは一致しない | endgame M3 は「finals-compute-checklist.md **§E2**」を指す。実体は **§E2-0**(事前準備・ユーザー作業1回だけ) | 実害なし(同じ節の中) |

---

# 4. U-10 事前登録(ドラフト・**承認待ち**)

> **これはドラフトである。本番10日ランの開始直前(8/21-22)にユーザー承認を得る**(記憶則 = U-10 は
> 「本番直前に決定」とユーザー指定済み)。**承認前は変更自由・承認後は変更禁止**。承認後に変更が必要に
> なったら、[stationarity-preregistration.md](stationarity-preregistration.md) §7 変更履歴に
> 「変更した事実・日付・理由」を記録し、**変更前後の判定を両方報告する**(事後的な閾値いじりを隠さない)。
>
> **既存文書との関係**: 閾値の正典は [stationarity-preregistration.md](stationarity-preregistration.md)
> (§3-A/B/C 非定常性・§3-E 規範・§3-F stylized facts・§3-G seed 分散・§3-H 一様予算・§3-I 組織形態)。
> 本章はそれを**置き換えず**、観察ラン全体の事前登録として **(a) 仮説の一覧 (b) 仮説→指標→スクリプトの
> 対応 (c) 停止・介入規則 (d) 尾部配分**を足す。数値の閾値は既存側にあるものはそちらを参照し、
> **本章で新しい閾値を発明しない**。

## 4.1 主要仮説(ラン前に固定する)

| # | 仮説 | 何を主張し / 何を主張しないか |
|---|---|---|
| **H1** | **k\*(世界改変志向の個体)の内生的出現**: この設計(実地図・実ダイヤ・IPF 合成人口・**全個体一様の認知予算**・10日)の下で、k\* の出現に対する**初期特性の寄与と環境フィードバックの寄与の相対的大きさ**が測れる | 主張する = 相対的大きさ。**主張しない** = 現実の渋谷で同じ**比率**が出ること・個体が実在個人と一致すること。★**「相転移」を主張するには条件を跨いだ非連続性が要り、それには seed 2本目(§4.6)が必須**。無ければ H1 は「1標本の記述」に落ちる |
| **H2** | **組織の自然形成とファウンダー成立条件**: 組織が下から立ち上がるか、立ち上がるとき前史に何があるか | 形(centralized↔decentralized / layered / 役割 / static↔dynamic)を報告する。**組織サイズ分布の同定(Zipf/Gibrat)はしない**(N が 4-5桁足りない=F10/F11 は「検定不能」と明記する枠) |
| **H3** | **語の自然発生と伝播**: 造語がいつ・誰の・どんな文脈で生まれ、どの層(offline / online / broadcast)で広がるか | **促成しない**(記憶則 `natural-coinage-observation`)。ラン中は件数を流し見するだけで、conf も prompt も触らない。伝播は**三層**で報告(二層では尽くせない=broadcast の存在自体が知見) |
| **H4** | **規範・制度の自然発生**: 4段(coin / quote / definite / institution)の到達と、下方因果(規範が個体の行動を縛るか) | **S4 到達を「内面化」と読まない**。本シムの S4 が見ているのは**言及だけ**で、「規範に従って行動した」は測っていない。**flexible 型**(違反を機構で禁じていない)という位置づけを明記 |
| **H5** | **日常の非定常性**: Day t と Day t' が日間ノイズ床を超えて区別できるか(原指示 D「饒舌な日常の反復に収束するリスク」の検証) | 判定式は既存 §4 を**逐語で使う**(SUSTAINED_NONSTATIONARY / TRANSIENT_ONLY / STATIONARY_LIKE / NONSTATIONARY_UNVERIFIED / INCONCLUSIVE)。★**burn-in ≈ 18日なので 10日ランはほぼ全部が過渡**であることを承知の上で読む |
| **H6** | **人間行動の stylized facts の再現**: 主判定 4件(**F5 バースト性 / F6 対面接触時間の裾 / F4 滞在時間の裾 / F7 次数分布の裾(条件付き)**) | 主判定 4件は**入力に埋め込まれていない**もの(タイミングと接触は空間・スケジューリングから内生)。F1/F2/F3/F8/F9/F12 は**参考**(循環性が高い=「EPR を入れたから EPR 則が出た」)。F10/F11 は**不採用=検定できないと書く**。F7 は `relations.dunbar` OFF 条件に限る |

**共通の境界宣言(既存 §前文をそのまま引き継ぐ)**: 主張は**条件間差が seed 間差を上回った指標に限る** /
モデル1系統・時間尺度10日 / **LLM 社会シムは対立を系統的に過小表現する = 観測された協調水準は上限側の推定値** /
分散比は片側バンド(下回れば「痩せている」と言えるが、上回っても「十分」とは言えない)。

## 4.2 主要評価指標(仮説 → 指標 → 判定枠)

| 仮説 | 主指標 | 判定枠・閾値 | 出典 |
|---|---|---|---|
| H1 | k\* 出現率・特性寄与 vs 環境寄与の分散分解 | **G1 ratio > 1.0 ∧ G2 ブートストラップ95%CI下限 > 1.0 ∧ G3 条件内 seed ≥ 3本**。満たさない指標は `INSUFFICIENT_SEEDS` として**有意でも主張しない**。`V_seed = 0` は `DEGENERATE_ZERO_SEED_VARIANCE` | 事前登録 §3-G |
| H2 | Freeman \(C_D\)+degree_gini(集権度)/ GRC(層)/ Guimerà–Amaral (z,P)(役割)/ Palla ライフサイクル+Jaccard(動態)/ betweenness | **eigenvector 中心性は採らない**(理由3点を事前に宣言済み)。(z,P) の原典閾値 2.5 / 0.62 は代謝ネット較正値なので**既定は分位点で報告し、4分類の件数は参考値**に留める | 事前登録 §3-I |
| H3 | 新規語彙出現率 ν(d)・語彙エントロピー・Jaccard・三層別の伝播量 | ν の閾値 **C1 = ν̄_late ≥ 0.05** は**報告であってゲートではない**。★**mock 由来の ν 絶対値を実 LLM の合否に使わない**(C1 は実 LLM で再較正する予定=未実施) | 事前登録 §1.1・§3-C・§6 |
| H4 | norm_stage 4段の到達・下方因果 | **E1 stage ≥ 3 / E2 使用者 ≥ 3名 / E3 stage ≥ 4 でも同方向(副判定)/ E4 コホート n ≥ 10・full-day 要求(満たさねば「判定不能」)/ E5 ラベル置換 p < 0.05**。**語の可用性交絡**を必ず併記し、単独で「下方因果」と断定しない | 事前登録 §3-E |
| H5 | TVD / R = TVD/F / 置換検定 p / lag_slope / lag_min / burn_in_end | **primary = p < 0.05 ∧ TVD ≥ 0.05 ∧ R ≥ 1.50**、**sustained = late_same_lag ペアで同条件**。★**p 単独では判定に使えない**(n が数百あると隣接日でも p < 0.05 になる) | 事前登録 §3-A/B・§4 |
| H6 | F5 burstiness B と memory M / F6 接触継続・総接触・接触間隔 / F4 滞在時間の対数尤度比 / F7 層別次数分布 | F4 は「**指数分布の棄却**」までを主張し、どの裾かは主張しない。F7 は offline / online で**層ごとに合否を出して併記**(層で割れること自体が知見) | 事前登録 §3-F |
| 全体 | **データ品質除外** | L2 `echo_max == 1.000` の**崩壊ラン**は k\*・規範・F5/F6 の母集団から**除外して別掲**(除外数と条件を必ず報告) | 事前登録 §1.1・§3-F.5 |
| 全体 | **認知の到達度(監査追補)** | zero-call 率・calls/person P50/P90/Gini・属性別 coverage・used/cap を**必ず併記**する(「平均だけでは25万人に届いたか分からない」) | triage §R4・本書 E1/E2 |

## 4.3 解析計画(どのスクリプトで何を出すか)

**ラン中(日次・読み取り専用・世界に触れない)**

| 何を | コマンド | 見るもの |
|---|---|---|
| 進捗・アラート | `python scripts/report_progress.py runs/<run> --interval 900` | ハートビート / 日次ダイジェスト / 6種アラート |
| 予算と飢餓 | `python -c "import json;print(json.load(open('runs/<run>/summary.json'))['starvation'])"` | used/cap・reply_dropped・purpose 別 denied |
| 保存則 | `python scripts/analyze_accounting.py runs/<run>` | 金と人数の Σ 整合(残差 0) |
| 日次の取り出し | `python scripts/report_progress.py runs/<run> --extract --day <n>` | l2_metrics / digest / rollup.html |
| 流し見8件 | 上の digest + rollup | 造語件数・規範段到達・undefined_action・記憶行数ほか(**見るだけ**) |

**ラン後(本選後の解析。新規実装は全部ここ=ラン前に書くコードは1行も無い)**

| 仮説 | スクリプト | 出力 |
|---|---|---|
| H5 | `python scripts/diagnose_stationarity.py runs/<run>` | `diagnose_stationarity.json/.md`(TVD/R/p/lag/verdict ラベル) |
| H1 | `python scripts/analyze_seed_variance.py "runs/finals*_s*"` | V_condition / V_seed / ratio / share / ブートストラップ CI / 判定ラベル |
| H2 | `python scripts/analyze_founders.py` + `python scripts/analyze_org_form.py` | ファウンダー検出+前史+マッチ対照 / \(C_D\)・GRC・(z,P)・Jaccard |
| H3 | `python scripts/analyze_specialization.py` + `python scripts/detect_emergence.py` | 語の専門化・創発検出(+U10 の造語文脈カードは本選後の小実装) |
| H4 | `python scripts/analyze_norms.py --norm-stage 3 --norm-threshold 3` | 4段到達・下方因果(**閾値は引数必須=既定値を埋め込まない設計**) |
| H6 | `python scripts/analyze_weak_ties.py` / `analyze_structure.py` / `analyze_communities.py` / `analyze_bridging.py` | 接触グラフ・裾・コミュニティ |
| 現実整合 | `python scripts/reality_score.py runs/<run>` + `python scripts/calibrate_report.py runs/<run>` | 成分表示の検証表(総合1点にしない)+ 30指標の健診 |
| 世界整合 | `python scripts/audit_world_invariants.py runs/<run>` | 22 検査の VIOLATION 一覧 |

## 4.4 「確定判定に使うラン」の宣言(★未確定=承認時に決める)

- 既存 §4 適用スケジュールは **②「GPU 開放初日の実 LLM 診断ラン(数百体 × 20 sim日相当)= これが確定判定に使うラン」** としているが、**本選日程にこの診断ランが計上されていない**(§3-④)。
- **選択肢**: (a) 8/17-18 の階段の隙間で数百体×20日相当を1本走らせる(GPU 時間を消費)/ (b) **本番10日ランそのものに同じ CLI を事後適用**し、「確定判定は本番ラン由来」と宣言を書き換える(★ burn-in ≈ 18日なので 10日では late_same_lag が過渡の中に入る=`NONSTATIONARY_UNVERIFIED` が出やすい)/ (c) 診断は mock 事前測定(既済)止まりとし、H5 を「参考」へ降格する。
- **⬜判断待ち**(承認時に (a)/(b)/(c) を選ぶ)。**どれを選んでも「選んだ」と書く**。

## 4.5 停止・介入規則(ラン中に何をしてよいか)

**原則: 観察ランでは世界に触れない。** 触れた瞬間、そのランは「条件を変えたラン」になる。

| 事象 | 規則 | 装置 |
|---|---|---|
| 進捗停止 | **max(`--stall-min` 20分, 1step 実測秒 × 6)** を超えたら watchdog が kill → **自動 resume**(必ず待つ側へ倒れる設計) | `scripts/watchdog.py`(F1) |
| checkpoint 破損 | watchdog が**1世代 rollback**(本体と COMPLETE マーカーを対で `corrupt/` へ隔離)→ resume | `_rollback_one_generation` |
| ディスク | warn 50GB で警告(**止めない**)/ crit 20GB で「最後の一声」。**checkpoint / dormant は最後まで消さない**(E0) | watchdog + F3 |
| vLLM 落ち | 計画再起動 drill 済みの手順で再起動 → シム側は再接続。**再起動は条件変更ではない**(呼の内容も乱数も変えない) | 信頼性リハ #7 |
| RAM 逼迫 | A3 の線で **NO-GO 帯なら起動しない**。走行中に逼迫した場合の縮退は**ユーザー判断**(present_cap を下げるのはラン継続ではなく**別ラン**) | A3 |
| 結果が「つまらない」 | **介入しない**。反復・定常も**測定された事実**として報告する(§5「反復した場合の報告条項」)。上界の測定であって LLM 社会一般の上界ではない、と書く | 事前登録 §5 |
| どうしても条件を変えるとき | **変えた事実・日付・理由を §7 変更履歴へ記録し、変更前後の判定を両方報告**。黙って変えない | 事前登録 §7 |
| fire を開けた場合 | fire ON は**条件の変更**なので、**閾値表へ反映してから**走る(D1-c #8) | 本書 B8b |

## 4.6 尾部(8/26-30)の配分案(⬜承認待ち)

**優先順(等分しない)**:

1. **seed 2本目(短縮版でも可)= 最優先**。理由: 事前登録 G3 は条件内 seed **3本**を要求するが、現状は**入力ランがゼロ**。`analyze_seed_variance.py` は実装済みで入力待ち。**seed 2本目が無いと H1 の量的主張がほぼ全部「1標本」に落ちる**。同構成 seed 違いにすれば「現実再現ランの追加」も兼ねられる(ユーザー提案 D2-d と両立)。
2. **介入 fork 1本**(checkpoint 分岐・交通障害 or 空間介入)。分岐点は **G2(剪定禁止)で保全済み**なので後日でも可能だが、尾部で1本取れるなら反実仮想の入口が開く。
3. **shadow 高認知ラン**(代表 5k・ほぼ全決定点 LLM)。低 LOD との行動一致率 = 「**呼数はいくらで足りるか**」の実証。階段の隙間(8/20-21)に入れられれば尾部を使わない。

**正直な注記**: 3本とも取れる保証は無い。**seed 2本目が取れなかった場合は、H1 の量的主張を落として「1標本の記述」と明記する**(取れなかったことを取れなかったと書く)。

## 4.7 事前に宣言する「出さない結論」

- G3(seed 3本)未達の指標 → `INSUFFICIENT_SEEDS`。**有意でも主張しない**。
- F10 / F11(企業規模 Zipf・Gibrat)→ **検定不能と書く**(N が 4-5桁足りない)。
- S4 到達 → 「合意への言及が発話中に現れた」までしか言わない(**内面化とは言わない**)。
- 分散比 → **片側バンド**。下回れば「痩せている」と言えるが、上回っても「十分」とは言えない。
- `ablate.cognitive_tier` → **片側検査**。変わらなければ「一様予算が結論を作っていない」と言えるが、変わっても「だから厚くすべきだ」とは言えない。
- **出さないことにした結論の一覧は報告書 §7.1 に列挙する**(出さなかったことも報告の一部)。

---

## 5. 出典一覧(本書の各行が引いた文書)

| 略記 | パス |
|---|---|
| dashboard | [docs/plans/decision-dashboard.md](decision-dashboard.md) |
| triage | [docs/plans/external-audit-triage.md](external-audit-triage.md) |
| endgame | [docs/plans/finals-endgame-plan.md](finals-endgame-plan.md) |
| beta | [docs/plans/beta-implementation-plan.md](beta-implementation-plan.md) |
| checklist | [ops/finals-compute-checklist.md](../../ops/finals-compute-checklist.md)(E0 剪定禁止 / E1 最適化 / E2 Discord / E3 watchdog 本選値) |
| runbook | [ops/runbook-first-night.md](../../ops/runbook-first-night.md) |
| handoff | [docs/plans/source/CLAUDE_CODE_HANDOFF_SHIBUYA_SIM_2026-08-16.md](source/CLAUDE_CODE_HANDOFF_SHIBUYA_SIM_2026-08-16.md)(§10 golden / §14 present_cap 罠 / §27 検証手順 / §29 やってはいけないこと / §30 ulimit) |
| 事前登録 | [docs/plans/stationarity-preregistration.md](stationarity-preregistration.md) |
| 信頼性 | [docs/plans/finals-reliability-plan.md](finals-reliability-plan.md) |
| 報告テンプレ | [docs/plans/observation-report-template.md](observation-report-template.md) |
| ユニークデータ | [docs/research/unique-data-candidates.md](../research/unique-data-candidates.md) |
