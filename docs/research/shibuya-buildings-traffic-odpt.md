# 渋谷ナイトシミュレーション用リサーチ

調査日: 2026-07-04
対象範囲: 渋谷駅周辺（緯度 35.6560〜35.6625、経度 139.6950〜139.7060）

出典URLは各項目に付記。数値・階構成は公式フロアガイドおよび政府機関を優先。不審ドメインは不使用。

---

## 調査1: 渋谷主要ビルの実フロア構成

注: フロア用途カテゴリは `restaurant / fashion / beauty / lifestyle / food(食物販) / office / observation / hall / theatre / hotel / station / park / bus` を使用。
各ビルは代表階レベルで網羅（一部は用途ゾーン単位のため代表テナントを付記）。

### 渋谷スクランブルスクエア（東棟, 地下2F〜47F, 高さ約230m, 2019開業）

出典: 公式フロアガイド https://www.shibuya-scramble-square.com/floorguide/ , SHIBUYA SKY https://www.shibuya-scramble-square.com/sky/ , 東京ビルマップ https://building.tokyo/shibuya-scramble-square-east/

```json
{"building": "渋谷スクランブルスクエア", "floors": [
  {"f": -2, "use": "food", "label": "フード（B2F〜1F 食物販ゾーン）"},
  {"f": -1, "use": "food", "label": "フード"},
  {"f": 1, "use": "food", "label": "フード・エントランス"},
  {"f": 2, "use": "fashion", "label": "ファッション（2F〜5F）"},
  {"f": 3, "use": "fashion", "label": "ファッション"},
  {"f": 4, "use": "fashion", "label": "ファッション"},
  {"f": 5, "use": "fashion", "label": "ファッション"},
  {"f": 6, "use": "beauty", "label": "ビューティー"},
  {"f": 7, "use": "fashion", "label": "ファッション（7F〜8F）"},
  {"f": 8, "use": "fashion", "label": "ファッション"},
  {"f": 9, "use": "lifestyle", "label": "ライフスタイルグッズ（9F〜11F）／ハンズ入居"},
  {"f": 10, "use": "lifestyle", "label": "ライフスタイルグッズ／ハンズ"},
  {"f": 11, "use": "lifestyle", "label": "ライフスタイルグッズ／ハンズ"},
  {"f": 12, "use": "restaurant", "label": "レストラン（12F〜13F）"},
  {"f": 13, "use": "restaurant", "label": "レストラン"},
  {"f": 14, "use": "observation", "label": "SHIBUYA SKY チケット/入口・ライフスタイルグッズ"},
  {"f": 15, "use": "office", "label": "共創施設 SHIBUYA QWS"},
  {"f": 17, "use": "office", "label": "オフィス（17F〜45F）"},
  {"f": 45, "use": "observation", "label": "SHIBUYA SKY 屋内展望 SKY GALLERY"},
  {"f": 46, "use": "observation", "label": "SHIBUYA SKY 移動空間"},
  {"f": 47, "use": "observation", "label": "屋上 SKY STAGE（約2,500㎡・SKY EDGE・ルーフトップバー・クラウドハンモック）"}
]}
```

### 渋谷ヒカリエ（地下3F〜17F, 2012開業）

出典: 公式 https://www.hikarie.jp/floorguide/ , ShinQs（東急百貨店） https://www.tokyu-dept.co.jp/shinqs/floor/

```json
{"building": "渋谷ヒカリエ", "floors": [
  {"f": -3, "use": "food", "label": "東横のれん街（惣菜・生鮮・イートイン）／副都心線・東横線改札方面"},
  {"f": -2, "use": "food", "label": "東横のれん街（スイーツ・ベーカリー・ワイン）"},
  {"f": -1, "use": "beauty", "label": "ShinQs Beauty（化粧品）"},
  {"f": 1, "use": "beauty", "label": "ShinQs Beauty（ビューティー・ファッション雑貨）"},
  {"f": 2, "use": "fashion", "label": "ShinQs Fashion（ファッション雑貨・インフォメーション・シアター連絡）"},
  {"f": 3, "use": "fashion", "label": "ShinQs Fashion（アパレル）"},
  {"f": 4, "use": "fashion", "label": "ShinQs Fashion（ファッション・ライフスタイル）"},
  {"f": 5, "use": "lifestyle", "label": "ShinQs Lifestyle（生活雑貨）"},
  {"f": 6, "use": "restaurant", "label": "dining 6（カフェ&レストラン）"},
  {"f": 7, "use": "restaurant", "label": "TABLE 7（カフェ&レストラン）"},
  {"f": 8, "use": "hall", "label": "8/（はち）クリエイティブスペース・渋谷区関連施設"},
  {"f": 9, "use": "hall", "label": "ヒカリエホール（イベント）"},
  {"f": 11, "use": "theatre", "label": "東急シアターオーブ スカイロビー・チケット・会議室"},
  {"f": 16, "use": "theatre", "label": "東急シアターオーブ（劇場）"},
  {"f": 17, "use": "office", "label": "オフィス"}
]}
```
補足: 11F〜16Fが劇場「東急シアターオーブ」、上層階はオフィス（〜34F, 高さ約182m）。

### SHIBUYA109（地下2F〜8F）

出典: 公式フロアマップ https://shibuya109.jp/floor-map/ , 攻略ガイド（スタッフブリッジ） https://www.staff-b.com/topics/detail/718/
注: 個店構成は入れ替わりが激しい。用途ゾーンの代表像として記載。

```json
{"building": "SHIBUYA109", "floors": [
  {"f": -2, "use": "food", "label": "MOG MOG STAND（スイーツ・スムージー・ポップアップ）"},
  {"f": -1, "use": "fashion", "label": "ファッション（B1F〜3Fが中核ファッション約120店）"},
  {"f": 1, "use": "fashion", "label": "ファッション"},
  {"f": 2, "use": "fashion", "label": "ファッション"},
  {"f": 3, "use": "fashion", "label": "ファッション"},
  {"f": 4, "use": "beauty", "label": "ライフスタイル・コスメ・アクセサリー（4F〜6F）"},
  {"f": 5, "use": "beauty", "label": "ビューティー・セルフフォトスタジオ"},
  {"f": 6, "use": "beauty", "label": "ビューティー・カルチャー"},
  {"f": 7, "use": "restaurant", "label": "コラボカフェ・イベントスペース（7F〜8F）"},
  {"f": 8, "use": "office", "label": "イベントスペース／SHIBUYA109 lab"}
]}
```

### 渋谷マークシティ（1F〜4F 商業＋オフィス/ホテル棟, 2000開業）

出典: 公式 https://www.s-markcity.co.jp/floor/ （ウエスト/イーストモール各階）
構造: ウエストモール(1F・2F)、イーストモール(1F・2F・3F)、アベニュー(4F)。5F以上はオフィス(イースト)とホテル「渋谷エクセルホテル東急」。京王井の頭線渋谷駅・バスターミナルが接続。

```json
{"building": "渋谷マークシティ", "floors": [
  {"f": 1, "use": "restaurant", "label": "ウエスト/イーストモール1F（ショップ&レストラン、日本料理『旬彩』、京王井の頭線改札・道玄坂連絡）"},
  {"f": 2, "use": "restaurant", "label": "ウエスト2F『BAKERY RESTAURANT C』/イースト2F『魚金醸造』・セブンイレブン"},
  {"f": 3, "use": "restaurant", "label": "イーストモール3F ショップ&レストラン"},
  {"f": 4, "use": "restaurant", "label": "アベニュー4F（飲食・ホテルロビー連絡）"},
  {"f": 5, "use": "hotel", "label": "渋谷エクセルホテル東急（イースト棟上層）"},
  {"f": 6, "use": "office", "label": "オフィス（イースト棟）"}
]}
```

### 渋谷ストリーム（1F〜35F, 2018開業）

出典: 公式 https://shibuyastream.jp/ , 東京ビルマップ https://building.tokyo/shibuya-stream/

```json
{"building": "渋谷ストリーム", "floors": [
  {"f": 1, "use": "restaurant", "label": "商業ゾーン（1F〜3F、全約30店のレストラン・グルメ、渋谷川・稲荷橋広場）"},
  {"f": 2, "use": "restaurant", "label": "商業ゾーン"},
  {"f": 3, "use": "restaurant", "label": "商業ゾーン"},
  {"f": 4, "use": "hall", "label": "ホール（4F〜6F、スタンディング約700名）＋ホテルフロント/ロビー/バー『TORRENT』"},
  {"f": 5, "use": "hall", "label": "渋谷ストリームホール"},
  {"f": 6, "use": "hall", "label": "渋谷ストリームホール"},
  {"f": 9, "use": "hotel", "label": "渋谷ストリームエクセルホテル東急（4F・9F〜13F、客室177室）"},
  {"f": 13, "use": "hotel", "label": "ホテル上層"},
  {"f": 14, "use": "office", "label": "オフィス（14F〜35F、全フロアをGoogle日本法人が入居）"},
  {"f": 35, "use": "office", "label": "オフィス（Google）"}
]}
```

### 渋谷パルコ（地下1F〜10F, 2019建て替え開業）

出典: 公式フロアガイド https://shibuya.parco.jp/floor/ , 6F https://shibuya.parco.jp/feature/detail/?id=1705

```json
{"building": "渋谷パルコ", "floors": [
  {"f": -1, "use": "restaurant", "label": "CHAOS KITCHEN（ダイニング・バー・食物販）"},
  {"f": 1, "use": "fashion", "label": "ファッション/ラグジュアリー"},
  {"f": 2, "use": "fashion", "label": "ファッション"},
  {"f": 3, "use": "fashion", "label": "ファッション"},
  {"f": 4, "use": "fashion", "label": "ファッション/アート"},
  {"f": 5, "use": "lifestyle", "label": "ライフスタイル・雑貨"},
  {"f": 6, "use": "fashion", "label": "CYBERSPACE SHIBUYA（Nintendo TOKYO・ポケモンセンターシブヤ・JUMP SHOP・CAPCOM STORE TOKYO）"},
  {"f": 7, "use": "restaurant", "label": "レストラン・ミュージアム（PARCO MUSEUM 等）"},
  {"f": 8, "use": "hall", "label": "劇場 WHITE CINE QUINTO / イベント"},
  {"f": 10, "use": "restaurant", "label": "屋上 ComMunE / PBOX STND（カフェ&バー・イベントスペース）"}
]}
```

### 渋谷モディ（渋谷MODI, 地下1F〜10F, マルイ系）

出典: 公式フロアガイド https://www.0101.co.jp/721/info/ , HMV&BOOKS SHIBUYA https://www.0101.co.jp/721/shop-guide/shop-detail.html?shop_id=5773
注: 5F〜7Fに HMV&BOOKS SHIBUYA（首都圏最大級の書籍＋音楽複合、5F/6F書籍・7F音楽）。他フロアはファッション・雑貨・飲食・クリニック等。個別階の一次ソースが薄いため一部「未確認」。

```json
{"building": "渋谷モディ", "floors": [
  {"f": 1, "use": "fashion", "label": "物販・カフェ（未確認: 個別テナント）"},
  {"f": 2, "use": "fashion", "label": "ファッション・雑貨（未確認）"},
  {"f": 3, "use": "fashion", "label": "ファッション・雑貨（未確認）"},
  {"f": 4, "use": "lifestyle", "label": "雑貨・サービス（未確認）"},
  {"f": 5, "use": "lifestyle", "label": "HMV&BOOKS SHIBUYA（書籍）"},
  {"f": 6, "use": "lifestyle", "label": "HMV&BOOKS SHIBUYA（書籍）"},
  {"f": 7, "use": "lifestyle", "label": "HMV&BOOKS SHIBUYA（音楽・イベント）"},
  {"f": 8, "use": "restaurant", "label": "飲食・サービス（未確認）"},
  {"f": 9, "use": "office", "label": "クリニック・サービス（未確認）"},
  {"f": 10, "use": "office", "label": "サービス（未確認）"}
]}
```

### MIYASHITA PARK（RAYARD MIYASHITA PARK, 1F〜3F＋屋上, 2020開業）

出典: 公式フロアガイド https://mitsui-shopping-park.com/urban/miyashita/floorguide.html , 渋谷横丁 https://shibuya-yokocho.com/ , Wikipedia https://ja.wikipedia.org/wiki/MIYASHITA_PARK
構造: 低層に商業「RAYARD」、屋上に区立宮下公園（芝生広場・スケート/ボルダリング・カフェ）、原宿寄りにホテル「sequence MIYASHITA PARK」。North/Southの2棟構成、全長約330m。

```json
{"building": "MIYASHITA PARK (RAYARD)", "floors": [
  {"f": 1, "use": "restaurant", "label": "渋谷横丁（北海道〜沖縄の郷土料理、約19店・100m）／ファッション・サービス"},
  {"f": 2, "use": "fashion", "label": "ファッション・雑貨・レストラン・カフェ・サービス"},
  {"f": 3, "use": "fashion", "label": "ファッション・雑貨・カフェ・レストラン・サービス"},
  {"f": 4, "use": "park", "label": "屋上 区立宮下公園（芝生広場・スポーツ施設）／カフェ／ホテル sequence"}
]}
```

### 渋谷フクラス（東急プラザ渋谷, 地下4F〜18F, 高さ約103m, 2019開業）

出典: 公式 https://www.shibuya-fukuras.jp/floorguide/ , 東急プラザ渋谷 https://www.tokyu-plaza.com/shibuya/shop/floor , シブヤ経済新聞 https://www.shibukei.com/headline/14652/

```json
{"building": "渋谷フクラス（東急プラザ渋谷）", "floors": [
  {"f": 1, "use": "bus", "label": "渋谷駅西口バスターミナル（空港リムジンバス乗り入れ）"},
  {"f": 2, "use": "fashion", "label": "東急プラザ渋谷（AKOMEYA TOKYO・BEAMS JAPAN 等 日本文化・工芸、2F〜4F）"},
  {"f": 3, "use": "fashion", "label": "東急プラザ渋谷（大人向け物販）"},
  {"f": 4, "use": "beauty", "label": "健康・美 関連"},
  {"f": 5, "use": "office", "label": "ライフプラン相談等サービス"},
  {"f": 6, "use": "restaurant", "label": "飲食フロア『シブヤグラン食堂』（6F・7F）"},
  {"f": 7, "use": "restaurant", "label": "シブヤグラン食堂"},
  {"f": 8, "use": "restaurant", "label": "飲食・サービス"},
  {"f": 9, "use": "office", "label": "オフィス（9F〜16F）"},
  {"f": 16, "use": "office", "label": "オフィス"},
  {"f": 17, "use": "park", "label": "東急プラザ渋谷（17F・18F）＋ルーフトップ『SHIBU NIWA（シブニワ）』スクランブル交差点一望"},
  {"f": 18, "use": "park", "label": "ルーフトップガーデン SHIBU NIWA"}
]}
```

### 渋谷駅そのもの（4社9路線, 地上3F〜地下5F）

出典: Wikipedia「渋谷駅」 https://ja.wikipedia.org/wiki/%E6%B8%8B%E8%B0%B7%E9%A7%85 , 乗りものニュース https://trafficnews.jp/post/81473 , 東京メトロ https://www.tokyometro.jp/station/shibuya/index.html
概要: スクランブル交差点の標高が約15mあるため谷地形。銀座線が高架3F、JRが2F、地下深部に半蔵門/田園都市線・副都心/東横線という縦積み構造。

```json
{"building": "渋谷駅（鉄道）", "floors": [
  {"f": 3, "use": "station", "label": "東京メトロ銀座線 ホーム（高架3F, G01）"},
  {"f": 2, "use": "station", "label": "JR山手線・埼京線・湘南新宿ライン ホーム（2F）／京王井の頭線は西側2F相当・マークシティ内"},
  {"f": 1, "use": "station", "label": "ハチ公口・中央改札・地上コンコース"},
  {"f": -1, "use": "station", "label": "地下コンコース・連絡通路（渋谷ちかみち）"},
  {"f": -3, "use": "station", "label": "東急田園都市線・東京メトロ半蔵門線 ホーム（地下3F, Z01）"},
  {"f": -5, "use": "station", "label": "東急東横線・東京メトロ副都心線 ホーム（地下5F, 明治通り直下, 島式2面4線, F16）"}
]}
```

### 渋谷ちかみち（地下通路網）

出典: 東急電鉄「渋谷ちかみち」 https://www.tokyu.co.jp/shibuyachikamichi/shibuyatsuu , 乗換ルート案内 https://www.tokyu.co.jp/shibuyachikamichi/route_guide , 東京メトロ構内図 https://www.tokyometro.jp/station/shibuya/yardmap/index_print.html

- 定義: 渋谷ヒカリエ〜SHIBUYA109まで、渋谷駅地下を端から端まで結ぶ地下通路網の総称。
- エリア分け（ハチ公前広場中心）: A=109/マークシティ/スクランブル交差点側、B=JRを跨いだ東口/明治通り/ヒカリエ/宮下公園側、C=渋谷川沿い/渋谷ストリーム側、D=西口フクラス/桜丘町側。
- 出入口ナンバリング: A0〜A12、B1〜B7、C1〜C3、D系統。
- 設備: 「渋谷ちかみちラウンジ」にトイレ・パウダールーム・ドレッシングルーム・授乳室・ベビールーム・Wi-Fi・案内所。

```json
{"building": "渋谷ちかみち", "areas": [
  {"code": "A", "use": "station", "label": "109・マークシティ・スクランブル交差点方面（A0〜A12）"},
  {"code": "B", "use": "station", "label": "東口・明治通り・ヒカリエ・宮下公園方面（B1〜B7）"},
  {"code": "C", "use": "station", "label": "渋谷川・渋谷ストリーム方面（C1〜C3）"},
  {"code": "D", "use": "station", "label": "西口・フクラス・桜丘町方面（D系統）"}
]}
```

---

## 調査2: 渋谷の道路交通量

出典（一次データ）:
- 国土交通省「令和3年度 全国道路・街路交通情勢調査（道路交通センサス）」 https://www.mlit.go.jp/road/census/r3/
- 令和3年度 一般交通量調査結果 WEBマップ（可視化ツール） https://www.mlit.go.jp/road/ir/ir-data/census_visualizationR3/index.html
- e-Stat 政府統計 全国道路・街路交通情勢調査 https://www.e-stat.go.jp/statistics/00600580
- 東京都建設局 令和3年度センサス結果 https://www.kensetsu.metro.tokyo.lg.jp/road/information/3sensasu
- 渋谷区「渋谷駅周辺地域交通戦略 第2章 交通実態」PDF https://files.city.shibuya.tokyo.jp/assets/12995aba8b194961be709ba879857f70/032add40cb1a4c7592a1c4ceda327f2e/assets_kankyo_000050292.pdf

重要な注意: 各道路の区間別「台/日」の正確な数値は、上記センサスのPDF/CSV/可視化ツール（区間コード単位）に格納されており、Web検索の要約テキストからは**正確な断面交通量を取得できなかった**。推測で埋めることを避け、確認できた事実と数値未確認を明記する。実装時は可視化ツールまたは e-Stat の「基礎集計（区間別）」CSVで渋谷区の該当区間コードを引くのが確実。

| 道路 | 種別 | 車線・確認事実 | 日交通量(台/日) | 状態 |
|---|---|---|---|---|
| 国道246号（玉川通り） | 一般国道（幹線） | 渋谷警察署前交差点付近から首都高3号渋谷線が上空、地下に田園都市線。片側3車線。渋谷区内は都内屈指の交通量・二輪車最多。 | 未確認（センサスに区間値あり） | 数値未確認 |
| 国道246号（青山通り, 宮益坂上以東） | 一般国道 | 渋谷駅東側で明治通りと交差、青山方面へ | 未確認 | 数値未確認 |
| 明治通り（都道305号） | 主要地方道 | 渋谷駅東側を南北。地下5Fに東横/副都心線が直下併走。 | 未確認 | 数値未確認 |
| 道玄坂（区道/都道系） | 坂道商業道路 | マークシティ・109方面へ上る。歩行者交通が非常に多い。 | 未確認 | 数値未確認 |
| 公園通り | 区道 | 渋谷駅ハチ公方面〜代々木公園/NHK方面。歩行者中心。 | 未確認 | 数値未確認 |
| ファイヤー通り（神南, 消防署通り） | 区道 | 神南エリア。歩行者・地元交通中心。 | 未確認 | 数値未確認 |
| 宮益坂 | 都道系 | 渋谷駅東口〜青山方面へ上る。246号（青山通り）へ接続。 | 未確認 | 数値未確認 |

参考（歩行者・自転車を含む交通実態の定性）: 渋谷区の交通戦略資料は自動車・歩行者・自転車の交通量推移を扱うが、当セッションでは当該PDFのテキスト抽出に失敗（バイナリ7.7MB）。数値化には現地DL/OCRが必要。

ヒント（実装者向け）: 可視化ツール（R3）は緯度経度からクリックで「観測地点番号・24時間自動車類交通量・昼間12時間交通量・大型車混入率・旅行速度」が読める。渋谷駅周辺の246号・明治通りは主要地点として登録されている。

---

## 調査3: ODPT（公共交通オープンデータ）APIキー取得手順

出典:
- ODPT 開発者サイト 登録 https://developer.odpt.org/signup
- 東京公共交通オープンデータ 開発者サイト https://developer-tokyochallenge.odpt.org/
- API利用ガイドライン https://developer-tokyochallenge.odpt.org/terms/api_guideline.html
- 公共交通オープンデータ協議会 概要 https://www.odpt.org/overview/
- データカタログ（CKAN） https://ckan.odpt.org/
- API移行解説（参考ブログ） https://mikan.github.io/2022/03/31/migrate-odpt-api/

### 登録手順・条件
1. `https://developer.odpt.org/signup` でユーザ登録（メールアドレス・パスワード等）。サイトはJavaScript必須。
2. 登録内容の**確認に最大2営業日程度**（自動即時ではなく内容確認あり）。
3. **無料**（ユーザ登録・API利用とも無料）。API利用規約・API仕様書への同意が前提。
4. 登録完了後、開発者サイト上で**アクセストークン（consumerKey）**を発行。初期に `DefaultApplication` トークンが発行されるが、用途ごとに個別発行が推奨。第三者へのトークン開示は禁止。
5. サンプルコード公開時はトークンを埋め込まず `acl:consumerKey=ACL_CONSUMERKEY` にマスクする規約。

補足: 従来「東京公共交通オープンデータチャレンジ（developer-tokyochallenge.odpt.org, api-challenge.odpt.org）」と、常設の「公共交通オープンデータセンター（developer.odpt.org, api.odpt.org）」の2系統がある。現行の本番は `api.odpt.org/api/v4`。JR東日本の一部リアルタイムはチャレンジ側（api-challenge）に残る場合あり。

### エンドポイント形式（v4, REST + JSON-LD）
ベース: `https://api.odpt.org/api/v4/`
共通クエリ: `?acl:consumerKey=YOUR_TOKEN`（＋ `odpt:operator=` 等でフィルタ）

主なデータ種別と例:
- 運行情報: `GET https://api.odpt.org/api/v4/odpt:TrainInformation?odpt:operator=odpt.Operator:TokyoMetro&acl:consumerKey=YOUR_TOKEN`
- 列車ロケーション（動的）: `GET https://api.odpt.org/api/v4/odpt:Train?odpt:operator=odpt.Operator:JR-East&acl:consumerKey=YOUR_TOKEN`
- 駅時刻表（静的）: `odpt:StationTimetable`、路線: `odpt:Railway`、駅: `odpt:Station`
- GTFS-RT（東京メトロ 例）: `GET https://api.odpt.org/api/v4/gtfs/realtime/tokyometro_odpt_train_alert?acl:consumerKey=YOUR_TOKEN`
- JR東日本アイステイションズ GTFS-RT（チャレンジ側 例）: `https://api-challenge.odpt.org/api/v4/gtfs/realtime/jreis_odpt_train_alert?acl:consumerKey=YOUR_TOKEN`

事業者ID（odpt:operator）の例:
- JR東日本（山手線含む）: `odpt.Operator:JR-East`
- 東京メトロ: `odpt.Operator:TokyoMetro`
- 東急: `odpt.Operator:Tokyu`
- 都営: `odpt.Operator:Toei`

対象データ（渋谷関連）:
- JR山手線: `odpt.Railway:JR-East.Yamanote`（列車ロケーション・遅延・時刻表）
- 東京メトロ銀座線/半蔵門線/副都心線: `odpt.Railway:TokyoMetro.Ginza` 等
- 東急東横線/田園都市線: `odpt.Railway:Tokyu.Toyoko` / `odpt.Railway:Tokyu.DenEnToshi`
- GTFS静的（路線・駅・時刻表一括）はデータカタログ ckan.odpt.org から事業者別に取得可能。

注意（正確性）: 上記URL例のうち `odpt:TrainInformation`（東京メトロ）と GTFS-RT（tokyometro/jreis）のパス形はデータカタログ/公式ドキュメントで確認済み。`odpt:Train`（列車ロケーション）のオペレータ別提供可否は事業者により異なる（JR-Eastは提供項目が限定的な時期あり）ため、実装前にデータカタログ ckan.odpt.org で各事業者の提供リソースを要確認。

---

## サマリ（要点）
- 主要10ビル＋渋谷駅＋ちかみちのフロア/用途構成を機械可読JSONで整理済み。スクランブルスクエア(SHIBUYA SKY 14F/45-47F)、ヒカリエ、109、マークシティ、ストリーム(14-35F Google)、パルコ(6F ゲーム聖地)、フクラス、MIYASHITA PARK(屋上公園)は公式ソースで用途カテゴリ付与。モディの一部個別階と交通量の実数値は「未確認」と明記。
- 道路交通量: 一次ソース（令和3年度センサス可視化ツール/e-Stat/東京都建設局/渋谷区交通戦略PDF）を特定したが、区間別「台/日」の正確値はWeb要約から抽出不能のため全て「未確認」表記。実装時は可視化ツールで観測地点値を直接読む手順を記載。
- ODPT: 登録無料・内容確認最大2営業日・審査は同意ベース。本番APIは `api.odpt.org/api/v4` でconsumerKey付与、`odpt:TrainInformation`/`odpt:Train`/GTFS-RTのURL形と主要事業者ID（JR-East/TokyoMetro/Tokyu）を提示。
