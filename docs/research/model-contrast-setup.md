# model×k 対照ランの実行構成 — abliterated/base 対照の実在確認・品質裏取り・ラン設計

- 作成: 2026-07-12 / 担当: Opus(リサーチ・**src/conf/data 非編集**・ダウンロードも実行もしない・調査と文書作成のみ)
- 目的: **SimBench の alignment–simulation tradeoff**(instruct 化がシミュレーション能力を下げる)と、本シムの観測課題**「世界改変ツール0行使 = RLHF 抑制仮説」**を切り分ける **model×k 対照実験**の、**実行可能な構成**を固める。現行運用モデル `qwen3:4b`(ollama)に対する対照候補(abliterated / base / 上位)の**実在をライブラリ実ページで確認**し(ダウンロードはしない)、能力低下と無行動を混同しないための最小ベンチ、ラン本数・呼数・GPU 時間・キャッシュ分離の注意、推奨構成と pull コマンドまで落とす。
- 前提資料(必読・既読): `docs/research/llm-model-selection.md`(§3.4 構成C = model×k、§2.5 ライセンス、§3.0 量子化)、`docs/lit/infra__model-choice-conflict.md`(abliterated 対照の設計・huihui 劣化警告)、`docs/calibration/calibration-20260709.md`(qwen3:4b/8b の実測呼数・行動分布)、`docs/research/world-change-motivation.md`(ツール0使用の実証)。
- 方針: ollama タグの実在は **library の実ページ確認を根拠**とする。未確認は「未確認」と明記(捏造禁止)。

---

## 0. サマリ(推奨構成と pull コマンド)

- **切り分けの核**: 現行 `qwen3:4b`(instruct)⇔ **同一系列 abliterated**(RLHF 拒否・同調を除去)の対を、**同一シード・同一ペルソナ**で `k{free, off}` に交差させ、**ツール行使率・free_action 率・提案/設立数・発話 distinct-2・R²ext** の差を見る。k* がモデルで消える/立つなら「アライメント固有アーティファクト」。
- **推奨対照(実在確認済み)**: `huihui_ai/qwen3-abliterated:4b-v2-q4_K_M`(2.5GB・Q4_K_M・40K ctx・Apache-2.0・publisher huihui_ai・209.3K pulls)。現行 `qwen3:4b`(既定 Q4_K_M・2.5GB)と**量子化・サイズ・hybrid thinking を揃えた**最もクリーンな対。
- **base 極は任意(第3条件)**: `Qwen/Qwen3-4B-Base`(HF 公式・Apache-2.0・pretraining stage・chat template なし)。**instruct 形式なし→JSON 行動出力が崩れるリスク大**。ollama 用の公式 base GGUF は**未確認**。採用するなら vLLM + guided_json 前提で別途検討。
- **pull コマンド(実行はしない・裏取り後に手動で)**:
  ```bash
  # 対照 abliterated(推奨・quant/size を現行と一致)
  ollama pull huihui_ai/qwen3-abliterated:4b-v2-q4_K_M     # 2.5GB
  # 上位対照(任意)
  ollama pull qwen3:8b                                     # instruct 上位(5.2GB 級)
  ollama pull huihui_ai/qwen3-abliterated:8b-v2-q4_K_M     # 5.0GB
  # 現行(既に運用中・参考)
  ollama pull qwen3:4b                                     # 2.5GB(基準 instruct)
  ```
- **最優先の注意**: huihui 系 abliteration は**能力劣化が入りうる**(`infra__model-choice-conflict.md`: huihui Qwen3.6-27B abliterated で TruthfulQA −12.65 / GSM8K −5.68)。**§3 の最小ベンチで「無行動が RLHF 除去由来か能力低下由来か」を必ず裏取り**してから k* 解釈に使う。

---

## 1. 何を切り分けるのか — SimBench tradeoff と RLHF 抑制仮説

- **SimBench(arXiv:2510.17516)の確認事実**: instruction tuning は **低エントロピー(合意的)問題では性能を上げ、高エントロピー(多様)問題では下げる**。因果分析では「有益な instruction-following 効果 vs 有害な entropy-reduction 効果」の差し引き。シミュレーション能力は**知識集約推論(MMLU-Pro)と最も強く相関(r=0.939)**、モデルサイズに log-linear、推論時 compute ではスケールしない。最良でも 40.80/100 の中程度の忠実度。
  - ⚠️ **数値の訂正/未確認**: 依頼文の「alignment–simulation tradeoff r=−0.942」は、**アブストラクト水準では確認できなかった**。確認できたのは MMLU-Pro との**正の** r=0.939 と、tradeoff の**定性的機構(entropy-reduction)**である。r=−0.942 という負相関は本文中の別指標(chat/alignment スコア等)の可能性があるが**未確認**。本ラン設計は**定性的 tradeoff(instruct ほど多様性が縮む)を前提に組む**(具体数値には依存しない)。
- **本シムの観測課題**: 実 LLM 3ランで**5つの世界改変ツールが 2,654回の中立提示に対し0使用**(`world-change-motivation.md`)。診断は2要因の交絡 — (i) **内部状態の飽和**(efficacy 天井/grievance 床=モデル非依存の設計問題)、(ii) **RLHF instruct の受動性・同調**(モデル依存。SimBench の entropy-reduction / peer 同調 最大85.5%)。
- **切り分けの論理**: 飽和(i)を機構側で緩めた上で、**同一系列の instruct ⇔ abliterated を model×k で交差**させれば、(ii) の純粋なモデル効果(アライメントが世界改変・異論・多様性を潰すか)を測れる。SimBench は外部ベンチでの相関を示すだけだが、**本シムは「渋谷という身体を持つ世界での実際の行動(ツール行使・提案・発話多様性)」で tradeoff を内製検証できる**のが独自性。

---

## 2. 対照候補の実在確認(library 実ページ・HF を確認。ダウンロードはしない)

現行運用モデル = **`qwen3:4b`**(ollama、hybrid-thinking Qwen3-4B、既定 Q4_K_M ~2.5GB。本シムは `model.reflect_think=true` で qwen3 の `enable_thinking` seam に依存 — 対照も**hybrid thinking を保つ版**が望ましい)。

### (a) abliterated 版 — ✅ 実在確認

- **ollama**: `huihui_ai/qwen3-abliterated`(publisher **huihui_ai**、**209.3K pulls**、based on Qwen/Qwen3、ライセンス **Apache-2.0**)。確認できた 4B/8B タグ:

  | タグ | サイズ | 量子化 | ctx | 系列 |
  |---|---|---|---|---|
  | `:4b` / `:4b-v2` | 2.5GB | 既定(Q4_K_M 相当) | 40K | hybrid(現行 qwen3:4b と同系) |
  | **`:4b-v2-q4_K_M`** ★推奨 | 2.5GB | Q4_K_M | 40K | hybrid |
  | `:4b-v2-q8_0` | 4.3GB | Q8_0 | 40K | hybrid |
  | `:4b-v2-fp16` | 8.1GB | FP16 | 40K | hybrid |
  | `:4b-instruct-2507-q4_K_M` | 2.5GB | Q4_K_M | 256K | **2507 split(instruct 専用・別系列)** |
  | `:4b-thinking-2507-q3_K_M` | 2.1GB | Q3_K_M | 256K | **2507 split(thinking 専用・別系列)** |
  | `:8b` / `:8b-v2-q4_K_M` | 5.0GB | Q4_K_M | 40K | hybrid(上位対照) |

- **HF 出所(裏取り可能)**: `huihui-ai/Qwen3-4B-abliterated` および改良版 `huihui-ai/Huihui-Qwen3-4B-abliterated-v2`(手法: refusal 方向の abliteration。「crude, proof-of-concept」「安全最適化なし・研究/統制環境向け」と自認)、`huihui-ai/Qwen3-8B-abliterated`。
- **推奨**: **`:4b-v2-q4_K_M`**。理由 = 現行 `qwen3:4b` と**量子化(Q4_K_M)・サイズ(2.5GB)・hybrid thinking・40K ctx を一致**させ、能力差を k* の交絡にしない(`infra__model-choice-conflict.md` の「同一系列・同一量子化・同一手法で統一」に合致)。
- **注意(系列の混同回避)**: `4b-instruct-2507` / `4b-thinking-2507` は **thinking と instruct を分離した別系列(256K ctx)**。現行 `qwen3:4b`(hybrid・40K)とは前提が異なり `reflect_think` seam の挙動も変わりうるので、**対照には使わない**(v1/v2 の hybrid を使う)。
- **信頼性の留保**: huihui は著名な abliteration 発行者だが、**能力劣化の実測がモデルごとにバラつく**(27B 版で TruthfulQA −12.65 / GSM8K −5.68 の報告)。劣化最小の **Heretic 手法版は ollama 上の 4B には見当たらず**(未確認)、使うなら自前量子化・GGUF 変換が要る。→ §3 のベンチで裏取り必須。

### (b) base 版 — ✅ HF 実在 / ollama 公式 base GGUF は ⚠️ 未確認

- **HF**: `Qwen/Qwen3-4B-Base`(**公式**・**Apache-2.0**・training stage = **Pretraining**・**chat template なし**・safetensors BF16)。instruction tuning・会話最適化なしの純ベース。実在確認済み。
- **ollama で使える形(GGUF)**: **公式の base GGUF は未確認**。`Qwen/Qwen3-4B-GGUF`(Q4_K_M 2.5GB 等)は**post-trained(instruct)版の GGUF であって base ではない**。HF ページには「Browse Quantizations(llama.cpp/Ollama/LM Studio/Jan)」のリンクがあるがコミュニティ量子化の域で、base の公式 GGUF は確認できていない。
- **instruct 形式なしで JSON 行動出力が成立するかのリスク評価(高リスク)**:
  - base は chat template・stop 制御・指示追従が弱く、**本シムの厳格 JSON(`parse_action` の13キー)を安定に出せない懸念が大**。fallback 率が跳ね上がると「無行動 = RLHF 除去の効果」と「無行動 = base が指示に従えないだけ」が**致命的に交絡**する。
  - 緩和策: `docs/lit/infra__model-choice-conflict.md` §設計帰結3 の通り **few-shot 例示 + guided decoding(JSON 文法制約)**。ollama は guided decoding が弱いので、**base を入れるなら vLLM(`response_format`/guided_json)前提**で、ollama スモークとは別枠にする。
- **結論**: base は「raw base 極」として**理論的価値は高いが実務コストと交絡リスクが高い**。**第1段は instruct⇔abliterated の2極に絞り、base は vLLM 環境が整ってからの第3条件(任意)**とするのが安全(llm-model-selection §3.4 の「raw-base 極を入れるなら別系列追加・系列交絡を明記」と整合)。

### (c) 上位モデル対照 — ✅ 実在確認

- **instruct 上位**: `qwen3:8b`(ollama 公式・hybrid・実測で fallback 0%・qwen3:4b とほぼ同一行動分布 = `calibration-20260709.md`)。
- **abliterated 上位**: `huihui_ai/qwen3-abliterated:8b-v2-q4_K_M`(5.0GB・Q4_K_M・40K・hybrid)。8B 対で「モデル規模 × アライメント」の2×2 も組める。
- **新系列(任意)**: `huihui_ai/qwen3.5-abliterated:4B`(HF `huihui-ai/Huihui-Qwen3.5-4B-abliterated`)。ただし現行 4b と系列が違う(3.5)ので、対照の第一選択は **同系列 qwen3 の 4b/8b abliterated** に置く。

---

## 3. 品質裏取りの最小ベンチ(能力低下と無行動を混同しない)

**目的**: abliterated/base の「ツール0行使・低い提案数」が **RLHF 抑制の除去による真の変化**なのか、単なる**能力低下(指示追従崩れ)**なのかを弁別する。`docs/research/llm-model-selection.md` の**構成C(model×k)**および §1.2/§1.5 の実測方針と整合させ、**本シムのプロンプト形式そのもの**で測る(汎用ベンチでなく in-domain)。

**最小ベンチ(1日スモーク・15体・各モデル、mock でなく実 LLM)**:

| 指標 | 測り方 | 合格の目安 | 何を弁別するか |
|---|---|---|---|
| **JSON 遵守率 / fallback 率** | `parse_action` 成功率(= 1 − routine フォールバック率)。既存 summary.json / L1b から | instruct 実測 **fallback 0%** が基準。abliterated が数%以内なら能力健全 | 能力低下の一次シグナル。**fallback 急増 = 無行動を「行動できない」に読み替えるべき危険信号** |
| **発話多様性 distinct-2** | speak/post テキストの bi-gram 種類比(既存の多様性監視) | instruct と同水準〜以上 | abliterated が entropy-reduction を外して**多様性が上がる**なら仮説と整合。**下がるなら能力低下** |
| **発話の言語健全性** | 日本語崩れ・反復・空応答の目視/簡易スコア(15体×1日) | 崩れ<数% | base で特に要チェック(chat template なしの崩壊) |
| **内省の JSON 健全性** | reflect の `{summary, salient[], belief}` 遵守率(reflect_think=true) | 遵守 | hybrid thinking seam が abliterated で保たれているかの確認 |
| **呼数・所要時間** | summary.json(15体×1日 ≈ 118呼/6.4分@qwen3:4b) | モデル間で呼数がほぼ一定 | compute が条件間で揃っているかの担保 |

**判定ロジック**: abliterated が **(JSON 遵守 ≈ instruct) かつ (distinct-2 ≥ instruct)** を満たしつつ**ツール行使/提案が変化**したら → その差は「RLHF 抑制の除去」と解釈してよい。**JSON 遵守が落ちる/日本語が崩れる**なら → 能力低下の交絡として k* 解釈から除外(またはより劣化の少ない版・Heretic 版へ切替)。この 1 日スモークは `validation-runs-short` 準拠(全日 LLM ランはしない)。

---

## 4. ラン設計(呼数・GPU 時間・シード・キャッシュ・判定指標)

### 4.1 マトリクス

- **daily プロファイル 15体 × 2日** を、**{instruct=qwen3:4b, abliterated=huihui_ai/qwen3-abliterated:4b-v2-q4_K_M}（, base 任意）** × **k{free, off}** で回す。
- セル数: **2モデル × 2 k = 4セル**(base を足すと 6セル)。上位対照を足すなら 8セル。

### 4.2 呼数・GPU 時間見積り

- 既知(依頼・実測): **instruct 15体×2日 ≈ 300–340呼・17–20分**(参考: `calibration-20260709.md` の qwen3:4b は 15体×1日=118呼/6.4分、15体×3日=413呼/21分 → 2日は約 275–300呼/約13分のオーダー。依頼値 17–20分/300–340呼を上限側の設計値として採用)。
- **4セル ≈ 1,200–1,360呼 / 約 60–80分**(ollama 単一 GPU で逐次)。**6セル ≈ 1,800–2,040呼 / 約 90–120分**。4B・単一 GPU で完結する軽量実験(A5000 なら余裕。本選 vLLM 艦隊は不要)。
- abliterated/8B は 5.0GB でも 24GB 級 1 枚に収まる。base(vLLM)を入れる場合のみ別途 vLLM 起動コスト。

### 4.3 シード・キャッシュ・交絡の統制

- **シード固定**: 全セルで `run.seed` を同一(例 42)に。乱数消費は k・モデルで不変(R1 設計)なので、**変える変数を model と k だけに限定**する。
- **ペルソナ・初期関係を全セル共通**: `agents.personas_file=data/personas_*.json` と `agents.icebreak_file` を全セルで同一に(config は既に「全 k 条件で同一 icebreak ファイル=初期関係が条件間で同一=交絡の排除」と明記)。→ model 間でも同一ファイルを使い、**唯一の差をモデルと k に**。
- **キャッシュ分離(重要)**: 応答キャッシュキー = `sha256(backend.name + params + prompt)`(`src/society/llm/cache.py`)。**`model.name`(=backend.name)を変えるとキャッシュは自動で別物**になるので、モデルごとに別キャッシュが張られ**相互汚染しない**。ただし:
  - 各モデル条件で `model.name` を**明示的に変える**(例 `qwen3-4b-instruct` / `qwen3-4b-ablit`)。同名だと別モデルの応答を誤再生する。
  - `think` はキャッシュキーに含まれる(切替時の旧応答誤再生を防止)ので reflect_think 切替も安全。
  - 再現は「初回ラン=キャッシュ生成 → 再生で完全一致」の運用。abliterated/ollama も初回は非決定的なので、**論文用 k* データは初回でキャッシュを焼き付けてから再生**。
- **compute 一定**: k{free, off} で LLM 呼数・トークン予算が一定であること(`controls.mode=compute_matched` / `null_series`)を確認。model 間は呼数がほぼ同一(§3 で測る)。

### 4.4 判定指標(model×k の主効果・交互作用)

| 指標 | 出所 | 仮説での期待 |
|---|---|---|
| **ツール行使率**(propose/host_event/post_flyer/found_group/open_venture) | L1 events | abliterated で>0 に立てば RLHF 抑制仮説を支持 |
| **free_action 率**(`freedom.open_actions=true` 時の "do") | L1 events | abliterated で自由行動が増えるか |
| **提案数 / 設立数**(propose 成立・found_group) | L1/制度DSL | 世界改変の実行が創発するか |
| **発話 distinct-2** | speak/post | entropy-reduction が外れて多様性が上がるか(SimBench tradeoff の内製検証) |
| **R²ext(R²(k) の外部世界改変量)** | analyze 側・Y外部4層 | k* 信号がモデルで保存/消失するか(→ pimmur-compliance §4 の robustness audit へ) |
| **fallback 率 / JSON 遵守**(統制指標) | summary.json | 能力低下の交絡監視(§3) |

→ **k* が instruct でだけ立ち abliterated で消える(または逆)なら、それは社会の相転移でなくアライメント固有アーティファクト**。この判定を `docs/research/pimmur-compliance.md` §4 の k* robustness audit に接続する。

---

## 5. 推奨構成(明記)

| 段階 | モデル(name) | ollama タグ | k | 用途 |
|---|---|---|---|---|
| 基準 | `qwen3-4b-instruct` | `qwen3:4b`(既運用) | free / off | 現行の基準条件 |
| **第1対照** ★ | `qwen3-4b-ablit` | `huihui_ai/qwen3-abliterated:4b-v2-q4_K_M` | free / off | RLHF 抑制の主効果(最優先・最クリーン) |
| 上位対照(任意) | `qwen3-8b-instruct` / `qwen3-8b-ablit` | `qwen3:8b` / `huihui_ai/qwen3-abliterated:8b-v2-q4_K_M` | free / off | 規模×アライメントの2×2 |
| base 極(任意・vLLM) | `qwen3-4b-base` | `Qwen/Qwen3-4B-Base`(要 vLLM+guided_json) | free / off | raw base 極。交絡リスク高・第3段 |

**ラン本数**: まず **第1対照の 4セル(15体×2日)** を最小実験として実施(§4.2: ~60–80分・~1,300呼)。**その前に §3 の 1 日スモークで abliterated の品質裏取り**を通す(これが無いと k* 解釈が能力低下と交絡する)。上位・base は結果を見て段階追加。

**pull コマンド(実行しない・裏取り後に手動で)**:
```bash
ollama pull huihui_ai/qwen3-abliterated:4b-v2-q4_K_M     # 第1対照(2.5GB, Q4_K_M, 40K, Apache-2.0)
ollama pull qwen3:8b                                     # 上位 instruct(任意)
ollama pull huihui_ai/qwen3-abliterated:8b-v2-q4_K_M     # 上位 abliterated(任意, 5.0GB)
# base は ollama 公式 GGUF 未確認 → HF Qwen/Qwen3-4B-Base を vLLM で(guided_json 前提)
```

---

## 6. 出典(アクセス日 2026-07-12・一次/実ページ優先)

**ベンチ・方法論**
- SimBench: Benchmarking the Ability of LLMs to Simulate Human Behaviors — arXiv:2510.17516: https://arxiv.org/abs/2510.17516 / HTML https://arxiv.org/html/2510.17516v4 / project http://simbench.tiancheng.hu/ (MMLU-Pro r=0.939・entropy-reduction tradeoff・40.80/100 を確認。**「r=−0.942」は未確認**)

**対照モデル(実ページ確認)**
- ollama `huihui_ai/qwen3-abliterated`(タグ一覧・209.3K pulls・Apache-2.0): https://ollama.com/huihui_ai/qwen3-abliterated / `:4b` https://ollama.com/huihui_ai/qwen3-abliterated:4b / `:4b-v2-q4_K_M` https://ollama.com/huihui_ai/qwen3-abliterated:4b-v2-q4_K_M
- HF `huihui-ai/Qwen3-4B-abliterated`: https://huggingface.co/huihui-ai/Qwen3-4B-abliterated / v2 https://huggingface.co/huihui-ai/Huihui-Qwen3-4B-abliterated-v2 / 8B https://huggingface.co/huihui-ai/Qwen3-8B-abliterated / 3.5-4B https://huggingface.co/huihui-ai/Huihui-Qwen3.5-4B-abliterated
- HF `Qwen/Qwen3-4B-Base`(公式・Apache-2.0・pretraining stage・chat template なし): https://huggingface.co/Qwen/Qwen3-4B-Base
- HF `Qwen/Qwen3-4B-GGUF`(**post-trained/instruct の GGUF。base ではない**): https://huggingface.co/Qwen/Qwen3-4B-GGUF

**本プロジェクト内部参照**
- `docs/research/llm-model-selection.md`(§3.4 構成C model×k・§2.5 ライセンス・§3.0 A5000 量子化)/ `docs/lit/infra__model-choice-conflict.md`(abliterated 設計・huihui 劣化警告・base 未公開)
- `docs/calibration/calibration-20260709.md`(qwen3:4b/8b 実測呼数・行動分布・fallback 0%)/ `docs/research/world-change-motivation.md`(ツール0使用・状態飽和)
- `src/society/llm/cache.py`(キャッシュキー = backend.name+params+prompt、think 含む)/ `conf/config.yaml`(agents.personas_file / icebreak_file / k.writeback / controls / freedom.open_actions / model.reflect_think)
- `docs/research/pimmur-compliance.md` §4(k* robustness audit — 本ランの R²ext 判定の接続先)
