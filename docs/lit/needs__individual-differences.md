# 欲求の個人差 — 何を欲し・何を不快と感じるかの多様性(文献リサーチ、2026-07-06)

> 依頼(Wave2-2): エージェントによって「何を不快と思うか・何に欲求を持つか」が変わる多様性を実装したい。
> **本稿はその学術接地**。スコープは「**欲求プロファイルの個人差**」= 既存の欲求駆動発火(drive)の
> ゲージ入力(novel_place / congestion / unknown_word / addressed / dm_received / news / sns / company /
> silence / state_change)に対する**個人別の感度倍率**を、確立した個人差理論から決める。
> 「感情(不満・興味)の生成機構そのもの」は本稿の対象外(別途ユーザーが判断)。
> 関連既存メモ: [motivation__sdt-flow-overview.md](./motivation__sdt-flow-overview.md) /
> [factors__personality-motivation-overview.md](./factors__personality-motivation-overview.md) /
> [value__axiology-overview.md](./value__axiology-overview.md)。

## 主張(claim)
「何を欲し・何を不快と感じるか」には**安定した個人差**があり、複数の独立に確立した枠組み
(自己決定理論の基本欲求 / Schwartz 基本価値 / Reiss 16 欲求 / 刺激欲求 と 感覚処理感受性)が
一致してこれを支持する。したがって、同じ出来事(混雑・新奇・話しかけ・沈黙)への反応の強さを
**個体ごとに倍率で分散**させることは、現実の再現に向けた妥当な近似である。数値は固定実装せず、
**因果の向き(どの価値がどの入力を強める/弱めるか)だけ**をコードに、大きさは conf で調律する。

## 枠組み 1: 自己決定理論(SDT)の3基本的心理欲求 — Deci & Ryan
- **有能感(competence)・自律性(autonomy)・関係性(relatedness)** の3つが普遍的な基本欲求。
  充足で内発的動機・well-being が高まり、阻害で低下する(Ryan & Deci 2000, American Psychologist;
  Deci & Ryan 2000, Psychological Inquiry)。
- **個人差**: SDT は3欲求を普遍とするが、(i)**因果志向性(causality orientations: autonomous / controlled /
  impersonal)** と (ii)**アスピレーション(内発的 vs 外発的な人生目標の相対的重み)** で、
  人により「どの欲求充足をどれだけ強く追うか」が異なると明示している(Deci & Ryan 2000)。
- 写像: 自律性・有能感が強い個体 → **自己主導の探索**(初めての場所・未知語)への欲求が強い。
  関係性が強い個体 → **対人接触**(話しかけ・DM・同席)への欲求が強く、**沈黙**(接触の欠如)を不快に感じる。

## 枠組み 2: Schwartz 基本価値理論(10価値)
- 価値=状況を超えた目標で重要度が異なる。10価値: **自己志向(self-direction)/刺激(stimulation)/
  快楽(hedonism)/達成(achievement)/権力(power)/安全(security)/同調(conformity)/伝統(tradition)/
  慈愛(benevolence)/普遍主義(universalism)**(Schwartz 1992; Schwartz 2012, Online Readings in Psych. & Culture)。
- 円環構造の2軸: **開放性(自己志向・刺激)↔ 保守(安全・同調・伝統)**、**自己超越(慈愛・普遍)↔ 自己高揚(達成・権力)**。
  隣接価値は両立、対極は葛藤。**人により円環上のどこを重視するかが違う**=価値プロファイルの個人差。
- 写像: **刺激・自己志向**高 → 新奇入力(novel_place / unknown_word)への欲求↑。
  **安全**高 → 混雑(congestion)を不快と感じる感度↑・新奇への欲求↓。
  **慈愛**高 → 対人入力↑。**普遍主義**高 → 世の中への注意(news)↑。

## 枠組み 3: Reiss の16の基本的欲求
- 内発的動機は単一でなく**16の基本的欲求**の多面体で、各人で**強さのプロファイルが異なる**(Reiss 2004,
  Review of General Psychology)。16 = 力・独立・好奇心・受容・秩序・貯蔵・名誉・理想・交流(社会的接触)・
  家族・地位・復讐・恋愛・食・運動・平穏(tranquility)。
- 本稿に効く軸: **好奇心(curiosity)**=新奇・情報への欲求、**社会的接触(social contact)/受容**=対人欲求、
  **平穏(tranquility)**=不安・混乱の回避(=混雑・過刺激への不快)、**秩序(order)**=予測可能性の選好(=沈黙は不快でない)。
- 意義: 「欲求は人により**強度のプロファイル**が違う」という設計思想そのものが Reiss の中核主張であり、
  本実装(reason 別倍率ベクトル)の直接の後ろ盾になる。

## 枠組み 4: 刺激欲求(Zuckerman)と感覚処理感受性(Aron & Aron)= 混雑・新奇の快不快の個人差
- **刺激欲求(sensation seeking, Zuckerman)**: SSS-V の4下位=スリル&冒険 / 経験追求 / 脱抑制 /
  **退屈感受性(boredom susceptibility: 反復・単調・予測可能性への嫌悪)**。**新奇・強刺激を積極的に求める度合いの個人差**。
  加齢で低下する頑健な傾向(Zuckerman 1994, Cambridge Univ. Press; メタ分析 Cross et al. 2013, Sci. Rep., doi:10.1038/srep02486)。
- **感覚処理感受性(SPS)/ HSP**: 刺激をより深く処理し、**強い刺激・過剰刺激に圧倒されやすい**特性の連続的個人差
  (Aron & Aron 1997, J. Pers. Soc. Psychol., doi:10.1037/0022-3514.73.2.345)。**混雑・喧騒を不快と感じやすい人が居る**ことの直接の接地。
- 写像(本稿の核): **刺激欲求**高 → novel_place / unknown_word への欲求↑、**silence を退屈で不快**と感じる(silence 感度↑)、
  混雑への耐性↑(congestion 感度↓)。**感受性(低刺激欲求 ≒ 高 SPS 側)**高 → **congestion を強く不快**(感度↑)、新奇欲求↓。

---

## シミュへの落とし込み: 潜在価値プロファイル → ゲージ入力の個人別倍率

4枠組みは大きく重なる。共通因子を **5つの潜在価値次元**に縮約し(いずれも [0,1]、中心 0.5=倍率 1.0)、
既存 trait(internal_locus / nfc / risk_tolerance)+ 年齢 + 職業 + needs 専用乱数で**決定論的に**生成する。

| 潜在次元 | 主な出典 | trait/属性からの写像(向きのみ) |
|---|---|---|
| stimulation(刺激・開放) | Schwartz 刺激/自己志向, Zuckerman SS, Reiss 好奇心 | nfc↑・risk_tolerance↑ で高、**年齢↑で低**、創造系職業で高 |
| security(安全・平穏) | Schwartz 安全, Reiss 平穏/秩序, 高 SPS 側 | risk_tolerance↓ で高、年齢↑で高 |
| relatedness(関係・慈愛) | SDT 関係性, Schwartz 慈愛, Reiss 社会的接触 | (1−internal_locus) 寄り + needs 乱数、対人系職業で高 |
| competence(有能・達成) | SDT 有能感, Schwartz 達成, Reiss 好奇心 | nfc↑・internal_locus↑ で高、専門系職業で高 |
| autonomy(自律・自己志向) | SDT 自律性, Schwartz 自己志向, Reiss 独立 | internal_locus↑ で高、フリー系職業で高 |

**次元 → reason 倍率**は「どの価値がどの入力の顕著さ/不快さを強めるか」の符号表(係数の絶対値は conf で調律)。
負の入力(congestion / silence)では**倍率↑ = より速くゲージが溜まる = より不快に感じる**(=「何を不快と感じるか」の個体差)。

| reason(ゲージ入力) | 効く次元(+ は倍率↑ / − は倍率↓) | 解釈 |
|---|---|---|
| novel_place | stimulation +, autonomy +, security − | 初めての場所への欲求は刺激・自律で強く、安全志向で弱い |
| unknown_word | stimulation +, competence + | 未知語=好奇心・習得欲 |
| congestion(不快) | **security +, stimulation −** | 安全/高感受性は混雑を強く不快に、刺激欲求は混雑に強い |
| addressed | relatedness + | 話しかけられる=関係欲求 |
| dm_received | relatedness + | DM=関係欲求 |
| company | relatedness +, autonomy − | 同席の社交圧は関係欲求で快・自律欲求で薄い |
| silence(不快) | **stimulation +(退屈感受性), relatedness +(孤独)** | 沈黙の継続を退屈・孤独として不快に感じる個体差 |
| news | competence +, security + | 情報・世相への注意 |
| sns | relatedness +, stimulation + | SNS 閲覧欲 |
| state_change | competence +(自己モニタリング) | 内的変化への気づきやすさ |

## seam としての入れ方(結論を固定しない)
- **因果構造(符号表)だけ**をコードに置き、**大きさ(gain・clip 範囲)は conf.needs** に出す。既定 OFF=現行と完全一致。
- **no-fingerprint**: trait/価値名を知ってよいのは `factors/registry.py`(プロファイル生成)のみ。
  `cognition/drive.py` は reason 文字列で引く**不透明な倍率 dict** しか見ない(SDT プラグインと同じ規約)。
- **R1(k 非依存) 死守**: プロファイルは trait/年齢/職業 + needs 専用乱数のみ由来で、belief 書き戻し・k.writeback を
  一切参照しない。同じ seed/agent なら k を変えてもプロファイルは同一 → 発火回数の k 間監査(±20%)を壊さない。
- **psych.sdt との非衝突**: SDT プラグイン(既定 OFF)は内発/外発の2軸倍率(drive_mods)、needs は価値プロファイル由来の
  倍率(needs_mods)。両者は別属性で**乗算合成**でき、既定は needs 単独(sdt OFF なので衝突しない)。

## 出典(DOI / 出版社 / 公式のみ)
- Ryan, R. M., & Deci, E. L. (2000). Self-determination theory and the facilitation of intrinsic motivation,
  social development, and well-being. *American Psychologist, 55*(1), 68–78. doi:10.1037/0003-066X.55.1.68
- Deci, E. L., & Ryan, R. M. (2000). The "what" and "why" of goal pursuits: Human needs and the
  self-determination of behavior. *Psychological Inquiry, 11*(4), 227–268. doi:10.1207/S15327965PLI1104_01
- 公式: Center for Self-Determination Theory — https://selfdeterminationtheory.org/theory/
- Schwartz, S. H. (1992). Universals in the content and structure of values. *Advances in Experimental
  Social Psychology, 25*, 1–65. doi:10.1016/S0065-2601(08)60281-6
- Schwartz, S. H. (2012). An overview of the Schwartz theory of basic values. *Online Readings in
  Psychology and Culture, 2*(1). doi:10.9707/2307-0919.1116 (open access)
- Reiss, S. (2004). Multifaceted nature of intrinsic motivation: The theory of 16 basic desires.
  *Review of General Psychology, 8*(3), 179–193. doi:10.1037/1089-2680.8.3.179
- Zuckerman, M. (1994). *Behavioral Expressions and Biosocial Bases of Sensation Seeking.*
  Cambridge University Press. ISBN 978-0521437141
- Cross, C. P., Cyrenne, D.-L. M., & Brown, G. R. (2013). Sex differences in sensation-seeking:
  A meta-analysis. *Scientific Reports, 3*, 2486. doi:10.1038/srep02486
- Aron, E. N., & Aron, A. (1997). Sensory-processing sensitivity and its relation to introversion and
  emotionality. *Journal of Personality and Social Psychology, 73*(2), 345–368. doi:10.1037/0022-3514.73.2.345
