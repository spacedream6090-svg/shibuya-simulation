# β実装計画 — 監査採用分(β1〜β11)を今日昼までに終わらせる段取り

> 2026-08-16作成。ユーザー方針: **サーバー接続・検証が最優先/追加実装は今日昼まで/監査(GPT-5.6 Sol)洗い出し分はおそらく全部組み込める/スモークはサーバー側で**。
> 本書は実装レーンの発注仕様(Opus実行役向け)。採否の根拠は [external-audit-triage.md](external-audit-triage.md)・全体日程は [finals-endgame-plan.md](finals-endgame-plan.md)。
> **不変の規律**: 全て既定OFF・golden L1バイト一致・新乱数はnamed stream/blake2b・観測がシムを変えない・凍結14本不触・chance.py不触・h.txt不触・コミットはFableのみ。

## 0. レーン全景(3並列+観測側1)

| レーン | 中身 | 規模 | 昼までの現実性 |
|---|---|---|---|
| **B1 安全系** | β6 mock fail-fast+凍結conf/β7 checkpoint stream/β10 モデル凍結manifest/β11 request seed | 小×4 | 高 |
| **B2 HOME_AWAKE最小** | β9(帰宅≠就寝) | 中 | 最小スコープ厳守なら可 |
| **B3 小粒束** | β1 fire#4b/β2 watchdog本選値化/β3 J1 24/β4 初期関係較正/used-cap観測列 | 小×5 | 高 |
| **B4 観測側**(昼縛りなし・動力学ゼロ) | V1 reality_score v1+A11(Vintage/Crosswalk)/V2 invariants/coverage・fairness指標 | 中 | 夕方まで |

検収の型: 各レーン自前pytest→**Fableが静止木フルゲート**(ローカル or サーバー→§5)→スキャン→明示パスstaging→コミット→push→**サーバーpull**。

## 1. B1 安全系(2〜3時間)

### β6 mock fail-fast+完全解決済みconf
- `scripts/run.py`(or engine起動部): `run.n_agents>=10000 かつ model.backend=="mock" かつ not run.allow_mock_production → RuntimeError`。既定`allow_mock_production: false`を基底confに宣言(未宣言トグル再発防止テストの作法)。
- 起動時バナー: backend/servers/model/pool dir/present_cap/max_llm_per_step を必ずstdoutへ。
- `scripts/freeze_config.py`(新規・小): profile+dotlistを完全解決して`conf/finals_YYYYMMDD_frozen.yaml`+sha256を出力(OmegaConf.to_yaml)。**生成物はコミットしない**(本番直前に生成)。
- テスト: mock大規模でraise/フラグで通る/バナー内容/凍結confが再解決と一致。

### β7 checkpoint stream書き
- [checkpoint.py:535-539](../../src/society/engine/checkpoint.py): `raw=pickle.dumps(blob)`→`with gzip.open(tmp,"wb") as f: pickle.dump(blob,f,protocol=HIGHEST)`(共有参照は1回のシリアライズ=dumpでも同一)。書き後`f.flush()+os.fsync`→既存の原子rename維持→**`COMPLETE`マーカー**(空ファイル or manifest末尾)→resumeは最新COMPLETEのみ読む。
- テスト: save/load往復同一・COMPLETE無しcheckpointをresumeが飛ばす・(可能なら)保存時RSS増分の前後比較を記録。

### β10 モデル・サンプリング凍結(ops+コード小)
- `ops/launch-vllm-finals.ps1`: `--generation-config vllm`追加・モデルはHF revision付き表記(第一候補Qwen3-8B-AWQ)・sampling全明示の注記。
- run_manifest(G1)拡張: model名/revision/vLLM version/sampling params(temperature/top_p/top_k/max_tokens/seed方針)を記録。バックエンドから取れない値は「起動側申告」欄として書く(捏造しない)。

### β11 request-level stable seed
- [vllm.py](../../src/society/llm/vllm.py): リクエストへ`seed = blake2b(run_seed, agent_id, step, purpose, ordinal) & 0x7fffffff`を付与。`llm.request_seed.enabled`既定OFF・finals ON予定。journalへseedを記録。
- テスト: 同一キー→同一seed・OFFで送出ボディ不変(バイト同一)。

## 2. B2 HOME_AWAKE最小(β9・4〜6時間・スコープ厳守)

**やること(これだけ)**:
1. 状態分離: `enter_building{home}`→即`sleep_start`の経路に**就寝ハザード**を挟む: `p_sleep = sigmoid(b0 + b1*circadian + b2*fatigue + b3*翌日早出 − b4*在宅活動中)`(全て既存stateで組む・新しい生理状態は足さない)。
2. 在宅活動ラベル(ルールベース・LLM呼ゼロ): meal/bath/housework/family_talk/media/hobby/study/rest の8種を年齢×職業×時刻の重み表(社会生活基本調査ベース・出典コメント)から抽選。既存named stream不可→**新stream "home_awake"**。
3. L1記録: 新kindは足さず既存`activity`系kindのpayloadで表せるなら流用。**新kindが必要な場合はschema+causalityの2箇所登録**(第115の即死教訓)+登録網羅テスト。
4. 世帯シナジー(最小): 同居人が在宅覚醒中なら family_talk 重み↑(household.context_line流用)。共同意思決定は入れない(本選後)。
5. conf: `daily.home_awake.enabled` 既定false・finals ONは縦煙後。

**やらないこと**(スコープ外を明記): hunger/sleep_pressure新設・LLM呼の追加・microthought・家計連動・DPH-A(起床地平)・reply意味論変更。

**検収**: OFFでgolden バイト一致・ONで(a)帰宅→就寝gapの分布が非ゼロ(60体×3日mockで実測値を記録)(b)21時在宅覚醒率>0(c)呼数OFF/ON完全一致(d)resume==straight。**較正目標**: 在宅覚醒 実4:24/日に対しmockで1:30〜5:00帯に入れば可(精密較正はV1レーンで)。

## 3. B3 小粒束(2〜3時間)

| # | 内容 | 要点 |
|---|---|---|
| β1 | fire#4b: `note_plan_due`を初回予約stepのみに(`plan_due_step`参照の1行)or `max_defer_steps`縮小 | fire OFFで無風=先に入れる。D1-c表の⬜を✅へ |
| β2 | watchdog/backup本選値化 | `--stall-min`を25万1step実時間連動(引数化)・ディスク閾値50GB・`--ckpt-generations 999`を既定側へ・**confは触らずCLI/ops側** |
| β3 | J1: `transit_interior.copresence.max_pairs_per_day: 8→24` | finals confのみ・動力学不変の機械検収(既存テスト)を回す |
| β4 | 初期関係較正(13日蒸発): decay/初期値のconf数値修正 | [initial-relations-improvement.md](../research/initial-relations-improvement.md)のR2推奨値・縦煙で確認(v2縦煙と同便) |
| obs | DPH-O拡張: summaryに`llm_budget.used_per_step`(mean/p95)と`used/cap` | 観測のみ・OFF/ONで世界不変テスト |

**着地(2026-08-15・レーンB3)**: 5 件とも完了。

| # | 何をしたか | 検収 |
|---|---|---|
| β1 | `fire._at_first_reservation` 新設 → `note_plan_due` と `_social_via` が **初回予約 step だけ**を拾う(内省も同じ穴を持っていたので同時に是正)。tiers OFF では両属性が誰にも生えない = 既定不変 | `tests/test_fire.py` +4(修正前のコードだと 2 本が `['plan','plan','plan']` で落ちる)・fire 全 53 緑・golden 緑。D1-c #4b の ⬜ → ✅ |
| β2 | `watchdog.stall_seconds`(純関数)+ `--stall-step-sec` / `--stall-factor`。**既定値は 1 つも変えず**、本選値はヘルプと [ops/finals-compute-checklist.md](../../ops/finals-compute-checklist.md) **E3** に明記(停滞=1step実測×6・ディスク 50/20・`--ckpt-generations 999`) | `tests/test_watchdog.py` +4(既定 20 分のまま)・全 21 緑 |
| β3 | J1 = **第114 で着地済み**と判明(本選 conf は既に 24・理由コメントつき)。再走のみ | `test_daily_cap_only_changes_the_copresence_rows` / `..._is_binding_and_conserves_the_pair_total` / `test_finals_conf_raises_the_daily_cap` 3 緑。PENDING §3 の J1 行を消化へ |
| β4 | `friends.py` に層別 margin(既定 None = 従来と同一)+ 本選 conf のみ R2 推奨値。実測は [initial-relations-improvement.md](../research/initial-relations-improvement.md) 冒頭の追記 | `tests/test_friends.py` +4・全 9 緑・golden 緑 |
| β1' | **追加発注**(β1 の未解決 #2 を採用): DPH-B の繰り越し予約 staleness。`health._exit_world`(死亡)/ `population._leave_world`(転出)が `plan_step` を落としながら `plan_due_step` を残していたため、同じ実体が次に予約を受けた日に `_defer_first` が何日も前の step を返し **初回から `max_defer_steps` 超過扱い = LLM 計画を撃たずに骨格へ落ちる**。両者に「印が立っているときだけ畳む」1 行を追加(**tiers OFF では属性が生えないので分岐が閉じる = 1 ビットも書かない**)。★内省側 `reflect_due_step` は対象外(これらは `reflect_step` を落とさないので予約は生きたままドレインされる = 宙に浮かない) | `tests/test_dph.py` +3(死亡版 / 転出版 / **tiers OFF で属性を生やさない**)。反証: 修正前は 2 本が `plan_due_step` に古い step が残って落ちる。golden 緑 |
| β2' | **追加発注**(B1 の COMPLETE マーカー `<checkpoint>.complete` の申し送り): マーカーを**本体と運命を共にさせる**。① `backup_run.select_payload` が `_ckpt_gen_step` でマーカーを本体と同じ世代に束ねる(退避先で `checkpoint.latest` の「書きかけを掴まない」判定が効くようになる。世代を絞っても本体と一緒に行く/一緒に落ちる)。★`checkpoint_boundary` は従来の `_ckpt_step`(本体のみ)のままにした = **マーカーの mtime が part の締切を緩めない** ② `watchdog._rollback_one_generation` が本体と同時にマーカーも `corrupt/` へ隔離 ③ 同じ不変量として `_clear_run_state` もマーカーを消す(孤児マーカーを積まない) | `tests/test_backup_run.py` +5 / `tests/test_watchdog.py` +4。反証: 修正前は 5 本が落ちる。**マーカーの無い旧 checkpoint でも従来どおり**をテストで固定 |
| obs | `starvation.note_step_budget`(run_step 末で `used`/`cap` を 1 件積む)+ summary の `starvation.llm_budget`(`used_per_step.mean/p95` / `used_over_cap_mean` / `cap_per_step_mean` / `used_total`)。p95 は**ヒストグラム**で持つ = step 列を持たない | `tests/test_dph.py` +5(観測 ON/OFF で行動列・呼数・乱数・最終状態一致 / `used_total == llm_budget_granted_total`)・DPH 全 38 緑(resume==straight 込み) |

## 4. B4 観測側(昼縛りなし・動力学リスクゼロ)

- **V1 reality_score.py v1**: calibrate_report拡張。カテゴリ=人口/生活時間(2021社会生活基本調査)/移動(PT・jinryu)/メディア(**令和7年度版**)。指標=JSD/MAPE/KS・**成分表示必須**・calibration/holdout列・**Data Vintage Ledger**(`data/ground_truth/registry.yaml`・「社会生活基本調査2026は提出前に未公表=2021が正当」を明記)+**Spatial Support Crosswalk**(bbox/区/都の分母明記)。
- **V2 audit_world_invariants.py**: 既存テストの検査式を流用した事後スクリプト(位置/役職年齢/容量/幽霊金流/孤児世帯)。250kリハ後に実行する前提のO(イベント数)実装。
- **coverage/fairness**: L1(l1b_llm)からzero-call率/P50/P90/Gini/属性別coverageを出す解析関数(reality_scoreのCognition節)。

## 5. スモークテストのサーバー実行(質問への回答=できる・役割分担つき)

```bash
# サーバー側の検証ワンライナー(pull→ゲート→結果)
cd ~/projects/shibuya-simulation && git pull --ff-only && \
source ~/venvs/sim/bin/activate && ulimit -n 65535 && \
python -m pytest tests -q -n auto 2>&1 | tail -3
```
- **64論理CPUなのでフルゲートはローカル15分→推定3〜6分**。mock/スケールスモーク(2k/10k)もサーバーでそのまま可(runs/はgitignore=clone汚染なし)。
- **注意①(初回に必ず確認)**: golden L1バイト一致は「同一プラットフォーム」で作られている(開発=Windows)。**Linuxで初回フルゲートを回して全緑かを見る**——全緑ならサーバーを高速ゲート機として常用/floatまわりで数本赤なら「golden系はローカル正・サーバーはスケールスモーク専用」に切り分ける(赤の内容を貼ってくれれば私が判定)。
- **注意②**: 検収の正典とコミット権はローカル(Fable)のまま。サーバーは「pull→検証→数字報告」の実行場(Read-only deploy key=構造的にpush不能)。
- 運用形: 実装(ローカルOpus)→検収+コミット+push(Fable)→サーバーpull→ゲート+スモーク(tmux内)→結果貼り戻し。

## 6. 今日のクリティカルパス(昼まで実装・午後判定)

```
朝    : B1・B2・B3を3レーン並列発注/(ユーザー)サーバー接続→setup→Phase 0
昼まで: 3レーン着地→フルゲート(サーバー緑ならサーバーで)→コミット→push→サーバーpull
午後  : (ユーザー)Phase 1実測(R_eff/c/RSS・2k×144→10k×144)+fire呼数mock+batch_llm A/B
      → 数字貼り戻し→私が判定: cap値(β8)・fire・RAM線・POP・A2
夕方  : v2生成+tier_quota+縦煙(β4/β9のON確認を同便)→50k階段
明日  : 100k階段(v2)+Codexレビュー1回転目(前倒し可)→8/18動力学凍結は予定どおり
```

判定待ちで実装をブロックしない: β8(cap)とfire/POP/A2/v2のONは**conf行のみ**なので、昼までの実装群とは独立に午後差し込める。
