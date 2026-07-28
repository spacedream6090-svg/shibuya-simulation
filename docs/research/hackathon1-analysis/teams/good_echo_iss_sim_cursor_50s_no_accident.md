# good_echo_iss_sim_cursor_50s_no_accident（Hop-Step-Jump・6位・34.0/40）

**講評スコア**: A 創発設計 8.0 / B 世界設定 9.0 / C 発展性 **9.0** / D 技術実装 8.0 = **34.0**
（Run1/Run2 とも 8-9-9-8 で完全一致。**提出リスト外**＝ハッカソン公式提出物ではないが評価対象になった）

**リポ URL**: https://github.com/Hop-Step-Jump/good_echo_iss_sim_cursor_50s_no_accident
**規模感**: Python 8,665 行。4 層構成（`sim_core/` 3 モジュール / `domain_packs/iss_benevolence/` / `examples/spatial_demo/` / `scripts/` 13 本）+ `visualization/`（iss_habitat_demo.html, viewer.html）。**データは TSV 27 本 + YAML**で完全外部化。LLM は Cursor Composer 2（CLI 経由、provider="command"）。ライセンス GPL v3。

**姉妹リポとの関係**: `good_echo_iss_sim_cursor_100s_w_accident`（8位・33.5）と対。**50 ステップ・事故なし** vs **100 ステップ・事故あり**の条件違い。以下「50s 版」と呼ぶ。

**スライド**: 個別スライドは提出リストに無いが、レビューリポの `slides/s26-2065_2095-good-echo-hackathon.pdf`（4 ページ・テキストベース）が **good echo プロジェクト全体の結び文書**として存在し、本リポの Run B オブジェクト（聖域マーク / 持ち寄り棚 / 話しかけてOKサイン）が名指しで登場する。謝辞に「karesansui氏、バッツ氏、RERE氏、もん氏」とあり、**複数リポにまたがるチーム企画**だったことが分かる（goodecho_r の RERE も同チーム）。

---

## どんなシムか

ISS を模した閉鎖空間に、宇宙飛行士訓練を受けていない**多文化 10 名**（中国農村工場労働者 Chen Wei、インドの母 Priya、バングラデシュ工場労働者 Fatima、シリア難民 Amir、ベトナム料理人 Linh、日本の退職者 Makoto Tanaka、ケニアの義足パラアスリート Aisha、コロンビアのアーティスト Sofia、米国学生 Marcus、元フランス外交官 Henri）を置き、1 ステップ = 1 日で生活させる。

**Run A（対照群・ナッジなし）と Run B（介入群・善性オブジェクトあり）の A/B 比較**が実験の骨格。外乱イベントは Run A/B 共通で TSV に外部化され、ナッジの有無だけが差分。KPI は `reciprocity_rate`（相互性）/ `repair_after_conflict_rate`（衝突後の修復率）/ `bridge_agent_count`（橋渡し役の数）/ `load_fairness`（負荷公平性）/ `isolated_agents`（孤立者）を **domain.yaml に事前定義**している。

仮説は「**善性は性格ではなく環境と運用によって育つのではないか**」。

---

## 講評の要点

### 強み

- **A=8.0**: 場所ごとの capacity/occupancy、通信半径、「同じ場所同士 or 両者とも屋外のみ通話可能」という in-place isolation ルール、4 方向移動、火災は半径内のみ知覚可能、といった物理・知覚ルールが明示され、エージェントには占有率・距離・強度など**定量値のみ**を渡す。プロンプトは "Decide what message you want to send" / "Decide your action" と中立。**Run B のナッジは行動指示ではなく場所 description への埋め込み＝環境アフォーダンスとして配置**している点を講評は「創発設計として極めて思想的に一貫」と評価。
- **B=9.0**: ISS × 訓練未経験の一般市民 10 名という設定の独創性と、災害避難所・病棟・介護施設・寮・船舶への転用射程を README が明示している点。
- **C=9.0（本作の最高点）**: 4 層分離、`sim_core/hooks.py` の **9 ステージ hook 規格**、`validate_domain_pack` によるスキーマ/必須ファイル/カラム別名/集団重みのバリデーション、**12 ランタイムプロファイル**（claude × codex × cursor × smoke/full × run_a/run_b）、複数 LLM バックエンド、TSV/YAML 完全外部化。README が「差し替えられるもの」「新しいドメインへの差し替え」「終盤イベントだけを差し替える」を**独立した章**として持ち、避難所への TSV 列単位の差替手順まで例示している。
- **D=8.0**: 2 段階プロンプト（Phase1 位置情報なしでメッセージ決定 → Phase2 位置情報あり + 自分の発話込みで行動決定）で発話と移動の因果順序を分離。`_extract_json_from_text` は文字列リテラル・エスケープを考慮した brace-matching。`CommandLLMClient` に max_retries / retry_backoff_seconds / timeout_seconds / ANSI エスケープ除去 / stdout 正規表現フィルタ。`ThreadPoolExecutor` の順序保存並列。

### 弱み

- `examples/spatial_demo/simulation.py` が 920 行で、空間・火災・**経済層（雇用・通貨）**が同一クラスに混在（ISS と無関係な機能が残っている）。
- **乱数シードの初期化が無い**。A/B 比較を売りにする作品としては講評が「クリティカル」と指摘。
- メモリがフラットなリスト止まり（人物別・オブジェクト別の構造化なし）。
- place description の `welcomes conversation` / `encourages moving` / `reduce isolation` がやや誘導的で、完全な raw data ではない（A で満点に届かなかった理由）。
- **README に 50 ステップ・no_accident シナリオの定量結果（A/B 差）が示されていない**。分析パイプライン `analyze_iss_pair.py` と UI `iss_habitat_demo.html` はあるのに数値がない。

### `_eval_review` 所見

「元評価のスコア 34.0/40 は、引用された全ソース根拠と完全に整合する。誇張または事実誤認は見出されず、減点要因（モノリス構造・乱数シード未確認・メモリのフラット構造）もすべて実態と一致する。**スコア改変は不要**」。引用行番号に数行のずれがあるのみ。特に「乱数シードの欠落は A/B 比較を売り物とする本プロジェクトにとってクリティカルな指摘」と追認。

---

## コード実査で面白かった点

### 1. `sim_core/hooks.py` の 9 ステージ hook 規格

```python
HOOK_STAGES = ("pre_run", "pre_step", "pre_observation", "post_observation",
               "aggregate", "feedback", "post_step", "export_viewer", "audit")
```

`@dataclass(slots=True) class HookSpec(stage, hook_id, enabled, module, function, config)` と `normalize_hooks(config)` で、YAML から `hooks: {pre_observation: [{id, module, function}], export_viewer: [domain_viewer_export]}` の形で外部モジュールを差し込める。**`audit` ステージが最後にあるのが特徴**——検証を拡張点として最初から規格に入れている。

### 2. domain.yaml が「実験仕様書」そのものになっている

340 行超の domain.yaml に、以下が**全部宣言的に書かれている**。

- `purpose.hypothesis`（仮説文）と `purpose.comparison`（Run A vs Run B）と `purpose.primary_kpis`（7 個）
- `pipeline.state.fields`: 社会状態 7 変数を `polarity: pressure / buffer` 付きで定義（confinement_stress / resource_pressure / communication_delay / privacy_pressure / interpersonal_tension / routine_fatigue / benevolence_affordance）
- `pipeline.feedback.signal_rules`: エージェントの行動カテゴリ・感情・**発話テキストのキーワード**から 7 種の圧力シグナルを重み付き合成する規則（例: `mutual_aid_pressure` は カテゴリ「手伝い」0.90 + 感情「連帯感」0.26 + テキスト「一緒」0.12 …）
- `pipeline.feedback.delta_coefficients`: シグナル → 社会状態変数の係数行列（例: `interpersonal_tension` は conflict_pressure +0.045 / mutual_aid_pressure −0.035）
- `pipeline.feedback.event_rules`: 社会状態が閾値を超えたら新しいイベントを生成して次ステップのエージェントに戻す

**つまりミクロ（LLM の行動/発話）→ マクロ（社会状態変数）→ ミクロ（イベントとして再注入）の双方向ループが、コードでなく YAML の係数表として書かれている**。監査可能性が極めて高い。当方の観測分離原則と相性が良い。

### 3. `realism_contract`（＝ビューアが嘘をつかないための誓約）

domain.yaml の `pipeline.habitat_ui.realism_contract` に 5 条。

```yaml
- "UI表示は、agent state / place capacity / event / conversation / relationship_seed から導出する"
- "摩擦や修復は event_id と conversation_id の両方に紐づける"
- "会話しない・沈黙する・相手を避ける状態も有効な観測として表示する"
- "位置と寝床割当はstepごとに連続性を持たせ、毎描画でランダムに変えない"
- "Run Bの改善は万能にせず、短い摩擦・遅れた修復・ナッジの押しつけ感も残す"
```

**「介入群を良く見せすぎない」を設計契約として明文化している**のが白眉。第 5 条は自作品の売り（ナッジ効果）を自ら抑制する規定で、当方の「正直な限界の明記」文化と完全に同型。第 3 条「沈黙・回避も有効な観測」は my-social-agents の FUTURE_WORK が課題として挙げた「沈黙の選択肢」を、こちらは最初から仕様に入れている。

### 4. ナッジ 30 種超のメニュー（`objects_menu.tsv`）

```
OBJ01 ハンドレール・メロディ    入口ハンドレールを握ると音が鳴る。モジュールごとに異なる音程。移動すること自体が演奏になる。
OBJ02 宇宙廃棄物サウンドボックス 正しく分別して投入すると宇宙の効果音が鳴る。重要作業がもう一度やりたい体験に変わる。
OBJ03 リソース・スコアボード    節約量がリアルタイム表示。個人競争ではなく全員のチームスコアとして見える。
OBJ06 話しかけてOKサイン       座席の一つに「ここにいる人は話しかけてOK」というサイン。声かけの心理的障壁を下げる。
OBJ07 持ち寄り棚              本・写真・レシピカード・家族の手紙を一つ置き、一つ取る棚。
```

**「移動そのものを演奏にする」「ゴミ分別を効果音にする」はゲーミフィケーションの範疇だが、`OBJ03` が「個人競争でなくチームスコア」と明示している**のは設計思想として意識的。当方の渋谷でも「サイネージ・掲示・置き看板」として同型の物を置ける。

### 5. 通信ルールがコードコメントで契約化されている

```python
# Agents can communicate if BOTH are outside places
# Agents can communicate if BOTH are in the SAME place
# Agents CANNOT communicate if one is inside a place and the other is outside
# Agents CANNOT communicate if they are in DIFFERENT places
same_area = ((not self.in_place and not agent.in_place) or
             (self.in_place and agent.in_place and self.current_place == agent.current_place))
if dist <= self.communication_radius and same_area: nearby.append(agent)
```

「屋内と屋外は通話不可」という**屋内/屋外の情報遮断**は、当方の屋内 SFM 人流と接続する設計。屋内にいると外の噂が届かない＝ラベル伝播の速度が場所構造に依存する、という効果を素直に作れる。

### 6. Run B のナッジ記述（誘導の度合いが実際に測れる）

```yaml
[Benevolence object: Talk-OK seat]  A seat has a sign saying the person sitting there welcomes conversation from strangers.
[Benevolence object: Memory Shelf]  People may leave a small personal item and take one, sharing stories across cultures.
[Benevolence object: Sanctuary mark] Others are expected not to interrupt when occupied.
[Benevolence object: challenge board] The board suggests pair workouts to reduce isolation.
[Benevolence object: move-vote panel] A daily two-choice panel encourages moving between modules.
```

**"welcomes" / "encourages" / "to reduce isolation" は効果を先取りして書いてしまっている**（＝fingerprint 寄り）。一方 Sanctuary mark の "Others are expected not to interrupt when occupied" は世界の規範事実の記述に留まっており、誘導度が低い。**同一リポの中で誘導度が揃っていない**ことが分かるので、当方の no-fingerprint レビュー基準の具体例集として使える。

### 7. 【本調査で発見・両講評とも未指摘】README が 100 ステップ・事故あり版のもので、50s 版のパックと食い違っている

50s リポと 100s リポの README を diff したところ、**最終行のリポ名 1 行を除いて完全に同一**だった。その README は「現行デモのサンプル出力は **10人/100ステップ**を基準にしています。**Day50 に宇宙デブリ衝突**による HAB 損傷、…Day65 以降の LAB 酸素低下による生命維持危機まで…」と書き、「終盤イベントだけを差し替える」章も `S50: DEBR01` 〜 `S65-S100: DEBR05` を列挙している。

しかし 50s リポの `domain_packs/iss_benevolence/domain.yaml` は `steps: 50`、`events_run_a.tsv` は 17 イベント（最後は `REPA06 49 50 帰還前の助言の修復`）で **DEBR 行は 1 つも無い**。

加えて README のクイックスタート冒頭は `python3 -m sim_core validate --pack ... --scenario run_b` だが、**50s リポの `sim_core/` には `__main__.py` が存在しない**（100s リポには 5 行の `__main__.py` がある）。つまり 50s リポでは README の手順 1 がそのままでは動かない。

→ **姉妹リポは「同じ本体の 2 スナップショット」で、README は 100s 版に合わせたまま**。条件違いの比較実験として読むなら、この非対称（50s の方が古い/簡素）を前提に置く必要がある。

---

## shibuya-simulation に活かせそうな点

1. **`realism_contract` の導入**（最重要）。当方のビューア/レポートに「介入条件を良く見せすぎない」「使われなかった・沈黙・回避も表示する」「毎描画でランダムに変えない」を**契約として docs に明文化**し、make_viewer / make_endo_report のレビュー観点にする。第64バッチの「正直な限界を明記」を、機械可読な契約に格上げできる。
2. **ミクロ→マクロ→ミクロのフィードバックを YAML 係数表で書く**。当方の関係性内生化は Python 側の関数として実装されているが、`signal_rules`（行動/感情/発話キーワード → シグナル）と `delta_coefficients`（シグナル → 社会状態）を conf に出せば、感度分析と較正が桁違いにやりやすい。
3. **KPI を domain.yaml に事前定義**（`purpose.primary_kpis`）。当方の KPI_COLS は Python 定数だが、「仮説・比較・主要 KPI」を実験仕様として 1 箇所に置く形式は endo_treatment 系の conf に持ち込める。
4. **`audit` を hook ステージに入れる**発想。当方は検収を人手＋テストでやっているが、run のパイプライン内に監査フックを持つと自動化しやすい。
5. **屋内/屋外の通信遮断ルール**。当方の屋内 SFM とラベル伝播を接続する具体策。
6. **ナッジ記述の誘導度レビュー**。"welcomes/encourages/to reduce X" のような効果先取り語を禁止語リスト化し、テストで検出する（後述 IDEA）。
7. **反面教師: README とパックの不一致**。当方も conf 6 セルと docs の記述がずれるリスクがある。`steps` などの主要パラメータを docs から自動生成するか、テストで突合する価値がある。

---

## web リサーチ（URL 必須）

- **Gibson (1979) のアフォーダンス理論** — 本作の「行動指示でなく環境に物を置く」設計の一般手法名。アフォーダンスは「行為者と環境の関係的property＝環境が特定の行為者に提供する行為可能性」であり、**環境を知覚することはそれが何を afford するかを知覚することである**。Norman は「real affordance（実際に可能なこと）」と「perceived affordance（可能だとユーザが信じること）」を区別した。本作の Run B は place description を通じて perceived affordance を操作している。
  - Gibson's Affordances（Chemero 解説 PDF）: https://www.researchgate.net/publication/15176211_Gibson's_Affordances
  - LLM におけるアフォーダンス駆動の環境認識フレームワーク: https://arxiv.org/pdf/2504.01644
  - マルチエージェント系のアフォーダンス設計（ASAF）: https://arxiv.org/pdf/2606.09832
  - アフォーダンス概念の拡張（Mind in action）: https://www.tandfonline.com/doi/full/10.1080/09515089.2024.2365554
- **ミクロ↔マクロ双方向因果（two-way micro–macro causation）** — 本作の `signal_rules` → `delta_coefficients` → `event_rules` のループは、この文献群でいう upward causation（エージェント行動の集計が state variable を作る）＋ downward causation（マクロ状態がエージェントに読み取り専用で供給される）の実装。EB-DEVS はこれを形式的枠組みとして規格化している。
  - Dynamical theory of complex systems with two-way micro–macro causation (PNAS): https://www.pnas.org/doi/10.1073/pnas.2408676121
  - EB-DEVS（創発挙動のモデリング形式）: https://arxiv.org/pdf/2010.05042
  - 人工社会における創発シミュレーションの実践的モデルベース手法: https://arxiv.org/pdf/2110.08170
  - 長期社会シミュレーションのためのマクロ動態とミクロ状態の結合: https://arxiv.org/html/2604.05516v2
- **ナッジ / 選択アーキテクチャ** — goodecho_r の項に記載（Thaler, Sunstein & Balz, SSRN）: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1583509
- **good echo チームの結び文書（レビューリポ内スライド）** — `slides/s26-2065_2095-good-echo-hackathon.pdf`（GitHub 上のレビューリポ内、直リンクは非公開扱いのため記載しない）。「善性 ＝ ego（自己効力感）× 共感（他者認知）× 協力（共同作業）」という**乗算モデル**を提示し、「劣悪な環境ではまず ego が破綻し、掛け算なので全体がゼロになる」「環境設計の役割は善性の量を増減させることでなく、種が発芽できるか否かを決定づける安全性の担保」と論じている。定量主張として「衝突の 60% 減少」「乖離値の 10% 短縮」「修復ラグ 1.17 ステップ」「物理的装置が消えた後も習慣として残る＝環境の内部化」を挙げる。**ただしこれらの数値の算出コード/ログは 50s・100s いずれのリポにも見当たらず、当方では追認できなかった**（正直に記録）。
