# 人間らしい記憶 — 認知科学リサーチ（ACT-R宣言記憶・忘却曲線・干渉・LLMエージェント統合）

作成: 2026-07-19 / 役割: Web リサーチ（コード変更なし）
目的: LLM エージェントの記憶を「忘れる」「思い出せない」「思い出そうとして失敗する」まで人間らしくするための理論基盤と、既存 `src/society/agents/memory.py` への最小差分（LLM 呼数 k-blind・決定論 RNG・数百体×数百 step 軽量）を設計する。

前提（既存実装の要点、`memory.py` を読取済み）:
- `Episode(step, text, kind, importance)`、`MemoryStore(buffer, episodes, day_summaries, relations, buffer_cap=30, store_cap=120, recency_decay=0.9983, relations_max=0)`。
- 想起 `retrieve(step, context, n)` = `0.5·recency + 2.0·(importance/10) + 3.0·relevance`。`recency = recency_decay**(step-ep.step)`、`relevance = min(1, hit数/2)`（文脈語の文字包含）。
- `query(step, query_text, n)`（agentic pull）= クエリ文を区切りで文脈語に分解し `retrieve` を再利用する非LLM検索。手掛かり無しなら `[]`。
- 係数 0.5:2:3 は Generative Agents 公式実装の実効比（recency:importance:relevance）に準拠。

---

## 1. ACT-R 宣言記憶: 活性化・想起確率・想起潜時

### 要点
ACT-R（Adaptive Control of Thought–Rational, J.R. Anderson）は宣言記憶を「チャンク」の集合とし、各チャンクに**活性化 A**を与える。A はそのチャンクが「いま必要とされる対数オッズ」の推定であり、(1) 過去の使用の頻度・新近性を反映する**基礎活性化 B**、(2) 現在の文脈から流れ込む**連想活性化**、(3) ノイズ、の和。想起は「A が最大かつ**想起閾値 τ を超える**チャンク」を返す。**τ を超えられなければ想起失敗**＝これが「思い出せない」を*閾値未達*として自然に生む構造。ノイズがあるため、同じ活性化でも確率的に成功/失敗が揺れる（＝「思い出そうとして失敗する」）。

### 式

基礎活性化（base-level learning equation, power law of forgetting）:

```
B_i = ln( Σ_{j=1..n} t_j^(-d) )
```
- n = チャンク i がこれまで参照（生成・再想起）された回数
- t_j = j 回目の参照からの経過時間
- d = 減衰率（**標準 d = 0.5**）

総活性化:

```
A_i = B_i + Σ_j ( W_j · S_{j,i} ) + ε
```
- W_j = 文脈要素 j の注意重み（W_j = W/n_cues、**W = 1** が既定、n_cues=手掛かり数）
- S_{j,i} = j→i の連想強度（§3 の fan effect）
- ε = ノイズ（下記 s のロジスティック近似）

想起確率（ガウスノイズをロジスティックで近似したシグモイド）:

```
P(retrieve i) = 1 / ( 1 + e^((τ - A_i)/s) )
```
- τ = 想起閾値（**既定 τ = -2**）
- s = 瞬時ノイズの尺度（**既定 s = 0.5**）。ガウス σ とは s = √3·σ/π の関係
- A_i = τ で P=0.5。A_i が τ を s 程度下回るごとに急速に想起不能へ

想起潜時（活性化が高いほど速い）:

```
Time_i = F · e^(-A_i)     （想起失敗時は Time = F · e^(-τ)）
```
- F = 潜時尺度係数（**既定 F ≈ 0.4** 秒）

### なぜ「思い出せない」が自然に出るか
`P` はシグモイドなので、A が τ 近傍を下回ると想起成功率が連続的にゼロへ落ちる。単純な「新近性で切る」ではなく、**頻度（何回参照したか）×新近性（いつ参照したか）×文脈連想（いま手掛かりがあるか）**の三者が閾値を跨ぐか否かで決まる。だから「昔たくさん思い出した記憶は手掛かりが薄くても出る」「重要でも一度きりで放置した記憶は消える」といった人間的な非対称が定量的に出る。

### 出典
- ACT-R（Wikipedia、概説）: https://en.wikipedia.org/wiki/ACT-R
- ACT-R Tutorial Unit4（基礎活性化・想起確率シグモイド・潜時・既定値 d=0.5, τ=-2, s=0.5, F=0.4 を明示）: https://huxianyin.github.io/blog/2020/11/09/tutorialUnit4
- Taatgen, Lebiere & Anderson, "Modeling paradigms in ACT-R"（活性化式の総説）: https://www.ai.rug.nl/~niels/publications/taatgenLebiereAnderson.pdf
- 基礎活性化式の計算効率近似（Petrov 2006、逐次近似の元ネタ）: http://act-r.psy.cmu.edu/wordpress/wp-content/uploads/2012/12/652petrovAbstract.pdf
- 近似手法の比較（Springer, Comp. Brain & Behavior 2018）: https://link.springer.com/article/10.1007/s42113-018-0015-3

---

## 2. Ebbinghaus 忘却曲線と間隔効果（spacing / testing effect）

### 要点
Ebbinghaus（1885）の忘却曲線は、学習直後に急落しその後緩やかに逓減する。ACT-R の基礎活性化式 `B = ln(Σ t^-d)` は**まさにこの冪乗則忘却を再現する**（単一参照なら B = -d·ln(t)、保持率は冪関数）。「再想起による強化」は、参照時刻リストに項 `t_j` が増えることで Σ が増え B が上がる＝**testing effect（想起そのものが記憶を強める）**として式に内蔵されている。

**spacing effect（分散学習が集中学習より長期保持に勝る）**は素の ACT-R では出ない。Pavlik & Anderson (2005) は、各参照の**減衰率 d_i を「その参照時点の活性化」に依存させる**ことで spacing を導出した（活性化が高い＝直前に想起したばかり＝集中学習の時ほど、その回の増分は速く減衰する→間隔をあけた方が durable）。

### 式

Ebbinghaus 保持（代表的定式化）:

```
R = e^(-t/S)          （R=保持率, t=時間, S=記憶強度）
```
（Ebbinghaus 自身の別式: Q(t) = 1.84 / ((log10 t)^1.25 + 1.84)）

Pavlik & Anderson (2005) 間隔効果モデル（activation-based、"optimized learning"）:

```
m_n(t_1..t_n) = β + ln( Σ_{i=1..n} t_i^(-d_i) )
d_i = c · e^( m_{i-1} ) + a
```
- m_{i-1} = i 回目の参照が起きた時点での活性化
- c = 減衰スケール、a = 減衰切片、β = 基準オフセット
- 活性化が高い時に練習すると d_i が大きく（＝その増分は速く消える）、間隔をあけて活性化が低い時に練習すると d_i が小さく（＝durable）→ spacing effect と、練習量・保持間隔との交互作用まで再現。

### 実装への含意
- **testing/spacing の第一近似**: 「再想起に成功したら参照時刻を追記」するだけで冪乗則の強化（testing effect）は無料で入る（§実装スケッチ d）。
- **本格 spacing**（d_i を活性化依存に）は任意拡張。数百体規模では c·e^m の追加コストは軽微だが、まず固定 d=0.5 で十分。

### 出典
- Murre & Dros (2015) "Replication and Analysis of Ebbinghaus' Forgetting Curve"（PMC、冪/指数フィット）: https://pmc.ncbi.nlm.nih.gov/articles/PMC4492928/
- Pavlik & Anderson (2005) "Practice and Forgetting Effects on Vocabulary Memory: An Activation-Based Model of the Spacing Effect", Cognitive Science（PubMed）: https://pubmed.ncbi.nlm.nih.gov/21702785/
- 同・ACT-R 出版リスト該当ページ: http://act-r.psy.cmu.edu/?post_type=publications&p=14206
- Pavlik & Anderson "An ACT-R model of the spacing effect"（ResearchGate、ワークショップ版）: https://www.researchgate.net/publication/228542334_An_ACT-R_model_of_the_spacing_effect
- Walsh et al. (2018) "Evaluating ... Computational Models of the Spacing Effect", Cognitive Science（複数モデル比較の総説）: https://onlinelibrary.wiley.com/doi/10.1111/cogs.12602

---

## 3. 干渉理論と fan effect（類似記憶の検索競合）

### 要点
**fan effect**（Anderson 1974-）: ある概念 j に結び付く事実の数（fan）が増えるほど、j を手掛かりにした個々の事実の想起は遅く・不確かになる。原因は**連想活性化の分配**＝j から流れ出す活性化が総量一定で、結び付き先が多いほど各先への配分が薄まる（連想干渉）。これは「よくある場所・よくある相手」に紐づく記憶ほど特定の一件を思い出しにくい、という人間的挙動を生む。

### 式

連想強度（fan で希釈）:

```
S_{j,i} = S + ln( P(i | j) )
      ≈ S - ln( fan_j )        （i が等確率のとき P(i|j)=1/fan_j）
```
- fan_j = 手掛かり j に結び付くチャンク数
- S = 最大連想強度（**多くの応用で S ≈ 2**）

これを §1 の `A_i = B_i + Σ_j W_j·S_{j,i}` に代入すると、手掛かり j が多くの記憶に現れるほど（fan_j 大）その j 経由の後押しが `-ln(fan_j)` で弱まる。

### 最小実装（既存 relevance の自然な置換）
現状 `relevance = min(1, Σ_c[c in ep.text]/2)` は「手掛かり語のヒット数」。これを連想活性化に置き換えるだけで fan effect が**無料で**入る:

```
spread_i = Σ_{j: 手掛かり語, j∈ep.text} (W/n_cues) · ( S - ln(fan_j) )
fan_j = その step 時点で語 j を含む episode 数（pool 内で数える）
```
「渋谷/ハチ公」のような頻出手掛かりは fan_j が大きく後押しが小さい＝ありふれた記憶は特定しにくい。逆に固有・稀な手掛かりは強く効く＝人間的。

### 出典
- Anderson (1999) "The Fan Effect: New Results and New Theories"（原典、連想干渉の定式化）: http://act-r.psy.cmu.edu/wordpress/wp-content/uploads/2012/12/35jra_lmr_1999.pdf
- Anderson (1983) "A spreading activation theory of memory"（要約）: http://www.jimdavies.org/summaries/anderson1983-2.html
- ACT-R Tutorial Unit5（S_{j,i}=S-ln(fan_j)、W_j=W/n、S≈2, W=1 を明示）: https://huxianyin.github.io/blog/2020/11/14/tutorialUnit5
- West et al. (2010) "Interference and ACT-R: New evidence from the fan effect"（ICCM）: http://act-r.psy.cmu.edu/wordpress/wp-content/uploads/2012/12/1075West%20Pyke%20RutledgeT%20Lang_ICCM_2010_Interference%20in%20ActR%20fan%20effect.pdf
- Thomson & Lebiere (2017) "An Account of Interference in Associative Memory: Learning the Fan Effect", Topics in Cognitive Science: https://onlinelibrary.wiley.com/doi/full/10.1111/tops.12244

---

## 4. Generative Agents（Park et al. 2023）との比較 / LLM×認知アーキテクチャ統合（2024-2026）

### 4.1 Park et al. 2023 と本実装
Generative Agents の memory stream は各記憶を **score = recency + importance + relevance** で採点（recency=指数減衰、importance=LLM 採点 1-10、relevance=埋め込み cos 類似）。論文本文は等重みだが実効比は本実装が採る 0.5:2:3。本実装は relevance を埋め込みの代わりに文脈語包含で安価代理し、LLM 呼数を増やさない設計。

**ACT-R 式との本質的な違い**:
| 観点 | Generative Agents（現行） | ACT-R 活性化 |
|---|---|---|
| recency | 指数減衰 `γ^Δt`（単一の最終アクセス時刻） | 冪乗則 `Σ t_j^-d`（**複数参照履歴**）＝頻度と分散の効果が入る |
| importance | LLM 採点（外挿）を加算 | 基礎/連想の中に内在（β オフセット等） |
| relevance | 埋め込み cos 類似（加算） | 連想活性化（**fan で希釈**＝干渉が入る） |
| 想起失敗 | 上位 n を常に返す（**失敗が構造上出ない**） | **閾値 τ 未達＝失敗**が第一級の出力 |
| ノイズ | なし（決定論） | ロジスティックノイズ＝**確率的な思い出し損ない** |

要するに ACT-R 化の眼目は「①複数参照履歴による頻度/spacing、②fan による干渉、③閾値＋ノイズによる*想起失敗*」の 3 点を GA スコアに持ち込むこと。本実装の 0.5:2:3 は「常に上位を返す」ため *forgetting/failure* が原理的に表現できないのが弱点で、そこを τ+ノイズで補うのが本リサーチの主眼。

### 4.2 ACT-R 式に置き換えた/統合した研究（2024-2026、新しめ優先）
- **Human-Like Remembering and Forgetting in LLM Agents: An ACT-R-Inspired Memory Architecture**（HAI 2025, ACM）: 本タスクにほぼ直球。LLM エージェントの記憶にベクトルベースの活性化機構を導入し、**時間減衰・意味類似の spreading・確率ノイズ**で自然な記憶動態（文脈・時間・使用頻度に応じた動的想起と忘却）を再現。反復話題による強化と、想起の確率的ゆらぎを再現したと報告。※本文は有料（ACM 403）。抄録/検索要約に基づく記述。 https://dl.acm.org/doi/10.1145/3765766.3765803
- **"My agent understands me better": Integrating Dynamic Human-like Memory Recall and Consolidation in LLM-Based Agents**（CHI 2024 EA）: 人間的な想起と統合（consolidation）を LLM エージェントに。 https://dl.acm.org/doi/10.1145/3613905.3650839
- **LLM-ACTR: from Cognitive Models to LLMs in Manufacturing Solutions**（Wu et al. 2024, AAAI-SS）: ACT-R の意思決定推論ステップの content vector を transformer 残差ストリームへ注入。認知モデル→LLM の埋め込み統合の代表例。 https://ojs.aaai.org/index.php/AAAI-SS/article/download/35610/37765/39681
- **Cognitive Architectures for Language Agents (CoALA)**（Sumers et al. 2023-24, arXiv 2309.02427）: 言語エージェントを記憶（作業/エピソード/意味/手続き）・行動・意思決定サイクルで整理する枠組み。本実装の 3 層構造の位置づけに有用。 https://arxiv.org/pdf/2309.02427
- **Cognitive LLMs: Towards Integrating Cognitive Architectures and LLMs**（2024, arXiv 2408.09176）: https://arxiv.org/pdf/2408.09176
- **Enhancing memory retrieval in generative agents through LLM-trained cross attention networks**（Hong & He, Frontiers in Psychology 2025）: Park の RIR 固定重みを、クロスアテンション（ACAN）で文脈依存の動的ランキングに置換。記憶スコア 5.94 vs 5.05（p<0.001）、イベント参加率 +8pt（32.6% vs 24.6%）。※本実装は「重み固定・非LLM」を堅持する方針なので**採用対象外だが、GA スコアの限界を示す傍証**として有用。 https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2025.1591618/full
- **Oblivion: Self-Adaptive Agentic Memory Control through Decay-Driven Activation**（2026 preprint）: 減衰駆動の活性化で階層的メモリを能動忘却。 https://arxiv.org/html/2604.00131v1
- **Human-Inspired Memory Architecture for LLM Agents**（Kerestecioglu, Microsoft, 2026 preprint）: 指数減衰（Ebbinghaus）＋想起誘導干渉＋再固定（reconsolidation）を統合。 https://arxiv.org/abs/2605.08538

### 出典（Park 原典）
- Park et al. (2023) "Generative Agents: Interactive Simulacra of Human Behavior"（arXiv 2304.03442）: https://arxiv.org/abs/2304.03442

---

## 5. 感情と記憶（情動的出来事の記憶増強）

### 要点
高覚醒（arousal）・強い価（valence）の出来事は、扁桃体がストレスホルモン（ノルアドレナリン等）を介して海馬の**固定（consolidation）を強化**し、長期に残りやすくする（LaBar & Cabeza 2006、McGaugh）。行動データでは、覚醒を伴う負価語の再生率が中性語を約 10pt 上回る（例: 覚醒負価 87% / 非覚醒負価 85% / 中性 77%）といった中程度の効果量。**現状 `observe(..., importance_bonus)` で importance を 3.0 から加点する部分実装**は、この「顕著な出来事を優先固定する」機構の妥当な対応物。

### 妥当な重み（現行スケール 1-10 への写像）
- 経験則: **高覚醒イベント → importance_bonus ≈ +2〜+3**、中覚醒 → +1、中性 → 0。文献の ~10-15pt 再生率差はこの程度の順位差で十分に再現される（過大にすると感情記憶ばかりが常に想起されて非現実的になる）。
- 活性化式に載せる場合は importance を基礎活性化のオフセット β_i に写像（例 β_i = 0.3·(importance-3)/7、log-odds で ~+0.3 は再生確率で ~+7〜10pt に相当）。感情ブーストを「β を上げる（初期活性化を底上げ）」形で入れると、**時間が経てば通常の減衰で薄れるが中性記憶より残る**という情動記憶の持続性がそのまま出る。

### 出典
- LaBar & Cabeza (2006) "Cognitive neuroscience of emotional memory", Nature Reviews Neuroscience: https://www.nature.com/articles/nrn1825
- McGaugh 系解説 "Making lasting memories: Remembering the significant", PNAS: https://www.pnas.org/doi/10.1073/pnas.1301209110
- Kensinger & Corkin (2004) "Two routes to emotional memory ... valence and arousal", PNAS: https://www.pnas.org/doi/10.1073/pnas.0306408101
- "Memory enhancement for emotional words is attributed to both valence and arousal"（Acta Psychologica 2024, ScienceDirect）: https://www.sciencedirect.com/science/article/pii/S0001691824001264
- Emotion and memory（Wikipedia、87%/77% 等の数値の出所整理）: https://en.wikipedia.org/wiki/Emotion_and_memory

---

## 実装スケッチ M-W（1 ページ）

方針: **既存の 0.5:2:3 スコアを既定として温存**し、`conf.memory_activation`（既定 False）で ACT-R 活性化ベースに切替。OFF 時は RNG を一切引かず新フィールドも書かず、`retrieve/query` の現行コードパスを 1 バイトも変えない（＝ゴールデンバイト＝R1 安全）。ON 時のみ「頻度履歴・fan 干渉・閾値＋ノイズによる想起失敗・再想起強化」を有効化。

### (a) episodes に活性化状態を持たせる差分
`Episode` に参照時刻リストを追加（既定は生成 step 一点）:
```python
@dataclass
class Episode:
    step: int
    text: str
    kind: str = "event"
    importance: float = 3.0
    refs: list[int] = field(default_factory=list)   # ★参照時刻。空=未使用（OFF時は触らない）
```
- 基礎活性化 `B = ln(Σ (max(1, step-t))^-d)`（refs が空なら生成時 `[self.step]` を暗黙に使う）。
- 逐次近似が要るスケールでは Petrov(2006) 近似で refs を固定長に畳む（当面は不要、refs は観測1＋再想起数回で十分短い）。
- **R1 注意**: 事前に「Episode/MemoryStore を pickle/`dataclasses.asdict`/json でスナップショット保存している箇所」を grep で確認。もし直列化しているなら、OFF 時に `refs` を出力形に混ぜない（`refs: list[int] | None = None` にして OFF では None のまま＝直列化に現れない、あるいは活性化状態を別 dict に隔離）。OFF でバイト不変を必ずゴールデンで検証。

### (b) retrieve/query の活性化ベース化（conf 切替・既定 OFF）
```python
def retrieve(self, step, context, n=3):
    ctx = [c for c in context if c]
    pool = self.episodes + self.buffer[:-4]
    if not getattr(self, "activation", False):
        ... # ← 現行の 0.5:2:3 を丸ごと維持（バイト一致）
    # ---- 活性化モード ----
    fan = {}                       # 手掛かり語→pool内出現数（干渉源）
    for c in ctx:
        fan[c] = sum(1 for ep in pool if c in ep.text) or 1
    W = 1.0 / max(1, len(ctx))
    out = []
    for ep in pool:
        B = math.log(sum((max(1, step - t)) ** -self.d for t in (ep.refs or [ep.step])))
        beta = 0.3 * (ep.importance - 3.0) / 7.0                 # §5 感情/重要度オフセット
        spread = sum(W * (self.S - math.log(fan[c])) for c in ctx if c in ep.text)  # §3 fan
        A = B + beta + spread + self._noise(step, ep)           # (e) の決定論ノイズ
        out.append((A, ep))
    out.sort(key=lambda t: (-t[0], -t[1].step, t[1].text))
    surfaced = [ep for A, ep in out if A >= self.tau][:n]       # ★閾値で切る
    for ep in surfaced:                                         # (d) 再強化
        if step not in ep.refs: ep.refs.append(step)
    return [ep.text for ep in surfaced]
```
`query()` は現行どおり文脈語へ分解して `retrieve` を呼ぶだけ（差分不要）。

### (c) ノイズ付き閾値 → memory_fail イベント＋プロンプト 1 行
`query()`（意図的な「思い出そうとする」パス）専用の戻り値を拡張:
- 手掛かり語はあるのに **A_i+ε が全て τ 未満** → 空でなく「失敗」を通知する薄いシグナル（例 `("__memory_fail__", cue)` か `query_ex()` 別メソッド）。
- 呼び出し側（内省/行動プロンプト組立）で `memory_fail` を検知したら、**LLM 呼び出しは増やさず**プロンプトに 1 行挿入:
  「（{手掛かり}のことを思い出そうとしたが、はっきりしない…）」
- これで「手掛かり無し（現行の `[]`）」と「手掛かりはあるが想起失敗」を区別。前者は無言、後者は*思い出そうとして失敗した*痕跡が言語化される。

### (d) 想起成功時の再強化（testing/spacing effect）
- (b) の `surfaced` に current step を `refs.append` するだけで、次回以降 B が上がる＝**testing effect**が無料で入る。
- 本格 spacing が欲しければ d を活性化依存に（Pavlik）: `d_i = c·e^(A_at_ref) + a`（refs と並行に per-ref d を保持）。**当面は固定 d=0.5 で十分**、拡張は任意。
- 暴走防止: 再強化は「実際に surfaced した上位 n のみ」。passive `retrieve` でも強化するか、意図的 `query` のみかは選択制（推奨: 両方だが query に +重み）。

### (e) RNG stream 設計と R1 安全性
- 専用ストリーム `rng.stream("mem_act", agent_id, ep.step)` を追加し、他ストリームの引き順を絶対に乱さない。ノイズはロジスティック（ACT-R のシグモイド近似と整合）:
  ```python
  u = stream.random()                 # (0,1)
  eps = self.s * math.log(u / (1.0 - u))   # ロジスティック(0, s)
  ```
- **R1 安全条件**: `activation=False` のとき①この新ストリームを一度も引かない、②`refs` を一度も書かない、③`retrieve/query` は現行式に完全一致 → 既存ゴールデン（台帳・プロンプト・スナップショット）バイト一致を保証。ON でも新ストリームが唯一の追加消費者で、既存ストリームの系列は不変であることをテストで固定。

### (f) パラメータ初期値
| 記号 | 意味 | 初期値 | 根拠 |
|---|---|---|---|
| d | 基礎活性化の減衰 | **0.5** | ACT-R 標準（§1,§2） |
| τ | 想起閾値 | **-2.0** | ACT-R 既定。step 時間単位で単一参照が Δt≈e^(4)≈55 step（≈9h @10min/step）で τ 割れ＝妥当な忘却時定数 |
| s | 想起ノイズ | **0.5** | ACT-R 既定。閾値近傍の確率的成否の幅 |
| S | 最大連想強度（fan） | **2.0** | ACT-R 応用の代表値（§3） |
| W | 注意総重み | **1.0**（W_j=W/n_cues） | ACT-R 既定（§1） |
| F | 潜時係数（任意） | **0.4** | 想起潜時を使う場合のみ（§1） |
| β係数 | 重要度→活性化オフセット | 0.3·(imp-3)/7 | §5、感情ブースト ~+7-10pt 再生に対応 |
| c, a | Pavlik 活性化依存 d（任意） | 既定は使わず固定 d | §2、本格 spacing 拡張時のみ |

**時間単位**: 本実装は 1 step=10 分。`t_j` は step 差で数えるのが自然（`recency_decay=0.9983` と同じ時間観）。ACT-R 原典は秒単位なので τ/F の絶対値は step 単位での忘却時定数（上記 τ=-2 で ~55 step）を見ながら微調整する前提。

---

### まとめ（設計判断の勘所）
1. 既存 0.5:2:3 は「常に上位を返す」ため *忘却/想起失敗* が構造上出ない。ACT-R 化の価値は**閾値 τ＋ノイズ s**で「思い出せない/思い出し損なう」を第一級イベント化する点に尽きる。
2. **fan effect は現行 relevance の自然な置換で無料**（頻出手掛かりを `-ln(fan)` で希釈）。干渉理論の最小実装として費用対効果が高い。
3. testing/spacing は **refs への append 一行**で第一近似が入る（Pavlik の活性化依存 d は任意の上物）。
4. 感情ブーストは β オフセットとして活性化に載せると「残るが薄れる」持続性が自然に出る。importance_bonus は +2〜+3/高覚醒が妥当。
5. k-blind・決定論・軽量・R1 バイト一致は「conf 既定 OFF＋専用 RNG ストリーム＋OFF 時ノータッチ」で満たせる（プロジェクト既定の「既定 OFF＝バイト一致」パターンと同型）。
