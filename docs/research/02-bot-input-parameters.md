# 02：Bot 选择与动态输入参数的可行性

核实日期：2026-10-16。状态：源码和文档调研，未进行 Dify 界面或插件联调。

2026-10-19 最新产品决定：一个 BrowserAct 插件提供“运行我的 Bot”和“运行官方模板”两个工具，各自保留“查看参数 / 运行 Bot”和 JSON 输入。各 Tool 的来源固定，分别加载自己的列表，替代下文历史单工具来源字段及合并列表候选；动态字段、选项与配置写回的证据边界仍有效。正式设计见 [v0.8 评审稿](../design/04-review-design.md)。

## 已确认的产品范围

用户已确认首版同时支持“我的已发布 Bot”和“官方模板”，现按来源拆成两个 Tool；运行模式内部轮询后同步返回结果。通用参数独立填写、业务输入使用 JSON；插件合并输入定义中的默认值与用户 JSON，用户提供的字段优先。两个工具各自提供“查看参数”模式：显式单步运行后只读取 `input_schema`，仅返回可复制修改的参数值对象，不启动任务；点击执行并收到输出后也不自动回填配置。当前产品决定见 [首版工具范围与输入方式](../design/01-tools-and-input.md)；Dify 实际展示与复制体验仍需联调。

最初核实对象是 n8n 的“选择 Bot 后动态加载业务输入字段”体验，随后也通过 Edge 查看了 Make 实际表单，见 [Make 表单实查](04-make-input-form.md)。动态表单调研保留为平台差异证据，不再作为首版业务输入的实现前提。

## 结论

### 本轮重新核对：当前标准 Tool 插件不能直接复刻 Make 的联动

本轮重新读取官方文档和源码：Dify `main` 为 `f3d7a49927da129f75c52a55392aad79a613e993`；SDK `main` 为 `a91e6b4a7d83b43746a70e86267796744f96d06b`。以下是当前源码结论，不是对 Dify Cloud 已部署版本的运行验证。

“一个 Run a Bot → 选择任意 Bot → 自动加载该 Bot 专属的独立业务字段”没有找到可直接使用的标准插件机制。阻碍不在 BrowserAct 缺少 `input_schema`，而在 Dify 的参数定义与节点配置之间缺少对应联动。

| 候选机制 | 当前证据 | 对本项目的结论 |
| --- | --- | --- |
| `dynamic-select` | 官方文档定义为动态下拉选项；SDK hook 只接收字段名，返回 `ParameterOption[]` | 可作为 Bot 列表机制，不能生成其他输入字段 |
| `_get_runtime_parameters()` | 可以返回参数列表，但已弃用；SDK 签名与后端请求均没有当前节点参数 | 可研究基于凭据生成字段，但不能直接按节点选中的 `bot_id` 联动 |
| `show_on` | SDK 声明了条件；当前主程序后端参数模型未声明，前端转换时显式置空 | 不能作为当前可用的字段联动方案；即使完整支持也只控制已有字段的显示 |
| `reset_on_change` | SDK 声明重置依赖；不是字段定义加载接口 | 不能用来请求新的 Bot 输入 Schema |
| `input_schema` | SDK 注释用于 MCP 对象/数组参数；工作流对象控件显示 JSON 编辑器和 Schema 查看入口 | 不是选择 Bot 后自动展开任意顶层表单的机制 |

### 当前调用链的直接证据

1. **编辑器字段来源**：`use-config.ts:58–69` 从 `currTool.parameters` 转换表单，按 `form` 分成输入与设置；`:107–118` 和 `:154–163` 在修改时更新节点值。未见参数变化后向插件请求新字段定义的步骤。
2. **动态下拉请求**：`form-input-item.tsx:132–140` 调用 `useFetchDynamicOptions`，传插件、provider、tool、字段名等；工作流 Tool 面板没有把当前 Bot 选择放入 `extraParams`。`use-plugins.ts:1506–1530` 返回并映射的是选项列表。后端 `PluginParameterService.get_dynamic_select_options` 同样没有当前节点参数，只加载凭据并转交动态选项客户端。SDK 最终为 `_fetch_parameter_options(self, parameter: str)`。
3. **旧动态字段入口**：SDK `tool.py:205–218`、`:464–468` 明确标记 deprecated。Dify `api/core/plugin/impl/tool.py:189–234` 请求的数据只有 provider、tool、credentials 及会话上下文，没有 `tool_parameters`；因此不能据此取得当前节点选择的 `bot_id`。
4. **条件显示未贯通**：SDK `entities/tool.py:153–163` 有 `show_on` 与 `reset_on_change`，但 Dify `api/core/plugin/entities/parameters.py:80–95` 的 `PluginParameter` 没有这两项。前端 `to-form-schema.ts:94–113` 明确将参数和选项的 `show_on` 都设为 `[]`，ToolForm 直接遍历 Schema 生成字段。

例如真实 SDK 的两个入口签名分别是：

```python
def _fetch_parameter_options(self, parameter: str) -> list[ParameterOption]:
def _get_runtime_parameters(self) -> list[ToolParameter]:
```

它们都没有 n8n 的 `getNodeParameter('workflowId', ...)` 那样的当前节点选择上下文。执行入口 `_invoke(tool_parameters)` 能收到这些值，但届时用户已经完成配置，不能据此补出执行前的编辑器字段。

### 对方案的影响

- 不能把“标准 Marketplace 插件内直接实现任意 Bot 动态表单”写成已可行。用户现已选择固定 JSON 输入字段，不再依赖这一能力。
- 同一限制也影响“来源切换后隐藏某些通用字段”的既有草案：不能仅凭 SDK 中存在 `show_on` 就承诺编辑器效果。
- 预先定义固定 Bot 的业务字段是另一种模式，不能满足当前任意 Bot 的单工具联动目标。为不同 Bot 生成独立工具、将目标放到凭据配置，或修改自部署 Dify 都会改变当前交互或部署条件，不能当作无成本替代方案。
- 用户已明确选择 JSON 输入及默认值覆盖方向；不采用修改 Dify 本体或为各 Bot 增加独立工具的替代路线。默认值合并由插件实现，不推断服务端一定自动补齐；嵌套对象等细节留待方案评审。

相关主程序 PR `langgenius/dify#36148` 的内容是补充 Tool 参数条件显示。GitHub 页面检索快照仍显示 Open，但本轮直接读取 GitHub API 得到 `state=closed`、`merged=false`、`merged_at=null`，因此按未合并记录，不能把该 PR 当成已发布能力。结论主要依据固定提交的实际源码，不依赖 PR 搜索摘要。

本轮证据：

- [官方 Tool 参数说明](https://docs.dify.ai/en/develop-plugin/dev-guides-and-walkthroughs/tool-plugin)
- [工作流参数来源与配置更新](https://github.com/langgenius/dify/blob/f3d7a49927da129f75c52a55392aad79a613e993/web/app/components/workflow/nodes/tool/hooks/use-config.ts#L58-L118)
- [工作流 Tool 面板](https://github.com/langgenius/dify/blob/f3d7a49927da129f75c52a55392aad79a613e993/web/app/components/workflow/nodes/tool/panel.tsx#L62-L102)
- [动态下拉请求](https://github.com/langgenius/dify/blob/f3d7a49927da129f75c52a55392aad79a613e993/web/service/use-plugins.ts#L1506-L1530)
- [后端动态选项服务](https://github.com/langgenius/dify/blob/f3d7a49927da129f75c52a55392aad79a613e993/api/services/plugin/plugin_parameter_service.py#L22-L119)
- [旧动态参数请求](https://github.com/langgenius/dify/blob/f3d7a49927da129f75c52a55392aad79a613e993/api/core/plugin/impl/tool.py#L189-L234)
- [前端清空条件显示](https://github.com/langgenius/dify/blob/f3d7a49927da129f75c52a55392aad79a613e993/web/app/components/tools/utils/to-form-schema.ts#L94-L113)
- [后端参数模型](https://github.com/langgenius/dify/blob/f3d7a49927da129f75c52a55392aad79a613e993/api/core/plugin/entities/parameters.py#L12-L95)
- [SDK 动态选项与弃用入口](https://github.com/langgenius/dify-plugin-sdks/blob/a91e6b4a7d83b43746a70e86267796744f96d06b/src/dify_plugin/interfaces/tool/tool.py#L441-L479)
- [SDK 参数条件声明](https://github.com/langgenius/dify-plugin-sdks/blob/a91e6b4a7d83b43746a70e86267796744f96d06b/src/dify_plugin/entities/tool.py#L151-L163)
- [主程序条件显示 PR](https://github.com/langgenius/dify/pull/36148)、[本轮核对 PR 状态的 GitHub API](https://api.github.com/repos/langgenius/dify/pulls/36148)

下文保留此前的 SDK、竞品与输入格式调研。涉及 Dify 当前支持情况时，优先采用以上本轮固定提交的调用链证据。

在本次检查的 Dify 标准 Tool 插件接口中，动态下拉选项与动态参数定义是两件事：

| 目标 | 调研结论 |
| --- | --- |
| 使用 API Key 拉取 Bot 名称和 ID，显示为下拉选项 | 存在 `dynamic-select` 和选项加载接口，具备标准机制；实际目标版本及界面仍需联调 |
| 选中某个 Bot 后，把当前 `bot_id` 传给插件并重新生成该 Bot 的输入字段 | 没有找到标准联动接口，不能承诺直接复刻 n8n |
| 在工具执行时读取 Bot Schema 并校验输入 | 插件可在 `_invoke(tool_parameters)` 中实现；这不代表编辑器动态生成字段 |
| 在 Agent 中自动获得每个 Bot 专属的参数 Schema | 本次未证明选中 Bot 后可动态刷新；不能直接承诺 |

以上是动态表单能力的调研边界，不应将动态下拉等同于 Schema 驱动表单；当前产品已选择 JSON 业务输入。

## 官方 SDK 与后端证据

SDK 的 `Tool._fetch_parameter_options(self, parameter: str)` 返回 `ParameterOption` 列表。它接收参数名称，未接收节点当前的全部参数值；`ToolRuntime` 提供 credentials、credential_type、user_id、session_id，没有当前节点已选择的 `bot_id`。[S1][S2]

这足以基于凭据加载可用 Bot。来源切换可考虑两个分别加载的列表或预先合并目录，但当前接口不能直接以兄弟字段值作为依赖参数。具体界面方案尚未确认。

旧的 `_get_runtime_parameters(self)` / `get_runtime_parameters(self)` 可以返回 `ToolParameter`，但 SDK 已将其标记为 deprecated，签名也不接收当前节点参数。Dify 后端调用 `get_runtime_parameters` 时传入 provider、tool、credentials 及会话上下文，没有传入当前工具参数值。[S1][S3][S4]

SDK Schema 中存在 `show_on`、`reset_on_change` 和 `input_schema` 字段。条件显示、重置或预先声明对象结构，不等于支持“选择 Bot 后远程请求新 Schema”。如果考虑预加载所有 Bot 参数、再条件显示等绕行方式，需要另外验证 SDK 版本、前端支持、字段冲突、刷新和性能；本次没有验证，不作为既定方案。[S2][S5]

## n8n 对照与官方插件参考

n8n 的 `BrowserAct.node.ts` 明确配置 `resourceMapperMethod: getWorkflowInputs`，读取 `workflowId` / `templateId`，请求对应详情的 `input_schema`，通过 `buildResourceMapperFields` 生成字段；配置还包括 `loadOptionsDependsOn`。这是本次所查 Dify SDK 接口缺少的依赖上下文。[S6]

Zapier 本地提交 `4b616c19b7cef658dda00637804ac015e92d4239` 的 `creates/runWorkflow.js:11–35` 也已实现动态业务字段：`getWorkflowInputFields(z, bundle)` 从 `bundle.inputData` 取得来源与所选 ID，读取 V2 Workflow 详情的 `input_parameters`，逐项返回字段定义。来源、Workflow 和模板选择字段配置 `altersDynamicFields: true`，选择变化时触发字段刷新。当前业务字段全部声明为 `type: 'string'`；不应描述成与 n8n 相同的多类型 Schema 控件。

Zapier [官方动态字段文档](https://docs.zapier.com/platform/build/dynamic-field) 明确允许字段加载代码读取 `bundle.inputData` 中先前字段的值，并在标记 `altersDynamicFields` 的字段变化后重新获取动态字段。因此，Zapier 与 n8n 都有“当前选择 → 远程读取输入定义 → 返回字段列表”的机制，而且 BrowserAct 仓库中已有对应实现；Dify 当前标准入口缺少的正是这一整段联动，不能通过直接移植脚本补齐。本轮为源码和官方文档核对，未重新执行两边的线上插件。

Dify 官方仓库的 ComfyUI `get_runtime_parameters()` 根据账号可用模型生成参数，不能作为“根据当前节点选择动态换字段”的证据。[S7]

官方 AIHubMix Image 插件展示了动态模型列表：从 credentials 创建客户端、返回选项，执行时再根据选定模型读取 Schema 校验 payload。其输入字段依然预先声明，没有证明选定模型后编辑器会自动生成任意字段。[S8]

## 尚未验证与后续讨论

- 未安装或启动 Dify，未执行目标 Cloud/Community 版本的界面验证。
- 动态选项加载的控件位置与 `form` 配置存在版本/界面差异。官方 AIHubMix 示例专门注明工作流中使用 `form: llm`，不能直接将此结论推广到所有 Agent 界面。[S8]
- 当前业务输入使用 JSON；Bot 选择器、列表加载、来源相关通用字段展示和上游 JSON 变量绑定仍需验证。
- 不把对 Dify 主程序的定制修改视为 Marketplace 插件自动具备的能力。

## Apify 的实际做法

2026-10-16 核实 `apify/apify-dify-integration` 的 `main` 提交 `4ea5006d53236eeec12474b59d57b1416bc30fe0`。以下结论来自对应源码和官方使用指南，未进行界面联调。

- `Run Actor` 使用固定字段：`actorId` 为普通 string，`input_body` 也是 string，显示名称为 Input，默认值为 `"{}"`。它没有在选择 Actor 后生成各 Actor 专属的输入控件。
- 用户从 Apify Console 的 Actor 输入页取得 JSON，在 Dify 的 Input 字段提供 JSON 字符串；不同 Actor 通过 JSON 的不同字段表达输入差异。其他固定字段包含 build、wait_for_finish、timeout 和 memory。
- 执行时调用 `parse_json_param` 解析 JSON，然后将解析结果作为 `run_input` 交给 Apify SDK。当前解析函数检查 JSON 语法，但没有在此处按 Actor Schema 完整校验字段结构；不可把通用 JSON 解析说成 Schema 验证。
- 若解析后的输入为空，`Run Actor` 会尝试从默认 build 的输入 Schema 提取 `prefill` 值作为运行输入。这发生在执行阶段，不会把 Schema 展开成编辑器字段；当前代码也不是对任意非空用户输入逐字段合并 prefill。
- `Run Actor Task` 用固定的 Task ID 与 `input_override` JSON 输入，覆盖预配置任务的输入。Apify 的 Actor Task 是预配置执行项，不能直接等同于 BrowserAct 的某次 Task 运行记录。

Apify 的“Actor ID + JSON”是当前 BrowserAct 输入方式的参考。BrowserAct 另外已确认采用“Bot 默认值 + 用户 JSON 覆盖”的合并方向，不能直接复制 Apify 仅在输入为空时提取 prefill 的行为；具体实现仍需设计。

上游对象可先序列化为 JSON 字符串再传入，避免手工拼接引号和换行。BrowserAct 的 JSON 字段变量绑定与控件体验仍需在目标 Dify 版本验证。

证据入口：

- [Apify 官方 Dify 使用指南](https://docs.apify.com/integrations/dify)
- [Run Actor 参数定义](https://github.com/apify/apify-dify-integration/blob/4ea5006d53236eeec12474b59d57b1416bc30fe0/tools/run_actor.yaml)
- [Run Actor 输入与 prefill 实现](https://github.com/apify/apify-dify-integration/blob/4ea5006d53236eeec12474b59d57b1416bc30fe0/tools/run_actor.py)
- [Run Actor Task 参数定义](https://github.com/apify/apify-dify-integration/blob/4ea5006d53236eeec12474b59d57b1416bc30fe0/tools/run_actor_task.yaml)
- [JSON 解析与错误处理](https://github.com/apify/apify-dify-integration/blob/4ea5006d53236eeec12474b59d57b1416bc30fe0/utils/error_handling.py)

## Firecrawl 截图对应的参数与脚本

用户提供的 Search 截图与本地参考提交的 `tools/firecrawl/tools/search.yaml` 相符：`query` 是 `type: string`、`form: llm`，位于输入变量区；limit、sources、categories、includeDomains 等是预先声明的 `form: form` 参数，位于设置区。

官方文档区分参数类型和使用方式：类型包含 string、number、boolean、select、dynamic-select、any、文件等；`form` 控制工具参数如何使用。在 Workflow 中 `llm` 参数作为节点输入变量配置；在 Agent 中由模型推断，`form` 参数则用于预配置。不能仅凭字段能插入变量，就推断工具会动态添加新字段。

`tools/firecrawl/tools/search.py` 接收 `tool_parameters`，将逗号分隔的 sources、categories、domains 转为数组，将抓取选项组为 `scrapeOptions`，补充默认值，过滤 None 和空字符串，最后调用 Firecrawl API 并产生 JSON 输出。这是 BrowserAct 可参考的请求适配脚本模式；不直接复制它的全部转换规则，例如不能把 BrowserAct 有意义的空值或未填参数不加区别地过滤。

普通分字段输入和 JSON 输入是两种用户操作方式，均可由脚本转换为 API JSON 请求。Firecrawl Search 的业务字段预先声明，不能据此证明动态表单可行；BrowserAct 当前选择通用参数独立填写、业务输入使用 JSON。

- [Firecrawl Search 参数声明](https://github.com/langgenius/dify-official-plugins/blob/f2d7811364193f8d7069f24a299ee465c5519d3c/tools/firecrawl/tools/search.yaml)
- [Firecrawl Search 请求转换脚本](https://github.com/langgenius/dify-official-plugins/blob/f2d7811364193f8d7069f24a299ee465c5519d3c/tools/firecrawl/tools/search.py)
- [官方 Tool 参数类型与 form 说明](https://docs.dify.ai/en/develop-plugin/dev-guides-and-walkthroughs/tool-plugin)

### 官方仓库中的 JSON 字符串输入实例

以下均核实于上述本地官方插件提交，不代表已执行联调或确认当前 Marketplace 安装包内容。

1. **Firecrawl Create Monitor**：`tools/firecrawl/tools/create_monitor.yaml:125` 起将 `scrapeOptions` 声明为 `type: string`、`form: form`，帮助文字要求 JSON 对象。`create_monitor.py:20` 调用 `get_json_params`，随后将对象放进 `target["scrapeOptions"]`。解析函数位于 `firecrawl_appx.py:151`，使用 `json.loads`。这说明 Firecrawl 也混合使用独立字段与 JSON 字符串字段。
2. **APITemplate Create PDF**：`tools/apitemplate/tools/create_pdf.yaml:21` 声明 `template_id`，`:39` 声明 `json_data`（`type: string`、必填、`form: llm`）。`create_pdf.py:18` 读取文本，`:32` 执行 `json.loads(json_data_str)`，`:62` 起使用 `requests.post(..., json=json_data, params=params, timeout=60)`。其“模板 ID + 模板业务数据 JSON”与 BrowserAct 的“Bot ID + Bot 业务输入 JSON”结构更接近，但 API 和字段语义不同。

这些是当前 JSON 输入方向的实际代码参考，不代表全部实现细节已确认。具体错误处理和类型校验不应直接照搬。尤其 Firecrawl 的 helper 会将单引号整体替换为双引号；BrowserAct 不能盲目复制，以免改变用户字符串内容。

- [Firecrawl JSON 输入声明](https://github.com/langgenius/dify-official-plugins/blob/f2d7811364193f8d7069f24a299ee465c5519d3c/tools/firecrawl/tools/create_monitor.yaml#L125-L137)
- [Firecrawl 参数解析与使用](https://github.com/langgenius/dify-official-plugins/blob/f2d7811364193f8d7069f24a299ee465c5519d3c/tools/firecrawl/tools/create_monitor.py#L18-L26)
- [Firecrawl JSON helper](https://github.com/langgenius/dify-official-plugins/blob/f2d7811364193f8d7069f24a299ee465c5519d3c/tools/firecrawl/tools/firecrawl_appx.py#L151-L160)
- [APITemplate 输入声明](https://github.com/langgenius/dify-official-plugins/blob/f2d7811364193f8d7069f24a299ee465c5519d3c/tools/apitemplate/tools/create_pdf.yaml#L20-L55)
- [APITemplate 执行脚本](https://github.com/langgenius/dify-official-plugins/blob/f2d7811364193f8d7069f24a299ee465c5519d3c/tools/apitemplate/tools/create_pdf.py#L15-L68)

## 原生结果编辑器与插件输出的边界

2026-10-19 修正：工具能返回文本/JSON 消息，不代表能指定它们在节点结果区的界面组件。用户要求原型与设计均按 Dify 原生能力呈现。

- Dify 1.17.1 提交 `8387590ace4a094de812b7847fc6a4c3a27cd52b` 的 `result-panel.tsx:142–162` 将整个 `outputs` 交给一个 `CodeEditor`，配置为 `readOnly`、JSON 语言和 JSON 美化。
- `code-editor/index.tsx:140–154` 使用 Monaco 只读编辑器、自动换行；`base.tsx:74–80` 的复制操作复制整个编辑器字符串。
- 最新设计仅用 `create_json_message()` 返回实际参数值对象，位于 `json[0]`，正常不返回文本消息、`text` 为空。过滤参数说明、Schema、Bot 信息和额外业务包装字段；Dify 原生外层仍保留。按最新产品决定，用户点击原生按钮复制整体输出并粘贴，插件运行前提取 `json[0]` 并忽略外层 `text`、`files`；这是插件输入适配，不是结果界面定制，默认配置值的必要 JSON 转义必须保留。
- 独立参数说明列表、默认 JSON 框、折叠约束、参数卡片，以及专用复制组件属于先前原型自定义排版，现已移除；不是标准工具插件接口提供的能力。
- 原型也不再模拟来源变化自动筛选 Bot、按模式动态改帮助文字/必填标记、在画布增加内部调用时间线；运行时校验和文档中的接口流程仍可实现。来源现由两个固定 Tool 确定，不再依赖来源字段联动；仍需在目标 Dify 验证工具声明和列表控件。
- 数据 API 只读实测已完成，目标 Dify Cloud 的插件联调尚未完成；源码证据绑定上述版本，不声称已核实目标 Cloud 的所有 UI 细节。

来源：[原生结果面板](https://github.com/langgenius/dify/blob/8387590ace4a094de812b7847fc6a4c3a27cd52b/web/app/components/workflow/run/result-panel.tsx#L142-L162)、[只读编辑器配置](https://github.com/langgenius/dify/blob/8387590ace4a094de812b7847fc6a4c3a27cd52b/web/app/components/workflow/nodes/_base/components/editor/code-editor/index.tsx#L128-L154)、[复制操作](https://github.com/langgenius/dify/blob/8387590ace4a094de812b7847fc6a4c3a27cd52b/web/app/components/workflow/nodes/_base/components/editor/base.tsx#L74-L80)、[官方工具返回文档](https://docs.dify.ai/en/develop-plugin/features-and-specs/plugin-types/tool)。

## 证据版本和入口

执行完成后的配置写回边界另见下节；标准返回消息与输出变量不代表具有编辑器配置写入能力。

2026-10-19 补充：[真实 Bot/模板详情查询](evidence/2026-10-19-bot-api/README.md)。已读取账号下两个 Bot，以及六个官方模板的详情。八个样本均返回 `input_schema` 和默认值；Google Maps Scraper、Reddit Scraper 的参数未返回说明。其他样本存在 `description`、枚举、类型及范围约束。完整响应和从 Schema 提取的默认参数 JSON 已保存；本次未启动任务，也不证明 Dify 编辑器可动态回填相邻字段。

此前 Dify 快照为 `10285432d2259cc1c1ebf1512d9fbc09810976c9`，本轮已重新核对到 `f3d7a49927da129f75c52a55392aad79a613e993`。SDK `main`：`a91e6b4a7d83b43746a70e86267796744f96d06b`。官方插件本地参考提交为 `f2d7811364193f8d7069f24a299ee465c5519d3c`；n8n 为 `46e4ecd1645a786797678b9ac1fc9447628b013f`。以上是调研快照，不是已选定的生产兼容版本。

## 执行完成后能否回填当前节点的 JSON 配置

2026-10-19 核对：点击“运行此步骤”后，插件可以处理 Bot API 返回内容并输出 JSON，但当前标准 Tool 插件没有将结果写回同一节点“自定义参数 JSON”配置的接口。触发时机从选择 Bot 改成点击运行，不会增加配置写入能力。

- 官方返回接口包括 `create_json_message()` 和 `create_variable_message()`；前者返回 JSON 消息，后者创建工作流输出变量。变量名与输入参数同名，也不代表修改该输入框。自定义输出变量仍需声明 `output_schema` 并实际返回，不能用它替代节点配置更新。
- 所查 Dify 提交 `f3d7a49927da129f75c52a55392aad79a613e993` 的单步运行 Hook `use-one-step-run.ts` 在执行结束时保存 `runResult`、刷新检查变量及运行状态；`setRunResult` 调用 `fetchNodeInspectVars`、`appendNodeInspectVars`。该处理链没有将返回值映射到工具输入 `tool_parameters` 或设置 `tool_configurations` 的步骤。
- 本项目保留手动复制/粘贴步骤，但改为点击“复制全部输出”并整体粘贴到自定义参数 JSON，由插件提取 `json[0]`；可直接用 `{}` 读取默认值，或者仅填写要覆盖的字段。下游节点引用上游结果属于运行时绑定，不等于把结果回写成本节点可编辑的配置，也不承诺本节点同次执行能引用自己的输出。

来源：[官方工具返回接口](https://docs.dify.ai/en/develop-plugin/features-and-specs/plugin-types/tool)、[Dify 单步运行处理源码](https://github.com/langgenius/dify/blob/f3d7a49927da129f75c52a55392aad79a613e993/web/app/components/workflow/nodes/_base/hooks/use-one-step-run.ts)、[节点输入配置更新源码](https://github.com/langgenius/dify/blob/f3d7a49927da129f75c52a55392aad79a613e993/web/app/components/workflow/nodes/tool/hooks/use-config.ts#L143-L150)。结论针对当前所查标准插件和主程序实现，目标 Cloud 尚未联调，不讨论修改 Dify 本体或浏览器扩展等额外方案。

- [S1：SDK Tool 接口](https://github.com/langgenius/dify-plugin-sdks/blob/a91e6b4a7d83b43746a70e86267796744f96d06b/src/dify_plugin/interfaces/tool/tool.py)
- [S2：SDK ToolRuntime 与 ToolParameter](https://github.com/langgenius/dify-plugin-sdks/blob/a91e6b4a7d83b43746a70e86267796744f96d06b/src/dify_plugin/entities/tool.py)
- [S3：Dify 插件工具运行时参数入口](https://github.com/langgenius/dify/blob/10285432d2259cc1c1ebf1512d9fbc09810976c9/api/core/tools/plugin_tool/tool.py)
- [S4：Dify 到 Plugin Daemon 的参数请求](https://github.com/langgenius/dify/blob/10285432d2259cc1c1ebf1512d9fbc09810976c9/api/core/plugin/impl/tool.py)
- [S5：官方 SDK Schema 文档](https://langgenius.github.io/dify-plugin-sdks/schema/)
- [S6：n8n BrowserAct 节点](https://github.com/browseract-ai/n8n-nodes-browseract/blob/46e4ecd1645a786797678b9ac1fc9447628b013f/nodes/BrowserAct/BrowserAct.node.ts)
- [S7：官方 ComfyUI 参数实现](https://github.com/langgenius/dify-official-plugins/blob/f2d7811364193f8d7069f24a299ee465c5519d3c/tools/comfyui/tools/txt2img.py)
- [S8：官方 AIHubMix 动态选项实现](https://github.com/langgenius/dify-official-plugins/blob/f2d7811364193f8d7069f24a299ee465c5519d3c/tools/aihubmix_image/utils/tool_base.py)及[参数声明](https://github.com/langgenius/dify-official-plugins/blob/f2d7811364193f8d7069f24a299ee465c5519d3c/tools/aihubmix_image/tools/image-generate.yaml)
- [官方 Tool 插件开发文档](https://docs.dify.ai/en/develop-plugin/dev-guides-and-walkthroughs/tool-plugin)
