# PENDING — 未実装・実装中・ユーザー判断待ち

> 本ファイルは **まだ終わっていないもの**だけを持つ。完了済みは → **[IMPLEMENTED.md](IMPLEMENTED.md)**(決定の履歴も同所の年表と git log が正典)。
> 索引と最終更新は → **[STATUS.md](STATUS.md)**。
> 最終更新: **2026-08-14**(第112後の掃除パス: L2日給0の穴=WAGE実装で消化・同型痩せ5件+全数検査約40件=甲/乙/丙で消化・wv_expect搬送=乙B8で消化。新規判断待ち=GTロガーG1-G7・b2b構造的供給)。

---

## 1. 運用中・未着手レーン

| レーン | 内容 | 状態 |
|---|---|---|
| **RW-U1 運用** | タスクスケジューラ稼働中(`shibuya-rw-fetch-daily` 毎日12:00)。残=①規約再確認(R3)②本選中は `--report` の欠け監視を時々目視③本選後の解除 `Unregister-ScheduledTask` | 稼働中 |
| P4 残り | D(J/w 水準)の原因切り分け・高密度の壁貫通脱出(接触項 or v_max クリップ再設計) | 未着手(任意) |

## 2. 計画済み(実装の残りがあるもの)

| 項目 | 残り |
|---|---|
| **犯罪×LLM検証** | [crime-llm-verification-plan.md](docs/plans/crime-llm-verification-plan.md)。**V0=mockハーネス実装完了(第109・82テスト)**。残=**V1選択率/V2被害者反応の実LLM実測(8/15-16 GPU同居・コマンドはスクリプトdocstring)**。判定分類器は日英語彙のみ=皮肉/婉曲は拾えない(md明記) |
| **所有権レイヤー** | [ownership-layer-plan.md](docs/plans/ownership-layer-plan.md)。**O1登記簿+O3相続=実装完了(第109・47テスト・ユーザー3決定=域内不動産org/相続承認/本線前)**。残=**O2家財L-agg・O4権利行(lease/permit)・O5流通内生=本選後**。既知の限界: 家賃/敷金の受け手は今もRoW(O4で家主へ)・売買代金は動かない(O5)・inheritance は analyze_accounting 未分類(監視装置に正直に列挙される)・プール退場中の世帯員は相続人になれない(heirs_absent で可視化) |
| **本選信頼性** | [finals-reliability-plan.md](docs/plans/finals-reliability-plan.md)。**小物2本=実装済み(第110)**: watchdogディスク残量ガード+`backup_run.py`(restore drill前段=実測成立)。残=**8/15の環境確認5点**→**リハーサル7本**+閾値/世代数の本選値化(既定20/5GBは小規模想定)。未実装(意図的)=ローカルpull側スクリプト・checkpoint剪定(人間判断)・クラウド系統。★運用注意: `--resume` は落ちたラン専用/走行中run-dirへのrobocopy直がけ禁止(backup_run.py経由=共有フラグ読み) |
| **在場内生化PRES** | **A1+A2+B+C=実装完了(第111)**。残=**A2 emergent のON判断のみ**(8/15 RSS/R_eff実測後・finals confの1行) |
| **メタバース射影** | [metaverse-projection-plan.md](docs/plans/metaverse-projection-plan.md)+[リサーチ](docs/research/metaverse-observable-data.md)(第112・計画のみ)。残=**§4 GTロガーG1-G7の承認**(下記§3)→承認分のみ8/15までに実装。射影フィルタF0-F4・復元実験3案は**本選後** |
| **アクターモデル移行** | 工学系の残(本選後): SoA配線(乱数キー判断が前提)・店主行為化・GTFS実発車時刻・PoA観測。OPEN: PoA/§4.5 |
| **身体と事件レイヤー** | chance.py の**コード削除**=本選後(運用退役は finals conf で済み)。設計上の残は §4「身体と事件の残」 |
| DP-U2/DP-U3/S-quick/DTスナップショット | 8/15-16 診断ランでの実測待ち(vLLM同居・R_eff/RSS・σ再実測)・S-quick は承認待ちのまま |

## 3. ユーザー判断待ち

| # | 事項 | 状態 |
|---|---|---|
| **U-10** | 事前登録の閾値承認+10日ラン解釈方針([stationarity-preregistration.md](docs/plans/stationarity-preregistration.md)) | **本番直前に決定**(2026-08-12 ユーザー指定=10日ラン開始 8/16 の直前に承認依頼) |
| **OBS-U1/U3** | 観察ラン ON セットの承認(候補= `conf/finals_observe.yaml`・chance退役/assets/bind_workplace/responder・guard語彙/serve_by_cat service 行を同梱)・認知 ON の 8/14 留保。★認知 ON 判断が出たら回転棚卸し(D1の型)を認知スタックにも再実行 | 8/14 |
| **Δt梯子の承認** | [dt-reduction-plan.md](docs/plans/dt-reduction-plan.md) 提示済み(2026-08-12): 本線25万×Δt=10+**並行1〜2万体×Δt=1**(驚き発火の解放=科学的動機・30秒は見送り推奨)。承認でDT-1〜3(呼数不変の機械固定・Δt=1プロファイル・運用)を実装。+並行ラン規模(1万or2万)と開始時期 | 承認待ち |
| **存在内生化POP** | [population-endogenization-plan.md](docs/plans/population-endogenization-plan.md) 提示済み(2026-08-12): 転入=案A(L4定着昇格)推奨/案B・実装=**本選後推奨**(10日ランでは0.03%)・出生=POP-3で含める推奨 | 承認待ち(3点) |
| **★GTロガーG1-G7** | [metaverse-projection-plan.md](docs/plans/metaverse-projection-plan.md)§4: G1入力3ファイルsha256→manifest(極小・推奨必須)/G2 checkpoint/dormant全世代保持の運用固定(実装ゼロ・推奨必須)/G3日次名簿(**A13としてroster.parquet実装済み=承認はfinals ONの追認のみ**)/G4 memory.parquet(記憶本文・+1.8GB)/G5 relations.parquet(closeness軌跡・+0.4GB)/G6 channelsにsat4列(+0.6GB)/G7小物束(計画のmood/carry/with・self/ties・感情句・needsプロファイル・期待上位k・C3集計)。**8/15までに承認分のみ実装**(本選ランで記録されないものは二度と取れない) | **新規(第112)・8/15期限** |
| **b2bの構造的供給不足** | 乙D2調査: 卸に勤務者は居る(中央値7名)が「最寄り1社指名の集中+all-or-nothing仕入れ」で100%在場でも生産42,408 vs 需要44,604/日・cap25%で生産1/4。初期在庫3日分(実装済み)は立ち上がりを渡すだけ。恒常解=(a)production_units引き上げ (b)複数卸への分散調達 (c)部分納品 の設計3択 | 新規(第112)・設計判断 |
| 賃金の残り2点 | ①最低賃金の床に27,740人(12.4%)が完全同一額で張り付く(現実にも最賃集積はあるが単一値スパイク)②家賃は実引落日(27日/末日)が10日窓に入らないため引落ゼロ=**savings_rate 0.555の帯超過は窓アーティファクトと記録済み**(機構は触らない判断=Fable)。異論あれば再検討 | 新規(第112)・小 |
| visit_purpose構成比のPT較正・曜日/雨弾性の水準較正 | PRES-A1の設計値を実測(PT調査・jinryu曲線)へ較正し直す別レバー(1レバーずつの規律) | 小・任意 |
| **policy_cache 保存判断** | checkpoint 未保存=resume で呼数と行動が変わりうる。推奨=8/15-16 診断で resume 前後の呼数差を実測してから | 本選前 |
| **回転搭載の判断待ち・残1件** | `implicit_self`+`behav_ema`(EMA の窓が回転を跨ぐべきかの意味論)。※`wv_expect` は第112乙B8で搬送済み=消化 | 第109・小 |
| beliefs の `--bin-steps` 既定24 | 唯一残った Δt 直書き(CLI 上書きで回避可)。直すなら 8/15 ハッシュ凍結前 | 小・任意 |
| NEW-5 | F/N/P 初期値条件の本選配分 | パイロット後に提案 |
| DT-U2 | UE5 デモ動画 | 保留(本選中判断) |

### 決定済み(履歴の要点のみ・詳細は git log と IMPLEMENTED 年表)
2026-08-13/14: **痩せ=「くまなく検査して漏れがないよう修正」承認**(→第112甲/乙/丙で約40件根治)/**賃金多様性=実装承認**(月給/日給・振込タイミング・ボーナス・職種適合額→WAGE実装)/**メタバース観測データ検証=リサーチ+計画まで**(実装しない)。
2026-08-12: **org_id+bind_workplace=両方実装してON**(第109で実装完了)/**所有権3決定**(域内不動産org追加・相続承認・本線前実装)/**犯罪×LLM=Fable案採用**(検閲なし不使用・V0実装/V1V2は8/15)/**フリーズ=仮決定**(直前まで修正可能の認識)/**退避先=ローカルPC・外付けHDD**(クラウド/GPU機詳細は8/15)。
2026-08-11: 身体と事件4決定(死=現実量で実装・chance廃止・全部実装・保険RoW)。
2026-08-07: DP-U2=暫定案C/DP-U3=本線25万/SV-05=③/DP-U4=呼数/B3=換算しない/RW-U1=承認/凍結3本修正=承認(**8/15凍結の正ハッシュ `79a2e549486fe6ab5eea350334cbe37b4c712c12dbf75e41afea617939010d0f`**)/RW運用=スケジューラ。
2026-08-06 以前: IF-E2=案B/DP-U1=無償/SV残13=採用/PUB-U1/P2=ゾーン別ハイブリッド/NEW-1〜4・ID-U1〜U3 等(git 履歴参照)。

## 4. 持ち越し小粒(未解決のみ)

- **第112の正直な限界5点**: ①truth_ledger.py:497,518 の幽霊解決は**凍結14本のため不触**(`_present()`が物理述語のため脱水個体を通す=`_fact_beliefs`が幽霊に書かれる・次のハッシュ変更に同梱)②途中入場者への友人グラフ適用は O(N²)で不可(dehydrate切り捨て問題のみ修復)③unbond は相手不在時保留(入場時整合で清算)④車両に rot_out 無し(退場者の車は「所有継続」と読む=O2耐久財寿命で再検討)⑤pool ONスモークの家計残差 rel 1.359e-06 は既存の丸め事象(旧挙動でも同値・|r|>0.5円の窓ゼロ)
- **σ_c の Δt 再測**(8/15-16 に統合)
- **finals プロファイル限定の未宣言トグル8件**(第109発見・既存の穴): `economy.bank.enabled`/`consumption`/`payment`/`vc`・`institution_routes.assembly.from_roster`/`.realism.enabled`・`memory.actr.enabled`・`prompts.dialog_history`=基底 conf に無いキーは registry 網羅テストが拾わない。機械的な宣言追加で塞がる
- **attach_record の本番コスト未実測**(第109): 台帳読み+25万回の dict 参照=8/15 の RSS/R_eff 実測に同梱
- **IF-E2 残**: ①窃盗の加害者への入金(挙動変化=独立トグル要・将来判断)②屋台の内税/床クリップギャップ(RoW が埋める)③b2b 買い手特定=一意率 4.5%(正直開示済み)
- **resume 整合の宣言済み限界**: `undefined_action_total` 等プロセス内カウンタ族=resume 後 0 から(checkpoint.py 明記)・`device_load` の時間内訳は resume 直後の1時間だけ過少(devices.py 明記・第109で1行差として実測確認)・凍結 `silence.py` docstring 6行は次のハッシュ変更に同梱
- **IF-C 残**: ①Item.transmissions 上限なし(25万ではホット噂 O(N)=別バッチ)②語り選択順(`max_per_talk=1`+古い順が律速)
- **P4 残**: J/w 未解明・壁貫通脱出・6変数同時最適化・ρ_meas 1.5 頭打ち
- **物理見積の残り**: 理論モード既定2つに根拠なし(実測外挿モードで迂回可)・混雑 dwell 未計上=下限側
- **3D 残り**: tracks.json は `--tracks-binary --no-tracks-json` が真の解・10日ラン実 RSS 未測
- **解析25万の残り**: ①`analyze_accounting` の events/flows は O(金額イベント数)(検査式に触れる別バッチ)②`row_group_rows` 既定 2^20 は本番前に実 L1 で再調整 ③W4-E 申告2点(ON=part 間スキーマ permissive 統一・indoor_tracks ON は +19GB)
- **Δt の残り**: L1 からの Δt 推定(pyarrow 依存で見送り)・旧ラン dt_min 無し=assumed 経路(仕様)・src 観測定数(凍結・8/15 以降)
- **W4-F の設計上の残**: `street` ブロックの帰属不能は仕様・`work_node` はスナップショット(受理集合の和で緩和済み)
- **身体と事件の残(第107・設計上の残のみ)**: 【H1】通報遅延分布は Δt=10 で同一 tick(payload 観測のみ)・死亡は発症時決定(治療→転帰の条件付けは別バッチ)・city_ops OFF では S3/S4 の物理表現なし【H2】医療機関 org 特定率=本番台帳で再測要・高額療養費/年齢別負担/病床数は未実装・H5 負傷者は搬送しない・S2 受診は移動を作らない【H3】落下ハザード=25万 ON 時は stride 化検討・resolve 1step 遅れ・落し物は知覚に出ない【H4】ペア確率=和近似・警察官を現場へ動かさない・detain_steps 既定0【H5】traffic 係数の本番規模再較正・延焼なし・群集は physics.zones ON のみ
- **`_dinner_logged` は予防的搭載で実測未達**(第109・帯の途中 resume の縮小再現は未取得)
- **D16 屋内 ON**・**D17 実験**・**4系統レーン2**(B-L1 以降)
- **竹-4 残**: ④span_m 実効速度差 ⑥サブステップ軌跡記録・`planning.py` 契約化

## 5. 設計制約と受領文書(背景・不変)

### 5.1 設計制約(R1 ドクトリン)
恒常制約: ①新機能は既定 OFF ②既定 OFF で golden L1 バイト一致 ③k 非依存 ④no-fingerprint ⑤用途別乱数 stream ⑥観測がシムを変えない。
観察ラン(本選10日)は再現性を厳密に求めず repro_tier=journal/none も投入可・検証ラン(verify)は strict のみ(第72で構造化済み)。

### 5.2 受領文書(原文は docs/plans/source/ に保存済み)
二重化指示書3本・認知/物理/DT定義3本・設計議論まとめ(2026-08-02)・サーベイ PDF(原本リポ外・読解=[llm-social-sim-survey.md](docs/research/llm-social-sim-survey.md))。
統合計画の正典: [dual-mode-observe-verify-plan.md](docs/plans/dual-mode-observe-verify-plan.md)・[cognition-physics-plan.md](docs/plans/cognition-physics-plan.md)・[dayplan-engaged-plan.md](docs/plans/dayplan-engaged-plan.md)・[highfidelity-3d-physics-plan.md](docs/plans/highfidelity-3d-physics-plan.md)・[if-sv-p4-plan.md](docs/plans/if-sv-p4-plan.md)。

### 5.3 日程
**本選 8/15–8/30**(提出 8/30)・**10日ラン 8/16–8/26**・**8/12-14 フリーズ=仮決定**(2026-08-12 ユーザー明言: 直前まで実装・修正可能。R1 規律は従来どおり厳守)・**8/15-16 診断ラン**(σ 再実測 → θ 再較正 → U-10 確定判定 → 人数最終確定・vLLM 同居実測=DP-U2 案C判定+**犯罪V1/V2 実測**・R_eff/144step RSS 実測=DP-U3・SV-05 seed 効果量・policy_cache resume 呼数差・**信頼性リハーサル7本**)。GPU=A5000 級 ×7枚(単一ノード)。

### 5.4 本選後(レーン3)
所有権 O2/O4/O5・chance.py コード削除・場所二層知覚(IDEA⑥)・誤情報構造化フル版(ID-U2)・SUMO 反実仮想(P5)・USD/3D Tiles(DT-U4)・UE5(DT-U2)・org 会計主体化の拡張(倒産・信用線)・SoA 配線・詳細順位は [dt-integration-plan.md](docs/plans/dt-integration-plan.md) §3。
