# L2 域内従業者(約25.4万人)の「業務の実体」実査と設計

**日付**: 2026-07-21 / **担当**: 実装(Opus)、検収: Fable(親)
**関連**: docs/research/shibuya-organizations.md, docs/research/org-book-11k.md,
docs/research/persona-pool-1m.md, docs/research/interstitial-life.md §4.2(S2)

ユーザー要望(2026-07-20): 「L2 はそれぞれ職場が設定されそこで業務を行っている状態か?
そうでないなら L5 役割と同様の実装に統合してもいい。L2 の人々も接客などのサービスを行っている、
もしくは会社単位で何かのサービスを作っているだろうからそれを反映したい。**例は一部にすぎない。
L2 に含まれる職業をリサーチして実装せよ**」。

---

## 1. 現状確認 — L2 は「職場に居るが業務の実体イベントが無い」

### 1.1 生成: L2 は org_id/role/shift 付きで作られる
`scripts/build_persona_pool.py` の `_build_L2_slots` / `gen_L2`:
- 組織台帳 `organizations_shibuya_wide11k.json` の各社 `employees` を需要源に、
  `roles[i % len]` を割り当てて従業者スロットを展開(会社 + 学校教職員)。
- レコードに `org_id` / `role` / `shift_pattern{open,close,days,rotates}` / `presence:"workday_shift"`
  を埋め込む。occupation には role 文字列をそのまま入れる(例 "エンジニア"/"店員"/"スタッフ")。

### 1.2 在場・通勤・賃金は入る
- presence=`workday_shift` → `world/presence.py` が平日在場を決める(pool.enabled ON 時)。
- commuter として朝は範囲外に置かれ、`arrival_min` に enter_area(`_init_inflow_commuters`)。
- 退勤完遂で `_settle_work` → `wage` イベント(経済 v0 ON 時)。

### 1.3 しかし「職場で何をしているか」のイベントは基本的に無い
コードで確認した事実:
- **work_node の付与が occupation 依存で穴だらけ**。`agents/persona.py` の `_pick_workplace` は
  `_WORK_CAT`(会社員/エンジニア/デザイナー→office、カフェ店員→food、アパレル店員/美容師→shop、
  大学生→education、他→None)でしか職場 POI を引かない。L2 の role 文字列(店員/スタッフ/
  営業/コーポレート/教員 等)は `_WORK_CAT` に無く、**work_node=空 → 決まった職場を持たない**個体が
  多数生じる(=「職場に通っているはずが、実際にはどこにも勤務していない」)。
- 業務の実体イベント(接客・産出)は既定では**発生しない**。既存の産出イベント
  `production` / `study` は `organizations` フィーチャ(assignments ファイル駆動・既定 OFF)専用で、
  **pool 経路の L2 には接続していない**(`_ensure_orgs` は personas_file+org_assignments_* を要求し、
  pool の org_id は読まない)。

### 1.4 L5(duty)との対比
L5(駅員/警察官/配信者 等)は `presence:"duty"` + `duty_pattern` を持つが、L5 も専用の
「duty 行動」機構がコード上にあるわけではない(post/duty_pattern はプロンプト文脈と在場のためのメタ)。
つまり **L2/L5 いずれも「勤務中に業務の実体イベントを出す」機構は未実装**だった。
本タスクはその一般機構を新設する。

**結論**: L2 は「職場が名目上あるが、業務の実体イベントが無い/work_node すら付かないことが多い」状態。
層統合はしない(下記 §3)。代わりに勤務中エージェントへ業務の実体を与える一般機構を新設する。

---

## 2. L2 の職業構成(実数)

`data/organizations_shibuya_wide11k.json`(経済センサス由来・11,000 事業所・**総従業者 252,311 人**)。

### 2.1 業種別 従業者数(上位)
| 業種(industry) | key | 事業所 | 従業者 | 構成比 |
|---|---|---:|---:|---:|
| 卸売業・小売業 | WR | 3,080 | 59,937 | 23.8% |
| 情報通信業 | IT | 880 | 44,538 | 17.7% |
| 学術研究・専門・技術サービス業 | PS | 1,100 | 28,506 | 11.3% |
| 不動産業・物品賃貸業 | RE | 990 | 24,733 | 9.8% |
| 宿泊業・飲食サービス業 | FB | 1,650 | 17,665 | 7.0% |
| サービス業(他に分類されないもの) | SV | 660 | 17,655 | 7.0% |
| 医療・福祉 | MW | 440 | 10,675 | 4.2% |
| 金融業・保険業 | FI | 220 | 10,496 | 4.2% |
| 製造業 | MF | 330 | 8,900 | 3.5% |
| 建設業 | CN | 330 | 8,788 | 3.5% |
| 生活関連サービス業・娯楽業 | LS | 770 | 8,212 | 3.3% |
| 教育・学習支援業 | ED | 330 | 7,848 | 3.1% |
| 運輸業・郵便業 | TR | 165 | 3,911 | 1.6% |
| 複合サービス事業・その他 | CS | 55 | 447 | 0.2% |

### 2.2 職場 POI カテゴリ別(=業務タイプ判定に直結)
各社は `workplace_poi.cat ∈ {office, shop, service, food}` を持つ(台帳が既に分類済み)。

| workplace_poi.cat | 事業所 | 従業者 | 構成比 | 業務タイプ |
|---|---:|---:|---:|---|
| office | 4,015 | 129,872 | **51.5%** | オフィス系(産出) |
| shop | 3,850 | 68,149 | **27.0%** | 接客系(販売) |
| service | 1,485 | 36,625 | **14.5%** | 接客系(対人サービス) |
| food | 1,650 | 17,665 | **7.0%** | 接客系(飲食) |

→ **接客系(shop+service+food)= 約 48.5%(≈12.2 万人)/ オフィス系(office)= 51.5%(≈13.0 万人)**。
これは「L2 の人々は接客などのサービスを行っている、もしくは会社単位で何かを作っている」という
ユーザー観察と実データが一致することを示す。

wage_tier は 会社員 166,497 人 / 店員 85,814 人。output_kinds は service/goods/retail/food/content/ad/software。
学校は 10 校(大学 2・高校 1・専門 2・小中一貫 1・小 2・中 2、教職員は L2 に計上)。

---

## 3. 判断(親の方針)— 層統合はしない。L5 duty と同型の「業務行動」機構を L2 に一般化

- L2(質量)と L5(希少役割)は presence/名簿の設計上、区別を保つ方が有用
  (L2 は rotation の主対象・匿名的、L5 は固定 id・深いペルソナ化対象)。統合しない。
- 代わりに、**勤務中(work_node に在場・勤務時間帯)のエージェントへ業務の実体イベントを出す
  決定論・LLM 呼ゼロの一般機構**(`work.service`)を新設し、L2/L5/procedural いずれにも効くようにする。

### 3.1 業種→業務タイプの決定論マップ(config データ駆動)
コードに業種名をハードコードせず、**POI カテゴリ**(既に台帳が付与)を鍵に config で写像する:
- **接客系**: 客の消費 `spend.cat`(food/cafe/nightlife/shop)→ 接客ラベル(config `work.service.serve_by_cat`)。
- **オフィス系**: 職場 POI cat ∈ `work.service.office.poi_cats`(既定 [office])→ 日次 org_output。

### 3.2 実装の3点(既定 OFF・R1 準拠)
1. **serve(接客)**: 客の `spend`(接客カテゴリ)と**同一 work_node に在場・勤務中**のスタッフに
   `serve` を帰属(決定論・機械的)。客側イベントは不変(新イベントを足すだけ)。id 昇順・
   `max_serve_per_event` 上限。スタッフ不在の消費は agent_id=-1 の `serve{unstaffed:true}` として
   記録するのみ(挙動変更なし)。
2. **org_output(産出)**: 日次境界で、オフィス系職場に在場・在職の出勤者を職場単位で束ね、
   `出勤者数 × role重み` を `org_output` として1件記録(会社が「何かを作っている」の最小観測形)。
3. **本人に残る**: serve の要約を interstitial(S2)ダイジェストに1行供給(「今日は接客が多かった」級)。
   夜内省は既存の interstitial_digest 経路でこれを材料に取り込む(ONでも LLM 呼数不変)。

### 3.3 深追いしない境界(別トラック)
C2 会話のペアリング変更・経済価格/在庫・物流は本タスクではやらない。

---

## 4. 残課題(coverage)
- **work_node 付与の穴**: pool 経路の L2 は occupation(role)が `_pick_workplace` の
  `_WORK_CAT` に載らないと work_node を持たない。台帳 `workplace_poi.node` へ束ねれば
  接客/産出の網羅率が上がる(`organizations.commute_to_poi` と同型の pool 版が要る)。
  本機構は work_node が付いていれば正しく動く=coverage 拡大は別バッチ(ユーザー承認要)。
- serve の粒度は「同一ノード=同一店」近似(1ノードに複数店がある建物は取り違えうる)。
  POI 単位束縛は B 段。
- role 重みは既定 base_weight=1.0(=出勤者数)。業種別の生産性差は config `role_weights` で後付け可能。
