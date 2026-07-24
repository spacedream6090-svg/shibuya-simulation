# 長期日常ラン(30日級)の実行見積もり — 第57バッチ タスクC

> 生成: `scripts/bench_longrun.py`(mock・seed=42・profile=conf/longrun30.yaml)。2026-07-24。
> 方針正典: docs/closed-world-daily-observation.md §3 タスクC。実 LLM 非使用=**mock エンジン単価**の見積り(実 LLM 時は per-step が LLM レイテンシ律速へ変わる=下記 §5)。

## 1. 実測(mock・人数 40人)

| ラン | 日数 | step | 実時間 | L1行数(events) | L1 parquet | 全parquet | ピークRAM(working set) |
|---|---|---|---|---|---|---|---|
| probe | 1 | 144 | 29.4s | 8,180 | 631.9KB | 685.0KB | 177.9MB |
| probe | 2 | 288 | 54.0s | 19,674 | 1.3MB | 1.4MB | 252.5MB |
| **検証** | 7 | 1008 | 1.7min | 63,918 | 4.5MB | 4.7MB | 584.0MB |

## 2. 外挿式(probe 1日/2日 からの線形モデル y = a + b·step)

| 量 | a(切片) | b(step単価) |
|---|---|---|
| 実時間[s] | 4.76 | 0.171 |
| L1行数 | -3314 | 79.82 |
| L1 parquet[B] | -8.034e+04 | 5052 |
| 全parquet[B] | -6.29e+04 | 5308 |
| ピークRAM[B] | 1.084e+08 | 5.429e+05 |

## 3. 外挿の精度検証(7日 予測 vs 実測)

| 量 | 線形外挿の予測 | 実測 | 誤差 |
|---|---|---|---|
| 実時間[s] | 3.0min | 1.7min | +76.2% |
| L1行数 | 77,144 | 63,918 | +20.7% |
| L1 parquet[B] | 4.8MB | 4.5MB | +6.6% |
| 全parquet[B] | 5.0MB | 4.7MB | +6.3% |
| ピークRAM[B] | 625.3MB | 584.0MB | +7.1% |

> 線形外挿は probe(短ラン)の固定コスト(init/1日目コールドスタート)を含むため、長い日数ほど誤差が縮む。以下の 30日外挿は**検証ラン(最長=最安定)の per-agent-step 単価**を用いる。

## 4. 30日ランの見積り(人数 100人・4320step)

- 単価(検証ラン由来): 2.4936 ms/agent-step ・ 228.3 events/agent-day ・ 73.6 B/event(L1)

| 量 | 30日×100人 の外挿 |
|---|---|
| 実時間(mock) | **18.0min** |
| L1行数(events) | 684,836 |
| L1 parquet | **48.0MB** |
| 全parquet(L1+L2+L3+L1b) | 50.8MB |
| ピークRAM(全量保持=checkpoint OFF の下限) | 6.1GB |
| ピークRAM(checkpoint_every=1440=10日ごと flush) | 2.0GB |

## 5. 本選 GPU 予算への含意

- 上表は **mock エンジン単価**。本選=実 LLM ではエンジン計算は LLM 呼(発火/計画/内省)のレイテンシに隠れるため、per-step 実時間は **req/s と在場数** で決まる(Day-0 ベンチ=finals-hardware-plan §2)。本ベンチは「エンジン+ロギング+観測レンズが 30日で破綻しないか(RAM/ストレージ/事後分析)」の確認に用いる。
- **ストレージ**: L1 parquet の 30日サイズが上表。lens ON(value/motive/trust/deviation/structure のL2 スカラー)は L2 に数列足すだけ=支配項は L1。全 parquet 見積りが本選ディスク予算(D8)の一材料。
- **RAM**: checkpoint_every=1440(10日)で L1 バッファは ~10日分に上限化(上表の 2 行目)。RAM が厳しければ flush_every_steps=288(2日)で更に圧縮できる(既定 0=従来と完全同一)。
- **分割実行**: 30日は 10日×3 に割って回せる(conf/longrun30.yaml のコマンド列)。resume はバイト一致(tests/test_resume + test_longrun)。夜間予算に合わせて区切っても straight と同一出力。
- **k\* 測定との棲み分け**: 本 30日ランは構造創発の観察 1 条件(人数を絞る)。k\* は 7–14日・人数多めで別に回す(二段構え)。D15(finals-day1-decisions)で本選確保を判断する。

## 6. ビューアの実測サイズ(30日×数百人で開けるか)

7日×40人ラン(上の検証ラン)で 3 種の出力サイズを実測:

| 生成 | コマンド | サイズ |
|---|---|---|
| フルビューア(地図+位置アニメ) | `make_viewer.py … --no-traffic` | viewer.html **5.79MB** / dashboard.html 5.82MB |
| **日次ロールアップ**(第57バッチ) | `make_viewer.py … --daily-rollup` | rollup.html **17.9KB** |

- viewer.html の支配項は `positions`(n_steps×n_agents×3)。30日×100人は positions 要素数が **約10.7倍**
  (=4320×100 / 1008×40)になり、viewer.html は **~50–60MB 級**に膨らむ(`--no-traffic` 込みでこの値。背景交通を
  入れると更に数倍=ブラウザで開けない領域)。→ 長期ランの全量アニメ閲覧は現実的でない。
- **`--daily-rollup` は日数に対してほぼ一定**(30日でも日行が 8→~30 に増えるだけ=**20–30KB 級**)・人数に非依存
  (positions を一切埋め込まない=L2 日次集計 + structure.json のみ)。**30日×数百人でも即開ける**ことを実測で確認。
  画面に「日次ロールアップ表示・位置アニメ/個票は含まない」を明示(silent 禁止)。既存 viewer/dashboard の生成経路には
  一切入らない別ファイル(rollup.html)なので、`--daily-rollup` 未指定時の出力は従来とバイト同一。
- 全量を見たいピンポイント時間帯は、run を短い step 窓で切って(`--start-tod` 併用)フルビューアを出す運用でも可。

## 7. タスクB 構造指標の 7日検証(0埋まり/NaN でないこと)

`scripts/analyze_structure.py` を上の検証ラン(7日=8暦日バケツ・40人・relations/hierarchy ON)に掛けた実測:

- **edge churn(組み替え)**: `edges_formed=[34,98,54,46,18,22,24,0]` / `edges_broken=[4,6,2,6,0,2,0,0]` /
  `edges_decayed=[0,12,84,60,46,38,20,28]` / `active_ties=[0,30,114,94,88,66,60,66]`。
  → 紐帯が**形成も風化も**しており、複数日で意味のある時系列(全て実数・0埋まりでない)。
- **順位固着(Kendall τ・順位ソース=status/L3)**: `tau_prev_day=[—,0.539,0.742,0.724,0.722,0.884,0.861,—]`。
  → 前日比 τ が **0.54→0.88 へ上昇**=ヒエラルキーが日を追って安定化(固着の兆し)。ただし固着閾値 0.90 は
  7日内で未超過=**固着の確定には 30日級が要る**という D15 の判断材料そのもの。
- **中心性 turnover**: `[—,0.7,0.7,0.7,0.6,0.7,0.8,0.3]`=会話ハブは日々入れ替わる(固着していない)。
- **コミュニティ変化**: `n_communities=[6,3,5,3,6,2,6,2]` / `change_rate=[—,0.86,0.82,0.81,0.89,0.85,0.83,0.67]`
  =決定論 LPA の所属が日次で大きく動く。
- **固着検知**: 7日では固着区間 **0**(中心性が N 日以上入れ替わらない期間なし=構造は動いている)。
- **NaN 検査**: churn_rate / tau / turnover いずれも NaN なし・None は初日/末端の未定義のみ(仕様どおり)。

→ **タスクB の各指標は複数日で意味を持つ**(0埋まり・NaN でない)ことを確認。順位 τ の上昇トレンドは、
固着の成立可否を見るには 7日では足りず 30日級の観察窓が要る、という**長期ランの必要性を裏づける**サイン。

## 8. 屋内ミクロ観察 ON 時の長期コスト(第58バッチ B9 2026-07-24)

> §1–7 は屋内 OFF(建物粒度)の見積り。本節は **屋内ミクロ観察 ON**(`indoor.enabled=true`+markov/sfm/
> meeting/tracks・会社観測 `work.service.ledger/by_org/indoor_fields`)を足したときの追加コストを実測+外挿する。
> 観測のみ(介入でなく観察=LLM 呼数不変・k 非依存=`tests/test_indoor_invariance.py`)。既存 §1–7 の記述は不変。

### 8.1 SFM 性能較正(24step・100体・屋内全ON・mock)

屋内 ON のコストは遷移駆動 SFM 積分が支配する(24step100体: OFF **1.96–2.78s** → ON **32.0s** ×約12–16)。
conf レバーを系統的に振った実測(seed=42・tracks ON。①実行時間 ②遭遇検出数 ③space_move 数=SFM 非依存の sanity):

| 設定 | 実行時間 | space_move | 遭遇(contacts) | 軌跡サンプル | 判定 |
|---|---|---|---|---|---|
| OFF(indoor off) | 2.78s | 0 | 0 | 0 | 参照 |
| baseline(dt0.2/msub900/samp5) | 32.00s | 293 | 5 | 28,810 | 基準 |
| **max_substeps=300** | **24.45s(−24%)** | 293 | 5(不変) | 12,599(**−56%**) | ◎ 時間+ストレージ削減・品質不変 |
| sample_interval=10 | 32.08s | 293 | 5(不変) | 14,363(−50%) | ◯ ストレージのみ削減(時間コストゼロ) |
| dt=0.3 | 31.87s | 293 | **115(+2200%)** | 27,873 | ✗ waypoint 超過で遭遇が偽増=品質劣化 |
| dt=0.4 | 31.62s | 293 | 14(+180%) | 26,870 | ✗ 同上(時間短縮は僅少) |
| bystander_cap 8/12・neighbor_cap 8 | ~31–32s | 293 | 5(不変) | 28,810 | − 自然密度では効果なし(同居が疎)=高密度セルの安全弁 |

- **壁非貫通**: 実レイアウト(vision 手続き生成・8 movers+6 bystanders)で dt∈{0.2,0.3,0.4,0.5}×max_substeps∈{300,900}
  の全組で **wall_crossings=0**(`indoor_flow.segment_hits_wall` 判定=`test_indoor_flow` と同一)。どの候補値も壁貫通を破らない。
- **推奨**: `sfm.max_substeps=300` + `sfm.sample_interval=10`(dt/各 cap は既定のまま)。実行時間 **−24%**・軌跡サイドカー
  **−78%**(msub −56% × samp −50%)・遭遇検出数と壁非貫通は不変。max_substeps=300=60s は直交フロア横断(~40m/1.2m/s≈33s)に十分。
  **dt は上げない**(0.3+ は積分不安定で遭遇が偽増=観測品質を壊す。時間短縮も僅少)。
- **既定は変更しない**(提案止まり=親が判断)。理由: `indoor.enabled=false` が既定=ゴールデンは不変だが、`sfm.*` 既定を
  変えると屋内 ON ランの軌跡/遭遇サイドカーのバイト内容が変わり、屋内 ON テスト群の期待値の再ベースラインが要る。推奨値は
  `conf/observe.yaml`・`conf/longrun30.yaml`・D16 のコメントに記載し、本選 param 選択は親に委ねる。

### 8.2 7日実測(1008step・40体・屋内全ON+org ON・推奨param・mock)

`indoor` 全 ON(msub300/samp10)+ `organizations`+`work.service`(ledger/by_org/indoor_fields, personas_80)・
`checkpoint_every=576`(4日ごと flush)で 1008step を実測:

| 量 | 実測(40体・1008step) |
|---|---|
| 実行時間(mock) | 307.3s(5.1min)= **304.8 ms/step** |
| L1 parquet | 2.90MB(うち space_move **1,211 行**) |
| indoor_tracks_samples | **483.5KB** |
| indoor_tracks_contacts | 2.1KB(遭遇は疎) |
| org_ledger | 2.73KB(**99 行**=会社×日) |
| ピーク RAM(working set・4日flush) | **339MB** |

**resume==straight のバイト一致(屋内状態込み)**: 3日(432step)・40体・同 conf を straight と split(216+216 resume)で回し、
`l1_events`(1,314,606B)/`indoor_tracks_samples`(234,700B)/`indoor_tracks_contacts`(2,132B)/`org_ledger`(2,535B)
の **4 系列すべてバイト一致**(既存 `test_resume_matches_straight` の 24step を 7日級で実地確認)。分割夜間実行でも屋内サイドカーが崩れない。

### 8.3 30日100体への外挿

per-agent-step 単価(§4 と同流儀=最長=最安定ランの単価)+ 密度超線形(40→100体で per-agent-step ×1.23=
24step 実測 (32.0/100)/(10.45/40) 由来。SFM のセル内対人斥力が O(n²))で 30日100体(4320step)へ外挿:

| 量 | 30日×100体 の外挿(屋内 ON 追加分) | 備考 |
|---|---|---|
| indoor エンジン時間(mock・OFF比の**増分**) | **+65min**(24step実測 OFF2.78s→ON24.45s=+0.90s/step) | 既定param(msub900)なら **+88min**(=B3 の「+85分」と一致)。**実LLMでは§5 のとおり LLM レイテンシに隠れ req/s 律速は不変** |
| indoor_tracks_samples | **≈5.1MB** | 483.5KB×(100/40)×(4320/1008)。既定 sample_interval=5 なら ≈10MB |
| indoor_tracks_contacts | ≈40KB | 遭遇は疎=無視可 |
| org_ledger | ≈25KB | 会社×日=無視可 |
| L1 space_move 追加行 | ≈13,000 行 | L1 へ加算(支配項でない) |
| ピーク RAM 上乗せ | 数百MB(checkpoint で有界) | §5 の longrun 本体 2.0GB(checkpoint_every=1440)に屋内バッファ分を上乗せ |

- **含意**: 屋内 ON の追加コストは **①SFM エンジン時間**(推奨 param で 30日100体 +65min mock)と **②indoor_tracks_samples ストレージ**
  (推奨 param で ≈5MB/30日)の 2 つが支配項。org_ledger・contacts・space_move の L1 加算はいずれも小。RAM は checkpoint flush で有界。
- **本選 GPU 予算への含意**(§5 と同じ論理): 上表は mock エンジン単価。本選=実 LLM ではエンジン計算(SFM 含む)は LLM 呼の
  レイテンシに隠れ、per-step 実時間は req/s と在場数で決まる=**屋内 ON でも本選の壁時計は延びない**(SFM が LLM レイテンシ窓に収まる限り)。
  屋内 ON は「余剰枠で観測解像度(遭遇ネットワーク/在館/会社在席)を上げる」追加オプション(判断=D16)。
