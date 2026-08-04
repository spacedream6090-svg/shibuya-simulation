# PENDING — 未実装・実装中・ユーザー判断待ち

> 本ファイルは **まだ終わっていないもの**だけを持つ。完了済みは → **[IMPLEMENTED.md](IMPLEMENTED.md)**。
> 索引と最終更新は → **[STATUS.md](STATUS.md)**。
> 最終更新: **2026-08-03**。
> 正典: [dual-mode-observe-verify-plan.md](docs/plans/dual-mode-observe-verify-plan.md) §2(第70〜78=完了)・
> [cognition-physics-plan.md](docs/plans/cognition-physics-plan.md)(第79〜85=完了)・
> [dayplan-engaged-plan.md](docs/plans/dayplan-engaged-plan.md)(第86〜91=現行レーン)・
> [highfidelity-3d-physics-plan.md](docs/plans/highfidelity-3d-physics-plan.md)・
> [hackathon1-ideas-implementation-plan.md](docs/plans/hackathon1-ideas-implementation-plan.md)・
> [dt-integration-plan.md](docs/plans/dt-integration-plan.md)。

---

## 1. 実装中・次バッチ

| バッチ | 内容 | 状態 |
|---|---|---|
| ~~第86~~ | day_plan v1(構造化スキーマ+検証/修復/フォールバック3段+ルール実行+priority×flex 割り込み) | **完了**(2026-08-03・新50テスト・[実装記録](docs/plans/dayplan-engaged-plan.md) §4 → [IMPLEMENTED.md](IMPLEMENTED.md)) |
| ~~並行~~ | 保守バッチ(ハードデッドライン・xdist 直列化・dunbar×pool 幅・竹-4①②・exit_building) | **完了**(2026-08-03・exit_building は実害クラッシュを実証し guard 1行で修正→ [IMPLEMENTED.md](IMPLEMENTED.md)) |
| **P4 較正** | 物理の高密度条件での較正+ゾーンのビューワー表示(竹-4 の残り) | 未着手・**8/12-14 フリーズ前に完了**が目標 |

> 根拠: ユーザー指示(2026-08-03)「僕の判断が必要ない実装は進めてもらって構わない」+
> 原文書 [source/design-discussion-20260802.md](docs/plans/source/design-discussion-20260802.md)(2026-08-02 受領・
> **概念決定済み・実装詳細は Claude Code 委任**と明記)。

## 2. 計画済み

### 2.1 第87〜91(day_plan / engaged レーン・全て既定 OFF=golden 無風・R1 準拠)

| バッチ | 内容 |
|---|---|
| ~~第87~~ | engaged モード=**完了**(2026-08-03・新47テスト・実測エピソード 7.38/人/日=目標帯内・[実装記録](docs/plans/dayplan-engaged-plan.md) §5 → [IMPLEMENTED.md](IMPLEMENTED.md)) |
| ~~第88~~ | 心モデル固定+三層知能=**完了**(2026-08-03・新38テスト・純関数割当=checkpoint不要・[実装記録](docs/plans/dayplan-engaged-plan.md) §6 → [IMPLEMENTED.md](IMPLEMENTED.md)) |
| ~~第89~~ | プラセボ L1 3種=**完了**(2026-08-03・新55テスト・[梯子文書](docs/research/ablation-ladder.md)・[実装記録](docs/plans/dayplan-engaged-plan.md) §7 → [IMPLEMENTED.md](IMPLEMENTED.md)) |
| ~~第91~~ | 退行シグナル監視+縦横煙=**完了**(2026-08-03・新40テスト・[判定基準](docs/research/regression-signals.md)・[実装記録](docs/plans/dayplan-engaged-plan.md) §9 → [IMPLEMENTED.md](IMPLEMENTED.md))。★DP-U3 の核心材料=**在場25万は presence cap で来街者ゼロ化**(総人口25万×在場制御の設計が必要)。メモリは第91の N=1,000 外挿 316〜363GB → **同日の1万体実測(_rss_probe_10k: peak 4,713MB・限界傾き0.36MB/体)で 25万 ≈ 90〜120GB に下方修正**=大容量 RAM 単一ノードなら射程内 |

(第90 バッテリーハーネスは **2026-08-03 完了**→ [IMPLEMENTED.md](IMPLEMENTED.md) O 節。正規版 D 層測定(n=30)と候補5〜6本への拡張は DP-U2 の材料として実施予定)

### 2.2 提案書提示済み(承認待ち)

| 項目 | 状態 |
|---|---|
| 観察ラン ON 構成 | **提案書提示済み**([observe-run-config-proposal.md](docs/plans/observe-run-config-proposal.md))→ OBS-U1〜U3 判断待ち・最終確定は 8/12-14(実 LLM 再較正後)。**25万人転換を受けて要改訂**(DP-U3) |
| DT スナップショット再提案 | **提案書提示済み**([dt-snapshot-integration-proposal.md](docs/plans/dt-snapshot-integration-proposal.md))→ DT-S1 ほか判断待ち |
| S-quick(S0/S1/S2/S5/S9) | 計 ≈1.8日。承認待ち(S-quick 行を参照) |

### 2.3 本選後(レーン3)

場所二層知覚(IDEA⑥)・誤情報構造化フル版(IDEA⑦=ID-U2)・SUMO 反実仮想(P5)・USD/3D Tiles(DT-U4)・UE5(DT-U2 保留)。
DT 側の詳細順位は [dt-integration-plan.md](docs/plans/dt-integration-plan.md) §3(P5 → P4' USD → P7 較正限定人流同化 → P1 Cesium/3D Tiles → P2 UE5 リプレイ)。
S 系列の本選後分は [dt-snapshot-integration-proposal.md](docs/plans/dt-snapshot-integration-proposal.md) §3(S6 実営業時間・S7 忠実度レポート・S8=旧P7 jinryu 接続・S10 お盆モデル)。
松(テクスチャ写実 LOD2.2)の残り作業は本選中の観察レイヤ作業として [highfidelity-3d-physics-plan.md](docs/plans/highfidelity-3d-physics-plan.md) §2 第3段。

## 3. ユーザー判断待ち

> 以下は現況台帳 §3 の**一字一句保持**(取り消し線の決定済み項目も履歴として残す)。

| # | 事項 | 状態 |
|---|---|---|
| U-10 | 事前登録の閾値承認+10日ラン解釈方針 | タイミング委任済み(2026-07-31)→**第74 完了後〜第78 で承認依頼**(10日ラン 8/16 開始前) |
| PUB-U1 | 公開ミラーの .md 除外範囲+「実装を適宜 public にコミット」の運用 | **要相談**(ユーザー発意 2026-07-31)。推奨: docs/**・STATUS.md を除外し README/ETHICS/LICENSE は残す・以後は各バッチ後に publish_public_mirror.ps1 を同期実行。**注意: DT 調査でライセンス地雷2件確認**(商業施設/区サイト情報=転載不可・OSM 由来テーブル=ODbL share-alike が配布時発動)=提案書 §4 |
| NEW-5 | F/N/P 初期値条件の本選配分 | パイロット後に提案 |
| ~~P2選定~~ | 物理エンジンの選定 | **決定済み**(2026-08-02: ユーザー委任「ベンチをまわして君が決定して」→ベンチ再実行=前回と全指標ビット一致→**ゾーン別ハイブリッド**確定。[選定文書](docs/research/physics-engine-selection.md) P2 決定節) |
| OBS-U1〜U3 | 観察ラン ON 構成の承認([提案書](docs/plans/observe-run-config-proposal.md))・Δt_move 1分の扱い・認知 ON の 8/14 留保 | **新規**。推奨=§1 の ON セット+Δt=10 維持(1分は並行小ラン)+8/14 最終判断 |
| S-quick | S0/S1/S2/S5/S9(計≈1.8日・S0 は第71 相乗り)を本選前に入れるか | **新規・承認求む**(提案書 §3。入力来歴・observe.yaml 是正・バス表・実イベント表・ODD 文書) |
| 3D-U0 | **sim 側 floor クランプ**(scheduler.py で建物階数超の floor がそのまま通る=L1 が変わる修正。表示側は 2026-08-02 修正済み) | **新規**。推奨=conf トグル既定 OFF で実装し観察ランで ON |
| ~~3D-U1/U2~~ | 高精細 3D の採否 | **承認済み**(2026-08-02: **松案で実装**指示・不要になれば竹へ縮退可の方針。U3=都区部点群は調査不要のまま) |
| RW-U1 | **現実フィードバック動線**([research](docs/research/real-world-feedback.md)): ライブカメラ自動取得=不採用(YouTube 規約)・目視転記のみ可・較正3層(L0 初期条件/L1 パラメータ較正/L2 事後検証・状態同化なし)・本選中取得計画(アメダス/WBGT/JARTIC/ODPT 自動+ダッシュボード目視) | **新規・承認求む**(事前準備の登録作業は 8/5〜の期限あり=提案 §4-1) |
| SV-U1 | **サーベイ反映 18 項目**([research](docs/research/llm-social-sim-survey.md) §3)の採否。~~◎印=S-01/S-02/S-03/S-04/S-16~~ → **◎5件は第92バッチで実装済み**(2026-08-05・ユーザー承認「SV-U1の実装を始めて」)。残=○/△ 13項目(S-05〜S-15/S-17/S-18)の採否は本選後 or 個別判断。**注意**: 事前登録に前文「主張の境界」+§3-F(stylized facts)が増えた=U-10 承認パッケージの承認対象2点追加(分散比の閾値・F1 の θ 数値化は §7 未決事項) | ◎5件**完了**・残13項目は判断待ち |
| DT-U2 | UE5 デモ動画 | 保留のまま(本選中判断) |
| **DP-U1** | **CEJC(日本語日常会話コーパス)の有償契約**の可否と時期 | **新規**(2026-08-03)。間に合わなければ名大会話コーパス無償統計で C 層を回す(実装はその前提で先行) |
| **DP-U2** | **心モデル候補の最終ショートリスト**(3B〜14B×5〜6本+プラセボ1本) | **新規**(2026-08-03)。バッテリーハーネス完成後に候補リスト+実測を添えて提案する |
| **DP-U3** | **観察ラン構成の 25万転換への改訂**(OBS-U1 の人数前提・fleet 構成・engaged/day_plan を本選 ON にするか) | **新規**(2026-08-03)。8/15-16 診断ラン前に改訂版提案書を出す |
| **DP-U4** | **engaged 較正の制御量**: 原文書の不整合(§6=4〜8 **呼**/人/日 vs §8=4〜8 **エピソード**/人/日は別量。第87実測=1.84 ターン/エピソード・エピソード 7.38 は帯内だが滞在 30.4% は超過) | **新規**(2026-08-03)。θ_in 実 LLM 較正(8/15-16)までに決める。推奨=**呼数**(予算式 N×f×D の f と直結) |
| **IF-U1** | **LLM⇄世界インターフェース増強**([監査](docs/research/llm-world-interface-audit.md)・[計画](docs/plans/if-sv-p4-plan.md)): ~~実装保留~~ → **実装承認済み**(2026-08-05「IF-U1の実装を始めて」)。**IF-A 完了**(=IF-1+穴2件)・**IF-B 完了**(拒否通知3水準+第87脱出条件(1)実バグ修正)。**IF-C 完了**(噂 Item+MT stifler)・**IF-D 完了**(痕跡=集約+蒸発)。残=IF-E(会計=検査先行)実装中。IF-D 補足: trouble 階層の源(crime/nuisance)は diversity 層既定 OFF のため diversity OFF ランでは空振り・「痕跡が後続行動を変えたか」の DiD 解析は別バッチ。**注意**: 第87 の engaged 実測値(7.38エピソード/滞在30.4%)は脱出条件(1)不発火バグ込みの測定=8/15-16 の θ_in 再較正で再測(DP-U4 と同時) | IF-A/B **完了**・IF-C〜E 実装中 |

### 決定済み(2026-07-31・履歴)
NEW-2=本選 **8/15–8/30 で確定**(指示書の 8/8 は誤り)/GPU 申請・ODPT 規約確認=ユーザー側完了/
NEW-1・NEW-3=承認(検証→計画→実装。R1 柔軟化は repro_tier 方式を採用)/ID-U1=**第72(ダンバー=現第75)まで本選前**/
DT-U1=P0+P6 を本選前に実施/DT-U3=用語問題はユーザーの「スナップショット型 DT」定義の提示により**再提案タスクに置換**
(観察ランは再現性を厳密に求めない方針も同時に確定)/DT-U4=本選後先頭/ID-U2=フル版は本選後(設計文書は先行可)/
ID-U3=エコー除外は新列並記(既存列不変)/指示書ファイルの処遇=Fable 委任→docs/plans/source/ へ保存・重複1本削除。
**2026-07-31 追加決定**: NEW-4=認知プログラム大枠承認(修正3点: ①天候=同期不要・サンプリング/生成型で可
=DT-S1 はこの形で決着 ②物理=できれば本選前・直前数日は検証/調整に確保 ③発火源に内省・会話を追加・
予測誤差大は「世界モデルの書き換え」を駆動)+実装前 web リサーチ必須+体制=Fable5 計画/Opus5 実行を継続。

## 4. 持ち越し小粒(未着手)

- `analyze_sweep` への **llm_health 3列接続**
- ~~**SFM 推奨 param の昇格**~~ → **2026-08-05 P4-2/3 で conf 化済み**(`physics.sfm.{far_field, v_of_s, wall}` 既定 OFF/現行値・観察ランで ON にするかは OBS/DP-U3 改訂時に判断)
- **IF-C 残課題(2026-08-05)**: ①凍結指標 c_transmission 等は Item.kind を見ないため **ON ランで噂が混ざる**(切り分けは解析側 item_id 接頭辞 `rumor-`・既定 OFF 無風)②pool dehydrate が `_rumors` を運ばない=街を出て戻ると噂を忘れる(pool ON では reach 過小)③誕生は step 末走査=1 step 遅れ ④Item.transmissions が上限なし(25万ではホット噂で O(N)=正典を L1 に置く再設計は別バッチ)
- **P4 残課題(2026-08-05)**: ①**D=ボトルネック specific flow の水準不足が未解明**(壁主因仮説は部分否定・残候補=接触項不在/τ=0.5s/v0分布 1.19 vs 実測1.41/定常部の取り方)②**高密度(ρ_global≥2)の壁貫通脱出**(対人斥力 clip 後が壁1本を上回り v_max クリップが向き保存で貫通=接触項 or v_max クリップの再設計が要る。**FD の高密度点はこの汚染込みでしか測れていない**)③(λ,A2,B2,T,ℓ,B_w) 同時最適化未実施(段階解)④ρ_meas が1.5 で頭打ち=判定 B 合格は弱い証拠
- **D16 屋内 ON**
- **D17 実験**
- **4系統レーン2**(B-L1 以降)
- ~~**`exit_building` の node 張り替えと `_apply_free_action`/`_route_to` の整合調査**~~ → **2026-08-03 実害を実証し修正済み**(本選構成 open_actions ON+実 LLM の where+遠距離で `_phase_move` が KeyError クラッシュ・mock は where を返さず完全潜在化していた。`and not agent.building` guard 1行+回帰テスト)
- ~~**pool dehydrate の関係台帳20件切りと dunbar 休眠の相互作用**~~ → **2026-08-03 conf 化済み**(`pool.relations_cap`/`episodes_cap`・既定=現行値で挙動不変・観察ランで広げられる+相互作用テスト固定)
- **3D エクスポータ側のメモリ**(`reconstruct_tracks` が全展開=10日ラン規模で GB 級。「ブラウザに載るか」は第76で解決済みだが「一括で組めるか」は別課題)
- ~~**WallCrowd.forces() が揺らぎ項 ξ を落としている**~~(壁ありで noise 完全無効を P2 比較で実測発見)→ **竹-3 で修正済み**(構造的に再発不能・ξ 実測=レーン形成改善なしと訂正)
- ~~**サブプロセス系テストの xdist 並列フレーク2件**~~ → **2026-08-03 loadgroup 直列化済み**(pyproject addopts=--dist loadgroup・グループ `subproc_run` 実測42s・フルゲート2回連続緑)
- ~~**LLM バックエンドの呼び出し全体ハードデッドライン欠落**~~ → **2026-08-03 修正済み**(`llm/deadline.py`=別スレッドタイマーでソケット shutdown・`model.call_deadline_s: 300`・4バックエンド適用・病的生成スタブで実発火テスト・mock/既定 summary バイト一致)
- **竹-4 持ち越し群**(2026-08-02→08-03 で①②解消): ~~①ゾーン通過区間の L1 位置欠落~~→zone_gate から直線補間(補間である旨をメタ宣言・未閉区間は捏造せず件数のみ)・~~②所有中 node の同席キー古さ~~→通過点前進時に node 更新。残=③pool dehydrate が `_phys_*` を運ばない(現行条件では非発火)④span_m グラフ長 vs 物理直線の実効速度差 ⑤**P4 較正は高密度条件が必要** ⑥サブステップ軌跡の記録 ⑦10日ラン ON 時は総サブステップ数の事前見積・`planning.py` 契約化は残置第一候補のまま

## 5. 設計制約と受領文書

### 5.1 設計制約(R1 ドクトリン)の現況と柔軟化

現行の恒常制約: ①新機能は既定 OFF ②既定 OFF で golden L1 バイト一致 ③k 非依存 ④no-fingerprint
⑤用途別乱数 stream ⑥観測がシムを変えない。
**2026-07-31 の方針確定**: 観察ラン(本選 10 日)は再現性を厳密に求めず、repro_tier=journal/none の機能も投入可。
検証ラン(verify)は strict のみ。この二重化は**第72で構造化済み**(registry.py+run.mode。verify モードは
planning/tools/rules=LLM 自由文が世界状態になる3機能も落とす=正直な宣言)。
既定値は現行動作のまま=golden 資産は verify 側の検収装置として恒久維持。

### 5.2 受領文書の処遇(2026-07-31 確定)

二重化指示書は [docs/plans/source/](docs/plans/source/) に原文保存(dual-mode-instructions / dual-mode-instruments /
dual-mode-requirements)。リポ直下の原本3本は移動・バイト同一重複1本(instruments 1)は削除。
検証済みの統合計画は [dual-mode-observe-verify-plan.md](docs/plans/dual-mode-observe-verify-plan.md) が正典。

**2026-07-31 受領の3本**(認知・物理・DT定義)も同所へ原文保存: physics-instructions / cognition-design-record
(=設計決定の正典)/ dt-alignment-record。統合計画は [cognition-physics-plan.md](docs/plans/cognition-physics-plan.md)。
dt-alignment の方針 1-7 は大半実装済み(可視性=C0・観測層=P0/P6・差分管理=world.mod)で、新規採用は
「系譜的同一性」の自己記述語彙のみ。

**2026-08-02 受領**: リポ直下 `3800683.pdf`(Mou et al., *From Individual to Society*, ACM Computing Surveys 58(11),
2026 = LLM 社会シム・サーベイ)。**原本はユーザー管理のまま未コミット**(PDF 原本リポ外維持の掟)。
読解と反映点 18 項目は [docs/research/llm-social-sim-survey.md](docs/research/llm-social-sim-survey.md)(SV-U1)。

**2026-08-02 受領(設計議論)**: [docs/plans/source/design-discussion-20260802.md](docs/plans/source/design-discussion-20260802.md)
(目標再定位=25万人・day_plan v1・engaged モード・プラセボ梯子・バッテリー・縦横煙。**概念決定済み・実装詳細は委任**と原文明記)。
統合計画は [dayplan-engaged-plan.md](docs/plans/dayplan-engaged-plan.md)。
**訂正**: 原文書 §9 の「GPU 申請 8/9 前」は申請提出済みのため消滅。スループット実測(prefix caching 込み)は 8/15-16 診断ランに統合。

### 5.3 日程

**本選 8/15–8/30**(提出 8/30)・**10日ラン 8/16–8/26**・**8/12-14 フリーズ**(新機能追加禁止=検証と微調整のみ)・
**8/15-16 診断ラン**(σ 再実測 → θ 再較正 → U-10 確定判定 → 人数最終確定)。GPU=A5000 級 ×7枚(単一ノード)。
