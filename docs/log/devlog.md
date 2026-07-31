# 開発ログ(ライブ)

> このプロジェクトを「作る側」の意思決定・節目の記録。シミュレーション内部の観測層ログとは別物。
> **プロトコル**: ユーザーとの1往復ごとに1エントリ追記。エントリが10に達したら圧縮して [devlog-compressed.md](./devlog-compressed.md) へ移し、本ファイルをリセット。設計の正典は [../design.md](../design.md)。
> **圧縮履歴**: devlog-compressed.md(Block #0: プロトコル前史 / #1: ログ機構〜分野1-3 / #2: リサーチ完走〜決定アジェンダ / #3: D0-D17決定→P0実装→世界v2-v5 / #4: 生態系→docs完遂→現実ギャップ全波→第9バッチ / #5: ODPT実ダイヤ→制度深化完遂→自己モデル→現実較正→実LLM初証拠→日常プロファイル(第10〜14バッチ) / #6: 開放行動→世界解釈の観察→マルチモデル対応(第15〜24バッチ) / #7: 復元→git化→入力解像度LOD→分析スイート→制約デコード→自由度P2(第25〜34バッチ) / #8: EnvPack→PLATEAU実形状→第37バッチ6トラック→現実スケール転換(第35〜38バッチ) / #9: 同時滞在実測→全員思考転換→行間レイヤS1-S5(第38バッチW2) / #10: W2完結→視覚F→オントロジー多軸→物流・乗れる交通→並列ゲート(第38W2後半〜第43バッチ) / #11: 関係性→経済完結→観測レンズ→日常観察ABC→マクロ⇄ミクロズーム(第44〜58バッチ) / #12: 精査3スライス→関係内生化→GitHub公開→第1回分析→4系統拡張始動(第59〜66バッチ) / **#13: レーン1完了→DT/IDEA計画→二重化転換→統合実装順第70-78始動(第67〜72バッチ)**)。全文アーカイブ: devlog-block6-fulltext.md / devlog-block7to9-fulltext.md / devlog-block10-fulltext.md / devlog-block11-fulltext.md / devlog-block12-fulltext.md / devlog-block13-fulltext.md。

**ライブエントリ数: 2 / 10**(Entry 71 から=継続採番)

---
### Entry 71 — 2026-07-31 — 第73バッチ検収: 真偽台帳ミニマル=fact+信念+伝播木+検証行動+漏洩3点(1964緑)
(日付訂正: 当初 08-01 と誤記=実際は 07-31 深夜〜朝の作業)
Opus実装をFable検収。新規3(truth_ledger.py・analyze_beliefs.py・test_beliefs.py=32テスト)+9変更。
- **fact 8種**(conf データ駆動マップ・コードに固有名詞なし): event_host/venture_open/flyer_post/group_found/
  crime/stock_out/price_change(唯一の連続量真値)/disaster=「場所と時刻が確定したL1既存イベント」のみ。
  shop_state(x,y=0,0)とscenario_shock(エッジ対)は場所が点にならず不採用と正直記録。**新乱数streamゼロ**。
- **信念/伝聞**: 話題一致=場所名+topic_keyの部分文字列(L1を読むだけ=発話生成不干渉・呼数不変・journal等級の
  根拠)。変形は最小(Bartlett型の無情報方向劣化+確信度減衰のみ)。288step mockで belief_update183/transmit41・
  伝播木11本/枝70/最大ホップ3・検証率96%→68%(伝聞拡散で低下)を実測。真値はL1に出さず
  beliefs_ledger.jsonサイドカーへ分離(行間ダイジェスト等の消費経路から構造的に遮断)。
- **検証行動3種**(go/ask/net・ON時のみ_VERIFY_LINE 1行=誘導語彙なしをテスト固定・新規LLM呼なし=k不変)。
  対象特定失敗時はrecent後退=検証率水増しリスクをby_matchで分離可能に(正直設計)。
- **漏洩3点**: 静的=cognition/に台帳識別子ゼロをgrepテスト固定・実行時=CachedLLM generate/generate_many両関門で
  check_prompt(台帳空なら1命令return=既定コストゼロ)・canary=共通接頭辞1本を実ラン全プロンプト(llm_journal)
  不出現で検証。検収時にcache.py別名importでgrep空振り→diff実査で配置確認(報告と一致)。
- 検収: OFF/ON呼数88=88/506=506/1027=1027・golden緑・resume=信念状態一致(checkpoint中央管理+canary再武装)・
  registry 2件journal宣言・verify モードで自動OFF確認・フルゲートxdist **1964緑**(284s)。
- 申し送り: exit_buildingのnode張り替えと_route_to/_apply_free_actionの整合=**潜在バグ疑い**(既存・スコープ外)
  →STATUS持ち越しに登録。→第74バッチ(規範化ステージ+コホートタグ+ゼロ対照)起動。

---
### Entry 72 — 2026-07-31 — 第74バッチ検収: 規範化4段+コホート+ゼロ対照=「記録しないと失われる」観測点が完了(2002緑)
Opus実装をFable検収。新規6(observer/norms.py・initial_frame.py・analyze_norms.py・zero_traits.yaml・テスト2本=38)+9変更。
- **③規範化ステージ**(labeling.norm_stage・観測のみ=cognition/にnorm参照ゼロをgrep確認): S1初出→S2他者引用→
  S3指示詞化(日本語に冠詞が無いため「例の/あの/いつもの」等8語で代替・語の直前max_gap2)→S4合意参照
  (「さっき決めた/ルール」等12語・同一発話共起)。マーカーはconf単一源=コード内ゼロ語。coiner/definitizer/
  institutionalizerを役割分離。mock 288step実測=語63・S2到達7・S3/S4は0件(表層一致の過小検出=mockでは正常と
  正直記録)。norm_stateはcheckpoint中央管理・resume L2一致。
- **Part E1**: 初presence stepは既存L1から導出可能=シム変更ゼロ(在場中は毎stepイベントが出る構造を実査確認)。
  下方因果=規範成立step前後の初参入コホートの初日行動分布比較+置換検定。**閾値は引数必須・未指定エラー**=
  U-10事前登録の枠組みに従い既定値を埋め込まない。配線実測=3コホート・use_rate 0.067→0.203(p≈0.02)だが
  「語の可用性交絡があるためmockの数値は配線確認であって証拠ではない」をレポート末尾に明記(正直設計)。
- **④ゼロ対照**(experiment.flat_traits): 実装点=build_agentの合流点1箇所(名簿/pool両経路)・下流7経路を実査し
  presence選抜はtraits非依存を確認。**実行役の重要な訂正: 「ON/OFFで呼数不変」は原理的に不成立**(発火閾値を
  潰す=誰が発火するかが変わるのが処置そのもの)→保持すべき不変条件は「build_agentの乱数消費本数一致」=
  CRN共分散維持(counting RNGプロキシでテスト固定)。k交絡はzero_traits.yaml(4セルCRN・compute_matched)で
  切り分け。initial_frame=初日N stepの決定論集計をsummaryへ=ラン単位共変量。
- 検収: golden・L1/呼数不変(③観測のみ+④既定OFF)・registry 3件strict宣言・フルゲートxdist **2002緑**(306s)。
  日付誤記の訂正(Entry 71は07-31)。→第75バッチ(ダンバー維持コスト)起動。U-10承認依頼の材料はこれで完備。