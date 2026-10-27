# Dify Marketplace 提交流程与预演

核实日期：2026-10-27。范围：从本地包到 Marketplace 上架的完整提交流程，以及 BrowserAct 插件当前还差什么。

本文依据当天抓取的官方文档、`langgenius/dify-plugins` 的 PR 模板与 CI 工作流、`dify-marketplace-toolkit` 的校验源码整理。官方要求会变，正式提交前按第 2 节重新核对一次。

## 1. 结论

- **不需要改代码，也不需要改 API 地址。** 源码默认就指向生产 `https://api.browseract.com`，Test03 才是打包脚本覆盖出来的。提审包 = 直接 `dify plugin package` 的产物。
- 真正要改的是**四份元数据**：`manifest.yaml` 补 `repo` 和 `contact`、重写英文 README、重写 PRIVACY、递增版本号。
- 有两条硬性门槛容易被忽略：**`repo` 只允许白名单主机的公开仓库**（公司 `git.ziniao.com` 不在名单内），**PR 正文必须是英文**。
- 当前包能通过体积、依赖、文件内容检查，但会在 `repo`、`contact` 两项上被 blocking 拦下。

## 2. 官方信息来源

| 内容 | 地址 |
| --- | --- |
| 官方发布文档 | <https://docs.dify.ai/en/develop-plugin/publishing/marketplace-listing/submit-plugin-to-marketplace> |
| 发布方式对比 | <https://docs.dify.ai/en/develop-plugin/publishing/marketplace-listing/release-overview> |
| 提交要求 | <https://github.com/langgenius/dify-plugins/blob/main/docs/plugin-submission-requirements.md> |
| PR 模板 | <https://github.com/langgenius/dify-plugins/blob/main/.github/pull_request_template.md> |
| 审核清单 | <https://github.com/langgenius/dify-plugins/blob/main/docs/plugin-review-guidelines.md> |
| 合并后上传工作流 | <https://github.com/langgenius/dify-plugins/blob/main/.github/workflows/upload-merged-plugin.yaml> |
| 本地校验工具 | <https://github.com/langgenius/dify-marketplace-toolkit> |

## 3. 三条分发路线

| | Marketplace | GitHub 仓库 | 本地文件 |
| --- | --- | --- | --- |
| 面对人群 | 全部 Dify 用户 | 拿到仓库地址的人 | 私下给文件的人 |
| 审核 | 自动检查 + 人工审核 | 无 | 无 |
| 版本方式 | 每个版本一个包 + 一个 PR | GitHub Release 附件 | 重新打包分发 |

我们走 Marketplace：首版目标就是公开上架。同一个 `.difypkg` 三种渠道通用，所以测试阶段发的 GitHub/本地包，不会影响后续提交。

## 4. 提审前置条件

1. 插件已在**当前版本**的 Dify Community Edition 或 Dify Cloud 上跑通。
2. 有一台能运行 Dify Plugin CLI 的机器（我们已固定 `.tools/dify.exe` v0.6.11）。
3. 有 Python 3 和 [`yq`](https://github.com/mikefarah/yq) 用于本地校验。
4. **有一个公开可访问的源码仓库**，且主机在白名单内。

### 源码仓库主机白名单

校验器只接受这些主机（`toolkit/checks/source_hosts.py`）：

```text
github.com, gitlab.com, bitbucket.org, gitee.com, codeberg.org, git.sr.ht,
gitlab.anchnet.com   # 厂商自建实例，逐个审核加入
```

`git.ziniao.com` 不在名单内。要用公司地址，需先向 `dify-marketplace-toolkit` 提 PR 把主机加进去；否则只能用 GitHub 或 gitlab.com 的公开仓库。

## 5. 包内硬性要求

### 5.1 manifest.yaml

校验器要求的字段（缺任一项即 blocking），依据 `toolkit/checks/manifest.py`：

| 字段 | 说明 |
| --- | --- |
| `author` | 不能包含 `dify` 或 `langgenius` |
| `name` / `version` / `type` | `type` 必须是 `plugin` |
| `icon` | 图标文件路径 |
| `plugins` | 工具/模型等注册入口 |
| `privacy` | 包内文件路径或 https URL；引用包内文件时该文件必须存在 |
| **`repo`** | **整个值必须是一个白名单主机的 https URL** |
| **`contact`** | **必须是合法邮箱** |
| `label.en_US` / `description.en_US` | 英文名称与说明 |
| `meta.version` / `meta.arch` / `meta.runner.*` | 运行环境声明 |
| `meta.minimum_dify_version` | 推荐项，缺失只警告 |

另建议声明出站域名，让扫描器能看见运行时拼出来的地址：

```yaml
network:
  domains:
    - api.browseract.com
```

### 5.2 README.md

- 必须是英文正文，**代码块以外的中文字符会让检查直接失败**；中文放 `readme/README_zh_Hans.md`。
- 必须出现源码仓库链接（白名单主机）。
- 必须覆盖：安装/配置、用法、需要的 API 或凭据、连接要求。这四项只做关键词检查，缺了是警告，但审核会问。

### 5.3 PRIVACY.md

- 包里必须存在，且 `manifest.yaml` 的 `privacy` 指向它。
- 写清收集、存储、日志、第三方传输；不收集也要明确写出来。
- 不能留下模板占位文本（会直接判失败）。

### 5.4 依赖

- Python 插件要求 `dify-plugin >= 0.9.0`；带 git、直接 URL 安装会被 blocking。
- 依赖必须有版本约束；只有下界是警告。
- `uv export` 默认会写 `--hash=sha256:...` 续行，校验器把每一行当成"无版本约束的依赖"，一次报出几百条 blocking。导出时加 `--no-hashes`。
- 体积上限 50 MB、文件数上限 5000；`.git`、`.venv`、`__pycache__`、`.env`（`.env.example` 除外）、`.pem`、`.key`、`.log` 等会被拦。

### 5.5 风险等级

浏览器自动化属于 **High risk**，没有降级空间。选了低等级不会缩小审核范围，只会增加返工。

## 6. 本地构建与校验

在插件根目录执行（PowerShell）：

```powershell
.\.tools\dify.exe plugin package . -o dist\browseract-<version>-<sha>.difypkg
```

校验器在独立目录跑，不要放进插件仓库：

```powershell
git clone https://github.com/langgenius/dify-marketplace-toolkit.git C:\tools\dify-marketplace-toolkit
cd C:\tools\dify-marketplace-toolkit
python validator\validate-difypkg.py <包路径> --output-dir <报告目录>
```

带 PR 正文一起跑，可以检查敏感能力披露是否与 PR 一致：

```powershell
python validator\validate-difypkg.py <包路径> --pr-body-file <pr-body.md> --output-dir <报告目录>
```

结果：退出码 0 表示无 blocking，1 表示有阻塞项或环境问题。报告在 `summary.md`、`*.errors.txt`、`*.warnings.txt`。只有依赖漏洞查询需要联网，可加 `--offline`，但那样不会给出"无漏洞"的结论。

本地校验**不覆盖**：PR 标题/正文语言、模板完整性、版本是否已发布、GitHub 审核、安装测试。这些只能在 PR 上验证。

2026-10-27 已在本机跑通一次完整校验（Windows + yq v4.54.1 + toolkit `57a21d1`）：

```text
Blocking failures: 0
Warning categories: 6
sensitive_capabilities: PASS
```

报告和当时使用的 PR 正文在 [validation/2026-10-27/](validation/2026-10-27/summary.md)。6 类警告都不是阻塞项：文件带可执行权限位（Windows 打包产物）、缺少 `meta.minimum_dify_version`、`tiktoken` 关键词误报、`python_safety` 对 `option_cache.get(api_key, ...)` 的启发式提示、出站域名提示、依赖漏洞（无已知漏洞）。

这些警告在 PR 上可能被审核追问，建议在 Reviewer notes 里主动说明。

## 7. 提交步骤

一个 PR 只放一个 `.difypkg`，路径固定为：

```text
<author>/<plugin-name>/<plugin-package>.difypkg
```

```bash
git clone https://github.com/<your-github-name>/dify-plugins.git
cd dify-plugins
git remote add upstream https://github.com/langgenius/dify-plugins.git
git fetch upstream
git switch main
git merge --ff-only upstream/main

git switch -c add-browseract-<version>
mkdir -p <author>/browseract
cp /path/to/browseract-<version>.difypkg <author>/browseract/

git status --short          # 确认只多了一个 .difypkg
git add <author>/browseract/browseract-<version>.difypkg
git commit -m "add browseract <version>"
git push -u origin HEAD
```

然后从自己的 fork 向上游 `main` 开 PR。包和描述都准备好了再退出 draft，因为开 PR、推送、转为可审核都会触发自动检查。

版本更新时：递增 `manifest.yaml` 的 `version`，重新打包，**只在原目录新增新包**，旧包保留。版本号必须大于同目录里已有的版本。

## 8. PR 正文要求

机器人会解析 PR 正文，以下缺一项就报错（`toolkit/checks/pr/body.py`）：

- `## Plugin information` 下 5 个字段都要有值：Author、Plugin name、Version、Source repository（含 http(s) URL）、Contact。
- `## Submission type` 勾选恰好一个：New plugin / Version update。
- `## Risk level` 勾选恰好一个。
- `## What changed` 和 `## Local validation` 不能为空（模板注释不算内容）。
- **正文里的中文字符会触发失败**（代码块内容除外）。

模板不要删字段、不要换成自由描述。可直接用的骨架：

```markdown
## Plugin information

- **Author**: browser-act
- **Plugin name**: browseract
- **Version**: 1.0.0
- **Source repository**: https://github.com/browser-act/dify-browser-act-plugin
- **Contact**: service@browseract.com

## Submission type

- [x] New plugin
- [ ] Version update

## What changed

Initial release. Adds two tools, Run My Bot and Run Official Template, that start
a BrowserAct task and wait for its result inside the node.

## Risk level

- [ ] Low risk
- [ ] Medium risk
- [x] High risk

## Required checks

- [x] I have read and followed the Marketplace submission requirements.
- [x] I have read and comply with the Plugin Development Guidelines.
- [x] I tested this plugin on Dify Cloud; limitations are listed in Reviewer notes.
- [x] The package contains only files needed at runtime.
- [x] The package does not contain secrets or development artifacts.
- [x] The package does not contain executables or bundled binaries.
- [x] The README includes setup, usage, credentials, connection requirements and the source repository.
- [x] The plugin includes PRIVACY.md and manifest.yaml references it.
- [x] All user-facing text is in English.

## Security and privacy notes

Browser automation: the plugin sends the user's BrowserAct API Key to
api.browseract.com and starts a Bot that runs in BrowserAct's hosted service.
Task inputs and outputs pass through that service. The plugin does not accept a
custom host, does not follow redirects, and redacts the API Key from errors.

## Local validation

    python validator/validate-difypkg.py browseract-1.0.0.difypkg --output-dir report
    exit code 0, 0 blocking errors

## Reviewer notes

Tested on Dify Cloud with both tools. Node wait timeout is 600
seconds by default; on timeout the node fails but the remote task keeps running.
```

## 9. 自动检查与人工审核

| 结果 | 处理 |
| --- | --- |
| 通过 | 等维护者审核；通过检查不等于批准 |
| blocking error | 修包或修 PR，重新构建，更新同一个 PR，不要另开新 PR |
| 警告 | 判断是否真实问题；属于有意行为就在 Reviewer notes 说明 |
| 要求修改 | 改源码、重新打包、推到同一 PR 并回复 |

仓库 CI 在合并前会再跑一遍包内容、密钥、二进制、manifest、README、依赖检查；人工审核按 `plugin-review-guidelines.md` 看文档、隐私、依赖和敏感能力。

## 10. 合并之后

合并到 `main` 后由 `upload-merged-plugin` 工作流自动执行：

1. 校验变更路径（一次只能有一个 `.difypkg`）。
2. 解包并重跑内容、密钥、二进制、manifest、README、依赖检查。
3. 从 PR 正文提取 release notes。
4. 上传到生产 Marketplace，再镜像到 staging（失败不阻塞生产）。

不需要我们手动上传。

之后在 [Creator Center](https://creators.dify.ai/) 关联发布用的 GitHub 账号查看下载量、评分、反馈。团队插件用组织身份发布时，可在 Creator Center 用 Plugin ID 前缀创建组织，或对已发布插件发起 Claim。

## 11. 本项目现状（2026-10-27 改造后）

这一轮已经把材料改成提审形态，源码行为没有改动。

| 项目 | 改造前 | 现在 |
| --- | --- | --- |
| `manifest.author` | `qilian_mountain` | `browser-act`（GitHub 组织，4 个文件同步） |
| `manifest.repo` | 缺失（blocking） | `https://github.com/browser-act/dify-browser-act-plugin`（仓库已创建，尚未推送） |
| `manifest.contact` | 缺失（blocking） | `service@browseract.com` |
| `manifest.network.domains` | 无 | `api.browseract.com` |
| `README.md` | 开发记录，12 处 Test03，无本插件源码链接 | 产品文档，Test03 为 0，含源码链接和安装/用法/凭据/连接说明 |
| `PRIVACY.md` | 0.0.8 "local test candidate"，6 处 Test03 | 生产链路，Test03 为 0，含 BrowserAct 隐私政策链接 |
| `requirements.txt` | `uv export` 带 `--hash`，285 条 blocking | `--no-hashes`，120 行，全部 `==` 固定 |
| `LICENSE` | 无 | MIT（2026 BrowserAct） |
| 开发命令 | 在 README 里 | 移到 [03-local-development.md](03-local-development.md) |

当前候选包：`dist/browseract-1.0.0-7ce5620.difypkg`，53,343 字节、26 文件，SHA256 `e8b053910cecd35ba190ebb36344c3c455bf483b7aebfa59f5307ed4e7f47287`。

官方校验器结果：**0 blocking**，`sensitive_capabilities` PASS，6 类警告（详见 [报告](validation/2026-10-27/summary.md)）。

身份、邮箱、许可证和版本已确定。公开仓库已创建但还没有提交；开 PR 未做。仓库里推哪些文件仍需确认，因为本地分支带着内部调研证据和演示代码。

## 12. 从测试到提审的切换清单

前提：测试通过，且工作区干净（`browseract/tool.py` 仍有一处未提交改动，提交或还原后才能作为发布基线）。

| # | 动作 | 状态 |
| --- | --- | --- |
| 1 | 确认发布者身份：`author` 用个人还是组织，联系方式邮箱 | 已完成：`browser-act` / `service@browseract.com` |
| 2 | 创建公开源码仓库（白名单主机），推 `feature/browseract-dify-v1` | 待做（唯一阻塞项） |
| 3 | `manifest.yaml` 加 `repo`、`contact`、`network.domains` | 已完成 |
| 4 | 重写 README 为产品文档 | 已完成 |
| 5 | 重写 PRIVACY 为生产链路 | 已完成 |
| 6 | 版本号改为 1.0.0，同步 `pyproject.toml` 和 `uv.lock` | 已完成 |
| 7 | 重新打包，跑官方 validator 到 0 blocking | 已完成（1.0.0 包） |
| 8 | 写 PR 正文（英文），带 `--pr-body-file` 再校验 | 已完成，草稿见 [pr-body.md](validation/2026-10-27/pr-body.md) |
| 9 | fork `dify-plugins`，建分支，放入 `<author>/browseract/` | 待授权（依赖 2） |
| 10 | 开 PR，处理 CI 与审核意见 | 待授权（依赖 9） |

第 9、10 项是唯一会对外产生记录的动作，等你确认后再做。

## 13. 实测：提交物与命名（2026-10-27）

对已合并仓库和合并 PR 的抽查结果，用来消除两处歧义。

**合并后的目录里只有包，没有源码。** 抽查 `BrightData/brightdata-dify-plugin`（只有 `brightdata_plugin.difypkg`）、`0000F8/salt`（只有 `salt-0.1.2.difypkg`）。`dify-plugins` 仓库 README 里「把源码和包一起放进去」的说法已经过时，以官方 Publish 文档和实际目录为准。

**组织可以作 author，PR 可以由成员个人账号提交。** PR #3519 由个人账号 `adityabatra072` 提交，PR 的 Author 字段是 `runanywhereai`，文件路径是 `runanywhereai/wally/wally-0.0.4.difypkg`，源码仓库是 `RunanywhereAI/wally-dify-plugin`。所以 `<author>` 填组织 handle、PR 用有权限的成员账号开，是被接受的。

**源码仓库命名没有官方规范。** 同期合并的 PR 里同时存在这些写法：

| 写法 | 例子 |
| --- | --- |
| `<vendor>-dify-plugin` | `call-e-dify-plugin`、`wally-dify-plugin`、`turan-dify-plugin`、`brightdata-dify-plugin` |
| `dify-plugin-<vendor>` | `dify-plugin-site-shot`、`dify-plugin-tidytools`、`dify-plugin-gisoo` |
| `dify-<vendor>-<product>` | `dify-line-message-sender`、`dify-qveris-mcp` |

命名只要满足三点：公开、主机在白名单、README 与 manifest 里的地址一致。BrowserAct 现有仓库是 `codex-browser-act-plugin`、`cursor-browser-act-plugin` 这种 `<平台>-browser-act-plugin`，按同样的习惯可以叫 `dify-browser-act-plugin`。

## 14. 待确认

- 公开源码仓库是否就用 `browser-act/dify-browser-act-plugin` 这个名字。建好并公开后才能提交；改名必须重新打包，否则包里的 `repo` 和 README 链接会失效。
- 仓库里推哪些内容：整条 `feature/browseract-dify-v1` 分支，还是只推插件目录加必要文档。
- 生产服务端 Dify 渠道（24 + 心跳）的部署时间；审核方会用生产 API 试跑，渠道未上线会直接影响体验。
- `meta.minimum_dify_version` 保持不填；如果以后使用了特定 Dify 版本才有的能力，再按实际最低版本补充。
