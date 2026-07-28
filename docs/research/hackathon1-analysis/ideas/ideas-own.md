# IDEA 起票 — 自チーム講評(shibuya-sim 35.0/40)由来

> 出典元: [`01-own-team.md`](../01-own-team.md) / 講評 `shibuya-sim_eval.md` / 検証 `shibuya-sim_eval_review.md` /
> 発表資料 `slides/04-2021_146-shibuya-sim.pdf`(いずれも [`ryukih/SD-Hackathon-Reviewer-2026May`](https://github.com/ryukih/SD-Hackathon-Reviewer-2026May))
> 起票日: 2026-07-29 / 担当: Opus 5(調査サブエージェント)
>
> 全 14 件(★★★ 6 / ★★ 6 / ★ 2)。**採否は親エージェント/ユーザーが決める**(ask-before-extending)。

---

### IDEA: ラン中 LLM 健全性 KPI(成功率 / fallback 率)の L2 系列化と watchdog ゲート

- 出典: スライド p.4「全7,680イベント中 エラー率 83.7%」/ p.6「成功率 28.5%(step0 67% → step5 6%)」/ p.10「制約: API レート制限」
- 分類: 実験・評価 / 規模化・性能
- 内容:
  第1回の最大の実害は「**ランが終わってから 83.7% がエラーだったと判明した**」こと。step 0-1 だけが
  クリーンで、step 8 以降はほぼ全エージェントがエラーだった。にもかかわらずスライドは
  そのデータから HHI を出して知見を主張せざるを得なかった。
  現行 shibuya-simulation は L1b(`observer/logger.py` の `llm_calls` → `l1b_llm.parquet`)に呼を残すが、
  実査した限り **`register_aggregator` 85 個の中に「LLM 成功率 / パース失敗率 / fallback 率」の L2 系列がない**
  (`fallback_rate|llm_fail|parse_fail|llm_error` は `observer/*.py` `cognition/*.py` でヒット 0)。
  `scripts/watchdog.py` はプロセス死・ストールは見るが「**生きているが全員 fallback**」は検知できない。
- shibuya-simulation への適用案:
  1. `src/society/observer/aggregate.py` に `@register_aggregator("llm_ok_rate")`
     `("llm_parse_fail_rate")` `("llm_fallback_rate")` を追加(L1b の当該 step 行から決定論算出。
     `__vllm_error__` 前置と JSON パース失敗を別カウント)。既存 85 集約器と同じ流儀なので局所改修。
  2. `scripts/watchdog.py` に **健全性ゲート**を足す: 直近 N step の `llm_ok_rate` が閾値
     (例 0.90)を下回り続けたら、プロセスが生きていても kill → checkpoint から再開、
     それでも回復しなければ `status=degraded` で停止して人間に上げる。
  3. `RESULTS.md` のラン台帳に **成功率列**を必ず置く(IDEA: RESULTS.md 参照)。
- web リサーチ知見:
  vLLM は `/metrics` エンドポイントで request rate / error rate / TTFT / TPOT を Prometheus 形式で出す
  ([vLLM Metrics 設計](https://docs.vllm.ai/en/latest/design/metrics/))。
  SLO を満たしたリクエストのみを数える **goodput** が LLM サービングの標準指標として定着しており
  ([Monitor LLM Inference in Production](https://www.glukhov.org/observability/monitoring-llm-inference-prometheus-grafana/))、
  シミュ側でも「成功呼のみを分母に入れた有効ステップ数」という goodput 相当の概念を持つと解釈が揺れない。
  本選はローカル vLLM なので `/metrics` をそのまま watchdog に食わせる選択肢もある(外部依存ゼロ)。
- 重要度: **★★★**(本選で採用検討。第1回の最大の実害の直接対策で、かつ現行に穴が実在する)

---

### IDEA: README に「将来展望(ロードマップ)」節を新設

- 出典: 講評 C. 発展性「**明文化された将来展望文書がない分、ロードマップ提示としては減点要因**」/ 検証レポート「減点要因: …ロードマップ文書がない」
- 分類: 提出物・審査対策
- 内容:
  C軸 8.0(唯一の 8 点台)の減点はほぼ全量が「将来展望」側だった。講評の「コード拡張性」節は
  否定語ゼロの絶賛であり、**コードではなく README の問題**で 2 点落としている。
  現行 README は研究課題(C-1)を解消済みだが、**「将来展望/ロードマップ」節がなく**
  `docs/design.md` へのリンク止まり。審査者が README しか読まなければ第1回と同じ判定になり得る。
- shibuya-simulation への適用案:
  README に 3 スパン構成で追加し、**各項目に既存内部文書へのリンクを張る**(「文書がない」の反証にする):
  - 本選期間(8/15–8/30): 観察ラン 5万〜25万体 → `docs/plans/finals-gpu-application.md` §1.2 #1 /
    k 掃引 300体×14日×30ラン → 同 #2 / 関係性内生化 6セル CRN → `conf/experiments/endogenous_accept.yaml`
  - 本選後 6か月: 100万体 → `docs/plans/million-scale.md` / VLM 視覚 → `docs/research/agent-vision.md` /
    3D PLATEAU → `docs/plans/plateau-3d.md`
  - 長期: k\* の再現性検証と論文化 / 他都市ポート(EnvPack: `env/shimokita/` で下北沢を試験済み)
  末尾に「未確定事項は `docs/design.md` §12 OPEN 台帳で管理し、勝手に確定させない運用」と書く。
  これは願望リストとの差別化になり、**研究プロジェクトの成熟度**として読ませられる。
- web リサーチ知見: なし(講評文の直接反転)
- 重要度: **★★★**(最も費用対効果が高い。数十分の作業で 2 点分の減点根拠を消せる)

---

### IDEA: `RESULTS.md` の新規作成(ラン台帳 + 成功率列 + ネガティブ結果)

- 出典: 公式サイト「実行結果のまとめ(RESULTS.md 等)もあると、審査に伝わりやすくなります」(`docs/plans/finals-gpu-application.md` §0.1 実査)/ スライド p.4・p.9 の破綻
- 分類: 提出物・審査対策 / 実験・評価
- 内容:
  現行リポジトリに `RESULTS.md` は**存在しない**(実査確認)。第1回はスライドが実質の結果報告だったが、
  講評は `src/` `config/` `README.md` `data/` しか参照しておらず**スライドの実験結果に一言も触れていない**。
  本選は「プレゼン資料・README 必須 + RESULTS.md 推奨」と公式明記のため、
  **本選では結果の質が採点対象に入る**と考えるべき。
- shibuya-simulation への適用案: 以下の 6 節構成を推奨。
  1. 1行サマリ(何が言えたか)
  2. **ラン台帳**: run_id / 条件 / 体数 / step 数 / seed / モデル / 壁時計 / **LLM 呼数と成功率**
     ← 成功率列が第1回との最大の差分アピールになる
  3. 主結果: R²(k) 曲線 + seed 階層ブートストラップ CI + k\* 候補(`scripts/analyze_sweep.py` 出力)
  4. **対照が効いている証拠**: sham / null / compute 一定で 3 信号(R² 低下・seed 発散・EWS)が出ないこと(R1)
  5. **ネガティブ結果と限界**を正直に(検出力・未達条件・残存交絡)
  6. 再現手順(`scripts/run_sweep.py` → `scripts/analyze_sweep.py` をコマンド1行ずつ)
- web リサーチ知見:
  シミュレーション研究の報告標準として **STRESS ガイドライン**
  ([Monks et al. 2019, J. Simulation](https://www.tandfonline.com/doi/full/10.1080/17477778.2018.1442155))と
  **ODD プロトコル**([Grimm et al. 2020, JASSS 23(2)7](https://www.jasss.org/23/2/7.html))が確立している。
  ODD 第2更新は「モデルが捉えられたパターンだけを報告するのは HARKing に似ており、
  **捉えられなかったパターンも報告するのが良い実践**」と明記しており、5 節(ネガティブ結果)の直接の根拠になる。
- 重要度: **★★★**(公式が名指しで推奨している唯一の追加提出物)

---

### IDEA: 「想定される結果のパターン」の事前登録(pre-registration)

- 出典: 講評 提言 P1「…創発指標の解釈、**想定される結果のパターン**を明文化することで、再現性と外部評価のしやすさが大幅に向上する」
- 分類: 実験・評価 / 提出物・審査対策
- 内容:
  P1 のうち「研究問い」「対照群設計」は現行 README で解消済みだが、
  **「想定される結果のパターン」= どう転んだら何が言えるかの事前予測が提出物にない**。
  事前予測がないと、どんな結果が出ても事後解釈(HARKing)に見えてしまう。
  逆に事前登録しておけば、**予測が外れても「予測外の発見」として語れる**。
- shibuya-simulation への適用案:
  README(または RESULTS.md 冒頭)に「### 想定される結果のパターン」を置き、
  ラン実行**前**に以下を書いてコミットする(git 履歴が事前性の証拠になる):
  - R²(k) が k に対して単調減少し sham で減少しない → **創発レジームの支持**
  - R²(k) が k に依らず高止まり → **初期条件支配(「生まれつき」寄り)**
  - sham でも同じ低下 → **計算量交絡**であり k\* の主張は取り下げる
  - seed 発散が k\* 近傍だけで立ち上がる → **相転移の傍証**(単調なら臨界ではない)
  さらに `docs/design.md` §3「反証可能な再定式化」から昇格させる形にすれば、内容は既にある。
- web リサーチ知見:
  ODD 第2更新([JASSS 23(2)7](https://www.jasss.org/23/2/7.html))は
  「捉えられたパターンのみの報告は HARKing に類似」と警告。
  AI エージェント実験の事前登録テンプレートも提案され始めている
  ([Preregistration for Experiments with AI Agents, arXiv 2606.11217](https://arxiv.org/pdf/2606.11217))。
  心理学方法論のシミュレーション研究でも「計画・事前登録・報告」の標準テンプレートが提案されている
  ([Simulation Studies for Methodological Research in Psychology](https://www.researchgate.net/publication/375251208_Simulation_Studies_for_Methodological_Research_in_Psychology_A_Standardized_Template_for_Planning_Preregistration_and_Reporting))。
- 重要度: **★★★**(P1 の唯一の未消化部分。実行前でないと価値が消えるので**時間的制約が強い**)

---

### IDEA: プロンプト文言のゴールデン監査(行動誘導表現の禁止語リスト)

- 出典: 講評 A軸 唯一の減点根拠「`src/simulation.py:329-336` — 『Choose stay when … prefer to move』というやや方向付けのある一文」/ 検証レポート「単なるヒントではなく `"most people don't stand still without reason"` という**明確な行動誘導文**で、創発設計の純度を若干損なう」
- 分類: 創発設計 / 実験・評価
- 内容:
  A軸 −1.0 の明示根拠はこれ 1 点だけだった。現行の no-fingerprint(R9)は
  「**engine が因子名を名指ししない**」契約で `tests/test_contracts.py` が担保しているが、
  「**行動の一般論ヒントをプロンプトに書かない**」ことを固定するテキスト監査は実査範囲で見つからなかった。
  R9 と「行動誘導ゼロ」は別の性質であり、後者は今も無防備。
- shibuya-simulation への適用案:
  `tests/` に `test_prompt_audit.py` を新設し、`cognition/{planning,deliberate,reflection}.py` が
  生成するプロンプト文字列(mock ラン 1 本ぶんを固定入力で生成)に対して:
  1. **禁止語彙リスト**の非出現を assert(例: `prefer to`, `should`, `most people`, `typical`,
     `普通は`, `〜するとよい`, `おすすめ`, `〜べき` …)。
     ※ ただし「規範発話の創発」を観測したいので、**エージェント発話**ではなく
     **システムプロンプト側**に限定して検査する(検査対象の切り分けが要)。
  2. **ゴールデン固定**: 承認済みプロンプト全文を `tests/fixtures/` にスナップショットし、
     差分が出たら人間レビューを強制する。既存のゴールデンテスト運用にそのまま乗る。
  3. 監査結果を `docs/research/agent-freedom-audit.md` に追補し、README の R9 節から参照。
- web リサーチ知見: なし(講評の直接指摘への対処)
- 重要度: **★★★**(A軸の唯一の失点原因。現行に対策が確認できず再発しうる)

---

### IDEA: 「実装したのに評価されていない強み」を README に列挙する

- 出典: 検証レポート「見落とし」欄(全4カテゴリに存在)
- 分類: 提出物・審査対策
- 内容:
  検証レポートは、**評価者が拾い損ねた強み**を各軸で列挙している:
  `_needs_boost` の正フィードバックループ / `_PER_STEP_DRIFT` の時刻ドリフト /
  `events.yaml`・`environment.yaml` / `smartphone_use` 計算式 / 4thレイヤペルソナ属性 /
  seed 派生 RNG による完全決定性 / Ollama→OpenAI のローカル→クラウド移行ワークフロー。
  つまり **実装してあっても README に書いていなければ採点されない**。
  現行 shibuya-simulation はこの問題がさらに深刻で、122 モジュール・実データ 5 系統・
  1,725 テストの大半が README に現れない。
- shibuya-simulation への適用案:
  README に「## この実装の技術的特徴」節を新設し、**採点されうる形で**箇条書き:
  - no-fingerprint(R9)を `tests/test_contracts.py` で機械担保
  - 中央集権シード + 応答キャッシュで**呼び出し順に依存しない**決定論(`tests/test_determinism.py`)
  - CRN(同一 seed 列)+ sham / null / compute 一定対照(R1)
  - 観測と本体の frame 分離(`observer/` 85 集約器・L1→L2→L3 の事後計測のみ)
  - 実データ 5 系統(OSM / 国交省人流 / ODPT 実ダイヤ / フロアガイド / 組織台帳 1.1万)+ 出典・ライセンス個別明記
  - LLM 一括発行(`engine.batch_llm`)が**逐次経路とバイト一致**(`tests/test_batch_llm.py`)
  - 複数 vLLM サーバへの sticky routing + 障害時再分配(`llm/fleet.py`)
  - テスト 175 ファイル・1,725 件
- web リサーチ知見: なし
- 重要度: **★★★**(第1回で「言及がないから減点されなかった/加点されなかった」現象が両方向に起きている)

---

### IDEA: 埋め込みベースの集合注目検出(detect_emergence の定量強化)

- 出典: 講評 提言 P4「創発検出が現状 stdlib-only の正規表現＋類似度ベースで保守的。実験規模に対して**埋め込み類似度ベースの集合注目検出**など、より定量的な追加指標を準備すると分析の説得力が増す」
- 分類: 実験・評価 / 創発設計
- 内容:
  現行 `scripts/detect_emergence.py` は旧実装の思想を parquet L1 へ移植済みだが、
  docstring が明記するとおり依存は「標準ライブラリ + pyarrow + omegaconf のみ」で
  `difflib.SequenceMatcher` を使う**表層一致**のまま。P4 は未消化。
  「#渋谷 #カフェ が独立に 8 ペルソナで採用された」(スライド p.8)ような**語形一致**は取れても、
  「同じことを別の言い方で言い始めた」= 意味収束は取れない。
- shibuya-simulation への適用案:
  1. 本選は GPU があるので、埋め込みモデルを 1 枚に載せる(または vLLM の embeddings API を使う)。
     `scripts/detect_emergence.py` に `--embed` オプションを足し、既定 OFF(stdlib のみ)を維持
     = **依存ゼロの現行挙動を壊さない**。
  2. 指標: 発話埋め込みの (a) 時系列コサイン分散の低下、(b) **内在次元(intrinsic dimensionality)の低下**、
     (c) クラスタ数の減少。いずれもラン内で単調評価でき、sham 対照との差分が取れる。
  3. `observer/measure.py` の既存 `vocab_entropy`(語彙エントロピー)と**併記**して、
     「表層(語彙)は収束していないが意味は収束した/その逆」を分離して語れるようにする。
- web リサーチ知見:
  [Emergent Convergence in Multi-Agent LLM Annotation (BlackboxNLP 2025 / arXiv 2512.00047)](https://arxiv.org/abs/2512.00047)
  が 7,500 討論・12.5 万発話で、**出力埋め込みの幾何**を追跡し
  「ラウンドが進むと内在次元(TwoNN-Id)が低下する = 意味的圧縮」を示している。
  役割プロンプトなしでも語彙的・意味的収束と非対称な影響パターンが出る、という点が本プロジェクトの
  「no-fingerprint で創発を観測する」姿勢と整合。指標の実装レシピとしてほぼそのまま使える。
- 重要度: **★★**(記録価値大。本選中に入れるなら既定 OFF の追加オプションとして低リスクに)

---

### IDEA: SNS の返信・引用連鎖(reply/quote)と「反応が返るまでの時間」の観測

- 出典: スライド p.8「**0 件の reply / quote** → 互いに反応するには時間が必要」「短時間ウィンドウでは投稿先行、会話は未発達」
- 分類: 世界設計 / 実験・評価
- 内容:
  第1回は 6 step(1時間)ウィンドウで SNS 15 投稿・**reply/quote ゼロ**だった。
  投稿は起きるが**会話にならない**という結果は、研究課題 Q2(SNS は物理集中を代替するか)に
  答えるための前提条件が満たされていなかったことを意味する。
  現行 `src/society/net/internet.py`(212行)は post / like / reshare を実装(`n_likes_total` / `reshares`)しているが、
  **reply(返信スレッド)は実査範囲で確認できなかった**。
- shibuya-simulation への適用案:
  1. 本選は 3〜10 シミュ日を回すので、そもそも時間窓の問題は解消する。
     ただし「**反応が返るまでの平均 step 数**」を L2 系列に置くと、
     「短い窓では会話が立たない」という第1回の知見を**定量的に再現・確認**でき、
     RESULTS.md で「第1回の未解決点を回収した」と書ける(継続性のアピール)。
  2. reply が未実装なら、`internet.py` に `kind="reply"`(親 post id を持つ)を追加するかを判断。
     ただし現行は物理側の `conversation.py` / `gossip.py` / `media.py` が対話を担う設計なので、
     **ネット上の対話連鎖が研究課題に必要かどうか**を先に決める(ask-before-extending)。
- web リサーチ知見:
  [Simulating hashtag dynamics with networked groups of generative agents (arXiv 2510.26832)](https://arxiv.org/pdf/2510.26832)
  が、生成エージェントのネットワーク群でハッシュタグ動態を再現する設計を扱っている。
  第1回の「#渋谷 #カフェ が 8 ペルソナで独立採用」という観測は、この系統の先行研究と
  直接比較可能な形にできる(採用曲線 S 字・独立採用者数)。
- 重要度: **★★**(記録価値あり。実装追加は要判断)

---

### IDEA: 旧実装の主役指標(HHI / 効果的選択肢数)を現行 L2 に接続して「継続性」を示す

- 出典: スライド p.5「HHI(集中度) = 0.179 / 効果的選択肢数 = 5.6(実際使用 9 POI)」/ p.7「HHI = 0.231(vs 実験1の 0.179)」
- 分類: 実験・評価 / 可視化
- 内容:
  第1回の主役指標は **HHI(目的地集中度)と効果的選択肢数**だった。
  現行 shibuya-simulation には `vocab_entropy`(`observer/measure.py:695-712` / `stream.py:479-496`)、
  `place_entropy_bit`(`scripts/analyze_resolution.py:141`)、`visit_entropy_mean`(`scripts/analyze_groups.py:251`)、
  Gini・上位10%集中度(`observer/aggregate.py` / `observer/assets.py`)がある一方、
  **HHI と効果的選択肢数(= 2^entropy or 1/HHI)に相当する L2 系列は見当たらない**。
- shibuya-simulation への適用案:
  1. `observer/aggregate.py` に `@register_aggregator("dest_hhi")` と `("dest_effective_n")` を追加
     (目的地 POI 分布から決定論算出。既存 `_gini` と同じ流儀で numpy 非依存に書ける)。
  2. RESULTS.md で「第1回 80体×1step で HHI 0.179 → 本選 N万体×10日で HHI x.xxx」と**並べる**。
     ただし第1回の数値は n=80・1 step・エラー率 83.7% 下の値なので、
     **参考値であることを明記**して同一土俵で比較しない(第1回 p.9 の交絡表の轍を踏まない)。
  3. 効果的選択肢数はエントロピーの指数だから、既存 `place_entropy_bit` から**変換 1 行**で出る。
     実質コストはほぼゼロ。
- web リサーチ知見: なし
- 重要度: **★★**(低コストで「第1回からの継続研究」という物語が作れる)

---

### IDEA: 巨大ファイル(`scheduler.py` 4,541行)の分割 seam を docs に明示する

- 出典: 講評 D軸 唯一の減点根拠「`src/simulation.py` が約1000行と大きく、プロンプト構築／IO／apply phase が同一ファイルに集中している点」/ 提言 P2 / 検証レポート「**958行**でモノリシック」
- 分類: その他(保守性)/ 提出物・審査対策
- 内容:
  現行は 7 ファイル → **122 モジュール**へ大幅分割したが、
  `src/society/engine/scheduler.py` = **4,541行**、`engine/simulation.py` = 1,341行、
  `observer/measure.py` = 1,123行 が残る。第1回で減点対象になった 958 行の **4.7 倍**の単一ファイルがある。
  同じ指摘が本選でそのまま再発しうる。
- shibuya-simulation への適用案:
  本選期間中の全面リファクタは回帰リスクが高い(1,725 テストの再検証が要る)。最小コストの対策:
  1. `docs/design.md` §11「モジュール構成(seam 一覧)」に
     **「なぜ scheduler.py が大きいか + 将来の分割 seam」**を追記
     (phase 単位: planning / reflect / commerce / transit / joint …)。
  2. README のアーキテクチャ節からそこへリンク。
     「認識していて計画がある」ことが読めれば、「気づいていない」よりはるかに心証が良い。
  3. 余力があれば、**依存が薄い 1 phase だけ**を先に切り出して分割可能性の実証にする
     (全部やらない。ゴールデンテストがあるので安全に切れる範囲だけ)。
- web リサーチ知見: なし
- 重要度: **★★**(D軸の唯一の失点原因だが、本選期間の工数配分としては優先度中)

---

### IDEA: アーキテクチャ 1 枚図(mermaid)を README に

- 出典: 講評 C軸「モジュール分離が極めて明確」(src/ 7 ファイルでも褒められた)/ スライド p.3 の薄さ(システム構成が 8 行)
- 分類: 提出物・審査対策 / 可視化
- 内容:
  第1回は **src/ 7 ファイル**の構成でも「モジュール分離が極めて明確」と高評価だった。
  現行は 122 モジュール + 4 層(空間 / 資源 / 象徴 / social network)+ observer frame 分離という
  はるかに厚い構造を持つが、README ではディレクトリツリー(L58-71)しか示していない。
  一方スライド p.3 の「システム構成」は 8 行しかなく、
  **コードを読んだ講評のほうがスライドより世界設定を高く評価する**という逆転が第1回に起きている。
- shibuya-simulation への適用案:
  README に mermaid 図を 1 枚(GitHub がそのまま描画するので**追加依存ゼロ**):
  - 上段: 世界(空間 / 交通 / 経済 / 組織 / 制度 / メディア)
  - 中段: エージェント(persona → factors → cognition LOD → actions)
  - 下段: **observer(点線で分離)** — 「シム本体は記録するだけ・測定は事後」を図で示す
  - 横: LLM 層(mock / ollama / vllm / fleet router)
  本選スライドにも同じ図を流用する(p.3 の薄さの解消)。
- web リサーチ知見: なし
- 重要度: **★★**(B軸の厚みと C軸の拡張性の両方に効く。作業量小)

---

### IDEA: 「代替説明を自分から潰す」節を RESULTS.md に制度化

- 出典: スライド p.7「これは社会的同調ではなく**構造誘発**(駅から見える POI が共通)」
- 分類: 実験・評価 / 提出物・審査対策
- 内容:
  第1回スライドで最も研究者的に強かったのがこの 1 行。
  「集中が起きた」だけなら創発と言い張れるところを、**自分から代替説明(構造誘発)を提示して
  社会的同調説を棄却している**。これは自動採点では拾われていないが、人間審査員には強く効くはず。
  現行の研究課題(k\* 探索)でも同型の代替説明が複数ある。
- shibuya-simulation への適用案:
  RESULTS.md に「### 代替説明の棄却」節を固定枠として置き、各主張について対抗仮説と棄却根拠を対で書く:
  - 「R² 低下 = 創発」に対する代替説明 → **計算量交絡**(sham で同じ低下が出れば棄却できない)→ R1 対照で潰す
  - 「seed 発散 = 相転移」に対する代替説明 → **単なる分散増**(k に依らず発散するなら臨界ではない)
  - 「ラベル採用の S 字 = 伝播」に対する代替説明 → **共通環境刺激による同時発火**(伝播経路を L1 で追う)
  - 「集中 = 社会的同調」に対する代替説明 → **構造誘発**(第1回と同じ。可視性・距離で説明できるか)
- web リサーチ知見:
  Grimm らの **Pattern-Oriented Modelling (POM)** は、複数スケールの複数パターンを
  「非現実的なモデル構造・パラメータ組を棄却するフィルタ」として使い、
  **別の独立したパターン集合で検証する**という二段構えを提唱している
  ([Gallagher et al. 2021, Biological Reviews](https://onlinelibrary.wiley.com/doi/10.1111/brv.12729) /
  [POM: a 'multi-scope' for predictive systems ecology, PMC3223804](https://pmc.ncbi.nlm.nih.gov/articles/PMC3223804/))。
  「1 つの出力変数の一致では不十分」という POM の中核主張は、
  本プロジェクトの「3 信号(R² 低下・seed 発散・EWS)の三角測量」と同じ発想であり、**引用できる**。
- 重要度: **★★**(記録価値大。RESULTS.md を書くなら同時に入れられる)

---

### IDEA: 比較表は「1 因子差分」に固定する設計規律

- 出典: スライド p.9「実験1 vs 実験2 比較」— 実験1(80体×96step・16時間)と実験2(200体×6step・1時間)を並べ、HHI 0.179 → 0.231 を「密度依存集中増幅」と読んでいる
- 分類: 実験・評価
- 内容:
  第1回の比較表は**体数も時間幅も同時に変わっており**、密度効果と時間帯効果が交絡している。
  「06:00 の 1 step だけ」vs「全日 96 step」でも HHI は変わるので、
  この表から「密度が集中を増幅する」は結論できない。
  現行は CRN・sham・compute 一定対照(R1)を持つので**枠組みとしては解消済み**だが、
  **提出物の表を作る段階での規律**は別問題として残る。
- shibuya-simulation への適用案:
  RESULTS.md / スライドに載せる比較表に規約を課す:
  1. 1 つの表で**変える因子は 1 つだけ**。体数を変えるなら step 数と seed は固定。
  2. 表のキャプションに「固定した因子」を必ず明記(例:「seed=1..5 固定・144step 固定・条件 k=free 固定」)。
  3. 交絡が避けられない比較は**別の表**にして「参考値・直接比較不可」と本文で断る。
  4. すべての数値に **n と CI** を付ける(第1回は HHI に CI がなかった)。
     `scripts/analyze_sweep.py` は seed 階層ブートストラップ CI を出せるので出力をそのまま使う。
- web リサーチ知見: なし
- 重要度: **★**(参考。ただし RESULTS.md 作成時に必ず参照すべき規律)

---

### IDEA: コード参照は行番号でなく関数名・見出しで書く

- 出典: 検証レポート「**引用行番号の系統的ズレ**: `src/simulation.py` の引用行が概ね **20〜40行下方**にズレている(最大約33行)…スコアへの影響は無いが、検証者の手間が増えるため修正推奨」
- 分類: 提出物・審査対策
- 内容:
  第1回の検証レポートは、講評が挙げた **24 個の引用行番号すべてを実ファイルと突き合わせて**検証していた。
  つまり**採点は再検証される**。行番号はコミットのたびに陳腐化するため、
  本選中に README / RESULTS.md に書いたコード参照は、提出時点で必ずズレる。
- shibuya-simulation への適用案:
  README / RESULTS.md / スライドでコードを参照するときは:
  - ✗ `src/society/engine/scheduler.py:812`
  - ○ `src/society/engine/scheduler.py` の `_phase_planning_batched()`
  - ○ `docs/design.md` §11「モジュール構成(seam 一覧)」
  数値を書くときは**出典ファイル名を併記**する。
  `docs/plans/finals-gpu-application.md` の【実測】【推定】【本書計算】凡例は良い先例で、
  提出物にもこの流儀を持ち込むと「検証可能性が高い」という心証になる。
- web リサーチ知見: なし
- 重要度: **★**(参考。ただしコストゼロで守れる)

---

## サマリ表

| # | IDEA | 分類 | 重要度 | 主な根拠 |
|---|---|---|---|---|
| 1 | LLM 健全性 KPI + watchdog ゲート | 実験・評価 / 規模化 | ★★★ | スライド p.4「エラー率 83.7%」・現行に L2 系列が実在しない |
| 2 | README「将来展望」節 | 提出物・審査対策 | ★★★ | C軸 −2.0 の主因「ロードマップ文書がない」 |
| 3 | `RESULTS.md` 新規作成 | 提出物・審査対策 | ★★★ | 公式推奨・現行に不在 |
| 4 | 想定される結果のパターンの事前登録 | 実験・評価 | ★★★ | 提言 P1 の未消化部分・実行前でないと価値が消える |
| 5 | プロンプト文言のゴールデン監査 | 創発設計 | ★★★ | A軸 唯一の減点根拠・現行に対策未確認 |
| 6 | 実装済みの強みを README に列挙 | 提出物・審査対策 | ★★★ | 検証レポート「見落とし」欄が全軸に存在 |
| 7 | 埋め込みベースの集合注目検出 | 実験・評価 | ★★ | 提言 P4 未消化 |
| 8 | SNS reply/quote と反応遅延の観測 | 世界設計 | ★★ | スライド p.8「reply/quote 0 件」 |
| 9 | HHI / 効果的選択肢数の L2 接続 | 実験・評価 | ★★ | 第1回の主役指標・現行に相当系列なし |
| 10 | 巨大ファイルの分割 seam を docs 明示 | その他 | ★★ | D軸 唯一の減点根拠・現行は 4.7 倍に肥大 |
| 11 | アーキテクチャ 1 枚図(mermaid) | 可視化 | ★★ | スライド p.3 の薄さ・122 モジュールが伝わらない |
| 12 | 「代替説明の棄却」節の制度化 | 実験・評価 | ★★ | スライド p.7 の良い先例 + POM 文献 |
| 13 | 比較表は 1 因子差分に固定 | 実験・評価 | ★ | スライド p.9 の交絡 |
| 14 | コード参照は行番号でなく関数名 | 提出物・審査対策 | ★ | 検証レポートの行番号ズレ指摘 |
