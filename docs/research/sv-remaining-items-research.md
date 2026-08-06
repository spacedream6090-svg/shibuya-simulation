# SV-U1 残 13 項目 実装前リサーチ — S-05〜S-15 / S-17 / S-18

**対象**: `docs/research/llm-social-sim-survey.md` §3 のうち、第 92 バッチ(◎5 件 = S-01/02/03/04/16)で実装済みの分を除いた **13 項目**。
**ユーザー決定(2026-08-06)**: 「SV-U1 に書いてある内容は積極的に採用してほしい。書いてある項目についてのリサーチは怠らないように。」= ○/△ を含む残り全件を**採用**する方針。
**目的**: 実装に入る前に、各項目の (i) 具体的な実装先、(ii) 凍結資産(`metrics_spec_hash` = `SPEC_FILES` 14 本)への抵触有無と回避策、(iii) 一次文献の根拠、(iv) フリーズ(8/12–14)前後どちらに置くかを確定する。
**アクセス日**: 全リンク **2026-08-06**(§4 に一覧)。
**制約**: R1 ドクトリン(既定 OFF / golden L1 バイト一致 / no-fingerprint / `metrics_spec_hash`)。本選フリーズ 8/12–14・10 日ラン 8/16〜。事前登録は U-10 承認前 = 追記自由(承認対象マーク)。
**本文書はコードを 1 行も変更していない**(調査のみ・コミットもしていない)。作法の前例は `docs/research/sv-items-research.md`(◎5 件)。

---

## 0. 3 行サマリ

1. **★ 残 13 項目のうち 12 項目は `src/` と `conf/` を 1 バイトも触らない = 本選フリーズの対象ではない。** 凍結 14 本のうち解析側は `analyze_beliefs.py` / `analyze_norms.py` / `analyze_specialization.py` / `diagnose_stationarity.py` の**4 本だけ**で、S-06 / S-09 / S-13 が触れたくなる相手はこの 4 本に集中している。回避策は 3 通りとも既に repo 内に前例がある(**新規スクリプトを立てる** / **凍結ファイルから import する**(逆方向の依存は禁止・ハッシュは不変)/ **対応表を事前登録へ置く**)。フリーズ前に急がねばならないのは実質 **(a) 事前登録・報告テンプレへの追記(U-10 承認パッケージ)** と **(b) S-11(唯一 `src/` に触る)** の 2 つだけである。
2. **★ 実査で「ただで手に入る資産」が 3 件見つかり、S-09 / S-11 / S-12 の実装コストが当初見積りより大幅に下がった。** ①`transmission` イベントの payload に **`channel` フィールドが既にある**(値は `face` / `dm` / `sns` / `search` / `news` の 5 種)ため、S-12 の offline/online 分離は**新規計装ゼロ**。②`scripts/analyze_communities.py` が既に Palla 2007 のライフサイクル語彙・窓間 Jaccard 安定度・`degree_gini` を出しているので、S-09 の **mode 軸(static/dynamic)は実質実装済み**。③`scheduler.py` の検索エンジンが**すでに `len(item.transmissions)`(拡散回数)をプロンプト材料に入れている**(L2516–2521)ため、S-11 の「送り手の伝播実績を受け手に見せる」は**新規状態変数ゼロ**で書ける。
3. **★ ただし S-11 だけは、文献が「本選前に入れてはならない」と言っている。** Salganik, Dodds & Watts 2006(Science 311:854)は、まさに「過去の成功を可視化する / しない」を実験操作した研究で、**可視化した条件では不平等(Gini)と同時に "予測不能性" が上がる**ことを示した。本プロジェクトの事前登録は前文 ④(a) で「**条件間差が seed 間差を上回らなければ結論を出さない**」を反証条件に据えているので、S-11 を本番で ON にすると **seed 間分散が構造的に増え、主結論の検出力を自分で削る**。加えて `sim.items` の全走査 O(items × transmissions) が毎材料集めで走るため、25 万体では PENDING §4 の既知課題(`Item.transmissions` 上限なし)に直撃する。→ **S-11 は本選後(SV2-C)を強く推奨**。

---

## 1. 項目別表

### 1.0 凍結の実態(全項目の前提・実査結果)

`SPEC_FILES` の定義は `src/society/observer/metrics_spec.py` L51–69。正規化は **BOM 除去 + 改行 LF 統一のみ**で、**コメント除去も空白正規化もしない**(L72–76)。したがって**コメント 1 文字・docstring 1 文字でもハッシュが動く**。

| # | 凍結ファイル | 本件との関係 |
|---|---|---|
| 1–9 | `observer/{aggregate, measure, stream, echo, norms, silence, deviation, structure, initial_frame}.py` | S-09 の中心性を L2 列にしたくなるが**禁止**(→ 解析側へ) |
| 10 | `truth_ledger.py` | S-11 の信念台帳。**読むだけなら可**(IF-B の前例) |
| 11 | `scripts/analyze_beliefs.py` | 触らない |
| 12 | `scripts/analyze_norms.py` | **S-13 が触れたい相手。docstring も禁止** |
| 13 | `scripts/analyze_specialization.py` | **S-09 が触れたい相手** |
| 14 | `scripts/diagnose_stationarity.py` | **S-06 が触れたい相手** |

**凍結**外**であることを実査で確認した解析器**: `analyze_g.py` / `analyze_weak_ties.py` / `analyze_groups.py` / `analyze_founders.py` / `analyze_communities.py` / `analyze_structure.py` / `judge.py` / `calibrate_report.py` / `build_persona_pool.py` / `panel_stats.py`。**これらは自由に改修してよい**。

**★ 回避策の設計原則(本文書の中核)**:
> **新規スクリプトが凍結ファイルを `import` するのは安全**(ハッシュはファイル内容のみに依存し、import は内容を変えない。凍結 4 本はすべて `if __name__ == "__main__":` ガードを持つので副作用なく import できる)。**逆に、凍結ファイルが非凍結ファイルを import するのは禁止**(凍結されていないコードの変更が凍結指標の値を静かに変える = ハッシュが嘘になる)。`diagnose_stationarity.py` が `analyze_weak_ties.py` の関数を「import せず複製」しているのは、まさにこの逆方向を避けるためである(同 L174–175 に明記)。
> → **S-06 の新スクリプトは `diagnose_stationarity.py` から `paired_signflip_tvd` / `paired_dz` / `_r` を import してよい。複製する必要はない。**

### 1.1 項目別一覧表

| 項目 | 実装内容(どこに何を) | 凍結抵触と回避策 | コスト | 推奨 |
|---|---|---|---|---|
| **S-05** seed 間分散の分散分解 | **新規 `scripts/analyze_variance.py`**。`panel_stats.py` の純関数(`_parse_cond_seed` / `t_ci` / `perm_test_paired` / `bh_fdr`)と `analyze_sweep.py` の seed 階層ブートストラップを import。全主要指標に対し **V_条件 / V_seed の 2 成分分解 + 分散比 + 「条件差 > seed 差」ゲートの機械判定**を出す | **抵触なし**(scripts 新設)。`analyze_g.py` の既存分解は**別物**(単一ラン内の**個体**横断分散を g0 と Δg に分ける)ので、拡張ではなく**新設**が正しい | 中 | **フリーズ前(最優先)**。事前登録の前文 ④(a) が既にこの判定を反証条件として約束済み = **装置が無いと反証条件が判定不能**。加えて必要 seed 本数がラン計画に影響する |
| **S-06** 個体レベル長期一貫性 | **新規 `scripts/analyze_persona_consistency.py`**。`diagnose_stationarity.py` を **import** して純関数を再利用。個体別に日ペア TVD を出し、**個体内一貫性 / 個体間差異の比**を 1 数値に | **抵触なし**(import は内容を変えない)。★ただし**交換単位が変わる**(現行は「エージェント」= Farine & Carter の置換前提。個体別化すると「日」になる)ので、置換検定の帰無仮説を**別途明記**する必要あり | 中 | **本選後**でよい(10 日ランの L1 さえ残れば事後解析で完全に等価)。ただし装置はフリーズ前に書いておくと安い |
| **S-07** LLM-judge 根拠の補強 | **`scripts/judge.py` の `_write_report` に `lines.append(...)` を 1 行**。挿入点は L404–408 の「R4(循環の防壁)」ブロッククォート末尾が最有力 | **抵触なし**(`judge.py` は `SPEC_FILES` 外) | **極小** | **フリーズ前** |
| **S-08** アウトライア非優遇の宣言 | **文書のみ**。`docs/plans/observation-report-template.md` **§7.2 が既に空枠として存在**(L227–232)。事前登録の前文 ③(e) にも既に 1 行入っている → **本文を埋めるだけ** | 抵触なし | **極小** | **フリーズ前** |
| **S-09** 組織観測 mode×structure×role | **新規 `scripts/analyze_org_form.py`**。`analyze_communities.py` の分割(Louvain seed=0)と `analyze_founders.py` の `betweenness_bfs` を再利用し、4 軸を出す(§3.3 参照) | **抵触なし**(`analyze_specialization.py` は**触らない**。新スクリプトで並置) | 中〜大 | **本選後**(事後解析で等価)。ただし**中心性指標の選択は事前登録に書く**べき(後出しの指標選択は査読で最も突かれる) |
| **S-10** MAS 失敗様式(MAST 14) | **解析のみ**。L1 イベントから判定可能な 14 様式の対応表(§3.1)を作り、`analyze_org_form.py` の 1 セクションか事前登録の付録に | 抵触なし | 小(対応表)〜中(判定実装) | **フリーズ前に対応表(文書)/ 本選後に判定実装** |
| **S-11** 送り手の影響力 | **`src/` に触る唯一の項目**。`perception_contract.py` に 1 欄 + `deliberate.py` に 1 行 + `scheduler._gather_material` に計算 1 か所 + `registry.py` に `_f()` + conf トグル(既定 OFF) | 抵触なし(`SPEC_FILES` 外)。**★契約列挙テストの追随は不要**(`_gather_material` 側に置けば IF-D `trace_line` と同型。`_llm_speak` 側に置くと IF-B `reject_line` と同型で 2 テスト更新が必須) | **大** | **本選後(SV2-C)**。理由は §0-3 と §1.2 |
| **S-12** offline / online 二層 | **`scripts/analyze_weak_ties.py` を直接改修**(凍結外)。**★`transmission` payload の既存 `channel` フィールドを使う**(新規計装ゼロ) | 抵触なし。★ただし `measure.communities()`(凍結)は speak+dm 混合固定 → **層別コミュニティが要るなら LPA を本スクリプトへ複製**(`diagnose_stationarity` の前例と同じ流儀) | 小〜中 | **フリーズ前**。事前登録 §3-F の **F7(次数分布の裾)を層別にする**なら指標定義の追記が要る = U-10 承認パッケージに間に合わせる必要がある |
| **S-13** 規範ライフサイクル対応表 | **文書のみ**。事前登録 §3-E の直後に対応表(§3.4)を追加。**`analyze_norms.py` は docstring も触らない** | **★最重要の回避**: `analyze_norms.py` は凍結 12 番。**コメント 1 文字でハッシュが動く**ので、サーベイが提案した「docstring に 1 表」は**採ってはならない** | **極小** | **フリーズ前** |
| **S-14** 人口の周辺分布再現誤差 | **新規 `scripts/report_population_fit.py`**(または `calibrate_report.py` に 1 節)。`data/shibuya_population.json` の目標 share と `data/persona_pool/L1/part-*.jsonl` の実績を突合し **SRMSE / TAE / %誤差**の表を出す | 抵触なし。**★`run_manifest`(= `src/society/observer/manifest.py`)に載せると `src/` を触る = フリーズ対象**になる → **報告書側に置く**のを推奨(受け皿は `observation-report-template.md` §4.4 に既に空欄で存在) | 小 | **フリーズ前**(安い・差別化が大きい) |
| **S-15** sycophancy 片側解釈宣言 | **文書のみ**。**★重複確認の結果**: 事前登録の前文 ③(c) に既に**片側解釈の全文が入っている**(第 92 バッチ B1)。報告テンプレ §7.3 も空枠で存在 → **残作業は §7.3 を埋めることだけ** | 抵触なし | **極小** | **フリーズ前** |
| **S-17** 境界アーティファクト検査 | **報告テンプレ §7.4(既に空枠あり)を埋める + 検査手順を明文化**。三つ組比較(`llm_off` / 中間条件 `propagation_off` / 本番)。**解析スクリプトは不要**と判定(§1.3) | 抵触なし | 小 | **フリーズ前**(ただし**3 条件を回す**というラン計画への含意があるので、フリーズ前に確定が必要) |
| **S-18** ステレオタイプ増幅検査 | **新規 `scripts/analyze_stereotype.py`**(読み取り専用・1 回限り)。L1 の `speak.text` / `sns_post.text` / `dm.text` と `agents.json` の属性を突合し、**Monroe et al. 2008 の重み付き log-odds ratio(informative Dirichlet prior)+ |z|>1.96** で属性別の過剰出現語を出す(§3.2) | 抵触なし。★`analyze_specialization.py` が同じ 3 種のテキストを読むが**触らない**(トークナイザは文字 n-gram を**複製せず自前で持つ**。あちらは語彙リテラルゼロ設計、こちらは語を出すのが目的で要件が違う) | 中 | **フリーズ前に装置 / 本選後に本番 L1 へ適用**。自然造語の主張の防壁として重要度が高い |

### 1.2 S-11 の詳細(唯一 `src/` に触る項目・実査結果)

**Perception 型**: `src/society/cognition/perception_contract.py` L82–235 の `@dataclass(frozen=True)`、現在 **54 欄**。対応表は `_KW_FIELDS`(L254–312)が唯一の源で、`_self_check()`(L460–475)が **import 時に 1 回**整合を検査する(書き忘れると全テストが collect 段階で `RuntimeError`)。

**★ 契約列挙テストの追随が要るかは「どこで材料を作るか」だけで決まる**(IF-B と IF-D の差分を実査した結論):

| 前例 | 配置 | 契約列挙テスト |
|---|---|---|
| IF-B `reject_line`(446ff12) | `_llm_speak` が**後から** `material[...] =` で足す | **追随必須**。`tests/test_physics_zones.py` L666 と `tests/test_traces.py` L716 の「後から足す 4 欄」→「5 欄」に書き換えた |
| IF-D `trace_line`(6c404cd) | **`_gather_material` が集める側** | **追随不要**。代わりに自前の宣言テスト(`test_traces.py` L694–697)を新設し、既存 5 欄集合を**そのままコピーして「変わらないこと」を再固定**した |

→ **S-11 は `_gather_material` 側(IF-D 同型)に置ける**。送り手の伝播実績は「材料集めの時点で確定している情報」だからである。よって**契約列挙テストの追随は不要**で、本選前でも構造的には安全に足せる。

**新規状態変数ゼロで計算できるか → できる。ただし「ID を持つ情報オブジェクト」に限る。**

| 問い | 既存構造だけの式 | 前例 |
|---|---|---|
| A が言い出したモノ | `[i for i in sim.items.items.values() if i.creator == A.id]` | `scheduler.py` L2516–2519 が `item.creator` を既に読む |
| それは何人に届いたか | `len({to for (_s,_f,to,_c) in i.transmissions})` | **`scheduler.py` L2521 が `len(item.transmissions)` を既にプロンプト材料に入れている**(検索エンジンの結果文) |
| A が中継役として広めた回数 | `sum(1 for i in ... for (_s,f,_t,_c) in i.transmissions if f == A.id)` | 同上の派生 |

`ItemStore`(`src/society/observer/provenance.py` L15–46)は **conf ゲートなしで常時 ON**(`simulation.py` L209)であり、`Item.creator` と `Item.transmissions`(= `(step, from, to, channel)` の列)が伝播木そのものである。

**正直な限界(4 件)**:
1. **素の発話テキストには item_id が無い**。追えるのは語彙/ラベル(常時)と噂 Item(IF-C・既定 OFF)だけで、「A が昨日した雑談が広まったか」は**原理的に追えない**。
2. **受け手側に送り手 id が残る構造は既定 OFF の 2 つだけ**(`truth_ledger._fact_beliefs["from"]` / `gossip._gossip_heard`)。`rumors` の `src` は源イベント種であって送り手ではなく、`labels.heard_counts` は回数のみ。
3. **索引が無い**。「送り手 A で引く」には全 Item 走査 O(items × transmissions)。**タリーを持てば新規状態変数**になり、`PENDING.md` L50 の既知課題「④`Item.transmissions` 上限なし(25 万ではホット噂 O(N))」に直撃する。
4. `build_prompt` は `sim` を読めない(`tests/test_perception_contract.py` L440–449 が AST で固定)。計算は必ず `_gather_material` 側。

**★ 文献が示す「本選前に入れない」根拠**(§3.5 に詳述): Salganik ら 2006 は「過去の成功の可視化」を実験操作し、**社会的影響を強めるほど不平等と "予測不能性" が両方上がる**ことを示した。S-11 は本シムにおける**まさにその操作**であり、ON にすると seed 間分散が増える方向に働く。事前登録の反証条件 ④(a)(条件差 > seed 差)と正面から衝突する。

### 1.3 S-17 に解析スクリプトが要るか → **不要と判定**

境界アーティファクト検査は「新しい量を測る」ものではなく「**既にある 3 条件の出力を、決められた順序で読む**」手順である。必要なのは以下 3 つで、いずれも既存資産で足りる:

1. **三つ組の比較対象**: `ablate.llm_off`(ルール層のみ)/ 中間条件(`ablate.propagation_off` または `ablate.context_sever` などプラセボ 3 種)/ 本番。→ 既存 ablate 枠。
2. **比較の実行器**: `scripts/compare_runs.py`(CRN ペア比較・置換検定・BH-FDR・効果量)が既にある。指標の比較そのものはこれで足りる。
3. **判定規則**: 「`llm_off` にも本番にも**無く**、中間条件でのみ現れる構造」= 境界アーティファクト候補。これは**規則であってコードではない**ので、報告テンプレ §7.4 に文章で固定するのが正しい。

→ **やること = §7.4 を埋める + 事前登録の反証条件 ④(f)(既に境界アーティファクトを列挙済み)と接続する**。ただし**「3 条件を回す」というラン計画への含意**があるので、フリーズ前に確定が必要。

### 1.4 S-12 の実装先(実査で確定した最短経路)

**★ 新規計装ゼロ**: `src/society/observer/schema.py` L29 —
```
register_event_kind("transmission",  "★伝播系譜: item が from→to へ伝わった(ユーザー指定ログ){item_id, from, channel}")
```
`channel` の実値は `scheduler.py` の `_hear_words` 呼び出し 5 か所から確定:

| channel | 呼び出し元 | 層 |
|---|---|---|
| `"face"` | L3096(対面会話) | **offline** |
| `"dm"` | L2966 | **online(対人)** |
| `"sns"` | L2605(タイムライン閲覧) | **online(対人)** |
| `"search"` | L2581(`from_id = -1`) | ★**媒体層**(送り手が人でない) |
| `"news"` | L2654(`from_id = -1`) | ★**媒体層** |

→ **二層(offline/online)では尽くせない**。`search` / `news` は送り手が `-1` で、対人ネットワークの辺にならない。**「offline / online / 媒体」の三層として宣言する**のが正直な設計であり、これ自体が報告に書く価値のある発見である(サーベイ §5.1.2 は offline/online の二分しか提示していない)。

**改修点**(`scripts/analyze_weak_ties.py`・凍結外):
- L62–77 `build_weighted_graph` を channel 別に(`speak.hearers` → offline / `dm.to` → online)。
- L238 の `params.channels` ハードコード文字列(`"speak(speaker->hearers) + dm(sender->to)"`)を層別に。
- L181 の `m.communities()` は**凍結ファイル内で speak+dm 混合固定**。混合分割を共通の参照として使うなら変更不要。層別コミュニティが要るなら **LPA を本スクリプトへ複製**する(凍結ファイルは変更しない)。
- ★**`sns_post` / `sns_read` は現状どちらも辺に入っていない**(`sns_read.authors` から reader への辺を張っていない)。= **現状の "online" は DM のみで過小評価**。ここを直すかどうかは事前登録に明記が要る。
- Granovetter 突合(L222–231)の `transmission` は `channel` を持つので、**採用の帰属を層別にできる**(現行は層無区別)。

**事前登録への影響**: §1.2 が「`speak` と `dm` を同一チャネルとして 1 つのグラフに合成」と明記しているので、**追記(承認対象)が必須**。§3-F の F7(次数分布の裾)も層別にするなら判定枠が変わる。

---

## 2. 実装バッチ分解案

### 2.1 分解と順序

| バッチ | 項目 | 変更範囲 | `metrics_spec_hash` | golden L1 | `src/`・`conf/` | コスト | 推奨時期 |
|---|---|---|---|---|---|---|---|
| **SV2-A** | **S-07 / S-08 / S-13 / S-15 / S-17**(+ S-05・S-12 の事前登録追記) | **文書 + `judge.py` に 1 行**。`docs/plans/stationarity-preregistration.md` / `docs/plans/observation-report-template.md` | 不変 | 不変 | **ゼロタッチ** | **極小** | **フリーズ前・即** |
| **SV2-B** | **S-05 / S-12 / S-14 / S-18 / S-06 / S-09 / S-10** | **`scripts/` のみ**。新規 5 本(`analyze_variance.py` / `analyze_persona_consistency.py` / `analyze_org_form.py` / `analyze_stereotype.py` / `report_population_fit.py`)+ `analyze_weak_ties.py` 改修 | 不変 | 不変 | **ゼロタッチ** | 中〜大 | **フリーズ非対象**。S-05/S-12/S-14 はフリーズ前、S-18/S-06/S-09/S-10 は本選後でも等価 |
| **SV2-C** | **S-11** | `perception_contract.py` + `deliberate.py` + `scheduler.py` + `registry.py` + `conf/config.yaml` + テスト | 不変 | **不変(既定 OFF)** | **触る** | 大 | **本選後** |

**★ 順序の根拠**:
- **SV2-A → SV2-B** は「何を測ると事前に宣言してから測る」順序。事前登録は U-10 承認前なので**今が追記の窓**であり(承認後は §7 変更履歴への記録が義務)、S-05 の判定規則・S-12 の層定義・S-09 の中心性指標選択を**先に凍結**しないと、後出しの指標選択と読まれる。
- **SV2-B → SV2-C** は「`src/` を触らない仕事を先に全部終える」順序。SV2-B は 1 バイトも `src/` を触らないのでフリーズ日程と独立に進行でき、SV2-C だけが本選ランの挙動を変えうる。
- **SV2-B 内の推奨順**: `analyze_variance.py`(S-05・反証条件が依存)→ `analyze_weak_ties.py` 改修(S-12・事前登録の指標定義に影響)→ `report_population_fit.py`(S-14・最も安い)→ `analyze_stereotype.py`(S-18)→ `analyze_org_form.py`(S-09 + S-10 の判定)→ `analyze_persona_consistency.py`(S-06)。

### 2.2 各バッチの R1 チェックリスト

**SV2-A(文書)**
- [ ] 事前登録の追記は**節番号を持たない前文か、既存 §1〜§7 の末尾**に置く(既存参照を壊さない。前文「主張の境界」が既にこの流儀を採用済み)
- [ ] 新規追記はすべて **「承認対象」マーク**を付ける(U-10 パッケージに合流)
- [ ] **`analyze_norms.py` を開かない**(S-13。docstring 1 文字でハッシュが動く)
- [ ] `judge.py` の 1 行は**静的文字列のみ**(実験条件・数値をゼロに)

**SV2-B(解析スクリプト)**
- [ ] `src/` と `conf/` に 1 バイトも触れていないこと(= `git diff --stat` が `scripts/` と `docs/` に閉じる)
- [ ] `metrics_spec_hash` 不変の確認(= `SPEC_FILES` 14 本に触れていないこと)
- [ ] 凍結ファイルからの **import は可、凍結ファイルへの依存追加(逆方向)は不可**
- [ ] 依存は `numpy` / `pyarrow` / `networkx` / 標準ライブラリのみ(**`scipy` は依存に無い** — `analyze_communities.py` L349 が明記。`nx.pagerank` が使えない理由もこれ。log-odds も自前実装が要る)
- [ ] 決定論(ノード/エッジはソート順・seed 固定・タイは最小 id・`json.dumps(sort_keys=True, ensure_ascii=False)`)
- [ ] データが無いときは**捏造せず明示終了**(`analyze_groups.py` の流儀)

**SV2-C(S-11)**
- [ ] `conf/config.yaml` の既定 OFF + `src/society/registry.py` に `_f()` エントリ(`tests/test_registry_modes.py` が全 bool リーフを走査するので未申告は CI で落ちる)
- [ ] **`_gather_material` 側に配置**(契約列挙テスト追随不要 = IF-D 同型)
- [ ] OFF 時 golden L1 バイト一致 + プロンプト文字列バイト一致
- [ ] `fingerprint_risk` の判定: **観測が世界を変えるので `known` ではなく、これは「機構」であって「観測」ではない**。`affects_k` の判定と併せて registry に正直に書く
- [ ] `_KW_FIELDS` と `Perception` の**両方**に書く(片方だけだと import 時 `RuntimeError`)
- [ ] `build_prompt` のシグネチャにも足す(`tests/test_perception_contract.py` L452 が `PROMPT_KEYWORDS <= args` を検査)
- [ ] 走査コストの実測(25 万体で `sim.items` 全走査が成立するか)。成立しないなら**本項目は不採用**と正直に書く
- [ ] `ask-before-extending`: 着手前にユーザー合意

### 2.3 やらないことの明記(ゴールドプレーティング防止)

- **`analyze_norms.py` / `analyze_specialization.py` / `diagnose_stationarity.py` / `analyze_beliefs.py` を開かない**(S-06/S-09/S-13。読むだけの `import` は可、**エディタで開いて保存するのも危険**)
- **`observer/aggregate.py` に中心性の L2 列を足さない**(S-09。凍結 1 番)
- **`run_manifest` に人口誤差を足さない**(S-14。`src/` を触るとフリーズ対象になる。報告書側で十分)
- **Gini の 6 個目の実装を書かない**(既存 5 実装 + `model_battery/metrics.py::cv()`)
- **中心性の 3 個目の実装を書かない**(degree = `measure.py` L866 / `stream.py` L371 / `analyze_structure.py` L287、betweenness = `analyze_founders.py` L300 `betweenness_bfs`。**eigenvector は repo 内に存在しない** = 新規に要るのはこれだけ)
- **S-18 で語彙リストをコードに書かない**(`analyze_specialization.py` の「語彙リテラルを 1 語も置かない」設計と、`labeling.norm_stage` の「マーカーは conf が唯一の源」の掟に整合させる。Marked Personas は**レキシコン不要**の手法なので、これは文献側の設計とも一致する)
- **S-11 で伝播実績のタリー(索引)を作らない**(新規状態変数になる。作るなら別項目として再提案)

---

## 3. 文献確認結果

### 3.1 S-10: MAST — Cemri et al. 2025 の 14 失敗様式(一次取得)

**Cemri, M., Pan, M. Z., Yang, S., Agrawal, L. A., Chopra, B., Tiwari, R., Keutzer, K., Parameswaran, A., Klein, D., Ramchandran, K., Zaharia, M., Gonzalez, J. E. & Stoica, I. (2025). *Why Do Multi-Agent LLM Systems Fail?* arXiv:2503.13657.**
7 フレームワーク・200+ タスク・1,600+ 実行トレースを 6 名の専門アノテータ(**アノテータ間一致 κ = 0.88**)で Grounded Theory 分析。失敗率は **41〜86.7%**。

| FC | 群 | 割合 | FM | 名称 | 定義 | 割合 | **本シムの L1 から判定可能か** |
|---|---|---|---|---|---|---|---|
| **FC1** | Specification issues(仕様の不備) | **41.77%** | FM-1.1 | Disobey task specification | 指定された制約・要件に従わない | 10.98% | **△** `parse_action` が有限語彙 `KNOWN_ACTIONS` で弾く = 「不正行為の試行」は L1 に残らない。`free_action{what, report}` の逸脱率か `undefined_action_rate`(L2)で代理可 |
| | | | FM-1.2 | Disobey role specification | 定義された責務・制約に従わない | 0.5% | **○** `agents.json` の `occupation` / `group_found{purpose}` と実行動の乖離。`deviation.py`(凍結・**読むだけ**)のペルソナ逸脱率が既存 |
| | | | FM-1.3 | Step repetition | 完了済みステップの不要な反復 | 17.14% | **◎** `observer.echo`(L2 常設 5 列)の自己反復と `reg_ngram_repeat_rate` がそのまま。**最頻の失敗様式が既に測れている** |
| | | | FM-1.4 | Loss of conversation history | 予期せぬ文脈切り詰め・直近履歴の無視 | 3.33% | **◎** `dialog_history` 欄の有無と発話内容の不整合。`analyze_firing.py` の発火連鎖グラフで A→B の断絶として検出可 |
| | | | FM-1.5 | Unaware of termination conditions | 終了すべき条件を認識しない | 9.82% | **◎** 第 87 `engaged` のターン上限 12 到達件数(= CAMEL の無限 goodbye ループが根拠)。`joint_activity` の未終結 |
| **FC2** | Inter-agent misalignment(エージェント間の不整合) | **36.94%** | FM-2.1 | Conversation reset | 対話の予期せぬ再開始 | 2.33% | **○** `speak` の話題トークン列が直前と非連続 + `relation_tier` 不変 |
| | | | FM-2.2 | Fail to ask for clarification | 不明確な情報に対し追加情報を求めない | 11.65% | **△** 疑問形の検出が要る(表層一致 = `norm_stage` と同じ弱さ)。**IF-B の `reject_line`(拒否理由の可視化)が最も近い装置** |
| | | | FM-2.3 | Task derailment | 意図した目的からの逸脱 | 7.15% | **◎** `group_found{purpose}` / `proposal{text}` の目的語彙と、その後のメンバー発話語彙の JS ダイバージェンス |
| | | | FM-2.4 | Information withholding | 他者に影響する重要情報を共有しない | 1.66% | **◎** `truth_ledger`(凍結・**読むだけ**)の `beliefs_of` に持っているのに `belief_transmit` しない件数 |
| | | | FM-2.5 | Ignored other agent's input | 他者の入力・提案を無視 | 0.17% | **◎** `joint_invite{verdict}` / `proposal_support` の不応答、`speak.hearers` に居るのに応答なし |
| | | | FM-2.6 | Reasoning-action mismatch | 推論と実行の不一致 | 13.98% | **◎★** **IF-A の `(llm_call_id, role)` 刻印(PROV `wasInformedBy` 辺)が、まさにこれを測る装置**。朝計画(`plan`)の内容と当日の実行イベントの乖離 = `day_plan` の `plan_exception` / 再計画率が既存 |
| **FC3** | Task verification(検証の失敗) | **21.30%** | FM-3.1 | Premature termination | 目的未達で対話・タスクを終える | 7.82% | **◎** `venture_close` / `group` の消滅(`analyze_communities.py` の Palla ライフサイクル "死")が到達前に起きた件数 |
| | | | FM-3.2 | No or incomplete verification | 成果の確認・検証の省略 | 6.82% | **◎★** **verify モードの `truth_ledger` がまさにこれ**。`verified=False` のまま行動に使われた信念の割合 |
| | | | FM-3.3 | Incorrect verification | 重要情報の検証が不適切 | 6.66% | **◎** `truth_ledger` の `verified=True` かつ真値と乖離した件数(台帳は真偽を持つ) |

**★ この表から得られる知見**: 14 様式のうち **10 件が既存 L1/L2 から直接判定可能**、うち 4 件(FM-1.3 / FM-2.6 / FM-3.2 / FM-3.3)は**既に専用の装置を持っている**。合計 41.4% を占める上位 4 様式(FM-1.3 17.14%・FM-2.6 13.98%・FM-1.1 10.98%・FM-2.2 11.65%)のうち 2 つが ◎ である。**「組織形成の失敗の内訳」は MAST の語彙で書ける**。

**注意(正直な限界)**: MAST は**タスク遂行型 MAS**(与えられたタスクを協働で解く系)のトレースから帰納された分類であり、本シムは**タスクを与えていない社会シム**である。「specification(仕様)」に相当するものは本シムでは**エージェントが自分で言い出した目的**(`group_found{purpose}` / `proposal{text}`)しかない。→ **対応表には「本シムでの仕様とは何か」を 1 行定義してから使う**こと。この読み替えを書かずに 14 様式を当てはめると、査読で「タスク型の分類を社会シムに機械適用した」と読まれる。

### 3.2 S-18: Marked Personas の手法(一次確認)

**Cheng, M., Durmus, E. & Jurafsky, D. (2023). *Marked Personas: Using Natural Language Prompts to Measure Stereotypes in Language Models.* ACL 2023, pp. 1504–1532. arXiv:2305.18189.**

**手法(Marked Words)**:
1. **社会言語学の markedness(有標性)**に基づく。「有標な群」(marked)と「無標の既定群」(unmarked default)のペルソナ文を生成し、**両者を区別する語**を統計的に同定する。**レキシコンもラベル付けデータも不要**。
2. 統計量 = **重み付き log-odds ratio + informative Dirichlet prior**(= **Monroe, Colaresi & Quinn 2008, *Fightin' Words*, Political Analysis 16(4):372–403**)。事前分布は両コーパスのプール語頻度から作り、低頻度語の推定を安定化する。
3. 有意判定は **|z| > 1.96**(95%・両側)。
4. **交差群では「両方の無標群に対して有意」を要求する**(例: Black woman なら「無標の人種 = White」との比較と「無標の性別 = man」との比較の**両方**で有意な語のみ採る = 積集合)。
5. 結果: GPT-3.5 / GPT-4 のペルソナは**人が書いた同一プロンプトのペルソナより人種ステレオタイプの率が高く**、周縁化された群に対して "othering / exoticizing" のパターンを示した。

**★ 本プロジェクトへの読み替え設計**:

| Marked Personas | 本シムでの対応 |
|---|---|
| ペルソナ生成文 | **L1 の発話テキスト**(`speak.text` / `sns_post.text` / `dm.text` の 3 種。`analyze_specialization.py` の `UTTERANCE_KINDS` と同じ集合) |
| 有標群 | `agents.json` の属性(年齢帯・性別・職業。IPF の 3 軸そのもの) |
| 無標の既定群 | **★本シムでは "既定" を決められない**。渋谷の IPF 人口には「無標」が定義されない → **「当該属性値 vs 残り全員(one-vs-rest)」に置き換える**のが正しい。この読み替えは報告に明記する |
| 交差群の積集合 | 年齢帯 × 職業の交差セルでは、**年齢の one-vs-rest と職業の one-vs-rest の両方で有意な語のみ**採る(Cheng らの積集合則を保存) |
| |z| > 1.96 | そのまま。ただし**語彙数が数千のとき多重比較になる** → BH-FDR(`panel_stats.py::bh_fdr` が既存)を併記する |

**実装上の注意**:
- **`scipy` が依存に無い**ので、log-odds + Dirichlet prior は**自前実装**(式は単純: \( \hat{\delta}_w = \log\frac{y_w^{(i)}+\alpha_w}{n^{(i)}+\alpha_0-y_w^{(i)}-\alpha_w} - \log\frac{y_w^{(j)}+\alpha_w}{n^{(j)}+\alpha_0-y_w^{(j)}-\alpha_w} \)、分散 \( \approx \frac{1}{y_w^{(i)}+\alpha_w}+\frac{1}{y_w^{(j)}+\alpha_w} \)、z = δ̂ / √var)。
- **トークナイズ**: `analyze_specialization.py` は文字 2-gram(語彙リテラルゼロ設計)だが、S-18 は**語を出すのが目的**なので別の切り方が要る。日本語なので形態素解析器を新規依存にはできない → **文字 n-gram(n=2,3)を「語の代理」として出し、その旨を正直に注記する**のが最も安全(「造語」の観測も同じ制約下にある)。
- **1 回限りの検査**であることを docstring に明記(サーベイのアクション文言どおり)。**シム本体ゼロタッチ・読み取り専用**。

**接続文献**: *Paraphrase-Induced Output-Mode Collapse: When LLMs Break Character Under Semantically Equivalent Inputs*(arXiv:2605.04665)— **言い換えでペルソナ崩壊が起きる**。第 92 バッチで入れた `ablate.prompt_paraphrase`(S-16)と S-18 は**同じ現象の裏表**であり、報告では並べて読むべきである。

### 3.3 S-09: 4 軸の指標選択と、中心性の選び方(文献根拠)

サーベイ §4.1.2–4.1.3 の **mode(static/dynamic)× structure(layered/centralized/decentralized)× role(communicator/worker/director)** を観測語彙に落とすとき、**どの指標を選ぶかには既に確立した標準がある**。以下はすべて `networkx>=3.2`(既存依存)で計算でき、`scipy` を要求しない。

| 軸 | 採るべき指標 | 一次文献 | 本 repo の状況 |
|---|---|---|---|
| **structure: centralized ↔ decentralized** | **Freeman の群レベル中心化指数 \(C_D\)**(最大次数と他ノード次数の差の総和を**スター型での値で正規化**。スター = 1、完全グラフ = 0) | **Freeman, L. C. (1979). *Centrality in Social Networks: Conceptual Clarification.* Social Networks 1:215–239** | **未実装**(`degree_gini` は `analyze_communities.py` L476 にあるが、これは**集中度であって中心化指数ではない**)。**両方出して併記するのが正しい**(Gini は分布の不平等、\(C_D\) はスター型からの距離) |
| **structure: layered(層の有無)** | **Global Reaching Centrality (GRC)**(局所到達中心性の最大値と平均の差。フラット網 = 0、完全な木 = 1 に近づく) | **Mones, E., Vicsek, L. & Vicsek, T. (2012). *Hierarchy Measure for Complex Networks.* PLOS ONE 7(3):e33799** | **★`networkx.algorithms.centrality.global_reaching_centrality` が標準実装済み**(純 Python・scipy 不要)。**有向グラフ**(speak: 話者→聞き手 / dm: 送信→受信)に当てる |
| **role: communicator / worker / director** | **Guimerà–Amaral の役割カルトグラフィ**(コミュニティ内次数の z スコア \(z_i\) × 参加係数 \(P_i\)。閾値 z = 2.5, P = 0.62 で peripheral / connector / module hub / network hub に分類) | **Guimerà, R. & Amaral, L. A. N. (2005). *Functional Cartography of Complex Metabolic Networks.* Nature 433:895–900** | **未実装**。`analyze_communities.py` の Louvain 分割をモジュールとして使えば直接計算できる。読み替え: **高 P = communicator(コミュニティ間の橋)/ 高 z = director(コミュニティ内ハブ)/ 低 z 低 P = worker** |
| **mode: static ↔ dynamic** | **窓間メンバーシップの Jaccard 安定度 + Palla らの「定常性 ζ」**(群の寿命は、大きい群ほど**メンバーを入れ替える**方が長く、小さい群は**不変**な方が長い、という非対称性が既知) | **Palla, G., Barabási, A.-L. & Vicsek, T. (2007). *Quantifying Social Group Evolution.* Nature 446:664–667** | **★実質実装済み**。`analyze_communities.py` は既に Palla のライフサイクル語彙(誕生/成長/縮小/合流/分裂/消滅)へ機械分類し、窓間 Jaccard(τ = 0.30)と `stability_jaccard` を出している |

**★ 中心性の選択について(査読耐性の観点で最も重要)**:
- **「どの中心性を使うか」を後から選ぶのは最悪**である。Freeman 1979 自身が degree / closeness / betweenness / eigenvector の 4 概念を**別々の理論的主張**として分けており、どれを使うかで「中心的」の意味が変わる。**事前登録に固定すべき**。
- **推奨は「degree 中心化(構造の集中)+ betweenness(仲介・層の橋)+ GRC(層の深さ)の 3 本立て」**で、**eigenvector は採らない**ことを推奨する。理由: (a) repo 内に実装が無く新規に書く唯一の中心性になる、(b) `nx.eigenvector_centrality` は冪乗法で**収束しないグラフがある**(決定論性の主張と相性が悪い)、(c) 「誰が影響力を持つか」は S-11 の主題であって S-09(組織の**形**)の主題ではない。**採らない理由を書くことが S-04 の境界宣言の作法である。**
- degree / betweenness は**既に repo 内に純 Python 実装がある**(`measure.py` L866 ほか / `analyze_founders.py` L300 `betweenness_bfs`)ので、**再実装しない**。

### 3.4 S-13: 規範ライフサイクルの対応表(3 系譜との接続)

本シムの 4 段は `src/society/observer/norms.py` L61 —
```python
STAGE_NAMES = {0: "none", 1: "coin", 2: "quote", 3: "definite", 4: "institution"}
```

| 本シム | 定義(実装) | **Ren et al. 2024(CRSEC)** | **Finnemore & Sikkink 1998(norm life cycle)** | **測っていないもの(正直な注記)** |
|---|---|---|---|---|
| **S1 `coin`** | `label_coin` イベント。同語の**最初の coin だけ** | **Creation**(規範の創出) | **Emergence**(norm entrepreneur による創出) | coiner が「規範を作ろうとしたか」の意図は測らない(行動からの検出のみ) |
| **S2 `quote`** | coiner **以外**による最初の使用(`transmission` 経由 or 発話テキスト初出の早い方) | **Spreading**(伝播) | **Emergence → Cascade の境界**。F&S は**約 1/3 の採用**を tipping point とする | 本シムの S2 は**1 人目**で成立する = tipping point ではない。**採用率の閾値は事前登録 E2(使用者 3 名)が別途担う** |
| **S3 `definite`** | 発話中に「〈定冠詞相当マーカー〉+ 語」(「例の◯◯」)が現れた初出 | **Representation**(形式的表象) | **Cascade**(共有指示対象の成立) | 表層文字列一致のみ = **過小検出**。マーカーは `conf` が唯一の源で、未設定なら永久に 0 件 |
| **S4 `institution`** | 発話中に〈合意参照マーカー〉と語が**同一発話内に共起**した初出 | **Evaluation + Compliance**(健全性検査と遵守) | **Internalization**(遵守が自動化された状態) | ★**最重要の限界**: F&S の internalization は**行動の自動化**、CRSEC の Compliance は**計画・行動への組み込み**だが、**本シムの S4 は「言及」しか見ていない**。「規範に従って行動した」ことは測っていない。**この 1 行を書かないと過大主張になる** |

- **Ren, S., Cui, Z., Song, R., Wang, Z. & Hu, S. (2024). *Emergence of Social Norms in Generative Agent Societies: Principles and Architecture.* IJCAI 2024 / arXiv:2403.08251.** — **CRSEC** = **C**reation & **R**epresentation / **S**preading / **E**valuation / **C**ompliance の 4 モジュール。「規範はどこから来るか / どう形式表象されるか / 会話と観察でどう広がるか / 健全性検査と長期統合 / 計画と行動にどう組み込まれるか」の 5 問を立てる。**本シムの 4 段はこの 4 モジュールにほぼ 1 対 1 で対応する**。
- **Finnemore, M. & Sikkink, K. (1998). *International Norm Dynamics and Political Change.* International Organization 52(4):887–917.** — 3 段(emergence → cascade → internalization)+ **tipping point ≈ 1/3**。social science 側の最も引用される枠。
- **Hollander, C. D. & Wu, A. S. (2011). *The Current State of Normative Agent-Based Systems.* JASSS 14(2):6. DOI 10.18564/jasss.1750.** — 規範的 MAS のサーベイ。規範を rigid(全体制約)/ flexible(エージェントの決定に委ねる)に分ける区分は、**本シムが flexible 側であることを 1 行で言える**ので併記の価値がある。

**置き場所**: **事前登録 §3-E(規範成立の判定と下方因果)の直後に §3-E' として置く**。`analyze_norms.py` の docstring は**絶対に触らない**(凍結 12 番)。

### 3.5 S-05: seed 分散 vs 条件分散の分解(文献根拠と設計)

- **Carmona-Cabrero, Á., Muñoz-Carpena, R., Oh, W. S. & Muneepeerakul, R. (2024). *Decomposing Variance Decomposition for Stochastic Models: Application to a Proof-of-Concept Human Migration Agent-Based Model.* JASSS 27(1):16. DOI 10.18564/jasss.5174.** — **乱数 seed をモデル入力として扱ってはならない**とし、総分散 \(V(Y)\) を **決定論的分散 \(V_d\)**(入力変化による期待値の変動)と **確率的分散 \(E_s\)**(入力固定時の内在ゆらぎ)に分ける「Approach IV」を推奨。報告すべき量は **\(V_d/V(Y)\) と \(E_s/V(Y)\) の 2 つの寄与率**、およびブートストラップによる頑健性。
- **Lorscheid, I., Heine, B.-O. & Meyer, M. (2012).** — 必要な反復回数は **出力の変動係数(CV)が安定する点**で決める。
- **設計への落とし込み**(本プロジェクト固有):

  ```
  各主要指標 Y について:
    V_condition = 条件平均の分散(条件間)
    V_seed      = 条件内 seed 分散の平均(条件内)
    ratio       = V_condition / V_seed          ← これが 1 を大きく超えないと結論を出さない
    報告形式    = d_j = 中央値 [min, max]        ← S-16 の FormatSpread 提言と同形式
  ```
  - **既存資産の再利用**: `panel_stats.py` は既に `_parse_cond_seed(run_name, cfg_seed)`(L85)で run 名から (条件, seed) を解釈し、条件別の平均 ± CI と同 seed ペア比較を出している。`analyze_sweep.py` は **seed 階層ブートストラップ 95%CI(B=2000)** と `seed_divergence`(同一 (N,k) 内の seed ペア間 L2 距離)を既に持つ。**新スクリプトはこの 2 本を import して束ねるだけでよい。**
  - **`analyze_g.py` は拡張先ではない**(実査確認): その分解は `Var(g_end) = Var(g0) + Var(Δg) + 2Cov(g0, Δg)` という**単一ラン内の個体横断分散**の分解であり、seed でも条件でもない。docstring L41–43 が「単独ランの `share_born` は生まれつきの寄与を意味しない、意味を持つのは条件間比較だけ」と自ら明記している。→ **S-05 は `analyze_g.py` の分解「型」を借りるが、`analyze_g.py` を改修するのではなく新設する。**
  - **★事前登録との接続(最重要)**: 前文 ④ 反証条件 (a)「条件間差が seed 間差を上回らない」は**既に承認対象として書かれている**。この装置が無いと**反証条件そのものが判定不能**になる。→ S-05 は「あると良い」ではなく「**約束済みの装置**」である。

### 3.6 S-06: 個体レベル長期一貫性(文献根拠)

- **Li, K., Liu, T., Bashkansky, N., Bau, D., Viégas, F., Pfister, H. & Wattenberg, M. (2024). *Measuring and Controlling Persona Drift in Language Model Dialogs.* arXiv:2402.10962.** — **8 ターン以内で有意な persona drift** が生じることを self-chat ベンチで示し、原因を transformer の attention decay(系列が伸びるほど自己記述の埋め込みが直近文脈に押される)に帰した。**本シムは 10 日 = 1,440 step であり、この時間尺度をはるかに超える。**
- サーベイ §3.5 の「lifelong evaluation はほぼ存在しない」は 2026 年時点でも実質そのままで、**個体レベルの長期一貫性を測った社会シムは見つからなかった**。→ **本項目は分野で最初の long-horizon persona consistency 指標になりうる**という survey の記述は妥当。
- **設計上の必須注記**(実査で判明): `diagnose_stationarity.py` は現状 **`D` を「エージェント方向の標本」**として扱っており(交換単位 = エージェント。docstring L44–45 が Farine & Carter を引く)、**個体別化すると交換単位が「日」に変わる**。置換検定の帰無仮説が変わるので、新スクリプトでは**この違いを明示的に書く**必要がある。
- **出力する 1 数値**: 個体内 TVD の平均 / 個体間 TVD の平均(= within/between 比)。**これが小さいほど「個体が一貫している」**。`flat_traits`(ゼロ対照)ランとの差分で「一貫性が特性由来か環境由来か」まで言える。

### 3.7 S-11: 送り手の影響力(文献根拠 — 実装可否を左右する)

- **Salganik, M. J., Dodds, P. S. & Watts, D. J. (2006). *Experimental Study of Inequality and Unpredictability in an Artificial Cultural Market.* Science 311(5762):854–856.** — 14,341 名を「他者のダウンロード数が**見える**市場」と「**見えない**市場」に振り分けた実験。**社会的影響を強めるほど、成功の不平等と "予測不能性" が両方上がった**。品質は結果を部分的にしか決めない(最良曲は滅多に沈まず、最悪曲は滅多に浮かないが、**それ以外はどんな結果もありうる**)。
  → **★本項目の最小案は、この実験の「見える」条件そのものである。** ON にすれば seed 間分散が増える方向に働き、S-05 の判定(条件差 > seed 差)を自分で困難にする。**本選前に入れない決定的な根拠。**
- **Bakshy, E., Hofman, J. M., Mason, W. A. & Watts, D. J. (2011). *Everyone's an Influencer: Quantifying Influence on Twitter.* WSDM 2011.** — 160 万ユーザー・7,400 万件の伝播を追跡。**最大のカスケードは「過去に影響力があった者」かつ「フォロワが多い者」から生じる**が、**どのユーザー/URL が大カスケードを生むかの個別予測は当たらない**。予測モデルの特徴量が「**過去のカスケードの平均サイズ**」= 本項目の最小案が受け手に見せようとしている量そのもの。
- **Merton, R. K. (1968). *The Matthew Effect in Science.* Science 159(3810):56–63.** — 累積優位の原典。サーベイ §5.1.3 が引く Pareto / Matthew の根拠。
- **観測設計(Matthew 効果を見る)**: ON/OFF 2 条件で、(i) 伝播実績の **Gini と上位 10% シェアの時間発展**(S-03 で既に `calibrate_report.py` に指標がある)、(ii) **seed 間の順位相関(Spearman)**が ON で下がるか(= 予測不能性の増大 = Salganik の再現)、(iii) 初期優位が持続するか(**t 期の実績 → t+1 期の実績の回帰係数**が 1 を超えるか = 累積優位)。**(ii) が Salganik の直接の再現実験になる**ので、これ自体が独立した知見になりうる。

### 3.8 S-12: offline / online 二層(文献根拠)

- **Szell, M., Lambiotte, R. & Thurner, S. (2010). *Multirelational Organization of Large-Scale Social Networks in an Online World.* PNAS 107(31):13636–13641.** — 多重関係(multiplex)網の実証の古典。層ごとに構造が異なることを示す。
- **Centola, D. & Macy, M. (2007) / Centola, D. (2010). Science 329:1194.** — **単純伝染(情報・疾病)は 1 接触で伝わるが、行動は複数の補強源を要する「複雑伝染」**。→ **「規範はどちらの層で成立するか」を問う S-12 のアクションは、まさにこの理論の検定になる**。予測: **対面(offline)層はクラスタが密で補強が起きやすいので規範(複雑伝染)が成立しやすく、オンライン層は到達が広いので語(単純伝染)が速く広がる**。この予測を事前登録に書いてから測るべき。
- **層間の相関の標準量 = edge overlap**(層 α に辺があるとき層 α' にも辺がある条件付き確率)。層が独立か冗長かを 1 数値で言える。
- **★本シムでの正直な注記(§1.4 参照)**: `channel` は 5 値で、`search` / `news` は送り手が `-1`(人でない)。**offline / online の二分では尽くせない**。三層目を「媒体」として宣言する。

### 3.9 S-14: 合成人口の再現誤差(標準指標)

- **Voas, D. & Williamson, P. (2001). *Evaluating Goodness-of-Fit Measures for Synthetic Microdata.* Geographical and Environmental Modelling 5(2):177–200.** — 合成人口の適合度指標の標準。**TAE(総絶対誤差)** と **TAE/2 = 分類誤差(CE)**(誤分類された個体数)、**SRMSE(標準化二乗平均平方根誤差。0 = 完全一致)**。疎な表ではゼロセルが指標を壊すという注意も同論文。
- **実査で判明した実装状況**:
  - IPF の目標周辺は `data/shibuya_population.json`(`age_bands` 6 帯 / `gender` 2 / `occupations` 12)。IPF 本体は `scripts/build_persona_pool.py` L238–257 `_ipf_joint(pop, iters=60)`。
  - **誤差を出す処理は存在しない。** `meta.json` に入るのは層別件数(`layer_targets` / `layer_counts`)だけで、**年齢・性別・職業の周辺分布誤差はどこにも無い**。
  - 近いものは `tests/test_persona_pool.py` L101–136 の `test_L1_age_gender_marginals` / `test_L1_occupation_marginals`(**許容誤差 0.06 の assert** = 合否だけ出して数値を出さない)。
  - **★後付けで完全に作れる**: `data/persona_pool/L1/part-0000.jsonl`(30,000 行・`age`/`gender`/`occupation` を各行が保持)と `data/shibuya_population.json` の突合で足りる。`_ipf_joint` は決定論なので再現も可能。
- **報告形式**: `| 属性 | カテゴリ | 目標 share | 実績 share | 差 | %誤差 |` + 属性ごとの **SRMSE / TAE / CE** の 3 数値。**サーベイ Table 5 は各研究の構成要素の有無を ✓ で並べるだけで、再現誤差を数値で出す研究はほぼ無い** → 安い差別化。

### 3.10 S-07 / S-08 / S-15 / S-17(文書のみ・確認結果)

| 項目 | 確認結果 |
|---|---|
| **S-07** | **実装変更不要を確認**。`judge.py` は `SPEC_FILES` 外(自由に編集可)。出力は `<run_dir>/analysis/judge_report.md`(L384–388)、レンダは `_write_report`(L400–454)。挿入点は **L404–408 の「R4(循環の防壁)」ブロッククォート**が最有力。書く内容: 「judge は **world_changer の単一次元にのみ用いる**(サーベイ §4.4 が『目標達成の次元では人間評価とよく一致するが他の次元では大きな乖離が残る』と報告する、**一致度が比較的高い側の次元**)。κ ≥ 0.7 の採用条件・別ファミリ推奨・シム逆流不能は分野の慣行より厳しい」 |
| **S-08** | 報告テンプレ **§7.2 が既に空枠として存在**(L227–232)。事前登録の前文 ③(e) にも既に 1 行(「分野標準と逆にアウトライアを厚くしない」)が入っている。さらに第 88 バッチ(`model.mind`)が **高解像度層 1〜5% を traits 非依存の一様抽選**にしており IMPLEMENTED.md L384 が「**S-08 整合**」と明記済み。→ **残作業は §7.2 の本文を埋め、`ablate.cognitive_tier` を片側検査として位置づける 1 段落を書くだけ** |
| **S-15** | **★重複を確認**: 事前登録の前文 ③(c) に**片側解釈の全文が既に入っている**(第 92 バッチ B1)。報告テンプレ §7.3 も空枠で存在(L233–241)。→ **残作業は §7.3 を埋めるのみ**。新規に書くべきは「`observer.echo` の `echo_max == 1.000` 崩壊ラン除外規則」と「是正機構を**入れない**という決定とその理由(機構を足すと『不満を人工的に作った』と読まれ k* の内生性の主張が弱る)」の 2 点 |
| **S-17** | 報告テンプレ **§7.4 が空枠で存在**(L242–252)。事前登録の反証条件 ④(f) に「`propagation_off` と本番の中間条件でのみ現れる構造が主結論を担っている = 境界アーティファクト」が既に入っている。**解析スクリプトは不要**(§1.3 の判定)。関連する新語として **"Fluency Fallacy"**(高い言語的一貫性を保ちながら社会的事実を幻覚し、"表層のリアリズム" が因果的妥当性と取り違えられる)が 2026 年の GABM 文献に現れており、境界アーティファクトの近縁概念として §7.4 に併記する価値がある |

---

## 4. リンク集(アクセス日: 2026-08-06)

### 4.1 S-10(MAS 失敗様式)

- Cemri, M. et al. (2025). *Why Do Multi-Agent LLM Systems Fail?* arXiv:2503.13657 — https://arxiv.org/abs/2503.13657 / 本文 HTML(**14 様式の表と割合の一次ソース**) https://arxiv.org/html/2503.13657v2 / PDF https://arxiv.org/pdf/2503.13657
- MAST を実運用テレメトリに適用した第三者再現 — https://github.com/hugomn/mast-taxonomy-production-telemetry

### 4.2 S-18(ステレオタイプ増幅)

- Cheng, M., Durmus, E. & Jurafsky, D. (2023). *Marked Personas: Using Natural Language Prompts to Measure Stereotypes in Language Models.* ACL 2023:1504–1532 — https://aclanthology.org/2023.acl-long.84/ / arXiv:2305.18189 https://arxiv.org/abs/2305.18189 / コード・データ https://github.com/myracheng/markedpersonas
- Monroe, B. L., Colaresi, M. P. & Quinn, K. M. (2008). *Fightin' Words: Lexical Feature Selection and Evaluation for Identifying the Content of Political Conflict.* Political Analysis 16(4):372–403 — https://www.cambridge.org/core/journals/political-analysis/article/fightin-words-lexical-feature-selection-and-evaluation-for-identifying-the-content-of-political-conflict/81B3703230D21620B81EB6E2266C7A66
- 参照実装(log-odds + informative Dirichlet prior・|z| > 1.96 の慣行) — https://github.com/jmhessel/FightingWords / https://github.com/kornosk/log-odds-ratio
- *Paraphrase-Induced Output-Mode Collapse: When LLMs Break Character Under Semantically Equivalent Inputs.* arXiv:2605.04665 — https://arxiv.org/html/2605.04665v2(**S-16 と S-18 の接続**)

### 4.3 S-09(組織形態・中心性の選択)

- Freeman, L. C. (1979). *Centrality in Social Networks: Conceptual Clarification.* Social Networks 1:215–239 — https://www.scirp.org/reference/referencespapers?referenceid=1448578
- Mones, E., Vicsek, L. & Vicsek, T. (2012). *Hierarchy Measure for Complex Networks.* PLOS ONE 7(3):e33799 — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3314676/ / **networkx 実装** https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.global_reaching_centrality.html
- Guimerà, R. & Amaral, L. A. N. (2005). *Functional Cartography of Complex Metabolic Networks.* Nature 433:895–900 — https://www.researchgate.net/publication/8004992_Nunes_Amaral_Functional_cartography_of_complex_metabolic_networks
- Palla, G., Barabási, A.-L. & Vicsek, T. (2007). *Quantifying Social Group Evolution.* Nature 446:664–667 — https://www.nature.com/articles/nature05670 / arXiv:0704.0744 https://arxiv.org/abs/0704.0744

### 4.4 S-13(規範ライフサイクル)

- Ren, S., Cui, Z., Song, R., Wang, Z. & Hu, S. (2024). *Emergence of Social Norms in Generative Agent Societies: Principles and Architecture.* IJCAI 2024 / arXiv:2403.08251 — https://arxiv.org/abs/2403.08251 / IJCAI 版 https://www.ijcai.org/proceedings/2024/0874.pdf(**CRSEC の 4 モジュール**)
- Finnemore, M. & Sikkink, K. (1998). *International Norm Dynamics and Political Change.* International Organization 52(4):887–917 — http://www.olivialau.org/ir/archive/fin5.pdf(**3 段 + tipping point ≈ 1/3**)
- Hollander, C. D. & Wu, A. S. (2011). *The Current State of Normative Agent-Based Systems.* JASSS 14(2):6 — https://www.jasss.org/14/2/6.html

### 4.5 S-05(分散分解)

- Carmona-Cabrero, Á., Muñoz-Carpena, R., Oh, W. S. & Muneepeerakul, R. (2024). *Decomposing Variance Decomposition for Stochastic Models.* JASSS 27(1):16. DOI 10.18564/jasss.5174 — https://www.jasss.org/27/1/16.html(**seed を入力として扱わない分解**)
- ten Broeke, van Voorn & Ligtenberg (2016). *Which Sensitivity Analysis Method Should I Use for My Agent-Based Model?* JASSS 19(1):5 — https://www.jasss.org/19/1/5.html
- Lee, J.-S. et al. (2015). *The Complexities of Agent-Based Modeling Output Analysis.* JASSS 18(4):4 — https://jasss.soc.surrey.ac.uk/18/4/4.html

### 4.6 S-06(長期一貫性 / persona drift)

- Li, K. et al. (2024). *Measuring and Controlling Persona Drift in Language Model Dialogs.* arXiv:2402.10962 — https://arxiv.org/html/2402.10962v1 / コード https://github.com/likenneth/persona_drift
- *ContextEcho: A Benchmark for Persona Drift in Long Agentic-Coding Sessions* — https://arxiv.org/html/2605.24279

### 4.7 S-11(送り手の影響力)

- Salganik, M. J., Dodds, P. S. & Watts, D. J. (2006). *Experimental Study of Inequality and Unpredictability in an Artificial Cultural Market.* Science 311(5762):854–856 — https://www.science.org/doi/10.1126/science.1121066 / 補遺 https://www.princeton.edu/~mjs3/salganik_dodds_watts06_som.pdf(**「見える/見えない」の実験操作 = 本項目そのもの**)
- Bakshy, E., Hofman, J. M., Mason, W. A. & Watts, D. J. (2011). *Everyone's an Influencer: Quantifying Influence on Twitter.* WSDM 2011 — https://snap.stanford.edu/class/cs224w-readings/bakshy11influencers.pdf
- Merton, R. K. (1968). *The Matthew Effect in Science.* Science 159(3810):56–63

### 4.8 S-12(offline / online 二層)

- Szell, M., Lambiotte, R. & Thurner, S. (2010). *Multirelational Organization of Large-Scale Social Networks in an Online World.* PNAS 107(31):13636–13641 — https://www.pnas.org/doi/10.1073/pnas.1004008107
- Centola, D. (2010). *The Spread of Behavior in an Online Social Network Experiment.* Science 329:1194–1197 / Centola & Macy (2007). *Complex Contagions and the Weakness of Long Ties.* AJS 113(3):702–734 — 概観 https://arxiv.org/pdf/1710.07606(*Complex Contagions: A Decade in Review*)
- multiplex の edge overlap ほか — https://link.springer.com/content/pdf/10.1140/epjb/e2015-50742-1.pdf

### 4.9 S-14(合成人口の再現誤差)

- Voas, D. & Williamson, P. (2001). *Evaluating Goodness-of-Fit Measures for Synthetic Microdata.* Geographical and Environmental Modelling 5(2):177–200 — https://www.researchgate.net/publication/233708235_Evaluating_Goodness-of-Fit_Measures_for_Synthetic_Microdata
- Chapuis, K., Taillandier, P. & Drogoul, A. (2022). *Generation of Synthetic Populations in Social Simulations: A Review of Methods and Practices.* JASSS 25(2):6 — https://www.jasss.org/25/2/6.html
- Lenormand, M. & Deffuant, G. (2013). *Generating a Two-Layered Synthetic Population for French Municipalities.* JASSS 24(2):5 — https://www.jasss.org/24/2/5.html

### 4.10 S-17(境界アーティファクト)

- Larooij, M. & Törnberg, P. (2025). *Validation is the Central Challenge for Generative Social Simulation.* Artificial Intelligence Review. DOI 10.1007/s10462-025-11412-6 — https://link.springer.com/article/10.1007/s10462-025-11412-6 / https://arxiv.org/html/2507.19364
- *Generative Agents in Agent-Based Modeling: Overview, Validation, and Emerging Challenges.* IEEE TAI (2025) — https://www.computer.org/csdl/journal/ai/2025/12/10985773/26trm5iUHYc
- *PhysicsAgentABM: Physics-Guided Generative Agent-Based Modeling.* arXiv:2602.06030 — https://arxiv.org/pdf/2602.06030(**"Fluency Fallacy"** の出所)

### 4.11 本プロジェクト内の接続先

- `docs/research/llm-social-sim-survey.md` §3(S-05〜S-18 の定義)/ §4(既に超えている点)
- `docs/research/sv-items-research.md`(◎5 件の前例・§6 のバッチ分解の作法)
- `docs/plans/stationarity-preregistration.md` — 前文「主張の境界」(L16–86)/ §3-E(L358)/ §3-F(L372)/ §7 変更履歴(L543)
- `docs/plans/observation-report-template.md` — §4.4(S-14 の空欄・L153)/ §7.1〜7.4(**S-05/S-08/S-15/S-17 の空枠**・L213–252)
- `src/society/observer/metrics_spec.py` L51–69(`SPEC_FILES` 14 本)/ L72–76(正規化)
- `PENDING.md` L14(**SV 残 13 項目 = リサーチ中 → 実装**)/ L50(`Item.transmissions` 上限なし = S-11 の障害)/ L70(SV-U1 行)

---

## 5. 本文書の限界(正直な列挙)

1. **Marked Personas の「群あたり生成数」は一次確認できていない**。統計量(Fightin' Words)・閾値(|z| > 1.96)・交差群での積集合則は複数の二次記述が一致して述べており確度は高いが、**生成本数と前処理(ストップワード等)は論文 PDF から直接取れなかった**。実装前に `marked_words.py` を読むこと。ただし本シムでは「1 属性群あたりの発話本数」は L1 の実データで決まるので、この数値は設計に影響しない。
2. **MAST の 14 様式は「タスク遂行型 MAS」から帰納された分類**であり、タスクを与えない社会シムへの適用は読み替えを要する(§3.1 末尾の注記)。**14 様式のうち △ を付けた 4 件は、判定の妥当性を実データで確認するまで「判定可能」と書いてはならない。**
3. **`analyze_org_form.py` の 4 軸のうち、role 軸(Guimerà–Amaral)の閾値 z = 2.5 / P = 0.62 は代謝ネットワークで較正された値**であり、社会ネットワークにそのまま使えるかは未検証。**閾値を使わず (z, P) 平面上の分布そのものを出す**のが安全(閾値は事前登録に書いてから使う)。
4. **S-12 の `sns_read` 由来の辺を張るかどうかは未決**。現状 online 層は DM のみで、SNS の到達が辺として数えられていない。これを直すと online 層の次数分布が大きく変わるので、**事前登録に「どちらの定義で測るか」を書いてから実装する**必要がある。
5. **S-11 の走査コスト(25 万体で `sim.items` 全走査)は実測していない**。本選後の着手時に、まず `bench_lod.py` 相当で実測し、成立しないなら**不採用と正直に書く**こと。
6. **本文書はコードを 1 行も変更していない**。§2 のバッチ分解は提案であり、SV2-B / SV2-C の着手には `ask-before-extending` に従いユーザー合意が必要。
