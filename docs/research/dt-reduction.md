# Δt 短縮(10分 → 5分 / 1分 / 30秒)の実現可能性 — 呼数不変設計とコストの正直な見積り

> ステータス: **リサーチ報告(実装なし・src 変更なし)**。2026-08-12 作成。
> 発端: ユーザーの問い(§1 に原文)。
> 先行文書: [obs-u2-dt1min-design.md](obs-u2-dt1min-design.md)(第94バッチ設計調査)/
> `src/society/timeconv.py`(第79バッチ)/ [proposal-dp-u3-observe-250k.md](../plans/proposal-dp-u3-observe-250k.md)。
> 本文書はそれらを「呼数」「壁時計」「30秒の当否」の 3 点で更新・拡張する。

---

## 0. 3 行サマリ

1. **「Δt を細かくしても LLM 発火の機会は増えない」というユーザーの直感は、機構の 8 割について既に実装済みの事実**である(周期発火=分単位・朝計画/夜内省=per-day・予算=日次総量保存)。残る 2 割(per-step 抽選 1 本と、Δt=10 が構造的に潰していた驚き発火の解放)により、実測は ×1 でなく **×2.2〜2.4**(mock・12体)。ただしこれは予算 cap で天井が固定されており、per-day 宣言+機械固定テストで**設計上 ×1 に固定することもできる**(§4.1)。
2. **増えるのは LLM ではなくエンジンの壁時計**である。エンジンは毎 step 全員を走査する time-driven 構造なので、壁時計は step 数にほぼ線形。25万体では Δt=1 で **27.6〜52.2 h/シミュ日 = 実時間より遅い**(§4.5)。Δt=1 は 1〜2 万体の並行小ラン、本線 25万は Δt=10(または Δt=5)が現実解。
3. **30秒(Δt=0.5)は現行アーキテクチャの通貨と衝突する**。`run.dt_min` は「1440 の約数の正整数[分]」であり(`timeconv.py:626-632`)、認知イベントキューも L1 も**整数分**を時間通貨にしている。認知の基本周期は最短 1 分に丸められる(`fire.py:375-377`)ため、**1 分より細かくしても思考層は 1 ビットも変わらない**。30秒が効くのは移動の補間だけで、物理は既に 0.05 秒サブステップを持つ。**推奨の梯子は「本線 Δt=10 → 並行小ラン Δt=1 → (掃引条件として Δt=5)」で、30秒は見送り**(§4.4)。

---

## §1 問いの定式化

ユーザーの問い(原文):

> 「Δtについて、10分から1分に短縮しても、LLMの発火回数が増加しないよう工夫できないだろうか。現状の発火数を踏まえると、Δtを細かくしても発火の機会自体が増えるわけではないので、計算量は増加しないのではないか。また、現実の人間の思考や出来事の最小単位は10分よりも細かいはずで、1stepは最低でも5分、できれば1分、理想を言えば30秒にすべきではないか。」

3 つの主張に分解して検証する:

| # | 主張 | 本文書の判定 |
|---|---|---|
| T1 | LLM 発火回数を Δt に依存させない工夫は可能 | **可能**。機構の大半は既にそうなっており、残りも per-day 宣言+機械固定で閉じられる(§2.2, §4.1)。ただし現状実測は ×2.2〜2.4 で、その増分は「バグ」ではなく「Δt=10 が潰していた驚き発火の解放」= 科学的動機そのもの(§2.2) |
| T2 | 発火機会が増えなければ計算量は増加しない | **半分誤り**。LLM 計算量は増えない(cap で固定可能)が、**非 LLM エンジンの壁時計は step 数にほぼ線形**に増える(毎 step 全員走査の time-driven 構造)。25万体 Δt=1 は実時間より遅い(§2.3, §4.5) |
| T3 | 思考・出来事の最小単位は 10 分より細かい → 5分/1分/30秒にすべき | **1 分までは実装も文献も支持**(認知の基本周期 talking 2.0 分・Generative Agents はゲーム内 10 秒刻み)。**30 秒は現行の「整数分」通貨と衝突し、思考層の利得ゼロ**(認知周期は 1 分に量子化済み・物理は 0.05 s サブステップ既存)(§3, §4.4) |

---

## §2 現状機構の実測 — 何が step 数に比例し、何がしないか

### 2.1 Δt 正規化の完成度(`src/society/timeconv.py`)

- **正準 Δt=10 分**(`timeconv.py:53`)。`run.dt_min` が唯一の宣言点で、変換は `config.load_config` 末尾の 1 箇所(`src/society/config.py:251-253`)。Δt=10 では config を 1 バイトも触らない恒等パス(`timeconv.py:682-683`)= golden 担保。
- **5 分類**(`timeconv.py:24-38`): RATE(線形)/ PROB(べき変換)/ KEEP(残存割合のべき)/ STEPS(逆比例)/ INVARIANT(理由必須)。宣言テーブルは現在 **229 エントリ**(`timeconv.py:146-578`。第94時点の 130 キーから H1〜H5・所有権系で増加)。網羅性は CI が棚卸し正規表現で機械検査(`tests/test_timeconv.py`)。
- **PROB のべき変換の意味**(`timeconv.py:81-93`): p' = 1−(1−p)^(Δt/10) は**ハザード λ = −ln(1−p)/10 を保存する変換**。「10 分あたりに少なくとも 1 回起きる確率」が Δt に依らず不変で、Δt→0 で p'→λ·Δt に一致する。確率の線形スケールは合成で壊れる(p=0.35 を 0.035 にすると 10 step 通しで 0.30≠0.35。`timeconv.py:20-22`)。これは医療決定分析で標準の rate↔probability 変換と同一(§3.4)。
- **解析側(C級)は完了**: scripts 31 本は `scripts/run_dt.py` を単一の源に Δt 対応済み(第79〜101・W2-3/W4-C/W3-1)。残る Δt 直書きは src 側の**凍結観測定数**のみ(§2.5, §5)。

### 2.2 LLM 発火の機構 — 発火機会の Δt 依存性の全数表

**構成要素と粒度**(★= step 数に比例する箇所):

| 経路 | 粒度 | Δt=1 で機会が増えるか | 証拠(行番号) |
|---|---|---|---|
| 予算 cap `lod.max_llm_per_step` | **RATE = 日次総量保存**(300/step×144 = 30/step×1440 = 43,200/日) | **増えない**(天井そのものが不変) | `timeconv.py:197`・`src/society/cognition/lod.py:80-93`(LodBudget)・`src/society/engine/simulation.py:272-279`(cap 設定) |
| 朝計画 / 夜内省 | **per-day**(日境界フェーズ・予算外) | **増えない**(1 日 1 回のまま) | `src/society/engine/scheduler.py:933`(_phase_planning)・`:3692`(_phase_reflect_day) |
| 周期発火 periodic(cognition.fire ON) | **分**(較正表 `base_period[ctx].mean_min`・INVARIANT 宣言) | **増えない**(再予約は sim_min+分。世界 tick から独立) | `src/society/cognition/fire.py:355-381`(_period_min)・`timeconv.py:409-414`(period 系 INVARIANT 宣言+理由) |
| 驚き/内部/social 割込み | **イベント**(S>θ の閾値超え。1 人高々 1 個の分単位キュー) | **機会は増えない**が、**Δt=10 が構造的に潰していた発火が解放される**(下記) | `fire.py:157-217`(CogQueue)・`:163-164`(生きたイベント高々1個)・`:185-190`(advance は繰り上げのみ) |
| 対面会話の確定発火 | 共在×クールダウン(`conv_cooldown_steps` は STEPS = 実時間保存) | ほぼ増えない(実時間クールダウンが律速) | `scheduler.py:2519-2527`・`timeconv.py:257` |
| ★ 欲求ゲート後の per-step 抽選 | **毎 step Bernoulli**(p = `fire_weight`≈0.5。TABLE の網外) | **増える**(唯一の素朴な step 比例点)。ただし補正実測で呼数 244→231 とほぼ動かず = 主因ではない | `scheduler.py:2536-2549`(抽選)・`src/society/agents/agent.py:99`(fire_weight)・OBS-U2 §4 B6(判断待ち) |
| ★ 欲求ゲージの蓄積・減衰 | RATE/PROB 変換済み(閾値到達の実時刻は近似保存) | 近似的に増えない | `timeconv.py:181-192`(drive 系の宣言) |

**発火ゲートの本体**(`scheduler.py:2504-2513`): requesters = 「drive ≥ 実効閾値 かつ 不応期外」→ 抽選 → 予算。cognition.fire ON では「誰がこの tick に申請するか」を分単位キューが決める(`scheduler.py:2479-2506`)。LLM 呼の唯一の計上点は `llm_deliberate`(`scheduler.py:2330-2334`)。

**実測**(OBS-U2 §2(b)。mock・12体・1シミュ日・seed 42):

| 条件 | Δt=10 (144 step) | Δt=1 (1440 step) | 比 |
|---|---:|---:|---|
| LLM 呼数(既定) | 102 | 227 | **×2.23** |
| LLM 呼数(cognition ON) | 100 | 244 | **×2.44** |
| cog_fire 内訳 | periodic 997 / salience **0** | periodic 1,586 / salience **103** | — |
| L1 イベント総数 | 1,716〜2,628 | 6,296〜8,230 | ×3.1〜3.7 |

**★増分の正体は「機会の増加」ではなく「抑圧の解放」**である。CogQueue は 1 人につき生きたイベントを高々 1 個しか持たず、文脈別基本周期(talking 2.0 分 / walking 8.0 分)がどちらも 10 分より短いため、**Δt=10 では periodic が常に先に due になり salience 割込みが一度も表に出ない**(実測 0 件)。Δt=1 でそれが 103 件観測される。ユーザーの直感 T1 は「機会は増えない」という点で機構の設計意図と一致するが、**現状の実測が ×1 でないのは、Δt=10 の解像度がその設計を量子化誤差で覆い隠していたから**である。

### 2.3 エンジンコスト実測 — step 数に比例する唯一の大物

- **c ≈ 2.76×10⁻⁴ 秒/agent/step**(第102 の性能回収後。0.000311→0.000276 = −11%。`docs/log/devlog.md` Entry 101)。25万提案書は保守値 **c = 5.22×10⁻⁴** を採用(`docs/plans/proposal-dp-u3-observe-250k.md:168`。1万体深夜帯実測 0.000528 由来)。
- エンジンは毎 step 全フェーズが在場全員を走査する time-driven 構造なので、**壁時計 ≈ c × N × step 数**。step 数 10 倍はほぼそのまま壁時計 10 倍(試算は §4.5)。
- **物理(ゾーン内 SFM)は Δt 中立**: サブステップ数 n_sub = step_seconds / dt_sub を Clock から導出する(`src/society/physics.py:329-331`)ため、1 日あたりのサブステップ総数は 144×12,000 = 1,440×1,200 = **1,728,000 で不変**。屋内 SFM の積分刻み `indoor.sfm.dt` は INVARIANT 宣言済み(`timeconv.py:386`「社会レイヤー Δt と非同期」)。**「物理は細かい固定 tick・社会層は粗い tick」という分担は既に実装されている**。

### 2.4 L1 体積 — 毎 step 行と日次行の構成

| 出力 | 粒度 | Δt=1 での増分(実測) |
|---|---|---|
| `move_segment` | per-移動者 per-step | 240 → 2,655(×11) |
| `traffic_flow` | **1 行/step** | 144 → 1,440(厳密 ×10) |
| L2 metrics | **毎 step 1 行(無条件)** | ×10(`scheduler.py:5535` log_metrics) |
| L3 snapshot | STEPS 分類 = 実時間粒度保存 | **×1**(`timeconv.py:261`) |
| 日次イベント(給料・天候・計画・内省…) | per-day | **×1** |
| 会話・購買・遭遇などの行為イベント | per-event | ×1〜緩増 |
| **L1 総数** | 混成 | **×3.1〜3.7**(理論上限 ×10 に届かないのは大半が event-driven だから) |

観測間引きキー(`observer.flush_every_steps` / `cognition.channels.every_steps` 等)は**意図的に INVARIANT**(実験者の指定量)なので、Δt=1 では手動 ×10 が前提。これは `conf/smoke_dt1.yaml` が既にプロファイルとして固めている(同ファイル (d) 注記・:82-102)。

### 2.5 Δt=1 準備(OBS-U2)の到達点と残り

**到達点(第94〜99 で完了済み)** — OBS-U2 文書執筆時の「確定ブロッカー」は現在すべて解消している:

| 項目 | 状態 | 証拠 |
|---|---|---|
| resume 二重変換(B1・唯一の確定ブロッカー) | **根治済み** | `config.py:202-221`(`apply_dt: bool = True` 引数)・`scripts/run.py:109-115`(resume 経路で `apply_dt=False`) |
| A級直書き 7 件(分→step 換算・会計日境界・バス便・ACT-R 忘却…) | **Clock 化済み** | `scheduler.py:176-177`(A1)・`:3366-3370`(A2)・`:3444`(A6)・`src/society/world/transit.py:294`(A3)・`src/society/agents/memory.py:292-304`(A7: 正準 step 換算・Δt=10 恒等パス) |
| 物理サブステップ上限の Δt 追随(R7) | 第99 で是正済み | `zones.derive_max_sub_steps` |
| σ_c の Δt 来歴照合 | 検知のみ実装(WARNING+manifest) | OBS-U2 §2(d)・第99 `check_sigma_dt` |
| 解析 scripts 31 本+viewer の Δt 対応(C級) | **完了** | `scripts/run_dt.py` 単一源(W2-3/W4-C)・凍結側 norms/specialization は W3-1 |
| 並行小ランプロファイル(B5) | **存在する** | `conf/smoke_dt1.yaml`(dt_min:1・間引き×10・checkpoint 毎シミュ日) |

**残り(未完・判断待ち)**:

1. **σ_c の再測(R1・最重要)**: `data/calib/sigma_c.json` は Δt=10 の母集団で測った分散。per-step カウント量チャンネル(ext.heard 等)は Δt=1 で 1 step あたりが減るため σ_c が過大 → salience 発火が系統的に**過小**に出る(= 実測 103 件は下限)。検知は入ったが値は測り直すしかない。
2. **`fire_weight` の Δt 変換(B6)**: per-step Bernoulli の網外 1 本。scale_prob 化はユーザー判断待ち(補正しても呼数はほぼ動かないが、T1 を「機械固定」するなら必須の 1 ピース。§4.1)。
3. **凍結観測定数**: `src/society/observer/measure.py:35` の `ECHO_WINDOW_STEPS = 144`(Δt=1 ではエコー窓が 24h→144 分に縮む)・`observer/stream.py:394` の window=24。W3 凍結 14 本の内側なので 8/15 以降の判断。
4. **`analyze_beliefs.py --bin-steps`**: 既定 24 step(=Δt=10 で 4 時間。`scripts/analyze_beliefs.py:377-378`)は**意図的に Δt 変換なし**(`tests/test_w3_frozen_analyzers.py:276-279` が「run_dt を含まない」ことを固定)。Δt=1 ランでは呼び手が `--bin-steps 240` を渡す運用。
5. **`lod.n_proportional.density` の未宣言(★本調査での新規指摘)**: density × N は **per-step cap** なのに timeconv TABLE に宣言がない(`simulation.py:272-279, 1796-1805` で消費)。Δt=1 で ON にすると**日次予算が黙って ×10** になる(density 0.15 × 1440 step)。Δt≠10 ランでは density を steps_per_day 比で割るか、TABLE に RATE 宣言を足す判断が要る(§5 R4)。

---

## §3 文献(URL 必須)

### 3.1 ABM の時間解像度 — 「Δt は結果を変える実験パラメータ」

- **時間解像度の感度は ABM の第一級の検証項目**。時間・空間解像度と確率的要因が結果に大きな分散を生むことの実証: [An analysis of spatial and temporal uncertainty propagation in agent-based models(Phil. Trans. R. Soc. A, 2025)](https://royalsocietypublishing.org/rsta/article/383/2293/20240229/234674/An-analysis-of-spatial-and-temporal-uncertainty)。「何 step・何回・何体が必要か」を正面から扱うスケール依存性研究: [Scale Dependency in Agent-Based Modeling: How Many Time Steps? How Many Simulations? How Many Agents?](https://www.researchgate.net/publication/303362797_Scale_Dependency_in_Agent-Based_Modeling_How_Many_Time_Steps_How_Many_Simulations_How_Many_Agents)。ABM の時間感度分析の方法論: [Temporal meta-optimiser based sensitivity analysis (TMSA) for agent-based models(Sci. Rep. 2024)](https://www.nature.com/articles/s41598-024-59743-8)。
- **「1 step より短い現象は原理的に捉えられない」**: 暴動 ABM の評価は「時間単位 1 時間以下でないと暴動の展開が写らない」と明言 — [Practicality of Agent-Based Modeling of Civil Violence: an Assessment(arXiv:1501.05838)](https://arxiv.org/pdf/1501.05838)。本リポの「salience 発火が Δt=10 で 0 件」はこの一般則の実例である。
- **ドメイン別の標準 Δt**(10分/1分/30秒がそれぞれ適切な領域):
  - 歩行者(社会力モデル): **0.05〜0.1 秒**級の積分刻み。商用実装の較正・検証: [Pedestrian Flow at Bottlenecks — Validation and Calibration of Vissim's Social Force Model(arXiv:0805.1788)](https://arxiv.org/pdf/0805.1788)。本リポの `indoor.sfm.dt=0.05s` / ゾーン物理 dt_sub=0.05s はこの標準に一致。
  - 車両交通(ミクロ): **1 秒が既定・0.001〜1.0 秒まで短縮可**、ただしサブ秒では反応時間を保つため action-step を別に持つ(= 物理刻みと意思決定刻みの分離): [SUMO Documentation — Basic Definition(step-length)](https://sumo.dlr.de/docs/Simulation/Basic_Definition.html)・[SUMO Car-Following Models(action step length)](https://sumo.dlr.de/docs/Car-Following-Models/index.html)。
  - 疫学(都市〜国家規模 ABM): **1 日**が標準(状態遷移確率を日次で評価): [Covasim: An agent-based model of COVID-19 dynamics and interventions(PLOS Comp. Biol. 2021)](https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1009149)。
  - → 本リポは 1 つのシミュレータの中に歩行者物理(0.05 s)・移動/遭遇(Δt)・認知(分単位イベント)・制度(日次)の 4 層を持つ。**「社会層 Δt をどこまで下げるか」は歩行者と疫学の間のどこに線を引くかの問題**であり、文献上は 1 分(移動・遭遇の粒度)が妥当域、30 秒はミクロ交通/歩行者の領分 = 本リポでは物理サブステップが既に担当している。

### 3.2 イベント駆動とハイブリッド — 「空の tick をスキップする」設計

- **教科書的二分法**: next-event time advance(次のイベント時刻へジャンプ・不活性期間を飛ばす)vs fixed-increment time advance(等間隔 Δt。イベント間隔が大きく変動する系には不向き): [Discrete-event simulation(Wikipedia の Law & Kelton 系の整理)](https://en.wikipedia.org/wiki/Discrete-event_simulation)・[The Effect of Time-Advance Mechanism in Modeling(DTIC 技術報告)](https://apps.dtic.mil/sti/tr/pdf/ADA552002.pdf)。
- **ABM+DES ハイブリッドの実装前例**: MASON への DES スケジューラ統合 — [Hybrid Agent-Based and Discrete Event Simulation in MASON(ANNSIM 2023)](https://cs.gmu.edu/~sean/papers/annsim23des.pdf)。time-stepped と discrete-event を 1 つの co-simulation 基盤で混成 — [MOSAIK 3.0: Combining Time-Stepped and Discrete Event Simulation(arXiv:2410.16937)](https://arxiv.org/abs/2410.16937)。
- **「個体は DES・全体はマクロ step で同期」という本リポと同型の前例**: 人口 ABM GEPOC は「person-level discrete-event simulators を simulation layer がマクロ step で同期する co-simulation 型 time-update」を採用 — [GEPOC ABM Version 2.2(arXiv:2510.20840)](https://arxiv.org/abs/2510.20840)。イベント駆動マルチエージェントの一般論: [Event-Driven Multi-agent Simulation](https://www.researchgate.net/publication/272504010_Event-Driven_Multi-agent_Simulation)。
- → 本リポの cognition.fire(分単位の 1 人 1 イベントキュー + step 末同期バリア)は、この文献群の「認知=非同期イベント・世界=固定 tick・step 境界で同期」をそのまま実装した形になっている(`fire.py:29-62` が DES の tie-breaking 文献を自ら引いている)。**欠けているのは世界層の next-event 化(空 tick スキップ)だけ**であり、それは §4.6 の通り本選スコープ外が妥当。

### 3.3 LLM エージェントの認知周波数 — 「認知はイベントで・世界は細かく」の前例

- **Generative Agents(Smallville・25体)**: サンドボックスは**ゲーム内 10 秒 = 1 step** で進み、エージェントの行動は「持続時間つきの行動」を LLM が計画し、行動の区切り・知覚イベントへの反応時にのみ再プロンプトされる(= 世界 tick ≠ LLM 呼数): [論文(arXiv:2304.03442)](https://arxiv.org/abs/2304.03442)・[公式実装(sec_per_step=10)](https://github.com/joonspk-research/generative_agents)。**世界刻み 10 秒でも破綻しないのは呼数がイベント駆動だから**であり、T1 の直接の前例。
- **AgentSociety(1万〜3万体)**: LLM 駆動エージェント+都市環境+分散エンジン(Ray)。24×A800 で 3 万体が実時間超で回る。認知は「needs→plan→action」のイベント連鎖で、環境シミュレータ(移動・経済)は別クロック: [arXiv:2502.08691](https://arxiv.org/abs/2502.08691)。
- **Lyfe Agents**: 低コスト実時間対話のため「cognitive controller が LLM 呼び出しを絞る」設計(観測ストリームは連続・高価な推論は選択的): [arXiv:2310.02172](https://arxiv.org/pdf/2310.02172)。
- LLM×社会 ABM の統合課題の概観(呼数・粒度・検証を含む): [Integrating LLM in Agent-Based Social Simulation: Opportunities and Challenges(arXiv:2507.19364)](https://arxiv.org/pdf/2507.19364)。
- → 定式化すると、先行系はいずれも **「世界 tick は忠実度の要請で決め、LLM 呼数は行動・イベントの区切りで決める」**。本リポの cognition-design-record §5.1「Δt を細かくしても思考の総量は変わらない」はこの潮流の明文化であり、実装(分単位周期+割込み+per-day 計画/内省)も同型である。

### 3.4 呼数不変の機械固定 — 予算宣言・確率変換・メタモルフィック検査

- **確率の時間スケール変換は「割り算」ではなく「ハザード経由」**(本リポ PROB 分類の学術的双子)。医療決定モデリングの標準手順: [Estimating Transition Probabilities from Published Evidence: A Tutorial for Decision Modelers(PharmacoEconomics 2020)](https://link.springer.com/article/10.1007/s40273-020-00937-z)・[TreeAge — Probability/rate conversion functions](https://www.treeage.com/help/Content/71-Advanced-Markov-Models/2-Probability-Rate-conversions.htm)・確率でなくハザードで扱うべき理由: [Study mortality with hazard rates, not probabilities(bioRxiv)](https://www.biorxiv.org/content/10.1101/216739v2.full)。
- **「Δt を変えても per-day 統計量が保存される」はメタモルフィック関係(MR)として機械検査できる**。シミュレーション検証への MR 適用の枠組み(ABM のケーススタディ含む): [Metamorphic validation for agent-based simulation models(SCSC 2016)](https://dl.acm.org/doi/10.5555/3015574.3015607)・[Multi-Agent Specification-based Metamorphic Testing of FMU-Based Simulations(arXiv:2605.25101)](https://arxiv.org/abs/2605.25101)。
- → 本リポには既に同じ流儀のテスト資産がある: 「ON/OFF で generate 呼数完全一致」をプロンプト非依存スタブで固定(`tests/test_transit_interior.py:96-107`(_FixedLLM)・`:718`)、日次総量保存(cap×steps_per_day 不変)は `tests/test_timeconv.py` が固定済み。**「Δt を動かしても per-day 呼数量が不変」という MR を同じ道具立てで足すだけ**である(§4.1)。

---

## §4 設計素材 — Δt=5 / 1 / 0.5 分それぞれの呼数不変設計とコスト

### 4.1 呼数不変の 3 本柱(全 Δt 共通)

**柱 1 — 予算の per-day 宣言**。発火予算を「43,200 呼/日」(または 呼/人/日 f)で宣言し、per-step cap は `cap_day / steps_per_day` の導出量にする。現行の RATE 分類(`timeconv.py:197`)は数学的に同じことを達成しているが、**宣言の向きが逆**(per-step が正で日次が従)。per-day を正にすると:
- `lod.n_proportional.density` の罠(§2.5-5)が構造的に消える(density も 呼/人/日 で宣言)。
- 25万提案書の「会話の生きの良さ = cap×144/N」(proposal-dp-u3 §2.2)がそのまま conf の第一級量になる。

**柱 2 — 発火のイベントゲート化の完遂**。step 比例の機会は現在 1 本だけ(`fire_weight` の per-step 抽選 = OBS-U2 B6)。これを scale_prob(ハザード保存)へ載せるか、cognition.fire ON 側(分単位キュー)へ一本化する。恒常性 `theta_target_per_day`(f* 件/日/人。`timeconv.py:449-450`)が既に per-day のフィードバックで発火率を吸引しており、σ_c 再測後はこれが「Δt を変えても f が f* に戻る」自動安定化として働く。

**柱 3 — 機械固定テスト(メタモルフィック関係)**。本リポの流儀に接続した 4 段:
1. **恒等段**: Δt=10 で L1 バイト一致(既存 golden。実装済み)。
2. **総量段**: cap_day = max_llm_per_step × steps_per_day が Δt∈{10,5,1} で不変(既存 test_timeconv の拡張)。plan/reflect の呼数 = 在場者数 × 日数 が Δt 不変(FixedLLM スタブで計数)。
3. **AST 段**: `generate` 呼び出しサイトの全数列挙をテストに焼き、「予算ゲート(budget.take)・per-day フェーズ・イベントキュー経由以外の generate 呼び出しサイトが存在しない」ことを AST で固定(test_transit_interior ⑤ の「会話の識別子が module に存在しない=AST 固定」と同型)。**これが「機会が step 数に比例しない」ことの構造的証明**になる。
4. **期待値段**: mock・小規模・seed 掃引で「呼/人/日」が Δt 間で同オーダー帯(T3 の緩い版)に収まることを band テスト。★等値は要求しない(乱数消費列が別世界=§5 R1。salience 解放は**意図した差分**なので、band は「periodic+plan+reflect の和」と「salience 込みの総和」を別々に張るのが正直)。

### 4.2 Δt=5 分 — 「今日動く」最小の一歩

- `run.dt_min=5` は整数・1440 の約数で**現行機構がそのまま受ける**(Δt=5 の resume テスト既存)。準備作業ゼロ(σ_c 再測を除く)。
- コスト: エンジン ×2・L1 ×1.5〜2(推定)・LLM 呼数 ×1.2〜1.5(推定。talking 周期 2.0 分 < 5 分なので salience は talking 文脈では引き続き沈黙 = 解放は部分的)。
- 科学的利得は**半端**: 第83 の人工物(talking の CV≈0)は 5 分でも残る。**Δt 掃引の中間点(10/5/1 の 3 条件)としての価値が主**。単独の本線変更として選ぶ理由は薄い。

### 4.3 Δt=1 分 — 準備 9 割済み・並行小ランの本命

- 土台は完成(§2.5)。`conf/smoke_dt1.yaml` で今日走る。残る実務は σ_c 再測(mock で手順を先に通す)と、B6/凍結定数のユーザー判断のみ。
- 呼数: 実測 ×2.2〜2.4(規模で予算を作る。smoke_dt1 の注記 (b) が「時間解像度で節約しない」を明文化済み)。柱 1〜3 を入れれば設計上 ×1 に固定することも可能だが、**salience 解放を潰す固定はしない**(それが Δt=1 の科学的動機)。
- 規模の上限(§4.5 の試算から): 10 日ランのエンジン時間を 240h 枠の 10〜20% に収めるなら **1〜2 万体**。25万の本線と同一 ON セット・同一 seed 方針で並走させ、比較はラン間統計量のみ。
- 得られるもの: salience 発火の直接観測(0→103 件)・思考頻度分布の真値(CV/バースト性)・1 分解像度の発火連鎖(誰の行動が誰の思考を起こしたか)。

### 4.4 Δt=0.5 分(30 秒)— 構造と利得の両面から見送り推奨

**構造的障壁(現行の時間通貨は「整数分」)**:
1. `dt_of` は `int(v)` + 「1440 の約数」検査(`timeconv.py:626-632`)。0.5 は**表現できない**(int(0.5)=0 → ValueError)。float 化は STEPS 逆比例・`sim_min` 整数演算・L1 固定列 `sim_min`(凍結スキーマ)・分単位の認知キューまで波及する**通貨の切替**(分→秒)になる。
2. **思考層の利得はゼロ**: 認知イベントは整数分でスケジュールされ、周期は `max(1.0, mean)` + `int(round(・))` で**最短 1 分に量子化済み**(`fire.py:375-381`)。Δt=1 分の時点で認知キューは完全解像しており、30 秒はサンプリングを倍にするだけで 1 件も新しい発火を生まない。
3. **物理層は既に 30 秒より細かい**: ゾーン内 0.05 秒サブステップ(§2.3)。30 秒で新たに細かくなるのは「ゾーン外移動の直線補間」だけで、それは SFM ではない(OBS-U2 R4)。
4. コスト: エンジン ×20(25万体で 55〜104 h/シミュ日)・L1/L2 の毎 step 行 ×20。

**結論**: 「現実の最小単位は 10 分より細かい」という直感の受け皿は、(a) 認知=分単位イベントキュー(実装済み・Δt=1 で完全解像)、(b) 物理=0.05 秒(実装済み)、の** 2 層が既に担っている**。30 秒の社会層 tick は両者の間に第 3 の解像度を挿す提案であり、費用(通貨切替+×20)に対して買えるもの(ゾーン外補間の平滑化)が釣り合わない。SUMO が「物理刻みを 0.1 秒にしても意思決定は action-step で 1 秒に保つ」流儀(§3.1)と同じ線引きである。

### 4.5 コストの正直な見積り(25万〜30.7万体)

**エンジン壁時計/シミュ日**(壁時計 ≈ c×N×steps_per_day。楽観 c=2.76e-4(第102 実測)〜保守 c=5.22e-4(25万提案書採用値)):

| Δt | step/日 | N=250,000 | N=307,000 | 10日ラン(25万) | 判定(240h 枠) |
|---|---:|---:|---:|---:|---|
| 10 分 | 144 | 2.8〜5.2 h | 3.4〜6.4 h | 28〜52 h | ◎ 現行 |
| 5 分 | 288 | 5.5〜10.4 h | 6.8〜12.8 h | 55〜104 h | ○ 入るが LLM 枠を圧迫 |
| **1 分** | **1,440** | **27.6〜52.2 h** | **33.9〜64.1 h** | **276〜522 h** | **✕ 実時間より遅い・枠超過** |
| 30 秒 | 2,880 | 55〜104 h | 68〜128 h | 552〜1,044 h | ✕✕ 論外 |

- ★c は 1 万体ベンチ由来。25万での超線形成分(同席系)は上振れ要因で、この表は**下界**。
- Δt=1 が入る規模: エンジン 10 日 ≤ 24〜48 h に収めるなら **N ≤ 1〜2 万**(楽観 c で 2 万体 = 22 h/10日)。
- 物理サブステップは Δt 中立(§2.3)なので表に加算不要。LLM 時間は呼数×R_eff で別勘定(呼数は cap で固定可能 = Δt に依らず同じ天井)。

**L1**: 実測 ×3.1〜3.7(Δt=1)。25万×10 日の線形下界 42.7 GB(proposal-dp-u3 §2.3)→ Δt=1 なら **130〜170 GB+超線形成分**。支配項は move_segment(per-移動者 per-step)と L2 metrics(×10)。間引き手動 ×10(プロファイル済み)が前提で、`observer.measure.load_events` の全件 RAM 展開は Δt=10 の 25万で既に破綻線(同 §2.4)なので、Δt=1 大規模はそもそも「回せても測れない」。小ラン(1〜2 万体)なら L1 は 3〜17 GB 級で許容。

**checkpoint**: サイズは状態量比例(step 数に非依存)。`observer.checkpoint_every` は INVARIANT(理由つき宣言 `timeconv.py:392-397`)なので、**Δt=1 では手動で ×10 しないと保存回数が 10 倍**になる — smoke_dt1.yaml は 1440(毎シミュ日)で固定済み。resume は第94 根治済みで Δt 非依存に動く。

### 4.6 イベント駆動ハイブリッドの適用可能性

- **認知層は完成形**: 分単位 DES(1 人 1 イベント・全順序・step 末同期バリア)は §3.2 の文献群(GEPOC の「個体 DES+マクロ step 同期」・MASON ハイブリッド)と同型で、これ以上の変更は不要。**Δt 短縮の目的の大半は「認知キューを世界 tick の量子化から解放する」ことであり、それは run.dt_min=1 で達成される**(第 2 の時間軸を作る案2 が OBS-U2 で棄却済みなのと同じ理由)。
- **世界層の next-event 化(空 tick スキップ)は本選スコープ外が妥当**: 到着時刻・滞在満了・便発車をイベント予約すれば「何も起きない step」を飛ばせるが、(a) 毎 step の共在走査・環境フィードバック・観測行が「何も起きない」を保証できず、(b) 乱数消費列が全面的に組み変わり golden・較正・凍結資産と切れる。25万の壁時計は Δt=10 なら 28〜52 h/10日で**律速ではない**(proposal-dp-u3 §2.4: 律速は解析→RAM→LLM→engine の順)。イベント駆動化は「Δt=1 を大規模で回したくなったとき」の将来投資として温存する。
- **現実解は 2 ラン体制**: 本線 25万 × Δt=10(制度・経済・組織の創発)+並行 1〜2 万 × Δt=1(思考・会話・遭遇の時間構造)。これは疫学(日次)と歩行者(サブ秒)が同じ現実の別解像度レイヤーとして併存する §3.1 のドメイン標準の縮図でもある。

---

## §5 リスク

| # | リスク | 深刻度 | 備考 |
|---|---|---|---|
| R1 | **Δt≠10 は別の世界**(乱数消費列が変わる)。step・個体単位の対応づけは原理的に不可能。「同じ seed なのに違う」は仕様 | 高(仕様) | `timeconv.py:45-46` の明文規約・smoke_dt1.yaml (a)。比較は必ずラン間統計量。論文の書き方を先に決める(OBS-U2 R2) |
| R2 | **較正 T3**: σ_c(per-step カウント量)は Δt=10 の母集団。流用すると salience 系統的過小。θ はその従属 | **高** | 検知(WARNING+manifest)は第99 で実装済み。値は再測のみ。8/15-16 実 LLM 枠外で mock 手順を先に通す |
| R3 | **凍結観測定数**: `measure.py:35` ECHO_WINDOW_STEPS=144・`stream.py:394` window=24・`analyze_beliefs.py --bin-steps` 既定 24(意図的に無変換=AST 固定済み)。Δt=1 では窓が実時間 1/10 に縮み、ラン横断比較が歪む | 中 | W3 凍結 14 本の内側 = 8/15 以降の判断。当面は呼び手が引数で ×10(beliefs は `--bin-steps 240`) |
| R4 | **`lod.n_proportional.density` が TABLE 未宣言**(per-step cap)。Δt=1 で ON にすると日次予算が黙って ×10 | 中(★新規指摘) | 使うなら density を手で 1/10 にするか、TABLE へ RATE 宣言(1 行)。呼数不変を per-day 宣言に切り替えれば構造的に消える(§4.1 柱1) |
| R5 | **エンジン壁時計 ×10/×20**。25万 Δt=1 は実時間より遅い(27.6〜52.2 h/シミュ日) | 高(規模限定で回避) | Δt=1 は 1〜2 万体の並行小ランに限定(§4.5)。c は 1 万体ベンチ由来で超線形成分は上振れ要因 |
| R6 | **L1 ×3〜4+解析側の全件 RAM 展開**。大規模 Δt=1 は「回せても測れない」 | 中 | 間引き手動 ×10(プロファイル済み)+小ラン限定で回避 |
| R7 | **fire_weight の per-step Bernoulli**(唯一の step 比例機会)が未変換のまま = T1 の形式的完成が欠ける | 低 | 補正しても呼数はほぼ動かない実測(244→231)。B6 はユーザー判断待ち(§4.1 柱2) |
| R8 | **30 秒は通貨切替**(整数分 → 秒)。`dt_of` の整数検査・sim_min・L1 凍結スキーマ・認知キューの分量子化まで波及 | 高(見送りで回避) | §4.4。思考層の利得ゼロ・物理は 0.05 s 既存。掃引の梯子は 10/5/1 で止める |
| R9 | Δt=1 実測(×2.2〜2.4・L1 ×3.7)は mock・12体・1 日。実 LLM・大規模では動く | 中 | 第83 の教訓「呼/人/日は人数不変でない」。外挿でなくパイロット実測(smoke_dt1 の設計意図) |

---

## 結語 — ユーザーの直感のどこが正しく、どこに罠があるか

- **正しい**: 「発火の機会自体は増えない」— 予算は日次総量保存・周期は分単位・計画/内省は per-day で、機構の設計意図はまさにそれ。LLM 計算量は Δt に依らず cap で天井固定できる。「10 分より細かい最小単位」も正しく、文献(Generative Agents 10 秒 tick・暴動 ABM の 1 時間則)と本リポの実測(salience 0→103 件)が支持する。
- **罠 1**: 実測呼数は ×1 でなく ×2.2〜2.4。ただしそれは機会の増加ではなく **Δt=10 が潰していた驚き発火の解放**であり、据え置くために間引くと Δt=1 の意味が消える。
- **罠 2**: 増えるのは LLM ではなく**エンジン壁時計**(step 数にほぼ線形)。25万体 Δt=1 は実時間より遅く、本選 240h 枠に入らない。Δt=1 は 1〜2 万体の並行小ランが正解。
- **罠 3**: **30 秒は整数分の時間通貨と衝突**し、認知層の利得はゼロ(周期は 1 分量子化済み・物理は 0.05 s 既存)。梯子は 10 → (5) → 1 分で止めるべき。
