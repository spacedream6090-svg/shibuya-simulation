# 本番ラン最終条件書(2026-08-24・開始GO判断用)

> 作成: 第156補(a7bf3b9)時点。ユーザーのGOサインを得てから起動する。
> 起動後は不介入原則(R1)。監視=毎時モニタ+day-1チェック(devlog第140補)。

## 1. 起動

```
# サーバー(GPU機)・リポ = ~/projects/shibuya-simulation・コード = a7bf3b9
nohup ~/venvs/sim/bin/python -u scripts/run.py \
  --profile conf/finals_observe.yaml \
  run.seed=42 run.seed_auto=false \
  run.name=finals_observe_20260824 \
  engine.batch_llm.enabled=true engine.batch_llm.workers=16 \
  > ~/finals_observe_20260824.log 2>&1 &
```
- オーバーライドは **seed 2キーと run.name・batch_llm のみ**。他は全て finals_observe.yaml の凍結値。
- 起動直前に freeze_config で凍結YAML+sha256を保存(条件の同一性を数字で残す)。

## 2. 規模・時間

| 項目 | 値 |
|---|---|
| 在場人口 | **250,000人**(present_cap)/ 名簿=ペルソナプール**v2**(100万人・8/24現HEAD再生成・第133分岐解決済み) |
| step | 10分/step・**144 step=1日** |
| 日数 | n_steps=1440(10日枠)。**日数可変方針**=提出(8/30 23:59)まで回しデータは随時flush(summary無しでも成果物は残る設計) |
| 開始日時 | シミュ内 **2026-08-22(土) 00:00**(暦固定・natural_start ON=初日から朝計画) |
| seed | **42**(全リハーサル・友人キャッシュ・A/B系譜と同一。init~3分) |
| 速度見込み | 日平均~10-12分/step(深夜4/朝7-8/昼~15/夕方~23分)→ **提出時点~5.5日分** |

## 3. 世界(主要ON機構・全てコミット済み検証付き)

- **地図**: 渋谷実地図 v8(OSM wide・実店舗POI・実入口・信号実測サイクル)
- **物理**: 3ゾーン(スクランブル=ORCA・ハチ公広場/センター街=SFM)・dt 0.1s・**所有=経路到達版**(第155・捕捉99.3%・交差点密度実勢化)・適応dt(ORCA)・近傍cap7・分離16
- **暦**: 土曜開始・census勤務曜日(土50.4%/日25%)・賃金支払い・第148暦根治済み
- **経済**: 組織11,000社・2層在庫(棚/バックヤード)+発注行動(order_on_low)・時間帯価格・見切り・混雑不満(CRWD)
- **社会**: 声の段階(通常5/10m・張り上げ12/20・叫び30/40)・聴衆cap(C2=15・S15=20)・関係台帳tiered退避(友人以上不可侵・上限2000)・ATT注意機構(層A ON)・witness各チャネル・SNS(フォロー網・投稿)・噂・真偽台帳
- **人口**: v2=年齢多様性(0-14歳9.75%・85+3.75%=年齢機構実発火)・非通勤来街74,947人/日(較正帯6-13万に初到達)・週末/平日比0.68・人口動態(転入転出出生)

## 4. ペルソナ(第156・ユーザー発案)

| 項目 | 値 |
|---|---|
| 骨格 | 決定論生成(census台帳駆動・属性+persona文) |
| 肉付け | **全100万人=100.000%**に過去情報2-3文(事前生成・凍結成果物=ランの決定論不変) |
| 生成モデル | L1+L3(コア6.7万)=**Qwen3-32B-AWQ**(rev 0499c3a)/ L2+L4+L5(93.3万)=Qwen3-8B / rescue代替145人=14B(model欄に記録) |
| 効果(A/B実測) | 語彙多様性 distinct-2/3 **+23〜24%**・480/480計画で応答変化・parse 479/480・**step時間増ゼロ** |
| プロンプト | 自己紹介直後に「これまでのこと: 」節(全purpose共通) |

## 5. LLM

| 項目 | 値 |
|---|---|
| 艦隊 | vLLM 7基: **8B×5(会話)+14B×2(plan/reflect)**・AWQ・revision固定・chat経路・prefix cache・sticky割当 |
| 呼数 | max **300呼/step**・batch 16 workers・実測=step時間への加算ゼロ(計算に埋没) |
| パラメータ | temp 0.7(会話)/0.3(plan)/0.2(recall)・plan 896tok・reflect 768tok・request seed(β11)・journal全記録 |

## 6. 観測・保全

- L1イベント全量(6stepごとflush)・L2毎step・L3日次スナップショット・G観測チャネル(全個体×毎step)・llm_journal(プロンプト+応答全文)・summary provenance(physics/goods/health他)
- **checkpoint=72stepごと(半日)**=resume可能・ディスク3.6TB空き・RSSガード群(第141)
- 監視: 毎時モニタ(step pace・RSS・エラー)+day-1チェック(staffed比・欠品率帯・新規フォロー/日/人・賃金>0・CRWD帯)+閾値アラート

## 7. 開始前の残決定(GO時に確定)

1. **start_date**: 8/22(土)のまま=**推奨**(全リハーサル系譜・週末立ち上がりはday-1監視も楽)/ 8/24(月)へ書き換え(confコメントの「順延したら書き換える」に従う場合・平日朝から始まる)
2. **seed**: 42明示=**推奨**(検証系譜+キャッシュ)/ seed_auto(confの観察ラン思想・ただしinit~2hと系譜切断)
