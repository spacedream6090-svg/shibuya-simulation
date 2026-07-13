# 生データ処理・可視化 8項目の標準手法調査 — 2026-07-14・担当Opus

読み手: 実装計画を書く親エージェント(Fable)。**本書はリサーチのみ・コード変更なし。**
方針は `docs/plans/data-strategy.md`(生=正準・最小/指標=後処理で派生・L1=`l1_events.parquet` が正準)に従う。
各項目は「標準手法(出典)/本シミュの既存資産と穴/推奨の最小実装(L1 から何をどう集計するか)/工数感」で書く。
値はすべて **ログ由来の what-if 実験値**であり渋谷の実測ではない(既存レポート群の誠実性条項を継承)。

---

## 0. 一覧表(8項目 × 既存の充足度)

| # | 項目 | 状態 | 既存の中核資産 | 主な穴 | 工数 |
|---|---|---|---|---|---|
| ① | 人流ヒートマップ | 一部あり | `export_3d`/`make_viewer`(点・軌跡)・`commercial_report` footfall | 空間**密度格子**(cell×時間)集計・KDE/hexbin が無い | 小 |
| ② | OD行列 | 一部あり | `commercial_report.analyze_circulation`(建物間遷移) | ゾーン分割・時間帯別・**目的別**・域外gatewayのODが無い | 中 |
| ③ | 混雑ランキング | 一部あり | footfall ランキング・`crowd_surge`・`vision-los.md` | 面積正規化した **Fruin LOS(人/m²)** が無い | 小 |
| ④ | エージェント行動統計 | 既存あり | `build_panel`(agent_day)・`calibrate_report`・`panel_stats` | 生活時間調査型の**時間配分/時刻別プロファイル**・分布一致検定 | 小 |
| ⑤ | 社会ネットワークの変化 | 既存あり | `analyze_communities`(窓別louvain・ライフサイクル)・`observe_flows`注意 | **全体メトリクスの時系列**(密度/クラスタ係数/次数分布)・tie decay・alluvial | 小 |
| ⑥ | 介入前後の比較 | 一部あり | `panel_stats` ペア比較(同seed差・CI)・`scenario_shock` | DiD・**置換検定**・CRN健全性チェック(実行パス破れ) | 中 |
| ⑦ | 統計的有意性 | 一部あり | `panel_stats`(mean±95%CI・n≥5・ペア比較) | **効果量**・多重比較補正・順位検定・p値の限界注記 | 小 |
| ⑧ | LLM自然言語要約 | 一部あり | 各 `*_report.md`(決定論テンプレ)・`judge.py`(R4防壁) | **計算済み数値のみ言語化する制約生成**+忠実性検証 | 中 |

- **最も工数が要る**: ② OD行列(ゾーン定義と目的帰属の設計)と ⑥ 介入比較(DiD/CRN健全性の設計)。
- **最も安く効く**: ⑦ 統計的有意性(`panel_stats` 純Python拡張)と ③ 混雑LOS(①の格子ができれば面積割り+閾値だけ)。
- **設計上の鍵**: ①→③→② は **同一の空間グリッド projection** を共有できる。cell 集計器を1つ作れば、密度ヒートマップ(①)・面積割りLOS(③)・cell を OD ゾーンに束ねる(②)が同じ土台から派生する。**最初に汎用グリッド器を1本作るのが最小コスト**。

---

## ① 人流ヒートマップ

**標準手法(出典)**
- 時空間密度の可視化は (a) **固定グリッド集計**(メッシュ別カウント)、(b) **hexbin**(六角ビニングで過剰描画を抑制)、(c) **KDE**(カーネル密度・連続面のヒートマップ)の3系統が定番。KDE は各点にカーネルを畳み込み色で密度を表す非パラメトリック法で、人流では帯域幅 ~500m がよく使われる([MapServer KDE](https://mapserver.org/output/kerneldensity.html)、[geoplotlib arXiv:1608.01933](https://arxiv.org/pdf/1608.01933)、[GPS活動空間 arXiv:1708.05017](https://arxiv.org/pdf/1708.05017))。
- 人流オープンデータの慣行: 国交省の全国人流データは **1kmメッシュ×滞在人口**で配布・可視化ツールで流線図/密度表示、NTTドコモ「モバイル空間統計」は **500mメッシュ×1時間**の滞留人口([国交省 人流データ可視化ツール2.0](https://www.mlit.go.jp/tochi_fudousan_kensetsugyo/chirikukannjoho/tochi_fudousan_kensetsugyo_tk17_000001_00033.html)、[e-Stat モバイル空間統計](https://www.e-stat.go.jp/bigdataportal/dataintro/130))。**メッシュ×時間帯×属性の集計が業界標準の粒度**。
- シミュレータの密度出力: MATSim は各リンク/エリアの通過・滞在を出力([matsim.org](https://matsim.org/))。SUMO は `edgeData` でエッジ密度・占有率を吐く(要一次確認・未fetch)。**いずれも「空間単位×時間ビンのカウント/占有」を正準出力とする**。

**本シミュの既存資産と穴**
- あり: `viz/make_viewer.py`(`move_segment` から位置を再構成し地図に点描画・レイヤ再生)、`scripts/export_3d.py`(tracks 時系列)、`commercial_report` footfall(建物別 `enter_building` の延べ/ユニーク・ピーク時・時間帯×曜日カウント、街路 footfall = `move_segment` 総数)。
- 穴: いずれも**点・軌跡・建物別カウント**であって、**空間を格子に切った密度面(cell×時間ビンの同時在圏 or 通過密度)**を出す projection が無い。KDE/hexbin も無い。L1 には材料が揃う: `move_segment {from_xy,to_xy}`・`arrive {node}`(x,y付き)・`stay`・`enter_building`。

**推奨の最小実装(L1 から)**
1. 汎用グリッド器: 各イベントの (x,y) を固定メッシュ(例 25m or 50m)へビニング → `(cell_x, cell_y, time_bin)` を単位に **通過カウント**(`move_segment.to_xy`)と **在圏カウント**(`arrive`/`stay`/在館は建物 centroid)を集計。
2. 出力 `panel/heatmap_grid.parquet`(cell_x, cell_y, hour|step_bin, pass_count, present_count, unique_agents)。
3. 可視化はビューアの既存レイヤに density オーバーレイを足すか、静的 PNG。KDE は任意(`scipy.stats.gaussian_kde`。依存が無ければ格子集計で十分・標準的)。

**工数感**: 小。既存の位置再構成(`make_viewer` 82–125行/`export_3d` に移植済み)を再利用し空間ビニングするだけ。~150行の読み出し専用1スクリプト。

---

## ② OD行列(Origin-Destination)

**標準手法(出典)**
- 交通工学の標準: 空間を**ゾーン(TAZ)**に分割し、`origin_zone × dest_zone` のトリップ数行列を作る。実務では **時間帯別**(ピーク/オフピーク)・**目的別**(通勤/業務/買物/私事)に層別する([OD/フロー可視化 ECMブログ](http://ecmapping.blogspot.com/2015/04/transportation-data-visualization-1.html))。
- 可視化: **flow map**(ゾーン重心間を曲線・太さ=流量)と **chord/connection barchart**(円周にゾーン・弦で流量)。chord は地理位置を示せない弱点、flow map は地理を保つ([コネクション棒グラフ+連携地図 RG:302073841](https://www.researchgate.net/publication/302073841_Visualization_of_origin-destination_matrices_using_a_connection_barchart_and_coordinated_maps))。国交省ツールは**エリア間移動ログからOD表→流線図**を生成([同上](https://www.mlit.go.jp/tochi_fudousan_kensetsugyo/chirikukannjoho/tochi_fudousan_kensetsugyo_tk17_000001_00033.html))。
- シミュ/軌跡からのOD抽出: 軌跡やセンサ計数から時間帯別ODを推定するのが標準([次元削減OD推定 arXiv:1810.06077](https://arxiv.org/pdf/1810.06077))。シミュは真値ODを直接出せる利点がある(推定不要)。

**本シミュの既存資産と穴**
- あり: `commercial_report.analyze_circulation`(同一 agent×日 の `enter_building` 系列 → **建物間遷移行列**・上位フロー)。`observe_flows` の金流/注意エッジ(社会ODに近いが空間ODでない)。
- 穴: (a) **ゾーン分割が無い**(建物 id 単位で粗い/細かい)。(b) **時間帯別・目的別の層別が無い**。(c) `route_start {dest}`・`arrive {node}`・`exit_area`/`enter_area {gateway}`(域外流出入)を使ったトリップ定義が未活用。

**推奨の最小実装(L1 から)**
1. トリップ = 連続する滞在地点の遷移。素材: `route_start→arrive`(明示的目的地つき)か、`arrive`/`enter_building` の時系列隣接ペア。
2. ゾーン写像: ①のグリッド cell、または地名/建物カテゴリのクラスタへ node/建物を束ねる。`exit_area`/`enter_area` の `gateway` を**外部ゾーン**として1行に含める(渋谷の域外流出入を捉える)。
3. 目的帰属: 到着後の行動で近似(`spend.cat`・到着建物 `bcat`・`day_plan`)。work/food/shop/leisure/home へ写像。
4. 出力 `panel/od_matrix.parquet`(origin_zone, dest_zone, hour_bin, purpose, trips, unique_agents)。可視化は flow map(ビューア)/chord。

**工数感**: 中。ゾーン定義と目的帰属の設計判断が要る(①の grid を流用すれば軽くなる)。~200行。

---

## ③ 混雑ランキング(歩行者LOS)

**標準手法(出典)**
- 歩行者混雑の事実上の標準は **Fruin の Level of Service(LOS A–F)**。密度(人/m² または m²/人)・速度・流率で 6 段階に格付け([Fruin/gkstill](https://www.gkstill.com/Support/crowd-flow/fruin/Fruin1.html)、[Crowd Dynamics Ch.3](https://www.gkstill.com/CV/PhD/Chapter3.html))。HCM の歩行者LOS も Fruin 由来([FHWA HCM Ch.13](https://highways.dot.gov/media/8521)、[NYC HCM法 Ch.2](https://www.nyc.gov/assets/planning/download/pdf/plans/transportation/td_pedloschaptertwo.pdf))。
- 数値の目安(**要一次確認: HCM/Fruin原典で確定してから掲載**): 歩道の面積基準で LOS A ≥ 約3.3 m²/人(≥35 ft²/人・自由歩行)、… LOS F < 約0.5 m²/人(接触不可避)。「ジャム密度」は約 0.25 m²/人。混雑安全の実務では **4–5 人/m² 超で危険域**([検索要約: 35 ft²/人=LOS A、0.25 m²/人=jam])。流率基準の別表(人/m/分)もある(A<23 … F>82)([digitwin Service Level Analysis](https://docs.idigitaltwin.org/docs/peddesign/service-level-analysis/))。
- 駅/街路の実務: メッシュ×時間帯の同時滞在人数を面積で割り LOS を色分けするのが定石(①のオープンデータ可視化と同じ土台)。

**本シミュの既存資産と穴**
- あり: `commercial_report` footfall(建物 visits/unique/**peak_hour**・時間帯×曜日ピーク)、`crowd_surge` イベント(スクランブル等への集中を L1 で記録)、`docs/research/vision-los.md`(視覚遮蔽用途で LOS 概念は既出)。
- 穴: footfall は**延べ入館**で瞬間密度でない。**面積正規化した人/m² と Fruin LOS 格付けが無い**。街路の**同時在圏人数(占有)**を出していない。

**推奨の最小実装(L1 から)**
1. ①のグリッド器の **present_count(cell×time_bin の同時在圏人数)** を再利用 → cell 面積で割り **人/m²** → Fruin 閾値で **LOS A–F** に格付け。
2. 出力: cell/node × 時間帯を LOS 降順に並べた**混雑ランキング**。`crowd_surge` の発火 cell と突合(検証)。
3. 建物は延床面積が無いので LOS は出さず**相対混雑(在館者数/そのcellピーク)**に留める(捏造回避)。街路グリッドで LOS を出すのが素直。

**工数感**: 小〜中。①ができていれば面積割りと閾値付けの増分(~100行)。**最も安く効く候補**。

---

## ④ エージェント行動統計

**標準手法(出典)**
- ABM の行動出力を人間データと比べる標準形式は **生活時間調査(time-use survey)との照合**: 1日の**活動時間バジェット**(睡眠/仕事/移動/食事/余暇の時間配分)と、**時刻別の活動プロファイル(tempogram)**。ETHOS.ActivityAssure など活動プロファイル評価枠組みや、TUS を ABM の活動確率の土台に使う手法が確立([TUSをMASで使う RG:314522291](https://www.researchgate.net/publication/314522291_Using_Time_Use_Surveys_in_Multi_Agent_based_Simulations_of_Human_Activity)、[日次時間配分モデリング比較](https://www.sciencedirect.com/org/science/article/pii/S2324993526000552))。MATSim は各エージェントに24h活動アジェンダを持たせる([matsim.org](https://matsim.org/))。
- 比較は点推定だけでなく**分布の一致**(滞在時間分布・活動継続時間)を KS/EMD で見るのが望ましい。

**本シミュの既存資産と穴**
- あり: `build_panel` の **agent_day パネル**(sleep_h・work_h・wage・spend カテゴリ別・speak・移動距離・POI訪問…)、`calibrate_report`(睡眠・労働・エンゲル・犯罪率などを**現実バンド lo..hi と照合**・出典つき・NHK国民生活時間調査/社会生活基本調査を既に引用)、`panel_stats`(シード横断CI)、`free_action` の価値4軸。
- 穴(**calibrate との差分だけ**): calibrate は「集計値 vs バンド」。無いのは (a) **1日の時間配分(カテゴリ別 分/日 の内訳)を生活時間調査形式で並べる表**、(b) **時刻別 activity プロファイル(24h × カテゴリの在圏割合 = tempogram)**、(c) **分布形の一致検定**(点推定でなく KS/EMD)。

**推奨の最小実装(L1 から)**
1. agent_day を**活動時間バジェット**に拡張: `sleep_start/wake_up`・在館(勤務先=work)・`move_segment`(移動)・`spend food/nightlife`・`media_use`・`study` の分/日を集計。
2. tempogram: step(=時刻)ごとに「各カテゴリに居た agent 割合」を 24h×カテゴリ行列で出す。
3. calibrate に「時間配分」節と、分布比較(`scipy` 無しでも自作 KS/EMD)を追加。既存資産が厚いので**拡張で足りる**。

**工数感**: 小。`build_panel`/`calibrate_report` の拡張。

---

## ⑤ 社会ネットワークの変化(temporal network)

**標準手法(出典)**
- temporal network analysis の標準: 観測を**時間窓(スナップショット)**に分け、窓ごとに **密度・平均次数・クラスタ係数・次数分布・中心性**を計算し**時系列**として並べる([Graph Metrics for Temporal Networks arXiv:1306.0493](https://arxiv.org/pdf/1306.0493)、[実ネットへの適用 arXiv:1305.6974](https://arxiv.org/pdf/1305.6974)、[Time-Varying Graphs & SNA arXiv:1102.0629](https://arxiv.org/pdf/1102.0629)、[Computational Human Dynamics arXiv:1907.07475](https://arxiv.org/pdf/1907.07475))。
- **tie decay**(紐帯の減衰・寿命)= エッジの初出→最終出現スパンや、非活性化までの時間の分布。中心性は時間順序を考慮した temporal 版が上位だが、窓別の静的中心性でも実務は足りる。
- 可視化: コミュニティの合流/分裂は **alluvial / stream(sankey 状)** で窓遷移を描く。ライフサイクル語彙(誕生/成長/合流/分裂/消滅)は Palla 2007 が定番(既存 doc で既出)。

**本シミュの既存資産と穴**
- あり: `analyze_communities`(窓別 louvain/LPA・modularity・**E-I index**・内部密度・PageRankリーダー・**ライフサイクル birth/grow/merge/split/death**・NMI・組織との乖離)、`observe_flows` の**有向注意グラフ**(gini・相互ペア)、`measure.communities`。`docs/research/community-detection.md`。
- 穴: (a) **ネットワーク全体メトリクスの時系列**(窓ごとの density/mean_degree/**global clustering coefficient**/次数分布/最大連結成分)が1本の系列として出ていない。(b) **tie decay/紐帯寿命**が無い。(c) alluvial 用の窓遷移データ(`dynamic_community_id` の推移)を出していない(値は保持済み)。

**推奨の最小実装(L1 から)**
1. `analyze_communities.build_window_graph` を再利用し、窓ごとに **global metrics** を `panel/network_ts.parquet`(window, day, n_nodes, n_edges, density, mean_degree, clustering_coeff, degree_gini, giant_component_frac, mean_tie_weight)へ。
2. tie decay: 各エッジの初出窓→最終出現窓のスパン分布、および N 窓連続で非活性化した割合。
3. alluvial: 既存 `dynamic_community_id` を窓×コミュニティで並べるだけ(検出は再利用)。

**工数感**: 小。既存の窓グラフ構築を再利用。~150行。

---

## ⑥ 介入前後の比較(処置効果推定)

**標準手法(出典)**
- ABM の処置効果は **paired counterfactual**(同一シードで介入あり/なしを走らせる)+ **共通乱数 CRN(common random numbers)**で分散削減するのが標準([Taming Randomness in ABMs using CRN arXiv:2409.02086](https://arxiv.org/html/2409.02086v1)、[When Does Pairing Seeds Reduce Variance arXiv:2512.24145](https://arxiv.org/pdf/2512.24145))。ペア差推定量は `(1/m)Σ(Y_i−X_i)`、SE はペア差の標本から。
- **重要な落とし穴**: CRN は「同じ draw index が両シナリオで同じイベントを引く」前提。介入が**実行パスを変える**とステートフル PRNG でこの前提が破れる → イベント鍵付きハッシュで乱数を引くのが対策([Event-Keyed Hashing arXiv:2603.11084](https://arxiv.org/pdf/2603.11084))。**本シミュは rng_stream をイベント単位で持つので優位**(schema の `Event.rng_stream`)。
- within-run の **DiD(差の差)**: 介入時刻の前後 × 処置/対照群で `(after−before)_treat − (after−before)_control`。分布フリーの有意性は **permutation test(置換検定)**(ラベル/符号を入替えて帰無分布を作る)。

**本シミュの既存資産と穴**
- あり: `panel_stats` の**条件×同seed ペア比較**(差=cond B−cond A・95%CI・分散削減)、`scenario_shock` イベント(摂動の発動/解除・step・phase を L1 記録)、`data-strategy.md`(「k条件間は同seedでペア比較」明記)。
- 穴: (a) **DiD**(介入 step 前後×処置/対照)が無い。(b) **置換検定**による p 値が無い(現状 CI のみ)。(c) **CRN 健全性チェック**(介入ランと対照ランで**介入前の L1 が step 単位でバイト一致するか**=実行パス破れの検出)が無い。

**推奨の最小実装(L1 から)**
1. between-run: 既存ペア差を **permutation test** で p 値化(純Python・符号反転 2^n or ラベル入替)。
2. within-run DiD: `scenario_shock.at` を境に、処置対象 vs 非対象(または介入ラン vs 対照ラン)の (after−before) 差の差。
3. CRN 健全性: 2ランの L1 を介入 step まで突合(`build_panel` stage0 の決定論チェックを2ラン差分へ拡張)。破れていれば「CRN前提崩壊」を警告。

**工数感**: 中。permutation は小、DiD と CRN 突合は設計が要る。~200行。

---

## ⑦ 統計的有意性

**標準手法(出典)**
- ABM 出力解析の標準: **複数ラン**の平均±CI、**効果量**、**多重比較補正**、**順位ベース検定**。分布形に敏感な正規前提を避け、保守的な **Wilcoxon 順位和**や経験的検出力推定が推奨([JASSS: Complexities of ABM Output Analysis](https://jasss.soc.surrey.ac.uk/18/4/4.html))。
- **「シミュのp値」の限界**: N=ラン数を無限に増やせるので、**些少な効果でも p を任意に小さくできる** → 統計的有意 ≠ 実質的有意。**効果量と CI 幅を主指標に、p は従**([最小効果量の検出力 SAGE 2024](https://journals.sagepub.com/doi/10.1177/25152459241240722))。多重比較は Holm または **BH-FDR** で補正。CI は n<30 で t 分布(正規近似は粗い)。

**本シミュの既存資産と穴**
- あり: `panel_stats`(各ラン=1標本の **mean±95%CI 正規近似**・**n≥5 seed を主張の最低ライン**と明記・条件×同seed ペア比較)、`build_panel` stage0(schema/欠落/重複の決定論検証)。
- 穴: (a) **効果量**(paired Cohen's d / Cliff's δ)が無い。(b) **多重比較補正**が無い(指標13本を並べているので FDR 必須)。(c) **順位/置換検定**が無い。(d) CI が 1.96 正規近似固定(n 小で粗い→ t 分布)。(e) **p値の限界注記**が無い。

**推奨の最小実装**
- `panel_stats` に列追加: paired Cohen's d、Cliff's δ、Wilcoxon/permutation p、BH-FDR 補正後 q、t 分布 CI(n<30)。純Python で実装可(既存が純Python)。
- レポート冒頭に免責:「p 値は seed 数で任意に小さくできる。効果量と CI 幅を主、p を従とし、実質的有意性で判断する」。

**工数感**: 小。`panel_stats` 拡張のみ。~120行。**最も安く効く候補その2**。

---

## ⑧ LLM による自然言語要約(忠実性)

**標準手法(出典)**
- data→text の中核課題は **hallucination(幻覚)**。構造データと文の乖離から、原表に反する **intrinsic**(例: 数値矛盾)と、原表に無い **extrinsic**(余計な比較・因果)が生じる([NLG幻覚サーベイ arXiv:2202.03629](https://arxiv.org/pdf/2202.03629))。**数値を含む table-to-text は数値推論を要し特に脆い**。
- **数値hallucination対策の定石**:
  1. **制約付き生成**: LLM に「**与えた表の数値のみ使い、表に無い数値・比較・因果を作らない**」と制約(content-matching / entity-centric grounding)([忠実な表→文 content制約 arXiv:2005.00969](https://arxiv.org/pdf/2005.00969)、[ToTTo 制御付き table-to-text arXiv:2004.14373](https://arxiv.org/pdf/2004.14373))。**計算は Python で確定させ、LLM は言語化のみ**(数値はテンプレ穴埋め/token で渡す)。
  2. **忠実性の後検証**: 生成文の主張が原表に entail するかを NLI/QA で照合。指標は **PARENT/PARENT-T**(表に entail する n-gram の precision/recall、Dhingra 2019)や NLI ベース(Dušek & Kasner 2020)([忠実性サーベイ arXiv:2203.05227](https://arxiv.org/pdf/2203.05227))。最小実装は**生成文から数値を正規表現抽出し原表と exact-match 照合**(不一致=リジェクト/再生成)。
- **R4 防壁との整合**: 要約は**読み手向けの projection** であり、`judge.py` と同じく **シミュ本体へ逆流させない**(scripts/ 配下・L1 の読み出し専用下流・src/ へ書き込まない)。既存 `docs/research/llm-human-fidelity.md` §3(hallucination/confabulation/grounding)が上位文献。

**本シミュの既存資産と穴**
- あり: 各 `*_report.md`(`commercial_report`/`observe_flows`/`analyze_communities`/`calibrate_report`/`panel_stats`)は**決定論テンプレで数値を Python 集計→文字列化**=既に「計算済み数値だけを載せる」を満たす。`judge.py`(R4防壁・別ファミリ推奨・κ)。
- 穴: (a) **LLM による自然言語要約器そのものが無い**(現状はテンプレ日本語)。(b) LLM を挟む場合の**制約生成**と**数値照合ガード**が無い。

**推奨の最小実装**
1. 既存テンプレ .md/parquet を**一次真実**として固定。
2. LLM 要約器: 確定 KPI 表(JSON/parquet)を入力に「表の数値のみ使用・表に無い比較/因果/数値を禁止」制約プロンプト。実装は既存 `src/society/llm/router` を read-only 利用(**別ファミリ推奨**は judge と同様)。
3. 後検証ガード: 生成文の数値を正規表現抽出 → 原表と exact-match。不一致は破棄/再生成。忠実性スコア=数値一致率(+任意で NLI entailment)。
4. R4: 出力は読み手向けのみ。src/ へ非依存。

**工数感**: 中。LLM 呼び出し + 数値照合ガード。~200行。既存 llm router を流用可。

---

## 9. 実装順序と共通土台(親エージェント向けメモ)

依存関係を踏まえた推奨順序(すべて **L1 読み出し専用**・sim本体/schema/`measure.py` は不変):

1. **汎用グリッド器**(新規1本)を最初に作る。(x,y)→固定メッシュのビニングで `pass_count`/`present_count`/`unique_agents` を `(cell, time_bin)` 単位に出す。→ ① をこれで完成、③ は面積割り+Fruin閾値の増分、② は cell を OD ゾーンに束ねる形で流用。**3項目が1つの土台から派生する**のが最大の省力ポイント。
2. **`panel_stats` 拡張**(⑦): 効果量・BH-FDR・順位/置換検定・t分布CI・p値限界注記。純Pythonで独立に着手可・依存なし。→ ⑥ の permutation/DiD がこの統計関数群を再利用する。
3. **⑥ 介入比較**: ⑦ の検定関数 + `scenario_shock` + `rng_stream` を使い、between-run permutation・within-run DiD・CRN健全性突合。
4. **⑤ ネットワーク時系列**: `analyze_communities.build_window_graph` を再利用し global metrics 時系列 + tie decay + alluvial データ。既存資産が厚く独立。
5. **④ 行動統計**: `build_panel`/`calibrate_report` に時間配分・tempogram・分布検定を増設。
6. **⑧ LLM要約**: 上記が出す確定表(parquet/JSON)を入力に制約生成+数値照合ガード。**最後に置く**(下流の下流・上流の表が固まってから)。

共通の誠実性規約(既存レポート群から継承): 該当イベント0件は「データ不足」と明記・値の捏造禁止・warmup(既定7日)は解析側で除外選択・決定論(ソート順・seed固定)。

---

## 出典(URL・本文で参照。🔶=二次/要一次確認)

**① 人流ヒートマップ**
- MapServer KDE dynamic heatmap: https://mapserver.org/output/kerneldensity.html
- geoplotlib(地理可視化Pythonツールボックス) arXiv:1608.01933: https://arxiv.org/pdf/1608.01933
- GPS活動空間の密度ランキング(帯域幅~500m) arXiv:1708.05017: https://arxiv.org/pdf/1708.05017
- 国交省 人流データ可視化ツール2.0: https://www.mlit.go.jp/tochi_fudousan_kensetsugyo/chirikukannjoho/tochi_fudousan_kensetsugyo_tk17_000001_00033.html
- e-Stat モバイル空間統計(NTTドコモ・500mメッシュ/1時間): https://www.e-stat.go.jp/bigdataportal/dataintro/130
- MATSim: https://matsim.org/  🔶SUMO edgeData 密度出力は未fetch=要確認

**② OD行列**
- OD/フロー可視化総説(ECMブログ): http://ecmapping.blogspot.com/2015/04/transportation-data-visualization-1.html
- コネクション棒グラフ+連携地図でのOD可視化 RG:302073841: https://www.researchgate.net/publication/302073841_Visualization_of_origin-destination_matrices_using_a_connection_barchart_and_coordinated_maps
- OD推定(次元削減) arXiv:1810.06077: https://arxiv.org/pdf/1810.06077

**③ 混雑ランキング(Fruin LOS)**
- Fruin LOS(gkstill): https://www.gkstill.com/Support/crowd-flow/fruin/Fruin1.html
- Crowd Dynamics Ch.3(密度・安全域): https://www.gkstill.com/CV/PhD/Chapter3.html
- digitwin Service Level Analysis(流率LOS表): https://docs.idigitaltwin.org/docs/peddesign/service-level-analysis/
- FHWA HCM Ch.13 Pedestrians: https://highways.dot.gov/media/8521
- NYC 歩行者LOS(HCM法) Ch.2: https://www.nyc.gov/assets/planning/download/pdf/plans/transportation/td_pedloschaptertwo.pdf  🔶面積基準の数値閾値は原典で確定要

**④ 行動統計(生活時間調査)**
- TUS を MAS で使う RG:314522291: https://www.researchgate.net/publication/314522291_Using_Time_Use_Surveys_in_Multi_Agent_based_Simulations_of_Human_Activity
- 日次時間配分モデリング比較: https://www.sciencedirect.com/org/science/article/pii/S2324993526000552

**⑤ temporal network**
- Graph Metrics for Temporal Networks arXiv:1306.0493: https://arxiv.org/pdf/1306.0493
- 実ネットへの temporal metrics 適用 arXiv:1305.6974: https://arxiv.org/pdf/1305.6974
- Time-Varying Graphs & SNA arXiv:1102.0629: https://arxiv.org/pdf/1102.0629
- Computational Human Dynamics arXiv:1907.07475: https://arxiv.org/pdf/1907.07475

**⑥ 介入前後の比較**
- Taming Randomness in ABMs using CRN arXiv:2409.02086: https://arxiv.org/html/2409.02086v1
- When Does Pairing Seeds Reduce Variance arXiv:2512.24145: https://arxiv.org/pdf/2512.24145
- Event-Keyed Hashing(CRN実行パス破れ対策) arXiv:2603.11084: https://arxiv.org/pdf/2603.11084

**⑦ 統計的有意性**
- JASSS: The Complexities of ABM Output Analysis: https://jasss.soc.surrey.ac.uk/18/4/4.html
- 最小効果量の検出力(CI アプローチ) SAGE 2024: https://journals.sagepub.com/doi/10.1177/25152459241240722

**⑧ LLM忠実性**
- Survey of Hallucination in NLG arXiv:2202.03629: https://arxiv.org/pdf/2202.03629
- Faithfulness in NLG 体系サーベイ arXiv:2203.05227: https://arxiv.org/pdf/2203.05227
- 忠実な表→文(content-matching制約) arXiv:2005.00969: https://arxiv.org/pdf/2005.00969
- ToTTo 制御付き table-to-text arXiv:2004.14373: https://arxiv.org/pdf/2004.14373
- 🔶 PARENT(Dhingra 2019)/PARENT-T・NLIベース(Dušek & Kasner 2020)= 上記サーベイ経由の二次参照(原論文URLは要確認)

**本プロジェクト内の関連既存doc**
- `docs/plans/data-strategy.md`(生=正準・パイプライン stage0-4)
- `docs/research/commercial-analytics.md`(①②③の商業KPI式)
- `docs/research/community-detection.md`(⑤ louvain/Palla ライフサイクル)
- `docs/research/vision-los.md`(③ LOS 概念)
- `docs/research/llm-human-fidelity.md` §3(⑧ hallucination/grounding の上位文献)
- `docs/research/data-pipeline-lit.md`(全体: event sourcing/tidy/後処理派生)
