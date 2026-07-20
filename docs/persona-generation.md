# ペルソナ生成のまとめ(現行仕様・2026-07-21 第40バッチ)

> エージェントの「人物」がどう作られるかの全体像。設計正典は
> [plans/persona-pool.md](./plans/persona-pool.md)(プール設計)・
> [plans/w2-execution-plan.md](./plans/w2-execution-plan.md) §4 P5(実行計画)。
> 本ファイルは**現状の一枚まとめ**(仕様変更時はここも更新)。

---

## §1 生成の2経路

| 経路 | 用途 | 生成器 | 規模 |
|---|---|---|---|
| **直接生成** | 小〜中規模ラン(実験・デモ) | [`scripts/build_personas.py`](../scripts/build_personas.py) | 数十〜数百体 → `data/personas_N.json` |
| **100万プール** | 本番(P3ローテーションで日次入替) | [`scripts/build_persona_pool.py`](../scripts/build_persona_pool.py) | 100万体 → `data/persona_pool/`(**gitignore**・736MB) |

どちらも**シミュ実行時は読むだけ**(実行中のペルソナ生成LLM負荷ゼロ・決定論)。

## §2 直接生成(build_personas.py)= 3段パイプライン

1. **IPF骨格**: [`data/shibuya_population.json`](../data/shibuya_population.json) の周辺分布
   (年齢×性別×職業・来街者比率=公的統計由来)から結合分布を推定しサンプル。
2. **尺度サンプリング**: traits(裾を明示確保)+欲求発火の個体差。traits→factors 写像は
   R9(参照は factors/economy/opinion 係数のみ)を遵守。
3. **LLM文章化**: Verbalized Sampling(5案+確率→既出と最も異なる案を採用=mode collapse対策)。
   構成概念語バリデータ(注入/評価分離)で検査。`--no-llm` で手続き生成に縮退可。

## §3 100万プール(build_persona_pool.py)= 5層×決定論

実測(meta.json・seed42・12.2秒で全量生成):

| 層 | 中身 | 件数 | 需要源 |
|---|---|---|---|
| **L1 住民** | 夜間人口の IPF 骨格 | 30,000 | shibuya_population.json |
| **L2 域内従業者** | 組織台帳の employees から逆算・**org_id/role/shift を本人に埋込み** | 253,702 | [organizations_shibuya_wide11k.json](../data/organizations_shibuya_wide11k.json)(台帳総和 252,311 と±2%整合) |
| **L3 定期来街** | 学生(学校 capacity 逆算)+常連(週次 cadence) | 36,690 | 台帳(学校)+分布 |
| **L4 非定期来街** | 回転の主層(観光/買物/ビジネス来訪の匿名合成セグメント・`is_foreign` フラグ有) | 678,588 | 同時滞在実測(人流データ)への充足 |
| **L5 役割** | 駅員/運転士/警察官/配信者など+**議員34人**(実定数・名簿制) | 1,020 | 制度・サービス提供の要員表 |

- **決定論**: 乱数は `SeedSequence([master_seed, layer_code, part_index])` 由来=同 seed なら
  シャード並列でもバイト再現。`--fraction 0.02` で縮小プール(テスト用)。
- **スキーマ**: 基底=`data/personas_300_civic.json` 互換(name/age/occupation/traits/…)+拡張
  (id/layer/presence/org_id/role/shift_pattern/visit_cadence/visit_purpose/is_foreign/party 等)。
  拡張は `persona.build_agent` が `entry.get` で読む後方互換(未知キーは無害)。
- **副産物(コミット対象)**: 議員名簿 [personas_councilors.json](../data/personas_councilors.json)
  (`assembly.from_roster` で着席)。

## §4 LLM上塗り(深いペルソナ化)= 本選前の宿題

- 対象リスト `data/persona_pool/llm_targets.json`(**24,020人 ≈ 2.4%**)= L5全員+L1の10%+L3常連。
- 中身: §2 の LLM 文章化を対象者にだけ適用(実行は本選前・[finals-day1-decisions.md](./plans/finals-day1-decisions.md) **D7** で率を最終決定)。
- 残り ~97.6% は手続き生成の persona 文のまま(それでも属性・生活圏・職は全員固有)。

## §5 実行時の流れ(プール→エージェント)

1. **presence 純関数**(P3・[world/presence.py](../src/society/world/presence.py)): `stream("presence", pid, day)` で
   その日の在場者を層優先(住民・役割>従業者平日>定期 cadence>非定期確率)+`pool.present_cap` で確定。
2. **PoolStore 遅延読み**([world/pool.py](../src/society/world/pool.py)): 必要シャードだけ読む。
   `agent.id` はプール列挙順の密 int(日跨ぎ安定=観測の同一人物性を保証)。
3. **build_agent**: ペルソナ record → エージェント実体(traits→factors 写像・worldview 初期化)。
4. **退場時 dehydrate / 再来街 hydrate**(DormantStore): 経験由来状態(信念・関係・所持金・意見…)のみ
   退避し、静的属性はペルソナから決定論再構築。**記憶を持った再来街**が成立。

## §6 群のオントロジー(文化圏×経験・第40バッチ新設)

外部アドバイス「地震に慣れた日本人と欧州旅行者では行動が異なる。**世界観を共有する群の割合を
コントロール**できると精密予測に近づく」を受けた拡張(ユーザー承認 2026-07-21)。

- **属性はプールに書かない**: 群割当は `stable_hash(ontology.seed, persona id)` の**純関数**として
  構築/hydrate 時に導出(736MB の再生成不要・run.seed 非依存=ラン間で同一人物は同一群)。
- **群定義と割合は config データ駆動**(`ontology.groups` / `ontology.composition`=層別構成比)。
  既定4群: 都市圏日本人 / 国内他地域 / アジア圏旅行者 / 欧米圏旅行者(比率は自由に変更可=実験ノブ)。
- **行動差はルールで書かない**: プロンプトに**「経験の事実」1行**(「地震をほとんど経験したことがなく…」)を
  注入するだけで、対処行動の差は LLM に委ねる(nature-like=ボトムアップ創発の方針)。
  worldview(可制御性など)の**初期値オフセット**のみ群別に与え、以後の更新則は不変(経路依存を保存)。
- **計測**: agents.json に群 id を共変量記録+`scripts/analyze_groups.py` で災害/ショック窓の
  群別反応(移動開始潜時・移動距離・退避率)と平常時の行動差を集計。**群割合を振った A/B** が
  「割合コントロール下の予測」の実験系。
- **R1整合**: 割当は traits・k と直交(persona id のみの関数)・LLM呼数不変・既定OFF=バイト一致。

## §7 掟(この分野の恒久ルール)

- `data/persona_pool/` は**コミットしない**(gitignore)。生成器+meta+小さい名簿のみコミット。
- 実在個人名は生成しない(ETHICS)。文化圏の記述は「経験の事実」に限定し、ステレオタイプ的な
  性格・能力の断定は書かない(groups.*.line の文言規律)。
- ペルソナ由来属性を LLM 呼び出しのゲートに使わない(呼数 k 非依存=R1)。
- 生成器の変更は同 seed バイト再現を壊さないこと(meta.json の blake2b 指紋で検知)。
