# 計算量・推論量の削減 — 「少ない計算で現実の人々を再現する」ための技法棚卸し

- 作成: 2026-07-11 / 担当: Opus 4.8(リサーチ) / 種別: 調査のみ(**コード非編集**・実LLM実行なし・commit なし)
- 目的: ユーザーの核心的問い「**いかに少ない計算量・推論量で現実の人々を再現できるか**(実現できればエージェント数と時間を大幅に増やせる)」に対し、(1)先行 LLM-ABM のスケール実測、(2)呼数削減・プロンプト削減・推論高速化・蒸留/ハイブリッド・観察最適化の各技法を、**期待削減 × 忠実度リスク × 決定論/R1 との相性 × 実装コスト**で棚卸しする。**実装はしない**(計画立案の材料)。
- 方針: 数値は出典付き。未確認・未実測は「**不明/要検証**」と正直に記す(捏造禁止)。二次情報(ブログ・ベンダー記事)は 🔶 を付し絶対値の根拠にしない。
- 前提の必読: [`docs/research/token-budgets.md`](token-budgets.md)(AGA=トークン30〜43%削減でも believability 維持)、[`docs/research/scale-audit-100days.md`](scale-audit-100days.md)(呼数・律速)、[`docs/research/llm-model-selection.md`](llm-model-selection.md)(A5000=Ampere・INT4)、`src/society/cognition/lod.py`(発火予算)、`src/society/llm/cache.py`(応答キャッシュ)、`src/society/llm/{vllm,fleet}.py`(prefix cache + sticky routing)。

---

## 0. 3行サマリ(結論を先に)

1. **「入力を削る」より「decode(出力)を締める+呼数を減らす」が我々の主レバー**。vLLM のスループットは decode 支配で、入力プロンプト(現行 530〜1,040 tok)は文脈窓に対し軽微(token-budgets §2.2、scale-audit §3.3)。→ LLMLingua 等の**プロンプト圧縮は我々では効きが薄い**(短プロンプト+圧縮器の追加呼で相殺しうる)。効くのは **reflect 出力上限の右サイズ化**と**呼数削減**。
2. **「タダに近い」勝ち筋は既に半分実装済み**: LOD 発火制御(実測 4.1〜11.4% = 約12倍削減)、agent-id sticky routing による prefix cache(単一機の天井 ~96% まで回復・**出力分布を変えないので決定論/R1 に完全中立**)、連続バッチ(静的比 最大23倍)。**未導入で低リスクなのは speculative decoding(vLLM で最大2.8倍・出力は目標モデルと同分布=無損失)**。これらは「何を計算するか」を変えないので**忠実度・決定論・R1 いずれも無傷**。
3. **最大の削減(数万倍)を出す archetype/群近似(AgentTorch=42,000倍)や蒸留・novelty ルーティングは、"個体の異質性"と"稀な世界改変者"を潰すため我々の研究目的(k\* = 個体レベルの創発)と正面衝突する**。呼数を根本から減らすこれらは魅力的だが、**Y_external を担う個体の分散そのものを消す**ので、採用するなら「前景=フル LLM の少数個体+背景=群近似の多数個体」という**階層化**に限る。忠実度検証(前景 vs 背景の分布一致)が前提。

> 一言でいえば: **「情報量(入力トークン)」を削るのではなく、「同じ意味の計算を安く回す」推論高速化を最大化し、呼数削減は"創発の材料を消さない範囲"に留める**。これが AGA(believability は行動の有限性で決まる=トークン長ではない)と我々の R1(呼数の k 非依存)の両制約に最も素直。

---

## 1. 前提 — 我々の実測値と「レバーはどこに効くか」

| 実測項目 | 値 | 出典 |
|---|---|---|
| LOD 発火率(agent×step のうち LLM を撃つ割合) | **4.1〜11.4%**(約12倍の呼数削減) | 依頼提示の実測 / lod.py + drive |
| 入力プロンプト | 530〜1,040 tok/呼(本番リッチ最大 ~1,400) | token-budgets §2.2 |
| 出力上限 | speak 320 / plan 448 / reflect 2048 cap | 依頼提示 / conf |
| 応答キャッシュ ヒット率 | **0%**(プロンプトに step/時刻/文脈の動的部分=完全一致せず) | cache.py + 依頼提示 |
| 実測ラン | mock 300体×100日=132分 / 実LLM 20体×7日=95分(1,635呼) | 依頼提示 |
| ハード | qwen3:4b ローカル1GPU → 本選 7GPU×1ノード(A5000 24GB×7 想定) | llm-model-selection §0 |
| 絶対制約 | **決定論**(同seed同設定→L1イベント列バイト一致)/ **R1**(呼数は k 非依存) | プロジェクト規約 |

**ここから導かれる設計上の効き所(重要)**:

- **A. 律速は decode(出力生成)、入力ではない。** scale-audit §3.2/§3.3 は総トークンの支配項を「reflect(思考モード+長出力)」と算定。vLLM の decode は1トークンずつで、prefill(入力)は安い。→ **出力上限(特に reflect)の右サイズ化がスループットの主レバー**(token-budgets §3.3 と一致)。**入力を削る技法(プロンプト圧縮)は我々では優先度が低い**。
- **B. 応答キャッシュは"再現性の実体"であって"初回計算の節約"ではない。** ヒット率0%は設計どおり(動的プロンプト=毎回別キー)。**ヒット率を上げる=プロンプトを反復させる=現実性を捨てる**ので、キャッシュで初回コストは減らせない。初回コストを減らすのは別系統(推論高速化・呼数削減)。
- **C. 呼数を減らす技法は R1 に直接触れる。** LOD 発火・plan/reflect の回数は k と独立でなければならない(scale-audit B9)。呼数を動かす削減(routine caching・novelty ルーティング・archetype)は**「削減率が k と相関しない」ことを設計で保証**しないと k\* を汚す。
- **D. モデルを変える技法(量子化・蒸留)はキャッシュ名(`backend.name`)を変える=別キャッシュ。** 決定論は各モデル内で保たれるが、比較ランはキャッシュを共有しない(実LLM再走)。

---

## 2. 先行 LLM-ABM のスケール実測(課題1)

> 凡例: トークン/コストを開示する論文はほぼ無い(token-budgets §1 と同じ所見)。**開示があるのは「エージェント数・呼数・壁時計時間・GPU台数」まで**。効率化"手法"は開示されるが1呼トークンは論文の関心外。

| プロジェクト | 規模 | モデル/推論 | スケール実測 | 効率化の要 | 出典 |
|---|---|---|---|---|---|
| **Generative Agents**(Park+ 2023) | 25体×2日 | gpt-3.5-turbo | 「**数千ドル**」・実時間数日 | importance ゲート発火・reflection 1日2〜3回・記憶 top-k 想起 | [arXiv:2304.03442](https://arxiv.org/abs/2304.03442) |
| **AgentSociety**(清華/復旦 2025) | **10,000〜30,000体**・500万 interaction | OpenAI/DeepSeek/**vLLM**/ollama いずれも可(実測モデル非開示) | 「real-time より速い」と主張(§6 実数は本文抜粋に無し=**要検証**) | **Ray 分散 + agent group(複数体を1プロセスに束ね TCP ポート枯渇=65,535上限を回避)+ asyncio で I/O 秘匿**。モデル最適化でなく**配線最適化**。トークン/GPU/コスト**全て非開示** | [arXiv:2502.08691](https://arxiv.org/abs/2502.08691) / [github](https://github.com/tsinghua-fib-lab/agentsociety) |
| **Project Sid / PIANO**(Altera 2024) | 500〜1,000体+ | **GPT-4o**(旧LMでは不可と明言) | 500体×2.5h の文化伝播ラン | 10 並行モジュール/体、social goal 5〜10秒毎再生成。トークン非開示 | [arXiv:2411.00114](https://arxiv.org/abs/2411.00114) |
| **OASIS**(camel-ai 2024) | **最大 100万体**(SNS) | Llama-3-8B・**vLLM** | **1M×1step = 18h / A100×27**、**100k×1step = 3h / A100×5** | **Time Engine(24次元・時間帯別の活動ベクトルで確率的に活性化=LOD 的機構)** + async 分散 + scale-free ネット生成 | [arXiv:2411.11581](https://arxiv.org/abs/2411.11581) / [github](https://github.com/camel-ai/oasis) |
| **AgentScope**(modelscope 2024) | **最大 100万体** | Llama3-8B・**vLLM 多モデル fleet**(8×8B/2×70B/1×176B per device) | **1M = 12分/4台**(basic prompt)、detailed prompt で **85分**、10k = 5.6分/4台。**線形スケール** | **actor 分散 + 依存グラフで自動並列**(依存の無い agent を並列実行)、多層 environment、agent あたり 2 LLM 呼/round(応答+形式抽出) | [arXiv:2407.17789](https://arxiv.org/abs/2407.17789) / [github](https://github.com/modelscope/agentscope) |
| **AgentTorch / "limits of agency"**(MIT Media Lab, AAMAS 2025) | **840万体**(NYC) | LLM archetype(群近似) | **100 archetype × 2 action ≒ 200 呼/step vs 個体別 840万呼 = 約 42,000倍削減**。ABM フレーム比 40,000倍高速 | **LLM-archetype**: 同一行動特性の個体群を1つの archetype に束ね、**archetype 単位で1呼**。個体別に撃たない | [arXiv:2409.10568](https://arxiv.org/abs/2409.10568) / [MIT Media Lab](https://www.media.mit.edu/posts/new-paper-on-limits-of-agency-at-aamas-2025/) |

**読み取れる相場観(我々への含意)**:

1. **100万体級は全て「小モデル1呼/step + 確率的活性化(LOD) + 分散配線(Ray/actor/async) + vLLM」の産物**。我々の LOD(発火制御)と sticky-fleet(vLLM 分散)は**この相場の中核を既に踏襲している**(OASIS の Time Engine ≈ 我々の drive+lod、AgentScope の fleet ≈ 我々の fleet.py)。
2. **AgentTorch の archetype は「削減の王者(42,000倍)」だが、個体を群に潰す**。彼らのタスク(感染率・失業率のマクロ予測)では archetype が個体別 LLM を**上回った**が、これは「マクロ量なら群近似で十分」を示すだけで、**我々が測る"個体レベルの稀な世界改変者(k\*)"には使えない**(§4 で詳述)。
3. **我々は A5000×7(A100 より弱)+ リッチ認知 + k×seed 掃引**なので、OASIS/AgentScope の100万体は非現実。**現実的な射程は ~1k〜10k、LOD 必須**(OASIS メモ [`docs/lit/mas__yang2024_oasis.md`] の結論と一致)。

---

## 3. 技法カタログ(課題2〜6)

> 各表の列: **技法 | 期待削減 | 忠実度リスク | 決定論・R1 との相性 | 実装コスト | 出典**。削減率は出典の文脈依存で、我々の decode 支配ワークロードでは目減りし得る(§1-A)。

### 3.1 呼び出し削減系(課題2)

| 技法 | 期待削減 | 忠実度リスク | 決定論・R1 との相性 | 実装コスト | 出典 |
|---|---|---|---|---|---|
| **attention-based LOD / 発火予算**(我々の実装) | **~12倍**(実測 発火 4.1〜11.4%) | 低〜中: 撃たない個体は routine 行動。発火個体の選び方が創発の材料を左右 | **◎ 既に R1 準拠**(予算は k 非依存・drive 由来)。決定論も担保済み | **導入済**(lod.py + drive) | 依頼実測 / [OASIS Time Engine](https://arxiv.org/abs/2411.11581) が同型 |
| **event-driven activation(ポーリング廃止)** | 中: 「何も起きない個体」を撃たない。OASIS は時間帯活動ベクトルで確率活性化 | 中: 活性化条件が粗いと反応の取りこぼし | ○: 我々の drive(欲求駆動発火)が既にこれ。**発火条件を k 非依存に保てば R1 維持** | **概ね導入済**(drive.py が surprise ポーリングを置換, 2026-07-04) | [OASIS](https://arxiv.org/abs/2411.11581) / lod.py 冒頭コメント |
| **階層化(前景=フル LLM / 背景=統計・小モデル)** | 大: 背景個体を統計/ルールで回す。前景だけ LLM。archetype の一般形 | **高(我々にとって致命的になりうる)**: 背景に落とした個体は"世界改変者"になれない=Y_external の分散を消す。**前景/背景の割当が k と交絡すると R1 破綻** | △: 前景個体の LLM 呼のみ決定論・キャッシュ。背景の割当ルールを k 非依存かつ決定論にする設計が必要 | **中〜大**(前景/背景の seam・忠実度検証) | [AgentTorch archetype](https://arxiv.org/abs/2409.10568) / hybrid ABM [arXiv:2412.06681](https://arxiv.org/pdf/2412.06681) |
| **archetype / 群近似(個体を束ねて archetype 単位で1呼)** | **最大(42,000倍)**。マクロ量では個体別を上回る場合あり | **極高**: 個体異質性を消す。**稀な逸脱者(世界改変者)は定義上出せない**。k\* の観測対象そのものを破壊 | ✕(我々の目的と非適合): 呼数が archetype 数で決まり個体の k と切り離される。マクロ研究には○だが個体創発研究には✕ | 大(モデル構造の作り替え) | [AgentTorch/limits of agency](https://arxiv.org/abs/2409.10568) |
| **routine caching(「昨日と同じ日」の plan/行動再利用)** | 中〜大: AgenticCache は**トークン -50% / レイテンシ -65%**(plan locality を利用) | 中: 再利用しすぎると新規性・多様性が痩せる(創発の材料が減る) | **△ 要注意**: **呼を skip する=呼数が変わる**。再利用率が k と相関すると R1 破綻。再利用の判定を**決定論かつ k 非依存**に設計する必要 | 中(状況ハッシュ+再利用ゲート、背景検証) | [AgenticCache arXiv:2604.24039](https://arxiv.org/abs/2604.24039) / [Agentic Plan Caching arXiv:2506.14852](https://arxiv.org/abs/2506.14852) |
| **importance sampling(重要イベントに呼を集中)** | 中: 低 importance 観測を撃たない(Park の importance ゲートが原型) | 中: importance 採点自体に LLM を使うと元も子もない(Park は 1〜10 採点を LLM で実施) | ○: 発火の選択であって k 非依存に保てる。ただし採点コストと相殺しないか要確認 | 小〜中(採点は heuristic 化推奨) | [Park 2023](https://arxiv.org/abs/2304.03442) |

**我々への適用可否(呼数削減)**: LOD と event-driven は**既に導入済みで R1 準拠**=これ以上の"新規削減"の主戦場ではない。**残る呼数削減の候補は routine caching と階層化**だが、いずれも**「削減率が k と相関しない」保証**と**「創発の材料を消さない」検証**が前提。archetype は**マクロ研究用であって k\* 研究には不可**。

### 3.2 プロンプト削減系(課題3)

> 大前提: **我々は decode 支配で入力が律速でない(§1-A)**ため、この系統は「トークンコストの主因」を叩かない。効果は限定的。

| 技法 | 期待削減 | 忠実度リスク | 決定論・R1 との相性 | 実装コスト | 出典 |
|---|---|---|---|---|---|
| **プロンプト圧縮(LLMLingua 系)** | 入力 **2〜20倍**(9倍で品質 -2% 未満、20倍で 2400→115 tok が full-shot と同等) | 中: 高圧縮で多様性の手がかり(口語の細部・状況ニュアンス)が落ちうる。**創作/ペルソナ生成では劣化が"標準ベンチに出ない形"で来る**(§3.3 の量子化と同型の警告) | **△**: 圧縮器(小 LM)の**追加呼が発生**=決定論には圧縮器も固定+キャッシュ要。圧縮は入力側のみ=呼数は不変(R1 中立)だが総計算は必ずしも減らない | 中(圧縮器の常駐・決定論化)。**我々のプロンプトは既に ~1,000 tok と短く、few-shot も無い**ので利得が小さい | [LLMLingua(公式)](https://llmlingua.com/llmlingua.html) / [arXiv:2310.05736](https://arxiv.org/abs/2310.05736) / [LongLLMLingua arXiv:2310.06839](https://arxiv.org/abs/2310.06839) |
| **観察の top-k 選別(salience filtering)** | 中: 想起する記憶/観察を上位 k に絞る。Park は recency+importance+relevance の和で top-k を「文脈窓に収まる分だけ」注入 | 中: 削りすぎると"創発の火種"(意外な観測・弱い情報)が消える。**AGA は「believability は行動の有限性で決まる=プロンプト長ではない」**とし、削っても Likert 不変を実証 | ○: 選別ルールが決定論なら決定論維持。呼数不変(R1 中立)。**内容の選別は k に影響しうる**ので選別基準は固定 | **概ね導入済**(episodes 120・日記7日・想起) | [Park 2023](https://arxiv.org/abs/2304.03442) / [AGA arXiv:2402.02053](https://arxiv.org/html/2402.02053v2)(token-budgets §1) |
| **記憶の要約階層化(summarize-and-forget)** | 中: 生ログを要約に畳んで注入トークンを圧縮(Lyfe Agents の Summarize-and-Forget) | 中: 要約で細部が失われる(memory-100day-audit の「7日超は蒸留物のみ」と同じ性質) | ○: 要約が決定論なら維持。要約に LLM を使うなら**その呼が R1 対象**(内省=既に日1回で計上済み) | **概ね導入済**(consolidate・day_summaries) | [Lyfe Agents arXiv:2310.02172](https://arxiv.org/abs/2310.02172)(token-budgets §1) |
| **few-shot 例の削除 / 構造化出力の最小化** | 小〜中: 例示を削り JSON 雛形を最小化 | 低: **AGA が「トークン 30〜43% まで削っても believability 維持」を定量に示す**=削減の限界効用は早く飽和 | ◎: 決定論・R1 に中立(内容不変なら) | 小(プロンプト整形) | [AGA arXiv:2402.02053](https://arxiv.org/html/2402.02053v2) |

**我々への適用可否(プロンプト削減)**: **優先度は低い**。理由は (i) 入力が律速でない、(ii) 我々のプロンプトは既に短く few-shot も無い、(iii) LLMLingua は圧縮器の追加呼で短プロンプトでは相殺しうる。**唯一やる価値があるのは「構造化出力の最小化」と「top-k 選別/要約(既に実装済み)の維持」**。AGA の教え=「トークンを削っても believability は落ちない」を**入力側の削り込みの安心材料**として使うが、積極的な圧縮投資はしない。

### 3.3 推論高速化系(課題4)★我々の主戦場

> 「何を計算するか」を変えず「同じ意味の計算を安く回す」=**忠実度・決定論・R1 に中立な"タダ飯"**。ここを最大化するのが我々の最善手。

| 技法 | 期待削減(高速化) | 忠実度リスク | 決定論・R1 との相性 | 実装コスト | 出典 |
|---|---|---|---|---|---|
| **prefix / KV cache(APC)+ agent-id sticky routing** | prefix cache ヒット率を**単一機の天井 ~96%** まで回復(sticky で同一ペルソナ+履歴を同一 GPU に固定) | **なし**: APC は同一プレフィックスの KV 再利用のみで**出力分布を一切変えない(意味論的に中立)** | **◎ 完全中立**: 決定論・R1 いずれも無傷。プロンプトは「共通部を先頭・個別部を後ろ」に構成済み | **導入済**(fleet.py sticky + deliberate.py の APC 順序) | [vLLM APC](https://docs.vllm.ai/en/stable/features/automatic_prefix_caching.html) / [infra__storage-routing.md] / [infra__gemini-summary-verification.md] |
| **continuous batching(連続バッチ)** | 静的バッチ比 **最大23倍**(+PagedAttention・+prefix cache で 23〜28倍。OPT-13B/A100 実測) | なし | **◎ 中立**(ただし temp>0 の**初回**はバッチ構成でサンプリングが揺れる→再現性は応答キャッシュ再生で担保、既定運用どおり) | **導入済**(vLLM 標準) | [Anyscale 23x](https://www.anyscale.com/blog/continuous-batching-llm-inference) |
| **speculative decoding(投機的デコード)** | vLLM で **最大2.8倍**(要約系 prompt-lookup)、Llama-70B+1B draft で 2.31倍、ShareGPT 1.5倍。**低 QPS で効きが大きい** | **なし(無損失)**: 検証段で目標モデルと**同一分布**を保証(採択/棄却で分布不変) | **◎ 中立**: 出力は目標モデルと同分布=キャッシュ・決定論・R1 に無傷 | **中(未導入)**: vLLM 起動フラグ+draft モデル選定・本選機で bench | [vLLM spec-decode 2.8x](https://blog.vllm.ai/2024/10/17/spec-decode.html) |
| **quantization(INT4 AWQ)** | メモリ ~1/4(27B→~14GB=24GB に7並列)+ 帯域律速の decode を高速化 | **中(我々の用途で要注意)**: ベンチ精度は 97〜99% 維持(平均 -1.6pt、<4%)だが、**"ニュアンス判断"が言語能力より先に劣化**=創作/ペルソナ/多様性に効く。「量子化が alignment を崩す/新たなバイアスが 2.2〜5.6% 出現」の報告。**標準ベンチは劣化を隠す** | ○: モデルが変わる=`backend.name` が変わり別キャッシュ。各モデル内では決定論・R1 中立 | **中**: AWQ 版の入手 or 自前量子化。A5000=Ampere で FP8 非加速のため**INT4 が実務解** | [AWQ 97-99% 🔶](https://localllm.in/blog/quantization-explained) / [comprehensive eval arXiv:2402.16775](https://arxiv.org/html/2402.16775v1) / [bias emergence arXiv:2605.15208](https://arxiv.org/pdf/2605.15208) / llm-model-selection §3.0 |
| **複数エージェントのバッチ推論(同一 step の独立発火をまとめる)** | 中〜大: 同一 step 内の独立呼を1バッチに(連続バッチが GPU 側で自動的に実現) | なし | ◎ 中立(順序非依存に集約すれば決定論も維持) | 小(既に vLLM が動的バッチ)。**明示的な step 内一括発行の seam を足すと更に効く** | [continuous batching](https://www.anyscale.com/blog/continuous-batching-llm-inference) / AgentScope の依存グラフ自動並列 [arXiv:2407.17789](https://arxiv.org/abs/2407.17789) |
| **出力上限の右サイズ化(reflect を締める)** | 中〜大: **decode 支配なので reflect(思考+長出力)の cap が最大レバー**。4b は思考が冗長で 1200〜2048 を食い切る | 低: token-budgets は「reflect 最終JSONは 140〜250tok。思考予算の飢餓で空応答 11〜18%」→ **右サイズ化は品質を上げつつ throughput も上げる** | ◎: cap は出力長のみ変え**呼数を変えない=R1 無傷**。cap はキャッシュキーに入る(別水準=別キャッシュ) | 小(config)。※実装前にユーザー合意(token-budgets §3.2) | token-budgets §3.3 / cache.py L29-35 |

**我々への適用可否(推論高速化)**: **ここが最優先の投資先**。prefix cache/sticky・連続バッチは**導入済み**。**未導入で低リスク高効果の筆頭は speculative decoding(無損失・最大2.8倍)**。量子化は**必須(VRAM 制約)だが忠実度リスクを持つ唯一の高速化技法**なので、**創作/ペルソナ/多様性のブラインド評価で INT4 vs 非量子化を検証**してから確定(llm-model-selection §4 の論点5・8と接続)。出力上限の右サイズ化は token-budgets の推奨どおり。

### 3.4 蒸留・ハイブリッド系(課題5)

| 技法 | 期待削減 | 忠実度リスク | 決定論・R1 との相性 | 実装コスト | 出典 |
|---|---|---|---|---|---|
| **LLM 決定ログ→軽量モデル/決定木へ蒸留(日常行動を代替)** | 大: 0.5B/1.5B/3B が次tier の大モデルに匹敵する蒸留報告。routine を"学習された routine"に置換 | **高**: 蒸留先は教師の分布を模倣=**教師が出さない稀な逸脱(世界改変)を再現しにくい**。ロングテール(=我々の観測対象)が最も削れる部分 | △: 軽量モデルを決定論化(temp=0・固定重み)すれば再現可。**LLM に回す割合が変わる=呼数が動く→R1 に触れる** | **大**: 教師ログ収集→蒸留→忠実度検証(分布一致)。本選日程に重い | [Structured Agent Distillation arXiv:2505.13820](https://arxiv.org/abs/2505.13820) / [Agent Distillation arXiv:2505.17612](https://arxiv.org/abs/2505.17612) |
| **novelty detection ルーティング(新規状況のみ LLM・既知は軽量へ)** | 中〜大: 既知状況を軽量モデル/キャッシュで処理し LLM 呼を削減(AgenticCache の plan locality が実証: -50% token) | 中〜高: 「新規/既知」の閾値が創発の火種を既知側に誤分類すると逸脱を潰す | **△ 要注意**: **LLM に回す割合(novelty 率)が k と相関すると R1 破綻**。novelty 判定を決定論かつ k 非依存に | 中〜大(novelty 指標+ルーティング+検証) | [AgenticCache arXiv:2604.24039](https://arxiv.org/abs/2604.24039) |
| **前景=LLM / 背景=ルール のハイブリッド ABM** | 大(§3.1 の階層化と同じ): 背景をルール/統計で回す | 高(同上): 背景個体は世界改変者になれない | △(同上): 前景/背景割当を k 非依存・決定論に | 中〜大 | hybrid ABM [arXiv:2412.06681](https://arxiv.org/pdf/2412.06681) / [AgentTorch archetype](https://arxiv.org/abs/2409.10568) |

**我々への適用可否(蒸留・ハイブリッド)**: **研究目的と最も緊張する系統**。我々は既に **routine.py(ルールベース fallback)という"背景"を持つ**。蒸留はこの背景を賢くするが、**「LLM に回す割合の変動」が R1(呼数の k 非依存)を脅かし、蒸留のロングテール欠落が k\*(稀な世界改変者)を潰す**という二重の危険がある。**採用するなら本番の主経路ではなく、"スケールを稼ぐための背景個体"に限定し、前景(フル LLM)個体の分布と背景の分布が一致することを検証**してから。忠実度検証方法=前景 vs 背景で Y_external 成分・行動レパートリー曲線・distinct-n の分布一致検定(token-budgets §4 の枠組みを流用)。

### 3.5 観察情報の最適化(課題6)

| 技法 | 期待削減 | 忠実度リスク | 決定論・R1 との相性 | 実装コスト | 出典 |
|---|---|---|---|---|---|
| **salience filtering(見せる観察を選別)** | 入力トークン中: 上位のみ注入(recency×importance×relevance) | **中〜高(創発の材料を削るリスク)**: 情報を削ると、意外な観測・弱い信号・多様性の手がかりが消え、**創発(語彙生成・世界改変の火種)が痩せうる**。ただし AGA は「believability はプロンプト長でなく行動の有限性で決まる」=**過度な観察は無益**とも示す | ○: 選別ルールが決定論なら維持。呼数不変(R1 中立)。**選別内容が k に影響する**ので基準は固定 | **概ね導入済**(想起・想起件数) | [Park top-k 想起](https://arxiv.org/abs/2304.03442) / [AGA](https://arxiv.org/html/2402.02053v2) |
| **情報を削ると何が壊れるか(先行議論の現状)** | — | **文献は"測定"より"議論"が先行**: 「観察を削ると創発が壊れる」の定量的閾値を直接測った LLM-ABM 研究は**見当たらず(要検証)**。関連して、OASIS はエージェントが人間より herd/分極が過剰=情報環境が創発を過剰駆動する例、AGA は削っても believability 不変=下限側の安全域を示す | — | — | [OASIS](https://arxiv.org/abs/2411.11581)(過剰 herd)/ [AGA](https://arxiv.org/html/2402.02053v2)(下限の安全域) |

**我々への適用可否(観察最適化)**: 我々の入力は律速でない(§1-A)ので**トークン節約目的での観察削減は不要**。むしろ**「創発の材料を消さない」ことが重要**=**削るより"的確に選ぶ"**(token-budgets §3.4 の「品質はトークン量でなく想起の的確さ・多様性ヒントに投資」と一致)。**salience の選別基準を変えることは k\* に影響しうる実験因子**なので、既定は固定し、変えるなら token-budgets §4 型の掃引で影響を測る。

---

## 4. 我々のアーキテクチャへの適用優先順位(提案・実装しない)

**評価軸**: 削減効果 × 忠実度リスク × 決定論/R1 適合 × 実装コスト。前提=**decode 支配・入力は律速でない・k\* は個体レベルの創発を測る・R1 は呼数の k 非依存**。

### Tier 1 — 迷わずやる(高効果・低リスク・決定論/R1 中立・多くは残作業=実機疎通のみ)

1. **speculative decoding の導入(未実装・最有力)** — 無損失で最大2.8倍。出力は目標モデルと同分布=**忠実度・決定論・R1 いずれも無傷**。残作業は vLLM 起動フラグ + draft モデル選定 + 本選機 `bench.py`。**新規で唯一の"タダ飯の未回収分"**。
2. **prefix cache + sticky routing の実機確認(実装済み・要疎通)** — ヒット率 ~96% の実測を本選機で検証(bench)。既に fleet.py + APC 順序で配線済み。効果最大・リスクゼロ。
3. **連続バッチ + 出力上限右サイズ化(実装済み/config)** — reflect の cap を token-budgets §3.2 推奨(4b: 1500〜2048、大型: 1000〜1500)へ。**decode 支配の主レバー**。呼数不変=R1 無傷。※実装前にユーザー合意。
4. **step 内独立発火の明示的バッチ発行(小改修)** — 連続バッチが GPU 側で吸収するが、同一 step の独立呼をまとめて投げる seam があると 7GPU の充填率が上がる。順序非依存に集約すれば決定論維持。

> Tier 1 は総じて**「何を計算するか」を変えない**ため、k\* データの意味を一切汚さずにエージェント数×時間の余地を広げる。**ここを最大化してから他を検討**が原則。

### Tier 2 — 条件付きでやる(効果大だが忠実度検証が前提)

5. **quantization(INT4 AWQ)の忠実度確定** — VRAM 制約で**事実上必須**だが、忠実度リスクを持つ唯一の高速化。**創作/ペルソナ/多様性のブラインド評価(distinct-2・自己反復率・LLM-judge believability をオフライン限定)で INT4 vs 非量子化を A/B**し、劣化が許容内と確認してから本番固定(llm-model-selection §4 論点5・8)。
6. **routine caching(「昨日と同じ日」再利用)の限定導入** — AgenticCache 型で -50% token の実績。ただし **(a) 再利用ゲートを決定論かつ k 非依存に、(b) 再利用率が創発を痩せさせないか(distinct-n・行動レパートリー曲線)を検証**。R1 を壊さない設計が確認できれば呼数削減の本命。

### Tier 3 — 研究目的と衝突。やるなら"背景個体"限定+分布一致検証

7. **階層化(前景=フル LLM 少数 / 背景=蒸留・小モデル・ルール 多数)** — スケールを桁で稼ぐ唯一路だが、**背景に落とした個体は世界改変者になれない=Y_external の分散を消す**。採用するなら「**前景個体でのみ k\* を測り、背景はマクロ環境の充填に使う**」と役割を分離し、前景/背景の割当を k 非依存・決定論に固定。**前景 vs 背景の分布一致検定**が採用条件。
8. **蒸留(決定ログ→軽量モデル)/ novelty ルーティング** — 最大級の呼数削減だが、**ロングテール(稀な逸脱=我々の観測対象)が最も削れる部分**で、**LLM 呼割合の変動が R1 に触れる**。本選日程では実装+検証が重い。**将来の"スケール後段レバー"**として設計 seam のみ意識(scale-audit B9 の平準化 seam と接続)。

### 明確に非推奨(我々の研究目的では採らない)

- **archetype / 群近似(AgentTorch 型 42,000倍)** — マクロ量の予測には最強だが、**個体異質性と稀な世界改変者を定義上消す**ため k\* 研究に不可。**マクロ検証用の別トラック**としてなら価値があるが、本線には乗せない。
- **積極的なプロンプト圧縮(LLMLingua 等)** — 我々は入力が律速でなく(§1-A)、プロンプトは既に短く few-shot も無い。圧縮器の追加呼で相殺しうる。**「構造化出力の最小化」だけで足り、圧縮フレームワークは過剰投資**。
- **応答キャッシュのヒット率向上を狙う** — ヒット率を上げる=プロンプトを反復させる=現実性を捨てる。キャッシュは**再現性の実体であって初回計算の節約ではない**(§1-B)。初回コストは Tier 1(推論高速化)で叩く。

### 一枚の指針

> **「入力(情報量)を削る」誘惑に乗らず、「同じ意味の計算を安く回す」推論高速化(Tier 1)を上限まで回収する。** 呼数削減(Tier 2-3)は "創発の材料を消さない範囲" かつ "削減率が k と相関しない設計" に限る。これが AGA(believability = 行動の有限性)と R1(呼数の k 非依存)を両立させ、**k\* データの意味を保ったままエージェント数と時間を伸ばす**唯一の筋。

---

## 5. 出典リンク

**LLM-ABM スケール(一次)**
- [Generative Agents(Park+ 2023)— arXiv:2304.03442](https://arxiv.org/abs/2304.03442)
- [AgentSociety(清華/復旦 2025)— arXiv:2502.08691](https://arxiv.org/abs/2502.08691) / [github(tsinghua-fib-lab)](https://github.com/tsinghua-fib-lab/agentsociety)
- [Project Sid / PIANO(Altera 2024)— arXiv:2411.00114](https://arxiv.org/abs/2411.00114)
- [OASIS(camel-ai 2024, 100万体)— arXiv:2411.11581](https://arxiv.org/abs/2411.11581) / [github](https://github.com/camel-ai/oasis)
- [AgentScope(modelscope 2024, 100万体)— arXiv:2407.17789](https://arxiv.org/abs/2407.17789) / [github](https://github.com/modelscope/agentscope)
- [AgentTorch / On the limits of agency(MIT Media Lab, AAMAS 2025)— arXiv:2409.10568](https://arxiv.org/abs/2409.10568) / [MIT Media Lab 解説](https://www.media.mit.edu/posts/new-paper-on-limits-of-agency-at-aamas-2025/) / [github(AgentTorch)](https://github.com/AgentTorch/AgentTorch)

**呼数削減 / caching(一次)**
- [AgenticCache(plan locality, -50% token / -65% latency)— arXiv:2604.24039](https://arxiv.org/abs/2604.24039)
- [Agentic Plan Caching — arXiv:2506.14852](https://arxiv.org/abs/2506.14852)

**プロンプト削減(一次)**
- [LLMLingua(公式ページ)](https://llmlingua.com/llmlingua.html) / [arXiv:2310.05736](https://arxiv.org/abs/2310.05736)
- [LongLLMLingua — arXiv:2310.06839](https://arxiv.org/abs/2310.06839)
- [Affordable Generative Agents(AGA)— arXiv:2402.02053](https://arxiv.org/html/2402.02053v2)(token-budgets.md で既収)
- [Lyfe Agents(Summarize-and-Forget)— arXiv:2310.02172](https://arxiv.org/abs/2310.02172)

**推論高速化(一次)**
- [vLLM Automatic Prefix Caching(公式)](https://docs.vllm.ai/en/stable/features/automatic_prefix_caching.html)
- [Continuous batching 23x(Anyscale)](https://www.anyscale.com/blog/continuous-batching-llm-inference)
- [Speculative decoding 2.8x(vLLM 公式ブログ)](https://blog.vllm.ai/2024/10/17/spec-decode.html)
- [A comprehensive evaluation of quantization strategies — arXiv:2402.16775](https://arxiv.org/html/2402.16775v1)
- [Quantization undoes alignment / bias emergence — arXiv:2605.15208](https://arxiv.org/pdf/2605.15208)
- 🔶 二次(相対比較のみ・絶対値の根拠にしない): [LLM quantization guide(AWQ 97-99%)](https://localllm.in/blog/quantization-explained) / [Understanding LLM Quantization For AI Roleplay](https://rpwithai.com/understanding-llm-quantization-for-ai-roleplay/)

**蒸留・ハイブリッド(一次)**
- [Structured Agent Distillation — arXiv:2505.13820](https://arxiv.org/abs/2505.13820)
- [Distilling LLM Agent into Small Models — arXiv:2505.17612](https://arxiv.org/abs/2505.17612)
- [LLM-Agent-Based Modeling of Transportation(hybrid ルール+LLM)— arXiv:2412.06681](https://arxiv.org/pdf/2412.06681)

**リポジトリ内(既存・根拠の中心)**
- [`docs/research/token-budgets.md`](token-budgets.md)(AGA=トークン削減でも believability 維持・出力上限の右サイズ化・decode 支配)
- [`docs/research/scale-audit-100days.md`](scale-audit-100days.md)(呼数 6.3M〜10.3M・トークン ~6.8B・律速)
- [`docs/research/llm-model-selection.md`](llm-model-selection.md)(A5000=Ampere・FP8 非加速・INT4・sticky/prefix)
- [`docs/lit/mas__yang2024_oasis.md`](../lit/mas__yang2024_oasis.md) / [`docs/lit/mas__agentscope2024_largescale.md`](../lit/mas__agentscope2024_largescale.md)(スケール様式)
- [`docs/lit/infra__storage-routing.md`](../lit/infra__storage-routing.md)(sticky routing で prefix cache ~96%)/ [`docs/lit/infra__gemini-summary-verification.md`](../lit/infra__gemini-summary-verification.md)(APC は意味論的に中立・N 上限)
- 実装: `src/society/cognition/lod.py`(発火予算)/ `src/society/llm/cache.py`(応答キャッシュ=再現性の実体)/ `src/society/llm/{vllm,fleet}.py`(APC + sticky routing)/ `src/society/cognition/{drive,routine,deliberate}.py`

> 注記(正直な記録): (i)AgentSociety の「real-time より速い」実数は本文抜粋で未確認=**要検証**。(ii)「観察を削ると創発が壊れる」定量閾値を直接測った LLM-ABM 研究は**見当たらず**(AGA の下限安全域と OASIS の過剰 herd から挟むのみ)。(iii)量子化の忠実度は**標準ベンチが劣化を隠す**ため、我々の用途(創作/ペルソナ/多様性)では自前ブラインド評価が必須。(iv)speculative decoding・spec 系の高速化倍率はワークロード依存で、本選機 `bench.py` 実測で確定すること(未測定値は書かない=ops 方針)。
</content>
</invoke>
