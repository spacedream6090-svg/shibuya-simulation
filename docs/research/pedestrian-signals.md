# 歩行者用信号の実装調査(第38バッチ / PED-SIG)

作成日: 2026-07-21
体制: Opus Web+コードリサーチ(**調査のみ・コード変更なし**・本ファイル1本)
問い(ユーザー): 「歩行者用信号の実装はできないのか調査してほしい」
前提監査: [traffic-signals-audit.md](traffic-signals-audit.md)(第37バッチ)=
現行シムの信号は **車(traffic mode=od)専用**で、しかも全ランで一度も作用していない。
**歩行者(エージェント)は信号と無関係**(scheduler の移動フェーズに signal 参照ゼロ)。

> **大原則(R1 = 本体無風 / ゴールデン保護)**: 既存の挙動・L1・ゴールデンバイトを一切
> 変えないこと。歩行者信号は **決定論(乱数不要)** で組め(信号は周期関数で、位相は
> `sim_min` から計算できる)、**新 conf ノブ・既定 OFF** にすれば OFF 時バイト一致。
> ON 時は「到着 step / 移動距離が変わる=別ゴールデン」として管理する。

---

## 0. 要約(TL;DR)

- **実装資産の実態**: 信号は3か所に別々の概念として散在するが、**歩行者に効くものは1つも無い**。
  - `world/traffic.py`: 信号 69 基(`data/traffic_features_shibuya.json`)を **od モードの背景車**の
    期待遅延にのみ使用。式は `delay = r²·C/2`(赤率² × 周期 ÷2)。**この式は歩行者にそのまま流用可**。
  - `viz/sfm.py`(Social Force コア): **信号ゲートの実装なし**(目標へ緩和+対人斥力のみ)。
  - `engine/scheduler.py::_phase_move`(L809): 歩行者移動は `budget_m = speeds[mode]×congestion`
    だけ。**signal / crossing への参照は皆無**。
- **データの実態(重要)**: 現行の信号データ(69基)は **`highway=traffic_signals`= 交差点の信号ノード**で、
  **歩行者横断そのもの(`highway=crossing`)は 1 件も入っていない**。しかし **OSM 再取得で歩行者横断が
  豊富に取れることを本調査で実証**(下記 §2、渋谷コア bbox で **信号付き横断 75 か所**を確認)。
- **渋谷スクランブルの実周期(実測・二次)**: **サイクル 140 秒**、歩行者全方向 **青 37 秒 + 青点滅 10 秒 +
  赤 93 秒**(2020-08-25 実測ブログ)。Wikipedia は「周期 120–140 秒/1青 3,000人(PR値)」。
- **設計**: 決定論の位相 `φ(node, sim_min)` を使い、① **メゾ**(10分step=期待待ちを移動予算から差し引く。
  `traffic.py` の既存式を歩行者へ流用)② **前景ミクロ**(SFM で赤=curb 待ち→青=一斉横断=スクランブルの
  見せ場)の2水準。どちらも **新ノブ・既定 OFF・乱数ゼロ=R1安全**。
- **正直な結論**: **メゾ単独では割に合わない**(1横断の期待待ち ≈ 30–38 秒 ≪ 1 step=600 秒。k*/研究には
  効かない)。**価値はほぼ視覚のみ** → **前景ミクロ(SFM スクランブル)を推す**。メゾは「多数横断の
  累積予算削り」を安価に足す程度が妥当。

---

## 1. 実装済み資産の実査

### 1.1 車の信号(`world/traffic.py`)= 歩行者には無関係
- 信号は **`traffic.mode: od` 専用**。既定は `ambient`(config.yaml:194)で **od は全ランで未使用**
  (前バッチ監査済み)。
- 信号ロジック(traffic.py:257-262):
  ```python
  def _signal_delay_m(self, node, speed):
      r = self.signal_red.get(node, 0.0)          # ノード別「赤率」= 0.35 + 0.20·hash
      delay_s = r * r * self.signal_cycle_s * 0.5  # 一様到着の期待待ち = r²·C/2
      return speed * delay_s / STEP_SECONDS        # 距離(m)に換算して移動予算から差し引く
  ```
  - **これは信号の点灯(青/赤の瞬時状態)ではなく、一様到着を仮定した期待待ち時間の近似**。
    「1 step=600s > 周期 90s なので瞬時状態は無意味」という設計判断(traffic.py:100-103 のコメント)。
  - 赤率 `r` は **node id のハッシュ**で決めた擬似値(実測ではない)。周期 `signal_cycle_s` は既定 90s。
  - **効くのは od の背景車だけ**。エージェント(歩行者)には触れない(モジュール冒頭に明記)。
- **流用可能性(◎)**: 上の `r²·C/2` は歩行者にもそのまま使える(§3.1)。歩行者の場合 `r`=歩行者赤の割合、
  `C`=歩行者用サイクル長。**車の実装を1関数コピーするだけでメゾ版が組める**。

### 1.2 SFM コア(`viz/sfm.py`)= 信号ゲートは無い
- `Crowd` クラスは Helbing & Molnár の駆動項+対人斥力のみ。**赤で止める/青で放つ機構は未実装**。
- ただし信号ゲートは **`active` フラグ**で自然に表現できる(§3.2)。`active=False` の個体は
  「力を及ぼさず・受けず・動かない」(sfm.py:89-90, 163)= **curb で赤待ち**にそのまま使える。
- 先行研究の裏付け: [social-force-crowd.md](social-force-crowd.md) §3.2 の **ShibuyaSocial
  (arXiv 2512.18550)** は、渋谷スクランブルの微視モデルに **信号状態 s[t] を sigmoid で明示的に投入**し、
  赤での横断前停止・青直前のフライング横断まで再現している。**「歩行者ミクロ+信号状態」は実証済みの構成**。

### 1.3 歩行者移動(`engine/scheduler.py::_phase_move`, L809-916)= signal 参照ゼロ
- 移動量は `budget_m = float(speeds[agent.trip_mode]) * factor`(混雑係数のみ)。
- 交差点ノードを通っても **信号による減速・停止は一切ない**。到着処理・課金・訪問カウントのみ。
- **差し込み口(メゾ)**: L832-845 の `while budget_m > 0` ループで **ノードを pop するたびに、その
  ノードが信号付き横断なら期待待ちを `budget_m` から引く**。これは traffic.py の od 走行
  (L311-313)が信号ノード通過時に `budget = max(0, budget - _signal_delay_m(...))` とやっているのと
  **完全に同型**。歩行者側に同じ3行を足すだけ。

### 1.4 交差点ノードとエージェント移動の関係
- コア地図(`data/shibuya_osm_wide_v7.json`)のノードは道路グラフの頂点。エージェントは
  edge を辿って node を通過する。**信号付き横断は「特定 node の通過にコストを乗せる」で表現できる**
  (専用ジオメトリ不要)。
- **注意**: 現行コア地図のノードは属性 `id/x/y/name/poi/layer/gateway` のみ(下記 §2)。
  **横断・信号のタグは保持されていない** → サイドカー(traffic_features 系)で外付けするのが疎結合。

---

## 2. データ: 渋谷の歩行者信号は取れるか(**実証済み**)

### 2.1 手持ち地図には無い
- 派生コア地図 `data/shibuya_osm_wide_v7.json` のノード属性は `{id,x,y,name,poi,layer,gateway}` のみ。
  **`highway=crossing` / `crossing=traffic_signals` タグは投影段階で捨てられている**。
- 現行の交通サイドカー `data/traffic_features_shibuya.json` の `signals`(69 基)は
  `build_traffic.py` が **`highway=traffic_signals`(交差点の信号ノード)だけ**を抽出したもの。
  **歩行者横断(`highway=crossing`)は抽出対象外**。

### 2.2 OSM 再取得で歩行者横断が取れる(本調査で Overpass 実行し確認)
渋谷コア bbox `(35.656, 139.695, 35.6625, 139.706)` に対し Overpass API へ本調査で問い合わせた結果
(取得日 2026-07-21):

| タグ | 件数 |
|---|---|
| `highway=crossing`(歩行者横断) | **186** |
| └ うち `crossing=traffic_signals`(**信号付き横断**) | **75**(+ `traffic_signals;marked` 1) |
| └ `crossing=marked`(マーク有・信号なし) | 42 |
| └ `crossing=uncontrolled` / `unmarked` | 36 / 12 |
| `highway=traffic_signals`(交差点信号ノード) | 65 |

- **信号付き横断は 75 か所も取れる**。さらに個々の横断に **豊富なサブタグ**が付く(実例):
  ```json
  {"highway":"traffic_signals","crossing":"traffic_signals","name":"勤労福祉会館前",
   "button_operated":"no","tactile_paving":"yes","traffic_signals:sound":"yes"}
  ```
  → **信号名・押ボタン式か・点字ブロック・音響式(視覚障害者用)** まで手に入る。
- **結論**: 歩行者信号の **位置は OSM 再取得で確実に入手可能**。取得口は既存
  `scripts/build_traffic.py`(Overpass 再利用・決定論投影)。**`highway=crossing` かつ
  `crossing=traffic_signals` を拾う数行を足すだけ**でサイドカーに `crossings` フィールドを追加できる。
- 出典: Overpass API(https://overpass-api.de/api/interpreter)。データ © OpenStreetMap contributors (ODbL)。

### 2.3 周期(サイクル)は OSM には無い → 別途表で与える
- OSM に **青/赤の秒数はほぼ入らない**(信号諸元は非公開が普通)。よって周期は下の実測値/近似表を
  外部から与える(車の od が `signal_cycle_s=90` を config で与えているのと同じ流儀)。

**渋谷スクランブル交差点の実周期**(信頼度つき):

| 項目 | 値 | 出典・確度 |
|---|---|---|
| サイクル長(日中) | **140 秒**(= 2分20秒) | 実測ブログ 2020-08-25・中確度 |
| 歩行者(全方向)青 | **37 秒** | 同上・実測 |
| 歩行者(全方向)青点滅 | **10 秒** | 同上・実測 |
| 歩行者(全方向)赤 | **93 秒** | 同上・実測 |
| 車 東西(旧大山街道)青/黄/赤 | 44 / 3 / 93 秒 | 同上・実測 |
| 車 南北(神宮通り)青/黄/赤 | 33 / 3 / 104 秒 | 同上・実測 |
| サイクル長(別説) | 120 秒 | Wikipedia 等・二次 |
| 1青の横断者数 | 「多いとき 3,000人以上」 | **センター街 PR値・低確度**(堅くは 1,000人以上) |

- **誠実性**: 上の秒数は **信号愛好家ブログの単発実測**(一次公的資料ではない)。曜日・時間帯・
  交通状況で可変とブログ自身が注記。**「日中の代表オーダー」として扱う**。夜間値・全赤時間は未確認。
- スクランブル以外の一般交差点の歩行者青は「概ね 20–50 秒 / サイクル 100–160 秒」程度が一般値
  だが、渋谷区内の個別交差点諸元は未確認 → **サイクル既定 = 140s、歩行者青 = 37s(+点滅10s)を代表
  値**とし、交差点別に上書き可能にする。
- 出典:
  - 渋谷スクランブル信号サイクル(実測秒数): https://www.shingou-saikuru.com/2019/01/shibuya-sta.html
  - 渋谷スクランブル交差点 — Wikipedia(周期・1青3,000人はPR値の注記): https://ja.wikipedia.org/wiki/渋谷スクランブル交差点

---

## 3. 設計案(2 水準)

共通の核: **決定論の信号位相**。乱数を一切引かない(R1 安全)。
```
# ノードごとに固定オフセット(node id ハッシュ=プロセス非依存)。周期 C、歩行者青 g、赤 red=C-g。
phase(node, sim_min) = ((sim_min*60) + offset(node)) mod C          # 現在位相[秒]
is_green(node, sim_min) = phase(node, sim_min) < g                  # 前景ミクロ用の瞬時状態
E_wait(node) = red² / (2·C)                                         # メゾ用の期待待ち[秒](一様到着)
```
`E_wait = red²/(2C)` は traffic.py の `r²·C/2`(`r=red/C`)と**恒等**。既存式の直接流用。

### 3.1 ① メゾ(既定の 10 分 step)= 期待待ちを移動予算から差し引く
- **やること**: `_phase_move` の node pop 時に、その node が信号付き横断なら
  `budget_m -= speeds[walk] * E_wait(node) / 600` を引く(car od と同型の3行)。
- **数値感(渋谷スクランブル)**: 歩行者青 g=37s / C=140s → red=103s → `E_wait = 103²/(2·140) ≈ 37.9 s`。
  青点滅も渡れるとして g=47s なら `E_wait ≈ 30.9 s`。
  歩行速度 800 m/step → **1 横断あたり `800×37.9/600 ≈ 50 m` の予算削り**(step予算の約 6%)。
- **意味の評価(正直)**: 1 横断 ≈ 50m/約38秒 は **1 step(600秒/800m)に対して小さい**。単発では
  ほぼ埋没する。**多数の信号付き横断を通る長い徒歩でのみ累積的に効く**(4 横断で ~200m=step の 25%)。
  到着 step が 1 ずれる程度の効果で、**k*(研究の主眼)には実質影響しない**。
- **決定論**: `E_wait` は node の純関数、`sim_min` 依存すらしない(平均待ち)→ 乱数ゼロ・完全決定論。
- **ゴールデン保護**: 新ノブ `world.ped_signals.enabled: false`(既定 OFF)。OFF で `_phase_move` は
  現行と 1 命令も変わらない(early-return ガード)→ **バイト一致**。ON は到着 step が変わる=別ゴールデン。

### 3.2 ② 前景ミクロ(SFM 連携)= 青で一斉横断(スクランブルの見せ場)
- **やること**: SFM 領域(スクランブル bbox。`annual.gathering_node` が既に原点最近傍)で、
  各歩行者の `active` を **信号位相でゲート**する:
  - **赤(`is_green=False`)**: curb(横断の手前)に到達した個体を `active=False` で停止 → 待ち行列が
    貯まる(sfm.py の `active` 機構をそのまま使用)。
  - **青(`is_green=True`)**: 待機列を一斉に `active=True` → **数百人が同時横断=レーン形成・対向流**。
    → [social-force-crowd.md](social-force-crowd.md) §3.2 の ShibuyaSocial が再現した現象そのもの。
- **2 形態**(social-force-crowd.md §4 の案a/案b に対応):
  - **案a(オフライン/描画専用・推奨の第一形)**: ビューアの `move_segment.pts` を後処理し、
    スクランブル領域だけ SFM 微視軌跡(信号ゲート付き)に差し替え。**シミュ本体・L1 完全無風**。
    R1 リスクほぼ無・決定論容易・デモ価値ほぼ最大。
  - **案b(オンライン物理)**: sim 内でスクランブル領域だけ SFM を回し、**信号待ちの滞留・横断所要時間を
    `_phase_move` の減速に還流**。因果は動くが既定 OFF ノブ・ゴールデン再取得コストが重い。
- **決定論**: SFM は `noise=0`(既定)で完全決定論。信号位相も乱数なし → **同一入力→同一 float 配列**。
- **時間スケール**: 1 step=600s の内側で dt=0.1s の SFM サブループ(social-force-crowd.md §1)。
  スクランブル領域 n が数十〜低百なら `6000 サブステップ × O(n)` は 1 step 内で現実的。

### 3.3 データ拡張(両水準共通・R1 安全)
- `build_traffic.py` に `highway=crossing`(かつ `crossing=traffic_signals`)抽出を追加 →
  サイドカーに新フィールド `crossings: [{node, x, y, cycle_s, green_s, ...}]`。
- `cycle_s/green_s` は §2.3 の代表値(スクランブルは実測値、他は既定 140/37)を交差点別に埋める。
- 既存 `signals`(車用 69 基)は不変。**新フィールドを足すだけ**なので od の車挙動もバイト不変。

---

## 4. 「やらない」選択肢の根拠(正直に)

- **メゾ単独は割に合わない**: 3.1 の通り **1 横断の期待待ち ≈ 30–38 秒 ≪ 1 step=600 秒**。
  10分 step 粒度では信号待ちが 1 step 未満に埋没し、到着 step を稀に 1 ずらす程度。
  **研究アウトプット(k*/創発)にはまず効かない**。「現実整合の測り」でも歩行者の滞留は
  10分平均に均され観測しづらい。
- **価値はほぼ視覚だけ**: 「赤で貯まり青で一斉に流れる」スクランブルの絵は前景ミクロ(SFM)で初めて
  出る。つまり **投資すべきは②前景ミクロ(できれば案a=描画専用)** であって、①メゾ単独ではない。
- **交差点諸元の不確かさ**: 青/赤の秒数は一次公的資料が乏しく実測ブログ頼み(§2.3)。メゾの期待待ちを
  「正確な待ち時間」と主張するのは誇大。**近似であることを成果物に明記**(traffic-signals-audit の
  誠実性方針を継承)。
- **したがって推奨は**: 「①メゾは **多数横断の累積予算削りとして安価に足す**(車の `_signal_delay_m` を
  歩行者へコピー、既定 OFF)。**主投資は②前景ミクロ案a**(スクランブルの見せ場)」。
  「歩行者を全交差点で厳密に止める meso 信号」は **費用対効果が低く非推奨**。

---

## 5. 工数・段階分割

| 段階 | 内容 | R1 リスク | 工数感 |
|---|---|---|---|
| **P0 データ** | `build_traffic.py` に `highway=crossing`+`crossing=traffic_signals` 抽出を追加 → サイドカー `crossings` 新フィールド。スクランブルに実測周期を埋める | 無(新フィールドのみ・既存不変) | 小(数十行+再生成) |
| **P1 メゾ(任意)** | `_phase_move` の node pop 時に `E_wait` を予算から差し引く。新ノブ `world.ped_signals.enabled:false`。車の `_signal_delay_m` を歩行者へ流用 | 小(既定 OFF でバイト一致・ON は別ゴールデン) | 小〜中 |
| **P2 前景ミクロ案a(推奨)** | ビューア後処理でスクランブル領域だけ SFM(信号ゲート付き `active`)微視軌跡に差し替え。本体・L1 無風 | ほぼ無(描画のみ) | 中(SFM ゲート+ビューア結線) |
| **P3 前景ミクロ案b(条件付き)** | sim 内 SFM で信号滞留を `_phase_move` に還流。新ノブ・既定 OFF・ゴールデン再取得 | 中(到着 step 変化・決定論スモーク要) | 中〜大 |

- **段階の独立性**: P0 は前提。P1 と P2 は独立に入れられる。**推奨順は P0 → P2(案a)→(必要なら)P1 →
  P3**。P1 単独は §4 の通り費用対効果が低いので後回しでよい。
- **決定論スモーク**(P1/P3 で必須): 同 seed で ≤24-step を2回 → L1 が byte 一致(OFF)/
  ON は別ゴールデンで固定。乱数を新たに引かない設計なので `hub.stream` の追加すら不要。

---

## 6. 未確認事項(事実と推測の区別)

- **渋谷スクランブルの青/赤秒数**: 一次公的資料ではなく **単発の実測ブログ**(2020-08-25)。
  夜間値・全赤時間・押ボタン式運用の有無は未確認。曜日/時間帯で可変とブログ自身が注記。
- **一般交差点(渋谷区内)の個別諸元**: 交差点ごとの実サイクルは未確認。代表値 140/37 で近似する前提。
- **1青の横断者数 3,000人**: センター街 PR 値で厳密な根拠が乏しい(Wikipedia が注記)。堅くは 1,000人以上。
- **OSM の横断タグの網羅性**: `crossing=traffic_signals` が付いていても、実地で信号があるとは限らない
  (マッパー依存)。逆に信号付き横断が `highway=traffic_signals` 側に統合されている例もある
  (§2.2 の実例=1 ノードが両タグ持ち)。**位置は取れるが「全数正確」ではない**。
- **SFM のスクランブル密度**: 実映像 407 軌跡は追跡成功率 ~18–22%(ShibuyaSocial)。密度上限
  (LOS F の圧潰)は現行 SFM コアが意図的に非対象(sfm.py 冒頭)。**超高密度の押し合いは再現対象外**。

---

## 付録: 出典一覧(実在確認済み)

- 交通・信号の前提監査(車 od 専用・歩行者無関係): [traffic-signals-audit.md](traffic-signals-audit.md)
- 群衆物理・ShibuyaSocial・信号状態 s[t]・案a/案b: [social-force-crowd.md](social-force-crowd.md) §3.2, §4
- 渋谷スクランブル信号サイクル(実測秒数・140s/青37s+点滅10s/赤93s): https://www.shingou-saikuru.com/2019/01/shibuya-sta.html
- 渋谷スクランブル交差点 — Wikipedia(周期120–140s・1青3,000人=PR値注記): https://ja.wikipedia.org/wiki/渋谷スクランブル交差点
- OSM 歩行者横断タグ(`highway=crossing` / `crossing=traffic_signals`): 本調査 Overpass 実クエリ
  (https://overpass-api.de/api/interpreter・データ © OpenStreetMap contributors, ODbL・取得 2026-07-21)
- ShibuyaSocial(渋谷スクランブル微視モデル・信号 sigmoid): arXiv 2512.18550(social-force-crowd.md 経由)
- コード実査: `src/society/world/traffic.py`(_signal_delay_m)・`viz/sfm.py`(Crowd.active)・
  `src/society/engine/scheduler.py`(_phase_move L809)・`scripts/build_traffic.py`(信号抽出)
</content>
</invoke>
