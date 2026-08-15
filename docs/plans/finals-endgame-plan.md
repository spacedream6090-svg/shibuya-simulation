# 本選エンドゲーム計画 — 検証∥β凍結 → Codexレビュー×2 → 本番 → 提出

> 2026-08-16作成。ユーザーのシナリオ(①現状をリモートで検証 ②並行で残実装を終わらせβ版 ③Codexレビュー→穴埋め→再レビュー ④通れば本番開始 ⑤Discord定期報告 ⑥提出物作成)を、日程・残作業の棚卸し・判断項目に落とした正典。
> 参照: [runbook-first-night.md](../../ops/runbook-first-night.md)(今夜の一本道)・[setup-gpu-sv-002.md](../../ops/setup-gpu-sv-002.md)(環境構築)・[decision-dashboard.md](decision-dashboard.md)(D1〜D8)・[codex-review-pack.md](../../ops/codex-review-pack.md)(レビュー実行キット)。

---

## 1. 日程(逆算・提出8/30固定)

**律速は本番ランの壁時計**: 25万×10日の外挿は T10=72〜164h(中間セル139.7h≈**5.8日**)。実測(Phase 1)で引き直すまでは中間セルで計画する。→ **本番開始は8/22推奨・遅くとも8/23**(8/23開始+140hで8/29朝完走=提出前日)。

| 日 | やること | 判定・成果物 |
|---|---|---|
| **8/16(今日)** | サーバー検証 Phase 0〜2(2k計測→10k初ラン)・環境インベントリ(§3)・Codexセットアップ(§5)・v2プール生成を仕込む | **R_eff / c / RSS の初実測**(±50%誤差の外挿が実数になる) |
| **8/17** | スケール階段 50k×1日・実測ゲート群(fire呼数・POP per_day・resume呼数差・犯罪V1/V2)・v2縦煙48step | fire GO/NO-GO・POP ON・A2 ON・v2切替の判定材料が揃う |
| **8/18** | **β凍結**(残実装の投入締切=§2のカット)・100k×1日(v2で)・**Codexレビュー1回転目**(6パス) | βタグ・レビュー指摘リスト |
| **8/19** | 指摘の穴埋め+検収(フルゲート)・**250kリハーサル開始(1〜2日)** | T10確定値・修正コミット |
| **8/20** | **Codexレビュー2回転目**(穴埋め差分+再指摘確認)・信頼性リハーサル7本・watchdog本選値化 | レビュー通過・リハ完走 |
| **8/21** | 最終判定反映(conf確定)・**U-10事前登録承認**(私から依頼)・予備 | 本番conf凍結 |
| **8/22** | **本番 250k×10日 開始**(遅くとも8/23)・Discord報告開始 | ハートビート/日次ダイジェスト稼働 |
| 〜8/27-28 | 本番走行(watchdog+報告)・提出物の下書き並行 | 完走→backup(--ckpt-generations 999) |
| 8/28-29 | 尾部: seed2本目短縮ラン(D2)・解析・ビューア生成 | rollup・calibrate_report・図表 |
| **8/30** | **提出** | 最終提出物 |

遅延時の縮退線: 250kリハが2日ずれたら本番を**8日ラン**に縮めるのではなく**開始日を優先**(10日という長さがU-10事前登録の前提)。それも無理なら U-10 閾値表の再承認とセットで日数変更。

## 2. β凍結線 — 残実装の棚卸しとカット提案

事実: **機能実装はほぼ完了している**。残りは (i) 小粒コード (ii) 実測ゲート待ちのconfスイッチ (iii) 実測タスク (iv) 本選後送りの確認、の4種で、(i)だけが「実装」。

### (i) βに入れる小粒コード(8/18凍結までに)
| # | 項目 | 規模 | 備考 |
|---|---|---|---|
| β1 | **D1-c#4b**: fire ON時の計画繰り越し×周期発火先送りの対処(`note_plan_due`を初回予約stepに絞る1行 or `max_defer_steps`縮小) | 小 | fire GOの場合の前提条件。既定OFFで無風=先に入れておける |
| β2 | watchdog閾値・backup世代数の**本選値化**(既定20/5GBは小規模想定) | conf+小 | 信頼性リハ7本とセット |
| β3 | **J1共在ペア上限 8→24**(conf 1行・L1 +2〜3GB・動力学不変の機械検収付き) | conf | U13完全接触ネットワークの分母。**承認待ち→§7-6** |
| β4 | **初期関係較正**(13日蒸発の修正・conf数値のみだが挙動変化) | conf | **承認待ち→§7-5**。v2切替と同時に縦煙で確認が効率的 |
| β5 | sleep_task_rewrite の**実LLM検収**(GPU到着で初めて可能になった)→良ければON・時間切れならOFFのまま | 検収のみ | 就寝前テンプレの言い換え。落ちてもOFF維持でリスクゼロ |

### (ii) 実測ゲート待ちのconfスイッチ(実装済み・数字が出たらON)
fire 3行(D1-b: T10≤140h∧増分≤+15%)・POP転出/転入2行(per_day vs 現実7.8/8.4件日)・PRES-A2 1行(RSS/R_eff)・v2プール1行(縦煙緑)・policy_cache(resume呼数差)・**engine.batch_llm(workers 8・Phase 1のON/OFF短A/B後→§7-13)**。**判定は数字を貼ってもらえれば私が即返す。**

### (iii) 実測タスク(サーバー・8/16-17)
R_eff/c(Phase 1-2)・144step RSS・fire呼数(mock可)・犯罪V1/V2(--allow-real-llm)・resume呼数差・σ再実測・attach_record本番コスト・row_group_rows実L1再調整。

### (iv) 本選後送り(βに入れない・確認)
DPH-A(起床→就寝地平)・LSR-B/H(「家に入る=寝る」分離)・build_friend_graph Chung-Lu化・所有権O2/O5・店主行為化・PoA・SoA配線・メタバース射影F0-F4・chance.pyコード削除・beliefs `--bin-steps`(CLI上書きの運用回避で足りる)・PPv2-G(workplace_scope/at_home engine接続)。

## 3. 本番環境の詳細把握(メモリ等)

### 3.1 インベントリ(サーバーで1ペースト・出力を貼り戻してください)
```bash
{ echo "=== os ==="; lsb_release -d; uname -r; date; \
  echo "=== cpu ==="; nproc; lscpu | grep -E "Model name|Socket|NUMA"; \
  echo "=== mem ==="; free -h; swapon --show; \
  echo "=== disk ==="; df -h / /home /tmp 2>/dev/null; \
  echo "=== gpu ==="; nvidia-smi --query-gpu=index,name,memory.total,driver_version --format=csv; \
  echo "=== limits ==="; ulimit -n; ulimit -u; \
  echo "=== tools ==="; python3 -V; git --version; tmux -V 2>&1; \
  echo "=== egress ==="; for h in huggingface.co discord.com github.com; do \
    printf "%s: %s\n" "$h" "$(curl -sI --max-time 5 https://$h -o /dev/null -w '%{http_code}' || echo NG)"; done; }
```
この出力で決まるもの: **RAMが需要見積り(§3.2)を満たすか・swap有無(OOM時の挙動)・ディスクが本番ラン+バックアップに足りるか・fdリミット(vLLM7本+parquet書き)・egress(HF重みDL/Discord投稿)**。

### 3.2 需要側の見積り(既存文書の集約・実測で置き換える)

| 資源 | 250k×10日の見積り | 確定させる実測 |
|---|---|---|
| **RAM** | **★矛盾する2本の外挿が併存**: **88〜110GB**(1万体24step実測の傾き0.362MB/体)vs **316〜363GB**(1,000体のみの傾き1.265MB/体)。PRES-A2 ONならさらに**+72GB**。10日の蓄積(relations/episodes)は上乗せ | §3.1の実RAM容量+**10,000体×144stepのpeak RSS**(24stepでは不足と文書明記)→どちらの傾きが正か確定=present_cap/A2判断の決定量 |
| ディスク(run本体) | **約67〜70GB**(L1 42.7GB+channels 2.8+journal 4+checkpoint他+GTサイドカー+3.4GB)。L1は**超線形の下界**(1,622 events/体/日@1万体) | 10kランの実run-dirサイズで傾き引き直し |
| ディスク(累積) | checkpoint 20世代=**20〜100GB級**(E0剪定禁止)+watchdog 3世代→**総計50〜150GB級**+退避先 | checkpoint 1個の実サイズ・保存実時間(未実測) |
| 壁時計 | T10=72〜164h(§1・全セル±50%誤差の外挿) | R_eff・c(Phase 1) |
| VRAM | qwen3:8b **AWQ-INT4=重み17.1GB+KV 4-5GB≈21-22/24GB**=A5000 1枚に収まる側(bf16は不可側)。prefix cache文献値hit~96% | 起動後nvidia-smi+`vllm bench serve` |

★見積り上の注意3点:
1. **RAMが最大の未知数**。悲観傾きが正なら250k単ノードはRAM不成立級(~316GB)→present_cap縮小の判断になる。インベントリの`free -h`と10k×144step実測を最優先する理由。
2. **`engine.batch_llm` が本選confに無い=OFF=計画呼が完全直列**(dayplan-horizon-plan.md:424)。Day-1判断ではON(workers 8)が推奨で、決定論は workers 1 vs 4 の state_hash 一致で証明済み。**T10を直接左右する**ため Phase 1 で ON/OFF を短時間A/B→ON判断(→§7-13)。
3. `reflect_max_tokens` 2048→**768**推奨(実測p95≈247tok・vLLMはmax_tokens分のKVスロットを予約=下げると同時実行が増える)・watchdog `--stall-min`(既定20分)を25万の1 step実時間(~10分想定)に合わせ再設定——どちらもβ2「本選値化」に同梱。

### 3.3 未実測(Phase 1-2が埋める)
`c`(エンジン秒/体/step)・`R_eff`(呼/秒)・250k時RSS・fire増分・resume呼数差・vLLM実効スループット(prefix cache込み)。

## 4. ペルソナ再生成 = v2プール切替(新規生成は不要)

- **結論: 「ペルソナの再生成」はv2プールへの切替として実装済み**(第116)。Kimi K3等のLLM生成は第115リサーチで**多様性崩壊を実証済み**のため不採用が確定している(台帳駆動の一次統計方式が正)。
- 残手順(すべて用意済み): ①サーバーで `python scripts/build_persona_pool.py --seed 42 --v2 --childcare --out data/persona_pool_v2` ②tier_quota再計算 ③縦煙48step ④conf待機ブロックの1行切替。
- **推奨タイミング: 8/17に①〜③、8/18の100k階段からv2で走る**(切替が早いほど後続の検証が本番構成で積み上がる)。
- 初期関係はプールからラン初期化時に構築される(30,000人で約25分=許容・250k化はChung-Lu案で本選後)。**β4の較正修正を同時に入れて縦煙1回で両方確認**が効率的。

## 5. Codexレビュー体制(セッティング)

- **実行場所=gpu-sv-002(Ubuntu)を推奨**。理由: ①ローカルPCにはnode/npmが無い(確認済み)②サーバーのcloneは**追跡ファイルのみ=h.txt・runs/・data/が物理的に存在しない**=情報衛生が構造的に良い ③Linuxが最もサポートが厚い。
- **レビュー専用の強制**: sandbox読み取り専用+「編集禁止・報告のみ」をAGENTS.md/プロンプト両方で明文化(→[codex-review-pack.md](../../ops/codex-review-pack.md))。
- **規模**: 本体約144k行(src 74k+scripts 62k+viz 8k)+tests 85k行。1セッション一括は不可能なので**系統別パス**に分割する。
- **2回転の設計**: 1回転目=6パス(§5.1)・2回転目=穴埋め差分+1回転目指摘の再確認。
- **現行仕様の要点**(2026-08時点・手順と出典はpack側): インストール=Node不要の公式インストーラ/認証=ChatGPTアカウント(Free/Go/Plus/Pro/Business同梱)かAPIキー・ヘッドレスは`codex login --device-auth`が公式/非対話レビュー=`codex exec --sandbox read-only -o out.md "…"`/差分レビュー=`codex review --base <タグ>`/AGENTS.mdはリポ直下を自動読込。**★個人プランは既定でコンテンツが学習に使われうる=Data Controlsのオプトアウト確認をレビュー前に必ず**(Business系は既定除外・APIキー課金も学習不使用)。

### 5.1 レビューパス構成(1回転目・優先順)
| パス | 対象 | 見るもの |
|---|---|---|
| P1 | 決定論・R1(乱数stream/blake2b/golden/no-fingerprint) | seed非依存の混入・乱数の順序依存 |
| P2 | 保存則・会計(economy/ownership/wage/POP) | 金と人数のΣ整合・幽霊書き込み |
| P3 | resume/checkpoint/回転搬送(dehydrate族) | 状態消失・resume==straightの破れ |
| P4 | conf配線(既定OFF・finals_observe実効・トグル従属関係) | ONセットの整合・宣言漏れ |
| P5 | 性能O(N)地雷(250k×10日で顕在化する計算量) | ループ内O(N)・無界成長 |
| P6 | 観測非侵襲(observer/starvation/GTロガー) | 観測がシムを変える経路 |

## 6. Discord報告(実装済み・残は手動2点)

`scripts/report_progress.py`(--dry-run検収済み)。残: ①**webhook URLの環境変数設定**(ユーザー作業・`SHIBUYA_DISCORD_WEBHOOK`・URLはチャット/リポ/CLI引数に書かない)②サーバーからのdiscord.com:443疎通(§3.1に同梱)。初回は必ず--dry-run→本番投稿。

## 7. 判断事項一覧(ユーザーが決める・推奨つき)

| # | 事項 | 選択肢と推奨 | 期限 |
|---|---|---|---|
| 1 | **β凍結線**: §2(i)のβ1〜β5を入れて8/18凍結 | **推奨=承認**(β3/β4は下の個別判断) | 8/17 |
| 2 | **Codex認証方式** | (a) ChatGPTアカウント(お持ちのプランで可・**個人プランなら学習オプトアウトOFF確認が前提**) (b) APIキー(API課金・学習不使用が既定)。手順=pack§2 | 8/17(1回転目前) |
| 3 | **Codexレビュー範囲** | **推奨=§5.1の6パス×2回転**(全量精読は物量的に不可能・系統別が最実効) | 8/17 |
| 4 | **v2プール切替** | **推奨=YES**(縦煙緑が条件・8/18の100k階段から) | 8/17-18 |
| 5 | **初期関係較正修正**(β4) | **推奨=入れる**(conf数値のみ・13日で初期関係が蒸発する較正ズレの修正・縦煙で確認) | 8/17 |
| 6 | **J1共在 8→24**(β3) | **推奨=入れる**(L1 +2〜3GB・動力学不変は機械検収済み) | 8/17 |
| 7 | **fire GO/NO-GO** | 基準は決定済み(D1=b案)。**Phase 1の数字が出たら私が判定を返す**→GOなら3行解凍の最終承認 | 実測後 |
| 8 | **D2尾部の使途** | **推奨=(a) seed2本目最優先**+現実再現ラン=同構成seed違いで兼用 | 8/20頃 |
| 9 | **本番開始日** | **推奨=8/22**(遅くとも8/23。§1の逆算) | 8/21 |
| 10 | **U-10事前登録** | 本番開始直前に私から承認依頼(お約束どおり) | 8/21-22 |
| 11 | 提出物の構成 | ハッカソン要項の提出要件(形式・分量・データ添付可否)を確認して共有してほしい→逆算して8/28-29に組む | 8/25頃 |
| 12 | 賃金残り2点(最賃集積・家賃窓) | **推奨=現状維持**(記録済み・異論あれば再検討) | 任意 |
| 13 | **engine.batch_llm を本選confへ**(workers 8) | **推奨=ON**(計画呼が現状完全直列=T10直撃・決定論はstate_hash一致で証明済み・Phase 1でA/B実測してから) | 8/17 |

## 8. 手動作業一覧(ユーザーにしかできないもの)

| # | 作業 | 手順の所在 |
|---|---|---|
| M1 | VPN接続+サーバーでのペースト実行(§3.1インベントリ・runbook Phase 0〜2) | [setup-gpu-sv-002.md](../../ops/setup-gpu-sv-002.md)・[runbook-first-night.md](../../ops/runbook-first-night.md) |
| M2 | **codex login**(認証・トークンをチャットに貼らない) | [codex-review-pack.md](../../ops/codex-review-pack.md) §2 |
| M3 | **Discord webhook URLのenv設定**(`SHIBUYA_DISCORD_WEBHOOK`) | [finals-compute-checklist.md](../../ops/finals-compute-checklist.md) §E2 |
| M4 | 数字の貼り戻し(R_eff・c・RSS・per_day・呼数差) → 私が判定即返し | 本文§2(ii) |
