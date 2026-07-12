# 分野8 概観 — 計測・検証(validation)= novelty 第4軸
- 分野: observer/measure, analyze | 重要度: P0
- 出典: 「Validation is the central challenge」(Springer AI Rev 2025)/ operational validation replication(arXiv 2508.21740)/ Argyle et al. 2023 silicon sampling(Political Analysis)/ Aher et al. 2023 Turing Experiments / 大規模再現(Nature Comp Sci 2025)

## validation の標準と落とし穴
- **operational validity**: 「表層でなく機構を捉える」。ABM 実務は **Monte Carlo(多 seed)で"正しい理由で正しいパターン"を micro/meso/macro の分布・構造で確認**。個体/テキストの一致でなく**マクロパターンの再現**。→ M2/M3 は face validity でなく **seed 再現 + 機構チェック**。
- ★ **LLM-as-judge の circularity**: LLM に自出力を評価させると**自己 favoring・poor calibration**。→ 事後 LLM-judge は **別モデルを judge に / 人手検証サブセット / 行動(非自己申告)指標 / 評価者間信頼性**で守る。
- **face validity の限界**: 「それっぽさ」は機構と緩くしか結びつかない。

## LLM を人間 proxy とする妥当性(silicon sampling)
- **Argyle 2023「algorithmic fidelity」**: demographic 条件付けで人間の回答分布を再現(集団・相関・少数派も)。
- ★ **限界: tail の過小表現**: silicon sampling は**多数派に overfit し、極端・少数派(tail)を過小表現**。→ **世界改変者は tail(joint upper tail, §2)**。LLM が tail を潰すなら、**観たい現象そのものが系統的に過小生成/歪曲**されうる = **最大級の validity 脅威**。
  - 緩和: trait の tail を**初期分布で明示的に確保**(OPEN#3、LLM の自発生成に頼らない)。emergent tail が本物か検証。
- **効果量の水増し + sensitive topic 盲点**(Nature CS 2025: 主効果73-81%再現だが効果量は人間より大、race/gender/ethics で再現低)。→ grievance/対立(我々の領域)は RLHF で抑圧される盲点(分野9)。

## 較正(calibration)= 新規 k* を信じる前に既知結果を再現
Turing Experiments(Aher 2023: Ultimatum/Milgram/Wisdom of Crowds 再現)の発想で、**既知の社会結果を再現できるかを sanity check**:
- 例: Centola の tipping ~25%(分野4)/ naming-game の収束(分野4)を我々のエンジンで再現 → 通れば novel な k* 結果を信頼する土台。

## 効く seam / no-fingerprint
- `observer/measure`: 多手法(行動ログ + 別モデル judge + 人手検証 + 評価者間信頼性)、operational validity(多 seed マクロ)、既知結果での calibration。
- 脅威 register: tail 過小 / 効果量水増し / sensitive topic 盲点 → 分野9(LLM性質)と対で扱う。

## 関連
[[complexity__phase-transition-methodology]](多 seed・R²)/ 分野9(LLM性質)/ [[mas__li2026_moltbook]](5指標)/ [[project-charter]]
