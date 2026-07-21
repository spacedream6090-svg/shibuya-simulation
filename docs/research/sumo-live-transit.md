# SUMO ライブ連成 = エージェントが「乗れる」交通の調査(第38バッチ / SUMO-RIDE)

作成日: 2026-07-21
体制: Opus Web+コードリサーチ(**調査のみ・コード変更なし**・本ファイル1本)
問い(ユーザー): 「タクシー・バス・自動車は生活に大きな影響を与える。**背景ではなく
エージェントが実際に乗れる・利用できるリアルタイム連成**にしたい。実装を調査して」

> **本書は差分**。SUMO の導入・netconvert・OD・fcd オフライン・TraCI/libsumo の基礎・決定論の
> 落とし穴・性能・先行事例(MobiVerse 等)は **[sumo-integration-research.md](sumo-integration-research.md)
> に既述**。ここでは重複を避け、**「乗れる交通」= タクシー device / 公共交通(pt) / エージェント乗車の
> 結合**に絞る。基礎事項はそちらを参照。

> **大原則(R1)**: シミュ本体・conf・L1・ゴールデンを既定で無風に保つ。乗れる交通は
> **新 conf ノブ・既定 OFF**。ON 時は **到着 step が実際に変わる**(=別ゴールデン)ことを明示管理。
> LLM 呼数は不変(乗車判断は既存の非LLM ロジック、SUMO は物理だけ担当)。

---

## 0. 要約(TL;DR)

- **現状の「乗車」は運賃オーバーレイのみ**: 既存 `transit_ride`(config.yaml:542)は、move_to に
  taxi/bus を **被せて mode="car" で走らせ、到着時に運賃を払うだけ**。**車両も待ち時間も配車もダイヤも
  無い**(routine.py `_ride_extra` / scheduler `_charge_ride`)。= ユーザーの言う「背景」の一種。
- **SUMO には「乗れる」ための一式が揃っている**:
  - **taxi device**: 予約(reservation)→ 配車(dispatch: greedy/greedyClosest/**greedyShared**/
    routeExtension/**traci**)→ pickup → dropoff。相乗り(group)・事前予約(prebooking)・
    待機挙動(idle: stop/randomCircling/taxistand)まで公式実装。**TraCI で外部配車**が可能
    (`traci.person.getTaxiReservations` / `traci.vehicle.dispatchTaxi` / `getTaxiFleet`)。
  - **公共交通(pt)**: `busStop`・`ride lines=`・固定路線(route+stop+`until` ダイヤ・`repeat/cycleTime`
    ループ)・`access` 辺。**`gtfs2pt.py` で GTFS→ptlines 変換**、`ptlines2flows.py` で便を生成。
- **データ(バス)は入手可**: **都営バス GTFS + GTFS-RT が ODPT で公開**
  (ckan.odpt.org)。現行 ODPT 連携は **鉄道9路線のみ**でバスは未取得([odpt-integration.md](odpt-integration.md))。
  `gtfs2pt.py` にそのまま渡せる。
- **推奨アーキテクチャ**: **(b) ハイブリッド**(SUMO を **背景車つきで連続実行**し、**エージェントが
  乗るときだけ SUMO の person/taxi と照会**)。完全ライブ(a)は決定論面積が過大、現行オフライン(c)は
  「乗る」体験が出ない。**段階計画**: v0(既存オフライン車=済)→ **v-Ride-1(タクシー配車を traci 制御・
  少数・既定 OFF)→ v-Ride-2(pt バスを実路線で・乗車結合)**。go/no-go はスモークで判定。
- **本選現実性**: SUMO 微視は **CPU コア 1 本を専有**すれば 1km・数千台規模は実時間より速い(既述)。
  タクシー数百台・バス数十便の追加は誤差。**律速は速度でなく「決定論の担保」と「Windows での安定性」**。

---

## 1. 現状の「乗車」実装(出発点の確認)

- **決定(routine.py `_ride_extra` L505-541)**: 距離 `dist>min_dist_m(既定600m)` かつ所持金充分で、
  `stream("taxi", id, step).random() < prob(0.15)` なら taxi。バスは `enabled` かつ停留所が
  出発/目的の両方 <100m のとき(`BusNetwork.find_ride`)。**いずれも決定論・LLM 非関与**。
- **実行(scheduler `_charge_ride` L592-603 / `_phase_move` 到着処理 L879-882)**:
  乗車は `mode="car"` で **通常の徒歩系ルートを車速で走る**だけ。到着 step で `ride` イベントを
  ログし運賃を `spend`。**配車待ち・車両・相乗り・遅延・満車・積み残しは無い**。
- **含意**: ユーザーの「実際に乗れる」= **(i) 呼ぶと車が来る待ち時間、(ii) 実車両の物理(渋滞に
  巻き込まれる)、(iii) バスは路線とダイヤに縛られる、(iv) 満車/未配車で乗れないことがある** ——
  これらは今は全て無い。**SUMO の taxi device / pt がちょうどこの4点を埋める**。
- **重要な違い(背景車との対比)**: [sumo-integration-research.md](sumo-integration-research.md) の
  v1 は「辺コスト倍率だけ還流」で **エージェントの到着 step をほぼ変えない**(徒歩は影響小)。
  一方「乗れる交通」は **到着 step を実際に変え、乗れない事象も生む** → **挙動・ゴールデンへの影響が
  本質的に大きい**。ここが新しい設計・検収上の勘所。

---

## 2. タクシー: SUMO taxi device の結合設計

### 2.1 SUMO taxi device の要点(公式)
- **車をタクシー化**: 車両に `<param key="has.taxi.device" value="true"/>`。オプション
  `--device.taxi.dispatch-algorithm`・`--device.taxi.dispatch-period`(既定 60s)・
  `--device.taxi.idle-algorithm`。
- **配車アルゴリズム(5種)**:
  - `greedy`(予約順に、旅行時間最短のタクシーを割当) / `greedyClosest`(空車ごとに最寄り客) /
    **`greedyShared`**(相乗り。`absLossThreshold`/`relLossThreshold` で許容回り道) /
    `routeExtension`(既存経路に沿って拾う) / **`traci`(配車を外部=我々のコードに委譲)**。
- **予約(reservation)の作り方**:
  - 直接(ライドヘイリング): `<person><ride from=".." to=".." lines="taxi"/></person>`
  - 交通結合: `<personTrip from=".." to=".." modes="taxi"/>`
  - 事前予約(prebooking): `earliestPickupTime` / `reservationTime`。
- **pickup/dropoff**: `--device.taxi.pickupDuration`(既定0s)/ `--device.taxi.dropOffDuration`(既定60s)/
  `--device.taxi.parking`(停車が車線を塞ぐか)。相乗りは `group` 属性で capacity まで同乗可。
- **TraCI API(外部配車=本命)**:
  - `traci.person.getTaxiReservations(state)`(state: 0=all,1=new,2=retrieved,4=assigned,8=picked-up)
  - `traci.vehicle.getTaxiFleet(state)`(0=empty,1=pickup,2=occupied,3=両方)
  - `traci.vehicle.dispatchTaxi(vehID, [reservationIDs])`(予約をタクシーへ割当)
- **待機挙動 `--device.taxi.idle-algorithm`**: `stop`(既定=最後の客の場所で停止)/ `randomCircling`
  (流し運転)/ `taxistand`(`parkingArea` で客待ち)。
- 出典: SUMO Taxi Device https://sumo.dlr.de/docs/Simulation/Taxi.html

### 2.2 我々のエージェント(徒歩系・非SUMO)との結合
**課題**: 我々のエージェントは **SUMO の person ではない**(LLM 駆動で別エンジン)。よって
「エージェントが呼ぶ」= **SUMO 側に幻の person(予約)を注入し、車の物理だけ SUMO に解かせ、
結果(配車待ち・所要時間)を我々の step 粒度へ写す**、という **片方向の物理委譲**にする。

**10分 step でどう見せるか**(`dispatch-algorithm=traci` 前提):
1. **呼ぶ(step t)**: routine.py が現行ロジックで taxi 乗車を決めた瞬間、SUMO に
   `traci.person.add(...)` + `appendDrivingStage(toEdge, lines="taxi")`(または予約を直接注入)で
   **エージェント位置の最寄り車道辺に予約を1件立てる**。同時に `dispatchTaxi` で最寄り空車へ割当。
2. **来る**: SUMO を当該 step 分(600 SUMO秒)進める間に、タクシーが pickup 辺へ走る。
   **pickup 到達時刻 = 配車待ち**。600s 内に拾えれば同 step 乗車、拾えなければ **次 step へ持ち越し**
   (= 「今すぐは来ない」体験)。
3. **乗る→降りる**: SUMO が dropoff 辺まで運ぶ。**総所要 = 配車待ち + 乗車時間(渋滞込み)**。
   エージェントの **到着 step = ceil((呼んだ時刻 + 総所要)/600)**。
4. **見せ方**: 既存の `route_start`(mode=taxi)/ `ride` イベントはそのまま使い、**payload に
   `wait_s`(配車待ち)・`ride_s`(乗車時間)・`shared`(相乗り相手数)を足す**だけでビューアに出せる。
   ビューアには SUMO のタクシー車両トラック(fcd と同型)を重ねれば「車が迎えに来て走り去る」絵になる。
- **満車/未配車**: `getTaxiFleet(0)` が空でなければ配車、無ければ **今 step は乗れない**
  (徒歩にフォールバック or 待機)。= 現実の「捕まらない」体験。
- **相乗り**: `greedyShared` or `group` で、近接・同方向のエージェント予約を capacity まで束ねる。
  「タクシーを分け合う」社会的行動が観測対象になりうる([org-emergence-goal] 的な協調の芽)。

**LLM 呼数不変**: 乗る/呼ぶの判断は既存の非LLM `_ride_extra`。SUMO は **待ち時間と所要時間(=到着step)**
だけを変える。エージェントの思考(LLM 呼び出し)には触れない → **呼数完全不変**(MobiVerse と同思想)。

---

## 3. バス/公共交通: SUMO pt の結合設計

### 3.1 SUMO pt の要点(公式)
- **停留所**: `<busStop id=".." lane=".." startPos=".." endPos=".."/>`(車線上の区間)。`<access>` 子要素で
  他辺からの徒歩接続(`lane`/`pos`/`length`)。
- **固定路線バス**: `<route>`(バス vType)+ `<stop busStop=".." duration=".." until=".."/>`。
  `until` は絶対時刻ダイヤ(車は until まで発車しない)。`repeat`/`cycleTime` で **1 台を巡回運行**。
- **乗客**: `<person>...<ride lines="<路線>" busStop="<降車停>"/>` で乗車(person 仕様側で規定)。
- **生成/取込ツール**:
  - **`gtfs2pt.py`**: GTFS → SUMO の pt(ptlines・stops・便)へ変換(地理参照網が必要)。
  - **`ptlines2flows.py`**: ptlines 定義から `until`/`duration` 付きの便フローを背景シミュで生成。
  - `osmWebWizard` は OSM の pt を取込む簡易口。
- 出典: SUMO Public Transport https://sumo.dlr.de/docs/Simulation/Public_Transport.html

### 3.2 データ: 渋谷区内の実バス路線
- **都営バス GTFS + GTFS-RT が ODPT で公開**(データセット `b_bus_gtfs_rt-toei`・ckan.odpt.org)。
  「標準的なバス情報フォーマット(GTFS-JP)」準拠。**東急バス・京王バスも ODPT カタログに順次**。
- **現行連携はバス未取得**: `data/odpt/` は **鉄道9路線+TokyoMetro 鉄道 GTFS のみ**
  ([odpt-integration.md](odpt-integration.md))。バス GTFS は **未 fetch**。`fetch_odpt.py` に
  バス GTFS 取得を足し、`gtfs2pt.py` へ渡す導線が要る(新規)。
- **既存の簡易バス**(`data/transit_shibuya.json` の `bus_lines` 2 路線=手書き中立名・既定 OFF)は、
  SUMO 実路線に置換すると **`BusNetwork.find_ride` の「停留所<100mなら乗れる」近似を、実ダイヤ・実所要で
  実体化**できる。
- 出典:
  - 東京都交通局 バス GTFS-RT(ODPT): https://ckan.odpt.org/dataset/b_bus_gtfs_rt-toei
  - 都営バス GTFS-RT 提供開始告知: https://www.odpt.org/2020/08/17/(東京都交通局バスロケGTFS-RT)
  - 公共交通オープンデータ GTFS 一覧: https://ckan.odpt.org/dataset

### 3.3 エージェント乗車の結合(既存 transit_ride.bus の実体化)
- **設計**: 既存の「停留所が近ければ乗車」(`find_ride`)を残しつつ、**乗車可否と所要を SUMO pt に問う**:
  1. 出発/目的が **実 busStop の access 圏内**か(SUMO 網の busStop で判定)。
  2. 次便の `until` から **待ち時間**を、路線所要から **乗車時間**を得る。
  3. 到着 step = ceil((呼んだ時刻 + 待ち + 乗車)/600)。運賃は既存 `_charge_ride`。
- **軽量版(pt を回さない)**: バスは **ダイヤが決定論**なので、SUMO を毎 step 回さずとも
  `gtfs2pt.py` が吐いた **停留所・便時刻・区間所要の静的表**だけ読めば「実ダイヤ近似乗車」ができる
  (= タクシーより SUMO ライブ不要度が高い)。**バスはまず静的表、タクシーだけライブ**が費用対効果良。

---

## 4. アーキテクチャ案の比較

| 観点 | (a) 完全ライブ(毎 step TraCI 同期) | (b) ハイブリッド(SUMO 連続実行・乗車時のみ照会)**推奨** | (c) 現行オフライン+時刻表近似 |
|---|---|---|---|
| SUMO の役割 | 全交通(背景車+タクシー+バス)を毎 step 同期 | 背景車+タクシーを連続実行、pt バスは静的表、**乗車照会だけ双方向** | ビルド時1回。乗車は運賃オーバーレイ(現状) |
| 「乗れる」体験 | ◎ 完全(待ち/渋滞/満車/相乗り) | ◎ タクシーは完全・バスは実ダイヤ | △ 無し(瞬間ワープ+運賃) |
| 計算コスト | 中(1km 数千台は実時間より速いが常時) | **小〜中**(乗車が起きる step だけ照会が増える) | 極小(静的読み) |
| 決定論 | **難**(外部プロセス連成の面積が全 step に広がる) | **中**(照会点が限定・我々の dispatch 順を純関数化すれば可) | ◎ 完全(seed 再現) |
| ゴールデン影響 | 大(常時 ON 相当) | 大だが **既定 OFF で無風**・ON は別ゴールデン | 無(現状) |
| 工数 | 大 | **中**(taxi=traci 配車ドライバ+pt 静的表) | 済 |
| 本選現実性(CPU1本) | タクシー/バス込みで専有必要・安定性懸念 | **1本専有で余裕**(照会は間欠) | 不要 |

### 決定論の勘所(乗れる交通で新たに load-bearing になる点)
- `dispatch-algorithm=traci` は **配車の割当順が我々のコードで決まる** → **その順序がシミュ状態の純関数**
  でなければ再現しない(dict 反復順・wall-clock 禁止。予約は id ソートで処理)。
  背景車の「辺コスト還流」より **決定論要求が厳しい**(割当が到着 step を直接変えるため)。
- SUMO 側は `--seed` 固定・`--random` 禁止・スレッド並列ルーティング禁止(既述の落とし穴を継承)。
- **積み残し/満車の分岐**も決定論に(`getTaxiFleet` の結果は seed 固定で再現するが、**照会タイミングを
  step 境界に固定**して曖昧さを消す)。
- 検収: 同 seed で ≤24-step を2回 → **乗車イベント列・到着 step・L1 が byte 一致**(OFF)。ON は別ゴールデン。

---

## 5. 推奨と段階計画(go / no-go 判断材料つき)

**推奨 = (b) ハイブリッド**。理由: 「乗れる」体験の核(配車待ち・渋滞・満車・相乗り・実ダイヤ)を
出しつつ、SUMO 連成の**決定論面積を『乗車が起きる点』に限定**でき、CPU1本で本選も回る。バスは
まず静的表(ライブ不要)、タクシーだけライブにして費用対効果を最大化する。

| 段階 | 内容 | go/no-go 判断材料 |
|---|---|---|
| **v0(済)** | 背景車オフライン(net/OD/fcd/vehicle_tracks)= [sumo-integration-research.md](sumo-integration-research.md) の第一形 | 完了済み(車6,460台/日) |
| **v-Ride-0 データ** | `fetch_odpt.py` にバス GTFS(都営)取得を追加 → `gtfs2pt.py` で pt 変換 → 停留所・便・区間所要の **静的表**を `data/sumo/` に生成 | GTFS 取得可(公開確認済)・gtfs2pt が渋谷網で通るか |
| **v-Ride-1 タクシー(ライブ・少数・既定 OFF)** | taxi device + `dispatch=traci`。エージェント乗車決定時に予約注入 → 配車 → 到着 step 算出。相乗りは後回し | **(1)** OFF/ON で LLM 呼数一致(mock) **(2)** 同 seed 2回で乗車列+到着 step が byte 一致 **(3)** 24-step mock の追加 wall 時間が許容内 **(4)** Windows で libsumo/traci 安定 |
| **v-Ride-2 バス乗車結合** | 既存 `transit_ride.bus` を **静的表(実ダイヤ・実所要)で実体化**。停留所 access 圏・次便待ち・区間所要 | **(1)** 実ダイヤ乗車が決定論 **(2)** 既存簡易バスと差し替えても OFF バイト一致 |
| **v-Ride-3(条件付き)** | 相乗り(greedyShared/group)・流し運転(randomCircling)・pt もライブ(遅延伝播) | 相乗り/遅延が **k*・組織創発の観測に意味ある差**を生むか |

**no-go(見送り)条件**: v-Ride-1 の判断材料 (1)(2) が byte で示せない / Windows で libsumo が不安定 /
「配車待ち・渋滞・満車」を入れても k*・観測が実質変わらない場合は、**バスの静的表(v-Ride-0/2)だけ入れ、
タクシーはライブ化せず**現行オーバーレイに実待ち時間の近似(固定分布ではなく時間帯別の期待待ち)を
足すに留める。**頭ごなしの不採用ではなく、v-Ride-1 スモークで判定**。

**工数見積り**:
- v-Ride-0(バス GTFS→pt 静的表): 中(取得導線+gtfs2pt+表整形。スクリプト1本)。
- v-Ride-1(タクシー traci 配車): **中〜大**(SUMO 連続実行ドライバ+予約注入+到着step写像+決定論スモーク。
  背景車 v1 の連成骨格を流用できるぶん軽くなる)。
- v-Ride-2(バス乗車結合): 小〜中(静的表を `_ride_extra`/`find_ride` 経路に差すだけ・SUMO ライブ不要)。
- v-Ride-3: 中〜大(相乗り/遅延の決定論と観測価値の検証が主コスト)。

---

## 6. 未確認事項(事実と推測の区別)

- **taxi device の Windows/libsumo 安定性**: 公式は OpenJDK 21.0.5+ 推奨(既述)。taxi+traci 配車を
  Windows で長時間回した一次事例は未確認 → **v-Ride-1 スモークで自前検証**。
- **`dispatchTaxi` の決定論**: seed 固定で再現するはずだが、**我々の配車順**が純関数であることは
  自前スモーク(同 seed 2回 byte 一致)で担保する必要(公式は TraCI コマンド順の決定論を明文保証せず)。
- **non-SUMO エージェントの person 注入**: 我々の徒歩系エージェントを SUMO の予約として注入する
  具体 API 経路(`person.add`+`appendDrivingStage` vs 予約直接注入)の最短実装は要 PoC 確認。
- **バス GTFS の渋谷網整合**: `gtfs2pt.py` は「地理参照網」を要求。我々の SUMO 車道網(左側通行・
  車限定)に **バス停スナップ**が綺麗に載るかは未検証(停留所 access 辺の生成率が鍵)。
- **東急/京王バスの GTFS 提供状況**: 都営は確認済。東急バス・京王バスの GTFS 提供有無・鮮度は
  ODPT カタログで個別確認要(未確認)。
- **相乗り(greedyShared)の観測価値**: 「タクシーを分け合う」協調が k*・組織創発に効くかは仮説段階。
- **性能の実測**: タクシー数百台の追加コストは「誤差」と推定(1km 微視は数千台でも軽い=既述)だが、
  **traci 照会を毎 step 挟むオーバーヘッド**の実測は未取得 → 24-step mock で測る。

---

## 付録: 出典一覧(実在確認済み)

- **本書の基礎(重複回避のため参照)**: [sumo-integration-research.md](sumo-integration-research.md)
  (導入・netconvert・OD・fcd・TraCI/libsumo・決定論・性能・MobiVerse 等の先行事例)
- SUMO Taxi Device(dispatch 5種・reservation・pickup/dropoff・idle・相乗り・TraCI API):
  https://sumo.dlr.de/docs/Simulation/Taxi.html
- SUMO Public Transport(busStop・ride lines・until ダイヤ・repeat/cycleTime・access・gtfs2pt/ptlines2flows):
  https://sumo.dlr.de/docs/Simulation/Public_Transport.html
- 都営バス GTFS-RT(ODPT データセット): https://ckan.odpt.org/dataset/b_bus_gtfs_rt-toei
- ODPT データカタログ(バス各社 GTFS): https://ckan.odpt.org/dataset
- 東京都交通局バスロケ GTFS-RT 提供告知: https://www.odpt.org/2020/08/17/(東京都交通局バスロケGTFS-RT)
- 現行 ODPT 連携(鉄道9路線・バス未取得): [odpt-integration.md](odpt-integration.md)
- コード実査: `src/society/cognition/routine.py`(_ride_extra L505)・
  `src/society/engine/scheduler.py`(_charge_ride L592 / _phase_move L879)・
  `src/society/world/transit.py`(BusNetwork.find_ride)・`conf/config.yaml`(transit_ride L542)
</content>
