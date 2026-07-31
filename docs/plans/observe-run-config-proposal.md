# 本選10日ラン(観察ラン)の ON 構成提案

> ステータス: **提案(ユーザー承認待ち=OBS-U1)**。2026-08-01 作成。
> 対象: 本選 10 日ラン(8/16〜8/26・production/daily 系プロファイル土台)。
> 最終確定は 8/12-14 フリーズ期間(σ/θ の実 LLM 再較正後)。ここでは方針の承認を求める。

## 1. 推奨 ON セット(世界を変えるもの=opt-in)

| トグル | 推奨 | 理由 / 注意 |
|---|---|---|
| run.mode: **observe** | ON | 全等級許可の宣言・manifest に記録(第72) |
| weather.mode: **generated** + extra_prompt_fields | ON | 現実の8月の統計構造(連続猛暑)を strict 等級で。猛暑をエージェントに見せる行も ON(世界の事実) |
| **cognition.channels + fire + watch + g_update** | ON | 認知プログラムの本命。g_init=**persona**・theta_scale=実 LLM 再較正値(8/15-16)。**発火数が予算内に収まることをパイロットで確認してから最終 GO**(第83: watch ON は較正27倍差) |
| **env.feedback** | ON | 環が閉じる=創発主張の土台。閾値は本番規模向け仮値のまま(渋谷駅統計較正は本選後) |
| **beliefs.enabled + verify_actions** | ON | 記録しないと失われる系。誰が確かめに行くかが観測対象 |
| labeling.norm_stage / place_binding | ON | 観測のみ / 造語の場所束縛(第69・見せ場) |
| freedom.undefined_register + explicit_nothing + open_actions | ON | 行動空間の外へ出る個体・沈黙の観測 |
| relations.dunbar | **条件付き ON** | pool dehydrate の台帳20件切りと干渉(第75実測)→ **dehydrate 幅の拡張(小修正)をフリーズ前に入れてから ON**。間に合わなければ OFF |
| relations/joint/schedule/friend_graph/planning ほか既存 ON 群 | production 通り | 変更なし |
| k.writeback: free / controls.mode: **none** | — | 観察ランは対照不要(compute_matched は検証ラン用) |

## 2. 推奨 OFF(観察ランでは使わない)

ablate.* 全部(検証ラン用)/ observer.state_hash(コスト・検証は L1 で)/ experiment.flat_traits / experiment.g_init の flat/noise(F/N/P は別条件ランで=NEW-5)/ cognition.contract(P1 検証済みだが本選は従来経路=変更を1つ減らす)/ world.mod(反実仮想は本選後)。

## 3. 判断が要る2点

- **OBS-U2: Δt_move を 1 分にするか**。談話中の思考周期(2分)が Δt=10分に丸められる人工物を第83が実測済みで、細分化の学術的価値は高い。ただし Δt 変更=別世界(乱数列変化)+ログ I/O 約10倍+σ/θ 再較正が全部やり直し。**推奨: 本選本線は Δt=10 維持・GPU 余剰があれば Δt=1 の並行小規模ラン**(比較はラン間で)。
- **OBS-U3: 認知プログラム ON の最終判断を 8/14 に留保**(パイロット実測で発火数が予算超過なら fire だけ OFF に落とす退路。全て既定 OFF 実装なので構成変更は conf のみ)。

## 4. 8/15-16 実 LLM 診断ランでやること(GPU 開放初日)

1. σ_c 再実測(本選 ON 構成・measure_sigma.py)→ 2. θ 再較正(watch ON・calibrate_theta.py・27倍差の解消)→
3. U-10 の確定判定ラン(数百体×20日相当・事前登録凍結後)→ 4. 発火数・呼数の実測から本選の人数を最終確定
(第83: 呼数/人/日は人数不変でない=外挿でなく実測で決める)。

## 5. 運用

毎日 checkpoint(いつ打ち切っても成果)・live_viewer 併走(第77・読み取り専用)・watchdog 併走・
本選中にしか取れない外部データの取得(Metro CrowdNavi・人口マップ・WBGT 等=承認待ち項目)。
