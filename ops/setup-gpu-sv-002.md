# gpu-sv-002 開発環境セットアップ手順(引き継ぎメモ§26の実コマンド版)

> 2026-08-16作成。前提: [引き継ぎメモ](../GPUサーバー環境構築・接続トラブル対応%20引き継ぎメモ.md)の状態
> (VPN/SSH/venv(~/venvs/gpu)/PyTorch/7GPU実演算=完了)。この先は [runbook-first-night.md](runbook-first-night.md) と対で使う。
> **不変の原則**: NVIDIA Driver・VPN・OSは触らない/`shutdown`系・`apt autoremove` 禁止/認証情報はチャット・リポに書かない(貸与元にローテーション相談推奨=メモ§25)。

## 1. VS Code Remote-SSH(Windows側・5分)

`%USERPROFILE%\.ssh\config` に追記:
```text
Host gpu-sv-002
    HostName 10.10.0.102
    User tsukamoto
    ServerAliveInterval 60
    ServerAliveCountMax 3
```
VS Code拡張「Remote - SSH」→ `gpu-sv-002` へ接続(VPN接続中のみ)。`ServerAliveInterval` はVPN越しの無通信切断対策。

## 2. venv 構成(サーバー側・10分)— ★3本に分ける

| venv | 用途 | 理由 |
|---|---|---|
| `~/venvs/gpu` | 既存(PyTorch検証用) | **触らない**(正常動作の保存) |
| `~/venvs/sim` | **シミュレーション本体** | シムはtorch不要(LLMはHTTP経由)=軽量・依存衝突なし |
| `~/venvs/vllm` | vLLMサーバー | vLLMは自分のtorchをpinする=分離が安全 |

```bash
python3 -m venv ~/venvs/sim
python3 -m venv ~/venvs/vllm
```
VS CodeのPython Interpreterはリポを開いたら `~/venvs/sim/bin/python` を選択。

## 3. Git/GitHub(サーバー側・10分)

**推奨=サーバーはpull専用**(pushとコミットは従来どおりローカルPC側=Fable検収体制を維持):
```bash
ssh-keygen -t ed25519 -C "gpu-sv-002-deploy" -f ~/.ssh/id_ed25519_github
cat ~/.ssh/id_ed25519_github.pub
# → GitHubのリポ Settings > Deploy keys に「Read-only」で登録(書き込み権限は付けない)
cat >> ~/.ssh/config << 'EOF'
Host github.com
    IdentityFile ~/.ssh/id_ed25519_github
EOF
git config --global user.name "syota tsukamoto"
```

## 4. リポ配置と依存(サーバー側・10分)

```bash
mkdir -p ~/projects && cd ~/projects
git clone git@github.com:<owner>/shibuya-simulation.git
cd shibuya-simulation
source ~/venvs/sim/bin/activate
pip install -U pip && pip install -e .        # pyproject.toml から
export PYTHONIOENCODING=utf-8                  # ~/.bashrc にも追記推奨
python -m pytest tests/test_scenario.py -q     # 動作確認(golden数本・1-2分。フルゲートは不要)
```

## 5. Claude Code / Codex(サーバー側・任意・10分)

```bash
# Claude Code(nativeインストーラ・Node不要)
curl -fsSL https://claude.ai/install.sh | bash
claude          # 初回にブラウザ/デバイス認証(トークンを手で貼らない)
# Codex(Node 18+が必要。nvm経由が安全)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
nvm install --lts && npm install -g @openai/codex
```
※インストールコマンドが変わっていたら公式docsを正とする。VS Code Remote のターミナルで `claude` / `codex` / 監視(`watch -n 1 nvidia-smi`)の3枚構成(メモ§20 Phase4-5)。

## 6. データ搬入=ペルソナプールの決定論リビルド(サーバー側・15分)

```bash
cd ~/projects/shibuya-simulation && source ~/venvs/sim/bin/activate
python scripts/build_persona_pool.py --seed 42 --out data/persona_pool          # v1(本選用)
# v2はPhase4(切替判断後): python scripts/build_persona_pool.py --seed 42 --v2 --childcare --out data/persona_pool_v2
```
**同一性の照合**(ローカルPCとサーバーの両方で実行して一致を確認):
```bash
python - << 'PY'
import hashlib, pathlib
h = hashlib.sha256()
for p in sorted(pathlib.Path("data/persona_pool").rglob("*")):
    if p.is_file():
        h.update(p.name.encode()); h.update(p.read_bytes())
print(h.hexdigest())
PY
```

## 7. vLLM とモデル重み(サーバー側・30-60分)

```bash
source ~/venvs/vllm/bin/activate && pip install -U pip vllm
curl -sI https://huggingface.co -o /dev/null -w "HF egress: %{http_code}\n"
```
- egressが通る → 初回起動時に自動ダウンロード(qwen3:8b級=A5000 1枚に載る)
- 通らない → ローカルPCでDL→`scp`で `~/.cache/huggingface/` へ転送
- 起動コマンドは Windows側で `powershell -NoProfile -File ops/launch-vllm-finals.ps1`(dry-run表示)の7本をサーバーへ貼る。**必ずtmux内で**:
```bash
sudo apt install -y tmux    # 無ければ
tmux new -s vllm            # 中で7本起動(ウィンドウ分割 or 連続&)。抜けるのは Ctrl-b d
python scripts/check_llm_backends.py --backend openai_compat --base-url http://localhost:8000/v1 --model qwen3:8b   # 8000..8006
```

## 8. ★ランは必ずtmux(またはnohup)で

**VPN/SSHは切れるもの**。SSHセッション直下でランを走らせると切断=ラン死。
```bash
tmux new -s run
# この中で runbook-first-night.md の Phase 1(2,000×144計測)→ Phase 2(10,000×1日)を実行
# 別window(Ctrl-b c)で watchdog / report_progress / watch -n 1 nvidia-smi
```
途中経過の目視は live_viewer の生成HTMLを VS Code Remote でそのまま開くのが最速(scp不要)。

## 9. この後

[runbook-first-night.md](runbook-first-night.md) の Phase 1 へ。**R_eff と c の実測値が出たら貼ってください——fire GO/NO-GO と本番壁時計の判定を即返します。**
