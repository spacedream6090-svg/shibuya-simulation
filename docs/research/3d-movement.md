# エージェント移動の3D地理精緻化 — リサーチ・構想・計画

作成: 2026-07-20 / 担当: Opus(リポジトリ読取 + Web調査・**コード変更なし**) / 種別: リサーチ + 構想 + 実装計画
ユーザー要望: 「エージェントの位置をより詳細に、3D地理情報を反映してより詳細に動くようにしたい。実装のリサーチと構想と計画をひとまずしてほしい」

必読の前提(本書はこれらと矛盾しない差分):
- [`social-force-crowd.md`](social-force-crowd.md) — 群衆物理(SFM)案a/案b・スクランブル微視移動の既決方針
- [`sumo-integration-research.md`](sumo-integration-research.md) — SUMOは**車限定**(歩行者は不採用)
- [`traffic-signals-audit.md`](traffic-signals-audit.md) — 信号・移動手段決定の現状監査
- [`3d-visualization.md`](3d-visualization.md) — PLATEAU入手・座標変換・ビューア(UE/Web3D/Blender)
- [`../plans/million-scale.md`](../plans/million-scale.md) — 背景tier SoA化・**0.0002s/agent-step予算**・「全員思考」方針
- [`env-asset-inventory.md`](env-asset-inventory.md) — PLATEAU/OSM/ODPT資産の再配布制約
- 実装: [`world/map.py`](../../src/society/world/map.py) / [`world/routing.py`](../../src/society/world/routing.py) / [`engine/scheduler.py`](../../src/society/engine/scheduler.py) `_phase_move` / [`viz/sfm.py`](../../viz/sfm.py) / [`scripts/plateau_extract.py`](../../scripts/plateau_extract.py)

---

## 0. 結論(TL;DR)

1. **現状のエージェント移動は純2D(x,y)**。位置はOSMグラフのノード + エッジ上の進捗(`edge_offset`)で決まり、`x,y` はエッジ折れ線の弧長補間([`map.py::xy_along`](../../src/society/world/map.py))。**z(高さ)はエージェント状態に存在しない**([`agent.py`](../../src/society/agents/agent.py):`node/x/y/edge_offset/floor/loc`。`floor` は整数の階のみ)。3Dは**ビューア側の描画時に地形へドレープ**しているだけ(`groundAt(x,y)+1.1`)。
2. **「3D精緻化」は2つの独立軸に分解できる**:(A)**水平解像度**=歩道・横断歩道・地下通路・駅構内を反映した層状歩行ネットワーク上を歩かせる、(B)**垂直解像度**=地形DEM・デッキ・地下・階のzをエージェント座標に載せる。両者はデータも工数も別。
3. **推奨アーキテクチャ = 連続2.5D座標 + 層状グラフのハイブリッド**(navmesh全面採用でも純グラフ維持でもない中庸)。前景/可視域は連続座標 + 局所回避(既存 [`viz/sfm.py`](../../viz/sfm.py) の Social Force を昇格)、背景は現行グラフ + SoA一括ベクトル演算で **0.0002s/agent-step 予算を死守**。zは全tier共通で**地形・レイヤーからのO(1)サンプリング**(移動計算には入れない=安い)。
4. **データは大半が入手可能**。垂直(z)は**PLATEAU資産が抽出済み**(地形2m格子 heights float32・地下街 ubld・橋 brid、[`data/plateau/`](../../data/plateau/))。水平の精緻化は 国交省「歩行空間ネットワークデータ」+ OSM footway/crossing + PLATEAU tran(道路)+ 手持ちの [`floorguide_shibuya.json`](../../data/floorguide_shibuya.json) を層状に統合する。駅構内の連続ナビは屋内地図(IMDF/ODPT)次第で**入手性に難あり**(§3-e)。
5. **SUMOは歩行者に使わない**(既決・[`engine-architecture.md`](../plans/engine-architecture.md)。striping歩道拘束モデルはスクランブルの高密度双方向に不適)。歩行者物理は**Social Force系**、車は将来SUMO、という役割分担を継承する。

> **一行の結論**: 「3D移動」は *z座標の追加*(安い・地形サンプリング=数日)と *水平ネットワークの精緻化*(中〜大・歩行空間NW/駅構内データ依存)と *局所連続移動*(既存SFMの昇格=中)の3つに分け、**LOD前提で前景だけ連続座標・背景はグラフ+SoA**で予算を守るのが唯一の現実解。全数を連続microにするのは 0.0002 予算と両立しない。

---

## 1. 現状の把握(実コードの精読結果)

### 1.1 エージェントの位置表現と移動(純2D・グラフ駆動)

| 要素 | 実装 | 備考 |
|---|---|---|
| 位置状態 | `agent.node`(現/直前ノード)・`agent.x, agent.y`(local-m)・`agent.edge_offset`(エッジ上の進捗m)・`agent.floor`(整数の階)・`agent.loc`("street"/"outside"/建物) | [`agent.py`](../../src/society/agents/agent.py):28-43。**z座標は無い**。`floor` は建物内の階数(高さmではない) |
| 移動1step | `_phase_move`([`scheduler.py`](../../src/society/engine/scheduler.py):696-796)。`budget_m = speeds[mode]×congestion` をエッジ折れ線に沿って消費、ノード到達で `route.pop(0)` | walk=800m/10分=**1.333 m/s**(Weidmann/Helbingの希望速度1.34と一致=SFM較正済み。social-force-crowd §1.3) |
| 座標補間 | [`map.py::xy_along`](../../src/society/world/map.py):114-129 がエッジ幾何(折れ線)の弧長 `offset` 地点を返す | ビューアも同じ弧長パラメータ化(`alongPath`) |
| 混雑 | エッジ単位の容量比 `factor = 1.0 if count≤capacity else max(0.3, capacity/count)` | **完全停止しない・エッジ粒度で粗い**。局所回避・レーン形成は無い |
| 静止時の揺らぎ | `_phase_jitter`([`scheduler.py`](../../src/society/engine/scheduler.py):601-621):路上滞在中は±5mのseed付きランダム | 「数十分同一座標で静止」の解消目的。信号監査が指摘した「車が自由に見える」正体の一部 |
| 垂直レイヤー | `node_layer`(-1=地下街 / 0=地上 / 1=デッキ)。routingはlayer混在グラフを普通に探索 | [`map.py`](../../src/society/world/map.py):131-191。**layerは離散ラベルでzではない** |
| 経路探索 | A* + ODキャッシュ([`routing.py`](../../src/society/world/routing.py))。walk=全klass / bicycle=階段以外 / car=車道のみ | |

**要点**: エージェントは「ノード間を折れ線に沿って弧長一定速度で進む2D点」。混雑はエッジ容量の減速だけで、**歩道の左右・すれ違い・横断歩道の待ち・階段の上り下り・駅構内の乗換動線**はいずれも表現されていない。

### 1.2 背景交通(車)— まだSoAではない

[`traffic.py`](../../src/society/world/traffic.py) の車両は ambient/od どちらも**1台=1 dict のPythonループ**で車道グラフを辿る(`for car in self.cars`)。numpy SoA一括演算ではない。million-scale が言う「背景tierのSoA化」は**未着手**で、車もエージェントも現状はオブジェクト逐次。→ 3D移動の背景tier設計は、この SoA化(W2-A)と同じ器に載せるのが自然。

### 1.3 3D可視化の現状(ビューア側でドレープ)

- [`scripts/plateau_extract.py`](../../scripts/plateau_extract.py) がPLATEAU渋谷区2025から抽出済み: **建物LOD2**(`plateau_mesh.npz`)・**地形**(`terrain.npz`: heights float32・**2m格子・nx=1088×ny=921・ground0=15.18m・z∈[-8.14, 23.91]m**、[`terrain.json`](../../data/plateau/terrain.json))・**地下街 ubld**・**橋 brid**(`extras.npz`)。
- [`make_viewer3d.py`](../../viz/make_viewer3d.py) の `groundAt(x,y)`(双一次補間)が地形高さを返し、エージェントは `groundAt(x,y)+1.1` に接地表示。道路/OSMは地表へドレープ。**sim側の x,y は不変で、zは描画時だけ付く**(地形なし時は `groundAt≡0` で従来動作とバイト一致)。
- 移動の見た目は `move_segment.pts`(RDP間引きポリライン)を `posAt/alongPath` で step内補間する。**これが「現状: ノード間補間」の実体**。

### 1.4 既に存在する群衆物理の足場(重要)

- [`viz/sfm.py`](../../viz/sfm.py): **自前の最小Social Force Model**(Helbing&Molnár1995 / Helbing2000、numpy全ペアO(n²)+カットオフ、決定論)。位置・速度・目標・希望速度のSoA配列を持ち、`step(dt)` でEuler積分。**まさに連続座標microエンジンの核が実装済み**。
- [`scripts/synth_crowd.py`](../../scripts/synth_crowd.py): **案a=オフライン合成**。既存ランのL1 `move_segment` を読み、スクランブル円領域だけをSFMで微視軌跡化 → `crowd_tracks.parquet`。R1/ゴールデン完全無風。
- つまり「連続座標 + 局所回避」は**スクランブル限定・オフライン・描画専用としては既に動いている**。本計画はこれを(i)領域を歩行者ネットワーク全体へ広げ、(ii)前景tierについてはオンライン化する拡張として位置づけられる。

---

## 2. リサーチ課題の整理(何を新たに調べるか)

3D精緻化に必要な外部知見を a–f に分けて §3 で詳述する。要旨:

- **a. 歩行空間ネットワークデータ**(国交省仕様・G空間情報センター・PLATEAU歩行者NW): 歩道・横断歩道・階段・EV・幅員・勾配の正確なリンクが入れば、水平精緻化の一次データになる。
- **b. OSM渋谷の歩行者タグ被覆率**(footway/crossing/steps/elevator): 手軽な一次候補。ただし日本の歩道は車道中心線に潰れがちで被覆に難。
- **c. CityGML/PLATEAU LOD2からのnavmesh生成**(recastnavigation・グリッド・TIN統合): 建物footprint + 地形から歩行可能面を作る手法。
- **d. 群衆マイクロモデルのコスト**(Social Force / ORCA・RVO2 / SUMO striping / numpyベクトル化): 前景を連続microにする際のs/step規模感。
- **e. 駅・地下の詳細**(渋谷駅構内図・乗換動線のオープンデータ・ODPT・IMDF): 最難関。屋内連続ナビの可否を左右。
- **f. 先行例**(PLATEAU人流実証・LLM社会シミュの空間解像度相場): 設計の相場観と妥当性の外部裏づけ。

---

## 3. リサーチ結果(a–f)

> 出典URLは各項末尾。ODPT等のAPIキー・トークンは**一切記載しない**(登録制である事実のみ記す)。2024–2026の最新状況を優先し、古い情報は年を明記する。

### 3-a. 歩行空間ネットワークデータ(国交省 / G空間情報センター / PLATEAU)★水平精緻化の本命

**(1) 国交省「歩行空間ネットワークデータ整備仕様」= 最新2024年7月版**。リンク(経路)+ノード(結節点)の2要素、座標系JGD2011、3層構造(第1層最低限〜第3層任意)。**本プロジェクトに直結する属性**:
- リンク `rt_struct`(経路構造): 1=車歩分離あり / 2=分離なし / **3=横断歩道** / 4=横断標示なし横断 / **5=地下通路** / **6=歩道橋・ペデストリアンデッキ** / **7=施設内通路** / 8=その他。
- リンク `route_type`: 2=動く歩道 / **3=踏切** / **4=エレベーター** / **5=エスカレーター** / **6=階段** / 7=スロープ。
- リンク `width`(幅員4区分)・`vtcl_slope`(縦断勾配)・`lev_diff`(段差)・`tfc_signal`(歩行者信号)・`stair`(段数)・`roof`(屋根)など全54項目。
- ノード `floor`(階層: 地上0 / 地下-1 / 中間0.5刻み)・`elevation`(標高m)・`in_out`(1施設外 / 2境界 / 3施設内)・接続リンクID。
- **屋内は「アンカーポイント」で階層別データと地上網を連結**する設計 = 駅構内⇄地上の接続に効く。
- フォーマット: CSV / Shapefile / GeoJSON / GML(UTF-8)。→ **本プロジェクトの `layer`/`z`/`width`/`grade` 属性付き層状グラフ(§4.2)にほぼそのまま写像できる**。

**(2) G空間情報センターに渋谷データが実在**: 「(東京都)渋谷地区」ノード/リンク/施設 GeoJSON+ZIP(**更新2017-12-22=旧仕様**)、「(東京都)渋谷南部」リンク/ノード。ライセンス=**政府標準利用規約2.0(CC BY 4.0互換・出典表示で再配布/改変/商用可)**。**注意: 渋谷地区は2017年時点で、2018–2025の駅前大改造(渋谷スクランブルスクエア/ストリーム/フクラス等)を未反映**。地上の基礎グラフには使えるが最新街区はPLATEAU 2025で補正が要る。

**(3) PLATEAU渋谷区2025に道路LOD3(歩道分離)+地下街LOD1**: 交通(道路)モデル**LOD1/2/3.0**、**地下街LOD1・4.1**。**LOD3道路は歩道と車道を区分し、縁石段差(~15cm)・横断歩道段差(~2cm)まで表現**。ライセンス=PLATEAU Site Policy(CC BY 4.0相当・再配布可)。**前例あり**: uc22-023(西新宿)は道路LOD1/LOD3枠線から**Pythonで歩行ネットワークを自動抽出**しKDDI人流で70%以上一致、uc24-01(台場)は**PLATEAU SDK for Unityで車道/歩道/分離帯幅を含む道路網を自動生成しGeoJSON出力**。→ **渋谷は歩行網の自動生成に最有力**。

- 国交省仕様(2024.7): <https://www.mlit.go.jp/sogoseisaku/soukou/sogoseisaku_soukou_tk_000056.html> / 本体PDF <https://www.mlit.go.jp/sogoseisaku/soukou/content/001757259.pdf>
- G空間 歩行空間NW: <https://www.geospatial.jp/ckan/dataset/0401>
- PLATEAU uc22-023(西新宿・歩行NW自動抽出): <https://www.mlit.go.jp/plateau/use-case/uc22-023/> / uc24-01(道路網自動生成): <https://www.mlit.go.jp/plateau/use-case/uc24-01/>
- PLATEAU渋谷区2025: <https://www.geospatial.jp/ckan/dataset/plateau-13113-shibuya-ku-2025>

### 3-b. OSM渋谷の歩行者タグ被覆率 ★渋谷中心部は日本OSM最高水準・線は揃う/属性と面が欠ける

**(1) 生OSMの実測(Overpass・bbox lat35.655–35.665×lon139.695–139.705≈1km²、2026-07スナップショット)**:

| タグ | 種別 | 件数 |
|---|---|---:|
| `highway=footway` | way | **698** |
| `footway=sidewalk`(歩道を車道と別線化) | way | **202** |
| `footway=crossing`(横断歩道の線) | way | **196** |
| `highway=crossing`(横断ノード) | node | **252** |
| `highway=steps`(階段) | way | **152** |
| `highway=elevator` | node | 16 |
| `highway=pedestrian`(歩行者専用街路) | way | 55 |
| `crossing:scramble`(スクランブル) | node | 6 |
| `area:highway`(面表現) | way | **1** |

→ **1km²に歩道系way約900本・横断関連約450件は日本OSMで最高水準の「マイクロマッピング済み」領域**。`footway=sidewalk`が202本=渋谷では歩道が車道中心線と別線で描かれている。ただし**面(`area:highway`)は1件のみ=歩行可能領域はほぼ線のみ**。

**(2) リポジトリ地図([`data/shibuya_osm_wide_v7.json`](../../data/shibuya_osm_wide_v7.json))の取込み実態(本調査で直接集計)**:

| klass | エッジ数 | 総延長 | | layer | エッジ / ノード |
|---|---:|---:|---|---|---|
| **footway** | 1937 | **61.8 km** | | 1(デッキ) | 246 / 118 |
| pedestrian | 262 | 10.3 km | | -1(地下) | 102 / 41 |
| **steps** | 193 | 2.3 km | | -2(地下2) | 88 / 75 |
| path / corridor / elevator | 51 / 3 / 2 | 1.4 km | | 2(高架2) | 60 / 32 |
| (車道系: residential/tertiary/…) | 2493 | ~110 km | | 0/None(地上) | 4448 / 3233 |

→ **footwayは既にリポジトリ地図で最大クラス(全4944エッジ中1937)**。デッキ・地下(layer 1/-1/-2)の立体構造も取込み済み。**ただしエッジ属性は `geometry/klass/layer/length` のみ**で、**幅員・横断種別・縁石・勾配・信号は無い**。`crossing` klassも存在せず(横断はfootwayに畳まれるか脱落)。

**(3) 日本OSMの一般傾向と限界**:
- 承認手法は歩道別線化(`footway=sidewalk`)だが、車道に `sidewalk=both/left/right` 属性だけ付ける簡易方式と**混在**(地域差大)。都心繁華街=濃密、郊外=車道中心線のみ。渋谷は別線化が進んだ例外的濃密域。
- **スクランブルは「点(信号ノード)+線(横断way)」で、面の歩行可能域は取れない**。対角同時横断の再現には横断wayを種に**自前で対角クロスリンクを補完**する必要(既存 `annual.gathering_node`=原点最近傍が集会点。social-force-crowd §4)。
- 縁石(kerb)ノードでの歩道⇔横断接続が未徹底の箇所=**グラフ連結性チェック必須**。駅ビル内部・地下街内部は欠測(§3-e)。

**含意(Phase 1)**: 渋谷中心なら**OSM/現行地図をベース歩行グラフにそのまま採用可能**(線は揃う)。精緻化は(i)幅員・横断・勾配属性の付与(§3-a歩行空間NW or PLATEAU道路LOD3から)、(ii)スクランブル/広場の面 or 対角リンク補完、(iii)駅・地下の欠測補完(§3-e)の3点に集約される。

- Overpass API(AGPL): <https://overpass-api.de/api/interpreter> / turbo: <https://overpass-turbo.eu/> / データ=OSM(ODbL)
- OSM Sidewalks手法: <https://wiki.openstreetmap.org/wiki/Sidewalks> / footway=crossing: <https://wiki.openstreetmap.org/wiki/Tag:footway=crossing>
- スクランブル議論: <https://community.openstreetmap.org/t/mapping-scramble-crossings/131845> / area:highway=pedestrian: <https://wiki.openstreetmap.org/wiki/Tag:area:highway=pedestrian>

### 3-c. CityGML/PLATEAU LOD2からのnavmesh生成 ★TINベースRecastが本命・律速は経路でなく高密度回避

**(1) Recast Navigation(業界標準・zlibライセンス)**: 任意の三角形メッシュ入力→**ボクセル化→非歩行領域除去→ポリゴン領域分割→再三角化でnavmesh自動生成**。構成: Recast(生成)/ Detour(実行時ロード・経路探索・空間クエリ)/ DetourTileCache(タイルストリーミング・動的障害物)/ **DetourCrowd(群集・衝突回避)**。Unity/Unreal/Godot/O3DEのAIナビの中核。
- ポート: **recast-navigation-js(MIT・WASM・Three.js統合・ブラウザ動作)**、recast4j(Java)、DotRecast(C#)。**RecastはzlibでプロジェクトのOSS方針と両立**。
- 生成器: <https://navmesh.isaacmason.com/>(ブラウザ)。

**(2) グリッド(占有格子)vs TINベースnavmesh**: PLATEAU地形は全データセットが **TINRelief(三角不規則網)**(`/udx/dem/`)で提供。**坂・立体交差の多い渋谷はTINベースnavmeshが有利**(占有格子は標高段差の扱いが弱い)。**PLATEAU地形TINをそのままRecast入力の地面に使い、建物LOD2でnavmeshに「穴(建物占有)」を開ける**のが素直な構成。※本プロジェクトは地形2m格子([`terrain.npz`](../../data/plateau/terrain.json))を抽出済み=Recast地面 or 双一次zサンプリングの両方に使える。

**(3) PLATEAU公式のnavmesh歩行者事例(重要な相場)**:
- **PLATEAU TOPIC36「避難シミュレーション」**(公式実装ガイド): 道路(tran)+接道PlaneにのみNavMesh Surface、**建物・地形はNavMesh Obstacle(歩行不可)**。AI Navigation + ML-Agents。避難者速度3.5m/s。**「エージェント数は50人程度を推奨、多いと重い」と明記**。<https://www.mlit.go.jp/plateau/learning/tpc36/>
- **UC22-023**: 歩行ネットワークを道路LOD1/LOD3外形線からPython+QGISで自動抽出(=**navmeshでなくリンク網**)、建物LOD2から視野情報を計算し経路選好に反映(§3-a/f)。
- **PLATEAU SDK-Toolkits for Unity(MIT・Sandbox Toolkit)**: 人/車/prop配置・交通シミュ機能。SDK本体v3.2.0betaで**横断歩道・車線・路面標示生成**対応=スクランブル対角動線の材料。<https://github.com/Project-PLATEAU/PLATEAU-SDK-Toolkits-for-Unity>

**(4) ランタイムコストと律速**:
- 経路探索は静的navmeshをオフライン生成→実行時ロードが定石。**単体A*≈1.2ms/回**、DetourCrowdは長距離探索を複数フレームに分割。マルチスレッドRecast A*で**1,000エージェント同時350+FPS**の実測(arXiv 2602.04130)。
- **律速は経路探索でなく高密度の局所回避(RVO/ORCA)**。渋谷スクランブル(1青3,000人)級の超高密度ではORCAが不安定化=**密度考慮の再計画・セル分割・連続体/場ベース群集の併用**が最大の技術課題(§3-d のFLAME GPU/warp路線、social-force-crowd §1.2の接触項に対応)。

**含意(本プロジェクト)**: navmeshは**全域には使わず**、案III(§4)の**前景の局所回避の歩行可能境界(壁斥力の代替)**として、スクランブル/駅前広場のオープンスペースにだけ生成する。生成はRecast(zlib)/recast-navigation-js(MIT)で建物LOD2+地形TINからオフライン一括。公式Unity/Unreal経路は50人規模想定なので、数千人規模は生Recast/Detour+DetourCrowd or SoA/GPU群集の自前運用が要る(=既存 `viz/sfm.py` の領域分割SFM昇格が本プロジェクトの最小コスト経路)。

- Recast(zlib): <https://github.com/recastnavigation/recastnavigation> / <https://recastnav.com/> / recast-navigation-js(MIT): <https://github.com/isaac-mason/recast-navigation-js>
- PLATEAU地形TIN解説: <https://zenn.dev/ozekik/articles/bf917b58f8ee89> / 公式terrain: <https://github.com/Project-PLATEAU/plateau-streaming-tutorial/blob/main/terrain/plateau-terrain-streaming.md>
- グリッドvs navmesh: <https://vav-labs.com/blog/godot-pathfinding-grid-vs-navmesh/> / Recast性能(arXiv): <https://arxiv.org/html/2602.04130>

### 3-d. 群衆マイクロモデルの計算コスト ★律速はLLM側・移動microは桁違いに安い

| モデル | ライセンス | コスト規模感 | 位置づけ |
|---|---|---|---|
| **Social Force**(Helbing&Molnár1995) | (自前実装 `viz/sfm.py` 済) | 素朴O(N²)→ cutoff+空間ハッシュで実効**O(N)**必須。CPU numpy+Numbaで **~10⁻⁶〜10⁻⁵ s/agent-step** | 密度依存の自然な流れ・レーン形成。**第一候補**(既存資産) |
| **ORCA / RVO2**(van den Berg) | **Apache-2.0**(snape/RVO2) | 数千体を数ms・kd-tree近傍で**O(N log N)**・OpenMP並列 | めり込み厳密回避。**補助**(詰まり耐性) |
| **SUMO striping**(Erdmann) | EPL-2.0 | 帯幅0.65mの離散近似で軽量 | **歩行者には不採用**(解像度粗・スクランブル不適=既決) |
| **GPUベクトル化(NVIDIA Warp)** | Apache-2.0 | **warpcrowd実測: 1万体×600step≈7s → ~1.2×10⁻⁷ s/agent-step** | 数十万規模の将来形 |

- **決定的な含意**: GPU SFMで **~10⁻⁷ s/agent-step**(10万体×1step≈12ms)。**歩行microのコストはLLM推論に比べ桁違いに小さく、律速はほぼ確実にLLM側**(million-scale §1 の結論と一致)。→ 前景を連続microにしても、**空間ハッシュでO(N)化 + SoAでベクトル化**すれば §5 の予算内。
- FLAME GPUは**65,000人超の群衆をリアルタイム実証**、数十万でも「性能が用途を阻害しない」= 数十万規模リアルタイム歩行は既に確立技術(GPU前提)。
- 出典: warpcrowd <https://github.com/cadop/warpcrowd> / RVO2 <https://github.com/snape/RVO2>(Apache-2.0) / PySocialForce <https://github.com/yuxiang-gao/PySocialForce> / SUMO歩行者 <https://sumo.dlr.de/docs/Simulation/Pedestrians.html> / FLAME GPU <https://flamegpu.com/citations/> / SFMレビュー(O(N²)vs O(N)) <https://arxiv.org/pdf/1609.01808>

### 3-e. 駅・地下の詳細データ(渋谷駅構内・乗換動線・ODPT・IMDF)★最難関

- **ODPTは駅構内の経路グラフ(乗換動線・コンコース・改札・ホーム)を提供していない**。提供は GTFS-JP・駅情報(`odpt:Station`)・駅施設情報(`odpt:StationFacility`=EV/トイレ等のメタ)・出入口相当(`ug:Poi`)・時刻表。**APIキー登録制(無料)** ※キー値は本書に不記載。ライセンスはデータセット毎に混在(基本ライセンス/チャレンジ限定/CC BY)で個別確認要。東京メトロ駅施設は2022-03以降更新停止。→ **ODPTは時間軸(時刻表・乗換所要・駅施設メタ)には有用だが、構内動線の空間グラフには使えない**。
- **国交省の屋内地図オープンデータ(階層別屋内地理空間情報データ仕様)**: 東京駅・新宿駅・新横浜・成田等は整備済みだが **渋谷駅は未整備**。**IMDF(Apple)形式の渋谷駅データも確認できず**(日本は独自仕様採用)。
- **代替の実データ(最有力)**:
  - **PLATEAU渋谷区2025 地下街モデル LOD1・4.1**(CC BY相当・再配布可)。
  - **3D City Experience Lab. の渋谷駅地下点群+3Dモデル**(東急東横/メトロ副都心ホーム周辺 350m×400m、点群PTS+OBJ ~437MB、**CC BY 4.0**): <https://3dcel.com/opendata/>。※通路中心線抽出の前処理が要る。
  - **歩行空間NWデータの「5:地下通路 / 7:施設内通路」リンク**(§3-a)+ 手持ちの [`floorguide_shibuya.json`](../../data/floorguide_shibuya.json)(駅・商業施設のフロア構成+接続)。
- **結論**: 渋谷駅の公式ベクター構内動線は**存在しない**。(a)歩行空間NWの地下/施設内リンク +(b)PLATEAU地下街LOD1 +(c)floorguide +(d)必要なら3dcel点群、を組み合わせて**自作**するしかない。Phase 1で floorguide + 地下街LOD1 の粗グラフから始め、精度が要れば点群を足す二段構え。
- 出典: ODPT <https://developer.odpt.org/> / ODPTカタログ <https://ckan.odpt.org/> / 国交省屋内地図 <https://www.mlit.go.jp/kokudoseisaku/kokudoseisaku_tk1_000108.html> / 3dcel <https://3dcel.com/opendata/> / 東京メトロ渋谷駅構内図(PDF) <https://www.tokyometro.jp/station/shibuya/yardmap/index_print.html>

### 3-f. 先行例(PLATEAU人流実証・LLM社会シミュの空間解像度)

- **PLATEAU人流実証**: uc22-023(西新宿・視野ベース経路選択)、uc25-07(横浜瀬谷・駅舎内外+ダイクストラ経路・**商用UC-win/Road拡張**)、uc24-07(**Moving Features JSON**=人流データ標準化)。**3D都市モデルから検証環境を自動生成**する枠組みが整備済み=本プロジェクトの環境自動生成(D2)方針と親和。ただし群衆モデルは経路選択中心で対人microコストの公表は薄い。
- **LLM社会シミュの空間解像度の相場(二極)**:
  - **小規模=タイルグリッド+意味ツリー**: Generative Agents/Smallville(Park 2023, 25体)。Phaser 2Dタイル+コリジョンマップ、世界=木構造(エリア→オブジェクト)、移動=pathfinding。座標は離散タイル。
  - **大規模=実地図(道路網+AOI/POI)+連続座標**: **AgentSociety(Tsinghua, 1万体超)**。OSM道路網+AOI+POI、**連続座標+離散時間で位置/速度/加速度を運動学更新**、徒歩=歩道を定速、Ray+MQTTで分散。GitHub <https://github.com/tsinghua-fib-lab/agentsociety/>。
  - → **渋谷×数万〜数十万なら(B)大規模型が相場**。ただしAgentSocietyの徒歩は「歩道を定速」で対人micro無し。**(B)のマクロ空間に SFM/ORCA のmicro回避層を重ねる二層構成**が最も整合(=本書の案IIIそのもの)。
- **日本の直近参照**: **KDDI×AWS(1万人超×GPUインスタンス×UE4)** <https://aws.amazon.com/jp/blogs/news/aws-example-of-massive-people-flow-simulation/>、日建の**渋谷駅避難シミュ** <https://note.com/nikken/n/ndd7242352da2>、東京都デジタルツイン(地下含むリアルタイム人流)。KDDI/AWS事例は本プロジェクトのハード/可視化構成(7GPU・UE)に最も近い。
- 出典: PLATEAU uc25-07 <https://www.mlit.go.jp/plateau/use-case/uc25-07/> / uc24-07(Moving Features) <https://www.mlit.go.jp/plateau/use-case/uc24-07/> / Generative Agents <https://arxiv.org/abs/2304.03442> / AgentSociety <https://arxiv.org/abs/2502.08691>

---

## 4. 推奨アーキテクチャ

### 4.1 3案の比較

| 案 | 概要 | 水平精度 | 垂直(z) | コスト適性 | R1/決定論 | 判定 |
|---|---|---|---|---|---|---|
| **(I) 層状歩行ネットワーク(グラフ拡張)** | 現行グラフに 歩道/横断歩道/地下/駅構内/階段リンク を足し、layer+z属性を付与。移動は現行`_phase_move`のまま | 中(リンク密度次第) | O(1)サンプリング | ◎(現行と同型・SoA化容易) | ◎(現行の延長) | **背景/中景の土台に採用** |
| **(II) navmesh(連続面)全面** | PLATEAU建物footprint+地形TINから歩行可能メッシュを生成し、全エージェントを連続座標で経路探索・回避 | 高 | 面から自然に出る | ✗(全数microは0.0002予算と両立不能・million-scale §1.3) | △(浮動小数・反復順の決定論設計が重い) | **全面採用は不可**。前景の局所だけ |
| **(III) 連続2.5D座標 + 層状グラフのハイブリッド** ★ | 大域=層状グラフ(案I)でルート決定、局所=前景/可視域だけ連続座標+SFM回避。zは全tier地形/レイヤーからサンプル | 前景=高 / 背景=中 | 全tial O(1) | ◎(前景少数のみmicro・背景SoA) | ◎(既存の案a/案b設計・OFFノブ文化と整合) | **推奨** |

### 4.2 推奨 = 案III(ハイブリッド)。層の定義

million-scale の3tier(前景FG / 中景MID / 背景BG)に**空間解像度**を重ねる:

| tier | 大域移動 | 局所移動 | z | 想定人数(25万同時中) |
|---|---|---|---|---|
| **前景FG**(観測対象+可視域) | 層状グラフでルート | **連続座標 + SFM局所回避**(`viz/sfm.py`昇格・すれ違い/レーン/横断待ち) | 地形+デッキ+階から連続サンプル | 1〜2万 |
| **中景MID** | 層状グラフでルート | エッジ弧長補間(現行`_phase_move`)+ **混雑を密度場から** | 地形サンプル | 8〜9万 |
| **背景BG** | 層状グラフ(SoA一括) | numpy SoAでノード間直線/弧長・**LLMなし・記録間引き** | 地形サンプル(SoAでgather) | 13〜15万 |

**設計原則**:
1. **zは移動計算に入れない**。水平(x,y)で移動を解き、zは表示・知覚・イベント時に `terrain.heights` の双一次補間 + `node.layer` のオフセット(デッキ+X m / 地下-Y m)+建物内は `floor×階高` で**後付けサンプリング**。これで垂直精度を上げても移動エンジンの単価は増えない(0.0002予算を守る鍵)。
2. **前景だけ連続microにする**。million-scale §1.3 の「支配は数の多い背景」に従い、背景を連続microにしない。前景1–2万×SFMサブステップは §3-d のコスト試算で成立域(領域内n数百規模)。
3. **層状グラフは全tier共通の一次ソース**。案IIのnavmeshは「前景の局所回避の歩行可能境界」としてのみ使う(壁斥力の代替=スクランブル/駅前広場のオープンスペース)。全域navmeshは作らない。
4. **既存の疎結合を壊さない**。sim本体はx,y(+新規z任意)を吐くだけ、ビューアは読むだけ。案a(オフライン合成)は据え置き、案b(オンラインSFM)を前景tierのOFFノブとして足す。

### 4.3 なぜnavmesh全面でないか / なぜグラフだけでないか

- **navmesh全面は予算違反**: 連続座標の経路探索(A* on navmesh)+ 局所回避を25万体毎stepは、§3-d のコスト(SFMで1e-6〜1e-5 s/agent-substep×サブステップ多数)から0.0002を数十〜数百倍超過。前景に限れば成立する。
- **グラフだけでは水平精度が頭打ち**: 現行は車道中心線グラフ主体で、歩道の幅・すれ違い・スクランブルの面的な流れが出ない。前景の連続座標化で「見た目と混雑の質」が上がり、研究側は真の瞬間密度(Fruin LOS)を観測量にできる(social-force-crowd §5.2)。
- **ハイブリッドは既決方針の自然な延長**: 「LLM=目的地/意図、群衆エンジン=物理」(engine-architecture §4)、「案a先行・案bはOFFノブ」(social-force-crowd §5.2)、「背景SoA」(million-scale W2-A)をそのまま3D軸へ拡張しただけで、新しい思想を持ち込まない。

---

## 5. LOD設計(0.0002予算の死守)

### 5.1 単価予算の割り当て

million-scale §1.3–1.4 の逆算(25万同時・144step/日)に空間解像度を載せる:

| tier | 移動様式 | 目標単価 s/agent-step | 支配コスト |
|---|---|---:|---|
| 前景FG(1–2万) | 連続座標+SFMサブステップ+z連続 | ~0.010(数が少ないので許容) | SFM全ペア(領域分割で有界化) |
| 中景MID(8–9万) | エッジ弧長補間+密度場混雑+zサンプル | ~0.002 | 現行`_phase_move`相当 |
| **背景BG(13–15万)** | **SoA一括: ノード進捗更新・在圏判定・zサンプルをnumpyでベクトル化** | **~0.0002** | numpy配列演算(gather/scatter) |

**背景BGの3D対応で単価が増えないことの担保**:
- 移動 = SoAの `offset += speed*dt` と `node` 遷移(現行スカラの配列版)。z非依存。
- z = 各stepの表示/知覚が要る分だけ `terrain.heights[j,i]`(格子index=`(x-x0)/cell`, `(y-y0)/cell`)を**一括gather**。双一次補間もnumpyベクトルで一括。**移動ループの外**で、しかも記録間引き対象。
- layerオフセット(デッキ/地下)は `node.layer` のLUT参照(整数→float加算)を一括。

### 5.2 前景の局所microのコスト有界化

- **領域分割**: SFMの全ペアO(n²)はスクランブル/駅前広場/主要交差点ごとの**独立セル**に区切り、セル内のみ相互作用(social-force-crowd §4 のTransiTUM遷移帯)。1セルn=数十〜低百なら §3-d の実測レンジで軽い。
- **サブステップ**: dt=0.1s×600s=6000サブステップは重い→ **可視域(カメラ視錐台)内 or 混雑イベント発火セルのみ**オンラインSFM、それ以外の前景はエッジ補間+密度混雑で足りる。million-scale の「全員思考」に対応する「注目領域だけ連続micro」。
- **決定論**: SFM揺らぎξを `hub.stream("sfm3d", cell, step)` に束ね、反復順・浮動小数総和順を固定(social-force-crowd §5.2 のOPEN条件を踏襲)。既定OFF・ONは別ゴールデン。

### 5.3 R1(k*非交絡)の維持

- 3D精緻化は**観測解像度の向上**であって個体の内部状態・信念・kに触れない(million-scale §2.2 の原則)。zや連続座標は**プロンプトに注入しない**(no-fingerprint)。tier割当は既存の `stream("tier")` k非依存決定論をそのまま使う。
- 混雑を連続密度で測ってgrievance/driveに繋ぐ場合は**別ゴールデン+研究設計判断**(social-force-crowd §5.2・engine-architecture の「意味が重い」問題)。既定は純観測(現行の `_phase_move` 混雑→driveは維持、連続密度は観測量として並記)。

---

## 6. ビューアへの反映(見え方の改善)

現状「ノード間補間+地形ドレープ」から、tier別に段階改善:

| 改善 | 現状 | 改善後 | 実装面 |
|---|---|---|---|
| **接地z** | `groundAt(x,y)+1.1`(既実装) | デッキ/地下/階のlayer-zを反映(地下歩行者は地表下、デッキは+X m) | `make_viewer3d.py` の高さ関数に `agent.layer/floor` を渡す。sim側zを吐けば補間不要 |
| **歩道上の左右** | 中心線上を1点で移動 | 歩道幅内でのオフセット(進行方向法線に±) | 前景=SFM座標そのまま。中景=幅内ジッタの決定論版 |
| **横断歩道の待ち** | 素通り | 信号連動の停止・青で一斉横断(スクランブル) | 前景のみ。SFM目標を信号状態でゲート(ShibuyaSocialのsigmoid信号と同型・social-force-crowd §3.2) |
| **駅構内/地下の動線** | 駅ノードで瞬間移動(traffic-signals-audit) | 構内リンクに沿って移動(データがあれば・§3-e) | 層状グラフに構内リンクを足すだけで既存補間が効く |
| **群れ・レーン形成** | 無し | スクランブルで自己組織化(既に案aで実証) | 前景オンラインSFM or 案a拡張 |

**疎結合の維持**: 上記はすべて `scene.json`/`tracks.json` 契約(3d-visualization §4.3)を壊さず、**キー追加のみ**(例: `move_segment` に `z`/`layer` 追加、前景セルに `crowd_micro` トラック追加)。既存 viewer3d/UE/Blender は無改変で従来動作。

---

## 7. 実装フェーズ分割

各フェーズ = 内容 / 対象ファイル / 工数(小=数日 / 中=1-2週 / 大=数週)/ 依存 / R1安全性。すべて `pre-coding-alignment`・`ask-before-extending` に従いユーザー合意後に着手。

### Phase 0 — 垂直z化(安い・独立に効く)★最初にやる価値大 → **実装済み(2026-07-20)**
> `src/society/world/elevation.py`(DEM 双一次・export_3d と同値・1.5µs/サンプル)+ `world.elevation.enabled`(既定 OFF)で
> move_segment/arrive payload に z を追加。実地形サニティ=原点0m・東西の坂で上り。tests/test_elevation.py 8本。
> ビューアは従来どおり terrain_web ドレープ(同一 DEM=描画は同値)。sim由来 z の直接消費は Phase 4 で。
- **内容**: エージェントに任意zを持たせる(既定は表示専用=移動非依存)。stepごと(or 記録時)に `terrain.heights` 双一次補間 + `layer`/`floor` オフセットでzを算出し、`move_segment`/`arrive` payloadに `z`(と `layer`)を足す。ビューアはドレープをやめsim由来zを使う。
- **対象**: [`scheduler.py`](../../src/society/engine/scheduler.py)(z算出ヘルパ・payload追加)/ 新規 `world/elevation.py`(terrain.npz読取+双一次補間+layer LUT)/ [`make_viewer3d.py`](../../viz/make_viewer3d.py)(z入力経路)。
- **工数**: **小(数日)**。terrain.npz は抽出済み。R1: payloadキー追加は新規=既定OFFなら従来とバイト一致で足せる。
- **やらないと**: 「垂直3D」が描画のドレープ止まりで、地下・デッキ・階の高さがsimの観測・イベントに乗らない。

### Phase 1 — 層状歩行ネットワークの構築(水平精緻化の一次データ)
- **内容**: 現行グラフに 歩道(footway)/横断歩道(crossing)/階段(steps)/EV/地下通路(ubld由来)/駅構内リンク を足し、各エッジ/ノードに `layer`・`z`・`width`・`grade` 属性を付与。データ源の優先順は §3-a/b/e の入手性で確定(第一候補: 国交省歩行空間NW→無ければOSM footway+PLATEAU tran+手持ち floorguide)。
- **対象**: [`scripts/build_map.py`](../../scripts/build_map.py)拡張(歩行者レイヤ取込)/ 新規 `scripts/build_walk_network.py`(歩行空間NW/OSM footwayのマージ)/ [`data/shibuya_osm_wide_v7.json`](../../data/) の後継 or サイドカー。
- **工数**: **中〜大**(データ入手性次第。歩行空間NWが渋谷に整備済みなら中、無くOSM+手動なら大)。R1: 地図差し替えはゴールデン再取得(EnvPack同一性検収の作法・devlog)。
- **やらないと**: 移動が車道中心線のままで、歩道・横断・地下・構内の水平精度が上がらない。

### Phase 2 — 背景BGのSoA化 + z一括サンプリング(予算の器)
- **内容**: 背景個体を numpy 構造体配列(x/y/node/offset/schedule_id/present/layer)へ。move/在圏/zサンプルを全背景一括ベクトル演算。million-scale W2-A と**同一の器**に3Dサンプリングを相乗り。
- **対象**: 新規 `world/background.py`(SoA)/ [`scheduler.py`](../../src/society/engine/scheduler.py) tier分岐 / [`traffic.py`](../../src/society/world/traffic.py) の車ループもSoA化(同型)。
- **工数**: **大**(million-scale W2-A本体)。R1: 前景と同じ物理則の二重実装に注意(SoA↔OO境界)。**本番プロファイルで c を実測**して0.0002級を確認。
- **やらないと**: 25万規模で背景の移動+zが単価を超過し、3D化が「回らない」。

### Phase 3 — 前景の連続座標 + 局所回避(SFM昇格・オンライン)
- **内容**: [`viz/sfm.py`](../../viz/sfm.py) の Crowd を可視域/混雑セルの前景に接続(案b・OFFノブ `crowd.sfm3d.enabled=false`)。大域=層状グラフでルート→局所=セル内SFMで足の運び。横断歩道の信号ゲート。navmesh(§3-c)を壁斥力境界に使う。
- **対象**: 新規 `world/crowd_micro.py`(領域分割SFMドライバ)/ [`scheduler.py`](../../src/society/engine/scheduler.py) `_phase_move` の前景分岐 / `viz/sfm.py`(壁斥力・信号ゲート追加)。
- **工数**: **中〜大**(social-force-crowd 案b + 領域分割 + 決定論設計)。R1: 既定OFF・別ゴールデン・ξをhub.streamへ。
- **やらないと**: 前景の見た目と混雑の質が中景と同じ(すれ違い・レーン・横断待ちが出ない)。※視覚だけなら案a(オフライン合成・既実装)で代替可。

### Phase 4 — ビューア反映 + 検証
- **内容**: §6 の見え方改善をtier別に配線。前景=crowd_microトラック、中景=幅内オフセット、全tier=layer-z接地。Fruin LOS の真密度列を [`analyze_flows_grid.py`](../../scripts/analyze_flows_grid.py) に追加(読取専用)。
- **対象**: [`make_viewer3d.py`](../../viz/make_viewer3d.py) / [`export_3d.py`](../../scripts/export_3d.py) / [`viz/unreal/`](../../viz/unreal/)(UE経路)。
- **工数**: **中**。R1: ビューアは下流=無風。
- **やらないと**: sim側で精緻化しても観察・研究に反映されない。

### 着手順の推奨
1. **Phase 0(z化)** — 独立・安い・即座に「3Dらしさ」が出る。データ入手を待たずに着手可。
2. **Phase 1(歩行NW)と §3-a/b/e のデータ入手を並行** — 入手性で規模が決まる。
3. **Phase 2(背景SoA)** — million-scale W2-Aと合流(3Dのためだけに前倒しはしない。scale計画に相乗り)。
4. **Phase 3(前景SFM)** — 視覚要件が固まってから。急がば案a据え置き。
5. **Phase 4(ビューア)** — 随時並行。

---

## 8. データ取得リスト(URL・ライセンス・再配布可否)

> シークレット記載禁止。ODPT等の登録制APIは「登録が必要」の事実のみ記す。

| データ | 用途(Phase) | 入手元 | ライセンス | 再配布 | 状態 |
|---|---|---|---|---|---|
| PLATEAU 渋谷区2025(建物LOD2/地形DEM/地下街ubld/橋brid) | z化・navmesh(0,1,3) | G空間 `plateau-13113-shibuya-ku-2025` | PLATEAU Site Policy(CC BY相当・商用可・翻案自由) | 可 | **抽出済み**([`data/plateau/`](../../data/plateau/)) |
| PLATEAU 渋谷区2025 **道路LOD3(歩道分離)+地下街LOD1・4.1** | 歩行NW(1) | 同上パッケージ(tran/地下街) | PLATEAU Site Policy | 可 | **未抽出**(uc22-023/uc24-01に自動生成前例) |
| 国交省 **歩行空間NWデータ 渋谷地区/渋谷南部** | 歩行NW(1) | G空間 `dataset/0401` | **政府標準利用規約2.0(CC BY互換)** | 可(出典表示) | 実在・**ただし2017年版=再開発未反映** |
| OSM 渋谷(footway/crossing/steps) | 歩行NW(1) | Overpass/`build_map.py` | ODbL(出典表示・継承) | 継承条件つき可 | 一部取込済(車道中心)・被覆は§3-b |
| floorguide_shibuya.json(駅/商業施設フロア構成+接続) | 構内動線(1) | 手動調査 | 概略・事実に限定 | — | **手持ち**([`data/floorguide_shibuya.json`](../../data/floorguide_shibuya.json)) |
| 3dcel 渋谷駅地下 点群+OBJ(東横/副都心ホーム周辺) | 構内動線(1,3・任意) | <https://3dcel.com/opendata/> | **CC BY 4.0** | 可(出典表示) | 未取得・要中心線抽出 |
| ODPT(GTFS-JP/駅施設メタ) | 乗換の時間軸(既存transit) | `developer.odpt.org`(登録制・無料) | データ毎に混在(要個別確認) | 条件付 | 一部取得済([`data/odpt/`](../../data/odpt/))・**構内動線グラフは無し** |
| 駅構内ベクター動線 | 構内連続ナビ(1,3) | **公式未整備**(構内図PDF/点群から自作) | — | — | 要自作(floorguide+地下街LOD1から) |

---

## 9. 掟の遵守・既存文書との整合

- **出典URL明記・シークレット禁止**: §3/§8 に反映(APIキー等は不記載)。
- **コード変更/コミット禁止**: 本書はリサーチ+計画のみ。実装は §7 の合意後。
- **既存文書と非矛盾**:
  - `sumo-integration-research.md` / `traffic-signals-audit.md` / `engine-architecture.md` — **SUMOは車限定・歩行者はSFM**。本書は歩行者物理をSocial Force系に限定し、SUMOを歩行者に持ち込まない(整合)。
  - `social-force-crowd.md` — 案a先行・案bはOFFノブ。本書のPhase 3は案bの前景tier拡張として位置づけ(整合)。既存 `viz/sfm.py`/`synth_crowd.py` を昇格利用。
  - `million-scale.md` — 0.0002背景SoA予算・「全員思考」。本書はz化を移動計算外のO(1)サンプリングにして予算を守り、Phase 2をW2-Aに相乗り(整合)。
  - `3d-visualization.md` — PLATEAU入手・座標系(local-m原点=スクランブル・EPSG:6677)・scene.json契約。本書はこの座標系と契約を踏襲しキー追加のみ(整合)。
- **MEMORY方針との整合**: realism-first(現実渋谷の忠実再現・人数>時間)= 層状NWと駅構内動線は現実忠実度に直結。nature-like-systems(ボトムアップ)= SFMの自己組織化(レーン形成)はボトムアップ創発と同系。ask-before-extending / pre-coding-alignment = 実装着手前に決定アジェンダをユーザーへ。

---

## 10. Sources

（Web調査の一次URL。アクセス2026-07-20。既存リポジトリ文書は本文中に相対リンク。）

**歩行空間ネットワーク / PLATEAU**
- 国交省 歩行空間NW整備仕様(2024.7): <https://www.mlit.go.jp/sogoseisaku/soukou/sogoseisaku_soukou_tk_000056.html> / PDF <https://www.mlit.go.jp/sogoseisaku/soukou/content/001757259.pdf>
- G空間 歩行空間NWデータ(渋谷地区含む): <https://www.geospatial.jp/ckan/dataset/0401>
- PLATEAU 渋谷区2025: <https://www.geospatial.jp/ckan/dataset/plateau-13113-shibuya-ku-2025>
- PLATEAU uc22-023(西新宿・歩行NW自動抽出): <https://www.mlit.go.jp/plateau/use-case/uc22-023/> / uc24-01(道路網自動生成): <https://www.mlit.go.jp/plateau/use-case/uc24-01/> / uc25-07: <https://www.mlit.go.jp/plateau/use-case/uc25-07/> / uc24-07(Moving Features): <https://www.mlit.go.jp/plateau/use-case/uc24-07/>

**群衆マイクロモデル / コスト**
- warpcrowd(GPU SFM・~1.2e-7 s/agent-step): <https://github.com/cadop/warpcrowd> / RVO2(Apache-2.0): <https://github.com/snape/RVO2> / PySocialForce: <https://github.com/yuxiang-gao/PySocialForce>
- SUMO歩行者(striping): <https://sumo.dlr.de/docs/Simulation/Pedestrians.html> / FLAME GPU(65k人): <https://flamegpu.com/citations/> / SFMレビュー: <https://arxiv.org/pdf/1609.01808>

**駅・地下 / 屋内**
- ODPT開発者: <https://developer.odpt.org/> / カタログ <https://ckan.odpt.org/>
- 国交省 屋内地図オープンデータ(渋谷駅は未整備): <https://www.mlit.go.jp/kokudoseisaku/kokudoseisaku_tk1_000108.html>
- 3D City Experience Lab. 渋谷駅地下点群(CC BY 4.0): <https://3dcel.com/opendata/>

**LLM社会シミュの空間解像度 / 日本の人流**
- Generative Agents: <https://arxiv.org/abs/2304.03442> / AgentSociety: <https://arxiv.org/abs/2502.08691> / <https://github.com/tsinghua-fib-lab/agentsociety/>
- KDDI×AWS(1万人×GPU×UE4): <https://aws.amazon.com/jp/blogs/news/aws-example-of-massive-people-flow-simulation/> / 日建 渋谷駅避難: <https://note.com/nikken/n/ndd7242352da2>

**OSM被覆 / navmesh**
- Overpass API(AGPL・データODbL): <https://overpass-api.de/api/interpreter> / turbo <https://overpass-turbo.eu/> / OSM Sidewalks <https://wiki.openstreetmap.org/wiki/Sidewalks> / scramble議論 <https://community.openstreetmap.org/t/mapping-scramble-crossings/131845>
- Recast Navigation(zlib): <https://github.com/recastnavigation/recastnavigation> / recast-navigation-js(MIT) <https://github.com/isaac-mason/recast-navigation-js> / PLATEAU TOPIC36(避難・NavMesh) <https://www.mlit.go.jp/plateau/learning/tpc36/> / SDK-Toolkits(MIT) <https://github.com/Project-PLATEAU/PLATEAU-SDK-Toolkits-for-Unity> / Recast性能 <https://arxiv.org/html/2602.04130>
