# Codexレビュー実行キット — レビュー専用(変更禁止)

> 2026-08-16作成。用途=**最終β版のコードレビューのみ**(ユーザー指定: 他の用途では使わない)。
> 実行場所=**gpu-sv-002 の clone**(`~/projects/shibuya-simulation`)を推奨: git追跡ファイルのみ=h.txt・runs/・data/ が物理的に存在しない。
> 全体計画は [finals-endgame-plan.md](../docs/plans/finals-endgame-plan.md) §5。レビューは2回転(1回転目=6パス・2回転目=穴埋め差分+再確認)。

## 1. インストール(サーバー・1回だけ)

推奨=公式スタンドアロンインストーラ(**Node不要**):
```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
codex --version
```
- Ubuntu 22.04はGNUビルドのglibc下限(2.35)ちょうど。不調なら npm 経路へ切替: `npm install -g @openai/codex`(musl同梱・[setup-gpu-sv-002.md](setup-gpu-sv-002.md) §5のnvmを流用)。※npmの無印`codex`は無関係の別物・`@openai/codex`のみ正。
- (参考)Windowsもネイティブ対応済み(`irm https://chatgpt.com/codex/install.ps1 | iex`)だが、本件は**サーバー実行を推奨**(cloneに h.txt/runs/data が物理不在=衛生が構造的)。

## 2. 認証(ユーザー手動・トークンをチャットに貼らない)

ヘッドレス(SSH越し)の公式手順は3通り。**推奨=①デバイスコード**:
```bash
codex login --device-auth      # 表示されたコードを手元ブラウザで入力
codex login status             # 確認
```
② SSHポート転送: 手元PCで `ssh -L 1455:localhost:1455 tsukamoto@10.10.0.102` → サーバーで `codex login` → 表示URLを手元ブラウザで開く。③ 手元PCで認証済みの `~/.codex/auth.json` をサーバーへコピー。

- **プラン**: CodexはChatGPTのFree/Go/Plus/Pro/Business等に同梱(利用枠はプラン依存)。APIキー課金で使うなら `printenv OPENAI_API_KEY | codex login --with-api-key`(API経由は既定で学習不使用)。
- **★学習オプトアウトを必ず確認してから流す**: 個人プラン(Free/Go/Plus/Pro)は既定でコンテンツが学習に使われうる → ChatGPT設定 > Data Controls > 「Improve the model for everyone」をOFF(Business/Enterprise/Eduは既定で学習除外)。Codex側に別トグルがあるという未確認情報もあるためCodexの設定画面も一読推奨。

## 3. レビュー専用の強制(3重)

1. **サンドボックス=読み取り専用**: `~/.codex/review.config.toml` にレビュー専用プロファイル
   (★Codex 0.147実測: 旧`config.toml`の`[profiles.review]`テーブルは**廃止**=あるとエラーで起動拒否。
   プロファイルは`<名前>.config.toml`の別ファイルに**トップレベルキー**で書く。2026-08-16セットアップ済み):
```toml
model = "gpt-5.6-sol"            # 旗艦。利用枠が厳しければ "gpt-5.6-terra"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
approval_policy = "never"        # 非対話。read-onlyなので昇格要求も発生しない
```
2. **AGENTS.md(§4テンプレ)をサーバーのcloneにだけ置く**(コミットしない。`git status`に出るがpull専用cloneなので混入しない)。
3. **各プロンプトの冒頭でも明示**(編集禁止・指摘のみ・出力はMarkdown)。

## 4. AGENTS.md テンプレ(サーバーcloneのリポ直下に置く)

```markdown
# レビュー専用の掟(このリポでのあなたの役割)

あなたの役割は**コードレビューのみ**。以下を厳守:
- **ファイルの作成・編集・削除・gitコマンドによる状態変更を一切しない**。修正はすべて「提案」として報告に書く。
- テスト実行は読み取り相当として許可(pytest)。ただしネットワークを使うテストは実行しない。
- 出力は日本語のMarkdown。指摘は次の形式:
  `[重大度: 即死級/本選前必修/本選後] [確度: 高/中/低] file:line — 何が起きるか(具体的な入力/状態→誤動作)→修正案`
- 重大度の定義: 即死級=10日ラン(25万体)が停止/破損する・本選前必修=結果の正しさや保存則を破る・本選後=品質改善。
- **憶測で「バグ」と断じない**。呼び出し元・conf既定値・テストの機械固定を確認してから確度を付ける。

## このリポの不変量(違反を見つけたら最優先で報告)
- R1: 新機能は既定OFF・既定OFFでgolden L1バイト一致・LLM呼数はk設定非依存・観測がシムを変えない・乱数は用途別named stream または blake2b安定ハッシュ(Python組込みhash禁止)。
- 保存則: 金銭・人数・車両はΣ整合(幽霊への書き込み=不在個体への状態変更は罪)。
- resume==straight: checkpoint復元後の走行は連続走行とバイト一致(プロセス内カウンタ族の宣言済み例外を除く)。
- 凍結14本(src/society/observer/{aggregate,measure,stream,echo,norms,silence,deviation,structure,initial_frame}.py・src/society/truth_ledger.py・scripts/{analyze_beliefs,analyze_norms,analyze_specialization,diagnose_stationarity}.py)への変更提案は自動的に[本選後]ラベル。
- conf/finals_observe.yaml が本選の実効ONセット。トグルの従属関係(fire→watch/engaged・fire→g_update等)の矛盾は必修級。
```

## 5. レビューパス6本(1回転目・優先順)

各パスは独立セッションで実行(コンテキスト汚染を避ける)。共通ヘッダを各プロンプト冒頭に付ける:

> 共通ヘッダ: 「AGENTS.mdを読み、掟に従うこと。あなたはレビュー専用。編集禁止。本番構成は conf/finals_observe.yaml(250,000体×1,440step=10日・Δt=10分)。指摘はAGENTS.mdの形式で、最後に重大度別サマリ表を付けること。」

| パス | プロンプト本文(共通ヘッダの後に) |
|---|---|
| **P1 決定論・R1** | src/ と scripts/run.py を対象に、決定論を破る経路を探せ: ①Python組込みhash/set反復順/dict順序依存が結果に混入する箇所 ②named streamを経由しない乱数 ③時刻・環境・パス等の実行環境が状態に漏れる箇所(no-fingerprint) ④並列度で結果が変わる箇所。テスト(tests/test_scenario.py=golden)がどこまで機械固定しているかも確認し、固定されていない穴を優先して報告せよ。 |
| **P2 保存則・会計** | src/society/economy*・ownership・wage・population を対象に、金銭と人数の保存則を破る経路を探せ: ①不在個体(dehydrate済み)への書き込み ②片側だけの計上(支払いはあるが受け手がいない/逆) ③回転(rot_in/rot_out)境界での量の消失 ④POP転出/転入/出生での口座・住戸・世帯の整合。既存の保存則テストが見ていない金流を優先せよ。 |
| **P3 resume/checkpoint** | src/society/checkpoint*・scheduler の回転搬送(dehydrate族)を対象に、resume==straight を破る経路を探せ: ①checkpointに保存されない可変状態 ②復元順序依存 ③resume後に0から始まるカウンタで動力学に影響するもの(観測のみなら宣言済みで可)④EMA・予約・不応期など時間窓を持つ状態の搬送漏れ。 |
| **P4 conf配線** | conf/finals_observe.yaml の実効ONセットを対象に: ①従属トグルの矛盾(親OFFで子ONのno-op・親ONで子の前提欠け)②基底confに宣言の無いキー ③250,000/1440/Δt10で破綻する定数(小規模想定の既定値のまま本選に入る値)④コメントアウト待機ブロック(cognition 3行・population 2行・v2切替)の解凍手順が安全か。 |
| **P5 性能O(N)地雷** | src/ を対象に、250,000体×1,440stepで顕在化する計算量を探せ: ①step内のO(N)走査がホットパスにあるもの(follower_count同型=逆引き索引で直せた前例あり)②無界成長するコレクション(Item.transmissions等は既知)③文字列連結・ログのO(N)④parquet書きのバッファリング。既知リスト(PENDING.md §4)との重複は除外し、新発見のみ報告せよ。 |
| **P6 観測非侵襲** | src/society/observer/ を対象に: ①observerがエンジン状態を書き換える経路(読むだけの契約)②観測ON/OFFで乱数消費・LLM呼数・最終状態が変わる経路 ③starvation/GTロガー/causalityの新kindがschemaとcausality両方に登録されているか(登録漏れ=logger.log()即死の前例あり)④finalize/flushの有界性。 |

## 6. 2回転目(穴埋め後)

1. **差分レビュー**: 「`git diff <β凍結タグ>..HEAD` の変更だけを対象に、1回転目と同じ掟・形式でレビューせよ。修正が新たな決定論違反・保存則違反を持ち込んでいないかを最優先」
2. **再確認**: 1回転目の指摘リスト(review/p1〜p6.mdを渡す)に対し「各指摘が修正済み/未修正/誤指摘だったかを判定せよ」

## 7. 実行コマンドと成果物の運用

```bash
mkdir -p ~/review && cd ~/projects/shibuya-simulation && git pull --ff-only
# 1回転目: 1パス=1セッション(コンテキスト独立)。tmux内で直列実行が安全
# ★0.147実測2点: バイナリは ~/.local/bin/codex。ssh/tmux等の非TTYから流すときは
#   stdinを閉じる(< /dev/null)こと=閉じないと「Reading additional input from stdin...」で停止する
codex exec --profile review -o ~/review/p1.md "<共通ヘッダ+P1プロンプト>" < /dev/null
#   … p2〜p6 も同様(-o で最終レポートをファイル保存)
# 2回転目(穴埋め差分): β凍結時に付けたタグ/ブランチをベースに
codex review --base <β凍結タグ> > ~/review/round2-diff.md
```
- 成果物はサーバー側 `~/review/`(**clone外**)に保存=clone内に書かせない。
- **回収**: scp または貼り戻し → 私(Fable)が重大度×確度で triage → 修正はOpusレーン → 検収=フルゲート → 2回転目へ。
- **Codexの指摘を鵜呑みにしない**: triage で「誤指摘」判定も普通にある(凍結ファイル・意図的仕様・宣言済み限界)。判断は台帳(PENDING §4 持ち越し小粒・宣言済み限界)と突合してから。
