# 参考文献リスト(リサーチ・読書リスト)

> あなたが自分で辿れるよう、論文へのリンクを一覧化したドキュメント。Phase R で各論文を読み、`docs/lit/<paper>.md` に構造化メモを作る。
> 各論文は **どの seam に効くか** を併記。設計の正典は [design.md](./design.md)。

## 🔐 リンクの安全性ポリシー(必読)
- **検証済みリンクのみクリック可能**として掲載する。基準: 正規かつ評判の確かな学術ドメイン(`arxiv.org` / `doi.org` / 公式出版社)、HTTPS、未知ホストへのリダイレクトなし、短縮URL・ミラー・不明ホストは不可。
- 正規URLを確認できていないものは「**🔶 リンク未検証**」と明示し、**クリック可能リンクを張らない**(検証後に張る)。
- 検証方法: 正規ドメインで `abs`/DOI ページが解決し、別ホストへ飛ばないことを確認してから掲載。

---

## クラスタ1: 規模で創発が崩壊しない機構 ★最重要
本プロジェクトの新規性に直結。「規模だけでは不十分、崩壊を防ぐ機構が要る」。

| 論文 | リンク | 効く seam | なぜ |
|---|---|---|---|
| **Li, Li & Zhou 2026** — "Does Socialization Emerge in AI Agent Society? A Case Study of Moltbook" | ✅ [arxiv.org/abs/2602.14299](https://arxiv.org/abs/2602.14299) | observer指標 / memory / propagation | 規模だけでは社会化が創発しない実証(大域的意味安定化・個体慣性・共有メモリ欠如)。失敗様態=我々が回避すべき設計点。5指標を観測層に流用 |
| **Park et al. 2023** — "Generative Agents: Interactive Simulacra of Human Behavior" | ✅ [arxiv.org/abs/2304.03442](https://arxiv.org/abs/2304.03442) | agents/memory / cognition | memory stream(経験の自然言語記録 + recency/importance/relevance 検索)+ reflection(高次内省の周期生成)。個別エージェントの階層メモリ+認知的圧縮の定番 |
| **Packer et al. 2023** — "MemGPT: Towards LLMs as Operating Systems" | ✅ [arxiv.org/abs/2310.08560](https://arxiv.org/abs/2310.08560) | agents/memory | 仮想コンテキスト管理(OSの階層メモリ着想、主⇄外部のページング)。有限コンテキストで長期記憶を扱う設計 |
| **Ashery et al. 2025** — "Emergent social conventions and collective bias in LLM populations" (Science Advances) | 🔶 リンク未検証 | labeling / propagation | naming game で慣習が自発創発、コミット少数派が tipping point で慣習を覆す。ラベル創発・集団バイアスの核 |

## クラスタ2: 因子(OPEN#1/#3)— trait / state の切り分け ✅ deep-dive 済 → [[factors__personality-motivation-overview]]
| 論文 | リンク | 効く seam | なぜ |
|---|---|---|---|
| Cacioppo & Petty 1982 — Need for Cognition | ✅ [PMC(6項目版)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7545655/)(原著 JPSP 10.1037/0022-3514.42.1.116) | factors(trait) | 思考頻度の trait 化(上流ゲート) |
| Rotter 1966 — Locus of Control | ✅ [Springer](https://link.springer.com/rwe/10.1007/978-94-007-0753-5_1688)(原著 Psych Monogr 10.1037/h0092976) | factors(trait寄り) | 内的統制 ≠ 自己効力感。世界改変に load-bearing |
| Bandura 1977/1997 — Self-Efficacy(4源泉) | ✅ [PMC(源泉の実証ランキング)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12502103/)(原著 Psych Rev 10.1037/0033-295X.84.2.191) | factors(state) / update | 効力感の4源泉 = state 更新則の入力 |
| Schwarzer & Jerusalem 1995 — GSE(初期分布) | ✅ [Taylor&Francis(多文化検証)](https://www.tandfonline.com/doi/abs/10.3200/JRLP.139.5.439-457) | config(OPEN#3) | 母集団分布(10-40, α=.86-.95)を初期分布の逆算に |
| Parker & Collins 2010 — Taking Stock(先行行動) | ✅ [SAGE](https://journals.sagepub.com/doi/10.1177/0149206308321554) | factors(trait) | 複数の proactive 行動の高次構造 |
| Parker, Bindl & Strauss 2010 — Making Things Happen | ✅ [SAGE](https://journals.sagepub.com/doi/10.1177/0149206310363732) | factors/update | proactive motivation(can-do/reason-to/energized-to)= ファネルと整合 |
| Bateman & Crant 1993 — Proactive Personality | ✅ [Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1002/job.4030140202) / [meta: Fuller&Marler 2009](https://www.sciencedirect.com/science/article/abs/pii/S000187910900075X) | ⚠️ observer/measure | world-changer の直接構成概念 → **入力にせず事後測定** |

## クラスタ3: state 更新則(OPEN#2)✅ deep-dive 済 → [[state-update__open2-overview]](★ k= フィードバックゲインの接地)
| 論文 | リンク | 効く seam | なぜ |
|---|---|---|---|
| Bandura — 4源泉(達成/代理/説得/生理) | ✅ クラスタ2参照(PMC) | factors/update | どの出来事で効力感が動くか(決め打ち禁止、因果構造のみ) |
| van Zomeren, Postmes & Spears 2008 — SIMCA | ✅ [Semantic Scholar](https://www.semanticscholar.org/paper/45cddbdf855141daa5be6ced32a1a0b2f28d954f)(Psych Bulletin 134(4):504-535) | factors/update | 不公正感・集団効力感・アイデンティティ+**フィードバックループ = k の接地** |
| Morrison & Phelps 1999 — Taking Charge | ✅ [Semantic Scholar](https://www.semanticscholar.org/paper/ab142c3b445b0da3e8afaf45e6b596040575aa78)(AMJ 42:403-419) | factors(state)/measure | felt responsibility が傍観者と主体を分ける。taking charge=事後測定 |

## クラスタ4: 文化進化・社会言語学 / ラベリング(OPEN#4)✅ deep-dive 済 → [[labeling__cultural-evolution-overview]]
| 論文 | リンク | 効く seam | なぜ |
|---|---|---|---|
| Ashery, Aiello & Baronchelli 2025 — Emergent conventions & collective bias in LLM populations | ✅ [Science Advances](https://www.science.org/doi/10.1126/sciadv.adu9368) / [arXiv](https://arxiv.org/abs/2410.08948) | labeling / propagation / observer | LLM集団で慣習が自発創発、**集団バイアス創発**、tipping、コミット少数派。制約版ラベリングの支柱 |
| Centola, Becker, Brackbill & Baronchelli 2018 — Tipping points in social convention | ✅ [Science](https://www.science.org/doi/10.1126/science.aas8827) | observer / labeling | コミット少数派 **~25%** で多数派反転(参照閾値) |
| Baronchelli — minimal Naming Game | ✅ [arXiv 1701.07419](https://arxiv.org/abs/1701.07419) | labeling | ラベル創発の形式モデル(form-meaning 慣習) |
| Centola & Baronchelli 2015 — Spontaneous emergence of conventions | ✅ [PNAS](https://www.pnas.org/doi/10.1073/pnas.1418838112) | labeling | 慣習の自発創発(実験的) |
| Snow & Benford — Framing Theory | ✅ クラスタ8参照(Benford&Snow 2000) | labeling | grievance の命名 = 動員(個人→集団の橋) |

## クラスタ5: MAS/ABM フレームワーク・大規模LLM社会(再利用・先行研究)★build-vs-reuse の判断材料
既存フレームワークを土台/参照にすれば10日ビルドが楽になり、結果も良くなる。**「規模」は既に達成済み**(OASIS=100万)であり、我々の差別化は規模でなく研究の問い+k*測定+崩壊回避機構である点に注意。

| 論文 / FW | リンク | 種別 | なぜ |
|---|---|---|---|
| **OASIS** — Open Agent Social Interaction Simulations (≤100万体) | ✅ [arxiv.org/abs/2411.11581](https://arxiv.org/abs/2411.11581) | 大規模先行研究 | 100万LLMエージェントのSNSシミュ。情報伝播・群分極・herd。アーキ(env server+推薦+time engine, 21行動)が直接の設計参照。M1現象の最接近先例 |
| **AgentSociety** — 1万+体・500万相互作用 | ✅ [arxiv.org/abs/2502.08691](https://arxiv.org/abs/2502.08691) | 大規模先行研究 | リアル社会環境+大規模エンジン。人間行動・社会の理解 |
| **Concordia**(DeepMind) — 生成エージェントMAS | ✅ [arxiv.org/abs/2312.03664](https://arxiv.org/abs/2312.03664) | フレームワーク | game master が環境を司る。物理/社会/デジタル空間に接地。再利用候補 |
| **AgentScope** — 超大規模MAS | ✅ [arxiv.org/abs/2407.17789](https://arxiv.org/abs/2407.17789) | フレームワーク | 数千〜数百万体の大規模実行・効率化。スケール工学の参照 |
| **AI Metropolis** — out-of-order 実行 | ✅ [arxiv.org/abs/2411.03519](https://arxiv.org/abs/2411.03519) | スケール技法 | LLM-MAS を依存関係解析で並列化しスケール |
| Mesa(Python ABM 古典) | 🔶 リンク未検証 | フレームワーク | 軽量Python ABM。scheduler/grid/datacollector/batch を提供 |

> 検証メモ: arxiv 5本は WebSearch で title↔URL が一致する `arxiv.org` 正規ページとして確認済み。

## クラスタ6: サーベイ & 方法論(validation 危機)★分野全体を覆う + 我々の novelty を強化
generative social simulation の**中核的未解決問題は「検証(validation)」**。多くが believability/zero-shot prompting 依存で operational validity を示せていない。我々の falsifiable 再定式化(分散分解・k*)+ 観測者frame測定 + 指紋最小化は、まさにこの危機への回答。

| 論文 | リンク | 種別 | なぜ |
|---|---|---|---|
| LLMs Empowered ABM & Simulation: A Survey | ✅ [arxiv.org/abs/2312.11970](https://arxiv.org/abs/2312.11970) | サーベイ(分野全体) | "数百本"を覆う出発点。LLM-ABM の全体像 |
| Do LLMs Solve the Problems of ABM? Critical Review | ✅ [arxiv.org/abs/2504.03274](https://arxiv.org/abs/2504.03274) | 批判的レビュー | validation危機の核。我々の設計が回答 |
| Validation is the central challenge... | ✅ [pmc.ncbi.nlm.nih.gov/articles/PMC12627210](https://pmc.ncbi.nlm.nih.gov/articles/PMC12627210/) | 批判的レビュー | operational validity の欠如 |
| Integrating LLM in ABM: Opportunities & Challenges (JASSS投稿) | ✅ [arxiv.org/abs/2507.19364](https://arxiv.org/abs/2507.19364) | レビュー | 機会と課題の整理 |
| LLM-Based Social Simulations Require a Boundary | ✅ [arxiv.org/abs/2506.19806](https://arxiv.org/abs/2506.19806) | 方法論 | 適用境界の議論 |
| Coupling Macro Dynamics & Micro States (long-horizon) | ✅ [arxiv.org/abs/2604.05516](https://arxiv.org/abs/2604.05516) | 機構 | 長期run × LOD(マクロ↔ミクロ結合)に直結 |
| Can LLMs Implement ABM? ODD Replication | ✅ [arxiv.org/abs/2602.10140](https://arxiv.org/abs/2602.10140) | 標準 | ODD = ABM 文書化プロトコル(再現性) |

## クラスタ7: ネットワーク科学・拡散理論(伝播 M1指標b)✅ deep-dive 済 → [[network__diffusion-overview]]
| 論文 | リンク | 効く seam | なぜ |
|---|---|---|---|
| Centola & Macy 2007 — Complex Contagions & the Weakness of Long Ties | ✅ [doi.org/10.1086/521848](https://doi.org/10.1086/521848) | propagation / world | 行動・運動は **complex contagion**(複数補強が必要)。伝播モデルの基盤 |
| Complex Contagions: A Decade in Review | ✅ [arXiv 1710.07606](https://arxiv.org/abs/1710.07606) | propagation | complex contagion の総説(数百本を覆う) |
| Granovetter 1978 — Threshold Models of Collective Behavior | ✅ [Springer](https://link.springer.com/chapter/10.1007/978-3-658-21742-6_54)(AJS 83(6):1420-43) | factors / propagation | 個人閾値の異質分布 → 集団的帰結 |
| Watts 2002 — A simple model of global cascades | ✅ [doi.org/10.1073/pnas.082090499](https://doi.org/10.1073/pnas.082090499) | propagation / engine | 稀な巨大カスケード・2つの感受性レジーム(相転移的)|

## クラスタ8: 集合行為・制度経済学・フレーミング(M1指標d)✅ deep-dive 済 → [[collective-action__institutions-framing-overview]]
| 論文 | リンク | 効く seam | なぜ |
|---|---|---|---|
| Olson 1965 — The Logic of Collective Action | ✅ [SEP: Free Rider](https://plato.stanford.edu/entries/free-rider/) | actions / observer | フリーライド。**大集団ほど協調が困難** = M1(d) の障壁 |
| Ostrom 1990 — Governing the Commons(8原則) | ✅ [Ostrom Workshop](https://ostromworkshop.indiana.edu/courses-teaching/teaching-tools/ostrom-design/index.html) | actions(affordance)/ observer | 共同体は CPR を自己統治可 = **制度の創発**(世界改変) |
| Benford & Snow 2000 — Framing Processes and Social Movements | ✅ [Annual Reviews](https://www.annualreviews.org/content/journals/10.1146/annurev.soc.26.1.611) | labeling / observer | 診断→予後→動機づけ = 不満が運動になる橋 |

## クラスタ9: 複雑系・統計物理(相転移・臨界)= k* 測定の方法論 ✅ deep-dive 済 → [[complexity__phase-transition-methodology]]
| 論文 | リンク | 効く seam | なぜ |
|---|---|---|---|
| Social nucleation — Group formation as a phase transition | ✅ [arXiv 2107.06696](https://arxiv.org/abs/2107.06696) | engine/metrics | 集団形成 = 相転移。k* の枠組み |
| Scheffer et al. 2009 — Early-warning signals for critical transitions | ✅ [doi.org/10.1038/nature08227](https://doi.org/10.1038/nature08227) | analyze | critical slowing down(分散・自己相関↑)で k* 検出 |
| Genetic nurturing & missing heritability(PNAS 2020) | ✅ [PNAS](https://www.pnas.org/doi/10.1073/pnas.2015869117) | analyze | **分散分解は nature/nurture 結合系で ill-defined** = R² caveat |
| Heritability(SEP) | ✅ [plato.stanford.edu/entries/heritability](https://plato.stanford.edu/entries/heritability/) | analyze | 分散分解の概念的限界 |

## クラスタ10: 計測・検証(validation)= novelty 第4軸 ✅ deep-dive 済 → [[measurement__validation-overview]]
| 論文 | リンク | 効く seam | なぜ |
|---|---|---|---|
| Towards Operational Validation of LLM-Agent Social Simulations | ✅ [arXiv 2508.21740](https://arxiv.org/abs/2508.21740) | observer/measure | 機構ベースの operational validity(多 seed マクロ) |
| Argyle et al. 2023 — Out of One, Many(silicon sampling) | ✅ [arXiv 2209.06899](https://arxiv.org/abs/2209.06899)(Political Analysis) | observer / config | algorithmic fidelity。**tail 過小 = 改変者(tail)の脅威** |
| Aher et al. 2023 — Turing Experiments | ✅ [arXiv 2208.10264](https://arxiv.org/abs/2208.10264) | observer/measure | 既知実験の再現 = calibration の枠組み |
| 大規模再現(Nature Comp Sci 2025) | ✅ [Nature CS](https://www.nature.com/articles/s43588-025-00840-7) | observer/measure | 73-81%再現だが効果量水増し・sensitive topic 盲点 |
| ※「Validation is the central challenge」はクラスタ6参照 | — | — | validation 危機の総説 |

## クラスタ11: LLM/AI を社会エージェントとして(validity gate)✅ deep-dive 済 → [[llm__agents-validity-model-choice]]
| 論文 | リンク | 効く seam | なぜ |
|---|---|---|---|
| LLMs Can't Handle Peer Pressure(multi-agent conformity) | ✅ [arXiv 2508.18321](https://arxiv.org/abs/2508.18321) | cognition / observer | RLHF instruct は peer に最大85.5%同調 → 異論/世界改変を抑圧・崩壊の一因 |
| Understanding the Effects of RLHF on Generalisation & Diversity | ✅ [arXiv 2310.06452](https://arxiv.org/abs/2310.06452) | llm/config | RLHF は多様性を減らす(mode collapse)→ tail/異質性を潰す |
| Generalization or Memorization: Data Contamination | ✅ [arXiv 2402.15938](https://arxiv.org/abs/2402.15938) | observer/measure | 汚染で「創発」が記憶再生の恐れ → calibration は新規設定で |
| Evaluating LLM Biases in Persona-Steered Generation | ✅ [arXiv 2405.20253](https://arxiv.org/abs/2405.20253) | config / observer | persona 注入は不完全・LLM の指紋(bias)混入 |

## クラスタ12: 世界2.0 分野群 — ①substrate/妥当性(承認プラン Part A)🔄 進行中
| 論文 | リンク | 効く seam | なぜ |
|---|---|---|---|
| Lynch 1960 — The Image of the City(+計算論版 Jiang) | ✅ [arXiv 1212.0940](https://arxiv.org/abs/1212.0940) / [Studio Skills: Legibility](https://ecampusontario.pressbooks.pub/studioskills/chapter/analysis-legibility-lynch/) | world/spatial / observer / viz | 5要素(path/edge/district/node/landmark)。**landmark を hardcode せず軌跡から創発・事後測定**(head/tail 則) → [[urban__lynch1960_image-of-the-city]] |
| Searle 1995 — The Construction of Social Reality(+Barry Smith 解説) | ✅ [Britannica](https://www.britannica.com/biography/John-Searle/Philosophy-of-social-institutions) / [PhilArchive: Smith](https://philarchive.org/rec/SMIJSF) | world/symbolic / labeling / collective-action | 「X counts as Y in C」status function=制度創発の哲学的接地。**制度を宣言 verb の affordance に** → [[ontology__searle1995_institutional-facts]] |
| Tolman(認知地図)/ Gibson(affordance)— 環境・知覚心理 | ✅ [Oxford Handbook: Wayfinding & Spatial Cognition](https://academic.oup.com/edited-volume/36322/chapter/318669085) / [地理空間認知(Taylor&Francis 2025)](https://www.tandfonline.com/doi/full/10.1080/19475683.2025.2451228) | agents/cognition / world/spatial / actions | 不完全な個体別認知地図 + affordance 知覚 = 設計原則の心理学的接地 → [[envpsych__cognitive-maps-affordance-overview]] |
| 生態学 — keystone/niche/succession/resilience/carrying capacity | ✅ [Keystone & Trophic Cascades(Fiveable)](https://fiveable.me/fundamentals-ecology/unit-7/keystone-species-trophic-cascades/study-guide/sdGJtHGe7OiZg3ZD) / [Ecological theory for restoration(ScienceDirect 2024)](https://www.sciencedirect.com/science/article/pii/S096098222400383X) | world/ecology / resource / observer | keystone=世界改変者アナログ / carrying capacity=スケール上限 / resilience=anti-collapse → [[ecology__ecosystem-metaphor-overview]] |
| 経済 affordance — 両面市場/ネットワーク経済/メカニズムデザイン/情報経済 | ✅ [Two-sided markets(Northwestern)](https://faculty.wcas.northwestern.edu/apa522/Two-Sided-Market-and-Network-Effects.pdf) / [Asymmetric info(Nobel 2001)](https://www.nobelprize.org/prizes/economic-sciences/2001/popular-information/) | world/resource / social-network / observer | cold-start=社会化ブートストラップ / critical mass=相転移 / 評判=信頼レイヤー → [[econ__affordance-cluster-overview]] |

## クラスタ13: 世界2.0 分野群 — ②engagement(承認プラン Part A)⚠️injection 注意
| 論文 | リンク | 効く seam | なぜ |
|---|---|---|---|
| Deci&Ryan(SDT)/ Csikszentmihalyi(flow) | ✅ [Ryan&Deci 2000 SDT(PDF)](https://selfdeterminationtheory.org/SDT/documents/2000_RyanDeci_SDT.pdf) / [Flow Theory(TheoryHub)](https://open.ncl.ac.uk/academic-theories/8/flow-theory/) | factors / state-update / actions | 自律・有能感・関係性=内発動機。⚠️注入せず充足**可能**な affordance に → [[motivation__sdt-flow-overview]] |
| Fogg 行動モデル(B=MAP)/ Thaler&Sunstein(nudge) | ✅ [Fogg Model(Stanford BDL)](https://behaviordesign.stanford.edu/resources/fogg-behavior-model) / [Fogg Model(Decision Lab)](https://thedecisionlab.com/reference-guide/psychology/fogg-behavior-model) | actions / cognition / world | 動機×能力×プロンプト同時性。⚠️設計者 nudge を仕込まず、改変者=環境設計者を観測 → [[behdesign__fogg-nudge-overview]] |
| Hamari 他(gamification / 過正当化) | ✅ [Hamari: PBL harm intrinsic?(ResearchGate)](https://www.researchgate.net/publication/264310429_Do_points_levels_and_leaderboards_harm_intrinsic_motivation_An_empirical_analysis_of_common_gamification_elements) / [meta-analysis(Springer ETR&D 2023)](https://link.springer.com/article/10.1007/s11423-023-10337-7) | observer / config | ⚠️★報酬注入は過正当化で内発的世界改変を歪める→既定off・実験変数化 → [[gamification__extrinsic-reward-overview]] |
| Skinner(強化スケジュール) | ✅ [Operant Conditioning(Simply Psychology)](https://www.simplypsychology.org/operant-conditioning.html) / [強化と動機(PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9090977/) | state-update / actions | variable-ratio=依存機構。⚠️結果 affordance のみ、報酬設計しない。cheap tier 行動則 → [[behpsych__reinforcement-schedules-overview]] |
| Rogers(イノベーション普及)+ オピニオンリーダー | ✅ [Diffusion of Innovations(TheoryHub)](https://open.ncl.ac.uk/theories/8/diffusion-of-innovations/) / [オピニオンリーダー特定(ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S0040162511001272) | labeling / network / observer | 採用者カテゴリ(革新者2.5%/初期13.5%)=tail 実証版 / オピニオンリーダー=keystone → [[marketing__diffusion-consumer-overview]] |
| Moore / Iansiti&Levien(ビジネスエコシステム・keystone) | ✅ [The Keystone Advantage(ResearchGate)](https://www.researchgate.net/publication/257926262_The_Keystone_Advantage_What_the_New_Dynamics_of_Business_Ecosystems_Mean_for_Strategy_Innovation_and_Sustainability) / [プラットフォーム価値共創(Springer MRQ 2024)](https://link.springer.com/article/10.1007/s11301-024-00416-1) | collective-action / social-network / observer | keystone orchestrator=世界改変者の組織版(制度・標準に投資) → [[bizeco__business-ecosystem-overview]] |

## クラスタ14: 世界2.0 分野群 — ③build・viz + Part B(PLATEAU/3DCG)
| 論文 | リンク | 効く seam | なぜ |
|---|---|---|---|
| PLATEAU/3DCG 可視化(Unity SDK + Web/Cesium 3D Tiles) | ✅ [PLATEAU SDK for Unity(公式マニュアル)](https://project-plateau.github.io/PLATEAU-SDK-for-Unity/manual/ImportCityModels.html) / [Project-PLATEAU/PLATEAU-SDK-for-Unity(GitHub)](https://github.com/Project-PLATEAU/PLATEAU-SDK-for-Unity) / [3dcitydb-web-map(GitHub)](https://github.com/3dcitydb/3dcitydb-web-map) / [CesiumGS/3d-tiles(GitHub)](https://github.com/CesiumGS/3d-tiles) | viz / engine/output / observer | 渋谷=商用可・無料。sim⇄viz 疎結合 I/F 定義。LLM推論と描画を分離 → [[viz__plateau-pipeline-overview]] |
| 分散システム・actor model(+AgentScope 大規模) | ✅ [Actor Model(GeeksforGeeks)](https://www.geeksforgeeks.org/system-design/actor-model-in-distributed-systems/) / [Event-Driven & Actor Models(wal.sh)](https://wal.sh/research/event-driven-architectures-actor-model.html) / [AgentScope 大規模(arXiv 2407.17789)](https://arxiv.org/abs/2407.17789) | engine / infra / observer | actor 並列=スケール中核。★非決定性 vs 多seed再現の緊張→決定化 seam → [[engine__distributed-actor-overview]] |
| ゲームデザイン MDA / 創発的ゲームプレイ(+HCI/サービスデザイン) | ✅ [MDA Framework(Game Developer)](https://www.gamedeveloper.com/design/revisiting-the-mda-framework) / [Redefining MDA(MDPI Information 2021)](https://www.mdpi.com/2078-2489/12/10/395) | actions / world / design-principle | ★emergent gameplay=no-fingerprint 原則の設計工学版(Mechanics のみ設計) → [[gamedesign__emergent-systemic-overview]] |

## クラスタ15: 世界2.0 分野群 — ④哲学(価値論 / システム哲学)
| 論文 | リンク | 効く seam | なぜ |
|---|---|---|---|
| 価値論(axiology)内在/道具的価値・関係説 | ✅ [Value Theory(SEP)](https://plato.stanford.edu/entries/value-theory/) / [Intrinsic vs Extrinsic Value(SEP)](https://plato.stanford.edu/entries/value-intrinsic-extrinsic/) | world/symbolic / observer | ★価値は関係から創発=ラベル/status の価値版。新価値樹立=世界改変 → [[value__axiology-overview]] |
| システム哲学 GST(Bertalanffy)equifinality/feedback/autopoiesis | ✅ [Systems theory(Wikipedia)](https://en.wikipedia.org/wiki/Systems_theory) / [Bertalanffy & Cybernetics(PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4610108/) | complexity / engine / meta | ★★equifinality=k*問いのGST版 / feedback=k / autopoiesis=anti-collapse → [[systems__gst-overview]] |

## クラスタ16: インフラ検証・運用(Gemini 要約 fact-check、2026-07-02 Opus 委譲)
| 論文/資料 | リンク | 効く seam | なぜ |
|---|---|---|---|
| vLLM 量子化/APC/最適化(公式 docs) | ✅ [FP8 要件](https://docs.vllm.ai/en/v0.8.5/features/quantization/fp8.html) / [APC](https://docs.vllm.ai/en/stable/features/automatic_prefix_caching.html) / [optimization](https://docs.vllm.ai/en/stable/configuration/optimization/) | infra / config | FP8=Ada/Hopper 要件(A5000 は W8A16 化)、APC は意味論的中立 → [[infra__gemini-summary-verification]] |
| Qwen3.6-27B(公式 HF + vLLM recipes + unsloth GGUF) | ✅ [Qwen/Qwen3.6-27B](https://huggingface.co/Qwen/Qwen3.6-27B) / [vLLM recipes](https://recipes.vllm.ai/Qwen/Qwen3.6-27B) / [unsloth MTP-GGUF](https://huggingface.co/unsloth/Qwen3.6-27B-MTP-GGUF) | llm/fleet / config | Apache-2.0・MTP 1.5-2x・Q4_K_M 17.1GB。base 版未公開 |
| ID-RAG(identity retrieval・drift 対象化) | ✅ [arXiv 2509.25299](https://arxiv.org/abs/2509.25299) | agents/memory / observer | ★内省ループの drift/mode collapse/hallucination 伝播を対象化=k 実装部位の直系先行 → [[infra__agentic-memory-reflection]] |
| Letta/MemGPT(self-editing memory) | ✅ [letta-ai/letta(GitHub)](https://github.com/letta-ai/letta) | agents/memory | 自発的記憶管理の実装系(クラスタ1 MemGPT の発展) |
| vLLM Router / prefix-aware routing | ✅ [vLLM Router(公式ブログ)](https://blog.vllm.ai/2025/12/13/vllm-router-release.html) / [prefix-aware routing(docs)](https://docs.vllm.ai/projects/production-stack/en/latest/use_cases/prefix-aware-routing.html) | infra / engine | agent-ID sticky routing で prefix ヒット率~96%回復 → [[infra__storage-routing]] |
| 量子化と精度(AWQ vs GPTQ) | ✅ [arXiv 2505.15030](https://arxiv.org/abs/2505.15030) | config | 小型モデル 4bit は AWQ 優位(tool calling 精度) |
| agentic workload scheduling | ✅ [arXiv 2506.24045](https://arxiv.org/abs/2506.24045) | infra / engine | 個別睡眠=負荷平準化の先行 |
| 🔶 実測ブログ群(信頼度中・自前ベンチで裏取り前提) | [qwen3.6-rtx3090-lab(GitHub)](https://github.com/tfriedel/qwen3.6-rtx3090-lab) 等 | infra | A5000 直接実測なし。スループット概算(N=90-480/step)の根拠 |

## クラスタ17: 第4フェーズ ギャップ埋め(実験計画/物理層/ペルソナ・言語・安全)2026-07-02 Opus 委譲
| 論文/資料 | リンク | 効く seam | なぜ |
|---|---|---|---|
| ABM 実験計画(Lorscheid / PELT / FSS / multiverse) | ✅ [Lorscheid 2012](https://link.springer.com/article/10.1007/s10588-011-9097-3) / [PELT](https://arxiv.org/abs/1101.1438) / [FSS naming game](https://arxiv.org/abs/1609.02869) / [multiverse CSS](https://arxiv.org/abs/2605.19745) | analyze / observer | 2段階掃引+CV収束 seed / k*主推定=FSS(N 3水準)/ pre-register+multiverse → [[method__experiment-design-statistics]] |
| LLM-judge 運用(self-preference / AgentRewardBench) | ✅ [arXiv 2410.21819](https://arxiv.org/abs/2410.21819) / [arXiv 2504.08942](https://arxiv.org/abs/2504.08942) | observer/measure | 別ファミリ judge+順序スワップ+人手 κ≥0.7 → 同上 |
| 人流経験則(Gonzalez / Schläpfer / EPR / scikit-mobility) | ✅ [Nature 2008](https://www.nature.com/articles/nature06958) / [Nature 2021](https://www.nature.com/articles/s41586-021-03480-9) / [skmob docs](https://scikit-mobility.github.io/scikit-mobility/reference/models.html) | world/spatial | EPR+visitation law=cheap tier 移動則(参照実装あり)→ [[world__mobility-shibuya-scenario]] |
| Epstein 2002 civil violence(grievance 範型) | ✅ [PNAS](https://www.pnas.org/doi/10.1073/pnas.092080199) / [Mesa 実装](https://mesa.readthedocs.io/stable/examples/advanced/epstein_civil_violence.html) | scenario / state-update | grievance=hardship×(1−legitimacy) 閾値。ショック=affordance 変化のみ → 同上 |
| 渋谷データ(OSM / 国土数値情報 / e-Stat / 人流) | ✅ [国土数値情報](https://nlftp.mlit.go.jp/ksj/) / [G空間人流](https://www.geospatial.jp/ckan/dataset/mlit-1km-fromto) / [e-Stat](https://www.e-stat.go.jp/) | world / config | POI グラフ無償構築+IPF 合成人口の骨格 → 同上 |
| ペルソナ生成(Verbalized Sampling / PersonaHub / 尺度妥当性) | ✅ [arXiv 2510.01171](https://arxiv.org/abs/2510.01171) / [PersonaHub](https://github.com/tencent-ailab/persona-hub) / [arXiv 2311.05297](https://arxiv.org/abs/2311.05297) | config(OPEN#3) | mode collapse 対策+尺度は注入/評価分離+tail 保護 → [[agents__persona-language-safety-opinion]] |
| 言語×文化(Swallow / 価値観の言語差) | ✅ [Qwen3 Swallow](https://swallow-llm.github.io/qwen3-swallow.en.html) / [arXiv 2604.22153](https://arxiv.org/abs/2604.22153) / [Ricoh 日本語版](https://jp.ricoh.com/release/2026/0605_1) | llm / config | 日<英・トークン2-3倍・方向不定の文化シフト → 日/英 ablation 要 → 同上 |
| Prompt Infection / 敵対的説得 | ✅ [arXiv 2410.07283](https://arxiv.org/abs/2410.07283) / [Nature Sci Rep](https://www.nature.com/articles/s41598-026-42705-7) | engine / observer | 1体→全網汚染の実証。防御=構造化分離+「操作量」を改変者指標に → 同上 |
| LLM×意見ダイナミクス(FJ 一致 / conformity) | ✅ [NAACL 2024](https://aclanthology.org/2024.findings-naacl.211/) / [arXiv 2501.13381](https://arxiv.org/abs/2501.13381) | propagation / lod | cheap tier=Friedkin-Johnsen、tail は LLM tier 残留 → 同上 |

## クラスタ18: 批判・境界論文(red-team 監査、先回り引用用)
| 論文 | リンク | なぜ(→ [[../risk-register]]) |
|---|---|---|
| LLM Social Simulations Require a Boundary | ✅ [arXiv 2506.19806](https://arxiv.org/abs/2506.19806) | ★tail/個体主張の禁止勧告=R2 の根拠。主張二層化で先回り武装 |
| Robustness Audits(実装差76pp) | ✅ [arXiv 2605.18890](https://arxiv.org/abs/2605.18890) | ★k* を artifact と断じる武器=R1 の根拠。自主監査を論文に載せる |
| AgentSociety(1万体・社会学 mind) | ✅ [arXiv 2502.08691](https://arxiv.org/abs/2502.08691) | 新規性競合(心理駆動大規模は既存) |
| trait→行動 generative ABM | ✅ [arXiv 2601.15114](https://arxiv.org/abs/2601.15114) | R4(trait ロールプレイ循環)の裏取り |
| BeliefShift(縦断信念ドリフト) | ✅ [arXiv 2603.23848](https://arxiv.org/abs/2603.23848) | R9(state が trait を鏡写す)の裏取り |

---

## ステータス
- ✅ 検証済み・掲載可: 100本超(1:3 / 2:7 / 3:+2 / 4:4 / 5:5 / 6:7 / 7:4 / 8:3 / 9:4 / 10:4 / 11:4 / 12:5 / 13:6 / 14:3 / 15:2 / 16:7 / 17:~17 / 18:5)+ 🔶実測ブログ(裏取り前提)
- 🔶 未検証: Mesa(github)のみ。**リサーチ funnel(分野1-9)は一巡完了。**
- 🔶 未検証: Snow&Benford(分野6で検証)+ Mesa(github)。deep-dive 時に正規 URL を検証してからリンクを張る
- 注: これは funnel の出発点(サーベイ層)。各分野の deep-dive で `docs/lit/` に1論文1メモを増やす
