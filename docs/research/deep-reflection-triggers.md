# 人はいつ・なぜ深い内省をするのか — 誘因・タイミングの文献調査(2026-07-08)

> 依頼: シミュのエージェントに実装済みの「深い内省」(蓄積記憶から自己像を更新する重い内省)が、現在
> 「N日ごとの就寝前」という固定周期で現実味に欠ける、との指摘。ユーザー仮説を文献で検証する:
> **(a)** 深い内省は強烈な出来事(外的要因)に促されて起こる /
> **(b)** 閾値を超える経験はポジティブよりネガティブが多い /
> **(c)** 出来事の直後ではなく「少し間をおいて」起こる。
> 本バッチは**調査のみ・コード変更なし**。関連: [reflection-drift.md](./reflection-drift.md)(発火閾値の時間ドリフト)、
> [../lit/cognition__reflection-drift-adaptation.md](../lit/cognition__reflection-drift-adaptation.md)。

## 用語の整理(このメモでの対応づけ)
- **shallow / 浅い内省** ≈ 心理学の「侵入的反芻(intrusive rumination)」「brooding(考え込み)」= 自動的・不随意・反復的。
- **deep / 深い内省** ≈ 「熟慮的反芻(deliberate rumination)」「reflective pondering(内省的熟考)」「意味形成(meaning-making)」の
  努力的・意図的側面 = 中核信念/自己像の再構築を伴う。
- 文献の一貫した含意: **この2つは別物で、前者が後者を準備する(順序と遅延がある)**。ここが仮説(c)の核心。

---

## §1 仮説判定表

| 仮説 | 判定 | 根拠(代表文献) |
|---|---|---|
| **(a)** 深い内省は強烈な出来事(外的要因)に促される | **支持**(ただし正確には「出来事 × 自己関連性」) | 反応スタイル理論(負の気分が反芻/内省を誘発:Nolen-Hoeksema 1991 / Treynor 2003)、意味形成モデル(状況的意味と全体的意味の**不一致**が苦痛→意味形成努力を誘発:Park 2010)、PTG(中核信念を揺るがす「地震的」出来事:Tedeschi & Calhoun)、制御理論(目標との不一致・目標の中断が自己注意を起動:Carver & Scheier)。**共通項は「出来事そのものの強さ」ではなく「既存の信念・目標との乖離(=自己関連性)」**。純粋な外的強度ではない点は修正が必要。 |
| **(b)** 閾値超えの経験はポジより**ネガが多い** | **条件付き支持**(真の軸は valence でなく「乖離の大きさ・自己関連性」) | ネガティビティ優位(Baumeister 2001「Bad is stronger than good」:負の出来事は**より徹底的に処理**され痕跡が長い)、反芻研究・PTG・意味形成研究の中心が逆境である点は(b)を支持。**一方で反例が確実に存在**: 畏敬(awe)、人生の転機/ターニングポイント、達成といったポジティブな「地震的」出来事も深い内省・自己再構築を誘発する(§2-6)。→ **ネガの方が閾値を越え「やすい/頻度が高い」のは正しいが、ポジを除外するのは誤り**。設計は valence でゲートせず、負に重み付けした「乖離ゲージ」にすべき。 |
| **(c)** 直後でなく「少し間をおいて」起こる | **支持**(深い=熟慮的内省について特に強い) | PTGの中核所見: **侵入的反芻が出来事直後に先行**し、**時間をおいて熟慮的反芻へ移行**して成長に至る(Tedeschi & Calhoun; ERRI: Cann et al. 2011 は熟慮的反芻を「後の時点で起こりやすい」と明記)。睡眠・オフライン処理(REM 依存の感情記憶固定)も「就寝をまたいだ処理」を支持。**ただし「直後は無」ではなく「直後は侵入的段階」**であり、深い内省はその後に来る、という**二段構え**が正確。 |

**総括**: 3仮説とも大筋で文献に整合するが、2点の修正が要る。
1. トリガーは「出来事の強度」より **「信念・目標との乖離(自己関連性)」**(a の精緻化)。
2. 遅延は「無 → 深い内省」ではなく **「侵入的(浅い)反芻 → 遅れて熟慮的(深い)内省」の二段階**(c の精緻化)。
3. ネガ優位は頻度・処理深度としては正しいが、**ポジティブな地震的出来事(畏敬・転機・達成)を排除しない**(b の限界)。

---

## §2 柱ごとの要旨(出典 URL つき)

### 1. 反芻と内省の区別 — 何がそれを起動するか
- **反応スタイル理論(RST; Nolen-Hoeksema 1991)**: 反芻は「負の気分への受動的・反復的な応答様式」で、負の気分を長引かせ抑うつを増す。**起動因は負の気分/出来事**。
- **Treynor, Gonzalez & Nolen-Hoeksema 2003「Rumination Reconsidered」**: 反芻尺度(RRS)を因子分析し、**brooding(考え込み=不適応的)**と **reflective pondering(内省的熟考=問題解決志向・適応的)**の2成分に分離。brooding は将来の抑うつと強く結びつくが、reflective pondering は建設的解決を志向する。
  → 本プロジェクトの「浅い内省=brooding/侵入的」「深い内省=reflective pondering/熟慮的」対応の学術的裏づけ。
  → いずれも**負の感情が入口**だが、深い側は「解決・理解を志向する意図的な熟考」である点が重要。
  出典: <https://deepblue.lib.umich.edu/handle/2027.42/44342> / <https://link.springer.com/article/10.1023/A:1023910315561>
  補足(brooding/reflection の妥当性再検討): <https://pmc.ncbi.nlm.nih.gov/articles/PMC2832851/>

### 2. 意味形成(meaning-making)— 不一致が努力を誘発
- **Park 2010「Making sense of the meaning literature」(Psychological Bulletin 136(2):257-301)**。
- **全体的意味(global meaning)**: 現実・公正・統制・アイデンティティに関する深く保持された信念と目標、人生が有意味だという主観。
- **状況的意味(situational meaning)**: 個別の出来事の評価的意味。
- **中核メカニズム**: 状況的意味と全体的意味の**乖離(discrepancy)の知覚が苦痛(distress)を生み**、その苦痛が乖離を減らす**意味形成努力を動機づける**(「Perceived discrepancies … produce distress」「This violation-related distress is painful, motivating people to try to alleviate it」— Frontiers 2022 要約より)。
- **同化(assimilation)**=出来事の見方を全体的意味に合わせて修正 / **調節(accommodation)**=乖離が大きいとき全体的意味(自己像・世界観)側を書き換える。**深い内省 ≈ 調節**。
  → 仮説(a)を強く支持し、かつ**「強度」でなく「乖離」がトリガー**という精緻化を与える。
  正直な限界: Park モデル自体は「自動的 vs 熟慮的」の区別や**タイミング(即時か遅延か)を明示していない**(Frontiers 要約で確認)。遅延の根拠は下記 PTG が担う。
  出典: <https://pubmed.ncbi.nlm.nih.gov/20192563/> / 概説 <https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.844891/full>

### 3. 外傷後成長(PTG)— 侵入的反芻 →(遅延)→ 熟慮的反芻 → 自己再構築
- **Tedeschi & Calhoun のモデル**: 中核信念(core beliefs)を揺るがす**「地震的(seismic)」出来事**が起点。まず**侵入的反芻(automatic・unwanted な思考/イメージ)が直後に優勢**になり、**progressively(徐々に)熟慮的反芻(intentional・sense-making)へ移行**し、それが自己/世界観の再構築=成長に至る。
- **役割の分化**: **熟慮的反芻は PTG の直接的予測子**、**侵入的反芻は PTSD 症状**とより強く結びつく。
- **ERRI(Event Related Rumination Inventory; Cann et al. 2011)**: 侵入的10項目+熟慮的10項目。**「熟慮的反芻は…人生への含意について後の時点で起こりやすい(likely to occur at a later time)」**と時間差を明記。侵入的 α=.94、熟慮的 α=.88。
- **縦断研究**: 直近の熟慮的反芻が「(震災)直後の侵入的反芻 → PTG」を部分媒介。ただし**「何が侵入的→熟慮的の移行を引き起こすか」は実証的に未解明**(研究ギャップとして複数文献が明言)。
  → 仮説(c)の最強の根拠。**「直後=侵入的(浅い)/遅れて=熟慮的(深い)」の二段構え**を明確に示す。
  出典(オープン): US-日本比較 <https://ptgi.uncc.edu/wp-content/uploads/sites/9/2015/01/Intrusive-versus-deliberate-rumination-in-posttraumatic-growth-across-US-and-Japanese-samples.pdf> /
  中核信念×反芻 <https://ptgi.uncc.edu/wp-content/uploads/sites/9/2015/01/The-relationship-of-core-belief-challenge-rumination-disclosure-and-sociocultural-elements-to-posttraumatic-growth.pdf> /
  ERRI 概要 <https://link.springer.com/rwe/10.1007/978-3-030-77644-2_130-1> /
  Tedeschi 2023 総説(本文は有料) <https://onlinelibrary.wiley.com/doi/10.1002/wps.21093>

### 4. ネガティビティ優位・期待違反が熟考を起動
- **Baumeister, Bratslavsky, Finkenauer & Vohs 2001「Bad Is Stronger Than Good」(Review of General Psychology 5(4):323-370)**: 負の出来事は**より徹底的に処理され(processed more thoroughly)**、印象形成が速く、痕跡が長い。日常事・重大ライフイベント・対人・学習の広範で「悪い方が強い」。**自己は良い自己定義を追うより悪い自己定義を避けるよう強く動機づけられる**。
  → 仮説(b)を支持:同じ乖離でもネガの方が処理が深く、閾値を越えやすい/頻度が高い。
- **Carver & Scheier の制御理論(サイバネティック自己制御)**: 行動は目標(基準)と現状の比較で制御され、**不一致の検出が自己制御(と自己注意)を起動**。反芻の「目標進捗理論」では、**目標が達成されない=不一致が持続する**限り反復思考が続く。目標の中断・妨害が自己注目的処理を呼ぶ。
  → 「期待違反・目標不一致 → 自己注意 → 熟考」という(a)の一般機構を提供。
  出典: <https://journals.sagepub.com/doi/abs/10.1037/1089-2680.5.4.323> / <https://roybaumeister.com/2001/10/15/bad-is-stronger-than-good/> /
  Carver & Scheier <https://link.springer.com/book/10.1007/978-1-4612-5887-2>

### 5. 日常レベルの誘因 — どんな日に・いつ人は反芻/内省するか
- **日記法・経験サンプリング**: ストレスの多い日ほど**その晩(就寝時)に反芻**が増える。夜間に「その日のストレスへの反芻」を報告させる設計が標準的で、**日中ストレス × 反芻が翌朝の起床時コルチゾール上昇を予測**(Perseverative Cognition 仮説の支持)。
  → 「衝撃の強い日 → その夜に反芻」という設計仮定は日常研究と整合。
- **睡眠と感情記憶の統合(オーバーナイト処理)**: 感情記憶は**オフラインで優先的に固定**され、**REM 睡眠が感情記憶の固定に寄与**する(REM シータ活動が自律的情動反応の固定を促進)。感情情報の優位は睡眠をまたいでむしろ強まりうる。
  → 「就寝前/夜間に処理が起こる」タイミング仮定を神経科学側からも支持。ただし「感情トーンの低減 vs 保存」は研究間で結論が割れる(下記)。
  出典: 日次反芻×睡眠×コルチゾール <https://pmc.ncbi.nlm.nih.gov/articles/PMC6783329/> /
  日次 co-rumination/反芻(夜報告) <https://pmc.ncbi.nlm.nih.gov/articles/PMC11757728/> /
  Sleep and Emotional Memory Processing <https://pmc.ncbi.nlm.nih.gov/articles/PMC4182440/> /
  REM×前頭シータと感情記憶固定 <https://pmc.ncbi.nlm.nih.gov/articles/PMC2665156/>

### 6. ポジティブ誘因の反例 —(b)の限界を正直に
- **畏敬(awe)**: 自己超越的なポジティブ感情。「小さな自己(small self)」を誘発し注意を他者・全体へ向ける。**存在論的問い(人生の意味など)への内省を誘発**し、Affect-Connect-Grow モデルで**意味生成と心理的成長**をもたらす。
  出典: <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6548882/> / <https://www.tandfonline.com/doi/full/10.1080/17439760.2025.2604069>
- **人生の転機/ターニングポイント・自伝的推論(autobiographical reasoning)**: 転機(高点・低点いずれも)や**伝記的断絶(biographical disruption)は自伝的推論を促し**、自己連続性・アイデンティティの再構築を駆動する。ナラティブ・アイデンティティ論では転機が自己物語更新の起点。
  出典: 転機記憶と適応 <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7969507/> / 断絶の緩衝 <https://www.researchgate.net/publication/262562199>
  → ポジ/ネガ双方の「地震的」出来事が深い内省を起こす。**valence でなく「中核信念・自己像への衝撃の大きさ」が真の閾値変数**。

---

## §3 シミュ実装への示唆

### 現行設計案の評価
> 案: 「日内の衝撃ゲージ(ネガ重み付き)が閾値を超えた日 → その夜の内省を**深い内省に格上げ**(=数時間の遅延+睡眠前)」。

**大筋で文献と整合する。** 固定周期(N日ごと)より格段に現実味がある。具体的整合点:
- **出来事駆動 + 閾値**: RST・Park・PTG・制御理論すべてが「(乖離を含む)出来事が閾値を越えて処理を起動」を支持(§2-1〜4)。
- **ネガ重み付け**: Baumeister のネガティビティ優位が直接支持(§2-4)。
- **睡眠前/夜間・数時間の遅延**: 日記研究(夜に反芻)+ 睡眠のオフライン感情処理が支持(§2-5)。

### 修正・追加を検討すべき点(重要度順)

1. **【最重要】侵入的(浅い)段階を挟む二段構えにする。** 文献の最も強固な所見は
   「**侵入的反芻が先行 → 遅れて熟慮的反芻**」(§2-3, ERRI が明示)。現案の「衝撃→その夜に即・深い内省」は
   遅延が**一晩で短すぎる**恐れがある(PTG では移行に日〜週単位)。推奨:
   - 高衝撃イベント当日〜その夜は **「侵入的想起(浅い内省)を昂進」** させ、
   - 深い内省(自己像更新)は **1晩以上のインキュベーションを置いて発火**しうる設計に。
   - シミュの時間圧縮を踏まえれば「その夜=侵入的、翌夜以降=深い」程度の**多日遅延オプション**が文献に最も忠実。
     (最低限、現案の「その夜に深い内省」も許容範囲だが、遅延分布を1晩固定にせず幅を持たせるべき。)

2. **トリガーを「強度」でなく「乖離(自己関連性)」に寄せる。** 純粋な出来事強度でなく、
   **エージェントの既存の信念/目標との不一致の大きさ**で重み付けするのが Park/Carver-Scheier に忠実(§2-2,4)。
   → ただし本プロジェクトの **R1 制約(計算量交絡)** に注意: 深い内省の発火入力に *belief 書き戻しの成否/量*(k 依存量)を
     使うと、[reflection-drift.md](./reflection-drift.md) と同じ交絡が復活する恐れ。
     **推奨: 乖離の近似は「出来事ゲージ入力・期待違反の大きさ・|Δstate|」など drive.py が既に見る k 非依存量で構成**し、
     belief 書き戻しにはゲートしない(既存の設計規律と整合)。これは設計上の要注意点であり実装判断はユーザー確認を要する。

3. **valence ゲートにしない(ポジ転機を排除しない)。** ネガ重み付けは可(§2-4)だが、
   **畏敬・達成・人生の転機といったポジティブな地震的出来事も閾値を越えられる**ようにする(§2-6)。
   → 実装は「valence で on/off」ではなく「**|乖離| に負のとき係数 >1 を掛ける非対称重み**」。
     ポジ側もゼロにせず、十分大きければ閾値超え可能に。

4. **閾値の個人差には根拠がある。** 深い内省の起きやすさの個体差は文献的に妥当:
   - **特性反芻(trait rumination)**(Nolen-Hoeksema)= 反芻傾向の安定した個人差。
   - **出来事の中心性(centrality of event)** = 同じ出来事でも自己物語の中心度が高い人ほど反芻・PTG が強い。
   → 既存の traits→params 写像(`factors/registry`)に沿って、**深い内省の閾値/ネガ非対称係数を trait 由来**にするのは妥当
     (reflection-drift の drift_params と同格)。fingerprint 回避・分布は既存方針(TruncNorm/LogNorm σ/μ≈0.2-0.4)を踏襲。

5. **睡眠前タイミングは維持してよいが、機構的意味を持たせる。** 「夜間/就寝前」は日記・睡眠研究に整合(§2-5)。
   ただし睡眠の感情処理は「感情トーンを減衰させる」説と「保存/強化する」説が併存(§2-5 の限界)ため、
   **内省後に自己像が必ず“安定化/沈静化”すると決め打ちしない**(更新方向はニュートラルに扱い、感度分析対象に)。

### まとめ(設計骨子の推奨形)
「**日内の乖離ゲージ(ネガ非対称重み・k 非依存入力)が閾値超え → まずその夜は侵入的想起を昂進 → 1晩以上の遅延を経て
(閾値・非対称係数は trait 由来の個人差)深い内省=自己像更新を発火。ポジティブな大乖離も同経路で許容**。」
これが現案を文献に最も忠実化した形。**実装は本メモの範囲外**であり、着手前にユーザーへ設計合意を取ること。

---

## §4 出典一覧(URL)

**柱1(反芻 vs 内省)**
- Treynor, Gonzalez & Nolen-Hoeksema 2003 "Rumination Reconsidered: A Psychometric Analysis", Cognitive Therapy and Research 27(3):247-259: <https://deepblue.lib.umich.edu/handle/2027.42/44342> / <https://link.springer.com/article/10.1023/A:1023910315561>
- Nolen-Hoeksema 1991 反応スタイル理論(上記論文内で参照)
- Brooding and Pondering(active ingredients の分離): <https://pmc.ncbi.nlm.nih.gov/articles/PMC2832851/>

**柱2(意味形成)**
- Park 2010 "Making sense of the meaning literature", Psychological Bulletin 136(2):257-301: <https://pubmed.ncbi.nlm.nih.gov/20192563/>
- Meaning Making Following Trauma(Park モデル概説, 直接取得・確認済): <https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.844891/full>

**柱3(PTG・遅延)**
- Intrusive versus deliberate rumination in PTG(US・日本比較, オープン PDF): <https://ptgi.uncc.edu/wp-content/uploads/sites/9/2015/01/Intrusive-versus-deliberate-rumination-in-posttraumatic-growth-across-US-and-Japanese-samples.pdf>
- 中核信念×反芻×PTG(オープン PDF): <https://ptgi.uncc.edu/wp-content/uploads/sites/9/2015/01/The-relationship-of-core-belief-challenge-rumination-disclosure-and-sociocultural-elements-to-posttraumatic-growth.pdf>
- Cann et al. 2011 ERRI(概要): <https://link.springer.com/rwe/10.1007/978-3-030-77644-2_130-1>
- Tedeschi 2023 "The post-traumatic growth approach", World Psychiatry(本文有料・書誌のみ): <https://onlinelibrary.wiley.com/doi/10.1002/wps.21093>

**柱4(ネガティビティ優位・制御理論)**
- Baumeister et al. 2001 "Bad Is Stronger Than Good", Review of General Psychology 5(4):323-370: <https://journals.sagepub.com/doi/abs/10.1037/1089-2680.5.4.323> / <https://roybaumeister.com/2001/10/15/bad-is-stronger-than-good/>
- Carver & Scheier, Attention and Self-Regulation(制御理論): <https://link.springer.com/book/10.1007/978-1-4612-5887-2>

**柱5(日常・睡眠)**
- 日次ストレス反芻×睡眠×コルチゾール: <https://pmc.ncbi.nlm.nih.gov/articles/PMC6783329/>
- 日次 co-rumination/反芻(夜報告日記法): <https://pmc.ncbi.nlm.nih.gov/articles/PMC11757728/>
- Sleep and Emotional Memory Processing(総説): <https://pmc.ncbi.nlm.nih.gov/articles/PMC4182440/>
- REM×前頭シータと感情記憶の固定: <https://pmc.ncbi.nlm.nih.gov/articles/PMC2665156/>

**柱6(ポジティブ誘因)**
- 畏敬と自己超越・向社会性: <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6548882/>
- 自己超越感情と人生の意味(Affect-Connect-Grow): <https://www.tandfonline.com/doi/full/10.1080/17439760.2025.2604069>
- 転機記憶のナラティブ一貫性と適応: <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7969507/>
- 自伝的推論が伝記的断絶を緩衝: <https://www.researchgate.net/publication/262562199>

---

## 確定できなかった点(正直な記録)
- **一次 PDF のテキスト抽出に失敗**: Park 2010 の EHP 概説 PDF、Tedeschi 2023(World Psychiatry, HTTP 402 有料)、
  US-日本 PTG 比較 PDF は本ツール環境でテキスト化できず、内容は**検索スニペット+オープンな二次概説(Frontiers 2022 は直接取得)で相互確認**した。
  一次原文の逐語確認は未実施。書誌情報は正しいが、逐語引用は限定的。
- **侵入的→熟慮的の移行を「何が」起こすか**は文献自体が未解明と明言(§2-3)。よって「衝撃ゲージ閾値超えが移行を駆動」は
  **本プロジェクトの作業仮説**であり、文献的に確立した機構ではない(RQ 検収対象)。
- **遅延の具体的な長さ**(何時間/何日)は研究間で幅があり、単一の定量値は未確認。「直後=侵入的/遅れて=熟慮的」という
  順序は堅いが、シミュ時間へのマッピング(1晩 vs 数日)は設計判断であり文献が一意に決めない。
- **睡眠の感情処理の向き**(トーン減衰 vs 保存/強化)は結論が割れている(§2-5)。内省後の自己像の変化方向は決め打ち不可。
