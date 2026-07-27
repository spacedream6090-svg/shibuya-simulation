# 本選 GPU 利用申請フォーム 回答草案 + GitHub 公開の判断材料

- 作成: 2026-07-27 / 担当: Opus 5(実行役・リポジトリ実査 + 既存文書からの計算のみ。コード変更なし・実 LLM ラン未実行)
- 目的: AUTOMATA 第2回ハッカソン本選(**本選 8/15 スタート・提出締切 8/30 23:59・GPU 利用申請締切 8/9** =
  公式サイト実査 2026-07-27・§0.1)の事務局提出フォーム 3 設問への回答草案と、
  GitHub 公開の可否判断に必要な材料(実査結果つき)を一枚にまとめる。**最終判断・提出は親(Fable 5)/ユーザー**。
- 本書の数値は**すべて既存文書からの引用または引用値からの計算**。出典をファイル名+節で併記する。
  不明・未確定は「未確定」と明記し、推測で埋めない。

> **凡例**: 【実測】= リポジトリ内に実測記録がある値 / 【推定】= 文書上の試算値(Day-0 ベンチで置換)/
> 【本書計算】= 文書の実測・推定値から本書が計算した値(計算式を併記)。

---

## §0 前提の確認(先に潰しておく食い違い)

| 事項 | 文書上の記載 | フォーム/依頼上の記載 | 本書の扱い |
|---|---|---|---|
| 期間 | **本選 10 日間**(`docs/AUTOMATA第2回ハッカソン案.md`「本選10日間」「日程は仮で以下の構成です」) | **8/8–8/23**(16 日) | GPU クラスタ開放は **10 日=最大 240 時間**を保守側の前提に置く。8/8–8/23 全期間開放なら上限 384 時間。**開放の実期間は未確定** |
| GPU | **RTX5000 × 7 台・VRAM 総量 168GB**(同案 L19-20/L37-59。主催公表値) | — | 168 ÷ 7 = **24GB/GPU** と逆算(`finals-hardware-plan.md` §0)。銘板(A5000 24GB か RTX 5000 Ada 32GB か)は**未確定** |
| トポロジ | **単一 PC に 7 GPU**(同案) | — | ops topology A(単一ノード 7GPU)で確定(`finals-hardware-plan.md` §0) |
| 1 step の意味 | 1 step = 10 分・**1 シミュ日 = 144 step**(`conf/experiments/endogenous_accept.yaml` L11 ほか) | — | 本書のステップ数はすべてこの換算 |

### §0.1 公式サイト実査(2026-07-27・https://hackathon.automata-lab.jp/ ・WebFetch 2 回で原文引用確認)

| 事項 | 公式サイトの記載(原文) | 本書への影響 |
|---|---|---|
| **GPU 利用申請の締切** | 「8.9(日)応募・利用申請の締切」「8.14(金)利用チーム発表」 | **フォーム提出は 8/9 まで**。本書の回答はそれまでに提出する |
| 本選日程 | 「8.15(土)本選スタート」「8.23(日)23:59 参加登録締切」「**8.30(日)23:59 提出締切**」「結果発表 後日」 | フォーム例の「8/8–8/23」はテンプレ例と判明。**実期間は 8/15–8/30(16 日)** → §2.1 の期間表現を修正済み。GPU 開放開始の厳密な日(8/14 発表直後か 8/15 か)のみ未確定 |
| GPU 構成 | 「168GB 1台あたりの合計VRAM」「×7台 ワークステーション」「RTX5000×7 1台の内訳」 | **ワークステーションは 7 台あり、1 台の内訳が RTX5000×7 = 合計 168GB**。§0 の「単一 PC に 7 GPU」を公式値で裏付け。フォームの 80/140/168GB は **1 台内の部分/フル占有**の選択と読める → 「168GB(フル)= 1 台占有」の申告は変更不要。24GB/GPU 逆算も整合 |
| 提出物 | 「プレゼン資料、README(目的・実行環境・使い方など)」必須・「実行結果のまとめ(RESULTS.md 等)もあると、審査に伝わりやすくなります」・GitHub リポジトリ | README は現状ほぼ充足(§3.4-D)。**RESULTS.md は本選中に作る**(推奨・必須ではない) |
| 公開時期・ライセンス規定 | 明記なし。「規約まわりの詳細は応募時にご案内します」 | 公開の実施タイミング・ライセンス指定は応募時案内待ち。§3 の準備は先行して可能 |

> この実査により §4-1(開放期間)はほぼ解消: **本選期間 = 8/15–8/30**。全期間開放なら上限 384h で、
> 申告 200h・最大到達 255h とも枠内。8B 主力の 304h も数字上は収まるが 16 日中 12.7 日連続占有となり非現実的
> (§2.4 の「8B なら規模を落とす」判断は不変)。

---

## §1 設問1「GPUサーバーを使って、どのようなことを行う予定ですか」回答草案

### 1.1 研究目的(1 段落・そのまま貼れる形)

> 実在の渋谷(OSM 実地図・実ダイヤ・国交省人流統計で較正した在場曲線・経済センサス由来の組織台帳)を
> 忠実に再現した LLM 人工社会を走らせ、**「世界を変えようとする個体は生まれつき存在するのか、環境から
> 創発するのか」**を反証可能な形で測る。改変者を直接実装せず、4 層(空間・資源・象徴・social network)への
> 連続的な書き換え量 Y を、初期パラメータ(traits)で回帰した決定係数 **R²(k)** として観測し、経験→内部状態の
> 結合強度 k を掃引して init-determined → path-dominated の**相転移点 k\***を探す。あわせて、強制トリガーを
> 入れない日常のみの世界から**組織の自然形成とファウンダー成立条件**、および**関係性(誰と過ごすかの承諾判断)の
> 内生化**が社会構造を動かすかを観察する。GPU が必然なのは、①リッチ認知(全員が朝に計画し・日中に考え直し・
> 夜に内省する)を保ったまま**在場数万〜25 万体**規模を回すこと、②その上で **k 掃引 × seed の多数フルラン**を
> 対照込みで積むこと、の両立が単機では成立しないため。
> (出典: `README.md` 研究課題 / `docs/design.md` §研究の問い・§23 / `docs/plans/w2-execution-plan.md` §0-§1)

### 1.2 実行計画の表(エージェント数 × ステップ数 × 試行回数)

> LLM 呼数の見積りは 2 系統の較正モデルを使い分ける(混ぜると誤る):
> - **(a) 較正済み密度モデル**(小〜中規模の実験ラン用): `C_calls(N) = min(3988·(N/200)^1.209, 43200) + 305·(N/200)`
>   【推定式・`docs/research/scale-feasibility.md` §6】。N=200 で 4,293 呼/シミュ日 = **21.5 呼/人日**で、
>   較正済み 200 体ランの【実測】21.6 呼/人日(`w2-execution-plan.md` §1.5 引用)とほぼ一致する。
>   15 体アンカー 187.5 呼/日【実測・`scale-feasibility.md` §2 表】に対し式は 197 呼/日=誤差 5%。
> - **(b) 全員思考モデル**(本番観察ラン用): 在場 25 万 → 朝計画 25 万 + 夜内省 25 万 + 日中熟慮 ~150 万 =
>   **~200 万呼/シミュ日 = ~8 呼/人日**【推定・`w2-execution-plan.md` §1.4/§3.2・`docs/research/agent-vision.md` §5】。
>   (a) の `min(…, 43200)` は旧 3 tier 設計の `lod.max_llm_per_step=300` × 144 step 上限で、全員思考モデルでは
>   N 比例予算に置き換わるため、大 N では (b) を使う。

| # | 目的 | エージェント数 × ステップ数 × 試行回数 | LLM 呼数【本書計算】 | 備考(出典) |
|---|---|---|---|---|
| **1** | **観察ラン(現実渋谷の再現・主成果)**<br>k 掃引なしの単一条件・純観察 | **在場 5 万〜25 万体 × 432〜1,440 step(3〜10 シミュ日)× 1 本**<br>(段階昇圧 1万→5万→10万→25万を内包) | 25 万×10 日 = **2.0×10⁷ 呼**<br>5 万×10 日 = **4.0×10⁶ 呼** | 規模とシミュ日数は **D4 で Day-0 ベンチ結果から当日決定**(`finals-day1-decisions.md` D4「在場5万〜25万 × 3〜10日」)。位置づけ=「本番 10 日ラン=k 掃引なしの単一条件・観察ラン」(`w2-execution-plan.md` §3.1) |
| **2** | **k 掃引実験(R²(k)/k\* 本命)** | **提案: 300 体 × 2,016 step(14 シミュ日)× 30 ラン**<br>(6 水準 {off, sham, degraded α=0.25/0.5/0.75, free} × 5 seed) | **2.93×10⁶ 呼**<br>(6,969 呼/シミュ日 × 14 × 30) | **文書上、本選の掃引セル数は確定していない**ため両論併記:<br>・案A【文書値】「本番データは finals GPU での **N=100 × 100 日 × 4 条件 × 複数シード**」(`docs/experiments/realllm-pilot-20260709.md` 総合所見4・2026-07-09)→ 12 ラン想定で **2.25×10⁶ 呼**<br>・案B【文書値】「k\* は **7–14 日・人数多め**で別に回す(二段構え)」(`docs/research/longrun-estimate.md` §5・D15・2026-07-24=より新しい)<br>上表の提案は案 B に `scripts/run_sweep.py` の既定(modes off/sham/free・seeds 5・alphas で degraded 中間点)を当てたもの。**開始タイミングは D12**(既定=観察ラン 1 日完走後) |
| **3** | **関係性の内生化 treatment(D17)** | **100 体 × 2,016 step(14 シミュ日)× 30 ラン**<br>(endogenous_accept {OFF,ON} × k {off, degraded α0.5, free} = 6 セル × seed 5、同一 seed 列 CRN ペア) | **7.89×10⁵ 呼**<br>(1,878 呼/シミュ日 × 14 × 30) | 構成は `conf/experiments/endogenous_accept.yaml` そのまま(実ファイル実査)。**LLM 呼数は ON/OFF 不変**(構造化出力からの決定論抽出=新規呼びゼロ)なので追加コストは条件数×ラン数のみ(D17)。配線検証は mock 12 ラン(7日60体)を**合計約22分で完走【実測】**(D17 予備実測・第63バッチ) |
| **4** | **30 日長期日常ラン(D15・構造創発)** | **100 体 × 4,320 step(30 シミュ日)× 1 条件** | **5.63×10⁴ 呼** | mock 実測外挿: 実時間 18.0 分・L1 parquet 48.0MB・全 parquet 50.8MB・ピーク RAM 2.0GB(checkpoint_every=1440)【`longrun-estimate.md` §4】。10日×3 に分割しても resume はバイト一致【同 §5】。既定は「7–14 日に短縮」で**30 日は余剰枠**(D15) |
| **5** | **model×k 対照 4 セル(任意)** | **15 体 × 288 step(2 シミュ日)× 8 ラン**<br>(instruct/abliterated × k{free,off} × seed 2) | **3.2×10³ 呼** | 構成は `conf/experiments/modelk_4cell.yaml` 実査。計算量は無視できるが**2 モデル分の重みを載せる**必要がある。スモーク合格済み・実行待ち(`docs/plans/unimplemented-inventory.md` C1) |
| **6** | **VLM 視覚パイプライン(D1 次第・条件付き)** | 観察ランに同居。VLM 呼 **2 万〜10 万/シミュ日**(前景の顕著時のみ) | 上記に加算 | **既定は OFF**(D1 既定=「B のみ作動・v1 OFF」)。ON にするなら GPU 役割を **テキスト6 + VLM1** に分割(D6)=テキスト容量 −14%。VLM 1 枚の容量は ~60〜70 万呼/日【推定・`agent-vision.md` §5.3】なので需給は余裕 |

**総推論規模の概算【本書計算】**

| シナリオ | 合計 LLM 呼数(オーダー) |
|---|---|
| **最大到達目標**(観察 25 万×10 シミュ日 + 上表 2〜5) | **≈ 2.4×10⁷ 呼(約 2,400 万呼)** |
| **堅い着地**(観察 5 万×10 シミュ日 + k 掃引を 100体×14日×4条件×5seed へ縮退 + 上表 3〜5) | **≈ 5.4×10⁶ 呼(約 540 万呼)** |

> 縮退の順序は `finals-hardware-plan.md` §3.1 の縮退線に従う(**まずシミュ日数を削り、体数は維持**。
> OOM・observer 破綻のときだけ体数を落とす=ユーザー既定「エージェント数 > 実行時間」)。

### 1.3 GPU が必然である理由(審査項目「GPUを使う必然性」「GPUで成果が伸びるか」への対応)

- **規模単体は差別化ではない**(OASIS=100 万体・AgentSociety=1 万体が既達)と自認した上で、
  novelty は **①agency 創発という問い ②k\* 相転移の測定 ③検証可能性(operational validity)** に置いている
  (`docs/design.md` §23・`docs/research-scope.md` novelty の再定義)。
- その測定には「**リッチ認知を保ったまま数万体 × k 掃引 × seed の多数フルラン**」が要り、
  ここが単機 GPU で成立しない部分(`docs/design.md` L23/L39: 「本選 10 日間の hard wall-clock → 因子数・掃引軸・seed 数を直接縛る」)。
- **GPU で成果が伸びる箇所が定量的に特定済み**: 在場を 1 段上げるごとに LLM 呼数が線形に増え(表 1)、
  seed 数を 1 増やすごとに R²(k) の CI が縮む。つまり GPU 時間がそのまま**統計的検出力**に変換される構造。

---

## §2 設問2「モデル・フレームワーク・想定使用時間・必要な GPU メモリ」回答草案

### 2.1 フォーム記入用の 1 行回答(例の書式に合わせた形)

> **Qwen3-4B(INT4/Q4_K_M)を主力・Qwen3-8B(INT4)を上位候補として Day-0 ベンチで確定、統制対照に
> huihui_ai/qwen3-abliterated:4b-v2-q4_K_M(Apache-2.0)/ vLLM(OpenAI 互換サーバを GPU 1 枚 = 1 レプリカの
> 7 本艦隊構成・prefix caching 有効)+ 自作 Python シミュレータ(numpy / networkx / omegaconf / pyarrow)/
> 本選期間中(8/15–8/30)で合計 約 200 時間(GPU 7 基をほぼ連続占有)/ 168GB(フル)**

### 2.2 モデル(文書上の実名・すべてリポジトリ内文書からの引用)

| 役割 | モデル | 出典・根拠 |
|---|---|---|
| **主力テキスト(第一候補)** | `qwen3:4b`(Qwen3-4B・hybrid thinking・既定 Q4_K_M ~2.5GB・40K ctx) | D3「主力テキストモデル 4B / 8B INT4 / 混成」の**既定 = 4B(実測が仕様書前提)**(`finals-day1-decisions.md` D3)。現行運用モデル(`docs/research/model-contrast-setup.md` §「現行運用モデル」) |
| **主力テキスト(上位候補)** | `qwen3:8b`(**24GB のため AWQ/INT4 を第一候補**) | `conf/profiles/finals-vllm7.yaml` の `model.name: "qwen3:8b"`。24GB 制約下の量子化方針は `finals-hardware-plan.md` §2-① 付録 1 |
| **統制対照(abliterated)** | `huihui_ai/qwen3-abliterated:4b-v2-q4_K_M`(2.5GB・Q4_K_M・40K ctx・**Apache-2.0**) | `conf/experiments/modelk_4cell.yaml` 実査 / `model-contrast-setup.md` §「推奨対照(実在確認済み)」。8B 対は `huihui_ai/qwen3-abliterated:8b-v2-q4_K_M`(5.0GB) |
| **speculative draft(任意)** | `qwen3:0.6b` 級 | `finals-hardware-plan.md` §4.4。**飽和運転では spec が 1.0 割れもある**ため Day-0 の before/after 実測で採否(同 §2-③′) |
| **VLM(D1 で ON の場合のみ)** | `Qwen2.5-VL-7B-Instruct`。**24GB では AWQ/INT4 か 3B/2B 版が現実的** | `agent-vision.md` §2c(「Qwen2.5-VL-7B は 24GB で動作可だが窮屈 → AWQ/INT4 か 3B/2B 版」)。テキスト 4B と VLM 7B の**同一 24GB 上への両重み常駐は非現実的** → GPU 単位で役割分離 |

> **未確定として残す項目(正直な註記)**: 主力を 4B にするか 8B INT4 にするか、量子化方式(AWQ か GPTQ か)、
> VLM を立てるか(D1/D6)、spec decoding の採否は **Day-0 ベンチで実測して当日確定**する(`finals-hardware-plan.md` §2 の
> 5 項目 + `finals-day1-decisions.md` D1/D3/D6)。本フォームには第一候補を書き、当日変わりうる旨を添える。

### 2.3 フレームワーク

- **推論サーバ**: **vLLM**。GPU 0〜6 にポート 8000〜8006 で **1 枚 1 プロセス = 7 レプリカ**(TP なし・データ並列)。
  起動フラグ: `--enable-prefix-caching` / `--max-model-len 8192` / `--gpu-memory-utilization 0.90` /
  `--max-num-seqs 128〜256`(Day-0 に 64/128/256/512 で飽和点を探す)。
  出典: `finals-hardware-plan.md` §1.2 本命行・§2-①、`ops/launch-vllm-finals.ps1`。
- **ルーティング**: 自作 **FleetLLM** が `agent_id` で **sticky 割当** → 同一エージェントのプロンプト接頭辞が
  同じサーバに当たり続け prefix cache が効く。`tiers` で purpose 別にサーバ群を分割可(例: reflect=8000 の 1 本・
  それ以外=8001-8006 の 6 本)。出典: `conf/profiles/finals-vllm7.yaml`。
- **シミュレータ本体**: 自作 Python(`src/society/`)。依存は `numpy>=1.26` / `networkx>=3.2` /
  `omegaconf>=2.3` / `pyarrow>=15.0`、Python 3.10+(`pyproject.toml` 実査)。GPU は使わない(CPU 側の直列律速)。
- **監視・耐障害**: `scripts/watchdog.py`(プロセス死→最新 checkpoint から自動 resume・ストール kill 再開・
  checkpoint 破損時は 1 世代前へロールバック)+ **part flush による走行中部分納品**(`finals-hardware-plan.md` §5.1/§5.2)。

### 2.4 想定使用時間(逆算過程つき)

**逆算に使う実効スループット**

```
R_eff = (集約 req/s) ÷ 1.15(overhead)          ← finals-hardware-plan.md §1.3 の定義
  4B : 38 req/s【推定・±50%】 ÷ 1.15 = 33.0 呼/s   ← D3「4B ~38(prefix込)」/ w2 §3.2
  8B : 21 req/s【推定・range 14–35】÷ 1.15 = 18.3 呼/s ← finals-hardware-plan.md §1.2 本命行
非LLM(直列時に加算) = 144 · N · c_nonllm
  c_nonllm =【実測】0.000528 s/agent-step(1万体・深夜帯・D4)/ 参考帯 lean 0.00183 〜 full 0.060
※ 本番は LLM 発行とエンジン物理演算の重畳(非同期バッチ発行)を前提とするため、
  下表は LLM 側のみを壁時間に計上(直列運用なら非LLM 分を加算。w2 §3.2「直列だと 26h 超/日」)。
```

| ラン | 呼数【本書計算】 | 壁時間(4B・R_eff 33.0) | 壁時間(8B・R_eff 18.3) | 検算 |
|---|---|---|---|---|
| 観察ラン **25 万体 × 10 シミュ日** | 2.0×10⁷ | **168 h**(16.8 h/シミュ日) | **304 h**(30.4 h/シミュ日) | w2 §3.2 の文書値は「**12–15 h/シミュ日**」(38 req/s の生値 2.0e6/38=14.6h。overhead 1.15 を掛けると 16.8h)。w2 §0「10 シミュ日 ≈ 5.5–6.5 壁日」= 132–156h と整合 |
| 観察ラン **10 万体 × 10 シミュ日** | 8.0×10⁶ | 67 h | 121 h | ― |
| 観察ラン **5 万体 × 10 シミュ日** | 4.0×10⁶ | **34 h** | **61 h** | 非LLM を直列加算すると +1.06 h/シミュ日(=144×5万×0.000528)=+11h |
| k 掃引(提案 300体×14日×30ラン) | 2.93×10⁶ | **25 h** | 44 h | ― |
| k 掃引(縮退 100体×14日×4条件×5seed=20ラン) | 5.26×10⁵ | 4.4 h | 8.0 h | ― |
| endogenous_accept D17(100体×14日×30ラン) | 7.89×10⁵ | **6.6 h** | 12.0 h | ― |
| 30 日長期ラン(100体×30日×1本) | 5.63×10⁴ | 0.5 h | 0.9 h | mock エンジンだけで 18.0 分【実測】なので実 LLM 側が律速 |
| model×k 4 セル(15体×2日×8ラン) | 3.2×10³ | <0.1 h | <0.1 h | ― |

**合計の申告値**

| 内訳 | 時間 |
|---|---|
| Day-0 ベンチ 5 項目(疎通/req-s/prefix cache/spec/mock エンジン単価) | **2〜3 h**(`finals-hardware-plan.md` §2) |
| Day-1 スモーク(2.5 万体 × 1 シミュ日・checkpoint→resume 往復) | ~6 h |
| 観察ラン(本命・段階昇圧込み) | **34〜168 h**(規模による) |
| k 掃引(D12) | 4〜25 h |
| endogenous_accept(D17) | 7〜12 h |
| 30 日ラン(D15・余剰枠)+ model×k(任意) | ~1 h |
| 障害復旧・再走・解析(analyze スイート・納品物再生成) | ~20 h |
| **合計** | **堅い着地 ≈ 75〜110 h / 最大到達目標 ≈ 180〜255 h** |

> **フォームには「合計 約 200 時間」と書く**(保守前提 = 開放 10 日なら上限 240 時間の枠内。最大到達目標を
> 狙いつつ障害・再走の余白 40 時間を残す設計)。公式日程は **8/15–8/30 の 16 日**(§0.1)なので、
> 全期間開放なら上限 384h でさらに余裕が出る。
>
> **正直な註記(そのままフォームに添えてよい)**: 上記 req/s は **±50% の推定値**であり、
> **Day-0 ベンチ(`vllm bench serve --random-input-len 1300 --random-output-len 320`)で実測に置換するまで
> 壁日数は確定しない**(`w2-execution-plan.md` §3.2 / `finals-hardware-plan.md` §2-②)。
>
> **本書計算から出た運用上の含意(重要)**: **8B を主力にすると在場 25 万 × 10 シミュ日は 304 h となり
> 240 h 枠を超える**。8B を選ぶなら (i) 在場を 10 万級に落とす(121 h)か (ii) シミュ日数を 7 日に削る、の
> どちらかが要る。**4B なら 25 万 × 10 シミュ日が 168 h で枠内**。→ D3(モデル選択)は D4(規模)と
> 一体で当日決める必要がある。

### 2.5 必要な GPU メモリ

**回答: 168GB(フル)= 24GB × 7 基。**

| 根拠 | 内容 |
|---|---|
| 配置方式 | **1 GPU = 1 vLLM レプリカ(データ並列)**。TP 分割はしない → 各 GPU が重み一式 + 自分の KV キャッシュを持つ。7 枚すべてを使い切る構成(`conf/profiles/finals-vllm7.yaml` の servers 7 本) |
| 1 枚あたりの内訳 | `--gpu-memory-utilization 0.90` → 実効 ~21.6GB/枚。重み(4B Q4_K_M ≈ 2.5GB / 8B INT4 ≈ 5GB)を除いた **~16.6〜19.1GB が KV キャッシュ**。`--max-model-len 8192`・呼形状 ~1,300 tok 入力 / ~320 tok 生成(reflect のみ ~768 tok 上限)(`finals-hardware-plan.md` §1.1・§2-①) |
| なぜフル 168GB か | ①在場数万〜25 万体を捌く集約 req/s は**レプリカ数に比例**する(7 枚 = 7 倍)、②sticky + prefix caching の効きは 1 枚あたりの KV 容量に依存し、24GB は KV が細いので枚数で補う、③VLM を立てる場合はテキスト 6 + VLM 1 に分割(D6)。**部分利用(80GB/140GB)では観察ランの規模が 1〜2 段落ちる** |
| ホスト側 RAM | **未確定**(`finals-hardware-plan.md` §6-3)。30 日 100 体で 2.0GB(checkpoint_every=1440)【`longrun-estimate.md` §4】、在場 1 万×1 シミュ日のリハーサルで **RSS ~14.5GB【実測】**(`finals-day1-decisions.md` 統合リハーサル実測)。25 万体は数百 GB 級の懸念があり **Day-0 に mock ベンチで実測**する |
| ストレージ | **未確定**(同 §6-4)。イベント量は在場 1 万×1 シミュ日で **16.2M イベント/日【実測】**、試算 4.68 億/10 日(D8) |

---

## §3 設問3「GitHub をパブリックにしないといけないらしい。その仕方と、するべきなのか」

### 3.1 結論(先に)

**公開は「任意」ではなく主催の必須要件。**
`docs/AUTOMATA第2回ハッカソン案.md` の「**最終提出物**」節に明記:

> 最終提出物は以下です。
> - 発表LT
> - **GitHubリポジトリ公開**

加えて審査項目に「**MVPやGitHubで実装進捗が見えるか**」がある(同・運営メモ節)。
応募時の「GitHubリポジトリ」は任意提出だが、**最終提出物としての公開は必須**。

**また、本リポジトリは公開を前提に既に整備が始まっている**: `ETHICS.md` の冒頭が
「本方針は **AUTOMATA 第2回ハッカソンの公開要件**、および設計文書 docs/design.md(D17)・
リスク台帳 docs/risk-register.md(R17)に基づく」と明記している(実査)。

→ **推奨結論: 公開に応じる。ただし §3.4 のチェックリストのうち未了 3 件(A/B/C)を片付けてからスイッチを押す。**
なお現行の運用ルールは「GitHub **非公開**リポジトリ + 三重バックアップ」(2026-07-13 決定・
`finals-day1-decisions.md` §2 / memory `github-repo`)なので、**公開はこの既定方針の変更にあたる**=最終判断はユーザー。

### 3.2 公開の手順(GitHub UI)

対象: `https://github.com/spacedream6090-svg/shibuya-simulation`(`git remote -v` 実査。**個人アカウント所有**=
組織移管や org のポリシー確認は不要)。

1. リポジトリページ → **Settings** タブ → 左メニュー **General**(既定表示)
2. ページ最下部の **Danger Zone** → **Change repository visibility** → **Change visibility**
3. **Make public** を選択 → 警告文の各チェックボックスに同意
4. 確認欄に **リポジトリ名を正確に入力**(`spacedream6090-svg/shibuya-simulation`)
5. **I understand, change repository visibility** を押下 → 即時に公開

**押す前後の注意**

- **公開されるのは現在のファイルだけではない**: **全コミット履歴・全ブランチ・タグ・Issue・PR・
  Actions のログ**がすべて閲覧可能になる。過去に消したファイルも履歴から復元できる(→ §3.3 の全履歴実査が要る理由)。
- **戻せない部分がある**: 後で private に戻すことは可能だが、公開中に fork / clone / アーカイブされたものは回収できない。
- **保護ブランチ**: 現在ブランチは `main` のみ(`git branch -a` 実査)。公開後は誤 push・誤 force-push を避けるため
  Settings → Branches → **Add branch protection rule**(`main` に対し force push 禁止・削除禁止)を推奨。
- **公開直後に有効化すべきもの**: Settings → **Code security and analysis** → **Secret scanning** と
  **Push protection** を ON(public リポジトリでは無料)。今後の誤コミットを GitHub 側でも止められる。
- **コミットのメールアドレスが公開される**: 全 135 コミットの author/committer が単一の個人メールアドレス
  (実査確認・本書には値を記載しない)。これは公開後、誰でも取得できる。許容するか、
  GitHub アカウント設定で今後を noreply メールに切り替えるか(過去分の書き換えは全履歴 rewrite = 全 commit hash が変わる)を選ぶ。実務上は許容が一般的。

### 3.3 公開前チェックリスト — **本書で機械確認できたもの(実査結果つき)**

> 実施日 2026-07-27・対象 = 全 135 コミット(`git rev-list --all --count` = 135)・追跡 668 ファイル・
> pack サイズ 8.35 MiB(`git count-objects -vH`)。**外部ツール(gitleaks / trufflehog)はインストールせず、
> git + grep でできる範囲**で実施。**シークレット値は一切本書に記載していない**(検出は「パス」と「文字種クラス」のみ出力)。

| # | 項目 | 実行したこと | **結果** |
|---|---|---|---|
| **1** | 全履歴 シークレットスキャン(高信頼パターン) | `git grep -l -I -E "(sk-[A-Za-z0-9]{20,}\|ghp_…\|gho_…\|github_pat_…\|AKIA[0-9A-Z]{16}\|xox[baprs]-…\|-----BEGIN … PRIVATE KEY-----\|AIza…)" $(git rev-list --all)` | **✅ 0 件** |
| **2** | 全履歴 汎用キー literal | `git grep -l -I -i -E "(api[_-]?key\|access[_-]?token\|secret\|password\|passwd\|bearer)['\" ]*[:=]['\" ]*[A-Za-z0-9_-]{16,}" $(git rev-list --all)` | **⚠️→✅ `tests/test_api_backends.py` のみ**。中身を確認したところ `"sk-DUMMYKEY-openai"` 等の**明示ダミー**で、テストは monkeypatch で環境変数を差し込む形。加えて同ファイルには「secret が出力に混入しないこと」を検証する assert がある。**問題なし** |
| **3** | ODPT consumerKey の漏洩 | 全履歴で `consumerKey=[A-Za-z0-9._-]{6,}` を抽出し、値を出力せず**文字種クラスのみ分類** | **✅ `docs/research/shibuya-buildings-traffic-odpt.md` の 6 箇所のみ。全履歴を通じて "大文字+アンダースコアのみ"(len=10 / 15)= プレースホルダ**。実キーは 0 件。`odpt-integration.md` §(d)4 の「コード・リポジトリ・ログ・成果物に埋め込まない」は守られている |
| **4** | 秘密ファイルの誤コミット | `git log --all --diff-filter=A -- "*.env" ".env*" "*secret*" "*credential*" "*.pem" "*.key"` | **✅ 0 件** |
| **5** | gitignore 済みパスの**履歴混入** | `git log --all --oneline --diff-filter=A -- <path>` を 7 パスに実行:<br>`runs/` `data/plateau/` `data/persona_pool/` `data/odpt_challenge/` `.claude/settings.local.json` `shibuya　バックアップ/` `uv.lock` | **✅ 全て 0 件(一度も add されていない)**。裏付け: pack が **8.35 MiB** しかない(数百 MB 級の persona_pool や runs が入っていれば桁が違う) |
| **6** | `.claude/` の追跡状況 | `git ls-files .claude/` | **✅ 0 件**(ローカル設定は一切追跡されていない) |
| **7** | ローカル絶対パスの混入 | `git grep -l -I -E "C:\\\\Users\\\\|/Users/[a-z]"` | **✅ 0 件** |
| **8** | LICENSE ファイルの有無 | ルート `ls` + `git ls-files \| grep -i licen` | **❌ ルートに LICENSE 無し**。存在するのは第三者ライセンス 2 件のみ:<br>・`reference/2d-fire-sim/LICENSE.txt` = **GNU GPL v3.0**<br>・`viz/vendor/LICENSE` = **three.js MIT**(`three.min.js` / `OrbitControls.js` に対応・同梱済みで適合) |
| **9** | GPL コードの同梱 ★最重要 | `reference/2d-fire-sim/`(14 ファイル)を実査。`grep -rn "2d-fire-sim" src/ scripts/ viz/ conf/ tests/ ops/ pyproject.toml` | **⚠️ 要対処。GPL-3.0 の第三者プロジェクトが初回コミット(`2727e91`)から全履歴に在籍**。ただし**本体コードからの import / 参照は 0 件**で、`docs/design.md` L197・`docs/impl-foundations.md` L18 に「**読み取り参照のみ・import 禁止**」と明記されている。上流の著者名・リポジトリ URL は同梱 README に記載が無い(添付動画 URL のみ) |
| **10** | 主催の内部メモの同梱 | `docs/AUTOMATA第2回ハッカソン案.md` を実査 | **⚠️ 要判断。「# 運営メモ / ここから下は公開前に整理する項目です」以下**に、連携候補の社名(公開時点で未確定なら削除、と主催自身が注記)・審査基準・未決事項が含まれる。**主催の非公開前提の資料を公開リポに置くことになる** |

### 3.4 公開前に片付けるべき 3 件(未了・親/ユーザー判断)

**(A) `reference/2d-fire-sim/`(GPL-3.0)の扱い — 推奨: 削除**

- 事実: 本体から一切使われていない参照専用コピー。GPL-3.0。上流の著作者表示・URL が同梱物に無い。
- 選択肢:
  - **(a) 公開前に削除【推奨】** — 「単なる集積(mere aggregation)」の主張は理屈としては可能だが、
    ①自リポの LICENSE(Apache-2.0 想定)と紛らわしく、②審査員・第三者に copyleft 汚染の疑いを与え、
    ③上流の著作権表示が無い状態での再配布は GPL 第4条(適切な著作権表示の保持)を満たしているか確認できない。
    使っていないものを残す利得がない。
  - (b) 残す — その場合は `NOTICE` に「第三者著作・GPL-3.0・未改変・本体からは未使用」と明記し、
    **上流リポジトリ URL と著作者名を補記**する(現状は補記できる情報が手元に無い)。
- **削除の実務**: 作業ツリーから消すだけなら `git rm -r reference/2d-fire-sim` + commit で足りる
  (**履歴には残る**)。履歴からも消すなら §3.5 の filter-repo。
  → 「使っていない参照コードが履歴に残っている」だけなら実害は小さいので、
    **まず作業ツリーから削除 + NOTICE 追記**で足り、履歴書換までは要らない、という判断も合理的。**親の判断事項**。

**(B) LICENSE の選定 — 推奨: Apache-2.0(+ データは別建て)**

- 現状ルートに LICENSE が無い = **法的には「All rights reserved」**。この状態で public にすると、
  審査員も第三者もコードを合法的に利用・fork できない(GitHub 上で見ることはできる)。**公開と同時に置くべき**。
- **推奨 Apache-2.0**。理由:
  1. 使用モデル群(Qwen3 = Apache-2.0 / huihui abliterated = Apache-2.0)と整合(`model-contrast-setup.md` §「実在確認」)。
  2. 設計上参照した先行 FW(Concordia = Apache-2.0 / AgentScope = Apache-2.0)の系列(`docs/research-scope.md` build-vs-reuse)。
  3. 特許条項があり研究コードの公開標準。
  - MIT でも可(より短い)。**GPL は選ばない**((A) で GPL コードを外す前提)。
- **データはコードと別ライセンスで明記する**(下表)。README に「Code: Apache-2.0 / Data: 各出典に従う(下表)」の
  2 段構えを書くのが定石。

| 同梱データ | 出所・ライセンス | 公開可否の判定 |
|---|---|---|
| `data/jinryu/*.csv` | 国交省「全国の人流オープンデータ」(Agoop 換算人口値)・**政府標準利用規約 2.0(license_id=ogl・CC BY 4.0 互換)** | **✅ 出典明記の上で再配布可**。`data/jinryu/SOURCE.md` に出典・定義・DL 元 URL を既記(実査)。ODPT チャレンジ等の再配布制限データとは異なる、と同ファイルが明言 |
| `data/odpt/*.json` + `data/odpt/gtfs/TokyoMetro-Train-GTFS.zip` | 公共交通オープンデータセンター(ODPT)**オープン枠**。`_index.json` の `_meta` に出典・免責・attribution を自動付与済み(実査) | **⚠️ 条件つき可**。`docs/research/odpt-integration.md` §(d)3「静的データのキャッシュ(取り込み)は許容(規約改定で取り込み禁止項目は削除)」+ §(d)1 出典表示義務。**ただし同 §(d)6 が「商用/非商用の別・最新の禁止事項は実運用前に規約原文を再確認すること」と自ら註記**している → **公開前に developer.odpt.org の規約原文を再確認**(本書では未確認)。**チャレンジ枠 `data/odpt_challenge/` は gitignore 済み・履歴混入 0 件を実査確認**(§3.3-5) |
| `data/shibuya_osm*.json` / `env/shimokita/*` | OSM 由来。`meta.attribution` = **"© OpenStreetMap contributors (ODbL)"**(実査) | **✅ 可・ただし ODbL の share-alike**。派生データベースを配布する以上、ODbL 継承と出典表示が要る。**コード(Apache-2.0)とデータ(ODbL)を分けて明記**する必要あり |
| `data/floorguide_shibuya.json` / `data/floor_layouts.json` | 公式フロアガイド等からの**事実データ**。`meta.note` に「詳細な間取りは非公開のため収録せず・**店名/ブランド名は不記載(カテゴリのみ)**」と記載、`meta.sources` に出典一覧(実査) | **✅ 可**。事実の集合であり、既に出典と収録範囲の限定が自己文書化されている |
| `data/organizations_shibuya_wide11k.json`(10.9MB・最大の追跡ファイル) | `scripts/build_orgs.py --dist` による**手続き生成の合成台帳**。`meta.note`「架空の組織台帳(R17: 実在企業名・学校名なし)」・`meta.honesty`「事業所数構成比=東商渋谷支部(平18)骨格」(実査) | **✅ 可**(合成物・センサス由来の分布のみ利用) |
| `viz/vendor/three.min.js` / `OrbitControls.js` | three.js **MIT**・`viz/vendor/LICENSE` 同梱(実査) | **✅ 可**(ライセンス同梱済みで要件充足) |
| `tests/data/golden_baseline_l1.json`(2.7MB) | 自作のゴールデン基準(シミュ出力) | ✅ 可 |

**(C) `docs/AUTOMATA第2回ハッカソン案.md` の運営メモ — 主催に確認 or 削除**

- 「ここから下は公開前に整理する項目です」以下は主催の内部メモ。**主催に確認するか、当該節を削除**するのが安全。
- 削除しても履歴には残るため、厳密にやるなら §3.5 の filter-repo。ただしこれは主催自身の資料であり、
  **一言確認すれば済む可能性が高い**ので、まず確認を推奨。

**(D) あわせて整備を推奨(公開の質を上げる・審査項目「実装進捗が見えるか」に直結)**

- `README.md`: 既に研究課題・セットアップ・主要コマンド・アーキテクチャが揃っている(実査)。
  追記すべきは **①ライセンス節(Code/Data の 2 段)②再現手順(mock で 1 コマンド動く例)③成果物の在り処**。
- `ETHICS.md`: **既に整備済み**(合成データのみ・実在個人団体不使用・abliterated の生出力非公開・
  LLM-judge は補助指標・OSM 出典)。公開要件を踏まえた内容になっており、**追加作業は不要**と判断。
- 外部ツールでの二重確認(未実施・**インストールが必要なので親/ユーザー判断**):
  ```bash
  # gitleaks(全履歴)
  gitleaks detect --source . --log-opts="--all" --redact -v
  # trufflehog(全履歴・検証済みのみ表示)
  trufflehog git file://. --only-verified
  ```
  本書の git ベース実査では 0 件だったが、正規表現の網羅性は外部ツールに劣る。**あれば回す**価値がある。
  なお `git grep <pattern> $(git rev-list --all)` は本書で実施した方法で、`git log -p | grep` より遥かに軽い
  (blob を revision ごとに直接検索するため。ただし 135 revision × 668 ファイル程度の規模だから成立する方法で、
  数千コミット規模では専用ツールのほうが速い)。

### 3.5 万一 履歴に問題があった場合の代替手段(現時点では**不要と判断**)

**(i) 特定パスを全履歴から削除 — `git filter-repo`**

```bash
pip install git-filter-repo
# 例: GPL 参照コードと主催メモを全履歴から除去
git filter-repo --invert-paths --path reference/2d-fire-sim --path "docs/AUTOMATA第2回ハッカソン案.md"
# → 全 commit hash が変わる。remote を付け直して force push が要る
git remote add origin https://github.com/spacedream6090-svg/shibuya-simulation.git
git push --force --all && git push --force --tags
```
- 影響: 既存 clone は再取得が必要。三重バックアップ(git / 日次 mirror / 日付 zip)のうち
  **mirror 側も同じ書換をするか、書換前の履歴をローカル退避しておく**こと。

**(ii) クリーンな公開用ミラー(履歴 squash)**

```bash
git checkout --orphan public
git add -A
git commit -m "Initial public release (history squashed)"
# 別リポ(例: shibuya-simulation-public)へ push
```
- **非推奨**。審査項目「MVPやGitHubで実装進捗が見えるか」を自ら潰す(135 コミットの開発履歴は
  本プロジェクトの強みそのもの)。**§3.3 の実査で履歴書換が必要な事実は見つかっていない**ので、
  この手段を採る理由は現時点で存在しない。

### 3.6 推奨結論(草案・最終判断は親/ユーザー)

> **公開する。**要件(最終提出物「GitHubリポジトリ公開」)であり、`ETHICS.md` は既に公開要件を前提に整備済み。
> 全 135 コミットの機械実査でシークレット・巨大データ・ローカル設定の混入は **0 件**であり、
> 履歴書換(filter-repo / squash)は**不要**と判断する。
>
> ただし**公開スイッチを押す前に次の 3 点だけ**片付ける:
> 1. **`reference/2d-fire-sim/`(GPL-3.0・本体未使用)を作業ツリーから削除**する(または NOTICE で第三者著作・未使用を明記)。
> 2. **ルートに LICENSE を置く(Apache-2.0 推奨)**+ README に「Code: Apache-2.0 / Data: ODbL(OSM)・
>    政府標準利用規約 2.0(人流)・ODPT 利用規約」の 2 段ライセンス表記を追記。
> 3. **`docs/AUTOMATA第2回ハッカソン案.md` の運営メモ節**の扱いを主催に一言確認(または当該節を削除)。
>
> あわせて **公開直後に Secret scanning + Push protection を ON**、`main` に branch protection を設定。
> ODPT の規約原文再確認(`odpt-integration.md` §(d)6 が自ら求めている)は公開前に一度行う。

### 3.7 実施記録(2026-07-28・本節の計画とは方式を変更して実施)

ユーザー確認(4 点: 方式・LICENSE・作者メール・タイミング)の上で **§3.2 の「既存リポの可視性切替」ではなく
「フィルタ済みミラー公開」方式**で実施した(ユーザー制約「GitHub 上で処理できるものは GitHub 上で・
フォルダー修正は最小限」に適合。§3.5-(i) の filter-repo を**一時 clone 上でのみ**使う変形)。

- **公開 URL**: https://github.com/spacedream6090-svg/shibuya-simulation-public (private 本体は無傷で維持)
- 手段: `ops/publish_public_mirror.ps1` = 一時 clone → `git filter-repo` で `reference/2d-fire-sim/` +
  `docs/AUTOMATA*` を全履歴除去 + 作者メールを公開側のみ noreply へ書換 → push。決定論なので再実行は
  fast-forward(提出前の同期が 1 コマンド)。
- 検証実測: ミラー 140 コミット = private 140 コミット(除去 2 パスだけを触るコミット無し)・除去パスの
  履歴残存 **0 件**・作者/コミッタメールは noreply 単一・シークレット走査は擬陽性 1 件のみ(§3.3 の監査表が
  スキャンパターン文字列自体を引用している行)。
- 設定: Apache-2.0 を GitHub が自動検出・Secret scanning + Push protection 有効・`main` へ force push/削除禁止
  (可視性変更直後は "Repository has been locked" 403 → 約 20 秒後のリトライで成功)。
- フォルダー修正は**追加 4 ファイルのみ**(LICENSE / NOTICE / README ライセンス節 / 同期スクリプト・コミット 8092625)。削除ゼロ。
- 未了のまま残るもの: ODPT 規約原文の再確認(§4-7。developer.odpt.org が SPA で自動取得不能・既存リサーチ
  結論のまま)・主催メモ節を除外した旨の主催への一言確認(任意・ユーザーから)。

---

## §4 未確定として残した項目(本書で埋めなかったもの)

| # | 項目 | なぜ未確定か |
|---|---|---|
| 1 | GPU 開放の実期間 | **ほぼ解消(§0.1)**: 公式サイトで本選 = 8/15–8/30(16 日)・GPU 利用申請締切 8/9・利用チーム発表 8/14 を確認。残る未確定は開放開始の厳密な日(8/14 直後か 8/15 か)のみ。申告値 200h は保守前提(10 日=240h)でも枠内 |
| 2 | GPU の正確な銘板(A5000 24GB か RTX 5000 Ada 32GB か) | 168GB÷7=24GB と逆算しているが未確認(`finals-hardware-plan.md` §6-1) |
| 3 | ホスト RAM・ストレージ容量・ネット接続・24h 占有か | すべて `finals-hardware-plan.md` §6 の [要確定]。25 万体は RAM が壁になりうる |
| 4 | 主力モデル(4B か 8B INT4 か)・量子化方式・spec 採否・VLM 有無 | **Day-0 ベンチで当日確定**(D1/D3/D6)。フォームには第一候補 + 当日確定の旨を書く |
| 5 | 本選 k 掃引の確定セル数 | 文書間で不一致(案A: N=100×100日×4条件・2026-07-09 / 案B: 7–14日・人数多め・2026-07-24)。§1.2 で両論併記。**親の決定事項** |
| 6 | endogenous_accept フェーズ1の検収状況 | D17 が「実装完了を条件に回す価値が高い」としており、フェーズ1〜3 は実装済み(直近コミット)だが**本選投入の可否は phase3_go ゲート待ち** |
| 7 | ODPT 利用規約の最新原文(商用/非商用の別・禁止事項) | `odpt-integration.md` §(d)6 が自ら再確認を求めている。**本書では未確認** |
| 8 | 上流 `2d-fire-sim` の著作者・リポジトリ URL | 同梱 README・LICENSE.txt から特定できず。NOTICE で正しく帰属表示するには要調査 |
