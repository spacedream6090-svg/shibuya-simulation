# 本選の信頼性・バックアップ計画 — 「結果を確実に持ち帰る」ための運用設計

> 入力: ユーザー指示(2026-08-12)「本選でのシミュレーションデータのバックアップ方法など、確実に結果を出せるようにするにはどうしたらいいか考えて実装の準備、計画をしてほしい。実際に実装する必要はない」。
> 退避先の回答(同日): **ローカルPCの空き/外付けHDD=利用可**・クラウド可否とGPU機の帯域/ディスクは8/15に判明(全パターン用意)。
> リサーチ正典: [finals-backup-reliability.md](../research/finals-backup-reliability.md)(リポ実物+文献20本超)。**本計画は準備・計画のみ=実装しない**。

## 0. 結論(3行)

1. **既にある機構を主軸にする**: watchdog.py(自動resume・ストール検知・破損時1世代前巻き戻し・3世代バックアップ)+checkpoint/finalize の原子的書き込み(tmp→os.replace)+zstd圧縮済みL1 part。新規実装はほぼ不要で、**運用手順とリハーサルが本体**。
2. **3-2-1の当てはめ**: ①GPU機内の世代コピー(watchdog既存)②**ローカルPCへの日次pull**(ユーザー回答=主線)③クラウド1系統(可否判明後・B2/R2候補=月数ドル)。同期は**copy系のみ(sync/MIR禁止=誤削除を伝播させない)**+sha256マニフェスト3箇所照合。
3. **checkpoint間隔は8/15-16にCを実測してから決める**(Young/Daly: T_opt=√(2Cμ)。現行72step≈12hは「checkpoint 60分・MTBF 72h」でのみ最適。C=15分・MTBF=24-48hなら21〜29step≈3.5-5hが最適)。

## 1. 守るべき資産(致命度分類)

| 資産 | 再生成 | 扱い |
|---|---|---|
| **L1 parts(runs/<id>/l1_events.part-*)** | 不可(実LLM10日=再走不能) | 最優先。**checkpoint境界後に確定したpartのみ**をバックアップ対象に(flush中partはfooter不完全でありうる=parquet footer検証を通ったものだけ転送) |
| **checkpoint/ + dormant サイドカー(全世代)** | 不可 | ★**剪定禁止**(下記 §1.1)。`backup_run.py --ckpt-generations 999` で**全世代**を退避する |
| summary.json・run_manifest・サイドカー群 | 部分的に可 | L1と同梱で転送 |
| conf(finals_observe.yaml)・コード | git | 転送不要(コミット済みが正) |
| 台帳・プール(data/) | 可(リビルド11.9s) | 初日に1回だけ退避。**sha256 は run_manifest.json の `inputs` 節に残る**(第114 G1) |

### 1.1 ★checkpoint / dormant 世代の剪定禁止(第114 G2・2026-08-14 確定)

**規則: 本選ランの `checkpoint/` は 1 世代も消さない。** `ckpt-NNNNNN.pkl.gz` と同 step の
`dormant-NNNNNN.pkl.gz` は**必ず対で**残す(片方だけでは在場者しか復元できない)。

理由(復元実験の正解ラベルの唯一の複製だから):

| 中身 | 他に残る場所 | 剪定したら |
|---|---|---|
| ペルソナ文(persona の本文) | **無い**(traits.json は数値・roster.parquet は素性欄のみ) | 二度と取れない |
| 記憶ストリームの本文 | memory.parquet(G4・日境界の粒度) | **半日粒度**が失われる |
| 関係台帳の全対 | relations.parquet(G5・変化した対のみ) | 台帳の全体像が失われる |
| 信念・自己モデル・可塑性 g の全欄 | 一部が L1/サイドカー | 半日粒度の完全状態が失われる |

- ディスクが逼迫したときに**最初に消してよいのは checkpoint ではない**。順序は
  ① `indoor_tracks_*`(ON なら)② `llm_journal`(応答全文。ただし思考の代理なので慎重に)
  ③ それでも足りなければユーザー判断を仰ぐ。**checkpoint と dormant は最後**。
- `scripts/backup_run.py` は `ckpt-` と `dormant-` を同 step で対に扱う実装になっている
  (`CKPT_PREFIXES`)が、**既定 `--ckpt-generations 2` は直近 2 世代しか転送しない**。
  本選では明示的に `--ckpt-generations 999`(= 全世代)で回すこと。**この既定値のままだと
  「バックアップは取れているのに 20 世代のうち 18 世代が手元に無い」という事故になる。**
- watchdog の「3世代バックアップ」はノード内のローリング複製であって、**世代保全ではない**。

## 2. 障害モード×対策(要点・詳細はリサーチ§2)

- **プロセス死/ハング/OOM**: watchdog常駐(自動resume・ストール検知)。実測根拠=大規模LLM実運用で中断は日常(GPU起因58%)。resume整合はD1レーンで修正済みの straight==resume を8/15のdrillで再確認。
- **vLLMの長時間劣化**: 日次計画再起動を運用に組み込む(深夜の呼数谷で・シム側はbackend再接続)。
- **ディスクフル**: 残量閾値の監視(watchdogのログに残量1行を足すのは小改修=承認あれば)。★**checkpoint 世代の剪定は禁止**(§1.1)。逼迫時に落とすのは indoor_tracks → llm_journal の順で、checkpoint/dormant は最後。
- **誤削除・人為ミス**: 転送はcopy系(rclone copy / robocopy 非MIR)のみ。削除を伝播させない。
- **L1破損**: footer検証+sha256マニフェスト(BagIt式)を転送単位ごとに生成・3箇所照合。
- **電源/ネットワーク断**: tmux/systemd配下で実行(切断耐性)・ローカルpullは再開可能なrclone/robocopyの再実行で冪等。

## 3. 転送・保管(ユーザー回答反映)

- **主線=ローカルPC日次pull**: 日次増分5-15GB想定→100Mbpsで30分未満。part はzstd圧縮済み=再圧縮不要・日次分をtar化して転送→ローカルで sha256 照合→外付けHDDへ二次コピー。
- **クラウド(可否判明後)**: rclone一本で sftp/S3系を同一手順化。概算=B2≈$1/月・R2≈$2.3(egress無料)。
- **GPU機ノード内**: watchdogの3世代+日次tarを別ディレクトリ(可能なら別ディスク)へ。
- 帯域が想定外に細い場合の縮退: L1のみ日次・checkpoint週2・サイドカーは最終日に一括。

## 4. リハーサル(8/15-16診断日に組み込む・7本)

1. **C実測**(checkpoint書き込み時間・世代サイズ@25万)→ Young/Daly で checkpoint_every を確定
2. **resume drill**(kill→watchdog自動復帰→L1整合確認)
3. **restore drill**(★バックアップコピーだけで解析(l1_stream系)が回るか=「バックアップはあるが復元できない」事故の予防)
4. 障害注入(ディスク残量僅少・vLLM停止・プロセスkill の3種)
5. 転送drill(実サイズのtar→ローカルpull→sha256照合の所要時間実測)
6. 無人運用drill(夜間8hを触らず放置→朝の状態確認手順)
7. vLLM計画再起動drill(シム側の再接続確認)

## 5. 8/15に確認する環境項目(5点)

GPU機の①外向き帯域 ②空きディスクと別ディスク有無 ③クラウド到達可否(egress制限) ④OS/tmux/systemd利用可否 ⑤運営側のバックアップ/スナップショット有無。

## 6. 小物の実装状況(2026-08-12ユーザー承認→同日実装)

- **実装済み(第110)**: ①watchdogディスク残量ガード(5分毎1行ログ+warn/crit閾値・警告のみ=止めない・status.jsonにdisk節)②`scripts/backup_run.py`(確定分のみ=footer検証+checkpoint mtime条件・増分tar+BagIt式sha256マニフェスト・冪等=差分ゼロなら1バイトも書かない・削除非伝播・`--verify`・★checkpoint対のdormantサイドカー同梱・★Windows走行中ランはFILE_SHARE_DELETEで安全読み)。**restore drill前段が実測成立**(バックアップコピー単体でwatchdog_llm完走・tar展開→解析OK)。使い方=スクリプトdocstringと完了報告のコマンド例。
- **未実装(意図的)**: ローカル側pull(PowerShell)=転送はユーザー側・checkpoint世代の剪定=何を消すかは人間判断・クラウド系統=可否判明後。閾値既定20/5GBは小規模想定=**8/15実測後に本選値へ**(推奨warn=日次増分×3〜200GB/crit=50GB)。
