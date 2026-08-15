# Claude Code Handoff — Shibuya Simulation GPU / vLLM Performance Work
**Date:** 2026-08-16  
**Project:** `spacedream6090-svg/shibuya-simulation`  
**Purpose:** Claude Code が、これまでのサーバ構築・vLLM検証・実走結果・現在の性能ボトルネックを再調査せずに引き継ぎ、次の実装へ進めるためのハンドオフ。

---

## 0. 最重要サマリ

現在、**7× RTX A5000 上の vLLM Fleet 自体は正常かつ十分に並列化できる**ことが実測で確認済み。

一方で、実シミュレーションでは GPU がほぼ1枚ずつしか動かず、2,000 agents × 20 steps の実走で、

- `llm_calls = 970`
- `elapsed_sec = 577.689`
- 実効 end-to-end ≈ **1.68 calls/s**
- `peak_rss_mb = 994.7`

だった。

対して、シミュレーションを介さず `CachedLLM.generate_many(..., workers=8)` から Fleet を直接叩くマイクロベンチでは、

### DEFAULT tier（GPU1〜6）
- workers=1: **7.92 calls/s**
- workers=8: **54.64 calls/s**

### REFLECT tier（GPU0のみ）
- workers=1: **8.65 calls/s**
- workers=8: **46.38 calls/s**

まで伸びた。

**したがって主ボトルネックは GPU / vLLM / Fleet ではなく、Simulation 側の LLM 発行方式。**

特に、現在の `engine.batch_llm` は **planning / reflection 系を batch 化するが、通常の `deliberate` は逐次経路に残っている**。

今回の 2,000×20 実走では、

- `deliberate = 450`
- `recall = 260`
- `reflect = 260`

であり、`deliberate` は最大 **88 calls/step** 発生した。

**次の最優先実装候補は `deliberate` の step 単位 batch 化。**

---

# 1. プロジェクトの目的

渋谷を対象とした都市スケール LLM マルチエージェント社会シミュレーション。

最終的には約 **250,000 agents** 規模を目標にしている。

基本方針:

- 1 step = 10分
- 移動など日常的な処理は rule-driven
- interaction / event / reflection など必要な箇所だけ LLM
- LOD / event-driven で LLM 発火を抑える
- 会話・記憶・主体性・広告反応・都市施策などを観測
- 推論と3D可視化は分離
- staged scaling を必須とする

想定スケール:

1. wiring smoke
2. 2k performance smoke
3. 10k
4. 50k
5. 100k
6. 250k

**250kへいきなり進めない。**

---

# 2. GPU サーバ環境

Host:

```text
gpu-sv-002
```

GPU:

```text
RTX A5000 × 7
VRAM 約24GB × 7
合計 約168GB
```

確認済み:

- NVIDIA Driver: `595.84`
- `nvidia-smi` 上 CUDA: `13.2`
- Compute Capability: `8.6`
- 全7GPUで PyTorch matmul 成功

---

# 3. Python / venv

既存環境:

```text
~/venvs/gpu
```

これは既存検証環境なので触らない。

シミュレーション:

```text
~/venvs/sim
Python 3.10.12
```

vLLM:

```text
~/venvs/vllm
Python 3.10.12
vLLM 0.27.1
torch 2.13.0+cu130
FlashInfer 0.6.16.post3
```

---

# 4. Repo

Server clone:

```text
~/projects/shibuya-simulation
```

この作業セッション中に確認した server HEAD:

```text
f7b2a9b45469b357b3b2b72cac9857aa9506c6b2
```

その時点で、

```bash
git pull --ff-only
```

は成功している。

サーバは **pull-only 運用**。

基本方針:

- 実装
- commit
- push
- PR

はローカル / Claude Code 側で行う。

**サーバ上で tracked source を直接編集しない。**

サーバ上の untracked:

```text
src/shibuya_society.egg-info/
vllm_gpu0.log
vllm_gpu0_eager.log
vllm_gpu1.log
...
vllm_gpu6.log
```

これらは pull を妨げない。

---

# 5. Persona Pool

生成済み:

```text
1,000,000 personas
```

aggregate SHA256:

```text
533a45d8a52bcfeaa2f8ac72098c81a292a7f73b2577af9d20b333fbd791f4bf
```

重要:

`pool.enabled=true` の場合、単に

```text
run.n_agents=2000
```

だけでは不十分。

`pool.present_cap` が実際の在場人口を制御するため、

```text
pool.present_cap=2000
```

も必ず合わせる必要がある。

これを忘れると、`run.n_agents=2000` でも 250k 規模の初期化へ入る。

---

# 6. vLLM Fleet 構成

Model:

```text
Qwen/Qwen3-8B-AWQ
```

Pinned revision:

```text
4da05a8edb55c6046cce958586c33b61da07bb79
```

served alias:

```text
qwen3:8b
```

Ports:

```text
GPU0 → 8000
GPU1 → 8001
GPU2 → 8002
GPU3 → 8003
GPU4 → 8004
GPU5 → 8005
GPU6 → 8006
```

Profile:

```text
conf/profiles/finals-vllm7.yaml
```

Tier:

```yaml
reflect:
  - http://localhost:8000

default:
  - http://localhost:8001
  - http://localhost:8002
  - http://localhost:8003
  - http://localhost:8004
  - http://localhost:8005
  - http://localhost:8006
```

意味:

- `reflect` → GPU0 専用
- 通常 deliberate 等 → GPU1〜6

Fleet routing は sticky routing。

`rng_key = purpose/agent_id/step` から agent_id を抽出し、同じ agent がなるべく同じサーバへ行く。

Prefix cache を効かせる意図。

---

# 7. vLLM 起動に必要な環境

vLLM venv:

```bash
source ~/venvs/vllm/bin/activate

export CUDA_HOME="$VIRTUAL_ENV/lib/python3.10/site-packages/nvidia/cu13"
export CUDA_PATH="$CUDA_HOME"
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib:${LD_LIBRARY_PATH:-}"
export CC=/usr/bin/gcc
export CXX=/usr/bin/g++
```

baseline server:

```bash
MODEL="Qwen/Qwen3-8B-AWQ"
REV="4da05a8edb55c6046cce958586c33b61da07bb79"

CUDA_VISIBLE_DEVICES=0 vllm serve "$MODEL" \
  --revision "$REV" \
  --served-model-name "qwen3:8b" \
  --port 8000 \
  --gpu-memory-utilization 0.90 \
  --max-model-len 8192 \
  --enable-prefix-caching \
  --generation-config vllm
```

GPU1〜6も port / CUDA_VISIBLE_DEVICES を変えて同様。

---

# 8. vLLM セットアップ時に必要だった修正

## 8.1 FlashInfer Python 3.10 annotation bug

対象:

```text
flashinfer/comm/fd_exchange.py
```

`array.array[int]` annotation で失敗。

venv 内のみ、

```python
from __future__ import annotations
```

を追加済み。

**FlashInfer reinstall で消える可能性あり。**

---

## 8.2 compiler

インストール済み:

```text
build-essential
gcc/g++ 11.4.0
python3.10-dev
```

---

## 8.3 nvcc

venv:

```bash
python -m pip install "nvidia-cuda-nvcc==13.0.88"
```

nvcc:

```text
~/venvs/vllm/lib/python3.10/site-packages/nvidia/cu13/bin/nvcc
```

---

## 8.4 CUDA package version mismatch

当初:

```text
nvidia-nvvm / nvidia-cuda-crt = 13.3.73
```

で PTX 9.3 を生成し、ptxas 側が PTX 9.0 までだった。

以下へ揃えた:

```bash
python -m pip install --force-reinstall \
  "nvidia-nvvm==13.0.88" \
  "nvidia-cuda-crt==13.0.88"
```

---

## 8.5 libcudart / lib64

作成済み:

```bash
ln -s "$CUDA_HOME/lib" "$CUDA_HOME/lib64"
ln -s "$CUDA_HOME/lib/libcudart.so.13" "$CUDA_HOME/lib/libcudart.so"
```

---

# 9. Qwen3 thinking mode

Qwen3 は通常 chat template だと `<think>` を出し、token budget を消費する。

Simulation の通常 action / planning では thinking を切る。

`VllmBackend` の chat path では、

```json
{"chat_template_kwargs":{"enable_thinking":false}}
```

を渡す。

Profile:

```text
reflect_think=false
```

---

# 10. テスト状態

Repo sync 後:

```bash
python -m pytest \
  tests/test_fleet.py \
  tests/test_request_seed.py \
  -q
```

結果:

```text
25 passed
```

過去の Linux full gate:

```text
5713 passed
16 skipped
4 golden fails
2 matplotlib errors
```

matplotlib install 後、関連34 tests passed。

既知問題:

## Python 3.10 tomllib

`tests/test_xdist_grouping.py` が stdlib `tomllib` を直接 import。

Python 3.10 では失敗。

ローカル側で修正候補:

```python
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
```

dev dependency に `tomli` / `pytest-xdist` を明示する。

## Golden hashes

Linux で4件 SFM wall golden mismatch。

Windows/Linux float byte差の可能性が高い。

**Linux 値で Windows canonical hash を上書きしない。**

---

# 11. Fleet / Backend 単体検証

## VllmBackend

実 server に対し正常応答:

```json
{
  "action": "speak",
  "text": "こんにちは"
}
```

## FleetLLM

例:

```text
deliberate → port 8006
reflect    → port 8000
```

正常に JSON 応答。

---

# 12. Phase 1-1 wiring smoke — PASS

実行:

```bash
python scripts/run.py \
  --profile conf/profiles/finals-vllm7.yaml \
  run.n_agents=6 \
  run.n_steps=20 \
  2>&1 | tee wiring_smoke.log
```

結果:

```text
n_agents: 6
n_steps: 20
llm_calls: 10
llm_cache_hits: 0
elapsed_sec: 10.797
peak_rss_mb: 135.9
```

`l1b_llm.parquet` も生成。

**実LLM wiring は PASS。**

---

# 13. finals_observe + vLLM profile merge

`conf/finals_observe.yaml` は world / observation profile。

しかし model backend は vLLM fleet を直接含まないため、一時 profile を作成:

```text
/tmp/finals_observe_vllm7.yaml
```

生成:

```python
from omegaconf import OmegaConf

world = OmegaConf.load("conf/finals_observe.yaml")
vllm  = OmegaConf.load("conf/profiles/finals-vllm7.yaml")
cfg = OmegaConf.merge(world, vllm)

OmegaConf.save(cfg, "/tmp/finals_observe_vllm7.yaml")
```

確認:

```text
backend = vllm
model   = qwen3:8b
servers = 7
pool    = True
cap     = 250000
```

重要:

この merge 後も `pool.present_cap=250000`。

小規模 run では必ず dotlist override:

```text
pool.present_cap=<scale>
```

---

# 14. 最初の 2k run で発見した present_cap 問題

最初:

```text
run.n_agents=2000
pool.present_cap=250000
```

のまま起動してしまった。

症状:

- CPU 高負荷
- RSS 約2.5GB
- GPU 0%
- run dir 空

原因:

**persona pool 在場人口は present_cap 側が効く。**

この run は停止。

性能値としては不採用。

---

# 15. corrected 2k sequential run

修正:

```text
run.n_agents=2000
pool.present_cap=2000
run.n_steps=144
```

ただし後で config を確認したところ、

```yaml
engine:
  batch_llm:
    enabled: false
    workers: 8
```

だった。

GPU監視では、

```text
GPU0 → GPU6 → GPU2 → GPU4 ...
```

と routing 自体は分散していたが、

```text
num_requests_running
```

は基本的に1台だけ `1.0`。

`num_requests_waiting` は全台 `0.0`。

つまり、

**Fleet は分散しているが、Simulation からはほぼ逐次発行。**

この run は途中停止し、

```text
runs/night0_seq_partial
perf_2k_seq_partial.log
```

として保存。

---

# 16. batch_llm workers=8 実走

実行:

```bash
python -u scripts/run.py \
  --profile /tmp/finals_observe_vllm7.yaml \
  run.seed=42 \
  run.seed_auto=false \
  run.n_agents=2000 \
  run.n_steps=20 \
  run.name=batch2k20 \
  pool.present_cap=2000 \
  engine.batch_llm.enabled=true \
  engine.batch_llm.workers=8
```

保存 config:

```text
agents = 2000
steps  = 20
cap    = 2000
batch  = {'enabled': True, 'workers': 8}
```

---

# 17. batch2k20 完走結果

summary:

```text
n_agents             = 2000
n_steps              = 20
llm_calls            = 970
llm_cache_hits       = 0
elapsed_sec          = 577.689
peak_rss_mb          = 994.7
```

実効 end-to-end:

```text
970 / 577.689 ≈ 1.68 calls/s
```

注意:

これは純粋な vLLM throughput ではなく、

- world update
- event processing
- prompt build
- LLM latency
- response apply
- logging

を全部含む。

---

# 18. LLM purpose 分布

`llm_journal.jsonl.gz` から集計。

total:

```text
970
```

purpose:

```text
deliberate  450
recall      260
reflect     260
```

cache:

```text
miss 970
hit  0
```

backend:

```text
fleet/qwen3:8b 970
```

---

# 19. purpose × step 分布

## deliberate

```text
total = 450
max_per_step = 88
active_steps = 13
```

代表:

```text
step 1: 33
step 2: 88
step 3: 58
step 4: 48
step 5: 69
...
```

## recall

```text
total = 260
max_per_step = 31
active_steps = 17
```

## reflect

```text
total = 260
max_per_step = 31
active_steps = 17
```

recall / reflect は同じ step 分布。

これは reflection が、

1. recall
2. reflect

の2ラウンド依存構造だから。

---

# 20. GPU / vLLM runtime observation

batch_llm workers=8 の run 中でも、1秒サンプリングでは、

```text
running=[0,0,0,0,1,0,0]
running=[0,1,0,0,0,0,0]
running=[0,0,1,0,0,0,0]
...
```

のように基本1 requestだけが観測された。

`num_requests_waiting` は常に全台 0。

GPU utilization は各GPUへ移動するが、複数同時高負荷はほぼ見えなかった。

ただし、これだけでは vLLM/Fleet 側の並列性能不足とは言えないため、直接 benchmark を実施。

---

# 21. Fleet direct microbenchmark — 決定的結果

Simulation を通さず、

```python
CachedLLM(FleetLLM(...), enabled=False).generate_many(...)
```

を直接実行。

24 requests。

## DEFAULT tier / GPU1〜6

```text
workers=1
n=24
sec=3.029
calls/s=7.92
errors=0
```

```text
workers=8
n=24
sec=0.439
calls/s=54.64
errors=0
```

倍率:

```text
約6.9倍
```

## REFLECT tier / GPU0 only

```text
workers=1
n=24
sec=2.774
calls/s=8.65
errors=0
```

```text
workers=8
n=24
sec=0.517
calls/s=46.38
errors=0
```

倍率:

```text
約5.4倍
```

---

# 22. このベンチから確定したこと

## 正常

- GPU
- vLLM
- FleetLLM
- sticky routing
- ThreadPool based `CachedLLM.generate_many`
- continuous batching
- workers=8

これらは正常。

## ボトルネック

Simulation 側。

特に、

```text
deliberate
```

が step 内で大量発火しているのに、現在の `engine.batch_llm` の主要 batch 対象外。

---

# 23. 現在の engine.batch_llm 実装範囲

コード調査結果:

`engine.batch_llm.enabled=true` で batch 化される主要箇所:

## planning

```text
_phase_planning_batched(...)
```

朝計画を request build → generate_many → id順 apply。

## reflection

```text
_phase_reflect_batched(...)
```

agentic pull 有効時:

1. recall requests を batch
2. recall response を解決
3. reflect requests を batch
4. id順 apply

決定論保持を意識した設計。

---

# 24. 既存 `CachedLLM.generate_many` の重要仕様

既にかなり良い実装がある。

基本:

1. request list を順番に受け取る
2. cache hit / miss を逐次判定
3. unique miss だけ並行発行
4. response を元の request 順へ戻す
5. cache / counters / journal を決定論順で更新

`workers>1` の場合のみ、

```python
ThreadPoolExecutor(max_workers=workers)
```

で backend.generate を並行発行。

したがって、

**新しく engine 側へ ThreadPoolExecutor を追加しない。**

既存:

```python
sim.llm.generate_many(...)
```

を使う。

---

# 25. 次の最優先実装: deliberate batch 化

Claude Code へ依頼したい内容。

---

## 25.1 目的

通常の `deliberate` を step 単位で batch 発行できるようにする。

現在:

```text
agent A deliberate → wait
agent B deliberate → wait
agent C deliberate → wait
...
```

のような逐次処理になっている可能性が高い。

目標:

```text
step N:

agent A request build
agent B request build
agent C request build
...
↓
generate_many(requests, workers=N)
↓
agent A response apply
agent B response apply
agent C response apply
...
```

---

## 25.2 最重要制約

### batch OFF

既存挙動を完全維持。

```yaml
engine.batch_llm.enabled: false
```

なら既存コードパスをそのまま通す。

---

### deterministic ordering

以下を変えない:

- agent_id 順
- RNG 消費順
- event 発行順
- L1 event 列
- cache 内容
- llm.calls
- llm.hits
- journal 順

---

### dependency

同一 step の deliberate が、

```text
他 agent の同step LLM response
```

に依存する場合、無理に全件batch化しない。

まず、

- request build が独立して可能か
- apply 前に他 agent response が必要か
- interaction / conversation の causal dependency があるか

を調査する。

必要なら安全な batch boundary を分ける。

---

# 26. Claude Code へのそのまま使える依頼文

以下を Claude Code に渡してよい。

---

```text
現在、GPUサーバ上で shibuya-simulation の実LLM性能診断を行っています。

ハードウェア:
RTX A5000 × 7
Qwen/Qwen3-8B-AWQ
vLLM 0.27.1
ports 8000-8006

Fleet:
reflect → GPU0 / port8000
default → GPU1-6 / port8001-8006

Fleet/vLLM自体の並列性能は正常です。

直接ベンチ:
DEFAULT tier
workers=1: 7.92 calls/s
workers=8: 54.64 calls/s

REFLECT tier
workers=1: 8.65 calls/s
workers=8: 46.38 calls/s

errors=0

一方、実シミュレーション:

2000 agents × 20 steps
pool.present_cap=2000
engine.batch_llm.enabled=true
engine.batch_llm.workers=8

結果:
llm_calls=970
llm_cache_hits=0
elapsed_sec=577.689
peak_rss_mb=994.7
end-to-end ≈1.68 calls/s

LLM purpose:
deliberate=450
recall=260
reflect=260

最大/step:
deliberate=88
recall=31
reflect=31

コード調査では、
engine.batch_llm は planning / reflection に既存 batch 経路を持っています。

既存:
_phase_planning_batched
_phase_reflect_batched
CachedLLM.generate_many

しかし通常 deliberate は主要 batch 対象外です。

依頼:

まず deliberate の現在の実行経路を調査してください。

特に、
- deliberate request の build
- LLM generate
- response apply
- conversation / interaction
- RNG
- event logger
- 同一step内の他agent依存

を確認し、

どの範囲なら個体間独立性を壊さずに
step単位で request をまとめられるか説明してください。

その上で安全なら、
既存 planning/reflection batch 実装を正典として
deliberate を batch 化してください。

重要条件:

1.
engine.batch_llm.enabled=false の既存挙動を完全維持。

2.
engine側へ新しい ThreadPoolExecutor を直接足さず、
既存 CachedLLM.generate_many を使う。

3.
agent_id順を維持。

4.
RNG消費列を変えない。

5.
L1イベント順を変えない。

6.
llm.calls / hits / cache内容 / journal順を
逐次版と一致させる。

7.
request build と response apply を分離する。

8.
同一stepの他agentのresponseに依存する処理があれば
無理にbatch化せず、batch boundaryを明示する。

9.
mock backendで以下を比較するテストを追加:
- batch OFF
- batch ON workers=1
- batch ON workers=8

比較対象:
- L1イベント列
- llm.calls
- llm.hits
- cache内容
- 必要ならstate hash

10.
既存 tests/test_batch_llm.py を拡張するか、
同等の専用テストを追加する。

11.
既存 planning/reflection batch behavior を壊さない。

12.
実装前に、
「どの関数をどう分割するか」
「決定論をどう保つか」
を先に説明してください。

サーバ側は pull-only です。
実装・commit・push はローカル側で行ってください。
```

---

# 27. 実装後の検証手順

いきなり 2k×144 へ進めない。

---

## Step 1: tests

最低:

```bash
python -m pytest \
  tests/test_batch_llm.py \
  tests/test_fleet.py \
  tests/test_request_seed.py \
  -q
```

追加した deliberate batch tests も実行。

---

## Step 2: server pull

サーバ:

```bash
cd ~/projects/shibuya-simulation
git status --short
git pull --ff-only
```

tracked modification が無いことを確認。

---

## Step 3: 2k×20 regression performance run

baseline と同条件:

```text
run.seed=42
run.seed_auto=false
run.n_agents=2000
run.n_steps=20
pool.present_cap=2000
engine.batch_llm.enabled=true
engine.batch_llm.workers=8
```

baseline:

```text
llm_calls=970
elapsed_sec=577.689
peak_rss_mb=994.7
```

比較する。

---

## Step 4: GPU concurrency

期待:

複数 default ports で同時に、

```text
num_requests_running > 0
```

が観測される。

特に deliberate burst で GPU1〜6 が同時利用されること。

---

## Step 5: workers tuning

deliberate batch 実装後に、

```text
workers=8
workers=16
workers=32
```

の短い smoke を比較。

今までは workers を増やす前に Simulation 側 batch 化が必要だった。

---

## Step 6: 2k×144

最適 workers で実施。

記録:

- elapsed_sec
- peak_rss_mb
- llm_calls
- cache hit
- fallback rate
- vLLM queue
- GPU utilization
- prefix cache delta

---

## Step 7: 10k×144

2k が問題なければ進む。

---

# 28. 250k 前に別途注意すべき問題

Repo の `conf/smoke_wide.yaml` には、

250k 時の単ノード RSS が非常に大きくなる可能性が記録されている。

過去 1k mock run の RSS 外挿では、

```text
約1.26 MB / agent
```

程度の傾き。

単純外挿では、

```text
100k → 約145GB
250k → 300GB超
```

の可能性。

つまり、

**LLM GPU性能を解決しても CPU RAM / state representation が別の壁になる。**

25万本番の前に最低でも 10k の RSS 実測が必要。

---

# 29. やってはいけないこと

現段階では以下を勝手に変更しない。

- NVIDIA Driver
- kernel
- VPN
- OS
- apt autoremove
- CUDA major version
- Qwen model
- served model alias
- model revision
- Windows canonical golden hashes
- persona pool seed / hash
- tracked source のサーバ直接編集
- 250k 本番へのジャンプ

---

# 30. tmux / open file limit

vLLM processes:

```text
soft open files = 65535
hard open files = 65535
```

Simulation run shell でも:

```bash
ulimit -n 65535
```

を使う。

長時間 run は tmux。

---

# 31. 現在の判断

優先順位:

## P0

**deliberate batch 化の設計・実装・決定論テスト**

## P1

2k×20 再実測

## P2

workers 8/16/32 tuning

## P3

2k×144

## P4

10k×144

## P5

CPU RAM scaling / state representation 調査

## P6

50k → 100k → 250k

---

# 32. 最後に

今回の性能診断で重要なのは、

```text
7×A5000 / vLLM Fleet が遅いわけではない
```

ことが実測で確定した点。

Fleet は workers=8 で 5〜7倍程度スケールする。

したがって、

**GPU設定を触るより Simulation の LLM 発行粒度を batch 化する方が優先度が高い。**

特に deliberate は、

```text
450 calls / 20 steps
max 88 calls / step
```

あり、現在もっとも大きい batch 化候補。

ここを直した後で、改めて 2k performance smoke を取り直す。
