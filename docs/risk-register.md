# リスク台帳(red-team 監査 2026-07-02、Opus 4.8 委譲 + Fable 5 検収)

> プロジェクト全体への批判的監査の結果。各リスクに深刻度・根拠・緩和策。**設計変更を伴う緩和策は OPEN 扱い(ユーザー決定)**。lit 詳細: [[lit/method__experiment-design-statistics]] 等。
> 監査の総評: 「自認と対策のギャップ」が急所。**"k* 確定" を10日のゴールに置くのは過大 — "反証可能な測定器+予備的兆候" に再設定すれば публикable 確率は数倍**。

## 🔴 致命(設計で必ず対処)

### R1. k の操作化が計算量・トークン量と交絡する
- **内容**: k(内省の頻度・深さ・接地・書き戻し)を上げると、トークン量・LLM呼び出し・サンプリング分散・drift 機会が**同時に単調増加**。R²低下・seed発散・EWS の3信号すべてが「LLM を多く回しただけ」で出る=三角測量が交絡に対して独立でない。
- **緩和(実験計画に組み込む)**: ①**sham reflection 対照**(内省を実行するが書き戻しを捨てる=計算量同一・結合ゼロ)②**compute/token 一定の k 掃引**(深さだけ変え総トークン固定)③**null 系列**(k を上げずに呼び出し量・温度だけ k と同じに増やす)— 3信号が null で出ないことを示して初めて k* を主張可能。④k の2通りの操作化(頻度版/接地版)で k* が一致するか。
- 根拠: 実装差が macro を最大76pp 動かす([arXiv 2605.18890](https://arxiv.org/abs/2605.18890))

### R2. tail(希少な世界改変者)× LLM の均質化の正面衝突
- **内容**: LLM は「平均ペルソナ」化し分散が人間より小さい(boundary 論文は「分散不足なら個体・tail 主張を禁じ集団レベル定性パターンに限定せよ」と明言)。trait の tail は初期分布で守れても、**k が効く emergent state 側の tail が LLM 均質化で消える**。
- **緩和**: ①**被説明変数を「希少二値(改変者か否か)」から「4層レイヤーへの連続的書き換え量」に変更**(検出力が桁で改善+judge 循環も緩和)②生成・更新・言語の各段で tail 保護(Verbalized Sampling / tail は LLM tier 残留 / conformity 監視)③主張を二層化(強:「LLM 社会で k* が測定可能」/ 保留:「人間社会への外挿」)。
- 根拠: [arXiv 2506.19806](https://arxiv.org/abs/2506.19806)(boundary)/ 分野8-9 の tail 過小

### R3. 検出力 × 10日 wall-clock の不成立リスク
- **内容**: 希少陽性で R² を推定し k×seed×N を回す予算が10日に収まらない公算。**事前検出力計算が存在しない**。
- **緩和**: ①R2 の連続量化(上記)②adaptive 掃引(粗→急落帯に集中)③**Phase 0 でパイロット→検出力計算を文書化**④ゴール再設定(k* 確定→「測定器+兆候」)。

## 🟠 重大(go/no-go ゲートか対照で対処)

### R4. 「世界改変」判定の循環(trait ロールプレイ → judge が拾う)
- LLM は salient trait を増幅(generative exaggeration)→ 高NFC ペルソナが「改変者を演じ」、judge がその演技を検出 → R² が人為的に nature 寄りに上振れ。
- **緩和**: 世界改変を **judge の意味判定でなく、4層への測定可能な書き換え量で客観計上**(POI 新設・資源プール形成・ラベル採用 S字到達)。judge は補助。高 salience だが世界を変えない行動の negative control。人手 κ≥0.7。

### R5. calibration の contamination(tipping 25% は LLM が暗唱できる)
- 既知結果の再現は「暗記の再生」かも。さらに **nature-nurture の「答え」自体(リーダーシップ遺伝率30-60%)が学習データにある** → R²(k) が既知物語の再生である恐れ。
- **緩和**: calibration は数値をずらした反実仮想設定で。**逆符号環境 probe**(経験が効かないはずの設定で LLM が既知物語に引きずられないか)を1本。

### R6. conformity 崩壊が drift・分岐(M1c)を殺す
- RLHF 同調(85.5%)で集団が1点収束 → 観たい現象が出ない。anti-collapse 機構が同調に勝つ保証なし。
- **緩和**: ★ **B段(N=100-500)に go/no-go ゲート**: conformity 率と drift 発生を anti-collapse ON/OFF で先に実測。負けるなら k* 実験は無意味 → 設計に戻る。

### R7. 退化解(全員運動家 / 全員無関心)
- SIMCA 正フィードバックは runaway を生む。「面白い帯」が razor-thin の可能性。
- **緩和**: 恒常性を injection せず **carrying capacity・資源・時間の affordance 制約で自然飽和**([[lit/ecology__ecosystem-metaphor-overview]])。退化解の k 範囲を先に地図化。

### R8. RLHF 対照が Qwen3.6-27B で組めない(base 版未公開)
- **緩和**: ①同系列 abliterated(Heretic 手法)②**base+instruct が揃う別ファミリを最小規模で1組**確保し model×k 交互作用の存在だけ示す。

### R9. trait→state の文脈汚染(分離可能性の前提が崩れる)
- 同じモデルが trait も state も同一文脈で読む → state が trait の鏡写しに(mirroring)。
- **緩和**: **state 更新器には行動ログのみ渡し、初期 trait を配線レベルで除外**(seam 化)。事後に trait-state 相関チェックを observer に。

### R10. 工学リスク(10日×未着手×ハイブリッド統合×1人)
- **緩和**: **lean 自前コア一本化**(Concordia は依存でなく必要部品の再実装)、P0 で Mock end-to-end 最優先、フリートは単一GPU から seam で拡張。→ build-vs-reuse 決定(案B寄り)の材料。

## 🟡 中(観測・運用で対処)
- **R11** EWS を tail 個体で推定=時系列不足 → **集団秩序変数(改変者割合・consensus)で推定**。無理なら三角測量2点に落とすと事前許容。
- **R12** 崩壊ドリフト vs 世界改変ドリフトの判別器が未検証 → **非LLM 指標(embedding 分散崩壊・語彙エントロピー低下)を先に定義**し k* が崩壊点と不一致なことを示す。
- **R13** 4bit 量子化×tail の未検証交互作用 → 小規模 fp16 vs 4bit 分散比較を1本。
- **R14** LLM 非決定性が seed 発散の床を上げる → **ノイズフロアを実測定量化**、フロア超えのみ k* 候補。
- **R15** 発話混入=injection 経路 → 構造化・sanitize・上限、伝播異常検知を observer に([[lit/agents__persona-language-safety-opinion]])。
- **R16** アフォーダンス貧困で「何も起きない」(OPEN#7)→ B段でファネル各段の通過率を実測、枯れた段の到達可能性を足す。

## 🟢 対外・倫理
- **R17** 実在渋谷×実在イシュー×abliterated の説明責任 → **【ユーザー決定 2026-07-03: 場所・施設は実名を使用】**(リアリズム優先、リスク受容)。残余リスクの緩和: 実在の**個人・特定団体は登場させない** / シミュ内の出来事は**すべて架空**と ETHICS.md・発表資料に明記 / abliterated は「統制目的」明記・生出力非公開。
- **R18** 「世界改変者」の政治的響き → 対外的には collective action / institutional change の用語に寄せる。
- **R19** ハッカソンで k* 曲線は地味 → **1画面デモ「3D渋谷でラベル伝播(色分け)+改変者ノード発火+R²(k) リアルタイム更新」**。GPU 必然性は GPU-hour 表で。予選 MVP は M1 を N=100-500 で見せる(k* は本選)。

## 新規性の位置(監査結論)
- 脅かされる: 規模・創発・慣習創発・「LLM社会に臨界がある」はすべて先行あり(OASIS/AgentSociety/Ashery/criticality 論文)。nature-nurture は人間の答えが既知。
- ★ **残る差別化(有望)**: 「variance decomposition × k 掃引 × 三角測量(+null/sham 対照)× observer-frame × tail 明示確保」の**測定プロトコル統合**は直接一致なし。**勝負所は現象でなく測定の厳密さ** — 分野の中核弱点(validation)への直接回答として論文化。boundary/robustness 論文は**自分から引用して先回り武装**する。
- 到達確率の見積り(監査者): k* 確定=低(5-15%)/ **方法論論文+予備兆候=中(35-50%)**/ ハッカソン製品性=中〜高。

## 主要出典
[Boundary(arXiv 2506.19806)](https://arxiv.org/abs/2506.19806) / [Robustness audits(arXiv 2605.18890)](https://arxiv.org/abs/2605.18890) / [AgentSociety(arXiv 2502.08691)](https://arxiv.org/abs/2502.08691) / [trait→行動 generative ABM(arXiv 2601.15114)](https://arxiv.org/abs/2601.15114) / [BeliefShift(arXiv 2603.23848)](https://arxiv.org/abs/2603.23848) / [Moltbook(arXiv 2602.14299)](https://arxiv.org/abs/2602.14299)
