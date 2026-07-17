# env/shibuya — 渋谷 環境パック(EnvPack)

基盤モデル抽出 D1 の成果物。「渋谷という場所」を1ディレクトリに集約した宣言的定義。
基盤コード(`src/society`)は場所の知識を持たず、場所の値はここ(と `conf/config.yaml` の
`envpack:` ブロック)に集約する(原則: **機構=基盤・値=環境**)。

## 中身
- `env.yaml` — このパックの manifest。3層設計(`docs/plans/env-classification.md`)に沿う:
  - **③-A 地理**: `data:` は実体を **参照**(`data/*.json`。移さない)。実体でなく再生成レシピを指す。
  - **③-B 抽象**: `culture.lexicon`(地名語彙)/ `culture.events`(年中行事)/ `culture.media`
    (架空番組名)/ `climate`(月別気候)/ `ads`(掲出地点)/ `transit.station_filters`。
  - **② 共有参照**: `institutions.pref: tokyo` + `ref/institutions_jp.yaml`(最低賃金 等の都道府県値)。
  - `origin`(群集・注目の中心=地図原点のランドマーク)、`attribution`(ODPT/OSM 出典表示)。

## いまの読まれ方(W2 時点)
基盤コードは **`conf/config.yaml` の `envpack:` ブロック**を読む(`src/society/envpack.py` が正準化し、
`simulation.py` が `sim.envpackcfg` として1回だけ保持)。`env.yaml` の値はこのブロックと同値。
W4(EnvPack ローダ)で `env.yaml` → config キー群への展開が実装され、`--env env/shibuya` で
単一の場所定義から従来と同一ランを再現できるようになる。

## データの再生成(取得レシピ)
実体は再配布制約(OSM=ODbL / ODPT=出典表示・実行時API禁止)があるため、パックは実体でなく
取得手順を指す:
- 地図:   `python scripts/build_map.py …` → `python scripts/patch_map.py …`
- ダイヤ: `python scripts/fetch_odpt.py` → `python scripts/build_transit_odpt.py`
- 名簿:   `python scripts/gen_personas.py` / `scripts/build_personas.py`
- 組織:   `python scripts/build_orgs.py …`

## 別の環境を作るには(W5 の見取り図)
`env/<place>/env.yaml` を1つ足し、`data:` を新地図/ダイヤに、`culture`/`origin`/`climate` を
その街の実測値に、`institutions.pref` を該当都道府県に差し替える。基盤コードは無変更。
