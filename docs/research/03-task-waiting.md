# 03：Firecrawl 与 Apify 如何等待任务完成

核实日期：2026-10-16。范围：插件与 SDK 源码/官方说明，未执行真实采集或 Dify 联调。

决策状态：用户已确认采用插件内部轮询模式。当前仅确定 `Run a Bot` 节点功能；本文源码细节作为后续技术方案与评审的参考，不要求现在逐项确认轮询、超时和重试参数。

## 结论

两者在等待模式下均采用“启动任务，内部查询直到终态”的思路，但等待放置位置与查询方式不同：

| 项目 | 启动与等待 | 查询方式 | 完成返回 |
| --- | --- | --- | --- |
| Firecrawl Crawl | 插件的 `crawl_url` 启动，再调用 `_monitor_job_status` | 插件显式 GET 查询，未结束则默认 sleep 5 秒 | 返回 completed 的查询响应；failed 抛错 |
| Apify Run Actor | 插件调用 `actor_client.call()` | SDK 内部先 start，再 wait_for_finish；当前 SDK 使用带 waitForFinish 的 GET 长轮询 | 返回终态 Run 对象，不等于直接读取数据集条目 |

BrowserAct 当前首版只有同步 `Run a Bot`。采用插件内部查询状态、成功后获取任务详情与结果的方式，与上述模式一致；同步是 Dify 用户观察到的节点行为，不要求 BrowserAct 启动 API 同步阻塞。

## Firecrawl 的实际代码

参考官方插件本地提交 `f2d7811364193f8d7069f24a299ee465c5519d3c`：

- `tools/firecrawl/tools/crawl.py` 将 `wait_for_results` 传入 `app.crawl_url`，之后生成 JSON 输出。
- `firecrawl_appx.py:76` 的 `crawl_url` POST `/v2/crawl`，拿到 job ID 后进入等待。
- `:93` 的 `check_crawl_status` GET `/v2/crawl/{job_id}`。
- `:135` 的 `_monitor_job_status` 使用 `while True`：completed 返回，failed 抛错，其余状态 sleep；默认间隔来自 `crawl_url` 的 `poll_interval=5`。
- 这个等待循环没有显式总截止时间，也没有在该路径自动调用取消接口。`:27` 的 HTTP helper 使用 `requests.request`，未显式设置请求 timeout；请求重试与 sleep 不构成总等待上限。

这里限定为 Crawl 操作；Search、Scrape 等单次 API 调用不应被统一描述成创建任务后轮询。

证据：[Crawl 入口](https://github.com/langgenius/dify-official-plugins/blob/f2d7811364193f8d7069f24a299ee465c5519d3c/tools/firecrawl/tools/crawl.py)、[任务创建/查询](https://github.com/langgenius/dify-official-plugins/blob/f2d7811364193f8d7069f24a299ee465c5519d3c/tools/firecrawl/tools/firecrawl_appx.py#L76-L105)、[循环](https://github.com/langgenius/dify-official-plugins/blob/f2d7811364193f8d7069f24a299ee465c5519d3c/tools/firecrawl/tools/firecrawl_appx.py#L135-L142)。

## Apify：等待封装在 SDK

插件提交 `4ea5006d53236eeec12474b59d57b1416bc30fe0`：

- `tools/run_actor.py:106` 在等待模式使用 `actor_client.call(run_input=run_input, **filtered_options)`；插件文件没有自己写状态轮询循环。
- 插件的 timeout 选项转换为 SDK 的 `run_timeout`，限制远端 Actor 运行时间；没有将它作为 SDK 的 `wait_duration`。因此不能把界面 timeout 直接等同于插件总等待期限。
- `requirements.txt` 声明 `apify-client>=3.0.0,<4.0.0`。本次没有获取 Marketplace 包内实际锁定的安装版本，不能断言所有发布安装均使用下面的 SDK 快照。

SDK `master` 本次核实提交 `9fb576cfd2bea935f17691b95bc3d602dbde4b3d`：

- `_resource_clients/actor.py` 的 `call()` 调用 `start()`，再构造 run client，执行 `wait_for_finish(wait_duration=wait_duration)`。
- `_resource_clients/run.py:140` 将等待交给 `_wait_for_finish`。
- `_resource_clients/_resource_client.py:312` 的 `_wait_for_finish` 循环 GET，带 `waitForFinish` 参数让服务端等待一段时间；检查终态或总 deadline，未结束再查询。循环间的 0.25 秒 sleep 是客户端重查间隔，不应说成每 0.25 秒固定产生一次状态请求，因为请求本身包含服务端等待。
- `wait_duration` 可限制客户端总等待；不传时没有该总 deadline。该等待函数没有自动 abort 远端任务的调用。
- Run 对象包含任务状态、数据集等引用；插件还提供独立的数据集读取工具。不能把返回 Run 对象描述为已经读取全部采集数据。

证据：[插件等待调用](https://github.com/apify/apify-dify-integration/blob/4ea5006d53236eeec12474b59d57b1416bc30fe0/tools/run_actor.py#L75-L111)、[SDK Actor 实现](https://github.com/apify/apify-client-python/blob/9fb576cfd2bea935f17691b95bc3d602dbde4b3d/src/apify_client/_resource_clients/actor.py)、[SDK 等待循环](https://github.com/apify/apify-client-python/blob/9fb576cfd2bea935f17691b95bc3d602dbde4b3d/src/apify_client/_resource_clients/_resource_client.py#L312-L382)、[官方等待说明](https://docs.apify.com/api/client/python/docs/concepts/convenience-methods)。

## BrowserAct 的建议执行链路

```text
解析及校验参数
 → 调用 Bot 或官方模板运行接口，取得 task_id
 → 查询轻量 status API
 → 尚在执行则间隔等待并继续查询
 → finished 时获取任务详情与业务结果
 → 将结果转换为 Dify 输出，结束工具节点
```

以上细化已确认的同步等待方向。不是“查询 API 返回了 HTTP 响应就结束”，而是依据业务状态判断任务是否结束。failed、canceled、paused 和请求异常需要明确退出或处理策略，不无限轮询；paused 的具体行为仍待确认。

轮询间隔、单次 HTTP 超时、总等待上限、重试策略与超时后的远端取消策略仍待确认。参考 Firecrawl 的循环结构，不直接继承其缺少总等待上限和请求 timeout 的做法。目标 Dify 环境也有独立执行限制，插件设置不能绕过平台限制。
