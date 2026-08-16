# 発話・内省の一貫性(coherence)とモデル選択 — 「支離滅裂さ」の根治リサーチ

- 種別: リサーチ(Web + GitHub + リポジトリ監査のみ)。**src 非編集・実LLM実行なし・git 操作なし**。成果物は本ファイル1点。
- 実施: 2026-08-17。
- 背景(ユーザー評価): 「発話・内省の内容のレベルが低い・支離滅裂に感じる。一貫性のある生成のためのモデル変更 or プロンプト再設計が必要」。
- 実測の土台(devlog Entry 134・GPUサーバー・perf2k144): deliberate=parse 100% / 1.79s / 応答短(中央値71字)・plan=**parse 33%(壊れ67%)**(broken JSON・p95 8,793字)・reflect=**19s/呼・約2,146字**。艦隊スループット 1.8〜2.5 calls/s/サーバー(w16→w64 で +35% のみ=計算律速)。
- 前提の必読(重複を避け差分を書く):
  - [`conversation-pipeline.md`](conversation-pipeline.md)(第37)— 会話パイプライン監査。「対話履歴なし・宛先が距離のみ・グループ会話なし」の構造診断は本ドクの出発点(その後 dialog_history / reply_partner=closeness は本番 ON 済み)。
  - [`constrained-decoding.md`](constrained-decoding.md) — ollama 時代の format×think 調査。「構造(封筒)は強制・中身は自由」の落とし所は現行設計に反映済み。
  - [`llm-model-selection.md`](llm-model-selection.md) / [`multi-model-lod.md`](multi-model-lod.md) — モデル候補と 7GPU 配置案(2026-07 時点)。本ドクは 2026-08 時点の裏取りと「支離滅裂さ」観点の再評価を足す。
- 出典方針: 一次ソース(公式リポジトリ・arXiv・公式ドキュメント・実在確認済み GitHub ファイル)優先。未確認・推測は明記。リポジトリ内の実測は run 名・ファイルパスを付す。

---

## 0. 結論(5行)

1. **「支離滅裂さ」の主因はモデルの地力ではなく入力の作り**である: (a) 逐語記憶の再注入ループ(壊れた発話がそのまま記憶→翌プロンプトへ=増幅系)、(b) 全 purpose 共通ヘッダの指示矛盾(reflect/plan のプロンプトに「出力は次のJSON1個のみ」が2回)、(c) 対話のスレッド構造なし(2往復1行連結のみ)。これらは 8B→14B/32B に替えても残る(§3)。
2. **plan の 67% JSON 壊れは「スキーマのトークン需要 > plan_max_tokens=448」の切断が第一容疑**(day_plan v1 は 4〜8ブロック×約50〜70tok+自由文で 350〜700tok 超を要求)。guided decoding は切断を防げない=まず予算の右サイズ化+ブロック数上限の引き下げ(§5)。
3. プロンプト再設計は **P1(矛盾除去・記憶の要約化・低リスク)→ P2(会話スレッド化)→ P3(内省の二段化)**の3段で、いずれも A8 ミニトーナメント(scripts/behavior_tournament.py)で機械採点できる(§8)。
4. モデルは **14B-AWQ(取得済み)を reflect/plan tier へ**(既存 tiers seam・R1安全)が最小リスクの第一手。発話 92.7% に効くモデル手は **Qwen3-Swallow-8B-RL-AWQ のドロップイン置換**(公式AWQ・同サイズ同速度・要A8ゲート)のみ。32B-AWQ は重み実測 19.33GB=KV 約2GB で高並列が崩壊するため非推奨。27B 世代(Qwen3.5/3.6・Gemma4-31B)は AWQ でも約21GB で単機不可(§4)。
5. 推奨は **「P1+予算右サイズ化(即日)→ A8 で {現行/P1束}×{8B/14B} の4セルを同時判定 → 14B tier 昇格 → 本選後に P2(記憶要約化=増幅ループ遮断)と Swallow-8B」**の併用案(§9)。

---

## 1. 何がどう壊れているか — リポジトリ一次データの監査

### 1.1 実測数字(perf2k144・vLLM×Qwen3-8B-AWQ)

devlog Entry 134(2026-08-16・実形状プロンプト300件の R_eff 実測)より:

| purpose | 結果 | 解釈 |
|---|---|---|
| deliberate | parse 100%・1.79s・応答中央値 71字 | 形式は堅い。**内容が短く浅い**(320tok 上限のうち実使用わずか) |
| plan | **parse 33%(壊れ67%)**・p95 8,793字 | day_plan v1 スキーマ有効(finals_observe.yaml L588-589)。壊れ方は長大化→切断(§1.4) |
| reflect | 19s/呼・約2,146字 | reflect_max_tokens=768 にほぼ張り付き(768tok×約2.8字/tok≈2,150字)=**毎回上限まで書いて切れている**疑い |

### 1.2 支離滅裂さの実例と増幅機構(runs/night_llm_100a3d・qwen3:4b 実LLM)

ジャーナル(llm_journal.jsonl.gz)から非キャッシュ呼 3,728 件を集計:

- **プロンプト長**: deliberate 中央値 3,162字(p95 4,507字)。約30種類の1行文脈(ペルソナ・時刻・場所・気分・記憶・信念・間柄・タイムライン…)を列挙する形。
- **★逐語記憶の再注入ループ**: deliberate プロンプトの **87%** が「直近の出来事:/記憶に残っていること:/思い出したこと:」行に **80字超の発話逐語引用**を含む。実例(agent 林修・23歳):
  - 記憶行: 『佐々木浩二が「…モスバーガーの新メニューでおすすめのコーヒーが1000円で買えるなら、今すぐチェックしてHANAKONAで音を収集するプロジェクトに参加しよう。でも、この雨の音をスマホで30秒録音する前に…」と言っていた』
  - それを受けた発話: 『山本さん、昨日のGoccioの広告を水に溶かすとしたら、井上さんのコーヒーの温度が下がるスピードと、雨の降り方が同じになるよね。』
  - **機構**: 小型モデルの一度の脱線(シュールな連想)が hear 経由で逐語のまま複数エージェントの記憶に入り、翌プロンプトの「記憶」「タイムライン」行として再注入され、模倣・連想でさらに増幅される。**支離滅裂さは個々の生成の失敗ではなく閉ループの発散**(conversation-pipeline.md §7 の「記憶→内省→信念の閉ループ」が、要約・正規化なしでは毒も循環させる)。
- **SNS 由来の退化記憶**: 「SNSで見た: 『RT @山本真央: RT @斎藤浩二: RT @』」のような**切り詰められた RT 連鎖**が記憶スロットを占有(40字切り詰め+RT ネストの相互作用)。内省の salient にもこの断片が採点される。
- **文脈のフィールド混入**: plan 出力の place 欄に『渋: 2026年8月2日(日)、07:10、渋谷の前、雨、30℃、26600円、落ち着いている。』=プロンプトの状況行がそのまま漏出(4B での実例。8B でも plan 壊れの一形態として同型が疑われる)。

### 1.3 プロンプト構造の指示矛盾(全 purpose 共通ヘッダ)

`cognition/deliberate.build_prompt` は発話・計画・内省・recall の**全経路で共有**され、冒頭に必ず行動メニューを置く:

```
出力は次のいずれかの JSON 1個のみ(キー名は厳守):
  {"action": "speak", ...} / {"action": "post", ...} / {"action": "wander"} ...
```

reflect / plan / recall はこの後ろに**別の**「出力は次の JSON 1個のみ」ブロックを足す(reflection.py `_REFLECT_TASK`・planning.py `_PLAN_TASK`・day_plan.schema_prompt)。つまり**1プロンプトに相互排他の出力指示が2つ**あり、モデルは「後勝ち」を期待されている。8B 級では概ね後勝ちするが、(a) 指示追従の予算を無駄に食う、(b) 行動メニューの語彙(speak/post…)が plan/reflect の自由文欄へ混入する誘因になる。ジャーナル実物で確認(runs/night_llm_100a3d)。

### 1.4 plan 67% 壊れの第一容疑 = トークン予算の不足(スキーマ需要との不整合)

- day_plan v1(finals ON)は `min_blocks:4 / max_blocks:8`(conf/config.yaml L1235-1237)。1ブロック=9欄(reason 自由文先頭+start/end/place/act/with/aim/priority/flex/note)≈ JSON で 150〜250字 ≈ **50〜80tok**。4〜8ブロック+mood/carry+if_then(≤3)で**需要 350〜700tok+**。
- これに対し finals の `plan_max_tokens: 448`(conf/profiles/finals-vllm7.yaml L34)。**5ブロック以上を書き始めた時点で切断がほぼ確定**する。`_loads_lenient` の閉じ括弧補完は配列途中の切断を救えない。
- 整合する傍証: p95 8,793字という長大応答(切断前の暴走)・SchemaBench の 7B 素の validation error は 18%(day_plan.py 冒頭の設計注記)であり **67% はモデル非適合だけでは説明できない**。
- なお fleet の 4xx 誤爆修正(devlog Entry 132)で判明した通り、**プロンプト+max_tokens > max_model_len 8192** の呼も実在した=入力側の長大化も併発している。

### 1.5 配線上の注意(vLLM バックエンド)

`src/society/llm/vllm.py`:

- `/v1/completions` を優先(404 で chat へ恒久切替)。**completions 経路は chat テンプレートを適用しない生テキスト継続**=instruct モデルに素の文書続きを書かせている。Qwen3 の `/no_think` ソフトスイッチをプロンプト末尾に付す運用(実機挙動は「本選で疎通確認」とコード注記=未検証)。
- `response_format: {"type": "json_object"}`(スキーマなしの JSON モード)を think=False の呼にだけ付す。guided_json(スキーマ強制)は未使用。
- 応答冒頭の `<think>...</think>` は正規表現で剥がす。

---

## 2. 一貫性の設計パターン(文献+GitHub 実装)

以下は全 URL アクセス・実在確認済み(2026-08-17)。

### 2.1 設計パターン表 — 「支離滅裂さの原因 → 各実装の対処」

| 原因 | Generative Agents([arXiv:2304.03442](https://arxiv.org/abs/2304.03442) / [GitHub](https://github.com/joonspk-research/generative_agents)) | ai-town([GitHub](https://github.com/a16z-infra/ai-town)) | Concordia([GitHub](https://github.com/google-deepmind/concordia)) | Project Sid([arXiv:2411.00114](https://arxiv.org/abs/2411.00114)) | AgentSociety([arXiv:2502.08691](https://arxiv.org/abs/2502.08691) / [GitHub](https://github.com/tsinghua-fib-lab/agentsociety)) | TinyTroupe([GitHub](https://github.com/microsoft/TinyTroupe)) |
|---|---|---|---|---|---|---|
| 文脈の欠落 | ISS(固定8行)+現在地+現在文脈を毎回注入 | identity+plan+「最後に話した時間」 | Component の pre_act 値を毎回合成 | Cognitive Controller の最新決定を全モジュールへ放送 | Profile+Status+関係タイプ/強度 | 巨大 system prompt+認知状態(GOALS/CONTEXT/ATTENTION/EMOTIONS)毎ターン更新 |
| 記憶の非選択 | recency×importance×relevance 加重 top-30 | embedding 検索 10倍 overfetch→3因子順位付け **top-3** | 関連記憶 25件(クエリ=**状況要約そのもの**) | Memory モジュール(時間スケール別) | Stream Memory(Event/Perception Flow) | エピソード/意味記憶の分離 |
| ペルソナ希釈 | ISS をほぼ全プロンプトに再注入 | identity 毎回全文 | SelfPerception 等の自己認識 Component(回答を記憶へ書き戻し) | 発話系を CC 決定で「強く条件付け」 | Profile 毎回+attitude/emotion を永続化 | 「ペルソナは組み込み特性に**常に優先**」+adherence 検証器 |
| 対話履歴なし | 会話中=**全文**+過去会話=**関係要約(past context)** | 同一会話=全文+過去会話=一人称要約を記憶化 | 記憶 Component 経由 | Memory が会話を保存 | **ペア別 chat history 全文**注入 | ターン制+全履歴 |
| 毎回独立サンプリング | 会話は同一プロンプト内で反復生成(iterative_convo) | 会話単位でプロンプト連続 | Component 状態が持続 | 並行モジュールが CC 決定を共有 | **前回の態度/感情値を渡して更新**(read-update-write) | 「前状態を起点に更新」と明示指示 |

### 2.2 個別実装の要点(移植候補になる具体構造)

**(1) Generative Agents(Park et al. 2023)**
- 記憶検索: `score = α_r·recency + α_i·importance + α_v·relevance`。論文は全α=1・**減衰0.995**・importance は LLM 採点(1=mundane〜10=poignant)・relevance は **embedding コサイン**・各成分 min-max 正規化。**実コード(retrieve.py)は gw=[0.5, 3, 2](recency 0.5/relevance 3/importance 2)で top-30**。
- 内省ツリー: 直近知覚の importance 合計が**閾値150**で発火(実運用 日2〜3回)→直近100件→「最も顕著な高レベル質問を3つ」→各質問で再検索→**「insight (because of 1, 5, 3)」形式=根拠記憶を引用**した洞察を生成し、それ自体を記憶へ(=内省の内省が可能な再帰ツリー)。プロンプト現物 [`insight_and_evidence_v1.txt`](https://github.com/joonspk-research/generative_agents/blob/main/reverie/backend_server/persona/prompt_template/v2/insight_and_evidence_v1.txt)。
- 計画: 日次骨子5〜8チャンク→1時間→**5〜15分**へ再帰分解。
- 会話プロンプト現物 [`iterative_convo_v1.txt`](https://github.com/joonspk-research/generative_agents/blob/main/reverie/backend_server/persona/prompt_template/v3_ChatGPT/iterative_convo_v1.txt) は **6層**: ISS+検索記憶+Past Context(過去関係の要約)+現在地+現在文脈+**現会話の全文** → 「次の一言+会話は終わったか(JSON bool)」を同時出力(本リポ engaged の end 欄の先例)。
- 会話後の保存は**4分解**: summarize_conversation / memo_on_convo / planning_thought_on_convo / summarize_chat_relationship(全文でなく要約・関係・メモ・計画思考として記憶化)。
- 温度(run_gpt_prompt.py 確認): **判定・分解・採点=0 / 生成系=0.5〜1** の使い分け。

**(2) ai-town(a16z)** — 記憶検索は n×10 を過剰取得→3因子(recency=0.99^経過時間h)→**top-3 だけ注入**。過去会話は終了時に**一人称要約**(「I liked/disliked this interaction」付き)へ変換して記憶化。max_tokens=300・話者名 stop 語で他人の発話生成を切断。

**(3) Concordia(DeepMind)** — `all_similar_memories.py`: 他 Component の出力を「Summarize the statements above.」で**状況要約→その要約文を検索クエリ**にして 25 件注入。`question_of_recent_memories.py`: 「私はどんな人間か/今どんな状況か/私のような人はどうするか」(logic of appropriateness の3段)を毎回問うて回答を**記憶へ書き戻す**=自己認識の連続性を明示維持。

**(4) Project Sid(PIANO・500体)** — 並行10モジュールが独立に LLM を呼ぶと「**say one thing but actually do something else**」(言動不一致)が起きる。対処は **Cognitive Controller**: 高レベル決定を下す唯一の場所+**情報ボトルネック**(CC への入力を絞る)+決定を全モジュールへ放送し「**発話モジュールを CC 決定で強く条件付ける**」。coherence の定量ベンチはなく CC 有無の ablation で間接測定。

**(5) AgentSociety(清華・1万体超・DeepSeek-V3 API)** — 記憶=Profile(静的)/Status(動的)/Stream(Event+Perception Flow)。**態度・感情・日次思考は「前回値をプロンプトに渡して更新」**(read-update-write)=毎回独立サンプリングの解消。対話はペア別 chat history 全文+関係タイプ/強度(0-1)注入・出力100字上限。

**(6) TinyTroupe(Microsoft)** — [`tiny_person.mustache`](https://github.com/microsoft/TinyTroupe/blob/main/tinytroupe/agent/prompts/tiny_person.mustache) の一貫性文言が最も明示的: 「persona characteristics **ALWAYS OVERRIDE ANY BUILT-IN CHARACTERISTICS**」「ペルソナが知らないはずのことは**知らないふりをする**(捏造禁止)」「直前と同一の行動を**繰り返さない**」「低品質なら何もしない(emergency DONE)」+ 行動検証器(persona_adherence / self_consistency)。

**(7) 横断的な既知原因の文献**
- **persona drift**: Li et al.(COLM 2024, [arXiv:2402.10962](https://arxiv.org/abs/2402.10962))— LLaMA2-70B/GPT-3.5 とも「**8ターン以内**にシステムプロンプトの人格から逸脱」。原因は長対話でのシステムプロンプトへの attention 減衰。
- **Lost in the Middle**(Liu et al., [arXiv:2307.03172](https://arxiv.org/abs/2307.03172))— 関連情報が**文脈中央**にあると性能が U 字に劣化 → ペルソナ・直近発話・出力指示は**先頭か末尾**に置く根拠。
- **few-shot 例**: GA / ai-town / AgentSociety / TinyTroupe のいずれの対話プロンプトにも**実質存在しない**(確認事実)。one-shot 例の欠如は本リポの欠陥ではない。

---

## 3. 本リポの現状との差分

`src/society/cognition/` と実ジャーナルの監査(§1)を §2 のパターンに突き合わせる。

| 次元 | 参照実装の型 | 本リポの現状 | 差分(欠けているもの) |
|---|---|---|---|
| **対話履歴** | GA=現会話全文+過去関係要約 / AgentSociety=ペア別全文 | `dialog_history` ON(本番)=相手別リング8人LRU・**直近2往復を1行連結**。reply 時の相手発話1件+自分の直近発話2件 | 会話の**スレッド構造なし**(発話が「直前のやりとり:」1行に平坦化)。**過去会話の関係要約なし**(record_contact は last 40字のみ)。engaged(エピソード層・end宣言=GA iterative_convo と同型)は実装済みだが **fire OFF 保留で本番未定** |
| **記憶検索** | GA 実コード gw=[0.5,3,2]・relevance=**embedding**・top-30 / ai-town=overfetch→top-3 | 係数は GA 同値(0.5·recency+2·imp/10+3·rel)だが **relevance=部分文字列一致**(context 語の包含数/2)。recent4+retrieve3+pull2 | **意味検索がない**ため「関連」がほぼ固有名詞の字面一致=検索の実効が薄い。件数は妥当(少数精鋭) |
| **記憶の中身** | GA/ai-town=会話は**要約・一人称化して**記憶化 | hear=「Xが「(逐語全文)」と言っていた」・SNS=40字切り詰め RT 断片 | **逐語保存→逐語再注入**(87%のプロンプトに80字超引用)=§1.2 の増幅ループの根。要約化・正規化の層がない |
| **ペルソナ** | GA ISS=8行固定・ほぼ全プロンプト再注入 / TinyTroupe=優先宣言+捏造禁止 | persona 1行+self_model 1行+implicit_self 1行+目標・趣味(H6 ON時) | 量は ISS 相当あるが、**「ペルソナ優先・知らないことは知らない・直前と同一発話禁止」型の規律文言がない**(反復禁止は said 有時の1行のみ) |
| **内省の階層** | GA=閾値発火・**3質問→根拠引用付き洞察**・洞察も記憶へ(再帰) | 夜1回+deep(出来事誘発)+recall 2段。summary+salient+belief を**1呼で合成**。belief 直近3件のみ注入 | **根拠引用がない**(belief が記憶と切断された一文)。**質問生成段がない**(recall は「思い出したいこと1つ」のみ)。beliefs は追記リストで**古い belief との統合・矛盾解消がない** |
| **状況→検索クエリ** | Concordia=状況要約を検索クエリに | deliberate の retrieve コンテキスト=場所名+周囲の人名の字面 | 「いま何が起きているか」を問い直す層がない(agentic pull は内省時のみ) |
| **言動一致** | Sid=発話を最新の高レベル決定(CC)で条件付け | day_plan は routine の行き先を決めるが、**発話プロンプトに当日計画ブロックが注入されない**(schedule_line=約束のみ) | 「計画上いま何をしている最中か」が発話に条件付けされない=言(発話内容)と動(計画実行)が別系統 |
| **状態の持続** | AgentSociety=前回の態度/感情を渡して更新 | mood/affect はエンジン決定論・implicit_self EMA・self_model 更新 | 概ね同型を既に持つ(この次元は欠けていない) |
| **purpose 別プロンプト** | 全実装が**目的別に別プロンプト** | 全 purpose が deliberate ヘッダ(行動メニュー)を共有 → §1.3 の指示矛盾 | reflect/plan/recall から**行動メニューを外す**だけで矛盾解消(APC prefix 共有とのトレードオフは要設計) |
| **温度** | GA=判定0/生成0.5〜1 | 全 purpose 一律 0.7 | **plan(構造化出力)と recall(検索クエリ)が 0.7** は参照実装の流儀に反する。発話 0.7 は妥当 |
| **few-shot** | どの実装も実質なし | なし | 差分なし(追加不要) |
| **出力の切断防御** | ai-town=max_tokens 300+stop語 | plan 448tok vs スキーマ需要 350〜700tok+(§1.4) | **予算がスキーマ需要とアンバランス**なのは本リポ固有の問題 |

**要約**: 「支離滅裂さ」への寄与が大きい順に、(1) 逐語記憶の再注入ループ(要約層の欠如)、(2) 対話スレッド構造の欠如(engaged 保留)、(3) purpose 混在ヘッダの指示矛盾、(4) plan 予算不整合、(5) 意味検索の欠如、(6) 内省の根拠引用欠如。**モデルを替えても (1)〜(4) は残る**。逆に、状態持続・記憶スコア式・少数精鋭注入・few-shot 不在は既に参照実装と同水準。

---

## 4. モデル選択肢(24GB×7・日本語・2026年8月)

全 HF リポジトリは実在確認済み。前提: A5000=Ampere・FP8 非 native → **AWQ INT4 一択**([`llm-model-selection.md`](llm-model-selection.md) §3.0 と同結論)。単GPU1サーバー・TPなし基本。

### 4.1 日本語ベンチの現在地(Nejumi リーダーボード4・2026-07-10版)

| モデル | Nejumi4 総合 | 24GB 単機適合 |
|---|---:|---|
| Gemma 4 31B-it(2026-04) | 0.8077 | △(QAT w4a16 約21GB=タイト) |
| **Qwen3.5-27B**(reasoning有効) | 0.8049 | **×(AWQ 実測21GB=[QuantTrio](https://huggingface.co/QuantTrio/Qwen3.5-27B-AWQ)。視覚塔+大語彙で4bitでも縮まない)** |
| Gemma 4 26B-A4B-it(MoE 活性4B) | 0.7872 | ○(AWQ 約15GB。vLLM 用の確立した量子化リポは未特定) |
| Qwen3.5-9B(reasoning有効) | 0.7485 | ◎([AWQ 7.7GB](https://huggingface.co/QuantTrio/Qwen3.5-9B-AWQ) 等コミュニティ量子化のみ) |
| Nemotron Nano 9B v2 Japanese(2026-02) | 0.7111 | △(BF16 18GB・確立4bit なし・Mamba2=KV極小) |
| **Qwen3-8B(現行)** | **0.690** | ◎(運用中) |
| Qwen3-Swallow-32B-RL-v0.2 | 0.6782 | ○(AWQ 19.33GB=KV約2GB) |
| llm-jp-4-32b-a3b-thinking | 0.6679 | △(AWQ 未確認) |

★重要な訂正: [`llm-model-selection.md`](llm-model-selection.md) §2.7 の「Qwen3.5-27B ≈14GB INT4」見積りは**実物 AWQ 21GB で覆った**(2026-08 実在ファイル確認)。**27B 世代(Qwen3.5/3.6/Gemma4-31B)は A5000 単機 vLLM 運用が実質不可**。multi-model-lod.md の構成案は 27B 前提の部分を読み替える必要がある。

### 4.2 主要候補の比較

| 候補 | 日本語品質の根拠 | AWQ/量子化 | 24GB での KV 余地 | スループット(8B比・概算) |
|---|---|---|---|---|
| **Qwen3-14B-AWQ(取得済み)** | Shaberi3: 8B=8.0→14B=8.2(no-think)/8.3→8.5(think)([実測記事](https://zenn.dev/robustonian/articles/qwen3_vel_shaberi3)) | [公式AWQ](https://huggingface.co/Qwen/Qwen3-14B-AWQ) | 重み約9.7GB→余裕あり | **約0.6倍**(帯域律速) |
| **Qwen3-32B-AWQ** | Shaberi3: 8.4/8.7 | [公式AWQ](https://huggingface.co/Qwen/Qwen3-32B-AWQ) | **重み実測19.33GB→KV約2GB≈8Kトークン**(fp8 KV で倍増可) | **約0.29倍**+KV枯渇で並列も落ちる |
| **Qwen3-Swallow-8B-RL-v0.2-AWQ** | 8Bクラス日本語最高(自前LB 0.557・JamC-QA+3.6pt・翻訳+2.6〜7.3pt)([公式](https://swallow-llm.github.io/qwen3-swallow.en.html)) | [公式AWQ-INT4](https://huggingface.co/tokyotech-llm/Qwen3-Swallow-8B-RL-v0.2-AWQ-INT4)(GPTQ は品質劣化で公式が非公開化) | 現行と同一 | **1.0倍(ドロップイン)** |
| **Qwen3-Swallow-30B-A3B-RL-v0.2-AWQ** | 自前LB 0.591(32B密 0.609 に肉薄) | [公式AWQ-INT4](https://huggingface.co/tokyotech-llm/Qwen3-Swallow-30B-A3B-RL-v0.2-AWQ-INT4) | 重み約16-17GB(推測)→余地あり | MoE 活性約3B=**ほぼ8B並み**(要実測) |
| **Qwen3.5-9B-AWQ** | Nejumi4 0.7485(現行比+5.9pt=同サイズ帯最大ジャンプ) | コミュニティのみ([QuantTrio](https://huggingface.co/QuantTrio/Qwen3.5-9B-AWQ)/[RedHatAI w4a16](https://huggingface.co/RedHatAI/Qwen3.5-9B-quantized.w4a16)) | 7.7GB+線形注意で KV 小 | ≈1倍(新アーキ=vLLM 最新版必須・Ampere 安定性未検証) |
| gemma-3-27b-it | — | [AWQ](https://huggingface.co/pytorch/gemma-3-27b-it-AWQ-INT4) 約14GB | ○ | 約0.4倍。**Gemma 4 が出た今、選ぶ理由が薄い** |
| Sarashina2.2 / CALM3 / ELYZA | 公開 instruct が 3B 以下 / 2024年世代 / Llama-3 世代 | — | — | いずれも候補外(入手性・世代) |

### 4.3 「モデルを上げる」は何を買えて何を買えないか

- **買えるもの**: 発話の流暢さ・話題の深さ・脱線耐性(Shaberi 8B 8.0→32B 8.4)。日本語特化 CPT+RL(Swallow)は同サイズで発話の自然さを直接底上げ。
- **買えないもの①(実測)**: [Structured Output Benchmark](https://arxiv.org/html/2604.25359v1) は「**モデルサイズは構造化出力品質を予測しない**」(8B が 20B 超を上回る例・スキーマ妥当でも葉値の17-31%が誤り)。**plan 67% 壊れの主因が予算切断(§1.4)である以上、32B に替えても壊れは直らない**。
- **買えないもの②(§3)**: 逐語記憶の再注入ループ・指示矛盾・スレッド欠如は入力側の問題=モデル非依存。conversation-pipeline.md の「大きいモデルで半分は解消する」の後段(構造問題は残る)は 2026-08 でも変わらない。
- 費用: 14B 化は同 GPU 数で**約1.7倍遅**=艦隊 12-18 calls/s が 7-11 calls/s へ(全面置換の場合)。tier 限定(reflect/plan のみ 14B)なら deliberate 6本は不変=総合影響は小。

---

## 5. JSON 壊れ対策(vLLM structured outputs の現在地)

### 5.1 API の現状(2026)

- 旧 `guided_json` / `guided_decoding_backend` 系パラメータは **v0.12.0 で削除済み**。現行は `structured_outputs` パラメータ(OpenAI互換: `extra_body={"structured_outputs": {"json": <schema>}}`、`response_format={"type":"json_schema",...}` も可)+ サーバー起動時 `--structured-outputs-config.backend`(既定 auto=xgrammar/guidance 自動選択)。[公式](https://docs.vllm.ai/en/latest/features/structured_outputs/)
- 本リポ現行(vllm.py)は `response_format: json_object`(構文のみ強制・スキーマなし)。**スキーマ強制へは1段の配線追加**(constrained-decoding.md の「ノブ化」設計の vLLM 側)。

### 5.2 速度への影響(実測報告)

- xgrammar: スキーマ初回コンパイル **0.12〜0.30秒**→以後キャッシュ(JSONSchemaBench, [arXiv:2501.10868](https://arxiv.org/abs/2501.10868))。vLLM V1 では初期化が非ブロッキング化され、キャッシュ済みなら TPOT は「わずかに高い」程度([Red Hat 解説](https://developers.redhat.com/articles/2025/06/03/structured-outputs-vllm-guiding-ai-responses))。V0 outlines 時代の「バッチ全体ブロック」は解消([vLLM blog](https://vllm.ai/blog/2025-01-14-struct-decode-intro): 負荷時 TPOT 最大5倍改善)。
- [SqueezeBits ベンチ](https://blog.squeezebits.com/guided-decoding-performance-vllm-sglang)(H100・**Qwen3-8B**/32B・並行1-512): vLLM はバッチ8以上で低下が見えるが、**同一スキーマ反復では xgrammar が一貫して優位**。本シムは「同一スキーマ×反復×短出力×1.8-2.5 calls/s」= xgrammar の最良ケース(実効オーバーヘッドは数%オーダーと推測。grammar 処理は CPU 側なのでホスト CPU は監視)。
- 品質の副産物: guided なしの valid JSON 率 61〜72% という条件でも **guided ありで 96〜100%**(同ベンチ)。67% 壊れの構文成分はほぼゼロにできる。

### 5.3 品質への影響(論争の現在地)

- 「JSON-mode で推論劣化」(Let Me Speak Freely?, [arXiv:2408.02442](https://arxiv.org/abs/2408.02442): GSM8K −27〜−63pt)に対し、dottxt([Say What You Mean](https://blog.dottxt.ai/say-what-you-mean.html))と JSONSchemaBench が方法論を正して再実験→**スキーマをプロンプトに明示した上での grammar 強制は同等以上**。コンセンサスは「劣化の主因は制約でなく、**推論させずにいきなり JSON を吐かせる**設計」。
- 本リポの day_plan v1 は既に **reason 欄先頭**(自由文→構造の順)で、この落とし所(constrained-decoding.md §2.3「封筒は強制・中身は自由」)を踏んでいる=guided 化しても品質劣化の根拠は薄い。

### 5.4 Qwen3 特有の地雷(要スモーク検証)

| 組み合わせ | 既知問題 |
|---|---|
| thinking OFF 指定+guided_json | 出力 JSON 破損(先頭ゴミ)。xgrammar/guidance 両方で再現([#18819](https://github.com/vllm-project/vllm/issues/18819)) |
| **Qwen3-32B-AWQ**+thinking OFF+guided_json+temp≠0 | サービス全体ブロック([#18821](https://github.com/vllm-project/vllm/issues/18821)) |
| thinking ON+guided_json(v0.10.0) | JSON が reasoning_content 側へ入り content 空([#23074](https://github.com/vllm-project/vllm/issues/23074)・closed as not planned) |
| スキーマ機能 | minItems 拒否([#16880](https://github.com/vllm-project/vllm/issues/16880))・巨大整数境界でクラッシュ([#17894](https://github.com/vllm-project/vllm/issues/17894))・空白無限ループの増幅([#13260](https://github.com/vllm-project/vllm/issues/13260)) |

本リポは reasoning parser 未使用+completions 経路+`/no_think` ソフトスイッチという独自構成なので、上記のどれに当たるかは**本選機での組み合わせスモークが必須**(vllm.py のコード注記「実機未検証」どおり)。

### 5.5 guided が防げないもの → 適用順序

- **防げない**: max_tokens 切断(grammar は「予算内に閉じ括弧へ到達」を保証しない)・繰り返し暴走(むしろ脱出経路が塞がれ増幅しうる)。**p95 8,793字→切断のパターンは guided 単体では直らない**。
- **適用順序の推奨**:
  1. **予算の右サイズ化(即効・配線ゼロ)**: `plan_max_tokens` 448→768〜1024 or `max_blocks` 8→5(スキーマ需要 §1.4 との整合)。reflect も「毎回768張り付き」なら同根(タスク文が要求過多)。
  2. **finish_reason=="length" の計数**を summary へ(切断が本当に主因かを1整数で判定=decision_mode と同じ流儀)。
  3. その上で **plan のみ structured_outputs(xgrammar)** を A8 で A/B(§8)。スキーマは平易に: additionalProperties:false・enum 活用・maxItems/maxLength で**構造的に総長を制限**(サポート可否は要スモーク)。
  4. 2段生成(自由記述→構造化)は**呼数2倍のため本シムでは不採用**(day_plan の reason 先頭化が既に等価の効果)。

---

## 6. 改修候補

### 6.1 プロンプト再設計 P1 — 「矛盾と予算の即日修正」(最小差分・低リスク)

1. **purpose 別ヘッダ**: reflect/plan/recall のプロンプトから行動メニュー(`_HEADER_FORMS`〜)を外し、「あなたは{city}の…」+ペルソナ+文脈+**そのpurposeの出力指示1つだけ**にする(§1.3 の矛盾解消)。deliberate は不変=APC prefix への影響は reflect/plan/recall のみ(呼数の約7%)。
2. **plan 予算右サイズ**: `plan_max_tokens: 448→896` または `max_blocks: 8→5`(§5.5-1)。
3. **規律3行(TinyTroupe 型)**をペルソナ直後に固定注入: 「この人物として知らないはずのことは知らないと言う(作らない)」「直前と同じ話題・言い回しを繰り返さない」「人物設定は他の何よりも優先する」(現行の said 時のみの反復注意を常設化・中立文言)。
4. **温度の purpose 分化**: plan/recall を 0.2〜0.3 に(GA 実コードの「判定=0/生成=0.5〜1」の流儀。新 conf キー `plan_temperature` 等)。
- 期待効果: plan 壊れの大半(切断成分)解消・reflect/plan の指示追従予算回復。**発話の支離滅裂さ自体には部分効果**。

### 6.2 プロンプト再設計 P2 — 「記憶の要約化+会話スレッド」(増幅ループの遮断)

1. **hear の逐語保存をやめる**: 記憶へは「〈相手〉と〈場所〉で〈話題語1-2個〉の話をした」の決定論テンプレ(発話全文は L1 にだけ残る=観測は不変)。SNS の RT 断片(「RT @…: RT @…」)は記憶化から除外 or 元投稿本文へ正規化。→ §1.2 の 87% 逐語注入と増幅ループを根から遮断。**LLM 呼ゼロ・決定論で実装可能**。
2. **会話のスレッド化**: dialog_history の1行連結を発話者ラベル付き複数行(GA iterative_convo の「会話 so far」形式)へ。engaged(実装済み・fire 判断待ち)ON と併用で「会話の始まり〜終わり」が構造として立つ。
3. **関係の past context**: 会話終了時に record_contact の last 40字を「前回: 〈話題語〉について話した(好感/不快)」の決定論要約へ拡張(GA の summarize_chat_relationship の無 LLM 近似)。
- 期待効果: **支離滅裂さの主因(§3 の (1)(2))への直接打撃**。発話品質の改善幅は P1 より大きいはず(推測)。

### 6.3 プロンプト再設計 P3 — 「内省の根拠引用」(質の底上げ・任意)

- reflect JSON に `evidence`(salient のどれに基づく belief か)を足し、belief を「一文+根拠」で保存(GA insight (because of 1,5,3) の型)。beliefs 追記リストに「矛盾する古い belief を1つ選んで更新してよい」の統合指示を足す。呼数不変。
- 期待効果: 内省の「レベルの低さ」(浮ついた一般論 belief)への対処。k の作用点なので **R1 上の検討(writeback 経路の意味が変わらないか)が必要**。

### 6.4 モデル変更 M1 — 「14B(取得済み)を reflect/plan tier へ」

- 既存 tiers seam(finals-vllm7.yaml)で reflect+plan(呼数約7%)だけ 14B サーバー1本へ。deliberate 6本は 8B のまま=スループット税ほぼゼロ。R1 安全(purpose 一様)。
- 期待効果: 内省・計画の内容品質+0.2〜0.3(Shaberi 比)。**発話(92.7%)は変わらない**点に注意。

### 6.5 モデル変更 M2 — 「Qwen3-Swallow-8B-RL-AWQ へのドロップイン置換」(要 A8 ゲート)

- 同サイズ・同速度・同運用で日本語だけ強化(§4.2)。取得→A8(束は finals 相当・8B vs Swallow-8B)→JSON 追従・`/no_think` 挙動・発話の自然さを見て置換判断。
- 発話 92.7% に効く唯一のモデル案。将来枠: Swallow-30B-A3B(32B級品質×8B級速度の本命だが MoE+新規取得=検証重め)・Qwen3.5-9B(伸びしろ最大・vLLM 最新版必須=本選持ち込みは非推奨)。

### 6.6 併用案(推奨の骨格)

P1(即日)→ A8 で「8B vs 14B」「現行束 vs P1束」「(取得後)vs Swallow-8B」を同一装置で判定 → M1(tier)は数字が出た時点で conf 1行 → P2 は本選のリハーサル窓 or 本選後に縦煙+A8 で検収 → guided_json(plan のみ)は §5.5 の順序で。

---

## 7. 各案の費用

| 案 | 実装工数(目安) | スループット影響 | 較正・検収コスト | リスク |
|---|---|---|---|---|
| P1 矛盾除去+予算+規律行+温度 | 小(0.5〜1日。既定 OFF トグル+finals ON の流儀) | plan 予算増は plan 呼(約3.5%)のみ・+448tok 分の KV。他はゼロ | ゴールデン=トグルで不変。A8 2ラン+縦煙 | 低(プロンプト差のみ・呼数/乱数不変=R1 無傷) |
| P2 記憶要約化+スレッド | 中(2〜4日。hear 経路・dialog_history・record_contact) | ゼロ(決定論・LLM 呼不変) | **中**: 記憶内容が変わる=挙動が動く。縦煙+A8+短い実LLM比較ラン | 中(記憶の情報量を落としすぎると別の劣化。要 A/B) |
| P3 内省の根拠引用 | 小〜中(1〜2日) | ゼロ | 中(k 作用点=R1 検討必須) | 中 |
| M1 14B tier(reflect/plan) | 極小(conf+起動スクリプト。モデル取得済み) | reflect/plan のみ 1.7倍遅(reflect 19s→約32s/呼。時間分散発火なので吸収可) | A8 1ラン | 低(RouterLLM/tiers 実装済み・キャッシュは name 別) |
| M2 Swallow-8B 置換 | 小(取得+A8)〜中(全サーバー入替) | ゼロ(同サイズ) | A8 必須(JSON 追従・no_think 挙動が RL で変わっていないか) | 中(新モデル検証を本選前に押し込む時間) |
| guided_json(plan のみ) | 小(vllm.py に structured_outputs 1経路+conf ノブ=constrained-decoding.md の設計) | 数%(xgrammar キャッシュ後)+初回0.1〜0.3s | **本選機での Qwen3 組み合わせスモーク必須**(§5.4) | 中(バージョン依存の地雷。§5.5 の順序を守れば低) |
| (参考)32B-AWQ 全面/tier | 中 | 全面=約3.4倍遅+KV 2GB で並列崩壊=**非推奨**。tier 限定でも 14B より税が重い | 大 | 高 |

---

## 8. A8 ミニトーナメントを「判定装置」として使う手順

`scripts/behavior_tournament.py`(実装済み・判定はしない=数字を並べるだけ)を、モデル比較だけでなく**プロンプト再設計の検収装置**としても使う。

### 8.1 ハーネスの性質(実装確認済み)

- シナリオ束は **mock シムの実ジャーナルから採る**(合成プロンプトを書かない)= `build_prompt` が組んだ現物を purpose別×時刻帯6区分でラウンドロビン間引き。`--set` で conf 上書き可・`--profile` / `--env` 指定可・決定論(同 seed 同 conf なら同じ束)。
- 発行は既存 `VllmBackend` + `generate_many(workers=N)`・request seed は `stable_request_seed`(A/B 同一シナリオに同一 seed)。
- 採点は機械指標のみ: JSON パース成功率 / `parse_action` 成功率 / `classify_reject` 内訳 / 空応答率 / 応答長分布 / 行動分布の Jensen–Shannon 距離 / レイテンシ p50・p95(すべて purpose 別)。出力 `runs/tournament_<name>/report.md` + `samples.md`(人手確認用 prompt/response 対)。
- `--endpoint-b` は省略可(A 片側のみのラン=ベースライン計測に使える)。

### 8.2 用途1: モデル比較(8B vs 14B)— 実装どおり

```powershell
# 1) 束を作る(GPU不要・mock)— finals 相当の conf で
python scripts/behavior_tournament.py --name a8 --build-only `
    --profile conf/finals_observe.yaml --per-purpose 100

# 2) 同じ束を 2 モデルへ(14B は空き port に別プロセスで起動しておく)
python scripts/behavior_tournament.py --name a8 `
    --endpoint-a http://localhost:8001 --model-a Qwen/Qwen3-8B-AWQ `
    --endpoint-b http://localhost:8006 --model-b Qwen/Qwen3-14B-AWQ `
    --per-purpose 100 --workers 16
```

見る線(判定はユーザー): plan の parse 率差・reflect の応答長分布(上限張り付きの解消)・deliberate の応答長と行動分布 JS 距離(「短く浅い」が動くか)・レイテンシ p95(スループット税)。

### 8.3 用途2: プロンプト再設計の A/B — 束を2つ作って同一モデルへ

ハーネスは「1束×2モデル」を比べる作りなので、プロンプト比較は**「2束×同一モデル」を2ランで**行い report.md を並べる:

```powershell
# 束A: 現行。束B: 再設計(conf トグル or コード変更後に --rebuild-src)
python scripts/behavior_tournament.py --name pr_base --build-only --profile conf/finals_observe.yaml
#(P1 実装後)
python scripts/behavior_tournament.py --name pr_p1  --build-only --profile conf/finals_observe.yaml

# 同一 endpoint へ片側ランを2本(seed 同一)
python scripts/behavior_tournament.py --name pr_base --endpoint-a http://localhost:8001 --model-a Qwen/Qwen3-8B-AWQ
python scripts/behavior_tournament.py --name pr_p1  --endpoint-a http://localhost:8001 --model-a Qwen/Qwen3-8B-AWQ
```

注意: 束が違うのでシナリオは1対1対応しない(同 seed でも発火列が変わりうる)。**purpose 別の分布比較**(parse率・応答長・行動分布・reject 内訳)として読む。1対1で比べたい場合は、束Aのプロンプトに決定論の後処理変換(例: 記憶行の切り詰め)を掛けた束A'を作る小スクリプトを足すのが最小(ハーネスは scenarios.jsonl を `--scenarios` で受け取れる=**変換済み jsonl を渡すだけで実装追加ゼロ**)。

### 8.4 用途3: 「内容の質」の採点を足す(機械指標の限界の補完)

現行採点は形式指標のみで「支離滅裂さ」自体は測れない。最小の追加(ハーネス外の後処理・results.parquet を読む):

1. **文脈整合スコア(決定論)**: 応答内の固有名詞(人名・店名)がプロンプトの「近くにいる人/場所/周りにある店」に含まれる率。プロンプト外の名詞の唐突登場率。
2. **反復率**: 同一 agent の応答間の n-gram 重複(「さっきと同じ話題を繰り返さない」の実効測定)。
3. **LLM 審判(任意・別モデル)**: samples.md の対を大モデル(または API)で1〜5点採点。A8 設計の「機械指標のみ」の流儀を破るので、使うなら**判定でなく参考欄**として report に併記。

---

## 9. 推奨

**中心命題: 「支離滅裂さ」はモデル起因が半分・入力起因が半分で、費用対効果は入力側(P1→P2)が圧倒的に高い。** 根拠: (i) deliberate は parse 100% なのに内容が浅い=形式でなく文脈の問題、(ii) 87% のプロンプトが壊れた逐語記憶を再注入している実測(§1.2)、(iii) plan 67% 壊れは予算切断で説明でき 32B でも直らない(§4.3・§5.5)、(iv) 参照実装(GA/ai-town/AgentSociety)は**もっと小さい文脈でも一貫した対話**を、要約化・スレッド化・purpose 別プロンプトで達成している(§2)。

段階案(すべて ask-before-extending: 実装着手はユーザー承認後):

1. **即日(本選前・低リスク)**: P1(purpose別ヘッダ・plan 予算右サイズ・規律3行・温度分化)+ finish_reason 計数。全て既定 OFF トグル+finals ON の既存流儀で R1・ゴールデン無傷。
2. **同時に A8 を判定装置に**(§8): 束2種(現行/P1)×モデル2種(8B/14B)の4セルを1晩で。判定線の例: plan parse 率(P1 で 33%→90% 台に乗るか)・reflect 応答長分布(768 張り付き解消)・deliberate 応答長と行動分布 JS 距離。
3. **数字が出たら**: M1(14B を reflect/plan tier へ・conf 1行)。14B が P1 束で優位を示せばそのまま本選投入(RouterLLM 実装済み)。
4. **本選リハーサル窓 or 本選後**: P2(記憶の要約化=増幅ループ遮断・会話スレッド化+engaged ON)。発話品質の本丸だが記憶内容が変わるため検収が重い。Swallow-8B-RL-AWQ の取得と A8 も この窓で(発話 92.7% に効く唯一のモデル手)。
5. **plan の guided_json(xgrammar)**は §5.5 の順序(予算→計数→スモーク→A/B)を守って導入。切断が消えた後の残存壊れ(モデル非適合分 約10-20%)を 96-100% へ押し上げる仕上げ。

**やらないこと**: 32B-AWQ の全面投入(KV 2GB で並列崩壊・§4.2)、2段生成(呼数2倍・§5.5)、27B 世代(AWQ 21GB で単機不可・§4.1)、few-shot 例の追加(参照実装に前例なし・§2.2-(7))。
