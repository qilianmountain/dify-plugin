# Run a Bot：输入参数与选择方式

2026-10-22 最新增量（13/17票、0.0.7）：两个工具的 Operation 按 Run Bot、View Parameters 排列，默认 run、显式 view 及 JSON 复制解析行为保持不变。共享客户端所有请求统一携带 `api-channel-ak: difyak`，Bearer Key 不变。轮询维持心跳，超时/异常停止查询、不主动取消；服务端可能因心跳过期取消。源码保留生产 API 主机，`scripts/package-test03.py` 在隔离打包时固定 `https://api-test03.browseract.com` 并标注 BrowserAct (Test03)，不增加用户环境配置项。最新验证与包见 Feature 17 票；以下旧版本决定保留历史语义。

2026-10-21最新决定（12票/0.0.6）：两个工具默认Run Bot，显式View Parameters仍只查询；移除模板Proxy Region字段、地区请求与校验，创建请求不传顶层proxy_region；自定义参数JSON灰字说明改为查询参数及官方集成指引链接。此前默认view、模板US必填的内容属于旧版本决定，已被本次用户指令替代。详情与验证以Feature入口的12票为准。

更新日期：2026-10-19。

统一评审入口：[首版设计方案 v0.8](04-review-design.md)。来源选择已由用户确认改为两个工具入口，其他字段细节仍按本页标记待确认。
状态：一个 BrowserAct 插件下提供“运行我的 Bot”和“运行官方模板”两个工具，各自保留“下拉选择目标 + JSON 输入业务参数”和节点内“查看参数 / 运行 Bot”两种模式；尚未实施正式插件或完成目标 Dify 联调。

## 本轮已确认

- Bot 使用动态加载的下拉选项供用户选择，展示名称、使用对应 ID 运行。
- 我的已发布 Bot 和官方模板继续包含在首版范围内。
- 两个工具分别固定来源、加载自己的列表；移除节点“Bot 来源”字段，不再合并两类目标列表。
- 业务输入采用 JSON；主要流程为粘贴完整 Dify 输出，插件提取 `json[0]` 后与 Bot 默认值逐层合并，对象递归合并、数组整体替换、显式用户值优先。保留纯参数对象和 `{}` 输入。
- 两个工具各自提供模式选择：两个工具均默认“查看参数”，仅返回可复制的参数值对象，不附带说明、不创建任务；用户手动切换“运行 Bot”后启动并同步等待结果。
- 首版先以可下拉选择为要求，不将关键词搜索作为首版必须交付的能力。

用户本轮确认两个工具入口，替代此前来源联动或合并列表的候选；后续用户已确定模板代理默认美国、运行时必须选择有效地区且不可留空，等待超时默认 600 秒；允许范围和平台兼容性仍需验证，手填 Bot ID 不在当前首版范围。

## 建议输入清单

2026-10-20补充决定：两个工具的操作模式放在节点输入变量区域最上方、目标选择之前，保持原生单选与默认查看参数。动态列表仅成功选项在同一插件进程内缓存60秒；凭据、用户与来源隔离，查看定义和执行前校验仍访问当前API，不改变输入及输出契约。升级已有节点需重新确认模式，不承诺原设置区值自动迁移。

将用户所说的“api”理解为 BrowserAct API Key。沿用 Dify 插件的凭据配置机制，API Key 在连接中配置，运行节点使用该连接，不作为每次运行的业务参数。不新增 API 主机地址设置。

| 内容 | 运行我的 Bot | 运行官方模板 | 用途与边界 |
| --- | --- | --- | --- |
| BrowserAct 连接 / API Key | 共用 Provider 凭据 | 共用 Provider 凭据 | 不写入业务 JSON |
| 操作模式 | 查看参数 / 运行 Bot | 查看参数 / 运行 Bot | 各自节点内切换，新建节点默认“查看参数”；不按模式另拆工具 |
| 目标 | 我的已发布 Bot 动态列表 | 官方模板动态列表 | 展示名称、保存确定 ID，不自动模糊匹配 |
| 代理地区 | 不声明此字段 | 地区下拉，仅运行时使用 | 运行模板时必填且默认美国；空值或无效值不启动任务；查看模式忽略，不阻止查看 |
| 等待超时（秒） | 数值 | 数值 | 仅运行时使用；默认 600 秒，允许范围及平台兼容性待验证；超时不取消远端任务，报告超时并保留 `task_id` |
| 自定义参数 JSON | 文本，建议初始 `{}` | 文本，建议初始 `{}` | 粘贴完整查看输出并修改 `json[0]`；插件提取配置后覆盖默认值 |

两个工具共用 1 项连接配置。“运行我的 Bot”有 4 项逻辑节点输入：模式、Bot、等待超时、业务 JSON；“运行官方模板”另有代理地区，共 5 项。不再声明来源参数。查看模式只要求连接和目标，不使用业务 JSON、代理地区、任务等待时限；不承诺随模式隐藏字段。模式默认“查看参数”已确认；字段技术名称与 Dify 的 `form` 分类在技术方案中确定。

## 已确认的参数查看与复制流程

用户在两个来源工具之一选择目标和“查看参数”，单步运行后只返回参数值对象，位于 Dify 输出的 `json[0]`。用户点击“复制全部输出”，整体粘贴到“自定义参数 JSON”，修改其中 `json[0]` 的配置，再切回“运行 Bot”。插件启动前提取 `json[0]`，忽略外层 `text`、`files`，用户不再自行提取对象。保留直接填写纯参数对象或 `{}` 的原有能力；完整输出必须只有一个配置对象，格式有误时不启动任务。

仅保留输入字段与 Schema 明确提供的默认值，不返回参数说明、类型、必填标记、约束、Bot 信息或额外业务包装。正常 `text` 为空、`files=[]`。保留参数名大小写与值类型，包括 `0`、`false`、空字符串。没有默认值的字段不生成占位值，运行时仍校验并提示缺失必填项；有效 Schema 无默认值时返回 `{}`，缺少 Schema 则报节点错误。

使用标准 JSON 消息和 Dify 原生只读结果编辑器，不增加专用复制按钮或独立 JSON 框。点击执行后也不自动回填本节点配置；用户可手动复制，或填 `{}` 使用默认值、只填写覆盖字段。本机演示已同步为两个工具与裸配置输出，真实调用各自 API，但目标 Dify Cloud 尚未联调。

## 与参考实现的关系

- n8n 的节点已有来源、Bot、代理地区、Timeout，凭据在节点 credential 中配置；业务参数使用 resourceMapper，本项目已决定改为 JSON。
- 已查看的 Make 表单包含 Connection、Search Bots From、Bot、Input Parameters、Proxy Region、Timeout；仅当前模板表单得到实查，不扩展为所有版本都具有同一能力。
- n8n 和 Make 展示的 3600 秒不是 Dify 的默认值决定。Dify 当前主分支 Docker 示例配置中 `PLUGIN_MAX_EXECUTION_TIMEOUT=600`，只是示例配置，不代表 Cloud 保证或不可修改的统一上限；后续按目标环境确定允许的等待时限。

## Bot 选择能否输入关键词搜索

区分三个层面：

| 层面 | 本轮核对结果 |
| --- | --- |
| BrowserAct API | Bot 和模板列表均支持可选的 `keyword` 参数 |
| Dify 动态选项加载 | 标准 hook 接收参数名称，返回选项；没有传入用户在下拉框中键入的搜索词 |
| Dify 工作流单选界面 | 本轮核对的主分支及 1.17.1 单选 dynamic-select 渲染为 Select 列表，没有搜索输入框或搜索词过滤逻辑 |

因此，可以将“动态加载 Bot 下拉列表”列入方案，但不能将“在 Bot 框输入关键词、实时查询匹配 Bot”写成当前标准控件已支持。输入字符触发的键盘定位即使存在，也不能等同于可见的关键词过滤或服务端搜索。

尚未对目标 Dify Cloud 的已部署版本进行控件实测，不能仅凭仓库版本推断它的全部实际行为。本轮确认的是所查源码路径未提供对应搜索交互，也没有搜索词传递到插件的接口。

若后续验证某个目标版本具有本地搜索，只能过滤已经加载的选项，仍需完整处理 API 分页，不能只加载第一页后宣称可搜索全部 Bot。必要时可另行讨论手填 Bot ID 作为补充入口，本页不将其记为已确认字段。

## 两个工具的来源边界

“运行我的 Bot”固定使用 Bot 列表、详情和启动接口；“运行官方模板”固定使用模板列表、详情和启动接口。每个 Tool 的动态选项实现只加载自己的列表，不需要读取兄弟字段。模板工具的固定参数中声明代理地区，Bot 工具不声明；两者共享凭据和内部适配模块。

该决定替代独立来源联动下拉及合并来源列表两种候选，参考同一 Firecrawl Provider 注册多个 Tool 的结构。[Firecrawl 注册源码](https://github.com/langgenius/dify-official-plugins/blob/f2d7811364193f8d7069f24a299ee465c5519d3c/tools/firecrawl/provider/firecrawl.yaml#L41-L48)。两种模式不是两个工具，而是每个来源工具内的固定模式参数。

本机演示已移除来源字段和静态样本列表，由两个 Python 工具入口分别加载真实列表与定义，模板入口单独声明地区字段。服务代码在 `docs/demo/live/`，它是本机交互验证服务，不是 Dify SDK Tool 实现，不能证明已在 Dify 联调。业务 JSON 格式和模式相关必填在执行时校验，不依赖编辑时标红、条件隐藏或自动回填。

## 证据入口

- [n8n 来源与目标参数](https://github.com/browseract-ai/n8n-nodes-browseract/blob/46e4ecd1645a786797678b9ac1fc9447628b013f/nodes/BrowserAct/BrowserAct.node.ts#L74-L176)
- [Make 实查记录](../research/04-make-input-form.md)
- [Dify 官方凭据与参数文档](https://docs.dify.ai/en/develop-plugin/dev-guides-and-walkthroughs/tool-plugin)
- [BrowserAct V3 OpenAPI](https://docs.browseract.com/openapi_3.json)
- [Dify main 的 dynamic-select 单选控件](https://github.com/langgenius/dify/blob/73c2c696ff8fe89bde006e40d2d5e99c9715aab1/web/app/components/workflow/nodes/_base/components/form-input-item.tsx#L416-L441)
- [Dify 1.17.1 的 dynamic-select 单选控件](https://github.com/langgenius/dify/blob/8387590ace4a094de812b7847fc6a4c3a27cd52b/web/app/components/workflow/nodes/_base/components/form-input-item.tsx#L422-L441)
- [Dify 动态选项请求](https://github.com/langgenius/dify/blob/73c2c696ff8fe89bde006e40d2d5e99c9715aab1/web/service/use-plugins.ts#L1506-L1530)
- [Dify Docker 配置示例](https://github.com/langgenius/dify/blob/73c2c696ff8fe89bde006e40d2d5e99c9715aab1/docker/.env.example)

本轮仅调研并整理文档，未添加插件、修改用户工作流或启动任务。
