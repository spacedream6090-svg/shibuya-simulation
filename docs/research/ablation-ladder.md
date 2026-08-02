# アブレーションの梯子 L0〜L4 — 「LLM 由来の知的振る舞いが集団結果を生んでいるか」の検証装置

作成: 2026-08-03(第89バッチ)
正典: `docs/plans/source/design-discussion-20260802.md` §1 /
      `docs/plans/dual-mode-observe-verify-plan.md` §2(第78行)/
      `docs/plans/dayplan-engaged-plan.md` 第89

---

## 0. 何を測る装置か

この分野の検証は未成熟で、多くの研究が「もっともらしく見えるか(believability)」の主観評価に
依存している(主要サーベイでは 35 本中 22 本)。「人を再現できたか」はそのままでは検証不能なので、
**「どの観測量が・どの水準で・どの許容誤差で一致するか」** に分解する必要がある。

ルールベースと LLM の差を議論ではなく測定するために、**知能の水準を段階化した梯子**を敷く。

> マクロ指標が **L0 から L4 へ単調に変化する**なら、LLM 由来の知的振る舞いが集団結果を
> 生んでいる証拠になる。単調でなければ、その指標は LLM の知能ではなく**別の何か**
>(呼び出しが起きること自体・プロンプトの書式・乱数の消費量・エージェント数)で説明される。

梯子の要は **L1 = プラセボ**である。L0(ルールのみ)と L2(小型 LLM)の差には
「LLM を呼んだ」以外にも「プロンプトを組んだ」「トークンを消費した」「JSON を返した」という
**中身と無関係な違い**が全部乗っている。L1 はそれらを**全部そのままにして中身だけを壊す**ので、
L1↔L2 の差だけが「文脈とペルソナを正しく読んだこと」に帰属できる。

---

## 1. 梯子の対応表

| 水準 | 意味 | 実装 | LLM 呼数 k | プロンプト | 乱数消費 |
|---|---|---|---|---|---|
| **L0** | ルールのみ | `ablate.llm_off: true` | **0** | 組まれない | 既存 stream のみ |
| **L1a** | プラセボ: 文脈シャッフル | `ablate.context_shuffle: true` | L2 と同一構造 | 書式同一・**中身が他人のもの** | +専用 stream のみ |
| **L1b** | プラセボ: ペルソナ入れ替え | `ablate.persona_swap: true` | L2 と同一構造 | 書式同一・**ペルソナが他人のもの** | +専用 stream のみ |
| **L1c** | プラセボ: 文脈遮断 | `ablate.context_sever: true` | L2 と同一構造 | 書式同一・**中身が "…"** | 追加なし |
| **L2** | 小型モデル | `model.mind.pool` に 3B 級を 1 本 | — | 正しい | — |
| **L3** | 中型モデル | `model.mind.pool` に 7〜8B 級を 1 本 | — | 正しい | — |
| **L4** | 大型モデル | `model.mind.pool` に 13〜14B 級を 1 本(または `mind.tiers.high`) | — | 正しい | — |

補足

- **L0** は第78バッチ。ルールは**既存のものだけ**(`routine.decide` = 既存のニーズ充足 +
  POI 選好)で構成し、新しい凝ったヒューリスティックは足していない。比較のベースラインなので
  素朴であることに価値がある。
- **L1** は第89バッチ。3 種は**同一軸**の条件なので**同時 ON にできない**(構築時 ValueError)。
  別々のランとして回し、3 本を並べて「何を壊したときにどの指標が落ちるか」を見る。
- **L2〜L4** は第88バッチの `model.mind`(1 エージェント 1 モデル固定)で構成する。
  梯子として使うときは **pool に 1 本だけ**入れて人口全体を同一モデルにする
  (混成 fleet は多様性の実装であって知能水準の階段ではない — 混ぜると水準が定義できない)。
  モデルの最終ショートリストは **DP-U2(ユーザー判断待ち)**。
- L2〜L4 は `repro_tier=journal`(LLM の自由文を消費する)。L0/L1 は全て `strict`
  = 決定論だけで挙動が決まるので、`run.mode=verify` でも走る。

---

## 2. プラセボ L1 の 3 種 — 何を壊し、何を保つか

|  | ペルソナ節 | 文脈節(他者由来) | 世界状態(記憶・語彙・関係) | プロンプト書式 | LLM 呼の発生点 |
|---|---|---|---|---|---|
| `context_shuffle` | **保つ** | **他人のものに差し替え** | 保つ | 保つ | 不変 |
| `persona_swap` | **他人のものに差し替え** | 保つ | 保つ | 保つ | 不変 |
| `context_sever` | 保つ | **"…" に潰す** | 保つ | 保つ | 不変 |

**触る節の一覧**(= 監査用の唯一の源は `src/society/ablate.py` の `SECTIONS`):

`知っている言葉:` / `直近の出来事:` / `記憶に残っていること:` / `ふと思い出したこと:` /
`間柄:` / `同席の身近な人:` / `近くにいる人:` / `タイムライン:` / `直前のやりとり:` /
返答の状況行 `状況: ○○に話しかけられた:「…」。`

**触らないもの**(意図的な除外。理由は `ablate.py` のコメントに逐一記載)

- 自分由来 …… 自分の理解(内省より)/ 最近の自分 / あなたの考え / 昨日までの日記 /
  あなたがさっき言ったこと / 馴染みの場所 → 「自分の状態は保持」の約束
- 物理世界 …… 時刻 / 場所 / いま / 気分 / 周りにある店 / 天気 / 日付 → 「世界状態は正しいまま」
- 全員共通の環境放送 …… 年中行事 / 災害 / 広告 / 取り決め / 街の動き / 群衆(k 非依存)
- 指示文 …… 所持ツール / 監視仕様 / engaged の終結宣言路 / 状況(social,post,dm,solo)/ 驚き
  → 書式を壊すと**課題そのものが変わる**ので触らない
- 中身を持たない固定文 …… 評判行「あなたは街でそこそこ名前が知られている」

### 2.1 `context_sever` と第78 `propagation_off` の違い(混同禁止)

| | propagation_off(第78) | context_sever(第89) |
|---|---|---|
| 遮断する側 | **送り手** | **受け手** |
| 世界状態 | **変わる**(他者の記憶・語彙・信念・TL に書かれない) | **1 バイトも変わらない** |
| 受け手のプロンプト | 節が**消える**(行ごと出ない) | 節は**残る**(中身だけ "…") |
| 測る因果 | 伝播そのもの(専門化スコアの帰無モデル) | 文脈の利用(読めない文脈は行動を変えるか) |

両者は**併用不可**(構築時 ValueError)。重ねると「消えた節」と「潰した節」を区別できず、
差分の帰属先が失われる。

### 2.2 なぜ入れ替えを**対合**にするか(persona_swap)

割当を A↔B の相互交換(involution)にすると写像が全単射かつ自己逆になり、
**人口全体のペルソナ分布が完全に保存される**。片方向の置換だと「人気ペルソナ」が偏って増え、
結果の変化が「分布が変わったせい」なのか「人格と行動の結びつきを壊したせい」なのかを
分離できなくなる。奇数人口では最後の 1 人だけが自分自身へ写る(= 交換なし。
`summary.placebo.persona_selfpair` に出る)。

### 2.3 正直な宣言(fingerprint_risk = **known**)

3 種とも「当人から観測できる差分」を**意図的に作る**条件である。
**中身が入れ替わればエージェントの応答は変わり、世界も変わる。それが目的**
(変わらなければプラセボとして無意味)。隠す方法は原理的に存在しないので registry へ
`known` として登録し、`run_manifest.json` の `ablate.placebo` と `summary.placebo` に
「壊した量」(書き換えた節の件数・ペルソナ交換数・対合が成立したか)を必ず残す。

観測されうる不自然さの具体:

- `context_shuffle` … 見覚えのない出来事・その場に居ない人の名前・噛み合わない直前のやりとり
- `persona_swap` … 自己紹介文と自分の記憶・関係・持ち物・場所の食い違い
- `context_sever` … 節はあるが中身が無い状態が続く

### 2.4 実装上の限界(隠さず書く)

1. **ドナー枯渇**: `context_shuffle` は「同一ラン内の直近 32 件の同種節」からドナーを引く。
   ラン開始直後はその輪が空なので、最初の数プロンプトだけ `context_sever` と同じ
   プレースホルダへ後退する。件数は `summary.placebo.shuffle_starved` に出る
   (0 でないラン = 冒頭に L1c 相当が混ざったラン)。
2. **pool × persona_swap**: 対合表は**構築時の名簿**から組む。`persona_pool` の日境界
   ローテーションで後から実体化した個体は表に無く、一方向ドナーへ後退する。
   `summary.placebo.involution=false` で判る。pool を使う梯子では対合性を保証しない。
3. **呼数の間接ドリフト**: 呼び出し**サイト**は 1 つも増減しないが、プロンプトが変われば
   応答が変わり、応答が変われば発火ドライブが動くので、実測の呼数は動く
   (mock 40体288step で `context_shuffle` **-14.0%** / `persona_swap` -1.8% /
   `context_sever` -3.1%。第78 `propagation_off` の +1.61%・`experiment.flat_traits` と
   同じ間接経路で、こちらは「知っている言葉」節まで壊すぶん振れ幅が大きい)。
   ★これが**応答経由の間接効果だけ**であることは、プロンプト内容を捨てる LLM プロキシの下で
   ON/OFF が呼数完全一致・L1 バイト一致になることで確定済み
   (`tests/test_placebo.py::test_call_count_is_exactly_equal_under_prompt_blind_llm`)。
   **k を揃えたい比較では `k.compute_matched` 対照を併用すること。**

---

## 3. 実行レシピ

### 3.1 単調性検証の 1 セット(同一 seed・同一人数・同一日数で 7 本)

```bash
# 共通の土台(人数・日数・seed・観測はすべて同じにする)
BASE="run.seed=42 run.n_agents=200 run.n_steps=864 run.mode=observe"

# L0: ルールのみ
python scripts/run.py $BASE run.name=ladder_L0 ablate.llm_off=true

# L1a/L1b/L1c: プラセボ(3 種は必ず別ラン。同時 ON は ValueError)
python scripts/run.py $BASE run.name=ladder_L1a ablate.context_shuffle=true
python scripts/run.py $BASE run.name=ladder_L1b ablate.persona_swap=true
python scripts/run.py $BASE run.name=ladder_L1c ablate.context_sever=true

# L2/L3/L4: モデルサイズの階段(pool に 1 本だけ入れて人口全体を同一モデルにする)
python scripts/run.py $BASE run.name=ladder_L2 \
  model.mind.enabled=true '+model.mind.pool=[{backend: vllm, name: small-3b,  base_url: "http://localhost:8000", weight: 1}]'
python scripts/run.py $BASE run.name=ladder_L3 \
  model.mind.enabled=true '+model.mind.pool=[{backend: vllm, name: mid-8b,    base_url: "http://localhost:8001", weight: 1}]'
python scripts/run.py $BASE run.name=ladder_L4 \
  model.mind.enabled=true '+model.mind.pool=[{backend: vllm, name: large-14b, base_url: "http://localhost:8002", weight: 1}]'
```

**mock だけで配線を通す**(GPU 不要・回帰用):

```bash
for m in context_shuffle persona_swap context_sever; do
  python scripts/run.py run.seed=42 run.n_agents=40 run.n_steps=288 \
    model.backend=mock run.name=placebo_$m ablate.$m=true
done
```

### 3.2 読み方(禁止事項つき)

1. **単独ランの数値に合否を付けない。** アブレーションは「差分でしか主張しない」ための装置。
2. 各水準について `summary.placebo`(L1)/ `summary.mind`(L2〜L4)/ `manifest.ablate` を
   必ず並べて出す。**`sections_shuffled` や `persona_swapped` が 0 のランは
   プラセボとして無効**なので単調性の主張に使ってはいけない。
3. マクロ指標は少なくとも次を見る(第91 の退行シグナルと同じ列):
   行動分散 / 訪問地点エントロピー / 発話の語彙エントロピー / n-gram 重複率 / 発火率 /
   会話統計(発話長・あいづち率・不同意率・話題持続長)。
4. **単調でない指標を隠さない。** 「合った指標と合わなかった指標を両方提示する」ことが
   この分野で誠実な検証である(正典 §1)。
5. 呼数 k がずれるので、k に敏感な指標は `k.compute_matched` 対照を併用する。

### 3.3 バッテリー(第90)との関係

第90 のモデル人間らしさテストバッテリーは**プラセボ(テンプレ応答)を 1 本混ぜ、
それが全テストで最下位に沈むことをテスト自体の健全性確認に使う**。本梯子の L1 は
**同じ役割をシミュレーション本体の側で果たす**もので、対象が違う:

- 第90 のプラセボ …… **モデル単体**の応答品質を測るハーネス上の対照
- 本梯子の L1 …… **集団結果(マクロ指標)**に対する対照

両者は独立に走り、両方でプラセボが下位に沈むことが「テストもシミュレーションも
健全に測れている」の二重確認になる。

---

## 4. 実装の所在

| 何 | どこ |
|---|---|
| L0 + 第78 の 4 種 | `src/society/ablate.py`(前半)/ `conf/config.yaml` の `ablate:` |
| L1 プラセボ 3 種 | `src/society/ablate.py` の `Placebo` / `SECTIONS` |
| 唯一の作用点 | `src/society/cognition/deliberate.py` `build_prompt` 末尾 3 行 |
| 結線 | `engine/simulation.py`(`make_placebo` / `attach_agent` / `finish_placebo`) |
| checkpoint | `engine/checkpoint.py` の `runtime.placebo_state` |
| 再現性等級の宣言 | `src/society/registry.py`(`ablate.context_shuffle` ほか 2 件) |
| L2〜L4(モデル固定) | `src/society/mind.py` / `conf/config.yaml` の `model.mind` |
| テスト | `tests/test_placebo.py` / `tests/test_ablate.py` / `tests/test_mind.py` |
