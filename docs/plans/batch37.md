# 第37バッチ計画(2026-07-19)— 6トラック: ビューア/忠実化/経済/記憶/ツール/観測

体制 = Fable計画・検収 / Opus実行。設計原則 = **自然界のような仕組み**(トップダウン制度注入より
ボトムアップ創発の素地・[[nature-like-systems]])+R1(新機能=新stream・既定OFF・ゴールデン維持)。
追加研究目標 = **組織の自然形成+ファウンダー成立条件の観察**。

監査済み一次資料: [traffic-signals-audit](../research/traffic-signals-audit.md) /
[council-vs-reality](../research/council-vs-reality.md) /
[conversation-pipeline](../research/conversation-pipeline.md) /
[off-features-inventory](../research/off-features-inventory.md)

## Track V: ビューア強化(viz下流のみ・シミュ無風)

- **V1 ライティング+無彩色**: r128にトーンマッピング(ACESFilmic)+sRGB出力・半球光/太陽光の
  再バランス・軽いフォグ。建物色は**既定を無彩色(単一ニュートラル)へ**、分類色はレイヤーパネルの
  トグルで残す(ユーザー要望)。
- **V2 地形起伏**: PLATEAU DEM(2タイル・計833MB)→ 高さグリッド(2m格子・int16量子化)を
  plateau_extract の新stageで抽出 → 地面TINメッシュ+OSM地図テクスチャのドレープ+
  **エージェントy=地表高サンプル**(建物boxのbaseも地表に接地)。
- **V3 駅・地下・橋**: ubld(渋谷駅地下街33MB=スクランブルタイルに実在)→ 半透明の地下構造として
  z<0に描画(地下鉄チューブと整合)。brid(歩道橋8タイル)→ 実形状追加。JR/地下鉄駅舎はbldg内に
  既存(kind=stationの実形状化を確認)。
- **V4 移動手段の可視化**: tracks.jsonのmode(walk/bicycle/car)+taxi(rideイベント)+電車
  (駅経由退出)をエクスポータで判別列化 → ビューアで車=車体グリフ・自転車・タクシー=色分け・
  電車乗車=駅で消える際のアイコン+凡例。2Dビューアにも同配色。
- **V5 統合ハブ**: make_hub.py=タブ型の単一入口HTML(iframe同フォルダ参照=file://可)で
  3D/2D/heatmap/OD/dashboardを統合+ラン要約ヘッダ。

## Track S: シミュ忠実化(全て新stream・既定OFF)

- **S1 選挙制度の現実化**([council-vs-reality](../research/council-vs-reality.md)の提案):
  立候補=自発行為(告示期間・供託金30万円=vote.deposit流用・25歳要件)/ SNTV(全候補から
  効用最大1人)/ 任期4年をprodにも / 議会権限拡張(予算承認・条例議決)/ 住民提案は署名1/50→
  議会審議型。**立候補行動そのものをファウンダー観察のイベントに**。
- **S2 交通**: (a) 本番プロファイルで traffic.mode=od をON(実装済み・信号69基が初結線)
  (b) **SUMO車限定オフライン合成**: netconvert(OSM)→ シミュのゲートウェイOD → duarouter →
  sumo --fcd-output → ビューア車両トラック変換(synth_crowdと同型の「本体無風」パターン)。
  リサーチ→v0実装。(c) 歩行者の信号待ち(横断ノードで決定論的待ち・新stream・OFF)は工数次第。
- **S3 会話強化**([conversation-pipeline](../research/conversation-pipeline.md)の乖離1〜3):
  対話履歴の注入(相手との直近2往復をプロンプトへ)/ 関係加重の返答宛先(最近傍のみ→
  closeness×距離)/ どちらも conf knob・既定OFF。

## Track E: 経済深化(リサーチ→計画→実装・ユーザー事前承認済み)

- **E-R(web深堀り)**: ABM経済の標準設計(EURACE・Delli Gatti系のbank-firm-household回路)・
  LLMエージェント経済(EconAgent等)・日本の決済実態(現金/電子)・家計消費構造(エンゲル係数)。
- **E-W1 銀行**: 預金(利息)・融資(信用スコア=収入履歴+資産・返済スケジュール・破産接続)。
  銀行は「場所」として存在し利用は創発(自然界原則)。
- **E-W2 VC/出資**: venture(freedom.p2 deviance/出店)への出資判定・持分・配当。
  **組織形成+ファウンダー観察の資金経路**。
- **E-W3 消費行動**: 予算制約下の需要(必需/選好/貯蓄率の個体差・needs接続)・商品購入時の決済
  (現金/電子の選択・手数料)。
- 全て economy 配下の新ブロック・既定OFF・test_economy 保護(wage_amount不変)。

## Track M: 記憶の人間化(リサーチ→実装・ユーザー事前承認済み)

- **M-R**: ACT-R宣言記憶(活性化=基底学習Σt^-d+文脈・想起=ノイズ付き閾値→**自然な忘却と
  「思い出せない」が創発**)・Ebbinghaus忘却曲線・干渉理論・Generative Agentsのrecency×
  importance×relevance との比較。
- **M-W**: retrieve() を活性化ベースに拡張(decay・強化=想起で再活性・ノイズ付き閾値で
  想起失敗イベント memory_fail)・「思い出そうとして思い出せない」をプロンプト1行で表現。
  新RNG stream・LLM呼数不変(agentic_pullの固定2段は維持)・既定OFF。

## Track T: 実行時間試算ツール(即実装)

- scripts/estimate_runtime.py: 入力=体数・日数(+モデルプリセット or 実測ラン)。
  较正=既存ランのl1bから日別呼数を抽出し「呼数/日 = f(体数)×(1+g)^day」(会話増加の実測反映)
  をフィット・sec/呼はランのwall時間 or bench値。出力=日別予測表+総所要時間+完走時刻。

## Track A: 組織・ファウンダー観測装置

- founder前駆イベントの統合パネル(venture/deviance/立候補/партnership hub化)+
  形成前履歴(資金・関係数・grievance・opinion極性・k)→ scripts/analyze_founders.py。
  「組織の自然形成」検出=同一場所×反復共在×役割分化のクラスタ検出(既存organizations台帳と対照)。

## 実行順(3ウェーブ)

1. **W1(並列5-6体)**: V1-V5(独立ファイル群)+T+E-R/M-R/SUMO-R(webリサーチ3本)
2. **W2**: S1選挙+S3会話+E-W1/W2(リサーチ結果待ち)
3. **W3**: E-W3+M-W+SUMO v0+A観測+本番プロファイル編成(ON機能はユーザー選定)+全回帰

検収 = 各Wave後 pytest全緑+ゴールデン維持+mockスモーク。実LLM検証はしない(短スモークのみ)。

## OPEN(ユーザー決定)

1. 本番ONにする機能セット(inventory A表から選択)
2. S1選挙現実化の深さ(フル=立候補+SNTV+権限拡張 / ライト=任期・SNTVのみ)
3. SUMOはオフライン合成でよいか(ライブ連成はR1・工数リスク大のため非推奨)
