# マルチモデル LOD 実装計画(第22バッチ 2026-07-12・計画のみ・実装なし)

体制: Opusリサーチ([multi-model-lod.md](../research/multi-model-lod.md))→ Fable統合(本書)。
元依頼: 「複数のローカルLLM・APIモデルに対応するようLLM周りを改修+一度のシミュで複数モデルを
使う際のLOD設計の見直し。まずリサーチ→結果から実装計画を出す(実装はまだしない)」。

## 結論(リサーチからの設計判断)
1. **LODの第一軸は purpose(呼種)別**。reflect(3.8%)=大モデル/deliberate(92.7%)=小モデル。
   全員一様なので呼数もモデルも k と交絡しない=R1無傷。既存 FleetLLM の tiers seam が原型。
2. **動的エスカレーション(崩れたら大モデルへ再送)は不採用**。呼数が変動し R1 を壊す。
   ルーティングは (purpose, agent_tier) の決め打ちのみ。「JSON崩れ→routine fallback」は現行のまま
   (エスカレーション先が非LLMなので呼数不変)。
3. **agent-tier LOD(前景=大/背景=小)は「割当方式」が研究の生命線**。
   ★リサーチの「固定traitで選抜」案は**採らない方向を推奨**: モデル能力が生得特性と相関すると、
   R²(k) に「生得の優位」を実装側から注入してしまう(k*研究の自殺点)。本命は
   **trait非依存・k非依存の決定論割当**(初期化時の専用 stream "model_tier" 1回のみ、または config の
   明示リスト)。trait連動割当は「それ自体を操作した実験条件」としてのみ許す。
4. **API混載の使いどころは「前景の少数個体 or reflect」のみ**。全体API化は k×seed 掃引
   (15-40ラン)で破綻($2.1k〜$23k)。本命=全ローカル、APIは品質の上澄み買い(Batch 50%引き必須)。
5. **再現性は llm_cache が唯一の実体**(Anthropic 現行世代は temperature/seed 撤廃=完全非決定)。
   「初回ランでキャッシュ生成→以降は再生でバイト一致」の規律を API 混載でも固定する。

## 実装フェーズ(承認後に着手)

### M1 — APIバックエンド増設(独立ファイルのみ・1日)
- `src/society/llm/openai_compat.py`(新規): OpenAI互換 /v1/chat/completions。OpenAI・Gemini
  (OpenAI互換エンドポイント)・llama.cpp server・LM Studio まで1実装でカバー。標準ライブラリのみ
  (urllib、vllm.py と同流儀)。`name = f"api/{model}"`。エラーは `__api_error__: ...` を返し
  上位 fallback(D16)。
- `src/society/llm/anthropic.py`(新規): ネイティブ Messages API(temp/seed なし・structured
  outputs 対応が OpenAI 互換と異なるため分離)。`name = f"anthropic/{model}"`。
- **APIキーは環境変数のみ**(ANTHROPIC_API_KEY / OPENAI_API_KEY / GEMINI_API_KEY)。コード・conf・
  ログ・キャッシュファイルへの書き込み禁止(ODPTキーと同じ扱い。キャッシュに入るのは応答本文のみ)。
- テスト: HTTP をモックした単体(リクエスト整形・エラー→fallback 文字列・name 安定性)。実疎通は
  ユーザーのキー投入後に1呼だけ(呼んだ事実と課金をユーザーに報告)。

### M2 — 合成ルータ RouterLLM(1日)
- `src/society/llm/router.py`(新規): `generate()` で rng_key の purpose(先頭セグメント)を見て
  子バックエンドへ dispatch。**子は各自 CachedLLM で包む**(キャッシュキーは子の name で分離=D13が
  そのまま効く。ルータ自身は無名でキーに関与しない)。
- config 案(既定は現行と完全同一):
  ```yaml
  model:
    backend: ollama          # 既存の単一指定は不変(mock|ollama|vllm|router)
    # backend: router のときだけ読む:
    router:
      default:  {backend: ollama, name: "qwen3:4b"}
      purpose:                       # purpose-LOD(R1安全・最初に使う層)
        reflect: {backend: ollama, name: "qwen3:14b"}
      # agent_tier: (M3で追加。M2では未実装キー=エラーにする)
  ```
- simulation.py のバックエンド構築分岐に `router` を追加(構築のみ・呼び出し経路は不変)。
- FleetLLM は「同一モデルの複数サーバ」担当として存置。router の子に fleet を置けば
  本選7GPUの「reflect=32B×TP2、deliberate=8B×5」構成(リサーチ§2.2 構成B)が組める。
- テスト: ①mock 子2つの router で単一 mock と**同一呼び出し列**(配線が呼数・順序を変えない)
  ②purpose 別 dispatch の決定論 ③キャッシュが子 name 別に分離 ④既定 config(router 不使用)で
  ゴールデン L1 バイト一致 ⑤_FixedLLM で k free/off の呼数 parity(router 経由でも不変)。

### M3 — agent-tier LOD(0.5日+検証・★割当方式のユーザー決定が前提)
- router.agent_tier: `{fg: {...}, bg: {...}}` + 割当は初期化時に1回、専用 stream("model_tier")
  から決定論生成(trait 非依存)。tier は L1(agents.json)に記録し、解析は tier 内比較を既定に。
- R1ガード: 割当が k・実行時状態・traits に触れないことをテストで固定(新 stream 1本のみ)。
- mock はモデル階層を模せないため、配線検証=mock/効果測定=実LLM(validation-runs-short 準拠)。

### M4 — 運用プロファイルと計測(本選前)
- conf/profiles: 手元(OLLAMA_MAX_LOADED_MODELS=2 で 4b+14b 常駐)/本選7GPU(vLLM プロセス分離
  +GPU割当表)/API混載(reflect=Haiku or Sonnet・Batch 事前生成→キャッシュ再生)。
- bench.py 拡張で tier別 tok/s・fallback率・キャッシュヒット率を1表に。

## OPEN(ユーザー判断が要る点)
1. **agent-tier 割当方式**: 独立決定論(推奨)/trait連動(実験条件としてのみ)/当面 purpose-LOD のみ。
2. **最初に実装するAPI**: openai_compat(汎用・Gemini も通る)先行を推奨。anthropic は品質検証用に次点。
3. **API課金の上限**: スモーク・前景実験の予算(目安: 検証 <$5、前景10%×1日ラン <$1)。
4. M1-M2 だけ先行(purpose-LOD まで)か、M3 まで一気か。

## やらないこと(理由つき)
- 動的カスケード/学習ルータ(RouteLLM型): 呼数変動=R1違反リスク+学習コスト。決め打ちで足りる。
- <2B の背景モデル: 日本語・JSON の実データなし(未確認)。背景は routine.py(ルールベース)が第一候補。
- SGLang への乗り換え: 既存 vllm.py/fleet.py が動いており積極理由なし(本選で prefix 共有が
  ボトルネック化したら再訪)。
- archetype 集約(AgentTorch 型): 個体異質性を潰す=k*研究と正面衝突(compute-efficiency §4 既決)。

## 受け入れ条件(実装時)
- 既定 config で L1 ゴールデンバイト一致(router は opt-in)。
- _FixedLLM parity: k∈{free,off} で呼数一致が router 経由でも成立。
- 新乱数は "model_tier" stream 1本のみ(M3)。それ以外は乱数ゼロ。
- キーがログ・キャッシュ・L1 に一切出ないことの検査(文字列走査テスト)。
- 実データ規模の退化検査(300体級の既存ランを router=単一子で再現しバイト一致)。
