# 現実ギャップ全実装 マスタープラン(第8バッチ 2026-07-07〜)

> 依頼(ユーザー 2026-07-07): 振り返りで挙げた現実とのギャップは「渋谷の再現に必要なイベント・仕組みばかり」。
> **全ての実装を任せる**。加えて (a) 日付の初期条件をユーザーが設定可能に、(b) OFF機能を本番シミュに組み込む
> (全機能ONスモーク→機能セット決定→一括ON)、(c) 本番の初期条件を決める仕組み、(d) サーバー実行の是非リサーチ。
> 体制=Fable5計画・検収 / Opus4.8実行。原資料: [social-life-gaps.md](social-life-gaps.md) / [../retrospective-2026-07-07.md](../retrospective-2026-07-07.md)。

## 0. 全バッチ共通の鉄則(既存の実験設計を保護)
- **既定 OFF でバイト一致**: 全新機能は config で既定 OFF。OFF 時はプロンプト・イベント列・乱数消費が従来と1バイトも変わらない。
- **新 stream のみ / 決定論**: 新しい乱数は named stream を新設(既存 draw 順に挿入しない)。可能な限り決定論(RNG不要)。
- **R1(k非依存)**: 内面変数の入力は観測イベントのみ。LLM 呼び出し回数を k に依存させない。
- **R9 / no-fingerprint**: 因子語は `factors/` と src/society 直下モジュールのみ。engine/cognition/world には不透明数値だけ渡す。
- **新イベント種は schema.py 登録**(steward=Fable5 が波ごとに事前登録し並列衝突を避ける)。
- 検証=pytest(ゴールデン緑=OFFバイト一致)+ mock 短ラン。コミットしない。**実装はディスク実在+Fable5 自身の pytest で検収**。

## 1. 既定ON化と初期条件の設計(ご要望 b/c/a を統合 = 本番プロファイル方式)
**判断: config.yaml 本体の既定は OFF のまま、本番用プロファイル `conf/production.yaml` で全機能ON+初期条件を設定する。**
理由: ゴールデン(`tests/data/golden_baseline_l1.json`)は「全 seam が no-op」を固定する回帰ガード。本体既定を ON にすると
このガードが壊れゴールデン再生成が要る。プロファイル方式なら**ゴールデン再生成なし**で「本番シミュに全機能を組み込む」目的を達成し、
casual/実験ランは従来どおりクリーン。
- `conf/production.yaml`: 全リアリズム機能 ON(行政/娯楽/組織/欲求/暦/天気/通勤/感情/スケジュール + 本バッチの新機能)。**実験ノブ**(rewards/null_series/compute_matched/agentic_pull/scenario shock/labeling.mode/y_weights)は**OFFのまま**(k 実験でラン毎に統制するため)。
- **初期条件を決める仕組み(c)**: `conf/production.yaml` に `run.n_agents / n_steps / seed / world.calendar.start_date` を集約。`scripts/run.py --profile production` で読む。
- **日付の初期条件(a)**: `world.calendar.start_date` を settable(既に config 化済)+ **`start_date: "auto"` で実行開始日=現実の当日**に解決する option を calendar.py に追加。本番開始日を初日にできる。
- **手順(b)**: 全リアリズム機能 ON の統合スモーク(健全性確認)→ 機能セット確定 → `conf/production.yaml` 完成。ゴールデンは本体OFFのため無傷。
- これは**全ギャップ波の完了後**に最終整備する(各波が config ブロックを足すので、最後にまとめて production プロファイルへ集約)。

## 2. ギャップ実装の波(高関連度=keystone 創発に効く順。各波=1 Opus バッチ、共有配線=Fable5 steward)
> 共有ファイル(scheduler/simulation/config/schema/factors/economy/net)が競合するため**波は直列実行**。schema 事前登録と config 集約は Fable5 が担当。

### Wave G1 — 経済的生活圧(関連度高・小〜中)★最初
- **相対的剥奪(relative deprivation)**: `factors/update.on_relative_deprivation`(on_money_pressure の隣)。engine が参照集団(同席/近傍で最近見た他者)の所持金 median を算出し、自分がそれを下回る量=不透明 magnitude を渡す→grievance+(1日1回・決定論)。**個体の相対的地位で grievance に個体差が復活=飽和を破る**。係数 `relative_deprivation_grievance` 既定 0。
- **固定費(光熱費・サブスク)**: economy.py に家賃(既存 rent)以外の定期固定費。日次/月次の spend。既定 0。
- 触るファイル: economy.py, factors/update.py(+registry), engine/scheduler.py(日次 phase・参照集団算出), conf, schema(spend/state_update 再利用)。

### Wave G2 — 社会関係の質(関連度高・中)
- **関係の深化段階**: 関係台帳に質的 tier(知人→友人→親友、恋人)を交流回数×valence から導出。
- **断絶/喧嘩/絶交**: ネガ交流・長期不在で関係が負遷移(現状は蓄積のみ)。
- **派閥/内外集団**: グループ帰属の分極(psych collective の拡張)。
- **評判/信頼**: 個人の評判スコアを口コミ/SNS で伝播。
- 触るファイル: agents/memory.py(relations), 新規 relations.py(src/society直下), factors, net, conf, schema(relation_tier/relation_break/reputation)。

### Wave G3 — 制度改変の3ルート(関連度高・中〜大)
- **労働争議/組合**: 職場同僚に限定した集合行為(organizations × tools/collective の新提案型)。
- **選挙/投票**: propose の民主的ルート(署名→投票機構)。
- **警察/条例執行**: 公務員(警察官=既存 civic)による制度DSLルール違反の執行・抑止。
- 触るファイル: tools.py, rules.py, government.py, world/scenario.py, conf, schema。

### Wave G4 — 文化カレンダー・群集(関連度高・中)
- **年中行事/祝日**: calendar に命名年中行事(正月/ハロウィン/年末)→行動・流入の修飾。祝日は既存 holidays を活用。
- **定例イベント**: 会場集客の外生リズム(制度DSL weekly_event を活用)。
- **ハロウィン型群集(渋谷固有)**: scenario 駆動の大規模自然集会(流入増+スクランブル空間集中)=世界改変・規制の実舞台。
- 触るファイル: world/calendar.py, world/scenario.py, conf, schema(annual_event/crowd_surge)。

### Wave G5 — キャリア転換(関連度高・中)
- **転職/失業/求職**: 職の喪失・変更(organizations 再配属・収入変化・時間余剰+grievance)。
- **起業転換**: open_venture→本業を辞める完全転換(現状は副業)。
- 触るファイル: economy.py, organizations.py, tools.py, conf, schema(job_change/unemployment)。

### Wave G6 — 情報環境の非対称(関連度高・中)
- **アルゴリズム推薦/エコーチェンバー**: TL に意見整合バイアス(分極の加速器)。
- **インフルエンサー非対称/バイラル**: フォロワー非対称・影響加重(reshare は既存)。
- **フェイク/炎上**: 誤情報・訂正・炎上ダイナミクス。
- 触るファイル: net/internet.py, opinion.py, conf, schema(feed_rank/viral/misinfo)。

### 後続波(中〜低関連度。G1-G6 完了後)
世帯・家族・同居 / 健康・疲労・病気 / 恋愛・パートナー / 犯罪・迷惑行為 / 医療受診 / 店舗の開閉・在庫・動的価格 /
観光客・多言語 / 災害ショック / 都市再開発 / 趣味・サブカルチャー / 感情の離散ラベル(affect本格版) / 長期目標(schedule本格版)。

## 3. 実行順とマイルストン
1. **サーバー実行の是非リサーチ**(Opus・docsのみ・独立=今すぐ並列)→ ユーザー判断用。
2. **Wave G1 → G2 → … → G6**(直列。各波: Opus実装→Fable5精査→全体pytest緑)。
3. 各波の後、Fable5 が config ブロックを本体(既定OFF)へ集約 + schema 事前登録。
4. G 波完了後: **本番プロファイル `conf/production.yaml` + start_date auto + 初期条件集約**(ご要望 a/b/c)。全機能ON統合スモークで健全性確認。
5. 後続波(中〜低)を順次。
6. devlog 追記・retrospective 更新。

## 4. 検収ゲート(各波共通)
- ゴールデン(test_scenario)緑 = 既定OFFバイト一致。
- 新機能の OFF==純粋既定 の L1 一致テスト。
- 決定論(ON同士2回一致)。R1 呼数不変(FixedLLM ON==OFF)。
- 全体 pytest 緑。mock 短ランで新イベントが出て落ちない。
