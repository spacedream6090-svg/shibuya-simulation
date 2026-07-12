# 欲求・価値の理論調査 — 開放型行動選択の学術的土台

> 依頼(2026-07-10): エージェントの行動を「列挙」でなく**開放型**にする(物理・現実を超えること以外は何でも
> でき、テレビを見る・創作する等の娯楽/消費を含め、行動選択を LLM 自身に委ねる)ための土台として、
> 「人が行動を選ぶ欲求・価値の分類・設計」を文献で固める。ユーザー仮説=**価値の3分類(実用的/感情的/社会的)**
> (佐藤航陽『世界2.0』由来。[sekai2.0-framework.md](../sekai2.0-framework.md) の「振る舞いを hardcode しない・
> affordance/observable として使う」限定つき)。
>
> **本ドキュメントは読み取り調査のみ。コード・schema・config は一切変更していない。** 設計素材は推奨であり、
> 採否と数値決定は主エージェント(Fable)/ユーザーが行う。

---

## 0. 要旨(5行)

1. **既存資産で「欲求の個体差」は既に厚い**。`needs.py` は SDT/Schwartz/Reiss/Zuckerman/Aron を接地した
   **5 潜在価値次元**(stimulation/security/relatedness/competence/autonomy)を持ち、これは実は
   ユーザーの3分類を上回る解像度で、**認識的(好奇心=stimulation)の穴を既に埋めている**。
2. ユーザーの3分類(実用/感情/社会)は **Sheth-Newman-Gross 消費価値**の functional/emotional/social と
   **ほぼ同型**で、消費行動を語る上で妥当な骨格。ただし SNG は残り2つ(**epistemic=認識的/好奇心**・
   **conditional=条件的/文脈**)を持ち、Holbrook は **ethics/spirituality=倫理的/超越的**の第4軸を足す。
3. **欠けやすい軸=認識的価値(好奇心・新奇・情報欲)**。開放型で「創作する・学ぶ・探索する」を扱うなら
   3分類に加えて観測軸に立てるべき(多理論一致)。**条件的価値**は価値タイプでなく**文脈変調**として扱うのが妥当。
4. 開放行動空間の先行事例(Generative Agents/Concordia/Voyager/AI Town/Project Sid)は、**自由文行動を
   GM/環境ツリーで接地**して幻覚 affordance を抑える点が共通。本プロジェクトの verb registry+scheduler は
   その GM 層に相当し、**価値タグは接地後の observable として後付けする**のが no-fingerprint と整合。
5. 設計素材は3案(LLM 自己申告タグ / 後処理辞書分類 / 語彙辞書)を提示。**中立な自己申告 or 決定論の後処理**が
   R1(呼数不変)・決定論・no-fingerprint と両立する。「価値を感じる個体差」は可、「これを追求せよ」は不可。

---

## 1. 既存資産(本調査はこの上に積む)

### 1.1 コード実装済みの欲求機構

| モジュール | 何を実装しているか | 接地理論 | 既定 |
|---|---|---|---|
| `src/society/cognition/drive.py` | **欲求駆動発火**: 出来事→欲求ゲージ(0-1)蓄積→個人別閾値で申請→個人重みで確率発火→不発なら減衰。reason別重み(novel_place/congestion/unknown_word/addressed/dm/news/sns/company/silence/state_change)。閾値ドリフト E2(馴化/鋭敏化) | Park 2023 reflection / Fogg B=MAP / OASIS 確率活性化 | drift 既定 OFF |
| `src/society/needs.py` | **欲求プロファイルの個体差**: 5潜在価値次元→reason別**感度倍率**(何を欲し・何を不快と感じるか)。`drive.add` が `needs_mods` を reason 文字列で乗算 | SDT/Schwartz10/Reiss16/Zuckerman SS/Aron SPS | 既定 OFF |
| `src/society/inner_life.py` | **内面3機構**: ①離散感情ラベル(core affect→Ekman系)②長期目標(最優位価値次元→目標文)③趣味・関心(職業+価値次元→趣味→余暇行き先バイアス) | 神経科学(構成主義)/価値プロファイル | 既定 OFF |
| `src/society/media.py` | **娯楽メディア消費**(TV/動画/ゲーム): 年齢・職業で媒体構成・開始確率・セッション長。気分修復(grievance↓)。**非LLM・決定論** | Zillmann 気分管理/Katz 利用と満足/Putnam 時間置換/NHK生活時間 | 既定 OFF |
| `src/society/factors/registry.py` | trait/年齢/職業→**5価値次元プロファイル**生成(`needs_profile`)。価値名を知る唯一の層 | 同上 | — |

**5 潜在価値次元(`registry.NEEDS_DIMS`)**: `stimulation`(刺激・開放)/ `security`(安全・平穏)/
`relatedness`(関係・慈愛)/ `competence`(有能・達成)/ `autonomy`(自律・自己志向)。
trait(nfc/internal_locus/risk_tolerance)+年齢+職業+専用乱数から**決定論生成**。

> ★ **重要な発見**: この5次元は **ユーザーの3分類(実用/感情/社会)より解像度が高い**。
> `competence`≈実用的、`relatedness`≈社会的、`stimulation`≈感情的+**認識的(好奇心)**、`security`/`autonomy` は
> 3分類に写らない独立軸。つまり**「3分類で足りない認識的の穴」はコード側では既に埋まっている**。
> 本調査の価値は、この5次元を**消費・娯楽・創作という開放行動の"価値タグ"へ橋渡しする理論**を足す点にある。

### 1.2 文献メモ(docs/lit)で既に接地済みの理論

- [`motivation__sdt-flow-overview.md`](../lit/motivation__sdt-flow-overview.md): SDT(自律/有能/関係)+ フロー。
  ★ **報酬・動機を injection しない**規約(3欲求は充足"できる"affordance として置く)。
- [`needs__individual-differences.md`](../lit/needs__individual-differences.md): SDT/Schwartz10/Reiss16/
  Zuckerman SS/Aron SPS を接地し、reason別倍率の符号表を確定済み(本調査と最も重複が近い=**再掲しない**)。
- [`value__axiology-overview.md`](../lit/value__axiology-overview.md): 内在的/道具的価値、**価値の関係説**
  (価値は対象に内在せず、対象と評価主体の関係から創発=ラベルと同型で観測)。
- [`gamedesign__emergent-systemic-overview.md`](../lit/gamedesign__emergent-systemic-overview.md): MDA。
  **Mechanics(affordance)だけ設計し Dynamics は創発**=no-fingerprint の工学版。
- [`media__entertainment-effects.md`](../lit/media__entertainment-effects.md): 娯楽の利用と満足・気分管理・
  時間置換・NHK生活時間(TV視聴の年齢差)。
- [`agent-freedom-audit.md`](./agent-freedom-audit.md) / [`agent-freedom-plan.md`](../plans/agent-freedom-plan.md):
  **行動的自由度の棚卸し**と拡張計画。開放行動空間の先行事例(Generative Agents/Project Sid/Voyager/OASIS)も
  §5 で既述(本調査 §5 はこれを**補完**し、Concordia/AI Town の"自由文接地"を掘り下げる)。

**結論**: 「欲求の個体差」と「先行事例の棚卸し」は既に厚い。**本調査が新たに足すのは、①欲求分類の全体地図
(Maslow/ERG/Max-Neef の位置づけ)②消費・娯楽の"価値"理論(SNG/Holbrook/hedonic-utilitarian/warm-glow/
経験財)③3分類の写像表と欠落軸の同定④開放行動を"価値タグ付き"で受ける設計素材**。

---

## 2. 欲求・動機理論(全体地図)

### 2.1 欲求分類(何を人は欲するか)

| 理論 | 分類 | 構造 | 実証・批判 | 本プロジェクトでの位置 |
|---|---|---|---|---|
| **Maslow 欲求階層**(1943) | 生理→安全→所属・愛→承認→自己実現 | **階層(下位充足で上位が活性)** | ⚠️ **実証が弱い**。Wahba & Bridwell(1976)のレビューは、10因子分析・3ランキング・縦断研究を精査し、**厳格な階層順序をほぼ支持しない**(縦断研究は充足→活性命題を支持せず、自己実現以外で剥奪→優位命題の明確な証拠なし)。「証明されたからでなく直感的だから普及した」 | **順序を焼き込まない**。分類語彙としてのみ参照。既存 needs.py も階層でなく**並列プロファイル**を採用済み |
| **Alderfer ERG**(1969) | 存在(E)/関係(R)/成長(G) の3群 | **非階層・同時追求可**。**frustration-regression**(上位欲求の挫折→下位への退行) | Maslow を実証的に修正。同時充足・順序の文化差を許容 | ★ **3群がユーザー3分類と部分対応**(E≈実用/生存、R≈社会、G≈自己実現)。frustration-regression は「世界改変が挫折→生活消費へ退行」等の観測仮説に使える |
| **Max-Neef 基本的人間ニーズ**(1991) | 生存/保護/愛情/理解/参加/**閑暇(idleness)**/創造/アイデンティティ/自由 の9 | **非階層**。9ニーズ×4存在様式(being/having/doing/interacting)のマトリクス。**ニーズは普遍・不変、satisfier(充足手段)が文化で変わる** | 「ニーズ vs 充足手段」の分離が要点 | ★★ **開放行動に最適合**: ニーズ(不変)=drive の reason、satisfier(可変)=**LLM が選ぶ開放行動**、と読める。「閑暇・創造」を明示的にニーズに数える点が**娯楽・創作を扱う本タスクの直接の後ろ盾** |
| **Reiss 16 基本欲求**(2004) | 力/独立/好奇心/受容/秩序/貯蔵/名誉/理想/交流/家族/地位/復讐/恋愛/食/運動/平穏 | 16の並列多面体・**強度プロファイルが個人で異なる** | 既存 needs.py の設計思想の直接の後ろ盾 | 既存接地済([[needs__individual-differences]]) |
| **SDT 基本心理欲求**(Deci&Ryan) | 自律/有能/関係 の3 | 普遍の3欲求+因果志向性/アスピレーションで個人差 | 内発的動機の中核。文化差に議論 | 既存接地済。needs.py の relatedness/competence/autonomy に直結 |

**要点**: Maslow は**分類語彙としてのみ**採る(階層の実証が弱いため順序を実装しない)。**ERG の非階層・
frustration-regression** と **Max-Neef の「ニーズ(不変)/satisfier(可変=開放行動)分離」**が、開放型行動空間の
理論的支柱として新しく効く。既存 needs.py は既に「並列プロファイル」でこの思想と整合している。

### 2.2 価値理論(何を人は価値づけるか — 消費・娯楽・向社会行動)

| 理論 | 分類 | 要点 | 本タスクへの効き |
|---|---|---|---|
| **Schwartz 基本価値**(1992: 10 / **2012 refined: 19**) | 開放性↔保守 × 自己超越↔自己高揚 の**円環連続体** | 2012 改訂で**19価値の円環連続体**へ精緻化(自己防衛↔成長、個人焦点↔社会焦点)。隣接=両立、対極=葛藤 | 価値プロファイルの個人差の骨格(既存)。**円環=価値は連続体**という思想は「価値タグを離散でなく分布で観る」示唆 |
| **Sheth-Newman-Gross 消費価値**(1991) | **機能的/社会的/感情的/認識的/条件的** の5 | 消費選択を説明する5独立価値。★ **functional/social/emotional がユーザー3分類とほぼ同型**。epistemic=好奇心・新奇・知識欲、conditional=特定状況での効用 | ★★ **本タスクの中核写像**。3分類の直接の学術的双子+欠落2軸の同定 |
| **Holbrook 消費者価値8類型**(1999) | efficiency/excellence/status/esteem/play/aesthetics/ethics/spirituality | **3二分法**(外在的↔内在的 × 能動↔反応 × 自己志向↔他者志向)で8象限。最も網羅的 | 3分類に**倫理的/超越的(ethics/spirituality)**の第4軸を追加。1消費経験が複数価値を同時に持つ=**多重タグ**の根拠 |
| **hedonic vs utilitarian 消費**(Hirschman&Holbrook1982; Batra&Ahtola1991; Voss+2003) | **快楽的 ↔ 実用的**の2次元(独立・両立可) | 態度は「役に立つ(utilitarian)」と「楽しい(hedonic)」の2軸。HED/UT尺度で測定 | ユーザーの**実用的↔感情的**軸の直接の実証的裏づけ。**2軸は独立**(1財が両方持てる) |
| **warm-glow / 不純な利他**(Andreoni 1990) | 純粋利他 vs **温情(warm-glow)** | 募金は結果への純粋利他だけでなく「与える行為自体の効用(warm-glow)」で動く=**不純な利他**が観測に整合 | ★ **募金(ユーザーの"社会的価値"例)は実は社会的+感情的の混合**。「社会的価値」を単独タグにすると warm-glow の感情成分を落とす |
| **経験財 vs 物質財**(Van Boven & Gilovich 2003) | 体験購入 vs 物質購入 | 基本ニーズ充足後は**体験の方が幸福に効く**(再解釈しやすい・アイデンティティ・**社会的つながりを育む**) | ★ **コンサートのチケット(ユーザーの"感情的価値"例)は感情的+社会的+アイデンティティの混合**。体験は感情・社会・認識が交差する |

---

## 3. 価値理論と3分類の対応表(本タスクの核)

### 3.1 写像表(各理論がユーザー3分類のどこに写るか)

凡例: ◎=中核対応 / ○=部分対応 / △=弱い/文脈依存 / ―=写らない(3分類の外)。

| 理論の要素 | 実用的(道具) | 感情的(コンサート) | 社会的(募金) | 3分類の**外**にはみ出す軸 |
|---|---|---|---|---|
| **SNG functional** | ◎ | | | |
| **SNG emotional** | | ◎ | | |
| **SNG social** | | | ◎ | |
| **SNG epistemic** | | ○(新奇の快) | | ★**認識的**(好奇心・新奇・知識欲) |
| **SNG conditional** | △ | △ | △ | **条件的**(状況変調=価値タイプでない) |
| **Holbrook efficiency/excellence** | ◎ | | | |
| **Holbrook play/aesthetics** | | ◎(hedonic) | | |
| **Holbrook status/esteem** | | | ◎ | |
| **Holbrook ethics/spirituality** | | ○ | ○ | ★**倫理的/超越的**(道徳・意味) |
| **hedonic-utilitarian: utilitarian** | ◎ | | | |
| **hedonic-utilitarian: hedonic** | | ◎ | ○ | |
| **warm-glow(Andreoni)** | | ○(与える快) | ◎ | 社会的と感情的の**混合** |
| **経験財(Van Boven)** | | ◎ | ○(つながり) | 感情×社会×アイデンティティの交差 |
| **SDT competence / relatedness / autonomy** | ◎(competence) | | ◎(relatedness) | autonomy=**自律**(3分類外) |
| **Schwartz self-enhance / hedonism / self-transcend** | ○(power/achieve) | ◎(hedonism) | ◎(benevolence/univ) | stimulation/self-direction=**認識・自律** |
| **既存 needs.py 5次元** | competence | stimulation | relatedness | ★security/autonomy/(stimulation=認識も) |

### 3.2 所見 — 3分類は妥当な骨格。ただし**認識的**を足すべき

1. **ユーザー3分類 ≈ SNG functional/emotional/social(ほぼ同型)**。消費・行動選択を語る骨格として妥当で、
   Holbrook・hedonic-utilitarian・SDT とも整合する。**土台として採用してよい**。
2. **最も強く漏れるのは「認識的価値(epistemic)」** = 好奇心・新奇・情報欲・学び。SNG epistemic、Reiss 好奇心、
   Schwartz stimulation/self-direction、Berlyne の新奇性動機、Zuckerman 経験追求が**多理論で一致**して支持する
   独立軸。**開放型で「創作する・学ぶ・探索する・未知を試す」を扱う本タスクでは、これを3分類に足すべき**
   (根拠: 娯楽・創作行動の主要な駆動が"面白いから/知りたいから"で、実用/感情/社会のどれとも異なる)。
   ★ **朗報**: 既存 needs.py の `stimulation` 次元が既にこの軸を担っている。**3分類→4分類化の追加コストは
   コード側では小さい**(観測タグに epistemic を1本足すだけ)。
3. **「条件的価値(conditional)」は価値タイプでなく文脈変調として扱う**。SNG 自身が「特定状況で立ち現れる効用」と
   定義しており、これは行動選択の**モデレータ**(天候・時間帯・混雑・所持金=既存の world 変数)であって、
   価値タグの1カテゴリに並べるべきでない。→ 既存の affordance/observable 変数で自然に表現される。
4. **3分類の各タグは"純粋"でなく混合しうる**(Holbrook「1経験が複数価値を持つ」)。
   - **募金**=社会的+**感情的(warm-glow)**(Andreoni)→ 単独"社会的"タグは感情成分を落とす。
   - **コンサートのチケット**=感情的+**社会的(共有)**+**認識的(新奇)**(Van Boven 経験財)。
   → **価値タグは排他的1択でなく多重タグ(分布)で観るべき**(§4 の設計に反映)。
5. **「倫理的/超越的(ethics/spirituality)」**(Holbrook)・**「自律(autonomy)」「安全(security)」**(SDT/Schwartz)は
   3分類でも4分類でも完全には写らない。ただしこれらは**消費価値でなく生き方の価値**で、本タスク(娯楽・消費・
   創作の開放行動)の主眼からはやや外れる。**当面は observable の"その他"に束ね、必要になれば足す**判断が妥当
   (既存 needs.py が autonomy/security を別次元で保持しているので、拡張余地は既にある)。

**推奨する観測タグ集合**: `utility`(実用/機能) / `emotion`(感情/快楽) / `social`(社会/つながり/承認) /
**`epistemic`**(認識/好奇心/新奇)+ **多重付与を許す**。`conditional` は文脈変数で表現しタグにしない。
`ethics`/`autonomy` は当面 "other" に束ねる(将来拡張可)。

---

## 4. 生活行動の実態分布(現実の人間が自由時間に何をするか)

「開放型で LLM に委ねたとき、現実の人間の行動分布に近いか」を検証する参照軸。日本の公的生活時間統計が最適。

### 4.1 総務省統計局 社会生活基本調査(令和3年=2021)の行動分類

1日の行動を**20種類**に分類し、3つの活動群に束ねる。開放型行動空間の「メニューの網羅性」の外部基準になる。

| 活動群 | 内容 | 本シムの現状 |
|---|---|---|
| **1次活動** | 睡眠・食事など生理的に必要 | ルール強制(bedtime/meal window) |
| **2次活動** | 仕事・家事・通勤・育児・買い物など義務性の強い活動 | ルール強制(work window/routine) |
| **3次活動(自由時間)** | 上記以外=各人が自由に使える時間の活動 ↓ | ← **開放型行動が主に効く領域** |

**3次活動の内訳(自由時間に人が実際にすること)**:
テレビ・ラジオ・新聞・雑誌 / **休養・くつろぎ** / 学習・自己啓発・訓練(学業外) / **趣味・娯楽** /
スポーツ / ボランティア活動・社会参加 / **交際・付き合い** / 受診・療養 / その他。
公的分類では **在宅型余暇**(テレビ等+休養・くつろぎ)と **積極的余暇**(学習/趣味・娯楽/スポーツ/社会的活動)に大別。

**アンカー数値**(令和3年 社会生活基本調査 / NHK 2020 国民生活時間調査):
- テレビ・ラジオ・新聞・雑誌: 全体平均 **約2時間8分/日**(2016年比 −7分、長期減少)。
- **休養・くつろぎ**: 2016年比 **+20分**(最も増加した項目)。
- テレビ(NHK 2020): 平日視聴 **約3時間01分**、毎日視聴する人の割合が**8割を下回る**(若年で急減、
  16-19歳は約47%)。若年=動画・ゲーム、高齢=TV(既存 media.py の媒体構成比の根拠)。
- 趣味・娯楽の内訳では「スマホ/家庭用ゲーム機のゲーム」「スマホ等での音楽鑑賞」の行動者率が上昇、
  「カラオケ」「遊園地・動植物園等の見物」は大幅低下(コロナ影響含む)。

### 4.2 3次活動 → 3(+1)価値タグの対応(実態分布の検証枠)

| 3次活動カテゴリ | 主な価値タグ(多重) | 3分類での位置 |
|---|---|---|
| 休養・くつろぎ | emotion(回復・relaxation) | 感情的 |
| テレビ・動画 | emotion(気晴らし)+ epistemic(情報) | 感情+認識 |
| ゲーム | emotion(flow)+ epistemic(習熟) | 感情+認識 |
| 趣味・娯楽・創作 | epistemic(好奇心)+ emotion(楽しさ) | **認識**+感情 |
| 学習・自己啓発 | epistemic + utility(技能→wage) | **認識**+実用 |
| スポーツ | emotion + utility(健康)+ social | 感情+実用+社会 |
| 交際・付き合い | social + emotion | 社会+感情 |
| ボランティア・社会参加 | social + emotion(**warm-glow**) | 社会+感情 |
| 受診・療養・買い物 | utility | 実用 |

→ **実態分布上、感情的・認識的・社会的が優勢で、純粋な"実用的"自由時間は少ない**。開放型 LLM 行動が
現実分布に近いかは、この 3次活動カテゴリ別の**時間配分/行動者率**を observer で集計して照合すればよい
(既存の media.py が TV/動画/ゲーム、schedule.py が routine を既に記録しているので接続点はある)。

> ⚠️ **数値較正の注意**: 上の分/割合は検索で得た概数であり、k* 実験の較正に使うなら
> [`rights-institutions-gap.md`](./rights-institutions-gap.md) §3 と同様、立案前に一次表
> (stat.go.jp 統計表 / NHK 放送文化研究所)での確認を推奨。

---

## 5. 開放的行動空間の先行事例(自由文行動をどう受けるか)

> [`agent-freedom-audit.md`](./agent-freedom-audit.md) §5 が Generative Agents/Project Sid/Voyager/OASIS を
> 既に棚卸し済み。**本節はそれを前提に、(a)自由文行動の受け方 (b)物理接地・効果の決め方 (c)失敗モードと対策**の
> 3観点で**補完**する(特に Concordia の GM 裁定・AI Town の運用を追加)。

| 事例 | (a) 自由文行動の受け方 | (b) 物理接地・効果の決め方 | (c) 失敗モードと対策 |
|---|---|---|---|
| **Generative Agents**(Park 2023, arXiv:2304.03442) | 自然文の行動記述("making breakfast")を生成 | **環境ツリー(area→object の木)へ接地**。行動を木の葉ノードへ写像し、状態(stove: idle→on)を書換。移動は木の探索 | 幻覚 affordance=木に無い物体を使おうとする→**木にある物体だけに接地(制約デコード的)**。長期一貫性は memory+reflection で担保 |
| **Concordia**(DeepMind 2023, arXiv:2312.03664) | **完全自由文の行動を Game Master(GM)が裁定** | ★ **GM が grounded world state(money/votes/資源在庫)を維持・検証し、不正行動を却下**。observation を各 agent へ配信。認知は March&Olsen「状況/自分は何者か/どう振る舞うか」=**非最大化**(reward 最大化でない) | GM 裁定はスケール非対応(O(N×T×C) LLM 呼)。grounded 変数は反応的で創発でない。stereotype/個体 fidelity を著者が明記 |
| **Voyager**(Wang 2023, arXiv:2305.16291) | コード(スキル)を自由生成 | Minecraft API で実行、環境フィードバックで**自己検証ループ**。成功スキルを**スキルライブラリに蓄積→再利用** | 幻覚 API→実行エラーを feedback に返して自己修正。★ **行動空間が開いていること自体が探索の駆動源**(63新規アイテム発見) |
| **AI Town**(a16z/convex 2023) | 会話中心の自由文 | 決定論エンジン+固定マップの座標接地。会話を非同期で解決 | 運用の軽量化が主眼で world-grounding は薄い(移動・会話中心)。破綻は少ないが行動空間が狭い |
| **Project Sid / PIANO**(Altera 2024, arXiv:2411.00114) | social goal を5-10秒毎に再生成、10並行モジュール | Minecraft に接地、role/経済/文化が創発 | 並行モジュール間の一貫性=**認知コントローラで調停**。★ 職業分化は**agent自身の職業選択・目標再生成から創発** |

**共通の教訓(本プロジェクトへの含意)**:
1. **自由文行動は"生成"と"接地(裁定)"を分離する**。生成は LLM、接地は決定論エンジン(GM/環境ツリー/API)。
   → 本シムの **`actions/registry.py`(verb 定義)+ `engine/scheduler.py`(実行・却下)が GM 層に相当**。
   開放化は「verb を増やす」でなく「**LLM の自由文を既存 verb+world 変数へ写す parse+裁定層**」を厚くすること。
2. **幻覚 affordance の抑制 = "存在する物/金/許可だけに接地"**。Concordia の grounded 変数却下、GA の環境ツリー、
   既存 `deliberate._equip_section` の「所持金30000円以上」客観条件は**同じ思想**。開放化しても
   **物理・所持・許可の客観ゲートは維持**する(=物理法則を超えない、というユーザー要件そのもの)。
3. **価値タグは接地の"後"に付ける observable**。Concordia の非最大化(reward を最大化させない)は
   本プロジェクトの no-fingerprint と親和的。価値を"報酬関数"にして最大化させると設計者の指紋になる
   → **価値は行動が起きた後に分類して観る**([[value__axiology-overview]] の関係説=価値は事後に創発)。

---

## 6. 設計素材(推奨・決定は Fable/ユーザー)

> R1(呼数不変)・決定論(新 stream のみ)・no-fingerprint(価値を"感じる"個体差は可、"追求せよ"は不可)との
> 適合を各案で明記。**既定 OFF ノブ**として入れる前提([`agent-freedom-plan.md`](../plans/agent-freedom-plan.md) と歩調)。

### 6.1 開放行動の「価値タグづけ」— 3案

| 案 | 方式 | R1(呼数) | 決定論 | no-fingerprint | 評価 |
|---|---|---|---|---|---|
| **A. LLM 自己申告タグ** | 発火応答 JSON に**中立な**フィールド `value?: [utility/emotion/social/epistemic]`(多重可)を1つ足す。同じ1呼の中 | ◎ **呼数不変**(既存1呼にキー追加) | ◎(生成物の一部) | △ **要注意**: タグ選択肢を見せること自体が価値を意識させる誘導になりうる。**中立列挙+「観測のみ・行動を促さない」**を厳守すれば可 | ★推奨候補。coin_label と同じ「メニューに置くだけ・促進しない」流儀 |
| **B. 後処理 分類(observer)** | 行動テキストを事後に分類。LLM judge だと**呼数増=R1違反**。cheap-tier(語彙/埋め込み)なら非LLM | LLM判定は✗ / 非LLMは◎ | 非LLMなら◎ | ◎ 行動後の観測=指紋なし | 非LLM後処理に限れば安全。精度は粗い |
| **C. 語彙辞書(決定論)** | 行動語→価値タグの決定論辞書(既存 `inner_life._HOBBY_CAT`/`media` 媒体と同型) | ◎ 非LLM | ◎ | ◎ | 最も安全・最も粗い。ベースラインに最適 |

**推奨**: **C(語彙辞書)を既定の observable 基盤**にし(呼数ゼロ・決定論・指紋なし)、
**A(中立自己申告)を任意 ON ノブ**として重ねる(自己申告の分布 vs 辞書分類の分布のズレ自体が観測対象になる)。
**B の LLM judge は R1 を壊すので採らない**(cheap-tier 後処理なら可)。いずれも**タグは decision に戻さない**
(価値を発火判断や行動選択の入力にしない=関係説どおり事後観測)。

### 6.2 欲求状態の力学(充足・飽和・減衰)

既存 `drive.py` は**単一の欲求ゲージ**(充足=fire_reset で減衰、飽和相当=閾値ドリフト馴化、自然減衰=decay)を
既に持つ。開放型で「価値ごとの満たされ度」を扱うなら、**単一ゲージを価値タグ別のベクトルに拡張**する案:

- **満足ゲージ**を価値タグ別に持つ(例 `sat[emotion]`, `sat[social]`, `sat[epistemic]`, `sat[utility]`)。
  - **減衰(需要の再蓄積)**: 毎 step わずかに低下(=その価値が久しく満たされないと欲しくなる)。Max-Neef の
    「ニーズは不変」に対応。
  - **飽和(satiation)**: その価値タグの行動を取ると当該ゲージが上昇し、**限界効用逓減**(同じ娯楽の反復で
    効きが鈍る=media.py の Vuorre「効果は最初の15分で飽和」と同じ思想)。
  - **frustration-regression(ERG)**: 高次価値(epistemic/social)の充足が長く阻害されると、低次(utility/emotion)へ
    需要が退行=Alderfer の直接実装。**観測仮説**として面白い(世界改変=高次挑戦の挫折→生活消費への退行)。
- **R1/決定論の担保**: この力学は**非LLM・決定論**(drive の step_tick と同居)。乱数が要るなら新 stream のみ。
  ★ **no-fingerprint の分岐点**: 満足ゲージを**発火判断や行動選択に食わせると「この価値を追求せよ」になる=指紋**。
  → **当面は observable 専用**(価値ごとの飢餓/充足の分布を観るだけ)に留め、行動へ戻すかは別途ユーザー判断。
  既存 `needs.py` が「価値を**感じる**感度倍率」までは許容していることと整合(感度=可、目標注入=不可)。

### 6.3 個体差(traits → 価値プロファイル写像)

**既に実装済み**(`factors/registry.needs_profile`: trait/年齢/職業→5価値次元)。開放型の価値タグへ橋渡しするなら:

- **5次元→4タグの写像を足すだけ**(価値名を知る層=factors/inner_life に閉じる=CHECKED_DIRS 外の規約を維持):
  `utility`←competence、`emotion`←stimulation×0.5+security、`social`←relatedness、`epistemic`←stimulation×0.5+competence。
  → 個体ごとに「どの価値の行動を取りやすいか」の**素質分布**が決まる(=誰がライブに行き誰が募金するかの個体差)。
- **R1 死守**: プロファイルは trait/年齢/職業+専用乱数のみ由来(belief/k を参照しない)→ k を変えても同一
  =発火回数の k 間監査(±20%)を壊さない(needs.py の R1 規約をそのまま踏襲)。
- **no-fingerprint**: 個体に「あなたは感情型だ/社会貢献せよ」と**言わない**。プロファイルは**倍率(感度)**に留め、
  プロンプトには価値名を出さない(inner_life が趣味・目標を"文脈"として出す現行方式と同じ)。

### 6.4 開放化の最小接続(娯楽・消費・創作を LLM 選択に開く道筋)

現状「テレビを見る/創作する/買う」は media.py(非LLM 確率)や routine(ルール)に閉じ、**LLM が選べない**
([`agent-freedom-audit.md`](./agent-freedom-audit.md) §3)。開放化の最小 seam(freedom-plan と接続):

1. 発火プロンプトの行動メニューに**自由時間アクション**を中立列挙で追加(`move_to`/`buy`/`leisure`(娯楽選択)/
   `create`(創作)等)。← freedom-plan P1#3(move_to)・P2#7(buy)に既に計画あり。
2. LLM の自由文を **verb registry+world 変数へ parse+裁定**(Concordia GM 思想)。物理・所持金・許可・時間窓の
   **客観ゲートは維持**(=物理法則を超えない)。
3. 起きた行動を **§6.1 の語彙辞書で価値タグ付け**して L2 記録。→ **自由度行使率**(freedom-plan §観測指標)に
   加え「**価値タグ別の行動分布**」を観測=§4 の現実分布と照合可能に。
4. **動機は注入しない**。「2,654回提示で行使0回」([`world-change-motivation.md`](./world-change-motivation.md))の
   教訓どおり、行動空間を広げるだけでは行使されない。接続は**発火 reason と行動タグの意味的対応**で作る
   (例: novel_place 発火→epistemic 行動が選ばれやすい"文脈"、を強制でなく提示で)。

---

## 7. 出典

**欲求分類**
- Maslow, A. H. (1943). A theory of human motivation. *Psychological Review, 50*(4), 370–396. doi:10.1037/h0054346
- Wahba, M. A., & Bridwell, L. G. (1976). Maslow reconsidered: A review of research on the need hierarchy theory.
  *Organizational Behavior and Human Performance, 15*(2), 212–240. doi:10.1016/0030-5073(76)90038-6(**厳格な階層を実証的にほぼ支持せず**)
- Alderfer, C. P. (1969). An empirical test of a new theory of human need. *Organizational Behavior and Human
  Performance, 4*(2), 142–175. doi:10.1016/0030-5073(69)90004-X(ERG・frustration-regression)
- Max-Neef, M. A. (1991). *Human Scale Development: Conception, Application and Further Reflections.* Apex Press.
  (9基本的人間ニーズ×4存在様式、ニーズ/satisfier 分離)
- Reiss, S. (2004). Multifaceted nature of intrinsic motivation: The theory of 16 basic desires. *Review of
  General Psychology, 8*(3), 179–193. doi:10.1037/1089-2680.8.3.179(既存 needs メモに接地済)
- Ryan, R. M., & Deci, E. L. (2000). Self-determination theory. *American Psychologist, 55*(1), 68–78.
  doi:10.1037/0003-066X.55.1.68(既存接地済)

**価値理論(消費・娯楽・向社会)**
- Schwartz, S. H. (1992). Universals in the content and structure of values. *Advances in Experimental Social
  Psychology, 25*, 1–65. doi:10.1016/S0065-2601(08)60281-6 (10価値、既存接地済)
- Schwartz, S. H., Cieciuch, J., Vecchione, M., et al. (2012). Refining the theory of basic individual values.
  *Journal of Personality and Social Psychology, 103*(4), 663–688. doi:10.1037/a0029393(**19価値の円環連続体**)
- Sheth, J. N., Newman, B. I., & Gross, B. L. (1991). Why we buy what we buy: A theory of consumption values.
  *Journal of Business Research, 22*(2), 159–170. doi:10.1016/0148-2963(91)90050-8
  (**機能的/社会的/感情的/認識的/条件的** — ユーザー3分類の直接の学術的双子)
- Holbrook, M. B. (Ed.) (1999). *Consumer Value: A Framework for Analysis and Research.* Routledge.
  (8類型: efficiency/excellence/status/esteem/play/aesthetics/ethics/spirituality を3二分法で)
- Hirschman, E. C., & Holbrook, M. B. (1982). Hedonic consumption: Emerging concepts, methods and propositions.
  *Journal of Marketing, 46*(3), 92–101. doi:10.1177/002224298204600314
- Batra, R., & Ahtola, O. T. (1991). Measuring the hedonic and utilitarian sources of consumer attitudes.
  *Marketing Letters, 2*(2), 159–170. doi:10.1007/BF00436035
- Voss, K. E., Spangenberg, E. R., & Grohmann, B. (2003). Measuring the hedonic and utilitarian dimensions of
  consumer attitude. *Journal of Marketing Research, 40*(3), 310–320. doi:10.1509/jmkr.40.3.310.19238(HED/UT尺度)
- Andreoni, J. (1990). Impure altruism and donations to public goods: A theory of warm-glow giving.
  *The Economic Journal, 100*(401), 464–477. doi:10.2307/2234133(**募金=社会的+感情的(温情)の混合**)
- Van Boven, L., & Gilovich, T. (2003). To do or to have? That is the question. *Journal of Personality and
  Social Psychology, 85*(6), 1193–1202. doi:10.1037/0022-3514.85.6.1193(**経験財 > 物質財**、体験は社会・感情交差)

**生活行動の実態分布**
- 総務省統計局『令和3年社会生活基本調査 — 生活時間及び生活行動に関する結果』(2021)。
  https://www.stat.go.jp/data/shakai/2021/kekka.html (1次/2次/3次活動、3次=20行動分類)
- NHK放送文化研究所『2020年 国民生活時間調査』。https://www.nhk.or.jp/bunken/research/yoron/
  (TV平日視聴 約3時間、毎日視聴8割割れ、若年でネット>TV)
- 渡辺洋子「新しい生活の兆しとテレビ視聴の今」『放送研究と調査』71(8). doi:10.24634/bunken.71.8_2

**開放行動空間の先行事例**
- Park, J. S., et al. (2023). Generative agents: Interactive simulacra of human behavior. arXiv:2304.03442
  (環境ツリー接地・memory/reflection/planning)
- Vezhnevets, A. S., et al. (2023). Generative agent-based modeling with actions grounded in physical, social,
  or digital space using Concordia. arXiv:2312.03664(**GM が自由文を裁定・grounded 変数で却下**)
- Wang, G., et al. (2023). Voyager: An open-ended embodied agent with large language models. arXiv:2305.16291
  (スキルライブラリの成長・自己検証)
- AL, et al. (2024). Project Sid: Many-agent simulations toward AI civilization (PIANO). arXiv:2411.00114
  (職業分化が agent 自身の選択から創発)
- Yang, Z., et al. (2024). OASIS: Open agent social interaction simulations. (SNS特化21行動)
- a16z/Convex (2023). AI Town. https://github.com/a16z-infra/ai-town(会話中心の軽量運用)

**プロジェクト内 関連ドキュメント(重複回避の参照元)**
- [`docs/lit/needs__individual-differences.md`](../lit/needs__individual-differences.md)(SDT/Schwartz/Reiss/
  Zuckerman/Aron の個体差=本調査と最重複、再掲せず)
- [`docs/lit/value__axiology-overview.md`](../lit/value__axiology-overview.md)(内在/道具的・価値の関係説)
- [`docs/lit/motivation__sdt-flow-overview.md`](../lit/motivation__sdt-flow-overview.md)(SDT・動機を注入しない規約)
- [`docs/lit/media__entertainment-effects.md`](../lit/media__entertainment-effects.md)(娯楽の利用と満足・生活時間)
- [`docs/research/agent-freedom-audit.md`](./agent-freedom-audit.md) / [`docs/plans/agent-freedom-plan.md`](../plans/agent-freedom-plan.md)
  (行動的自由度の棚卸し・拡張計画=本調査 §5/§6 の接続先)
- [`docs/sekai2.0-framework.md`](../sekai2.0-framework.md)(価値の3分類の出所・affordance/observable 限定)

> **注**: 一部の生活時間の分/割合は検索由来の概数。k* 実験の較正に用いる数値は、立案前に一次表
> (stat.go.jp 統計表・NHK 放送文化研究所)で確認すること(捏造回避=rights-gap §3 と同方針)。
