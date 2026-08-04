# SV-U1 実装前文献リサーチ — S-01 / S-02 / S-03 / S-04 / S-16

**対象**: `docs/research/llm-social-sim-survey.md` §3 の「サーベイ反映 ◎」5 項目のうち、SV-U1 に束ねられた 5 件。
**目的**: 実装に入る前に、各項目が **どの文献に依拠して何を書くべきか** を一次ソース付きで確定する。
**アクセス日**: 全リンク 2026-08-05(§7 に一覧)。
**制約の前提**: R1 ドクトリン(既定 OFF / golden L1 バイト一致 / no-fingerprint / `metrics_spec_hash` = 指標定義 14 ファイルの凍結)。本文書は調査のみで、コード変更・コミットを含まない。

---

## 0. 3 行サマリ

1. **S-02 と S-01 は ODD 2020 の要素 1「Purpose and patterns」に丸ごと対応する** — ODD が言う "patterns" とは「モデルが再現できたら成功と見なすパターン」の**事前宣言欄**そのものであり、我々の「stylized facts リスト」は独自発明ではなく ABM の標準要素の充足である。この接続を書くだけで「勝手な基準」批判が消える。
2. **S-03 の最重要の発見は「現実側の分散バンドを取れるデータは限られる」こと** — 社会生活基本調査は**平均と行動者率しか公表しておらず個体間 SD が無い**。個体間分散を直接計算できる一次データは実質 SocioPatterns(接触)と全国家計構造調査(所得 Gini)に限られる。捏造しない原則を守るなら、**CV は「行動者率から復元できる分散の下界」に留め、Gini/上位 10% シェアを主軸にする**設計が正しい。
3. **S-16 は分野が 2026 年に急速に厳しくなった領域** — Ye et al. 2026 (TRAILS) は「同一の摂動が frontier model 間で 1pp〜76pp と桁違いに効き、**頑健性は claim ごと・model ごとに測るもので仮定してはならない**」と結論した。paraphrase は 3〜5 セットが文献の相場で、判定は **符号保存 + spread を seed 間レンジと比較**の 2 段が実装可能かつ最も安い。ただし本プロジェクト固有の障害が 2 つある(`ablate.SECTIONS` の接頭辞リテラル一致テスト、CachedLLM のキャッシュミスによる実 LLM コスト P 倍)。

---

## 1. S-02: 渋谷の stylized facts 候補表

### 1.1 表の読み方

- **循環性リスク**: 本シムは EPR(exploration & preferential return)を `src/society/cognition/routine.py` に実装済みで、日次計画も決定論的に与えられる(事前登録 §0 に明記済み)。したがって **移動系の法則の一部は「入力の再生」であり、再現できても創発の証拠にならない**。この列で区別する。
- **判定枠**: 事前登録で「**再現できたら成功と見なす(主判定)**」と「**再現できなくても主張に影響しない(参考)**」に二分する。これがサーベイ §5.4 の要求。

### 1.2 候補表

| # | 法則 | 定量形 | 出典(一次) | シムで検定可能か | 循環性 | 検定方法 | 判定枠 |
|---|------|--------|-------------|------------------|--------|----------|--------|
| F1 | 時間帯別人流の二峰性 | 在圏人口の時刻系列に朝(7–9h)・夕(17–19h)の 2 極大 | 東京都市圏 PT 調査 第 6 回 / 全国の人流オープンデータ(1km メッシュ・昼夜) | ◎(1 日 288 step で可) | **高**(日次計画が入力) | L1 移動イベント → 時刻別在圏人口。極大 2 個 + 谷/ピーク比 < θ | **参考** |
| F2 | 訪問頻度の Zipf 則 | \( f_k \sim k^{-\zeta} \), ζ ≈ 1.2 | Song, Koren, Wang & Barabási 2010 (Nature Physics) | ○(10 日・1 人あたりランク 5–15 程度) | **高**(EPR 実装済み) | 個体別の訪問地点をランク付け、両対数回帰で ζ 推定。**実装パラメータから予測される ζ との一致=内部整合性検査**として使う | **参考**(内部整合性のみ) |
| F3 | 探索の逓減 | \( S(t) \sim t^{\mu} \), μ = 0.6 ± 0.02 | Song et al. 2010 | △(t レンジ 1–2880 step で両対数の腕が短い) | **高** | 個体別の累積訪問地点数 S(t) の両対数傾き | **参考** |
| F4 | 滞在時間分布の重い裾 | 指数分布が棄却され、truncated power law / lognormal が優越 | 人流実証文献群(§7 参照)。※分布形は集計水準に依存する点に注意 | ◎ | 中(POI 営業時間・行動長で上限が入る) | 滞在時間の対数尤度比検定(指数 vs 対数正規 vs 切断冪)。**「指数分布の棄却」までを主張し、どの裾かは主張しない** | **主判定(弱形)** |
| F5 | 行動のバースト性 | 事象間隔が heavy-tail。burstiness \( B=(\sigma-m)/(\sigma+m) > 0 \) | Barabási 2005 (Nature 435:207) / Goh & Barabási 2008 (EPL 81:48002) | ◎ | **低**(発話タイミングは内生) | 個体別の発話・DM の事象間隔から B と memory M を算出。Poisson 帰無(B≈0)を置換検定で棄却 | **主判定** |
| F6 | 対面接触時間の重い裾 | 接触継続時間・個体別総接触時間・接触間隔がいずれも heavy-tail | Cattuto et al. 2010 (PLOS ONE) / SocioPatterns。文脈(会議・学校・病院)に依らず同型 | ◎ | **低**(接触は空間から内生) | `speak` の hearers から接触ペア×継続を再構成し、3 分布とも指数を棄却 | **主判定** |
| F7 | 社会ネットワーク次数分布の重い裾 | 次数分布が右に長い裾(Pareto 的) | 同上 + 影響の Pareto/Matthew(サーベイ §5.1.3) | ○ | 中 | offline(対面 speak)/ online(SNS・DM)を**分離して**次数分布を推定(S-12 と接続) | **主判定(条件付き)**。※`relations.dunbar` ON 時は上限 51 で裾が機械的に切られる。**事前に「切られる」と宣言**し、OFF 条件でのみ主判定に用いる |
| F8 | 週次周期 | 平日/休日プロフィールの差 | 社会生活基本調査(週全体/土曜/日曜の別表) | △(10 日 = 週末 2 回) | 高(カレンダーが入力) | 平日/休日の日次プロフィール差が **seed 間分散を超えるか**(S-05 の分散分解を流用) | **参考** |
| F9 | 混雑と待ちの単調関係 | 密度 ↑ → 待ち時間 ↑ の単調性 | 都市工学の一般則(本プロジェクトは既に環の閉じを L1 実例で実証済み) | ◎ | 高(機械系) | 密度ビン別の平均待ち時間の単調性(Spearman ρ > 0) | **参考(機械系の健全性確認)** |
| F10 | 企業規模の Zipf 則 | \( P(S>s) \propto s^{-1} \) | Axtell 2001 (Science 293:1818) | **×** | — | 自然形成組織が 10 日で数十件規模。Axtell は 550 万社。**N が 4–5 桁足りない** | **不採用**(検定不能を明記) |
| F11 | Gibrat 則(比例効果) | 成長率が規模に独立 | Axtell 2001 の Kesten 過程解釈 | **×** | — | 10 日では成長率の推定に必要な時間断面が足りない | **不採用** |
| F12 | 移動の予測可能性 | 上限 ~93% | Song, Qu, Blumm & Barabási 2010 (Science 327:1018) | △ | 高 | 実エントロピー推定が 10 日では不安定 | **参考** |

### 1.3 事前登録に書くべき二分(推奨)

- **主判定(再現できたら成功と見なす)**: **F5(バースト性)/ F6(接触時間の重い裾)/ F4(滞在時間の非指数性)/ F7(次数の重い裾・dunbar OFF 条件)** の 4 件。
  - 選定理由が明快である: **いずれも入力に埋め込まれていない**(タイミングと接触は空間・スケジューリングから内生する)。F1–F3 のような「EPR を入れたから EPR 則が出た」という循環に落ちない。
- **参考(再現できなくても主張に影響しない)**: F1, F2, F3, F8, F9, F12。
- **不採用(検定不能と明記)**: F10, F11。**「検定できない法則を検定できないと書く」こと自体が S-04 の境界宣言の一部**であり、書かないと「都合の良い法則だけ選んだ」と読まれる。

### 1.4 注意 — 渋谷固有の一次バンドについて

「渋谷の」stylized facts と銘打つが、F1 以外は**渋谷固有ではなく人間行動の普遍則**である。渋谷固有の水準値(乗降人員・昼間人口・滞留人口)は既に `scripts/calibrate_report.py` の `REALITY` 表(29 エントリ)が持っており、**S-02 が足すのは「水準」ではなく「形」の判定**である。この区別を事前登録に 1 行書くこと(サーベイ §3 S-02 の「水準の照合であって法則の再現ではない」という自己指摘への直接の回答になる)。

---

## 2. S-03: 分散バンドのデータ源と指標定義

### 2.1 指標選択の文献的裏付け

| 指標 | 定義 | 採用根拠 |
|------|------|----------|
| CV | \( \sigma/\mu \)(母集団 SD) | スケール不変で分布の散らばりをスカラー 1 個に落とす標準量。単位の異なる指標を横並びにできる |
| Gini | ローレンツ曲線の面積比 | 集中度の標準量。**Gini と CV は同一関数の L¹ ノルムと L² ノルム**の関係にあり、強く相関するが同一ではない → **併記に意味がある** |
| 上位 10% シェア | 上位 decile の合計 / 全体 | Gini は「上位 0.1% がシェアを伸ばしても全体面積が変わらない」場合を見落とす。上位シェア(Palma 型の議論)はこれを捉える |

**3 つ併記の根拠**: 単独指標では捉えられない変化があるため。特に本プロジェクトの主張は **k*(裾の創発)** なので、**上位シェアが最も直撃する指標**である。平均だけで「現実的」と言うのが分野の典型的過大主張である、というサーベイ §8.1 の指摘に対し、3 指標併記が最小限の応答になる。

**LLM の「average personality」問題の一次文献**:
- **Wu, Peng, Ito & Xiao 2025** (arXiv:2506.19806) — 本項目の直接の根拠。系統的レビューの結果として「**大半の論文は ground truth 比較を含むが、行動的分散を明示的に評価するのは半数未満で、評価した論文の大半は人間集団より低い分散を報告している**」。3 提言のうち②が「**mean alignment と並べて variance を明示的に報告せよ**」。
- **Bisbee et al. 2024**(ANES を GPT-3.5 で再現)— LLM の平均意見スコアは母集団平均に表面上似るが、**回答のばらつきが小さく、多数派意見に過適合して裾(極端な意見・少数サブグループ・低頻度の属性交差)を系統的に過少表現する**。回帰係数が実データと大きく異なる。

### 2.2 現実側バンドのデータ源(重要な制約つき)

**★ 最重要の調査結果: 「個体間分散」を直接与える公的統計は極めて少ない。**

| 源 | 何が取れるか | 個体間 CV が取れるか | 用途 |
|----|--------------|---------------------|------|
| **社会生活基本調査(令和 3 年・総務省統計局)** | 行動の種類別の **総平均時間 / 行動者平均時間 / 行動者率**、時間帯別行動者率、地域別 | **× (SD 非公表)** | 下記 2.3 の**分散の下界**復元。時間帯別行動者率は F1/F8 の形の照合に使える |
| **SocioPatterns 公開接触データ**(Cattuto et al. 2010 ほか) | 個体別の総接触時間・接触相手数・接触継続時間の**生分布** | **○(唯一、直接計算できる)** | 会話頻度・社会接触数の CV / Gini / 上位 10% シェアの**現実バンドの主源**。F6/F7 の裾判定とも共用できる |
| **全国の人流オープンデータ**(国交省 / G 空間情報センター、1km メッシュ・時間帯別滞在人口、2019/01–2021/12 月次 CSV) | **メッシュ間**の滞在人口分布 | ×(個体間ではない) | 空間集中度(メッシュ間 Gini)のバンド。個体間 CV には流用しないこと |
| **モバイル空間統計**(e-Stat ビッグデータポータル) | 同上(集計値) | × | 同上 |
| **全国家計構造調査 / 家計調査** | 所得・支出の分布、所得 Gini の公表値 | ○(Gini は公表値あり) | 既存 L2 列 `asset_gini` / `asset_top10_share` の現実バンド |
| **Dunbar 層(5/15/50/150)** | 関係層のサイズ | 間接 | 既に `relations.dunbar` が参照済み。Lindenfors 2021 の 150 懐疑も既記載 |

### 2.3 社会生活基本調査から「分散の下界」を復元する手続き(捏造しない設計)

公表されるのは行動者率 \(p\) と行動者平均時間 \(m\) と総平均時間 \(\bar{x} = p\,m\) の 3 つ。個体内のばらつきは不明だが、**「やる人/やらない人」の二値だけによる分散**は復元できる:

\[
\mathrm{Var}(x) \;\ge\; p\,(1-p)\,m^2 \quad\Longrightarrow\quad \mathrm{CV} \;\ge\; \sqrt{\dfrac{1-p}{p}}
\]

- これは **参加/非参加の分散のみを数えた下界**であり、行動者内のばらつきを 0 と仮定した最も保守的な値。
- したがって報告は「**現実の CV は少なくとも X 以上**」という **片側バンド**になる。シム側の CV が X を下回れば「分散が痩せている」と**確実に言える**が、上回っても「十分」とは言えない。**この非対称性を報告に明記する**こと。これは既存の `propagation_off` の `fingerprint_risk=known` 正直宣言と同じ作法である。
- **既存の資産が使える**: `scripts/model_battery/reference.py` は publisher / title / url / accessed / license を強制し、未取得は `values: null` + `status="未取得"` で**捏造を拒否する** schema (`model_battery.reference/1`) を既に持ち、`data/battery/reference/estat_shakai_seikatsu_time_use.json` が存在する。**S-03 の現実バンドはこの schema を再利用して外部化すべき**(現在の `calibrate_report.py` は `REALITY` を 585 行中 44–106 行のモジュール定数として**インライン保持**しており、出典文字列はあるが機械検証されていない)。

### 2.4 報告形式の提案

各指標について 1 行に:

```
| 指標 | sim 平均 | 現実バンド | 判定 | sim CV | 現実 CV(下界) | 分散比 | sim Gini | 現実 Gini | sim top10% | 現実 top10% |
```

- **分散比** = sim CV / 現実 CV(下界)を 1 数値で必ず出す。「平均は ✅ だが分散比 0.42」という形で読める。
- Wu et al. 2025 の提言③に従い、**分散比が閾値未満なら主張を collective-level qualitative pattern に限定する**、という規則を事前登録に固定する(§5 の境界宣言 ③ と接続)。

### 2.5 実装上の決定的な制約(コード調査結果)

- **`calibrate_report.py` は `SPEC_FILES`(凍結 14 ファイル)に含まれない。** 凍結対象は observer 側 9 本(`aggregate.py` / `measure.py` / `stream.py` / `echo.py` / `norms.py` / `silence.py` / `deviation.py` / `structure.py` / `initial_frame.py`)+ `truth_ledger.py` + 解析側 4 本(`analyze_beliefs.py` / `analyze_norms.py` / `analyze_specialization.py` / `diagnose_stationarity.py`)。
- したがって **S-03 を `calibrate_report.py` 内に閉じれば `metrics_spec_hash` は変わらない**。逆に `observer/aggregate.py` の `_gini()` に手を入れると**凍結が破れる**(正規化はコメント除去をしないので、コメント 1 文字でもハッシュが変わる仕様)。
- **再利用できる既存実装**: CV は `scripts/model_battery/metrics.py::cv()`(母集団 SD、mean≤0 → 0.0)、分位は同 `quantile()`、Gini は repo 内に **5 実装が重複**(`observer/aggregate.py::_gini` / `observer/assets.py::_gini`+`_top_share` / `build_panel.py` / `observe_flows.py` / `analyze_communities.py::_gini_seq` / `bench_lod.py`)。**新規に 6 個目を書かず、凍結外の `model_battery/metrics.py` 側に寄せるのが正しい**。
- 既存 L2 列で流用できるもの: `status_gini` / `status_top10_share` / `trust_gini` / `deviation_top_share` / `asset_gini` / `asset_top10_share`。**これらは既に凍結表の中で計算済み**なので、`calibrate_report.py` は**読むだけ**でよい(現に `status_top10_share` は表示のみで既に消費している)。新規に必要なのは「行動時間・発話数・接触数」の分散列。

---

## 3. S-16: prompt paraphrase の設計

### 3.1 文献の相場

| 研究 | 言い換えセット数 | 水準 | 主要な発見 |
|------|------------------|------|-----------|
| **Sclar, Choi, Tsvetkov & Suhr 2024** (FormatSpread, ICLR 2024) | **320 formats × 53 tasks** | 書式(区切り・大小・空白) | LLaMA-2-13B で **最大 76 accuracy point** の差。GPT-3.5 で最大 56pt・**中央値 6.4pt**。format 性能はモデル間で弱相関 → **単一書式でのモデル比較は方法論的に疑わしい**。提言: **単一値でなくレンジで報告せよ** |
| **Zhu et al. 2023** (PromptRobust / PromptBench, arXiv:2306.04528) | 4,788 adversarial prompts / 8 タスク・13 データセット | **character / word / sentence / semantic の 4 水準** | 4 水準の階層が実装設計の雛形として使える |
| **Elazar et al.** (ParaRel) | 328 paraphrases / 38 relations(注釈者一致 95.5%) | 語彙・統語 | 意味が保たれても予測の変動が大きい |
| **Cao et al.** (RobustAlpacaEval) | **10 paraphrases / query**(GPT-4 生成 + 人手検証) | 意味等価 | 性能変動 **最大 45%**。worst-case が best-case を大きく下回る |
| **WASSA 2026, Measuring LLMs' Sensitivity to Paraphrased Opinion Prompts** | 200 質問 × **5 人手検証 paraphrase** | 表層 | 頑健性はモデルサイズよりアラインメント戦略・推論設計に依存 |
| **ParaConsist** | 150 base × **5 variants** | lexical / syntactic / semantic-expansion | 3 水準の切り方が我々の用途に最も近い |
| **Ye, Cao, Chen & Ferrara 2026** (TRAILS, arXiv:2605.18890) | — | agent(micro)/ interaction(meso)/ system(macro) | **persona 書式と課題文の枠づけの軽微な摂動が協調率を最大 76pp 動かす**。同じ摂動が別の frontier model では 1pp。→「**頑健性は claim ごと・model ごとに測るもので、仮定してはならない**」 |

**相場の結論**: **1 セットでは不足、5 セットが文献の中央値**。本プロジェクトは実 LLM 予算が有限なので、**最小 3・推奨 5** を提案する。

### 3.2 言い換えの水準(3 水準・我々のプロンプト構造に合わせて)

`src/society/cognition/deliberate.py::build_prompt`(L116、~130 個のキーワード引数、`lines: list[str]` を組み立てて `"\n"` 連結)の構造に合わせて:

| 水準 | 内容 | 例 | 実装可否 |
|------|------|-----|----------|
| **P-a 語彙(同義語置換)** | 内容語を意味等価な同義語に | 「近くにいる人」→「そばにいる人」 | ○ |
| **P-b 文体(敬体/常体・丁寧度)** | 語尾・待遇表現のみ変更 | 「〜してください」→「〜せよ」 | ○ |
| **P-c 統語(語順・節構造)** | 節の順序・修飾関係を変更 | 「直近の出来事: X」→「X が直近の出来事だ」 | **△ — 下記 3.4 の障害あり** |

固定ヘッダ側(`_HEADER_INTRO` / `_HEADER_FORMS` / `_COIN_LINE` / `_HEADER_TAIL` / `_EQUIP_INTRO` / `_EQUIP_LINES`)は**モジュール定数なので言い換えセットの差し替えが容易**。逆に約 60 個の条件付き `lines.append(f"...")` は接頭辞が load-bearing(3.4 参照)。

**推奨する 5 セットの構成**: `v0`(原文)/ `v1`(P-a のみ)/ `v2`(P-b のみ)/ `v3`(P-a+P-b)/ `v4`(P-a+P-b+P-c 限定適用)。**水準を単独と複合に分けることで「どの水準が効いたか」まで言える**(PromptBench の 4 水準階層に対応)。

### 3.3 判定式

事前登録で**主要結論を符号付き効果量の集合として凍結**する: \( d_j,\; j=1..J \)(例: 「k* 的個体の出現に対する環境フィードバックの寄与 − 初期特性の寄与」)。

各 paraphrase セット \(p \in \{0,\dots,P\}\) でランを回し \( d_j^{(p)} \) を得たとき:

1. **符号保存(第一判定・必須)**
   \[
   \forall p:\; \mathrm{sign}\!\left(d_j^{(p)}\right) = \mathrm{sign}\!\left(d_j^{(0)}\right)
   \]
   1 つでも符号が反転したら、その結論 \(j\) は**「言い回しに依存する」として取り下げる**か、言い回しを限定して報告する(TRAILS の per-claim 原則)。

2. **効果量の変動幅(第二判定)**
   \[
   \mathrm{spread}_j = \max_p d_j^{(p)} - \min_p d_j^{(p)}
   \]
   これを **seed 間の同一指標のレンジ**と比較する(S-05 の分散分解装置をそのまま流用):
   \[
   \mathrm{spread}_j \;\le\; \mathrm{range}_{\text{seed}}(d_j) \quad(\text{または } 2\,\mathrm{SE}_{\text{seed}})
   \]
   が成立すれば「**言い回しの効果は seed のゆらぎに埋もれる = 頑健**」と言える。これは S-05 の「条件差が seed 差より大きくなければ結論を出さない」規則と**同じ形式**なので、事前登録に既にある判定様式を再利用できる。

3. **報告形式(FormatSpread の提言に従う)**
   単一値でなく **\( d_j = \text{中央値}\;[\min,\max] \)** の形で報告する。

### 3.4 本プロジェクト固有の障害(コード調査で判明・実装前に必ず解消)

1. **`ablate.SECTIONS` の接頭辞リテラル一致**
   `src/society/ablate.py` L464–483 の `SECTIONS` は 9 個の接頭辞リテラル(`"知っている言葉: "` / `"直近の出来事: "` / `"記憶に残っていること: "` / `"ふと思い出したこと: "` / `"間柄: "` / `"同席の身近な人: "` / `"近くにいる人: "` / `"タイムライン: "` / `"直前のやりとり: "`)で照合し、`tests/test_placebo.py::test_section_prefixes_actually_occur_in_build_prompt` が実出力に対して機械検証している。
   → **接頭辞を言い換える variant は placebo 3 種と両立しない**。対策は 2 択: (a) 接頭辞は変えず値の側だけ言い換える(P-c を諦める)、(b) `_check_placebo_exclusion` に `prompt_paraphrase` × placebo 3 種の**相互排他**を追加する。**(b) が正しい**(placebo が既に 3 種の相互排他を実装済みなので、同じ関数に 1 行足すだけ)。

2. **CachedLLM のキャッシュミス → 実 LLM コストが P 倍**
   CachedLLM は内容アドレスキャッシュなので、プロンプト文字列が変われば全ミスする。5 セットなら実 LLM 呼び出しが 5 倍。
   → **対策**: paraphrase ラン は「主要結論の指標だけ・短いラン(≤24 step または 1 日)」に限定する。ユーザー記憶の `validation-runs-short`(修正後は mock か ≤24 step smoke のみ)と整合する。**10 日フルランを 5 本回す設計にしてはならない。**

3. **言い換えの生成方法**
   LLM で動的生成すると `affects_k=False` の構造保証を壊す(`tests/test_placebo.py::test_call_count_is_exactly_equal_under_prompt_blind_llm` が呼数完全一致を強制している)。
   → **凍結ルックアップ表**が唯一の正解。`data/` 配下に JSON + sha256(`model_battery/reference.py` の provenance schema と同じ作法)か、`ablate.py` 内の Python 定数。**生成は事前にオフラインで行い、成果物を凍結して来歴を manifest に載せる**。

4. **`metrics_spec_hash` には無関係** — paraphrase は指標定義 14 ファイルに触らないので凍結は破れない。`deliberate.py` / `ablate.py` / `registry.py` / `conf/config.yaml` はいずれも `SPEC_FILES` 外。

5. **既定 OFF の golden バイト一致は自明に成立** — 適用点が `build_prompt` 末尾の `Placebo.apply(agent, lines, step)` と同じシーム(`deliberate.py` L~378)であり、OFF 時は `lines` に一切触れない。placebo と完全に同型の構造で書ける。

6. **`fingerprint_risk` は本質的に `known`** — プロンプト文字列が変わる以上、観測が世界を変えないという主張は成立しない。placebo 3 種と同じく `known` を宣言する(`src/society/registry.py` の `_f()` エントリ)。

---

## 4. S-01: ODD 対応表(micro / macro / system 3 節テンプレ)

### 4.1 ODD 2020 の構造(一次)

Grimm et al. 2020, *The ODD Protocol for Describing Agent-Based and Other Simulation Models: A Second Update to Improve Clarity, Replication, and Structural Realism*, JASSS 23(2):7, DOI 10.18564/jasss.4259。

7 要素(3 カテゴリ):

- **Overview**: ① Purpose and patterns ② Entities, state variables and scales ③ Process overview and scheduling
- **Design concepts**: ④ Design concepts(**11 概念**: Basic principles / Emergence / Adaptation / Objectives / Learning / Prediction / Sensing / Interaction / Stochasticity / Collectives / Observation)
- **Details**: ⑤ Initialization ⑥ Input data ⑦ Submodels

2020 更新の 2 つの追加:
- **ODD summary**(論文本文用の要約 ODD): 「全モデルの物語的記述を与える」「**完全な ODD に頼らずとも主要結果が理解できる程度に具体的である**」こと。
- **シミュレーション実験の記述の標準化**: ODD 本体には**入れず** Supplement S7 の別ガイダンス扱い。理由は「実験記述の標準化は ODD と同程度に複雑になりうるので、別途の検討に値する」。

### 4.2 micro / macro / system への対応表

| ODD 要素 | 我々の報告書の対応先 | 備考 |
|---------|---------------------|------|
| ① **Purpose and patterns** | **§0 主張の境界(S-04)+ §macro 冒頭の stylized facts リスト(S-02)** | ★**最重要の接続**。ODD の "patterns" は「モデルが再現できたら成功と見なすパターン」の事前宣言欄そのもの。S-02 は独自発明ではなく **ODD 要素①の充足**である |
| ② Entities, state variables and scales | 前置き「装置編」/ `run_manifest.json` | 既存資産で充足 |
| ③ Process overview and scheduling | 装置編 / `docs/spec.md` | 既存資産で充足 |
| ④ Design concepts — **Emergence** | **§macro** | k*・規範創発・組織形成 |
| ④ — **Sensing / Objectives / Adaptation / Learning / Prediction** | **§micro** | `cognition.contract` の Perception 型がそのまま Sensing の記述になる |
| ④ — **Interaction / Collectives** | **§macro** | S-09(mode × structure × role)、S-12(offline/online 二層) |
| ④ — **Stochasticity** | **§system** + S-05 | RngHub named streams・seed 間分散分解 |
| ④ — **Basic principles** | 前置き(理論的立場) | EPR・Dunbar・7 ニーズ等の依拠理論 |
| ④ — **Observation** | **§system** | ★分野に稀な強み。no-fingerprint テスト・observer の読み取り専用性・`live_viewer.py` の別プロセス読み取り |
| ⑤ Initialization | **§system** | IPF 合成人口の周辺分布再現誤差(S-14) |
| ⑥ Input data | **§system** | PLATEAU / ODPT / 天候生成器(来歴 sha256) |
| ⑦ Submodels | 装置編(付録) | |
| **ODD summary**(2020 追加) | **報告書冒頭 1 ページ要約** | 3 節の前に置く |
| シミュレーション実験の記述(Supplement S7) | **事前登録 + `docs/research/ablation-ladder.md` §3.1** | 既に相当物を持っている |

### 4.3 各節の必須欄(S-01 のアクション本体)

3 節それぞれの冒頭に **「何と比較したか / 比較できないなら、なぜできないかと代替」** 欄を固定する。

- **§micro**: 「実個人の行動ログとの照合は**行わない**(構造上持てない)。代替は (i) `calibrate_report` の行動頻度バンド、(ii) `judge.py` の κ、(iii) **分布の分散(S-03)**」と明示宣言。**宣言することが妥当性主張になる。**
- **§macro**: stylized facts リスト(S-02)の主判定/参考の別と、各法則の合否。
- **§system**: 実行時間・資源・トークン消費・費用(サーベイ §5.3 の system の定義)+ ODD ④ Observation / ⑤ Initialization / ⑥ Input data。

### 4.4 ★用語衝突の警告(実装前に必ず決めること)

**TRAILS(Ye et al. 2026)は agent(micro)/ interaction(meso)/ **system**(macro)の 3 層を使う。サーベイ §5.3 の micro / macro / **system** とは、"system" の語が指すものが違う**:

| 語 | サーベイ §5.3 の意味 | TRAILS の意味 |
|----|---------------------|--------------|
| micro | 個体挙動の人間らしさ | agent 設計(persona 書式・記憶表現) |
| macro | 集合結果と現実の整合 | — |
| meso | — | 相互作用プロトコル |
| **system** | **実行時間・資源・スケーラビリティ・トークン消費と費用** | **集合結果・環境設計(= サーベイの macro 相当)** |

→ **対策**: 報告書では **§system(計算資源)** と括弧付きで明記し、TRAILS の 3 層は **§頑健性** の下位見出し(§頑健性.agent / .interaction / .system)として別立てにする。この整理を報告テンプレに書いておかないと、査読者が確実に混乱する。

### 4.5 LLM 社会シム向けの報告チェックリスト(現状の探索結果)

- **Larooij & Törnberg 2025**, *Validation is the central challenge for generative social simulation*, Artificial Intelligence Review, DOI 10.1007/s10462-025-11412-6(arXiv:2507.19364)— 検証実務を 4 カテゴリ(**Empirical Validation and Benchmarking / Human-in-the-Loop Evaluation / Specialized Validation Methods / Data Sources and Comparative Benchmarks**)に分類。**「micro-validity を確立しても macro-level veridicality は保証されない」**(§4.1)を明示。推奨は「初期条件・パラメータの摂動に対する感度分析」「exploratory modeling と confirmatory empirical research の区別」「長期一貫性」「実サーベイデータへの較正」。**ODD への言及は無く、分散/異質性の報告基準にも触れていない**(=我々が S-03 で埋めるのは実際に空いている穴)。
- **Bück-Kaeffer et al. 2025**, *The Silicon Society Cookbook: Design Space of LLM-based Social Simulations*(arXiv:2605.00197)— 単一チェックリストではなく多次元の設計空間(Agent Design / Interaction Architecture / Simulation Parameters / Evaluation Metrics / Software Infrastructure)。報告の透明化と比較可能性のための語彙として使える。
- **結論**: **LLM 社会シム専用の確立した報告チェックリストは 2026 年 8 月時点で存在しない。** したがって **ODD を骨格に据え、micro/macro/system をその上の読み替え層として置く**のが最も査読耐性が高い。「ODD を満たしたうえで、LLM 特有の 3 レベル評価を追加した」という構図になる。

---

## 5. S-04: 境界宣言の 4 行案

### 5.1 Wu et al. 2025 の実体

**Zengqing Wu, Run Peng, Takayuki Ito, Chuan Xiao (2025), *LLM-Based Social Simulations Require a Boundary*, arXiv:2506.19806**(2025-06-24 投稿、2026-02-05 改訂。京都大 / 大阪大 / ミシガン大 / 名古屋大)。

**基準は 3 つ**(abstract に明記、"We propose that researchers should:"):

1. **検証の深さを、研究課題が要求する異質性の水準に合わせる**(match validation depth to the heterogeneity demands of their research questions)
2. **平均の一致と並べて分散を明示的に報告する**(explicitly report variance alongside mean alignment)
3. **分散が不十分な場合、主張を集団レベルの定性的パターンに限定する**(constrain claims to collective-level qualitative patterns when variance is insufficient)

系統的レビューの結果: 大半の論文は ground truth 比較を持つが、**行動的分散を明示的に評価するのは半数未満**、評価した論文の**大半は人間集団より低い分散を報告**。

### 5.2 事前登録 §0「主張の境界」4 行案(文案)

> **① 主張する**
> 本研究は、**この設計(実地図・実ダイヤ・IPF 合成人口・全個体一様の認知予算・10 日)の下で**、世界改変志向の個体(k*)の出現に対する**初期特性の寄与と環境フィードバックの寄与の相対的大きさ**を主張する。主張は **条件間差が seed 間差を上回った指標に限る**(S-05)。集団レベルの定性的パターン(規範の成立、組織の自然形成、語の伝播)については、その成立/不成立と成立条件を主張する。
>
> **② 主張しない**
> 現実の渋谷において同じ**比率**で世界改変者が現れることは主張しない。個体の行動が特定の実在個人と一致することは主張しない。得られた協調水準・対立水準の**絶対値**が現実の水準であることは主張しない。組織サイズ分布などの**分布形の同定**(Zipf / Gibrat)は N と期間の不足により主張しない(§1 の F10/F11)。
>
> **③ 外的妥当性の限界**
> (a) LLM は 1 系統・世代固定であり、`prompt_paraphrase`(S-16)と `cognitive_tier` ablate が通っても、**別モデルファミリでの再現は主張の外**である(Ye et al. 2026 は同一摂動の効果がモデル間で 1pp〜76pp と桁違いになることを示した)。(b) 期間は 10 日であり、それ以上の時間尺度の主張はしない。(c) **LLM 社会シムは対立・不満を系統的に過小表現する(既知のバイアス)。本ランで観測された協調水準は上限側の推定値であり、対立の実在水準はこれを下回らない**(片側解釈・S-15)。(d) **分散**については §2 の分散比を必ず併記し、**分散比が事前登録の閾値を下回った指標については、主張を集団レベルの定性的パターンに限定する**(Wu et al. 基準③)。(e) 我々は分野標準と逆に**アウトライアを厚くしない**(全個体一様の認知予算)。これは k* の内生的出現を問うための設計上の選択であり、大規模時の効率を代償にしている(S-08)。
>
> **④ 反証条件**
> 次のいずれかが観測された場合、当該仮説を棄却する。(a) 条件間差が seed 間差を上回らない。(b) `prompt_paraphrase` の 5 セットのいずれかで主要結論の**符号が反転**する。(c) `ablate.llm_off`(ルール層のみ)で同じ結論が出る = LLM の寄与が無い。(d) `experiment.flat_traits`(ゼロ対照)で同じ結論が出る = 特性の寄与が無い。(e) `echo_max == 1.000` の崩壊ランが母集団の過半を占める。(f) `propagation_off` と本番の中間条件でのみ現れる構造が主結論を担っている = 境界アーティファクト(S-17)。

### 5.3 Wu の 3 基準と我々の対応表(事前登録に貼る)

| Wu et al. 2025 の基準 | 我々の対応 | 状態 |
|---|---|---|
| ① 検証の深さを異質性要求に合わせる | 研究課題が「裾の創発(k*)」= **異質性要求が最大級** → 分散の検証が必須 | S-03 で実装 |
| ② 平均と並べて分散を報告 | `calibrate_report.py` に CV / Gini / 上位 10% シェア + 分散比列 | S-03 で実装 |
| ③ 分散不十分なら主張を集団レベル定性パターンに限定 | 事前登録 §0 ③(d) に規則として固定 | S-04 で実装 |

**この 3 行の対応表を貼るだけで、「分野が 2025 年に出した境界基準を、実装で満たしている」と言える**。実装コストはほぼゼロで、査読者が最初に見る箇所である。

---

## 6. 実装への具体的示唆(バッチ分解案)

### 6.1 分解と順序

| バッチ | 項目 | 変更範囲 | `metrics_spec_hash` | golden L1 | コスト | 依存 |
|--------|------|----------|---------------------|-----------|--------|------|
| **B1** | **S-04 + S-01** | **文書のみ**。`docs/plans/stationarity-preregistration.md` に **§0 の前**へ「主張の境界」を挿入(現 §0「なぜ事前登録するか」は §0.1 に降格 or 新節を §0' とする)+ `docs/plans/observation-report-template.md` 新設 | **不変** | **不変** | 最小 | なし |
| **B2** | **S-02** | **文書のみ**。事前登録に「渋谷の stylized facts」節を追加(§3 の A–E に続けて **F 節**とするのが既存構造と整合) | **不変** | **不変** | 小 | B1(境界宣言と主判定/参考の二分が接続する) |
| **B3** | **S-03** | **コード**。`scripts/calibrate_report.py` のみ + `data/battery/reference/` に現実分散の provenance JSON 追加。**凍結表外**。Gini/CV は `scripts/model_battery/metrics.py` の既存実装を import(6 個目の Gini を書かない) | **不変**(要確認: `calibrate_report.py` は `SPEC_FILES` に**無い**) | **不変**(scripts のみ) | 中 | B2(何をバンドにするかが決まってから) |
| **B4** | **S-16** | **コード**。`conf/config.yaml`(`ablate:` L1696 付近に追加)/ `src/society/ablate.py`(`_DEFAULTS` / `build_cfg` / 述語 / `any_on` / `describe` / **`_check_placebo_exclusion` に相互排他 1 行**)/ `src/society/registry.py`(`_f("ablate.prompt_paraphrase", "strict", affects_k=?, "known", ...)`)/ `src/society/cognition/deliberate.py`(placebo と同じシーム)/ `data/` に凍結言い換え表 + sha256 / `tests/test_ablate.py` 系 | **不変** | **不変**(OFF で `lines` 不触) | **大** | B1(反証条件④(b) が paraphrase を参照する) |

### 6.2 各バッチの R1 チェックリスト(共通)

- [ ] 既定 OFF(`conf/config.yaml` の default が false / 空)
- [ ] OFF 時 golden L1 バイト一致(B3/B4)
- [ ] OFF 時 manifest / summary にキーが**生えない**(`describe()` が空を返せば `manifest.py` L190 のウォルラス代入がキーごと落とす既存構造をそのまま使う)
- [ ] `src/society/registry.py` に `_f()` エントリ(**`tests/test_registry_modes.py` が `conf/config.yaml` の全 bool リーフを走査して未申告を落とすので、書かないと CI が通らない**)
- [ ] `metrics_spec_hash` 不変の確認(= `SPEC_FILES` の 14 本に触れていないこと)
- [ ] no-fingerprint(B4 は原理的に不可 → `fingerprint_risk="known"` を正直宣言)
- [ ] `ask-before-extending`: B3/B4 はコード変更を伴うので**着手前にユーザー合意を取る**

### 6.3 B1 の注意点(既存文書構造との衝突)

`docs/plans/stationarity-preregistration.md` は **406 行 / 29KB** で、**既に `## 0. なぜ事前登録するか` を持つ**。S-04 の「§0 主張の境界」をそのまま §0 にすると衝突する。推奨は:

- 新節を **`## 0. 主張の境界`** とし、既存の §0 を **`## 0.5 なぜ事前登録するか`** に改番する(査読者が最初に見る位置に境界宣言を置くのが S-04 の狙いなので、位置は譲れない)。
- または新節を **`## -1`** ではなく **冒頭の「前文」**として節番号なしで置く(改番不要・最小変更)。**後者を推奨**(既存の §1〜§7 の参照が本文中に多数あるため)。
- 文書は **U-10 承認待ちのドラフト**であり「承認前は変更自由」と自ら宣言しているので、**今が追記の窓**である。承認後は §7 変更履歴への記録が義務になる。

### 6.4 B2 の注意点

事前登録 §3 は既に A(主判定)/ B(過渡切り分け)/ C(構造 3 指標)/ D(併読必須の派生量)/ E(規範成立の判定と下方因果)の 5 サブ節を持つ。**stylized facts は §3 の F 節**として置くのが構造的に自然(E 節と同じ「| # | 条件 | 推奨値 | 根拠 |」形式の表が使える)。E 節と同じく **承認対象**としてマークする。

### 6.5 B4 の予算注意(再掲・重要)

- CachedLLM が全ミスするので**実 LLM 呼び出しが paraphrase セット数倍**になる。
- ユーザー記憶 `validation-runs-short` に従い、**10 日フルランを 5 本ではなく、≤24 step または 1 日の短ランを 5 本**にする。
- 主要結論の効果量 \(d_j\) が短ランで推定できない場合は、**paraphrase を「10 日ランの結論」ではなく「短ランで測れる中間指標」に対してのみ適用し、その限界を報告に書く**(TRAILS の per-claim 原則に照らしても、claim ごとに測るのが正しい作法なので、これは妥協ではなく正道)。

### 6.6 やらないことの明記(ゴールドプレーティング防止)

- **`observer/aggregate.py` の Gini を触らない**(凍結が破れる)。
- **Gini の 6 個目の実装を書かない**(既存 5 実装 + `model_battery/metrics.py::cv()` を使う)。
- **`REALITY` インライン定数の全面外部化を「ついで」でやらない**(S-03 で新規に足す分散バンドのみ provenance schema に載せる)。
- **S-05〜S-18 は本バッチの範囲外**(ただし S-01 の報告テンプレは S-05/S-08/S-15/S-17 の宣言欄を空枠として用意しておくと後で安い)。

---

## 7. リンク集(アクセス日: 2026-08-05)

### 7.1 S-01(報告標準 / ODD)

- Grimm, V. et al. (2020). *The ODD Protocol for Describing Agent-Based and Other Simulation Models: A Second Update to Improve Clarity, Replication, and Structural Realism*. JASSS 23(2):7. DOI 10.18564/jasss.4259 — https://www.jasss.org/23/2/7.html
- 同 Supplement S1(ODD テンプレート) — https://www.jasss.org/23/2/7/S1-ODD.pdf
- Grimm, V. et al. (2010). *The ODD protocol: A review and first update*. Ecological Modelling 221(23):2760–2768 — https://www.bobm.net.au/teaching/SimSS/ODD_protocol.pdf
- Grimm, Polhill & Touza (2013). *Documenting Social Simulation Models: The ODD Protocol as a Standard* — https://faculty.sites.iastate.edu/tesfatsi/archive/tesfatsi/DocumentingABMODD.GrimmPolhillTouza2013.pdf
- Larooij, M. & Törnberg, P. (2025). *Validation is the central challenge for generative social simulation: a critical review of LLMs in agent-based modeling*. Artificial Intelligence Review. DOI 10.1007/s10462-025-11412-6 — https://arxiv.org/html/2507.19364 / https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12627210/
- Bück-Kaeffer, A. et al. (2025). *The Silicon Society Cookbook: Design Space of LLM-based Social Simulations*. arXiv:2605.00197 — https://arxiv.org/pdf/2605.00197

### 7.2 S-02(stylized facts)

- González, M. C., Hidalgo, C. A. & Barabási, A.-L. (2008). *Understanding individual human mobility patterns*. Nature 453:779–782. DOI 10.1038/nature06958 — https://www.nature.com/articles/nature06958
- Song, C., Koren, T., Wang, P. & Barabási, A.-L. (2010). *Modelling the scaling properties of human mobility*. Nature Physics 6:818–823. arXiv:1010.0436 — https://arxiv.org/abs/1010.0436
  - μ = 0.6 ± 0.02(S(t) ~ t^μ)は二次情報で確認済み。**ζ ≈ 1.2(f_k ~ k^{-ζ})と P_new = ρ S^{-γ} の ρ, γ の具体値は一次で未確認** → 実装前に本文 PDF で確認すること。
- Song, C., Qu, Z., Blumm, N. & Barabási, A.-L. (2010). *Limits of Predictability in Human Mobility*. Science 327:1018–1021. DOI 10.1126/science.1177170 — https://barabasi.com/media/2010-Song_et_al-Limits_of_Predctiability-Science.pdf(「93% potential predictability」)
- Barabási, A.-L. (2005). *The origin of bursts and heavy tails in human dynamics*. Nature 435:207–211. DOI 10.1038/nature03459 — https://www.nature.com/articles/nature03459
- Goh, K.-I. & Barabási, A.-L. (2008). *Burstiness and memory in complex systems*. EPL 81:48002 — https://arxiv.org/pdf/physics/0610233(burstiness \(B=(\sigma-m)/(\sigma+m)\) の定義元)
- Cattuto, C., Van den Broeck, W., Barrat, A., Colizza, V., Pinton, J.-F. & Vespignani, A. (2010). *Dynamics of Person-to-Person Interactions from Distributed RFID Sensor Networks*. PLOS ONE 5(7):e11596 — https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0011596
- SocioPatterns — https://sociopatterns.org/
- *On the duration of face-to-face contacts*. EPJ Data Science (2023) — https://link.springer.com/article/10.1140/epjds/s13688-023-00444-z
- Axtell, R. L. (2001). *Zipf Distribution of U.S. Firm Sizes*. Science 293:1818–1820. DOI 10.1126/science.1062081 — https://faculty.sites.iastate.edu/tesfatsi/archive/tesfatsi/ZipfDistributionFirmSizes.RAxtell2001.pdf
- 東京都市圏パーソントリップ調査(第 6 回集計結果概要) — https://www.spt.metro.tokyo.lg.jp/tosei/hodohappyo/press/2019/11/27/02.html / データ利用の手引き https://www.tokyo-pt.jp/static/hp/file/data/tebiki.pdf
- 全国の人流オープンデータ(1km メッシュ、市区町村単位発地別)国土交通省 / G 空間情報センター — https://www.geospatial.jp/ckan/dataset/mlit-1km-fromto / 公開告知 https://www.mlit.go.jp/tochi_fudousan_kensetsugyo/tochi_fudousan_kensetsugyo_fr17_000001_00006.html

### 7.3 S-03(分散バンド)

- Wu, Z., Peng, R., Ito, T. & Xiao, C. (2025). *LLM-Based Social Simulations Require a Boundary*. arXiv:2506.19806 — https://arxiv.org/abs/2506.19806 / https://arxiv.org/pdf/2506.19806 / OpenReview https://openreview.net/pdf?id=1T1SE9xxAB
- Bisbee, J. et al. (2024). LLM 生成のサーベイ回答(ANES 再現)— 平均は似るが**分散が小さく裾を過少表現**。二次記述: https://arxiv.org/pdf/2509.26080(*Evaluating the Use of LLMs as Synthetic Social Agents in Social Science Research*)/ https://arxiv.org/pdf/2507.02919(*Representativeness and Structural Consistency of Silicon Samples*)
- 社会生活基本調査(令和 3 年・総務省統計局)生活時間に関する結果 主要統計表 — https://www.e-stat.go.jp/stat-search/files?page=1&layout=datalist&lid=000001298496 / 調査全体 https://www.e-stat.go.jp/stat-search/files?toukei=00200533
- モバイル空間統計(e-Stat ビッグデータポータル) — https://www.e-stat.go.jp/bigdataportal/dataintro/130
- Gini / CV / 上位シェアの指標選択:
  - Our World in Data, *Measuring inequality: what is the Gini coefficient?* — https://ourworldindata.org/what-is-the-gini-coefficient
  - *A note on the relationship between top income shares and the Gini coefficient* — https://www.sciencedirect.com/science/article/abs/pii/S0165176510003460
  - *The Gini Coefficient as a useful measure of malaria inequality among populations*(Gini と CV が同一関数の L¹/L² ノルムであること・分散指標の使い分け) — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7709295/

### 7.4 S-16(prompt paraphrase)

- Sclar, M., Choi, Y., Tsvetkov, Y. & Suhr, A. (2024). *Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design, or: How I learned to start worrying about prompt formatting*. ICLR 2024. arXiv:2310.11324 — https://arxiv.org/abs/2310.11324 / コード https://github.com/msclar/formatspread
- Zhu, K. et al. (2023). *PromptRobust / PromptBench: Towards Evaluating the Robustness of Large Language Models on Adversarial Prompts*. arXiv:2306.04528 — https://arxiv.org/abs/2306.04528 / https://github.com/microsoftarchive/promptbench
- Ye, J., Cao, L., Chen, D. & Ferrara, E. (2026). *Stop Drawing Scientific Claims from LLM Social Simulations Without Robustness Audits*. arXiv:2605.18890(2026-05-17)— https://arxiv.org/abs/2605.18890 (**TRAILS**: agent / interaction / system の 3 層監査分類)
- *Measuring LLMs' Sensitivity to Paraphrased Opinion Prompts*. WASSA 2026 — https://aclanthology.org/2026.wassa-1.5/ (200 質問 × 5 人手検証 paraphrase)
- *Towards LLMs Robustness to Changes in Prompt Format Styles*. arXiv:2504.06969 — https://arxiv.org/html/2504.06969v1
- *Paraphrase-Induced Output-Mode Collapse: When LLMs Break Character Under Semantically Equivalent Inputs*. arXiv:2605.04665 — https://arxiv.org/html/2605.04665v2(**ペルソナ崩壊が言い換えで起きる**= S-18 とも接続)

### 7.5 S-04(境界宣言)

- Wu et al. 2025(上記 7.3 と同一。**3 基準の一次ソース**)
- 本プロジェクト内の接続先: `docs/research/llm-social-sim-survey.md` §3 S-04 / S-08 / S-15 / S-17、`docs/plans/stationarity-preregistration.md` §0・§5・§6・§7

---

## 8. 本文書の限界(正直な列挙)

1. **Song et al. 2010 の ζ・ρ・γ の具体値は一次確認できていない**(PDF がテキスト抽出不能だった)。μ = 0.6 ± 0.02 のみ二次で確認。**F2/F3 を事前登録に書く際は、本文 PDF から数値を取り直すこと**。ただし F2/F3 は「参考」枠なので、主判定には影響しない。
2. **Bisbee et al. 2024 は書誌情報(掲載誌・巻号)を一次で確認していない**。二次記述(3 本の 2025–2026 年論文が一致して引用)による。事前登録に引く前に書誌を確定すること。
3. **社会生活基本調査の「時間帯別行動者率」表の実データを開いていない**。「行動者率から分散の下界を復元する」手続き(§2.3)は数学的には正しいが、**実際に p と m が同一表で取れるか**は e-Stat のファイルを開いて確認する必要がある。
4. **渋谷固有の stylized facts(F1 の二峰性の定量形)の一次数値を取っていない**。東京都市圏 PT 調査の第 6 回概要が「朝ピークは横ばい、昼以降減少」と述べる程度までしか確認できていない。ただし F1 は「参考」枠なので主判定には影響しない。
5. **本文書はコードを 1 行も変更していない**。§6 のバッチ分解は提案であり、B3/B4 の着手には `ask-before-extending` に従いユーザー合意が必要。
