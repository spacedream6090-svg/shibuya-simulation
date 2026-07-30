# STATUS — 現況台帳(実装済み / 計画のみ / ユーザー判断待ち)

> **更新プロトコル**: 実装バッチのコミットごとに必ず本ファイルを更新する(検収の一部)。
> ここは「今どこにいるか」の一覧だけを持ち、詳細は各リンク先(計画書・devlog)が正典。
> 最終更新: **2026-07-31**(〜第69バッチ+計画書2本 f9e2049+二重化指示書の一次実査まで反映・テスト 1846 緑)

## 1. 実装済み(主要システムの現在地)

新機能はすべて **既定 OFF**(R1)。バッチ履歴の全文は [docs/log/devlog.md](docs/log/devlog.md)
(圧縮版 [devlog-compressed.md](docs/log/devlog-compressed.md) Block #0〜#12)。

| 領域 | 内容(主なトグル) | バッチ |
|---|---|---|
| 世界基盤 | 渋谷実地図(PLATEAU/OSM)・実ダイヤ(ODPT)・日次 presence 名簿制・経済/制度/物流・現実較正(calibrate_report) | 〜第58 |
| 関係性の内生化 | 承諾/拒否の内生(relations_endo)・treatment 実験一式(endogenous_accept)・誘い相手の内生(endogenous_invite) | 第62-64 |
| LLM 健全性 | fallback 率など L2 KPI・watchdog_llm・observer.llm_health 3列 | 第66/P0 |
| 反実仮想の器 | world.mod = edges_closed / edge_speed_scale / open_hours(+gate_capacity 予約) | 第67 |
| 実高さ・可視 | building_heights(3,531棟)・build_visibility(2.5D LOS 行列) | 第67-68 |
| 場所の意味づけ | labeling.place_binding(造語の場所束縛→知覚1行) | 第69 |
| 決定論・再現基盤 | RngHub named streams(68+)・CachedLLM(llm_cache.jsonl=応答の内容アドレスキャッシュ・D13)・golden L1 バイト一致・k非依存(controls.mode=compute_matched)・no-fingerprint | 恒常 |

## 2. 計画のみ(未実装)

| 計画 | 内容 | 状態 |
|---|---|---|
| [DT統合](docs/plans/dt-integration-plan.md) | P0 軌跡バイナリ化→P6 追いかけ再生→P5 SUMO→P4' USD→P7→P1 3D Tiles→P2 UE5 | **承認待ち**(DT-U1) |
| [第1回IDEA組込](docs/plans/hackathon1-ideas-implementation-plan.md) | 第70(エコー計測+未定義行動+沈黙)→第71(規範化ステージ+ゼロ対照)→第72(ダンバー)→本選後(場所二層知覚・誤情報構造化) | **承認待ち**(ID-U1) |
| [4系統拡張レーン2/3](docs/plans/twin-physics-vision-affordance-plan.md) | B-L1 歩行者ネットワーク以降・C1 広告接触・D2 以降 | レーン1完了・レーン2以降未着手 |
| [非定常性の事前登録](docs/plans/stationarity-preregistration.md) | 閾値+診断ラン日数+10日ラン解釈方針 | **U-10 承認待ち** |
| 観察/検証ランの二重化(新着) | FREE/REPLAY/STRICT・機能レジストリ(repro_tier)・真偽台帳・コホートタグ ほか(§5) | **受領のみ・検証/計画化前** |
| 持ち越し小粒 | analyze_sweep への llm_health 3列接続・SFM 推奨 param 昇格・D16 屋内 ON・D17 実験 | 未着手 |

## 3. ユーザー判断待ち

| # | 事項 | 推奨 |
|---|---|---|
| U-10 | 事前登録の閾値承認+診断ラン日数+「10日ラン=burn-in 内」の解釈方針 | 提案済み(過渡期観察と明示) |
| DT-U1 | P0+P6(2.5-3.5日)を本選前に入れるか | 入れる |
| DT-U2 | UE5 デモ動画を提出物に使うか | 保留(本選中判断) |
| DT-U3 | 「Digital Model(一方向・事後)」の用語採用 | 採用 |
| DT-U4 | 3D Tiles / USD 書き出しの優先度 | 本選後先頭 |
| ID-U1 | 本選前は IDEA 第70-71 まで(≈4.5日)か第72まで含めるか | 第70-71 まで |
| ID-U2 | 誤情報構造化の設計レビュー時期 | 本選後先頭(設計文書のみ先行可) |
| ID-U3 | エコー除外を既存 KPI の既定にするか | 新列並記(既存列不変) |
| NEW-1 | 二重化指示書(§5)の採否と範囲・IDEA/DT 計画との優先順位統合 | 検証→統合計画を先に作る |
| NEW-2 | 指示書の想定日程「本選 8/8-8/23・8/8 締切」と現行認識「本選 8/15-8/30・GPU申請 8/9」の食い違い | 要ユーザー確認 |
| NEW-3 | R1 制約の柔軟化(repro_tier 3等級+ランモード observe/journal/verify)を採用するか | 採用寄りで検証 |
| (ユーザー側) | GPU 申請フォーム(締切 8/9)・ODPT 規約の目視確認 | — |

## 4. 設計制約(R1 ドクトリン)の現況と柔軟化

現行の恒常制約: ①新機能は既定 OFF ②既定 OFF で golden L1 バイト一致 ③k 非依存(LLM 呼数が世界を変えない)
④no-fingerprint ⑤用途別乱数 stream ⑥観測がシムを変えない。
これらは物理法則ではなく**現行ポリシー**。二重化指示書は「再現性を機能ごとの宣言属性
(repro_tier = strict / journal / none)にし、ランモードで自動取捨する」柔軟化を提案しており(NEW-3)、
採用すれば「観察ランは全部盛り・検証ランは strict のみ」が構造的に両立する。

## 5. 受領済み・計画化前の文書(2026-07-31 受領)

| ファイル | 内容 | 処遇 |
|---|---|---|
| claude-code-instructions.md(リポ直下・未追跡) | 二重化 Phase 0-2(記録と再生・対照条件・完全決定論化・T1-T8) | 検証→計画化後に吸収・削除予定 |
| claude-code-instructions-instruments.md(同) | 機能フラグ Part A〜G(レジストリ・真偽台帳・語彙帰無・認知階層・円環の閉じ・環境差分・指標凍結) | 同上 |
| claude-code-instructions-instruments 1.md(同) | 上とバイト同一の重複 | 削除候補(要ユーザー確認) |
| ~/Downloads/dual-mode-requirements.md(リポ外) | 上2本の要件定義版(FREE/REPLAY/STRICT の根拠) | リポ外のまま参照 |

一次実査メモ(2026-07-31): T8(実時刻・グローバル乱数の不在)は**現行で既に成立**。
CachedLLM は content-addressed 応答キャッシュとして既存だが、**REPLAY の fail-fast モードとプロンプト全文の
永続化が無い**。world.mod≈env.variant_id、Part E≈IDEA③④、Part B≈IDEA⑦(投入時期が指示書=本選前必須 vs
IDEA 計画=本選後で**衝突**)。新規性が高いのは機能レジストリ・状態ハッシュチェーン・metrics_spec_hash。
