# 04：Make 上的 BrowserAct 业务参数表单

核实日期：2026-10-16。通过用户指定的已登录 Edge 查看已有 Make 页面，仅观察当前节点配置，未修改、保存或运行场景，未检查 Make 集成源码。

## 界面证据

页面为 Make 的 `Integration BrowserAct` 场景，节点为 BrowserAct `Run a Bot`。当前来源为 `Template Marketplace`，所选模板为 `Google Maps No Website Lead Finder API`。

Bot 选择项下展示 `About This Bot` 说明及模板链接。`Input Parameters` 区域按业务参数分别展示控件：

| 参数 | 当前可见的表单表现 |
| --- | --- |
| `industry` | 独立下拉选项，当前值 Dentist / Dental Clinic |
| `country` | 独立下拉选项，当前值 United States |
| `location` | 独立文本输入，显示长度范围 1–160 |
| `max_results` | 独立数值输入，显示范围 5–50 |
| `min_rating` | 独立数值输入，显示上限 5 |
| `min_review_count` | 独立数值输入 |
| `exclude_chains` | 独立 Yes / No 选项 |
| `start_rank` | 独立数值输入，显示范围 1–1000 |
| `excluded_maps_urls` | 独立文本输入，显示长度范围 1–200000 |

多项字段带必填星号、业务说明；部分控件旁有 `Map` 切换。通用设置 `Proxy Region` 与 `Timeout` 位于业务参数区域之外。

本次确认了所选模板的业务字段在页面中逐项展示；未切换其他 Bot、未验证值映射、校验执行效果或运行结果，不能由此推断底层实现方式或全部 Bot 的兼容范围。

## 历史方案与最新决定

用户曾要求 Dify 参考该体验：选择 Bot 或模板后，展示对应的业务参数，每个参数单独填写。以上界面证据仍然有效。

在核对 Dify 标准插件的联动限制后，用户最新明确确认使用 JSON 输入：通用参数独立填写，业务 JSON 提供的字段覆盖 Bot 默认值。逐字段动态业务表单不再是当前首版要求。完整首版范围以 [设计记录](../design/01-tools-and-input.md) 为准。

Make 已有此界面，不等于 Dify 标准插件已支持相同的动态字段联动。限制与源码证据见 [02：Bot 选择与动态输入参数](02-bot-input-parameters.md)，本页保留为历史交互参考。
