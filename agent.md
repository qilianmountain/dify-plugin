# BrowserAct Dify 插件：项目上下文与证据入口

2026-10-22 排障增量（20票/0.0.8）：Test03包独立使用 `qilian_mountain/browseract_test03`、Provider `browseract_test03`，源码生产身份保留browseract。新测试包不更新旧身份或迁移旧节点，用户需新增测试节点并配置连接。同一test03 Key及旧包解出客户端的认证/列表真实GET已通过；Cloud动态下拉仍401，官方代码存在独立的Provider凭据缓存路径，与现象吻合但未直接读取Cloud缓存。详情见Feature20票及排障报告。

2026-10-22 最新增量（13/17票、0.0.7）：两个工具的 Operation 按 Run Bot、View Parameters 排列，默认 run、显式 view 及 JSON 复制解析行为保持不变。共享客户端所有请求统一携带 `api-channel-ak: difyak`，Bearer Key 不变。轮询维持心跳，超时/异常停止查询、不主动取消；服务端可能因心跳过期取消。源码保留生产 API 主机，`scripts/package-test03.py` 在隔离打包时固定 `https://api-test03.browseract.com` 并标注 BrowserAct (Test03)，不增加用户环境配置项。最新验证与包见 Feature 17 票；以下旧版本决定保留历史语义。

2026-10-21最新决定（12票/0.0.6）：两个工具默认Run Bot，显式View Parameters仍只查询；移除模板Proxy Region字段、地区请求与校验，创建请求不传顶层proxy_region；自定义参数JSON灰字说明改为查询参数及官方集成指引链接。此前默认view、模板US必填的内容属于旧版本决定，已被本次用户指令替代。详情与验证以Feature入口的12票为准。

2026-10-21展示位置修正（11票/0.0.5）：两工具完整指引从Operation移至Custom Parameters JSON灰字说明，保留Operation、Bot/Template的简短悬停提示；本机演示同步原生字段展示规则，不改变任务和输出行为。

2026-10-21增量：实施待改项10，0.0.4统一插件自有英文文案与确认后的参数指引；Operation明确从LAST RUN复制完整输出。两套语言声明均使用英文，错误提示和演示同步；原始API数据及服务端消息不翻译。执行流程、默认值及输出契约不变，交付与验证以Feature入口为准。

2026-10-20增量：用户确认运行结果对齐Make字段，随后要求一并实施此前待改项。0.0.3保留run的17个命名变量、文件字段树及原完整json，view复制不变；两个工具operation改为首个form: llm输入并默认view；动态列表成功结果进程内固定复用60秒，按Key摘要、SDK user_id和来源隔离、最多128组，不缓存定义或运行前校验。具体07/08/09状态与交付以Feature入口为准，Cloud新包顺序和旧节点模式迁移另行验证。

当前开发入口：[Feature README](../../development/README.md)、[仓库/基线/分支](../../development/repos.yaml)。本checkout在 `feature/browseract-dify-v1`，固定基线 `92c83d4d2b4f1179258bd80e4be7fa7a1738d008`。01–04本地实现及05当前Cloud远程调试验证已完成：两工具查看、完整输出复制/修改/粘贴、真实运行及下游结果通过；三个dynamic-select为form: llm，既有149项检查通过。本轮新增600.000秒超时、610.593秒完成，Cloud整条流程历史SUCCESS611.524秒；真实短超时不取消远端任务，8档输出完整性与临时链接通过。单步约100秒请求超时、实时流network error和后台继续执行须分别判断，证据见[05边界报告](../../development/verification/2026-10-20-dify-cloud-boundaries.md)。已安装包和绝对平台上限未验证；06打包与审查最新结果以Feature入口为准，未推送或发布。

核实日期：2026-10-15。本文记录已确认的仓库分工、开发流程入口和参考证据；不代替产品范围、技术方案或 API 契约。

2026-10-19 API 实测补充：[Bot 与官方模板真实返回](docs/research/evidence/2026-10-19-bot-api/README.md)。只读认证查询确认账号下共 2 个已发布 Bot、官方模板列表共 408 个；读取了两个 Bot 和 6 个模板详情，全部 HTTP 200。样本可取得输入默认值，但部分模板缺少参数说明。保留完整响应及派生默认参数 JSON；未启动任务、未实现 Dify 插件界面，也未保存 API Key。

统一评审入口：[BrowserAct Dify 插件首版设计方案 v0.8](docs/design/04-review-design.md)（2026-10-19；用户确认功能设计文档完成，进入 Feature 启动准备）。用户确认一个 BrowserAct 插件提供“运行我的 Bot”和“运行官方模板”两个工具，各自保留节点内“查看参数 / 运行 Bot”和 JSON 输入，新建节点均默认“查看参数”，用户手动切到运行模式；R1 按此收敛，替代单工具来源字段及合并列表候选。R2 已确认：超时只结束节点等待，不取消远端任务，节点报告超时并保留 `task_id`；R3 已确认对齐自家 n8n/Zapier：返回 API 任务详情 JSON，保留原字段及文件链接，不按字段白名单裁剪，首版不下载转存为 Dify `files`；R2 与暂停处理不因此改变。用户已确定模板运行时必须选择有效代理地区、默认美国且不可留空；查看参数不要求地区。等待超时默认 600 秒，平台兼容性仍待验证。Feature 与分支方案已初始化；2026-10-20 用户确认拆分，01环境及02只读认证/动态列表已完成本地验证，查看参数和运行按后续票据推进。

结果输出源码对照：[05：各平台结果与文件输出](docs/research/05-result-and-file-outputs.md)，记录 BrowserAct n8n/Zapier 与 Firecrawl/Tavily Dify 插件的实际返回方式和图片文件例外。

后续调研入口：[01：Marketplace 提交路线](docs/research/01-marketplace-submission.md)（2026-10-16；提交路线建议，待确认）。

等待机制证据：[03：Firecrawl 与 Apify 的任务等待](docs/research/03-task-waiting.md)，核实插件与 SDK 的内部查询、终态和超时边界。

产品范围：首版同时支持“我的已发布 Bot”和“官方模板”（用户已确认）。参数能力见 [02：Bot 选择与动态输入参数](docs/research/02-bot-input-parameters.md)；动态下拉与选中 Bot 后动态生成字段不能混同，尚未进行 Dify 界面联调。

当前设计决定统一记录在 [首版工具范围与输入方式](docs/design/01-tools-and-input.md)：首版按来源拆为“运行我的 Bot”和“运行官方模板”，共用 Provider 凭据和内部适配逻辑。每个工具固定调用各自列表、详情和启动接口，不再依赖来源字段联动。运行模式同步等待，移除等待开关、仅提交模式及独立查询/取消等任务管理工具。通用参数独立填写，业务输入使用 JSON：读取默认值，与用户参数对象逐层合并；数组整体替换、显式用户值优先，校验后启动，内部轮询后返回结果。

暂停处理已确认：内部轮询查询到 `pausing/paused` 时立即结束等待，节点以失败报告当前状态并保留 `task_id`；不继续等到超时，不自动恢复或取消远端任务，也不将其状态改写为 `failed`。该决定不代表正式插件已完成联调。

2026-10-19 已确认补充：两个来源工具都在各自节点提供“查看参数 / 运行 Bot”。查看模式只读取 `input_schema`，仅返回可复制修改的参数值对象，不输出说明、Schema、Bot 信息或额外业务包装；通过标准 JSON 消息位于 `json[0]`。用户点击“复制全部输出”后整体粘贴到自定义参数 JSON，修改其中 `json[0]` 后切回运行模式；插件提取该对象，忽略外层 `text`、`files`；不自动写回本节点配置，正式 Dify 联调尚未完成。

最新查看输出决定：设计 v0.8 只返回参数值对象，正常 `text` 为空、`files=[]`；原生 `text/json/files` 外层和整体复制行为仍保留。只提取明确默认值，保留大小写及类型；无默认值不伪造占位，运行时校验必填，缺少 Schema 时返回错误。本机演示已同步两个入口与裸配置输出，并移除静态样本：实际 Python 工具类分别加载列表与定义，共享 API 客户端、参数处理和轮询。它是本机服务，尚未接入 Dify SDK，当前要求以 v0.8 文档为准。最新复制决策：完整 Dify 输出直接粘贴，运行前提取唯一的 `json[0]`；包装不合法时不启动任务，保留纯参数对象和 `{}` 输入。

2026-10-19 本机 API 演示补充：[实时演示说明](docs/demo/live/README.md)。用户授权将查看参数及运行请求接到真实 API；新增独立本机演示，原对话内嵌页面仍是静态样本。个人 Bot 与官方模板详情的实时读取、原生格式输出和复制均已浏览器验证；运行请求与状态轮询已接入演示代码，但本轮没有真实启动任务。该演示不改变正式设计的待评审项，也不代表 Dify Cloud 插件联调完成。

演示 UI 边界修正：API Key 输入及“加载演示列表”按钮仅存在于模拟窗口外的“本机演示连接设置 · 非 Dify 控件”，不作为正式节点能力或字段。实际凭据由 Dify Provider 授权管理。

最新演示同步：本机服务已实现参数对象逐层合并（数组整体替换）、前后端默认 600 秒等待、模板运行时代理必填且从真实列表默认美国，查看模式仍忽略运行参数。20 项离线验证通过；没有因此完成正式 Dify SDK 或 Cloud 联调。

当前阶段：01–04本地验证及05当前Cloud远程调试验证完成；06打包、固定范围审查和本地交付的进展以Feature README为准。600秒默认值未改；当前后台长等待成功不等于单步/实时界面或已安装包无限兼容。历史调研段落记录当时阶段，不替代本页顶部最新结论。

最新推进范围：两个工具各自提供参数查看与同步运行，来源由工具身份确定。草案见 [接口选型与内部编排](docs/design/02-api-orchestration.md)，合计仍为 9 个 V3 接口；查看模式复用各自详情接口，两类任务共用状态和结果接口。接口已完成部分只读实测，草案仍待整体评审，未执行真实任务。

输入参数与选择方式见 [输入参数](docs/design/03-run-inputs.md)：运行我的 Bot 的逻辑输入为模式、Bot、等待超时、业务 JSON；运行官方模板另有代理地区。两者共用连接，不再声明来源字段。Bot/模板列表各自处理分页，关键词搜索暂不作为首版要求；目标 Dify Cloud 的实际控件效果仍需联调。

动态字段最新核对：Dify `main` 提交 `f3d7a49927da129f75c52a55392aad79a613e993` 与 SDK `a91e6b4a7d83b43746a70e86267796744f96d06b` 中，没有找到按当前所选 Bot 刷新业务字段或在执行后将输出写回 JSON 配置的标准机制。动态下拉只返回选项；两来源现由各自 Tool 固定，代理地区仅在模板工具声明，不再依赖条件显示。单步运行处理链只保存结果和刷新变量/状态，证据见 [调用链与执行后回填边界](docs/research/02-bot-input-parameters.md)。

本地开发方式已确认：先完成本地开发和测试，不依赖远程仓库；个人 GitHub 可作为后续发布位置，具体账号、仓库和可见性未选定。本地启动方案见 [Feature 启动准备](docs/development/01-feature-start.md)，根 [AGENTS.md](AGENTS.md) 提供正式阅读入口。初始提交、Feature 与工作分支已创建；实际 SHA 与进展见 Feature 入口。

## 项目目标与当前范围

- `dify-plugin` 是 BrowserAct Dify 插件的开发仓库，目标是在 Dify Marketplace 上线 BrowserAct 服务。
- 开发核心流程采用 `team-infra`；插件的格式和平台集成方式参考 `dify-official-plugins`。
- BrowserAct 在 n8n 和 Zapier 上的集成用于参考已有产品能力范围与用户操作流程；Dify 首版范围仍需单独确认，不默认复制全部接口或平台行为。
- 功能设计、Feature及01–04本地实现、05当前Cloud远程调试验证已完成，正式SDK链路与演示分离；06审查与本地交付状态见Feature入口；已安装包行为及上架尚未验证。未创建远程或推送。

## 权威来源与使用边界

| 内容 | 权威入口 | 使用方式 |
| --- | --- | --- |
| 团队开发与协作流程 | `team-infra/AGENTS.md`、`README.md` | 按入口加载相关流程，不在本仓库复制一套团队规则 |
| 本项目需求、实现与验证 | `dify-plugin` 及后续关联的 Feature 文档 | 首版范围、实现结果和验收结论必须在本项目明确 |
| Dify 插件结构和平台适配 | `dify-official-plugins` 中 Firecrawl、Tavily | 参考真实源码；历史实现不自动等于最新上架要求 |
| BrowserAct 已有跨平台集成 | `n8n-nodes-browseract`、`zapier` | 参考功能范围、参数处理、任务等待和结果返回；核对 API 版本及平台差异 |
| BrowserAct 对外 API 契约 | 官方 V3 Bot API 文档与 OpenAPI | 请求、返回值、状态和限制以当前契约为准，不根据旧集成推断 |

下列本地路径仅是本机已核实的位置，不要求其他开发者使用相同目录。源码结论绑定所列提交及核实日期；后续使用前检查实际分支、提交和工作区。

## team-infra：开发流程入口

- 远程仓库：`git@git.ziniao.com:a59-agentbase/common/team-infra.git`
- 本地路径：`C:/Users/Administrator/Documents/Codex/2026-09-20/git-git-ziniao-com-a59-agentbase-2/work/team-infra`
- 本次查看时的 HEAD：`8f9467d32e7bafcda7b40ce9bfe5f0803a5dbc2a`；未核实是否与远端最新版本一致。
- 优先阅读：`AGENTS.md`、`README.md`。
- 仓库注册入口：`foundations/repositories.yaml`。
- Feature 启动与收尾入口：`skills/feature-start/SKILL.md`、`skills/feature-archive/SKILL.md`。实际启动或归档时再完整读取并执行对应流程。
- 按任务需要读取 `docs/agents/learning.md`、已有的 `docs/agents/lession.md` 和 Feature 局部经验。

团队流程将 Feature 协作资料组织在 `workspaces/<feature>/`；涉及仓库及实际基线、工作分支由该 Feature 的 `development/repos.yaml` 记录。具体代码、构建和测试规则归对应代码仓库。本项目已确认 `feat-browseract-dify-plugin`、仓库ID `client/dify-plugin`、工作分支 `feature/browseract-dify-v1`；基线与实际位置见当前 Feature 的 `development/repos.yaml`。

## dify-plugin：本项目开发仓库

- 本地路径：`C:/Users/Administrator/Documents/ChatGPT/dify-plugin`。
- 本次整理前：已初始化 Git，分支为 `master`，无提交、无远程地址，目录内尚无插件实现。
- `agent.md` 继续维护项目上下文和证据入口；根 `AGENTS.md` 已补充阅读指引，引用本页与正式设计，不再复制维护一套项目事实。

## dify-official-plugins：插件格式与竞品源码

- 仓库：<https://github.com/langgenius/dify-official-plugins>
- 本地路径：`C:/Users/Administrator/Documents/Codex/2026-10-14/new-chat/work/dify-official-plugins`。
- 本次核实提交：`f2d7811364193f8d7069f24a299ee465c5519d3c`；本地为浅克隆。
- Firecrawl Tool 插件：`tools/firecrawl/`，Marketplace ID 为 `langgenius/firecrawl`。
- Tavily Tool 插件：`tools/tavily/`，Marketplace ID 为 `langgenius/tavily`。
- 两者是统一源码仓库内可独立打包、独立版本的插件，不是各自单独的插件仓库。

重点参考文件：

| 文件 | 参考内容 |
| --- | --- |
| `manifest.yaml` | 插件标识、版本、运行环境、权限及工具注册入口 |
| `main.py` | Dify Plugin SDK 启动入口 |
| `provider/*.yaml`、`provider/*.py` | 凭据配置、工具注册和凭据校验 |
| `tools/*.yaml` | 用户及模型可读的工具说明、参数、类型和默认值 |
| `tools/*.py` | API 调用、参数转换、错误处理和输出消息 |
| `pyproject.toml`、`uv.lock` | 依赖声明与锁定 |
| `README.md`、`_assets/` | 使用说明和图标 |

已核实的实现示例：

- Firecrawl 的 `tools/crawl.py` 提供 `wait_for_results`；`tools/firecrawl_appx.py` 根据此参数等待结果或先返回任务信息，等待时默认每 5 秒轮询。`tools/crawl_job.py` 提供后续查询或取消入口。
- Tavily 的 `tools/tavily_search.py` 使用 Tavily Python SDK，并返回 JSON 和格式化文本。`tools/tavily_research.py` 在插件内创建任务并轮询，初始间隔 3 秒、逐步增加至最多 10 秒。
- 上述轮询代码没有显式的总等待上限，不据此推断 Dify 平台允许无限等待。
- `datasources/firecrawl_datasource/`、`datasources/tavily_datasource/` 是另外的数据源插件，不能与 Tool 插件范围混同。

官方插件仓库的 `.github/workflows/upload-merged-plugin.yaml` 包含合并后的自动发布设施。第三方插件提交渠道是另一个仓库 `langgenius/dify-plugins`；不要将官方源码仓库和 Marketplace 包提交仓库混为一谈。

- Marketplace 提交仓库：<https://github.com/langgenius/dify-plugins>
- 上架流程：<https://docs.dify.ai/en/develop-plugin/publishing/marketplace-listing/submit-plugin-to-marketplace>
- 编排规则：<https://docs.dify.ai/en/cloud/use-dify/build/orchestrate-node>

正式准备上架时重新核实最新提交模板、校验工具、英文文档、隐私政策和包要求；现有竞品目录不是完整的上架检查清单。

## n8n-nodes-browseract：V3 Bot 集成范围参考

- 仓库：<https://github.com/browseract-ai/n8n-nodes-browseract>
- 本地路径：`C:/Users/Administrator/Documents/Codex/2026-10-14/new-chat/work/n8n-nodes-browseract`。
- 本次核实提交：`46e4ecd1645a786797678b9ac1fc9447628b013f`。
- 入口：`README.md`、`credentials/BrowserActApi.credentials.ts`、`nodes/BrowserAct/BrowserAct.node.ts`、`nodes/BrowserAct/helper.ts`、`nodes/BrowserAct/schema.ts`。

已核实范围：API Key 认证；选择官方模板或账号下有发布版本的 Bot；读取 `input_schema` 并映射参数；启动 V3 任务；轮询状态并获取最终详情；模板代理地区选择；可配置超时。

现有实现达到等待上限后会请求取消 BrowserAct 任务，再读取任务详情。这是 n8n 当前行为，不自动作为 Dify 的超时策略。n8n 的参数控件和映射机制也不保证能原样移植到 Dify。

## Zapier：回调执行参考

- 远程仓库：`git@git.ziniao.com:a59-agentbase/client/zapier.git`
- 本地路径：`C:/Users/Administrator/Documents/Codex/2026-10-15/zapier`。
- 本次核实提交：`4b616c19b7cef658dda00637804ac015e92d4239`。
- 入口：`index.js`、`authentication.js`、`creates/runWorkflow.js`、`lib/helper.js`、`triggers/workflowList.js`、`triggers/templateList.js`。

已核实范围：API Key 认证；选择账号 Workflow 或官方模板；获取输入定义；提交任务并返回结果。当前本地实现仍使用 `/v2/workflow/...` API。

正式运行通过 `z.generateCallbackUrl()` 与 `performResume` 处理异步完成；编辑器 sample 路径采用最多 25 秒的短轮询。该回调恢复机制属于 Zapier 平台适配，不能直接认定 Dify 有相同语义。V2 字段和旧参数结构不能替代 V3 API 契约。

## BrowserAct V3 Bot API：对外契约

- 用户指定的执行入口：<https://docs.browseract.com/workflow/api-reference/tasks/run-a-bot-create-a-task>
- Bot 定义入口：<https://docs.browseract.com/workflow/api-reference/bots/retrieve-a-bot>
- 机器可读契约：<https://docs.browseract.com/openapi_3.json>
- API 主机：`https://api.browseract.com`；认证：`Authorization: Bearer <API_KEY>`。
- OpenAPI 确认版本为 `v3`；2026-10-19 已完成 Bot/模板列表和详情的真实只读认证查询，见上述实测证据。尚未执行任务启动或 Dify 端到端联调。

核心对象：Bot 是自动化定义，Task 是某次执行记录。Bot 类型包括 `workflow` 与 `agent`。

| 能力 | 接口 |
| --- | --- |
| 查找可运行的已发布 Bot | `GET /v3/bots` |
| 读取 Bot 输入及输出 Schema | `GET /v3/bots/{bot_id}` |
| 启动 Bot，返回 `task_id` 和状态 | `POST /v3/bots/{bot_id}/runs` |
| 查询任务状态 | `GET /v3/bots/runs/{task_id}/status` |
| 获取任务详情与结果 | `GET /v3/bots/runs/{task_id}` |
| 查询历史任务 | `GET /v3/bots/runs` |
| 取消任务、恢复符合条件的暂停任务 | `POST /v3/bots/runs/{task_id}/cancel`、`POST /v3/bots/runs/{task_id}/resume` |
| 查找和读取官方模板 | `GET /v3/bots/templates`、`GET /v3/bots/templates/{template_id}` |
| 运行官方模板 | `POST /v3/bots/templates/{template_id}/runs` |
| 查询模板可用代理地区 | `GET /v3/bots/regions` |

接入需要保留的契约边界：

- 启动请求的 `input` 必须符合 Bot 或模板的 `input_schema`；无需参数时传 `{}`。
- 启动成功代表任务已创建，不代表采集完成。支持 `callback_url` 和 `status_change_callback_url`，回调包含完整任务详情；回调地址必须满足公开可达等 API 要求。
- 状态包括 `created`、`running`、`pausing`、`paused`、`finished`、`canceled`、`failed`。`paused` 不等于成功；Agent Bot 不支持恢复。
- `output_schema` 可以为 `null`；不能承诺任意 Bot 都有固定的下游输出字段。
- `output` 内联结果上限为 5 MB；较大结果通过 `output_files` 读取，业务结果单文件上限为 100 MB。文件 URL 是临时地址，插件需处理文件获取和有效期。
- 当前这套 API 不包含 Bot 创建、编辑、发布或通用点击、输入等浏览器操作接口。

## 后续设计时需要确认

- 当前功能讨论：对用户开放哪些通用参数、返回哪些内容供下游使用，以及任务未成功完成时的用户反馈。
- 技术方案与评审阶段：控件实现、字段定义、轮询间隔、请求时限、600 秒默认等待时限的允许范围和平台兼容性、重试、输出结构与大文件处理、认证校验等；R2 超时不取消远端任务已确认。

这些是后续需求和技术方案的输入，不是已确定的实现方案。推进前按 `team-infra` 的流程确认并记录，不从参考仓库自动继承产品决策。
