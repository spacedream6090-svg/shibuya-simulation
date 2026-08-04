# LLM⇄世界インターフェース監査 — 外部相談4IF案 × 6問チェックリストのコード実診断

> 2026-08-05。ユーザーが外部チャット(Claude)に相談した「エージェントの思考・行為を世界に具現化するインターフェース」設計案
> (①行為API ②観測パケット ③世界側書き込み先 ④観測者IF)と、その6問チェックリストを、実コードに突き合わせた診断。
> **実装は保留**(ユーザー指示)。診断は Explore×2 並行(行為経路系/世界状態・観測ループ系)・file:line 証拠付き。

---

## 0. 総括(3行)

1. チャット案の核心原則「**LLMは世界を直接触らない。行為は環境定義の有限語彙のみ**」は、本シムの**最初からの憲法**であり、①行為API・②観測パケット(LLMアダプタ層)は**ほぼ完全に実装済み**。
2. 薄いのはチャット側の予想どおり **③の情報オブジェクト(vocab のみ完全)と痕跡(個別3種のみ)**、**④の world_diff(無い)**。ただし「拒否が通知されない」のは欠落ではなく **no-fingerprint 規約による意図的設計**([envfeedback.py:60-62](../../src/society/envfeedback.py))。
3. 「情報オブジェクト」レーンはゼロから作る話ではない: `provenance.Item`(kind に rumor/institution を**宣言済み**)+ `truth_ledger`(fact/belief/親ノード=伝播木・既定OFF)という**既存2系統の統合・昇格**が正攻法。

---

## 1. 6問チェックリストへの回答

| # | 問い | 回答 |
|---|---|---|
| 1 | 環境変更は単一の行為API経由に限定? LLM出力の直接書き込みは? | **ほぼ Yes**。唯一のパーサ `parse_action`([deliberate.py:482](../../src/society/cognition/deliberate.py))→ 唯一のディスパッチャ `_apply`([scheduler.py:2666](../../src/society/engine/scheduler.py))の1本道。生テキストの直接書き込みは**ゼロ**。ただし構造化後の自由文フィールドが決定論変換器を通って世界に届く帯域が6本(§2-B) |
| 2 | 行為の有限語彙は定義済み? 前提条件・効果は? | **Yes**。`KNOWN_ACTIONS`(frozenset・[deliberate.py:431](../../src/society/cognition/deliberate.py))が唯一の源で、パーサとの同期を `test_undefined_action.py` が機械固定。約20動詞+ルール層専用9種+day_plan 列挙(act12/place15/purpose10/条件7/対処5/修復6)。前提条件チェックは裁定側(tools.py / truth_ledger.py / scheduler.py)に集中し、cognition 層は寛容受理 |
| 3 | 拒否パスは存在? エージェントへの通知は? | **3層存在**するが通知の強さが異なる(§2-C)。(a)パース失敗→ルール層後退・**無通知** (b)config ゲートの静かな無視・**無通知** (c)裁定拒否→**一部のみ**記憶に書かれ次のプロンプトに入る(出店却下/交際不成立/摘発)。所持金不足・空き住戸なし・経路なし・閉店は**無音**。day_plan の `plan_exception`→fire→engaged REPLAN 突入の骨組みは実装済みだが「何が失敗したか」は渡らない |
| 4 | 行為で変化する環境状態変数は? | §3 の開閉マトリクス参照。物理(混雑・遅延)・経済(実在庫・台帳)・社会(関係・評判・悪評)・情報(語彙 Item)・痕跡(貼り紙/出店/場所ラベル)が実装済み。ただし多くが**既定OFF or 観測非注入** |
| 5 | 変化は他者の観測に入る?(因果鎖が閉じる?) | **完全に閉じるのは5経路**: 語彙(ID付き Item+伝播記録=カスケード木再構成可)・発話テキスト・関係台帳(closeness/tier)・貼り紙・venture。物理・経済は「行動が黙って制約される」**半閉**(候補から静かに消える・移動が止まる) |
| 6 | world_diff は記録? 世界変化→原因行為へ遡れる? | **world_diff は無い**(L1 の189イベント種に差分種なし)。部分差分は `state_update{name,old,new,cause}`([factors/update.py:61-77](../../src/society/factors/update.py))と `env_feedback` のみ。**行為イベントに `llm_call_id` が無い**(フィールド自体は [observer/schema.py:390](../../src/society/observer/schema.py) に存在・思考系のみ付与)。llm_journal にプロンプト+応答全文があり `(step, agent_id)` join で思考まで遡れるが、同 step 複数発火で曖昧 |

**チャット側の予想**「1〜3は部分的にあり、③の書き込み先(特に情報オブジェクトと痕跡)と④の world_diff が薄い」→ **大筋的中**。ズレは2点: (i) ①②は「部分的」ではなくかなり完全(fleet 差し替え=第88 MindRouter・プラセボ=第89 build_prompt 作用点も、チャット案の言う「アダプタ層の差し替え」として既に実現している)。(ii) 拒否通知の薄さは**できない**のではなく**しない**(実験条件がプロンプトから漏れない no-fingerprint 規約とのトレードオフ)。

---

## 2. 診断詳細A: 行為の経路(チャット案①に対応)

### 2-A. 単一の口

- LLM生出力を受ける関数は5つのみで、全て `_loads_lenient`(JSON寛容ロード)経由。パース→`KNOWN_ACTIONS` 写像→`_apply`(scheduler.py:2666、唯一の呼び出しは :4946、fire barrier で id 昇順正準化)。
- `_apply` から3サブディスパッチャ: ツール(Tools.apply)/生活P2(_apply_p2)/開放・検証行動(_apply_free_action / truth_ledger.apply_verify)。
- 未知 `type` は if-chain 素通しで**無音 no-op**(意図的設計・routine.py:658-660 が明記)。
- 制約デコードは2層: バックエンド側 `format:"json"`(ollama/vllm/openai_compat)+アプリ側の検証→物理検証→決定論修復→フォールバック(day_plan.py:58-70 が「文法しか保証しない」と明記)。

### 2-B. 実質的な"広い口" — 構造化後の自由文が世界に届く6帯域

| # | 自由文 | 決定論変換器 | 到達先 |
|---|---|---|---|
| 1 | speak/post/dm の text | 感情辞書(lang.sentiment) | 他者の states 差分・drive・opinion |
| 2 | 同上 | 無変換 | 聞き手の記憶・SNS本体・L1 payload |
| 3 | coin_label.word | 語彙正規化(12字以下等) | **世界に新語彙 Item を作る** |
| 4 | do.what | values.classify(キーワード辞書) | カテゴリ中央値価格で所持金減 |
| 5 | do.where | _free_dest(名前解決・決定論) | **実ノードへの route(物理移動)** |
| 6 | propose.rule | RuleBook.validate(4型ホワイトリスト) | **全員の実効価格・行き先係数**(最強の書き込み帯域) |

数値は全クランプ(hours_later 1..6・minutes 10..240・watch の expect は単位ドメイン+σクランプ)。

### 2-C. 拒否3層と通知

- **層(a) パース失敗** → L1 `fallback{parse_error}` → routine 後退。エージェント通知**なし**。
- **層(b) config ゲートの静かな無視** — パースは寛容受理し適用層で `return` のみ(open_actions OFF・P2各項目OFF・verify OFF・未知type)。「該当項目が OFF や解釈不能では静かに無視(=wander 相当)」(scheduler.py:2684)。**イベント0・記憶0**。
- **層(c) 裁定拒否** — 通知**あり**: 出店許可却下・破産直後出店・交際不成立・無許可摘発(agent.remember → 次プロンプトへ)。通知**なし**: 所持金不足出店・敷金不足転居・空き住戸なし・相手不在・経路が張れない(`len(path)<2: return` 無音)・改札規制(混雑係数のみ・envfeedback.py:505-514 が「新しい記憶文・欄・理由キーを足さない」と明記)。
- **day_plan**: 物理検証(no_place/closed/unreachable/overflow)→決定論修復→実行時再解決→`plan_block_drop`。破綻はプロンプト文脈に**一切入らない**(interstitial digest 対象表 `_ISL_ACT` に plan_* 系ゼロ)。唯一の間接経路= `note_plan_exception` → fire キュー前倒し → engaged REPLAN 突入(**「今すぐ考える」だけが起き、何が失敗したかは伝わらない**)。

### 2-D. LLM注入点は5サイト(+バッチ変種3)・残りは全部ルール層

deliberate(発話系)/朝計画/recall/夜内省/対照 null 呼び出し。全て llm_off ガード付き(`test_ablate.py` が LLM呼0でも世界完走を固定)。構造化会話 C2/C3・接客・検証裁定・day_plan 修復・engaged 状態機械は「LLM呼ゼロ」を docstring 明記。行為APIの外で LLM が書ける内部状態は3本のみ: belief 書き戻し(=k の作用チャネル)・自己モデル・watch 監視仕様(全てホワイトリスト検証付き)。

---

## 3. 診断詳細B: 世界側の書き込み先(チャット案③)— 開閉マトリクス

| カテゴリ | 世界状態が動く | 他者の観測に入る | ループ | 既定 |
|---|---|---|---|---|
| 混雑(現在地) | 派生量のみ(保持なし) | ✅ crowd_line / worldview 期待差分 | ✅ | ON(production) |
| 混雑(行き先候補) | poi_hold に保持 | ❌ 候補が黙って消える | △ | **OFF** |
| 駅遅延・入場規制 | ✅ sim._envfb | ❌ **明文で禁止**(no-fingerprint) | △ | **OFF** |
| 実在庫(店・(s,S)方策+配送) | ✅ sim._goods_stock | ❌ 品切れ時に本人の記憶1行のみ | △ | **OFF** |
| 卸在庫(B2B) | ✅ | ❌ | ❌ | **OFF** |
| 所持金 | ✅ | ✅ 自分のみ | ✅ | ON |
| org_ledger(売上・賃金) | ✅ 日次parquet | ❌ 誰も見ない | ❌ | ON(観測のみ) |
| venture(個人出店) | ✅ 売上累積 | ✅ 店主の記憶・SNS | ✅ | ON |
| closeness / tier | ✅ 会話ごと更新+日次減衰 | ✅ 「間柄:」行 | ✅ | ON |
| 評判(スカラー) | ✅ | ✅ 自分のみ閾値超1行 | △ | ON |
| 悪評(gossip・匿名タグ) | ✅ complex contagion 閾値2 | ❌ 相手選択・確率の変調のみ | △ | **OFF** |
| trust(信用) | ❌ **未実装**(observer 呼称のみ) | — | — | — |
| **語彙(coin_label)** | ✅ **ID付き Item+transmissions** | ✅ 「知っている言葉:」 | ✅ **完全** | ON |
| 発話テキスト | ✅ 記憶/対話履歴/返答権 | ✅ 生テキスト注入 | ✅ | ON |
| 信念(truth_ledger・fact/belief/親ノード) | ✅ **伝播木を事後構成可** | △ 行動として現れるのみ(canary で漏洩検査) | ✅ | **OFF** |
| 貼り紙(場所の痕跡) | ✅ node別・TTL1日・最大3枚 | ✅ 閲覧→記憶+語彙受領 | ✅ | ON |
| 場所の呼ばれ方(place_bind) | ✅ | ✅ 1行 | ✅ | **OFF** |
| 場所のイベント履歴 | ❌ L1 に座標付きで全部残るが**シム内から読む経路ゼロ** | ❌ | ❌ | — |

**観測パケット(チャット案②)の実体** = `build_prompt`([deliberate.py:116-385](../../src/society/cognition/deliberate.py))。時刻・場所・近隣POI名(最大3)・シーン記述・混雑質感・同席者・間柄・タイムライン・直前のやりとり・状況行(reply には相手の発話本文)等を注入。**入らないもの**: 営業中か(閉店は候補から静かに消えるだけ)・行き先の混雑・遅延・在庫・org_ledger 全数値・他人の所持金・真偽台帳。「毎tick数値処理・LLM渡しは engaged 時だけ・驚きスコアは無料」もチャット案の記述どおり第87で実装済み。

**経済会計の断絶(所見)**: `revenue_est = 日給×margin`(scheduler.py:450-452)で**客の spend と非接続**。会計保存が成り立つのは venture と B2B のみ。

---

## 4. 診断詳細C: 観測者インターフェース(チャット案④)

- **ある**: L1 イベント189種(step/座標/payload)・`llm_journal`(プロンプト+応答**全文**)・`l1b_llm.parquet`(llm_call_id/purpose/step/cached)・state_hash チェーン(第78・抜粋ハッシュ・片側判定)・llm_cache replay(ミス即例外)・checkpoint/resume(resume==straight バイト一致固定)・分析19本(伝播木・模倣連鎖・DiD・発火解析)。
- **ない**: world_diff(世界の物理量の逐次差分。goods はイベント時のみ・occupancy は記録すら残らない)。行為イベントの `llm_call_id`(思考系のみ付与→ 行為→思考の突合が (step,agent_id) join 依存)。「世界の変化→原因の行為→その思考」を一本で辿るツール。

---

## 5. 診断の副産物(実装の穴・修正候補)

1. **contingency がデッドデータ**: day_plan は if_then を最大3個 LLM に書かせ検証・格納するが(`plan["cont"]`)、**消費するコードが無い**(_sweep/_replan/plan_action のいずれも読まない)。
2. **`_apply` に plan/recall/reflect 分岐が無い**: deliberate 経路で LLM が `{"action":"plan"}` を返すと無音で消える(KNOWN_ACTIONS には含まれるため undefined_action にも落ちず、fallback にもカウントされない=観測の穴)。
3. 行為イベント `llm_call_id` 欠落(§4)。

---

## 6. 実装候補(優先順・全て未着手=ユーザー指示で実装保留)

| # | 内容 | 規模 | R1適合性 |
|---|---|---|---|
| IF-1 | **行為イベントへの llm_call_id 付与**(スキーマのフィールドは既存・付与箇所を行為系に広げるだけ) | 小 | 観測のみ=シム不変。golden は payload 差分が出るため既定OFFトグルで |
| IF-2 | **拒否通知の段階 conf 化**: 無音拒否(所持金不足・閉店・空き住戸・経路なし)に 無音/記憶1行/engaged 突入 の3水準+plan_exception に失敗理由を載せる | 小〜中 | 既定OFF。no-fingerprint とは「全実験条件で同一の通知規則」なら両立(条件間で差をつけない)。チャット案の「拒否が生む驚き→思考」の核心 |
| IF-3 | **情報オブジェクトの一般化**: Item.kind の rumor 枠(宣言済み)+truth_ledger の伝播木を統合し、噂・誘い・伝聞を ID 付きで追跡 | 中 | 新設でなく既存2系統の昇格。論点=発話→オブジェクト抽出を LLM 追加呼なしでやる方式(truth_ledger 流の部分文字列 or 構造化タグ) |
| IF-4 | **痕跡=場所イベント履歴の汎用機構**: 貼り紙の一般化として「場所の記憶」(後から来た者の観測に入る) | 中 | 観測入力が増える=創発に効く候補。既定OFF+アブレーション軸として設計 |
| IF-5 | **経済会計の接続**: revenue_est を客の spend 由来へ(venture/B2B と同じ会計保存を org へ) | 中 | 25万の経済リアリズム課題。by_org トグル配下 |

+ §5 の穴3件(contingency 消費・_apply 分岐・llm_call_id)は判断不要枠の修正候補。

---

*診断実施: 2026-08-05(Explore×2 並行・読み取り専用)。実装はユーザーの明示指示があるまで行わない。*
