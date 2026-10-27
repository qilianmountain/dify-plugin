from shared.base_tool import BotTool


class RunOfficialTemplate(BotTool):
    name = "run_official_template"
    label = "Run Official Template"
    list_path = "/v3/bots/templates"
    id_field = "template_id"
    page_limit = 500
