# PENDING — 未実装・実装中・ユーザー判断待ち

> 本ファイルは **まだ終わっていないもの**だけを持つ。完了済みは → **[IMPLEMENTED.md](IMPLEMENTED.md)**(決定の履歴も同所の年表と git log が正典)。
> 索引と最終更新は → **[STATUS.md](STATUS.md)**。
> 最終更新: **2026-08-12**(第108=Day 3 リビルド+ONセット候補+縦煙・クォータ照合=差ゼロ解消・★縦煙発見=org_id/bind_workplace が本選ブロッカーへ昇格+resume 全ON構成の+106行。計画2本提示=犯罪×LLM検証・所有権レイヤー)。

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
| **アクターモデル移行** | [actor-model-migration-plan.md](docs/plans/actor-model-migration-plan.md)(2026-08-09 承認)。**Wave 1〜3 完了(第102〜104)**: 因果台帳・デバイス・性能−11%・境界計画・駅員車掌・device_id(-1 行の 94.5% 回収)・SoA 基盤・パルス流入・境界較正データ。**工学系の残(本選後)**: SoA 配線(乱数キー判断が前提)・店主行為化(serve org_id 判断が前提)・GTFS 実発車時刻・PoA 観測。残 OPEN: chance_event 再分類/PoA/§4.5 |
| **Wave 4=現実被覆** | [wave4-reality-coverage-plan.md](docs/plans/wave4-reality-coverage-plan.md)。**α+β+Day 3完了(第105〜108)**: Day 3=台帳v8リビルド(9,872社・夜勤34.1%)+プール100万(L2夜勤11.21%・org_id 100%)+**ONセット候補 `conf/finals_observe.yaml`**(231機能ON・chance退役・weather=generated=WBGT実働)+縦煙(mock 48step×2窓・例外0・新機能L1発火確認)+**層別クォータ照合=差ゼロで完了**。残判断=縦煙発見4件(§3) |
| **犯罪×LLM検証** | [crime-llm-verification-plan.md](docs/plans/crime-llm-verification-plan.md) **提示済み(2026-08-12・リサーチ=crime-llm-cognition.md)**。結論=本シムの犯罪はLLM不通過(構造派=犯罪学ABM主流と一致)・向社会バイアスは実証あり・**検閲なしモデルは本選前非推奨**。V0(mockハーネス)=いつでも可・V1選択率/V2被害者反応=8/15-16診断日にGPU同居実測。**実装未着手=承認待ち** |
| **所有権レイヤー** | [ownership-layer-plan.md](docs/plans/ownership-layer-plan.md) **提示済み(2026-08-12・リサーチ=ownership-asset-models.md)**。タグ案の核心は正・推奨=**タグ付きレコードを登記簿に置くハイブリッド**(lost_propertyの一般化)+権利行RRR(own先行)+**資産保存則**(貨幣保存の双対)+階層LoD(不動産全個体/家財世帯集計/消耗品フロー)。スライスO1〜O5・**実装=本選後が本線・承認待ち**(OPEN3: 住戸初期所有者=RoW推奨/相続=O1同時推奨/スライス順) |
| **身体と事件レイヤー** | [body-incident-layer-plan.md](docs/plans/body-incident-layer-plan.md)。**2026-08-11 ユーザー4決定(計画書§6に原文)→ H1〜H5+H2 全6レーン実装完了(第107)**=全て既定OFF。残: ①**chance の運用退役**=本選 ON セット conf で `chance.enabled: false`(機能代替=H3拾得+H4盗難が完備。コード削除は golden 再生成を伴うため本選後)②残課題は §4「身体と事件の残」 |

## 3. ユーザー判断待ち(残りのみ)

| # | 事項 | 状態 |
|---|---|---|
| **U-10** | 事前登録の閾値承認+10日ラン解釈方針。**承認対象が2点増えた**: 前文「主張の境界」+§3-F stylized facts(分散比の閾値・F1 の θ 数値化は §7 未決事項) | 8/15-16 診断ラン前に承認依頼(10日ラン 8/16 開始前・タイミング委任済み) |
| OBS-U1/U3 | 観察ラン ON セットの承認・認知 ON の 8/14 留保(OBS-U2=Δt は準備実装へ移行済み) | DP-U3 改訂提案書とセットで判断 |
| **policy_cache 保存判断** | 小粒A(2026-08-07)発見: LLM 決定のウォームキャッシュ(`cognition/policy_cache.py`)が checkpoint 未保存=resume で空になり**同じ骨格でも呼数と行動が変わりうる**。保存自体は容易だが「キャッシュは再構築可能」という設計思想との整合と L1 一致検証の設計が要る | 新規・本選前(推奨=8/15-16 診断で resume 前後の呼数差を実測してから) |
| beliefs の `--bin-steps` 既定24 | 唯一残った Δt 直書き(Δt=1 では 4時間窓が24分になる。CLI 上書きで回避可)。W3-1 の承認範囲(I/O のみ)外だったため意図的未着手。直すなら**8/15 のハッシュ凍結前**(もう1回だけハッシュが動く) | 小・任意(推奨=Δt=1 で beliefs を使う予定が立った時点で) |
| NEW-5 | F/N/P 初期値条件の本選配分 | パイロット後に提案 |
| **★bind_workplace+pool org_id(縦煙で昇格=本選ランのブロッカー)** | 第108縦煙の実測: pool ランでは `organizations.attach` が**0件**(personas_file 前提)→ 870体中 org_id 付与 0・org_accounting n_orgs=3。さらに**客引き(ユーザー明示要件)が構造的に沈黙**(`_is_tout` は nightlife POI 勤務者を選ぶが pool の work_node は手続き生成=客引き帯に持ち場に居ない)。第102からの判断待ち2件(bind_workplace=serve 84%→66%・spend統計激変 / pool org_id=career・org_output波及)が「あれば良い」から「**本選ランで org 系観測と客引きが実効化するかを決める前提**」へ昇格。8/15 前に要決定 | **昇格(第108)** |
| **resume の +106行(全ON構成・第108縦煙発見)** | `finals_observe` 相当の全ONで straight(48) と resume(24+24) の L1 が不一致(11,945 vs 12,051行=+0.89%)。主因= `joint_activity +97`・`friend_graph_built +1` が**起動時1回の発火体の再実行で step0 イベントを同一 payload で二重発火**(+viral_cascade 3/misinfo 2/row_flow 1/signal_summary 1/state_update 1)。relations+friend_graph+joint+party+pool の同時ONが初構成のため第98/101の resume 全数監査の網外。観察ランは厳密再現性を要求しない(DT定義)が、10日ランは resume 前提=**修正推奨(フリーズのバグ修正枠・chance 二重発火=第98 と同族の直し方)** | 新規(第108)・修正承認待ち |
| ~~chance_event の因果再分類~~ | **決着(2026-08-11・第107)**: ユーザー原理「運は世界のアルゴリズムでなく人の行動から」→ windfall=H3拾得・loss=H3遺失+H4盗難被害・encounter=既存共在で機能代替完備。運用退役=本選 ON セットで `chance.enabled: false`・**コード削除は本選後**(golden 保護) | 決着 |
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
- ~~層別クォータの照合~~ **解消(第108)**: 本番プール100万に present_for_day 実走=5層すべて計算値と**差ゼロ**(平日 day0・cap 250,000 ちょうど・週末は資格者<cap で全員在場・OFF では第91の来街者ゼロを再現)
- **第108縦煙の小粒**: ①`build_persona_pool` が出力ディレクトリを掃除しない(L2 縮小で stale shard 残留=meta.shards 経由の実行は無害・glob 消費者には罠。今回は手動削除)②`incidents_env.FIRE_OCCS=("消防士",)`・`GUARD_OCCS` が src ハードコード=消防士は名簿に0(pool ランで恒久 unstaffed)→ conf 化 or 名簿追加の判断 ③設備対応者: 「設備保守員」「警備員」とも名簿0・新台帳は「設備巡回3,944/常駐警備3,875」(L2夜勤ロール)を生やした→ ONセット conf に `world.facilities.responder_occupations` 4語彙の行を提案済み(night_cleaning と同型・承認は ONセット承認に同梱)④`work.serve_by_cat` に service が無い(conf 1行で 1,972社が接客対象化=挙動変更なので未投入・census doc §7.1 の seam)⑤新5モジュール+street_life/city_ops/transit_* の summary provenance 未配線=縦煙の判定コストを上げる(L1 kind 経由でしか見えない)
- **解析25万の残り(最終)**(第101で live_viewer 有界化・研究解析 19/19 移行・サイドカー finalize 横展開まで完了): ①`analyze_accounting` の events/flows は O(金額イベント数) 残存(`flows_for` の `id(payload)` 呼び出し規約の変更が要る=検査式に触れる別バッチ)②自前 loader の残り5本(`analyze_layers`/`analyze_mas_failures`/`analyze_org_form`/`analyze_persona_consistency`/`analyze_plan_execution`)+`analyze_firing.load_g`(cognition_g 全読み)=同じ型で機械的に続行可 ③`row_group_rows` 既定 2^20 は本番前に実 L1 の行バイトで再調整(全ファイル共有・個別チューニングは新キー要=意図的見送り)④W4-E の申告2点=ON は part 間スキーマずれを permissive 統一(OFF は例外・較正固定が前提)・indoor_tracks ON はディスク +19GB を容量計画へ(OFF 経路の concat ピークは**約124GB=L1超え**なので大きい3本の ON 実効性は L1 と同格)
- **Δt の残り(最終)**(第101で make_viewer(JS21式含む)・manifest dt_min・σ_c 来歴照合まで完了=**C級は全て完了**): ①L1 からの Δt 推定=第3の源(pyarrow 依存で見送り)②旧ラン 173/178 本が dt_min 無し=assumed 経路で stderr 1行(仕様=黙って仮定しない)③src 観測定数(measure.py `ECHO_WINDOW_STEPS=144` 等=凍結・8/15 以降の判断)
- **W4-F の設計上の残**: `street` ブロックは habit 委譲のため帰属不能が仕様(解くには「street の実体」の別判断)・`work_node` はスナップショット(B4 OFF+orgs ON のランは初期値のまま=受理集合を本業∪バイトの和にして緩和済み)※観測強化3点自体は第101で解消
- **身体と事件の残(第107・全て既定OFFのため本選前は無風)**: 【H1】①熱中症チャネルは `weather.mode: generated|table` が前提(既定 synthetic は wbgt 欠測=不活性・conf 明記済み)②通報遅延分布(46/29/25%)は Δt=10 で同一 tick に丸まる=payload 観測のみ③死亡は発症時決定=治療→転帰の条件付けは未実装(H1 の設計判断・再開封は別バッチ)④city_ops OFF では S3/S4 に物理的「倒れる」表現なし(sick 在宅と同型・明記済み)【H2】①プール回転 dehydrate に `med_*`(在院の印)非搭載②医療機関 org 特定率=小ラン 0%・本番台帳で再測要③高額療養費・年齢別負担割合(未就学2割/75+1割)・病床数制約は未実装④H5 の負傷者は搬送しない(搬送=collapse 経路限定)⑤S2 自力受診は移動を作らない(会計帰属のみ)【H3】①analyze_accounting の部門フロー分類に lost_return/keep/expire 未追加=監視装置が設計どおり列挙する状態(家計内移転+主体なしバケツの会計設計判断が要る)②落下ハザードは1人1step 1draw=25万 ON 時は stride 化検討③resolve 順序による1step遅れ(IF-C 第98 と同型)④落し物は知覚に出ない(拾得=決定論判定)【H4】①ペア確率の合成は和近似(較正値では誤差無視可・大きな上書きで飽和=weight_sum で観測)②プール退場で酩酊マーカー喪失(rumors と同じ制約)③警察官を現場へ動かさない(response_min=モデル値)④detain_steps 既定0=勾留 seam 不踏(発火権が動くため)【H5】①traffic.hazard_per_exposure の本番規模再較正(背景交通は step 末在庫を持たない設計=係数が標本規模を吸収)②延焼なし(重度分布較正と二重になるため)③群集 incident は physics.zones ON のランのみ④「設備保守員」は L5 名簿に不在=名簿再生成まで警備員が担う【共通】新5モジュールの provenance() は summary 未配線(city_ops と同status)
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
