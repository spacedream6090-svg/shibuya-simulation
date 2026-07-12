# 旧・渋谷シミュレーション実装レビュー — 移植候補の棚卸し(2026-07-12)

> 依頼(ユーザー): 別の機会に作った旧・渋谷シミュレーション(`shibuya-sim/`)に一度目を通し、
> **現在の実装に活かせそうな部分を「実装案」としてまとめる**。実装はまだしない。
> 作成: Opus 4.8(レビュー専任・コード変更なし)。原資料: `shibuya-sim/`(64ファイル・494KB)全読 +
> 現行 `src/society/**`・`scripts/**`・`docs/log/devlog*.md` の対応箇所照合。
> 制約遵守: 本書は `docs/research/` に新規作成のみ。`shibuya-sim/` および現行 `src/`・`conf/`・`tests/` は不変。

---

## 0. 位置関係(前提の明確化)

- **旧実装** = `<repo親>/shibuya-sim/`(config/・main.py・visualization/ 構成の MVP)。
- **現行実装** = 本リポジトリ(`src/society/**`・conf/・tests/・docs/)。本書はこちらの `docs/research/` に置く。

旧実装は「動く MVP をひとまず立てる」段階の設計で、現行は決定論・R1(k非依存の呼数不変)・
現実較正・LOD・570本規模テストを備えた研究基盤。**規模も成熟度も現行が全面的に上位**。
したがって本レビューの目的は「旧の丸ごと移植」ではなく、**現行に無い/現行が学べる少数の粒**を
貪欲になりすぎず選別することにある。

---

## 1. 旧実装の全体像

### アーキテクチャ

単一プロセス・同期ステップの MVP。1 step=10分、06:00–22:00 の 96 step、200体規模を想定。
毎 step **全エージェントが LLM を1回ずつ呼ぶ**(LOD なし)。各エージェントは JSON で
`action(move/stay) / target_poi / message / internet_post / current_goal / memory` を返す。
移動は「目標POIへ直線を最大300m/step で近づく」(**道なり経路なし=テレポート的直線**)。

```
main.py ─ CLI(--steps/--seed/--condition/--internet/--no-internet)
src/simulation.py ─ メインループ(プロンプト構築・decision適用・SNS投稿・ログ書き出し)
  ├ agent.py            Agent dataclass(位置・記憶・関係・needs・4層ペルソナ属性)
  ├ conversation_prob.py 5層の会話開始確率(近接者リストのソフトフィルタ)
  ├ needs.py            7ニーズ×2層の副作用更新 + 和文レンダリング
  ├ timeline.py         時刻⇄step変換・2h環境バケット(天気/気温/ニュース)・時刻イベント
  ├ geo.py              haversine・step_toward・GeoJSON POIローダ
  └ llm_client.py       OpenAI/Ollama 統一クライアント(単一プロバイダのみ)
scripts/ ─ オフライン系(pool生成・warmup・emergence検出・集計・コスト試算・人口統計検証)
config/ ─ YAML群(config/conversation/demographics/archetypes/environment/events/personas)
visualization/build_viewer.py ─ run→単体HTML(スライダー・地図・SNSアーク・距離ヒスト)
```

### 設計思想(旧が明示的に持っていた良い点)

- **対照群 A/B が第一級**: `A_physical_only`(SNS無し)/ `B_physical_internet`(SNS有り)を config で切替。
  `--internet/--no-internet` で直接指定。同一 seed でペアにして「SNS層の有無」を独立変数にする実験設計。
- **SNS層の空間性**: SNS返信/引用のたびに「返信者と親投稿者の**物理距離**」を計算してエッジに記録
  (`simulation.py:880-922`)。=「SNSが物理的にどれだけ離れた人をつないだか」を測る観測を最初から埋め込んでいる。
- **創発の副次指標を後付け検出**: `detect_emergence.py` が架空POI・集合的注目・規範発話をテキストから拾う。
- **関係網の事前ウォームアップ**: 本番前に LLM で初対面会話をさせ、非対称な初期関係を作る(現行の icebreak の原型)。
- **予算ガード**: `estimate_cost.py` + `budget_hard_limit_usd` でクラウドLLMの費用を事前試算。
- **人口の「流動人口」フレーミング**: 居住者ではなく駅前昼間人口(居住+通勤+学生+観光)を出典付きで手符号化。

いずれも現行と思想は連続しており、旧は現行の思想的プロトタイプと読める(実際 devlog にも
icebreak・A/B・emergence・IPFペルソナの系譜が残る)。

---

## 2. モジュール別比較表

| 旧モジュール(ファイル) | 現行の対応物 | 判定 | 一言 |
|---|---|---|---|
| `scripts/detect_emergence.py` | 現行に相当機能なし(measure.py は定量: cascade/drift/community/EWS/R²) | **A** | 架空POI・規範発話・語の共伝播をテキストから拾う後付け検出器。読み取り専用で無リスク。**本命** |
| `src/simulation.py` の SNS距離ブリッジ(`:880-922`)+ `aggregate_runs.py` の near/far エッジ(`:120-123`) | transmission ログは `{item_id,from,channel}` のみで**返信時の両者物理距離を持たない**(schema.py:29 で確認) | **B** | 「SNSが何m離れた人をつないだか」の空間×社会観測。現行の観測層に None安全で足せる。**本命** |
| `scripts/generate_pool.py` の depth fields(`contradiction`/`past_setback` 等, `:125-167`) | `gen_personas.py`/`persona.py`(IPF×e-Stat+Verbalized Sampling) | **B** | 生成機構は現行(IPF)が上位。ただし「自覚した矛盾・過去の小さな傷」等の**深さ属性**は学べる。**本命** |
| `src/conversation_prob.py`(5層会話開始確率) | `cognition/drive.py`(欲求ゲージ発火)+ 対面=確定発火・返答保証 | **B** | 現行の発火機構が上位だが、**「誰に話すか」を関係×文脈で決定論的に重み付け**する発想は現行に無い |
| `scripts/warmup_relationships.py`(二者独立の記憶ジャッジ) | `scripts/build_icebreak.py`(ペア会話+valence) | **B** | icebreak は既存。ただし**両者が独立に remembered/warmth/共通点を判定=非対称関係**の生成は学べる |
| `scripts/estimate_cost.py`(USDコスト試算) | 相当なし(bench.py は mock の壁時計/メモリ計測) | **A** | 現行に**費用/計算量の事前見積り**が無い。ただしローカル運用中心で優先度は低い |
| `src/simulation.py` の smartphone_use 傾向(`:78-128`) | `net/internet.py`(SNS)+ drive.py の `sns` 重み 0.08 | **B** | ペルソナ由来の**SNS利用傾向(heavy/light)を記述文脈として提示**する異質化は軽量で学べる |
| `src/needs.py`(7ニーズ×2層 副作用) | `needs.py`(感度倍率)+ `health.py` + `inner_life.py` + drive.py + 食事行動 | **C** | 現行が分解・高度化。ただし**POI種別→ニーズ充足デルタ表**は affordance 参照物として一見の価値 |
| `config/demographics_shibuya.yaml` + `fetch_demographics.py` | IPF×e-Stat(`gen_personas.py`)+ `shibuya-inflow.md`/`shibuya-population.json` | **C** | 機構は IPF が上位。**出典付き marginal + 年齢×職業の下限年齢表**は IPF目標値の検算用参照 |
| `src/timeline.py`(時刻/環境バケット/イベント) | `world/clock.py`・`calendar.py`・`weather.py`・`scenario.py`・`annual.py` | **C** | 現行が全面上位(stream天気・季節バイアス・摂動カタログ) |
| `src/geo.py`(haversine/直線移動/POIローダ) | `world/geom.py`・`map.py`・`routing.py`(A*/Dijkstra・道なり) | **C** | 現行は道なり連続移動。旧は直線テレポート=退行 |
| `src/llm_client.py`(OpenAI/Ollama) | `llm/*`(base/ollama/vllm/mock/cache/fleet) | **C** | 現行はキャッシュ・艦隊・mock を持ち上位 |
| `src/agent.py`(Agent dataclass) | `agents/agent.py`(+memory/persona/validate) | **C** | 現行が上位 |
| `scripts/aggregate_runs.py` の A/B 平均比較表 | `run_experiment.py`・`analyze_sweep.py`(k掃引・contrast) | **C** | A/B対照は現行の実験ツールで充足(距離ブリッジ指標のみ上表 B で分離) |
| `visualization/build_viewer.py` | `viz/`(viewer.html+dashboard.html+3D) | **C** | 現行が桁違いに高機能 |
| `scripts/build_personas_index.py`/`fetch_pois.py`/`run_metrics.py`/`summarize_run.py` | 現行 scripts 群(observe.py 等) | **C** | 現行に同等以上あり |

---

## 3. A/B 候補の詳細(移植案)

各案の形式: **旧該当箇所** | **何をするか** | **現行への組込み方(制約遵守の設計スケッチ)** | **工数** | **優先度の私見**。
現行の制約 = 決定論(新規RNG stream を増やさない or 専用stream)・R1(free==off の LLM呼数不変)・
no-fingerprint(因子名をプロンプトに出さない)・既定OFF(OFF=ゴールデンbyte一致)・L1正準スキーマ尊重。

---

### 【A-1・本命①】創発の後付けテキスト検出(架空・規範・共伝播)

- **旧該当**: `scripts/detect_emergence.py`
  - L1 架空(`:85-133`): 発話/投稿中の固有名詞候補(カタカナ2+/「」引用/大文字ASCII)を抽出し、
    実在POI名と**曖昧一致しないもの**を「架空の場所・モノ候補」として列挙(SequenceMatcher 0.7閾値)。
  - L1 集合的注目(`:148-180`): ある語が **window(既定3step)内に ≥2 の別エージェント**で使われたら
    「注目が収束した語」として記録(語ごと1件)。
  - L3 規範発話(`:183-213`): 正規表現で「〜べき/してはいけない/〜が普通・当たり前/should/must/everyone…」を検出。
- **何をするか**: 既存ログのテキストだけを読む**完全に読み取り専用のオフライン分析**。既存の定量パイプ
  (vocab_coin/transmission/cascade)が捉えない「**言語としての創発の質**」— とくに①エージェントが
  実在しない場所・モノを口にする(虚構の析出=world-change の芽)②規範言明の出現(制度・規範創発と直結)③
  複数人での語の同時期共有 — を可視化する。
- **現行への組込み**: 新規スクリプト `scripts/detect_emergence.py`(仮)として追加。
  - 入力は `measure.load_events()` で `l1_events.parquet` を読み、`kind in {speak, sns_post, dm}` の
    `payload.text` を対象にする(旧の events.jsonl/internet_messages.jsonl 直読を現行 L1 に置換)。
  - 実在POI名は `data/shibuya_osm*.json` / `poi_patch_shibuya.json` の名称集合から作る。
  - **決定論/R1/ゴールデン**: シミュ本体・observer に一切触れないので**全制約に完全非抵触**
    (RNG不使用・LLM不使用・L1不変)。純粋な後段解析。
  - 日本語向けに正規表現を微調整(旧は日英混在の素朴パターン。「〜すべき/〜してはいけない/〜が当たり前」等)。
    形態素解析は入れず stdlib のみで保守的にすれば依存も増えない。
  - 望ましくは `judge.py`(LLM-judge, κ検証)への橋渡しとして、この検出器の hit を**judge の入力候補**にする。
- **工数**: 半日〜1日(旧コードをほぼそのまま現行 L1 ローダに繋ぐだけ。日本語パターン調整が主)。
- **優先度**: **高**。研究の主題(規範・制度・虚構の創発=world-changer)に最も直結し、リスクが実質ゼロ。
  現行の定量指標(採用数/カスケード)は「語が広がったか」を測るが、「**どんな種類の**発話が現れたか」を
  測る器が欠けている。その穴をちょうど埋める。

---

### 【B-1・本命②】SNSが架橋した物理距離(空間×社会の観測)

- **旧該当**: `src/simulation.py:880-922`(返信/引用ごとに author と親author の haversine 距離・same_poi・
  near(≤10m)を算出しエッジに記録)+ `scripts/aggregate_runs.py:120-123`(near/far エッジ分類・
  平均/最大距離)+ `:84-90`(相互(双方向)ペア検出)。
- **何をするか**: SNSの返信/引用が起きた瞬間の**両当事者の物理距離**を記録し、「近接(すぐ隣)での SNS」と
  「遠隔を跨いだ SNS」を分離する。=「インターネット層が物理的隔たりをどれだけ越えて相互作用を生んだか」を
  定量化する。A/B(SNS有無)対照の**被説明変数として非常に筋が良い**(SNS層の存在意義そのものを測る)。
- **現行への組込み**:
  - 現行 `transmission` イベントは `{item_id, from, channel}` のみ(`observer/schema.py:29` で確認)で、
    **返信時点の from/to の座標・距離を持たない**。ここに **None安全な追加フィールド**を入れる。
  - 設計: `channel in {sns, dm}` の transmission を記録する箇所(net/internet.py の送出時)で、
    送り手と受け手の現在座標が既知なら `payload` に `dist_m`(と `near` フラグ)を**任意キーで**足す。
    座標が取れない経路(media/news 起点=from が -1)は付けない=既存出力不変。
  - 観測側は `observer/aggregate.py` に `@register_aggregator` で `sns_far_frac` 等を1関数追加、
    または後付けの measure 関数(`sns_bridge_stats(events)`)として実装。**None安全・欠損は0**の作法で
    OFF/既存ランでは列が増えないようにすればゴールデン不変。
  - **決定論/R1**: 距離計算は既存座標の純関数=乱数不使用・LLM不使用。呼数不変。
  - 併せて旧の**双方向(相互会話)ペア指標**(`aggregate_runs.py:53-90`: 互いに earshot 内で発話した対)も
    measure に足すと、`network_windows`(次数/クラスタ)を補完する「関係が相互化したか」の軽い指標になる。
- **工数**: 1日程度(送出箇所での距離付与 + measure/aggregate 関数 + テスト1〜2本)。距離の付与位置が
  net/internet.py の内部にあるため、そこだけ現行コード確認が要る(本書はロジック未確認=要精査)。
- **優先度**: **中〜高**。SNS層(condition B)の効果を直接測る指標で、A/B設計と噛み合う。実装は局所的。

---

### 【B-2・本命③】ペルソナの「深さ属性」(矛盾・過去の傷)

- **旧該当**: `scripts/generate_pool.py:125-167`(ENRICH_PROMPT)。骨格(年齢/性/職業/出身/Big5)に加え、
  LLM に **`contradiction`(自覚した内的矛盾)・`past_setback`(過去の小さな挫折/コンプレックス)**、および
  6つの文体軸(`attitude`/`speech_register`/`money_sense`/`social_density`/`place_criteria`/`time_pace`)を
  生成させ、`Agent` に載せてプロンプトへ提示(`shibuya-sim/src/simulation.py:315-335` の deep_section)。
- **何をするか**: 人物に「平板なアーキタイプ」ではなく**テクスチャと矛盾**を与える。世界改変者(keystone)が
  誰から立ち上がるかは動機の質に依存しうるため、動機の**深さ**を持たせる意義がある。
- **現行への組込み**:
  - 現行は IPF×e-Stat の**統計整合**を優先し、`agents/persona.py`+`gen_personas.py` でペルソナ文を生成。
    ここへ **contradiction/past_setback 相当の1〜2文**を Verbalized Sampling プロンプトに**追加項目**として
    織り込む(生成機構は現行のまま。旧のアーキタイプ加重割当は採らない=IPF と非整合)。
  - 生成物は**決定論キャッシュ化された名簿(`data/personas_*.json`)**に入る静的資産なので、
    シミュ本体の決定論・R1・ゴールデンには非抵触(名簿を差し替えるだけ)。既存名簿はそのまま、
    新規プロファイルにだけ深さ属性を持たせれば後方互換。
  - no-fingerprint: これは**ペルソナ文(観測可能な人物像)**であって因子(nfc等の指紋)ではないので、
    プロンプト提示は問題なし(現行が bio/persona を出しているのと同格)。
- **工数**: 半日(生成プロンプトへ項目追加 + 1名簿の再生成 + 目視レビュー)。
- **優先度**: **中**。研究の被説明変数(誰が改変者になるか)に効きうる。ただし効果は実証待ちで、
  「まず detect_emergence と距離指標で観測を厚くしてから」でも遅くない。

---

### 【B-3】会話の「相手選び」を関係×文脈で決定論的に重み付け

- **旧該当**: `src/conversation_prob.py:83-131`(`conversation_probability`)。
  L1 関係クラス(stranger…best_friend)→ L2 トリガ加算(共通興味/共通職/共通話題/視覚手がかり)→
  L3 外向性の乗算倍率 → L4 文脈減衰(静かなPOIで低下・深夜低下・空腹/疲労で低下)→ 孤独/退屈で微増 → cap 0.92。
  近接者リストの**ソフトフィルタ**(`VISIBLE_THRESHOLD`未満は「気づいてすらいない」)として使う。
- **何をするか**: 「近くにいる誰に話しかける気になるか」を、関係の深さ・共通点・場の性質・時刻・体調で連続変調する。
- **現行との差**: 現行は `cognition/drive.py` の**欲求ゲージ発火**(出来事→ゲージ→個人閾値→重み抽選)で
  「話すか否か」を決め、対面は確定発火・返答保証。発火機構としては現行が明確に上位(R1のため入力を
  観測可能な出来事に限定=k非依存を保証)。一方で**「発火した後、同席者の誰を宛先にするか」を
  関係・場・共通点で構造的に重み付けする層は現行に無い**(relations.py は tier を持つがプロンプト文脈止まりで、
  宛先選択のスコアには使っていない)。
- **現行への組込み(R1安全な形に限定)**:
  - **確率ゲート化はしない**(発火可否に確率を足すと LLM呼数が seed×k で動き R1 を壊す)。代わりに、
    発火は現行のまま維持し、**hearer のランキング/宛先の優先度**として旧5層の**決定論スコア**を使う。
  - スコア入力 = 関係 tier(`relations.tier_of`)+ 共通興味/職(ペルソナ由来)+ POI静粛度(map)+
    時刻(clock)+ needs 感度。**すべて既存の決定論量**で、乱数を引かず belief/k を見ない=R1・決定論不変。
  - `social_lines`(relations.py:188)が既に「間柄行」を作っているので、そこに**宛先優先度の並べ替え**を
    足すのが最小侵襲。既定OFF(スコア未使用=現行の並び)にすればゴールデン不変。
- **工数**: 1〜2日(スコア関数の移植 + 宛先選択への配線 + free==off 呼数一致の smoke)。R1 を壊さない
  設計確認に神経を使う。
- **優先度**: **中〜低**。会話の質を上げうるが、現行の発火機構と丁寧に棲み分ける必要があり、
  リスク/効果比は上の3本より劣る。「会話が均質・定型」という既知課題(sim-improvement-analysis.md P3)への
  補助にはなりうる。

---

### 【B-4】icebreak の非対称化(両者独立の記憶ジャッジ)

- **旧該当**: `scripts/warmup_relationships.py:160-203`。ペア会話後に**両当事者が独立に** JUDGE_PROMPT で
  `remembered(bool)/warmth/common_topics/first_impression` を判定(`:122-141`)。=「A は B を覚えているが
  B は A を忘れた」という**非対称な初期関係**が自然に生じる(内向的/無関心な人は忘れやすい、と明示教示)。
- **現行との差**: 現行 `build_icebreak.py` は類似+ランダムのペアリングと会話生成までは同型だが、出力は
  ペア単位の `valence`(対称・1値)のみ。**方向別の記憶/親密度シードは持たない**。
- **現行への組込み**:
  - `build_icebreak.py` の会話後に、両者それぞれの視点で**軽い判定**(mock時は valence から近似、実LLM時は
    1〜2呼の判定)を足し、`pairs[*]` に `a_view/b_view`(remembered・closeness シード)を追加。
  - シミュ側は起動時に icebreak を読み `agents/memory.record_contact` の **closeness_delta 初期値**として
    方向別に流し込む(relations.py の tier 導出が非対称に走る)。既定は現行の対称挙動を維持(新フィールドが
    無ければ従来通り)=ゴールデン/決定論不変。オフライン生成物なのでシミュ本体の R1 には非抵触。
- **工数**: 半日〜1日(生成側の判定追加 + 読込側の方向別シード)。
- **優先度**: **低〜中**。関係網の初期リアリティは上がるが、現行の icebreak+relations で概ね足りており、
  「非対称性が研究結果に効く」証拠が出てからでも良い。

---

### 【A-2】LLMコスト/計算量の事前見積り

- **旧該当**: `scripts/estimate_cost.py`。`calls = steps×agents`、per-call トークン概算、プロバイダ別 USD
  単価表(`:20-37`)から run/実験の費用を出し、`budget_hard_limit_usd` と比較して OVER 警告。
- **何をするか**: 大規模ラン前の**予算/計算量ガード**。
- **現行への組込み**:
  - 現行は LOD で `calls = steps×agents×発火率(実測 4〜11%)`(devlog E10)なので、旧の `steps×agents` は
    過大。**発火率とキャッシュヒット率を掛けた現行式**に置き換える必要がある。
  - ローカル(Ollama/vLLM)運用なら USD より **GPU時間/step壁時計**が実務指標。`bench.py`(scaling bench)が
    既に step 壁時計と呼数を出すので、それに**「本番 N×日数 への外挿」+ 任意でクラウド単価**を足すのが自然。
  - 純オフライン計算で制約に非抵触。単価表は 2026 初頭時点で陳腐化しているため要更新。
- **工数**: 半日。ただし現行 `bench.py` の拡張として書くのが筋。
- **優先度**: **低**。finals のクラウド/艦隊計画時にあると便利という程度。研究本体には寄与しない。

---

## 4. 採用不要(C)の理由 — 貪欲に拾わないための明示

将来同じ問いを繰り返さないため、C 判定の根拠を正直に残す。

- **`src/needs.py`(7ニーズ×2層 副作用)**: 現行は `needs.py`(価値プロファイル由来の感度倍率)+
  `health.py`(疲労/病気/メンタル)+ `inner_life.py`(離散感情/長期目標/趣味)+ drive.py ゲージ + 食事行動へ
  **分解・高度化済み**。旧の単一テーブル(空腹→restaurant で減る等)は現行の重複・退行。
  *ただし* `needs.py:35-63` の **POI種別→ニーズ充足デルタ表**は「どのアフォーダンスがどの欲求を満たすか」の
  コンパクトな一覧として、現行の食事/休憩行動を調律する際の**参照値**にはなる(移植ではなく参照)。
- **`config/demographics_shibuya.yaml` + `fetch_demographics.py`**: 現行は **IPF×e-Stat** で周辺分布に整合した
  ペルソナを生成(統計的により正しい)。旧の手符号化 marginal は機構として下位。*ただし* この YAML の
  **出典注記([R]国勢調査/[C]通勤流動/[T]観光/[S]区統計)と年齢×職業の下限/上限年齢ルール**は、
  現行 IPF の**目標周辺分布を検算する参照表**として一見の価値がある(`shibuya-inflow.md` と突合可能)。
- **`src/timeline.py`**: 現行 `world/clock.py`・`calendar.py`・`weather.py`(stream決定論天気・季節バイアス)・
  `scenario.py`(摂動カタログ)・`annual.py`(年中行事)が全面上位。2h環境バケットは粗く、現行の連続時計に非整合。
- **`src/geo.py`**: 旧は「目標へ直線を近づく」テレポート的移動。現行は OSM 実地図上の A*/Dijkstra 道なり連続移動
  (`world/routing.py`・`map.py`・`geom.py`)。移植は**明確な退行**。
- **`src/llm_client.py`**: 現行 `llm/*` はキャッシュ(再現性)・vLLM 艦隊・mock・fleet を備え上位。
- **`src/agent.py` / `main.py` / `simulation.py`(ループ本体)**: 現行 engine(scheduler/simulation/checkpoint)が
  LOD・phase 分割・決定論・resume を備え全面上位。旧ループは LOD 無しで全員毎step LLM=現行のスケール方針と非互換。
- **`scripts/aggregate_runs.py` の A/B 平均比較表**: A/B(k)対照は現行の `run_experiment.py`・`analyze_sweep.py`
  (掃引・contrast・finite-size scaling)で充足。**距離ブリッジ指標だけ**を B-1 として分離採用すればよく、
  集計表そのものの移植は不要。
- **`visualization/build_viewer.py`**: 現行 `viz/`(viewer+dashboard+3D、8.4MB 軽量化済み)が桁違いに高機能。
- **`scripts/build_personas_index.py` / `fetch_pois.py` / `run_metrics.py` / `summarize_run.py` /
  `test_llm.py` / `debug_one_call.py`**: 現行 scripts 群(`build_map.py`/`observe.py`/`gen_personas.py` 等)に
  同等以上があり、旧は MVP 用の素朴版。

---

## 5. まとめ(候補数・本命)

- **A/B 候補 = 6 件**(A: 2、B: 4)。**C(採用不要)= 11 系統**を §4 に明示。
- **本命トップ3**:
  1. **A-1 創発の後付けテキスト検出**(`detect_emergence.py`)— 架空POI・**規範発話**・語の共伝播を既存ログから拾う。
     読み取り専用で決定論/R1/ゴールデンに完全非抵触。研究主題(規範・制度・虚構の創発)に最も直結。**最優先**。
  2. **B-1 SNSが架橋した物理距離**(`simulation.py:880-922` + `aggregate_runs.py`)— 返信時の両者物理距離を
     transmission に None安全で付与し、near/far を分離。A/B(SNS有無)対照の被説明変数として筋が良い。
  3. **B-2 ペルソナの深さ属性**(`generate_pool.py` の contradiction/past_setback)— IPF生成を保ちつつ
     動機のテクスチャを足す。名簿は静的資産なのでシミュ本体の制約に非抵触。

- **判断の要旨**: 旧実装は現行の思想的プロトタイプで、コアは現行が全面上位。移植価値があるのは
  **現行が「まだ観測していない切り口」**(規範/虚構のテキスト創発・SNSの空間架橋)と、**軽量なペルソナ深化**に絞られる。
  いずれも「観測を厚くする/静的資産を差し替える」層に閉じており、**決定論・R1・既定OFF・L1正準を一切壊さずに**
  足せるのが共通の利点。会話の相手選び(B-3)と icebreak 非対称化(B-4)、コスト試算(A-2)は
  「効果が実証されてから」で十分な後回し候補。
