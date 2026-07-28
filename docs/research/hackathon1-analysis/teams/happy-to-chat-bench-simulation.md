# happy-to-chat-bench-simulation(滝本哲也(もん)・8位・33.5/40)

**講評スコア**: A 創発設計 9.0 / B 世界設定 8.5 / C 発展性 8.0 / D 技術実装 8.0 = **33.5**
(Run1 34, Run2 33。`_eval_review` 判定「妥当(誤差 ±1.0 以内)」= 修正不要)

**リポジトリ**: https://github.com/ops324/happy-to-chat-bench-simulation
**規模感**: Python 約 3,700 行(`agent.py` 608 / `simulation.py` 550 / `visualization.py` 748 / `metacog/` 約 500)、リポジトリ 29 MB。20 エージェント × 100 step × 2 条件を Ollama ローカル推論で実走。
**備考**: 3位チーム作者(もん氏)のもう1本。レビューリポの `s26-2065_2095-good-echo-hackathon.pdf`(GOOD ECHO 総括)を読むと、本作(公園のベンチ)・hackathon-singulab-inu(ISS)・50日長期滞在の3フェーズが **karesansui / バッツ / RERE / もん の4名による1つのメタプロジェクト** であることが明記されている。本作は担当チーム内で孤立した提出物ではなく、GOOD ECHO 系の「第1フェーズ(公園ベンチ)」に相当する。

## どんなシムか

公園空間(中央ベンチ・噴水広場・芝生・ブランコ・売店・花壇・並木道の7サブエリア)に20体の固有ペルソナ(退職男性・未亡人・若い母親・就活中の学生・心理カウンセラー等)を置き、Ollama ローカル LLM で毎 step Message / Memory / Action を生成させる。**唯一の介入は中央ベンチのプロンプトに1行を足すか否か**だけ — `"** SPECIAL: This is a Happy-to-Chat Bench. Anyone sitting here is signaling 'I am open to chat with strangers.' Approaching this bench is a socially accepted way to start a conversation with someone seated on it."`。位置・サイズ・定員などの物理プロパティは Happy / Ordinary の2条件で完全同一(`config.yaml` と `config_ordinary_bench.yaml` の diff は bench の name/type と output_dir/log_file のみ、と `_eval_review` が実 diff で確認)。100 step 走らせて集約・会話量・ペア形成・関係深化の差を定量比較する A/B 実験。

## 講評の要点

**強み**
- **A 9.0(担当5チーム中の最高点)** の直接理由は「世界ルールの設計精度と行動の自由度が高い水準で両立」。具体的には (a) 場所内エージェントへ渡す情報が `Number of agents here / Capacity / Occupancy rate` の**3数値のみ**で「快適」「混雑」等の定性評価を一切与えない、(b)「動け」「話せ」「逃げろ」の行動指示がゼロ、(c) ベンチ追記は行動指示ではなく**世界の社会的シグナルの意味づけ**でその上でどう振る舞うかは完全にエージェント任せ、の3点。
- 通信可否が「同じ場所内」または「両方とも場所外」と精密に定義され、**知覚境界が物理ルールとして規定**されている(`agent.py:99-122`)。
- B 8.5: 公園自体は標準的な設定だが、実在の社交装置(英国「Happy to Chat Bench」)の効果を LLM MAS で A/B 検証する問いの立て方に社会科学的意義がある、という評価。`_eval_review` は「独自性は『問いの立て方』と『20ペルソナの具体性』で稼いでいる。9点未満は妥当な落とし所」と補足。
- D 8.0: 4フェーズ同期実行、括弧バランス方式の独自 JSON 抽出器、`temperature=0.2 / repeat_penalty=1.1 / repeat_last_n=128 / min_p=0.05` の慎重な Ollama チューニング。

**弱み・改善提言**
- `random` の **seed が config から指定できない**(再現性の唯一の明確な弱点として A/D 双方で指摘)。`_eval_review` はさらに踏み込み「『中央ベンチ平均人数 3.3〜5.7倍』は1試行ベースの可能性があり、再現性確認がされていない(seed なし)点に元評価は触れていない」と留保をつけている。
- **`_eval_review` の最重要所見(shibuya-simulation の no-fingerprint に直結)**: ベンチ追記の後半 `Approaching this bench is a socially accepted way to start a conversation` は「**弱い行動誘導とも解釈可能**」。元評価も改善点で「『行動指示なし』原則を完全に守るなら、この行動誘導表現も最小化できる余地がある」と明記。つまり A9.0 でも **満点(10)を阻んだのはこの1フレーズ**。
- メタ認知層(`metacog/`)と Happy-to-Chat 実験の関係の統合説明が薄い。ペルソナ別・場所別の感受性分析が README に無い。

## コード実査で面白かった点

1. **プロンプトが「数値」と「解釈」を厳密に分離している**。`agent.py` の place セクションは `f"Number of agents here: {n}\n Capacity: {cap}\n Occupancy rate: {rate:.2f}"` を組み立てるだけで、閾値判定も形容詞も一切挟まない。さらに **場所の外にいるエージェントには place status を渡さない**(`else: place_section_text = ""`)= 知覚の非対称性がプロンプト組立段階で保証されている。

2. **「沈黙する自由」を明示的にプロンプトに書いている**。message タスク欄は `"...ask questions, or remain silent if your persona would not initiate."`、JSON スキーマ側も `"ペルソナが話しかけない状況なら空文字"`。話させる圧を掛けないことで「発話しない」も観測値になる。

3. **メッセージ用プロンプトと行動用プロンプトで渡す情報を切り替える**。message プロンプトには**座標も PLACE LOCATIONS も渡さない**(場所名と占有率のみ)。action プロンプトで初めて `Position: (x, y)` と全場所の座標範囲を渡す。「会話は位置を知らずに行い、移動は位置を知って行う」という情報設計。

4. **4フェーズ同期実行**(`simulation.py:338`)。Phase 1 全員のメッセージ決定 → Phase 2 送信(**移動前の位置関係で判定**)→ Phase 3 行動決定(自分が送ったメッセージを文脈に含む)→ Phase 4 一斉移動。「メッセージ送信中に位置が変わる」レースを構造的に排除。

5. **対照条件(Ordinary)側で予想外の創発が出た**のが最大の収穫。ベンチという外部装置が無い Ordinary では、Step 11 に犬の散歩中の女性が面接前の学生に深呼吸を勧め、Step 14 に**ミュージシャンとカウンセラーが同 step で同時に**「4秒吸って7秒止めて8秒で吐く」と命名・体系化し、Step 90 までに全メッセージの **49%(2,831/5,831通)が「呼吸」に言及、「4-7-8」を含むもの 1,366通** という規模で公園を覆った(Happy 条件では呼吸言及 2%、「4-7-8」は **0通**)。レポートはこれを「装置依存型集約 vs **テーマ依存型集約**」という2つの異なる集約メカニズムとして解釈している。

6. **個体レベルの反転が記録されている**。Agent 11(昼休みのサラリーマン)は Happy 条件で送受信 **0通の完全孤立**(ベンチが混雑→芝生へ逃避)、Ordinary 条件では 101通送信の緩い参加。「社交装置が全員の社交を増やす」わけではなく、押し出される個体がいることを個体追跡で示している。

7. **メッセージ長の時系列で「関係深化」を測っている**。Happy は 103→164 字(+59%)、Ordinary は 120→119 字で横ばい。「深化 = 長文化」という代理指標の置き方が簡潔。

8. **`metacog/`(Claude API 使用の自己書き換えメタ認知エージェント)**。`ExcitementEvaluator` が興奮スコア(0-10)を記録し、**直近5サイクルの発火数に応じて閾値を自己調整**する(発火0回→閾値-1で下げる / 3回以上→+1で上げる)。さらに `can_modify_section` がセクション単位のクールダウン(既定3サイクル)を課し、`is_stagnant` で停滞も検知する。`SelfModifyTool.modify` は自分のシステムプロンプトのセクションを差し替え、before/after/unified_diff/prompt_version を返してファイルへ永続化する。**LLM が自分のプロンプトを書き換える履歴が diff として全部残る**設計。

## shibuya-simulation に活かせそうな点

- **「弱い行動誘導」の検出基準**: `_eval_review` が減点材料に挙げたのは `socially accepted way to start a conversation` という**動詞句(行動の推奨)**であって、`Anyone sitting here is signaling "I am open to chat"`(**状態の記述**)ではない。shibuya-simulation の no-fingerprint 監査に「名詞句・状態記述は可、動詞句・推奨形は不可」という機械的なリント規則として持ち込めそう。
- **知覚非対称のプロンプト組立**: 「場所の外にいる者には場所の内部状態を渡さない」を if/else で保証する型は、屋内 SFM 人流の視界・聴取範囲の実装監査に直接使える。
- **対照条件を「何も起きない条件」と見なさない**: sham/null 対照で予想外の内生的秩序(4-7-8 呼吸法のような)が立ち上がる可能性があり、対照側のログも同じ厚さで解析すべき。shibuya-simulation のラベル伝播研究にとって、これは**介入なしでも語が自然発生し集団を覆う**という直接の前例。
- **個体の反転を必ず見る**: 集計平均(ベンチ人数3.3〜5.7倍)の裏で完全孤立する個体が出ている。k* 掃引でも「平均 R² が上がったとき誰が押し出されたか」を個体追跡する軸を用意したい。
- **自己書き換えプロンプトの安全弁**: `metacog` の「クールダウン + 適応閾値 + 全 diff 永続化」は、もし shibuya-simulation が自己改変エージェントを扱うなら最小限の再現性担保セットとしてそのまま参考にできる。

## web リサーチ

- Happy to Chat Bench は実在の社交装置。起源は 2019年6月、英 Avon & Somerset 警察の Ashley Jones 巡査部長が、詐欺被害の高齢女性から「送金しなければ何週間も誰とも話さない」と聞いたのをきっかけに Burnham-on-Sea / Taunton / Weston-super-Mare の公園に設置したもの。ベンチには "The 'Happy to Chat' Bench: Sit Here If You Don't Mind Someone Stopping To Say Hello." と書かれる。 https://www.cnn.com/2019/07/08/europe/elderly-chat-bench-trnd/index.html / https://www.washingtonpost.com/lifestyle/2019/07/17/this-towns-solution-loneliness-chat-bench/
- 学術的裏付けも 2025年に出ている: Cities & Health 誌 "Happy to chat: leveraging **phatic communication** to address loneliness and foster social connection through a public bench intervention"(Vol 10, No 2)。米マサチューセッツ州の中規模州立大学に設置し、対面交流・社会的つながり・包摂感への効果を評価したもの。 https://www.tandfonline.com/doi/abs/10.1080/23748834.2025.2544095
- World Economic Forum も "Happy Benches" としてプロジェクト化している。 https://www.weforum.org/projects/happy-benches/
- 用語の背景: **phatic communication**(交感的言語使用 = 情報伝達ではなく社会的接触の維持のための発話。Malinowski 1923 の phatic communion に由来)。本作の「ベンチは会話を命令せず、会話の**許可**を与える装置」という設計思想はこの概念に対応している。
