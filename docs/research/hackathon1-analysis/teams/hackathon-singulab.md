# hackathon-singulab(Karesansui・8位・33.5/40)

**講評スコア**: A 創発設計 8.0 / B 世界設定 9.0 / C 発展性 8.5 / D 技術実装 8.0 = **33.5**
(Run1 34, Run2 33。`_eval_review` 判定「妥当。引用精度は極めて高く、誇張・捏造は確認されず」)

**リポジトリ**: https://github.com/karesansui-u/hackathon-singulab
**規模感**: 202 MB / 478 ファイル。Python は `scripts/` に 6,223 行(最大 `run_civilization_os_llm_demo.py` 1,705 行)、`sim_core/` 429 行(汎用フレーム)、`domain_packs/agi_youth_japan/` に TSV データ約 25 本 + プロンプト md。出力は `public/data/runs/<scenario>_83steps_panel48/` に TSV 群。GitHub Pages で観測ビューアと発表スライドを公開。

## どんなシムか

「制度導入前に、シミュレーションでデバッグする」がコンセプトの**制度設計シミュレーター**。AGI・AIロボ普及後の日本を舞台に、施策が人間の感情・行動・不信・疲労・制度利用へどう変換されるかを観測する。LLM を会話相手ではなく **観測センサー**として使い、国家30・組織15・個人60 + 次世代コホートの反応を row データ(`country_turns.tsv` / `organization_turns.tsv` / `agent_turns.tsv` / `child_cohorts.tsv`)へ保存する。閉ループは「世界イベント → 国家反応 → 日本社会状態 → 組織反応 → 個人反応 → 社会フィードバック → 政策AI調整」。83 step で直近5年を月次、以降を年次〜5年単位に伸ばし **100年観測**まで届かせる。比較シナリオは8通り(`no_intervention` / `birth_grant_only` / `structure_intervention` / `structure_birth_grant_package` / `structure_hope_family_package` / `policy_search_no_sustain` / `policy_search_with_sustain` / `policy_search_with_sustain_hope_family`)。独自概念として**構造持続通貨 nat** と**制度ストレステストエージェント8体**を実装。

## 講評の要点

**強み**
- **「LLM を観測器として使う」思想がプロンプト・コード・ドキュメントの全レイヤーで一貫**。「エージェント本人へ『不安になれ』『希望を持て』『抗議しろ』と命令しない」「`event.direction` は『こう変化させろ』という指示ではなく、社会状態の説明ラベル」と明文化されている(A8.0 の主因)。
- B 9.0: 題材の独自性と社会的意義がともに極めて高い。nat・ストレステストエージェント・100年観測という**独自の概念装置を実装まで落とし込んでいる**点を評価。
- C 8.5: `sim_core/` + `domain_packs/` のドメインパック方式が**最初から第一級概念**。継承(`inherits: default_v1`)・deep_merge・トークン置換・validation・9段階 hooks が揃う。
- D 8.0: 3層プロンプト(出力契約/世界条件/人間反応)、Claude CLI / Codex CLI 切替、`--max-budget-usd` 制御、多段 JSON 抽出、per-agent 3回リトライ、`step_complete` 冪等再開、`memory_update`/`carryover_concern`/`side_effect`/`fairness_perception`/`policy_fatigue` という**意味ラベル付き構造化メモリ**、次世代コホートへの希望/不信/連帯**継承係数**。

**弱み・改善提言**
- 4本の runner で `run_claude` / `run_codex` / `extract_json_from_text` / `is_codex_model` が**重複実装**。共通 LLM クライアントへ抽出すべき。
- 各 runner が 1,500-1,700 行に達し、prompt 組立・JSON 処理・正規化・I/O が同一モジュールに同居。
- **A が 9-10 に届かなかった唯一の理由**: `normalize_emotion` 等の正規化が評価×感情の組合せを強く固定するため、「LLM が意図的に出した境界感情が中央値に丸められる可能性がある」。出力契約が強すぎて自由度がやや絞られる。
- 単体テスト・LLM 応答 fixture が無い。Ollama/Gemini 等のバックエンドアダプタを足せば CLI サブスク依存から脱せる。
- `_eval_review` の指摘は軽微1点のみ: 国家目的関数を「9次元」と書きつつ列挙は8項目(「国家構造の存続」が漏れ)。

## コード実査で面白かった点

1. **プロンプト冒頭の「レイヤー宣言」**。`run_civilization_os_llm_demo.py:917-920` は自分のプロンプトの構造をプロンプト内で自己申告する:
   ```
   - 出力契約: JSON形式、観測項目、分類語彙、短さは実装上の制約として固定する。
   - 世界条件: エージェント属性、世界状態、…は観測条件として固定する。
   - 人間反応: その条件で本人がどう知覚し、どう感じ、どう動くかは固定しない。
   ```
   **「何を固定し何を固定しないか」を宣言してから中身を渡す**という順序。no-fingerprint 原則の自己文書化として非常に真似しやすい。

2. **「観測原則」がシコファンシー(迎合)対策そのもの**。「望ましい発表ストーリーに合わせる必要はありません」「全員が同じ方向に動くとは限りません」「大きな事件が起きても、本人に届かなければ反応は小さくてよい」「支援が届いた層と届かない層…平均値だけに寄せず、**二極化や対象外反発を自然に出してください**」。**介入が効かないことを明示的に許可する**プロンプト設計。

3. **バイアスの両方向に釘を刺している**。単に「悲観に寄せるな」ではなく「不安が少し残るだけで自動的に注意へ固定しないでください」と**楽観方向にも悲観方向にも**同じ分量で歯止めを書いている。一方向だけの是正はそれ自体が誘導になるという理解。

4. **`thought` / `private_talk` / `social_post` の3層発話分離**。内心(本音・未言語化の不安)/ 友人との会話(砕けた口調・弱音)/ SNS 発信(見られる前提)を**別フィールドとして同時に観測**し、字数上限も 90 / 80 / 60 字と分けている。「同じ人物の同じ step でも文脈により言うことが違う」を構造として取り出している。

5. **副作用が第一級の観測項目**。`side_effect` の語彙は「対象外感 / 監視疲れ / 財政不安 / 強制感 / 手続き疲れ / 政策疲労 / 実装不信 / なし」、`adjustment_request` は「対象条件の説明 / 手続き簡素化 / 地域枠追加 / 財源説明 / 一時停止 / 補完支援 / 非強制説明 / なし」。**施策が効いたかだけでなく、どう嫌がられたかを型で持つ**。

6. **入れ子閉ループ = LLM 政策プランナー**(`run_policy_planner_llm_demo.py`)。「平均値を良く見せるのではなく、**悪化している層、副作用、二極化、政策疲労を見て**次の政策アクションを提案します」。政策アクション語彙は `maintain / amend / sequence / explain / localize / simplify / pause / rollback / compensate / add` の10種で、**「やめる」「戻す」「一時停止する」が最初から選択肢にある**。さらに各施策に `budget_cost_0to1`(合計1.0以内)・`implementation_lag_steps`・`duration_steps` を持たせ、**予算制約と実装遅延を型で強制**している。

7. **探索空間に `not_allowed` を明示**。`scenario_policy_context` は `allowed` と並んで `not_allowed` を持ち、`policy_search_with_sustain_hope_family` では「出生や家族形成の強制」「**希望感情の直接命令**」「副作用や財源説明を省いた拡大」「非婚・非出産の選択を不利益化する設計」を禁じている。**「感情を直接命令する施策」を探索空間から機械的に除外する**という発想。

8. **`step_complete` による冪等再開**。`ids_completed_for_step(path, step, id_field)` が出力 TSV を読んで「この step で完了済の ID 集合」を作り、`expected_ids` が部分集合なら phase をスキップして `run_log.tsv` に `status=skipped` を記録する。**出力ファイル自身が進捗チェックポイント**になっており、別途の state ファイルが要らない。

9. **9段階 hooks**(`sim_core/hooks.py`): `pre_run / pre_step / pre_observation / post_observation / aggregate / feedback / post_step / export_viewer / audit`。`audit` が独立ステージとして最後にあるのが特徴的。

10. **通貨設計のガードレールが TSV で外出し**。`structure_sustain_guardrails.tsv` に「統治分離、権利床、**反実仮想事前登録**、個人監視禁止」。発行量は「**介入なし/介入ありの差分**から推定」= 反実仮想比較を通貨発行の根拠に据えている。`structure_sustain_anomaly_audit.tsv` は「申請成果と実測 row、類似集団、長期副作用、サブグループ分布の乖離」からゲーム化を検出する設計。**LLM エージェントは通貨発行額を決めない**(観測 row を出すだけ)と役割分離が明記されている。

11. **ストレステスト用の運用ポリシーが別 TSV**(`structure_stress_test_run_policy.tsv`): 「通常ステップでは2-3体、重要イベント時は8体」= LLM 予算のための**サンプリング運用が設計として文書化**されている。

## shibuya-simulation に活かせそうな点

- **プロンプト冒頭の3層宣言**(出力契約 / 世界条件 / 人間反応)をそのまま導入価値あり。shibuya-simulation の no-fingerprint 監査は「行動指示が無いこと」を確認する側だが、**プロンプト自身に「何を固定しないか」を書かせる**と、ゴールデンテストで宣言部の diff を見るだけで原則違反を検出できる。
- **「効かないことを許可する」プロンプト節**。k* 掃引で「介入したのに何も起きない」が正当な観測値であることを明示する節を、REALITY 較正まわりのプロンプトに入れておきたい(sycophancy 対策として第62バッチの hedge_markers と同系統だが、こちらは**プロンプト側で先に許可を出す**アプローチ)。
- **`thought` / `private_talk` / `social_post` の3層発話**は shibuya-simulation の SNS 機能と非常に相性が良い。現状の発話と SNS 投稿を「同一 step の別文脈」として同時生成し、**内心と公開発言の乖離**を指標化できる(ラベル伝播研究では「公に言う語」と「内心で使う語」のズレが核心になりうる)。
- **副作用語彙の型化**。「世界を変えようとする個体」の観測でも、成功指標だけでなく「疲労 / 対象外感 / 不信 / 強制感」に相当する**離脱・反発の型**を持つと、k* の相転移が「参加の増加」だけでなく「反発の増加」としても見えるようになる。
- **政策アクション語彙に `pause` / `rollback` / `compensate` を入れる**。組織・選挙機能で内生的な施策生成を扱うなら、「増やす」だけでなく「やめる」「戻す」を最初から語彙に持たせないと単調増加のバイアスが出る。
- **`not_allowed` リスト**。shibuya-simulation で組織や候補者が施策を作る場合、「感情の直接命令」を禁止項として機械的に弾く仕組みは no-fingerprint 原則の内生版として使える。
- **出力ファイルを進捗チェックポイントにする `step_complete` 型冪等再開**。長時間ランの mid-day resume で、別 state ファイルと実出力のズレを構造的に無くせる(第62バッチで `_joint_day` の checkpoint 未保存ギャップを直したのと同じ問題への別解)。
- **反実仮想事前登録(pre-registration)をデータとして持つ**。`structure_sustain_guardrails.tsv` の発想は、shibuya-simulation の実験プロトコル(`conf/experiments/*.yaml`)に「この実験で何を主検定にするか」を**ランの前にファイルとして固定**する運用と合致する。すでに第63バッチで sign-flip permutation の主/副検定を決めているので、その延長で「事前登録 TSV」を出力に同梱する形にできる。

## web リサーチ

- **GPLab: A Generative Agent-Based Framework for Policy Simulation and Evaluation**(JASSS 29(1)6)。LLM 駆動の政策シミュレーション枠組みで、Social Agents / Social Subsystem / Simulate & Evaluate の**3層アーキテクチャ**。本作の「観測レイヤー5層」と発想が近く、学術側に同型の先行がある。 https://www.jasss.org/29/1/6/6.pdf
- **PoliSim @ CHI 2026: LLM Agent Simulation for Policy**。政策向け LLM エージェントシミュレーションのワークショップが CHI 2026 に立っており、この領域が学会トラックとして成立し始めている。 https://dl.acm.org/doi/10.1145/3772363.3778738
- **Validation is the central challenge for generative social simulation: a critical review of LLMs in agent-based modeling**(Artificial Intelligence Review, Springer 2025)。生成的社会シミュレーションの中心課題は妥当性検証であるというレビュー。本作が「制度導入前のデバッグ装置」と限定的に位置づけているのは、この批判に対する誠実な間合いの取り方といえる。 https://link.springer.com/article/10.1007/s10462-025-11412-6
- **Stop Drawing Scientific Claims from LLM Social Simulations Without Robustness Audits**(arXiv 2605.18890)。LLM 社会シミュレーションから科学的主張を引くにはロバストネス監査が必須という論文。shibuya-simulation の k* 主張にも直接刺さるので、第63バッチの permutation 検定と併せて参照価値が高い。 https://arxiv.org/pdf/2605.18890
- **Agentic AI for Sustainable Development: Leveraging LLM-Enhanced Agent-Based Modeling for Complex Policy Strategies**(2025)。ABM と LLM 自律エージェントの収束が複雑政策戦略に有効という総説。 https://journals.sagepub.com/doi/full/10.1177/27523543251365678
