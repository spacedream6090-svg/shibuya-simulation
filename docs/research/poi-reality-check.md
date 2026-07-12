# 実装済みPOI vs 現実の渋谷 — 再現度検証(調査、2026-07-07)

> 調査目的: シミュに実装済みのPOI(Point of Interest)が、現実の渋谷駅周辺(半径〜1km)を
> どれほど再現できているかを検証し、過不足と追加推奨をまとめる。**次波で宿泊(ホテル)機能を
> 実装予定**のため、宿泊施設がシミュに存在するかを最優先で明記する。
>
> 制約: 本ドキュメントは調査レポートのみ。`src/` `conf/` `data/` は変更していない。
> POIデータは OpenStreetMap contributors(ODbL)由来。

---

## 0. 結論(先出し)

1. **本番シミュが読む地図は最古スキーマの小型地図 `data/shibuya_osm.json`(v3・約1.0×0.7km)**。
   より広く・分類も新しい `shibuya_osm_wide_20250401.json`(v6・約2.0×2.0km、POI 1,965件)が
   すでに `data/` に存在するのに、`conf/config.yaml` の既定(`map: data/shibuya_osm.json`)を
   `conf/production.yaml` が上書きしていないため使われていない。**これが最大の再現ギャップ**。
2. **ホテルはPOIとして「存在する」が、宿泊機能は皆無**。本番地図に hotel カテゴリPOIが8件
   (セルリアンタワー、渋谷エクセルホテル東急、Tokyu Inn、The Millennials 渋谷、カプセル、
   渋谷シティホテル、GRANDBEL HOTEL、ホテルインディゴ東京渋谷)。ただしコード上は
   `commerce.py` で「常時営業カテゴリ」、`vision.py` で視認顕著性の重み(=3)として参照される
   だけで、**チェックイン・宿泊・滞在の仕組みは一切ない**(次波の実装余地=まっさら)。
3. コア商業(109/ヒカリエ/スクランブルスクエア/PARCO/マークシティ/ストリーム/フクラス/西武)は
   **建物として概ね網羅**。飲食・物販・夜遊びのPOI密度も1km圏としては妥当(food 423 + nightlife 191
   + shop 310)。
4. 一方、**行政中枢・大公園・大学・映画館・ライブハウスの「機能的分類」が本番地図では欠落**。
   本番v3地図には `cinema`/`hall`/`landmark`/`school` カテゴリが存在せず、映画館は `service`、
   忠犬ハチ公像POIは不在(ノード名としてのみ存在)。代々木公園・北谷公園・渋谷区役所(本庁舎)・
   金王八幡宮・青山学院・実践女子・渋谷消防署は**bbox外**で本番地図に無い(wide地図には有る)。
5. OSM抽出の構造的欠落: **WOMB・トランクホテル・総合病院・ゲームセンター**は wide 地図にも無い
   (要手動追加)。コンビニ・カラオケ・ゲーセンは専用カテゴリが無く `shop`/`nightlife` に溶けている。

**最小コストの是正**: 本番プロファイルの地図を wide 版へ差し替える(下記 §5 Tier A)。
それだけで hotel 24件・cinema 7件・hall 18件・landmark 24件・school 68件・代々木公園・北谷公園・
区役所・金王八幡宮・青山学院・実践女子・消防署が一括で入る。

---

## 1. シミュのPOIデータ(実装状況)

### 1.1 データ構造と座標系

- 地図ローダ: `src/society/world/map.py`(`CityMap`)。生成: `scripts/build_map.py`(Overpass API)。
- 座標系: `crs="local-m"`。原点=スクランブル交差点 `(35.6595, 139.70062)`。x=東(m)、y=北(m)。
  投影 `project(lat,lon)`: `x=(lon-139.70062)*111320*cos(35.6595°)`、`y=(lat-35.6595)*110540`。
- POIレコード形式(`pois[]`):
  ```json
  {"id": "p_w123", "name": "渋谷パルコ", "cat": "shop",
   "x": -220.4, "y": 289.1, "node": "n456", "building": "b789", "floor": 2}
  ```
  `cat` は `poi_category()`(build_map.py)が OSM タグから決める。`node`=最寄り道路ノード、
  `building`=内包する大建物ID(任意)、`floor`=階(任意)。
- 建物レコード(`buildings[]`)は `kind`(residential/office/retail/station/hotel/public/generic/house?)を持つ。
- 待ち合わせ名所は2系統: (a) `build_map.py` の `LANDMARKS` ハードコード(スクランブル交差点・
  ハチ公前広場・109・センター街・道玄坂・文化村通り・スペイン坂・PARCO・公園通り・宮下公園・
  宮益坂下・ストリーム・マークシティ)を**ノード名**として付与、(b) v6以降は `cat="landmark"` の
  **POI**(忠犬ハチ公像等)。`destinations()` は両方を行き先候補に含める。

### 1.2 各地図ファイルのPOI集計

| ファイル | ver | bbox(概略) | nodes | buildings | POI総数 | 備考 |
|---|---|---|---|---|---|---|
| **`shibuya_osm.json`** ★本番既定 | 3 | 約1.0×0.7km | 1,289 | 1,181 | **1,098** | 最古スキーマ。cinema/hall/landmark/school カテゴリ無し |
| `shibuya_osm_v6.json` | 6 | 約1.0×0.7km | 1,300 | 1,181 | 1,117 | v3と同範囲だが新カテゴリ有り(cinema6/hall12/landmark15/school12) |
| `shibuya_osm_wide.json` | 6 | 約2.0×1.6km | 3,234 | 6,202 | 1,903 | 広域。ただし cinema/hall/landmark=0、education 50(旧カテゴリ名) |
| `shibuya_osm_wide_20250401.json` | 6 | 約2.0×2.0km | 3,499 | 7,210 | **1,965** | 最新・最広・最も分類が揃う(下記) |

### 1.3 本番地図(`shibuya_osm.json`)のカテゴリ分布

| cat | 件数 | 代表例(実データより) | 機能配線 |
|---|---|---|---|
| food | 423 | (飲食店全般) | ○ commerce/routine(食事) |
| shop | 310 | ハンズ、ロフト等 + コンビニ・物販が全て混在 | ○ economy/scheduler(買物) |
| nightlife | 191 | 和民、土間土間、白木屋、ビッグエコー、カラオケ館、CLUB COSTA DEL SOL 等 | ○ routine(夜の食事) |
| service | 70 | 郵便局・銀行(みずほ/三菱UFJ/三井住友)・交番・薬局・**TOHOシネマズ/Cinemarise(映画館が誤分類)** | △ 目的地のみ |
| office | 68 | ワコール、Loftwork、SMBCフレンド証券、不動産各社 等 | ○ persona(勤務先) |
| education | 11 | 大向保育園、映画美学校、資格の大原、グノーブル、伊藤塾 等(**大学・中高は無し**) | ○ persona(通学先) |
| attraction | 11 | d47 MUSEUM、東京アニメセンター、Parco Museum、ミヤシタパークサウス 等 | △ 目的地のみ |
| **hotel** | **8** | **セルリアンタワー、渋谷エクセルホテル東急、Tokyu Inn、The Millennials 渋谷、渋谷シティホテル、GRANDBEL HOTEL、ホテルインディゴ東京渋谷、capsule hotel et sauna** | **× 宿泊機能なし**(常時営業カテゴリ扱い+視認重みのみ) |
| leisure | 6 | 宮下公園、美竹公園、SHIBUYA CAST. GARDEN、エニタイムフィットネス、TIP.X、IMAOKA BOXING GYM | ○ scheduler(余暇) |
| cinema | **0** | — (v6では TOHOシネマズ/シネクイント等6件) | — |
| hall | **0** | — (v6では WWW/パルコ劇場/ヨシモト∞ホール等12件) | — |
| landmark | **0** | — (v6では忠犬ハチ公像等15件) | — |
| school | **0** | — (education と重複。v6/wideで青山学院・実践女子等) | — |

建物 `kind` 分布: house? 618 / generic 432 / retail 69 / office 33 / residential 15 / public 6 /
station 5 / hotel 3。名前付き建物389件にコア施設が揃う(渋谷ヒカリエ、渋谷スクランブルスクエア、
渋谷パルコ、渋谷マークシティEAST、渋谷ストリーム、渋谷フクラス、西武渋谷店A/B/ロフト館、
SHIBUYA 109、渋谷ソラスタ、Shibuya Sakura Stage、アベマタワーズ、セルリアンタワー、渋谷警察署 等)。

---

## 2. 現実の渋谷駅周辺(半径〜1km)のPOI構成

Web調査で得たおおよその実数感(2021〜2026年時点、出典は末尾)。

- **大型商業施設(コア)**: 渋谷スクランブルスクエア(2019、229m)、渋谷ヒカリエ(2012)、
  渋谷PARCO、レイヤードミヤシタパーク(2020)、渋谷ストリーム(2018、ホテル内包)、
  渋谷マークシティ、SHIBUYA109、渋谷フクラス(2019)、西武渋谷店、渋谷モディ、Bunkamura(改装休館中)。
  → **主要10前後**。
- **ハチ公・スクランブル交差点**: 忠犬ハチ公像、スクランブル交差点、モヤイ像(南口)。渋谷の象徴。
- **商店街・坂**: センター街、道玄坂、宮益坂、公園通り、スペイン坂、文化村通り、
  奥渋(神山町・富ヶ谷)、のんべい横丁、キャットストリート。
- **クラブ・ライブハウス**: 東京クラブマップに**「音箱やDJバー等100軒以上」**。主要箱=
  WOMB、Spotify O-EAST(キャパ1,300)/O-WEST/O-Crest/O-nest、clubasia、Sound Museum Vision、
  VISION、Contact(閉店)、WWW/WWW X、渋谷CLUB QUATTRO、TSUTAYA O-系。
- **映画館**: 少なくとも**9館** — TOHOシネマズ渋谷、Bunkamuraル・シネマ(渋谷宮下)、
  ヒューマントラストシネマ渋谷、シネクイント、ホワイトシネクイント(PARCO 8F)、渋谷HUMAXシネマ、
  ユーロスペース、シネマヴェーラ渋谷、シアター・イメージフォーラム。
- **ホテル(宿泊)**: JTB掲載で渋谷駅周辺**約23件**、渋谷区全体で**約30件**。代表=
  セルリアンタワー東急ホテル、渋谷ストリームホテル(旧 渋谷ストリームエクセルホテル東急)、
  渋谷エクセルホテル東急(マークシティ)、TRUNK(HOTEL)、渋谷東急REIホテル、渋谷東武ホテル、
  ホテルインディゴ東京渋谷、sequence MIYASHITA PARK、hotel koé tokyo 等。
- **神社**: 金王八幡宮(渋谷3丁目、渋谷警察署裏。区内有数)、宮益御嶽神社(宮益坂)、
  豐榮稲荷神社、千代田稲荷神社(道玄坂)、穏田神社(神宮前)。
- **公園**: 代々木公園(超大型、北西)、宮下公園(ミヤシタパーク)、北谷公園(神南)、美竹公園、
  神宮通公園、渋谷区立桜丘公園 等。
- **区役所・警察・消防・病院**: 渋谷区役所本庁舎(宇田川町15-1)、渋谷警察署(宇田川町)、
  渋谷消防署(渋谷1丁目)+松濤出張所、日本赤十字社医療センター/JR東京総合病院(いずれもコア外)。
  区内クリニックは多数。
- **学校**: 青山学院(大学/高等部/中等部/初等部)、実践女子学園、渋谷教育学園渋谷中学高校、
  區立神南小・鉢山中、國學院大學(渋谷4丁目)、専門学校(日本デザイナー学院・青山製図等)多数。
- **オフィス**: ビットバレーのIT集積。渋谷ソラスタ、Shibuya Sakura Stage、渋谷ストリーム、
  渋谷スクランブルスクエア(オフィス階)、アベマタワーズ(サイバーエージェント)、渋谷ヒカリエ、
  住友不動産渋谷ガーデンタワー 等。
- **飲食店密度**: 渋谷区全体で**約3,970事業所**(2021経済センサス、2016は4,294)。コア1km圏は
  その一部だが数百〜千規模。
- **コンビニ・カラオケ・ゲーセン**: コア圏にコンビニ数十軒、カラオケ十数店(ビッグエコー・
  歌広場・カラオケ館・パセラ・鉄人等)、ゲーセン数店(GiGO・タイトーステーション・adores等)。

---

## 3. 差分表(現実 vs 本番シミュ地図 `shibuya_osm.json`)

「シミュ内」=本番既定地図の件数。( )内は wide版(`shibuya_osm_wide_20250401.json`)の件数。

| カテゴリ | 現実のおおよその数・代表例 | シミュ内(本番/wide) | 過不足評価 | 追加推奨(優先度) |
|---|---|---|---|---|
| 大型商業施設 | 主要10(109/ヒカリエ/スクランブルスクエア/PARCO/ミヤシタ/マークシティ/ストリーム/フクラス/西武/モディ) | 建物として概ね全て有り | ◎ 妥当 | — |
| ハチ公/スクランブル交差点 | 象徴2〜3(ハチ公像・交差点・モヤイ像) | 交差点=ノード名有り、ハチ公=ノード名有りだが**像POI=0**(wide 24) | △ 像・モヤイのlandmark POI不足 | **忠犬ハチ公像・モヤイ像**(高) |
| 商店街・坂 | 8前後(センター街/道玄坂/宮益坂/公園通り/スペイン坂/文化村通り/奥渋/のんべい横丁) | ノード名6(宮益坂は「宮益坂下」のみ、奥渋・のんべい横丁無し) | △ 一部欠 | 宮益坂・奥渋・のんべい横丁(中) |
| クラブ・ライブハウス | 100軒以上、主要箱10+(WOMB/O-EAST系/VISION/clubasia/WWW) | nightlifeに混在。**WOMB=0**、O-EASTは建物のみ(POI無)、hall=0(wide 18) | ▲ 機能分類が弱い | **WOMB/O-EAST/VISION/clubasia**(高)、hall再分類(中) |
| 映画館 | 9館(TOHO/Bunkamura/ヒューマントラスト/シネクイント/HUMAX/ユーロスペース等) | **cinema=0**(TOHO等はservice誤分類)(wide 7) | ▲ 専用カテゴリ欠 | cinema化(中、wide採用で解決) |
| **宿泊施設(ホテル)** | **約23〜30**(セルリアン/ストリーム/エクセル東急/TRUNK/東急REI/東武/インディゴ/sequence) | **本番8 / wide 24。★機能は宿泊未実装** | ○ 数は妥当・**機能ゼロ** | **宿泊機能の実装+ TRUNK/ストリームホテル/東急REI補完**(最高) |
| 神社 | 5(金王八幡宮/御嶽/豐榮稲荷/千代田稲荷/穏田) | 本番3(御嶽・千代田稲荷・社務所)、**金王八幡宮=0**(wide 有) | △ 金王八幡宮欠 | **金王八幡宮**(高) |
| 公園 | 代々木公園/宮下/北谷/美竹/神宮通 | 本番: 宮下・美竹のみ、**代々木・北谷=0**(wide 有) | ▲ 大公園欠 | **代々木公園・北谷公園**(高) |
| 区役所 | 渋谷区役所本庁舎 | 本番=**美竹分庁舎のみ**(本庁舎無)、wide 有 | ▲ 中枢欠 | **渋谷区役所本庁舎**(高) |
| 警察署 | 渋谷警察署+交番数 | 建物「渋谷警察署」有+交番POI(渋谷駅前・道玄坂上) | ○ 妥当 | — |
| 消防署 | 渋谷消防署+松濤出張所 | 本番=**0**(wide 2) | ▲ 欠 | **渋谷消防署**(中) |
| 病院 | 日赤医療センター/JR東京総合病院(コア外)+クリニック多数 | 総合**病院=0**(本番/wide とも)、クリニックは有 | ▲ 総合病院欠 | 総合病院1〜2(中、防災シナリオ用) |
| 学校 | 青山学院/実践女子/渋教渋谷/國學院/区立小中/専門校多数 | 本番 education 11(塾・保育・専門のみ、**大学・中高=0**)、wide school 68 | ▲ 大学・中高欠 | wide採用 or **青山学院・実践女子・區立小中**(中) |
| オフィス | ソラスタ/サクラステージ/ストリーム/アベマタワーズ 等 | office POI 68 + office建物多数 | ◎ 妥当 | — |
| 飲食店 | 区全体約3,970(コア圏は数百〜千) | food 423 + nightlife 191 ≈ 600(wideで food 730) | ○ 1km圏として妥当 | — |
| コンビニ | コア圏数十軒 | shopに混在(専用cat無・粒度なし) | △ 粒度なし | convenience サブ分類(低) |
| カラオケ | 十数店 | nightlifeに混在(カラオケ館・ビッグエコー・歌広場・JOYSOUND 有) | ○ 実体は有 | — |
| ゲームセンター | 数店(GiGO/タイトー/adores) | ほぼ**欠落**(OSM amusement_arcade 未取得) | ▲ 欠 | ゲーセン2〜3(低) |

凡例: ◎良好 / ○妥当 / △一部不足 / ▲要改善。

---

## 4. 追加すべきPOIリスト(優先度順・シミュのデータ形式)

座標は原点=スクランブル交差点のローカルm。緯度経度も併記(build_map の LANDMARKS 追記 or 手動POI
補完に使える)。`node` は最寄り道路ノードを別途解決する前提(値は生成時に確定)。

> **命名の注意**: 本番地図は OSM 由来で実名(セルリアンタワー・青山学院 等)がそのまま入っている
> ため、下記も実名で提案する。ただし別途の「組織台帳」(`data/organizations_shibuya.json`)は
> 倫理制約 R17 により架空名のみ(`docs/research/shibuya-organizations.md`)。**地図POI(実名)と
> 組織台帳(架空名)でルールが異なる**点に留意。

### 優先度: 最高(次波の宿泊機能と直結)

宿泊機能そのものの実装が本丸。地図側の補完として、コアの主要ホテルを hotel カテゴリで揃える。

```json
{"name": "渋谷ストリームホテル", "cat": "hotel", "lat": 35.65695, "lon": 139.70320, "x": 233, "y": -281, "note": "渋谷ストリーム内。旧・渋谷ストリームエクセルホテル東急"}
{"name": "TRUNK(HOTEL)",        "cat": "hotel", "lat": 35.66780, "lon": 139.70640, "x": 523, "y": 917,  "note": "神南/キャットストリート寄り。ライフスタイル型"}
{"name": "渋谷東急REIホテル",    "cat": "hotel", "lat": 35.65760, "lon": 139.70360, "x": 269, "y": -210, "note": "桜丘寄り"}
```
(セルリアン・エクセル東急・Tokyu Inn・Millennials・シティホテル・GRANDBEL・インディゴ・カプセルは
本番地図に既存=**宿泊機能の割当先として即使える**)

### 優先度: 高(象徴・大公園・行政中枢・神社。本番bbox外で欠落=wide採用で一括解決)

```json
{"name": "忠犬ハチ公像",   "cat": "landmark", "lat": 35.65905, "lon": 139.70047, "x": -1,   "y": -50,  "note": "待ち合わせ名所。destinations に載る"}
{"name": "モヤイ像",       "cat": "landmark", "lat": 35.65760, "lon": 139.70090, "x": 25,   "y": -210, "note": "南口・待ち合わせ名所"}
{"name": "代々木公園",     "cat": "leisure",  "lat": 35.67170, "lon": 139.69490, "x": -517, "y": 1349, "note": "超大型公園(bbox拡張要)"}
{"name": "北谷公園",       "cat": "leisure",  "lat": 35.66270, "lon": 139.69870, "x": -174, "y": 354,  "note": "神南"}
{"name": "渋谷区役所本庁舎","cat": "service",  "lat": 35.66390, "lon": 139.69760, "x": -273, "y": 486,  "note": "行政中枢(本番は分庁舎のみ)"}
{"name": "金王八幡宮",     "cat": "landmark", "lat": 35.65530, "lon": 139.70720, "x": 595,  "y": -464, "note": "区内有数の神社。渋谷警察署裏"}
```

### 優先度: 中(夜遊び機能分類・消防・映画館・学校)

```json
{"name": "WOMB",            "cat": "nightlife", "lat": 35.65700, "lon": 139.69600, "x": -418, "y": -276, "note": "円山町の大箱クラブ"}
{"name": "Spotify O-EAST",  "cat": "hall",      "lat": 35.65550, "lon": 139.70750, "x": 622,  "y": -442, "note": "O-EASTビルは建物として既存=hall POIを付与"}
{"name": "SOUND MUSEUM VISION","cat":"nightlife","lat":35.65640,"lon":139.69620, "x": -400, "y": -342, "note": "道玄坂のクラブ"}
{"name": "渋谷消防署",      "cat": "service",   "lat": 35.66060, "lon": 139.70360, "x": 270,  "y": 122,  "note": "防災シナリオの拠点"}
{"name": "青山学院大学",    "cat": "school",    "lat": 35.66000, "lon": 139.71400, "x": 1210, "y": 55,   "note": "渋谷4丁目・青山寄り(bbox拡張要)"}
{"name": "実践女子学園",    "cat": "school",    "lat": 35.65540, "lon": 139.70900, "x": 758,  "y": -453, "note": "東2丁目"}
```
(cinema は本番地図の TOHOシネマズ/Cinemarise を `service`→`cinema` に再分類、または wide採用で自動解決)

### 優先度: 低(粒度向上)

- コンビニを `shop` から `convenience` サブ分類へ(コア数十軒。買い物・立ち寄りの粒度向上)。
- ゲームセンター(GiGO/タイトーステーション/adores 等)を `leisure` で2〜3件追加(OSM未取得ぶん)。
- のんべい横丁・奥渋(神山町)・宮益坂(全体)をノード名 or landmark として補完。

---

## 5. 実装アプローチの推奨(参考。実装は別途要ユーザー合意)

### Tier A(最小コスト・最大効果): 本番地図を wide 版へ差し替え

`conf/production.yaml` に `world.map: data/shibuya_osm_wide_20250401.json` を1行足すだけで、
以下が一括で入る(※本ドキュメントでは変更しない。提案のみ):
- hotel 24件(宿泊機能の割当先が3倍)、cinema 7、hall 18、landmark 24(ハチ公像含む)、school 68。
- 代々木公園・北谷公園・渋谷区役所本庁舎・金王八幡宮・青山学院・実践女子・渋谷消防署。
- 建物 7,210・住宅系 5,397(居住割当の現実味↑)。
- 座標原点はスクランブル交差点で全地図共通=**既存の座標・シナリオと整合**(ローカルmは不変)。
- 留意: ノード/建物増でメモリ・描画・経路計算コスト増。100日フル前に mock/≤24step スモークで確認推奨。

### Tier B(Tier A後も残る欠落を手動補完)

wide 地図にも無い: **WOMB・トランクホテル・総合病院・ゲームセンター**、
および O-EASTビルの hall 化。§4 の JSON 案を手動POIファイル(または build_map の LANDMARKS 追記)で補う。

### 宿泊機能(次波)の設計メモ

- 割当先は hotel カテゴリPOI(本番8 / wide 24)。`building` 紐付けがある hotel(セルリアンタワー等)は
  屋内フロア(floorguide)と接続すれば「チェックイン→客室滞在」を建物内活動として表現しやすい。
- 現状 `commerce.py` は hotel を「常時営業」として素通ししているだけ。宿泊は営業時間ではなく
  「予約・在庫(客室数)・チェックイン/アウト時刻・宿泊者の夜間滞在」という別モデルが要る
  (§ commerce の在庫モデルとは別軸)。訪問者/流入通勤者(persona v3 commuter)の一部を
  「宿泊visitor」に拡張する余地。

---

## 出典(URL)

- 渋谷の大型商業施設: 中古マンションなび渋谷区 — https://www.shibuyasenmon.com/column/241 /
  SHOPCOUNTER MAGAZINE — https://shopcounter.jp/magazine/area-guide/shibuya-commercial-facilities /
  東急 渋谷観光ガイド — https://www.tokyu.co.jp/area/shibuya/
- クラブ・ライブハウス(100軒以上): 東京クラブマップ — https://www.tokyo-club.net/shibuya/ /
  ライブガイドドッグ 渋谷ライブハウス一覧 — https://trend-dogman.com/shibuya-livemusicclub/ /
  LIVEHOUSENAVI(渋谷区キャパ一覧) — http://live-house.info/capacity/sibuyaku/
- 映画館一覧: 映画.com(渋谷) — https://eiga.com/theater/13/130301/ /
  NAVITIME 渋谷区の映画館 — https://www.navitime.co.jp/category/0106001/13113/
- ホテル数(約23〜30): JTB 渋谷駅周辺 — https://www.jtb.co.jp/kokunai-hotel/list/station/1130205/ /
  JTB 渋谷区 — https://www.jtb.co.jp/kokunai-hotel/list/13113/ /
  NAVITIME 渋谷区のホテル — https://www.navitime.co.jp/category/0608002/13113/
- 金王八幡宮ほか神社: 東京都神社庁 — http://www.tokyo-jinjacho.or.jp/shibuya/200222 /
  Wikipedia 金王八幡宮 — https://ja.wikipedia.org/wiki/金王八幡宮
- 区内警察・消防: 渋谷区ポータル — https://www.city.shibuya.tokyo.jp/kurashi/kurashi-joho/kankosho/policefire.html
- 飲食店数(約3,970事業所): GraphToChart 渋谷区飲食店数 — https://graphtochart.com/japan/shibuya-ku-no-of-eating-and-drinking-places.php /
  HOMEMATE 渋谷区市場調査 — https://www.homemate.co.jp/research/pr-tokyo/13113/
- カラオケ・ゲーセン: クレマップ 渋谷区ゲームセンター — https://cranegame-map.cgp-corp.co.jp/shibuyaku/
- POI原データ: OpenStreetMap contributors(ODbL) via Overpass API(`scripts/build_map.py`)

> 集計スクリプト(読み取り専用)は scratchpad に作成・実行(本リポジトリには残していない)。
> 本番地図の特定は `conf/config.yaml`(L76 `map: data/shibuya_osm.json`)と
> `conf/production.yaml`(world.map の上書き無し)による。
