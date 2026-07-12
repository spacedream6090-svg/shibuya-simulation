# 内省しやすさの時間変化(発火閾値ドリフト)— 調査と実装設計案(R1、2026-07-06)

> 依頼: 「エージェントごとの内省の推論しやすさ(= drive_threshold / fire_weight 相当)が **step が進むごとに
> 上昇または下降する**ようにしたい」。まず手元(docs/lit/、特に
> [cognition__drive-firing-memory.md](../lit/cognition__drive-firing-memory.md) の MicroPsi selection threshold
> ヒステリシス・EVC)を確認し、足りなければ Web リサーチ。**本バッチは調査・設計のみ・実装なし**。
> 学術メモ: [../lit/cognition__reflection-drift-adaptation.md](../lit/cognition__reflection-drift-adaptation.md)。

## 0. 現状(コード確認済み)
- `cognition/drive.py`: 出来事がゲージ `drive`(0-1)を溜め、個人別 `drive_threshold` で申請、`fire_weight`
  で確率発火。閾値・重みは**固定**(`factors/registry.drive_params` が traits から一度写像)。
- `engine/scheduler._phase_drive`: 申請=残量順、発火後 `drive×0.20`、不応期 3 step、抽選落ちで `drive×0.70`。
- 発火の入力は**出来事のみ**(信念/k 非依存)=既存の R1 対策。閾値は**時間で動かない**のが今回の空白。
- 既存メモの接地: MicroPsi の selection threshold は「閾値+ヒステリシス」の**静的**個体差。今回はこれを
  **時間発展**へ拡張する(θ が経験履歴で緩やかに動く)。

## 1. 文献の要点(→ 詳細は lit メモ)
| 系列 | 出典 | ドリフトへの含意 |
|---|---|---|
| 馴化/鋭敏化 | Rankin et al. 2009 | 単調・反復刺激→**馴化**(閾値↑)。頻度依存・刺激特異・**自発回復**・脱馴化。強刺激反復→**鋭敏化**(閾値↓) |
| メタ認知の練習効果 | 教育心理(reflection begets reflection) | **発火経験そのものが次の発火を促す**使用依存促通=鋭敏化。入力=発火回数(k 非依存) |
| 精神的努力=機会費用 | Kurzban et al. 2013 (BBS) | 競合需要が高い局面(混雑・多イベント)は実効閾値↑。資源枯渇でなくコスト説 |
| 好奇心=情報ギャップ | Loewenstein 1994 | 未知語で一時的に閾値↓→露出継続で**満腹**(馴化と整合) |
| EVC の適応強度 | Shenhav et al. 2013 | 制御配分は期待価値で時々刻々調整=時間発展する θ の規範形 |

**収束点**: 閾値は「単調刺激で上がり(馴化)、新奇・強刺激と発火経験で下がり(鋭敏化・練習)、休止で base へ戻る(自発回復)」。
向き・速さは個体差。これは既存の発火機構に緩変数 1 個を足すだけで表現できる。

## 2. 実装設計の推奨(seam・既定 OFF・実装は次バッチ)

### 2.1 状態と実効閾値
- 各 agent に緩変数 `theta_drift: float = 0.0` を追加(記憶 float 1 個)。
- **実効閾値** = `clip(drive_threshold + theta_drift, 0.30, 0.85)`。fire_weight は当面据え置き(閾値ドリフトを
  主経路にする。両方動かすと交絡が読みにくい)。logistic 発火時は `p=σ(slope·(drive−(threshold+theta_drift)))`。

### 2.2 ドリフト則(因果構造のみ。magnitude は conf)
毎 step / 発火時に θ を 3 力の和で更新(すべて drive.py が既に見る量=k 非依存):
1. **馴化(閾値↑)**: 低顕著イベント(silence / sns / company / news)を受けるたび
   `theta_drift += h_rate · w_event`(頻度依存: 高頻度ほど速く上がる)。上限 `+drift_cap`。
2. **鋭敏化(閾値↓)**: (a) 発火のたび `theta_drift -= s_fire`(練習効果)。
   (b) 新奇/強イベント(novel_place / unknown_word / 大 |Δstate|)で `theta_drift -= s_novel · scale`(脱馴化)。下限 `−drift_cap`。
3. **自発回復(base へ)**: 毎 step `theta_drift -= recover_rate · theta_drift`(θ を 0 へ緩やかに引く。刺激休止で回復)。

これで「刺激が単調な期間は内省が減衰し、新奇・活発な期間や内省を重ねた個体は内省が起きやすくなり、
静かな夜/範囲外滞在で base に戻る」という時間変化が自然に出る。

### 2.3 個体差(向き・速さ)は traits 由来(no-fingerprint)
`factors/registry.py` に `drift_params(traits, rng) -> {h_rate, s_fire, s_novel, recover_rate}` を新設
(drive_params と同格。cognition/engine は戻り値の数値しか見ない):
- **NFC 高** → s_fire/s_novel を強め・h_rate を弱め = **鋭敏化型(sensitizer)**: 使うほど内省が加速し閾値が下がる。
- **NFC 低 / 内的統制低** → h_rate 強め = **馴化型(habituator)**: 刺激に慣れて内省が減っていく。
- 速さの散らばりは既存方針どおり **TruncatedNormal or LogNormal(σ/μ≈0.2-0.4)**。**1 draw** を build_agent 末尾に置き
  既存ストリームの draw 位置を動かさない(再現性維持=opinion_params と同じ作法)。

### 2.4 パラメータ範囲(初期値の当たり。conf.drive.drift で調律・感度分析は B 段)
| 記号 | 意味 | 推奨初期レンジ | 根拠/備考 |
|---|---|---|---|
| `h_rate` | 馴化の 1 イベント増分 | 0.001–0.005 | 数十イベントで有意な θ↑。頻度依存は w_event 経由 |
| `s_fire` | 発火 1 回の閾値低下 | 0.005–0.02 | 数回の内省で「乗ってくる」。練習効果 |
| `s_novel` | 新奇/強イベントの低下係数 | 0.01–0.03 | 脱馴化。|Δstate| や novelty に scale |
| `recover_rate` | base への回帰(自発回復) | 0.002–0.01 /step | 半減 ~70–350 step ≈ 半日〜2日。日跨ぎで base 復帰 |
| `drift_cap` | θ の可動域 | ±0.15–0.20 | base±20% 程度。clip[0.30,0.85] と二重で暴走防止 |
| 分布 | h/s/recover の個体差 | TruncNorm/LogNorm σ/μ≈0.2–0.4 | MicroPsi 個体差の既存注記 |

### 2.5 seam の形(既定で挙動不変)
```
drive:
  drift:
    enabled: false        # 既定 OFF = 現行 fixed と完全同一(θ_drift 常に 0)
    h_rate: 0.002
    s_fire: 0.01
    s_novel: 0.02
    recover_rate: 0.005
    cap: 0.18
    dist: lognormal        # 個体差分布(normal|lognormal)
```
`drive.build_cfg` に `drift` を追加(既定 enabled=false)。OFF 時は `theta_drift` を一切触らない
=イベント列がバイト一致で不変(既存ゴールデン/決定論テストを壊さない)。

## 3. R1 監査(計算量交絡の再発防止)— **設計に埋め込む制約**
- ❌ **禁止**: θ ドリフトの入力に `beliefs`・書き戻し成否・Y_internal を使う(k.writeback にゲートされる量)。
  理由: 発火数が k 条件で乖離し、計算量交絡(off で内省が減って発火も減る等)が復活する。
- ✅ **許可**: 発火回数・棄却回数・出来事ゲージ入力(drive.py が既に持つ量)。これらは k 非依存
  (drive.py は beliefs を参照しない/factor 更新は全 k で走る)。
- 監査手段: L2 に `mean_theta_drift` を追加(aggregate.py に register 1 個)。既存 R1 テスト
  (`tests/test_drift.py` 相当・k∈{free,off} で n_fires ±20%)が drift ON でも通ることを担保。
  → drift が k 非依存に閉じている限り通るはず。**もし n_fires が k で乖離したら、入力に k 依存量が混入した証拠**。

## 4. 検証手順(実装後の次バッチ向け・本バッチでは回さない)
- mock ≤24 step スモークで `theta_drift` が (a) 単調刺激で上がり (b) 発火/新奇で下がり (c) 静穏で 0 へ戻ることを軌跡確認。
- k∈{free,off}×seed で n_fires 差が ±20% 以内を再確認(R1)。
- 感度分析は B 段(conf.drive.drift の掃引)。

## 5. 確定できなかった点(正直な記録)
- Loewenstein 1994 原文 PDF は本調査で直接取得せず(2次解説 Golman&Loewenstein で機構確認)。数式化は要原著確認。
- MicroPsi の urge leaky 係数の具体値は既存メモどおり**未確認**(PDF 抽出失敗)。θ の recover_rate は LIF/自発回復の桁からの当たり値。
- traits→drift の写像(誰が sensitizer/habituator か)は**仮説**。RQ 検収対象。

## 出典
lit メモ [../lit/cognition__reflection-drift-adaptation.md](../lit/cognition__reflection-drift-adaptation.md) の出典欄参照
(Rankin 2009 / Kurzban 2013 / Loewenstein 1994 / Shenhav 2013 / Frömer&Shenhav 2021、URL 検証済み)。
