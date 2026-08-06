# PENDING — 未実装・実装中・ユーザー判断待ち

> 本ファイルは **まだ終わっていないもの**だけを持つ。完了済みは → **[IMPLEMENTED.md](IMPLEMENTED.md)**(決定の履歴も同所の年表と git log が正典)。
> 索引と最終更新は → **[STATUS.md](STATUS.md)**。
> 最終更新: **2026-08-06**(ユーザー指示で完了項目を除去し全面整理)。

---

## 1. 実装中レーン(承認済み・リサーチ→実装の順)

| レーン | 内容 | 状態 |
|---|---|---|
| **IF-E2 案B** | **org の会計主体化+rest-of-world(域外)概念実装**(2026-08-06 ユーザー決定=案B。域外取引は概念のみで可・他シミュレーション例を参考に)。org 残高・賃金の資金源・支払不能規則・spend の受け手解決・RoW 部門・残高の L2 サイドカー(=検査①が全部門で成立) | **リサーチ中** → 実装 |
| **SV 残13項目** | S-05〜S-15/S-17/S-18 の採用(2026-08-06 ユーザー決定「積極的に採用・リサーチを怠らない」)。凍結14ファイル抵触の回避設計が焦点 | **リサーチ中** → 実装 |
| **OBS-U2 準備** | **Δt=1分にできる準備**(2026-08-06 ユーザー指示)。本番は Δt=10 のまま・1分の並行小ランを走らせられる状態を作る | **設計調査中** → 実装 |
| **PUB-U1** | 公開ミラー修正(2026-08-06 ユーザー決定=Fable 案で進める・提出用 public の修正のみ): docs/**・台帳3md を除外し README/ETHICS/LICENSE は残す。**ライセンス地雷2件**(商業施設/区サイト情報=転載不可・OSM 由来=ODbL)の除外を確認して同期 | **作業中**(Fable 直轄) |
| P4 残り | D(ボトルネック J/w 水準)の原因切り分け(接触項不在/τ/v0分布/定常部)・高密度の壁貫通脱出(接触項 or v_max クリップ再設計) | 未着手(フリーズ前は任意・§4 参照) |

## 2. 提案書(作成中・提示済み)

| 項目 | 状態 |
|---|---|
| **DP-U2 提案書**(心モデル最終ショートリスト) | **ドラフト作成中**(2026-08-06 ユーザー指示)。候補3B〜14B×5〜6本+プラセボ・混成 fleet 配分・D層 n=30 正規測定計画 |
| **DP-U3 提案書**(観察ラン25万転換改訂) | **ドラフト作成中**(同上)。総人口25万×在場制御・メモリ90〜120GB・新機能 ON セット改訂・8/15-16 診断→8/16 開始手順 |
| 観察ラン ON 構成(旧提案) | [observe-run-config-proposal.md](docs/plans/observe-run-config-proposal.md) 提示済み → **DP-U3 改訂版で置換予定**。OBS-U1〜U3 の判断は改訂版で |
| DT スナップショット再提案 | [dt-snapshot-integration-proposal.md](docs/plans/dt-snapshot-integration-proposal.md) 提示済み → DT-S1 ほか判断待ち |
| S-quick(S0/S1/S2/S5/S9) | 計 ≈1.8日。承認待ち(入力来歴・observe.yaml 是正・バス表・実イベント表・ODD 文書) |

## 3. ユーザー判断待ち(残りのみ)

| # | 事項 | 状態 |
|---|---|---|
| **U-10** | 事前登録の閾値承認+10日ラン解釈方針。**承認対象が2点増えた**: 前文「主張の境界」+§3-F stylized facts(分散比の閾値・F1 の θ 数値化は §7 未決事項) | 8/15-16 診断ラン前に承認依頼(10日ラン 8/16 開始前・タイミング委任済み) |
| **RW-U1** | 現実フィードバック動線([research](docs/research/real-world-feedback.md)): 較正3層・本選中取得計画(アメダス/WBGT/JARTIC/ODPT 自動+ダッシュボード目視) | **承認求む**。⚠ 事前準備の登録作業は 8/5〜の期限=**既に到来**(未承認のまま) |
| OBS-U1/U3 | 観察ラン ON セットの承認・認知 ON の 8/14 留保(OBS-U2=Δt は準備実装へ移行済み) | DP-U3 改訂提案書とセットで判断 |
| **DP-U4** | engaged 較正の制御量=**呼数**か**エピソード数**か(原文書の不整合に由来。第87実測: 1.84 ターン/エピソード)。**推奨=呼数**(予算式 N×f×D の f と直結)。※第87実測値は脱出条件(1)バグ込み=8/15-16 に再測 | θ_in 実 LLM 較正(8/15-16)までに決める |
| NEW-5 | F/N/P 初期値条件の本選配分 | パイロット後に提案 |
| 3D-U0 | sim 側 floor クランプ(建物階数超の floor が通る=L1 が変わる修正。表示側は修正済み) | 推奨=conf トグル既定 OFF で実装し観察ランで ON |
| DT-U2 | UE5 デモ動画 | 保留のまま(本選中判断) |

### 決定済み(履歴の要点のみ・詳細は git log と IMPLEMENTED 年表)
2026-08-06: **IF-E2=案B**(org 会計主体化+RoW 概念実装)/**DP-U1=無償**(CEJC 契約せず名大会話コーパス無償統計で C 層=実装は既にこの前提)/**SV 残13項目=採用**/**PUB-U1=Fable 案で決定**/OBS-U2=Δt1分の準備指示。
2026-08-05: IF-U1 実装承認→IF-A〜E 完了・SV-U1 ◎5件完了・P4-1〜3 完了。
2026-08-02: P2選定=ゾーン別ハイブリッド(委任決定)・高精細3D=松案承認。
2026-07-31 以前: NEW-1〜4・ID-U1〜U3・DT-U1/U3/U4 等(旧台帳 git 履歴参照)。

## 4. 持ち越し小粒(未解決のみ)

- `analyze_sweep` への **llm_health 3列接続**
- **IF-C 残課題**: ①凍結指標 c_transmission 等に ON ランで噂が混ざる(切り分けは解析側 `rumor-` 接頭辞)②pool dehydrate が `_rumors` を運ばない(pool ON で reach 過小)③誕生は step 末走査=1 step 遅れ ④Item.transmissions 上限なし(25万ではホット噂 O(N)=正典を L1 に置く再設計は別バッチ)
- **P4 残課題**: ①D=J/w 水準不足の未解明(残候補=接触項不在/τ/v0分布/定常部)②高密度 ρ≥2 の壁貫通脱出(接触項 or v_max クリップ再設計・FD 高密度点は汚染込みでしか測れない)③6変数同時最適化未実施 ④ρ_meas 1.5 頭打ち=判定B合格は弱い証拠
- **D16 屋内 ON**・**D17 実験**・**4系統レーン2**(B-L1 以降)
- **3D エクスポータ側のメモリ**(reconstruct_tracks 全展開=10日ラン規模で GB 級)
- **竹-4 残**: ③pool dehydrate が `_phys_*` を運ばない ④span_m グラフ長 vs 物理直線の実効速度差 ⑥サブステップ軌跡の記録 ⑦10日ラン ON 時の総サブステップ事前見積・`planning.py` 契約化は残置第一候補

## 5. 設計制約と受領文書(背景・不変)

### 5.1 設計制約(R1 ドクトリン)
恒常制約: ①新機能は既定 OFF ②既定 OFF で golden L1 バイト一致 ③k 非依存 ④no-fingerprint ⑤用途別乱数 stream ⑥観測がシムを変えない。
観察ラン(本選10日)は再現性を厳密に求めず repro_tier=journal/none も投入可・検証ラン(verify)は strict のみ(第72で構造化済み)。

### 5.2 受領文書(原文は docs/plans/source/ に保存済み)
二重化指示書3本・認知/物理/DT定義3本・設計議論まとめ(2026-08-02)・サーベイ PDF(原本リポ外・読解=[llm-social-sim-survey.md](docs/research/llm-social-sim-survey.md))。
統合計画の正典: [dual-mode-observe-verify-plan.md](docs/plans/dual-mode-observe-verify-plan.md)・[cognition-physics-plan.md](docs/plans/cognition-physics-plan.md)・[dayplan-engaged-plan.md](docs/plans/dayplan-engaged-plan.md)・[highfidelity-3d-physics-plan.md](docs/plans/highfidelity-3d-physics-plan.md)・[if-sv-p4-plan.md](docs/plans/if-sv-p4-plan.md)。

### 5.3 日程
**本選 8/15–8/30**(提出 8/30)・**10日ラン 8/16–8/26**・**8/12-14 フリーズ**(新機能追加禁止=検証と微調整のみ)・**8/15-16 診断ラン**(σ 再実測 → θ 再較正 → U-10 確定判定 → 人数最終確定)。GPU=A5000 級 ×7枚(単一ノード)。

### 5.4 本選後(レーン3)
場所二層知覚(IDEA⑥)・誤情報構造化フル版(ID-U2)・SUMO 反実仮想(P5)・USD/3D Tiles(DT-U4)・UE5(DT-U2)・org 会計主体化の拡張(倒産・信用線)・詳細順位は [dt-integration-plan.md](docs/plans/dt-integration-plan.md) §3。
