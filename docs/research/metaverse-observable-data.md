# リサーチ: メタバース事業者の観測可能データと内部状態復元の境界

> 2026-08-13。ユーザー構想「メタバースのようなサイバー空間上で、人々からどのようなデータを得られるのかという視点での検証」を、
> 「**観測可能な痕跡だけから、内部状態をどこまで復元できるか**」という問いに変換するためのWeb文献調査。
> 本シムは全エージェントの内部状態(LLM思考・needs・信念・関係)を正解として持つ——実事業者には原理的に不可能な非対称性が武器。
> 計画は [metaverse-projection-plan.md](../plans/metaverse-projection-plan.md)。実装は未着手(ユーザー指示=計画まで)。
> 総ソース数 約150(一次ソースURL)。ここには設計判断に効くものを厳選して記録する。

---

## 1. 実事業者が実際に収集しているテレメトリ(一次ソース=プライバシーポリシー/開発者API)

### 最重要の日本語一次資料
- **クラスター株式会社「メタバースプラットフォームにおける取得可能なデータと活用事例」(総務省 メタバース研究会 資料14-2-1)**
  https://www.soumu.go.jp/main_content/001011638.pdf
  事業者のデータアナリスト本人が政府に説明した「何が取れるか」= **射影フィルタの設計仕様書としてほぼ理想**。
  (a) **アクションイベントログ100〜200種類程度**をユーザー行動ごとに設定・独立タイミングで取得
  (b) **周期取得**(空間上の移動・視線の動き)と**都度取得**(写真撮影・別空間への移動)の2分
  (c) **3D同期通信ログ** = アバター位置・姿勢・音声・アイテム位置を xyz座標高頻度で
  (d) **「設定していない行動はデータが記録されず、過去に遡って取得することもできない」= 射影フィルタは事前定義かつ遡及不能**
  ※画像PDFのため自動抽出不可。手動精読を強く推奨。議事録: https://www.soumu.go.jp/main_content/001015030.pdf
- cluster Tech Blog「メタバースのデータ分析とはなにをやっているのか」 https://tech-blog.cluster.mu/entry/2023/10/24
  ロビーの位置ログ可視化で「時計塔の頂上に滞留」を発見 = **位置ログだけから選好が読める**実例。

### 各社の観測集合(要点のみ)
| 事業者 | 一次ソース | 特徴的な観測 |
|---|---|---|
| Meta (Horizon/Quest) | https://www.meta.com/legal/privacy-policy/ ・視線: https://www.meta.com/legal/quest/eye-tracking-privacy-notice/ | ヘッド+コントローラ位置姿勢・abstracted hand/body/gaze/表情・音声録音+トランスクリプト・**部屋の壁/物のサイズ**・EMG。視線は **raw(端末で削除)/abstracted(送信)/metadata** の3層 |
| VRChat | https://hello.vrchat.com/privacy ・ https://hello.vrchat.com/state-privacy | 「指・手・頭・身体各部の movement information」「Eye Movement Information」を明示名指し。**Inferences(推定プロファイル)が観測と別カテゴリで立つ** |
| Roblox | https://en.help.roblox.com/hc/en-us/articles/115004630823 ・ https://create.roblox.com/docs/reference/engine/classes/AnalyticsService | 音声「monitor, collect, use, and store」+学習利用。VR姿勢は「収集するが**保存しない**」。開発者API `LogEconomyEvent`(残高まで)・**`GetPlayerSegmentsAsync` = 課金傾向セグメントを第三者に再配布** |
| Epic/Fortnite | https://www.epicgames.com/site/en-US/privacypolicy ・ https://dev.epicgames.com/docs/epic-online-services/player-and-game-data/eos-metrics-interface | gameplay attempts/progression。音声は**端末保存・通報時のみ送信**。ワイヤ実フィールド(SessionId等)=セッション境界+ハートビートが業界最小原子 |
| ZEPETO | https://support.zepeto.me/hc/en-us/articles/45625958331033 | クロスデバイス追跡明記。画像は端末内 |
| cluster | https://help.cluster.mu/hc/ja/articles/20264222848153 | DM取得明示(「三者間通信」と警告)・音声レコード・Inferences。外部送信: https://cluster.mu/terms/external-transmission (手動閲覧要) |
| Second Life | https://lindenlab.com/privacy | 取引の「**parties involved**」までログ(取引相手ID) |
| Unity Analytics | https://docs.unity3d.com/Packages/com.unity.services.analytics@3.0/manual/index.html | `gameRunning`を**1分ごと**・60秒フラッシュ・全イベントにsessionID |
| PlayFab | https://learn.microsoft.com/en-us/gaming/playfab/features/analytics/metrics/playstream-events | **`client_focus_change`(ウィンドウのフォーカス喪失)が標準イベント** = 注意の所在まで |
| Apple分類語彙 | https://developer.apple.com/app-store/app-privacy-details/ | 16分類にXR用 **Body(Hands, Head)/Surroundings(Environment Scanning)** が追加済み。射影フィルタのカテゴリ語彙にそのまま使える |

### 分類の理論的背骨
- **OECD/Abrams 四分類 provided / observed / derived / inferred** — https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2510927
  全状態ログ=真値、observed=フィルタ出力、inferred=復元実験の出力、の三項対応が直接作れる。
- EU DSA Art.40 委任規則(研究者データアクセス・2025-07採択) — 「事業者が持つデータ」の法的カタログ。

### 横断的発見(4つ)
1. **生体データは例外なく「オンデバイス処理+抽象化」で分岐**(Meta/VRChat/Roblox/ZEPETO共通)→ 射影フィルタは「センサーの有無」でなく**抽象化レベル**で切るのが現実に忠実。
2. **連続姿勢ストリームは収集されるが保持されない**(Roblox明示)。**どの事業者もサンプリングレートと保持期間を公開していない** = 論文で「未知」と正直に書ける空白。
3. **音声は3レジーム**: 常時録音+保存+学習(Roblox 13+)/録音+文字起こし(Meta)/端末保存・通報時のみ(Epic)。
4. **アンチチートが最大の収集範囲**(VRChat EAC: RAM・プロセス・通信・ファイル)でほぼ非開示。

---

## 2. 痕跡からの個人特定・内部状態推定(実証)

### VRモーション(構想の中核証拠)
- **Nair et al. (USENIX Sec '23) 55,541人**: 頭+両手の3点、100秒で**94.33%**・10秒で73.20%の一意特定 — https://arxiv.org/abs/2302.08927
- **Nair et al. 属性推定**: モーション+調査票1,006人、**40超の個人属性が単純MLで一貫推定可** — https://arxiv.org/abs/2305.19198
- **MetaData(PoPETs 2023)**: VR脱出ゲーム数分で**25超の属性**(身長・腕長・IPD・年齢・性別・部屋の広さ・遅延多辺測量で地理位置・視線から母語)。**事業者は世界を設計して測定を誘発できる**(能動的攻撃面) — https://arxiv.org/abs/2207.13176
- **Truth in Motion(IEEE S&P 2024)**: 敵対者4分類 **hardware / client / server / unprivileged user** = 射影フィルタを視座別に4本作る根拠 — https://arxiv.org/abs/2306.06459
- **BehaVR**: センサー群別(body/gaze/hand/face)の識別性能比較=アブレーションのテンプレート — https://arxiv.org/abs/2308.07304
- **劣化は効かない(2024)**: ノイズ・フレームレート低下・精度低下・次元削減が**全て失敗** — https://arxiv.org/abs/2407.18378
  → **フィルタ段は「解像度を落とす」でなく「チャンネルを丸ごと落とす/抽象化を変える」で切ること**(設計上の警告)。
- SoK: Data Privacy in VR(68論文の分類法) — https://arxiv.org/abs/2301.05940 / MetaGuard(LDP防御・privacy-utility曲線) — https://arxiv.org/abs/2208.05604

### 視線
- **Kröger et al. (2020)「視線単独から何が漏れるか」**: 同一性・性別・年齢・体重・性格・薬物習慣・感情・技能・恐怖・興味・性的指向・認知プロセス・疾患 — https://dl.ifip.org/IFIP-AICT-576/hal-03378980
  **「仮想世界だけにあるセンサー1つでこれだけ落ちる」の最良引用**(都市に等価センサーなし)。
- 視線には標準DPが効かない(時間相関) — https://arxiv.org/abs/2002.08972 / 視線×モーションの個別保護は組み合わせで破れる — https://arxiv.org/abs/2411.12766

### 物理世界の unicity(比較対照)
- **de Montjoye 2013**: CDR 150万人、**4時空点で95%一意**。一意性は解像度の**約1/10乗**でしか減衰しない — https://www.nature.com/articles/srep01376
- **de Montjoye 2015(Science)**: カード取引、4点で90%。金額を足すと+22% — https://www.science.org/doi/10.1126/science.1256297
- **Rocher 2019**: **サンプリングは防御にならない**(15属性で99.98%再識別) — https://www.nature.com/articles/s41467-019-10933-3
- **Golle & Partridge 2009**: **自宅×職場ペアは中央値労働者で一意** — https://crypto.stanford.edu/~pgolle/papers/commute.pdf
- 成都メトロ(2023): 改札3点・1分解像度で90%超 — https://doi.org/10.1016/j.physa.2023.129155
- **Song et al. 2010**: 個人移動の**予測可能性上限93%** = 復元実験の天井 — https://www.science.org/doi/10.1126/science.1177170
- **Crandall 2010(PNAS)**: **時空共起の回数→知り合い確率**の定量化 = 共在ログから関係グラフを復元する実験の設計図 — https://www.pnas.org/doi/10.1073/pnas.1006155107
- Gong & Liu 2016: 友人グラフ+行動の統合で属性推定が跳ねる(57%→絞れば90%超) — https://www.usenix.org/system/files/conference/usenixsecurity16/sec16_paper_gong.pdf

### テキスト・SNS・スマホ
- **Staab et al. (ICLR 2024)**: 実RedditからLLMが居住地・収入・性別等を**top-1 85%/top-3 95.8%**、人間の1/100コスト — https://arxiv.org/abs/2310.07298
  → **シムの発話/SNSチャンネルの期待復元率+復元器としてLLMを使う正当化**。
- **Kosinski 2013(PNAS)**: Facebook Likes だけで性的指向88%・人種95%・政党85% — https://www.pnas.org/doi/full/10.1073/pnas.1218772110
- **Hinds & Joinson 2018(327研究の系統レビュー)**: デジタル痕跡から推定成功した**14属性と精度**(性別80%+・年齢70%+・位置50-94%・政治11-91%) — https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0207112
  → **属性別の期待天井テーブルが既製**。事前登録の予測値に使う。
- **Stachl 2020(PNAS)**: スマホ受動センシング30日でBig Five r≈0.37-0.40。**特性ごとに効くセンサークラスが違い、単独十分なセンサーは無い** — https://www.pnas.org/doi/10.1073/pnas.1920484117
- **ExtraSensory(Vaizman 2017)**: モダリティ別アブレーションの最良ソース。**支配的な単一モダリティは無く、最良センサーはラベルごとに変わる。モダリティを落とすと一様劣化でなく特定の文脈クラスが消える** — https://arxiv.org/abs/1609.06354
  → **射影フィルタ設計の中心的仮説そのもの**。

---

## 3. 行動からの潜在状態推定の方法論

- **Baker, Saxe, Tenenbaum 2009**: 逆計画(inverse planning)=信念と選好の同時ベイズ推論の古典 — https://www.sciencedirect.com/science/article/abs/pii/S0010027709001607
- **Machine Theory of Mind(ICML 2018)**: 行動観測のみから他者モデルを構築する償却ベイズ推論器 = **復元器のアーキテクチャそのもの** — https://arxiv.org/abs/1802.07740
- IRLサーベイ(Arora & Doshi 2021) — https://arxiv.org/abs/1806.06877
- **★Skalse & Abate 部分同定性**: 複数の報酬関数が同一方策と整合=報酬は部分的にしか同定できず、行動モデルは実務上必ず誤特定される — https://arxiv.org/abs/2411.15951
- **★Armstrong & Mindermann (NeurIPS 2018) No Free Lunch**: 方策を「計画」と「報酬」に一意分解するのは**原理的に不可能**。Occamでも救えない — https://arxiv.org/abs/1712.05812
  → **「行動からは選好を原理的に復元しきれない」の決定的引用 = 「取れないデータ」の境界を数学で引ける**。
- Goal Recognition as Planning サーベイ(IJCAI 2021・ノイズ/欠損観測が中心課題) — https://www.ijcai.org/proceedings/2021/616
- digital phenotyping 定義論文(Onnela & Rauch 2016) — https://www.nature.com/articles/npp20167
- **LLMエージェントの自己申告は行動と不一致**(独立3本): Behaviorally Coherent? https://arxiv.org/abs/2509.03736 / Practice What They Preach? https://arxiv.org/abs/2507.02197 / Alignment Revisited https://arxiv.org/abs/2506.00751
  → **真値は「LLMが何と言ったか」でなく「シムの状態変数」に置く**。

---

## 4. 広告・ターゲティングの信号価値

- **Youyou 2015(PNAS) 用量反応曲線**: 10 Likesで同僚超え・70で友人・150で家族・300で配偶者 = **観測量→復元率曲線の形の予告** — https://www.pnas.org/doi/10.1073/pnas.1418680112
- Matz 2017(PNAS): 心理ターゲティングでクリック+40%/購買+50%(350万人) — https://www.pnas.org/doi/10.1073/pnas.1710966114
  **★必ず Perla et al. 2026(41研究メタ分析)と並記**: 復元できる性格分散は約5%・行動効果は無視できる水準 — https://onlinelibrary.wiley.com/doi/10.1002/mar.70073
- **行動ターゲティングの増分価値は数字が対立**: Marotta+4% vs Google実験−52%。**現時点の最良裁定 = Gu, Johnson, Kobayashi 2026(PNAS・2億imp・CMA監督)**: 3rd party cookie廃止で−29.1%、Privacy Sandboxは4.2%しか回復せず — https://www.pnas.org/doi/10.1073/pnas.2603752123
- **Neumann 2019**: データブローカー90オーディエンス実測、ヒット率改善はランダム比0〜77%で乱高下 = 「データは売り文句よりずっと悪い」 — https://pubsonline.informs.org/doi/10.1287/mksc.2019.1188
- GDPR効果(Aridor 2020): 観測可能な消費者−12.5%、**残った者はより予測しやすくなる** = 観測の選択バイアス — https://www.nber.org/papers/w26900
- **最小観測量**: クリックストリーム**5クリックでF1≈60%・9クリックで>70%**(遡る必要はほぼ無い) — https://www.nature.com/articles/s41598-020-73622-y
- **privacy-utility の定量化**: Noriega-Campero「**information ratio**」(最細粒度=本人データ7%で残り93%復元/粗粒度=51%必要) — https://arxiv.org/abs/1808.00160
  区分冪乗則でデータ量→性能をフィット — https://arxiv.org/abs/2107.08096 / Where's Waldo効果=**規模自体がプライバシーパラメータ** — https://pure.eur.nl/ws/portalfiles/portal/189200824/1-s2.0-S0167811624000417-main.pdf

---

## 5. 仮想世界を社会科学の実験場に(先行研究)

- **Bainbridge 2007(Science)**: 創設マニフェスト。「最小の経済活動まで正確にログできる」= **事業者の記録は構成上完全、都市の記録は常に標本** — https://www.science.org/doi/10.1126/science.1146930
- Castronova 2001(EverQuest経済測定) — https://papers.ssrn.com/sol3/papers.cfm?abstract_id=294828 / **2009 EQ2マクロ**: 取引ログから国民経済計算を構築・新規サーバが同一マクロに収束=「Code is Law」 — https://journals.sagepub.com/doi/10.1177/1461444809105346 / Arden実験(需要法則のRCT・専用世界構築はコスト限界) — https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1173642
- **Virtual Worlds Exploratorium(EQ2 60TBログ+調査票連結)** — https://experts.illinois.edu/en/publications/the-virtual-worlds-exploratorium-using-large-scale-data-and-compu/ / Virtual Census(合成人口をセンサス周辺分布と比較する手法) — https://journals.sagepub.com/doi/10.1177/1461444809105354
- **WoW Avatar History**: 91,065アバター・10分サンプル・1,107日 = **在場/位置時系列の最良の公開類似物**(セッション長・日周在場・ゾーン占有のリアリティチェックに) — http://web.cs.wpi.edu/~claypool/mmsys-dataset/2011/wow/ (元ホスト到達不能・WPI/Kaggleミラーを使う)
- Corrupted Blood(Lancet ID 2007): 隔離失敗は「人間の意思決定に駆動されたため数値的手法で予測不能」= **個体意思決定の内生化の根拠** — https://www.thelancet.com/journals/laninf/article/PIIS1473-3099(07)70212-8/fulltext
- EVE Online 月次経済レポート(公開最長の仮想経済系列) — https://www.eveonline.com/news/t/monthly-economic-reports
- Game Analytics(Springer 2013・標準テレメトリ分類法) — https://link.springer.com/book/10.1007/978-1-4471-4769-5 / Destiny社会ネットワーク — https://eprints.whiterose.ac.uk/id/eprint/127393/ / プレイヤークラスタリング手法比較 — https://arxiv.org/abs/1407.3950

### LLM社会シムの評価方法論(本シムの評価にも直結)
- **Generative Agents(Park 2023)**: インタビュー統制評価(5領域)+end-to-end+**アブレーションの梯子**(full > no-reflection > … > 人間基準線) — https://arxiv.org/abs/2304.03442
- **★Park et al. arXiv:2411.10109 は v3(2026-06-28)で改題済み**。「85%」は旧版値。現行: インタビュー基盤83%/複合86%/**人口統計のみ74%**。**分母を「本人の2週間再検査一貫性」に取る正規化**が最重要の移転アイデア — https://arxiv.org/abs/2411.10109
- Twin-2K-500(再検査天井が同梱された公開データセット) — https://arxiv.org/abs/2505.17479
- SOTOPIA(7次元ルーブリック) — https://arxiv.org/abs/2310.11667 / SimBench(最良でも40.80/100・alignment-simulationトレードオフ) — https://arxiv.org/abs/2510.17516
- **批判系**: Illusion of Artificial Inclusion — https://arxiv.org/abs/2401.08572 / **Hullman et al.(発見的検証は探索的主張のみ・確証的因果主張には統計的較正)** — https://arxiv.org/abs/2602.15785 / **Li & Ji(統計的リアリズム≠処置効果精度)** — https://arxiv.org/abs/2604.02458 / 同質化効果(TiCS 2026) — https://www.cell.com/trends/cognitive-sciences/abstract/S1364-6613(26)00003-3 / Computational Turing Test — https://arxiv.org/abs/2511.04195
- OASIS(100万エージェント・既知現象の再現で評価) — https://arxiv.org/abs/2411.11581 / AgentSociety — https://arxiv.org/abs/2502.08691

---

## 6. 復元実験の設計手法

- **Hewitt & Liang 2019 control tasks / selectivity**: 復元率には**対照課題が必須**(probeがラベルを記憶しただけかを分離) — https://aclanthology.org/D19-1275/
- **Voita & Titov 2020 MDL probing**: accuracyでなく**記述長(codelength)**を主指標に — https://aclanthology.org/2020.emnlp-main.14/
- 相互情報量としてのprobing — https://arxiv.org/pdf/2004.03061
- **Dinur-Nissim 再構成攻撃**: 「集計統計しか出さない射影フィルタ」も安全でない(米センサス2010は人口46%が脆弱) — https://queue.acm.org/detail.cfm?id=3295691 / https://www.pnas.org/doi/10.1073/pnas.2300976120
- Geo-Indistinguishability(位置チャンネルのノイズ設計) — https://arxiv.org/abs/1212.1984
- **疎観測からの軌跡復元**: 既知1%でも中央値2セル以内(復元率vsサンプリング率曲線の実測) — https://epjdatascience.springeropen.com/articles/10.1140/epjds/s13688-019-0206-8 / BERT4Traj — https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.GIScience.2025.8
- Synth-MIA(合成データ上で正解を持ったまま攻撃評価する先例・1,525構成) — https://arxiv.org/html/2509.18014v1
- **off-policy evaluation の support 条件**: 「事業者のログには提示しなかった選択肢の情報が構造的に無い」を形式化 — https://dl.acm.org/doi/10.1145/3097983.3098155
- Salganik *Bit by Bit* ビッグデータ10特性(**algorithmically confounded / incomplete** が「取れないデータ」の質的分類軸) — https://www.bitbybitbook.com/en/1st-ed/observing-behavior/characteristics/
- ABM較正の同定可能性(**集計は同定可能性を著しく劣化させる・層別で改善**) — https://www.jasss.org/25/2/1.html

---

## 7. 物理都市シム vs メタバースのセンサー差分(射影フィルタ設計時に明示すべき差)

### 日本の都市側の実観測(一次資料)
- **★NTTドコモ「モバイル空間統計」**: 500mメッシュ×**1時間**×性別×**5歳階級**×居住市区町村。処理3段=非識別化→拡大推計→**秘匿処理(少人数除去)**。**個人軌跡・端末単位履歴は提供されない** — https://mobaku.jp/about/
  → **「物理都市側の射影フィルタの既定値」としてそのまま実装できる**。
- **PLATEAU UC20-005**: Wi-Fi=MACアドレス検知で台数計数 / 4G/LTE=**MACを取得せず**強度・周波数パターンから台数推定=「匿名性の担保された計測」。**同じ人流でも取得方式で個人識別可能性が全く違う** — https://www.mlit.go.jp/plateau/use-case/uc20-005/
- 渋谷区エッジAIカメラ人流計測(シミュレーション対象都市そのものの実観測体制) — https://www.city.shibuya.tokyo.jp/contents/kusei/shibuya-data/collaboration/case02.html
- CDRから動的人口地図(Deville 2014 PNAS) — https://www.pnas.org/doi/10.1073/pnas.1408439111 / 群衆センシングのモダリティ→能力対応表(Draghici & van Steen) — https://dl.acm.org/doi/10.1145/3129343 / 交通ICカード(Pelletier 2011) — https://doi.org/10.1016/j.trc.2010.12.003
- Wi-Fiプローブの現実: MACランダム化は破れる(Martin 2017・Vanhoef 2016) / **プローブから社会グラフ再構成**(Barbera 2013=物理世界でも「関係」チャンネルは観測可能) — https://conferences.sigcomm.org/imc/2013/papers/imc148-barberaSP106.pdf / Apple BLE Continuityは「相互作用イベント」を漏らす — https://arxiv.org/abs/1904.10600
- **YJMob100K**(10万人75日・**意図的劣化: 500mグリッド・30分ビン・日付削除**) = 劣化後の都市軌跡に何が残るかの経験的ベンチマーク=**射影フィルタの1設定として直接複製できる** — https://www.nature.com/articles/s41597-024-03237-9
- Pseudo-PFLOW(日本全人口の合成モビリティ) — https://arxiv.org/abs/2205.00657

### 差分表(計画書に転記)
| 軸 | メタバース事業者 | 物理都市運営者 |
|---|---|---|
| 記録の完全性 | **構成上完全**(同期のため全員の位置を毎フレーム保持) | **常に標本**(既知位置は通常5〜20%) |
| 環境の設計権 | **測定を誘発するよう世界を作り替えられる**(MetaData) | 不可 |
| 固有センサー | **視線**(単独で同一性〜疾患まで) | 等価物なし |
| 身体制約 | なし(テレポート・アバター改変)——それでも**モーションは指紋**(100秒94.33%) | あり——**4時空点で95%一意**(別経路で同じ結論) |
| 観測装置の中立性 | **中立でない**(Proteus効果=アバターが行動を変える) https://doi.org/10.1111/j.1468-2958.2007.00299.x | 概ね中立 |
| 粗視化の効き | 劣化が**全て失敗**(2407.18378) | 解像度の**約1/10乗**でしか減衰しない |
| 離脱可能性 | アプリを閉じれば観測停止(→選択バイアス) | **オプトアウト不能な母集団** |
| 観測境界の決定要因 | **物理でなく事業者の方針**(Apple=視線を渡さない vs Meta=abstracted gaze) | 物理とセンサー配置 |

- メタバース脅威の構造化サーベイ: Wang et al. IEEE COMST 2023 — https://arxiv.org/abs/2203.02662 / VRアプリ実態調査(6,565本・1/3が機微データ利用未申告) — https://arxiv.org/abs/2510.23024
- 都市DT×メタバース収束の概念整理 — https://link.springer.com/article/10.1007/s10676-024-09812-3

---

## 8. 横断的な注意(実験設計に必ず入れる)

1. **分布一致は因果効果の検証にならない**(Li & Ji・Hullman)。復元率が高い≠このシムで介入実験ができる、と明記。
2. **エージェントの自己申告を真値にしない**(不一致の実証3本)。真値=シムの状態変数。
3. **分母を天井で正規化**(Park流=人間の再検査一貫性/シムでは決定論リプレイの一致度が天井)。
4. **観測装置は中立でない**(Proteus)。本シムの射影は事後解析なので「観測がシムを変えない」= この留保を構造的に回避できる(実事業者に対する優位点として書ける)。
5. **規模自体がプライバシーパラメータ**(Where's Waldo効果)。25万人という規模は独立変数。
6. **復元率100%は原理的に不能**(No Free Lunch・部分同定性)→「復元率が上がらない」は失敗でなく**境界の測定**。
