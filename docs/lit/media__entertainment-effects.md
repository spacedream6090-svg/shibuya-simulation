# 娯楽メディア(TV・動画・ゲーム)の効果 — 文献調査とシミュレーション写像

対象: バッチD「テレビ・動画・ゲームなど娯楽の提供」。現代人の生活の再現に不可欠な
在宅娯楽メディアの利用実態と心理的効果を文献から整理し、シミュレーション
(渋谷、1 step = 10分、144 step = 1日)へ写す定量パラメータへ落とす。

原則(本リポジトリの設計契約に合わせる):
- **因果構造のみ文献接地、magnitude は conf で可変**(決め打ち禁止。park_grievance 等と同格の seam)。
- 効果は最小限。気分修復は factors seam(state_update, cause="media")経由でのみ state を動かす。
- LLM を一切増やさない(全て非LLM・決定論)。実在番組・作品名は使わない(架空プールのみ)。

---

## 1. 気分管理理論(Mood Management Theory / Zillmann)

**主張**: メディア選択は感情状態の自己調整に奉仕する。ネガティブな気分の人は、
気分を持ち上げる娯楽的・ユーモラスなコンテンツを選好する(mood repair)。
Zillmann, Hezel & Medoff (1980) の実験で、ネガ気分に誘導された被験者ほど
明るい・喜劇的なTV内容を選んで視聴した。Knobloch & Zillmann (2002) では
ネガ気分の人が気分改善のため明るい音楽を選ぶ傾向を確認。

**シミュへの含意**: 娯楽メディアの利用は「不満(grievance)をわずかに和らげる」
方向の気分修復として写す(セッション終了時に grievance を小さく下げる)。

- 出典: Reinecke, L. "Mood Management Theory." *The International Encyclopedia of Media Effects* (Wiley), DOI: [10.1002/9781118783764.wbieme0085](https://doi.org/10.1002/9781118783764.wbieme0085)

## 2. 利用と満足研究(Uses and Gratifications / Katz)

**主張**: 受け手は能動的で、メディアを「情報(認知)」「娯楽・気晴らし(感情/緊張解消)」
「対人・社会的効用(交際・話題)」「自己確認」といった欲求充足の手段として選ぶ
(Katz, Blumler & Gurevitch 1973)。McQuail, Blumler & Brown (1972) の4分類:
気晴らし(diversion=逃避・感情放出)、対人関係(companionship・social utility)、
自己同一性、環境監視(surveillance=情報探索)。

**シミュへの含意**: 娯楽利用の動機は主に (a) 気晴らし/緊張解消(=気分修復)と
(b) 話題の獲得(=直近視聴タイトルが会話・投稿の文脈になり得る)。後者は
prompt_context フラグ(既定 OFF)で「直近視聴タイトル1行」を発火プロンプト文脈へ
写す(架空タイトルのみ)。

- 出典: Katz, E., Blumler, J. G., & Gurevitch, M. (1973). "Uses and Gratifications Research." *Public Opinion Quarterly*, DOI: [10.1086/268109](https://doi.org/10.1086/268109)

## 3. 時間置換仮説(Time Displacement / Putnam)

**主張**: TV視聴は余暇時間を私的化し、家庭外の対面交流・社会参加(社会関係資本)を
置換する(Putnam *Bowling Alone* 2000)。実証は賛否あり — Moy, Scheufele &
Holbert (1999) の検証では「時間圧力を介した」経路は支持されなかったが、
**視聴時間の市民参加への直接的な負の効果は観測**された(混在した結果)。

**シミュへの含意**: 因果としては robust ではないが、**機会費用としての時間置換**を
最小限に写す = 「メディア視聴セッション中は外出・余暇の外出・SNS閲覧をしない」
(在宅で数 step 消費)。心理効果は付けず、行動選択の占有だけで自然に置換を表現する。

- 出典: Moy, P., Scheufele, D. A., & Holbert, R. L. (1999). "Television Use and Social Capital: Testing Putnam's Time Displacement Hypothesis." *Mass Communication and Society*, DOI: [10.1080/15205436.1999.9677860](https://doi.org/10.1080/15205436.1999.9677860)

## 4. 回復体験(Recovery Experience / Sonnentag & Fritz)+ ゲームと気分・フロー

**主張(回復)**: 余暇による仕事ストレスからの回復は4因子 — 心理的距離(detachment)、
リラクゼーション、熟達(mastery)、コントロール — で説明される(Sonnentag & Fritz 2007)。
在宅の受動的娯楽(TV/動画)は detachment/relaxation に、能動的娯楽(ゲーム)は
mastery/flow に対応しやすい。

**主張(ゲーム)**: ゲームプレイ中に気分が改善する。Vuorre et al. (2024, Oxford OII)
の自然観察(8,695人・67,328セッション・162,325件の気分報告)では、プレイ中の気分は
開始時より平均 **+0.034(0–1 VAS)** 上昇し、その大半は **最初の15分**で生じ、
約 **72%** のプレイヤーが上昇を報告した。Koçak (2024) はゲームが日々のストレス・
気分変動からの回復活動として機能することを示す(長期の大きな効果は限定的)。

**シミュへの含意**: この **+0.034 / 15分** が気分修復 magnitude の実証アンカー。
1 step = 10分、15分 ≈ 1.5 step で効果が飽和する。セッション終了時に grievance を
約 0.03 下げる値を推奨初期値とする(飽和を踏まえ、セッション長には比例させない)。

- 出典(回復): Sonnentag, S., & Fritz, C. (2007). "The Recovery Experience Questionnaire." *Journal of Occupational Health Psychology*, DOI: [10.1037/1076-8998.12.3.204](https://doi.org/10.1037/1076-8998.12.3.204)
- 出典(ゲーム気分): Vuorre, M., Ballou, N., Hakman, T., Magnusson, K., & Przybylski, A. K. (2024). "Affective Uplift During Video Game Play: A Naturalistic Case Study." *Games: Research and Practice* (ACM), DOI: [10.1145/3659464](https://doi.org/10.1145/3659464)
- 出典(ゲーム回復): Koçak (2024). "Recovery from work by playing video games." *Applied Psychology* (Wiley), DOI: [10.1111/apps.12519](https://doi.org/10.1111/apps.12519)

## 5. 日本人の実際の時間量(NHK 国民生活時間調査 2020)

**実態**: 1日にテレビを見る人の割合は全体で 79%(5年前 85% から低下)。
**年層差が大きい** — 16〜19歳は 47%(5割割れ)、20代以下で前回比 約20ポイントの大幅減。
若年層ほどインターネット/動画・ゲームへシフトし、**20代以下ではネット利用時間が
テレビ視聴時間を上回る**。16〜19歳は日中はTVとネットが同程度だが、**夕方以降は
ネットがTVを上回る**。動画視聴は若年層でネット利用時間の1時間以上を占める。逆に
高年層はテレビ視聴が長く、実時間視聴の中心。

**シミュへの含意(年齢・職業プロファイル)**:
- 視聴媒体構成(TV / 動画 / ゲーム)を年齢帯で変える(若年=動画・ゲーム寄り、
  高齢=TV寄り)。
- 利用時間帯は現実的に **夜間帯(在宅後)と起床後の朝**に置く。
- 職業(学生・無職・フリーランス等=自由時間多)で開始確率を微調整。

- 出典: NHK放送文化研究所「2020年 国民生活時間調査」 [https://www.nhk.or.jp/bunken/research/yoron/](https://www.nhk.or.jp/bunken/research/yoron/)
- 出典(分析): 渡辺洋子「新しい生活の兆しとテレビ視聴の今」『放送研究と調査』71巻8号, J-STAGE DOI: [10.24634/bunken.71.8_2](https://doi.org/10.24634/bunken.71.8_2)

---

## 6. 文献 → シミュレーション定量パラメータ 対応表

| 文献/根拠 | 現象 | シミュへの写し方 | パラメータ(実装位置) | 向き |
|---|---|---|---|---|
| Zillmann(気分管理) / Vuorre 2024(+0.034 / 15分) | 娯楽視聴で気分が回復 | セッション終了時に grievance を小さく下げる(factors seam, cause="media") | `factors.media_grievance`(update.py, 既定 **0.0**=無効。推奨 ON 値 **-0.03**) | grievance ↓ |
| Putnam / Moy 1999(時間置換) | 視聴が外出・対面・社会参加を置換 | セッション中は在宅で数 step 占有=外出・余暇外出・SNS閲覧をしない(機会費用のみ、心理効果なし) | セッション長 `media.min_steps`/`max_steps`(既定 2〜8 step = 20〜80分) | 行動占有 |
| Katz(利用と満足) | 娯楽=気晴らし+話題の獲得 | prompt_context ON 時のみ、直近視聴タイトル1行を発火プロンプト文脈へ(架空タイトル) | `media.prompt_context`(既定 **false**。LLMキャッシュキーに影響=独立フラグ) | 文脈付与 |
| NHK 2020(年層差) | 若年=動画/ゲーム、高齢=TV | 年齢帯で媒体構成比を変える(media.py で age から precompute) | `_MEDIUM_WEIGHTS`(youth/mid/senior/elder の tv/video/game 比) | 媒体構成 |
| NHK 2020(利用時間帯) | 夜間帯・起床後の朝 | 在宅かつ朝/夜の時間帯だけセッション開始 | `media.morning_hours`(既定 5–10時)/`media.night_hours`(既定 20–24時) | 時間帯 |
| NHK 2020 / 自由時間 | 学生・無職ほど視聴多 | 職業で開始確率を微調整 | 開始確率 `media.start_prob` × プロファイル倍率(年齢帯・職業) | 頻度 |
| Sonnentag & Fritz / Koçak | 回復は媒体でモードが違う | 効果は grievance 修復に一本化(最小限)。媒体別の差は媒体構成比のみで表現 | (効果は共通 seam。過剰実装を避ける) | — |

### 媒体構成比の初期値(NHK の年層差を写した既定。`media.py` の `_MEDIUM_WEIGHTS`)

| 年齢帯 | TV | 動画 | ゲーム | 根拠 |
|---|---|---|---|---|
| youth(<30) | 0.20 | 0.45 | 0.35 | 若年=動画・ゲーム中心、TV離れ(16–19歳の視聴率47%) |
| mid(30–49) | 0.45 | 0.35 | 0.20 | 中間層。TVと動画が拮抗 |
| senior(50–64) | 0.65 | 0.25 | 0.10 | TV中心へ回帰 |
| elder(65+) | 0.85 | 0.12 | 0.03 | 実時間TV視聴の中心層 |

### 効果 magnitude の実証アンカー

- ゲーム気分改善: **+0.034(0–1 VAS)/ 最初の15分で飽和**(Vuorre 2024)。
  → 逆符号で grievance 修復に写し、`media.py` のセッション長には比例させず(飽和)、
  推奨 `factors.media_grievance = -0.03`(0–1 の state スケールに整合)。
- 既定は **0.0**(seam のみ実装、値は回しながら調律)。park_grievance(-0.008)と同じ
  「因果は接地・量は conf」方針。media の修復はゲームの実証値を根拠に park より
  やや強めに置ける(-0.03)。

---

## 7. 実装との対応(このバッチで導入したもの)

- `src/society/media.py`: 年齢・職業から媒体構成・開始確率・セッション長を precompute
  (economy.py の precompute 前例に準拠。cognition は性格特性を直接読まない=R9)。
  架空タイトルプール(実在作品名なし=R17)。乱数は新 stream **"media"** のみ。
- `src/society/cognition/routine.py`: 在宅×朝/夜の時間帯に TV/動画/ゲームを選択して
  数 step 消費(セッション)。セッション中は外出・余暇・SNS閲覧をしない(時間置換)。
  セッション終了時に factors seam(cause="media")で気分修復。勤務時間帯は仕事優先。
- `src/society/factors/update.py`: `on_media`(grievance 修復)と `media_grievance`
  magnitude(既定 0.0)を追加。既定 0.0 = OFF 時完全不変。
- イベント: `media_use {medium, title?, steps, at}`(schema 登録済み)。全て非LLM。

既定は完全 OFF(`media.enabled: false`)。ON 時のみ挙動が変わる。
