# devlog Block #12 全文アーカイブ(Entries 50–60・2026-07-25 〜 07-29)

> devlog.md のライブエントリ10本到達に伴う圧縮時の全文退避。要約は devlog-compressed.md の Block #12。
> 注: Entry 52 はライブ原本に存在しない欠番(採番飛び)。本ブロックの実エントリは 50,51,53〜60 の 10 本。

### Entry 50 — 2026-07-25 — 未実装要素候補一覧の精査(実装前レビュー)
ユーザー提示 docs/missing-elements-candidates.md(A内部可動性/B加齢/C対人の陰/D蓄積/E場所/F個人差)を
Explore 12項目のコード実査で裏取り。**主な訂正**: ①転職・異動は実装済み(_phase_career・lay_off/
rehire/switch_org・既定OFF=確率駆動。真のギャップは「選択由来化」と転居・世帯再編・既存org生死)
②資産ストックは口座E5で実装済み=残高永続・破産・免責・利子(欠けは残高Gini/時系列の観測列のみ)
③記憶は忘却まで実装済み(ACT-R冪乗減衰+日次間引き。未実装は「美化」のみ)④偶然の出会い→関係形成は
C2会話の基幹経路として既存(物理近接hearers_of→meet_prob→record_contact。第58バッチが屋内へ拡張。
属性類似は初期友人グラフのみ)⑤リスク選好はTRAITS={nfc,risk_tolerance,internal_locus}で既存構成概念
=R²(k)の核(時間割引は不在だが**persona_pool再生成禁止により新trait軸は実質封印**)。
**方針整合の指摘**: 模倣・嘘は「促進機構」でなく「観測レンズ」先行が natural-coinage/日常観察方針と
整合。B(加齢・生死)は実装せず限界明記とする文書の判断を支持。**優先提案**=(a)観測スライス
(資産分布・弱い紐帯・模倣連鎖検出=シム不変)(b)内部可動性(転居・bond→同棲・career選択由来化)
(c)負の評判伝播(語彙contagionの負方向再利用=コスト低)。既存機構のON構成(career等)で得られる
可動性が大きい点も明記。実装はユーザー承認待ち。候補一覧ドキュメントをリポジトリへ収録。

---
### Entry 51 — 2026-07-25 — 第59-61バッチ: 精査承認3スライス完走(観測/内部可動性/負の評判・1687緑)
ユーザー承認「提案通りに実装を進めていい」+候補一覧.mdの作業ツリー撤去(b57f468・履歴とEntry 50に保存)。
体制: Fable計画/検収/コミット・Opus実行(3コミット 55d0e0e→9cf9fe6→0baabba)。
- **第59 観測スライス(a)**: assets.py=L2全体5列(gini/top10/median/mean/前日比順位τ)+💰資産タブ(L3事後
  再構成=resume安全)・analyze_weak_ties.py=既存決定論LPA再利用でbridge辺/brokerage/語彙採用のbridge
  経由率(グラノヴェター検証観測)・analyze_imitation.py=接触→初行動の時差検出+非曝露ベースライン比
  (促進せず観測のみ=natural-coinage方針・因果断定しない注記)。mock実測: Gini 0.417→0.450・模倣RR7.34・
  bridge経由採用8.7%。**検収補修**: τ前日状態のcheckpoint非搭載(status.py前例踏襲)がassets ONの
  resume==straightを崩す欠陥を検収で発見→checkpoint中央管理へ搭載・260step境界跨ぎresumeテストで固定。
- **第60 内部可動性(b)**: mobility.py=転居(職場変更/家賃滞納rent_due起点・世帯全員一括・evicted対象外)・
  同棲(bond14日+closeness→move_in世帯併合/unbond→move_out)・career選択由来化(job_searchツールを
  LLM行動空間へ=既存tool選択枠内で呼数不変・決定論マッチング→既存switch_org再利用)。stream "housing"・
  イベント4種。mock576step: relocate10件=全件世帯単位。**支援修正2件**=既存resumeギャップの顕在化対応
  (_career_day保存=転職二重発火防止・_ensure_orgsのresume時再attach回避=agents pickleの配属が正典)。
- **第61 負の評判伝播(c)**: gossip.py=内生の悪評タグ(種=既存負イベントのみ・データ駆動マップ・LLM悪評文
  生成なし)・伝播=相異なる知人数の閾値2(labelsの延べ回数と意味論が異なるため独立実装・理由記録)・
  日次忘却=永続烙印にしない・制裁=相手選択後退+joint誘い低下+status負項(max_penalty安全弁・会話数/
  呼数不変)。mock288step: seed7/spread257/fade43・reach分布に準飽和と局所消滅の二峰性が自然発生。
  **検収補修**: gossipのresumeテストが既存relationsギャップ(_rel_day非保存=mid-day resumeで減衰/風化
  二重発火)を顕在化→checkpoint中央管理へ搭載・全層一致+round-trip直接検証で固定。
- 検収の型が結実した往復: 3バッチ連続で「新機能のresumeテストが既存の未検証ギャップを顕在化→中央管理へ
  補修」(assets τ・career/orgs・relations)。resume==straight保証の網羅が実質的に前進。
  ゲート1626→1656→1667→**1687**(全green・全既定OFF=ゴールデン維持)。

---
### Entry 53 — 2026-07-27 — 第62-64バッチ: 関係性の内生化フェーズ1-3実装(承認済み計画の実行・1725緑)
ユーザー承認「1〜4まで君の進め方で実装していい」+実装中も文献参照の指示。逐次実行(joint.py/conf共有のため)。
- **第62(d6731e5)フェーズ1 承諾内生化**: relations_endo.py=構造化決定論抽出(予定帳簿の当日衝突veto/
  前日day_scheduleのwith志向/前日発話の明示キュー=hedge_markersで願望文誤マッチを実装中に検出し棄却・
  断り研究の出典つき)・合成p=clamp(w·較正+(1−w)·内生)−gossip・**always-draw conditionally-use**=
  joint streamのdecision単位消費ON/OFF不変=CRN共分散維持。L2 4列(承諾率/内生化率/較正乖離/履行率)・
  calibrate REALITYへ参加率+承諾プロキシ帯(断り頻度の直接統計は不在と確認し捏造せず=日経2020/SHIBUYA109)。
  mock3日: 承諾率0.601・calib_gap−0.008・fallback97.2%(材料はday2から効く構造的性質)・履行率0.337=
  Generative Agentsの不履行型と同型。検収補修=joint日次状態の既存checkpoint未保存ギャップを中央管理へ。
- **第63(385c4ca)フェーズ2 実験プロトコル**: 6セル(endo×k)CRN 30ラン14日100体マニフェスト・
  analyze_endo_treatment.py=sign-flip permutation(n≤12全列挙/Phipson&Smyth 2010)+ブロック副検定
  (Künsch 1989)+H1/H2/H3+乖離ゲートの機械判定phase3_go・make_endo_report.py(自己完結HTML)。
  配線検証mock12ラン=約22分・全ペア差p=1.0=「差なし」を正しく検出・**CRN片側で呼数6507=6507完全一致**
  =always-draw設計の実地確認。シム本体変更ゼロ。検収でD17行の改行欠落を補修。
- **第64(6ad4b12)フェーズ3 誘い先内生化**: _companions候補の並べ替え拡張のみ(前日計画with→発話明示
  キュー=accept側_has_positive_cueの役割交換で語彙単一の源→closeness降順=較正事前分布維持→弱い紐帯
  探索枠1=tier1知人を安定ハッシュ・乱数ゼロ・Granovetter 1973+Onnela 2007 PNASを根拠に保守既定・
  誘い先が知人の直接統計は不在と正直註記)。実装のみ=実験投入はphase3_goゲート(実装と実験実施の分離)。
  mock: source内訳closeness146/weak_tie9=5.8%・内生経路0.0=mockでは材料なし=設計どおり。
- ゲート1711→1725(全green・全既定OFF)。

---
### Entry 54 — 2026-07-27 — 第65バッチ=フェーズ4完結+Opus 5訂正+GPU申請/GitHub公開文書(1739緑)
ユーザー指示3点: 実装再開・**Opus 5の再確認**・GPU申請フォーム回答+GitHub公開の.md作成。
- **Opus 5訂正(重要な教訓)**: Fableが前回「Opus 5は非実在」と誤回答(旧環境情報が原因)→ユーザーの
  再確認要請でclaude-apiスキルにより**実在を確認**(claude-opus-5=Opus 4.8後継)。実行役サブを
  model:"opus"=Opus 5に設定し直しメモリ訂正。**モデル情報は記憶で断言せず必ずスキルで確認する**。
- **第65(e1938c6)フェーズ4 関係の質**: note_contactにmagnitude(既定1.0=×1.0はIEEE754厳密でOFF
  バイト一致)・会話由来の決定論抽出(発話長+往復数+明示キュー・hedge共起は中立1.0=実測18.7%)・
  [0.5,2.0]clamp・**片方向hook厳守**=tier閾値凍結テストでON/OFF L1完全一致+呼数一致を固定・C2対象外の
  理由明記。文献: Altman&Taylor 1973/Reis&Shaver 1988/Laurenceau 1998 JPSP=「深さが親密さを予測」→
  文字数を最大加点にしない正直設計。mock3日: n1601・mean1.255・clamp到達0%。**関係内生化1〜4完結**=
  エージェントの主体性が承諾・誘い先・関係の質を動かす経路が全て開通(実験はD17=本選実LLMで)。
- **GPU申請+GitHub公開文書(5ed4763)**: docs/plans/finals-gpu-application.md=設問1(実行計画6行・
  総推論規模最大2.4e7呼)・設問2(Qwen3-4B主力/vLLM 7GPU艦隊/約200時間/168GBフル=実測req/sから逆算・
  8B主力だと25万×10日で時間枠超過の発見)・設問3(**公開は主催の必須要件**と確認・全135コミット機械実査=
  シークレット0件/gitignoreデータ履歴混入0件=履歴書換不要・公開前の未了3件=GPL参照コード削除/
  LICENSE選定Apache-2.0+データ別建て/主催メモ節の扱い)。公開は07-13非公開方針の変更=ユーザー最終判断待ち。
- ゲート1725→**1739**(全green・全既定OFF=ゴールデン維持)。

---
### Entry 55 — 2026-07-27 — 公式サイト実査(申請締切8/9判明)+GitHub公開の処理計画提示
ユーザー指示2点: ①公式サイト https://hackathon.automata-lab.jp/ に正式内容があるはず→確認
②GitHub公開処理は「GitHub上で処理できるものはGitHub上で・フォルダー修正は最小限」+実行前に計画確認。
- **公式サイト実査(WebFetch 2回・原文引用で確認)**: **GPU利用申請の締切=8/9(日)・利用チーム発表=8/14(金)**・
  本選スタート8/15(土)・参加登録締切8/23(日)23:59・**提出締切8/30(日)23:59**。フォーム例の「8/8–8/23」は
  テンプレ例と判明(実期間は8/15–8/30の16日)。GPU=ワークステーション7台・**1台の内訳RTX5000×7=合計168GB**
  (=単一ノード7GPU説を公式値で裏付け・24GB/GPU逆算整合・168GBフル=1台占有の申告は不変)。提出物=
  プレゼン+README必須・RESULTS.md推奨・GitHubリポジトリ。公開時期/ライセンス規定は「応募時にご案内」。
  → finals-gpu-application.md へ §0.1 新設+§2.1/§2.4/§4-1 を修正(申告200h/168GBフルは全て不変)。
- **GitHub公開の処理計画(実行はユーザー確認待ち)**: 両問題ファイル(reference/2d-fire-sim/=GPL・
  docs/AUTOMATA第2回ハッカソン案.md=主催メモ)が**初回コミット2727e91から全履歴に在籍**することを再確認。
  ユーザー制約(フォルダー修正最小)に合わせ、推奨=**scratchpadでmirror clone→git filter-repoで2パスを
  全履歴から除去→新設の公開リポへpush**(ローカル作業フォルダー・既存privateリポは完全無傷・フィルタ済み
  135コミット履歴は公開側に保持=審査項目「実装進捗が見えるか」を守る)。フォルダー修正が避けられないのは
  **追加のみ**=LICENSE(Apache-2.0推奨)+README ライセンス節(Code/Data 2段=ODbL/政府標準利用規約2.0/ODPT)。
  代替案=既存リポ直接公開(rm --cached方式・履歴に2件残置)/filter-repo直接書換(最も侵襲的)も併記し
  AskUserQuestionで方式・LICENSE・作者メール書換・実行タイミングを確認に出した。

---
### Entry 56 — 2026-07-28 — GitHub公開実施: フィルタ済みミラー方式で公開リポ稼働
ユーザー4点確認(AskUserQuestion)=ミラー方式・Apache-2.0・作者メール公開側のみnoreply書換・今すぐ公開まで実行。
- **フォルダー修正は追加4ファイルのみ**(8092625): LICENSE(Apache-2.0全文)+NOTICE+READMEライセンス節
  (Code/Data二段=OSM ODbL継承・人流=政府標準利用規約2.0・ODPT=_meta出典付与済み・フロアガイド=カテゴリ
  事実のみ・組織台帳=合成・three.js MIT)+ops/publish_public_mirror.ps1。削除ゼロ=ユーザー制約
  「GitHub上で処理できるものはGitHub上で」を充足。
- **ミラー生成と検証**: 一時cloneにgit filter-repo(--invert-paths)でreference/2d-fire-sim/+docs/AUTOMATA*
  を全履歴除去+mailmapでnoreply書換(個人メールはスクリプト不記載=実行時にgitから導出)。検証実測=
  ミラー140=private140コミット・除去パス履歴残存0件・メールはnoreply単一・シークレット走査は擬陽性1件のみ
  (監査文書がスキャンパターン文字列を引用する行)・icloudアドレスのファイル内容混入0件。
- **公開**: https://github.com/spacedream6090-svg/shibuya-simulation-public =作成(private)→push→
  リモートHEAD一致確認→public切替→Secret scanning+Push protection有効→branch protection(可視性変更直後の
  一時ロック403→20秒後リトライで成功)。GitHubがApache-2.0を自動検出。filter-repoは決定論なので以後の同期は
  同スクリプト再実行=fast-forward 1コマンド。
- 付随: private originへ120+コミットをpush(バックアップ同期)・メモリgithub-repo.mdを2本体制に更新・
  finals-gpu-application.md §3.7実施記録を追記。残タスク=ODPT規約原文の目視再確認(SPAで自動取得不能)・
  主催メモ節除外の一言確認(任意・ユーザーから)。

---
### Entry 57 — 2026-07-29 — 第1回ハッカソンAIレビューリポの実査+分析計画の提示
ユーザー指示: ①ryukih/SD-Hackathon-Reviewer(2URLは同一リポ=旧名リダイレクト)をざっくり把握し分析計画を
提示 ②社会シミュレーション関連の他者PDFの共有方法を提案。
- **実査**: 第1回(2026-05-14)全提出のClaude自動採点リポ。40点ルーブリック(A創発設計/B世界設定/C発展性/
  D技術実装・各10点・2回採点平均+独立再検証+検証総括)・評価md31組・スライドPDF・評価スキル定義
  (.claude/skills/evaluate-submission/SKILL.md)・参照実装のみ収録(チーム本体コードはgitignore=各自の
  公開リポリンクで辿る)。**shibuya-sim(syota/Aji)は4位35.0/40**(A9.0/B9.0/C8.0/D9.0=最弱軸C発展性)。
  上位=lunar_agents 37.0・Project_Gaara 37.0・near-future-ai-society 36.0。ルーブリックA軸「生データのみ・
  行動指示なし」は本プロジェクトのR9/no-fingerprintと同型=現行設計の強い追い風。
- **分析計画(3フェーズ・実行はユーザー承認待ち)**: P1=自チーム講評精読→現行shibuya-simulationとの
  解消状況対照表→未解消の本選タスク化(C軸減点理由の精査を最優先)。P2=ルーブリック逆算チェックリスト+
  上位3作品との差分分析(eval根拠引用+スライド+必要なら公開リポのコード)。P3=全31評価の軸別分布・
  頻出強み弱み語彙の横断集計。成果物=docs/research/hackathon1-review-analysis.md+本選提出物チェック
  リスト。第2回が同一ルーブリックとは限らない旨の正直註記つき。
- **PDF共有方法の提案**: 推奨=リポジトリ外のローカルフォルダ(例 Desktop\shared-refs\)に置きパスを共有
  (ReadツールでPDF直読可・公開ミラー混入リスク構造ゼロ)。Web入手可ならURLのみで可。Google Drive連携は
  未認証のため非推奨。

---
### Entry 58 — 2026-07-29 — 第1回全提出物の横断分析実行(PDF2本+31リポ・Opus5×8体・IDEA228件)
ユーザー指示: Desktop\PDF資料の2本を参考に第1回の他参加者コード/リポを分析し、shibuya-simulationに
活かせそうな点・技術的に面白い点を記録。記録物への知見はwebリサーチで補強。記録方法は柔軟に(1ファイル
に押し込まない)。**途中指示: 調査内容は公開GitHubにコミットしない**。
- **PDF**: report.pdf=匿名実践レポート「言葉が世界を動かすまで」(12人30日・Qwen3.5 4B・否定的結果の
  正直な記録)を精読→pdf-notes.md(「LLM判断2回」設計ドリフト・文章/画面/因果の三分法・oracle=評価装置
  自体の検証・not_reached区別・出自固定表)。はぐら氏kibo_crew_sim資料=画像15頁をPNG化しG4担当が全頁
  視覚読解(リポより新しい事実上のREADME=Run3/4/5比較・行動プロファイル類型)。
- **体制**: docs/research/hackathon1-analysis/ を新設(ハブREADME・00ルーブリック・01自チーム・02上位3・
  teams/32本・ideas/8本・ideas-ledger統合台帳・pdf-notes)。Opus5サブ8体並列(自チーム/ルーブリック+未評価/
  上位3/中位下位5グループ)・各チーム=講評+_eval_review+コード実査+スライド(fitz抽出orPNG視覚)+web
  リサーチ(URL付き)。**IDEA総起票228件(★★★102/★★111/★15)**を機械抽出で索引化し台帳へ統合。
- **主結論**(台帳T1-T7): ①C軸は総合点と最強相関r=0.942・自チームC-2.0はほぼ全量README将来展望不在=
  文書で回収可能(上位3に唯一負けた軸もCのみ) ②A軸は防御軸・減点は「誘導が残る層の成果物への近さ」で
  決まる→no-fingerprintのCI機械証明を提出物表層へ(31チーム中我々のみ可能) ③観測ギャップ=LLM成功率/
  fallback率のL2系列が現行に無い(第1回「エラー率83.7%事後判明」+report.pdf「判断2回」と同じ穴)→健全性
  KPI+watchdogゲート ④研究輸入品=未定義行動(enum外)計測=改変者の操作的定義候補(kibo)・規範化の言語
  形式検出(lunar_sim)・LLM臨界質量が人間25%(Centola2018)より低い可能性(beyond-badminton 80%即時採用)・
  初期個体差ゼロ対照(workplace)・初期フレーム共変量(kibo/mars固着)・ground_truth/rumorペア5分類(Alberia)
  ⑤講評はリポのみ読んで採点(スライド不参照)→スライド情報のREADME/RESULTS回収が必須。
- **公開防御**: publish_public_mirror.ps1の除去パスに docs/research/hackathon1-analysis を追加(filter-repo
  --path+push前検証regex)=公開ミラーへ構造的に混入しない。PDF原本はリポ外のまま。実装・提出物への反映は
  standing rule(実装前確認)に従い別途合意して着手。

---
### Entry 59 — 2026-07-29 — 4系統拡張(A環境ツイン/B物理二層/C視覚広告/Dアフォーダンス)の検証済み実装計画
ユーザー指示: claude-code-planning-prompt.md(4系統拡張のプラン策定依頼書)を読んで実装計画を立てる+
同ファイルの処遇も決める。
- **検証体制**: Opus5サブ2体=①リポ接点実査(999行・9節・file:line付き→scratchpad)②文献/PLATEAU/k指標
  webリサーチ(553行・全主張URL付き→scratchpad)。Fable5が両報告を統合して計画書を執筆。
- **成果物**: docs/plans/twin-physics-vision-affordance-plan.md(§0原指示の訂正9点・§1リポ調査報告・
  §2 3レーン計画・§3 H指標3案・§4未決10件+推奨・§5不変条件整合・付録=原指示全文)。
  **原指示ファイルは吸収→削除**(endogenous-relations先例と同じ・原文は付録+git履歴に保存)。
- **主要訂正**: ①本選日程は8/15-8/30(指示書の8/8-8/23は旧テンプレ)→10日ランは8/16-8/26推奨
  ②CONSCIENTIA(2604.09746)がLLM×ビルボード曝露を既にやっている→Cの新規性は受動的視界曝露・長期反復・
  幾何的視覚計算の3点に限定 ③「7-need負フィードバック」は不正確=実体はEPR正フィードバック(診断ランの価値は不変)
  ④環境軸はkと衝突するためH(到達異質性)へ改名=k×Hの2軸 ⑤Isaac SimはRTコア必須(幾何方式なら不要・デモ用)。
- **実査の重要発見**: PLATEAU実高さ6311棟+OSM対応表3531棟+抽出パイプラインは既に完備(欠けは配線のみ)・
  street.py=OOH骨格実装済み(LOSなし距離のみ)・驚きゲートは現存せず(欲求駆動発火・計画/内省はLOD予算外)・
  goods.py=本物のrivalry実装済み・最大欠落は「場所の意味づけ」・★endo7スイープがcontrols.mode:noneで
  k=off/free呼数9.5%乖離(P0で再走要)・★bench.jsonが3体スモークで上書き=スケーリング実測喪失(P0で再取得)。
- **H指標3案**: H_C非冗長性(Burt・既存関係グラフで今すぐ)/H_A遭遇エントロピー(Moro 2021 NatCommun直訳・
  L1近似は即可)/H_B時空間プリズム内異質性(Hägerstrand・本命・A1のworld.modがedge走行時間を供給)。
  AとBの乖離=機会の未活用が独立の知見。
- **レーン概要**: 前=P0前提整備(ベンチ再取得/endo7再走/LLM健全性KPI)→A1環境条件スキーマ+実高さ配線→
  B-L0 3D再生仕上げ→C0可視行列基盤(O(n·m))→D0診断+事前登録(既存daily300_100dへ即適用)→D1軽量
  アフォーダンス(場所の意味づけ最小版)。中=コード凍結・10日ラン8/16-26・実LLM診断は開放初日・B-L1は
  ブランチ仕込み。後=B-L2屋外SFM・C 3条件本実験+VLM・A反実仮想H掃引・D本実装。
- 未決10件(範囲U-1・規模U-2・H命名U-6・診断閾値の事前登録承認U-10など)はユーザー判断待ち。実装着手はまだしない。

---
### Entry 60 — 2026-07-29 — 第66バッチ: 4系統拡張レーン1第1波(P0前提整備+D0診断+B-L0 3D規模検証・1772緑)
ユーザー指示「実装できるところは実装を始めてほしい」→計画書レーン1の独立3バッチをOpus5サブ3体並列で実装、Fable一括検収。
- **P0**: bench_scaling新設(N=10..1000実測+10000はrehearsal流用・ms/agent-step 18.37→1.155@N1000・
  bench.pyを上書き防止化・summary.jsonにelapsed_sec/peak_rss_mb追加キー)・endo呼数交絡の是正
  (3 manifestにcompute_matched明示・endo8w 12ラン19分再走=mock系統偏り−5.50%→−1.23%符号混在・
  切り分けprobe=固定応答LLMなら1199=1199完全一致→「完全一致」受入基準はmockでは原理的に不可という訂正)・
  LLM健全性KPI 3列(observer.llm_health.enabled既定false=resumeのL2バイト一致保護・fallback率は
  発話系パース失敗のみ=真の下限と明記・watchdog --fallback-warn+watchdog_llm.py事後点検)・
  死んだキーlod.congestion_surprise削除・finals-llm-budget.md(予算外呼=総数の10.7%・実プロンプト実測
  1,014入力tok/41.5出力tok=million-scaleの320出力仮定は約8倍過大・present推奨1万)。
- **D0**: diagnose_stationarity.py(L1のみ・2パスストリーム・22テスト)+事前登録ドラフト
  (stationarity-preregistration.md・承認前変更自由/承認後変更禁止を明記)。daily300_100d実測=
  **TRANSIENT_ONLY**: Day2vs5はTVD0.111/p=1e-4でPASSだが**Day96vs99はノイズ床R=0.98**=約18日の
  burn-in後に定常化・lag=7の週次リズム自動検出(weekday_workと整合=ツール妥当性確認)。提案閾値=
  p<0.05∧TVD≥0.05∧R≥1.50(ノイズ床比)+late_same_lag条件。★**本選10日ランは丸ごとburn-in内**=
  Day2vs5だけでは自明に非定常が出る→診断日数と解釈はU-10承認時に要判断。
- **B-L0**: export_3d --low-mem(既定OFF・出力バイト同一19/19検証・84.8s→12.8s/RSS13.3GB→2.05GB)=
  10日ラン再生を実質可能化(既定パスは外挿≈128GBで不可・間引きレシピでviewer≈88MiB)・
  ★data/plateauは既に2025年度CityGML由来と判明(建物更新はno-op)・★道路LOD3(歩道=codelist2020
  定義済・シム範囲4タイルに約5,800面)が未抽出で手元GMLに存在=B-L2/H_Bの素材(被覆1.41km²は要マップ)。
- **検収補修(Fable)**: start_date="auto"の実行日依存(同一設定で6,507→6,635呼)を3 manifestに
  固定日2026-08-17(月曜=endo7と曜日整合・本選週)で排除。検収78本+統合フルゲート1772緑。
  持ち越し=analyze_sweepへのKPI3列接続・計画書ステータス更新(第2波で)。
