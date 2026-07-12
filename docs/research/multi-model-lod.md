# マルチモデル LOD 設計 — 一度のシミュレーションで複数 LLM を使い分ける

- 作成: 2026-07-12 / 担当: Opus 4.8(リサーチ) / 種別: **調査のみ**(コード非編集・実LLM実行なし・commit なし)
- 目的: 「前景=高計算/背景=低計算」の **Level of Detail(LOD)** をモデル選択の次元でも実装するための材料を集める。ローカル複数モデル + API モデルを **同一ラン内で使い分ける** ときの (1)モデル選択肢、(2)同時サービング機構、(3)API 単価と再現性、(4)ルーティング/カスケード先行研究、(5)コスト試算、(6)本シミュ制約(R1・キャッシュ・mock)との整合、を棚卸しする。
- 前提の必読(重複を避け差分を書く):
  - [`docs/research/llm-model-selection.md`](llm-model-selection.md) — 本命モデル(Qwen3系)・A5000量子化・GPU構成案A/B/C・要件R1〜R10。本メモは **API 次元** と **同一ラン内の複数バックエンド配線** を足す。
  - [`docs/research/compute-efficiency.md`](compute-efficiency.md) — 削減技法カタログ(E1=speculative decoding 等)。**階層化(前景=フルLLM/背景=統計)は「Tier 3=研究目的と衝突」に分類済み**。本メモはその階層化を "モデル級の階層" として具体化しつつ、同 doc の R1 警告を継承する。
  - [`docs/research/token-budgets.md`](token-budgets.md) — 入出力トークン実測(コスト試算の基礎)。
  - [`docs/research/scale-audit-100days.md`](scale-audit-100days.md) — 呼数の非対称(deliberate は cap、reflect/plan は非 cap)。
- 出典方針: 単価は **公式価格ページで裏取り**。二次情報は 🔶 を付し絶対値の根拠にしない。未確認は「**未確認**」と明記(捏造禁止)。Anthropic 単価/仕様は `claude-api` スキル同梱の公式キャッシュ(2026-06-24)に準拠。

---

## 0. LOD 設計への示唆(結論を先に)

1. **LOD の第一軸は「エージェント」ではなく「purpose(呼種)」にすべき。** 現行 `FleetLLM(tiers=...)` は `rng_key` 先頭の purpose(`deliberate` / `plan` / `reflect` / `recall`)でサーバ群を分ける seam を**既に持つ**(fleet.py L14-16, 71-74)。purpose 単位のモデル割当は **全エージェントに一様**=呼数もモデル割当も k と交絡しない=**R1 に安全**。「重い内省 1回/日=大モデル、軽い発話96%=小モデル」がまず正解。
2. **「エージェント階層」LOD(前景=API上位/背景=小型)は効くが k\* を汚す危険がある。** 背景に落とした個体は "世界改変者" になれず Y_external の分散を消す。採用するなら **割当を初期化時の固定traitで決め、k 非依存・決定論**にし、**k\* は同一tier内でのみ測る**(compute-efficiency §3.1/§4 の結論を継承)。
3. **API を混ぜる最大の動機は「前景の少数個体に発話品質・ペルソナ忠実度を厚くする」こと**。会話96%はローカル 8-14b で fallback 0% が実測済み(llm-model-selection §1.2)なので、API は "全体" ではなく "前景 or reflect" に絞るのが費用対効果最良。
4. **同一ラン内マルチモデルには新しい配線が要る。** 現行は `model.backend` が単一(mock|ollama|vllm)で `CachedLLM` が1バックエンドを包む。複数モデル併用には **(purpose, agent-tier)→サブバックエンド** に振り分ける合成ルータが必要(§7)。各サブバックエンドは `name` が別=キャッシュキーが別=**再現性は各モデル内で独立に担保**される(既存D13設計がそのまま効く)。
5. **API 再現性は要注意。** Anthropic の現行世代(Opus 4.8 / Sonnet 5)は **temperature も seed も無い**(§3.4)。`llm_cache`(初回保存→再生)がこの非決定性を吸収する唯一の実体。API を混ぜても「初回ランでキャッシュ生成→以降は再生」の規律を守れば決定論は保てる。

### 推奨 LOD マトリクス

**主軸(R1安全・既存seam流用可) = purpose 別:**

| 層 | 呼種(purpose) | 呼数比(実測) | 推奨モデル級 | 根拠 |
|---|---|---:|---|---|
| 深(Deep) | `reflect`(内省・kの作用点) | 3.8% | **API上位** or **ローカル 27-32b** | 深い世界観変容=質を厚く。1呼/日でレア(scale-audit §3.1) |
| 中(Mid) | `plan`(朝の計画) | 3.5% | ローカル 8-14b | 構造化出力・専用予算448tok |
| 軽(Light) | `deliberate`(発話/投稿/DM) | 92.7% | **ローカル 4-8b** | テンポ・多様性・fallback 0%実績。ここを最速で回すのが本体 |

**副軸(条件付き・R1リスク) = エージェント階層別:**

| 層 | 対象個体 | 割合目安 | 推奨モデル級 | R1 上の注意 |
|---|---|---:|---|---|
| 前景 | keystone/世界改変候補(固定traitで選抜) | ~5-10% | API上位(Sonnet 5/Opus 4.8)or ローカル 27-32b | **割当はk非依存の固定trait**。k\*は前景内でのみ測る |
| 中景 | 通常アクティブ | ~40% | ローカル 8-14b | — |
| 背景 | 低活性・routine中心 | ~50% | ローカル 4b or **ルールベース(routine.py)** | 背景個体は世界改変者になれない=環境充填役に限定 |

> 実装優先順: **①purpose別(reflect大/deliberate小)を既存 tiers seam で** → ②必要なら agent-tier を新seamで。①は R1 無傷でスケール余地を稼ぐ "タダ飯"。

---

## 1. ローカル LLM の選択肢(2026)

> 8b〜32b の本命帯は [`docs/research/llm-model-selection.md`](llm-model-selection.md) §2 が既に網羅(Qwen3.5/3.6-27B が Nejumi4 開重み最上位・Apache-2.0・思考モード内蔵)。ここでは **重複を避け、LOD の下層に使う超小型(<4B)** の実用性を評価する。

### 1.1 超小型モデル(背景層候補)の実力

| モデル | 規模 | VRAM(Q4目安) | 日本語 | JSON遵守 | ライセンス | LOD背景への適性 |
|---|---|---:|---|---|---|---|
| **Qwen3-0.6B** | 0.6B dense | ~1.0GB 🔶 | △(119言語対応だが生成品質は薄い) | △(guided必須) | Apache-2.0 | 実用性低。ルールベースの方が安定 |
| **Qwen3-1.7B** | 1.7B dense | ~1.4GB 🔶 | △〜○ | ○(format=json併用) | Apache-2.0 | 最小の "会話らしさ" 下限候補。要検証 |
| **Qwen3-4B** | 4B dense | ~2.5GB | ○ | ◎(手元運用で実績) | Apache-2.0 | **背景層の実務下限**(現行手元モデル) |
| **Gemma3-270M** | 0.27B | <1GB 🔶 | ×(英語中心) | × | Gemma規約 | 発話生成には不適。分類/フィルタ用途向け |
| **Gemma3-1B** | 1B | ~1GB 🔶 | △ | △ | Gemma規約 | 多言語140だが日本語生成は弱い |

出典: [Qwen3 Technical Report — arXiv:2505.09388](https://arxiv.org/abs/2505.09388) / [Qwen3 lineup 🔶](https://insiderllm.com/guides/qwen3-complete-guide/) / [Gemma3 — arXiv:2503.19786](https://arxiv.org/html/2503.19786v1)。VRAM 値は Q4 概算(🔶=二次情報)で本選実機の実測で埋めること。

**評価(本シミュ固有の警告)**:

- **<2B は "会話" には推奨しない。** 本シミュは日本語一人称・非定型発話・厳格 JSON を要求(llm-model-selection §1.1-1.2)。<2B は日本語口語の自然さと JSON 閉じ括弧が崩れやすく、fallback 率が上がる。手元の実測は **8b で fallback 0%**、4b で内省最終JSONが 11-18% 空(token-budgets §2.3)。**<2B の実データはリポジトリに無い=未確認**。
- **背景層は「小型LLM」より「ルールベース(routine.py)」が第一候補。** 既に routine.py という決定論 fallback があり、背景個体は環境充填が役目=発話品質は不要。**<2B に金/GPU を割くより、routine を賢くする方が R1・忠実度の両面で安全**(compute-efficiency §3.4 の "背景=ルール" 結論と一致)。
- **超小型を使うなら 4b を下限に。** Nejumi 4 は sub-10B で Nemotron Nano 9B JP(0.7111)がトップ級だが <4B の日本語スコアは公開ボードで低位。**LOD の下層 = 4b(現行手元モデル)or ルールベースの二択**が現実解。

### 1.2 中〜上位帯(前景/中景層)

llm-model-selection §2.7 の表を参照(要点のみ再掲):
- **中景=Qwen3-8B/14B**(~5-8GB INT4、fallback 0%実測、思考モード内蔵、Apache-2.0)。
- **前景=Qwen3.5-27B / Qwen3.6-27B**(~14GB INT4、Nejumi4開重み最上位、262K文脈)。
- 日本語特化(Sarashina/PLaMo)は品質高いが **非商用ライセンス**が配備の壁。llm-jp/Qwen は Apache で安全。

---

## 2. 複数モデルの同時サービング

### 2.1 Ollama(手元 Windows 単機)

| 環境変数 | 挙動 | LOD への含意 |
|---|---|---|
| `OLLAMA_MAX_LOADED_MODELS` | 同時ロード可能なモデル数。既定 = **3×GPU数**(CPUは3)。メモリに収まる範囲で複数常駐 | 手元1GPUでも **小モデル複数**なら同時ロード可(例: 4b+1.7b) |
| `OLLAMA_NUM_PARALLEL` | 1モデルが同時処理する並列リクエスト数。既定 = メモリに応じ **4 or 1** 自動選択 | 並列数だけ **context がその倍に膨張**(2K×4=8K相当のVRAM) |
| `keep_alive` | モデルの常駐時間。既定 **5分**。`/api/generate` で指定可、`0`=即アンロード | LODでモデルを切替えると **cold start**(再ロード)が入る。頻繁切替は keep_alive を長めに |

出典: [Ollama FAQ(公式)](https://docs.ollama.com/faq) / [Ollama multi-model 🔶](https://eastondev.com/blog/en/posts/ai/20260406-ollama-multi-model-deployment/)。

**手元単機での LOD 運用**: VRAM が足りれば `OLLAMA_MAX_LOADED_MODELS≥2` で **4b(背景)+ 14b(前景)を同時常駐**できる。ただし RTX系1枚(24GB想定)では 14b+4b で ~10GB、余裕はあるが並列数を上げると context 膨張で逼迫。**手元は "小2種の同時ロード" or "1種+API併用" が現実的**。VRAM を超えると新モデル要求時に **既存モデルをアンロードして入替**=スループット激減(頻繁な入替は避ける設計に)。

### 2.2 vLLM(本選 データセンター)

- **vLLM は 1プロセス=1モデルが基本。** 複数モデル=複数プロセス+GPU割当が必要(公式 issue #3326、AI-VERDE も "LLM ごとに vLLM インスタンス" + LiteLLM 名前ルーティング)。PagedAttention で単一GPUのモデル密度は 2-3倍にできるが、**別モデルの同居は依然プロセス分離**が原則。
- **LoRA は例外**: 同一ベースの複数 fine-tune は Multi-LoRA で MB単位追加のみ。だが本シミュは "別サイズの別モデル" を混ぜたい=LoRA では解けない。
- 出典: [vLLM issue #3326(複数モデル)](https://github.com/vllm-project/vllm/issues/3326) / [vLLM multi-model 🔶](https://lyceum.technology/magazine/multi-model-serving-single-gpu-vllm/) / [AI-VERDE — arXiv:2502.09651](https://arxiv.org/pdf/2502.09651)。

**7GPU 1ノードへの配置パターン(本選)**:

| パターン | 配置 | 長所 | 短所 |
|---|---|---|---|
| **均質**(構成A) | 27B-INT4 ×7 全GPU | prefix cache最大・キャッシュ単純・R7堅い | 発話にも27Bで過剰 |
| **purpose階層**(構成B) | reflect用 32B×(2GPU TP)1本 + deliberate用 8B×5本 | 認知の非対称にHW一致 | tier別モデルでキャッシュ規律↑ |
| **agent階層**(本メモ提案) | 前景用 27B×2 + 中景用 14B×2 + 背景用 4B×3(1GPUに複数プロセス) | 個体LODに一致・小モデルは高密度 | プロセス管理複雑・FleetLLM を purpose ではなく agent-tier で振る seam が要る |

- FleetLLM の `tiers` は現状 **purpose→URL群** の写像(fleet.py L54-61)。上表 "purpose階層" は既存seamで即実装可。"agent階層" は tier キーを agent-tier に読み替える改修が要る(§7)。
- **7GPU で "大×2 + 中×2 + 小×3" は VRAM 的に成立**: 27B-INT4×2=~28GB(2GPU)、14B×2=~16GB(2GPU)、4B×3=~7.5GB(1-2GPU に多重)。A5000 24GB×7 の予算内。実スループットは本選 `bench.py` 実測が必須。

### 2.3 その他のサーバ選択肢

- **SGLang**: RadixAttention で prefix 共有が強く、構造化出力(xgrammar)・複数モデルのルーティングも視野。本シミュは長共通prefix(ペルソナ)を持つので相性は良いはずだが **リポジトリに導入実績なし=未検証**。vLLM から乗り換える積極理由は現状薄い(既に vllm.py/fleet.py が動く)。
- **llama.cpp server**: 手元 CPU/小VRAM で軽量。GGUF量子化が豊富で <4B の背景モデルを CPU で回す選択肢になりうる。GPU を前景モデルに専有させ、背景を CPU llama.cpp に逃がす "異種混載" は手元単機で有効。ただし OpenAI互換HTTPなので現行 vllm.py の口(/v1/completions)で叩ける=**バックエンド増設コストは小**。
- 出典: [SGLang(GitHub)](https://github.com/sgl-project/sglang) / [llama.cpp(GitHub)](https://github.com/ggml-org/llama.cpp)。いずれも本選投入前に疎通確認要。

---

## 3. API モデル(2026年7月時点・公式価格で裏取り)

> **注意**: API 世代は数ヶ月で刷新される。以下は 2026-07 時点の公式ページ確認値。実装直前に必ず再確認。単価は **1M トークンあたり USD**。

### 3.1 Anthropic(Claude)

`claude-api` スキル同梱の公式キャッシュ(2026-06-24)より:

| モデル | Model ID | 入力 | 出力 | 文脈窓 |
|---|---|---:|---:|---|
| Claude Opus 4.8 | `claude-opus-4-8` | $5.00 | $25.00 | 1M |
| Claude Sonnet 5 | `claude-sonnet-5` | $3.00($2.00 introは2026-08-31まで) | $15.00($10.00 intro) | 1M |
| Claude Haiku 4.5 | `claude-haiku-4-5` | $1.00 | $5.00 | 200K |

- **Batch API**: 全モデル **50%引き**(非同期・最大24h・100k req/256MB/batch)。k×seed の大量ランに最適。
- **Prompt caching**: cache read ≈ **0.1×** 入力単価、cache write = **1.25×**(5分TTL)/2×(1h)。最小キャッシュprefix は Opus 4.8/Haiku 4.5=**4096tok**、Sonnet系=より小。**ペルソナ+ヘッダの長い共通prefixがそのまま効く**(本シミュのAPC設計 deliberate.py と整合)。
- **Structured outputs**: `output_config.format`(json_schema)対応(Opus 4.8/Sonnet 5/Haiku 4.5)。初回スキーマはコンパイル遅延、以降24hキャッシュ。→ 本シミュの厳格JSON要件(parse失敗=fallback)に**API側で強制可**。
- **再現性(重要)**: **temperature/top_p/top_k は Opus 4.8/Sonnet 5 で撤廃(送ると400)、seed パラメータ無し**。→ サンプリング制御が一切効かない=**完全非決定**。再現は応答キャッシュ頼み(§3.4)。
- 出典: [Anthropic Pricing(公式)](https://platform.claude.com/docs/en/pricing) / [Models overview(公式)](https://platform.claude.com/docs/en/about-claude/models/overview)。

### 3.2 OpenAI

公式価格ページ([developers.openai.com/api/docs/pricing](https://developers.openai.com/api/docs/pricing)、2026-07確認):

| モデル | 入力 | cached入力 | 出力 |
|---|---:|---:|---:|
| gpt-5.6-sol | $5.00 | $0.50 | $30.00 |
| gpt-5.6-terra | $2.50 | $0.25 | $15.00 |
| gpt-5.6-luna | $1.00 | $0.10 | $6.00 |
| gpt-5.4-mini | $0.75 | $0.075 | $4.50 |
| gpt-5.4-nano | $0.20 | $0.02 | $1.25 |

- **Batch API**: 50%引き。**seed パラメータ + `system_fingerprint` あり**(ベストエフォート決定性、保証ではない)=Anthropic より再現性制御の手がかりは多い。structured outputs(json_schema strict)対応。
- 出典: [OpenAI Pricing(公式)](https://developers.openai.com/api/docs/pricing)。🔶 世代名は流動的([DevTk 2026](https://devtk.ai/en/blog/openai-api-pricing-guide-2026/))。

### 3.3 Google Gemini

公式価格ページ([ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing)、2026-07確認):

| モデル | 入力(≤200k) | cached入力 | 出力 |
|---|---:|---:|---:|
| gemini-3.1-pro-preview | $2.00 | $0.20-0.40 | $12.00 |
| gemini-3.5-flash | $1.50 | $0.15 | $9.00 |
| gemini-2.5-flash | $0.30 | — | $2.50 |
| gemini-3.1-flash-lite | $0.25 | — | $1.50 |
| **gemini-2.5-flash-lite** | **$0.10** | — | **$0.40** |

- **Batch mode**: 全モデル **50%引き**(最大24h)。context caching は miss の ~10%。無料枠あり(検証に有用)。
- **gemini-2.5-flash-lite($0.10/$0.40)が現行 "API最安" 帯** = 全部APIシナリオの下限価格を決める。
- 再現性: temperature あり。seed は一部モデルで対応するが保証は弱い(**要確認**)。
- 出典: [Gemini API Pricing(公式)](https://ai.google.dev/gemini-api/docs/pricing)。

### 3.4 rate limit / レイテンシ(共通所見)

- 3社とも **tier別 RPM/TPM 制限**あり。300体×144step の同期ランを "実時間" で回すと瞬間QPSが跳ねる=**Batch API(非同期)に寄せるのが安全**。本シミュは応答キャッシュ前提で "初回は非同期一括生成→再生" にできるので Batch 相性が良い。
- レイテンシは Batch=最大24h(実測は多く1h以内)、同期=モデル依存。**同期API を毎step叩く設計は非推奨**(rate limit と決定論の両面で不利)。

---

## 4. ルーティング/カスケード研究

### 4.1 品質-コスト曲線の先行研究

| 研究 | 手法 | 削減実績 | 本シミュへの含意 |
|---|---|---|---|
| **FrugalGPT**(Chen+ 2023, [arXiv:2305.05176](https://arxiv.org/abs/2305.05176)) | 3段カスケード(安モデル→品質推定→上位へエスカレーション) | GPT-4比 **最大98%** コスト減で同等 | "まず小、崩れたら大" はLODの原型。ただし品質推定器が追加呼=本シミュでは崩れ検知(JSON parse失敗)を無料で流用できる |
| **RouteLLM**(Ong+ 2024, [arXiv:2406.18665](https://arxiv.org/pdf/2406.18665)) | 選好データで学習したルータが強/弱モデルを選ぶ | **2倍+** コスト減で品質維持 | 学習ルータは重い。本シミュは "クエリ" ではなく "purpose/agent-tier" で決め打ちする方が単純・R1安全 |
| **カスケード survey**(2026, [arXiv:2603.04445](https://arxiv.org/html/2603.04445v2)) | 動的ルーティング/カスケードの体系 | — | 品質推定→エスカレーションの一般形。本シミュは "エスカレーション" を入れると呼数が動く=R1注意 |

**本シミュへの適用可否**:
- **決め打ちルーティング(purpose/agent-tier固定)が本命**。FrugalGPT型の "動的エスカレーション"(小→大へ再送)は **呼数を変動させる=R1(呼数のk非依存)を脅かす**。崩れたら大モデルに再送する率が k と相関すると k\* を汚す。
- **例外的に安全な流用**: 「JSON parse 失敗 → routine(ルールベース) fallback」は既存機構で、エスカレーション先が LLM ではないので呼数を増やさない。これは FrugalGPT の "崩れ検知" を無料で持っているのと同じ。

### 4.2 マルチエージェント社会シミュでの計算階層化(先行例)

| プロジェクト | どのエージェント/呼に高計算を割るか | 本シミュとの距離 |
|---|---|---|
| **Generative Agents**(Park+ 2023, [arXiv:2304.03442](https://arxiv.org/abs/2304.03442)) | importance採点で発火ゲート、reflection は 1日2-3回だけ | **内省を階層化**する発想の祖。本シミュの reflect=深層と一致 |
| **OASIS**(camel-ai 2024, [arXiv:2411.11581](https://arxiv.org/abs/2411.11581)) | Time Engine(時間帯別活性ベクトル)で確率的に活性化=誰を撃つか | 本シミュの drive+lod と同型。"誰に計算を割るか" を確率活性化で決める |
| **AgentScope**(2024, [arXiv:2407.17789](https://arxiv.org/abs/2407.17789)) | vLLM 多モデル fleet(8×8B/2×70B/1×176B per device)+依存グラフ自動並列 | **多モデル艦隊の実例**。本シミュの fleet.py と同思想。異サイズ混載の先行例 |
| **Project Sid/PIANO**(Altera 2024, [arXiv:2411.00114](https://arxiv.org/abs/2411.00114)) | GPT-4o固定・10並行モジュール/体、social goal を5-10秒毎再生成 | 全体を上位モデルで回す(階層化なし)。コスト非開示 |
| **AgentTorch**(MIT, AAMAS 2025, [arXiv:2409.10568](https://arxiv.org/abs/2409.10568)) | archetype で群を束ね archetype 単位1呼=42,000倍削減 | **個体異質性を消す**=k\*研究に不可(compute-efficiency §4 と同結論) |

**読み取り**: 先行研究の "計算階層化" は主に **(a) 発火ゲート(誰を撃つか)** と **(b) 呼種の階層(reflection をレアに)** で、本シミュは両方を既に持つ(drive/lod + reflect日1回)。**"モデル級の階層"(前景=大/背景=小)を明示採用した社会シミュは AgentScope の異サイズ艦隊が最も近い**が、彼らは "どの個体に大を割るか" ではなく "スループット確保" が動機。**本シミュ固有の課題=「モデル級の割当が k\* を交絡しないこと」は先行研究に直接の答えがない**(archetype は個体を潰すので参考にならない)。

---

## 5. コスト試算(300体 × 100日 = 1ラン)

### 5.1 呼数の実測(基礎)

`runs/daily300_100d/summary.json`(mock, 300体×100日=14,400step)より:

| purpose | 呼数 | 比率 | 呼数/体/日 |
|---|---:|---:|---:|
| `llm_deliberate` | 642,215 | 92.7% | 21.4 |
| `reflect` | 26,640 | 3.8% | 0.89 |
| `day_plan` | 24,004 | 3.5% | 0.80 |
| **合計 `llm_calls`** | **692,859** | 100% | **23.1** |

(3 purpose の和 = 692,859 = summary の `llm_calls` と完全一致で検算済み)

### 5.2 トークン仮定(token-budgets 実測ベース)

- **入力**: 本番リッチ profile で deliberate ~1,040tok / plan ~1,140 / reflect ~1,230(token-budgets §2.2)。deliberate 支配なので **加重平均 ≈ 1,100tok** を採用。試算では丸めて **入力 1,200tok**。
- **出力**: deliberate ~100-170tok / plan ~300-450 / reflect ~250(思考オフ時の最終JSON、daily.yaml で `reflect_think:false`)。加重 **≈ 170tok**。試算では **出力 200tok**。
- 1ランの総トークン: 入力 692,859×1,200 ≈ **0.83B tok** / 出力 692,859×200 ≈ **0.139B tok**。
- ⚠️ トークンは概算(±30%)。プロンプトキャッシュ(APC)でペルソナ共通prefixが効けば入力実効コストは下がる(API prompt caching は prefix 一致で cache_read≈0.1×)。

### 5.3 3シナリオ概算(標準単価 / Batch 50%引き)

| シナリオ | 構成 | 入力コスト | 出力コスト | **標準計** | **Batch計** |
|---|---|---:|---:|---:|---:|
| **(a) 全部API最安** | Gemini 2.5 Flash-Lite($0.10/$0.40) | $83 | $56 | **~$139** | **~$70** |
| (a') 全部API中位 | Haiku 4.5($1/$5) | $831 | $693 | **~$1,524** | **~$762** |
| **(b) API上位×前景10% + ローカル90%** | 前景=Sonnet 5(intro$2/$10)、背景=ローカル(~$0) | $166 | $139 | **~$305** | **~$153** |
| (b') 前景=Opus 4.8 | 前景10%=Opus($5/$25)、背景ローカル | $416 | $347 | **~$763** | **~$381** |
| **(c) 全ローカル** | Qwen3 艦隊(7GPU自前/借用) | — | — | **~$0(限界費用)** | 電力/GPU借用のみ |

**k×seed 掃引での増幅(最重要)**: 上は **1ラン**。論文級は **複数 k × ≥5 seed = 15〜40ラン**。全部API最安でも $70×30 ≈ **$2,100**、Haiku ×30 ≈ **$23k**、前景Opus ×30 ≈ **$11k**。**全ローカルだけが掃引に耐える限界費用**。→ **本命=全ローカル(c)、API はゴールデン/前景の "厚み" に選択投入(b)** という結論を強く支持する。

**含意**:
- API を "全体" に使うのは掃引で破綻。**前景の少数個体 or reflect(3.8%)だけに絞れば** API混載は $150-380/ラン に収まり、発話品質/ペルソナ忠実度の "上澄み" を買える。
- **Batch API(全社50%引き)は必須**。同期毎step叩きは rate limit・コスト・決定論すべてで不利。
- Gemini Flash-Lite($0.10/$0.40)が最安帯。ただし日本語品質は Sonnet/Opus 級に劣る可能性=**前景の品質投資には向かない**(最安帯は "全体を安く" 用、上位は "前景に厚く" 用)。

---

## 6. 再現性の論点

### 6.1 各APIの決定論性

| 提供者 | temperature | seed | 決定論の実態 |
|---|---|---|---|
| Anthropic(Opus 4.8/Sonnet 5) | **撤廃(送ると400)** | **無し** | サンプリング制御ゼロ=**完全非決定**。プロンプトで誘導するのみ |
| OpenAI(GPT-5系) | あり | **あり**(+system_fingerprint) | ベストエフォート決定性。保証ではない(fingerprint変化で揺れる) |
| Google Gemini | あり | 一部対応(**要確認**) | temp=0でも保証弱い |
| ローカル vLLM | あり | あり | temp=0でも **バッチ構成で揺れる**(compute-efficiency §3.3)。MoEはexpert routingで更に揺れる |

**共通事実**: temperature=0 でも "初回ランのバイト一致" はどの提供者も保証しない。本シミュの L1 バイト一致(決定論)を満たすのは **応答キャッシュのみ**。

### 6.2 llm_cache が API 非決定性をどこまで吸収するか

`src/society/llm/cache.py` の設計(D13):
- キー = `sha256(backend.name + params + prompt)`。初回=実呼び出し+保存、再生時=完全再現。
- **`backend.name` はモデル名ベース**(vllm.py L32 / ollama.py L18)。→ **モデルを混ぜても各モデルの応答が別キーで独立にキャッシュされる**。マルチモデル LOD と D13 は自然に両立。
- **吸収できること**: 初回でキャッシュを作れば、以降の再生ランは API の非決定性/temp無し/seed無しに一切影響されず **バイト一致で再現**。論文用 k\* データは「初回ランでキャッシュ生成 → 再生で完全再現」で担保(llm-model-selection §1.7 と同じ規律)。
- **吸収できないこと**: **初回生成そのものの揺れ**は残る。同じ seed 設定の別ラン初回同士は一致しない。k 掃引の各セルは "初回キャッシュを固定して以降共有" しないと比較が汚れる。API を混ぜると初回コストが金銭で発生する点も注意(ローカルは電力のみ)。
- **キャッシュ規律**: `model.name`(→backend.name)を変えるとキャッシュ全無効。比較ランは **同一モデル構成(同一 tier 割当・同一 API モデル)を厳守**。マルチモデルにすると規律面が増える(どの purpose/tier がどのモデルだったかを固定)。

---

## 7. 本シミュ固有の制約との整合

### 7.1 R1 原則(モデル割当はエージェント決定論・k非依存であるべき)

- **R1(呼数の k 非依存)への直接の脅威 = 動的エスカレーション**。「崩れたら上位モデルへ再送」は呼数を増やす=k と相関すると k\* を汚す。→ **本シミュでは動的カスケードを採らず、purpose/agent-tier で決め打ち**する。
- **agent-tier LOD の必須条件**: 前景/背景の割当は **初期化時の固定trait(k非依存)で決定論的に**決め、run中は不変。割当が k や実行時状態と交絡すると "どの個体が世界改変者になれるか" が k で変わり k\* が交絡する。
- **purpose-LOD は R1 に無条件で安全**: 全エージェントが同じ purpose 割当を受ける=呼数もモデルも k と独立。→ **まず purpose-LOD(reflect大/deliberate小)から**が原則。
- 参考: scale-audit §3.1(deliberate は budget cap、reflect/plan は非cap)。モデル階層化しても **呼数の cap 構造は変えない**こと。

### 7.2 キャッシュキーにモデル名が入る現行設計

- `backend.name`(URL非依存・モデル名ベース)がキーに入る(cache.py L32、vllm.py/ollama.py/fleet.py の name 設計)。→ **マルチモデルは "各モデル別キャッシュ" として自然に成立**。fleet の `name=f"fleet/{model}"` は艦隊全体で1名=同一モデルの艦隊内では共有される(D13)。
- **含意**: 異モデルを混ぜる合成ルータを作る場合、各サブバックエンドが **固有の name** を返せば、キャッシュ整合は既存機構のまま。実装で気をつけるのは "同じ purpose/tier に必ず同じモデルを割当てる"(でないと同一プロンプトが別モデルで別キャッシュに散る)。

### 7.3 mock / 実LLM の分担

- 現行: `backend: mock | ollama | vllm`(config.py/simulation.py L336-362)。mock は配線検証・決定論スモーク用、実LLM は品質検証・本番。
- **マルチモデル LOD の mock 戦略**: MockBackend は1種の疑似応答=モデル階層を模せない。**LOD 掃引・トークン LOD 実験は実LLMでしか出ない**(token-budgets §4 の "mock は予算に反応しない" と同型)。→ **配線(合成ルータ)の決定論テストは mock で、モデル級の効果測定は実LLM(ollama手元/vLLM本選)で**、と分担。
- 検証は `validation-runs-short` の方針どおり: フル100日は避け、mock or ≤24step スモークで配線を確認 → 実LLM は小規模で品質確認。

### 7.4 実装への具体的示唆(親エージェント=Fable 向け)

現行アーキで **同一ラン内マルチモデルに必要な最小改修**(本メモは提案のみ・コード非編集):

1. **purpose-LOD(最小・R1安全)**: config の `model.tiers` に purpose→URL群を書くだけで既存 FleetLLM が振り分ける(fleet.py L54-61)。`reflect: [大モデルURL]`, `default: [小モデルURL群]`。**新規コード不要**。ただし同一 model 名で複数サイズを混ぜられない現制約(FleetLLM は単一 `model` 引数)に注意 → tier別に別モデルを載せるには FleetLLM を tier別 model 名対応に拡張が要る。
2. **agent-tier LOD or API混載(要新規配線)**: `CachedLLM(backend)` の backend を **合成ルータ**(rng_key の purpose/agent-tier で子バックエンドへ dispatch)に差し替える。各子(Ollama/Vllm/新設 API バックエンド)は固有 name を持ちキャッシュ独立。**API バックエンドは未実装**=Anthropic/OpenAI/Gemini 用の LLMBackend 実装(base.py の generate インタフェース準拠)を新設する必要。
3. **API 再現性の担保**: API を混ぜるなら「初回一括生成(Batch API)→ llm_cache 保存 → 以降再生」の運用を固定。Anthropic は seed/temp 無しなので **キャッシュ固定が唯一の再現手段**。
4. **R1 ガード**: agent-tier 割当を初期化時の固定trait(persona由来・k非依存)から決定論生成。tier割当ロジックが k や乱数stream に触れないことをテストで担保(既存の "新stream追加なし=決定論不変" 規律に沿う)。

---

## 8. 出典リンク

**API 単価(公式・裏取り済み)**
- [Anthropic Pricing(公式)](https://platform.claude.com/docs/en/pricing) / [Models overview(公式)](https://platform.claude.com/docs/en/about-claude/models/overview)(Opus 4.8 $5/$25・Sonnet 5 $3/$15・Haiku 4.5 $1/$5、Batch 50%、caching read0.1×/write1.25×、temp/seed撤廃)
- [OpenAI API Pricing(公式)](https://developers.openai.com/api/docs/pricing)(gpt-5.6-luna $1/$6・mini $0.75/$4.5・nano $0.20/$1.25、Batch 50%、seed+fingerprint あり)
- [Google Gemini API Pricing(公式)](https://ai.google.dev/gemini-api/docs/pricing)(2.5 Flash-Lite $0.10/$0.40 最安・3.5 Flash $1.5/$9・3.1 Pro $2/$12、Batch 50%)

**ローカルモデル / サービング**
- [Qwen3 Technical Report — arXiv:2505.09388](https://arxiv.org/abs/2505.09388) / [Gemma 3 — arXiv:2503.19786](https://arxiv.org/html/2503.19786v1)
- [Ollama FAQ(公式・並列/keep_alive/MAX_LOADED)](https://docs.ollama.com/faq)
- [vLLM 複数モデル issue #3326](https://github.com/vllm-project/vllm/issues/3326) / [AI-VERDE(1モデル1インスタンス+ルータ)— arXiv:2502.09651](https://arxiv.org/pdf/2502.09651)
- [SGLang(GitHub)](https://github.com/sgl-project/sglang) / [llama.cpp(GitHub)](https://github.com/ggml-org/llama.cpp)
- 🔶 二次(絶対値の根拠にしない): [Qwen3 lineup](https://insiderllm.com/guides/qwen3-complete-guide/) / [Ollama multi-model](https://eastondev.com/blog/en/posts/ai/20260406-ollama-multi-model-deployment/) / [vLLM multi-model](https://lyceum.technology/magazine/multi-model-serving-single-gpu-vllm/)

**ルーティング / カスケード / 社会シミュ階層化**
- [FrugalGPT — arXiv:2305.05176](https://arxiv.org/abs/2305.05176) / [RouteLLM — arXiv:2406.18665](https://arxiv.org/pdf/2406.18665) / [カスケードsurvey — arXiv:2603.04445](https://arxiv.org/html/2603.04445v2)
- [Generative Agents — arXiv:2304.03442](https://arxiv.org/abs/2304.03442) / [OASIS — arXiv:2411.11581](https://arxiv.org/abs/2411.11581) / [AgentScope — arXiv:2407.17789](https://arxiv.org/abs/2407.17789) / [Project Sid — arXiv:2411.00114](https://arxiv.org/abs/2411.00114) / [AgentTorch — arXiv:2409.10568](https://arxiv.org/abs/2409.10568)

**リポジトリ内(既存・根拠の中心)**
- [`docs/research/llm-model-selection.md`](llm-model-selection.md)(本命モデル・GPU構成A/B/C・要件R1-R10)
- [`docs/research/compute-efficiency.md`](compute-efficiency.md)(階層化=Tier3・archetypeは非推奨・R1警告)
- [`docs/research/token-budgets.md`](token-budgets.md)(入出力トークン実測)/ [`docs/research/scale-audit-100days.md`](scale-audit-100days.md)(呼数の非対称)
- 実装: `src/society/llm/{base,cache,ollama,vllm,fleet,mock}.py`(バックエンド抽象・キャッシュD13・tier seam)/ `src/society/config.py` + `engine/simulation.py:336-362`(backend分岐)/ `conf/{config,daily,production}.yaml`(model ブロック)
- 実測: `runs/daily300_100d/summary.json`(692,859呼・purpose内訳)

> 正直な記録: (i)<2B の日本語/JSON 実データはリポジトリに無く **未確認**(4b が実務下限)。(ii)API 世代名は 2026-07 時点の公式値だが数ヶ月で刷新される=実装直前に再確認。(iii)Gemini の seed 対応・SGLang/llama.cpp の本シミュ疎通は **未検証**。(iv)トークン量は概算(±30%)で、APC のヒット率次第で API 入力実効コストは更に下がりうる。(v)スループット(tok/s)・7GPU実配置の VRAM 実測は本選 `bench.py` で埋めること。
