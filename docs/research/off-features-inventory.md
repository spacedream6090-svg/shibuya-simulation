# 既定OFF機能の全数棚卸し(第37バッチ 2026-07-19・本番ON選定の一次資料)

conf 全キー×src実装×tests突合。詳細な効果/リスクは調査ログ参照。ここでは判断用に凝縮。

## A. 本番ONの判断対象(実装+テスト済み・どのプロファイルでもOFF)

**都市リアリズム系**
| キー | 機能 | ON効果 |
|---|---|---|
| world.vision.enabled | 壁による視線遮蔽(LOS) | 建物内の非現実的な壁越し会話が消える |
| world.traffic.mode: od | 個体化背景交通(信号69基・車線・一方通行295) | 信号が初めて作用。車の挙動が精緻化(重め) |
| transit_ride.bus.enabled | バス路線 | 移動手段+1(合成路線要) |
| ads.enabled | 街頭広告→来店ファネル | dailyは設定済で1フラグ |
| crowd_visual.enabled | 同席者の視覚要約1行 | 記述的規範がプロンプトに(呼数不変) |
| sns_geo.enabled | 伝播に物理距離を記録 | 分析列追加のみ(無風) |

**自由度・創発系(ファウンダー観察の核)**
| キー | 機能 | ON効果 |
|---|---|---|
| freedom.open_actions | LLM自由記述行動 "do" | 行動の自由度↑・価値4軸観測 |
| freedom.p2.move_home/buy/study/partnership/deviance | 転居・消費・学び・交際・無許可出店 | 生活の自己決定+逸脱(deviance=ファウンダー前駆の観察点) |

**認知深化系**
| キー | 機能 | ON効果 |
|---|---|---|
| memory.agentic_pull | 発火/内省時の能動記憶検索 | 想起1行(呼数不変・キャッシュキー変化) |
| worldview.enabled | 主観的世界モデル(期待/可制御性/規範予期) | 日次観測列(乱数ゼロ) |
| psych.sdt.enabled | 自己決定理論(内発/外発の個体差) | 動機の異質性↑ |
| psych.collective.enabled | 集団効力感・SIMCA | 集団帰属→効力感(組織形成観察と相性) |
| psych.lynch.enabled | 都市イメージ(ランドマーク重み) | 行き先が現実の認知地図に寄る |
| lod.input_res.enabled | 情報量の個体差 | R1安全な異質性 |

## B. ONにしない(理由つき)

- prompts.reflect_variety: **丸写し33%の正味悪化**(再ON条件=棄却ガード or reflect 8b化)
- rewards / labeling.mode: open / controls.* / k.writeback≠free: **実験統制ノブ**(交絡の意図的排除)
- drive.firing: logistic / threshold_dist: lognormal: **k掃引の比較基準が動く**(研究本体保護)
- psych.searle: recursion.rules_in_prompt と重複
- media.prompt_context: media本体ON済・これはキャッシュ影響のみ大

## C. 既にON済み(30機能超・判断不要)/ D. 未実装

- C: reflection.deep・calendar/weather・economy一式・government・organizations・relations・
  info_env・health・household・commerce・career・annual・institution_routes 等(全て実装テスト済)
- D: **agent-tier LOD(M3)= 未実装**(router は purpose別のみ・agent_tier は ValueError)。
  model.format の schema モードも未対応。opinion(FJ)は**既定ONであり**OFF候補ではない。
