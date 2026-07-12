# 自己認識の更新とアイデンティティ形成 — 無意識的過程 vs 意識的・物語的過程(調査、2026-07-08)

> 依頼: シミュのエージェントは「深い内省」で自己像(自分がどんな人間か・大事な関係)を更新している。
> ユーザー仮説 = **自己認識の改善は人が無意識的に行う背景過程**であり、外的要因で誘発される意識的な深い内省
> とは厳密には別物 → 自己認識の更新は「裏で回るシステム」、深い内省は「閾値を超えたとき意識的にする行為」
> として**二層に分けて設計すべき**では、という提案。この二層説が文献的に支持されるかを判定する。
> **本バッチは調査のみ・コード変更なし**(本ファイル1つだけ作成)。

---

## §1. ユーザー二層説の判定 — **条件付き支持(strong but coupled)**

**結論: 支持(ただし「完全分離した2モジュール」ではなく「相互作用する2つの端(連続体の両極)」として設計するのが正しい)。**

心理学には「自己知識には自動的・暗黙的な経路と、統制的・顕在的な経路がある」という**二重過程(dual-process)の合意**があり
(Evans & Stanovich 2013)、これはユーザーの二層説の骨格をそのまま裏づける。具体的な対応は次の通り。

| ユーザーの層 | 対応する確立した機構 | 性質 |
|---|---|---|
| **裏で回る無意識層**(漸進的な自己知識更新) | 自己知覚(Bem)/暗黙的自己(Greenwald & Banaji)/ working self-concept の文脈活性化(Markus & Wurf)/反射的評価・looking-glass(Cooley)/予測誤差による自己評価更新(計算論) | 自動・内省を要さない・漸進的・文脈依存 |
| **意識的層**(強い出来事に誘発される深い内省) | 物語的アイデンティティと autobiographical reasoning(McAdams / Habermas & Bluck)/ 自己定義記憶と転機の意味づけ(Singer) | 努力を要する・言語的/物語的・出来事に誘発される・統合的 |

**「支持」と言える根拠(3点)**
1. **経路の解離が実証されている**: 暗黙的自己(IAT等)と顕在的自己報告は乖離しうる(Greenwald & Banaji 1995)。
   自己知識は「内省でアクセスできる部分」と「できないが行動を左右する部分」に分かれる、という主張そのもの。
2. **内省なしの自己更新経路が理論化されている**: Bem の自己知覚は「内的手掛かりが弱い/曖昧なとき、人は自分の行動と
   状況を外部観察者のように見て自己を推論する」= 内省を経ない自己知識更新。ユーザーの「裏で回る」層に直接対応。
3. **意識的層は"強い出来事"に誘発されるという実証がある**: 物語研究では high/low-point(感情的に強い・秩序を乱す
   エピソード)が優先的に意味づけ(autobiographical reasoning)を誘発する。「閾値を超えたとき意識的に行う」という
   トリガー観に整合。閾値の駆動量としては自己不一致(Higgins)や社会的予測誤差(計算論)の**大きさ**が理論的裏づけ。

**「条件付き」= 単純二分にしない理由(3点)**
1. **境界は硬くない**: autobiographical reasoning は「努力を要する」一方、日常では「ほとんど意図的にはやっていない」
   =自発的にも起こる(McLean & Fournier 2007 / McLean & Mansfield 2011)。意識層は"外的誘発時のみ"に限定されない。
2. **両層は双方向に結合する**: 無意識層の産物(観察された行動・反射的評価)は意識的内省の**材料**になり、逆に意識的
   内省の結論(自己定義スクリプト)は以後の自動処理を**フィルタ**する(Singer:narrative scripts が認知-感情処理を濾過)。
   Breakwell の同化-調節+評価も、内容の取り込み(漸進的でありうる)と価値づけ(より評価的・意識的)の両方にまたがる。
3. **層の使い方に個人差がある**: Berzonsky の情報型/規範型/拡散回避型、Campbell の自己概念明確性は「どちらの層を
   どれだけ使うか」の安定した個人差。二層は"全員一律"ではなくパラメータ化すべき。

→ **設計判定**: 二層に分ける方針は文献的に妥当。ただし (i) 密閉した2箱ではなく**共有状態を更新する2経路**とし、
(ii) 意識層のトリガーは「自己不一致/予測誤差の大きさ」で駆動し、(iii) 無意識層→意識層(材料供給)と
意識層→無意識層(以後の解釈バイアス)の**双方向結合**を明示的に設計する。詳細は §3。

---

## §2. 柱ごとの要旨(出典 URL つき)

### 2.1 動的自己概念 — working self-concept(Markus & Wurf 1987)
- **出典**: Markus, H., & Wurf, E. (1987). The dynamic self-concept: A social psychological perspective. *Annual Review of Psychology, 38*, 299–337. <https://www.annualreviews.org/doi/10.1146/annurev.ps.38.020187.001503>
- **要旨**: 自己概念は静的な貯蔵庫ではなく**動的**。全体の自己知識のうち、いま文脈で想起される部分集合を
  **working self-concept**(作動自己概念)と呼び、これが思考・感情・行動を規定する。自己スキーマは高いアクセス
  可能性を持ち、入力刺激は活性化中の自己スキーマを背景に解釈・記憶・評価される。
- **二層説への含意**: 「文脈に応じてどの部分自己が前景化するか」は**自動的・連続的な背景過程**。可変(working)と
  安定(全体構造)の二重性そのものが、揮発的な「最近の自分」層と安定した「核」層の分離を裏づける。

### 2.2 自己知覚理論(Bem 1972)— 内省なしの自己更新
- **出典**: Bem, D. J. (1972). Self-perception theory. *Advances in Experimental Social Psychology, 6*, 1–62. <https://doi.org/10.1016/S0065-2601(08)60024-6>(概説: <https://learning-theories.com/self-perception-theory-bem.html>)
- **要旨**: 人は自分の態度・感情・内的状態を、**自分の外的行動とその状況を観察して部分的に推論する**。内的手掛かり
  が弱い/曖昧/解釈困難なとき、本人は外部観察者と同じ立場に置かれ、同じ外的手掛かりに頼って自己を推し量る。
  態度は行為の後づけの意味づけ道具でありうる。
- **二層説への含意**: 「行動の観察から自己を推論する」= **内省を経ない自己知識更新経路**。ユーザーの「裏で回る」層の
  中核的な理論的根拠。§3(a) の"行動カウントから最近の自分を組み立てる"を直接支持する。

### 2.3 物語的アイデンティティと autobiographical reasoning(McAdams / Habermas & Bluck / Singer)
- **出典**:
  - McAdams, D. P., & McLean, K. C. (2013). Narrative identity. *Current Directions in Psychological Science, 22*(3), 233–238. <https://journals.sagepub.com/doi/10.1177/0963721413475622>
  - Habermas, T., & Bluck, S. (2000). Getting a life: The emergence of the life story in adolescence. *Psychological Bulletin, 126*(5), 748–769. <https://doi.org/10.1037/0033-2909.126.5.748>
  - Singer, J. A., Blagov, P., Berry, M., & Oost, K. M. (2013). Self-defining memories, scripts, and the life story: Narrative identity in personality and psychotherapy. *Journal of Personality, 81*(6). <https://onlinelibrary.wiley.com/doi/abs/10.1111/jopy.12005> / <https://pubmed.ncbi.nlm.nih.gov/22925032/>
  - McLean, K. C., & Fournier, M. A. (2007). The content and processes of autobiographical reasoning in narrative identity. <https://www.sciencedirect.com/science/article/abs/pii/S009265660700089X>
- **要旨**: 人は重要な自伝的記憶を内在化・発展する**人生物語(life story)**に統合してアイデンティティを構成する
  (McAdams)。その中核操作が **autobiographical reasoning**(自伝的推論)= 出来事と自己の間に因果-動機的つながりを
  作る(「Xが起きたから私はYになった」)意味づけ過程で、青年期に発達し**努力を要する**(Habermas & Bluck)。
  **転機(turning points)**や **自己定義記憶(self-defining memories)**= 感情的・重要・人生物語に中心的な記憶が、
  この推論の焦点になり、繰り返される感情-結末系列は**物語スクリプト**へと抽象化され以後の処理を濾過する(Singer)。
- **二層説への含意**: ユーザーの「意識的・物語的な自己再構築」層に対応。**強い出来事に誘発され**、言語的・統合的・
  努力的。§3(b) を直接支持。注: 常に有益とは限らず、反芻的な過剰推論は well-being を損ないうる(下記 2.4/2.5 参照)。

### 2.4 暗黙的自己 vs 顕在的自己 — 二重過程(Greenwald & Banaji 1995 / dual-process)
- **出典**:
  - Greenwald, A. G., & Banaji, M. R. (1995). Implicit social cognition: Attitudes, self-esteem, and stereotypes. *Psychological Review, 102*(1), 4–27. <https://doi.org/10.1037/0033-295X.102.1.4>(機構レビュー: <https://pmc.ncbi.nlm.nih.gov/articles/PMC3073696/>)
  - Evans, J. St. B. T., & Stanovich, K. E. (2013). Dual-process theories of higher cognition. *Perspectives on Psychological Science, 8*(3), 223–241. <https://scottbarrykaufman.com/wp-content/uploads/2014/04/dual-process-theory-Evans_Stanovich_PoPS13.pdf>
- **要旨**: 暗黙的認知の"署名"は「過去経験の痕跡が行動に影響するが、その経験は通常の意味で想起されず自己報告や
  内省にアクセスできない」こと(Greenwald & Banaji)。暗黙的自尊心(自動的に喚起される感情的自己連合)と
  顕在的自尊心(熟慮的自己評価)は解離しうる。より一般に、認知は「速い・自動・連合的・無意識(System 1)」と
  「遅い・熟慮的・規則的・意識(System 2)」に二分される(Evans & Stanovich)。関連する自己の哲学的整理として、
  瞬間的・前反省的な**経験的自己(minimal self)**と時間を横断し概念を蓄積する**物語的自己(narrative self)**の区別も
  ある(<https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11521916/>)。
- **二層説への含意**: 二層説の最も直接的な一般理論的裏づけ。**自動/暗黙**の自己と**統制/顕在**の自己が別経路として
  実証的に分離することが、シミュで「裏システム」と「意識的内省」を別モジュールにする根拠になる。

### 2.5 アイデンティティ過程理論・処理スタイル・自己概念明確性(Breakwell / Berzonsky / Campbell)
- **出典**:
  - Breakwell, G. M. Identity Process Theory(同化-調節/評価の2過程 + 連続性等の原理)。概説: <http://assets.cambridge.org/97811070/22706/excerpt/9781107022706_excerpt.pdf>
  - Berzonsky, M. D. — identity processing styles(情報型/規範型/拡散回避型)。メタ分析: <https://www.sciencedirect.com/science/article/abs/pii/S0140197111001059>
  - Campbell, J. D., et al. (1996). Self-concept clarity: Measurement, personality correlates, and cultural boundaries. *Journal of Personality and Social Psychology, 70*(1), 141–156. <https://psycnet.apa.org/record/1996-01707-011>
- **要旨**:
  - **IPT(Breakwell)**: アイデンティティ構造は2つの普遍過程で調整される — **同化-調節**(新内容の吸収と既存要素の
    調整)と**評価**(内容への意味・価値の付与)。原理(連続性・独自性・自尊・自己効力等)がこれを方向づける。
  - **処理スタイル(Berzonsky)**: **情報型**=自己関連情報を熟慮的に探索・評価(§3(b)の意識層を多用)、**規範型**=
    重要他者の価値を**自動的に**内面化、**拡散回避型**=先延ばし・状況依存で回避(well-being と負相関)。
  - **自己概念明確性(Campbell)**: 自己信念が安定・明確・確信を持って定義されている程度(12項目尺度)。低い明確性は
    高神経症傾向・低自尊・**反芻的自己注目**と関連。日本人サンプルは明確性が低く、自尊との相関も弱いという文化差あり。
- **二層説への含意**: **どちらの層をどれだけ使うか**は安定した個人差(処理スタイル)。**明確性**は核自己の安定度の指標で、
  「安定した核」と「揺らぐ作動自己」を分ける設計の根拠。IPT の「内容取り込み(漸進的)」と「評価(意識的)」の
  分業は、無意識層(内容集計)と意識層(価値づけ)の役割分担にそのまま写像できる。

### 2.6 自己概念更新のタイミング — 自己不一致・予測誤差・反射的評価(Higgins / Cooley / 計算論)
- **出典**:
  - Higgins, E. T. (1987). Self-discrepancy: A theory relating self and affect. *Psychological Review, 94*(3), 319–340. <https://persweb.wabash.edu/facstaff/hortonr/articles%20for%20class/Higgins.pdf>
  - Cooley, C. H. (1902). looking-glass self / reflected appraisal。整理: <https://en.wikipedia.org/wiki/Reflected_appraisal> ・ <https://psychology.iresearchnet.com/social-psychology/self/looking-glass-self/>
  - 計算論: Will, G.-J., et al. (2017). Neural and computational processes underlying dynamic changes in self-esteem. <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5655144/> / 低自尊の社会学習 <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7078312/>
- **要旨**:
  - **自己不一致(Higgins)**: 自己は actual / ideal / ought の3領域 × own / other の2視点。**gap の大きさとアクセス
    可能性**が不快と特定の感情族(理想不一致→落胆系、義務不一致→焦燥系)を予測し、これが自己概念変化を動機づける。
  - **反射的評価/looking-glass(Cooley)**: 自己像は「他者が自分をどう見ているかの**知覚**」に影響される(漸進的更新)。
    **重要な但し書き**: メタ知覚の正確性は低く、「他者が実際にどう見るか」より「自分がどう見ているか」に近い
    (looking-glass は逆向きかもしれない)。社会的フィードバックは"生の他者評価"ではなく"知覚された評価"経由で効く。
  - **予測誤差/ベイズ(計算論)**: 自尊心は「期待した社会的フィードバックと受け取ったフィードバックの差=社会的
    予測誤差」で逐次更新される。低自尊者は「嫌われる」期待が持続し予測誤差で更新しにくい(自己確証スパイラル)。
- **二層説への含意**: **無意識層の更新は"誤差駆動"で漸進的**(予測誤差/反射的評価)。**意識層のトリガーは"誤差/不一致の
  大きさが閾値超え"**という定式化が可能。§3(c) の層間結合(無意識層が誤差を計算 → それが意識層を発火させる)の理論基盤。

---

## §3. シミュ実装への示唆

前提: 既存のシミュには出来事ゲージ `drive` が個人別 `drive_threshold` を超えると「深い内省」を発火する機構がある
(参照: [reflection-drift.md](./reflection-drift.md) / [../lit/cognition__drive-firing-memory.md](../lit/cognition__drive-firing-memory.md))。
以下はこれを二層に整理する提案の**文献整合性の判定**であり、実装は次バッチ・設計のみ。

### (a) 裏で回る無意識層 = 行動の客観カウントから決定論で「最近の自分」1行を組み立てる — **整合する(強く支持)**
提案: よく話した/出かけた/家にこもった/誰とよく居たか、を客観カウントし、決定論で「最近の自分」1行に要約
(Bem の自己知覚・looking-glass の近似)。

- **判定**: **文献に整合。強く支持される。**
  - Bem の自己知覚は「内的手掛かりが弱いとき、自分の行動と状況の観察から自己を推論する」= 行動カウントからの
    自己要約はこの直接的な操作化。looking-glass は「誰とよく居たか」を社会的入力として取り込む点で整合。
  - working self-concept(Markus & Wurf)とも整合 — 文脈(最近の行動履歴)で前景化する部分自己の近似。
- **設計上の精緻化(文献からの示唆)**:
  1. **生カウントより"予測誤差"を推奨**: 計算論(Will 2017)は更新が「期待との差」で駆動されることを示す。
     `最近の行動 − そのエージェントのベースライン` の**逸脱量**を主入力にすると、単なる集計より現実的で、かつ
     (c)の意識層トリガーにそのまま使える。
  2. **決定論での要約は妥当な簡約**: ただし Bem は「観察→**推論**」であり、純粋な数え上げは推論(評価)ステップを
     省いた近似である点は明記。評価・価値づけ(IPT の evaluation / Higgins の ideal・ought 照合)は本来この層と
     意識層の中間にある。まず決定論版で始め、価値づけは意識層に寄せるのが層分離として綺麗。
  3. **"誰と"は知覚された評価の近似にとどめる**: looking-glass の正確性問題(反射的評価は実際の他者評価より自己像に
     近い)を踏まえ、他者からの生の評価を直接注入せず、あくまでエージェント自身が観測した共在頻度の要約に留めるのが
     文献的に安全(過度な"他者の真意"注入は正確性の実証に反する)。
  - **これは k 非依存・決定論の"裏システム"にできる**: 入力が自分の行動カウント/共在頻度のみなら、既存の
    reflection-drift 監査の「発火数が信念条件で乖離しない(R1)」制約とも両立しやすい。

### (b) 意識的層 = 強い出来事に誘発される深い内省での自己物語の更新 — **整合する(支持)**
提案: 強い出来事に誘発される深い内省で自己物語を更新(autobiographical reasoning の近似)。

- **判定**: **文献に整合。支持される。**
  - 物語研究は high/low-point(感情的に強い・秩序を乱すエピソード)が優先的に autobiographical reasoning を誘発する
    ことを示す。「強い出来事に誘発」「閾値超えで意識的に発火」は転機・自己定義記憶の実証に合致。
  - 発火の駆動量は自己不一致(Higgins)/社会的予測誤差の**大きさ**で正当化できる(既存 `drive`→threshold 機構の
    自然な意味づけ = "誤差/不一致が閾値を超えたら意識的内省")。
- **設計上の注意(文献からの示唆)**:
  1. **過剰発火は有害**: autobiographical reasoning は常に有益ではなく、反芻的な過剰推論は well-being を損なう
     (McLean & Mansfield 2011)。低・自己概念明確性 × 反芻傾向のエージェントほど悪化しうる。発火頻度は抑制的に、
     出力は「統合的意味(私はXな人間だ/この関係が大事だ)」であって単なる反芻ループにしない。
  2. **出力は"物語/スクリプト"として蓄積**: Singer の narrative scripts のように、内省の結論を再利用可能な自己定義
     (核自己)として保存し、以後の処理をフィルタさせる(→(c)へ)。
  3. **外的誘発は簡約**: 文献上、自伝的推論は自発的にも起こる。"外的強イベント誘発のみ"は妥当な簡約だが、
     完全な排他ではない点を仕様に明記(将来、静穏期の自発内省を足す余地)。

### (c) 二層の相互作用の設計上の注意 — **双方向結合が必須(片方向では文献に反する)**
- **無意識層 → 意識層(材料供給)**: 意識的内省(autobiographical reasoning)は自伝的観察を材料に動く。よって
  (a)の「最近の自分」1行・行動カウント・**予測誤差/自己不一致量**を、意識層の内省プロンプトの入力として渡す。
  さらに**予測誤差/不一致の大きさを意識層の発火閾値の駆動変数にする**(Higgins/計算論):`drive` に「行動の逸脱量」を
  加算する経路。これで「裏で溜まった不一致が閾値を超えたとき意識的内省が起きる」= ユーザーの直感を機構化できる。
- **意識層 → 無意識層(以後のバイアス)**: 意識的内省の結論(自己定義スクリプト)は、以後の自動的解釈をフィルタする
  (Singer / 内面化された自己像は反射的評価の解釈を左右)。よって意識層の出力を**核自己**として保存し、(a)の
  「最近の自分」要約やベースライン期待に事前分布として反映させる。
- **状態の書き分け(交絡・二重計上の回避)**: どちらの層がどのフィールドを書くかを分離する。
  - 無意識層 → **揮発的な「作動自己/最近の自分」**(working self-concept、頻繁に上書き)。
  - 意識層 → **安定した「核自己・自己定義・大事な関係」**(narrative identity、稀に更新)。
  - 根拠: Markus & Wurf の working vs 全体構造、Campbell の自己概念明確性(安定した核の存在)。同一フィールドを両層が
    競合更新すると、どちらの過程の効果か分離できず分析が濁る。
- **暴走ループの減衰**: 意識層→無意識層→意識層の自己確証スパイラル(低自尊で予測誤差を更新しない持続的悲観、
  Will 2017)に注意。核自己が予測を強く固定しすぎると更新が止まる。事前分布の重みに上限/減衰を入れ、
  無意識層が新規の逸脱を拾える余地を残す(既存 reflection-drift の自発回復と同じ発想)。
- **個人差でゲート**: 意識層への入りやすさを、Berzonsky の処理スタイル(情報型=内省多用/規範型=自動内面化/
  拡散回避型=回避)や Campbell の自己概念明確性の類似変数でゲートする。全エージェント一律にしない。既存の
  `drive_params`/`drift_params`(traits→数値写像)に同格の写像を足す形が自然(実装は別途要相談)。

---

## §4. 出典一覧(URL 検証: すべて本調査の Web 検索結果に出現したもの)

**動的自己概念**
- Markus & Wurf (1987) *Annu. Rev. Psychol.* 38:299–337 — <https://www.annualreviews.org/doi/10.1146/annurev.ps.38.020187.001503>

**自己知覚**
- Bem (1972) *Adv. Exp. Soc. Psychol.* 6:1–62 — <https://doi.org/10.1016/S0065-2601(08)60024-6>(概説 <https://learning-theories.com/self-perception-theory-bem.html>)

**物語的アイデンティティ**
- McAdams & McLean (2013) *Curr. Dir. Psychol. Sci.* 22(3):233–238 — <https://journals.sagepub.com/doi/10.1177/0963721413475622>
- Habermas & Bluck (2000) *Psychol. Bull.* 126(5):748–769 — <https://doi.org/10.1037/0033-2909.126.5.748>
- Singer, Blagov, Berry & Oost (2013) *J. Pers.* 81(6) — <https://onlinelibrary.wiley.com/doi/abs/10.1111/jopy.12005> / <https://pubmed.ncbi.nlm.nih.gov/22925032/>
- McLean & Fournier (2007) — <https://www.sciencedirect.com/science/article/abs/pii/S009265660700089X>
- McLean & Mansfield (2011) "To reason or not to reason" — <https://pubmed.ncbi.nlm.nih.gov/21387534/>

**暗黙的自己 / 二重過程**
- Greenwald & Banaji (1995) *Psychol. Rev.* 102(1):4–27 — <https://doi.org/10.1037/0033-295X.102.1.4>(レビュー <https://pmc.ncbi.nlm.nih.gov/articles/PMC3073696/>)
- Evans & Stanovich (2013) *Perspect. Psychol. Sci.* 8(3):223–241 — <https://scottbarrykaufman.com/wp-content/uploads/2014/04/dual-process-theory-Evans_Stanovich_PoPS13.pdf>
- 経験的自己 vs 物語的自己(概説) — <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11521916/>

**アイデンティティ過程 / スタイル / 明確性**
- Breakwell, Identity Process Theory(概説) — <http://assets.cambridge.org/97811070/22706/excerpt/9781107022706_excerpt.pdf>
- Berzonsky, Identity Style Inventory(メタ分析) — <https://www.sciencedirect.com/science/article/abs/pii/S0140197111001059>
- Campbell et al. (1996) *J. Pers. Soc. Psychol.* 70(1):141–156 — <https://psycnet.apa.org/record/1996-01707-011>

**更新タイミング(不一致・予測誤差・反射的評価)**
- Higgins (1987) *Psychol. Rev.* 94(3):319–340 — <https://persweb.wabash.edu/facstaff/hortonr/articles%20for%20class/Higgins.pdf>
- Cooley (1902) looking-glass / reflected appraisal(整理) — <https://en.wikipedia.org/wiki/Reflected_appraisal> ・ <https://psychology.iresearchnet.com/social-psychology/self/looking-glass-self/>
- Will et al. (2017) 自尊心の神経計算論 — <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5655144/>
- 低自尊の社会学習(計算論) — <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7078312/>

### 未確認事項(事実と推測の区別)
- 一次PDFは全件は直接取得していない。書誌情報(巻・号・頁)のうち **Habermas & Bluck 126(5):748–769 / Markus & Wurf
  38:299–337 / Bem 6:1–62 / Greenwald & Banaji 102(1):4–27** は検索結果本文で確認。**Higgins 94(3):319–340 /
  Campbell 70(1):141–156** は標準的書誌からの記載で、原著頁の再検証は未実施(**未確認**)。
- Singer et al. (2013) の頁範囲は検索で未取得のため号のみ記載(**未確認**)。
- Breakwell の4原理の完全な列挙(連続性・独自性・自尊・自己効力等)は二次資料ベース。原著での正確な原理集合と
  版による差異は**未確認**。
- §3 の「予測誤差を主入力にする」「traits→層ゲートの写像」等は文献に整合する**設計提案(推測)**であり、実証された
  数値やパラメータではない。magnitude は実装時の調律・感度分析対象。
