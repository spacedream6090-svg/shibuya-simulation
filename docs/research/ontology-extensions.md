# 群のオントロジー拡張 — 軸候補のwebリサーチと選定(実装は次wave)

作成: 2026-07-21 / 担当: リサーチ(Opus)/ **コード変更なし・読み取りのみ・conf変更なし**

## この文書の目的

第40バッチで「文化圏×経験」の群オントロジー(`src/society/ontology.py`)を実装済み。ユーザーの要望:

> 僕が例示したもの以外にたくさんあるかもしれないので、webをリサーチして候補を挙げ**最も重要そうだと思うものを実装**してほしい。僕の例は信用せず、君がリサーチして重要そうと思ったものを。

本稿は**リサーチと選定まで**を担当する(実装は次wave=config競合回避のため別途)。5トピッククラスタで並行webリサーチを行い、行動差の実証(効果量・公的統計優先)・出典URL・本シムでの表現可能性・R1整合を各候補に付し、採点表で順位づけして**実装推奨トップ3**と**実装仕様案**を示す。決定はFable/ユーザーが行う前提の「素材」である。

**先に結論(3行)**
1. **推奨トップ1=情報行動・情報源信頼(年代コホート差)**。総務省・内閣府の本文確認済み統計が最強クラスで、災害時の避難タイミング・デマ拡散・組織核形成の情報カスケードに直結し、既存の文化圏軸・P3層と**真に直交**する。機構的には「直交する第2軸」の追加が自然。
2. **トップ2=防災訓練経験**。避難率の調整オッズ比 **OR=1.99** という効果量最強・日本データ。既存4群の `line` に1句織り込む(**経験キー追加**)だけで済む最小コスト。ただし文化圏軸と相関=補完的に使う。
3. **トップ3=同行者構成(単独/連れ)**。歩行速度 −17〜30%・合議遅延・はぐれ待ちの実証があり、避難ダイナミクスと最小社会単位(組織核)の両方に効く。文化圏・情報・訓練いずれとも直交。

**使わない方がよい軸(negative finding)**: 世代論(職場価値観のメタ分析で世代差ほぼゼロ+APC識別不能)、Hofstede文化次元スコアの個体直接適用(生態学的誤謬)。詳細は §5。

---

## 1. 現状機構の実査(正確な把握)

`src/society/ontology.py` と `conf/config.yaml` の `ontology` ブロック、および注入経路(`engine/simulation.py`・`cognition/deliberate.py`)を読んだ結果:

### 1.1 現行の軸と経験キー
- **軸**: 「文化圏×経験」の**単一群**(1エージェント=1群)。既定4群:
  - `jp_metro`(都市圏在住の日本人)/ `jp_other`(国内他地域来街者)/ `asia_visit`(アジア圏旅行者)/ `west_visit`(欧米圏旅行者)。
- **経験プライア(メタキー)**: `quake_exp`(high/mid/low/none)・`city_exp`(high/mid)・`ja`(native/partial/none)。`build_cfg` は `label`/`line`/`wv_offsets` 以外のキーを**素通し**で保持する(`ontology.py:61-63`)=観測・分析用。
- **プロンプトへ入るのは `line`(経験の事実1行)のみ**(`deliberate.py:157-159` で `agent.persona` の直後に1行 append)。経験キー自体はプロンプトに入らない。行動分岐はルールで書かず、この1行を読んだLLMが自ら生む(nature-like方針)。
- **`wv_offsets`**: 現状 `controllability` のみ対応(`initial_controllability`, worldview起点をS-bで1回ずらす)。

### 1.2 割当機構(決定論・直交)
- `assign_group(cfg, pid, tier)`: `_stable_uniform(seed, pid)`(hashlib blake2b、run.seed非依存・PYTHONHASHSEED不感)で一様値[0,1)を作り、`composition[tier]` の比率を**group id昇順**で累積分割して1群を選ぶ。
- **tier** = P3 presence層名: `resident`/`duty`/`workday_shift`/`cadence`/`stochastic` + 直接ラン用 `default`。層別に構成比を振れる(`composition.<tier>`)。
- **R1直交(doctrine #4)**: 割当は `pool_pid`(またはagent.id)=persona id のみの関数。traits・k は一切読まない。乱数ゼロ(RngHub無風)。
- **既定OFF**: `enabled=false` で属性を1つも作らない=プロンプト・状態とも不変=ゴールデンL1バイト一致。

### 1.3 拡張3方式の機構的比較(どれが自然か)

| 方式 | 機構への影響 | 直交な軸を足せるか | コスト | 適する候補 |
|---|---|---|---|---|
| **(A) 経験キーの追加** | `build_cfg` は既に未知キーを素通し=configのみで完結。ただし**プロンプトに効かせるには既存群の `line` に1句を織り込む**必要がある(観測メタだけならkey追加で済むが行動には効かない) | ×(文化圏群に固定結合=文化圏と相関する経験しか足せない) | **最小**(conf のみ) | 防災訓練経験(日本人=訓練済み、と文化圏に沿う) |
| **(B) 直交する第2軸** | `assign_group` を軸引数付きに、または第2割当関数を追加。`_stable_uniform(seed + 軸オフセット, pid)` で第1と独立な一様値=決定論・直交を保てる。第2 `line` を注入(プロンプトが2行に) | ○(文化圏と真に独立な軸=情報行動・同行者を表現可) | **中**(ontology.py + config スキーマ + 注入側の2行連結) | 情報行動、同行者構成 |
| **(C) 群の細分化** | 単一軸内で群数を増やす(例 `jp_metro` を訓練済/未訓練で2分割) | △(組合せ爆発。composition記述が煩雑) | 中〜高 | 非推奨 |

**考察**: ユーザーの例(地震/都市/日本語)はすべて「文化圏」という1つのペルソナ次元に束ねられ**1行で語られている**。文化圏と相関する経験(防災訓練など)は方式(A)で足りるが、**文化圏と独立な軸(情報行動=年代に紐づく・同行者=来街時の連れ)は方式(B)の直交第2軸でしか正しく表現できない**(日本人都市圏でも高齢者はTV依存・若者はSNS依存=文化圏に固定できない)。したがって「機構的に自然か」は候補次第で、推奨トップ1(情報行動)は方式(B)、トップ2(訓練)は方式(A)が正解。

> 補足(交絡回避): `agent.age`(P0ペルソナ、int 18-70)は実在するが、情報行動を age から直読すると割当が「persona id のみの関数」でなくなる。**composition の比率で年代分布を近似する方が R1純度(persona id純関数)を保てる**(§6.1で仕様化)。age は P0 でありtraits/k因子ではないので R1直交は破れないが、決定論・純関数性の観点で composition 近似を推す。

---

## 2. リサーチ全候補一覧(採点表)

5クラスタのwebリサーチ(出典は §7)から抽出した**行動差の実証がある軸**を、本シムの4評価軸+**直交性**(既存軸/P3層と冗長でないか)で採点した。各5点満点(**実装容易性は容易ほど高、直交性は独立なほど高**)。

| # | 軸候補 | 渋谷再現 | 災害・群衆予測 | 実装容易性 | 実証の強さ | 直交性 | 合計 | 実証の核(§7に出典) |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|---|
| 1 | **情報行動・情報源信頼(年代差)** | 4 | 4 | 3 | 5 | 5 | **21** | 災害情報入手が18–29歳でSNS76.6%>TV73.8%・70歳+でTV91.9%(内閣府, 本文確認)。デマ感受性MISTの年代差(本文確認) |
| 2 | **防災訓練経験** | 3 | 5 | 5 | 5 | 2 | **20** | 訓練参加者の避難率が非参加者より高い調整OR=1.99(95%CI 1.53–2.61, 東日本大震災2,314名) |
| 3 | **同行者構成(単独/連れ)** | 4 | 4 | 3 | 4 | 4 | **19** | 2人組は単独より約30%遅い・4人組17%遅い(Moussaïd 2010)。連れあり初動1.88秒vs単独1.21秒 |
| 4 | 移動制約(歩行速度) | 4 | 5 | 2 | 4 | 4 | **19** | 健常1.0–1.5・後期高齢0.98・車椅子0.3–0.9 m/s。混合群集で全体速度低下。※機構ミスマッチ(§3) |
| 5 | 障害・感覚特性(要配慮者) | 3 | 5 | 3 | 4 | 4 | **19** | 障害者の震災死亡率が一般の約2倍(東日本, 本文確認)。聴覚障害の警報アクセス欠如 |
| 6 | 土地勘・常連度(渋谷固有) | 4 | 4 | 3 | 4 | 2 | **17** | 二等距離出口で約71%が「入ってきた馴染みの扉」を選択。認知地図解像度差 |
| 7 | ペット同伴 | 2 | 3 | 4 | 3 | 4 | **16** | 16.2%が「ペット無しでは避難しない」・カトリーナ避難拒否の44%がペット理由。※米国データ |
| 8 | 来街目的(通勤/買回り/観光/夜) | 5 | 3 | 2 | 4 | 1 | **15** | 平均滞在269分・昼夜間人口比2.39。※**P3 tierと冗長**(§3) |
| 9 | 宗教・食制約(ハラール/菜食) | 3 | 2 | 4 | 3 | 3 | **15** | 訪日菜食者約128万人(訪日客の約5%, 本文確認)・訪日ムスリム150万人超。※国籍と交絡 |
| 10 | クロノタイプ(朝型/夜型) | 3 | 2 | 4 | 3 | 2 | **14** | 朝型25%/中間50%/夜型25%・20歳で夜型ピーク。※**年齢と強交絡** |
| 11 | 対人距離・密度許容(proxemics) | 3 | 3 | 2 | 4 | 3 | **15** | 見知らぬ他者への選好距離 国差76–140cm。密度は物理制約(Fruin 5→6→7人/㎡)=文化非依存 |
| 12 | 世代コホート価値観 | 2 | 1 | — | 1 | 1 | **除外** | メタ分析で世代差ほぼゼロ+APC識別不能(§5)。**使わない** |
| 13 | Hofstede文化次元(UAI等) | 2 | 2 | — | 3 | 1 | **除外/条件付** | 生態学的誤謬で個体直接適用NG。**compositionパラメータとしてのみ**(§5) |

採点の根拠は各候補の実証・出典(§7)と、機構的自然さ(§1.3, §3)による。上位3(#1・#2・#3)を推奨とし、#4・#5は「予測効果は高いが機構が現行の line 注入と相性が悪い/倫理配慮が要る」ため次点として §4 で扱う。

---

## 3. 高スコアだが採用を見送る/条件を付ける軸(重要な留保)

- **#4 移動制約(歩行速度)**: 避難の律速で予測効果は最大級だが、現行機構は「経験の事実1行→LLMに委ねる」もので**物理速度(m/s)には直結しない**。速度はengine側の移動パラメータとして別途モデル化するのが自然(ontologyは意思決定バイアスの層)。「ベビーカーで階段を避け遠回りする」のような**意思決定バイアス**としてなら line で表現可だが、速度そのものはR1/engineの管轄。→ **ontology軸としては見送り、engine側の別提案として切り出すべき**。
- **#5 障害・感覚特性**: 死亡率2倍という強い実証だが、(i)割合が小さく composition の粗い比率では表現が荒い、(ii)実在の要配慮者への配慮=センシティブ。ただし「音の警報が聞こえない/標識が読めない」という**警報アクセス機序**は災害種を問わず頑健で、災害シナリオ研究の価値は高い。→ **本番投入は要ユーザー判断**。まずは #1〜#3 を先行。
- **#8 来街目的**: 渋谷再現の主駆動因だが、**P3 presence層(resident=住民/workday_shift=通勤従業者/cadence=定期常連/stochastic=非定期観光娯楽)が既に来街目的の代理になっている**。ontology軸に重ねると二重計上。→ 来街目的は tier で表現済みとみなし、ontology軸には立てない。
- **#10 クロノタイプ**: 夜型×夜間娯楽/飲酒の関連は堅いが、**年齢と強交絡**(20代夜型ピーク)=年齢/来街時刻を入れれば大半説明可能。独立軸として過剰重み付けは二重計上。
- **#13 Hofstede**: §5参照。個体割当は誤謬。使うなら composition の**分布パラメータ**としてのみ。

---

## 4. 推奨トップ3と理由(実装は次wave)

### トップ1 — 情報行動・情報源信頼(年代コホート差) 〔機構: 直交する第2軸(方式B)〕

**なぜ最有力か**
- **実証が公的統計で最強クラス(本文確認済み)**: 内閣府「防災に関する世論調査」で災害情報の入手手段が**18–29歳はSNS 76.6%>テレビ 73.8%(逆転)**、**70歳以上はテレビ 91.9%**(令和5年防災白書で全数値裏取り)。総務省令和3年白書のメディア信頼度=新聞61.2%/テレビ53.8%に対しSNSは「信用できない」27.5%。デマ感受性MIST(査読)は18–29歳で高スコア11%・65歳+で36%と年代差。
- **災害・群衆予測に直結**: 情報源が避難開始タイミングを規定(SNS一次情報は速いが誤報リスク、公式待ちは遅いが正確)。デマ拡散(Vosoughi 2018: 虚偽は真実より70%多く拡散)→誤避難・パニックの土壌。既存の `labeling`/`sns_geo`/`ads` の情報伝播機構と観測が接続する。
- **組織形成観察(org-emergence-goal)にも効く**: 情報カスケードは組織核の形成土壌。誰の情報を信じ、誰に伝えるかが最小の社会結合。
- **既存軸と真に直交**: 文化圏(日本人/旅行者)ともP3層(住民/来街)とも独立。日本人都市圏の中に「SNS一次派」と「公式・放送派」が併存する=文化圏群に固定できない=**方式(B)の直交第2軸が機構的に正しい**。
- **渋谷との整合**: 渋谷来街は20–30代が半数超=若年SNS層が濃い街。情報行動の再現は渋谷らしさに直結。

**ステレオタイプ回避の規律**: 群ラベルを年代でなく「情報行動様式」にし、composition で年代分布を近似する(§6.1)。プロンプトは「若者は〜」の断定でなく、**一人称の行動の事実**で書く(§6.3)。

### トップ2 — 防災訓練経験 〔機構: 経験キー追加(方式A)〕

**なぜ有力か**
- **効果量が最強・査読・日本データ**: 東日本大震災の被災地2,314名(67%が避難)で、事前の津波避難訓練参加者は非参加者より避難率が有意に高い(**多変量調整OR=1.99, 95%CI 1.53–2.61**)。訓練以外の防災経験は避難に効果なし=「身体的リハーサル」の弁別的効果。GIS×ABMでも訓練群は出口が分散し総避難時間短縮(未訓練19分42秒→訓練済10分28秒)。
- **日本の学校・職場の防災訓練文化と直結**し、既存4群の `line` に1句(「毎年避難訓練を受けて手順が身体化している」)を織り込むだけ=**最小コスト**。
- **留保**: 文化圏軸(quake_exp)と相関する=独立軸ではない。既存日本人群の line 精緻化として**補完的に**使う。過剰訓練で「ルート選択に迷う」逆効果の報告もあり、断定は避ける。

### トップ3 — 同行者構成(単独/連れ) 〔機構: 準静的な第3軸(方式B)または line 織り込み〕

**なぜ有力か**
- **実証あり**: 2人組は単独より約30%遅い・4人組17%遅い(Moussaïd 2010, PLOS ONE)。制御実験で連れあり初動1.88秒 vs 単独1.21秒、最寄り出口選択率 連れあり59% vs 単独75%(連れに引かれ最適から逸脱)。子連れは避難確率↑だが出発遅延、はぐれ待ちで合議遅延。
- **避難ダイナミクスと最小社会単位の両方に効く**: 群衆速度の律速であり、「連れ=最小の社会結合」は組織形成の観察素材にもなる。
- **直交**: 文化圏・情報・訓練いずれとも独立。line で自然に表現可(「連れと一緒なので、はぐれないよう皆と同じ方へ動きがち」)。
- **留保**: 同行者は本来動的(その場で変わる)。来街時点で決まる**準静的属性**(単独来街/連れあり来街)として割り当てるのが妥当。

---

## 5. 使わない方がよい/条件を付ける軸(negative finding=重要)

- **世代コホート価値観(除外)**: 職場価値観の世代差はメタ分析で「中程度〜ゼロ」(Ravid et al. 2025, J. Organizational Behavior)。横断データでは age/period/cohort が識別不能(APC問題)で、観察差を「世代」に断定帰属できない。**ボトムアップ創発を志向する本プロジェクトに擬似相関を注入するリスク**が最も高い軸。差を入れるなら年齢・時代文脈で表現し、世代カテゴリは避ける。
- **Hofstede文化次元の個体直接適用(条件付)**: UAI等の国別スコアを個体の性格にコピーするのは**生態学的誤謬**(Brewer & Venaik 2014)。国レベルで相関する項目が個人レベルでは同様に相関しない。使うなら「集団の分布パラメータ」として与え、個体は分布からサンプリングし集団内分散を必ず持たせる=**composition の比率設計に反映するに留める**。
- **パニック神話(ガードレール)**: 災害社会学の合意は「集団パニックはまれ、実際は協調的」(Quarantelli, Clarke)。これは個体差ではなく**基準率のガードレール**=「パニック個体の基準率を極めて低く」設計し、災害時デフォルトを協調に置く原則。
- **対人距離と密度耐圧は分離**: 選好対人距離(文化差)と高密度の許容(満員電車を我慢できる)は別問題。密度の危険閾値(Fruin 5→6→7人/㎡)は**文化非依存の物理制約**として全エージェント共通に置くべき(ontology軸にしない)。

---

## 6. 実装仕様案(次waveの素材。conf/コードは本waveでは触らない)

### 6.1 configスキーマ拡張案 — 直交する第2軸(方式B)

現行 `ontology` は単一 `groups`/`composition`。第2軸(情報行動)を**別名前空間**で足すと既存の文化圏軸と衝突しない。案(スキーマのみ・値は例):

```yaml
ontology:
  enabled: false
  seed: 20260721
  groups: { ...現行4群そのまま... }
  composition: { ...現行そのまま... }

  # ---- 追加軸(直交する第2軸=情報行動)。既定 OFF は現行と完全同一 ----
  axes:                          # 第2軸以降を配列/辞書で持つ(現行groups/compositionは第1軸として据置)
    info_behavior:
      seed_offset: 101           # _stable_uniform(seed + seed_offset, pid)=第1軸と独立な一様値
      groups:
        info_sns:      { label: "SNS一次情報を頼る人",   line: "気になることがあると、まずスマホで現地の投稿や短い動画を探して状況をつかもうとする。" }
        info_official: { label: "公式・放送を頼る人",     line: "大事な知らせは、テレビや駅・行政のアナウンスで確かめてから動く習慣がある。" }
      composition:               # tier別に年代分布を近似(渋谷=若年濃い→stochasticでinfo_sns高め)
        resident:      { info_sns: 0.45, info_official: 0.55 }
        duty:          { info_sns: 0.55, info_official: 0.45 }
        workday_shift: { info_sns: 0.60, info_official: 0.40 }
        cadence:       { info_sns: 0.70, info_official: 0.30 }   # 学生/常連=若年
        stochastic:    { info_sns: 0.65, info_official: 0.35 }   # 非定期来街(観光娯楽)
        default:       { info_sns: 0.55, info_official: 0.45 }
```

- 割当: `assign_group2 = assign(cfg.axes[name], pid, tier, seed_offset)`。`_stable_uniform(seed + seed_offset, pid)` で第1軸ハッシュと独立=**同一pidでも第1軸群と第2軸群は無相関**。決定論・run.seed非依存・乱数ゼロは現行と同じ性質を継承。
- 注入: `deliberate.py` の `ontology_line` 追加箇所(157–159行)を、第1軸行に続けて第2軸行も append(**2行**)に拡張。あるいは agent に `ontology_lines: list[str]` を持たせ順に注入。
- 既定OFF: `axes` 未指定/`enabled=false` は属性を1つも作らない=バイト一致(現行の既定OFF規律をそのまま継承)。
- 3群化(`info_mixed` 中間)も可だが、まず2群でシグナルを見るのが軽い。

### 6.2 トップ2(防災訓練)=既存群の line 織り込み(方式A)

第2軸を足さず、**既存日本人群の `line` に1句**足すだけ(conf1行編集)。観測用に `drill_exp` メタも付す(素通しで保持され observer で集計可):

```yaml
groups:
  jp_metro: { label: "都市圏在住の日本人", line: "長く都市部で暮らし、地震や混雑した街には慣れている。学校や職場で毎年避難訓練を受け、揺れたらまず身を守り指定ルートで動く手順が身体に染みついている。", quake_exp: high, city_exp: high, ja: native, drill_exp: high }
  # jp_other も native/日本の訓練文化=drill_exp: high。旅行者群(asia/west)は drill_exp: low/none のまま line に訓練句を入れない。
```

- 文化圏に沿う経験なので方式Aで足りる。旅行者群には訓練句を入れない=文化圏との相関を保ったまま「訓練済み日本人」の初動速さを LLM に委ねる。

### 6.3 プロンプト文言の規律(「経験の事実」=ステレオタイプ断定の回避)

現行 line と同じ**一人称・行動の事実**で書き、属性による断定(「若者は〜」「外国人は〜」)を避ける。

| 悪い例(断定) | 良い例(経験の事実・一人称行動) |
|---|---|
| 「若者はSNSばかり信じる」 | 「気になることがあると、まずスマホで現地の投稿や短い動画を探して状況をつかもうとする。」 |
| 「高齢者はデジタルに弱い」 | 「大事な知らせは、テレビや駅・行政のアナウンスで確かめてから動く習慣がある。」 |
| 「連れがいると判断が鈍る」 | 「連れと一緒なので、はぐれないよう皆と同じ方へ動きがちだ。」 |

- worldview offset は**付けない**(慎重): デマ感受性(MIST)は年代差があるが「SNS一次派=だまされやすい」と固定するのはステレオタイプ。純粋に情報源チャネルの事実に留め、行動差は line を読んだLLMに委ねる(nature-line方針)。

### 6.4 計測可能性(observer)とR1整合
- **観測**: 第2軸群idと `drill_exp` 等のメタは agent 属性/イベントに素通しで乗る(現行 `ontology_group` が既に L1 イベントに出る=`simulation.py:638-639`)。observer で**群別**に避難タイミング分布・デマ(labeling/transmission)再送率・情報イベント接触・組織核参加を集計できる。
- **R1整合**: 第2軸割当も persona id のみの関数(traits/k非参照)=因子と直交。age を直読しない(composition で年代分布を近似)=persona id純関数性も保つ。既定OFFでゴールデン維持。

### 6.5 A/B設計例(精密予測の使い方)
- 情報行動軸: `stochastic` の `info_sns` 比率を 0.4↔0.8 で振り、「SNS一次派の割合→初動速度とデマ拡散幅→街の反応」を計測。
- 訓練軸: 日本人群の訓練句を入/切で振り、「訓練文化の有無→避難率・出口分散」を計測(OR=1.99が目標帯の接地)。

---

## 7. 出典(webリサーチ・実在確認済み)

各URLは並行リサーチの各エージェントが WebSearch/WebFetch で実在確認したもの。**[本文確認]** は本文まで取得し数値照合、無印は検索でURL実在・書誌一致を確認(本文細部は要ダブルチェック)。実在の個人名は伏せている。

### 防災心理(クラスタA)
- 正常性バイアス(80%・9/11の70%が避難前に会話): https://en.wikipedia.org/wiki/Normalcy_bias 〔本文確認〕
- 東日本大震災の避難意思決定(訓練・家族所在別の避難確率): https://findingspress.org/article/77365-evacuation-decisions-during-the-great-east-japan-earthquake 〔本文確認〕
- 訓練参加の避難率 OR=1.99(IJDRR 2018): https://www.sciencedirect.com/science/article/abs/pii/S2212420917303710 / ミラー https://ui.adsabs.harvard.edu/abs/2018IJDRR..28..206N/abstract
- 訓練群の避難時間・出口分散(ABM): https://pmc.ncbi.nlm.nih.gov/articles/PMC7918431/ 〔本文確認〕
- PADM(Lindell & Perry 2012): https://pubmed.ncbi.nlm.nih.gov/21689129/ 〔本文確認(抄録)〕
- 緊急地震速報への防護行動(約35%): https://ouci.dntb.gov.ua/en/works/7Xy0Er04/ 〔本文確認〕
- 観光客vs住民の避難(鎌倉ABM): https://www.sciencedirect.com/science/article/abs/pii/S2212420917300158 / https://www.sciencedirect.com/science/article/pii/S0967070X24002063

### リスク認知・情報行動(クラスタB)
- 総務省 令和3年版 情報通信白書(メディア信頼度 新聞61.2%/テレビ53.8%/SNS「信用できない」27.5%): https://www.soumu.go.jp/johotsusintokei/whitepaper/ja/r03/html/nd125220.html 〔本文確認〕
- 防災白書 令和5年版(災害情報入手の年代逆転 18–29歳SNS76.6%>TV73.8%・70歳+TV91.9%): https://www.bousai.go.jp/kaigirep/hakusho/r05/honbun/t1_2s_06_00.html 〔本文確認〕 / 一次: https://survey.gov-online.go.jp/r04/r04-bousai/2.html
- SNS利用率の年代差(総務省 令和7年白書): https://www.soumu.go.jp/johotsusintokei/whitepaper/ja/r07/html/nd111120.html
- デマ拡散の非対称性(Vosoughi, Roy & Aral 2018, Science 359:1146): https://www.science.org/doi/10.1126/science.aap9559 / https://politics.media.mit.edu/papers/Vosoughi_Science.pdf
- デマ感受性MIST(Maertens et al. 2023, Behav Res Methods; 年代差): https://link.springer.com/article/10.3758/s13428-023-02124-2 / 数値解説 https://www.cam.ac.uk/stories/misinformation-susceptibility-test 〔本文確認〕
- 熊本地震「ライオン脱走」デマ(1時間で2万超RT・日本初逮捕): https://www.itmedia.co.jp/news/articles/1607/21/news087.html
- リスク認知の心理測定パラダイム(Slovic 1987解説): https://www.thepumphandle.org/2013/01/16/how-do-we-perceive-risk-paul-slovics-landmark-analysis-2/
- 文化理論メタ分析(Xue et al. 2014, JEP; 67効果量・15,660名): https://www.sciencedirect.com/science/article/abs/pii/S0272494414000619
- やさしい日本語 認知度29.6%: https://www.nikkei.com/article/DGXMZO64289290W0A920C2CE0000/
- 訪日客の意思疎通困難15.2%(観光庁受入環境調査): https://www.mlit.go.jp/kankocho/news08_00022.html

### 文化次元・群衆行動(クラスタC)
- Hofstede UAI国別スコア: https://www.researchgate.net/figure/Uncertainty-Avoidance-UAI-Scores-and-Rankings-for-70-Countries_tbl1_288964749
- 生態学的誤謬(Brewer & Venaik 2014): https://journals.sagepub.com/doi/abs/10.1177/0170840613517602
- 共有アイデンティティと集合的レジリエンス(Drury): https://pubmed.ncbi.nlm.nih.gov/18789185/ 〔本文確認〕 / https://www.tandfonline.com/doi/abs/10.1080/10463283.2018.1471948
- パニック神話の否定(Clarke 2002, Contexts): https://journals.sagepub.com/doi/abs/10.1525/ctx.2002.1.3.21
- 馴染み出口への移動(Sime 1985, Environment and Behavior): https://journals.sagepub.com/doi/10.1177/0013916585176003
- 社会集団と避難反応時間(連れあり1.88秒vs単独1.21秒, n=108): https://pmc.ncbi.nlm.nih.gov/articles/PMC4364745/ 〔本文確認〕
- 傍観者効果/煙部屋(単独75%→サクラ同席10%): https://en.wikipedia.org/wiki/Bystander_effect
- 選好対人距離42か国(Sorokowska et al. 2017): https://journals.sagepub.com/doi/abs/10.1177/0022022117698039
- 群衆密度LOS(Fruin 5→6→7人/㎡): https://www.gkstill.com/Support/crowd-flow/fruin/Fruin2.html 〔本文確認〕

### 都市社会学・人口統計(クラスタD)
- 渋谷 滞在人口・来街年代・流入元(RESAS): https://magazine.tempoly.jp/notice/shibuya-resas-sakata/
- 渋谷区 昼間人口・昼夜比2.39(国勢調査): https://www.city.shibuya.tokyo.jp/kusei/kuni_kikamtokei/kokusei_cyosa/01kokusei_r2.html
- 馴染み出口71%(exit familiarity): https://www.sciencedirect.com/science/article/abs/pii/S0925753516306038
- 訪日消費 国籍別(欧米豪が平均1.6–1.7倍・団体vs FIT): https://www.mlit.go.jp/kankocho/content/001764510.pdf / 解説 https://yamatogokoro.jp/inbound_data/55887/ / 渋谷が訪問先1位 https://honichi.com/news/2024/07/31/tokyo-inbound-report202406/
- 歩行速度実測(高齢者): https://www.ncgg.go.jp/ri/advice/52.html / 車椅子混合群集: https://arxiv.org/pdf/1912.07941
- 社会集団の歩行速度(2人組30%遅い・4人組17%, Moussaïd 2010): https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0010047 / https://arxiv.org/pdf/1003.3894

### 時間生物学・生活制約(クラスタE)
- クロノタイプ分布(朝25%/中間50%/夜25%・20歳夜型ピーク, Roenneberg): https://cet.org/wp-content/uploads/2017/10/Roenneberg-2004-CB.pdf / https://www.nature.com/articles/srep45874
- 夜型×飲酒/social jetlag: https://academic.oup.com/sleep/article/41/2/zsx202/4718366
- 職業×リスク許容/感情労働: https://www.sciencedirect.com/science/article/pii/S0378426624002437 / https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6465590/
- 訪日菜食者約128万人・約5%(本文確認): https://www.travelandtourworld.com/news/article/vegetarian-travelers-face-limited-choices-as-japan-falls-short-in-catering/ 〔本文確認〕 / 訪日ムスリム https://www.japan.travel/en/guide/muslim-travelers/
- ペット同伴避難(16.2%が避難せず・カトリーナ44%): https://pmc.ncbi.nlm.nih.gov/articles/PMC5551593/
- 世代差メタ分析(差ほぼゼロ, Ravid et al. 2025, JOB): https://onlinelibrary.wiley.com/doi/10.1002/job.2827 / APC識別問題 https://academic.oup.com/book/26877/chapter/195941916
- 障害者の震災死亡率2倍(東日本, 本文確認): https://www.dinf.ne.jp/doc/english/twg/escap_121031/fujii.html 〔本文確認〕 / 聴覚障害と早期警報 https://link.springer.com/article/10.1007/s11069-024-06719-6

---

## 8. 未確認事項(事実と推測の区別)

- **本文まで確認できた強い数値**: 内閣府 災害情報入手の年代逆転(18–29歳SNS76.6%>TV73.8%・70歳+TV91.9%)、総務省 令和3年白書のメディア信頼度、MIST年代差、訪日菜食者約128万人・約5%、障害者震災死亡率2倍、社会集団の避難反応時間(1.88秒vs1.21秒)、Fruin密度閾値。これらは軸設計の実証コアに使える。
- **検索確認のみ(本文はペイウォール/403/画像PDF等で未取得)**: 訓練OR=1.99(検索で数値2回一致=信頼度高だが本文一次確認は未達)、Vosoughi「虚偽70%多く拡散」、文化理論メタ分析(67効果量)、馴染み出口71%、Moussaïd集団速度、観光庁年次報告書の国籍別網羅表。数値の一次確認が必要なら該当PDF/論文本文の追加取得を推奨。
- **未確認の具体数値**: 観光客の避難所到着時間差(分)、緊急地震速報レビューの効果量、共有アイデンティティ→援助の効果量(定性研究が主)、helper/leader/follower比率、日本人一般の朝型/夜型%の決定的統計。いずれも方向性は文献支持ありだが効果量は要追加リサーチ。
- **機構的推測(実装検証は次wave)**: §6.1の第2軸スキーマ・`seed_offset` による独立ハッシュ・2行注入は**設計案**であり、実装時にゴールデンL1バイト一致(既定OFF)と決定論(resume/replay一致)をpytestで確認する必要がある。本waveでは実装・conf変更を行っていない。
