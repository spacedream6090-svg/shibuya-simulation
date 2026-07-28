# 01 自チーム講評の精読と現行実装の解消状況(shibuya-sim → shibuya-simulation)

> 調査日: 2026-07-29 / 担当: Opus 5(調査サブエージェント)
> 一次資料:
> - 講評 [`ryukih/SD-Hackathon-Reviewer-2026May` `evaluations/20260511-1st-Hackathone-valuations/shibuya-sim_eval.md`](https://github.com/ryukih/SD-Hackathon-Reviewer-2026May)(2026-05-11・実施2回)
> - 検証 同 `shibuya-sim_eval_review.md`(2026-05-11)
> - 発表資料 同 `slides/04-2021_146-shibuya-sim.pdf`(11ページ・2026/05/07 進捗報告)
> - 評価対象リポジトリ [`spacedream6090-svg/shibuya-sim`](https://github.com/spacedream6090-svg/shibuya-sim)(created 2026-05-06 / 最終 push 2026-05-06T07:13:28Z / Python / 86KB)
> - 対照先 = 現行 `shibuya-simulation`(本リポジトリ・別実装)
>
> **註記**: 講評は Claude による自動採点。人間審査員の観点と一致する保証はない。
> 第2回(本選)が同一ルーブリックである保証もない(`README.md` の正直な註記参照)。

---

## ① 講評スコアと総評(引用)

### スコア

| カテゴリ | Run1 | Run2 | Run3 | 最終(平均) |
|---|---|---|---|---|
| A. 創発設計 | 9 | 9 | - | **9.0** |
| B. 世界設定 | 9 | 9 | - | **9.0** |
| C. 発展性 | 8 | 8 | - | **8.0** |
| D. 技術実装 | 9 | 9 | - | **9.0** |
| **合計** | 35 | 35 | - | **35.0 / 40** |

第1回総合 **4位**(35.0)。**唯一の 8 点台が C. 発展性**。

### 概要(講評冒頭・原文)

> 渋谷駅周辺 500m 四方を舞台に、06:00-22:00 の 16 時間を 10 分刻み 96step で進める都市流動シミュレーション。OpenStreetMap から取得した実 POI(店舗・施設約 100 件)を地理空間として配置し、200 体の LLM エージェント(gpt-4o-mini)を動作させる。(中略)SNS 層あり(condition B)／なし(condition A)の 2 条件 ×2 seed の対照実験設計を採用し、物理距離と情報伝搬の関係を計測する。

### 総評「優れている点」(原文・4項目)

> - 渋谷駅前という具体的実地に対し、OSM実POI＋citation付き人口分布＋12アーキタイプで世界を厳密に組み上げ、SNS有無のA/B対照群と複数seedで研究的に再現可能な実験設計を実現している
> - 7ニーズ×2層の副作用ルール、5層会話開始確率、関係性ウォームアップという3層の世界規則をエージェントの行動には直接介入させず「状態と環境」のみ提示することで、構造的に高い創発ポテンシャルを担保している
> - モジュール分離(src/ 7ファイル)と設定外部化(YAML 8種)が徹底され、`detect_emergence.py` の3指標(架空POI／集合的注目／規範発話)など創発検出パイプラインまで一貫している
> - LLM呼び出しの頑健性(format_json、tolerant parser、retry、フォールバック)、メモリ多層化(rolling/goal/relationships)、シード決定性、構造化JSONL+manifest出力など技術実装の完成度が高い

### 総評「改善点・提言」(原文・4項目 = P1〜P4 と呼ぶ)

> - **(P1)** README冒頭の「プロジェクト概要」プレースホルダを埋め、研究問いと対照群A/B設計、創発指標の解釈、想定される結果のパターンを明文化することで、再現性と外部評価のしやすさが大幅に向上する
> - **(P2)** `src/simulation.py`(約1000行)はプロンプト構築・IO・apply phaseを別モジュールに分割すると保守性が上がる
> - **(P3)** `llm.fleet` モード(cognitive_tier ごとの混在LLM)が `NotImplementedError` のまま残されているため、これを実装するか、READMEで「未実装・将来計画」と明示することで誤解を避けられる
> - **(P4)** 創発検出が現状 stdlib-only の正規表現＋類似度ベースで保守的。実験規模に対して埋め込み類似度ベースの集合注目検出など、より定量的な追加指標を準備すると分析の説得力が増す

### 一言コメント(原文)

> 研究的問い・世界設計・モジュラなコード・LLM統合の完成度のいずれも高水準で揃った、ハッカソン提出物としては突出したクオリティ。READMEの研究目的を明文化すれば公開研究プロトタイプとして十分通用する仕上がりである。

---

## ② 各軸の採点根拠(引用)

### A. 創発設計 — 9.0/10

**評価文(原文)**
> 世界ルールの設計精度と行動の自由度の両軸ともに高水準で両立している。(中略)一方エージェントには、位置・距離・近傍POI・近傍人物・ニーズの自然言語表現・記憶など「生データと制約」のみを渡し、行動(移動先、発話、SNS投稿、中期目標)は完全にLLMの判断に委ねている。プロンプト中の「prefer to move」「typical dwell range」等は軽い記述的ヒントに留まり指示ではない。創発ポテンシャルは設計上極めて高い。

**明示された唯一の減点根拠(原文)**
> `src/simulation.py:329-336` — 「Choose stay when … prefer to move」というやや方向付けのある一文が含まれる(**減点要因の軽微なヒント**)

→ **A軸 −1.0 の明示根拠はこの1点のみ**。他の根拠 5 項目はすべて加点方向。

### B. 世界設定 — 9.0/10

**評価文(原文)**
> 題材は「渋谷駅周辺500m四方の流動人口」という極めて具体的な実地設定で、OSMから取得した実POI(`pois.geojson`、約100施設)を地理データとして用い、人口分布は国勢調査citation付きでハンドエンコードされている。(中略)デモ的な抽象都市ではなく、社会科学研究としてのオリジナリティと実問題への接続が極めて明瞭。

根拠 5 項目(demographics citation・12アーキタイプ・条件A/B・detect_emergence 3指標・pois.geojson 40KB)は**すべて加点方向で、減点根拠の記載が一切ない**。
→ **B軸 −1.0 の理由は講評本文に書かれていない**(検証レポートも指摘せず)。満点を出さない採点者の保守バイアスの可能性が高いが、断定はできない。

### C. 発展性 — 8.0/10 ★最弱軸

ルーブリック上は **コード拡張性 5 点 + 将来展望 5 点**の内訳(`00-rubric-and-ranking.md` 参照)。講評は節見出しをこの2つに分けている。

**コード拡張性(原文)**
> モジュール分離が極めて明確。`src/agent.py`(データクラス)、`src/simulation.py`(メインループ)、`src/llm_client.py`(プロバイダ抽象)、`src/needs.py`、`src/conversation_prob.py`、`src/geo.py`、`src/timeline.py` と単一責任で分割されており、新規ニーズ・会話レイヤ・POI種別の追加が局所改修で完結する。設定は8種のYAMLに完全外部化(中略)。`llm_client.get_client` は provider 文字列で分岐し、`llm.fleet` 設定で tier ごとに別LLMを混在させるスキャフォールドも既に用意されている。

→ 拡張性側は**べた褒めで否定語ゼロ**。

**将来展望(原文)**
> README のトップに「プロジェクト概要(ここはご自分で記述してください)」というプレースホルダが残されており、**研究の問いや具体的将来計画は明文化されていない**。一方で、コードレベルでは方向性が読み取れる:`config.llm.fleet`(gpt-4o-mini 60%/gemini-flash 30%/claude-haiku 10%の混在艦隊)は `NotImplementedError` で未実装、`scripts/detect_emergence.py` は架空地名・集合的注目・規範発話の3層指標を準備済み、`aggregate_runs.py` は条件比較を実装済み。**明文化された将来展望文書がない分、ロードマップ提示としては減点要因。**

→ **C軸 −2.0 は事実上すべて「将来展望」側**。減点の実体は 3 つ:
- **C-1** README 冒頭が未記入プレースホルダのまま(研究の問いが読み取れない)
- **C-2** `llm.fleet` が `NotImplementedError` の空スキャフォールド(意図が不明で誤解を招く)
- **C-3** ロードマップ文書が存在しない

検証レポートも同じ 3 点を減点要因として追認している:
> 減点要因: READMEの「プロジェクト概要」プレースホルダ未記入、`llm.fleet` 未実装、`scripts/aggregate_runs.py` などのスクリプトが揃っているが、**ロードマップ文書がない**。

### D. 技術実装 — 9.0/10

**LLM利用(原文抜粋)**
> `OpenAIClient`/`OllamaClient` が Protocol で統一インターフェース。`format_json=True` で `response_format=json_object` を指定し構造化出力を強制、コードフェンス／前置プロセを許容する `parse_decision` が頑健性を担保。(中略)プロンプトはセクション分離(中略)と末尾近接の重要フィールド配置で小型モデルの脱落に配慮されている。

**メモリ設計(原文抜粋)**
> 3層のメモリが意味的に機能。①rolling memory(`MEMORY_WINDOW=5` の自由記述行)、②`current_goal`(中期目標)、③`relationships`(warmth・common_topics・first_impression・remembered)。単なるログダンプではなく、過去会話の印象が次の遭遇時にプロンプトに具体的に再注入される。

**明示された唯一の減点根拠(原文)**
> 減点ポイントとして `src/simulation.py` が約1000行と大きく、プロンプト構築／IO／apply phase が同一ファイルに集中している点。

---

## ③ 指摘 → 現行 shibuya-simulation の解消状況 対照表

判定基準: **解消済み** = 現行に相当実装/文書が存在し確認できた / **部分** = 枠組みはあるが提出物・観測面で穴が残る / **未解消** = 相当物が確認できない。
根拠は現行リポジトリの実ファイル実査(2026-07-29)。

### A軸(創発設計)由来

| # | 講評の指摘(要約) | 判定 | 現行の根拠 |
|---|---|---|---|
| A-1 | プロンプトに「Choose stay when … prefer to move」という**方向付け文**が混入(唯一の明示減点根拠) | **解消済み(原則化)** | `README.md` L84-86「**no-fingerprint(R9)**: engine は因子を名指ししない…state 更新器には行動ログのみを渡し、初期 trait を配線レベルで除外する」を不変原則として宣言。`src/society/engine/scheduler.py:7`「engine は因子名を一切参照しない(no-fingerprint、tests/test_contracts.py で担保)」ほか `annual.py:10` `chance.py:20` `cognition/drive.py:11` `cognition/routine.py:9,236` `commerce.py:19,202` `conversation.py:19` `delivery.py:36` `disaster.py:19` `diversity.py:20` `economy.py:5` に契約コメント。`tests/test_contracts.py` で機械担保 |
| A-2 | (検証レポート R-1)「prefer to move」は実際には `"most people don't stand still without reason"` という**明確な行動誘導文**で、創発設計の純度を損なう | **部分** | R9 は「**因子名**を engine/プロンプトに出さない」契約であり、「**行動の一般論ヒント**を書かない」ことを直接固定するテキスト監査テストは実査範囲では見つからなかった。`scripts/detect_emergence.py` は分析専用でプロンプト監査ではない。→ 本選前に**プロンプト文言のゴールデン監査**(禁止語彙リスト = 行動誘導表現)を足す価値あり(IDEA-4) |
| A-3 | (検証レポート・見落とし)`_needs_boost` の**正フィードバックループ**(孤独/退屈が会話確率を押し上げる)が創発ループの重要要素なのに講評が触れていない = **アピール不足** | **解消済み(実装)/ 部分(提出物での提示)** | 現行は `src/society/needs.py` `factors/{affect,mood,psych,update}.py` `cognition/drive.py` で因子→状態更新を registry 化。ただし「どのフィードバックループが創発の駆動源か」を**提出物側で図示していない**(README にループ図なし) |
| A-4 | (`agent-freedom-audit.md` 由来の自己認識)行動的自由度が狭い = LLM が選べるのは「発火時の発話系+改変ツールだけ」で移動・就寝・消費等はルールベース | **部分** | `docs/research/agent-freedom-audit.md` §0 要旨3 が明示。以後 `src/society/freedom_p2.py` + `docs/plans/agent-freedom-plan.md`(P2 自由度)で拡張中。**完全解消の記載は確認できず** |

### B軸(世界設定)由来

| # | 講評の指摘(要約) | 判定 | 現行の根拠 |
|---|---|---|---|
| B-1 | (減点根拠の明示なし。加点のみ) | **強化済み** | 旧: OSM POI 102件・500m四方・16時間。現行: `data/shibuya_osm*.json`(OSM/ODbL)・`data/jinryu/`(国交省人流オープンデータ)・`data/odpt/`(公共交通オープンデータ実ダイヤ)・`data/floorguide_shibuya.json`(屋内フロア)・`data/organizations_shibuya_wide11k.json`(組織台帳1.1万)。`README.md` L100-110 に出典・ライセンスを個別明記 |
| B-2 | (検証レポート・見落とし)`events.yaml`/`environment.yaml`/`smartphone_use` 計算式の独自性が評価文に載っていない = **世界の細部が伝わっていない** | **強化済み(実装)/ 部分(提示)** | 現行 `conf/` は `config.yaml`/`daily.yaml`/`observe.yaml`/`production.yaml`/`longrun30.yaml`/`experiments/`/`profiles/`。世界側モジュールは 122 本(`src/society/**.py`)。ただし**「世界にこれだけの層がある」ことを一望させる図表が README にない** |

### C軸(発展性)由来 ★最重要

| # | 講評の指摘(要約) | 判定 | 現行の根拠 |
|---|---|---|---|
| **C-1** | README 冒頭が「プロジェクト概要(ここはご自分で記述してください)」の**未記入プレースホルダ**。研究の問いが読み取れない | **解消済み** | 現行 `README.md` L1-21: タイトル直後に「## 研究課題」節。「世界を変えようとする個体は、生まれつき存在するのか、環境から創発するのか。」を引用ブロックで提示し、Y(4層への書き換え量)/ k(信念書き戻し自由度)/ R²(k) / 相転移点 k\* / sham・null 対照(R1) まで**反証可能な形で明文化**。旧リポの `<!-- # プロジェクト概要（ここはご自分で記述してください…）-->` は現行に存在しない |
| **C-2** | `llm.fleet`(tier別混在LLM)が `NotImplementedError` の空スキャフォールド | **解消済み** | `src/society/llm/fleet.py`(112行)で `FleetLLM` 実装 = 複数 vLLM サーバへの sticky routing(agent_id 安定割当で prefix cache ヒット率向上)・障害時再分配 + cooldown(D16)・tier seam(`tiers={"reflect":[...], "default":[...]}`)。`src/society/llm/router.py`(79行)で purpose 別ルータ。`src/society/llm/vllm.py`(114行)。現行に残る `NotImplementedError` は `engine/simulation.py:661` の「未知 backend 名」ガード(`mock \| ollama \| vllm \| router`)と `llm/base.py:17` の抽象メソッドのみ = **意図が明示された正当な用法** |
| **C-3** | **明文化された将来展望文書(ロードマップ)がない**(C軸減点の主因) | **部分** | 内部文書は充実: `docs/design.md` §0 ビジョン / §4 ゴールの階層と今回の到達点 / §5 マイルストーン梯子 / §6 規模ラダー / §12 OPEN台帳 / §14 次のフェーズ計画、`docs/plans/` 22本(`finals-gpu-application.md` 402行・`w2-execution-plan.md`・`million-scale.md` 等)。**しかし README 自体に「将来展望/ロードマップ」節がなく**、`RESULTS.md` も未作成(実査で不在確認)。**審査者が README しか見ない場合、第1回と同じ「ロードマップ提示なし」評価になり得る** → ④で対策 |
| C-4 | (検証レポート・見落とし)`agent.py` の4thレイヤペルソナ属性など**拡張余地の宣言**が評価されていない | **解消済み(実装)** | `src/society/agents/persona.py` + `scripts/build_personas.py`(IPF骨格×尺度分布×LLM文章化)・`scripts/build_persona_pool.py`・`docs/plans/persona-pool.md` / `docs/research/persona-pool-1m.md` |

### D軸(技術実装)由来

| # | 講評の指摘(要約) | 判定 | 現行の根拠 |
|---|---|---|---|
| **D-1** | `src/simulation.py` 約1000行(実測958行)が**モノリシック**。プロンプト構築/IO/apply phase が同居 | **部分(むしろ悪化の側面あり)** | 全体としては 7ファイル → **122 モジュール**へ大幅分割(`llm/` `world/` `agents/` `factors/` `cognition/` `actions/` `labeling/` `observer/` `engine/`)。観測は `observer/` に frame 分離済み。**ただし `src/society/engine/scheduler.py` = 4,541行、`engine/simulation.py` = 1,341行、`observer/measure.py` = 1,123行**。旧 958行より大きい単一ファイルが 2 本存在し、第1回と同じ指摘が**そのまま再発しうる** → ④で対策 |
| D-2 | (検証レポート R-5)LLM 呼び出しが**各エージェント逐次(並列化なし)**でスケールしない(200×96 = 19,200呼が直列)。「言及があれば D=8.5」 | **解消済み** | `engine.batch_llm` 経路: `scheduler.py:796-835` `_phase_planning_batched`(朝計画一括)・`841-901` `_phase_reflect_batched`(夜内省一括)、既定 `workers=8`。`llm/cache.py:99-100` が `ThreadPoolExecutor(max_workers=workers)` で `generate_many` を実装。逐次経路と**イベント列・カウンタ・キャッシュ内容が完全同一**であることを `tests/test_batch_llm.py` がバイト一致で固定。加えて `FleetLLM` が複数 vLLM サーバへ水平分散 |
| D-3 | (検証レポート・加点見落とし)seed 派生 RNG による**完全決定性**が評価文に載っていない | **解消済み(実装)/ 部分(提示)** | `src/society/rng.py`(中央集権シード)+ `llm/cache.py`(応答キャッシュ)。`README.md` L82-83「Mock はプロンプトと rng キーだけから応答が決まり、**呼び出し順に依存しない**」。`tests/test_determinism.py` あり。CRN 設計は `conf/experiments/endogenous_accept.yaml` で同一 seed 列 |

### 総評の改善提言(P1〜P4)

| # | 提言 | 判定 | 現行の根拠 |
|---|---|---|---|
| **P1** | README のプレースホルダを埋め、研究問い・対照群設計・創発指標の解釈・**想定される結果のパターン**を明文化 | **部分** | 研究問い・k 掃引・sham/null 対照は `README.md` L6-21 / L80-90 に明文化済み(C-1 解消)。**「想定される結果のパターン」= どう転んだら何が言えるかの事前予測が README にない**。`docs/design.md` §3 反証可能な再定式化に近い記述はあるが提出物面には出ていない → ④で対策 |
| **P2** | `simulation.py` をプロンプト構築/IO/apply phase に分割 | **部分** | D-1 と同じ。全体分割は達成、巨大ファイル 2 本が残存 |
| **P3** | `llm.fleet` を実装するか README で「未実装・将来計画」と明示 | **解消済み** | C-2 と同じ。実装完了 |
| **P4** | 創発検出が **stdlib-only の正規表現＋類似度ベースで保守的**。埋め込み類似度ベースの集合注目検出など定量指標を追加せよ | **部分** | `scripts/detect_emergence.py` は現行 parquet L1 へ移植済み(fiction / norms / attention の3検出器・分析専用・sim 本体不変)。しかし**依存は「標準ライブラリ + pyarrow + omegaconf のみ」**(同ファイル docstring 明記)で `difflib.SequenceMatcher` を使用 = **埋め込み化は未着手**。一方で定量側は大幅強化: `observer/` に 85 個の集約器(`register_aggregator`)、`aggregate.py` の Gini・上位10%集中度、`observer/assets.py` の資産 Gini、`analyze_*.py` 15本(structure / communities / bridging / weak_ties / founders / imitation / worldview / od / luck / groups / resolution / endo_treatment / flows_grid / sweep)、`labeling/` のラベル採用S字・伝播計測 |

### スライド(自己申告)由来 — 第1回の実験そのものの弱み

講評は**コードを見て採点しており、スライドで自己申告された実験の破綻をほぼ減点していない**。しかし本選では「実行結果のまとめ(RESULTS.md 等)」が推奨されている(`docs/plans/finals-gpu-application.md` §0.1 公式サイト実査)ため、ここが最大の再発リスク。

| # | スライドが自己申告した弱み | 判定 | 現行の根拠 |
|---|---|---|---|
| **S-1** | 実験1: 全 7,680 イベント中 **エラー率 83.7%**。step 0-1 のみ 100% 成功、step 8 以降ほぼ全エージェントがエラー(p.4) | **解消済み(構造的)** | 根本原因は OpenAI API の TPM/RPD。本選は**ローカル vLLM × GPU 7枚**(`docs/plans/finals-gpu-application.md` §0)= 外部レート制限なし。`llm/vllm.py:110-114` はエラーを例外でなく `"__vllm_error__: ..."` 文字列で返し上位で fallback(D16)。`llm/fleet.py:100` が failover + cooldown。`scripts/watchdog.py` が checkpoint/resume・ストール検知・破損時の世代巻き戻しを担う |
| **S-2** | 実験2: 成功率 28.5%(step0 67% → step5 6%)(p.6) | 同上 | 同上 |
| **S-3** | SNS: **reply/quote が 0 件**。「短時間ウィンドウでは投稿先行、会話は未発達」(p.8) | **部分** | 現行 `src/society/net/internet.py`(212行)は post / like / reshare を実装(`n_likes_total`・`reshares`)。**reply(返信スレッド)は実査範囲で確認できず**。会話は物理側 `conversation.py` + `gossip.py` + `media.py` が担う設計。ネット上の対話連鎖を測るなら追加検討が要る(IDEA-6) |
| **S-4** | **A/B 対照群の比較が未実施**。実測は B(SNS あり)・seed=1 のみで、研究課題 Q2「SNS は物理集中を代替するか」に未回答 | **解消済み(枠組み)** | `scripts/run_sweep.py`(k 掃引 off/sham/free × seeds)・`scripts/analyze_sweep.py`(seed 階層ブートストラップ CI・計算量交絡監査)・`conf/experiments/endogenous_accept.yaml`(6セル CRN 同一 seed 列 30ラン)・`scripts/analyze_endo_treatment.py`(CRN ペア差 + sign-flip permutation 主検定)。README L87-88 に R1 対照が不変原則として記載 |
| **S-5** | 根本原因が **TPM(1コール≈2,500 tokens × 200体 = 500k tokens/step > Tier1 上限 200k/min)**。解決策は Token Bucket throttling / Tier2 課金(p.10) | **解消済み** | S-1 と同じ。加えて `scripts/estimate_runtime.py` `scripts/bench.py` `scripts/bench_longrun.py` `scripts/profile_engine.py` で事前見積り。`finals-gpu-application.md` §1.2 に呼数較正式 `C_calls(N)=min(3988·(N/200)^1.209, 43200)+305·(N/200)` |
| **S-6** | 実験1(80体×96step)と実験2(200体×6step)は**規模も時間幅も違い直接比較できない**(交絡)。にもかかわらず p.9 で並べて比較表にしている | **解消済み** | CRN(同一 seed 列)・sham/null/compute 一定対照(R1)・`analyze_sweep.py` の「計算量交絡監査」。`analyze_endo_treatment.py` は「ネットワーク内置換はラン単位置換で過大有意回避(Farine 2022)」まで実装 |
| **S-7** | 集合幻想(Q3)の証拠は「ハッシュタグ #渋谷 #カフェ の自発収束」のみ。**L3 規範形成は未検出**(p.11「長期」へ先送り) | **部分** | `detect_emergence.py` の norms 検出器(〜べき/してはいけない/普通/常識/マナー…)+ `labeling/labels.py` のラベル造語・採用閾値・drift + `observer/structure.py`。ただし**規範創発の実 LLM 実測記録**は本調査の範囲では確認していない |
| **S-8** | LLM 呼の成否がラン中に見えず、**終わってから 83.7% エラーと判明**した | **未解消(観測ギャップ)** | 現行は L1b(`observer/logger.py:31,54` `llm_calls` → `l1b_llm.parquet`)に呼を残すが、**`register_aggregator` 85個の中に「LLM 成功率 / パース失敗率 / fallback 率」の L2 系列が見当たらない**(grep: `fallback_rate\|llm_fail\|parse_fail\|llm_error` → `observer/*.py` `cognition/*.py` でヒット 0)。`watchdog.py` はプロセス死・ストールは見るが**「生きているが全員 fallback」は検知できない**。→ 本選最大級の再発リスク(IDEA-1) |

---

## ④ C軸(発展性 8.0)の精査と本選対策案

### 4.1 何が減点されたのかの結論

- ルーブリック内訳 = **コード拡張性 5 + 将来展望 5**。
- 講評の「コード拡張性」節は**否定語ゼロの絶賛**(「モジュール分離が極めて明確」「局所改修で完結する」)。
- 講評の「将来展望」節は**明確に減点を宣言**(「明文化された将来展望文書がない分、ロードマップ提示としては減点要因」)。
- 検証レポートも減点要因を「READMEプレースホルダ未記入 / `llm.fleet` 未実装 / ロードマップ文書がない」の3点に限定して追認。

→ **C軸 −2.0 のほぼ全量が「将来展望」側**、つまり **コードではなく提出物(README)の問題**だった。逆に言えば、
**書けば取り返せる 2 点**であり、本選で最も費用対効果の高い改善点である。

### 4.2 現行の残存リスク(第1回と同じ穴が空いていないか)

| リスク | 現状 | 危険度 |
|---|---|---|
| README に「将来展望/ロードマップ」節が**ない** | 研究課題節はあるが、次に何をするかは `docs/design.md` へのリンク止まり。審査者が README しか読まないと第1回と同じ判定になる | **高** |
| `RESULTS.md` が**存在しない** | 公式が「実行結果のまとめ(RESULTS.md 等)もあると、審査に伝わりやすくなります」と明記(`finals-gpu-application.md` §0.1) | **高** |
| 「想定される結果のパターン」が提出物にない | P1 提言の未消化部分。事前予測がないと事後解釈に見える | 中 |
| 巨大ファイル(`scheduler.py` 4,541行 / `simulation.py` 1,341行 / `measure.py` 1,123行) | D軸で「約1000行がモノリシック」と減点された当時より大きい | 中(C軸の拡張性側にも波及しうる) |
| 122 モジュールの**全体像を示す図が README にない** | 現在はディレクトリツリー(README L58-71)のみ。層の多さが強みなのに伝わらない | 中 |

### 4.3 本選提出物への具体対策案

#### (A) README に「## 将来展望(ロードマップ)」節を新設 ★最優先

第1回の減点文をそのまま反転させる構成にする。3 スパンで書き、**各項目に既存の内部文書へのリンクを張る**
(「文書がない」ではなく「文書がある」ことを審査者に見せる)。

```markdown
## 将来展望(ロードマップ)

### 本選期間(8/15–8/30)で到達する
- 在場 5万〜25万体 × 3〜10 シミュ日の観察ラン(→ docs/plans/finals-gpu-application.md §1.2 #1)
- k 掃引 300体 × 14 シミュ日 × 30 ラン で R²(k) と k* の初回推定(同 #2)
- 関係性内生化 treatment 6セル CRN(同 #3・conf/experiments/endogenous_accept.yaml)

### 本選後 6 か月
- 100万体スケール(→ docs/plans/million-scale.md)
- VLM 視覚パイプライン(→ docs/research/agent-vision.md)
- 3D/PLATEAU 実形状ビューア(→ docs/plans/plateau-3d.md)

### 長期(研究基盤として)
- k* の再現性検証と査読論文化
- 他都市へのポート(EnvPack: env/shimokita/ で下北沢を試験済み)

未確定事項は docs/design.md §12「OPEN 台帳」で管理し、勝手に確定させない運用にしている。
```

**効き目**: C-3(ロードマップ文書がない)を直接潰す。かつ「OPEN 台帳で未確定を管理」は
**研究プロジェクトとしての成熟度**のアピールになり、単なる願望リストと差別化できる。

#### (B) `RESULTS.md` を新規作成 ★最優先

公式推奨。第1回スライドの敗因(「実験1と実験2が比較不能」「83.7%エラー」)を**繰り返さない形式**で書く。
推奨構成:

1. **1行サマリ**(何が言えたか)
2. **ラン台帳**: run_id / 条件 / 体数 / step 数 / seed / モデル / 壁時計 / **LLM 呼数と成功率** の表
   ← ここに成功率列を必ず置く。第1回はこれがなく、事後に 83.7% と判明した
3. **主結果**: R²(k) 曲線 + seed 階層ブートストラップ CI + k* 候補
4. **対照が効いていることの証拠**: sham / null / compute 一定で 3 信号が出ないこと(R1)
5. **ネガティブ結果と限界**(正直に): 検出力の限界・未達の条件・交絡の残り
6. **再現手順**: コマンド1行ずつ(`scripts/run_sweep.py` → `analyze_sweep.py`)

**効き目**: 「将来展望」だけでなく「今回何が言えたか」が独立文書になるため、A/B/D 軸の心証にも波及する。

#### (C) 「想定される結果のパターン」を README か RESULTS.md に事前登録

P1 の未消化部分。例:

> - R²(k) が k に対して単調減少し、sham で減少しない → **創発レジームの支持**
> - R²(k) が k に依らず高止まり → **初期条件支配(「生まれつき」寄り)**
> - sham でも同じ低下が出る → **計算量交絡**であり k* の主張は取り下げる

**効き目**: 事前予測を書いておくと、どちらに転んでも「予測どおり/予測外」を語れる。
講評 P1 が名指しした「想定される結果のパターン」に正面から答える形になる。

#### (D) 巨大ファイル 2 本の分割(または分割計画の明示)

`scheduler.py` 4,541行は第1回の減点対象(958行)の 4.7 倍。本選期間中の全面リファクタは
リスクが高いので、**最低でも「なぜ大きいか + 分割の seam」を docs に明記**して、
README のアーキテクチャ節から参照する。`docs/design.md` §11「モジュール構成(seam 一覧)」に
追記するのが最小コスト。理想は phase 単位(planning / reflect / commerce / transit)への分割。

#### (E) アーキテクチャ 1 枚図を README に

122 モジュール・4 層(空間/資源/象徴/social network)・observer frame 分離を 1 枚で見せる。
mermaid なら GitHub 上でそのまま描画されるため追加依存ゼロ。
**効き目**: B軸(世界の厚み)+ C軸(拡張性)の両方に効く。第1回は「src/ 7ファイル」でも褒められた。

---

## ⑤ `_eval_review`(検証レポート)の所見

### 5.1 検証の結論

> 元評価の**スコア(35/40)はソースコードの実在内容と整合しており、誇張・捏造は見られない**。ただし `src/simulation.py` 内の引用行番号が系統的に若干ズレている(おおむね20〜40行下方)点は要修正。**本質的なスコア改定は不要**。

推奨調整は **A 9.0 維持 / B 9.0 維持 / C 8.0 維持 / D 8.5〜9.0**、最終 **34.5〜35.0 が妥当**。

### 5.2 本選に効く「検証者視点」の学び

1. **引用行番号は検証される**。検証レポートは全 24 個の引用行を実ファイルと突き合わせ、
   ズレを列挙している(最大 33 行)。→ 本選の README / RESULTS.md で
   コードを引用するなら **行番号ではなく関数名・見出しで参照**するほうが陳腐化しない。
2. **評価者が拾い損ねた強みは失点になる**。検証レポートの「見落とし」欄には、
   `_needs_boost` の正フィードバックループ / `smartphone_use` 計算式 / seed 派生 RNG の完全決定性 /
   4thレイヤペルソナ属性 / Ollama→OpenAI のローカル→クラウド移行ワークフロー が並ぶ。
   **実装してあっても README に書いていなければ採点されない**。
   → 現行の強み(no-fingerprint R9・CRN・sham/null 対照・観測 frame 分離・122モジュール・
   実データ 5 系統・1,725テスト)を**README に列挙する**べき(IDEA-2)。
3. **「言及があれば減点されたはずの弱み」がある**。検証レポートは
   「LLM呼び出しが各エージェント逐次(並列化なし)でスケールしない…**言及があれば 8.5 寄りの評価にもなり得る**」
   と書いている。つまり **評価者が気づかなかったから 9.0 だった**。
   → 本選の評価者(または人間審査員)が気づく可能性を前提に、**スケール性の証拠を先回りで出す**
   (`scripts/bench.py` の実測表を RESULTS.md に載せる)。
4. **検証レポートは「加点根拠の実在確認」までやる**。`data/pois.geojson` の Feature 数を 102 個と数え、
   `archetypes.yaml` の weight 合計 1.00 を確認している。→ **README の主張は必ず実ファイルで裏が取れる形にする**。
   数値を書くなら出典ファイル名を併記(現行 `finals-gpu-application.md` の【実測】【推定】【本書計算】凡例は良い先例)。

---

## ⑥ スライドの気づき — 審査に何が伝わり、何が伝わらなかったか

`slides/04-2021_146-shibuya-sim.pdf`(11ページ・2026/05/07 進捗報告)。
※ PDF のテキスト抽出は日本語がサブセットフォントで欠落したため、`fitz` で dpi=100 の PNG 化して視覚読解した。

### 6.1 スライド構成

| p | 内容 |
|---|---|
| 1 | 表紙「渋谷マルチエージェントシミュレーション」進捗報告 2026/05/07 / 200エージェント × 100POI × LLM決定 × SNS層 |
| 2 | 研究課題 Q1 都市の物理的集中はどう創発するのか / Q2 インターネット(SNS)は物理集中を代替するか / Q3 集合幻想は自然発生するか |
| 3 | システム構成(200ペルソナ・100 POI・96step×10分・7ニーズ×2層・5層会話確率・1,615エッジの事前関係グラフ) |
| 4 | 実験1: 80ag × 96step。**「結果: データ品質に致命的問題」エラー率 83.7%**・SNS 2投稿・有効POI移動 929(16.3%) |
| 5 | 実験1の知見「朝の集中創発」: step0 で 78/80 が move、Urth Caffé 34.6% / トップ3カフェ 67% / HHI 0.179 / 効果的選択肢数 5.6 |
| 6 | 実験2: 200ag × 6step。成功率 28.5%(step0 67% → step5 6%)・SNS 15投稿・ハッシュタグ収束 #渋谷 #カフェ |
| 7 | 実験2の知見「密度が集中を増幅」: HHI 0.231(vs 0.179)・step5 で 161/200 が POI 到着・**「これは社会的同調ではなく構造誘発(駅から見える POI が共通)」** |
| 8 | SNS層: 15投稿の主題分布(カフェ12/ラーメン3)・#渋谷#カフェ を異なる8ペルソナが独立採用・**reply/quote 0件** |
| 9 | 実験1 vs 実験2 比較表 |
| 10 | 制約: API レート制限。TPM 根本原因 / RPD 二次原因 / 解決策 (A) Token Bucket throttling (B) Tier2 課金 |
| 11 | 次のステップ(短期1-2日 / 中期1週間 / 長期) |

### 6.2 審査に**伝わった**もの

- **研究課題が3つの疑問文で最初に出る**(p.2)。講評 A/B 軸の高評価と整合。
  → 現行 README も同じ構造(研究課題を最上部)を維持しており、この形式は正解だった。
- **定量指標を持っている**こと(HHI・効果的選択肢数・シェア%)。抽象的な「創発した」ではなく数値。
- **失敗を隠していない**(p.4「データ品質に致命的問題」・p.10 で根本原因を TPM まで分解)。
  講評はこれを減点していない。**むしろ原因分析の質が技術実装の心証を上げた可能性がある**。
- **代替説明を自分から潰している**(p.7「社会的同調ではなく構造誘発」)。
  これは研究者的な誠実さのアピールとして強い。

### 6.3 審査に**伝わらなかった**もの / スライドの弱み

1. **研究課題 Q2 に答えていない**。Q2 は「SNS は物理集中を代替するか」= A/B 比較が本体なのに、
   実測は **B のみ・seed=1 のみ**。p.11 で「同 seed で A と B のペア比較」が**短期タスクに残っている**。
   → **問いを立てたのに対照を回していない**。第1回で最も惜しい構造的欠落。
2. **p.9 の比較表が交絡している**。実験1(80体×16時間)と実験2(200体×1時間)は
   体数も時間幅も違うのに HHI 0.179 → 0.231 を「密度依存集中増幅」と読んでいる。
   時間帯効果(06:00 のみ vs 全日)と交絡している可能性を排除できていない。
3. **「エラー率83.7%」の下でも知見を主張している**構図。p.5 は「step0 のみクリーンデータ」と
   断りを入れているが、n=80 の 1 step から HHI を出すのは統計的に脆い(CI なし)。
4. **講評はスライドをほぼ見ていない**。講評根拠は全て `src/` `config/` `README.md` `data/` のファイル参照で、
   スライドの実験結果への言及がゼロ。→ **第1回の採点はコード実査ベース**だった。
   ただし本選は「プレゼン資料・README 必須 + RESULTS.md 推奨」と公式に明記されているため、
   **本選では結果の質が採点対象に入る**と考えるべき。
5. **世界の厚みがスライドに出ていない**。p.3 の「システム構成」は 8 行。
   講評が高く評価した citation 付き人口分布・12アーキタイプ・events.yaml・environment.yaml は**スライドに登場しない**。
   → **コードを読んだ講評のほうがスライドより世界設定を高く評価している**という逆転が起きている。

### 6.4 本選のスライド設計への含意

- p.2 の「疑問文3つ」形式は維持。ただし **立てた問いには必ず対照ランで答える**(Q2 の失敗を繰り返さない)。
- **比較表は必ず同一条件差分にする**(体数・時間幅・seed を揃え、変えるのは1因子だけ)。
- **数値には必ず n と CI を付ける**。第1回は HHI に CI がなかった。
- **世界の厚み(実データ 5 系統・122モジュール・組織1.1万)を 1 枚図で見せる**。
  第1回はコードを読まないと分からない状態だった。
- **ラン成功率をスライドに1行載せる**。「LLM 呼 N 万・成功率 99.x%」は第1回との対比で強い。

---

## 付録: 評価対象リポジトリ(旧 shibuya-sim)の構成

`gh api repos/spacedream6090-svg/shibuya-sim/git/trees/main?recursive=1` 実査(2026-07-29)。
**34 ファイル・合計 86KB**。現行 `shibuya-simulation` とは別実装(前身 MVP)。

```
README.md (9,229B)  main.py (2,822B)  requirements.txt
config/  archetypes.yaml demographics_shibuya.yaml config.yaml conversation.yaml
         environment.yaml events.yaml personas.yaml
data/    pois.geojson (40,028B)
src/     agent.py(2,148) conversation_prob.py(4,435) geo.py(1,917) llm_client.py(5,500)
         needs.py(7,073) simulation.py(40,910=958行) timeline.py(7,395)
scripts/ aggregate_runs.py build_personas_index.py debug_one_call.py detect_emergence.py
         estimate_cost.py fetch_demographics.py fetch_pois.py generate_pool.py
         run_metrics.py summarize_run.py test_llm.py warmup_relationships.py
visualization/ build_viewer.py (30,417B)
```

**実査で判明した補足**: main ブランチのツリーに `config/personas/agent_*.yaml` と
`config/personas_index.yaml` は**含まれていない**(生成物のためコミットされていない)。
講評 C軸は「`config/personas/`(生成された個別ペルソナ)」を根拠に挙げているが、
これは README の記述からの推定だった可能性がある。テストディレクトリも存在しない。
→ 現行は `tests/` 175ファイル・1,725テスト緑(直近コミットメッセージ)であり、**明確な前進**。
**ただし第1回はテストがゼロでも D軸 9.0 だった**ため、テスト数が直接得点に効く保証はない。
