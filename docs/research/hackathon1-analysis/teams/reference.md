# reference(リファレンス実装) — 30.5/40(A8.5 B7.0 C7.0 D8.0)

> ランキング対象外。主催者 ryukih 氏が用意した「基準器」。
> 講評: [reference_eval.md](https://github.com/ryukih/SD-Hackathon-Reviewer-2026May/blob/main/evaluations/20260511-1st-Hackathone-valuations/reference_eval.md)
> 検証: reference_eval_review.md — **総合判定「妥当」**(4軸すべて是認、推奨帯 A8-9 / B6-7 / C6-7 / D7-8)

## コード実体の所在(実査できた)

レビューリポの `submissions/reference/` は `.gitignore` で本体が除外されており、追跡されているのは
`README.md` と `.gitignore` のみ。**しかし同一コードが公開されている**:

- **[ryukih/SD-Hackathon-2026DEMO](https://github.com/ryukih/SD-Hackathon-2026DEMO)**(public / 説明「社会シミュレーションのハッカソン用デモコード」)
- ファイル構成が `reference_eval.md` の引用先(`agent.py` / `simulation.py` / `ollama_client.py` /
  `visualization.py` / `utils.py` / `main.py` / `config.yaml`)と完全一致。
  引用行番号も実査で一致(例: `agent.py:174` = `_build_fire_section` の定義行、
  `agent.py:347` 付近 = 行動プロンプト先頭、`simulation.py:299` = `get_fire_info_for_agent`)。
- **正直な註記**: DEMO リポの push は 2026-07-03、講評日は 2026-05-07 なので**同一版とは断定できない**。
  README を差分比較したところ、(a) 参加者向け注意書きの追記、(b) デモ動画 URL の差し替え、
  (c) `config.yaml` の fire パラメータ変更(`start_step: 15/30 → 35/70`、`radius: 10 → 15` 等)の
  3 点が異なる。**構造・設計思想は同一**で、講評の読解には支障がないと判断した。

## 実装規模(実査値・DEMO 版)

| ファイル | 行数 | 役割 |
|---|---:|---|
| `agent.py` | 593 | Agent クラス・2種のプロンプト生成・JSON パース・メモリ |
| `simulation.py` | 508 | ループ・場所/火災管理・ログ |
| `main.py` | 255 | CLI・ロギング・可視化分岐・統計出力 |
| `ollama_client.py` | 129 | Ollama HTTP クライアント |
| `utils.py` | 74 | `FireConfig`/`PlaceConfig` TypedDict + 位置判定 |
| `config.yaml` | 76 | 全パラメータ外部化 |
| (計・可視化除く) | **1,641** | + `visualization.py` 22KB, `visualization/viewer.html` 35KB |

依存は `numpy / matplotlib / pyyaml / requests / Pillow` の 5 つのみ。

## 「基準器」が**持っている**もの(= 30.5 点の土台)

1. **no-fingerprint の徹底**(A8.5 の中核)。`_build_fire_section` は
   Position / Intensity / Radius / Your distance の 4 数値だけを出す。
   コード内コメントに `No qualitative descriptions (e.g. 'dangerous', 'evacuate') are included` と
   **設計意図が明文化**されている。行動プロンプトも `=== AVAILABLE ACTIONS ===` に
   `"stay"` / `"move"` を機械的に列挙するだけで戦略誘導がない。
2. **知覚境界の明示**(知覚モデル B)。火災半径外のエージェントにはプロンプトに火災節が**存在しない**。
   情報は他者メッセージ経由でのみ間接伝播する。
3. **通信制約**。`get_nearby_agents` が通信半径 **かつ** 同一領域(共に場所内 / 共に場所外)を要求。
   場所内↔場所外は通信不可 = 情報非対称性が構造化されている。
4. **2 フェーズのプロンプト分離**。メッセージ決定プロンプトには**座標を渡さない**、
   行動決定プロンプトには渡す。情報アクセスの非対称性を実験装置として使っている。
5. **LLM 自己生成メモリ(self-feedback)**。LLM が毎ステップ `memory` フィールドを自分の言葉で書き、
   次ステップに `=== PREVIOUS MEMORY ===` として再注入。`memory_limit`(保存 20)と
   `memory_size`(参照 5)を分離管理。
6. **同期 4 フェーズ実行**でレース条件なし。堅牢な JSON 抽出(括弧深度追跡)+ 全 LLM 呼び出しに
   try/except フォールバック。`repeat_penalty` / `repeat_last_n` / `min_p` まで調整。
7. **YAML 完全外部化**。places / fires がリスト型で、新しい場所種別も YAML だけで追加可能。

## 「基準器」が**持っていない**もの(= ここが 30.5 の天井)

これが本選対策として最も重要。**A/B/C/D それぞれで「基準器に無いもの」が上位との差分になっている**。

| 欠落 | 該当軸 | 講評の指摘 |
|---|---|---|
| **乱数シードが無い** | D | 実査でも確認: `random.randint` / `random.choice` を直呼びし `seed()` 不在。「再現性のためのランダムシード設定を追加すると実験の再現・比較が可能になる」 |
| **対照群・条件比較が無い** | C / 実験設計 | 単一シナリオを 1 回走らせるだけ。sham/null 対照も A/B 条件も無い |
| **創発の定量指標が無い** | C | 「創発の定量的測定手法…の記述がない」。創発は**デモ動画の目視**でしか主張されていない |
| **テストが無い** | D | `tests/` ディレクトリ自体が存在しない |
| **将来展望が浅い** | C(7.0 の主因) | README の拡張例が「YAML を書き換えて cafe / library にできる」だけ。「コードの拡張性ポテンシャルに比して、将来ビジョンの具体性・深度が不足」 |
| **シナリオが既視感**(バー+火災) | B(7.0 の主因) | 「『バーでの群集』自体は標準的なクラウドシミュレーション題材であり、際立った独創性には一歩届かない」 |
| **非同期化されていない** | D | 20 体 × 2 呼び出し/step を直列実行 |
| **行動空間が極小** | (減点にはなっていない) | 移動は 4 方向 1 セルのみ。`stay` / `move(up/down/left/right)` の 2 アクションだけ |

## shibuya-sim(自チーム 35.0)との対照 — なぜ +4.5 だったか

| 軸 | ref | shibuya-sim | 差分の源 |
|---|---:|---:|---|
| A | 8.5 | 9.0 | +0.5。ref も no-fingerprint は徹底しているので**差は小さい**。shibuya 側は世界ルールの層数(7ニーズ×2層・5層会話確率・環境/イベント層)で上回った |
| B | 7.0 | 9.0 | **+2.0。最大の差**。実 POI(OSM)+ citation 付き人口分布 + 研究的問い(SNS 有無)で「既視感」を脱した |
| C | 7.0 | 8.0 | +1.0。モジュール分離と YAML 8 種で勝ったが、**将来展望の明文化不足は ref と同じ弱点**(README にプレースホルダ残置) |
| D | 8.0 | 9.0 | +1.0。シード決定性・manifest.json・2 プロバイダ対応・多層メモリで上回った |

**教訓**: 基準器に対する優位は「B(世界の現実性・研究的問い)」で最も大きく作れる。
逆に **C は基準器と同じ罠(将来展望を書かない)にはまっていた** — 本選では最も安く回収できる伸びしろ。

## 本選への含意

- 基準器が 30.5 = **「きれいな no-fingerprint 実装 + モジュール分離」だけでは 30 点台前半で止まる**。
  A は 8.5 まで取れてしまうので、**A で差をつけるのは難しい**(上位10平均 8.60 に対し ref 8.5)。
- 30.5 → 37.0 の 6.5 点は、ほぼ **B(独創的で現実に接続したシナリオ)+ C(具体的ロードマップ)+
  実験装置(対照群・定量指標・再現性)** で構成されている。
- shibuya-simulation の現行資産(CRN 対照実験・permutation 検定・sham/null 対照・
  ゴールデンテスト 1725 本・calibrate REALITY 出典つき較正)は、**基準器が一つも持っていない層**にある。
  これを提出物で可視化できるかが勝負どころ。
