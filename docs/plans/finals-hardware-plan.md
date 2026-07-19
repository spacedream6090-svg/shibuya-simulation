# 本選ハードウェア調整計画(finals-hardware-plan)

- 作成: 2026-07-19 / 担当: Opus(運用計画・リポジトリ読取のみ・コード変更なし) / 種別: **仮計画 + スペック確定時の差し替え箇所を [要確定] で統一**
- 依頼(ユーザー 2026-07-19): 本番シミュ環境が使えるのは**ハッカソン本選期間に入ってから**。
  環境スペックは確定次第ユーザーが伝える。それまでに**仮でいいので綿密なハードウェア調整計画**を立てておく。
  想定 = データセンター1ノード・GPU7基。目標 = **100万プール・同時25万体級・10シミュ日**。
- 一次資料(本書が依拠):
  [`docs/research/scale-feasibility.md`](../research/scale-feasibility.md)(規模逆算の全数値の出所) /
  [`ops/launch-vllm-finals.ps1`](../../ops/launch-vllm-finals.ps1)(起動手順書) /
  [`ops/finals-compute-checklist.md`](../../ops/finals-compute-checklist.md)(E1実測手順) /
  [`docs/plans/compute-optimization.md`](compute-optimization.md)(タダ飯レバーの方針) /
  [`docs/ops-production.md`](../ops-production.md)(vLLM艦隊インフラ手順) /
  [`conf/profiles/finals-vllm7.yaml`](../../conf/profiles/finals-vllm7.yaml) /
  [`scripts/estimate_runtime.py`](../../scripts/estimate_runtime.py)(逆算ツール) /
  [`scripts/bench.py`](../../scripts/bench.py)(ベンチ) / [`scripts/watchdog.py`](../../scripts/watchdog.py)(安全装置) /
  [`docs/plans/persona-pool.md`](persona-pool.md)(100万プール設計) / devlog Entry 11-12(部分納品の実運用)。

> **凡例**: `[要確定]` = スペック確定時にユーザー回答で差し替える箇所。**推定** = 実測でない試算値(本選 Day-0 で置換)。
> 太字の「本命」= 現時点で最も確度が高いと判断した構成。

---

## §0 現時点で判明しているハード事実(重要 — ほぼ確定)

ハッカソン募集要項([`docs/AUTOMATA第2回ハッカソン案.md`](../AUTOMATA第2回ハッカソン案.md) L19-20, L37-59)に
**ハード仕様が明記されている**。これは「仮定」ではなく主催の公表値:

| 事項 | 公表値 | 含意 |
|---|---|---|
| VRAM 総量 | **168 GB** | 168 ÷ 7 = **24 GB/GPU** |
| GPU | **RTX5000 × 7 台**(1 台の PC) | 24GB 級 = **RTX A5000 相当**(`vllm-7gpu-a5000` プリセットと一致) |
| トポロジ | **単一 PC に 7 GPU** | **ops topology A(単一ノード7GPU)で確定**。複数ノード配線(構成B)は不要 |
| 利用期間 | **本選 10 日間** | wall 予算 = 10 日。Day-0 ベンチ込みで実ラン枠は実質 **8〜9 日** |
| 割当 | 7チーム程度に各1クラスタ(7台用意) | **1チーム=1ノード占有**の可能性が高い([要確定]: 占有か共有か) |

> **判断**: 本書は**「A5000級 24GB × 7・単一ノード」を本命**として全構成を組む。
> `docs/research/scale-feasibility.md` の「本選機が A5000 級なら LLM 時間は上表の ~2.7倍」という注記が
> **本命シナリオそのもの**になる。ただし「RTX5000」の正確な世代(A5000=24GB か RTX 5000 Ada=32GB か)は
> 168GB 総量から 24GB と逆算できるものの**銘板未確認**なので [要確定]。他 GPU 種の行(§1)は
> 主催が直前に機材変更した場合の保険として残す。

### §0.1 目標の正直な現実チェック(25万体 × 10シミュ日)

`scale-feasibility.md` の表は **N=100,000 まで**で、そこですら「非LLM が lean でも 439分/日 →
engine を桁で最適化しない限り 100日は非現実的」と結論している。**同時25万体は表の外挿**であり、
以下が全て揃って初めて 10日 wall に収まる:

- **非LLM(Python step)が lean(0.00183 秒/agent-step)以下**であること。`scale-feasibility.md` §6 の
  可否ライン `c_nonllm ≤ 600/(N·D)`(D=シミュ日/24h)より、**25万体で 1シミュ日/24h を出すには
  c ≤ 600/250000 = 0.0024**。現状の lean 実測 0.00183 は**ギリギリ通る**が、full 0.060 では 25倍足りない。
- **観測/出力パイプラインのストリーミング化**(`scale-feasibility.md` §4.3): `measure.load_events` の全件RAM展開・
  L3 snapshot 全 agent JSON 化・`export_3d` の T×N セルは、25万体では **wall でなくメモリで破綻**する。
- **LOD(前景比率)+ プレゼンス・ローテーション**で「同時実体数」を絞る余地。25万を**全員フルLLM前景**にする
  必要はない(§1・§4 で扱う)。

→ 本計画は **25万体を"最大到達目標"、5万〜10万体を"堅い着地"** と二段構えで設計し、Day-0 実測で
どちらに倒すかを決める(§2・§3 の縮退線)。**「まず engine を lean 以下へ、次に LOD」**の順序は
`scale-feasibility.md` の結論そのまま。

---

## §1 環境パターン別 初動構成表(スペックを聞いたら該当行を読むだけ)

**使い方**: ユーザーから GPU 種 × 基数を聞いたら、下表の該当行の「起動」「同時体数の上限」を読む。
全 req/s は **推定**(`scale-feasibility.md` §2 冒頭の捏造回避方針に従い、measured ではない)。
**Day-0 の `vllm bench serve` で必ず置換**(§2-②)。

### §1.1 本workloadの呼形状(全行共通の前提)

- プロンプト **~1,300 tok 入力 / ~320 tok 生成**(reflect のみ ~768 tok 上限)。**prefill 支配**。
- temperature=0.7・JSON 強制・`reflect_think=false`(`conf/production.yaml` L265 で確定済)。
- FleetLLM が `agent_id` で **sticky 割当** → prefix cache が効く(`conf/profiles/finals-vllm7.yaml`)。

### §1.2 GPU種 × 基数 マトリクス

| # | GPU / 基数 | モデル配置(本命) | vLLM起動の要点 | 期待 集約req/s(推定) | LLM側が捌ける上限 | **非LLM律速の同時体上限** |
|---|---|---|---|---|---|---|
| **本命** | **RTX5000/A5000 24GB × 7**(168GB) | qwen3:8b を **AWQ/INT4** で7レプリカ(1枚1本)。VRAM節約優先。4B bf16 なら余裕 | `--enable-prefix-caching` / `--max-model-len 8192` / `--gpu-memory-utilization 0.90` / `--max-num-seqs 128〜256`(要調整) | **21 req/s**(3/GPU×7・range 14–35) | 予算ゲート下で 10万体でも回る(~178分/シミュ日 @full-LLM) | lean 0.00183 → **~25万体で 1シミュ日/24h(要 streaming)** / full 0.060 → ~4千体 |
| 2 | A100 40GB × 7 | qwen3:8b bf16 7レプリカ or 4B bf16。AWQ 不要 | 同上・`--max-num-seqs 256〜512` | **56 req/s**(8/GPU×7・range 42–84) | 10万体でも余裕 | 同上(**非LLMは GPU 種に非依存**) |
| 3 | A100 80GB × 7 | 8b bf16 7本、or **reflect tier=32B(TP2)+ 8b×5** | tier分割は `finals-vllm7.yaml` の servers/tiers を port 割当に合わせ書換 | 56 req/s(default tier) | 10万体でも余裕 | 同上 |
| 4 | H100 80GB × 7 | 8b bf16 7本 or 32B tier + 8b | 同上 | **98 req/s**(14/GPU×7・range 70–140) | 10万体で最速 | 同上 |
| 5 | L40S 48GB × 7 | 8b bf16 7本(48GBは余裕) | 同上・`--max-num-seqs 256` | **~35 req/s**(5/GPU×7・**推定**) | 10万体で回る | 同上 |
| 6 | 基数 **4** の場合 | レプリカ4本(reflect兼務) | port 8000-8003 のみ | 上記 × (4/7) | 5万体級まで現実的 | 同上(非LLMは不変) |
| 7 | 基数 **8** の場合 | レプリカ8本 | port 8000-8007 | 上記 × (8/7) | 10万体+ | 同上 |

> **この表の最重要メッセージ**(`scale-feasibility.md` の核心):
> **「同時体数の上限を決めるのは GPU 種ではなく、非LLM(Python step)の秒/agent-step」**。
> どの GPU でも非LLM 物理 step は全 N 体分必ず回り、LOD でも spec でも減らない。
> GPU 種が効くのは「LOD 前景比率をどこまで上げられるか(=忠実度)」「モデルサイズ」「LLM の余裕」であって、
> **同時体の天井そのものではない**。→ 投資先は engine 最適化(§4 の宿題)。

### §1.3 同時体数の逆算式(該当スペックで即計算)

`scale-feasibility.md` §6 の直列モデル。**per-シミュ日の壁時間 = LLM + 非LLM(直列)**:

```
T_simday(N) = C_calls(N,fg) / R_eff   +   144 · N · c_nonllm
  C_calls(N,fg) = min( 3988·(N/200)^1.209·λ , 43200 ) + 305·(N/200)·λ    (λ = fg + (1−fg)·0.1)
  R_eff = (集約req/s) ÷ 1.15(overhead)          ← 例: A5000 21 → 18.3 呼/s
  c_nonllm ∈ [0.00183(lean), 0.060(full)]        ← Day-0 の mock 実測で確定(§2-④)
シミュ日/24h = 86400 / T_simday
```

**逆算のショートカット**(LLM を無視した非LLM 律速の上限。大 N ではこれが支配):

| 目標: 10シミュ日を 10日 wall で = **1シミュ日/24h** 必要 | 必要 c_nonllm | lean(0.00183)で可能か |
|---|---|---|
| 同時 **2.5万**体(Day1 スモーク) | ≤ 0.024 | ◎ 余裕(lean なら ~13シミュ日/24h) |
| 同時 **5万**体 | ≤ 0.012 | ◎ 可(~7シミュ日/24h) |
| 同時 **10万**体 | ≤ 0.006 | ○ 可(~3.3シミュ日/24h・要 streaming) |
| 同時 **25万**体(最大目標) | ≤ 0.0024 | △ ギリギリ(lean 0.00183 で ~1.3シミュ日/24h・**streaming 必須**) |

**該当スペックで実際に叩くコマンド**(表を実測較正で再現。§2 の後に本番スペックで再実行):

```bash
# 本命(A5000×7)・25万体・full-LLM・spec+apc 込み・非LLM lean で 1シミュ日の壁時間を見る
python scripts/estimate_runtime.py --agents 250000 --days 1 --calib runs/demo_event_200a3d \
    --fleet vllm-7gpu-a5000 --speculative --prefix-cache --nonllm-profile lean
# 5万体・前景10%LOD・堅い着地の確認
python scripts/estimate_runtime.py --agents 50000 --days 10 --calib runs/demo_event_200a3d \
    --fleet vllm-7gpu-a5000 --lod-fg-ratio 0.1 --nonllm-profile lean
# Day-0 で非LLMを実測したら --nonllm-sec-per-agent-step <実測値> で上書きして再判断
```

---

## §2 Day-0 ベンチプロトコル(環境到着初日・所要 2〜3 時間)

**目的**: 「文献値で約束しない」(`finals-compute-checklist.md` の不変条件)。到着初日に 5 項目を実測し、
**その日のうちに §1 の表を実測値へ更新 → 規模を決定**する。全て `runs/_bench/` に証跡を残す。

### ① vLLM 起動疎通(~20分)

```bash
# まず dry-run でコマンドを確認(何も起動しない)
powershell -NoProfile -File ops/launch-vllm-finals.ps1 -Model qwen3:8b
# 表示された Linux 用1行(GPU0→8000 ... GPU6→8006)を finals ノードで7本起動。例(GPU0):
CUDA_VISIBLE_DEVICES=0 vllm serve qwen3:8b --port 8000 --served-model-name qwen3:8b \
    --gpu-memory-utilization 0.90 --max-model-len 8192 --enable-prefix-caching > vllm_gpu0.log 2>&1 &
# 疎通(2体×2step だけ vLLM 経路へ流す)
python scripts/check_llm_backends.py --backend openai_compat --base-url http://localhost:8000/v1 --model qwen3:8b
python scripts/run.py --profile conf/profiles/finals-vllm7.yaml run.n_agents=6 run.n_steps=20
```
- **VRAM 確認**(24GB 制約が本命): 8b bf16 が KV 込みで載るか。載らなければ **AWQ/INT4** へ切替
  (`--quantization awq` 等・[要確定]: 使う量子化)。載れば bf16 のまま。`nvidia-smi` でメモリ実測。

### ② 本 workload 呼形状での req/s 実測(~40分)★最重要

```bash
# vLLM 標準ベンチ(1,300in/320out = 本シミュの呼形状)を各 GPU で数点
vllm bench serve --model qwen3:8b --base-url http://localhost:8000/v1 \
    --random-input-len 1300 --random-output-len 320 --num-prompts 200 --request-rate inf
# → 集約 req/s・TTFT・生成 tok/s を記録。7本合計が §1 の「集約req/s」の実測値。
```
- サーバ側メトリクスも取る: `curl http://localhost:8000/metrics | grep vllm:`(`avg_generation_throughput_toks_per_s`)。
- **`--max-num-seqs` を振って**(64/128/256/512)スループット飽和点を探す。24GB は KV が細いので
  過大な max-num-seqs は OOM/スワップ。飽和点を本番 config に採用。

### ③ prefix cache 有効時の実測(~20分)

```bash
# finals-vllm7.yaml で 6体×20step の配線スモーク → ヒット率を /metrics で確認
python scripts/run.py --profile conf/profiles/finals-vllm7.yaml run.n_agents=6 run.n_steps=20
curl http://localhost:8000/metrics | grep -E "prefix_cache|gpu_prefix_cache_hit_rate"
```
- sticky が効けば同一 agent の2回目以降の接頭辞がヒット(`finals-compute-checklist.md` E1-2)。
- **前後比較**: prefix cache OFF/ON で ② の req/s を取り直し、**apc 実効倍率**(推定 ×2.2)を実測に置換。
- **★共有が無いと逆に −37%**(`scale-feasibility.md` §2.2)。ヒット率が低ければプロンプト接頭辞の
  共有構築を見直す(この場合 apc 倍率は 1.0 として扱う)。

### ③′ speculative decoding 実測(任意・時間があれば ~30分)

```bash
powershell -NoProfile -File ops/launch-vllm-finals.ps1 -Model qwen3:8b -Speculative   # ngram draft から
```
- **無損失確認は temperature=0(greedy)でバイト一致**(`finals-compute-checklist.md` E1-1)。0.7 では
  acceptance rate と distinct-n・自己反復率で健全性を見る(バイト一致は使わない)。
- **飽和運転では spec が 1.0 割れもある**(`scale-feasibility.md` §2.2)。before/after の tok/s を実測し、
  1.0 を割るなら **本番では spec OFF**。倍率は実測値のみ記載。

### ④ mock 1万体エンジンベンチ(非LLM 単価の実測)★規模を決める数字(~30分)

```bash
# LLM をスタブ化(mock)して純 Python step 時間を測る。ms/agent-step が §1.3 の c_nonllm。
python scripts/bench.py --backend mock --agents 1000 5000 10000 --steps 144
# 出力の ms_per_agent_step ÷ 1000 = c_nonllm(秒)。peak_mem(MB) も規模の壁の予兆。
```
- **これが 0.00183(lean)〜0.060(full)の 33倍レンジのどこか**を確定する数字(`scale-feasibility.md` §4)。
  本番 config(`production.yaml`=全チャネルON)で測るので **full 寄り**が出るはず。**ここが 0.006 を超えたら
  25万体は不可** → §3 の縮退線へ。
- N を上げて `events_per_step`・`peak_mem_mb` が**超線形**に伸びていないか(密度上昇で O(N²) 劣化・
  `scale-feasibility.md` §4.3)を確認。

### ⑤ 表の更新 → 当日中に規模決定(~20分)

```bash
# ②の実測 req/s と ④の実測 c_nonllm を estimate_runtime に入れて §1.3 の表を作り直す
python scripts/estimate_runtime.py --agents 250000 --days 1 --calib runs/demo_event_200a3d \
    --fleet vllm-7gpu-a5000 --sec-per-call <②から算出した実効秒/呼> \
    --nonllm-sec-per-agent-step <④の実測 c_nonllm>
# 2.5万/5万/10万/25万で回し、「1シミュ日/24h ≥ 1」を満たす最大 N を当日の本番規模に採用。
```
**決定ルール**: 「10シミュ日を 8〜9 日 wall(Day-0 を除く残り)で完走」= **必要 ~1.1〜1.25 シミュ日/24h**。
これを満たす最大の N を本番規模に据える。満たさなければ LOD 前景比率を下げる → それでも駄目なら N を下げる。

---

## §3 段階リハーサル計画(本選 10 日の日程表 + 縮退線)

wall 予算 10 日。前半で規模を確定し、後半に本番ランを積む。**部分納品体制**(devlog Entry 12・
checkpoint の part 結合)により**ランを止めずに随時データを出す**。

| Day | 予定 | 完了ゲート(次へ進む条件) |
|---|---|---|
| **Day 0** | §2 のベンチ全 5 項目 → 規模決定・本番 config 確定 | ②req/s・④c_nonllm 実測済 / `finals-vllm7.yaml` の max-num-seqs 確定 |
| **Day 1** | **2.5万体 × 1シミュ日 スモーク**(watchdog 経由)。checkpoint 日次・part flush 確認 | 崩壊なし(fallback<1%・reflect 書き戻し>0) / checkpoint→resume 往復1回成功 |
| **Day 2** | 規模拡大判断(5万→10万→25万を段階投入)+ **観測系の確認**(heatmap/OD/summary/viewer の part 結合予行) | 目標 N で 1シミュ日が完走 / assemble_parts で部分データが出せる / RAM 破綻なし |
| **Day 3-8** | **本番 10 シミュ日ラン**(確定 N)。checkpoint 日次・**日次部分納品**(part 結合で昼夜リズム毎に差替) | 日次 checkpoint 進捗 / 異常値のみ定期確認(無停止続行=Entry 12 の運用) |
| **Day 9** | 予備日 / 解析(analyze_* スイート・detect_emergence・founder パネル)・最終納品の再生成 | summary_ja・忠実性スコア・k* データの確定 |

> **無停止運用の原則**(devlog Entry 12・memory `validation-runs-short`/`ask-before-extending`):
> ランは承認待ちで止めない。**異常値のみ定期確認**し、納品は走行中ランの checkpoint part から結合して出す。

### §3.1 縮退線(遅延時にどの日までに何が動かねば規模を1段落とすか)

| 判定時点 | これが動かなければ | 縮退アクション(1段落とす) |
|---|---|---|
| **Day 0 終わり** | ④ c_nonllm が 0.006 超(=10万体で 1シミュ日/24h 未満) | 目標を **25万→10万体以下**へ。lean 化(engine最適化)が Day-0 で間に合わないため |
| **Day 0 終わり** | ② 実測 req/s が推定の半分未満(A5000 で <10) | LLM が律速に戻る規模を LOD 前景比率で回避(fg=0.03〜0.1)。またはモデルを 4B へ |
| **Day 1 終わり** | 2.5万体スモークが 1シミュ日を回せない / OOM | 同時体を **1万体**級へ。observer ストリーミングが要るなら Day2 で対処、無理なら N 固定 |
| **Day 2 終わり** | 目標 N で observer/RAM が破綻(export_3d・load_events) | LOD 背景の観測を間引く or N を 1 段(25万→10万→5万→2.5万)下げる |
| **Day 5 昼** | 本番ランが 5 シミュ日に未達(ペース不足) | 残り日数 ÷ 必要シミュ日で**シミュ日数目標を短縮**(10→7→5)。体数は維持(「体数>時間」方針) |
| **Day 7 昼** | まだ本番完走の見込みが立たない | **確定分を部分納品で確定**(Entry 12 方式)。未完でも 2〜3 シミュ日分の k* データを成果として固める |

**方針の軸**(memory `project-charter`・ユーザー既定「エージェント数 > 実行時間」): 縮退はまず**シミュ日数を削る**、
体数はできる限り維持。ただし OOM・observer 破綻は例外で**体数を落とす**(wall でなくメモリの壁のため)。

---

## §4 ローカルで事前に済ませる宿題(本選期間前)

本選 10 日を実ランに使うため、**LLM を要さない準備は全て期間前にローカルで終える**。

### §4.1 データ・名簿の事前生成(決定論・LLM 負荷ゼロ or 少)

```bash
# 100万プール(persona-pool.md §1.1: gen_personas は pool→sample の2段が既存)。
# まず大プールを決定論生成(--pool は余剰・--sample は同時実体の初期名簿)。
python scripts/gen_personas.py --pool 1000000 --sample 250000 --seed 42 \
    --out data/personas_finals.json --pool-out data/persona_pool_1M.json
# ↑ [要確定] pool/sample の最終数は Day-0 の規模決定に合わせる。100万は生成コスト・RAM を要確認
#   (§4.4 の mock スモークで名簿ロード時間・メモリを先に測る)。
# 組織台帳・配属(場所非依存・需要駆動。役割ペルソナ=店員/駅員等の必要数はここから逆算)
python scripts/build_orgs.py --map data/shibuya_osm_wide_v7.json \
    --roster data/personas_finals.json --out data/org_assignments_finals.json \
    --orgs-out data/organizations_shibuya_wide.json
# 議員はペルソナで事前決定(production.yaml: assembly.from_roster=true・選挙はしない)
```
- **プール・ローテーション機構は現状未実装**(persona-pool.md §1.3 が明言)。「同時存在数の数倍プールから
  日次で誰が入域するか」を選ぶ設計は **[要確定] 実装するか**(実装は `pre-coding-alignment` に従いユーザー合意後)。
  未実装のまま行くなら「同時 = run.n_agents 固定」で回す(プールは初期名簿の供給源としてのみ使う)。
- ODPT 実ダイヤ・地図・交通は生成済み資産(`data/transit_odpt.json` 等)を流用(再取得不要)。

### §4.2 エンジン最適化(**最優先の宿題** — これが 25万体の可否を決める)

`scale-feasibility.md` の結論 = **投資先は LLM でなく Python シミュ本体**。期間前にローカルで:

- **非LLM 秒/agent-step を lean(0.00183)以下へ**近づける。現状 full 0.060 との 33倍差を詰める。
  ボトルネックは §4.3 に列挙(観測 IO・snapshot・O(N²) 劣化)。
- **観測/出力のストリーミング化**(`scale-feasibility.md` §4.3 が破綻点として警告):
  `measure.load_events` の全件 RAM 展開 / L3 snapshot の全 agent JSON 化(~3GB) / `export_3d` の T×N セル /
  `network_windows` の O(窓×E)。**25万体では wall でなく RAM で落ちる**ため、N を上げる前に必須。
- これらは **src/society 変更を伴う** → memory `ask-before-extending`/`pre-coding-alignment` に従い、
  **ユーザーに実装可否と範囲を確認してから着手**([要確定])。ゴールデン L1 バイト一致・R1(呼数不変)を維持。

### §4.3 25万体の mock スモーク(ローカル RAM で可能な範囲)

```bash
# 非LLM 純計算・メモリの実測。ローカル RAM の許す最大 N まで段階的に。
python scripts/bench.py --backend mock --agents 10000 50000 100000 --steps 144
# peak_mem_mb と ms_per_agent_step の N 依存(線形か超線形か)を確認。
# 100万プール名簿のロード時間・常駐メモリも別途 6体×2step で計測(名簿だけ finals サイズにして)。
```
- ローカル RAM で 25万体が載らない場合でも、10万体までの傾きから **外挿して本選ノードの RAM 要件を見積る**
  → §6 の「RAM [要確定]」の質問材料にする。
- この段階で observer 破綻点(export_3d・load_events)を**実際に踏んで**、期間前に潰す。

### §4.4 転送物のパッケージング(本選ノードへ持ち込む一式)

- **モデル**: qwen3:8b(+ AWQ/INT4 版)・spec draft(qwen3:0.6b 級)を事前 DL しておく(本選ノードの
  ネット [要確定] に依存しないよう、可能ならオフライン持込)。
- **データ**: 生成済み `data/*.json`(地図 wide_v7・組織台帳・ODPT ダイヤ・personas_finals・pool)。
  **★ODPT 再配布制限**(§5.4)に注意 — ODPT 由来の生データは**成果物に同梱しない**。加工物のみ。
- **リポジトリ + セットアップスクリプト**: `git clone` + `pip install -e .`(pyproject.toml)の一発手順を
  用意。`ops/launch-vllm-finals.ps1` は **Linux ノード向けにコマンドを表示するだけ**なので、貼るだけで動く。
- **チェックリスト**: `ops/finals-compute-checklist.md` を印刷/携行(実測項目の抜け防止)。

---

## §5 運用の備え(監視・checkpoint/resume・障害・セキュリティ)

### §5.1 監視(watchdog)

`scripts/watchdog.py` は run.py を子プロセスとして監督し、**落ちたら最新 checkpoint から自動 resume・
ストールで kill 再開・破損でバックアップから復旧**する(標準ライブラリのみ・society 非依存)。

```bash
# 本番は必ず watchdog 経由で起動。checkpoint_every を有効化しておくこと(=resume の前提)。
# 例: 確定 N 体で 10シミュ日(1440 step)を checkpoint_every=144(=日次)で回す
python scripts/watchdog.py --run-dir runs/finals1 --stall-min 20 --max-restarts 10 \
    --keep-backups 3 -- \
    --profile conf/production.yaml \
    --env env/shibuya \
    model.backend=vllm \
    run.name=finals1 run.out_dir=runs \
    run.n_agents=<確定N> run.n_steps=1440 observer.checkpoint_every=144
```
- 監視ロジック: プロセス死→resume / checkpoint・part が `--stall-min`(既定20分)進まず生存→kill再開 /
  exit0+summary.json→完了 / `--max-restarts` 超過→failed / 連続即死→指数バックオフ /
  同一 checkpoint から2回無進捗→1世代前へロールバック。
- 生成物: `watchdog.log`・`status.json`(state/restarts/last_progress)・`run.out.log`。
- **`--stall-min` は 25万体の1 step 実時間に合わせて調整** [要確定]。step が 20 分を超えるなら誤検知するので上げる。

### §5.2 checkpoint / resume(D16)+ 部分納品

- `src/society/engine/checkpoint.py`: **完全状態を pickle+gzip・原子的 rename**。RngHub はステートレスなので
  乱数状態は保存せず master seed から再導出。**`config_hash` が n_agents 等を含む** → resume 時に
  seed/n_agents/因子を変えると弾かれる(決定論保護)。resume は run-dir の `config.yaml` を土台に
  `run.n_steps=…` だけ追加して先へ延ばせる。
- **part flush**(`observer/logger.py`): checkpoint ごとに溜まったログを `l1_events.part-NNNN.parquet` 等へ
  書き出しメモリ解放。finalize で part 群を結合し単一 parquet を出す(checkpoint 無効時は part を作らず
  byte 完全同一)。**この機構が「走行中ランからの部分納品」を可能にする**(devlog Entry 12)。
- **部分納品手順**(Entry 12 の実運用): 走行中でも最新 checkpoint 到達分の part を結合 → heatmap/OD/
  crowd/summary_ja/viewer/dashboard を再生成して差し替え送付。第35バッチは `scratchpad/assemble_parts.py`
  で part 結合した(**本選前にこの結合スクリプトを scripts/ 正規化するか要検討** [要確定])。

### §5.3 障害リカバリ(GPU 落ち・OOM)

| 障害 | 検知 | 対応 |
|---|---|---|
| **GPU 1枚死/vLLM 1本落ち** | FleetLLM のサーバ応答エラー | FleetLLM は生存サーバへフェイルオーバ・復旧後自動復帰(`ops-production.md` §6)。全滅時は checkpoint 併用で救う |
| **全 vLLM 全滅** | run.py が LLM エラー連発 → 進捗停止 → watchdog がストール kill | 最新 checkpoint から resume。vLLM を再起動してから watchdog を同コマンドで再実行 |
| **OOM(GPU VRAM)** | vLLM が CUDA OOM で落ちる | `--max-num-seqs` を下げる / `--gpu-memory-utilization` を下げる / モデルを AWX/INT4・4B へ。24GB は特に注意 |
| **OOM(ホスト RAM)** | run.py が MemoryError(observer 全件展開・snapshot) | **§4.2 の streaming 化が未了なら N を落とす**。checkpoint から低 N で resume は不可(config_hash 不一致)→ 新ランで規模再設定 |
| **checkpoint 破損** | resume 2回連続無進捗 | watchdog が corrupt 隔離 → 1世代前バックアップ(`<run-dir>_backup/gen-*`)から復元 |
| **ストレージ枯渇** | part/checkpoint 書込失敗 | 25万体は part parquet が巨大化 [要確定 ストレージ容量]。古い part は納品後アーカイブ削除 |

- **日次バックアップ**は本選ノードでは `ops/backup-daily.ps1` がローカル Windows 用なので**そのままは使えない**。
  本選(Linux 想定)では watchdog の `--keep-backups 3` 世代コピー + 別ディスク/別マシンへの `rsync` を
  日次 cron で回す運用に読み替える [要確定 ネット/外部ストレージ]。

### §5.4 セキュリティ・データ持込制限

- **API キー**: 本番は vLLM(ローカル自ホスト)なので外部 API キーは原則不要。混成(mixed-api)を使う場合のみ
  **環境変数で渡す**(config・リポジトリにハードコードしない)。memory `devlog-protocol` の「セキュリティ確認後にリンク」。
- **ODPT 再配布制限**(memory `github-repo`・`odpt-integration.md`): 公共交通オープンデータの**生データは再配布不可**。
  `data/transit_odpt.json` は**加工物**として扱い、成果物・公開物に ODPT 生データを含めない。出典表記
  「公共交通オープンデータセンター(ODPT)のデータを加工して作成」を維持(`production.yaml` L44-45 に既記)。
- **データ持込**: 本選ノードへ持ち込むのは加工済み資産のみ。個人情報を含むペルソナは合成(実在人物でない)。
- **リポジトリは非公開**(memory `github-repo`)。本選ノードへの clone 時も公開先に出さない。

---

## §6 未確定事項一覧(スペック確定時にユーザーへ聞くこと)

**[要確定]** を集約。ユーザーから回答が来たら本書の該当箇所を差し替える。

| # | 質問 | なぜ必要か(どの判断に効くか) | 現時点の仮置き |
|---|---|---|---|
| 1 | **GPU の正確な種別**(RTX A5000 24GB か RTX 5000 Ada 32GB か等) | §1 の行選択・量子化要否(24GB なら AWQ ほぼ必須) | 168GB÷7=**24GB/A5000級**と逆算 |
| 2 | **GPU 基数**(7 で確定か / 4・8 の可能性) | §1 のレプリカ数・集約 req/s | **7**(公表値) |
| 3 | **ホスト RAM 容量** | 25万体・100万プール・observer 全件展開が載るか(§4.3・§5.3) | [要確定]・25万体は数百 GB 級の懸念 |
| 4 | **ストレージ容量・種別**(NVMe か) | part parquet・checkpoint・納品物の総量。25万体×10日は巨大 | [要確定] |
| 5 | **ネット接続**(外部 DL 可否・帯域) | モデル/データを事前持込するか本選 DL か(§4.4) | 事前オフライン持込を仮定 |
| 6 | **利用可能時間帯**(24h 占有か / 夜間停止か) | 連続ラン設計・watchdog の再開前提・10日 wall の実効時間 | 24h 連続を仮定 |
| 7 | **占有か共有か**(1ノードを他チームと共有するか) | GPU メモリ・スケジューリングの前提。共有なら max-num-seqs 保守化 | 1チーム1ノード占有を仮定 |
| 8 | **OS / 事前ソフト**(Linux か・vLLM 版・CUDA 版・Docker か) | 起動フラグ形(speculative-config の新旧・§launch script)・環境構築手順 | Linux・vLLM 新版を仮定 |
| 9 | **障害時の扱い**(募集要項 L118 が「調整中」) | GPU 落ち時の補償・再割当。checkpoint/resume 設計の余裕度 | 自力復旧(§5.3)を前提 |
| 10 | **プール・ローテーション機構を実装するか**(persona-pool の未実装部) | 100万プール→同時25万の日次入替を回すか、同時=固定で回すか | 未実装=同時固定を仮定 |
| 11 | **engine 最適化(streaming 化)の実装可否**(§4.2) | 25万体の可否を直接決める。src 変更を伴うため合意が要る | ユーザー合意後に着手 |

---

## 付録: 本命シナリオの初動サマリ(スペックが公表値どおりだった場合)

**A5000級 24GB × 7・単一ノード・10日** が確定したら、以下を順に実行するだけ:

1. Day-0: §2 の 5 項目を実測(特に ② req/s と ④ c_nonllm)。24GB なので 8b は **AWQ/INT4** を第一候補。
2. §2-⑤ で `estimate_runtime.py --fleet vllm-7gpu-a5000` に実測値を入れ、**1.1〜1.25 シミュ日/24h を満たす最大 N** を本番規模に採用。
   - c_nonllm が lean(≤0.0024)なら 25万体に挑戦。full 寄り(>0.006)なら 5万〜10万体に着地(§3.1 縮退線)。
3. `conf/production.yaml` の model ブロックを `finals-vllm7.yaml` の vLLM 配線へ差し替え、`--env env/shibuya` で起動。
4. `scripts/watchdog.py`(checkpoint_every=144・日次)で本番ラン。**無停止続行・異常値のみ確認・part 結合で日次部分納品**。
5. 遅延したら §3.1 の縮退線に従い**まずシミュ日数を削る**(体数は維持)。OOM/observer 破綻のときだけ体数を落とす。
