# env_report — shimokita(下北沢)

自動生成: scripts/make_env.py v0(D2)。取得統計・縮退・未実施を明示する。

## stage1 geography(地図)
- 原点: [35.66125, 139.668](モード=bbox-center)/ bbox(S,W,N,E)=[35.6595, 139.666, 35.663, 139.67]
- OSM elements 取得数: 4126
- ノード 177 / エッジ 220(地下 11 / デッキ 0)
- 建物 492(住宅系 435)/ POI 188 / ゲートウェイ 26
- POIカテゴリ: {'shop': 86, 'food': 69, 'service': 14, 'hall': 4, 'nightlife': 13, 'office': 1, 'cinema': 1}
- **連結性: 連結(1成分)** / 最大成分 177/177(=1.0)/ ノードID一意=True
- 構造検証 ok = **True** / 出力: env/shimokita/map.json

## stage2 transit(交通)
- **縮退=徒歩の街(mode=walking)**: 徒歩の街として継続(transit 未生成)。理由: ODPT_API_KEY=あり / 路線識別子未定義

## stage3-4 templates(人口・組織・制度)
- 手動テンプレ手順: env/shimokita/TODO.md(gen_personas / build_orgs / institutions 雛形)
- personas(渋谷名簿の機械的縮小流用): env/shimokita/personas_shimokita.json (20 名・src=data/personas_100_civic.json) ※persona 本文の地名は渋谷のまま(v0 縮退)
- institutions: pref=tokyo

## 縮退・未実施の明示(誠実性)
- 文化(地域行事・番組名)= LLM 生成せず base 既定(generic)に縮退(捏造ガード=v2 の領分)。
- 語彙 = 地名(place_name)のみ機械設定。persona/組織台帳の渋谷語彙は未街化(v1/v2)。
- 交通 = 徒歩の街に縮退(上記 stage2)。base のダイヤ設定が読まれるが place 固有ダイヤは未生成。
- 気候 = base 既定(東京近似)を継承。place 固有の気候は未設定(v1 以降)。

## attribution
- 地図: © OpenStreetMap contributors(ODbL)。Overpass 経由取得。EnvPack は取得レシピを指す。
