# 群衆物理(Social Force Model)導入のための文献・実装調査 — 渋谷スクランブル交差点の歩行者流

第33バッチ調査(2026-07-15・Opus実行役)。**コード変更なし・調査のみ**。
承認済み方針: engine-architecture.md §4 P1-2「LLM が目的地・意図を決め、群衆エンジンが物理移動を解く」分業。
本書は実装前の文献・実装調査であり、実装の可否・設計はユーザー討議後に決める(MEMORY: ask-before-extending / pre-coding-alignment)。

出典は §6 にアクセス日つきで一括。一次ソース優先。**未確認は「未確認」と明記**した。

---

## 0. 要旨(結論先出し)

1. **時間スケール差が導入設計の核心**。SFM は緩和時間 τ=0.5s を持ち、数値積分は τ より十分小さい**サブ秒刻み(dt≈0.01–0.4s)**が前提。本シミュの **1 step = 600s(10分)**とは3–4桁違う。したがって SFM は「1 step の移動そのもの」にはならず、**stepの内側で多数のサブステップを回す下位ループ**として、(案a)描画専用にオフラインで、あるいは(案b)スクランブル領域限定で回して横断所要時間・密度だけをメゾ層に返す、のいずれかで結合するしかない。
2. **推奨ライブラリ**: 用途で二択。**(i) オフライン合成・完全な決定論制御が要るなら PySocialForce(MIT・純NumPy・約600行・vendoring 容易)**。ただし保守が停滞気味(最終実質更新 ~2024-02)。**(ii) 本番忠実度・保守継続性を優先し LGPL を許容できるなら JuPedSim(LGPL-3.0+・pip wheel・2026-05 に v1.4.2・A*経路+操作モデル内蔵・活発)**。ORCA/RVO2(Apache-2.0)は回避特化の補助、Vadere(LGPL・Java)は結合コスト高、PedPy(MIT)は解析専用。
3. **渋谷の直球先行研究がある**: **ShibuyaSocial(arXiv 2512.18550, 2025)**は渋谷スクランブルの実映像から 407 軌跡を追跡し、**グラフ(4ノード)上の大域移動+局所の連続微視移動を統合したマルチスケール学習モデル**。位置誤差 **0.068–0.070 m**・エッジ精度 **99.5–99.7%**。**本シミュの「LLM が目的地ノード → 群衆エンジンが物理」構造の直接の実証**。ただし**コード・データ公開は論文に記載なし**(=そのままは使えない・要問い合わせ)。
4. **マルチスケール結合は確立領域**: 「臨界領域だけ連続空間の微視、非臨界は離散/ネットワーク」+「遷移帯(transition zone)で状態受け渡し」が定石(TransiTUM 他)。案a/案b はどちらもこの定石の範囲内で、**案b=領域限定ミクロ化そのもの**。
5. **推奨は案a(オフライン合成)を先行**。R1/ゴールデン完全無風・決定論容易・デモ価値は案bとほぼ同等(視覚忠実度が目的なら描画で足りる)。案b(オンライン物理)は横断所要時間・真の瞬間密度をメゾに返せる魅力があるが、既定OFFノブ・RNG/決定論設計・ゴールデン再取得のコストが重く、**k*(研究)には効かない**ため本選前の優先度は案aに劣る。

---

## §1. Social Force Model の理論とパラメータ

### 1.1 モデルの本体(Helbing & Molnár 1995)

歩行者 i の運動をニュートンの運動方程式で表し、加速度を「社会的力(social force)」の和で駆動する:

```
m_i (dv_i/dt) = f_i^drive + Σ_j f_ij + Σ_W f_iW + ξ_i
```

- **駆動項(desired force)**: `f_i^drive = m_i (v_i^0 e_i − v_i) / τ`。希望速度 `v_i^0`・希望方向 `e_i` へ、緩和時間 **τ** で速度を寄せる(τ が小さいほど機敏)。
- **対人斥力 f_ij**: 1995版は**指数ポテンシャル** `U(b) = V₀ exp(−b/σ)`(b=楕円状の実効距離)の勾配。相手が視野の前方にいるほど強く効く**異方性重み** `w = c + (1−c)(1+cosφ)/2`(c≈0.5, 視野±約100°)を掛ける。
- **対壁斥力 f_iW**: 同型の指数斥力(境界・障害物)。
- **揺らぎ ξ_i**: 小さなランダム項(対称性の破れ・レーン形成の種)。

この最小構成だけで、**双方向流の自発的レーン形成・ボトルネックでのアーチ状詰まり・振動的な通り抜け**といった実際の群集の自己組織化が創発する(1995論文の主眼)。

**1995版の代表パラメータ(文献で広く引用。一次値は要確認)**: V₀ ≈ 2.1 m²/s²・σ ≈ 0.3 m、境界斥力 U₀ ≈ 10 m²/s²・R ≈ 0.2 m、異方性 c ≈ 0.5、τ = 0.5 s。**τ=0.5s と希望速度分布は §1.3・§1.4 の確定値を参照**。

### 1.2 パニック拡張(Helbing, Farkas & Vicsek 2000, Nature)

高密度の押し合いを表すため、身体接触時の**物理的な力**を2つ追加する(接触=半径和 r_ij が中心間距離 d_ij を超えるとき):

- **body force(体の圧縮に対する弾性反発)**: `k·g(r_ij − d_ij)·n_ij`
- **sliding friction(接線方向のずれを妨げる摩擦)**: `κ·g(r_ij − d_ij)·Δv_t·t_ij`

このパニック版は「**faster-is-slower 効果**(急ぐほど出口で詰まって遅くなる)」「アーチング」「群集圧」を再現し、避難・群集事故解析の標準になった。

**確定パラメータ(一次に近い二次で複数一致・§6 参照)**:

| 記号 | 意味 | 値 |
|---|---|---|
| A | 社会的斥力の強さ | **2000 N** |
| B | 斥力の特性距離 | **0.08 m** |
| k | 体圧縮定数 | **1.2×10⁵ kg·s⁻²** |
| κ | 滑り摩擦定数 | **2.4×10⁵ kg·m⁻¹·s⁻¹** |
| τ | 緩和(反応)時間 | **0.5 s** |
| m | 歩行者質量 | **80 kg** |
| r | 半径 | **0.25–0.35 m**(一様分布) |
| v_max | 最高速度 | 希望速度の **1.3 倍** |

### 1.3 希望速度分布(較正の要)

自由歩行速度は **平均 1.34 m/s・標準偏差 0.26 m/s の正規分布**(Weidmann 1993 の文献レビュー値を Helbing が採用。実測レンジ ~0.97–1.65 m/s)。σ は文献により 0.26–0.37 m/s。

> **本シミュとの整合(重要)**: conf の `world.modes.speeds.walk = 800.0 m / 10分`= **1.333 m/s**。これは Weidmann/Helbing の希望速度平均 1.34 m/s と**ほぼ完全一致**している。つまりメゾ移動の自由速度は既に SFM の希望速度に較正済みで、SFM を差しても**平時の平均移動時間は保存される**(混雑時の減速の質だけが精緻化される)。

### 1.4 計算量と時間刻み(=案の分岐点)

- **計算量**: 素朴には毎サブステップ全ペアで斥力を評価= **O(n²)**。実務では**近傍リスト/セルリスト+カットオフ半径**(斥力は指数減衰なので数 m 先は無視可)で **≈O(n)** に落とす。数百体規模なら容易。
- **時間刻み**: 数値安定のため **dt ≪ τ** が必要。パニック高密度では dt≈0.01s、通常流でも dt≈0.1–0.4s が定石(PySocialForce の既定積分刻みもこの水準)。
- **∴ 時間スケール差の扱い**: 本シミュ 1 step=600s の内側で、**dt=0.1s なら約6000サブステップ**を回すのが物理的に正しい姿。これは「SFM を sim の1ノブとして毎 step 呼ぶ」ではなく、**下位ソルバをサブループで回し、結果(軌跡/横断時間/密度)を上位へ集約**する結合を強制する。オフライン(案a)なら描画フレーム解像度までダウンサンプルすればよく、負荷は問題にならない。オンライン(案b)でも領域内 n が数十〜低百なら `6000×O(n)` は1 step 内で現実的。

---

## §2. 実装ライブラリの実在・ライセンス・保守(実ページ確認)

| ライブラリ | 種別/得意 | 言語・結合 | ライセンス(実確認) | 保守・最新 | 本件での位置づけ |
|---|---|---|---|---|---|
| **PySocialForce**(yuxiang-gao) | 拡張SFM(Moussaïd 2009 楕円仕様+集団力) | 純NumPy・同一Python=**結合最易** | **MIT**(実確認) | ★停滞気味(実質更新 ~2024-02・約79★・研究grade) | **案a本命**。約600行で vendoring・決定論改造が容易 |
| **JuPedSim**(Forschungszentrum Jülich) | 操作モデル(collision-free speed)+SFM系+**A*経路内蔵** | C++コア+**Python API(pip wheel)** | **LGPL-3.0+**(LICENSE 実確認) | ◎活発(**v1.4.2 / 2026-05**・Py3.10–3.14・Win/Mac/Linux・Production/Stable) | **案b/本番忠実度の本命**。LGPL(動的リンク・再リンク可能性の担保が条件) |
| **Vadere**(HM/München) | 微視群集(OSM/GNM/SFM 複数モデル・GUI・解析同梱) | **Java** スタンドアロン | **LGPL** | 継続(研究機関主体) | 機能豊富だが **Java↔Python 橋渡しコスト高**。参照実装として有用 |
| **Python-RVO2 / ORCA**(mit-acl, 原典 UNC-GAMMA) | 相互速度障害による**高速衝突回避** | C++/Cython バインド(要ビルド) | **Apache-2.0**(LICENSE 実確認) | 実績多(自律移動系で標準) | **回避特化の補助**。群集流の「質感」は SFM ほど自然でない |
| **PedPy**(PedestrianDynamics) | 軌跡→**密度/速度/流量/基本図**の解析 | Python | **MIT**(実確認) | 活発(v1.4系) | 出力軌跡の**検証・Fruin/基本図較正**に使える解析専用 |

補足:
- **PySocialForce** には後継フォーク(Bonifatius94/PySocialForce・型付け整理版)もあり、より新しい可能性がある(要確認)。原典は Johns Hopkins IAA 由来で **Arena 3.0(社会ナビ研究基盤)の既定 SFM**。
- **JuPedSim** は独自の A* 経路網を持つため、本シミュの routing.py と**役割が重複**する。使うなら「経路は本体、SFM解決だけ JuPedSim」と切り分けが要る。LGPL のため**静的リンク/同梱時は再リンク可能性(利用者が JuPedSim 部分を差し替えられる)を保つ**義務。研究コードの内製配布なら現実的だが、MIT の PySocialForce より制約は強い。
- いずれも **pip で入るのは JuPedSim / PySocialForce / PedPy / Python-RVO2**。Vadere のみ Java 実行系。

---

## §3. 渋谷スクランブル交差点の実データ・先行研究

### 3.1 マクロ統計(較正に使える桁)

- **1回の青信号での横断者数**: 「多いとき **約3,000人**/1回(約2分間隔)」が最も流布。ただしこれは**渋谷センター街の PR 値で厳密なデータ根拠は乏しい**との指摘あり(Wikipedia)=**目安・上限オーダーとして扱う**。堅めには「**1回の青で 1,000人以上**」。
- **信号サイクル**: 概ね **約2分周期**(全方向同時横断のスクランブル運用)。1周期あたり青の実尺・全赤時間の一次値は**未確認**(現地信号諸元は要一次確認)。
- **日交通量**: 2014年の渋谷再開発協会の流動計測に基づく算定で **平日 約26万人・休日 約39万人**、ピーク時「1日最大50万人」の言及もある(いずれも二次・報道系)。

### 3.2 ShibuyaSocial(arXiv 2512.18550, 2025)— 直球の先行研究

**タイトル**: *ShibuyaSocial: Multi-scale Model of Pedestrian Flows in Scramble Crossing*。**本シミュの分業構造そのものを実証**する重要文献。

- **データ**: 高層ビルから **8K/30fps 映像(約50分)**を撮影 → SMILETrack で歩行者検出・追跡 → DLT 校正で画素→2D 実座標。**407 軌跡**を取得(Flow1=183, Flow2=224)。ただし追跡成功率は約18–22%で、**実際の横断者は各フローで概ね ~1,000人規模**と推定(=1信号あたりの母数オーダーの傍証)。学習/シミュは **5fps** にダウンサンプル。
- **モデル**: LSTM エンコーダ/デコーダ+**アテンション**。**マルチスケール**=大域(目的地ノード・エッジ遷移=数十mの経路選択)と局所(節点からの相対位置・**占有マップ**・環境の bird map・**信号状態 s[t]**=数十cmの回避)を中間層で統合。**信号は sigmoid で表現**。**LLM は不使用**。
- **精度**: **位置誤差 < 0.1 m(実測 0.068 m / 0.070 m)**、**エッジ(どの経路にいるか)精度 99.7% / 99.5%**、シミュ vs 実測の人数 RMSE 2.34 / 1.88 人、平均歩行速度 RMSE **0.17 / 0.20 m/s**。
- **再現できた質的現象**: 赤信号での**横断前停止**、対向流での**レーン形成**(自己組織化・明示プログラムなし)、青直前のフライング横断(実データにも存在)。エッジ精度<100% の副作用で赤無視の突入も少数生じる、と正直に報告。
- **公開**: **コード・データの公開は論文に明記なし**(=再利用可否は著者問い合わせ次第。**そのまま差せる部品ではない**)。「lit-review が触れた 0.07m」の出典・数値は**本調査で一次(arXiv HTML)まで遡って確認済み**。

> 意義: ShibuyaSocial は「**グラフ上の目的地決定(大域)+連続空間の微視移動(局所)**」を渋谷実データで 0.07m 精度に載せた実例。本シミュの「LLM=大域(どこへ)/群衆エンジン=局所(足の運び)」は、この論文が LLM を学習モデルに置き換えただけの同型であり、**設計方針の妥当性を外部から裏づける**。

### 3.3 較正に使える数値(まとめ)

| 量 | 値 | 出典/確度 |
|---|---|---|
| 自由歩行速度(希望速度) | 1.34 m/s(σ 0.26–0.37) | Weidmann1993/Helbing・高確度 |
| 最高速度 | 希望×1.3 | Helbing2000・高確度 |
| 1青の横断者 | 1,000人以上(上限 ~3,000は PR値) | Wikipedia・中〜低確度 |
| 信号周期 | 約2分 | 二次・中確度 |
| 日交通量 | 平日26万/休日39万(最大50万) | 再開発協会算定の二次・中確度 |
| 位置予測到達精度(学習型) | 0.068–0.070 m | ShibuyaSocial一次・高確度 |
| 群集密度の危険域(参考) | LOS F ≥ ~2.0人/m²、群集事故域 概ね >4–5人/m² | FHWA/Fruin・群集力学・中〜高確度 |

Fruin LOS 閾値(A>3.2 … F<0.5 m²/人)は**既にリポジトリで一次確認済み**(`scripts/analyze_flows_grid.py` docstring・FHWA Ch.13)。SFM/密度出力の格付けにそのまま流用できる。

---

## §4. ABM×群衆物理のマルチスケール結合の先行例

「メゾ(グラフ/ネットワーク移動)× ミクロ(連続空間 SFM)」のハイブリッドは確立した研究領域で、**本件の案a/案b はこの定石の内側**にある。

- **空間解像度の階層**: マクロ(ネットワーク流)=低解像 / メゾ(セルオートマトン)=中 / ミクロ(SFM 等の連続空間)=高。**臨界領域だけ高解像、非臨界は低解像**で回し、境界で整合を取るのがハイブリッドの定石(計算量削減+局所忠実度の両取り)。
- **TransiTUM(Biedermann ら, TU München)**: メゾ⇄ミクロを**遷移帯(transition zone)**で結合する汎用枠組み。異なるモデルでも「位置・速度」等の**共通量だけを遷移帯で受け渡す**。→ 本件の「スクランブル領域の境界で、メゾのノード到達を SFM の流入エージェントへ変換/回収」の設計指針になる。
- **A hybrid multi-scale approach(Transportation Research Part C, 2013)** / **A mesoscopic model for large-scale simulation(同, 2018)**: 「臨界域=連続空間、非臨界=離散」を切り替え、**両モデル間で一貫した情報交換**を行う実装例。避難・大規模歩行者流で実績。
- **ShibuyaSocial(§3.2)自体がマルチスケール結合の実例**: グラフ大域 + 連続局所を1モデルで内包。
- **交通側の同型**: SUMO/MATSim は「activity chain(日課)= メゾ計画」+「車の微視移動」。engine-architecture が SUMO を歩行者本体には不採用とした判断(striping で高密度双方向に不向き)は、**歩行者は SFM 系、車は将来 SUMO** の役割分担と整合。

**結合パターンの要点(本件へ)**:
1. **領域限定ミクロ化**: スクランブル交差点の bbox(地図原点(0,0)近傍。`annual.gathering_node` が既に原点最近傍を集会ノードに採る)だけを SFM 領域にする。
2. **境界条件**: メゾでその領域ノードに「到達」したエージェントを SFM のソース(流入)に、SFM 領域の出口ノードに達したら**メゾへ回収**(sink)。滞留数・横断所要時間・瞬間密度を集約量として返す。
3. **遷移帯**: 領域境界に緩衝帯を設け、速度・向きを引き継いで不連続を避ける(TransiTUM 流)。

---

## §5. 本シミュへの統合案の比較評価と推奨

前提の接合面(実コード確認済み):
- **メゾ移動**: `engine/scheduler.py::_phase_move`。1 step で `walk=800m/10分×congestion` 進み、`congestion = 1.0 if count≤capacity(=20) else max(0.3, capacity/count)`。**混雑は「最大0.3倍まで減速・完全停止しない・エッジ単位で粒い」**。移動軌跡は `move_segment` イベントに **RDP 間引き済みポリライン `pts`(最大20点)**で記録。
- **ビューア補間の接合面(案a の差し込み口)**: `viz/make_viewer.py` の `alongPath(pts,f)`/`posAt(t)` と `scripts/export_3d.py::reconstruct_tracks` が、**`move_segment.pts` に沿って step 内を補間**して滑らかな移動を描く。**ここで pts をスクランブル領域だけ SFM 微視軌跡に差し替え/上書き**すれば、シミュ本体・L1 を触らずに視覚忠実度を上げられる。
- **密度の器**: `scripts/analyze_flows_grid.py`(25mメッシュ×時間ビン→Fruin LOS)。ただし自認どおり **present_count は「在圏観測 proxy」で瞬間頭数ではない**(stay は0件・arrive は疎)。真の瞬間密度は現状出ない。
- **群集イベント**: `annual.check_surge` が原点近傍の集中を **crowd_surge** として観測(発火/grievance には非接続=純観測)。案bの自然な足場。

### 5.1 比較表

| 観点 | 案a(オフライン合成) | 案b(オンライン物理) |
|---|---|---|
| 何をする | L1 の `move_segment.pts` を後処理し、スクランブル周辺**だけ**を SFM 微視軌跡に合成 → ビューア/3D 用トラックに反映 | sim 内でスクランブル領域だけ SFM を回し、**横断所要時間・瞬間密度を `_phase_move` の減速に反映** |
| 触る所 | `viz/` `scripts/export_3d` 相当の**読み出し専用後処理**(sim本体・L1・schema・conf 不変) | `scheduler._phase_move` 近傍に領域SFMソルバを接続(本体に作用) |
| **R1/ゴールデン安全性** | ◎ **完全無風**(L1バイト不変・k非接触・ゴールデン再取得不要) | △ **要既定OFFノブ**。ON時は乱数消費・イベント列が変わりゴールデン再取得。CRN/決定論の設計必須 |
| 決定論 | ◎ 後処理を固定seed/固定反復順にすれば自明に決定論。numpy/BLAS の総和順だけ注意 | △ SFM揺らぎξを `hub.stream` に束ね、反復順・浮動小数総和順を固定。**跨プラットフォーム再現は追加検証** |
| 時間スケール処理 | step内を dt=0.1s で解いて描画fpsへダウンサンプル(負荷=軽・オフライン) | step内サブループ6000回×領域内O(n)。領域nが低百なら現実的だがランを重くする |
| 工数(目安) | **小〜中(1–2日)**: 領域内エージェント抽出→SFMソルバ→pts差し替え→ビューア確認 | **中〜大(3–5日+検証)**: ソルバ+境界条件+OFFノブ+RNG/決定論+ゴールデン再取得+スモーク |
| **デモ価値** | ◎ 高。スクランブルの群れ・レーン形成・信号待ち滞留が**見た目で**再現(視覚忠実度が目的なら十分) | ◎ 高。加えて「混雑で実際に横断が詰まる」因果が動く |
| **研究価値(k*への影響)** | ○ 中。真の瞬間密度・LOS を**観測量**として出せる(混雑の現実味↑)。ただし agent の意思決定・k には非接続 | △ 限定的。混雑がgrievance/driveに繋がれば因子に影響しうるが、**engine-architecture は「k*には効かない・デモに効く」と明言**。因子接続は交絡増でむしろ慎重 |
| 主なリスク | 合成軌跡が L1 と乖離(見た目専用と割り切る/注記で担保) | 決定論・R1・性能・ゴールデン維持の同時達成。誤ると研究再現性を毀損 |

### 5.2 推奨

**案a(オフライン合成)を先行実装、案bは保留(将来オプション)**。理由:

1. **R1/ゴールデンが完全無風**。研究の生命線(決定論・k-blind・golden_baseline_l1.json)に一切触れずデモ品質を上げられる。これは本プロジェクトの `★既定OFF` 文化(config 全域)と最も整合。
2. **デモ目的(視覚忠実度)は案aでほぼ達成**。engine-architecture が P1-2 を「**研究(k*)には効かない・デモに効く**」と正しく位置づけている以上、本体に作用する案bのコスト(RNG/決定論/ゴールデン再取得)は費用対効果が悪い。
3. **接合面が既にある**: `move_segment.pts` → `alongPath/reconstruct_tracks` の補間経路に、領域限定で SFM 微視軌跡を差し込むだけ。`analyze_flows_grid` に「SFM由来の真の瞬間密度」列を足せば、Fruin LOS を**在圏proxyでなく実密度で**格付けでき、研究側の混雑観測も同時に改善する(これも読み出し専用=無風)。
4. **ライブラリは PySocialForce(MIT・純NumPy)を vendoring** し、揺らぎξを固定seedにして決定論化するのが最小コスト。忠実度を上げたくなったら JuPedSim(LGPL・操作モデル)へ差し替える余地を残す。

**案b を将来やるなら**の必須条件(先に合意すべき OPEN):
- `crowd.sfm.enabled=false` の既定OFFノブ(config 文化に合わせる)。
- SFM揺らぎを `sim.hub.stream("sfm", …)` に束ねる/または揺らぎ無し決定論モードを既定にする。
- 反復順・浮動小数総和順の固定と、跨プラットフォーム再現の検証(numpy/BLAS 依存に注意)。
- ゴールデン再取得(ON経路は別ゴールデン)。**混雑を grievance/drive に繋ぐか否かは研究設計の判断**(繋ぐと k 解釈が変わる=engine-architecture の Skill と同じ「意味が重い」問題)。

**ShibuyaSocial(学習型)** は精度最高(0.07m)だが**未公開=即利用不可**。案a の SFM で足場を作り、公開/著者連携が取れたら差し替える二段構えが堅い。

---

## §6. 出典(アクセス日: 2026-07-15)

**SFM 理論・パラメータ**
- Helbing, D. & Molnár, P. (1995) *Social Force Model for Pedestrian Dynamics*, Physical Review E 51, 4282–4286. arXiv: https://arxiv.org/abs/cond-mat/9805244(アクセス 2026-07-15。abstract を確認、式・数値は本文PDF)
- Helbing, D., Farkas, I. & Vicsek, T. (2000) *Simulating dynamical features of escape panic*, Nature 407, 487–490. PDF: https://angel.elte.hu/pedsim/pdf/panic.pdf / ETH COSS: https://coss.ethz.ch/publications/supporting/escape-panic.html(アクセス 2026-07-15。PDF本体は自動抽出不可のため数値は下記二次で相互確認)
- パニック版パラメータ(A=2000N, B=0.08m, k=1.2×10⁵, κ=2.4×10⁵, τ=0.5s, m=80kg)の相互確認: *Improved social force model … subway station*(ResearchGate) / *Effects of the body force …*(arXiv 2003.02890 https://arxiv.org/pdf/2003.02890)/ *SFM parameter testing …*(arXiv 2007.06651 https://arxiv.org/pdf/2007.06651)(アクセス 2026-07-15)
- 希望速度 1.34 m/s(σ 0.26–0.37): Weidmann 1993(文献レビュー値)/ Daamen & Hoogendoorn *Free Speed Distributions*(TRB 2006 http://vigir.missouri.edu/~gdesouza/Research/MobileRobotics/Free%20Speed%20Distributions%20for%20Pedestrian%20Traffic...pdf)(アクセス 2026-07-15)
- Moussaïd ら (2009) *Experimental study of the behavioural mechanisms underlying self-organization in human crowds*, arXiv 0908.3131 https://arxiv.org/pdf/0908.3131(PySocialForce が実装する楕円仕様の出典。アクセス 2026-07-15)

**ライブラリ(実ページ確認)**
- PySocialForce(MIT): https://github.com/yuxiang-gao/PySocialForce ・ PyPI https://pypi.org/project/PySocialForce/ ・後継フォーク https://github.com/Bonifatius94/PySocialForce(アクセス 2026-07-15。ライセンス MIT・実質更新 ~2024-02 を確認)
- JuPedSim(LGPL-3.0+): https://github.com/PedestrianDynamics/jupedsim ・ LICENSE 実確認 https://github.com/PedestrianDynamics/jupedsim/blob/master/LICENSE ・ PyPI https://pypi.org/project/jupedsim/(v1.4.2 / 2026-05-21・Py3.10–3.14。アクセス 2026-07-15)
- Vadere(LGPL): https://www.vadere.org/ ・ https://github.com/pedestrian-dynamics-HM/vadere ・論文 arXiv 1907.09520(アクセス 2026-07-15)
- Python-RVO2 / ORCA(Apache-2.0): https://github.com/mit-acl/Python-RVO2 ・ LICENSE https://github.com/mit-acl/Python-RVO2/blob/master/LICENSE(アクセス 2026-07-15)
- PedPy(MIT): https://github.com/PedestrianDynamics/PedPy ・ docs https://pedpy.readthedocs.io/stable/(アクセス 2026-07-15)

**渋谷スクランブル・先行研究**
- ShibuyaSocial: *Multi-scale Model of Pedestrian Flows in Scramble Crossing*, arXiv 2512.18550 (2025) https://arxiv.org/html/2512.18550v1(アクセス 2026-07-15。407軌跡・位置誤差0.068–0.070m・エッジ精度99.5–99.7%・速度RMSE0.17–0.20m/s・コード公開記載なし、を本文HTMLで確認)
- 渋谷スクランブル交差点 — Wikipedia(ja) https://ja.wikipedia.org/wiki/渋谷スクランブル交差点(1青3,000人はセンター街PR値との注記・平日26万/休日39万の算定。アクセス 2026-07-15)
- 交差流のレーン形成(PNAS) https://www.pnas.org/doi/10.1073/pnas.2505488122(アクセス 2026-07-15)

**マルチスケール結合**
- TransiTUM(遷移帯によるメゾ⇄ミクロ結合): https://www.academia.edu/72438552/Towards_TransiTUM_...（アクセス 2026-07-15）
- *A hybrid multi-scale approach for simulation of pedestrian dynamics*, Transportation Research Part C (2013) https://www.sciencedirect.com/science/article/abs/pii/S0968090X13000594(アクセス 2026-07-15)
- *A mesoscopic model for large-scale simulation of pedestrian dynamics*, Transportation Research Part C (2018) https://www.sciencedirect.com/science/article/abs/pii/S0968090X18307228(アクセス 2026-07-15)

**歩行者 LOS(リポジトリで既に一次確認済み・再掲)**
- FHWA *Recommended Procedures for Chapter 13, Pedestrians, of the HCM*(Fruin 列 m²/人: A>3.2 … F<0.5)。`scripts/analyze_flows_grid.py` docstring 参照(2026-07-14 に WebFetch 一次確認済み)

---

### 未確認・要注意(誠実性)
- Helbing 1995 の指数ポテンシャル定数(V₀≈2.1 m²/s²・σ≈0.3 m・c≈0.5)は**広く引用される二次値**で、原論文PDFの一次照合は未了(PDF自動抽出が不可だった)。実装時は原論文で再確認のこと。
- 渋谷「1青3,000人」「1日50万人」は**PR/報道系の二次値**で厳密なセンサス根拠は乏しい。較正には「平日26万/休日39万(2014流動計測算定)」「1青1,000人以上」を採るのが安全。
- 渋谷信号の実諸元(青尺・全赤)は一次未確認。
- ShibuyaSocial は**コード・データ未公開**(論文記載なし)。即利用は不可、要著者問い合わせ。
- PySocialForce の後継フォーク(Bonifatius94)の活発度・API 差分は未精査。
