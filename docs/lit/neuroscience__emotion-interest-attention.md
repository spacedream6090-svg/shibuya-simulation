# 脳科学: 感情・興味・注意 — 文献リサーチと実装提案(2026-07-07)

> 依頼: エージェントに **感情(emotion)・興味(interest/curiosity)・注意(attention)** を実装する
> ための **脳科学(neuroscience)** 文献を調査し、このシミュに接続できる **実装提案** にまとめる。
> ユーザーは認知科学だけでなく **脳科学の視点で人の思考に関する新しい発見** を期待している。
> 関連既存メモ: [needs__individual-differences.md](./needs__individual-differences.md)(欲求の個人差=trait 倍率)/
> [cognition__drive-firing-memory.md](./cognition__drive-firing-memory.md)(発火ゲージ・記憶検索の接地)/
> [media__entertainment-effects.md](./media__entertainment-effects.md)(気分修復 seam)/
> [../design-candidates/social-life-gaps.md](../design-candidates/social-life-gaps.md) §15(内面・感情の未実装棚卸し)。
>
> 本リポジトリの設計契約に沿う(既存 lit と同格):
> - **因果構造だけ文献接地、magnitude は conf で可変**(決め打ち禁止)。
> - **R1(k 非依存)死守**: 内面変数の入力は「観測可能な出来事」のみ。belief 書き戻し・k.writeback を参照しない。
> - **no-fingerprint**: trait/次元名を知ってよいのは `factors/` だけ。`cognition/drive` も engine も不透明な数値しか見ない。
> - **決定論**: 既定 OFF はバイト一致。乱数を引く場合のみ **新規 stream**。多くの機構は決定論ゲートで RNG 不要。
> - **最小版 / 本格版** を分けて提案(1万〜3万エージェント規模=計算コスト意識)。

---

## 0. 統一する視点 — なぜ3系をまとめて設計するか(脳科学の「新しい発見」の核)

**核心アイデア: 既存の valence(正負1次元)に arousal(覚醒度)を足して core affect(2次元)にし、
その arousal を「サリエンス・ネットワーク的なハブ変数」として注意・記憶・発火へ配線する。**

脳科学が2000年代以降に収束させた知見は「**感情・興味・注意は別々のモジュールではなく、
覚醒(arousal)とサリエンス(salience)を共有した1つの回路系**」である:

- **Russell の core affect**: すべての感情状態は valence(快−不快)× arousal(覚醒)の2軸に還元できる
  (Russell 1980, 2003)。**既存シミュの valence は1軸だけ**=半分しか無い。
- **Menon & Uddin のサリエンス・ネットワーク**: 前部島皮質(AI)+前帯状皮質(ACC)が **顕著な出来事を検出し、
  内向き注意(DMN)と外向き注意(CEN)を切り替えるスイッチ** として働く(Menon & Uddin 2010)。
  = 感情(何が顕著か)・注意(どこに向くか)・興味(何を探すか)が **同じサリエンス信号で駆動される**。
- **arousal が3系の結び目**: 感情の強さ=arousal、注意の捕捉=高 arousal 刺激が注意を奪う(Vuilleumier 2005)、
  記憶の符号化=arousal が扁桃体経由で海馬の定着を強める(LaBar & Cabeza 2006)、好奇心=中脳ドーパミン系の
  SEEKING 覚醒(Panksepp 1998; Gruber et al. 2014)。

**設計上の含意**: arousal を **drive ゲージと同型の「漏れ積分器(leaky accumulator)」** として1本足すだけで、
感情・興味・注意を三位一体で回せる。既存の drive.py(欲求ゲージ)・memory.py(importance)・
factors(valence→state)に **最小の配線** で接続でき、計算コストはほぼゼロ(スカラ1本+決定論ゲート)。

> 用語の対応(脳科学 → 本シミュ):
> - **core affect** = (mood_valence, arousal)。mood_valence は既存 state(efficacy−grievance)から**導出**でき、
>   新規に足すのは **arousal のみ**。
> - **phasic(相動性)vs tonic(持続性)**: arousal=phasic(速い・減衰する transient)、grievance/efficacy=tonic
>   (遅い mood/慢性)。**感情と気分の時間スケール差** を、新 transient と既存 state の分担で自然に表現する。

---

## 1. 感情(affect / emotion)

### 1.1 core affect — valence × arousal の2次元(Russell)
- **主張**: すべての感情は2つの神経生理系 = **valence(快−不快の連続体)** と **arousal(覚醒・活性の連続体)**
  から構成される。感情語は円環(circumplex)上に配置される(28語の類似度判断で2次元が回復)。core affect は
  常に存在する背景状態で、離散感情はその上に構成される(Russell 1980; **core affect と心理的構成**: Russell 2003)。
- **シミュへの含意**: **既存 valence は1軸=半分**。arousal 軸を足すことで「同じネガでも、しょんぼり(低覚醒)と
  激怒(高覚醒)」を区別でき、注意・発火・記憶への効き方が質的に変わる(下記 1.6・§4)。

### 1.2 離散基本感情(Ekman)vs 構成主義(Barrett) — 「次元 か 離散 か」への回答
- **Ekman(離散)**: 怒り・嫌悪・恐怖・喜び・悲しみ・驚き(+軽蔑)は文化普遍で、生得的に配線された基本感情
  (Ekman 1992)。それぞれ固有の表出・行動傾向を持つ。
- **Barrett / Russell(構成主義)**: 離散感情は脳に固定モジュールとして在るのではなく、**core affect(valence×arousal)
  という素材の上に、文脈と概念で構成されるラベル**である(Russell 2003; Barrett 2017 "theory of constructed emotion")。
- **設計への回答(重要)**: 「valence-arousal か 離散感情か」は二択ではなく **二層に分ける**のが脳科学的に正しい:
  - **ゲート計算(非LLM)は次元(valence×arousal)で**行う(連続量=閾値・importance・salience の演算に向く)。
  - **プロンプト注入(LLM)は離散ラベルで**行う(「今は不安/高揚している」等、言語表現の豊穣化に向く)。
  - これは構成主義そのもの(離散=core affect 上に構成される言語ラベル)であり、理論的にも一貫する。

### 1.3 appraisal theory — OCC / Scherer 成分過程モデル
- **OCC(Ortony, Clore & Collins 1988)**: 感情は環境の **評価(appraisal)** から生成される。出来事(目標との
  合致)・行為者(自他の責任)・対象(選好)の3系統の評価から22種の感情を導く。**計算機で扱える(computationally
  tractable)** ことを明示的に狙った枠組み=エージェント実装の定番。
- **Scherer 成分過程モデル(CPM)**: 感情は **逐次的な評価チェック**(新奇性・快不快・目標妥当性・対処可能性・
  規範適合)の同期的変化(Scherer 2009)。評価が更新されるたびに感情経験が変わる。
- **シミュへの含意**: 完全な OCC は重い。**「軽量 appraisal」= (valence 符号, arousal, 原因の帰属:自分/他人/状況)**
  の3ビットだけで、離散ラベルへ写像するのに十分(§1.2 の離散層に使う)。

### 1.4 somatic marker hypothesis(Damasio / Bechara)
- **主張**: 過去の情動経験が身体信号(somatic marker)として ventromedial 前頭前皮質に蓄積され、意思決定時に
  **選択肢を情動で事前バイアス**する。Iowa Gambling Task で健常者は「悪いデッキ」を選ぶ前に **皮膚電気反応が上昇**
  (=意識的に理由を言える前に情動が先に警告する)。vmPFC 損傷者はこの予期的反応が出ず、不利な選択を続ける
  (Damasio 1994; Bechara, Damasio, Tranel & Damasio 1997, Science)。
- **シミュへの含意**: 「合理計算の前に、過去に嫌な思いをした対象/場所/相手を情動で忌避する」= **記憶に付いた
  valence タグが、次の行動選択を安価にバイアスする** 経路。関係台帳や場所なじみに valence を持たせ、接近/回避の
  重みに使える(本格版)。

### 1.5 affect-as-information & mood-congruence(Schwarz & Clore; Bower)
- **affect-as-information(Schwarz & Clore 1983)**: 人は判断時に暗黙に「これについてどう感じるか?」を参照し、
  **今の気分を判断材料に流用**する(誤帰属)。ポジ気分→物事を肯定的に、ネガ気分→否定的に評価。
- **mood-congruent memory(Bower 1981)**: 気分と一致する価の記憶が想起されやすい/符号化されやすい。
- **シミュへの含意**: (a) **プロンプトに気分1語**を注入すると、LLM の発話・判断が気分整合的になる(affect-as-info)。
  (b) **記憶検索(retrieve)を今の valence 符号に寄せる**バイアス(mood-congruent recall)。どちらも既存機構に薄く乗る。

### 1.6 感情 → 記憶 / 行動 の効き
- **arousal → 記憶定着(LaBar & Cabeza 2006, Nat Rev Neurosci)**: 情動喚起した出来事は扁桃体→海馬投射により
  **符号化・定着が強まる**。高頻度神経活動が海馬・扁桃体で符号化成功時に上昇(直接証拠)。
- **arousal → 行動/認知(Yerkes-Dodson 1908)**: 覚醒と遂行は **逆U字**。低覚醒=退屈・低遂行、中覚醒=最適、
  過覚醒=ストレスで注意狭窄・遂行低下。単純課題は高覚醒寄り、複雑課題は低覚醒寄りが最適。
- **シミュへの含意**: arousal は (a) **memory.importance を押し上げ**(顕著記憶として残る)、(b) **発火閾値を
  逆U字で変調**(中覚醒で行動しやすく、過覚醒で狭窄)。両方とも入力は観測イベントのみ=R1 を壊さない。

### → 感情の実装提案

| 版 | 何を足すか | 型 | ゲート先 | 文献 |
|---|---|---|---|---|
| **最小** | `agent.arousal ∈[0,1]`(baseline 0.2、毎 step 減衰)。**valence は既存**(mood_valence = efficacy−grievance で導出) | **state+gate**(非LLM・決定論・RNG不要) | ①memory.importance を +w·arousal ②発火 effective_threshold を arousal で変調(逆U字) ③§3 の salience 利得 | Russell 1980; LaBar&Cabeza 2006; Yerkes-Dodson 1908 |
| **最小+** | プロンプトに **気分1語**(valence×arousal の象限→「不安/高揚/しょんぼり/穏やか」等)を1行注入 | **prompt 注入**(既定 OFF、media.prompt_context と同型) | 発火プロンプト文脈 | affect-as-info(Schwarz&Clore 1983); Russell 2003 |
| **本格** | 軽量 appraisal(valence符号, arousal, 原因帰属)→ **離散感情ラベル**(Ekman系6語)。記憶検索を valence 整合にバイアス | prompt 注入 + gate | プロンプト + memory.retrieve のスコア | OCC 1988; Scherer 2009; Barrett 2017; Bower 1981 |
| **本格+** | 記憶/場所/関係に **valence タグ**(somatic marker)→ 接近/回避の行動重み | state+gate | 行動選択(routine/planning) | Damasio 1994; Bechara+ 1997 |

**arousal 更新則(最小版の具体案)**: `arousal += g·signal`(観測イベント由来)、毎 step `arousal += -λ·(arousal−a0)`。
- signal 源(すべて観測量=R1安全): 聞いた/読んだ発話の **|valence|**、**novelty**(novel_place / unknown_word)、
  **驚き**(|valence| の大きい news)、**被話しかけ**(addressed)、**混雑ストレス**(congestion)。
- drive ゲージと同じ「漏れ積分器」構造 → 既存コードの発想と地続き。**states 監査集合(efficacy/grievance/ownership)には
  入れない**(R²(k) の因子分解を汚さないため、drive ゲージと同格の内部 transient として持つ)。

---

## 2. 興味・好奇心(interest / curiosity)

### 2.1 information-gap theory(Loewenstein)/ collative variables(Berlyne)
- **Loewenstein 1994(Psychol. Bull. 116, 75–98)**: 好奇心は **知識のギャップ(information gap)** に注意が向いた
  ときに生じる **認知的な剥奪感**。ギャップを埋めるべく情報探索へ動機づけられる。**「知っていることと知りたいこと
  の差」が好奇心の量**。
- **Berlyne(1960)collative variables**: 好奇心は **新奇性・複雑性・不確実性・葛藤** の4つの照合変数が **覚醒を上げる**
  ことで駆動される。中覚醒=快(Wundt 曲線)。探索は2種 — **inspective(不確実性低減=特定的好奇心)** と
  **diversive(退屈解消=刺激追求)**。
- **シミュへの含意**: **既存の novel_place / unknown_word はまさに collative variables**。好奇心=「予測とのズレ」を
  信号化し、arousal と drive ゲージを押し上げる。ギャップの大きさ(=novelty 量)に比例。

### 2.2 報酬予測誤差(RPE)とドーパミン(Schultz)/ SEEKING(Panksepp)
- **Schultz, Dayan & Montague 1997(Science 275, 1593–1599); Schultz 1998(J Neurophysiol 80, 1–27)**:
  中脳ドーパミンニューロンは **報酬予測誤差(RPE)** を符号化 — 予測外の報酬で発火(正の誤差)、予測どおりで無反応、
  期待した報酬の欠落で抑制。**新奇・顕著な刺激** でも相動性発火。= **「驚き」そのものが学習・接近の信号**。
- **Panksepp SEEKING system(1998)**: 中脳辺縁ドーパミン系(VTA 起源)が **探索・foraging・好奇心・期待** を
  エネルギー付与する **「対象なき欲動(a goad without a goal)」**。内発的動機はこの SEEKING の高度化。
- **シミュへの含意**: 好奇心は **RPE(予測とのズレ)= 新奇/驚き** で発火する **相動性信号**。arousal 更新則の
  novelty/驚き項がまさにこれ。**「興味 → 行動の方向づけ」= RPE の高い方向へ探索を向ける**(本格版で foraging に接続)。

### 2.3 好奇心 → 記憶(Gruber & Ranganath)/ 総説(Kidd & Hayden)
- **Gruber, Gelman & Ranganath 2014(Neuron 84, 486–496)**: 高好奇心状態では **中脳・側坐核の活動が上昇** し、
  **海馬の符号化が強まる**。重要な発見 = **好奇心が高いときは、対象そのものだけでなく、同時に居合わせた無関係な
  情報(incidental)まで記憶が良くなる**。好奇心と外的報酬が同じ回路を共有。
- **Kidd & Hayden 2015(Neuron 88, 449–460)**: 好奇心の総説。眼窩前頭皮質(OFC)が **賭けの stake と選択肢の
  情報価値の両方** を符号化、後帯状皮質は探索試行で発火率が高い。好奇心=情報を報酬として扱う。
- **シミュへの含意**: **好奇心(novelty/RPE)→ memory.importance を押し上げ**、その出来事(と周辺)を顕著記憶として
  残す。§1.6 の arousal→記憶と同じ経路で実装でき、**arousal を共通ハブにする設計** の直接の裏付け。

### 2.4 information foraging theory(Pirolli & Card)
- **Pirolli & Card 1999(Psychol. Rev. 106, 643–675)**: 人は情報を **採餌(foraging)** のように探す — 単位時間あたりの
  情報獲得を最大化するよう、**information scent(手がかりから推定した情報価値)** に従って探索先を選ぶ。情報パッチ間の
  滞在/移動を最適化。
- **シミュへの含意**: **「興味 → 行動の方向づけ」の本格版**。エージェントの移動先/注意先を **information scent の高い方向**
  (新奇な場所・未知語の出所・話題の濃い相手)へバイアスする。ただし行動選択への介入=重い(本格版)。

### → 興味の実装提案

| 版 | 何を足すか | 型 | ゲート先 | 文献 |
|---|---|---|---|---|
| **最小** | **novelty/驚き → memory.importance 加点**(観測時に buffer episode の importance を底上げ) | **state+gate**(非LLM・決定論) | memory.observe/consolidate(顕著記憶として残る) | Gruber+ 2014; Schultz 1997 |
| **最小+** | novelty/驚き → **arousal と drive ゲージを押し上げ**(既存の novel_place/unknown_word 重みに RPE 的な「予測外ボーナス」) | state+gate | arousal(§1)+ drive.add | Loewenstein 1994; Berlyne 1960; Panksepp 1998 |
| **本格** | プロンプトに **「今きになっていること」1行**(未解消の最大 information-gap を1語) | prompt 注入(既定 OFF) | 発火プロンプト文脈 | Loewenstein 1994; Kidd&Hayden 2015 |
| **本格+** | **information foraging**: 移動先/注意先を information scent 高い方向へバイアス | state+gate | 行動選択(routine/planning) | Pirolli&Card 1999 |

**個人差との分担(重要・既存と非衝突)**: 「**何にどれだけ興味を持ちやすいか(trait)**」は既に needs_profile の
**stimulation 次元 → novel_place/unknown_word 倍率** で表現済み([needs__individual-differences.md](./needs__individual-differences.md))。
本節が足すのは「**その時々の好奇心 state(RPE 相動性)**」= transient。**trait(生得の感度)× state(いまの驚き)** の
乗算で、既存の traits/states 二層構造と同じ分担になる(需要 profile は生まれつき、arousal/curiosity は経験で動く)。

---

## 3. 注意(attention)

### 3.1 top-down(dorsal)vs bottom-up(ventral)(Corbetta & Shulman)
- **Corbetta & Shulman 2002(Nat Rev Neurosci 3, 201–215)**: 注意は2系統。
  - **背側前頭頭頂系(dorsal: IPS+FEF)= top-down / goal-driven**: 目標・期待に従って意図的に注意を配分。
  - **腹側前頭頭頂系(ventral: TPJ+下前頭、右半球優位)= bottom-up / stimulus-driven**: **予期しない・行動関連の
    刺激** を検出し注意を再定位。「**回路遮断器(circuit breaker)**」として背側系に割り込む。
- **シミュへの含意**: 知覚のゲートは2成分の和 — **bottom-up(顕著さ: 新奇・強 valence・自分宛て)** と
  **top-down(目標/欲求への関連度)**。「誰の発話を聞くか・何に気づくか」= この合成サリエンスで決まる。

### 3.2 サリエンス・ネットワークとスイッチング(Menon & Uddin; Seeley)
- **Menon & Uddin 2010(Brain Struct Funct 214, 655–667)**: 前部島皮質(AI)+ACC の **サリエンス・ネットワーク(SN)**
  が **顕著イベントを bottom-up 検出** し、**DMN(内向き=自己参照)と CEN(外向き=課題実行)を動的にスイッチ** する
  中枢。ACC 経由で運動系へ、島皮質で自律反応(=arousal)へ結合。
- **Seeley et al. 2007(J Neurosci 27, 2349–2356)= SN を機能結合で同定した原著**(※本セッションで直接検索せず・要確認)。
- **シミュへの含意**: **感情(arousal)・注意(切替)・興味(顕著さ検出)が同じ SN で束ねられる** = §0 の統一設計の
  神経基盤。実装では **1本の salience 関数** が「注意を割り当てる/内省へ切り替える」を担う。

### 3.3 容量制約(Cowan)= 認知負荷 / ワーキングメモリ
- **Cowan 2001(Behav Brain Sci 24, 87–114)**: 注意の焦点(focus of attention)の容量は **平均約4チャンク(3–5)**。
  Miller の7±2 を下方修正。**同時に保持・処理できる項目数には強い上限**。
- **シミュへの含意**: **同時に多数の刺激(混雑・複数話者・大量 TL)が来ても、符号化・処理できるのは上位数件だけ**。
  = **salience 上位 K 件だけを知覚に通す** ゲート。これは知覚の選択であると同時に、**計算コストを下げる**
  (記憶書き込み削減・プロンプト短縮)= 1万〜3万規模に理想的。

### 3.4 感情による注意バイアス(Vuilleumier; Anderson & Phelps)
- **Vuilleumier 2005(Trends Cogn Sci 9, 585–594)**: 扁桃体が **情動的(特に脅威)刺激を高速検出** し、感覚野への
  逆投射で **知覚処理を増強**。情動刺激は **top-down 注意の変動を上書きして bottom-up に注意を奪う**。
- **Anderson & Phelps 2001(Nature 411, 305–309)**(※検索で言及・DOI は知識ベース): 両側扁桃体損傷者は
  情動刺激への注意バイアスを示さない = **扁桃体が情動→注意バイアスの起点**。
- **シミュへの含意**: **強 valence(特にネガ/脅威)の刺激は salience を跳ね上げ、注意を優先的に捕捉** する。
  = salience 関数の bottom-up 項に **|valence| と arousal** を入れる根拠。

### → 注意の実装提案

| 版 | 何を足すか | 型 | ゲート先 | 文献 |
|---|---|---|---|---|
| **最小** | **salience 上位 K 件ゲート**: 1 step に同時知覚できる発話/TL/news を、salience スコア上位 K(≈3–4、Cowan)だけ memory.observe・プロンプトへ通す | **state+gate**(非LLM・決定論・**計算削減**) | memory 書込 + プロンプト材料の選別 | Cowan 2001; Corbetta&Shulman 2002 |
| **最小+** | salience = **bottom-up**(novelty + \|valence\| + addressed_to_me + arousal 利得)+ **top-down**(needs_profile 関連度 + 当日目標語の一致) | state+gate | 同上の K 選抜スコア | Corbetta&Shulman 2002; Vuilleumier 2005 |
| **本格** | **注意モード切替(SN)**: 高 drive・沈黙継続で **内向き(内省/DMN)**、被話しかけ・高 salience で **外向き(CEN)** へ切替。K を arousal/負荷で可変 | state+gate | 発火の内省 vs 応答の優先、K の動的調整 | Menon&Uddin 2010; Yerkes-Dodson 1908 |
| **本格+** | **top-down 注意セット**: 当日計画/目標に一致する語・相手の salience を恒常的に加重(注意の構え) | state+gate | salience の top-down 項の重み | Corbetta&Shulman 2002 |

**salience スコア(最小+版の具体案、決定論・RNG不要)**:
```
salience(item) = w_nov·novelty(item)              # bottom-up: 新奇(collative)
               + w_val·|valence(item)|             # bottom-up: 情動強度(Vuilleumier)
               + w_adr·addressed_to_me(item)       # bottom-up: 自分宛て(社会的顕著)
               + w_aro·arousal_gain                # 感情→注意利得(SN, arousal ハブ)
               + w_top·relevance_to_goal_needs(item)  # top-down(needs_profile + 当日目標語)
```
`item ∈ {同席者の発話, TL投稿, news}`。上位 K のみ知覚に通す。K 既定=既存挙動を壊さぬよう **十分大(=全通し)**、
ON 時に K=3–4 へ絞る(Cowan)。**relevance_to_goal_needs の needs 参照は不透明な倍率経由**(no-fingerprint 遵守)。

---

## 4. 三系の結合(coupling)— arousal/salience を共有ハブにする

脳科学の最重要知見は「**3系が独立でなく、arousal と salience を共有した1つの回路**」であること。
本シミュではこれを **arousal(1スカラ)+ salience(1関数)** で表現する。結合の因果:

| 経路 | 神経基盤(文献) | 本シミュの配線 |
|---|---|---|
| **感情 → 注意** | 情動刺激が bottom-up に注意を捕捉(Vuilleumier 2005; Anderson&Phelps 2001) | \|valence\|・arousal が salience の bottom-up 項を上げる → 上位 K に残りやすい |
| **興味 → 注意** | 好奇心=SEEKING 覚醒が探索的注意を駆動(Panksepp 1998; Berlyne 1960) | novelty/RPE が arousal と salience を上げる → 新奇 item が注意に通る |
| **興味 → 感情** | RPE/新奇が相動性ドーパミン=覚醒(Schultz 1997) | novelty/驚きが arousal 更新則の主要 signal |
| **注意 → 記憶** | 注意した情動項が扁桃体→海馬で符号化増強(LaBar&Cabeza 2006; Gruber+ 2014) | K に通った高 arousal item だけ importance 加点 → 顕著記憶へ |
| **感情 → 行動** | arousal と遂行の逆U字(Yerkes-Dodson 1908) | arousal が発火 effective_threshold を逆U字変調 |
| **統合スイッチ** | SN(島皮質+ACC)が内向き/外向き注意を切替(Menon&Uddin 2010) | 高 salience→外向き(応答)、高 drive/沈黙→内向き(内省) |

**結合の実装的な美点**: これらは **arousal 1本と salience 1関数** に集約されるので、機構ごとに別変数を持たず、
相互作用が自然に創発する(例: ネガ発話→arousal↑→注意が偏る→その記憶が濃く残る→気分が引きずる=
mood-congruence のループ)。**追加する状態はスカラ1つ**で、この連鎖全部が回る。

---

## 5. 実装提案まとめ(最小版 / 本格版)

### 5.1 最小版 = 3つの小改造で三位一体(すべて非LLM・決定論・既定 OFF でバイト一致)
1. **arousal スカラ追加**(§1): drive ゲージと同型の漏れ積分器。観測イベント(\|valence\|・novelty・驚き・
   被話しかけ・混雑)で上昇、毎 step baseline へ減衰。**states 監査集合には入れない**(R²(k) を汚さない)。
2. **novelty/arousal → memory.importance 加点**(§1.6・§2.3): 観測時に顕著記憶として底上げ。既存 importance の
   既定(3.0)+ 重み·(arousal, novelty)。**LLM 統合前に非LLMで事前タグ** = 顕著記憶が生き残る。
3. **salience 上位 K ゲート**(§3): 同時知覚を salience 上位 K(≈3–4)に制限。**知覚の選択 + 計算削減**。
   salience = bottom-up(novelty+\|valence\|+addressed+arousal)+ top-down(needs 関連+目標語)。

→ この3点だけで、感情(arousal)・興味(novelty→importance)・注意(salience K ゲート)が
**1つの arousal ハブで結合** し、§4 の連鎖が回る。**追加状態はスカラ1つ、RNG stream 不要、計算はむしろ軽くなる**。

### 5.2 本格版 = 表現力と方向づけを足す
- **離散感情ラベル + 気分/興味のプロンプト注入**(§1.2–1.5, §2.3): 軽量 appraisal→Ekman系ラベル、
  「気分1語」「今きになっていること1行」を発火プロンプトへ(既定 OFF、media.prompt_context と同型)。
- **somatic marker**(§1.4): 記憶/場所/関係に valence タグ→接近/回避の行動重み。
- **information foraging**(§2.4): 移動先/注意先を information scent 高い方向へ。
- **注意モード切替(SN)**(§3.2): 内向き(内省)/外向き(応答)の動的切替、K を負荷で可変。

### 5.3 型の割り当て(どの機構が state+gate か prompt 注入か)
| 機構 | 推奨型 | 理由 |
|---|---|---|
| arousal(core affect の第2軸) | **state+gate** | 連続量の演算(閾値/importance/salience)= 非LLM が正確・安価・決定論 |
| novelty/RPE → importance | **state+gate** | 記憶符号化の重み付け=数値演算 |
| salience 上位 K ゲート | **state+gate** | 知覚選択=決定論ソート、しかも計算削減 |
| mood-congruent 検索バイアス | **state+gate** | retrieve スコアの補正=数値 |
| 気分1語 / 離散感情ラベル | **prompt 注入** | LLM の言語表現を豊穣化(ゲートでは表せない) |
| 今きになっていること1行 | **prompt 注入** | 発話内容の方向づけ=言語 |
| information foraging / 行動重み | **state+gate** | 行動選択の数値バイアス(ただし統合先が重い) |

---

## 6. 既存機構との統合方法(設計契約の遵守)

### 6.1 valence(1D)→ core affect(2D)への拡張
- **既存**: `sentiment.valence(text) ∈ [-1,1]`(刺激の価)→ `on_heard_valence` が grievance/efficacy を動かす。
- **拡張**: valence(刺激の価)は据え置き。**agent の core affect = (mood_valence, arousal)** とし、
  - `mood_valence` は **既存 state から導出**(例 `efficacy − grievance` を [-1,1] に写像)= 新規変数ゼロ。
  - `arousal` **のみ新規**。`on_heard_valence` の隣に `on_arousal`(\|valence\|・novelty で arousal↑)を並べる。
- こうすると **mood(遅い tonic)= efficacy/grievance、emotion(速い phasic)= arousal transient** と時間スケールが
  自然に分離(§0)。既存の grievance 更新則(混雑・被傾聴・達成・公園・金銭圧)はそのまま mood 側で生き続ける。

### 6.2 needs_profile(trait 倍率)と arousal/curiosity(state)の分担
- needs_profile の5次元(stimulation/security/relatedness/competence/autonomy)は **生得の感度倍率**(何を欲し/
  何を不快に感じるか)を既に担う。**本提案はこれと衝突しない**:
  - needs = **trait 側(生まれつき・reason 別倍率)**、arousal/curiosity = **state 側(経験で動く transient)**。
  - drive.add での合成は既に **乗算合成**(drive_mods × needs_mods)。arousal/curiosity も **同じ乗算合成レーン** に
    別属性で載せられる(例 `scale *= arousal_gain`)。既定 None で現行バイト一致。
  - salience の top-down 項は needs_mods を **不透明倍率として** 参照(価値名を drive/engine に晒さない)。

### 6.3 drive 発火との統合(R1 死守)
- arousal は **観測イベントのみ** から更新(\|valence\|・novelty・驚き・addressed・congestion)= **k 非依存**。
  belief 書き戻し・k.writeback を一切見ない → 同 seed/agent なら k を変えても arousal 系列が同一 → 発火回数の
  k 間監査(±20%)を壊さない。
- 発火閾値への効きは **既存 `effective_threshold` seam** に合流(現状 `drive_threshold + theta_drift` を clip)。
  arousal 項を **逆U字**(中覚醒で閾値↓=行動しやすい、過覚醒で↑=狭窄)で足し、同じ clip[0.30, 0.85] に通す。
  既定 gain=0 で恒等(バイト一致)。
- **注意**: arousal を drive の `state_change` reason にフィードバックしない(自己増幅ループ防止)。arousal は
  drive ゲージと **並列の内部 transient** に留める。

### 6.4 memory との統合
- **観測時(observe)**: 現状 importance=3.0 固定 → `importance = 3.0 + w_a·arousal + w_n·novelty`(clip 1–10)。
  高好奇心/高覚醒の出来事が **統合(consolidate)の上位5件選抜を生き残りやすくなる**(Gruber 2014 の符号化増強)。
- **検索時(retrieve)**: 既存スコア `0.5·recency + 2.0·importance + 3.0·relevance` に、本格版で
  **mood-congruent 項**(今の mood_valence 符号と記憶の valence タグの一致)を薄く加える(Bower 1981)。既定 0 で不変。
- **salience K ゲート**は observe の **手前** に置く(通らなかった item はそもそも記憶に入らない=注意による符号化ゲート)。

### 6.5 決定論・RNG・no-fingerprint の遵守
- 最小版(arousal 更新・importance 加点・salience K ソート)は **すべて決定論=RNG 不要**。乱数を引く拡張
  (例 arousal に個体ノイズ)を入れる場合のみ **新規 stream `"affect"`** を追加(既存 draw 順を汚さない)。
- **no-fingerprint**: arousal/salience の計算は factors 層に置き、drive/engine には **不透明な数値(gain・K)** だけ渡す。
  trait/価値次元名は factors の外に出さない(needs/sdt プラグインと同じ規約)。
- **既定 OFF = バイト一致**: arousal_gain=0・importance 重み=0・K=∞ で現行と完全一致(media/needs/drift と同じ seam 方針)。

---

## 7. 出典

> 著者・年・誌名は本調査(WebSearch, 2026-07-07)で確認済み。巻号・頁・DOI は検索結果および既知の標準値に
> 基づくが、投稿前に Crossref での最終照合を推奨。**「要確認」= 本セッションで直接検索していない(記憶ベース)**。

### 感情(affect / emotion)
- Russell, J. A. (1980). A circumplex model of affect. *Journal of Personality and Social Psychology, 39*(6), 1161–1178. doi:10.1037/h0077714
- Russell, J. A. (2003). Core affect and the psychological construction of emotion. *Psychological Review, 110*(1), 145–172. doi:10.1037/0033-295X.110.1.145
- Ekman, P. (1992). An argument for basic emotions. *Cognition & Emotion, 6*(3–4), 169–200. doi:10.1080/02699939208411068
- Barrett, L. F. (2017). The theory of constructed emotion: an active inference account of interoception and categorization. *Social Cognitive and Affective Neuroscience, 12*(1), 1–23. doi:10.1093/scan/nsw154
- Ortony, A., Clore, G. L., & Collins, A. (1988). *The Cognitive Structure of Emotions.* Cambridge University Press. (OCC model; ISBN 978-0521353649)
- Scherer, K. R. (2009). The dynamic architecture of emotion: Evidence for the component process model. *Cognition & Emotion, 23*(7), 1307–1351. doi:10.1080/02699930902928969
- Damasio, A. R. (1994). *Descartes' Error: Emotion, Reason, and the Human Brain.* Putnam. (somatic marker hypothesis; ISBN 978-0399138942)
- Bechara, A., Damasio, H., Tranel, D., & Damasio, A. R. (1997). Deciding advantageously before knowing the advantageous strategy. *Science, 275*(5304), 1293–1295. doi:10.1126/science.275.5304.1293
- Schwarz, N., & Clore, G. L. (1983). Mood, misattribution, and judgments of well-being: Informative and directive functions of affective states. *Journal of Personality and Social Psychology, 45*(3), 513–523. doi:10.1037/0022-3514.45.3.513 (affect-as-information)
- Bower, G. H. (1981). Mood and memory. *American Psychologist, 36*(2), 129–148. doi:10.1037/0003-066X.36.2.129 (mood-congruent memory)
- LaBar, K. S., & Cabeza, R. (2006). Cognitive neuroscience of emotional memory. *Nature Reviews Neuroscience, 7*(1), 54–64. doi:10.1038/nrn1825
- Yerkes, R. M., & Dodson, J. D. (1908). The relation of strength of stimulus to rapidity of habit-formation. *Journal of Comparative Neurology and Psychology, 18*(5), 459–482. doi:10.1002/cne.920180503

### 興味・好奇心(interest / curiosity)
- Berlyne, D. E. (1960). *Conflict, Arousal, and Curiosity.* McGraw-Hill. (collative variables; doi:10.1037/11164-000)
- Loewenstein, G. (1994). The psychology of curiosity: A review and reinterpretation. *Psychological Bulletin, 116*(1), 75–98. doi:10.1037/0033-2909.116.1.75
- Schultz, W., Dayan, P., & Montague, P. R. (1997). A neural substrate of prediction and reward. *Science, 275*(5306), 1593–1599. doi:10.1126/science.275.5306.1593 (reward prediction error)
- Schultz, W. (1998). Predictive reward signal of dopamine neurons. *Journal of Neurophysiology, 80*(1), 1–27. doi:10.1152/jn.1998.80.1.1
- Panksepp, J. (1998). *Affective Neuroscience: The Foundations of Human and Animal Emotions.* Oxford University Press. (SEEKING system; ISBN 978-0195096736)
- Gruber, M. J., Gelman, B. D., & Ranganath, C. (2014). States of curiosity modulate hippocampus-dependent learning via the dopaminergic circuit. *Neuron, 84*(2), 486–496. doi:10.1016/j.neuron.2014.08.060
- Kidd, C., & Hayden, B. Y. (2015). The psychology and neuroscience of curiosity. *Neuron, 88*(3), 449–460. doi:10.1016/j.neuron.2015.09.010 (DOI は検索結果で確認)
- Pirolli, P., & Card, S. (1999). Information foraging. *Psychological Review, 106*(4), 643–675. doi:10.1037/0033-295X.106.4.643

### 注意(attention)
- Corbetta, M., & Shulman, G. L. (2002). Control of goal-directed and stimulus-driven attention in the brain. *Nature Reviews Neuroscience, 3*(3), 201–215. doi:10.1038/nrn755
- Menon, V., & Uddin, L. Q. (2010). Saliency, switching, attention and control: a network model of insula function. *Brain Structure and Function, 214*(5–6), 655–667. doi:10.1007/s00429-010-0262-0 (salience network)
- Seeley, W. W., et al. (2007). Dissociable intrinsic connectivity networks for salience processing and executive control. *Journal of Neuroscience, 27*(9), 2349–2356. doi:10.1523/JNEUROSCI.5587-06.2007 (**要確認**: 本セッションで直接検索せず・記憶ベース)
- Cowan, N. (2001). The magical number 4 in short-term memory: A reconsideration of mental storage capacity. *Behavioral and Brain Sciences, 24*(1), 87–114. doi:10.1017/S0140525X01003922 (誌名は知識ベース、概念は検索確認)
- Vuilleumier, P. (2005). How brains beware: neural mechanisms of emotional attention. *Trends in Cognitive Sciences, 9*(12), 585–594. doi:10.1016/j.tics.2005.10.011
- Anderson, A. K., & Phelps, E. A. (2001). Lesions of the human amygdala impair enhanced perception of emotionally salient events. *Nature, 411*(6835), 305–309. doi:10.1038/35077083 (検索で言及・DOI は知識ベース、**要確認**)

### 公式・総説(オープンアクセス起点)
- Posner, J., Russell, J. A., & Peterson, B. S. (2005). The circumplex model of affect. *Development and Psychopathology, 17*(3), 715–734. PMC2367156(circumplex の情動神経科学レビュー)
- Schwarz, N., & Clore, G. L. (2007). Feelings and phenomenal experiences. In *Social Psychology: Handbook of Basic Principles* (2nd ed.). (feelings-as-information の更新版総説)
