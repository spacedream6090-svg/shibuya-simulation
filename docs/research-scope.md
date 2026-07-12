# 研究スコープ:分野選定と実装重要度 (v0.1 — 仮説・チューニング前提)

> 本シミュレーションが跨ぐ学際分野の選定と、**実装/grounding の重要度分類**。
> ⚠️ **これは仮説**。誤っていても、シミュを回す → feedback → 分野の追加/削除 → チューニング、で版を上げる(versioned)。
> 設計正典は [design.md](./design.md)。世界2.0 原フレームは [sekai2.0-framework.md](./sekai2.0-framework.md)。文献は [references.md](./references.md)。

## 重要原則:世界2.0 をどう使うか(指紋問題の回避)
『世界2.0』は「**設計者が世界を作る/立ち上げるレシピ**」。本プロジェクトの中核は「**設計者の指紋を最小化し、創発を観る**」。素朴にレシピを実装(ヒエラルキー確立・進歩実感の付与 等を仕込む)と、観たい創発を **injection** してしまい研究が無効化する。

→ 世界2.0 は **2つの役割でのみ**使う(振る舞いは hardcode しない):
1. **Affordance(基盤の"可能性")**: 「可能」にするが「強制」しない(信用が可視化*できる*、ルールを*作れる*)。→ `actions/` `world/` レジストリ。
2. **Observable(観測項目)**: 世界2.0 が「効く」と予測する機構が**実際に創発したか**を研究者frameで測る。→ `observer/measure`。

### 補足:世界2.0 は「世界(基盤)の構築ガイド」として正式採用(2026-06-30)
正しい線引きは **「ステージ(世界)を作る」= 世界2.0 歓迎 / 「劇(創発)を台本化する」= 禁止**。世界2.0 の項目の大半は基盤構築ガイドであり injection ではない。3つの注意:
- **注意1**: リアルな環境 ≠ リアルな社会(Moltbook)。環境の忠実度は創発の妥当性を保証しない。
- **注意2(2026-06-30 修正 — 旧「視空間より生態系優先」を撤回)**: **視空間 = 社会の"構造/器"**(空間構造・ランドマーク=要点・存在/アイデンティティ)であり **load-bearing**。**生態系 = コミュニティの"動態"**(価値・役割・信用が動く)。両方を two-layer として構築する。ただし**描画忠実度(顔のグラフィック等)だけは別物で低優先**。設計対応: 視空間→`world/space`、生態系→`actions`/経済+`observer`。
- **注意3**: 目標は「創発が"可能"になる十分なリアルさ」であって「最大忠実度の再現」ではない(過剰忠実 = 設計者の仮定 = 指紋増)。

## 重要度の定義
- **P0** — 第1実験(M1 + k* + エンジン)の必須(load-bearing)。最初に grounding。
- **P1** — 重要・第2波。主要 affordance/機構を grounding。
- **P2** — framing/応用・保留。深い grounding は後回し(着想・語り・投下先)。

## 分野マップ

### Object(観察対象の現象)
| 分野 | 重要度 | 役割 | 担うもの / 世界2.0対応 | seam |
|---|---|---|---|---|
| 性格・動機づけ心理学 | **P0** | 機構ground | 改変者の内部状態(NFC/効力感/統制/当事者意識) | factors |
| 集合行為・社会運動論 | **P0** | 機構ground | 個人の不満→命名→集団化 / 立ち上げ手順 | factors/update, labeling |
| 文化進化・社会言語学 | **P0** | 機構ground | ラベル創発・semantic drift・少数派tipping | labeling, propagation |
| ネットワーク科学・拡散理論 | **P0** | 機構ground | 非ブロードキャスト伝播・採用曲線 | world/perception, propagation |
| 意見ダイナミクス(形式モデル) | P1 | bridge | 合意/分極/drift(bounded confidence) | propagation, observer |
| 組織社会学・社会階層 | P2 | observable | ヒエラルキーの創発(世界2.0「階層」) | observer |

### Method(方法・レンズ)
| 分野 | 重要度 | 役割 | 担うもの / 世界2.0対応 | seam |
|---|---|---|---|---|
| 複雑系・統計物理・自己組織化 | **P0** | 分析frame | k*相転移 / 基本3要素(自律的・有機的・分散的) | engine/metrics, analyze |
| マルチエージェントAI・ABM・メモリ・**MASフレームワーク** | **P0** | 実装(+再利用) | generative agents・LOD・大規模ABM。**既存FW(Concordia/AgentScope/OASIS/Mesa)の活用**で10日ビルドを de-risk | 全体, agents, cognition, engine |
| 計測・心理測定・LLM-judge | **P0** | 観測 | 構成概念の事後測定・信頼性 | observer/measure |
| 認知科学(二重過程・metacontrol) | P1 | bridge | LOD正当化・思考頻度=主体性 | cognition/lod |
| **LLM/AI を社会エージェントとして**(バイアス/忠実度/RLHF/モデル選択) | **P0** | validity gate | train-test汚染・RLHF が対立/世界改変を抑圧・sycophancy/conformity・silicon sampling 忠実度。**モデル選択(base/instruct/uncensored)は実験変数**、k と交互作用しうる | llm/*, cognition, observer/measure |

### 経済・制度・基盤(世界2.0 が強く引く)
| 分野 | 重要度 | 役割 | 担うもの / 世界2.0対応 | seam |
|---|---|---|---|---|
| 制度経済学・ガバナンス(Olson/Ostrom) | **P0** | 機構ground+affordance | 集合行為・公共財・フリーライド / ルールとペナルティ | actions, factors/update |
| プラットフォーム/市場経済学・メカニズムデザイン | P1 | affordance | 生産者/消費者・マッチング・流動性・ネットワーク効果 | actions, world |
| 信頼・評判・社会関係資本 | P1 | affordance+observable | 信用の可視化 | actions, observer |
| 行動経済学・モチベーション・ゲーミフィケーション ⚠️ | P2 | affordance/observable限定 | 熱中させる仕掛け5(フロー・変動報酬) ※injection注意 | (慎重に) |

### 生命・ビジョン / 応用
| 分野 | 重要度 | 役割 | 担うもの / 世界2.0対応 | seam |
|---|---|---|---|---|
| 人工生命・情報生命(open-ended evolution) | P1 | framing+affordance | 生命的創発・開放アクション空間 / 自律的・有機的・分散的 | vision全体, actions |
| 安全保障/都市/社会制度/未来予測 | P2 | framing | 投下先・デモ設計 | (語りのみ) |

### 世界2.0 分野群(第2フェーズ 2026-07-02, 全30分野を均等 exhaustive でリサーチ済)
> 承認プラン golden-purring-dijkstra に基づく追加リサーチの成果。詳細は [lit/README](./lit/README.md) 群①〜④。
#### ①substrate/妥当性
| 分野 | 重要度 | 役割 | 担うもの / 世界2.0対応 | seam |
|---|---|---|---|---|
| 建築・都市計画(Lynch 5要素) | **P0** | 基層+観測 | 視空間=社会構造。landmark を軌跡から創発・事後測定(head/tail) | world/spatial, observer, viz |
| 社会存在論(Searle / Harari) | **P0** | 哲学的接地 | 象徴レイヤー・制度創発「X counts as Y」= 世界改変の定義 | world/symbolic, labeling |
| 環境・知覚心理(Tolman/Gibson) | **P0** | 設計原則接地 | 不完全な個体別認知地図 + affordance 知覚 | agents/cognition, world/spatial |
| 生態学(keystone/carrying capacity) | P1 | 観測レンズ | 生態系=コミュニティ動態。keystone=改変者アナログ | world/ecology, resource, observer |
| 経済 affordance(両面市場/評判/メカニズムデザイン) | P1 | affordance | cold-start=社会化ブートストラップ / 評判=信頼レイヤー | world/resource, social-network |
#### ②engagement(⚠️injection 注意)
| 分野 | 重要度 | 役割 | 担うもの / 世界2.0対応 | seam |
|---|---|---|---|---|
| 動機づけ(SDT/flow) | P1 | 機構ground | 自律/有能感/関係性=充足**可能**な affordance | factors, state-update |
| 行動デザイン(Fogg/nudge) | P1 | 診断+affordance | B=MAP。改変者=環境設計者を観測 | actions, cognition |
| ゲーミフィケーション | P1 | ⚠️交絡register | 過正当化=内発改変を歪める→既定off・実験変数化 | observer, config |
| 行動心理(Skinner 強化) | P1 | cheap tier 行動則 | 結果 affordance のみ。variable-ratio=依存機構 | state-update, actions |
| マーケ・消費者行動(Rogers 普及) | P1 | 観測 | 採用者カテゴリ=tail 実証版 / オピニオンリーダー=keystone | labeling, network, observer |
| ビジネスエコシステム(Moore/Iansiti) | P1 | 観測 | keystone orchestrator=改変者の組織版 | collective-action, social-network |
#### ③build・viz + Part B / ④哲学
| 分野 | 重要度 | 役割 | 担うもの / 世界2.0対応 | seam |
|---|---|---|---|---|
| PLATEAU/3DCG 可視化(Part B) | **P0** | 成果物 | sim⇄viz 疎結合 I/F。LLM推論と描画を分離。渋谷=商用可 | viz, engine/output |
| 分散システム・actor model | **P0** | 実装基盤 | actor 並列=スケール中核。非決定性 vs 多seed再現の決定化 | engine, infra |
| ゲームデザイン(MDA/emergent) | P1 | 設計哲学 | emergent gameplay=no-fingerprint の工学版。HCI/サービス同族 | actions, world, design |
| 価値論(axiology) | P1 | 哲学的接地 | 価値は関係から創発=新価値樹立=世界改変 | world/symbolic, observer |
| システム哲学(GST/Bertalanffy) | P1 | メタ枠組み | equifinality=k*問い / feedback=k / autopoiesis=anti-collapse | complexity, engine, meta |

## P0 セット(最初に grounding する8分野)
性格動機心理 / 集合行為・社会運動 / 文化進化・社会言語学 / ネットワーク拡散 / 複雑系・自己組織化 / マルチエージェントAI・ABM / 計測・心理測定 / 制度経済学・ガバナンス。
**第2フェーズで P0 昇格**: 建築・都市計画(Lynch)/ 社会存在論(Searle)/ 環境・知覚心理(Gibson)/ PLATEAU可視化 / 分散システム・actor。

## novelty の再定義(2026-06-30, MASリサーチ後)
OASIS(100万体)・AgentSociety(1万体)が既に大規模を達成済み。よって **「規模」単体は差別化ではない**。我々の novelty = **①世界改変者/agency の創発という研究の問い + ②k* 相転移の測定 + ③崩壊(意味収束・慣性)を防ぐ機構(LOD/memory/感受性)**。規模は必要インフラ(既存FWで到達)。GPU 必然性も「リッチ認知を保った大規模 + k掃引×seed の多数フルラン」で論じる。
**④検証可能性(2026-06-30 追加)**: この分野の中核的未解決問題は validation(多くが believability/zero-shot 依存で operational validity を示せない)。我々の反証可能な再定式化(分散分解・k*)+ 観測者frame測定 + 指紋最小化は、その直接の回答 = 「検証可能な創発」。これが最大の差別化軸。

## エンジン構築方針: build-vs-reuse(2026-07-01 精読後の暫定結論)
精読(Concordia / AgentScope / OASIS / Mesa)の結論: **単一FWで「リッチ認知 × 大規模」を両立するものは存在しない**(各FWが片側を選ぶ)。この空白こそ我々の thesis。
- **Concordia**(CC-BY/Apache): 認知が最良(component型 agent、Game Master が grounded world state=money/votes/resources を管理、March&Olsen の**非最大化**=指紋最小と親和、連想記憶)。だが**スケール非対応**(batch/並列なし、100+/1000step で prohibitive)。空間都市の例なし。
- **AgentScope**(Apache): **スケール最良**(actor 分散・自動並列・vLLM 多モデル fleet=8×8B/2×70B/1×176B per device、1M=12分/4台)。認知は薄い(2 LLM 呼/round)、環境は汎用。
- **OASIS**: スケール実証(async+vLLM+GPUマネージャ+time-engine)。SNS ドメイン特化。
- **Mesa**: 軽量 Python ABM 土台(scheduler/grid/datacollector)。LLM 無し。
→ **暫定方針(要合意)**: 単一FW採用せず **hybrid**。認知(熟考tier)= Concordia/Generative Agents 借用、スケール/fleet = AgentScope/OASIS 様式、安価tier = Mesa的/自前 SoA、**LOD が両者を橋渡し**。world/factors/labeling/observer は自作(どのFWも非提供)。
- 具体2案(P0 skeleton 着手時に確定): **(A)** Concordia 基盤にスケール層を足す / **(B)** 自前 lean core + 各種様式借用(+熟考tierに Concordia 部品)。

## 計算予算の現実(2026-07-01, OASIS 実測ベース)
OASIS 実測: **1M体×1step=18h/A100×27**、**100k体×1step=3h/A100×5**(小モデル1呼出/step + 確率的活性化)。我々は **A5000×7(A100より弱) + リッチ認知(熟考・memory) + k掃引×seed の多数フルラン**。
→ **現実的な本番規模は ~1,000〜10,000体。100k+ は非現実的。LOD は必須(オプションでない)。**
→ 規模ラダー(design.md §6)の「本番=フル規模」は**数千〜1万**を指す。この数字は実測で更新する。

## チューニング方針
仮説(本スコープ + 世界2.0)を立てて回し、観測 feedback で分野を追加/削除し版を上げる。各版は本ファイルで `vX.Y` 管理。
