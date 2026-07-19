# ペルソナ100万プール — 決定論生成の統計サマリ(W2 P5)

作成: 2026-07-20 / 生成器: `scripts/build_persona_pool.py`(seed=42・LLM 不使用・完全決定論) /
種別: 実装成果物のサマリ(数百MB級の本体 `data/persona_pool/` は .gitignore 済み・非コミット)。

本書は W2 実行計画 §4 P5(ペルソナ100万生成)の成果物である。目的は
**同時存在数(LLMコスト源)とプール規模(記憶保持の source)の分離**(`docs/plans/persona-pool.md` §9)を
データ側で成立させること — すなわち日次ローテーション(P3)に食わせる**100万人の名簿**を、
出典統計と組織台帳に接地した5層構造で**決定論的に**吐く。この段では LLM 生成は一切行わない。

---

## 1. 層別件数(seed=42・fraction=1.0)

| 層 | 定義(現実の対応) | 件数 | 生成方式 | presence キー(§5) |
|---|---|---:|---|---|
| **L1 住民** | 夜間人口(街に住む) | 30,000 | (a) IPF(年齢×性別×職業の周辺分布) | `resident`(常時present) |
| **L2 域内従業者** | 通勤流入者+店員(昼間人口の中核) | 253,702 | (b) 需要駆動(組織台帳 employees 逆算) | `workday_shift`(暦∧シフト) |
| **L3 定期来街者** | 通学生+常連 | 36,690 | (b) 学校 capacity 逆算 + (d) 常連セグメント | `cadence`(通学日/週次) |
| **L4 非定期来街者** | 観光・買物・ビジネス来訪(**回転の主層**) | 678,588 | (d) 来訪セグメント + (a) 属性肉付け | `stochastic`(日次 visit_rate 抽選) |
| **L5 役割ペルソナ** | 駅員・運転士・タクシー・警察・配信者+議員 | 1,020 | (b) インフラ需要から人数確定 | `duty`(当番)/議員は `resident` |
| **合計** | | **1,000,000** | | |

- L2 = 会社従業者 252,311(台帳 `employees` 総和)+ 学校教職員 1,391(capacity/12 で逆算)。
- L3 = 学生 16,690(学校 capacity の逆算=需要駆動)+ 常連 20,000(週2-4回来街)。
- L4 は残余(= 総数 − 他4層)で回転の主層。**プール倍率は L4 に集中**(§5)。
- 回転はほぼ L3/L4 に集中し、L1/L2/L5 は「毎日概ね同じ顔」(`persona-pool.md` §2 の設計どおり)。

### presence(日次ローテーション区分)
各レコードに `presence` を付与(P3 のローテーション機構が読む純関数キー):
`resident`(常時) / `workday_shift`(暦∧シフト) / `cadence`(周期) / `stochastic`(確率抽選) / `duty`(当番)。
本 P5 では**キーの付与のみ**行い、presence の抽選ロジック自体は P3(engine 側)の担当。

---

## 2. 分布整合(検収数値)

### 2.1 L1 住民の周辺分布 vs 出典(`data/shibuya_population.json`)
IPF 骨格が出典の周辺分布を再現していることを実測(30,000 件):

| 軸 | 出典 share | 生成 share | 乖離 |
|---|---:|---:|---:|
| 性別(女) | 0.517 | 0.514 | −0.003 |
| 年齢 18-24 | 0.160 | 0.156 | −0.004 |
| 年齢 25-34 | 0.300 | 0.302 | +0.002 |
| 年齢 35-49 | 0.280 | 0.282 | +0.002 |
| 年齢 50-64 | 0.170 | 0.169 | −0.001 |
| 年齢 65-79 | 0.090 | 0.091 | +0.001 |
| 職業 会社員 | 0.300 | 0.304 | +0.004 |

全軸で乖離 ±0.004 以内。出典自体は「性別/来街者比は令和2年国勢調査実数由来、年齢帯/職業は暫定」
(`shibuya_population.json` の status)であり、実数化は差し替え時に本ファイルのみ更新すれば横展開できる。

### 2.2 L2 域内従業者(需要駆動の接地)
- 253,702 件が**組織台帳の全 11,010 事業所**(会社 11,000+学校 10)に org_id で接地(未使用組織ゼロ)。
- 各人に `org_id`・`role`(台帳 roles から巡回割付)・`shift_pattern`(open/close/days/rotates)を埋め込み。
- シフト日タイプ内訳: `mon-fri` 131,263 / `all`(年中無休・小売飲食) 85,814 / `mon-sat` 36,625。
- 従業者総和は台帳 `employees=252,311`(`docs/research/shibuya-population.md` §5 の bbox 従業者 約25.7万に整合)+ 教職員 1,391。

### 2.3 L4 非定期来街者(匿名合成セグメント)
- 訪日外国人比 0.150 / 再訪(revisit)比 0.101(**同一観光客が数日後に再訪→記憶保持**の source)。
- 来訪目的: 買い物 0.259 / 観光・見物 0.240 / 飲食 0.180 / エンタメ 0.120 / ビジネス来訪 0.100 /
  友人と会う 0.070 / 通院・用事 0.030。
- `visit_rate`(来訪確率/日): 対数一様[0.003, 0.06]・平均 0.019・中央値 0.013。
  **大多数は稀にしか来ない**=大きなプール倍率(回転の主層)。P3 が日次で `draw < visit_rate` で present を抽選。

### 2.4 L5 役割ペルソナ(インフラ需要)
| 役割 | 件数 | post(持ち場)例 | 根拠(`persona-pool.md` §4) |
|---|---:|---|---|
| 駅員 | 300 | 改札/ホーム/案内/事務室 | 4社9路線ターミナル×持ち場 |
| 電車運転士 | 60 | 路線別(範囲内を走行/折返し) | 大半は通過=範囲内乗務のみ計上 |
| バス運転士 | 120 | 東口/西口/南口/マークシティ | 渋谷=バス一大ターミナル |
| タクシー運転手 | 350 | 道玄坂/宮益坂乗場・流し | 交通量調査からのオーダー |
| 警察官 | 140 | 渋谷署/駅前・宇田川・神南交番・巡回 | 交番数×要員×シフト |
| 配信者 | 16 | ハチ公前/スクランブル/センター街 | インフラ非束縛の設計値 |
| **議員** | **34** | — | 現実の渋谷区議会=34議席(下記) |

---

## 3. 議員名簿(選挙なし・事前決定)

- **34名**を生成(`data/personas_councilors.json`=コミット対象・小)。
  現実の渋谷区議会 34議席に一致し、config の `institution_routes.assembly.size`(既定 9)**以上**を満たす。
- occupation は `src/society/tools.py::COUNCILOR_OCCS`(`"議員"`)に合致し、`visitor=false`(住民)。
  → `institution_routes.assembly.from_roster=true` で**警告なしに着席**することを smoke で確認済み
  (council 組成・from_roster=true・9名着席=size まで・フォールバック警告なし)。
- 各議員に `seat_id`(seat_01..34)と `party`(会派)を事前付与。**回転しない**(常時 present)。
- 議員名簿は**専用の乱数ストリーム+固定 id(`L5c_001..034`)**で生成するため、`--fraction` に依存せず同一
  (小規模テスト実行でコミット対象の名簿が揺れない=検収の安定性)。

---

## 4. 決定論とシャーディング

- 乱数はパートごとに `numpy.random.SeedSequence([master_seed, layer_code, part_index])` から導出。
  → **同 seed・同 fraction なら他パートの実行順に依存せず同一出力**。RngHub のステートレス設計
  (`persona-pool.md` §1.4)と同思想で、**シャード並列生成が可能**(各 part は独立に再現できる)。
- 出力は `data/persona_pool/{layer}/part-XXXX.jsonl`(1行=1レコード・PART_SIZE=50,000)。
  `meta.json` に層別件数・seed・スキーマ版・**各シャードの先頭行 blake2b ハッシュ**を記録
  (`tests/test_persona_pool.py` の同seed同出力チェックが参照)。
- **シャード並列化の指針**(将来 fraction/seed を増やして更に巨大化する場合):
  layer×part は完全独立ゆえ、`(layer, part_index)` をワーカーに配って並列生成→ meta を後段でマージすればよい。
  現状は単一プロセスで 12 秒のため並列化は未実施(下記性能)。

---

## 5. 性能実測(フル 100万・単一プロセス)

| 指標 | 実測値 |
|---|---|
| 生成時間 | **12.2 秒**(L4 8.4s / L2 2.5s / L3 0.35s / L1 0.19s / L5 0.02s) |
| ピークメモリ(working set) | **約 393 MB**(パート単位ストリーミング=1M でも有界) |
| 出力サイズ | **737 MB**(JSONL・23 シャード) |
| 議員名簿 `personas_councilors.json` | 28 KB(コミット対象) |

- メモリは PART_SIZE(50,000)刻みで書き出すため**総件数に比例しない**(L2 スロット表 ~25万タプルが主因)。
- 12 秒・393 MB は本選ハードでも余裕。並列化・parquet 化は現状不要(必要になれば §4 の指針で対応可)。

---

## 6. スキーマ互換と拡張

- 基本フィールドは `data/personas_300_civic.json` に完全準拠
  (`name/age/gender/occupation/visitor/commute/persona/traits/drive_threshold/fire_weight/`
  `bedtime_min/sleep_steps/has_bicycle/has_car` + commuter は `arrival_lead_min/commute_gateway/residence_line`)。
- **拡張フィールド**(層識別・ローテーション・接地):
  `id`・`layer`・`presence`・`org_id`・`role`・`shift_pattern`・`work_days`・`visit_cadence`・`subtype`・
  `visit_purpose`・`visit_rate`・`is_foreign`・`party_size`・`revisit`・`post`・`duty_pattern`・`seat_id`・`party`。
  拡張分は `src/society/agents/persona.py::build_agent` が `entry.get` で読まない=**無視されるため後方互換**
  (engine 非改変。プールの接続は P3 ローテーションの仕事)。
- `conf/` は**未変更**(本 P5 の掟)。

### LLM 上塗り対象(`data/persona_pool/llm_targets.json`)
- 深いペルソナ化(LLM 上塗り)をすべき id 一覧を出力(生成自体は後日=本選前)。
- 内訳: **L5 全員 + L3 常連(20,000)全員 + L1 の 10%(3,000)= 24,020 件(全体の 2.4%)**。
  `docs/plans/persona-pool.md` §3.2 の「(c) LLM は薄く・再登場する常連/役割など一貫性が観測に効く個体に限定」に沿う。

---

## 7. 再生成手順

```bash
# フル(~100万・約12秒)
python scripts/build_persona_pool.py --fraction 1.0 --out data/persona_pool
# 小規模(テスト/検証・約0.2秒)
python scripts/build_persona_pool.py --fraction 0.02 --out /tmp/pp_test --no-councilors-json
```

検証: `python -m pytest tests/test_persona_pool.py -q`(14 件・同seed同出力/層別件数/L1周辺分布/
org_id実在/議員定数/実在人名混入なし/presenceキー/スキーマ/fraction非依存議員名簿)。

---

## 8. 正直な限界・留意

1. **年齢/職業の出典は暫定**(`shibuya_population.json` の status のとおり。実数化は同ファイル差し替えで横展開)。
2. **L1 に世帯(household)次元は未導入**。仕様は「年齢×性別×世帯」を挙げるが、出典に世帯結合分布が無いため
   本段は年齢×性別×職業の IPF に留めた(IPU/HIPF への拡張は出典整備後=`persona-pool.md` §8.1)。
3. **外国人来街者(L4 `is_foreign`)も名前は日本語手続き生成**。実在人物想起・個人特定を避けるため
   (ETHICS)、氏名は全層で汎用の姓×名合成のみとし、`is_foreign` は行動セグメントの属性に留めた。
4. **presence の抽選ロジック本体は未実装**(本 P5 はキー付与まで)。日次ローテーション・ドーマント・
   k非交絡(共通乱数)は P3(engine)の担当(`persona-pool.md` §5)。
5. **深いペルソナ化(LLM 2-5%)は未生成**(対象 id のみ確定)。本選前にバッチ生成+人手確認ゲート。
