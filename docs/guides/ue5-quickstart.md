# UE5 クイックスタート — シミュ軌跡を PLATEAU 実形状の渋谷で再生する

UE を初めて触る人向けの **一本道**手順。網羅版は
[`viz/unreal/README_UE.md`](../../viz/unreal/README_UE.md)(8 章構成)にあり、本書はその
**この実機の実パスを埋めた要約版**。迷ったら README_UE の該当節を見る(各手順にリンク)。

> ⚠️ 正直な前提: このリポジトリ側の 2 コマンド(手順 3)は実際に動く。一方、UE 側
> (SDK インポート・エディタ内 Python・位置合わせ)は **この環境の実機では未検証**。UE 本体
> `5.5.4` の存在・SDK zip・CityGML フォルダはディスク上で実査済みだが、**UE の UI 文言や
> Python API はバージョンで差**があり得る。詰まったら手順 6 と README_UE を参照。

**実機の確認事項(2026-07-18 実査)**
- Unreal Engine: `C:\Program Files\Epic Games\UE_5.5`(正確版 **5.5.4** / Changelist 40574608 / `++UE5+Release-5.5`)
- PLATEAU SDK for Unreal v3.2.2 zip(未展開): `C:\Users\塚本翔太\Desktop\PLATEAU-SDK-for-Unreal-v3.2.2.0.zip`
- 渋谷区 2025 CityGML(展開済み): `C:\Users\塚本翔太\Desktop\13113_shibuya-ku_pref_2025_citygml_1_op`
  (この直下に `udx/` と `codelists/` がある = **SDK でインポート時に選ぶのはこのフォルダ自体**)
- 代表ラン: `runs/demo_event_200a3d`(**200 体 × 3 日 = 432 step**。`scene3d/` は未生成なので手順 3 で作る)

---

## 0. これで何ができるか

シミュレーションが吐いた 200 体分のエージェント軌跡(1 日 = 144 step、3 日で 432 step)を、
PLATEAU の**実際の形の渋谷の街**(実形状の建物・道路)に載せ、UE5 のビューポートで視点を自由に
動かしながら**再生ボタンひとつで動かす**ところまでを、コードを一切書かずに通します
(200 体は後述の **sequence モード**で Level Sequence の再生だけで完結する)。

---

## 1. PLATEAU SDK の導入(所要目安 5〜10 分)

参照: [README_UE §0](../../viz/unreal/README_UE.md)

1. `C:\Users\塚本翔太\Desktop\PLATEAU-SDK-for-Unreal-v3.2.2.0.zip` を展開する。中にプラグイン
   フォルダ(`PLATEAU-SDK-for-Unreal` 相当の 1 フォルダ)が入っている。
2. そのフォルダを、**手順 2 で作る UE プロジェクトの `Plugins/` フォルダ**に丸ごと置く
   (`Plugins/` が無ければ作る)。エディタを再起動すると **`PLATEAU`** メニューが出る = OK。
   - UE 5.5.4 に対して SDK は **v3.2.x が対応**(README_UE §0)。この組み合わせは適合。
3. 代替: 展開・配置をしたくなければ、**Fab**(旧マーケットプレイス)から
   「PLATEAU SDK for Unreal」をエンジンに追加してもよい(zip 展開・配置が不要)。

> 注: 手順 1〜2 は「プロジェクト作成前に zip を展開しておく」だけ。プラグインの実際の有効化は
> プロジェクトができてから(手順 2-2)行う。

---

## 2. UE プロジェクト作成 → PLATEAU 都市のインポート(所要目安 15〜30 分・初回 DL 別)

参照: [README_UE §2](../../viz/unreal/README_UE.md) / 公式マニュアル
<https://project-plateau.github.io/PLATEAU-SDK-for-Unreal/manual/ImportCityModels.html>

1. UE 5.5 を起動 →**Games > Blank**(または Third Person)テンプレートで新規プロジェクトを作成。
   作成後、手順 1 のプラグインフォルダをこのプロジェクトの `Plugins/` へ置く(未実施なら)。
2. **Edit → Plugins** で「PLATEAU SDK for Unreal」を有効化 → エディタ再起動 →
   メニューに **`PLATEAU`** が出ることを確認。
3. メニュー **PLATEAU → PLATEAU SDK** → **インポート**タブを開く。
4. インポート元 = **ローカル** を選び、フォルダに
   **`C:\Users\塚本翔太\Desktop\13113_shibuya-ku_pref_2025_citygml_1_op`** を指定
   (= `udx/` と `codelists/` が見える階層フォルダそのもの)。
5. **基準座標系の選択**: 渋谷は関東 → **第9系(EPSG:6677 / JGD2011 平面直角第IX系)**。
6. **基準座標系からのオフセット値の設定**: 下表を入力する(単位 m)。これでレベルの原点
   (0,0,0)が**スクランブル交差点**に一致し、手順 3 の出力(既定 offset=0)とそのまま重なる。

   | 項目 | 値 |
   |---|---|
   | 東西(Easting) | **-12015.952** m |
   | 南北(Northing) | **-37768.576** m |
   | 高さ | **0** m |

   (この値は `scripts/export_ue.py` の `ORIGIN_EPSG6677` と一致。GSI 準拠の算出。高さの起伏は
   手順 5 で吸収する。)
7. **最小/最大 LOD**: 建物 = **LOD2**(道路 `tran` は **LOD1** で十分)。
8. **モデル結合単位**: **主要地物単位**(建物ごとに扱えて後の調整が楽)。
9. インポート実行。CityGML がメッシュ化されてレベルに配置される(数分〜十数分)。

---

## 3. シミュ側の書き出し(このリポジトリで実行・所要目安 3〜10 分)

UE に渡す軌跡を作る。**このリポジトリのルート**
(`c:\Users\塚本翔太\Desktop\shibuya-simulation`)で以下 2 コマンド。

```bash
# 1) 中立 3D シーン(scene.json / tracks.json)を作る
python scripts/export_3d.py runs/demo_event_200a3d

# 2) UE 用に座標変換して sim_ue.json を出す
python scripts/export_ue.py runs/demo_event_200a3d
```

- 出力先: `runs/demo_event_200a3d/scene3d/`
  - `scene.json` / `tracks.json` … 中立 3D シーン(コマンド 1 が生成)
  - `sim_ue.json` … **すでに UE ワールド座標(cm・Z-up・左手系)**の再生データ。UE 側は座標変換しない(コマンド 2 が生成)
- 補足: `scene3d/` が無い状態でコマンド 2 だけ実行しても、`export_ue.py` が内部で
  `export_3d.py` を呼んで自動生成する。上の 2 段で明示的に作っておくと分かりやすい。
- 位置合わせを変えたいときだけコマンド 2 に引数を足す(手順 5):
  `python scripts/export_ue.py runs/demo_event_200a3d --heading 90 --no-yflip`

---

## 4. UE 内 Python で取り込む(sequence モード・所要目安 5〜15 分)

参照: [README_UE §5](../../viz/unreal/README_UE.md)

**★ 200 体は `mode="sequence"` が主経路**。この方式なら **Blueprint も C++ も一切書かず**、
生成された **Level Sequence の再生ボタン**を押すだけで 200 体が動く(1 体 = 1 アクタ + Level
Sequence にトランスフォームキーをベイクする方式。上限 300 体まで対応、本ランは 200 体で範囲内)。

1. **Edit → Plugins** で **Python Editor Script Plugin** を有効化 → エディタ再起動。
2. **Tools → Execute Python Script**、または **Output Log** のコンソールを Python に切り替えて、
   以下を実行(パスは実機のリポジトリ位置に合わせてある):

   ```python
   import sys
   sys.path.append(r"C:/Users/塚本翔太/Desktop/shibuya-simulation/viz/unreal")
   import import_shibuya_sim as imp
   imp.run(
       r"C:/Users/塚本翔太/Desktop/shibuya-simulation/runs/demo_event_200a3d/scene3d",
       mode="sequence",
       max_seq_actors=300,
   )
   ```

3. 実行後、Content 内 `/Game/ShibuyaSim/ShibuyaSimSeq`(Level Sequence アセット)が作られ、
   200 体のシリンダがレベルに並ぶ。この **`ShibuyaSimSeq` を開いて Sequencer の再生ボタン**を
   押すと軌跡が再生される。映像に書き出すなら **Movie Render Queue**(README_UE §7.2)。

> ⚠️ 未検証: エディタ内 Python の実行と Sequencer 再生はこの環境の実機で未確認。UE の
> バージョンによって API 名(例: アクタ生成・キー打ち)が変わることがある(手順 6 参照)。

### 付録: 1,000 体超の将来用(ISM + SimReplayActor)

大規模(数百〜1 万体)は `imp.run(scene_dir)`(既定 `mode="ism"`)で人・車の ISM を配置する。
ただし再生には自作の **SimReplayActor**(Blueprint か C++)が別途必要
([`viz/unreal/SimReplayActor_DESIGN.md`](../../viz/unreal/SimReplayActor_DESIGN.md) の設計に従う)。
200 体規模では不要なので、本書では sequence モードのみ扱う。

---

## 5. 初回の位置合わせ(sim ↔ PLATEAU・所要目安 15〜40 分)

参照: [README_UE §4](../../viz/unreal/README_UE.md)

手順 2-6 のオフセットで**原点(スクランブル交差点)は合う**が、**向き(heading)と鏡像
(y_flip)**は SDK のバージョン差があるため初回だけ実測で合わせる。

1. **総当たり(必ずどれかで合う)**: `export_ue.py`(既定 `--heading 0` / y_flip 有効)で出した
   ものが回転・鏡像でズレていたら、`--heading {0,90,180,270}` × 鏡像なら `--no-yflip` を足した
   **計 8 通り**を試して再出力 →手順 4 で読み直す。アフィン変換なので 8 通りのどれかで一致する。
2. **ランドマーク法**: **ハチ公像(交差点の南西)**・**渋谷駅(南東)**のような非対称の目印と、
   sim の建物・人の配置を見比べて正しい向きを選ぶ。
3. **高さ合わせ**: PLATEAU 建物は標高(T.P.)基準、sim は地面 z=0 基準。人が地面から浮く/埋まる
   場合は `--offset 0 0 <Z_uu>`(1 m = 100 uu)で持ち上げ/沈めて路面に合わせる(交差点付近の
   標高ぶん)。厳密でなくても、見た目で 1 回調整すれば足りる。
4. 合った `--heading` / `--no-yflip` / `--offset` を確定値として以後固定する。

---

## 6. トラブルシュート(初心者が踏みやすい上位 5 件)

網羅版は [README_UE §8](../../viz/unreal/README_UE.md)。ここは頻度の高い 5 件のみ。

| 症状 | 対処 |
|---|---|
| **`PLATEAU` メニューが出ない** | プラグイン未有効、または UE↔SDK のバージョン不一致。手順 1〜2 を確認(UE 5.5.4 ↔ SDK v3.2.x)。有効化後はエディタ再起動 |
| **インポートで CityGML フォルダが選べない** | `udx/` の**1 つ上**、つまり `udx/` と `codelists/` が見える階層(= `13113_shibuya-ku_pref_2025_citygml_1_op` フォルダ自体)を選ぶ(手順 2-4) |
| **街と人がズレる / 鏡像になる** | 手順 5-1。`--heading {0,90,180,270}` × `--no-yflip` の 8 通りを試す |
| **人が地面から浮く / 埋まる** | 手順 5-3。`--offset 0 0 <Z_uu>` で高さ調整(1 m = 100 uu) |
| **人が極端に大きい / 小さい** | 単位ズレ。`export_ue.py` の `--scale`(既定 100 = m→cm)を確認。PLATEAU も cm 前提 |

---

## 参照

- 網羅版手順書: [`viz/unreal/README_UE.md`](../../viz/unreal/README_UE.md)
- ランタイム再生の設計(大規模用): [`viz/unreal/SimReplayActor_DESIGN.md`](../../viz/unreal/SimReplayActor_DESIGN.md)
- 取り込みスクリプト: [`viz/unreal/import_shibuya_sim.py`](../../viz/unreal/import_shibuya_sim.py)
- 座標変換スクリプト: [`scripts/export_ue.py`](../../scripts/export_ue.py)
- PLATEAU 公式インポート手順: <https://project-plateau.github.io/PLATEAU-SDK-for-Unreal/manual/ImportCityModels.html>
