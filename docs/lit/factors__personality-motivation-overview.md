# 分野2 概観 — 性格・動機づけ心理学(factors)
- 分野: factors(OPEN#1/#3、及び #2 の入力)| 重要度: P0
- 構成概念の集合メモ(古典が多いため consolidated)。個別出典は references.md クラスタ2。

## 構成概念と trait/state 分類
| 構成概念 | 出典 | 分類 | 役割 |
|---|---|---|---|
| **Need for Cognition (NFC)** | Cacioppo & Petty 1982(34項目, Cacioppo+1984 で18項目, r=.95) | **trait(初期)** | 思考を好み没頭する傾向 = **上流ゲート(熟慮が起動するか)=主体性の"量"** |
| **統制の所在 (Locus of Control)** | Rotter 1954/1966 | trait 寄り(経験で動く) | 「世界は自分の行動に応答する」信念(内的 vs 外的)。**世界改変に load-bearing**、効力感とは別 |
| **好奇心・未来志向 / proactive motivation** | Parker & Collins 2010 / Parker, Bindl & Strauss 2010(can-do / reason-to / energized-to) | trait(初期) | 探索・先行行動の傾向。動機状態が先行行動をゲート(ファネルと整合) |
| **自己効力感 (Self-Efficacy)** | Bandura 1977/1997、GSE: Schwarzer & Jerusalem 1995 | **state(経験で構築)** | 「自分は実行できる」。**4源泉で更新**(下記) |
| **proactive personality** | Bateman & Crant 1993(17項目 PPS) | ⚠️ **測定対象(入力にしない)** | 「状況に縛られず環境を変える」= world-changer の直接構成概念。**焼き込むと指紋** |

## Bandura 効力感の4源泉(= OPEN#2 state更新則の"入力") ★分野3へ直結
1. **達成経験 (mastery)** — 自身の過去の成功の想起(**最強**)
2. **代理経験 (vicarious)** — 他者の成功を見聞き
3. **社会的説得 (verbal persuasion)** — 他者からの評価・励まし
4. **生理・情動状態 (physiological/affective)** — 自身の感覚の解釈
→ 更新則は「成功→+10」の決め打ちでなく、**この4つを因果入力**にして確率的に動かす(seam)。

## 効く seam / 入れ方
- `factors/registry`: trait(NFC, LOC, 好奇心)= 初期条件。state(効力感)= 経験から立ち上げる。
- `factors/update`(OPEN#2): 4源泉 + SIMCA(分野6)を因果入力に。決め打ち禁止。
- `observer/measure`: **proactive personality / world-changing は事後測定**(エージェントに構成概念を教えない)。
- `config`(OPEN#3 初期分布): GSE(10-40, α=.86-.95, 独/波/韓 n=1933)・NFC 尺度の母集団分布から trait の分布形を逆算。

## no-fingerprint 上の要点
- **world-changer に直結する proactive personality を"入力ダイアル"にしない。** 上流 trait(NFC/LOC/好奇心)を初期条件に置き、効力感と先行行動の"結果"を創発させ、改変者は**事後測定**する。これが handoff §3-4 の trait/state 分離 + 観測者frame の核。
- **NFC は"量"であって"向き"でない**(高NFC=思考量↑だが良い決定とは限らず、既存バイアスを増幅しうる)→ 主体性≠世界改変を保つ。

## 関連
[[project-charter]] / 分野3(state更新則: Bandura4源泉 + SIMCA + Morrison&Phelps)/ 分野6(集合行為・制度経済)
