# data/jinryu/ — 渋谷中心部の同時滞在人口 生データ(出所・ライセンス)

本フォルダは「同時に何人が渋谷に集まるのか」を実データで確定するための一次データと派生物。
分析本体は `docs/research/shibuya-concurrent-population.md`。

## 一次データ: 全国の人流オープンデータ(1kmメッシュ)

- 提供: 国土交通省 不動産・建設経済局(データ作成は Agoop社の GPS由来 換算人口値)
- データセット: 「全国の人流オープンデータ(1kmメッシュ、市区町村単位発地別)」
  - カタログ: https://www.geospatial.jp/ckan/dataset/mlit-1km-fromto
  - 掲載(国交省): https://www.mlit.go.jp/tochi_fudousan_kensetsugyo/tochi_fudousan_kensetsugyo_fr17_000001_00006.html
- ダウンロード元(東京都、monthly_mdp_mesh1km_13):
  https://www.geospatial.jp/ckan/dataset/8fd79f08-00e6-4d14-9c89-e3bdca66af11/resource/3b69ffab-2fb8-4901-9cf3-9da2c19e3351/download/monthly_mdp_mesh1km_13.zip
  - 取得日 2026-07-19。ブラウザ相当 User-Agent での GET で取得可(HEAD/既定UAは403)。要ログインの案内はあるが実際の認証は不要だった。
- 定義書PDF: https://www.geospatial.jp/ckan/dataset/8fd79f08-00e6-4d14-9c89-e3bdca66af11/resource/e2083495-8095-4119-a865-e5c22e6a7eee/download/opendatadefinition.pdf
- メッシュ属性(座標): .../download/attribute.zip(本フォルダの *_attribute.csv はここから該当6メッシュを転記)

### ライセンス = 政府標準利用規約(第2.0版) / license_id=ogl
- CC BY 4.0 互換。**出典明記の上で複製・再配布・加工が可能**。→ 本リポジトリへのコミット可(ODPTチャレンジ等の再配布制限データとは異なり gitignore 不要)。
- 出典表示例:「国土交通省『全国の人流オープンデータ』(Agoop社換算人口値)を加工して作成」

### 定義(定義書PDFより、要点)
- `population` = 滞在人口(平均)。**換算人口値**: ①アプリ利用者を全国人口に拡大推計 ②メッシュ集計 ③**滞在時間で按分**(あるメッシュに10分滞在→その1時間で1/6人と数える)。
  → 値は「その時間帯・その月の平日/休日で、瞬間あたり平均何人が“居た”か」= **同時滞在(concurrent presence)の期待値**。累積通行量(footfall)ではない。ユーザーの問い「同時に何人」に直接対応する量。
- `timezone`: 0=昼(**11時台〜14時台の平均**) / 1=深夜(**1時台〜4時台の平均**) / 2=終日(0〜23時台の平均)
- `dayflag`: 0=休日 / 1=平日 / 2=全日
- 単位=人(整数)、月別・1日あたり平均。10人未満のメッシュは非出力。
- 収録: 2019/1〜2021/12(定義書表記は24ヶ月だが実データは36ヶ月に拡張済)。

## 対象メッシュ(渋谷中心 bbox=[35.6505,139.6905]〜[35.6685,139.7115] を包含)
コア4メッシュ 53393585/86/95/96(すべて citycode=13113 渋谷区)で lon 139.6875–139.7125・lat 35.6500–35.6667 をカバー。
bbox南北の約91%(北端 35.6667–35.6685 の約200m帯のみ欠、これは北スリバー 53394505/06 が担当・bbox内は各21%)。
座標詳細は `shibuya_mesh1km_attribute.csv`。

## ファイル
- `shibuya_mesh1km_2019_2021.csv` — 一次データから該当6メッシュ全行を抽出した**生データ**(6メッシュ×36ヶ月×9区分=1944行)。列は定義書のまま。
- `shibuya_mesh1km_attribute.csv` — 該当6メッシュの緯度経度矩形(attribute.zip 由来)。
- `shibuya_concurrent_144step_curve.csv` — **派生物**。2019年コア4メッシュ平均を昼(11-14)/深夜(1-4)/終日(0-23)の3アンカーに拘束し、公表された日内形状(ドコモ区ビジョン)で内挿した平日/休日の10分刻み144stepテーブル。派生の手順は本体docの§7。

## 補助出典(絶対値の形状・イベント)
- 渋谷区 産業・観光ビジョン(ドコモ モバイル空間統計 2018): https://files.city.shibuya.tokyo.jp/assets/12995aba8b194961be709ba879857f70/a0407bb8a8074a2cb4f3e06a08cbc370/assets_com_000047966.pdf
  - p19: エリア別 1日の人の動き(深夜0時基準の24h推移、250mメッシュ)/ p21: スクランブル交差点周辺のイベント時人波(縦軸0-50000、ハロウィン21-22時ピーク・カウントダウン23-24時ピーク)
- モバイル空間統計 渋谷分析: https://mobaku.jp/analysis/2022/1102_849.html
- 渋谷ハロウィン(1日100万人規模): https://ja.wikipedia.org/wiki/渋谷ハロウィン
- 年越しカウントダウン人出(シブヤ経済新聞): https://www.shibukei.com/headline/12817/ ほか
