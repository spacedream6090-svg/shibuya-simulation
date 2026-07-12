# コミュニティ検出とその時間発展 — 後処理パイプラインのための文献調査

作成: 2026-07-11 / 担当: リサーチ(Opus)/ コード変更なし・読み取りのみ

## この文書の目的

ユーザーの要望:

> 無理に組織を作らせず、**自然に形成されたコミュニティの動き(誕生・成長・合流・分裂・消滅)と構造を観察・分析できるようにしたい**。実装は後処理(ランの L1 イベントログを読むスクリプト)で行う。networkx>=3.2 は既存依存。決定論(同一入力→同一出力)が絶対条件。

本稿は、そのための(1)コミュニティ検出手法の比較、(2)時間発展の追跡、(3)構造の測度、(4)多層(異種エッジ)の扱い、(5)生成エージェント系論文での観測手法、(6)創発集団の「達成」の測定、を文献で裏付けたうえで、各論点に **本プロジェクトへの適用推奨(networkx の具体関数・パラメータ・決定論の担保まで)** を付す。最後に L1 → エッジ重み → 窓分割 → 検出 → ライフサイクル追跡 → 測度、の推奨パイプラインを擬似コードで示す。決定は Fable/ユーザーが行う前提の「素材」である。

**先に結論(3行)**
1. **決定論を最優先するなら、検出の正準器は「seed 不要で決定的な手法」**——既存 `measure.communities()`(自作の決定論 label propagation)を基準器に据え、モジュラリティ視点の交差確認として `networkx.louvain_communities(..., seed=固定)` を併走させるのが最も安全。**networkx の Leiden はネイティブ実装が無く backend(cugraph)専用**なので、Leiden を真に使うなら `leidenalg`/`igraph` の別依存が要る(後述)。
2. **時間発展は「窓ごとに検出 → 窓間を Jaccard でマッチング → Palla 2007 のライフサイクル分類(誕生/成長/合流/分裂/消滅)」** が標準(instant-optimal / detect-then-match 系)。決定論と相性が良い。
3. **異種エッジ(対面/DM/SNS/イベント共参加/組織所属)は、まず「重み付き合成1層」で検出**するのが N<300 の実務標準。ただし **組織所属(会社・学校)は検出グラフに混ぜず、検出された自然コミュニティと突き合わせる「参照分割」として別扱い**にする——これがユーザーの「無理に組織を作らせず、自然形成を観る」という要望の肝。

---

## 1. コミュニティ検出手法の比較(Louvain / Leiden / LPA / greedy modularity)

### 1.1 networkx 3.x の関数マップ(アクセス日 2026-07-11, networkx 3.6 系ドキュメント)

`networkx.algorithms.community` 名前空間([Communities リファレンス](https://networkx.org/documentation/stable/reference/algorithms/community.html)):

| 関数 | seed 引数 | weight | resolution | 有向対応 | 決定論性 |
|---|---|---|---|---|---|
| `louvain_communities(G, weight='weight', resolution=1, threshold=1e-07, max_level=None, seed=None)` | あり | ○ | ○(既定1) | ○(有向モジュラリティ) | **seed 固定で再現**(ノード順の random shuffle をシードで固定) |
| `leiden_communities(...)` | あり | ○ | ○ | (backend 依存) | **ネイティブ実装なし=backend 専用**(cugraph 等) |
| `label_propagation_communities(G)` | **なし** | 使わない | なし | **無向のみ**("Not implemented for directed graphs") | **決定的**(半同期 LPA、彩色で更新順を固定) |
| `asyn_lpa_communities(G, weight='weight', seed=None)` | あり | ○ | なし | 実質無向 | seed 固定で再現(**確率的**) |
| `greedy_modularity_communities(G, weight=None, resolution=1, cutoff=1, best_n=None)` | **なし** | ○ | ○ | (無向前提、有向は未確認) | **RNG 不使用=構造的に決定的**(ただしタイ処理は挿入順・版依存) |
| `modularity(G, communities, weight='weight', resolution=1)` | — | ○ | ○ | ○ | **決定的**(分割を与えれば一意) |
| `partition_quality(G, partition)` | — | — | — | — | 決定的(coverage, performance を返す) |

- `louvain_communities` は **有向・重み付きの双方に対応**し、`resolution<1` で大コミュニティ寄り・`>1` で小コミュニティ寄り。ドキュメントは「ノードを考慮する順序が最終結果に影響する。順序付けは random shuffle で行う」と明記=**seed 固定で再現**([louvain_communities ドキュメント](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.louvain.louvain_communities.html))。ただし「一部 backend は seed を無視する(例: cugraph)」との注記あり。
- `leiden_communities` は **「デフォルトの NetworkX 実装を持たず、cugraph 等の backend でのみ実行可能」** と明記されている([leiden_communities ドキュメント](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.leiden.leiden_communities.html))。→ **純 CPU・決定論の後処理では networkx 経由の Leiden は現実的でない**。Leiden を使うなら `leidenalg`(python-igraph)を直接呼ぶ(seed で再現可能)。

### 1.2 (a) 決定論性

- **`label_propagation_communities`(半同期 LPA, Cordasco & Gargano 2010)は seed 不要で決定的**。ノードを彩色して更新順を固定するため、同一グラフなら常に同一結果。**本プロジェクトの `measure.communities()` はこれと同系の自作決定論 LPA**(id 昇順更新・タイ時は現ラベル保持→最小ラベル、community_id を最小メンバ id に正準化)で、外部乱数を一切使わない=最も強い決定論。
- **`louvain_communities` / `asyn_lpa_communities` は乱数を使うが、`seed` 固定 + networkx バージョン固定 + グラフ構築順の固定**で再現できる。注意点:
  - グラフを **set 由来の非決定的順序で構築すると、シャッフル入力が変わり結果がぶれる**。→ **ノードを id 昇順、エッジをソート順で add する**こと(決定論の実務上の要)。
  - **networkx の版が変わるとアルゴリズムが変わりうる**。→ 環境で **networkx を厳密ピン**(`>=3.2` だけでなく実際の版を固定)。
  - backend(cugraph 等)は seed を無視しうる=CPU の純 networkx で回す。
- **`greedy_modularity_communities` は RNG 不使用**なので原理的に決定的だが、モジュラリティ利得のタイ処理がノード/エッジ挿入順・実装版に依存する。決定論を担保するなら **構築順を固定**すれば同一入力→同一出力。

### 1.3 (b) 小規模ネットワーク(N=20〜300)での信頼性

- **モジュラリティ最大化の縮退(degeneracy)**: 小〜中規模でも「最適に近い分割が指数的に多数存在し、それらが互いに大きく異なる」ことが知られる(Good, de Montjoye, Clauset 2010, PRE、[arXiv:0910.0165](https://arxiv.org/abs/0910.0165))。→ **単一分割を「真の構造」と断定しない**。複数 seed・複数窓で安定な境界だけを信頼する。
- **LPA の不安定性**: LPA は小・疎グラフで「巨大1コミュニティに潰れる」「多数の孤立点に散る」など退化しやすい(Raghavan, Albert, Kumara 2007 の原法は同期更新で振動)。半同期版・自作決定論版は振動を抑えるが、**疎な週次窓では退化しうる**。→ N が小さい初期ラン(20〜80)では、モジュラリティ系(Louvain seeded / greedy)の方が「解釈できるコミュニティ数」を返しやすい。
- **推奨運用**: N<50 では 1 ノードの移動で指標が大きく動くため、**必ず n(ノード数)と併記し、過剰解釈を避ける**。窓をまたいだ安定性(§3 の membership Jaccard)を信頼性の代理指標にする。

### 1.4 (c) 重み付き・有向対応

- 重み付き: `louvain` / `asyn_lpa` / `greedy_modularity` / `modularity` は `weight` を受ける。`label_propagation_communities` と自作 LPA は**重みを使わない**(隣接の有無のみ)。→ 重みを効かせたいなら Louvain 系。
- 有向: `louvain_communities` は有向モジュラリティに対応。`label_propagation_communities` は **無向専用**。→ **コミュニティ「所属」は無向(対称化)グラフで、影響・流れの「方向」は別途 PageRank 等で**測るのが実務的(§3)。

### 1.5 (d) resolution limit 問題

- **Fortunato & Barthélemy 2007**(PNAS, [論文](https://www.pnas.org/doi/10.1073/pnas.0605965104)): モジュラリティ最大化は、ネットワーク全体の規模で決まるスケール以下の**小コミュニティを検出できず、大きな塊に併合**してしまう(resolution limit)。Louvain・greedy modularity は本質的にこれを抱える。
- **Leiden の改善**(Traag, Waltman, van Eck 2019, Scientific Reports 9:5233、[論文](https://www.nature.com/articles/s41598-019-41695-z)): Louvain は「内部が非連結なコミュニティ」を返しうる(報告では最大 25% が悪接続・最大 16% が非連結)。Leiden は**精緻化フェーズで各コミュニティの連結性を保証**し、resolution limit と非連結問題を緩和、再現性も改善。
- 実務的緩和: `resolution` パラメータを掃引して、検出される粒度の妥当帯を探す(小さいコミュニティを見たいなら resolution を上げる)。**resolution 感度は必ず報告**する。

### 1.6 本プロジェクトへの適用推奨(§1)

- **正準検出器 = 既存 `measure.communities()`(自作決定論 LPA)を基準に据える**。外部乱数ゼロ・community_id 正準化済みで、**「決定論が絶対条件」に最も忠実**。まずこれを窓別検出に流用する。
- **モジュラリティ視点の交差確認として `louvain_communities(G, weight='weight', resolution=γ, seed=SEED)` を併走**。γ は既定 1 から掃引、SEED はラン設定の定数として config に記録。**決定論担保の4点セット**:(i)ノードを id 昇順で add、(ii)seed 固定、(iii)networkx を厳密ピン、(iv)community_id を最小メンバ id に正準化(既存踏襲)。
- **Leiden は networkx では backend 専用**。連結性保証が研究上必要になった段階で `leidenalg`(igraph)を別依存として導入する(seed 再現可)。現時点では必須ではない。
- `greedy_modularity_communities` は「コミュニティ数を自動で決める決定的な選択肢」として有用だが、タイ処理の版依存に注意(構築順固定で回避)。
- **手法の一致度そのものを指標化**する:LPA と Louvain で境界が一致するノードだけを「頑健なコミュニティコア」とみなすと、縮退・不安定性への保険になる。

---

## 2. 時間発展コミュニティの追跡(窓間マッチングとライフサイクル)

### 2.1 標準アプローチ:detect-then-match(instant-optimal)

動的コミュニティ検出の分類は Rossetti & Cazabet 2018(ACM Computing Surveys 51(2)、[PDF](https://giuliorossetti.github.io/assets/pdf/papers/CSUR18.pdf))が整理:(i)**Instant-optimal**(各時刻で独立に検出 → 窓間をマッチング)、(ii)Temporal Trade-off、(iii)Cross-Time。**決定論・後処理・可解釈性の観点では (i) が最適**——各窓の検出が決定的で、マッチングも決定的にできる。

- **窓間マッチング = Jaccard 類似度**。時刻 t のコミュニティ集合 C_i と t+1 の C_j について J(C_i, C_j) = |C_i ∩ C_j| / |C_i ∪ C_j| を計算し、**最大 Jaccard かつ閾値 τ 以上**なら「同一の動的コミュニティ」とみなす(標準的に τ=0.3〜0.5)。複数の Web ソースがこの手続きを標準として記述([Community Evolution, Springer](https://link.springer.com/rwe/10.1007/978-1-4939-7131-2_223))。

### 2.2 ライフサイクル分類(Palla et al. 2007 系譜)

- **Palla, Barabási, Vicsek 2007「Quantifying social group evolution」**(Nature 446:664–667、[ResearchGate PDF](https://www.researchgate.net/publication/6412158_Quantifying_social_group_evolution)): 携帯通話網と共著網で動的コミュニティを解析し、**誕生(birth)・消滅(death)・成長(growth)・縮小(contraction)・合流(merging)・分裂(splitting)** という**イベント語彙**を確立(原論文の検出は clique percolation + 重なりベース対応付けだが、**イベント分類の枠組みが標準語彙として定着**)。
- **イベント判定ルール**(Jaccard マッチングの上で):
  - **誕生**: t+1 に存在するが t の誰ともマッチしないコミュニティ。
  - **消滅**: t に存在するが t+1 の誰ともマッチしない。
  - **成長/縮小**: マッチしたペアで、サイズが閾値超で増/減。
  - **合流**: t の 2 個以上が t+1 の 1 個へマッチ。
  - **分裂**: t の 1 個が t+1 の 2 個以上へマッチ。
- 関連手法: GED(Group Evolution Discovery, Bródka ら)、estrangement confinement(Kawadia & Sreenivasan 2012, [arXiv:1203.5126](https://arxiv.org/pdf/1203.5126))なども同枠組み。

### 2.3 安定性・「動的コミュニティ id」の付与

- マッチしたコミュニティを**時系列でチェーン**にまとめ、チェーンごとに **`dynamic_community_id`** を割り振る(そのコミュニティの一生を1本の線として追える)。
- **メンバシップ Jaccard の系列**が、そのまま「安定性」の測度になる(§3.5)。

### 2.4 本プロジェクトへの適用推奨(§2)

- **窓 = 週次(7日 = 7×144 = 1008 step)を既定**にしつつ、**小 N の初期ラン(20〜80人)では窓が疎になりすぎる**ため、日次(144 step)やスライディング窓も選べるようにし、**窓幅感度を報告**する。既存 `network_windows(window=24)` の窓機構と同じ考え方でコミュニティ・スナップショットを取る。
- **完全決定論のマッチング**: 各窓で決定的検出 → Jaccard 行列 → τ 以上で貪欲マッチ、**タイは最小 community_id 優先**で割る。τ 既定 0.3(感度を併記)。
- ライフサイクル(誕生/成長/合流/分裂/消滅)を上記ルールで機械分類し、**「街に自然発生したグループが、いつ生まれ・膨らみ・割れ・消えたか」を時系列イベント表として出力**する(これがユーザーの「動きを観る」中核成果物)。

---

## 3. コミュニティ構造の測度

### 3.1 モジュラリティ Q

- `networkx.algorithms.community.modularity(G, communities, weight='weight', resolution=1)`。分割を与えれば決定的。**注意**: resolution limit と縮退(§1.5, §1.3)があり、**N が違うランの Q を直接比較しない**。同一グラフ内での分割比較や、乱雑化ヌルモデルとの差として使う。

### 3.2 E-I index(内外結合比, Krackhardt & Stern 1988)

- **(EL − IL) / (EL + IL)**、範囲 [−1, +1]。EL=外部(コミュニティ間)結合数、IL=内部(コミュニティ内)結合数。**−1 に近い=内向き(結束的)、+1 に近い=外向き**([Krackhardt E/I Ratio, Wikipedia](https://en.wikipedia.org/wiki/Krackhardt_E/I_Ratio))。原典は Krackhardt & Stern 1988, Social Psychology Quarterly「Informal Networks and Organizational Crises」——**危機時に、形式的な内部集団を横断する非公式ネットワークが強い組織ほど有効**、という文脈で提案。**networkx には無いので手計算**(重み和で加重版も可)。
- 用途: 各コミュニティが「どれだけ閉じているか/外に開いているか」を1数値で。**「無理に作った組織」と「自然コミュニティ」の乖離**を測るのに特に有効(§4)。

### 3.3 コンダクタンス

- `networkx.algorithms.cuts.conductance(G, S, weight=...)`: 集合 S から外へ出るエッジ体積の割合。**低い=よく分離したコミュニティ**。ランダムウォークが S を出る確率に対応し、E-I index と近縁([Wikipedia の記述](https://en.wikipedia.org/wiki/Krackhardt_E/I_Ratio) が E/I と conductance の関連に言及)。決定的。
- `partition_quality(G, partition)` → (coverage, performance)。coverage=内部エッジ割合、performance=正しく分類されたノード対の割合。分割全体の品質サマリに。

### 3.4 リーダーシップ/中心性(degree / betweenness / PageRank の使い分け)

- **degree(次数)**: 局所的な活発さ・人気。安価(既存 `network_windows` の top1 は degree ベース)。「最もよく話す人」。
- **betweenness(媒介中心性)**: `betweenness_centrality(G, weight=...)`。**コミュニティ間を橋渡しするブローカー**を特定。O(NM) だが N<300 なら実用範囲。決定的(全探索時)。「集団と集団をつなぐ人」。
- **PageRank**: `pagerank(G, alpha=0.85, weight=...)`。**有向・重み付きの流れ(DM・SNS reshare)における影響力**。既定 nstart(一様)で決定的。「拡散で効く人」。
- 使い分け指針: **無向合成グラフで degree/betweenness(所属内の活発さ・橋渡し)**、**有向グラフ(DM/reshare)で PageRank(影響の向き)**。「創発リーダー」を主張するなら**複数中心性が同一人物を指すか**で頑健性を見る。

### 3.5 コア-周辺 と 安定性

- **コア-周辺(Borgatti & Everett 1999, Social Networks 21:375–395)**: 密なコア + 疎につながる周辺、の二部構造。離散(コア/周辺割当)と連続(coreness)がある。networkx の **`core_number` / k-core** は近縁概念(厳密な CP モデルは `cpnet` 等の別実装)。**創発集団に安定したコアがあるか**=「組織化の芽」の観察に使える。
- **安定性(membership Jaccard)**: 窓をまたいだメンバ集合の Jaccard(§2.3)。ノードの所属フリップ率、ライフサイクルイベント数も安定性の代理。**小 N 注意**: 1 名の移動で大きく振れるため、必ず n と併記し、可能なら複数 seed の帯で示す。

### 3.6 本プロジェクトへの適用推奨(§3)

- **コミュニティ単位**: size / 内部密度 / モジュラリティ寄与 / E-I index / conductance を各窓で出す。すべて**グラフの純関数=決定的**。
- **ノード単位(役割)**: degree(活発)/ betweenness(橋渡し)/ PageRank(有向影響)/ core_number(コア性)。
- networkx 関数: `modularity`, `partition_quality`, `cuts.conductance`, `betweenness_centrality`, `pagerank`, `core_number`。E-I index のみ自作(既存 `_conversation_adj` の隣接から数える)。
- **N<50 では解釈を控えめに**し、n・窓幅・seed 帯を必ず添える。

---

## 4. 多層ネットワーク(異種エッジ)の扱い

### 4.1 (a) 重み付き合成1層 vs (b) 多層のまま

- **合成(flattening)**: 各層を1層に潰し、既存の検出器をそのまま適用。最単純版は「どれか1層で隣接すれば隣接」、加重版は層の構造的性質を重みに反映([多層コミュニティ検出 ar5iv:1910.07646](https://ar5iv.labs.arxiv.org/html/1910.07646))。**長所=単純・可解釈・既存 networkx 資産をそのまま使える**。**短所=層固有の構造情報が失われる**(集約で多層コミュニティ情報が失われうる、と複数レビューが警告)。
- **多層のまま(multiplex)**: **Mucha et al. 2010「Community structure in time-dependent, multislice, and multiplex networks」**(Science 328:876–878、[arXiv:0911.1824](https://arxiv.org/abs/0911.1824))の**一般化 Louvain**が代表——層間結合 ω を持つ多スライス・モジュラリティを最大化。層固有構造を保つが、**networkx 標準には無く別実装(`pymnet`, `multinetx`, 一般化 Louvain 実装)が要る**。De Domenico らの多層モジュラリティ、コンセンサス(層別検出を集約)も同系。
- **実務標準**: N<300・異種エッジでは、**まず重み付き合成1層で検出**し、**層別検出を副次診断**として「合成が何を隠したか」を確認するのが穏当。層間構造そのものが研究対象になった段階で Mucha 一般化 Louvain に進む。

### 4.2 重み設計(先行例と本プロジェクトの案)

異種イベント → エッジ重みの設計指針(先行例=affiliation network の二部射影 Breiger 1974、加重 flattening):

| L1 イベント種 | エッジ | 向き | 重み設計の考え方 |
|---|---|---|---|
| `speak`/`hear`(近接会話) | speaker ↔ 各 hearer | 無向 | 高サリエンスだが**高頻度で支配しがち**。会話1回あたり `w_speak`、必要ならログスケール/上限 |
| `dm` | from → to | 有向(所属は対称化) | 意図的・高サリエンス。1通あたり `w_dm`(> w_speak) |
| `sns_post`/`sns_read`/`like`/`reshare` | reader/liker → author | 有向 | **reshare > like > read** の順に強い(承認の強度)。post 自体はノード活動 |
| `event_attend`(イベント共参加) | 共参加者どうし | 無向 | **二部射影**(event × agent → agent–agent)。**大イベントが完全グラフで支配しないよう `w_event/(k−1)` で割る** |
| `found_group`/`group_join`(明示グループ) | 同一グループ員 ↔ | 無向 | 明示的紐帯。**検出に入れるか要検討**(§4.3) |
| org 所属(会社・学校) | — | — | **検出グラフに入れない**(§4.3) |
| `move_segment`(位置) | 共在ペア(任意) | 無向 | 近接レイヤとして任意。ノイズ大なので既定オフ推奨 |

- **チャネル正規化**: 各チャネルは発生頻度が桁違い(会話が SNS reshare の何十倍も出うる)。**チャネルごとに正規化してからサリエンス重みを掛ける**(合成が最頻チャネルに乗っ取られるのを防ぐ)。重み係数 α_channel は config 化し既定値を明記。

### 4.3 「無理に組織を作らせない」ための設計上の肝

- **org 所属(会社・学校)と明示グループ(found_group)は、検出グラフから外し、「参照分割 R_org」として別に持つ**。そのうえで:
  - 検出された**自然コミュニティ** vs **R_org** の一致度(NMI / ARI / E-I index of org boundaries)を測る=「自然な集団は会社・学校の線とどれだけズレるか」。
  - これが**ユーザーの要望(組織を強制せず自然形成を観る)の直接の操作化**。組織所属を重みに焼き込むと「組織があるから密」という自明な結果になり、自然形成の観察が濁る。
- found_group は「創発の達成」側の指標(§6)としても使うので、**検出入力からは外し、成果イベントとして計上**するのが二重に整合的。

### 4.4 本プロジェクトへの適用推奨(§4)

- **主検出=重み付き合成・無向1層**(会話/DM/SNS/イベント共参加をチャネル正規化して合成)。決定的な Louvain(seeded)/自作 LPA を適用。
- **org 所属・明示グループは検出に混ぜず、参照分割/成果イベントとして別扱い**。
- 有向情報(DM/reshare)は**影響力(PageRank)**専用に別途保持。所属判定は対称化グラフで。
- 層別検出を副次で回し、「合成が隠した層固有構造」を点検。多層モジュラリティ(Mucha)は将来オプション。

---

## 5. 生成エージェント系論文でのコミュニティ観測

| 研究 | 何を・どう測ったか | 本プロジェクトで流用できる点 |
|---|---|---|
| **Park et al. 2023 Generative Agents**([arXiv:2304.03442](https://arxiv.org/abs/2304.03442)) | **情報拡散**(市長選候補・バレンタインパーティの2事実を種まき→2日後に全員をポーリング、既知率が 4%→32%/48% に上昇)、**関係形成**(開始時/終了時に「互いを知っているか」を尋ね、関係密度が増加)、**協調**(パーティに正しい時刻・場所に集まった人数を数える) | **正式なグラフ・コミュニティ検出ではなく、拡散率・関係密度・協調到達数で測る流儀**。既存 provenance/transmission + sns で拡散率を、`network_windows` の edges/density で関係密度を再現できる |
| **Project Sid(Altera 2024)**([arXiv:2411.00114](https://arxiv.org/abs/2411.00114)) | PIANO アーキテクチャ。**役割特化**(同一で始まった 30 体が相互作用で farmer/artist 等に分化)、**集団規則への遵守**(民主的に憲法・法を改正しそれに従う)、**文化(宗教)伝播** | 役割分化を**活動構成のエントロピー/gini**で、規則遵守を**制度ルール(propose→institution_rule)への追従率**で。※**明示的なグラフ・コミュニティ検出の手法は論文から未確認** |
| **AgentSociety(Tsinghua 2025)**([arXiv:2502.08691](https://arxiv.org/abs/2502.08691)) | 1万+体。検証は行動集約(radius of gyration・1日訪問地点数・意図分布)を実データと突合 | 移動・行動の現実整合の型は既存 calibrate_report と同型。※**組織・コミュニティの明示検出手法は本調査の範囲では未確認** |
| **Moltbook(Li, Li & Zhou 2026)**([arXiv:2602.14299](https://arxiv.org/abs/2602.14299)) | 「社会化は創発するか」を5診断指標(semantic stabilization / lexical turnover / individual inertia / influence persistence / **collective consensus**)で測定。**規模だけでは社会化は生まれない**と結論 | collective consensus / influence persistence は**コミュニティ内の合意・影響持続の測度**として、§3 の構造測度と接続可能 |
| **Emergent Relational Order in LLM Agent Societies(2026)**([arXiv:2606.23764](https://arxiv.org/pdf/2606.23764)) | 集団感情(collective affect)から**権威階層化(authority stratification)**への創発 | リーダーシップ/中心性(§3.4)の創発を測る先行例 |

- **総括**: 生成エージェント系の多くは「相互作用ログ + 後処理の集約指標(拡散率・関係密度・役割分化・合意)」で創発を測り、**Louvain/Leiden 級の正式なコミュニティ検出を主指標に据えた公開例は乏しい**(未確認/非公開が多い)。→ 本プロジェクトが**「正式なコミュニティ検出 × ライフサイクル追跡 × 達成の紐づけ」を後処理で体系化**すること自体が差別化ポイントになりうる。

### 5.1 本プロジェクトへの適用推奨(§5)

- Park の**拡散率(事実既知フラクションの時間推移)**を transmission/provenance + sns から再現。**関係密度の成長**は既存 `network_windows` の edges/density を窓系列で。
- Sid の**役割特化指標**(各エージェントの活動構成の entropy/gini の時間推移)と**規則遵守率**を追加。
- 検出したコミュニティを「合意・感情・影響を測る単位」として使い(§3 と §5 を接合)、**「どのコミュニティが内部合意を高め、リーダーを立て、外へ影響を広げたか」**を可視化する。

---

## 6. 創発組織の「達成」の測定(集合行為の成果)

### 6.1 「大きなことを成し遂げる」の操作化

「達成」を**具体的な集合行為の成果イベント**に落とし、**それを検出コミュニティに帰属**させる:

| 成果の型 | L1 での操作化 | 強度の目安 |
|---|---|---|
| **イベント主催の到達** | `event_host` + 紐づく `event_attend` 数 | 協調集会の規模・到達 |
| **グループの設立と持続** | `found_group`/`group_join` + 時系列生存(消えずに残るか) | 組織化の成否 |
| **提案の採択(制度化)** | `propose` → `institution_rule` 生成 / `n_active_rules` 増 | **最強の「世界改変」信号**(規範・制度の創発) |
| **経済活動** | `venture_open` + `venture_sale` 額 | 集団的経済成果 |
| **文化カスケード** | 語彙・ラベルの採用が閾値到達(既存 `item_cascades`: size/depth/reach) | 1→多への文化的達成 |

- **帰属ルール**: 各成果イベントを、**駆動した参加者の(当該時点の)コミュニティ所属の多数決**で1つの `dynamic_community_id` に帰属。
- **測る問い**: (i)あるコミュニティが**規模の割に成果を出す**か(1人あたり成果)、(ii)**成果が現れる閾規模・閾結束**があるか(→ 分野7 の k*・相転移と直結)、(iii)成果が **E-I index(内向き結束)や強いコア(§3.5)や高中心性リーダー(§3.4)**と相関するか。

### 6.2 先行例・理論的裏付け

- **制度の創発(Ostrom 系・コモンズ ABM)**: 「集合行為を通じた制度の創発」を単純モデルで示す([Managing the commons, IJC](https://thecommonsjournal.org/articles/10.18352/ijc.606))。**propose→institution_rule** はこの「制度の創発」の直接の操作化。
- **集合知の「協調利得」**: 小規模ではまず**タスク性能を上げる協調利得**として現れる(Emergent Coordination in Multi-Agent Language Models, [arXiv:2510.05174](https://arxiv.org/html/2510.05174v1))。
- **Project Sid の憲法改正遵守**は「統治=ガバナンスの達成」の計測例(§5)。**Park のパーティ集合到達**は小規模な集合行為成功の計測例(§5)。

### 6.3 「無理に組織を作らせない」との整合

- **達成はイベントログからボトムアップに定義**し、**「formal な group オブジェクトが在るか」に依存させない**。あるコミュニティは `found_group` を一度も呼ばずとも、イベント共催や語彙カスケードで「成し遂げる」ことがありうる——それを取りこぼさない定義にする(これがユーザー要望の核心)。

### 6.4 本プロジェクトへの適用推奨(§6)

- 上表の成果イベントを **`dynamic_community_id` に帰属**させ、**(コミュニティ × 窓)の成果集計表**を出す。
- 成果 × 構造(E-I / コア / 中心性 / サイズ)の相関を出し、**「どんな構造の自然コミュニティが達成に至るか」**を記述統計で提示(因果主張は控え、k* 掃引で閾を探す)。

---

## 7. 実装スケッチ(推奨パイプライン・擬似コード)

**すべて L1 を読むだけの後処理。決定論は「ソート挿入・seed 固定・版ピン・id 正準化・タイ最小 id」で担保。**

```python
# 0) 読み込み(既存 measure.load_events の列射影・逐次読みを流用)
events = load_events(run_dir, kinds=[
    "speak","hear","dm","sns_post","sns_read","like","reshare",
    "event_attend","found_group","group_join","propose","institution_rule",
    "venture_open","venture_sale","vocab_coin","label_adopt","move_segment"])
R_org = load_org_membership(run_dir)   # 会社・学校=参照分割(検出には使わない)

# 1) 窓分割(既定=週次 1008 step。小Nは日次/スライディングも。決定的に境界を切る)
windows = split_windows(events, window=WEEK, mode="tumbling")  # sorted, 決定的

# 2) 各窓 → 重み付き合成・無向グラフ(チャネル正規化 → α で加重)
def build_graph(win_events):
    W = defaultdict(float)                       # {(min(u,v),max(u,v)): weight}
    per_channel = defaultdict(lambda: defaultdict(float))
    for e in win_events:
        k, a, p = e["kind"], e["agent_id"], e["payload"]
        if k == "speak":
            for h in p.get("hearers", []):       # speaker ↔ hearer
                add(per_channel["speak"], a, h, 1.0)
        elif k == "dm":
            add(per_channel["dm"], a, p["to"], 1.0)         # 所属は対称化
        elif k in ("like","reshare","sns_read"):
            add(per_channel["sns"], a, p["author"],
                {"sns_read":0.2,"like":0.5,"reshare":1.0}[k])
        elif k == "event_attend":
            coattend[p["event_id"]].add(a)       # あとで二部射影
        # found_group/group_join/org は検出に入れない(成果/参照へ)
    for eid, members in coattend.items():        # イベント共参加=二部射影
        m = sorted(members); kf = len(m)-1 or 1
        for i in range(len(m)):
            for j in range(i+1, len(m)):
                add(per_channel["event"], m[i], m[j], 1.0/kf)  # 大イベント抑制
    # チャネル正規化 → サリエンス α で合成
    for ch, edges in per_channel.items():
        s = normalize(edges)                     # チャネル内で正規化
        for (u,v), w in s.items():
            W[(u,v)] += ALPHA[ch] * w
    G = nx.Graph()
    G.add_nodes_from(range(n_agents))            # ★ id 昇順で add(決定論)
    for (u,v), w in sorted(W.items()):           # ★ ソート順で add
        G.add_edge(u, v, weight=w)
    return G

# 3) 検出(正準=自作決定論LPA、交差確認=seeded Louvain)
def detect(G):
    base = measure_communities_lpa(G)            # 既存の決定論LPA(seed不要)
    louv = nx.community.louvain_communities(     # モジュラリティ視点
        G, weight="weight", resolution=GAMMA, seed=SEED)
    louv = canonicalize(louv)                    # community_id = 最小メンバ id
    core = agreement_core(base, louv)            # 両者一致=頑健コア
    return base, louv, core

comm_by_win = [detect(build_graph(w)) for w in windows]  # 決定的

# 4) 窓間マッチング → Palla ライフサイクル(誕生/成長/合流/分裂/消滅)
def track(prev, curr, tau=0.30):
    events = []
    for j, Cj in curr.items():                   # id 昇順で走査
        matches = [(jaccard(Ci, Cj), i) for i, Ci in prev.items()
                   if jaccard(Ci, Cj) >= tau]
        matches.sort(key=lambda x: (-x[0], x[1]))# タイは最小 id
        if not matches:      events.append(("birth", j))
        elif len(matches) >= 2: events.append(("merge", j, [i for _,i in matches]))
        else:
            i = matches[0][1]
            events.append(("grow" if len(Cj) > len(prev[i]) else "shrink", i, j))
    # prev 側で curr にマッチしないもの=death、1→多=split も同様に判定
    return assign_dynamic_ids(events)            # チェーン化 → dynamic_community_id

lifecycle = chain([track(comm_by_win[t], comm_by_win[t+1])
                   for t in range(len(comm_by_win)-1)])

# 5) 構造測度(コミュニティ単位 / ノード単位)すべて決定的な純関数
for w, (G, comm) in zip(windows, comm_by_win):
    Q   = nx.community.modularity(G, comm.values(), weight="weight")
    for cid, S in comm.groups():
        size   = len(S)
        ei     = ei_index(G, S)                  # (EL-IL)/(EL+IL) 自作
        cond   = nx.conductance(G, S, weight="weight")
        dens   = internal_density(G, S)
    deg   = nx.degree_centrality(G)              # 活発
    betw  = nx.betweenness_centrality(G, weight="weight")   # 橋渡し
    pr    = nx.pagerank(DiG_win, alpha=0.85, weight="weight")  # 有向影響
    kcore = nx.core_number(G)                     # コア性
    # 対 R_org: NMI/ARI/E-I(org境界) で「自然 vs 組織」の乖離
    align = compare_to_reference(comm, R_org)

# 6) 達成の帰属(成果イベント → dynamic_community_id)
for e in achievement_events(events):             # event_host+attend, propose→rule,
    cid = plurality_community(participants(e), comm_at(e.step))  # venture_sale, cascade≥閾
    achievements[(cid, window_of(e))].append(e)

# 7) 出力=tidy long-format(下流の信頼区間・回帰・作図を一様化)
emit_long_table(cols=["run","seed","window","community_id",
                      "dynamic_community_id","metric","value"])
emit_lifecycle_table(lifecycle)                  # 誕生/成長/合流/分裂/消滅の時系列
emit_achievement_table(achievements)             # (community × window) の成果
```

**決定論チェックリスト**: (1) `G.add_nodes_from(sorted ids)` / `add_edge` をソート順、(2) Louvain は `seed` 固定 + networkx 版ピン、(3) community_id = 最小メンバ id 正準化、(4) Jaccard マッチングのタイは最小 id、(5) 自作 LPA を「乱数ゼロの基準器」に据える、(6) 成果帰属の多数決タイも最小 id。→ **同一 L1 + 同一 config → 同一出力**。

---

## 8. まとめ(素材としての示唆)

- **検出**: 決定論絶対の要件下では、**自作決定論 LP(既存 `measure.communities`)を正準器**に、**seeded Louvain を交差確認**に。**networkx の Leiden は backend 専用**なので当面採用不可(必要なら `leidenalg` 別依存)。resolution limit と縮退があるため**単一分割を真理としない**(手法一致コア・複数 seed・窓安定性で頑健化)。
- **時間発展**: **窓別検出 → Jaccard マッチング → Palla ライフサイクル**が標準で決定論と好相性。週次既定・窓幅感度を報告。
- **測度**: modularity / E-I index / conductance / partition_quality と、degree・betweenness・PageRank・core_number の役割分担。**小 N は n と併記し過剰解釈を避ける**。
- **多層**: **重み付き合成1層を主**、層別を副次。**組織所属は検出に混ぜず参照分割**にして「自然 vs 組織」の乖離を測る=ユーザー要望の直接の操作化。
- **達成**: 成果イベント(主催到達・提案採択・経済・カスケード)を**ボトムアップに定義しコミュニティへ帰属**。formal group の有無に依存させない。
- 生成エージェント系論文の多くは正式なコミュニティ検出を主指標にしておらず、**「検出 × ライフサイクル × 達成」の後処理体系化は本プロジェクトの独自性になりうる**。決定は Fable/ユーザー。

---

## 出典

一次ソース優先。アクセス日 2026-07-11。

**コミュニティ検出手法・networkx**
- [Communities — NetworkX リファレンス(3.6)](https://networkx.org/documentation/stable/reference/algorithms/community.html) / [louvain_communities](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.louvain.louvain_communities.html) / [leiden_communities(backend 専用の記述)](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.leiden.leiden_communities.html)
- Louvain: [Blondel et al. 2008 の解説群](https://metricgate.com/blogs/community-detection-louvain-vs-leiden/)
- Leiden: [Traag, Waltman, van Eck 2019, Scientific Reports 9:5233 "From Louvain to Leiden"](https://www.nature.com/articles/s41598-019-41695-z) / [arXiv:1810.08473](https://arxiv.org/abs/1810.08473) / [非連結コミュニティの扱い arXiv:2402.11454](https://arxiv.org/html/2402.11454v2)
- 半同期 LPA: Cordasco & Gargano 2010(networkx `label_propagation_communities` の基礎)/ 原法 Raghavan, Albert, Kumara 2007
- resolution limit: [Fortunato & Barthélemy 2007, PNAS](https://www.pnas.org/doi/10.1073/pnas.0605965104)
- モジュラリティ縮退: [Good, de Montjoye, Clauset 2010, PRE(arXiv:0910.0165)](https://arxiv.org/abs/0910.0165)

**時間発展・ライフサイクル**
- [Palla, Barabási, Vicsek 2007 "Quantifying social group evolution", Nature 446:664](https://www.researchgate.net/publication/6412158_Quantifying_social_group_evolution)
- [Rossetti & Cazabet 2018, ACM Computing Surveys 51(2) "Community Discovery in Dynamic Networks: A Survey"](https://giuliorossetti.github.io/assets/pdf/papers/CSUR18.pdf)
- [Community Evolution(Springer, Jaccard マッチングの解説)](https://link.springer.com/rwe/10.1007/978-1-4939-7131-2_223) / [estrangement confinement, arXiv:1203.5126](https://arxiv.org/pdf/1203.5126)

**構造の測度**
- [Krackhardt E/I Ratio(Krackhardt & Stern 1988), Wikipedia](https://en.wikipedia.org/wiki/Krackhardt_E/I_Ratio)
- コア-周辺: Borgatti & Everett 1999, Social Networks 21:375–395 "Models of core/periphery structures"

**多層ネットワーク**
- [Mucha et al. 2010, Science 328:876 "Community structure in ... multiplex networks"(arXiv:0911.1824)](https://arxiv.org/abs/0911.1824)
- [Community Detection in Multiplex Networks(ar5iv:1910.07646)](https://ar5iv.labs.arxiv.org/html/1910.07646) / [Multilayer Networks レビュー(arXiv:1309.7233)](https://arxiv.org/pdf/1309.7233)

**生成エージェント・LLM 社会シム**
- [Park et al. 2023 "Generative Agents"(arXiv:2304.03442)](https://arxiv.org/abs/2304.03442)
- [Project Sid(Altera 2024, arXiv:2411.00114)](https://arxiv.org/abs/2411.00114)(正式なコミュニティ検出手法は未確認)
- [AgentSociety(arXiv:2502.08691)](https://arxiv.org/abs/2502.08691)(組織検出手法は本調査範囲では未確認)
- [Moltbook(Li, Li & Zhou 2026, arXiv:2602.14299)](https://arxiv.org/abs/2602.14299) / [Emergent Relational Order in LLM Agent Societies(arXiv:2606.23764)](https://arxiv.org/pdf/2606.23764)

**集合行為・達成**
- [Managing the commons: emergence of institutions through collective action(IJC)](https://thecommonsjournal.org/articles/10.18352/ijc.606)
- [Emergent Coordination in Multi-Agent Language Models(arXiv:2510.05174)](https://arxiv.org/html/2510.05174v1)

**自プロジェクト内部参照(コード/ドキュメント — 読み取りのみ)**
- `src/society/observer/measure.py`: `communities()`(決定論 LPA)/ `network_windows()`(会話グラフ窓・degree/clustering/top1/churn)/ `_conversation_adj()` / `drift_metrics()`
- `docs/research/data-pipeline-lit.md`(event sourcing・後処理 projection の設計)/ `docs/lit/network__diffusion-overview.md`(complex contagion)/ `docs/lit/mas__li2026_moltbook.md`(5診断指標)
</content>
</invoke>
