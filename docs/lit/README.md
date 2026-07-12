# 文献コーパス(docs/lit/)

> 各論文の**エッセンス抽出メモ**を1論文1ファイルで蓄積する場所。数百本にスケールする設計。
> 索引・リンクは [../references.md](../references.md)、設計正典は [../design.md](../design.md)、スコープは [../research-scope.md](../research-scope.md)。

## Funnel(各分野で回す)
1. **サーベイ/レビュー + 被引用アンカー**で分野の"数百本"を覆う
2. **ランドスケープ地図化**(系統・対立・合意・未解決)
3. **エッセンス抽出** → 本フォルダに1論文1メモ
4. **load-bearing な数本を精読**
5. **seam へ反映**(design.md / research-scope.md を更新)
> 規律:**参照は多く、実装は少なく**。論文の結論を直接実装しない(seam/機構として)。

## メモのテンプレート
```
# <著者 年> — <タイトル>
- リンク: <検証済みURL>  | 分野: <field> | 重要度: P0/P1/P2
- 主張(claim): 
- 機構(mechanism): 
- 効く seam: 
- "結論でなく seam として"の入れ方: 
- コスト/スケール含意: 
- 批判・限界: 
- 関連: [[...]]
```

## ファイル命名
`<field>__<著者年>_<短縮タイトル>.md`(例: `mas__yang2024_oasis.md`)

## 分野別インデックス(deep-dive の進捗)
### 1. MAS / LLMエージェント・シミュレーション & FW  ✅ 一巡完了(build-vs-reuse=hybrid 暫定)
- [[mas__survey2024_llm-abm-survey]] — 分野サーベイ。標準アーキ / スケール効率は未解決問題(=我々の空白)
- [[mas__yang2024_oasis]] — 100万体SNSシミュ。実測コスト + 流用可能なスケール・インフラ様式
- [[mas__concordia2023_deepmind]] — 認知最良(GM+component+非最大化)だがスケール非対応
- [[mas__agentscope2024_largescale]] — スケール最良(actor並列+vLLM多モデル)だが認知薄い
- **結論**: 単一FWで認知×規模は両立不能 → hybrid(借用)。詳細は research-scope「エンジン構築方針」

### 2. 性格・動機づけ心理学(factors)  ✅ 一巡完了
- [[factors__personality-motivation-overview]] — trait/state 分離、Bandura4源泉=更新則入力、proactive personality=事後測定(指紋回避)

### 3. state 更新則(Bandura4源泉 / SIMCA / Morrison&Phelps)= OPEN#2  ✅ 一巡完了
- [[state-update__open2-overview]] — 因果構造のみ / ★ k = フィードバックゲインの接地(k* の意味づけ)

### 4. 文化進化・社会言語学(ラベル創発 / semantic drift)  ✅ 一巡完了
- [[labeling__cultural-evolution-overview]] — naming game / Ashery(集団バイアス創発)/ Centola(tipping ~25%)。drift=創発→観測

### 5. ネットワーク科学・拡散理論(complex contagion / 閾値)  ✅ 一巡完了
- [[network__diffusion-overview]] — 運動は complex contagion(複数補強)/ 閾値異質分布 / カスケード2レジーム(相転移的)

### 6. 集合行為・制度経済学(Olson / Ostrom / Snow&Benford)  ✅ 一巡完了
- [[collective-action__institutions-framing-overview]] — フリーライド(大集団で悪化)/ Ostrom 8原則(制度創発)/ フレーミング。**§4 統一チェーン完成**

### 7. 複雑系・相転移(k*)  ✅ 一巡完了
- [[complexity__phase-transition-methodology]] — k*=相転移 / early-warning で検出 / R²の限界→3点で三角測量

### 8. 計測・validation  ✅ 一巡完了
- [[measurement__validation-overview]] — operational validity / LLM-judge circularity / tail過小 / 既知結果で calibration

### 9. LLM/AI を社会エージェントとして  ✅ 一巡完了
- [[llm__agents-validity-model-choice]] — RLHF が世界改変を抑圧・崩壊の原因 / モデル選択=実験変数

---
## 🔄 第2フェーズ:世界2.0 分野群(全30・均等 exhaustive)+ PLATEAU 可視化 — 進行中
### 群①substrate/妥当性  ✅ 一巡完了
- [[urban__lynch1960_image-of-the-city]] — Lynch 5要素。landmark を hardcode せず軌跡から創発・事後測定(計算論版 head/tail 則)。「視空間=社会構造」の核
- [[ontology__searle1995_institutional-facts]] — Searle「X counts as Y in C」status function。制度創発=宣言 verb の affordance。象徴レイヤーの哲学的接地
- [[envpsych__cognitive-maps-affordance-overview]] — Tolman 認知地図(不完全・個体別)+ Gibson affordance = 「行動でなく可能性を与える」設計原則の心理学的接地
- [[ecology__ecosystem-metaphor-overview]] — keystone=世界改変者アナログ / carrying capacity=スケール上限 / resilience=anti-collapse / succession=レジーム遷移
- [[econ__affordance-cluster-overview]] — 両面市場 cold-start=社会化ブートストラップ / critical mass=相転移 / 評判=社会ネット信頼レイヤー / メカニズムデザイン=制度
### 群②engagement  ✅ 一巡完了(⚠️injection 注意分野)
- [[motivation__sdt-flow-overview]] — SDT(自律/有能感/関係性)+ flow。⚠️動機は注入せず充足**可能**な affordance に、発生は創発+観測
- [[behdesign__fogg-nudge-overview]] — Fogg B=MAP(動機×能力×プロンプト)+ nudge。⚠️設計者 nudge を仕込まず、改変者=環境設計者を観測
- [[gamification__extrinsic-reward-overview]] — PBL+過正当化。⚠️★最重要:報酬注入は内発的世界改変を歪める→既定off・実験変数化
- [[behpsych__reinforcement-schedules-overview]] — Skinner 強化スケジュール。variable-ratio=依存機構。結果 affordance のみ・cheap tier 行動則
- [[marketing__diffusion-consumer-overview]] — Rogers 普及。採用者カテゴリ=tail 実証版 / オピニオンリーダー=keystone
- [[bizeco__business-ecosystem-overview]] — Moore/Iansiti keystone orchestrator=世界改変者の組織版(制度・標準に投資)
### 群③build・viz + Part B  ✅ 一巡完了
- [[viz__plateau-pipeline-overview]] — **Part B**: PLATEAU(Unity SDK / Web Cesium 3D Tiles 両経路)+ **sim⇄viz 疎結合 I/F 定義**(LLM推論と描画を分離)。渋谷=商用可・無料
- [[engine__distributed-actor-overview]] — actor model / event-driven / PDES。スケール中核 + ★非決定性 vs 多seed再現の決定化 seam
- [[gamedesign__emergent-systemic-overview]] — MDA / emergent gameplay = **no-fingerprint 原則の設計工学版**(Mechanics=affordance のみ設計)。HCI/サービスデザイン同族
### 群④哲学  ✅ 一巡完了
- [[value__axiology-overview]] — 内在/道具的価値・関係説。★価値は関係から創発=新価値樹立=世界改変
- [[systems__gst-overview]] — GST(Bertalanffy)。★★equifinality=k*問いのGST版 / feedback=k / autopoiesis=anti-collapse。プロジェクト全体のメタ枠組み

---
## 🔧 第3フェーズ: インフラ検証(Gemini 要約 fact-check、Opus 4.8 委譲)✅ 完了
- [[infra__gemini-summary-verification]] — 判定表(✅⚠️❌)。★FP8 は A5000 で不可→4bit / APC「多様性」理由は誤り / **N=90-480 decision/step 上限 → LOD 必須が数字で確定**
- [[infra__model-choice-conflict]] — instruct 確定 vs 分野9 の衝突。base 版未公開 → 対照=同系列 abliterated(Heretic 手法優先)。model×k 実験変数化
- [[infra__agentic-memory-reflection]] — pull vs push ハイブリッド + ★★**ソロ内省の頻度・深さ・接地強度 = k の operational 実装部位**(ID-RAG 直系)
- [[infra__storage-routing]] — OPEN#5 判断材料(Redis+pgvector+NetworkX 推奨)/ agent-ID sticky routing(prefix ~96%)/ 個別睡眠=負荷平準化

## 🔍 第4フェーズ: ギャップ埋め+総点検(Opus 4.8 委譲)✅ 完了
- [[method__experiment-design-statistics]] — DOE(2段階掃引・CV収束seed)/ **k*主推定=FSS(N 3水準)** / PELT+bootstrap / judge κ≥0.7 / Hydra+MLflow+DVC / **応答キャッシュ=再現性の要**
- [[world__mobility-shibuya-scenario]] — **EPR+visitation law=cheap 移動則**(skmob 参照実装)/ POI グラフ+リンクキュー(メソ)/ 渋谷データ表 / **Epstein grievance 範型+摂動カタログ**
- [[agents__persona-language-safety-opinion]] — IPF×LLM 2段ペルソナ+Verbalized Sampling / **言語選択=第一級交絡(日/英 ablation 要)** / Prompt Infection 防御+「操作量」=改変者指標 / cheap 意見則=Friedkin-Johnsen
- [[../risk-register]] — ★★ **red-team 監査(R1-R19)**: k の compute 交絡(sham/null 対照必須)/ tail×均質化 → **被説明変数の連続量化** / B段 go/no-go ゲート / ゴール再設定(k*確定→測定器+兆候)/ boundary 論文の先回り武装

## ✅✅ 第2フェーズ(世界2.0 全30分野・均等 exhaustive + PLATEAU 両経路)一巡完了。

---
## ✅ リサーチ funnel(分野1-9)一巡完了。

## その他メモ
- [[mas__li2026_moltbook]] — Moltbook(規模だけでは社会化しない。5指標を観測層に流用)
