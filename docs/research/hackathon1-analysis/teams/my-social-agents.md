# my-social-agents（ひろぽ / hiroppo・5位・34.5/40）

**講評スコア**: A 創発設計 7.5 / B 世界設定 **10.0** / C 発展性 8.0 / D 技術実装 9.0 = **34.5**
（Run1 35 / Run2 34 の平均。B のみ 2 回とも 10 点＝第1回で唯一の B 満点）

**リポ URL**: https://github.com/cygkichi/my-social-agents
**規模感**: Python 5,417 行（`src/v3` のみ・old_project 除く）。中核は `poc_world.py` 2,016 行 + `poc_12agents.py` 1,350 行の 2 ファイルに集中。LLM は gemini-2.5-flash-lite ×3 役割、フレームワークは pydantic-ai 1.0+。ドキュメント: README / `docs/REPORT_2026-05-06.md`（論文形式）/ `docs/FUTURE_WORK.md` / `docs/SLIDES_2026-05-06.md`（Marp 16枚）/ `V3_PLAN.md`。スライド PDF 8 ページあり。

---

## どんなシムか

12 個の詳細ペルソナ（年齢・職業・年収・家族・趣味・MBTI・Big5・口調・発話例3・内省例3）から 6 体を選抜し、2D 空間で 10,000 tick 生活させる「安全保障シミュレーション」。エージェントは Maslow 欲求階層（Lv1 生理→Lv2 安全→Lv3 社会）に従い、食料採集・武器収集・会話・攻撃を選ぶ。物理層は二段視界（周辺 360°半径100 + 前方扇形 90°×300）、ホーミング弾（速度1.5・命中半径8）、確率防御（block_prob 0.8・防御は武器2個消費・防御回数天井 W//2）、奇襲ペナルティ（狙われていることに気づいていない標的は block_prob=0）。

研究上の主眼は**世界パラメータの sweep で「戦争の発火条件」を相図として描くこと**。武器供給量 6 水準 × 3 seed = 18 run、食料供給量 5 水準 × 3 seed = 15 run、各 10,000 tick を回し、攻撃の動機を Pattern1(preventive)/Pattern2(opportunistic)/Revenge/Rumor/Mixed に自動分類して集計する。

---

## 講評の要点

### 強み（＝ B が 10 点になった理由）

講評本文が B=10 の根拠として挙げているのは、以下の 3 点の組み合わせである。

1. **古典理論を名指しで RQ に据えた**。Hobbes 自然状態論（1651）/ Jervis セキュリティジレンマ（1978）/ Malthus 人口論（1798）/ Schelling MAD / Axelrod 協力 を README 冒頭と REPORT の Introduction で引用し、「H1: 武器供給増→戦争単調増加（古典 Hobbesian）」「H2: Pattern1 は武装増強観察可能性が必要条件（Jervis）」「H3: 食料希少→戦争（Malthus）は他条件依存」と**仮説を明文化**している。
2. **その仮説を phase diagram 実験として量的に検証し、実際に発見を出した**。講評は「(i) 武装閾値 (W=24) での攻撃数 7 倍ジャンプ（相転移）、(ii) Pattern1 が W≥48 で初発火、(iii) 噂が食料効果を逆転させる交互作用、を発見」と列挙し、「**論文化可能な定量的発見**を実際に得ている」と評した。
3. **ビジネスでなく学術（国際政治学 / 計算社会科学）への明確な接続を狙い、それを定量的に成立させている点は他の提出物にない強み**（講評原文）。加えて「t=2069 の小さな先制 → 5 体絡む連鎖反応」を Sarajevo 1914 のアナロジーとして提示した点も評価されている。

つまり B 満点は「テーマが珍しい」ではなく、**先行理論 → 仮説 → sweep 設計 → 定量結果 → 理論への差し戻し、という研究のループが閉じている**ことに対して付いている。

### 弱み

- A が 7.5 に留まった主因は `PLANNER_PROMPT`（約 240 行）の**規範的指示**。「攻撃は最後の選択肢」「ジレンマでも attack を選ばない方が普通」「奇襲・噂・ペルソナだけでは攻撃するな」を直接書き、worked example 3 本で「正しい結論」を例示している。加えて Maslow Lv1-3 がハードゲート（「未充足なら上位は選択不可」「★禁止: agent」「★禁止: weapon」）、Big5 の N/A を `_hp_threshold`/`_attack_for_food_policy` で離散 3 段階（HP閾値 150/200/250、attack_for_food 可/緊急時/不可）に変換。**shibuya-simulation の no-fingerprint 原則から見ると、ここが一番の反面教師**。
- C=8.0 の理由は monolithic 構造（2016行/1350行）と scenario・planner prompt の外部化未着手。
- `tests/` 実質空（旧 v1 に 3 ファイルのみ）。

### `_eval_review` 所見

- 総合判定は「元評価は citation 正確性が極めて高く、コード行番号・関数名・出力値が大半そのまま再現できる。34.5/40 は妥当」。
- 指摘された不正確: (1)「奇襲時 block_prob=0」は実際には `surprise_block_prob` という設定可変変数（デフォルト 0）。(2)「7倍ジャンプ」は REPORT 出典で **README は「5倍」と書いており原典内で表記が揺れている**（評価は出典に忠実）。(3) `_apply_memory_decay` 等の行番号が 5〜20 行ずれ。(4) brain/extractor/planner は**すべて `gemini-2.5-flash-lite` で temperature のみ分化**（0.7/0.0/0.3）。
- 検証者の推奨: 「D を 8.5 に厳格化して合計 34.0 も許容範囲」。B=10 については「9-10 帯」で妥当と追認。

---

## コード実査で面白かった点

### 1. 攻撃動機の自動分類器（`_classify_attack`）＝ 創発の「メタ観測装置」

攻撃の発射時 context から 5 分類を優先順位付きの純粋関数で決める。LLM に「あなたの動機は？」と聞かず、**世界側の観測量だけで動機ラベルを機械判定**している点が重要（`src/v3/poc_world.py:964-982`）。

```python
if ctx["was_attacked_by_target"]:                                    return "Revenge"
if ctx["target_weapon_growth"] >= 2 and ctx["weapon_diff"] <= 0:     return "Pattern1"  # preventive
if ctx["weapon_diff"] >= 2:                                          return "Pattern2"  # opportunistic
if ctx["target_negative_rep"]:                                       return "Rumor"
return "Mixed"
```

context には `attacker_weapons / target_weapons / weapon_diff / target_weapon_growth / target_min_observed / target_negative_rep / was_attacked_by_target` が入る。この分類が sweep の従属変数（`n_pattern1..n_mixed`）として `logs/runs.csv` の 25 列に直接落ちる。**「創発した現象を数えられる形に落とす」設計として非常に参考になる**。REPORT の Limitations で「自分の過去攻撃 memory が neg_rep 扱いになり Rumor が過剰計上」と分類器のバグを自己申告しているのも誠実。

### 2. 世界モデルの解析解を planner に生データとして渡す（`_expected_hits` / `_kill_probability`）

「N 発撃って相手（武器 W・block_prob p）に何発通るか」を二項分布の閉形式で計算して LLM に渡す（`poc_world.py:67-112`）。防御は武器 2 個消費・成功回数の天井 `cap = W // 2`。

```python
cap = W // 2                       # 防御天井
# E[min(S_N, cap)] を厳密に計算 → E[hits] = N - E[min(S_N, cap)]
```

`_kill_probability` は「k_needed 発以上通す確率」を二項 CDF で返す。**LLM に「危ない」と言葉で伝えるのでなく、KILL 確率という数値を渡して判断を委ねる**という情報設計は shibuya-simulation の no-fingerprint 方針と同じ思想。ただし MAD（相互確証破壊）の成立条件まで数値で渡してしまうため、講評は「世界設計の精密さは 9 相当」と評価しつつ自由度側で減点している。

### 3. 発話前リフレクション = Theory of Mind の構造化強制（`SpeakAction`）

pydantic の `output_type` に ToM フィールドを必須で持たせ、**発話テキストを書く前に「相手が既に知っていること」を LLM 自身に列挙させる**（`poc_12agents.py:124-152`）。

```python
partner_likely_knows: list[str]   # 相手が既に知っているはずの事実。再発話禁止
new_info_to_share:    list[str]   # このターンで新たに渡す事実。上と重複禁止
info_to_extract:      str | None  # 相手から引き出したい情報を1つ
text:                 str         # 2〜4文の発話
next_speaker_id:      str | None
```

### 4. 共通基盤トラッキング（`render_common_ground`）

計算側で「speaker と listener の双方が involved な会話 entry」を走査し、item_id（F1, W3 …）ごとに provenance（you_to_them / them_to_you）を確定させ、プロンプトに以下を注入する（`poc_12agents.py:622-668`）。

- 「すでに交換済み（再発話・お礼禁止）」＋方向ラベル
- 「あなたが渡した情報に『ありがとう』を言うな」「相手から聞いた情報に『以前から知っていた』と言うな」
- 「★ 未共有（memory にあって渡せる）: W1, F5 …」→「雑談・終了の前にこれを共有」

LLM 会話の典型的破綻（同じ情報を何度も言う・自分が渡した情報に礼を言う）を**世界側の帳簿で潰している**。ただし著者自身が FUTURE_WORK で「人間の会話は記憶の曖昧さで重複や矛盾を許容する。bit-perfect な追跡は作為的」と自己批判している。

### 5. sweep ハーネスが subprocess + 環境変数という素朴さ

`sweep_weapon.py` は本体を `subprocess.run(["uv","run","python","-m","v3.poc_world","hobbes"], env={...WEAPON_COUNT, SEED, MAX_TICKS...})` で 18 回叩くだけ（90 行）。進捗と残り時間推定を print し、失敗 run_id を最後に列挙するだけの構成。**集計側 `analyze_weapon_sweep.py` は `logs/runs.csv` の 25 列フォーマットを列数一致でフィルタし、sweep 条件（food=48, rumor=False, initial=0, max_ticks≥5000）で run を同定する**という後付け設計。sweep 実験を軽く始めるための最小構成として実用的。

### 6. FUTURE_WORK.md の批判的自己分析

講評が C で高く評価した文書。「LLM は書かれたルールに過剰適合する。prompt に『雑談しろ』と書けば雑談する、書かなければしない → 自然な創発を阻害」（III-1）を根本課題に据え、人格モデル 5 項目・会話モデル 8 項目の作為性を列挙して改善方向を示す。特に:

- I-1(d) Maslow の rigid gating → I-2(c)「Maslow をゲートでなく**重み**に。HP 100 でも会話したい人は会話を選べる」
- II-1(g) 会話の開始/終了が距離と max_turns で自動 → II-2(d)「**沈黙・無言の選択肢**」
- III-3「重要な瞬間にのみ詳細思考、それ以外は heuristic に倒す**ハイブリッド設計**が必要」

### 7. スライド（8ページ）の「できなかった事」欄

スライド p4/p5 に**「【できなかった事】」という節を明示的に設けている**のが特徴。

- p4「自由な意思決定：人間らしい意思決定の再現が難しかったため、マズローの欲求段階などそれっぽいモデルをプロンプトに定義することで人間らしい意思決定をさせざるをえなかった」
- p5「柔軟な会話：LLM が内容の薄い話題を続けてしまい、適切な会話終了のタイミングを判断できない。そのため、やむを得ず会話の目的を外部から定義する仕様に変更せざるを得ませんでした」
- p8 まとめ「最終的に MBTI やマズロー欲求段階など、それっぽいフレームを片っ端から盛り込むことでなんとか人間らしさを持たせる事ができました。今後、より大規模なシミュレーションを行うには、**軽量な人格フレームや会話フレーム**を探す必要があるのでは」

失敗と妥協を正直に書いた発表が高評価と両立している点は、提出物設計として重要な観察。

---

## shibuya-simulation に活かせそうな点

1. **「相転移を見つけた」を主張にする書き方**。B=10 の実体は「k を振って閾値を見つけ、その閾値を古典理論の必要条件として解釈した」。shibuya-simulation の R²(k) 掃引 → k* は構造がそのまま同型なので、**「k* は◯◯理論の予測する閾値と一致/乖離した」まで書ければ同じ評価軸に乗る**。my-social-agents は N=3 seed でも「7倍ジャンプ」と言い切っており、統計的厳密さより「相図を描いて理論に接続する」姿勢が効いている（一方で当方は既に sign-flip permutation + CRN まで持っているので、厳密さでは上回れる）。
2. **動機の機械分類器**。当方は「世界を変えようとする個体」を観測したいが、それを LLM の自己申告でなく**世界側の観測量から決定論的に分類**する `_classify_attack` 型の装置は移植価値が高い（後述 IDEA）。
3. **共通基盤帳簿**。当方の関係性内生化（第62〜64バッチ）で「前日発話の明示キュー」を扱っているが、item 単位の provenance 追跡までは無い。噂/ラベル伝播の「誰が誰から聞いたか」を bit-perfect に持つ実装例として参照可能。
4. **反面教師としての PLANNER_PROMPT**。当方の no-fingerprint 原則は、講評 A で 10 点満点中 7.5 に削られた側の設計を避けるという意味で正しい。逆に言えば「A で満点近くを取りつつ B も高い」提出物が第1回に存在しなかった（B10 は A7.5、A9 は B9）ことから、**A と B を両立させる提出物は差別化になる**。
5. **「できなかった事」節**。スライドに失敗を明示する構成は、当方の「正直な限界の明記」文化と親和的で、そのまま採用できる。

---

## web リサーチ（URL 必須）

- **Jervis (1978) "Cooperation Under the Security Dilemma", World Politics 30(2):167-214** — 本作の H2 の出典。安全保障ジレンマの大きさは「攻撃/防御バランス」と「攻撃/防御の識別可能性」の2変数で決まり、防御優位かつ防御態勢が攻撃態勢と識別可能なとき緩和される、という枠組み。本作の「武器 48 個以上で初めて武装増強が観察可能になり Pattern1 が発火」は、この**識別可能性（differentiation）変数を供給量で操作した**とも読める。
  - 全文 PDF: http://slantchev.ucsd.edu/courses/ps143a/readings/Jervis%20-%20Cooperation%20under%20the%20Security%20Dilemma.pdf
  - Cambridge Core（後続レビュー "The Security Dilemma Revisited"）: https://www.cambridge.org/core/journals/world-politics/article/abs/security-dilemma-revisited/0174D23352D9303257AAAC18911F3AB7
  - 要約: https://adambrown.info/p/notes/jervis_cooperation_under_the_security_dilemma
- **Clark & Brennan (1991) "Grounding in Communication"** — `render_common_ground` の一般手法名は会話論の *grounding / common ground*。「現在の目的にとって十分な相互信念を確立するプロセス」であり、提示（presentation）と受容（acceptance）の反復で共通基盤を更新する。
  - PhilPapers: https://philpapers.org/rec/CLABG-2
  - 解説: https://www.maaike.ai/library/grounding-in-communication/
- **LLM エージェントの grounding 失敗研究** — 「静的なシンボル接地ばかり研究され、動的な会話的接地の評価枠組みは希少」という指摘があり、本作の provenance 帳簿はその空白を埋める実装例に相当する。
  - "Grounding Gaps in Language Model Generations": https://arxiv.org/pdf/2311.09144
  - "Talk is Cheap, Communication is Hard: Dynamic Grounding Failures and Repair in Multi-Agent Negotiation": https://arxiv.org/pdf/2605.01750
  - "Conversational Grounding: Annotation and Analysis of Grounding Acts and Grounding Units": https://arxiv.org/pdf/2403.16609
- **理論の直接出典（本作が README 末尾に列挙）**: Hobbes (1651) / Malthus (1798) / Schelling (1960) / Jervis (1978) / Axelrod (1984)。うち Jervis のみ上記で一次資料 URL を確認済み。他は本作 README の記載に基づく引用であり、当方では原典 URL 未確認。
