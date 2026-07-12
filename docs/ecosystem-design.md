# 生態系設計(エージェント認知・社会機構)— 正典 v1.4(2026-07-06)

> **v1.4 追補**: ①朝の一日計画LLM(起床時に1回・k非依存。計画が暇な時間帯のルールベース行動の土台に。planning.enabled)
> ②タクシー(既定ON)+簡易バス(既定OFF)。電車の実ダイヤはAPI申請待ちで保留 ③車の交通v2(world.traffic.mode=od:
> 信号69・車線・一方通行295区間・ゲートウェイOD。既定ambient=本番でON) ④心理プラグイン4種(psych.*、**全て既定OFF**・
> config着脱: SDT動機=欲求入力の個人別倍率 / 集団効力感+内集団boost / Lynch都市イメージ=ランドマーク重み+認知地図レンズ /
> Searle制度化=成立提案が「街の取り決め」としてプロンプトに載る) ⑤地図v6(bbox/OSM日付指定・実入口・実フロア接続。
> data/shibuya_osm_wide_20250401.json=PLATEAU 2025年度整合の暫定基準日) ⑥可視化の主軸をUEへ(viz/unreal/、PLATEAU SDK。
> Web3D=quick-look維持) ⑦本番マルチGPU基盤(llm/fleet.py sticky routing+フェイルオーバ、docs/ops-production.md)。
> テスト177本。詳細は devlog Entry 5。

> 世界(空間)v5 の上に載る「エージェントが作る生態系」の設計。決定の経緯は
> [decision-agenda](./decision-agenda.md) / [risk-register](./risk-register.md)、
> 実験の枠組みは [design.md](./design.md) §3。ユーザーすり合わせ 2026-07-04(発火方式・Y二系統・感情辞書・一気に実装)、
> 2026-07-05 追補(v1.1: 対面会話=確定発火+返答保証・アイスブレイク・SNS自然化・内省の思考モード /
> v1.2: 経済v0・世界改変ツール4軸・滞在短縮・造語の自然観察 /
> **v1.3: docs棚卸しの未実装25項目を完遂** — 対照2種(null_series/compute_matched)・FSS・EWS統合・semantic drift・
> 崩壊検知・LLM-judge・4層Y統合・scenario摂動・labeling open・rewards・自営日銭・屋内イベント参加・founder優先枠・
> SNSいいね/RT・logistic発火・**FJ意見力学**・**agentic pull記憶**・checkpoint/resume・ETHICS/README・bench・
> **3D可視化(export_3d + Blender + Web3Dビューア + PLATEAUリサーチ)**。テスト120本。詳細は devlog Entry 4)。

## 1. 欲求駆動発火(推論タイミングの分散)— Phase A
**仕様(ユーザー案 2026-07-04)**: 出来事が欲求ゲージ(drive 0-1)を溜める → 個人別閾値で「申請」→ 申請時に個人の重み(fire_weight)で**確率的に発火判定** → 不発ならゲージを**数十%減衰**(fail_decay=0.30)→ 再蓄積・再申請。

- 実装: `cognition/drive.py` + `engine/scheduler._phase_drive`(申請順=欲求残量順、id順バイアスなし。予算超過は持ち越し)
- ゲージ入力(**出来事のみ・信念/k非依存 = R1対策**): 初訪問 .35 / 混雑 .30 / 未知語 .40 / 話しかけられ .25 / DM受信 .35 / ニュース .15 / SNS .08 / 同席 .10 / 沈黙 .015/step / 状態変化 .50×|Δ|。減衰 .02/step、発火後残量 ×.20、不応期 3step
- 個体差: traits→(drive_threshold, fire_weight) の写像は **factors/registry.drive_params のみ**が知る(no-fingerprint)。NFC→閾値低、内的統制→通過率高
- 発火時の表現形: きっかけ(top reason)で選択 — novel/congestion/unknown→状況コメント、DM受信→返信、ニュース→投稿、同席→会話、独りでスマホ→投稿/DM、それ以外→独り言(solo)
- 学術接地: Park2023 reflection(重要度累積閾値)/ MicroPsi selection threshold(閾値+ヒステリシス=不応期)/ Fogg B=MAP / OASIS 確率活性化 / EVC metacontrol(RQ1 検収 2026-07-05)
- **R1 監査**: drive_request イベント+L2 n_fires。テストで k∈{free,off} 間の発火数±20%以内を担保

### 1b. 対面会話の確定発火と返答保証(v1.1、ユーザー決定 2026-07-05)
**現実の会話は必ず LLM で推論し、抽選(確率発火)は媒体(SNS投稿・DM)と独り言/思考のみに適用する。**

- **開始**: 申請時(ゲージ≥閾値・不応期外)に同席者がいて会話クールダウン外なら、**抽選なしで確定発火**(`drive_request.mode="face"`, `lottery=null`)。同席者なし/クールダウン中は従来どおり fire_weight 抽選(`mode="media"`)
- **返答保証**: 話しかけられた最寄りの相手(`_reply_to`)は次stepに**抽選なしで必ず LLM 返答**(trigger="reply"、相手の発話をプロンプトに引用)。予算(lod)は共通の上限として残る
- **収束**: 各人の返答枠 conv_max_turns=3 を使い切ると conv_cooldown_steps=6(1時間)の会話クールダウン→無限連鎖しない。クールダウン明けに枠は回復
- **R1**: 対面発火・返答とも入力は出来事(同席・被発話)のみで k 非依存。L2 に n_face_fires / n_replies を追加し監査可能
- 検証(mock 40人×1日): face申請123→granted 123(100%・抽選なし)、media申請243→129(抽選53%)、reply 104、最大連続reply 2(収束)

### 1c. 内省の深化(v1.1)
- 会話 max_tokens 160→**320**。内省は **reflect_max_tokens=1200 + qwen3 思考モード ON**(`model.reflect_think`。llm 層に think 引数を追加、**キャッシュキーにも think を含める**=切替時の旧応答再生を防止)
- 内省プロンプトに「出来事を順に思い出す→なぜ印象に残ったか→気持ちの動き→明日への影響」の熟考指示を追加。スモークテスト済み(qwen3:8b で reflect JSON 解釈成功)
- 内省の計算量は k 全条件で同一に増える(sham 対照は維持)

## 2. 記憶 v2 — Phase B
3層: **エピソード緩衝**(直近30件)→ **統合記憶**(就寝時の内省呼び出しに同居: 日次要約(日記・最大7日)+顕著エピソード(重要度1-10、上限120件・重要度×新しさで忘却))→ **意味記憶**(beliefs=kの作用点+関係台帳(相手・回数・最終接触)+場所なじみ)。

- 想起 = 非LLM push: `score = 0.5·recency + 2.0·importance + 3.0·relevance`(**GA公式実装の実効比**。decay 0.9983/step = GA 0.99/時 換算。relevance=文脈語の包含で代理)(RQ2 検収)
- プロンプト注入: 直近4件 / 想起3件 / 間柄(◯◯とはn回話した仲)/ 昨日までの日記1行
- **k境界**: 統合は全条件で実行(計算量同一)。**書き戻しゲート(free/degraded/sham/off)は beliefs のみ**
- agentic pull(能動検索)は P2 seam(infra 方針: 日常=push)

## 3. ペルソナ v2(D6 実装)— Phase C
`scripts/build_personas.py N` → `data/personas_N.json`(シミュ本体の LLM 負荷ゼロ・決定論):
1. **IPF 骨格**: `data/shibuya_population.json`(令和2年国調 渋谷区: 夜間243,883・昼間551,344・**来街者比率0.56**・性比は実数由来。年齢帯/職業 share は暫定=RQ4で表IDまで特定済み)→ 年齢×性別×職業の結合分布→骨格
2. **尺度**: sample_traits(tail 10%明示確保)+ drive個体差。**注入/評価分離**: 構成概念語バリデータ(`agents/validate.py`)で検査、違反は手続き文に差し替え
3. **文章化**: qwen3:8b で Verbalized Sampling(5案→既出と最も異なる案を採用=mode collapse対策)。distinct-2 で多様性監視
- **来街者(visitor)**: 家は街の外。就寝時刻→駅(終電後は徒歩で縁)→exit_area→**帰路の電車で内省(k処置を全員に保証)**→睡眠時間+αで朝に帰還。居住者は実在住宅で就寝→内省
- 初期関係: 同じ住宅・同じ職場は顔なじみ(1人≤3、complex contagion の wide bridges)
- 出力: `runs/<name>/traits.json`(R²回帰の研究者frame入力。エージェントには見せない)

### 3b. アイスブレイク(実験前の初期関係形成、v1.1・ユーザー決定 2026-07-05)
`scripts/build_icebreak.py` → `data/icebreak_N.json`(オフライン生成・決定論):
- **ペアリング**: 骨格属性(年齢・性別・職業・来街)+心理尺度を標準化→cosine 類似度。各人に**類似上位2人+ランダム1人**(ランダム枠=弱い紐帯・遠い橋。情報伝播研究の知見)
- **会話**: 各ペアで qwen3 が「知人の集まりで初めて会った立ち話」を3往復。全発話の感情価(東北大辞書)を記録
- **取り込み**: simulation 起動時に関係台帳(record_contact×往復数)+初対面エピソード+知り合い登録(net.add_contact=フォロー・DM可)
- **公平性**: 全 k 条件が**同一ファイル**を読む=初期関係は条件間で完全同一(k以外の交絡を排除)

### 3c. SNS の自然化(v1.1)
- 投稿プロンプトから「場所・気分・出来事の報告」枠を廃止 →「いま感じたこと・目にした光景・タイムラインへの反応を、SNSらしいくだけた口語の短文で。場所・時刻の報告文/挨拶をしない」
- タイムラインは「@著者名: 本文」形式で提示(誰の投稿かがわかる→返信的な投稿・言及が可能に)

## 4. state 更新則レジストリ(OPEN#2)— Phase D
`factors/update.py`: 因果構造のみ実装、**magnitude は conf.factors で調律**(B段)。全変更を state_update(cause付き)に記録。R9: 更新関数は traits を見ない。R7: 恒常性は注入しない(clip のみ)。

| ルール | 因果 | 接地 |
|---|---|---|
| congestion | 混雑遅延→grievance+ | Epstein 2002 |
| heard_valence | 聞いた/読んだ言葉の感情価→grievance±(ネガ強)・efficacy+ | SIMCA(affective)|
| being_heard / ignored | 聞き手の有無→efficacy± | Bandura 社会的説得 |
| work_done | 勤務完遂→efficacy+ | Bandura 達成経験 |
| vicarious | 他者の語・成功の目撃→efficacy+小 | Bandura 代理経験 |
| park | 公園滞在→grievance− | 回復環境 |
| own_adopted | 自分の造語が採用→ownership+ efficacy+ | 影響の実感=当事者化 |

- 感情価 = `lang/sentiment.py`(**東北大 乾・岡崎研 評価極性辞書** pos5,345/neg7,983、純stdlib・決定論・否定反転・再配布可ライセンス、RQ3 検収)。SNS×0.5 / ニュース×0.7 / 対面・DM×1.0
- 検証(mock 40人×1日): 729更新、8ルール全発火(heard_positive 362 / ignored 112 / own_adopted 94 / being_heard 55 / heard_negative 45 / vicarious 33 / work_done 26 / park 2)

## 5. 観測・計測 — Phase E(何をどう観察するか)
**Y(世界改変量)は二系統で別記録**(ユーザー決定): **Y外部**=起点カスケード規模+引き起こした採用+新規関係+SNS到達(主指標・客観計上=R4対策)/ **Y内面**=belief書き戻し回数・量(副指標。kと定義結合するため主指標にしない)。

- Run単位(`scripts/analyze.py`): agent_features / item_cascades(規模・深さ・チャネル構成・S字)/ network_windows(次数・クラスタ・中心性churn)/ collective(採用率・語彙エントロピー・Moltbook型指標)+ 論文風図版 + report.md
- 掃引横断(`scripts/analyze_sweep.py`): **R²(k)**(OLS Y~traits、seed階層ブートストラップCI)/ **seed発散** / **EWS**(Dakos: detrend→分散・AC1→Kendall τ)の三角測量 + **発火数のk間監査(R1)**
- 手順: A段=世界調律(接触率・採用率・崩壊なし)→ B段=k掃引(off/sham/degraded/free×seed、まずmock→実LLM)。k*主推定=FSS(N 3水準)は本選

## 6. 経済 v0(v1.2、ユーザー決定 2026-07-05)
`src/society/economy.py` + conf.economy。お金は**世界の状態**(心理因子ではない):
- **所持金**: 職業別初期レンジ(persona 生成時)。来街者は allowance のみ(賃金なし)
- **賃金**: 勤務完遂で日給支給(wage イベント)。**バイト**: 学生・フリーターに実在 POI のシフト(週3夕方4h等)を割当、シフト完遂で時給支給+達成経験
- **消費**: 飲食・買い物・夜遊びに価格(conf.economy.prices)。**残高不足の選択肢は選べない**(無料の公園等へ)
- **心理接続**: 残高<閾値 → 1日1回 grievance+(factors.money_pressure_grievance、conf調律可)。R9: ルールは金額イベントのみ参照
- 観測: wage/spend イベント、L3に money、L2に mean_money/n_broke
- 既知の穴: 自営業(固定職場なし)は v0 では賃金が発生しない(初期資金+バイトで生活)

## 7. 世界改変ツール(v1.2、ユーザー枠組み: モノ/制度/人/虚構)
`src/society/tools.py`。**中立提示**(発火時のみ1-2行、「使っても使わなくてもよい」。造語と同じく促進せず自然な使用を観察する方針)。効果は全て客観カウント(R4)、提示条件は k 非依存(R1):

| ツール | 軸 | 仕組み | Y(客観測定) |
|---|---|---|---|
| host_event | 虚構・人 | 開催宣言→SNS/DM告知→自由な人が確率参加(関係で+)。会場では対面確定発火が会話を自然発生させる | 参加人数・event経由採用 |
| (勉強会) | **人** | 主催者の語がタイトルにあると出席者に channel="event" で2露出=教育は complex contagion を一撃で満たす | 教えた語の採用カスケード |
| post_flyer | 虚構 | 現在地に貼る(ttl1日・ノード3枚まで)。通行人だけが見る場所ベース放送 | ユニーク閲覧・flyer経由採用 |
| found_group | 虚構→構造 | 結成→名前が labels 伝播に乗る→関係者が確率加入→相互フォロー。所属はプロンプトに出る | 会員数曲線 |
| propose | **制度** | 提案→2回露出=署名(露出ベース、内容判定なし)→25%で成立: 世界ニュース+提案者に当事者化効果 | 署名数・成立時間 |
| open_venture | **モノ** | 所持金≥開業費(3万)で出店→通行人が購入(売上は店主の money へ)。3日売上ゼロで閉店 | 客数・売上 |

- 観測: 13イベント種+L2集計6種+ measure.agent_features に9列(**y_external の合成式は不変**、列追加のみ。合成はB段で決定)+ analyze「tools」セクション
- mock検証(40人×1日×3seed): 全ツール発火・勉強会で造語が3人に伝わる・提案成立→ニュース配信を確認

## 8. 残課題・seam(v1.3 で大半を解消。残りは以下)
- **IPF の年齢×職業実数**: e-Stat 取得を試行したが不成立(DB は JS 描画・API は appId 必須)。試行記録は docs/research/lexicon-ipf-shibuya.md。appId(無料登録)があれば実数化可能
- 集団効力感・社会的アイデンティティ因子(第2弾)/ ペルソナ文の文化的妥当性検証
- ツール列の Y_external への合成重みの**値**(機構 y_weights は実装済み。重みの決定はB段でユーザーと)
- venture 売上は複数日ランで蓄積(機構は検証済み)/ conv・logistic 発火パラメータの感度分析(B段)
- 本選GPU前提: vLLM バックエンド・モデル艦隊/tier ルータ・abliterated 対照・Redis+pgvector・分散 actor・FSS の実データ N 3水準
- 3D: PLATEAU LOD2 実形状への差し替え(導入設計は docs/research/3d-visualization.md に記録済み。scene.json 契約は追加専用で互換維持)
- null_series 対照を実LLMで使う際は llm キャッシュを無効化するか per-call 変動プロンプトに(呼数監査は現状で成立、計算量一致にはキャッシュが干渉)
