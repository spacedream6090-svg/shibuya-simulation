# 環境自動生成モジュールの構築計画(第16バッチ 2026-07-10・計画のみ・実装なし)

体制: Fable計画 → Opusリサーチ(docs/research/framework-architecture.md)→ Fable統合計画(本書)。
ユーザー構想: 「環境再現モジュールの要素を分解し、自動で環境を作成するモジュールの構築計画を
立てる」。前提: foundation-extraction.md の EnvPack が出力形式になる。

## 環境の要素分解と自動化難易度(リサーチ表の要約+Fable判定)
| 層 | 要素 | 入力データ源 | 自動化 | 既存資産 |
|---|---|---|---|---|
| 地理 | 道路網・建物・POI・フロア | OSM(Overpass/OSMnx)。高さ・階数は OSM タグ+推定 | **低(容易)** | build_map.py / patch_map.py(渋谷専用の座標が一部直書き→汎用化) |
| 交通 | 鉄道・バスのダイヤ | 日本: ODPT・GTFS-JP / 海外: GTFS | **低〜中** | fetch_odpt / fetch_gtfs_odpt / build_transit_odpt(駅名フィルタの汎用化が必要) |
| 社会 | ペルソナ分布(年齢・職業・世帯) | e-Stat 小地域統計(国勢調査)→ IPF で合成人口 | **中**(e-Stat API の癖・小地域の秘匿処理) | gen_personas.py(分布パラメータ化すれば地域差し替え可)/ IPF は既存試行あり |
| 社会 | 組織・職場・配属 | 生成した地図の POI 構成から導出 | **低**(既にほぼ場所非依存) | build_orgs.py |
| 制度 | 最低賃金・家賃相場・税・議会定数 | 都道府県別の公表値(最賃は厚労省表、家賃は公表統計) | **中**(表の整備は一度やれば横展開) | economy/government の機構+institutions パック(W3) |
| 文化 | 祝日・地域行事・群集イベント | 祝日=カレンダー法で自動 / 地域行事=**LLM抽出+人手確認** | **高**(捏造リスク) | annual.py の機構 |
| 語彙 | 地名・ランドマーク・プロンプト語彙 | 地図 POI から機械抽出+LLM 整形 | **中** | culture.lexicon(W2 で seam 化) |

## パイプライン設計: `make_env`(将来のCLI)
```
make_env --place "下北沢" --bbox <...> --out env/shimokita/
  stage1 geography : Overpass 取得 → map.json(検証: ノード連結性・POI密度・建物数)
  stage2 transit   : GTFS/ODPT 照会 → transit.json(無ければ「徒歩の街」宣言で継続)
  stage3 social    : e-Stat 小地域 → 分布パラメータ → gen_personas → personas.json
                     → build_orgs → orgs/assignments
  stage4 institutions: 都道府県テーブルから該当値を引く(無い項目は全国既定+「既定」フラグ)
  stage5 culture   : 祝日自動+地域行事の LLM 候補出し → **人手確認キュー**(未確認は入れない)
  stage6 lexicon   : POI 名から地名語彙を機械抽出 → env.yaml に書き込み
  stage7 検証     : 1日スモーク+calibrate_report の汎用バンド(睡眠・労働・移動)で
                     「街として成立しているか」を自動判定 → env_report.md
```
- 各 stage は独立再実行可能・失敗時は前段の成果物を保持(現 fetch→build の2段流儀の一般化)。
- **捏造ガード**: stage5/6 の LLM 生成物は「候補」止まりで、確認フラグなしでは pack に入らない。
  データが取れない要素は「無い」と宣言して縮退(transit なし=徒歩の街、行事なし=祝日のみ)。

## フェーズ計画
| フェーズ | 内容 | 完了条件 |
|---|---|---|
| **v0(半自動)** | stage1-2 の自動化+stage3-4 は手動テンプレ。渋谷の build_map/transit スクリプトの汎用化(bbox・駅名を引数化) | 別の街の EnvPack が半日の人手で作れる(W5 の実証と同一マイルストーン) |
| **v1(統計接続)** | e-Stat IPF による合成人口の自動化+制度テーブル(47都道府県)整備 | 名簿と制度値が place 指定だけで出る |
| **v2(一括生成)** | stage5-6 の LLM 支援+make_env 一発化+env_report 自動検収 | `make_env --place X` 一発で「回る街」が出る(人手確認は文化のみ) |
- v0 は foundation-extraction.md の W5(2つ目の環境での実証)と同時に着手するのが効率的。
- v1 の IPF は過去試行(e-Stat 取得の失敗記録あり)を踏まえ、API でなく統計表の手動DL+
  パーサでも可(自動化の定義を「place 指定→pack」に置き、取得だけは半自動を許す)。

## 本選(ハッカソン)との関係
- 本選での差別化点: 「渋谷で較正した基盤モデル」を**他の街に即日展開できる**こと自体が
  基盤モデル性の実証になる(較正レポートの汎用バンドがそのまま「街の再現度スコア」になる)。
- GPU 資源は不要(全 stage が CPU/データ処理)。本選前に v0 を済ませておけば、当日は
  環境差し替えのデモが可能。

## リスク
- OSM ODbL・ODPT 利用条件: pack にはデータでなく「取得レシピ」を同梱(再配布回避)。
- 小地域統計の秘匿・粒度: 300体規模なら区レベル分布で十分(過剰精度を追わない)。
- 文化・語彙の捏造: 人手確認ゲートで遮断(unverified は pack に入れない)。
