# 開発ログ(圧縮アーカイブ)

> 10往復ごとに [devlog.md](./devlog.md) のライブエントリをここへ圧縮保存する。
> 設計の正典は [docs/design.md](../design.md)。ここは「何を・なぜ決めたか」の圧縮履歴。

---

## Compressed Block #0 — プロジェクト立ち上げ・設計framing(プロトコル導入前の全往復)

**プロジェクト**: AUTOMATA 第2回ハッカソン参加作品。LLM による大規模人工社会シミュレーション。

**経緯と主要決定**
- ベースコード(2D fire-sim)を `reference/` に隔離(参照のみ・import 禁止)。ハンドオフを北極星に、新規構築+パターン参照で進行。
- ゴール階層 L0–L4 を確定。到達点 = スケール第一の「動く人工社会」(プロダクト)を主役、k*/改変者の創発研究を旗艦デモ、論文級データは副産物。
- マイルストーン梯子 **M1→M2→M3**。最初の成功 = M1(ラベル創発+伝播+drift+高コスト行動、指標 a–d)。
- 規模ラダー: 骨格 10–50(Mock)→ 創発調律 100–500(本物LLM)→ 本番フル×k掃引×seed。規模は設定パラメータ。
- アクション空間 = **Bundle C**(発話/ラベル + 移動/POI + 資源プール/集団形成)、モジュール式レジストリで最大プランへ拡張可。
- 基盤 = 4永続レイヤー(空間/資源/社会network/象徴)。frame 分離(エージェント=世界にラベル / 研究者=事後測定)。LOD = LLM 起動はイベント時のみ、ラベリング起動と統一。
- リサーチ: **Moltbook 2026** で「規模だけでは社会化は創発しない(大域的意味安定化・個体慣性・共有メモリ欠如)」→ 主張を「**規模化しても創発が崩壊しない機構(メモリ・感受性・非ブロードキャスト伝播・LOD)が新規性**」へ鋭利化。観測指標に Moltbook 5指標を流用。
- 観測層/ログ設計(暫定): 世界系 / エージェント個別 / コミュニティ × 2つの圧縮(認知的=drift源 / 保存=計測対象保持)。物理 backend は OPEN#5 として指標確定後に逆算。

**恒久ルール確立**: 拡張前に確認 / 論文は結論でなく seam として / 論文リサーチは自動・web 優先 / 本開発ログのプロトコル / リンクは security 検証後に掲載。

**ファイル**: `docs/` 整理、`design.md`(252行)清書、`project-charter` 等を記憶へ保存。

**未決(OPEN)**: 因子 down-select(#1)、state 更新則(#2, 次の肝)、初期分布(#3)、ラベリング粒度(#4)、storage(#5)、観測層の記録内容(暫定・変更前提)。

---

## Compressed Block #1 — Entries 1–10(2026-06-29 〜 07-02)
**テーマ: 開発ログ機構構築 → 学際スコープ確定 → リサーチ funnel 開始(分野1-3完了)**

- **ログ機構(E1)**: devlog(往復ごと)+ 10往復で本ファイルへ圧縮。references はリンクを security 検証後に掲載。
- **学際スコープ(E2-4)**: Object(性格動機 / 集合行為 / 文化進化・社会言語 / ネットワーク拡散)+ Method(複雑系 / マルチエージェントAI / 計測)+ 経済制度(ゲーム理論・制度経済 / 市場・メカニズムデザイン / 信頼・評判)+ ALife。**世界2.0 を「構築ガイド」として採用**(affordance + observable、振る舞いは焼き込まない)。**視空間=社会の構造(load-bearing)/ 生態系=コミュニティの動態**。P0/P1/P2 で重要度分類(research-scope.md)。
- **novelty 再定義(E5-6)**: 規模は既達(OASIS 100万 / AgentSociety 1万)→ 差別化は ①世界改変者の創発(問い)②k* 測定 ③崩壊回避機構(memory / 感受性 / 非broadcast / LOD)④**検証可能性**(validation 危機への回答)。
- **分野1 MAS(E7-8)完了**: 単一FWで認知×規模は両立不能 → **hybrid**(Concordia 認知 + AgentScope/OASIS スケール様式 + Mesa/自前 安価tier + LOD 橋渡し、world/factors/labeling/observer 自作)。OASIS 実測 1M×1step=18h/A100×27 → 我々は **~1k–10k・LOD 必須**。
- **分野2 factors(E9)完了**: trait(NFC/LOC/好奇心)/ state(効力感)分離。Bandura4源泉=更新則入力。proactive personality=事後測定(指紋回避)。GSE/NFC=初期分布(OPEN#3)。
- **分野3 state更新則=OPEN#2(E10)完了**: SIMCA(不満/集団効力感/アイデンティティ+フィードバック)+ Morrison&Phelps(当事者意識)。★ **k = 経験↔state フィードバックループのゲイン**(低k=init-determined / 高k=path-dominated / k*=反転点)= k の文献的接地。
- **成果物**: lit コーパス7メモ、references 検証済24本。
- **恒久ルール**: 拡張前に確認 / 論文は seam として / web-only・DL禁止(多重検証)/ devlog protocol。
- **懸案**: build-vs-reuse 具体案(A/B)は P0 skeleton 時 / `docs/2602.14299v2.pdf` の扱い / 分野4-8 継続。

---

## Compressed Block #2 — Entries 4–10(2026-07-02)
**テーマ: リサーチ funnel 完走(分野4-9)→ 世界2.0 全30分野+PLATEAU → インフラ検証 → ギャップ埋め+red-team → 実装前 決定アジェンダ**

- **分野4-9 完了(E4)= 一次 funnel 一巡**: 文化進化(naming game/Ashery 集団バイアス創発/Centola tipping~25%)/ ネットワーク(complex contagion・閾値)/ 集合行為(Olson フリーライド/Ostrom 8原則=制度創発/Snow&Benford フレーミング)/ 複雑系(k*=相転移/early-warning/**R²の限界→R²+seed発散+EWS の3点三角測量**)/ validation(operational validity/LLM-judge circularity/**tail 過小=改変者の脅威**)/ LLM性質(**RLHF が世界改変を系統抑圧・Moltbook 崩壊の一因/モデル選択=実験変数**)。★§4 統一チェーン全段接地。lit 15・references 47。
- **第2フェーズ: 世界2.0 全30分野+PLATEAU(E5-6, 均等 exhaustive)**: 群①substrate(Lynch 5要素=軌跡から credemergent 事後測定/Searle「X counts as Y」=制度創発/Gibson affordance/生態学 keystone/経済 cold-start)② engagement(SDT/Fogg/★ゲーミフィケーション過正当化=injection 警告/Skinner/Rogers 採用者カテゴリ=tail/Moore keystone)③ build・viz(**Part B: PLATEAU sim⇄viz 疎結合 I/F**/actor model/MDA emergent gameplay)④ 哲学(価値論=価値は関係から創発/GST equifinality=k*問い・feedback=k・autopoiesis=anti-collapse)。★横断発見: keystone=オピニオンリーダー=committed minority=tail=世界改変者 が概念収束。no-fingerprint = Gibson=Searle=MDA の三重接地。lit 31・references 72。
- **第3フェーズ: インフラ検証(E7, Gemini 要約 fact-check, Opus 委譲)**: ❌APC「多様性」理由は誤り(APC は出力分布不変)/⚠️**FP8 は A5000 で不可→AWQ-INT4 ~17GB**/⚠️「30秒/step」は **N≈90-480 decision/step 上限=LOD 必然が数字化**/★ソロ内省の頻度・深さ・接地強度=**k の operational 実装部位**/storage 推奨=Redis+pgvector+NetworkX。design §11.5 新設。
- **第4フェーズ: ギャップ埋め+red-team(E9, Opus×4)**: ①実験計画(2段階掃引/seed=CV収束/**k*主推定=finite-size scaling N3水準**/judge=別ファミリ+κ≥0.7/pre-register+multiverse/Hydra+MLflow+DVC/応答キャッシュ=再現性の要)②人流(**EPR+visitation law=cheap 移動則**/POIグラフ+リンクキュー/Epstein grievance 範型)③ペルソナ・言語・安全(IPF×LLM+Verbalized Sampling/**言語=第一級交絡**/Prompt Infection→操作量を改変者指標に/cheap 意見則=Friedkin-Johnsen)④**risk-register.md 新設 R1-R19**: 🔴k の compute 交絡(sham/null 対照必須)/tail×均質化→被説明変数の連続量化/検出力×10日→ゴール再設定。★**監査結論: k*確定は10日で低確率(5-15%)、測定器+兆候なら 35-50%**。lit 35・references 100+。
- **第5フェーズ: 実装前 決定アジェンダ(E10, Opus×2)= decision-agenda.md 新設**: D0ゴール/D1被説明変数/D2 build-vs-reuse/D3言語/D4モデル/D5-D9 OPEN/D10-D17 実装土台(config・ログ正準スキーマ・応答キャッシュ・クロック・テスト・エラー処理=どの文書にも無かった考慮漏れ)。★訂正: **RLHF 対照は Qwen3-32B 不可(base 未公開)→ OLMo-2-32B/Qwen2.5-32B、言語×対照モデルは連動**。運用=Qwen3.6-27B AWQ-INT4(VLM, Apache-2.0)。Ricoh 日本語版=非オープン。★design.md が red-team 提言を未反映=文書整合が必要。
- **現況**: コード未着手(src/ なし)。リサーチ実務は Opus 4.8 委譲・Fable 5 検収統合の体制確立。**次: decision-agenda を D0 からユーザーとすり合わせ**。
- **懸案(実装前)**: D0-D17 の決定 / 文書整合(design 更新)/ 要検証(A5000 実機ベンチ・日本語トークン倍率・abliterated 劣化)/ ハッカソン正式日程待ち。

---

## Compressed Block #3 — Entries 1–10(2026-07-03 〜 07-04)
**テーマ: 決定(D0-D17)→ P0 実装 → 世界 v2-v5 へ急拡張(OSM実地図・実LLM・インターネット層・ビューア2分割)**

- **決定すり合わせ(E1-3)**: D0=二段ゴール(必達: 測定器+チューニング+k兆候 / ストレッチ: k*確定)、D1=連続量主、D2=自前 lean core、D3=日本語仮、D4=Qwen3.6-27B AWQ-INT4 仮+RLHF対照両方、D5-D9 決定。D10-D17 実装土台草案→ユーザーFB: **移動=経路検索+道なり(テレポート禁止)/ ログ簡単拡張+語彙・伝播経路ログ / 実名使用(D17改)**。運用=Fable5主・Opus4.8サブを恒久化。
- **P0 骨格(E4, src/ 初コード約30ファイル)**: config(OmegaConf)/RngHub(PCG64, 順序非依存)/observer(**イベントレジストリ式L1+L1b+L2プラグイン+L3, Parquet+zstd, vocab_coin・transmission=伝播系譜**)/world(CityMap/Router A*+ODキャッシュ/Clock 1step=10分・144=1日/知覚40m)/認知(LOD驚き発火・EPR routine・deliberate JSON・**reflection=k: free/degraded/sham/off**)/llm(Mock+**応答キャッシュ=D13**)/labeling(採用閾値2=complex contagion)/scheduler(agent_id昇順=決定論)。**テスト9本**(e2e/テレポート禁止/bit一致決定論/no-fingerprint静的チェック等)以後全維持。手作り渋谷600m四方地図(19ノード)。
- **ビューア+Ollama(E5)**: Parquet→単体HTML(sim⇄viz疎結合)。Ollamaバックエンド(format=json, 失敗→routine fallback=D16)。
- **世界 v2(E6)**: **OSM/Overpass 実地図**(1,208交差点・1,677道路折れ線・建物40・ゲートウェイ55)。道なり連続補間移動/移動手段 walk800・bicycle2000・car3500(モード別サブグラフ)/建物階層(知覚=同建物同階)/**範囲外=計算しない**(駅経由は定刻ダイヤ制約=終電後帰れない。ダイヤ=公表間隔の近似と明記、GTFS seam)/ビューアv2(フォーカス・関係グラフ・フロアマップ)。
- **v3(E7)**: ユーザーFB6件。**直線移動の正体=ログが最終座標のみ→move_segmentに経路ポリライン記録**(観測側の情報不足)。家・個別就寝(22:00-25:50)→**内省LLMが自然分散**(0:00一斉停止廃止)。**発話=必ずLLM**(定型文全廃、予算切れ=沈黙)。ビューアv3=OSMタイル背景+レイヤーパネル+色分けセレクタ。**Ollama qwen3:4b 稼働**(think:false・キー名寛容・JSON修復の3連デバッグ→fallback 0)。
- **v4(E8, 夜通し10項目)**: 地図v3=**全建物1,181(住宅633)・実名POI 1,098・渋谷ちかみち地下141本・デッキ148本・車ゲートウェイ158**。家=実在住宅建物(路上睡眠解消)/職場=実在POI+個別出勤/食事行動/**背景交通**(Poisson発生・3万台/日=設定値と明記)/会話多様化(時刻・場所・**気分=factors/mood.py で自然文化、因子名は見せない**・直近発話で反復抑制)/GTFS受け口(ODPT登録=無料・2営業日、手順は docs/research/)。ビューアv4=不透明度スライダー・密度ヒートマップ・地下/POI/車レイヤー・**実フロアガイド10施設**(Opusリサーチ→floorguide_shibuya.json)。**qwen3:8b 導入**。night8b(30体×2日)=423呼び出し・fallback 0・重複発話16%。
- **v5(E9-10)**: ①**インターネット層**(net/internet.py): SNS(投稿=LLM・タイムライン・フォロー=初期k+対面自動)/ニュース/**検索=シミュ内DB**(語彙来歴+ニュース+実在POI+SNS索引。実APIは D13 再現性+架空世界の閉性で不採用と決定)/DM(対面知人へ遠隔・LLM)。**伝播チャネル=face/sns/news/search/dm を transmission に記録**。②**シナリオイベント**(world.events_file: day/time/title/word→coin_media+ニュース配信。ダッシュボードにフォーム→JSON保存。本選でサーバー化しビューアから直接起動予定)。③車の道路逸脱=等間隔間引きで角が消えていた→**RDP形状保存間引き**(geom.py、人にも適用)。④**ビューア2ファイル分離**: viewer.html(地図)+dashboard.html(**X風SNS・LINE風DM・SERP風検索ログ・論文風グラフ5種**(語彙S字/次数中心性の移り変わり/grievance個別/集まる建物/街のリズム)・関係グラフ改良(ラベル・閾値スライダー・ドラッグ)・タイル消失修正・フロア切替バグ修正・全体階層フィルタ・UIリサイズ)。
- **実LLM実績**: day80(80体×1日 qwen3:8b+シブヤレンズ発表)=**LLM 1,327回・fallback 0**、発話849・投稿255(時刻場所職場を反映)・DM151・検索79。**シブヤレンズ伝播1,540回→79/80人採用**(sns 1172主導)。
- **懸案**: qwen3系が coin_label をほぼ選ばない(造語調律=B段)/「初めて来た」トリガー頻発/交通量センサス実値未確認/ODPT키=ユーザー登録待ち/SNSのいいね・拡散機構なし/IPFペルソナ・vLLM(本選)未着手。

---

## Compressed Block #4 — Entries 1–10(2026-07-04 〜 07-07)★生態系→現実ギャップ→再帰性

**E1-3 生態系フェーズ(07-04/05)**: 欲求駆動発火(ゲージ→個人閾値申請→重み抽選→不発30%減衰。R1=出来事のみ入力+k間発火監査)/記憶v2(3層・統合は内省同居・書き戻しゲート=beliefsのみ=k境界)/ペルソナv2(IPF+VS文章化・来街者0.56=夜帰宅→帰路内省で全員k処置)/state更新レジストリ8ルール(R9)/計測パイプライン(R²/カスケード/EWS)。**測定器検証が設計バグ2つ捕獲**(belief未接続=kが不活性→「あなたの考え」行で開通/旧キャッシュ再生→掃引クリーン実行強制)。対面=確定発火+返答保証・アイスブレイク(全k同一ファイル)・内省think:true。経済v0(賃金/消費/バイト/逼迫→grievance)・世界改変ツール5種=4軸(モノ/制度/人/虚構。中立提示・R4客観カウント)・造語は自然観察(coin文脈記録)。テスト29→51。

**E4 docs完遂25項目(07-05/06)**: compute_matched(offでも内省実行・全破棄=4条件計算量一致)/null_series/FSS掃引(N×α擬似連続k軸)/semantic drift・崩壊検知/LLM-judge(κ自作・R4逆流なし)/ETHICS・README/**FJ意見力学**(opinion.py=検査外。プロンプト非注入・接点=face/dm/sns)/agentic pull(固定2段=呼数k不変)/scenario(封鎖・注入)/labeling open/checkpoint-resume(L1全層byte一致)/**3D**(export_3d手書きglb+Blender bpy+three.js同梱viewer3d)。51→120。

**E5 UE転換・車OD・朝計画・心理4種(07-06)**: UE=PLATEAU渋谷2025年度+import script+README(基準日=OSM 2025-04-01暫定)/車OD個体化(信号=期待遅延近似・車線容量渋滞。ambient既定=byte一致)/**朝の一日計画**(起床1回LLM・全k同数→routineの行き先の土台)/タクシー・簡易バス/心理プラグイン4種(SDT/集団効力感/Lynch/Searle=全て既定OFF・因果構造のみ文献接地)/vLLM+FleetLLM(sticky routing・キャッシュはURL非依存)。159→177。

**E6 制度DSL・流入通勤・スケール(07-06)**: **制度DSL 4型**(fee/bonus/curfew/weekly_event=成立提案が実効ルール化。ホワイトリスト・降格安全)/流入通勤者74%(朝二峰流入・POI拡大 office/school/cinema/hall/landmark)/内省ドリフトE2(馴化/鋭敏化/回復・既定OFF)/口座E5(月給・家賃・ATM)/hearers空間ハッシュ51.8×/watchdog(自動再開・巻き戻し)。実LLM3日=劣化なし・**ツール0使用**(B段最優先)。208→239。

**E7 社会の厚み+100日実証(07-06)**: mem100(実LLM5体×100日)=記憶劣化なし・belief線形蓄積。**変革モチベ分析=efficacy天井/grievance床に飽和し個体差消滅**(最大の詰まり)。行政B(区/都/国・源泉徴収・消費税78:22・公務員給与)/娯楽メディアD/組織W2(架空42社10校・配属)/needs 5次元/擬似視覚LOS/equip_all。**Opus偽完了/停滞5件→検収=ディスク実在+自分のpytest を標準化**。W2統合はFable直接実装。330。

**E8 第7バッチ(07-07)**: ビューア軽量化(255MB→5.5MB/3D 4.24MB)/**暦**(start_date設定可・weekday_work)/**天気**(stream "weather"・雨→grievance)/**物理通勤**(commute_to_poi=職場学校POIへ実通勤)/**affect統一ハブ**(arousal+salience。脳科学リサーチ=感情・興味・注意は1回路。飽和を破る第2駆動軸)/**スケジュール帳**(会話から決定論パーサで未来予定抽出→双方の帳簿→プロンプト注入。追加LLMゼロ)/UE出力確認/LLM選定(Qwen3系AWQ-INT4主候補)/振り返り+現実ギャップ棚卸し。345。

**E9 第8バッチ=現実ギャップ全実装(07-07)**: ユーザー「全てのイベントや仕組みの実装を任せたい」。**G1-G6**(相対的剥奪=飽和を破る/関係の質tier・断絶・評判/制度3ルート=労働争議・決定論投票・警察執行/年中行事・ハロウィン群集/キャリア転換/情報環境=推薦・バイラル・炎上)+**H1-H6**(健康疲労病気/世帯家族恋愛/商業=営業時間・動的価格・在庫/災害・運休・停電/観光・多言語・犯罪/内面=離散感情・長期目標・趣味)。**重要発見: 物理・co-locationを変える機能はFixedLLMでON≠OFFが必然→R1の本旨は compute_matched下のk不変性(free==off)で担保**(各波回帰テスト化)。**本番プロファイル方式**(conf/production.yaml=差分重ね書き・ゴールデン再生成不要・start_date="auto")+サーバー是非=「部分的に要る(vLLM艦隊のみ・他は過剰)」。378→**447**。

**E10 第9バッチ(07-07)**: **再帰性**(norm_line/digest_line/repeal/impact_news=監視→知覚→改変の閉ループ。Fable自身実装)/**実験条件=パラメータ宣言方式に決定**(conf/experiments/*.yaml+run_experiment.py)/3観点まとめ(agent-implementation-summary.md)/**制度深化**(権利制度調査の核心=適正手続の欠如→審議・パブコメ段階=立場表明・否決可能/供託金=参入障壁/declare型=権利創設)/**宿泊Wave L**(ホテル泊・連泊・reflect_step=k処置同格。POIパッチ12件=v3p地図)/観測CLI(observe.py=訪問・関心。mem100実証)+商業データ提案17件/ペルソナ自動生成(プール→無作為抽出)/過去ラン分析→P2来街者財布補充・P3発話定型化ガード/ODPT取得スクリプト(キー待ち)。**Opusセッション上限で実装2体停止→ユーザー指示でFableメイン化**(memory更新)。447→476(全緑・退行ゼロ)。

---

## Compressed Block #5 — Entries 1–10(2026-07-08 〜 07-09)★ODPT実ダイヤ→制度深化完遂→自己モデル→現実較正→実LLM初証拠→日常プロファイル

**E1-4 ODPT・地図v7・制度深化2(07-08)**: ODPT実ダイヤ(キーは環境変数+winregフォールバック・チャット/コード/ログに残さない原則確立。オープン枠=メトロ3路線)→**チャレンジ2026キーで東急2+京王1解放=実ダイヤ6/近似3路線**(api-challenge.odpt.org、限定データは data/odpt_challenge/ を .gitignore=再配布不可対策)。JR東GTFSは**未投入と悉皆プローブで確定**(fetch_gtfs_odpt.py=受け皿実装済み・投入後2コマンドで全9路線化。メトロ/京王GTFSで駅時刻表と完全一致の相互検証)。広域地図v7(POI10件補完・組織台帳wide=49組織・3,499ノードでも40体2日35秒)。制度深化2=**勾留・解雇規制(退職金/不当解雇)・営業許可**(却下+許可待ち)。486本全緑。
**E5 制度深化3(07-08)**: **最低賃金の床**(一次確認=東京都1,226円/時・2025-10発効。min_wage_hourly 既定0=床なし。自営は対象外=現実の穴を保存)/**代表制議会**(FJ意見の最近傍投票=決定論選挙→議会が採決=代表制の歪みを観測可)/**立退き**(滞納30日→路上就寝・完済で再入居)/**破産**(滞納60日→免責+自由財産1万+出店制限30日)=滞納→立退き→破産→再入居のサイクルが決定論で閉じる。E5口座を本番ON。493本全緑・初日に議会成立。
**E6 第11バッチ(07-08)**: **Fable計画/Opus実行の分業確立**(agent-coreはFable)。④LOD動態=E2ドリフト実装済みだが**本番未配線が問題**→production配線。③**反射=自己モデル**(self_model_days=N夜の内省を深い内省に格上げ→self/ties→プロンプト注入=自己認識の再帰。書込みはbelief同一kゲート・R1呼数不変)。①**ヒエラルキー**(status.py=合成地位スコア百分位。イベント参加/購買/フィード露出の閾値を機械変調=優先的選択。乱数draw追加ゼロ・プロンプト非注入。L2にstatus_gini等)。②鉄道直通(ビューワー層のみ=東横⇔副都心・田都⇔半蔵門を1本に継ぐ)。516本全緑。
**E7 第12バッチ(07-08)**: 深い内省を固定周期→**出来事誘発に刷新**(文献検証: 引き金=信念との乖離・ネガ非対称だがポジ「地震的」も・侵入的→熟慮的の遅延二段=全て支持)→日内衝撃ゲージ(ネガ2:ポジ1加重)+個人閾値(NFC/LOC写像)+incubation 1-2晩+cooldown 3日。**無意識層 implicit_self**(行動カウントEMA逸脱→「最近の自分」1行を日次決定論合成=揮発的作動自己。核自己 self_model とフィールド分離・双方向結合)。R1呼数完全不変。522本全緑。
**E8 第13a 現実較正(07-09 深夜自律)**: **calibrate_report.py 新設**(現実バンド表=NHK生活時間調査等の出典付き近似と照合)。原則=1シム日=1実日・圧縮≤10倍は明記時のみ・**較正は production.yaml 重ね書きのみ**(基底=ゴールデン不変)。大半は最初から整合(睡眠7.33h・労働7.07h・家賃比0.28・貯蓄率13-16%等)。乖離3系統を較正: **窃盗×554→crime_prob 2.0e-6**・**タクシー×13-20→prob 0.02**・**雇用×80-100→layoff 2e-4/switch 4e-4/rehire 0.02**。100日で全✅。**mock行動系はアーティファクト**(SNS0・設立×152)→実LLM(qwen3:4b)では全部バンド内=**機械系=mock・行動系=実LLM**の分担確立。副次: 不満0.101→0.034=k*信号が外生ノイズから浄化。`model.backend=ollama`が正キー(llm.*は無効)。
**E9 第13b 実LLMパイロット(07-09 日中自律・テーマ自己選定)**: ①**R²(k)初の実LLM証拠**=R²ext free 0.508/0.800 vs off 0.387/0.621(Δ+0.12/+0.18・両シード符号一致)。Y総量はk不変=kは「誰がやるか」を動かす。④mock対照=null(canned応答ではk不効)+off で R²int=0.000=kゲート機械検証。②深い内省閾値の用量反応=0.60→0件/0.45→0件/**0.30→月1ペース=最終推奨**(production未変更=ユーザー判断待ち)。③実LLM 5体×100日完走(3,805呼212分)=記憶劣化なし・地位ジニ実LLMでも横ばい(マタイ効果検証はN≥50へ)。
**E10 第14バッチ(07-09)**: ①LLM使用検証=会話返答14%等、発話系は全てLLM由来・ルールは身体系のみ ②**LOD効率=発火率4.1-11.4%≈LLM呼数1/12**(キャッシュヒット0=効率は全てdrive gate) ③トークン相場(AGA: 30-43%削減でも believability 不変)→**plan_max_tokens 448/reflect 2048**(飢え11.4%→8.7%) ⑥**scripts/observe_flows.py**=金流(spendは売り手なし=catシンク・depositは政治供託)+注意ネットワーク(被注意gini) ⑦**conf/daily.yaml**=災害OFF・議会4年・立退き90日/破産240日・300体名簿(「日常の範囲内・現実に忠実のみ」) ⑧ビューワーは--no-trafficで439MB→8.4MB。**daily_llm_20a7d(実LLM20体7日)=全項目現実バンド内・daily300_100d(mock300体100日)=較正が再調整なしでスケール**。

---

## Compressed Block #6 — Entries 1–10(2026-07-10 〜 07-12)★開放行動→世界解釈の観察→マルチモデル対応(第15〜24バッチ)

**E1 第15(07-10)**: 歩行速度検証=シムは既に現実準拠(move_segment実測 中央値1.14m/s vs 渋谷実測1.0-1.5)。「速すぎる」の正体=ビューワー時間圧縮→既定×4→×1へ。3D版ビューワー送付(長期ラン368MB=日数スライスが課題)。
**E2 第16(07-10)**: 計画専用4本=データ戦略(生=正準・最小/指標=後処理。L2凍結)・基盤抽出(**EnvPack** env.yaml方式W1-W5=渋谷と基盤の分離)・環境自動生成(make_env 7-stage v0-v2)・自由度監査(行動的自由度の初監査=「提示2,654回で行使0回」・move_toすら無い)。
**E3 第17(07-10)**: ★**開放行動 "do"**(freedom.open_actions=LLM自身が自由記述で行動決定・物理/所持金/拘束の客観ゲートのみ)+**価値4軸**(values.py=実用/感情/社会/認識。辞書+自己申告・充足の限界効用逓減+日次中立回帰)。実LLM検証=開放行動は自然に行使(deliberateの1.7%)vs 世界改変ツール0行使と対照的。tests 6本。
**E4 第18(07-11)**: コミュニティ検出(min_weight2.0+louvain正準・7-13コミュ/窓・ライフサイクル66件・組織NMI0.35=自然コミュは会社の線から乖離)・tidyパネル+商業4観点(**広告転換94.1%→target照合+非接触対照で5.9%に修正**)・街頭広告OOH+群衆視覚(新stream "ads"・ファネルがシミュ内で閉じる・実LLMで広告の口コミ化38件)・計算量削減は計画のみ(E1-E3)。**教訓=検収は実データ規模で**(LPA潰れ/pagerank0.0/転換盛りの3実バグがテスト緑のまま露呈)。
**E5 第19(07-11)**: リサーチ専用=世界モデル(C1-C9導出。最優先C2可制御性/C6規範予期/C1期待形成)・AI解像度(**manifold collapse=属性を盛ると均質化**・introspection自己報告は2割接地→「行動でkを測る」の機構的正当化)・Social Simulacra系譜(**PIMMUR 6原則=代表論文の90.7%違反**・Aaru等の商用はQ&A型=物理的帰結を返せない空隙・PLATEAU行動レイヤーが最有望経路)→reality-levers.md統合(P1-P3)。
**E6 第20(07-12)**: ★主観的世界モデル実装(worldview.py=C1場所×時間帯の期待EMA+誤差/C2可制御性0.5起点・世界の応答のみで分岐=純経験の経路依存・日次キャップで飽和防止/C6開拓的行動の記述規範)・★**内省全滅バグ発見**(ollama num_predictは思考込み→reflect_think=trueで全実LLMランのbelief書き戻し0件。daily.yaml修正→15/15。**R²(k)パイロット+0.12/+0.18はbelief死亡状態の測定=再検証要**)・PIMMUR準拠表(5 PASS/Unawareness PARTIAL)・model×k対照設計(abliterated)・7日実LLM観察=belief122件・世界観クラスタ49・解釈の分岐(雨への反応個体差)。
**E7 第21(07-12)**: 旧shibuya-sim全読レビュー(A2/B4/C11)→legacy-adoption計画=P1創発の後付けテキスト検出/P2 SNS架橋距離/P3ペルソナ深さ属性(条件付き)+保留3。
**E8 第22(07-12)**: P1実装(detect_emergence=**架空イベント「ボードライブ」を12人が105回共有**・規範発話・語形ドリフト「パーラー→パーリー」伝播・coined分離)・P2実装(sns_geo既定OFF=SNS/DM伝播にdist_m。**SNS伝播の27%が500m超の遠距離架橋**)・P3=不採用判断(manifold collapse抵触・比較可能性・推論量・非決定化)・abliterated=セキュリティ4連検証(発行元/レジストリ層直接検査/CVE/取得後digest)→pull→1日スモーク合格(日本語率0.88=instruct同等・書き戻し14/14・distinct-2 0.136=やや定型化)・multi-model-lod計画(purpose-LOD第一・動的エスカレーション不採用・**trait由来割当は却下=生得性の裏口**)。フルスイート584本全緑。
**E9 第23(07-12)**: **マルチLLM/API対応実装**(M1=openai_compat+anthropic(temp/seed送らない)/M2=RouterLLM purpose別dispatch+配線=**子を各自CachedLLMで包む**(D13維持)・キャッシュは子name別ファイル・APIキーは環境変数名のみ・agent_tierはValueErrorガード)。検収で実バグ発見修正=ollama互換口のqwen3は思考停止不可→content空(空を__api_error__化)。router(mock子)=素mockとL1バイト一致。agent-lod-deepdive討議資料(AC Unity=identityを捨てる群衆LOD・The Sims=trait条件付き背景は生得性裏口の実物・**300体では個体軸LOD不要の示唆**)・pending-decisions説明書。**609本全緑**。
**E10 第24(07-12)**: 計画済み未実装の棚卸し→docs/plans/unimplemented-inventory.md(大型=基盤抽出/環境自動生成/自由度P2/デモ・LOD残り=M3討議待ち/M4・計算量E1-E3・小粒=作話接地率/内省プロンプト改善・実験ラン=4セル/k再検証/Unawareness・条件付き保留3)。
