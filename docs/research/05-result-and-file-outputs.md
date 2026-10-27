# 各平台结果与文件输出实现

核对日期：2026-10-19。范围：任务成功结果、文件链接及平台原生文件输出；不重新讨论轮询或嵌套参数合并。未启动真实任务、下载业务文件或执行竞品插件。

## 结论

BrowserAct n8n 将任务详情直接作为 JSON 返回；Zapier 将任务详情、回调内容合并返回，所查路径没有文件下载或平台文件封装。Firecrawl Dify 的 Crawl 输出 API JSON，Scrape 输出 Markdown 文本及 API JSON，所查路径没有文件消息。Tavily Dify 输出 JSON 和格式化文本，并为开启的图片、favicon 选项增加下载和 blob 文件消息；不能将它概括为“只返回链接”，也不能推断其下载所有结果文件。

R3 已由用户进一步确认“对齐我们之前的平台实现”：BrowserAct Dify 返回 API 任务详情对象，保留原字段、结构、类型及文件信息/临时链接，不按列举字段进行白名单裁剪，不下载转存为 Dify `files`。Dify 以标准 JSON 消息承载，任务详情位于 `json[0]`。对齐范围为结果与文件处理，不照搬 Zapier 回调、`timedOut` 附加字段或 n8n 超时取消；已确认的 R2 与暂停处理保持不变。Tavily 的图片文件功能不纳入首版。

## 本地源码证据

| 对象 | 核对提交 | 实现与位置 |
| --- | --- | --- |
| BrowserAct n8n | `46e4ecd1645a786797678b9ac1fc9447628b013f` | `nodes/BrowserAct/BrowserAct.node.ts:340–343` 取得任务详情，`:372–376` 返回 `{json: taskDetail, pairedItem: ...}`，该输出路径没有 `binary` 或文件下载转换 |
| BrowserAct Zapier | `4b616c19b7cef658dda00637804ac015e92d4239` | `creates/runWorkflow.js:122–126` 返回详情和 `timedOut`；`:129–156` 回调恢复合并 `outputData`、详情和 `cleanedRequest`；`:245–251` 声明任务元数据输出，未声明文件字段。所查仓库未发现文件 hydration/dehydration 或业务文件下载实现；它使用 V2 API，不能据此承诺 V3 文件字段 |
| Firecrawl Dify | `f2d7811364193f8d7069f24a299ee465c5519d3c` | `tools/firecrawl/tools/crawl.py:38–39` 以 `create_json_message(crawl_result)` 输出；`scrape.py:44–47` 追加 Markdown 文本后输出完整 JSON。所查工具代码没有 `create_blob_message` 文件转换 |
| Tavily Dify | 同上 | `tools/tavily/tools/tavily_search.py:160–182` 输出 JSON 和文本，并按图片/favicon 选项调用处理函数；`utils.py:15–28`、`:43–72` 以 `requests.get(..., timeout=10)` 下载图片，再以 `create_blob_message` 输出内容、MIME 和文件名；下载异常打印日志，不中断循环。`tavily_research.py:187–192` 的完成路径只输出 JSON 和文本 |

本地仓库位置以 [项目证据入口](../../agent.md) 为准；以上结论绑定所列提交，不声称部署平台或 Marketplace 包已逐一运行验证。

## 公开源码复核

本次还打开官方仓库 `main` 的以下文件，相关返回逻辑与本地快照一致；`main` 是可变引用，不视为固定版本或线上安装包证明：

- [Firecrawl Crawl](https://github.com/langgenius/dify-official-plugins/blob/main/tools/firecrawl/tools/crawl.py)：API JSON 输出。
- [Firecrawl Scrape](https://github.com/langgenius/dify-official-plugins/blob/main/tools/firecrawl/tools/scrape.py)：Markdown 文本及 API JSON 输出。
- [Tavily Search](https://github.com/langgenius/dify-official-plugins/blob/main/tools/tavily/tools/tavily_search.py)：JSON、文本及条件图片处理。
- [Tavily 图片处理](https://github.com/langgenius/dify-official-plugins/blob/main/tools/tavily/tools/utils.py)：下载图片/favicon 并创建 blob 消息。

文件 URL 留在 JSON 中与转成 Dify 文件是两种不同输出：前者交给下游自行获取，后者需要插件读取二进制内容并创建文件消息。本次比较不把 Tavily 的搜索图片等同于 BrowserAct 任意 CSV、Excel、PDF 或压缩包任务文件。
