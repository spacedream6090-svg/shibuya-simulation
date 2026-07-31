# 観察/検証ランの二重化+機能レジストリ 実装計画(検証済み)

> ステータス: **実装完了**(第70〜78 全9バッチ・2026-07-31 同日完結・テスト 1846→2150。T1〜T8 全達成。
> 2026-07-31 ユーザー承認=NEW-1/NEW-3・実装順の決定は Fable に委任)。
> 原指示書3本(2026-07-31 受領): [dual-mode-instructions.md](source/dual-mode-instructions.md) /
> [dual-mode-instruments.md](source/dual-mode-instruments.md) / [dual-mode-requirements.md](source/dual-mode-requirements.md)。
> 前提日程: **本選 8/15–8/30・10日ラン 8/16–8/26**(指示書の「8/8 締切・本選 8/8–8/23」はユーザー確認により誤りと確定。
> GPU 申請・ODPT 規約確認は完了済み)。
> 関連方針(2026-07-31 ユーザー): 本選の観察ランは**再現性を厳密に求めない**。repro_tier=journal/none の
> 機能も観察ランには積極投入してよい(=指示書 Part A の思想をそのまま採用)。

## 1. 検証結果 = 原指示と現行コードの差分

### 1.1 既に成立しているもの(再実装しない)
| 指示書の要求 | 現行の実体 |
|---|---|
| T8(実時刻・グローバル乱数の排除) | src/ に `datetime.now()`・グローバル random は **grep ゼロ**。世界時間は sim clock(step/sim_min)基準 |
| content-addressed LLM キャッシュ | [cache.py](../../src/society/llm/cache.py) CachedLLM(D13)= key=sha256(model+params+think+prompt)・llm_cache.jsonl に永続化・run 間共有可 |
| 意思決定ジャーナル | L1(append-only・part parquet・flush_segment)が行動/移動/発話/対話相手を全記録。**T2 の「意思決定完全一致」の比較対象は L1 バイト比較として既に運用中**(golden がその装置) |
| STRICT 相当 | mock バックエンド+RngHub named streams = seed のみからバイト一致(golden テスト群が常時検証) |
| FREE 相当 | 実 LLM+cache(初回保存)が現行の既定動作 |
| world snapshot | checkpoint 既存(中央管理・resume 検収済み) |
| env.variant_id 相当 | world.mod(第67)= edges_closed/edge_speed_scale/open_hours。ラン開始時固定・profile 指定 |
| 並列適用の決定論 | generate_many のバリア+逐次格納(cache.py)・エージェント適用順固定の既存設計 |

### 1.2 欠けているもの(今回実装する)
REPLAY fail-fast モード/**プロンプト全文の永続化**(現状キャッシュは応答のみ・L1b は call_id 等のみ)/
run manifest の統合(git SHA・config hash・スイッチ全状態・各種 spec hash)/metrics_spec_hash/
機能レジストリ(repro_tier)+ランモード自動取捨/ablate 4種(llm_off・propagation_off・cognitive_tier・
shuffle_partners)/真偽台帳+信念+伝播木+検証行動(Part B)/コホートタグ(Part E1)/状態ハッシュチェーン。

### 1.3 指示書からの訂正・適応(理由つき)
1. **日程**: 8/8 前提の優先順位圧縮は不要。本選前に Part B まで含めて入る。
2. **「閾値未設定ならラン開始時エラー」→ 解析実行時エラーに変更**。シム本体を指標定義に依存させると
   「観測がシムを変えない」原則に反する。凍結指標の閾値は事前登録文書(U-10・
   [stationarity-preregistration.md](stationarity-preregistration.md) と同じ枠組み)+解析スクリプトの必須引数で担保。
3. **Part B は IDEA⑦(誤情報の構造化)と統合**: 本選前=ミニマル台帳(fact+信念+伝播木+検証行動+漏洩検査)。
   truth_status 5 分類・情報源別減衰などフル版は本選後(ID-U2 決定どおり)。二重実装を避ける。
4. **Part E は IDEA③④と同一バッチに統合**(規範候補検出が第71計画の規範化ステージ検出器と同物)。
5. **FREE/STRICT はモードとして新造しない**。実体が既存なので、新規は (a) REPLAY の fail-fast (b) ランモード
   (observe/journal/verify)の宣言と自動取捨のみ。既定は現行動作(mode 未指定=従来どおり)= R1 維持。
6. **プロンプト全文記録の「省略不可」要求**は R1(新機能既定 OFF)と衝突するため、**新規別ファイル**
   (L1 バイトに触れない)として実装し observe/journal プロファイルで必須 ON、既定は conf で ON
   (golden は L1 のみ比較なので無風)。容量は 実測して報告(mock 概算+実 LLM 呼数実測 1,014 入力 tok/呼 から
   10 日ラン概算)。逼迫時に削るのは snapshot 側という指示は維持。

## 2. 統合実装順(第70〜78・全体で本選前完了目標)

| バッチ | 内容 | 主な受入基準 | 目安 |
|---|---|---|---:|
| **第70** | IDEA①エコー計測+②未定義行動レジスタ+沈黙(着手済み・実装計画は [hackathon1-ideas-implementation-plan.md](hackathon1-ideas-implementation-plan.md)) | golden 不変・新列並記(ID-U3) | 1-2日 |
| **第71** | **LLM 入出力ジャーナル**(プロンプト全文+応答+params+key の per-run 記録・resume 重複なし)+**REPLAY fail-fast**(model.cache_mode: free(既定)/replay。miss 時に step/agent/key を明示して即例外・フォールバック絶対禁止)+**run_manifest.json**(git SHA・config hash・run_seed・モデルID・スイッチ全状態・開始時刻) | T2(FREE→REPLAY で L1 一致)・T5(1レコード削除→即 fail)・golden 不変 | 1.5日 |
| **第72** | **機能レジストリ+ランモード**: 全主要トグルに repro_tier(strict/journal/none)/affects_k/fingerprint_risk を宣言。run.mode=observe/journal/verify(既定 none=現行動作)。モード超過機能の自動 OFF+manifest/ログへの明示+目立つ警告。解析側のラン間比較ガード(tier 混在は明示フラグ必須)。未宣言トグルを検出する CI テスト | verify モードで none/journal 全 OFF でも完走・自動 OFF が黙って起きない | 1.5日 |
| **第73** | **真偽台帳ミニマル(Part B)**: fact 台帳(ID・発生 step・場所・真値・目撃可能条件)=エージェント絶対不可視。信念状態(値・確信度・情報源・取得 step・検証済み・親ノード=伝播木)。検証行動3種(現場確認・当事者に聞く・ネットで裏取り)を freedom.open_actions の前例で行動空間に追加(誘導プロンプト禁止)。**台帳→プロンプト漏洩の静的検査+実行時アサーション+テスト** | 漏洩検査テスト・既定 OFF golden 不変・k 不変 | 2.5日 |
| **第74** | **IDEA③④+Part E1 統合**: 規範化ステージ4段検出器+coiner/institutionalizer 分離(観測のみ)。コホートタグ(初 presence step・その時点の規範状態スナップショット)。ゼロ対照セル(traits 定数化)+初期フレーム共変量。下方因果の解析スクリプト(成立前後コホートの参入初日行動分布比較) | 観測のみ=プロンプト不変・実験セルは CRN 基盤に追加のみ | 2日 |
| **第75** | IDEA⑤ ダンバー維持コスト+忘却/再会(既存 LRU 拡張・resume 検収注意) | 既定 OFF golden 不変 | 1.5日 |
| **第76** | DT P0 軌跡バイナリ化(quantized+遅延ロード。1万体10日の viewer/UE 出力を成立させる) | 既存 19/19 バイト同一検証の流儀 | 1.5-2日 |
| **第77** | DT P6 追いかけ再生(part parquet を読むだけのライブ風画面) | ドクトリン無傷(読み取り専用) | 1-1.5日 |
| **第78** | **装置系の締め**: ablate 4種(llm_off=素朴ルール・propagation_off=発話生成するが文脈非注入で k 不変・cognitive_tier=fleet 強制下位・shuffle_partners)+状態ハッシュチェーン(verify 用・既定 OFF・T1/T6)+metrics_spec_hash(指標コードの正規化ハッシュ→manifest)+凍結3指標の定義(閾値は U-10 で承認)→**事前登録の承認依頼(8/12–14 目安)** | T1・T6・T7・propagation_off の fingerprint 方針は実装前に提示 | 2日 |

- 合計目安 ≈13.5-15 日 vs 暦 14 日(8/1〜8/14)。直近の実速度(レーン1=6バッチ/日)から本選前完了は現実的。
  遅延時のスリップ順: 第78 の ablate 4種→本選前半(対照ランは装置さえあれば本選後に回せる)・第75。
- **観測点(記録しないと 10 日ランから永久に失われるもの)を装置より先に**: 第71(全 LLM I/O)・第73(信念・伝播木)・
  第74(コホートタグ)は 8/15 までに必須。これが指示書の最優先思想であり、順序の根拠。
- U-10(事前登録閾値)のタイミングはユーザーから委任: **第74 完了後〜第78 で承認依頼**(10 日ラン開始 8/16 の前)。

## 3. 検収条件(全バッチ共通)
既定 OFF(または新規別ファイルのみ)= golden L1 バイト一致・draw 数同一・k=free/off 呼数一致・resume==straight・
no-fingerprint・フルゲート緑。実 LLM フルランはローカル禁止(mock または ≤24step スモークのみ)。
各バッチのコミットで [STATUS.md](../../STATUS.md) を必ず更新。

## 4. リスク
- **ジャーナル容量**: 実測 1,014 入力 tok/呼・14-25 呼/agent/日 → 1万体10日で入力全文は数十 GB 級になりうる。
  zstd 圧縮+共通プレフィックス(テンプレート)の辞書化で圧縮率実測を第71で報告。削るのは snapshot 側。
- **cache_mode=replay と generate_many の整合**: 並行発行経路のミス検出はフェーズ1(逐次)で行う=決定論維持。
- **レジストリの網羅性**: 一括全登録は事故のもと。主要トグルから登録し、未宣言検出 CI で漸進的に埋める。
- **Part B 漏洩**: 静的検査(import 経路)+実行時アサーション+プロンプト文字列への台帳値混入テストの三重。
- **フルスイート時間の伸び**(現行 1846 本・251s): バッチごとに +1-2 分想定。許容。
