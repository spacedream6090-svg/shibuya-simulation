# 本番インフラ手順書(vLLM 艦隊)— ops-production

ハッカソン本選で LLM 呼び出しを複数 vLLM サーバへ分散してシミュレーションを回すための手順。
**GPU 構成は未確定のため、1台マルチGPU・複数ノードの両方で同じシミュ側 config が動く**ように設計してある
(サーバの URL を並べるだけ。シミュ側コードの変更は不要)。

> ⚠️ **実機(GPU / 実 vLLM)未検証**。以下の vllm serve コマンド・量子化指定・think 制御は
> 公式ドキュメント準拠の設計値であり、本選環境で最初に**疎通確認**(§4)してから本番投入すること。
> 数値(トークン/秒、GPUあたり同時実行数、VRAM 実測)は**書かない**——実測は本選で埋める。

## 目次
- 0. 本番ハード構成(2026-07-06 更新)
- 1. アーキテクチャ(艦隊ルータの動作)
- 2. サーバ起動: 3構成
  - (A) 1台7GPU: `CUDA_VISIBLE_DEVICES` で 800i ポート×7
  - (B) 7台×1GPU: URL を7本並べるだけ
  - (C) tensor-parallel: 大モデル1本 + 小モデル群(tier 振り分け)
- 3. シミュ側 config
- 4. 疎通確認(bench.py)
- 5. checkpoint と決定論・キャッシュ
- 6. 障害時の挙動
- 7. トラブルシュート
- 8. 安全装置(watchdog)— 自動再開・復旧

---

## 0. 本番ハード構成(2026-07-06 更新)

> **本番ハードは単一ノードに 7GPU の可能性が高い**(データセンター提供、2026-07-06 ユーザー情報)。
> → **構成 (A)「1台7GPU」を第一候補**とする。各 GPU に vLLM を 1 インスタンス立て、
> `servers` に `http://localhost:8000..8006` を並べて FleetLLM(艦隊)で sticky routing。
> 複数ノード構成 (B) はフォールバック(コード・config は URL 差し替えのみで両対応)。
> tensor-parallel 構成 (C) は「重い内省を大モデルへ寄せたい」場合の選択肢。
> 単一ノードなので **watchdog も同ノードで常駐**させ、run.py を監督する(§8)。

---

## 1. アーキテクチャ

```
                     ┌─ VllmBackend(server0) ── vLLM :8000 (GPU0)
 Simulation          │
   └─ CachedLLM ── FleetLLM ─┼─ VllmBackend(server1) ── vLLM :8001 (GPU1)
      (D13 再現性)   (艦隊)   │   ...
                     └─ VllmBackend(serverN) ── vLLM :800N (GPUN)
```

- **FleetLLM** が rng_key(`"purpose/agent_id/step"`)から **agent_id** を抜き、
  `agent_id → サーバ` を安定割当(**sticky routing**)する。同じエージェントの
  ペルソナ + 履歴という長い共通 prefix が毎回同じサーバに当たるため、
  vLLM の **prefix cache** が効き、単一機の天井(~96%)近くまでヒット率が回復する
  (根拠: `docs/lit/infra__storage-routing.md`)。
- **CachedLLM** のキーは `backend.name`(= `fleet/<model>` / `vllm/<model>`)を含む。
  この name は **URL 非依存・モデル名ベース**なので、**サーバ台数や URL を変えても
  同一プロンプトの応答キャッシュがそのまま有効**(D13)。7GPU→複数ノードへ構成を
  差し替えてもキャッシュは無効化されない。
- 実 LLM は `backend=vllm` を選んだときだけ使われる。**既定(mock/ollama)の挙動は完全不変**。

---

## 2. サーバ起動

前提: 各 GPU / 各ノードで vLLM(OpenAI 互換サーバ)を起動する。共通の推奨フラグ:

| フラグ | 目的 |
|---|---|
| `--enable-prefix-caching` | ★sticky routing と対で効かせる。ペルソナ prefix を再利用 |
| `--max-model-len N` | KV キャッシュの VRAM を抑える。会話は短トークンなので過大にしない |
| `--quantization awq`(AWQ の場合) | 量子化。モデルが AWQ 版なら明示 |
| `--gpu-memory-utilization 0.90` | VRAM 使用率上限(余裕を残す) |
| `--enable-chunked-prefill` | 長 prefill の詰まり回避(infra summary の防衛策) |
| `--swap-space 0` | スワップ由来の 15〜35倍ペナルティを避ける(infra summary) |

`<MODEL>` は本選採用モデル(例: 量子化済み Qwen3 系。`docs/lit/shibuya_sim_infra_summary.md §6`)。
port は `800i`(i=GPU index)で統一しておくと URL を機械的に並べられる。

### (A) 1台7GPU — `CUDA_VISIBLE_DEVICES` でポート 800i ×7

各 GPU に 1 インスタンス(1枚=1モデル。NVLink/PCIe 帯域と並列制約を避ける方針=infra summary §1)。

```bash
# GPU i ごとに(i = 0..6)。別々のターミナル or tmux ウィンドウ/systemd で常駐。
for i in 0 1 2 3 4 5 6; do
  CUDA_VISIBLE_DEVICES=$i vllm serve <MODEL> \
    --port 800$i \
    --enable-prefix-caching \
    --enable-chunked-prefill \
    --swap-space 0 \
    --gpu-memory-utilization 0.90 \
    --max-model-len 8192 \
    --quantization awq \
    > vllm_$i.log 2>&1 &
done
```

→ シミュ側 servers:
```yaml
servers: ["http://localhost:8000","http://localhost:8001","http://localhost:8002",
          "http://localhost:8003","http://localhost:8004","http://localhost:8005",
          "http://localhost:8006"]
```

### (B) 7台×1GPU — URL を7本並べるだけ

各ノードで 1 インスタンスを起動(コマンドは A と同じ、`CUDA_VISIBLE_DEVICES=0`・`--port 8000`)。
**シミュ側は URL のホスト名を差し替えるだけで、コードも FleetLLM も一切変えない**(両対応の要点)。

```bash
# 各ノード(node1..node7)で:
vllm serve <MODEL> --port 8000 --enable-prefix-caching --enable-chunked-prefill \
  --swap-space 0 --gpu-memory-utilization 0.90 --max-model-len 8192 --quantization awq
```

→ シミュ側 servers:
```yaml
servers: ["http://node1:8000","http://node2:8000","http://node3:8000",
          "http://node4:8000","http://node5:8000","http://node6:8000","http://node7:8000"]
```

> ネットワーク越しになるので `model.timeout_s` はやや大きめ(例 180)に。ファイアウォールで 8000 番を開ける。

### (C) tensor-parallel — 大モデル1本 + 小モデル群(tier 振り分け)

重い内省(`reflect`)を大モデル(複数 GPU を tensor-parallel で束ねた1本)へ、
軽い会話・投稿を小モデル群へ振り分ける。**tier seam** を使う。

```bash
# 大モデル: GPU0-3 を tensor-parallel で1本(内省=reflect 専用)
CUDA_VISIBLE_DEVICES=0,1,2,3 vllm serve <BIG_MODEL> \
  --tensor-parallel-size 4 --port 8000 \
  --enable-prefix-caching --enable-chunked-prefill --swap-space 0 --max-model-len 16384

# 小モデル: GPU4,5,6 に1本ずつ(会話・投稿=default)
for i in 4 5 6; do
  CUDA_VISIBLE_DEVICES=$i vllm serve <SMALL_MODEL> --port 800$i \
    --enable-prefix-caching --enable-chunked-prefill --swap-space 0 --max-model-len 8192 &
done
```

→ シミュ側は `tiers` で purpose 別に振り分け:
```yaml
model:
  backend: vllm
  name: qwen3-society        # ★キャッシュキーはこの name（URL 非依存）。構成変更で無効化されない
  servers: ["http://localhost:8000","http://localhost:8004","http://localhost:8005","http://localhost:8006"]
  tiers:
    reflect: ["http://localhost:8000"]                                       # 内省=大モデル1本
    default: ["http://localhost:8004","http://localhost:8005","http://localhost:8006"]  # それ以外=小モデル群
```

- `purpose` は rng_key の先頭(`reflect` / `deliberate` / `recall` / `null` …)。
  `tiers` に無い purpose は `default` プールへ。`tiers` を書くと servers が1本でも FleetLLM 経路になる。
- ★注意: 大小でモデルが違っても `model.name` は**1つ**(キャッシュキー)。tier で別モデルを混ぜる場合、
  応答キャッシュは name 単位で共有されるため、**再現ランでは同じ tier 構成を使う**こと(§5)。

---

## 3. シミュ側 config(最小)

`conf/config.yaml` の `model` セクション、または実行時 dotlist 上書きで指定する。

```yaml
model:
  backend: vllm
  name: qwen3-society        # 応答キャッシュのキー（URL 非依存・モデル名ベース）
  temperature: 0.7
  max_tokens: 320
  reflect_max_tokens: 1200
  reflect_think: true        # 内省を思考モードで（qwen3: chat 経路は enable_thinking を送る）
  cache: true                # D13 再現性
  servers: ["http://localhost:8000"]   # 1本でも可（この場合 FleetLLM ではなく VllmBackend 直）
  timeout_s: 120
```

dotlist での上書き例(コードは書き換えない=D11):
```bash
python scripts/run.py model.backend=vllm 'model.servers=[http://localhost:8000,http://localhost:8001]'
```

- `servers` が **1本 かつ tiers 無し** → `VllmBackend`(単一)。
- `servers` が **複数 or tiers 有り** → `FleetLLM`(艦隊)。
- どちらも `CachedLLM` に包まれる(既存流儀・変更なし)。

---

## 4. 疎通確認(bench.py)

本番投入の前に、**小規模スモークで各サーバへ実際に到達するか**を確認する。

```bash
# vLLM へ 2 エージェント×2step だけ流す（疎通＋JSON 応答の確認）
python scripts/bench.py --backend vllm --servers http://localhost:8000 --agents 2 --steps 2

# 艦隊（複数サーバ）
python scripts/bench.py --backend vllm \
  --servers http://localhost:8000 http://localhost:8001 --agents 4 --steps 2
```

- `llm_calls > 0` かつ完走すれば疎通 OK。応答が壊れていれば `__vllm_error__: ...` が
  混ざり、シミュは fallback(routine)へ落ちて**クラッシュせず続行**する(§6)。
- 各 vLLM の起動ログに prefix cache ヒットが出ているかも確認する。
- ルーティング/フェイルオーバはログで追える(logger 名 `society.llm.fleet`、WARNING=フェイルオーバ / INFO=復帰)。
  本番ランで `logging` を INFO 以上にしておくと再分配が可視化される。

---

## 5. checkpoint と 決定論・キャッシュ

- **checkpoint_every**: 長時間ランでは `observer.checkpoint_every` を有効化しておくと途中再開できる(D16)。
  推奨: シミュ内 **半日〜1日ぶん(72〜144 step)ごと**を目安に(I/O と復旧粒度のバランス。実測で調整)。
  `0`(既定)= 無効で挙動は従来と完全同一。`>0` で `--resume` 可能。
- **決定論とキャッシュ(重要)**:
  - 実 LLM は `temperature > 0` だと**初回は非決定的**(サーバ側サンプリング。seed 固定しても
    バッチ構成で揺れうる)。**再現性の実体は応答キャッシュ(`llm_cache.jsonl`)**。
  - 初回ランで各プロンプトの応答がキャッシュへ書かれ、**同じ out_dir を使う再生ランは
    キャッシュを読んで完全に同じ軌道を再現する**(mock と同じ経路)。
  - キャッシュキーは `sha256(backend.name + params + prompt)`。`backend.name` は
    **URL 非依存**なので、**キャッシュ済みランの再生時にサーバ構成(台数/URL)を変えてもヒットする**。
  - 逆に **`model.name` を変えるとキャッシュは別物**になる。tier で大小モデルを混在させる場合は、
    再現ランでも同じ name・同じ tier 構成を保つこと(混在時はキャッシュが name 単位で共有される)。
  - temperature=0 でもサーバ実装により完全一致は保証されない。**厳密再現はキャッシュ再生で担保**する方針。

---

## 6. 障害時の挙動(D16)

- **1サーバがエラー/タイムアウト**: FleetLLM が `__vllm_error__` を検知して**次候補へフェイルオーバ**し、
  そのサーバを `cooldown_s`(既定30秒相当。実装は monotonic 時計基準)だけプールから外す。
  `cooldown` 経過後の呼び出しで自動的に **sticky 先へ復帰**する。再分配は WARNING ログに残る。
- **全サーバ不通**: 最後のエラー文字列(`__vllm_error__` / `__fleet_error__`)を返す。
  上位のシミュは壊れた応答を**行動 fallback(routine)**として扱い、**クラッシュせず継続**する
  (mock/ollama と同じ D16 流儀)。
- **単一 VllmBackend(servers 1本)**: フェイルオーバ先が無いので、失敗時はそのままエラー文字列 → fallback。
- 影響: 障害中はそのエージェントの LLM 発話が routine に落ちるだけで、**シミュ全体は止まらない**。
  復旧後は自動で元サーバに戻る。長時間の全滅に備え checkpoint を併用する(§5)。

---

## 7. トラブルシュート

| 症状 | 原因/対処 |
|---|---|
| `__vllm_error__: HTTP 404 ...` | `/v1/completions` 無し。VllmBackend は自動で `/v1/chat/completions` へ恒久切替(再試行)。それでも 404 ならモデル/エンドポイント設定を確認 |
| `__vllm_error__: HTTP 400 ...` | `response_format` 非対応など。VllmBackend は response_format を外して1度再送する。なお 400 が続く場合はプロンプト/パラメータを確認 |
| JSON パース失敗が多い | サーバが JSON 強制に非対応。プロンプト規約のみで動くが、可能なら `response_format`/`guided_json` 対応版の vLLM を使う |
| 思考ブロックが本文に混入 | `think=True` 時 qwen3 が `<think>…</think>` を出す場合あり。VllmBackend は先頭の think ブロックを剥がすが、モデル/テンプレ差異は本選で確認 |
| フェイルオーバが頻発 | `timeout_s` が短い/サーバ過負荷。timeout を上げる、`--max-model-len` を下げる、エージェント数(N上限 `lod.max_llm_per_step`)を絞る |
| キャッシュが効かない | `model.name` を途中で変えた/`model.cache=false`。再現ランは name とキャッシュファイルを固定 |

## 8. 安全装置(watchdog)— 自動再開・復旧

`scripts/watchdog.py` は run.py を子プロセスとして監督し、**落ちたら最新 checkpoint から自動再開**、
**壊れたらバックアップから復旧**する外殻。checkpoint/resume(D16, §5)の上に載る。標準ライブラリのみ・
Windows 対応。society を import しないので、シミュ本体のコードには一切触れない。

### 推奨起動コマンド(本番)

長時間ランは **必ず watchdog 経由**で起動する。`observer.checkpoint_every` を有効化しておくこと
(これが無いと再開できない)。**推奨: 半日〜1日ぶん(72〜144 step)ごと**(§5。I/O と復旧粒度のバランス)。

```bash
# 例: 構成A(1台7GPU)で 28日ぶん(4032 step)を checkpoint_every=72(=半日)で回す
python scripts/watchdog.py --run-dir runs/prod1 --stall-min 20 --max-restarts 10 -- \
    run.out_dir=runs run.name=prod1 \
    model.backend=vllm 'model.servers=[http://localhost:8000,http://localhost:8001,http://localhost:8002,http://localhost:8003,http://localhost:8004,http://localhost:8005,http://localhost:8006]' \
    observer.checkpoint_every=72 run.n_agents=80 run.n_steps=4032
```

- `--` の**後ろは run.py にそのまま渡る引数**(初回は素の起動、2回目以降は自動で `--resume runs/prod1` を付与)。
- **`--run-dir` は run.py の出力先(`run.out_dir/run.name`)と一致させる**こと(上例は `runs/prod1`)。
- 同じコマンドを再実行すれば、既存 run-dir を監督して checkpoint から続きを回す(再開)。
- 完走判定は **`summary.json` の存在 + exit 0**(= n_steps 到達)。誤って再起動しない。

主なオプション(既定値): `--stall-min 20`(ストール判定・分)/ `--max-restarts 10` /
`--poll-sec 5`(監視間隔)/ `--min-uptime-sec 60`(即死判定)/ `--backup-dir <run-dir>_backup` /
`--keep-backups 3`(世代数)/ `--backup-every-min 0`(0=checkpoint 進捗ごと)。

### 生成物(run-dir 内)

| ファイル | 内容 |
|---|---|
| `watchdog.log` | タイムスタンプ付きの全アクション(起動・再開・ストール・バックアップ・復元) |
| `status.json` | `{state: running/restarting/failed/done, restarts, last_progress, last_backup_step, pid}` |
| `run.out.log` | 子プロセス(run.py)の stdout/stderr(障害解析用) |
| `<run-dir>_backup/gen-<step>-<ts>/` | checkpoint/ + config.yaml + l1 parts の世代スナップショット(直近3世代) |

### 障害シナリオ別の挙動

| シナリオ | 検知 | watchdog の動作 |
|---|---|---|
| **プロセス死**(exit≠0, セグフォ/OOM 等) | `proc.poll()≠0` | 最新 checkpoint から `--resume` で再起動。`summary.json` 未生成なので完走と誤認しない |
| **ストール**(生きているが進まない) | checkpoint / l1 part が `--stall-min` 分更新なし | プロセスを terminate→kill し、最新 checkpoint から再開 |
| **連続即死**(起動 `--min-uptime-sec` 秒以内に進捗なく死) | uptime 短 & 進捗なし | 指数バックオフ(`2^n·base`, cap 60s)を挟んで再起動。config 不正など永続失敗を暴走させない |
| **checkpoint 破損**(gzip/pickle 読めない) | 起動前検証 or 同一 checkpoint から2回連続で再開失敗 | 疑わしい checkpoint を `checkpoint/corrupt/` へ隔離し、**1世代前のバックアップ**(checkpoint+parts+config の整合スナップショット)へ巻き戻して再開 |
| **リトライ上限超過** | `restarts > --max-restarts` | 諦めて `status.json` を `failed` にし exit 1(手動介入が必要=下記) |
| **正常終了** | exit 0 かつ `summary.json` 存在 | 再起動せず `done` で終了 |

> ⚠️ **ディスク逼迫**: watchdog 自体はディスク監視をしない(標準ライブラリのみの範囲外)。
> checkpoint 書き込みが失敗すると run.py が落ち→再開ループに入り得る。**バックアップ(`<run-dir>_backup`)
> は直近3世代で自動ローテーションされるが、run-dir 本体の checkpoint/ と l1 parts は溜まり続ける**。
> 本番前に `df` で空き容量を確認し、必要なら `--keep-backups` を下げる/ `--backup-dir` を別ボリュームに置く。
> 復旧不能(`status=failed`)の一次原因はまず `run.out.log` 末尾(トレースバック)を見る。

### 手動介入の手順

1. **状況把握**: `status.json`(state/restarts)と `watchdog.log` 末尾、`run.out.log` 末尾を見る。
2. **`failed` からの復帰**: 原因を除去(GPU 復旧・ディスク確保・config 修正)後、**同じ watchdog コマンドを再実行**すれば
   最新 checkpoint から続行する(`--max-restarts` はプロセス起動ごとにリセット)。
3. **checkpoint 破損が疑わしいのに自動巻き戻しで直らない**: `<run-dir>_backup/` の健全な世代を選び、
   その `checkpoint/`・`config.yaml`・`l1 parts` を run-dir へ手動コピーしてから再実行(watchdog も同じ復元を試みる)。
4. **やり直し(完走扱いを解除)**: 途中で `summary.json` が誤って残っている場合は削除してから再実行する
   (watchdog は `summary.json` があると「完走済み」とみなして何もしない)。
5. **停止**: watchdog プロセスを Ctrl-C / kill すると子 run.py も落ちる。次回起動で checkpoint から再開できる。

> **既知の制約**: run.py が l1 part の flush 中にクラッシュすると、その part が不完全に残り、最終 finalize の
> 結合を壊し得る(watchdog 由来ではなく D16 基盤側のリスク)。watchdog のバックアップは **直前の整合した
> checkpoint 時点**を捕えているため、疑わしい場合はバックアップ世代から復元するのが安全。`checkpoint_every`
> を大きすぎない値(§5 推奨)にしておくと、ロールバックで失う step も小さく抑えられる。

---

## 関連
- `docs/lit/infra__storage-routing.md`(sticky routing / prefix cache ~96%)
- `docs/lit/shibuya_sim_infra_summary.md`(GPU 配置・採用モデル・VRAM 防衛)
- 実装: `src/society/llm/vllm.py`(OpenAI 互換 HTTP)、`src/society/llm/fleet.py`(艦隊ルータ)、
  `src/society/engine/simulation.py`(backend 配線)、`tests/test_fleet.py`(スタブ検証)
