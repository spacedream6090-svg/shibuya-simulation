# STATUS — 現況台帳(実装済み / 計画のみ / ユーザー判断待ち)

> **更新プロトコル**: 実装バッチのコミットごとに必ず本ファイルを更新する(検収の一部)。
> ここは「今どこにいるか」の一覧だけを持ち、詳細は各リンク先(計画書・devlog)が正典。
> 最終更新: **2026-08-02**(**高精細3D×物理=松案+P3縫合まで全レーン完結**: ビューワー品質修正→レーンA データ3本→
> 竹-3 f_iW→レーンB テクスチャ統合79.39MiB→**竹-4 P3境界縫合**(physics.zones+ORCA昇格+ゲート+知覚翻訳・既定OFF)・
> テスト **2536→2687 緑**・**夜間実LLM検証ラン完走**(100体×288step=sim2日・3,759呼・fallback 0・plan retry 0・
> reflect 176 正常=「LLMシミュレーションが回る」検証達成・runs/night_llm_100a3d に 2D/3D ビューワー生成済み)・判断待ちに 3D-U0/RW-U1/SV-U1)

## 1. 実装済み(主要システムの現在地)

新機能はすべて **既定 OFF**(R1)。バッチ履歴の全文は [docs/log/devlog.md](docs/log/devlog.md)
(圧縮版 [devlog-compressed.md](docs/log/devlog-compressed.md) Block #0〜#12)。

| 領域 | 内容(主なトグル) | バッチ |
|---|---|---|
| 世界基盤 | 渋谷実地図(PLATEAU/OSM)・実ダイヤ(ODPT)・日次 presence 名簿制・経済/制度/物流・天候(weather.py)・現実較正(calibrate_report) | 〜第58 |
| 関係性の内生化 | 承諾/拒否の内生(relations_endo)・treatment 実験一式(endogenous_accept)・誘い相手の内生(endogenous_invite) | 第62-64 |
| LLM 健全性 | fallback 率など L2 KPI・watchdog_llm・observer.llm_health 3列 | 第66/P0 |
| 反実仮想の器 | world.mod = edges_closed / edge_speed_scale / open_hours(+gate_capacity 予約) | 第67 |
| 実高さ・可視 | building_heights(3,531棟)・build_visibility(2.5D LOS 行列) | 第67-68 |
| 場所の意味づけ | labeling.place_binding(造語の場所束縛→知覚1行) | 第69 |
| エコー計測・未定義行動・沈黙 | observer.echo(L2 常設5列・enabled:false で退避可)+freedom.undefined_register / explicit_nothing(既定 OFF)・伝播 KPI のエコー除外は新列並記 | 第70 |
| LLM 全文ジャーナル+REPLAY | model.journal(既定 ON・gz 11.5x=1万体10日≈1GB)・model.cache_mode: free/replay(fail-fast・フォールバック無し)・run_manifest.json(git SHA/config hash/全トグル) | 第71 |
| 機能レジストリ+ランモード | registry.py 175件(strict146/journal27/none2・未宣言は CI fail)・run.mode: none(既定=不変)/observe/journal/verify(自動 OFF+manifest 記録)・比較ガード3スクリプト | 第72 |
| 真偽台帳ミニマル | beliefs.enabled / verify_actions(既定 OFF・journal 等級)= fact 8種・信念/伝播木・検証行動3種・漏洩3点ガード(静的+実行時 canary+全プロンプト検査)・beliefs_ledger.json・analyze_beliefs.py | 第73 |
| 規範化+コホート+ゼロ対照 | labeling.norm_stage(4段検出・markers=conf 単一源・観測のみ)・coiner/definitizer/institutionalizer 分離・下方因果解析(analyze_norms.py・閾値は引数必須)・observer.initial_frame・experiment.flat_traits(CRN 乱数消費一致・zero_traits.yaml 4セル) | 第74 |
| ダンバー認知枠 | relations.dunbar(既定 OFF・strict・乱数/LLM ゼロ)= 最外層上限51(縮約 scale 0.34・conf 化)・休眠=closeness 退避で可逆・relation_dormant/rekindle・弱い紐帯枠でのみ再会(Levin 2011)・L2 3列 | 第75 |
| DT P0 軌跡バイナリ化 | --tracks-binary(既定 OFF=既存出力バイト同一 31/31)= int16×0.05m 量子化+状態パレット+chunk sidecar 遅延ロード。viewer3d 86.1MiB→**24.7MiB(ラン長非依存)**・sim_ue 10日 0.23GB | 第76 |
| P6 追いかけ再生 | scripts/live_viewer.py(読み取り専用別プロセス・src ゼロタッチ)= part parquet 増分読み→ライブ風 HTML(_live/・JSONP差し替え)。**Windows 共有フラグ事故を発見修正**(読み中 unlink で本体 finalize が落ちる→SHARE_DELETE で開く) | 第77 |
| ablate 4種+検証装置 | ablate.llm_off / propagation_off(内容のみ遮断・捏造なし・fingerprint_risk=known 宣言・呼数差+1.6%=間接経路のみ)/ cognitive_tier / shuffle_partners(always-draw)・observer.state_hash(チェーン・T1/T6)・metrics_spec_hash(14ファイル・T7)・analyze_specialization.py(propagation_off 差分でのみ主張) | 第78 |
| Δt 不変化 | run.dt_min(既定10=構造分岐で1バイト不変・1440の約数強制)・timeconv.py=分類テーブル130キー(rate13/prob26/steps31/invariant60・棚卸し全載 CI)・Δt=5/1 スモーク済み | 第79 |
| 天候生成器 | weather.mode: synthetic(既定=不変)/ generated(較正生成器・"weather_gen" stream 一括生成=strict・resume 一致)/ table(実日付表引き)。10日窓でも10連猛暑到達可・来歴 sha256 を summary/manifest へ・**cal_day の checkpoint 欠落バグ(resume で weather 二重記録)を発見修正** | 天候W1-W2 |
| 観測チャンネル+σ | cognition.channels(既定 OFF・ON でも L1 不変=サイドカーのみ)= 14チャンネル(外界5/身体8/予測不成立1=第81枠)・measure_sigma.py→data/calib/sigma_c.json 凍結(σ=0 は床でなく除外)・較正テーブル外部化(provisional 宣言)・precision weighting+イベント分節理論の文献根拠 | 第80 |
| 閾値発火+同期バリア | cognition.fire(既定 OFF)= 認知イベントキュー((時刻,agent_id) 全順序)・発火源4種(periodic/salience/internal/social=会話・内省の第一級化)・単一作用点=_phase_drive の requesters 決定→**後方互換は厳密バイト一致**・T1 完了順序不変(workers=4 実並行含む)・T2 発火オラクル・S 寄与内訳を cog_fire に記録 | 第81 |
| watch spec+可塑性 | cognition.watch / g_update / experiment.g_init(F/N/P)= LLM が期待値 ô+DSL トリガを出力(不透明記号 c01…=因子名をプロンプトに出さない・不正は前回仕様維持)・g 更新=慣れ/感作/引き戻し(Groves&Thompson 1970・適格性トレースで感作死の退行を修正)・θ 恒常性=日境界のみ・model-revision 行(中立文言)・analyze_g.py=分散分解(生まれつき vs 創発) | 第82 |
| θ較正+発火観測 | calibrate_theta.py=θ全体スケールのみ掃引(0.03125 で f=7.90/日・誤差1.2%・凍結+dotlist 適用=src差分ゼロ)・**watch ON は27倍差=実LLM再較正が最重要**・analyze_firing.py=間隔分布/原因内訳/Kleinberg バースト/**発火連鎖グラフ**(A→B 因果候補・確度3段)/的中率・推論量見積(salience/人/日は人数不変・総呼数は不変でない=GPU外挿注意) | 第83 |
| 環境フィードバック | env.feedback(既定 OFF・strict・LLM/乱数ゼロ)= ①ホーム密度+乗降→停車延長→遅延(回復運転 γ=0.7・不動点10分に収束を実測=T5)②改札飽和→入場規制(有限解除+クールダウン・gate_capacity を初消費)③POI 占有→待ち→filter_open 除外。**環の閉じを L1 実例で実証**(待たされた本人が密度に還る)・step 末一括・congestion 既存語彙のみ | 第84 |
| Perception/Intent 契約 | cognition.contract(既定 OFF・strict)= 世界→Perception→prompt / LLM→Intent→実行の2型に結合面を限定。**ON/OFF で全プロンプト文字列まで完全一致**(無損失性の証明)・build_prompt 49引数と契約の集合一致をテスト固定・直接参照の残置リスト明示(planning.py=P3 前の第一候補)・body/salience はプロンプトに出ない構造=P3 no-fingerprint の前倒し | 第85 |
| 決定論・再現基盤 | RngHub named streams(68+)・CachedLLM(llm_cache.jsonl=応答の内容アドレスキャッシュ・D13)・golden L1 バイト一致・k非依存(controls.mode=compute_matched)・no-fingerprint | 恒常 |

## 2. 実装中・計画済み(統合実装順=確定・2026-07-31)

正典: [dual-mode-observe-verify-plan.md](docs/plans/dual-mode-observe-verify-plan.md) §2。
IDEA 系の詳細は [hackathon1-ideas-implementation-plan.md](docs/plans/hackathon1-ideas-implementation-plan.md)、
DT 系は [dt-integration-plan.md](docs/plans/dt-integration-plan.md)。

| バッチ | 内容 | 状態 |
|---|---|---|
| 第70 | IDEA①エコー計測+②未定義行動レジスタ+沈黙 | **完了**(2026-07-31 検収済み・新30テスト) |
| 第71 | LLM 入出力ジャーナル(プロンプト全文)+REPLAY fail-fast+run_manifest | **完了**(2026-07-31 検収済み・新26テスト。S0=入力来歴はユーザー承認後に manifest へ追補) |
| 第72 | 機能レジストリ(repro_tier)+ランモード observe/journal/verify | **完了**(2026-07-31 検収済み・新30テスト) |
| 第73 | 真偽台帳ミニマル(fact+信念+伝播木+検証行動+漏洩検査) | **完了**(2026-07-31 検収済み・新32テスト) |
| 第74 | 規範化ステージ+coiner/institutionalizer+コホートタグ+ゼロ対照(IDEA③④+Part E1) | **完了**(2026-07-31 検収済み・新38テスト)=**「記録しないと失われる」観測点はこれで全て投入済み** |
| 第75 | ダンバー維持コスト(IDEA⑤) | **完了**(2026-07-31 検収済み・新21テスト) |
| 第76 | DT P0 軌跡バイナリ化 | **完了**(2026-07-31 検収済み・新27テスト。ブラウザ実機の目視は未=成果物パスあり) |
| 第77 | DT P6 追いかけ再生 | **完了**(2026-07-31 検収済み・新37テスト) |
| 第78 | ablate 4種+状態ハッシュチェーン+metrics_spec_hash+指標凍結 | **完了**(2026-07-31 検収済み・新63テスト)=**統合実装順 9/9 完結**(T1〜T8 全達成) |
| 第79〜85 | **認知・時間三層・物理**([cognition-physics-plan.md](docs/plans/cognition-physics-plan.md))= 毎分レート化→σ実測→閾値発火+同期バリア→watch spec+g/θ+F/N/P(発火源は内省・会話も第一級/驚き大=世界モデル書き換え)→θ較正→環境FB→Perception契約+**物理 P2 比較(前倒し)**+**天候生成器 W1/W2** | **全完結**(2026-08-01・2536緑)。残=P3 縫合(P2 承認待ち・〜8/11)・8/12-14 フリーズ |
| 3D品質 | **3D ビューワー品質修正**(原因: OSM ドレープ解像度 1/7 頭打ち=面積33%が地形下・地下街メッシュ露出・IDW スパイク・線路/道路の非接地・sim floor 未クランプ・カプセル中心配置)→ 修正: OSM を地形メッシュ直貼り(交差構造的不可能)・TIN 重心座標補間・表示側 w クランプ・建物参照 upOf/footY 足元アンカー+サイズスライダー | **完了**(2026-08-02 検収済み・数値検証=屋根超え 531→0・線路埋没 310→0・足元Δ 3.9m→0.000m・新19テスト・2555緑。sim 側クランプは 3D-U0 のまま) |
| 3D計画 | **高精細渋谷 3D×物理接合**([highfidelity-3d-physics-plan.md](docs/plans/highfidelity-3d-physics-plan.md))— **松案で承認**(2026-08-02・竹への縮退退路つき)。**P2 決定=ゾーン別ハイブリッド**(既定 SFM・交差流=ORCA。[選定文書](docs/research/physics-engine-selection.md) P2 決定節) | **全レーン完結**(2026-08-02): レーンA データ3本(5ff56c4)→竹-3 f_iW(086dabe)→レーンB テクスチャ統合+梅塗り分け+80MBゲート内化 79.39MiB(d996240/de2f684)→**竹-4 P3境界縫合 完了**=physics.zones(排他所有・ゲート経由のみ)+orca_core 昇格(重なり対策 min_gap+0.10m)+guarded ゲート(跳び最大2.25m・accel p99 4.6=ベンチ閾値内・反転0.000)+物理→知覚(body 欄・プロンプト文字列不変)+L1 zone_gate/L2 5列/checkpoint 中央管理・実測由来の設計変更2件(通過点追跡・二重移動バグ回帰固定)・新36テスト。**残=P4 較正(高密度条件)とビューワー表示・8/12-14 フリーズ前に完了** |
| 検証ラン | **夜間実 LLM 検証ラン**(night_llm_100a3d=100体×3 sim日・production+Ollama qwen3:4b・checkpoint毎日・watchdog+live_viewer 併走) | **実行中**(2026-08-02 03:45 起動・推定 09:15 完走) |
| 次 | 観察ラン ON 構成 | **提案書提示済み**([observe-run-config-proposal.md](docs/plans/observe-run-config-proposal.md))→ OBS-U1〜U3 判断待ち・最終確定は 8/12-14(実 LLM 再較正後) |
| 並行 | DT スナップショット再提案 | **提案書提示済み**([dt-snapshot-integration-proposal.md](docs/plans/dt-snapshot-integration-proposal.md))→ DT-S1 ほか判断待ち |
| 本選後 | 場所二層知覚(IDEA⑥)・誤情報構造化フル版(IDEA⑦=ID-U2)・SUMO 反実仮想(P5)・USD/3D Tiles(DT-U4)・UE5(DT-U2 保留) | レーン3 |
| 持ち越し小粒 | analyze_sweep への llm_health 3列接続・SFM 推奨 param 昇格・D16 屋内 ON・D17 実験・4系統レーン2(B-L1 以降)・**exit_building の node 張り替えと _apply_free_action/_route_to の整合調査**(第73実行役が発見した潜在バグ疑い・スコープ外として未着手)・**pool dehydrate の関係台帳20件切りと dunbar 休眠の相互作用**(pool ON では休眠が再会前に消えやすい=本選で dunbar ON にするなら要検討・第75実行役の実測)・**3D エクスポータ側のメモリ**(reconstruct_tracks が全展開=10日ラン規模で GB 級・「ブラウザに載るか」は第76で解決済みだが「一括で組めるか」は別課題)・**WallCrowd.forces() が揺らぎ項 ξ を落としている**(壁ありで noise 完全無効を P2 比較で実測発見・P3 で決め直し要)・**サブプロセス系テストの xdist 並列フレーク2件**(test_watchdog 実 run.py スモーク・test_taxi_live SUMO ブリッジ。いずれも単体緑=serial マーカー群の付与候補・フリーズ期間に対処)・**LLM バックエンドの呼び出し全体ハードデッドライン欠落**(2026-08-02 夜間ラン実測: トークンが細々と流れ続ける病的生成では read timeout 120s が発火せず 1 呼び出しに 1 時間47分張り付いた。Ollama/vLLM 両バックエンド該当=本選前に「呼び出し開始からの絶対時限」を追加すべき。運用の暫定緩和= watchdog --stall-min 30 + flush_every_steps=12)・**竹-4 持ち越し群**(2026-08-02: ①ゾーン所有中は move_segment 不発=L1 位置再構成がゾーン通過区間で欠落(viz/tracks)②所有中 agent.node が入場ゲート値のまま=ノード基準同席(channels._place_key/ext.crowd_local)が通過中古い ③pool dehydrate が _phys_* を運ばない(現行 rotation 条件では非発火・条件変更時要対応)④span_m グラフ長 vs 物理直線の実効速度差 ⑤P4 較正は高密度条件が必要 ⑥サブステップ軌跡の記録 ⑦10日ラン ON 時は滞在分布から総サブステップ数を事前見積・planning.py 契約化は残置第一候補のまま) | 未着手 |

## 3. ユーザー判断待ち

| # | 事項 | 状態 |
|---|---|---|
| U-10 | 事前登録の閾値承認+10日ラン解釈方針 | タイミング委任済み(2026-07-31)→**第74 完了後〜第78 で承認依頼**(10日ラン 8/16 開始前) |
| PUB-U1 | 公開ミラーの .md 除外範囲+「実装を適宜 public にコミット」の運用 | **要相談**(ユーザー発意 2026-07-31)。推奨: docs/**・STATUS.md を除外し README/ETHICS/LICENSE は残す・以後は各バッチ後に publish_public_mirror.ps1 を同期実行。**注意: DT 調査でライセンス地雷2件確認**(商業施設/区サイト情報=転載不可・OSM 由来テーブル=ODbL share-alike が配布時発動)=提案書 §4 |
| NEW-5 | F/N/P 初期値条件の本選配分 | パイロット後に提案 |
| ~~P2選定~~ | 物理エンジンの選定 | **決定済み**(2026-08-02: ユーザー委任「ベンチをまわして君が決定して」→ベンチ再実行=前回と全指標ビット一致→**ゾーン別ハイブリッド**確定。[選定文書](docs/research/physics-engine-selection.md) P2 決定節) |
| OBS-U1〜U3 | 観察ラン ON 構成の承認([提案書](docs/plans/observe-run-config-proposal.md))・Δt_move 1分の扱い・認知 ON の 8/14 留保 | **新規**。推奨=§1 の ON セット+Δt=10 維持(1分は並行小ラン)+8/14 最終判断 |
| S-quick | S0/S1/S2/S5/S9(計≈1.8日・S0 は第71 相乗り)を本選前に入れるか | **新規・承認求む**(提案書 §3。入力来歴・observe.yaml 是正・バス表・実イベント表・ODD 文書) |
| 3D-U0 | **sim 側 floor クランプ**(scheduler.py で建物階数超の floor がそのまま通る=L1 が変わる修正。表示側は 2026-08-02 修正済み) | **新規**。推奨=conf トグル既定 OFF で実装し観察ランで ON |
| ~~3D-U1/U2~~ | 高精細 3D の採否 | **承認済み**(2026-08-02: **松案で実装**指示・不要になれば竹へ縮退可の方針。U3=都区部点群は調査不要のまま) |
| RW-U1 | **現実フィードバック動線**([research](docs/research/real-world-feedback.md)): ライブカメラ自動取得=不採用(YouTube 規約)・目視転記のみ可・較正3層(L0 初期条件/L1 パラメータ較正/L2 事後検証・状態同化なし)・本選中取得計画(アメダス/WBGT/JARTIC/ODPT 自動+ダッシュボード目視) | **新規・承認求む**(事前準備の登録作業は 8/5〜の期限あり=提案 §4-1) |
| SV-U1 | **サーベイ反映 18 項目**([research](docs/research/llm-social-sim-survey.md) §3)の採否。◎印=S-01 報告書 micro/macro/system 3節固定・S-02 stylized facts の事前登録追記・S-03 分散/分位列(k* 主張に直結)・S-04 主張境界の宣言・S-16 prompt_paraphrase ablate(S-quick への追加候補) | **新規**。実装コスト小の宣言系(S-01/S-02/S-04)だけでも本選前推奨 |
| DT-U2 | UE5 デモ動画 | 保留のまま(本選中判断) |

### 決定済み(2026-07-31・履歴)
NEW-2=本選 **8/15–8/30 で確定**(指示書の 8/8 は誤り)/GPU 申請・ODPT 規約確認=ユーザー側完了/
NEW-1・NEW-3=承認(検証→計画→実装。R1 柔軟化は repro_tier 方式を採用)/ID-U1=**第72(ダンバー=現第75)まで本選前**/
DT-U1=P0+P6 を本選前に実施/DT-U3=用語問題はユーザーの「スナップショット型 DT」定義の提示により**再提案タスクに置換**
(観察ランは再現性を厳密に求めない方針も同時に確定)/DT-U4=本選後先頭/ID-U2=フル版は本選後(設計文書は先行可)/
ID-U3=エコー除外は新列並記(既存列不変)/指示書ファイルの処遇=Fable 委任→docs/plans/source/ へ保存・重複1本削除。
**2026-07-31 追加決定**: NEW-4=認知プログラム大枠承認(修正3点: ①天候=同期不要・サンプリング/生成型で可
=DT-S1 はこの形で決着 ②物理=できれば本選前・直前数日は検証/調整に確保 ③発火源に内省・会話を追加・
予測誤差大は「世界モデルの書き換え」を駆動)+実装前 web リサーチ必須+体制=Fable5 計画/Opus5 実行を継続。

## 4. 設計制約(R1 ドクトリン)の現況と柔軟化

現行の恒常制約: ①新機能は既定 OFF ②既定 OFF で golden L1 バイト一致 ③k 非依存 ④no-fingerprint
⑤用途別乱数 stream ⑥観測がシムを変えない。
**2026-07-31 の方針確定**: 観察ラン(本選 10 日)は再現性を厳密に求めず、repro_tier=journal/none の機能も投入可。
検証ラン(verify)は strict のみ。この二重化は**第72で構造化済み**(registry.py+run.mode。verify モードは
planning/tools/rules=LLM 自由文が世界状態になる3機能も落とす=正直な宣言)。
既定値は現行動作のまま=golden 資産は verify 側の検収装置として恒久維持。

## 5. 受領文書の処遇(2026-07-31 確定)

二重化指示書は [docs/plans/source/](docs/plans/source/) に原文保存(dual-mode-instructions / dual-mode-instruments /
dual-mode-requirements)。リポ直下の原本3本は移動・バイト同一重複1本(instruments 1)は削除。
検証済みの統合計画は [dual-mode-observe-verify-plan.md](docs/plans/dual-mode-observe-verify-plan.md) が正典。

**2026-07-31 受領の3本**(認知・物理・DT定義)も同所へ原文保存: physics-instructions / cognition-design-record
(=設計決定の正典)/ dt-alignment-record。統合計画は [cognition-physics-plan.md](docs/plans/cognition-physics-plan.md)。
dt-alignment の方針 1-7 は大半実装済み(可視性=C0・観測層=P0/P6・差分管理=world.mod)で、新規採用は
「系譜的同一性」の自己記述語彙のみ。

**2026-08-02 受領**: リポ直下 `3800683.pdf`(Mou et al., *From Individual to Society*, ACM Computing Surveys 58(11),
2026 = LLM 社会シム・サーベイ)。**原本はユーザー管理のまま未コミット**(PDF 原本リポ外維持の掟)。
読解と反映点 18 項目は [docs/research/llm-social-sim-survey.md](docs/research/llm-social-sim-survey.md)(SV-U1)。
