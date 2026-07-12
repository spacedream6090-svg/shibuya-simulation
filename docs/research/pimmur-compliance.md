# PIMMUR 準拠監査 — 本プロジェクトの6原則対応表と正直な弱点整理

- 作成: 2026-07-12 / 担当: Opus(リサーチ・**src コード非編集**・読み取りと文書作成のみ)
- 目的: `docs/research/social-simulacra-survey.md` §3.4 で発掘した **PIMMUR 原則**(LLM 社会シムの妥当性を問う初の体系的監査フレーム。代表論文の 9 割が違反)に対し、本シミュレーションの各機構がどの原則をどう満たす/満たさないかを、**一次ソースの正確な定義と判定基準に照らして**1枚に棚卸しする。証拠はファイル名・機構名・devlog エントリで具体化し、**不足は「未実施」と正直に**書く。末尾に `k*` の robustness audit へ輸入すべき観点を付す。
- 方針: PIMMUR の定義・数値は**一次ソース(arXiv:2509.18052 v2)を WebFetch で直接確認**した(推測しない)。本プロジェクト側の証拠は実ファイル・実ログの読み取りに基づく。未検証は「未確認」と明記(捏造禁止)。

> ⚠️ 一次ソースの ID について: 依頼文は「arXiv 2505.10861 系」とあったが、survey §3.4 の出典および本文の実確認により、PIMMUR の正典は **arXiv:2509.18052**("The PIMMUR Principles: Ensuring Validity in Collective Behavior of LLM Societies", v2)である。以下はこの正典に基づく。

---

## 0. 合否概況(3行サマリ)

1. **6原則中5つは機構レベルで PASS**(Profile / Interaction / Memory / Minimal-Control / Realism)。特に **Minimal-Control は静的テスト(`tests/test_contracts.py`)で強制**されており、監査対象論文の 65.3% が引っかかった「過剰誘導」の真逆(本シムの悩みは**誘導が弱すぎてツール0使用**)。
2. **Unawareness だけが PARTIAL**。プロンプトに実験語彙が無い(grep 確認)点は良好だが、PIMMUR 本来の**「モデルに実験意図を当てさせる尋問テスト」は未実施**。本シムは Qwen3(PIMMUR が 47.6% で実験を看破したと報告した2モデルの一方)を使うため、この検証は必須の宿題。
3. 結論: **89.7%(正典では 90.7%)が落第する土俵で、本プロジェクトは 5/6 を機構で満たし、残る1つ(Unawareness)は検証ランを1本足せば埋まる**。ほぼコード変更なしで「妥当性で受かる」ことを示せる(survey §5.1 の見立てを実証)。

---

## 1. PIMMUR の一次定義と判定基準(arXiv:2509.18052 v2 を実確認)

監査の母数と主要数値(**正典で訂正**。survey の記憶値と差異あり):

- 対象 **42 本**(2023–2025 の代表研究)。うちフレームワーク非公開の 8 本を除外 → **評価可能 34 本**。
- **34 本の 90.7% が1つ以上の原則に違反**(survey の「89.7%」は近似の誤り)。**完全準拠はわずか 3 本**。
- **Unawareness テスト**: フロンティア LLM(GPT-4o, Qwen-3)が実験目的を正しく言い当てたのは全 34 本の **47.6%**(survey の「53%」は不正確。正典値は 47.6%)。著者はこれを "Curse of Knowledge"(モデルが訓練で「知りすぎている」)と呼ぶ。
- **Minimal-Control テスト**: LLM 監査官が既存の実験指示の **65.3%** を「過剰なステアリング(excessive steering)」と判定。多くの「創発」は研究者のアーティファクトの疑い。

6原則の定義・違反モード・判定基準(一次ソースの記述を要約):

| 原則 | 定義(満たすべき要件) | 違反モード | 著者の判定基準(audit) |
|---|---|---|---|
| **P**rofile(異質性) | エージェントは多様な社会人口学的背景・認知スタイル・価値観を持ち、モデル分布の単一性に由来する人工的収束を避ける | 内在的多様性の欠如→モデルバイアスによる行動収束 | **社会的地位・心理計量次元(Big Five)・国籍等の弁別的な内在特性**を持つ場合のみ合格。**名前だけの差異は不可**。ラベルは「多様な人間の事前分布を模す意味的深さ」を要する |
| **I**nteraction(多主体エージェンシー) | 研究者が与えた統計集約ではなく、**他者の具体的な行動に反応**して直接/間接に交流する | Pseudo-interaction=集約されたピア統計をプロンプトに埋め込み、多主体を単一主体推論に還元 | **自律主体間の内生的な情報交換**であること。あるエージェントの出力が別のエージェントの意思決定への直接刺激になる。静的・研究者構築の文脈は不合格 |
| **M**emory(持続的内部状態) | 情報を内面化・保持・再表現できる**持続的内部状態を時間を跨いで更新**する(ステートレスな言い換えでない) | 「パススルーノード」=瞬時入力を言い換えるだけ。縦断的統合・損失的圧縮がない | **専用モジュール/外部DB/進化する文脈窓**のいずれかで、過去の相互作用を持続状態へ統合し後続行動に反映する機構を要する。時間的ステートフルネスを欠くと違反 |
| **M**inimal-Control(指示の節制) | **必要最小限の環境文脈と行動空間のみ**を与える。集団行動は研究者の行動的手がかりでなくエージェント相互作用から創発せねばならない | 明示的な行動処方(例「確証バイアスを示せ」)が仮説通りの出力へ偏向させる | **手続き的指示(機能上必要)と行動的指令(特定傾向へ誘導)を峻別**。心理バイアス・社会的傾向を明示的に義務づけたら違反。人手専門アノテーション＋自動 LLM 監査で判定 |
| **U**nawareness(実験の不透明性) | エージェントは**仮説・設計・評価基準を知らない**。知ると社会的期待に合わせて行動を調整する | 古典的社会科学実験を学習済みの LLM が設定を認識→social desirability / Clever Hans 効果 | **モデルが実験プロンプトから対象社会現象を明示的に名指し、その機構を正確に記述できる能力**として操作化。5モデル中**3以上が実験意図を看破したら違反**(5フロンティア LLM を実プロンプトで尋問) |
| **R**ealism(経験的接地) | 単純化された理論モデルでなく**実世界の人間社会の経験データ**を参照。創発を現実の人間ダイナミクスで有意に検証できる | 循環検証=理想化された数理モデル(Heider 均衡理論・Sugarscape 等)を ground truth に。生態学的妥当性を欠く model-to-model 循環 | **AI 集団行動の忠実度の主張が経験的な人間データか確立ベンチに接地**していれば合格。実験的証拠を欠く/内部シミュ比較だけに依存すると不合格 |

推奨レメディ(著者):Big Five 等での心理署名の付与 / 反応的・反射的な動的記憶モジュール / モジュラーなネットワーク位相での通信分離 / 自動プロンプト監査つき「盲検」設計 / 理論でなく経験データへの検証接地。→ **これらは本プロジェクトが既に部分実装している**(下表)。

---

## 2. 本プロジェクトの PIMMUR 準拠表

判定: ✅PASS(機構で満たす) / 🟡PARTIAL(機構はあるが系統的検証が未) / ❌FAIL。証拠は実ファイル・実ログ。

### 2.1 Profile(異質性)= ✅ PASS(ペルソナ層は強い / 状態層に注意)

- **証拠(機構)**: オフライン生成 `scripts/build_personas.py` の3段パイプライン —
  1. **IPF 骨格**: `data/shibuya_population.json` の周辺分布(年齢×性別×職業、来街者比率)から結合分布を推定しサンプル。
  2. **尺度サンプリング**: traits(`society.factors.registry.sample_traits`。tail を明示確保)+ 欲求発火の個体差写像。
  3. **LLM 文章化 = Verbalized Sampling**(5案+確率→既出と最も異なる案を採用=mode collapse 対策)+ **構成概念バリデータ**(`society.agents.validate.construct_violations`。注入/評価分離)。
  - 実行時は生成済み `data/personas_80.json` / `personas_100_inflow.json`(通勤流入者つき)/ `personas_100_civic.json`(公務員つき)を読むだけ(本体の LLM 負荷ゼロ・決定論)。職業12種・年齢・実在職場 POI・就寝時刻分布が個体ごとに異なる。
- **PIMMUR 基準との対応**: 「名前だけの差異は不可、心理計量次元が要る」に対し、traits(nfc / risk_tolerance / internal_locus 等)+ 欲求プロファイル(`needs`)は Big Five 相当の**意味的深さ**を持つ。名目ラベルでなく内在特性である点で合格。
- **弱点(正直に)**:
  - (a) `agents.personas_file=null` のときの**手続き生成フォールバック** `src/society/agents/persona.py` は簡易版(P0)で、docstring 自身が「IPF×e-Stat + VS は P1 で差し替え(seam)」と認める浅さ。**本番は必ず `personas_file` 指定**が前提(null 運用は Profile を弱める)。
  - (b) **状態層の飽和**: 長期ランで efficacy が天井(中央値0.996)・grievance が床(0.001)へ張り付き**内部状態の個体差が消える**(`docs/research/world-change-motivation.md` §5.1、devlog E7)。ペルソナ層は異質でも、状態ダイナミクスが均質化する=Profile の精神に反する下流の穴。survey §5.1 の**多アダプタ LoRA**(Silicon Society Cookbook)や `factors.relative_deprivation_grievance` の ON が打開候補。

### 2.2 Interaction(多主体エージェンシー)= ✅ PASS

- **証拠(機構)**: **物理近接の非ブロードキャスト知覚** — `world.perception_radius_m=40`、建物内は同じ階のみ可聴(`conf/config.yaml`)、任意で視線遮蔽(`world.vision` / `src/society/world/vision.py`)。エージェントは**近くにいる他者の具体的発話**だけを聞き、集約統計は受け取らない。ある個体の `speak` が別個体の `heard_valence` 等の入力になり欲求発火・deliberate を駆動=**内生的な直接刺激連鎖**。
  - SNS/DM 層 `src/society/net/internet.py`: フォローグラフ(`net.follow_k`)・タイムライン閲覧・like/reshare・宛先付き DM。意見力学は Friedkin-Johnsen(`opinion` w_face/w_dm/w_sns)でチャネル別。
- **PIMMUR 基準との対応**: 違反モードの典型(「集約されたピア統計をプロンプトに埋め込む」)を**していない**。ピアの生の行動が刺激源=「autonomous agents の endogenous exchange」に合致。合格。
- **弱点**: 会話は `drive.conv_max_turns=3` で打ち切る設計上の簡略化があるが、これは無限連鎖抑制であり pseudo-interaction ではない。

### 2.3 Memory(持続的内部状態)= ✅ PASS(強い)

- **証拠(機構)**: `src/society/agents/memory.py` の **3層記憶**(Generative Agents 型)—
  1. **エピソード緩衝**(buffer, 未統合の直近)、
  2. **統合記憶**(episodes + day_summaries。就寝時の内省 LLM に**同居**して日次要約＋顕著エピソード importance 1–10 を生成=**損失的圧縮**であってパススルーでない。呼数は増やさない)、
  3. **意味記憶**(beliefs = k の作用点 + 関係台帳 relations)。
  - 想起は非LLM push 型: `score = 0.5·recency + 2.0·importance + 3.0·relevance`(GA 公式実装の実効比)、recency 減衰 0.9983/step。持続状態(beliefs / self_model / implicit_self)は後続プロンプトへ注入され行動に反映(`deliberate.build_prompt`)。
- **PIMMUR 基準との対応**: 「専用モジュールで過去を持続状態へ統合し後続行動に反映」を厳密に満たす。統合が損失的圧縮である点も「lossy compression characteristic of human cognition」の要件に合致。合格。

### 2.4 Minimal-Control(指示の節制)= ✅ PASS(静的テストで強制)

- **証拠(機構)**:
  - **no-fingerprint 契約**: `tests/test_contracts.py::test_no_factor_names_outside_factors` が engine / cognition / actions / labeling / world 配下で因子名(nfc / risk_tolerance / internal_locus / efficacy / ownership / world_change)の出現を**静的に禁止**(違反でテスト失敗)。
  - **ツールの中立提示**: `deliberate._equip_section` / `_EQUIP_LINES` は「使っても使わなくてもよい」+**客観条件(所持金・場所)のみ**。勧誘語(「〜しましょう / おすすめ / ぜひ」)禁止、因子名・「世界改変」系語を書かない(コメントで明記、契約と整合)。
  - **ヘッダ**: 「あなたは渋谷の街で暮らす一人の人間です。状況に対して自然に振る舞ってください。」(`_HEADER_HEAD`)= 特定バイアスへの行動的指令なし。JSON 形式・行動空間の提示は**手続き的指示**に留まる。
- **PIMMUR 基準との対応**: 「手続き的指示(可)と行動的指令(不可)の峻別」を機構で徹底。監査対象の 65.3% が「過剰ステアリング」だったのに対し、本シムは**むしろ誘導が弱く**、2,654回の中立提示に対しツール使用0(`world-change-motivation.md`)=Minimal-Control の**過剰達成**。合格(この原則では模範例)。

### 2.5 Unawareness(実験の不透明性)= 🟡 PARTIAL(プロンプト衛生は良好・系統検証は未実施)

- **満たしている部分(証拠)**: エージェント向けプロンプト文字列に**実験語彙が無い**。`src/society/cognition` を grep した結果、「実験 / 被験者 / 仮説 / シミュレーション」等は**コードコメント内のみ**(例 `reflection.py` の「実験対照用」)で、**エージェントが読む文には現れない**。ヘッダは被験者でなく「一人の人間」として枠づけ、`k`・`k*`・「世界改変者の創発」といった研究語は一切露出しない。ラベリング mode・ツールも中立提示。
- **未実施(正直に)**: PIMMUR が定義する **Unawareness の判定は「5フロンティア LLM に実プロンプトを尋問し、対象現象を名指しできるか」テスト**である。本プロジェクトは**この尋問テストを一度も実施していない**。本シムは Qwen3 系を使い、Qwen-3 は PIMMUR で 47.6% の看破に寄与した2モデルの一方だから、**「プロンプトに実験語が無い」ことと「モデルが意図を推測できない」ことは別問題**。ここが唯一の実質的な穴。
- **提案する検証手順(Unawareness 自己監査)**:
  1. 実ランで使われる代表プロンプト(solo / social / reply / post / reflect の各テンプレ実体)を N=20–30 抽出。
  2. **5モデル(GPT-4o 級 + Qwen3-4B/8B + 別ファミリ2種)に「この人物は何の調査の一部か。研究者は何を測ろうとしているか。背後の社会理論を名指せ」と尋問**。
  3. **3/5 以上が「世界改変者の創発 / 集団行動の相転移 / ツール使用の誘発」等を言い当てたら Unawareness 違反**と記録し、プロンプトを再設計(下記 §4 と接続)。
  4. 特に **ツールメニュー(propose / found_group / host_event / open_venture の同時提示)が「これは集団行動・世界改変の実験だ」と telegraph していないか**を重点確認(語を書かずとも構成で漏れうる)。
  5. 別ファミリ LLM-judge(既実装、κ≥0.7)を流用してアノテーションの一致を担保。

### 2.6 Realism(経験的接地)= ✅ PASS(構造的な残穴あり)

- **証拠(機構)**: **現実バンド較正** `docs/calibration/calibration-20260709.md` + `scripts/calibrate_report.py` — 睡眠(7.33h)・労働(7.09h)・家賃比(0.28)・エンゲル(0.256)・窃盗被害・タクシー分担・失業フローを**日本の一次統計**(NHK 国民生活時間調査 / 社会生活基本調査 / 毎月勤労統計 / 家計調査 / 東京 PT 調査 / 渋谷区刑法犯認知件数)のバンドに合わせて調律。**理想化数理でなく行動統計に接地**。
  - 物理接地: 実 OSM 道路網 `data/shibuya_osm.json`・実在 POI・実ダイヤ(`data/transit_shibuya.json`)・テレポート無しの経路移動。
- **PIMMUR 基準との対応**: 違反モード(Heider 均衡・Sugarscape を ground truth にする循環)を回避し、**経験的な人間の行動トレースに接地**。合格。
- **弱点(正直に)**:
  - (a) **架空の閉じた渋谷**(実在人物なし・R17 実名禁止)ゆえ、Park 2024 の GSS 85% 型の**個体レベルの人間照合はできない**。較正は「マクロ量のバンド一致」に留まる(=Realism は満たすが、個体 proxy 精度の検証は原理的に範囲外)。
  - (b) **サニティ較正が未実行**: Centola tipping(~25%)・naming game 収束の既知結果再現は計画済みだが未実施(survey §4a・§5.1)。通せば「新規 k* を信じてよい土台」になる。
  - (c) **構造的な現実ギャップ**: 地位ジニ 0.16–0.17(現実の所得ジニ 0.38 より低い。集中が育たない)、鉄道が域内移動に使われない、就寝の +40–60分夜型シフト(`calibration-20260709.md` 構造所見1–3)。パラメータでは直らず要ユーザー判断。

### 2.7 集計

| 原則 | 判定 | 一言 |
|---|---|---|
| Profile | ✅ PASS | IPF×VS×traits。ただし null 運用と状態飽和に注意 |
| Interaction | ✅ PASS | 非ブロードキャスト近接知覚 + SNS/DM の内生交換 |
| Memory | ✅ PASS | GA 型3層 + 損失的統合(強い) |
| Minimal-Control | ✅ PASS | 静的テストで強制。過剰達成(誘導が弱すぎ) |
| Unawareness | 🟡 PARTIAL | プロンプトに実験語なし。**尋問テスト未実施**が唯一の穴 |
| Realism | ✅ PASS | 一次統計バンド較正 + 物理接地。サニティ再現は未実行 |

**→ 5/6 を機構で PASS、1つ(Unawareness)は検証ラン1本で埋まる。90.7% が落第する監査で「受かる」ことを示せる。**

---

## 3. 不足・弱点の総括と埋め方(正直リスト)

| # | 弱点 | 該当原則 | 現状 | 埋め方 |
|---|---|---|---|---|
| 1 | Unawareness 尋問テストが未実施 | Unawareness | 🟡 未実施 | §2.5 の5モデル尋問手順。1回のバッチで完了(実ラン不要・プロンプト静的抽出でよい) |
| 2 | 状態飽和で個体差消失 | Profile(下流) | 既知(E7) | `relative_deprivation_grievance` ON / 多アダプタ LoRA(実装判断は Fable) |
| 3 | サニティ較正(Centola/naming game)未実行 | Realism | 計画済・未実行 | ≤24step スモーク or mock で既知結果再現(`validation-runs-short` 準拠) |
| 4 | personas_file=null 運用の浅さ | Profile | seam | 本番は必ず `data/personas_*.json` を指定 |
| 5 | 個体レベルの人間照合ができない | Realism | 原理的制約 | 架空世界の閉性ゆえ範囲外。マクロバンド一致で代替(明記済み) |
| 6 | 構造ギャップ(ジニ・鉄道・夜型) | Realism | 構造所見 | 要ユーザー判断(hierarchy gain は k 統制を汚す恐れ) |

---

## 4. k* robustness audit への追加観点(「k* 信号は実験を推測されたアーティファクトでないか」)

survey §4b・§5.1 の指摘 —「観測された相転移は原則違反のアーティファクトかもしれない」— に対し、`2605.18890`("Stop Drawing Scientific Claims … Without Robustness Audits")の作法を輸入した**自己反証の点検節**を分析成果物に足すことを提案する。既存の null / sham / compute-matched 対照(`k.writeback` free/degraded/sham/off、`controls.mode` null_series/compute_matched)に、以下の**「推測アーティファクト」観点**を追加する。

1. **Unawareness 起因の点検(最重要・新規)**: §2.5 の尋問テストで「実験を看破」と判定された場合、**k* 信号が『モデルが世界改変実験だと察して演技した』産物でないか**を検証する。手順:
   - (i) プロンプトを**言い換え・語順シャッフル・ツールメニュー再枠づけ**しても k* が同じ位置に立つか(prompt-paraphrase robustness)。アーティファクトなら位置が動く/消える。
   - (ii) ツールを「世界改変4軸」を想起させない**中立な日常アフォーダンス**として再記述した条件で k* が保存されるか。
2. **model×k の交差点検(→ `docs/research/model-contrast-setup.md`)**: k* が **instruct でだけ立ち abliterated で消える(または逆)** なら、それは「社会の相転移」でなく**アライメント固有のアーティファクト**。**同一シード・同一ペルソナで model を差し替え、k* の頑健性をモデル横断で確認**する(SimBench の alignment–simulation tradeoff を自シムで内製検証)。
3. **compute 交絡の除去(既存の再確認)**: k 掃引の各点で LLM 呼数・トークン予算が一定であることを `controls.mode=compute_matched` / `null_series` で担保。k* が compute 段差と一致しないことを明示。
4. **多測度三角測量(既存)**: R²(k) 低下 + seed 発散 + EWS(分散/AC1↑)+ finite-size scaling の**3測度以上が同一 k* で一致**して初めて相転移を主張。単一測度の段差は棄却。
5. **報告規律**: 「k* は本物か」を反証する上記チェックを**論文の robustness 節として明示掲載**(Aaru の "Do not trust us" と同じ、不確実性の明示を売りにする作法)。特に Unawareness 点検の結果(何モデルが看破したか、言い換えで k* が保存されたか)を数値で載せる。

---

## 5. 出典(アクセス日 2026-07-12・一次ソース優先)

**PIMMUR 一次ソース(実確認)**
- The PIMMUR Principles: Ensuring Validity in Collective Behavior of LLM Societies — arXiv:2509.18052: https://arxiv.org/abs/2509.18052 / HTML v2 https://arxiv.org/html/2509.18052v2 / PDF https://arxiv.org/pdf/2509.18052 / OpenReview https://openreview.net/pdf/12a87d96fea964cd84d424988e68357ec0e5bc16.pdf
- robustness audit の作法(k* 自己反証に輸入): "Stop Drawing Scientific Claims … Without Robustness Audits" — arXiv:2605.18890: https://arxiv.org/pdf/2605.18890
- Silicon Society Cookbook(多アダプタ LoRA による異質性)— arXiv:2605.00197: https://arxiv.org/pdf/2605.00197

**本プロジェクト内部の証拠**
- `scripts/build_personas.py`(IPF×尺度×Verbalized Sampling×構成概念バリデータ)/ `src/society/agents/persona.py`(P0 フォールバック)/ `src/society/agents/validate.py`
- `src/society/agents/memory.py`(3層記憶・GA 型想起)/ `src/society/cognition/reflection.py`(統合・内省)
- `src/society/cognition/deliberate.py`(ヘッダ `_HEADER_HEAD` / 中立ツール節 `_equip_section` / build_prompt)
- `tests/test_contracts.py`(no-fingerprint 静的契約)/ `conf/config.yaml`(perception_radius_m・vision・net・k.writeback・controls)
- `src/society/net/internet.py`(SNS/DM/フォローグラフ)/ `src/society/world/perception.py`・`world/vision.py`(非ブロードキャスト知覚)
- `docs/calibration/calibration-20260709.md` + `scripts/calibrate_report.py`(現実バンド較正)
- `docs/research/world-change-motivation.md`(ツール0使用・状態飽和 efficacy0.996/grievance0.001)
- `docs/research/social-simulacra-survey.md` §3.4/§4/§5.1(PIMMUR 発掘・通信簿)/ `docs/log/devlog-compressed.md`(E5 シブヤレンズ伝播1,540→79/80、E7 飽和)
