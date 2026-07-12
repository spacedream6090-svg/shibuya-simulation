# 商業分析KPIとOOH広告効果量の較正リサーチ — 2026-07-11・担当Opus

> 目的: ユーザー要望2件へのリサーチ回答。(1)「**商業的に重要・必要な観点**をデータパイプラインに
> 追加して観察できるようにしたい」→ 小売・都市の商業分析KPIの業界標準を洗い出し、**各KPIを我々の
> L1イベントログから計算する式**を明記する。(2)「現実の渋谷の**OOH広告(街頭ビジョン・看板)**を
> シミュに追加、効果量は現実に忠実に較正したい」→ OOH/DOOHの接触→認知→来店→購買の**現実バンド
> (出典URL付き)**を集め、実装時の**較正推奨値**を提案する。
>
> 制約: 本ドキュメントは調査レポートのみ。`src/` `conf/` `data/` は一切変更していない。
> 誠実性の大前提(既存 [observation-commercial-data.md](./observation-commercial-data.md)・
> [calibration-20260709](../calibration/calibration-20260709.md) と同旨): 本シミュのエージェントは
> 架空人格であり、出力は「渋谷の実測」ではなく**「渋谷を模した社会モデル上の what-if 実験値」**。
> 効果量の現実バンドは公表統計・実証研究・業界レポートの**近似**であり、確証が取れない数値は
> 「**未確認・目安**」と明記する(捏造禁止)。

---

## 0. 結論(先出し)

1. **商業KPIの大半は既存L1で計算可能**。footfall(人流)・dwell time(滞在時間)・回遊・
   conversion(来店転換)・basket(客単価)・リピート率・時間帯×曜日は、`enter_building`/
   `exit_building`/`arrive`/`stay`/`move_segment`/`spend`/`weather` と `agents.json`(home)・
   `traits.json`(visitor)から導出できる。**新規イベントは不要**で、`scripts/observe.py`/
   `observe_flows.py` の流儀で「商業レポート派生層(L2/L3)」を足すのが最小コスト(§1・§6)。
2. **OOH広告は既存 `flyer_post`/`flyer_view` 機構の「高トラフィックnode・恒久・掲示者=公式/媒体」
   版として実装できる**。`flyer_view {author, node}` がすでに「通行人のユニーク接触」を記録し、
   制度DSL `rule_bonus(flyer_view)` が「接触→行動」のファネル足場を持つ(§6・§7)。
3. **効果量は「盛りすぎ」が最大リスク**。広告の売上弾力性はメタ分析で短期 **0.12**(872推定の
   平均。バイアス補正後は **0.0008**〜長期0.03まで下がる)、弾力性の**53%しか有意でなく、40%は
   0〜0.05に集中**する=「広告接触の大半は行動に影響しない」が実証の基調(§3)。OOH1接触あたりの
   来店リフトは、好調事例で数%〜十数%、**集団平均では数%が現実の天井**(§2)。
4. **渋谷スクランブル交差点は実データが豊富**。1日通行者 平日約26万・休日約39万・最大50万人、
   大型ビジョン視認率(媒体社公表)最大80%、渋谷駅前ビジョンは30秒×7日で75万円クラス(§2.6)。
5. **イベントROIは正負両方が現実**。渋谷ハロウィンは周辺店舗にはむしろ**マイナス**(センター街
   売上減・警備費年7,000万〜1億円)、一方スタジアム試合日は周辺決済額**平均+4.4%**。イベント=
   自動で売上増ではない、という非対称を実装バンドに入れるべき(§4)。

---

## 1. 小売・都市の商業分析KPI標準(+ 我々のL1からの計算式)

商圏・人流ビッグデータ企業(Placer.ai〈米〉、KDDI Location Analyzer / クロスロケーションズ〈日〉)
が商用提供する指標を軸に、**各KPIを我々のL1イベントから計算する式**を対応づける。凡例: イベント種は
`schema.py` の登録名、フィールドは payload のキー。位置は全イベント共通の `x,y` と `sim_min`(分)。

| # | KPI(業界標準) | 定義 | **我々のL1からの計算式** | 現実の代表値・出典 |
|---|---|---|---|---|
| 1 | **Footfall(人流・来訪数)** | ある地点/施設への来訪人数 | 施設: `enter_building{building,name}` のユニーク agent_id 数/時間バケット。街路: `move_segment{edge}` の edge 通過カウント(=通り単位の通行量)。地点: `arrive{node}`+`stay{node}` | Placer.ai は施設来訪数・来訪トレンドを主指標に。KLA は市区町村・町丁目単位で来訪者数を表示 [Placer](https://www.placer.ai/foot-traffic-analytics) / [KLA](https://k-locationanalyzer.com/domestic/uses/retail) |
| 2 | **Dwell time(滞在時間)** | 施設に滞在した時間 | `exit_building.sim_min − enter_building.sim_min`(同一 agent×building)。地点滞在は `arrive`→次 `route_start`/`move_segment` までの `sim_min` 差 | Placer.ai実測: Costco 37.3分・Walmart 31.8分・Target 28.7分(滞在長→バスケット大の相関) [growthfactor](https://www.growthfactor.ai/blog-posts/footfall-traffic-complete-guide) |
| 3 | **回遊 / Cross-shopping(店舗間遷移)** | 来訪者が前後にどこを訪れるか | 同一 agent×日の `enter_building` 系列 → building(→POI cat)間の**遷移行列**。同時来訪(co-visit)ペアで cross-shopping | Placer.ai「Cross-Shopping/Audience Overlap」、KLA「併用来訪・居住地別」 [growthfactor](https://www.growthfactor.ai/blog-posts/footfall-traffic-complete-guide) / [KLA feature](https://k-locationanalyzer.com/domestic/feature) |
| 4 | **商圏 / Catchment(Huffモデル)** | 来訪者の居住地分布・来訪確率 | `agents.json` の home と来訪POIの距離分布(`x,y`のユークリッド)。`traits.json` の `visitor` で来街者/居住者を層別。Huff: 来訪確率 P_ij = A_j/d_ij^b ÷ Σ_k A_k/d_ik^b(A=魅力度、d=距離、b=距離減衰) | Huffモデル(1963)は小売立地の標準。b(距離減衰)と A(売場面積等)で商圏を確率面で描く [GIS Geography](https://gisgeography.com/huff-gravity-model/) / [Mapular](https://mapular.com/glossary/huff-model) |
| 5 | **Conversion(来店転換率)** | 来訪→購買の割合 | ある building で `spend` を出した agent 数 ÷ `enter_building` した agent 数。**注意**: `spend{amount,cat,src}` に売り手/POIフィールドは無い→「その建物に在館中(enter〜exit間)のspend」で帰属する seam が要る(§6) | 実店舗の一般値 **20〜40%**(業態・立地依存。観光地は browsing で低く、目的来店は高い) [trurating](https://trurating.com/reports/retail-conversion-analysis/) / [getdor](https://www.getdor.com/blog/2026/04/28/what-is-a-retail-conversion-rate-the-complete-guide-for-store-owners/) |
| 6 | **客単価 / Basket(購買バスケット)** | 1来店あたり購入額・品目 | 1回の enter〜exit 間の `spend.amount` 合計=バスケット。`spend.cat`(food/shop/nightlife/taxi/lodging/medical/fixed_cost)別の平均・分布 | ARPV=総売上÷総来訪。Placer.ai は Average Revenue Per Visitor を財務接続指標に [growthfactor](https://www.growthfactor.ai/blog-posts/footfall-traffic-complete-guide) |
| 7 | **時間帯×曜日パターン** | 混雑の時間分布(Peak/Power hours) | 全イベントの `sim_min`→時刻バケット × `weather{weekday, holiday}` でヒートマップ。footfall/spend を層別 | Placer.ai「Peak Hours / Power Hours」、KLA「曜日・時間帯・居住/来街/勤務者別」 [growthfactor](https://www.growthfactor.ai/blog-posts/footfall-traffic-complete-guide) / [KLA feature](https://k-locationanalyzer.com/domestic/feature) |
| 8 | **リピート率 / Visit frequency** | 再訪する客の割合・頻度 | 同一 agent×building の再来訪(`enter_building` 反復)。リピート率=期間内に≥2回来訪した agent の割合。再訪間隔=来訪日の差分 | Placer.ai「Visit Frequency=ロイヤルティ指標」。KLA も来訪頻度を提供 [Placer](https://www.placer.ai/foot-traffic-analytics) |
| 9 | **Bounce / 素通り率** | 入ってすぐ出る割合 | dwell time が閾値(例<3分)以下の `enter_building` の割合 | Placer.ai「Bounce Rate=第一印象の問題を示す」 [growthfactor](https://www.growthfactor.ai/blog-posts/footfall-traffic-complete-guide) |
| 10 | **金流・注意ネットワーク**(独自) | 誰が金/注意を集めるか | 既実装 `scripts/observe_flows.py`: `spend`/`wage`/`rent`/`venture_sale`/`tax` の金流、`hear`/`sns_read`/`event_attend`/`flyer_view` の注意集中(gini) | 既存の観測系で対応済(本プロジェクト独自価値) |

**ベンダー指標の要点(実例)**
- **Placer.ai**(米): 携帯位置ビッグデータで来訪数・dwell time・cross-shopping・visit frequency・
  Peak/Power hours・ARPV を提供。「footfall だけでなく滞在・回遊・重複」を売る。
  [placer.ai/foot-traffic-analytics](https://www.placer.ai/foot-traffic-analytics)
- **KDDI Location Analyzer / クロスロケーションズ**(日): KDDIのGPS位置データで、来訪者数・**来店率**
  (対象施設への来訪者数÷母集団人口)・商圏(居住地別の集客)・曜日/時間帯/居住・来街・勤務者別の
  人流を可視化。最大6施設を同時比較。 [k-locationanalyzer.com/domestic/uses/retail](https://k-locationanalyzer.com/domestic/uses/retail)
- 共通の「来店率(visit rate)」= 商圏人口に対する実来訪者の割合。我々のL1では
  `enter_building` のユニーク数 ÷(商圏内 home を持つ agent 数)で近似できる。

---

## 2. OOH / DOOH 広告の効果量(現実バンド)

**段階モデル**: 通行量 →(視認率)→ 接触 →(想起率)→ 認知(recall)→(来店リフト)→ 来店 →
(conversion)→ 購買。各段で急激に人数が落ちる「漏斗」。以下、段ごとに出典付きの現実値を置く。

### 2.1 到達(Reach)の測り方 — 通行量 × 視認率

- OOHの impression は「その面の前を通る**通行量(traffic)** × その面を**視認する割合(視認率
  / visibility, VAC=Visibility Adjusted Contacts)**」で算定するのが業界標準(米 Geopath / OAAA、
  日 media社の視認率)。 [OAAA measurement](https://oaaa.org/resources/ooh-measurement/)
- 日本のインプレッション型DOOH(**LIVE BOARD**)は、ドコモの位置情報で「面の前に居た人数」を
  推定し、視認をインプレッションとして課金。従来の「場所×期間」買いから「データで届いた人数」へ。
  [liveboard.co.jp/new_ooh](https://liveboard.co.jp/new_ooh/)

| 指標 | 現実値 | 出典 |
|---|---|---|
| 大型ビジョンの視認率(渋谷ハチ公口) | **最大80%**(媒体社公表=**目安**。自己申告値) | [shunkosha](https://shunkosha.co.jp/column/ad_relation/18421-2) |
| billboard を過去30日に「気づいた」成人の割合 | **69%**(OOH全般では約90%) | [tastyad(Nielsen/OAAA集計)](https://www.tastyad.com/ooh-advertising-trends-stats-over-time-2019-2025/) |

### 2.2 認知(Recall)の現実値

| 指標 | 現実値 | 出典 |
|---|---|---|
| 過去1ヶ月にOOH広告を想起した買い物客 | **82%** | [tastyad(Nielsen/OAAA)](https://www.tastyad.com/ooh-advertising-trends-stats-over-time-2019-2025/) |
| デジタルビルボードの特定広告を想起(旅行者) | **74〜89%**(5都市6キャンペーン) | [OAAA Nielsen Poster Study 2017](https://oaaa.org/wp-content/uploads/2022/09/Nielsen-OAAA-Poster-Study-2017-FINAL.pdf) |
| OOHのブランド想起 vs デジタル媒体 | **47% vs 35%** | [tastyad(Nielsen)](https://www.tastyad.com/ooh-advertising-trends-stats-over-time-2019-2025/) |

> 注意: これら想起率は「見た/気づいた」の自己申告で高く出やすい。**認知≠行動**である点は§3で扱う。

### 2.3 来店リフト(Visit lift)の実測値 — ここが較正の核心

OOH接触群 vs 非接触群(位置情報でマッチング)の**増分来店/購買**。個別事例は幅が大きい:

| 事例 | リフト | 性質 | 出典 |
|---|---|---|---|
| フィットネスブランド(OOH+モバイル) | 来店 **+260%** | **上位事例(外れ値)** | [IAB](https://www.iab.com/news/ooh-mobile-integration/) |
| 好調OOHキャンペーンの短期ブランド行動(モバイル) | **+38%** | 上位事例 | [IAB](https://www.iab.com/news/ooh-mobile-integration/) |
| Jones Road Beauty(NYデジタルビルボード) | 新規注文 **+9%** | 単一事例 | [BlueAlpha](https://bluealpha.ai/articles/how-to-measure-ooh-advertising) |
| Jameson(ラスベガス Sphere) | 出荷(depletion)**+4.71%** | 単一事例 | [BlueAlpha](https://bluealpha.ai/articles/how-to-measure-ooh-advertising) |
| 日用品ブランド | 追跡来店 11,500件(全追跡来店の**53%**が当該店) | 帰属の分母注意 | [IAB](https://www.iab.com/news/ooh-mobile-integration/) |

> **読み方(較正上の最重要点)**: +260%や+38%は**「好調キャンペーンの上位」**であり典型ではない。
> 単一事例の+4.71〜9%が「うまくいった1媒体の増分」の現実的オーダー。**集団平均に均すと数%が天井**。
> かつOOHのブランドリフト測定は接触/非接触群のマッチングが甘く**過大に出やすい**という批判もある
> ([OOH TODAY](https://oohtoday.com/why-your-ooh-brand-lift-results-are-statistically-flawed/))。

### 2.4 反復接触(Frequency)と効果

- 古典理論「**effective frequency = 3**」(Krugman の3-hit)。行動に効くには複数回接触が要る。
- 広告効果は**adstock(残存効果)**として時間減衰しつつ累積する。decay係数は0〜1で、
  オフラインのブランド構築(TV等)は **0.4〜0.8**(半減期=数日〜数週で緩やか)、
  タクティカルなデジタル(検索)は **0.1〜0.4**(即効・短命)。
  [Wikipedia Adstock](https://en.wikipedia.org/wiki/Advertising_adstock) / [Recast](https://getrecast.com/adstock-rates/)
- キャンペーン終了後のcarryoverは **3週間〜6ヶ月**。 [Recast](https://getrecast.com/adstock-rates/)

### 2.5 DOOH(デジタル)と静的看板の差

| 指標 | 現実値 | 出典 |
|---|---|---|
| DOOH の brand lift(静的比) | **+49%**(消費者行動76%) | [mfour](https://www.mfour.com/wp-content/uploads/2025/08/DOOH-Delivers-49-Percent-More-Lift-and-76-Percent-Consumer-Action.pdf) |
| aided ad recall のリフト(静的 vs フルモーション) | **38% vs 41%**(差は僅か3pt) | DOOHベンチマーク(Happydemics/Vistar系) |
| 3Dモーション広告のトップオブマインド認知 | **+67%**(モーション無し比) | [ppc.land](https://ppc.land/3d-motion-dooh-ads-are-67-better-at-brand-awareness-study-finds/) |

> 要旨: DOOHは静的の**1.0〜1.5倍**のリフト係数が妥当な上限。ただし**想起の差は小さい(3pt)**ので、
> 「DOOHを万能に強くしない」のが誠実。強みは感情反応・エンゲージ・柔軟な出し分け側。

### 2.6 渋谷スクランブル交差点の実データ(ユーザー要望の一次収集)

| 指標 | 実データ | 出典 |
|---|---|---|
| 通行量(スクランブル交差点) | 1回の青信号(約2分間隔)で最大**2,000〜3,000人**。1日 平日**約26万人**・休日**約39万人**・最大**50万人**(2014渋谷再開発協会 流動計測ベース) | [Wikipedia](https://ja.wikipedia.org/wiki/%E6%B8%8B%E8%B0%B7%E3%82%B9%E3%82%AF%E3%83%A9%E3%83%B3%E3%83%96%E3%83%AB%E4%BA%A4%E5%B7%AE%E7%82%B9) / [tokyomarketingblog](https://tokyomarketingblog.com/50-shibuya-scramble) |
| 視認率(ハチ公口大型ビジョン) | **最大80%**(媒体社公表=目安) | [shunkosha](https://shunkosha.co.jp/column/ad_relation/18421-2) |
| 渋谷駅前ビジョン(料金・仕様) | 30秒素材/1時間×**7日で75万円**。主ビジョン262㎡+バナー90㎡=壁面計352㎡、9-24時放映(最短1日) | [media-pedia](https://www.media-pedia.com/media/2) |
| 主要ビジョンの1時間料金(15秒×4回/時) | 渋谷駅前ビジョン/Q'S EYE **20万円**、スターツビジョン **36.8万円**、109フォーラムビジョン **40万円** | [media-pedia](https://www.media-pedia.com/media/2) / [imitsu(PRONIアイミツ)](https://imitsu.jp/cost/transportation_advertising/article/shibuyaadvertising-price) |
| 長期・大型枠の目安 | 渋谷109シリンダー広告 **2週間約1,300万円**、東急ハチ公前壁面ビックシート **2週間約1,400万円** | [imitsu](https://imitsu.jp/cost/transportation_advertising/article/shibuyaadvertising-price) |

> 較正的含意: 我々の地図(スクランブル交差点=原点)の**中心node群を高トラフィックOOH面**として
> 設定できる。1面の日次接触規模は「そのnodeの `move_segment` 通過数 × 視認率」で内生的に決まり、
> 実データ(平日26万〜休日39万通行、視認率80%)がその上限アンカーになる。

---

## 3. 広告→行動のモデル化(先行例と「盛りすぎ」回避バンド)

### 3.1 マーケティングサイエンス/ABM の標準部品

- **Adstock / carryover(残存・減衰)**: 接触の効果を `A_t = imp_t + λ·A_{t-1}`(λ=decay)で
  累積・減衰。§2.4のλ=0.1〜0.8。 [Wikipedia Adstock](https://en.wikipedia.org/wiki/Advertising_adstock)
- **AIDA / ファネル**: Attention→Interest→Desire→Action の各段で歩留まり(§2の漏斗)。
  日本のDOOH実証(ビデオリサーチ×LIVE BOARD)では「ターゲティングDOOHはトップ&ミドルファネルに効く」
  =**認知・関心は動くが、最下段の行動転換は限定的**と整理される。 [videor](https://www.videor.co.jp/press/2024/240328.html)
- **閾値モデル(複雑感染)**: n回接触で初めて採用。我々の既存 `label_adopt`(閾値2)や
  `heard_counts→採用` が既にこの機構=OOHも「n回接触で来店確率bump」に自然に載る(§6)。

### 3.2 「盛りすぎ」を止める現実バンド(ベースレートの低さ)

これが**実装で最も効く節**。効果を大きくしたい誘惑への歯止め:

| 指標 | 現実値 | 出典 |
|---|---|---|
| 広告の**短期**売上弾力性(平均) | **0.12**(872推定のメタ分析。広告費2倍で売上+約12%) | [Sethuraman/Tellis/Briesch SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1866002) / [John Dawes](https://johndawes.info/2019/09/25/advertisings-short-term-influence-on-sales-a-lot-lower-than-thought/) |
| バイアス補正後の短期/長期弾力性 | 短期 **0.0008** / 長期 **0.03**(補正で従来推定を5倍以上圧縮) | [Korkames et al. 2025/2026 IJRM](https://www.sciencedirect.com/science/article/abs/pii/S016781162500028X) |
| 有意な弾力性の割合 | **約53%のみ**が0より有意。**40%超が0〜0.05**、40%超が0〜0.1 | 同上メタ分析 |

> 意味: **広告接触の大半は行動を変えない**。個別「+9%」「+260%」の裏には、無数の「効果ゼロ」の
> 接触がある。集団平均では弾力性0.1前後(補正すればさらに小さい)。よって**シミュのOOHは「接触した
> ほとんどのエージェントの行動を変えない」を既定**にすべき(§7の較正推奨値へ)。

---

## 4. イベント集客のROI(実測例・日本)

**イベント=自動で周辺売上増、ではない**。正負両方の実データを持つのが誠実。

| 事例 | 周辺への効果 | 出典 |
|---|---|---|
| **渋谷ハロウィン** | 周辺店舗にはむしろ**マイナス**。センター街当日売上は普段より大きく減、区の対策費 年**7,000万〜1億円**(2019ピーク)、2024来場約1.8万人でも「経済効果は薄い」。利益はドンキ(仮装グッズ)・クラブなど**限定的**。「公式主催者なしの自発的集合」 | [東洋経済](https://toyokeizai.net/articles/-/310227) / [ITmedia](https://www.itmedia.co.jp/business/articles/2211/01/news069_3.html) / [Wedge](https://wedge.ismedia.jp/articles/-/35715?layout=b) |
| **スタジアム試合日**(人流×決済データ) | 試合開催日の周辺**決済額 平均+4.4%**。土日昼開催でさらに増、試合前後に滞留・消費が増 | [日本経済研究所](https://www.jeri.or.jp/survey/202508-09_06/) / [Location AI](https://location-ai.com/solutions/visualizing-stadium-spillover/) |
| スポーツ施設の地域効果(政策資料) | 周辺の流動人口・消費増を高める取組が国のアクションプラン対象 | [MEXT](https://www.mext.go.jp/sports/content/1415586_02_2.pdf) / [METI](https://www.meti.go.jp/shingikai/mono_info_service/entertainment_creative/pdf/006_04_03.pdf) |

> 我々のL1対応: イベント開催=`event_host{node,start_step}`/`annual_event{name,date}`/
> `crowd_surge{node,level}`、周辺売上リフト=イベント前後・近接nodeの `spend`/`venture_sale` 増分。
> **ハロウィン型(集客↑・売上↓/マイナス)も再現できるよう、イベント→売上を一律プラスにしない**
> のが現実整合(混雑で入店不能=`stock_out`/回避で `spend` 減、という負のパスを持たせる)。

---

## 5. シミュレーションデータの商用価値(デジタルツイン / PLATEAU)

「シミュ発の商業レポート」需要が実在する観点。国交省 **PLATEAU**(全国3D都市モデルのオープンデータ化)
はデジタルツイン上で都市活動シミュレーション(人流・都市計画・防災)を進めており、**建物属性を用いた
都市状況分析**が商業含む各分野の用途として位置づけられている。
[mlit.go.jp/plateau](https://www.mlit.go.jp/plateau/) / [Use Case](https://www.mlit.go.jp/plateau/use-case/)

| 商業向け需要 | 内容 | 我々のシミュが出せるもの |
|---|---|---|
| **出店計画** | 立地の集客ポテンシャル・商圏・競合カニバリの事前評価 | §1のfootfall/dwell/回遊/Huff商圏 × POI別の what-if |
| **賃料査定の補助** | 人流・滞在・回遊の量で立地価値を序列化 | node/建物別の来訪・滞在・spend集計(既存 observe) |
| **広告枠価値算定** | OOH面の到達(通行量×視認率)と来店寄与の見積り | §2.6のnode通過数×視認率、接触→来店増分(§6・§7) |
| **イベント計画** | 開催の集客・周辺売上・混雑の事前評価(正負) | §4のイベント→spend/crowd_surgeの前後差分 |

> 誠実性の宣言(既存docと同一): これらは**実データによる較正を挟んだ「仮説生成・感度分析」**であって
> 実測の代替ではない。PLATEAU等の実データ層と組み合わせて初めて商用意思決定に使える。

---

## 6. 我々のL1へ「商業観点」を足す提案(観測パイプライン)

**コードは変更しない前提の設計メモ**。§1・§2のKPIを既存 `scripts/observe.py`/`observe_flows.py` の
流儀(読み出し専用のL2/L3派生層)で足せる。追加が要る seam を明示する:

1. **conversion の帰属 seam**: `spend` に売り手/POIフィールドが無い。→「agent が enter_building 中
   (enter〜exit の step 区間)に出した `spend` を、その building に帰属」する派生ロジックで解決。
   building→POI cat は地図(`map.py` の pois/buildings)で join。
2. **回遊・商圏の派生**: 同一 agent×日の `enter_building` 系列→遷移行列。home(`agents.json`)×
   来訪POIの距離→商圏。`traits.visitor` で来街/居住を層別。Huff の b(距離減衰)は較正パラメータ。
3. **OOH接触の観測**: **既存 `flyer_post`/`flyer_view` がそのまま「OOH面と接触」に対応**。
   `flyer_view{author, node}` のユニーク agent が「接触」、`move_segment{edge}` の node 通過が「到達
   母数」、接触後の `enter_building`/`spend` 増分が「来店リフト」。**接触群 vs 非接触群の差分**を
   観測する派生を足せば、§2.3の visit lift を内生的に測れる(A/B が世界内で自然発生)。
4. **既存の足場**: 制度DSL `rule_bonus{behavior=flyer_view/event_attend/park}` は「接触/来場に報酬」の
   機構=OOHファネルの実験レバーがすでにある。`sns_*`/`hear`/`news_read` と併せてチャネル横断の
   到達・転換比較(既存 [observation-commercial-data.md](./observation-commercial-data.md) §9)も可能。

> OOHを新イベントとして持ちたい場合でも、`register_event_kind("ooh_view", ...)` を1行足すだけの
> D12スキーマ設計(§schema.py)なので、`flyer_view` の高トラフィック・恒久・author=媒体/-1 版として
> 最小追加できる。**ただし実装はユーザー合意が前提**(本ドキュメントは提案のみ)。

---

## 7. 較正推奨値(OOH広告実装時のパラメータ提案)

§2〜§3の現実バンドから、OOH実装時の**接触率・行動転換率・減衰**を提案する。既存の較正流儀
([calibration-20260709](../calibration/calibration-20260709.md))に倣い、**基底 config は不変・
`production.yaml` の重ね書き**で、**現実バンド内**に収め、**観測性のための圧縮は明記した倍率だけ**許す。

| パラメータ | 推奨バンド | 根拠(現実値・出典) | 備考 |
|---|---|---|---|
| **視認率 p_see**(OOH面を通過した agent が接触=`flyer_view`する確率) | 大型ビジョン(高輝度・大)**0.3〜0.6**、通常看板 **0.1〜0.3** | 媒体公表の視認率 最大80%(§2.1・目安)は「見える」上限。認知ベースはこれより低い | node/面サイズ別。スクランブル中心node=高め |
| **想起率 p_recall**(接触者のうち記憶に残る割合) | **0.3〜0.5** | OOH想起率は自己申告で高い(47〜82%)が、行動接続する「意味のある想起」はこれより低く見る | adstock に載る「有効接触」だけ残す |
| **来店転換 lift**(1接触あたりの来店/消費確率の上乗せ) | **乗数 ×1.02〜×1.15**(上限)、絶対上乗せ **0.1〜1.0%pt** | 好調事例+4.71〜+9%(§2.3)、広告弾力性0.12・**53%のみ有意・40%は0〜0.05**(§3.2) | **既定は ×1.05 程度に抑える**。大半の接触は無効果 |
| **有効フリークエンシー**(効果が立つ接触回数) | **3回**(閾値モデル。既存 `label_adopt` 閾値機構を流用可) | Krugman 3-hit(§2.4) | 1〜2回接触は微小、3回目で bump 最大 |
| **adstock 減衰 λ**(接触効果の日次残存率) | **0.7〜0.9/日**(半減期 数日〜1〜2週) | オフライン/ブランドの decay 0.4〜0.8、carryover 3週〜6ヶ月(§2.4) | step単位なら λ^(steps/day)。数日〜2週で消える |
| **DOOH係数**(静的看板比のリフト倍率) | **1.0〜1.5倍** | DOOH +49% lift、ただし aided recall 差は3pt(§2.5) | DOOHを万能に強くしない |
| **集団総量ガード**(全体の来店リフト上限) | 平均来店リフト **数%〜十数%を超えない**総量キャップ | 集団平均では弾力性0.1前後が天井(§3.2)、イベントは負もありうる(§4) | 「盛りすぎ」検知の安全弁 |

**設計原則(まとめ)**:
1. **既定は「効かない」**。接触したエージェントの**大多数は行動を変えない**を出発点に置く
   (弾力性0.12・有意53%・40%が0〜0.05)。効果は少数の閾値到達者に集中させる。
2. **漏斗で必ず削る**: 通行量 →(p_see)→ 接触 →(p_recall・3回閾値)→ 有効接触 →(×1.02〜1.15)→
   来店。各段で人数が落ち、最終の集団リフトが数%に収まることを observe で確認(§6のA/B差分)。
3. **減衰で消す**: adstock λ=0.7〜0.9/日で、接触の記憶は数日〜2週で消える。恒久的なブーストにしない。
4. **負のパスも許す**: イベント/OOHで人は集まっても売上が上がらない・むしろ減る(ハロウィン型)を
   `stock_out`/回避で表現可能に。イベント→売上を一律プラスにしない。
5. **実データでアンカー**: スクランブル交差点の通行量(平日26万〜休日39万)・視認率80%・
   ビジョン料金(§2.6)を、面の接触規模と枠価値算定の上限アンカーに使う。
6. **検証は短縮ラン**([validation-runs-short] 準拠): 較正後は mock または ≤24step スモークで
   「接触率・来店リフト・減衰」が上記バンド内かを確認してからフルランへ。

---

## 出典(URL)

**商業KPI・人流ベンダー**
- Placer.ai 人流分析: https://www.placer.ai/foot-traffic-analytics
- 人流KPI(dwell time等)概説(Placer実測値含む): https://www.growthfactor.ai/blog-posts/footfall-traffic-complete-guide
- KDDI Location Analyzer(小売用途): https://k-locationanalyzer.com/domestic/uses/retail
- KDDI Location Analyzer(機能一覧): https://k-locationanalyzer.com/domestic/feature
- Huffモデル: https://gisgeography.com/huff-gravity-model/ / https://mapular.com/glossary/huff-model
- 小売コンバージョン率ベンチマーク: https://trurating.com/reports/retail-conversion-analysis/ / https://www.getdor.com/blog/2026/04/28/what-is-a-retail-conversion-rate-the-complete-guide-for-store-owners/

**OOH / DOOH 効果量**
- OAAA OOH measurement: https://oaaa.org/resources/ooh-measurement/
- Nielsen/OAAA OOH統計集計(想起82%・気づき69%等): https://www.tastyad.com/ooh-advertising-trends-stats-over-time-2019-2025/
- OAAA Nielsen Poster Study 2017(デジタルビルボード想起74-89%): https://oaaa.org/wp-content/uploads/2022/09/Nielsen-OAAA-Poster-Study-2017-FINAL.pdf
- OOH来店リフト事例(IAB): https://www.iab.com/news/ooh-mobile-integration/
- OOH来店/購買リフト事例(BlueAlpha): https://bluealpha.ai/articles/how-to-measure-ooh-advertising
- OOHブランドリフト測定の統計的問題: https://oohtoday.com/why-your-ooh-brand-lift-results-are-statistically-flawed/
- DOOH vs 静的(+49% lift): https://www.mfour.com/wp-content/uploads/2025/08/DOOH-Delivers-49-Percent-More-Lift-and-76-Percent-Consumer-Action.pdf
- 3Dモーション広告+67%: https://ppc.land/3d-motion-dooh-ads-are-67-better-at-brand-awareness-study-finds/
- LIVE BOARD(インプレッション型DOOH・ドコモ位置情報): https://liveboard.co.jp/new_ooh/
- ターゲティングDOOH実証(ビデオリサーチ×LIVE BOARD): https://www.videor.co.jp/press/2024/240328.html

**広告モデル・弾力性(盛りすぎ回避)**
- Advertising adstock(Wikipedia): https://en.wikipedia.org/wiki/Advertising_adstock
- Adstock decay rates(Recast): https://getrecast.com/adstock-rates/
- 広告弾力性メタ分析 872推定(Sethuraman/Tellis/Briesch): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1866002
- 広告の短期効果は低い(John Dawes解説): https://johndawes.info/2019/09/25/advertisings-short-term-influence-on-sales-a-lot-lower-than-thought/
- バイアス補正メタ分析(短期0.0008/長期0.03): https://www.sciencedirect.com/science/article/abs/pii/S016781162500028X

**渋谷スクランブル交差点 OOH 実データ**
- 通行量(Wikipedia 渋谷スクランブル交差点): https://ja.wikipedia.org/wiki/%E6%B8%8B%E8%B0%B7%E3%82%B9%E3%82%AF%E3%83%A9%E3%83%B3%E3%83%96%E3%83%AB%E4%BA%A4%E5%B7%AE%E7%82%B9
- 通行量50万人(補足): https://tokyomarketingblog.com/50-shibuya-scramble
- 視認率80%(shunkosha): https://shunkosha.co.jp/column/ad_relation/18421-2
- 渋谷駅前ビジョン 料金・仕様(media-pedia): https://www.media-pedia.com/media/2
- 渋谷OOH料金一覧(PRONIアイミツ): https://imitsu.jp/cost/transportation_advertising/article/shibuyaadvertising-price

**イベントROI**
- 渋谷ハロウィン(東洋経済): https://toyokeizai.net/articles/-/310227
- 渋谷ハロウィン 地元にカネが落ちない(ITmedia): https://www.itmedia.co.jp/business/articles/2211/01/news069_3.html
- 渋谷ハロウィン 警備費と経済効果(Wedge): https://wedge.ismedia.jp/articles/-/35715?layout=b
- スタジアム試合日 周辺決済+4.4%(日本経済研究所): https://www.jeri.or.jp/survey/202508-09_06/
- スタジアム波及効果の人流可視化(Location AI): https://location-ai.com/solutions/visualizing-stadium-spillover/
- スタジアム・アリーナの経済効果(MEXT): https://www.mext.go.jp/sports/content/1415586_02_2.pdf

**デジタルツイン / PLATEAU**
- PLATEAU(国交省): https://www.mlit.go.jp/plateau/
- PLATEAU Use Case: https://www.mlit.go.jp/plateau/use-case/

> 集計・確認は読み取り専用で実施(本リポジトリのコード・データは未変更)。数値のうち媒体社公表の
> 視認率、上位キャンペーン事例(+260%/+38%)は「目安/上位事例」と本文で明記した。
