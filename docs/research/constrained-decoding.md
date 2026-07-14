# 制約付きデコード(構造化出力)の文献・API調査 — モデル交換時の行動JSON保険

- 種別: リサーチ(調査のみ)。**src非編集・実LLM実行なし・git commitなし**。成果物は本ファイル1点。
- 実施: 2026-07-14、Opus 4.8 サブエージェント。
- 位置づけ: `docs/plans/engine-architecture.md §3 計画A`(承認済み)の**実装前調査**。断定は避け、一次ソース優先・未確認は「未確認」と明記する。
- 出典方針: 公式ドキュメント/公式リリース/arXiv/GitHub Issue(挙動の一次証拠)を優先。個人ブログは検証用として引くが絶対値の根拠にはしない。アクセス日は §6 に付す(全て 2026-07-14)。
- **調査前の確認事項(リポジトリ実物)**: `src/society/llm/ollama.py` は**全呼び出しに `format:"json"` を無条件付与している**(L27-34)。`cache.py::_key` は format を**キーに含めていない**(L29-35)。`vllm.py` は `response_format={"type":"json_object"}` を優先し 400 で外す(L53-54, L97-98)。`deliberate.py::parse_action` は 13 行動を寛容正規化し、`propose` は入れ子 `rule` dict(自由形)を通す(L361-369)。この3点が本調査の接合点(§4)。

---

## 0. 結論(5行)

1. **ollama の `format` は既に本シミュで常時 ON**(json モード)。承認済み「計画A」の本質は *新規導入* ではなく、①`none|json|schema` を選べる**ノブ化**、②将来の vLLM `guided_json` を同じノブから配線、の2点。
2. **format と think は事実上排他**。`format:"json"` の GBNF 文法は `<think>` タグを禁止するため思考が抑制され(Zenn/7shi 解析)、`format:{schema}`+think は qwen3 で JSON が破損する報告あり(GitHub #10929)。本シミュの **reflect は think=True + format=json で回っており**(config `reflect_think:true` × ollama.py 無条件 json)、ここが最大の危険領域(§4.2)。
3. 文献は割れている: 「format 制約は推論を下げる」(Let Me Speak Freely, EMNLP2024)に対し、**プロンプトを揃えれば構造化が非構造化に勝つ**という強い反論(dottxt)。落とし所は**「構造(封筒)は強制・中身(text)は自由」** — 本シミュの行動JSONは既にこの形(§2.3)。
4. **キャッシュキーへの format 追加は必須**。format を可変にすると、現行キー(model/temp/max_tokens/think/prompt)では none↔json↔schema 切替時に旧応答を誤再生する。`think` と同じ扱いで `_key` に足す(§4.1・§5.3)。
5. **スキーマ全行動 union は非現実的**(可変キー `propose.rule` が難所)。まず `"json"` モード(構文のみ強制)が安全。schema モードは reflect を除外し、単一行動へ限定した将来拡張とする(§5.2)。

---

## 1. ollama の構造化出力 `format` 仕様

### 1.1 二つのモード

`format` パラメータは2形態を取る(公式 API ドキュメント・構造化出力ガイドで確認):

| モード | 指定 | 強制の粒度 | 導入 |
|---|---|---|---|
| **json モード** | `"format": "json"` | 汎用 JSON 文法(構文が JSON であることのみ強制。キー・型は自由) | 旧来から |
| **schema モード** | `"format": { JSON Schema オブジェクト }` | 指定スキーマ専用の文法を生成し、キー名・型・required まで強制 | **v0.5.0(2024-12-06)** |

- schema モードは v0.5.0 の目玉機能。「汎用 JSON 文法の代わりに、渡した JSON Schema からその場で文法を生成して強制する」(公式ブログ/DEV まとめ)。**本シミュの `ollama.py` が使う `"json"` は前者(構文のみ)**で、キー厳守は文法でなく**プロンプト規約+parse_action の寛容正規化**が担っている(だから別名キー `content`/`message` を吸収できる)。
- 出典: [Ollama Structured Outputs(公式docs)](https://docs.ollama.com/capabilities/structured-outputs)、[ollama/docs/api.md](https://github.com/ollama/ollama/blob/main/docs/api.md)、[Structured outputs(公式ブログ 2024-12-06)](https://ollama.com/blog/structured-outputs)。

### 1.2 /api/generate と /api/chat の違い

- **両エンドポイントとも `format:"json"` と `format:{schema}` を受ける**(api.md に `/api/generate` の cURL 例が両方あり)。本シミュは `/api/generate`(`ollama.py` L36)を使用=schema 化は同エンドポイントのまま `format` を差し替えるだけで届く(**追加の配線不要**)。
- 公式の作法差: chat 側の例が docs では中心。実装差ではなく例示差。
- 注意(公式 tips): **json モードはプロンプトで「JSONで返せ」と明示しないと大量の空白を吐きうる**。本シミュのヘッダは既に「出力は次のいずれかの JSON 1個のみ」(`deliberate.py::_HEADER_HEAD`)で満たしている。

### 1.3 think との併用可否 ★本調査の核心

**公式ドキュメントは format×think の併用について沈黙**(構造化出力docs・thinking docs いずれも言及なし=未文書化)。一次証拠は挙動報告に依る:

- **json モード × think(qwen3): 思考が消える**。json モードは GBNF 文法で「文法違反トークンの logit を −∞」にして JSON を保証するが、この文法は `<think>` を許さないため**モデルは思考タグを生成できず、`thinking` フィールドが出ずに直接 JSON が始まる**(Zenn/7shi の GBNF 解析・qwen3:4b で実測)。出典: [Ollama の JSON モードと thinking の相互作用(7shi)](https://zenn.dev/7shi/articles/fa36989a04c9ed?locale=en)。
- **schema モード × think(qwen3): JSON が破損**。`think:true` + schema 指定で応答が `{"{` と二重の開き括弧で始まり**パース不能**になる報告(qwen3:0.6b で再現、`think:false` なら正常)。**Open**、担当 @drifkin。出典: [ollama#10929](https://github.com/ollama/ollama/issues/10929)。
- 関連: **thinking + tools + qwen3 で空応答**(別経路だが「think 併用時の空/破損」傾向を補強)。出典: [ollama#10976](https://github.com/ollama/ollama/issues/10976)。

> **含意**: think が要る呼(=内省 reflect)には schema/json を**強制してはならない**。逆に、think を使わない呼(=deliberate/post/dm/plan、config 上 `reflect_think` 以外は think=False)は json モードと両立する。本シミュは既に deliberate=think False・reflect=think True と分かれており、ノブは**この purpose 境界に沿って format を出し分ける**べき(§5.1)。

### 1.4 num_predict(=max_tokens)との相互作用

- 公式は num_predict×format の相互作用を明示していない(**未確認**)。機構から言えること:
  - **文法は「どのトークンを許すか」を制約するだけで「何トークンで終えるか」は保証しない**。num_predict はトークン総数の上限として独立に効く。schema が要求する構造が num_predict を超えると**途中で切れて不完全 JSON**になりうる(json モードでも同様)。本シミュは `_loads_lenient`(末尾 `}`/`"}` 補完)で末尾切れを救済済み=json モードとは整合。深いスキーマほど切れやすい=schema モードは truncation リスクが上がる。
  - **json モードで think が抑制される分、予算が JSON 本文へ回る**(§1.3)=同じ num_predict でも本文が長く取れる副次効果(reflect 予算問題 `docs/research/token-budgets.md §3.3` と逆向きに効きうるが、内省の思考自体が消えるトレードオフを伴う)。
  - json モードの**空白暴走**(§1.2)は num_predict を空白で食い潰し実質空応答を招く=`token-budgets.md §2.3` の「空/未パース 11〜18%」の一因の候補(未確認)。
- **温度**: schema 遵守は temperature=0 が推奨(公式 tips)。本シミュ既定は 0.7(発話多様性優先)。schema モードを使う場合、遵守率と多様性のトレードオフが顕在化する(§2)。

---

## 2. 構造化が品質を下げるか — 文献

### 2.1 「下げる」側: Let Me Speak Freely?(Appier, EMNLP2024 Industry)

- 3つの format 制約を比較: **①JSON-mode(制約付きデコード=最強制)/②FRI(形式指示のみ)/③NL-to-Format(自然文→後から整形=最緩)**。
- **推論タスクでは劣化**: GSM8K で GPT-3.5-Turbo が自然文 76.60% → JSON-mode **49.25%**。Last Letter で LLaMA3-8B が自然文 70.07% → JSON **28.00%**(−38.15pt)。
- **分類タスクでは向上**: DDXPlus で Gemini1.5Flash が自然文 41.59% → JSON-mode **60.36%**。
- 推奨: **内容生成と形式順守を分離せよ**。NL-to-Format は「ほぼ自然文と同等」の推論性能を保ったまま構造を得る。
- 出典: [arXiv:2408.02442](https://arxiv.org/html/2408.02442v1) / [ACL Anthology 2024.emnlp-industry.91](https://aclanthology.org/2024.emnlp-industry.91.pdf)。

### 2.2 「下げない/上げる」側: dottxt の反論(Say What You Mean)

- 方法論批判: 元論文は**構造化条件と非構造化条件で違うプロンプトを使い**、しかも構造化側に**スキーマを与えていない**(「どの形式で返すべきか」が本文にない)。さらに**「JSON-mode(未保証の形式示唆)」と真の制約付きデコード(FSM/正規表現で強制)を混同**し、非構造化側の採点に Claude-3-Haiku パーサを使って結果を水増し。
- 再実験(プロンプトを揃え、スキーマを明示): **構造化が非構造化に勝つ**。GSM8K/Last Letter/Shuffle Object で 非構造化 0.65–0.66 に対し 正規表現制約 **0.68–0.77**、JSON も非構造化 0.73 < 構造化 **0.77**。
- 出典: [Say What You Mean(dottxt blog)](https://blog.dottxt.ai/say-what-you-mean.html) / [outlines discussion #1117](https://github.com/dottxt-ai/outlines/discussions/1117)。

### 2.3 落とし所 —「構造は強制・中身は自由」

- 両者の対立は**「何を文法で縛るか」**で解ける。**推論を JSON の *値* の中で行わせる(思考ステップを短い enum やフィールドに押し込む)と劣化**。**封筒(キーの有無・型)だけ縛り、自由記述フィールド(`text`)は無制約**なら劣化はほぼ無い(dottxt の再現、JSONSchemaBench の整理とも整合)。
- **本シミュは既にこの形**: 行動JSONは `{"action":"speak","text":"…"}` の薄い封筒で、発話本文 `text` は**自由文字列**。推論(どう振る舞うか)は text の中で自由に展開され、文法で刻まれない。したがって **deliberate 系に json モードを掛けても、Let Me Speak Freely が言う「推論劣化」は原理的に小さい**(そこで縛るのはキー名だけ)。
- **危険なのは reflect**: 内省は「順に思い出す→なぜ印象に残ったか→結論」という**推論そのもの**が価値(k の作用点)。ここで think を殺して JSON 文法に押し込むのは、まさに文献が警告する「形式で推論を潰す」ケース。→ **reflect は非構造(または NL-to-Format 相当=思考は think で自由、最終 JSON だけ小さく)を維持すべき**。
- 小型モデルの構造化遵守の一般傾向(参考、既収と重複): Llama3.2-3B のパース率 47.8–56.5%、Gemma3-4B は 87%。文法制約は遵守率を底上げするがレイテンシ・タスク性能とトレードオフ。出典: [JSONSchemaBench arXiv:2501.10868](https://arxiv.org/html/2501.10868v1)。
- 日本語・多様性への影響: 「json モードで日本語の質・distinct が落ちるか」を**直接測った一次文献は見つからず(未確認)**。機構上は §2.3 の通り「text 無制約なら日本語生成は素の分布のまま」だが、schema で温度0を強いると多様性が落ちるのは確実。→ **実測(distinct-2)で確認すべき事項**(§5.4)。

---

## 3. vLLM の構造化出力(本選環境)

### 3.1 API と経路

- パラメータ: **`guided_json`(スキーマ)/ `guided_choice` / `guided_regex` / `guided_grammar` / `guided_whitespace_pattern`**。OpenAI 互換経路では `response_format={"type":"json_object"}`(現行 vllm.py が使用)や `{"type":"json_schema","json_schema":{…}}`、あるいは `extra_body={"guided_json": schema}` でリクエスト毎に指定。オフラインは `SamplingParams` 内の `GuidedDecodingParams`。
- バックエンド: **outlines / xgrammar / lm-format-enforcer / guidance(llguidance)**。既定は **auto**(リクエストに応じて自動選択)。`guided_decoding_backend` で固定でき、`"xgrammar:no-fallback"` のようにフォールバック抑止も可。
- 出典: [vLLM Structured Outputs(v0.8.2 docs)](https://docs.vllm.ai/en/v0.8.2/features/structured_outputs.html)、[Structured outputs in vLLM(Red Hat)](https://developers.redhat.com/articles/2025/06/03/structured-outputs-vllm-guiding-ai-responses)。

### 3.2 スループットへの影響(実測報告)

- **正確性は上がるが、vLLM ではバッチ増で throughput が落ちる**。SqueezeBits の比較: 複雑スキーマ(Github)で非制約の正答率 61.1% → 制約で +20〜25pt。反復スキーマ(Book-Info)で非制約 ≤72% → 制約で 100%。ただし **vLLM は batch≥8 で guided decoding のスループット低下が顕著**、SGLang は劣化が小さい。**xgrammar は文法再利用(=同一スキーマの繰返し)でキャッシュが効き TPOT が良い**;動的スキーマでは llguidance が優位・タイムアウト0で頑健。
- 本シミュへの含意: **同一スキーマを毎 step 大量に使う**(全 deliberate が同じ封筒)= **xgrammar のキャッシュが最も効く使い方**。艦隊(FleetLLM)の sticky routing で同一スキーマが同一 GPU に当たれば文法コンパイルも1回で済む。**具体的なトークン/秒は本選実機で `scripts/bench.py` 実測**(ops 方針=未測定値は書かない)。
- 出典: [Guided Decoding Performance: vLLM & SGLang(SqueezeBits)](https://blog.squeezebits.com/guided-decoding-performance-vllm-sglang)、[XGrammar arXiv:2411.15100](https://arxiv.org/pdf/2411.15100)。

### 3.3 think(qwen3)との併用(vLLM 側)

- vLLM の reasoning parser(`enable_thinking` / reasoning content 分離)と guided decoding の併用は**バージョン依存で注意が要る**(推論トークンにも文法が掛かると `<think>` を割り込ませられない問題は ollama と同型)。一次の網羅ドキュメントは薄く**未確認**。本シミュの vllm.py は既に chat 経路で `chat_template_kwargs={"enable_thinking": think}`、`<think>…</think>` 剥がしを実装済み=**guided_json を足すなら think=True 経路には適用しない**運用が安全(§5.1 と同じ結論)。

---

## 4. 現実装との接合点

### 4.1 キャッシュキー(`cache.py`)— format 追加は必須

- 現行 `_key` = `sha256(model.name + temperature + max_tokens + think + prompt)`(L32-34)。**format は入っていない**。現状は format が定数(常に json)なので衝突しないが、**ノブで format を可変にした瞬間、`none`/`json`/`schema` は同一キーに潰れて旧応答を誤再生する**(依頼の仮説どおり=真)。
- 対処は既存の `think` と同型: `_key` の JSON blob に `"f": format_mode` を1個足す。これで format 別に独立キャッシュ=モデル交換保険の検証(ON/OFF 比較)が別名で安全に並走できる。
- 副次: `backend.name`(D13, URL非依存)は変えない設計を維持。format はキーの独立フィールドにするのが「think と対称」で読みやすい。

### 4.2 parse_action / propose.rule — union スキーマの難所 ★

- `parse_action` は 13 行動を扱い、**別名キー吸収(`text`/`content`/`message`…)・数値クリップ・途中切れ修復**という**寛容さ**が売り。schema モードで**キー名を厳格化すると、この寛容さと衝突**(モデルが `content` で返しても文法が `text` を強制=モデル側が矛盾に陥る/破損)。
- 最難関は **`propose`**: `rule` が**自由形の入れ子 dict**(型は RRuleBook が成立時に検証、`deliberate.py` L365-368)。**全 13 行動を1つの JSON Schema(anyOf/oneof union)で表し、かつ可変 `rule` を許す**のは、書けはするが**巨大で脆く、文法コンパイルも重い**。しかも `reflect`(salient 配列+可変キー)も別系統。
- 結論: **schema モードの全行動 union は当面見送り**。まず **`"json"` モード(構文のみ強制)**が、寛容正規化を壊さず・propose の自由 rule も通せて安全。schema は「単一行動を狙い撃つ」将来拡張(例: 崩れやすいモデルで speak だけ `{"action":"speak","text":str}` を強制)に限定する。

### 4.3 現行 ollama の「既定 json」— 「既定OFF」の意味に注意 ★

- **ゴールデン(`golden_baseline_l1.json`)は mock 生成**で、mock は format を一切見ない=**format ノブは mock 経路をバイト単位で変えない**(「既定OFF=ゴールデン不変」は自明に真)。
- ただし**実LLM較正ラン(calib_llm4b/8b・fallback 0%)は全て format=json で取得済み**。ノブ既定を安直に `none` にすると、**ollama の実LLM挙動が較正時と変わり、既存の実LLMキャッシュ(name 一致)も意味が変わる**。→ **ノブの ollama 既定は現行維持の `"json"` にすべき**(`none`/`schema` を opt-in)。「OFF」という言葉は「schema 強制を既定で使わない」の意に解し、**json モードは現状どおり既定 ON** と整理するのが実装事故を防ぐ。

### 4.4 router / vllm の配線面

- `router.py` は戻り値・呼数に不干渉の dispatch のみ。**format は「子バックエンドの構築時属性」**にするのが最も非侵襲(generate() 署名 `base.py` を触らない)。例: `OllamaBackend(model, format_mode="json")` / `VllmBackend(model, format_mode="schema")`。router 設定の子ごとに `format` を書けば purpose 別・モデル別に出し分く(崩れるモデルの子だけ schema、qwen3 の子は json 等)。
- vllm.py 側は `format_mode` に応じて body を `json_object`(現行)/`json_schema` or `guided_json`(schema)/無指定(none)に分岐。400 フォールバック機構(L97-98)はそのまま流用。

---

## 5. 設計提案(ノブ・テスト計画)

> すべて**提案**。実装はユーザー合意後(pre-coding-alignment)。数値・挙動は本選実機で要確認。

### 5.1 ノブ設計案

- **キー**: `model.format`(`conf/config.yaml` の model ブロック)。値 `none | json | schema`。
- **既定**: **`json`(=現行 ollama 挙動を保存)**。§4.3 の通り `none` を既定にすると較正が変わるため。mock は無視(バイト一致)。
- **think 境界の尊重(必須)**: `think=True` の呼(reflect)には **format を適用しない**(json/schema とも)。実装は「think なら format を強制的に none 扱い」の1行ガード。理由=§1.3(思考抑制/JSON破損)・§2.3(推論をJSONで潰さない)。
- **purpose/子ごと指定**: router 経由で子バックエンドの構築属性として持たせ、purpose 別・モデル別に上書き可(§4.4)。
- **schema の適用範囲**: 当面 `schema` は**単一行動狙い撃ちのみ**(全行動 union は非推奨=§4.2)。既定運用は `json`。

### 5.2 スキーマ強制の段階

1. **第1段(推奨・今すぐ効く保険)**: `json` モードを**ノブ化するだけ**(実質は現状を明示化+`none` 逃げ道+cache キー整備)。モデル交換で JSON が崩れたら子単位で `json` を担保、think 系は除外。
2. **第2段(将来)**: 崩れる特定モデル×特定行動に限り `schema` を狙い撃つ。propose/reflect は対象外。vLLM では `guided_json`(xgrammar)に同ノブから配線。

### 5.3 キャッシュキーへの format 追加

- **要**(§4.1)。`_key` の blob に `"f": format_mode` を追加(`think` と同型)。format 別に独立キャッシュ=ON/OFF 比較ランが混線しない。既存キャッシュ(format=json 時代)との一致を保つには、**既定 `json` のときのキー文字列を現行と同一に保つ**移行(例: `format=="json"` なら従来キー、それ以外のみ `"f"` を加える)も選べる=**既存 llm_cache の再利用を壊さない**。二案のどちらを採るかはユーザー判断。

### 5.4 導入手順・テスト項目(既定OFF=ゴールデン不変を守る)

- **T1(OFF一致)**: mock でゴールデン L1 バイト一致(`golden_baseline_l1.json`)。format ノブが mock 経路に一切触れないことを保証(format=none/json/schema いずれでも mock 出力不変)。
- **T2(cache 分離)**: 同一 prompt/params で format を変えると別キーになり、旧応答を誤再生しないことの単体テスト(`cache.py`)。
- **T3(think ガード)**: reflect(think=True)呼で format が none 扱いになる(schema/json が body に載らない)ことのテスト。
- **T4(ON 時の実効・実LLM ≤24step スモーク)**: `validation-runs-short` 準拠。ollama qwen3:4b で format=json(現行)vs format=none を比較し、**fallback 率**と**distinct-2(発話多様性)**、**日本語質の目視**を並べる。schema 狙い撃ちは対象行動のみで遵守率を測る。**フルデイ実LLMランはしない**。
- **T5(vLLM 疎通・本選)**: `guided_json` を1子に配線し、response_format 400 フォールバックが効くこと・スキーマ再利用でスループット劣化が許容内かを bench で確認。

### 5.5 リスク(大きい順)

1. **think 干渉(最大)**: reflect は think=True + 現行 format=json。§1.3 の GBNF 抑制で**内省の思考が実行されない**恐れ(config `reflect_think:true` の意図と矛盾)。ノブ実装時に think 境界ガード(§5.1)を**同時に入れないと、format ノブが内省を静かに壊す**。※本シミュの reflect-think 周りは既知の注意領域であり、ノブ設計は必ずこの相互作用を前提にすること。
2. **空応答/JSON破損**: schema+think の `{"{`(#10929)、json モードの空白暴走。既定 json 維持+think 除外で回避、`_loads_lenient` が最終防波堤。
3. **日本語品質・多様性の低下**: schema で温度0を強いると distinct が落ちる(未確認だが機構上確実)。→ text 無制約の json モードに留め、schema は狙い撃ちのみ(§2.3・T4)。
4. **cache 誤再生**: format をキーに入れ忘れると ON/OFF 比較が汚染(§4.1)。T2 で担保。
5. **既定 none 化の事故**: 較正済み ollama 挙動を無自覚に変える(§4.3)。既定 json で回避。

---

## 6. 出典(公式優先。アクセス日 = 2026-07-14)

**ollama(公式)**
- [Structured Outputs — Ollama 公式docs](https://docs.ollama.com/capabilities/structured-outputs)
- [Thinking — Ollama 公式docs](https://docs.ollama.com/capabilities/thinking)
- [ollama/docs/api.md — GitHub(format の /api/generate・/api/chat 例)](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Structured outputs — Ollama 公式ブログ(2024-12-06, v0.5)](https://ollama.com/blog/structured-outputs)

**ollama × think × format(挙動の一次証拠)**
- [Ollama の JSON モードと thinking の相互作用 — 7shi(Zenn, GBNF が `<think>` を抑制する解析)](https://zenn.dev/7shi/articles/fa36989a04c9ed?locale=en)
- [ollama#10929 — thinking + structured output で invalid JS(`{"{`, qwen3, Open)](https://github.com/ollama/ollama/issues/10929)
- [ollama#10976 — thinking + tools + qwen3 = empty output](https://github.com/ollama/ollama/issues/10976)

**構造化 vs 品質の文献**
- [Let Me Speak Freely? — arXiv:2408.02442(HTML)](https://arxiv.org/html/2408.02442v1) / [ACL Anthology 2024.emnlp-industry.91](https://aclanthology.org/2024.emnlp-industry.91.pdf)
- [Say What You Mean: A Response to 'Let Me Speak Freely' — dottxt](https://blog.dottxt.ai/say-what-you-mean.html) / [outlines discussion #1117](https://github.com/dottxt-ai/outlines/discussions/1117)
- [JSONSchemaBench(構造化出力ベンチ)— arXiv:2501.10868](https://arxiv.org/html/2501.10868v1)

**vLLM(本選)**
- [Structured Outputs — vLLM 公式docs(v0.8.2)](https://docs.vllm.ai/en/v0.8.2/features/structured_outputs.html)
- [Structured outputs in vLLM — Red Hat Developer(2025-06-03)](https://developers.redhat.com/articles/2025/06/03/structured-outputs-vllm-guiding-ai-responses)
- [Guided Decoding Performance: vLLM & SGLang — SqueezeBits](https://blog.squeezebits.com/guided-decoding-performance-vllm-sglang)
- [XGrammar — arXiv:2411.15100](https://arxiv.org/pdf/2411.15100)

**リポジトリ内(接合点の実物・既存調査)**
- `src/society/llm/ollama.py`(format=json 無条件付与)/ `cache.py`(_key に format なし)/ `vllm.py`(response_format json_object・400 フォールバック)/ `router.py`(dispatch のみ・戻り値不干渉)
- `src/society/cognition/deliberate.py`(`_HEADER_*` / `parse_action` の 13 行動・propose.rule 自由 dict)
- `conf/config.yaml` model ブロック(`reflect_think:true` ほか)
- `docs/plans/engine-architecture.md §3`(計画A/B/C)/ `docs/research/llm-model-selection.md`(R2 JSON 遵守・実測 fallback 0%)/ `docs/research/token-budgets.md`(空/未パース 11〜18%・reflect 予算)
