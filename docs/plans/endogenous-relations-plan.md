# 関係性の内生化 — 検証済み実装計画・実験設計(2026-07-27)

> 出自: `docs/endogenous-relations-implementation.md`(Claudeチャット由来の実装指示・2026-07-27精査)を、
> コード実査(Explore)+Web文献リサーチで検証・具体化した**正典**。原文書は本書へ吸収済みのため削除
> (全文は git 履歴 c8866e2 以降のコミットに保存)。
> 状態: **フェーズ1=第62バッチ(d6731e5)・フェーズ2=第63バッチ・フェーズ3=第64バッチ(6ad4b12)・
> フェーズ4=第65バッチで実装済み**(2026-07-27 ユーザー「1〜4まで進めていい」)・フェーズ3/4の
> 実験としての実施はフェーズ2評価(本選実LLM=D17)の phase3_go 合否ゲート。
> 体制: Fable計画/検収・実行役=Fable継承サブ(2026-07-27〜)。

---

## 1. 妥当性検証の結論(原文書に対する所見)

**骨格は妥当・文献支持あり**。「較正値を候補提示の事前分布に残し、最終判断のみ委譲する二段構え」は
LLMを較正済み測定器として使う先行設計(LLMs as Calibrated Measurement Instruments, arXiv:2602.01022)と
同型。二層切り分け(初期構造=機構維持/変化=委譲)も交絡排除として正しい。

**訂正・具体化 5点**:

1. **「エージェント思考が社会的位置を変えられない」は部分的に旧い**。第60バッチ(job_search=LLM選択由来の
   転職)・B3b(遭遇→会話相手)・第61(gossip)で内生経路は既に存在する。ただし関係形成の中心=誘い承諾は
   なお較正確率の抽選(`joint.py:346-348`・S-R3/S-R4共通・stream "joint")であり、勝負どころの選定は正しい。
2. **技術的前提の訂正(最重要)**: 原文書の推奨「同stepでLLM思考層に載っている出力から抽出」は**現phase順で
   不成立**。`_phase_joint`(承諾判定)は日境界=真夜中に走り、当日の `_phase_planning`(朝)・発話(`_phase_drive`)
   より**前**。被誘者の当日LLM出力は承諾時点で未生成。→ 主経路を**構造化・決定論抽出**に変更する(§2)。
   phase順の移動は draw 順・既存挙動への波及が大きく不採用。
3. **sycophancyリスクは実証済みの既定路線**: LLMに受諾/拒否を直接生成させると承諾率が現実統計から上振れする
   (Simulated Customers Never Walk Away, arXiv:2606.20708 が定量確認。Generative Agents では招待12→来場5=
   不履行型の脱落もある)。本計画の設計は**LLMにYES/NOを聞かない**(呼数ゼロ制約の副産物として構造化出力からの
   決定論読み取りになる)ためこのバイアスの侵入経路は限定されるが、k↑で計画自体が社交過多になる経路は残る。
   → **承諾率乖離KPIをフェーズ移行の合否判定に第一級化**(§3)。
4. **較正の器が無い**: `calibrate_report.py` の REALITY バンドに承諾率・共同行動率は不在(較正基準は
   `docs/research/relationships-activities.md` §2.5-2.6 とjoint.py DEFAULTSコメントに埋没)。
   フェーズ1で新バンド+L2列+`analyze_sweep._EXTRA_L2_SERIES` 接続を必須実装とする。
5. **gossipとの合成順序の明示**: 第61の `gossip.joint_penalty` が既に承諾式へ介入済み。合成は
   `p = clamp(w·p_calib + (1−w)·p_endo) − gossip_penalty`(gossipは常に最後の減算=第61の不変則維持)。

**日本語態度抽出の限界(文献)**: 敬語・婉曲拒否(「行きたいのは山々ですが…」)は辞書法で誤検出しやすい。
自由文からの抽出は**明示キューに限定**し、曖昧例はフォールバックへ(フォールバック率自体を品質指標に)。

---

## 2. フェーズ1: 承諾/拒否の内生化(実装設計・確定)

変更点は `joint.py` 承諾抽選の1箇所+新モジュール `src/society/relations_endo.py`(society直下=
no-fingerprint走査外・mobility/gossipと同層)。conf `relations.endogenous_accept.*` 既定OFF。

- **always-draw, conditionally-use**: ONでも "joint" stream の draw 数を不変に保つ(drawして条件次第で
  結果を破棄=compute_matchedのRNG版。draw列のズレ防止・監査容易・resume無風)。
- **判定材料(優先順・全て決定論・LLM呼ゼロ・中間状態が監査可能)**:
  1. **予定帳簿の当日衝突**(`schedule.py` の appointment 台帳・schedule ON時): 誘いの時間帯と重複する
     当日予定があれば拒否(conflict_veto)。
  2. **前日 `day_schedule` の志向**: `with` に誘い主の名が載る=積極受諾/solo系cat卓越=消極。
     (構造化フィールドのみ=敬語・婉曲問題を構造的に回避)
  3. **関係台帳の直近valence**(relations ON時): 直近の負交流→拒否傾向。
  4. **判定不能→較正確率フォールバック**(fallback率をL2記録=「どれだけ内生化できたか」)。
- **自由文抽出**は明示キュー(前日発話中の「(相手名)と…したい/行こう」型)のみ・パターンの層分割は
  schedule.py 前例(基盤=コード・地名/固有=conf)を踏襲。
- **conf**: `relations.endogenous_accept.{enabled=false, prior_weight=0.5, conflict_veto=true,
  positive_boost, negative_cut, fallback="calibrated"}`。
- **観測(L2・ON時のみ)**: `joint_accept_rate` / `joint_endo_share`(内生判定率=1−fallback率)/
  `joint_accept_calib_gap`(較正基準との乖離pp)。+ `calibrate_report.py` REALITYバンド追加
  (レジャー白書§2.5-2.6基準)+ `analyze_sweep._EXTRA_L2_SERIES` へ接続(deviation_mean前例)。
- **履行率の観測(文献由来の追加)**: 承諾→実同席の率(`joint.observe` 同席観測と突合)と脱落理由。
  Generative Agents の「関心はあるが不履行」を弁別する。
- **検収**: OFF=ゴールデンL1バイト一致・draw数不変・compute_matched・no-fingerprint・
  resume==straight(状態はagent属性 or checkpoint中央管理=第59-61前例)・ダッシュボードで乖離と
  fallback率が目視可能。

## 3. フェーズ2: treatment比較の実験設計(確定)

- **条件**: endogenous_accept {OFF, ON} × k {off, degraded(α=0.5), free} = **6セル**。
  `run_experiment.py` + `conf/experiments/endogenous_accept.yaml` のconf宣言方式(spark前例)。
- **seedペア(CRN)**: 同一seedでOFF/ONをペア比較(ABM標準の分散低減・arXiv:2409.02086)。
  always-draw設計により分岐前のRNG消費が同一=ペアの共分散が保たれる。
- **規模**: 予備=7日100体×各セルseed3(mock=配線・指標感度の検証のみ。実LLM判断は本選)。
  本実験=14日×seed5/セル(30ラン)を本選GPU予算内で(D17)。
- **指標**: タスクB4種(edge_churn/コミュニティJaccard/中心性turnover/順位τ固着=
  `structure.py`+`analyze_structure.py` の既存列がそのまま対応)+承諾率乖離+fallback率+履行率+
  弱い紐帯レンズ(第59 `analyze_weak_ties.py`)。
- **検定**: seedペア差の permutation(sign-flip)。ネットワーク構造比較は double permutation を推奨
  (Farine 2022=素朴置換は過大有意)。
- **仮説(理論から導出・Jackson-Wolinsky/triadic closure×homophily)**:
  - H1: ON で edge churn↑(主体選択が構造を動かす)
  - H2: 同時に homophily×三者閉包でコミュニティ固着帯も発生(**H1と両立**=Science Advances aax7310)
  - H3: k×ON の交互作用(k↑でONのみ構造変動が増える=本命)
- **フェーズ3進出の合否**: H1/H3 のいずれかが3seed以上で符号一致、かつ承諾率乖離が±15pp以内
  (超過時はプロンプトでなく prior_weight で調整=呼数不変のまま)。満たさなければ結果をdevlogに記録し終了
  (原文書の「フェーズ2を飛ばさない」を維持)。

**実装済み(第63バッチ 2026-07-27)・実行手順**:
- マニフェスト: `conf/experiments/endogenous_accept.yaml`(本実験=14日100体×6セル×seed[11,13,17,19,23]
  =30ラン・CRN)/ `endogenous_accept_pilot.yaml`(予備=7日100体×seed3・mock固定)/
  `endogenous_accept_wiring.yaml`(配線検証=7日60体×seed2=12ラン・実行済み)。
- 実行: `python scripts/run_experiment.py conf/experiments/endogenous_accept.yaml`(本選=D17 は
  common に model.backend=vllm 等を重ねる。mock は配線検証のみ=fallback支配でONの効果ほぼゼロが正)。
- 解析: `python scripts/analyze_endo_treatment.py "runs/endo14_*" --out runs/_endo14`
  = CRNペア差+sign-flip 主検定(n≤12 全列挙 / n>12 MC 1万回=Phipson & Smyth 2010)+日次ブロック
  符号反転の副検定(Künsch 1989 の趣旨)+H1/H2/H3 と乖離ゲートの機械判定。ネットワーク内置換は
  しない(Farine 2022 の過大有意回避=ラン単位置換)→ `python scripts/make_endo_report.py runs/_endo14`
  (自己完結HTML の条件比較ビュー)。
- 配線検証実測(mock・7日60体・12ラン): 合計約22分(1ラン94–112秒)。全ペア差 p=1.0=「差なし」を
  正しく検出・calib_gap +0.8〜+3.5pp(±15pp内)・endo_share 0.06–0.11(fallback支配=設計どおり)。

## 4. フェーズ3/4(条件付き・原文書の方針を踏襲)

- フェーズ3(誘う相手の内生化): 対象は `joint._companions` の決定論選抜。前日出力の志向抽出+
  フォールバック。Dunbar上限は `friends.py` の層次数上限(close 3-5/friend 7-12/acq +20)をconf参照で維持。
  観測: 誘い先分布の関係強度分布からの乖離・弱い紐帯誘いの発生率・クラスタ係数/直径。
  - **実装済み(第64バッチ 2026-07-27)・実験投入は phase3_go ゲート**(analyze_endo_treatment の
    機械判定合格が条件=実装と実験実施の分離)。conf `relations.endogenous_invite.*` 既定 OFF。
    friend 経路の候補集合の並べ替え・拡張のみ(枠組み・min/max_group・daily_rate 不変):
    ①前日計画 with(従来=最優先)→②前日発話の明示キュー(フェーズ1 `_has_positive_cue` の役割交換
    で invite 方向に再利用=語彙は accept ブロックと共用)→③closeness 降順(較正事前分布の維持=
    二段構えの invite 版)→④弱い紐帯探索枠(tier=1 知人・(agent,day) 安定ハッシュ=乱数ゼロ・末尾。
    `weak_tie_slots=1`=誘い先が知人である現実頻度の直接統計は文献に見つからず保守的既定。理論根拠:
    Granovetter 1973 AJS 78(6) / Onnela et al. 2007 PNAS 104(18):7332=交流量の大半は強い紐帯)。
    層次数上限は不変更(誘い=一時的接触・tier 遷移は relations の closeness 蓄積経由のみ=構造上
    新規超過しない)。"joint" stream は承諾抽選専用を維持(invite 側は乱数ゼロ。ON で候補列が変わる
    ことによる承諾 draw 数差は treatment そのもの)。観測: `joint_invite.source`(accept ON 時のみ
    L1 に出る=正直な限界)+ L2 `invite_weak_tie_rate` / `invite_endo_share`(analyze_endo_treatment
    の KPI_COLS へ接続済み)+ クラスタ係数/直径は `analyze_weak_ties.py` へ追加(既存 analyze 系に
    事後算出が無かったため)。resume==straight(`_invite_state` を checkpoint 中央管理)。
    テスト: `tests/test_endogenous_invite.py`。
- フェーズ4(関係の質): 会話由来の増減を closeness への不透明magnitude片方向hook(現 `note_contact` は
  valence符号のみ=magnitude一定なので拡張点は明確)。発火判定には流さない。優先度低・本選前不要。
  - **実装済み(第65バッチ 2026-07-27)・実験投入は phase3_go ゲート**(フェーズ3と同じ扱い=実装と
    実験実施の分離)。conf `relations.endogenous_quality.*` 既定 OFF・要 `relations.enabled=true`。
    `relations.note_contact` が `magnitude`(既定 1.0=×1.0 は IEEE754 で厳密=OFF バイト一致)を受け、
    増減**量**にのみ乗る。値の算出は `relations_endo.magnitude_of/contact_magnitude`(既生成テキストの
    決定論抽出=LLM 呼ゼロ・乱数ゼロ): ①発話長(len_chars 正規化・len_gain まで)②往復数(相手別
    リングバッファ `_dialog_hist` の蓄積・turn_gain/回・turn_max 上限)③明示キュー共起(フェーズ1
    `positive_cues` をそのまま再利用=語彙は単一の源・cue_gain)④`hedge_markers` 共起は**中立 1.0**へ
    (曖昧例を落とす=フェーズ1と同じ保守側)→ [mag_min, mag_max] へ clamp。
    文献: Altman & Taylor 1973(社会的浸透)/ Reis & Shaver 1988(親密さ=自己開示+応答性)/
    Laurenceau, Barrett & Pietromonaco 1998 JPSP 74(5):1238-1251(開示の**深さ**と応答性が当日の親密さを
    予測・事実より感情の開示)。**正直な限界**: 文字数は「深さ」の代理にならないので len_gain は最大の
    加点にしない(0.5=cue 0.4/turn 0.45 と同程度)。
    **片方向 hook の厳守**: magnitude は engine の `_quality_mag`→`_contact` 以外へ渡らない=発火判定・
    会話ペアリング・tier 閾値の式・誘い/承諾判定には流さない。tier 閾値を凍結すると quality ON/OFF で
    L1 が**完全一致**し LLM 呼数も一致することをテストで固定(通常設定で tier 遷移の時期が動くのは
    closeness 蓄積速度の変化経由=treatment そのもの)。観測: L2 `quality_magnitude_mean`(当日の会話由来
    magnitude 平均。`analyze_sweep._EXTRA_L2_SERIES` と `analyze_endo_treatment.KPI_COLS` へ接続)。
    resume==straight(`_quality_state` を checkpoint 中央管理・日境界の初期化は `_phase_relations_day`)。
    テスト: `tests/test_endogenous_quality.py`。
    mock 実測(432step・60体・quality+accept+invite+関係系 ON): 会話由来 magnitude 1601 件・
    mean 1.255 / min 1.000 / max 1.875・中立(hedge 共起)18.7%・上限 clamp 到達 0%
    (mock の発話は 1 文で短く長さ加点が飽和しないため。実LLM ではより長い発話=分布は上振れし得る)。
  - **第64からの引き継ぎ(追加実装なし)**: source=weak_tie 起点の接触が tier 遷移に至る率は、
    既存 L1 の `joint_invite.source` と `relation_tier`(other/tier/step)の事後突合で算出できる
    (`analyze_weak_ties.py` の材料が揃っている)=新規実装は不要。

## 5. 本選判断

`finals-day1-decisions.md` D17 に登録: endogenous_accept 条件を本選で回すか(6セル×ラン数のGPU配分)。

## 主要出典

- Simulated Customers Never Walk Away(sycophancy承諾上振れの直接実証): arXiv:2606.20708
- Generative Agents(招待12→来場5=不履行型脱落): arXiv:2304.03442
- LLMs as Calibrated Measurement Instruments(二段構えの同型): arXiv:2602.01022
- CRN in ABM(seedペア分散低減): arXiv:2409.02086 / Farine 2022(double permutation): 10.1111/2041-210X.13741
- Windrum et al. 2007(calibration/validation分離): JASSS 10/2/8
- Jackson & Wolinsky 1996(戦略的ネットワーク形成)/ triadic closure×homophily: 10.1126/sciadv.aax7310
- フェーズ4(会話の質→関係の深化): Altman & Taylor 1973 社会的浸透理論 / Reis & Shaver 1988 対人過程
  モデル(自己開示+応答性)/ Laurenceau, Barrett & Pietromonaco 1998 JPSP 74(5):1238-1251
  (日誌法: 知覚された開示の**深さ**と応答性が当日の親密さを予測・事実より感情の開示が効く)
- LLM社会シムの検証が中心課題: 10.1007/s10462-025-11412-6 / arXiv:2603.00113
