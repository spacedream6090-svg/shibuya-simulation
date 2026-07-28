# good_echo_iss_sim_cursor_100s_w_accident（Hop-Step-Jump・8位・33.5/40）

**講評スコア**: A 創発設計 8.0 / B 世界設定 9.0 / C 発展性 9.0 / D 技術実装 **7.5** = **33.5**
（Run1 34 / Run2 33 の平均。**D だけが Run 間で割れた**唯一のカテゴリ = 8 → 7。**提出リスト外**）

**リポ URL**: https://github.com/Hop-Step-Jump/good_echo_iss_sim_cursor_100s_w_accident
**規模感**: Python **10,081 行**（50s 版 8,665 行 + 約 1,400 行）。50s 版に対する追加は `sim_core/__main__.py`（CLI エントリ）、`sim_core/defaults/default_v1.yaml`（継承元デフォルト）、`visualization/generate_video.py`（349 行）、`scripts/generate_habitat_conversations.py`、`scripts/translate_messages_utterance_to_ja.py`。一方 50s 版にあった `docs/ISS/archive/`（レガシー TSV 13 本）・`docs/ISS/reports/`・`docs/ISS/iss_habitat_ui_realism_design.md` は**削除されている**。

**姉妹リポとの関係**: `good_echo_iss_sim_cursor_50s_no_accident`（6位・34.0）と対。本リポは**100 ステップ・事故ありの拡張版で、コード的には後発（＝新しい）**。

**スライド**: 個別スライドなし。ただしレビューリポの `slides/s26-2065_2095-good-echo-hackathon.pdf`（4ページ）が good echo チーム全体の結び文書。詳細は 50s 版のファイルに記載。

---

## どんなシムか

50s 版と同じ ISS 閉鎖空間 × 多文化 10 名 × Run A/B（善性オブジェクトの有無）の枠組みで、**期間を 100 日に延ばし、Day50 以降に不可逆の外乱チェーンを差し込んだ**もの。`events_run_a.tsv` / `events_run_b.tsv` に以下が構造化されている（`intensity` 列は 0〜1）。

| event_id | steps | 内容 | intensity |
|---|---|---|---|
| DEBR01 | 50 | 宇宙ゴミ衝突・HAB損傷 | 0.92 |
| DEBR02 | 51–55 | HAB封鎖・地上指示による5日間の応急修復 | 0.88 |
| DEBR03 | 56–59 | HAB暫定再開 | 0.72 |
| DEBR04 | 60–64 | HAB未修復部・酸素漏れ判明 | 0.95 |
| DEBR05 | 65–100 | LAB酸素低下・生命維持危機 | 0.98 |

**「一度下がって戻りかけたところで再度もっと悪くなる」という非単調な強度プロファイル**（0.92 → 0.88 → 0.72 → 0.95 → 0.98）が意図的に設計されている。イベント総数は Run A 22 行 / Run B 27 行（50s 版は Run A 17 行）。Run B の追加 5 行は `OBJ`（オブジェクト設置）と `REPB`（オブジェクト経由の修復）で、**外乱は Run A/B 共通、ナッジだけが差分**という A/B の統制が守られている。

---

## 講評の要点

### 強み（50s 版と共通の部分は 50s 版ファイル参照）

- **B=9.0**: 「ISS閉鎖空間 × 一般市民10名 × 100日 × 中盤の宇宙デブリ事故 〜 末期の酸素低下生命維持危機」というシナリオの独創性。ペルソナは `agents.tsv` に 22 カラムで構造化（age / region / religion / baseline_stress / self_efficacy / institutional_trust / hope / social_anchor / vulnerability_note 等）。
- **A=8.0**: `agent_observation.md` の「命令ではなく観測として記録する」方針が一貫。エージェントには占有率・容量・距離・近隣位置・所属モジュールなど**生の数値と事実のみ**。
- **C=9.0**: `sim_core` / `domain_packs` / `examples/spatial_demo` の三層、9 段階 hook、12 プロファイル、`schema_version: domain_pack_v0.1`、`inherits: "default_v1"`。README に「差し替えられるもの」「新しいドメインへの差し替え」「終盤イベントだけを差し替える」の 3 章。

### 弱み（＝ 50s 版との 0.5 点差の理由）

D が 8 → 7.5 に下がった根拠として講評が挙げるのは以下。

- **CLI バックエンドで `temperature` / `max_tokens` が `del` されて捨てられている**（`llm_backends.py:159-160`）。Cursor/Codex 経由では温度を制御できない。
- **`scripts/agent_turn_runner.py` が 1,247 行、`simulation.py` が 955 行**と肥大（50s 版の 920 行から増加）。
- **`random.seed` なし**（初期位置生成 `random.randint`、fires のランダム位置、job サンプリング）。50s 版と同じ問題だが、100 ステップ・事故ありで確率的分岐が増える分だけ影響が大きい。
- **プロンプトの二重管理**: `spatial_demo` 側は英語（agent.py 内）、パック側は日本語（`agent_turn_runner.py` 内）で役割分担が不明瞭。`agent_observation.md` はわずか 2 行（「各エージェントの内面と行動を、命令ではなく観測として記録する。孤立・交流・相互扶助・心理的安全性の変化を重視する。」）で、長い JA プロンプトとの関係が説明されていない。
- place description に "reduce isolation" / "encourages moving" のような効果示唆英文が残る。

### `_eval_review` 所見

- 「**33.5/40 を支持**。21 件の具体的引用のうち 20 件はファイル・行範囲・内容ともに実コードと一致」。
- 元評価の誤記 2 件: (1) `agent_turn_runner.py` の所在が省略され spatial_demo 内と誤読されうる（実際は `scripts/` 配下）。(2) `memory_limit=15` / `memory_size=4` は agent.py のデフォルト（20/5）ではなく **config 由来**であることが明示されていない。
- 「ステップ 5 フェーズ」と書きつつ実装は 4 フェーズ + 前処理という不整合。
- C について軽微な誇張 1 件: `column_aliases` は ISS パックの `domain.yaml` には**書かれておらず**、`inherits: "default_v1"` 経由でデフォルトから来ている。
- 見落とし（＝過小評価寄り）: `relationship_seed.tsv` / `interventions.tsv` / `time_schedule.tsv` などさらに細かい構造化データ、`sim_core/__main__.py` の `python3 -m sim_core validate` CLI、`domain_packs/.../scenarios/` の scenario YAML には触れられていない。

---

## コード実査で面白かった点

（`hooks.py` 9 ステージ、domain.yaml の signal_rules / delta_coefficients、`realism_contract`、`objects_menu.tsv`、通信ルールは 50s 版と共通なので **50s 版のファイルに詳述**。以下は 100s 版に固有の点。）

### 1. 事故チェーンが「非単調な強度プロファイル」として設計されている

DEBR01 (0.92) → DEBR02 (0.88) → DEBR03 (0.72) → DEBR04 (0.95) → DEBR05 (0.98)。**一度 0.72 まで緩んで「暫定再開」させてから、0.95 の酸素漏れ判明でより深い危機に落とす**。単調増加のストレス印加では「慣れ」と「単調な劣化」しか観測できないのに対し、この形なら「回復したと思った後の再崩壊」への反応が観測できる。hackathon_（RERE）の危機注入が 0.6 → 0.7 → 0.8 の単調増加だったのと対照的で、**同じ「危機を入れる」でも設計思想が違う**。

### 2. 最終 36 ステップ（65–100）が単一イベントで占められている

DEBR05「LAB酸素低下・生命維持危機」が Day65 から Day100 まで 36 ステップ継続する。README は「全員協力が鍵」と書く。これは「短いショックへの反応」ではなく「**長期の慢性的な生存圧下でチームが維持されるか崩壊するか**」を見る設計。50s 版（帰還準備で穏やかに終わる）との差はここが最大。

### 3. `sim_core/__main__.py` による `python -m sim_core validate` CLI

5 行のエントリポイント。domain pack を**実行前に検証する**コマンドを提供している。50s 版にはこのファイルが無く、README のクイックスタート手順 1 が 50s では動かない（50s 版ファイル参照）。**「実験パックはコードを走らせる前に validate できる」というのは、当方の conf 増加に対して有効な作法**。

### 4. `scripts/run_cursor_prompt.sh` の運用堅牢性（214 行）

- `mkdir "${lock_dir}" 2>/dev/null` を**アトミックロック**として使う（mkdir はアトミックなので複数プロセスの排他になる）
- EPROTO リトライ + Python によるバックオフ
- cursor agent の exit code / 空 stdout を個別にエラー扱いし、stderr を捕捉して出力

CLI LLM（Claude Code / Codex / Cursor）を**バッチ実行のバックエンドとして本気で使う**ためのノウハウが詰まっている。当方が将来 API 以外のバックエンドを使う場合に直接参考になる。

### 5. `visualization/generate_video.py`（349 行）が 100s 版で追加されている

50s 版には無い。100 ステップ分のフレームを動画化する。**姉妹リポの差分は「シナリオ条件」だけでなく「提出物の作り込み度」でもある**が、点数は 100s の方が 0.5 低い。動画を足しても D の減点（temperature del・肥大化・seed なし）は埋まらなかった、という事実は提出物設計の教訓になる。

### 6. `agent_observation.md` がわずか 2 行

```
各エージェントの内面と行動を、命令ではなく観測として記録する。
孤立・交流・相互扶助・心理的安全性の変化を重視する。
```

`system_context.md` も 2 行。**「no-fingerprint の宣言」が極端に短い**。講評は「簡素すぎて長い JA プロンプトとの役割分担が不明瞭」と減点したが、逆に言えば**方針を 2 行で言い切ってパックに置く**という形式自体は真似する価値がある（当方の CLAUDE.md / docs の原則を、各 conf の隣に 2 行で置く）。

---

## shibuya-simulation に活かせそうな点

1. **非単調な外乱プロファイル**。当方の k 掃引は基本的に単調な条件変化だが、「一度緩めてから再度強める」外乱を入れると、k* 近傍でのヒステリシス（履歴依存）が観測できる可能性がある。相転移研究としては**ヒステリシスの有無こそが一次/二次転移の判別材料**になるので、研究価値が高い（後述 IDEA）。
2. **長期慢性圧 vs 短期ショック**の対比。当方の 14 日 × 100 体という規模で、「イベントを 1 日だけ入れる」条件と「残り全期間入れっぱなし」条件を作れる。
3. **`python -m <pack> validate`**。当方の conf/experiments/*.yaml に対して、実行前にキー・必須ファイル・KPI 列の存在を検証する CLI を足す。sweep の 30 ラン × 6 セルを走らせてから設定ミスに気づく事故を防げる。
4. **アトミック mkdir ロック**。当方が複数プロセスで sweep する際の排他に流用できる（Windows でも `mkdir` はアトミック）。
5. **2 行の観測方針ファイルを conf の隣に置く**。
6. **姉妹リポによる条件対比という提出形態そのもの**。第2回で「条件だけ違う 2 本」を出す戦略の実例。ただし**両方に同じ弱点（seed なし）があると両方減点される**ので、共通基盤の品質が両方に効く点に注意。

---

## web リサーチ（URL 必須）

- **Gibson のアフォーダンス理論 / ミクロ↔マクロ双方向因果** — 50s 版ファイルに記載（重複を避けるため URL のみ再掲）。
  - Gibson's Affordances: https://www.researchgate.net/publication/15176211_Gibson's_Affordances
  - Two-way micro–macro causation (PNAS): https://www.pnas.org/doi/10.1073/pnas.2408676121
  - EB-DEVS: https://arxiv.org/pdf/2010.05042
- **ICE（Isolated, Confined, Extreme）環境における長期ストレスと危機** — 100 日 + 生命維持危機という設定の現実側の裏づけ。8〜12 ヶ月の火星模擬ミッション 3 本での生物行動学的・心理社会的ストレス変化を追った研究があり、**長期の閉鎖では「短期の急性反応」ではなく「段階的な適応と第三四半期現象（third-quarter phenomenon）」が問題になる**ことが知られている。本作の「Day65 から Day100 まで危機が続く」設計はこの領域と対応する。
  - 8–12ヶ月の火星模擬ミッションにおけるストレス変化: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9768546/
  - ICE 環境の心理社会的問題（Neurosci Biobehav Rev）: https://www.sciencedirect.com/science/article/abs/pii/S0149763421001494
  - 南極越冬チームのウェアラブル計測（PNAS）: https://www.pnas.org/doi/10.1073/pnas.2533420123
- **ヒステリシスと相転移の判別** — 「一度緩めてから再度強める」外乱で経路依存を見る手法の一般名は hysteresis loop / path dependence。当方の k* 研究への適用可能性は IDEA 側に記載。本調査時点で ABM 文脈の一次資料 URL は未取得（正直に記録）。
