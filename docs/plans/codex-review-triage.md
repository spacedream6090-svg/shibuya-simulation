# Codexレビュー全6パス — 裏取り済みトリアージ(2026-08-16)

> 入力: gpt-5.6-sol によるレビュー6パス(P1決定論/P2保存則/P3resume/P4conf/P5性能/P6観測)。
> 裏取り: 読み取り専用の検証エージェント3本+手動検証で全指摘をコード突合。
> **結果: 誤指摘(REFUTED)は0件。ただし約1/4は規模・重大度の割引(NUANCE)が必要。**
> 併走の自前計測: prof10k6(cProfile 10k×6step)= 物理ゾーンが実行時間の74%と確定。

## 0. 結論(推奨)

8/18凍結(仮)までに **即死級10件+必修の軽量13件** をレーン5本並列で消化する。
本選後送り14件は理由付きで見送り。物理ゾーン痩身と cap 値は mock10k144 完走
(RSS勾配)と合わせて別途判断=決定ダッシュボード D 系へ追記。

## 1. 即死級(本選開始不可級)— 裏取り結果

| # | 指摘 | 出典 | 裏取り | 対処 | 工数 |
|---|---|---|---|---|---|
| A1 | `agent_by_id` が実体化済み全個体(累計45.9万)をフルAgentで強参照・departed を半日ごと pickle | P4/P6 | **CONFIRMED・最重要**。scheduler.py:5669-5675 で退場者を消さない設計コメントあり。RSS外挿が「在場250k」でなく「累計459k」に比例するなら 320GB→588GB で NO-GO 確定級 | 退場者は name 等最小 `AgentRef` へ分離。※mock10k144 の RSS 勾配で「1.28MB/体が累計込みか」を先に切り分け | 中 |
| A2 | `dormant_cap=50000` の LRU 退避が money/口座/債権ごと状態を破棄=真の消失+再入場時に初期残高を再鋳造 | P2/P4 | **CONFIRMED・Codexより悪い**。pool.py:132-137。economy_sfc に rot_in/rot_out の語が1件も無い=回転境界の金銭は完全未カバー。日境界の city_total は O(10^10)円 跳ぶ | 金銭・債権・賃金累積を容量非依存の軽量台帳へ分離(LRUはリッチ状態のみ)+回転境界のSFC両建て | 大 |
| A3 | 資産レンズ Kendall τ が純Python二重ループ=25万体で日境界312億比較 | P5/P6 | **CONFIRMED**。finals で `lens.assets.enabled: true`。★P6の「凍結だからconf OFFのみ」は誤り — observer/assets.py は凍結14本の対象外 | マージソート反転数で O(N log N) 化+現行実装との完全一致テスト(レンズは殺さない) | 小-中 |
| A4 | 購入ごとに `occupancy()` が25万体全走査=O(BN) | P5 | **CONFIRMED・やや過小**(VC審査レーンも同関数)。副発見: `stock_threshold: 6` は25万体でほぼ常時品切れ判定=較正問題が同居 | node→在場覚醒人数の逆引き索引(follower_count 同型・同値性テスト)。stock_threshold は別途較正判断 | 小-中 |
| A5 | `posts_max=0`(無制限)で投稿/likes/news 無界+checkpoint が sim.net 丸ごと pickle | P5 | **CONFIRMED・範囲はさらに広い**(follows/read_marks も生涯46万キー)。推薦全ソート指摘(P5)は過大だが「途中入場20.9万人の初回閲覧が全履歴走査」は実在し、posts_max 有限化で両方同時に切れる | posts_max 有限化(id不変+offset補正は test_scale.py が固定済み)+read_marks 初期値を末尾に | 小 |
| A6 | checkpoint の COMPLETE マーカーが pool sidecar/L1 flush より前=窓内停止で「欠落世代を完成扱い」 | P3 | **CONFIRMED**。保存順序をコードで確定。pool sidecar 欠落時は警告なく素通り(dormant全消失) | 全成果物確定後に COMPLETE 作成+sidecar欠落を不完全世代として前世代へ戻す+障害注入テスト | 中 |
| A7 | 同名 run dir へ `--resume` なし再実行で旧 part 混入・旧 llm_cache 再生 | P1 | **CONFIRMED**(中断ラン後の再実行=resume付け忘れの典型状況で発生) | fresh 起動は出力先非空なら拒否(逃し弁フラグ付き) | 小 |
| A8 | 正準コマンドが backend=mock のまま=β6ガードで RuntimeError | P4 | **NUANCE**: うるさく落ちる設計どおり(t=0で気づける)。ただし規律としては正 | freeze_config.py で vLLM ブロック合流済み解決confを1枚正典化(β9と合流) | 小 |
| A9 | provenance `transmissions` 無界+`len()` がプロンプト/記憶へ流入=観測でなくエンジン状態 | P6 | **CONFIRMED**。1億件で~12GB+checkpoint時間単調増。len がプロンプトに入るため有界化は累積カウンタで値を保存 | 明細は追記型サイドカーへ、メモリは累積カウンタ(len と同値)のみ | 中 |
| A10 | 物理ゾーン(SFM/ORCA)の超線形=10k で実行時間の74% | 自前(prof10k6) | **CONFIRMED**。_accumulate 等ペア計算。2k→10k で step単価13倍 | mock10k144 完走後に痩身案(近傍cap/セル法/サブステップ)を別途提示=D系判断 | 中-大 |

## 2. 本選前必修(軽量・確実に直す)

| # | 指摘 | 出典 | 裏取り | 対処 | 工数 |
|---|---|---|---|---|---|
| B1 | LLM 障害応答(`__vllm_error__` 等)がキャッシュ永続化・同一promptに再生 | P1 | CONFIRMED(書き込み条件に応答検査ゼロ) | エラー接頭辞は cache 書き込み除外 | 小 |
| B2 | `start_date=auto` が起動日をラン内世界へ固定(generated 天候の較正は8月限定) | P1 | CONFIRMED(意図的挙動・ラン内決定論は無事。confからの再現不能が実害) | 本選 launcher で明示日付必須化(8月内なら較正内) | 小 |
| B3 | `_goods_stock`/`_goods_pending` checkpoint 未搬送=resume で棚が満杯へ復活(卸 _b2b は保存済み=非対称) | P3 | CONFIRMED(既存テストは inventory OFF で不発) | 両dictをruntime搬送+分割走行比較テスト | 小-中 |
| B4 | city_ops `_co_state` 未搬送=救急上限・夜間清掃が resume で二重発火 | P3 | CONFIRMED(第98のAST全数監査は dict内キーを拾えず漏れ) | `_co_state` を runtime 搬送+夜帯跨ぎ resume テスト | 小 |
| B5 | `_boredom` 搬送が恒久 no-op(`_bore_node` 未搬送→初回tickで0クリア) | P3 | CONFIRMED(straight/resume 両側が同じに壊れる=一致テストで原理的に検出不能) | 初回分岐で既存 `_boredom` を保持し node のみ初期化 | 小 |
| B6 | 消費税が nominal 基準(実支払 actual と乖離)=受け手が負になり得る・行政が未払税を収受 | P2 | CONFIRMED(docstring「実支払基準」と実装が不一致。Σ=0なので既存テスト通過) | 税を actual から計算・`0<=tax<=actual` テスト | 小 |
| B7 | 死者へ給与・利息・給付、死者から家賃・固定費(3フェーズが dead/outside 未除外) | P2 | CONFIRMED(機構確実・総額は小=数百 agent日。コホート分析と幽霊人件費が汚染) | 経済フェーズへ共通の生存資格述語 | 小 |
| B8 | 出生時に両親別世帯だと子が二重所属 | P2 | CONFIRMED(finals の friend_graph 較正で partner 成立が conf の但し書きより早い。件数は0〜数件) | 共通世帯でないペアを出生対象外に(最小修正) | 小 |
| B9 | starvation 観測が `agent._plan_expired_day` を書く=観測ON/OFFでcheckpointバイトが変わる | P6 | CONFIRMED(事実)/影響は checkpoint バイト差のみ・誰も読まない。R1文言違反として修正 | 重複排除を observer 側 dict へ | 小 |
| B10 | 縮小コマンドの `present_cap` 対指定漏れ(dashboard/runbook) | P4 | CONFIRMED(自前でも実地事故記録あり) | 全縮小コマンド修正+起動バナー両値一致の機械検査 | 小 |
| B11 | v2 煙試験 `--clean` が完成済みプールを上書きする罠 | P4 | CONFIRMED(手順) | 煙試験は別dir必須+切替前 meta/hash 起動ガード | 小 |
| B12 | 13b コメント「lead増ならmaxも増やせ」は二重加算(routine.py:822 が自動加算済み) | P4 | CONFIRMED | コメント修正のみ(max_awake_min は触らない) | 極小 |
| B13 | v2 実測コメントが meta.json 実値(L2 157,715/L4 774,303)と不一致 | P4 | CONFIRMED | 切替時に meta から再計算し conf コメント更新 | 極小 |

既知重複(別レーンで処理中): max_llm_per_step cap 再導出=β8(R_eff実測済み・mock10k144待ち)、g_update/fire 依存=D1判断待ち(confに正直な申告コメントあり・1160行の矛盾記述だけ直す)。

## 3. 本選後送り(理由付き)

| # | 指摘 | 理由 |
|---|---|---|
| C1 | `init_follows` O(N²) 起動時(250kで~73分) | 一回きり・起動が伸びるだけ。余力があれば O(Nk) 化(小工数)を凍結前に拾う価値あり |
| C2 | 資産 scalars 5列×5走査/step | 250kで~0.7s/step=総12-18分。許容 |
| C3 | aggregate 140列の同一provider再走査 | 凍結14本(SPEC_FILES)対象=不触 |
| C4 | aggregate 3-gram 巨大連結文字列 | 同上(凍結) |
| C5 | truth_ledger 無界+目撃者全走査 | 凍結。ただし A4 の stock_threshold 較正で stock_out 洪水を抑えると F が下がり間接緩和 |
| C6 | memory_daily 日次バースト(~8-9GB・60分内に解放) | RAM予算の~3%・持続短。RAM線判定に+9GBとして計上のみ |
| C7 | relations `_last` 無界(~4-7GB単調増)+resume時part展開 | RAM線判定に計上。10日ランでは許容、延長ランでは要修正 |
| C8 | 車両 rot_out 無し | NUANCE: A12のΣ残差0は成立(両立)。`live`=累計登記の語彙を docs に明記のみ |
| C9 | batch_decide stats checkpoint 未搬送 | finals は batch OFF(ONにする場合はβ8と同時に搬送追加) |
| C10 | 実vLLM workers 非決定性 | 既知・文書化済み。DT定義(観察ランは厳密再現を求めない)と整合 |
| C11 | test_dph の「コメントアウト固定」テスト | fire解凍判断が出た時に同時修正 |
| C12 | registry 検査が bool リーフのみ | 本選後に全リーフ schema 検査 |
| C13 | 転出入 ON 時の債務・lease 清算漏れ | 転出入は本選 OFF 継続前提(POP解凍判断が出たら A2 とセットで) |
| C14 | 休眠 housemate への離脱反映漏れ | 同上(emigration OFF) |
| C15 | L1 flush 一括Arrow化 | NUANCE: finals は flush6+streaming finalize で有界化済み=現存欠陥でない |

## 4. 実装レーン案(並列・各レーン=検収→フルゲート→コミット)

| レーン | 内容 | 規模 |
|---|---|---|
| R(RAM根治) | A1 AgentRef分離・A2 金銭台帳分離+SFC境界・(C6/C7はRAM線計上のみ) | 大 |
| P(性能) | A3 τ O(NlogN)・A4 逆引き索引・A5 posts_max有限化・(余力でC1) | 中 |
| C(checkpoint) | A6 COMPLETE順序・A7 run dirガード・B3 goods・B4 city_ops・B5 _bore_node | 中 |
| E(経済正しさ) | B6 消費税・B7 死者除外・B8 出生世帯・A9 provenance有界化・B9 starvation | 中 |
| D(conf/手順) | A8 freeze_config正典化・B1 cacheエラー除外・B2 日付固定・B10-B13・矛盾コメント | 小 |

共通検収: 既定挙動の golden L1 バイト一致(修正が既定ONの経路に触れる場合は同値性テストで機械固定)・resume==straight・フルゲート緑・スキャンCLEAN・凍結14本不触。

## 5. 保留(別判断・決定ダッシュボードへ)

- **物理ゾーン痩身の方式**(A10): mock10k144 の完走値(RSS勾配+Nスケール定数)を見て提案。
- **cap 値(β8)**: R_eff実測(艦隊12-18 calls/s)+エンジン実測で T10 表を引き直して提示。
- **stock_threshold 較正**(A4副発見): 25万体での品切れ判定基準の再設計。
