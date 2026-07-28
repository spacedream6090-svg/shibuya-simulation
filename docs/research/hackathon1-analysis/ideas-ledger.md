# アイデア台帳(統合版)

> 8 体の調査エージェントが起票した **228 件**(★★★102 / ★★111 / ★15)の統合。
> 個別の詳細(内容・適用案・web リサーチ知見)は [ideas/](ideas/) の原本 8 ファイルを参照。
> **較正註記**: ★はエージェント別の判断で基準がばらつく(例: g3 は★★★を広めに付与)。
> 優先順位はこの台帳の「統合トップ提言」が正であり、複数エージェントが**独立に同じ結論へ到達したもの**を上位に置いた。

## 統合トップ提言(重複起票を統合・7 テーマ)

### T1. C 軸は文書で回収する(35.0→36.0 の最短経路)【6 エージェントが独立に合意】
- 根拠: C は総合点と最強相関(r=0.942・00 参照)。自チームの C−2.0 はほぼ全量が「将来展望」側で、
  上位 3 チームに唯一負けた軸も C だけ(02 参照)。下位でも「README に成果と展望がない」が最頻減点。
  17 位 lunar_simulation は 16,000 API コールで規範創発まで実観測しながら README に書かず C7.0 に沈んだ。
- アクション(本選提出物):
  1. README に**将来展望(ロードマップ)節**を新設 — 番号つき Phase 表+「実装済み/実装中/構想」3 列(lunar_agents C9.5 の型)。
  2. **RESULTS.md 新設** — ラン台帳+LLM 健全性列+ネガティブ結果+1 コマンド再現+出自固定表(git HEAD/モデル digest/温度/seed/予算 = report.pdf 付録 B 型)。
  3. スライドにあって README にない情報の回収(リポだけ読まれて減点された実例が複数)。
  4. プレースホルダ・`NotImplementedError` 放置の掃討(第1回 C 減点の直接原因)。

### T2. no-fingerprint の機械的証明(A 軸の防御)【5 エージェントが独立に合意】
- 根拠: A の 7〜9 点帯は「誘導がどの層に残っているか」で決まり、**審査者が実際に見る成果物に近い層ほど減点が重い**
  (本体プロンプト無誘導でも UI 用会話再生成スクリプトの語彙リストで −1.0 の実例 = hackathon-singulab-inu)。
  第1回自チームの A 唯一の減点もプロンプト内の一文だった。同一原作の対照実験(su A9.0 vs 柴田 A4.0)は
  「LLM の判断をルールと指示で置き換えた」一点で −5.0。
- アクション: 行動誘導表現の**禁止語リント(プロンプト文言のゴールデン監査)**を CI テスト化し、
  その存在自体を README/提出物の表層に載せる(「主張」を「機械的証明」に格上げ=全 31 チームの誰もやっていない)。
  監査対象はシム本体だけでなく**ビューア・レポート生成経路**まで(g3 の指紋ブラックリスト 8 パターンを語彙源に)。
  境界図(どこまでが世界の物理でどこからが LLM 判断か)を 1 枚添える。

### T3. 創発判定の反証可能な診断器+事前登録(A10 への道)【4 エージェント合意】
- 根拠: 第1回唯一の A 満点(Project_Gaara)は「認知/物理層の厳密分離」+「**データを見る前に宣言した閾値**で
  解釈/ドローンを機械判定する診断器」で取った。講評も自チームへの提言 P1 で「想定される結果のパターンの明文化」を明記。
- アクション: k* 判定の 3 信号(R² 低下・seed 発散・EWS)は実装済みなので、**本選の本ラン実行前に**
  閾値・失敗モード・想定結果パターンを日付つき文書で事前登録する(実行後では価値が消える=時間制約あり)。
  sham/null 対照は「プラセボ介入=動いてはならない対照」(near-future)の語彙で提出物に前面化。

### T4. LLM 寄与の会計と健全性観測【4 エージェント合意+report.pdf】
- 根拠: report.pdf の「画面は 30 日動いたが LLM 判断は 2 回」事件と、第1回自チームの「エラー率 83.7% が
  終わってから判明」は同じ穴。現行は L1b に呼を残すのみで **LLM 成功率/fallback 率の L2 系列がない**
  (`register_aggregator` 85 個中ヒット 0 = 01 参照)。1 位 lunar_agents は `parse_fallback_rate>0.05` で
  ラン自体を機械的に不採用にしていた。
- アクション: ①LLM 健全性 KPI(成功率/fallback 率/パース失敗率)の L2 系列化+watchdog ゲート
  ②パース失敗は独立カテゴリに隔離(fallback による分布汚染の防止) ③RESULTS.md に「LLM 寄与の会計」節
  (呼数・判断が因果へ届いた率・履行率 0.337 の類)。report.pdf の三分法(文章/画面/監査可能な因果)を提出物の構成原理に。

### T5. 研究の中身に効く輸入品(本選実験の拡張候補)
- **未定義行動(enum 外出力)の計測** — kibo_crew_sim で LLM が用意された行動空間外の `interact` を発明した実例。
  「世界を変えようとする個体」の**操作的定義の最有力候補**(捨てずに創発シグナルとして L2 化)。
- **規範化の言語形式検出器** — lunar_simulation の「survival protocol」命名→定冠詞化→`as previously discussed` で
  退出強制まで 4〜20 step。自然造語観察(coin_label)の下流に「規範化段階」の検出器を足せる。
- **命名者と制度化者の分離観測+臨界質量** — beyond-badminton の「1 体命名→翌 step 80% 採用」は
  Centola (Science 2018) の 25% 臨界質量よりはるかに低い。**LLM 集団は人間より臨界質量が低い可能性** = k* の事前予測材料。
- **初期個体差ゼロの N 体対照実験** — workplace-agent-simulation の「生まれつきを実験的に消す」セル。
  R²(k) の対照群として理論的に強力(traits 分散ゼロなら R² の分母が消える→経路依存の純度検証)。
- **初期フレームのラン単位共変量化** — kibo(初期解釈が以後全部を支配)+ mars(固着 13〜17 step)。
  k* 解釈の交絡因子として、初期数 step の解釈状態を記録し層別集計する。
- **誤情報の構造化** — Alberia の ground_truth/rumor ペア定義・truth_status 5 分類・信念強度を感情と別チャネルに。
  ラベル伝播/gossip の拡張(バックファイア効果は稀 = Wood & Porter 2019、訂正は CIE でモデル化)。
- **cheap talk 検出** — near-future の「自己申告と実挙動の乖離」測定。履行率(第 62 バッチ)と同型で、発話⇄行動の整合監査に拡張可能。
- **語彙生カウント+ヒット 0 件否定リスト** — su(fire-public)の A9.0 を支えた証拠様式。自然造語の観測報告にそのまま使える。

### T6. B 10.0 への道(実在からの逆算を名指しで語る)【3 エージェント合意】
- 根拠: B 満点 2 例の実体は lunar_agents =「実在ミッション(LUPEX/Artemis)からの逆算の明示」、
  my-social-agents =「先行理論→仮説→sweep→結果→理論への差し戻しのループが閉じている」こと。
  B は実装量ではなく素材の実在性で決まる(kibo は 1 体・README 無しで B8.0)。
- アクション: 我々は現実渋谷再現・人流実データ・ODPT・フロアガイドを既に持つ。
  **「実データ→シム内パラメータ対応表」1 枚**を README に置き、導入は外部統計から問いの必然性を作る
  (渋谷の一次統計を提出物冒頭に)。理論側は Granovetter/Centola 等の既引用文献で仮説→掃引→差し戻しの環を明示。

### T7. 提出物の様式知(細目チェックリスト)
表紙に達成率でなく観測された創発現象 / 先行研究との差分表 1 枚 / 「限界」独立節 /
「うまくいかなかった仮説」節を成功と同格に / What this is NOT 表 / 主張→証拠パス→再現コマンドの 3 列表 /
アーキテクチャ 1 枚図(mermaid) / 実験木の 1 枚図 / 代表 run の生ログ同梱 / 1,000 行超ファイルは名指しされる
(現行 `scheduler.py` 4,541 行 → 分割 seam の文書化か分割) / コード参照は行番号でなく関数名 /
「できなかった事」の正直な明記はむしろ加点方向 / ソースコード添付は絶対(未添付 2 チームはランキング除外)。
→ 個別項目は 00 の 40 点チェックリストと併用。

## 全 IDEA 索引(機械抽出)

以下は 8 ファイルからの自動抽出索引(名称 — 分類 / 出典先頭 / 原本ファイル)。詳細は各原本を参照。

### ★★★(102 件)

- **動機の決定論的分類器(world-side motive classifier)** — 実験・評価 / my-social-agents / [ideas-g1.md](ideas/ideas-g1.md)
- **realism_contract — ビューア/レポートが嘘をつかないための誓約** — 可視化 / good_echo_iss 系 / [ideas-g1.md](ideas/ideas-g1.md)
- **誘導語(effect-preloading)検出 lint — no-fingerprint の機械チェック** — 創発設計 / good_echo_iss 系 / [ideas-g1.md](ideas/ideas-g1.md)
- **非単調な外乱プロファイルで k のヒステリシスを見る** — 実験・評価 / good_echo_iss_100s / [ideas-g1.md](ideas/ideas-g1.md)
- **「相転移を見つけた」を主張の形に落とす(B 満点の型)** — 提出物・審査対策 / my-social-agents / [ideas-g1.md](ideas/ideas-g1.md)
- **制度転換の時間断続デザイン(同一個体・同一 seed でルールだけ切替)** — 実験・評価 / hackathon_ / [ideas-g1.md](ideas/ideas-g1.md)
- **governance_debate 型の「問いかけだけ」刺激で組織創発を観測** — 世界設計 / hackathon_ / [ideas-g1.md](ideas/ideas-g1.md)
- **「できなかった事」節を提出物に明示** — 提出物・審査対策 / my-social-agents / [ideas-g1.md](ideas/ideas-g1.md)
- **行動誘導リント —「状態記述は可、行動推奨は不可」** — 創発設計 / happy-to-chat / [ideas-g2.md](ideas/ideas-g2.md)
- **観測系と提示系を分離する(realism_contract)** — 可視化 / hackathon-singulab-inu / [ideas-g2.md](ideas/ideas-g2.md)
- **知覚カバレッジ率をスケール不変量にする** — 規模化・性能 / singulab / [ideas-g2.md](ideas/ideas-g2.md)
- **プロンプト冒頭の「何を固定し何を固定しないか」3 層宣言** — LLM統合 / hackathon-singulab / [ideas-g2.md](ideas/ideas-g2.md)
- **「効かないことを許可する」観測原則節(sycophancy 対策)** — LLM統合 / hackathon-singulab / [ideas-g2.md](ideas/ideas-g2.md)
- **対照条件のログを介入条件と同じ厚さで解析する** — 実験・評価 / happy-to-chat / [ideas-g2.md](ideas/ideas-g2.md)
- **A 評価(創発設計)の 3 条件チェックリスト** — 提出物・審査対策 / singulabo-hackathon / [ideas-g2.md](ideas/ideas-g2.md)
- **「率」ではなく「経路」を測る — 媒介物語彙カウント** — 実験・評価 / hackathon-singulab-inu / [ideas-g2.md](ideas/ideas-g2.md)
- **LLM 由来の方向バイアス監査と選択肢シャッフル null 対照** — 実験・評価 / singulab / [ideas-g2.md](ideas/ideas-g2.md)
- **指紋ブラックリスト(プロンプト禁止表現一覧)** — 創発設計 / G3 講評横断 / [ideas-g3.md](ideas/ideas-g3.md)
- **動機は世界に置き、プロンプトには置かない** — 創発設計 / workplace `hidden_theme` / [ideas-g3.md](ideas/ideas-g3.md)
- **行動制約を物理制約に翻訳する** — 創発設計 / ebiyama 講評提言 / [ideas-g3.md](ideas/ideas-g3.md)
- **ペルソナ属性は行動ではなく履歴とパラメータで与える** — 創発設計 / ebiyama 講評提言 / [ideas-g3.md](ideas/ideas-g3.md)
- **フェーズ分離で「答え」を発話フェーズに漏らさない** — 創発設計 / fire-public / [ideas-g3.md](ideas/ideas-g3.md)
- **変化率クランプを「世界の物理法則」として設計・明示(上下対称に)** — 創発設計 / workplace / [ideas-g3.md](ideas/ideas-g3.md)
- **イベントを ground_truth と rumor のペアで定義** — 世界設計 / Alberia / [ideas-g3.md](ideas/ideas-g3.md)
- **truth_status を 5 分類にする(実際に流れるのは「未確認」)** — 世界設計 / Alberia / [ideas-g3.md](ideas/ideas-g3.md)
- **同一事象の物理チャネルと SNS チャネルの到達範囲を独立に持つ** — 世界設計 / Alberia / [ideas-g3.md](ideas/ideas-g3.md)
- **perceive_pass / perceive_enter — 場所の知覚を二層にする** — 世界設計 / ebiyama / [ideas-g3.md](ideas/ideas-g3.md)
- **「世界の変え方」を観測可能なカテゴリに分解する** — 世界設計 / workplace / [ideas-g3.md](ideas/ideas-g3.md)
- **訂正を特権チャネルにせず一投稿として競合させる** — 世界設計 / Alberia / [ideas-g3.md](ideas/ideas-g3.md)
- **初期個体差ゼロの N 体対照実験(生まれつきを実験的に消す)** — 実験・評価 / workplace / [ideas-g3.md](ideas/ideas-g3.md)
- **「前提化指標」— 普及率でなく不使用のコストで定着を測る** — 実験・評価 / workplace / [ideas-g3.md](ideas/ideas-g3.md)
- **観察者 LLM 経由のアンケート(本人忖度バイアスの回避)** — 実験・評価 / ebiyama / [ideas-g3.md](ideas/ideas-g3.md)
- **語彙の生カウント表+「ヒット 0 件」否定リスト** — 実験・評価 / fire-public / [ideas-g3.md](ideas/ideas-g3.md)
- **実装失敗事例カタログを予防チェックリスト化** — 実験・評価 / ebiyama(事象 A〜F) / [ideas-g3.md](ideas/ideas-g3.md)
- **LLM の自己反復を「計測して伝播から除外」する** — 実験・評価 / ebiyama / [ideas-g3.md](ideas/ideas-g3.md)
- **「起きなかった」を一次データとして提示** — 実験・評価 / Alberia / [ideas-g3.md](ideas/ideas-g3.md)
- **ラベルごとの信念強度を感情と別チャネルで持つ** — メモリ / Alberia / [ideas-g3.md](ideas/ideas-g3.md)
- **情報源別の減衰率とユニーク報告者追跡** — メモリ / 柴田 fire / [ideas-g3.md](ideas/ideas-g3.md)
- **Canonical ID による実体同一性の回復(正規化は観測側だけが知る)** — メモリ / 柴田 fire / [ideas-g3.md](ideas/ideas-g3.md)
- **「安全な最適化」と「危険な最適化」の区別** — 規模化・性能 / fire 2 本の対照 / [ideas-g3.md](ideas/ideas-g3.md)
- **通信グラフからの役割の事後 induction(観測器として分離)** — 可視化 / 柴田 fire / [ideas-g3.md](ideas/ideas-g3.md)
- **否定空間のロギング(拾えなかった声/発話しなかった記録)** — 可視化 / workplace / [ideas-g3.md](ideas/ideas-g3.md)
- **先行研究との差分表を README に 1 枚** — 提出物・審査対策 / Alberia(Epstein 2002 比較) / [ideas-g3.md](ideas/ideas-g3.md)
- **スライドにあって README にない情報を回収** — 提出物・審査対策 / workplace / [ideas-g3.md](ideas/ideas-g3.md)
- **「将来展望」セクションは必ず置く** — 提出物・審査対策 / G3 の 3 チーム同時減点 / [ideas-g3.md](ideas/ideas-g3.md)
- **「限界」セクションを独立に立てる** — 提出物・審査対策 / workplace / [ideas-g3.md](ideas/ideas-g3.md)
- **表紙に達成率を置かない — 置くのは観測された創発現象** — 提出物・審査対策 / 柴田 fire / [ideas-g3.md](ideas/ideas-g3.md)
- **設計原則の根拠コメントをプロンプト断片の隣に置く** — 提出物・審査対策 / fire-public / [ideas-g3.md](ideas/ideas-g3.md)
- **決定論・シード・テストを差別化点として明示** — 提出物・審査対策 / G3 横断 / [ideas-g3.md](ideas/ideas-g3.md)
- **倫理的注意セクション(実在渋谷だからこそ)** — 提出物・審査対策 / Alberia / [ideas-g3.md](ideas/ideas-g3.md)
- **規範化の言語形式検出器(定冠詞化・as previously discussed)** — 創発設計/実験・評価 / lunar_simulation / [ideas-g4.md](ideas/ideas-g4.md)
- **未定義行動(enum 外出力)を創発シグナルとして計測** — 創発設計/実験・評価 / kibo_crew_sim / [ideas-g4.md](ideas/ideas-g4.md)
- **ペルソナ文言の行動指示棚卸し(環境と役割の no-fingerprint は別物)** — 創発設計 / ai-homecare 他 / [ideas-g4.md](ideas/ideas-g4.md)
- **決定論部分と LLM 判断部分の境界を先に説明する** — 創発設計 / all-in-smoke 他 / [ideas-g4.md](ideas/ideas-g4.md)
- **設定ファイルのヘッダに実験プロトコルを書く(2×2 表・RQ)** — 実験・評価 / beyond-badminton / [ideas-g4.md](ideas/ideas-g4.md)
- **集計方法の明文化+生ログ同梱で第三者再計算可能に** — 実験・評価 / beyond-badminton / [ideas-g4.md](ideas/ideas-g4.md)
- **初期フレームをラン単位共変量として記録し層別集計** — 実験・評価 / kibo_crew_sim / [ideas-g4.md](ideas/ideas-g4.md)
- **「命名者」と「制度化者」を分けて観測(coiner vs institutionalizer)** — 実験・評価 / beyond-badminton / [ideas-g4.md](ideas/ideas-g4.md)
- **数値を隠して「気分ラベル」だけ渡す(mechanical self-correction 回避)** — メモリ/LLM統合 / all-in-smoke / [ideas-g4.md](ideas/ideas-g4.md)
- **3 レイヤー構造(Environment/Nudge/Agent)説明フレーム** — 提出物・審査対策 / all-in-smoke / [ideas-g4.md](ideas/ideas-g4.md)
- **実データを提出物の冒頭に置く** — 提出物・審査対策 / G4 横断 / [ideas-g4.md](ideas/ideas-g4.md)
- **成果は README(提出物の入口)に置く** — 提出物・審査対策 / lunar_simulation / [ideas-g4.md](ideas/ideas-g4.md)
- **プロンプト行動指示検出器(no-fingerprint の機械的証明)** — 提出物・審査対策 / spring-park / [ideas-g5.md](ideas/ideas-g5.md)
- **観測対象語のプロンプト混入禁止(measurement contamination 遮断)** — 実験・評価 / mars / [ideas-g5.md](ideas/ideas-g5.md)
- **提出前「審査軸→実在ファイル」対応表チェック** — 提出物・審査対策 / risk-gap(gitignore 事故) / [ideas-g5.md](ideas/ideas-g5.md)
- **相補的 KPI(線形従属列)の検出** — 実験・評価 / psychology / [ideas-g5.md](ideas/ideas-g5.md)
- **パース失敗を独立カテゴリに隔離(fallback 分布汚染の防止)** — LLM統合 / psychology / [ideas-g5.md](ideas/ideas-g5.md)
- **死んだ状態変数の検出(プロンプト掲載変数の実動テスト)** — 実験・評価 / psychology / [ideas-g5.md](ideas/ideas-g5.md)
- **トートロジー回避の明示(sham/null 対照を前面に)** — 実験・評価 / meta-pop-agent / [ideas-g5.md](ideas/ideas-g5.md)
- **エージェント間の情報到達経路を 1 枚図に** — 提出物・審査対策 / G5 横断 / [ideas-g5.md](ideas/ideas-g5.md)
- **README 単体完結チェック** — 提出物・審査対策 / psychology(README 不在 C4.0) / [ideas-g5.md](ideas/ideas-g5.md)
- **LLM なしで動くモックモードを README トップに** — 提出物・審査対策 / agi-job / [ideas-g5.md](ideas/ideas-g5.md)
- **マクロ分布とミクロの語りを 1 画面に(k スライダー付きビューア)** — 可視化 / agi-job / [ideas-g5.md](ideas/ideas-g5.md)
- **固着(stuck)を LLM の普遍的失敗モードとして計測** — 実験・評価 / mars / [ideas-g5.md](ideas/ideas-g5.md)
- **外れ値ランの解剖(初期条件 1 ビットがラン全体を凍結)** — 実験・評価 / mars / [ideas-g5.md](ideas/ideas-g5.md)
- **小サンプルの効果量を信用しない(パイロット数字を確定と書かない)** — 実験・評価 / mars / [ideas-g5.md](ideas/ideas-g5.md)
- **提出前セルフ採点(40 点チェックリストの機械的照合)** — 提出物・審査対策 / SKILL.md / [ideas-misc.md](ideas/ideas-misc.md)
- **no-fingerprint 自動監査を「提出物の表層」に載せる** — 提出物・審査対策 / SKILL.md A 軸 / [ideas-misc.md](ideas/ideas-misc.md)
- **創発を「反証可能に」判定する診断器を持つ** — 実験・評価 / Project_Gaara / [ideas-misc.md](ideas/ideas-misc.md)
- **番号つき段階的ロードマップで C の「将来展望 5 点」を回収** — 提出物・審査対策 / lunar_agents / [ideas-misc.md](ideas/ideas-misc.md)
- **設計意図を「採点者が読む場所」に置く** — 提出物・審査対策 / SKILL.md Phase 0 / [ideas-misc.md](ideas/ideas-misc.md)
- **ソースコード添付の絶対規則(派生物でも差分は必ず出す)** — 提出物・審査対策 / 未評価 2 チーム / [ideas-misc.md](ideas/ideas-misc.md)
- **実在ミッション/実データからの「逆算」で B=10 を狙う** — 世界設計 / lunar_agents / [ideas-misc.md](ideas/ideas-misc.md)
- **主張の裏取り表(claim → file:line)を提出物に添付** — 提出物・審査対策 / SKILL.md / [ideas-misc.md](ideas/ideas-misc.md)
- **ラン中 LLM 健全性 KPI の L2 系列化と watchdog ゲート** — 実験・評価/規模化・性能 / 自チーム講評 / [ideas-own.md](ideas/ideas-own.md)
- **README「将来展望(ロードマップ)」節の新設** — 提出物・審査対策 / 自チーム講評 C / [ideas-own.md](ideas/ideas-own.md)
- **RESULTS.md 新規作成(ラン台帳+成功率列+ネガティブ結果)** — 提出物・審査対策 / 公式サイト+講評 / [ideas-own.md](ideas/ideas-own.md)
- **「想定される結果のパターン」の事前登録** — 実験・評価 / 講評提言 P1(実行前限定) / [ideas-own.md](ideas/ideas-own.md)
- **プロンプト文言のゴールデン監査(行動誘導の禁止語リスト)** — 創発設計 / 自チーム講評 A / [ideas-own.md](ideas/ideas-own.md)
- **「実装したのに評価されていない強み」を README に列挙** — 提出物・審査対策 / 検証レポート見落とし欄 / [ideas-own.md](ideas/ideas-own.md)
- **README を「問い+対照群+創発指標+主張しないこと」の 4 節に** — 提出物・審査対策 / 上位 3 共通 / [ideas-top3.md](ideas/ideas-top3.md)
- **ロードマップ 1 枚+「実装済み/実装中/構想」3 列表** — 提出物・審査対策 / lunar_agents / [ideas-top3.md](ideas/ideas-top3.md)
- **「What this is NOT」表を提出物に** — 提出物・審査対策 / Project_Gaara / [ideas-top3.md](ideas/ideas-top3.md)
- **「うまくいかなかった仮説」節を成功例と同格に** — 提出物・審査対策 / Project_Gaara / [ideas-top3.md](ideas/ideas-top3.md)
- **創発判定の閾値と失敗モードをデータを見る前に宣言** — 実験・評価 / Project_Gaara / [ideas-top3.md](ideas/ideas-top3.md)
- **観測の信頼性をラン採否の機械判定に(parse_fallback_rate ゲート)** — 実験・評価 / lunar_agents / [ideas-top3.md](ideas/ideas-top3.md)
- **自己申告と実挙動の乖離(cheap talk)を別々に測る** — 実験・評価 / near-future / [ideas-top3.md](ideas/ideas-top3.md)
- **プラセボ介入(動いてはならない対照)を実験設計に** — 実験・評価 / near-future / [ideas-top3.md](ideas/ideas-top3.md)
- **残存する行動誘導文を環境コストへ置換(「世界を変える、言葉を変えない」)** — 創発設計 / lunar_agents / [ideas-top3.md](ideas/ideas-top3.md)
- **認知層と物理層の分離を docstring で 1 文宣言** — 創発設計 / Project_Gaara / [ideas-top3.md](ideas/ideas-top3.md)
- **reflection を「継続 or 変更」の二値決定に強制** — メモリ / lunar_agents / [ideas-top3.md](ideas/ideas-top3.md)
- **世界設定を「どの実在制度から逆算したか」で語る** — 世界設計 / lunar_agents B10 / [ideas-top3.md](ideas/ideas-top3.md)

### ★★(111 件)・★(15 件)

原本参照: [ideas-g1.md](ideas/ideas-g1.md)(17+2) / [ideas-g2.md](ideas/ideas-g2.md)(16+3) /
[ideas-g3.md](ideas/ideas-g3.md)(12+1) / [ideas-g4.md](ideas/ideas-g4.md)(18+1) /
[ideas-g5.md](ideas/ideas-g5.md)(14+1) / [ideas-misc.md](ideas/ideas-misc.md)(7+0) /
[ideas-own.md](ideas/ideas-own.md)(6+2) / [ideas-top3.md](ideas/ideas-top3.md)(21+5)。
代表例: 実験仕様を conf に宣言(good_echo)・ダンバー数 LRU 忘却(singulab)・エコー指標常設 KPI(singulab)・
プロンプトキャッシュ静的/動的分離+cache hit 計測(ebiyama 81.4%)・「死」を第一級イベントに(near-future)・
温度を下げずに再現性(per-call シード・near-future)・実行中ランの別 LLM 途中診断(lunar_agents)・
JS ダイバージェンス創発指標(lunar_agents)・保存量と参照量の分離(fire-public)・
「何もしない」を行動選択肢に明示(workplace)・介入と別イベントを隣接させない(goodecho_r の交絡)。

## 採用判断について

本台帳は**記録**であり、実装・提出物への反映は別途ユーザーと合意して着手する
(standing rule: 拡張実装前に必ず確認)。時間制約があるのは T3 の事前登録
(本選ランの**実行前**でないと価値が消える)と、提出締切 8/30 に向けた T1/T2/T7 の文書系。
