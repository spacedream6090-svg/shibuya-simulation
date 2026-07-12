# サーバー化の要否 — 実行場所・アーキ・可視化配信・オーケストレーションの判断材料

- 種別: リサーチ(調査のみ)。実LLM実行なし・src非編集・git commitなし。
- 実施: 2026-07-07、Opus 4.8 サブエージェント。
- 位置づけ: **これは「確定」ではなく判断材料**。ユーザーが「このシミュをサーバー上で動かすべきか」を決めるための整理。最終決定はユーザー。
- 出典方針: リポジトリ内の一次(コード・既存 docs)を根拠に据え、クラウド価格のみ外部を引く。**価格・所要時間は変動・未実測が多いので「概算/要検証」と明記**し、推測を事実として書かない。
- **主シナリオ = ハッカソン本選(単一データセンター機、7×A5000 相当 168GB、10日間・無償提供)**(`docs/AUTOMATA第2回ハッカソン案.md`「168GBのVRAM(RTX5000×7台)」、`docs/lit/shibuya_sim_infra_summary.md §1`)。
  - ⚠️ 本選 GPU が **A5000(Ampere)か RTX 5000 Ada か**は現地確認事項(168÷7=24GB は両立)。量子化・FP8 の可否に影響するがサーバー化の結論には無関係。詳細は `docs/research/llm-model-selection.md §3.0/§5`。

---

## 0. 結論(4行)

**サーバー化は「部分的に要る」。** ただし内訳が重要:

1. **本当に要る「サーバー」= 7GPU 上の vLLM 群(LLM 艦隊)は、既に必須でありコード上も完成済み**(`src/society/llm/{vllm,fleet}.py`、`docs/ops-production.md`)。実 LLM 推論は OpenAI 互換サーバとして常駐させ、シミュはその**クライアント**になる——この意味では「サーバー化」は設計済みで、残りは本選機での**疎通確認(bench.py)だけ**。
2. **世間で「サーバー化」と言うときの残り(シミュ本体の API/サービス化・ジョブキュー・分散スケジューラ・可視化のストリーム配信・外部DB)は、単一機の本選には不要**で、むしろ本選中の障害面を増やす**過剰投資**。現状のバッチ実行(run→analyze→viewer)+ watchdog 監督で単一機は完結する。
3. 実行場所は**本選機(オンプレ単一ノード)が第一**。ローカル開発機は mock/ollama のスモーク専用、クラウドは**本選前のリハーサル/障害時フォールバック**に限定(URL 差し替えだけで両対応=移行コストほぼゼロ)。

---

## 1. 前提の確定(このシミュのワークロード)

サーバー化を論じる前に、コード・docs から「何を回すのか」を固定する。

| 項目 | 実体 | 根拠 |
|---|---|---|
| 研究目的 | 世界改変者の創発を R²(k) で測る。論文級 k* データが目標 | MEMORY / `docs/research-scope.md` |
| 本番規模 | **1万〜3万エージェント × 100日 = 14,400 step**(1 step=10分、目標 現実30秒/step) | `docs/research/scale-audit-100days.md §0` |
| 律速 | **LLM 推論**。`lod.max_llm_per_step=300` が deliberate を cap。planning/reflection は非ゲート(n で増える)。総呼数 **~6.3M(10k)〜10.3M(30k)**、~6.8B〜14B token | scale-audit §3、`conf/config.yaml:275` |
| ハード(本選) | **単一ノードに 7×A5000 24GB(168GB)**。各 GPU に vLLM 1 本、7 本を FleetLLM で sticky routing | ops-production §0、infra summary §1 |
| 再現性 | **応答キャッシュ**(`llm_cache.jsonl`、キー=`sha256(backend.name + params + prompt)`、**URL 非依存**) | `src/society/llm/cache.py`、ops §5 |
| 決定論 | named RNG stream + checkpoint/resume。厳密再現は**キャッシュ再生**で担保 | `src/society/engine/checkpoint.py`、ops §5 |
| 既存インフラ | **vLLM 艦隊(fleet.py)+ watchdog(自動再開・破損復旧)+ checkpoint** は実装済み。1台7GPU/複数ノード/tensor-parallel を **config の URL 差し替えだけ**で切替 | fleet.py、`scripts/watchdog.py`、checkpoint.py、ops §2 |
| 実行形態 | **バッチ**。`run.py`(または `run_sweep.py` / `watchdog.py`)→ `analyze.py` → `export_3d.py`/`export_ue.py` → `make_viewer.py`。すべて CLI・config 駆動(D11) | scripts/*、viz/* |
| 現状に**無い**もの | HTTP API・ジョブキュー・外部DB。`storage.backend: redis_pg` は **config の未実装スタブ**(src に redis/pg 実体なし)。全処理は **in-process** | `conf/config.yaml:319`、src 全走査で redis/fastapi 実体なし |

要点: **「サーバー」の一次候補である vLLM 群は既に設計・実装済み**。未検証なのは**実機での疎通**であって、新規インフラの構築ではない(ops-production は繰り返し「実機未検証」と明記)。

---

## 2. 「サーバー上で動かす」の 4 解釈を分けて論じる

「サーバー化」は多義的なので、4 つに分解して個別に是非を出す。

### 2.1 実行場所 — ローカル / オンプレ単一機 / クラウドGPU

| 場所 | 何ができるか | コスト | 再現性 | 立上げ手間 | 位置づけ |
|---|---|---|---|---|---|
| **ローカル開発機**(RTX 5070。infra summary ではフロント専用) | mock/ollama で ≤80体・数日ぶんのスモーク。27B 艦隊も 10k体の RAM も載らない | 無償(手元) | mock/キャッシュで完全 | ゼロ(現状) | **開発・スモーク専用**。本番は不可 |
| **オンプレ単一機(本選機 7×A5000)** ★第一 | 本番 10k〜30k×100日。vLLM 7 本 + watchdog を同ノード常駐。ops-production の構成(A)そのまま | **無償**(本選提供、10日間) | 同一機でキャッシュ生成→再生=完全 | 中(vLLM 起動+bench 疎通) | **本番の主戦場** |
| **クラウドGPU**(AWS/GCP/Azure/Lambda/RunPod/Vast 等) | 本選機と同じ config を **URL 差し替えだけ**で実行(ops §2-B 複数ノード両対応、D13 キャッシュ URL 非依存) | 従量(§3.5) | キャッシュは URL 非依存で移設可。ただし temperature>0 の**初回**はサーバ差で揺れる→**k\* 本データは1か所で生成**すべき | 中〜大(調達・環境構築・egress) | **本選前リハーサル / 障害時フォールバック**限定 |

- **A5000 は Ampere で FP8 ハード加速なし**(llm-model-selection §3.0)。クラウドで近い等価は **A6000(Ada 48GB より前世代の Ampere・48GB)**、速度優先なら L40S/A100。
- クラウドの効きどころは「本選機を触れるのは本選 10 日間だけ」という制約。**本選前に 100日フルスケールのリハーサル**をしたい/**本選機が落ちたときの保険**を持ちたい場合にのみ意味を持つ。**移行コストが低い**(URL 差し替え+キャッシュ有効)ので「保険として設計に織り込む」のは安いが、**常用する理由はない**(本選機が無償)。
- 注意点(クラウド固有): 7 枚同一 GPU を**1ノードに**揃えられる保証はない(揃わなければ複数ノード構成 B=コードは対応済み)。**egress**(結果 parquet ~15〜90GB/100日ラン=scale-audit §2.1)に課金する事業者あり(Lambda は egress 無料)。community/spot は**プリエンプト**され得る→長時間ランは watchdog + checkpoint 必須(既に具備)。

**小結**: 実行場所は**本選機が第一**。クラウドは「安く保険を張れるが常用不要」。ローカルは開発専用。

### 2.2 アーキテクチャ — バッチのまま / 常駐サービス・API 化

- **(a) 現状バッチ**: `run.py`(または sweep / watchdog)を叩き、成果物をファイルに書く。config が実験条件を宣言し(D11)、watchdog が長時間ランを監督(落ちたら最新 checkpoint から自動再開、破損は世代バックアップから復旧)。
- **(b) 常駐サービス/API 化**: シミュを HTTP/キュー越しにジョブ投入・進捗取得・結果取得する形にする。

| | (a) バッチ(現状) | (b) API/サービス化 |
|---|---|---|
| 利点 | 最小・決定論・D11 と一致。watchdog が監督ランを既に提供。sweep が N×k×seed を直列で回す。**単一機・単一長時間ランに最適**。本選中に壊れる可動部が少ない | 複数ラン並列投入・リモート投入・ライブ進捗・掃引自動化 |
| 重さ/難点 | リモート投入や API はない。掃引は直列 | Web サービス+キュー+(場合により)DB という**新しい面**。本選中の新規障害モード。**シミュは長時間バッチであってリクエスト応答サービスではない**——API を被せても計算内容は変わらず複雑性だけ増える |

- 重要な誤解の解消: **「サーバー」は既に1つ動く——vLLM 群**(常駐 OpenAI 互換サービス)。シミュは**既にその常駐サーバのクライアント**。問題は「**シミュ本体まで**サービス化するか」であり、単一機の本選では**否**。
- 進捗の可視化は薄い面が既にある: watchdog が `status.json`(state/restarts/last_progress/pid)+ `watchdog.log` + `run.out.log` を書く。リモートで見たいだけなら **SSH で tail、または 10 行の静的ファイルサーバ**で足り、フル API は不要。

**小結**: 本選ではバッチ維持が正解。API 化は「複数ノードで多数ランを無人運用する」段階になって初めて検討。

### 2.3 可視化の配信 — 自己完結 HTML / サーバがストリーム配信

- **現状**: `make_viewer.py` が `viewer.html`(地図・再生・フォーカス)と `dashboard.html`(出来事/SNS/語彙/関係グラフ/分析)を**データ埋め込みの自己完結 HTML**として静的生成。`viewer3d.html`(three.js)も同様。OSM タイルのみオンライン時に読む(オフラインでも動く)。検索は**シミュ内DB**(実 API 不使用=D13 再現性+架空世界の閉性)。UE 経路は `export_ue.py` → `sim_ue.json` を **UE の再生アクタが読む**下流(Blender は quick-look)。
- **「サーバがストリーム配信」型にする価値は本選デモの観点で低い**:
  - 自己完結 HTML は**強いデモ資産**——ブラウザで開くだけ・オフライン可・ポータブル(USB/メール)。発表 LT は「回し終えたランのダッシュボード/3D、または PLATEAU 渋谷の UE フライスルー」を見せる形で、**どれもストリームサーバを要しない**。
  - ライブ配信が意味を持つのは「実行中のランを進捗表示」する場合だが、**100日ランは数日かかる**ので本番ランのライブ配信はデモにならない。ライブで見せるなら**数体×数十 step の短スモーク**——それは事前生成物として用意する方が堅い。
  - チームや審査員が各自端末で HTML を見たいだけなら **`python -m http.server` か任意の静的ホスト or SSH トンネル**で配れる。これは「ファイルを配る」であって「シミュのサーバー化」ではない(自明・任意)。
  - UE は重量級のフォトリアル・デモで、**フロント PC(RTX 5070)**上で `sim_ue.json` を再生する別アプリ。GPU ノードをサーバー化する必要はなく、**エクスポート済み JSON があればよい**(バッチの1ステップ)。

**小結**: 可視化はサーバー化不要。静的 HTML +(フロント PC 上の)UE 再生が本選デモの正解。配布したいなら静的ファイルサーバで足りる。

### 2.4 オーケストレーション — 単一機の並列 / ジョブスケジューラ

掃引(N×k×seed の多数ラン)の回し方。

- **現状**: `run_sweep.py` が modes×seeds×agents を**直列** in-process 実行。各ランは自分の `runs/<name>/` に隔離(実行前に掃除)。長時間ランは watchdog が個別に監督。
- **単一機で直列が実は正しい理由**: **1 ランが既に 7GPU 全部を FleetLLM で使い切る**。10k体級ランを2本同時に走らせても同じ GPU を奪い合うだけで速くならない(干渉するだけ)。だから**大規模ランは直列が最適**(各ランがフル艦隊を得る)。
- **小規模パイロット(60体×144step 等)**は艦隊を余らせるので数本パックできる。ここは**シェルの並列(GNU parallel 等)や run_sweep の薄い並列化**で足りる。ジョブスケジューラは不要。
- **スケジューラ(Slurm/Ray/Redis queue)が正当化されるのは**「複数ノードのクラスタ」or「競合管理が要る多数小ジョブのファンアウト」。**単一ノード+1本の支配的長時間ランには過剰**。信頼性(自動再起動・再開)は watchdog が既に肩代わりしている。
- 既存 docs との整合: `docs/lit/engine__distributed-actor-overview.md` は actor/Ray を「**実装の器**であり現象を規定しない、分散の複雑性は開発コスト」と結論。`docs/lit/infra__storage-routing.md` の Fable 5 見立ても「10日ビルドなら単一ノードの Redis+pgvector+NetworkX が運用最小、限界が見えたら差替え」——そして**その storage backend すら未実装スタブ**(§1)。つまりプロジェクトの既定路線は「分散を最初から入れない」で一貫している。

**小結**: 本選はスケジューラ不要。大規模=直列(フル艦隊)、小規模パイロット=軽い並列。watchdog が信頼性を担保。

---

## 3. 推奨と判断基準

### 3.1 今すぐ要る最小限(本選・単一機)

1. **7 本の vLLM を本選機に起動**(ops §2-A、`CUDA_VISIBLE_DEVICES=i` でポート 800i×7)。→ **実機での疎通確認 = `scripts/bench.py --backend vllm --servers ...`**(ops §4)。これが唯一の「新規に確認すべきサーバー作業」。[コードは完成済み・要実機検証]
2. **watchdog 経由で長時間ラン**(`observer.checkpoint_every` を 72〜144 に設定)。落ちても自動再開。[完成済み]
3. **バッチで analyze/export/viewer**。成果物は自己完結 HTML + UE 用 JSON。[完成済み]
4. (任意)**リモート監視**が要れば `status.json` を tail、**HTML 配布**が要れば `python -m http.server`。フル API/DB は入れない。[コード不要]

### 3.2 将来あると良い(本選クリティカルではない)

- **薄いジョブランナー/キュー**: 将来「複数ノードで多数掃引を無人運用」する段になったら。今は run_sweep + watchdog で十分。
- **ライブ進捗ダッシュボード**: `status.json`/`watchdog.log` を読む静的ページ。リモート監視が実際に苦痛になってから。
- **外部 storage(Redis/pgvector)**: in-process 構造(relations/posts)が有界化で足りなくなったら(scale-audit は既に config cap で有界化済み=B6/B7)。**スケールの後段レバーであって本選要件ではない**。

### 3.3 過剰投資の戒め

- **分散 actor(Ray)/Slurm/Kubernetes/マイクロサービス**は「本選=1 ノード・1 本の支配的ラン」には無用の問題解決で、**10日しかない本選の開発日を溶かす**。入れない。
- シミュ本体の **API サービス化**も同様(2.2)。計算は変わらず障害面だけ増える。
- 可視化の**ストリーム配信サーバ**(2.3)。自己完結 HTML の方が本選デモに強い。

### 3.4 トレードオフ表(コスト/再現性/本選デモ/開発速度)

| 軸 | (A) 現状: 単一機・バッチ ★推奨 | (B) 常駐サービス/API 化 | (C) クラウドGPU 常用 | (D) 分散スケジューラ |
|---|---|---|---|---|
| **コスト** | 本選機無償・追加ゼロ | 開発工数(サービス+運用)。本選機は無償のまま | 従量課金(§3.5)。本選機無償を捨てる合理性なし | 開発工数大。単一ノードでは無益 |
| **再現性** | キャッシュ+checkpoint で完全。**k\* を1か所生成** | サービス層はキャッシュに無関与=不変だが、投入経路のバグ余地増 | キャッシュは移設可だが初回揺れ→本データは分散させない | ノード間の順序・スケジューリングが再現性の敵(distributed-actor 注記) |
| **本選デモ** | 自己完結 HTML + UE 再生。オフライン・ポータブル | ライブ投入を見せられるが、100日ランは即時に映えない | デモ内容は変わらない | 変わらない(裏方) |
| **開発速度** | 追加ゼロ。残作業=実機疎通のみ | 遅くする(新規実装+デバッグ) | 環境構築・egress で目減り | 最も遅い(本選日程に不整合) |

### 3.5 クラウドを使う場合の概算費用レンジ(要検証)

前提: 本選機は**無償**なので、以下は**リハーサル/フォールバックの予算感**。7GPU 相当を借りる想定。
所要時間は **scale-audit §3.3 の「10k体で ~3〜5日、30k体で ~7〜12日」= 未実測の仮定**に線形依存(トークン/秒が未計測)。**費用は所要時間の仮定ごと動くので必ず bench 実測後に見直す**。

主要 GPU の従量単価(**2026 年中頃・変動あり・要公式再確認**):

| GPU | VRAM | 単価/時(概算) | 出典 |
|---|---|---:|---|
| RTX A5000(本選機に近い) | 24GB | **$0.27**(RunPod Community) | RunPod 公式(下記) |
| RTX A6000(A5000 の 48GB 版・同 Ampere) | 48GB | **$0.49**(RunPod Community)/ $0.80(Lambda) | RunPod 公式 / 🔶Lambda 集計 |
| A40 | 48GB | **$0.44**(RunPod Community) | RunPod 公式 |
| L40S | 48GB | **$0.99**(RunPod Community) | RunPod 公式 |
| A100 80GB | 80GB | **$1.39〜1.49**(RunPod)/ $2.49(Lambda) | RunPod 公式 / 🔶Lambda 集計 |
| H100 | 80GB | 🔶$2.49〜3.29(Lambda) | 🔶二次集計 |

> ⚠️ RunPod の値は **Community Cloud**(安価層)。**Secure Cloud はおよそ2倍**(🔶northflank 二次)。spot/community は**プリエンプト**され得る。

**1 ラン(10k体・100日)の概算**(7 枚×単価×壁時計時間。壁時計 **~5日=120時間**は仮定・要検証):

- 7×A5000 @ $0.27 = $1.89/時 → 120時間 ≈ **$227/ラン**(A5000 のクラウド在庫は少なめ=要確認)
- 7×A6000 @ $0.49 = $3.43/時 → 120時間 ≈ **$410/ラン**
- 7×L40S @ $0.99 = $6.93/時 → 120時間 ≈ **$830/ラン**(A5000 より高速な可能性→時間短縮で相殺され得る=要 bench)
- 7×A100 80GB @ ~$1.45 = $10.15/時 → 120時間 ≈ **$1,220/ラン**(80GB なら少ない枚数で大モデルも可)

> これらは**単一ランのオーダー**。掃引(modes×seeds)本数で乗算。30k体は所要 ~1.5〜2.4倍。**egress**(結果 15〜90GB)課金の事業者あり(Lambda は無料)。**すべて仮定依存の桁——確定値ではない**。

---

## 4. 出典

**リポジトリ内(一次・根拠の中心)**
- `docs/ops-production.md`(vLLM 艦隊・3構成・キャッシュ規律・watchdog 手順)
- `docs/research/scale-audit-100days.md`(規模・呼数・所要時間・RAM 破綻点)
- `docs/research/llm-model-selection.md`(A5000=Ampere・FP8 不可・量子化)
- `docs/lit/shibuya_sim_infra_summary.md`(GPU 配置・時間スケール・VRAM 防衛)
- `docs/lit/infra__storage-routing.md`(sticky routing / prefix cache ~96% / storage 選択肢=判断材料)
- `docs/lit/engine__distributed-actor-overview.md`(actor/分散=器であり過剰の戒め)
- `docs/research/3d-visualization.md`(UE/PLATEAU/Web3D 可視化経路)
- `docs/AUTOMATA第2回ハッカソン案.md`(本選=168GB・7台クラスタ・10日)
- 実装: `src/society/llm/{vllm,fleet,cache}.py`、`src/society/engine/checkpoint.py`、`scripts/{run,run_sweep,watchdog,bench,analyze,export_ue,export_3d}.py`、`viz/make_viewer.py`、`conf/config.yaml`

**クラウド価格(外部)**
- [Runpod GPU Cloud Pricing(公式)](https://www.runpod.io/pricing) — A5000 $0.27 / A6000 $0.49 / A40 $0.44 / L40S $0.99 / A100 PCIe $1.39 / A100 SXM $1.49(Community Cloud、2026-07 取得)
- [Lambda AI Pricing(公式)](https://lambda.ai/pricing) — A6000 $0.80 / A100 80GB $2.49 / H100 $2.49〜3.29(🔶数値は二次集計経由・公式で要再確認)
- 🔶 二次(相対比較のみ): [Northflank: Runpod pricing breakdown](https://northflank.com/blog/runpod-gpu-pricing)(Secure Cloud ~2倍)、[ComputePrices: Lambda](https://computeprices.com/providers/lambda)

> 価格は変動が激しい。**採用時は各公式ページで再確認**。所要時間は本選機で `scripts/bench.py` により実測してから費用を再計算すること(ops の方針=未測定値を書かない)。
