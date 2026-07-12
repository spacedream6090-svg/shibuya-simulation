# ペルソナ生成・言語選択・エージェント間安全・意見ダイナミクス — 第4フェーズ課題3(Opus 委譲 2026-07-02)
- 分野: config(OPEN#3), factors, llm, propagation, observer | 重要度: P0

## A. 大規模合成ペルソナ生成
- 2系統の合成: **IPF(国勢調査ベース合成人口)で属性骨格** × **LLM で文章化**。e-Stat 令和2年国勢調査に渋谷区(13113)の年齢各歳・昼間人口(来街者=昼夜差分)あり → 「年齢×職業×居住/来街」骨格を作れる。
- ★ **mode collapse が最大の敵**(RLHF typicality bias で tail が消える=世界改変者=tail に致命的)。対策: **Verbalized Sampling**(N個+確率を出させる、多様性1.6-2.1倍、training-free)+ **embedding 分散の定量監視**。
- ★ **心理尺度→文章変換の注意**: (1) trait 値は「行動命令」でなく**価値観・傾向のニュアンス**として控えめに翻訳(指紋回避)、(2) **注入用と評価用の尺度を分離**(同一質問紙は妥当性汚染)、(3) LLM は人間の5因子構造を再現しない(測定モデル不成立)+ 自己申告と行動が乖離する報告 → 行動ベース測定([[measurement__validation-overview]] と整合)。
- 先行: PersonaHub(10億、ただし人手より多様性低)/ Stanford 1052人(実インタビュー注入)/ 多様性最大化 Persona Generators(2026)。

## B. 言語選択(日本語 vs 英語)— ★未決定の第一級交絡
- **Qwen3 系は日<英**(Swallow 32B: 日0.609 vs 英0.792)。素の Qwen3.6-27B の日本語ベンチは未確認(Nejumi 直参照要)。Ricoh が Qwen3.6-27B 日本語強化版を公開(2026/6)→ 有力候補。
- **言語=文化価値観のスイッチ**だが方向はモデル依存で不定(Claude は母語で集団主義化、Gemini は逆)。「日本語=集団主義バイアス」とは断定できない。
- **トークン効率: 日本語は英語比 約2-3倍** → スループット・実効 context・コスト直撃(N 上限 90-480/step がさらに下がる)。
- 判断材料表(要ユーザー決定): 日本語全処理=リアリズム高/性能・効率低 // 英語全処理=効率高/文化平板化 // **ハイブリッド(思考=英語・発話=日本語)=中間だが翻訳段が新交絡+実装複雑**。→ **同一 seed で日/英 ablation を1回入れる価値大**。

## C. エージェント間 prompt injection・シミュ内安全
- ★ **Prompt Infection は実証済み**(LLM-to-LLM で自己複製・伝播、GPT-4系で有害行動成功率>80%、1体→全網汚染)。敵対1体で討論精度10-40%低下・誤答合意+30%。
- **二面性が本研究の武器**: 悪性 injection と正当な説得は「透明性/対象の利益」軸で区別できる → **「他者の認知を操作した量」を世界改変者指標に**(observer で誰が誰の意見をどれだけ動かしたか計測)。
- 防御標準: **発話は必ず user 層・structured field に格納し system と厳格分離** / JSON 通信+privilege 分離 / sanitize / defense-in-depth。→ engine の通信設計に必須 seam。

## D. 意見ダイナミクス形式モデル(cheap tier の意見更新則)
- ★ **Friedkin-Johnsen(初期意見 anchor 付き重み付き平均)が LLM 挙動と最も一致**と複数報告 → cheap tier の第一候補。bounded confidence(HK/Deffuant)は分極再現に(confirmation bias を明示変数化)。
- LLM 固有の逸脱: **凸包破れ**(意見が既存意見の凸包外へ=線形モデルで捉えられない)/ **合意過収束**(事実バイアス+sycophancy で分極が消える)/ conformity は多数派サイズで sigmoid 増(モデル依存: Llama3-70B は多数派6→3で69.9%→32.6%)。
- ★ **LOD 設計への帰結: tail エージェントは形式近似せず LLM tier に残す**(FJ 近似は tail の異質性を消す)。anchor 強度・BC 閾値は LLM tier の実測で較正。

## 出典(検証済み)
[Verbalized Sampling(arXiv 2510.01171)](https://arxiv.org/abs/2510.01171) / [PersonaHub(GitHub)](https://github.com/tencent-ailab/persona-hub) / [LLM 性格検査の妥当性批判(arXiv 2311.05297)](https://arxiv.org/abs/2311.05297) / [psychometric framework(Nature MI)](https://www.nature.com/articles/s42256-025-01115-6) / [e-Stat 昼間人口](https://www.e-stat.go.jp/stat-search/database?query=%E6%98%BC%E9%96%93%E4%BA%BA%E5%8F%A3&layout=dataset&statdisp_id=0003179188) / [Qwen3 Swallow](https://swallow-llm.github.io/qwen3-swallow.en.html) / [Ricoh Qwen3.6-27B 日本語版](https://jp.ricoh.com/release/2026/0605_1) / [文化価値観の言語差(arXiv 2604.22153)](https://arxiv.org/abs/2604.22153) / [Prompt Infection(arXiv 2410.07283)](https://arxiv.org/abs/2410.07283) / [敵対的説得(Nature Sci Rep)](https://www.nature.com/articles/s41598-026-42705-7) / [LLM×意見ダイナミクス(NAACL 2024)](https://aclanthology.org/2024.findings-naacl.211/) / [LLM conformity(arXiv 2501.13381)](https://arxiv.org/abs/2501.13381)

## 関連
[[llm__agents-validity-model-choice]](RLHF tail 潰しの生成段版)/ [[measurement__validation-overview]](尺度分離)/ [[factors__personality-motivation-overview]](OPEN#1/#3 の実装法)/ [[network__diffusion-overview]](FJ=cheap 伝播)/ [[infra__model-choice-conflict]](言語×モデルの交絡)/ [[risk-register]]
