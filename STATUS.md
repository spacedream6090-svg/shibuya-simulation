# STATUS — 索引

> 最終更新: **2026-08-03** — 現況台帳を2分割(実装済み / 未実装・判断待ち)。
> 直前の実装状況: 高精細3D×物理=松案+**竹-4 P3 境界縫合**まで全レーン完結・テスト **2687 緑**・
> **夜間実 LLM 検証ラン完走**(100体×288step=sim2日・3,759呼・fallback 0)。現行レーンは第86 day_plan v1(実装中)。

| 探しているもの | 行き先 |
|---|---|
| **実装済み**(シミュレーションの概要 + 完了済み実装の全リスト) | **[IMPLEMENTED.md](IMPLEMENTED.md)** |
| **未実装・実装中・計画済み・ユーザー判断待ち** | **[PENDING.md](PENDING.md)** |

- [IMPLEMENTED.md](IMPLEMENTED.md) 第1部 = シミュレーションの概要(これは何か / 研究の柱 / アーキテクチャの本質 / 体制と運用 / 本選)。
  第2部 = 完了済み実装の全リスト(システム別 A〜Q + バッチ完了年表)。
- [PENDING.md](PENDING.md) = ①実装中・次バッチ ②計画済み ③ユーザー判断待ち(表)④持ち越し小粒 ⑤設計制約と受領文書。

## 更新プロトコル

> **実装バッチのコミットごとに、該当するファイル([IMPLEMENTED.md](IMPLEMENTED.md) / [PENDING.md](PENDING.md))を必ず更新する**(検収の一部)。
> 本ファイル(STATUS.md)は**索引と最終更新行のみ**を維持し、詳細は持たない。
> 各項目の正典は計画書と [docs/log/devlog.md](docs/log/devlog.md)(圧縮版 [devlog-compressed.md](docs/log/devlog-compressed.md))。
