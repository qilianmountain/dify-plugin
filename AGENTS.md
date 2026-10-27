# BrowserAct Dify 插件开发入口

2026-10-22 排障增量（20票/0.0.8）：Test03包改为独立插件ID `qilian_mountain/browseract_test03` 与Provider名 `browseract_test03`，避免复用生产身份的动态下拉凭据缓存。源码生产身份仍为browseract，接口、业务参数和输出契约不变。旧节点不自动迁移，需用户安装新包并新增测试节点及连接。当前Key与0.0.7解包客户端的真实只读列表已通过；Cloud缓存命中本身尚未直接证明，新包Cloud验收仍需用户操作。最新证据以Feature20票为准。

2026-10-22 最新增量（13/17票、0.0.7）：两个工具的 Operation 按 Run Bot、View Parameters 排列，默认 run、显式 view 及 JSON 复制解析行为保持不变。共享客户端所有请求统一携带 `api-channel-ak: difyak`，Bearer Key 不变。轮询维持心跳，超时/异常停止查询、不主动取消；服务端可能因心跳过期取消。源码保留生产 API 主机，`scripts/package-test03.py` 在隔离打包时固定 `https://api-test03.browseract.com` 并标注 BrowserAct (Test03)，不增加用户环境配置项。最新验证与包见 Feature 17 票；以下旧版本决定保留历史语义。

2026-10-21最新决定（12票/0.0.6）：两个工具默认Run Bot，显式View Parameters仍只查询；移除模板Proxy Region字段、地区请求与校验，创建请求不传顶层proxy_region；自定义参数JSON灰字说明改为查询参数及官方集成指引链接。此前默认view、模板US必填的内容属于旧版本决定，已被本次用户指令替代。详情与验证以Feature入口的12票为准。

## 权威资料

- [agent.md](agent.md)：项目上下文、当前阶段、参考仓库和证据位置。
- [首版功能设计](docs/design/04-review-design.md)：用户已确认的行为与待验证项。
- [Feature 启动记录](docs/development/01-feature-start.md)：本地初始化记录。
- [当前 Feature 开发入口](../../development/README.md)、[仓库清单](../../development/repos.yaml)：技术 Spec、分票、实际分支与验证的权威入口。
- 团队流程采用 `agent.md` 指向的 team-infra `AGENTS.md` 与 `skills/feature-start/SKILL.md`；仓库与分支方案已确认并初始化，接下来按技术 Spec 与任务确认节点继续。

## 当前范围

当前工作分支为 `feature/browseract-dify-v1`，固定基线 `92c83d4d2b4f1179258bd80e4be7fa7a1738d008`。01–04本地验证和05当前Dify Cloud远程调试验证已完成。两工具原生流程与真实运行通过，动态下拉为form: llm；600秒超时、610秒返回、输出完整性与临时链接已有证据，见[05边界报告](../../development/verification/2026-10-20-dify-cloud-boundaries.md)。单步约100秒请求超时、实时流错误可能与后台状态不同；不重复提交任务，不将远程调试结论扩展为已安装包保证。06打包与固定范围审查的最新结果以[Feature README](../../development/README.md)为准。

先在本地完成开发与测试，远程仓库尚未创建。用户允许个人 GitHub 作为后续发布位置；当前没有选定具体账号、仓库名或可见性，不自动创建远程或推送。通过测试后再安排团队交付。

正式插件与 `docs/demo/live/` 本机演示是不同产物；演示验证不能替代 Dify SDK、插件包或目标 Dify 环境验证。节点功能遵循首版设计；演示辅助控件放在模拟 Dify 窗口外，不将其视为标准插件能力。

## 验证入口

11增量（0.0.5）：完整操作指引放在两工具Custom Parameters JSON的常驻human_description；Operation、Bot/Template保留简短问号提示。演示按原生字段类型区分问号/灰字，不再把下拉说明常驻显示。其余参数和执行契约不变。

10增量（0.0.4）：插件自有文案统一英文，en_US/zh_Hans显示同一英文；Operation使用用户确认的View Parameters → Run this step → LAST RUN →复制完整输出至Custom Parameters JSON指引，目标与JSON说明按10票定稿。插件生成错误及本机演示自有文案同步英文；服务端原文、Bot名称和业务数据不翻译。参数、默认值、输出与执行行为不变，最新验证及包以Feature记录为准。

08增量：run增加Make对应的17个命名输出和文件字段树，完整json保留；view实际消息及复制流程不变。output为任意业务JSON类型，不伪造Bot特有字段结构。07/09增量（0.0.3）：用户已要求实施待改项，operation为首个form: llm输入，默认view；三种动态列表成功选项在进程内固定缓存60秒，按Key摘要、SDK user_id和来源隔离，最多128组。定义、运行前校验、任务和认证不缓存。实际Cloud升级后的顺序与已有节点模式迁移仍需安装验证，不能以SDK声明检查代替。

本机演示的现有验证：

```powershell
python -m unittest discover -s docs/demo/live -p test_server.py -v
node --check docs/demo/live/app.js
```

正式插件使用 Python 3.12.13 与 SDK 0.10.2；从本 worktree 先执行 `. ./scripts/use-local-environment.ps1`，再执行 `uv sync --locked`、`uv run python -m pytest -q` 和 `uv pip check`。本机 CLI 为 `.tools/dify.exe`；启动与打包命令、Windows 环境恢复方法见 [README.md](README.md)。API Key 不写入源码、日志、Git 或页面持久化存储。保留现有设计、证据、用户修改和本机演示。
