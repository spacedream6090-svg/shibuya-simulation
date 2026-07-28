# all-in-smoke(えす / 福本真士・19位・28.0)

| 軸 | スコア | 内訳(Run1/Run2) |
|---|---|---|
| A. 創発設計 | 5.0 | 5 / 5 |
| B. 世界設定 | 8.0 | 8 / 8 |
| C. 発展性 | 7.0 | 7 / 7 |
| D. 技術実装 | 8.0 | 8 / 8 |
| **合計** | **28.0/40** | 28 / 28 |

- リポジトリ: https://github.com/sfkmt/all-in-smoke
- スライド: `slides/19-182-all-in-smoke.pdf`(10ページ・**テキスト層ゼロ=全ページ画像**。dpi=100 で PNG 化し全 10 ページ視覚読解した)
- 規模感: **本グループ最大**。`live_fire_simulation.py` 単体で 55KB(講評時点 1,398 行)、`smoke_simulation.py` 30KB、`poker_simulation.py` 21KB、`smoke_timeql_converter.py` 17KB。`poker_engine/`(cards/deck/betting/showdown/hand_evaluator/pots/table/actions = 8 モジュール)と `poker_agents/`(base/scripted/llm/openrouter/endpoint/personas/session_state/voice_profile/card_language/commentator/manifest_loader/replay_timing/tts_normalizer = 13 モジュール)を分離。`tools/` に 8 本(トーナメント実行・実況・TTS・動画書き出し・リール生成)。**`tests/` が 12 ファイル・計 10 万文字超**で本グループ唯一の本格的テスト整備。`configs/` に 9 種類の YAML。`visualization/viewer.html` が 104KB。

## どんなシムか

テキサスホールデムのポーカーテーブルを中心に、テーブル群(table_a/b/c)・バー・倉庫・観戦席・2 つの出口(exit_a/b)を持つ屋内空間。**ハンドが進行している最中に、赤い危険リング(fire perimeter)がテーブル中央に向かって縮小してくる**。エージェントは毎ターン「プレーを続ける」「勝ち手札に固執する」「チップが惜しくて居残る」「危険が到達する前に席を立つ」を選ぶ。火がかかる位置に座り続けると `engulfed` → `fatal` と段階的に悪化。

危機の報酬構造が三つ巴で組まれているのが肝で、`fatal_overrides_chips`(死んだら勝負終了)/ `stand_up_forfeits_stack`(席を立てばチップ放棄)/ `last_seated_claims_forfeited_chips`(最後まで座っていた者が放棄チップを得る)。**逃げれば助かるが負け、粘れば勝てるが死ぬ**という、サンクコストと損失回避が真正面からぶつかる設計。LLM は OpenRouter(grok 系)/ Ollama の両バックエンドに対応。

## 講評の要点

**強み(eval)**
- **世界設定 B=8.0**。ポーカーの不完全情報ゲームと縮小する危険リングを**同時進行**させる構図は標準デモに無い。避難シミュレーション + ゲーム理論 + 心理プロファイルの組合せとして強い。
- **メモリ設計が秀逸**。`SessionState` が tilt 減衰・rivalry note 蓄積・recent_outcomes ledger を扱い、**バッドビート検出**(自分の手が two_pair 以上でショウダウン負け → `_TILT_BADBEAT_BONUS` 加算)まで実装。LLM へは数値 tilt ではなく**日本語の mood label**(「落ち着いている」「やや熱が入っている」「明らかにイラついている」「完全にティルト気味」)のみ露出し、機械的自己修正を避けている。
- `PokerFeedbackState` が chip_attachment / loss_chasing / entitlement / table_image_pressure / rivalry_pressure / fold_success_memory 等の心理プレッシャーをポーカー期から累積し、**避難行動の遅延要因に転移**させる。
- LLM 統合: 構造化 JSON 強制(Ollama `format:"json"` / OpenRouter `response_format:{type:"json_object"}`)、transport エラー / JSON パース失敗 / 空コンテンツ全てで **fold にダウングレード**する防御的設計、API キー欠如時の早期 fold。
- `card_language.py` が LLM 出力のカード表記揺れを 20 種以上の正規表現で正規化。
- **乱数はすべて seed 制御**され、トーナメントはハンドごとに `seed + hand_index` で deterministic。`JsonlLogger.next_step` の単調増加カウンタが action / memory_reasoning / table_talk を同一 step に結びつける。**本グループで唯一、再現性で減点されていないチーム**。

**弱み(eval)** — A=5.0 の理由が全部ここに集約されている
- **作品のハイライトである「火の手にどう反応するか」で LLM が一切呼ばれない**。`live_fire_simulation.py:1264-1331` の状態遷移(`stood_up`/`clinging_to_stack`/`tempted_by_chips`/`engulfed`/`fatal`)は完全に閾値 if/elif チェーン(`FIRE_CONTACT_DANGER=0.92`、`FATAL_EXPOSURE_TICKS=3`)。`_crisis_inner_voice`(L891-947)も status/motive をキーにした条件分岐で固定文字列を返す純粋テンプレート。
- **デフォルトの `all_in_smoke_demo.yaml` は 6 エージェント全員が `type: scripted`** で LLM 呼び出しゼロ。新規読者が最初に動かす体験で LLM 駆動が見えない。
- eval の提言: 「ここで LLM に raw 圧力データ(danger, belief_fire, chip_temptation, crisis_match_forfeit_pressure 等)を渡して自由判断させれば、**創発性が飛躍的に高まるはず**」。
- `live_fire_simulation.py` が 1,398 行の単一ファイル。`crisis_state_machine.py` / `pressure_model.py` / `crisis_voice.py` への分割を提言。
- README が技術手順書中心で、研究的問い(`Does poker-table trust transfer into fire-alarm trust?` は `smoke_simulation.py:478` のログラベルにしか登場しない)がハイレベルに出ていない。

**_eval_review の所見**
- 引用 22 件のうちほぼ全てが実在・内容一致。軽微な不整合 2 件程度。「スコア・記述ともそのまま採用可能」。
- 見落とし 3 点を指摘:
  1. B で `_crisis_match_snapshot` の**4 つ目のルール `poker_result_breaks_tie_after_survival`** が言及されていない(世界設定の独創性をさらに強化する材料)。
  2. `PokerFeedbackState` は厳密には 11 フィールド(心理プレッシャー float 9 + recent_delta + hands_played)。「9 次元」はおおむね正しい。
  3. A で `SCHEMA_RULES` の **inner_voice 強要**(personas.py L34)が「raw observation のみ」という主張をやや弱める材料だが、本文では未言及。

## コード実査で面白かった点

1. **「数値を隠して気分だけ渡す」メモリ設計** — `session_state.py` の `prompt_block()` の docstring がそのまま設計思想:
   > Hides the numeric tilt; only mood label + recent outcome notes flow through, so the model reacts via **vibe rather than mechanical self-correction**.

   さらに prompt_block に渡す `note` フィールドが「過去ハンドの読み材料。**逐語的にコピーせず**、自分の reads と inner_voice を更新する材料に使う。」と、LLM に対する*使い方の指示*ではなく*素材の位置づけ*を明示している。「fresh session なら None を返す」(何も無ければ何も渡さない)という判断も入っている。

2. **`SCHEMA_RULES` が「感情語彙と分析語彙を強制的に分離」している**(`personas.py`)。全 10 条のうち 5〜6 条がこの分離に費やされている:
   - (5) `inner_voice` は手札解説ではない。カード・ボード・レンジ・オッズ・エクイティ・ハンドカテゴリ・ドロー・アクション計算は **reasoning に書け**。inner_voice ではホールカード・ボード・ハンド名・コンボ記法・ポーカー分析を繰り返すな。`top pair`/`draw`/`pot odds`/`range`/`kicker`/`equity`/`EV` といったポーカー用語を inner_voice で使うな。
   - (6) `inner_voice` は **fear, hesitation, attachment, regret, self-justification, suspicion, pride, shame, relief, or resistance to folding/betting** を中心に据えよ。

   つまり「合理的説明」と「心の声」を**同じ出力の別フィールドに強制的に住み分けさせる**ことで、後者を「なぜ降りられないのか」の観測データとして純化している。これは A の減点(行動誘導)にもなり得る両刃の設計だが、**観測したいものを出力スキーマで定義する**という発想は強い。

3. **失敗時のフォールバックが全部 `fold`** — transport エラーも JSON パース失敗も空レスポンスも API キー欠如も、すべて fold にダウングレードする。ポーカーにおいて fold は「最も損失が確定的で、最も安全で、ゲームを進行させる」行動なので、**フェイルセーフの意味論がドメインと一致している**。

4. **`seed + hand_index` によるハンド単位の決定論** — トーナメント全体を 1 つの seed から回すのではなく、ハンドごとに派生 seed を作る。途中のハンドだけを再現・デバッグできる。shibuya の CRN 設計と同じ思想。

5. **`tools/` の充実が「提出物生成パイプライン」になっている** — `poker_commentator.py`(実況生成)→ `commentary_to_tts.py`(音声化)→ `mux_audio_to_video.py`(合成)→ `export_replay_video.py` / `make_short_reel.py`。シムの出力からデモ動画までを自動化している。lunar_simulation の 8 本のレポート生成スクリプトと同じく、**提出物生成をコードに落とす**チームは提出物の質が高い。

## 説明資料(スライド)より

タイトル「不完全情報ゲームにおけるエージェンティック心理シミュレーション — ALL-IN SMOKE: 命の危険が迫るテーブルで、AI は最後の一手を降りられるか」(2026.05.07 / 福本真士)。

**3 つのコア問い(p3)**: エージェントはどこまでプレイを続けるのか / どの瞬間にゲームそのものを降りるのか / **勝敗最適化を超えた行動はどう創発するのか**。

**実験設計:3 レイヤー構造(p4)** — これがこのチームの設計思想の核心で、リポの README には無い整理。

| Layer | 内容 |
|---|---|
| **Layer 1: Environment** | テキサスホールデムを「心理露出環境」として設計。ブラインド上昇 → 時間経過そのものがリスクに。火災イベントでゲーム内報酬と身体的リスクが同時発生。勝敗 = チップ量 + 生存 + 離席判断 |
| **Layer 2: Nudge** | **「逃げろ」と指示しない**。危険領域が段階的に縮小。チップリード・連敗・対抗心が離席を遅らせる。ポーカーの勝ち筋 vs 生存の合理性が衝突 |
| **Layer 3: Agent** | 性別・年齢・出生情報・プレイ履歴から心理傾向を生成。TimeQL(占術)→ 数値スコア → 初期パラメータ。自己制御・損失回避・執着・リスク感度を設定。**作為的な性格付けではなく、偏りの確率的発生** |

**Layer 2 の「『逃げろ』と指示しない」は shibuya の no-fingerprint 原則と同じ思想**であり、作者自身も明確に意識している。にもかかわらず A=5.0 なのは、**指示しない代わりに LLM に判断させることもしなかった**(閾値ロジックが決めた)ためで、no-fingerprint だけでは A は取れないという教訓になっている。

**シミュレーション結果(p5)** — 総ハンド数 64、火災発生 Hand 34 / Step 232、火災継続 51 ticks、離席 5、**Fatal 1**。

| | チップ優位側 | 生存勝者側 |
|---|---|---|
| 最終チップ | 3,565 chips(取消線) | 2,435 chips |
| 結末 | **fatal(チップ優位が無効化)** | 生存(総合勝者) |

Key Insight: 「ポーカーだけを見れば、チップ優位側が勝っていた。しかし火災下では、**チップ量より生存が上位ルールとなる**」。

**心理的解釈:なぜエージェントは降りられないのか(p6)** — 3 フェーズの物語として提示:
- **Phase 1 危機をノイズとして処理**: 「まだ勝負のノイズとして処理している。先に立った方がチップを失う。火より相手の我慢を見てしまう。」
- **Phase 2 危機認知 + 損得計算の並走**: 「火の手が席まで来ている。相手が先に立てば取れる。こちらが先に立てば失う。」
- **Phase 3 分岐点 — 生存 or 執着**: 生存勝者「勝敗より上位のルールを選んだ」/ チップ優位「**視線がまだチップに残っている**」→ fatal

  *(註記: 講評は危機フェーズの `_crisis_inner_voice` がテンプレート生成であることを実コード照合で確認している。上記引用がポーカー期の LLM `inner_voice` 由来か、危機期のテンプレート由来かは資料からは判別できない。)*

**創発した行動パターンの分析(p7)** — 2 体を 4 段階の Fire Phase で 3 指標(チップ誘惑 / 目標圧力 / 生存判断)の折れ線でプロット:
- **チップ優位エージェント**: チップ誘惑と目標圧力が高いまま維持。生存判断は最後まで低く(〜10-15)、結果として fatal。
- **生存勝者エージェント**: チップ誘惑は高いが目標圧力は中程度(〜50)。**Phase 2→3 の火災接触で生存判断が 10 → 95 へ急上昇**し、離席・生存に至る。

Key Insight: 「不完全情報ゲームは、環境ナッジによって『手札を読むゲーム』から『**自分がなぜ席を立てないのかを露呈するゲーム**』へ変化した」。

**システム構成(p9)**: TimeQL(占術 API)→ 出生情報 → エージェント初期化レイヤー → 心理パラメータ → LLM エージェント群(意思決定ループ)→ テキサスホールデム環境(火災イベント発火)→ 行動ログ・心の声記録 → 分析・可視化。

**社会実装の可能性(p8)** — 4 つ:
1. **危機時ナッジ設計シミュレーター**: 災害・避難・医療・金融危機で、警告・遮断・退出導線・損失補償の**タイミング**を検証するツール
2. **エージェントによる危機訓練**: 迷う人・粘る人・責任感で残る人など複数の心理傾向を持つ参加者を生成し、行動分岐を低コストで反復
3. **AI エージェントの安全性評価**: 「**撤退能力**」「危機認識」「**報酬関数から降りる力**」を検証する評価環境。タスク成功率では測れない能力を評価
4. **合成行動データ生成**: 多様な認知バイアスを持つ合成ペルソナで環境設計の弱点を事前発見

**まとめ(p10)**: 「危機判断の失敗は、情報不足だけで起きない」。勝ち筋が見えているとき、人は危険から離れられなくなる / 損失が目前にあるとき、避難は「**敗北**」として意味づけられる / 環境ナッジは、命令なしに判断の重みを変えられる。

## shibuya-simulation に活かせそうな点

- **「数値を隠して気分ラベルだけ渡す」は shibuya の内生化に直輸入できる**。第62-64バッチで `closeness` や較正確率といった数値を扱っているが、**LLM のプロンプトには数値をそのまま出さず「気分/関係の温度」の語彙ラベルに変換して渡す**と、機械的自己修正(「closeness 0.7 だから承諾しよう」)を避けられる。`prompt_block()` の「fresh session なら None(何も渡さない)」も、材料が無いときにノイズを渡さない良い規律。当プロジェクトは既に「材料が無い日は fallback」という構造を持っているので相性が良い。
- **出力スキーマで観測対象を定義する**(`SCHEMA_RULES` の reasoning / inner_voice 強制分離)。shibuya が「世界を変えようとする個体」を観測したいなら、**分析的説明と動機的独白を別フィールドに分けさせる**と、後者だけを対象にラベル伝播や語彙分析ができる。ただし当プロジェクトの no-fingerprint 原則との整合には注意 — all-in-smoke の (6) は「fear, attachment, regret を中心に据えよ」と**感情の方向まで指定している**ので、これは fingerprint に該当する。**「分けろ」までは安全、「何を書け」は危険**という線引きが学べる。
- **3 レイヤー構造(Environment / Nudge / Agent)という説明フレーム**は提出資料の構成としてそのまま使える。shibuya なら Layer 1 = 屋内 SFM 人流 + 組織/経済、Layer 2 = 定員・時間・体力・関係の物理圧力(行動指示ゼロ)、Layer 3 = 個体パラメータと k。**「Layer 2 で『こうしろ』と一切書かない」を明示的なレイヤーとして立てる**と、審査員に no-fingerprint の価値が伝わる。
- **反面教師 — 「指示しない」だけでは A は取れない**。all-in-smoke は Layer 2 で明確に「『逃げろ』と指示しない」と設計しながら A=5.0。理由は、指示しない代わりに**判断そのものを閾値ロジックに移した**から。shibuya の第62バッチ `relations_endo.py` は「構造化決定論抽出」で内生材料を作り、合成 p = clamp(w·較正 + (1−w)·内生) − gossip という**決定論的合成**をしている。**この境界の説明を提出物で明示しておく必要がある**:「決定論部分は世界の物理であり、行動選択そのものは LLM が決めている」ことを、all-in-smoke が減点された構図と対比させて言語化しておくと守れる。
- **「報酬関数から降りる力」を評価軸にする(p8-3)** — これは AI 安全性の文脈で強い言葉。shibuya の「世界を変えようとする個体」の裏返しとして、**「与えられた役割/目標から降りる個体」**を観測項目にする発想が得られる。組織/経済モジュールがあるので、「所属組織の目的関数に反する行動を取った回数」は実装可能な指標になり得る。
- **`seed + hand_index` のイベント単位派生 seed** — shibuya の CRN 設計(第63バッチ)は既にラン単位で seed を揃えているが、**日単位・decision 単位の派生 seed** を足すと「特定の日だけ再現してデバッグ」ができる。`always-draw conditionally-use` の設計と両立する。
- **テスト 12 ファイルが D=8.0 を支えている**。shibuya は 1,725 テスト緑なので既に上だが、**その事実を提出物で数字として出す**べき(all-in-smoke は eval に「tests/ 12 ファイル、合計 3,000 行超」と数えられて加点されている)。
- **提出物生成をコード化する**(`tools/` の実況→TTS→動画パイプライン、lunar の 8 本のレポート生成スクリプト)。shibuya にも `make_viewer` / `make_endo_report.py` があるので、この系統をもう一段自動化すると、本選までの反復コストが下がる。

## web リサーチ

- **避難意思決定と milling(逡巡)行動** — https://pmc.ncbi.nlm.nih.gov/articles/PMC3919722/ (Measuring and Modeling Behavioral Decision Dynamics in Collective Evacuation, arXiv: https://arxiv.org/abs/1304.4704)。統制された実験室設定で、broadcast 情報と peer-to-peer 情報の緊張、災害の切迫度による時間的緊急性、**避難者に対する避難所定員の制限**が個人の避難意思決定に与える影響を検証している。all-in-smoke の「危険リング縮小 × 席を立てばチップ放棄」も、lunar_simulation の「20 体 vs 定員 10」も、まさにこの**「限られた避難先容量」**という同じ構造圧力の変奏である。
  - 避難前に人々が多くのタスクをこなすことで避難開始が遅れること(milling time)、milling time と避難参加率が津波死亡推定に**非線形な影響**を与えることが示されている: https://www.sciencedirect.com/science/article/pii/S0925753525002905
  - shibuya への含意: 「非線形な影響」という点が k* 探索と直結する。**避難研究では既に閾値的な相転移が観測されている**ので、shibuya の R²(k) 掃引でも「なめらかな線形反応」ではなく閾値を予期して測定点を配置すべき。
- **Lindell & Perry の Protective Action Decision Model (PADM)** — 上記スコーピングレビューが避難意思決定研究の基礎モデルとして挙げている。「危機を認知する → 脅威と判断する → 防護行動を選ぶ」の段階モデルで、all-in-smoke のスライド p6 の Phase 1/2/3(危機をノイズとして処理 → 危機認知 + 損得計算の並走 → 分岐点)はほぼ PADM の再発見。**先行モデルを引いていれば B/C が伸びた**可能性がある(beyond-badminton がホイジンガ/カイヨワを引いて B=8.0 を取ったのと同じ構図)。
- **TimeQL(占術ベースのペルソナ生成)** — 資料 p4/p9 と `smoke_timeql_converter.py` が依存している外部システム。**web 検索では公開情報を確認できなかった**(「TimeQL」で該当する公開製品・サービス・論文はヒットせず、TimeML という別物の時間表現マークアップ言語が引っかかるのみ)。作者側の独自資産または非公開 API と推測されるが、**断定できないので不明と記録する**。設計思想としては「出生情報 → 数値スコア → 初期パラメータ」で、資料の言葉では「**作為的な性格付けではなく、偏りの確率的発生**」。shibuya への示唆は、外部の(内容としては非科学的でも)**一貫した規則で個体差を生成する仕組み**を持つと、手作りペルソナより多様性が担保され「作為性」への批判をかわせるという点。当プロジェクトなら実在の人口統計(年齢・職業・世帯構成の同時分布)から個体を引く方が、同じ効果を科学的根拠つきで得られる。
