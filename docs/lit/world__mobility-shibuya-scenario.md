# 人流モビリティ・渋谷データ・シナリオ設計 — 第4フェーズ課題2(Opus 委譲 2026-07-02)
- 分野: world/spatial, config, scenario, observer | 重要度: P0(物理層の実体)

## A. cheap tier の移動モデル(経験則で接地)
- ★ **EPR(exploration and preferential return, Song 2010)が中核**: 確率 ρS^(-γ) で新規 POI 探索、それ以外は訪問頻度比例で回帰。+ ジャンプ長 truncated power-law(Gonzalez 2008, β≈1.75)+ **universal visitation law**(Schläpfer 2021: 訪問者数∝(頻度×距離)^(-2))を POI 選択の事前分布に。radiation model(パラメータフリー)で OD フロー初期化。
- **参照実装: scikit-mobility**(EPR/density-EPR/STS-EPR/radiation/gravity 全部ある。ゼロから書かない)。
- **空間表現は POI グラフ**(ノード=POI/建物、エッジ=徒歩リンク)が正解。10分=1リンク移動 or 1滞在。グリッドも道路ネットワークも過剰。

## B. 群衆物理は「メソスコピック」で十分
- Social Force / CA(秒スケール・衝突回避)は**不要**(社会現象が主目的)。**POI グラフ+リンク容量/キュー**で混雑を表現 → **混雑=キュー遅延が grievance 源として社会層に自然接続**。微視モデルはスクランブル交差点演出等の最上位 LOD オプションに温存。
- activity scheduling は MATSim 流「各エージェントが日次活動計画を持ち評価で更新」を軽量借用。

## C. 渋谷・日本の利用可能データ(所在・ライセンス確認済み、DL 未実施)
| データ | 提供元 | ライセンス | 粒度 | 用途 |
|---|---|---|---|---|
| 全国人流オープンデータ | 国交省/G空間 | 無償 | 1kmメッシュ・月次 | 大枠 calibration |
| モバイル空間統計 | ドコモ | **有償**(研究申請可) | 125-500m・時間帯別 | 細粒度(必要時) |
| OSM(渋谷 POI/道路) | OSMF | ODbL(商用可・帰属) | POI点・道路網 | **POI グラフの主構築源** |
| 国土数値情報(P33集客施設等) | 国交省 | 政府標準規約(商用可) | 施設点・面 | POI 種別補強 |
| PLATEAU 建物用途コード | 国交省 | オープン | 建物単位+用途+高さ | POI グラフ+高さ層 |
| 渋谷区オープンデータ | 渋谷区 | オープン | 行政系 | 補助 |
- ⚠️ スクランブル交差点通行量(俗説: 平日26万/休日39万人/日)は**一次未確認** → 使うなら渋谷区「渋谷駅周辺地域交通戦略」PDF 原本で確定。

## D. シナリオ・ショック(grievance 源)の設計方法論
- ★ **Epstein 2002 civil violence が範型**: grievance = hardship × (1−legitimacy)、閾値超過で行動化(Mesa に参照実装)。最小機構として cheap tier に採用可。
- **no-fingerprint の注入法**: ショックは**世界側 affordance の変化のみ**(資源希少化・施設閉鎖・ルール変更・価格上昇・空間アクセス制限)。意味づけ・命名・運動化はエージェントに委ねる。
- **摂動実験の作法**: 無摂動ベースライン必須 + 種類×時点×強度を独立に振る + 複数 seed + 創発指標を事前定義。
- **渋谷の現実接地シナリオ(抽象化して使う)**: ①宮下公園再開発型(公共空間の私企業的再編・排除→抗議。行政代執行・高裁賠償命令の実史)②夜間路上飲酒禁止条例型(2024年10月施行、公共空間の利用制限 vs 反発)。→ **摂動カタログ化**。⚠️red-team 指摘: 実在イシューの名指しは対外リスク → **架空・抽象化**して使用([[risk-register]])。

## 出典(検証済み)
[Gonzalez 2008(Nature)](https://www.nature.com/articles/nature06958) / [Schläpfer 2021 visitation law(Nature)](https://www.nature.com/articles/s41586-021-03480-9) / [scikit-mobility docs](https://scikit-mobility.github.io/scikit-mobility/reference/models.html) / [density-EPR(arXiv 1607.05952)](https://arxiv.org/abs/1607.05952) / [Epstein 2002(PNAS)](https://www.pnas.org/doi/10.1073/pnas.092080199) / [Mesa Epstein 実装](https://mesa.readthedocs.io/stable/examples/advanced/epstein_civil_violence.html) / [MATSim(OAPEN)](https://library.oapen.org/bitstream/id/859157dd-5478-4089-9fca-b3df7a7a39d4/613715.pdf) / [国土数値情報](https://nlftp.mlit.go.jp/ksj/) / [G空間 人流データ](https://www.geospatial.jp/ckan/dataset/mlit-1km-fromto) / [渋谷区条例改正(公式)](https://www.city.shibuya.tokyo.jp/kusei/shisaku/jorei-toshin/sbykankyo.html)

## 関連
[[urban__lynch1960_image-of-the-city]](POI グラフ=path/node の器)/ [[envpsych__cognitive-maps-affordance-overview]](EPR=認知地図の cheap 近似)/ [[state-update__open2-overview]](Epstein grievance=SIMCA の cheap 版)/ [[collective-action__institutions-framing-overview]] / [[risk-register]]
