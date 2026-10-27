# 01：BrowserAct 插件的 Dify Marketplace 提交路线

核实日期：2026-10-16。
状态：第一步调研结论与提交路线建议，供确认；尚未提交插件。

2026-10-27 更新：完整的现行提交流程、校验规则和本项目差距见 [02：Dify Marketplace 提交流程与预演](../development/02-marketplace-submission.md)。本文的路线结论仍然成立，具体字段与命令以新文档为准。

本文只确定插件提交渠道、材料和审核步骤，不确定工具范围、参数设计或任务等待策略。后续完整设计按 `agent.md` 引用的 team-infra 流程组织；本文不是完整技术方案或实施计划。

## 结论

采用第三方 Tool 插件的 Marketplace 提交流程：在我们自己的公开源码仓库维护 BrowserAct 插件，构建 `.difypkg`，通过我们 Fork 的 `langgenius/dify-plugins` 向上游 `main` 提交 PR。审核通过并合并后，由 Dify 官方工作流再次校验并上传 Marketplace。[S1][S2][S4]

`dify-official-plugins` 用于参考 Firecrawl、Tavily 的代码组织，不作为本项目默认提交目标。自己维护源码、提交插件包即可走公开的上架流程，无需预先成为官方插件仓库的一部分。[S1]

## 三类仓库的职责

| 仓库 | 职责 | 本项目如何使用 |
| --- | --- | --- |
| 我们的 `dify-plugin` | 维护源码、测试、文档和版本 | 开发仓库；正式提交前必须有可公开访问的源码地址 |
| `langgenius/dify-official-plugins` | Dify 官方维护的插件源码集合 | 格式和实现参考 |
| `langgenius/dify-plugins` | Marketplace 提交及发布仓库 | 在 Fork 中增加插件包，再向上游提 PR |

公开范围是插件适配源码；BrowserAct 服务端仍由 API 提供能力，不要求因此公开全部服务端实现。公开源码仓库应准确对应待提交的包，不能只填写组织主页。[S1]

## 提交路径与产物

Marketplace 仓库中的目标路径：

```text
<author>/<plugin-name>/<plugin-package>.difypkg
```

其中 `author`、插件名称、版本必须与包内元数据和 PR 一致。发布者标识、正式插件名称、公开源码 URL 和联系渠道仍需我们确认；目前不把 `browser-act`、`browseract-ai` 或 `langgenius` 中任何一个擅自写成发布身份。

提交步骤：

1. 完成开发和真实 Dify 联调，记录环境、版本、用例与结果。
2. 准备公开源码、英文说明、隐私声明、图标和准确的 manifest。
3. 用 Dify CLI 打包，运行 Marketplace Toolkit 本地校验。
4. Fork `langgenius/dify-plugins`，在独立分支中按上述路径添加包；每个 PR 只提交一个 `.difypkg`。
5. 向上游 `main` 提 PR，完整填写当时的提交模板。
6. 修复自动检查和人工审核提出的问题，继续更新同一 PR。
7. 合并后关注官方发布工作流与实际商店页面；合并、上传成功和商店可安装是分别要核实的状态。[S1][S2][S4]

本次未执行 Fork、创建远程仓库、打包、校验、提交或上架。

## 需要准备的材料

| 材料 | 官方要求及本项目落点 |
| --- | --- |
| 公开源码 | 提供可检查、与发布包对应的插件源码仓库 |
| `manifest.yaml` | author、name、version、runner、插件类型、图标及隐私引用准确 |
| 英文 `README.md` | 安装、认证、必需账号/API、网络连接要求、用法、源码和维护联系方式 |
| 用户可见文本 | 名称、说明、参数标签、帮助和错误信息以英文为主，可补中文翻译 |
| 隐私政策 | `PRIVACY.md` 或托管页面，并由 manifest 引用；说明实际收集、存储、日志、传输和第三方数据流 |
| 运行包 | 只包含必要运行文件、依赖和文档资产；排除 `.git`、`.env`、凭据、缓存、日志和开发环境 |
| 验证记录 | 实际 Dify 环境与测试结果，以及本地包校验命令和结果 |

来源：[S1][S2][S3][S5][S6]。PR 模板要求确认在 Community Edition 和 Cloud 测试，或明确说明限制；未测试的项目不能直接勾选通过。[S2]

打包与校验的命令形式如下，路径是占位示例，尚未执行：

```text
dify plugin package ./<plugin-project>

python3 validator/validate-difypkg.py /path/to/plugin.difypkg --output-dir ./validation-report --pr-body-file /path/to/pr-body.md
```

第二条在 `langgenius/dify-marketplace-toolkit` 中执行。官方文档当前要求 Python 插件使用 `dify-plugin >= 0.9.0`；实际实现时重新核对 SDK 兼容性和依赖规则。本地校验通过仅代表无阻塞的包级错误，不保证人工审核通过。[S1]

## BrowserAct 的审核披露

按当前规则，BrowserAct 提供浏览器自动化能力，提交时应选 `High risk`，说明插件调用 BrowserAct 托管服务执行 Bot 的实际边界。固定 API 域名不能用于隐去服务端浏览器自动化能力。[S1][S3]

随实际实现说明：输入限制、执行所在服务、数据去向、凭据用途、HTTP 与总等待超时、错误及日志如何处理敏感信息。涉及结果文件获取、用户 URL、代理或回调时如实披露；尚未纳入首版的能力不写成已经支持。[S1][S3]

隐私声明必须覆盖 BrowserAct 服务实际收到和处理的数据，不能因为插件适配层不持久化，就声明整个链路不收集或传输用户数据。[S6]

## PR 内容及版本更新

当前模板包含：插件身份、源码与联系方式、新插件/版本更新、改动说明、单选风险等级、必需检查、数据与敏感能力说明、本地校验和审核补充信息。PR 标题、正文和主 README 使用英文。[S1][S2]

新版本应递增 `manifest.yaml` 的版本，重新构建并提交一个新包，通常仅新增该 `.difypkg`，保留旧版本包；兼容性变化写入说明。后续是否自动创建发布 PR，另行设计，不属于本步骤。[S1][S3]

## 官方资料存在的表述差异

本次核实的仓库 README 的 Publishing 第 3 步仍写着将源码和包放入提交目录。[S7] 但专门的发布文档明确 Marketplace 接收 `.difypkg`，通过独立公开仓库检查源码；发布工作流也从包解压、校验再上传。[S1][S4]

因此本项目采用“源码保留在自己的公开仓库，提交 PR 只增加一个包”的路线。正式提交前再次读取实时模板、要求与 CI；如维护者提出不同要求，记录具体差异后调整，不推断两种说法完全一致。

## 证据来源

提交仓库本次核实的 `main` 为 `1fa39d40abd48e584204b96fcc966cb36ec16e21`；下方仓库文件链接固定到该提交。文档页面与外部校验工具会变化，发布前需重查。此次为资料核实，未实际执行 CI 或验证器。

- [S1：官方 Marketplace 发布文档](https://docs.dify.ai/en/develop-plugin/publishing/marketplace-listing/submit-plugin-to-marketplace)
- [S2：提交仓库 PR 模板](https://github.com/langgenius/dify-plugins/blob/1fa39d40abd48e584204b96fcc966cb36ec16e21/.github/pull_request_template.md)
- [S3：提交仓库要求](https://github.com/langgenius/dify-plugins/blob/1fa39d40abd48e584204b96fcc966cb36ec16e21/docs/plugin-submission-requirements.md)
- [S4：合并后发布工作流](https://github.com/langgenius/dify-plugins/blob/1fa39d40abd48e584204b96fcc966cb36ec16e21/.github/workflows/upload-merged-plugin.yaml)
- [S5：官方插件开发准则](https://docs.dify.ai/en/develop-plugin/publishing/standards/contributor-covenant-code-of-conduct)
- [S6：官方隐私准则](https://docs.dify.ai/en/develop-plugin/publishing/standards/privacy-protection-guidelines)
- [S7：提交仓库 README](https://github.com/langgenius/dify-plugins/blob/1fa39d40abd48e584204b96fcc966cb36ec16e21/README.md)

## 下一步

先确认本提交路线，再确认发布者标识、公开源码仓库和维护联系渠道。工具范围与执行方式随后分别讨论，避免本步骤提前决定功能设计。
