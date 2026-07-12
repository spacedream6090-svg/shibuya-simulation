# 擬似視覚(壁による遮蔽)= vision LOS(バッチC)

## 目的とユーザー要望
エージェントが他者・環境を知覚する手段として擬似的な視覚を導入する。建物内に壁があれば、
隔たれたエージェント同士は互いに「見えず」交流できない。実装が重くなりうるので **既定 OFF の
config トグル**で入れ、本番でのみ ON にすればすぐ使える状態にする。

## 何を実装したか(要約)
- `src/society/world/vision.py`(新規): 建物 id + 階から決定論生成した「推定間取り」の壁
  セグメント集合と、2エージェント間の線分交差(LOS)判定。`VisionOccluder`。
- `src/society/world/perception.py`(改修): `hearers_of` / `PerceptIndex` / `build_index` に
  任意の `occluder` を追加。距離・同一階フィルタを通ったペアにだけ LOS 判定を足す。遮蔽器が
  無ければ **従来と完全にバイト一致(遮蔽なし)**。`install_occluder()` でモジュール全体へ
  一括で据える本番トグルの据え付け先を用意。
- `tests/test_vision.py`(新規): 決定論・LOS プリミティブ・同室/壁越し・OFF 一致・mock 24step。

## config キー(案)
`conf/config.yaml` は編集禁止なので**下記を `world:` ブロックに足す提案**(コードは既に
`cfg.get` で安全に読む。キーが無ければ既定 OFF = 完全に従来挙動):

```yaml
world:
  # ...既存...
  # ---- 擬似視覚(壁による遮蔽)。既定 OFF の本番トグル。ON で屋内の間仕切り壁が知覚を切る ----
  vision:
    enabled: false     # true で屋内 LOS 遮蔽を有効化(距離・同一階フィルタ後に壁判定を追加)
    outdoor: false     # true のときだけ屋外も他建物フットプリントで遮蔽(重いので既定 false)
```

`world.vision` 自体が無くても `enabled=false` 相当で動く(`vision.occluder_from_cfg` が None を返す)。

## 間取り(壁)の手続き生成
`viz/make_viewer.py` の `floorLayout(b, f)` と**同系列**で生成する:
- seed = `FNV-1a(building.id) + (floor+50)*2654435761`(uint32)。
- 乱数 = **mulberry32**。`_hash` / `_rng` / `_cols` は JS 実装と**ビット一致**(200 seed × 20 draw の
  独立エミュレータ照合、および `tests/test_vision.py::test_rng_hash_bit_exact_to_viewer` で回帰)。
- 区画数 n: その階に POI があれば `min(10, POI数)`(cols 前に乱数を消費しない=ビューアと一致)。
  無ければ建物 kind → 用途プール長から `2 + floor(rng()*min(4, pool_len-1))`、重複回避ループの
  乱数消費数もビューアと一致(プール内は相異なる語なので重複判定は index 一致と等価)。
- 幾何: 長辺沿いの通路(band = 短辺の 9%)、両側を `_cols` で重み付き列分割した部屋、中央コア
  (min(w,h)*0.13 の正方形=EV/階段)。

**壁の導出(本層で追加。ビューアは壁を描かない=区画を塗るだけ)**:
- 各部屋の通路側の辺 = **開口部(ドア)付きの壁**(辺中央に半幅 0.8m の開口)。
- 同じ側の隣接部屋の間仕切り = **無開口の壁**(部屋間は通路経由でのみ接続)。
- コアの4辺 = 無開口の壁。
→ 同室・開口部越しは可視、壁を挟むと不可視、という所望の挙動になる。

LOS = 端点接触/共線は非交差扱い(寛容側=ドアや端点で誤って塞がない)の真交差判定。

## 決定論・no-fingerprint
- 乱数ストリームは一切引かない(壁は hash ベース)。壁は `(building_id, floor)` でキャッシュ。
- `hearers_of` の返り値は従来どおり `agent_id` 昇順。set は使うが返り値順序に影響しない。
- vision/perception は座標・幾何しか見ない(grievance/efficacy 等の因子語を書かない)。

## 性能(マイクロベンチ)
実地図 `data/shibuya_osm.json`、代表建物(大規模 station、footprint 57 頂点、壁 11 セグメント)、
centroid±8m の点対で計測(Python 3.12, Win):

| 判定 | 1万回 | 1判定あたり |
|---|---|---|
| `segment_blocked`(屋内、壁11本) | 34 ms | 3.4 us |
| `VisionOccluder.blocks`(屋内、壁キャッシュ込み) | 36 ms | 3.6 us |
| `VisionOccluder.blocks`(屋外、1181 建物、bbox 前フィルタ) | 191 ms | 19 us |

**1 step 換算の見積り**: 遮蔽器は「距離・文脈フィルタを通ったペア」にだけ呼ばれる。屋内は
同一建物・同一階の同居者どうし(空間セル局在で近傍のみ)なので評価ペア数は総当たりよりずっと
小さい。屋内 3.6 us/ペアなら、1 step に 1万ペア評価しても ~36 ms/step。開発規模
(n=10〜40)では 1 step あたり 1ms 未満で無視できる。屋外は 5倍重く(街路は建物局在が効かず
全建物走査)1万ペアで ~190 ms/step になりうる → **既定 OFF**の妥当性。

## エンジンとビューアの間取り一致性(実態と妥協点)
**壁の幾何(間取り)はビューアと同系列**で、hash/rng/cols がビット一致なので、POI のある階では
区画割りがビューアと一致し、POI の無い階でも同じ生成器(kind ベース)で「同種」の部屋になる。
ただし**完全一致しない2点**を正直に記す:

1. **エージェント位置がそもそも別物**(最重要)。エンジンの屋内座標は `centroid ± 8m` の
   ジッタ(就寝は centroid 丁度)で、部屋に配置されていない。ビューアは表示時に
   `_agentSpot(b,f,id,lay)` で**区画内へ再配置**する別ロジック。したがって本層の LOS は
   「エンジンの実座標」上の物理的に一貫した遮蔽であって、ビューアが描く部屋メンバーシップの
   再現ではない。centroid 近傍にコアや通路壁が通るため occlusion 自体は起きる(=現状
   「同一階の全員が聞こえる」に空間構造が入る)が、どの部屋かは一致しない。
2. **guide(実フロアガイド)由来の用途**は本層の生成器では未使用(POI が無い guide 一致
   建物で、ビューアは guide.use のプール、本層は kind のプールを使う → 区画数が食い違う)。
   主要ビルは POI も持つため POI 経路が優先され実害は小さいが、guide のみの階では乖離しうる。

**将来の統一(1段落提案)**: 決定版は `_agentSpot` の区画配置ロジックをエンジン側へ移し、
`enter_building` 時に各エージェントへ「部屋 + 部屋内座標」を決定論付与して `agent.x/agent.y` を
区画整合にすること。そうすれば (a) LOS が幾何的にも部屋意味的にも一致し、(b) ビューアは
エンジンの座標をそのまま描けて `_agentSpot` を廃せる。あわせて間取り(zones/corridor/core と
guide.use 解決)を**エンジンが正典として生成し、ログ経由でビューアが読む**形にすれば、
JS/Python 二重実装のドリフトも消える。本バッチは既定 OFF のトグルなので、この統一は次段で
安全に載せられる。

## 本番配線(scheduler 差分。別バッチ所有につき本バッチでは未適用)
`perception.py` は city 地図に手が届かないため、ON 化の配線だけ外部で 1 箇所必要。**最小差分**は
シミュ初期化(または `run_step` 冒頭で 1 回)に据え付ける方式:

```python
# 例: simulation.Simulation.__init__ の末尾、または scheduler.run_step の冒頭で 1 回だけ
from ..world import vision
from ..world import perception
perception.install_occluder(vision.occluder_from_cfg(self.city, self.cfg))
# enabled=false（既定）なら occluder_from_cfg は None を返す → install(None) = 従来と完全同一。
```

これだけで `build_index` / `_apply` の live 走査を含む**全 hearers_of 呼び出し**に一括で効く
(索引/legacy 双方が据え付けの遮蔽器へ後退する)。明示的に通したい場合は各呼び出しへ
`occluder=` を渡す経路も用意済み(`build_index(..., occluder=occ)`、
`hearers_of(..., occluder=occ)`)。

## 既知の制限
- centroid ジッタ位置ゆえ、コア内や footprint 外にジッタした点で occlusion が直感と外れうる
  (上記統一で解消)。
- 屋外遮蔽は全建物走査(bbox 前フィルタのみ)で重い → 既定 OFF、本番の必要時のみ。
- 別バッチ所有 `scheduler._gov` に既知バグ(config に `government` ブロックが無いと
  `OmegaConf.to_container(plain dict)` が落ちる)。baseline の mock ランも同様に落ちるため、
  mock 24step テストは `government.enabled=false` を渡して回避している(vision とは無関係)。
