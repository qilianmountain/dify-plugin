import re
import time
from urllib.parse import urlencode

from shared.client import ApiError
from shared.parameters import default_inputs, input_schema, merge_inputs


class BotTool:
    """Executable local tool service; not a Dify SDK Tool or plugin package."""

    def list_options(self, client):
        page, total_pages, options = 1, 1, []
        while page <= total_pages:
            data = client.request("GET", self.list_path + "?" + urlencode({"page": page, "limit": self.page_limit}))
            if not isinstance(data, dict) or not isinstance(data.get("items"), list):
                raise ApiError("The list API returned an invalid response.", 502)
            for item in data["items"]:
                if self.id_field == "bot_id" and not item.get("published_at"):
                    continue
                options.append({"label": item.get("name", "Untitled"), "value": str(item[self.id_field])})
            total_pages = max(1, int(data.get("total_pages", 1)))
            page += 1
        return options

    def definition_path(self, target_id):
        if not isinstance(target_id, str) or not re.fullmatch(r"[0-9]+", target_id):
            raise ApiError("Select a valid Bot or template.")
        return self.list_path + "/" + target_id

    def invoke(self, client, parameters):
        mode = parameters.get("operation", "run")
        if mode not in ("view", "run"):
            raise ApiError("Operation must be View Parameters or Run Bot.")
        path = self.definition_path(parameters.get("target_id"))
        detail = client.request("GET", path)
        if not isinstance(detail, dict) or str(detail.get(self.id_field, "")) != parameters["target_id"]:
            raise ApiError("The returned target ID does not match the selected target.", 502)
        schema = input_schema(detail)
        if mode == "view":
            # Return only the editable configuration; no descriptions or wrappers.
            return {"text": "", "json": [default_inputs(schema)], "files": []}
        raw_timeout = parameters.get("timeout", 600)
        if type(raw_timeout) not in (int, float) or raw_timeout != int(raw_timeout) or raw_timeout <= 0:
            raise ApiError("Wait Timeout must be a positive integer in seconds.")
        body = {"input": merge_inputs(schema, parameters.get("input_json", "{}"))}
        created = client.request("POST", path + "/runs", body)
        task_id = str(created.get("task_id", ""))
        if not re.fullmatch(r"[0-9]+", task_id):
            raise ApiError("No valid task_id was returned. Check BrowserAct before resubmitting.", 502)
        deadline = time.monotonic() + raw_timeout
        try:
            while True:
                status = client.request("GET", f"/v3/bots/runs/{task_id}/status", timeout=deadline-time.monotonic())
                if status.get("status") in ("pausing", "paused"):
                    raise ApiError("The task is paused or pausing: " + status["status"] + ". Waiting has ended; the remote task was not automatically resumed.")
                if status.get("status") in ("finished", "failed", "canceled", "pausing", "paused"):
                    result = client.request("GET", f"/v3/bots/runs/{task_id}", timeout=deadline-time.monotonic())
                    if result.get("status") != "finished":
                        raise ApiError("The task did not complete successfully: " + str(result.get("status")) + "; " + str(result.get("task_failure_info", "")))
                    return {"text": "Bot execution completed", "json": [result], "files": []}
                if status.get("status") not in ("created", "running"):
                    raise ApiError("Unknown task status: " + str(status.get("status")))
                time.sleep(min(3, max(0, deadline-time.monotonic())))
        except ApiError as error:
            raise ApiError(str(error) + f"; task_id={task_id}. The plugin sent no cancellation request; the server may cancel the task after its heartbeat expires.", error.status) from None
