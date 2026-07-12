# 計画済み・未実装の棚卸し(第24バッチ 2026-07-12)

「計画書は書いたが、コードにはまだ入っていないもの」の全リスト。実装済みコードとの照合済み
(EnvPack・作話メトリクス等は grep で不在を確認)。各項目に出典・待ち理由・工数目安を付す。

---

## A. すぐ着手できるもの(計画確定・ご承認があれば即)

| # | 項目 | 内容(1行) | 出典 | 工数目安 |
|---|---|---|---|---|
| A1 | **計算量削減 E1(タダ飯)** | speculative decoding(無損失~2.8倍)+prefix cache疎通+reflect出力上限の右サイズ化+step内バッチ。全て決定論/R1中立 | [compute-optimization.md](compute-optimization.md) | 1-2日+実測 |
| A2 | **production.yaml に reflect_think:false** | 内省全滅バグの修正1行を本選用プロファイルへ | [pending-decisions.md](pending-decisions.md) 事項1 | 10秒 |
| A3 | **作話の接地率メトリクス** | 発話中の固有名詞のうち実在名の割合を日次系列に。第22の detect_emergence(fiction検出)が骨格を実装済み=集計を足すだけ | reality-levers P2 | 半日 |
| A4 | **内省プロンプト改善** | belief の25%が雛形復唱(「今日の経験からの〜」)→表現の差し替え+書き戻し検収 | 第20バッチ検収メモ | 半日+短スモーク |
| A5 | **LOD M4(運用)** | 手元/本選7GPU/API混載の運用プロファイル+bench.py拡張(tier別tok/s・fallback率) | [multi-model-lod.md](multi-model-lod.md) M4 | 1日・本選前で可 |

## B. 判断・討議が先のもの

| # | 項目 | 内容 | 待ち理由 |
|---|---|---|---|
| B1 | **agent-tier LOD(M3)** | エージェント階層別モデル割当。コードには ValueError ガード済み | **討議待ち**([agent-lod-deepdive.md](../research/agent-lod-deepdive.md) を送付済み。資料の示唆=300体では不要・3k体級の後段レバー) |
| B2 | **新機能のON化** | ads / crowd_visual / worldview / sns_geo / router は**実装済みだが既定OFF**。daily/production でどれを常時ONにするか | 運用判断待ち(実装は完了している=本リストの「未実装」とは別枠) |
| B3 | **計算量削減 E2** | INT4量子化・routineキャッシュ(ブラインドA/B合格が条件) | E1の実測後 |

## C. 実験・検証ラン(器は実装済み・「回すのは待つ」指示に従い停止中)

| # | 項目 | 内容 | 状態 |
|---|---|---|---|
| C1 | **model×k対照 4セル** | 15体×2日×{instruct, abliterated}×k{free, off} | スモーク合格済み・実行待ち |
| C2 | **k実験の再検証** | belief開通後の free/off 再測定。**C1のinstruct側2セルが兼ねる** | [pending-decisions.md](pending-decisions.md) 事項2 |
| C3 | **PIMMUR Unawareness 尋問テスト** | エージェントが「自分はAI」と気づくかの5モデルテスト(手順提案済み) | [pimmur-compliance.md](../research/pimmur-compliance.md) |

## D. 大型構想(計画のみ・コード未着手)

| # | 項目 | 内容 | 出典 | 規模感 |
|---|---|---|---|---|
| D1 | **基盤モデル抽出(EnvPack)** | 渋谷固有部を env.yaml manifest に外出しし「人格などの本質モジュール」と分離。W1-W5(各Waveゴールデン一致が検収)。W5=2つ目の街で実証 | [foundation-extraction.md](foundation-extraction.md) | 数日〜 |
| D2 | **環境自動生成(make_env)** | 地図・交通・合成人口・制度表・語彙の7-stageパイプライン。v0半自動→v1 e-Stat IPF→v2一括。D1が前提。本選の差別化=「渋谷で較正した基盤を他の街に即日展開」 | [environment-autogen.md](environment-autogen.md) | 数日〜 |
| D3 | **自由度 P2(生活の自己決定の残り)** | 移転・消費の高度化・学び・家族形成・軽微な逸脱。P1相当は第17バッチの開放行動 "do" で実装済み | [agent-freedom-plan.md](agent-freedom-plan.md) | 中 |
| D4 | **本選デモ** | 3幕構成(生きている渋谷→ライブ政策what-if→世界を変える人は生まれるのか)。事前分岐ラン方式・介入キュー・worldviewファンチャート | [demo-plan.md](demo-plan.md) | 本選前・中 |
| D5 | **reality-levers P3(本選向け)** | インタビュー接地のサブ集団・27Bモデル・LoRA人格 | [reality-levers.md](reality-levers.md) | GPU依存 |
| D6 | **PLATEAU LOD2 建物(3D)** | 現行はOSM押出しで実装済み。LOD2実建物の導入は設計記録のみ | [3d-visualization.md](../research/3d-visualization.md) | 中・見た目のみ |

## E. 条件付き保留(発動条件を満たしたら再訪)

| # | 項目 | 発動条件 | 出典 |
|---|---|---|---|
| E1 | 宛先選択の重み付け | variety_hint(発話定型化対策)の効果を見てから | [legacy-adoption.md](legacy-adoption.md) |
| E2 | icebreak 非対称化 | 「関係の非対称性が結果に効く」証拠が出てから | 同上 |
| E3 | ペルソナ深さ属性(P3) | **不採用決定済み**。再訪条件=内省改善後も多様性頭打ち+50人A/Bの見込み | 同上 |
| E4 | コスト事前見積り(bench拡張) | 本選クラウド計画時(A5と合流) | 同上 |

## 明示的に「やらない」と決めたもの(再確認用)

archetype集約(個体異質性を消す=k*と正面衝突)/RAP木探索(R1衝突)/動的モデルカスケード
(呼数変動=R1違反)/ペルソナリッチ化/内省自己報告のk証拠化/Q&A型synthetic users参入/
<2Bモデルの背景利用(日本語未検証・routineで足りる)。

---

## 推奨順(参考)

1. **A2**(10秒)→ **B1討議**(agent-LODの方針が決まると A5/B3/D5 の形も決まる)
2. シミュ解禁時: **C1+C2一括**(研究本体の最重要データ)
3. 手が空く枠で **A3→A4**(観測の精度向上・小粒)、その後 **A1**(スループット=以降の全ランが速くなる)
4. **D1→D2** は本選のスケール戦略(他都市展開)を採るかの判断とセットで
