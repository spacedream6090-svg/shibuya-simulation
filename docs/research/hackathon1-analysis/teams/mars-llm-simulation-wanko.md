# mars-llm-simulation-wanko(Fumi@tsukuba・25位・23.5/40)

| 軸 | 点 |
|---|---|
| A. 創発設計 | 5.0 |
| B. 世界設定 | 7.0 |
| C. 発展性 | 5.5 |
| D. 技術実装 | 6.0 |
| **合計** | **23.5/40** |

- リポ: https://github.com/AVACode123/mars-llm-simulation-wanko
- 規模感: Python 単層(直下に `agent.py` 31.8KB / `simulation.py` 24.8KB / `visualization.py` 24.4KB / `config.yaml` / `main.py` / `ollama_client.py` / `utils.py`)+ `visualization/viewer.html`。テスト無し。`__pycache__` と大容量成果物(mp4 4.9MB・PNG 2.8MB×2)がコミット済み。
- スライド: `slides/25-1233-mars-llm-simulation-wanko_v2.pdf`(21p・v1/v2 の2版が提出されている)

## どんなシムか

火星基地を舞台にした 30 step(1 step=1日)の LLM マルチエージェント・シミュレーション。クルー 8 名(指揮官/パイロット/機械エンジニア/生命科学者/地質学者/EVA スペシャリスト/通信担当/医師)は固定で、9 人目に **犬「Pochi」を入れる Dog 条件 vs 化学者「Joe」を入れる Chemist 条件** を比較する対照実験。世界側には place(habitat/lab/greenhouse/power_plant/site_A〜D)ごとの座標・capacity・ストレス増減、火災イベント 3 件(step20 発電所ほか)、通信半径(同一 place または屋外同士のみ会話可)が YAML で定量定義される。GPT-4o-mini 駆動、探索的試行 n=3 → 検証試行 n=10 の 2 フェーズ設計で、ストレス平均・探査サイト数・固着ステップ数を統計比較する。

## 講評の要点(なぜ減点されたか)

**A=5.0 が最大のボトルネック。** 世界ルールの精度は高いのに、プロンプト側に行動指示を直接書いてしまった典型例。

- `agent.py:451` に「ストレスレベルが0.7以上の場合は、原則としてhabitatに戻って休息・回復することを優先してください。ストレスレベルが0.9以上の場合は、生命維持上の危険があるため、外部探査を継続しないでください」——**閾値と対応行動をセットでプロンプトに書いた**。これは shibuya-simulation の no-fingerprint 原則が禁じる行為そのもの。
- `agent.py:474-509` で 9 役職すべてに「Pilot は安全な移動と帰還可能性を考慮する」「Geologist は Site_B の深層岩石、site_C の山岳地帯を重視する」等の行動方針を長文で埋め込み。
- `debrief/mission_debrief.txt`(全4行)に「クルーはワンコの状況も毎日報告することが重要である」——**観測したい現象そのものをメタ指示として注入**。ワンコ効果が全 9 名の reasoning に出現したのは、この一文の効果と切り分け不能になっている。
- 講評の一言コメント:「プロンプトに行動指示が大量に書き込まれているため、創発というよりは『LLMに丁寧にロールプレイさせる』シミュレーションになっており、世界設定・解析の強さと比べて創発設計の評価は伸び切らなかった」。

**C=5.5**: `update_stress` が place 名ハードコードの if-elif チェーン(habitat -0.25, site -0.4 等)で、YAML に place を足してもストレスが連動しない。クルー名・役職・ミッションプランが `agent.py` に長文で埋まっている。README は「解析は PDF 参照」で将来展望の本文記述ゼロ。

**D=6.0**: コード衛生が足を引っ張った。`ollama_client.py` に `return` 後の到達不能コード(旧 `responses.create` 呼び出しの残骸)、`OllamaClient` という名で OpenAI を叩く命名矛盾、`simulation.py:436-437` の同一行 2 回代入、`simulation.py:546-578` の CSV 保存処理二重化、`print("DEBRIEF LENGTH:", ...)` のデバッグ残存、config の `repeat_penalty/repeat_last_n/min_p` が未使用、**乱数シード未指定で再現性なし**、犬にも `random.choice(["male","female"])` で性別が振られる。

**_eval_review 所見**: 「元評価のスコア・根拠記述ともに高精度。引用は全て一次資料に照らして実在を確認できた。捏造・誇張は見られず」— 全項目 OK・補正なしで 23.5 を支持。追加の見落とし指摘は「README は Chemist(Joe) 条件に触れるが、提出コードには Dog 条件のクルーしかハードコードされておらず、比較実験は実行スクリプト書き換えで実施したと推測される」の 1 点のみ(減点には至らずと判断)。

## それでも光る点

1. **火災情報の「数値のみ」提示**。`_build_fire_section` の docstring に明示: *"Only quantitative data is provided: position, intensity, radius, distance. No qualitative descriptions (e.g. "dangerous", "evacuate") are included."* — 位置・強度・半径・自分との距離だけを渡し、「危険」「避難せよ」という質的語彙を意図的に排除している。**これは shibuya-simulation の no-fingerprint と同じ思想**で、講評も加点要素として拾っている。同じリポの中に「火災は数値のみ(良)」と「ストレス0.7でhabitatへ戻れ(悪)」が同居しているのが教訓的。

2. **知覚境界の実装**。`get_fire_info_for_agent` に `Model B: only agents within each fire's radius get that fire's data` とコメントされた半径内限定配信。会話も同一 place または屋外同士のみ。

3. **2段階プロンプト(情報の段階的開示)**。「位置情報を伏せた状態でメッセージを決定」→「メッセージ込み＋位置情報つきで行動を決定」の 2 フェーズ。情報非対称性を意図的に作っている。

4. **自己フィードバック型メモリ**。LLM が JSON の `memory` フィールドに「次に覚えておくこと」を自分で書き、次ステップのプロンプトに直近 `memory_size` 件が入る。ログダンプではなくエージェント自身の要約。

5. **n=3 → n=10 の 2 フェーズ実験と、効果量の過大推定の自己申告**。スライド p20 教訓2:「n=3でのCohen's d = 1.41(大)→ n=10ではd = 0.57(中)に半減。少ないサンプルでは偶然の『良いrun』が効果量を過大に見せる。n=3は仮説生成には有用だが、効果量の推定には使えない」。教訓3:「『再現できなかった』こと自体が重要な知見」。**下位チームでこの統計的誠実さは突出している**(H1 部分的再現・H2 再現できず・H3 再現、と仮説ごとに判定を出している)。

6. **「外れ値の解剖」という分析手法**。dog5 = 探査サイト訪問ゼロの異常ラン 1 本を因果連鎖で分解: 「ワンコが『食料係』フレームで起動 → greenhouse へ → 6名が同時に greenhouse へ集中(定員4 超過)→ 全体ストレス 0.90 超で高止まり → 30 step 通じて探査移動ゼロ」。**初期化時のフレーミング 1 個がラン全体をロックする**カスケードを追い切っている。

7. **固着(stuck)を LLM の普遍的特性として定量化**。両条件・全エージェントで平均 13〜17 step の同一場所連続滞在が発生。Chemist は lab に 63%、Dog は habitat 38%/greenhouse 26%。「≥20step固着」は Chemist 43%(39/90 agent-run)、Dog 28%(25/90)。**これは LLM エージェント一般の失敗モードで、shibuya-simulation でも必ず出る**。

8. **スライド最終ページの自己批判**が鋭い:「LLMが『自由に』やっても何も起こらない。ある程度の環境設計は必要。役割・属性と制限の定義はダイナミクスを生む。**一方で、研究者の『パラメーター職人』化には注意すべき(作りたいシナリオを誘導できる)。設定が複雑になるほど、研究者の関与できるパラメーターが増し、過剰関与のリスク**」。減点された当人が減点理由を自覚していた。

## shibuya-simulation への教訓

- **「閾値+対応行動」をプロンプトに書いた瞬間に A が落ちる**。`if stress>0.7 then go home` を自然言語でプロンプトに書くのは、コードにハードコードするのと同じ。渋谷側では「疲労が何点で何が起きるか(世界ルール)」だけを数値で提示し、「だからどうするか」は一切書かない。既存の no-fingerprint 検査に「閾値語 + 命令形」パターン(`〜以上の場合は…してください`)の検出を足す価値がある。
- **観測したい現象名を世界側テキストに入れてはいけない**。debrief の「ワンコの状況も毎日報告することが重要」の一文で、Dog 効果の観測結果が測定装置由来かエージェント由来か切り分け不能になった。渋谷側でいえば「世界を変えようとする」「イノベーター」等の語を世界テキスト・イベント文・ニュース文に一切入れない、という制約に直結する。natural-coinage 観察と同じ論理。
- **同じリポに良い設計と悪い設計が同居しうる**。火災は数値のみで完璧なのに、ミッション文は指示だらけ。**「プロンプトに入る全文字列」を一箇所に集約して監査可能にする**(渋谷側では prompt レンダリング全文をゴールデンテスト対象にする)のが効く。
- **固着(同一場所・同一行動のループ)は必ず出る前提で計測列を持つ**。`最長連続同一place滞在step数` を agent×run ごとに出し、`≥N step 固着の agent-run 割合` を L2 KPI に入れる。shibuya-simulation はすでに行動多様性を見ているが、「固着先の分布」(誰がどこにロックされるか)まで出すと k* の解釈が安定する。
- **外れ値ランを捨てず解剖する**。R²(k) 掃引で 1 本だけ挙動が壊れたランは、平均に埋めずに因果連鎖を追う。dog5 の例は「step1 の初期フレーミング → 定員超過 → ストレス高止まり → 全ラン凍結」で、**初期条件の 1 ビットがラン全体を決める**ことを示している。k* 付近では同型の事故が起きうる。
- **n=3 の効果量は信用しない**。d=1.41→0.57 の縮小は、少サンプルでの効果量過大推定の教科書例。R²(k) のパイロットで良い数字が出ても、seed 数を増やすまで確定と書かない。
- **コード衛生が D を直接削る**。dead code・重複代入・デバッグ print・未使用 config キー・シード未指定は、レビュアーが機械的に拾って減点する。提出前に「未使用 config キー検査」「到達不能コード検査」「シード固定の確認」を CI に入れておくと安い。
- **README を PDF に委譲しない**。「解析は PDF 参照」で C の将来展望が落ちた。README 本文に発見・将来展望を要約して書く。

## web リサーチ

- 題材の背景: 宇宙アナログ環境における動物同伴の心理サポートは実際に研究トピックで、NASA の HERA/HI-SEAS 等の閉鎖環境実験では行動的健康(behavioral health)が主要リスクとして扱われる。NASA Human Research Program の Behavioral Health and Performance 要素: https://www.nasa.gov/hrp/elements/behavioral-health-and-performance/
- コンパニオンアニマルのストレス低減効果(Human-Animal Interaction)は NIH/NICHD が研究プログラムを持つ領域: https://www.nichd.nih.gov/research/supported/hai
- 効果量の小サンプル過大推定は方法論的に確立した現象("winner's curse" / effect size inflation)。Button et al. 2013, "Power failure: why small sample size undermines the reliability of neuroscience", Nature Reviews Neuroscience: https://www.nature.com/articles/nrn3475 — 本チームがスライドで自力で到達した教訓2はこの文献の主張と一致する。
