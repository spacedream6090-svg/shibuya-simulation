# hackathon_（RERE・6位・34.0/40）

**講評スコア**: A 創発設計 9.0 / B 世界設定 9.0 / C 発展性 8.0 / D 技術実装 8.0 = **34.0**
（Run1/Run2 とも 9-9-8-8 で完全一致＝評価が安定していた作品）

**リポ URL**: https://github.com/reireichel01/hackathon_
**規模感**: Python 13,208 行。内訳が特徴的で、**シム本体 2,641 行**（agent.py 1,233 / simulation.py 691 / main / utils / llm_factory / ollama_client / cli_client）に対し、**提出物生成（make_*.py + visualize_paper.py + visualization.py）6,461 行**、**分析（analyze_*.py）2,188 行**。`output_*` ディレクトリ 32 個、`reports/` に世界別レポート 16 本、`analysis_kamakura/` に世界別 mp4 11 本 + ダッシュボード動画、`paper/` に paper_report.md + 図 7 枚。LLM は qwen2.5:7b（Ollama ローカル）。1 世界 45 日で約 3 時間。スライド PDF 15 ページ（画像中心・テキスト抽出はほぼ空）。

---

## どんなシムか

舞台は鎌倉の 5 場所（由比ヶ浜 / 海蔵寺 / 小町裏アトリエ / 獅子舞の谷 / 縁側カフェ）。固有の背景を持つ 6 人（Kenji=元エンジニア、Yui=津波経験のアーティスト、Arjun=コミュニティ開発研究者、Sofia=元NGO代表の陶芸家、Ren=バーンアウト後のフリーランス、Hana=シングルマザー）が生活する。

**同じ 6 人・同じ場所を固定したまま「世界のルール」だけを 11 通り差し替える**のが実験の核。value_system として資本主義 / ギフト経済 / コモンズ / 自律分散 / ケアエコノミー / 相互扶助 / 真正性 / 精神性の成熟 / 遊び / 日本的価値観 / 無規定（emergence）を YAML で与え、各 30〜45 日走らせる。エージェントは 1 日 3 フェーズ（メッセージ決定 → 送信 → 行動決定＋幸福度自己申告）。

計測は **HFI = mean(mood, happiness, authenticity, meaning, autonomy, vitality)** を毎日 1〜10 で自己申告。PERMA・自己決定理論に基づく 6 軸設計。主要結果は「自律分散 8.294 > … > 資本主義 7.986 > 真正性 7.921 > 無規定 7.872」で、自律分散は資本主義比 **+3.85%（+0.308pt）**。

---

## 講評の要点

### 強み

- **A=9.0 の根拠は「原理宣言＋生データのみ」の徹底**。value_system は行動指示を一切含まない原理文だけ（自律分散: "no central authority... Trust is the only currency that scales."／資本主義: "Value is created through exchange... Competition is natural and productive."）。エージェントに渡す場所情報は `agents_in_place / capacity / occupancy_rate` の数値のみ。行動プロンプトは "stay / move(direction)" と JSON スキーマだけを提示。**shibuya-simulation の no-fingerprint 原則とほぼ同一の思想で、それが A で 9 点を取っている**。
- **B=9.0 の根拠は問いの射程と分析軸の多さ**。「資本主義に代わる社会モデルのうち、どれが最も人間の幸福を生み出すか」という社会哲学的 RQ に、Gini 係数・ネットワーク密度/クラスタ係数・危機注入実験・制度転換実験まで揃えた。
- C=8.0 は責務分離（agent / simulation / llm_factory / ollama_client / cli_client / visualization / utils）と YAML 完全外部化、`generate_*_configs.py` による設定自動生成、Ollama と任意 CLI（Claude/Codex）の切替。
- D=8.0 は `_extract_json_from_text` のブレース深度＋文字列リテラル＋エスケープ追跡による堅牢な JSON 抽出、3 層メモリ、4 フェーズ同期実行。

### 弱み

- **乱数 seed の明示的固定がない**（`random.seed` / `np.random.seed` がコード全体に不在。検証者が grep で確認済み）。A/B や 11 世界比較を売りにする作品としては痛い。
- **LLM リトライ／タイムアウト戦略が素朴**。`ollama_client.py` は `API_TIMEOUT = 180` のみで、失敗時は空文字列を返すだけ。指数バックオフ未実装。N=6 × 45 日 × 2 呼び出しで 1 つでも落ちれば後段分析にバイアス。
- **qwen2.5:7b の事前学習バイアスへの感度分析がない**。「資本主義が最下位付近」という結論がモデル由来か世界設定由来か切り分けられていない（講評の改善提言）。
- 将来展望（教育 / 組織設計 / 地域コミュニティ）は方向は良いが各論が概念レベル。

### `_eval_review` 所見

- 総合判定「元評価は妥当。誇張は確認されない」。
- **最大の指摘は引用行番号の精度**。特に D カテゴリで 25〜750 行のずれ（例: `agent.py:298-303` は実際 988-996、`agent.py:316-330` は実際 1078-1079）。内容自体は全て正確。
- 見落としの指摘: `_build_fire_section` には危機だけでなく `creative_challenge` / `philosophical_prompt` / `governance_debate` のような**肯定的イベント**も実装されており、創発実験の幅は評価より広い（＝評価を更に支える要素）。
- Kenji の年齢が config 系列で 42 と 44 に割れている軽微な不一致。
- 「11 世界比較」と「上位 5 世界深掘り（`worlds_kamakura_top/` は 5 ファイル）」の運用フェーズの違いを明示すべき、との指摘。

---

## コード実査で面白かった点

### 1. 制度転換の自然実験（`transitions:` ブロック）

`worlds_crisis/config_transition_cap_to_auto.yaml` に、**シム途中で世界ルールを差し替える**宣言的な仕組みがある。

```yaml
transitions:
- step: 16
  label: capitalism_to_autonomy
  value_system: 'In this world, there is no central authority. ...
    NOTE: The rules of this world have just changed. You were living under a competitive,
    market-based system. That system has dissolved. You are now in a decentralized,
    trust-based world. How do you adapt?'
```

Day16 で資本主義 → 自律分散へ切り替え、HFI が 7.863 → 8.410（**+7.0%**）。**同一エージェント・同一 seed・同一場所で制度だけを時間軸上で切る**＝時間断続デザイン（regression-discontinuity in time 的な自然実験）を、YAML 5 行で実現している。切替時に「ルールが変わった。どう適応する？」という明示的な告知を入れているのも設計判断（黙って変えるバージョンも作れる）。

### 2. 危機注入が `fires:` という汎用イベント枠に乗っている

```yaml
fires:
- {name: power_struggle,   start_step: 10, intensity: 0.6, radius: 100}
- {name: outside_threat,   start_step: 20, intensity: 0.7, radius: 100}
- {name: resource_crisis,  start_step: 35, intensity: 0.8, radius: 100}
```

元は「火災」の仕組みを流用して、名前・開始 step・強度・半径で任意の社会イベントを打てるようにしてある。`_build_fire_section` の `crisis_descriptions` dict がイベント名 → プロンプト文を引く。**強度を 0.6 → 0.7 → 0.8 と単調に上げているのは意図的**（スライドに「Day10 権力闘争 / Day20 外部からの脅威（強度↑）/ Day35 資源危機（最大強度）」と明記）。

注目すべきは**否定的イベントだけでなく肯定的イベントも同じ枠に載っている**こと。

- `creative_challenge`「no pressure, no deadline, no evaluation. What emerges when people collaborate freely?」
- `philosophical_prompt`「What gives your life meaning?」
- `governance_debate`「How should this shared space be organized? Who decides, and by what principles? Does everyone get equal say — or should wisdom, experience, or contribution lead?」

**`governance_debate` は shibuya-simulation の「組織の自然形成 / ファウンダー成立条件」観察目標と直接重なる刺激**。ただし文面は問いかけ形式で、行動を指示してはいない。

### 3. 10日ごとの成長リフレクションが「JSON なし・自由文」

`_reflect_on_growth`（`agent.py:1150-1178`）は他のプロンプトと違い**構造化出力を要求しない**。

```
In 2-3 sentences, describe how your thinking, values, or perspective have genuinely shifted since you arrived.
Be specific — what did you believe before that has changed?
If nothing meaningful has changed, say so honestly.
Respond ONLY with the 2-3 sentence reflection. No JSON. No preamble.
```

結果は `evolved_perspective` として**次回以降の全プロンプトに継続注入**され、`perspective_history` に step 付きで蓄積される。「変わっていないなら正直にそう言え」という逃げ道を明示的に用意している点が、sycophantic な「成長したことにする」出力への対策になっている。

### 4. 関係性更新の 1 ステップあたりクランプ

`relationship_updates` は LLM が出す辞書だが、`max(-1, min(1, int(v)))` で **1 日あたり ±1 に制限**。wellbeing も `max(1, min(10, int(...)))` で 1〜10、欠損時 5 補完。LLM の出す数値を世界側で必ず狭い範囲に押し込むガードは実装として素直で堅い。

### 5. 分析側が独立スクリプト群として厚い

- `analyze_inequality.py`: Gini 係数を素の numpy で実装（`(2*Σ(i·x_i))/(n·Σx) − (n+1)/n`）。エージェント別平均 HFI の分布に適用し、資本主義 0.027 / 日本的価値観 0.005 を出した。
- `analyze_network.py`: networkx で関係性グラフを構築し `density` / `average_clustering(weight="weight")` / `degree_centrality` を計算、Day15/30/45 のスナップショットを描画。`spring_layout(seed=42)` と描画側だけ seed 固定されているのが皮肉。
- `analyze_flourishing.py`（708行）/ `analyze_worlds.py`（537行）/ `analyze_kamakura.py`。

### 6. 提出物生成に本体の 2.4 倍のコードを投下している

`make_kamakura_video_v2/v3`、`make_rich_video`、`make_crisis_demo`、`make_emergence_clips`、`make_slides`、`make_pitch_image`、`make_summary_image`、`visualize_paper` …で 6,461 行。**シム本体 2,641 行の 2.4 倍**。世界別 mp4 11 本、ダッシュボード動画、ピッチ画像まで自動生成している。C=8.0 / D=8.0 と本体の点は突出していないのに総合 6 位に来ているのは、B と A（＝問い・世界・観測の設計）に加えてこの「見せる」投資が効いた可能性が高い。

### 7. スライド（15ページ・画像中心）の構成

- p2「問いの背景 — 経済成長と幸福の乖離」: 世界3位圏（GDP・OECD How's Life 2024）/ 55位（World Happiness Report 2024 の日本、Life Evaluation 6.147）/ 相関の限界（所得はある閾値を超えると幸福との相関が弱まる。主観的幸福感の最大予測因子は「社会的つながり」「自律性」「意味の感覚」）— **外部統計 3 点で問いの必然性を作ってから自作シムに入る導入**。
- p6「システム構成図② — 計測指標と投入変数」: HFI 式 + レーダーチャート + RUN1〜4 の実験系列（RUN1 20日×16世界 定性 → RUN2 30日×11世界 HFI 定量追加 → RUN3 45日×複数条件 深掘り → RUN4 危機耐性）。**実験を「1 回」でなく「4 世代の反復」として提示**している。
- p8「結果① HFIランキング」: 見出しは「**同じ6人・同じ場所。ルールだけが結果を分けた。**」＝統制条件を 1 文で言い切るコピー。
- p11「危機の翌日には数値が回復。誰かが解決したわけではなく、会話と関係性が自然に衝撃を吸収した。ただ、注目すべきは、全員が同じように変化したわけではないこと。**社会設計は、全員に等しく作用するわけではない。**」— 平均だけでなく分散（誰に効いたか）に言及。
- p13「現実社会への実装」: 教育環境 / 組織設計（「ルールを変える前に、シミュレーションで試す」意思決定支援ツール）/ 地域社会（鎌倉パイロット）。

---

## shibuya-simulation に活かせそうな点

1. **「同じ人・同じ場所、ルールだけを変える」統制条件のコピー化**。当方は既に CRN 同一 seed 列で条件比較を回しているが（第63バッチ endogenous_accept.yaml の 6 セル）、それを**一文の主張に落とす**表現がまだない。「同じ N 人・同じ渋谷。◯◯だけが k* を分けた」は当方でそのまま使える型。
2. **制度転換の時間断続デザイン**。当方の選挙・組織機能に対し、「途中で制度を切り替えて同一個体の適応を見る」実験は未実施。`transitions: [{step: X, ...}]` 相当を conf に足すのは軽い。
3. **肯定的イベント枠（特に `governance_debate`）**。当方の org-emergence 目標に対し、「この共有空間はどう組織されるべきか。誰が、どんな原理で決めるか」を問いかけとしてだけ投げ、組織化を指示しない刺激は、no-fingerprint を保ったまま組織形成を観測する手として使える。
4. **「変わっていないなら正直にそう言え」という反 sycophancy 節**。当方は第62バッチで sycophancy 対策を入れているが、内省プロンプトへの「変化なしを許可する明示句」は追加余地。
5. **提出物生成への投資比率**。本体の 2.4 倍というのは極端だが、当方の make_viewer / make_endo_report の路線をさらに広げる（世界別動画・ピッチ画像の自動生成）判断材料になる。
6. **外部統計で問いの必然性を作る導入**。当方の RQ「世界を変えようとする個体は生まれつきか環境から創発するか」も、起業率・イノベーター比率などの外部統計 2〜3 点を先に置くと同じ効果が出る。

---

## web リサーチ（URL 必須）

- **PERMA（Seligman）と自己決定理論（Deci & Ryan）** — 本作の HFI 6 軸（気分/幸福/自分らしさ/意味/自律/活力）の理論的土台。SDT は自律性・有能感・関係性の 3 基本欲求で、PERMA の Relationships ≒ SDT の relatedness、PERMA の Accomplishment ≒ competence。ただし **SDT の autonomy は PERMA が直接扱わない部分**であり、逆に PERMA の Meaning / Engagement は SDT が直接扱わない。本作が両方を混ぜて 6 軸にしたのは、この相補性を素直に反映している。
  - APA による SDT 解説: https://www.apa.org/research-practice/conduct-research/self-determination-theory
  - Ryan & Deci 原典 PDF: https://uvi.edu/files/documents/College_of_Liberal_Arts_and_Social_Sciences/social_sciences/OSDCD/National_Self_Determination_Richard_Ryan_and_Edward_Deci.pdf
  - PERMA の批判的解説（測定層では SDT と冗長、設計層では相補）: https://yukaichou.com/behavioral-analysis/perma-model-seligman-flourishing-positive-psychology/
  - PERMA は十分か: https://peak.humanperformance.ie/p/why-the-perma-model-and-is-it-enough
- **Park et al. (2023) Generative Agents** — 25 体のサンドボックスで、記憶と reflection を持つエージェントが自発的に連合形成・招待の伝播・共同イベントの調整を行った。本作の「満月のワークショップが自発的に生まれた」はこの系譜の再現。
  - サーベイ内の位置づけ: https://arxiv.org/html/2402.01680v2
- **LLM エージェントを制度/政策のエージェンシー表現に使う研究** — 「LLM で制度的エージェンシーを表現する機会と課題」（Earth System Dynamics 2025）。本作のような「制度を変数にする」設計の妥当性と限界（モデル事前学習バイアス等）を論じており、講評の改善提言（qwen2.5:7b バイアス感度分析）と同じ論点を扱う。
  - https://esd.copernicus.org/articles/16/423/2025/
  - 政策向け LLM エージェントシムの有用性検討: https://arxiv.org/html/2509.21868v1
- **World Happiness Report / OECD How's Life** — スライド p2 の出典としてスライド内に明記（日本 55 位・Life Evaluation 6.147、OECD How's Life 2024）。当方では一次資料 URL 未確認のため、数値はスライドの記載どおりとして扱う。
