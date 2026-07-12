# ODPT(公共交通オープンデータ)組込設計

作成日: 2026-07-07
対象: 渋谷駅に乗り入れる鉄道の実データを、決定論を壊さずシミュへ載せる設計。
関連スクリプト: `scripts/fetch_odpt.py`(オフライン取得 CLI)
出力先: `data/odpt/*.json`(静的キャッシュ)

> 方式の大原則: **オフライン取得 → 静的キャッシュ → シミュはキャッシュのみ読む**。
> シミュ実行中の API 呼び出しは**禁止**(ネットワーク I/O は再現性・決定論を壊す)。
> 本波は「設計まで」。実配線(loader 拡張・conf 追記)は次波で主エージェントが差配する。

---

## 0. 全体像

```
[事前・オフライン]                         [シミュ実行時・オンラインなし]
ODPT API v4 ──fetch_odpt.py──▶ data/odpt/*.json ──(次波の変換)──▶ 既存キャッシュ
(api.odpt.org)   ↑ ODPT_API_KEY            静的キャッシュ            (transit_shibuya.json 等)
                 環境変数のみ                                        │
                                                                    ▼
                                                       src/society/world/transit.py
                                                       (has_service / lines_in_service)
```

`fetch_odpt.py` は API から生の JSON-LD を取得して `data/odpt/` に保存するだけ。
シミュが読む形(定刻ダイヤ・駅位置・混雑曲線)への**変換は別ステップ**にして、
生キャッシュと派生キャッシュを分離する(再取得しても派生が勝手に変わらない=決定論)。

---

## (a) 取得できるデータの内訳

### API の形式(確認済み)
- ベース URL: `https://api.odpt.org/api/v4/`(v4, REST + JSON-LD、応答は JSON 配列)
- 認証: クエリ `acl:consumerKey=<TOKEN>`(トークンは環境変数 `ODPT_API_KEY`。**リポジトリに書かない**)
- フィルタ: `odpt:operator` / `odpt:railway` / `odpt:station` / `odpt:railDirection` / `odpt:calendar`、
  厳密一致は `owl:sameAs`。値・キー中のコロンは素で渡す(スクリプトは `urlencode(safe=":")` で保持)。
- 静的データ(路線・駅・時刻表)の**キャッシュ(取り込み)は利用規約上も許容**((d)参照)。

### 取得する 4 種別と主なフィールド
| 種別 | 主フィールド | 用途 |
|---|---|---|
| `odpt:Railway` | `owl:sameAs`, `dc:title`/`odpt:railwayTitle.ja`, `odpt:lineCode`, `odpt:color`, `odpt:stationOrder[]`(駅の並び=`odpt:station`,`odpt:index`) | 路線メタ・駅順・渋谷駅の特定 |
| `odpt:Station` | `owl:sameAs`, `dc:title`(駅名), `geo:lat`/`geo:long`, `odpt:stationCode`, `odpt:connectingRailway[]`, `odpt:exit[]` | 駅位置 → POI/地理反映、乗換 |
| `odpt:StationTimetable` | `odpt:station`, `odpt:railway`, `odpt:railDirection`, `odpt:calendar`(Weekday/SaturdayHoliday), `odpt:stationTimetableObject[]`(各便の `odpt:departureTime`,`odpt:destinationStation`,`odpt:trainType`) | **時刻帯別運行頻度・ラッシュ曲線の一次ソース** |
| `odpt:TrainTimetable`(任意 `--train-timetable`) | `odpt:railway`, `odpt:train`, `odpt:trainTimetableObject[]`(駅ごとの発着) | 列車単位の詳細ダイヤ(重い。当面は不要) |

### 対象路線(渋谷乗り入れ 9 路線)と ODPT 識別子
`fetch_odpt.py` の `TARGETS` に定義。既定 sameAs が空振りしたら operator 一覧の title 一致で自己修復する。

| key | 路線 | operator | Railway sameAs(既定) |
|---|---|---|---|
| jr_yamanote | JR山手線 | JR-East | `odpt.Railway:JR-East.Yamanote` |
| jr_saikyo | JR埼京線 | JR-East | `odpt.Railway:JR-East.SaikyoKawagoe` |
| jr_shonanshinjuku | JR湘南新宿ライン | JR-East | `odpt.Railway:JR-East.ShonanShinjuku` |
| tokyu_toyoko | 東急東横線 | Tokyu | `odpt.Railway:Tokyu.Toyoko` |
| tokyu_denentoshi | 東急田園都市線 | Tokyu | `odpt.Railway:Tokyu.DenEnToshi` |
| keio_inokashira | 京王井の頭線 | Keio | `odpt.Railway:Keio.Inokashira` |
| metro_ginza | 東京メトロ銀座線 | TokyoMetro | `odpt.Railway:TokyoMetro.Ginza` |
| metro_hanzomon | 東京メトロ半蔵門線 | TokyoMetro | `odpt.Railway:TokyoMetro.Hanzomon` |
| metro_fukutoshin | 東京メトロ副都心線 | TokyoMetro | `odpt.Railway:TokyoMetro.Fukutoshin` |

### 出力ファイル(`data/odpt/`)
路線ごとに 3(+1)ファイル + 索引。各ファイルは `{"_meta": {...出典・fetched_at・count...}, "data": [...]}`。
- `railway_<key>.json` / `stations_<key>.json` / `station_timetable_<key>.json` /(任意)`train_timetable_<key>.json`
- `_index.json`(全路線の件数サマリ・自己修復ノート)

### 提供状況の注意(2026-07-08 実測で確定)
- **オープン枠**(`https://api.odpt.org/api/v4/`・ODPT_API_KEY): 渋谷駅の `StationTimetable` は
  **東京メトロ3路線のみ**(各2件=平日+土休日)。東急・京王・JR は 0 件。
- **チャレンジ2026枠**(`https://api-challenge.odpt.org/api/v4/`・ODPT_CHALLENGE_API_KEY):
  参加者キーは通常エンドポイントでは **HTTP 403**(=専用エンドポイントのみ有効)。渋谷駅の
  `StationTimetable` が **東急東横・田園都市・京王井の頭で解放**(各2件)。**JR東日本は
  チャレンジ枠でも API 提供なし**(Station は主要8駅のみ・時刻表 0 件。時刻表は GTFS ファイル
  提供と公表 → `Transit._load_gtfs` の既存経路で別途対応可能)。メトロはチャレンジ側に無い
  (オープン枠で取得済みのキャッシュへフォールバック)。
- 取得キャッシュ: オープン枠= `data/odpt/`、チャレンジ枠= `data/odpt_challenge/`
  (**限定データは再配布不可の可能性 → .gitignore 済み・コミット禁止**)。
  `build_transit_odpt.py` はチャレンジ→オープンの順で探索し、0 件ファイルは次候補へ。
- JR 3路線(山手2方向・埼京)は `data/transit_shibuya.json` の近似ダイヤを維持し、
  他6路線を実データで置換する部分適用(source フィールドで実/近似と枠を区別)。

### 静的 GTFS(zip)の提供状況(2026-07-08 実測)
- URL パターン: `…/api/v4/files/{事業者}/data/{事業者}-Train-GTFS.zip?acl:consumerKey=…`。
  取得は `scripts/fetch_gtfs_odpt.py --operator <名> [--challenge]`(キーは環境変数から)。
- **実在確認**: TokyoMetro=オープン枠(1.1MB)・Keio=チャレンジ枠(0.6MB)。
- **JR東日本は未投入**: チャレンジ2026 の告知に「GTFS形式の時刻表データ」とあるが、
  カタログ(チャレンジ限定59データセットを悉皆確認)にも files/ にも API にも現物なし
  (JR東にあるのは運行情報 JSON と GTFS-RT Alert のみ)。チャレンジは 2026-07-01 開始
  直後なので期間中の投入が濃厚。**投入されたら**
  `python scripts/fetch_gtfs_odpt.py --operator JR-East --challenge` →
  `python scripts/build_transit_odpt.py` の2コマンドで山手(内/外)・埼京も実ダイヤ化される
  (build 側に GTFS フォールバックを実装済み。山手の内回り/外回りは trip_headsign の
  内回/外回キーワードで対応付け、特定不能なら近似のまま=捏造しない)。
- **相互検証**(駅時刻表 vs 静的GTFS・渋谷駅平日): 井の頭線・半蔵門線は**完全一致**。
  銀座線・副都心線は代表方面の選び方の差だけ(本数は一致)。GTFS 経路の正しさを実データで確認。

---

## (b) シミュへの写像案

### b-1. 時刻帯別運行頻度 → 世界側の transit サービス状態

**接続点(現状コード):**
- `src/society/world/transit.py:97` `Transit.has_service(sim_min)` — 運行中の路線があるか(退出/帰還ゲート)
- `src/society/world/transit.py:85` `Transit.lines_in_service(sim_min)` — `_first`/`_last`/`headway_min` から在線判定
- `src/society/world/transit.py:25` `_load_gtfs(gtfs_dir)` — GTFS(txt)→ 路線別 first/last/中央 headway を再構成する既存の実データ経路
- `src/society/engine/simulation.py:45` 付近 — `cfg.transit.file` と `cfg.transit.gtfs_dir` から `Transit` を構築
- `conf/config.yaml:276`–`278` — `transit.file`(既定ダイヤ)/ `transit.gtfs_dir`(実ダイヤ切替)
- 消費側: `src/society/cognition/routine.py:452`(就寝帰宅で駅へ), `src/society/engine/scheduler.py:492` と `:608`(終電後は帰れない)

**現状のダイヤ表現**(`data/transit_shibuya.json` の `lines[]`):
`{name, first "HH:MM", last "HH:MM"(24超可), headway_min}` を `_to_min` で `_first`/`_last` に展開。

**写像(推奨=既存スキーマへの変換):**
ODPT `StationTimetable`(渋谷駅・路線別・calendar 別)の `odpt:departureTime` 列から、
路線ごとに **始発 `first` = 最小発時刻・終電 `last` = 最大発時刻・`headway_min` = 発時刻差の中央値**を再構成する
(`_load_gtfs` と同じ流儀=フォーマット互換)。これで `transit_shibuya.json` を**同一スキーマのまま差し替え**でき、
`has_service`/`lines_in_service` はコード無改変で実データを読む。
- 変換は次波の別スクリプト(例 `scripts/build_transit.py`)で `data/odpt/station_timetable_*.json` →
  `data/transit_shibuya.json`(または `data/transit_shibuya_odpt.json`)を生成。`conf/config.yaml:277` の
  `transit.file` を差し替えれば適用(既存ファイルは温存)。
- **平日ダイヤを既定採用**(`odpt:calendar` = Weekday)。土日祝別ダイヤを使うなら `world.calendar`(config.yaml:129)と
  連動させる拡張は将来波。まずは平日一本で決定論を単純に保つ。

**より豊かな案(将来・任意):** 時刻帯別の**運行頻度テーブル**(1時間ごとの発本数)を持たせ、
`lines_in_service` を「在/不在」から「頻度」へ拡張。ただし現行 seam は在/不在で足りるため、
まずは first/last/headway 変換に留める(コード改変を最小化)。

**災害・運休との関係:** `src/society/disaster.py:234` が日次で `sim.transit.suspended` を立てる seam は
**そのまま**(実データ化と独立)。運休判定は決定論の新 stream `"disaster"` に閉じており、本写像は触れない。

### b-2. 駅位置 → POI/地理への反映

**接続点:** `sim.city.station_node`(`routine.py:452`, `scheduler.py:491`/`:607` が参照)、地図キャッシュ
`data/shibuya_osm*.json`(`conf/config.yaml:76` `world.map`)、地図ビルダ `scripts/build_map.py`。

**写像:** `odpt:Station` の `geo:lat`/`geo:long` と `dc:title`・`odpt:stationCode`・`odpt:exit[]` を使い、
- 渋谷駅ノード(`city.station_node`)の座標・出入口を実測値へ寄せる/検証する、
- 乗り入れ各線ホーム・改札を駅 POI として補強(既存 `data/floorguide_shibuya.json` の駅記述と突合)、
- `odpt:connectingRailway` を「渋谷駅=4社9路線ハブ」の乗換メタとして持つ。

反映は**地図ビルドの入力**として使う(オフライン)。実行時の地図キャッシュ(`shibuya_osm*.json`)は
これまで通り静的に読むだけで、実行中の座標解決に API は関与しない。

### b-3. 時刻表 → 通勤ラッシュの混雑度曲線

**接続点:**
- 流入通勤者の到着: `src/society/engine/scheduler.py:626`–`628`(`agent.commute` の翌朝 `arrival_min` 再流入)、
  同 `:89`–`90`(二峰分布の jitter は `arrival_min` に内包=決定論)
- 名簿・分布: `data/personas_100_inflow.json`、`data/shibuya_population.json` の inflow 節(出入口配分・到着二峰・沿線タグ)
- 混雑=不満の実効経路: `conf/config.yaml:86` `world.edge_capacity`(超過で減速)→ `conf/config.yaml:16`
  `factors.congestion_grievance`(混雑遅延→不満+)。混雑計上は `scheduler.py` の移動フェーズ occupancy。

**写像:** 渋谷駅 `StationTimetable` の発時刻を**1時間ビンで集計**し、時刻帯別の到着本数(=到着人流の重み)を作る。
これを「通勤ラッシュ曲線」とし、
- **到着分布のパラメータ化:** 流入通勤者の `arrival_min` 二峰(朝ピーク・夕ピーク)の山の位置・高さを、
  実ダイヤの高頻度帯へ合わせる(名簿ビルダ `scripts/build_personas.py` / 人口ビルダの入力として。オフライン)。
- **駅由来の人流パルス:** `transit.py` 冒頭が定義する役割(2)「到着ごとの人の波(パルス)」の強度を、
  時刻帯別頻度で重み付け(将来 seam)。

曲線は**名簿・分布の事前生成に使う**のが素直で、実行時の乱数消費・呼数を一切増やさない。
実行時に曲線から確率抽選する拡張を入れる場合は、必ず b-c(下記)の**新 stream** で引く。

---

## (c) 決定論の守り方

1. **実行中の API 呼び出し禁止。** シミュは `data/odpt/`(または派生した `data/transit_shibuya*.json`・
   `data/shibuya_osm*.json`)の**静的ファイルのみ**読む。`fetch_odpt.py` は事前の別プロセス。
2. **キャッシュ固定 + 設定でファイルパス指定。** 使うファイルは `conf/config.yaml` のパス
   (`world.map` / `transit.file` / `transit.gtfs_dir`)で明示。再取得しても、実験で使うファイルを
   config で固定している限り挙動は不変。**版はファイル名で分ける**(例 `transit_shibuya_odpt_20260707.json`)。
   再 fetch → 変換 → 新ファイル、を新しい config 値として扱い、**サイレントな上書き更新をしない**
   (`data/shibuya_osm_wide_20250401.json` 等の既存の日付付き命名と同じ流儀)。
3. **生キャッシュと派生を分離。** `data/odpt/*`(生)→ 変換スクリプト → シミュが読む形(派生)。
   変換は純関数(乱数なし)。`_load_gtfs`(transit.py:25)や既存ダイヤ JSON と**同一スキーマ**に落とし、
   `has_service`/`lines_in_service` を無改変で通す=ゴールデン(`golden_baseline_l1.json`)を壊さない。
4. **乱数が要るなら必ず hub の新 stream。** ラッシュ曲線からの到着抽選など確率を足す場合は、
   `sim.hub.stream("transit_odpt", agent.id, step)`(`src/society/rng.py:22`)のように**新しいストリーム名**で引く。
   既存 draw 順に割り込まない=既存条件・k 掃引の乱数消費を汚さない(災害層が `"disaster"` stream で
   既定ダイヤの draw を汚さないのと同型 / `src/society/disaster.py` 冒頭の R1 契約)。
   まずは**乱数ゼロ経路**(名簿・分布の事前生成に曲線を使う)を優先し、実行時抽選は必要になってから。
5. **静的性の担保。** ダイヤは「乱れなし=定刻」を維持(`transit.py` 冒頭・`transit_shibuya.json` の meta と一致)。
   遅延・運休は実データではなく `disaster` 層(config・新 stream)でのみ注入する。

---

## (d) ライセンス・出典表記の要件

**出典元:** 公共交通オープンデータセンター(ODPT, Public Transportation Open Data Center)/ 公共交通オープンデータ協議会。
API: `https://api.odpt.org/api/v4/` 。開発者サイト `https://developer.odpt.org/` 。

**要件(利用規約・API ガイドラインより):**
1. **出典表示義務。** 加工・提供物に出典(例:「本データは公共交通オープンデータセンターのデータを利用して作成」)を明記する。
   `fetch_odpt.py` は各出力ファイルの `_meta` と `_index.json`、stdout サマリに出典文を自動付与済み。
   派生ファイル(変換後ダイヤ・地図)にも同じ出典を継承させること。
2. **リアルタイム情報**(運行情報・列車ロケーション・GTFS-RT)を表示する場合は**データ生成時刻と出典の併記**が必要。
   本設計は**静的データ(路線・駅・時刻表)のみ**扱い、リアルタイムは取得しない → 決定論方針とも一致。
3. **静的データのキャッシュ(取り込み)は許容**(協議会の規約改定で取り込み禁止項目は削除)。よって
   `data/odpt/` への保存・変換は規約上問題なし。ただし出典表示は必須。
4. **トークンの秘匿。** consumerKey は第三者開示禁止。**コード・リポジトリ・ログ・成果物に埋め込まない**
   (環境変数 `ODPT_API_KEY` のみ、`.gitignore` は既に環境系を除外)。公開サンプルでは `acl:consumerKey=***` にマスク
   (`fetch_odpt.py` の表示・ログはマスク済み)。
5. **免責。** データの正確性・完全性は保証されない旨を保持(`_meta.disclaimer` に同梱)。
6. 商用・非商用の別、最新の禁止事項は**実運用前に規約原文を再確認**すること
   (`https://developer.odpt.org/` の利用規約・API ガイドライン)。

**参考(規約・仕様):**
- ODPT 概要 / 利用規約: https://www.odpt.org/ , https://developer.odpt.org/
- 従来チャレンジ側ガイドライン: https://developer-tokyochallenge.odpt.org/terms/api_guideline.html
- データカタログ(CKAN): https://ckan.odpt.org/
- v4 移行解説(参考): https://mikan.github.io/2022/03/31/migrate-odpt-api/

---

## 次波への引き継ぎ(実配線 TODO・本波では未実施)

1. `scripts/build_transit.py`(新規): `data/odpt/station_timetable_*.json` → `transit_shibuya` 互換ダイヤ
   (平日・路線別 first/last/headway)。JR が 0 件の路線は既定近似を残す。版は日付付き命名。
2. `conf/config.yaml:277` `transit.file` を生成ファイルへ差し替え(実験ごとに固定)。※本波は conf 変更禁止のため未実施。
3. 駅座標・出入口を `scripts/build_map.py` の入力に取り込み、`city.station_node` を実測へ寄せる。
4. ラッシュ曲線を `scripts/build_personas.py` / 人口分布ビルダの `arrival_min` 生成に反映(乱数ゼロ経路)。
5. 実行時抽選を足す場合のみ `hub.stream("transit_odpt", ...)` の新 stream を導入(既存 draw 順を汚さない)。
