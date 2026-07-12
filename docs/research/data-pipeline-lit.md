# データパイプライン設計 — 文献調査と自プロジェクト棚卸し

作成: 2026-07-10 / 担当: リサーチ(コード変更なし・読み取りのみ)

## この文書の目的

ユーザーの問題意識:

> シミュレーションで得たデータを「ただプロットする」のではなく、処理して有効なデータにするべきでは。
> また、生データは一番基礎的な事項のみの記録でよいのでは。どちらの方式が良いか文献で調べ、処理方法も考えてほしい。

結論を先に一言でいうと——**「生イベントは最小・正準で持ち、指標は後処理で導出する」方式が文献の主流であり、本プロジェクトは既にほぼその設計になっている**。ただし例外として「イベントに現れない連続内部状態(drive ゲージ・theta_drift・地位合成値など)」だけは後処理で復元できないため、そこは in-sim 集計(L2)かスナップショット(L3)が必然的に必要になる。以下、文献の裏付けと自プロジェクトの現状マップ、非復元状態量の具体、処理手法カタログを示す。決定(何を採用するか)は Fable が行う前提の「素材」である。

---

## 文献サーベイ

### 1. シミュレーション出力解析の標準(Law & Kelton 系)

離散事象シミュレーションの出力は「1本の生ログをそのまま眺める」のではなく、**統計的な後処理**を経て初めて意味を持つ、というのが Law & Kelton 以来の標準的立場。要点:

- **warm-up(過渡期)除去 / 初期化バイアス**: 定常状態を測るなら、初期条件依存のバイアスがかかる冒頭区間を切り捨てる(truncation)。Law & Kelton は移動平均(窓幅 w)でグラフが滑らかになる最小の切捨点を選ぶ手続きを推奨。信頼区間幅を最小化する truncation rule も知られる([WSC15 統計出力解析](https://www.informs-sim.org/wsc15papers/188.pdf)、[warm-up 検出手法の評価](https://www.researchgate.net/publication/4111771_Evaluation_of_Methods_Used_to_Detect_Warm-Up_Period_in_Steady_State_Simulation))。
- **複数レプリケーション**: 乱数シードだけを変えた独立反復を複数回走らせ、レプリケーション間で平均・分散を取って**信頼区間**を出す。1本の長ランから区間推定する場合は batch means 法。逐次法(必要精度に達するまでレプリケーションを追加)も標準([Arena: steady-state & warmup](https://info.arenasimulation.com/blog/steady-state-and-warmup)、[定常状態出力解析手法の性能評価](https://www.sciencedirect.com/science/article/pii/S037704271630019X))。
- 含意: **単一ランのプロットは点推定ですらない**。k を掃引して相転移点 k* を探す本プロジェクトでは、各 k で複数シード反復し「seed 発散」と信頼区間を出すことが前提になる。

### 2. ABM のデータ管理・報告の標準(ODD / ODD+D)

社会・生態系 ABM の記述標準は **ODD プロトコル**(Overview, Design concepts, Details)。2020 年に第2次更新([Grimm et al. 2020, JASSS 23(2)7](https://www.jasss.org/23/2/7.html))。再現性のための「モデル記述の lingua franca」で、CoMSES/OpenABM がモデル+コードの寄託標準を運用([CoMSES standards](https://www.comses.net/resources/standards/))。人間の意思決定・学習・適応を明示する拡張が **ODD+D**([Müller et al. 2013, Environmental Modelling & Software 48:37-48](https://www.sciencedirect.com/science/article/abs/pii/S1364815213001394))。

- 本プロジェクトへの含意: 何を記録し何を後処理で出したかは **再現可能な記述(ODD の "Observation" 節に相当)** として固定すべき。schema.py の register 制はまさにこの「観測契約」の実装。実験そのものの記述標準(warm-up/レプリケーション数/シード)も ODD が要求する。

### 3. 生ログ最小 + 後処理 vs シミュ内集計 の設計比較

このトレードオフは複数分野で同型の議論がある。

- **event sourcing(ソフトウェア設計)**: 現在状態を保存せず、**追記専用(append-only)のイベント列**だけを正とし、状態は必要に応じてイベントを replay して導出する。派生ビュー(read model / projection / materialized view)はいつでも捨てて作り直せる。Martin Fowler の "Complete Rebuild":アプリ状態を全部捨ててログの再処理だけで再構成できる。要件が変わったら**過去イベントに新ロジックを当てて新指標を遡及計算**できる([Azure: Event Sourcing pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing)、[event-sourcing.html](https://arkwright.github.io/event-sourcing.html))。→ これは「生最小+後処理」方式そのもの。
- **tidy data(Wickham 2014)**: 分析可能な整形データは「各変数=列、各観測=行、1セル1値」。**生データ(raw)と分析準備済みデータ(analysis-ready)を分ける**のが標準で、分析準備済みは tidy 形式のプレーンテキスト/列形式が望ましい。時系列指標は「時間窓での集計(events per second 等)」で生イベントから作る派生物と位置づけられる([Tidy Data](https://vita.had.co.nz/papers/tidy-data.html))。
- **in-situ vs post-hoc(HPC シミュレーション)**: エクサスケールでは生データを全部ディスクに書けないので、**in-situ**(生成と同時にメモリ上で解析・削減)と **post-hoc**(全生データを保存して後で解析)を対比。多くのチームは**ハイブリッド**——in-situ で統計量・等値面など削減データを作りつつ、**選択したタイムステップの生データだけ残して**後処理する([In-situ vs post-hoc の比較](https://cdux.cs.uoregon.edu/pubs/KressISC.pdf)、[ECP ALPINE](https://www.diva-portal.org/smash/get/diva2:1907161/FULLTEXT01.pdf))。→ 「生は最小、状態量は間引きスナップショット、集計は後処理」というのは HPC でも実務解。
- **共通する結論**: 生は**正準・最小・追記専用**にし、指標は**再計算可能な派生ビュー**として後処理で作る。ただし *再構成に必要な生を落としてはいけない*(replay できなくなる)。HPC が「一部タイムステップの生データは残す」のは、in-situ でしか取れない状態を post-hoc 復元できないため——本プロジェクトの L3 スナップショットと同じ役割。

### 4. LLM エージェント社会シムの記録・後処理(公開情報の範囲)

- **Generative Agents(Park et al. 2023)**: 中核は **memory stream**——エージェントが知覚したすべてを自然言語で**タイムスタンプ付き追記ログ**にする。各記憶に recency(指数減衰)・importance(LLM 採点)・relevance(コサイン類似)を付け、**reflection** で生観測から高次の洞察を後段生成する([arXiv:2304.03442](https://ar5iv.labs.arxiv.org/html/2304.03442))。→ 記録は生観測の追記ログ、洞察は派生、という分離。ただし彼らの memory stream は「エージェントの認知入力」であって解析用データ層とは別物である点に注意(役割が違う)。
- **AgentSociety(Tsinghua FIB Lab 2025)**: 1万+エージェント・500万相互作用。検証は**シミュ出力と実データの突合**——radius of gyration(移動半径)、1日訪問地点数、行動意図分布などの**行動集約指標**を実測と比較([arXiv:2502.08691](https://arxiv.org/abs/2502.08691))。→ 記録した生軌跡から**移動統計を後処理で導出**して現実照合する流儀。本プロジェクトの observe.py / calibrate_report.py と同型。
- **Project Sid(Altera 2024)**: 10〜1000+ エージェントの Minecraft 文明。PIANO アーキテクチャで複数認知モジュールを並列。役割分化・統治・文化伝播などの**創発を事後計測**([arXiv:2411.00114](https://arxiv.org/abs/2411.00114))。記録スキーマの詳細は論文では限定的(**不明**)。
- **方法論レビュー**: LLM×ABSS の機会と課題を JASSS 投稿でレビュー([arXiv:2507.19364](https://arxiv.org/html/2507.19364v1))、再現性のための設定管理(EASE)提案([arXiv:2605.30258](https://arxiv.org/pdf/2605.30258))。→ LLM 社会シムでは**再現性(シード・設定・プロンプト版)の固定**が中心論点になっている。
- 総じて公開情報の範囲では、これらは「生の相互作用/軌跡ログ + 後処理の集約指標(移動・拡散・分極)」という構図。**各社が正確に何列を生で持つかの詳細スキーマは大半が非公開**(不明と明記する)。

### 5. 早期警戒シグナル(EWS)/ 相転移検知 — 既存資産との接続

k* 探索の三角測量のうち EWS は Dakos/Scheffer 系が一次ソース。臨界遷移の手前で **critical slowing down** により**分散と lag-1 自己相関が上昇**する。ガウシアン detrend → 移動窓で分散/AC1 → Kendall τ でトレンド検定、が標準手順([Scheffer et al. 2009, Nature](https://www.nature.com/articles/nature08227)、[Dakos et al. 2012, Ecology(頑健性)](https://esajournals.onlinelibrary.wiley.com/doi/10.1890/11-0889.1))。→ 本プロジェクトの `measure.ews()` はこの手順の自作実装で、**文献手法に忠実**(後述)。

---

## 自プロジェクトの記録層マップ

sim 本体は「起きたことを記録するだけ」で、測定・集計は事後にログから行う、という frame 分離が明示されている(`observer/logger.py` docstring)。層構成:

| 層 | ファイル/出力 | 内容 | 記録の性格 |
|---|---|---|---|
| **L1** | `l1_events.parquet` | 生イベント。固定列 `step, sim_min, agent_id, kind, x, y, payload(JSON), rng_stream, llm_call_id`。約130種の kind を `schema.py` に register 制で登録 | **追記専用・正準**(event sourcing の event store) |
| **L1b** | `l1b_llm.parquet` | LLM 呼び出し台帳。行=`{llm_call_id, agent_id, purpose, step, cached}` | 追記専用・計算資源監査 |
| **L2** | `l2_metrics.parquet` | **毎 step 1 行の集計指標**。`aggregate.py` の AGGREGATORS(約40列)を `collect(sim)` で in-sim 計算 | **シミュ内集計**(in-situ 集約) |
| **L3** | `l3_snapshots.parquet` | `snapshot_every` step ごとの全 agent 状態(JSON)。id,x,y,node,loc,sleeping,building,floor,activity,money,opinion,states,adopted(+ON時 theta_drift/account/arousal/status) | **間引きスナップショット**(状態の直接保存) |
| summary | `summary.json` | ラン全体の要約(n_agents, n_steps, n_events, event_kinds 件数, llm_calls, cache_hits, n_items, n_transmissions, total_adoptions) | 集計スナップ |
| config | `config.yaml` | 再現用の全設定(save_config) | 再現性 |
| meta | `agents.json` / `traits.json` | 個体メタ・因子(Y~traits 回帰の説明変数、状態初期値) | 静的入力 |

### 記録の性格:「生で持つ / シミュ内集計 / 後処理で導出」

- **生で持っている(L1)**: 移動(route_start/move_segment/arrive/stay)、入退館、睡眠(sleep_start/wake_up)、会話(speak/hear/dm)、SNS(sns_post/read/like/reshare)、伝播系譜(transmission=誰→誰・どのチャネル。`provenance.py`)、造語・採用(vocab_coin/label_coin/label_adopt/vocab_use)、内省(reflect)、金銭(wage/spend/rent/tax/withdraw/venture_sale…)、**状態更新(state_update=name,old,new,cause)**、意見更新(opinion_shift=source,old,new)、覚醒(affect_update)、健康(health_update)、ツール(event_host/group_found/proposal/venture…)ほか。
  - 重要な設計上の性質: **`factors/update.py` の `_bump()` が全 state 変化の唯一の通過点で、変化のたびに old/new/cause を state_update イベントに書く**(`agent-implementation-summary.md` に「全変更が state_update イベントに記録=因果分解可能」)。opinion/arousal/fatigue も同様に old/new を都度ログ。→ **これらの内部状態は event-sourced であり、初期値(agents.json)+イベント replay で完全復元できる。**
  - ただし L1 は「最小」ではなく **文脈をリッチに載せている**(例: vocab_coin の payload に fire_reason/drive/place/company_ids/saw_feed/adopted_n/recent_mem を同梱=自然造語の観察のため。norm_digest は既に日次集計済みの値を載せる)。→ 純粋な「基礎事項のみ」ではなく**半加工の生ログ**。
- **シミュ内で集計(L2)**: 毎 step の人口カウント(n_moving/n_sleeping/n_working/n_outside/n_inside/n_cars)、累積カウント(n_items/total_adoptions/n_likes/n_reshares/ツール各種)、**連続内部状態の平均**(mean_grievance/mean_drive/mean_money/mean_theta_drift/opinion_var/opinion_extremity/status_gini…)、崩壊検知(speech_diversity/belief_diversity/speech_pairwise_var)。
- **後処理で導出(スクリプト群、すべて L1 を読むだけ)**:
  - `observer/measure.py`(純関数): agent_features(Y_external/内訳/ツール効果/Y_composite)、item_cascades(size/depth/t_half/channel_mix)、network_windows(会話グラフの次数・クラスタ・中心性 churn)、collective_series、**ews()**(Dakos 手順)、r2_traits(Y~traits の OLS R²)、drift_metrics(語形/文脈の分岐)、communities(label propagation)。
  - `scripts/analyze.py`: 上記を束ね JSON+図+report.md。
  - `scripts/observe.py`: 訪問(POI/建物/ノード)・興味(drive reason/spend/検索/採用語)。0件は正直に明記(捏造禁止)。
  - `scripts/observe_flows.py`: 金流 Sankey・注意ネットワーク(gini・相互注意)。payload フィールド名を実データで確認済みと明記。
  - `scripts/calibrate_report.py`: 現実一次統計との近似バンド照合(睡眠・労働・経済・事件率)。

### L2 各列は L1 から再導出可能か(冗長判定)

| L2 列 | L1 から再導出? | 根拠 |
|---|---|---|
| n_items / total_adoptions / distinct_vocab_in_use | **○ 冗長** | vocab/label_coin・label_adopt の累積 |
| n_likes / n_reshares | **○ 冗長** | sns_like / sns_reshare の累積 |
| n_cars | **○ 冗長** | traffic_flow.payload.n |
| n_drive_requests / n_fires | **○ 冗長** | drive_request(件数 / granted=True 件数) |
| n_events_hosted / n_event_attend / n_flyers / n_groups / n_proposals / n_ventures / n_institutions | **○ 冗長** | 対応ツールイベントの累積 |
| mean_grievance / mean_collective_efficacy | **○ 復元可**(要初期値) | states は state_update で old/new を都度記録=event-sourced |
| opinion_var / opinion_extremity | **○ 復元可**(要初期値) | opinion は opinion_shift で old/new 記録(shift が唯一の mutator である限り) |
| mean_money / n_broke / mean_account | **○ 復元可**(要初期値・重い replay) | wage/spend/rent/tax/withdraw/venture_sale + agents.json 初期額 |
| n_sleeping / n_outside / n_inside_buildings / n_moving / n_working | **△ 状態 replay で可** | sleep/wake・enter/exit_area・enter/exit_building・route/arrive を再生。working は明確な開始終了イベント対が弱く近似 |
| speech_diversity / belief_diversity / speech_pairwise_var | **△ 近似可** | speak.text / reflect.belief から復元。ただし「その step 時点の said 末尾」は replay 依存で厳密一致は要注意 |
| n_face_fires / n_replies | **△** | drive/返答の内部カウンタ。llm_deliberate.trigger や L1b.purpose から近似 |
| n_active_rules | **△** | institution_rule + rule_expired/repealed の再生で可 |
| n_sns_posts | **✗**(窓依存) | `len(net.posts)` はエイジアウトする生存バッファ数。累積ではなく時点窓なので L1 から厳密復元不可 |
| **mean_drive** | **✗ 非復元** | drive ゲージは毎 step 減衰・蓄積する連続量。値は drive_request 時のみ・当該 drive のみ記録。全員の毎 step 平均は取れない |
| **mean_theta_drift** | **✗ 非復元** | theta_drift は毎 step `+=Δ` と自発回復 `-=rate*θ` で動くが**変化イベントを一切吐かない**。L2/L3 でしか観測できない |
| **status_gini / status_top10_share / status_rank_mobility** | **✗ / △** | status は日次再計算の合成値。rank_mobility は前日 rank に依存(状態を持つ)ため L1 単独では不可 |

→ **要約: L2 の大半は L1 から再導出可能(冗長)であり、event sourcing の projection として後処理に回せる。真に L2/L3 が必要なのは「イベントに変化点を持たない連続内部量」= drive・theta_drift・status(合成/移動性)と、窓依存の n_sns_posts のみ。**

---

## 生最小 vs 加工重視 の比較表

「生イベント最小 + 派生指標は後処理」対「シミュ内で集計済み指標を吐く」の設計比較(本プロジェクト文脈)。

| 観点 | (A) 生最小 + 後処理(event sourcing 型) | (B) シミュ内集計を吐く(in-situ 型) |
|---|---|---|
| 再現性 | ◎ 生ログ+シード+config で完全 replay・完全 rebuild 可 | ○ 集計値は残るが、集計ロジックのバグ発覚時に遡及修正が難しい |
| 新指標の遡及計算 | ◎ 過去ランの生ログに新ロジックを当てて後から計算可 | ✗ 吐かなかった指標は再ラン必須 |
| ストレージ | △ イベント数が多いと肥大(要圧縮・セグメント化) | ◎ step×列で小さい(L2 は1ラン数十列×step) |
| 後処理コスト | △ 大規模ランで replay が重い(measure.py は列射影+逐次読みで緩和済み) | ◎ 実行時に一度計算するだけ |
| in-situ でしか取れない状態量 | ✗ **連続内部量は復元不能**(drive/theta_drift/status) | ◎ その瞬間の内部状態を直接読める |
| 数値決定性 | ◎ 後処理は純関数・決定論(measure.py) | ○ ただし浮動小数の round 時点が固定される |
| 実装保守 | ◎ sim 本体を汚さず観測を足せる(疎結合) | △ 新指標ごとに sim 内 aggregator を触る(ただし register 制で緩和) |
| スケール(1万人×100日) | △ 生ログ I/O とメモリがボトルネック | ◎ 事前集計で下流を軽くする |

**含意(本プロジェクト向けの読み)**: 本プロジェクトは既に **ハイブリッド**(HPC の実務解と同型)。L1=生ログ(event store)、observe/analyze=projection、L2=in-situ 集約、L3=間引きスナップショット。ユーザーの直観「生は基礎事項のみ+処理して有効化」は方向として正しく、**大半の L2 列は原理上 L1 から後処理で作れる=冗長**。ただし L2 を全廃すると drive/theta_drift/status の観測窓を失うので、**「連続内部量だけを L2/L3 に残し、再導出可能な集計は後処理へ寄せる」**のが文献整合的な落としどころ(決定は Fable)。

---

## 再構成不能な状態量(自プロジェクトの具体)

「イベント列から状態を replay しても復元できない量」= in-situ でしか取れないもの。本プロジェクトでの具体:

1. **drive(欲求ゲージ)** — `agent.drive` は毎 step 減衰(`decay: 0.02`)・抽選落ちで `fail_decay: 0.30` 減衰・蓄積する連続量。ログに出るのは `drive_request`(申請時、当該 drive の閾値近傍)だけで、**全員の毎 step ゲージ値は記録されない**。→ `mean_drive`(L2)でしか観測できない。
2. **theta_drift(内省ドリフト、緩変数)** — `cognition/drive.py` で毎 step `theta_drift += Δ`(馴化+/鋭敏化−)と自発回復 `theta_drift -= recovery_rate*theta_drift`。**変化イベントを一切吐かない**。→ `mean_theta_drift`(L2, ON時)/ L3 スナップショット(drift_on 時)でしか観測できない。
3. **status(社会的地位、合成値)と rank_mobility** — status は他量から日次再計算する合成スコア。`status_rank_mobility` は前日 rank との差=**状態依存**。→ L1 単独では不可。
4. **n_sns_posts(生存中の投稿バッファ数)** — エイジアウトする時点窓の量で累積ではない。→ L1 の sns_post からは厳密復元不可。

**逆に、復元可能な内部状態**(=イベントに old/new を都度書いているため):`states`(grievance/efficacy/ownership/collective_efficacy…)、`opinion`、`arousal`、`fatigue/mental`、`money/account`、位置・睡眠・入退館、`adopted` 語彙。これらは L3 スナップショットに載っていても**原理上は L1 replay で再構成できる**(L3 は速度/検証のための冗長コピー)。

→ 設計判断の核心: **「L3 スナップショットに載せる価値が高いのは、復元可能量の検証用コピーではなく、上記 1–4 の非復元量」**。もし L1 を真に最小化するなら、drive/theta_drift 等に「変化イベント(あるいは低頻度の専用スナップ列)」を足すか、L3 の対象を非復元量に絞るのが筋(実装判断は Fable)。

---

## 処理手法カタログ(推奨素材。採用は Fable が決定)

「ただプロットする」から「処理して有効なデータにする」ための手法。既存資産との接続を併記。

### A. 実験設計・前処理(Law & Kelton 系)
- **warm-up 除去**: 冒頭の過渡期(街の起動〜生活リズム安定まで)を切り捨ててから定常統計を取る。本プロジェクトは 1 step=10 分・144 step/日なので「最初の N 日」を warm-up とする運用が素直。切捨点は移動平均でリズム系列(n_sleeping 等)が周期定常化する点、または truncation rule。
- **複数レプリケーション + 信頼区間**: 各 k で**シードのみ変えた反復**を複数走らせ、レプリケーション間で平均・分散・信頼区間。`rng.py`/`hub.stream` の stream 分離があるので**シード統制は既に可能**。`run_sweep.py`/`analyze_sweep.py` が掃引の受け皿。
- **単位の tidy 化**: 現状 observe 系は用途別 JSON。相互比較には「1行=(run, seed, k, day/window, metric, value)」の **long-format tidy table**(Wickham)を1枚作ると下流(信頼区間・回帰・作図)が一様に扱える。

### B. 時系列集計・要約
- **日次/週次集計**: L2 の step 系列を 144 step=1日 で畳む(calibrate_report.py が既に `_daily_series` で実施)。曜日効果・週次トレンドの分離。
- **人口リズム**: n_sleeping/n_working/n_moving の日内プロファイル(observe.py の hour_trend と接続)。
- **累積 vs 増分の明確化**: 累積カウント列(n_likes 等)は差分して「per step 発生率」に直すと EWS/変化点にかけやすい。

### C. 変化点検出・早期警戒(k* 三角測量の核)
- **EWS(Dakos 手順)**: 分散↑・lag-1 自己相関↑を Kendall τ で。**既に `measure.ews()` に実装済み**(ガウシアン detrend→移動窓→τ)。適用先を adoption_frac/vocab_entropy 以外(mean_grievance, opinion_var, status_gini など)にも広げる余地。
- **seed 発散**: 同一 k・異シード間で最終指標(Y 分布、adoption_frac)の分散が急増する k を探す=相転移の別測度。レプリケーション設計(A)と直結。
- **R²(k) 低下**: `r2_traits()` の Y~traits R² を k ごとに出し、説明力が崩れる点を探す(研究の主測度)。extra_targets で Y_composite にも対応済み。
- 注意: EWS は false positive が出るため、**分散・AC1・seed 発散・R² 低下の複数指標の合致**で相転移と判断する(Dakos の頑健性論文が単一指標の弱さを指摘)。

### D. ネットワーク指標
- **会話/注意/金流グラフ**: network_windows(次数・クラスタ係数・中心性 churn)、observe_flows(注意 gini・相互注意、金流 Sankey)を時間窓で。中心性の churn 上昇や gini 上昇を集団構造の相転移シグナルとして EWS にかけられる。
- **コミュニティ検出**: `communities()`(決定論 label propagation)で下位集団を出し、drift_metrics で語形/文脈のコミュニティ間分岐(方言化)を測る。

### E. カスケード・拡散
- item_cascades(size/depth/t_half/channel_mix)+ adoption S字曲線(analyze.py)。t_half・depth の分布で「バイラル/緩慢」を分類。complex contagion は transmission 系譜(provenance)から木を再構成して検証。

### F. 因果に踏み込む場合の注意
- **シード統制**: 介入(k や scenario_shock)の効果を測るなら、**介入群と対照群で同一シード**にして共通乱数(CRV)で分散を抑える。`llm_null`(内容非結合ダミー呼び出し)や controls_mode が既に対照設計の足場。
- **交絡**: LLM 温度・キャッシュヒット率(L1b)が結果に効くので、比較ランでは model/temperature/prompt 版を固定し config で記録(ODD の再現性要件)。
- **多重比較**: 多数の指標×多数の k を検定すると偽陽性が増える。事前登録的に主測度(R²(k) 低下)を決め、他は探索的と明示。

### G. データ管理・再現性
- **生ログは正準・追記専用のまま維持**(event sourcing)。派生(observe/analysis 出力)は「いつでも捨てて作り直せる projection」と割り切る。
- **run manifest**: 各ランに (git hash, config, seed, model, prompt 版, warm-up 設定) を1枚で残す(EASE/ODD 整合)。summary.json を拡張する余地。
- **スケール**: measure.load_events は列射影+RecordBatch 逐次で peak メモリを抑制済み。1万人×100日では L1 の row-group 分割・列志向クエリ(pyarrow/duckdb)で「必要列・必要期間だけ」読む後処理に寄せると replay コストを緩和できる。

---

## まとめ(素材としての示唆)

- 文献の主流(event sourcing / tidy data / HPC ハイブリッド / ABM の ODD)はいずれも**「生は正準・最小・追記専用、指標は再計算可能な派生」**を支持。ユーザーの直観は正しい。
- 本プロジェクトは既にこの型。**L2 の大半は L1 から後処理で再導出可能(冗長)**で、真に in-sim が要るのは drive・theta_drift・status・n_sns_posts の少数。
- したがって現実的な設計選択は「L1 を(必要なら)基礎事項寄りに整理しつつ、**非復元の連続内部量だけを L2/L3 に残し**、集計・指標は後処理(measure.py/observe 系)に寄せる」。決定は Fable。
- 「処理して有効なデータに」の具体は上記カタログ(warm-up 除去→日次集計→複数シード信頼区間→EWS/変化点/R²(k) の多測度合致→tidy long-format で束ねる)。

---

## 出典

一次ソース優先。アクセス日 2026-07-10。

**シミュレーション出力解析**
- Law & Kelton 系: [統計出力解析(WSC15)](https://www.informs-sim.org/wsc15papers/188.pdf) / [warm-up 検出手法の評価](https://www.researchgate.net/publication/4111771_Evaluation_of_Methods_Used_to_Detect_Warm-Up_Period_in_Steady_State_Simulation) / [定常状態出力解析手法の性能評価(ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S037704271630019X) / [Arena: steady-state & warmup](https://info.arenasimulation.com/blog/steady-state-and-warmup)

**ABM 記述・再現性標準**
- ODD 第2次更新: [Grimm et al. 2020, JASSS 23(2)7](https://www.jasss.org/23/2/7.html) / [補遺 S1](https://www.jasss.org/23/2/7/S1-ODD.pdf)
- ODD+D: [Müller et al. 2013, EMS 48:37-48(ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S1364815213001394) / [PDF(ETH)](https://ethz.ch/content/dam/ethz/special-interest/usys/ites/ecosystem-management-dam/documents/EducationDOC/EM_DOC/Recommended%20readingDOC/Muller_2013.pdf)
- 寄託標準: [CoMSES Net standards](https://www.comses.net/resources/standards/)

**設計パターン(生最小 vs 集計)**
- event sourcing: [Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing) / [event-sourcing.html(Fowler 系解説)](https://arkwright.github.io/event-sourcing.html)
- tidy data: [Wickham, Tidy Data](https://vita.had.co.nz/papers/tidy-data.html)
- in-situ vs post-hoc(HPC): [Kress et al., in-situ 効率比較](https://cdux.cs.uoregon.edu/pubs/KressISC.pdf) / [ECP ALPINE(in situ + post hoc)](https://www.diva-portal.org/smash/get/diva2:1907161/FULLTEXT01.pdf)

**LLM エージェント社会シム**
- Generative Agents: [Park et al. 2023, arXiv:2304.03442](https://ar5iv.labs.arxiv.org/html/2304.03442)
- AgentSociety: [arXiv:2502.08691](https://arxiv.org/abs/2502.08691) / [GitHub](https://github.com/tsinghua-fib-lab/AgentSociety)
- Project Sid: [arXiv:2411.00114](https://arxiv.org/abs/2411.00114)(記録スキーマ詳細は非公開=不明)
- レビュー/再現性: [LLM×ABSS レビュー(JASSS 投稿, arXiv:2507.19364)](https://arxiv.org/html/2507.19364v1) / [EASE 設定管理(arXiv:2605.30258)](https://arxiv.org/pdf/2605.30258)

**早期警戒シグナル / 相転移**
- [Scheffer et al. 2009, Nature 461:53-59](https://www.nature.com/articles/nature08227) / [Dakos et al. 2012, Ecology(分散・AC1 の頑健性)](https://esajournals.onlinelibrary.wiley.com/doi/10.1890/11-0889.1)

**自プロジェクト内部参照(コード/ドキュメント)**
- `src/society/observer/logger.py`(L1/L1b/L2/L3・frame 分離・セグメント化) / `schema.py`(register 制イベント約130種) / `aggregate.py`(L2 aggregator 約40列) / `measure.py`(後処理純関数・ews/r2_traits/drift) / `provenance.py`(transmission 系譜)
- `src/society/engine/scheduler.py`(L2 collect・L3 snapshot 呼び出し) / `simulation.py`(summary.json)
- `src/society/factors/update.py`(`_bump`=全 state 変化を state_update に記録) / `cognition/drive.py`(theta_drift の非イベント更新)
- `scripts/analyze.py` / `observe.py` / `observe_flows.py` / `calibrate_report.py`
- `docs/agent-implementation-summary.md`(「全変更が state_update イベントに記録=因果分解可能」)
