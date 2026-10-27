"""Reuse approved mock chrome, with a real two-tool frontend and no sample data."""

import argparse
from pathlib import Path

from english_copy import english_markup

parser = argparse.ArgumentParser()
parser.add_argument("fragment", type=Path)
args = parser.parse_args()
original = args.fragment.read_text(encoding="utf-8")
page = original[:original.index('<script type="application/json" id="ba-catalog-data">')]
page += original[original.index('<style>', original.index('id="ba-catalog-data"')):original.index('<script>')]


def replace(old, new):
    global page
    if old not in page:
        raise ValueError("Missing source markup: " + old[:80])
    page = page.replace(old, new)


start = page.index('  <div class="ba-preview-bar">')
end = page.index('  <div class="ba-window">', start)
page = page[:start] + '''  <div class="ba-preview-bar">
    <div><strong>BrowserAct 工具入口</strong><span class="ba-preview-caption">真实 API · 本机演示 · 非 Dify 运行环境</span></div>
    <div id="ba-tool-picker" role="group" aria-label="选择 BrowserAct 工具"></div>
    <span class="ba-preview-caption" id="ba-api-evidence" aria-live="polite">请配置连接并加载列表</span>
  </div>
''' + page[end:]
replace('value="ba_demo_review_only"', 'value="" placeholder="填写 BrowserAct API Key"')
replace('在插件连接中配置，节点复用此连接。', 'Key 仅在当前页面和请求内存中使用；不保存到文件或浏览器存储。')
replace('演示连接', '未连接')
replace('草稿</span>', '本机演示</span>')
replace('测试运行</button>', '运行当前工具</button>')
replace('              <div class="ba-help" id="ba-key-help">Key 仅在当前页面和请求内存中使用；不保存到文件或浏览器存储。</div>', '              <div class="ba-help" id="ba-key-help">仅用于本机真实 API 演示，不属于 Dify 节点。实际凭据由插件授权管理；Key 不保存到文件或浏览器存储。</div><button type="button" class="ba-button" id="ba-connect">加载演示列表</button>')
start = page.index('            <div class="ba-auth-block">')
end = page.index('            <div class="ba-fields">', start)
connection = page[start:end].replace('class="ba-auth-block"', 'class="ba-demo-connection" id="ba-demo-connection" aria-label="本机演示连接设置"')
connection = connection.replace('授权连接</span>', '本机演示连接设置 · 非 Dify 控件</span>')
page = page[:start] + page[end:]
page = page.replace('  <div class="ba-window">', connection + '  <div class="ba-window">', 1)
start = page.index('              <div class="ba-field"><label class="ba-label" for="ba-source">')
end = page.index('              <div class="ba-field"><label class="ba-label" for="ba-bot">', start)
page = page[:start] + page[end:]
start = page.index('              <div class="ba-field"><label class="ba-label" for="ba-region">')
end = page.index('              <div class="ba-field"><label class="ba-label" for="ba-timeout">', start)
page = page[:start] + '<div id="ba-region-slot"></div>\n' + page[end:]
replace('点击“运行此步骤”读取说明和默认 JSON，不创建任务。', '查看参数只返回配置 JSON，不创建任务；运行 Bot 会真实创建任务并使用账户额度。')
replace('查看模式：text 为参数说明，json 为默认参数对象。', '查看参数后点击“复制全部输出”，粘贴到自定义参数 JSON；修改 json[0] 中的配置，运行时自动提取。')
replace('填写需要覆盖的参数；留空或 {} 使用 Bot 默认值。', '粘贴完整输出并修改 json[0]，也可填写参数对象。对象逐层合并，数组整体替换；未填写的字段保留默认值。')
replace('value="120" required aria-describedby="ba-timeout-help"', 'value="600" aria-describedby="ba-timeout-help"')
replace('本节点等待结果的上限。120 秒仅为演示值。', '默认 600 秒；仅运行时使用。到期结束节点等待，保留 task_id，不取消远端任务。')
replace('查看输入参数，或运行 Bot 并等待完成结果。', '查看可复制的参数配置，或运行 Bot 并等待完成结果。')
start = page.index('                <div class="ba-input-modes"')
end = page.index('                <textarea id="ba-input"', start)
page = page[:start] + page[end:]
start = page.index('                <div class="ba-variable-binding" id="ba-variable-binding"')
end = page.index('\n', start)
page = page[:start] + page[end:]
page += '''<style>
#ba-dify-review .ba-preview-bar{padding-right:0}
#ba-dify-review #ba-tool-picker button[aria-pressed="true"]{background:var(--ba-blue);color:light-dark(#fff,#101d37);border-color:var(--ba-blue)}
#ba-dify-review .ba-demo-connection{display:grid;grid-template-columns:70px minmax(120px,1fr) auto;gap:8px 12px;align-items:center;padding:14px;margin-bottom:14px;border:1px dashed var(--ba-border);border-radius:10px;background:var(--ba-bg)}
#ba-dify-review .ba-demo-connection .ba-section-heading{grid-column:1/-1;margin:0}
#ba-dify-review .ba-demo-connection .ba-label{margin:0}
#ba-dify-review #ba-key{grid-column:2;grid-row:2}
#ba-dify-review #ba-connect{grid-column:3;grid-row:2}
#ba-dify-review #ba-key-help{grid-column:1/-1;grid-row:3;margin:0}
@media(max-width:500px){#ba-dify-review .ba-demo-connection{grid-template-columns:1fr auto}#ba-dify-review .ba-demo-connection .ba-label{grid-column:1/-1}#ba-dify-review #ba-key{grid-column:1;grid-row:3}#ba-dify-review #ba-connect{grid-column:2;grid-row:3}#ba-dify-review #ba-key-help{grid-row:4}}
</style><script src="/app.js"></script>'''
header = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BrowserAct · 两个工具实时演示</title><style>html{color-scheme:light dark}body{margin:0;padding:18px;background:light-dark(#f6f7f9,#111318)}#ba-dify-review{max-width:1200px;margin:auto}</style><script src="https://unpkg.com/lucide@0.468.0/dist/umd/lucide.min.js"></script></head><body>'''
(Path(__file__).parent / "index.html").write_text(english_markup(header + page + '</body></html>\n'), encoding="utf-8")
print("Built two-tool demo; no inline sample data or credentials.")
