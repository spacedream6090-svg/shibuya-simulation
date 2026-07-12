# エージェント単位 LOD 深掘り — 前景=高計算/背景=低計算を入れるべきか(討議資料)

- 作成: 2026-07-12 / 担当: Opus 4.8(リサーチ) / 種別: **討議用の材料整理**(コード非編集・実装提案の結論は出さない)
- 目的: ユーザーと Fable(親)が「**エージェント単位の LOD**(前景=高計算/背景=低計算)を導入すべきか・どう設計すべきか」を深く議論するための **選択肢・先行例・トレードオフ** を 1 ファイルに揃える。結論を出すことではなく、**論点を漏らさず・事実で武装する** のが本書の役割。
- 既読前提(重複を避け差分を書く):
  - [`docs/research/multi-model-lod.md`](multi-model-lod.md) §0(LOD マトリクス)・§4(先行研究)・§7(R1 整合)
  - [`docs/plans/multi-model-lod.md`](../plans/multi-model-lod.md) M3(agent-tier)と OPEN#1(割当方式の論点)
  - [`docs/research/compute-efficiency.md`](compute-efficiency.md) Tier 3(階層化=「研究目的と衝突」の判定根拠)・§4(archetype 非推奨)
  - 実装: [`src/society/cognition/lod.py`](../../src/society/cognition/lod.py)(発火予算のみ)・[`cognition/drive.py`](../../src/society/cognition/drive.py)(発火ゲート)・[`cognition/routine.py`](../../src/society/cognition/routine.py)(ルールベース既定動作)
  - [`docs/log/devlog.md`](../log/devlog.md) Entry 8(agent-tier 割当を「trait 由来」にすると R²(k) に生得性を裏口注入する、という Fable の懸念)
- 出典方針: 一次ソース URL 必須。二次情報(ゲーム解説・ベンダー記事・wiki)は 🔶 を付し絶対値の根拠にしない。未確認は「**未確認**」と明記(捏造禁止)。ゲーム技術の細部は GDC/公式ドキュメント以外は 🔶。

---

## §1 現在地 — 我々が「今」持っている LOD

**用語の整理(本書での定義):**
- **発火 LOD**(実装済): 「その step で誰が LLM を撃つか」を絞る。1 step あたりの発火予算 `LodBudget.max_per_step`(lod.py)+ 欲求駆動発火ゲート(drive.py)。実測発火率 **4.1〜11.4%**(≒12倍の呼数削減、compute-efficiency §1)。
- **purpose LOD**(計画中・M1-M2): 「呼種ごとに違うモデル」。reflect(3.8%)=大、deliberate(92.7%)=小。全員一様=R1 無傷(multi-model-lod §0)。
- **モデル級 agent LOD**(本書の主題・未導入): 「**個体ごとに違うモデル級**」。前景個体=大モデル/API、背景個体=小モデル or ルール。**これは現状まったく入っていない。**

**現状の事実(コードから):**
1. `lod.py` は **発火予算(インフラ上限 N)しか持たない**。「誰を撃つか」の質的選別は drive.py に移譲済み(v1 の surprise トリガーを 2026-07-04 に置換)。予算は k 非依存・全個体共通。
2. `drive.py` の発火は **観測可能な出来事のみ**を入力とし、信念・k 条件に依存しない(R1 計算量交絡対策が設計に明記)。個体差(閾値・重み)は traits→factors 経由の no-fingerprint。
3. `routine.py` は **非 LLM の身体日課(通勤/食事/帰宅/就寝/移動)だけ**を返す。★発話・思考は必ず LLM(routine は定型文を一切話さない)。= 既に「背景=ルールベース」の器はあるが、**それは"撃たない step の充填"であって"背景個体という階層"ではない**。
4. 全個体は **同一モデル**を引く(model.backend 単一)。前景/背景の区別は概念としても実装としても存在しない。

> **要点**: 我々の LOD は「時間軸の LOD(いつ撃つか)」であって「**個体軸の LOD(誰を安く回すか)**」ではない。本書が問うのは後者の是非。前者は既に R1 準拠で機能しており、後者は R1・k\* に新しい危険を持ち込む別物である。

---

## §2 先行例カタログ — 「見ていない部分を安く・破綻なく保つ」実務知

各例末尾の **▶ 移せる知見** が本シミュへの 1 行接続。

### 2-1 ゲーム業界の群衆・オフスクリーン LOD

| 事例 | 仕組み | 状態保存・整合の扱い |
|---|---|---|
| **Assassin's Creed Unity「Bulk System / AI Recycling」** 🔶 | NPC を 3 LOD に分類: **LoRes Bulk**(>40m・低ポリ・基本反応のみ)/**Puppet Bulk**(entity はあるがコンポーネント OFF=低 CPU・LoRes に animate される・相互作用不可)/**Autonomous Bulk**(全コンポーネント稼働・"本物"の NPC・プレイヤー近傍に **40〜60 体**のみ)。実 AI **40 体**+高解像モデル **120 体**で画面上 **1 万体**を演出 | **プール+リサイクル**で低解像↔高解像を差し替え、プレイヤーに気づかせない。プールに所望モデルが無いと "popping"。**個体の identity は永続しない**(近づくたび別個体を割当てて構わない=群衆は交換可能) |
| **Cities: Skylines II 市民シミュ + Lifepath** 🔶 | 3 段の抽象度: **Citizen Instance**(物理的に歩く個体・上限 ~65k)/**Citizen Unit**(建物・交通に割当てられ"賑わい"を演出・~52万)/総人口 ~100万。目的地に到達不能な cim は despawn/teleport | 大多数の"市民"は**建物に束ねた統計プレースホルダ**で、物理移動する個体は上限内のみ。到達不能なら消して整合を保つ(破綻を"消去"で回避) |
| **RimWorld vs Dwarf Fortress** 🔶 | DF=世界を原子単位でフル・シミュ(歴史生成まで)。RimWorld=**AI Storyteller** が物語ペーシングのためにイベントを"注入"(原子単位で世界を回さない) | 2 哲学の対比: **フル・シミュ(高コスト・真の創発)** vs **ディレクタ/物語家(低コスト・但しイベントは著者付与で創発ではない)** |
| **The Sims 3 Story Progression / Sims 4 Neighborhood Stories** 🔶 | プレイヤーが操作**していない**世帯を、安価な**確率ルール**で進行(結婚・出産・転職・引越・死亡)。フル・シミュはしない。傾向は**性格特性で条件付け**(family-oriented は出産しやすい・子嫌いは絶対しない) | 背景世帯のライフイベントは**サイコロで付与**され、当人が"生きて"到達したものではない。★**特性で背景の分岐確率を変える** = Entry 8 が警告する「trait 条件付き背景」の実物 |

▶ **移せる知見(2-1)**:
- **AC Unity**: 群衆 LOD の本質は「背景個体の identity を捨てて交換可能にする」こと。**我々は逆に個体 identity(k\* の測定単位)を捨てられない** → 群衆 LOD の"タダ飯"は我々には半分しか来ない。
- **CS2**: 「物理個体は上限内、残りは建物に束ねた統計」= 前景/背景を **役割で分離**する実例。背景は"環境の賑わい"であり主役ではない。
- **RimWorld**: 背景を安くする道は「フル・シミュを諦めてイベントを注入する」= **創発を著者付与に置換**すること。k\* 研究は創発を測るのでこの置換は使えない。
- **The Sims**: **trait 連動の背景イベント確率**は、まさに我々が避けたい「生得優位の裏口」の完成形。反面教師として最も直接的。

### 2-2 交通・都市シミュのマルチレゾリューション

| 事例 | 仕組み | 境界整合(保存則) |
|---|---|---|
| **SUMO micro↔meso 協調**(Libsumo) | 同一ネットを micro(時間離散・車追従)と meso(イベント指向・キュー)で混在。汎用クロックで同期イベントを生成 | meso と micro で時間進行の原理が違う → **クロック module で同期**が必須 |
| **Aimsun / PTV Vissim ハイブリッド meso-micro** 🔶 | 境界ノードで上流 meso・下流 micro のように**動的モデルを切替**。micro→meso: 最後の micro turn の退出時刻を meso の進入時刻に。meso→micro: ネット進入と同じ gap-acceptance アルゴリズムで受け入れ | 越境時に**車両を生成も消滅もさせない**。到着時刻・順序を持ち越す=**保存則を明示ハンドオフ** |
| **MATSim**(activity-based・queue simulation) | 大規模を **queue-based mesoscopic**(リンクをキューで表現・車追従を解かない)で回し、co-evolutionary な日次再計画で個体の 1 日行程を最適化。individual は"行程プラン"として保持し交通流だけ粗く解く | **個体プランは全個体で保持**(消さない)しつつ**交通ダイナミクスだけ粗くする** = 「個体の history は精細・環境の解像度だけ落とす」分離の実例 |
| **Hybrid Traffic: Vehicle Loading at Meso-Micro Boundaries**(学術) | 境界での車両受け渡しの整合要件を体系化 | 整合は「ネット/経路選択の整合」と「境界での交通ダイナミクスの整合」の 2 層で要求される |

▶ **移せる知見(2-2)**: LOD 境界を跨ぐには **明示的なハンドオフ・プロトコルで保存則を守る**のが交通シミュの定石。個体を「背景→前景」に**昇格**させるなら、位置・記憶・drive ゲージ・履歴を**欠落も捏造もなく持ち越す**設計が要る(§4 Q4 に接続)。交通は"車両数と到着時刻"を保存したが、我々が保存すべきは"**個体の履歴の連続性**"。**MATSim の解法(個体プランは全保持・環境の解像度だけ落とす)は 2-4 の"背景=環境場"と同じ結論に別ルートで到達している** — LOD を掛ける対象は「個体」ではなく「個体が動く環境の解像度」であるべき、という示唆。

### 2-2b ヒステリシス — LOD 切替のちらつきをどう抑えるか(横断論点)
- **[事実]** ゲーム LOD は昇格と降格で**別閾値**を使うのが定石(例: 前景化は 35m 以内、背景化は 45m 超のように**バンドを設ける**)。単一閾値だと境界上で個体が毎 step 前景↔背景を往復(flicker)し、状態の作り直しコストと見た目/挙動の破綻を生む。AC Unity の "popping" はプール枯渇由来だが、根は同じ「切替の不連続」問題(2-1)。
- **[本シミュへの含意]** もし agent-LOD(静的でも動的でも)を入れるなら、**切替のヒステリシス幅**が新しい設計パラメータになる。そして **ヒステリシス幅は「どの個体がどれだけ精細に生きたか」を変える=k\* に効く隠れ因子**。決定論の観点でも、閾値往復のたびにモデルが変わると同一プロンプトが別 name のキャッシュに散る(multi-model-lod §7.2)。**ちらつき抑制と再現性・k\* 非交絡は同じ「切替を安定させよ」という要求に収束する**。

### 2-3 LLM マルチエージェント研究の計算配分(multi-model-lod §4.2 との**差分のみ**)

> §4.2 で既収: Generative Agents / OASIS / AgentScope / Project Sid / AgentTorch / AgentSociety。以下は**そこに無い新規**。

| 事例 | 計算配分の要点 | 本シミュとの距離 |
|---|---|---|
| **Concordia**(DeepMind, [arXiv:2312.03664](https://arxiv.org/abs/2312.03664), v2.0=NeurIPS2024 後) | **Game Master(GM)**が全エージェント行動を裁定する Entity-Component 構成。GM が「行動の妥当性判定・環境への反映」を一手に担う | GM は**背景を安く裁く seam になりうる**(背景は GM のナレーション解決だけで済ませ、個体 LLM を撃たない)。但し Concordia 自身は**前景/背景の差分計算を native には持たない**(未確認の範囲では均質) |
| **GATSim**(2025, [arXiv:2506.23306](https://arxiv.org/abs/2506.23306)) | 都市モビリティの生成エージェント。階層記憶(短期=当日の作業空間/長期=行動学習)+ planning/reactive 二経路 | 2025-26 の新事例。**reactive(安い反応)と planning(高い計画)を経路分離** = 我々の purpose LOD と同型。個体軸ではなく**認知経路軸**の LOD |
| **budget-aware / adaptive worker 割当**([OpenReview JMDCMf7mlF](https://openreview.net/forum?id=JMDCMf7mlF)・AgentCollab [arXiv:2603.26034](https://arxiv.org/pdf/2603.26034) 等) | 入力の複雑さで worker 数を動的配分/「小モデル既定→難所だけ大モデルに escalation」/trajectory 単位で「どのエージェントを呼ぶか」を最適化 | **全て複雑さ駆動の動的割当** = 呼数がラン時状態に依存 = **R1 が構造的に禁じる形**。我々にとっては"やってはいけない設計"の実例集(§4 Q4) |

▶ **移せる知見(2-3)**: 最新の計算配分研究はほぼ全て「**難しいところに動的にモデルを厚くする**」方向で、これは**呼数を状態依存にする=R1 違反**。Concordia の GM だけは「背景を裁定で安く済ます」静的 seam として参考になる。GATSim は「個体軸ではなく認知経路軸で LOD を切る」我々の purpose LOD の正当化。

### 2-4 平均場近似・集団力学による背景置換

| 手法 | 仕組み | k\*(個体創発)への含意 |
|---|---|---|
| **平均場近似 / 密度場**([mean-field dynamics 🔶](https://www.emergentmind.com/topics/mean-field-dynamics)・[arXiv:2101.09644](https://arxiv.org/pdf/2101.09644)) | 多数の相互作用個体を**平均量・経験分布(密度場)**で近似。個体を追わず場を回す | **大 N・稠密相互作用・交換可能性を仮定**して初めて厳密。個体異質性を消す=**世界改変者の分散を定義上消す**(compute-efficiency §4 の archetype と同結論) |
| **平均場ゲーム(MFG)**([arXiv:2107.04050](https://arxiv.org/abs/2107.04050)) | 価値関数 + 密度の連立 PDE。個体は"代表エージェント"に集約 | 個体の稀な逸脱を表現できない。マクロ量には強いが k\* には不可 |
| **場の 2 階層観**(collective=背景場が平均を条件付け / individual=場の中の個体動力学) | 背景を「場」、前景を「場の中で動く個体」として**分離**して扱う定式化 | ★**背景を"環境場"としてのみ使う**なら k\* を汚さない道がある(下記) |

▶ **移せる知見(2-4)**: 平均場は「背景個体**そのもの**を平均に潰す」なら k\* に致命的(archetype と同じ)。だが「背景を **前景が反応する環境場**(混雑密度・語彙普及率の場)として回し、個体は前景だけ」なら、**背景を候補者から外す代わりに交絡は生まない**。= 平均場は「世界改変者候補の削減」ではなく「**環境の安価な充填**」に使うのが唯一安全な用法。

### 2-5 動的 LOD(昇格/降格)と観測の一貫性

| 論点 | 事実 | 出典 |
|---|---|---|
| オープンワールドの streaming は一般に**非決定** | チャンクの load/unload と物理内部状態の順序が同期崩れ=決定論ロックステップは不可、rollback も困難 | 🔶 [mas-bandwidth](https://mas-bandwidth.com/choosing-the-right-network-model-for-your-multiplayer-game/) / [Box2D determinism](https://box2d.org/posts/2024/08/determinism/) |
| "観測されたものだけ計算"(observer effect の比喩) | 見ていない部分を計算しない=計算節約。だが**観測していない個体の歴史は書かれていない**。後で観測するとき"あり得た歴史"を**生成で捏造**する必要 | 🔶 [The Sims 的 persistence の議論](https://en.wikipedia.org/wiki/Persistent_world) |
| 決定論リプレイの原理 | 決定論操作は最小記録で verbatim 再生、非決定操作のみ詳細記録。スナップショットから再走 | 🔶 deterministic replay(VM 特許系) |

▶ **移せる知見(2-5)**: **動的昇格は「昇格した個体の過去」問題を必ず生む**。背景で安く回した個体を途中で前景に上げると、その個体の"それまでの人生"は薄い(or 無い)。もし背景から世界改変者が出るなら、その履歴は**後付け捏造**になり、k\* の観測対象(実際に生きられた軌跡)を壊す。決定論を保つには「昇格条件=記録済み状態の決定論関数」+「昇格後の LLM は llm_cache 固定」が要るが、**それを満たすと"背景も結局フル履歴が要る"=節約が消える**という矛盾に突き当たる(§4 Q4)。

### 2-6 先行例から抽出した 4 つの共通パターン(討議の下敷き)
1. **「個体を潰す」LOD と「環境を粗くする」LOD は別物**。archetype/平均場/AC 群衆は**個体**を潰して安くする(k\* に毒)。MATSim/CS2 の建物統計/平均場の"環境場"用法は**個体は保持し環境の解像度だけ落とす**(k\* に無害)。→ **我々が掛けてよい LOD は後者に限る**という仮説が、独立な複数分野から示唆される。
2. **背景を安くする実務は必ず「創発を著者付与に置換」している**。The Sims のサイコロ・RimWorld の Storyteller は、背景の出来事を**シミュレートせず注入**する。安さの源泉が"創発の放棄"である以上、**創発を測る研究では背景の安化に本質的な上限がある**。
3. **LOD 境界の整合は"保存則の明示ハンドオフ"で解く**(交通の meso-micro)。動的 LOD を入れるなら、越境で**個体の履歴を欠落も捏造もなく持ち越す**プロトコルが前提。これが無い動的 LOD は決定論も k\* も壊す。
4. **切替の安定化(ヒステリシス)・再現性(キャッシュ name)・k\* 非交絡は同じ要求に収束する** = 「**個体がどの解像度でどれだけ生きたかを、ラン間・k 間で不変に固定せよ**」。この 1 条件を満たせない LOD 案は、どの角度から見ても危険。

---

## §3 設計の選択肢空間 — 5 案と 4 象限評価

> 4 象限 = **コスト削減見込み / R1・決定論リスク / k\* 研究への交絡 / 実装工数**。★は本シミュ固有の急所。

| 案 | 中身 | コスト削減見込み | R1・決定論リスク | k\* への交絡 | 実装工数 |
|---|---|---|---|---|---|
| **(A) LOD なし=全員同格**(現状) | 発火予算のみ・全員同一モデル | 基準(発火 LOD で既に ~12倍。追加削減なし) | **なし**(既に R1 準拠・決定論担保済) | **なし** | ゼロ(導入済) |
| **(B) purpose LOD のみ** | reflect=大/deliberate=小・**全員一様** | 中(reflect 3.8% を大に振っても呼数の 92.7% は小。全体は小寄り+品質の厚み) | **なし**(全員同じ purpose 割当=k 非依存) | **なし**(個体差なし) | 小(既存 tiers seam。FleetLLM の tier 別 model 名対応拡張のみ) |
| **(C) 静的 agent-tier**(3 案: ①trait 由来 ②独立決定論 ③明示指定) | 前景個体=大/背景個体=小 or ルール。割当は初期化時固定 | 大(背景を 4b/ルールに落とせば呼あたりコスト減) | 低〜中(割当が固定・k 非依存なら決定論は保てる) | **割当方式で激変**: ①**致命的**(trait=生得優位を裏口注入=Entry 8) ②低(独立ストリームだが k\* は前景内でのみ) ③実験操作(明示指定=条件として明示) | 中(M3: "model_tier" stream + 合成ルータ) |
| **(D) 動的昇格降格** | 注目/活性で個体を前景↔背景に移動 | 大(注目個体だけ厚く。平時は薄く) | **高**(昇格=呼数がラン時イベント依存=k と相関しうる) | **高**(observer effect: 昇格個体の過去が薄い=履歴の後付け) | 大(昇格条件の決定論化+状態ハンドオフ+履歴リプレイ) |
| **(E) 背景の平均場置換** | 背景を個体でなく密度場/統計で回す | **最大**(背景個体数を場に畳む) | 中(場の更新を決定論化すれば可) | 個体潰し=**最大** / 但し"**環境場のみ**"に限れば**なし** | 大(場モデル + 前景との結合 + 忠実度検証) |

**表からの読み(結論ではなく観察)**:
- **左上(安全・低工数)= (A)(B)**。purpose LOD は "タダ飯" 側で、agent LOD の議論とは独立に進められる。
- **(C) は割当方式が全て**。同じ「静的 agent-tier」でも ①と②で k\* への毒性が正反対。Entry 8/plan の焦点はここ。
- **(D)(E) は削減が大きいほど k\*・R1 の危険が増す**という綺麗な反比例。削減効果と研究妥当性が正面衝突する領域。
- **(E) は"使い方"で毒にも薬にもなる唯一の案**: 背景個体を潰すと最悪、背景を**環境場**に限れば無害。

---

## §4 討議アジェンダ — ユーザーと Fable が決めるべき 5 問

> 各問に **[材料となる事実]** と **[選択肢]** を添える。**結論は出さない。**

### Q1. k\* は誰について測るのか — 全員か、前景のみか
- **[事実]** compute-efficiency Tier 3 は「階層化を採るなら**前景でのみ k\* を測り背景はマクロ環境の充填**」を採用条件に挙げる。multi-model-lod §0 も「k\* は同一 tier 内でのみ測る」。CS2 は物理個体=上限内・残りは建物統計と**役割分離**している(2-1)。現行 300 体で全員前景なら、そもそも選択の余地がない。
- **[選択肢]** (i) 全員前景=agent LOD 不採用、k\* は全数母集団で測る / (ii) 前景のみで k\* を測り背景は環境=N を稼ぐが**母集団が縮む**(統計検出力とのトレードオフ) / (iii) tier 内比較を既定にし tier 間は別実験扱い。
- **[未決の核]** 「前景だけで測った k\*」は「全数で測った k\*」の**代理として妥当か**。背景を除外した母集団で測る R²(k) は何を主張できるのか。

### Q2. 「世界を変える人が背景から出てくる」可能性を殺さない条件
- **[事実]** The Sims の背景世帯はライフイベントを**サイコロで付与**され、当人が生きて到達したものではない(2-1)。AC Unity の群衆は identity 非永続=**個体史を持たない**(2-1)。平均場/archetype は個体異質性を消す(2-4・compute-efficiency §4)。→ **背景に落とすと「そこから世界改変者が出る」経路が構造的に閉じる**。背景個体は定義上、逸脱の分散を持てない。
- **[選択肢]** (i) 背景→前景の**昇格経路**を開ける(=動的 LOD、Q4 と連動) / (ii) 背景は環境専任と割り切り、世界改変者候補は**最初から前景に固定** / (iii) 背景も稀にフル LLM を引く"**抽選**"を入れる(但し呼数変動=R1 注意)。
- **[未決の核]** 我々の研究仮説は「世界改変者は**生得か創発か**」。**創発説を検証したいのに背景を潰すと、創発の主要経路(無名から立ち上がる個体)を実験デザインで先に消す**ことにならないか。

### Q3. 割当の独立性 — trait 相関の裏口問題(Entry 8)
- **[事実]** Entry 8 / plan §結論3: **trait 由来の tier 割当は R²(k) に生得優位を注入=k\* 研究の自殺点**。The Sims は trait(family-oriented)で背景分岐確率を変える=まさに trait 条件付き背景の実物(2-1)。plan の本命は **trait 非依存・k 非依存の決定論割当**("model_tier" stream 1 本)。
- **[選択肢]** (i) 独立決定論割当(専用ストリーム 1 回・trait と無相関) / (ii) 明示リスト指定(config で誰が前景かを人手指定=実験条件として透明) / (iii) trait 連動は「**それ自体を操作した実験条件**」としてのみ許可(生得性の効果を測る実験)。
- **[未決の核]** 「独立決定論割当」でも、**前景に多くの計算を割く=前景個体が世界改変者になりやすくなる**なら、割当自体が Y_external の分散を作る。割当が trait と無相関でも、**計算量そのものが交絡因子**になりうる。これは trait 相関とは別の第二の裏口。

### Q4. 動的昇格は決定論と R1 に耐えるか
- **[事実]** オープンワールド streaming は一般に非決定(2-5)。budget-aware LLM 文献は全て**複雑さ駆動の動的割当**=呼数がラン時状態依存(2-3)=R1 が禁じる形。observer effect: 昇格個体の過去は薄く**履歴の後付け捏造**が要る(2-5)。交通の meso-micro 境界は**保存則の明示ハンドオフ**で越境を整合(2-2)。決定論リプレイは「昇格条件=記録済み状態の決定論関数」なら再走可能(2-5)。
- **[選択肢]** (i) 動的 LOD **不採用**(静的固定のみ) / (ii) 昇格条件を決定論化 + **背景も最初からフル履歴**(=節約が消える矛盾を受容) / (iii) 昇格を「**観測のためのリプレイ**」に限定(本ランは軽く回し、注目個体だけ後から高精細で再走=履歴は本ランで確定済みなので捏造なし)。
- **[未決の核]** (iii) の「軽く回して後で高精細再走」は、**本ランと再走で軌跡が一致する保証**(同じ llm_cache・同じ乱数)があれば決定論・R1 を守れる可能性がある唯一の動的案。だが「軽い本ラン」が背景を薄く回すなら、その薄い軌跡が"確定した歴史"になる=結局 (ii) の矛盾に戻る。**動的 LOD が節約と妥当性を両立できる余地は本当にあるのか**を詰める必要。

### Q5. LOD 導入の判断基準 — どの規模から必要か(300 体では不要? 3000 体では?)
- **[事実]** 現行実測: 発火 4.1〜11.4%(~12倍削減済)、mock 300体×100日=**132 分**、実 LLM 20体×7日=**95 分 / 1,635 呼**(compute-efficiency §1)。300体×100日 = **692,859 呼**(all-local なら限界費用 ~$0、multi-model-lod §5)。先行の大規模例: AgentScope 10k体=5.6 分/4台(小モデル)、OASIS 100k体=3h/A100×5(compute-efficiency §2)。**300 体は先行大規模例に比べ極小**。未回収の"タダ飯"= speculative decoding・prefix cache 実機確認・出力上限右サイズ化(compute-efficiency Tier 1)。
- **[選択肢]** (i) 300 では agent LOD **不要**、Tier 1 推論高速化 + purpose LOD で足りる / (ii) 3k〜10k で **GPU-time が律速化**したら agent LOD / 平均場を後段レバーに / (iii) 閾値を `bench.py` 実測(tok/s・GPU 充填率・壁時計)で**定量的に引く**。
- **[未決の核]** 「規模が上がれば agent LOD が要る」は本当か、それとも「**規模が上がっても Tier 1 + purpose LOD + 分散配線(AgentScope 型 actor 並列)で足りる**」のか。先行 100万体例は**全て小モデル均質 + 発火制御 + 分散**で達成しており、**個体軸 LOD を使っていない**点は重い示唆。

---

## §5 出典

**ゲーム群衆・オフスクリーン LOD(🔶=二次)**
- [GDC Vault "Massive Crowd on Assassin's Creed Unity: AI Recycling"](https://gdcvault.com/play/1022411/Massive-Crowd-on-Assassin-s) / 🔶 [Bulk System 解説](https://www.toolify.ai/ai-news/revolutionary-crowd-system-in-assassins-creed-unity-2133256)(3 bulk・40 実 AI/120 高解像/1万体・popping)
- 🔶 [Cities: Skylines II Citizen Simulation & Lifepath(公式)](https://www.paradoxinteractive.com/games/cities-skylines-ii/features/citizen-simulation-lifepath) / 🔶 [Citizens — CS Wiki](https://skylines.paradoxwikis.com/Citizens)(instance 65k・unit 52万)
- 🔶 [RimWorld vs Dwarf Fortress(AI Storyteller vs 原子シミュ)](https://www.gamedeveloper.com/design/how-i-rimworld-i-fleshes-out-the-i-dwarf-fortress-i-formula)
- 🔶 [The Sims Story Progression — Sims Wiki](https://sims.fandom.com/wiki/Story_progression) / 🔶 [Sims 4 Neighborhood Stories](https://simscommunity.info/2021/12/01/introduction-to-neighborhood-stories-in-the-sims-4/)(trait 条件付き背景イベント)

**交通・都市マルチレゾリューション**
- 🔶 [Aimsun Next Hybrid Meso-Micro Simulator(公式マニュアル)](https://docs.aimsun.com/next/22.0.2/UsersManual/HybridSimulator.html)(境界の車両受け渡し・退出時刻→進入時刻)
- [Hybrid Traffic Simulation: Vehicle Loading at Meso-Micro Boundaries(学術)](https://www.researchgate.net/publication/254398938_Hybrid_Traffic_Simulation_Models_Vehicle_Loading_at_Meso_-_Micro_Boundaries) / 🔶 [PTV Vissim mesoscopic/hybrid](https://blog.ptvgroup.com/en/technologyplus/mesoscopic-and-hybrid-simulations-in-ptv-vissim/)
- 🔶 [MATSim(activity-based / queue simulation・公式)](https://www.matsim.org/)(個体プランは全保持・交通流のみ mesoscopic)

**LLM マルチエージェント計算配分(§4.2 差分)**
- [Concordia(DeepMind)— arXiv:2312.03664](https://arxiv.org/abs/2312.03664) / [github](https://github.com/google-deepmind/concordia)(Game Master・Entity-Component)
- [GATSim — arXiv:2506.23306](https://arxiv.org/abs/2506.23306)(生成エージェント都市モビリティ・階層記憶・reactive/planning 分離)
- [Anytime Verified Agents(adaptive compute)— OpenReview](https://openreview.net/forum?id=JMDCMf7mlF) / [AgentCollab(model escalation)— arXiv:2603.26034](https://arxiv.org/pdf/2603.26034)(=複雑さ駆動の動的割当=R1 が禁じる形)

**平均場・集団力学**
- 🔶 [Mean-Field Dynamics 概説](https://www.emergentmind.com/topics/mean-field-dynamics) / [Mean-field for Stochastic Population Processes with Heterogeneous Interactions — arXiv:2101.09644](https://arxiv.org/pdf/2101.09644) / [Model-Based Multi-Agent Mean-Field RL — arXiv:2107.04050](https://arxiv.org/abs/2107.04050)

**動的 LOD・決定論・観測の一貫性(🔶=二次/比喩)**
- 🔶 [Choosing the right network model(streaming は非決定)](https://mas-bandwidth.com/choosing-the-right-network-model-for-your-multiplayer-game/) / 🔶 [Box2D determinism](https://box2d.org/posts/2024/08/determinism/) / 🔶 [Persistent world — Wikipedia](https://en.wikipedia.org/wiki/Persistent_world)

**リポジトリ内(根拠の中心)**
- [`docs/research/multi-model-lod.md`](multi-model-lod.md) §0/§4/§7 / [`docs/plans/multi-model-lod.md`](../plans/multi-model-lod.md) M3・OPEN#1
- [`docs/research/compute-efficiency.md`](compute-efficiency.md) Tier 3・§4(archetype 非推奨)・§1(実測発火率)
- 実装: [`src/society/cognition/lod.py`](../../src/society/cognition/lod.py) / [`drive.py`](../../src/society/cognition/drive.py) / [`routine.py`](../../src/society/cognition/routine.py)
- [`docs/log/devlog.md`](../log/devlog.md) Entry 8(trait 由来 tier 割当=生得性の裏口注入への懸念)

> 正直な記録: (i) ゲーム技術の細部(AC Unity の bulk 数・CS2 の instance 上限)は GDC 講演タイトル + 二次解説からで、**細部の数値は 🔶=一次スライド未確認**。(ii) Concordia が前景/背景の差分計算を native に持つかは**未確認**(abstract 範囲では均質)。(iii) 平均場を「環境場のみに使えば k\* を汚さない」は本書の**論理的整理**であって、LLM 社会シミュでの実証例は**見当たらず=要検証**。(iv) 「動的 LOD が節約と妥当性を両立できるか」(Q4)は本書でも未解決の核として残す。
</content>
</invoke>
