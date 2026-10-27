from shared.base_tool import BotTool


class RunMyBot(BotTool):
    name = "run_my_bot"
    label = "Run My Bot"
    list_path = "/v3/bots"
    id_field = "bot_id"
    page_limit = 100
