# STATUS — 索引

> 最終更新: **2026-08-07** — **第98小粒バッチ=実行役7本並行**: resume 整合の全数監査(未保存の日/期ガード**15件+付随5族**を修復・★chance が resume で 29→44 二重発火の実測)・
> **IF-E2 UNCOVERED 完全接続**(SNA §3.98 の非取引 K5 部門・`UNCOVERED_KINDS`=空)・**DP-U3 層別クォータ**(第91破綻の解消・既定OFF)・3D-U0 クランプ・3D ストリーミング化(SHA一致12通り)・
> llm_health 接続+噂混線オーバーレイ(★噂は novel rate を押し下げる)・**RW-U1 取得リサーチ**(★無料のみで構成可・アメダス保持10日=日次取得必須)。テスト **3536 緑**(3357→+179)。
> ユーザー決定6件: **DP-U2=暫定案C**(8/15 に vLLM 同居実測で判定)・**DP-U3=本線25万**(現実同等規模)・SV-05=③・DP-U4=呼数・B3=換算しない・RW-U1=承認(自律実装委任)。
> 判断待ちの要点: U-10・OBS-U1/U3・**policy_cache 保存**(新規=resume で呼数が変わりうる)・PUB-U1=公開リポの Allow force pushes 一時 ON 待ち。次=wave2(RW フェッチャー・解析25万対応)。

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
