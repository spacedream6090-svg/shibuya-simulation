# 社会シミュレーション基盤モデルの抽出計画(第16バッチ 2026-07-10・計画のみ・実装なし)

体制: Fable計画 → Opusリサーチ(docs/research/framework-architecture.md)→ Fable統合計画(本書)。
ユーザー構想: 「渋谷と切り離した基盤モデル(人格などの本質モジュール)と、特定の場所を再現する
環境モジュールに分類・分離したい。渋谷シム本体は本番検証用に凍結する。」

## リサーチの核心
1. 先行事例(Concordia の Entity-Component/GM、AgentSociety の4層、Mesa-Geo の
   GeoSpace/GeoAgent、Generative Agents の環境ツリー)はいずれも「認知基盤と環境の分離+
   環境の宣言的記述」を採る。本プロジェクトに最も近い到達型は **Concordia 型(基盤=機構、
   環境=差し替え可能なデータ+パラメータ)**。
2. **本コードは既に大部分が分離済み**: 場所固有性は `data/`(地図・ダイヤ・名簿・台帳)と
   `conf/production.yaml`(制度値)に外出しされ、`src/` はほぼ基盤。基盤から data/ への
   直接 import は無く、**config パス束縛(engine/simulation.py)が既にきれいな切断面**。
3. 残る「混在(C)」は少数・行番号レベルで特定済み: プロンプト内「渋谷」直書き
   (cognition/deliberate.py)、駅名フィルタ(world/transit.py)、原点=スクランブル・10/31群集
   (annual.py/routine.py)、media.py の局名、schedule.py、日本の制度既定値
   (economy.py/government.py の最賃・住民税按分・区予算)。

## 設計判断(Fable)
- **物理的なパッケージ分割(別リポジトリ化)は今はしない。** 理由: 渋谷シム凍結の要請と矛盾せず
  最小工数で同じ効果を得る道があるため。まず**論理境界(EnvPack 契約)**を確立し、物理分割は
  「2つ目の環境」を作る時に判断する(その時点で境界の正しさが実証されている)。
- 分離の単位は **EnvPack(環境パック)**: 1つの場所=1ディレクトリ(env/shibuya/ など)に
  manifest(env.yaml)+データ束を集約し、シムは manifest だけを読む。
  - **機構は基盤・値は環境**(例: 最低賃金という機構=基盤、1226円=環境)。
  - **プロンプトの言語=基盤設定(lang)、地名・文化語彙=環境**(lexicon として pack へ)。

## EnvPack manifest(仕様案)
```yaml
env:
  name: shibuya
  locale: ja-JP
  map: map.json              # 地理(道路網・建物・POI・フロア)
  transit: transit.json      # 交通ダイヤ(無ければ徒歩のみの街)
  personas: personas.json    # 名簿(または生成レシピ: 分布パラメータ)
  organizations: orgs.json
  assignments: assignments.json
  institutions:              # 制度パック(機構のパラメータ値)
    min_wage_hourly: 1226
    rent_income_ratio: 0.3
    council: {size: 9, term_days: 1460, deposit: 30000}
    tax: {resident_split: [0.6, 0.4]}
  culture:
    calendar: events.yaml    # 祝日・地域行事(ハロウィン群集など)
    lexicon:                 # プロンプトに出る地名・場面語彙
      place_name: 渋谷
      landmark: スクランブル交差点
  origin: {node: <スクランブルのノードid>}   # 群集・注目の原点
```

## 実装ウェーブ(各ウェーブでゴールデン完全一致を検収条件にする)
| Wave | 内容 | 渋谷シムへの影響 |
|---|---|---|
| **W1** | EnvPack 仕様確定+ env/shibuya/ の組み立て(現 data/ と production.yaml の値を**移すのではなく参照で束ねる**。コード変更なし) | なし(ファイル追加のみ) |
| **W2** | 混在(C)のパラメータ化: 「渋谷」等の直書きを cfg 経由に置換。**既定値=現在のリテラル**=ゴールデン・バイト一致で無傷を証明 | 挙動ゼロ差(テストで保証) |
| **W3** | 制度値の pack 化: economy/government の日本既定値を institutions ブロックから読む(既定=現行値) | 同上 |
| **W4** | EnvPack ローダ: env.yaml → 現行 config キー群への展開(profile と同じ重ね書き機構を再利用)。`--env env/shibuya` で従来と同一ランになることを検収 | 同上 |
| **W5** | **2つ目の環境で実証**: environment-autogen.md の v0 パイプラインで小さな別の街(候補: 下北沢 or 吉祥寺=同じ東京圏でダイヤ・統計が取れる)を生成し、基盤コード無変更で1日スモークが回ることを確認 | なし(別 pack) |
- W2/W3 は各1-2ファイルの小差分に分割し、都度フルガード(ゴールデン+契約)を回す。
- 本番検証(k*実験)は現行 production.yaml のまま実施可能 — EnvPack は並走し、検証が終わった
  タイミングで production を pack 参照に切替える(切替自体も同一ラン検収つき)。

## 基盤(A)として確立するモジュール一覧(=「シミュレーションの本質」)
認知(deliberate/reflection/planning/memory/drive+LOD/theta_drift)・人格(traits/persona機構)・
社会(relations/status/groups/net=SNS/infoenv)・経済機構(wage/accounts/career/ventures)・
制度機構(rules DSL/routes/assembly/enforcement)・因子(factors)・観測(observer/schema/L1-L3)・
エンジン(scheduler/simulation/RngHub)・LLM 抽象(llm/)。
→ これらに場所の知識を**新たに入れない**ことを今後のレビュー規約とする(契約テストの正規表現
ガードに「渋谷」等の地名を基盤ディレクトリで禁止する案=W2 完了後に導入)。

## リスクと対処
- パラメータ化の漏れ(プロンプト内の暗黙の日本語文化仮定): W5 の別環境スモークが検出器になる。
- ゴールデンのバイト一致が崩れる変更が必要になった場合: そのウェーブを中断しユーザー判断へ。
- ODPT データの再配布制約: EnvPack にデータ実体を入れず「取得レシピ」を入れる(fetch スクリプト
  参照)ことでパック共有と権利を両立。
