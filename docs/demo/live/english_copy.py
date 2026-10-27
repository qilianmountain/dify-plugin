"""Translate legacy mock markup when regenerating the English local demo."""

from html import escape
import re

OPERATION_HELP = 'Choose View Parameters to inspect defaults, or Run Bot to execute.'
JSON_HELP = 'Select a Bot or template, then choose View Parameters to inspect its inputs. For setup and usage instructions, see https://docs.browseract.com/integrations/integration-overview'

TRANSLATIONS = {
    '仅用于本机真实 API 演示，不属于 Dify 节点。实际凭据由插件授权管理；Key 不保存到文件或浏览器存储。': 'For this local live API demo only, outside the Dify node. Dify manages plugin credentials. The Key is not saved to files or browser storage.',
    '查看参数只返回配置 JSON，不创建任务；运行 Bot 会真实创建任务并使用账户额度。': 'Select a Bot or template and choose View Parameters. Click ▶ Run this step in the upper-right corner to retrieve its parameters. Then open the LAST RUN tab, copy the full output, and paste it into Custom Parameters JSON.',
    '查看参数后点击“复制全部输出”，粘贴到自定义参数 JSON；修改 json[0] 中的配置，运行时自动提取。': 'After viewing parameters, copy the full output into Custom Parameters JSON. Edit json[0]; the configuration is extracted when running.',
    '粘贴完整输出并修改 json[0]，也可填写参数对象。对象逐层合并，数组整体替换；未填写的字段保留默认值。': 'Edit the parameter values in the JSON to customize the inputs.',
    '默认 600 秒；仅运行时使用。到期结束节点等待，保留 task_id，不取消远端任务。': 'Default: 600 seconds. A timeout ends waiting and retains task_id. The plugin sends no cancellation request; the server may cancel the task after its heartbeat expires.',
    '查看可复制的参数配置，或运行 Bot 并等待完成结果。': 'View the parameter configuration to copy, or run a Bot and wait for its results.',
    '本机演示连接设置 · 非 Dify 控件': 'Local Demo Connection · Outside Dify',
    '真实 API · 本机演示 · 非 Dify 运行环境': 'Live API · Local Demo · Outside the Dify Runtime',
    '请配置连接并加载列表': 'Configure the connection and load the lists',
    '选择后使用对应 Bot ID 执行。': 'Select one of your custom Bots.',
    '选择 Run a Bot 节点': 'Select the Run a Bot node',
    '选择 BrowserAct 工具': 'Select a BrowserAct tool',
    'BrowserAct 工具入口': 'BrowserAct Tools',
    'BrowserAct 集成': 'BrowserAct Integration',
    'BrowserAct · 工具': 'BrowserAct · Tool',
    'BrowserAct Dify 节点交互原型': 'BrowserAct Dify Node Prototype',
    '两个工具实时演示': 'Two-Tool Live Demo',
    '填写 BrowserAct API Key': 'Enter your BrowserAct API Key',
    '本机演示连接设置': 'Local Demo Connection',
    '等待超时（秒）': 'Wait Timeout (seconds)',
    '自定义参数 JSON': 'Custom Parameters JSON',
    '加载演示列表': 'Load Demo Lists',
    '运行当前工具': 'Run Current Tool',
    '模拟工作流画布': 'Mock Workflow Canvas',
    '工作流编排': 'Workflow Editor',
    '选择节点以编辑配置': 'Select a node to edit its configuration',
    '等待上游节点': 'Waiting for the upstream node',
    '输入变量': 'Input Variables',
    '输出变量': 'Output Variables',
    '操作模式': 'Operation',
    '运行时校验': 'Validated when running',
    '节点配置': 'Node Configuration',
    '节点面板': 'Node Panel',
    '应用导航': 'App Navigation',
    '用户输入': 'User Input',
    '本机演示': 'Local Demo',
    '查看参数': 'View Parameters',
    '运行 Bot': 'Run Bot',
    '运行此步骤': 'Run this step',
    '未连接': 'Not Connected',
    '未运行': 'Not Run',
    '上次运行': 'LAST RUN',
    '工作室': 'Studio',
    '编排': 'Editor',
    '监测': 'Monitor',
    '日志': 'Logs',
    '设置': 'Settings',
    '个节点': 'nodes',
    '选填': 'Optional',
    '输出': 'Output',
}


def english_markup(markup):
    for old, new in sorted(TRANSLATIONS.items(), key=lambda item: -len(item[0])):
        markup = markup.replace(old, new)
    markup = markup.replace('for="ba-bot">Bot ', 'for="ba-bot"><span id="ba-target-label">Bot</span> ')
    markup = markup.replace('lang="zh-CN"', 'lang="en"')
    markup = markup.replace('<div id="ba-region-slot"></div>', '')
    markup = markup.replace('<option value="view" selected>', '<option value="view">').replace('<option value="run">', '<option value="run" selected>')
    markup = markup.replace('<option value="view">View Parameters</option><option value="run" selected>Run Bot</option>', '<option value="run" selected>Run Bot</option><option value="view">View Parameters</option>')
    return native_help_markup(markup)


def native_help_markup(markup):
    # Match Dify's presentation rule without claiming an actual Dify runtime.
    for field, help_id, description in (
        ('ba-operation', 'ba-operation-help', OPERATION_HELP),
        ('ba-bot', 'ba-bot-help', 'Select one of your custom Bots.'),
    ):
        markup = re.sub(r'<div class="ba-help" id="' + help_id + r'">.*?</div>', '', markup)
        markup = re.sub(r'<span class="ba-tooltip" id="' + help_id + r'"[^>]*>\?</span>', '', markup)
        hint = (f'<span class="ba-tooltip" id="{help_id}" tabindex="0" '
                f'title="{escape(description, quote=True)}" aria-label="{escape(description, quote=True)}">?</span>')
        markup = re.sub(r'(<label class="ba-label" for="' + field + r'">.*?)(</label>)',
                        lambda match: match[1] + hint + match[2], markup)
    markup = re.sub(r'<div class="ba-help" id="ba-json-help">.*?</div>', '', markup)
    markup = re.sub(r'(<label class="ba-label" for="ba-input">.*?</label>)',
                    lambda match: match[1] + '<div class="ba-help" id="ba-json-help">' + escape(JSON_HELP).replace('https://docs.browseract.com/integrations/integration-overview', '<a href="https://docs.browseract.com/integrations/integration-overview" target="_blank" rel="noopener noreferrer">https://docs.browseract.com/integrations/integration-overview</a>') + '</div>', markup)
    markup = re.sub(r'<style id="ba-native-help-style">.*?</style>', '', markup)
    style = ('<style id="ba-native-help-style">#ba-dify-review .ba-tooltip{display:inline-flex;'
             'align-items:center;justify-content:center;width:13px;height:13px;margin-left:6px;'
             'border:1px solid var(--ba-muted);border-radius:50%;font-size:10px;font-weight:400;'
             'line-height:1;color:var(--ba-muted);cursor:help;vertical-align:middle}</style>')
    markup = re.sub(r'(?m)^[ \t]+$', '', markup)
    return markup.replace('</head>', style + '</head>', 1)
