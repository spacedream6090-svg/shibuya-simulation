# エージェント実装の全体まとめ(3観点)— 2026-07-07 第9バッチ

ユーザー要望「LOD・ツール(実験の前提)/ 社会的実装(関係・環境影響)/ 推論回数を変化させる機構、
の3観点でエージェント自体の実装をまとめる」への回答。Fable 5 が中核コードを直接精読して作成
(対象: agents/agent.py, cognition/{lod,drive,reflection,deliberate,routine,planning}.py,
factors/{registry,update,affect,mood,psych}.py, engine/scheduler.py, tools.py, rules.py,
relations.py, opinion.py, recursion.py, conf/config.yaml)。

---

## 0. エージェントの解剖図(前提)

`Agent`(agents/agent.py)は**状態の容器**であり、行動ロジックは cognition/、更新則は factors/ に
分離されている(no-fingerprint 契約の物理的な形)。状態は4系統:

| 系統 | 中身 | 誰が読む/書く |
|---|---|---|
| 生まれつき(traits) | nfc・risk_tolerance・internal_locus(D5 最小セット) | **factors/ だけが名前を知る**。他層は写像後の不透明な数値のみ |
| 経験で動く(states) | efficacy 0.5 / grievance 0.1 / ownership 0.1 初期値 | factors/update.py の `_bump` 経由のみ(全変更が state_update イベントに記録=因果分解可能) |
| 内部 transient | drive(欲求ゲージ)・arousal(覚醒)・fatigue(疲労)・theta_drift(閾値ドリフト)・opinion(FJ意見) | R²(k) の監査集合(states)に入れない=結果変数を汚さない |
| 生活・物理 | 位置(node/建物/階)・家・職場・金(現金/口座)・スケジュール帳・記憶(3層 MemoryStore)・関係台帳 | engine が客観量として扱う |

**k の作用点は1点のみ**: 内省(reflection)の結論 `belief` を `agent.beliefs` に書き戻すか
(free/degraded/sham/off)。beliefs は次の発火プロンプトに「あなたの考え」として注入される
=経験→内部状態→行動の結合をここだけで実験的に開閉する。

---

## 1. LOD・ツール(実験の前提となる実装)

### LOD(cognition/lod.py)
- 現在の LOD は**予算のみ**: `LodBudget(max_per_step=300)` が 1step の LLM 発火数上限。
  かつての「驚きトリガー」は欲求駆動発火(下記 §3)に移行済みで、LOD は k 条件間で共通の
  インフラ上限として振る舞う(R1: 予算は k と無関係に消費される)。
- 本番スケール(1万体〜)では、この予算がそのまま「1step に考える人数」の物理上限になる。
  発火要求が予算を超えた分は**ゲージ維持で翌 step へ持ち越し**(取りこぼしではなく遅延)。

### ツール=世界を変える affordance(tools.py、5種+標準装備)
- 4軸を最小で覆う: モノ=open_venture(出店・売上)/ 制度=propose(署名→成立→**制度DSL の
  実効ルール自動制定**)/ 人=host_event(勉強会=複雑感染の閾値2を1回で満たす教育帯域)/
  虚構=found_group・post_flyer(共通インフラ)。
- **制度DSL(rules.py)**: 成立提案の機械可読 rule を検証し実効化。型はホワイトリスト
  fee(価格±)/bonus(行動に支給)/curfew(時間帯×カテゴリの行き先抑制)/prohibit(禁止
  =警察執行の対象)/weekly_event(定期イベント)+ **repeal(既存ルールの廃止。第9バッチ
  再帰性で追加・既定 OFF)**。検証失敗は「文言だけの制度」に降格=壊れない。
- 提示は**中立**(offer_text / equip_all の所持ツール節)。可否条件は所持金など客観量のみ
  (R1: k 非依存)。効果は客観カウント(参加人数・署名数・売上=R4。LLM 審判なし)。
- 制度改変の3ルート(G3): 労働争議(propose の職域 variant・同僚に賛同が偏る)/
  投票(署名でなく決定論投票で可決)/ 執行(prohibit 下で警察官が罰金+不満)。
- **再帰性(第9バッチ・本バッチで実装)**: (1)いま実効の取り決めをプロンプトで知覚
  (norm_line)、(2)昨日の街の動き=提案/成立/廃止/取り締まりの客観カウントを知覚
  (digest_line)、(3)repeal 提案で廃止=**監視→知覚→不服→改変の閉ループが一周**、
  (4)執行多発ルールの日次ニュース化(社会の自己観測)。

### 実験プロトコルの前提装置
- 対照(controls.mode): compute_matched(off でも内省 LLM を実行し全破棄=4条件の計算量を
  完全一致)/ null_series(発火ごとに内容非結合ダミー呼び出しを固定本数)。
- ペルソナ: 名簿(personas_file)を**全 k 条件で共有**、icebreak(初期関係)も同一ファイル
  =初期条件の交絡を排除。traits の tail 確保(D6: 10% で上位 tail を明示サンプル)。
- 条件行列: **パラメータ宣言方式**(第9バッチ決定)。conf/experiments/*.yaml に条件×シードを
  宣言し scripts/run_experiment.py が直列実行(条件は各ランの config スナップショットに完全記録)。

## 2. 社会的実装(関係の質・環境からの影響の受け方)

### 影響の入口(全て「出来事→factors 経由→states」の一方向)
factors/update.py が唯一の書き手。主な流入(magnitude は conf の factors で調律):
- **対人**: 聞いた発話の感情価(ネガ→grievance+ / ポジ→grievance−・efficacy+)、聞き手の
  有無(being_heard/ignored→efficacy±)、他者の成功の目撃(vicarious)、自分の造語の被採用
  (own_adopted→ownership+ efficacy+=当事者化)。
- **環境**: 混雑(congestion)、公園(回復環境)、天気(雨の不快)、災害・遅延・停電、
  犯罪被害・迷惑行為、品切れ・行列、執行(罰金)、炎上(misinfo)。
- **経済**: 金銭逼迫(1日1回)、**相対的剥奪(G1)**=街に居る他者の所持金中央値を下回る量
  →不満(個体の相対的地位で grievance に個体差が復活=飽和対策の主役)、失業の生活不安。
- **受けやすさの個体差**は factors が traits から事前写像した不透明倍率で表現:
  needs_mods(5次元価値プロファイル→出来事感度)、drive_mods(SDT 内発/外発)、
  opinion_susceptibility(FJ の s)。engine は倍率の意味を知らない。

### 関係の質(relations.py G2 + household H2)
- 関係台帳: 接触回数 count(常時)+ **closeness weight**(G2 ON 時。ポジ交流+1/ネガ−2/
  不在日−1)→ tier(知人2/友人5/親友12)を決定論導出しプロンプトに「○○とは友人」。
  断絶(relation_break)・評判(rep: 被採用+1.0・被傾聴+0.2・日次風化−0.5、閾値3で
  「街で名が知られている」行)・派閥(同グループ=「同じ仲間」)。
- 世帯・恋愛(H2): 起動時に世帯グループ化(home 共有=夜間の家庭内 co-location)、相互
  closeness≥15 で恋人成立(デート先の共有=移動理由)。
- **重要な設計判断**: tier/評判は efficacy/grievance に**結合しない**(独立の観測スコア+
  プロンプト文脈)。結合すると call-count 不変が壊れるため G2 で意図的に見送り(保留中の
  ユーザー判断事項)。

### 環境→行動の経路(プロンプト文脈 vs 物理)
- **文脈注入(呼数不変)**: 日付・天気・予定・行事・災害・間柄・評判・世帯・観光/多言語・
  感情ラベル・長期目標・趣味・制度(Searle)・実効ルール+街の動き(再帰性)…全て
  「None なら1行も足さない」ゲート付きで build_prompt に注入。
- **物理(co-location を変える)**: 群集(ハロウィン)、失業、病気の在宅、災害の在宅・運休、
  観光回遊、閉店、趣味の行き先バイアス、宿泊(実装中)。これらは FixedLLM で ON≠OFF に
  なるのが必然だが、**k・内面状態を読まない**ため compute_matched 下で k 不変(各波に回帰テスト)。
- 意見(FJ opinion.py): 対面 w=0.20 / DM 0.15 / SNS 0.08 で聞いた文の感情価に意見が寄り、
  anchor(初期意見)へ (1−s) で引き戻される。プロンプト非注入=純粋な観測層+投票の決定論判定に使用。

## 3. 推論回数(LLM 発火)を変化させる機構

**発火パイプライン**(_phase_drive → _decide → _llm_speak):
```
出来事 → drive.add(reason, 倍率)          ← 個体差: needs_mods × drive_mods(乗算)
  ゲージ ≥ 実効閾値 で「申請」            ← 実効閾値 = clip(drive_threshold + Σdelta, 0.30, 0.85)
  申請 → 対面同席なら確定発火 /            ← delta の源(全て既定0=恒等):
         それ以外は fire_weight で抽選         E2 ドリフト theta_drift(馴化+/鋭敏化−/回復)
  抽選成功 → LodBudget.take()(上限300/step)     affect 逆U字 4a(1−a)(Yerkes-Dodson)
  不発 → ゲージ 30% 減衰して再蓄積               fatigue(高疲労→閾値↑=休息へ)
  発火 → ゲージ×0.2 + 不応期3step
```
- **閾値・重みの個体差**(factors/registry.drive_params): NFC 高→閾値低(考え事が起動しやすい)、
  内的統制高→fire_weight 高(思考を行動に移す重み)。閾値分布は normal/lognormal を seam で切替可。
- **発火の関数形** seam: fixed(既定=閾値ゲート+重み抽選)/ logistic(p=σ(slope·(drive−θ)))。
- **返答保証**: 話しかけられたら抽選なしで必ず返答(conv_max_turns=3 で無限連鎖抑制)。
- **内省(k の本体)**: 就寝直後に1回(個別時刻=自然に時間分散)。agentic_pull ON なら固定2段
  (recall+本内省=常に+1呼)。呼数はいずれも writeback 条件と無関係(R1)。
- **監査可能性**: 全申請が drive_request イベント(drive/threshold/lottery/granted/reason)に
  記録され、L2 で k 条件間の呼数一致を事後検証できる。null_series/compute_matched で計算量を統制。

### R1 検証の型(確立済みドクトリン)
1. 内容注入のみの機構 → FixedLLM で ON==OFF(呼数完全一致)。
2. 物理位置を変える機構 → compute_matched 下で k=free と k=off の呼数完全一致
   (機構が k・内面状態を読まないことの operational な証明)。各波に regression テストあり。

---

## 4. 残された設計上の開き(ユーザー判断待ち/今後)
- grievance/評判→発火(fire_weight)への結合: 理論的には自然だが呼数の k 不変を壊すため未結合。
  結合するなら「compute_matched 必須」の設計変更が要る。
- 状態飽和(efficacy 天井)対策: G1 相対的剥奪+affect で部分対応済みだが、efficacy の負の源が
  少ない構造非対称は残る(sim-improvement-analysis.md P1)。
- LOD の質的階層(遠方エージェントの簡略推論など)は未実装(現在は予算=量の LOD のみ)。
  本番 1万体では周辺人口の firing を needs/routine に委ねる現行設計で足りる見込み。
