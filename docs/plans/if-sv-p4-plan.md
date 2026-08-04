# IF-U1 × SV-U1 × P4較正 — 3レーン統合実装計画

> 2026-08-05 ユーザー承認「IF-U1とSV-U1、P4較正の実装を始めてほしい。実装前に文献リサーチ」。
> 体制: Fable 5=計画・検収・コミット / Opus 5=実行役(コミット禁止)。
> ステータス: **リサーチ中**(3本並行)→ 本節を確定後にバッチ着手。
> R1準拠: 全新機能既定OFF・golden L1バイト一致・k非依存・no-fingerprint・専用stream・観測がシムを変えない。
> 検証ランは mock or ≤24stepスモークのみ(実LLMフルラン禁止)。

## 0. リサーチ成果(2026-08-05 完了・3本)

- **P4**: [p4-calibration-research.md](../research/p4-calibration-research.md) — ★最大の発見=**現行SFMはVISSIM製品版の短距離項のみで長距離項が丸ごと欠落**(A=2000N÷80kg=25 m/s² が短距離項と完全一致)→ P4は「A・B振り直し」でなく「**第2項を足す**」。λ=0.5 は較正済み文献値 0.06–0.12 の4〜8倍(engine_kw だけで検証可能=最安の先行実験)。Jülich は CC BY 4.0・軌跡txt直リンクで合わせ込みCSV可。±20%帯は単独では不十分=単調性 dv/dρ≤0+複数密度点を必須併記。RiMEA は 16 テスト(v4.1.1)・Test 4=2D基本図・Test 16=1D基本図(判定は10/90パーセンタイル包絡線)。v₀系の防御=Tordeux/Chraibi/Seyfried 2015(JuPedSim製品モデル)・ただし前例は「密度ρ」でなく「前方間隔s」で引く形。CUTOFF_M=2.0 が長距離項を49%高で垂直に切る不連続の作り込みを検出。
- **IF**: [if-lane-research.md](../research/if-lane-research.md) — ★**Zeigarnik効果は2025年メタ分析(59文献)で否定**(再生比0.99)→ IF-2の根拠は **Ovsiankina効果**(中断課題の再開率67%)+Masicampo & Baumeister 2011(計画を立てるだけで侵入思考が消える=再計画成功時に失敗理由行を降格させる設計要求)。IF-3は「不足の補填」でなく「**優位の完成**」(Generative Agents は事後インタビュー測定でIDオブジェクト非所持=本シムの Item+transmissions が先行)・追加要求は stifler化(Daley-Kendall/Maki-Thompson・最終ignorant≈20%等の理論値と比較可能に)・指標は OASIS の scale/depth/max_breadth に揃える。IF-4は**propagationを入れない**(Parunak の propagation factor=0 として文献的に正当)=集約と蒸発の2演算のみ・TTLは3階層(transient/daily=既存flyer 144step/persistent)・貼り紙は完全なスティグマジー実装なのでその一般化。IF-1は PROV の wasInformedBy 辺1本+**(llm_call_id, role) 対**で同step複数発火の曖昧さを構造的に解消。IF-5は「接続」より先に「**検査**」(Caiani et al. 2016 の検査法2本→pytest 2関数・行列は部門別6〜8個)。実装順は IF-1 が先(他の因果測定基盤)+_apply plan分岐の穴は同時に潰す。
- **SV**: [sv-items-research.md](../research/sv-items-research.md) — S-02はODD 2020要素①「Purpose and patterns」の充足(独自発明でない)。stylized facts 主判定=**入力に埋め込まれていない4法則**(F5バースト性/F6接触時間の裾/F4滞在時間の非指数性/F7次数の裾=dunbar OFF条件)・EPR由来の移動系は循環につき参考枠・F10/F11はN不足で検定不能と明記。S-03は社会生活基本調査がSD非公表→**CV下界 √((1-p)/p) の片側判定**+SocioPatterns主源+Giniの6個目を書かない。S-16は**凍結ルックアップ表**(LLM動的生成は呼数一致テストを壊す)・3〜5セット・プラセボ3種と相互排他・判定=符号保存+spread vs seed間レンジ。S-04は Wu et al. 2025 の3基準(異質性整合/分散併記/不足時は集団定性に限定)。用語衝突警告=TRAILSの system はサーベイの macro。

## 1. バッチ列(依存関係)

**IF-A → SV-1 → SV-2 → P4-1 → P4-2 → IF-B → IF-C → IF-D → IF-E**
(IF-A/SV/P4 は相互独立。IF-B〜E は IF-A の後。各バッチ=実装→私の検収→フルゲート→コミット)

| # | 内容 | 規模 | 主要ファイル | 根拠 |
|---|---|---|---|---|
| IF-A | 行為イベントへの **(llm_call_id, role) 対**付与(PROV の wasInformedBy 辺・既定OFFトグル)+穴2件(contingency消費・_apply の plan/recall/reflect 明示分岐+fallback計上)。※会計はIF-Eへ | 小 | scheduler.py・day_plan.py・observer/schema.py | [監査](../research/llm-world-interface-audit.md) §5-6・IFリサーチ §4 |
| SV-1 | 宣言系: S-01 報告書3節テンプレ+S-02 stylized facts 節+S-04 主張の境界 §0(事前登録ドラフトへの追記=U-10承認前なので変更自由の範囲)+S-08/S-15 の宣言文 | 小(文書+テンプレ生成) | docs/plans/stationarity-preregistration.md・scripts/report_template.py(新) | survey §3 |
| SV-2 | S-03 分散/分位列(個体間CV・上位10%シェア・Gini+現実バンド)を calibrate_report.py へ+S-16 ablate.prompt_paraphrase(既定OFF・PLACEBOS同構造・manifest宣言) | 中 | scripts/calibrate_report.py・src/society/ablate.py・deliberate.py作用点 | metrics_spec_hash 凍結14ファイルに calibrate_report.py は**含まれない**ことを確認済み |
| P4-1 | 較正ハーネス: Jülich 実測取り込み(生データは gitignore・派生CSVのみ)+ボトルネックシナリオ+RiMEA Test4/16 型指標+**λ先行実験(0.06–0.12 vs 0.5)**+**第2項(A2,B2)を含む3変数較正**(ExtendedSFM=reference内サブクラス・src無改変) | 中 | reference/physics_bench/(scenarios.py・metrics.py・calibrate.py 新・data/) | リサーチ §1/§3/§5/§6 |
| P4-2 | 較正結果の本体反映: **長距離第2項+λ+CUTOFF テーパーを conf 昇格**(既定は現行値=golden無風)+必要なら v₀(s)(前方間隔ベース)テーブル外付け(ハッシュ manifest)+受入テスト(包絡線内率+単調性 dv/dρ≤0+1step変位上限) | 中 | src/society/physics.py・conf・tests | リサーチ §2/§3/§6・選定文書 §7.4-3/4 |
| IF-B | 拒否通知の段階conf化: 無音拒否(所持金不足・閉店・空き住戸・経路なし等)に notify=silent/memory/engaged の3水準+plan_exception に失敗理由+**再計画成功時に失敗理由を降格**(Masicampo & Baumeister)。根拠は Ovsiankina 効果(**Zeigarnik は2025メタ分析で否定=引用禁止**) | 中 | scheduler.py・tools.py・day_plan.py・engaged.py | 監査 §2-C・IFリサーチ §3。no-fingerprint両立=全条件同一規則 |
| IF-C | 情報オブジェクト一般化: Item.kind=rumor 生成+伝聞追跡(truth_ledger 流の決定論抽出・LLM追加呼ゼロ)+**stifler化 conf**(DK/MT 理論値と比較可能に)+指標=OASIS の scale/depth/max_breadth | 中 | labeling/labels.py・observer/provenance.py・scheduler.py | 監査 §6 IF-3・IFリサーチ §2 |
| IF-D | 痕跡=場所イベント履歴(stigmergy): **集約と蒸発の2演算のみ(propagation なし=Parunak factor 0)**+TTL 3階層(transient/daily/persistent)+後続者の観測1行(既定OFF・アブレーション軸)。既存貼り紙の一般化 | 中 | world/(新)・perception 系・conf | 監査 §6 IF-4・IFリサーチ §1 |
| IF-E | 会計: **検査を接続より先に**(Caiani et al. 2016 の2検査=pytest 2関数・純粋観測=R1自明適合)→漏れ量を数値で見てから接続方式決定。行列は部門別6〜8個(25万で個体別は不可) | 中 | tests(検査)→ scheduler.py・work.py(接続) | 監査 §3 所見・IFリサーチ §5 |

## 2. 検収条件(共通)

- 既定OFF=golden L1バイト一致(再生成禁止)・ON同seed2ラン一致・k=free/off呼数一致・no-fingerprint テスト・フルゲート `python -m pytest tests -q -n auto` 緑。
- SV-2: calibrate_report は**読み取り専用スクリプト**を維持(シム本体ゼロタッチでの列追加)。prompt_paraphrase は PLACEBOS と同じ排他規則(propagation_off 併用禁止・llm_off で警告)+fingerprint_risk 登録。
- P4-1: ベンチは reference/ 配下=シム本体ゼロタッチ。データ出典・ライセンスを README に記録。
- P4-2: **既定パラメータ変更はしない**(現行値=golden 維持)。較正値は conf プロファイル(observe/production)での明示 ON。
- IF-B: 通知文言は全実験条件で同一規則(条件間差ゼロ=no-fingerprint)。
- IF-E: 金の保存則(全主体の残高+フロー合計が不変)を新テストで固定。

## 3. 判断待ちとの接続

- SV-1 の事前登録追記は **U-10 承認前=変更自由の範囲**(承認パッケージに含めて提示)。
- S-16 は S-quick 候補として推されていたもの=本レーンで実装し、観察ランで ON にするかは OBS/DP-U3 改訂時に判断。
- IF-B〜D の観察ラン ON 採否も DP-U3 改訂提案書に含める。
