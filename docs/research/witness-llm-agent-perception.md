# LLMエージェント社会シムの環境知覚の先行(WITリサーチ レーン3)

> 2026-08-20。witness再設計=注意ゲート設計のためのLLMエージェント系調査。

## 1. 結論3行
1. 「重要度スコアで知覚の入口を絞る」先行は**Generative Agentsにも無い**: Park et al.のperceive()は
   **距離順top-k(att_bandwidth=8)**で切り、重要度(poignancy)は取込み後にreflection発火予算にのみ使う。
2. 1万体超は例外なく**チャネル側で候補を絞ってから配る**(OASIS 100万体=RecSys・AgentSociety 1万体=
   MQTT+ソーシャルグラフ・AgentTorch 840万体=archetype単位LLM 1回)。per-agent×per-factの
   スコアリング全走査をする系はゼロ。
3. 注意ゲート導入後は指標が「悪化」して見えるのが正常(Zhou et al. EMNLP 2024: omniscient条件の方が
   LLM成績は良い)。較正アンカー=Park et al.実測「2日で新情報到達32%/52%・招待12名中参加5名」。
   **認知率ほぼ100%は成功でなく壊れている証拠**。

## 2. システム比較(要点)
| システム(規模) | 知覚上限 | 選択基準 | スケール手法 |
|---|---|---|---|
| Generative Agents (25) | att_bandwidth=8/step・retention=8 | **距離のみ**(重要度は取込み後) | 中央配信・総当たり |
| Project Sid/PIANO (500) | Cognitive Controllerがボトルネック | **種別優先度を設計者が制御** | モジュール並列 |
| AgentSociety (10k) | なし | ソーシャルグラフ(関係型+強度) | Ray group+MQTT |
| OASIS (1M) | RecSys推薦件数 | 推薦(interest+hot)=事実上のチャネル | RecSys+Inferencer |
| CitySim (1k-1M) | POI候補top-200・記憶top-5・**社会交流1人/30分tick** | LLM判定(明示的注意なし) | 種別ハードキャップ |
| Lyfe Agents | workmem 4-5 items | **新規性フィルタ**+goal-relevance | 10-100倍低コスト |
| Zhang et al. 2025 (1.5k) | **なし(全件重み付き通過)** | 関係+新規性+履歴+頻度の加算スコア(ATT priority式と同構造) | — |

## 3. 設計上の注意点(失敗パターン)
1. **重要度をintakeゲートに置くのは先行と逆**。二段構え: ①チャネル到達(決定論)で候補生成
   ②注意は「信念化する対象」の選抜のみ。「その時は無価値だが後から効く情報」の永久喪失を防ぐ。
2. **重複除去は複雑接触を殺す**(Centola & Macy: 複数の独立情報源からの反復曝露が必須条件)。
   重複は捨てずexposure_count+distinct_sourcesとして加算。信念強度をその関数に。
3. **指標悪化を事前に較正**: 切替で口コミ到達率・参加率が一斉低下するのは正常(Zhou 2024)。
   Park実測(32%/52%・5/12参加)をアンカーに固定してから切り替える。
4. **社会的注意と環境注意でk予算を食い合わせない**: 高密度渋谷では人がfactを常時押し出す。
   k_social(現行ATT)とk_ambient(環境fact)は**別枠**にする(PIANO CC・CitySimの種別キャップが先行)。
5. **スコア計算自体のO(在場×事象)が残る**: 注意ゲートは「チャネルが配った候補集合の中」でのみ
   働かせる。priority式は加算の決定論スコア(LLM呼びゼロ)に限定。
6. **忘却を対にしないと非対称性は飽和する**(Park: recency_decay=0.995)。exposure decayを必ず対に。

## 4. 「全員が知っている」と消える現象(k*研究の測定対象そのもの)
情報カスケード(Bikhchandani 1992)・複雑接触(Centola & Macy 2007)・ミーム人気の重い裾(Weng 2012)・
可視性減衰による伝播障壁(Hodas & Lerman 2012)・弱い紐帯の優位(Granovetter)・多元的無知と突発革命
(Kuran 1995)・共有知識と協調儀式(Chwe 2001)・噂の変形(Allport & Postman 1947)。
→ **知識台帳(誰がいつ何を知ったか)は副産物でなく主要観測量**。

## 5. 新規性主張が可能な領域(直接の先行なし)
1. 物理環境factへの統合サリエンススコア型top-kゲート
2. 個体差のある知覚容量k_i(GAはatt_bandwidthフィールドはあるが全員8)
3. 会話用の社会的注意モジュールを環境情報ゲートに再利用した先行
4. 認知アーキテクチャ(LIDA/GWT/ACT-R)の注意フィルタの大規模LLM社会シム適用
(LIDA=注意コデレットの連合競争→勝者のみ大域放送はtop-k∧θと同型・ACT-Rのgoalバッファ増幅=目標関連項)

## 6. 主要出典
- Park et al. (2023) Generative Agents, UIST(arXiv:2304.03442・perceive.py実値: vision_r=8タイル・
  att_bandwidth=8・retention=8・importance_trigger_max=150・recency_decay=0.995)
- Zhou, Su, Eisape, Kim & Sap (2024) EMNLP(arXiv:2403.05020・omniscientの誤誘導的成功)
- Zhang, Wu, Hua, Lu & Hu (2025) arXiv:2502.13160(情報非対称下の動的注意・加算スコア)
- Piao et al. (2025) AgentSociety arXiv:2502.08691 / OASIS arXiv:2411.11581 / Bougie & Watanabe (2025)
  CitySim arXiv:2506.21805 / Chopra et al. AgentTorch arXiv:2409.10568 / Altera Project Sid arXiv:2411.00114
- Kaiya et al. (2023) Lyfe Agents arXiv:2310.02172 / Vezhnevets et al. (2023) Concordia arXiv:2312.03664
- Weng et al. (2012) Sci Rep 2:335 / Hodas & Lerman (2012) arXiv:1205.2736 / Centola & Macy (2007) AJS
- Kuran (1995) Private Truths, Public Lies / Chwe (2001) Rational Ritual / Granovetter (1973)
- Franklin et al. LIDA / ACT-R (act-r.psy.cmu.edu) / Sumers et al. (2024) CoALA, TMLR arXiv:2309.02427
