# PLATEAU 2025年度版 更新手順メモ(B-L0 / 2026-07-29)

対象: `data/plateau/` の生成元と、**2025年度版データセットへ更新する場合**の手順・期待差分・確認事項。
本メモの作成時点で**ダウンロードは行っていない**(手元に展開済みの CityGML を実査しただけ)。
関連: [`docs/plans/twin-physics-vision-affordance-plan.md`](../plans/twin-physics-vision-affordance-plan.md) §2 レーン1 B-L0 /
[`docs/plans/plateau-3d.md`](../plans/plateau-3d.md)(第36バッチの設計と「不採用」記録)/
[`docs/lit/viz__plateau-pipeline-overview.md`](../lit/viz__plateau-pipeline-overview.md)。

データセットページ: <https://www.geospatial.jp/ckan/dataset/plateau-13113-shibuya-ku-2025>

---

## 0. 先に結論 — 「2025年度版への更新」は建物についてはほぼ no-op

**現行 `data/plateau/` は、すでに 2025年度版 CityGML から生成されている。** 根拠:

- `scripts/plateau_extract.py:41 DEFAULT_CITYGML_DIR` =
  `C:\Users\<user>\Desktop\13113_shibuya-ku_pref_2025_citygml_1_op\udx\bldg`
- `scripts/export_3d.py:159 PLATEAU_ATTRIBUTION` = 「…3D都市モデル(渋谷区 **2025年度**)を加工」
- 手元の展開済みデータセット `README.md` = 「3D都市モデル(Project PLATEAU)渋谷区(2025年度)/
  作成年月日 2026年3月13日 / 標準製品仕様書 第5.0版」

したがって B-L0 の残タスクは**版の更新ではなく抽出スコープの拡大**である。
現行パイプラインが読んでいるのは `udx/bldg`(建物)と `udx/dem`(地形)、および
`--extras` 経路の `udx/ubld`(地下街)・`udx/brid`(橋)だけで、
**`udx/tran`(道路)・`udx/frn`(都市設備)・`udx/veg`(植生)は一度も抽出していない**。
道路 LOD3.0 の歩道ポリゴンはこの `udx/tran` にあり、B-L2 / H_B の歩行ネットワークに直結する。

---

## 1. 現行 `data/plateau/` の生成元

| 成果物 | 生成元 | 消費者 |
|---|---|---|
| `plateau_mesh.npz`(V 1,107,132 / F 590,670 / building_offsets 6,312)<br>`plateau_index.json`(6,311棟) | `scripts/plateau_extract.py`(既定=`run`) | `scripts/export_3d.py --plateau` |
| `terrain.npz`(heights 921×1088 float32)+ `terrain.json`(cell 2.0m) | `plateau_extract.py --terrain`(`udx/dem`) | `export_3d --plateau` / **`src/society/world/elevation.py`(シム本体で唯一 `data/plateau/` を読む箇所・`world.elevation.enabled` 既定 OFF・表示/観測専用)** |
| `extras.npz` + `extras.json`(ubld 6,256三角形 / brid 15,025三角形) | `plateau_extract.py --extras`(`udx/ubld`・`udx/brid`) | `export_3d --plateau` |
| `plateau_match.json`(matches 3,531 / unmatched_osm 3,679 / unmatched_plateau 2,780) | `scripts/match_plateau.py`(重心 kNN 25m → 0.5m ラスタ IoU ≥ 0.4 の貪欲マッチ) | `export_3d --plateau` |

`plateau_index.json` の `params` 実測:
`origin_latlon=[35.6595,139.70062]`(スクランブル交差点)/ `buffer_m=150` /
`mesh_codes=["53393585","53393586","53393595","53393596"]`(3次メッシュ4タイル)/
`latlon_bbox=[35.65260,139.68931,35.66645,139.71002]`(≈ 1.87km × 1.54km ≈ **2.9km²**)/
`dem_radius_m=50`・`dem_n_points=2522`・`ground0=15.18`(`ground0_source="dem"`)/
`counts={skipped_clip:3224, holes_ignored:180, lod1:3250, lod2:3061}`。

> **注意**: `plateau_extract.py --map` と `match_plateau.py --osm` の**既定は `data/shibuya_osm.json`** だが、
> 現行 `plateau_match.json` は 3,531 + 3,679 = **7,210 = `data/shibuya_osm_wide_v7.json` の建物数**なので、
> 実際には **wide_v7 を明示指定して回されている**。再実行時に既定のまま流すと照合対象がすり替わる。

パイプラインは **sim 非依存の一方向**: CityGML → `data/plateau/` → `scene3d/` → `viewer3d.html`。
シム本体への影響は `world.elevation`(既定 OFF)経由の `terrain.npz` だけ。

---

## 2. 2025年度版データセットの内容(手元 README.md の実測値)

| モデル | LOD と整備範囲 |
|---|---|
| 建築物 | LOD1 15.11km² **41,626棟**(区内全域)/ **LOD2.0 1.16km² 1,917棟** / **LOD2.2 1.41km² 2,658棟**(都市再生緊急整備地域) |
| **交通(道路)** | LOD1 15.11km²(全域)/ LOD2 2.57km² / **LOD3.0 1.41km²(都市再生緊急整備地域)** |
| 都市設備(frn) | LOD1 0.01km²(渋谷駅周辺)/ **LOD3.0 0.08km²(渋谷駅周辺・代々木駅周辺)** |
| 植生(veg) | LOD1 / LOD3 各 0.01km²(渋谷駅周辺) |
| 橋梁(brid) | LOD2.1 58箇所 |
| 地下街(ubld) | LOD1 / LOD4.1 各 0.04km²(渋谷駅周辺地下街) |
| 地形(dem) | LOD1 15.11km²(全域) |
| 土地利用 / 災害リスク(浸水・土砂)/ 都市計画決定情報 | LOD1 |

品質: 位置正確度 = 地図情報レベル 2500。準拠 = 3D都市モデル標準製品仕様書 第5.0版。
ライセンス: 政府標準利用規約(第2.0版)/ **CC BY 4.0** / ODC BY / ODbL から利用者が選択、
**商用利用を含め無償**([PLATEAU Site Policy](https://www.mlit.go.jp/plateau/site-policy/))。
既存の帰属表記 `export_3d.py:159` はこの条件を満たしている。

配布形式は CityGML のほか **3D Tiles 変換済み**もあるが、本プロジェクトは
`docs/plans/plateau-3d.md`「不採用」の判断(file:// でタイル fetch 不可 = ローカルサーバ必須になり
「ブラウザで開くだけ」の自己完結性を失う)により **CityGML 経路を維持**する。

---

## 3. 更新する場合の手順

前提: シム本体・conf・tests には触らない。`data/plateau/` は生成物なので**更新前に退避**する。

```bash
# 0) 退避(照合率・IoU 分布を後で比較するため)
cp -r data/plateau data/plateau.bak-$(date +%Y%m%d)

# 1) 取得(CityGML 版 zip)。数百MB〜GB 級なので展開先は repo の外に置く
#    https://www.geospatial.jp/ckan/dataset/plateau-13113-shibuya-ku-2025
#    → 13113_shibuya-ku_pref_<年度>_citygml_<版>_op/

# 2) 建物メッシュ + 地形 + 付帯(地下街/橋)を一括(--all = bldg + terrain + extras)
#    --dem-dir / --ubld-dir / --brid-dir は --citygml-dir の親の兄弟を既定に取るので、
#    <DIR>/udx/bldg を渡せば <DIR>/udx/{dem,ubld,brid} が自動で拾われる。
#    ★ --map だけは wide_v7 を明示する(既定は shibuya_osm.json)。
python scripts/plateau_extract.py --all \
  --citygml-dir <DIR>/udx/bldg \
  --map         data/shibuya_osm_wide_v7.json \
  --out-dir     data/plateau

# 3) OSM ⇄ PLATEAU 照合表(★ --osm も wide_v7 を明示)
python scripts/match_plateau.py \
  --index data/plateau/plateau_index.json \
  --osm   data/shibuya_osm_wide_v7.json \
  --out   data/plateau/plateau_match.json

# 4) 再生の作り直し(シム再実行は不要。L1 を読むだけ)
python scripts/export_3d.py runs/<run> --plateau --low-mem
python viz/make_viewer3d.py runs/<run>
```

**検収**(B-L0 の既存基準を流用):
1. `plateau_index.json` の `counts.lod2` / `n_buildings` と、`match_plateau.py` が stdout に出す
   マッチ率・IoU の min/median/max を**更新前後で並べて記録**する(下がっていたら採用しない)。
2. `export_3d.py --plateau` なし(既定)の出力が**従来とバイト同一**であることを確認
   (`data/plateau/` は `--plateau` 経路でしか読まれない = 既定は無風)。
3. `viewer3d.html` のサイズが 80MB ゲート内か(超えたら分離版 `viewer3d_lite.html` + `plateau_mesh.js`)。
4. `world.elevation.enabled=true` で回した既存ランがあるなら、`terrain.npz` の差し替えで
   `move_segment`/`arrive` payload の `z` が変わる。**既定 OFF なので本線ゴールデンは無風**だが、
   elevation ON の比較ランを持っている場合は再現性の観点で退避版を残すこと。

---

## 4. 期待される差分 — 道路 LOD3.0 が B-L2 / H_B に効く見込み

現行の歩行ネットワークは **OSM edge の折れ線 +`world.modes.speeds`** だけで、**幅も面も持たない**。
道路 LOD3.0 は歩車道を **面(MultiSurface)** で持つので、ここが埋まる。

手元の 2025年度 `udx/tran` を実査した結果(シム bbox の 4 タイル):

| タイル | サイズ | `lod3MultiSurface` | `tran:TrafficArea` | `tran:AuxiliaryTrafficArea` |
|---|---:|---:|---:|---:|
| 53393585 | 10MB | 1,348 | 1,836 | 16 |
| 53393586 | 14MB | 1,360 | 1,848 | 78 |
| 53393595 | 13MB | 1,630 | 2,378 | 8 |
| 53393596 | 21MB | 1,444 | 2,044 | 136 |

`codelists/TrafficArea_function.xml` の該当コード: **2000=歩道部 / 2010=自転車歩行者道 /
2020=歩道 / 2030=自転車道**(車道側は 1000=車線・1010=車道交差部・1030=踏切道…)。
`AuxiliaryTrafficArea_function.xml`: 3000=島・3010=交通島・3020=分離帯・5000=植栽・5010=植樹帯。

含意:

- **B-L2(屋外 SFM)**: `sfm_core.Crowd` に渡す「歩ける面」の実形状が取れる。
  現行は `data/crossings_shibuya.json`(横断歩道)+ OSM 線分のみ。
- **A1 `world.mod.歩道幅係数`**: 歩道ポリゴンから実幅を算出でき、係数の**原点(実測 1.0)**を定義できる。
  現状は原点が測れないので係数が無次元の仮定値になる。
- **H_B(時空間プリズム内異質性)**: 到達可能領域が「線」から「面」になり、PPA の面積計算が実測ベースになる。
- **C0(可視行列)**: 視点グリッドを「歩行可能面 2m 格子」で切る要件(計画 §2 C0)を、
  OSM 線分バッファではなく実ポリゴンで満たせる。
- **C0 の実サイネージ位置**: `udx/frn`(都市設備 LOD3.0 0.08km²・渋谷駅/代々木駅周辺)が一次候補。
  手元にタイルは 53393586・53393596 の 2 枚が存在(シム 4 タイルのうち 2 枚)。**中身は未確認**。

---

## 5. 確認事項(未解決)

1. **LOD3.0 の被覆範囲**。README の 1.41km²(都市再生緊急整備地域)に対し、シム bbox は約 2.9km²。
   **全域はカバーしない**。どのリンク/エリアが LOD3 被覆内かの**被覆マップを先に作り**、
   被覆外は現行 OSM 線分にフォールバックする二層設計が要る(被覆の境目で歩行モデルが不連続になる)。
   索引図 `13113_indexmap_op.pdf` と `metadata/udx_13113_pref_2025_op.xml` で範囲を確定できる。
2. **LOD2.2 も 1.41km² のみ**。残りは LOD2.0(1.16km²)/ LOD1(全域)。
   現行抽出の実績は `lod1:3250 / lod2:3061`(LOD2.0 と 2.2 を区別せず "LOD2" とだけ記録している)。
   建物側は再抽出しても総数はほぼ変わらない見込み。
3. **`plateau_extract.py` は bldg 専用**。`SURFACE_TAGS` が `GroundSurface`/`RoofSurface`/`WallSurface` 等の
   建物半題面に固定されており、`tran` を読むには **新規の抽出器が必要**(既存スクリプトの再実行では出てこない)。
   座標系は `*_tran_6697_op.gml` = EPSG:6697 で bldg と同じなので、局所接平面変換はそのまま流用できる。
4. **`--extras` の ubld/brid は 1 タイルずつしか無い**(`ubld`=53393596 のみ・`veg`=53393596 のみ)。
   地下街 LOD4.1 は現行 LOD1 のみ抽出済み(`extras.json` の `counts.lod1:1, lod2:0`)。
5. **更新の必要性そのもの**。本選(10日ラン)に必要なのは L1 の 3D 再生だけで、
   計画書 §2 の判断どおり **現行 npz で足りる**。道路 LOD3 の抽出は B-L2(レーン3)の前提作業であって、
   レーン1 では着手しないのが妥当。
