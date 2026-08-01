# 現実世界からのフィードバックをシミュレーションに反映する動線

作成: 2026-08-02 / 調査: web リサーチ（一次情報URL付き）
前提: 本プロジェクトのDT定義 = **「ある時点の現実スナップショットが舞台。常時同期は不要。同期は初期条件と較正のためだけ」**（memory: dt-snapshot-definition）
関連既存文書: `docs/research/dt-integration-deep.md` §8（P7 人流実データ同化）, `docs/research/odpt-integration.md`, `docs/plans/dt-integration-plan.md`

> 本書は法的分析を含むが、弁護士による法的助言ではない。実運用の最終判断は法務確認を推奨する。
> 数値・条文の一部に **[要一次確認]** マークを付けた箇所がある。論文化時にはそこだけ原典で再確認すること。

---

## ① 結論: ライブカメラ映像からのデータ取得は「やめるべき（自動取得）／条件付き可（目視のみ）」

### 1-0. 三行結論

1. **YouTube 配信（FNN / テレ朝ANN / SHIBUYA SKY 等）からの自動フレーム取得は「やめるべき」。** 著作権法上は30条の4で説明できる余地があるが、**YouTube 利用規約の「自動化された手段によるアクセス禁止」に正面から衝突**し、契約違反リスクを研究成果に持ち込む。
2. **「人間が画面を見て、数値だけをメモする」＝条件付きで可。** 閲覧はサービスの本来利用であり、著作物の複製が発生せず、規約にも触れない。較正アンカーを数点取る用途なら実用十分。
3. **本命は構造化オープンデータ。** 渋谷区ダッシュボード・センター街AIカメラ由来の通行量・国交省人流・ODPT・気象で、較正に必要な情報はほぼ代替できる。映像解析に投じるコスト（許諾交渉＋アノテーション＋ドメイン適応）は本選期間には見合わない。

### 1-1. 実在するソースの列挙

| 配信元 | 内容 | 設置位置 | 備考 |
|---|---|---|---|
| **FNNプライムオンライン（フジテレビ系）** | 渋谷スクランブル交差点 24時間ライブ（YouTube） | 渋谷マークシティ低層部屋上（道玄坂） | 最大12時間の巻き戻し、チャット、音声あり |
| **ANN / テレビ朝日（ANNnewsCH）** | 渋谷スクランブル交差点 24時間ライブ（YouTube） | 宇田川町 | 別アングル。複数の配信URLが並行存在 |
| **渋谷スクランブルスクエア「SKY LIVE CAMERA」** | 地上約230mのSHIBUYA SKYからの俯瞰ライブ（YouTube、2021-09-13開始） | 渋谷スクランブルスクエア屋上 | 俯瞰角が最も群衆カウント向き |
| **渋谷センター商店街振興組合 / Intelligence Design（IDEA）** | センター街 3地点のAIカメラ・ライブ配信＋**通行量カウント数値を画面表示** | センター街入口ほか | https://center-gai.jp/live-camera/ 。サイト利用規約で複製・再利用は事前承諾制 |
| まとめサイト（カメ探、livecam.asia、LiveAtlas 等） | 上記の埋め込み一覧 | — | 一次ソースではない。規約は各配信元に従う |

出典:
- 渋谷スクランブルスクエア SKY LIVE CAMERA プレスリリース https://prtimes.jp/main/html/rd/p/000000047.000046405.html
- ANN 渋谷スクランブル交差点ライブ https://www.youtube.com/watch?v=8H3nRCFVR6Y
- FNN系 渋谷スクランブル交差点ライブ（設置位置の記載あり） https://livecam.asia/tokyo/shibuya/fnn-shibuya.html
- センター街ライブカメラ https://center-gai.jp/live-camera/ / 事例記事 https://idea.i-d.ai/case-study/municipality/shibuya-center-gai-live-camera/

### 1-2. 法的分析（日本法）

#### (a) 著作権法30条の4 — 情報解析のためのTDM例外

条文（2018年 平成30年法律第30号で新設）:

> 第三十条の四　著作物は、次に掲げる場合その他の当該著作物に表現された思想又は感情を自ら享受し又は他人に享受させることを目的としない場合には、その必要と認められる限度において、いずれの方法によるかを問わず、利用することができる。**ただし、当該著作物の種類及び用途並びに当該利用の態様に照らし著作権者の利益を不当に害することとなる場合は、この限りでない。**
> 　一　著作物の録音、録画その他の利用に係る技術の開発又は実用化のための試験の用に供する場合
> 　二　**情報解析**（多数の著作物その他の大量の情報から、当該情報を構成する言語、音、影像その他の要素に係る情報を抽出し、比較、分類その他の解析を行うことをいう。）**の用に供する場合**
> 　三　前二号に掲げる場合のほか、著作物の表現についての人の知覚による認識を伴うことなく当該著作物を電子計算機による情報処理の過程における利用……に供する場合

（条文 https://ja.wikibooks.org/wiki/著作権法第30条の4 、立法趣旨 文化庁 https://www.bunka.go.jp/seisaku/chosakuken/hokaisei/h30_hokaisei/pdf/r1406693_17.pdf ）

**当てはめ:**
- 群衆カウントは映像の表現を「享受」する目的ではなく、影像から人数という要素を抽出・集計する行為 → **2号の情報解析に該当し、柱書の適用可能性は高い**。目的が営利か研究かは問わない（30条の4は目的を限定していない）。
- 映像そのものを Web に再掲載する行為は「享受」目的なので **30条の4の射程外**。出力は集計値・グラフに限る必要がある。
- **ただし書のリスク**: 文化庁「AIと著作権に関する考え方について」（2024-03-15）は、**著作物の利用市場と衝突する場合／権利者の潜在的販路を実質的に阻害する場合**を但し書き該当と整理し、とくに**データベース著作物の複製**を典型例に挙げる。放送局が映像解析用ライセンス市場を持つ場合は該当し得るが、単一地点の人数時系列を短期取得する程度では通常は該当しにくい。
  - 文化庁 AIと著作権 https://www.bunka.go.jp/seisaku/chosakuken/aiandcopyright.html
  - チェックリスト＆ガイダンス（2024-07-31） https://www.bunka.go.jp/seisaku/bunkashingikai/chosakuken/seisaku/r06_02/pdf/94089701_05.pdf
- **著作隣接権への準用**: 放送局の映像には著作隣接権も絡む。ただしYouTube配信は「放送」ではなく「自動公衆送信」なので放送事業者の権利（98条以下）の射程は限定的。現行102条1項は「第30条の2から第32条まで」を準用列挙しており30条の4を含むと解される **[要一次確認: e-Gov原文]**（検索でヒットする条文テキストの多くが2018年改正前のもので、30条の4が列挙に現れない）。

#### (b) YouTube 利用規約 — ここが決定的な障害

日本語版 https://www.youtube.com/t/terms （発効日 2023-06-01、準拠法カリフォルニア州法、専属管轄サンタクララ郡）「許可および制限」より:

> 自動化された手段（ロボット、ボットネット、スクレーパなど）を使用して本サービスにアクセスすること。ただし、（a）公開されている検索エンジンを YouTube の robots.txt ファイルに従って使用する場合、または（b）**YouTube が事前に書面で許可している場合**を除きます。

> 本サービスまたはコンテンツのいずれかの部分に対しても、アクセス、複製、ダウンロード、配信、送信……を行うこと。ただし、（a）本サービスによって明示的に承認されている場合……を除きます。

また API 経由でも、YouTube API Services Developer Policies が **「YouTube アプリケーションをスクレイピングしてはならない／スクレイピングされたデータを取得してはならない」** と明記している（https://developers.google.com/youtube/terms/developer-policies ）。そもそも Data API は**メタデータのみで映像フレームは取得できない**。

**帰結（重要）:**
- `yt-dlp` / `streamlink` / HLS(m3u8)直叩き / ヘッドレスブラウザの定期スクリーンショット — **すべて「自動化された手段によるアクセス」に該当**する。
- **配信者（FNN・テレ朝）から許諾を得ても、YouTube との契約違反は解消しない。** 例外は「YouTube が事前に書面で許可した場合」であり、許諾主体は YouTube である。放送局からの許諾で合法化したいなら、**YouTube を経由せず直接映像提供を受ける**しかない。

#### (c) 30条の4 と利用規約の関係（オーバーライド問題）

- 30条の4 を**強行規定でない（任意規定）とする見解が有力**であり、規約による制限は契約として有効に働き得る。文化審議会も「権利制限規定の趣旨、事業上の合理性、利用者の不利益、公正競争を総合考慮」とし、一律の結論を示していない。
- 実務上の要点: **規約違反は著作権侵害ではなく債務不履行（契約違反）**。損害賠償・差止のほか、現実的には**アカウント停止・IPブロック**という執行が先に来る。
- 参考: STORIA法律事務所「著作権法の柔軟な権利制限規定とオーバーライド問題」 https://storialaw.jp/blog/7658 、YS法律事務所「スクレイピングはどこまで許されるのか」 https://www.ys-law.jp/IT/column/column-11384/

→ **「著作権法的にはセーフでも、契約的にはアウト」という二層構造**。研究成果として論文・ハッカソン発表に載せる以上、後者を抱えたままにするのは不適切。

#### (d) 肖像権

- 最判 平成17年11月10日: 人は「みだりに自己の容ぼう等を撮影されない」人格的利益を有し、違法性は**被撮影者の社会的地位・活動内容・撮影の場所・目的・態様・必要性等を総合考慮**して判断される。判断基準は「社会生活上の受忍限度」。
- 公道の群衆・遠景・特定個人が識別できない映像で、出力が**人数という集計値のみ**であれば侵害の成立は考えにくい。
- 逆にリスクが上がるのは、**高解像度フレームを長期保存する**、**個人追跡（re-identification）を行う**、**特定人物の映り込みを公開資料に載せる**の3点。
- 参考: 個人情報保護委員会 資料3「肖像権・プライバシーに関する裁判例」（弁護士 森亮二） https://www.ppc.go.jp/files/pdf/20220309_shiryou-3.pdf 、東京都都市整備局 資料5「市街撮影行為の適法性」 https://www.toshiseibi.metro.tokyo.lg.jp/documents/d/toshiseibi/pdf_bunyabetsu_machizukuri_pdf_digital03_5

#### (e) 個人情報保護法

- 顔が識別できる映像は**個人情報**に当たり得る。特徴量データは個人識別符号となり得る。
- 「カメラ画像利活用ガイドブック ver3.0」（2022-03、IoT推進コンソーシアム／総務省／経産省）は、ユースケースの一つとして **「人物・車両等の計数：公共空間に向けたカメラで通行人数を計測し、撮影画像は速やかに破棄する」** を掲げ、この形態を適切な運用例として整理している。
  - ver3.0 https://www.meti.go.jp/policy/it_policy/privacy/01_CameraGuideBook_ver3.0.pdf / ver2.0 https://www.soumu.go.jp/main_content/000542668.pdf
- 実際、渋谷区のエッジAIカメラ人流計測（渋谷100台プロジェクト）も **「映像から抽出される人数・属性・滞留情報に個人を特定できる情報を含まず、映像は解析後に即時破棄・保存しない」** という設計で運用されている。 https://prtimes.jp/main/html/rd/p/000000056.000048250.html
- **学術研究例外は当てにできない。** 令和3年改正で「学術研究機関等」の一律適用除外は廃され、義務ごとの例外に精緻化された。かつ主体は大学・学会・国立研究開発法人等に限られる。ハッカソンチーム単体は通常該当しない。
  - ニッセイ基礎研究所 解説 https://www.nli-research.co.jp/report/detail/id=70142?site=nli
- → **例外規定に頼らない設計**（フレーム非保存・集計値のみ保存・属性推定なし・追跡なし）が唯一の安全策。

### 1-3. 技術パイプライン（参考: 仮に許諾が取れた場合の実装像）

```
HLS/RTMP or 提供元からの直接フィード
  → ffmpeg で N 秒に1フレーム抽出（1080p 相当）
  → 透視補正（交差点平面へのホモグラフィ）＋ ROI マスク（横断歩道4本＋待機島）
  → 群衆カウントモデル
       CSRNet   : VGG16 + dilated conv バックエンド。密度マップ回帰。軽量・実装豊富
       P2PNet   : ICCV2021 Oral（Tencent Youtu）。点ベース。位置も出るので「横断歩道別」に集計しやすい
       P2PNeXt  : ConvNeXt バックボーンに置換した後継（Fraunhofer）
  → フレームは即時破棄、per-ROI 人数と時刻のみ parquet に追記
  → 信号周期（約2分）で位相同期し「1サイクルあたり横断人数」に整形
```

- 実装: P2PNet 公式 https://github.com/TencentYoutuResearch/CrowdCounting-P2PNet 、P2PNeXt https://publica.fraunhofer.de/bitstreams/b83c96ce-87a7-48ae-9c0b-053dfe3481bc/download
- サーベイ: Wang et al. 2025, IET Image Processing https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/ipr2.13328 / Deng et al. 2024, CAAI Trans. https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/cit2.12241
- **精度の現実**: ShanghaiTech A/B や WorldExpo'10 で学習したモデルを渋谷の斜俯瞰・夜間ネオン・雨天にゼロショット適用すると誤差が大きい。実用化には数百枚規模の現地アノテーションとドメイン適応が必要 → 本選までの工数として非現実的。**これは「やらない」判断のもう一つの理由。**

### 1-4. 先行研究の有無

- **渋谷スクランブル交差点を対象にした研究は存在する**が、確認できたのは信号制御の深層強化学習（"Deep Reinforcement Learning at Scramble Intersections for Traffic Signal Control: An Example of Shibuya Crossing", 2023 https://www.researchgate.net/publication/373267738 ）であり、**公開ライブ配信映像を解析データ源とした査読論文は今回の検索では確認できなかった。**
- 一般に、公開動画由来のデータセットは**映像本体を再配布せず、動画ID・タイムスタンプ・アノテーションのみを配布する**慣行が定着している。公共空間カメラを研究に使う際の倫理・情報ガバナンスは独立した論点として扱われている（"Using Video Cameras as a Research Tool in Public Spaces: Addressing Ethical and Information Governance Challenges Under Data Protection Legislation" https://www.researchgate.net/publication/369905948 ）。
- 参考: Windy Webcams API のような**ライセンス済みウェブカメラAPI**は存在するが、画像URLトークンが10分（無料）／24時間（Pro）で失効し、表示にクレジット・元ページへのリンクが必須。渋谷交差点の該当カメラがカタログにあるかは未確認 **[要一次確認]**。 https://api.windy.com/webcams/docs / 規約 https://api.windy.com/webcams/terms

### 1-5. 推奨条件（もしどうしても映像を使うなら）

| # | 条件 | 理由 |
|---|---|---|
| 1 | YouTube を経由せず、**放送局・施設運営者から直接**フィード提供を受ける書面許諾 | YouTube ToS の自動アクセス禁止を回避できる唯一の道 |
| 2 | フレームは**メモリ上のみ・即時破棄**。ディスクに書くのは per-ROI 人数と時刻だけ | カメラ画像利活用ガイドブックの「計数」ユースケースに準拠 |
| 3 | **属性推定・追跡・再識別を行わない** | 個人情報／肖像権リスクの本体を切る |
| 4 | 出力は**集計値・グラフのみ**公開。映像・フレームは一切公開しない | 30条の4は「享受目的」を許さない |
| 5 | 取得期間・地点を**必要最小限**に限定（例: 較正用に3日×3時間帯） | 30条の4ただし書き（市場との衝突）リスクの低減 |
| 6 | 撮影範囲・目的・破棄方針を明記した**運用記録**を残す | 論文の倫理記述および事後説明に必要 |

**上記1が満たせないなら、自動取得は行わない。** 代替として「人間が配信画面を見て、青信号1サイクルあたりの横断人数を目視カウントし、数値だけを記録する」は、複製が発生せず規約にも触れないため**実施可**。較正には十分な粒度（例: 平日/休日 × 朝/昼/夕/夜 の8条件 × 5サイクル = 40サンプル）が数時間の人手で得られる。

---

## ② データソース比較表（較正用・合法かつ構造化）

凡例: 入手性 ◎=即日API / ○=登録要 / △=閲覧のみ（人手転記）/ ▲=商用契約要

| # | ソース | 内容 | 空間粒度 | 時間粒度 | 費用 | 入手性 | ライセンス | URL |
|---|---|---|---|---|---|---|---|---|
| 1 | **ODPT 公共交通オープンデータ**（利用中） | 列車走行位置・時刻表・駅情報・バス位置。GTFS/GTFS-RT/JSON。352データセット | 駅・便単位 | RT〜静的 | 無料 | ○（アカウント＋トークン） | 公共交通OD基本ライセンス／CC BY 4.0／チャレンジ限定 | https://ckan.odpt.org/dataset |
| 2 | **公共交通ODチャレンジ2026** | 上記＋JR東日本 関東エリア一部路線のGTFS-RT（列車走行位置）等、チャレンジ限定 | 路線・列車 | RT | 無料 | ○（応募登録） | チャレンジ限定ライセンス | https://challenge2026.odpt.org/ |
| 3 | **国交省 全国の人流オープンデータ**（P7で採用済） | 滞在人口（Agoop GPS由来換算）2019–2021 | 1kmメッシュ／市区町村発地別 | 日次・時間帯別 | 無料 | ◎（G空間情報センター、要ユーザ登録） | 政府標準利用規約2.0（CC BY 4.0互換） | https://www.mlit.go.jp/tochi_fudousan_kensetsugyo/tochi_fudousan_kensetsugyo_fr17_000001_00006.html |
| 4 | **渋谷区 SHIBUYA CITY DASHBOARD／渋谷駅周辺の滞在・通行人流** | KDDI Location Analyzer 由来の滞在人口・通行量 | 駅周辺5ゾーン＋3街路（宮益坂・道玄坂・表参道） | 未記載（更新日2026-07-22） | 無料 | **△**（Power BI 埋め込み、CSV/API なし） | 未明示（要問合せ） | https://www.city.shibuya.tokyo.jp/kusei/tokei_shibuya/shibuya-data/shibuya_city_dashboard_peopleflow_KDDI.html |
| 5 | **渋谷センター街 AIカメラ通行量（IDEA counter）** | ライブ映像＋**当日累計通行量・現在人数**の実数表示 | 3地点（センター街入口ほか） | リアルタイム | 無料 | **△**（サイト規約で複製・再利用は事前承諾制） | 組合／提供元帰属 | https://center-gai.jp/live-camera/ |
| 6 | **渋谷区オープンデータ（SHIBUYA OPEN DATA / ArcGIS Hub）** | 区政統計・施設・地理データ | 区・町丁目 | 年次中心 | 無料 | ◎ | 各データセット記載 | https://city-shibuya-data.opendata.arcgis.com/ |
| 7 | **東京都オープンデータカタログ** | 約5.4万データセット、うち約3.5万CSVがAPI提供 | 都・区市町村 | 主に年次 | 無料 | ◎ | CC BY 4.0 相当 | https://catalog.data.metro.tokyo.lg.jp/ ／API解説 https://portal.data.metro.tokyo.lg.jp/opendata-api/ |
| 8 | **東京都デジタルツイン 3Dビューア** | 区部3次元点群、3D都市モデル、都バス等リアルタイム重畳 | 建物単位 | 静的＋一部RT | 無料 | ◎ | オープンデータ（G空間情報センター併載） | https://info.tokyo-digitaltwin.metro.tokyo.lg.jp/3dmodel/ |
| 9 | **気象庁 アメダス（bosai JSON）** | 気温・降水・風速・湿度 | 観測地点（東京地点あり） | **10分** | 無料 | ◎（非公式JSON、過去10日保持） | 気象庁HP利用規約＝公共データ利用規約1.0、出典明記で自由利用 | 最新時刻 https://www.jma.go.jp/bosai/amedas/data/latest_time.txt ／全国 https://www.jma.go.jp/bosai/amedas/data/map/{ymdhns}.json ／規約 https://www.jma.go.jp/jma/kishou/info/coment.html |
| 10 | **環境省 WBGT 暑さ指数（電子情報提供サービス）** | 実況値・予測値（当日＋2日、3時間毎）、841地点＋47都道府県 | 地点 | 1時間（実況）／3時間（予測） | 無料 | ○（バイザー(株)経由で規約同意・申込） | 出典明記要。提供期間 4月第4水〜10/21 → **8月は期間内** | https://www.wbgt.env.go.jp/data_service.php ／CSV形式 https://www.wbgt.env.go.jp/wbgt_data_download_csv_format.php |
| 11 | **JARTIC / xROAD 交通量API** | 全国直轄国道 約2,600地点の断面交通量（方向別） | 観測断面 | **5分／1時間**（観測から約20分遅れ） | 無料 | ○（利用登録・規約同意） | 規約準拠 | https://www.jartic-open-traffic.org/ ／ https://www.xroad.mlit.go.jp/ ／報道発表 https://www.mlit.go.jp/report/press/road01_hh_001930.html |
| 12 | **東京メトロ Metro CrowdNavi** | 駅別・列車別 混雑度（直近5日平均＋リアルタイム重畳）、全9路線（2026-06-16 本格提供） | 駅・列車 | 10分／30分 | 無料 | **△**（Web閲覧のみ、API・オープンデータの提供は発表になし） | 未明示 | https://prtimes.jp/main/html/rd/p/000001478.000020053.html |
| 13 | **全国道路・街路交通情勢調査（道路交通センサス）** | 断面交通量・旅行速度 | 道路区間 | 年次（数年おき） | 無料 | ◎ | 政府標準利用規約 | https://www.kensetsu.metro.tokyo.lg.jp/road/information/3sensasu |
| 14 | **警視庁 主要交差点交通量集計表** | 主要交差点の交通量 | 交差点 | 年次 | 無料 | ◎（PDF） | 出典明記 | https://www.keishicho.metro.tokyo.lg.jp/about_mpd/jokyo_tokei/tokei_jokyo/ryo.files/01_kousatenkubu.pdf |
| 15 | **モバイル空間統計（ドコモ・インサイトマーケティング）** | 携帯NW由来の人口分布（国内居住者・訪日）。1時間ごと・24時間365日 | メッシュ（標準版）／カスタム | 1時間 | **有償（価格非公開、エリア数×期間×時間帯で変動）** | **▲**（学術研究機関＝学校法人は**アカデミック価格**、研究成果フィードバックが条件） | 個別契約 | https://mobaku.jp/ ／価格 https://mobaku.jp/price/ ／学術 https://mobaku.jp/academic/ |
| 16 | **Agoop 流動人口データ** | アプリGPS由来の流動人口（総務省検証では500mメッシュ・国勢調査ベンチマーク） | 250m〜500mメッシュ | 1時間 | **有償** | **▲**（学術・研究開発の活用実績あり） | 個別契約 | https://agoop.co.jp/mail_movie_academic/ ／総務省検証資料 https://www.soumu.go.jp/main_content/000577343.pdf |
| 17 | **LocationMind xPop** | 東大 柴崎研系譜の人流解析データ・SaaS | メッシュ／エリア | 1時間 | **有償** | **▲** | 個別契約 | https://locationmind.com/products/xpop-e/ |
| 18 | 歩行者通行量調査（自治体・商店街） | 12時間通行量。センター街入口は調査地点中最多クラス（平日 約11.4万人／休日 約11.2万人 **[要一次確認: 調査年・実施主体]**） | 調査地点 | 年1〜2回 | 無料 | ○（PDF中心） | — | 国交省「まちの活性化を測る歩行者量調査のガイドライン」 https://www.mlit.go.jp/common/001239908.pdf |

### 押さえるべき運用上の注意

- **#4 #5 #12 は「閲覧のみ」**。自動スクレイピングは #5 のサイト規約（複製・公開・再利用に事前承諾要）に抵触する。**人手で数値を転記して `docs/` 配下に較正表として持つ**のが正しい使い方。ハッカソン程度の較正点数なら十分機能する。
- **#5 は問い合わせ価値が高い**。渋谷区・渋谷未来デザイン・Intelligence Design による渋谷100台プロジェクトは「ビッグデータを一部オープンデータ化し、協賛事業者が利用できる形で公開する」と明言している。研究利用の照会は正攻法のルート。 https://idea.i-d.ai/shibuya-project/
- **#15〜17 は大学所属が前提**。学術研究機関（学校法人）でないとアカデミック価格に乗れない。共同研究者に大学所属者がいるかで可否が決まる。
- APIキー・トークンは `.env` に置き、`.gitignore` 対象とすること（既存の掟）。

---

## ③ データ同化の設計パターン — 本プロジェクトへの推奨

### 3-1. 用語の整理（ここを混ぜると設計が崩れる）

| 種別 | 何を動かすか | 頻度 | 決定論・再現性への影響 |
|---|---|---|---|
| **パラメータ較正 (offline calibration)** | モデルの定数（移動速度分布、POI選好、出勤率…） | ラン前に一度 | **なし**（seed 固定なら同一結果） |
| **状態同化 (online data assimilation)** | ラン中のエージェント状態（位置・保有量…） | ステップ毎／窓毎 | **破壊的**（観測が乱数と等価に効き、再現性が観測系列に依存） |
| **ナッジング (nudging)** | 状態に弱い引き戻し項を加える | 連続 | 破壊的（弱いだけ） |
| **事後検証 (posterior validation)** | 何も動かさない。走らせた結果を実データと突き合わせるだけ | ラン後 | **なし** |

**本プロジェクトのDT定義（スナップショット型・常時同期不要）と最も整合するのは「パラメータ較正」＋「事後検証」であり、状態同化ではない。** これは `dt-integration-deep.md` §8 の「やってはいけないこと: ラン中に人流データでエージェント位置を補正する」と完全に一致する。

### 3-2. 先行研究（歩行者ABMへのデータ同化）

Leeds大 Urban Analytics（DUST プロジェクト）が事実上の中心。 https://urban-analytics.github.io/dust/

| 文献 | 手法 | 規模 | 要点 |
|---|---|---|---|
| Wang & Hu 2015 | 粒子フィルタ | 粒子 800–2,000 / エージェント 2–6 | 初期の適用例 |
| **Malleson et al. 2020**（JASSS）"Simulating Crowds in Real Time with Agent-Based Modelling and a Particle Filter" | 粒子フィルタ | 粒子 1–10,000 / エージェント 2–40 | **エージェント数の増加に対し必要粒子数が急増**（次元の呪い）。実時間性の限界を明示 https://www.semanticscholar.org/paper/1ff393c97e3a32e967d7e26784cd22662108014c |
| Ternes et al. 2021/2022 | カテゴリカル・ノイズ付き粒子フィルタ | 粒子 5,000 / エージェント 274 | **カテゴリ型のエージェント属性**（離散状態）の同化に踏み込んだ https://pmc.ncbi.nlm.nih.gov/articles/PMC10445938/ |
| **Suchak, Kieu, Oswald, Ward, Malleson 2024**（Royal Society Open Science 11(4)）"Coupling an agent-based model and an ensemble Kalman filter for real-time crowd modelling" | EnKF | アンサンブル 20–100 | StationSim GCS（NYグランドセントラル駅、11ゲート）。**20ステップごとに同化**、観測ノイズ σ=1.0 px、更新する状態は**エージェントの x-y 位置のみ**。誤差は大幅低減するが、**合成データ（identical twin）での検証にとどまり実データ未適用**、モデル誤差なし・ゲート既知を仮定 https://pmc.ncbi.nlm.nih.gov/articles/PMC11017988/ |
| Clay ほか（博士論文） | EnKF の実時間歩行者ABM適用 | — | https://etheses.whiterose.ac.uk/32039 |

**この文献群から本プロジェクトが引き出すべき結論:**
1. **粒子フィルタは1万体規模に効かない。** 数十エージェントで粒子1万本の世界であり、スケールしない。
2. **EnKF も状態が連続実数ベクトル（位置）であることを前提**にしている。LLMエージェントの意思決定は離散・記号的で、ガウス更新の対象にならない。位置だけ補正しても内部状態（記憶・関係・意図）と矛盾する。
3. **最新のSOTAですら実データ未検証**。ここに独自実装で挑むのは、ハッカソン本選のスコープを大きく超える。

### 3-3. 較正手法（こちらが本命）

- **History Matching + ABC（近似ベイズ計算）** の二段構え。尤度関数が書けないABMで標準的な枠組み。
  - Calibrating Agent-Based Models Using Uncertainty Quantification Methods, JASSS 25(2)1, 2022 https://www.jasss.org/25/2/1.html （PDF https://eprints.whiterose.ac.uk/id/eprint/185400/6/1.pdf ）
  - Improving policy-oriented agent-based modeling with history matching: A case study, 2025 https://www.sciencedirect.com/science/article/pii/S1755436525000337
  - Uncertainty Quantification for Agent Based Models: A Tutorial, arXiv 2024 https://arxiv.org/pdf/2409.16776
- 手順: ①要約統計量を決める → ②パラメータ空間を粗くサンプリング → ③History Matching で implausible 領域を刈る（GPエミュレータで高速化）→ ④残った領域で ABC により事後分布を得る → ⑤代表点を本ランのパラメータに採用。
- **要約統計量の候補**（すべて上表の合法データで作れる）:
  - 時間帯別の渋谷駅周辺滞在人口プロファイル（#3 #4）
  - 列車到着本数から導かれる流入パルス（#1 #2）
  - 主要街路の通行量比（宮益坂 : 道玄坂 : 表参道）（#4）
  - 平日／休日のコントラスト（#3 #4 #18）
  - 気温・WBGT と屋外滞在割合の相関（#9 #10）

### 3-4. 推奨アーキテクチャ（3層・既存設計と非破壊で接続）

```
L0  初期条件同化（ラン開始 t0 のみ）
      実データ由来の在圏人数プロファイルに合わせてペルソナ初期配置を生成
      → 既存 P7 の延長。決定論は seed で保持される

L1  パラメータ較正（オフライン・ラン前）
      History Matching → ABC で移動/滞在/選好パラメータを絞る
      成果物: calib/params_posterior.json（値はコミット、手続きはスクリプト化）

L2  事後検証（ラン後・何も補正しない）
      走らせた結果 vs 実データの誤差を報告するだけ
      → 論文で最も安全に主張できる層。「同化していない」ことが主張の強さになる

× アンチパターン: ラン中の位置補正 / ナッジング
      再現性・決定論（golden テスト、状態ハッシュチェーン）を壊す
```

**論文上の言い方**: 「本モデルは観測データを状態同化していない。実データはパラメータ較正と事後検証にのみ用いた」。これは弱い主張ではなく、**創発を主張する研究では強い主張**である（同化していれば「現実に似ているのは同化のおかげ」という交絡が消せない）。

---

## ④ ハッカソン本選期間（2026-08-15〜30）の取得計画案

### 4-1. 事前準備（〜2026-08-14）

| 期限 | 作業 | 所要 |
|---|---|---|
| 8/05 | ODPT アカウント／アクセストークンの有効性確認、チャレンジ2026 の応募登録（募集 2026-10-01〜2027-01-11、コンテスト期間 2026-07-01〜2027-03-12 → **本選期間中はデータ利用可**） | 0.5日 |
| 8/05 | JARTIC / xROAD 交通量API 利用登録・規約同意 | 0.5日 |
| 8/07 | 環境省 WBGT 電子情報提供サービス 申込（バイザー(株)経由、規約同意） | 1日（承認待ち含む） |
| 8/08 | 気象庁 bosai JSON の取得スクリプト（登録不要。ポーリング間隔は10分・過度な連打をしない） | 0.5日 |
| 8/10 | 国交省 全国人流オープンデータ（既取得分）の再確認 | — |
| 8/12 | 目視較正シートの用意（渋谷区ダッシュボード／センター街カウンタ／YouTube目視の記録様式） | 0.5日 |

### 4-2. 期間中の取得スケジュール

| データ | 取得方法 | 頻度 | 保存先（案） | 備考 |
|---|---|---|---|---|
| 気象庁アメダス（東京） | HTTP GET（latest_time.txt → map/{ymdhns}.json） | 10分 | `data/realworld/amedas/YYYYMMDD.parquet` | 出典表記「気象庁ホームページ」を成果物に明記 |
| 環境省 WBGT（東京地点） | CSV 定期取得 | 1時間 | `data/realworld/wbgt/` | 提供期間内（〜10/21） |
| JARTIC/xROAD 交通量（国道246号ほか渋谷近傍断面） | API | 5分（実データは約20分遅れ） | `data/realworld/traffic/` | 断面IDを事前に特定しておく |
| ODPT 鉄道リアルタイム（JR東・東急・東京メトロ 渋谷駅関連） | API / GTFS-RT ポーリング | 30秒〜1分 | `data/realworld/odpt/` | 既存 `odpt-integration.md` の実装を再利用 |
| 渋谷区 人流ダッシュボード | **人手で目視転記** | 1日1回（朝） | `docs/calibration/shibuya_dashboard_YYYYMM.md` | Power BI 埋め込み。自動取得しない |
| センター街 通行量カウンタ | **人手で目視転記** | 1日2回（12時／20時） | 同上 | サイト規約により自動取得不可 |
| 交差点横断人数 | **人手で目視カウント**（配信画面を見る） | 平日/休日 × 4時間帯 × 5サイクル | 同上 | フレーム保存なし・数値のみ |

### 4-3. 期間の性質を活かす

- 8/15〜30 は **お盆明け・週末3回（8/15-16, 22-23, 29-30）・平日10日**を含む。**平日／休日／お盆残りのコントラスト**が自然に取れる。
- 8月は WBGT 提供期間内かつ猛暑期 → **気温と屋外滞在の関係**を較正に載せる好機（既存 `weather-generator-design.md` と接続）。
- 大規模イベントが重なる場合は「外れ値日」としてラベルし、較正データから除外するか別コホートにする。

### 4-4. 成果物への反映

1. `docs/calibration/` に実測サマリを置く（現況の `docs/calibration` を拡張）。
2. 較正スクリプトは既存の `calibrate_report.py` 系（memory: calibration-toolkit）に `--realworld` 系の入力を足す形が最小改変。
3. 論文・発表資料には **「状態同化はしていない。実データはパラメータ較正と事後検証のみに使用」** を明記。
4. 出典表記義務: 気象庁（公共データ利用規約1.0）、環境省（出典明記）、国交省人流（政府標準利用規約2.0）、ODPT（公共交通オープンデータ基本ライセンス／チャレンジ限定ライセンス）。

---

## 参考: 主要出典URL一覧

**法令・ガイドライン**
- 著作権法30条の4 条文 https://ja.wikibooks.org/wiki/著作権法第30条の4
- 文化庁「AIと著作権について」 https://www.bunka.go.jp/seisaku/chosakuken/aiandcopyright.html
- 文化庁「AIと著作権に関するチェックリスト＆ガイダンス」（2024-07-31） https://www.bunka.go.jp/seisaku/bunkashingikai/chosakuken/seisaku/r06_02/pdf/94089701_05.pdf
- 文化庁「柔軟な権利制限規定に関する基本的な考え方」 https://www.bunka.go.jp/seisaku/chosakuken/hokaisei/h30_hokaisei/pdf/r1406693_17.pdf
- カメラ画像利活用ガイドブック ver3.0 https://www.meti.go.jp/policy/it_policy/privacy/01_CameraGuideBook_ver3.0.pdf
- 個人情報保護委員会 資料3「肖像権・プライバシーに関する裁判例」 https://www.ppc.go.jp/files/pdf/20220309_shiryou-3.pdf
- YouTube 利用規約 https://www.youtube.com/t/terms
- YouTube API Services Developer Policies https://developers.google.com/youtube/terms/developer-policies
- STORIA法律事務所「柔軟な権利制限規定とオーバーライド問題」 https://storialaw.jp/blog/7658

**データ**
- 公共交通オープンデータセンター https://ckan.odpt.org/dataset ／チャレンジ2026 https://challenge2026.odpt.org/
- 国交省 全国の人流オープンデータ https://www.mlit.go.jp/tochi_fudousan_kensetsugyo/tochi_fudousan_kensetsugyo_fr17_000001_00006.html
- 渋谷区 SHIBUYA CITY DASHBOARD https://www.city.shibuya.tokyo.jp/contents/kusei/shibuya-data/
- 渋谷駅周辺の滞在・通行人流ダッシュボード https://www.city.shibuya.tokyo.jp/kusei/tokei_shibuya/shibuya-data/shibuya_city_dashboard_peopleflow_KDDI.html
- SHIBUYA OPEN DATA https://city-shibuya-data.opendata.arcgis.com/
- 東京都オープンデータカタログ https://catalog.data.metro.tokyo.lg.jp/ ／API https://portal.data.metro.tokyo.lg.jp/opendata-api/
- 東京都デジタルツイン3Dビューア https://info.tokyo-digitaltwin.metro.tokyo.lg.jp/3dmodel/
- 気象庁 利用規約 https://www.jma.go.jp/jma/kishou/info/coment.html
- 環境省 WBGT 電子情報提供サービス https://www.wbgt.env.go.jp/data_service.php
- JARTIC 交通量オープンデータ https://www.jartic-open-traffic.org/ ／xROAD https://www.xroad.mlit.go.jp/
- 東京メトロ Metro CrowdNavi（2026-06-16） https://prtimes.jp/main/html/rd/p/000001478.000020053.html
- モバイル空間統計 https://mobaku.jp/ ／Agoop https://agoop.co.jp/mail_movie_academic/ ／LocationMind xPop https://locationmind.com/products/xpop-e/
- 渋谷100台プロジェクト https://idea.i-d.ai/shibuya-project/

**データ同化・較正**
- Suchak et al. 2024, R. Soc. Open Sci. 11(4)（ABM×EnKF） https://pmc.ncbi.nlm.nih.gov/articles/PMC11017988/
- Malleson et al. 2020（ABM×粒子フィルタ） https://www.semanticscholar.org/paper/1ff393c97e3a32e967d7e26784cd22662108014c
- Ternes et al.（カテゴリカル・パラメータ同化） https://pmc.ncbi.nlm.nih.gov/articles/PMC10445938/
- DUST プロジェクト https://urban-analytics.github.io/dust/
- Calibrating ABMs Using UQ Methods, JASSS 25(2)1 https://www.jasss.org/25/2/1.html
- UQ for ABMs: A Tutorial, arXiv:2409.16776 https://arxiv.org/pdf/2409.16776

**群衆カウント技術**
- P2PNet（ICCV2021 Oral） https://github.com/TencentYoutuResearch/CrowdCounting-P2PNet
- 群衆密度推定サーベイ（2025） https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/ipr2.13328
