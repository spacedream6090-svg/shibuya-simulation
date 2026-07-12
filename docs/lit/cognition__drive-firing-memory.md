# 欲求駆動発火 + 記憶検索スコアの実装接地(RQ1+RQ2、2026-07-05 検収)

> フル調査: [../research/drive-memory-architectures.md](../research/drive-memory-architectures.md)(Opus 4.8 実行・Fable 5 検収)。
> 用途: 生態系フェーズ Phase A(drive.py)/ Phase B(memory.py)のパラメータ根拠。

## 欲求発火(RQ1)
- **Park 2023 reflection トリガー**: 直近イベントの重要度総和 > **150** で reflection 発火 → 「蓄積→閾値」型の直系前例。我々の drive ゲージはその一般化。
- **MicroPsi(Bach)selection threshold**: 現在の動機は閾値を超えないと交代しない**ヒステリシス**(緊急度+個体差依存)→ 個人別閾値+不応期の理論接地。urge の leaky 係数の具体値は**未確認**(PDF抽出失敗)。
- **BDI**: bold(再考少)⇔ cautious(再考多)— 動的環境ほど cautious が優位(Kinny & Georgeff)→ fire_weight の個体差解釈。
- **EVC(Shenhav)**: 認知努力の配分は期待価値で決まる → 発火確率の規範形は `p = logistic(k(gauge − θ))`(B段で現行の固定 fire_weight から拡張検討)。
- 減衰の桁: 常時リーク 0.5-2%/時、**不発時 30-50% 部分リセット**(LIF 類推)→ ユーザー仕様「数十%」と整合。閾値個体差は TruncatedNormal/LogNormal(σ/μ≈0.2-0.4)推奨。

## 記憶検索(RQ2)
- **GA の検索式(一次資料確定)**: score = 正規化(min-max)した recency・importance・relevance の加重和。論文は等重みだが**公式コードの実効比 = recency 0.5 : relevance 3 : importance 2**(relevance 支配)。recency decay はコード既定 **0.99/時**(論文 0.995)。→ memory.py は 0.5/2.0/3.0 + 0.9983/step(10分換算)を採用済み。
- reflection 原文仕様: 重要度和>150 → 直近100件 → 高レベル質問3 → 各質問で検索 → 洞察5件(証拠ID付き)。我々は就寝時1回の JSON 統合(summary/salient+importance/belief)に畳んだ。
- 埋め込み無しの relevance 代理: BM25/Jaccard/メタデータ一致で可(文脈語の包含 = 最軽量版)。
- 日本語統合プロンプトの注意: 出力言語を明示 / 先頭 `{` を強制 / トークン1.5-2倍を予算に。

## 設計への反映(済み)
drive.py の重み・減衰・不応期 / memory.py のスコア式・係数 / reflection の統合プロンプト。未反映: logistic 発火(B段)、閾値分布の LogNormal 化(感度分析とセットで)。
