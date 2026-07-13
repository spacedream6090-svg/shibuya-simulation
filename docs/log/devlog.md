# 開発ログ(ライブ)

> このプロジェクトを「作る側」の意思決定・節目の記録。シミュレーション内部の観測層ログとは別物。
> **プロトコル**: ユーザーとの1往復ごとに1エントリ追記。エントリが10に達したら圧縮して [devlog-compressed.md](./devlog-compressed.md) へ移し、本ファイルをリセット。設計の正典は [../design.md](../design.md)。
> **圧縮履歴**: devlog-compressed.md(Block #0: プロトコル前史 / #1: ログ機構〜分野1-3 / #2: リサーチ完走〜決定アジェンダ / #3: D0-D17決定→P0実装→世界v2-v5 / #4: 生態系→docs完遂→現実ギャップ全波→第9バッチ / #5: ODPT実ダイヤ→制度深化完遂→自己モデル・出来事誘発内省→現実較正→実LLM初証拠→日常プロファイル(第10〜14バッチ) / **#6: 開放行動→世界解釈の観察→マルチモデル対応(第15〜24バッチ)**)。

**ライブエントリ数: 4 / 10**

---

### Entry 1 — 2026-07-13 — 第25バッチ: フォルダ構成の復元(実装を直下へ・移動途中状態の修復)
- **依頼**: 直下・shibuya バックアップ・新しいフォルダーに分散した状態を整理し、今までの実装を直下に復元。
- **診断**: 直下=手動移動の途中状態(1,587件・conf/.gitignore/pyproject.toml/worldview.py 等168件が欠落)/
  shibuya バックアップ=最も完全(1,755件・07-12 21:27頃)/新しいフォルダー=残骸14件(全てバックアップと
  ハッシュ一致 or 旧版)。曖昧2件を diff で判定: devlog.md=バックアップ側が正(圧縮後リセット版)・
  unimplemented-inventory.md=直下が正(バックアップ側は改行混入のみ)。
- **実施**: バックアップから欠落162件を補充コピー(既存1,588件は一切上書きなし・mtime保持)→全1,750件の
  ハッシュ照合で欠落0・内容差は意図した1件のみ→圧縮前devlog全文を docs/log/devlog-block6-fulltext.md に
  退避→新しいフォルダー削除。shibuya バックアップは無傷で保持。shibuya-sim はユーザーがデスクトップ直下へ
  退避済み(リポジトリ外)。
- **検証**: 直下から golden/contracts/router_wiring/bridging/detect_emergence 26本緑・.gitignore 機能確認
  (data/odpt_challenge・runs は除外維持=ODPT再配布制限の防壁)・フルスイート実行中。
- **注意(要ユーザー判断)**: リポジトリは**コミットが1件も無く**、現行実装は全て未追跡。今回の復元を救ったのは
  git でなく手動バックアップだった。初回コミットの実施を推奨(ユーザー承認待ち)。

### Entry 2 — 2026-07-13 — 第26バッチ: 初回コミット+GitHub非公開リポジトリ作成(ユーザー承認済み)
- **依頼**: 「GitHubの新しいリポジトリを作ってコミットする理解でいい?それなら実行して」→ 実行。
- **コミット前検査**: .gitignore に手動バックアップ(shibuya バックアップ/)と .claude/settings.local.json を追加/
  staged 410件に対しシークレットスキャン(sk-/ghp_/AKIA/ODPTキー直書き)=検出なし・40MB超=なし・
  runs/・odpt_challenge/・バックアップの除外を確認。
- **実施**: 初回コミット 2727e91 → gh CLI 導入(winget)→ デバイスフロー認証(ユーザーがブラウザで承認)→
  `gh repo create shibuya-simulation --private --source=. --push`。
  リポジトリ: https://github.com/spacedream6090-svg/shibuya-simulation(**非公開**・main)。
- **これで手動バックアップ(shibuya バックアップ/)は git が代替**=ユーザー判断でいつでも削除可。

### Entry 3 — 2026-07-13 — 第27バッチ: 手動バックアップをリポジトリ外へ退避
- ユーザー指示で「shibuya バックアップ」をデスクトップへ移動(→ `Desktop/shibuya バックアップ_20260712`・日付を付与)。
  git が保全を代替済み(初回コミット 2727e91)。.gitignore の除外行は再発防止として残置。リポジトリ直下は実装+runs のみに。

### Entry 4 — 2026-07-13 — 第28バッチ: 日次自動バックアップの仕組み(シミュ実装から独立)
- **依頼**: 一日の終わりに作業内容を shibuya バックアップへ自動バックアップする仕組み(シミュ実装とは別の部分で)。
- **実装**: ops/backup-daily.ps1(新設・PowerShell・UTF-8 BOM)+ タスクスケジューラ
  「shibuya-simulation-daily-backup」(毎日23:30・PCが寝ていれば次の機会に実行=StartWhenAvailable)。
  出力= Desktop\shibuya バックアップ\ ①mirror(robocopy /MIR 増分完全鏡像・runs/.git込み)
  ②snapshots/code-YYYY-MM-DD.zip(runs/.git除く軽量日付版・14日分保持で自動削除)③backup-log.txt(1行/回)。
- **検証**: 初回手動実行=9秒で完走(mirror 1,752ファイル・zip 6.3MB・exit 0)。次回自動実行 2026-07-13 23:30。
- 三重の保全体制が完成: git(コミット履歴)+日次mirror(完全鏡像)+日付zip(14日ロールバック)。
