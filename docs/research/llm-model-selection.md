# 本番LLMモデル選定 — 要件の体系化・候補モデル比較・GPU構成案(議論の土台)

- 種別: リサーチ(調査のみ)。実LLM実行なし・src非編集・git commitなし。
- 実施: 2026-07-07、Opus 4.8 サブエージェント(W5)。
- 位置づけ: **これは「確定」ではなく議論のための土台**。断定は避け、要件×モデルのトレードオフを正直に並べる。最終決定はユーザー。
- 出典方針: **一次資料(公式技術報告 / arXiv / 公式HFモデルカード / vLLM公式 / Nejumi公式)を優先**。二次情報(個人ブログ・ベンダー記事)は 🔶 を付し、絶対数値の根拠にはしない。VRAM 値は「パラメータ数からの見積り」で、実測は本選環境で埋める(`docs/ops-production.md` の方針に従い、未測定のトークン/秒は書かない)。
- **検証状況(2026-07-07 Web 再確認)**: 本命候補の一次情報を公式HFカードで裏取り済み。**Qwen3.5-27B** = dense、Gated DeltaNet(線形注意)+ Gated(フル)Attention のハイブリッド、262,144 ネイティブ・最大 1,010,000 拡張、Apache-2.0、思考モード既定 ON、MMLU-Pro 86.1(カード)。**Qwen3.6** = dense 27B(2026-04-22)+ MoE 35B-A3B(2026-04-16)、Apache-2.0、262K、思考既定 ON、カード確認ベンチ **SWE-bench Verified 77.2 / MMLU-Pro 86.2 / AIME26 94.1**。**Nejumi 4 の Qwen3.5-27B = 0.8049(開重み初の 0.80 超)** は二次記事で確認(公式ボードでの最終照合は本選前に推奨)。両カードとも **JA 個別スコアは非掲載**(JA 実力は Nejumi 実績で担保)。

> ⚠️ 前提の時点差: 本メモは 2026-07 時点の公開情報で書く。リポジトリの旧記述(`docs/lit/shibuya_sim_infra_summary.md`「Qwen3.6-27B-MTP の FP8/4bit」)は Gemini 議論由来の暫定確定であり、本メモで **A5000 実機制約と量子化の観点から再検討**する(下記 §3.0)。

---

## 0. 3行サマリ

1. **このシミュが LLM に求める中核要件**は、①日本語の自然な一人称発話+長期ペルソナ一貫性、②厳格な行動JSONの高い遵守率(parse失敗=routineフォールバック)、③思考モードでの深い内省(1200token)、④短文(≤320token)のテンポと多様性、⑤A5000 24GB×7・単一ノード・vLLM で「毎step ~300呼」を捌くスループット、⑥応答キャッシュ前提の再現性、⑦論文公開・ハッカソン可のライセンス、⑧長い共通prefix(ペルソナ+ヘッダ)を活かす prefix-cache/sticky-routing 適合。**実測(qwen3:8b, eco系ラン)では fallback 0%・100日でも劣化なし**で、8B級でも JSON 遵守と長期運用は既に成立している。
2. **候補の本命は Qwen3 / Qwen3.5 / Qwen3.6 系(Apache-2.0・思考モード内蔵・日本語が開重み最上位クラス)**。A5000(Ampere, FP8のW8A8ハード加速なし)では **FP8 ではなく AWQ/GPTQ の INT4** が実務解。27B-dense は INT4 で ~14GB=24GB に7並列で収まる。日本語特化(Sarashina/PLaMo)は品質は高いが **非商用ライセンス**が本番配備の壁。
3. **推奨は単一決め打ちにしない**。(A)均質艦隊=Qwen3.5/3.6-27B-INT4 ×7、(B)階層=内省を大モデル(32B/27B)へ・会話を小モデル(4B/8B)群へ、(C)**model×k を実験変数化**(instruct ⇔ abliterated)で「世界改変の観測を RLHF 同調が潰す」問題を検証。§3 に試算、§4 に論点。

---

## 1. 要件の体系化(コード根拠つき)

シミュが LLM に課している要件を、コードと実測ランから逆算して体系化する。各項目に「どこで効くか(根拠ファイル)」を付す。

### 1.1 日本語の自然な会話 + 一人称ペルソナの一貫性
- ヘッダで**一人称の人間**を宣言:「あなたは渋谷の街で暮らす一人の人間です。状況に対して自然に振る舞ってください。」(`src/society/cognition/deliberate.py:_HEADER_HEAD`)。ペルソナ本文・所属・気分・記憶・間柄・日記が毎回注入される(`build_prompt`)。
- **反復抑制**:「さっきと同じ話題・言い回しを繰り返さない。今の時刻・場所・気分・出来事に根ざした新しい内容を話す」(同 L144)。SNS は「場所・時刻の報告文にしない/挨拶・自己紹介しない」(L157)。→ **口語の自然さと非定型性**が要件。
- **長期一貫性**: 100日ランで beliefs が線形蓄積・関係台帳を全員分保持・過去参照率が増える(`docs/research/memory-100day-audit.md`)。→ **persona drift(長期の人格崩れ)に強いモデル**が望ましい。学術的裏付けは §2.6。
- 既知の弱点(実測): qwen3:8b は SNS 投稿が「朝のコーヒー・ラーメン」へ収斂しがち(`docs/log/devlog.md` Entry2 正直注記)。**mode collapse/話題収斂**はモデル選定・温度・プロンプトの三者で対処する論点。

### 1.2 行動JSONフォーマットの遵守率(parse失敗=fallback)
- `parse_action`(`deliberate.py`)は **厳格JSON**を要求。キー `action` 必須、型は speak/coin_label/post/dm/host_event/post_flyer/found_group/propose/open_venture/plan/recall/reflect/wander の13種。
- **壊れたJSONの寛容修復**あり(`_loads_lenient`: 途中で切れた JSON に `}`/`"}` を補って再パース)= **トークン上限での閉じ括弧欠落**を救済。それでも失敗すれば `None` → **routine(ルールベース)へフォールバック**(D16、`docs/ops-production.md §6`)。
- vLLM 経路は **`response_format={"type":"json_object"}` を優先**し、非対応(HTTP400)なら外して再送(`src/society/llm/vllm.py`)。**guided_json / 文法制約対応の vLLM だと更に堅い**(ops §7 トラブルシュート)。
- **実測の JSON 遵守率(重要)**:

  | ラン | 構成 | LLM呼数 | fallback | 出典 |
  |---|---|--:|--:|---|
  | eco40v13 | 40人×1日(qwen3:8b) | 622 | **0** | `runs/eco40v13/summary.json`, devlog E5 |
  | eco80v2 | 80人×1日 | 1,493 | **0** | devlog E2 |
  | **eco80_3day** | **80人×3日** | **5,194** | **0** | `runs/eco80_3day/summary.json`, devlog E6 |
  | mem100 | 5人×100日(14,400step) | 2,897 | **0** | devlog E7, `docs/research/memory-100day-audit.md` |

  → **8B級 + format=json で fallback 0% が既に成立**。モデルを上げる主目的は「JSON 遵守」ではなく、後述の発話品質・ペルソナ忠実度・世界改変の観測にある。

### 1.3 内省の深さ(思考モード・1200token)
- 内省は **k(経験→内部状態の結合)の実装部位**(`src/society/cognition/reflection.py`)。就寝直後に1回、`reflect_max_tokens=1200` + **思考モード ON**(`model.reflect_think=true`)で回す(`conf/config.yaml:52-59`)。
- プロンプトは熟考を明示指示:「出来事を順に思い出す→なぜ印象に残ったか→気持ちの動き→明日への影響→結論だけJSON」(`reflection.py:_REFLECT_TASK`)。出力は `{summary, salient[], belief}`。
- **think 制御の実装**: chat 経路は `chat_template_kwargs={"enable_thinking": think}`、completions 経路は `/no_think` ソフトスイッチ(qwen3 固有)。`<think>…</think>` は本文から剥がす(`vllm.py`)。**think はキャッシュキーにも含む**(切替時の旧応答誤再生を防止、`src/society/llm/cache.py`)。
- → **要件: qwen3 系の「思考/非思考」二相を1モデルで切替できること**が実装と密結合。Qwen3/3.5/3.6 の hybrid thinking はこの前提に最も合う(§2.1)。DeepSeek-R1 蒸留系のような「常時 reasoning・冗長 `<think>`」は内省には向くが短文発話には冗長(§2.4)。
- 内省は全呼び出しの **約4%**(eco80_3day: reflect 213 / recall 213 が計 8.2%、うち reflect 213=4.1%)。**重い1200token呼はレアで、95%超は ≤320token 呼**。→ 階層構成(§3)の合理的根拠。

### 1.4 ツール(propose 等)の自発使用 ★最大の未解決問題
- 「世界を変えるツール」5種(propose/host_event/post_flyer/found_group/open_venture)は**中立提示**(勧誘なし、`deliberate.py:_equip_section`/tools.offer_text)。
- **実測: 実LLM は3ラン合計で 2,654回の明示提示に対しツール使用 0回**(`docs/research/world-change-motivation.md`)。組織化動詞を含む発話は 7,628件中実質1件。不満由来の変革意図 0件。
- 診断: 一部は**内部状態機構の飽和**(efficacy 天井0.996 / grievance 床0.001 で個体差消失)= モデル非依存の設計問題。一方で **RLHF instruct の受動性・同調性**も一因たりうる(`docs/lit/llm__agents-validity-model-choice.md`: peer 同調 最大85.5%、mode collapse で tail 潰し)。
- → **モデル選定の第一級論点**: 「世界改変者の創発」を観たいなら、instruct の迎合が現象を潰していないかを **model×k 交互作用**で検証する必要がある(§4-1)。abliterated/base 対照は `docs/lit/infra__model-choice-conflict.md` で既に設計済み。

### 1.5 短文(≤320token)の生成品質
- 発話・投稿・DM は `max_tokens=320`(`conf/config.yaml`)。会話は「テンポよく短く」が設計思想(infra summary §6「短トークン制限でテンポよく」)。
- 要件: **短い出力でも人格・文脈・SNS口語らしさが出る**こと、かつ **話題の多様性**(distinct-2 監視、Verbalized Sampling、`docs/ecosystem-design.md §3`)。短文品質は「小さいモデルほど不利」ではなく、**日本語口語の自然さ**が効く軸。

### 1.6 スループット(本番=1万〜3万エージェント×100日)
- ハード: **RTX A5000 24GB × 7、単一ノード**が第一候補(`docs/ops-production.md §0`、2026-07-06 ユーザー情報)。vLLM を各GPUに1インスタンス、`servers` に7本並べ FleetLLM で sticky routing。
- **呼数の実測から見た負荷の実体**:
  - eco80_3day: 5,194呼 / 432step = **12.0呼/step**(80人)。1人1日あたり **21.6呼**(5,194 ÷ (80×3))。
  - 内訳: deliberate 4,592 / reflect 213 / recall 213 / plan 176。**reflect(1200tok think)は4.1%**、残り ~96% は ≤320tok。
- **スケール時の律速は「エージェント数」ではなく「毎step の LLM 予算」**: `lod.max_llm_per_step=300`(`conf/config.yaml:265`)が上限。1万〜3万人でも 1step に LLM を撃つのは最大300体で、残りは routine に落ちる(欲求駆動発火+予算で間引く設計、`docs/ecosystem-design.md §1`)。
  - 総呼数の上限 ≈ 300/step × 144step/日 × 100日 = **432万呼(キャップ時)**。エージェントを増やしても総呼数はこの天井で頭打ち(混雑・多様性は増える)。
  - → **スループット要件の本質 = 7×A5000 で「毎step ~300呼(~96%が≤320tok・~4%が≤1200tok think)」を、狙う step あたり実時間内に捌く**こと。実時間/step の目安(infra: 現実30秒=1step)を厳守するかはランの長さと相談(100日×144×30秒=約50時間の連続運転になるため、本選では step 実時間をどこまで許すかが設計判断)。**具体的なトークン/秒は本選実機で `scripts/bench.py` により実測して埋める**(ops §4、未測定値は書かない)。
- 効く道具: **INT4量子化 + 連続バッチ + chunked-prefill + swap-space 0**(VRAM あふれの15〜35倍ペナルティ回避、infra summary §5)、**prefix caching + agent-id sticky routing**(§1.9)。

### 1.7 決定論・再現性(温度・シード)
- `temperature=0.7`(既定)。**実LLMは初回非決定的**(サーバ側サンプリング。seed 固定してもバッチ構成で揺れる)。**再現性の実体は応答キャッシュ**(`llm_cache.jsonl`、キー=`sha256(backend.name + params + prompt)`、`cache.py`)。
- `backend.name` は **URL 非依存(モデル名ベース)**なので、サーバ台数/URL を変えてもキャッシュは有効(D13、ops §5)。**`model.name` を変えるとキャッシュは別物**。
- モデル選定への含意: **MoE モデルは expert routing がバッチ構成で揺れやすく、初回の非決定性がより大きい可能性**(要実機確認)。論文用 k* データは「初回ランでキャッシュ生成→再生で完全再現」の運用で担保するので、**キャッシュ規律(同一 name・同一 tier 構成)が最優先**。temperature=0 でも完全一致は保証されない(ops §5)。

### 1.8 ライセンス(ハッカソン・論文公開可)
- 要件: **配布・改変・(準)商用・論文での再現公開**に耐えること。最も安全なのは **Apache-2.0 / MIT**。
- Qwen3/3.5/3.6 = **Apache-2.0**(§2.1)。llm-jp = Apache-2.0。Phi-4 = MIT。DeepSeek-R1 蒸留 = ベースに追随(Qwen2.5系=Apache / Llama70B系=Llama license)。
- **注意が要るもの**: Gemma(Gemma 利用規約)、Llama 系(Llama Community License=月間7億MAU制限等)、そして**日本語特化の多く(Sarashina=NonCommercial、PLaMo=Non-Commercial)は非商用**でハッカソン配備の障害になりうる(§2.5、要一次確認)。

### 1.9 プロンプトキャッシュ(APC)との相性 — 長い共通prefix
- プロンプトは **「共通部を先頭・個別部を後ろ」**に構成(`deliberate.py` 冒頭コメント: "APC 効率のため")。ヘッダ(labeling_mode は run 内固定)→ ペルソナ → 個別文脈の順。
- **sticky routing**: FleetLLM が rng_key から agent_id を抜き、同一エージェント→同一サーバに固定。**同じペルソナ+履歴という長い共通prefix が毎回同じGPUに当たり、vLLM の prefix cache が単一機の天井(~96%)近くまで効く**(`docs/lit/infra__storage-routing.md`、実測系の主張)。
- モデル選定への含意: **prefix caching が効くモデル/構成であること**(vLLM 対応必須)。長ペルソナで prefix が長いほど sticky routing の利得が大きい。Gated DeltaNet 系(Qwen3.5/3.6)は KV キャッシュ費用が低く長prefixに有利だが、本シミュは `--max-model-len 8192` の短文中心なので主便益は throughput 側。

### 1.10 要件サマリ(優先度つき)

| # | 要件 | 優先度 | 根拠 | モデル選定への効き |
|---|---|:--:|---|---|
| R1 | 日本語の自然な一人称発話 | ★★★ | deliberate.py ヘッダ/反復抑制 | 日本語ベンチ・口語の自然さ |
| R2 | 行動JSON遵守(fallback最小) | ★★★ | parse_action / 実測 fallback 0% | 指示追従・guided decoding 対応 |
| R3 | 思考モード内省(1200tok) | ★★☆ | reflection.py / think seam | hybrid thinking 内蔵が理想 |
| R4 | 長期ペルソナ一貫性(100日) | ★★★ | memory-100day-audit | persona drift 耐性 |
| R5 | 短文≤320tok の品質・多様性 | ★★☆ | max_tokens=320 / distinct-2 | 収斂しない日本語口語 |
| R6 | スループット(毎step~300呼) | ★★★ | lod=300 / bench / A5000×7 | INT4適性・vLLM throughput |
| R7 | 再現性(キャッシュ規律) | ★★☆ | cache.py / ops §5 | MoE非決定性・name固定 |
| R8 | ライセンス(公開・配備可) | ★★★ | ops / 論文公開 | Apache/MIT が安全 |
| R9 | APC/sticky routing 適合 | ★★☆ | infra storage-routing | vLLM prefix caching |
| R10 | 世界改変の観測を潰さない | ★★☆ | world-change-motivation / validity | instruct×abliterated 対照 |

---

## 2. 候補モデルの文献収集(出典リンク)

> **VRAM 見積りの前提**: 重みのみの概算。INT4(AWQ/GPTQ)≈ パラメータ数 × 0.5〜0.6 バイト、FP8 ≈ ×1 バイト、FP16 ≈ ×2 バイト。これに KV キャッシュ(`--max-model-len 8192` なら小)+ ランタイム余裕を足す。**A5000=24GB / gpu-memory-utilization 0.90 ≈ 実効21.6GB**。実測は本選で。

### 2.1 Qwen3 系(本命ファミリ・Apache-2.0・思考モード内蔵)
- **Qwen3(2025-05)**: dense 6種(0.6B/1.7B/4B/8B/14B/32B)+ MoE 2種(30B-A3B/235B-A22B)。**思考/非思考を1モデルで統一切替**、thinking budget 機構。**全モデル Apache-2.0**。日本語含む多言語。出典: [Qwen3 Technical Report (arXiv:2505.09388)](https://arxiv.org/abs/2505.09388)。
- **Qwen3.5(2026-02〜03)**: dense(0.8B/2B/4B/**9B**/**27B**)+ MoE(35B-A3B / 122B-A10B / 397B-A17B フラッグシップ)。**注意点(公式カードで確認・旧記述の訂正)**: 27B は **dense** で、アーキは **Gated DeltaNet(線形注意)層 + Gated(フル)Attention 層のハイブリッド**(カード表記のレイアウト = `16 × (3×(GatedDeltaNet→FFN) → 1×(GatedAttention→FFN))`)。**MoE は -A3B/-A10B/-A17B の MoE 系のみ**で、27B dense を「スパースMoE」と書くのは誤り。思考モード既定 ON(`<think>…</think>`)、**262,144 ネイティブ文脈・最大 1,010,000 まで拡張**、Apache-2.0、多言語 201。カード確認ベンチ: MMLU-Pro 86.1。リリース: 27B/35B-A3B/122B-A10B = 2026-02-24、9B/4B/2B/0.8B = 2026-03-02。出典: [HF: Qwen/Qwen3.5-27B(公式カード)](https://huggingface.co/Qwen/Qwen3.5-27B)。
- **Qwen3.6(2026-04)**: **dense 27B(2026-04-22)** + **MoE 35B-A3B(2026-04-16)** の2本立て。27B dense = Hidden 5120、思考モード既定 ON、262K(→ 1,010,000 拡張)、Apache-2.0。**公式HFカードで確認したベンチ: SWE-bench Verified 77.2 / MMLU-Pro 86.2 / AIME26 94.1**(2026-07-07 に Web 照合済み=自己申告だが実在の掲載値)。JA 個別スコアはカード非掲載。出典: [HF: Qwen/Qwen3.6-27B(公式カード)](https://huggingface.co/Qwen/Qwen3.6-27B)、[HF: Qwen/Qwen3.6-35B-A3B](https://huggingface.co/Qwen/Qwen3.6-35B-A3B)、[QwenLM/Qwen3.6(GitHub)](https://github.com/QwenLM/Qwen3.6)。
- **日本語の位置**(Nejumi 4): **Qwen3.5-27B が開重み初の 0.80 突破(0.8049, 総合11位)**で、開重み日本語最上位クラス。出典(公式): [Nejumi LLM Leaderboard(wandb-japan)](https://wandb.ai/wandb-japan/llm-leaderboard/reports/Nejumi-LLM-Leaderboard-Evaluating-Japanese-Language-Proficiency--Vmlldzo2MzU3NzIy)、[wandb/llm-leaderboard(GitHub, リリースノート)](https://github.com/wandb/llm-leaderboard/releases)。🔶 順位・数値の細部は二次記事([Qualiteg 2025ランキング](https://blog.qualiteg.com/llm-ranking-2025-10-11/))経由もあり、採用前に公式ボードで裏取り。
- **本シミュ適合**: 思考モード内蔵(R3)、Apache(R8)、日本語最上位(R1)、vLLM 一級対応(R6/R9)。**現行 seam(enable_thinking / /no_think / think剥がし)が qwen3 系前提**で書かれており移行コスト最小。カードは JA を明示列挙しないが、Nejumi 実績が JA 実力を裏づける。

### 2.2 Gemma 3(Google・多言語140+・Gemma ライセンス)
- サイズ 270M/1B/4B/12B/**27B**。4B以上はマルチモーダル・**128K文脈**、140言語超。27Bは14Tトークン学習。出典: [Gemma 3 Technical Report (arXiv:2503.19786)](https://arxiv.org/html/2503.19786v1)、[Introducing Gemma 3(Google Developers Blog)](https://developers.googleblog.com/en/introducing-gemma3/)、[HF: google/gemma-3-27b-it](https://huggingface.co/google/gemma-3-27b-it)。
- 適合/懸念: 日本語・指示追従は良好で vLLM 対応。ただし **専用思考モードなし**(R3 は別モデル/プロンプトで代替要)、**ライセンスが Gemma 利用規約**(Apache ではない=R8 で一段の確認)。マルチモーダルは本シミュ不要(テキストのみ)。

### 2.3 Llama 3.3 / ELYZA・Swallow(Llama ライセンス)
- **Llama-3.3-70B-Instruct**: 高品質だが 70B=INT4 ~35GB で **単機A5000に載らず 2GPU tensor-parallel 必須**。Llama Community License。
- **ELYZA(Llama-3.1-ELYZA-JP 8B/70B)**: 日本語継続学習。8B は単機INT4 ~5GB で軽量・JA 良好。70B は要TP。ライセンスは Llama 追随。🔶 2026-03 に KDDI/ELYZA の Llama-3.1-ELYZA-JP-70B がデジタル庁「Gennai」基盤へ採用との報道([codenote まとめ](https://codenote.net/en/posts/japanese-local-llm-development-case-studies/)、二次)。
- **Swallow(東工大系, Llama 継続学習)**: 日本語強化。公式評価: [Swallow LLM Leaderboard](https://swallow-llm.github.io/leaderboard/about.en.html)。
- 適合/懸念: JA は良いが **思考モードなし**、ライセンスが Llama(R8 一段確認)、70B 級は VRAM で階層構成前提。

### 2.4 DeepSeek-R1 蒸留系(reasoning 特化・内省ティア候補)
- **DeepSeek-R1-Distill-Qwen-14B/32B**(ベース Qwen2.5=**Apache-2.0**)、**-Llama-70B**(ベース Llama3.3=Llama license)。800k の R1 生成サンプルで蒸留。出典: [HF: DeepSeek-R1-Distill-Qwen-32B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B)、[HF: -Qwen-14B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-14B)、[DeepSeek-R1(GitHub)](https://github.com/deepseek-ai/deepseek-r1)。
- 適合/懸念: **長い `<think>` を出す reasoning 志向**で、内省ティア(R3)には好適。ただし **短文発話(R5)には冗長**で、思考の抑制制御が qwen3 の enable_thinking ほど綺麗でない。日本語は Qwen3.5/3.6 の方が新しく強い見込み。**Qwen3/3.5/3.6 が hybrid thinking を内蔵した今、蒸留系をわざわざ使う積極理由は薄い**(内省ティアも同系 Qwen で足りる)。

### 2.5 日本語特化(品質は高いが多くが非商用=配備の壁)
- **Sarashina2(SB Intuitions)**: 日英コード 5:4:1 の 2.1T 学習。🔶 **Sarashina Model NonCommercial License**(非商用)= ハッカソン/配備に不適の恐れ。出典(二次): [codenote まとめ](https://codenote.net/en/posts/japanese-local-llm-development-case-studies/)。→ 採用検討時は **SB Intuitions 公式カードでライセンス一次確認**。
- **PLaMo 2 / 2.2 Prime 31B(PFN)**: SSM+SWA ハイブリッド。🔶 JFBench で GPT-5.1 相当・150+自治体で採用との記述。ただし 🔶 **PLaMo Non-Commercial License**(非商用)。出典(二次): 同上、[pfnet-research(GitHub)](https://github.com/pfnet-research/japanese-lm-fin-harness)。→ **PFN 公式でライセンス一次確認**。
- **llm-jp-3 / llm-jp-4(NII)**: **Apache-2.0**(R8 クリーン)。日本語コミュニティの公開モデル。出典(公式): [LLM-jp Resources(NII)](https://llm-jp.nii.ac.jp/en/resources-en/)、[awesome-japanese-llm(llm-jp)](https://github.com/llm-jp/awesome-japanese-llm)。フロンティア Qwen より素の能力は一段下だが、**ライセンスが完全に自由**なのは論文公開で強い。
- **NVIDIA Nemotron Nano 9B JP**: Nejumi 4 の **sub-10B で1位**・日本語開発モデル最上位クラス(0.7111)。小型ティア候補。出典(公式): [NVIDIA Nemotron Nano 9B Japanese(HF 公式ブログ)](https://huggingface.co/blog/nvidia/nemotron-nano-9b-v2-japanese-ja)。→ ライセンス(NVIDIA Open Model License)の再利用条件は一次確認。
- **Rakuten AI 3.0(2026-03-17, ~700B MoE, Apache-2.0)**: GENIAC(経産省/NEDO)枠で公開。JA ベンチで GPT-4o 超えと自社発表(JamC-QA 76.9 / MMLU-ProX-JA 71.7 / MATH-100-JA 86.9 / M-IFEval-JA 72.1、JA MT-Bench 8.88 — いずれも GPT-4o 上回りと主張)。**ライセンスは Apache-2.0 で公開配布は可**だが、**~700B は A5000 24GB×7 の VRAM 予算に到底載らない**(本用途では規模外=採用不可)。加えて 🔶 **config.json のアーキ宣言が `DeepseekV3ForCausalLM`= DeepSeek-V3 ベースの JA 追加学習**との指摘があり(ライセンス/来歴の議論あり)、参照時は一次確認。出典(公式): [Rakuten AI 3.0 press(Rakuten Group)](https://global.rakuten.com/corp/news/press/2026/0317_01.html)、🔶 来歴議論: [BigGo Finance](https://finance.biggo.com/news/202603181324_Rakuten_AI_3.0_Exposed_as_DeepSeek_V3_Rebrand)。→ **JA 最強クラスの Apache 開重みでも、A5000 予算では大 MoE は選外**という好例(VRAM 制約が JA 品質に優先する場面)。
- **NTT tsuzumi 2(~30B)**: 🔶 単一H100で JA MT-bench が GPT-5 近傍との記述(二次)。ただし **NTT の提供形態は商用/限定配布**の可能性が高く、**開重み配布・論文再現公開に不向きな恐れ**=本用途では優先度低。要一次確認。

### 2.6 LLM を社会エージェントに使う先行研究(妥当性の土台)
- **Generative Agents(Park+ 2023, arXiv:2304.03442)**: observation/planning/reflection のメモリ機構で長期一貫の創発行動。本シミュの内省・計画・記憶設計の直接の祖(reflection.py/planning.py が踏襲)。長期一貫性には「増え続ける記憶の retrieve→reflect→plan」が要る、という主張。
- **ペルソナ一貫性/drift**: off-the-shelf LLM は長対話でペルソナから逸脱・自己矛盾・役割放棄を起こす([Consistently Simulating Human Personas with Multi-Turn RL, arXiv:2511.00222](https://arxiv.org/abs/2511.00222))。→ R4 の学術的裏づけ。本シミュは「就寝内省で beliefs を再固定+関係台帳」で drift を抑える設計。
- **小型モデルの構造化出力**: 小型ほど「正しさ」と「形式順守」の乖離が大きく、grammar 制約(XGrammar/Outlines 等)で妥当性を担保する代わりにレイテンシ・タスク性能のトレードオフがある([JSONSchemaBench, arXiv:2501.10868](https://arxiv.org/pdf/2501.10868))。→ R2 で「guided_json 対応 vLLM を使えば小型でも堅い」という運用方針の裏づけ(実測でも8Bは既に fallback 0%)。
- **RLHF instruct の同調・多様性減(妥当性ゲート)**: RLHF は迎合を増幅し tail/異論を潰す(`docs/lit/llm__agents-validity-model-choice.md`、`docs/lit/mas__li2026_moltbook.md`)。→ R10・§4-1 の中核。マルチエージェント社会シミュの先行(OASIS/Concordia/AgentScope)は `docs/lit/mas__*` に既収。

### 2.7 候補比較表(要件×モデル)

> 記号: ◎=強い / ○=良好 / △=条件付き / ×=不利・不適。VRAM は **A5000 単機・INT4 見積り**(重みのみ概算)。「思考」= 専用 thinking モードの有無。

| モデル | 規模(総/活性) | 想定VRAM(INT4) | 日本語(R1) | 指示追従・JSON(R2) | 思考(R3) | vLLM/throughput(R6/R9) | ライセンス(R8) | 出典 |
|---|---|--:|:--:|:--:|:--:|:--:|---|---|
| **Qwen3-8B** | 8B dense | ~5GB | ○ | ◎(実測fallback0%) | ◎(内蔵) | ◎ 単機で高並列 | Apache-2.0 | [arXiv:2505.09388](https://arxiv.org/abs/2505.09388) |
| **Qwen3-14B** | 14B dense | ~8GB | ○〜◎ | ◎ | ◎ | ◎ | Apache-2.0 | 同上 |
| **Qwen3-32B** | 32B dense | ~17GB | ◎ | ◎ | ◎ | ○(単機可・並列は落ちる) | Apache-2.0 | 同上 |
| **Qwen3.5-27B** | 27B dense(GDN hybrid) | ~14GB | ◎(Nejumi4開重み最上位) | ◎ | ◎(既定ON) | ◎ 長文脈・低KV | Apache-2.0 | [HF](https://huggingface.co/Qwen/Qwen3.5-27B) |
| **Qwen3.5-35B-A3B** | 35B/3B活性 MoE | ~18GB | ◎ | ◎ | ◎ | ◎ 活性3Bで高速(要MoE非決定性注意) | Apache-2.0 | [HF](https://huggingface.co/Qwen/Qwen3.5-27B) |
| **Qwen3.6-27B** | 27B dense | ~14GB | ◎(推定) | ◎ | ◎(既定ON) | ◎ | Apache-2.0 | [HF](https://huggingface.co/Qwen/Qwen3.6-27B) |
| **Gemma 3 27B** | 27B dense | ~14GB | ○〜◎ | ○ | ×(専用なし) | ○ | Gemma 規約 | [arXiv:2503.19786](https://arxiv.org/html/2503.19786v1) |
| **Llama-3.3-70B** | 70B dense | ~35GB(要2GPU) | ○ | ○ | × | △(TP必須) | Llama 規約 | [HF via DeepSeek card](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-70B) |
| **Phi-4** | 14B dense | ~8GB | △(英語中心) | ○ | × | ◎ | MIT | [arXiv:2412.08905](https://arxiv.org/abs/2412.08905) |
| **DeepSeek-R1-Distill-Qwen-32B** | 32B dense | ~17GB | ○ | ○ | ◎(冗長) | ○ | Apache-2.0 | [HF](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B) |
| **llm-jp-3/4** | 各種 | 規模次第 | ◎(JA特化) | ○ | △ | ○ | **Apache-2.0** | [NII](https://llm-jp.nii.ac.jp/en/resources-en/) |
| **ELYZA Llama-3.1-JP-8B** | 8B dense | ~5GB | ◎(JA特化) | ○ | × | ◎ | Llama 規約 | 🔶 [codenote](https://codenote.net/en/posts/japanese-local-llm-development-case-studies/) |
| **Nemotron Nano 9B JP** | 9B dense | ~5.5GB | ◎(Nejumi4 sub-10B 1位) | ○ | △ | ◎ | NVIDIA Open Model | [NVIDIA(HF blog)](https://huggingface.co/blog/nvidia/nemotron-nano-9b-v2-japanese-ja) |
| **Sarashina2** | 8x70B(MoE)等 | 大 | ◎(JA特化) | ○ | × | × 規模大 | 🔶 **NonCommercial** | 🔶 [codenote](https://codenote.net/en/posts/japanese-local-llm-development-case-studies/) |
| **PLaMo 2.2 Prime 31B** | 31B(SSM hybrid) | ~16GB | ◎(JFBench高) | ○ | △ | ○ | 🔶 **Non-Commercial** | 🔶 [codenote](https://codenote.net/en/posts/japanese-local-llm-development-case-studies/) |
| **Rakuten AI 3.0** | ~700B MoE | ×(規模外・A5000不可) | ◎(GPT-4o超を主張) | ○ | × | ×(単機に載らず) | **Apache-2.0**(🔶DeepSeek-V3ベース議論) | [Rakuten press](https://global.rakuten.com/corp/news/press/2026/0317_01.html) |

> 表の「日本語」は Nejumi/Swallow 実績と一般評判の総合。Qwen3.5/3.6 のカードは JA を明示列挙しないが、Nejumi 4 で開重み最上位=実力は担保。非商用ライセンス(Sarashina/PLaMo)は **論文用の学術利用は可の場合が多いが、ハッカソン配備・公開配布で要注意**。

---

## 3. GPU構成別の構成案と試算(A5000 24GB × 7・vLLM 前提)

### 3.0 まず量子化の前提を正す(A5000 = Ampere の制約)★重要
- **A5000 は Ampere(sm_86)**。vLLM の **FP8 W8A8 のハード加速は Hopper/Ada のみ**(出典: [vLLM FP8 W8A8 docs](https://docs.vllm.ai/en/latest/quantization/fp8.html))。→ **A5000 で「FP8で高速化」は成立しにくい**(Marlin 経由の weight-only FP8 は動くが W8A8 の 1.6x スループット利得は得られない)。
- 加えて **27B を FP8(~28GB)にすると 24GB に載らない**。→ **実務解は AWQ/GPTQ の INT4**(27B≈14GB)。小型4bitは AWQ>GPTQ の報告([arXiv:2505.15030](https://arxiv.org/abs/2505.15030)、`infra__model-choice-conflict.md` 既収)。
- **結論**: infra summary の「FP8/4bit」という併記は、A5000 前提では **INT4(AWQ)一択に寄せる**のが妥当。ops-production.md の `--quantization awq` 例と整合。**FP8 を使うなら本選GPUが Ada/Hopper だった場合のみ**(現状は A5000 前提)。

### 3.1 呼数からの負荷試算(共通前提)
- 毎step の LLM 呼び出しは `lod.max_llm_per_step=300` が上限。内訳の実測比(eco80_3day)を保つと想定: **≤320tok 呼 ~96% / ≤1200tok think 呼 ~4%**。
- 7GPU に sticky routing で分散 → **1GPU あたり定常 ~43呼/step**(300÷7)。同一エージェントは同一GPUに固定=prefix cache が効く。
- reflect(think)は step あたり ~12呼(300×4%)で、これを大モデル/専用GPUに寄せられる(§3.3)。
- **実時間/秒あたりトークンは本選で bench 実測**(ops §4)。ここでは「毎step ~300呼を7GPUで捌く」を設計目標として構成を分ける。

### 3.2 構成案A — 均質艦隊(推奨・最短路)
- **7GPU すべてに同一モデル(Qwen3.5-27B or Qwen3.6-27B の AWQ-INT4、~14GB)**を1インスタンスずつ。`servers:` に800x×7、FleetLLM で agent-id sticky。
- 長所: **prefix cache 利得最大**(sticky が均質に効く)、キャッシュキー単純(name 1つ=再現性 R7 が堅い)、運用最小、ops-production の構成(A)そのまま。
- 短所: 27B で ≤320tok の会話も回すのは「やや過剰」。think(1200tok)も同じGPUで混ざり、ロングテール遅延が出うる → `--max-num-seqs` と予算(lod)で制御。
- 軽量版: **Qwen3-14B-AWQ(~8GB)×7** にすると 1GPU に複数プロセス or 大 KV 余裕で高並列。日本語がやや落ちるかは要 A/B(Nejumi では 27B が明確に上)。

```yaml
model:
  backend: vllm
  name: qwen3-society          # キャッシュキー(URL非依存・不変に保つ)
  temperature: 0.7
  max_tokens: 320
  reflect_max_tokens: 1200
  reflect_think: true
  cache: true
  servers: ["http://localhost:8000", ..., "http://localhost:8006"]   # 7本
```
起動は `--quantization awq --enable-prefix-caching --enable-chunked-prefill --swap-space 0 --gpu-memory-utilization 0.90 --max-model-len 8192`(ops §2-A)。

### 3.3 構成案B — 階層(内省=大 / 会話=小)★認知設計に一致
- **内省(reflect, ~4%・1200tok・think)を大モデルへ、会話・投稿・計画(~96%・≤320tok)を小モデル群へ**。`tiers` seam(ops §2-C)を使う。
  - reflect ティア: Qwen3-32B or Qwen3.5-27B を **GPU 2枚 tensor-parallel で1本**(深い内省=kの作用点なので質を厚く)。
  - default ティア: **Qwen3-4B/8B-AWQ を残り 5GPU に1本ずつ**(短文をテンポよく・高並列)。
- 長所: **認知の非対称設計(会話=短/内省=深)にハード配分が一致**(infra summary §4)。会話スループットを稼ぎつつ内省の質を落とさない。
- 短所: **tier で別モデルを混ぜると応答キャッシュが name 単位で共有される**ため、再現ランは同一 tier 構成を厳守(ops §5、キャッシュ規律の注意が増える)。運用複雑度↑。
```yaml
model:
  backend: vllm
  name: qwen3-society
  servers: ["http://localhost:8000","http://localhost:8002","http://localhost:8003","http://localhost:8004","http://localhost:8005","http://localhost:8006"]
  tiers:
    reflect: ["http://localhost:8000"]        # 大モデル1本(GPU0-1 をTP)
    default: ["http://localhost:8002", ...]   # 小モデル群5本
```

### 3.4 構成案C — model×k 実験(妥当性ゲート用)
- 目的: R10。「RLHF instruct の迎合が世界改変/異論を潰していないか」を **同一系列 instruct ⇔ abliterated** の対で検証(`infra__model-choice-conflict.md` の設計)。
- 運用: **ランを分けて `model.name` を差し替える**のが最もクリーン(1ラン=1モデルでキャッシュ・再現が単純)。同一量子化(AWQ)・同一手法で統一し、能力劣化を k* の交絡にしない。abliterated は劣化最小手法(例: Heretic 系)を選び、自前 TruthfulQA/GSM8K で裏取り。
- 注意: これは**追加実験の条件**であって本番既定ではない。既定運用=instruct(Qwen3.5/3.6-27B)、対照=abliterated。

### 3.5 構成の当てはめ早見

| 案 | reflect | 会話/投稿/計画 | prefix cache | 再現性 | 運用 | 向く局面 |
|---|---|---|:--:|:--:|:--:|---|
| A 均質艦隊 | 同一27B | 同一27B ×7 | ◎ | ◎(name1つ) | ◎最小 | まず動かす・本番既定 |
| A' 軽量均質 | 14B | 14B ×7 | ◎ | ◎ | ◎ | 会話量が支配・多並列優先 |
| B 階層 | 32B/27B(TP) | 4B/8B ×5 | ○ | △(tier固定要) | △ | 内省の質を厚く・会話高速両立 |
| C model×k | instruct/abliterated を別ラン | 同左 | ◎ | ◎(ラン分離) | ○ | 妥当性検証・論文の対照条件 |

---

## 4. 議論すべき論点リスト(断定しない)

1. **世界改変の観測 × RLHF 同調(最重要)**: ツール0使用は「飽和(モデル非依存)」と「instruct の受動性(モデル依存)」の交絡。**まず飽和(efficacy天井/grievance床)を機構側で解いてから**、instruct⇔abliterated の model×k で純粋なモデル効果を測るべきか? それとも並行して両方回すか?(§1.4 / §3.4)
2. **均質(A) vs 階層(B)**: 内省4%のために tier 分けの運用複雑度・キャッシュ規律コストを払う価値があるか。まず A で本選疎通→余裕があれば B、が安全か?
3. **モデル規模の落とし所**: Nejumi 4 で 27B が明確に上だが、**会話が支配的(96%)なので 8B〜14B でも足りる**可能性。日本語会話の「自然さ」は A/B ブラインド評価(LLM-judge κ ゲートは既実装)で決めるべきか。実測で 8B は既に fallback 0% なので、上げる根拠は「品質・多様性・drift 耐性」に限定して議論。
4. **Qwen 版数の固定**: 3.5-27B / 3.6-27B / 3-32B のどれを既定に? 新しいほど JA・思考は強いが、**seam(enable_thinking / think剥がし)の実挙動は本選疎通で要確認**(ops §7 の「思考ブロック混入」)。版を上げるとキャッシュが無効化(name 変更)= A段のゴールデンとの整合も論点。
5. **量子化の確定**: A5000 前提なら AWQ-INT4 で確定してよいか(§3.0)。本選GPUが Ada/Hopper だった場合に FP8 へ切替える分岐を残すか。AWQ 版が公式に無いモデルは自前量子化 or コミュニティ版の品質確認が要る。
6. **日本語特化 vs 汎用フロンティア**: Sarashina/PLaMo は JA 品質が高いが**非商用ライセンス**(要一次確認)。論文用の学術利用に限れば可か、ハッカソン配備で不可か。**Apache が完全に自由な llm-jp / Qwen** に寄せるのが安全という整理でよいか。
7. **MoE の再現性**: Qwen3.5-35B-A3B は活性3Bで高速だが、**expert routing のバッチ非決定性**が初回ランの揺れを増やす懸念(R7)。キャッシュ再生で最終再現は担保されるが、初回生成のばらつきが k 掃引に与える影響を bench で確認すべきか。
8. **話題収斂(mode collapse)対策**: qwen3:8b の「コーヒー/ラーメン収斂」はモデル更新(3.5/3.6)で改善するか、温度・Verbalized Sampling・プロンプト側で対処すべきか。**モデルを上げて解けるのか、機構で解くのか**の切り分けは A 段の実測で。
9. **内省ティアに reasoning 特化(R1蒸留)を混ぜるか**: hybrid thinking の Qwen で足りるなら不要。だが「深い世界観変容」を厚くしたいなら reflect だけ R1-Distill-Qwen-32B にする選択肢の是非(冗長 `<think>` と JA 品質のトレードオフ)。
10. **スループットの実測ゲート**: 本メモは呼数(300/step)ベースの設計目標まで。**トークン/秒・GPUあたり同時実行数・VRAM 実測は本選で `scripts/bench.py`** により埋める(ops の方針=未測定値を書かない)。100日連続運転の実時間見積り(step 実時間の許容)も併せて決める。

---

## 5. 出典(公式優先。🔶=二次情報)

**モデル(公式)**
- [Qwen3 Technical Report — arXiv:2505.09388](https://arxiv.org/abs/2505.09388)
- [Qwen/Qwen3.5-27B — HF 公式カード](https://huggingface.co/Qwen/Qwen3.5-27B)
- [Qwen/Qwen3.6-27B — HF 公式カード](https://huggingface.co/Qwen/Qwen3.6-27B) / [Qwen/Qwen3.6-35B-A3B — HF 公式カード](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) / [QwenLM/Qwen3.6 — GitHub](https://github.com/QwenLM/Qwen3.6)
- [Gemma 3 Technical Report — arXiv:2503.19786](https://arxiv.org/html/2503.19786v1) / [Introducing Gemma 3 — Google Developers Blog](https://developers.googleblog.com/en/introducing-gemma3/) / [google/gemma-3-27b-it — HF](https://huggingface.co/google/gemma-3-27b-it)
- [Phi-4 Technical Report — arXiv:2412.08905](https://arxiv.org/abs/2412.08905)
- [DeepSeek-R1 — GitHub](https://github.com/deepseek-ai/deepseek-r1) / [-Distill-Qwen-32B — HF](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B) / [-Qwen-14B — HF](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-14B) / [-Llama-70B — HF](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-70B)
- [LLM-jp Resources — NII 公式](https://llm-jp.nii.ac.jp/en/resources-en/) / [awesome-japanese-llm — llm-jp](https://github.com/llm-jp/awesome-japanese-llm)
- [NVIDIA Nemotron Nano 9B Japanese — HF 公式ブログ](https://huggingface.co/blog/nvidia/nemotron-nano-9b-v2-japanese-ja)
- [Rakuten AI 3.0(~700B MoE, Apache-2.0)— Rakuten Group 公式プレス](https://global.rakuten.com/corp/news/press/2026/0317_01.html)(🔶 来歴議論: [BigGo Finance](https://finance.biggo.com/news/202603181324_Rakuten_AI_3.0_Exposed_as_DeepSeek_V3_Rebrand))

**ベンチマーク / 日本語評価(公式)**
- [Nejumi LLM Leaderboard — Weights & Biases Japan](https://wandb.ai/wandb-japan/llm-leaderboard/reports/Nejumi-LLM-Leaderboard-Evaluating-Japanese-Language-Proficiency--Vmlldzo2MzU3NzIy) / [wandb/llm-leaderboard — GitHub(リリースノート)](https://github.com/wandb/llm-leaderboard/releases)
- [Swallow LLM Leaderboard](https://swallow-llm.github.io/leaderboard/about.en.html)
- [Open Japanese LLM Leaderboard — llm-jp(HF Space)](https://huggingface.co/spaces/llm-jp/open-japanese-llm-leaderboard)

**推論基盤 / 量子化(公式)**
- [vLLM FP8 W8A8 — 公式ドキュメント(Hopper/Ada のみ加速)](https://docs.vllm.ai/en/latest/quantization/fp8.html)
- [vLLM Router / prefix-aware routing — 公式](https://blog.vllm.ai/2025/12/13/vllm-router-release.html)(`infra__storage-routing.md` 既収)
- [小型4bit は AWQ>GPTQ — arXiv:2505.15030](https://arxiv.org/abs/2505.15030)

**エージェント妥当性 / ペルソナ(公式)**
- [Generative Agents — arXiv:2304.03442](https://ar5iv.labs.arxiv.org/html/2304.03442)
- [Consistently Simulating Human Personas with Multi-Turn RL(persona drift)— arXiv:2511.00222](https://arxiv.org/abs/2511.00222)
- [JSONSchemaBench(構造化出力)— arXiv:2501.10868](https://arxiv.org/pdf/2501.10868)

**二次情報(裏取り前提・🔶)**: [Qualiteg 日本語LLMランキング2025](https://blog.qualiteg.com/llm-ranking-2025-10-11/) / [codenote 国産LLMサーベイ](https://codenote.net/en/posts/japanese-local-llm-development-case-studies/) / [lilting.ch 日本語LLM比較 2026-04](https://lilting.ch/en/articles/japanese-llm-options-compared)

**リポジトリ内の関連(既存)**
- `docs/lit/llm__agents-validity-model-choice.md`(RLHF 同調=妥当性ゲート)
- `docs/lit/infra__model-choice-conflict.md`(Qwen 確定 vs 妥当性の衝突・abliterated 対照)
- `docs/lit/infra__storage-routing.md`(sticky routing / prefix cache ~96%)
- `docs/lit/shibuya_sim_infra_summary.md`(GPU配置・採用モデル・VRAM 防衛)
- `docs/ops-production.md`(vLLM 艦隊・3構成・キャッシュ規律)
- `docs/research/world-change-motivation.md`(ツール0使用・飽和の実証)
- `docs/research/memory-100day-audit.md`(100日で劣化なし)
