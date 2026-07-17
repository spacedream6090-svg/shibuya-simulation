# env/shimokita — 手動テンプレ(stage3-4)TODO

make_env v0 は地理(stage1)と交通判定(stage2)までを自動化する。人口・組織・制度の
「値」は **渋谷の分布パラメータを流用した縮小版** を以下の手順で生成する(v0=手動テンプレ)。

## 1. 人口(personas)= 渋谷の職業/年齢分布を流用した縮小版
gen_personas.py は渋谷の昼間人口分布(職業・年齢・流入)を procedural に再現する。
街を差し替える最小手順は「その分布で N 名を生成」する:

    python scripts/gen_personas.py --pool 3000 --sample 20 --seed 42 \
        --out env/shimokita/personas_shimokita.json

→ 生成後、env.yaml の data: に `personas: env/shimokita/personas_shimokita.json` を追記する。
   ※ persona 本文の地名(「渋谷に通勤」等)は渋谷語彙のまま。真の街化(語彙差し替え)は
     v1/v2 の領分(env-classification.md ③-B)。v0 では分布のみ流用する縮退。

## 2. 組織・職場(organizations / assignments)= 地図 POI から導出
build_orgs.py は地図の POI 構成から架空組織台帳と配属を決定論生成する(ほぼ場所非依存):

    python scripts/build_orgs.py --map env/shimokita/map.json \
        --roster env/shimokita/personas_shimokita.json
    # 生成物を env.yaml data: の organizations / assignments に接続する
    #   organizations: env/shimokita/organizations_shimokita.json
    #   assignments:   env/shimokita/org_assignments_shimokita.json
    # ※ build_orgs.py の既定台帳は渋谷テーマの架空社名。街化は v1 の領分。

## 3. 制度(institutions)= ② 共有参照テーブルから pref セレクタで引く
env.yaml の institutions ブロック(雛形)を有効化し、pref をこの街の都道府県に:

    institutions:
      pref: <tokyo 等>            # ref/institutions_jp.yaml のキー(未整備の県は一次確認して追記)
      ref: ../../ref/institutions_jp.yaml
      council: {size: 9, term_days: 1460, deposit: 30000}   # 地点固有(議会規模・供託金)
      rent_income_ratio: 0.30

## 4. 交通(transit)= ODPT/GTFS(任意・徒歩の街なら不要)
この街に鉄道があり ODPT で取れるなら、路線識別子を定義して2段で生成する:

    python scripts/fetch_odpt.py --targets-file <lines.json> \
        --station-title 下北沢 --station-suffix <.RomanName>
    python scripts/build_transit_odpt.py --station 下北沢 \
        --keymap-file <keymap.json> --out env/shimokita/transit_shimokita.json

## 5. 検証
    python scripts/make_env.py --place shimokita --out env/shimokita --stage 7   # 構造検証+env_report
    python scripts/run.py --env env/shimokita run.n_agents=12 run.n_steps=24   # mock スモーク
