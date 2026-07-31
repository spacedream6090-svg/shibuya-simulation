# data/snapshot/ — 「ある時点の現実」を凍結した静的データ(出所・ライセンス)

ユーザーの DT 定義(「ある時点の現実を切り取ってデジタル上に持ってくる。必ずしも現実と同期させる
必要はない」)に対応する凍結置き場。**シミュ本体はこのフォルダの静的ファイルしか読まない。
実行中の API 呼び出しは禁止**(`data/odpt/.gitkeep` と同じ大原則=決定論の保護)。

設計ノート: [docs/research/weather-generator-design.md](../../docs/research/weather-generator-design.md) /
背景調査: [docs/research/dt-snapshot-reproposal-notes.md](../../docs/research/dt-snapshot-reproposal-notes.md)

---

## `weather_tokyo_aug.json` — 東京の8月の日別実測(1996–2025・930日)

- **提供**: 気象庁
- **データセット**: 過去の気象データ検索「日ごとの値」(官署 = 東京 / prec_no 44 / block_no 47662)
  - 取得元: `https://www.data.jma.go.jp/stats/etrn/view/daily_s1.php?prec_no=44&block_no=47662&year=YYYY&month=M&day=&view=`
  - 別窓口(手動): <https://www.data.jma.go.jp/risk/obsdl/>
- **取得**: `scripts/fetch_weather_history.py`(2026-08-01・30要求・要求間隔1.5秒・欠測0日)
- **収録列**: 最高/最低/平均気温・降水量合計・平均/最小湿度・日照時間・平均風速・降雪・天気概況(昼/夜)

### ライセンス = 公共データ利用規約(第1.0版) / PDL 1.0

- 気象庁: 「コンテンツは、権利表記の記載がない限り**「公共データ利用規約(第1.0版)」に準拠した
  利用条件の下で、利用することができます**」 <https://www.jma.go.jp/jma/kishou/info/coment.html>
- 規約本体: <https://www.digital.go.jp/resources/open_data/public_data_license_v1.0>
- **CC BY 4.0 互換・商用可・複製/再配布/加工が可能**。→ **本リポジトリへのコミット可・公開ミラーへの同梱可**
  (商業施設サイトや渋谷区 HTML のような「私的利用を超える複製は事前許諾要」の制約は無い)。
- **出典明示は必須**。表示例: 「出典:気象庁ホームページ(https://www.data.jma.go.jp/stats/etrn/)」
- **加工した旨の明記が必要**: 本ファイルは HTML 表を機械的に抽出して JSON 化したもの
  (値そのものの補正・加工はしていない)。meta.source.modified_note に記載済み。

### 使う前に必ず読む注意

1. **渋谷区内に気象庁の気温観測点は存在しない**。「東京」は**北の丸公園**にあり渋谷駅から約 5.8km NE。
   都市キャノピー(スクランブル交差点)の実効気温より**系統的に低い**。本ファイルは生の観測値であり
   都市バイアス補正を**含まない**。
2. **観測点は 2014-12-02 に大手町から北の丸公園へ移転している**
   (<https://www.jma.go.jp/jma/kishou/know/kansoku/info/20141202_tokyo_rojo.html>)。
   移転前後で系列に不連続がある(報道ベースで年平均 約 −0.9℃・日最低 約 −1.4℃)。
   実測でも 1996–2014 の P(最高≥35℃)=7.6% に対し 2015–2025 は 23.5% と3倍。
   **30年を一括で使うと低温側へ引かれる**ので、較正の既定窓は移転後(2015–2025)にしてある。
3. 気象庁の掲載値は**過去に遡って修正されることがある**(取得日時は meta.fetched_at_utc)。
4. **日別値のみ**。時刻別気温・全天日射量・WBGT 実測は含まれない。

### 完全性の検査

```
python scripts/fetch_weather_history.py --verify     # スキーマ + payload_sha256
```

`meta.payload_sha256` は**取得日時を含まない観測ペイロードだけ**のハッシュなので、
同じ年月を取り直せば同じ値になる(= 取得の決定論を機械検査できる)。

---

## `weather_gen_params.json` — 確率的天候生成器の較正パラメータ

- **生成**: `scripts/fit_weather_gen.py`(上記の凍結実測のみが入力・ネットワーク不使用・**同入力→バイト同一**)
- **来歴**: `meta.source_payload_sha256` が `weather_tokyo_aug.json` の `meta.payload_sha256` と一致する
  (来歴の連鎖。`tests/test_weather_gen_offline.py` が機械検査)
- **中身**: 3状態マルコフ連鎖 / 状態別気温の平均・SD / Matalas 2変量 AR(1) の A・B / 年効果 /
  降水量ガンマ / 湿度回帰 / WBGT 係数 / 実測要約 / モンテカルロ自己検証 / **`validation.known_gaps`(未達の記録)**
- **ライセンス**: 上記 PDL 1.0 データからの派生。出典表示義務は引き継ぐ
  (`meta.source_attribution` に保持)。WBGT 推定式の出典は**小野雅司ら(2014)**・
  掲載元 環境省 熱中症予防情報サイト <https://www.wbgt.env.go.jp/wbgt_detail.php>。
- **限界**: 8月のみ較正。他月は未較正。詳細は
  [weather-generator-design.md §6](../../docs/research/weather-generator-design.md)。

```
python scripts/fit_weather_gen.py --verify           # payload_sha256
```
