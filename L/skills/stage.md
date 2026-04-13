# Skill: /stage — 演劇型素材生成（Stage System連携）

## いつ使うか
ユーザーとの対話の中で「このシーンはStageで」と決まったとき。
自分で判断して使わない。使用はユーザーの指定、またはユーザーとの合意による。

### Stageが効く場面
- 2人以上のキャラの掛け合いが核心のシーン
- キャラクター間の化学反応・予測の外れ・かみ合わなさが重要な場面
- 方向性が未確定で、複数の解釈を試したいシーン

### Stageが不要な場面
- 独白・内省中心のシーン
- 設計が既に固まっていて、あとは散文化するだけの場面
- Opusの推論の深さが直接必要な心理描写中心の場面

## Stageの仕組み
Stageは独立プロジェクト（`../stage/`）。
ペルソナを持った「役者」がローカルLLM（Gemma 4 26B）とSonnetで共有ワークシート上をリレー演技し、複数テイクから監督が最良パーツを選んで素材パッケージを作る。

### Stageの価値
Opusの予定調和を破壊する装置。異なるモデルの衝突から、Opus単体では生まれない掛け合いの化学反応を引き出す。表現力の補完ではなく、歪みの供給源。

## 実行手順

### 1. scene_detailの引き渡し
現在の対話で確定している設計書（/plot, /structure, /psyche, /dominator, /mechanics の出力）とscene_detailを整理する。

### 2. Stageプロジェクトでの撮影
Stageプロジェクトのワークフローを実行する：
- /cast — キャスティング（ペルソナ×役×モデルの決定）
- /rehearsal — 共有ワークシート上でリレー演技（複数テイク）
- /cut — テイク評価・選択・混成
- /wrap — 素材パッケージング

実行方法：Agent toolでStageプロジェクトディレクトリを作業ディレクトリとして起動するか、メインコンテキストで直接scripts/actor.pyを呼び出す。

### 3. 素材の受け取りと/writeへの接続
/wrapの出力（Stage Output）を受け取り、/writeに渡す。
Stage Outputには以下が含まれる：
- Selected Performance（採用テイクの組み合わせ）
- Director's Note（活かすべき表現、トーン指定、補足事項）

/writeのAgentには通常の設計書に加え、Stage Outputを「演技素材」として渡す。

## 参照
- Stage CLAUDE.md: `../stage/CLAUDE.md`
- Stageペルソナ: `../stage/personas/`
- actor.py: `../stage/scripts/actor.py`
