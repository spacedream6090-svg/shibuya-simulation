# PENDING — 未実装・実装中・ユーザー判断待ち

> 本ファイルは **まだ終わっていないもの**だけを持つ。完了済みは → **[IMPLEMENTED.md](IMPLEMENTED.md)**(決定の履歴も同所の年表と git log が正典)。
> 索引と最終更新は → **[STATUS.md](STATUS.md)**。
> 最終更新: **2026-08-08**(第101=wave4 6レーン完結: 持ち越し小粒の「今できる分」を掃討・§4 は各見出しに ※解消済み注記。**PUB-U1=公開ミラー同期完了**=実装中レーンから除去)。

---

## 1. 実装中レーン(承認済み・リサーチ→実装の順)

| レーン | 内容 | 状態 |
|---|---|---|
| **RW-U1 運用** | フェッチャー実装**完了**+**タスクスケジューラ稼働中**(2026-08-07・`shibuya-rw-fetch-daily` 毎日12:00・PC電源オフ時は次回起動で追走・ログ `data/realworld/_scheduler.log`・アメダス 7/28〜8/6 回収済み)。残=①8/12 頃の規約再確認(R3)②本選中は `--report` の欠け監視を時々目視③本選後の解除は `Unregister-ScheduledTask` | **稼働中** |
| P4 残り | D(ボトルネック J/w 水準)の原因切り分け(接触項不在/τ/v0分布/定常部)・高密度の壁貫通脱出(接触項 or v_max クリップ再設計) | 未着手(フリーズ前は任意・§4 参照) |

## 2. 提案書(作成中・提示済み)

| 項目 | 状態 |
|---|---|
| **DP-U2 提案書**(心モデル) | **暫定決定=案C**(2026-08-07 ユーザー: 小型同居で多様性6種×冗長性を両立。提案書では**未検証**マークの構成)→ **8/15 診断ランに「vLLM 同居性能の実測」を必須追加し、厳しければ案Bへ**(退路は conf 1箇所)。D層 n=30 は280呼=8/15午後に同居可。残=候補7本のライセンス/VRAM一次確認(8/12まで) |
| **DP-U3 提案書**(観察ラン25万) | **決定=本線10日ラン25万(現実同等規模)**(2026-08-07 ユーザー「現実の渋谷の再現が目的なのでここは削れない」)。前提3点が必須化: ①層別クォータ=**実装済み**(小粒G 2026-08-07・R-1=(a)で決着)②解析25万対応(§1 wave2)③R_eff/144step RSS 実測(8/15-16)。週末28%は R-3(b)=正直記載を既定線。★ON では resident も比率で切られる=コホート/k* 追跡系への影響確認は 8/15-16 |
| 観察ラン ON 構成(旧提案) | [observe-run-config-proposal.md](docs/plans/observe-run-config-proposal.md) 提示済み → **DP-U3 改訂版で置換予定**。OBS-U1〜U3 の判断は改訂版で |
| DT スナップショット再提案 | [dt-snapshot-integration-proposal.md](docs/plans/dt-snapshot-integration-proposal.md) 提示済み → DT-S1 ほか判断待ち |
| S-quick(S0/S1/S2/S5/S9) | 計 ≈1.8日。承認待ち(入力来歴・observe.yaml 是正・バス表・実イベント表・ODD 文書) |
| **アクターモデル移行** | [actor-model-migration-plan.md](docs/plans/actor-model-migration-plan.md)(2026-08-09 承認・並列実装開始)。**Wave 1 完了(第102)**: P0+P1 因果台帳・P2 デバイス土台(改札+SignalGate identity)・P5 前工程(−11%/step)・P3b 前提(work_node 被覆)。**Wave 2 候補**: P4 境界スキーマ(day_plan 圏外セグメント+パルス流入)・P3a 駅員車掌(ダイヤ結合)・P1×デバイス統合(transit_delay 再分類・車両/歩行者信号の統一)・P5 本体(SoA)設計。残 OPEN: chance_event 再分類/PoA 位置づけ/§4.5 保留 |

## 3. ユーザー判断待ち(残りのみ)

| # | 事項 | 状態 |
|---|---|---|
| **U-10** | 事前登録の閾値承認+10日ラン解釈方針。**承認対象が2点増えた**: 前文「主張の境界」+§3-F stylized facts(分散比の閾値・F1 の θ 数値化は §7 未決事項) | 8/15-16 診断ラン前に承認依頼(10日ラン 8/16 開始前・タイミング委任済み) |
| OBS-U1/U3 | 観察ラン ON セットの承認・認知 ON の 8/14 留保(OBS-U2=Δt は準備実装へ移行済み) | DP-U3 改訂提案書とセットで判断 |
| **policy_cache 保存判断** | 小粒A(2026-08-07)発見: LLM 決定のウォームキャッシュ(`cognition/policy_cache.py`)が checkpoint 未保存=resume で空になり**同じ骨格でも呼数と行動が変わりうる**。保存自体は容易だが「キャッシュは再構築可能」という設計思想との整合と L1 一致検証の設計が要る | 新規・本選前(推奨=8/15-16 診断で resume 前後の呼数差を実測してから) |
| beliefs の `--bin-steps` 既定24 | 唯一残った Δt 直書き(Δt=1 では 4時間窓が24分になる。CLI 上書きで回避可)。W3-1 の承認範囲(I/O のみ)外だったため意図的未着手。直すなら**8/15 のハッシュ凍結前**(もう1回だけハッシュが動く) | 小・任意(推奨=Δt=1 で beliefs を使う予定が立った時点で) |
| NEW-5 | F/N/P 初期値条件の本選配分 | パイロット後に提案 |
| **bind_workplace を観察ランで ON にするか** | 第102実測: 現実的占有(1,482人)で非スタッフ serve 84%→66%。ON なら `rebind_bound: true` 同伴が正(org 帰属の意味論)。**副作用=spend/economy 統計が激変**(通勤者が増え serve 1259→301)=ON/OFF 跨ぎの比較は不可。nightlife/cafe は org 台帳に職場カテゴリが無く構造的に無人(build_orgs.py 側の課題) | 新規(第102)・OBS-U1/U3 とセットで判断 |
| **pool 経路の `agent.org_id` 付与** | `build_pool_agent` が台帳 entry の org_id を読まない=pool ランでは serve.org_id が永久 null(**IF-E2 org 帰属の真のブロッカー**)。ただし org_id は career 解雇/転職・org_output・org 台帳にも波及=影響半径が広く独立判断が要る | 新規(第102)・P3b 本体前に要決定 |
| **chance_event の因果再分類** | 指示書§5.1 では exogenous=自然のみ。windfall/loss=境界フロー(RoW)・encounter=出会いへの再分類が素直だが挙動変更を伴う。現行は分類表で暫定 boundary+注記 | アクター移行計画 OPEN#5 |
| DT-U2 | UE5 デモ動画 | 保留のまま(本選中判断) |

### 決定済み(履歴の要点のみ・詳細は git log と IMPLEMENTED 年表)
2026-08-07: **DP-U2=暫定案C**(小型同居・8/15 に vLLM 同居性能を実測し厳しければ案B)/**DP-U3=本線25万**(現実同等規模「ここは削れない」)/**3D-U0=実装**(小粒F完了)/**SV-05=③**(診断後決定・既定線=集団定性パターン限定)/**DP-U4=呼数**/**B3=換算しない**/**RW-U1=承認**(リサーチ先行・無料優先・自律実装は委任・手動は最小)。
2026-08-07(夜): **凍結3本まとめて修正=承認**(beliefs/norms/specialization・判定式ゼロタッチをASTで機械証明・W3-1実施済み。**8/15 凍結の正ハッシュ= `79a2e549486fe6ab5eea350334cbe37b4c712c12dbf75e41afea617939010d0f`**・以後 8/15 まで凍結14本は再び不触)/**RW運用=タスクスケジューラ**(`shibuya-rw-fetch-daily` 毎日12:00・StartWhenAvailable・登録済み=State Ready)。
2026-08-06: **IF-E2=案B**(org 会計主体化+RoW 概念実装)/**DP-U1=無償**(CEJC 契約せず名大会話コーパス無償統計で C 層=実装は既にこの前提)/**SV 残13項目=採用**/**PUB-U1=Fable 案で決定**/OBS-U2=Δt1分の準備指示。
2026-08-05: IF-U1 実装承認→IF-A〜E 完了・SV-U1 ◎5件完了・P4-1〜3 完了。
2026-08-02: P2選定=ゾーン別ハイブリッド(委任決定)・高精細3D=松案承認。
2026-07-31 以前: NEW-1〜4・ID-U1〜U3・DT-U1/U3/U4 等(旧台帳 git 履歴参照)。

## 4. 持ち越し小粒(未解決のみ)

- **σ_c の Δt 再測**(Δt=1 では salience が系統的に過小・8/15-16 に統合)
- **IF-E2 残**: ①**窃盗の加害者への入金**(SNA では被害者−/加害者+の再分配だが本シムは受け取り側を K5 に置いたまま=挙動変化を伴うので独立トグルが要る・将来判断)②屋台の内税/床クリップギャップ(RoW が埋める=改名して隠さない)③b2b 買い手特定=`(node,POI種別)` 一意率 4.5%=本番規模では大半が「域外資本の店」(RoW)扱い(正直開示済み)※K5 の日次 L1 は第101で解消(`row_flow` に累積 `k5_total`)
- **resume 整合の残り(最終)**(第101で spark 二重記録・レンズ4本・worldview 走査+★flush 欠陥まで解消済み): ①`undefined_action_total/rate` はプロセス内カウンタ族(llm_health 3列と同族)=watermark 族の再設計なしに一貫不能・resume 後は 0 から数え直す旨を checkpoint.py に明記 ②凍結 `silence.py` の docstring 6行が旧記述のまま(state は保存されるようになった)=**次に承認されるハッシュ変更があれば2行同梱**(それだけのためにハッシュは動かさない)③`lens.assets` の `asset_rank_tau` は conf 明記どおり非搭載
- **IF-C 残課題**: ①Item.transmissions 上限なし(25万ではホット噂 O(N)=正典を L1 に置く再設計は別バッチ)②語り選択順(`max_per_talk=1`+「古い順」が同 step 伝播の律速=ポートフォリオ選択順は別課題)※誕生遅れ・混線切り分け・pool dehydrate は解消済み
- **P4 残課題**: ①D=J/w 水準不足の未解明(残候補=接触項不在/τ/v0分布/定常部)②高密度 ρ≥2 の壁貫通脱出(接触項 or v_max クリップ再設計・FD 高密度点は汚染込みでしか測れない)③6変数同時最適化未実施 ④ρ_meas 1.5 頭打ち=判定B合格は弱い証拠
- **物理見積の残り**: ①理論モードの既定2つ(`traversals-per-agent-day 2.0`/`zone-share 0.5`)に根拠なし=OD 表で埋める(ただし第101で較正ラン `runs/zone_smoke_p99` が誕生し**実測外挿モードで迂回可能**に)②混雑で dwell が伸びる効果は未計上=見積は下限側 ※max_sub_steps の Δt 追随は第101で解消(Δt=10=厳密12000)
- **3D 残り**: tracks.json の O(n_steps×n_agents) は出力そのもの(真の解=既存 `--tracks-binary --no-tracks-json`)・10日ラン規模の実 RSS 絶対値は未測(構造上は O(row group+1 step) 化済み)
- **層別クォータの照合**(小粒G): 提案書 §1.2 の割当は計算値=8/12 の縦煙で `present_for_day` を1回実走して照合(±1人ずれは最大剰余法が正・提案書 §6-5 訂正済み)
- **解析25万の残り(最終)**(第101で live_viewer 有界化・研究解析 19/19 移行・サイドカー finalize 横展開まで完了): ①`analyze_accounting` の events/flows は O(金額イベント数) 残存(`flows_for` の `id(payload)` 呼び出し規約の変更が要る=検査式に触れる別バッチ)②自前 loader の残り5本(`analyze_layers`/`analyze_mas_failures`/`analyze_org_form`/`analyze_persona_consistency`/`analyze_plan_execution`)+`analyze_firing.load_g`(cognition_g 全読み)=同じ型で機械的に続行可 ③`row_group_rows` 既定 2^20 は本番前に実 L1 の行バイトで再調整(全ファイル共有・個別チューニングは新キー要=意図的見送り)④W4-E の申告2点=ON は part 間スキーマずれを permissive 統一(OFF は例外・較正固定が前提)・indoor_tracks ON はディスク +19GB を容量計画へ(OFF 経路の concat ピークは**約124GB=L1超え**なので大きい3本の ON 実効性は L1 と同格)
- **Δt の残り(最終)**(第101で make_viewer(JS21式含む)・manifest dt_min・σ_c 来歴照合まで完了=**C級は全て完了**): ①L1 からの Δt 推定=第3の源(pyarrow 依存で見送り)②旧ラン 173/178 本が dt_min 無し=assumed 経路で stderr 1行(仕様=黙って仮定しない)③src 観測定数(measure.py `ECHO_WINDOW_STEPS=144` 等=凍結・8/15 以降の判断)
- **W4-F の設計上の残**: `street` ブロックは habit 委譲のため帰属不能が仕様(解くには「street の実体」の別判断)・`work_node` はスナップショット(B4 OFF+orgs ON のランは初期値のまま=受理集合を本業∪バイトの和にして緩和済み)※観測強化3点自体は第101で解消
- **D16 屋内 ON**・**D17 実験**・**4系統レーン2**(B-L1 以降)
- **竹-4 残**: ④span_m グラフ長 vs 物理直線の実効速度差 ⑥サブステップ軌跡の記録・`planning.py` 契約化は残置第一候補(※③ `_phys_body` 搬送と⑦事前見積は 2026-08-07 解消・ゾーン所有は「その旅に固有の状態」として意図的非搬送=根拠コード内明記)

## 5. 設計制約と受領文書(背景・不変)

### 5.1 設計制約(R1 ドクトリン)
恒常制約: ①新機能は既定 OFF ②既定 OFF で golden L1 バイト一致 ③k 非依存 ④no-fingerprint ⑤用途別乱数 stream ⑥観測がシムを変えない。
観察ラン(本選10日)は再現性を厳密に求めず repro_tier=journal/none も投入可・検証ラン(verify)は strict のみ(第72で構造化済み)。

### 5.2 受領文書(原文は docs/plans/source/ に保存済み)
二重化指示書3本・認知/物理/DT定義3本・設計議論まとめ(2026-08-02)・サーベイ PDF(原本リポ外・読解=[llm-social-sim-survey.md](docs/research/llm-social-sim-survey.md))。
統合計画の正典: [dual-mode-observe-verify-plan.md](docs/plans/dual-mode-observe-verify-plan.md)・[cognition-physics-plan.md](docs/plans/cognition-physics-plan.md)・[dayplan-engaged-plan.md](docs/plans/dayplan-engaged-plan.md)・[highfidelity-3d-physics-plan.md](docs/plans/highfidelity-3d-physics-plan.md)・[if-sv-p4-plan.md](docs/plans/if-sv-p4-plan.md)。

### 5.3 日程
**本選 8/15–8/30**(提出 8/30)・**10日ラン 8/16–8/26**・**8/12-14 フリーズ**(新機能追加禁止=検証と微調整のみ)・**8/15-16 診断ラン**(σ 再実測 → θ 再較正 → U-10 確定判定 → 人数最終確定・**vLLM 同居性能実測=DP-U2 案C判定**・**R_eff/144step RSS 実測=DP-U3 25万**・SV-05 seed 効果量・policy_cache resume 呼数差)。GPU=A5000 級 ×7枚(単一ノード)。

### 5.4 本選後(レーン3)
場所二層知覚(IDEA⑥)・誤情報構造化フル版(ID-U2)・SUMO 反実仮想(P5)・USD/3D Tiles(DT-U4)・UE5(DT-U2)・org 会計主体化の拡張(倒産・信用線)・詳細順位は [dt-integration-plan.md](docs/plans/dt-integration-plan.md) §3。
