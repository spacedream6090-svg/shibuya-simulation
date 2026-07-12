# 内省しやすさの時間変化 — 馴化/鋭敏化・練習効果・努力コスト・好奇心・EVC(R1調査、2026-07-06)

> フル調査・設計反映: [../research/reflection-drift.md](../research/reflection-drift.md)。
> 用途: drive.py の**発火閾値ドリフト**(step 進行で内省が起きやすく/にくくなる)の学術接地。
> 既存の [cognition__drive-firing-memory.md](./cognition__drive-firing-memory.md)(MicroPsi selection threshold のヒステリシス・EVC)の**時間発展版**。

## 主張(claim)
発火閾値は固定でよいという前提を外し、**経験の履歴で緩やかに動く**(馴化=上昇/鋭敏化=下降)と、
心理学・神経科学の複数系列が一致して支持する。ドリフトの向き・速さは個体差(traits)由来にできる。

## 機構(mechanism)— 5 系列
1. **馴化/鋭敏化(Rankin et al. 2009, Neurobiol. Learn. Mem.)**: 非連合学習の 10 特性を再定義。
   - 反復・単調な刺激 → 応答減衰(馴化)。**頻度依存**(高頻度刺激ほど速く・深く馴化)。
   - **刺激特異性**(馴化は刺激の種類に固有)。**自発的回復**(刺激を止めると時間経過で応答が戻る)。
   - **脱馴化**(新奇/強刺激で一時的に応答回復)。強刺激の反復は逆に**鋭敏化**(応答増大)。
   → 発火ゲージ機構に直訳: 単調な低顕著イベント(沈黙・SNS・同席)= 馴化 = 閾値↑。
     新奇/強イベント(初訪問・未知語・大 |Δstate|)= 鋭敏化 = 閾値↓。刺激休止で閾値は base へ回復。
2. **メタ認知の練習効果 = "reflection begets reflection"(教育心理の一致所見)**: 構造化された
   反復・自己評価で reflective thinking は向上する(明示的訓練で学習効果が増す)。
   → **発火(=内省)経験そのものが次の発火を促す**使用依存的促通 = 鋭敏化項の第2の根拠。
   入力は「発火回数」= k 非依存量。
3. **精神的努力の機会費用(Kurzban et al. 2013, BBS)**: 努力感 = 実行系の**機会費用**の主観出力。
   競合タスクが多いほど当該タスクへの配分は下がる。→ 混雑・多イベントで competing demand が高い局面は
   実効閾値↑(考え込みにくい)方向のゲート。資源枯渇説ではなくコスト・ベネフィット説。
4. **好奇心=情報ギャップ(Loewenstein 1994, Psych. Bull. 116(1):75-98)**: 好奇心は飢餓様のドライブ。
   **少量の priming 情報で急上昇→十分な情報摂取で満腹(satiation)**。→ 未知語イベントは閾値を一時的に
   下げるが、露出が続くと満腹して馴化する(2 の一時性・自発回復と整合)。
5. **EVC の適応的強度(Shenhav et al. 2013, Neuron)**: 制御配分は期待報酬×効力÷努力コストで決まり、
   **強度は時々刻々調整される**(dACC が監視)。既存メモの EVC を「時間発展する θ」に拡張する規範形。
   ⚠️ 効力(efficacy)は state だが、**k は efficacy を動かさない**(k は belief 書き戻しのみゲート)ので
   efficacy 自体は k 非依存。ただし安全側では θ ドリフトの入力を**発火・出来事カウントに限定**するのが
   証明が簡単(下記 R1 制約)。

## 効く seam
`cognition/drive.py`: 各エージェントに緩変数 `theta_drift`(既定 0)を持たせ、`step_tick`/`on_fire`/`on_reject`
で更新。実効閾値 = clip(base_threshold + theta_drift, [0.30, 0.85])。
向き・速さは `factors/registry.drift_params(traits, rng)`(no-fingerprint)で写像。

## "結論でなく seam として"の入れ方
- 論文の数値は固定実装しない。**因果構造だけ**を drive.py に、**magnitude は conf.drive.drift** に(既定 OFF=現行 fixed と完全同一)。
- 分布形は既存方針どおり TruncatedNormal/LogNormal(σ/μ≈0.2-0.4)。

## R1 制約(最重要・計算量交絡の再発防止)
- **ドリフトの入力に belief 書き戻しの成否/量(Y_internal)を絶対に使わない**。
- 使ってよいのは drive.py が既に見ている量のみ = **発火回数・棄却回数・出来事ゲージ入力**(すべて k 非依存)。
- drive.py は beliefs を参照しないので、この規律を守れば θ ドリフトのループ全体が k 非依存に保たれ、
  発火数の k 間同一性(±20%)が壊れない。監査: L2 に `mean_theta_drift` を追加し、k∈{free,off} で n_fires を再確認。

## コスト/スケール含意
- 計算量ゼロ増(緩変数 1 個・毎 step O(1) 更新)。記憶ゼロ増(float 1 個/agent)。LLM 呼数不変。
- 100 日ランでも安全。むしろ「100 日で全員の内省頻度が単調収束して均質化」する崩壊を θ の自発回復で緩和できる副次利得。

## 批判・限界
- Rankin の特性は反射・単純応答系の知見で、LLM 内省への外挿は隠喩。→ 現象論モデルとして扱い、感度分析必須。
- 4 と 5 は state(efficacy)を経由すると k と結合しうる → **入力を出来事・発火カウントに限定**して回避(上記制約)。
- 個体差の向き(sensitizer/habituator)を traits にどう割るかは仮説 → traits→drift の写像は RQ 検収対象。

## 関連
[[cognition__drive-firing-memory]](閾値・ヒステリシス・EVC の静的版)/ [[behpsych__reinforcement-schedules-overview]](強化スケジュール=別系列の使用依存変化)/ [[factors__personality-motivation-overview]](trait→個体差写像)/ [[../risk-register]](R1 計算量交絡)

## 出典(検証済み URL)
- Rankin et al. 2009 "Habituation revisited": https://pmc.ncbi.nlm.nih.gov/articles/PMC2754195/ / https://pubmed.ncbi.nlm.nih.gov/18854219/
- Kurzban et al. 2013 "An opportunity cost model of subjective effort and task performance", BBS: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3856320/
- Loewenstein 1994 "The psychology of curiosity", Psychological Bulletin 116(1):75-98(情報ギャップ理論): https://www.cmu.edu/dietrich/sds/docs/golman/golman_loewenstein_curiosity.pdf(Golman&Loewenstein の解説)/ 原著 Psychol. Bull. 116(1)
- Shenhav et al. 2013 "The Expected Value of Control", Neuron: https://www.shenhavlab.org/s/Neuron-2013-Shenhav.pdf / https://www.cell.com/neuron/fulltext/S0896-6273(13)00607-7
- EVC 効力拡張(Frömer/Shenhav 2021, Nat. Commun.): https://www.nature.com/articles/s41467-021-21315-z
