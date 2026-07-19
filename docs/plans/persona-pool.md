# ペルソナプール設計計画(第37バッチ 2026-07-19・計画のみ・実装なし)

体制: ユーザー構想 → Opus リサーチ+設計計画(本書。リポジトリ読取+軽Webリサーチ・**コード変更なし**)。
本書は素材であり、実装着手は `pre-coding-alignment` / `ask-before-extending` に従いユーザー合意の後。

## 0. ユーザー構想(2026-07-18)

本番=現実渋谷の忠実再現。要件:

1. **全員が毎日範囲内にいるわけではない**(観光・会議来訪は毎日は来ない)。
   → **同時存在数の数倍のペルソナプール**を用意し、日次でローテーションさせる。
2. 行政データの肉付け**以外**の作成方法も検討する。
3. **エージェントが触れるサービスの提供者で範囲内にいる人**(電車運転士・店員・配信者・駅員・
   タクシー運転手など)は**全てエージェント化**する。
4. **議員はペルソナで事前決定**する(選挙はしない)。

---

## 1. 既存資産の棚卸し(本設計の出発点)

### 1.1 ペルソナ生成の2系統(どちらも決定論・LLM負荷ゼロで名簿を吐く)

| スクリプト | 方式 | 主入力 | 出力 | 特徴 |
|---|---|---|---|---|
| `scripts/gen_personas.py` | **手続き生成 + プール→無作為抽出** | 内蔵の語彙・分布パラメータ | `personas_*.json` / `persona_pool.json` | `--pool N --sample M` の**2段構造が既に存在**。`random.Random(seed)` のみ=完全決定論 |
| `scripts/build_personas.py` | **IPF骨格 × 尺度分布 × LLM文章化(VS)** | `data/shibuya_population.json`(周辺分布) | `personas_*.json` | 年齢×性別×職業の結合分布をIPFで推定→骨格抽出。`--civil-share` で公務員注入 |

- **既に「プール余剰生成→抽出」の思想がコードにある**(`gen_personas.py` docstring: 「本番では余剰に生成したプールから無作為抽出」)。`data/persona_pool.json`(pool_size=500)が実在の中間生成物。
- ただし現状の「プール」は**生成時の一回抽出**であり、**ランタイムのローテーションではない**(下記1.3)。

### 1.2 組織台帳=需要の逆算源(既に場所非依存)

`scripts/build_orgs.py` → `data/organizations_shibuya_wide.json`:

- 架空の**会社42社+学校10校**。各社に `size.employees`(従業者数=需要)・`size.band`・`roles`・
  `generalist_roles`・`workplace_poi`(地図ノード束縛)。学校は `capacity`・`timetable`。
- `data/org_assignments_*_wide.json` が `agent_index → org_id + role` を決定論ハッシュで割付。
- **含意**: 「この店に店員N人」の逆算(需要駆動生成)に必要な数量は**既に台帳の `employees` に入っている**。
  役割ペルソナ(店員)の必要数は台帳の集計だけで出せる(§4)。

### 1.3 来街者(visitor)機構の現状 — 「日内の出入り」であって「日次ローテーション」ではない

`src/society/agents/persona.py::build_agent` と `scheduler.py::_phase_wake_and_returns` の実装:

- 名簿 entry の `visitor:true` は**街の外に生活基盤**を持つ主体。`commute:true` はその下位型(流入通勤者)。
- **日内サイクル**: 夕方 `depart/bedtime` で `loc="outside"`(範囲外へ退出)→ 翌朝 `return_at` で
  `enter_area` して復帰。終電後は始発待ち(`transit.has_service`)。
- `economy.visitor_refresh`(既定OFF・production ON): 帰宅のたび手持ちを `allowance_visitor` まで補充
  (財布の恒久破綻対策 P2)。**ペルソナの入れ替えではない**。
- **ロード方式**(`simulation.py` L438-442):
  ```python
  for agent_id in range(int(cfg.run.n_agents)):
      entry = roster[agent_id % len(roster)] if roster else None
  ```
  → **生存エージェント数 = `run.n_agents` に固定**。名簿はサイクリックに割当。名簿が n_agents 以上あっても
  **超過分は一度も具現化しない**(現状 n_agents=100, 名簿=100 で 1:1)。

**結論: 「同時存在数の数倍のプールから日次で誰が入域するか」を選ぶ機構は現状存在しない。** これが本設計の核。

### 1.4 決定論とチェックポイントの土台(ローテーション設計の制約)

- `src/society/rng.py::RngHub`: **完全にステートレス**。乱数は `stream(用途, id, step)` から都度導出。
  → プレゼンス選択を `stream("presence", persona_id, day)` と書けば、**他者の実行順に依存しない・
  リプレイ完全再現**(R1原則)。
- `src/society/engine/checkpoint.py`: **乱数状態を保存しない**(master_seed から再導出)。`sim.agents`(生存リスト)を
  pickle。`config_hash` が **`run.n_agents` を含む**ため、n_agents を変えた resume は弾かれる。
  → プールを入れるなら「pool_size / 同時上限」を config 化し、**日カウンタから presence を再計算**する設計にすれば、
  presence 自体はチェックポイントに保存不要(ステートレス)。**永続化が要るのは個々のペルソナの記憶・所持金・関係のみ**。

### 1.5 役割ペルソナの現状 — 公務員のみ・勤務地なし

- 現状の役割ペルソナは**公務員(区職員/警察官/消防士)のみ**(`build_personas.py --civil-share`、`gen_personas.py` の
  `_CIVIL_OCCS`)。地図に交番/消防署POIが無く、**空間上の勤務地を持たない**(給与は `government` の日次ペイロールで支給)。
- **駅員・運転士・配信者・タクシー運転手は未実装**。ユーザー要件③はこれらの新規役割化を要求。
- 配信者の接続先候補は既に存在: `conf/production.yaml` の `info_env.influence.enabled`(インフルエンサー非対称/バイラル)。
- 議員: `institution_routes.assembly.size=9`(渋谷区議会34議席を100体スケールへ圧縮)+ `vote.enabled/realism`(**選挙ON**)。
  → 要件④(事前決定・選挙なし)と**現config が衝突**(§7 OPEN)。

---

## 2. プールの層構造(5層)

同時存在(present)= LLM 計算コストの源。プール規模 = 記憶・アイデンティティ保持の source。この2つを分離する。
現実の渋谷: 夜間人口243,883 / 昼間人口551,344(昼夜比≈226%)・区外流入通勤通学≈74%(`data/shibuya_population.json`)。

| 層 | 定義(現実の対応) | プレゼンス様式 | プール倍率※ | 主生成方法(§3) | 必要属性(既存スキーマ+追加) |
|---|---|---|---|---|---|
| **L1 住民** | 夜間人口。街に住む | **常時present**(日内は睡眠/外出) | ×1(回転しない) | (a) IPF + (c) 深み | 既存フル。`visitor=false` |
| **L2 域内従業者** | 通勤流入者+店員。昼間人口の中核 | **勤務日present**(暦+シフト) | ×1.2〜1.5(休日/シフト非番) | (b) 需要駆動 + (a) 人口属性 | 既存 + `shift_pattern`・`org_id`(配属)・`residence_line` |
| **L3 定期来街者** | 通学生・常連 | **周期present**(通学日/曜日常連) | ×1.5〜3 | (a)+(b) + (d) 常連セグメント | 既存 + `visit_cadence`(週n回等) |
| **L4 非定期来街者** | 観光・買物・ビジネス来訪。**ローテーションの主層** | **低頻度present**(確率/予定) | **×数〜数十**(要件①の主対象) | (d) 観光/消費統計セグメント + (a) 属性 | 既存 + `visit_purpose`・`visit_rate`・`is_foreign`・`party_size`・`revisit`(再訪フラグ) |
| **L5 役割ペルソナ** | 議員・警察官・駅員・運転士・配信者・タクシー運転手 | **勤務時present**(当番) | ×1(数は§4式で確定) | (b) インフラ需要 + (c) 人手確認の来歴 | 既存 + `role`・`duty_pattern`・`post`(勤務地/持ち場)・(議員)`seat_id` |

※プール倍率 = プール人数 ÷ その層の平均同時存在数。**回転はほぼ L3/L4 に集中**。L1/L2/L5 は「毎日概ね同じ顔」で回転が薄い。

### 2.1 各層の生成方法と要点

- **L1 住民**: `shibuya_population.json` の夜間人口周辺分布から IPF(既存 `build_personas.py`)。回転しないので
  プール=同時数。深みが要る個体(将来のファウンダー候補)だけ (c) で来歴を厚くする(ただし §3-c の均質化リスクに注意)。
- **L2 域内従業者**: 二源合成。**(b) 需要駆動**=組織台帳 `employees` から「この店に店員N人」を逆算し職業テンプレを起こす。
  **(a)**=通勤流入の年齢×性別×職業を `inflow`(commuter_share 0.74・到着二峰・沿線タグ)から。配属は `build_orgs.py` を流用。
  シフト(週n日・時間帯)を `shift_pattern` に持たせ、非番日は present から外す(回転の薄い源)。
- **L3 定期来街者**: 学生は学校 `capacity` から逆算(需要駆動)+ 通学暦。常連は (d) の来街セグメント(頻度分布)から
  `visit_cadence` を与える。**同一ペルソナが規則的に再登場**=記憶が育つ層(関係・行きつけの形成観察に重要)。
- **L4 非定期来街者(回転の主層)**: (d) 観光統計・消費者セグメントの構成比(来訪目的・国籍・滞在時間・同行人数)を
  骨格に、(a) で人口属性を肉付け。各人に `visit_rate`(来訪確率/日)を与え、日次でプレゼンスを抽選(§5)。
  大多数は稀にしか来ない(=大きなプール倍率)。一部に `revisit=true` を与え、**同じ観光客が数日後に再訪**(記憶保持)。
- **L5 役割ペルソナ**: インフラ需要から人数を確定(§4)し、当番(`duty_pattern`)で present。来歴に固有名の混入リスクが
  あるため (c) の**人手確認キュー**を通す(捏造ガード=`environment-autogen.md` stage5 と同思想)。

---

## 3. 作成方法の比較(層×方法マトリクス)

4方法の品質・コスト・バイアスと使い分け。**単一方法では全層を賄えない**——層ごとに主/従を組む。

### 3.1 各方法の評価

| 方法 | 品質(現実整合) | コスト | 主なバイアス | 本プロジェクトの既存資産 |
|---|---|---|---|---|
| **(a) 行政統計IPF/IPU** | 周辺分布は高精度。**平均は当たる** | 低(表を一度整備すれば横展開) | **裾・希少交差セルが痩せる**(empty-cell)/ 結合の弱依存はヒント頼み | `build_personas.py`(IPF)・`shibuya_population.json`・環境自動生成 v1(D2) |
| **(b) 需要駆動生成** | **数量が現実の供給に接地**(店員数=店の需要) | 低(台帳の集計のみ) | 職業テンプレが定型/役割内の個体差が薄い | `build_orgs.py`・`organizations_shibuya_wide.json`(`employees`/`roles`) |
| **(c) LLM一括+人手確認** | 文章・来歴の**深みは最高**(Park型接地に近づく) | **高**(生成トークン+確認工数) | **均質化/mode collapse**・**捏造(confabulation)**・リッチ過ぎで manifold collapse | `build_personas.py` の VS(Verbalized Sampling)・`construct_violations` バリデータ |
| **(d) 実在調査データの匿名合成** | **来訪構成が現実に接地**(観光目的・国籍・滞在) | 中(統計セグメントの整備) | セグメント粗さ/**個人特定リスク→匿名合成必須**(実個人を入れない) | (新規)観光統計・消費セグメントの整備が要 |

### 3.2 層 × 方法マトリクス(◎主/○従)

| | (a) IPF/IPU | (b) 需要駆動 | (c) LLM+確認 | (d) 匿名合成 |
|---|---|---|---|---|
| **L1 住民** | ◎ | | ○(深み・少数) | |
| **L2 域内従業者** | ○(人口属性) | ◎(店員数) | | |
| **L3 定期来街者** | ○ | ◎(学生=capacity) | | ○(常連頻度) |
| **L4 非定期来街者** | ○(属性肉付け) | | | ◎(来訪セグメント) |
| **L5 役割ペルソナ** | | ◎(インフラ需要=数) | ◎(来歴・要人手確認) | |

**設計判断の骨子**:
- **数量の接地は (b)、分布の接地は (a)、来訪構成の接地は (d)、深みは (c)**。それぞれ得意な軸が違うので層で分担。
- (c) は**全員に使わない**。LLM人間忠実度リサーチ(`docs/research/llm-human-fidelity.md`)の教訓——
  「リッチなペルソナほど manifold collapse で逆に均質化する(Chameleon's Limit)」「均質化は温度でも残る」——から、
  **ペルソナは"薄く多様に"**を既定とし、(c) は再登場する L3 常連・L5 役割など**一貫性が観測に効く個体に限定**する。
- (c)/(d) の生成物は**人手確認ゲートを通るまで pack に入れない**(捏造・固有名混入・個人特定の遮断。R17 と整合)。

---

## 4. 役割ペルソナの必要数(概算式・実数は population リサーチ側が供給)

台帳・地図・インフラの**数量から人数を逆算する式**のみを示す。実数(店舗数・駅数・交番数・便数)は
population/インフラ・リサーチが `shibuya_population.json` 系や地図・台帳に投入する。

記号: `present` = ある瞬間に範囲内に居る当該役割の期待人数(=LLMコスト源)。`pool` = 交代要員込みの総数。

- **店員(L5と L2の境界。既に台帳にある)**
  `present_staff ≈ Σ_店(営業中) [ staff_per_shift ]`、`pool_staff = Σ_店 employees`(台帳 `size.employees`)。
  同時在店 = `employees × shift_overlap_ratio`(週n日・1日1シフトなら概ね 0.2〜0.4)。
  → **`organizations_shibuya_wide.json` の `employees` 合計が pool、その shift 率が present。追加調査ほぼ不要。**

- **駅員(新規)**
  `present_station = Σ_駅施設 [ gate_posts + platform_posts + office_posts ] × shift_factor`。
  渋谷は約9路線が乗り入れるが**物理的な駅施設数はそれより少ない**(`docs/research/rail-shibuya.md`)。
  駅施設数 × 持ち場数 が骨格。`post` に改札/ホーム/事務室を持たせる。

- **運転士(新規・注意)**
  `present_driver ≈ Σ_路線 [ trains_in_service(t) × (dwell_in_bbox / headway) ]`。
  **大半の列車は渋谷を"通過"**(山手・埼京・東横⇔副都心・田都⇔半蔵門は スルー運転=`rail-shibuya.md` §2)。
  → **範囲内に物理的に居る乗務員のみ**を数える(通過中に bbox 内を走行する編成 + 終着2路線=井の頭線・
  (旧)東横ターミナルの折返し乗務)。近似: `路線数 × ピーク時運行本数 × (bbox内走行時間/運行間隔)`。
  「触れるサービス提供者で範囲内にいる人」の条件を厳密に効かせる層(全列車の運転士を実体化しない)。

- **タクシー運転手(新規)**
  `pool_taxi = 目標乗車数/日 ÷ (1台あたり乗車数/日)`、`present_taxi ≈ 客待ち台数(タクシー乗場) + 流し走行台数(bbox内)`。
  目標乗車数は `transit_ride.taxi.prob`(production=0.02)× 人日から逆算可能(現実較正済みの分担率)。

- **警察官(公務員の拡張)**
  `present_police ≈ 交番数 × officers_per_koban × shift_factor + 巡回ユニット数`。
  交番数は government リサーチが供給(`docs/research/shibuya-government.md`)。現状は勤務地POIなしの概念存在=拡張余地。

- **配信者(新規・インフラ非束縛)**
  インフラで決まらない。設計値として `n_streamers = 上位k人のクリエイター`(例: 数〜十数人)。
  `info_env.influence` のインフルエンサー非対称に接続し、街頭配信の`post`(ハチ公前等の掲出地点)を持たせる。
  **present は当人の活動時間帯**(常時ではない)。

- **議員(選挙なし・事前決定)**
  `n_council = institution_routes.assembly.size`(production=9。現実の渋谷区議会34議席の圧縮)。
  **プール=同時数=議席数で固定**。回転しない。各議員に `seat_id` と党派/信条を**事前に**与える(§7 OPEN)。

---

## 5. ローテーション機構の設計(日次プレゼンス)

### 5.1 二層のプレゼンス

現状の visitor 機構(**日内**の外出→復帰)は温存し、その**上位に「日次プレゼンス」を新設**する。

1. **日次プレゼンス選択**(新規): 日境界で、プール各人 `p` の当日 present/absent を層別に決定。
   - L1 住民: 常に present。
   - L2 従業者: `weekday_work` 暦(既存 `world.calendar`)∧ `shift_pattern(p, day)`。
   - L3 定期来街者: `visit_cadence(p)`(通学暦・週次常連)に一致する日だけ present。
   - L4 非定期来街者: `hub.stream("presence", p.id, day)` から抽選し `draw < p.visit_rate` なら present。
     `revisit=true` の個体は再訪スケジュール(初回+Δ日後)を決定論で持ち、**同一 p が再登場**。
   - L5 役割: `duty_pattern(p, day)`(当番表)。議員は常時 present。
2. **日内サイクル**(既存): 当日 present の主体だけが、既存の起床→出勤→外出→復帰→就寝の経路に乗る。
   absent の主体はドーマント(§5.3)。

### 5.2 決定論・k非依存・現実整合

- **決定論**: presence は `stream("presence", p.id, day)` の純関数(他者順・実行環境に非依存)。`gen_personas.py` の
  「pool→無作為抽出」を**日次に一般化**したもの。
- **k非依存(R1)**: presence は **k(経験→内部状態のゲイン)を一切読まない**。暦・persona固有の visit_rate・専用streamのみ。
  → k掃引の全条件で**同じ人が同じ日に present**(共通乱数)になり、**presence が k* を交絡しない**。これは重要な制約
  (`sim-improvement-analysis.md` / calibration の統制思想と整合)。
- **現実整合**: 平均同時 present 数が昼夜比(≈226%)や流入率(≈74%)を再現するよう `visit_rate` を較正
  (`calibrate_report.py` の汎用バンドで検収)。

### 5.3 再訪者の記憶持続(要件①後半)

- **ペルソナ実体は永続**: プール各人は自分の `MemoryStore`・関係台帳・所持金・意見・地位を**absent 日も保持**。
- **absent = ドーマント**: 生存 tick ループ(移動・発火・LLM)から外れる=**LLMコストゼロ**。状態は凍結(時間経過の
  副作用を与えるかは設計判断: 記憶の忘却(ACT-R)を absent 中も進めるか否かは OPEN)。
- **再登場 = 同一実体の再活性化**: 数日ぶりに present になった観光客/常連は、**前回の記憶・関係を持ったまま**戻る。
  → 「行きつけの店員と顔なじみになる常連」「二度目の渋谷で前回の場所を思い出す観光客」が自然に立ち上がる。

### 5.4 チェックポイント/resume との整合

- `checkpoint.py` は現状 `sim.agents`(生存リスト)を pickle。**プール全員(present+dormant)の永続状態**を保存対象に拡張する。
- presence は `(seed, p.id, day)` の純関数=**保存不要**。resume 時は day カウンタから**再計算**すれば present 集合が復元。
  → RngHub がステートレスな設計(§1.4)がそのまま効く。
- `config_hash` の同一性キーを `run.n_agents` 依存から **`pool.size` + `present_cap`(同時上限)** に置換
  (これらは resume で不変)。`_VOLATILE_KEYS` の運用と同じ流儀。
- **既定OFFの規律**: `pool.enabled=false`(または `pool.size == n_agents` かつ rotation なし)のとき、**現行の
  ゴールデンとバイト一致**にする(civil-share=0 / visitor_refresh=false と同じ後方互換の掟)。

### 5.5 エンジンへの影響(要 agent-core 変更・ユーザー合意前提)

- 現エンジンは**全 agent を毎 step tick**する前提。「当日 active な部分集合だけ回す」概念を新設する必要がある
  (`_phase_*` が `sim.agents` を舐める全ループに present ゲートを噛ませる)。
- `sim.agent_by_id` はプール全域を張る。L1/L2/L5 の active 集合はほぼ固定、L3/L4 が日々入れ替わる。
- **これは非自明なエンジン改変**(agent-core, `agent-operating-mode` の担当区分)。実装前に方式(presence ゲート方式)を
  提示し合意を取る(§7)。

---

## 6. 段階導入(v0 → v1 → v2)

`environment-autogen.md` のフェーズ思想(半自動→統計接続→一括生成)と足並みを揃える。

### v0 — 現行300名簿 + 役割追加(回転は最小)

- **内容**: `personas_300_civic.json` を土台に、**役割ペルソナ(駅員/運転士/配信者/タクシー/警察拡張)を注入**
  (`build_personas.py` の `--civil-share` と同型の役割注入器を追加)。組織台帳の `employees` から店員需要を突合。
  日次ローテーションは**まだ入れない**か、暦(勤務日/通学日)のみの薄い present ゲートに留める。
- **プール規模**: ≈ 同時数(数百)。回転倍率 ≈ ×1。
- **工数**: 小〜中。名簿生成スクリプトの役割注入 + 配属フックのみ(エンジン大改変なし)。
- **検収**: 役割ペルソナが当番時に present・勤務地/持ち場に着く / 非役割経路は**ゴールデンとバイト一致**
  (役割share=0 で従来同一) / ≤24step スモーク(`validation-runs-short`)。

### v1 — 数千規模(IPF/IPU + 需要駆動)+ 回転機構の投入

- **内容**: プール3,000〜5,000・同時上限 数百。**(a) IPF/IPU を実国勢調査の周辺分布に接続**(e-Stat 手動DL可=
  `environment-autogen.md` v1 の合成人口自動化)+ **(b) 需要駆動で L2/L5 の数量を接地**。§5 のプレゼンス機構を実装。
- **工数**: 中〜大。**プールローダ + 日次プレゼンス・エンジン(agent-core)+ checkpoint 拡張**が新規。
- **検収**: 属性構成が周辺分布バンド内(`calibrate_report.py`)/ 平均同時 present が昼夜比・流入率を再現 /
  **resume 決定論テスト**(save→load→続行で presence と状態が完全一致)/ k掃引で presence が k非依存(共通乱数)。

### v2 — 数万規模(LLM一括生成 + 検証)

- **内容**: プール10,000〜50,000。**(c) LLM一括**で L3常連・L5役割・少数のL1住民の来歴を厚く+
  **人手確認キュー**(文化・固有名・外国人観光客の忠実度が疑わしい層。`llm-human-fidelity.md` §2.5 WEIRD偏り)。
  同時上限は GPU で律速(本選ハードウェア)。
- **工数**: 大。バッチLLM生成 + 検証キュー + **多様性監視**(distinct-2・埋め込み分散・VS)+ 重複排除。
- **検収**: 多様性指標(VS 1.6-2.1倍・distinct-2)/ **接地率チェック**(固有名・出来事の捏造検知)/
  人手確認サインオフ(役割・外国人ペルソナ)/ 数万規模のスケール・スモーク。

---

## 7. OPEN 事項(実装前に要ユーザー決定)

1. **議員の選挙 vs 事前決定(要件④)**: 現 production は `institution_routes.vote.enabled` +
   `assembly.realism`(告示→立候補→SNTV改選)が**ON**。要件④は「事前決定・選挙なし」。
   → 選択肢: (A) 議席を事前確定ペルソナで固定し council 選挙を無効化、(B) 選挙は残すが**初期議員を事前シードした現職**
   として与える(day0 のフォールバックは既に候補0で従来方式)。**どちらにするか要決定**。
2. **エンジン改変の可否**: §5.5 の presence ゲート方式は agent-core への非自明な改変。着手可否と方式合意
   (`pre-coding-alignment`)。
3. **回転が k* を交絡しない保証**: presence を k非依存・共通乱数にする(§5.2)方針でよいか。研究の主測度(R²(k)低下)を
   守るための制約。
4. **absent 中の時間経過**: ドーマント個体の記憶忘却(ACT-R)・関係減衰を absent 日も進めるか凍結するか。
5. **プール規模と同時上限の目標値**: v1/v2 の pool.size と present_cap の具体値(GPU予算=`compute-optimization.md` と接続)。
6. **(d) 匿名合成データの調達**: 観光/消費セグメントの一次統計をどこから引くか(実個人を入れない匿名合成の設計)。

---

## 8. Webリサーチ(軽め・出典は実在確認済み)

### 8.1 合成人口(synthetic population)生成の標準手法

- **総説(最重要)**: Chapuis, Taillandier & Drogoul (2022) "Generation of Synthetic Populations in Social
  Simulations: A Review of Methods and Practices", *JASSS* 25(2)6 — 合成再構成(SR: IPF系)・組合せ最適化(CO)・
  深層生成の三系統を横断比較。<https://www.jasss.org/25/2/6.html>
- **IPF と多レベル拡張(IPU)**: 単純IPFは年齢×性別等の**個人属性の結合分布**を周辺分布から反復比例適合で推定
  (本プロジェクト `build_personas.py::ipf_joint` が該当)。世帯と個人の**両レベルを同時に満たす**拡張が
  **IPU(Iterative Proportional Updating; Ye et al. 2009)** — 世帯型の重みを個人・世帯制約の双方に合うよう反復再配分。
  大量制約では empty-cell 問題で不収束しうる。原著: <https://www.researchgate.net/publication/228963837>。
  階層拡張 **HIPF**(Müller & Axhausen, スイス合成人口): <https://www.researchgate.net/publication/254457473>。
- **手法カタログ(arXiv)**: "Generating Synthetic Population" — IPF/サンプルフリー/深層生成の実装レビュー。
  <https://arxiv.org/html/2209.09961>
- **SR vs CO**: **合成再構成(SR)**=分布から属性を生成(IPF/MCMC)。**組合せ最適化(CO)**=実サンプル個体を複製し
  目的関数最小化で実集団に適合。**COは要約統計の当てはまりは良いが計算コスト大**(上記 JASSS 総説)。
  → 本プロジェクトは SR(IPF)採用済み。数千規模までは SR で十分、CO は過剰。

### 8.2 LLMペルソナ生成の先行と品質検証(リポジトリ既調査=`docs/research/llm-human-fidelity.md` に一次確認済み)

- **接地で忠実度を買う**: Park et al. (2024) "Generative Agent Simulations of 1,000 People" — 実在1,052人に
  2時間インタビューを接地し、**本人の2週間後再テスト整合の~85%**を再現。**属性のみ(74%)より接地(83-86%)が上**。
  → プールの深み投資(§3-c)の裏づけ。<https://arxiv.org/abs/2411.10109>
- **分布シミュ能力の上限測定**: "SimBench"(arXiv:2510.17516)— 45モデルで人間**行動分布**の再現力を測定。最良でも
  40.8/100、instruct化は合意的質問で改善するが**多元的質問では劣化**(alignment-simulation tradeoff)。
  → ペルソナ多様性・裾の再現は本質的に難しい=(c)を薄く多様に運用する根拠。<https://arxiv.org/html/2510.17516v2>
- **多様性回復**: Verbalized Sampling(arXiv:2510.01171)— 「N案+確率を出せ」で mode collapse を回避(多様性1.6-2.1倍)。
  本プロジェクト `build_personas.py::llm_persona` が実装済み。<https://arxiv.org/abs/2510.01171>
- **スケールと実データ照合の先行**: AgentSociety(arXiv:2502.08691)— 1万+エージェント。移動半径・訪問地点数等の
  **行動集約指標を実測と突合**して検証。→ v2 の検収指標設計の参照。<https://arxiv.org/abs/2502.08691>

---

## 9. まとめ(素材としての示唆)

- **回転機構の核心は「present(LLMコスト源)とプール(記憶保持)の分離」**。現行 visitor 機構は**日内**の出入りで、
  **日次ローテーションは未実装**——ここが新規実装の中心(要 agent-core 合意)。
- **数量は組織台帳(需要駆動)に既にある**。役割ペルソナの人数は台帳 `employees` とインフラ数の集計式(§4)で出る。
  実数は population リサーチ側が供給。
- **方法は層で分担**: (a)分布 / (b)数量 / (d)来訪構成 / (c)深み。(c)は薄く多様に・人手確認ゲート付きで限定運用。
- **決定論とチェックポイントの土台(ステートレスRngHub)がローテーション設計に有利**: presence を純関数化すれば
  保存不要・resume再現・k非交絡が同時に立つ。
- 段階: **v0(300+役割・回転薄)→ v1(数千・IPF/IPU+需要駆動+回転投入)→ v2(数万・LLM一括+人手確認)**。
  各段の既定OFF後方互換(ゴールデン不変)を厳守。
- 実装着手は §7 の OPEN(特に議員の選挙/事前決定・エンジン改変可否・k非交絡)をユーザーと詰めてから。
