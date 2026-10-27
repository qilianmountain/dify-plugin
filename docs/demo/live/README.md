# BrowserAct Two-Tool Live API Demo

## English UI update — 2026-10-21

The local demo now uses English for its controls, tool labels, guidance and
generated errors. Run it with `python docs/demo/live/server.py` and open
<http://127.0.0.1:1840/>. Enter the Key in **Local Demo Connection · Outside Dify**,
click **Load Demo Lists**, and select **Run My Bot** or **Run Official Template**.
These connection controls belong to the demo; Dify manages actual plugin credentials.

Both tools default to **Run Bot**. To inspect parameters first, select a target,
choose **View Parameters**, then click
**▶ Run this step**. Open **LAST RUN**, copy the full output, paste it into
**Custom Parameters JSON**, and edit the parameter values inside `json[0]`.
Switch to **Run Bot** when ready to create a real task. Runs use account credits;
the wait defaults to 600 seconds. The plugin exposes no proxy region and sends
no proxy override. A timeout stops waiting without canceling the remote task.

The JSON field help now links to the official integration overview. Operation
and Bot/template keep short question-mark tooltip hints, matching
Dify's native field-type rules. The earlier demo incorrectly showed dropdown
descriptions as permanent gray text; this has been corrected. The demo uses
browser tooltips to illustrate the rule, not Dify's exact tooltip styling.

The descriptions follow Issue 12's shorter linked help, retaining Issue 11's
placement rule. Real
Bot/template names, defaults, API results and service messages retain their
original language. This is a separate local demo, not installed-package or Cloud
verification. The original checkout's running demo is preserved; the following
Chinese sections and older screenshots document historical development evidence.

这是可丢弃的本机交互原型，对齐 [v0.8 设计](../../design/04-review-design.md)。它有实际执行的两个 Python 工具入口和共享后端，使用真实 BrowserAct V3 API；不是运行在 Dify 内的插件，没有安装 Dify SDK、插件清单或 Marketplace 上架包。界面按已核对的 Dify 原生结构制作，不代表目标 Cloud 已联调。

## 使用

运行 `python docs/demo/live/server.py`，打开 <http://127.0.0.1:1840/>。在模拟 Dify 窗口上方的“本机演示连接设置 · 非 Dify 控件”中填写 API Key，点击“加载演示列表”，再在节点中选择目标并点击“运行此步骤”。页面顶部两个按钮用于演示选择不同的 Tool，属于工具入口，不是同一节点里的来源参数。两个工具初始均为“查看参数”，与已确认的 R6 一致；只有手动切换“运行 Bot”才创建任务。

- **运行我的 Bot**：实际加载 `GET /v3/bots` 的全部分页，仅列已发布 Bot；不声明代理地区字段。
- **运行官方模板**：实际加载 `GET /v3/bots/templates` 的全部分页；另从 `GET /v3/bots/regions` 加载代理地区。
- **查看参数**：后端读取该工具固定来源的详情接口，从 `input_schema` 提取明确默认值，直接返回 `{"text":"","json":[参数对象],"files":[]}`。无说明、Schema 或额外业务包装；用户点击“复制全部输出”并整体粘贴到自定义参数 JSON，修改其中 `json[0]` 的配置；无需手动删除外层包装。
- **运行 Bot**：后端重新读取定义，识别完整 Dify 输出并提取唯一的 `json[0]` 参数对象，忽略外层 `text`、`files`，再合并 JSON，真实创建任务，在后端轮询状态并获取最终详情；将整个任务详情对象放入 `json[0]`，不按字段白名单裁剪、不下载转存文件，与已确认的 R3 一致。超时报告任务 ID，不自动取消；此行为与已确认的 R2 一致。前后端默认等待超时均为 600 秒。模板代理从实际地区列表中默认选择美国（`US`），运行时必填且不能留空，后端校验是否为有效地区；查看模式忽略地区、超时和业务 JSON。

“加载演示列表”按钮与密钥输入仅是本机 API 调试入口，已移出模拟 Dify 窗口和节点表单。真实 Dify 在插件授权中配置 Provider 凭据，动态选项由平台获取；不把这个演示辅助按钮当作正式插件 UI。

该调整已浏览器验证：模拟窗口及节点表单均无 API Key 输入或加载按钮，外部演示连接仍能加载 408 个官方模板，并查询 Google Maps Scraper 参数 HTTP 200。无重复元素 ID 或横向溢出。页面效果见 [外置演示连接设置](demo-connection-outside-node.png)。

Key 只保存在当前页面与请求内存，不写文件、日志、浏览器存储或 URL，刷新需重填。没有内置 Bot 列表或 Schema，也不在查询失败时回退到样本。两个工具共用连接，分别保留自己的页面配置；切换入口不是来源字段联动。查看不使用运行 JSON、超时或代理地区，也不会回填 JSON。

## 实际代码职责

| 文件 | 本机服务实际执行的职责 |
| --- | --- |
| `provider.py` | 注册两个工具实例，共用凭据与内部模块 |
| `tools/run_my_bot.py` | 固定 Bot 接口路径、ID 字段与分页大小 |
| `tools/run_official_template.py` | 固定模板接口路径、ID 字段与代理地区能力 |
| `shared/base_tool.py` | 分页列表、读取定义、两模式分流、创建与轮询任务 |
| `shared/client.py` | 固定 BrowserAct 主机的 HTTP 客户端、错误处理与凭据脱敏 |
| `shared/parameters.py` | 提取默认值、识别完整输出并提取配置、合并覆盖字段、常用 Schema 约束预校验 |
| `server.py` | 本机 HTTP 传输层，按工具身份路由，只有固定工具动作，不接收任意 URL |
| `app.js` | 显示两个入口与各自字段，调用本机工具服务，呈现标准输出 |

这些模块均参与实际请求链路，不是仅为展示目录而创建。Tool 服务目前是普通 Python 类；后续正式插件需接 Dify `Tool` / Provider SDK 和 YAML 声明，本演示不能替代这一步。

业务参数合并已同步最新方案：默认对象与用户对象逐层合并，未填写字段保留默认值；数组整体替换，`0`、`false`、空字符串及合法 `null` 保留用户值。支持纯参数对象及完整 Dify 输出提取后的配置；合并后进行 Schema 预校验，不修改原始默认对象。

参数预校验覆盖常用类型、必填、枚举、数值/字符串范围及格式，完整 Schema 合法性仍由 BrowserAct API 校验；不声称已覆盖所有 JSON Schema 特性。运行结果文件目前只展示 API 元数据，没有下载转存到 Dify `files`。

`build_demo.py` 从旧内嵌原型复用界面外观，并完全移除内置目录和模拟执行脚本；它不更改原内嵌页面。生成的 `index.html` 加载实际 `app.js`。服务仅监听 `127.0.0.1:1840`，日志只记录 BrowserAct 方法、路径和 HTTP 状态。

## 验证

离线验证：`python -m unittest discover -s docs/demo/live -p test_server.py -v`，20 项通过，覆盖两个独立来源、分页、未发布过滤、查看模式只请求定义、裸配置输出、`0`/`false`/空字符串保留、缺失 Schema、完整输出在两个工具中的复制/修改/运行请求往返、错误包装不创建任务、纯参数对象兼容、多层对象合并保留必填默认值、数组清空、合并不修改默认对象、600 秒默认预算、模板地区空值/无效值不创建任务、暂停立即结束且不再查询详情、创建请求与内部轮询、失败/任务 ID、路由及凭据脱敏。运行测试没有创建真实任务。

2026-10-19 浏览器真实验证：个人列表返回 2 个已发布 Bot、官方模板列表返回 408 项，代理地区返回 37 项，均通过对应 API 加载。个人 `google search` 详情 HTTP 200，查看输出只含 `search_input` 配置；查看时业务 JSON 非法且超时为空仍可成功，输入框保持原值。官方 `Google Maps Scraper` 详情 HTTP 200，复制结果的 `json[0]` 仅包含 `URL`、`Area`、`Keyword`、`datalimit`，后者仍为字符串 `"20"`，不包含参数说明或额外业务包装。

本轮没有真实创建任务；运行 API 调用与内部轮询由上述离线测试验证。正式 Dify 插件及真实任务完整执行仍未端到端验证。

v0.8 补充验证：浏览器读取当前选中模板详情 HTTP 200，点击“复制全部输出”并整体粘贴到自定义参数 JSON，确认保留 `text/json/files` 完整结构及新的字段提示，查看模式没有自动回填。两个工具提取 `json[0]` 后生成正确运行请求的行为由离线测试验证；本次仍未真实启动任务。页面效果见 [完整输出粘贴截图](full-output-paste.png)。

最新方案同步验证：页面默认“查看参数”、等待超时 600 秒；真实地区接口返回 37 个地区，默认选择 `USA · US`。Google Maps Scraper 查看详情 HTTP 200，代理和超时留空、业务 JSON 非法时仍可查看；切到运行模式后空代理被启动前校验拦截。服务日志只有列表、地区、详情 GET，没有创建任务 POST。嵌套对象递归合并、数组替换及后端地区校验由上述 20 项离线测试验证；未真实运行任务或实际等待 600 秒。当前页面见 [最新默认配置截图](latest-plan-settings.png)。
