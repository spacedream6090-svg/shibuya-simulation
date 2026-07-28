# hackathon-singulab-inu(Karesansui・11位・33.0/40)— GOOD ECHO

**講評スコア**: A 創発設計 7.0 / B 世界設定 9.0 / C 発展性 9.0 / D 技術実装 8.0 = **33.0**
(Run1 33, Run2 33。`_eval_review` 判定「妥当(微調整余地あり)」— A のみ「やや厳しめ。realism_contract を加味すれば 7.5 まで上振れ余地あり」)

**リポジトリ**: https://github.com/karesansui-u/hackathon-singulab-inu
**規模感**: 13 MB / 522 ファイル。`examples/spatial_demo/` 3,503 行(2D 空間エンジン)、`scripts/` 5,092 行、`sim_core/` は姉妹リポと共通の汎用フレーム。ドメインパックは **2本**(`iss_benevolence` + `agi_youth_japan`)。GitHub Pages で ISS ハビタットのデモを公開。

## どんなシムか

**GOOD ECHO** = 「善性を個人の性格だけに任せず、空間・物・ルール・会話の設計によって支えられるか」を検証するプロジェクト。ISS のような閉鎖環境に 20 人の HCD 設計ペルソナ(難民 Amir、義足の Aisha、識字率の低い Tariq 等)を置き、資源圧力・プライバシー圧力・対人緊張・ルーティン疲労・通信遅延の 5 種の圧力フィールドが閾値を超えると自動イベントが発火する。介入要素はナッジオブジェクト10種(持ち寄り棚 / 話しかけてOKサイン / リソース・スコアボード / 個室聖域マーク / モジュール移動投票パネル 等)とルール(短い確認・静穏時間・再開時刻)。**A(ナッジなし)/ B(標準ナッジ)/ C(途中でナッジ撤去)/ D(ルールのみ)/ E(ナッジのみ)の5条件**に加え、「修復イベントなし」「喧嘩イベントなし」の補助軸で比較する。中心仮説は「**ナッジは仲直りを作ったのではない。仲直りしなくても戻れる道を作った**」という再フレーミング。

## 同一作者2本の設計差(最重要の観察)

| | hackathon-singulab | hackathon-singulab-inu(GOOD ECHO) |
|---|---|---|
| スコア | A8.0 B9.0 C8.5 D8.0 = 33.5 | A**7.0** B9.0 C**9.0** D8.0 = 33.0 |
| 世界の持ち方 | **空間なし**。国家/組織/個人/次世代の階層 row のみ | **2D 空間あり**(`examples/spatial_demo/`。座標・移動・通信半径・定員) |
| ドメインパック | 1本(agi_youth_japan) | **2本**(iss_benevolence + agi_youth_japan)= 汎用性を実証 |
| LLM バックエンド | Claude CLI / Codex CLI | `LLMClientProtocol` で **Ollama / Claude CLI / Codex CLI / Cursor CLI** を抽象化 |
| 比較条件 | 8シナリオ(制度パッケージの組合せ) | 5条件 A/B/C/D/E + 補助軸2本 |
| 減点の主因 | 出力語彙の `normalize_*` が強すぎる | **ポストプロセスの会話再生成が語彙を制限している** |

- **C が 8.5 → 9.0 に上がった理由**は「2つ目のドメインパックの存在が再利用性を実証している」こと。**同じフレームで別題材を実際に1本作ったこと自体が加点**になっている。フレームワークを謳うなら2本目を作れ、という明確な教訓。
- **A が 8.0 → 7.0 に下がった理由**は空間エンジンのせいではない。コアエンジン(`agent.py` の message / action プロンプト)は「数値と場所説明のみを渡し、行動は `move/stay` + 自由記述 memory/reasoning で完全自由」という**満点級**の設計だと講評自身が認めている。減点は **UI 用の会話再生成スクリプト `generate_habitat_conversations.py`** に、tone 許容集合(`normal/caution/trouble/repair/nudge` を会話タイプごとに絞る)と語彙禁止リスト(`rule_only_no_nudge_objects` の時は「ナッジ」「善性オブジェクト」「持ち寄り棚」という語を出すな)が入っているため。
- 講評の提言は的確: 「**ポストプロセスをオプション化するか、『観測のみ』と『再生成』で記録を二系統に分ける**とさらに堅牢になる」。`_eval_review` はさらに「これは UI 用の別レイヤーでありシミュレーション本体の自由度は下げていないと扱えば 7.5〜8.0 でも妥当」と留保している。
- **教訓**: 本体が no-fingerprint でも、**観測者が実際に見る成果物(動画・UI)を作る後処理に誘導が入ると A が落ちる**。shibuya-simulation の 2D/3D ビューア・レポート生成が生データからの写像に留まっているか(語彙の付け替え・整形をしていないか)を確認する価値がある。

## 講評の要点

**強み**
- B 9.0: ISS 閉鎖環境 × HCD 20 ペルソナ × 5条件対照実験。「ナッジは仲直りを増やすのではなく、仲直りしなくても戻れる道を作る」という**非自明な再フレーミング**が高評価。災害避難所・病棟・介護施設・寮・船舶への転用構造まで明示。
- C 9.0: `sim_core` のドメインパック汎用フレーム(deep_merge 継承・`${pack}`/`${root}` トークン置換・validation report・hooks)と、**20 以上の runtime profiles 登録**(Claude/Codex/Cursor × smoke/full × 条件別)。
- D 8.0: `LLMClientProtocol` 抽象化、CLI 用 `CommandLLMClient`(リトライ/タイムアウト/ANSI 除去/stdout フィルタ/JSON フィールド抽出)、LLM 自己生成メモリの FIFO 管理、4フェーズ同期実行、`previous_fire_exposure`/`previous_place_occupancy` を step 開始時に凍結してレース回避。

**弱み・改善提言**
- 上記のポストプロセス語彙制限(A の減点主因)。
- `random.seed` の明示が見当たらず、CLI バックエンドの非決定性も加わり厳密な再現性確保に追加の仕組みが要る。
- 約 4,000 行に肥大化し、ISS 実験では使わない economy / fire レイヤーが残っている。**ドメインパックごとに不要レイヤーを明示的に無効化する仕組み**が欲しい。
- `_eval_review` の見落とし指摘: `domain.yaml` の `realism_contract` が講評で言及されていないが、これは自由度を強く保証する設計で A の加点材料になり得た。

## コード実査で面白かった点

1. **`realism_contract`(`domain_packs/iss_benevolence/domain.yaml:218-223`)が可視化層に対する反シコファンシー契約になっている**:
   ```
   - UI表示は、agent state / place capacity / event / conversation / relationship_seed から導出する
   - 会話しない・沈黙する・相手を避ける状態も有効な観測として表示する
   - 位置と寝床割当はstepごとに連続性を持たせ、毎描画でランダムに変えない
   - Run Bの改善は万能にせず、短い摩擦・遅れた修復・ナッジの押しつけ感も残す
   ```
   「**介入条件を良く見せるな**」を YAML に書いて契約化している。可視化が結論を先取りするのを防ぐ仕掛けとして秀逸。

2. **`auto_pressure_rules` が閾値 → 状況ラベルの変換に徹している**。`resource_pressure > 60` で発火するイベントの `direction` は「緊張↑ 協力必要性↑」、`input_text` は「水・酸素・食料の節約意識が高まり、個人行動と共同責任の緊張が出る。」= **状態の記述であって行動の指示ではない**。5つの圧力(資源 / プライバシー / 対人緊張 / ルーティン疲労 / 通信遅延)にそれぞれ閾値 55〜60 が設定されている。

3. **観測優先順位がプロンプトに明示されている**(`agent_turn_runner.py` neutral_v2):
   ```
   1) 指示の最適化ではなく、自然な反応分布を優先する
   2) 全員を協力方向へ誘導しない
   3) 不安・撤退・沈黙などの反応も、条件に整合するなら正当な観測値として扱う
   ```
   さらに「event.intensity は圧力の強さを示す観測パラメータです。高強度では、**防衛反応・相談遅延・短期志向の増加を許容してください**」— 圧力を上げたら協力が増える、という素朴な期待に先回りして歯止めをかけている。

4. **ネガティブ結果を正直に書いている**。README は「喧嘩イベントなし条件では形式的な `conflict` は A/E とも **0** でした。したがって『LLM エージェントが自然に喧嘩を始めた』とは言いません」「創発を言うなら、衝突の自然発生ではなく、**摩擦後にどう戻るかの作法**として読むのが安全です」と明記。**主張を観測が支える範囲まで縮める**姿勢。

5. **「率は変わらないが経路が変わる」という発見の切り方**。修復イベントなし条件で修復的 status 率は A 約60% / E 約61% とほぼ同じ。差が出たのは**媒介物語彙の行数**(D=0 vs E=164、A/E 補助軸では E=57)。つまり「**何回仲直りしたか**」ではなく「**何を介して戻ったか**」を数える指標を新設したことで、率が同じでも差を検出できた。
   - A(ナッジなし): 「ごめん」「言いすぎた」「短く確認しよう」= **人格に直接踏み込む**修復
   - E/B(ナッジあり): 「持ち寄り棚で」「OKサインの下で」「スコアボードを見ながら」= **第三項を介した**修復
6. **ルールとナッジの機能分離**が結論として抽出されている: 「ルール = これ以上踏み込まない**境界**を作る / ナッジ = ここからなら戻れる**接点**を作る」。D 条件(ルールのみ)は「会話を短く閉じる力が強い」。介入を1種類にせず2種類に割って比べたから出た知見。

7. **修復ラグの操作的定義**(`analyze_iss_pair.py`): conflict イベントの発生 step から `repair_window = 3` step 以内に**同一ペア**で repair tone / repair キーワードのメッセージが出たかで `repair_after_conflict_rate` を計算。ペアを `undirected`(無向)で正規化して数えている。あわせて発話量の `_gini`、`bridge_agents`(橋渡し役)も算出。

8. **20以上の runtime profile を YAML に登録**。`claude_smoke_a` / `codex_fast_20x100_e_all_no_repair` のように「バックエンド × 速度 × 規模 × 条件」を名前で引ける。`scripts/run_profile.py --pack ...` で起動。**実験セルの命名規約がそのまま実行エントリポイント**になっている。

9. **`LLMClientProtocol`(Protocol 型)で4種のバックエンドを差し替え可能**にし、CLI 系は `CommandLLMClient` が ANSI エスケープ除去・stdout フィルタ・JSON フィールド抽出まで面倒を見る。サブスク型 CLI(Claude Code / Codex / Cursor)を LLM バックエンドとして使う実装パターンとして参考になる。

## shibuya-simulation に活かせそうな点

- **「観測系と提示系を分ける」規律**。A 減点の原因がポストプロセスにあったのは重い教訓。shibuya-simulation の `make_viewer` / `make_endo_report.py` が「生データの写像」に徹しているか、語の言い換え・トーン整形をしていないかを一度監査したい。分けるなら `raw` と `presented` の二系統でログを残す。
- **`realism_contract` を YAML 契約として持つ**。「介入条件を良く見せない」「効かなかった部分を消さない」を実験設定ファイルに書き、ゴールデンテストで契約項目の存在を検査する、という運用ができる。
- **「率」ではなく「経路」を測る指標を作る**。shibuya-simulation の関係内生化でも、承諾率(第62バッチで 0.601)や履行率(0.337)といった率に加えて、「**何を介して**その関係が成立したか」= 媒介語彙・媒介チャネルの分布を数える軸を足すと、率が動かない条件間でも差が出る可能性がある。第64バッチの `joint_invite.source`(closeness / weak_tie / 内生経路)はまさにこの「経路」指標の芽なので、媒介物語彙に相当する**発話中の媒介語カウント**まで伸ばせる。
- **介入を「境界を作るもの」と「接点を作るもの」に割る**。ラベル伝播や組織形成で介入を試すとき、1種類の強度を振るのではなく機能の異なる2種類を直交させると解釈可能性が上がる。
- **圧力フィールド → 閾値 → 状況ラベルの3段構成**。SFM 人流の混雑・待ち時間などの物理量を、閾値超えで「状況の説明ラベル」に変換してプロンプトへ渡す型は no-fingerprint を保ったまま環境圧力を効かせる実装として直輸入できる。
- **「主張を観測が支える範囲まで縮める」書き方**。「自然に喧嘩を始めたとは言いません」に相当する留保を、k* の主張でも同じ粒度で書く準備をしておく(第63バッチの「小 seed 数の検出力限界を出力に正直注記」と同じ精神)。
- **runtime profile の命名 = 実験セル ID**。第63バッチの `conf/experiments/endogenous_accept.yaml` の6セルにも、`endo_on_k3_crn` のような引ける名前を付けておくと再走・再現の手間が下がる。

## web リサーチ

- **ICE 環境(Isolated, Confined, Extreme)の行動健康研究**は本作の題材そのものの学術的裏付け。NASA HRP は "Isolation and Confinement" を5大ハザードの1つに位置づけている。 https://www.nasa.gov/hrp/hazard-isolation-and-confinement/
- **Social interactions in isolated, confined, and extreme environments: A study of Antarctic winter teams using wearable sensors**(PNAS 2026)。南極越冬隊をウェアラブルセンサーで追跡し、孤独感と対立が**進行的に増加**すること、**近距離の接触が対立と被害妄想的思考に結びつく**こと、**国籍による社会的断片化**が起きることを報告。本作の「混雑 → 対人摩擦 → 修復」というモデル化は実証研究と整合的で、かつ「近距離接触が必ずしも良くない」という点は GOOD ECHO の「押しつけ感も残す」契約と符合する。 https://www.pnas.org/doi/full/10.1073/pnas.2533420123
- **Space Analogs and Behavioral Health Performance: review and recommendations checklist from ESA Topical Team**(npj Microgravity 2024)。アナログ環境の利点として「**焦点を絞った心理的介入を実験的に検証できる**」ことを挙げており、本作が LLM シム上で A/B/C/D/E 介入を比較したのはこの系譜のシミュレーション版と位置づけられる。 https://www.nature.com/articles/s41526-024-00437-w
- **Optimise behavioural health and human factors research for deep space missions by classifying analogue scenarios and fidelity**(Frontiers in Space Technologies 2025)。アナログの忠実度(fidelity)を分類する枠組み。LLM シムを「低忠実度だが高スループットのアナログ」として位置づける議論に使える。 https://www.frontiersin.org/journals/space-technologies/articles/10.3389/frspt.2025.1391331/full
- **プロジェクト全体像**: レビューリポの `slides/s26-2065_2095-good-echo-hackathon.pdf`(GOOD ECHO 総括資料。研究員番号が本リポと異なるため厳密な帰属は不確定だが内容は本プロジェクトの結び)によれば、GOOD ECHO は **公園のベンチ → 宇宙ステーション → 50日長期滞在**の3フェーズ構成で、karesansui / バッツ / RERE / **もん**(= happy-to-chat-bench-simulation の作者)の4名による共同プロジェクト。同資料は「衝突の60%減少」「修復ラグ 1.17ステップが撤去後も維持」と**リポジトリ README より強い主張**をしているので、引用するならリポ側の慎重な記述(「BはAより摩擦系カウントが少ない」)を優先すべき。この**スライドと README の主張強度のズレ**自体が、提出物間で主張を揃える難しさの実例。
