# ペルソナ生成・必要項目の充足・初期関係構築の全容(調査まとめ)

作成 2026-08-14 / 対象コミット `3a64044`(第112)/ 調査のみ・src/tests/conf は 1 行も変更していない。

ユーザーの問い:
> 初期条件のペルソナで必要となる項目は生成されるの? ペルソナの生成方法、初期の関係性構築についてはどうなっている?

## 0. 直答(3 行)

| 問い | 答え |
|---|---|
| 必要項目は生成されるか | **部分**。エンジンが `build_agent` で読む 17 項目は**全層 100% 充足**(欠損ゼロ)。一方 (a) 生成されるのに誰も読まない項目が 4 つ、(b) エンジンが要求するのに名簿に無く**別機構の ON が前提**になっている接続が 3 つ(職場 POI・賃金・世帯)、(c) 現実の初期条件として**存在しない項目**が多数(子ども・学歴・健康・資産・区外の旧友)ある。 |
| 生成方法 | `scripts/build_persona_pool.py` が 100 万件を **LLM ゼロ・完全決定論**で吐く。L1 のみ国勢調査周辺分布から IPF、L2/L3 学生は**組織台帳からの需要逆算**(org_id 込み)、L3 常連/L4 は合成セグメント、L5 は現実の人数根拠を書き下した固定表。 |
| 初期関係 | day0 に 7 機構(世帯 → SNS フォロー → 顔なじみ → 友人グラフ → party → spark → icebreak)。第112 で**プール入場時にも同じ配布が走る**ようになった(A1〜A11)。ただし**友人グラフだけは入場駆動化されていない**(day0 限定)。恋愛は初期値ゼロ=創発のみ。 |

---

## 1. 生成パイプライン

### 1.1 全体像

```
data/shibuya_population.json ─┐                      (周辺分布: 年齢帯×性別×職業)
                              ├→ build_persona_pool.py ─→ data/persona_pool/
data/organizations_shibuya_   ┘                              L{1..5}/part-XXXX.jsonl
  census.json (9,872社)                                      meta.json / llm_targets.json
      ↑ scripts/build_orgs.py --census --night-shifts       + data/personas_councilors.json
```

実行(finals の再生成手順は `conf/finals_observe.yaml:20-26` に明記):

```
python scripts/build_orgs.py --census --night-shifts
python scripts/build_persona_pool.py --orgs data/organizations_shibuya_census.json
```

`scripts/build_personas.py`(321 行)は**旧系統**で、数十〜数百人の小名簿を LLM 文章化つきで作る道具(D6)。100 万プールは通らない。ただし `_WORK_CAT` を import して職場整合を検査する(`scripts/build_personas.py:28`)。プールに公務員を注入する `inject_civil_servants`(`build_personas.py:50`)は**小名簿だけの機能**で、プール側には無い(→ §4 ギャップ)。

### 1.2 実測値(`data/persona_pool/meta.json`・seed 42 / fraction 1.0)

| 層 | 件数 | 生成の駆動源 | 実データ較正 | `visitor` |
|---|---:|---|---|---|
| **L1 住民** | 30,000 | 目標値 30,000 固定(`build_persona_pool.py:1018`) | **△** 年齢帯×性別×職業を IPF(`:556 _ipf_joint`)。性別のみ国勢調査実数、年齢帯/職業 share は**暫定値**(下記) | false |
| **L2 域内従業者** | 224,240 | 組織台帳 `employees` の総和 + 学校教職員(生徒 12 人に 1 人)を**スロット展開**(`:661`) | **◎** 台帳がセンサス較正(従業者 222,849 と一致) | true(commute) |
| **L3 定期来街** | 36,690 | 学生 = 学校 `capacity` から逆算(20,000)+ 常連 20,000(目標固定) | **○** 学生は台帳 capacity 由来。常連は合成 | true |
| **L4 非定期来街** | 707,778 | **残り** = `total(100万) − 他層`(`:1029`) | **×** 合成セグメント(目的×属性の重み表) | true |
| **L5 役割** | 1,292 | 固定表 `_L5_ROLES`(`:294`)+ 議員 34 | **○** 各行に現実の実数根拠をコメントで明記(消防士 45 = 3 部制 ×15 等) | 役割ごと |
| 計 | 1,000,000 | | | |

職業の種類 **186 種**(`occupations_distinct`)。うち L2 が 146 種を担う。

### 1.3 決定論の仕組み

- 乱数は `np.random.SeedSequence([master_seed, layer_code, part_index])` からパートごとに派生(`build_persona_pool.py:457 _seed_rng`、層コードは `:66 LC`)。→ **同 seed・同 fraction なら他パートの実行順に依存せず同一出力**(シャード並列可)。
- L3 常連は学生と名前空間を分けるため `part_index = 1000 + p`(`:824`)。議員は `part_index=1` の専用ストリーム + 固定 id `L5c_001..034` で **`--fraction` 非依存**(`:941-955`)。
- `_L5_ROLES` への追加は**必ず末尾**(id が並び順で振られるため。`:308`, `:355`, `:366`, `:406` に 4 度警告が書かれている)。
- 夜勤の埋め込みは**乱数を 1 draw も引かない**: 枠は末尾から数えるだけ(`:681 night_slot_count`)、就寝時刻は退勤時刻の純関数(`:652 night_bedtime_min`)。→ 夜勤なし台帳での再生成は完全同一出力。

### 1.4 実データ由来 vs 合成(正直な内訳)

| 要素 | 出所 | 状態 |
|---|---|---|
| 性比(男 117,907 / 女 125,976) | 令和2国勢調査 渋谷区 | **実数** |
| 来街者比率 0.56(昼夜比 226%) | 同上 sid 0004003060 | **実数** |
| 流入通勤者比率 0.74 | 統計 Today No.187 系 | **実数(2次資料)** |
| 年齢帯 share `[18-24 .16, 25-34 .30, 35-49 .28, 50-64 .17, 65-79 .09]` | — | **暫定**。e-Stat の JS 描画で静的取得に失敗、`meta.retrieval_attempts` に手順つきで残置 |
| 職業 share(会社員 .30 / 大学生 .12 / …12 種) | — | **暫定** |
| 事業所・従業者(9,872 社 / 222,849 人) | 経済センサス station_area_industry.json | **実数較正** |
| 学校 capacity・教職員比 | 台帳 | 合成(構成比は実在の教育課程準拠) |
| L4 の来訪目的・来訪確率・同行人数 | — | **完全合成** |
| L5 各役割の人数 | 各行に根拠コメント(区の調査・消防署の部制・路線数等) | **半実数**(地図 bbox 内に絞る方針) |
| 姓名 | 一般的な姓 60 × 名 96 の手続き生成 | 合成(実在人物想起を避ける規律) |

**status は `partially-real`** と `data/shibuya_population.json:meta` 自身が申告している。実数と偽装していない点は健全だが、**年齢と職業の骨格が暫定**であることは論文級主張の弱点(→ §4)。

### 1.5 職業名対応表(146 種化。第109 レーン PRES-B)

台帳の `(industry_key, sector_detail, role)` → 現実の職業名へ写像(`:269 occupation_for`、表は `:140 _OCC_BY_INDUSTRY` と `:179 _OCC_BY_SECTOR`)。規律 5 つがコード内に明文化されている:

1. 一般名詞のみ(実在ブランド・企業・人物を想起させない)
2. **台帳に無い業種の職業は発明しない**(宿泊業・保育所・理容室が台帳に 0 社 → ホテルフロント・保育士・理容師は生えない)
3. IT の現行 5 種は残す
4. **夜勤スロットのロールは写像を通さない**(conf が名指しで引く語のため。`:687`)
5. 写像に無い組は**ロール名のまま**(推測で埋めない)

効果: conf が名指ししていたのに名簿に 0 人だった「警備員」1,397 人・「設備保守員」1,033 人が実在化。退路は `--no-occupation-map`(第108 までの名簿とバイト一致)。

### 1.6 副産物

| 出力 | 内容 |
|---|---|
| `meta.json` | 層別件数・seed・シャード一覧(**`PoolStore` はこれしか読まない**)・職業分布全数・stale part 検知 |
| `llm_targets.json` | 深いペルソナ化(LLM 上塗り)対象 24,292 件 = L5 全員 + L3 常連全員 + L1 の 10%(`:1129`)。**生成は未実施**(後日の予定として残っている) |
| `data/personas_councilors.json` | 議員 34 名(コミット対象・`from_roster` で着席可能) |

---

## 2. ペルソナの全項目

### 2.1 レコードの全フィールド(1 行 = 1 人)

**A. `build_agent` が読む項目**(= エンジンの必須項目。`src/society/agents/persona.py:97-111,166-168`)

| フィールド | 生成方法 | 実データ較正 | 読み手 | 全層充足 |
|---|---|---|---|---|
| `name` | 姓 60 × 名 96 の手続き生成(`:482`) | × | `Agent.name`・プロンプト | ✅ |
| `age` | L1=IPF帯内一様 / L2=N(38,11) clip[18,68] / L3学生=学校段の年齢範囲 / L3常連=N(34,13) clip[16,78] / L4=N(36,14) clip[15,82] / L5=N(40,11) clip[20,66]・議員 N(52,9) | △(L1 のみ、暫定 share) | `friends._score`・`needs_profile`・世帯続柄・プロンプト | ✅ |
| `gender` | L1=IPF / L2・L3=女 49%・52% / L4=女 52% / L5=女 35% | ○(L1 は実数由来) | 世帯続柄(夫/妻)・プロンプト | ✅ |
| `occupation` | L1=IPF の 12 種 / L2=**職業名対応表**(146 種) / L3=学校段 or L4 表 / L4=9 種重み / L5=役割名 | ○(L2 は台帳由来) | `_WORK_CAT`(職場)・`WAGE_CAT`(賃金)・`COUNCILOR_OCCS`(議会)・`street_life`/`city_ops`/`incidents_env` の担い手判定 | ✅ |
| `visitor` / `commute` | 層で決定(L1=F/F, L2=T/T, L3学生=T/T, L3常連=T/F, L4=T/F, L5=役割ごと) | ○(来街者比率 0.56・通勤 0.74) | 帰宅・到着・世帯対象判定・`wage_target` | ✅ |
| `persona` | 手続き生成のテンプレ文(趣味・話し方・沿線を差し込む)。**構成概念語を書かない**規律 | × | LLM プロンプトの自己紹介 | ✅ |
| `traits`(internal_locus / nfc / risk_tolerance) | N(0.5,0.18) clip[0,1] + 10% を上位裾[0.9,1.0]へ(`:463`) | ×(心理尺度の分布形のみ) | drive/opinion/drift/reflect/sdt/needs/collective | ✅ |
| `drive_threshold` | `N(0.60 − 0.20·(nfc−0.5)·2, 0.08)` clip[0.30,0.85] | × | 発火閾値 | ✅ |
| `fire_weight` | `N(0.50 + 0.30·(locus−0.5)·2, 0.12)` clip[0.15,0.90] | × | 発火確率 | ✅ |
| `bedtime_min` | 非就業=22:00+10分刻み24通り / L2=退勤時刻(夕ピーク 80%+深夜裾)/ **夜勤者=退勤+30分から 1 時間散らす** | × | 帰宅トリガ・睡眠 | ✅ |
| `sleep_steps` | `randint(39,49)`(6.5〜8h) | × | 睡眠長 | ✅ |
| `has_bicycle` / `has_car` | 15% / 8%(L4 は自転車 0・車 5%) | ×(**要較正**) | 移動モード | ✅ |
| `arrival_lead_min` | 学生 N(30,15) / 就業 N(40,20) clip[10,120] | ○(朝ピークの一般則) | `arrival_min = work_start − lead` | L2/L3学生 |
| `commute_gateway` | 87% station / 13% edge | ○(§4.2 暫定 85-90%) | 到着・帰宅の出入口 | L2/L3学生 |
| `residence_line` | 沿線 8 種から一様 | ×(話題接地用メモ) | プロンプト・`Agent.residence_line` | L2/L3/L5 |

**B. スキーマ拡張(`build_agent` は `entry.get` で無視。別機構が読む)**

| フィールド | 生成 | 読み手(file:line) | 効いているか |
|---|---|---|---|
| `id` | `L1_00000000` 形式 | `PoolStore.id_of`(`world/pool.py:85`)→ `agent.id`・`pool_pid` | **◎ 中核**(日跨ぎ同一人物の保証) |
| `presence` | 層ごと固定 5 値 | `world/pool.py:33` → `PresenceRec.key` → `world/presence.py` のローテーション | **◎ 中核** |
| `org_id` | L2=台帳の社 id / L3学生=学校 id | `organizations.attach_record`(`simulation.py:1934`)・`work.bind_workplace`(`:1952`)・`friends._score`・`economy.wage_plan` | **◎**(`organizations.enabled` が前提) |
| `role` | 台帳のロール名(夜勤枠は夜勤ロール) | 同上 + `city_ops:652,1467`・`incidents_env:1323`(担い手判定) | ◎ |
| `shift_pattern` / `work_days` | 台帳の営業時間・曜日 | `world/pool.py:29,34` → presence の曜日資格 / `work.py:327` | ◎ |
| `duty_pattern` | L5 固定表 | `world/pool.py:30,38`(`days` のみ) | ○(`rotates`/`shift_hours` は**未使用**) |
| `visit_cadence` | L3 学生=`school_day` / 常連=`weekly_N` | `world/pool.py:35` | ◎ |
| `visit_rate` | log-uniform [0.003, 0.06] | `world/presence.py:394` | ◎(L4 の在場駆動) |
| `visit_purpose` | 7 目的の重み | `world/pool.py:42`(`sys.intern`)→ 第111 A1 の曜日×天候プロファイル | ◎ |
| `revisit` | 10% | `world/pool.py:37` | ○ |
| `party_size` | 1〜5 | `simulation.py:1794` → `party.py:68`・ontology 同行者軸 | ◎(`party.enabled` 前提) |
| `post` | L5 の持ち場文字列 | **persona 文への差し込みのみ**。`street_life`/`city_ops` は自前の持ち場表を使う | △ **文字列としてしか効かない** |
| `layer` | L1..L5 | `simulation.py:1978`(観測サマリの集計のみ) | △ 観測用 |
| `subtype` | `student` / `regular` | `scripts/analyze_founders.py` のみ | △ **解析用**(エンジンは読まない) |
| `is_foreign` | 15% | **読み手ゼロ** | ❌ **死に項目**(→ §4) |
| `seat_id` | `seat_01..34` | **読み手ゼロ**(議会は `occupation=="議員"` の id 昇順で着席。`tools.py:227`) | ❌ 死に項目 |
| `party`(会派) | 7 会派の巡回 | **persona 文のみ**。`tools.py` の議会も `assets.py` の `party` も無関係 | ❌ 実質死に項目 |

### 2.2 エージェント化のときに足される派生属性

`build_pool_agent`(`src/society/engine/simulation.py:1771`)の順序がそのまま「名簿に無い属性がどこで生えるか」の一覧になる。

| 順 | 生成物 | 実装 | 由来 | 決定論 |
|---|---|---|---|---|
| 1 | `Agent` 本体・**住居**(実在の住宅建物+階) | `persona.py:138-149` | `city.residential_buildings` から一様抽選 | stream `persona`(run.seed 依存) |
| 2 | **職場 POI**・勤務窓 | `persona.py:43 _pick_workplace` | `occupation` → `_WORK_CAT` → POI カテゴリ | 同上 |
| 3 | 手持ち現金・本業日給・バイト・口座分割 | `economy.py:271,249,281` | `occupation` 別レンジ | 同上 |
| 4 | 意見アンカー `N(0,0.3)`・感受性 | `persona.py:211-212` | traits 写像 | 同上 |
| 5 | 内省ドリフト率・深い内省パラメタ | `persona.py:216-227` | traits 写像(既定 OFF) | 同上 |
| 6 | 到着パルス量子化 | `simulation.py:1792` | 純関数 | 乱数ゼロ |
| 7 | 群のオントロジー(文化圏・軸・可制御性起点) | `simulation.py:1701` | **`pool_pid` の安定ハッシュ**(k/trait 非参照) | run.seed 非依存 |
| 8 | 心のモデル・知能層 | `mind.assign` | `(master_seed, agent.id)` の純関数 | ○ |
| 9 | **org 配属**(`org_id`/`org_role`/`org_line`) | `organizations.attach_record` | 名簿の `org_id` | 乱数ゼロ |
| 10 | **職場束ね直し** | `work.bind_workplace` | 台帳 `workplace_poi` × POI 実体 | 乱数ゼロ |
| 11 | **賃金プラン**(第112 WAGE) | `scheduler.wage_assign` → `economy.assign_wage_plan:1101` | 産業 × 規模帯 × 職種群 × 個体ハッシュ | **blake2b・乱数ゼロ** |
| 12 | SNS フォロー(k=6)+ 空 contacts | `net/internet.py:49 ensure` | 在場者から重複なし k 人 | stream `follows_entry` |
| 13 | 顔なじみ(同住居/同職場 最大 3 人) | `simulation.py:1898` | 建物索引の直近入場順 | 乱数ゼロ |
| 14 | SDT / 集団効力感 / **欲求プロファイル 5 軸** / 価値の充足 / 入力解像度 LOD | `simulation.py:1852-1876` | traits+年齢+職業 | 各専用 stream |
| 15 | **世帯**(`household_id`/`housemates`/続柄) | `household.py:373 bind_pool_household` | 名簿の決定論分割 + blake2b | **乱数ゼロ・run.seed 非依存** |
| 16 | 観光客フラグ・言語 | `diversity.py:161 assign_for_entry` | 個体ハッシュ閾値 | 乱数ゼロ |
| 17 | 長期目標・趣味 | `inner_life.py:261 assign_for_entry` | 純関数 | 乱数ゼロ |

12〜17 が**第112 で入場駆動化された部分**(レーン乙 ブロック2/3)。それ以前は `__init__` の一本道でしか配られず、finals 構成で **day1 以降に入場する 20.9 万人が SNS も顔なじみも世帯も持たない別種の住民**になっていた。day0 の着席では `_init_event_mark`(`simulation.py:1840`)で二重配布を防ぎ、直後に `__init__` が名簿全体へ一括配布する。

### 2.3 生成されるのに誰も読まない項目

| 項目 | 件数 | 状態 |
|---|---:|---|
| `is_foreign` | 149,895(L4 の 15%) | **完全に死んでいる**。非日本語話者は `society_diversity.foreign_ratio` が**別途ハッシュで**決める(`diversity.py:174`)ので、名簿の「訪日外国人」タグと**一致しない**。persona 文には「訪日外国人」と書かれているのに engine の `agent.language` は無関係に決まる=**内部矛盾** |
| `seat_id` | 34 | 議席は `occupation=="議員"` の id 昇順で決まる |
| `party`(会派) | 34 | persona 文にだけ現れる。議会の会派力学は存在しない |
| `duty_pattern.rotates` / `.shift_hours` | 1,292 | `days` しか読まれない |
| `subtype` | 20,000 | 解析スクリプト専用 |

### 2.4 エンジンが要求するのに名簿が直接は満たさない接続(**別トグルが前提**)

| 穴 | 実測 | 塞ぐ機構 | finals |
|---|---|---|---|
| **職場 POI が付かない** | `occupation` が `persona._WORK_CAT` に無い個体 **635,192 人 / 186 種中 166 種**。層別では **L2 224,240 人中 198,264 人(88.4%)が職場なし** | `work.bind_workplace`(台帳 `workplace_poi` へ束ね直し) | **ON**(`:583`) |
| **本業日給 0** | `economy.WAGE_CAT`(25 語)にも `CIVIL_SERVANTS` にも無い個体 **634,929 人 / 159 種**。L2 は 198,264 人が構造的に日給 0 円だった | 第112 `economy.wage_profile`(産業 380k〜260k × 規模帯 0.84〜1.16 × 職種群 0.66〜1.30 × 個体差、給料日 5 種、賞与) | **ON**(`:521`) |
| **世帯・同居が回転で壊れる** | `housemates`/`household_id` が退避に載らず、`build_pool_agent` が `home_*` を record から作り直していた | 第112 `household.pool_bind`(名簿の決定論分割) | **ON**(`:469`) |

**なお残る穴**: L5 の **880 人**(タクシー運転手 350・駅員 300・バス運転士 120・電車運転士 60・議員 34・配信者 16)は `WAGE_CAT` にも `CIVIL_SERVANTS` にも無く、`_WORK_CAT` にも無い。駅員/運転士/車掌は `transit_staff.bind` が勤務窓を与えるので第112 の日次 `_phase_wage_profile`(`scheduler.py:3666`)が後から拾うが、**タクシー運転手 350・配信者 16・議員 34 は勤務窓を持つ経路が無く、賃金・議員報酬とも 0 円のまま**(`work.py:236` が「地図に対応 POI カテゴリが無い層」として名指ししている)。

---

## 3. 初期関係の構築(全数)

### 3.1 day0 の 7 機構(`simulation.py:1160-1274` の一本道)

| 順 | 行 | 機構 | 何が作られるか | 決定論 | 現実較正 | finals |
|---|---|---|---|---|---|---|
| 1 | `:1173` | `household.build_households` | 世帯 id・同居者・**住居の共有**・続柄 | `pool_bind` ON なら blake2b(run.seed 非依存)、OFF なら stream `household` | 単身 64.5%(令和2国調 渋谷)・2人以上は全国分布で按分 | ON |
| 2 | `:1244` | `net.init_follows` | **SNS フォロー k=6**(全員から一様・重複なし)+ 空 contacts | stream `follows`(run.seed 依存) | **×**(冪等分布・優先的選択なし) | ON |
| 3 | `:1247-1260` | 顔なじみ | 同 `home_building` / 同 `work_building` で**1 人あたり最大 3 人**に `add_contact` + 記憶台帳 1 行 | 乱数ゼロ | ×(「密になりすぎない」ための実装都合) | ON |
| 4 | `:1263` | `friends.build_friend_graph` | **友人グラフ**(下記) | **blake2b・seed 20260722・run.seed 非依存** | ◎(McPherson 2001 homophily・職場 34.0%/学生時代 31.6%・Dunbar 入れ子層) | **ON**(`:656`) |
| 5 | `:1265` | `party.form_parties` | 来街者の**同行グループ**(名簿 `party_size` 1〜5)を同一ノードへ寄せ、相互 `closeness=5.0/tier=2` | 関係注入は乱数ゼロ | ○(同行人数は合成) | ON |
| 6 | `:1268` | `spark.apply` | 実験介入(関係の束・資本・集会アンカー) | 乱数ゼロ | 介入ノブ | **OFF**(観測ランでは除外) |
| 7 | `:1271` | `_load_icebreak` | 事前生成の初対面会話を両者の記憶+contacts へ | 生成物は固定ファイル | 実験の交絡排除用(全 k 条件で同一) | **OFF**(`icebreak_file: null`) |

### 3.2 友人グラフの中身(`src/society/friends.py`)

スコア(`:103-129`):

```
score = w_age(1.0) × max(0, 1 − |Δage| / age_scale(15.0))
      + w_occ(0.5)         if 同 occupation
      + w_same_work(1.2)   if 同 org_id(非学生)
      + w_same_school(1.0) if 同 org_id かつ両者 org_role=="学生"
      + w_same_area(0.4)   if 同 home_building
      + noise(0.3) × blake2b(seed, ペアキー)
```

読む属性は `age` / `occupation` / `org_id` / `org_role` / `home_building` のみ。**traits も k も読まない**(no-fingerprint 契約)。

次数は Dunbar の入れ子層で較正(`:48-54`、個体ごとに安定ハッシュで抽選):

| 層 | 次数 | 注入 closeness |
|---|---|---|
| 親友(tier3) | 3〜5 | `tier_close(12.0) + margin(0.5)` |
| 友人(tier2) | +7〜12 | `tier_friend(5.0) + 0.5` |
| 知人(tier1) | +20 | `tier_acquaintance(2.0) + 0.5` |

→ 有向次数 30〜37。対称化は**ペアの max tier**。`dunbar.py` の認知上限(scale 0.34 適用後 = 親友 2 / 友人 5 / 知人 17 / **総計 51**)は**構築時には効かず**、以後の関係増加にだけ効く。初期 37 < 上限 51 という設計。

対象は**居住者のみ**(`:163`)。来街者は圏外(世帯と同じ規約)。

### 3.3 プール入場時(第112 レーン乙)

| 機構 | 実装 | day0 との差 |
|---|---|---|
| SNS | `internet.ensure`(`:49`) | 冪等。候補は**その日の在場者**(`_pool_follow_candidates`・回転ごとに 1 度だけ組む)。`rng.choice(replace=False)` は 25 万人 × 2 万入場で非現実的なので O(k) 棄却抽出に置換(分布は同じ) |
| 顔なじみ | `_link_colocated`(`:1898`) | 建物索引を**参入順**で持ち、`reversed` で直近 3 人へ張る。退場者には書かない(`present_agent` で濾す) |
| 世帯 | `bind_pool_household`(`household.py:373`) | 名簿の決定論分割。**`pool_bind` ON なら day0 の着席もこちらを通る**(`household.py:193-201`)=`hh…` と `hp…` の 2 重分割が並立しない |
| party | 日境界でも `form_parties` | day0/毎日 |
| 観光・言語・長期目標・趣味・SDT・needs・価値・LOD | `_init_pool_agent_extras`(`:1830`) | ハッシュ or 専用 stream |
| **友人グラフ** | **無し** | ❌ **入場駆動化されていない**(→ §4) |

**関係の持続**: 退避(dehydrate)は上位 `relations_cap` 件だけを運ぶ。第112 レーン乙 A3 で**並べ替えキーが `count` → `closeness` 優先に修正**された(`world/pool.py:437-449`)。友人グラフの辺は `count=1`(会話履歴ではなく初期条件)なので、旧実装では**親友から先に捨てられていた**。finals は `relations_cap: 60`(既定 20)。

### 3.4 恋愛・パートナー

**初期値はゼロ**。`partner_id` は未設定で始まり、日次の `form_partners`(`household.py:608`)が相互 `closeness ≥ 15.0`(`tier_close 12.0` の上位)から決定論で成立させる=**完全に創発**。第112 レーン丙 5 で「片側だけ既婚」バグ(退場中の相手を `unbond` できず、再入場で復活する)を `reconcile_partner`(`household.py:400`)が修復。

### 3.5 決定論・seed の一覧

| 機構 | 乱数源 | run.seed 依存 | resume 不変 |
|---|---|---|---|
| 友人グラフ | blake2b(`friend_graph.seed=20260722`) | **否** | ○ |
| プール世帯 | blake2b(`pool_bind.seed=20260813`) | **否** | ○ |
| 顔なじみ・party 関係注入・icebreak 注入 | 無し | — | ○ |
| SNS `init_follows` | stream `follows` | 是 | ○ |
| SNS `ensure` | stream `follows_entry`,aid | 是 | ○ |
| day0 世帯(非プール) | stream `household` | 是 | ○ |

`RngHub.stream` は呼ぶたびに新しい Generator を派生するので、**新しい named stream を足しても既存の draw 列は 1 粒も動かない**——第112 の全レーンがこの不変量に乗っている。

---

## 4. ギャップ(現実の初期条件として欠けているもの)

較正可能な実データの有無つき。**上位 5 件を先に置く。**

### 上位 5 件

| # | ギャップ | 実測・根拠 | 較正可能な実データ | 難度 |
|---|---|---|---|---|
| **G1** | **住民に子どもが 1 人も居ない** | L1 の年齢は **18〜79 歳**(`shibuya_population.json:age_bands` が 18 始まり)。18 歳未満は L3 学生 5,641 人だけで、**全員 `visitor=true`(区外から通学)**。実測 `visitor=false` の未成年 = **0 人**。→ 世帯の「親/子」は 18 歳以上どうしのラベルにすぎず、出生・育児・学区・保護者責任がすべて成立しない | **有り**。令和2国調 渋谷区の 5 歳階級別人口(0-4 / 5-9 / 10-14 = 概数 2.4 万人)。`age_bands` に 3 帯を足し、`_SCHOOL_OCC` の生徒を居住者側にも配分すればよい | 中(L1 の IPF を 0 歳から張り直す+就学の職業写像) |
| **G2** | **世帯の年齢整合が無い** | `_family_roles`(`household.py:159`)は**年齢順位だけ**で夫/妻/親/子を割る。夫婦の年齢差制約も親子の年齢差制約も無い。day0 realistic 経路は `(地理, 年齢)` ソートで束ねるので**4 人全員がほぼ同齢**になり「40 歳の親と 39 歳の子」が生じる。プール経路(`_pool_partition`)は**名簿の並び順で連続 n 人を束ねる**だけなので年齢の相関すら無い | **有り**。国勢調査の世帯類型別構成(夫婦のみ/夫婦と子/単独/ひとり親)+ 人口動態統計の初婚年齢差・母の年齢別出生数 | 中(IPU/IPF で世帯を合成人口として直接生成するのが学術的正道。MATSim/ActivitySim の標準) |
| **G3** | **友人グラフが入場者に配られない** | `build_friend_graph` の呼び出しは `simulation.py:1263` の 1 箇所のみ。第112 で SNS・顔なじみ・世帯・needs 等 11 族は入場駆動化されたが**友人だけ取り残されている**。finals 構成で day1 以降に入場する 20.9 万人は「顔なじみ最大 3 人」しか初期関係を持たない。加えて実装が `residents × residents` の総当たり(`:177-178` が各居住者につき全員をソート、`:190-198` が全ペア走査)で、居住者 3 万人なら**約 9.0 億回のスコア計算 + 3 万回の 3 万件ソート**——day0 の壁時計コストは**未実測**(要計測) | 不要(既存機構の入場駆動化) | 中〜高(O(N²) を候補集約に変える設計が要る) |
| **G4** | **区外の旧友・家族が存在しない** | 関係の源泉は「同建物・同 org・年齢/職業の近さ」のみ。現実の紐帯の大半を占める**同郷・出身校・親族(別居)・前職**が 1 本も無い。来街者(70.8 万人)は**関係ゼロで入場**する(友人グラフは `visitor` を除外) | **一部有り**。社会生活基本調査・NHK 国民生活時間調査の交際時間、友人の出会い経路調査(職場 34% / 学校 31.6% は既に friends.py が使用)。区外の相手は**シムに実体が無い**ので「圏外の関係」を持つには別設計(記憶だけ持つ NPC 参照)が要る | 高(設計判断) |
| **G5** | **SNS フォローが一様ランダム k=6** | `init_follows`(`internet.py:40`)は全員から重複なし 6 人。出次数は**全員ちょうど 6**、入次数は Binomial ≒ Poisson(6)。現実の SNS は**べき則/対数正規のフォロワー分布**で、インフルエンサーが情報伝播を支配する。`net.follower_count`(`:87`)が「インフルエンサー判定」に使われているのに、初期条件にインフルエンサーが存在しない | **有り**。総務省 情報通信白書の SNS 利用率(年代別)、Twitter/X のフォロワー分布に関する公刊研究(べき指数 ~2.3)。年代別利用率だけでも「高齢層はフォロー数が少ない」を入れられる | 低〜中(優先的選択 or 対数正規で k を個体別にする。1 関数の差し替え) |

### その他のギャップ

| 分類 | 欠けているもの | 較正データ |
|---|---|---|
| 人口骨格 | **年齢帯 share・職業 share が暫定値**(`meta.status = partially-real`)。手順は `retrieval_attempts` に残置済み(e-Stat statsDataId 0003176482 等) | **有り**(e-Stat API・appId 必要) |
| 人口骨格 | **公務員がプールに居ない**。`build_personas.py:50 inject_civil_servants`(区職員/警察官/消防士)は小名簿専用。プールの「公務員」21,669 人は L4(来街者)の職業タグで、区職員として働いてはいない | 有り(国勢調査「公務」≈3.5%) |
| 人口骨格 | 世帯収入・資産・学歴・婚姻状態が**存在しない**。現金は職業別レンジの一様抽選のみ | 有り(全国家計構造調査・就業構造基本調査・国勢調査の学歴/配偶関係) |
| 身体 | 健康・持病・障害・要介護が**全員中立**(`agent.py:114-120` はすべて 0/False 始点)。医療機関 org は在るのに患者の素因が無い | 有り(国民生活基礎調査の有訴者率・通院者率) |
| 内部矛盾 | `is_foreign`(persona 文に「訪日外国人」と書かれた 14.9 万人)と `society_diversity.foreign_ratio`(engine が別ハッシュで決める `agent.language`)が**一致しない** | 不要(名簿値を読むだけで解消) |
| 内部矛盾 | L3 常連の年齢下限が 16 歳なので「16 歳の会社員」が 720 人生じる(実測) | 不要(clip の下限を職業依存にするだけ) |
| 賃金 | タクシー運転手 350・配信者 16・**議員 34**(報酬)が賃金経路に載らない | 有り(区議会議員の議員報酬は公表値) |
| 移動 | 自転車 15% / 自動車 8% が根拠なし | **有り**(全国都市交通特性調査・パーソントリップ調査。渋谷区は自動車保有率が全国最低水準) |
| 関係 | `party`(会派 7 つ)が persona 文だけの飾りで、議会に会派力学が無い | 有り(渋谷区議会の実際の会派構成) |
| 関係 | 「顔なじみ最大 3 人」に根拠が無い(過密回避の実装都合とコメントにある) | 一部有り(近隣交際に関する社会調査) |
| 生成 | `llm_targets.json` の 24,292 件(深いペルソナ化)が**未生成**。L5 全員と L3 常連は今も手続き生成のテンプレ文のまま | — |

---

## 5. 参照(主要 file:line)

生成:
`scripts/build_persona_pool.py` — `:66` 層コード / `:140,:179,:269` 職業名対応表 / `:294` L5 固定表 / `:457` seed 派生 / `:463` traits / `:556,:578` L1 IPF / `:633-657` 夜勤 / `:661,:709` L2 / `:766,:780,:820` L3 / `:857` L4 / `:900` L5+議員 / `:1004` build_pool / `:1129` llm_targets
`scripts/build_orgs.py`(台帳・`--census --night-shifts`)/ `scripts/build_personas.py`(旧系統)
`data/shibuya_population.json`(周辺分布・`meta.status`)

読み込み:
`src/society/world/pool.py:27` `_slim` / `:85` `id_of` / `:102` `get` / `:437-449` 退避の並べ替え
`src/society/agents/persona.py:26` `_WORK_CAT` / `:43` `_pick_workplace` / `:71` `build_agent`
`src/society/engine/simulation.py:1160-1274` day0 一本道 / `:1617` icebreak / `:1771` `build_pool_agent` / `:1830` 入場駆動配布 / `:1884` フォロー候補 / `:1898` 顔なじみ / `:1934` org 配属 / `:1952` 職場束ね直し

関係:
`src/society/friends.py:38` 既定値 / `:103` スコア / `:154` 構築
`src/society/household.py:159` 続柄 / `:180` day0 / `:287-397` プール束ね / `:608` パートナー
`src/society/net/internet.py:40` `init_follows` / `:49` `ensure` / `:81` `add_contact`
`src/society/party.py` / `src/society/dunbar.py:174` 認知上限

経済:
`src/society/economy.py:24` `WAGE_CAT` / `:723-768` 第112 賃金表 / `:1054` `wage_eligible` / `:1101` `assign_wage_plan`
`src/society/engine/scheduler.py:3544` `wage_assign` / `:3666` 日次清算

設定:
`conf/finals_observe.yaml:20-26` 再生成手順 / `:60` pool / `:108` relations_cap 60 / `:421` organizations / `:462-470` household+pool_bind / `:521` wage_profile / `:583` bind_workplace / `:656` friend_graph
`docs/plans/persona-pool.md`(正典の設計計画)
