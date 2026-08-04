# IF レーン(LLM⇄世界インターフェース増強)実装前 文献リサーチ

> 2026-08-05。対象 = [llm-world-interface-audit.md](llm-world-interface-audit.md) §6 の実装候補 IF-1〜IF-5。
> 目的 = 「発明する前に、先行研究がすでに決めている設計パラメータを取り込む」。
> 制約 = R1ドクトリン(新機能既定OFF・golden L1バイト一致・k非依存・no-fingerprint・専用乱数stream・観測がシムを変えない)、
> LLM追加呼び出し原則ゼロ、25万体スケール。
>
> **本文書は実装ではない。**設計判断の材料であり、採否はユーザーの指示による。

**取得レベルの明示(誠実性のため)**
| 到達度 | 文献 |
|---|---|
| 本文全文を機械抽出して読んだ | Heylighen 2011 working paper(23p)/ Caiani et al. 2016 JEDC(34p) |
| HTML全文をフェッチして該当節を確認 | Park et al. 2023(ar5iv)/ OASIS 2024 / arXiv 2605.17353 / W3C PROV-DM / Fowler Event Sourcing / Zeigarnik-Ovsiankina メタ分析(Nature HSSC 2025)/ Ledger-State Stigmergy 2026 / PROV-AGENT 2025 |
| 検索結果の要約・abstract 相当まで | Grassé 1959 / Daley-Kendall / Maki-Thompson / Kempe et al. 2003 / Reflexion / Voyager / SayCan / Inner Monologue / ReAct / Helbing et al. 1997 / Parunak digital pheromone / Masicampo & Baumeister 2011 / EconAgent / SIMPROV |

---

## §0. 3行サマリ

1. **5件すべてに先行研究の設計解がある。ゼロから設計する箇所はほぼ無い。** IF-4 はスティグマジー(Grassé→Heylighen→Parunak の「集約・蒸発・拡散」3演算)、IF-1 は W3C PROV + event sourcing、IF-5 は SFC の四重記入(Caiani et al. が**そのままテストに落とせる検査法を2本**提示している)。
2. **主張の向きを変えるべき発見が2つ。** (a) Generative Agents の情報拡散測定は**事後の自然言語インタビュー**であり、IDつき情報オブジェクトを持っていない → 本シムの `provenance.Item`+`transmissions` は先行研究に**追随ではなく既に先行**しており、IF-3 は「不足の補填」でなく「優位の完成」として設計・記述すべき。(b) **Zeigarnik効果は2025年のメタ分析(59文献)で否定された**(中断/完了の再生比 0.99)。生き残ったのは **Ovsiankina効果=中断課題の再開(67%)**。IF-2 の心理側の正当化は「拒否されると記憶に残る」ではなく「**中断は再開/再計画を誘発する**」に置き換える必要がある。
3. **既定値・上限・減衰速度は文献が具体化している。** 痕跡は「情報が陳腐化する速度」に合わせた減衰が**機能的に必須**(古い痕跡は無関係ではなく**誤誘導**になる=Heylighen)。経済は「行と列が全時点でゼロ」+「全主体の純資産合計=実物資産」の2検査(Caiani)。噂は「飽和」でなく「**語り手が黙ること**」で止まる(Daley-Kendall/Maki-Thompson)。

---

## §1. スティグマジー(IF-4: 痕跡=場所イベント履歴の汎用機構)

### 1-1. 指摘(文献が言っていること)

**定義の系譜。** Grassé (1959) は白蟻の巣修復の観察から stigmergy を提唱し、「**労働者が自分たちの成し遂げた仕事そのものによって刺激されること**」と定義した(語源 = στίγμα「刺す印」+ ἔργον「仕事」)。Heylighen (2011 WP / 2016 CSR I) はこれを一般化し、次の定義を与える:

> *stigmergy is an indirect, mediated mechanism of coordination between actions in which a perceived effect of an action stimulates the performance of a subsequent action.*
> (行為の**知覚された効果**が後続行為の遂行を促す、間接的・媒介的な行為間調整の機構)

刺激は決定論ではなく確率的で、`P(action | condition) > P(action)` として定式化される。

**構成要素は4つ+1。** action(世界状態を変える因果過程)/ agent(**必須ではない**。単一主体の行為間調整にも成立する)/ **medium** / **trace** / coordination。Heylighen は medium を「環境(environment)」と呼ぶ通例を明確に退ける:

> *The medium is that part of the world that undergoes changes through the actions, and whose states are sensed as conditions for further actions.*

すなわち medium とは「**関与する全エージェントが知覚でき、かつ変更できる**世界の部分」であり、空(見えるが変えられない)も海(変えられるが結果が見えない)も medium ではなく、砂浜が medium である。trace は「行為が medium に残した知覚可能な変化」で、意図的な marker とは区別される(trace は副産物でもよい)。

**分類軸(Heylighen の5次元。すべて連続量であって二値ではない)**
| 軸 | 一方の極 | 他方の極 |
|---|---|---|
| 主体数 | individual(単独ハチの巣作り。段階 S1→R1→S2→R2…) | collaborative |
| 量/質 | quantitative(強度が連続。フェロモン濃度・価格) | qualitative(状態種が離散。巣の建設段階) |
| 痕跡の性格 | **sematectonic**(仕事そのものが刺激。Peirce の index) | **marker-based**(専用の記号。Peirce の symbol) |
| 持続性 | **persistent → 非同期スティグマジー**(同時に居合わせる必要がない) | **transient → 同期スティグマジー**(群れ・警戒声) |
| 到達範囲 | **broadcast**(全員が知覚) | **narrowcast**(1人〜数人。medium の位相と拡散度で決まる) |

**減衰は欠陥ではなく機能である(IF-4 の設計上いちばん重要な指摘)。** Heylighen:

> 痕跡は後続作業への指示として機能する。更新が続かなければ、その情報は状況の変化とともに少しずつ陳腐化する。枯れた餌場を指すフェロモン道は「無関係になった」のではなく、**無駄な旅を誘発する点で誤誘導(misleading)になった**。

そして減衰速度の設計原理を明示する:「新しい寄与の重み(学習パラメータ)は、既存痕跡の減衰速度(忘却パラメータ)と**実質的に等価**である。その最適値は、**情報が陳腐化する速度に依存する**」。文献が挙げる時間スケールの例: 白蟻の柱の位置=ほぼ陳腐化しない(永続)/ 蟻の餌場=数時間〜数日 / 捕食者の出現=秒(音・光=波動なので即座に減衰)。

**実装の3演算(Parunak, デジタルフェロモン)。** place agent が場を保持し、walker が deposit/sense する。場に対する演算は正確に3つ:
1. **aggregation**(同 flavor の堆積を強度として合算)
2. **propagation / diffusion**(propagation factor の比率だけ近傍へ渡す。**factor=0 で拡散なし**)
3. **evaporation**(evaporation factor で時間減衰)

さらに **flavor**(フェロモンの種別。赤=敵性、青=友軍のように**意味が異なる場を混ぜない**)。

**都市・歩行者への応用。** Helbing, Keltsch & Molnár (1997, *Nature* 388:47-50) の active walker モデルは、歩行者が地面に残す「歩きやすさ」の痕跡と、その自然減衰(草の回復)の釣り合いから公園の desire path 網が創発することを示した(PRE 56:2527 に詳細版)。近年も desire path の ABM 再現(Ma et al. 2024, *EPB: Urban Analytics and City Science*)が続いており、「エージェントが地表に足跡を残し、それが affordance を上げる」という定式が標準になっている。

**永続媒体の落とし穴。** 分散台帳を medium と見る 2026 年の形式化(Ledger-State Stigmergy)は、生物系との決定的な差を突く: 「フェロモンは蒸発するが、台帳の状態は蒸発しない」。生物系には**組み込みのガベージコレクション**があるが、デジタル媒体では**明示的な失効ロジックが無ければ古い痕跡が恒久的に居座る**。

### 1-2. 本シムへの適用

**本シムには既に完成したスティグマジー実装が1本ある。** `tools.py` の貼り紙(flyer)である:

- medium = **node**(`flyers_by_node: dict[str, list]`)
- trace = flyer(`{author, node, text, items, expire_step, viewers}`)
- evaporation = `flyer_ttl_steps=144`(10分step換算で**ちょうど1日**)+ `_flyers_expire` が `flyer_expire` イベントを出す
- capacity = `flyer_max_per_node=3`、超過は**古い順に押し出し**て `flyer_expire{reason:"overflow"}`
- 観測 = 同一 node の者だけが `_view_flyers` で見る(**narrowcast**)。`viewers` set で1体1回に固定
- 効果 = 記憶1行 + `_hear_words` による語彙受領(=`provenance` の transmission)

Heylighen の分類軸で言えば、flyer は「marker-based × qualitative × persistent(1日) × narrowcast × collaborative」。一方、監査 §3 の「混雑(現在地)」は「**sematectonic** × quantitative × transient × broadcast」であり、**本シムは既にスティグマジーの2象限を実装している**。IF-4 は新機構の発明ではなく、**flyer の構造を kind 一般に持ち上げる作業**である。

監査 §3 が指摘した穴「場所のイベント履歴 = L1 に座標付きで全部残るがシム内から読む経路ゼロ」は、Heylighen の用語では「**medium ではない**」状態そのものである(変更できるが知覚できない=海に石を投げる状態)。

### 1-3. 設計への具体的示唆

1. **3演算のうち propagation(拡散)は入れない。** Parunak の枠組みでは propagation factor = 0 が正当な設定であり、文献的に説明がつく。理由は本シム固有: (a) node グラフ上の拡散は近傍列挙順に依存し golden のバイト一致を壊しやすい、(b) 25万体で O(node × kind) の毎step掃引が乗る、(c) 「隣の駅に噂が滲む」は情報オブジェクト(IF-3)の担当であって痕跡の担当ではない。**aggregation と evaporation の2演算に限定**する。
2. **kind ごとに独立の場を持つ(flavor)。** 「混雑の痕跡」と「揉め事の痕跡」と「賑わいの痕跡」を1つのスカラーに混ぜない。Parunak の flavor は意味の異なる場を混ぜないことを要求している。実装上は `traces_by_node: dict[node, dict[kind, list]]`。
3. **TTL は「情報が陳腐化する速度」で3階層に分ける**(Heylighen の学習=忘却パラメータ)。既存値を基準に、transient(数step=混雑・行列)/ daily(144step=貼り紙・出来事)/ persistent(週オーダー=場所の評判・place_bind)。**単一の TTL 既定値を全 kind に使うのは文献に反する。**
4. **容量と押し出しは flyer の既存流儀をそのまま継承する。** kind ごとの `max_per_node`、超過は古い順、`*_expire{reason:"overflow"}` イベント。新しいイベント種を発明せず既存 payload 形式に揃えれば、分析ツールの追加コストがゼロになる。
5. **観測範囲は narrowcast(同一 node)から始める。** broadcast(遠くの痕跡が見える)は「全員のプロンプトに同じ文字列が入る」経路を作るため no-fingerprint 上の危険が跳ね上がる。Heylighen も「多くの研究は暗黙に broadcast を仮定するが、実際には常にある程度の narrowcast である」と述べており、narrowcast 既定は文献的にも自然。
6. **観測が世界を変えないための既存流儀 = `viewers` set。** 痕跡を見る行為が痕跡を強化する(=観測が世界を変える)設計は、R1 の「観測がシムを変えない」と衝突しやすい。**痕跡の強化は「行為」の副産物としてのみ起こし、「観測」では絶対に起こさない**ことをテストで固定する。これは Heylighen の定義(trace は action の効果であって perception の効果ではない)とも一致する。
7. **明示的失効ロジックの義務化。** Ledger-State Stigmergy の指摘どおり、デジタル媒体は放置すると痕跡が永久化する。checkpoint/resume を跨いだ `expire_step` の整合(第75バッチ dunbar の日境界問題と同型)を最初から回帰テストに含める。
8. **R1適合。** 減衰・容量・押し出しはすべて決定論(乱数stream 0本)。既定 OFF 時は `traces_by_node` を生成せず、payload に鍵を生やさない(第75の dormant キー方式と同型)。LLM呼 0本。プロンプトに入るのは「痕跡の本文」であり、これは flyer が既に通した経路と同じ帯域なので新しい fingerprint 面を作らない。

---

## §2. 噂・情報伝播のオブジェクト化(IF-3: 情報オブジェクトの一般化)

### 2-1. 指摘(文献が言っていること)

**古典噂モデル: 止まる理由は「飽和」ではなく「語り手が黙ること」。** Daley & Kendall (1964, *Nature* 204:1118; 1965) は人口を **ignorant / spreader / stifler** の3クラスに分け、(a) spreader→ignorant で ignorant が spreader 化、(b) **spreader→spreader で両者が stifler 化**、(c) spreader→stifler で spreader が stifler 化、と定めた。Maki & Thompson (1973) は (b) を「接触した側の spreader だけが stifler 化」に簡約した。両モデルとも極限で **最終的な ignorant 比 ≈ 20%**、**spreader のピーク比 = 1 − ln2 ≈ 0.3069** に収束する(近年の arXiv 論文群が繰り返し引用する古典結果)。

要点は「**全員が知って飽和するから止まる**」のではなく「**既知の相手に出会った語り手が語るのをやめるから止まる**」ことである。だからこそ最終的に2割が永久に知らないままになる。

**ネットワーク上の拡散: independent cascade / linear threshold。** Kempe, Kleinberg & Tardos (2003, KDD) は IC(各辺が**一度だけ**確率 p で活性化を試みる)と LT(各ノードが閾値をランダムに引き、活性隣接の重み和が閾値を超えると活性化)を統一的に扱い、影響最大化が NP困難であること・貪欲法が劣モジュラ性により (1−1/e)≈63% 保証を持つことを示した。IC の「**辺ごとに一度だけ**」という規則は、実測データとの比較可能性を担保する上で決定的である。

**Generative Agents (Park et al. 2023) の測定法 — ここが最大の発見。** Smallville の25体で、Sam の市長選出馬と Isabella のバレンタインパーティの拡散を測定したが、その方法は:

> *To observe whether the information has spread, we conduct interviews at the end of the two game days with each of the 25 agents*

つまり **2日終了時点で全25体に自然言語で聞く**。「バレンタインパーティがあるのを知っていましたか?」「誰が市長選に出ているか知っていますか?」。結果は Sam 1体→8体(4%→32%)、Isabella のパーティ 1体→13体(4%→52%)。肯定回答は**記憶ストリーム内の該当対話を人手で特定して幻覚でないことを検証**しており、関係形成の設問(453回答)では **1.3%(6件)が幻覚**だった。

**すなわち Generative Agents には ID つきの情報オブジェクトが存在しない。** 拡散木は事後に記憶ストリームを人手で辿って再構成するものであり、機構としては持っていない。

**OASIS (2024, 100万エージェント) の構造化。** 投稿・コメント・関係をリレーショナルDBの6テーブル(users / posts / comments / relations / **traces** / recommendations)で持ち、**各投稿は一意IDを持つ**。伝播の測定指標は **scale(参加者数)/ depth(グラフ最大深さ)/ max breadth(深さごとの最大参加者数)** の3つ。実データとの整合は NRMSE ≈ 30%、depth は実データより**顕著に浅い**。「噂は真情報より有意に広く到達する」という計算社会科学の知見を再現。

**2026年の噂シム(arXiv 2605.17353)。** claim を「内容 + 知覚信頼度 + 情報源ID」の構造化オブジェクトとして持ち、毎ラウンド約10%のエージェントに直接曝露、他は隣接からの伝聞。ただし**信頼度判定 τ ∈ [0,1] とスタンス4分類(support/deny/query/comment)に LLM 呼を使っている**。本シムの「LLM追加呼ゼロ」制約とは正面から衝突する設計。

**発話テキストから追加LLM呼なしで情報オブジェクトを抽出する前例。** 文献側で確立した方式は3つ:
- **(a) 同一呼び出し内の構造化フィールド**(追加呼ゼロ。構造化出力/関数呼び出しで本文と並べて ID や属性を吐かせる)
- **(b) 語彙・部分文字列マッチ**(安価・決定論。ただし意味的言及を取り逃がす/固有名詞頻出領域で過剰一致)
- **(c) テンプレート化された行為**(「招待する」「伝える」を行為APIの引数にして ID を直接運ぶ)

限界は明白で、(b) は再現率と適合率の両方で妥協が要る。truth_ledger の docstring が既に自認している「意味的な言及(場所名を出さずに同じ話をする)は捉えられない/地名頻出の街では過剰一致しうる」は、この文献的限界そのものである。

### 2-2. 本シムへの適用

本シムの `observer/provenance.py` は、実は **W3C PROV の噂版をすでに実装している**:

```python
@dataclass
class Item:
    item_id: str
    kind: str            # label | vocab | rumor | institution ...
    text: str
    creator: int
    born_step: int
    transmissions: list[tuple[int, int, int, str]]   # (step, from, to, channel)
```

`transmissions` は「誰から誰へ・いつ・どのチャネルで」の有向辺列であり、**IC の実現(realization)そのもの**である。事後にカスケード木を完全再構成できる。Generative Agents が人手で復元し、OASIS が DB テーブルで持つものを、本シムは **1体1行のイベントとして走行中に記録している**。

そして `kind` には `rumor` が**すでに宣言済み**である。IF-3 は新設ではなく「宣言済みの枠に実体を入れる」作業。

一方 `truth_ledger.py` は fact/belief を持ち、belief に「情報源・取得step・親ノード」を持たせて伝播木を構成できる。話題一致は**部分文字列**、上限は `max_facts_per_utterance`、鮮度は `fact_ttl_steps` で抑えてある。これは上記 (b) 方式の完全な前例であり、**canary による漏洩検査(接頭辞1本の substring 走査)**という「台帳をエージェントに見せない」保証機構まで付いている。

### 2-3. 設計への具体的示唆

1. **主張の向きを変える。** IF-3 は「先行研究に追いつく」機能ではない。**Generative Agents は事後インタビュー(=追加LLM呼、しかも幻覚率1.3%)でしか拡散を測れないのに対し、本シムは走行中の台帳から誤差ゼロで測れる**。これは論文で主張すべき方法論上の優位であり、IF-3 の設計目標は「この優位を rumor/伝聞まで広げること」と定義するのが正しい。
2. **`provenance.Item` に新スキーマを足さない。** `kind="rumor"` を実体化するだけで PROV 相当の骨格は既にある。`ItemStore.new_item` / `transmit` を再利用すれば、分析19本のカスケード木ツールが**そのまま効く**。新しい伝播記録系を作るのは二重化になる。
3. **停止規則(stifler)を明示的に conf 化する。** 現行 truth_ledger の減衰は「伝聞ホップ数による 0.5 へのドリフト+確信度減衰」で、**Daley-Kendall の stifler 化に相当する規則がない**。噂が止まる理由が本シムには存在しない状態。conf で少なくとも次を選べるようにする:
   - `stifle: none | dk | mt`(既定 none = 現行不変)
   - `once_per_pair: bool`(IC の「辺ごとに一度だけ」。真なら Kempe et al. と比較可能になる)
   これにより「本シムの拡散曲線が DK/MT の理論値(最終ignorant≈20%、ピーク≈0.307)とどれだけ違うか」が言える。**LLMエージェントが古典噂モデルからどう逸脱するかは、それ自体が論文の主張になりうる。**
4. **抽出方式は (a)>(c)>(b) の優先順で。** `coin_label.word` が既に (a) の前例(同一呼び出し内の構造化フィールド=追加呼ゼロ)であり、監査 §2-B の帯域3として実績がある。伝聞・招待は (c)(行為APIの引数に item_id を載せる)。(b) の部分文字列は truth_ledger 同様の**上限+鮮度クランプ付き**で最後の受け皿にする。**追加LLM呼(=k汚染)は一切不要**であることを明記する。
5. **測定指標を OASIS に揃える。** analyze 側に **scale / depth / max_breadth** を追加(観測のみ=シム不変)。既存の伝播木ツールから計算できる。OASIS が「depth が実データより浅い」と自認しているので、本シムの depth を並べれば直接比較の主張が立つ。
6. **no-fingerprint。** 噂本文がプロンプトに入る経路は「発話テキスト」という既存の最強帯域と同一で、新しい面を作らない。ただし `item_id` **そのものは絶対にプロンプトへ入れない**(truth_ledger の canary と同型の静的検査 + 実行時検査を流用)。ID は観測側だけの概念に閉じる。
7. **25万体スケール。** `transmissions` を Item 内の list で持つとホット Item が O(N) に膨れる。25万体では **Item 側の list は上限付き(または保持しない)にし、正典は L1 の `transmission` イベント列**とする(event sourcing の考え方=§4)。事後再構成は parquet 側で行う。

---

## §3. 行為拒否のフィードバック(IF-2: 拒否通知の段階conf化)

### 3-1. 指摘(文献が言っていること)

**工学側: 環境フィードバックは効く。ただし「粒度」で効き方が違う。**

- **SayCan** (Ahn et al. 2022): LLM が出す「有用性」と、学習済み価値関数が出す「**実行可能性(affordance)**」を掛け合わせて次スキルを選ぶ。「Say(タスク接地)× Can(世界接地)」。PaLM-SayCan は正しいスキル列を **84%** で選び、実行成功は **74%**。重要な限界を著者自身が述べる: **環境フィードバックは現ステップの価値関数だけであり、スキルが失敗したり環境が変化しても必要なフィードバックが得られない**。
- **Inner Monologue** (Huang et al. 2022): その限界に対する直接の回答。**success detection(二値)/ scene description(記述)/ human interaction(介入)** の3種のフィードバックを**自然言語で**LLMに戻し、ループを閉じる。追加学習なしで、卓上再配置・長期horizonのキッチン移動操作で高レベル指示の完遂率が有意に改善。**「何が失敗したか」を言語で返すことが効く、という直接の裏付け。**
- **Reflexion** (Shinn et al. 2023, NeurIPS): 失敗後に LLM 自身が言語的自己批評を生成し、エピソード記憶バッファに積んで次試行の文脈に前置する。重み更新なしの「**意味的な勾配信号**」。
- **Voyager** (Wang et al. 2023): **環境フィードバック + 実行エラー + 自己検証**の3点を含む反復プロンプトでプログラムを改善し、スキルライブラリに蓄積。
- **ReAct** (Yao et al. 2022): 推論と行為を交互に出し、行為の**観測結果を文脈へ戻す**ことで幻覚と誤差伝播を減らす。

粒度に関する設計知見は Inner Monologue が最も明快で、**二値の成功検出だけでも効くが、シーン記述があると長期タスクで効く**、というのが結論。IF-2 の「無音 / 記憶1行 / engaged突入」の3水準は、この「なし / 記述 / 介入」に**ほぼ1対1で対応する**。

**心理側: Zeigarnik効果は否定された。生き残ったのは Ovsiankina効果。**

2025年の系統的レビュー+メタ分析(*Humanities and Social Sciences Communications*)が59文献(Zeigarnik効果 38、Ovsiankina効果 20、両方 1)を統合した結果:

| 指標 | 値 |
|---|---|
| 中断課題/完了課題の再生比(Zeigarnik 原データ込み, N=38) | **0.99** |
| 同(原データ除外, N=37) | **0.99** |
| 効果量 Cohen's dz(N=8) | 0.15(小) |
| 全再生中に中断課題が占める割合 | **49.16%**(むしろ不利) |
| **Ovsiankina効果: 中断課題の再開率**(原データ込み N=21) | **67.00%** |
| 同(原データ除外, N=20) | **66.79%**(偶然の50%を明確に上回る) |

著者らの結論は「**未完了課題に記憶優位は見出せなかった**」「Zeigarnik効果は**普遍的妥当性を欠く**」、一方で「**Ovsiankina効果は一般的傾向を表す**」。調整変数として実験の雰囲気(リラックス条件で比 1.07 と最大)が挙がるが、達成動機の影響は小さい。

**計画を立てるだけで侵入思考は止まる。** Masicampo & Baumeister (2011, *JPSP*): 未達成目標は無関連課題中に侵入思考を生み、目標関連語のアクセシビリティを上げ、無関連なアナグラム課題の成績を落とす。しかし**実行意図(いつ・どこで・どうやるか)を形成するだけで**、実際の作業を一切していなくても侵入思考は急減する。

### 3-2. 本シムへの適用

監査 §2-C が記述した現状:
- 通知**あり**: 出店許可却下・破産直後出店・交際不成立・無許可摘発(→ `agent.remember` → 次プロンプト)
- 通知**なし**: 所持金不足出店・敷金不足転居・空き住戸なし・相手不在・**経路が張れない**(`len(path)<2: return` で無音)・改札規制
- day_plan の破綻(no_place/closed/unreachable/overflow)は**プロンプト文脈に一切入らない**。唯一の間接経路 `note_plan_exception → fire キュー前倒し → engaged REPLAN` は「**今すぐ考える**」だけを起こし、**何が失敗したかは伝わらない**

これを文献に照らすと:
- 現状の `plan_exception → REPLAN` は **Ovsiankina効果の実装そのもの**である(中断 → 再開/再計画)。メタ分析で生き残った唯一の効果を、本シムは既に持っている。
- 足りないのは **Inner Monologue の言う failure description** であり、現状は SayCan の限界(「価値関数が弾いたことは分かるが、なぜ弾かれたかが返らない」)と**まったく同じ位置**にいる。
- `envfeedback.py:505-514` の「新しい記憶文・欄・理由キーを足さない」という no-fingerprint 規約は、IF-2 と衝突するように見えるが、規約の本質は「**実験条件がプロンプトから漏れないこと**」であって「拒否理由を返さないこと」ではない。

### 3-3. 設計への具体的示唆

1. **心理側の正当化を差し替える。** 計画書・事前登録に「Zeigarnik効果」を根拠として書いてはならない(2025メタ分析で否定済み)。書くべきは **Ovsiankina効果(中断課題の再開率67%)** と **Masicampo & Baumeister 2011(計画形成が侵入思考を消す)**。これは単なる引用の差し替えではなく、**測るべき量が変わる**: 「拒否後に記憶が強くなるか」ではなく「**拒否後に再計画が起きるか・その再計画が成功すると侵入が止まるか**」。
2. **Masicampo からの直接の設計要求 — 「解決済み」の降格。** 失敗理由を記憶に1行残しっぱなしにすると、再計画に成功した後も文脈を汚し続ける。文献が言うのは「**計画が立った時点で侵入は止まる**」なので、**REPLAN が成功したら該当理由行を降格/失効させる**設計にする。これは記憶側に TTL か resolved フラグを1つ足すだけで足り、既定OFFトグル配下に収まる。この挙動は「失敗理由が延々と溜まって全員のプロンプトが失敗談で埋まる」という 25万体スケールでの現実的な劣化も同時に防ぐ。
3. **3水準はアブレーション軸として文献的に整合している。** `none / memo / engaged` を Inner Monologue の `no feedback / scene description / intervention` に対応づけて事前登録すれば、「フィードバック粒度がLLM社会シムの創発に効くか」という問いが**先行研究と直接比較可能な形**になる。単なる機能追加ではなく実験デザインとして書ける。
4. **no-fingerprint との両立は「有限語彙」で解く。** 危険は「拒否理由の文言が実験条件を露呈すること」なので、理由を **`KNOWN_ACTIONS` と同型の有限集合**に閉じる: `no_money / closed / no_room / unreachable / absent / overflow / …`。理由文字列は (行為種, 理由コード) の純関数であり、**config・実験条件・k・エージェント特性の関数ではない**ことをテストで機械固定する。これは SayCan の affordance が「有限スキル集合上の値関数」であることと同型であり、設計として文献的に自然。
   - 追加の固定テスト: **同一の拒否は全実験条件で同一バイト列**(第78の flat_traits / propagation_off で使った「呼び出しサイト増減ゼロ」型の検査と同流儀)。
5. **k非依存の維持。** engaged 突入は既存 fire キューの**前倒し**であって新規呼び出しではない、という現行構造を維持する。第78バッチが確立した「呼数±<10%をテストで固定する」流儀をそのまま適用し、IF-2 ON/OFF で LLM 呼数が変わらないことを機械固定する。
6. **監査 §5 の穴3件のうち2件が IF-2 の前提条件である。** (i) `contingency` がデッドデータ(day_plan が if_then を最大3個書かせるが消費コードが無い)、(ii) `_apply` に plan/recall/reflect 分岐が無く `{"action":"plan"}` が無音で消える。**(ii) は「拒否すら記録されない」= 観測の穴**であり、IF-2 の効果測定(拒否が何件起きたか)の分母を壊す。IF-2 より先に、あるいは同時に潰すべき。(i) は Masicampo の「実行意図」そのものなので、IF-2 の設計と自然に統合できる(拒否 → contingency の該当分岐を発火)。

---

## §4. 来歴・因果追跡(IF-1: 行為イベントへの llm_call_id 付与)

### 4-1. 指摘(文献が言っていること)

**W3C PROV-DM(Recommendation, 2013-04-30)。** 中核型3つ:
- **Entity**: 「固定された側面を持つ、物理的・デジタル的・概念的なもの」
- **Activity**: 「一定期間にわたって発生し、entity に対して/entity とともに作用するもの」
- **Agent**: 「activity の発生、entity の存在、あるいは他の agent の activity に対して何らかの責任を負うもの」

中核関係7つ: `wasGeneratedBy`(entity ← activity)/ `used`(activity → entity)/ **`wasInformedBy`(activity ← activity。両者の間で不特定の entity が交換された)**/ `wasDerivedFrom`(entity ← entity)/ `wasAttributedTo`(entity ← agent)/ `wasAssociatedWith`(activity ← agent)/ `actedOnBehalfOf`(agent ← agent)。

設計上重要な2点:
- **関係それ自体に識別子を付けられる**(関係インスタンスを他の来歴構成から参照できる)
- **bundle** = 「名前を持つ来歴記述の集合であり、それ自体が entity」。これにより「**来歴の来歴**」が表現できる
- 関係は属性を持てる(予約属性 `prov:role` / `prov:type` / `prov:location`)

**Event Sourcing (Fowler)。** 「アプリケーション状態の全変化をイベント列として捕捉する」。核心は **イベントログが system of record であり、現在状態はそこから導出可能なキャッシュに過ぎない**こと。過去の任意時点の状態を replay で再構成でき、誤ったイベントの遡及訂正もできる。**唯一の重大な注意点は外部系との相互作用**:

> イベントが外部システムへの更新メッセージを引き起こす場合、replay 時に問題が起きる。外部システムは本番処理と replay の区別がつかないからである。

解法は「replay 中は外部呼び出しを抑止するゲートウェイ」または「履歴的に一貫した応答を返すクエリログ」。

**シミュレーション分野の来歴。** Ruscheinski & Uhrmacher は「シミュレーション**モデルがどう生成されたか**」を PROV(有向非巡回グラフ)で記述することを提案し、SIMPROV(PLOS ONE 2025)へ発展させた。設計上の要点は **provenance capturer(各ソフトから収集)と provenance builder(一貫したグラフへ組み立て)の関心の分離**。

**PROV-AGENT (2025)。** LLM エージェントの**プロンプト・応答・ツール呼**を PROV の entity/activity へ分解し、識別子で下流影響へ接続する。エージェント実行をブラックボックスとして扱わず因果連鎖を保存する。用途は **誤り伝播の追跡・障害帰属・デバッグ**。

### 4-2. 本シムへの適用

本シムを PROV の語彙に写像すると、ほぼ完全に対応がつく:

| PROV | 本シム |
|---|---|
| Agent | `agent_id` |
| Activity(思考) | LLM 呼(`llm_call_id`、`l1b_llm.parquet` に purpose/step/cached) |
| Activity(行為) | L1 の行為イベント189種 |
| Entity | `provenance.Item` / truth_ledger の fact / flyer / venture |
| `wasDerivedFrom` | `Item.transmissions` の (from → to) |
| `wasInformedBy` | **これが欠けている** = 行為 activity ← 思考 activity |
| `wasGeneratedBy` | `state_update{name, old, new, cause}`(部分的) |
| `prov:role` | `l1b_llm` の `purpose` |
| bundle(来歴の来歴) | manifest(`metrics_spec_hash` / `state_hash` チェーン) |

つまり **IF-1 が足すのは PROV の `wasInformedBy` の辺1本**である。監査 §6 が言う「(step, agent_id) join に依存し、同step複数発火で曖昧」は、PROV 的には「**関係インスタンスに識別子が無い**」状態にあたる。

Event Sourcing の観点では、本シムは既に完全にこの型に入っている: L1 が system of record、checkpoint/resume が「resume==straight バイト一致」で固定、`llm_cache` replay は**ミス即例外**。Fowler の言う「replay 時に外部系を叩かないゲートウェイ」に厳密に対応するのが `llm_cache` replay である。

### 4-3. 設計への具体的示唆

1. **`llm_call_id` を単独値でなく `(llm_call_id, role)` の対にする。** 同step複数発火の曖昧さは PROV が「関係に識別子と `prov:role` を付けられる」ことで解いている問題そのもの。`role` は `l1b_llm` の `purpose` と同じ語彙(deliberate / plan / recall / reflect / null)を使い、**新語彙を作らない**。
2. **辺は1本ではなく3本揃えて初めて DAG が閉じる。** 「行為 ← 思考」(IF-1 本体)/「状態差分 ← 行為」(`state_update.cause` が既存)/「entity ← entity」(`Item.transmissions` が既存)。**IF-1 を入れると残り2本は既にあるので、その時点で『世界の変化 → 原因の行為 → その思考』が一本で辿れるようになる**。監査 §4 の「ない: 一本で辿るツール」は、IF-1 の後は**分析スクリプト1本の話に縮む**(コア改変不要)。
3. **payload には整数IDを入れる。** 25万体×10日で文字列 UUID を全行為イベントに載せるとサイズが爆発する。`l1b_llm` 側と join できる**単調増加の整数**にする(第76バッチの tracks_bin が「素int16では屋内max720で不可」と実測して設計変更した前例に倣い、**先に上限を実測してから型を決める**)。
4. **既定OFF + payload に鍵を生やさない。** OFF 時は golden L1 がバイト一致(監査 §6 の「payload 差分が出るため既定OFFトグルで」の判断は正しい)。第75の dormant キー方式(OFF ではキー自体が生えない)を踏襲。
5. **replay 契約を明文化する。** Fowler の警告どおり、ログを増やしても **replay 時に新たな外部副作用が起きないこと**を docstring とテストで固定する。本シムでは `llm_cache` ミス即例外がこの保証であり、IF-1 はログの**読み取り側**にしか触らないので契約は変わらない — その旨を明記しておくと後続バッチの事故を防げる。
6. **capturer / builder の分離(SIMPROV)。** 収集(scheduler が payload に ID を載せる)と組み立て(analyze 側で DAG を構成)を混ぜない。シム側には**グラフを持たせない**。これが「観測がシムを変えない」の実装形でもある。
7. **PROV-AGENT が示す用途をそのまま検収項目にできる。** 誤り伝播・障害帰属・デバッグ。本シムでは「ある創発現象(規範成立・新語定着)の起点となった LLM 呼を特定できるか」が対応物であり、**IF-1 の受入テストは『既知の1件を人工的に仕込み、逆引きで一意に到達できること』**という形に書ける。

---

## §5. 経済会計の保存則(IF-5: revenue_est を客の spend 由来へ)

### 5-1. 指摘(文献が言っていること)

**SFC(stock-flow consistent)の中核。** Godley & Lavoie (2007, *Monetary Economics*) が定式化し、Caiani, Godin, Caverzasi, Gallegati, Kinsella & Stiglitz (2016, *JEDC* 69:375-408) が ABM へ持ち込んだ。Caiani et al. の本文から直接:

> Stock Flow Consistency implies, as explained in Godley and Lavoie (2007), that **the rows and columns of the Transaction Flow Matrix sum to 0**.

そして最も実務的に価値があるのは §5.2 Validation の**2つの検査法**である(以下は本文の要約):

1. **取引フロー行列 + 完全統合行列を導出し、Copeland の四重記入原理への適合を確認する。** 要求は「**シミュレーションのあらゆる時点で、行列のすべての行と列がゼロに合計されること**」。これは「ある主体の流出は必ず別の主体の流入である」「ある主体の金融資産は必ず別の主体の負債である」という基本事実を反映する。副次的な利点として、経済内のフロー間の相互依存が明確になり、部門間フローと実物・金融ストック蓄積の推移が一望できる。
2. **経済全体のバランスシートによる検査。** 「**経済内の全主体(政府・中央銀行を含む)の純資産の合計が、実物資産の価値と毎シミュレーションラウンドで正確に等しいこと**」を確認する。理由は単純で、**実物ストックだけが負債の相手方を持たない資産**だからである。金融ストックはすべて誰かの資産かつ誰かの負債なので、合計すると相殺される。

そして著者らは、この検査が必要な理由を率直に述べている:

> 初期ストック・フローの適切な較正と、微視的主体間の交換から生じる会計記録の正しい記述があれば、理論的には集計レベルの会計整合も保証されるはずである。**しかし実際には、モデル実装の途中で漏れ(leakage)が生じることは珍しくない。** これは特に、多様な主体を抱え、複雑なイベント時系列と多種の異質な実物・金融ストックを持つ大規模で複雑な AB モデルで起きやすい。

Caiani et al. は「これらの会計条件がシミュレーション全期間で満たされることを確認した**上で**、経験的妥当化(定型化された事実との突合)に進む」という順序を明示している。

**LLM 経済シムの現状。** EconAgent (Yang et al. 2023, arXiv:2310.10436) は LLM 家計に労働供給と消費性向を決めさせ、ルールベース環境が中央政府(徴税)と中央銀行(金利)を兼ねる。インフレ・失業率などの古典的マクロ現象を従来のルールベース/学習ベースより妥当に再現した。**ただし著者自身が限界として、企業(価格設定・雇用)が未実装であることを挙げている。** SFC 的な会計整合の検査については記述がない。

### 5-2. 本シムへの適用

監査 §3 の所見: `revenue_est = 日給 × margin`(scheduler.py:450-452)で**客の spend と非接続**。会計保存が成り立つのは venture と B2B のみ。

Caiani et al. の言葉を借りれば、これは典型的な **leakage** である。「客が払った金」と「店が受け取った金」が別の式で決まっているので、取引フロー行列の当該行はゼロにならない。**そして著者らが「大規模で複雑な AB モデルでは実装中の漏れは珍しくない」と明言している以上、これは本シム固有の不手際ではなく、この分野で標準的に検査される既知の失敗モードである。**

同時に、LLM 経済シムの先行研究(EconAgent)が企業側を持たず会計検査にも触れていない以上、**本シムが venture/B2B で保存を成立させている点は既に先行**しており、org へ拡張すれば「LLM 社会シムで SFC 会計整合を機械検査した初めての例」を主張しうる。

### 5-3. 設計への具体的示唆

1. **「接続」より先に「検査」を入れる。これが最大の示唆。** Caiani et al. の順序(会計整合の確認 → 経験的妥当化)に従い、**IF-5 の第1段階は revenue_est の書き換えではなく、漏れ量を測る検査を既定OFFで入れること**。理由:
   - 検査は**純粋な観測**なので R1 適合が自明(シム不変・golden バイト一致・乱数0・LLM呼0)
   - 現行の漏れの**大きさが数値で分かってから**接続方式を決められる(漏れが小さければ接続の優先度は下がる)
   - 接続を先にやると「直したつもりで別の漏れが増えた」を検知できない
2. **テストの形は文献どおり2本にする。**
   - **(a) 取引フロー行列の行・列がゼロ**(全step。部門別集計で可)
   - **(b) 全主体の純資産合計 = 実物資産の価値**(全step)。本シムの実物資産 = 商品在庫(`_goods_stock`)+ 卸在庫 + venture 設備。金融資産 = 所持金・預金・貸出。
   検査 (b) のほうが実装が軽く(合計2本の比較)、しかも漏れがあれば必ず検出できるので、**(b) を先に、(a) を後に**入れるのが実務的。
3. **25万体スケールでは行列を部門別に持つ。** エージェント別の N×N 行列は 25万で不可能。Caiani et al. の行列も**部門別**(家計・消費財企業・資本財企業・銀行・政府・中央銀行)である。本シムでは (家計 / 店・org / venture / 卸 / 政府 / 外部) 程度の 6〜8 部門で足りる。計算量は O(部門²) = 定数。
4. **許容誤差をゼロにしない設計判断を先に決めておく。** 浮動小数の丸めがあるため厳密ゼロは成立しない。第76バッチの量子化往復誤差(IEEE754 ノイズ 2.3e-13)と同じ問題であり、**絶対誤差ではなく相対誤差(総フローに対する比)で閾値を置き、閾値を conf 化してテストで固定する**のが本シムの既存流儀と整合する。
5. **`by_org` トグル配下・k非依存。** LLM 呼は 1本も増えない(会計は完全に決定論)。既定 OFF では新しい dict も列も生やさない。
6. **接続時の設計(第2段階)。** revenue_est を廃止するのではなく、**客の spend を積む実測 revenue を並行して持ち、両者の差を L2 に出す**段階を挟む。差がゼロに収束したら revenue_est を実測に置き換える。これは第78の state_hash が「片側検定と明記し、厳密判定は L1 バイト比較のまま」とした慎重さと同型のやり方。

---

## §6. IF-1〜IF-5 への反映表

| # | 内容 | 文献裏付け | 主要根拠 | **設計への変更** |
|---|---|---|---|---|
| **IF-1** | 行為イベントへの `llm_call_id` 付与 | **強** | W3C PROV-DM(`wasInformedBy` / 関係の識別子 / `prov:role` / bundle)、Fowler Event Sourcing、PROV-AGENT 2025、SIMPROV | **あり(4点)**: ① 単独値でなく **(llm_call_id, role)** の対にして同step複数発火の曖昧さを構造的に解く ② payload は**整数ID**(先に上限を実測してから型決定) ③ capturer/builder 分離 = シム側にグラフを持たせない ④ replay 契約不変を docstring とテストで明文化。**「3辺目を足すと DAG が閉じる」という位置づけを明記**(残り2辺は既存) |
| **IF-2** | 拒否通知の段階conf化 | **工学=強 / 心理=要修正** | Inner Monologue(feedback 3種)、SayCan(affordance と「失敗理由が返らない」限界)、Reflexion、Voyager、ReAct / **Zeigarnik-Ovsiankina メタ分析 2025**、Masicampo & Baumeister 2011 | **あり(重要・5点)**: ① **心理側の根拠を Zeigarnik効果から Ovsiankina効果+Masicampo に差し替える**(Zeigarnik は 2025 メタ分析で比0.99・普遍的妥当性を欠くと結論。**事前登録・計画書に書いてはならない**) ② 測る量を「記憶が強くなるか」→「**再計画が起きるか**」へ ③ **再計画成功時に理由行を降格/失効**(Masicampo の「計画で侵入が止まる」の実装。25万体でのプロンプト汚染も同時に防ぐ) ④ 理由を**有限語彙**に閉じ「同一拒否は全条件で同一バイト列」をテスト固定(no-fingerprint 両立) ⑤ 3水準を Inner Monologue の3種に対応づけてアブレーション軸として事前登録。**前提**: 監査 §5 の `_apply` plan分岐欠落は IF-2 の分母を壊すので先に/同時に潰す |
| **IF-3** | 情報オブジェクトの一般化 | **強**(ただし**向きが逆**) | Daley-Kendall 1964 / Maki-Thompson 1973、Kempe et al. 2003(IC/LT)、**Park et al. 2023(事後インタビュー測定・幻覚1.3%)**、OASIS 2024(post ID / scale-depth-breadth)、arXiv 2605.17353(構造化 claim だが LLM 呼を使う) | **あり(向きの転換+4点)**: ① **「先行研究への追随」ではなく「既に先行している優位の完成」**として設計・記述する(GA は ID を持たず事後インタビューでしか測れない。本シムは走行中に誤差ゼロで測れる) ② `provenance.Item` に**新スキーマを足さず** `kind="rumor"` を実体化するだけにする(分析19本が無改変で効く) ③ **停止規則(stifler)を conf 化**(現行は噂が止まる理由が無い)+ `once_per_pair`(IC互換)で DK/MT 理論値(最終ignorant≈20%・ピーク 1−ln2≈0.307)と比較可能に ④ 抽出は **(a) 同一呼び出しの構造化フィールド > (c) 行為API引数 > (b) 部分文字列** の優先順(追加LLM呼ゼロを維持) ⑤ 測定指標を OASIS の **scale / depth / max_breadth** に揃える。25万体では `transmissions` の正典を L1 イベント側に置く |
| **IF-4** | 痕跡=場所イベント履歴の汎用機構 | **強** | Grassé 1959、**Heylighen 2011/2016**(components / 5分類軸 / 減衰の機能的必然性)、Parunak(集約・蒸発・拡散 + flavor)、Helbing et al. 1997(active walker / desire path)、Ledger-State Stigmergy 2026(永続媒体の落とし穴) | **あり(6点)**: ① **propagation(拡散)を入れない**(Parunak の propagation factor=0 として文献的に正当。golden 破壊と O(node×kind) を回避)。**集約と蒸発の2演算のみ** ② **kind ごとに独立の場(flavor)** — 意味の違う痕跡を1スカラーに混ぜない ③ **TTL を単一既定にせず3階層**(transient / daily=144step / persistent)= Heylighen の「陳腐化速度に合わせる」の直接適用 ④ 容量・押し出し・expire は flyer の既存形式をそのまま継承(新イベント種を作らない) ⑤ **narrowcast(同一node)既定**(broadcast は fingerprint 面を拡大) ⑥ **痕跡の強化は「行為」でのみ起こし「観測」では起こさない**をテスト固定(= R1「観測がシムを変えない」と Heylighen の定義の両方を満たす) |
| **IF-5** | 経済会計の接続 | **強** | **Caiani et al. 2016(検査法2本を明示)**、Godley & Lavoie 2007、EconAgent 2023(LLM経済シムは企業未実装・会計検査なし) | **あり(順序の転換+4点)**: ① **第1段階を「接続」でなく「検査」にする**(Caiani の順序=会計整合を確認してから妥当化へ。検査は純粋観測なので R1 適合が自明で、漏れ量が分かってから接続方式を決められる) ② テストは文献どおり2本 = **行と列が全step ゼロ** / **全主体の純資産合計 = 実物資産**。実装の軽い後者を先に ③ 行列は**部門別 6〜8 個**(25万でエージェント別は不可。Caiani も部門別) ④ 許容誤差は相対誤差 + conf 化(厳密ゼロは浮動小数で不成立) ⑤ 接続は revenue_est を即置換せず**実測 revenue を並走させて差を L2 に出す**段階を挟む |

**横断の所見(採否判断の材料)**

- **IF-4 と IF-5 は「文献の設計解をほぼそのまま移植できる」**ため、設計コストが事前の想定より小さい。特に IF-5 は Caiani et al. の検査2本が**そのまま pytest の関数2本に落ちる**。
- **IF-2 は文献リサーチによって前提が1つ壊れた。** Zeigarnik効果を根拠にした記述が計画書・事前登録ドラフトに既に入っているなら、**IF-2 の実装可否とは独立に修正が必要**。
- **IF-3 は主張の格が上がる。** 「情報オブジェクトを持てる」ことは Generative Agents に対する明確な方法論的優位であり、事前登録の売りに使える。
- **IF-1 は他の3件の測定基盤になる。** IF-2 の「拒否 → 再計画」の因果、IF-3 の「発話 → 情報オブジェクト」の因果、IF-4 の「痕跡観測 → 行為」の因果は、いずれも `wasInformedBy` の辺があって初めて一意に辿れる。**順序を付けるなら IF-1 が先。**

---

## §7. リンク集(すべて 2026-08-05 アクセス)

### §1 スティグマジー
- Grassé, P.-P. (1959) "La reconstruction du nid et les coordinations interindividuelles chez *Bellicositermes natalensis* et *Cubitermes* sp. La théorie de la stigmergie", *Insectes Sociaux* 6(1):41-80 — https://link.springer.com/article/10.1007/BF02223791 (書誌のみ確認・本文未取得)
- Heylighen, F. (2011) "Stigmergy as a generic mechanism for coordination: definition, varieties and aspects", ECCO Working Paper 2011-12 — https://pespmc1.vub.ac.be/Papers/Stigmergy-WorkingPaper.pdf (**全23頁を本文抽出して精読**)
- Heylighen, F. (2016) "Stigmergy as a universal coordination mechanism I: Definition and components", *Cognitive Systems Research* 38:4-13 — https://dl.acm.org/doi/10.1016/j.cogsys.2015.12.002 / 研究ポータル: https://researchportal.vub.be/en/publications/stigmergy-as-a-universal-coordination-mechanism-i-definition-and-
- Heylighen, F. (2016) "…II: Varieties and evolution", *Cognitive Systems Research* 38:50-59
- Parunak, H. V. D. et al. "Digital Pheromone Mechanisms for Coordination of Unmanned Vehicles" — http://biomimetic.pbworks.com/f/Digital%20pheromone%20mechanisms%20for%20coordinationParunaK.pdf / AIAA-2002-3446: https://www.abcresearch.org/abc/papers/AIAA-2002-3446.pdf
- Helbing, D., Keltsch, J. & Molnár, P. (1997) "Modelling the evolution of human trail systems", *Nature* 388:47-50 — https://www.nature.com/articles/40353 / arXiv: https://arxiv.org/pdf/cond-mat/9805158
- Helbing, D., Schweitzer, F., Keltsch, J. & Molnár, P. (1997) "Active walker model for the formation of human and animal trail systems", *Phys. Rev. E* 56:2527 — https://link.aps.org/doi/10.1103/PhysRevE.56.2527
- Ma, L., Brandt, S. A., Seipel, S. & Ma, D. (2024) "Simple agents – complex emergent path systems: Agent-based modelling of pedestrian movement", *EPB: Urban Analytics and City Science* — https://journals.sagepub.com/doi/full/10.1177/23998083231184884
- "Ledger-State Stigmergy: A Formal Framework for Indirect Coordination Grounded in Distributed Ledger State" (2026) — https://arxiv.org/html/2604.03997

### §2 噂・情報伝播
- Daley, D. J. & Kendall, D. G. (1964) "Epidemics and rumours", *Nature* 204:1118 / (1965) "Stochastic rumours", *J. Inst. Maths Applics* 1:42-55(書誌のみ)
- Maki, D. P. & Thompson, M. (1973) *Mathematical Models and Applications*(書誌のみ)
- 古典結果の確認に用いた近年の論文: "The Maki-Thompson model with random awareness" — https://arxiv.org/pdf/2508.07099 / "Fundamentals of spreading processes in single and multilayer complex networks" — https://arxiv.org/pdf/1804.08777
- Kempe, D., Kleinberg, J. & Tardos, É. (2003) "Maximizing the Spread of Influence through a Social Network", KDD'03 — https://www.cs.cornell.edu/home/kleinber/kdd03-inf.pdf
- Park, J. S. et al. (2023) "Generative Agents: Interactive Simulacra of Human Behavior", UIST'23 — https://arxiv.org/abs/2304.03442 / ar5iv 全文(**該当節を確認**): https://ar5iv.labs.arxiv.org/html/2304.03442 / ACM: https://dl.acm.org/doi/10.1145/3586183.3606763
- Yang, Z. et al. (2024) "OASIS: Open Agent Social Interaction Simulations with One Million Agents" — https://arxiv.org/abs/2411.11581 / HTML 全文(**該当節を確認**): https://arxiv.org/html/2411.11581v1
- "You Can't Fool Us: Understanding the Resilience of LLM-driven Agent Communities to Misinformation" (2026) — https://arxiv.org/html/2605.17353

### §3 拒否・失敗フィードバック
- Ahn, M. et al. (2022) "Do As I Can, Not As I Say: Grounding Language in Robotic Affordances" (SayCan) — https://arxiv.org/abs/2204.01691 / プロジェクト: https://say-can.github.io/
- Huang, W. et al. (2022) "Inner Monologue: Embodied Reasoning through Planning with Language Models" — https://arxiv.org/abs/2207.05608 / プロジェクト: https://innermonologue.github.io/
- Shinn, N. et al. (2023) "Reflexion: Language Agents with Verbal Reinforcement Learning", NeurIPS 2023 — https://proceedings.neurips.cc/paper_files/paper/2023/file/1b44b878bb782e6954cd888628510e90-Paper-Conference.pdf / arXiv: https://arxiv.org/abs/2303.11366 / 実装: https://github.com/noahshinn/reflexion
- Wang, G. et al. (2023) "Voyager: An Open-Ended Embodied Agent with Large Language Models" — https://arxiv.org/abs/2305.16291 / https://huggingface.co/papers/2305.16291
- Yao, S. et al. (2022) "ReAct: Synergizing Reasoning and Acting in Language Models" — https://arxiv.org/abs/2210.03629
- **Zeigarnik-Ovsiankina メタ分析(2025)**: "Interruption, recall and resumption: a meta-analysis of the Zeigarnik and Ovsiankina effects", *Humanities and Social Sciences Communications* — https://www.nature.com/articles/s41599-025-05000-w(**全文を確認**)
- Masicampo, E. J. & Baumeister, R. F. (2011) "Consider It Done! Plan Making Can Eliminate the Cognitive Effects of Unfulfilled Goals", *JPSP* — https://users.wfu.edu/masicaej/MasicampoBaumeister2011JPSP.pdf
- Masicampo & Baumeister (2011) "Unfulfilled goals interfere with tasks that require executive functions", *JESP* — http://users.wfu.edu/masicaej/MasicampoBaumeister2011JESP.pdf
- Seifert, C. M. & Patalano, A. L. (1991) "A Re-examination of the Zeigarnik Effect" — https://apatalano.faculty.wesleyan.edu/files/2019/07/Seifert_Patalano_1991.pdf

### §4 来歴・因果追跡
- W3C (2013) "PROV-DM: The PROV Data Model", W3C Recommendation 30 April 2013 — https://www.w3.org/TR/prov-dm/(**全文を確認**)
- Fowler, M. "Event Sourcing" — https://martinfowler.com/eaaDev/EventSourcing.html(**全文を確認**)
- Ruscheinski, A. & Uhrmacher, A. M. et al. "Relating simulation studies by provenance—Developing a family of Wnt signaling models", *PLOS Computational Biology* — https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1009227
- "SIMPROV: Provenance capturing for simulation studies", *PLOS ONE* (2025) — https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0327607
- "Automatic Reuse, Adaption, and Execution of Simulation Experiments via Provenance Patterns" — https://arxiv.org/pdf/2109.06776
- "PROV-AGENT: Unified Provenance for Tracking AI Agent Interactions in Agentic Workflows" (2025) — https://arxiv.org/pdf/2508.02866

### §5 経済会計
- Caiani, A., Godin, A., Caverzasi, E., Gallegati, M., Kinsella, S. & Stiglitz, J. E. (2016) "Agent based-stock flow consistent macroeconomics: Towards a benchmark model", *JEDC* 69:375-408 — https://business.columbia.edu/sites/default/files-efs/imce-uploads/Joseph_Stiglitz/Agent%20based-stock%20flow.pdf (**全34頁を本文抽出して §5.2 Validation を精読**) / ScienceDirect: https://www.sciencedirect.com/science/article/abs/pii/S0165188915301020 / SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2664125
- Godley, W. & Lavoie, M. (2007) *Monetary Economics: An Integrated Approach to Credit, Money, Income, Production and Wealth*(書誌のみ)
- Yang, N. et al. (2023) "EconAgent: Large Language Model-Empowered Agents for Simulating Macroeconomic Activities" — https://arxiv.org/abs/2310.10436 / HTML: https://arxiv.org/html/2310.10436v3

---

*リサーチ実施: 2026-08-05。実装・コミットは行っていない(ユーザー指示)。書き込みは本ファイル1件のみ。*
