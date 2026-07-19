# SUMO 車限定統合の技術調査(第37バッチ Track S2 / SUMO-R)

作成日: 2026-07-19
体制: Opus Webリサーチ(コード変更なし・本ファイル1本のみ)
対象: 渋谷LLM社会シミュに **車のみ** の SUMO(Eclipse SUMO)を統合する技術的下調べ。
関連計画: [batch37.md](../plans/batch37.md) Track S2(b) / [traffic-signals-audit](traffic-signals-audit.md)
先例(読み取り専用で参照): `scripts/synth_crowd.py`(本体無風・窓別seed・平均移動時間保存)
                          `scripts/analyze_od.py`(L1読み出しのゲートウェイOD行列)

> **大原則(R1 = 本体無風)**: シミュ本体(src/society・conf・L1・ゴールデンバイト)を一切
> 触らない。SUMO は「事前オフライン合成 → 静的成果物をビューアが読む」を基本形とし、
> ライブ連成(TraCI)は **新stream・既定OFF** の追加機能としてのみ検討する。決定論
> (seed再現)・LLM呼数不変・Windows 11 を絶対制約とする。

---

## 0. 要約(TL;DR)

- **導入**: 現行安定版 **SUMO 1.27.1**(EPL-2.0)。Windows は MSI / ZIP / `winget` / `pip`
  の4系統で導入可。Python ツール(netconvert・duarouter・od2trips・sumolib・traci・libsumo)
  は同梱 or PyPI。決定論は既定(Mersenne Twister・既定seed 23423・`--seed` で固定)。
- **OSM→網**: `netconvert` で車道のみ抽出可(`--keep-edges.by-vclass passenger` または
  `--remove-edges.by-vclass ...`)。**日本は左側通行 → `--lefthand` 必須**。信号は
  `--tls.guess-signals` 等で自動推定。
- **需要**: 本シミュの `analyze_od.py` が出すゲートウェイOD(hour_bin別)を **TAZ + OD行列**
  に写して `od2trips → duarouter` で経路化。データが無い時は `randomTrips.py` が代替。
- **オフライン(v0)**: `sumo --fcd-output fcd.parquet`(**1.24以降 Parquet/CSV直書き可**)で
  車両軌跡を吐き、10分窓へ集約してビューア用トラックにする。`--seed` 固定で同一機・同一版なら
  再現。**これが推奨の第一形**。synth_crowd と同型の「本体無風」パターン。
- **ライブ連成(v1)**: `traci`/`libsumo` で 1 sim-step(=600s)ごとに SUMO を 600 SUMO秒
  進め、**辺別の混雑(所要時間倍率)だけをシミュに還流**する。還流先は非LLMの経路コストのみ
  なので **LLM呼数は不変**。決定論は「SUMOの`--seed`固定 × こちらのTraCIコマンド列が
  シミュ状態の純関数」で担保できるが、**外部プロセス連成=再現性の面積が広がる** ため
  新stream・既定OFF・byte一致スモークで go/no-go を判定する。
- **先行事例**: SUMO+JADE(ABM連成の古典)、**MobiVerse / AgentSUMO(LLM×SUMO・2026)**、
  外部歩行者モデル連成など。いずれも TraCI が結合面。MATSim は活動ベース需要を内蔵する
  大規模指向で、SUMO は微視挙動が精密。本件は「車の微視描写」目的なので SUMO が適。

---

## 1. SUMO の Windows 導入

### 要点
- **現行安定版**: **SUMO 1.27.1**(2026-06-25 リリース)。開発は継続中で、最新機能が要れば
  GitHub の `main` をソースから使う選択もある。
- **ライセンス**: **EPL-2.0**(第二ライセンスとして GPLv2)。標準 Windows ビルドは Eclipse 承認
  ライセンスのコードのみ(GPL コード非同梱)。GeoTIFF/シェープファイル対応が要る場合のみ
  `-extra` 版(GPL コード同梱)を使う。**車限定のオフライン/ライブ連成では通常版で十分**。
- **Windows インストール4系統**:
  1. **MSI**: `sumo-win64-1.27.1.msi`(約190MB)。インストーラが環境変数 `SUMO_HOME` を設定。
  2. **ZIP**(可搬): `sumo-win64-1.27.1.zip`(約170MB)。手動で `SUMO_HOME` を設定。
  3. **winget**: `winget install --name sumo`。
  4. **pip(PyPI・1.8.0以降)**: 
     - `pip install eclipse-sumo`(実行ファイル一式)
     - `pip install traci` / `pip install libsumo` / `pip install sumolib`(個別ライブラリ)
- **Python 要件**: アプリ群は Python 2/3 対応、**libsumo は Python 3.9+**。Windows で libsumo を
  使う場合は **OpenJDK 21.0.5 以上を強く推奨**(libsumo 1.22.0 以降・旧版は原因不明のクラッシュ報告)。
- **同梱ツール**: `netconvert`・`duarouter`・`od2trips`・`polyconvert`・`sumo`/`sumo-gui`、および
  `$SUMO_HOME/tools/` 配下の Python スクリプト(`randomTrips.py`・`osmGet.py`・`edgesInDistricts.py`
  等)と `sumolib`/`traci` パッケージ。Python から `sumolib`/`traci` を import するには
  **`SUMO_HOME` を設定**(または `pip` 版を使用)。

### 本件への含意
- **推奨導入**: 開発機は **MSI(SUMO_HOME 自動設定)** + venv に `pip install eclipse-sumo sumolib traci libsumo`。
  版を **1.27.1 に固定**(決定論=同一版前提のため、バージョン混在を避ける)。
- ライセンス上の縛りは緩い(EPL)。成果物(net/rou/fcd)は本リポジトリの `data/` 系に静的キャッシュ
  として置く方針が gitignore の掟と整合(生成物は commit しない)。

### 出典
- Downloads(版・MSI/ZIP/winget/pip・EPL・Python要件): https://sumo.dlr.de/docs/Downloads.php
- 公式サイト: https://eclipse.dev/sumo/
- ソース(GitHub): https://github.com/eclipse-sumo/sumo
- ドキュメント目次: https://sumo.dlr.de/docs/index.html

---

## 2. OSM → SUMO 車道網(netconvert)

### 要点
- **入力形式**: `netconvert` は **OSM XML(`.osm` / `.osm.xml`)** を読む。本リポジトリの
  `data/shibuya_osm.json` は**シミュ用の派生JSON**なので netconvert には直接は使えない。
  **生OSM XML** を別途用意する(SUMO 同梱の `osmGet.py --bbox <同じ約1km bbox>` で1回だけ取得、
  または既存の生OSM取得を XML に変換)。**派生JSONもシミュ本体も無風のまま**、SUMO 用の生OSMを
  横に持つのが疎結合。
- **車のみ抽出(2通り・どちらも公式)**:
  - `--keep-edges.by-vclass passenger` … 乗用車が使える辺だけ残す(最も素直な「車のみ」)。
  - `--remove-edges.by-vclass rail_slow,rail_fast,bicycle,pedestrian` … 鉄道・自転車・歩行者辺を除去。
  - 併せて **歩道生成をしない**(`--sidewalks.guess` を付けない)・歩行者用 typemap を読み込まない。
- **左側通行(日本)**: 既定は右側通行前提。**`--lefthand` を必ず付ける**(交差点内の車線接続・
  合流の左右が変わる)。付け忘れると右側通行の網になる。
- **信号の自動推定**: OSM の `highway=traffic_signals` ノードを交差点の信号へ束ねる。推奨セット:
  - `--tls.guess-signals`(OSM の信号ノードを交差点TLSの一部として解釈)
  - `--tls.join`(近接交差点の信号を1つの制御へ統合)
  - `--tls.discard-simple`(車線の少ない些末な信号を捨てる)
  - `--tls.default-type actuated`(感応式。定周期 `static` より現実の待ちに近い)
  - 交差点そのものの信号有無を推定するなら `--tls.guess`(流入車線数などから推定)も併用可。
- **交差点・幾何の整形(OSM 由来ノイズ対策)**:
  - `--junctions.join`(OSM が並行エッジで表す大交差点を1ノードに統合)
  - `--geometry.remove`(トポロジを変えずに冗長頂点を削除=網が軽くなる)
  - `--ramps.guess`(加減速レーンの推定)
  - `--roundabouts.guess`(環状交差点推定)
- **typemap**: `--type-files $SUMO_HOME/data/typemap/osmNetconvert.typ.xml`(道路の既定属性)。
  歩行者用 `osmNetconvertPedestrians.typ.xml` は**読み込まない**(車限定のため)。

### 推奨コマンド(車のみ・左側通行・信号推定)
```bash
netconvert \
  --osm-files shibuya_raw.osm.xml -o data/sumo/shibuya_car.net.xml \
  --type-files "$SUMO_HOME/data/typemap/osmNetconvert.typ.xml" \
  --lefthand \
  --keep-edges.by-vclass passenger \
  --tls.guess-signals --tls.join --tls.discard-simple --tls.default-type actuated \
  --junctions.join --geometry.remove --ramps.guess --roundabouts.guess \
  --no-turnarounds true \
  --output.street-names true
```

### 本件への含意 / 注意
- **座標系の整合が要点**: netconvert は OSM(経緯度)を **メートル網へ投影 + オフセット(`netOffset`)**
  して出力する。SUMO の車両座標は「その網ローカル系」。シミュは渋谷中心のローカルm系
  (`data/shibuya_osm.json` を作った変換)を使うため、両者の原点が違う。**解決策**: fcd/TraCI 出力で
  `--fcd-output.geo`(経緯度)にして受け取り、**シミュ側の経緯度→ローカルm変換で座標合わせ**する。
  こうすれば `netOffset` を推測せず確実に重なる。
- 信号推定は「近似」であること(現示・オフセットの実測ではない)を成果物に明記する
  = traffic-signals-audit の誠実性方針を継承。

### 出典
- OSM 取込み(車限定・vclass 除去/保持・左側通行・信号推定): https://sumo.dlr.de/docs/Networks/Import/OpenStreetMap.html
- netconvert オプション全般: https://sumo.dlr.de/docs/netconvert.html
- OSM 取込みチュートリアル: https://sumo.dlr.de/docs/Tutorials/Import_from_OpenStreetMap.html

---

## 3. 需要生成(ゲートウェイOD → 経路)

### 要点
- **OD 行列方式(本命)**: `od2trips` が **OD行列 + TAZ(交通ゾーン)** をトリップ列に変換 →
  `duarouter` が網上の経路(`.rou.xml`)を生成。
  ```bash
  od2trips -n data/sumo/shibuya_car.net.xml -d shibuya.od -o shibuya.trips.xml \
           --taz-files shibuya.taz.xml --scale 1.0
  duarouter -n data/sumo/shibuya_car.net.xml -r shibuya.trips.xml -o data/sumo/shibuya.rou.xml
  ```
- **TAZ の作り方**: 
  - 各ゾーンを「源/汇となる辺集合」で定義した XML(`<taz id=".." edges="e1 e2 .."/>`)。
  - 100m 地区セルなどのポリゴンから **`edgesInDistricts.py`** で辺をゾーンに自動割当できる。
- **OD 行列フォーマット(3種)**: `tazRelation`(XML・`<tazRelation from=".." to=".." count=".."/>`
  を時間 `interval` で束ねる)/ VISUM の V-format / O-format。**時間帯別**は `interval` を
  複数並べる(または `--timeline`)。
- **代替: `randomTrips.py`**(OD が無い/粗い時)。網から source/dest 辺を確率サンプルして
  トリップ生成。主オプション:
  - `-n <net>` / `-o <trips>` / `-b`,`-e`(開始/終了秒・既定0–3600)/ `-p`(挿入間隔秒=発生率)
  - `--fringe-factor`(網の縁=流入出を重み付け。`max` で全交通を縁から)
  - `--vehicle-class passenger`(vType 自動生成)/ `--validate`(経路不能トリップを除去)
  - `--route-file <rou>`(裏で duarouter を呼び経路まで生成)/ **`--seed <INT>`(再現)**

### 本シミュのゲートウェイODの流用設計
`analyze_od.py` は既に **(origin, dest, hour_bin, purpose, trips)** を出す(L1読み出し専用)。
これを SUMO 需要へ写す:
1. **ゾーン対応**:
   - 域外ゲートウェイ `G:<node>`(流入出)→ **網の縁(fringe)辺**に紐づく TAZ。
   - 域内 100m 地区セル `D:cx:cy` → その矩形に入る辺群の TAZ(`edgesInDistricts.py`)。
2. **時間帯**: `hour_bin`(0–23)を SUMO の `interval`(各3600s)に写す。
   1日=144step・1step=600s の粒度は SUMO 側では秒時刻に展開。
3. **車のみ**: `purpose`/`mode` は使わず、**車トリップ(agent の car + 背景 Poisson 車)** の
   OD だけを対象にする(歩行・自転車・電車は除外)。
4. **決定論**: `od2trips`/`duarouter`/`randomTrips` すべて `--seed` 固定で再現。

### 誠実性
- OD 行列は **what-if 実験ログ由来**(渋谷の実測交通量ではない)。SUMO はその需要を「もっともらしく
  微視展開」するだけで、**実測交通の再現ではない**ことを成果物に明記(analyze_od の注記を継承)。

### 出典
- OD 行列取込み(od2trips・TAZ・行列フォーマット・duarouter 連携): https://sumo.dlr.de/docs/Demand/Importing_O/D_Matrices.html
- randomTrips.py(ランダム需要・--seed・--route-file・--fringe-factor): https://sumo.dlr.de/docs/Tools/Trip.html

---

## 4. オフライン方式(fcd-output → 10分集約 → 決定論)

### 要点
- **軌跡出力 `--fcd-output`**: 各シミュ秒(または `--device.fcd.period` 指定周期)ごとに全車両の
  位置・速度を吐く「フローティングカーデータ」。既定 XML 形式:
  ```xml
  <fcd-export>
    <timestep time="T">
      <vehicle id=".." x=".." y=".." angle=".." type=".." speed=".."/>
    </timestep>
  </fcd-export>
  ```
  既定属性は **id, x, y, angle, type, speed**(任意で pos, lane, slope, acceleration 等)。
- **Parquet/CSV 直書き(1.24 以降・実験的)**: 出力ファイルの拡張子で分岐。
  - `sumo -c my.sumocfg --fcd-output fcd.parquet` → **Parquet**
  - `sumo -c my.sumocfg --fcd-output fcd.csv` → CSV(区切りは `--output.column-separator`)
  - 拡張子から判別できない時は `--output.format`。Parquet 圧縮は `--output.compression`(gzip/bz2/zstd)。
  - **Parquet は pandas 読み込みで XML の約50倍速・ファイルも小さい**。本シミュの panel が既に
    Parquet 中心なので相性が良い(synth_crowd の `crowd_tracks.parquet` と同流)。
- **出力周期の制御**: `--device.fcd.period <T>`(全体周期)・`--device.fcd.begin <T>`(暖機の
  スキップ)・`--device.fcd.probability`(車両サンプリング率)。**既定は毎ステップ**。
- **地理座標**: `--fcd-output.geo`(経緯度=WGS84)・`--fcd-output.utm`。→ §2 の座標整合に使う。
- **決定論**: `sumo --seed <INT>` 固定で、**同一版・同一入力・同一引数**なら結果は再現
  (Mersenne Twister・既定seed 23423)。ただし**プラットフォーム差の落とし穴**あり(§5 参照)。
  Windows 単機・版固定なら実務上問題ない。

### 10分粒度への集約設計(本シミュ向け)
SUMO は秒(or 周期)刻み、本シミュは **1 step = 600s**。オフライン成果物は用途で2系統:
- **(A) ビューア用車両トラック**(batch37 の第一目標): fcd を読み、各車の (t, lon/lat→ローカルm, speed)
  を **ビューアの必要レートに間引き**、`runs/<name>/panel/vehicle_tracks.parquet` 等に保存。
  synth_crowd の `crowd_tracks.parquet`(window, t_s, agent_id, x, y)と同型スキーマにできる。
- **(B) 辺別・窓別の混雑統計**(v1 の布石にも): fcd(または `--edgedata`/`--summary`)を
  600s 窓へビン化し、辺ごとの **平均速度・通過台数・所要時間** を出す。これが「平均移動時間を保存」
  する synth_crowd の思想の車版(窓別の実効速度を保存)。
- **決定論の担保**: SUMO ラン自体が seed 固定で決定論。**後処理(集約・parquet書き)は自前の
  決定論ライタ**で書く(synth_crowd 同様 `compression="none"`・固定 version・ソート固定)と
  byte 一致まで狙える。SUMO の Parquet 直書きは実験的(データ欠損の注意書きあり)なので、
  **中間は XML/CSV で受けて自前 Parquet に整形**する方が byte 決定論は堅い。

### 成果物(v0)
- `data/sumo/shibuya_car.net.xml`(車道網・生成物)
- `data/sumo/shibuya.rou.xml`(需要=経路)
- `runs/<name>/panel/vehicle_tracks.parquet`(ビューア用トラック)
- `runs/<name>/vehicle_demo.html` 等(自己完結ビューア・任意)
- いずれも **シミュ本体・L1・ゴールデン無風**(読み出しと横置き生成のみ)。

### 出典
- FCDOutput(属性・period/begin/probability・geo/utm): https://sumo.dlr.de/docs/Simulation/Output/FCDOutput.html
- Tabular Outputs(1.24以降 CSV/Parquet 直書き・--output.format・50倍速): https://sumo.dlr.de/docs/TabularOutputs.html
- Randomness(既定seed 23423・--seed・--random・再現条件): https://sumo.dlr.de/docs/Simulation/Randomness.html
- 出力全般の目次: https://sumo.dlr.de/docs/Simulation/Output/index.html

---

## 5. ライブ連成(TraCI / libsumo)

### 5.1 ステップ同期の作法
- **接続と制御**: `traci.start([...])` が SUMO をサブプロセス起動しソケット接続(または
  `--remote-port` で先に起動したサーバに接続)。`traci.simulationStep()` を呼ぶと
  **SUMO が 1 ステップ進む**。全クライアントが `simulationStep` を呼ぶまで次に進まない
  (同期式=ブロッキング)。データは各ステップ間に取得。終了は `traci.close()`。
- **ステップ長**: `--step-length` の**既定は 1.0 秒**(0.001〜1.0 で可変)。`simulationStep(t)` に
  目標時刻(秒)を渡すとその時刻まで一括で進めることもできる。
- **高速化**: 
  - **libsumo(インプロセス C++ ライブラリ)** はソケット通信のオーバーヘッドが無く TraCI より
    大幅に速い。移行は `import libsumo as traci` か環境変数 `LIBSUMO_AS_TRACI` だけ。
  - libsumo の制約: **複数クライアント接続不可**、一部サブスクリプション非対応、型チェックが厳格、
    `sumo-gui` は Windows で不可。Windows は **OpenJDK 21.0.5+ 推奨**(旧版クラッシュ)。
  - TraCI 側でも **サブスクリプション**(必要属性を予約取得)で取得を約半減できる(例: 90s→42s)。

### 5.2 時間スケール整合(1 SUMO秒 vs シミュ10分)
- 1 sim-step = 600s。**案A(素直)**: 各 sim-step で `simulationStep()` を **600回(step-length=1s)**
  または `--step-length 2〜10` にして 60〜300 回呼び、SUMO を 600 秒進める。
- **案B(高速)**: **メゾスコピック(`--mesosim`)** で走らせる。1km・数百台なら微視でも軽いが、
  メゾなら辺の所要時間だけ精度良く・桁違いに速い。ライブ還流が「辺別所要時間」なら案Bで十分。
- **案C(疎結合)**: SUMO を毎 sim-step ではなく **数 step に1回だけ 600s 進め**、混雑場を保持。
  精度と速度のトレードオフ。

### 5.3 シミュ側への情報還流(LLM呼数不変が絶対条件)
- **還流する情報**: 各 600s 窓の末尾で SUMO から **辺別の混雑指標**を読む
  (`traci.edge.getTraveltime` / `getLastStepMeanSpeed` / `getLastStepVehicleNumber`)→
  自由流に対する **所要時間倍率(渋滞レベル)** を辺ごとに算出。
- **還流先**: シミュの車道グラフ A* の **辺コスト(所要時間)** に掛ける。現在の
  「信号=期待待ち近似」を **SUMO 由来の実遅延**で置換/上乗せする。
- **なぜ LLM 呼数が変わらないか**: 経路探索・移動手段選択(`routine.py` の距離閾値×保有確率)は
  **非LLM の決定論ロジック**。SUMO は「移動の**所要時間/到着step**」だけを変え、
  **エージェントの思考(LLM 呼び出し)には触れない**。従って LLM 呼数は不変。
  (MobiVerse も同思想: LLM はイベント時のみ・SUMO は交通力学のみを担当 → §6)
- **R1 の帰結**: この還流を ON にすると **到着step が変わり=ゴールデンバイトは変わる**。よって
  **新 RNG stream・新 conf knob・既定 OFF**。OFF ならゴールデン完全一致(traffic.mode=od の
  結線と同じ流儀)。

### 5.4 決定論の担保と既知の落とし穴
- **SUMO 側**: `--seed` 固定で決定論(Mersenne Twister)。`--random` は禁止。
- **こちら側**: **TraCI コマンド列がシミュ状態の純関数**であれば、同 seed・同版で全体が再現する。
  = 還流→コスト更新→次の車注入…の系列を、乱数を挟まず(または本シミュの決定論 RNG stream から)
  生成する。ソケットのタイミングは同期式なので**結果には影響しない**(速度のみ)。
- **公式が挙げる非決定・非再現の要因(避ける)**:
  - `--random`(意図的に再現を壊す)。
  - **`--device.rerouting.threads` + `--weights.random-factor`** の併用 → ルーティングが非決定的。
    **スレッド並列ルーティングは使わない**。
  - **プラットフォーム差**: 地理座標変換は Proj のバージョン差で結果が変わる。`log()` の実装差が
    EIDM / DriverState 系の追従モデルに影響。→ **Windows 単機・SUMO 版固定・車追従は既定
    (Krauss)** に寄せれば実務上は同一機で byte 再現。**クロスOS byte 一致は保証されない**
    (本シミュも Windows 前提なので許容)。
  - **TraCI コマンド順**: 公式は「TraCI コマンド順の決定論」を明文保証しない → こちらの
    ドライバが順序決定論であることを**自前スモーク(同 seed 2回で byte 一致)で検収**する。
  - **libsumo と traci の結果差**: 原則一致するはずだが型チェック等の差異があるため、**どちらか
    一方に固定**して検収する。
- **パフォーマンス**(1km 網・数百台):
  - SUMO 微視は数千台でも実時間より速いのが通常。**1km・数百台 × 600 SUMO秒/step は
    ミリ秒〜秒オーダー**。libsumo ならオーバーヘッド無視可。メゾならさらに速い。
  - 総ステップ数の目安: 144 step/日 × 600 s = 86,400 SUMO秒/日分の前進。小規模網では軽い。
  - **ボトルネックは速度ではなく「外部プロセス連成の複雑さ・決定論面積・Windows での libsumo 安定性」**。

### 出典
- TraCI 概要(同期・simulationStep・libsumo 推奨・サブスクリプション): https://sumo.dlr.de/docs/TraCI/index.html
- libsumo(インプロセス・高速・制約・Windows OpenJDK 21.0.5+): https://sumo.dlr.de/docs/Libsumo.html
- Randomness(--seed・rerouting.threads×weights.random-factor・Proj/log のOS差): https://sumo.dlr.de/docs/Simulation/Randomness.html
- 基本定義(--step-length 既定1.0s・0.001〜1.0): https://sumo.dlr.de/docs/Simulation/Basic_Definition.html
- FAQ(決定論・seed): https://sumo.dlr.de/docs/FAQ.html

---

## 6. 先行事例(社会シミュ/ABM × SUMO)

### 要点
- **SUMO + JADE(古典・ABM連成の定番)**: SUMO と Java Agent DEvelopment framework を TraCI で
  つなぎ「人工交通システム(ATS)」を構成。**TraCI が ABM とのボトルネック的結合面**である
  ことを示した初期の代表例。
- **MobiVerse(2026・LLM×SUMO・本件に最も近い)**: 軽量ジェネレータで24時間活動連鎖を生成 +
  **LLM は道路閉鎖・混雑・イベント等の「変化時のみ」起動**(毎ステップ呼ばない)。SUMO を主交通
  エンジンにし **TraCI で双方向通信**、SUMO の時計を**マスタ時刻**(1秒step)に。53,000体
  (同時2万アクティブ)を実時間比 1.33× で回した。**「LLM 呼び出しをイベント駆動に絞り SUMO は
  交通力学だけ担当」= 本件の LLM呼数不変・車限定と同じ設計思想**。
- **AgentSUMO / SUMO-MCP(2026)**: LLM エージェントで SUMO のシナリオ生成・最適化を対話的に行う
  枠組み(MCP 経由)。連成というより「LLM が SUMO を操作」する系で、TraCI/ツール群の
  プログラム制御が容易なことを裏付ける。
- **外部歩行者モデル連成**: TraCI 経由で歩行者を外部モデルに委譲しつつ SUMO 車両と相互作用させる
  研究。**本件では歩行者は SUMO に載せない(車限定)**が、「一部モードだけ SUMO に持たせ、他は
  本体が持つ」疎結合が実在することの傍証。
- **エージェント交通シミュレータ概観(サーベイ)**: SUMO は「微視・連続の交通シミュ」で、素の
  SUMO は活動ベースABMではないが TraCI 拡張で ABM 連成が定番、と整理。

### MATSim との比較(1段落)
**MATSim** は各旅行者を個別エージェントとしモデル化し、**活動ベース需要生成 + 動的交通配分**を
Java 枠組みに**内蔵**(反復学習で個人の1日計画を最適化・大規模指向でスケーラブル)。一方 **SUMO**
は微視・連続の交通力学(追従・車線変更・信号)が精密で、需要は外部(od2trips/duarouter/randomTrips)
から与える。**本件は「渋谷の車の微視的な動き・信号待ち・渋滞を描く/還流する」目的**で、
需要は既にシミュ側(analyze_od のゲートウェイOD)にあるため、**活動ベース需要を内蔵する MATSim より、
微視挙動 + TraCI 連成が容易な SUMO が適切**。MATSim は「都市全体の活動-移動を丸ごと別エンジンに
置き換える」場合の選択肢で、本プロジェクトの「本体無風・車だけ精緻化」方針とは目的がずれる。

### 出典
- SUMO+JADE(ABM連成・ATS): https://link.springer.com/chapter/10.1007/978-3-662-45079-6_4
- MobiVerse(LLM×SUMO・イベント駆動LLM・TraCI 双方向): https://arxiv.org/pdf/2506.21784 / https://arxiv.org/html/2506.21784
- AgentSUMO(LLM×SUMO シナリオ生成): https://arxiv.org/html/2511.06804v1
- SUMO-MCP(MCP でSUMO自律操作): https://arxiv.org/html/2506.03548v1
- エージェント交通シミュレータ概観(サーベイ): https://arxiv.org/pdf/2102.07505
- 微視シミュレータ定量比較(SUMO 他): https://www.mdpi.com/2673-7590/5/4/201
- MATSim 公式: https://www.matsim.org/

---

## 推奨アーキテクチャ

### v0 = オフライン合成(**第一形・推奨**)

**位置づけ**: synth_crowd と同型の「本体無風」パイプライン。SUMO はビルド時に1回走らせ、
成果物(車道網・経路・車両トラック)を静的に置き、ビューア/パネルが**読むだけ**。
シミュ本体・conf・L1・ゴールデンは一切触らない(R1完全安全)。

**手順**:
1. **導入**: SUMO 1.27.1(MSI・SUMO_HOME 自動) + venv に `pip install eclipse-sumo sumolib`。版固定。
2. **生OSM**: `osmGet.py --bbox <既存bboxと同一>` で渋谷約1kmの生OSM XML を1回取得
   (`data/sumo/shibuya_raw.osm.xml`)。派生 `data/shibuya_osm.json` は不変。
3. **網生成**: §2 の `netconvert`(`--lefthand` + `--keep-edges.by-vclass passenger` +
   `--tls.guess-signals` …)→ `data/sumo/shibuya_car.net.xml`。
4. **TAZ**: 100m 地区セル + 縁(fringe)ゾーンを `edgesInDistricts.py` で辺割当 → `shibuya.taz.xml`。
5. **需要**: `analyze_od.py` の車OD(hour_bin別)→ `tazRelation` OD行列 → `od2trips` →
   `duarouter`(`--seed` 固定)→ `data/sumo/shibuya.rou.xml`。OD が薄い区間は `randomTrips.py --seed` で補完。
6. **軌跡**: `sumo -n ...net.xml -r ...rou.xml --seed <fix> --fcd-output.geo true --fcd-output fcd.xml`
   (or `.csv`)。座標は経緯度で受ける。
7. **集約**: fcd を **経緯度→シミュのローカルm** に変換し、10分窓へ整形 → 自前決定論ライタで
   `runs/<name>/panel/vehicle_tracks.parquet`(+任意で辺別・窓別の混雑統計)。
8. **可視化**: ビューアに車両トラックを結線(batch37 Track V4 の車グリフと接続)。

**工数感**: 導入〜網〜需要〜軌跡〜集約で **中規模スクリプト1〜2本 + 手順書**。R1 リスク=ほぼ無
(生成物は横置き)。難所は **(a) 生OSM XML の用意**、**(b) 座標整合(geo で回避)**、
**(c) ゲートウェイOD→TAZ 写像**の3点のみ。

**成果物**: `data/sumo/{shibuya_car.net.xml, shibuya.taz.xml, shibuya.rou.xml}` /
`runs/<name>/panel/vehicle_tracks.parquet` / ビューア統合。**全て本体無風・seed 再現**。

**誠実性**: 信号推定・OD いずれも近似(実測交通の再現ではない)。SUMO 版・seed・netconvert
引数を成果物に刻む(再現性の担保と限界の明示)。

---

### v1 = ライブ連成(TraCI/libsumo・**新stream・既定OFF で条件付き検討**)

**結合面の設計**:
- 起動: sim 開始時に `libsumo.start([... net, rou, --seed <fix>, --step-length 1 or mesosim ...])`。
- ループ: 各 sim-step(600s)で SUMO を 600s 前進 → **辺別 所要時間倍率(渋滞レベル)** を読む →
  シミュの**車道グラフ辺コストにだけ反映**(次 step の車移動 ETA/到着step に効く)。
- **LLM 不変**: 還流先は非LLMの経路コストのみ。移動手段選択・目的地決定・会話は不変 → **LLM 呼数不変**。
- **切り分け**: 新 conf knob(例 `traffic.sumo_live: false`)・新 RNG stream・既定 OFF。
  OFF でゴールデン完全一致。

**決定論リスクと対策**:
| リスク | 対策 |
|---|---|
| 外部プロセス連成で再現面積が拡大 | SUMO 版固定・`--seed` 固定・`--random` 禁止・単機運用 |
| スレッド並列ルーティングが非決定 | `--device.rerouting.threads` を使わない(`--weights.random-factor` 併用厳禁) |
| Proj/log のOS差でクロスOS不一致 | Windows 単機に限定・車追従は既定(Krauss)・**同一機 byte 再現**のみ主張 |
| TraCI コマンド順の決定論が無保証 | ドライバをシミュ状態の純関数に(乱数は本体の決定論streamのみ) |
| libsumo と traci の結果差 | どちらか一方に固定(Windows は libsumo + OpenJDK 21.0.5+ か、安定重視で traci) |
| ゴールデン破壊 | 新stream・既定OFF。ON時は「到着step が変わる」と明記し別ゴールデンで管理 |

**go / no-go 判断基準**(この順で満たせば GO):
1. **v0 が先に完成**していること(網・座標整合・OD写像が検証済み=ライブの土台)。
2. **決定論スモーク合格**: 同 seed で ≤24-step を2回 → 車道コスト系列と L1 が **byte 一致**。
3. **LLM 呼数不変の実証**: OFF/ON で LLM 呼数が完全一致(mock スモークで確認)。
4. **性能**: 24-step mock で SUMO 連成の追加 wall 時間が許容内(libsumo/mesosim 前提で軽いはず)。
5. **価値**: 「SUMO 由来の渋滞遅延」が期待待ち近似より k*/観測に**意味ある差**を生むこと。

**no-go(見送り)条件**: 上の (2)(3) のいずれかが byte で示せない / Windows で libsumo が不安定 /
還流のリアリズム向上が k* 観測を実質変えない場合は、**v0 に留める**(batch37 OPEN-3 の
「ライブ連成は工数リスク大」判断と整合。ただし本調査の結論として、**LLM 呼数不変・座標geo整合・
mesosim による軽量化・新stream OFF が全て成立するなら v1 は技術的に実現可能**であり、
頭ごなしの不採用ではなく「go/no-go スモークで判定」を推奨)。

---

## 付録A: コマンド早見

```bash
# 0) 生OSM(1回だけ・約1km bbox)
python "$SUMO_HOME/tools/osmGet.py" --bbox <W,S,E,N> --prefix shibuya -d data/sumo

# 1) 車道網(左側通行・車のみ・信号推定)
netconvert --osm-files data/sumo/shibuya_bbox.osm.xml -o data/sumo/shibuya_car.net.xml \
  --type-files "$SUMO_HOME/data/typemap/osmNetconvert.typ.xml" \
  --lefthand --keep-edges.by-vclass passenger \
  --tls.guess-signals --tls.join --tls.discard-simple --tls.default-type actuated \
  --junctions.join --geometry.remove --ramps.guess

# 2) TAZ(地区セル/縁ポリゴン→辺割当)
python "$SUMO_HOME/tools/edgesInDistricts.py" -n data/sumo/shibuya_car.net.xml \
  -t districts.poly.xml -o data/sumo/shibuya.taz.xml

# 3) 需要(OD→trips→routes・seed固定)
od2trips -n data/sumo/shibuya_car.net.xml --taz-files data/sumo/shibuya.taz.xml \
  -d shibuya.od -o shibuya.trips.xml --seed 42
duarouter -n data/sumo/shibuya_car.net.xml -r shibuya.trips.xml \
  -o data/sumo/shibuya.rou.xml --seed 42
#   (OD無し時の代替) 
python "$SUMO_HOME/tools/randomTrips.py" -n data/sumo/shibuya_car.net.xml \
  -o shibuya.trips.xml --vehicle-class passenger --fringe-factor 5 --seed 42 \
  --route-file data/sumo/shibuya.rou.xml --validate

# 4) オフライン軌跡(geoで座標整合・seed固定)
sumo -n data/sumo/shibuya_car.net.xml -r data/sumo/shibuya.rou.xml \
  --seed 42 --fcd-output.geo true --fcd-output data/sumo/fcd.xml
#   (1.24以降) --fcd-output data/sumo/fcd.parquet で直接Parquet(実験的)

# 5) ライブ連成(v1・Python・既定OFFの新stream内)
#   import libsumo as traci; traci.start(["sumo","-n",...,"-r",...,"--seed","42"])
#   for each 600s window: [traci.simulationStep() ×600] → traci.edge.getTraveltime(e) …
#   → 辺コスト倍率をシミュのA*へ(LLM非関与)→ traci.close()
```

## 付録B: 出典一覧(実在確認済み)

- SUMO Downloads / 版・Windows・EPL・pip: https://sumo.dlr.de/docs/Downloads.php
- 公式サイト: https://eclipse.dev/sumo/ ・ GitHub: https://github.com/eclipse-sumo/sumo
- OSM 取込み(車限定・左側通行・信号): https://sumo.dlr.de/docs/Networks/Import/OpenStreetMap.html
- netconvert: https://sumo.dlr.de/docs/netconvert.html ・ 取込みチュートリアル: https://sumo.dlr.de/docs/Tutorials/Import_from_OpenStreetMap.html
- OD 行列取込み(od2trips/duarouter/TAZ): https://sumo.dlr.de/docs/Demand/Importing_O/D_Matrices.html
- randomTrips.py: https://sumo.dlr.de/docs/Tools/Trip.html
- FCDOutput: https://sumo.dlr.de/docs/Simulation/Output/FCDOutput.html ・ 出力目次: https://sumo.dlr.de/docs/Simulation/Output/index.html
- Tabular Outputs(CSV/Parquet・1.24+): https://sumo.dlr.de/docs/TabularOutputs.html
- TraCI: https://sumo.dlr.de/docs/TraCI/index.html ・ libsumo: https://sumo.dlr.de/docs/Libsumo.html
- Randomness(決定論・seed・落とし穴): https://sumo.dlr.de/docs/Simulation/Randomness.html
- 基本定義(--step-length): https://sumo.dlr.de/docs/Simulation/Basic_Definition.html ・ FAQ: https://sumo.dlr.de/docs/FAQ.html
- MobiVerse: https://arxiv.org/abs/2506.21784 ・ AgentSUMO: https://arxiv.org/abs/2511.06804 ・ SUMO-MCP: https://arxiv.org/abs/2506.03548
- SUMO+JADE: https://link.springer.com/chapter/10.1007/978-3-662-45079-6_4
- エージェント交通シミュレータ概観: https://arxiv.org/abs/2102.07505 ・ 微視比較: https://www.mdpi.com/2673-7590/5/4/201 ・ MATSim: https://www.matsim.org/
