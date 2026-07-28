# IDEA 集 — 第1回ハッカソン グループ1（5リポ）

対象: my-social-agents（5位 34.5）/ hackathon_（6位 34.0）/ goodecho_r（24位 24.5）/ good_echo_iss_sim_cursor_50s_no_accident（6位 34.0）/ good_echo_iss_sim_cursor_100s_w_accident（8位 33.5）

各チームの詳細は `../teams/<repo名>.md` を参照。

---

### IDEA: 動機の決定論的分類器（world-side motive classifier）

**出典**: my-social-agents `src/v3/poc_world.py:964-982` `_classify_attack` / 同 `logs/runs.csv` の `n_pattern1..n_mixed` 列
**分類**: 実験・評価

**内容**
攻撃が起きたとき、LLM に「なぜ攻撃したか」を聞かずに、世界側の観測量（相手の武器増加量 `target_weapon_growth`、戦力差 `weapon_diff`、過去に殴られた記憶 `was_attacked_by_target`、相手への negative reputation）だけから Revenge / Pattern1(preventive) / Pattern2(opportunistic) / Rumor / Mixed を優先順位付きで判定する純粋関数。判定結果は run ごとの CSV 列になり、そのまま sweep の従属変数として集計できる。著者は「分類器のバグで Rumor が過剰計上されている」と REPORT の Limitations に自己申告しており、分類器自体を検証対象として扱っている。

**shibuya-simulation への適用案**
「世界を変えようとする個体」の判定を、LLM の自己申告や発話テキストの語彙マッチではなく、**世界側の帳簿から決定論的に分類**する `classify_change_attempt(ctx) -> str` を新設する。context 候補は当方が既に持っている量から作れる: 組織設立の有無 / 選挙立候補 / 新規ラベルの初出（coin_label）/ 誘い（joint_invite）の発信数と weak_tie 比率 / SNS 投稿の到達範囲 / 弱い紐帯を跨いだ回数。分類の型は例えば `Founder`（組織を作った）/ `Broker`（弱い紐帯を橋渡し）/ `Coiner`（語を作り伝播させた）/ `Candidate`（選挙で動員）/ `Follower`（既存に乗った）/ `Mixed`。判定は**乱数ゼロ・決定論**で書き、ゴールデンテストを付ける。これを L2 の新列にすれば、R²(k) 掃引の従属変数が「1 本の連続量」から「型別カウントのベクトル」に増え、**k* 前後で創発の型が入れ替わるか**（例: k 低では Follower のみ、k*超で Founder が初発火）を見られる。my-social-agents の「Pattern1 は W≥48 で初発火」に相当する発見が狙える。

**web リサーチ知見**
Jervis (1978) の枠組みでは、セキュリティジレンマの大きさは「攻防バランス」と「攻防の識別可能性」の 2 変数で決まる。my-social-agents の「武器 48 個以上で初めて武装増強が観察可能になり preventive が発火」は、この**識別可能性を供給量で操作した**とも読める。当方でも「変革志向が他者から観察可能になる閾値」という形の RQ に翻訳できる。
- https://www.cambridge.org/core/journals/world-politics/article/abs/security-dilemma-revisited/0174D23352D9303257AAAC18911F3AB7
- 全文 PDF: http://slantchev.ucsd.edu/courses/ps143a/readings/Jervis%20-%20Cooperation%20under%20the%20Security%20Dilemma.pdf

**重要度**: ★★★

---

### IDEA: realism_contract — ビューア／レポートが嘘をつかないための誓約

**出典**: good_echo_iss_sim_cursor_50s/100s `domain_packs/iss_benevolence/domain.yaml` の `pipeline.habitat_ui.realism_contract`
**分類**: 可視化

**内容**
domain.yaml に UI の設計契約を 5 条で明文化している。(1) UI 表示は agent state / place capacity / event / conversation / relationship_seed から導出する（＝表示専用の別データを作らない）、(2) 摩擦と修復は event_id と conversation_id の両方に紐づける、(3) **会話しない・沈黙する・相手を避ける状態も有効な観測として表示する**、(4) 位置と寝床割当は step ごとに連続性を持たせ毎描画でランダムに変えない、(5) **Run B の改善は万能にせず、短い摩擦・遅れた修復・ナッジの押しつけ感も残す**。第 5 条は自作品の売り（ナッジ効果）を自ら抑制する規定。

**shibuya-simulation への適用案**
`docs/` に `viewer-realism-contract.md` を新設し、当方版の条文を置く。候補: (a) ビューアは L1/L2/イベント JSONL からのみ導出し、演出用の合成データを持たない、(b) **不参加・不履行・沈黙・使われなかった施設を空白でなく明示的に表示する**（第64バッチで観測した「承諾したが同席せず 0.337」のような不履行はむしろ主役として出す）、(c) 位置と所属は step 間で連続、(d) **treatment 条件を良く見せる演出をしない**（endo ON セルだけ色を強める等の禁止）、(e) 較正乖離・p 値・seed 数の限界を同じ画面に出す。make_viewer / make_endo_report のレビュー時にこの 5 条をチェックリストとして使う。第64バッチまでで「正直な限界の明記」を毎回やっているが、それを**機械可読な契約**に格上げでき、検収の再現性が上がる。

**web リサーチ知見**
本調査では ABM ビューアの「表示誠実性契約」に相当する一次文献は見つからなかった（正直に記録）。近い概念としては、EB-DEVS 等の形式的枠組みが「マクロ状態は micro からの集約としてのみ定義される」ことを規格化している点が (a) に対応する。
- EB-DEVS: https://arxiv.org/pdf/2010.05042

**重要度**: ★★★

---

### IDEA: 誘導語（effect-preloading）検出 lint — no-fingerprint の機械チェック

**出典**: good_echo_iss_sim_cursor_* `configs/config.iss.cursor.run_b.yaml` の place description（`welcomes conversation` / `encourages moving` / `to reduce isolation`）と、両講評の A 減点理由
**分類**: 創発設計

**内容**
Hop-Step-Jump 版は「行動指示を書かない」方針を掲げながら、環境オブジェクトの記述に **"welcomes" / "encourages" / "to reduce isolation" という効果を先取りする語**が混入し、両評価とも A の減点理由に挙げた。一方 `Sanctuary mark: Others are expected not to interrupt when occupied` は世界の規範事実の記述に留まり誘導度が低い。**同一リポ内で誘導度が揃っていない**。goodecho_r 版のナッジ記述は「和らぐ人もいれば、逆に遠さを感じる人もいる」と**両方向の効果を併記**しており、no-fingerprint としてはこちらが上。

**shibuya-simulation への適用案**
prompt / conf に含まれる自然文（場所説明・イベント説明・ペルソナ文）に対する **lint テスト**を追加する。禁止パターン例: 効果先取り動詞（促す/助長する/緩和する/減らす/高める、encourages/welcomes/reduces/improves）、行動指示形（〜すべき/〜しよう/should/must）、評価語（危険な/良い/望ましい）。許容形は「事実の記述」「規範の記述（〜と期待されている）」「両論併記」。既存の禁止語チェックがあれば拡張、無ければ `tests/test_no_fingerprint_lint.py` として新設し、`conf/**/*.yaml` と prompt 定数を走査する。第64バッチまでで no-fingerprint は原則として守られているはずだが、**原則をテストで固定していないと将来のバッチで漏れる**。1725 テストの中に 1 本足すコストは小さい。

**web リサーチ知見**
Gibson (1979) のアフォーダンス理論では、環境を知覚することは「それが何を afford するか」を知覚すること。Norman は real affordance（実際に可能なこと）と perceived affordance（可能だとユーザが信じること）を区別した。**世界側が書くべきは real affordance の事実であり、perceived affordance の誘導ではない**、と整理すると lint の判定基準が明確になる。
- Gibson's Affordances: https://www.researchgate.net/publication/15176211_Gibson's_Affordances
- LLM のアフォーダンス駆動環境認識: https://arxiv.org/pdf/2504.01644
- Mind in action: expanding the concept of affordance: https://www.tandfonline.com/doi/full/10.1080/09515089.2024.2365554

**重要度**: ★★★

---

### IDEA: 非単調な外乱プロファイルで k* のヒステリシスを見る

**出典**: good_echo_iss_sim_cursor_100s_w_accident `events_run_a.tsv` の DEBR01–05（intensity 0.92 → 0.88 → 0.72 → 0.95 → 0.98）／ hackathon_ `worlds_crisis/config_crisis_autonomy.yaml` の `fires`（0.6 → 0.7 → 0.8 の単調増加）との対比
**分類**: 実験・評価

**内容**
100s 版は「衝突 → 応急修復 → 暫定再開（0.72 まで緩む）→ 酸素漏れ判明（0.95）→ 生命維持危機（0.98）」と**一度緩めてから再度深く落とす**強度設計になっている。単調増加のストレス印加では「慣れ」と「単調な劣化」しか観測できないが、この形なら「回復したと思った後の再崩壊」への反応が見える。同じ「危機を入れる」でも hackathon_（単調増加）とは思想が違う。

**shibuya-simulation への適用案**
R²(k) 掃引を**上りと下りの両方向で走らせる**。すなわち k を低→高で上げていく系列と、高→低で下げていく系列を同一 CRN seed で回し、同じ k でも到達経路によって R² が異なるか（ヒステリシスループ）を測る。相転移研究では**ヒステリシスの有無が一次転移と二次転移（連続転移）の判別材料**になるため、「k* が存在する」よりさらに強い主張になりうる。実装は `conf/experiments/` に `k_sweep_hysteresis.yaml` を足し、run 内で k を段階的に変える（前のステップの状態を引き継ぐ）だけ。既存の checkpoint 機構（第62バッチで中央管理化済み）がそのまま使える。単発ショック条件（1 日だけ）と慢性条件（残り全期間）の対比も同じ枠で作れる。

**web リサーチ知見**
本調査では ABM における k 掃引ヒステリシスの一次文献 URL を取得できなかった（正直に記録）。関連として、複雑系の双方向ミクロ↔マクロ因果の理論枠組みが、マクロ状態がミクロに戻ることで経路依存が生じる機構を扱っている。
- Dynamical theory of complex systems with two-way micro–macro causation (PNAS): https://www.pnas.org/doi/10.1073/pnas.2408676121

**重要度**: ★★★

---

### IDEA: 「相転移を見つけた」を主張の形に落とす（B 満点の型）

**出典**: my-social-agents README「観察された 4 つの法則」/ `docs/REPORT_2026-05-06.md` Abstract / 講評 B=10.0 の評価文
**分類**: 提出物・審査対策

**内容**
第1回で唯一 B 満点だった my-social-agents の実体は「テーマが珍しい」ではなく、**先行理論 → 仮説（H1/H2/H3）→ sweep 設計 → 定量結果 → 理論への差し戻し、という研究のループが閉じている**こと。README 冒頭で Hobbes/Jervis/Malthus を引き、REPORT で「H2: Pattern1 は武装増強観察可能性が必要条件（Jervis）」と明示し、結果表で「weapon=24 で攻撃 0.7 → 5.0」を出し、最後に「Hobbes: ✓ / Jervis: ✓ / Malthus: △ 噂OFF環境でのみ成立」という**理論 × 検証結果の対応表**で締める。N=3 seed という統計的弱さは Limitations で正直に認めている。

**shibuya-simulation への適用案**
本選提出物の README / レポートを**この 5 段構成で書き直す**。(1) 先行理論を名指し（Granovetter 1973 弱い紐帯、Onnela 2007、Rogers のイノベーター普及、Centola の複雑感染、Schelling の分居モデル閾値 等、当方が既に第64バッチで引いているもの）、(2) H1/H2/H3 を明文化、(3) R²(k) 掃引設計、(4) k* とその周辺の定量結果、(5) **「理論 × 検証結果の対応表」**で「◯◯理論は成立/条件付き成立/不成立」と一覧化。当方は既に sign-flip permutation + CRN + 較正乖離ゲートまで持っており、統計的厳密さでは my-social-agents を上回れるので、**「理論への接続」だけが不足**している。ここを埋めれば B は同等以上を狙える。

**web リサーチ知見**
Jervis の枠組みは「必要条件（識別可能性）」という形で仮説を書く型を提供している。当方でも「k* を超えると変革志向が他者から観察可能になり、模倣が始まる」のような**必要条件型の仮説**に落とすと、単なる相関の報告より強い主張になる。
- http://slantchev.ucsd.edu/courses/ps143a/readings/Jervis%20-%20Cooperation%20under%20the%20Security%20Dilemma.pdf
- 要約: https://adambrown.info/p/notes/jervis_cooperation_under_the_security_dilemma

**重要度**: ★★★

---

### IDEA: 制度転換の時間断続デザイン（同一個体・同一 seed でルールだけ切り替える）

**出典**: hackathon_ `worlds_crisis/config_transition_cap_to_auto.yaml` の `transitions: [{step: 16, label: capitalism_to_autonomy, value_system: "... NOTE: The rules of this world have just changed. ... How do you adapt?"}]`
**分類**: 実験・評価

**内容**
YAML 5 行で「Day16 に世界ルールを資本主義から自律分散へ差し替える」自然実験を実装。HFI は 7.863 → 8.410（+7.0%）。**同一エージェント・同一場所・同一 seed で制度だけを時間軸上で切る**ため、個体差が完全に統制される（regression-discontinuity in time 的な設計）。切替時に「ルールが変わった。どう適応する？」と明示告知を入れているのは設計判断で、黙って変える版も作れる。

**shibuya-simulation への適用案**
`conf/experiments/` に `transitions:` 相当のキーを足し、run の途中で (a) k を切り替える、(b) 組織/選挙の制度を有効化/無効化する、(c) relations.endogenous_* のフラグを切り替える、を可能にする。特に**「選挙制度を Day X から導入する」「組織設立を Day X から可能にする」**は当方の org-emergence 目標に直結し、「制度が先か志向が先か」を切り分けられる。告知あり版／なし版の 2 セルを作れば「制度変化の認知そのものの効果」も分離できる。checkpoint が中央管理済みなので mid-run の状態差し替えは実装しやすい。

**web リサーチ知見**
LLM エージェントで制度的エージェンシーを表現する研究は近年立ち上がっており、機会と課題（特にモデル事前学習バイアス）が整理されている。制度を変数化する際の妥当性論点として参照できる。
- Exploring the opportunities and challenges of using LLMs to represent institutional agency (ESD 2025): https://esd.copernicus.org/articles/16/423/2025/
- 政策向け LLM エージェントシムの有用性: https://arxiv.org/html/2509.21868v1

**重要度**: ★★★

---

### IDEA: governance_debate 型の「問いかけだけ」刺激で組織創発を観測する

**出典**: hackathon_ `agent.py:_build_fire_section` の `crisis_descriptions` に含まれる肯定的イベント群（`governance_debate` / `creative_challenge` / `philosophical_prompt`）
**分類**: 世界設計

**内容**
危機イベントと同じ枠組みで、**否定的でない刺激**も打てるようになっている。特に `governance_debate` は「The group is asked: How should this shared space be organized? Who decides, and by what principles? Does everyone get equal say — or should wisdom, experience, or contribution lead?」と、**問いを投げるだけで組織化を指示していない**。`creative_challenge` は「no pressure, no deadline, no evaluation. What emerges when people collaborate freely?」。評価検証者はこの肯定イベント群を「元評価の見落とし＝評価を更に支える要素」と指摘した。

**shibuya-simulation への適用案**
当方の追加研究目標「組織の自然形成 + ファウンダー成立条件の観察」に対し、**no-fingerprint を保ったまま組織形成の観測窓を開ける刺激**として導入する。例: 渋谷の共有空間（公園・広場・施設）について「この場所の使い方は誰がどう決めるべきか」という問いが世界イベントとして全員に届く（掲示・SNS の話題として）。行動は一切指示しない。刺激の有無を treatment セルにすれば、「刺激なしでも組織が生まれるか」「刺激があると k* が下がるか」を測れる。既存の 6 セル CRN 実験プロトコル（第63バッチ）にセルを足す形で載る。

**web リサーチ知見**
Park et al. (2023) の Generative Agents では、記憶と reflection を持つ 25 体が自発的に連合形成・招待の伝播・共同イベントの調整を行った。「問いを投げるだけで集団行動が立ち上がるか」はこの系譜の直接の後続実験になる。
- LLM マルチエージェント サーベイ内の位置づけ: https://arxiv.org/html/2402.01680v2

**重要度**: ★★★

---

### IDEA: 「できなかった事」節を提出物に明示する

**出典**: my-social-agents スライド p4/p5 の「【できなかった事】」欄と p8「まとめ・感想」／同 `docs/FUTURE_WORK.md`
**分類**: 提出物・審査対策

**内容**
5 位 34.5 の作品のスライドは、システム構成図のページごとに**「【できなかった事】」という節を明示的に置いている**。p4「自由な意思決定：人間らしい意思決定の再現が難しかったため、マズローの欲求段階などそれっぽいモデルをプロンプトに定義することで人間らしい意思決定をさせざるをえなかった」。p5「LLM が内容の薄い話題を続けてしまい、適切な会話終了のタイミングを判断できない。そのため、やむを得ず会話の目的を外部から定義する仕様に変更せざるを得ませんでした」。p8「最終的に MBTI やマズロー欲求段階など、それっぽいフレームを片っ端から盛り込むことでなんとか人間らしさを持たせる事ができました」。**失敗と妥協を正直に書いた発表が、高評価（特に C 発展性 8.0）と両立している**。講評は FUTURE_WORK の批判的自己分析を「研究としての成熟度を示す」と明示的に加点した。

**shibuya-simulation への適用案**
本選スライド／README に「できなかったこと・作為的なままの部分」節を独立して設ける。当方には既に材料が揃っている: 誘い先が知人である直接統計の不在（第64バッチで註記済み）、断り頻度の直接統計の不在（第62バッチ、プロキシで代用）、小 seed 数の検出力限界（第63バッチ）、mock では内生経路 0.0 になる構造、履行率 0.337（承諾したが同席しない）。これらを**隠さず 1 枚にまとめる**。加えて FUTURE_WORK 相当（「作為性をどう減らすか」）を docs に置き、README から参照する。

**web リサーチ知見**
本項は評価運用の観察に基づくもので、外部一次資料は参照していない（正直に記録）。

**重要度**: ★★★

---

### IDEA: 実験仕様（仮説・比較・主要 KPI）を conf に宣言する

**出典**: good_echo_iss_sim_cursor_* `domain_packs/iss_benevolence/domain.yaml` の `purpose:` ブロック
**分類**: 実験・評価

**内容**
domain.yaml の冒頭近くに

```yaml
purpose:
  hypothesis: "閉鎖空間に善性オブジェクトを置くと、孤立や関係断絶が緩和されるか"
  comparison: "Run A（オブジェクトなし） vs Run B（オブジェクトあり）"
  primary_kpis: [total_messages, unique_interaction_pairs, reciprocity_rate,
                 repair_after_conflict_rate, bridge_agent_count, load_fairness, isolated_agents]
```

があり、**主要 KPI を実験開始前に宣言している**（＝事後の p-hacking を構造的に抑える）。C=9.0 の一因。

**shibuya-simulation への適用案**
`conf/experiments/*.yaml` に `purpose: {hypothesis, comparison, primary_kpis, secondary_kpis}` を必須キーとして足す。第63バッチの `endogenous_accept.yaml` は既に H1/H2/H3 とゲート条件を持っているので、**形式を統一して機械可読にする**。`analyze_*.py` は `primary_kpis` を conf から読むようにし、宣言されていない列で主検定をしたらエラーにする。これで「主要 KPI の事前登録」が仕組みとして担保される。

**web リサーチ知見**
本項に対応する一般手法名は事前登録（preregistration）。本調査では ABM/LLM シム文脈の一次資料 URL を取得していない（正直に記録）。

**重要度**: ★★

---

### IDEA: ミクロ→マクロ→ミクロのフィードバックを YAML 係数表として外部化する

**出典**: good_echo_iss_sim_cursor_* `domain.yaml` の `pipeline.state.fields` / `pipeline.feedback.signal_rules` / `delta_coefficients` / `event_rules`
**分類**: 創発設計

**内容**
エージェントの行動カテゴリ・感情・**発話テキストのキーワード**から 7 種の圧力シグナルを重み付き合成し（`mutual_aid_pressure` = カテゴリ「手伝い」0.90 + 感情「連帯感」0.26 + テキスト「一緒」0.12 …）、そのシグナルから 7 個の社会状態変数を係数行列で更新し（`interpersonal_tension` ← conflict_pressure +0.045 / mutual_aid_pressure −0.035）、社会状態が閾値を超えたら新イベントを生成して次ステップのエージェントに戻す。**この双方向ループ全体が Python でなく YAML の表として書かれている**ため監査・感度分析が容易。各状態変数には `polarity: pressure / buffer` が付く。

**shibuya-simulation への適用案**
当方の関係性内生化（第62〜64バッチ）は Python 関数として実装されているが、**係数を conf に外出しする**とゲイン。具体的には (a) 発話/行動から「変革圧」「同調圧」「孤立圧」等のシグナルを合成する規則、(b) シグナル → 街レベル状態（雰囲気・ラベル普及率・組織密度）の係数行列、(c) 状態閾値 → 世界イベント生成。ただし当方の no-fingerprint 原則上、生成されるイベントは**事実の記述のみ**にする必要がある（前掲の lint IDEA と併用）。外部化すれば較正（calibrate REALITY）で係数を fit する対象が明確になる。

**web リサーチ知見**
これは複雑系でいう upward causation（ミクロの集約が state variable を作る）＋ downward causation（マクロ状態がミクロに読み取り専用で供給される）の実装。EB-DEVS はこれを形式的枠組みとして規格化しており、「every atomic model has read-only access to global state」という設計を明示している。
- Two-way micro–macro causation (PNAS): https://www.pnas.org/doi/10.1073/pnas.2408676121
- EB-DEVS: https://arxiv.org/pdf/2010.05042
- 人工社会における創発シミュレーションの実践的手法: https://arxiv.org/pdf/2110.08170
- マクロ動態とミクロ状態の結合（長期社会シミュレーション）: https://arxiv.org/html/2604.05516v2

**重要度**: ★★

---

### IDEA: public / private 二値申告で「未表明の変革志向」を測る

**出典**: goodecho_r `agent.py` の出力スキーマ（`public_stress` / `private_stress` / `gap_reason`）と README の考察「乖離値の縮小こそが実質的効果」
**分類**: 実験・評価

**内容**
24.5 点の低評価作品だが、**指標設計だけは講評が「洞察に富む」と評価**した唯一の点。表向きに見せるストレスと内心のストレスを別々に自己申告させ、その乖離を「心理的安全性の欠如」の代理指標とする。結果は「ストレス水準はほぼ不変（−0.04）だが乖離は縮小（3.35 → 3.01）」で、**主効果より乖離のほうが動いた**。

**shibuya-simulation への適用案**
当方の内省／発話に、**公開面と内面を分けた申告**を導入する。例: 「今日、他人に見せた自分の志向」と「実際に思っていた志向」を別フィールドで出させ、乖離を `latent_change_intent`（未表明の変革志向）として L2 に列追加。仮説は「k が k* に近づくと、まず乖離が縮む（言えるようになる）→ 次に公開志向が上がる」。**乖離が公開行動より先に動くなら、k* の先行指標（early warning signal）になる**。第64バッチの joint_invite / label 伝播とも接続できる（言えるようになった人から誘い始める、等）。

**web リサーチ知見**
この乖離には確立した学術概念がある。Hochschild (1983) の**感情労働 / 表層演技（surface acting）/ 感情的不協和（emotional dissonance）**で、「表出感情と実感情の齟齬」が emotional exhaustion と関連することが実証されている。goodecho_r はこれを引けておらず、引いていれば B がさらに上がった可能性が高い。当方は最初から引用して導入すべき。
- 概説: https://www.simplypsychology.org/emotional-labor.html
- Grandey & Gabriel (2015) レビュー: https://goal-lab.psych.umn.edu/orgpsych/readings/7.%20Job%20Satisfaction%20&%20Affect/Grandey%20&%20Gabriel%20(2015).pdf
- 感情労働と心理的 well-being のレビュー: http://homepages.se.edu/cvonbergen/files/2013/01/Emotion-Work-and-Psychological-Well-Being_A-Review-of-the-Literature-and-Some-Conceptual-Considerations.pdf

**重要度**: ★★

---

### IDEA: 沈黙・不参加・未使用を第一級の観測にする

**出典**: good_echo_iss_sim_cursor_* `realism_contract` 第3条「会話しない・沈黙する・相手を避ける状態も有効な観測として表示する」／ goodecho_r README「使われなかった観察も実験の一部として記録する」／ my-social-agents `FUTURE_WORK.md` II-2(d)「沈黙・無言の選択」
**分類**: 創発設計

**内容**
3 リポが独立に同じ論点に到達している。Hop-Step-Jump は UI 契約として最初から仕様化、goodecho_r は HCD の設計思想として明文化（「田中幸子がオブジェクトを使わなかったことは設計通りの結果」）、my-social-agents は**やり残した課題**として挙げている（speak action に「無言」オプションがなく、距離が近づけば自動で会話が始まってしまう）。

**shibuya-simulation への適用案**
(a) 会話/誘いの action に**明示的な「何もしない・沈黙する・断らずに離れる」選択肢**を持たせる（現状 accept/reject の 2 値なら 3 値以上に）。(b) L2 に `unused_rate` 系列を追加: 施設・組織・SNS・選挙のそれぞれについて「使われなかった率」を出す。(c) ビューアで空白＝欠測ではなく「不使用」として明示表示。第64バッチで既に「承諾したが同席せず 0.337」を記録しているので、**不履行を欠陥でなく主要な観測として扱う**方向に踏み込む。

**web リサーチ知見**
ICE（Isolated, Confined, Extreme）環境研究では、**「社会的相互作用の量を自分で調節できること」が最も価値の高い設計要素**とされる。つまり「関わらない自由」の有無が環境設計の核心であり、沈黙/回避を選べないシムは現実から乖離する。
- ICE 環境の心理社会的問題: https://www.sciencedirect.com/science/article/abs/pii/S0149763421001494
- ICE 環境の内装設計と心理的健康の系統的レビュー: https://www.sciencedirect.com/science/article/abs/pii/S0272494426001155

**重要度**: ★★

---

### IDEA: 共通基盤帳簿（item 単位の provenance 追跡）

**出典**: my-social-agents `src/v3/poc_12agents.py:622-668` `render_common_ground`
**分類**: メモリ

**内容**
会話履歴を走査し、item_id（F1, W3 …）ごとに「あなた→相手」「相手→あなた」の初出方向を確定させ、プロンプトに「すでに交換済み（再発話・お礼禁止）」＋方向ラベル、「★未共有（memory にあって渡せる）」を注入する。「あなたが渡した情報に『ありがとう』を言うな」「相手から聞いた情報に『以前から知っていた』と言うな」という**メタルールまで明示**。LLM 会話の典型的破綻を世界側の帳簿で潰す。ただし著者は FUTURE_WORK で「人間の会話は記憶の曖昧さで重複や矛盾を許容する。bit-perfect な追跡は作為的」と自己批判している。

**shibuya-simulation への適用案**
当方のラベル伝播・噂・SNS について、**「誰が誰から、いつ、何を聞いたか」を item 単位の provenance 帳簿として持つ**。既に joint_invite.source（closeness / weak_tie / 内生経路）のラベル付けはあるので、これをラベル/語彙にも広げる。効果は 2 つ: (1) 会話の重複を減らして LLM 出力の質が上がる、(2) **伝播経路そのものが解析対象になる**（coin_label がどの経路で広がったか、弱い紐帯経由か強い紐帯経由かを事後追跡できる = Granovetter 検証の直接材料）。ただし bit-perfect にするか曖昧化するかは次の IDEA と表裏。

**web リサーチ知見**
一般手法名は会話論の grounding / common ground（Clark & Brennan 1991）。「現在の目的にとって十分な相互信念を確立するプロセス」で、提示と受容の反復で共通基盤を更新する。NLP では静的なシンボル接地ばかり研究され、**動的な会話的接地の評価枠組みは希少**という指摘があり、当方の provenance 帳簿はその空白を埋める実装例になりうる。
- Clark & Brennan (1991): https://philpapers.org/rec/CLABG-2
- 解説: https://www.maaike.ai/library/grounding-in-communication/
- Grounding Gaps in Language Model Generations: https://arxiv.org/pdf/2311.09144
- Talk is Cheap, Communication is Hard（動的接地の失敗と修復）: https://arxiv.org/pdf/2605.01750
- Conversational Grounding: 注釈と分析: https://arxiv.org/pdf/2403.16609

**重要度**: ★★

---

### IDEA: 不完全記憶（鮮明度 decay + 確率的欠落／改変）

**出典**: my-social-agents `docs/FUTURE_WORK.md` II-2(c)「不完全記憶」／ II-1(h)「共有基盤を計算で完璧に」への自己批判
**分類**: メモリ

**内容**
「memory に鮮明度スコアを持たせ、時間経過で曖昧化する。抽出時に確率的に entry を欠落／改変する。→『あれ、どこだったかな』『○○さんから聞いた気がする』」という提案。現状の v3 は `memory_max_age_ticks` で古い entry を drop するだけの hard cut。著者は「人間は忘れる、誤解する、思い込みで補完する」を表現できないことを課題として挙げている。

**shibuya-simulation への適用案**
当方の記憶に `vividness` を持たせ、時間と反復で増減させる。プロンプト投入時に vividness に応じて (a) そのまま、(b) 曖昧化（「たしか◯◯だったはず」）、(c) 欠落、を**決定論的ハッシュ**（agent, day, item の安定ハッシュ）で選ぶ——第64バッチの「乱数ゼロで安定ハッシュ」パターンをそのまま流用すれば CRN 共分散を壊さない。効果として、**噂の変異（誤情報の生成）が内生的に起きる**。ラベル伝播研究にとっては「伝わるうちに変わる」が観測できるのは大きい。既定 OFF、実験セルで ON という第63〜64バッチの流儀に乗せる。

**web リサーチ知見**
動的な会話的接地の失敗と修復（grounding failure / repair）を扱う研究があり、記憶の不完全さが交渉の破綻と修復をどう生むかの評価軸として使える。
- Talk is Cheap, Communication is Hard: https://arxiv.org/pdf/2605.01750
- Understanding Common Ground Misalignment in Goal-Oriented Dialog: https://arxiv.org/pdf/2503.12370

**重要度**: ★★

---

### IDEA: 発話前 Theory-of-Mind フィールドの構造化強制

**出典**: my-social-agents `src/v3/poc_12agents.py:124-152` `SpeakAction` の `partner_likely_knows` / `new_info_to_share` / `info_to_extract`
**分類**: LLM統合

**内容**
pydantic の `output_type` に ToM フィールドを必須で持たせ、**発話テキストを書く前に「相手が既に知っているはずのこと」を LLM 自身に列挙させる**。`new_info_to_share` は `partner_likely_knows` と重複させない規約。講評は「prompt engineering として高度」と D=9.0 の根拠に挙げた。

**shibuya-simulation への適用案**
当方の発話・誘い・SNS 投稿の構造化出力に、軽量な ToM フィールドを 1〜2 個足す。例: 誘い（joint_invite）を出す前に `partner_likely_busy: bool` と `why_this_person: str`。承諾判定（第62バッチの relations_endo）では既に構造化決定論抽出をしているので、**LLM 側にも「相手の状態の推定」を一言出させる**と、内生化の材料が増える。コスト増は出力トークン数のみ。注意点として、フィールドを増やすほど LLM が「フィールドを埋めるための思考」に引っ張られる（＝作為性が上がる）ので、既定 OFF + A/B セルで効果を測るのが当方の流儀に合う。

**web リサーチ知見**
Clark & Brennan の grounding の枠組みでは、話者は「相手が受容したか」を逐次確認しながら共通基盤を更新する。`partner_likely_knows` はこの presentation/acceptance サイクルを明示フィールド化したもの。
- https://philpapers.org/rec/CLABG-2
- Reflect, Not Reflex: Inference-Based Common Ground Improves Dialogue Response Quality: https://arxiv.org/pdf/2211.09267

**重要度**: ★★

---

### IDEA: 反 sycophancy の「変化なしを許可する」節

**出典**: hackathon_ `agent.py:_reflect_on_growth`（10日ごと）のプロンプト末尾「**If nothing meaningful has changed, say so honestly.**」
**分類**: LLM統合

**内容**
成長リフレクションのプロンプトは、他と違い**構造化出力を要求しない自由文**（"Respond ONLY with the 2-3 sentence reflection. No JSON. No preamble."）で、かつ「意味ある変化がなければ正直にそう言え」という逃げ道を明示している。結果は `evolved_perspective` として以後の全プロンプトに継続注入され、`perspective_history` に step 付きで蓄積される。「成長したことにする」sycophantic な出力への構造的対策になっている。

**shibuya-simulation への適用案**
当方の内省・日次計画・関係性評価の各プロンプトに、**「該当なし／変化なしを明示的に許可する句」**を統一的に足す。第62バッチで sycophancy 対策を入れているが、「変化なしの許可」は別軸。加えて、**「変化なし」と答えた率を L2 に列として出す**（`no_change_rate`）と、プロンプトが変化を強要していないかのモニタになる。この率が異常に低ければプロンプト側の誘導を疑う、というゲートにできる。

**web リサーチ知見**
本項は評価対象コードの観察に基づくもので、sycophancy 緩和の一次文献 URL は本調査では取得していない（正直に記録）。

**重要度**: ★★

---

### IDEA: 実行前 validate CLI と conf キー未参照検出

**出典**: good_echo_iss_sim_cursor_100s `sim_core/__main__.py`（`python3 -m sim_core validate --pack ... --scenario ...`）と `sim_core/domain_pack.py:158-208` `validate_domain_pack`（必須キー／必須ファイル／カラム別名／集団重みの検証）／ 反例として goodecho_r の `likely_uses` / `unlikely_uses`（personas.py に定義されているが `build_prompt` から一切参照されない＝設計だけあって未配線）
**分類**: その他

**内容**
Hop-Step-Jump 版は domain pack をシム実行前に検証する CLI を持ち、C=9.0 の根拠のひとつになった。一方 goodecho_r は「使いそう／使わなそうなオブジェクト」を 10 人分定義したのにプロンプトに配線しておらず、**さらに `likely_uses` に出てくる「共有日記」というオブジェクトが `world.py` に存在しない**（本調査で確認）。にもかかわらず README の考察には「Sofia: 共有日記・地球ビュー窓を積極活用」と書かれている。設計メモ → 実装 → 結果考察の 3 段で対象が食い違っている。

**shibuya-simulation への適用案**
2 本立て。(a) `python -m shibuya validate --conf conf/experiments/xxx.yaml`: 必須キー・KPI 列の存在・参照ファイルの実在・セル数と seed 列の整合を実行前にチェック。30 ラン × 6 セルを走らせてから設定ミスに気づく事故を防ぐ。(b) **conf キー未参照検出テスト**: conf の全キーを走査し、コードから一度も読まれないキーを警告する（意図的に未使用なら allowlist に登録）。逆方向（コードが読むが conf に無いキー）も。当方は conf キーが第62〜64バッチで急増しており、「実装したつもりで配線されていない」は現実的リスク。

**web リサーチ知見**
本項は実装作法であり、外部一次資料は参照していない（正直に記録）。

**重要度**: ★★

---

### IDEA: 介入と別イベントを隣接させない（交絡の回避）

**出典**: goodecho_r `agent.py:build_prompt` の Day25「【通知】今日でちょうど半分です」と Day26「【新しい設備】今日からアイテムが設置されました」が**1 日違いで隣接**
**分類**: 実験・評価

**内容**
A/B の転換点で、ナッジ投入（Day26）と「折り返し」告知（Day25）が隣接しているため、**A→B の差分がナッジ効果か折り返し告知効果か原理的に分離できない**。README の結論「乖離が 3.35 → 3.01 に縮小＝ナッジの効果」はこの交絡を含む。講評・検証者ともにこの点を指摘していないので、**評価をすり抜けた設計欠陥**でもある。

**shibuya-simulation への適用案**
条件切替を含む実験（前掲の transitions IDEA、k のヒステリシス IDEA を含む）で、**切替日の前後 ±N 日に他のイベントを置かないバッファ**を conf レベルで強制する（validate CLI で検査）。加えて当方の既存原則である sham/null 対照を、「切替の告知だけして中身を変えない」sham セルとして具体化する。第63バッチの 6 セル設計に「sham transition」セルを足す形。

**web リサーチ知見**
本項は実験設計の基本（交絡統制）であり、外部一次資料は参照していない（正直に記録）。

**重要度**: ★★

---

### IDEA: 屋内/屋外の情報遮断をラベル伝播に接続する

**出典**: good_echo_iss_sim_cursor_* `examples/spatial_demo/agent.py:107-128` `get_nearby_agents` の通信ルール（両者屋外 or 同一場所内のみ通話可能／片方が屋内で片方が屋外なら不可／異なる場所同士も不可）
**分類**: 世界設計

**内容**
物理的な情報遮断をコードコメントで契約化している。屋内にいると外の会話が一切届かない。これにより「どこにいるか」が「何を知れるか」を直接決める。

**shibuya-simulation への適用案**
当方は屋内 SFM 人流を既に持つので、**屋内/屋外の情報遮断を明示ルールとして入れ、ラベル/噂の伝播速度が場所構造に依存する**ようにする。効果: (a) 「渋谷のどこにいると情報が早いか」という空間的な情報格差が生まれる、(b) 弱い紐帯の橋渡し効果が**場所を跨ぐ移動と結びつく**（Granovetter の橋は物理的にも橋になる）、(c) k* が場所構造に依存するかを測れる（施設配置を変えた条件セル）。既存の joint/同席判定と整合させる必要があるが、当方の同席ロジックは既に場所単位なので接続は素直。

**web リサーチ知見**
アフォーダンス理論の観点では、場所は「行為可能性」だけでなく「知覚可能性」も規定する。ICE 環境研究でも「社会的相互作用の量を自分で調節できること」が最重要設計要素とされ、遮断できる場所の存在自体が価値を持つ。
- Gibson's Affordances: https://www.researchgate.net/publication/15176211_Gibson's_Affordances
- ICE 環境の心理社会的問題: https://www.sciencedirect.com/science/article/abs/pii/S0149763421001494

**重要度**: ★★

---

### IDEA: soft gating — 欲求階層をゲートでなく重みにする

**出典**: my-social-agents `docs/FUTURE_WORK.md` I-1(d) / I-2(c)、および講評 A=7.5 の減点理由（Maslow Lv1-3 のハードゲート、Big5 の離散 3 段階変換）
**分類**: 創発設計

**内容**
現状は「Lv1 が未充足なら Lv2 以上は絶対選べない」「★禁止: agent」「★禁止: weapon」というハードゲート、Big5 N/A → HP 閾値 150/200/250 と attack_for_food 可/緊急時/不可の離散 3 段階変換。著者は「実際には多動機並列（HP 削れてても友人を助ける、空腹だが趣味活動を続ける）」であり、**Maslow を強制ゲートでなく重みにして LLM に天秤を委ねるべき**と自己批判。講評もこれを A の減点理由かつ改善提言として挙げた（「連続値 + soft weighting に置換するとペルソナ間のニュアンス差と多動機並列性が表現可能になる」）。

**shibuya-simulation への適用案**
当方に Maslow 的な階層はないが、**同型の「ハード禁止」が無いか棚卸しする**。候補: 予定帳簿の当日衝突 veto（第62バッチ）、tier 遷移の条件、行動選択肢の事前フィルタ。これらが「物理的に不可能」なのか「普通はしない」なのかを区別し、後者は**選択肢から消すのでなく、コストや事前確率として渡す**（＝生データ化）。前者だけ veto に残す。第62バッチの合成式 `p = clamp(w·較正 + (1−w)·内生) − gossip` は既に soft な形なので、この思想を行動選択側にも広げる。

**web リサーチ知見**
本項は評価対象の自己批判とその追認に基づくもので、外部一次資料は参照していない（正直に記録）。

**重要度**: ★★

---

### IDEA: 外部統計 3 点で問いの必然性を作る導入

**出典**: hackathon_ スライド p2「問いの背景 — 経済成長と幸福の乖離」（世界3位圏 GDP／World Happiness Report 2024 で日本 55 位 Life Evaluation 6.147／所得はある閾値を超えると幸福との相関が弱まり主観的幸福感の最大予測因子は「社会的つながり」「自律性」「意味の感覚」）
**分類**: 提出物・審査対策

**内容**
自作シムの話を始める前に、**外部の公開統計 3 つだけで「この問いは解かれていない」を示す**。3 枚のカードで「経済は上位／幸福は下位／両者の相関には限界」と並べ、次のスライドで「だからルールを変えて比べる」に入る。B=9.0 の一因と考えられる。

**shibuya-simulation への適用案**
本選スライド冒頭を同型にする。当方の RQ「世界を変えようとする個体は生まれつきか環境から創発するか」に対する外部統計候補: 日本の開業率／起業無関心層の比率（GEM 等）、イノベーター理論の 2.5% という定説値、渋谷の昼間人口・流動人口。**3 枚で「変革者は稀で、その稀さの理由は個体差か環境かが分かっていない」を作る**。当方は既に calibrate REALITY で外部統計を扱う作法があるので、素材は集めやすい。

**web リサーチ知見**
スライド内に出典が明記されている（OECD How's Life 2024 / World Happiness Report 2024）が、当方では一次資料 URL 未確認のため、数値はスライドの記載どおりとして扱う（正直に記録）。理論側の裏づけとして SDT（自律性・有能感・関係性）が「社会的つながり」「自律性」の重要性を支持する。
- APA による SDT 解説: https://www.apa.org/research-practice/conduct-research/self-determination-theory
- Ryan & Deci 原典 PDF: https://uvi.edu/files/documents/College_of_Liberal_Arts_and_Social_Sciences/social_sciences/OSDCD/National_Self_Determination_Richard_Ryan_and_Edward_Deci.pdf

**重要度**: ★★

---

### IDEA: 提出物生成コードへの投資比率を意識的に決める

**出典**: hackathon_ のコード内訳（シム本体 2,641 行 vs 提出物生成 `make_*.py` + `visualize_paper.py` + `visualization.py` 6,461 行 = **本体の 2.4 倍**、分析 2,188 行、`output_*` 32 ディレクトリ、世界別 mp4 11 本）／ 対照として good_echo_iss_sim_cursor_100s は動画生成を足したのに 50s より 0.5 点低い
**分類**: 提出物・審査対策

**内容**
hackathon_ は C=8.0 / D=8.0 と本体の点は突出していないのに総合 6 位。A（創発設計 9.0）と B（世界設定 9.0）に加え、「見せる」への大量投資が効いた可能性が高い。一方 100s 版は `generate_video.py` を追加したが D の減点（temperature が `del` される・肥大化・seed なし）を埋められず 50s より低い点になった。**つまり見せる投資は A/B を持っている作品には効くが、D の穴は埋めない**。

**shibuya-simulation への適用案**
当方は make_viewer / make_endo_report を持つ。本選に向けて (a) **D（技術実装）の穴を先に潰す**（当方の場合 1725 テスト・決定論・CRN があるので比較的強い）、(b) その上で「世界別/条件別の自動生成物」を増やす。具体案: k 水準ごとの短尺動画、k* 前後の比較ダッシュボード、ピッチ用サマリ画像の自動生成。ただし**提出物生成コードが本体の 2 倍を超えるのは当方の研究品質重視の方針とは合わない**ので、上限（例: 本体の 30%）を先に決めてから作る。

**web リサーチ知見**
本項は評価対象のコード計量と点数の対照に基づくもので、外部一次資料は参照していない（正直に記録）。

**重要度**: ★★

---

### IDEA: ハイブリッド認知 — 重要な瞬間だけ詳細思考

**出典**: my-social-agents `docs/FUTURE_WORK.md` III-3「計算コスト vs リアリズム: 高頻度 LLM 呼び出しでもっとリアルになるがコスト爆発。**重要な瞬間にのみ詳細思考、それ以外は heuristic に倒すハイブリッド設計が必要**」／同スライド p8「今後、より大規模なシミュレーションを行うには、軽量な人格フレームや会話フレームを探す必要があるのではないか」
**分類**: 規模化・性能

**内容**
6 体 × 10,000 tick を回した著者が到達した結論。全 tick で LLM を叩くのではなく、閾値を超えた瞬間だけ詳細思考に切り替える設計を課題として提示している。同作は既に `asyncio.create_task` でブレイン呼び出しを fire-and-forget して tick をブロックしない設計を持つ。

**shibuya-simulation への適用案**
当方の本番方針は「人数 > 時間・100体・現実忠実」なので、この問題に正面から当たる。設計案: **LLM 呼び出しトリガを世界側のイベントで決める**（他者との遭遇、組織/選挙イベント、ラベル初出、承諾/拒否の分岐点）。それ以外の時間帯は決定論ヒューリスティクスで動かす。当方は既に「always-draw conditionally-use」で CRN 共分散を保つ設計を持っているので、**呼び出しの有無が変わっても乱数消費を変えない**形（呼ばない場合もダミー消費）にすれば CRN が壊れない。呼び出し率を conf 化して A/B すれば「詳細思考の density が k* に効くか」という研究上の問いにもなる。

**web リサーチ知見**
本項は評価対象の自己分析に基づく。関連して、長期社会シミュレーションのためのマクロ/ミクロ結合研究は、全エージェントを常時高解像度で回さずマクロ側で近似する方向を扱っている。
- Coupling Macro Dynamics and Micro States for Long-Horizon Social Simulation: https://arxiv.org/html/2604.05516v2

**重要度**: ★★

---

### IDEA: CLI LLM バックエンドの運用堅牢化パターン

**出典**: good_echo_iss_sim_cursor_100s `scripts/run_cursor_prompt.sh`（214 行、`mkdir` によるアトミックロック・EPROTO リトライ・Python 指数バックオフ・exit code と空 stdout の個別エラー扱い・stderr 捕捉）／ `examples/spatial_demo/llm_backends.py:140-243` `CommandLLMClient`（max_retries / retry_backoff_seconds / timeout_seconds / ANSI エスケープ除去 / stdout 正規表現フィルタ）
**分類**: LLM統合

**内容**
Claude Code / Codex / Cursor といった **CLI ツールを LLM バックエンドとしてバッチ実行する**ための実務ノウハウ。`mkdir` がアトミックであることを利用した排他ロック、ANSI エスケープの除去、stdout の正規表現フィルタ（CLI が出す進捗表示を捨てる）。ただし `del temperature; del max_tokens` で温度制御が捨てられている点は講評の減点対象。

**shibuya-simulation への適用案**
当方は API バックエンドが主だが、(a) **sweep の並列実行における排他制御**にアトミック mkdir ロックは流用できる（Windows でも mkdir はアトミック）、(b) 本選のハードウェア想定（データセンタ 1 台 7 GPU / ops トポロジ A）でローカル LLM を複数プロセスから叩く場合の排他に同じパターンが使える、(c) リトライ・タイムアウト・バックオフの構成（max_retries / retry_backoff_seconds / timeout_seconds を conf 化）は当方の model.backend 設定に足せる。**教訓としては「CLI をバックエンドにすると温度が制御できなくなる」**——決定論を重視する当方は API 経路を維持すべき。

**web リサーチ知見**
本項は実装作法であり、外部一次資料は参照していない（正直に記録）。

**重要度**: ★

---

### IDEA: ドキュメントと conf の主要パラメータを突合するテスト

**出典**: 本調査で発見（両講評とも未指摘）— good_echo_iss_sim_cursor_50s の README が 100s 版のもので、`steps: 50` / DEBR イベントなしの実パックと食い違っている（README は「10人/100ステップ」「Day50 に宇宙デブリ衝突」「S65-S100: DEBR05」と記述）。さらに README のクイックスタート手順 1 `python3 -m sim_core validate` は 50s に `sim_core/__main__.py` が無いため動かない
**分類**: その他

**内容**
50s と 100s の README を diff すると**最終行のリポ名 1 行を除いて完全に同一**。姉妹リポとして条件だけ変えて出す際に、README を更新し忘れた（あるいは共通化した）結果、**低い方のリポの README が自分の設定を説明していない**状態になっている。評価側もこれを検出していない。

**shibuya-simulation への適用案**
`docs/` と `conf/` の主要パラメータ（体数・日数・k 水準・seed 列・セル数）を突合するテストを 1 本足す。実装は簡単で、docs 内の記述をパースするのではなく、**docs 側に埋め込みマーカーを置いて conf から自動生成**する方式が堅い（例: `<!-- AUTOGEN:endogenous_accept.cells -->`）。当方は devlog を毎回追記し、計画書のステータスも更新する運用（第63バッチで実施）なので、記述と設定の乖離は現実的リスク。

**web リサーチ知見**
本項は実装作法であり、外部一次資料は参照していない（正直に記録）。

**重要度**: ★

---

## 総括: このグループから読み取れる評価軸の構造

同一作者・同一 LLM の 2 作品（hackathon_ 34.0 / goodecho_r 24.5）の差分内訳が、評価軸の構造をそのまま示している。

| カテゴリ | hackathon_ | goodecho_r | 差 | 何で決まったか |
|---|---|---|---|---|
| A 創発設計 | 9.0 | 5.5 | **−3.5** | エージェント間相互作用経路の有無 |
| B 世界設定 | 9.0 | 8.0 | −1.0 | ほぼ保存（テーマの鋭さは両方ある） |
| C 発展性 | 8.0 | 6.0 | −2.0 | 設定外部化・将来展望の記述 |
| D 技術実装 | 8.0 | 5.0 | **−3.0** | メモリ・再現性・エラー処理 |

**良いテーマは B にしか効かない。** A は「世界ルールの精度 × 行動自由度」の積なので、相互作用経路が無ければ自由度がいくら高くても集団創発は原理的に起きず落ちる。

また 5 リポ全体を通して、**A で満点近くを取りつつ B も高い作品は第1回に存在しなかった**（B10 は A7.5、A9 は B9）。shibuya-simulation は no-fingerprint 原則で A 側の設計思想を既に持ち、決定論/CRN/permutation 検定で D も強い。**残る課題は B（先行理論への接続と、相転移という発見の提示）に集中している**——前掲の ★★★ IDEA「相転移を見つけたを主張の形に落とす」がこのグループから得られた最大の学び。
