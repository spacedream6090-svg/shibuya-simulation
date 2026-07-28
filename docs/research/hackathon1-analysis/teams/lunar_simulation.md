# lunar_simulation(kaii・17位・30.0)

| 軸 | スコア | 内訳(Run1/Run2) |
|---|---|---|
| A. 創発設計 | 8.0 | 8 / 8 |
| B. 世界設定 | 7.0 | 7 / 7 |
| C. 発展性 | 7.0 | 7 / 7 |
| D. 技術実装 | 8.0 | 8 / 8 |
| **合計** | **30.0/40** | 30 / 30 |

- リポジトリ: https://github.com/kaii0624/lunar_simulation
- スライド: `slides/17-2267-lunar_simulation.pdf`(12ページ・テキスト抽出可)
- 規模感: フラット構成(ディレクトリは `events/` `visualization/` `docs/` のみ)。中核は `agent.py`(27KB)/`simulation.py`(35KB)/`llm_client.py`(30KB)/`main.py`(13KB)/`utils.py`(3.4KB)/`visualization.py`(19KB)。**レポート生成スクリプトが 8 本で計 290KB 超**(`make_20run_comparison_report.py` 33KB、`make_10run_comparison_report.py` 49KB、`make_presentation.py` 41KB 等)と、シム本体よりも「実験集計・提出物生成」側が重い構成。テストディレクトリは無い。

## どんなシムか

30×30 の月面 2D グリッドに 20 体の LLM エージェントを置き、中央に定員 10 名の `central_lunar_base` を 1 つだけ置く。基地外では毎ステップ酸素 −2.5、基地内(定員内)では消費ゼロ、初期酸素 100、ゼロで死亡。**20 体 vs 定員 10** という、数学的に必ず半数が締め出される構造的ジレンマが唯一の創発ドライバである。会話は半径 5、基地の入口付近だけ半径 2 で内外越境通信ができる。LLM(既定 `gemini-3.1-flash-lite-preview`)には座標・酸素・占有率などの数値だけを渡し、「定員超過なら退去せよ」の類の戦略指示は一切書かない。ステップは「①メッセージ判断 → ②送信 → ③アクション判断 → ④移動 → ⑤酸素消費」の同期 4〜5 フェーズ。**thinking_level(minimal/low)× collective_prompt(off/on)の 2×2 を各 5 ラン、計 20 ラン実走**している。

## 講評の要点

**強み(eval)**
- 世界ルールが精密。3 層の酸素消費レート、正方基地+入口ゾーン(`utils.py:78-106`)、エリア別の会話可能範囲がすべて分離設計されている。
- プロンプトは数値データのみで戦略指示ゼロ(`agent.py:340-348`, `agent.py:443-451`)。「20 人 vs 定員 10 人」の構造的緊張が設計レベルの創発圧力を生む。
- **2 段階プロンプトの情報設計**: Phase 1 のメッセージ判断ではエージェント自身の座標を渡さず、Phase 3 のアクション判断で初めて座標を含める(`agent.py:280,332` vs `agent.py:361,416`)。「通信では位置を伏せ、行動判断では使う」という意図の表現。
- Gemini の `responseMimeType: application/json` + `thinkingLevel`、指数バックオフ、`ThreadPoolExecutor` 8 並列、`MockLLMClient`(約 260 行)。API key の redact と `config_used.yaml` / `experiment_conditions.md` 出力。
- イベントは `EVENT_TYPES` 辞書登録パターン(`events/registry.py:10-37`)+`SimulationEvent` 基底クラスの `should_fire`/`apply`/`manifest` 分離。

**弱み(eval)**
- `~N steps until depletion`(`steps_to_death` 前計算)は便利だが軽い行動誘導。raw な `oxygen_level` + `consumption_rate` のみを渡す版を実験オプション化すべき、と提言されている。
- **`random.seed` が無く再現性が担保されない**(`_generate_random_position` が `random.randint` を直呼び)。
- 世界の物理が浅い。基地 1 つ・地形なし・4 方向移動のみ。イベント実装は `rescue_announcement` 1 種のみ。
- README に「Future Work」「想定応用(資源配分・避難所運用・ICU ベッド管理)」章が無い。`collective_prompt` の効果検証結果も README に書かれていない(**実際にはスライド側に載っているのに、README で訴求できていない**)。

**_eval_review の所見**
- 引用検証ヒット率ほぼ 100%、「元評価 30.0/40 を支持。検証側からの修正提案なし」。
- 補強できる点として 2 つだけ指摘: (1) A の「20 人 vs 定員 10 人」は単なるシェルター不足ではなく**数学的に必ず半数が締め出される**強い対立圧力でありもっと高評価でもよい、(2) D の `MockLLMClient` は「オフライン検証可能」より一段強く、**API 課金ゼロでフル比較実験ができる**規模。いずれもスコアは動かさないと判断。

## コード実査で面白かった点

1. **イベントの「カタログ YAML」という発想** — `event_catalog.yaml` はコードではなく*人間と LLM が読むための拡張手順書*で、`trigger_condition` を自然言語で書き、`scope`、`side_effects`(「全生存エージェントの received_messages に注入」「messages.jsonl に broadcast 1 件」「event_log.jsonl に 1 件」)、`config_fields.required/optional`、そのまま貼れる `example` まで含む。実装 3 行(`events/<type>.py` 作成 → `registry.py` 登録 → `config.yaml` に辞書追加)の手順もヘッダコメントに書いてある。ドキュメントを機械可読な YAML に落とす形。

2. **`SimulationEvent` の `manifest()`** — イベントが自分の状態を `disabled`/`pending`/`fired` の 3 値で自己申告し、それが `event_manifest.json` として実行成果物に出る。「この実験でどのイベントが実際に発火したか」が後から機械的に検証できる。介入の有無を後追いできるのは対照実験として重要。

3. **`rescue_announcement` の中身が「創発の反証装置」になっている** — カタログの example は step 75 に「救助ローバーが step 100 に到着する。全員分の容量と酸素がある。**生存のために基地内にいる必要はない**」と全員に放送する。これは基地占有規範が創発した後で「その規範を無効化する外生情報」を注入し、規範がどれだけ粘るかを見る介入になり得る。実験には未使用(`events: []`)だが設計としては鋭い。

4. **設定バリアントが 4 つ** — `config.yaml` / `config_collective.yaml` / `config_low_thinking.yaml` / `config_low_thinking_collective.yaml`。2×2 の各セルが 1 ファイルに対応しており、`--config` の差し替えだけでセルが切り替わる。eval が数え落としていた 4 本目を _eval_review が拾っている。

## 説明資料(スライド)より

リポの README には無く、スライドにしかない実験結果・主張。**shibuya-simulation にとって本チームの最大の価値はここ**。

**実験規模**: 4 条件 × 5 ラン = 20 ラン。20 エージェント × 100 step × 2 API コール(行動+会話)× 4 条件 = **16,000 API コール**(p7)。

**主要結果(p9)** — 生存率は全条件で 50%(10/20)と**同一**。差は「いつ死ぬか」だけに出た。

| 条件 | 平均死亡ステップ | 改善幅 |
|---|---|---|
| Minimal / 通常 | 47.7 | (基準) |
| Minimal / 集団 | 53.1 | +5.4 |
| Low / 通常 | 50.6 | +2.9 |
| Low / 集団 | 60.1 | +12.4 |

集団プロンプトの中身は**たった 1 行**(`You are operating as part of a group under survival constraints.`)の追加(p4)。それだけで平均死亡ステップが +5.4〜+12.4 動いた。ただし作者自身が「**各条件内の標準偏差が大きく、現時点では傾向として捉えるにとどめる必要がある**」と正直に註記している(p12)。

**ルール創発①「プロトコル名の自己発明と伝播」(p10)** — 条件 Minimal×集団。プロンプトに「プロトコル」の語は一切無いのに:
- Step 9: Agent 2 が `as per our survival protocol` と初めて命名
- Step 10: Agent 17 が同じ表現をそのまま引用・採用
- Step 11: Agent 1 が全体放送で `rotation protocols` を提案
- Step 13: **定冠詞つきの `the rotation protocol` として既存ルールに昇格**(`the rotation protocol dictates you are next in line.`)

**創造から規範化まで 4 ステップ**。しかもこのランでは譲り合いは*起きず*、「基地内に留まり酸素を節約する」という規範が強化されて誰も退出しない膠着に至った。

**ルール創発②「数値閾値が条約になる」(p11)** — 条件 Low×集団の最良ラン。
- Step 13: Agent 6 が私的なつぶやきとして「酸素が 20.0 を割ったら助けを求める」と発言
- Step 17: 別エージェントが `critical threshold` として参照
- Step 22: 5 体以上が同時に `as per our protocol` と引用
- Step 33: Agent 1 が `I have reached the 20.0 oxygen threshold. I am ready to initiate the rotation protocol as previously discussed. Please vacate the base.` と**退出を要求・強制**

作者の観察: 「**誰も合意した記憶のないルールが拘束力を持った**」。`as previously discussed` という虚偽の合意履歴の参照が正当化の根拠になっている。

**最大の知見(p12-3)**: 同じ「自己ルール生成」という現象が、条件によって**正反対の方向に機能した**。Minimal/通常では「留まって節約する」規範 → 膠着 → 早死に。Low/集団では「20.0 以下で退出要求」という協調規範 → 生存時間延長。作者は「どちらの規範が創発するかの分岐点が何で決まるかは 5 ラン では判断できなかった」と正直に限界を書いている。

## shibuya-simulation に活かせそうな点

- **「規範の創発 → 定冠詞化」を検出器として実装できる**。lunar が観察した「無冠詞での命名 → 他者引用 → 定冠詞 `the X` での参照 → `as per our X` / `as previously discussed` による強制」という 4 段階は、shibuya の `coin_label` / ラベル伝播の観測にそのまま移植可能な**言語形式ベースの規範化指標**。特に「定冠詞つきで参照された初出ステップ」と「`as per our`/`as previously discussed` の初出」は、単なる語の頻度より遥かに強い「規範として拘束力を持ったか」のシグナルになる。当プロジェクトの no-fingerprint 原則とも矛盾しない(観測側だけの追加)。
- **「同一設計から正反対の規範が創発する」という分岐の存在**は k* 探索に直結する警告。R²(k) 掃引で「相転移点」を探すとき、同一 k で*膠着規範*と*協調規範*が二極化していれば、平均値は k* を隠してしまう。ラン単位で規範のタイプを分類してから集計すべき(第63バッチの sign-flip permutation はラン単位置換なのでこの分類とも相性が良い)。
- **`event_catalog.yaml` 方式**: shibuya の介入イベントも、実装だけでなく「trigger_condition / scope / side_effects / config_fields / example」を機械可読 YAML でカタログ化すると、審査員にも自分にも「どの介入が可能で、実験でどれを使ったか」が一目で示せる。`manifest()` の `disabled/pending/fired` 3 値と `event_manifest.json` 出力は当プロジェクトの「観測分離」原則と親和性が高い。
- **「1 行のプロンプト差分」を独立変数にする実験設計**: `You are operating as part of a group under survival constraints.` の有無だけで平均死亡ステップが動く。shibuya でも「1 行だけ違う」条件を CRN 同一 seed 列で回せば、fingerprint を増やさずに効果量を測れる(第63バッチの endogenous_accept.yaml と同じ枠組みで実装可能)。
- **反面教師 — README に結果を書かないと損をする**: 20 ラン・16,000 API コールの実験を回して規範創発まで観察していながら、C=7.0 の減点理由が「README に Future Work が無い」「collective_prompt の効果検証結果が README に記載されていない」。**成果は提出物の入口(README)に置く**。shibuya の本選提出でも同じ失敗をしないこと。

## web リサーチ

- **Ashery et al., "Emergent social conventions and collective bias in LLM populations", Science Advances 11(20), 2025-05-14** — https://www.science.org/doi/10.1126/sciadv.adu9368 (PDF: https://www.lajello.com/papers/sciadv25emergent.pdf)。分散した LLM エージェント集団に**普遍的に採用される社会規範が自発的に立ち上がる**こと、個々のエージェントには偏りが無くても集団レベルで強いバイアスが生じること、コミットした少数派が既存規範を覆せることを naming game 枠組みで示した。lunar が「survival protocol」「酸素 20.0 閾値」で観察したのはまさにこの現象の 1 事例で、**先行研究の枠組み(naming game)を引用していれば B/C のスコアが伸びた可能性が高い**。shibuya のラベル伝播も同じ文献ラインに接続できる。
- **Gemini `thinkingConfig` / `thinking_level`** — https://ai.google.dev/gemini-api/docs/thinking。MINIMAL / LOW / MEDIUM / HIGH の 4 段階で内部推論の深さを制御。「思考トークンはレスポンスとは別に消費される」「`thinking_level` と `thinking_budget` を同時指定するとエラー」。lunar は下位 2 段階(minimal: max_tokens 192 / low: 512)だけを比較しており、**思考予算そのものを独立変数にする**という発想は当プロジェクトでも使える(shibuya の `reflect/think` 経路の予算を条件化する)。
