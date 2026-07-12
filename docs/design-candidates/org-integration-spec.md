# 組織台帳の Wave2 統合仕様(バッチE、2026-07-06)

> 目的: 架空の組織台帳(`data/organizations_shibuya.json`)と配属
> (`data/org_assignments_*.json`)を、Wave2 でエンジン(`src/`)へ結線するための仕様。
> **本バッチではエンジンを一切編集していない**(データと本仕様書のみ)。統合は本仕様に沿って
> 別 Wave で最小差分で行う。
>
> **不変条件(最重要)**: 統合しても **LLM 呼び出し回数を1回も増やさない**。台帳は決定論の
> 事前計算データであり、産出(production)・学習(study)・収益の記録はすべて非LLMの
> スケジューラ経路で行う。プロンプトへの注入は「既存の1プロンプトに1行足す」だけ(新規
> プロンプト・追加生成なし)。
>
> 前提資料: `docs/research/shibuya-organizations.md`(構成の出典)。関連: `src/society/economy.py`
> (賃金)、`src/society/engine/scheduler.py`(勤務完遂)、`src/society/observer/schema.py`
> (イベント種)、`src/society/cognition/deliberate.py`(プロンプト)、`src/society/cognition/routine.py`
> (勤務窓)。

---

## 0. データ構造の要約(統合側が読むもの)

`data/organizations_shibuya.json`
- `companies[]`: `{id, name(架空), industry, industry_key, sector_detail, products_services[],
  size{employees,band}, wage_tier(会社員/店員/自営), workplace_poi{cat, poi_id, node, x, y},
  roles[], generalist_roles[], output_kinds[]}`
- `schools[]`: `{id, name(架空), school_type, subjects[] または faculties[]/lecture_fields[],
  timetable{period_min, periods_per_day, start}, capacity, workplace_poi{cat=education,...}, roles[]}`
- `workplace_poi.node` は必ず地図(`meta.map`)の実在ノード(検証済み)。gig umbrella
  (自営)は `workplace_poi.cat=null`(固定拠点なし)。

`data/org_assignments_{tag}.json`
- `assignments[]`: `{agent_index, org_id, role, occupation, resident_type, org_name}`
- `unassigned[]`: `{agent_index, name, occupation, resident_type, reason}`(reason=unemployed 等)
- `meta`: coverage・by_reason・by_org_kind・assigned_by_resident_type。

統合側は起動時に台帳と該当名簿の配属を読み、`agent.org_id` / `agent.org_role` を
`agent` に持たせる(1属性追加。既存フィールドは不変)。配属は `agent_index` = 名簿の並び順
= エンジンの `build_agent` 生成順に一致する(persona.py が名簿を先頭から生成)。

---

## 1. scheduler / economy への接続点

### 1.1 産出(production)イベント = 勤務完遂フック
- **登録済み**: `observer/schema.py:93`
  `register_event_kind("production", "職場での産出(財・サービスの実態){org, output, kind}")`。
- **発火点**: `engine/scheduler.py:156` `_settle_work(sim, agent, step, sim_min)`。ここは
  退館(`exit_building`)時に本業/バイトの完遂を判定し賃金を払う既存フック。`main_done`
  が真(職場ビルからの退館=勤務完遂)になった直後に、非LLMで1行ログするだけ:
  ```python
  # _settle_work 内、main_done 判定後(既存の _pay_wage と並置)
  org = sim.orgs.get(agent.org_id)          # 台帳(dict)。無ければ何もしない
  if org and org.get("output_kinds"):
      kind = org["output_kinds"][0]         # 決定論(hashで選んでもよいが乱数streamを汚さない)
      output = org["products_services"][0]  # 産出の実態(架空・具体)
      sim.logger.log(Event(kind="production", ...,
          payload={"org": agent.org_id, "output": output, "kind": kind}))
  ```
- 学生(role="学生")の登校完遂も同じ `_settle_work`(学生は work として扱われ
  `work_start/end` を持つ)で判定できる。学生は `study` を、就労者は `production` を出す
  (`agent.org_role=="学生"` で分岐)。**賃金ロジックは一切変えない**(学業は無給=
  `wage_amount` が 0 のまま)。

### 1.2 学習(study)イベント = 登校完遂フック
- **登録済み**: `observer/schema.py:92`
  `register_event_kind("study", "学校の授業・学習(教科・講義){org, subject, role}")`。
- 学生の登校完遂時に、台帳の学校の `subjects`(小中高)または `lecture_fields`(大学・専門)
  から**その日の1教科を決定論選択**して記録:
  ```python
  sch = sim.orgs.get(agent.org_id)
  subj_pool = sch.get("subjects") or sch.get("lecture_fields") or []
  subject = subj_pool[(sim_min // 1440) % len(subj_pool)]   # 曜日で巡回=非乱数
  sim.logger.log(Event(kind="study", ...,
      payload={"org": agent.org_id, "subject": subject, "role": "学生"}))
  ```
- 時限(timetable.period_min/periods_per_day)は §3 の routine 制約で使う。

### 1.3 会社の売上(産出→組織収益)の抽象化
- **原則(B段の市場メカニズムは作らない)**: 売上=個々の消費者取引の集計ではなく、
  **勤務完遂1回=その組織の収益カウンタに固定額を積む**だけの記録に留める。
- 実装: `sim.org_ledger[org_id]` に `{production_count, revenue_est, wage_paid}` を持ち、
  `_settle_work` の production 発火時に `revenue_est += 単価×係数`(単価は
  `output_kinds`/`wage_tier` から決め打ち、`economy.wages` を流用可)。これは既存の
  `_pay_wage`(個人への賃金)とは別レイヤの**組織会計の集計のみ**。
- 自営(gig umbrella, `workplace_poi.cat=null`)は固定拠点=勤務完遂フックに乗らないため、
  `economy.gig_profile`(日銭)を組織収益ではなく個人所得として扱う(現状のまま)。
  production は出さない(固定産出拠点がない)。台帳上は所属記録のみ。
- 市場(価格形成・需給・在庫)は **B段**に委ねる。本仕様の収益は「産出量の代理指標」に留め、
  `public_budget`(schema.py:90、行政会計)と同じ「集計だけ」の粒度に合わせる。

### 1.4 賃金との整合(wage_tier)
- 台帳の `wage_tier` ∈ {会社員, 店員, 自営} は `economy.WAGE_CAT` の値と一致。統合時に
  agent の職業→wage_tier と台帳の org.wage_tier が矛盾しないことを assert できる(配属は
  職業→業種で決めているので自動的に整合)。**賃金額のロジックは変更しない**。

---

## 2. 発火プロンプトへの職場・学校1行の注入

- **注入位置**: `cognition/deliberate.py:67` `build_prompt` の**ペルソナ節**
  (`lines = [_header(...), agent.persona, "時刻: ...", "場所: ..."]` の直後)。
  ここに所属1行を足す:
  ```python
  if getattr(agent, "org_line", None):
      lines.append(agent.org_line)   # 例: "職場: (株)スクランブル計画(業務SaaS開発)"
  ```
- `agent.org_line` は起動時に台帳から1回だけ組み立てる決定論文字列:
  - 就労者: `f"職場: {org.name}({org.sector_detail})"`
  - 学生: `f"学校: {school.name}({school.school_type}・{主な学部/教科})"`
  - 自営: `f"仕事: {org.sector_detail}(フリーランス)"`
- **LLM 呼数不変の理由**: `build_prompt` は発火・朝の計画(`planning.py:42`)・内省
  (`reflection.py:45/90`)が**共有する唯一のプロンプト組み立て**。ここに1行足すと全経路に
  一様に反映されるが、**プロンプトの本数も生成回数も変わらない**(APC prefix 一致も、
  ペルソナ節はもともと個別部なので崩さない)。
- R17/R9 遵守: 注入するのは架空の組織名と事業内容のみ。構成概念語(効力感等)は入れない
  (`agents/validate.py` のバリデータに引っかからない平文)。

---

## 3. 学生の時間割が routine に与える制約

- 現状 `cognition/routine.py:38` `in_work_window` は `work_start_min..work_end_min` で就労/
  登校を一様に扱う。学生の**時限構造**(1コマ=小45/中50/大90分、1日 periods_per_day コマ)を
  routine の在校時間へ反映する:
  - `work_start_min = timetable.start`、`work_end_min = start + periods_per_day×period_min
    + 休憩`。これは persona.py の学生 5h 決め打ちを台帳由来に置換する seam(**値の出所を
    台帳にするだけ**でロジックは不変)。
  - コマ境界(period 区切り)で §1.2 の `study` を出す設計も可能だが、**LLM は呼ばない**
    (study は非LLMログ)。授業中は routine が「在校=working 相当」を返し、発火抽選の
    土台は現行のまま。
- 会社員の勤務時間帯(9:00-18:00 標準、`WORK_HOURS`)も同様に台帳の標準値へ寄せられるが、
  既存の persona.py(8:00-10:30 始業・8h)の後方互換を壊さないため、**seam として提示するに留め**、
  既定は現行値、台帳値の採用は Wave2 のオプトインにする。

---

## 4. 公務員 / government(別バッチB)との接続

- 別バッチBが実装中の `government`(区/都/国の行政主体、`schema.py:88-90` の
  `tax`/`civic_service`/`public_budget` を発火)と本台帳を**区役所 org**で結ぶ。
- 追加する org(台帳に1件追記でよい): `{id:"gov_ward_01", name:"渋谷区役所(架空)",
  industry:"公務", wage_tier:"会社員", workplace_poi:{cat:"office",...},
  roles:["区職員","窓口","管理職"], output_kinds:["civic_service"]}`。
- 配属規則: 職業が「公務員」相当のエージェント(現名簿には未登場)を `gov_ward_01` へ。
  現行の12職業には公務員がないため、**バッチBが公務員職業を名簿へ足した時点で
  `build_orgs.py` の `OCC_INDUSTRIES` に1行追加**([公務]→[gov])すれば自動配属される。
- 収益接続: 区役所の `production` は `civic_service`、収益カウンタは B段の `public_budget`
  (歳入=税、歳出=給付)へ合流させる(本台帳の org_ledger を government 会計に委譲)。

---

## 5. 統合チェックリスト(Wave2 で満たすこと)

1. agent に `org_id`/`org_role`/`org_line` を1属性ずつ付与(既存フィールド不変)。
2. `_settle_work` に production/study の**1行ログ**追加(賃金ロジック不変・乱数stream不変)。
3. `build_prompt` ペルソナ節に**所属1行**注入(プロンプト本数・生成回数不変)。
4. 学生の在校時間を台帳 timetable 由来にする seam(既定は後方互換、台帳採用はオプトイン)。
5. org_ledger は「集計のみ」。市場・価格・需給は B段に委ねる。
6. government(バッチB)とは 区役所 org + `OCC_INDUSTRIES` 1行で結線。
7. **回帰**: 既定 OFF 経路では出力バイト一致(mock/≤24step スモークで確認。実LLM不要)。

---

## 6. 未配属・来街者の扱い(統合側の注意)

- `unassigned` は現状 **無職のみ**(coverage 95-96%)。無職は経済的所属なし=production/study を
  出さない。統合側は `agent.org_id is None` を安全に扱う(上記フックは org 無しなら no-op)。
- 来街者(`resident_type=leisure_visitor`)も就労職業ならエンジンが職場POIを与えるため配属済み。
  これは persona.py の現挙動を鏡写しにしたもの。もし「区外で働く来街者を Shibuya org に
  紐付けない」方針にするなら、`build_orgs.py` の `assign_agent` 冒頭で
  `resident_type=="leisure_visitor"` を early-return する1行を足せば切り替え可能(データ再生成のみ、
  エンジン不変)。判断は本統合時にユーザーへ確認する。
</content>
