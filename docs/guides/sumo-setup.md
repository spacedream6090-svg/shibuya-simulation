# SUMO 導入と v0 オフライン合成パイプライン(Windows)

`scripts/sumo_pipeline.py`(SUMO v0 = 車限定オフライン合成)を Windows 11 で動かすための
導入手順・実行例・設計(なぜ「本体無風=R1 安全」か)・v1 ライブ連成の go/no-go 基準をまとめる。

- 技術的下調べの原典: [`docs/research/sumo-integration-research.md`](../research/sumo-integration-research.md)
- 先例(本体無風・窓別 seed): `scripts/synth_crowd.py`
- 入力になる OD 行列: `scripts/analyze_od.py`(`runs/<name>/panel/od_matrix.parquet`)

> **大原則(R1 = 本体無風)**: `src/society`・`conf`・L1・ゴールデンバイト・既存 `tracks.json` を
> 一切触らない。SUMO は「事前オフライン合成 → 静的成果物を横置き」だけを行う。決定論(seed 再現)・
> LLM 呼数不変・Windows 11 を絶対制約とする。

---

## 1. 導入(3 経路)

現行安定版は **SUMO 1.27.1**(EPL-2.0)。決定論の担保のため **版は固定**して使う
(バージョン混在を避ける)。

### (A) pip(本パイプラインが自動で試す経路・最軽量)

```powershell
python -m pip install eclipse-sumo
```

- 実行ファイル一式(`netconvert` / `od2trips` / `duarouter` / `sumo` …)と、
  `SUMO_HOME`(= `.../site-packages/sumo`)・`tools/sumolib`・`data/typemap` を site-packages に置く。
- `import sumo; sumo.SUMO_HOME` で本体の場所が分かる。パイプラインはこれを自動検出する。
- **重要(Windows の落とし穴)**: pip は `<venv>/Scripts/netconvert.EXE` という **launcher shim** も置くが、
  この shim は同梱 DLL(`site-packages/sumo/bin` の 87 個)を解決できず即クラッシュする。
  **本パイプラインは `SUMO_HOME/bin/netconvert.exe`(本体 exe)を優先呼び出し、`bin` を PATH 先頭へ
  載せて DLL を解決する**(`find_bin` / `_sumo_env`)。手動で叩くときも `SUMO_HOME/bin` の exe を使うこと。

### (B) winget

```powershell
winget install --id EclipseFoundation.SUMO
```

- インストーラが環境変数 `SUMO_HOME` を設定する(Machine スコープ)。新しいシェルを開いてから使う。
- 公式版の sumolib は経緯度→net 座標変換に **pyproj が必要**(`pip install pyproj`。無いと
  demand 段で `Network does not provide geo-projection or pyproj not installed` エラー)。
  `rtree` は任意(無くても総当たりフォールバックで動く・遅いだけ)。
- 検証済み(2026-07-20): winget 版 1.27.1 で v0 全段(net→demand→run→convert)完走。
  pip 版の XML 読込クラッシュは公式バイナリでは発生しない。

### (C) MSI(公式インストーラ)

1. <https://sumo.dlr.de/docs/Downloads.php> から `sumo-win64-1.27.1.msi`(約190MB)を入手。
2. インストール時に `SUMO_HOME` が自動設定される(可搬 ZIP 版は手動設定)。

### 環境変数 `SUMO_HOME`

- pip 経路では **設定不要**(パイプラインが `sumo.SUMO_HOME` を自動検出)。
- winget/MSI/ZIP では `SUMO_HOME` を SUMO のルート(`bin` `tools` `data` を含む階層)に向ける。
  PowerShell(恒久設定):
  ```powershell
  [Environment]::SetEnvironmentVariable("SUMO_HOME", "C:\Program Files (x86)\Eclipse\Sumo", "User")
  ```

---

## 2. 実行例(stage 独立再実行可)

パイプラインは `synth_crowd` / `make_env` と同じ流儀で **stage ごとに独立再実行**できる。

```powershell
# 0) SUMO 導入の確認(無ければ pip install を試行→失敗なら本ガイドを案内して正直に終了)
python scripts/sumo_pipeline.py runs/demo_event_200a3d --stage check

# 1) 車道網: 生 OSM XML → netconvert(左側通行・車のみ・信号推定)
#    生 OSM XML が無いと「Overpass 再取得コマンド」を手順として出力する(勝手に大容量 DL しない)。
#    --fetch-osm を付けると道路+信号のみの軽量クエリで取得する。
python scripts/sumo_pipeline.py runs/demo_event_200a3d --stage net --fetch-osm

# 2) 需要: OD 行列 → TAZ + tazRelation → od2trips → duarouter
python scripts/sumo_pipeline.py runs/demo_event_200a3d --stage demand

# 3) 走行: sumo(CLI)で fcd(--fcd-output.geo=経緯度)を吐く
python scripts/sumo_pipeline.py runs/demo_event_200a3d --stage run --sumo-end 7200

# 4) 変換: fcd → local-m・10 分窓集約 → panel/sumo_traffic.parquet + _segs.json
python scripts/sumo_pipeline.py runs/demo_event_200a3d --stage convert

# まとめて(check→net→demand→run→convert)
python scripts/sumo_pipeline.py runs/demo_event_200a3d --stage all --fetch-osm
```

主なオプション:

| オプション | 既定 | 意味 |
|---|---|---|
| `--seed` | 42 | netconvert / od2trips / duarouter / sumo の全 seed(固定=再現) |
| `--district-m` | 100 | OD 地区セル辺長 m(`analyze_od` の `--district-m` と一致させる) |
| `--fetch-osm` | off | net 段で生 OSM XML を明示取得(道路+信号のみの軽量クエリ) |
| `--scale` | 1.0 | od2trips の需要スケール |
| `--sumo-end` | 86400 | sumo 終了秒(fcd を軽くしたいとき短縮) |
| `--fcd-period` | 10 | fcd 記録周期 s(小さいほど密で巨大) |
| `--taz-radius` | 120 | ゾーン重心→最寄り車道エッジの探索半径 m |
| `--taz-k` | 4 | 各ゾーンに割当てるエッジ数の上限 |

### 成果物

- `runs/<name>/sumo/<map>_road.osm.xml` … 生 OSM(道路+信号のみ・キャッシュ)
- `runs/<name>/sumo/<map>_car.net.xml` … 車道網(左側通行・信号推定)
- `runs/<name>/sumo/{taz.xml, od_tazrel.xml, trips.xml, routes.rou.xml, fcd.xml}` … 中間物
- `runs/<name>/panel/sumo_traffic.parquet` … (step, veh_id, x, y) 車両位置(local-m)
- `runs/<name>/panel/sumo_traffic_segs.json` … **tracks.json の traffic segs 互換**(各 step `{n, segs}`)
- `runs/<name>/panel/sumo_meta.json` … SUMO 版・seed・bbox・車両数などの来歴

いずれも `runs/`(= gitignore 済み)の下=**本体無風**(読み出しと横置き生成のみ)。
**元の `tracks.json` は変更しない**(ビューア統合は後続バッチ)。

---

## 3. 設計: なぜ「オフライン=シミュ本体無風(R1 安全)」か

`synth_crowd.py` と同型の「本体無風」パイプラインである。

- SUMO はビルド時に **1 回だけ**走らせ、成果物(車道網・経路・車両軌跡)を静的に置く。
  シミュ本体・`conf`・L1・ゴールデンバイトは一切実行時に絡まない。
- 入力は既存ランの **読み出しのみ**: `panel/od_matrix.parquet`(`analyze_od` 出力)と、ランが使った
  地図(`config.yaml` の `world.map`)のノード座標(域外ゲートウェイ重心)。
- 出力は **横置きの新規ファイル**(`runs/<name>/sumo/` と `panel/sumo_*`)。既存の `tracks.json`・
  L1・panel の既存成果物には触れない。→ ゴールデンバイトは完全に不変(R1 完全安全)。
- 決定論: netconvert / od2trips / duarouter / sumo すべて `--seed` 固定。後処理(10 分窓集約・
  parquet 書き)は自前の決定論ライタ(`compression="none"`・固定 version・ソート固定=`synth_crowd` と同法)。

### 座標整合(要点)

netconvert は OSM(経緯度)を **UTM へ投影 + オフセット**して車道網を作る(net ローカル系)。
シミュは地図原点(`meta.origin_latlon` ≒ スクランブル交差点 35.65950,139.70062)基準の局所接平面
(`scripts/build_map.project` と同一式)。両者は原点が違う。→ **fcd を `--fcd-output.geo`(経緯度)で
受け、シミュ側の経緯度→ローカル m 変換(`sumo_pipeline.project`)で座標を合わせる**。`netOffset` を
推測せず確実に重なる。TAZ 割当ても「ゾーン重心 local-m → 経緯度 → `sumolib.net.convertLonLat2XY`」で
net 座標へ写す。

### 誠実性(限界の明示)

- 信号は netconvert の **推定**(`--tls.guess-signals` 等)であり **実測現示ではない**。
- OD 行列は what-if 実験ログ由来で **渋谷の実測交通の再現ではない**。しかも `analyze_od` の OD は
  mode 非分離のため、v0 では **全トリップを車需要の代理**として展開する近似(この旨を `sumo_meta.json`
  に明記)。
- net の bbox 外に落ちるゾーン・OD ペアは捨て、落とした数を報告する(捏造しない)。
- SUMO 不在時は軌跡を **捏造せず**、本ガイド(pip/winget/MSI)を案内して正直に終了する。

---

## 4. Windows のトラブルシュート

### 4.1 `Quitting (on unknown error).`(XML 入出力での即クラッシュ)

`netconvert`/`sumo`/`duarouter`/`od2trips` が **XML ファイルを読む/書く瞬間**に、進捗を一切
出さず `Quitting (on unknown error).` で終了する(終了コード 1)ことがある。一方 `--version` /
`--help` / `--save-configuration` / 入力の無い `netgenerate --grid -o net.xml` は成功する。

- 症状の本質: **catch(...) で握られる非 std C++ 例外**(= Xerces / STL-locale 系)が、XML ファイル
  デバイス生成時に投げられる。オプション解析・本体ロードは正常で、**XML ファイル I/O だけ**が死ぬ。
- pip の launcher shim(`Scripts/*.EXE`)を叩くと DLL 解決失敗で別のクラッシュも起きる。
  → 本パイプラインは `SUMO_HOME/bin` の本体 exe を PATH 先頭で叩くので shim 問題は回避済み。
- 公式 FAQ が挙げる定番の是正は **Microsoft Visual C++ Redistributable の導入/修復**
  (<https://sumo.sourceforge.net/docs/FAQ.html>)。ただしこれは **システムインストーラ**であり、
  pip だけでは解決しない環境がある(VC++ 再頒布可能パッケージが導入済みでも XML I/O が死ぬ個体が実在)。
- **回避策の候補**(本パイプラインの制約外=手動対応):
  1. **MSI / winget で SUMO を導入**(pip wheel ではなく公式インストーラ版のバイナリを使う)。
  2. **VC++ 2015–2022 Redistributable(x64)を修復インストール**して再試行。
  3. 別 Windows 個体 / WSL / データセンター機(決勝 GPU 機)で net→demand→run を回し、成果物
     `runs/<name>/panel/sumo_*` を持ち込む(convert は純 Python なのでどこでも走る)。

### 4.2 cp932 コンソールでの文字化け・例外

日本語 Windows コンソール(cp932)対策として、パイプラインは `sys.stdout/stderr` を
`reconfigure(errors="replace")` する(`synth_crowd` と同修正)。SUMO サブプロセスの出力も
`encoding="utf-8", errors="replace"` で受ける。ファイル出力は常に UTF-8。

### 4.3 生 OSM XML の取得

`data/*.json`(コア地図)は **派生 JSON** で netconvert には使えない。生 OSM XML が必要:

```powershell
# SUMO 同梱(bbox は W,S,E,N の順に注意)
python "$env:SUMO_HOME/tools/osmGet.py" --bbox 139.6905,35.6505,139.7115,35.6685 --prefix road -d runs/<name>/sumo
# もしくは軽量 Overpass(道路+信号のみ)を本パイプラインに任せる
python scripts/sumo_pipeline.py runs/<name> --stage net --fetch-osm
```

---

## 5. v1 = ライブ連成(TraCI/libsumo)の go/no-go 基準

v0 が土台。v1(各 10 分 step で SUMO を 600s 進め、**辺別の所要時間倍率だけ**をシミュの車道グラフ
辺コストへ還流)は **新 RNG stream・新 conf knob・既定 OFF** の追加機能としてのみ検討する。
研究ドク([sumo-integration-research §5](../research/sumo-integration-research.md))の要約:

**GO(この順で全て満たす):**

1. **v0 が先に完成**(網・座標整合・OD 写像が検証済み)。
2. **決定論スモーク合格**: 同 seed で ≤24-step を 2 回 → 車道コスト系列と L1 が **byte 一致**。
3. **LLM 呼数不変の実証**: OFF/ON で LLM 呼数が完全一致(mock スモークで確認)。還流先は非 LLM の
   経路コストのみ(移動手段選択・目的地決定・会話は不変)なので原理的に不変。
4. **性能**: 24-step mock で追加 wall 時間が許容内(libsumo / `--mesosim` 前提で軽いはず)。
5. **価値**: 「SUMO 由来の渋滞遅延」が期待待ち近似より k*/観測に **意味ある差**を生む。

**NO-GO(v0 に留める):**

- (2)(3) のいずれかが byte で示せない / Windows で libsumo が不安定 / 還流のリアリズム向上が
  k* 観測を実質変えない。
- 決定論を壊す要因は厳禁: `--random` 禁止・`--device.rerouting.threads` × `--weights.random-factor`
  併用厳禁(スレッド並列ルーティングは非決定)。クロス OS byte 一致は保証しない(Windows 単機・
  車追従は既定 Krauss に寄せて **同一機 byte 再現**のみ主張)。
