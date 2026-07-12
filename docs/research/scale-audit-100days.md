# スケール監査: 1万〜数万エージェント×100日(現実時間)(R4、2026-07-06)

> 本番想定: **1万〜3万エージェント × 100日**。1 step = 10分 → 144 step/日 → **100日 = 14,400 step(総数)**。
> 現行コードを読んで具体的なボトルネックを**数値で**監査する。**修正の実装はしない**(次バッチが使う設計書)。
> スループット・件数の仮定は明示し、桁の不確かさは正直に記す。

## 0. 前提と概算パラメータ
| 記号 | 意味 | 低位(基準) | 高位 |
|---|---|---:|---:|
| n | エージェント数 | 10,000 | 30,000 |
| T | 総 step 数(100日) | 14,400 | 14,400 |
| a | 平均アクティブ率(範囲外・睡眠除く) | ~0.5(昼は 0.6-0.8、夜は <0.2) | 同 |
| ev | イベント発生率 | mock 実測 80人×144step≈15k → **~1.3 events/agent/step**(全員アクティブ時) | 同 |
| L | lod.max_llm_per_step | 300 | 300 |

⚠️ ev はモック値からの外挿。実 LLM では発話量が変わり得る。以下の桁は**オーダー推定**。

---

## 1. 計算量(CPU ホットパス)
`engine/scheduler.run_step` は毎 step 全 agent を数フェーズで走査。ボトルネックは**全対全の知覚判定**。

### 1.1 hearers_of = O(n²)/step の主犯 ★最優先
`world/perception.hearers_of(speaker, agents, radius)` は毎回**全 agent を線形走査**(context 一致+hypot 距離)= O(n)。
呼び出し箇所(scheduler):
- `_decide`(l.624): **アクティブ agent 1人ごとに 1回** → a·n 回 × O(n) = **O(a·n²)/step**(支配項)
- `_phase_drive`(l.536, 申請者ごと `face=bool(hearers_of(...))`)= O(requesters·n)
- `_llm_speak`(l.436)・`_apply` の speak/coin_label(l.978, 957)= 発火・発話ごと

**数値(n=10,000, a=0.5)**: `_decide` だけで 5,000 × 10,000 = **5×10⁷ 距離判定/step**(昼はもっと)。
Python の hypot ループを ~10⁷/s と見て **~5秒/step の純 CPU**。全 step を活動加重で ~10¹² 演算 →
**約 1〜2 日ぶんの CPU が LLM とは別に直列で発生**。n=30,000 では 9倍 → **~10日以上**。GPU では解けない純 CPU 律速。
→ **空間ハッシュ(グリッド/エッジ・建物階のバケット)化で O(近傍数) に落とす**。context(street/建物階/outside)は既に
バケット鍵に使える。半径 40m の近傍だけ見れば O(n·k)(k=平均近傍数)= 実質 O(n)/step。**桁が変わる最重要修正。**

### 1.2 L2 集計 collect() を毎 step 全走査
`observer/aggregate.collect`(run_step l.1134 で**毎 step**)は ~35 aggregator を回す。多くが O(n):
- O(n) 系(mean_grievance/n_outside/n_working/opinion_var/belief_diversity/speech_diversity 等)× ~35 = **~35n/step**。
  n=10k → 3.5×10⁵/step × 14,400 = 5×10⁹。分〜時間オーダー(hearers_of に比べれば小)。
- ⚠️ **隠れた O(P): `n_likes`/`n_reshares`(l.143-153)は毎 step `net.posts` 全件を走査**して likes/reshares を数え直す。
  posts は無上限(§2.4)。中盤 P≈50万件なら 2×50万×14,400 = **1.4×10¹⁰**。posts 増加で悪化。
  → いいね/RT は**増分カウンタで O(1) 更新**に(発生時に += )。全走査を廃止。
- `speech_pairwise_var`(l.269)は先頭 50体に cap 済み(O(50²))= 良い前例。

### 1.3 その他(現状は許容だが要監視)
- `_phase_move`(l.205): 単一ループ O(n) + occupancy dict O(n) + 移動者ごと RDP。線形。OK。
- `_phase_traffic`(l.330): cars_per_day=30000。od モードは車を個体追跡。ログは max_log で cap。中程度。
- `timeline_for`(internet l.95): `rest = [p for p in fresh if p not in followed]` の `followed` が**list**
  → メンバシップ O(len(followed))。長期未読で fresh が肥大すると **O(fresh·followed)**。→ followed を set 化・fresh 窓を cap。

---

## 2. 記憶(RAM・永続構造)
### 2.1 L1 イベントバッファ = 最大の RAM リスク ★最優先
`observer/logger.ObserverLogger.events` は `flush_segment()` を呼ぶまで**全件 RAM 保持**。
`flush_segment` は **checkpoint_every>0 のときだけ**呼ばれる(simulation.run l.363-367)。既定 0 = **一度も flush せず全 run を RAM に積む**。
- 件数: ~0.65 events/agent/step(a=0.5)× 10,000 × 14,400 = **~9.4×10⁷ 件(10k)** / ~2.8×10⁸(30k)。
- RAM: Event dataclass(payload dict、move_segment は polyline)~0.5-1 KB/件 → **70〜140 GB(10k)**。**即破綻**。
- ディスク(parquet+zstd)~100-200 B/件 → **~15-30 GB(10k)** / ~45-90 GB(30k)。保存は可能。
→ **checkpoint と独立に定期 flush を必須化**(例: N step ごと or events が上限件数で自動 flush)。flush_segment 機構は既にあるので
  **トリガを checkpoint から分離**するだけ。加えて **L1 のサンプリング/シャーディング**(move_segment を間引く・種別別 parquet)を検討。

### 2.2 relations 台帳 = 唯一の無上限な per-agent 構造 ★高
`agents/memory.MemoryStore.relations: dict[int, dict]`(l.39)は `record_contact` で追記されるのみ、**上限なし**。
呼び出し: 対面 speak の**聞き手ごと**(scheduler l.1015-1016)+ DM(l.937-938)+ 初期関係。
- 100日で社交的 agent は distinct 接触が O(n) まで増え得る → 全体 **最悪 O(n²) = 10⁸ エントリ × ~150 B = ~15 GB**。
  実際は共在で疎だが、hub/keystone 個体は数千件を保持しうる。checkpoint にも丸ごと入る(§2.5)。
→ **relations に上限 + LRU/重要度(count×recency)退避**。cold な弱紐帯を落とし、上位 K を保持。

### 2.3 episodes 120 / 日記 7日 は 100日でも安全(上限で頭打ち)
- `episodes` は store_cap=120 で **importance×新しさ**で忘却(consolidate l.75-78)。`day_summaries` は `[-7:]`(l.63)。
- どちらも**ハード上限**なので 100日でオーバーフローしない。→ **溢れは問題なし。問題は「質の劣化」**(§5)。
- `beliefs`(agent)は無上限だが +1/内省(最大 100/agent)。10k×100 = 1M 短文字列 ~100 MB。低リスク。**cap 30 + 件数**を推奨(均質化対策も兼ねる)。
- `visits` Counter は地図ノード数(数千)で頭打ち。OK。`said` は [-4:]。`heard_counts` は語彙数で頭打ち。

### 2.4 net.posts / net.news = 無上限リスト ★中
`net/internet.Internet.posts`(l.23)は全投稿を保持、reshare は**新規 post を追記**(l.83)。trim なし。
- 100日で数百万件。各 post に `likes:set`(バイラルで O(n) まで膨張)。**数 GB〜、増加一方**。§1.2 の全走査コストとも複合。
→ **古い post を退避/エイジアウト**(timeline_for は read_marks 以降しか読まない=古い post は不要)。likes を件数のみ保持も検討。

### 2.5 checkpoint サイズ
`engine/checkpoint.save` は agents(relations!)+ net(posts!)+ tools + labels を pickle+gzip。
- 支配項 = relations と posts。§2.2/2.4 が無上限なので checkpoint は **run 後半で数百 MB〜GB に増大**。
→ relations LRU + post エイジアウトで有界化すれば checkpoint も有界。

### 2.6 L3 snapshot
`log_snapshot`(l.1135, snapshot_every=12)は 1,200 回、各回**全 agent の全状態を JSON 文字列化**。
10k agents × ~250 B = 2.5 MB/snapshot × 1,200 = **~3 GB RAM(未 flush 時)**。flush_segment に乗るが、
snapshot 間隔を粗く or agent サブサンプルを検討。

---

## 3. LLM(呼数・トークン・所要時間)
### 3.1 呼数 ★重要な非対称: planning/reflection は budget 非ゲート
| 経路 | budget 上限 | 呼数(10k/100日) | 呼数(30k/100日) | 備考 |
|---|---|---:|---:|---|
| deliberate+reply+face 発火 | **あり(L=300/step)** | ≤ 300×14,400 = **4.32M** | 4.32M(n によらず頭打ち) | scheduler の budget.take() |
| 朝の計画(planning) | **なし** | 1/agent/日 = **1.0M** | **3.0M** | `_phase_planning` は take() を通らない |
| 内省(reflection) | **なし** | 1/agent/日 = **1.0M**(pull で 2M) | **3.0M**(pull 6M) | run_step の maybe_reflect ループ |
| **合計** | — | **~6.3M** | **~10.3M** | — |

→ **発見: LOD 予算は deliberate だけを cap し、planning と reflection は cap しない**。よって n を増やすと
  **planning+reflection が総 LLM コストの成長を支配**(deliberate は 300/step で飽和・n 非依存)。
  意図的(k 非依存・日1回・時間分散)だが、**スケール時のコスト主因**として明記。必要なら planning/reflection にも
  step あたり上限 or キュー平準化の seam を検討。

### 3.2 トークン(オーダー推定・仮定明示)
仮定: deliberate ~400 prompt+320 out ≈ 720 / planning ~400+300 ≈ 700 / reflect ~600 prompt+1200 out、
**思考モード(reflect_think=true)で出力実効 ~2×** → reflect ≈ 3,000 tok。
- deliberate 4.32M×720 ≈ **3.1B** / planning 1.0M×700 ≈ **0.7B** / reflect 1.0M×3,000 ≈ **3.0B**。
- **総計 ≈ 6.8B tokens(10k)** / **~12-14B(30k)**。**内省が思考モード+1200出力で最大**。
- 出力のみ: deliberate 1.38B + planning 0.3B + reflect ~2.4B ≈ **~4.1B out tok(10k)**。
- キャッシュ(model.cache): 実 LLM では prompt に step/時刻/文脈が入り**ヒット率は低い** → 節約は限定的。

### 3.3 A5000×7(8B AWQ 4bit)での所要時間 ⚠️仮定に強く依存
仮定: vLLM バッチで **~2,000-3,000 出力 tok/s/GPU** 持続 → ×7 ≈ **14,000-21,000 out tok/s**。
- 出力 4.1B tok ÷ 17,500 tok/s ≈ 234,000 s ≈ **2.7日(decode のみ)**。prefill(3B+ prompt)を足して
  **現実 ~3-5日(10k)**、**~7-12日(30k)**。
- ⚠️ **スループット仮定を半分にすれば所要は倍**。本番前に `scripts/bench.py` で実測 tok/s を取り直すこと(既存メモ: A5000 で FP8 不可→4bit、N=90-480 decision/step の上限)。
- 補足: 100日を実時間で回すには **CPU 律速(§1.1)が GPU 律速(本節)と直列**なので、§1.1 未修正だと GPU が遊ぶ。

---

## 4. 観測(analyze / measure / export)の破綻点 ★高
### 4.1 measure の全量 RAM 展開
`observer/measure.load_events`(l.38)は `pq.read_table().to_pydict()` の後に **10⁸件の Python dict list を構築**。
- 1 KB/dict → **~100-200 GB RAM。ハード破綻**。全 measure 関数(`agent_features`/`item_cascades`/`network_windows`/
  `collective_series`/`drift_metrics`)は `events: list[dict]` を受ける = **パイプライン全体が全件 RAM 前提**。
→ **ストリーミング化**(row-group 単位・列射影・step 窓ごとに逐次集計)。多くは 1 パスで済む集計。

### 4.2 network_windows の O(窓×イベント)
`network_windows`(l.519)は `while start<=max_step:` の**各窓で ordered 全件を再走査**。
- 窓数 = 14,400/24 = 600 × 10⁸件 = **6×10¹⁰ 反復**。RAM を無視しても破綻。
→ イベントを**1 パスで窓バケットに振り分け**てから各窓を処理(O(E + 窓))。

### 4.3 export_3d の positions[step][agent] 全構築
`scripts/export_3d.reconstruct_tracks`(l.341)は密行列 `positions` を作る = **T×n = 14,400×10,000 = 1.44×10⁸ セル**、
各 `[x,y,w]`。RAM ~15-30 GB(positions)+ 同程度(moves)。加えて `export_run`(l.436)は `to_pylist()` で**L1 全件を先に materialize**。
- **~10⁸ セルで破綻**(依頼が指摘した 1.4億の破綻点)。
→ **ビューアの LOD 出力**: 空間/時間ダウンサンプル、ビューポート・タイル分割、per-step 疎デルタ(動いた agent だけ)、
  バイナリ(glb 風)ストリーム、描画 agent 数の上限。scene 契約は追加専用で互換維持(既存方針)。

### 4.4 その他
- `r2_traits`(l.769)は n_agents 行の numpy 配列 → 10k-30k 行は問題なし。OK。
- `communities`/`drift_metrics` の label propagation は O(iter×edges)。edges は会話量で有界だが、**入力の全件走査**が 4.1 と同根。

---

## 5. 記憶の質:「100日間持続するか」への回答
**結論: 持続はするが、7日を超える文脈は"圧縮された蒸留物"としてのみ残る(設計上、劣化は緩やかで recency 偏り)。**
- 保持経路は3つ: (a) **顕著エピソード ≤120**(importance×新しさで忘却=中重要度の古い出来事は新しい顕著記憶に押し出される)、
  (b) **日記 直近7日のみ**(l.63。**8日以上前は日記から消える**)、(c) **beliefs**(内省の結論の累積)+ **relations**(間柄の回数)。
- したがって 100日の長期文脈は **日記の圧縮に依存**し、**1週間より古い出来事は「120の顕著記憶に残ったもの/信念を動かしたもの/接触回数」以外は失われる**。
- 劣化の性質: **recency 偏りの忘却 + importance ゲートの保持**。100日で episodes は 120 で飽和・入れ替わり、
  agent は実質「これまでで最重要の ~120件 + 直近1週 + 誰と何回話したか + 現在の信念」を覚えている。人間的だが:
  (i) 中重要度の古記憶は消える、(ii) k 下で belief がドリフト蓄積(既存の**崩壊検知** belief_diversity が監視対象)、
  (iii) relations だけ忘却が無い(§2.2。LRU を入れると最古の弱紐帯が失われる)。
- 補強案: **R1 の閾値ドリフト(自発回復)**と **beliefs の cap** は 100日均質化(全員の内省・信念の収束)を緩和する副次利得。

---

## 6. ボトルネック一覧(現状の限界規模 → 必要な修正 → 重さ)
| # | 箇所 | 現状の限界 | 症状 | 必要な修正 | 重さ |
|---|---|---|---|---|---|
| B1 | `hearers_of`(perception) | ~数千 agent | O(a·n²)/step。10k で ~5s/step CPU、run 全体で日単位の純 CPU | **空間ハッシュ(グリッド/建物階バケット)**で O(n·k) 化 | 中 |
| B2 | L1 events バッファ(logger) | checkpoint OFF だと全 run RAM | 10k で 70-140 GB RAM で OOM | **flush を checkpoint から分離**(件数/step 閾値で自動 flush)+ move_segment 間引き | 小 |
| B3 | measure.load_events | ~10⁷ 件 | 10⁸件で 100-200 GB RAM。analyze 全滅 | **ストリーミング集計**(row-group/列射影/1パス) | 大 |
| B4 | export_3d positions | ~10⁷ セル | T×n=1.4億で 15-30 GB+、materialize で二重 | **ビューア LOD 出力**(時空間ダウンサンプル・疎デルタ・タイル) | 中 |
| B5 | network_windows | 全件×窓 | 6×10¹⁰ 反復 | **1パス窓バケット化** | 小 |
| B6 | relations 台帳(memory) | 無上限 | 最悪 O(n²)=~15 GB、checkpoint 肥大 | **上限+LRU(count×recency 退避)** | 小 |
| B7 | net.posts/news | 無上限 | 数百万件・数 GB、増加一方 | **古い post のエイジアウト/退避**、likes 件数化 | 小 |
| B8 | collect() の n_likes/n_reshares | posts 全走査/step | O(P·T)。中盤 1.4×10¹⁰ | **増分カウンタ化**(発生時 += ) | 小 |
| B9 | planning/reflection の LLM | budget 非ゲート | n 増で総 LLM コストを支配(6.3M→10.3M 呼) | 必要なら **step 上限/キュー平準化 seam** | 中 |
| B10 | L3 snapshot | 未 flush で ~3 GB | RAM 圧・書き出し重 | 間隔粗く/agent サブサンプル、B2 の flush に同乗 | 小 |
| B11 | timeline_for | list メンバシップ | 長期未読で O(fresh·followed) | followed を set 化・fresh 窓 cap | 小 |

## 7. 優先順位付き修正リスト(次バッチ設計の推奨順)
1. **B2 L1 定期 flush(checkpoint と分離)** — 重さ小・効果絶大。これが無いと 100日は物理的に回らない。まず必須。
2. **B1 空間ハッシュ化** — CPU 律速の桁を変える唯一の修正。GPU を遊ばせないためにも先行。
3. **B3 analyze のストリーミング化** — 回した後に**測れない**と研究にならない。measure/analyze の入力を row-group 逐次へ。
4. **B6 relations LRU + B7 posts エイジアウト + B8 増分カウンタ** — 無上限構造3点を有界化(RAM・checkpoint・毎step走査を同時に解消)。まとめて小改修。
5. **B4 export_3d の LOD 出力** — 可視化の破綻点。研究本体とは分離できるので優先度は中。
6. **B5/B10/B11** — 局所最適化。B3/B2 のついでに回収。
7. **B9 planning/reflection の平準化** — スケール時の GPU コスト管理。bench 実測(§3.3)後に要否判断。

## 8. 確定できなかった数値(正直な記録)
- **ev(events/agent/step)= ~1.3** はモック 80人×144step の外挿。実 LLM では発話・SNS 量が変わり桁が動きうる。
- **LLM スループット(tok/s/GPU)** は未実測の仮定値。§3.3 の「3-5日/10k」は仮定に線形依存 → `bench.py` 実測が必須。
- **relations/posts の実成長** は共在・SNS 挙動次第で、O(n²) は最悪上界。実効は疎で数 GB オーダーの見込みだが未計測。
- parquet 圧縮率(~100-200 B/件)は move_segment の polyline 比率に依存。実ラン 1 本で実測すべき。
- A5000 の 8B AWQ 実効バッチスループットは context 長で大きく変動(既存 infra メモの N=90-480 上限と併読)。

## 参照(コード位置)
scheduler.py(run_step l.1098, _phase_drive l.508, _decide l.621, _apply speak l.976)/ perception.py(hearers_of l.18)/
memory.py(relations l.39, consolidate l.60)/ logger.py(events l.40, flush_segment l.99)/ aggregate.py(n_likes l.143)/
internet.py(posts l.23, timeline_for l.95)/ measure.py(load_events l.38, network_windows l.519)/ export_3d.py(reconstruct_tracks l.341)/
simulation.py(run l.348, checkpoint 分岐 l.363)/ checkpoint.py(save l.52)。
既存インフラ知見: [../lit/infra__storage-routing.md](../lit/infra__storage-routing.md) / [../lit/infra__gemini-summary-verification.md](../lit/infra__gemini-summary-verification.md)(A5000/LOD 上限)。

---

## 9. 実施済み修正と残課題(バッチ E1、2026-07-06)
> 原則: **既定設定はバイト一致で不変**(test_scenario prechange golden・test_resume が担保)。
> 追加した上限系は config 既定=実質無効(0=無制限/現行同一)。純最適化(乱数不使用)・no-fingerprint。

### 実施済み(既定不変を確認: 全 193 テスト green = 従来 182 + 新規 tests/test_scale.py 11 本)
- **B1 hearers_of の空間ハッシュ化** — `world/perception.py` に `build_index()`/`PerceptIndex`(cell=perception_radius,
  key=(context, ⌊x/r⌋, ⌊y/r⌋))を追加。`scheduler.run_step` が `_phase_move`/`_phase_traffic` の**後**(位置確定後)に
  `sim.percept_index` を1回だけ張り、`_phase_drive`/`_decide`/`_llm_speak` の hearers_of に渡す(近傍9セル+距離判定)。
  返り値は全対全走査と**内容・順序まで完全一致**(cell=r なので半径内は必ず±1セル、距離判定は残置)。
  API は `hearers_of(agent, agents_or_index, radius)` の後方互換(索引 or agent 列のどちらでも同値)。
  **計測(1,000体, radius=40, active=805)**: 旧 59.5 ms/step → 新 1.1 ms/step = **51.8x**(hearer 総数 9640 で一致確認)。
  - ⚠️ **逸脱(意図的)**: `_apply` の speak/coin_label は**索引を渡さず live 走査のまま**残した。`_apply` は
    enter/exit_building で**同 step 内に位置・context が変わる**ため step 索引は古くなる(byte 不一致の原因)。
    _apply の hearers_of は O(fires·n)(≤ budget·n)で**支配項 O(a·n²) ではない**ので、正しさ優先で live に。
    索引は位置が安定な _phase_drive/_decide にのみ適用=そこが O(a·n²) の主犯だったので効果は担保。
    索引が無い経路(内部関数を直接呼ぶテスト等)は `getattr(sim,"percept_index",None)` で agent 列へ後退=従来同一。
- **B2 ログ flush の checkpoint からの分離** — `observer.flush_every_steps`(既定0=無効)を追加。>0 で N step ごとに
  checkpoint とは独立に `flush_segment()` を呼び L1 バッファ RAM を解放。同一 step の二重 flush を回避。part は
  finalize で結合(既存 `_next_seg`/resume 整合を再利用)。flush_every=12 の L1/L2/L3 が一気ランと一致することを test 済み。
- **B6 relations の有界化** — `memory.relations_max`(既定0=無制限)。>0 で `record_contact` 時に **LRU(last_step 最古・
  同点は相手id小)を退避**(いま触れた相手は除外)。決定論。`simulation` が各 agent.mem へ配線。
- **B7 net.posts の有界化** — `net.posts_max`(既定0=無制限)。>0 で古い post を先頭から破棄し `_post_offset` を進める。
  **post id は追記通し番号で不変**にし、`react`/`timeline_for`/`read_marks`/`rt_of` を **id ベース**へ(offset で位置補正)。
  既定 offset=0 で従来と完全同一。退避境界より古い read_marks でも timeline は安全(index ずれで別 post を叩かない)。
- **B8 n_likes/n_reshares の増分カウンタ化** — `Internet` に `n_likes_total`/`n_reshares_total` を持たせ、`react` で += 。
  aggregate は毎step全 posts 走査を廃止しカウンタ参照へ。like は set 意味を保つ増分(二重いいねは非計上)。trim なしでは
  従来の全走査和と完全一致(checkpoint は net 全体を pickle するのでカウンタも resume 整合)。
- **B4-lite 観測出口** — `scripts/export_3d.py` に `--sample-agents N`/`--step-stride K`(既定=全量・現行同一)。
  `measure.load_events` を **列射影+RecordBatch 逐次**へ(返り値・行順は不変、peak メモリ低減)。`network_windows` は
  speak/dm を先に1回抽出して窓ごとに使い回す同値最適化(全件×窓 → 会話件×窓)。

### 残課題(未実施=正直な記録)
- **B3 analyze/measure の完全ストリーミング化** — 未実施。`load_events` の逐次読みと `network_windows` の1パス化は入れたが、
  `agent_features`/`item_cascades`/`collective_series`/`drift_metrics` は依然 `events: list[dict]` を**全件 RAM 前提**で受ける。
  10⁸件では破綻する(§4.1)。**API を崩さずに** row-group 逐次・step 窓ごとの逐次集計へ組み替える設計が必要(次バッチ)。
  export_3d の `reconstruct_tracks` も内部は密行列のまま(サンプリングで幅は縮むが、フル出力は T×n を持つ)。
- **B9 planning/reflection の LLM 予算ゲート** — 未実施(設計判断が要る)。planning/reflection は budget 非ゲートで、n を
  増やすと総 LLM コストを支配(§3.1)。step 上限/キュー平準化の seam を入れられるが、**reflection のゲートは R1(k 非依存で
  日1回・全員内省)に直接触れる** — 発火数を絞ると k 条件間の内省回数が揃わなくなる恐れがあり、実験設計上の合意が要る。
  planning は R1 に比較的中立(行き先の土台)なので先に平準化しやすいが、いずれも bench 実測(§3.3)後に要否判断。
- **B5/B10/B11 の残り** — network_windows は入れたが、L3 snapshot 間隔の粗化(§2.6)と timeline_for の followed set 化(§1.3/B11)
  は未実施(局所最適化。既定挙動を変えるため config seam 化してから)。
