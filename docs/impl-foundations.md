# 実装の土台仕様(D10-D17 草案)— 2026-07-03

> [decision-agenda](./decision-agenda.md) 第2部の草案。**ユーザー承認後に scaffold(コードの骨組み)を作る**。
> 方針: D2 で決めた「自前 lean core」の背骨。どれも後から差し替え可能だが、**D12(ログ)と D13(再現性)だけは最初に固めないと後で全部作り直しになる**。

---

## D10. リポジトリ構成・言語・依存管理

**言語**: Python 3.12(vLLM / Hydra / scikit-mobility / NetworkX / pgvector クライアント等、使うものが全部 Python 製のため)。

**依存管理**: **uv**(高速・lockfile 自動・Windows/Linux 両対応)。`pyproject.toml` + `uv.lock` をコミットし、手元 Windows と本選 Linux クラスタで**同じ環境を再現**できるようにする。

**ディレクトリ**(design §11 の seam 一覧を確定版に拡張):
```
shibuya-simulation/
├── docs/                     # 設計・lit・ログ(現状のまま)
├── reference/2d-fire-sim/    # 読み取り参照のみ・import 禁止
├── conf/                     # Hydra 設定(D11)— コードと設定を分離
├── src/society/
│   ├── llm/                  # backend 抽象(mock/vllm)+ router + ★応答キャッシュ(D13)
│   ├── world/                # space(道路網+POI)/ routing(経路探索)/ perception / clock(D15)/ scenario(ショック注入)
│   ├── agents/               # agent / persona(D6 の3段パイプライン)/ memory
│   ├── factors/              # trait/state レジストリ(D5)+ 更新則 seam(OPEN#2)
│   ├── cognition/            # lod(発火ゲート)/ routine(EPR移動・FJ意見 等の cheap 層)/ deliberate(LLM層)
│   │   └── reflection/       # ★ソロ内省 = k の実装部位(D7: 書き戻し on/sham/off)
│   ├── actions/              # 動詞レジストリ(Bundle C)
│   ├── labeling/             # 制約版⇄オープン版スイッチ + 伝播
│   ├── observer/             # ★L1/L2/L3 ログ(D12)+ 事後測定(judge は補助)
│   ├── storage/              # Redis/pgvector/NetworkX の抽象化(D8)
│   └── engine/               # scheduler / simulation / seeds(D13)
├── scripts/                  # run.py / analyze.py / bench.py(実機ベンチ用)
├── tests/                    # D14
└── viz/                      # sim とは別プロセス(読み取り専用の下流)
```

---

## D11. config スキーマ(Hydra)

**考え方**: 「実験の全条件を YAML で宣言し、コードは一切書き換えずに条件を変えられる」状態にする。k×seed×N の掃引も、モデル差し替えも、言語切替も、すべて config。

```yaml
# conf/config.yaml(トップの骨格)
run:        { seed: 42, n_agents: 100, n_steps: 288, out_dir: ... }
k:          { writeback: free }   # free | degraded(α) | sham | off ← D7 の主軸
controls:   { mode: none }        # none | null_series | compute_matched ← D7 対照
model:      { backend: mock }     # mock | vllm。name/quant/lang(ja|en)は下位キー
world:      { scenario: baseline }# baseline | shock_closure | shock_rule ...(D9 摂動カタログ)
lod:        { trigger: surprise, max_llm_per_step: 300 }  # N上限(実測で更新)
labeling:   { mode: constrained } # constrained | open(D9)
rewards:    { enabled: false }    # D9: 既定 off
storage:    { backend: memory }   # memory(開発) | redis_pg(本番)
observer:   { snapshot_every: 12 }
```
- Hydra の multirun で `k.writeback=free,sham controls.mode=...` のように**掃引をコマンド1行で宣言**。
- config 全体は各 run の出力ディレクトリに**そのまま保存**(=どの条件で走ったか常に再現可能)。

---

## D12. ログの正準スキーマ(observer 3層)★全測定の土台【2026-07-03 ユーザーFBで改訂】

**考え方**: 「シミュで起きたことを、あとから何度でも別の角度で分析できる」ために、**イベントを1つの正規形式で全部記録**する。R² も EWS も viz も、全部このログから計算する(シミュ本体は測定を知らない=frame 分離)。

### ★ 移動は「瞬間移動」でなく「経路追従」(ユーザー要望)
旧 2d-fire-sim のようなステップ毎テレポートは廃止。**Google Maps 同様の経路検索→追従**方式:
1. 世界 = **OSM 渋谷の歩行者道路ネットワーク**(ノード=交差点、エッジ=道路。POI は道路網上にスナップ)。
2. エージェントが目的地を決める(EPR/意図)→ **経路探索(A*/Dijkstra, NetworkX)** → エッジ列を保持。
3. 各 step で**歩行速度分だけ経路に沿って前進**(徒歩 ~4.8km/h → 1 step=10分 ≈ 800m。混雑エッジでは減速=キュー遅延が grievance 源)。
4. **毎 step の連続座標 (x,y) を L1 に記録** → 渋谷3D上でリアルな歩行軌跡がそのまま描ける。
- コスト対策: 経路探索は非LLM・OD ペア単位でキャッシュ(同じ出発→目的地は再計算しない)。

### ログの拡張性(ユーザー要望: 「後から絶対追加したくなる」)
**答え: 簡単にできる設計にする。** L1 を「固定列 + kind + payload(JSON)」の**イベントレジストリ方式**にする:
- 新しいログ種類の追加 = **EventKind を1個登録するだけ**(名前+payload の中身を定義)。既存データの変換・スキーマ移行は不要(固定列は変わらず、種類ごとの詳細は payload に入るため)。
- L2 の集計指標も**プラグイン式**(集計関数を1個登録すれば新指標が増える)。

- **L1 イベントログ(個体・追記専用)**: 1行=1イベント。
  `{step, sim_time, agent_id, kind, x, y, z?, payload(JSON), rng_stream, llm_call_id?}`
  - kind 例: `move_segment / route_start / speak / label_adopt / label_coin / reflect / group_join / resource_commit / institution_declare ...`
  - **D1 の連続量(4層書き換え量)は L1 から集計可能**な粒度で設計(誰が・どの層を・どれだけ動かしたか)。
- **★ 追加ログ(ユーザー指定・最初から実装)**:
  1. **新規・専門語彙**: `vocab_coin`(新語の誕生: 発話から新語を検出し語彙IDを付与)/ `vocab_use`(使用)。L2 で「語彙の誕生→普及→死滅」曲線と集団間の専門語彙分化(drift の語彙版)を追える。
  2. **伝播系譜(provenance)**: 広まるモノ(ラベル・語彙・噂・制度案)に **item_id** を付与し、**すべての伝達に `{item_id, from(エージェント|情報媒体), to, channel(対面/SNS/掲示…), step}`** を記録。→ 「何が・誰から誰へ・どの媒体経由で広まったか」の**系譜木(カスケード)を完全再構成**できる。M1b(S字伝播)と complex contagion の実測に直結。
- **L1b LLM 呼び出しログ**: `{llm_call_id, agent_id, model, params, prompt_hash, response_hash, tokens_in/out, cached}` — 本文は応答キャッシュ(D13)に、ログにはハッシュと統計のみ。
- **L2 集団集約(step ごと)**: ラベル採用率・意見分布・conformity 指標・埋め込み分散(崩壊検知 R12)・語彙統計・EWS 用時系列 — **非LLM の後処理**で L1 から生成(プラグイン式)。
- **L3 世界スナップショット(定期)**: POI 状態・資源プール・制度状態・グラフ — リプレイと viz の基準点。
- **形式**: すべて **Parquet + zstd**(列指向・高圧縮・pandas/duckdb で直接分析可)。
- **座標**: **JGD2011 平面直角座標系 系IX**(D9 で確定)。viz はこの L1/L3 を読むだけ(sim⇄viz 疎結合)。

---

## D13. 決定論リプレイ(再現性)★論文の生命線

**考え方**: 「同じ設定・同じ seed なら、いつ誰が走らせても同じ結果」を保証する。LLM は temperature=0 でも完全には同じ応答を返さないので、**初回の応答を全部保存して、再実行時はそれを再生する**(=キャッシュが再現性の実体)。

1. **応答キャッシュ**: key = hash(prompt + model + params)。初回は実呼び出し+保存、リプレイ時はキャッシュ配信。SQLite(開発)/ pgvector 同居 Postgres(本番)。
2. **乱数**: マスター seed から **agent_id ごとに独立ストリーム**を派生(numpy PCG64)。誰かの行動順が変わっても他人の乱数がズレない。
3. **順序決定化**: 並列処理の結果は **agent_id 順に整列してから**世界に適用(実行順に依存しない)。
4. **検証**: 「同一 seed で2回走らせ L1 が bit 一致」を CI テストに(D14)。

---

## D14. テスト方針

- **pytest**。重い物は不要、以下の4種に絞る:
  1. **Mock end-to-end**(最重要): Mock LLM で N=10×20step が無クラッシュ完走し L1/L2/L3 が出る — これが P0 の合格判定そのもの。
  2. **決定論テスト**: 同一 seed 2回 → L1 一致(D13 の検証)。
  3. **seam 契約テスト**: 各レジストリ(factors/actions/labeling/llm backend)が interface を満たすか。
  4. **観測の健全性**: 「engine が因子を名指ししていない」ことの静的チェック(`world_change_drive` 的な直接参照の禁止を grep レベルで担保)。

---

## D15. クロック仕様

- sim 時間の正準 = **整数 step**(1 step = sim内10分、144 step = 1 sim日)。壁時計とは完全分離(30秒/step は本番の目標スループットであって、シミュの意味には関与しない)。
- **昼(6:00-24:00 = 108 step)= 通常解像度 / 夜(24:00-6:00 = 36 step)= 圧縮**(routine のみ+個別睡眠で内省・要約をここに分散 → 負荷平準化)。
- 移動との整合(D12 改訂に合わせ更新): **1 step = 経路に沿って徒歩約800m前進 or 滞在**(混雑で減速)。EPR は「次の目的地の選び方」を担い、移動自体は経路追従。

---

## D16. エラー処理・障害復旧

- **LLM 応答の失敗**(タイムアウト/JSON 崩れ): リトライ最大2回(guided decoding で崩れ自体を抑制)→ それでも駄目なら**そのエージェントはその step を routine(cheap 層)で行動**し、L1 に `fallback=true` を記録(=データから除外・重み付けできる)。**シミュ全体は決して止めない**。
- **vLLM インスタンス障害**: ルータが該当インスタンスを外し残りへ再分配(sticky の割当も再計算)。
- **チェックポイント**: L3 スナップショット+乱数状態+キャッシュで**途中再開可能**に(10日 wall-clock の保険)。

---

## D17. 倫理注記・開発環境・運用【2026-07-03 ユーザー決定で改訂】

- **実名使用(ユーザー決定)**: 場所・施設は**実名を使う**(宮下公園、スクランブル交差点、ハチ公前 等)— 「渋谷を本当に再現している」実感を優先。
- **倫理の線引き(実名採用に伴う残余リスクの扱い)**: 実在の**個人・特定の団体は登場させない**。シミュ内の出来事・発言は**すべて架空である**旨を ETHICS.md と発表資料に明記。abliterated モデルは「RLHF 交絡の統制目的」と README に明記し、生出力は公開しない。
- **開発環境**: 手元 Windows = Mock/小規模(GPU 不要で全ロジック開発可能)→ 本選 Linux クラスタ = vLLM 実機。**backend 切替は config 1行**(D11)。
- **運用**: GitHub リポジトリ(ハッカソン要件=公開)。main 直 push、タグで節目管理(1人開発なのでブランチ運用は最小)。実験は Hydra multirun+出力ディレクトリで管理(MLflow は本選で必要になったら追加)。

---

## 実装順(P0 骨格の中の順番)
1. D10 scaffold + D11 config + **D12 ログ**(骨格)
2. D13 再現性(キャッシュ・RNG)+ D14 テスト1・2
3. world/agents/cognition の最小実装(Mock で M1 配線)
4. D15 クロック・D16 エラー処理を組み込みつつ end-to-end
