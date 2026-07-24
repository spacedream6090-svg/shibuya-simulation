# 渋谷主要ビルの屋内間取り — Web公開情報リサーチ(B0、2026-07)

> 目的: 渋谷の主要ビルについて、**Web上の公開情報(公式フロアガイド)**から取れる実事実
> (階ごとの用途・店舗/区画数・EV/エスカレーター/トイレ等のアンカー設備)を収集し、
> シミュレーションの**決定論間取り生成(手続き生成)への制約データ**として
> `data/floor_layouts.json` を新規作成した。
>
> 制約: 本作業は調査+データ収集のみ。既存の `data/floorguide_shibuya.json` は変更していない
> (既存コンシューマ保護)。新ファイルは同一の `match` 規約・同一の `use` カテゴリ語彙を用いる。

---

## 0. 結論(先出し)

1. **21棟・197階**を収録(`data/floor_layouts.json`)。うち**79階**で公式ガイドの
   店舗/区画列挙から `shops`(生値)を取得できた。既存 `floorguide_shibuya.json` 収録9棟
   (スクランブルスクエア・ヒカリエ・109・マークシティ・ストリーム・パルコ・モディ・ミヤシタパーク・
   フクラス)に shops/zone_mix/anchors を追補し、未収録12棟(西武渋谷店・渋谷ロフト・cocoti・
   MAGNET by SHIBUYA109・サクラステージ・セルリアンタワー・渋谷キャスト・渋谷ソラスタ・
   SHIBUYA AXSH・SHIBUYA TSUTAYA(Q-FRONT)・ヒューマックスパビリオン・LINE CUBE SHIBUYA)を新規追加した。
2. **幾何(区画の実配置・寸法)は公開されていない**。公式フロアマップはほぼ全ビルで
   **画像/JavaScript描画**のため、区画のXY配置はもとより設備アイコン(EV/エスカレーター/階段/トイレ/
   案内)すらテキスト抽出できなかった。よって本ファイルは**「各階に何がいくつあるか」までの制約**に限定し、
   幾何配置は**手続き生成が担う**という分担を明示的に守っている(下記 §4 正直さ注記)。
3. **anchors(設備)は大半が欠測**。テキストで設備が読めたのは例外的に**渋谷マークシティ**
   (低層モール1〜5Fで ev/escalator/stairs/restroom/info を全取得)と**渋谷ヒカリエ B3F/2F**
   (info カウンターを本文記載で確認)のみ。他は「地図は存在するがアイコンを機械読取できない」ため
   `anchors` キー自体を省略した(=欠測は欠測のまま)。
4. **店名・ブランド名・企業名は JSON に一切入れていない**(ETHICS)。カテゴリ(`use`/`zone_mix`)と
   数(`shops`/`zone_mix`)と設備(`anchors`)のみ。出典URLは `meta.sources` と本ドキュメント §3 に記録。
5. **Bunkamura は現行世界の制約から除外**した。2023-04-10 から再開発で長期閉館中(再開 ~2029、
   機能はル・シネマ=渋谷宮下、シアターコクーン公演=THEATER MILANO-Za、ザ・ミュージアム/ギャラリー=
   ヒカリエへ一時移転)。閉館中ビルの旧間取りを「現行の制約」として入れると誤誘導になるため
   JSONには収録せず、本ドキュメントにのみ調査結果を残す(§3 参照)。
6. **渋谷駅**は `floorguide_shibuya.json` 側にホーム/改札のフロア構成があるが、屋内の
   店舗/区画(shops/zone_mix)という本ファイルの粒度に当てはまらないため `floor_layouts.json` には
   加えていない(重複回避)。

---

## 1. 調査方法

- **ツール**: WebSearch / WebFetch。各ビルの**公式サイトのフロアガイドを最優先**で取得し、
  各階の店舗リストが列挙されている場合はそれを数えて `shops` とした。公式が404/JS/TLS不達の場合のみ
  Wikipedia等の二次資料に切替え、URLを必ず記録した。
- **`use`(用途カテゴリ)**: `floorguide_shibuya.json` と同一の基本語彙
  `restaurant/fashion/beauty/lifestyle/food/office/observation/hall/theatre/hotel/station/park/bus` を優先。
  基本語彙で表せない実態のみ、追加語彙を最小限で使用した(§2)。
- **`shops`(店舗/区画数)**: 公式フロアガイドがその階のテナントを**列挙していて数えられる場合のみ**の
  生値。数えられない階はキー自体を省略。
- **`zone_mix`(区画のカテゴリ別内訳)**: カテゴリごとの区画数が**明確に判別できた階のみ**。
  合計は `shops` と一致するよう検証済み(スクリプトで全件チェック、不整合0)。
- **`anchors`(アンカー設備)**: 公式フロアマップに `ev/escalator/stairs/restroom/info` の
  記載が**確認できた設備のみ**。確認できない階は省略。
- **並列収集**: 棟を6グループに分け、各グループを独立に調査してから統合した。統合時に
  `use` 語彙・ETHICS(店名排除)・スキーマ整合を一元管理した。

### 出典の信頼度(重要)

- **公式・階別列挙(高信頼)**: ヒカリエ/ShinQs(B3〜5F, 6/7F)、パルコ(B1〜9F 全階列挙)、
  マークシティ(低層モール1〜4F)、渋谷ストリーム(1〜3F)、MAGNET(全階)、SHIBUYA TSUTAYA(全階)、
  SHIBUYA AXSH(1〜4F)、サクラステージ SHIBUYA SIDE(B2〜5F)。
- **公式+二次列挙(中信頼)**: 渋谷フクラス(公式フロアガイド構成 + skyskysky のテナント別列挙で階別数を補完。
  公式の「約69〜70テナント」総数と整合)。
- **二次列挙(参考値)**: スクランブルスクエア(公式は各階の総数を非公表。東急百貨店の食物販フロア
  ブランド数=B2/1F と、shibukei の階別列挙=2〜9F を採用。公式は「約120売場&ショップ」を掲げる一方、
  列挙合計は約180〜213となる**総数の表現差**があるため、本ファイルは各階の**列挙生値**を採用し参考値扱い)。
- **B2のみ確定(109)**: 公式フロアガイドが404、公式フロアマップは画像、店舗検索はJSで
  部分取得(合計~88/実121)に留まったため、確定できた階別数は **B2=10** のみ。総数121は
  Wikipedia。1〜8Fの `shops` は不確実として**省略**した。
- **数を記録しなかった(欠測)**: ミヤシタパーク(公式ガイドは列挙されるが免税カウンター等の
  ノイズ混入で整数が確定できず、正直に `shops` 省略)、西武渋谷店(百貨店ブランド数は要約読取の
  概算で確定不可のため省略、A館婦人/B館紳士・インテリア・宝飾を1棟に統合表現)、
  渋谷ロフト(単一業態=区画列挙ではなく部門構成のため `shops` 非該当)、cocoti(映画館7-8F・
  ジム9-11F・アパレル B1-1F が複数階にまたがりクリーンな階別数が取れず省略)。

---

## 2. 追加した `use` 語彙(基本語彙で表せなかった実態のみ)

| 追加語彙 | 意味 | 使用箇所(例) |
|---|---|---|
| `clinic` | 医療モール/クリニック/健診 | cocoti 5F(生殖医療)、サクラステージ 5F(歯科×3+内科)、SHIBUYA AXSH 4F(人間ドック) |
| `gym` | フィットネスクラブ | cocoti 9〜11F(ジム)、セルリアンタワー 3F(フィットネス+プール) |
| `school` | スクール/教室 | cocoti 6F(音楽教室) |
| `amusement` | カラオケ/ゲーム/アニメ系エンタメ | モディ 8F(カラオケ)、MAGNET B1・5F・7F、TSUTAYA 5F(カードゲームラウンジ)、ヒューマックス B1〜B2(カラオケ) |

- これら4語彙は `meta.note` にも列挙済み。
- **語彙で表せず収録を見送った実態(正直に)**: `parking`(各ビルの地下駐車場)、`residential`
  (キャスト13〜16F・サクラステージ上層の住宅/サービスアパートメント)、`gallery/museum`
  (AXSH 3Fのギャラリー〔2026開業予定〕、Bunkamura のザ・ミュージアム)、`bank`(金融カウンターは
  `office` に寄せた)。これらは基本+追加語彙のいずれにも当てはめず、該当階/棟を省略またはドキュメント注記に留めた。

---

## 3. カバレッジ表(棟 × 階数 × shops取得率 × 出典)

`shops率` = shops を取得できた階 / 収録階。★=既存 `floorguide_shibuya.json` 収録棟への追補。

| 棟 | 収録階 | shops取得階 | anchors取得階 | 主な出典 |
|---|---:|---:|---:|---|
| ★渋谷スクランブルスクエア | 21 | 10 | 0 | 公式 floor/ + 東急百貨店 foodshow_edge(二次: shibukei) |
| ★渋谷ヒカリエ / ShinQs | 15 | 10 | 2(info) | 公式 hikarie.jp/floorguide + tokyu-dept shinqs/floor |
| ★SHIBUYA109 | 10 | 1(B2のみ) | 0 | 公式 floor-map(画像)+ Wikipedia(総数121) |
| ★渋谷マークシティ | 7 | 4 | 5(全設備) | 公式 s-markcity floorguide(設備テキスト取得可の唯一棟) |
| ★渋谷ストリーム | 8 | 3 | 0 | 公式 shop/?floor + facilities |
| ★渋谷パルコ | 12 | 10 | 0 | 公式 floor/detail(全階テナント列挙) |
| ★渋谷モディ | 10 | 0 | 0 | 公式(JS不可)→ Wikipedia 階構成 |
| ★ミヤシタパーク | 4 | 0 | 0 | 公式 mitsui-shopping-park floorguide(数はノイズで省略) |
| ★渋谷フクラス / 東急プラザ渋谷 | 12 | 10 | 0 | 公式 floorguide + tokyu-plaza + skyskysky(階別列挙) |
| 西武渋谷店(A館+B館 統合) | 10 | 0 | 0 | 公式 sogo-seibu floor-guide(ブランド数は概算のため省略) |
| 渋谷ロフト | 7 | 0(非該当) | 0 | 公式 sogo-seibu floor-guide/loft(単一業態=部門構成) |
| cocoti SHIBUYA | 13 | 0 | 0 | 公式 cocoti.net floorguide/shops(複数階跨ぎで数省略) |
| MAGNET by SHIBUYA109 | 10 | 10 | 0 | 公式 magnetbyshibuya109.jp/floor(全階列挙) |
| SHIBUYAサクラステージ | 8 | 7 | 0 | 公式 shibuya-sakura-stage townmap_floorguide(SHIBUYA SIDE) |
| セルリアンタワー | 9 | 0 | 0 | 公式ホテル + Wikipedia(ホテル/オフィス/能楽堂=店舗列挙なし) |
| 渋谷キャスト | 3 | 0 | 0 | 公式 shibuyacast.jp/floor(商業5区画・階分け不可) |
| 渋谷ソラスタ | 6 | 0(非該当) | 0 | Wikipedia + skyskysky(純オフィス) |
| SHIBUYA AXSH | 5 | 4 | 0 | 公式 shibuya-axsh.jp/shop(1〜4F列挙) |
| SHIBUYA TSUTAYA(Q-FRONT) | 10 | 10 | 0 | 公式 shibuyatsutaya.tsite.jp/floor(全階) |
| ヒューマックスパビリオン | 12 | 0 | 0 | 公式 humax.co.jp(各階単一テナント=数は非該当) |
| LINE CUBE SHIBUYA(渋谷公会堂) | 5 | 0(非該当) | 0 | 公式 linecubeshibuya.com(単一ホール・全客席1,956席) |
| **合計** | **197** | **79** | **7** | — |

### 収録しなかったビルの調査メモ(正直な記録)

- **Bunkamura**(オーチャードホール2,150席 / シアターコクーン747席 / ル・シネマ 2スクリーン等):
  2023-04-10 から**再開発で長期閉館**(再開 ~2029)。機能は場外へ一時移転済み。旧間取りは
  Wikipedia に残るが、閉館中ビルを「現行世界の制約」として入れると誤誘導になるため
  **JSONには収録せず**、ここに記録のみ。出典: bunkamura.co.jp / ja.wikipedia.org/wiki/Bunkamura /
  prtimes 再開発リリース。

---

## 4. 正直さ注記(ETHICS・分担・限界)

1. **幾何(区画の実配置)は非公開=手続き生成の担当**。
   公式フロアガイドは「どのカテゴリの区画が何個あるか」までは分かるが、**各区画のXY位置・面積・
   通路形状は公開されていない**(フロアマップは画像/JS描画で、寸法つきの図面は非公表)。
   よって `floor_layouts.json` は**手続き生成への上位制約(各階の用途・区画数・接続設備)**に徹し、
   実際の区画レイアウトは決定論的手続き生成が矛盾なく埋める、という分担を明記する。
   このファイルは幾何を「与えない」ことがむしろ設計意図である。

2. **テナントは入替があり得る概略**。フロアガイドは調査時点(2026-07)のスナップショット。
   `shops`/`zone_mix` は「その時点で公式が列挙した区画数」であり、恒久的な確定値ではない。
   手続き生成の**分布制約(その階はおよそ何区画・どのカテゴリ比か)**として使う想定。

3. **店名・ブランド名・企業名を JSON に入れない理由(ETHICS)**。
   本プロジェクトの倫理制約(実在の個別事業者名を台帳化しない方針)に沿い、`floor_layouts.json` には
   **カテゴリと数と設備のみ**を収録し、`label` フィールド自体を設けていない。個別店舗名は出典URLを
   辿れば公式サイトで確認できるが、シミュ用データには持ち込まない。構造チェックスクリプトで
   「floors 内の全文字列が use語彙 / anchor語彙 / zone_mix キー(=use語彙)のいずれか」であることを
   全件検証済み(自由文字列は建物名 `match` 配列のみ)。

4. **anchors の欠測は「不在」ではない**。ほぼ全ビルでフロアマップが画像/JSのため設備アイコンを
   機械抽出できず、`anchors` を省略した。これは「その階にEV/トイレが無い」意味では**ない**
   (大型商業施設には当然存在する)。「公式マップ上のアイコン配置をテキストで確認できなかった」
   という取得限界を、捏造せず欠測として残した。設備アンカーを本気で埋めるには、各ビルの
   フロアマップ画像を目視(または画像対応の取得)で読む人手作業が必要。

5. **秘密情報の非記載**。APIキー・認証情報・非公開データは一切含まない。全出典は公開URL。

---

## 5. 取れなかったもの(まとめ)

- **全ビルの設備アイコン配置**(anchors)—— マークシティ全設備とヒカリエ2階分の info を除き欠測。
- **SHIBUYA109 の 1〜8F 階別店舗数**(確定は B2=10 のみ。総数121)。
- **スクランブルスクエアの公式階別総数**(非公表。二次列挙の参考値で代替、総数表現に差)。
- **ミヤシタパークの階別区画数**(公式列挙にノイズ混入で整数確定できず省略)。
- **西武渋谷店の階別ブランド数**(百貨店ゆえ概算のみ=省略。A館/B館を1棟に統合表現。M2F中2階は非整数階のため割愛)。
- **cocoti の複数階跨ぎテナントの階別内訳**(映画館7-8F・ジム9-11F・アパレルB1-1F)。
- **オフィス/ホテル/住宅の詳細**(区画列挙が公開されないため用途行のみ。住宅/駐車場は語彙外で省略)。
- **セルリアンタワー 17-18F の用途・38F の住宅/ホテル判別**(資料不一致)。

---

## 6. 出典URL(全リスト)

### 既存収録棟への追補
- スクランブルスクエア: https://www.shibuya-scramble-square.com/floor/ /
  https://www.tokyu-dept.co.jp/scsq/foodshow_edge/ /(二次)https://www.shibukei.com/column/43/
- ヒカリエ/ShinQs: https://www.hikarie.jp/floorguide/ / https://www.tokyu-dept.co.jp/shinqs/floor/
- SHIBUYA109: https://shibuya109.jp/floor-map/ / https://ja.wikipedia.org/wiki/109_(商業施設)
- 渋谷マークシティ: https://www.s-markcity.co.jp/floorguide/
- 渋谷ストリーム: https://shibuyastream.jp/shop/ / https://shibuyastream.jp/facilities/
- 渋谷パルコ: https://shibuya.parco.jp/floor/
- 渋谷モディ: https://www.0101.co.jp/721/ / https://ja.wikipedia.org/wiki/渋谷モディ
- ミヤシタパーク: https://mitsui-shopping-park.com/urban/miyashita/floorguide.html
- 渋谷フクラス/東急プラザ渋谷: https://www.shibuya-fukuras.jp/floorguide/ /
  https://www.tokyu-plaza.com/shibuya/shop/floor / https://skyskysky.net/construction/201924-2.html

### 新規追加棟
- 西武渋谷店: https://www.sogo-seibu.jp/shibuya/floor-guide/ / https://www.sogo-seibu.jp/shibuya/floor-guide/b
- 渋谷ロフト: https://www.sogo-seibu.jp/shibuya/floor-guide/loft
- cocoti SHIBUYA: https://www.cocoti.net/floorguide/ / https://www.cocoti.net/shops/
- MAGNET by SHIBUYA109: https://magnetbyshibuya109.jp/floor/
- SHIBUYAサクラステージ: https://www.shibuya-sakura-stage.com/townmap_floorguide/floorguide/
- セルリアンタワー: https://www.tokyuhotels.co.jp/cerulean-h/ / https://ja.wikipedia.org/wiki/セルリアンタワー /
  https://www.ceruleantower-noh.com/access/ / https://www.jzbrat.com/access/
- 渋谷キャスト: https://shibuyacast.jp/floor/ / https://ja.wikipedia.org/wiki/渋谷キャスト
- 渋谷ソラスタ: https://ja.wikipedia.org/wiki/渋谷ソラスタ / https://office.tokyu-land.co.jp/bldg/shibuya_sorasta/ /
  https://skyskysky.net/construction/201829.html
- SHIBUYA AXSH: https://www.shibuya-axsh.jp/shop/ / https://www.shibuya-axsh.jp/facilities/
- SHIBUYA TSUTAYA(Q-FRONT): https://shibuyatsutaya.tsite.jp/floor/
- ヒューマックスパビリオン: https://www.humax.co.jp/facility_p_shibuya_park/
- LINE CUBE SHIBUYA(渋谷公会堂): https://linecubeshibuya.com/facility

### 収録しなかったビル(記録のみ)
- Bunkamura: https://www.bunkamura.co.jp/ / https://ja.wikipedia.org/wiki/Bunkamura /
  https://prtimes.jp/main/html/rd/p/000000050.000031037.html

> 集計・検証スクリプト(読み取り専用)は scratchpad で実行し、本リポジトリには残していない。
> `data/floor_layouts.json` は `json.load` で読込可能・zone_mix合計=shops を全件検証済み・
> floors内の自由文字列は建物名 `match` のみ(店名なし)を確認済み。
