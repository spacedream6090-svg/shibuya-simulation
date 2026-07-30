# デジタルツイン/3Dシミュレーション業界 — 大枠調査

調査日: 2026-07-30 / 担当: 調査サブエージェント(大枠担当)
目的: shibuya-simulation(LLM人工社会シミュレーション・決定論・L1イベントログ事後観測・PLATEAU実高さ/3D再生/SUMO連成/UEエクスポート既保有)と、企業が開発する3Dデジタルツイン(DT)の「組み合わせ方」を判断するための地図。

**読み方の約束**
- すべての主張にURLを付す。未確認・推測は「【未確認】」と明記する。
- マーケティング文言と「実際にダウンロード/購入して使える実体」を区別する。後者を優先して書く。
- 検索は英語・日本語の両方に当たった。ただし本エージェントは大枠担当であり、各製品の詳細APIレベルは別エージェントの深掘りに委ねる。

---

## 1. グローバル主要プラットフォーム

### 1.1 NVIDIA Omniverse(+OpenUSD / SimReady / Cosmos)

**何を提供するか**: Omniverseは「物理AI(Physical AI)アプリケーション開発」を掲げる開発プラットフォーム群。単一製品ではなく、OpenUSDベースのシーン記述・RTXレンダリング・PhysX物理・Kit SDK(アプリ組み立てフレームワーク)・各種ライブラリの集合体。
- 公式: https://www.nvidia.com/en-us/omniverse/
- 2026年GTCでの位置づけ(仮想世界=物理AI時代の基盤): https://blogs.nvidia.com/blog/gtc-2026-virtual-worlds-physical-ai/

**データ形式**: OpenUSD(Universal Scene Description)が中核。CADデータ・シミュレーション資産・実世界テレメトリを共通のシーン記述言語に集約する設計。加えて「SimReady」アセット規約(物理属性・セマンティックラベル付きの3Dアセット規格)がある。
- OpenUSD/SimReadyの説明: https://developer.nvidia.com/blog/creating-immersive-events-with-openusd-and-digital-twins
- SimReadyの商用例: https://smartspatial.com/company/nvidia-omniverse

**API/SDK**: Omniverse Kit SDK(Python/C++拡張)、USD API、PhysX、各種Blueprint(リファレンス実装)。2026年GTCではデータセンター向け「Omniverse DSX Blueprint」が発表され、ギガワット級AIファクトリのDTを OpenUSD + SimReady + 電力/熱シミュレーションで構成するリファレンスが公開されている(=都市ではなく施設スケール)。
- DSX Blueprint: https://www.hpcwire.com/aiwire/2026/06/02/vertiv-introduces-1st-converged-physical-infrastructure-digital-twin-for-nvidia-omniverse-dsx/

**ライセンス/費用感**: **2026年に大きく変わった。** 2026年5月時点で Omniverse は開発・本番利用・再配布まで無償(コミュニティサポート)になったと複数の二次情報が報じている。以前は開発無償+本番は NVIDIA AI Enterprise サブスク($4,500/GPU/年、永続$22,500/GPU、クラウド$1/GPU時 が公表list価格だった)という構造。エンタープライズサポートが要るなら NVIDIA AI Enterprise を別途購入。
- 無償化の報道: https://www.storagereview.com/news/nvidia-quietly-makes-omniverse-free-for-production-use
- 同件の解説(Launcher廃止も同時): https://roughcut.dev/writing/the-omniverse-license-change-you-might-have-missed/
- 一次情報に近い規約PDF(2025.01.30版・無償化前の版である点に注意): https://www.nvidia.com/content/dam/en-zz/Solutions/license-agreements/enterprise-software/NVIDIA-Product-Specific-Terms-for-Omniverse-2025.01.30.pdf
- 【未確認】無償化の一次ソース(NVIDIA公式のライセンス改訂告知ページ)には本調査では到達できていない。二次情報が複数一致しているため事実性は高いと見るが、実際に採用判断する前に最新の Product Specific Terms を直接確認すべき。

**Cosmos(世界基盤モデル)**: Omniverseの隣接製品。物理環境の「次に何が起きるか」を予測する world foundation model。2026年に Cosmos 3 が発表され、20兆トークン・約10億画像・4億の実+合成動画で学習、ロボット/AVの合成データ生成が主用途。
- 公式発表: https://nvidianews.nvidia.com/news/nvidia-announces-major-release-of-cosmos-world-foundation-models-and-physical-ai-data-tools
- 原論文(Cosmos WFM Platform): https://arxiv.org/html/2501.03575v1
- 開発者向け解説: https://developer.nvidia.com/blog/scale-synthetic-data-and-physical-ai-reasoning-with-nvidia-cosmos-world-foundation-models

**社会シム(エージェント)を上に載せる観点**: 最強の「幾何+物理+レンダリング」層だが、**上に載るエージェントは想定上ロボット/車両/歩行者の身体エージェントであり、社会的意思決定エージェントではない**。我々にとっては「可視化+合成データ生成」の受け皿として非常に強く、意思決定の場としては過剰。Kit の Python 拡張から外部シミュレータを駆動する形が現実的。

### 1.2 Siemens(Xcelerator / Digital Twin Composer)

**何を提供するか**: Siemens Xcelerator は産業向けの「ハード+ソフト+サービス」プラットフォーム。都市DTは単体製品というより、Building Twin / Campus Twin / Energy Twin を束ねた事例駆動の提供。旗艦事例が **Siemensstadt Square**(ベルリン、約188エーカー・約35,000人が住み働く街区)のエンドツーエンドDT。
- 事例プレスリリース: https://press.siemens.com/global/en/pressrelease/siemens-leverages-siemens-xcelerator-transform-industrial-location-city-future-digital
- 解説記事: https://www.automation.com/en-us/articles/july-2024/siemens-xcelerator-industrial-site-city-future
- Digital City Twin(社史ページ): https://www.siemens.com/global/en/company/about/history/specials/175-years/digital-city-twin.html

**2026年の新規**: CES 2026 で **Digital Twin Composer** を発表。Siemens Xcelerator と NVIDIA Omniverse を統合し、写実的DTを作るツールと説明されている(=Siemens側もOmniverseを描画/物理層として採用する方向)。
- https://news.siemens.com/en-us/digital-twin-composer-ces-2026/
- 製品ページ: https://www.siemens.com/en-us/company/digital-transformation/industrial-metaverse/introducing-digital-twin-composer/

**データ形式/API/費用**: 【未確認】都市スケールで「ダウンロードして使える実体」は本調査では特定できなかった。Xcelerator は基本的にエンタープライズ商談ベース(価格非公開)。Siemens は歩行者シミュレーション文脈でも語るが、公開SDKで社会エージェントを載せる道筋は見えない。
- 「スマートシティの人」記事(歩行者シミュレーション言及): https://www.siemens.com/global/en/company/stories/research-technologies/digitaltwin/people-in-smart-cities.html

**社会シムを載せる観点**: 適合度は低い。閉じたエンタープライズ提供で、我々が外部から使える公開APIの実体が見えない。ただし「Omniverseを描画層に採用する大手」という業界トレンドの証左として重要。

### 1.3 Dassault Systèmes(3DEXPERIENCE / 3DEXPERIENCity / Virtual Singapore)

**何を提供するか**: 3DEXPERIENCE プラットフォーム上の都市向けソリューション 3DEXPERIENCity。代表事例が **Virtual Singapore**(2014年12月開始、National Research Foundation・Singapore Land Authority・GovTech の共同主導)。
- Dassault 顧客事例ページ: https://www.3ds.com/insights/customer-stories/virtual-singapore
- 開始時のプレスリリース: https://investor.3ds.com/news-releases/news-release-details/dassault-systemes-and-national-research-foundation-collaborate
- Wikipedia(概況・完了時期): https://en.wikipedia.org/wiki/Virtual_Singapore

**現況**: Virtual Singapore は **2022年に完了**したとされる。政府部門向けの限定アクセスであり、一般に開かれたデータ配信基盤ではない。
- 【未確認】完了後の後継プログラム名・現在の一般公開範囲は本調査で確定できなかった。「Virtual Singapore は成功したので他都市に横展開する」という Dassault 側の意向表明は確認できるが、それ以上の実体は不明。

**社会シムを載せる観点**: 適合度は低い。クローズドな政府向け。ただし「都市DTは10年がかりの国家プロジェクト規模になる」というスケール感の参照点として有用。

### 1.4 Bentley Systems(iTwin Platform)

**何を提供するか**: インフラDTアプリを作るためのクラウド開発者スタック(API群+サービス)。iModel(独自のBIM/インフラモデルコンテナ)の連合、変更追跡、可視化、IoTセンサ/ドローンからの実世界状態の取り込み。
- 公式開発者ポータル: https://developer.bentley.com/itwinplatform/
- API一覧: https://developer.bentley.com/apis/
- GitHub組織(OSS部分あり): https://github.com/Bentley-iTwin

**データ形式/API**: iModel が中核フォーマット。REST API 群(iTwins・データ管理・可視化・レポート等)。iTwin.js は OSS。

**ライセンス/費用感**: クレジット制サブスク。Community($0・月100クレジット)/Standard/Premium/Enterprise の4段。超過クレジットは$1.20/クレジット。iModelの入出力・ストレージ・可視化・レポート行数・リアリティモデリングジョブがそれぞれクレジット単位で従量課金。
- 価格プラン(第三者まとめ): https://apis.io/plans/bentley-systems/bentley-systems-plans-pricing/
- 機能/価格まとめ(第三者): https://bimtoolshub.com/bentley-itwin-platform
- 【未確認】Communityプランの正確な現行条件は Bentley 公式の価格ページで再確認が必要(第三者まとめに依拠している)。

**社会シムを載せる観点**: 適合度は中〜低。強みは「インフラ資産の正確なジオメトリ+変更履歴」であって群衆/社会挙動ではない。無償Communityティアがあるのは試すハードルが低い点で好材料だが、渋谷という都市単位のデータを我々が持ち込む必要があり、PLATEAUで足りる部分と重複する。

### 1.5 Microsoft Azure Digital Twins

**何を提供するか**: 「モノとその関係」をグラフとしてモデル化するPaaS。3Dレンダリングエンジンではなく、**DTのセマンティックグラフ+テレメトリのバックエンド**である点が他と決定的に違う。
- モデル概念: https://learn.microsoft.com/en-us/azure/digital-twins/concepts-models
- モデル管理: https://learn.microsoft.com/en-us/azure/digital-twins/how-to-manage-model

**データ形式**: DTDL(Digital Twins Definition Language)。JSON-LDベース。v2とv3をサポートし、v3が推奨。仕様はOSSで公開。
- DTDL仕様リポジトリ: https://github.com/Azure/opendigitaltwins-dtdl

**API/SDK**: REST + 各言語SDK(.NET/Java/JS/Python)。Azure Digital Twins Explorer という可視化ツールあり(DTDL v3は限定サポート)。
- Explorer の現況(v3限定サポートの記述): https://learn.microsoft.com/en-us/answers/questions/4372601/azure-digital-twin-explorer-preview

**費用感**: Azure従量課金(操作数・メッセージ数ベース)。【未確認】具体的単価は本調査で価格ページに到達していない。

**廃止/後退の噂について**: 「DTDL/Azure Digital Twins が2026年に廃止される」という情報は**本調査では確認できなかった**。確認できたのは2023年5月2日にプレビュー版コントロールプレーンAPIが廃止された件のみ。
- https://learn.microsoft.com/en-us/azure/digital-twins/resources-migrate-from-preview-apis
- 【未確認】製品の将来性についてはMicrosoft公式ロードマップの直接確認を推奨。

**社会シムを載せる観点**: 適合度は中。我々の「L1イベントログ」を時系列テレメトリとして流し込み、エージェント/場所をDTDLグラフで表現すれば、標準的なDTセマンティクスに乗る。ただし**3Dは自前で用意する必要があり**、当プロジェクトが既にPLATEAU+UEを持っている以上、ここが必須になる場面は限定的。「企業DTと接続する共通語彙」としての価値が主。

### 1.6 Unity / Unreal Engine の都市DT活用

**Unreal Engine 5 City Sample**: The Matrix Awakens のシティシーンをそのまま公開したサンプルプロジェクト。ビル・車両・MetaHuman群衆を含む。World Partition・Nanite・Lumen・Chaos・Rule Processor・**Mass AI**・Niagara・MetaHumans を実際にどう使ったかが読める。約93GB。無償ダウンロード(Fab経由)。
- Fab配布ページ: https://www.fab.com/listings/4898e707-7855-404b-af0e-a505ee690e68
- 解説(構成要素の内訳・City Sample Buildings/Vehicles/Crowds の3パック): https://www.cgchannel.com/2022/04/download-epic-games-free-city-sample-assets-for-ue5/
- 解説: https://80.lv/articles/city-sample-from-the-matrix-demo-released-for-ue5

  ここで重要なのは **Mass AI**(UEのECSベース大量エージェントフレームワーク)。数千〜数万体の群衆/交通を描画する実績あるランタイムであり、**我々の「LLMが決めた行動を、大量体で描画する」層としてほぼそのまま使える**。UEライセンスは通常のEpicライセンス(売上100万USD超で5%ロイヤリティ、非ゲーム用途は別条件)。
  - 【未確認】2026年時点のUEライセンス最新条件(非ゲーム/シミュレーション用途のシート課金)は本調査で確認していない。Epic の現行ライセンスページで要確認。

**Unity**: PLATEAU SDK for Unity が公式提供されている(後述2節)。Unity側の都市DT向け商用パッケージ(Unity Industry等)は【未確認】。
- PLATEAU SDK for Unity(Asset Store): https://assetstore.unity.com/PLATEAU-SDK

**社会シムを載せる観点**: **適合度は最高**。理由は(a)我々が既にUEエクスポート設計を持っている(b)City Sample が「大量エージェント+都市」の完成された参照実装である(c)無償で実物が手に入る(d)描画専用なので「観測がシムを変えない」原則と衝突しない。

### 1.7 Cesium(3D Tiles / CesiumJS / 各エンジンプラグイン)

**何を提供するか**: 巨大で異種混合な3D地理空間データのストリーミング標準 **3D Tiles** と、その参照実装群。
- 3D Tiles 概要: https://cesium.com/why-cesium/3d-tiles/
- 仕様(OGC Community Standard 1.0): https://docs.ogc.org/cs/18-053r2/18-053r2.html
- 仕様 1.1: https://docs.ogc.org/cs/22-025r4/22-025r4.html
- OGCコミュニティ標準化の経緯(2019年2月): https://cesium.com/blog/2019/02/05/3d-tiles-ogc-community-standard/
- 仕様リポジトリ: https://github.com/CesiumGS/3d-tiles

**ライセンス**: CesiumJS / Cesium for Unreal / Cesium for Unity はすべて **Apache 2.0 の OSS**。オープンコアモデルで、クラウドのタイリングパイプラインやコンテンツ(Cesium ion)が商用。
- Cesium for Unreal: https://cesium.com/platform/cesium-for-unreal/ / https://github.com/CesiumGS/cesium-unreal
- Cesium for Unity: https://cesium.com/platform/cesium-for-unity/ / https://github.com/CesiumGS/cesium-unity
- Omniverse/O3DE版も含む解説: https://www.cgchannel.com/2023/03/free-cesium-plugins-unreal-o3de-unity-omniverse/

**社会シムを載せる観点**: 適合度は高。**3D Tiles は「都市ジオメトリの共通輸送形式」としてPLATEAU・東京都データ・海外DTを横断できる**。我々はPLATEAU実高さを既に持っているので、3D Tilesで出力できれば Web(CesiumJS)でも UE でも Omniverse でも同じ地形の上に再生できる。エンジン非依存の保険として価値が高い。

---

## 2. 日本の都市デジタルツイン

### 2.1 Project PLATEAU(国土交通省)

**全体像**: 2020年12月に国交省が開始した、全国の3D都市モデルの整備・オープンデータ化プロジェクト。CityGMLベースで、建築物・道路・都市計画情報・土地利用・災害リスクなどを含む。
- 公式: https://www.mlit.go.jp/plateau/
- データポータル(G空間情報センター): https://front.geospatial.jp/plateau_portal_site/

**「実際に使える実体」の内訳**(ここが我々にとって最重要):
1. **PLATEAU 配信サービス** — CityGML本体だけでなく、**3D Tiles / MVT(ベクトルタイル) / terraindb(地形) / オルソ画像タイル**の各形式で配信。REST API(データカタログAPI・仕様書API・CityGML Pack API等)と **GraphQL API** が公開されている。全データセット無償。ただしドキュメント自身が「**あくまで試験的な運用であるため、提供期間やサービスレベルについては保証できない**」と明記している点は要注意。
   - https://docs.plateauview.mlit.go.jp/intro/
   - 利用チュートリアル(公式リポジトリ): https://github.com/Project-PLATEAU/plateau-streaming-tutorial
2. **PLATEAU SDK for Unity / PLATEAU SDK for Unreal** — 3D都市モデルをゲームエンジンに取り込む公式ツールキット。2023年3月に正式版がGitHubで公開。自動車で走行できるサンプルも付属。
   - Unreal版リポジトリ: https://github.com/Project-PLATEAU/PLATEAU-SDK-for-Unreal
   - Unity版(Asset Store): https://assetstore.unity.com/PLATEAU-SDK
   - 公開時の報道: https://www.moguravr.com/project-plateau-sdk/ / https://gamemakers.jp/article/2023_03_02_33079/
3. **PLATEAU VIEW 3.0** — ブラウザビューア。OSSのWeb GISプラットフォーム **Re:Earth** ベースでWebGL利用。任意形状/高さの建物を描く機能、Googleストリートビュー連携などを持つ。データセットの一元管理とAPI提供を含む。
   - 国交省リリース: https://www.mlit.go.jp/report/press/toshi03_hh_000129.html
   - Re:Earth側の開発者解説: https://note.com/eukarya/n/n75c8eea7b31e
   - 【未確認】Re:Earth CMS / Re:Earth Visualizer の一般提供は「2025年半ば頃」と告知されていたが、2026年7月時点での実際の提供状況は本調査では未確認。

**渋谷区のデータ**: 3D都市モデル(Project PLATEAU)渋谷区 2023年度版がオープンデータとして公開されている。商用・非商用問わず利用可。
- https://search.ckan.jp/datasets/www.geospatial.jp__ckan__dataset:plateau-13113-shibuya-ku-2023
- 【未確認】より新しい年度版(2024/2025年度)の渋谷区データの有無は未確認。2025年度版は他区(例: 文京区)で存在するのを確認: https://www.geospatial.jp/ckan/dataset/plateau-13105-bunkyo-ku-2025

**我々との接点仮説**: 既に活用済みの前提だが、未使用なら **(a) 3D Tiles配信の直接利用**(CityGMLを自前変換しない)、**(b) 用途地域/土地利用/災害リスク属性をエージェントの環境変数として使う** の2点が上積み余地。特に(b)は「渋谷のどの街区が商業/住居か」をシムの意味論に持ち込める。

### 2.2 東京都デジタルツイン実現プロジェクト

**内容**: 「スマート東京」の一環。2024年10月31日に**区部(23区)の高精度3次元点群データを公開**。点群以外にDEM、オルソ画像、赤色立体地図なども公開されており、**商用・学術・個人を問わず二次利用可能**。
- 公式(3Dモデルでみる東京): https://info.tokyo-digitaltwin.metro.tokyo.lg.jp/3dmodel/
- 公開の報道: https://gamemakers.jp/article/2024_11_08_84819/
- ビューアの解説: https://ledge.ai/articles/3d_viewer_tokyo_open_data
- QGISでの実際の読み込み手順(第三者ブログ・実務的): https://qgis.mierune.co.jp/posts/usecase_tokyo-23-pcd

**ビューア**: 「東京都デジタルツイン3Dビューア(β版)」。データカタログからデータを3D地図に重ね、手元のCSV/KMLをアップロードして可視化できる。
- 3Dビジュアライゼーション実証(日照・風況等)の初期段階: https://mag.tecture.jp/culture/20210129-21291/

**我々との接点仮説**: **点群は「PLATEAUの箱型建物より現実に近い渋谷の見た目」を得る最短ルート**。ただし点群はエージェントのナビゲーションには直接使いにくい(メッシュ化が要る)。**背景ビジュアル用途としては極めて相性が良い**。また「CSVをアップロードして3D上に可視化」というビューアの機能は、我々のL1イベントログ集計を都の公式ビューア上に重ねる、という軽量な可視化経路になりうる。【未確認】アップロード可能なCSVの形式仕様・件数上限は未確認。

### 2.3 渋谷に関係する取り組み

**渋谷区スマートシティ推進基本方針**(2024年11月22日版PDF): 交通・教育・エネルギー等の分野横断で、民間企業・大学と連携してデータを活用する方針。
- https://files.city.shibuya.tokyo.jp/assets/12995aba8b194961be709ba879857f70/5e37c20d9c124c1fa7009395de4273ea/shibuya-smartcitykihonhoushin-zentai-20241122.pdf

**デジタルツイン渋谷プロジェクト**(2021年11月開始): Symmetry Dimensions・渋谷未来デザイン・渋谷データコンソーシアム参加企業による。第1弾は**笹幡(ササハタハツ)エリア**(玉川上水旧水路緑道)の点群+PLATEAU+企業データをブラウザ/ARグラスで可視化。街路樹の樹種・サイズを樹木診断データから表示するなど。
- 渋谷未来デザインのプレスリリース: https://prtimes.jp/main/html/rd/p/000000145.000033690.html
- 報道: https://ascii.jp/elem/000/004/074/4074709/ / https://digital-shift.jp/flash_news/FN211110_3
- Symmetry Dimensions のDT製品ページ: https://symmetry-dimensions.com/jp/digital-twin/
- 【未確認】2021年の発表以降の進捗・成果物の公開有無は本調査で確認できなかった。**渋谷駅周辺(我々の主舞台)ではなく笹幡エリアが対象**である点に注意。

**バーチャル渋谷 / KDDI**: 2020年5月に「渋谷5Gエンターテイメントプロジェクト」(KDDI・渋谷未来デザイン・渋谷区観光協会)が立ち上げた**日本初の自治体公認の都市連動型メタバース**。プラットフォームは cluster。2022年には「デジタルツイン渋谷」を拡張する取り組みも発表。
- KDDI 2022年リリース(デジタルツイン渋谷の拡張): https://news.kddi.com/kddi/corporate/newsrelease/2022/10/27/6354.html
- 1DAYイベントパッケージ: https://creatorzine.jp/news/detail/2570
- 背景解説: https://xtrend.nikkei.com/atcl/contents/18/00621/00005/
- 【未確認】2025-2026年時点でのバーチャル渋谷の運営継続状況・データ公開有無は未確認。**これは「人が入るメタバース」であって「シミュレーション基盤」ではない**点が重要な区別。

**我々との接点仮説**: 渋谷という土地には既に複数の「DT」を名乗る取り組みがあるが、**いずれも可視化・体験側**であり、**社会的意思決定のシミュレーションは空白**。ここが我々の差別化ポイントであると同時に、「可視化層は既存資産を借りられる」ことも意味する。

### 2.4 建設系(スーパーゼネコン)

- 鹿島・大林組・安藤ハザマ等が**現場管理用途**でDTを活用しているとの報道(日経、2025年9月)。
  - https://www.nikkei.com/article/DGXZQOUC176PJ0X10C25A9000000/ (有料記事の可能性あり)
- 竹中・清水・鹿島の担当者が建設DXフォーラムに登壇(2025年6月)。D3B(Data Driven Design Build)等が話題。
  - https://jbpress.ismedia.jp/articles/-/88695 / https://jbpress.ismedia.jp/articles/-/85893
- 日立ソリューションズ「都市・建物向け xRトータルソリューション」(DT+xRで設備管理を効率化):
  - https://cloud.watch.impress.co.jp/docs/news/1443869.html

**評価**: **建設系DTは「建物単体・工事現場」のスコープが中心で、街区スケールの社会挙動を扱う公開資産は本調査では見つからなかった。** 我々との接点は薄い。【未確認】各社の非公開の街区DT研究は当然あり得るが、外部から使える実体は確認できず。

### 2.5 通信系(人流データ)

3社の主力人流データ商品:
- **NTTドコモ「モバイル空間統計」** — 携帯ネットワークから、いつ・どんな属性の人が・どこからどこへ移動したかの人口統計。全国500mメッシュ〜都心部125mメッシュの粒度。
  - 公式: https://www.nttdocomo.co.jp/biz/service/spatial_statistics/
  - e-Stat のビッグデータポータル掲載: https://www.e-stat.go.jp/bigdataportal/dataintro/130
- **KDDI「位置情報ビッグデータ」**、**ソフトバンク子会社 Agoop「流動人口データ」**。
  - 3社比較の記事(日経xTECH): https://xtech.nikkei.com/atcl/nxt/column/18/01304/051900003/
  - 測位方式の違いの解説: https://www.data-clew.net/atoz/point/positioning-method.html

**我々との接点仮説**: **これが最も直接的に効く**。我々のシムの「較正(calibration)の現実側データ」として、渋谷の時間帯別・属性別の滞留/流動が使える。ただし**いずれも有償の商用データ**であり、無償のオープン版は限定的。【未確認】学術利用向けの無償/割引提供枠の有無は未確認(ドコモは学術提供実績があるとされるが本調査では一次ソース未取得)。**メッシュ粒度125m〜500mは、我々の「個人の行動」の粒度より粗い**ため、集計指標での照合(マクロ検証)に留まる。

### 2.6 富士通 Social Digital Twin / 日立 / NEC

**富士通 ソーシャルデジタルツイン™**: 「社会の動きをデジタル空間に再現し、政策を現実に適用する前にシミュレーションする」技術。行動経済学・行動科学と計算機科学を融合し、人間モデルと社会モデルを構築するという建て付け。「デジタルリハーサル™」という概念も掲げる。
- 富士通の解説記事: https://www.fujitsu.com/jp/about/research/article/202407-social-digital-twin.html
- **Fujitsu Research Portal で一般公開されている**(2024年1月〜): https://blog.fltech.dev/entry/2024/01/25/social-digital-twin-publishing
- データ生成ツールも公開(2024年7月): https://blog.fltech.dev/entry/2024/07/31/social-digital-twin-datagen-ja
- CMU との共同研究: https://www.cmu.edu/news/stories/archives/2022/february/cmu-fujitsu-collaborate-to-develop-social-digital-twin-technology-for-smart-cities
- 英ワイト島でのシェアードeスクーター実証: https://pr.fujitsu.com/jp/news/2023/04/19.html

  → **国内で最も我々に思想が近い商用/研究プロダクト**。「社会シミュレーション」を明示的に名乗り、Research Portal で試せる実体がある。ただし人間モデルは**行動経済学ベースであってLLMベースではない**(=我々との差分がここ)。【未確認】Research Portal の利用条件(登録要否・商用可否・APIの粒度)は本調査で未確認。**深掘り候補の筆頭**。

**NEC**: 防犯カメラ映像から数万人規模の混雑度と人流をリアルタイム推定・予測する技術。「群衆モデル」でエージェント個々の追従・衝突回避・すり抜けを表現。
- 2016年のプレスリリース(技術の中身が具体的): https://jpn.nec.com/press/201610/20161024_05.html
- 群衆行動解析の技報: https://jpn.nec.com/techrep/journal/recommend_year/2014/06.html
- NEC Digital Twin 製品ページ: https://jpn.nec.com/iot/digitaltwin/index.html
- 混雑状況可視化サービス: https://jpn.nec.com/cloud/s_iot/congestion/use_flow.html

**日立**: 「人流予測情報提供サービス」。鉄道/バスの発着地別人数+時刻表をAI・シミュレーションで解析し、駅や列車の混雑度を過去再現/将来予測。
- https://dcross.impress.co.jp/docs/news/003116.html

**評価**: NEC/日立はいずれも**物理的な移動と混雑**が対象で、社会関係・意思決定は扱わない。我々の「歩行/移動レイヤ」の外注先候補にはなるが、思想的な重複はない。実体としては商用サービスであり、SDKで組み込める形では公開されていない(本調査の範囲では)。

---

## 3. 群衆・歩行者・交通のシミュレーション製品

| 製品 | 中身 | エージェント連成のAPI | DT文脈での使われ方 |
|---|---|---|---|
| **PTV Vissim / Viswalk** | ミクロ交通シミュレーション。Viswalk アドオンで歩行者。歩行者移動は **Social Force Model (Helbing & Molnár, 1995)** ベース。Wiedemann(車両追従)との選択可 | COM API / 【未確認】詳細は未取得。MATLAB/Simulink 連携あり | 駅・都心・イベント会場の多モーダル群衆評価 |
| **Oasys MassMotion** | 建築/駅の歩行者シミュレーション(Arup系) | **Python 3.7 の SDK が公式提供。エージェントDBを共有し、外部システムへ直接パイプライン可能**。SDKドキュメントはユーザーガイド内 | 建築設計評価が主。クラウド化とIoTデータ取り込みのDT化を研究中と表明 |
| **Bentley Legion** | 歩行者シミュレーション | 【未確認】。検索結果では「Legion for Aimsun」がAimsunのアドオンとして言及されるのみ | 駅・空港・スタジアム |
| **SUMO(我々は導入済み)** | OSSのミクロ交通シミュレーション | **TraCI**(実行中にリルート/流入較正を外部コントローラから制御) | 実データを流し込む「高速道路DT」の学術事例あり |
| **Aimsun Next** | 商用ミクロ/メゾ交通 | **Python API**(シミュレーション時刻と車両状態を制御) | Aimsun Live でリアルタイム予測。Yunex Traffic の交通予測製品に採用 |

出典:
- PTV Vissim 公式: https://www.ptvgroup.com/en/products/ptv-vissim / Viswalk: https://www.ptvgroup.com/en-us/products/pedestrian-simulation-software-ptv-viswalk
- Viswalk の Social Force Model 記述(公式ヘルプ): https://cgi.ptvgroup.com/vision-help/VISSIM_2022_ENG/Content/8_VISWALK/Fugae_SimulationvonFu.htm
- Vissim×群衆ユースケース: https://www.ptvgroup.com/en-us/products/ptv-vissim/use-cases/multimodal-crowd-simulation
- MATLAB連携: https://www.mathworks.com/products/connections/product_detail/ptv-vissim.html
- MassMotion 公式: https://www.oasys-software.com/products/pedestrian-simulation-software/massmotion/
- MassMotion 11 SDK更新(Python 3.7・native API doc): https://www.oasys-software.com/news/massmotion11sdk/
- MassMotion SDK FAQ: https://www.oasys-software.com/?faqs=massmotion-software-development-kit-sdk
- MassMotion のDT/IoT方向の言及(AEC Magazine): https://aecmag.com/simulation/massmotion-pedestrian-simulation-during-covid-19/
- SUMOによる高速道路DT(IEEE): https://ieeexplore.ieee.org/document/9899796/
- Aimsun vs SUMO 比較(学位論文PDF): https://www.diva-portal.org/smash/get/diva2:555913/FULLTEXT01.pdf
- Aimsun ベースの交通予測: https://www.yunextraffic.com/portfolio/urban/mobility-management/traffic-prediction/

**この節の要点(我々向け)**:
1. **この業界の歩行者モデルはほぼ全部 Social Force Model 系(物理ベース)であり、「なぜそこへ行くか」を決めない。** 行き先(OD)は外から与える前提。**つまり我々のLLM社会シムは、これらの製品の「入力側の空白」をちょうど埋める形になる。**
2. **SUMO(TraCI)を既に持っているのは正しい選択。** 商用のAimsun/Vissimに乗り換える動機は薄い(APIの型は同種、費用が跳ねる)。
3. **歩行者を真面目にやるなら MassMotion の Python SDK が唯一「買えば外部から叩ける」実体**。ただし商用ライセンスが必要。【未確認】価格は未取得。

---

## 4. LLMエージェント × 都市/DT の研究動向(2025-2026)

### 4.1 都市規模のLLMエージェント社会(我々の直接の隣人)

| 研究 | 中身 | 我々との差分 |
|---|---|---|
| **AgentSociety**(Tsinghua FIB Lab, 2025) | LLM駆動エージェント+現実的な社会環境+大規模シミュレーションエンジン。**1万体超・500万インタラクション**。分極化・炎上・UBI政策・ハリケーン等の外部ショック・都市持続可能性の5テーマ | 規模が我々より1〜2桁大きい。ただし論文本体は CC BY-NC-ND。**実装(AgentSociety 2)は Apache 2.0 でPyPI配布(`pip install agentsociety2`)**、Ray分散。**ただしV2は汎用研究プラットフォームへ舵を切っており、V1の都市シミュレーション機能とは別物**とREADMEにある |
| **CitySim**(2025) | 再帰的価値駆動のスケジュール生成、信念・長期目標・空間記憶。ミクロ/マクロ両面で先行研究より人間に近いと主張。群密度推定・場所の人気予測・ウェルビーイング評価で検証 | 検証指標の設計が近い。GIS/地図データを使うかは論文アブストからは不明【未確認】 |
| **GATSim**(2025) | 生成エージェントによる都市モビリティ。社会経済プロファイル・生活様式・心理的に妥当な記憶システムと生涯学習 | 交通行動に特化 |
| **Emergent Crowds Dynamics from Language-Driven Multi-Agent Interactions**(2025) | **LLMの生成した会話が、その後の物理的なナビゲーション/ステアリング決定に影響する**パイプライン。対話システム+言語駆動ナビゲーション | **「社会的相互作用→物理的群衆挙動」を明示的につないだ数少ない例**。規模・使用モデル・レンダリング基盤はアブストからは不明【未確認】 |
| **EconSimulacra**(2026) | LLMエージェント駆動の社会経済システムDTプラットフォームを名乗る | 【未確認】詳細未調査 |

出典:
- AgentSociety: https://arxiv.org/abs/2502.08691 / 実装: https://github.com/tsinghua-fib-lab/agentsociety/
- CitySim: https://arxiv.org/abs/2506.21805
- GATSim: https://arxiv.org/abs/2506.23306
- 言語駆動群衆: https://arxiv.org/pdf/2508.15047
- EconSimulacra: https://arxiv.org/pdf/2606.26883
- 生成エージェント都市環境の基盤プラットフォーム論(PLOS Complex Systems): https://journals.plos.org/complexsystems/article?id=10.1371%2Fjournal.pcsy.0000093
- サーベイ「Large Language Model Powered Intelligent Urban Agents」: https://arxiv.org/pdf/2507.00914

### 4.2 DT と LLM の結合を掲げる論文(=「組み合わせ方」の学術側の議論)

- **AUDiTs: Towards Agentic Urban Digital Twins**(Xinyue Ye ほか、*Urban Informatics*、2026年3月)。「既存の都市DTは予測・計画はできるが、**社会的複雑性・倫理・ステークホルダー参加の表現が乏しい**」という問題設定から、LLM/マルチモーダルエージェントをDT環境に埋め込む研究アジェンダを提示。LLM拡張GISとエージェント的オーケストレーションで、都市科学のEDUG(Explaining/Discovering/Understanding/Generalizing)を進めるという建て付け。
  - https://link.springer.com/article/10.1007/s44212-025-00099-3 (Springer側は本文が認証壁の可能性)
  - 著者研究室の告知: https://www.geoearlab.com/post/new-publication-on-agentic-urban-digital-twins-and-human-ai-co-learning
- **Towards fully automated city operations: Integrating agentic AI with urban digital twins**(UCL Discovery に公開PDFあり、2025年10月版)。市場化済みシステム/初期実験/ビジョン駆動 の3層で整理し、スケーラビリティ・リアルタイム処理・相互運用性・倫理ガバナンス・データ標準の欠如を課題として挙げる。
  - PDF(オープンアクセス): https://discovery.ucl.ac.uk/id/eprint/10225208/1/Batty_ssrn-5596992.pdf
  - 出版版: https://www.sciencedirect.com/science/article/abs/pii/S0198971526000517
- **AI Agent-Based Intelligent Urban Digital Twin (I-UDT)**(MDPI Smart Cities, 2025): https://www.mdpi.com/2624-6511/8/1/28
- **Leveraging generative AI for urban digital twins(scoping review)**(Urban Informatics): https://link.springer.com/article/10.1007/s44212-024-00060-w
- **DTのパラメータ設定をLLMマルチエージェントで自動化**(IEEE): https://ieeexplore.ieee.org/document/10710900/ — LLMエージェントがシミュレータと閉ループで動き、データインタフェースからシミュレーション結果を読み、パラメータ調整のAPI/関数呼び出しを出力するという型。

**重要な観察**: 学術側の「DT×LLM」の議論は、**圧倒的に「LLMがDTを操作/解釈する」方向**(オペレーター・アナリスト・パラメータ調整者としてのLLM)。**「LLMエージェント自身が住民として社会を構成し、その帰結をDTで観測する」方向は少数派**。AUDiTs が明示的にその欠落(社会的複雑性の過小表現)を指摘しているのは我々にとって追い風。

### 4.3 NVIDIA / 大手の「AIエージェント × Omniverse」の実体

- **NVIDIA Omniverse Blueprint for Smart City AI**(GTC Paris 2025、2025年6月発表)。Omniverse(都市規模の物理的に正確なDT)+ Cosmos(合成データ生成)+ NeMo(VLM/LLMの学習)+ **Metropolis(ビデオ分析AIエージェント)** の4層構成。
  - NVIDIA公式ブログ: https://blogs.nvidia.com/blog/smart-city-ai-blueprint-europe/
  - 解説: https://www.iotworldtoday.com/smart-cities/nvidia-smart-city-ai-blueprint-showcased-at-nvidia-gtc-paris
  - パートナー: XXII, AVES Reality, Akila, Blyncsy, **Bentley**, **Cesium**, K2K, Linker Vision, Milestone Systems, Nebius, SNCF Gares&Connexions, Trimble, Younite AI
  - **入手可否**: 記事時点で「サインアップして提供時に通知を受ける」段階。GitHub等での直接ダウンロード提供の記載なし。【未確認】2026年7月現在のGA状況は未確認。
  - **決定的な注意点**: ここで言う「AIエージェント」は **カメラ映像を見て要約・警報を出す視覚分析エージェント**であり、**住民として振る舞う社会エージェントではない**。交通インシデント予測(毎秒10万件超の予測生成)など、運用支援が主眼。
- **Mega Omniverse Blueprint**(工場/倉庫内で物理AIロボット群を訓練するDT): https://blogs.nvidia.com/blog/mega-omniverse-blueprint-industrial-digital-twins/
- **Omniverse DSX Blueprint**(AIファクトリDT、GTC 2026でGA): https://nvidianews.nvidia.com/news/nvidia-releases-vera-rubin-dsx-ai-factory-reference-design-and-omniverse-dsx-digital-twin-blueprint-with-broad-industry-support / https://blogs.nvidia.com/blog/omniverse-dsx-blueprint/
  - ここでは Phaidra / Emerald AI の **AIエージェントがDT内で訓練され、電力・冷却・ワークロードを継続最適化**し、DTを「自己学習システム」にする、という形が示されている。**これは「DT内で訓練されたエージェントを実世界の運用に出す」型**であり、我々の「社会の観察」とは目的が違う。

### 4.4 我々の立ち位置(どこが空白か)

**空白は「社会的意思決定の内生性」と「決定論的な観測可能性」の交点にある。**
産業界のDTは幾何・物理・センサ同化に極めて強いが、そこに置かれるエージェントは(a)身体を持つロボット/車両、または(b)映像を解釈する運用支援AIのいずれかで、**「なぜその人がそこへ行き、誰と会い、何を言うのか」を内生的に決めるレイヤは商用DTの外にある**。逆に学術側のLLM都市エージェント研究(AgentSociety・CitySim・GATSim)は社会挙動を内生化しているが、**都市の実ジオメトリ・実物理・実センサとの接続は薄く、再現性の担保も一様ではない**。shibuya-simulation は「決定論・L1イベントログからの事後観測(観測がシムを変えない)・PLATEAU実高さ・SUMO連成・UEエクスポート」を既に持っており、**この2つの陣営を橋渡しする位置に既にいる**。特に「観測がシムを変えない」という設計原則は、DT業界が持っていない資産で、**同じ乱数種で何度でも同じ社会を再生できる**ことを意味する — これは商用DTの「リアルタイム同化」型とは正反対の強みであり、社会科学的な反実仮想実験(CRN・sign-flip permutation 等、既に本プロジェクトが実装している手法)を成立させる前提である。逆に弱点は、産業界が持つ**実センサデータ同化**と**大規模な物理的忠実度**であり、そこは借りるのが合理的。

---

## 5. 「組み合わせ」の類型整理

まず**我々の現状の結合点**を確認しておく(リポジトリ実査、2026-07-30時点):
- `scripts/export_3d.py` — **`l1_events.parquet` を読むだけで sim 本体に非依存**(ファイル冒頭に「sim⇄viz 疎結合」と明記)。出力は `scene.json` / `tracks.json` / `buildings.glb`(glTF 2.0)/ `plateau_web.json` / `terrain_web.json`。
- `scripts/export_ue.py` — 中立シーン → UE座標(cm・左手系)への一方向変換。UE側は「配列を読んで線形補間してISMを更新するだけ」に保つ設計(`viz/unreal/SimReplayActor_DESIGN.md`)。**PLATEAU SDKのインポート時オフセットをEPSG:6677第9系のスクランブル交差点座標に設定すれば原点が一致する**と明記。
- `scripts/plateau_extract.py` / `match_plateau.py` / `build_heights.py` — PLATEAU実形状の抽出と照合。
- `scripts/sumo_pipeline.py` / `sumo_taxi_bridge.py` — SUMO連成。
- `scripts/fetch_odpt.py` / `build_transit_odpt.py` — 公共交通オープンデータ(ODPT)。
- `docs/research/social-force-crowd.md` — Social Force 系の既往調査あり。

つまり **我々は既に類型①と②を実装済み**である。以下、業界事例から抽出した6類型。

### 類型① 可視化/リプレイ層としてのDT
- **代表事例**: UE5 City Sample(Mass AI による大量群衆描画)、PLATEAU SDK for Unity/Unreal、東京都デジタルツイン3Dビューア、CesiumJS。
- **要求される結合インタフェース**: シムから**一方向**の軌跡ストリーム(位置・状態・時刻)。エンジン側は再生器に徹する。
- **我々との整合性**: **完全に整合。これが最も安全な結合。** 既に `export_3d.py` → `export_ue.py` の経路がまさにこれ。「観測がシムを変えない」原則を一切損なわない(そもそもシムは既に終わっている)。
- **成熟度**: 高。無償の実体(UE5 City Sample・PLATEAU SDK・Cesium プラグイン)が揃っている。

### 類型② 幾何/環境データ源としてのDT
- **代表事例**: PLATEAU配信サービス(3D Tiles/MVT/CityGML/terraindb)、東京都の23区点群、OSM。
- **要求される結合インタフェース**: シム初期化時にジオメトリと属性を読み込む一方向のバッチ。CityGML/3D Tiles/GeoJSON のパーサ。
- **我々との整合性**: 完全に整合。**決定論を保つ条件は「データを固定してリポジトリ/キャッシュに固める」こと**。配信APIをラン中に叩くと再現性が壊れるので、必ず事前スナップショット化する(PLATEAU配信サービスが自ら「試験的運用でSLA保証なし」と言っている以上、これは必須)。
- **成熟度**: 高。日本は世界的に見ても恵まれている(PLATEAUの無償オープンデータ)。

### 類型③ 物理エンジンとしてのDT
- **代表事例**: Omniverse(PhysX)、UE(Chaos/Mass AI)、Viswalk/MassMotion の Social Force。
- **要求される結合インタフェース**: **毎ステップの双方向**。シムが「行き先」を出し、物理側が「実際に着いたか/どれだけ混んだか」を返す。
- **我々との整合性**: 一般には**要注意**。物理側が非決定論(浮動小数・スレッド順序・GPU・並列ルーティング)だと我々の決定論が壊れ、ループを閉じると「観測」が「相互作用」に変わる。
  - **ただし本プロジェクトは既にこの問題を解いている。** リポジトリ実査で2つの型が並存しているのを確認した:
    - `scripts/sumo_pipeline.py` = **完全オフライン後段合成**。既存ランのOD行列(`analyze_od.py` の出力)をSUMOの車需要に写し、車両軌跡を合成してビューアの交通データへ変換する。ファイル冒頭に「シミュ本体(src/society)・conf・L1・ゴールデン・既存 tracks.json を**一切触らない**(R1 完全無風)」と明記。→ **原則と完全整合**。
    - `scripts/sumo_taxi_bridge.py` = **ラン中のライブ連成(TraCI)だが、「物理委譲だけを担う(片方向)」**と自ら定義。決定論を「絶対条件」として明文化し、`--seed` 固定・`--random` 禁止・`--threads` 既定1(並列ルーティング禁止)・taxi fleet のソート済みエッジidへの決定論配置・id昇順の空車への逐次 dispatchTaxi(純関数規則)・step境界での照会、という制約を課す。結果として**同seed 2回で (wait_s, ride_s) 列がバイト一致**する(PoC実測: pickup=321s, dropoff=581s 再現)。
  - **ここから引き出せる一般則**: 類型③は「双方向だから危険」なのではなく、**「物理側が非決定論だから危険」**。物理側に決定論制約(seed固定・単スレッド・順序の全順序化)を課せるなら、ラン中連成でも原則は守れる。**この制約を課せるのはOSS(SUMO)だからであり、商用のブラックボックス製品(Vissim/Aimsun/Omniverse)では同じ保証を取りにいけない** — これが類型③で商用を避けるべき本当の理由。
- **成熟度**: 高(製品として)。我々にとっては「OSSで決定論を握れるか」が採否の唯一の基準。

### 類型④ センサー実データ同化
- **代表事例**: NEC の防犯カメラ群衆推定、日立の人流予測、SUMOの高速道路DT(交通カウンタのストリーム同化)、NVIDIA Metropolis、Bentley iTwin の IoT/ドローン取り込み、Azure Digital Twins。
- **要求される結合インタフェース**: 時系列テレメトリの取り込み+状態推定(データ同化)。
- **我々との整合性**: **原則との衝突が最も大きい。** リアルタイム同化は定義上「外部からシムの状態を書き換える」ので、決定論も反実仮想実験も成立しない。
  - **我々にとっての正しい使い方は「同化」ではなく「較正(calibration)と検証(validation)」**。人流データ(モバイル空間統計等)や PLATEAU 属性を、ランの**事前**に較正データとして使い、ランの**事後**に集計指標を突き合わせる。これは既に `scripts/calibrate_report.py` が担っている構造と同じ。
- **成熟度**: 高(産業側)。ただし我々が採るべきは「弱い形」のみ。

### 類型⑤ リアルタイム連成
- **代表事例**: Aimsun Live、Omniverse DSX(Phaidra/Emerald AI のエージェントがDT内で継続最適化)、Siemens Digital Twin Composer。
- **要求される結合インタフェース**: 双方向・低レイテンシ・イベント駆動。
- **我々との整合性**: **非整合。採用しない方がよい。** 我々の価値は「同じ種で同じ社会が再現できる」ことであり、リアルタイム性ではない。デモとしての「ライブ感」が欲しいなら、**決定論的なランを事後に等速再生する**(類型①)で見た目上は同じ効果が得られる。
- **成熟度**: 中〜高(産業側)。我々への適合度は低。

### 類型⑥ 合成データ生成
- **代表事例**: NVIDIA Cosmos(世界基盤モデル・20兆トークン学習)、Omniverse Replicator、SimReady アセット、Physical AI Data Factory Blueprint。
- **要求される結合インタフェース**: シムから大量の(画像・軌跡・イベント)を書き出し、下流のモデル学習に食わせる。
- **我々との整合性**: **完全に整合し、かつ最も過小評価されている接点。** 我々のL1イベントログは「決定論的に再生成できる、人間の社会行動のラベル付きデータ」である。これを類型①の経路で3D化すれば、**「LLM社会シムが生成したODと会話に駆動された、写実的な渋谷の群衆映像」という合成データ**が作れる。産業側がまさに欲しがっているもの(Cosmos/Metropolis の学習素材)であり、かつ**彼らが自前では作れないもの**(彼らのエージェントは行き先を内生的に決めない)。
- **成熟度**: 中(この方向の実例はまだ少ない)。**だからこそ空白**。

### 類型の要約
| 類型 | 方向性 | 決定論を壊すか | 「観測がシムを変えない」原則との整合 |
|---|---|---|---|
| ① 可視化/リプレイ | sim → DT(一方向・事後) | 壊さない | ◎ 完全整合 |
| ② 幾何/環境データ源 | DT → sim(一方向・事前) | 壊さない(要スナップショット固定) | ◎ 完全整合 |
| ③ 物理エンジン | 双方向(毎ステップ) | **壊しうる** | △ 後段オフライン化なら○ |
| ④ センサ実データ同化 | 実世界 → sim(ラン中) | **壊す** | ✕(較正/検証としての弱い形なら○) |
| ⑤ リアルタイム連成 | 双方向・ライブ | **壊す** | ✕ |
| ⑥ 合成データ生成 | sim → 下流モデル(一方向・事後) | 壊さない | ◎ 完全整合 |

**設計上の一般則(この調査の中心的な結論)**: **「一方向・事後」の結合はすべて我々の原則と整合し、「双方向・ラン中」の結合はすべて原則を壊す。** DT業界の花形は後者(リアルタイム同化)だが、**我々が取るべきは前者に限定される**。これは制約ではなく、**むしろ我々の差別化そのもの**である(再現可能な社会実験は、リアルタイム同化型のDTには原理的に作れない)。

---

## 6. 総括表: 類型 × 主要選択肢 × 成熟度 × 我々への適合度

| 類型 | 主要選択肢 | 入手性(実体) | 成熟度 | 適合度 | 理由(1行) |
|---|---|---|---|---|---|
| ① 可視化 | **UE5 + PLATEAU SDK for Unreal**(既採用) | 無償・GitHub/Fab | 高 | **高** | 既に `export_ue.py` があり、City Sample の Mass AI が大量体描画の完成参照実装 |
| ① 可視化 | **CesiumJS / Cesium for Unreal**(Apache 2.0) | 無償・OSS | 高 | **高** | ブラウザで誰でも見られる。エンジン非依存の保険。3D Tiles 出力が前提 |
| ① 可視化 | Unity + PLATEAU SDK for Unity | 無償 | 高 | 中 | UEを既に選んでいるので二重投資。共同研究先がUnityなら価値 |
| ① 可視化 | Omniverse(2026に無償化) | 無償(要RTX GPU) | 高 | 中 | 見た目は最強だがGPU要件と学習コストが重い。USD出力の価値は将来的 |
| ① 可視化 | 東京都デジタルツイン3Dビューア(CSVアップロード) | 無償 | 中 | 中 | 集計結果を公的ビューアに重ねる軽量経路。粒度は粗い |
| ② データ源 | **PLATEAU 配信サービス**(3D Tiles/MVT/CityGML/terrain) | 無償・API公開 | 中(自称「試験的運用」) | **高** | 既採用。SLA保証なしなのでスナップショット固定が必須 |
| ② データ源 | 東京都 23区高精度点群(商用可) | 無償 | 高 | 中〜高 | 見た目の現実感は最高。ナビには使いにくく、メッシュ化の一手間が要る |
| ② データ源 | ODPT 公共交通オープンデータ(既採用) | 無償 | 高 | 高 | 既に `fetch_odpt.py` で活用済み |
| ② データ源 | Bentley iTwin(Community $0 枠あり) | 一部無償 | 高 | 低 | 強みはインフラ資産管理。渋谷の街はPLATEAUで足りる |
| ③ 物理 | **SUMO / TraCI**(既採用) | 無償・OSS | 高 | **高** | 既に導入済み。乗り換え動機なし。後段オフライン運用に徹すれば決定論も守れる |
| ③ 物理 | Oasys MassMotion(Python 3.7 SDK) | 商用(価格未確認) | 高 | 中 | 「買えば外部から叩ける」歩行者シムの唯一の実体。駅構内など高密度局面を精緻化したい時 |
| ③ 物理 | PTV Vissim/Viswalk・Aimsun Next | 商用(高額) | 高 | 低 | SUMOと同型のAPIで費用だけ跳ねる |
| ③ 物理 | UE Mass AI(描画側の群衆) | 無償 | 高 | 中〜高 | 「物理」ではなく「描画のための群衆」。①の一部として使うのが正しい |
| ④ センサ同化 | モバイル空間統計/Agoop/KDDI 人流 | **商用有償**・粒度125〜500m | 高 | 中 | 較正/検証データとしてのみ。ラン中同化はしない。学術枠の有無は未確認 |
| ④ センサ同化 | Azure Digital Twins(DTDL) | 従量課金 | 高 | 低〜中 | 企業DTと会話する共通語彙としての価値。3Dは自前なので必須ではない |
| ④ センサ同化 | NEC 混雑推定 / 日立 人流予測 | 商用サービス | 高 | 低 | SDK提供が確認できず、外部から組み込めない |
| ⑤ リアルタイム | Aimsun Live / Omniverse DSX / Siemens | 商用 | 中〜高 | **低** | 原理的に決定論と反実仮想実験を壊す。採用しない |
| ⑥ 合成データ | **自前の L1→3D 経路 + Cosmos/Metropolis 下流** | 無償(Cosmosはオープンモデル) | 中 | **高(戦略的)** | 我々だけが作れる「内生的なODと会話に駆動された都市群衆データ」。業界の空白 |
| — | 富士通 ソーシャルデジタルツイン(Research Portal 公開) | 一部無償公開 | 中 | **中〜高(要深掘り)** | 国内で唯一「社会シミュレーション」を正面から名乗る実体。人間モデルは行動経済学ベースでLLMではない=補完関係 |
| — | 渋谷の既存DT(デジタルツイン渋谷/バーチャル渋谷) | 公開範囲不明 | 低〜中 | 低(現時点) | 対象が笹幡エリアまたは体験用メタバース。渋谷駅周辺の社会シムは空白のまま |

### 総括の3点

1. **我々の既存構成(PLATEAU + UE + SUMO + L1事後観測)は、業界の類型①②③の主要な正解を既に押さえている。** 大きな乗り換えは不要。追加投資すべきは「幅」ではなく「出口」。
2. **最も効く未実装の接点は「3D Tiles 出力」**。現在の出力は glTF(`buildings.glb`)+ 独自JSON(`scene.json`/`tracks.json`/`plateau_web.json`)。ここに **3D Tiles(OGCコミュニティ標準)** を1本足すと、CesiumJS(ブラウザ)・Cesium for Unreal・Cesium for Omniverse・他都市のDT基盤に**同じ出力で**乗る。Cesium が NVIDIA Smart City AI Blueprint のパートナーに入っていることもあり、業界の共通輸送形式として賭ける価値がある。
3. **最も差別化になるのは類型⑥(合成データ)**。産業DTのエージェントは「行き先を内生的に決めない」。我々のLLM社会シムはそれを決める。**「なぜその人がそこへ行くか」を内生化した都市群衆データは、現時点で我々以外にほぼ誰も生成していない。**

---

## 付録: 本調査で確認できなかった/未確認の事項(正直な限界)

- NVIDIA Omniverse 無償化(2026年5月)の**一次ソース**(NVIDIA公式のライセンス改訂告知)に到達できていない。二次情報3件が一致。採用前に現行 Product Specific Terms の直接確認が必要。
- Unreal Engine の**2026年時点のライセンス条件**(特に非ゲーム/シミュレーション用途のシート課金)は未確認。
- Bentley iTwin Community プランの正確な現行条件は第三者まとめ依拠。
- Azure Digital Twins の具体的単価、および製品の将来ロードマップは未確認。「2026年廃止」情報は**確認できなかった**(=噂の裏取りができなかった、という意味であり、否定でもない)。
- Virtual Singapore の2022年完了後の後継プログラム・現在の公開範囲は不明。
- Re:Earth CMS / Visualizer の一般提供(告知は「2025年半ば頃」)の2026年7月時点の実状況は未確認。
- 渋谷区の PLATEAU データの最新年度版(2024/2025年度)の有無は未確認。
- デジタルツイン渋谷プロジェクト(2021年開始)の**その後の進捗**は公開情報が見つからなかった。バーチャル渋谷の2025-2026年の運営状況も同様。
- モバイル空間統計等の人流データの**学術利用向け無償/割引枠**の有無は未確認(一次ソース未取得)。
- MassMotion / PTV Vissim / Aimsun の**価格**は未取得。
- NVIDIA Omniverse Blueprint for Smart City AI の 2026年7月時点の GA/入手可否は未確認(2025年6月時点では「サインアップして通知を待つ」段階)。
- Siemens Xcelerator の都市スケールで「外部開発者が使えるAPI」の実体は特定できなかった(価格も非公開)。
- 建設系ゼネコンの街区スケールDTで、外部から使える公開資産は見つからなかった。日経記事は有料の可能性あり。
- CitySim / Emergent Crowds Dynamics 論文の詳細(GIS利用の有無・規模・基盤)はアブストラクトのみの確認で、本文未読。
- (解消済み)SUMO連成の型は実査で確認した。`sumo_pipeline.py`=完全オフライン後段、`sumo_taxi_bridge.py`=ラン中TraCIだが片方向の物理委譲+決定論制約付き。両方とも原則と整合している。
- `docs/research/sumo-live-transit.md`・`sumo-integration-research.md`・`social-force-crowd.md` 等、本プロジェクト内に既に詳細な既往調査がある。本レポートは**外部業界の地図**に徹しており、内部ドキュメントとの重複・矛盾の突き合わせは行っていない。

