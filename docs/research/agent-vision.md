# エージェントの「視覚」— 実装方式のリサーチと段階導入計画(調査+計画, 2026-07-20)

> 依頼(ユーザー旨): 「エージェントがシミュレーションの中で**視覚**を使えるようにしたい。
> ビューアの実装を生かして、**推論時にエージェント視点(POV)の画像を送る**方式で実現できそうだが、
> **他の実装方法がないか web リサーチしながら検討**してほしい。**この実装がシミュレーションに
> 与える影響**も計画レポートに入れてほしい」。
>
> **担当: Opus。本バッチは調査+計画のみ・コード変更なし**(本ファイル1つだけ作成)。
> 制約: 出典 URL 明記・シークレット記載禁止・数値は出典つき or 「推定/計算(前提つき)」と明記(捏造禁止)。
> 目的: (1) 視覚実装の方式空間を先行研究で整理し、(2) 本シムの制約(R1 呼数 k 非依存・既定 OFF
> バイト一致・no-fingerprint・決定論・A5000×7 24GB・在場25万)の内側で実装可能な段階案を出し、
> (3) **シミュレーションへの定量的影響**(予算・研究・ハード・行間レイヤ整合)を示す。

一次資料(本書が依拠):
[`src/society/cognition/deliberate.py`](../../src/society/cognition/deliberate.py)(`build_prompt`=現行の記号的視覚) /
[`viz/make_viewer3d.py`](../../viz/make_viewer3d.py)(three.js ビューア=ユーザー案の転用元) /
[`scripts/export_3d.py`](../../scripts/export_3d.py)(`tracks.json`=時系列エージェント位置) /
[`docs/research/vision-los.md`](vision-los.md)(既実装の擬似視覚=壁 LOS 遮蔽) /
[`docs/research/world-models.md`](world-models.md)(世界モデル・外部化の設計思想) /
[`docs/plans/p2-interstitial-design.md`](../plans/p2-interstitial-design.md)(S2 ダイジェスト/S3 会話=注入 seam) /
[`docs/plans/finals-hardware-plan.md`](../plans/finals-hardware-plan.md)(本選ハード=A5000×7 24GB・req/s 試算) /
[`docs/plans/input-resolution-lod.md`](../plans/input-resolution-lod.md)(注入「件数」LOD の作法)。

---

## §0 要約(TL;DR)と推奨

- **本シムの「視覚」は既に存在する。ただし記号的**。`build_prompt` は
  `場所名 / 周りにある店・場所(nearby_pois)/ 近くにいる人(nearby_names)/ 混雑(crowd_line)/
  馴染みの場所(familiar_places)` をテキストで注入している。加えて壁による遮蔽
  ([`vision-los.md`](vision-los.md))で「見えない相手」も表現済み。**問われているのは
  「視覚を足すか」ではなく「記号的視覚をどこまでリッチにするか/画素画像に踏み込むか」**。

- **先行研究の要点(§2a・§2d)**: 都市/embodied で POV 画像を使う VLM エージェントは実在する
  (V-IRL・EmbodiedCity・CityEQA・CityBench)。しかし**大半は「VLM で画像 → テキスト説明(caption)
  → LLM で行動」**という**知覚と行動を分離**した構成であり、Minecraft 系ベンチ(SmartPlay 系譜)や
  複数の embodied 研究は **「丁寧なテキスト観測が画像入力を上回ることが多い(text often outperforms
  visual inputs)」**と報告している。画像が効くのは**細粒度の空間認識/検出**が本質のタスク(CityCube・
  RoadBench・幾何推論)であって、本シムの主眼(**社会的相互作用・世界改変の創発**)ではない。

- **推奨アーキテクチャ(§4)**: **段階導入**。
  - **v0(全員・追加 LLM 呼ゼロ・最優先)**: 世界側で決定論に組む**構造化シーン記述(セマンティック
    シーングラフ)**を `build_prompt` に数行注入して記号的視覚を強化する。R1/決定論/no-fingerprint と
    完全整合(既存 `crowd_line`/`digest_line`/`input_res` と同型の seam)。
  - **v1(顕著性駆動の稀な画像 POV・前景のみ・VLM 専用 tier)**: ごく一部(熟慮の数%)の
    「見た目が意思決定に効く」瞬間だけ、ビューア転用のヘッドレス POV 画像を VLM に渡す。
    ユーザー案はここに位置づく。**全員画像は予算的に不成立**(§5.1 で定量)。
  - **v2(将来・研究枠)**: 学習型知覚・視覚の言語化キャッシュ・注視モデル等。

- **全員に画像 = 不成立(§5.1)**。200万呼/日を全部 VLM 化すると (i) 画像トークンで prefill が
  +20〜80%、(ii) 画像はプロンプト接頭辞キャッシュ(APC ×2.2)が**効かない**、(iii) VLM は視覚
  エンコーダぶん重い、の三重で**実効スループットがテキストの概ね 1/2〜1/3**に落ち、テキストですら
  ギリギリの 25万在場が wall で破綻。加えて 200万画像/日のレンダ計算(GPU 競合)とストレージ
  (低解像度でも 200〜600 GB/10日・中解像度で TB 級)が乗る。

- **一言の推奨**: **まず v0(構造化シーン記述)を全員に安価で入れ、画素画像は v1 として
  「顕著性ゲートで絞った前景の稀な POV」に限定**する。ユーザーの「ビューア転用 POV+VLM」案は
  v1 として妥当だが、**既定 OFF・呼数 k 非依存・決定論保護(GPU レンダは画素非決定なので画像は
  観測ログであって決定論の入力にしない設計)**を満たす形に整える必要がある。

---

## §1 現状整理 — 本シムは既に「記号的視覚」を持つ

### 1.1 現行の視覚 = `build_prompt` の記号的注入

[`deliberate.py::build_prompt`](../../src/society/cognition/deliberate.py) は、発火時に以下の
「見え」に相当する情報をテキスト行として組む(抜粋・行の順は APC 効率のため固定):

| 視覚に相当する現行の行 | ソース | LOD 対象 |
|---|---|---|
| `場所: {place_name}` | 現在ノード | — |
| `周りにある店・場所: …` | `nearby_pois[:poi_n]` | `input_res.poi_n`(既定3) |
| `近くにいる人: …` | `nearby_names[:people_n]` | `input_res.people_n`(既定=全列挙) |
| `群衆の視覚情報`(`crowd_line`) | crowd_visual 実在集計 | ON時のみ |
| `馴染みの場所: …`(`familiar_places`) | Lynch 認知地図 | 上位3 |
| `間柄 / 同席の身近な人`(relation/household) | relations/household | ON時のみ |

さらに [`vision-los.md`](vision-los.md) の**壁 LOS 遮蔽**(`world/vision.py`・既定 OFF トグル)で
「屋内の間仕切りで隔てられた相手は互いに見えない=交流できない」という**遮蔽の視覚**も実装済み。
つまり本シムの視覚は「**何が見えるか(記号)+ 何が見えないか(遮蔽)**」の記号レイヤとして既に稼働。

### 1.2 既に持っている視覚関連資産(ユーザー案の転用元)

- **3D ビューア** [`make_viewer3d.py`](../../viz/make_viewer3d.py): three.js(r128)。PLATEAU 建物
  LOD2・地形・地下街・歩道橋のメッシュ、`tracks.json` の時系列エージェント位置を描く。カメラは
  `PerspectiveCamera(fov=52)` + **OrbitControls(自由旋回)** で、**エージェント POV カメラは未実装**。
- **時系列位置** [`export_3d.py`](../../scripts/export_3d.py) `tracks.json`: `positions[step][i]=[x,y,w]`
  (w=0 路上 / -1 圏外 / -2 睡眠 / 1000+建物×100+階=屋内)。**向き(heading)は未保存だが連続位置から導出可**。
  P1 で `z` 列が入る予定([`p2-interstitial-design.md`](../plans/p2-interstitial-design.md) §5)。
- **注意点(既知の不一致)**: ビューアはエージェントを `_agentSpot` で表示時に区画内へ**再配置**する
  別ロジックで描いており、**エンジンの実座標(centroid±8m ジッタ)とは一致しない**
  ([`vision-los.md`](vision-los.md) §「エンジンとビューアの間取り一致性」)。POV レンダを厳密化するなら
  この統一(区画配置をエンジン側へ移す)が前提になる。

### 1.3 ユーザー案の位置づけ

「ビューア転用 POV 画像 + VLM」は**技術的には実現可能**(データも 3D 資産も揃う)。ただし本書は
web リサーチの結論として、**(a) 全員には予算的に載らない、(b) 社会シムでは画像より丁寧なテキスト
観測が効くという実証が多い、(c) GPU レンダは画素非決定で決定論と相性が悪い**の三点から、
**「顕著性で絞った前景の稀な POV(v1)」に限定し、全員は非画像の構造化記述(v0)で賄う**ことを推す。

---

## §2 リサーチ結果(2024–2026 優先)

### §2a VLM エージェントの先行例と「画像が効いた/効かなかった」実証

| 先行例 | 環境 | 視覚の扱い | 本シムへの示唆 |
|---|---|---|---|
| **V-IRL**(2024, HKU/NYU) | 実世界地理 + Google ストリートビュー画像 | 視覚検出器 + VLM + LLM を**反復**して知覚→判断→行動。知覚(認識/位置/照合/VQA)と推論を明確に分離 | POV 画像経路の代表。ただし**知覚は別モジュール**で LLM は言語で受ける構成 |
| **EmbodiedCity**(2024, Tsinghua) | UE4 + AirSim の実都市3D | POV 画像を **VLM(GPT-4o)で caption 化 → LLM が回答** | 「画像→テキスト→行動」の分離が主流であることの実例 |
| **CityEQA**(2025) | 都市空間の embodied QA | 階層 LLM エージェント。探索中の視覚を**画像 caption に変換**し LLM が解 | 同上。画像は「言語化してから使う」 |
| **CityBench**(KDD 2025, [arXiv:2406.13945](https://arxiv.org/abs/2406.13945)) | 13都市・8都市タスク・30 の LLM/VLM を評価 | 知覚理解 + 意思決定の2系。**VLM は常識/意味理解タスクでは競争力、しかし地理空間予測・信号制御など
  数値/専門タスクでは失敗** | 本シムの主眼は前者(社会・意味)寄り → 画像の追加価値は限定的の傍証 |
| **SSO/SmartPlay 系譜**([arXiv:2310.01557](https://arxiv.org/abs/2310.01557)) | ゲーム(Minecraft 等) | 視覚観測を**言語記述子に変換**して LLM に渡す(方向つき視覚記述スキーム) | **「丁寧なテキスト観測が視覚入力を上回ることが多い」**を明示 |
| **STEVE-1**([arXiv:2306.00937](https://arxiv.org/abs/2306.00937)) / Voyager / Ghost | Minecraft | STEVE-1 は**生ピクセル入力**で低レベル制御(12/13 タスク)。Voyager/Jarvis-1 は**テキスト状態+スキル
  ライブラリ**で高レベル | 画素が効くのは**低レベル運動制御**。本シムの高レベル社会行動は Voyager 型(言語状態)寄り |
| **IS-Bench**([arXiv:2506.16402](https://arxiv.org/abs/2506.16402)) の ablation | 家庭内 embodied 安全 | 画像に**バウンディングボックスを併記**すると安全認識が大きく改善 | 画像より「**構造化した空間情報の明示**」が効く=v0 の構造化記述を支持 |

**総合的知見**: (1) 都市/embodied で POV 画像 → VLM は確立した系列だが、**大半は知覚と行動を分離**し
LLM は言語で受ける。(2) 複数の実証で**丁寧なテキスト観測 ≥ 生画像**(SmartPlay 系譜・IS-Bench の
bbox 効果)。(3) 画素が本質的に効くのは**細粒度の空間・幾何・低レベル制御**であって、本シムの
**社会的相互作用・世界改変の創発**ではない。→ **本シムでは v0(構造化記述)が費用対効果で優位、
画像は「見た目が本当に効く瞬間」に限る**、という設計判断を裏づける。

### §2b POV レンダリングのパイプライン(コスト相場)

| 方式 | 実体 | 決定論 | コスト相場(推定・出典つき) |
|---|---|---|---|
| **three.js ヘッドレス**(puppeteer/playwright + `--use-gl=egl`) | ビューア HTML をそのまま実行し screenshot | **画素非決定**(GPU/ドライバ依存) | ブラウザ起動が重い。GPU 実描画は可だが「blank screen」等の不安定報告あり([three.js forum](https://discourse.threejs.org/t/headless-rendering/14401)) |
| **headless-gl**(node の WebGL) | three.js を Node で直接描画 | 画素非決定 | ブラウザ不要で軽い。texture 付き描画の実例あり([gist](https://gist.github.com/bsergean/08be90a2f21205062ccc)) |
| **Python ラスタライザ**(pyrender/moderngl/trimesh) | glTF/メッシュを EGL(GPU)or OSMesa(CPU)で offscreen | EGL=画素非決定 / **OSMesa(CPU)=画素決定** | pyrender は EGL/OSMesa 両対応・ML 用途向け。depth 読み出し ~40ms/frame、CPU 律速の描画コールがボトルネックになりうる([pyrender docs](https://pyrender.readthedocs.io/en/latest/examples/offscreen.html) / [issue#149](https://github.com/mmatl/pyrender/issues/149)) |
| **低解像度セマンティックレンダ** | 色=クラス(建物/人/道)で塗る低解像画像 | CPU なら決定 | 画素は「意味ラベルの画像」。VLM でなく**そのまま構造化記述に落とせる**(=v0 と地続き) |

**要点**: **GPU レンダ(EGL/ブラウザ)は速いが画素が非決定**、**CPU レンダ(OSMesa/ソフトウェア)は
決定的だが遅い**([§2e](#2e-決定論と再現性) の中心トレードオフ)。1画像あたりの厳密なミリ秒は
**構成依存で公表相場が薄い**ため本書では約束しない(数十〜数百 ms/画像・並列で緩和、が妥当な作業仮説)。
本選 Day-0 に実測すべき数字(§6 の検収)。

### §2c VLM のスループットと VRAM(24GB 現実)

- **画像トークン数**: Qwen2.5-VL は動的解像度で**1画像あたり可変トークン**。既定レンジは 4〜16384、
  実運用は `min_pixels/max_pixels` で **256〜1280 tokens/画像**に収めるのが標準
  (896×896 ≈ 1024 tokens、式 `H×W/(14×14×4)`)。→ **低解像度に振れば ~256 tokens/画像**まで下げられる
  ([Qwen2.5-VL blog](https://qwenlm.github.io/blog/qwen2.5-vl/) / [HF discussion](https://huggingface.co/Qwen/Qwen2-VL-7B-Instruct/discussions/47))。
- **スループット**: Qwen2.5-VL-7B は vLLM・A100・concurrency 50 で **~20.89 req/s(画像込み)**
  ([Clore.ai guide](https://docs.clore.ai/guides/vision-models/qwen-vl))。本選機は A5000 級で
  [`finals-hardware-plan.md`](../plans/finals-hardware-plan.md) §0 の「A5000 は A100 比 ~2.7倍遅い」を用いると
  **A5000 1枚で ~7〜8 req/s(推定)**。
- **画像がスループットを削る三要因**:
  1. **prefill 増**: 現行テキスト ~1300 tok 入力([finals §1.1](../plans/finals-hardware-plan.md))に画像
     +256〜1024 tok = **+20〜79%**。本 workload は prefill 支配なので実効はほぼ入力長に反比例。
  2. **APC が効かない**: 画像トークンは各画像固有 → プロンプト接頭辞キャッシュ(sticky で ×2.2 実効)が
     **画像部で無効化**。テキストで効いていた無料レバーが消える。
  3. **視覚エンコーダの固定コスト**: 短系列で throughput **−37.7%** の報告([SqueezeBits](https://blog.squeezebits.com/vllm-vs-tensorrtllm-13-visionlanguage-models-40761));
     長系列では相対的に小さくなるが、encode→projection→inject の prefill 支配は残る。
- **VRAM(24GB)**: Qwen2.5-VL-7B は RTX 3090/4090(24GB)で動作可
  ([HF discussion #18](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct/discussions/18))。ただし KV+視覚
  エンコーダで 24GB は窮屈 → **AWQ/INT4** か **3B/2B 版**が現実的。
- **テキスト4B との混載**: 同一 24GB 上に「テキスト4B」と「VLM 7B」の**両重みを常駐させるのは非現実的**
  (KV が痩せる/OOM)。→ **GPU 単位で役割を分ける(VLM 専用 tier)**のが定石(§5.3)。

### §2d 画像の代替表現(=v0 の中身。テキストで視覚意思決定をどこまで再現できるか)

| 代替表現 | 何を渡すか | 本シムでの実装容易性 | 文献/裏づけ |
|---|---|---|---|
| **セマンティックシーングラフ** | 見えている対象・位置・幾何・空間関係を object-centric な有向グラフに蒸留。**軌跡から決定論再構成**でき、潜在シミュレータ状態に依存しない | 高(世界側の決定論集計。既存 `nearby_pois`/`crowd` の自然な拡張) | scene graph は「軌跡から決定論再構成」される構造表現(§2 の検索所見)。[AriGraph](https://arxiv.org/pdf/2407.04363) が KG 世界モデルを LLM エージェントに接続 |
| **セマンティックグリッド/ASCII マップ** | 周囲を格子で「建物/道/人/店」の記号に | 高(2D 位置から生成) | SmartPlay 等の「視覚→言語記述子」と同型([arXiv:2310.01557](https://arxiv.org/abs/2310.01557)) |
| **注視対象リスト**(salient objects) | 「今、視野内で目立つもの」上位 N を距離・向き付きで | 高(LOS + 距離で決定論選抜。`vision-los.py` と接続) | IS-Bench の bbox 併記が効く=**明示的空間情報**が有効([arXiv:2506.16402](https://arxiv.org/abs/2506.16402)) |
| **方向つき視覚記述**(directional scheme) | 「北にビル群、右手にスクランブル、正面に人だかり」等の一人称記述 | 中(heading 導出が要る) | SmartPlay の Minecraft 記述スキームそのもの |
| **CLIP 埋め込み**(画像→ベクトル) | 画像を数値ベクトルにして状態に格納 | 低(埋め込みモデルの追加呼・LLM は直接読めない) | 埋め込みは検索/類似には有用だが LLM プロンプトに直接は載らない。**決定論なら v0 の記号化が優位** |
| **「見え」の言語化キャッシュ** | 場所×時間帯×天気ごとに「見え」を一度だけ言語化して**キャッシュ再利用** | 中(決定論キー設計が要る) | 呼数を増やさず「画像らしさ」を近似。v2 候補 |

**結論(§2d)**: 本シムの主眼(社会的相互作用・世界改変)に対しては、**セマンティックシーングラフ +
注視対象リスト + 方向つき記述**の組み合わせで「視覚的意思決定」の大半を**追加 LLM 呼ゼロ・決定論・
no-fingerprint** で再現できる。これが v0 の中身。画素画像が上乗せする価値は「細粒度の見た目判断」に
限られ、それは v1 の稀な POV で足りる。

### §2e 決定論と再現性

- **CPU/ソフトウェアレンダは画素決定的**: 「同じ入力 → どのマシンでも同じ画像」([digitalcitizen](https://www.digitalcitizen.life/how-software-rendering-differs-from-hardware-acceleration-and-why-it-still-exists/))。
- **GPU レンダは画素非決定**: 同一形状でも GPU 世代・ドライバで FMA・丸め・加算順が違い**画素が一致しない**
  ([EigenAI arXiv:2602.00182](https://arxiv.org/pdf/2602.00182) / [WebGL fingerprint](https://scrapfly.io/web-scraping-tools/webgl-fingerprint))。
- **本シムへの含意(重大)**: 画像を**行動の決定論入力にすると R1/決定論が壊れる**(同 seed でも
  ハードが違えば画像が変わり→ VLM 出力が変わり→ 行動が変わる)。したがって **v1 では画像を
  「観測ログ/前景の稀な入力」に留め、決定論の骨格(発火・乱数・呼数)は画像に依存させない**設計が必須。
  もし決定論を厳密に守るなら **CPU ソフトウェアレンダ(OSMesa)**を選ぶ(遅いが画素決定)か、
  **画像 → 決定論の記号記述に一旦落として**からプロンプトに入れる(=v0 に合流)方式にする。
- **キャッシュ可能性**: 同一状態(場所×時間帯×天気×近傍構成)→ 同一「見え」なら**言語化 or 画像を
  キャッシュ**でき、レンダ/VLM の反復コストを大幅削減できる(§2d の言語化キャッシュ)。

---

## §3 実装方式の比較表(ユーザー明示要望)

凡例: コスト = 追加 LLM/VLM 呼・トークン・レンダ時間・VRAM。品質 = 視覚的意思決定への寄与(私見)。
工数は**推定**(本シムの seam 作法=既定 OFF トグル+専用集計 を前提)。

| 方式 | 追加呼 | 追加トークン | レンダ | VRAM | 決定論 | 品質期待 | 工数(推定) |
|---|---|---|---|---|---|---|---|
| **A. 現状維持**(記号的視覚のまま) | 0 | 0 | なし | 0 | ◎ | 基準 | 0 |
| **B. v0: 構造化シーン記述強化**(全員・シーングラフ+注視リスト+方向記述) | **0** | +数十〜百 tok | なし | 0 | ◎(世界側決定論) | **中〜高**(社会行動に十分) | **中**(2〜4日) |
| **C. ユーザー案: ビューア転用 POV 画像+VLM(全員)** | 全呼が VLM 化 | +256〜1024 tok/呼・**APC 無効** | **200万/日**(GPU 競合) | VLM 専有で不足 | ✕(GPU 画素非決定) | 高だが**過剰** | **大**+**不成立**(§5.1) |
| **D. v1: 顕著性駆動の稀な POV+VLM**(前景の数%のみ・VLM 専用 tier) | 熟慮の数%のみ VLM | 同上だが件数少 | 2万〜10万/日(専用枠) | 1〜2枚を VLM 占有 | △(画像は観測/前景入力に限定) | 高(効く瞬間に限定) | **大**(1〜2週) |
| **E. ヘッドレス専用レンダ(セマンティック低解像・CPU)**→ 記号化 | 0(記号化は決定論) | +数十 tok | CPU 数十〜数百ms/画像 | 0 | ◎(CPU 決定) | 中(v0 と同等を画像経由で) | 中〜大 |
| **F. ハイブリッド(推奨): 通常 v0・顕著時のみ v1)** | 前景の数%のみ | 通常 v0・稀に画像 | 稀 | VLM 専用 tier | ◎(骨格)+ △(画像は非決定入力を隔離) | **最良**(費用対効果) | 大(v0→v1 の順で段階) |

**読み方**: **B(v0)は追加呼ゼロ・決定論◎で全員に載る**唯一の選択。**C(全員画像)は §5.1 で
不成立**。**D(v1)は「効く瞬間だけ」に絞れば現実的**。→ **F(ハイブリッド)= B を土台に D を
重ねる**のが本書の推奨。

---

## §4 推奨アーキテクチャ(段階案)

### v0 — 構造化シーン記述の強化(全員・低コスト・最優先)

- **中身**: 世界側に**決定論のシーンビルダ**を作り、発火時に `build_prompt` へ 2〜4 行を注入:
  - `視界: 正面にスクランブル交差点、右手に109、頭上に歩道橋`(方向つき記述。heading は連続位置から導出)
  - `目立つもの: 人だかり(20m先)・大型ビジョン・警官`(注視対象リスト=LOS+距離で決定論選抜)
  - `空間: あなたは歩道橋の上・地上の群衆を見下ろす`(z/レイヤ由来の垂直関係。P1 の z 列と接続)
- **制約整合**: 既存 `crowd_line`/`digest_line`/`interstitial_digest` と**同型の seam**。既定 OFF で
  ゴールデン L1 バイト一致、追加 LLM 呼ゼロ(R1=呼数 k 非依存)、注入は「件数」LOD(`input_res`)対象、
  因子名を書かない(no-fingerprint)。**GPU も VLM も不要**。
- **対象**: **全員**(在場25万に載る唯一の視覚強化)。

### v1 — 顕著性駆動の稀な画像 POV(前景のみ・VLM 専用 tier)

- **中身**: **顕著性ゲート**(既存 `drive.py` の閾値発火と同型)が「見た目が意思決定に効く」と判定した
  **ごく一部の熟慮**でのみ、エージェント位置・heading にカメラを置いた **POV 画像**をヘッドレスで
  レンダし、**VLM 専用レプリカ**に投げる。ユーザー案(ビューア転用)はここ。
- **絞り方の例**(いずれも客観条件=R1 準拠): 初訪問ノード / 群衆・災害・イベントの現場 / 前景
  (観察対象近傍)エージェントのみ / v0 の注視リストが「異常」を示した時。**背景個体は v0 のみ**。
- **決定論の隔離**: 画像は**観測ログと「前景の稀な入力」に限定**し、発火・乱数・呼数の骨格は画像に
  依存させない(§2e)。厳密決定論が要る比較実験では **v1 を OFF** にして v0 と同一 seed で回せる。
- **対象**: 前景の数%(§5.1 で 2万〜10万画像/日規模)。

### v2 — 将来(研究枠)

- 「見え」の言語化キャッシュ(場所×時間帯×天気 → 一度言語化して再利用)、注視/馴化モデル(何に
  目が行くかの個人差)、CPU セマンティックレンダ → 記号化の常時経路、学習型知覚。いずれも本選後の
  探索枠(実装前アジェンダで要すり合わせ)。

---

## §5 シミュレーションへの影響分析(ユーザー明示要望)

### 5.1 予算試算(在場25万・前提と計算を明示)

**前提**(出典): 在場25万・全員思考 → **~200万 LLM 呼/日**(朝計画25万 + 夜内省25万 + 顕著性熟慮
~6/人日×25万 ≈ 150万)。主力テキスト4B・**実効 ~38 req/s(prefix cache 込)**(依頼前提)、
別試算では 8B INT4 で **~21 req/s**([finals §1.2](../plans/finals-hardware-plan.md))。テキスト
プロンプト ~1300 tok 入力/~320 tok 生成([finals §1.1](../plans/finals-hardware-plan.md))。

**ケース C(全員に画像=毎熟慮に POV)— 不成立の定量**:
- **LLM 側**: 200万呼が全て VLM 化。実効スループットは §2c の三要因で**テキストの概ね 1/2〜1/3(推定)**。
  → 200万呼を捌く LLM 時間が**2〜3倍**。テキストですら 25万は LLM と非 LLM の両律速で「streaming 必須の
  ギリギリ」([finals §0.1](../plans/finals-hardware-plan.md))なので、**2〜3倍増は wall で破綻**。
- **レンダ側**: 200万画像/日。GPU ヘッドレスは楽観 10ms/画像でも **~20,000 GPU-秒/日 ≈ 5.6 GPU時間相当**
  だが、7枚は全て LLM で飽和 → **レンダ用 GPU を別に確保できない(競合)**。CPU レンダなら数十〜数百ms/画像
  で **200万×0.1s = 20万 CPU-秒/日 ≈ 55 CPU時間/日**(並列で緩和するが多コアを恒常占有)。
- **ストレージ**: 200万画像/日。低解像度 JPEG ~10〜30KB でも **20〜60 GB/日 → 10日で 200〜600 GB**、
  中解像度なら **TB 級**。ログ肥大で観測パイプライン([finals §4.2 の streaming 化](../plans/finals-hardware-plan.md))を直撃。
- → **結論: 全員画像は成立しない(計算)**。

**ケース D(v1: 顕著性駆動・熟慮の 1〜5% に画像)— 現実的**:
- 画像数 = 200万 × 1〜5% = **2万〜10万画像/日**。
- **VLM 容量**: A5000 1枚で Qwen2.5-VL-7B ~7〜8 req/s(§2c 推定)→ **1枚で ~60〜70万呼/日**。2万〜10万は余裕。
  ただしテキストが 7→6枚に減り**テキスト容量 −14%(推定)**。
- **レンダ**: 10万×10ms(GPU)= 1000 GPU-秒/日 ≈ 0.28 GPU時間/日。CPU でも 10万×0.1s ≈ 2.8 CPU時間/日。
- **ストレージ**: 10万×20KB = 2 GB/日 → 10日 20 GB。現実的。
- → **v1 は載る**。「効く瞬間だけ」に絞る顕著性ゲートが鍵。

**ケース B(v0: 構造化記述)— 最安**:
- 追加 LLM 呼ゼロ・追加トークン数十〜百・レンダ不要・VRAM ゼロ。**在場25万に無条件で載る**。

### 5.2 研究への影響(R1・決定論・観測・行動品質)

- **R1(呼数 k 非依存)**: v0 は**追加呼ゼロで自明に準拠**。v1 は「画像を投げる条件」を**客観量のみ
  (物理位置・訪問履歴・イベント・前景フラグ)**で組み、**k 由来量(grievance/efficacy 等)を一切
  ゲートに入れない**こと。さらに「画像あり群/なし群で LLM 呼数の分布が交絡しないか」を検証する
  **呼数 k 乖離テスト**を新設(S7 方針キャッシュと同じ関門作法。[p2 §3](../plans/p2-interstitial-design.md))。
  画像は**呼の中身**を変えるので、**画像の有無が発火数・熟慮数と独立**であることをブラインドで担保する。
- **決定論**: §2e の通り **GPU 画素非決定は致命的**。v1 は**画像を決定論の骨格から隔離**(観測/前景入力
  限定・既定 OFF で v0 と同一 seed 再現)。厳密決定論の比較実験は v1 OFF で回す。CPU 決定レンダは
  選択肢だが遅い。
- **観測(画像ログ保存量)**: §5.1 の通り全員画像は保存量で破綻。v1 なら 10日 ~20 GB で可。**画像は
  parquet でなくサイドカーの画像ストア + イベントに参照キー**を持たせる設計(観測 streaming と整合)。
  研究価値: 「エージェントが実際に何を見ていたか」の**事後可視化・査読用の証跡**になる(k* データの
  定性補強)。
- **行動品質(創発・組織形成への寄与)**: §2a の実証は**社会行動では画像の限界効用が小さい**ことを示す。
  期待できるのは (i) **場所の見た目に根ざした発話の具体性**(定型の情景報告を減らす)、(ii) **群衆・
  災害・イベント現場での状況即応**、(iii) **注視の個人差**が行動個体差(k の素材)を生む可能性。
  ただしこれらは**v0 の構造化記述でも大半が取れる**ため、画像の純増分は限定的と見るのが誠実。

### 5.3 ハード(A5000×7 の VRAM 配分・スループット低下)

- **混載しない**: テキスト4B と VLM 7B の**両重みを同一 24GB に常駐は非現実的**(§2c)。
  → **GPU 単位で役割分割**: 例 7枚のうち **6枚をテキスト、1枚を VLM 専用**(AWQ/INT4 or 3B 版)。
- **代償**: テキスト容量が 7→6 で **−14%(推定)**。v1 の画像数が少ないうちは 1枚で足りるが、増えれば
  2枚目を割く(テキスト −28%)。**Day-0 で VLM 実 req/s と v1 発火率を実測して枚数を決める**。
- **レンダの置き場**: GPU ヘッドレスは LLM と GPU を食い合う → **CPU レンダ(OSMesa/pyrender)を
  別コアで回す**か、VLM 専用 GPU の空き時間に相乗り。**Day-0 の実測必須**([finals §2](../plans/finals-hardware-plan.md) に v1 ベンチ項目を追加)。
- **VRAM 目安**: VLM 7B AWQ ≈ 6〜8 GB 重み + KV + 視覚エンコーダ → 24GB に収まるが `max-num-seqs` は
  テキストより保守化。3B/2B 版なら余裕。

### 5.4 行間レイヤ(S2 ダイジェスト・S3 会話)との整合

- **S2(ナラティブ補間ダイジェスト)**: 前回発火以降のイベントを**客観列挙**するのが S2 の役目
  ([p2 §1](../plans/p2-interstitial-design.md))。**視覚情報も「客観の見え」としてダイジェストに
  1行足せる**(例: 「歩道橋から群衆を見た/初めての路地を通った」)。**意味づけは夜内省の LLM の仕事**
  という S2 の原則を守り、視覚も**意味づけない客観記述**で入れる(v0 と同じ規律)。既定 OFF で
  バイト一致・追加呼ゼロ。
- **S3(会話3層)**: 会話の話題・スタンスは両者状態からの決定論写像。**「今この場所で何が見えているか」を
  会話プロンプトの `場所×注視対象` として供給**すると、会話の具体性が上がる(v0 の注視リストを
  会話 seam にも配る)。**追加呼ゼロ**で S3 の機械効果と両立。
- **入力解像度 LOD**: 視覚行は `input_res` の「件数」LOD 対象に含める(注視対象 N・シーングラフ深さ)。
  ON でも変わるのは件数だけ=**呼数・乱数・発火は不変**([input-resolution-lod](../plans/input-resolution-lod.md) の作法)。

---

## §6 実装フェーズ分割・対象ファイル・工数・検収基準

> いずれも [`ask-before-extending`] / [`pre-coding-alignment`] に従い**実装前アジェンダでユーザー合意後に着手**。
> 本書は設計まで(コード変更なし)。工数は**推定**。

| Phase | 内容 | 主な対象ファイル | 工数(推定) | 検収基準 |
|---|---|---|---|---|
| **v0-1** | シーンビルダ(世界側・決定論)。方向つき記述・注視対象リスト・垂直関係 | 新規 `src/society/world/scene_desc.py`、`cognition/deliberate.py`(注入 seam)、`world/vision.py`(LOS 流用) | 2〜3日 | 既定 OFF で **L1 バイト一致** / ON でも呼数・乱数・発火不変(R1) / mock ≤24step green / 因子名非注入(no-fingerprint) |
| **v0-2** | S2 ダイジェスト・S3 会話への視覚行の配線 | `cognition/reflection.py`(S2)、会話 scheduler(S3)、`input_res` LOD 拡張 | 1〜2日 | 既定 OFF バイト一致 / S2 は「意味づけない客観記述」規律 / LOD は件数のみ変化 |
| **v1-1** | POV カメラ + ヘッドレスレンダ(まず CPU 決定 or GPU 実測)。`_agentSpot` 統一(区画配置をエンジンへ) | `viz/make_viewer3d.py`(POV カメラ)、新規 `viz/render_pov.py`、`scripts/export_3d.py`(z/heading) | 1週 | 同状態→同画像(CPU 決定を確認)/ レンダ ms/画像を Day-0 実測 / ビューア座標とエンジン座標の一致(統一後) |
| **v1-2** | 顕著性ゲート + VLM 専用 tier 配線 + 画像ストア(サイドカー) | `cognition/drive.py`(ゲート)、LLM フリート設定(VLM tier)、`observer/logger.py`(画像参照キー) | 1週 | ゲートが**客観量のみ**(k 由来ゼロ)/ **呼数 k 乖離テスト green**(新設)/ 既定 OFF で v0 と同一 seed 再現 / 画像ログ量が予算内 |
| **本選 Day-0** | v1 のベンチ項目追加(VLM req/s・レンダ ms・v1 発火率・VRAM) | [`finals-hardware-plan.md`](../plans/finals-hardware-plan.md) §2 に1項目 | 併合 | 実測で VLM 枚数・v1 発火率上限を確定 |

**推奨着手順**: **v0-1 → v0-2(ここまでで全員の視覚強化は完了・低リスク)**。v1 は**本選の余力次第**
(GPU 枚数・非 LLM 律速の残り)。全員画像(ケース C)は**採らない**(§5.1)。

---

## §7 出典一覧(URL・本調査の Web 検索に出現したもの)

**VLM/embodied エージェント(都市・ゲーム)**
- V-IRL: Grounding Virtual Intelligence in Real Life — [project](https://virl-platform.github.io/) / [arXiv:2402.03310](https://arxiv.org/abs/2402.03310)
- EmbodiedCity: A Benchmark Platform for Embodied Agent in Real-world City — [arXiv:2410.09604](https://arxiv.org/html/2410.09604) / [PDF](https://fi.ee.tsinghua.edu.cn/~gaochen/papers/EmbodiedCity.pdf)
- CityEQA: A Hierarchical LLM Agent on Embodied QA in City Space — [arXiv:2502.12532](https://arxiv.org/pdf/2502.12532)
- CityBench: Evaluating the Capabilities of LLMs for Urban Tasks (KDD 2025) — [arXiv:2406.13945](https://arxiv.org/abs/2406.13945) / [GitHub](https://github.com/tsinghua-fib-lab/CityBench)
- SmartPlay: A Benchmark for LLMs as Intelligent Agents — [arXiv:2310.01557](https://arxiv.org/abs/2310.01557) / [OpenReview](https://openreview.net/forum?id=S2oTVrlcp3)
- STEVE-1: A Generative Model for Text-to-Behavior in Minecraft — [arXiv:2306.00937](https://arxiv.org/pdf/2306.00937) / [GitHub](https://github.com/Shalev-Lifshitz/STEVE-1)
- IS-Bench: Interactive Safety of VLM-Driven Embodied Agents(bbox ablation)— [arXiv:2506.16402](https://arxiv.org/pdf/2506.16402)
- See and Think: Embodied Agent in Virtual Environment — [ECCV 2024 PDF](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/01280.pdf)
- AriGraph: Knowledge Graph World Models for LLM Agents — [arXiv:2407.04363](https://arxiv.org/pdf/2407.04363)

**POV レンダリング(ヘッドレス・ラスタライザ)**
- three.js headless rendering(forum)— [discourse](https://discourse.threejs.org/t/headless-rendering/14401) / [headless-gl gist](https://gist.github.com/bsergean/08be90a2f21205062ccc)
- pyrender offscreen(EGL/OSMesa)— [docs](https://pyrender.readthedocs.io/en/latest/examples/offscreen.html) / [GPU issue#149](https://github.com/mmatl/pyrender/issues/149)
- moderngl headless — [DeepWiki](https://deepwiki.com/moderngl/moderngl/5.2-headless-rendering)

**VLM スループット/VRAM/画像トークン**
- Qwen2.5-VL blog(動的解像度・トークン式)— [qwenlm.github.io](https://qwenlm.github.io/blog/qwen2.5-vl/)
- Qwen2-VL「1画像は何トークンか」— [HF discussion #47](https://huggingface.co/Qwen/Qwen2-VL-7B-Instruct/discussions/47)
- Qwen2.5-VL-7B の VRAM 要件 — [HF discussion #18](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct/discussions/18)
- Qwen2.5-VL vLLM req/s(A100・concurrency 50)— [Clore.ai guide](https://docs.clore.ai/guides/vision-models/qwen-vl)
- vLLM vs TensorRT-LLM: Vision-Language Models(throughput −37.7%)— [SqueezeBits](https://blog.squeezebits.com/vllm-vs-tensorrtllm-13-visionlanguage-models-40761)

**決定論・再現性**
- Software vs Hardware rendering(CPU 決定・GPU 非決定)— [digitalcitizen](https://www.digitalcitizen.life/how-software-rendering-differs-from-hardware-acceleration-and-why-it-still-exists/)
- GPU 浮動小数点非決定 / EigenAI Deterministic Inference — [arXiv:2602.00182](https://arxiv.org/pdf/2602.00182)
- WebGL fingerprint(GPU/ドライバで画素差)— [scrapfly](https://scrapfly.io/web-scraping-tools/webgl-fingerprint)

**本シム内の関連ノート(既存)**
- [`vision-los.md`](vision-los.md)(壁 LOS 遮蔽=既実装の擬似視覚)
- [`world-models.md`](world-models.md)(世界状態の外部化=設計思想)
- [`p2-interstitial-design.md`](../plans/p2-interstitial-design.md)(S2/S3 の注入 seam)
- [`finals-hardware-plan.md`](../plans/finals-hardware-plan.md)(A5000×7・req/s 試算)
- [`input-resolution-lod.md`](../plans/input-resolution-lod.md)(件数 LOD の作法)

---

## 未確認事項(事実と推測の区別)

- **一次 PDF は全件は直接取得していない**。arXiv 番号・数値は検索結果本文で確認したもの
  (Qwen2.5-VL のトークン式・レンジ、CityBench の結論、V-IRL/EmbodiedCity/CityEQA の構成、SmartPlay の
  「text ≥ vision」示唆、SqueezeBits の −37.7%、Clore.ai の ~20.89 req/s、pyrender の depth 40ms/frame)。
  巻号・厳密設定は要再確認。
- **スループット/レンダ/VRAM/予算の数値は「推定」または「計算(前提つき)」**。特に:
  - A5000 の VLM req/s(~7〜8)は「A100 比 2.7倍遅い」([finals §0](../plans/finals-hardware-plan.md))からの
    外挿であり**未実測**。**本選 Day-0 の `vllm bench serve`(画像込み)で置換**が必須。
  - レンダの ms/画像は構成依存で公表相場が薄く、本書は**約束していない**(数十〜数百 ms を作業仮説)。
  - 「全員 VLM で実効 1/2〜1/3」「テキスト容量 −14%(1枚 VLM 化)」は三要因からの推定。
  - v1 の発火率(1〜5%)は**設計上の仮置き**で、実際は顕著性ゲートの閾値と較正で決まる。
- **§4/§6 の設計はすべて設計提案(推測)**。実装可否・粒度・対照設計(compute_matched・画像の有無が
  k と交絡しないブラインド検証・呼数 k 乖離テスト)・`_agentSpot` 統一の是非は**実装前アジェンダで
  ユーザー判断**([`pre-coding-alignment`])。
- **「画像より丁寧なテキスト観測が効くことが多い」は複数実証の傾向**であって、本シムの具体タスクで
  同じ結論になる保証はない。v1 を「効く瞬間だけ」に絞れば、この不確実性は小さなコストで検証できる
  (v0 単独 vs v0+v1 のブラインド A/B)。
