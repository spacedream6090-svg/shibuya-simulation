# アーキテクチャ5層対応表(2026-07-14 ユーザー採用・第33バッチ)

エンジン群の恒久整理として **5層**(Agent/World/Society/Dynamics/Meta)を正とする
(docs/plans/engine-architecture.md §2 の提案をユーザーが採用)。
**コードの再編はしない** — 本表は「概念の層 ↔ 実装の在り処」の対応をドキュメントとして固定するもの。
全エンジンの詳細な被覆状況は [engine-coverage-map.md](research/engine-coverage-map.md) を一次資料とする。

| 層 | 含むエンジン(概念) | 実装の在り処(代表) |
|---|---|---|
| **Agent層**(個体の認知) | 知覚・注意 / 記憶 / 推論 / 計画 / 目標 / 感情 / 人格 / 健康 / 自己同一性 / 信念・世界観 / 言語 | `src/society/cognition/`(deliberate・reflection・planning・lod)・`agents/`(persona・memory)・`factors/`(mood・affect・registry)・`health.py`・`inner_life.py`・`worldview.py` |
| **World層**(舞台) | 空間・地図 / 交通 / インフラ / 住宅 / 天気 / 災害 | `src/society/world/`(map・routing・transit・traffic・perception・vision・scenario)・`weather.py`・`disaster.py`・`lodging.py` |
| **Society層**(相互作用が作る構造) | 経済 / 消費 / 労働 / 娯楽 / 情報 / SNS / 噂 / メディア / 行政 / 企業 / 教育 / 医療 / 治安 / 文化 / コミュニティ / 信頼 / 規範 / 政治 / 評判 / 家族 | `economy.py`・`commerce.py`・`organizations.py`・`career.py`・`net/`(internet・infoenv)・`media.py`・`government.py`・`rules.py`・`recursion.py`・`relations.py`・`status.py`・`annual.py`・`diversity.py`・`household.py`・`institution_routes`(scheduler 内) |
| **Dynamics層**(統合・時間) | 時間進行 / 行動反映 / 内省(k) / 社会力学 / 世界モデル | `engine/`(simulation・scheduler)・`world/clock.py`・`world/calendar.py`・`actions/`・`tools.py`・`cognition/reflection.py`・`opinion.py`・`drive.py` |
| **Meta層**(研究基盤・系外) | 観測(L1/L2/L3) / 再現性(乱数・CRN・ゴールデン) / 実験マニフェスト / 較正・検証 | `observer/`(logger・schema・aggregate・measure)・`rng.py`・`llm/cache.py`・`conf/experiments/`+`scripts/run_experiment.py`・`scripts/calibrate_report.py`・`scripts/analyze_*.py` |

## 4抽象・情報遷移システムとの対応(参照用)
- 4抽象(State/Decision/Interaction/Evolution): Agent層+World層=State、Agent層の意思決定=Decision、
  Society層=Interaction、Dynamics層=Evolution。Meta層は研究者フレーム(系外)。
- 情報遷移システム(Environment/Entity/State/Behavior/Interaction): Environment=World層、
  Entity=agents/組織/POI、State=agent状態+L3スナップショット、Behavior=routine/deliberate、
  Interaction=hear/transmission/opinion/市場。**現実装は既にこのモデルに一致**しており、
  読み替えのためのコード変更は不要(engine-architecture.md §2)。

## 4層パイプライン(知覚→思考→意思決定→行動)との対応
1ステップの流れ(詳細は engine-coverage-map.md §13):
知覚=scheduler の知覚組み立て(hearers_of・feed・retrieve)→ build_prompt /
思考=drive 発火 → LLM 生成(deliberate)/ 意思決定=parse_action(+失敗時 routine)/
行動=_apply → factors/update → L1 記録。
