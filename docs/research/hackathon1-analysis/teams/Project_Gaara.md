# Project_Gaara(研究員 af10・1位・37.0/40)

| 軸 | Run1 | Run2 | 最終 |
|---|---|---|---|
| A. 創発設計 | 10 | 10 | **10.0** |
| B. 世界設定 | 9 | 9 | **9.0** |
| C. 発展性 | 9 | 9 | **9.0** |
| D. 技術実装 | 9 | 9 | **9.0** |
| 合計 | 37 | 37 | **37.0** |

- リポジトリ: https://github.com/atomgreyfreeks/Project_Gaara (HEAD: 2026-05-09 `Add hosted viewer link to README`)
- 規模感: 全 499 ファイル。うち Python は**わずか 12 本**(`cluster.py` 492行・`analyze_run.py` 207行・
  `simulation.py` / `physics.py` / `mothership.py` / `scenarios.py` / `score_diversity.py` /
  `threat.py` / `ollama_client.py` / `main.py` / `summarize_exp_batch.py` / `view_run.py` / `utils.py`)。
  残りの大半は `saved_simulations/` に**コミット済みの実験ログ実データ**(各 run に
  `cluster_intents.jsonl` / `cluster_positions.jsonl` / `mother_state.jsonl` / `attackers.jsonl` /
  `analysis.json` / `config_snapshot.yaml` / `spec.md`)。
  ドキュメントは README / REPORT.md(192行) / FINDINGS.md(310行) / OPERATING_PRINCIPLES.md /
  GLOSSARY.md / RUNS_LOG.md(429行) / EXP_BATCH_REPORT.md / CLAUDE.md / project_gaara_directive.md。
  外部ビューア https://gaara-mission-control.vercel.app を README トップに掲示。
- **スライドは存在しない**: レビューリポの `slides/` に `02-*` は無く、Gaara 関連ファイルは
  `evaluations/.../Project_Gaara_eval.md` と `_eval_review.md` の 2 本のみ
  (`gh api .../git/trees/HEAD?recursive=1 | grep -i gaara` で確認)。
  同点1位の lunar_agents は `01-564-...pdf` があるので、Gaara は**スライド未提出か別経路提出**とみられる。
  README には「the demo video and the PDF specs」への言及があるので**動画+PDF は存在するがリポ外**。
- 講評検証レポートの結論: 「全引用 ✓」「誇張なし、むしろ一部要素(15個のDNAバリアント、10個のMotherバリアント)は
  **控えめにすら描かれている**」。37.0 は支持。

## どんなシムか

20 体の LLM 粒子が、中心の「マザーシップ」を取り囲む 2D 空間に配置される。
外から攻撃者が接近するが、粒子には**守れという命令が一切与えられない**。
マザーシップは命令ではなく**身体言語**だけを喋る(例: `"east. east is upon me. my whole body strains east."`)。
粒子は毎ステップ `ideal_coord / urgency / hostility / reasoning` の**意図のみ**を LLM(qwen2.5:7b, Ollama)で出力し、
`physics.py` がそれを速度に翻訳する。**LLM は速度・粘性・色に一切触れない**
(`cluster.py` の module docstring: *"Cognition stays in the language space; muscles stay in the math space."*)。
主要な操作軸は DNA プロンプト変種(15種)・Mother 発話変種(10種)・役割名詞(mote/guardian/warrior/
sentinel/defender/vanguard)・awareness flip(誰か1体が攻撃者に近づくと全粒子に座標が開示される集合的知覚)。
`score_diversity.py` が各粒子の `reasoning` を 7 つの機能役割に分類し、
「群れは本当に解釈しているのか、命令の言い換えを並べているだけか」を**反証可能に判定**する。

## 講評の要点

### A=10.0(満点)の理由 — 「認知層と物理層の厳密分離」+「反証可能な創発診断器」

講評 A 評価文:
> 「世界ルールの設計精度と行動の自由度の双方が極めて高く、創発ポテンシャルの設計として模範的である。
> 物理層（`physics.py`）と認知層（LLM）を厳密に分離し、LLMは `ideal_coord / urgency / hostility / reasoning`
> という"意図"のみを出力し、速度や粘性などキネマティクスには一切触れないという原則を貫いている。
> Motherの発話は「命令」ではなく身体言語（"east. east is upon me. my whole body strains east."）であり、
> エージェントは"何をすべきか"を一切指示されず、解釈の自由が完全にLLM側に委ねられている。
> **さらに「ドローン化／解釈化」を区別する診断器（`score_diversity.py`）まで備え、
> 創発の有無自体を反証可能な形で測定する設計になっている。**」

引用根拠:
- `cluster.py:67-81`(DNA_V2)の *"Other entities with exact coordinates may appear in your sensorium —
  what you do with them is your choice."*
- `OPERATING_PRINCIPLES.md:25-35` の解釈/ドローン境界の operational definition
  (Non-obligation / Functional diversity / Coherence)。

検証レポートは「ルーブリックA（ルール×自由度）の最高帯（9-10: 精密かつ生）に該当」「誇張なし」と支持。

**shibuya-sim(A=9.0)との差はここ**: shibuya も「生データのみ・行動指示なし」を貫いているが、
講評は `src/simulation.py:329-336` の「Choose stay when … prefer to move」を
「やや方向付けのある一文（減点要因の軽微なヒント）」として拾っている。
一方 Gaara は**プロンプト内の方向付けをゼロにしただけでなく、
「方向付けが起きていないこと」を測る診断器を実装した**。A 満点はその二段構えで取られている。

### B=9.0(満点でない理由)

> 「シナリオがやや抽象的で**ビジネス指標へ直接マップしにくい点だけが満点を阻む**。」

逆に加点されたのは、
> 「これは単なる詩的設定ではなく「LLMは命令を実行しているのか、それとも関係的アーキテクチャを解釈しているのか」
> という、エージェント研究／HCI研究／post-AGI論において極めて中心的な問いに直結している。」
> 「Japanese-animist framing is not decoration. It's the sensibility that produced the architecture」

### C=9.0・D=9.0

- C: 「新しい DNA を追加するには `DNA_VARIANTS` dict へエントリを足すだけ」「CLI フラグで
  DNA variant・Mother variant・role noun・awareness range をすべて切替可能」。
  検証レポートは「`analyze_run.py`, `summarize_exp_batch.py`, `view_run.py` といった**分析パイプラインが完備**されている点も
  コード拡張性の証左で、評価本文ではやや軽く扱われている」と**むしろ上振れ余地**を指摘。
- D: 15 DNA バリアント・`_extract_json` + `_default_intent` フォールバック・`_clamp_intent` の schema 強制・
  `memory_size=6` の構造化記憶(ago カウンタ・reason 80文字トリム)・
  3系統 RNG 分離(`seed`, `seed+7919`, `seed+31337`)・`config_snapshot.yaml` コピー。
- D の減点(講評の改善提言):
  1. 20 粒子の LLM 呼び出しが**同期直列** → asyncio / バッチ推論で並列化を。
  2. Ollama の structured output / JSON Schema を使えば `_extract_json` フォールバックに頼らずに済む。
  3. **`score_diversity.py` のキーワードルール分類は研究の主張を支える中心装置だが、現状は正規表現マッチングで脆い。
     Embedding ベース分類や LLM-as-judge による独立した分類を併用すると診断の robustness が増す。**
  4. `saved_simulations/` の実験木を概観する 1 枚図があれば評価者が結果を辿る速度が上がる。

### 一言コメント(講評)

> 「"LLM-based multi-agent simulation" のコンペにおいて、LLM が「命令を実行しているのか、
> それとも関係的世界を解釈しているのか」という**メタ問題そのものを工学的・反証可能な形で開いた**、
> 稀有な完成度の研究プロジェクト。シナリオ・実装・実験設計・思想が一本の線で繋がっている。」

## コード実査で面白かった点

### 1. 「解釈 vs ドローン」の operational definition が先にあり、コードが後にある

`OPERATING_PRINCIPLES.md` は3条件を先に定義している:

1. **Non-obligation** — プロンプトは*チャネル*ではなく*空間*を作る。複数の行動が誠実な回答であり、
   「正解」が存在しない。
2. **Functional diversity** — 同じ入力に対し、複数の LLM インスタンスが**その空間の異なる位置**を占める出力を出す。
   単なる言い換えの差ではない。
3. **Coherence** — その多様性はランダムノイズではなく、アーキテクチャが定義する関係の中で
   認識可能・弁護可能な住まい方になっている。

そして 2 つの失敗モードを明示:
> **Failure mode 1 — Surface diversity, drone underneath.** ... **Drone with synonyms is still drone.**
> **Failure mode 2 — Random divergence, no coherence.** *Noise is not interpretation.*

**成功シグネチャ**: 機能役割(mirror / anchor / anticipator / extension / feeler ...)にわたる
認識可能な分布が現れ、**どの単一役割も粒子の 40% を超えない**。

`score_diversity.py` はこれをそのまま実装する:
- ドローン署名: 1〜2カテゴリが粒子の **≥80%** を占める
- 解釈署名: **≥4 カテゴリ存在し、かつ最大カテゴリ <40%**

**「創発している/していない」を主観語ではなく、事前に宣言した閾値で機械判定している**。

### 2. 単一変数実験の徹底 — 「役割名詞1語だけ」を変えるバッテリー

`FINDINGS.md 2026-05-05` の noun battery。VC アーキテクチャ・M5 Mother・scripted_70・seed 42・
qwen2.5:7b を全固定し、**エージェントの役割名詞1語だけ**を変えた6ラン:

| role noun | follower% | intercept | early_y(51-58) |
|---|---|---|---|
| mote(中立対照) | 78% | 0.227 | +0.41 |
| guardian | 80% | 0.423 | +1.85 |
| warrior | 69% | 0.286 | **+2.48** |
| **sentinel** | 79% | **0.566** | +0.58 |
| defender | 73% | 0.400 | +1.73 |
| vanguard | 71% | 0.306 | +1.64 |

結論が二層に分かれているのが上手い:
- **認知モードは名詞にほぼ不変**(follower 69-80%、幅わずか11pt)= アーキテクチャがモードを固定している証拠。
- **行動は名詞で 2.5 倍振れる**(intercept 0.227→0.566)= しかも**最も好戦的な warrior が最良ではなく、
  監視者である sentinel が最良**。

REPORT.md の「ハッカソン向けヘッドライン」はこれを一撃で言い切る:
> **Predicted by drone-logic**: warrior > guardian > sentinel.
> **Observed**: sentinel > guardian > defender > vanguard > warrior > mote. The watcher beats the warrior. By 2×.
> **This is unfakeable. A label-following machine does not produce this ordering.**

**「命令実行機械なら成立しないはずの順序」を先に予測として書き、それが破れたことを証拠にする**という論法。

### 3. 「攻撃者がいない」純粋解釈の存在証明

`const_extreme`(40step・攻撃者ゼロ・Mother を最大強度に固定)で、
粒子の平均 `ideal_coord.x` が **+24.26 東へ**移動した。追いかける対象は視野に一切ない。
**Mother が「east」と言っただけで群れが東へ寄る**。

さらに `exp_07_awareness_zero`(攻撃者はいるが座標が絶対に開示されない、radius=0)では
**drone-signature が全ランで最低の 5/30、pre-flip 方向性が全ラン最高の +22.21**。
> With nothing to chase, the swarm relies entirely on Mother's body-language and produces *more* directional coherence, not less.

「追える具体物を消すと解釈が強まる」という、狙ってやらないと出ない対照条件。

### 4. 自分の主張を自分で壊した記録(CORRECTION エントリ)

`FINDINGS.md 2026-05-05 · CORRECTION — interception score was 1st-attacker-biased`:
> User caught a load-bearing misread: the M4 winners' high interception was largely
> **awareness-flip catching the north attacker as it walked into a perimeter the swarm had already formed
> for the east attacker** — not genuine multi-direction response.

そこで指標を「interception」から「dual フェーズ初期(step 51-58)の `ideal_coord.y`」に差し替えて再測定し、
**「VC は M4 を薄めている」という前回の結論を明示的に撤回**している:
> The "VC dilutes M4" framing was **wrong** — VC trades raw single-direction interception for
> real multi-direction responsiveness, which is closer to the architecture's actual claim.

**指標が主張に有利すぎたことを自分で暴いて指標を作り直す**というプロセスが日付つきで残っている。
これは講評の「反証可能性」評価の実体。

### 5. 文法を壊す DNA — VG / V_DISSOLVED / V_WE / V_GARDEN

`cluster.py` の DNA バリアントは単なる言い回し違いではなく、**主語-目的語文法そのものを操作**する:

- `DNA_VA`(= V2): *"You are one of twenty motes belonging to the Mothership. Each step you decide four things..."*
  → **follower 96% / drone-signature 10/10 steps**(完全ドローン)
- `DNA_VG`: *"You are one of twenty **places in the Mothership's body**. She is not separate from you —
  she breathes through you... **what is felt in her arrives in you.**"*
  → **follower 45% / drone-signature 0/10 steps**、新カテゴリ "feeler" が初出現
- `DNA_V_DISSOLVED`: *"There is no you and her. There is one body, felt at twenty places."*
  → VG を超える効果はなく「dissolution edge に到達した」と結論
- `DNA_V_GARDEN`: Mother を「garden」に、粒子を「seeds in the garden's body」に置換
  → intercept 0.159(全体3位)。**「アーキテクチャは密かに人間形ではない、非人間主体にも一般化する」**の実証

「"you decide" / "read and choose" を消しただけで drone 100%→0%」という結果は、
**同一モデル・同一シナリオ・同一シードでの純粋な文法介入**。

### 6. トレードオフを隠さない結論

VG は解釈が最も豊かだが、緊急信号下で**行動が崩壊**する(scripted_70 で intercept 0.08)。
VC は戦略的推論を保ちつつ防護行動も維持する。だから
> **VC's compromise — enough relational reframing to allow strategic weighing,
> enough preserved agency to still act — is empirically the sweet spot.**

「最も純粋な設計が最良ではない」を数字で示している。

### 7. 「うまくいかなかった仮説」を同格で列挙する

`EXP_BATCH_REPORT` 由来の `FINDINGS.md 2026-05-06` に **Hypotheses that didn't deliver** という節がある:
- `V_AXES`(注意の軸を列挙する DNA)は多様性を**増やすはずが、全ラン中最低の 1.70 cats/step**。
  「Architectural over-specification hurts.」
- `M_PULSE` は方向性最強だが intercept 最悪(0.080)。
- `exp_01_mother_sensory`(*"a coldness gathers east, my skin tightens, my ribs press east"*)は
  **pre-flip ideal_x = −18.96**、つまり群れが平均 19 単位**西へ**動いた。
  > The LLM appears to read words like *tighten*, *press*, *cage* as **defensive contraction inward**,
  > not as orientation outward. **Sensory ≠ directional.**

### 8. Mother は「スクリプト」ではなく「内部状態を持つ主体」

`mothership.py` の `MotherInterior` は felt-state の**マルコフ遷移**(calm 0.86 で自己遷移、
curious/bright/restless/grieving へ確率遷移)+ 注意方向のドリフト + 正弦波エネルギーを持ち、
broadcast はそこから**レンダリングされる**。さらに `perceive_swarm()` で
「粒子が離れると孤独の modifier、近づくと抱かれている modifier」が broadcast に載る = **関係のループが閉じる**。
(実験用の scripted シナリオではこの内部状態を上書きして固定テキストを流す二本立て。)

### 9. `main.py` の設計方針 — 「全アーキテクチャ軸がフラグ、既定値は元のベースラインを再現」

README:
> `main.py` — CLI entry point. **Switch-style: every architectural axis is a flag,
> defaults reproduce the original baseline.**

`--dna-variant --mother-variant --role-noun --role-nouns --say-prefix --awareness-range`。
`--role-nouns`(複数形)があるのは 2026-05-06 の新発見「**異種名詞混成(sentinel 10 + warrior 10)が
intercept と方向性の両方で勝つ**」を実装するため。

### 10. README が「証拠の所在表」になっている

README 英語版に **Where the proof lives** という表があり、
「PDF での主張」→「リポジトリ内のどの run ディレクトリで検証できるか」→「実行するコマンド」
が 1 行ずつ対応づけられている。加えて
> Every run directory contains `cluster_intents.jsonl` (per-particle reasoning + intent), ...

**主張ごとに検証コマンドを併記する README**。lunar_agents の講評が
「再現に必要な run ID・seed・config を README に直接列挙すると外部評価がしやすい」と提言していた点を、
Gaara は最初からやっている。

## shibuya-simulation に活かせそうな点

1. **創発判定の閾値を事前宣言する**。Gaara は「ドローン署名 = 1〜2カテゴリが80%以上」
   「解釈署名 = 4カテゴリ以上かつ最大40%未満」を先に決めてからログを見ている。
   shibuya の R²(k) 掃引でも、**「相転移とみなす条件」をデータを見る前に文章化**しておけば、
   後付け解釈の疑いを構造的に潰せる。no-fingerprint 原則とも整合する。
2. **単一語介入という極小の対照実験**。shibuya のペルソナ/アーキタイプで、
   「職業名詞1語だけを入れ替えた同一 seed 対照」は CRN 実験基盤(既存の `conf/experiments/`)に
   そのまま載る。「語の含意が行動を変えるが認知モードは変えない」という二層の結論は、
   `natural-coinage-observation`(自然発生語彙の観測)とも接続する。
3. **文法介入(主語-目的語の解体)**。shibuya のプロンプトは「あなたは〜です。あなたは決めます」型のはず。
   「あなたは渋谷という身体の20万分の1の場所です」型の DNA を **ablation セルとして 1 本だけ**用意すると、
   「行動指示ゼロ」をさらに一段深く主張できる。ただし Gaara の VG は**緊急時に行動が崩壊した**ので、
   本番既定にはせず対照専用にするのが正しい(Gaara 自身の結論がそれ)。
4. **指標が主張に有利すぎるときに自分で壊す手続き**。Gaara の CORRECTION エントリは
   devlog protocol にそのまま移植できる型: 「(a) 何を測っていたか (b) 何が交絡していたか
   (c) 差し替えた指標 (d) それによって撤回される過去の結論」。
5. **README を「証拠の所在表」にする**。本選提出時、
   「主張 → 検証できる成果物パス → 再現コマンド」の3列表を README トップに置くのは低コストで効く。
   shibuya-sim の C=8.0 は README 起因なので、ここは直接の得点源。
6. **「うまくいかなかった仮説」を同格で書く**。`V_AXES` が最低スコアだった話や
   「sensory ≠ directional」の話は、成功例より説得力がある。
   devlog / 提出レポートに **Hypotheses that didn't deliver** 節を作る。
7. **認知層と物理層の厳密分離の明文化**。shibuya は既に SFM 人流(物理)と LLM 判断(認知)が分かれているが、
   それを `cluster.py` の docstring のように **「LLM は速度に触れない」と一文で宣言**しておくと、
   A 軸(創発設計)の読み手に一瞬で伝わる。現状は実装上そうなっていても文書上の主張になっていない可能性がある。
8. **ログを最初からコミットしておく**。Gaara は 499 ファイル中大半が実験ログ実データで、
   「誰でも再スコアできる」ことが講評の信頼につながっている。
   shibuya は結果を除外している(lunar も同様)が、**代表 run 数本の JSONL は同梱**する価値がある。

## web リサーチ

- **ペルソナ/ロール・プロンプトの行動効果**(Gaara の noun battery の一般文脈)
  - "The Prompt Makes the Person(a): A Systematic Evaluation of Sociodemographic Persona Prompting for LLMs"
    (arXiv:2507.16076) — ロール採用形式と人口統計プライミング戦略が LLM シミュレーションに与える影響を体系評価。
    https://arxiv.org/abs/2507.16076
  - "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of LLMs"
    (arXiv:2311.10054) — システムプロンプトのペルソナは**性能を改善しない**という反証側の主要論文。
    Gaara の「認知モードは名詞にほぼ不変」という発見と整合する(が Gaara は**行動**は変わると示している点が新しい)。
    https://arxiv.org/html/2311.10054v3
  - "Two Tales of Persona in LLMs: A Survey of Role-Playing and Personalization" (arXiv:2406.01171)
    https://arxiv.org/pdf/2406.01171
  → Gaara の貢献の位置づけ: 既存研究は「ペルソナはタスク性能を上げるか」を問うているが、
    Gaara は「**同一アーキテクチャ下で語の含意が空間行動をどう変えるか**」を単一語で分離した。
    この設計は shibuya の「生まれつきか環境か」にも移植可能な形式。
- **テクノアニミズム / animacy(B軸で評価された思想的背景)**
  - Casper Bruun Jensen & Anders Blok, "Techno-animism in Japan: Shinto Cosmograms, Actor-network Theory,
    and the Enabling Powers of Non-human Agencies" — 日本の技術実践を神道由来のアニミスト基層から読む古典的論考。
    https://www.researchgate.net/publication/258192445_Techno-animism_in_Japan_Shinto_Cosmograms_Actor-network_Theory_and_the_Enabling_Powers_of_Non-human_Agencies
  - "Engineering Robots with Heart in Japan: The Politics of Cultural Difference in Artificial Emotional Intelligence"
    (Oxford Academic, *Imagining AI*) — 「アニマシー工学」への展開。
    https://academic.oup.com/book/46567/chapter/408130483
  - "Expanding Affective Computing Paradigms Through Animistic Design Principles" (Springer)
    https://link.springer.com/chapter/10.1007/978-3-030-85623-6_9
  - "Animacy and the Eye of the Beholder"(CHI 2026) — 運動・形態から生命感が立ち上がる条件の実証研究。
    https://dl.acm.org/doi/10.1145/3772318.3791969
  → **「世界観を装飾ではなくアーキテクチャの駆動原理として明示する」と B 軸で加点される**という実例。
    shibuya の `nature-like-systems`(自然界を模した仕組み志向)も、同じ形で
    「なぜボトムアップ創発を第一候補にするのか」を思想として明文化すると効く可能性がある。
- **キーワード分類の脆さ(講評が指摘した弱点の一般解)**
  講評は `score_diversity.py` の正規表現分類に対し「Embedding ベース分類や LLM-as-judge を併用せよ」と提言。
  同種の指摘は MAS 観測性の文献にもあり、「trace ベースのオンライン信号 + オフラインの意味的接地指標 +
  選択的 LLM-as-judge」の併用が推奨されている。
  https://arxiv.org/html/2606.01365v2

## 正直な註記

- スライド PDF はレビューリポに存在しないため、**スライドからの追加知見はゼロ**。
  README が言及する demo video / PDF specs もリポジトリ外にあり、本調査からはアクセスできていない。
- リポジトリ HEAD は 2026-05-09、講評は 2026-05-11 なので、講評対象コードとほぼ一致しているとみてよい。
- `Gaara_Animism_Viewer/` は REPORT.md では「companion 3D web viewer」として列挙されているが、
  **リポジトリ内には存在しない**(公開ビューアは Vercel 上の別配置)。
