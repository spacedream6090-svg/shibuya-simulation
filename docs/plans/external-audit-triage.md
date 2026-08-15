# 外部監査のトリアージ — 全5本(第1ラウンド2本+第2ラウンド3本)

> 2026-08-16作成・同日第2ラウンド追記(§R1〜R6)。リポ直下の監査群を読了し、**全claimをリポ実物と突合**した上で、採否と日程への織り込みを決める文書。実装はまだ始めない(ユーザー指示)。
> 位置づけ: 監査2本は「上位計画」を自称するが、**正典は引き続き台帳3md+decision-dashboard+finals-endgame-plan**。本書はその正典への差分提案として監査を消化する。
> 結論(3行): **方向は概ね正しく、特に「呼数密度」と「帰宅=就寝」は本物の急所**。ただしE0系5件のうち2件は実装済み/大半済みで、正しいのは3件。採用は「壊れない系(小)+呼数cap再導出(conf・実測後)+HOME_AWAKE最小(要判断)+検証ハーネス(観測側)」に絞り、**本番開始8/22は動かさない**。

---

## 1. ファクトチェック(主要claim × リポ実物)

| # | 監査のclaim | 判定 | 根拠 |
|---|---|---|---|
| F1 | **LLM呼数は0.17回/人/日しかない** | **⭕ 現行finals confでは正しい**(★ただし監査の算式は偶然当たり) | 第115 DPH-B(`lod.budget.tiers` ON)で**計画・内省も総枠に入った**([finals_observe.yaml:1004-1019](../../conf/finals_observe.yaml))。250k×cap300=43,200呼/日=**0.173回/人/日**。lifeレーン30%=12,960呼/日 vs 計画+内省の需要≈47万/日=**LLM計画の被覆は数%・残りは骨格フォールバック**。60体検収ではcapが非拘束で見えなかった規模創発。**dashboardのT10表(738万呼)はDPH-B以前の前提=古い** |
| F2 | E0-1: `agent_by_id`が退場者のfull objectを保持 | **⭕ 設計事実**(意図的・注記明文化) | [simulation.py:1407-1409](../../src/society/engine/simulation.py#L1407)「これまで実体化した**全**個体の索引」。幽霊書き込みは第112甲で全数ガード済み=**正しさは守られている**。残る問題は**RAMのみ**(悲観外挿316GBの駆動因候補) |
| F3 | E0-2: checkpointの`pickle.dumps`全量バイト化=保存時RAMスパイク | **⭕ 実在** | [checkpoint.py:535](../../src/society/engine/checkpoint.py#L535)。streamへ直接`pickle.dump`する3行修正で消える(共有参照は1回のシリアライズなら`dump`でも保存される) |
| F4 | E0-3: checkpointが非原子的・log不整合 | **❌ 大半誤認** | 原子的rename実装済み([checkpoint.py:536-539](../../src/society/engine/checkpoint.py#L536))+watermark保存(第109)+resume==straightはsidecar含め機械検収済み(第113)。残る正しい指摘=**fsync無し**(電源断時のみ)と多ファイルCOMPLETEマーカー=小粒 |
| F5 | E0-4: profile単独実行でmockになり得る | **⭕ 実在** | [finals_observe.yaml:47-49](../../conf/finals_observe.yaml#L47)=基底backendはmock(縦煙用・意図的)。本選はCLI dotlistで差し替え運用=**打ち間違い1つで25万体mockラン**。fail-fastガード+完全解決済みconf 1枚は安い保険 |
| F6 | E0-5: batch_llm未配線=計画呼が完全直列 | **⭕ 既知**(endgame §7-13で判断待ちに載せ済み) | dayplan-horizon-plan.md:424・決定論はworkers 1vs4で証明済み |
| F7 | 帰宅=就寝100%固定 | **⭕ 既知の本物**(第115発見・LSR-B/Hとして本選後送りにしていた) | 在宅覚醒0分 vs 実4:24。監査2本が揃ってP0昇格を主張=**再判断に値する** |
| F8 | 初期friend graph O(N²)が危険 | **⭕ 既知**(30kで25分=現L1規模なら耐える・Chung-Lu案=本選後) | PENDING§2。初期関係はL1 30kのみに張るため250k即死ではない |
| F9 | 内省が夜固定 | **🔶 半分古い** | RFX-A(第116)で夜間シェア100%→44-52%・文脈=歩行最多を実装済み。監査のmicrothought(16-64tok層)は**新規**提案 |
| F10 | ODPT「今すぐ申請」・交通が未接地 | **❌ 誤認** | ODPTキー取得済み(env運用)・GTFS実発車1,810本/6路線は第114で実装済み |
| F11 | 状態の飾り検査(writer/reader監査)が必要 | **🔶 大半済み** | 第113認知棚卸し62属性突合・第112痩せ全数検査・因果台帳197kind分類が同型。未カバー=「reader無しstate」の系統grep=小粒 |
| F12 | 3D=PLATEAU未導入 | **🔶 半分誤認** | viewer3dはPLATEAU共存済み(X線トグル)。**2025年度版(V5・LOD2/道路LOD3/地下街LOD4.1)への更新**と建物パルケ化は新規提案 |

## 2. ★最重要の発見 — 呼数レジームの真実(監査との衝突が掘り当てたもの)

F1の帰結を正面から書く:

1. **現行finals confの認知密度は0.173回/人/日で、監査の批判はこの点で有効**。DPH-Bは「返事保証」を直したが、250kではlifeレーンが桁で不足し、**ほぼ全員の計画が骨格(LLMゼロ)に落ちる**。
2. ただし**処方箋は監査の新規機構(AdaptiveLLMBudgetController)ではない**。conf自身が「capはDP-U4の決定事項・R_eff実測後に決める」と明記済み([finals_observe.yaml:1000-1001](../../conf/finals_observe.yaml#L1000))=**実測→cap再導出はもともとの設計**。新スケジューラを本番5日前に書くのは最大のリスク。
3. cap再導出の早見表(R_eff悲観18.3呼/s・エンジン27.6〜52.2hに加算):

| cap/step | 総呼数(10日) | 回/人/日 | LLM時間 | **T10** |
|---:|---:|---:|---:|---:|
| 300(現行) | 43.2万 | 0.17 | 6.6h | 34〜59h |
| **1,500** | 216万 | **0.86** | 32.8h | **60〜85h** |
| **2,500** | 360万 | **1.44** | 54.6h | **82〜107h** |
| 5,000 | 720万 | 2.88 | 109h | 137〜162h(GO線140h際) |

→ **推奨帯=1,500〜2,500**(監査のTarget 1.0-1.5回/人/日帯と一致・GO線140hに大幅余裕・fire分の頭出しも残る)。Phase 1のR_eff実測後に確定し、**lane share(life 30%)も需要比で再配分**する。
4. **fireの見え方が変わる**: tiers ON下ではfireは総呼数を増やせない(cap内のgeneralレーン需要が増えるだけ)。つまり**fire ONの壁時計リスクはcapで有界**であり、D1判定の主眼は「呼数増分」から「レーン飢餓カウンタと行動品質」へ移る。dashboard D1-b表はcap再導出後に引き直す。

## 3. トリアージ表(監査の全主要提案 → 採否)

### 3.1 β採用候補(動力学に触れる=8/18凍結までに・全て既定OFF/conf)
| ID | 内容 | 規模 | 判定 |
|---|---|---|---|
| **β6** | E0-4: mock fail-fast(`n_agents≥10,000 ∧ backend==mock → raise`・`--allow-mock-production`逃し弁)+完全解決済み本番conf 1枚(`conf/finals_YYMMDD_frozen.yaml`)+起動時マニフェスト表示 | 小 | **推奨=採用** |
| **β7** | E0-2: checkpoint stream書き(dumps→dump直流し)+fsync+COMPLETEマーカー | 小 | **推奨=採用**(保存時間を前後実測) |
| **β8** | **DP-U4: cap再導出**(§2の表・R_eff実測後にconf値変更+lane share再配分) | conf | **推奨=採用**(新コードなし・もともとの予定) |
| **β9** | **HOME_AWAKE最小**: 帰宅→就寝を分離(就寝=ハザード化)+在宅行動ラベル(食事/入浴/メディア/家事/家族会話…をルールベース選択・**LLM呼数は増やさない**)・既定OFF | **中(1〜1.5日)** | **要ユーザー判断**(監査2本のP0筆頭・第115実測の実害・ただし凍結直前の中型変更) |

### 3.2 観測・解析側採用(動力学リスクゼロ=8/20まで並行可)
| ID | 内容 | 判定 |
|---|---|---|
| V1 | **reality_score.py v1**(6カテゴリのうちデータが手当て可能な4: 人口/生活時間(社会生活基本調査)/移動(PT・jinryu)/メディア(総務省)。JSD/MAPE等・**総合1点に潰さず成分表示**・calibration/holdout分離) | **推奨=採用**(提出物の柱・calibrate_report.pyの拡張) |
| V2 | audit_world_invariants.py(250kリハ後の全数整合検査: 位置/役職年齢/容量/幽霊金流…※大半は既存テストの流用) | 推奨=採用(小) |
| V3 | 決定モード印字(habit/rule/LLMをprovenanceへ)=既存causality/L1で大半可視・差分のみ | 小・任意 |

### 3.3 実測後判定(既存判断枠のまま)
fire(D1・§2-4の再解釈込み)・POP・A2・v2切替・policy_cache・batch_llm(§7-13)・**agent_by_id痩身化**(→10k×144のRSSと「実体化累計数」を突合し、88-110GB帯に収まるなら**触らない**。悲観側なら緊急最小=dehydrate時に重欄を落とす案を別途提示)。

### 3.4 尾部・デモ系(本番中〜8/28-29)
| 内容 | 判定 |
|---|---|
| **介入fork 1本**(checkpoint分岐・交通障害 or 空間介入=監査§34のC案。D2尾部の使途に追加) | 推奨=seed2短縮版と両取り |
| **Shadow高認知ラン**(代表5k・ほぼ全決定点LLM・低LODとの行動一致率=「呼数はいくらで足りるか」の実証) | 階段の隙間(8/20-21)か尾部で1本・推奨=やる |
| PLATEAU 2025(V5)の**viewer側のみ**(3D Tiles直読み・エンジン不触=R1構造安全) | 時間があれば(A5判断)。engine側建物レイヤは**本選後** |
| LLM行動バッテリ・ミニ版(日本語シナリオ×数百sample・艦隊の空き時間) | 任意(半日) |

### 3.5 本選後送り(価値は認める・14日枠では危険)
AdaptiveLLMBudgetController(runtime動的制御)・habit学習(Contextual Habit Memory)・hunger/sleep_pressure・microthought層・cognition debt/公平性・social attention capacity・reply4型(ignore/ack/short/full=DPH-B直後の意味論変更は危険)・group hyperedge・norm知覚分離・goal memory・行動蒸留・PLATEAU engine層・実フロアアーキタイプ・人為ミス層。**監査2本はこのレーンのロードマップとして正典化する**(本選後の最初の計画書に昇格)。

### 3.6 不採用・誤認訂正(§1のF4/F10/F12ほか)
checkpoint原子性の主要部・ODPT申請・交通未接地・「24万9950人が永遠にroutine」の表現(正: 骨格計画は全員毎日走る=ゼロLLM者の問題ではなく**LLM計画の被覆率**の問題)。

## 4. β凍結線の改訂(finals-endgame-plan §2への差分)

- β1〜β5(既存)+**β6・β7(推奨採用)**+**β8(実測後conf)**+**β9(要判断)**。
- 凍結規律: **動力学に触れるもの=8/18中に投入完了**(β9を採るなら8/17着手が条件)。観測側(V1/V2)は8/20まで延長可(R1構造上、ラン結果に影響しない)。**本番開始8/22は不変**。

## 5. 追加の判断事項(A系列・endgame §7の続番)

| # | 事項 | 推奨 | 期限 |
|---|---|---|---|
| A1 | **呼数cap再導出**(β8): 実測R_effで§2表を引き直し→cap 1,500〜2,500帯へ | **推奨=YES**(数字が出たら私が表を出す) | 実測後 |
| A2 | **HOME_AWAKE最小**(β9)をβに入れるか | 入れる価値は高い(監査2本一致・実害実測済み)が凍結直前の中型=**ユーザー判断**。入れるなら8/17着手 | **8/17朝** |
| A3 | E0系小粒(β6+β7)を入れるか | **推奨=YES**(安全のみ・挙動不変) | 8/17 |
| A4 | reality_score v1(V1)を作るか | **推奨=YES**(提出物の柱・観測側) | 8/17 |
| A5 | PLATEAU 2025 viewer側 | 時間次第(本番中の並行作業枠)・engine側はNO | 8/18 |
| A6 | 尾部の再配分: seed2短縮+介入fork1本(+shadow) | **推奨=この3点セット** | 8/20 |
| A7 | 監査2本の扱い: リポ直下に未コミットのまま置かれている。**root直下は公開ミラーの除外対象外**=コミットすると次回同期で公開される。**推奨=docs/plans/source/へ移してコミット**(ミラー除外域・受領文書の置き場) | 移動+コミット | 任意 |

## 6. 日程への影響(結論: 骨格は不変)

8/16(今夜〜): サーバー検証+Phase1実測(変わらず最優先)/ 8/17: A2-A4判断→β6-β9着手+v2縦煙 / 8/18: **動力学凍結**+レビュー1回転目 / 8/19-20: 穴埋め+250kリハ+V1/V2仕上げ / 8/21: conf確定(cap込み)+U-10 / **8/22: 本番開始**。監査採用分はこの骨格の中に収まる——収まらないものは全て§3.5へ送った。

---

# 第2ラウンド(2026-08-16・追加3本: SERVER_CAPACITY / FINAL_DESIGN_GAPS / RESOURCE_AWARE)

## R1. 状況 — 監査ループは収束した

- **RESOURCE_AWARE(3本目)は本トリアージのコミット`1297072`を基準HEADに執筆され、§80で当方の訂正をそのまま採択**: 0.173回/人/日が正・cap候補1,500〜2,500/step・「4.5〜5.5回/日」は本線前提にしない・reasoning増=忠実度増と仮定しない・大型behavior変更はβ凍結後にしない。
- SERVER_CAPACITY(1本目)の「4.5〜5.5回/日」「1シミュ日=18〜24h」は**3本目の§80で自己上書き済み=採用しない**。RAM判定線とR_effバンドは採用(→R2)。
- FINAL_DESIGN_GAPS(2本目)の統合仕様書要求は→A10。日程は3本とも当方と一致(**β凍結8/18・本番開始8/22**)=骨格変更なし。

## R2. 確定した新事実 — サーバー実機スペック(§3.1インベントリの回答)

| 項目 | 実測値 |
|---|---|
| CPU | 64 logical / 2 NUMA |
| RAM | **251 GiB**(available 242)+ swap 8 GiB |
| ディスク | /home 約3.7 TB空き |
| GPU | RTX A5000 24GB ×7(既知) |
| OS/Python | Ubuntu 22.04.5 / 3.10.12 |
| **ulimit -n** | **1024 ★本番不足**(vLLM7本+parquet+sockets)→ **65535へ**(runbookに追記) |

- **RAM判定線を採用**: 250k外挿peak RSSが **GO <180GiB / CONDITIONAL 180〜215 / NO-GO >220**。楽観外挿+A2(110+72=182GiB)はCONDITIONAL境界=**10k×144のRSS実測が引き続き最重要**(§3.2どおり)。
- 未取得の残り: `nvidia-smi topo -m`(NUMA偏り)・ディスク実throughput(checkpoint書きの停止時間)・**持続熱試験**(30〜60分連続推論でreq/sドリフト)・vLLM `/metrics`収集。→runbook 0-4へ追記済み。

## R3. 追加ファクトチェック

| # | claim | 判定 |
|---|---|---|
| F13 | RouterLLM実装済み+multi-model-lod計画あり=S1構成は主に艦隊conf変更 | **⭕確認**([router.py:38](../../src/society/llm/router.py#L38)・[multi-model-lod.md](multi-model-lod.md)) |
| F14 | VllmBackendはrequest seedを送っていない | **⭕確認**(vllm.pyに`seed`なし・vLLM SamplingParamsは受け付ける) |
| F15 | `--generation-config auto`既定=未指定サンプリングパラメータがモデル側defaultへ依存 | ⭕(vLLM現行仕様)→`--generation-config vllm`+全パラメータ明示(β10) |
| F16 | DPH-B: generalはreply/lifeの予約の余りを**借りられない**→capを上げてもused/cap<1がありうる | ⭕(設計どおり)→**used/cap実測を判定に追加**: ≥0.90維持/0.75〜0.90はlane share再配分/<0.75でreclaim検討 |
| F17 | 検証アンカーの年次更新が可能: メディア=令和7年度版公表済み(2026-06・平日183.9分)・家計調査2025年平均公表済み・社会生活基本調査2026は10月調査=**提出前に存在しない**(2021が正当な最新) | ⭕→V1レーンで年次更新+Data Vintage Ledgerに「2026未公表」を明記 |

## R4. 採否の更新(第2ラウンド分)

**β/ops追補(小・推奨採用)**:
- **β10 モデル・サンプリング完全凍結**: model repo/revision/quantization(第一候補=Qwen3-8B-AWQ 6.11GB・14B-AWQ 9.99GB)・tokenizer/chat_template SHA・vLLM版・sampling全明示+`--generation-config vllm`をmanifestへ(ops+起動スクリプト・G1マニフェストのモデル側拡張)
- **β11 request-level stable seed**: `rng_key`→`SamplingParams.seed`(数行・観察ランの再現性改善。bit決定論の保証ではなく乱数条件の明示・保存)
- **ops追補**(runbookへ反映済み): ulimit 65535・NUMAトポロジ取得・/metrics定期保存・持続熱試験・ディスクthroughput
- **判定指標追補**(解析側・V1へ同梱): used/cap・**zero-call率・calls/personのP50/P90/Gini・属性別coverage**(「平均だけでは25万人に届いたか分からない」は正しい)

**要判断(A8〜A11・endgame §7の続番)**:

| # | 事項 | 推奨 | 期限 |
|---|---|---|---|
| A8 | **モデル構成**: S0=7×8B維持 vs **S1=6×8B+1×14B**(reflect/deep→14B・RouterLLM既存) | まず**ミニ行動トーナメント**(8B vs 14B・数百シナリオ・半日・8/17-18のGPU隙間)→差が明確ならS1。32B/TP2は余力のみ | 8/18 |
| A9 | JSON Schema structured outputs(purpose別schema) | constrained decodingは出力分布を変えるため**A/B後**。差が小なら採用 | 8/18 |
| A10 | FINAL_DESIGN_SPEC(統合正典)を今書くか | **推奨=書かない**(8/18前の工数はゲート実測へ。完了チェックリスト§61/§76だけ採用し、統合スペックは本選後) | — |
| A11 | 検証アンカー年次更新+Data Vintage Ledger+Spatial Support Crosswalk | **推奨=YES**(V1レーンに同梱・observer側) | 8/19-20 |

## R5. Tier C見解の一致(確認のみ)

habit学習・hunger/sleep_pressure・microthought・social capacity・group hyperedge・CVA型・ABC較正・distillation・dt=1分=**本選後**——3本目も同結論(§51-64)。人間行動系の本選前投入は**HOME_AWAKE最小(β9)のみ**で変わらない。

## R6. 完了ゲートの統合

FINAL_DESIGN_GAPS §61とRESOURCE_AWARE §76のチェックリストは、既存のD1-c 8項・信頼性リハ7本・U-10と重複が多い。**β凍結時(8/18)に「本番前ゲート一覧」1枚へ統合**する(新規要素=model freeze・used/cap・coverage/fairness・zero-call率・Data Vintage)。

## R7. A7の更新

リポ直下の監査ファイルは**5本**になった(いずれも未コミット)。root直下=公開ミラー除外対象外の事情は不変→**docs/plans/source/へ移動してコミット**を引き続き推奨。
