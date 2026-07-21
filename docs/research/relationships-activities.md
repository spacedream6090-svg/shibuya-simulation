# 家族・友人関係の再現と「関係性に基づく共同行動」— 実査・リサーチ・実装案

**日付**: 2026-07-21 / **担当**: リサーチ(Opus)、検収: Fable(親)
**関連**: `src/society/relations.py`, `src/society/household.py`, `src/society/schedule.py`,
`src/society/tools.py`(host_event), `src/society/cognition/plan_schema.py`,
docs/research/daily-plan-framework.md, docs/research/interstitial-life.md, docs/research/persona-pool-1m.md

ユーザー要望(2026-07-21): 「エージェント同士の家族や友人の関係を再現する部分も実装したい。まずは
関係性とその行動について調べて、エージェントがする行動の候補の実装案を出してほしい。例: 友達と映画・
カラオケなどの遊び、ビジネスでご飯を一緒に行くなど」。
恒久指針(natural-coinage / realism-first / nature-like-systems): **例は一部にすぎない**。関係タイプ×
共同行動の空間を統計で網羅してから重要なものを選定する。既定 OFF・呼数 k 非依存・新 stream のみ・
バイト一致を守る(R1 契約)。

> **本書は調査+実装案のみ。コード/conf は一切変更していない。実装はユーザー承認後。**

---

## 0. 要旨(3行)

1. **土台はかなり揃っている**: 関係の質(relations 台帳=知人/友人/親友)・世帯/家族/恋愛(household)・
   会話からの予定自動記入(schedule 帳)・イベント誘い→参加の**関係駆動ランデブー**(host_event の
   attend_relation_bonus)・計画の**同伴者フィールド `with`** ・待ち合わせ what-type(`meetup`)—
   いずれも実装済み。本番(production/daily)で relations/household/schedule は **ON**。
2. **足りないのは3点**: (A) プールに**家族・友人の事前構造が無い**(世帯は起動時に id 順で束ねるだけ=
   年齢/続柄が非整合、友人は同建物の「顔なじみ」のみ=homophily 無し)。(B) 計画の同伴者 `with` が
   **どの共同行動機構にも接続されていない**(誘う→合流の駆動に使われていない)。(C) **類型化された
   共同行動カタログ**(映画/カラオケ/会食…)と参加率較正が無い。
3. **実装は既存機構の再利用でほぼ賄える**: 先行例(Generative Agents)の知見どおり「共同行動=同一
   (場所,時刻)を各自が独立に選ぶ+合流は決定論」。household の `date_dest`(ペア決定論行き先)と
   host_event の `_route_to`(会場へ経路)が既にその形。これを**任意の関係ペア/グループへ一般化**する。

---

## 1. 現状実査(file:line)

### 1.1 関係の質 — `src/society/relations.py`(G2・本番 ON)

- **tier 台帳**: closeness(交流の符号付き累積)から質的段階を純関数導出。`tier_of`(relations.py:77):
  0=見知らぬ / 1=知人(closeness≥2.0)/ 2=友人(≥5.0)/ 3=親友(≥12.0)。`TIER_LABELS`(:31)。
- **更新**: `note_contact`(:105)が交流1件ごとに closeness を ±(pos_weight=1.0 / neg_weight=2.0)動かし、
  tier 変化で `relation_tier` / `relation_break` を記録。決定論・乱数ゼロ・LLM 非増。
- **断絶/風化**: `decay_day`(:161)最終接触が前日以前の相手を日次減衰(長期不在で友人→知人へ後退)。
- **評判**: `gain_reputation`/`reputation_decay`(:126,145)語の採用・被傾聴で伝播する社会的地位。
- **プロンプト**: `social_lines`(:188)同席者ごとに「○○とは友人」、faction ON なら「(同じ仲間)」。
- 既定 OFF は record_contact に closeness_delta を渡さず=台帳・イベント列バイト一致。**production.yaml:142 /
  daily.yaml:136 で `relations.enabled: true`**。

### 1.2 世帯・家族・恋愛 — `src/society/household.py`(H2・本番 ON)

- **世帯グループ化** `build_households`(household.py:94): 起動時1回。**居住者のみ**(visitor 除外・:105)を
  **id 昇順で並べ**、新 stream `"household"` からサイズを引いて先頭から詰める。size_weights の既定
  `[0.35,0.30,0.22,0.13]`(:38)=単身35/2人30/3人22/4人13%。2人以上に `household_id`/`household_kind`
  (family or roommate、family_ratio=0.7)/`housemates`/共有 `home_building` を付す。
  - ⚠ **続柄・年齢の整合は無い**: 束ねるのは id が隣接する居住者で、夫婦/親子/年齢差を考慮しない。
    「4人世帯」でも実態は無関係な4人の同居に近い(家族の意味論は薄い)。
- **恋愛形成** `form_partners`(:228): 日次。relations の相互 closeness が `partner_closeness`(既定15.0)以上の
  2者を決定論でパートナーに。`bond`/`unbond`(:190,202)で partner_id 相互設定+`partner_formed`/`life_event`。
- **デート** `date_dest`(:151): 自由時間に専用 stream `"date"` で date_bias 抽選 → **(ペア,当日) から純関数で
  同一ノードを導出**=両者が同じ場所へ=合流(co-location)。★これが「関係駆動の決定論ランデブー」の既存実例。
- **同席文脈** `context_line`(:129): 同席する同居者=「同居する家族の○○」、恋人=「恋人の○○」。
- **production.yaml:198 / daily.yaml:183 で `household.enabled: true`**(恋愛は relations.enabled=true 前提)。

### 1.3 初期関係ネットワーク — `simulation.py`(顔なじみ + icebreak + follow)

- **顔なじみ**(simulation.py:594-607): 同じ `home_building` / 同じ `work_building` の居住者を、代表の建物ごとに
  「1人あたり最大3人」`record_contact(…, "顔なじみ")` で相互に初期関係へ。
  - ⚠ **地理的共在のみ**が初期関係の源泉。homophily(年齢/職業の類似)・学校/サークル/趣味の紐帯は無い。
    友人は「同じ建物に住む/働く人」に限られる。
- **icebreak**(`_load_icebreak` simulation.py:735, `build_icebreak.py` 生成物): 実験前の初対面会話を全 k 条件で
  同一ファイル注入(交絡排除)。record_contact で初期の知り合いを作る。
- **SNS follow**(`net.init_follows` :591): follow_k=6 のフォローグラフ。
- **プールに家族・友人フィールドは無い**(§1.6)。世帯は**起動時に生成**、友人は**顔なじみのみ**。

### 1.4 予定・スケジュール帳 — `src/society/schedule.py`(本番 ON)

- **会話からの予定抽出** `extract`(schedule.py:204): 発話/DM の**既生成テキスト**を正規表現で解析し
  {day, when, what, place, with} を決定論抽出(**追加 LLM 呼ゼロ**)。what ラベル(:38-45)=
  `会う/食事/買い物/勉強会/遊び/イベント`。日付語(明日/週末/来週/○曜)・時刻・場所ヒントを解決。
- **記入** `_record_appointments`(scheduler.py:1089): 話者と相手双方の帳簿へ `with`=相手 id つきで記録し
  `appointment` イベント(:1117)。プロンプトに `next_line`/`today_line` を1行注入。
- ⚠ **予定を「実際に守る」機構が弱い**: `appointment_kept`(schema.py:110)は「予定時刻に該当場所に居た」を
  **受動観測**するだけで、予定へ向かって移動させる能動ルーティングは無い(予定は行き先バイアスに未接続)。
- **production.yaml:100 / daily.yaml:103 で `schedule.enabled: true`**。

### 1.5 イベント誘い→参加(既存の関係駆動ランデブー) — `src/society/tools.py`

- **開催** `_host_event`(tools.py:631): LLM 行動 `host_event` が (node, start_step) にイベントを作り、
  SNS 投稿 + **関係台帳上位5人へ自動 DM 告知**(`_announce_dm` :669)。DM 受領で `invite`(:604)が
  `_known_events` に登録。
- **参加抽選** `_events_start`(:864): 開始時、known な各 agent が
  `p = attend_base(0.25) + attend_relation_bonus(0.35 if 主催者が既知の相手) + 主催者status`(:881)で抽選。
  通れば `_route_to`(:940)で会場ノードへ経路 → 合流 → `event_attend`(:968)。屋内者は退館後 `event_retry`
  stream で再試行(:907)。
- ★ **これが現状唯一の「関係の強さで参加確率が上がる共同行動」**。ただし (i) 行動が**無類型**(映画/カラオケ等の
  区別なし、ただの "event")、(ii) **主催者→招待者の一方向**(友人同士の相互の誘いではない)、(iii) 起点に
  **LLM の host_event 行動が要る**(内発的に湧かない)。

### 1.6 プール(約100万人)— `scripts/build_persona_pool.py`(737MB on disk)

- L1 住民/L2 域内従業者/L3 定期来街/L4 非定期来街/L5 役割、全**決定論**生成。
- **家族・友人の事前構造は無い**(spouse/child/family/household/friend フィールドは grep でゼロ)。世帯は
  実行時に household.py が生成、友人は顔なじみのみ。
- L4 来街者に `party_size` 1-5(:488「同行人数」)と `visit_purpose`(:101-103: 観光0.24/買い物0.26/飲食0.18/
  エンタメ0.12/ビジネス来訪0.10/**友人と会う0.07**/通院0.03)がある。
  - ⚠ **`party_size` は sim 内で未使用**(grep ゼロ)=来街グループが**同席する同伴者として実体化されていない**。
    visit_purpose も現状はフレーバー(「友人と会う」で来ても実際に友人と合流しない)。

### 1.7 計画の同伴者フィールド + 待ち合わせ what-type(接続先)

- **`with`(同伴者)フィールド**: `plan_schema.py:11,71,150` で計画スキーマに存在し `_as_list` で文字列
  リストに正規化。だが **`planning.framework.enabled: false`(config.yaml:463)で既定 OFF**、かつ ON でも
  `with` は**どの共同行動機構にも接続されていない**(co-location/rendezvous への配線は grep でゼロ)。
  = 現状 `with` は**保持されるだけの休眠フィールド**。
- **`meetup` what-type**: `routine.py:412-415` に `_PLAN_CAT = {… "meetup":"landmark", "visit":"landmark"}`。
  コメント「meetup = 待ち合わせ(像・名所 等 landmark)。会えたかは既存の対面機構が拾う」。
  - ⚠ ただし各自が**独立に** landmark を選ぶため、place を明示しない限り**同じ landmark に集まる保証は無い**。
    共同行動には「同伴者が同一(場所,時刻)を選ぶ」協調が要る(§4)。

### 1.8 満足・ドライブへの接続点(共同行動の効果の受け皿=既存)

- **drive** `drive.py`: `"company"`(人と一緒にいる=社交圧 +0.10)・`"dm_received"`(+0.35)。company は馴化対象。
- **SDT needs** `needs.py:38-43`: `company` → relatedness +0.7 / autonomy −0.4、`dm_received` relatedness +0.8、
  `addressed` relatedness 1.0。
- **価値充足** `values.py:63-65`: 「交流」タグ(kw: 友達と/友人と/飲み会/遊びに/会いに/集まり)→ social 0.6。
  = 共同行動は既存の relatedness(SDT)・social 価値・company ドライブに自然に流し込める(新 state 不要)。

**§1 結論**: 関係の器(tier/世帯/恋愛/予定/評判)と**関係駆動ランデブーの原型2つ**(household.date_dest の
決定論合流、host_event の attend_relation_bonus 経路)は既にある。欠けているのは
**(A) 現実的な家族・友人の初期構造**、**(B) 同伴者フィールドを合流へ配線する一般機構**、
**(C) 類型化された共同行動カタログと参加率較正**。この3つが本タスクの実装対象。

---

## 2. リサーチ: 関係の構造と共同行動の統計(出典 URL つき)

出典の格付け: **[GOV]** 政府基幹統計 / **[GOV-SURVEY]** 省庁委託世論調査 / **[PRIVATE]** 民間(方法論明示・
大標本)/ **[PRIVATE-SMALL]** 民間(小標本・自己選択=指標として扱う)/ **[THEORY]** 学術定説。

### 2.1 渋谷の世帯構造 — 単身率が全国最高水準(重要な現実制約)[GOV]

令和2年国勢調査(2020)より。
- **渋谷区 単独世帯率 = 64.5%**(96,707 / 149,856 世帯)。2人以上=35.5%。23区で新宿67.8%に次ぐ**2位**。
  23区平均 ≈ 53.5%。出典: https://jp.gdfreak.com/public/detail/jp010050000001013113/13 ,
  https://www.clearthlife.com/feature/bizinfo/6860 , 渋谷区一次: https://www.city.shibuya.tokyo.jp/kusei/kuni_kikamtokei/kokusei_cyosa/01kokusei_r2.html
- **渋谷区の単身は「若年・就業世代」に偏る**: 高齢単身8.2% + 高齢夫婦4.7% = 13.0%(全国23.8%より−10.8pt)。
- **渋谷区 平均世帯人員 ≈ 1.6 人**(常住243,883 ÷ 約149,856世帯)。東京都1.92(全都道府県最低・初の2人割れ)、
  全国2.21。東京都: https://www.spt.metro.tokyo.lg.jp/tosei/hodohappyo/press/2022/01/20/07.html
- **全国 世帯人数分布(2020)**: 1人38.0% / 2人28.1% / 3人16.6% / 4人11.9% / 5人+5.5%。
  出典: https://www.stat.go.jp/data/kokusei/2020/kekka.html
- ⚠ **現状の household 既定 size_weights `[0.35,0.30,0.22,0.13]`(単身35%)は渋谷の実態64.5%と乖離**。
  居住者の世帯較正は渋谷区値へ寄せるべき(§4-A)。

### 2.2 昼夜間人口比 — 街にいる大多数は住人でない(来街者の同伴制約)[GOV]

- **昼間人口 551,344 / 夜間(常住)243,883 / 昼夜間人口比率 226.1**(2020)。日中は常住の**約2.26倍**、
  約30万人超が流入。出典: https://www.e-stat.go.jp/dbview?sid=0004003060 ,
  https://www.juken-net.com/main/ranking/chuyajinkou_rank/
- ⚠ **含意**: 街にいる大多数は来街者=**家族・自宅は圏外**。来街者の同伴者は「一緒に来た連れ(party)」に限られ、
  世帯・友人グラフの主対象は**居住者**(現状 household も居住者限定=整合)。来街者は §4-A3 の party 実体化で扱う。

### 2.3 友人ネットワークの構造 — 層・homophily・弱い紐帯 [THEORY/GOV]

- **Dunbarの入れ子層**[THEORY]: 親密 ~5(支援クリーク)→ 15(親しい友人)→ 50 → 150(安定関係の上限)→
  500(知人)。各層は内側の約3倍。強い紐帯=内側5-15、弱い紐帯=外側50-150+。
  出典: Mac Carron/Kaski/Dunbar 2016 https://www.sciencedirect.com/science/article/pii/S0378873316301095
- **homophily(McPherson et al. 2001 "Birds of a Feather")**[THEORY]: 類似が紐帯を生む。強さ順に
  人種>**年齢>宗教>教育>職業>性別**。友人は**年齢・職業・教育で類似**。異質な紐帯は解消率が高く niche が強化。
  出典: https://www.annualreviews.org/content/journals/10.1146/annurev.soc.27.1.415
- **弱い紐帯の強さ(Granovetter 1973)**[THEORY]: 弱い紐帯=クラスタ間の**橋**で**非冗長な情報**を運ぶ。
  強い紐帯は同クラスタ内=冗長。「禁じられた三者関係」= A-B, A-C が強ければ B-C も繋がる → 橋は必ず弱い紐帯。
  職探しは弱い紐帯経由が多い。**世界改変者(k*)の情報伝播は弱い紐帯が要**。
  出典: https://www.complexsystemsframeworks.ca/framework/strength-of-ties/
- **友人数(日本)**: 親友 ≈ 3-5(Dunbar 内層と整合)。commercial 調査で「友人」平均~27・「親友」~3.7、
  年齢とともに減少(大学生~45 → 20代社会人~21 → 30代~15)[PRIVATE=参考値]。
  出典: https://life.oricon.co.jp/news/73727/
- **友人の作られ方 / 会う頻度**[GOV/PRIVATE]:
  - 現在の友人は**学生時代**中心(31.6%)、社会人後の新規友人は**職場34.0% / 趣味・イベント17.3%**、
    社会人後に新友人ゼロ18.2%[PRIVATE]。 https://prtimes.jp/main/html/rd/p/000000004.000164135.html
  - 交際頻度は低下傾向(社会生活基本調査 交際・つきあい行動者率の逓減)[GOV]。
    非同居の家族・友人と対面で**「全くない」9.2%**(内閣官房 孤独・孤立基礎調査 令和5年)[GOV]。
    https://www.cao.go.jp/kodoku_koritsu/torikumi/zenkokuchousa/r5/pdf/tyosakekka_gaiyo.pdf
  - 学生時代友人と会う頻度は**月1回**が最頻[PRIVATE]。 https://gakumado.mynavi.jp/freshers/articles/46575

### 2.4 家族の共同行動 [GOV-SURVEY/PRIVATE]

- **共食率(夕食)**[GOV-SURVEY]: 家族と夕食「ほとんど毎日」**68.7%**、週4-5日11.6%、ほとんどない5.2%
  (農水省 食育に関する意識調査 令和5年)。朝食「ほとんど毎日」48.1%・「ほとんどない」26.1%。
  夕食共食は逓減(H30 73.8% → R5 68.7%)。 https://www.maff.go.jp/j/syokuiku/ishiki/r05/3-3.html
  → **家族同居者の夕食共食確率 ~0.69/日 が強い既定**(§3 カタログ)。
- **週末の家族外出**[PRIVATE-SMALL]: 月2-4回が過半(4回/月25.8%最頻)、0回はわずか1.3%(幼稚園児家庭・n=450)。
  https://hugkum.sho.jp/96829 (小標本=指標)
- **送迎(escort)**[PRIVATE]: 送迎の場面は保育園/幼稚園48.4%・習い事46.7%・学校32.6%。**44.3%が週5日以上**送迎。
  送迎の車利用は約9割。 https://dime.jp/genre/1484077/
- **親の育児関連時間**[GOV]: 6歳未満児あり世帯の家事関連時間、夫1時間54分 / 妻7時間28分(社会生活基本調査 R3)。
  https://www.stat.go.jp/data/shakai/2021/pdf/youyakua.pdf
- **夫婦の会話時間**[PRIVATE]: 平日15-30分が最頻、休日1-3時間。良好夫婦は疎遠夫婦の2.6倍。
  https://www.halmek-holdings.co.jp/news/insights/2024/zzig906nnuew/

### 2.5 職場の関係行動 — コロナ後に二極化 [PRIVATE]

- **飲み会の頻度**: 月**0回=64.4%**が最頻・月1回26.9%(ワークポート2023, n=621)。コロナ前比で**45.4%が減少**。
  https://xn--pckua2a7gp15o89zb.com/journal/news/347/
  「一切飲みに行かない」15%(前)→**30%(後)**、飲み相手「職場の同僚」44%→30%(ファンくる2023)。
  https://www.fancrew.co.jp/news/research/2309drinking.html
- **忘年会**: 実施率は回復**73.6%(2024)**(2019=61.4%)だが、参加意欲は低下(64.1%が意欲減・52.0%が対面飲み会不要)。
  参加したい**20代68.8%が最高** > 40代51.9% > 30代49.2% > 50代40.3%(Job総研2024)。
  https://prtimes.jp/main/html/rd/p/000000225.000013597.html
- **歓迎会・懇親会**: 実施率**29.1%(2024)** vs 51.8%(2019)=未回復(労務行政研究所)。 https://roumu.com/archives/126927.html
- **ランチ**: 平日昼食は**ひとり60.4%**(増加)、家族23.4%、職場の同僚・上司14.4%(いずれも減少)
  (マイボイスコム 第7回, n=9,907)。 https://prtimes.jp/main/html/rd/p/000001296.000007815.html
- **飲みニケーション**: 「不要」62%(2021 日本生命・初の不要過半)、20代までで不要66%。
  ただし **忌避は"上司同席・義務的"に集中**、同世代の任意の付き合いは受容(SHIBUYA109 lab.: 上司ありの飲み会
  「苦手」66.7% だが同世代なら「好き」50.8%)。 https://www.nli-research.co.jp/report/detail/id=79717
  → **職場の会食はモデル上「上司同席=忌避↑ / 同世代任意=許容」と階層依存で表現すべき**(年齢依存ではない)。

**§2 モデル化メモ**:
- 世帯シードは渋谷実数へ(単身~64.5%・平均~1.6人・若年就業偏り)。来街者は家族圏外=同伴は「連れ」のみ。
- 友人は Dunbar 層(強い5-15/弱い50-150)+ homophily(年齢/職業)で生成。情報伝播は弱い紐帯。
- 家族共同行動の最硬い数字=夕食共食0.69/日(農水省)。職場は「構造化イベントは復活・日常飲みは崩壊・
  ランチは単独化(0.60)」。飲み会忌避は階層依存。

### 2.6 余暇活動の参加率(レジャー白書2024=2023年データ)[GOV/二次]

余暇活動 年間参加率(15-79歳・全国)。⚠ レジャー白書は**種目別の同伴者構成(家族/友人/一人)を非公表**=
下表の同伴者列は活動特性+渋谷若年調査からの**【推定】**。参加率一次: 日本生産性本部
https://www.jpc-net.jp/research/detail/007085.html , 二次: https://www.nippon.com/ja/japan-data/h02068/ ,
https://www.business-plus.net/business/2412/241204_tp0001.html

| 活動 | 参加率2023 | 典型同伴【推定】 |
|---|---|---|
| 国内観光旅行 | 48.7% | 家族>友人・カップル |
| **外食(非日常)** | **39.2%** | 友人・家族・カップル(複数同伴が主) |
| 動画鑑賞 | 37.0% | 一人>家族 |
| 音楽鑑賞 | 34.5% | 一人 |
| ドライブ | 32.7% | 家族・カップル・友人(要 has_car) |
| **映画館** | 7位(2024=33.7%) | 友人・カップル>一人 |
| ウォーキング | 7位 | 一人・夫婦 |
| **ショッピング(SC/アウトレット)** | 9位 | 友人(女友達)・家族 |
| 家庭用ゲーム | 21.6% | 一人>友人 |
| **カラオケ** | **20.2%** | 友人・同僚(集団性が高い) |
| 一人当たり平均参加種目 | 10.1種目/年 | — |

### 2.7 渋谷の若者の遊び(同伴者の実データが最も濃い領域)[一次・自主調査]

SHIBUYA109 lab.「around20の渋谷に関する調査」2020(N=400・15-24歳女性・首都圏・過去1年渋谷来街)。
出典: https://www.shibuya109.co.jp/shibuya109lab/reports/2004121/
- **来街目的**: ランチ38.3% / ファッション買い物35.3% / ディナー32.3%。
- **同伴者(誰と来るか)**: **女友達54.0%(最多)** / 学校の友達31.8% / 家族22.3% → 報告書は渋谷を
  「シスターフッドシティ」=**友人主導が家族の約2.4倍**。
- **遊びの中身**: Instagram投稿=友達との写真70.9% / カフェ・食事52.0% / **プリクラ33.6%**。
  定番活動=ショッピング/カフェ/プリクラ/外食/ゲームセンター。行き先探しは Instagram 82.9%。
- プリクラは「記念に残したい」約90%=**友人・恋人と撮る"体験"**(seamint. 調査)。
  https://prtimes.jp/main/html/rd/p/000000005.000048437.html
- ⚠ **含意**: 渋谷の共同行動の主役は**若年層の友人グループ**。カタログ(§3)で若年層の友人同伴率を高く較正する。

---

## 3. 共同行動カタログ(関係タイプ×行動)

**選定方針**: ユーザー例(映画/カラオケ/ビジネス会食)は網羅空間の一部。§2 統計から参加率・同伴実態で
重要度を判断し、**渋谷で日中に発生し・既存 POI/機構に載り・関係タイプが効く**行動を選んだ。国内旅行・
ドライブ(要 has_car・圏外移動)は渋谷日中シムでは優先度低。以下は関係タイプ別の候補と実装接続。

### 3.1 家族/同居(household・居住者のみ)

| 行動 | 較正値 | 実装機構 | コスト/効果 |
|---|---|---|---|
| **夕食の共食** | 0.69/日(ほぼ毎日) | 夜帯に同一世帯が home_building へ収束(household の home 共有=既存)。共食フラグ+`meal` | 食費(既存 spend)/ relatedness+ |
| 週末の外出 | 月2-4回 | 休日に世帯で共有(POI,時刻)=date_dest を家族へ一般化 | 交通・POI費 / social+ |
| 送迎(escort) | 送迎者44%が週5日+ | 既存 `escort` what-type(:_PLAN_CAT 未登録=landmark後退)。子の学校/習い事へ同行 | 時間 / 義務(maintenance) |
| 買い物同行 | — | 世帯ペアで shop POI 収束 | 買い物費 / social+ |

### 3.2 恋人(partner・既存 date_dest で実装済み)

| 行動 | 較正値 | 実装機構 | コスト/効果 |
|---|---|---|---|
| **デート** | date_bias | **既存 `date_dest`(household.py:151)**=(ペア,当日) 純関数で同一ノード収束 | POI費 / social+emotion+ |
| 会食・映画・買い物 | — | date の行き先カテゴリを活動カタログから引く(現状は全 dests 一様) | 各POI費 |

### 3.3 友人(relations tier≥2・強い紐帯/弱い紐帯)

| 行動 | 参加率 | 主同伴 | 実装機構 | コスト/効果 |
|---|---|---|---|---|
| **外食・カフェ・お茶** | 外食39.2% | 友人・渋谷若年 | 同伴選択+food POI 収束(§4-B) | 食費 / social+ |
| **カラオケ** | 20.2% | 友人・同僚 | leisure POI(カラオケ)収束 | 娯楽費 / social+emotion+ |
| **映画** | ~33.7% | 友人・カップル | leisure POI(映画館)収束 | 映画代 / emotion+ |
| **ショッピング** | 9位 | 女友達・家族 | shop POI 収束(渋谷若年で高頻度) | 買い物費 / social+ |
| プリクラ/ゲーセン | 渋谷33.6% | 友人 | leisure POI(若年層限定で較正) | 娯楽費 / emotion+ |
| ライブ・イベント | エンタメ12% | 友人 | **既存 host_event/annual_events** | 参加費 / emotion+ |
| 遊び(汎用) | — | 友人 | schedule の `遊び` what(既存) | — |

### 3.4 同僚/ビジネス(org_id 共有・階層依存)

| 行動 | 較正値 | 実装機構 | コスト/効果 |
|---|---|---|---|
| **ランチ(同僚)** | 14.4%(単独60.4%) | 勤務者×昼帯に同 org_id を food POI 収束(低確率=単独が主) | 食費 / social+ |
| **飲み会/会食** | 月0回64%・忘年会73.6% | 退勤後に同 org_id を居酒屋POI収束。**上司同席=参加率↓/同世代=↑**(§2.5 階層依存) | 飲食費 / social+(義務感) |
| ビジネス会食 | — | ビジネス関係(取引=将来)を meal POI 収束 | 会食費 / — |

### 3.5 来街者の連れ(party・現状 party_size 未使用)

| 行動 | 較正値 | 実装機構 | コスト/効果 |
|---|---|---|---|
| 連れと来街・回遊 | party_size 1-5 | プールの `party_size`(未使用)を同席実体化=同一入街時刻・同行 | POI費 / social+ |

**カタログ上位(実装優先)**: (1) 家族の夕食共食(最硬い統計・home共有済み)、(2) 友人の外食/カラオケ/映画/
買い物(渋谷の主役・参加率高)、(3) 同僚のランチ/飲み会(階層依存の妙)、(4) 恋人デート(既存拡張)、
(5) 来街者 party。**すべて "同伴者が同一(POI,時刻)を選ぶ+合流は決定論" の一機構(§4-B)で表現できる**。

---

## 4. 実装案(ユーザー承認用=実装はしない)

**設計原則**(先行例 §research + R1 契約): 共同行動=「N人が独立に同一(場所,時刻)を選ぶ+**合流は決定論**
パスファインディング」(Generative Agents が創発で示し、AgentSociety が gravity model で定式化)。
**誘い→承諾は決定論**(LLM 呼を増やさない)、**会話だけ既存の対面会話予算**を使う。既存の `date_dest`
(ペア決定論収束)と host_event `_route_to`(会場へ経路)が既にこの形=**一般化するだけ**。

### A. 初期関係ネットワークの生成

**プール736MB 再生成は不要**(結論)。household/friend とも**実行時の純関数導出**(オントロジー方式=
`_apply_ontology` と同型)で賄える。プールに spouse_id/friend edges を焼き込むと 736MB 再生成+
gitignore 資産の作り直しになるが、**persona の属性(age/gender/occupation/area/org_id)は実行時に読める**
ので、それらと決定論シードから世帯・友人を導出すれば再生成ゼロ。R1(OFF でバイト一致・新 stream のみ)も守れる。

- **A1. 世帯(家族)の現実化** — 既存 `household.build_households` を拡張:
  - size_weights を**渋谷実数へ較正**(単身~64.5%・平均~1.6人・§2.1)。現状 `[0.35,...]` は乖離。
  - **人口統計整合の束ね**: 現状は id 昇順で機械的に束ねる。改善案=居住者を (area, age) でソートしてから束ね、
    2人世帯は年齢近接=夫婦、3-4人は年齢差=親子を**決定論**割当(続柄 `household_role` を付す)。
    `age` は既にオントロジー人口統計(P0)にあり読める。乱数は新 stream `household` のみ。
  - 家族の**夕食共食**: 夜帯に同一世帯を home へ収束(home 共有は既存)+共食観測イベント。
- **A2. 友人グラフ** — 現状「同建物の顔なじみ」を homophily グラフへ拡張(実行時純関数):
  - **辺の生成**: 各居住者に対し (a) 同 area 近接、(b) **homophily**(age/occupation 類似=McPherson)、
    (c) **共有所属**(同 school org_id=学生時代友人31.6%、同 work org_id=職場友人34.0%)で友人辺を張る。
  - **次数分布**: Dunbar 層で較正(強い紐帯~5-15)。弱い紐帯(50-150)は relations tier=1(知人)相当で薄く。
  - **決定論**: 友人辺は (persona id ペア, seed) の純関数ハッシュ=run.seed 非依存(比較実験の要)。
    新 stream `friend_graph` のみ。初期 relations 台帳へ `record_contact` で注入(顔なじみ経路と同じ)。
  - **来街者は対象外**(家族・友人は圏外)=現状 household と整合。
- **A3. 来街者 party 実体化** — プールの `party_size`(未使用)を同席の連れに: 同一入街時刻・同一初期ノード・
  相互 relations 注入。新 stream `party`。
- **同僚** = `org_id` 共有(既存・追加不要)。

### B. 共同行動カタログの実装機構(LLM 呼を増やさない機械層)

**新モジュール(仮) `src/society/joint.py`**(src/society 直下=検査対象外、household/schedule と同じ流儀):

1. **同伴者選択(決定論)**: 自由時間(discretionary)の agent が、活動タイプに応じ relations/household から
   同伴候補を選ぶ。友人行動=tier≥2 かつ homophily 上位、家族行動=housemates、同僚行動=同 org_id。
   選択は (agent, day, 活動) の純関数(乱数は新 stream `joint` のみ)。
2. **同一(POI,時刻)への収束(決定論=ランデブー)**: **`date_dest` の一般化**。(同伴ペア/グループの最小id,
   当日, 活動タイプ) から純関数で活動カテゴリ内 POI を1つ導出=**全員が同じ POI を選ぶ**。時刻は活動の帯
   (昼=ランチ・夜=飲み会等)。両者 `_route_to`(既存)で合流 → **既存の対面会話が発火**(追加 generate ゼロ)。
3. **誘い→承諾(決定論、任意で LLM 一部)**:
   - **既定=決定論**: 承諾確率 = base + relation_bonus(tier で増)− 階層ペナルティ(上司同席の飲み会)。
     **host_event の `_events_start` 抽選(attend_base+attend_relation_bonus)を再利用**。専用 stream。
   - **任意=計画時LLM**: `planning.framework` ON なら計画スキーマの `with`(休眠中の同伴者フィールド)に
     LLM が同伴者名を書ける。決定論リゾルバが名前→最近傍 relation に解決し(2)へ。**追加呼は無し**(既存の
     計画 generate 内)。→ **休眠フィールド `with` の初めての接続先**。
4. **活動の類型化**: 活動タイプ(meal/karaoke/cinema/shopping/drinking/date/family_meal…)を**参加率で較正**
   した重みで抽選(§3 の表)。年齢条件付き(渋谷若年=友人遊び高・カラオケ/プリクラ)。POI カテゴリは既存
   food/shop/leisure/landmark(routine `_PLAN_CAT`)へマップ。
5. **費用(economy 接続)**: 各活動に費用=既存 `_poi_price`/spend/consumption に載る(新規経済機構は不要)。
6. **満足/ドライブ効果**: 共同行動の完遂で既存の **social 価値タグ(values.py 交流)+ relatedness(needs
   company)+ company ドライブ**へ加算(新 state 不要)。孤独(silence)の解消にも接続。
7. **観測**: 新イベント種 `joint_activity`{type, with, place, tier} を1本追加(schema.py 登録)。
   共同行動の発生率・同伴構成・関係タイプ別を計測(measure/aggregate に列)。

**呼数 k 非依存の担保**: (1)-(6) は全決定論(乱数は専用 stream のみ)+ LLM generate をゼロ増。会話は
**既存の対面会話予算内**(合流後に同席者が増えるだけ=host_event/date と同型の「物理位置は変わるが呼数不変」)。
既定 OFF=`joint.py` を一切呼ばず・新 stream も引かない=ゴールデン `golden_baseline_l1.json` バイト一致。

### C. スライス分割(優先順位・工数・R1整合)

| スライス | 内容 | 再利用 | 工数 | 依存 |
|---|---|---|---|---|
| **S-R1 世帯・家族の現実化** | size_weights を渋谷実数へ+人口統計整合の束ね(続柄)+夕食共食 | household.py 拡張 | 小 | age(P0) |
| **S-R3 共同行動エンジン** | 同伴選択→同一(POI,時刻)収束→合流(決定論)+活動カタログ+費用+充足+観測 | date_dest/route_to/values/needs | 中 | relations/household ON |
| **S-R2 友人グラフ生成** | homophily+所属(school/work)+Dunbar次数、実行時純関数 | 顔なじみ/relations 拡張 | 中 | age/occupation/org_id |
| **S-R4 職場の会食・飲み会** | 同 org_id のランチ/飲み会+**階層依存**(上司同席=忌避) | S-R3 の上に薄く | 小 | S-R3, org_id |
| **S-R5 来街者 party 実体化** | party_size を同席の連れに | プール既存フィールド | 小 | pool |

**推奨順**: **S-R1(基盤・最安・家族に意味を与える)→ S-R3(ユーザー要望の核=共同行動。既存 relations の
顔なじみ+household で即機能)→ S-R2(友人を現実化=S-R3 の質を上げる)→ S-R4(職場の妙)→ S-R5(来街者)**。
- S-R3 は S-R2 を待たずに**既存の顔なじみ友人+household 家族で先行可能**(段階投入)。S-R2 完了で友人の
  質(homophily・弱い紐帯)が上がる。
- 各スライスとも: **既定 OFF=バイト一致**(新 conf キー・OFF で no-op)、**呼数 k 非依存**(全決定論+新 stream
  のみ・LLM generate ゼロ増)、**no-fingerprint**(joint/household/friend のロジックは src/society 直下=検査外、
  因子名・地名リテラルを engine に書かない)。R1 契約は career/health/household と同型で担保できる。
- **観測(共同行動イベント)**: `joint_activity` 1種を追加し、共同行動の発生率・関係タイプ別同伴構成・
  年齢別・POI別を calibrate_report/measure に接続(現実の参加率 §2.6 との照合=较正の測り方)。

### 渋谷の現実制約の反映(まとめ)

- **単身率64.5%**=居住者の約2/3は世帯を組まない(家族共同行動の母数は限定)。size_weights を実数へ。
- **昼夜間比2.26倍**=街の大多数は来街者・家族圏外 → 家族/友人グラフは**居住者限定**、来街者は party のみ。
- **渋谷=若年友人の街**(女友達54%)=友人共同行動を年齢条件付きで高く較正(カラオケ/プリクラ/カフェ)。
- **飲み会は階層依存**(上司同席=忌避↑・同世代任意=許容)=年齢一律でなく org 内の役職差で表現。

---

## 5. 未確認事項(事実と推測の区別)

**事実(コード実査で確認)**:
- relations/household/schedule/host_event(attend_relation_bonus)は実装済み・production/daily で ON。
- 計画スキーマの `with`(同伴者)は存在するが `planning.framework.enabled: false` かつ共同行動機構に未接続。
- プールに家族・友人フィールドは無い(世帯は起動時 id 順生成・友人は顔なじみのみ)。`party_size` は未使用。
- `date_dest` はペア決定論の同一ノード収束を既に実装(ランデブーの原型)。

**確認済み統計(出典 URL 付き・§2)**: 渋谷単身率64.5%・昼夜間比2.26・夕食共食0.69・飲み会月0回64%・
忘年会73.6%・ランチ単独60.4%・外食39.2%/カラオケ20.2%(レジャー白書)・渋谷若年 女友達同伴54%。

**推測・未確定(要追加確認)**:
- **レジャー種目別の同伴者構成(家族/友人/一人)は公的に非公表** → §3 の同伴者列は活動特性+渋谷若年調査
  からの推定。カラオケ/映画/ショッピングの「友人同伴率」の確たる実数は未取得。
- **交際・付き合いの絶対時間(分)・年齢別行動者率**は e-Stat 表1-1(Excel)にあるが当環境で未抽出。
- カラオケ/スポーツ観戦/遊園地の**単年参加率の確定値**はレジャー白書本編要参照(二次で20.2%等は確認)。
- 渋谷若年データは**女性 around20 中心**=男性・他年齢の同伴構成は外挿(推定)。
- 実装の R1 厳密性(joint.py の合流が FixedLLM で ON==OFF 呼数一致になるか)は**設計時に career/health と
  同じ検証が必要**(物理位置変化で対面会話の同席者が変わる=呼数は不変だがキャッシュキーは変わりうる)。
- household の人口統計整合の束ね(続柄割当)の具体アルゴリズムは本書では方針のみ=設計スライスで詳細化。

**次アクション(ユーザー承認待ち)**: S-R1/S-R3 の設計詳細(pre-coding-alignment に従い決定アジェンダ提示)へ
進むか、S-R2 の homophily 辺生成の較正パラメータ(次数分布・homophily 強度)を先に詰めるか、を確認したい。

