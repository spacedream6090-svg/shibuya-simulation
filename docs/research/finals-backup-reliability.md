# 本選バックアップ・信頼性設計の材料集(リサーチ)

- 作成: 2026-08-12(フリーズ期間・実装なし=材料の提示のみ)
- 目的: 本選(8/15〜8/30・10日ラン 8/16〜8/26)で**シミュレーション結果を確実に持ち帰る**ためのバックアップ・信頼性設計の判断材料を、(a) リポの実物確認と (b) Web 文献・実務前例の両面から揃える。
- 前提: 本選環境はデータセンターの GPU 機 1 台(A5000 級 24GB×7・単一ノード)。ローカル PC(Windows)は別。**ネットワーク帯域・外部ストレージの有無は未確認**(ユーザー確認中=本文書では複数シナリオで併記)。
- 本文書は判断材料であり決定ではない([ask-before-extending] に従い、実装・conf 変更・スケジュール登録はすべてユーザー承認後)。

---

## §1 守るべき資産の棚卸し(リポ実物確認)

### 1.1 runs/<run_id>/ の実物構成

実ラン(`runs/_sigma_pilot`・`runs/_w2_4_smoke`・`runs/eco80_3day` 等)と src の読解で確認した現物:

| ファイル/ディレクトリ | 生成機構 | 中身 |
|---|---|---|
| `l1_events.part-NNNN.parquet` 群 | `observer/logger.py` flush_segment(zstd 圧縮で書き出し) | **一次データの本体**。全イベント |
| `l1_events.parquet`(canonical) | `observer/finalize.py`(ラン完了時に part 群+残バッファを結合) | part 群から**再生成可能** |
| `l1b_llm.part-*.parquet` / `l1b_llm.parquet` | 同上 | LLM 呼び出し記録(呼数・cached・purpose) |
| `l2_metrics` / `l3_snapshots`(part+canonical) | 同上 | 集計系列・スナップショット |
| サイドカー(`channels` / `org_ledger` / `finance` / `cognition_g` / `indoor_tracks`) | 各サイドカー(finalize は `FinalizeStreamMixin` に一本化済み) | ON のもののみ |
| `llm_journal.jsonl.gz`(+`.index.json`) | LLM 入出力ジャーナル(第71)。gzip メンバ境界=安全な切り詰め点。checkpoint に確定点(records/bytes)を同梱し resume 時に巻き戻す | **実 LLM 応答の一次記録** |
| `llm_cache.jsonl` | 応答キャッシュ(同一呼のバイト再生=再現性の実体) | 一次データ |
| `checkpoint/ckpt-NNNNNN.pkl.gz` | `engine/checkpoint.py` save(pickle+gzip・**tmp 書き→os.replace の原子的 rename**) | 完全状態。resume の起点 |
| `run_manifest.json` | `observer/manifest.py`(git SHA・config ハッシュ・seed・モデル ID・全スイッチ・開始時刻。履歴 20 世代) | ランの来歴。書くだけ・シムは読まない |
| `config.yaml` / `summary.json` / `agents.json` / `traits.json` | run.py(config は checkpoint_every>0 なら**先出し保存**) | 設定正本・最終集計・名簿 |
| `analysis/` `panel/` `*.html` | 解析・可視化スクリプト | **再生成可能**(派生) |

### 1.2 再生成可能性による分類(何が失われると致命的か)

| 級 | 資産 | 再生成可能性 | 失った場合 |
|---|---|---|---|
| **S(致命)** | L1/L1b/L2/L3 の part 群・LLM ジャーナル・llm_cache・summary.json・run_manifest.json・config.yaml | **不可能**。観察ランは repro_tier=journal/none 可(PENDING §5.1)+ temperature>0 の実 LLM 初回生成は再現不能。**10 日ランは 8/16-8/26 の 1 回しか回せない**(時間枠そのものが資産) | 本選の研究成果が消える |
| **A(重大)** | checkpoint 群(最新+1 世代前) | 不可能(ただし用途は resume のみ。完走後は価値が下がる) | 障害時に day0 からやり直し=日程的に全損と同義 |
| **B(再生成可・高コスト)** | canonical parquet・ペルソナプール 100 万(build_persona_pool は seed 決定論)・台帳 9,872 社 | part 群/スクリプトから再生成可能(プールのリビルドは時間コスト大) | 時間を失う |
| **C(再生成可・低コスト)** | viewer/dashboard/panel/analysis・heatmap 等 | スクリプト一発 | ほぼ無害 |
| **環境資産** | コード(git・ローカル+リモート)・conf・data/env スナップショット | git 管理+ローカル日次バックアップ(ops/backup-daily.ps1)済み | 既に多重 |

★ポイント: **本選機のディスク上にしか存在しない時間帯を最小化すべき対象は S 級と A 級**。B/C 級は転送優先度を落としてよい(帯域が細い場合の順位付けに効く)。

### 1.3 書き込み中の安全性(クラッシュ時に何が壊れうるか・実物調査)

| 書き込み | 原子性 | 根拠(実物) |
|---|---|---|
| checkpoint 保存 | **原子的**(`.tmp` に書いて `os.replace`) | `src/society/engine/checkpoint.py` save() |
| streaming finalize(canonical) | **原子的**(`<stem>.parquet.tmp`→`os.replace`。落ちても part と旧 canonical が残る) | `src/society/observer/finalize.py` docstring(既定 OFF の concat 経路は canonical 直接上書き=**本選は streaming ON なので安全側**) |
| LLM ジャーナル | 確定点方式(checkpoint に records/bytes を同梱・resume で gzip メンバ境界まで巻き戻し=二重記録と seq 巻き戻りを防止) | `simulation.py` L1302-1306・checkpoint.py "llm_journal" |
| **part flush** | **非原子的**(`pq.write_table` が最終名へ直接書く。tmp+rename なし) | `src/society/observer/logger.py` flush_segment() |

★発見(バックアップ設計に効く): **part flush 中にクラッシュすると、最終名で footer 不完全な不正 parquet が残りうる**。resume 整合はエンジン側で保たれる(「checkpoint が真の境界」流儀・part 採番は `_next_seg` が既存最大+1 で衝突回避)が、**バックアップ側は「書き込み中の末尾 part」をコピーしてしまう可能性**がある。対策素材:
1. スナップショット取得は **checkpoint 直後**(flush と対で走る)に行うか、「更新時刻が数分以上古い part のみ」を対象にする(parquet は footer を閉じて初めて有効=書きかけ検知は footer 検証で可能。→§3-2)。
2. 転送後に pyarrow で **footer 読み(メタデータだけ)検証**を restore drill に含める。`scripts/detect_regression.py --quick` が「完結 part のみ読む」実装済みで同じ思想。

### 1.4 サイズ見積とディスク予算(実測+外挿)

リポ内の実測外挿(`docs/plans/proposal-dp-u3-observe-250k.md` §2.3-2.4・PENDING §4):

| 項目 | 見積 | 備考 |
|---|---|---|
| L1(在場 25 万×10 日) | **42.7 GB・40.6 億イベント(線形下界)** | イベント数は N に超線形(135→618→1,622 /体/日)=**上振れ余地大** |
| L1 concat ピーク(streaming OFF) | **約 124 GB** | 本選 conf は `observer.finalize.streaming: true` で回避済み |
| indoor_tracks ON | +19 GB | 本選は indoor 系 OFF |
| L3 | 60 MB/日(25 万×250B・snapshot_every=144) | 10 日で 0.6 GB |
| ホスト RSS | 88.4〜110.3 GB(24step ランからの下界) | 8/15-16 に実測予定 |
| checkpoint 1 個(25 万体) | **未実測**。手元小規模実測: 200 体で 0.45→0.88 MB(step144→432・**時間とともに成長**)= 2〜4.4 KB/体 → 単純外挿 0.5〜1.1 GB/個は**下界**。`docs/research/scale-audit-100days.md` §2.5 は「run 後半で数百 MB〜GB 級」 | conf 注記も「★25万体の完全状態 pickle=ディスクを先に確認すること」 |
| LLM ジャーナル | 呼数依存(10 日想定 7.38×10⁶ 呼)。数 GB 級の想定・未実測 | gzip 済み |

★発見(ディスク予算): `checkpoint/` は**世代を削除しない**(`checkpoint.latest` が最大 step を選ぶだけ・pruning 実装なし)。checkpoint_every=72 なら 10 日で **20 個**蓄積= 1 個 1〜数 GB でも 20〜100 GB 級。さらに `scripts/watchdog.py` の世代バックアップ(checkpoint+config+l1 parts を直近 3 世代コピー)は**その時点までの全 part を含む**ため、終盤は 3×(L1 総量+checkpoint)級になりうる。**合計ディスク= L1 系 50-100GB + checkpoint 蓄積 20-100GB + watchdog バックアップ 3 世代**を予算に入れ、8/15-16 に実測値で引き直すこと(古い checkpoint の間引き=ops 側スクリプトで可能・src 変更不要)。

### 1.5 既存の運用資産(再利用できるもの)

| 資産 | 何をするか | 本選への転用 |
|---|---|---|
| `scripts/watchdog.py` | run.py を子プロセス監督: プロセス死→最新 checkpoint から自動 resume・ストール検知(既定 20 分)→kill して再開・リトライ上限 10・指数バックオフ・**破損 checkpoint は 1 世代前へ巻き戻し**・世代バックアップ(直近 3)・llm_fallback_rate 監視(警告のみ)・status.json/watchdog.log | **そのまま主軸**。ストール分は checkpoint/part の進捗で見る=ハング検知も兼ねる |
| `scripts/watchdog_llm.py` | 事後点検(呼数・cache 率・fallback 率・deadline 超過=「1 件でも出たら異常」) | restore drill の検証コマンドに最適(シム本体を import しない=バックアップコピーに直接掛けられる) |
| `scripts/detect_regression.py --quick` | 完結 part のみ読む軽量退行検査 | ラン中の日次健全性チェック |
| `ops/backup-daily.ps1` + タスクスケジューラ | ローカル PC: robocopy /MIR 増分ミラー+14 日分 code zip+1 行ログ | **ローカル側の受け皿の前例**。runs 用に対象を足す形が素直 |
| `scripts/rw_fetch_daily.py` + タスクスケジューラ(shibuya-rw-fetch-daily・毎日 12:00) | アメダス日次取得 | 「日次無人実行」の運用前例 2 件目 |
| `ops/launch-vllm-finals.ps1` / `ops/finals-compute-checklist.md` | vLLM 7 本起動・実測チェックリスト | 本選機セットアップ手順の正本 |
| `ops/publish_public_mirror.ps1` | 公開ミラー同期 | 転用なし(コード側の冗長化は既に十分) |
| resume 整合の実装史(第 98/101/108) | 日/期ガード全数監査・spark 二重記録・flush 欠陥・journal 巻き戻しまで解消済み。既知の残り= `undefined_action_total/rate` は resume 後 0 から数え直し(PENDING §4 明記) | **resume は「使ってよい」水準**。ただし観察ランの resume は続行性が目的(verify の strict とは別物) |

---

## §2 障害モード×対策表

発生率の根拠: Meta の Llama 3 405B 事前学習(16,384 GPU・54 日)は**予期せぬ中断 419 回=約 3 時間に 1 回**、うち **GPU/HBM3 起因が約 58%**・ネットワーク 8.4%・CPU はわずか 2 回([Tom's Hardware](https://www.tomshardware.com/tech-industry/artificial-intelligence/faulty-nvidia-h100-gpus-and-hbm3-memory-caused-half-of-the-failures-during-llama-3-training-one-failure-every-three-hours-for-metas-16384-gpu-training-cluster)・[DCD](https://www.datacenterdynamics.com/en/news/meta-report-details-hundreds-of-gpu-and-hbm3-related-interruptions-to-llama-3-training-run/))。7 GPU なら中断率は 3 桁下がるが、**10 日間で「1 回も落ちない」を前提にしてはならない**(504 GPU 規模の運用報告でも中断は常態: [Lablup 技術報告](https://arxiv.org/html/2605.09370))。

| 障害モード | 検知 | 一次対策(リポ既存) | 二次対策(追加素材) |
|---|---|---|---|
| **電源断/ノード再起動** | SSH 不通・watchdog 停止 | checkpoint(原子的保存)+ watchdog `--resume` | watchdog 自体を tmux/systemd 配下に(§3-3)。**再起動後に watchdog が自動で立ち上がる**手段(systemd unit / cron @reboot)を用意。損失最大= checkpoint 間隔+再走分(§4) |
| **ネットワーク断(ユーザー→DC)** | SSH 切断 | — | **ラン本体は tmux/screen 内で起動**すれば切断と無関係に続行(§3-3)。転送は rsync/rclone のリトライで再開(部分転送再開対応) |
| **ディスクフル** | 書き込み例外でランが落ちる(最悪=**静かに壊れる**。GitLab 事故はバックアップジョブがディスクフルで数ヶ月沈黙) | conf 注記「ディスクを先に確認」(手動) | **残量ガード**: 日次で `df` 閾値(例: 見積残り日数×日次増分×2)を監視・警告。checkpoint 世代の間引き(§1.4)。転送済み世代バックアップの削除 |
| **GPU 障害(1 枚死亡)** | vLLM サーバのエラー/応答停止 | FleetLLM は複数サーバ構成対応(URL 差し替え)・LLM 呼失敗はフォールバック段階あり=ランは止まらない設計 | 6 枚構成の起動コマンドを事前に用意(launch スクリプトの引数変更のみ)。`nvidia-smi` の XID エラー監視。**ラン再開不要**(シム側は checkpoint 起点で resume すれば整合) |
| **vLLM ハング/リーク** | tok/s 低下・応答タイムアウト・ホスト/GPU メモリ漸増 | 呼単位の絶対時限 `model.call_deadline_s`(1 呼 1h47m 張り付き事故から導入済み)・watchdog のストール検知 | vLLM は長時間運用でリーク実績あり(§3-3)。**「日次で計画的に vLLM を再起動」**が実務の定石(checkpoint 直後の休止点で)。`gpu_memory_utilization` を 0.85 以下に。Prometheus /metrics の常時記録 |
| **シムプロセスハング** | checkpoint/part が進まない | watchdog `--stall-min`(20 分)→ kill→resume | stall-min は 25 万体の 1 step 実時間(~10 分想定)より十分大きく設定し直す(誤 kill 防止) |
| **ホスト OOM** | カーネル OOM killer(exit 137) | flush_every_steps=6・streaming finalize・regression OFF 等の有界化済み(第 99/101) | `dmesg`/`journalctl -k` で OOM 痕跡確認を復旧手順に含める(§3-3)。RSS 実測(8/15-16)で在場 N を最終決定するのが根本対策 |
| **ソフトバグ(L1 破損・finalize 失敗)** | footer 検証・detect_regression --quick・watchdog_llm | part 群が真の一次データ= canonical 破損は再結合で復旧可能。streaming finalize は失敗しても part と旧 canonical が残る | 日次で「前日 part の footer 検証+行数記録」。**バックアップは part 群を最優先**(canonical は派生) |
| **checkpoint 破損** | resume 時の例外・config_hash 不整合 | watchdog が同一 checkpoint 2 回失敗で 1 世代前へ自動巻き戻し | 世代を 2 つ以上残す運用の維持(間引き時も最新 2-3 個+日次 1 個は残す) |
| **人為ミス(誤削除・誤上書き)** | — | run_manifest による取り違え防止・checkpoint config_hash ガード | **同期は `rclone copy`(削除を伝播しない)を基本**にし `sync`/`robocopy /MIR` は runs には使わない(§3-2)。クラウド側バージョニング/オブジェクトロック。rm 前に必ず `ls` 確認(GitLab 事故=本番/レプリカの取り違え) |
| **(クラウド退避時)プリエンプト** | — | `docs/research/server-deployment.md` §2.1 が watchdog+checkpoint 具備を明記済み | 本選機が使えなくなった場合の避難先として §5 のクラウド GPU+キャッシュ移設(URL 非依存)が保険 |

---

## §3 文献・実務発見(URL 付き)

### 3-1 チェックポイント間隔の理論(課題 1)

- **Young の一次近似**(1974): 最適間隔 T_opt ≈ √(2·C·μ)(C=checkpoint 保存コスト・μ=MTBF)。**Daly(2006)が高次近似へ拡張**: [A higher order estimate of the optimum checkpoint interval for restart dumps(ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S0167739X04002213)・[PDF](https://graal.ens-lyon.fr/~abenoit/CR02/papers/daly.pdf)。
- **Young/Daly 総説**(Benoit ら 2022): W_YD=√(2μC) の導出と適用条件の整理。[Checkpointing à la Young/Daly: An Overview](https://icl.utk.edu/files/publications/2022/icl-utk-1569-2022.pdf)([ACM 版](https://dl.acm.org/doi/pdf/10.1145/3549206.3549328))。
- 適用条件の注意: 公式は「任意時点で checkpoint できる」仕込み前提。**反復境界(=本シムの step/日境界)でしか checkpoint できない場合は最寄りの境界に丸める**のが実務([Checkpointing Workflows à la Young/Daly Is Not Good Enough](https://dl.acm.org/doi/full/10.1145/3548607)・[確率的反復アプリでの頑健性(丸めに対して頑健)](https://people.bordeaux.inria.fr/gaupy/ressources/pub/confs/icpp20_robustness.pdf))。
- サーベイ: [A survey on checkpointing strategies: Should we always checkpoint à la Young/Daly?](https://www.sciencedirect.com/science/article/abs/pii/S0167739X24003777)。
- ML クラスタの信頼性実測(Meta 研究クラスタ): [Revisiting Reliability in Large-Scale ML Research Clusters](https://arxiv.org/pdf/2410.21680) — ジョブ規模と MTBF の実データ。単一ノードの MTBF は日〜週のオーダー。

### 3-2 バックアップの原則(課題 2)

- **3-2-1 ルール**(3 コピー・2 種メディア・1 オフサイト): [Backblaze](https://www.backblaze.com/blog/the-3-2-1-backup-strategy/)・[CISA](https://www.cisa.gov/audiences/small-and-medium-businesses/secure-your-business/back-up-business-data)。発展形 3-2-1-1-0(不変コピー 1+**復元検証エラー 0**): [Backblaze 比較記事](https://www.backblaze.com/blog/whats-the-diff-3-2-1-vs-3-2-1-1-0-vs-4-3-2/)。
- **append-only データの増分同期**: part 群は「追記のみ・不変ファイルの増加」なので増分同期に理想的。rsync は差分転送+cron 日次が定石([Tecmint](https://www.tecmint.com/linux-rsync-incremental-backup-cron/)・[ArchWiki](https://wiki.archlinux.org/title/Rsync))。rclone は「クラウド版 rsync」でアップロード時にチェックサム検証・`rclone check` で事後照合([docs](https://rclone.org/docs/)・[B2 backend は SHA1 を格納](https://rclone.org/b2/))。Windows 側は robocopy(/Z 再開可能・/R:n /W:n リトライ・/LOG。**/MIR は削除も同期=誤削除伝播のリスク**があり dry-run(/L)必須: [PDQ ガイド](https://www.pdq.com/blog/hitchhikers-guide-to-robocopy/)・[Petri](https://petri.com/robocopy-complete-guide/))。→ **runs の同期は「削除を伝播しないコピー」(rclone copy / robocopy without /MIR)が原則**。
- **書き込み中ファイルの扱い・atomic rename**: 「tmp に書く→fsync→rename→(厳密には)ディレクトリ fsync」が定石パターン([danluu: Files are hard](https://danluu.com/file-consistency/)・[LWN: A way to do atomic writes](https://lwn.net/Articles/789600/)・[解説](https://0xkiire.com/crash-consistency-fsync-rename/))。本リポは checkpoint と streaming finalize が既にこの型(§1.3)。**parquet は footer をファイル末尾に書いて閉じる形式なので、書きかけ=footer 不在で機械検出できる**(破損事例と検証実務: [Gluten issue #9801](https://github.com/apache/incubator-gluten/issues/9801)・[ARROW-2369](https://issues.apache.org/jira/browse/ARROW-2369))。
- **チェックサムマニフェスト**: デジタル保存分野の標準 **BagIt(RFC 8493)** が「manifest-sha256.txt に `ハッシュ 相対パス` を列挙し、転送検証と定期 fixity check に使う」形式を規定: [RFC 8493](https://datatracker.ietf.org/doc/html/rfc8493)。完全準拠は不要でも、**「日次で確定 part の sha256 を取り、転送先で照合」**という運用の型として借りられる(sha256sum / `Get-FileHash` / `rclone check` いずれでも照合可)。
- **backup 失敗の実例**: GitLab 2017-01-31 事故 — 誤った rm によるデータ消失に対し**5 系統のバックアップが全て機能せず**(S3 空・スナップショット破損・ジョブがディスクフルで沈黙・通知メール不達)、たまたま 6 時間前の手動スナップショットで復旧: [公式ポストモーテム](https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/)・[当時の速報](https://about.gitlab.com/blog/gitlab-dot-com-database-incident)。教訓=「**バックアップの成功ログではなく、復元の成功だけが証拠**」(§6 の restore drill の根拠)。

### 3-3 長時間ラン運用(課題 3)

- **切断耐性**: SSH 切断時に SIGHUP で子プロセスが死ぬのが既定。tmux/screen(再接続可能)・nohup・systemd unit の使い分け: [Tecmint 総説](https://www.tecmint.com/keep-remote-ssh-sessions-running-after-disconnection/)。実務は「**watchdog を tmux セッション内で起動**」が最小構成(接続が切れても監督ループが生き続ける)。systemd が使えるなら `Restart=on-failure` で watchdog 自体の再起動+ブート時自動起動まで賄える。
- **OOM 検知**: OOM killer の犠牲プロセスは `dmesg -T` / `journalctl -k` に記録される([Baeldung](https://www.baeldung.com/linux/which-process-killed))。予防側は [earlyoom](https://github.com/rfjakob/earlyoom)(available メモリ 10% 閾値で大食いを先制 kill=**ホスト巻き添えフリーズの回避**)。
- **vLLM の長時間安定性**: 長時間サービングでのメモリリーク/性能劣化(software aging)は既知の実務課題。Mistral のデバッグ記: [Heaps do lie: debugging a memory leak in vLLM](https://mistral.ai/news/debugging-memory-leak-in-vllm/)。GPU LLM サービングの aging 特性の研究: [Characterizing Software Aging in GPU-Based LLM Serving Systems](https://arxiv.org/pdf/2606.11916)。カーネル起因の 12-48h でのリーク事例と対処(THP=madvise・`gpu_memory_utilization` 0.80-0.85): [事例記事](https://ai.islinux.com/articles/fixing-vllm-memory-leaks-kernel-tuning.html)。→ **「リークを直す」より「checkpoint 休止点で日次再起動する」方が本選 10 日には確実**(シム側は LLM サーバ再起動と独立に continue できる設計=クライアントのリトライで吸収)。
- ディスク残量ガード: 専用ツール不要。日次点検スクリプトに `df` 閾値+「残り日数×日次増分」比較を 1 行入れるのが最小(§2 ディスクフル行)。

### 3-4 障害モードの前例(課題 4)

- GPU/HBM 故障が支配的・一晩に 1 回級の中断が常態(大規模時): §2 冒頭の Llama 3 実測。
- 単一ノード 7 GPU 級では「電源・ディスクフル・ソフトバグ・人為ミス」が相対的に主役になる(GitLab 事故=人為ミス+バックアップ未検証の複合。§3-2)。
- 検知→復旧の運用分析: [From Detection to Recovery: Operational Analysis on LLM Pre-training with 504 GPUs](https://arxiv.org/html/2605.09370)。

### 3-5 転送の実務(課題 5)

- rclone の実務: SHA1/SHA256 をアップロード時に検証・5GB 超は自動マルチパート・`--transfers/--checkers` を不安定回線では保守的に・事後 `rclone check`([docs](https://rclone.org/docs/)・[B2](https://rclone.org/b2/))。sftp バックエンドがあるので**クラウドを介さず DC→ローカル PC 直の pull にも同じツールが使える**(Windows 側 rclone.exe 1 バイナリ・チェックサム照合込み)。
- zstd: レベル 1-5 が速度優先(silesia で L1=2.88x@470MB/s・L3=3.17x@300MB/s)・L19+ はアーカイブ用: [facebook/zstd](https://github.com/facebook/zstd)・[ベンチ](https://openbenchmarking.org/test/pts/compress-zstd)。★ただし**本リポの part は既に zstd 圧縮済み parquet・checkpoint は gzip 済み・ジャーナルも gzip 済み**(§1.1 実物確認)= 再圧縮の利得はほぼ無い。転送最適化は圧縮ではなく「**小ファイル多数を tar でまとめる**」(転送セッション数削減)と分割再開(rsync --partial / rclone 自動)が効く。
- ストレージ価格(2026 時点の公表値): B2 $6.95/TB/月+egress は保存量の 3 倍まで無料([Backblaze pricing](https://www.backblaze.com/cloud-storage/pricing))・Cloudflare R2 $0.015/GB/月+**egress 無料**・S3 Standard $0.023/GB/月+egress $0.09/GB([比較](https://mecanik.dev/en/posts/cloudflare-r2-pricing-explained-real-costs-vs-s3-and-backblaze/))。150 GB×1 ヶ月の概算: **B2 ≈ $1・R2 ≈ $2.3・S3 ≈ $3.5+取り出し $13.5**。rclone は全対応。Google Drive も rclone 対応(既存プランがあれば追加費用ゼロの選択肢)。

### 3-6 リハーサル(課題 6)

- **Schrödinger's backup**(検証されていないバックアップは存在しないのと同じ): [用語解説](https://www.ministryoftesting.com/software-testing-glossary/schrodinger-s-back-up)。GitLab 事故が実証例(§3-2)。
- **障害注入で DR 手順を事前検証する**(chaos engineering の DR 適用): [Gremlin: Testing disaster recovery with Chaos Engineering](https://www.gremlin.com/community/tutorials/testing-disaster-recovery-with-chaos-engineering)。
- 3-2-1-1-0 の「0」= 復元テストでエラー 0 を定期確認(§3-2 Backblaze)。

---

## §4 チェックポイント/バックアップ間隔の計算材料(Young/Daly×本シム実測値)

### 4.1 公式と本シムの変数

- **T_opt = √(2·C·μ)**(C=checkpoint 保存の実時間・μ=MTBF)。最適時の総オーバーヘッド率 ≈ √(2C/μ)。
- 現行 conf(`conf/finals_observe.yaml`): `checkpoint_every: 72`(=半シミュ日)・`flush_every_steps: 6`(=1 シミュ時間ごと part flush)。
- 壁時間換算: 10 日ラン=1,440 step を約 240h で回す想定 → **1 step ≈ 10 分 → checkpoint_every=72 ≈ 実時間 12h 間隔**。
- **C は未実測**(25 万体の完全状態 pickle+gzip。保存は run ループ内の同期実行=C はそのまま総時間に乗る)。μ も未実測(単一ノードの実績値がない)。→ **どちらも 8/15-16 の診断ランで測る**(§6-4)。

### 4.2 シナリオ表(T_opt と step 換算・1 step=10 分)

| C \ μ | 12h | 24h | 48h | 72h |
|---|---|---|---|---|
| **5 分** | 1.4h(≈8 step) | 2.0h(≈12) | 2.8h(≈17) | 3.5h(≈21) |
| **15 分** | 2.4h(≈15) | 3.5h(≈21) | 4.9h(≈29) | 6.0h(≈36) |
| **30 分** | 3.5h(≈21) | 4.9h(≈29) | 6.9h(≈41) | 8.5h(≈51) |
| **60 分** | 4.9h(≈29) | 6.9h(≈41) | 9.8h(≈59) | 12h(≈72) |

読み方:
1. **現行 72 step(実時間 12h)は「C=60 分かつ μ=72h」でようやく最適**になる長さ。C が 15 分・μ が 24-48h なら最適は **21〜29 step(3.5-5h)**で、現行は「攻めすぎ」(=落ちたとき最大 12h+再走を失う)。
2. 逆に C が本当に 60 分級(数十 GB の pickle+gzip は 1 コア直列で遅い)なら、間隔を詰めるほど総時間を食う。**Young/Daly は「C を測らずに間隔を語れない」ことを教える公式**である。
3. 丸めの実務: checkpoint は step 境界でしか打てないが、Young/Daly は境界への丸めに頑健(§3-1 ICPP20)。**flush_every_steps=6 と snapshot_every=144 との整合(倍数関係)だけ守って最寄りに丸める**。
4. 損失の非対称性: 観察ラン 10 日は締切固定なので、「失う時間の上限=間隔+resume 再走」が **8/26 の締切を突き破らないか**という制約が Young/Daly の期待値最適より優先される。終盤(残り 2-3 日)は間隔を敢えて短くする「締切前は保守側」運用も材料に。

### 4.3 バックアップ間隔への適用

- part 群は checkpoint 境界で確定する(§1.3)ので、**バックアップ間隔の自然な単位も「checkpoint 何回ぶんか」**。日次(=checkpoint 2 回ごと)が §5 の帯域試算と噛み合う基本線。
- 「失ってよい量」から逆算: 日次転送なら**最悪 24h ぶんの part+ローカル世代バックアップ**が失われる(DC 機の全損時)。これを許容できないなら半日次へ。転送コストは増分のみなので間隔を半分にしてもコストは倍にならない(同量を 2 回に分けるだけ)。

---

## §5 転送・保管の選択肢比較

### 5.1 日次増分の量(見積)

- L1 系 42.7GB/10 日(下界)+ ジャーナル/サイドカー → **日次増分 ≈ 5〜15 GB(上振れ込み)**。
- 最終日の全量(canonical 化後)= **50〜150 GB 級**(checkpoint を含めるかで大きく変わる。S 級のみなら 50-100 GB)。

### 5.2 帯域→時間の換算表(理論値。実効は 6〜8 割)

| データ量 | 50 Mbps | 100 Mbps | 500 Mbps | 1 Gbps |
|---|---|---|---|---|
| 10 GB(日次) | 27 分 | 13 分 | 2.7 分 | 1.3 分 |
| 50 GB | 2.2h | 1.1h | 13 分 | 6.7 分 |
| 100 GB | 4.4h | 2.2h | 27 分 | 13 分 |
| 150 GB(全量) | 6.7h | 3.3h | 40 分 | 20 分 |

→ **100 Mbps さえあれば日次 10-15 GB は 30 分未満**で送れる=日次退避は帯域的に現実的。全量 150 GB も一晩で送れる。50 Mbps を下回る場合のみ、S 級優先の選別転送(§1.2)が必要になる。★実帯域は 8/15 のセットアップ時に実測(§6-5)。

### 5.3 宛先の比較

| 宛先 | ツール | コスト | 長所 | 短所 |
|---|---|---|---|---|
| **DC 機内の別ディスク/パス** | watchdog 世代バックアップ(既存)+ cp | 0 | 最速・既に動く | 筐体全損に無力(3-2-1 の「1 オフサイト」にならない) |
| **ローカル PC(Windows)** | rclone(sftp)pull または rsync→(WSL) | 0 | 既存資産(backup-daily.ps1 の受け皿・ローカル解析にそのまま使える) | ローカルディスク残量(要事前確認)・帯域依存 |
| **Backblaze B2** | rclone copy | $6.95/TB/月・egress 3 倍まで無料 | 最安・SHA1 検証内蔵・バージョニング可 | アカウント新規作成の手間 |
| **Cloudflare R2** | rclone copy | $0.015/GB/月・egress 無料 | 取り出し無料=何度でも引き直せる | 同上 |
| **AWS S3** | rclone copy | $0.023/GB/月+egress $0.09/GB | 実績・オブジェクトロック | 取り出しが高い(150GB≈$13.5) |
| **Google Drive** | rclone copy | 既存プラン内なら 0 | 追加契約不要の可能性 | API レート制限・大量小ファイルに弱い(tar 化で緩和) |

### 5.4 推奨構成の素材(3-2-1 への当てはめ)

1. **コピー 1(一次)**: DC 機の runs/(watchdog 世代バックアップ込み)。
2. **コピー 2(別メディア)**: ローカル PC へ日次 pull(rclone sftp・チェックサム照合・**削除を伝播しない copy**)。ローカル側は既存 backup-daily.ps1 のミラー対象に入り二重化される。
3. **コピー 3(オフサイト)**: クラウド 1 つ(B2 か R2)へ DC 機から日次 push。10 日+α で数ドル。
- 完全性: 日次で確定 part の **manifest-sha256.txt**(BagIt 式)を DC 側で生成→ 3 箇所すべてで照合。マニフェスト自体も S 級としてコピー。
- 帯域が判明するまでの縮退案: 帯域が細い場合はコピー 3 を「S 級のみ」に絞る(§1.2 の優先順位)。

---

## §6 リハーサル項目の素材(8/15-16 診断ラン・それ以前のローカルで)

| # | drill | 何を確認するか | 合格条件の素材 |
|---|---|---|---|
| 1 | **resume drill** | 診断ラン中に kill -9 → watchdog が最新 checkpoint から自動再開するか。checkpoint 破損を注入(先頭バイト破壊)→ 1 世代前への自動巻き戻し | 再開後に step が進む・L1 part 採番が衝突しない・watchdog.log に想定どおりの記録 |
| 2 | **restore drill(最重要)** | バックアップコピー(ローカル PC 側)**だけ**を入力に、`watchdog_llm.py`・`detect_regression.py --quick`・解析スクリプト・make_viewer が回るか=「復元の成功だけが証拠」(GitLab 教訓・Schrödinger's backup) | 解析が最後まで走る・part footer 検証全通過・sha256 マニフェスト照合エラー 0(3-2-1-1-0 の「0」) |
| 3 | **障害注入** | (a) vLLM プロセス kill → シムが継続/復帰するか (b) ダミーファイルでディスクを枯らす → 落ち方と検知 (c) 転送中の切断 → rclone/rsync の再開 | それぞれの復旧手順を 1 枚の runbook にする(本選中に考えない) |
| 4 | **C・サイズ実測** | 25 万体(または実測できる最大 N)で checkpoint 1 回の実時間 C とファイルサイズ・part flush の実時間 | §4.2 の表に代入して checkpoint_every を最終決定。ディスク予算(§1.4)を実数で引き直す |
| 5 | **転送 drill** | DC→ローカル/クラウドの実効帯域測定・1 日分相当を実際に送って照合 | §5.2 の表と突き合わせて日次運用が成立するか判定 |
| 6 | **無人運用 drill** | tmux 内 watchdog 起動→ SSH 切断→ 再接続で状況確認(status.json/tail)。日次点検(df・直近 checkpoint 時刻・fallback 率・OOM 痕跡 `journalctl -k`)を 5 分で回せるか | 朝夕 2 回の点検チェックリスト化 |
| 7 | **vLLM 再起動 drill** | checkpoint 休止点で vLLM を再起動し、シムが呼び損ねなく続行するか(リトライ/deadline の挙動確認) | 日次再起動を運用に入れるかの判断材料(§3-3) |

### 未確認事項(ユーザー確認待ち・本文書の前提が変わりうる点)

1. DC→外部の**実効帯域**(§5 の全シナリオ分岐点)。
2. DC 機の**ディスク総量と空き**(checkpoint 世代の間引き要否・watchdog バックアップ世代数)。
3. **外部ストレージ(クラウド課金の可否・Google Drive 等の既存プラン)**。
4. DC 機の OS・tmux/systemd の利用可否・再起動時の自動復帰手段。
5. 本選機に**ユーザー以外(運営側)のバックアップ機構**があるか(あるなら 3-2-1 の数え方が変わる)。
