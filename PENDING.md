# PENDING — 未実装・実装中・ユーザー判断待ち

> 本ファイルは **まだ終わっていないもの**だけを持つ。完了済みは → **[IMPLEMENTED.md](IMPLEMENTED.md)**(決定の履歴も同所の年表と git log が正典)。
> 索引と最終更新は → **[STATUS.md](STATUS.md)**。
> 最終更新: **2026-08-07**(第98小粒バッチ7レーン完結+ユーザー決定6件を記帳)。

---

## 1. 実装中レーン(承認済み・リサーチ→実装の順)

| レーン | 内容 | 状態 |
|---|---|---|
| **RW-U1 運用** | フェッチャー実装**完了**(2026-08-07 第99・`scripts/rw_fetch/` 9ファイル+80テスト・鍵は全出口スクラブ・**アメダス 7/28〜8/6 をバックフィル回収済み**)。残=①運用方式の決定(§3)②8/12 頃の規約再確認(R3)③**8/15〜30 は毎日 `python scripts/rw_fetch_daily.py --backfill` を1回**(数秒・取り逃し=永久喪失) | **運用待ち** |
| **PUB-U1** | 公開ミラー修正(2026-08-06 ユーザー決定=Fable 案で進める・提出用 public の修正のみ): docs/**・台帳3md を除外し README/ETHICS/LICENSE は残す。**ライセンス地雷2件**(商業施設/区サイト情報=転載不可・OSM 由来=ODbL)の除外を確認して同期 | **作業中**(Fable 直轄) |
| P4 残り | D(ボトルネック J/w 水準)の原因切り分け(接触項不在/τ/v0分布/定常部)・高密度の壁貫通脱出(接触項 or v_max クリップ再設計) | 未着手(フリーズ前は任意・§4 参照) |

## 2. 提案書(作成中・提示済み)

| 項目 | 状態 |
|---|---|
| **DP-U2 提案書**(心モデル) | **暫定決定=案C**(2026-08-07 ユーザー: 小型同居で多様性6種×冗長性を両立。提案書では**未検証**マークの構成)→ **8/15 診断ランに「vLLM 同居性能の実測」を必須追加し、厳しければ案Bへ**(退路は conf 1箇所)。D層 n=30 は280呼=8/15午後に同居可。残=候補7本のライセンス/VRAM一次確認(8/12まで) |
| **DP-U3 提案書**(観察ラン25万) | **決定=本線10日ラン25万(現実同等規模)**(2026-08-07 ユーザー「現実の渋谷の再現が目的なのでここは削れない」)。前提3点が必須化: ①層別クォータ=**実装済み**(小粒G 2026-08-07・R-1=(a)で決着)②解析25万対応(§1 wave2)③R_eff/144step RSS 実測(8/15-16)。週末28%は R-3(b)=正直記載を既定線。★ON では resident も比率で切られる=コホート/k* 追跡系への影響確認は 8/15-16 |
| 観察ラン ON 構成(旧提案) | [observe-run-config-proposal.md](docs/plans/observe-run-config-proposal.md) 提示済み → **DP-U3 改訂版で置換予定**。OBS-U1〜U3 の判断は改訂版で |
| DT スナップショット再提案 | [dt-snapshot-integration-proposal.md](docs/plans/dt-snapshot-integration-proposal.md) 提示済み → DT-S1 ほか判断待ち |
| S-quick(S0/S1/S2/S5/S9) | 計 ≈1.8日。承認待ち(入力来歴・observe.yaml 是正・バス表・実イベント表・ODD 文書) |

## 3. ユーザー判断待ち(残りのみ)

| # | 事項 | 状態 |
|---|---|---|
| **U-10** | 事前登録の閾値承認+10日ラン解釈方針。**承認対象が2点増えた**: 前文「主張の境界」+§3-F stylized facts(分散比の閾値・F1 の θ 数値化は §7 未決事項) | 8/15-16 診断ラン前に承認依頼(10日ラン 8/16 開始前・タイミング委任済み) |
| OBS-U1/U3 | 観察ラン ON セットの承認・認知 ON の 8/14 留保(OBS-U2=Δt は準備実装へ移行済み) | DP-U3 改訂提案書とセットで判断 |
| **policy_cache 保存判断** | 小粒A(2026-08-07)発見: LLM 決定のウォームキャッシュ(`cognition/policy_cache.py`)が checkpoint 未保存=resume で空になり**同じ骨格でも呼数と行動が変わりうる**。保存自体は容易だが「キャッシュは再構築可能」という設計思想との整合と L1 一致検証の設計が要る | 新規・本選前(推奨=8/15-16 診断で resume 前後の呼数差を実測してから) |
| **凍結ハッシュ更新判断** | 第99実測(2026-08-07): 凍結4本のうち ①`analyze_beliefs`=25万で **4.2〜6.4 TiB** の全件展開(HARD BREAK・修正は2行置換で**判定式不変**)②`analyze_norms`/`analyze_specialization`=Δt 直書き(Δt=1 で観測窓が実時間 1/10)。3本とも判定式に触れない最小手で直せるが **metrics_spec_hash が動く**。`diagnose_stationarity` は既に安全=対処不要。あわせて specialization は **25万実証ランでは走らせない**(O(発話×トークン) は指標再設計なしに消えない・本線10日ランでは走らせる)ことの確認 | 新規・**8/15 の U-10 凍結前に1回で確定**(推奨=3本まとめて直して以後不触) |
| **RW-U1 運用方式** | 本選中の日次取得(アメダス取り逃し=永久喪失)を (a)手動1日1回 (b)Windows タスクスケジューラ登録(Fable が設定可・`--report` 定期確認とセット)のどちらで回すか | 新規・8/12 まで |
| NEW-5 | F/N/P 初期値条件の本選配分 | パイロット後に提案 |
| DT-U2 | UE5 デモ動画 | 保留のまま(本選中判断) |

### 決定済み(履歴の要点のみ・詳細は git log と IMPLEMENTED 年表)
2026-08-07: **DP-U2=暫定案C**(小型同居・8/15 に vLLM 同居性能を実測し厳しければ案B)/**DP-U3=本線25万**(現実同等規模「ここは削れない」)/**3D-U0=実装**(小粒F完了)/**SV-05=③**(診断後決定・既定線=集団定性パターン限定)/**DP-U4=呼数**/**B3=換算しない**/**RW-U1=承認**(リサーチ先行・無料優先・自律実装は委任・手動は最小)。
2026-08-06: **IF-E2=案B**(org 会計主体化+RoW 概念実装)/**DP-U1=無償**(CEJC 契約せず名大会話コーパス無償統計で C 層=実装は既にこの前提)/**SV 残13項目=採用**/**PUB-U1=Fable 案で決定**/OBS-U2=Δt1分の準備指示。
2026-08-05: IF-U1 実装承認→IF-A〜E 完了・SV-U1 ◎5件完了・P4-1〜3 完了。
2026-08-02: P2選定=ゾーン別ハイブリッド(委任決定)・高精細3D=松案承認。
2026-07-31 以前: NEW-1〜4・ID-U1〜U3・DT-U1/U3/U4 等(旧台帳 git 履歴参照)。

## 4. 持ち越し小粒(未解決のみ)

- **σ_c の Δt 再測**(Δt=1 では salience が系統的に過小・8/15-16 に統合)
- **IF-E2 残**: ①**窃盗の加害者への入金**(SNA では被害者−/加害者+の再分配だが本シムは受け取り側を K5 に置いたまま=挙動変化を伴うので独立トグルが要る・将来判断)②屋台の内税/床クリップギャップ(RoW が埋める=改名して隠さない)③K5 の日次 L1 未出力(`finance.parquet` の `k5_other` 列のみ。要るなら `_emit` 1キー)④b2b 買い手特定=`(node,POI種別)` 一意率 4.5%=本番規模では大半が「域外資本の店」(RoW)扱い(正直開示済み)
- **resume 整合の残り**(小粒A 2026-08-07・日カウンタ15件+付随5族は修復済み): ①`spark_roster` が resume で二重記録(記録のみ・状態は正しい)②observer 状態の非対称(echo/norm 等は保存済み・lens/silence/structure/deviation 未保存=動力学非影響だが mid-day resume の当該 L2 列が食い違いうる)③worldview の C2 応答走査が「直前の日境界〜checkpoint」区間を取りこぼす(イベント本体の保存が要る・checkpoint.py にコメント明記済み)※policy_cache は §3 判断待ち
- **IF-C 残課題**: ①噂誕生は step 末走査=1 step 遅れ(→§1 wave2)②Item.transmissions 上限なし(25万ではホット噂 O(N)=正典を L1 に置く再設計は別バッチ)※混線切り分け(オーバーレイ新設)と pool dehydrate は 2026-08-07 解消
- **P4 残課題**: ①D=J/w 水準不足の未解明(残候補=接触項不在/τ/v0分布/定常部)②高密度 ρ≥2 の壁貫通脱出(接触項 or v_max クリップ再設計・FD 高密度点は汚染込みでしか測れない)③6変数同時最適化未実施 ④ρ_meas 1.5 頭打ち=判定B合格は弱い証拠
- **物理見積の残り**(小粒E 2026-08-07): ①`max_sub_steps: 12000` は Δt=10分の直書きで Δt に追随しない(Δt=20分では不足=テストで明示固定)②理論モードの既定2つ(`traversals-per-agent-day 2.0`/`zone-share 0.5`)に根拠なし=OD 表・実測通行量で埋める ③物理 ON の較正ラン(mock 可)を runs/ に1本作れば実測外挿モードが本番投入可(現状 runs/ 163本に `zone_gate` 含むランは 0)④混雑で dwell が伸びる効果は未計上=見積は下限側
- **3D 残り**: tracks.json の O(n_steps×n_agents) は出力そのもの(真の解=既存 `--tracks-binary --no-tracks-json`)・10日ラン規模の実 RSS 絶対値は未測(構造上は O(row group+1 step) 化済み)
- **層別クォータの照合**(小粒G): 提案書 §1.2 の割当は計算値=8/12 の縦煙で `present_for_day` を1回実走して照合(±1人ずれは最大剰余法が正・提案書 §6-5 訂正済み)
- **解析25万の残り**(第99・W2-2/W2-6 実測済み): ①`analyze_accounting` の events/flows は O(金額イベント数) 残存(`flows_for` の `id(payload)` 呼び出し規約の変更が要る=検査式に触れる別バッチ)②`live_viewer` の 1 part 丸ごと Python 化は要見積 ③研究解析十数本の `l1_stream` 移行は型が揃い機械的に可能(必要時)④finalize streaming のサイドカー横展開(indoor_tracks/org_ledger/finance 等=同型)⑤`row_group_rows` 既定 2^20 は本番前に実 L1 の行バイトで再調整(conf 1行)。※src logger の finalize 42.7GB 懸念は W2-6 で解消済み=**観察ランは `observer.finalize.streaming: true` 推奨**
- **Δt の残り**(第99・31本移行済み): ①`viz/make_viewer.py` の STEP_MINUTES=10 ×15箇所(最後の1本・export_3d と同型の importlib 移行)②`run_manifest` に dt_min が無い(manifest.py 1行=src)③σ_c の dt 来歴照合(設計文書 B3・src)④L1 からの Δt 推定=第3の源(pyarrow 依存で見送り)⑤旧ラン 173/178 本が dt_min 無し=assumed 経路で stderr 1行(仕様=黙って仮定しない)
- **W2-4 観測強化の src 候補3点**(1語〜1列の追加で突合が厳密化): `agents.json` に work_node 列・`plan_block_start` payload に node 1語・`plan_block_*` にブロック添字(台帳再生の多義性が構造的に消える)
- **噂の語り選択順**(W2-5): 同 step 伝播の実効量は `max_per_talk=1`+「古い順に語る」が律速=ポートフォリオ選択順は別課題
- **D16 屋内 ON**・**D17 実験**・**4系統レーン2**(B-L1 以降)
- **竹-4 残**: ④span_m グラフ長 vs 物理直線の実効速度差 ⑥サブステップ軌跡の記録・`planning.py` 契約化は残置第一候補(※③ `_phys_body` 搬送と⑦事前見積は 2026-08-07 解消・ゾーン所有は「その旅に固有の状態」として意図的非搬送=根拠コード内明記)

## 5. 設計制約と受領文書(背景・不変)

### 5.1 設計制約(R1 ドクトリン)
恒常制約: ①新機能は既定 OFF ②既定 OFF で golden L1 バイト一致 ③k 非依存 ④no-fingerprint ⑤用途別乱数 stream ⑥観測がシムを変えない。
観察ラン(本選10日)は再現性を厳密に求めず repro_tier=journal/none も投入可・検証ラン(verify)は strict のみ(第72で構造化済み)。

### 5.2 受領文書(原文は docs/plans/source/ に保存済み)
二重化指示書3本・認知/物理/DT定義3本・設計議論まとめ(2026-08-02)・サーベイ PDF(原本リポ外・読解=[llm-social-sim-survey.md](docs/research/llm-social-sim-survey.md))。
統合計画の正典: [dual-mode-observe-verify-plan.md](docs/plans/dual-mode-observe-verify-plan.md)・[cognition-physics-plan.md](docs/plans/cognition-physics-plan.md)・[dayplan-engaged-plan.md](docs/plans/dayplan-engaged-plan.md)・[highfidelity-3d-physics-plan.md](docs/plans/highfidelity-3d-physics-plan.md)・[if-sv-p4-plan.md](docs/plans/if-sv-p4-plan.md)。

### 5.3 日程
**本選 8/15–8/30**(提出 8/30)・**10日ラン 8/16–8/26**・**8/12-14 フリーズ**(新機能追加禁止=検証と微調整のみ)・**8/15-16 診断ラン**(σ 再実測 → θ 再較正 → U-10 確定判定 → 人数最終確定・**vLLM 同居性能実測=DP-U2 案C判定**・**R_eff/144step RSS 実測=DP-U3 25万**・SV-05 seed 効果量・policy_cache resume 呼数差)。GPU=A5000 級 ×7枚(単一ノード)。

### 5.4 本選後(レーン3)
場所二層知覚(IDEA⑥)・誤情報構造化フル版(ID-U2)・SUMO 反実仮想(P5)・USD/3D Tiles(DT-U4)・UE5(DT-U2)・org 会計主体化の拡張(倒産・信用線)・詳細順位は [dt-integration-plan.md](docs/plans/dt-integration-plan.md) §3。
