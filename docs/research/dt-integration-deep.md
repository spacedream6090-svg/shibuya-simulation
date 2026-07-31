# 企業DT / 3Dシミュレーション × 社会シムの結合経路 — 技術深掘り(リポ照合つき)

作成 2026-07-30 / 調査サブエージェント。読み取り+Web のみ・リポ変更ゼロ。
リポ言及は `file:line`、Web 主張は URL、確認できなかったものは **UNVERIFIED** と明記する。

日程前提: 本選 8/15-8/30(10日連続ラン 8/16-26・提出 8/30)。9月以降が本番の拡張期。
レーン定義は `C:\Users\塚本翔太\Desktop\shibuya-simulation\docs\plans\twin-physics-vision-affordance-plan.md` §2 に従う
(レーン1=本選前 / レーン2=本選中・原則コード凍結・L1を読むだけの観測系のみ / レーン3=本選後)。

---

## 0. 結論を先に(推奨順位)

| 順位 | 経路 | いつ | 工数 | プレゼン映え | 研究価値 | ひとこと |
|---|---|---|---:|---|---|---|
| **1** | **P0 軌跡バイナリ化**(前提工事・下記いずれの3D経路にも効く) | レーン1 | 1.5-2日 | ★☆☆(単体では無) | ★★☆(10日ランの再生可能性そのもの) | **10日ランは現行 tracks.json では再生できない**(実測根拠 §1.3)。全経路の共通ボトルネック |
| **2** | **P6 追いかけ再生**(part-N を読む二次観測) | レーン1(仕込み)→2(運用) | 1-1.5日 | ★★★(「ライブに見える」) | ★★☆(10日ランの監視=運用価値) | 既存 `l1_events.part-NNNN.parquet` を読むだけ。ドクトリン完全無傷 |
| **3** | **P5 SUMO 反実仮想の交通DT化** | レーン3(骨格はレーン1可) | 2-3日 | ★★☆ | ★★★(A系 H_B の入力を実測化) | 既存 SUMO 全段完走+ライブ連成の資産が最大。`world.mod.edge_speed_scale` の原点を SUMO が供給する |
| **4** | **P1 Cesium/3D Tiles** | レーン3 | 2-4日 | ★★★ | ★☆☆ | **自己完結 file:// を捨てる**判断が要る(過去に明示棄却済み・§2.4) |
| **5** | **P2 UE5 リプレイ** | レーン3(提出動画だけならレーン2末) | 5-7日+UE学習(**狭い道限定**) | ★★★★ | ★☆☆ | 設計・書き出しは完成済み・**UE 実機検証ゼロ**。**バージョン三竦みが最大の罠**(§3B.2) |
| **6** | **P7 人流同化(較正フェーズ限定)** | レーン3 | 2-3日 | ★☆☆ | ★★★ | 「企業DTのセンサー同化」を**較正にだけ**入れる。本体決定論は無傷 |
| **7** | **P4 の USD 書き出しだけ**(Omniverse 抜き) | レーン3 | 1.5-2日 | ★★☆ | ★☆☆ | 「企業DTに繋がる」の**最も安く最も正直な実弾**(§5.7) |
| **却下** | **P3 Unity+PLATEAU SDK** | — | — | ★☆☆ | — | **歩道を SDK が export しない**ことが判明(§4.2)。官製の Unity 非依存代替が 2 つある(§4.4/§4.6) |
| **却下** | **P4 の Omniverse / Isaac Sim 本体** | — | — | ★★☆ | ★☆☆ | **本選中は GPU 余剰ゼロ**(vLLM が 7 基を 200時間占有)+ 画素非決定が決定論ドクトリンと衝突(§5.5) |

意外な発見(先出し):
1. **10日ランの3D再生は現行パイプラインでは物理的に無理**。10,000体×1日 で `tracks.json` 65.8MB / `viewer3d.html` **90.4MB(既に 80MB ゲート超過)**。10日は単純外挿で ~660MB / ~900MB(§1.3)。UE 経路も同じで `sim_ue.json` は **10,000体×10日 ≈ 9.8GB**(§1.2)。**3D の話をする前にここが折れる**。
   **【訂正 2026-07-31・第76バッチ実測】** §1.2 の基準ラン `demo_event_200a3d` は 200体×**432step**(本文の 144step は誤り)のため 684 B/agent-step は**3倍過大**。実測は 228 B/agent-step(1万体スケールでは 61.7 B)で、**10日 JSON は ≈0.89GB**。「JSON では不可能」という結論は不変。P0 実装後はバイナリで **viewer3d.html 24.7MiB(ラン長非依存)/ sim_ue 0.23GB**。
2. **「ライブっぽさ」はもう配線されている**。`ObserverLogger.flush_segment()` が checkpoint 毎に `l1_events.part-NNNN.parquet` を書き、finalize で結合して消す(`src/society/observer/logger.py:116-131,155-177`)。ラン中にこの part を読むだけで、シムに指一本触れずに「追いかけ再生」が成立する(§7.3)。
3. **GPU レンダは決定論と非互換、という判断が既にリポに刻まれている**(`viz/render_pov.py:1-16`)。Isaac Sim を研究主経路に置けない理由は外部事情ではなく**自分の設計原則**である。加えて **Isaac Sim 6.0 は「RT コアの無い GPU(A100, H100)は非対応」と公式に明記**(§5.5)。
4. **SUMO 側に「交通DT」の材料が既に全部ある**(net 5,575エッジ・OD・fcd・**実 SUMO 同 seed バイト一致のライブ連成**)。P5 は新規実装ではなく「既存 2 本の配線」に近い。しかも **CARLA↔SUMO の TraCI ロックステップこそが交通DTの業界標準パターン**で、我々は既にそれをやっている(§5.7)。
5. **PLATEAU SDK for Unity は歩道を内部で持っているのに export しない**(`RnSideWalk` は API にあるが、GeoJSON export は車線のみ)。代わりに **官製・Unity 非依存の `PLATEAU-RoadNetwork-Generator`(C++・車道+歩道ネットワークを Shapefile/GeoJSON 出力)** と、**渋谷区を含む既製の「歩行空間ネットワークデータ」** が存在する(§4.4/§4.6)。
6. **社会的エージェント状態を交換する標準は世界のどこにも無い**(USD/IFC/CityGML/3D Tiles/DTDL/FMI のいずれにも信念・関係のスキーマは無い)。**幾何と軌跡は相互運用できるが意味論はできない** — この非対称性を正確に言うことが、DT を名乗るより強い(§5.7)。
7. **Omniverse は 2026-05 に本番利用も含めて無償化された**(従来 $4,500/GPU/年)。それでも我々が使う理由にはならない(§5.4)。
8. **UE5 経路には解けないバージョン三竦みがある**: PLATEAU SDK for Unreal は **UE 5.5.4 のみ対応で 14ヶ月休止中**、City Sample の群衆は **5.6+ のパッチが要り 5.7 では壊れている**、MetaHuman Crowd は **5.8 で Experimental**。**「PLATEAU + City Sample 群衆 + 外部軌跡」は単一バージョンで成立しない**(§3B.2)。回避路は **PLATEAU の FBX 版**か **Cesium for Unreal + Cesium ion の Japan 3D Buildings**(§3B.4)。
9. **`SimReplayActor_DESIGN.md` の Tick 駆動設計は Movie Render Queue で壊れる**。MRQ は temporal サンプルごとにエンジンを tick するため、**サンプル数 8 なら 8倍速で再生される**(既知バグ)。対策は Sequencer プロパティトラック駆動 or Temporal Samples=1(§3B.7)。**着手前に設計書へ追記すべき既知バグ**。
10. **City Sample のライセンスは「UE でレンダした非インタラクティブ動画」を明示的に許可している**(§3B.8)。つまり**提出動画に使うこと自体は問題ない** — 問題はバージョンと工数の方。
11. **PLATEAU SDK は Unreal 版だけが放置されている**。Unity 版は 2026年も活発(v4.3.0・2026-06-29)。にもかかわらず **Unity 版は歩道を export しない**(§4.2)。**どちらの SDK も、我々の用途にはそのままでは使えない。**

---

## 1. リポ既存 3D/DT 資産の実査

### 1.1 Web 3D 再生(完成・本命)

| 資産 | 実体 | 状態 |
|---|---|---|
| `scripts/export_3d.py`(902行) | L1 → 中立3Dシーン。`scene.json`/`tracks.json`/`buildings.glb`(**手書き glTF 2.0 バイナリ**・`build_glb` at `scripts/export_3d.py:422`)/`plateau_web.json` | 完成。`--plateau`・`--rich-tracks`・`--low-mem`・`--sample-agents N`・`--step-stride K` |
| `viz/make_viewer3d.py`(1,624行) | three.js **r128 完全ベンダリング**(`viz/vendor/three.min.js` + `OrbitControls.js` + `LICENSE`)の自己完結 HTML。PLATEAU 実形状・地形・地下街/橋・屋内プレート・顕著イベントジャンプ・昼夜太陽 | 完成。**Cesium 不使用**(`viz/make_viewer3d.py:5`) |
| `data/plateau/` | `plateau_mesh.npz`(V 1,107,132 / F 590,670 / 6,311棟)・`plateau_index.json`・`terrain.npz`(921×1088・2m格子)・`extras.npz`(地下街/橋)・`plateau_match.json`(matches 3,531 / IoU≥0.4) | 完成。**2025年度版 CityGML から生成済み**(`docs/research/plateau-2025-update-notes.md:14-22`) |

**設計の掟**: パイプラインは `CityGML → data/plateau/ → scene3d/ → viewer3d.html` の**一方向・sim 非依存**。
シム本体が `data/plateau/` を読むのは `world/elevation.py` 経由の `terrain.npz` 1 箇所だけで、既定 OFF・「表示/観測専用」宣言つき(`docs/research/plateau-2025-update-notes.md:36`)。

### 1.2 UE5 リプレイ(**設計完成・実装ゼロ**)

- `scripts/export_ue.py`(239行): `scene3d` → `sim_ue.json`。**座標変換を Python に一本化**して UE 側を素直な再生器に保つ設計(`scripts/export_ue.py:12-17`)。
  - sim(ENU・m・右手系・原点=スクランブル交差点 35.6595/139.70062)→ UE(cm・Z-up・左手系)。
  - `ORIGIN_EPSG6677 = {northing_m: -37768.576, easting_m: -12015.952}`(`scripts/export_ue.py:49`)。PLATEAU SDK のインポート時オフセットにこの値を入れると **PLATEAU 原点=スクランブル交差点=sim 原点**になり `--offset 0 0 0` のままで合う(`viz/unreal/README_UE.md:90-104`)。
  - `--heading {0,90,180,270}` × `--no-yflip` の 8 通りのどれかで必ず合う(アフィン変換だから)。**初回だけエディタで実測合わせ**が前提(`viz/unreal/README_UE.md:106-113`)。
- `viz/unreal/import_shibuya_sim.py`(13.6KB): UE エディタ内 Python。`mode="ism"`(人 ISM + 車 ISM を持つ `ShibuyaSimReplay` アクタ配置 + JSON を `Content/ShibuyaSim/` へコピー)/ `mode="sequence"`(≤300体・1体=1アクタ+Level Sequence ベイク)。
- `viz/unreal/SimReplayActor_DESIGN.md`(9.6KB): BeginPlay で JSON を `FSimData` へ一括展開 → 毎 tick `BatchUpdateInstancesTransforms` で ISM 一括更新 → `sim_min` から SunSky 駆動。C++/BP 両ルートの擬似コードあり。
- **正直な現状**: `viz/unreal/README_UE.md:10` に「⚠ この手順は UE 実機で未検証(開発環境に UE 無し)」、`SimReplayActor_DESIGN.md:8` に「この環境に UE が無いため実装は未検証」。§6「実機での検証項目(未検証)」に 5 項目が列挙されている。
  **= 書き出し側は動くが、UE 側は 1 行も書かれていない/1 度も動いていない。**
- **書き出し側は実際に走っている**(実測): `runs/demo_event_200a3d/scene3d/sim_ue.json` **19.7 MB**(200体×144step)、`runs/eco80_3day/scene3d/sim_ue.json` **10.1 MB** + `sim_ue.csv` 1.15 MB(80体×3日)。
  → **1 agent-step あたり ≈ 684 B**。**10,000体×10日 = 14.4M agent-step ≈ 9.8 GB** の JSON。`FJsonSerializer` に食わせる話にならない。**P0(バイナリ化)は UE 経路でも必須**。
  **【訂正 2026-07-31】** 基準ランは 200体×**432step**(144 は誤記)なので正しくは **228 B/agent-step・10日 ≈ 0.89GB**(1万体実測 61.7 B/agent-step)。結論(バイナリ化必須)は不変。
- **テストが無い**: `tests/` に `export_ue` / `sim_ue` を参照するテストはゼロ(`test_export3d.py` のみ)。
- **人・車は `/Engine/BasicShapes` のシリンダとキューブ**(`viz/unreal/import_shibuya_sim.py:38-45`)。City Sample の群衆アセットや MetaHuman は**一切使っていない**。README_UE の「フォトリアル」は **PLATEAU 建物 + Lumen の話**であって群衆の話ではない。

### 1.3 ★ 規模の実測(全経路を規定する最重要の数字)

`runs/` の実測(`ls -la`):

| ラン | 規模 | `l1_events.parquet` | `tracks.json` | `viewer3d.html` |
|---|---|---:|---:|---:|
| `eco80v2` | 80体×1日 | — | 2.6 MB | 3.7 MB |
| `demo_event_200a3d` | 200体 | — | 15.4 MB | 39.9 MB |
| `mem100` | 100体×100日 | — | **223 MB** | 4.4 MB(traffic 除去版と推定) |
| `exp_llm_100d` | 100日 | 46 MB | **382 MB** | (無し) |
| **`rehearsal_pool10k`** | **10,000体×1日** | **174.9 MB** | **65.8 MB** | **90.4 MB**(lite 71.5MB + `plateau_mesh.js` 別) |

- `make_viewer3d.py:912` に **80MB ゲート**の警告が実装済み。`rehearsal_pool10k` は **90.4MB で既に超過**している。
- 本選候補の「present 1万体×10日」を線形外挿すると `tracks.json` ≈ **660 MB** / 自己完結 HTML ≈ **900 MB**。
  → **ブラウザに載らない。JSON.parse の前にメモリで死ぬ。**
- 逃げ道は既にある(`--sample-agents` / `--step-stride`)が、それは「10日ランを見せない」ことと同義。

**この節が §2 の P0 提案の根拠。**

### 1.4 SUMO 連成(v0 全段完走 + ライブ連成 GO)

- `scripts/sumo_pipeline.py`(823行): `check → net → demand → run → convert` の 5 stage。
  - `net`: 生 OSM XML → `netconvert --lefthand`・車道のみ・`--tls.guess-signals --tls.join --tls.discard-simple --tls.default-type actuated`・seed 固定(`scripts/sumo_pipeline.py:539-540`)。**`tlLogic` 件数を stdout に出す**(`:549-551`)。
  - `demand`: `analyze_od.py` の `od_matrix.parquet` → TAZ + tazRelation → `od2trips` → `duarouter`。
  - `run`: `sumo --seed 固定 --step-length 1.0 --fcd-output.geo`(`:662-664`)。
  - `convert`: fcd(経緯度)→ ローカル m → 600s 窓 → `panel/sumo_traffic.parquet` + `sumo_traffic_segs.json`。**元の tracks.json は変更しない**。
  - 実績(devlog E24): 「**SUMO v0全段完走**(公式1.27.1・net 5,575エッジ→OD 6,460台→24h fcd→144step parquet)」(`docs/log/devlog-compressed.md:146`)。
- `scripts/sumo_taxi_bridge.py`(230行)+ `src/society/transit_live.py`: **ハイブリッド・ライブ連成**。TraCI で予約注入 → 決定論配車 → `picked_up`/`dropped_off` の実秒を返す片方向委譲。
  - go/no-go 実測(`runs/bench_taxi_live/bench_taxi_live.md`): **LLM 呼数 k 不変 PASS(free=67 off=67)**・**実 SUMO 同 seed バイト一致 PASS**・wall start 0.82s / max-req 3.28s・Windows 完走 PASS。
  - 決定論の作り方が明記(`scripts/sumo_taxi_bridge.py:12-19`): seed 固定・`--random` 禁止・`--threads 1`(並列ルーティング禁止)・taxi fleet はソート済みエッジ id への決定論配置・配車は id 昇順空車への逐次 `dispatchTaxi`。
- **正直な限界(リポが自認)**: 信号推定も OD も近似で「**渋谷の実測交通の再現ではない**」、OD は mode 非分離で全トリップを車需要の代理にしている(`scripts/sumo_pipeline.py:46-50`)。

### 1.5 環境改変条件 `world.mod`(A1・第67バッチ・既定 OFF)

`src/society/world/worldmod.py`(266行)+ `conf/config.yaml:217-236`。**ワールド構築時に一度だけ・決定論・乱数ゼロ**で適用する静的改変層(`scenario.shock_closure` の一般化)。

| 改変 | 状態 |
|---|---|
| `edges_closed` | **実効**(routing が迂回) |
| `edge_speed_scale` | **実効**(走行コスト長へ写して経路選択と所要 step の双方に効く・`CityMap.scale_edge_cost`)。歩道幅の代理 |
| `open_hours.cats` | **実効**(cat 単位) |
| `open_hours.pois` | ★**予約フィールド=未消費** |
| `gate_capacity` | ★**予約フィールド=未消費**(現行エンジンに改札容量の概念が無い) |

**P5 の接続点はここ**(§6)。`edge_speed_scale` は「係数」だが**原点(実測 1.0)が測れていない**と計画書が自認している(`docs/research/plateau-2025-update-notes.md:146-147`)。

### 1.6 観測ドクトリン(全提案が守るべき制約)

- **「観測がシムを変えない」**: 再生専用ツールは 60 本が「L1 を読むだけ」の疎結合パターン(`docs/plans/twin-physics-vision-affordance-plan.md:66`)。
- **ゴールデン不変**: `tests/data/golden_baseline_l1.json`(1,711イベント)は**再生成の前例ゼロ**(同 §1.3)。
- **既定 OFF + 専用 stream(or always-draw 再利用)**、L1 バイト一致・draw 数同一が全バッチの検収条件。
- **GPU レンダは決定論と非互換**という判断が明文化されている: 「GPU レンダは画素非決定(FMA/丸め/加算順がハード依存)で決定論と相性が悪い。ここは **CPU ソフトウェアで画素決定** の低解像度セマンティック POV を numpy + zlib で自作」(`viz/render_pov.py:1-16`)。→ **P4 の Isaac Sim を研究主経路に置けない理由は、外部事情ではなく自分の設計原則**。
- **`file://` で開くだけ**の自己完結性は**ユーザー決定として明文化**されている(`docs/plans/plateau-3d.md`「ユーザー決定(2026-07-18)」)。→ **P1 の最大の障壁**。

---

## 2. P0(前提工事): 軌跡バイナリ化 — 全 3D 経路の共通ボトルネック

> これは 7 経路のどれでもないが、**P1/P2/P6 のいずれを選んでも先に必要**なので最初に置く。

### 2.1 問題

§1.3 のとおり、10日ラン規模で `tracks.json` が数百 MB になり、
(a) ブラウザで開けない (b) UE の `FJsonSerializer` でも起動時パースが数十秒〜分オーダー (c) git/転送が現実的でない。

### 2.2 具体案(差分)

`scripts/export_3d.py` に `--binary-tracks` を追加(既定 OFF=既存出力バイト同一)。

- 出力: `scene3d/tracks.bin` + `scene3d/tracks_meta.json`
- レイアウト(案):
  - ヘッダ: magic/version/nSteps/nAgents/quant(m/unit)/origin
  - `positions`: `int16[nSteps][nAgents][3]`(x, y, w)。量子化 0.05 m/unit なら ±1638m を表現でき、既に `PLATEAU_QUANT = 0.05`(`scripts/export_3d.py:158`)で同じ手が使われている。
  - `moves`: 可変長。オフセット表 `uint32[nSteps][nAgents]` + ポリライン本体 `int16[·][2]`。
  - `traffic`: 同様に step 毎オフセット。
- **見積り**: 10,000体×144step の positions = 10,000×144×3×2B = **8.6 MB**(JSON 65.8MB の **1/7.6**)。10日(1,440 step)で **86 MB**。gzip でさらに落ちる。
- **実装の容易さ**: `scripts/export_3d.py:422 build_glb` が既に **numpy + stdlib 手書きの glTF バイナリ生成**をやっている(依存追加ゼロ)。同じ流儀でそのまま書ける。
- `viz/make_viewer3d.py` 側: `viewer3d_lite.html` の**サイドカー方式が既にある**(`plateau_mesh.js` を `<script src>` で読む=`file://` でも動く JSONP 回避策・`make_viewer3d.py:915-920`)。`tracks.bin` は `fetch` できないので、**base64 を `tracks_bin.js` に入れて `<script src>` で読む**か、`--server` 前提の分離版を別に持つ。前者なら base64 で 4/3 倍(115 MB @10日)になるが、それでも現行 JSON の 1/5.7。

### 2.3 評価

| 軸 | |
|---|---|
| ①手順 | `export_3d.py` に writer 追加(~150行)+ `make_viewer3d.py` に reader 分岐(~80行)。**シム本体・L1・conf・ゴールデン無風** |
| ②工数 | Opus **1.5-2日** |
| ③レーン | **レーン1**(B-L0 の残タスク①「10日ラン規模での再生スモーク」そのもの・計画書 §2 に既記載) |
| ④リスク | 低。既定 OFF でバイト同一。唯一の注意は量子化誤差(0.05m=5cm は歩行者可視化には十分・PLATEAU メッシュと同一量子化) |
| ⑤価値 | プレゼン ★☆☆(単体では見えない) / 研究 ★★☆(**10日ランを再生できるかどうかそのもの**) |
| ⑥ライセンス | 自作・依存追加ゼロ |

### 2.4 なぜこれを P1(Cesium)より先に置くか

Cesium にしても UE にしても、**軌跡の運搬形式は同じ問題を抱える**。Cesium の CZML は JSON なので事態は悪化する(CZML は 3D Tiles と違いストリーミング前提の空間分割を持たない)。先に binary を作れば、その後どの経路にも同じ `tracks.bin` を食わせられる。

---

## 3. P1: Cesium / 3D Tiles リプレイ

### 3.1 技術的事実(Web 確認)

- **PLATEAU は 3D Tiles を公式配信している**。配信基盤は `assets.cms.plateau.reearth.io`、tileset URL の形は例えば
  `https://assets.cms.plateau.reearth.io/assets/0e/e5948a-.../13101_chiyoda-ku_pref_2023_citygml_1_op_bldg_3dtiles_13101_chiyoda-ku_lod1/tileset.json`
  (千代田区2023の例。**渋谷区の URL は当該チュートリアル内には無い**=カタログ API から引く必要がある)
  — [Project-PLATEAU/plateau-streaming-tutorial](https://github.com/Project-PLATEAU/plateau-streaming-tutorial/blob/main/3d-tiles/plateau-3dtiles-streaming.md)
  なお同チュートリアルは **[docs.plateauview.mlit.go.jp](https://docs.plateauview.mlit.go.jp) へ全面移行済み・当該リポは更新停止**と明記されている。移行先は「3D Tiles / MVT データとデータカタログ API」「CityGML」「Terrain」「Ortho」を分けて文書化しており、REST + GraphQL の API リファレンスとプレイグラウンドを持つ。
- **渋谷区2025 のデータセット自体には 3D Tiles zip が同梱**されている:
  `13113_shibuya-ku_pref_2025_3dtiles_mvt_1_op.zip`(`viz/unreal/README_UE.md:37`・zip は 637MB と `docs/plans/plateau-3d.md:12` に記録)。
- **CesiumJS は Apache 2.0**、商用・非商用とも無償。Cesium ion は**任意**の商用サービスで、ion のコンテンツ(地形・衛星画像)を使わなければ **ion トークンは不要** — [CesiumJS platform page](https://cesium.com/platform/cesiumjs/) / [LICENSE.md](https://github.com/CesiumGS/cesium/blob/main/LICENSE.md)。ただし上記 PLATEAU チュートリアルは **PLATEAU-Terrain を使う箇所で `Cesium.Ion.defaultAccessToken` を要求**している(地形を使わなければ回避可)。
- **オフライン(`file://`)は原則不可**。Cesium 公式 Offline Guide は「3D Tiles や glTF はサーバ側処理不要の静的アセットだが、ブラウザは `file://` へのリクエストを cross-origin として扱うのでローカルサーバ推奨」としている — [Cesium OfflineGuide](https://github.com/CesiumGS/cesium/blob/main/Documentation/OfflineGuide/README.md)、および [Cesium Community: Is there a way to use Cesium 3D Tiles offline?](https://community.cesium.com/t/is-there-a-way-to-use-cesium-3d-tiles-offline/6129)。
- **CZML の大量エンティティは重い**: Cesium コミュニティに「~10,000 の時間非依存ラベル entity で深刻な性能劣化」「1,000台を 10Hz 更新したい」といった相談が複数あり、対策は entity ではなく **Primitive API / point 化 / LOD 縮退** — [~10k Entity Performance](https://community.cesium.com/t/10k-entity-performance/9058)、[Performance with 10's of thousands of entities](https://community.cesium.com/t/performance-with-10s-of-thousands-of-entities/3722)。
  → **10,000体を CZML entity で出すのは無理**。`PointPrimitiveCollection` / `BillboardCollection` 直叩き+自前時刻補間になる。それは要するに**今 three.js でやっていることと同じ**。
- **three.js を保ったまま 3D Tiles を読む道もある**: [NASA-AMMOS/3DTilesRendererJS](https://github.com/NASA-AMMOS/3DTilesRendererJS)(three.js / Babylon.js / r3f 対応)。**ただしこれは過去に明示的に棄却済み**: 「ライブラリ vendor + `file://` でのタイル fetch 不可=ローカルサーバ必須となり『ブラウザで開くだけ』の自己完結性を失う。棄却」(`docs/plans/plateau-3d.md:58`)。

### 3.2 現行 three.js 版との比較

| 軸 | 現行 three.js r128 自己完結 | Cesium / 3DTilesRendererJS |
|---|---|---|
| 建物形状 | PLATEAU LOD1/2 を**自前抽出・量子化して埋め込み**(6,311棟・`plateau_web.json` 18.9MB) | 公式 3D Tiles を**そのまま**。LOD ストリーミングが効く=渋谷区全域も可能 |
| 見た目 | 単色+陰影+昼夜光(テクスチャは意図的に不採用・`plateau-3d.md`) | 同上(PLATEAU 3D Tiles も基本テクスチャ無し LOD1/2)+ 地形・衛星画像を重ねられる |
| オフライン | **`file://` でダブルクリック起動**(ユーザー決定) | **ローカルサーバ必須**(公式が明言) |
| 大量エージェント | 現行実装で 10,000体を描けている(`rehearsal_pool10k`) | Primitive API 直叩きが必要=**同じ実装を書き直す** |
| 工数 | 0(完成品) | 2-4日(座標系を ECEF/Cartographic に載せ替え・軌跡再実装・配信 URL 解決) |
| ライセンス | three.js MIT(vendor 済み・`viz/vendor/LICENSE`) | CesiumJS Apache 2.0 / 3DTilesRendererJS Apache 2.0。PLATEAU データは CC BY 4.0 等で商用可 |

### 3.3 評価

| 軸 | |
|---|---|
| ①手順 | (a) `docs.plateauview.mlit.go.jp` のカタログ API で渋谷区2025 の tileset.json を解決 (b) 新規 `viz/make_viewer_cesium.py`(既存 `make_viewer3d.py` は触らない) (c) `tracks.bin`(P0)を `PointPrimitiveCollection` へ流す自前時刻補間 (d) `python -m http.server` 起動を README 化 |
| ②工数 | Opus **2-4日**(P0 完了後) |
| ③レーン | **レーン3**。本選前に入れる理由が無い(見た目の上積みが小さく、自己完結性を失う) |
| ④リスク | **自己完結性の喪失=ユーザー決定の反故**。配信 URL の可用性依存。オフライン運用には 637MB zip の自前ホストが要る |
| ⑤価値 | プレゼン ★★★(「PLATEAU の公式配信に載せた」は分かりやすい)/ 研究 ★☆☆(**因果は 1 mm も動かない。見た目だけ**) |
| ⑥ライセンス | すべて無償・商用可。ion トークンは地形を使わなければ不要 |

**判定**: 純粋な上位互換ではない。**「サーバを立てて見せる」が許容できるなら価値がある**が、本選提出物としては現行 three.js 版で十分。**優先度 4 位**。

---

## 3B. P2: UE5 リプレイ — 「設計は完成、実装はゼロ、そして**バージョンが噛み合わない**」

### 3B.1 何が済んでいて何が済んでいないか(§1.2 の再掲+差分)

| 段 | 状態 |
|---|---|
| 座標変換の設計(sim ENU-m 右手 → UE cm Z-up 左手) | **完成・実行実績あり**(`scripts/export_ue.py`・`sim_ue.json` が 2 ラン分生成済み) |
| PLATEAU 原点合わせ(EPSG:6677 第9系オフセット) | **数値が確定済み**(`export_ue.py:49`)。SDK のインポート時オフセットに入れるだけ |
| heading / y_flip | **8 通りの総当たりで必ず合う**手順が文書化済み。ただし**実測合わせは未実施** |
| UE エディタ内 Python(ISM 配置 / Sequence ベイク) | **書かれている**(`import_shibuya_sim.py` 13.6KB)が**未実行** |
| ランタイム再生アクタ(`AShibuyaSimReplay`) | **設計と擬似コードのみ。C++/BP のコードは 0 行** |
| 群衆の見た目 | **シリンダとキューブ**(`/Engine/BasicShapes`)。City Sample も MetaHuman も未使用 |
| テスト | **ゼロ**(`tests/` に `export_ue`/`sim_ue` の参照なし) |

**= 残っているのは「UE を入れて、設計どおり 1 度動かす」という、純粋に実機作業の塊。**

### 3B.2 ★★ 最重要の発見: 3 つのバージョン制約が**同時には満たせない**

| 要素 | 要求する UE バージョン | 出典 |
|---|---|---|
| **PLATEAU SDK for Unreal v3.2.2**(最新・2025-06-03) | **UE 5.5.4 のみ** | [Releases](https://github.com/Project-PLATEAU/PLATEAU-SDK-for-Unreal/releases) |
| **City Sample の群衆/交通**(MassCrowd/MassTraffic) | **5.6 以降のパッチが要る**(5.6 発売時は非互換・2025-08-12 に更新)。**5.7 では out of the box で壊れている**(`LogMassSpawner: Error: No locations found on zone graphs`。2026-02 に `CityTrafficBuilder_BP` の Build を手動実行する回避策が判明) | [5.6 スレッド](https://forums.unrealengine.com/t/how-can-i-use-the-city-sample-in-unreal-engine-5-6/2544089) / [5.7 broken](https://forums.unrealengine.com/t/ue-5-7-city-sample-broken/2701997) |
| **MetaHuman Crowd / Collections**(最新の群衆技術) | **UE 5.8**(2026-06-17)。しかも **Experimental** かつ **Mass 結合** | [UE 5.8 features](https://www.cgchannel.com/2026/06/see-5-key-features-for-cg-artists-in-unreal-engine-5-8/) |

**→ PLATEAU SDK(≤5.5.4)と City Sample 群衆(≥5.6)と MetaHuman Crowd(5.8)は排他。**
「PLATEAU の渋谷 + City Sample のフォトリアル群衆 + 外部軌跡駆動」は**単一の UE バージョンでは成立しない**。

**さらに PLATEAU SDK for Unreal は事実上の休止状態**: Project-PLATEAU ミラーの最終 push は **2025-06-03(約14ヶ月前)**。上流(Synesthesias)の最終 push は 2025-11-24・デフォルトブランチ `dev/v4` だが**リリースはゼロ**。Issue に UE 5.6/5.7/5.8 の言及は無い。
対照的に **Unity 版 SDK は 2026 年も活発**(CityGML v4 対応 2026-03・Unity 6000.2.15f1 でテスト)。**Unreal 側は放置されている兄弟**。

### 3B.3 ★ 我々の環境を直撃する 2 つの落とし穴

1. **プロジェクトパスに日本語が入るとビルドエラー**(公式インストールマニュアルに明記) — [Installation manual](https://project-plateau.github.io/PLATEAU-SDK-for-Unreal/manual/Installation.html)。
   **我々の作業ディレクトリは `C:\Users\塚本翔太\Desktop\shibuya-simulation`**。→ **UE プロジェクトは別の場所に置かねばならない**。
2. **C++ プロジェクト + Visual Studio が必須**(Blueprint-only プロジェクトはダミー C++ クラスの追加が要る)。同ページ。

(なお v3.2.2 の changelog には「**渋谷の地下街を読み込めないのを修正**」がある = **渋谷は 2025年中頃まで既知の壊れケースだった**。)

### 3B.4 ★ 迂回路: PLATEAU SDK を使わない 2 つの道

- **(a) FBX 直取り込み**: PLATEAU は **東京23区の FBX(2020年度)** を配布している。**LOD1 は 23区全域、LOD2 は 11地区で渋谷(1.39 km²)を含む**。**SDK もプラグインも一切不要**。無償・商用可 — [plateau-tokyo23ku-fbx-2020](https://www.geospatial.jp/ckan/dataset/plateau-tokyo23ku-fbx-2020)。
  → **UE のバージョン制約から完全に解放される**。代償はデータが 2020年度(現行 `data/plateau/` は 2025年度)。
- **(b) Cesium for Unreal**: **v2.28.0(2026-07-01)が UE 5.5 / 5.6 / 5.7 / 5.8 に対応**(2.28 が 5.5 対応の最後) — [Releases](https://github.com/CesiumGS/cesium-unreal/releases)。
  Cesium ion が **PLATEAU 由来の "Japan 3D Buildings & Terrain"(210+自治体・約2300万棟)を無償ホスト**(帰属表示のみ) — [Cesium ion](https://cesium.com/platform/cesium-ion/content/japan-3d-buildings/)。
  → **新しい UE を使いたいならこちら**。⚠️ 生の PLATEAU 3D Tiles は glTF の `RTC_CENTER` を使っており Cesium for Unreal 向けに変換が要った履歴がある(2026 年時点で必要かは **UNVERIFIED**)。**ion の焼き済みアセットを使うのが安全**。

### 3B.5 Mass(MassCrowd/MassTraffic)は**使ってはいけない**

- Mass の実体: **MassEntity**(アーキタイプ ECS)→ **MassGameplay**(世界表現/スポーン/LOD/StateTree)→ **MassAI**(ZoneGraph レーン航法+SmartObjects)→ **MassCrowd**(レーンベース歩行者)/ **MassTraffic**(レーンベース車両) — [Mass Gameplay overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/overview-of-mass-gameplay-in-unreal-engine)。
- **外部から与えた位置で Mass エージェントを駆動した事例は、調査の結果 1 件も見つからなかった(UNVERIFIED / 前例なし)**。
- Mass が用意しているフックは `FMassMoveTargetFragment` だが、これは**位置ではなく「操舵目標」**。外部の正確な位置を再生するには `FTransformFragment` を上書きする自前プロセッサを書き、移動・回避・ZoneGraph の各プロセッサを無効化する必要がある = **Mass の機能を全部捨てて ECS ストレージと ISM 描画だけ借りる**ことになる。
- Epic 自身が Mass Replication と「ISM のアニメーションは全ユースケースで未完全対応」を **Experimental** と表示。主要コミュニティ資料も「頻繁に変更されるので情報は不正確かもしれない。迷ったらコードが唯一信頼できる指標」と書いている — [Megafunk/MassSample](https://github.com/Megafunk/MassSample)。

**→ リポの `SimReplayActor_DESIGN.md:198`「Mass の挙動生成は使わず、描画スケール手段(ISM/VAT/Niagara)だけ借りるのが素直」という判断は、外部調査で完全に裏づけられた。**

### 3B.6 ★ 大量描画の実数(設計の見直しが 1 点必要)

- **ISM の性能の崖**: `BatchUpdateInstancesTransforms` を `bMarkRenderStateDirty = true` で呼ぶと **50,000 インスタンスで 7-8 fps**。対策は**最後の 1 インスタンスだけで MarkRenderStateDirty する**こと(そうしないと transform ごとにレンダ状態更新が走る) — [ISM transform update performance](https://forums.unrealengine.com/t/instanced-static-mesh-transform-update-performance/577043)。
  `UpdateInstanceTransform()` は内部に O(n) の呼び出しを含み、`BatchUpdateInstancesTransforms` は実質その for ループ — [UE-38585](https://issues.unrealengine.com/issue/UE-38585)。
  → **リポの設計は既に正しい**: 人は 1 回の Batch 呼び出し、車は `UpdateInstanceTransform(..., false, false)` を回してから最後に `MarkRenderStateDirty()` 1 回(`SimReplayActor_DESIGN.md:100,110-111`)。**この点は変更不要**。
- **★ C++ か Blueprint かで 60倍以上違う**: 外部データ(Niagara GPU sim)から ISM へ transform を書く最良の実測例では、**10,000 インスタンスの変換が Blueprint で ~20 ms、C++ で 0.3 ms**。C++ 実装なら **100,000 インスタンスを 4K/60fps で Nanite ISM 描画**できている。ボトルネックは読み出しではなく**ゲームスレッドでの transform 配列への変換/ソート** — [Nanite+Niagara 100k](https://forums.unrealengine.com/t/nanite-niagara-how-i-do-it-its-supported-since-5-0-using-blueprints-to-export-particle-positions-from-the-gpu-and-c-to-convert-that-data-to-transform-arrays-by-static-mesh/1814048)。
  → **リポの設計は「数百〜千体台なら BP で十分実用」(`SimReplayActor_DESIGN.md:171`)としているが、10,000体を狙うなら C++ 一択**。この 1 行は更新すべき。
- **VAT(AnimToTexture)**: UE 5.1 以降エンジン標準。City Sample の背景群衆を動かしているのがこれ。制限は **1メッシュ 8,192 頂点**・**ベイク 8,192 フレーム**(DX11 テクスチャ寸法由来) — [VAT limits](https://www.unrealcode.net/AnimationTextures.html)。18,000体 VAT がリアルタイムで動いた逸話あり(RTX 2060 で 1-2 fps 低下・**単一の逸話であってベンチマークではない**)。
- **5.5 以降の新技術**: 5.5 で Nanite skinned mesh が安定化。5.6 で `UInstancedSkinnedMeshComponent`(ISKM)が入ったが**事実上ドキュメント無し**(2025-09〜2026-02 の開発者報告「1 つも表示できないし情報がどこにも無い」)。5.8 の MetaHuman Crowd は ISKM + Nanite + Mass だが **Experimental** かつ **ISKM は SkinnedMeshComponent 継承のため AnimBlueprint 非対応**。
  → **新しい群衆技術は全部 Experimental で、しかも 5.8 には PLATEAU SDK が無い。**

### 3B.7 ★★ Movie Render Queue が Tick 駆動リプレイを壊す(既存設計の実バグ)

**リポの `SimReplayActor_DESIGN.md:84-115` は `Tick(dt)` で `T += dt * PlaybackSpeed` する設計。これは MRQ で壊れる。**

- MRQ は `UMoviePipelineCustomTimeStep`(`UEngineCustomTimeStep` の実装)を差し込み、キャッシュした時刻を吐く。Epic の文言:「**エンジンが tick される(ひいてはワールドで時間が進む)ので、これらは temporal サンプルと呼ぶ**」— [Cinematic image quality settings](https://dev.epicgames.com/documentation/unreal-engine/cinematic-rendering-image-quality-settings-in-unreal-engine) / [UMoviePipelineCustomTimeStep](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Plugins/MovieRenderPipelineCore/UMoviePipelineCustomTimeStep)。
- **delta time はフレーム内で不均一**。temporal サンプルはシャッター開区間だけを等分し、シャッター閉区間は**1 回の大きなステップ**で埋める — [Setting Up Motion Blur](https://dev.epicgames.com/documentation/unreal-engine/setting-up-motion-blur)。
- **報告されている実バグ**:「Blueprint イベントと tick ベースのシステムがフレームごとではなくサンプルごとに実行される … temporal サンプル 8 で 8倍速になる」+「サンプル間でアクタが動くためのゴースト」— [BP events accelerated by temporal samples](https://forums.unrealengine.com/t/blueprint-events-accelerated-by-anti-aliasing-temporal-samples/676935)。
- **対策(頑健な順)**:
  1. **Sequencer のプロパティトラックから駆動する**(Tick をやめる)。float 変数を `Expose to Cinematics` + `Instance Editable` にし、`Set<VarName>` 関数を用意すると Sequencer が生プロパティ書き込みの代わりにその関数を呼ぶ → **正しいサブフレーム位置で ISM を再構築できる**。
  2. **Temporal Sample Count = 1** にして AA は spatial サンプルだけで取る(MRQ のモーションブラーは失われるが、最も単純で完全に決定論的)。
  3. 「Lock to Display Rate at Runtime」は MRQ 中にも効くが、**temporal サンプルを上書きするので両立しない** — [Setting your Display Rate](https://dev.epicgames.com/documentation/unreal-engine/setting-your-display-rate)。
- その他の MRQ の実務コスト: ウォームアップフレームが要る(Epic の高品質ガイドは **Render/Engine Warm Up Count 各 120**)。MRQ は初回フレームで Sequencer タイムラインを飛び回るため Event Track が保存前に複数回発火する。
- **Movie Render Graph は 5.8 で production-ready** になり MRQ の後継と位置づけられた(MRQ も引き続き利用可)。

**→ `SimReplayActor_DESIGN.md` に「MRQ 収録時は Tick 駆動を使わず Sequencer プロパティトラック駆動へ切り替える」節を足すべき。§6「実機での検証項目」に 6 個目として追加する価値がある。**

### 3B.8 City Sample のライセンス: **動画なら明示的に許可されている**

- City Sample は Epic Content License の **"UE-Only Content"**。条項の要点(Epic の EULA PDF から確認・原文引用):
  > "For UE-Only Content, you may exercise your rights under the License only if and to the extent that the UE-Only Content is utilized in a Product that requires the Engine Code to operate **or is a non-interactive linear media product (e.g., broadcast or streamed video files, cartoons, movies, or images) rendered using the Engine Code.**"
  — [Epic Content License](https://www.unrealengine.com/eula/content)(直接取得は 403。文言は [EULA PDF](https://cdn2.unrealengine.com/Unreal+Engine/faq/UnrealEngineEULA_for_Publishing_v14-64b26ec5ab4ffcc34c6cce2aaa0a6988dfcd6541.pdf) で裏取り。**現行版の正確な改訂文言は UNVERIFIED**)
- **→ 「UE でレンダリングした研究デモ動画に City Sample の MetaHuman 群衆・車両を使う」ことは、まさに許可されているケース**。禁止されるのは生アセットの再配布と、UE 以外のレンダパイプラインでの使用。
- MetaHuman 単体のライセンスは 2025-06 に変更され、**他エンジン/DCC でも収益 100万USD 未満なら無償** — [metahuman.com/license](https://www.metahuman.com/license)。**UNVERIFIED**: City Sample の群衆キャラが新 MetaHuman ライセンス側か UE-Only 側か(どちらでも動画用途は可)。
- モジュール分割パックあり(City Sample Buildings / Vehicles(運転可13車種)/ Crowds(6体型・12頭部・10 groom+衣装))= **フルプロジェクトを落とさなくてよい**。
- Epic 推奨ハードウェア: 12コア 3.4GHz・**システム RAM 64GB**・RTX 2080+ / VRAM 8GB 以上。

### 3B.9 提出動画としての価値と、その正体

- **プレゼン映えは全経路中で最高**(Lumen + Nanite + PLATEAU LOD2 の渋谷)。
- しかし**現在の設計で動くのはシリンダとキューブ**である(`import_shibuya_sim.py:38-40`)。「フォトリアルな渋谷を人が歩く」画にするには (a) キャラメッシュ + VAT (b) ISM/Niagara への適用、という**別の工数**が要る。
- **研究価値はゼロに近い**。これは `tracks.json` の再生であって、幾何が挙動に与える影響は 1 mm も測っていない(§9 の警告がそのまま当てはまる)。

### 3B.10 工数(外部の実データ点)

**業界の統計的な答えは存在しない。以下はすべて逸話**(調査エージェントが明示):

| データ点 | 所要 |
|---|---|
| 映像/VFX 経験者が UE5.5 で環境+カメラフライスルー+レンダ+音楽を**初めて**作る | 「約 3〜4 日」 |
| PLATEAU→UE の初回インポート(UE 5.1・SDK 1.0・2023): プラグイン再ビルド 2-3分・インポート~10分でプレビュー・**3GB DL → 展開 80GB+**・16GB RAM / RTX3050 ラップトップで頻繁にクラッシュ | 順調でも半日 |
| PLATEAU ハッカソン攻略ガイド(**Unity**): 環境構築 30分・データ取込 60分・「3時間以内に完全表示」。**範囲は 1-2 km² に絞れ**。市全体は「固まるか数時間かかる」 | 動くデモ+機能1つで 2日 |

**3〜7 実働日で収まるのは、以下の「意図的に狭い道」を通った場合だけ**(調査エージェントの総合判断):
- **UE 5.5.4 + PLATEAU SDK v3.2.2 に固定**(唯一の公式対応組合せ)**か**、**UE 5.6+ + Cesium ion Japan 3D Buildings で PLATEAU SDK を完全に回避**
- **渋谷の 1-2 km² のみ**取り込む(区全体はやらない)= 我々の bbox 2.9km² とほぼ整合
- **Mass を使わない・City Sample 群衆を使わない**。**ISM + VAT** を **C++** アクタで駆動
- **Sequencer プロパティトラックから駆動**し、**Temporal Samples = 1** でレンダ
- **UE プロジェクトを日本語を含まないパスに置く**

**逆に、「City Sample の MassCrowd/MassTraffic + PLATEAU SDK + 外部軌跡駆動 + フォトリアル MetaHuman」を狙うと 3-7日では絶対に終わらない**(§3B.2 のバージョン三竦みが物理的に解けないため)。

### 3B.11 評価

| 軸 | |
|---|---|
| ①手順 | (1) **UE 5.5.4 + PLATEAU SDK v3.2.2** を固定(or 5.6+ & Cesium ion 経路)(2) **日本語を含まないパス**に C++ プロジェクトを作る (3) CityGML を 1-2km² だけインポート(オフセット = `export_ue.py:49` の EPSG:6677 値)(4) `export_ue.py --binary`(§3B.12)(5) `import_shibuya_sim.py` で ISM 配置 (6) `SimReplayActor` を **C++ で**実装し、**Tick ではなく Sequencer プロパティ**から駆動 (7) heading/y_flip を 8通り総当たりで実測合わせ (8) **Temporal Samples = 1** で MRQ 収録 |
| ②工数 | **狭い道なら Opus 5-7日 + UE 学習**。広い道(City Sample 群衆)なら**達成不能** |
| ③レーン | **レーン3**。「提出動画 1 本」だけなら **200-500体・1日規模でレーン2 末(8/27-29)**に押し込む選択はありうる(入力 `demo_event_200a3d/scene3d/sim_ue.json` は既に存在)。ただし §3B.10 の実データ点(初回インポートだけで半日・80GB 展開)を見ると、**8/27-29 の 3日では厳しい** |
| ④リスク | **高**。①バージョン三竦み ②SDK が 14ヶ月休止 ③日本語パス ④MRQ の Tick 問題 ⑤実機経験ゼロ。**10日ランと競合させてはいけない** |
| ⑤価値 | プレゼン **★★★★**(最高)/ 研究 **★☆☆**(位置ログの再生) |
| ⑥ライセンス | UE5 = Epic EULA。**City Sample は「UE でレンダした非インタラクティブ動画」用途を明示的に許可**(§3B.8)。PLATEAU SDK/データ・FBX 版・Cesium ion の Japan 3D Buildings はいずれも無償・商用可 |

### 3B.12 UE 経路でも P0(バイナリ化)は必須

`sim_ue.json` の実測(§1.2)から **684 B/agent-step**(【訂正 2026-07-31】正しくは 228 B/agent-step=§1.2 の訂正参照。以下の 9.8GB は 0.89GB と読み替え)。
- 200体×1日 = 19.7 MB(OK)
- 1,000体×1日 ≈ 98 MB(BeginPlay のパースが数十秒)
- **10,000体×10日 ≈ 9.8 GB(不可能)**

`SimReplayActor_DESIGN.md:60` は「毎 tick の JSON アクセスは厳禁。BeginPlay で一度だけ展開」としているが、**その一度が終わらない**。
→ `export_ue.py` にも `--binary`(`sim_ue.bin` + `sim_ue_meta.json`)を足し、UE 側は `FFileHelper::LoadFileToArray` で読んで `TArray<int16>` に載せるのが正しい。**P0 と同じ量子化スキームを共有すればよい**。

---

## 4. P3: Unity + PLATEAU SDK — 「使うな。ただし隣に本命がある」

### 4.1 結論を先に

**描画目的では不要**(three.js / UE で足りる)。評価すべきは唯一「**B-L2(屋外SFM)/ H_B(歩行ネットワーク)の歩道データ抽出器として使えるか**」という点だが、その答えは **No、しかし Unity を経由しない官製の代替が 2 つある**。

### 4.2 Unity SDK の道路ネットワーク機能: 中は良いが、出口が塞がっている

- **最新 v4.3.0(2026-06-29)。Unity 6000.3.10f1 以上が必須**(v4.2.0 で最小要件が Unity 6000.3 に上がった。v3.x 系は Unity 2022.3) — [Releases](https://github.com/Project-PLATEAU/PLATEAU-SDK-for-Unity/releases)。
- 生成物は `PLATEAURnStructureModel` コンポーネント + `ReproducedRoad` ツリー。UI は「道路調整」タブ(生成/編集/追加/エクスポート) — [manual/RoadNetwork](https://project-plateau.github.io/PLATEAU-SDK-for-Unity/manual/RoadNetwork.html)。
- **レーン単位のグラフであり、歩道は第一級オブジェクト**: `PLATEAU.RoadNetwork.Structure` 名前空間に `RnModel` / `RnRoad` / `RnLane` / `RnWay` / `RnIntersection` に加えて **`RnSideWalk`** が存在する — [API index](https://project-plateau.github.io/PLATEAU-SDK-for-Unity/api/PLATEAU.RoadNetwork.Structure.html)。
  `RnSideWalk` は `OutsideWay` / `InsideWay` / `StartEdgeWay` / `EndEdgeWay` の 4 ポリラインを持つ(閉多角形ではなく帯のフレームだが、4本を閉じれば面になる) — [RnSideWalk API](https://project-plateau.github.io/PLATEAU-SDK-for-Unity/api/PLATEAU.RoadNetwork.Structure.RnSideWalk.html)。
  LOD2 以上なら実モデルの歩道幅を使い、LOD1 では「全部車道として生成 → 幅が閾値を超えたら車道を狭めて歩道を足す(車道が 2m を割るならスキップ)」という**推定**になる。

- **★ 出口が塞がっている**: エクスポートタブは **GeoJSON のみ**(FBX/JSON/OpenDRIVE なし)。しかも出力ファイルは
  `roadnetwork_node` / `_link` / `_lane`(**車線のみ**)/ `_track` / `_signal*` で、
  **歩道(sidewalk)は 1 つも出力されない** — [RoadNetworkExported.md](https://github.com/Project-PLATEAU/PLATEAU-SDK-for-Unity/blob/main/Documentation~/manual/RoadNetworkExported.md)。
  属性の一部(`PROHIBIT`/`TURNCONFIG`/`TYPECONFIG`)は商用交通シミュレータ **AVENUE**([i-Transport Lab](https://www.i-transportlab.jp/en/index/products/avenue/))互換のためのハードコード定数。
  → **歩道を取り出すには自前で C# エクスポータを書いて `RnModel → RnSideWalk → 4本の RnWay` を歩く**必要がある。Unity 拘束・手作り。
- Toolkits の Sandbox 交通シミュレーションは **車両のみ**(AWSIM 由来)で歩行者エージェントは無い — [PlateauToolkit.Sandbox](https://github.com/Project-PLATEAU/PLATEAU-SDK-Toolkits-for-Unity/tree/main/PlateauToolkit.Sandbox)。

### 4.3 OpenDRIVE 経由の裏道は**存在しない**(明確な否定)

- PLATEAU SDK for Unity に **OpenDRIVE / .xodr エクスポートは無い**(エクスポート仕様・API TOC・v3.4.x 以降のリリースノートで確認)。
- 逆方向の変換器も助けにならない: **r:trån**(TUM-GIS)は **OpenDRIVE → CityGML の一方向のみ** — [tum-gis/rtron](https://github.com/tum-gis/rtron)。
- SUMO `netconvert` がインポートできるのは OSM / VISUM / Vissim / **OpenDRIVE** / MATSim / Shapefile / DlrNavteq で、**CityGML は読めない**(`--opendrive-output` で書き出せるが方向が逆) — [netconvert docs](https://sumo.dlr.de/docs/netconvert.html)。
- **公式の PLATEAU × SUMO 連携も存在しない**。MLIT の交通シミュレーション UC は [UC24-01](https://www.mlit.go.jp/plateau/use-case/uc24-01/) だが **AVENUE を使い、交換形式は GeoJSON**。同ページは歩行者シミュとの統合を**将来課題**と明記している。
  → **我々の SUMO 経路(OSM → netconvert)は、公式路線から外れているのではなく、そもそも別系統**。現状維持でよい。

### 4.4 ★ 本命 1: PLATEAU-RoadNetwork-Generator(Unity 不要・官製・歩道つき)

**本調査で最大の発見のひとつ。** 令和6年度 Project PLATEAU 成果物、**C++・Windows GUI・LGPL-2.1・Unity 非依存** — [Project-PLATEAU/PLATEAU-RoadNetwork-Generator](https://github.com/Project-PLATEAU/PLATEAU-RoadNetwork-Generator)。

> 3D都市モデル(交通(道路)、都市設備、橋梁)を使用して、**車道及び歩道ネットワークデータ(ノードデータ、リンクデータ)**を作成し、シェープファイル又はGeoJSONファイルに出力します。
> — [docs/README](https://github.com/Project-PLATEAU/PLATEAU-RoadNetwork-Generator/blob/main/docs/README.md)

- 入力: tran LOD1/2/3(+ frn + brid)。**手元にすべてある**(`docs/research/plateau-2025-update-notes.md:129-136` の実査で tran 4タイル・`lod3MultiSurface` 5,782面・`TrafficArea` 8,106・`AuxiliaryTrafficArea` 238 を確認済み)。
- 出力: Shapefile / GeoJSON の**ノード・リンク**(車道と歩道の両方)+ CSV エラーレポート。
- 開発動機がまさに我々の課題:「歩行者や車両の動態シミュレーション」に必要なネットワークデータが従来は手作業抽出だった。[技術報告書PDF](https://www.mlit.go.jp/plateau/file/libraries/doc/plateau_tech_doc_0115_ver01.pdf)。
- **限界**: 出るのは**グラフ(中心線のノード/リンク)であって歩行可能ポリゴンではない**。H_B の「面」が欲しければ §4.5。
- **UNVERIFIED**: CLI があるか(GUI のみに見える=自動パイプラインに組めない可能性)。歩道リンクが種別・幅員・横断接続を持つか。

### 4.5 ★ 本命 2: CityGML `tran` を Python で直接読む(面が欲しい場合)

歩行可能**面**は CityGML の `tran:TrafficArea` にある。`tran:function` コード(標準製品仕様 D.4):
**1000=車道部 / 1020=車道交差部 / 2000=歩道部**(LOD3.1+ で 1010=車線が加わる。LOD3.4 でさらに細分) — [tran:TrafficArea 仕様](https://www.mlit.go.jp/plateaudocument02/tocD/tocD_04/)。
幾何は `lod2MultiSurface` / `lod3MultiSurface` = **面モデル(MultiSurface)** で solid ではない。
→ **`tran:function == 2000` が歩行可能面のセレクタ**であり、**CityGML の XML パースだけで取れる(Unity も SDK も不要)**。

これは我々のリポの自認と完全に一致する:
> `plateau_extract.py` は bldg 専用。`SURFACE_TAGS` が `GroundSurface`/`RoofSurface`/`WallSurface` 等に固定されており、`tran` を読むには **新規の抽出器が必要**。座標系は `*_tran_6697_op.gml` = EPSG:6697 で bldg と同じなので、**局所接平面変換はそのまま流用できる**。
> — `docs/research/plateau-2025-update-notes.md:165-167`

**つまり `scripts/plateau_extract.py` に `--tran` を足す(投影は既存流用)のが最短。** 補助ツール候補:
- [PLATEAU-GIS-Converter](https://github.com/Project-PLATEAU/PLATEAU-GIS-Converter)(Rust・**CLI あり**・MIT・GeoJSON/GeoPackage/Shapefile/3D Tiles/glTF/OBJ 等)— 汎用の第一候補。**UNVERIFIED**: TrafficArea 単位の `tran:function` を出力に保存するか。
- [plateaupy](https://github.com/AcculusSasao/plateaupy)(MIT・Python・`tran` を明示的にパースし Open3D TriangleMesh 化)— コミット 35 で保守が薄い。
- [plateaukit](https://github.com/ozekik/plateaukit) v0.19.0 — 実例は `-t bldg` のみ。**UNVERIFIED**: `tran` 対応。

### 4.6 ★ 抜け道 3: 歩行空間ネットワークデータ(PLATEAU ですらない・渋谷区あり)

国交省 政策統括官の **歩行空間ネットワークデータ** — バリアフリー属性(幅員・段差・傾斜)つきの歩行者ネットワーク(ノード・リンク)。
[geospatial.jp/ckan/dataset/0401](https://www.geospatial.jp/ckan/dataset/0401) が 25 自治体を収録し **東京都_渋谷区を明示的に含む**。形式は **GeoJSON / Shapefile / CSV**。渋谷の最新改訂は 2020-03-01。現行仕様は 2024年7月版で [ほこナビDP](https://www.hokonavi.go.jp/opendata/) がホスト。
→ **歩行「グラフ」で足りるなら、PLATEAU から導出するより速い。既に導出済みのものが配布されている。**

### 4.7 評価(P3 = Unity 経路そのもの)

| 軸 | |
|---|---|
| ①手順 | Unity 6000.3 導入 → SDK v4.3.0 → CityGML インポート → 道路ネットワーク生成 → **自前 C# エクスポータを書いて RnSideWalk を吐かせる** |
| ②工数 | Opus **4-6日**(Unity 未経験+C# エクスポータ自作+検証)。**§4.4/§4.5/§4.6 のいずれかなら 1-2日** |
| ③レーン | **やらない**。レーン3 でも §4.4/§4.5 を優先 |
| ④リスク | 高。Unity 6000.3 という重い依存を、**出力が塞がれている**ツールのために入れることになる |
| ⑤価値 | プレゼン ★☆☆(Unity の画面を見せる理由が無い)/ 研究 ★★☆(欲しいのは歩道データであって Unity ではない) |
| ⑥ライセンス | SDK は Apache-2.0 系(要確認)。**Unity 本体のライセンス条件**が新たに載る |

**推奨**: **P3(Unity)は却下**。代わりに **レーン3 で「`plateau_extract.py --tran`(§4.5)+ 歩行空間ネットワークデータ(§4.6)の二本立て」**を B-L2 / H_B の前提作業として置く。前者が「面」、後者が「グラフ」を供給し、被覆の穴を互いに埋める。

### 4.8 ★ 未解決の重要リスク(先に潰すべき)

**渋谷の tran LOD3.0 の被覆範囲**。データセット README は LOD3.0 = **1.41km²(都市再生緊急整備地域)**、シム bbox は **約 2.9km²**(`docs/research/plateau-2025-update-notes.md:43,61,158-161`)。**全域はカバーしない**。
外部調査でも「PLATEAU の LOD3 道路は通常、区全域ではなく限定的な実証コリドー。カタログは LOD3.0 ありと書くが被覆面積の記載を見つけられなかった」と **UNVERIFIED** 扱い。
→ **被覆マップを先に作り、被覆外は OSM 線分にフォールバックする二層設計**が要る(これは既にリポが同じ結論に達している・同 :158-161)。§4.6 の歩行空間ネットワークデータが**このフォールバック層に最適**。

---

## 5. P4: OpenUSD / Omniverse — 「USD 書き出しは安く、Omniverse は要らない」

### 5.1 OpenUSD の 2026 年の実状(ここが分岐点)

- **Core Specification 1.0 が 2025-12-17 に公開された**(OpenUSD 初の正式仕様。データモデル+合成規則、USDA/USDC/USDZ フォーマット、準拠ツールつき) — [AOUSD](https://aousd.org/news/core-spec-announcement/) / [Linux Foundation](https://www.linuxfoundation.org/press/alliance-for-openusd-announces-core-specification-1.0-the-universal-language-for-building-3d-worlds)。
- **★ しかし「アニメーション」は Core Spec 1.0 の対象外**。「大規模/複雑シーンのスケーリング」も同様に 1.1 送り(同 AOUSD 発表)。
  → **時系列の軌跡を USD で運ぶことは、まだ標準化されていない**。実装(Pixar USD ランタイム)は当然できるが、「標準に準拠しています」とは言えない。
- 2026-07-21 時点で Core Spec 1.1 は未公開(ISO 認証プロセスに入る段階) — [PRNewswire 2026-07-21](https://www.prnewswire.com/news-releases/alliance-for-openusd-drives-global-3d-data-interoperability-and-agentic-ai-workflows-with-new-core-specification-milestones-and-members-302830574.html)。エージェントに最も近い **Characters, Motion & Interactivity (CMI) は 2026-03-25 発足の Interest Group**(=標準以前) — [Linux Foundation 2026-03](https://www.linuxfoundation.org/press/aousd_prmarch2026)。
- **地理空間の USD スキーマは標準として存在しない**。AOUSD に geospatial WG は無く、Cesium は**独自ベンダ固有 USD スキーマ**を自作している — [NVIDIA blog](https://developer.nvidia.com/blog/leverage-3d-geospatial-data-for-immersive-environments-with-cesium/)。Bentley(iTwin)/ Esri(CityEngine)の Omniverse 統合は**コネクタであってスキーマではない** — [Geo Week News](https://www.geoweeknews.com/news/bentley-esri-announce-major-integrations-with-nvidia-omniverse)。
  → **「OpenUSD for cities」は 2026 年時点でマーケティング+ベンダ固有スキーマ。標準ではない。**

### 5.2 ★ 安い側: Python だけで USD を書く(GPU も NVIDIA アカウントも不要)

| ツール | pip | 対応 | NVIDIA 必要? | 判定 |
|---|---|---|---|---|
| **`usd-core` 26.8**(2026-07-20) | ✅ | Win x64 / manylinux x64 / macOS universal2・**Py 3.9-3.14** | 不要 | ✅ **これが道** |
| `usd-exchange` 2.3.0(NVIDIA OpenUSD Exchange SDK・Apache-2.0) | ✅ | Win/Linux x64+aarch64・Py 3.10-3.12 | **不要**(アカウント・GPU・Omniverse すべて不要) | ✅ 任意の便利層 |
| `guc`(glTF→USD) | ❌ | ソースビルド | 不要 | ⚠️ **アニメーション/スキニング非対応** |
| Blender USD export | n/a(`blender -b`) | headless 可 | 不要 | ⚠️ PointInstancer 書き出しは **Blender 5.0 から**。インスタンスのアニメは未対応 |

出典: [usd-core PyPI](https://pypi.org/project/usd-core/) / [usd-exchange PyPI](https://pypi.org/project/usd-exchange/) / [guc](https://github.com/pablode/guc) / [Blender USD manual](https://docs.blender.org/manual/en/latest/files/import_export/usd.html)

**`usd-core` の重要な但し書き**(PyPI 原文):「コア USD ライブラリのみ。フル配布版のオプションプラグインや imaging 機能は含まない」。
→ `UsdGeom`/`UsdShade`/`UsdSkel` は使えるが、**`usdview` も Hydra も glTF プラグインも入らない**。**pip で入る glTF→USD 変換器は存在しない**。

**したがって実務上の作り方はこうなる**:
- 静的な街(`buildings.glb`)は **一度だけオフラインで USD 化**(Blender headless か guc)。
- **動きは glTF を経由せず、`usd-core` で `UsdGeomPointInstancer` の time sample として直接書く**。

### 5.3 `UsdGeomPointInstancer` の API レベルの罠(3 つ)

[openusd.org API ref](https://openusd.org/dev/api/class_usd_geom_point_instancer.html)

主要属性: `protoIndices`(必須・その時刻のインスタンス数)/ `positions`(必須)/ `orientations`(**half 精度 quat**)/ `scales` / `velocities` / `ids` / `invisibleIds`。

1. 仕様は「数十億インスタンスにスケールする設計」と述べる。pos+quat+scale に分解しているのは **32 B/インスタンス**(4×4 float 行列なら 64 B)にするため。
2. **インスタンス数が時間変化する場合は `ids` を必ず書く**。書かないとマスクの index が `protoIndices` の**配列位置**を指してしまい、エージェントの生成/消滅で意味を失う。**我々の visitor 入退場(範囲外 state -1・睡眠 -2)はまさにこれに当たる**。
3. **`velocities` を書くと USD は `positions` を補間せず速度から積分する**。しかも `protoIndices` と `positions` が両方アニメートすると配列長が変わり補間不能になる。
   → **我々の正しい選択は「毎 step にサンプルを書き、velocities は書かない」**(10分 step = 144 sample/日 なので現実的)。

**サイズ試算**(外部エージェントの導出値・出典なしと明記されている): pos(12B)+ orient(4×f16=8B) ≈ **20 B/インスタンス/サンプル**。
我々に当てはめると: **10,000体 × 1,440 step(10日)× 20 B ≈ 288 MB**。§2 の `tracks.bin`(86MB)より重いが、USD の `.usdc` は疎に遅延ロードされる([Maximizing USD Performance](https://openusd.org/release/maxperf.html))ので許容範囲。
**UNVERIFIED**: 重い time-sampling での PointInstancer の公表ベンチマークは見つからなかった。

### 5.4 ★ Omniverse は 2026 年に**無償化**された(が、だから使う理由にはならない)

- **Omniverse は開発・本番とも無償、再配布も同条件で可**。ライセンス文書が 2026-05 に更新、フォーラム告知が 2026-07-01。従来は本番利用に NVIDIA AI Enterprise($4,500/GPU/年 等)が必要だった — [StorageReview](https://www.storagereview.com/news/nvidia-quietly-makes-omniverse-free-for-production-use) / [公式ライセンス](https://docs.omniverse.nvidia.com/ov/latest/common/NVIDIA_Omniverse_License_Agreement.html)。AI Enterprise が買うのは SLA サポートのみになった。
- **Omniverse Launcher は 2025-10-01 に廃止**、GitHub + NGC へ移行。**USD Composer / USD Explorer は「テンプレート」として存続**([kit-app-template](https://github.com/NVIDIA-Omniverse/kit-app-template))で、新機能開発はされていない。
- 「Omniverse Blueprints」は製品ではなく参照ワークフロー。**Blueprint for Smart City AI** は Omniverse+Cosmos+NeMo+Metropolis の構成だが、**実映像に対する映像解析エージェント**が主題で、**社会/行動エージェントのシミュレーションではない** — [NVIDIA blog](https://blogs.nvidia.com/blog/smart-city-ai-blueprint-europe/)。隣接するが別問題。

### 5.5 ★★ Isaac Sim の決定的な障壁: RT コアが**無いと動かない**(公式明記)

[Isaac Sim 6.0 requirements](https://docs.isaacsim.omniverse.nvidia.com/6.0.0/installation/requirements.html) 原文:

> **"GPUs without RT Cores (A100, H100) are not supported."**

- 最小 RTX 4080 / 推奨 RTX 5080 / 理想 RTX PRO 6000 Blackwell。VRAM 最小 16GB・理想 48GB。5.1 の要件も同一文言。
- Omniverse RTX Renderer 側のアーキ対応表は A100/H100/B200 を「対応」と列挙するが、DLSS Ray Reconstruction 無し(Real-Time モードで「著しくノイジー」)・Frame Generation 無し・SER 無し等の**大幅劣化**+「非 RTX GPU での動作はサポート保証なし」の但し書きつき — [対応表](https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_architecture_support.html)。

**→ 本選 GPU への直接の含意**: 計画書 §0-2 は「公式は RTX5000×7=合計168GB(24GB/GPU)。いずれも RT コアあり = Isaac Sim 動作可(A100/H100 だと不可)」としており、**本調査はこの記述を裏づけた**。ただし **U-4 の「開放時に実機で SKU を確認」は依然として必須**で、H100/A100/H200/B200 が出てきたら **Isaac Sim は即座に選択肢から消える**。サーバ筐体で使える RT コア持ちは L40 / L40S / RTX 6000 Ada / RTX PRO 6000 Blackwell Server Edition。
**さらに 2 つの独立した障壁**(リポ実査):
- **銘板が未確定**: 「A5000 24GB か RTX 5000 Ada 32GB か は**未確定**」(`docs/plans/finals-gpu-application.md:20`)。どちらも RT コアはあるが、確認は開放後。
- **★ そもそも GPU 時間が無い**: 申請草案は「本選期間中(8/15-8/30)で合計 **約 200 時間(GPU 7 基をほぼ連続占有)**」を vLLM に充てると書いている(同 `:105`)。**Isaac Sim を回す GPU 余剰は本選中に存在しない**。
  → **Isaac Sim は本選中に物理的に不可能。レーン3 以降の話ですらオプション。**

**Replicator(合成データ生成)について**:
- `isaacsim.replicator.agent`(IRA)が人物キャラ+ロボットをシミュレートし注釈つきデータをレンダリングする。アノテータは RGB / semantic seg / instance seg / distance-to-camera / normals / motion vectors / カメラ内部パラメータ+姿勢 — [IRA docs](https://docs.isaacsim.omniverse.nvidia.com/6.0.0/action_and_event_data_generation/tutorial_replicator_agent.html)。
- **ヘッドレス CLI は文書化されている**(`./python.sh tools/actor_sdg/actor_sdg.py -c <config>`)。外部 USD シーンも使えるが**キャラ配置に NavMesh 構築が要る**。
- ★ **「エージェント視点(ego camera)」は文書化されたワークフローではない**。docs は固定カメラとランダム配置のみ。USD 的には Camera prim を親付けするだけで自明だが **UNVERIFIED**。エージェント数上限も **記載なし=UNVERIFIED**。

**そして最も重い論点**: 仮に動いても、**GPU レンダは画素非決定**であり、リポは既にこの理由で **CPU 決定論 POV レンダラを自作している**(`viz/render_pov.py:1-16`)。
→ **Isaac Sim を C 段階2(VLM 入力画像)の主経路に置くと、決定論という研究の背骨を折る。** 計画書 U-4 の「デモ動画オプションに限定(研究主経路に置かない)」は正しく、**本調査はそれを強く支持する**。

### 5.6 Cesium for Omniverse(存在する・維持されている)

- **v0.29.0(2026-07)・Apache 2.0・商用非商用とも無償**。**Kit 110.0+(Isaac Sim 6.0.1+)が必要** — [Cesium 2026-07 releases](https://cesium.com/blog/2026/07/01/cesium-releases-in-july-2026/) / [CesiumGS/cesium-omniverse](https://github.com/CesiumGS/cesium-omniverse)。
- 3D Tiles を USD ステージへストリーミングする(`CesiumTileset` / `CesiumGeoreference` / `CesiumServers` prim)。**ただし Cesium 独自スキーマ経由で AOUSD 標準ではない**。
- **PLATEAU 経路は実在する**: Cesium ion が PLATEAU 由来の "Japan 3D Buildings" をホストし、Cesium for Omniverse で使えると明記 — [Cesium 2024-06](https://cesium.com/blog/2024/06/03/japan-3d-buildings/)。
  ⚠️ ただしこれは**ランタイムのストリーミング**で、第三者に渡せる USD アセットにはならない。ion のホスティング料金は **UNVERIFIED**。

### 5.7 ★ 「企業DTとの相互運用」の実質的意味(正直な査定)

**企業DTが実際にやりとりしている標準(2026)**:

| 層 | 実際に使われている標準 |
|---|---|
| 都市/地理空間 | **CityGML 3.0**(OGC 標準・4D/時系列を追加)・CityJSON・**3D Tiles**・I3S・**OGC API**(Features/Tiles/Processes)・SensorThings |
| AEC/BIM | **IFC**(buildingSMART) |
| グラフィクス交換 | **glTF**(配信の主流)・USD(新興) |
| IoT/資産セマンティクス | **DTDL** v2/v3(Azure Digital Twins・**Azure 固有**) |
| 連成シミュレーション | **FMI 3.0 / FMU**・SSP(100+ ツール対応の事実上の標準) |

**最も示唆的なデータ点**: 都市DT相互運用の旗艦演習である **OGC Urban Digital Twin Interoperability Pilot(ER 24-067r1・2025-06-26 公開)は OGC API + 3D 都市モデル + 交通プロファイル + センサーデータ**を軸に構成されている — [報告書](https://docs.ogc.org/per/24-067r1.html)。
→ **都市DTの相互運用は「OGC API / CityGML の物語」であって「USD の物語」ではない**(報告書に USD が出てくるか自体は **UNVERIFIED**=全文取得に失敗、ただし要約群に一切現れないこと自体が信号)。

**FMI について**: FMI 3.0 は「次世代デジタルツイン」を明示的に標的にしている([fmi-standard.org](https://fmi-standard.org/news/2022-05-10-fmi-3.0-release/))が、**都市交通では支配的ではない**。交通DTの標準パターンは **CARLA↔SUMO のロックステップ連成(TraCI・毎 timestep の車両状態ベクトル交換)**であり FMI ではない — [Digital Twins for Intelligent Intersections review, arXiv 2510.05374](https://arxiv.org/pdf/2510.05374)。
→ **我々の SUMO ライブ連成(TraCI・`src/society/transit_live.py`)は、交通DTの標準パターンそのものを既にやっている。**

**★ 決定的な事実**: **社会的/行動的なエージェント状態を交換する標準は、どこにも存在しない。**
USD にも IFC にも CityGML にも 3D Tiles にも DTDL にも FMI にも、**信念・関係・closeness tier・発話のスキーマは無い**。
**幾何と軌跡はきれいに相互運用できるが、意味論は相互運用できない。**

**したがって主張できることの強さ順**:
1. **最強かつ実現可能**: 「エージェント軌跡を OpenUSD `UsdGeomPointInstancer` の time sample として書き出し、街の基盤は 3D Tiles / CityGML として取り込む」= **可視化/幾何レベルの統合**。Python のみ・GPU 不要・ベンダロックイン無し。**正直で検証可能**。
2. **企業向けには最強だが未実装**: シムを **FMI 3.0 co-simulation FMU** として包む。これがあれば実企業DTのマスタが我々をコンポーネントとして駆動できる。(PythonFMU / FMPy が候補だが **2026 年時点の FMI 3.0 Python 書き出し経路は UNVERIFIED**)
3. 相手が Azure のときだけ: DTDL。
4. **主張してはいけない**: 社会モデルそのものの意味論的相互運用。

**推奨する言い方**: 「**OpenUSD へ書き出し、3D Tiles を取り込むので、企業デジタルツインが使うのと同じ可視化パイプラインに載る**」。**FMU が実在するまで co-simulation は主張しない。**

### 5.8 評価(P4)

| 軸 | |
|---|---|
| ①手順 | **(a) 安い版**: 新規 `scripts/export_usd.py` — `pip install usd-core` → `scene3d/tracks.bin`(P0)を読み `UsdGeomPointInstancer` の `positions`/`orientations`/`protoIndices`/**`ids`** を **毎 step の time sample** として書く(velocities は書かない)。静的な街は `buildings.glb` を Blender headless で一度だけ USD 化。→ `runs/<name>/scene3d/shibuya_sim.usdc`<br>**(b) 高い版**: Omniverse Kit / Isaac Sim へ載せる。**GPU SKU の RT コア確認が前提**(§5.5) |
| ②工数 | (a) Opus **1.5-2日**(P0 完了後。`export_ue.py` と同型の「変換を Python に一本化」パターンの再演)/ (b) **見積り不能**(UE と同じく実機ゼロ・+ GPU 制約) |
| ③レーン | (a) **レーン3**。ただし依存が pip 1 個で `src/` 無風なので、時間が余ればレーン1 でも成立する<br>(b) やらない(デモ動画オプション以上にしない) |
| ④リスク | (a) 低。**ただし OpenUSD Core Spec 1.0 にアニメーションが含まれない**ため「標準準拠」とは言えない(実装準拠とは言える)<br>(b) 高。RT コア無し GPU なら Isaac Sim は**動かない**。画素非決定が決定論ドクトリンと衝突 |
| ⑤価値 | プレゼン ★★☆(「USD で出ます」は企業聴衆に効く)/ 研究 ★☆☆(**因果には何も足さない**) |
| ⑥ライセンス | usd-core = Apache 2.0 系(Pixar)/ usd-exchange = Apache-2.0 / Omniverse = **2026-05 から本番利用も無償・再配布可** / Cesium for Omniverse = Apache 2.0 |

**判定**: **(a) の USD 書き出しだけをやる**。**Omniverse も Isaac Sim も要らない**。
「企業DTと繋がる」という主張の実弾としては、**USD 書き出し 1 本が最も安く、最も正直**である。

---

## 6. P5: SUMO 連成の深化 — 「交通DT」化と `world.mod` への接続

### 6.1 いま何ができるか(§1.4 の再掲)

- `net`(5,575エッジ・信号推定つき)→ `demand`(OD 6,460台)→ `run`(24h fcd)→ `convert`(144step parquet)が**全段完走済み**。
- ライブ連成(TraCI・タクシー配車)が **k 不変 PASS・同 seed バイト一致 PASS** で go 判定済み。

### 6.2 「交通DT」に足りない 1 ピース = 信号計画の反実仮想

現状の `stage_net` は `netconvert --tls.guess-signals --tls.join --tls.default-type actuated` で**信号を推定して埋め込む**だけで、**信号計画を差し替える口が無い**。

SUMO は追加ファイル(additional-file)で `tlLogic` を**上書き**でき、既存 tls の offset だけを変えることもできる — [SUMO Traffic Lights docs](https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html)。また `edgeData`(meandata)でエッジ単位の平均速度・所要時間を集計できる — [Lane-/Edge-based Traffic Measures](https://sumo.dlr.de/docs/Simulation/Output/Lane-_or_Edge-based_Traffic_Measures.html)。

### 6.3 ★ 具体案: SUMO が `world.mod.edge_speed_scale` の原点を供給する

これが本調査で見つけた**最も費用対効果の高い結合**である。

```
[信号計画 A(現況推定)] --sumo--> edgeData: エッジ別平均速度 v_A
[信号計画 B(反実仮想)] --sumo--> edgeData: エッジ別平均速度 v_B
                    ↓
        scale_e = v_B(e) / v_A(e)   (決定論・乱数ゼロ・純関数)
                    ↓
      conf/worldmod/<name>.yaml の edge_speed_scale へ書き出し
                    ↓
        社会シムを world.mod.enabled=true で回す = 反実仮想ラン
```

- **なぜ効くか**: `world.mod.edge_speed_scale` は計画書で「歩道幅の代理」とされているが、**係数の原点(実測 1.0)が測れていない**という自認がある(`docs/research/plateau-2025-update-notes.md:146-147`)。SUMO の edgeData は**そのエッジで実際に何 m/s 出るか**を返すので、係数を無次元の仮定値から**シミュレートされた実量の比**に格上げできる。
- **なぜ安全か**: 完全にオフライン・一方向・ラン前に確定。シム実行中に SUMO は動かない(ライブ連成とは別物)。`world.mod` は既に「ワールド構築時に一度だけ・決定論・乱数ゼロ」(`src/society/world/worldmod.py:3-6`)なので、そこへ数字を流し込むだけ。
- **研究上の意味**: 計画書 §3 の **H_B(時空間プリズム内異質性)**が要求する「edge 走行時間を第一級の改変可能属性に」(同 §3 の H_B 行)を、**仮定ではなく交通シミュから供給**できる。「信号計画を変えると誰が誰に会うかが変わる」という A 系反実仮想の**入力側が実測ベース**になる。

### 6.4 差分の具体

| ファイル | 差分 |
|---|---|
| `scripts/sumo_pipeline.py` | ① `stage_net` に `--tls-plan <file>` を追加(additional-file を `sumo` の `-a` に渡すだけ・net は再生成しない=A/B で net バイト同一を保証) ② `stage_run` に `--edgedata` を追加(`edgeData` additional + `--tripinfo-output`)③ 新 `stage_edgestats`: edgeData XML → `panel/sumo_edge_speed.parquet` |
| **新規** `scripts/make_worldmod_from_sumo.py` | A/B の `sumo_edge_speed.parquet` 2 本 → SUMO エッジ id を OSM エッジ (u,v) へ逆写像(`sumo_pipeline` の投影ユーティリティを再利用)→ `conf/worldmod/<name>.yaml` を生成。**マッチしなかったエッジ数を正直に報告**(既存 `sumo_pipeline` の「落とした数を報告する(捏造しない)」流儀を継承・`scripts/sumo_pipeline.py:49`) |
| `src/` | **変更ゼロ** |

### 6.5 評価

| 軸 | |
|---|---|
| ①手順 | 上表。既存の投影・TAZ・エッジ写像コードを再利用できるのが大きい |
| ②工数 | Opus **2-3日**(SUMO 実機が既に入っている前提。骨格=`--tls-plan` と `edgeData` だけならレーン1 で 1日) |
| ③レーン | **レーン3 本命**(A 反実仮想と同時)。ただし `stage_edgestats` だけならレーン1 に置いても `src/` 無風 |
| ④リスク | 中。SUMO エッジ ↔ OSM エッジの逆写像が最大の難所(`convert` stage で座標変換は済んでいるが id 対応表は無い)。**信号計画 B の妥当性**は主張できない(現況推定 A 自体が近似だと `sumo_pipeline.py:46` が自認)→ **絶対値ではなく A/B 比のみ**を使う設計にすべき |
| ⑤価値 | プレゼン ★★☆(「信号を変えたら出会いが変わる」は語れる)/ 研究 ★★★(**H_B の入力を実測化・反実仮想の原点を定義**) |
| ⑥ライセンス | SUMO = **EPL 2.0**(Eclipse)。`pip install eclipse-sumo` で入る(`scripts/sumo_pipeline.py:27-30` に導入経路が実装済み)。無償 |

### 6.6 業界文脈(Web)

- SUMO を物理道路構成の DT として使い、抽出した交通量の下で 21 通りの信号設定を試し、最適設定を実信号へ返す**双方向**ループ — [Digital Twin-Aided Municipal Traffic Control (SUMO Conf 2025)](https://sumo.dlr.de/pdf/2025/pre-print-2619.pdf)。
- 交通カウンタの連続データストリームを実時間で流し込む motorway DT — [Kušić & Schumann, Building a Motorway Digital Twin in SUMO](https://www.semanticscholar.org/paper/d2b3bff00ea55cbdfd13be806eff25b34ebc2acc)。
- Google の「都市モビリティ DT を大規模較正する」記事 — [Urban mobility solutions: Calibrating digital twins at scale](https://research.google/blog/urban-mobility-solutions-calibrating-digital-twins-at-scale/)。
  → **我々のやろうとしていること(信号 A/B の反実仮想)は業界の標準的な DT 用途そのもの**。差分は「下流に社会シムがぶら下がる」点で、そこが新しい。

---

## 7. P6: ライブ連成 vs 事後リプレイ — ドクトリンとの整合

### 7.1 概念整理(ここを間違えると全部が濁る)

DT の標準的分類は **Kritzinger et al. 2018**(IFAC INCOM)の 3 段階 — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2405896318316021) / [TU Wien repositum](https://repositum.tuwien.at/handle/20.500.12708/176517):

| 段階 | データフロー | 我々 |
|---|---|---|
| **Digital Model (DM)** | 自動データ交換なし | ← **本線の 10日ランはこれ**(較正で一度取り込むだけ) |
| **Digital Shadow (DS)** | 物理→デジタルの**一方向自動** | ← P7(センサー同化)を入れるとここ |
| **Digital Twin (DT)** | **双方向自動**。仮想が物理へ介入する | 我々は目指さない(渋谷の実信号を変える手段が無い) |

**結論として言うべきこと**: 我々は **Digital Model / 限定的 Digital Shadow** であり、Kritzinger 自身「最上位段階(DT)の文献は乏しく、DM/DS の方が多い」と書いている。**「うちは DT じゃない」と正確に言う方が、DT を名乗って詰められるより強い。**

### 7.2 なぜ「ライブ」を安易に入れてはいけないか

リポの原則:
- 観測は L1 を読むだけ(再生専用 60 本)。
- 決定論(同 seed バイト一致)。ライブ入力は**外部非決定論の唯一の侵入経路**であり、`docs/research/traffic-indirect-effects.md` が「SUMO 固有リスクは外部非決定論のみ」と特定している(devlog E38・`docs/log/devlog-compressed.md:161`)。
- 既にライブ連成(タクシー)を入れた前例があり、そこでは **seed 固定・`--random` 禁止・`--threads 1`・ソート順の決定論配車**という**厳格な条件で決定論を守った**(`scripts/sumo_taxi_bridge.py:12-19`)。
  → **「ライブでも決定論は守れる」ことは既に実証済み**。守り方が高くつくだけ。

### 7.3 ★ 具体案: 「追いかけ再生(chase playback)」= 壊れないライブっぽさ

**発見**: L1 はラン中に**セグメント書き出し**されている。

```
src/society/observer/logger.py:5-8
  D16 セグメント化: checkpoint 連携で flush_segment() が溜まったログを part-N として
  書き出しメモリを解放する。finalize の flush() は part 群 + 残りバッファを結合して
  従来どおり単一の l1_events.parquet 等を出す(part は削除)。
```
- 実体: `l1_events.part-NNNN.parquet`(`logger.py:107,121,131`)、resume 時は既存 part の最大 index+1 から採番(`logger.py:104-109`)。
- **finalize で結合して part は削除される**(`logger.py:155-177`)ので、ラン中にだけ存在する。

**提案**: 新規 `scripts/watch_replay.py`(仮)
1. `runs/<name>/l1_events.part-*.parquet` を **mtime 順に監視**(既存の `scripts/watchdog.py` と同じ流儀)。
2. 新しい part が**完全に書き終わった**もの(次の part が現れた=直前は確定、というルールで half-written を読まない)だけを `export_3d.export_run` の増分版に食わせ、`tracks.bin`(P0)へ **append** する。
3. ビューア側は `tracks_meta.json` の `nSteps` を数秒ごとに読み直して**タイムラインの右端を伸ばす**。ユーザーは常に「N step 遅れの現在」を見る。

- **なぜ壊れないか**: シム側に read も write も一切しない。part ファイルは**シムが自発的に書いたもの**で、消費者の有無に挙動が依存しない。`--low-mem` の row-group ストリーム読みが既にある(`scripts/export_3d.py:9-14`)ので増分読みの土台もある。
- **見せ方**: 「10日ランが今 3日目の 14:20 を走っています」を**ラン中ずっと投影しておける**。10日連続ラン(8/16-26)の期間、これは事実上そのままデモになる。
- **正直な注記**: これは Digital Shadow ではない(物理→デジタルの流れが無い)。**単に「自分の計算を遅延つきで見ている」**。プレゼンでそう言い切るべき。

### 7.4 評価

| 軸 | |
|---|---|
| ①手順 | 新規 `scripts/watch_replay.py` + `export_3d` に増分 append モード。**`src/` 変更ゼロ・`viz/make_viewer3d.py` はメタ再読込のみ ~30行** |
| ②工数 | Opus **1-1.5日**(P0 の後) |
| ③レーン | **レーン1 で実装 → レーン2 で運用**。レーン2 の「main に入れてよいのは L1 を読むだけの観測系のみ」に完全適合 |
| ④リスク | 低。唯一の注意=**書きかけ part を読まない**規律(「次の part が出たら直前を確定」ルール)と、checkpoint が有効なランでのみ part が出る点(`logger.py:157`「part が無い(=checkpoint 無効)場合は従来どおり」) |
| ⑤価値 | プレゼン ★★★(**10日ラン期間中ずっと動いている画面**は最も強い提出物になりうる)/ 研究 ★★☆(**長時間ランの異常を早期発見できる**=運用価値。`scripts/watchdog.py` の視覚版) |
| ⑥ライセンス | 自作 |

---

## 8. P7: 人流実データ同化 — 較正フェーズ限定の「センサー同化」

### 8.1 いま持っているもの

`data/jinryu/`(`SOURCE.md` 実査):
- 一次データ: **国交省「全国の人流オープンデータ」(1kmメッシュ・Agoop GPS 由来換算人口値)**。ライセンス=**政府標準利用規約2.0(CC BY 4.0 互換)** で加工・再配布可。リポにコミット済み。
- `shibuya_mesh1km_2019_2021.csv`(6メッシュ×36ヶ月×9区分=1,944行・**生データ**)。
- **`shibuya_concurrent_144step_curve.csv`(派生物)**: 2019年コア4メッシュ平均を 昼(11-14時)/深夜(1-4時)/終日 の 3 アンカーに拘束し、公表された日内形状(ドコモ区ビジョン)で内挿した**平日/休日の10分刻み 144step テーブル**。
- 値の意味は明確: 滞在時間按分の**同時滞在(concurrent presence)の期待値**であって累積通行量(footfall)ではない。

**★ そして今これは使われていない**: `src/society/world/presence.py:16` に「在場実測曲線(`data/jinryu/shibuya_concurrent_144step_curve.csv`)は **v1 では使わない(将来拡張点)**」と明記。
grep の結果、`src/` から `data/jinryu` を読む箇所はこのコメント 1 行だけ。**144step の実測曲線が、144step のシムの隣に置かれたまま接続されていない。**

**較正対象を正確に特定しておく**(ここを取り違えると無意味な較正になる):
- `presence.py` は **日次選択のみ**の純関数(層別 resident/duty/workday_shift/cadence/stochastic を `present_cap` 上限で層優先充足)。**k 非依存・trait 非依存**を明示設計している(`src/society/world/presence.py:8-11`)。
- **日内の出入り(朝流入→夕退出)は別機構**: 「日内の出入り(朝流入→夕退出)は既存の visitor 入退場機構が担う。ここは**日次選択のみ**を行う」(`presence.py:15`)。実体は `cognition/routine.py` 系 + conf の `world.exit_prob` / `world.outside_steps`(`conf/config.yaml:239-241`)。
- したがって **144step 曲線が拘束できるのは「日内の在場曲線の形」** であり、較正すべきパラメータは
  (a) `present_cap`(振幅)(b) visitor の到着/退出時刻分布(形)(c) `exit_prob`/`outside_steps`(日中の出入り)
  であって、`presence.py` の層別規則そのものではない。**presence.py の k/trait 非依存性は絶対に壊さない。**

### 8.2 企業DTがやっていること(Web)

歩行者 ABM へのデータ同化は方法論が確立している:
- **EnKF(アンサンブルカルマンフィルタ)を ABM に結合**して実時間で群衆モデルの精度を改善 — [Coupling an agent-based model and an ensemble Kalman filter for real-time crowd modelling, R. Soc. Open Sci. 2024](https://royalsocietypublishing.org/doi/10.1098/rsos.231553) / [PMC](https://ncbi.nlm.nih.gov/pmc/articles/PMC11017988)。Grand Central Station の実データで実演。
- **LETKF** で監視カメラの歩行者軌跡とメゾ群衆モデルを結合し、密度と行動パラメータを同時推定 — [arXiv 2605.29968](https://arxiv.org/abs/2605.29968)。
- 「実時間 ABM は時間とともに実系から乖離する。走行中の ABM へ新観測をどう取り込むかに合意は無い」— 同 R. Soc. 論文の問題設定。

### 8.3 ★ 具体案: 同化を「較正」に閉じ込める(本体の決定論を一切壊さない)

**やってはいけないこと**: ラン中に人流データでエージェント位置を補正する。これは
(a) 決定論を壊し (b) 「創発の観察」を「実データへのフィッティング」にすり替え (c) k の因果解釈を消す。

**やるべきこと**: **オフライン・ラン前・パラメータ推定にだけ**同化を使う。

```
既存: 在場曲線を決める conf(present_cap / exit_prob / outside_steps / visitor 到着退出)は手置き
      = 一度も実測曲線と突き合わせていない
 ↓
提案: scripts/calibrate_presence.py(新規・mock backend で回す=LLM 呼びゼロ)
   観測    = L1 から step 毎の在場人数を復元(既存 observe 系の再利用)
   目的関数 = Σ_step ( sim在場(step)/present_cap − jinryu実測曲線(step)/実測ピーク )²  ← 形を合わせる
              ※絶対値ではなく正規化形状で合わせる(1kmメッシュ月次平均を絶対人数として使わない)
   探索     = 事前に列挙した少数パラメータの決定論グリッド(seed 固定・CRN)
   出力     = conf/presence/<profile>.yaml + calib_presence_report.md(残差・帯・不適合の正直な記載)
 ↓
本番ラン: そのプロファイルを固定して回す(ラン中の同化はゼロ・決定論無傷)
```

既存 `scripts/calibrate_report.py`(較正ツールキット)の REALITY 帯の作法をそのまま流用できる
(第62バッチで「直接統計が不在なら捏造せず出典つきプロキシ帯を置く」流儀が確立している)。

- **これは「センサー同化」の正当な弱版**である。Kritzinger の分類で言えば **DM のまま**(自動データフローが無い=人間がプロファイルを固定する)。DS を名乗るなら「日次で自動再較正する」まで行く必要があるが、**そこまで行く必要は無い**。
- 既存の `scripts/calibrate_report.py`(較正ツールキット)と `presence.py` の「将来拡張点」宣言に素直に接続する。
- **正直に書くべき限界**: (i) 1km メッシュ×月次平均なので**空間解像度が桁で足りない**(シム bbox 2.9km² に対しメッシュ 1km²・4枚)。(ii) 2019-2021 のデータで現在を較正している。(iii) 日内形状は「公表された形状で内挿」した**派生物**であって実測 10分値ではない(`SOURCE.md` が自認)。→ **点推定ではなく帯(区間)として合わせるべき**。

### 8.4 評価

| 軸 | |
|---|---|
| ①手順 | 新規 `scripts/calibrate_presence.py` + `conf/presence/` プロファイル置き場。**`src/` 変更ゼロ**(較正するのは既存 conf キーの値だけ)。ラン中の挙動変更ゼロ |
| ②工数 | Opus **2-3日**(mock で回せるので GPU 不要) |
| ③レーン | **レーン3**。ただし「実測曲線が接続されていない」事実自体はレーン1で潰す価値がある(較正の当てはまりを一度も測っていない) |
| ④リスク | 中。**過剰適合の誘惑**が最大のリスク。1km/月次のデータで 10分/個体の挙動を較正しにいくと、事前登録の趣旨を壊す。→ **較正するパラメータを事前に列挙して固定**(事前登録の作法を D0 から流用) |
| ⑤価値 | プレゼン ★☆☆(グラフ 1 枚)/ 研究 ★★★(**「現実整合をどこまで主張できるか」の上界を数字で言える**ようになる。査読で必ず聞かれる質問への答え) |
| ⑥ライセンス | 政府標準利用規約2.0 / CC BY 4.0 互換。出典表示例まで `SOURCE.md` に用意済み |

---

## 9. 見た目と因果を混同しないための注記(全経路共通)

本調査の評価軸が「プレゼン映え」と「研究価値」を分けているのは正しい。ABM 可視化の文献も同じ警告を出している:

- 「適切な視覚表現は複雑なモデル構造と挙動を伝える**説得的**手段である」一方で、「GUI のスクリーンショットや複雑な 3D 表現が論文に何かを足しているか、検討する価値がある」— [Design Guidelines for Agent Based Model Visualization, JASSS 12(2)1](https://www.jasss.org/12/2/1.html)、[The Practice of Agent-Based Model Visualization, Artificial Life 20(2)](https://direct.mit.edu/artl/article/20/2/271/2766/The-Practice-of-Agent-Based-Model-Visualization)。
- モデル信頼性評価の第一歩は **face validity**(詳しい人が見て尤もらしいか)だが、それは検証の**入口**であって出口ではない — [Methods That Support the Validation of Agent-Based Models, JASSS 27(1)11](https://www.jasss.org/27/1/11.html)。

**運用ルール案**: 3D 経路の成果物には必ず「この映像は L1 の位置ログの再生であり、幾何が挙動に与える影響は別条件ランで測る」旨を焼き込む。既に `export_3d.py:159 PLATEAU_ATTRIBUTION` で帰属表記を焼き込む前例があるので、同じ場所に 1 行足せばよい。

なお、リポの正典もこの結論と整合している: 「viz は**読み取り専用の下流**。sim は viz を一切知らない(出力形式だけ契約)。Unity/Web の選択は viz アダプタの差し替えで、sim には非影響」「**数万体の個体軌跡同時描画は非現実的→集約表現へ**」(`docs/lit/viz__plateau-pipeline-overview.md`)。
**= どの 3D 経路を選んでも、それは「アダプタの差し替え」であって研究の変更ではない。** この一文をプレゼンに置くと、見た目と因果の混同を自分から断てる。

---

## 10. 推奨ロードマップ(日程に落とす)

### レーン1(〜8/14)— **やるのは 2 つだけ**

| # | 項目 | 工数 | `src/` 変更 | 理由 |
|---|---|---:|---|---|
| **1** | **P0 軌跡バイナリ化**(`export_3d --binary-tracks` + viewer3d reader) | 1.5-2日 | **ゼロ** | 10日ランを再生できるかどうかそのもの。計画書 B-L0 の残タスク①に既記載 |
| **2** | **P6 追いかけ再生**(`scripts/watch_replay.py`) | 1-1.5日 | **ゼロ** | 8/16-26 の 10日間ずっと動く画面になる。レーン2 の凍結原則に完全適合 |

**やらないこと**: P1(Cesium)・P2(UE5)・P3(Unity)・P4(Omniverse)。いずれも 10日ランの成立に寄与せず、提出物文書系(hackathon1-analysis T1-T4)と D17 実験準備の方が優先度が高い(計画書 §2 の明示順位「10日ランの成立と観測 > 提出物文書 > 本計画の仕込み」)。

### レーン2(8/15〜8/30)— コード凍結

- **P6 を運用**(10日ラン中ずっと投影)。
- **P2(UE5)は本選内では推奨しない**。§3B.10 の実データ点(PLATEAU→UE 初回インポートだけで半日・3GB DL が展開 80GB+・16GB RAM でクラッシュ)と §3B.2 のバージョン三竦みを踏まえると、**8/27-29 の 3日は解析と提出物に使うべき**。
  どうしてもやるなら **UE 5.5.4 + PLATEAU SDK v3.2.2 に固定・渋谷 1-2km²・200体・シリンダのまま・Temporal Samples=1**まで削り、**入力は既存の `demo_event_200a3d/scene3d/sim_ue.json`(19.7MB)をそのまま使う**(新規ランを回さない)。

### レーン3(9月〜)— 本番の拡張

| 優先 | 項目 | 依存 | 一言 |
|---|---|---|---|
| 1 | **P5 SUMO 反実仮想 → `world.mod.edge_speed_scale`** | 既存 SUMO 資産 | **H_B の入力を実測化**。研究価値が最も高い |
| 2 | **`plateau_extract.py --tran`(歩道面)+ 歩行空間ネットワークデータ**(§4.5/§4.6) | なし | B-L2 / H_B の前提。**Unity は要らない** |
| 3 | **P7 較正フェーズ限定の人流同化** | mock で可 | 「現実整合をどこまで主張できるか」の上界を数字で言えるようになる |
| 4 | **P4(a) USD 書き出しのみ**(`pip install usd-core`) | P0 | 「企業DTに繋がる」の最も安い実弾 |
| 5 | P2 UE5 フル(キャラ+VAT) | P0 | 映像品質を上げたいときだけ |
| 6 | P1 Cesium | P0 | 「サーバを立ててよい」判断が出たときだけ |

### 判断を仰ぐべき未決事項

| # | 未決 | 推奨 |
|---|---|---|
| **D-1** | **`file://` 自己完結性を捨ててよいか**(2026-07-18 のユーザー決定) | **捨てない**。P1/Cesium はこの一点で不採用。捨てるなら P1 の価値が一気に上がる |
| **D-2** | **提出動画に UE5 を使うか**(=8/27-29 に 3-5日を割く価値があるか) | **10日ランの解析が終わってから判断**。前もって着手しない |
| **D-3** | **量子化精度**(P0 の 0.05 m/unit) | PLATEAU メッシュと同一の 0.05 を推奨(`export_3d.py:158` と揃う) |
| **D-4** | **「デジタルツイン」という語を提出物で使うか** | **使うなら Kritzinger の分類を添えて「Digital Model である」と明示**(§7.1)。曖昧に DT を名乗ると相互運用の実装を問われる |
| **D-5** | **本選 GPU の SKU 確認**(RT コア有無) | 開放初日に `nvidia-smi` で確認し記録。**ただし 200時間 vLLM 占有なので Isaac Sim は本選中は不可**(§5.5) |
| **D-6** | **既存 UE 設計書の訂正を今入れるか**(§10.5) | **入れる**。コード変更ゼロの文書修正で、後で数日を失うのを防ぐ |

---

## 10.5 リポ文書へ反映すべき訂正(コード変更ゼロ・今すぐ可能)

本調査で、既存の UE 設計書に**事実と異なる/危険な記述**が 3 点見つかった。**いずれも `.md` の修正だけで済む**。

| # | ファイル:行 | 現状 | 訂正 | 根拠 |
|---|---|---|---|---|
| **1** | `viz/unreal/SimReplayActor_DESIGN.md:84-115`(Tick 駆動)+ `:176-183`(検証項目) | `Tick(dt)` で `T += dt * PlaybackSpeed` |**「MRQ 収録時は Tick 駆動が temporal サンプル数だけ倍速になる。Sequencer プロパティトラック駆動へ切り替えるか Temporal Samples=1 にする」**を追記。検証項目に 6 個目として追加 | §3B.7(Epic 公式 + 既知バグ報告) |
| **2** | `viz/unreal/SimReplayActor_DESIGN.md:171` | 「数百〜千体台なら BP で十分実用」 | **「10,000体を狙うなら C++ 一択(外部データ→ISM の transform 変換は BP ~20ms vs C++ 0.3ms = 60倍差)」**を追記 | §3B.6([Nanite+Niagara 100k 実測](https://forums.unrealengine.com/t/nanite-niagara-how-i-do-it-its-supported-since-5-0-using-blueprints-to-export-particle-positions-from-the-gpu-and-c-to-convert-that-data-to-transform-arrays-by-static-mesh/1814048)) |
| **3** | `viz/unreal/README_UE.md:17-27`(環境表) | UE 5.5.4 / SDK v3.2.2 を推奨(**当時は正しく、今も最新**) | **「2026-07 時点でも v3.2.2 が最新=約14ヶ月更新なし。UE 5.6/5.7/5.8 は非対応。日本語を含むパスにプロジェクトを置くとビルドエラー(=本リポの作業ディレクトリは不可)。新しい UE を使うなら Cesium for Unreal + Cesium ion の Japan 3D Buildings 経路」**を追記 | §3B.2 / §3B.3 / §3B.4 |

(いずれも**実装ではなく文書**なので、レーン1 の 30分作業。ただし本メモは読み取り専用調査であり、**修正は行っていない**。)

---

## 11. 調査の限界(正直な記載)

- **UE5 関連の未確認事項**: PLATEAU SDK の `dev/v4` ブランチが UE 5.6+ でビルドできるか(**報告例ゼロ**)。**MassEntity を外部再生データで駆動した前例は 1 件も見つからなかった**(存在しないのか、単に公表されていないのかは区別できない)。Epic Content License の**現行版の正確な改訂文言**(公式ページが 403・PDF で裏取り)。City Sample の群衆キャラが 2025-06 の新 MetaHuman ライセンス側か UE-Only 側か。City Sample コンテンツパックのダウンロードサイズ。生 PLATEAU 3D Tiles が 2026年時点でも `RTC_CENTER` 変換を要するか。UE 5.6 のアニメーション性能数値(Epic 一次情報ではなく二次ブログ)。
- PLATEAU 渋谷 **tran LOD3.0 の被覆面積**は公式に記載を見つけられなかった(§4.8)。**着手前に索引図 `13113_indexmap_op.pdf` で確認すべき**。
- `PLATEAU-RoadNetwork-Generator` の **CLI の有無・歩道リンクの属性スキーマ**は未確認(GUI のみに見える)。
- `UsdGeomPointInstancer` の重い time-sampling についての**公表ベンチマークは存在しない**。§5.3 のサイズ試算は導出値であって出典ではない。
- Isaac Sim Replicator の **エージェント視点(ego camera)は文書化されたワークフローではない**。エージェント数上限も記載なし。
- OGC ER 24-067r1(都市DT相互運用パイロット)の**全文は取得できなかった**。「USD が出てこない」は要約群からの推測であって全文確認ではない。
- FMI 3.0 の **Python FMU 書き出し経路が 2026 年時点で動くか**は未確認。

