"""Local demo registry: both tools share credentials and their implementation core."""

from tools.run_my_bot import RunMyBot
from tools.run_official_template import RunOfficialTemplate

TOOLS = {tool.name: tool for tool in (RunMyBot(), RunOfficialTemplate())}
