# スケール実現可能性 — 何体を何日/日で回せるか(vLLM 7GPU 試算)

- 作成: 2026-07-19 / 担当: Opus 4.8(試算+ツール拡張) / 種別: **試算 + 前提の正直な明記**
- 目的: 本番方針「**エージェント数の確保 > 実行時間**」の下で、7GPU vLLM 1ノードで
  **N ∈ {1,000〜100,000} を 1 シミュ日あたり何分・24h で何シミュ日** 回せるかを、
  較正済み `scripts/estimate_runtime.py` と web リサーチした vLLM スループットから見積もる。
- 較正の中心: [`runs/demo_event_200a3d`](../../runs/demo_event_200a3d)(200体・3日・qwen3:4b・ローカル ollama)。
- 関連: [`docs/plans/compute-optimization.md`](../plans/compute-optimization.md) / [`docs/research/agent-lod-deepdive.md`](agent-lod-deepdive.md) / [`docs/research/scale-audit-100days.md`](scale-audit-100days.md) / [`ops/launch-vllm-finals.ps1`](../../ops/launch-vllm-finals.ps1)

> **一行の結論(先出し)**: この N 域では **LLM 推論は律速ではない**(A100×7 で最大 ~67分/シミュ日)。
> 律速は **Python シミュ本体(非LLM step 処理)** で、実測は **0.00183〜0.060 秒/agent-step の
> 33 倍レンジ**にあり、これが 5,000体超の可否をほぼ決める。LOD 前景比率は LLM 側だけを削るので、
> 非LLM が支配し始める規模では効きが薄い。**先に engine を最適化 → 次に LOD**、が順序。

---

## §1 前提と較正

### 1.1 較正定数(`runs/demo_event_200a3d` 実測)
| 記号 | 値 | 由来 |
|---|---:|---|
| N_calib | 200 | agents.json |
| C1(day1 実呼数) | 4,293 | l1b_llm.parquet(日別 [4293, 4493, 4375]) |
| α(体数スケール指数) | 1.209 | 15体アンカー(187.5呼/日)との log-log |
| g(日成長率) | 0.95%/日 | 日別呼数の幾何成長 |
| sec/call(ollama 逐次) | 3.1 | qwen3:4b ローカル実測 |

### 1.2 ★決定的な非対称: deliberate は飽和・plan/reflect は線形
`runs/demo_event_200a3d` の呼種内訳(l1b_llm.parquet の `purpose`):

| 群 | 呼種 | 3日合計 | 割合 | スケール挙動 |
|---|---|---:|---:|---|
| **deliberate 系(予算ゲート)** | reply/social/novel_place/solo/post/dm | 12,229 | **92.9%** | `lod.max_llm_per_step=300` で **step 上限に飽和**(大 N で N 非依存) |
| **非ゲート** | plan(419)+reflect(513) | 932 | 7.1% | budget を通らず **N にほぼ線形**(体あたり ~一定) |

これは [`scale-audit-100days.md`](scale-audit-100days.md) §3.1 の「LOD 予算は deliberate だけを cap し、
planning/reflection は cap しない」と一致する。**帰結が試算を根底から変える**:

- 200体では deliberate ≈ 28/step で cap(300)に遠い → α=1.209 が素直に効く。
- cap が binding になるのは **~1,500体**(28×(N/200)^1.209 = 300)。
- それ以上で α=1.209 を **素で外挿すると deliberate を桁で過大評価**する:
  10,000体で ~10.7倍、100,000体で ~159倍。よって **本試算は既定で予算ゲート付きモデル**を使う
  (`estimate_runtime.py --cap-per-step 300`)。素の α は「上限値(over-estimate)」として `--cap-per-step 0` で出せる。

モデル(ツール実装 `predict_calls_capped`):
```
calls/day(N) = min( C1·0.929·(N/200)^1.209 , 300·144 )   ← deliberate(飽和)
             +      C1·0.071·(N/200)^1.0                   ← plan+reflect(線形)
             ) × λ_LOD                                     ← LOD 実効呼数倍率
```

---

## §2 vLLM スループット(web リサーチ結果)

qwen3:4b 級(dense, bf16)を**プロンプト ~1,300tok 入力 + ~320tok 生成**という本シミュの呼形状で回す前提。

> ★**捏造回避の明記**: 「4B × 1300/320 の *measured* な公開値」は見つからなかった。下の A100/H100/A5000 の
> req/s は **近傍実測 + FLOP/帯域モデルからの推定**であり measured ではない。1,300tok プロンプトは
> prefill 支配(prefill FLOP ≈ decode の ~4倍)なので、decode 支配の短プロンプト実測(100/600 等)は直接転用不可。
> **本選機で必ず実測して置換**すること: `vllm bench serve --random-input-len 1300 --random-output-len 320`。

### 2.1 フリートプリセット(`estimate_runtime.py --fleet`)
| プリセット | GPU | req/s/GPU(推定) | ×7 集約 | 根拠 / レンジ |
|---|---|---:|---:|---|
| `vllm-7gpu-a100` | A100 80GB×7 | **8**(range 6–12) | 56 req/s | Gemma-3-4B ≈ 3,385 out tok/s@A100-40GB(100/600)+ FLOP モデル |
| `vllm-7gpu-h100` | H100 80GB×7 | **14**(range 10–20) | 98 req/s | A100比 ~1.7x(HBM3 3.35 vs 2.0 TB/s) |
| `vllm-7gpu-a5000` | A5000 24GB×7 | **3**(range 2–5) | 21 req/s | 本選想定機・4bit・A100比 ~0.35x(帯域 768 GB/s) |
| `ollama-local` | (逐次) | — | 1/3.1s | ローカル実測 3.1 秒/呼・並列なし |

sec/呼 = 1 ÷(req/s/GPU × 7 × spec × apc)。overhead(既定15%)はオーケストレーション遅延として別掛け。

### 2.2 タダ飯レバー(speculative / prefix cache)
| レバー | 効果(採用値) | レンジ | 出典と注意 |
|---|---|---|---|
| **speculative decoding**(`--speculative`) | **×1.15** | 1.0–1.3 | vLLM blog は QPS≈1 で最大 **2.8x** だが、それは *decode 支配・低並列* の数字。本シミュの**飽和運転(高並列)では逆に減速**もある。かつ 1,300/320 は prefill 支配で spec は decode しか速くしない → **2x は当てにしない** |
| **prefix cache / APC**(`--prefix-cache`) | **×2.2** | 1.8–3.0 | ペルソナ+履歴の共有接頭辞が長いほど効く(prefill を直接削る)。SqueezeBits 実測 +32%(中プロンプト)〜長接頭辞で数倍。**★共有が無いと逆に −37%** → プロンプト構築で接頭辞を実際に共有させることが条件 |

> 量子化: FP8 は 4B/8B のような小モデルでは decode が帯域律速で **~1.1x** 程度。INT4/AWQ は concurrency>1 で
> **むしろ低下しうる**(dequant オーバヘッド)= 速度ではなく **VRAM 節約**の手段。req/s は量子化で上げない前提。

### 2.3 出典
- databasemart vLLM GPU ベンチ [A100-40GB](https://www.databasemart.com/blog/vllm-gpu-benchmark-a100-40gb) / [A100-80GB](https://www.databasemart.com/blog/vllm-gpu-benchmark-a100-80gb) / [H100](https://www.databasemart.com/blog/vllm-gpu-benchmark-h100) / [RTX4090](https://www.databasemart.com/blog/vllm-gpu-benchmark-rtx4090)(Gemma-3-4B/7B/8B の out tok/s)🔶二次
- [Koyeb GPU LLM ベンチ(Qwen2.5-7B/Llama-3.1-8B × L40S/A100/H100)](https://www.koyeb.com/docs/hardware/gpu-benchmarks)🔶二次
- vLLM blog [Speculative Decoding up to 2.8x(2024-10-17)](https://blog.vllm.ai/2024/10/17/spec-decode.html)(★高QPSで減速の明記あり)/ [EAGLE 3.1(2026-05-26)](https://vllm.ai/blog/2026-05-26-eagle-3-1)
- vLLM docs [Automatic Prefix Caching](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/) / [SqueezeBits APC 分析](https://blog.squeezebits.com/vllm-vs-tensorrtllm-12-automatic-prefix-caching-38189)(+32% / 共有無しで −37%)
- vLLM GitHub [issue #20469(Qwen3-14B-AWQ が concurrency>1 で低下)](https://github.com/vllm-project/vllm/issues/20469)

---

## §3 試算表 — LLM 側(`vllm-7gpu-a100` / 予算ゲート込み)

**セル = 「1シミュ日あたりの分」+「24h で回せるシミュ日数」**。列 (a)全員フルLLM / (b)前景10% / (c)前景3%
(背景係数 0.1=前景の1/10呼)。**非LLM は §4 に分離**(ここは LLM のみ)。day1 代表値(長期ランは §5 の g で漸増)。

### (spec なし)
| N | (a) full | (b) 前景10% | (c) 前景3% |
|---:|---|---|---|
| 1,000 | 10.1分 / 143/日 | 1.9分 / 753/日 | 1.3分 / 1126/日 |
| 5,000 | 17.4分 / 83/日 | 13.2分 / 109/日 | 8.8分 / 163/日 |
| **10,000** | **20.0分 / 72/日** | **15.8分 / 91/日** | **15.4分 / 93/日** |
| 20,000 | 25.2分 / 57/日 | 16.8分 / 86/日 | 16.1分 / 89/日 |
| **50,000** | **40.8分 / 35/日** | **19.7分 / 73/日** | **18.1分 / 80/日** |
| 100,000 | 66.8分 / 22/日 | 24.7分 / 58/日 | 21.4分 / 67/日 |

### (spec あり ×1.15)
| N | (a) full | (b) 前景10% | (c) 前景3% |
|---:|---|---|---|
| 1,000 | 8.8分 / 164/日 | 1.7分 / 865/日 | 1.1分 / 1295/日 |
| 5,000 | 15.1分 / 95/日 | 11.5分 / 126/日 | 7.7分 / 188/日 |
| **10,000** | **17.4分 / 83/日** | **13.7分 / 105/日** | **13.4分 / 107/日** |
| 20,000 | 21.9分 / 66/日 | 14.6分 / 99/日 | 14.0分 / 103/日 |
| **50,000** | **35.5分 / 41/日** | **17.2分 / 84/日** | **15.7分 / 92/日** |
| 100,000 | 58.1分 / 25/日 | 21.5分 / 67/日 | 18.6分 / 77/日 |

**読み**: cap のおかげで LLM 側は 100,000体・全員フルでも **~67分/シミュ日(22シミュ日/24h)**。
前景3%で ~21分。spec は ~13〜15% 短縮。**この域では LLM は"回る"**。prefix cache(×2.2)を足せば更に半減。

- **フリート換算**(同 N・full・spec なし・10,000体 = 20.0分基準):
  H100×7 → **11.4分 / 126/日**(≈0.57倍)、A5000×7 → **53.3分 / 27/日**(≈2.66倍)。
  本選機が A5000 級なら LLM 時間は上表の **~2.7倍**として読むこと。

**再現コマンド**(表と一致・acceptance):
```bash
python scripts/estimate_runtime.py --agents 10000 --days 1 --calib runs/demo_event_200a3d \
    --fleet vllm-7gpu-a100                       # → 20.0分 / 72.0 シミュ日/日
python scripts/estimate_runtime.py --agents 50000 --days 1 --calib runs/demo_event_200a3d \
    --fleet vllm-7gpu-a100 --lod-fg-ratio 0.03   # → 18.1分 / 79.6 シミュ日/日
python scripts/estimate_runtime.py --agents 10000 --days 1 --calib runs/demo_event_200a3d \
    --fleet vllm-7gpu-a100 --speculative         # → 17.4分 / 82.8 シミュ日/日
```

---

## §4 非LLM(Python step 処理)— 実はこちらが律速

`estimate_runtime.py --nonllm-profile {lean,full}`。**LOD でも spec でも減らない**(全 N 体の物理 step は必ず回る)。

### 4.1 2 つの実測アンカー(33倍レンジ)
| プロファイル | 秒/agent-step | 由来 |
|---|---:|---|
| **lean** | **0.00183** | mock 300体×100日=132分([compute-efficiency.md](compute-efficiency.md))= LLM スタブ化の Python 下限 |
| **full** | **0.060** | `runs/demo_event_200a3d` の実測 wall 分離(下記) |

**full の分離手続き**(依頼の「l1b呼数×3.1s vs 総wall時間」): checkpoint mtime から
ckpt-000144 → ckpt-000432 = **515.7分**(シミュ日2+3の wall)。同区間の LLM 逐次 = (4493+4375)×3.1s = **458.2分**。
差 = **57.5分 / 2日 = 28.7分/シミュ日 = 0.060 秒/agent-step**(全チャネル+イベント記録IO込み)。
= このランは **ほぼ逐次**(LLM が wall の ~89%)で、非LLM は ~11%。ただし LLM が cap で頭打ちになる大 N では
この 11% が**逆転**する。

### 4.2 非LLM だけの試算(LOD/spec 非依存)
| N | lean(0.00183) | full(0.060) |
|---:|---|---|
| 1,000 | 4分 / 328/日 | 144分 / 10.0/日 |
| 5,000 | 22分 / 66/日 | 720分 / 2.0/日 |
| **10,000** | **44分 / 33/日** | **1,440分(24h) / 1.0/日** |
| 20,000 | 88分 / 16/日 | 2,880分 / 0.5/日 |
| **50,000** | **220分 / 6.6/日** | **7,200分 / 0.2/日** |
| 100,000 | 439分 / 3.3/日 | 14,400分 / 0.1/日 |

**読み**: **10,000体で既に lean 非LLM(44分)> full-LLM(20分)**。full プロファイルなら 10,000体で
**非LLM だけで 1シミュ日 = 24時間**。→ **N≥10,000 では非LLM が支配**し、LLM 高速化(spec/apc/LOD)は
体感を変えない。

### 4.3 非LLM の N スケール — O(N) か O(N²) か(要注意)
- **知覚**([`src/society/world/perception.py`](../../src/society/world/perception.py)): 全対全 O(N²) は空間グリッド索引で
  回避済み(cell=perception_radius・近傍9セルのみ走査)。**密度が有界なら ~O(N)**。ただし
  **固定面積に N を増やすと密度が上がり**、speaker あたり hearer 数が増える → 局所的に **O(N²) へ劣化**しうる。
  上表は**線形前提**なので、混雑シナリオでは非LLM が更に悪化する側の不確実性を持つ。
- **イベント記録**: 200体×3日で 238,993 events(2.77 events/agent-step)。相互作用が超線形に増えれば
  イベント量も超線形 → 非LLM 超線形化。
- **別ボトルネック**([`scale-audit-100days.md`](scale-audit-100days.md) §4 が既に警告): `measure.load_events` の全件 RAM 展開
  (10⁸件で ~100-200GB=ハード破綻)、`network_windows` の O(窓×E)、`export_3d` の T×N=1.44×10⁸ セル、
  L3 snapshot の全 agent JSON 化(~3GB)。**これらは wall だけでなくメモリの壁**で、N を上げる前に
  ストリーミング化が必須。**本試算の非LLM 秒/agent-step は step ループのみ**で、これら観測/出力の破綻は含まない。

---

## §5 前提と不確実性(正直な明記)

1. **α 外挿**: 1.209 は 15–200体較正。cap でこの外挿の暴走は抑えたが、**cap 未満の 1,000–1,500体域**では
   まだ α に依存。deliberate 割合 92.9% と uncapped_alpha=1.0(plan/reflect 線形)は **単一ラン由来の仮定**。
2. **フリート req/s は全て推定**(§2 冒頭)。measured ではない。±50% は覚悟。本選 `vllm bench serve` で置換。
3. **speculative ×1.15・apc ×2.2 は控えめ既定**。飽和運転では spec が 1.0 割れもある(vLLM blog)。apc は接頭辞共有が前提。
4. **非LLM 0.00183〜0.060 の 33倍レンジ**が最大の不確実性。真値は有効チャネル数(vision/SUMO/群衆視覚等)と
   観測IO の最適化度に依存。**この 1 数字が 5,000体超の可否を決める**ので、**本番プロファイルで mock 実測して確定**が最優先。
5. **メモリ/状態管理は別の壁**(§4.3)。wall が回っても RAM で落ちる規模がある。
6. **g(日成長)**: 表は day1 代表値。100日連続なら deliberate は cap 済で不変だが、plan/reflect と小 N の deliberate は
   (1+g)^(d-1) で漸増(g=0.95%/日 → day100 は day1 の ~2.5倍)。**長期ランの後半は上表より重い**。
7. **LLM/非LLM は直列前提(保守)**。単一ノード Python オーケストレータの step バリアで直列とみなした。
   非LLM を GPU 推論と**オーバーラップ**できれば短縮余地あり(未実装・未検証)。

---

## §6 結論 — 逆算「平均同時滞在 X万人を LOD いくつで何日/日」

per-simday の壁時間は LLM と非LLM の**和**(直列):
```
T_simday(N, fg, spec, 非LLM) = C_calls(N,fg) / R_eff(spec)   +   144·N·c_nonllm
  C_calls(N,fg) = min( 3988·(N/200)^1.209·λ , 43200 ) + 305·(N/200)·λ,   λ = fg + (1−fg)·0.1
  R_eff(A100)   = 48.7 呼/s(spec なし) / 56.0 呼/s(spec あり)   ← =56·1.15÷1.15overhead 換算
  c_nonllm ∈ [0.00183(lean), 0.060(full)]
シミュ日/24h = 86400 / T_simday
```

**支配項は非LLM**。N≥10,000 では `T ≈ 144·N·c_nonllm` に近く、LOD(fg)は C_calls しか削らないので効きが薄い。
**非LLM 側の可否ライン**(LLM を無視した上限):
```
D シミュ日/日を出すには  c_nonllm ≤ 600 / (N · D)
```

### 代表シナリオ(A100×7・spec なし・full-LLM=fg1.0)
| 目標 X | N | 非LLM lean(0.00183) | 非LLM full(0.060) |
|---|---:|---|---|
| **1万人** | 10,000 | 64分/日 → **22.5シミュ日/24h**(100日=4.4日) | 1,460分/日 → **1.0/24h**(100日=101日) |
| **5万人** | 50,000 | 260分/日 → **5.5シミュ日/24h**(100日=18日) | 7,241分/日 → **0.2/24h**(100日=503日) |

(前景3%にしても lean 10,000体は 59分→24シミュ日/24h、5万体は 238分→6.1/24h と**ほぼ変わらない**=非LLM 律速の証拠。)

### 実務の逆算(本選 10日 wall・100シミュ日を回す = 10シミュ日/24h 必要)
- **必要な非LLM 予算**: `c_nonllm ≤ 600/(N·10)`。→ 10,000体なら ≤0.006、**50,000体なら ≤0.0012 秒/agent-step**
  (= 現状 lean 0.00183 すら上回る速さが要る)。
- **したがって**:
  - **10,000体 × 100日**: lean エンジンなら **可**(4.4日で完走)。full エンジンだと不可(101日)→ **engine 最適化が前提条件**。
  - **50,000体 × 100日**: lean でも 18日 > 10日 wall → **engine を lean 未満へ最適化 + snapshot/observer のストリーミング化**が必須。LOD だけでは届かない。
  - **100,000体**: LLM は回る(§3)が、非LLM が lean でも 439分/日 → **engine を桁で最適化しない限り 100日は非現実的**。「数万人 × 短シミュ日」か「1万人 × 100日」が現実的な着地。

**要するに**: 「エージェント数 > 実行時間」を活かすなら、**投資先は LLM 推論(既に軽い)ではなく Python シミュ本体
(step ループ + 観測/出力パイプラインのストリーミング化)**。LOD 前景比率は LLM が律速に戻る
(engine を lean 未満へ最適化した後の)局面で初めて効く**第二レバー**。まず [scale-audit §4] の破綻点を潰し、
非LLM 秒/agent-step を本番プロファイルで実測して 0.00183〜0.060 のどこかを**確定**することが、
全ての試算の前提になる。
