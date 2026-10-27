# BrowserAct Bot 与官方模板：真实 API 返回

核实日期：2026-10-19（Asia/Shanghai）。使用用户提供的 API Key 进行只读认证查询；凭据没有保存在这些证据文件中。未创建、运行、取消或修改任务。

## 查询范围

- `GET /v3/bots?page=1&limit=100`：账号下有 2 个可运行的已发布 Bot，`total_pages=1`；两个详情均已查询。
- `GET /v3/bots/templates?page=1&limit=500`：官方模板共 408 个，`total_pages=1`；抽查其中 6 个详情，没有查询全部 408 个模板详情。
- Bot 详情：`GET /v3/bots/{bot_id}`。
- 模板详情：`GET /v3/bots/templates/{template_id}`。
- 以下 8 个详情请求均返回 HTTP 200。证据只证明本次账号可见范围和样本，不保证所有 Bot 均有说明、默认值或同样的字段约束。

## 原始响应与可复制默认参数

“说明数”统计非空的顶层参数 `description`；“默认值数”按 `default` 字段是否存在统计，不按值的真假判断。默认参数 JSON 是从真实 `input_schema.properties` 提取生成的派生文件，不是 API 单独返回的字段。

| 来源 | 名称 | 类型 | 参数数 | 说明数 | 默认值数 | 必填数 | 原始响应 | 默认参数 JSON |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| 我的 Bot | google search | workflow | 1 | 1 | 1 | 0 | [完整响应](bot-91728565825850643.json) | [默认参数](bot-91728565825850643-defaults.json) |
| 我的 Bot | Bot-0914-01 | agent | 1 | 1 | 1 | 0 | [完整响应](bot-118154167847668957.json) | [默认参数](bot-118154167847668957-defaults.json) |
| 官方模板 | Google Maps No Website Lead Finder API | agent | 9 | 9 | 9 | 9 | [完整响应](template-117700557239492064.json) | [默认参数](template-117700557239492064-defaults.json) |
| 官方模板 | Google Maps Scraper | workflow | 4 | 0 | 4 | 0 | [完整响应](template-54054669770646127.json) | [默认参数](template-54054669770646127-defaults.json) |
| 官方模板 | Website Data Scrape | workflow | 1 | 1 | 1 | 0 | [完整响应](template-54602233871863413.json) | [默认参数](template-54602233871863413-defaults.json) |
| 官方模板 | Amazon Product Reviews Scraper Bot | agent | 3 | 3 | 3 | 3 | [完整响应](template-113863425622286759.json) | [默认参数](template-113863425622286759-defaults.json) |
| 官方模板 | Reddit Scraper | workflow | 2 | 0 | 2 | 0 | [完整响应](template-57685316630221694.json) | [默认参数](template-57685316630221694-defaults.json) |
| 官方模板 | YouTube Transcript Scraper | agent | 1 | 1 | 1 | 1 | [完整响应](template-113863461617804199.json) | [默认参数](template-113863461617804199-defaults.json) |

结构化汇总见 [summary.json](summary.json)，统计见 [stats.json](stats.json)，八个完整详情的合并版见 [all-detail-responses.json](all-detail-responses.json)。原始响应文件保存成功响应正文，未添加 Dify 的 `text/json/files` 包装。

## 对输入方案的影响

1. 这 8 个样本均提供 `input_schema`，22 个顶层参数均有 `default`，其中 16 个有非空 `description`。API 可以支持提取默认参数并显示已存在的说明；不是所有字段都有说明。
2. `required` 与 `default` 可以同时存在。Google Maps No Website Lead Finder API 的 9 个参数都必填且都有默认值；插件合并默认值后仍应依据完整输入校验。
3. 字段类型必须保留。Google Maps Scraper 的 `datalimit` 为字符串 `"20"`，Reddit Scraper 的 `Total_Comments` 为字符串 `"10"`；Agent 模板则存在 integer、number、boolean，不能统一转换成字符串或数字。
4. 字段名区分大小写，例如 `URL`、`Area`、`Keyword`、`TargetURL`。Google Maps No Website Lead Finder API 的 `excluded_maps_urls` 默认值是字符串 `"None"`，不是 JSON `null`。Website Data Scrape 的 `websitelink` 默认值含前导空格，证据文件按原值保留。
5. 参数还可能包含 `enum`、`minimum`、`maximum`、`minLength`、`maxLength`、`pattern` 等约束。展示参数时不应只展示名称和默认值。
6. 实测普通 Bot 返回 `bot_id` 和 `output_schema`（允许 null）；本次模板详情返回 `template_id`、`recommend_desc`、`detail_url`，没有 `output_schema` 字段。不能把“缺少字段”和“显式 null”混为一谈。
7. 模板的整体 `description` 很长，本次样本约 9,000–37,000 字符；完整正文保存在原始文件。参数帮助应优先使用各参数自己的 `description`，不能用模板整体介绍代替。
8. 本次只验证 BrowserAct API 数据能力，不证明 Dify 配置界面支持选择 Bot 后自动回填或动态展示。2026-10-19 用户已确认同一节点内提供“查看参数 / 运行 Bot”，查看模式输出参数说明和可复制默认参数 JSON，见 [已确认功能范围](../../../design/01-tools-and-input.md)；这是一项后续产品决定，尚未实现或进行 Dify 联调，不是本次 API 验证已证明的界面能力。
9. 同日按 Dify 源码修正展示方案：完整输出在单个原生只读 JSON 编辑器中显示，说明在 `text` 字符串、默认参数在 `json[0]`；原生按钮复制全部输出，用户手动提取参数对象。原型不再提供独立参数列表、默认 JSON 框或折叠说明。该 UI 结论来自 [Dify 源码调研](../../02-bot-input-parameters.md#原生结果编辑器与插件输出的边界)，不属于本组 BrowserAct 接口实测结论。
