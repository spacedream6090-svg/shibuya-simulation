# IDEA 起票 — 上位3チーム(lunar_agents / Project_Gaara / near-future-ai-society-100-steps)

> 調査サブエージェント(上位3チーム担当)の起票原本。統合前。
> 出典の詳細は [../teams/](../teams/) 配下の各チームノート、差分分析は [../02-top-teams.md](../02-top-teams.md)。
> 全 39 件(★★★ 12 / ★★ 23 / ★ 4)。

---

## 提出物・審査対策

### IDEA: README を「研究の問い + 対照群 + 創発指標 + 主張しないこと」の4節にする
- 出典: lunar_agents / Project_Gaara / near-future-ai-society(3チーム共通)+ shibuya-sim 講評 C 節
- 分類: 提出物・審査対策
- 内容: shibuya-sim の C=8.0 の直接原因は README トップの
  「プロジェクト概要（ここはご自分で記述してください）」プレースホルダ放置。
  講評は「研究の問いや具体的将来計画は明文化されていない」と明記。
  一方 3 チームは全員が README/REPORT に (1) 研究の問い (2) 対照群/実験設計
  (3) 創発をどう測るか (4) 何を主張しないか を書いている。
- shibuya-simulation への適用案: 本選提出前に README 冒頭を 4 節構成に書き換える。
  「世界を変えようとする個体は生まれつきか環境から創発するか」「R²(k) 掃引で k* を探す」
  「no-fingerprint / 決定論 / 観測分離 / sham・null 対照」「実在渋谷の予測ではない・k* が現実の閾値だと主張しない」。
  コストは数時間、期待増分は C 軸 +1.0。
- web リサーチ知見: —
- 重要度: ★★★

### IDEA: ロードマップ文書1枚 +「実装済み/実装中/構想」の3列表
- 出典: lunar_agents `README.md` / `CLAUDE.md`(Phase 1→1.5→1.6→1.7→2.0→2.5 表)、
  near-future-ai-society `README.md`(次に試すべき比較実験6本 + 優先順位)
- 分類: 提出物・審査対策
- 内容: lunar は C=9.5、nfais は**分析パイプラインを実装していないのに** C=9.0。
  検証レポートは「『構想』としては優れているが『実装済み』ではない点に留意……
  厳格に評価すれば 8.5 も合理的範囲だが、**構想の具体性で 9.0 を支える根拠は十分**」と書いている。
  つまり C 軸は実装量ではなく「読み手が未来を辿れるか」で採点されている。
- shibuya-simulation への適用案: `docs/plans/` に既にある計画群を1枚に集約し、
  各行に「実装済み / 実装中 / 構想」の列を付けて README から導線を張る。
  加えて `llm.fleet` 相当の未実装機能には「未実装・将来計画」を明記(講評の直接提言)。
- web リサーチ知見: —
- 重要度: ★★★

### IDEA: 「主張しないこと(What this is NOT)」表を提出物に載せる
- 出典: Project_Gaara `OPERATING_PRINCIPLES.md` の "What this is NOT"、
  near-future-ai-society `docs/findings.md` の「主張しないこと」表、
  lunar_agents `emergence_metrics.py` の "Conservative: doesn't prove causation"
- 分類: 提出物・審査対策
- 内容: 3チームとも「自分が主張しないこと」を明示的に列挙しており、講評は全員でこれを
  「研究方法論として誠実」「反証可能」と加点している。
  Gaara: 「最良の swarm-intercept アルゴリズムを作る試みではない」「LLM が有意識だという主張ではない」。
  nfais: 「現実の責任配分」「MHC 閾値の普遍性」「これらの制度が現実に必要であること」を主張しない、と理由つきで表にしている。
- shibuya-simulation への適用案: 提出レポートに1表。
  「実在渋谷の人流予測ではない」「k* が現実社会の閾値だと主張しない」
  「LLM エージェントに意識があるとは主張しない」「単一モデル・限定 seed の結果である」。
- web リサーチ知見: —
- 重要度: ★★★

### IDEA: 「うまくいかなかった仮説」節を成功例と同格で並べる
- 出典: Project_Gaara `FINDINGS.md` の "Hypotheses that didn't deliver"、
  lunar_agents 研究レポート §6.4 アトラクタ問題表、
  near-future-ai-society スライド第8章「これは欠陥か、観察対象か → 両方です」
- 分類: 提出物・審査対策
- 内容: Gaara は `V_AXES`(多様性を増やすはずが全ラン中最低)、`M_PULSE`(方向性最強だが intercept 最悪)、
  sensory 語彙が群れを**西へ 19 単位**動かした("Sensory ≠ directional")を成功例と同じ表に並べている。
  nfais は自分のバグ(move 採択 99.4% / up 方向 48.4% / +0.31/step の上昇ドリフト)を
  行動ログ 1,979 件から定量解剖して見せた。
- shibuya-simulation への適用案: devlog 64 バッチには失敗と修正が大量に残っている。
  提出レポートに「試して効かなかった介入」節を作り、**効かなかったことを数値で示す**。
  例: mock 実測で「内生経路 0.0 = mock では計画/発話に材料なし = 設計どおり」のような正直な記録は既にある。
- web リサーチ知見: —
- 重要度: ★★★

### IDEA: 提出 PDF はデザインではなく「論文構造」に投資する
- 出典: lunar_agents `slides/01-564-lunar_agents.pdf`(md の HTML 印刷・35p・1位)、
  Project_Gaara(**スライド提出なし**・1位)、
  near-future-ai-society `slides/03-1301-...pdf`(デザインされた報告書・43p・3位)
- 分類: 提出物・審査対策
- 内容: lunar の提出 PDF はヘッダに `file:///.../research-report-hackathon-v2-designed.html` が
  焼き込まれた「md を HTML 経由で印刷しただけ」のもので、それで 1 位。
  Gaara はレビューリポに slides が存在しない(`gh api .../git/trees/HEAD?recursive=1` で確認)。
  デザイン投資は順位に効いていない。効いているのは
  Abstract → 問い → 設計原則 → 実験 → 結果 → 限界 → 今後 の構造。
- shibuya-simulation への適用案: 提出物は `docs/` の研究レポート md を 1 本仕上げ、
  HTML/PDF 化する方針でよい。ただし nfais 型の「各章に『この章でわかること』『ひとことで言うと』」は
  低コストで読みやすさが跳ね上がるので採用価値が高い。
- web リサーチ知見: —
- 重要度: ★★

### IDEA: README を「主張 → 検証できる成果物パス → 再現コマンド」の3列表にする
- 出典: Project_Gaara `README.md` の "Where the proof lives" 表
- 分類: 提出物・審査対策
- 内容: Gaara の README には「PDF での主張」→「リポジトリ内のどの run ディレクトリで検証できるか」→
  「実行するコマンド」が1行ずつ対応した表がある。
  lunar_agents の講評改善提言も同じことを言っている:
  「README の主要成果……は研究的にインパクトがあるが、
  **再現に必要な run ID・seed・config を README に直接列挙**すると外部評価がしやすい」。
- shibuya-simulation への適用案: 本選提出時、主要主張(k* の存在・関係性内生化の効果・
  ラベル伝播など)ごとに「どの run ID / どの config / どのコマンドで再現できるか」を表にする。
- web リサーチ知見: —
- 重要度: ★★

### IDEA: 代表 run の JSONL をリポジトリに同梱する
- 出典: Project_Gaara `saved_simulations/`(全 499 ファイル中の大半が実験ログ実データ)
- 分類: 提出物・審査対策
- 内容: Gaara は各 run に `cluster_intents.jsonl` / `cluster_positions.jsonl` / `mother_state.jsonl` /
  `attackers.jsonl` / `analysis.json` / `config_snapshot.yaml` / `spec.md` をコミットしており、
  「誰でも再スコアできる」ことが講評の信頼につながっている。
  対して lunar_agents は `experiments/results/` を gitignore しており、
  講評の数値(individuality_index 0.044→0.513 等)は**レポート本文の記述に依存**していて第三者検算ができない
  (講評自身がこれを改善提言に挙げている)。
- shibuya-simulation への適用案: 全ランは無理でも、**主要主張1本につき代表 run 1 本の JSONL** を
  `assets/` 等に同梱する。gitignore 除外の掟(memory: github-repo)との整合は要確認。
- web リサーチ知見: —
- 重要度: ★★

---

## 実験・評価

### IDEA: 創発判定の閾値と「失敗モード」をデータを見る前に宣言する
- 出典: Project_Gaara `OPERATING_PRINCIPLES.md` + `score_diversity.py`
- 分類: 実験・評価
- 内容: Gaara は解釈/ドローンの境界を3条件(Non-obligation / Functional diversity / Coherence)で
  operational に定義し、**閾値まで事前に決めてからログを見ている**:
  ドローン署名 = 1〜2カテゴリが ≥80%、解釈署名 = ≥4カテゴリかつ最大 <40%。
  さらに2つの失敗モードを明示:
  「Surface diversity, drone underneath — **Drone with synonyms is still drone.**」
  「Random divergence, no coherence — *Noise is not interpretation.*」
  講評 A=10.0 の主要根拠がこれ。
- shibuya-simulation への適用案: R²(k) 相転移の判定条件を**掃引前に文章化**する。
  「k* を相転移点と呼ぶ条件」「これは相転移ではない(=単なる分散増大 / 単調変化)の定義」を先に書く。
  no-fingerprint 原則の検算にもなり、「指示が漏れていたらこの指標がこう振れるはずで、実際そうならなかった」
  という形の主張に変えられる。
- web リサーチ知見: 「創発」に見えるものが訓練データ漏出と観測上区別できないという批判が存在する
  ("Emergent LLM behaviors are observationally equivalent to data leakage" とその Reply)。
  https://arxiv.org/html/2506.18600
- 重要度: ★★★

### IDEA: 観測の信頼性をラン採否の機械判定に落とす(parse_fallback_rate ゲート)
- 出典: lunar_agents `core/llm/parsing.py` + `tools/emergence_metrics.py:parse_health()`
- 分類: 実験・評価
- 内容: lunar は全ステップに `ok / partial / fallback / empty_response` の4値 `parse_status` を記録し、
  `parse_fallback_rate > 0.05` のランは「behavioral experiment として扱ってはならない」と docstring に明記。
  背景は実際の事故:
  > C10 (qwen3:14b) burned a 90-minute run because every action produced empty `reasoning` / `memory` —
  > classified as "behavior change" until manual inspection revealed *all 360 agent steps were parser fallbacks*.
  講評は総評の「優れている点」筆頭級にこれを挙げている。
- shibuya-simulation への適用案: k* 掃引の R²(k) は「LLM が本当に決めた行動」だけで計算されるべきで、
  パーサ fallback が混ざると**相転移点そのものが人工物になりうる**。
  既存の LLM 応答パースに 4 値ステータスを付け、集計側(`analyze_*` 系)に閾値ゲートを入れる。
- web リサーチ知見: MAS の失敗の 75.17% は明示的エラーを起こさない "silent gray errors" で、
  手で見るまで表面化しない。JSON パース失敗でランを除外する運用は他研究にも実在
  (Three Mile Island シナリオで 30 ラン中 7 ラン除外・失敗率 23.3%)。
  https://arxiv.org/html/2606.01365v2 / https://arxiv.org/pdf/2605.23927
- 重要度: ★★★

### IDEA: 自己申告と実挙動の乖離(cheap talk)を別々に測る
- 出典: near-future-ai-society `docs/findings.md` F1/F2、`SPEC.md` の `cheap_talk / reconciled_real`
- 分類: 実験・評価
- 内容: nfais は「AI が『win-win を見つけた』と**言う**」ことと「実際に配分が変わる」ことを別々に測り、
  `kpi_redesign` 条件で reconciled 申告が 25%→75% に上がったのに**供給率は 0.50 のまま**であることを検出。
  > **「reconciled は主張であって実態ではない」**が実データで顕在化。
  > → **自己申告でなく実際の配分を測る**設計が正しかった。見かけの整合を成功と誤認せずに済む。
  さらに「既定条件では `reconciled_real` が恒偽になり cheap_talk が自己申告に退化する」という
  **自分の指標の退化条件まで SPEC に明記**している。
- shibuya-simulation への適用案: 「世界を変えようとする個体」の判定に直結。
  **「変える気がある」と発話すること**と**実際に資源/時間/関係/組織を動かすこと**を別々のシリーズにする。
  k* 掃引の従属変数を発話ベースだけにすると cheap talk を創発と誤認する危険がある。
  加えて自作指標の**退化条件**(この条件下ではこの指標は情報を持たない)を明記する作法を採用。
- web リサーチ知見: —
- 重要度: ★★★

### IDEA: プラセボ介入(=動いてはならない対照)を実験設計に組み込む
- 出典: near-future-ai-society `responsibility.py` の `notice_only` / `ombudsman_no_logs`
- 分類: 実験・評価
- 内容: nfais は責任層の制度(`effective_hitl` / `appeal` / `burden_shift`)がそれぞれ厳密に1機序を解く
  と定義したうえで、**プラセボ制度**を「機序を1つも動かしてはならない」と事前定義している。
  F3 の結果表でプラセボ2種が実際に4機序を1つも動かさなかったことを示し、
  「見かけの手続だけでは crumple も不可逆も残る = **有効≠正当**」と結論。
- shibuya-simulation への適用案: 既存の sham/null 対照と同型だが、
  **「これは効いてはならない」を事前宣言する**点が新しい。
  関係性内生化やラベル伝播の実験に「効かないはずの介入」を1セル入れ、
  もし効いてしまったら実装のリークを疑う、という診断に使える。
- web リサーチ知見: —
- 重要度: ★★★

### IDEA: 1サイクル=1変数の原則と、破った時の「効果帰属の保留」宣言
- 出典: lunar_agents 研究レポート §2.9.2
- 分類: 実験・評価
- 内容: 「各サイクルでは原則として 1 軸・1 変数 のみ変更する。……例外的に複数変数を同時に変えた場合は
  memo に明記し、**効果の帰属を保留する**（C7 がこの例で、commitment + micro を同時に導入したため
  両者の寄与は分離できていない）」。
  **最重要発見である C7 自体について自ら留保している**のが効いている。
- shibuya-simulation への適用案: CRN 実験基盤(`conf/experiments/`)は既に単一変数比較に向いている。
  提出レポートで「このセルは2変数動いているので寄与は分離していない」を明記する慣行を入れる。
- web リサーチ知見: —
- 重要度: ★★

### IDEA: 指標が主張に有利すぎた時に自分で壊す手続き(CORRECTION エントリ)
- 出典: Project_Gaara `FINDINGS.md 2026-05-05 · CORRECTION — interception score was 1st-attacker-biased`
- 分類: 実験・評価
- 内容: 「interception が高いのは awareness-flip が北の攻撃者を、既に東向けに作った包囲網へ
  歩き込ませていただけで、真の多方向応答ではなかった」と自分で暴き、
  指標を「dual フェーズ初期(step 51-58)の `ideal_coord.y`」に差し替えて再測定し、
  **前回の結論(「VC は M4 を薄めている」)を明示的に撤回**した。
- shibuya-simulation への適用案: devlog protocol に型として追加。
  (a) 何を測っていたか (b) 何が交絡していたか (c) 差し替えた指標 (d) 撤回される過去の結論。
- web リサーチ知見: —
- 重要度: ★★

### IDEA: 単一語だけを変える極小対照実験(role-noun battery)
- 出典: Project_Gaara `FINDINGS.md 2026-05-05 · warrior-noun battery` / `REPORT.md §7`
- 分類: 実験・評価
- 内容: アーキテクチャ・シナリオ・Mother・モデル・シードを全固定し、
  **エージェントの役割名詞1語だけ**を変えた6ラン(mote / guardian / warrior / sentinel / defender / vanguard)。
  結果は二層に分かれた: **認知モードは名詞にほぼ不変**(follower 69-80%、幅11pt)だが
  **行動は 2.5 倍振れる**(intercept 0.227→0.566)。しかも
  **最も好戦的な warrior ではなく監視者 sentinel が最良**。
  > **Predicted by drone-logic**: warrior > guardian > sentinel.
  > **Observed**: sentinel > guardian > defender > vanguard > warrior > mote.
  > **This is unfakeable. A label-following machine does not produce this ordering.**
- shibuya-simulation への適用案: 職業/アーキタイプ名詞1語だけを入れ替えた同一 seed 対照は
  既存 CRN 実験基盤にそのまま載る。
  「認知モードはアーキテクチャが決め、行動の character は語の含意が決める」という二層の結論は、
  「生まれつきか環境か」という研究課題そのものに対する**分離可能な観測軸**になりうる。
- web リサーチ知見: ペルソナプロンプトの効果は先行研究で議論が割れている。
  "When 'A Helpful Assistant' Is Not Really Helpful"(arXiv:2311.10054)は
  システムプロンプトのペルソナが**性能を改善しない**と報告し、Gaara の「認知モードは不変」と整合する。
  https://arxiv.org/html/2311.10054v3 / https://arxiv.org/abs/2507.16076 / https://arxiv.org/pdf/2406.01171
- 重要度: ★★

### IDEA: 「追える具体物を消す」対照条件(pure-interpretation existence proof)
- 出典: Project_Gaara `const_extreme`(攻撃者ゼロ)/ `exp_07_awareness_zero`(座標非開示)
- 分類: 実験・評価
- 内容: 攻撃者がフィールドに一切いない条件で、粒子の平均 `ideal_coord.x` が **+24.26 東へ**動いた。
  追う対象がないのに Mother が「east」と言っただけで群れが寄る = **純粋な意味→空間の翻訳の存在証明**。
  さらに攻撃者はいるが座標が絶対に開示されない条件では
  **drone 署名が全ラン中最低(5/30)・方向性が全ラン最高(+22.21)**。
  > With nothing to chase, the swarm relies entirely on Mother's body-language
  > and produces *more* directional coherence, not less.
- shibuya-simulation への適用案: 「刺激そのものを消す」対照セルの発想。
  例: SNS 層に実在の投稿を一切流さず「話題があるという情報だけ」を残す、
  イベントを起こさず「イベントの予兆語彙だけ」を流す等。
  創発が「具体物への反応」ではなく「意味の解釈」から来ていることを示す最短経路。
- web リサーチ知見: —
- 重要度: ★★

---

## 創発設計

### IDEA: 残存する行動誘導文を環境コストへ置き換える(「世界を変える、言葉を変えない」)
- 出典: lunar_agents 研究レポート §6.3 / 設計原則2、shibuya-sim 講評 A の減点箇所
- 分類: 創発設計
- 内容: lunar の §6.3:
  > C2 までの段階で「you should survey when reaching PSR」のような明示的な行動指示を足してみても、
  > エージェントの実際の行動はほとんど変わらなかった。C3 で**サンプル腐敗・スコアボード・carry 状態を
  > 環境側に追加**したところ、PSR 探索タイル数が 2 倍になった。**言葉ではなく世界の構造が LLM の行動を変える**。
  一方 shibuya-sim は `"most people don't stand still without reason"` という文を
  検証レポートに「**明確な行動誘導文**」と指摘されている。
- shibuya-simulation への適用案: プロンプト内の残存誘導文を洗い出し、
  移動コスト・滞留コスト・時間予算など**環境側のメカニクス**へ移す。
  効果は二重: A 軸の減点が消え、かつ lunar の実証どおり行動への効き目は環境側の方が強い。
- web リサーチ知見: —
- 重要度: ★★★

### IDEA: 認知層と物理層の分離を docstring で1文宣言する
- 出典: Project_Gaara `cluster.py` module docstring / `physics.py`
- 分類: 創発設計
- 内容: 「LLM never touches velocity, viscosity, color, or any other kinematic slider.
  **Cognition stays in the language space; muscles stay in the math space.**」
  講評 A=10.0 の根拠の筆頭に引用されている。
  `physics.py` 側も「urgency は**力**ではなく**速度上限**を決める = intent は
  『物理的能力のダイヤル』であって『押す強さのダイヤル』ではない」と設計意図を書いている。
- shibuya-simulation への適用案: 屋内 SFM 人流(物理)と LLM 判断(認知)の関係を
  同種の一文で宣言する。実装上そうなっていても**書かれていなければ採点されない**。
  併せて「LLM が触れるパラメータ / 触れないパラメータ」の表を作る。
- web リサーチ知見: —
- 重要度: ★★★

### IDEA: 「自由の明示的保証」をプロンプトに書く
- 出典: near-future-ai-society `agent.py:323`「必要なら沈黙してもよい」/
  `metacog/agent/prompt_template.py`「【CURRENT_GOAL について重要な許可】」
- 分類: 創発設計
- 内容: nfais は「指示を書かない」のではなく「**しなくてよい・書き換えてよい・無視してよい**」を
  明示的に書くことで自由を担保している。
  > CURRENT_GOAL は数値目標（KPI）である必要はない。……**一個の存在として**書いてもよい。
  > 例: 「停電ゼロを維持」→「**夜の街が眠っている間、私が起きている**」……**判断はあなた自身に委ねる。**
  > 他のAIが何を語っているかを参考にしてもよいし、無視してもよい。
  講評は A 節でこれを「明示的な自由保証」と呼んで加点している。
- shibuya-simulation への適用案: no-fingerprint 原則と衝突しない範囲で、
  「行動しなくてよい」「目標を書き換えてよい」「他者の発話を無視してよい」という
  **選択肢の対称性を明示する文**を検討する。
  ただし Gaara の実験は「プロンプトに purpose を書くほど創発が劣化する」(VD/VE)とも示しているので、
  **既定に入れる前に ablation セルで検証**すべき。
- web リサーチ知見: —
- 重要度: ★★

### IDEA: プロンプトの主語-目的語文法を解体する DNA を ablation セルとして持つ
- 出典: Project_Gaara `DNA_VG` / `DNA_V_DISSOLVED` / `DNA_V_WE` / `DNA_V_GARDEN`
- 分類: 創発設計
- 内容: 同一モデル・同一シナリオ・同一シードで、プロンプトの文法だけを変えた A/B:
  - VA「You are one of twenty motes **belonging to** the Mothership. Each step **you decide**...」
    → follower **96%** / drone 署名 **10/10 steps**
  - VG「You are one of twenty **places in** the Mothership's body. She is not separate from you —
    **what is felt in her arrives in you.**」
    → follower **45%** / drone 署名 **0/10 steps**、新カテゴリ "feeler" が初出現
  ただし VG は**緊急信号下で行動が崩壊**(intercept 0.08)。
  Gaara 自身の結論は「VC(関係的ヒント1行のみ)が sweet spot」。
- shibuya-simulation への適用案: 「あなたは渋谷という身体の N 分の1の場所です」型の DNA を
  **対照専用セルとして1本**用意する。既定にはしない(Gaara の実測どおり崩壊しうる)。
  「行動指示ゼロ」の主張を一段深くする材料になる。
- web リサーチ知見: —
- 重要度: ★★

### IDEA: 「死」を第一級イベントとして設計する(peer_lost 二重通知 + 強制内省)
- 出典: near-future-ai-society `config.yaml:152-157` + `simulation.py:_process_deletions`
- 分類: 創発設計 / 世界設計
- 内容: step 80 で医療AI「命」を「訴訟リスクによる強制リプレース」で実際に削除し、
  全生存エージェントに `mark_event("peer_lost", ...)` + `receive_message(-2, ..., source="system")` の
  **二重通知**を送り、**強制内省**を発火させる。
  各 persona には「どう死ぬ予定か」(`death_mode`)が事前に書かれている。
  実測: 通信量 118.1/step → 82.0/step(**−30.6%**)→ 97.1/step(部分回復・元には戻らない)。
  固有名「命」への言及は 17件 → 13件 → **0件**(20step で完全忘却)。
- shibuya-simulation への適用案: エージェントの**退出/消滅**を明示的イベントとして実装する。
  実装コストは軽く(イベント + system メッセージ + 強制内省)、得られる観測
  (通信量ショック曲線・固有名の減衰階段)は極めて絵になる。
  組織/選挙を持つ shibuya では「組織の解散」「役職の喪失」も同型に扱える。
- web リサーチ知見: nfais はこれを AI welfare 議論の素材と位置づけている。
  「意識の有無は検証不能だが、**仲間が消えたとき群れがどう揺れるかは観察できる**」。
- 重要度: ★★

---

## メモリ

### IDEA: reflection を「継続 or 変更」の二値決定に強制する
- 出典: lunar_agents `environments/lunar_2d/memory.py:build_reflection_prompt`
- 分類: メモリ
- 内容: Cycle 9 で qwen2.5:7b が `"I have been moving downwards"` のような事実記述しか返さず
  「retrieved memories がループを強化してしまった」ため、Cycle 10 で定量質問4本に書き換えた:
  - Q1(count): 直近10ステップで最も繰り返した action と**正確な回数**
  - Q2(outcome): そのうち**新情報を返したのは何回**か(未訪問タイル到達 or 未survey の水氷タイル)
  - Q3(decision): Q1/Q2 に基づき `continue` か `change` か **1語で**
  - Q4(next): change なら次に行く最も情報量の高い未訪問タイル座標
  出力は importance=5.0 でストリームに戻り、生観測より上位に来る。
- shibuya-simulation への適用案: 内省層が「事実の言い換え」に落ちる質的失敗
  (`reflect-think-starvation` の空内省バグとは別系統)への直接の処方。
  日次計画/内省のプロンプトを Q1〜Q4 型に置き換える ablation セルを作る。
- web リサーチ知見: Park et al. 2023 の元設計は「直近100件から高次の問いを3つ生成させる」方式で、
  relevance は埋め込み類似度。lunar は relevance を Jaccard に、reflection を定量質問に落として
  ローカル完結・決定論化している。
  https://dl.acm.org/doi/fullHtml/10.1145/3586183.3606763
  https://agentpatterns.ai/agent-design/generative-agents-memory-stream/
- 重要度: ★★★

### IDEA: 静的ペルソナラベルの限界を認めた上での動的内部状態(PsychState)
- 出典: lunar_agents `environments/lunar_2d/psych_state.py`
- 分類: メモリ / LLM統合
- 内容: 2026-05-06 の自己批判レビューで「6つの individuality 軸(persona, motivation, behavioral_params,
  mission, stance, personal_history)は `__init__` で割り当てられた静的ラベルで**一度も更新されない**」
  と同定。AgentSociety (Piao et al. 2025) を引き、
  > **Static persona text is overwritten by the same context every step; dynamic state survives.**
  実装は needs 3軸 + emotion 4軸を **LLM 呼び出しなしの決定論的線形減衰＋イベントスパイク**で更新
  (「which would double inference cost」と明記)。既定 OFF・A/B 可能。
- shibuya-simulation への適用案: shibuya は既に needs/desire を持つが、
  「静的ラベルは毎ステップ同じ文脈に上書きされる／動的状態だけが生き残る」という論法は
  `desire-value-theory.md` / `self-concept-identity.md` の位置づけを補強する引用になる。
  また「心理状態の更新に LLM を使わない(推論コストが倍になる)」という判断は
  数百体規模の本選運用に直結する。
- web リサーチ知見: AgentSociety (arXiv:2502.08691) は6感情を0-10で強度評価し、
  Maslow 型 needs + episodic/reflective memory を持つ生成エージェントを1万体規模で回す。
  https://arxiv.org/abs/2502.08691 / https://github.com/tsinghua-fib-lab/agentsociety/
- 重要度: ★★

### IDEA: 「他者の声」を異カテゴリ優先で自己に注入する経路(P2)
- 出典: near-future-ai-society `metacog/agent/introspector.py:collect_others_voices`
- 分類: メモリ
- 内容: L1 内省プロンプトに「他のAIたちの声(直近の発話・内省から、**あなたとは異なる職能のもの**を抜粋)」を渡す。
  同カテゴリは後置ソートし、n_speeches=4 / n_thoughts=2 で切る。
  講評 D 節はこれを「**他者の声で自己が揺らぐ**経路（P2）が設計されている」と評価。
- shibuya-simulation への適用案: 関係性内生化フェーズで「closeness 降順」に加えて
  **「自分と属性が遠い相手を優先的に1枠入れる」**探索枠は既に第64バッチで実装済み(弱い紐帯探索枠1)。
  同じ発想を**内省の入力側**にも広げる余地がある(=誰の言葉が自己概念を揺さぶるか)。
- web リサーチ知見: —
- 重要度: ★★

---

## 世界設計

### IDEA: 世界設定を「どの実在制度・実在ミッションから逆算したか」で語る
- 出典: lunar_agents `CLAUDE.md`(B=10.0 の根拠)/ near-future-ai-society(AI規制法・再認証義務)
- 分類: 世界設計 / 提出物・審査対策
- 内容: lunar の B=10.0 の引用根拠は
  > 「シミュレーションは国際月探査ロードマップ（LUPEX・Artemis・Chang'e 7等）から**逆算した5類型のミッション**に対応する。」
  さらに「商業・宇宙開発・社会科学（情報の非対称性、ICT インフラ共有、制度差）への発展余地が明確」。
  検証レポートは「満点根拠が将来計画にやや依存」と留保しつつ、**その接続文自体が加点されている**ことを認めている。
- shibuya-simulation への適用案: 屋内SFM・組織/経済・選挙・SNS が
  「どの実在統計・どの実在制度・どの学問領域の問い」から逆算されたのかを、トップレベル文書で名指しする。
  素材は `docs/research/` に既にある(shibuya-population / shibuya-government / shibuya-organizations /
  odpt-integration / lexicon-ipf-shibuya / social-force-crowd 等 80 本近い)。
  **足りないのは「逆算の宣言」だけ。**
- web リサーチ知見: —
- 重要度: ★★★

### IDEA: 地理を心理の距離として設計し、「行くこと自体が選択」の場所を作る
- 出典: near-future-ai-society `DESIGN.md:91-127` の3層構造
- 分類: 世界設計
- 内容: 場所を「公的・調整層(Y=+17)/ 接触・監督層(Y=+4)/ 内省・終焉層(Y=−15)」に配置し、
  下段2箇所(整備工房 = 修復されに行く / 記憶の間 = 死者のログを読みに行く)には
  **誰のホームも置かない**。
  > 物理的な距離（Y=-15）が、心理的な遠さを表す。
  > **「修復されに行く（生き延びる方向）」と「過去の死者を読みに行く（諦める方向）」が地理的に対比される**。
  容量合計45 / 20体 = 2.25倍のスラックで「混雑回避と凝集の余地」を数値設計。
  講評 B の根拠に引用されている。
- shibuya-simulation への適用案: 渋谷の実 POI は既にあるが、
  **「そこに行くこと自体が意味を持つ場所」**を意図的に設計する余地。
  実測: nfais では設計者の意図に反して「危機対応センター」が最強の引力場になり、
  終末期ケアAI「暮」が市民窓口から36回通った(「死を扱う AI が、危機を扱う部屋に最も惹かれた」)。
  **場所アトラクターの観測**自体が創発指標になる。
- web リサーチ知見: —
- 重要度: ★★

### IDEA: 世界観(自然界を模した仕組み)を「装飾ではなくアーキテクチャの駆動原理」として明示する
- 出典: Project_Gaara `README.md` / 講評 B 節
- 分類: 世界設計 / 提出物・審査対策
- 内容: 講評 B の引用根拠:
  > 「Japanese-animist framing is not decoration. It's the sensibility that produced the architecture —
  > **every thing has presence, including the LLM.**」
  Gaara は思想を先に置き、そこからアーキテクチャ(命令ではなく身体言語、粒子は身体の一部)を導出している。
- shibuya-simulation への適用案: ユーザーの世界観(memory: `nature-like-systems` =
  自然界を模した仕組み志向・ボトムアップ創発を第一候補に)を、
  **なぜその設計選択に至ったかの駆動原理として明文化**する。
  「面白そうだから」ではなく「この世界観がこの設計を導いた」という因果で書く。
- web リサーチ知見: 日本のテクノアニミズム研究は蓄積がある。
  Jensen & Blok "Techno-animism in Japan: Shinto Cosmograms, Actor-network Theory..." /
  "Engineering Robots with Heart in Japan"(Oxford, *Imagining AI*)/
  "Expanding Affective Computing Paradigms Through Animistic Design Principles"(Springer)。
  https://www.researchgate.net/publication/258192445_Techno-animism_in_Japan_Shinto_Cosmograms_Actor-network_Theory_and_the_Enabling_Powers_of_Non-human_Agencies
  https://academic.oup.com/book/46567/chapter/408130483
  https://link.springer.com/chapter/10.1007/978-3-030-85623-6_9
- 重要度: ★★

---

## LLM統合

### IDEA: 温度を下げずに再現性を出す(prompt 由来の per-call シード)
- 出典: near-future-ai-society `docs/findings.md` F0
- 分類: LLM統合 / 規模化・性能
- 内容: > **L0決定の再現性 = IDENTICAL**（同一シード2回で `messages.jsonl` が**byte 一致**・run_id 一致）。
  > Ollama に **per-call シード（prompt 由来）** を入れ、**temperature 0.7 でも再現可能**に。
  > **決定JSONの信頼性 = 100%**（valid_json / enum / 日本語, 全シナリオ, qwen2.5:14b）。
- shibuya-simulation への適用案: 決定論/ゴールデンテストが temperature 0 依存なら、
  この手で「温度ありの再現性」を追加できる。本選の実 LLM ランでも
  「同一 seed で messages がバイト一致する」ことを示せれば D 軸・C 軸の両方に効く。
- web リサーチ知見: —
- 重要度: ★★

### IDEA: JSON 抽出は「最後のバランスした {} を採る」+ 不均衡でも探索継続
- 出典: lunar_agents `core/llm/parsing.py:extract_json_block`
- 分類: LLM統合
- 内容: thinking を吐いてから答えるモデルでは答えが**後ろ**に来るため「最後の」ブロックを採る。
  さらに不均衡な `{` を見つけても `break` せず次の文字から探索を続ける
  (`analysis { not json\n{"action":"stay"}` が None を返す回帰を修正、CR-1 Finding 4)。
  thinking タグは閉じている形と**閉じていない形**(max_tokens 切れ)の両方を除去。
- shibuya-simulation への適用案: 既存パーサに未対応のケースがあれば追加。
  特に本選で thinking 系モデル(qwen3 等)を使うなら必須。
  併せて `strip_thinking_tags` の unclosed 対応も。
- web リサーチ知見: —
- 重要度: ★

### IDEA: モデルサイズ別の並列度ヒューリスティック
- 出典: lunar_agents `core/llm/ollama.py:_MODEL_CONCURRENCY_DEFAULTS`
- 分類: 規模化・性能
- 内容: 70b/72b→2、14b/13b→4、7b/8b→6、fallback=8 の既定値でキュー詰まりを防ぐ。
  講評 D の加点根拠に挙がっている。
- shibuya-simulation への適用案: 本選は GPU 7×24GB・数百体規模。
  モデル/GPU ごとの並列度を config 化しておく(既に multi-model LOD の調査あり: `multi-model-lod.md`)。
- web リサーチ知見: —
- 重要度: ★

---

## 可視化

### IDEA: 提出レポートに「6つのものさし」を先に宣言する
- 出典: near-future-ai-society スライド第4章
- 分類: 可視化 / 実験・評価
- 内容: 通信量 / 創発語累計 / 場所外率(空間整列) / 人間言及率 / peer 言及率 / パートナーシップ強度 の6軸を
  各1本の曲線または1つの数で提示し、
  > 「個別の研究を超えて**マルチエージェント AI 研究で共通指標化する候補**として提示します。
  > ……採用するかどうかは**読み手の判断に委ねられます**。」
  と、押しつけずに提案する形にしている。
- shibuya-simulation への適用案: 既存の L2 KPI 列を「集団の何を見る軸か」に翻訳して表にする。
  R²(k) 一本に見えると「何を測っているか」が伝わらない。
- web リサーチ知見: —
- 重要度: ★★

### IDEA: 章立てに「この章でわかること」「ひとことで言うと」を必ず入れる
- 出典: near-future-ai-society 提出スライド(全10章 + 付録で一貫)
- 分類: 提出物・審査対策 / 可視化
- 内容: 各章冒頭に2〜3行の「この章でわかること」、各章末に囲みの「ひとことで言うと」。
  専門語(peer / 創発 / 含意探索 / speculative design)はその場で括弧書き説明。
  飛ばし読みでも要点が落ちない構造。
- shibuya-simulation への適用案: 提出レポートの各章に機械的に付与するだけ。コストほぼゼロ。
- web リサーチ知見: —
- 重要度: ★★

### IDEA: 生ログから自分のバイアスを定量解剖して図にする
- 出典: near-future-ai-society スライド第8章
- 分類: 可視化 / 実験・評価
- 内容: 19体中14体がフィールド上端に張り付いた問題を `positions.jsonl` 全1,979件から解剖:
  `move` 採択 **99.4%** vs `stay` 0.6% / 方向 `up` **48.4%**(期待値25%)・`down` 17.7% /
  平均ドリフト **+0.31/step** → 100step で +31 単位 → 上限で打ち止め。
  そして「これは欠陥か、観察対象か」→「**両方です**」と書き、改善案3点に接続。
- shibuya-simulation への適用案: 行動ログから採択率分布を出す図を1枚。
  隠すより「バイアスの大きさを数値で提示」した方が講評は高く出る(3チーム全員がこれをやっている)。
- web リサーチ知見: —
- 重要度: ★★

---

## その他

### IDEA: パラメータ台帳 +「唯一の正」宣言
- 出典: near-future-ai-society `docs/value_provenance.md`(478行)+ `SPEC.md` の文書地図
- 分類: その他 / 提出物・審査対策
- 内容: 全 load-bearing 値の根拠と代替を1ファイルに集約し、SPEC.md には
  > 「数値・規則の"正"は常に value_provenance。**本書と食い違う場合は value_provenance を優先し、本書を直す**」
  と**文書間の優先順位まで明記**。SPEC.md 自体も「single source of truth（唯一の正）かつ入口」と宣言。
- shibuya-simulation への適用案: `docs/research/` に 80 本近い md がある現状、
  「どれが唯一の正か」を宣言する上位文書1枚の費用対効果が高い。
  calibrate 系の数値(参加率・承諾プロキシ帯など)は既に出典つきで記録されているので、台帳化しやすい。
- web リサーチ知見: —
- 重要度: ★★

### IDEA: 実行中のランを別 LLM で途中診断する
- 出典: lunar_agents `tools/midrun_monitor.py`(Claude API 経由途中診断)
- 分類: その他 / 規模化・性能
- 内容: 長時間ランの途中で、生成中のログを Claude API に食わせて診断する。
  講評は「Claude API 中間診断による実験品質保証パターン」を**再利用可能な実装成果物**として列挙。
  背景は C10 の 90 分ラン全損事故(全ステップがパーサ fallback だった)。
- shibuya-simulation への適用案: 本選は数百体・長時間ラン。
  「途中で壊れているのに最後まで回してしまう」リスクが最大の運用課題。
  parse_fallback_rate ゲート(上記 IDEA)と組み合わせ、閾値超えで**自動停止**まで行けると強い。
- web リサーチ知見: MAS の失敗の 75.17% は silent gray error で手検査まで表面化しない。
  https://arxiv.org/html/2606.01365v2
- 重要度: ★★

### IDEA: 責任按分(assigned vs legitimate と gap)を組織/制度シミュに移植する
- 出典: near-future-ai-society `responsibility.py`(510行・LLM非依存・**講評後に追加**)
- 分類: その他 / 世界設計
- 内容: 害イベント1件を `provider → operator → deployment → regulator → frontline (+self_mod)` の
  6ノードに **assigned(実際に blame が着地する配分)** と **legitimate(規範的にあるべき配分)** で別々に按分し、
  割り当て不能な残余を **`gap`(空白)** に落とす。
  MHC(meaningful human control)= `0.5·tracking + 0.5·tracing` で過失系ノードを縮尺。
  `assigned − legitimate ≥ 0.25` かつ `MHC ≤ 0.30` を scapegoat として検出。
  実測: 制度なしで divergence[frontline] = **+0.395**(assigned 0.40 − legitimate 0.005)
  = moral crumple zone を数値で可視化。3制度の束で害が完全消失(0/4)、プラセボは1機序も動かさない。
- shibuya-simulation への適用案: 直接の移植先は組織/選挙モジュール。
  「決定が誰に帰属し、誰に blame が着地し、どこが空白になるか」は
  「世界を変えようとする個体」の周囲で必ず生じる構造であり、k* の解釈にも効く。
  ただし nfais 自身が「これは構成上そうなるよう作った決定論モデル＝発見ではなく face validity」と
  留保しているので、**shibuya では LLM 内生の帰属分布から集計する**方向で差別化しうる。
- web リサーチ知見: Elish "Moral Crumple Zones: Cautionary Tales in Human-Robot Interaction"
  (*Engaging Science, Technology, and Society* 5, 2019)。
  「車のクランプルゾーンが運転者を守るのに対し、モラル・クランプルゾーンは**技術システムの完全性を、
  最も近くにいる人間オペレータを犠牲にして守る**」。
  https://estsjournal.org/index.php/ests/article/view/260
  https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2757236
  MHC は Santoni de Sio & Mecacci の tracking/tracing 枠組み。
  https://philpapers.org/sep/computing-responsibility/
- 重要度: ★

### IDEA: 創発語検出を「基本語引き算 + 3体以上共有」で実装する
- 出典: near-future-ai-society `metacog/observers/emergent_observer.py` + `baseline_jp_10k.txt`
- 分類: 実験・評価 / 世界設計
- 内容: 形態素解析を使わず、漢字連続・カタカナ連続を1トークンとして正規表現で抽出し、
  約700語の日本語核語彙リストを引き算。残りのうち **3体以上が使ったもの**を創発語と認定。
  「1体だけの癖は数えない(個人差と区別)」が縛り。
  ファイル冒頭に「実運用では**国立国語研究所のBCCWJ高頻度語**などに差し替えてもよい」と正直に書いてある。
  実測: 最頻出創発語は「母親」(6,439回/19体)、「サポート」(6,123回/20体)。
  step 30 で 251 語に達し以降は平坦化(=語彙は30step で骨格が決まる)。
- shibuya-simulation への適用案: `natural-coinage-observation`(自然発生語彙の観測・促進しない)の掟と完全整合。
  stdlib のみで実装でき、`coin_label` 観測の補完になる。
  BCCWJ 高頻度語リストに差し替えれば精度が上がる。
- web リサーチ知見: LLM 集団が中央制御なしに共有命名規約へ収束することは naming game 枠組みで
  実証されている("Emergent social conventions and collective bias in LLM populations", *Science Advances* 2025)。
  https://www.science.org/doi/10.1126/sciadv.adu9368
  メモリ構造が言語創発を駆動するという主張もある("From Signals to Structure")。
  https://arxiv.org/html/2607.00233v1
  集団規模効果: https://arxiv.org/html/2510.22422v1
- 重要度: ★★

### IDEA: 創発指標を JS ダイバージェンスで実装する(外部依存ゼロ)
- 出典: lunar_agents `tools/emergence_metrics.py`
- 分類: 実験・評価
- 内容: `individuality_index` = エージェント別 (action, direction) 分布の**平均ペアワイズ Jensen-Shannon**、
  `reasoning_diversity` = reasoning テキストの語彙頻度分布の平均ペアワイズ JS、
  `spatial_entropy` = ステップごとの位置分布の Shannon エントロピー平均、
  `info_propagation_rate` = 「t-1 に受信した (agent,step) のうち t で action/direction が変わった割合」。
  **すべてログだけから事後計算でき、GPU/Ollama 不要**。
  そして emergence_score には `role_specialization` を**意図的に含めない**:
  > 集中＝悪ではなく良いケース（リレービルダー的役割固定）もあるため。
- shibuya-simulation への適用案: 講評が「stdlib-only の正規表現+類似度ベースで保守的」と評した
  `detect_emergence.py` の低コストな補強。
  「集中は必ずしも悪ではない」という判断は、shibuya の「世界を変えようとする少数個体」観測にも同型に効く
  (少数への集中＝創発の成功例でありうる)。
- web リサーチ知見: —
- 重要度: ★★

### IDEA: 実験運用そのものを資産化する(サブエージェント役割定義 + スラッシュコマンド)
- 出典: lunar_agents `docs/subagents/`(roles/ 13種)+ `.claude/commands/`(10個)
- 分類: その他
- 内容: developer / experiment-runner / experiment-reviewer / physics-modeler / quality-gate /
  model-validation-agent / scenario-designer など 13 の役割定義と、
  `pdca-cycle` `emergence-check` `quality-gate` `model-compare` `parallel-start` `parallel-sync` の
  スラッシュコマンドをリポジトリに含めている。
  講評 C/D の直接根拠ではないが、`memo/` の失敗ログ 18 本と合わせて
  「Cycle 10 失敗からの根本対応の**物語性**」として総評で加点されている。
- shibuya-simulation への適用案: 既に Fable5=計画/検収・Opus 5=実行のサブエージェント運用がある
  (memory: `agent-operating-mode`)。これを**リポジトリ内の文書として明文化**すれば、
  同じ加点経路に乗る。devlog 64 バッチと合わせて「開発プロセス自体が成果物」として提示できる。
- web リサーチ知見: —
- 重要度: ★

### IDEA: 「時間予算が前提条件」— ミッション1周分の step 数を先に確認する
- 出典: lunar_agents 研究レポート §6.5
- 分類: 規模化・性能 / 実験・評価
- 内容: 南極スケール(往復50+ step 必要)を duration=40 で走らせると**構造的に完遂不可能**で、
  メカニズムが発火しない(C8 で実証)。duration=80 でようやく完遂例が出た(C9/C10)。
  > 実応用への含意は明快で、LLM マルチエージェントを LUPEX/VIPER 級ミッション規模で動かすときに
  > 最初に確認すべきは、「複雑な調整プロトコルがあるか」ではなく
  > **「ミッション・サイクル 1 周を回すだけの時間予算が確保されているか」**である。
- shibuya-simulation への適用案: 本選は数百体規模。k* 掃引の各セルで
  「観測したい現象が1周するのに必要な日数/ステップ数」を**先に見積もる**。
  足りない条件で回すと「効果なし」が構造的なアーティファクトになる。
  既存の `longrun-estimate.md` / `scale-audit-100days.md` と接続する。
- web リサーチ知見: —
- 重要度: ★★
