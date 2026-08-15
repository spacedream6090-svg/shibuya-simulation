# GPUサーバー環境構築・接続トラブル対応 引き継ぎメモ

## 0. この文書の目的

Windows 11 PCから、貸与されたUbuntu GPUサーバー `gpu-sv-002` にVPN → SSHで接続し、7枚のRTX A5000をPython / PyTorchから利用できるところまで環境構築した。

現時点では、

**VPN接続、SSHログイン、Ubuntuへのアクセス、Python仮想環境、PyTorch CUDA認識、7GPUでの実演算テストまで全て成功済み。**

今後はVS Code Remote-SSH、開発リポジトリ、Claude Code / Codex、LLM実行環境などを整えて、本来の開発・シミュレーション作業へ移る段階。

---

# 1. サーバー概要

サーバー：

```text
hostname: gpu-sv-002
IP: 10.10.0.102
OS: Ubuntu 22.04.5 LTS
Kernel: 5.15.0-187-generic
SSH user: tsukamoto
```

GPU：

```text
NVIDIA RTX A5000 × 7
各GPU 約24GB VRAM
合計 約168GB VRAM
```

`nvidia-smi` では7枚すべて正常認識されている。

確認時：

```text
Driver Version: 595.84
nvidia-smi上の CUDA Version: 13.2
```

GPU 0〜6すべてアイドル状態で認識された。

---

# 2. VPN構成

Windows 11からL2TP/IPsec VPNを使用している。

方式：

```text
VPN type:
L2TP/IPsec with pre-shared key

VPN server:
152.165.117.187
```

VPN用ユーザー名・パスワード・PSKは別途発行済み。

※認証情報はこの引き継ぎ文には意図的に記載していない。

---

# 3. 最初に発生していたVPN問題

Windows 11でVPN接続すると、

```text
セキュリティ層でリモート コンピューターと
互換性のあるパラメーターをネゴシエートできなかったため、
L2TP接続に失敗しました
```

というエラーが発生。

RasClientログでは、

```text
Reason code: 788
```

だった。

つまり、最初はユーザー名・パスワード認証以前の、

```text
IKE / IPsec
↓
L2TP
↓
PPP認証
```

のうち、**IKE/IPsec側で失敗していた。**

---

# 4. NAT-T対策

Windowsの管理者PowerShellで以下を設定済み。

```powershell
Set-ItemProperty `
  -Path "HKLM:\SYSTEM\CurrentControlSet\Services\PolicyAgent" `
  -Name "AssumeUDPEncapsulationContextOnSendRule" `
  -Type DWord `
  -Value 2
```

PC再起動も実施済み。

確認すると、

```text
AssumeUDPEncapsulationContextOnSendRule : 2
```

となっている。

そのため、この設定は現在も有効。

---

# 5. VPNプロファイルの試行錯誤

途中でWindows側に、

```text
VPN
GPU-VPN
```

の2つのVPNプロファイルが存在していた。

古い `VPN` は788で失敗していたため、その後は主に `GPU-VPN` を使って調査。

## GPU-VPNで一度進展した状態

当初、

```text
AuthenticationMethod : {Eap, MsChapv2}
EncryptionLevel      : Optional
L2tpIPsecAuth        : Psk
```

という状態では、RasClientに、

```text
リモートアクセスサーバーへのリンクを正常に確立
```

が記録され、

```text
628
```

まで進んだ。

これは、

```text
IPsec OK
L2TP OK
↓
PPP / 認証付近で切断
```

と判断できる状態だった。

---

# 6. GUIのセキュリティ設定変更後に788が再発

WindowsのVPNプロパティで、

- L2TP/IPsec
- データ暗号化
- CHAP / MS-CHAPv2
- IPv4 / IPv6

などを設定し直したところ、再び788になった。

そのため、

```powershell
Set-VpnConnectionIPsecConfiguration `
  -ConnectionName "GPU-VPN" `
  -RevertToDefault `
  -Force
```

を使って、カスタムIPsec設定を一度デフォルトに戻した。

---

# 7. PPP暗号化設定と788/628の関係

一時的に、

```text
AuthenticationMethod : MSChapv2
EncryptionLevel      : Maximum
```

にすると再び788。

その後、

```powershell
Set-VpnConnection `
  -Name "GPU-VPN" `
  -AuthenticationMethod MSChapv2 `
  -EncryptionLevel Optional `
  -Force
```

として、さらにL2TPのPSKを明示的に再入力。

するとRasClientが再び、

```text
20223:
リモートアクセスサーバーへのリンクを正常に確立

20224:
リンクは確立されました

Reason code: 628
```

まで進んだ。

つまり、**788問題は実質的に突破できた。**

その後、CHAP / MS-CHAPv2を含む互換性のある設定でVPN接続を試したところ、最終的にVPN接続そのものが成功。

現在の正確な有効設定を確認する必要がある場合は、

```powershell
Get-VpnConnection -Name "GPU-VPN" |
Format-List Name,ServerAddress,TunnelType,AuthenticationMethod,EncryptionLevel,L2tpIPsecAuth
```

で再確認すること。

重要なのは、`EncryptionLevel = Maximum` にすると問題が再現した一方、`Optional` でIPsec/L2TPを突破できたという経緯。

---

# 8. VPN接続成功の確認

VPN接続後、

```powershell
ping 10.10.0.102
```

を実行。

結果：

```text
送信 = 4
受信 = 4
損失 = 0

24〜25ms程度
```

だった。

したがって、

```text
Windows
↓
VPN
↓
GPU内部ネットワーク
↓
10.10.0.102
```

の通信は完全に成功している。

---

# 9. SSH接続

Windowsから、

```powershell
ssh tsukamoto@10.10.0.102
```

を使用。

初回は、

```text
The authenticity of host ... can't be established
```

が出たため、

```text
yes
```

でED25519ホスト鍵を `known_hosts` に登録。

---

# 10. 一度SSHが切断されていた問題

初回SSH接続時、

```text
tsukamoto@10.10.0.102's password:
```

まで進んだ後、

```text
Connection closed by 10.10.0.102 port 22
```

となった。

`ssh -vvv` で調査すると、

```text
Remote protocol version 2.0
OpenSSH_8.9p1 Ubuntu

SSH2_MSG_NEWKEYS received

Authentications that can continue:
publickey,password

Next authentication method:
password
```

まで正常に進んでいた。

つまり、

```text
TCP/22
SSH handshake
鍵交換
暗号化
認証方式の選択
```

はすべて正常。

問題はパスワード入力後だった。

---

# 11. RDPでUbuntuに直接ログイン

SSH調査のためWindows Remote Desktopから、

```text
10.10.0.102
```

へ接続。

xrdpの、

```text
Session: Xorg
username: tsukamoto
```

でUbuntuデスクトップへのログインに成功。

この時点で、

- tsukamotoアカウントが正常
- パスワードが正常
- Ubuntu自体が動作中

であることを確認。

---

# 12. UbuntuのSSHログ調査

Ubuntu側で、

```bash
sudo grep -iE 'sshd|pam|tsukamoto' /var/log/auth.log | tail -100
```

を確認。

重要な過去ログとして、

```text
Accepted password for tsukamoto from 10.10.3.1
pam_unix(sshd:session): session opened for user tsukamoto
```

が存在。

つまり、**tsukamotoユーザーでのSSHパスワード認証はサーバー側で正常に動作していることが確認できた。**

そのため、SSH設定そのものに大きな問題はないと判断。

前回接続が切れたのは、パスワードプロンプト表示後に調査のため時間を空け、SSHの認証待ちタイムアウトに到達した可能性が高かった。

---

# 13. SSHログイン最終成功

改めて、

```powershell
ssh tsukamoto@10.10.0.102
```

を実行し、パスワードをすぐ入力したところ正常ログイン。

表示：

```text
Welcome to Ubuntu 22.04.5 LTS
...
tsukamoto@gpu-sv-002:~$
```

つまり現在、

```text
Windows
↓
L2TP/IPsec VPN
↓
10.10.0.102
↓
OpenSSH
↓
tsukamoto@gpu-sv-002
```

まで完全に動作している。

---

# 14. GPU確認

SSH接続後、

```bash
whoami
hostname
nvidia-smi
```

を実行。

結果：

```text
whoami
→ tsukamoto

hostname
→ gpu-sv-002
```

`nvidia-smi`：

```text
RTX A5000 × 7
GPU 0〜6
各24564 MiB程度
```

全GPU正常。

---

# 15. Python環境

サーバー標準：

```text
Python 3.10.12
git 2.34.1
```

一方、

```bash
nvcc --version
```

は、

```text
nvcc: command not found
```

だった。

ただしこれは現状問題ではない。

`nvidia-smi` のCUDA Versionはドライバが対応するCUDAバージョンを表しており、CUDA Toolkit / nvccがシステムに入っていることを意味しない。

PyTorchはpip側のCUDAランタイムを使用できるため、現時点ではシステムの `nvcc` は不要。

---

# 16. Python venv

最初、

```bash
python3 -m venv ~/venvs/gpu
```

を実行すると、

```text
ensurepip is not available
```

となった。

そのため、

```bash
sudo apt update
sudo apt install -y python3.10-venv
```

を実行。

その後、

```bash
rm -rf ~/venvs/gpu
python3 -m venv ~/venvs/gpu
source ~/venvs/gpu/bin/activate
```

で仮想環境作成に成功。

現在の仮想環境：

```text
~/venvs/gpu
```

有効化：

```bash
source ~/venvs/gpu/bin/activate
```

有効化後：

```text
(gpu) tsukamoto@gpu-sv-002:~$
```

Pythonは3.10.12、pipは最終的に26.2.1まで更新された。

---

# 17. PyTorch / CUDA環境

仮想環境内で、

```bash
pip install torch torchvision torchaudio
```

を実行。

インストールされた主要バージョン：

```text
torch       2.13.0
torchvision 0.28.0
torchaudio  2.11.0
```

PyTorch側にはCUDA 13.0系ランタイム、cuDNN、NCCL、Tritonなども導入された。

確認：

```python
import torch

print(torch.__version__)
print(torch.cuda.is_available())
print(torch.version.cuda)
print(torch.cuda.device_count())
```

結果：

```text
PyTorch version : 2.13.0+cu130
CUDA available  : True
PyTorch CUDA    : 13.0
GPU count       : 7
```

GPU 0〜6すべて、

```text
NVIDIA RTX A5000
約23.5 GB
```

としてPyTorchから認識された。

---

# 18. 7GPUの実演算テスト

単にGPUが列挙されるだけでなく、実際に7枚すべてでCUDA演算を実行。

テスト：

```python
for i in range(torch.cuda.device_count()):
    with torch.cuda.device(i):
        a = torch.randn(2048, 2048, device=f"cuda:{i}")
        b = a @ a
        torch.cuda.synchronize(i)
        print(f"GPU {i}: OK")
```

結果：

```text
GPU 0: OK
GPU 1: OK
GPU 2: OK
GPU 3: OK
GPU 4: OK
GPU 5: OK
GPU 6: OK

All GPUs OK
```

よって、**7枚すべてPyTorchから実際に計算可能な状態。**

---

# 19. 現在の完成状態

現在は以下まで完了。

```text
Windows 11
    │
    ▼
L2TP/IPsec VPN
    │
    ▼
10.10.0.102
    │
    ▼
SSH
    │
    ▼
Ubuntu 22.04.5
    │
    ▼
tsukamoto user
    │
    ▼
~/venvs/gpu
    │
    ▼
Python 3.10.12
    │
    ▼
PyTorch 2.13.0 + CUDA 13.0
    │
    ▼
RTX A5000 × 7
    │
    ▼
実CUDA演算成功
```

つまり、GPUサーバーの基礎セットアップは完了したと考えてよい。

---

# 20. 今後の展望

## Phase 1：VS Code Remote-SSH化

次の最優先事項。

Windows側のVS Codeから、

```text
tsukamoto@10.10.0.102
```

へRemote-SSH接続する。

毎回PowerShellからSSHしてvim等で作業するのではなく、

```text
Windows VS Code UI
        ↓
Remote SSH
        ↓
gpu-sv-002
```

という形で開発する。

SSH configには例えば、

```text
Host gpu-sv-002
    HostName 10.10.0.102
    User tsukamoto
```

を設定すると扱いやすい。

VPN接続中のみアクセス可能。

---

## Phase 2：VS CodeのPython Interpreter設定

VS Code Remote側で、

```text
/home/tsukamoto/venvs/gpu/bin/python
```

をPython Interpreterとして選択。

これによりVS Code上の、

- Python
- Jupyter
- lint
- debug
- terminal

などを同じGPU仮想環境に揃える。

---

## Phase 3：Git / GitHub環境

本番プロジェクトを、

```bash
~/projects/
```

などに置く。

例：

```bash
mkdir -p ~/projects
cd ~/projects
git clone <repository>
```

SSH keyやGitHub CLIなども必要に応じて設定。

---

## Phase 4：Claude Code / Codex

Remote-SSHしたVS Codeのターミナル上から、

```text
claude
codex
```

を使えるようにする。

理想構成：

```text
VS Code Remote-SSH

Terminal 1:
claude

Terminal 2:
codex

Terminal 3:
python / server / monitoring
```

とする。

Claude/Codexが操作するファイルもGPUサーバー上の同一リポジトリになるため、ローカルPCとの同期を意識する必要がなくなる。

---

## Phase 5：GPU監視

開発中は別ターミナルで、

```bash
watch -n 1 nvidia-smi
```

を動かしておくとよい。

これで、

- GPU使用率
- VRAM使用量
- GPU温度
- 使用中プロセス

をリアルタイム確認できる。

---

## Phase 6：LLM実行環境

PyTorch GPU基盤は完成したので、次に用途に応じて、

- Transformers
- Accelerate
- vLLM
- Hugging Face
- bitsandbytes
- sentence-transformers
- Ray
- DeepSpeed

などを検討。

ただし、最初から全部入れるのではなく、実際に使う方式を決めてから依存関係を入れる方がよい。

---

# 21. 7GPU利用時の重要事項

A5000 × 7 = 約168GB VRAMだが、

```text
24GB × 7
```

であり、

```text
168GBの単一GPU
```

として自動的に扱えるわけではない。

大型モデルでは、

- Tensor Parallelism
- Pipeline Parallelism
- model sharding
- Accelerate `device_map`
- DeepSpeed
- vLLM tensor parallel
- PyTorch Distributed

などによって複数GPUへモデルを分割する必要がある。

---

# 22. nvccについて

現在：

```text
nvcc: command not found
```

だが、これは今のところ問題なし。

PyTorch CUDAは正常に動いているため、

```bash
sudo apt install nvidia-cuda-toolkit
```

を今すぐ実行する必要はない。

むしろシステムCUDAを不用意に追加すると、現在正常なドライバ / PyTorch CUDA環境との依存関係が複雑になる可能性がある。

`nvcc` が必要になるのは例えば、

- CUDA C++を自分でコンパイル
- custom CUDA extension
- CUDA依存ライブラリのsource build
- 特定バージョンのFlashAttention等

を利用するとき。

その時点でCUDA Toolkitを慎重に導入する。

---

# 23. OSアップグレードについて

ログイン時、

```text
New release '24.04.4 LTS' available.
Run 'do-release-upgrade'
```

と表示される。

ただし、**現時点ではUbuntu 24.04へアップグレードしない。**

理由：

現在、

- NVIDIA Driver
- 7GPU
- PyTorch CUDA

がすべて正常動作している。

OSアップグレードによってGPUドライバやライブラリを壊すメリットがない。

Ubuntu 22.04のまま利用する。

---

# 24. サーバー操作上の注意

貸与元から、

```text
再起動はOK
シャットダウンはNG
```

と明示されている。

したがって、

```bash
sudo reboot
```

は必要時に可能だが、

```bash
sudo shutdown
sudo poweroff
shutdown -h now
```

などは実行しないこと。

また、

```bash
sudo apt autoremove
```

も現在は不用意に実行しない。

貸与環境なので、既存パッケージを必要以上に削除・更新しない方針。

---

# 25. セキュリティ上の注意

VPN PSK、VPNパスワード、サーバーパスワードはトラブルシューティング中に一度チャットへ記載している。

環境構築が安定した後、可能なら貸与元に、

- VPN PSK
- VPNユーザーパスワード
- サーバーユーザーパスワード

のローテーションが可能か相談する。

今後Claude等へ引き継ぐ際も、認証情報そのものはプロンプトに貼らず、

```text
「認証情報は発行済み」
```

として扱うこと。

---

# 26. 次にClaudeにやってほしいこと

現時点ではトラブルシューティングよりも、**実際の開発環境構築へ移行したい。**

次の優先順位で支援してほしい。

1. Windows 11 → VS Code Remote-SSH設定
2. `gpu-sv-002` をVS Codeから開く
3. Python interpreterを `~/venvs/gpu/bin/python` に固定
4. GitHub / Git環境を整える
5. Claude Codeをサーバー上で利用可能にする
6. Codexもサーバー上で利用可能にする
7. プロジェクト用ディレクトリ・リポジトリを配置
8. 必要なPython依存関係を導入
9. 7GPU環境でLLM / シミュレーションを動かす
10. 必要ならvLLM / Accelerate / Distributed環境へ進む

特に、**既に正常に動いているNVIDIA Driver / PyTorch / VPN周辺を不用意に変更しないこと。**

これ以降は「GPUを使えるようにする」段階ではなく、

**「この7GPU環境を実際の開発・推論・シミュレーションにどう使うか」**

の段階。