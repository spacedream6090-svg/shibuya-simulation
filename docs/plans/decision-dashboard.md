# 意思決定ダッシュボード

> 2026-08-14作成(第113後)。ユーザー要望「僕が決めることの選択肢がわからないから、選択肢と判断材料をまとめてほしい」への回答。
> **開いている判断だけ**を期限順に持つ。決まったら決定履歴([PENDING.md](../../PENDING.md) §3末尾)へ移す。各行の詳細は→列の文書。
> 読み方: 「推奨」はFableの提案。承認は「D1=b」のような短い返答で足りる。

## 期限つき(8/15〜16に決める)

> **2026-08-15 ユーザー決定**: D1=**b案**(8/15診断で呼数実測→許容ならON・準備中)/D2=**d 予備日**(できれば現実再現ランを追加——同構成seed違いにすれば seed分散の入力も兼ねられるため、その形を提案予定)/D3=**DPH-O+C+B実装**(実装レーン走行中)/U15=見送り・U1〜U14は観察方法を確定して観察する/**AGE-A〜F全部実装**+全年齢+職業=業種×役職の現実分布+ペルソナプールv2(設計レーン走行中)。

### D1. `cognition.fire` を開けるか ★最重要(=b案で準備中)
- **何が起きているか**: 承認済みの `g_update`(可塑性=g ベクトル分散拡大の主要証拠)は、発火システム `fire` がOFFのままだと**1行も出力されない**(no-op)。fireはLLM呼の発生点そのものが変わる(affects_k=True)ため勝手に開けていない。Δt短縮の科学的価値(驚き発火)もfireが前提。
- **選択肢**: (a) OFF維持=g_updateは今大会は取らない (b) **8/15診断で呼数増を実測→許容ならfire+g_updateをONで本選へ**(推奨) (c) 本選はOFF・尾部のΔt5短ランでのみON
- **判断材料**: 呼数増分は未実測(8/15診断で1時間で取れる)。副作用=朝のreply飢餓(D4)がさらに悪化する可能性。詳細: [dt-reduction-plan.md](dt-reduction-plan.md)§5・PENDING§3
- **期限**: 8/15診断中
- **準備状況(2026-08-15)**: `conf/finals_observe.yaml` の `cognition:` ブロックに **3行(watch / fire / engaged)をコメントアウト状態で用意済み**。解凍するのは下の実測を取り、判定基準を満たしたときだけ。

#### D1-a. 実測手順(1時間・mock で足りる。実LLMは任意)

```bash
# ① 呼数の増分(mock・同 seed・同 step 数。fire 以外は本選 conf のまま)
python scripts/run.py --profile conf/finals_observe.yaml \
  run.seed=42 run.n_agents=2000 run.n_steps=288 run.name=_fire_off model.backend=mock
python scripts/run.py --profile conf/finals_observe.yaml \
  run.seed=42 run.n_agents=2000 run.n_steps=288 run.name=_fire_on  model.backend=mock \
  cognition.fire.enabled=true cognition.watch.enabled=true cognition.engaged.enabled=true

# ② 集計(l1b_llm の purpose 内訳 + step あたりピーク + DPH-O の飢餓カウンタ)
python - <<'PY'
import json, pyarrow.parquet as pq
from collections import Counter
for name in ("_fire_off", "_fire_on"):
    t = pq.read_table(f"runs/{name}/l1b_llm.parquet").to_pylist()
    per = Counter(r["step"] for r in t)
    s = json.load(open(f"runs/{name}/summary.json", encoding="utf-8"))["starvation"]
    print(name, "total", len(t), Counter(r["purpose"] for r in t),
          "peak/step", max(per.values()),
          "reply_dropped", s["reply_dropped"],
          "budget", s["llm_budget_by_purpose"])
PY
```

**見るべき指標(この3つだけ)**
1. `l1b_llm` の**総件数**と **purpose 内訳**(fire が増やすのは social / novel_place / solo 等の**発火系**。plan / reflect / reply は増えない)。
2. **1 step あたりのピーク呼数**(= 壁時計の律速。`lod.budget.tiers` ON なら cap を超えない)。
3. **DPH-O の飢餓カウンタ**(`summary.json` の `starvation`): `reply_dropped` と `llm_budget_by_purpose.*.denied`。fire ON で発火の競合が増えたぶん `face`/`media` の denied が増えるのは想定内。**`reply` の denied が増えたら二層予算が効いていない**ので、そちらを先に直す。

#### D1-b. 判定基準(Δt計画の壁時計表から導出)

[dt-reduction-plan.md](dt-reduction-plan.md) §5.4 の実測外挿(25万 × 10シミュ日):

| セル | エンジン | LLM | 総壁時計 T10 |
|---|---:|---:|---:|
| 最良(c 楽観 × R_eff 楽観) | 27.6 h | 44.4 h | **72.0 h** |
| 中間(c 楽観 × R_eff 悲観) | 27.6 h | 112.1 h | **139.7 h** |
| 最悪(c 保守 × R_eff 悲観) | 52.2 h | 112.1 h | **164.3 h** |

実効枠 **W = 192 h**(保守側。楽観側は 216 h)、運用余裕 **15%**(中断・自動 resume・vLLM 再起動)。
fire ON が増やしてよい LLM 呼の割合は、**LLM 成分だけが増える**ので:

```
Δ_allow = ( W/1.15 − T10 ) / T_llm       W/1.15 = 166.96 h
  最良セル … (166.96 − 72.0)/44.4  = +214%   → 事実上ノーリミット
  中間セル … (166.96 − 139.7)/112.1 = +24.3%
  最悪セル … (166.96 − 164.3)/112.1 = **+2.4%**
```

**運用する単一の線**:
- **GO**: 8/15 実測の fire OFF 総壁時計 **T10 ≤ 140 h**(= 中間セル以下)**かつ** 呼数増分 **≤ +15%** → 3行を解凍する。
- **CONDITIONAL**: T10 が 140〜167 h → 許容増分は `(166.96 − T10)/T_llm` を**その場で計算**して比較する(最悪セルなら +2.4% が上限 = 実質 NO-GO)。
- **NO-GO**: fire OFF ですら T10 > 167 h → 開けない(選択肢 c = 尾部の短ランでのみ ON へ退避)。
- ★ `c` も `R_eff` も本選機での実測が無い(誤差 ±50%)。**8/15 に実機で測った値でこの表を引き直してから**判断する。上の 3 セルは mock 由来の外挿である。

#### D1-c. fire ON の事前チェックリスト(解凍する直前に上から順に確認)

| # | 確認項目 | 状態(2026-08-15) |
|---|---|---|
| 1 | **rotation 搬送**: 可塑性の学習状態が在場ローテーションで消えないか | ✅ 第113 で 4 族(g 族11欄 / θ倍率 / ê / credit)搬送済み。消えていたら g の分散拡大は測れない |
| 2 | **g_update の従属**: `cognition.g_update` は `fire` が ON でなければ 1 行も走らない | ✅ conf に申告済み。fire を開けて初めて `cognition_g.parquet` が生える。**生えなければプール再生成漏れ**と読む |
| 3 | **watch / engaged の従属**: どちらも `fire` ON が前提 | ✅ 3行同時に解凍する(fire だけ開けると watch/engaged は no-op のまま) |
| 4 | **DPH-B との相互作用**: fire が増やす呼は**どのレーンに入るか** | ✅ **general レーン**(発火・独り言・投稿)。`lod.budget.tiers` が ON なら reply / life の予約枠は原理的に食われない = 返事の飢餓は悪化しない。**tiers が OFF のまま fire を開けると D4 の reply 飢餓が直接悪化する** → 必ず両方 ON |
| 4b | **★正直な相互作用(fire ON + tiers ON でのみ起きる)**: DPH-B が計画/内省を繰り越すと、その個体は `plan_step`/`reflect_step` が翌 step へ立つので、`fire.note_plan_due` → `_social_via` が **繰り越した step 数だけ `cog_event{via:"plan"/"reflect"}` を出し、そのたびに周期発火を先送りする**(`fire.py:412-556`)。fire OFF の現状では 1 行も走らないので無風だが、**3行を解凍するときはここを最初に見ること**。対処案は 2 つ:(a) `max_defer_steps` を小さくして繰り越し自体を短くする (b) `note_plan_due` を「初回予約 step だけ」に絞る(= `plan_due_step` を見る 1 行)。どちらも fire を開ける判断とセットで決める | ✅ **対処済み(第121 レーンB3 β1・案(b))**。`note_plan_due` と `_social_via` が **初回予約 step だけ**を拾う(`plan_due_step` / `reflect_due_step` を見る `fire._at_first_reservation`)。内省も同じ穴を持っていたので同時に塞いだ。tiers OFF では両属性が誰にも生えない = 既定は 1 バイトも変わらない(golden 緑)。反証: 修正前のコードだと新テストが `['plan','plan','plan']` / `['reflect','reflect','reflect']` で落ちる |
| 5 | **予算外呼の消滅**: tiers ON なら plan / reflect も予算の中 = 1 step の総呼数が cap を超えない | ✅ `tests/test_dph.py::test_tiers_cap_the_per_step_calls` が機械固定 |
| 6 | **観測**: fire ON で何が枯れたかが事後に読めるか | ✅ DPH-O(`observer.starvation`)が purpose 別の denied と `reply_dropped` を summary に残す |
| 7 | **k 不変の再証明**: fire は affects_k=True なので `compute_matched` 下で k=free/k=off の呼数一致を取り直す | ⬜ 解凍を決めたら実施(型2。`docs/agent-implementation-summary.md` §120-123) |
| 8 | **事前登録**: fire ON は条件の変更なので U-10 の閾値表へ反映する | ⬜ D4 の承認時に同時に処理する |

### D2. GPU尾部(8/26-30)の使途と seed 2本目 ★量的主張の生死
- **何が起きているか**: 事前登録は「条件間差 > seed間差」を要求するが、**seed分散を測る入力ランが存在しない**。`analyze_seed_variance.py` は実装済みで入力待ち。
- **選択肢**: 尾部を (a) **seed2本目(短縮版でも可)を最優先→残りで反実仮想U15**(推奨) (b) 反実仮想U15優先 (c) Δt5感度ラン (d) 予備日として空ける
- **判断材料**: seed2本目が無いと10日ランの量的主張がほぼ全部「1標本」に落ちる。U15(checkpoint分岐再走)は分岐点さえ保全されていれば後日でも可能=保全はG2で確保済み。詳細: [unique-data-candidates.md](../research/unique-data-candidates.md) J5/J6・U15
- **期限**: 本選ラン計画確定まで(実質8/15)

### D3. 日課DPHレーンをどこまで本選前に入れるか
- **何が起きているか**: ①計画が深夜0時に無条件廃棄される一方、就寝の61%は0時以降(夜勤4,984人は毎日「計画消失後に2時間労働」)②cap拘束下で「返事」が−96%飢餓し、**L1に痕跡が残らない=観測不能**。
- **選択肢**: (a) **DPH-O(観測4点=飢餓を見えるように・世界不変)+DPH-C(日跨ぎブロック)を本選前**(推奨) (b) DPH-Oのみ (c) 全部本選後 (d) DPH-B(二層予算)まで入れる=挙動変化大
- **判断材料**: Oは純観測でリスクゼロ・Cは夜勤4,984人の実害修正。A(起床→就寝地平)とBは挙動が大きく変わるため本選後推奨。詳細: [dayplan-horizon-plan.md](dayplan-horizon-plan.md)
- **期限**: 8/15
- **実装状況(2026-08-15・ユーザー決定=O+C+B)**: **3レーンとも着地済み・全て既定OFF・本選conf でON**。
  - **DPH-O** = `observer.starvation.enabled`。新kind 3種(`reply_dropped` / `plan_skipped` / `reflect_dropped`)+ `summary.json` の `starvation` ブロック(wrap_clipped・plan_expired_awake・purpose別の予算許可/拒否)。**L2 へは列を足していない**(`observer/aggregate.py` は metrics_spec の凍結対象)。観測ON/OFFで行動列・LLM呼数・世界の最終状態が完全一致することをテストが機械固定。
  - **DPH-C** = `planning.day_plan.wrap_blocks`。24-29時表記の受理 / `end<start → +1440` / 計画の原点からの絶対分で窓判定 / 夜勤骨格 18:00→02:00。**朝の呼数もプロンプトも1バイト不変**(地平=DPH-Aには触っていない。前日の計画は自分の日跨ぎブロックが伸びている間だけ生き延びる)。
  - **DPH-B** = `lod.budget.tiers.enabled`。life(plan+reflect)/ reply / general の3レーン+FIFO繰り越し+骨格フォールバック。**総呼数は増えない**(`used <= cap` を常に満たす)。実測: 60体×144step・cap4 で返答保証の成立率 **2.6% → 100%**(落ちた返事 74件 → 0件)・総呼数 502 → 218。
  - **A(起床→就寝地平)は未着手**(今回対象外)。P1(0時失効)は観測だけ入った = `plan_expired_awake` で件数が読めるようになった(3日60体ランで140個体×step / 39個体×日)。
  - **★実装中に見つけた即死バグ(修正済み)**: 新 kind は `observer/causality.py` の `CAUSE_OF_KIND` にも登録しないと `logger.log()` が **KeyError で即死**する(未分類を黙って unknown にしない設計)。本選 conf は `observer.causality.enabled: true` なので、既定OFFのテストだけ緑にして通すと **最初の飢餓イベント1件で10日ランが落ちる**ところだった。3種を分類(`reply_dropped`/`reflect_dropped`=boundary=実験者側の予算上限が落とした / `plan_skipped`=device=ルールが世界状態に反応)+「因果台帳ON×観測ON×cap拘束で実際に飢餓イベントが出て落ちない」スモークをテスト化。**新 kind を足すときは schema と causality の 2 箇所**が作法。

### D4. U-10 事前登録の閾値承認(既存・ユーザー指定=本番直前)
- [stationarity-preregistration.md](stationarity-preregistration.md)。8/16ラン開始直前に承認依頼します。

## 方針(急がないが決めると先が変わる)

### D5. Δt: 10分維持 vs 5分
- **推奨=10分維持**。実測判断表([dt-reduction-plan.md](dt-reduction-plan.md)§5): エンジン×1.65で最悪セルの壁時計余裕が消える・現ONセット(fire OFF)では思考層の利得ゼロ・**凍結解析器2本がΔt≠10で静かに壊れる**。D1でfireを開けるなら価値が復活するが、その場合も「本線Δt10+尾部Δt5短ラン」(D2-c)が安全。

### D6. 年齢AGEレーン
- **推奨=本選後**(AGE-Aはプール100万の再生成が必要=8/15前は危険)。現状: 0-14歳0.259%(実10.03%)・「15歳」に4.08%集積・年齢は思考量に一切効かない。取得不能とされていた実センサス表は**取得可能と判明済み**なので、本選後すぐ着手できる状態。詳細: [age-diversity-plan.md](age-diversity-plan.md)(レーンA〜F・最小対=A+C)

### D7. 賃金の残り2点(記録済み・異論あれば)
- 家賃=実引落日(27日/末日)が10日窓に入らないため引落ゼロ。**savings_rate 0.555の帯超過は「給料日直後だけを切り取った窓」の測定アーティファクトとして記録**(機構は触らない判断済み)。最低賃金の床に12.4%が同一額集積(現実にも最賃集積はある)。

### D8. visit_purpose構成比のPT較正(小・任意)・policy_cache保存(8/15のresume呼数差実測後)・NEW-5(パイロット後)・DT-U2 UE5動画(保留)
- 従来どおり。

## 走行中(決定不要・完了報告を待つだけ)

- **POP案A=着地済み**(フルゲート5563緑・+35テスト)。出生=finals ON(リスクゼロ・10日で約3.4件=現実の0.57倍)。**転出/転入=8/15リハーサル(1〜2日ラン+現実レート7.8/8.4件日との照合)後に1行ON**(PRES-A2と同じ実測ゲート方式・転出量が25万規模で未実測のため)。転出は「滞納+失職=1日目・縁5本=400日でも発火せず」の個体応答として実装済み
- **第3波小粒**(判断不要と事前承認済みの範囲): L5タクシー/配信者/議員の日給0・is_foreign/language不一致・J1共在ペア上限8→24(動力学不変の機械検収付き)・finals未宣言トグル8件の宣言・beliefs --bin-steps
- **所有権O2/O4/O5・アクターモデル残**(店主行為化・GTFS実発車・PoA観測)——第3波で着手し、8/15検収に間に合った分だけ投入(「できれば本線前」の運用)

## 決まったこと(直近・詳細はPENDING§3決定履歴)

2026-08-14: GTロガー全部実装(第113)/OBS承認=g_update ON/b2b=部分納品+分散(第113)/Δt=本番1本のみ・5分案は計画/POP=案A試行/痩せ全数根治+賃金多様性(第112)。
