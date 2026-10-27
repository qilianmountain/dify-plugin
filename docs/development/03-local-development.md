# 本地开发环境与打包

更新日期：2026-10-27。本页承接原 `README.md` 中的开发说明。`README.md` 现在是对外产品文档，会随插件包发布；开发命令、测试环境和打包细节保留在这里，不进入 `.difypkg`。

## 环境

从本 Feature 的 `dify-plugin` worktree 执行：

```powershell
. ./scripts/use-local-environment.ps1
uv python install 3.12.13
uv sync --locked
uv run python --version
uv run python -m pytest -q
uv pip check
```

Python 固定 3.12.13，`dify-plugin==0.10.2` 及传递依赖锁在 `uv.lock`。脚本选择 `$env:USERPROFILE/.venvs/browseract-dify-v1`：worktree 内的虚拟环境在加载 jsonschema 资源时超过 Windows 路径上限。原环境保留，当前命令使用短路径。

`requirements.txt` 是锁定的运行时依赖（不含 pytest）。改动依赖后重新生成：

```powershell
uv export --locked --no-dev --no-emit-project --format requirements-txt --output-file requirements.txt
```

本机 uv 0.11.8 写可执行文件时失败过。恢复方式是先用 Python 原生模块建环境，再用 pip 补齐控制台脚本：

```powershell
$python312 = uv python find 3.12.13
& $python312 -m venv $env:UV_PROJECT_ENVIRONMENT
New-Item -ItemType Directory -Force .tools | Out-Null
uv export --locked --no-emit-project --format requirements-txt --output-file .tools/requirements-dev.txt
& "$env:UV_PROJECT_ENVIRONMENT/Scripts/python.exe" -m pip install --force-reinstall --require-hashes -r .tools/requirements-dev.txt
uv sync --locked
uv run python -m pytest -q
```

用 `python -m pytest` 保证测试用的是选定的解释器。测试关闭 pytest 的 AnyIO 自动插件，因为它在 SDK 应用 gevent 补丁前导入 SSL。SDK 0.10.2 会输出一条上游 Pydantic 弃用警告，未做屏蔽。

不先执行 `use-local-environment.ps1` 而直接 `uv run` 时，会用到 worktree 内的 `.venv`。该路径下 `jsonschema_specifications` 的 schema 资源超过 Windows MAX_PATH，表现为收集阶段 `FileNotFoundError`，7 个测试文件全部失败。看到这个错误先检查是否用了短路径环境，不要按依赖损坏排查。

## 官方 CLI

本地 CLI 是 `.tools/dify.exe` v0.6.11，来自 [官方发布](https://github.com/langgenius/dify-plugin-daemon/releases/tag/0.6.11)，不是 `difyctl`。该文件被 Git 忽略，也未加入全局 PATH。

```powershell
New-Item -ItemType Directory -Force .tools | Out-Null
Invoke-WebRequest https://github.com/langgenius/dify-plugin-daemon/releases/download/0.6.11/dify-plugin-windows-amd64.exe -OutFile .tools/dify.exe
$actualHash = (Get-FileHash .tools/dify.exe -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actualHash -ne '427136f982ca083bb3a7e1ca6f4b08d7d73e1f6f80c0c83576d90c3ae5ebc9c5') {
    throw 'CLI checksum mismatch'
}
& ./.tools/dify.exe version
```

## SDK 启动与打包

仅当本地没有 `.env` 时，从示例复制一份：

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
uv run --env-file .env python -m main
```

本地模式通过 stdio 输出注册信息和心跳，Ctrl+C 停止。`PYTHONUTF8=1` 在 Python 启动前加载，保证 Windows 控制台按 UTF-8 处理。本地模式不连接 Dify 服务端。

打包生产包：

```powershell
New-Item -ItemType Directory -Force dist | Out-Null
& ./.tools/dify.exe plugin package . -o dist/browseract-<version>-<sha>.difypkg
```

Test03 包由隔离脚本生成，会覆盖主机、插件身份、README 和 PRIVACY：

```powershell
uv run python scripts/package-test03.py --output dist/browseract-<version>-test03-local.difypkg
```

`.difyignore` 排除 demo、API 证据、测试、脚本、凭据、CLI、虚拟环境和 Git 元数据；TLS/包内清单见各次验证记录。

## 验证与交付记录

需求、任务和验证结果在 Feature 的 `development/` 下，不在本仓库包内。Marketplace 提交流程见 [02-marketplace-submission.md](02-marketplace-submission.md)。
