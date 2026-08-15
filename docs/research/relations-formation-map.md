# 調査: 関係形成の全経路マップ — 関係値は誰が動かしているのか

> 2026-08-15。ステータス: **調査のみ(src/tests/conf 不触)**。ユーザーの概念質問への回答。
> 問い(原文):
> 「エージェント同士の関係性は初期関係値の設定でもシミュレーション内でも LLM の出力などによって
> 作成されるものになっているか? この案ではエージェントの LLM 推論時以外の時の関係性の構築が
> なくなるのか? それとも関係値が作られるような関係はほとんどの場合 LLM が発火することと
> 結びついているから考える必要はないのか? 初期からシミュレーションの中で関係値が変わらない人は
> 認識が変わるイベントもなさそうだし、発火させる必要はない気がする」
>
> ★行番号は **2026-08-15 時点**の読み。並行して別バッチが `engine/scheduler.py` /
> `engine/simulation.py` / `cognition/lod.py` / `conf/finals_observe.yaml` を改修中
> (調査中に git status が 3 回変化した)なので、行番号は数十行ずれ得る。
> **関数名・シンボル名の方を正**として読むこと。
>
> ★★**姉妹文書**: [initial-relations-improvement.md](initial-relations-improvement.md)(同日・別バッチ)が
> **初期関係の作り方をどう良くするか**を扱っている。本書は**現行実装で関係値が実際にどう動くか**の
> 全数マップで、両者は補完関係にある。**独立に同じ非対称を見つけている**:
> 向こうの **R2「初期 closeness の減衰整合」**(注入値 = 閾値+0.5 なので接触が無ければ親友が翌日 tier2 へ落ちる)は、
> 本書 §2.2 の「1接触 +1.0 vs 日次 −1.0」および §5.4 の非対称と**同じ現象の別断面**である。

---

## 0. 結論(先に答える)

**問い①「関係性は初期関係値でもシム内でも LLM 出力によって作られるのか」**
→ **両方が併存していて、しかも役割が分かれている**。

- **関係の「成立」(誰と誰が関係を持つか)は、ほぼ全て LLM 非依存**。
  t=0 の `friend_graph`(homophily + 所属 + Dunbar 層)が居住者に約 30 辺/人を**乱数ゼロで直接注入**し、
  顔なじみ(同一建物)・`party`(来街者の連れ)がそれに乗る。**新しい関係の生成は会話経路だけ**で、
  その会話経路の 1 つ(C2 構造化会話)は**LLM を 1 本も呼ばない**。
- **関係値の「増減」(closeness の流れ)は、件数では LLM 発話(C1)が多数派**である。
  ★**実測(250体×2日・finals 構成・§4.3): LLM 関与 67.0% / LLM 非依存 33.0%**。
  ただしこれは「**LLM 呼 1 本が聞き手全員 × 両方向に増幅される**」ためで、
  **LLM 呼の本数とはずれる**(実測 1.63〜22.5 件/呼で、規模により 1 桁動く)。
- **関係の「質」**(magnitude・承諾/拒否・誘い先の選抜)は「**LLM が生んだテキストを
  決定論の読み取り器が事後に測る**」二段構え。**LLM 呼は 1 本も増えない**(§3)。

**問い②「この案(`cognition.fire`)で LLM 推論時以外の関係構築がなくなるのか」**
→ **ならない**。fire が差し替えるのは `_phase_drive` の `requesters` 集合だけで、
C2 構造化会話・日次減衰・休眠/再会・friend_graph・party・顔なじみ・joint 同席は
**どれも fire を経由しない**(fire の ON/OFF で 1 行も変わらない)。§5.1。

**問い③「関係値が作られる関係はほとんど LLM 発火と結びついているから考えなくてよいか」**
→ **半分だけ正しい**。増分の件数では C1 が多数派(67.0%)なので「結びついている」のは事実だが、
**C2・decay・初期注入は完全に独立に回る**(33.0%)ので「考えなくてよい」わけではない。
とくに **decay(−1.0/日)は fire と無関係に効き続ける**ので、
発火を絞ることは関係台帳を**非対称に痩せさせる**(§5.4)。

**問い④「関係値が変わらない人は発火不要ではないか」**
→ **設計としては正しく、しかも既にそう実装されている**(fire の S は共在チャンネル
`ext.encounter`/`ext.heard` で立つので、関係が動く人ほど S が上がる)。
ただし **finals 構成では「関係値が変わらない人」自体がほぼ居ない**
(C2 が拾い、decay が毎日削る)ので、前件はほぼ空である。§5.3。

★★**この 4 つを 1 行にすると**: `_contact` は**話者と聞き手の両方向**に呼ばれるので、
**「聞いていただけの人」の関係値も動く**。発火するのは話す側だけなので、
**「発火を必要とする更新」は実測 67.0% のさらに半分 ≒ 33.5%** に落ちる。
**closeness 更新の約 2/3 は、発火しない個体にも起きている**。§5.1b。

---

## 1. 「関係値」の実体

`agent.mem.relations` は `{other_id: rel}` の辞書で、`rel` の欄は次のとおり
(`src/society/agents/memory.py:134` `MemoryStore.record_contact` が唯一の生成点)。

| 欄 | 生える条件 | 意味 |
|---|---|---|
| `name` / `count` / `last_step` / `last` | **常に**(record_contact を通れば必ず) | 相手名 / 交流回数 / 最終接触 step / 直近の文(40字) |
| `closeness` | `closeness_delta` を渡した呼び出しだけ | 親密度の連続値。**relations OFF ではこの欄が一度も生えない** |
| `tier` | closeness から `relations.tier_of` で導出して代入 | 0=見知らぬ / 1=知人 / 2=友人 / 3=親友 |
| `dormant` / `dormant_closeness` / `dormant_step` | dunbar ON のときだけ | 認知枠超過で休眠した関係の退避欄 |

**重要な非対称**: `count` は全経路が触るが、`closeness` は「渡した経路だけ」が触る。
`relations.enabled=false` なら closeness/tier は**存在しない**(= §2 の C 列が全部消える)。
finals は `relations.enabled: true`(現行作業木 `conf/finals_observe.yaml:786-787`)。

`tier` を跨いだ瞬間だけが L1 に出る(`relation_tier` / `relation_break` /
`relation_dormant` / `relation_rekindle`)。**段の内側の連続的な増減は L1 に無音**で、
軌跡は第114 の GT ロガー `observer.relations_daily`(G5)サイドカーにしか残らない
(`src/society/observer/relations.py`)。

---

## 2. 更新経路の全数マップ

`closeness`/`tier`/`count` を書く**全ての箇所**をコード全走査で列挙した(`grep` で
`record_contact` / `rel["closeness"]` / `rel["tier"]` を掃いた結果。書き手はこれで全部)。

### 2.1 一覧表

凡例: **LLM** = その経路の発生に LLM 呼が必要か。**finals** = `conf/finals_observe.yaml` での ON/OFF。

| # | 経路 | 実装 | 何を動かすか | LLM | 乱数 | finals |
|---|---|---|---|---|---|---|
| **A. 初期条件(t=0 / 入場時)** ||||||
| A1 | 顔なじみ(起動時) | `engine/simulation.py:1288-1291` | `count` のみ(同一 home/work 建物で最大3人ずつ相互) | **不要** | ゼロ | 常時 |
| A2 | 顔なじみ(途中入場) | `engine/simulation.py:1965` `_link_colocated`(記録は `:1996-1997`) | 同上。プール回転で入る個体に同じ処理。実測 584 件 | **不要** | ゼロ | ON(pool ON) |
| A3 | **friend_graph** | `friends.py:154` `build_friend_graph` → `_inject`(`:142`) | `closeness` / `tier` を**直接代入**。homophily(年齢>職業)+ 同 org_id + 同建物 + 安定ハッシュノイズ → Dunbar 層(親友3-5 / 友人7-12 / 知人+20) | **不要** | **ゼロ**(全 hashlib・run.seed 非依存) | **ON** |
| A4 | icebreak | `engine/simulation.py:1696` | `count` のみ(`agents.icebreak_file` の初対面会話ログを読む) | 不要(事前生成) | ゼロ | **OFF**(基底 `icebreak_file: null`・finals 未設定) |
| A5 | **party(来街者の連れ)** | `party.py:117` `form_parties` → `_inject`(`:83`) | `closeness=5.0` / `tier=2` を直接代入。L4 record の `party_size` で日境界にグループ化 | **不要** | ゼロ(注入部分。回遊先だけ `party` stream) | **ON** |
| A6 | spark(火種介入) | `spark.py:170` `_apply_relations` | friends 流儀の注入 | 不要 | ゼロ | **OFF**(実験ノブ) |
| **B. シム内・LLM 非依存** ||||||
| B1 | **C2 構造化会話** | `conversation.py:224` `_apply_effects` → `_contact`(`:178`) → `relations.note_contact` | `closeness ±`(stance=oppose なら −0.5 相当、他は +0.4)+ tier 変化ログ。**両方向** | **不要**(実文を作らない) | `c2_meet` 1本(会話成立の抽選のみ) | **ON** |
| B2 | chance encounter | `chance.py:155` `_apply_encounter` | `closeness += 1.5`(双方・未知なら台帳新設) | 不要 | `chance` stream | **OFF**(第107 で運用退役) |
| B3 | **日次減衰(decay)** | `relations.py:175` `decay_day` | `closeness -= 1.0/日`(最終接触が前日以前)。tier 降格で `relation_break{cause=absence}` | **不要** | **ゼロ** | **ON** |
| B4 | **dunbar 休眠** | `dunbar.py:296` `_make_dormant`(日境界 `enforce`/`day_phase`・`population` 転出の `mark_dormant`) | `closeness→0` / `tier→0`(退避は残す) | **不要** | ゼロ | **ON** |
| B5 | **dunbar 再会** | `dunbar.py:340` `_rekindle` | 休眠前 closeness × `rekindle_discount` で復元 + tier 再導出 | **不要** | ゼロ | **ON** |
| B6 | joint 同席の維持 | `joint.py:508` → `dunbar.touch_group`(`:419`)→ `touch`(`:400`) | `last_step` を**進めるだけ**(closeness も count も増やさない)+ 休眠なら再会 | **不要** | ゼロ | **ON** |
| B7 | 評判 decay | `relations.py:152` `reputation_decay` | `agent._reputation`(関係値ではなく個体スコア) | 不要 | ゼロ | ON |
| **C. LLM 呼を伴う** ||||||
| C1 | **対面発話 speak** | `engine/scheduler.py` `_apply` の `kind=="speak"` 分岐 → `_contact`(`:138`) | 聞き手全員と**両方向** `closeness ±`。符号は `valence(text)`、増減**量**は `_quality_mag`(`:161`)= `relations_endo.contact_magnitude` | **必要**(`_llm_speak` が生成した本文) | `drive` stream(発火抽選) | **ON** |
| C2' | **DM** | 同 `kind=="dm"` 分岐 → `_contact` | 受信者が在場・非睡眠なら**両方向** `closeness ±` | **必要** | 同上 | **ON** |
| C3' | イベント告知 DM | `tools.py:747` `_announce_dm`(← `_host_event` ← `apply`) | `count` のみ(closeness を渡さない)。宛先 = 関係台帳の count 上位5人。実測 1,482 件 | **必要**(LLM の `plan_event` ツール実行が起点。**本文は定型**) | ゼロ | ON |

### 2.2 各経路の設計上の注意

- **関係の「新規作成」は会話経路(C1 / C2)だけ**。`record_contact` の `setdefault` が
  台帳エントリを作るので、**発話を聞いただけでも相手の欄が生える**(C1)。
  一方 `dunbar.touch` は台帳に無い相手には**何もしない**
  (`dunbar.py:405` の docstring が「正直な限界: 同席だけでは知り合わない」と明記)。
  したがって **C3 すれ違い(近くに居ただけ)は、それだけでは関係にならない**。
  「共在 → 関係」の口は **①誰かが発話して自分が hearers に入る(C1)** と
  **②`c2_meet` 抽選に当たる(C2)** の 2 つだけである。
  → これは U13(都市規模の完全接触ネットワーク)が測ろうとしている転換率そのもので、
  **分母(共在)と分子(関係)の間に「誰かが喋ったか」という第3の条件が挟まっている**ことを
  解析設計に必ず織り込むこと。
- **C2 は 1 step 1 会話・1 日最大 `daily_cap: 40`**(`conversation.py:38-47`)。
  対して LLM 発火は lod 上限で約 3 呼/人日だが、**1 発話が聞き手全員(実測 11.2 人)× 両方向に
  増幅される**ので、closeness 更新の件数では C1 が上回る(§4.2)。
  「呼数」で比べると C2 が主に見え、「更新件数」で比べると C1 が主に見える —— **どちらの見方を
  採るかを先に宣言してから数えること**。
- **decay は在場者だけを走らせるが、またいだ日数ぶんまとめて効く**
  (`relations.py:191-215` のレーン乙 F1/F2)。プール回転で街を出ていた個体が
  「不在中は関係が減らない」バイアスは塞がっている。
- **休眠は削除ではない**。`relations_max`(finals は `pool.relations_cap: 60`)の LRU 退避だけが
  台帳から**消す**。G5 サイドカーは差分方式なので「消えたこと」は行として出ない(不在でしか読めない)。
- ★**数値の釣り合いが「反復相互作用だけが関係になる」を機械的に保証している**
  (`conf/config.yaml:2127-2140` の較正済み既定):

  | 量 | 値 | 含意 |
  |---|---|---|
  | C1 1接触の増分 | `pos_weight: 1.0` × magnitude(実測 mean ≈ 1.16-1.26) | 1回聞いただけ ≈ +1.0〜1.3 |
  | C2 1会話の増分 | +0.4(同意/中立)/ −0.5 相当(反論) | C1 より小さい |
  | 日次減衰 | `decay_per_day: 1.0` | **1日会わないと +1.0 が丸ごと消える** |
  | 知人(tier 1)の閾値 | `tier_acquaintance: 2.0` | **同日に2回以上**接触しないと届かない |
  | 友人(tier 2) | 5.0 / 親友(tier 3) 12.0 | 反復が要る |

  → **「1回すれ違って発話を聞いただけの相手」は翌日の減衰でほぼ確実に 0 へ戻る**。
  関係として定着するのは**繰り返し会う相手だけ**である(Granovetter 的な反復相互作用の定義が
  パラメータで機械固定されている)。実測でも `edges_formed` が日中に数千立ち、
  日境界で `edges_decayed` と在場ローテーションによって大半が消える(§4)。
- ★**`hearers_of` に上限が無い**(`world/perception.py:82-103`。`perception_radius_m: 40.0` の
  9セル近傍を全数返す)。したがって **C1 由来の contact 件数は局所群衆密度に比例して増える**。
  25万体の本選ランでは、スクランブル交差点での 1 発話が数百人に届き得る = §4 の比は
  **規模依存**である(小規模ランの比をそのまま外挿してはいけない)。

### 2.3 関係値を**読むが書かない**下流(参考)

関係値が何に効いているか = 「関係が変わらない人」に何が起きないかの裏返し。

| 読み手 | 何に使うか |
|---|---|
| `household.form_partners`(`household.py:640-`) | 相互 closeness ≥ `partner_closeness` でパートナー成立(`partner_formed`) |
| `mobility._mutual_closeness`(`mobility.py:147`) | 同棲判定 |
| `engine/scheduler.py` `propose_partnership` 分岐 | 交際申込の可否(閾値未満は `partnership_declined`) |
| `joint._companions` / `relations_endo.weak_tie_candidates`(`:509`) | 共同行動の誘い候補(closeness 降順 + tier=1 の弱い紐帯枠) |
| `conversation._rel_strength`(`:96`) | C2 の話題・トーン・帰結の決定論写像 |
| `relations.social_lines`(`:224`) | プロンプトの「○○とは友人」「同じ仲間」1行 |
| `cognition/engaged.py:487` | `familiar_closeness`(定型応答で流すか ENGAGED に入るか) |
| `tools.py:459 / 741 / 1290` | 投票 / イベント招待先 / ベンチャーの network スコア |
| `gossip.py:209,227` | 悪評の伝播先(前日会話した相手を `last_step` から辿る) |
| `commerce.vc_score` | 関係次数を出資判断の素性に |

---

## 3. 関係の「質・内容」の LLM 依存度

「関係値が動く」ことと「関係の質・内容が LLM で決まる」ことは**別の軸**である。分けて整理する。

| 量 | 決め方 | LLM 依存度 |
|---|---|---|
| closeness の**符号** (C1/C2') | `valence(text)`(辞書法の純関数) | **間接**: 関数は非 LLM だが、入力テキストが LLM 出力 |
| closeness の**符号** (B1 C2) | `stance` = opinion 整合度の決定論しきい(`conversation.py:129-135`)→ oppose なら −0.5 / 他は +0.4 | **ゼロ** |
| closeness の**増減量** magnitude | `relations_endo.magnitude_of`(`:647`)= 発話長 / 往復数 / 明示キュー / hedge 中立化 | **間接**(既生成テキストからの決定論抽出。LLM 呼ゼロ)。**C2 経路には載せない**(実文が無いので材料が構造的に無い=`conversation.py:183-187` に明記) |
| `tier` | `relations.tier_of` = closeness の純関数 | **ゼロ** |
| 共同行動の**承諾/拒否** | `relations_endo.decide_accept`(`:280`)= 予定帳簿の当日予定 / 前日 `day_schedule` の `with` / 前日発話の明示キュー / 較正確率フォールバック | **間接**(「前日までに生成済みの構造化 LLM 出力」を読む。判定は全決定論・LLM 呼ゼロ・乱数ゼロ) |
| 誘う**相手の選抜** | `relations_endo` invite(`:483`,`:509`)= plan_with > dialog_cue > closeness 降順 > 弱い紐帯枠 | **間接**(同上) |
| 評判 `_reputation` | `gain_reputation`(mention=聞き手のいる発話 / own_adopted=語の採用)+ 日次 decay | **間接**(mention は LLM 発話に付随) |
| 悪評 gossip | `gossip_seed{cause}`(原イベント=`crime`/`relation_break`/`eviction` 等)→ complex contagion(独立2人から) | **ゼロ**(構造化イベント駆動) |
| 信念 beliefs | `belief_update` / `belief_transmit` / `belief_verify` | 会話チャネルに相乗り = C1 経由は LLM、C2 経由は非 LLM |

**まとめ**: 関係の**質**(magnitude・承諾判断・誘い先の選抜)は
「**LLM が生んだテキストを、決定論の読み取り器が事後に測る**」二段構えで、
**LLM 呼そのものは 1 本も増えない**。これは `docs/plans/endogenous-relations-plan.md` の設計原則
(片方向 hook = 値の生成のみ・発火判定には流さない)がそのまま効いている。

★**逆に、完全に LLM から切れているもの**は次の 3 つで、これが「発火しなくても関係が動く」の
実体である: **C2 の符号(opinion 整合度の決定論しきい)/ tier(closeness の純関数)/
日次減衰・休眠・再会(全て構造的過程)**。
★★**LLM が最も強く効くのは「符号」ではなく「誰と接触するか」**である。
発話が起きた場所と時刻が hearers 集合を決め、それが closeness の更新対象を決める。
つまり **LLM は関係の"内容"より"配線先"を決めている**。

---

## 4. 実測 — 関係値更新イベントのうち LLM 関与の割合

### 4.1 測り方(repo 不触)

`conf/finals_observe.yaml` をそのまま使い、`present_cap` と `n_agents` だけ小さくした mock ラン
(`model.backend=mock`)を 2 本回した。**`src/` `tests/` `conf/` は 1 バイトも変更していない**
(プローブは scratchpad の外部スクリプトで、必要な関数をプロセス内で wrap するだけ)。

| ラン | 規模 | 何を測ったか | 状態 |
|---|---|---|---|
| `relmap_f3` | 400体 × 150 step(≒1日強) | **L1 イベントからの経路別接触件数**(§4.2) | ✅ |
| `relmap_f4` | 250体 × 288 step(**2日=日境界を2本またぐ**) | **全 writer の実行時センサス**(`record_contact` / `decay_day` / `dunbar` / 初期注入) | ✅ (§4.3) |

★参考: **基底 `conf/config.yaml`(relations OFF・conversation OFF)** で同じ計測をすると
`record_contact` の呼び出し元は `scheduler.py:_contact` 36,114 / `tools.py:_announce_dm` 1,932 /
`simulation.py:__init__`(顔なじみ)374 の 3 箇所だけになり、
**closeness を持つ関係は 1 件も生まれない**(`closeness_delta` を渡す経路が 1 つも通らない)。
= relations ブロックを OFF にすると**関係の質の層がまるごと消える**ことの実測確認。

> ★調査中に**別レーンが並行して `observer/starvation.py`(DPH-O)を追加**しており、
> その新 kind 3 種が `observer/causality.py` の `CAUSE_OF_KIND` に未登録で
> **起動即 `KeyError`** になる状態だった。プローブ側で**そのプロセス内だけ**分類を補って走らせた
> (repo は触っていない)。**本選前に repo 側で 3 行足す必要がある** → **§6-6(本選ブロッカー)**。

### 4.2 L1 イベントから読める経路別の接触件数(400体・finals プロファイル・150 step ≒ 1日強)

`speak` は聞き手 1 人につき**両方向 2 件**、`conversation`(C2)は 1 会話につき**両方向 2 件**、
`dm` は受信者が在場・非睡眠のときだけ**両方向 2 件**。

| 経路 | L1 の件数 | closeness 更新件数(= 2 × 対) | LLM |
|---|---|---|---|
| **C1 対面発話** | `speak` 2,261 / `hear` 25,383(= Σhearers) | **50,766** | **必要** |
| **B1 C2 構造化会話** | `conversation` 4,356 | **8,712** | **不要** |
| **C2' DM** | `dm` 850 | ≤ **1,700**(在場・非睡眠の受信者のみ) | **必要** |

同ランの L1 に出た関係イベント: `relation_tier` 13,706 / `relation_break` 940 /
`reputation_update` 4,424 / `train_copresence` 1,031。

★**発話 1 件あたりの聞き手が 11.2 人**(25,383 / 2,261)ある。これが C1 の件数を押し上げている
主因で、`hearers_of` に上限が無い(§2.2)以上、**25万体の本選ではこの倍率がさらに上がる**。

### 4.3 ★全 writer の実行時センサス(250体 × 2日・finals プロファイル・mock)

**これが本節の主結果**である。closeness を書く writer を**全部**包んで数えた。

| 経路 | 呼び出しチェーン | 件数 | 比率 | **LLM 関与** |
|---|---|---|---|---|
| **C1 発話 + C2' DM** | `relations.note_contact ← scheduler._contact ← scheduler._apply_action` | **19,952** | **67.0%** | **あり** |
| **B1 C2 構造化会話** | `relations.note_contact ← conversation._contact ← conversation._apply_effects` | **8,786** | **29.5%** | **なし** |
| **A3 friend_graph 初期注入** | `friends._inject`(t=0・直接代入) | 552 | 1.9% | なし |
| **A5 party 連れ注入** | `party._inject`(日境界・直接代入) | 316 | 1.1% | なし |
| **B3 日次減衰** | `relations.decay_day`(直接減算) | 184 | 0.6% | なし |
| **B4/B5 dunbar 休眠 / 再会** | `dunbar._make_dormant` / `_rekindle` | **0** | 0% | なし |
| | **closeness 更新 合計** | **29,790** | 100% | |

> **LLM 関与 67.0% / LLM 非依存 33.0%**(件数ベース)。
> 同ランの **LLM 呼は 12,210 本** = **1 呼あたり 1.63 件**の closeness 更新
> (400体ランでは 22.5 件/呼。**この増幅率は群衆密度で 1 桁動く**)。

**`count` だけ動く経路**(closeness を渡さない)も別に数えた: 合計 **3,334 件** —
`tools._announce_dm`(LLM の `plan_event` ツール由来)1,482 /
`simulation._link_colocated`(途中入場の顔なじみ)584 /
`friends._inject` の台帳確保 552 / `simulation.__init__` の起動時顔なじみ 400 /
`party._inject` の台帳確保 316。

**この表の 4 つの読みどころ**:

1. **`dunbar` の休眠/再会が 0 件**。`pool.relations_cap: 60` と dunbar の上限に
   **250 体規模では誰も到達しない**。25万体・10日では到達するはずなので、
   **本選では 0 でないことを確認する**(`relation_dormant` / `relation_rekindle` の L1 件数)。
   0 のままなら「認知枠が一度も binding にならなかった」= それ自体が所見。
2. **日次減衰が 184 件と小さい**。理由は `decay_day` が
   **「当日接触した相手」を除外する**(`relations.py:203-205`)ため。
   密な街では大半の関係が当日に接触するので、減衰対象は**取り残された関係だけ**に絞られる。
   → 「減衰が全部を薙ぎ倒す」わけではない。**会わなくなった相手にだけ効く**という設計どおりの挙動。
   ★ただし居住者の初期友人グラフ(約 30 辺/人)は**在場しない相手を多く含む**ので、
   25万体では絶対数がこの比率のままとは限らない(規模依存)。
3. **`decay_day` は `record_contact` を通らない**(`rel["closeness"]` を直接引く)ので、
   **L1 にも L2 にも「何件減らしたか」が出ない**。tier を跨いだ分だけが
   `relation_break{cause=absence}` として見える。
   → U13(共在→関係)や U12(前史パネル)で closeness の軌跡を説明するときは、
   **G5 `relations.parquet` の差分の負側**を必ず見ること(L1 だけ見ると「関係は増える一方」に見える)。
4. **初期注入(friend_graph + party)は合計 868 件で 2.9%** に見えるが、これは
   **「1回きり」だからで、影響は件数では測れない**。t=0 に 552 件で
   **tier 2〜3 の関係が最初から在る**状態を作っており、その後の C1/C2 はその上を動く
   (§2.2 の閾値表: 会話で tier 2 に到達するには closeness 5.0 = 同日 5 接触が要る)。

**再取得コマンド**(プローブは `scratchpad/probe_relmap2.py`・repo 不触):

```
python <scratchpad>/probe_relmap2.py --profile conf/finals_observe.yaml \
  pool.present_cap=250 pool.dormant_cap=250 run.n_agents=250 run.n_steps=288 \
  run.seed=42 run.name=relmap_f4 model.backend=mock observer.checkpoint_every=0
```

### 4.4 実測から言えること(と言えないこと)

**言えること**:

**1行の答え**: **LLM 関与 67.0% / LLM 非依存 33.0%**(250体×2日・件数ベース・§4.3)。

1. **「LLM が発火しなければ関係値が動かない」は明確に偽**。
   **closeness 更新の 33.0%(9,838 件 / 29,790 件)は LLM 呼を 1 本も伴わない**。
   内訳は C2 構造化会話 8,786 + 初期注入 868 + 日次減衰 184。
2. **しかし多数派は C1(LLM 発話 + DM)である**(67.0%)。
   当初の予想(非 LLM が件数でも主)は**外れた**。理由は「1 発話が聞き手全員に届き、
   さらに両方向に記録される」という構造で、**LLM 呼 1 本が複数件の closeness 更新に増幅される**ため。
3. **その増幅率は規模で 1 桁動く**。250体で 1.63 件/呼、400体で 22.5 件/呼
   (400体ランの `speak` 2,261 本 → 50,766 件)。**「LLM が喋った回数」を関係形成の
   代理指標に使ってはいけない**。25万体では増幅率がさらに上がる。
4. ★**ただし C1 の 50% は「聞き手側」の更新**である(`_contact` が両方向に呼ばれる。§5.1b)。
   聞き手は**自分が発火している必要がない**ので、
   **「発火を要求される個体」の割合は 67.0% ではなく、その半分の 33.5% 程度**になる。
   → **発火しない個体の関係値も、実測の 2/3(33.0% + 33.5%)で動いている**。
5. **関係の「成立」(誰と誰が関係を持つか)は非 LLM が圧倒的**。t=0 の friend_graph が
   居住者に約 30 辺/人を注入し(552 件の注入で tier 2〜3 が最初から在る)、
   顔なじみ(984 件の count 更新)・party(316 件)がそれに乗る。C1/C2 が作るのは**その上の増減**。

**言えないこと(限界)**:

- **mock LLM である**。実 LLM では発話長・valence 分布・`magnitude` が変わるので、
  closeness の**増分の大きさ**は変わる。ただし**件数**は「聞き手の人数 × 発火数」で決まるので
  構造は同じ。
- **規模が違う**(250体・400体 vs 25万体)。§2.2 のとおり C1 は局所群衆密度に比例するので、
  **本選では C1 の比率がさらに上がる**と予想される。**この表を外挿してはいけない**。
  逆に `dunbar` の休眠/再会(本実測 0 件)は**本選では立ち上がる**はずで、
  非 LLM 側の比率を押し上げる方向に効く。
- **fire ON では測っていない**(finals で OFF。§5.5)。fire を開けたときの C1 件数の変化は未実測。
- **2 日しか回していない**。`decay_day` は「会わなくなった相手」に効く機構なので、
  **日数が伸びるほど非 LLM 側(減衰)の比率が上がる**。10 日ランの比率はこの表より
  非 LLM 寄りになると予想される。

---

## 5. `cognition.fire` の drive 駆動設計との整合

### 5.1 fire は何を差し替えるのか

`cognition/fire.py` は発火判定を

```
S_i(t) = Σ_c  g_ic · |o_c(t) − ô_ic| / σ_c  +  Σ_j w_ij·[trigger_j]
発火 ⟺ S_i(t) > θ_i(t)
```

のイベントキューに置き換える。差し替わるのは **`_phase_drive` の `requesters` 集合だけ**である
(`engine/scheduler.py` の `fire_on` 分岐: `requesters = [a for a in active if a.id in due and ...]`)。

正確に書くと、OFF/ON の差は `requesters` の述語 1 つである:

```
OFF: requesters = [a for a in active if a.drive >= _eff_thr(a) and step >= a.refractory_until]
ON : requesters = [a for a in active if a.id in due and step >= a.refractory_until
                   and (a.id in forced or logistic or a.drive >= _eff_thr(a))]
```

`a.id in due` が**必要条件として増える**だけで、そこから先(対面 face の確定発火・予算・抽選)は同一。

**したがって fire が触らないもの**(= §2 の A / B 列は fire の ON/OFF で 1 行も変わらない):

- `_phase_c2`(C2 構造化会話)は独立フェーズで `sim.agents` を全走査する。`due` を見ない。
- `_phase_relations_day`(decay + dunbar day_phase)は日境界フェーズ。`due` を見ない。
- `form_parties` / `build_friend_graph` / 顔なじみは起動・日境界の構造的過程。
- `_phase_joint`(共同行動の編成・承諾)も `due` を見ない。
- **`_decide` は毎 step **全在場・非睡眠個体**に対して呼ばれる**(`actions = [(agent, _decide(...)) for agent in active]`)。
  `due` に居ない個体も `_decide` を通る = **返答保証(`_reply_to`)は fire を迂回する**。

### 5.1b ★最重要: **聞く側は発火しなくても関係値が動く**

`_apply` の `speak` 分岐は、話者と聞き手の**両方向**に `_contact` を呼ぶ:

```
_contact(sim, hearer, agent.id, agent.name, _htext, v_text, ...)   # 聞き手→話者
_contact(sim, agent,  hearer.id, hearer.name, "",     v_text, ...)  # 話者→聞き手
```

**聞き手は自分が発火していなくてよい**(`hearers_of` に入っているだけでよい)。
つまり fire で発火が絞られても、**「その場に居て誰かの発話を聞いた」個体の closeness は動く**。
実測(§4.3)の C1 系 19,952 件のうち**半分(約 9,976 件)は聞き手側の更新**であり、
この半分は **fire で発火しなかった個体にも起きる**。

同じことが C2 にも言える(`_apply_effects` が `_contact(a,b)` と `_contact(b,a)` を両方呼ぶ)。

**発火を必要とする更新の割合**(実測 29,790 件を分母に):

| 区分 | 件数 | 比率 |
|---|---|---|
| **発火した個体の側**(C1 の話者側) | ≈ 9,976 | **33.5%** |
| 発火していない個体の側(C1 の聞き手側) | ≈ 9,976 | 33.5% |
| LLM を一切通らない(C2 + 初期注入 + 減衰) | 9,838 | 33.0% |

→ **「発火しない人の関係が凍る」ことは構造上ない**。約 2/3 は発火を要求しない。

### 5.2 「関係変化と LLM 発火の相関」はどの機構で生まれるか

3 つある。**どれも「関係値が S に入る」からではない**。

**(a) 共通原因としての共在**。`cognition/channels.py` の観測チャンネル一覧に
**関係チャンネルは 1 本も無い**(`ext.crowd_local` / `ext.encounter` / `ext.heard` /
`ext.signage` / `ext.transit_delay` / `ext.weather_temp` / `body.*` / `pred.unmet`)。
closeness は S に**直接は入らない**。しかし `ext.encounter`(知覚半径内の起きている他者数)と
`ext.heard`(この step に聞いた発話 + 受信 DM 数)は、C2 の会話成立条件・C1 の hearers 集合と
**同じ物理的近接**から立つ。つまり「関係が動く状況」と「S が上がる状況」は
**共在という共通原因**で相関する。関係値そのものが発火を引くのではない。

**(b) 返答保証という直結経路**。話しかけられた個体は `_decide` の先頭
(`agent._reply_to is not None`)で **`due` を通らずに** LLM 返答を撃つ
(予算があれば)。fire ON でも `_social_via` が `reply` を **SOCIAL 発火源として第一級化**し、
`cog_event{reason:social, via:reply}` を L1 に残す。
→ **「関係が動くような出来事(話しかけられた)」は、fire のキューの外側で必ず発火する**。
これが「関係変化 → 発火」の唯一の直結経路である。

**(c) C2 → C1 昇格**。`conversation._apply_effects` の (5) が、帰結が
`opinion_gap`(強い意見差)/ `rapport_shift`(関係の転機)のとき
`drive_mod.add(..., "state_change", scale=...)` で **drive を余分に押し上げる**。
未知語接触は `unknown_word` で同様。fire ON では drive の**閾値の上向き横断**が
INTERNAL 割込み(`fire.py:526-536`)になるので、
**C2 で関係が大きく動いた個体ほど、次 tick に割込み発火しやすい**。
→ これが「関係変化 ⇒ 発火」を設計として作っている唯一の機構で、
**方向は「関係が先・発火が後」**である(逆ではない)。

### 5.3 ユーザー仮説の評価

> 「初期からシミュレーションの中で関係値が変わらない人は認識が変わるイベントもなさそうだし、
> 発火させる必要はない気がする」

| 論点 | 評価 |
|---|---|
| 「関係値が変わらない人は発火不要」 | **設計としては正しく、かつ既に実装されている**。fire の S は「観測の予測誤差 + 身体ゲージ」で決まり、静かな個体は θ を超えない = 周期発火の間隔だけで回る。関係が動く=共在がある個体は `ext.encounter`/`ext.heard` が動く=S が上がる。**「関係が動く人ほど発火する」は (a) の共通原因で自動的に成立する**。 |
| 「関係値が変わらない人」は実在するか | **finals 構成では稀**。C2 が 1 日最大 40 会話まで拾い、`decay_day` が毎日 −1.0 を掛ける。**動かないのは「街に出てこない個体」だけ**で、それはそもそも `sim.agents` に居ない(在場ローテーションの外)。→ **前件が空に近い**ので、この仮説は「fire を絞ってよい理由」にはなるが「関係が止まる心配」の反証にはならない(心配自体が不要)。 |
| 「LLM 推論時以外の関係構築がなくなる」 | **ならない**。§2 の A/B 列(初期注入・C2・decay・休眠/再会・joint 維持)はすべて fire を経由しない。さらに **C1 の聞き手側の更新**も発火を要求しない(§5.1b)。 |
| 「関係値が作られる関係はほとんど LLM 発火と結びついている」 | **半分正しい**。closeness 更新の件数では C1(LLM 発話 + DM)が多数派(実測 §4.3 で **67.0%**)。ただし ① そのうち**半分は聞き手側**=発火不要(→ 発火を要する更新は **33.5%**)② **関係の成立**(誰と関係を持つか)は friend_graph/顔なじみ/party という非 LLM の初期注入が圧倒的 ③ **減る側**(decay)は 100% 非 LLM。**「結びついている」と「それだけで決まる」は別**。 |

### 5.4 ★正直な非対称(fire を開けるなら見るべき点)

fire ON で LLM 発火が減ると、**C1 由来の closeness の「増加」だけが減る**。
一方 `decay_day` の **−1.0/日は fire と無関係に効き続ける**。
つまり発火を絞ることは、関係台帳に対して**非対称に痩せる方向**へ働く。

- ★**実測はこの懸念を強める方向に出た**(§4.3): closeness 更新の最大源は C2 ではなく **C1**
  (19,952 vs 8,786 = 約 2.3 倍)。**発火を絞ると増分の 2/3 が細る**一方で、
  減衰は 1 件も変わらない。C2 が受け皿として残るので**ゼロにはならない**が、
  「影響は小さい」とは言えない。
- **C2 を切って fire だけ開ける構成にすると、供給が C1 だけになり、decay に食い負けて
  tier が総崩れする**。finals は `conversation.enabled: true`(現行 `conf/finals_observe.yaml:819-820`)
  なのでこの穴は無いが、**fire を開ける実験条件で C2 も切る組み合わせは作らないこと**。
- ★緩和材料が 2 つある:
  (i) **発話の増幅率は群衆密度に比例する**(250体で 1.63 件/呼・400体で 22.5 件/呼)ので、
  25万体では 1 発火あたりの関係更新がさらに増える = **発火数が減っても総量は思ったほど減らない**。
  (ii) ★**並行レーンが `lod.budget.tiers` を finals ON にした**
  (現行 `conf/finals_observe.yaml:905-910`: `reply_share: 0.20` / `life_share: 0.30`)。
  返答レーンが予約されたので、**fire ON で発火同士の競合が増えても返答は原理的に食われない**
  = §5.2(b) の直結経路(関係が動く出来事 → 発火)が**予算面でも保護された**。
  conf 自身が「**D1(fire)を開けるならこちらも ON でなければならない**」と明記している。
- 検証法: `observer.relations_daily`(G5)の closeness 差分の**符号の分布**を日次で見る。
  正の合計 / 負の合計 の比が 1 を下回り続けたら痩せている。
  L1 側は `relation_break{cause=absence}` と `relation_tier` の比で同じことが読める
  (`lens.structure` が `edges_formed` / `edges_broken` / `edges_decayed` / `edge_churn_rate` を
  L2 に既に出している。finals `lens.structure.enabled: true`)。

### 5.5 fire の現在地(2026-08-15 の作業木で取り直した事実)

`conf/finals_observe.yaml:440-442` で `cognition.watch` / `fire` / `engaged` の 3 行は
**まだコメントアウトされている**。ただし前後の注記が調査中に**並行レーンによって書き換わった**:

- 旧: 「OBS-U3『認知 ON の 8/14 留保』・**未承認**」
- 現(`conf/finals_observe.yaml:422`):
  **「★D1 = b案(2026-08-15 ユーザー決定): 『8/15 診断で呼数実測 → 許容ならこの 3 行を解凍』」**
  判定基準は「fire ON による**予算内呼の増分が総枠の +15% 以内**」。
  詳細手順は `docs/plans/decision-dashboard.md` §D1。

`cognition.g_update: true` は宣言されているが、`plasticity.enabled()` が `fire.enabled()` を
前提にしているため**現状は 1 行も走らない**(conf 自身が `★★正直な申告` として明記)。

→ **本節の議論は「開ける判断が出たときのため」のものである**。
**開けなければ関係形成は 100% 現行経路(§2)のまま回る**。
そして**開けても §2 の A/B 列(33.0%)と C1 の聞き手側(33.5%)は変わらない** ——
影響を受けるのは **C1 の話者側 33.5% だけ**である。

### 5.6 ★もし fire を開ける判断が出たら(先に測ること)

1. **同一 seed で fire OFF/ON を 2 本**(縮小規模でよい)走らせ、
   **`hear` の総件数**を比べる(= C1 由来 closeness 更新の 1/2 に等しい代理量。L1 だけで取れる)。
2. **`lens.structure` の `edges_formed` / `edges_decayed` の日次比**を並べる。
   ON 側で `edges_decayed / edges_formed` が上がっていれば、関係台帳が痩せている。
3. **`active_relations_mean`(L2・dunbar 由来)の日次系列**を並べる。
   ON 側が単調に下がるなら、認知枠より先に「供給不足」で痩せている。
4. 上の 3 つが揃って悪化するなら、**fire は開けない**か、
   `conversation.c2.meet_prob` を上げて供給を補う
   (ただしそれは較正済み既定からの逸脱 = 別途ユーザー判断が要る)。

---

## 6. 正直な限界

1. **実測は mock LLM・小規模**(§4 の条件)。実 LLM では発話の長さ・valence 分布が変わるので
   C1 側の closeness 増分の**大きさ**は変わる。ただし**件数比**は C2 の `daily_cap` と
   lod 呼数上限という構造で決まるので、桁は動かない。
2. **`count` と `closeness` を混ぜて数えていない**。§4 は closeness を動かした件数
   (= `closeness_delta is not None` の呼び出し)で数えた。`count` だけ動く経路
   (A1/A2/A4/C3')は別欄に出してある。
3. **両方向カウント**。C1/C2 とも 1 会話 = 2 件(actor→other と other→actor)として数えている。
   「会話の本数」に直したければ 2 で割る。
4. **relations_daily(G5)は日境界の差分**なので、日内に上がって日内に下がった軌跡は
   1 行に潰れる。日内の増減の全数は L1 にも出ない(tier 跨ぎだけ)。
5. **fire ON の実測はしていない**(finals で OFF・`affects_k=true` で承認が要る)。
   §5 は**コードの読み**であって実測ではない。開ける判断が出たら
   「C1 由来 contact 件数の ON/OFF 比」を先に測ること。
6. ★★★**調査中に見つけた本選ブロッカー(本調査の対象外・担当レーンへ申し送り)**:
   並行レーンが追加した `src/society/observer/starvation.py`(DPH-O)が新しい L1 kind を 3 種
   出すが、**3 種とも `src/society/observer/causality.py` の `CAUSE_OF_KIND` に未登録**である。
   `observer/logger.py` の `log()` が全イベントで `causality.cause_of(kind)` を引き、
   未分類なら **`KeyError: 未分類のイベント種類 '...'`** を送出する設計なので、
   **`observer.starvation.enabled: true`(現行 `conf/finals_observe.yaml:928-929` で ON)の
   ランは最初の 1 件で即死する**。実測(2026-08-15 の作業木):

   ```
   plan_skipped    -> KeyError (未分類)
   reply_starved   -> KeyError (未分類)
   budget_starved  -> KeyError (未分類)
   ```

   本調査は**プローブのプロセス内だけ**分類を補って回避した(repo は 1 バイトも触っていない)。
   **`CAUSE_OF_KIND` へ 3 行足すのは担当レーンの仕事**。
   ★実際に本調査の 1 本目のプローブランは、この KeyError で `_phase_planning` の
   最初の呼び出し中に落ちている(= 実装途中の状態を踏んだだけで、本調査の結論には影響しない)。
7. **並行改修のため行番号がずれる**。調査中に `engine/scheduler.py` / `engine/simulation.py` /
   `cognition/lod.py` が別バッチで書き換わった(`sim.net.add_contact` の行が 3330 → 3416 へ移動)。
   本文書は**関数名・シンボル名を正**として読むこと。

---

## 7. 関連

- [initial-relations-improvement.md](initial-relations-improvement.md) — **姉妹文書**。初期関係の作り方の改善案(R1-R5)
- `docs/plans/endogenous-relations-plan.md` — 承諾/誘い/質の内生化の設計正典(片方向 hook の原則)
- `docs/research/relationships-activities.md` — 関係と共同行動の較正
- [unique-data-candidates.md](unique-data-candidates.md) §U13(g)/ §U12(g)/ §U9(g) — 本書の結論を観察方法へ落としたもの
- `src/society/observer/relations.py` — G5 サイドカーのスキーマと正直な限界
- `docs/research/community-detection.md` — 下流のコミュニティ検出
- `docs/plans/decision-dashboard.md` §D1 — `cognition.fire` を開けるかの判定基準(b案)

---

## 8. 一枚まとめ

| 問い | 答え |
|---|---|
| 関係は LLM で作られるか | **成立は非 LLM が圧倒的**(friend_graph / 顔なじみ / party の初期注入)。**増減は LLM 関与 67.0% / 非依存 33.0%**(実測・250体×2日) |
| fire で「LLM 推論時以外の関係構築」が消えるか | **消えない**。fire が触るのは `_phase_drive` の `requesters` だけ。C2・decay・dunbar・初期注入・joint 同席は全て fire の外 |
| 関係変化は LLM 発火と結び付いているか | **相関はあるが同一ではない**。相関の源は ①共在という共通原因 ②返答保証(fire を迂回・予算も `lod.budget.tiers` で予約済み)③C2→C1 昇格(方向は「関係が先・発火が後」) |
| 関係値が変わらない人は発火不要か | **その通りで、既にそう実装されている**。ただし finals 構成では前件がほぼ空(C2 と decay が全員に効く) |
| 発火を絞ると何が起きるか | **C1 の話者側 33.5% だけが細る**。聞き手側 33.5% と非 LLM 33.0% は不変。一方 **decay は不変**なので**非対称に痩せる**。開けるなら §5.6 の 4 点を先に測る |
