"""Offline service/transport checks. Never create real BrowserAct tasks."""

import contextlib
import io
import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch

import server
from provider import TOOLS
from shared.client import ApiError, BrowserActClient
from shared.parameters import default_inputs, merge_inputs


class FakeClient:
    def __init__(self, test, responses):
        self.test, self.responses, self.calls, self.bodies = test, list(responses), [], []
        self.timeouts = []

    def request(self, method, path, body=None, timeout=30):
        expected_method, expected_path, result = self.responses.pop(0)
        self.test.assertEqual((method, path), (expected_method, expected_path))
        self.calls.append({"method": method, "path": path, "status": 200})
        self.bodies.append(body)
        self.timeouts.append(timeout)
        return result


class ToolTests(unittest.TestCase):
    def test_omitted_operation_runs_both_tools_without_region(self):
        for tool in TOOLS.values():
            with self.subTest(tool=tool.name):
                final = {"task_id": "10", "status": "finished"}
                client = FakeClient(self, [
                    ("GET", tool.list_path + "/1", {tool.id_field: "1", "input_schema": {}}),
                    ("POST", tool.list_path + "/1/runs", {"task_id": "10"}),
                    ("GET", "/v3/bots/runs/10/status", final),
                    ("GET", "/v3/bots/runs/10", final),
                ])
                result = tool.invoke(client, {"target_id": "1", "proxy_region": "legacy"})
                self.assertEqual(client.bodies[1], {"input": {}})
                self.assertEqual(result["json"], [final])

    def test_two_registered_tools_have_distinct_fixed_sources(self):
        self.assertEqual(set(TOOLS), {"run_my_bot", "run_official_template"})

    def test_personal_list_paginates_and_excludes_unpublished(self):
        client = FakeClient(self, [
            ("GET", "/v3/bots?page=1&limit=100", {"items": [{"bot_id": "1", "name": "A", "published_at": "now"}], "total_pages": 2}),
            ("GET", "/v3/bots?page=2&limit=100", {"items": [{"bot_id": "2", "name": "B", "published_at": "now"}, {"bot_id": "3", "name": "draft"}], "total_pages": 2}),
        ])
        self.assertEqual([item["value"] for item in TOOLS["run_my_bot"].list_options(client)], ["1", "2"])
        self.assertFalse(client.responses)

    def test_template_list_uses_template_endpoint(self):
        client = FakeClient(self, [("GET", "/v3/bots/templates?page=1&limit=500", {"items": [{"template_id": "9", "name": "T"}], "total_pages": 1})])
        self.assertEqual(TOOLS["run_official_template"].list_options(client), [{"label": "T", "value": "9"}])

    def test_view_returns_only_copyable_defaults_and_ignores_run_inputs(self):
        for tool in TOOLS.values():
            with self.subTest(tool=tool.name):
                detail = {tool.id_field: "1", "description": "Do not return", "input_schema": {"type": "object", "required": ["missing"], "properties": {
                    "Area": {"type": "string", "default": "Los Angeles", "description": "Do not return"},
                    "datalimit": {"type": "string", "default": "20"}, "zero": {"default": 0},
                    "flag": {"default": False}, "empty": {"default": ""}, "missing": {"type": "string"}}}}
                client = FakeClient(self, [("GET", tool.list_path + "/1", detail)])
                result = tool.invoke(client, {"operation": "view", "target_id": "1", "input_json": "not-json", "timeout": "invalid", "proxy_region": "invalid"})
                self.assertEqual(result, {"text": "", "json": [{"Area": "Los Angeles", "datalimit": "20", "zero": 0, "flag": False, "empty": ""}], "files": []})
                self.assertEqual(len(client.calls), 1)

    def test_missing_schema_fails_and_empty_schema_returns_empty_config(self):
        tool = TOOLS["run_my_bot"]
        for schema in [None, {"type": "object", "properties": {}}]:
            client = FakeClient(self, [("GET", "/v3/bots/1", {"bot_id": "1", "input_schema": schema})])
            if schema is None:
                with self.assertRaises(ApiError): tool.invoke(client, {"operation": "view", "target_id": "1"})
            else:
                self.assertEqual(tool.invoke(client, {"operation": "view", "target_id": "1"})["json"], [{}])

    def test_merge_preserves_types_and_merges_nested_objects(self):
        schema = {"properties": {"flag": {"type": "boolean", "default": True}, "nested": {"type": "object", "default": {"a": 1}}}}
        self.assertEqual(merge_inputs(schema, '{"flag":false,"nested":{"b":2}}'), {"flag": False, "nested": {"a": 1, "b": 2}})
        self.assertEqual(default_inputs(schema)["nested"], {"a": 1})

    def test_recursive_merge_preserves_required_defaults_and_replaces_arrays(self):
        schema = {"type": "object", "properties": {"filters": {"type": "object",
            "default": {"category": "restaurant", "options": {"limit": 10, "active": True}, "tags": ["a", "b"]},
            "required": ["category"], "properties": {"category": {"type": "string"}}}}}
        copied = {"text": "", "json": [{"filters": {"options": {"limit": 0, "active": False}, "tags": [], "empty": "", "nullable": None}}], "files": []}
        self.assertEqual(merge_inputs(schema, json.dumps(copied)), {"filters": {"category": "restaurant",
            "options": {"limit": 0, "active": False}, "tags": [], "empty": "", "nullable": None}})
        merged = merge_inputs(schema, '{"filters":{}}')
        self.assertEqual(merged["filters"], schema["properties"]["filters"]["default"])
        merged["filters"]["options"]["limit"] = 99
        self.assertEqual(schema["properties"]["filters"]["default"]["options"]["limit"], 10)
        with self.assertRaisesRegex(ApiError, "category"):
            merge_inputs({"properties": {"filters": {"required": ["category"]}}}, '{"filters":{"limit":20}}')

    def test_full_output_roundtrip_uses_only_config_for_both_tools(self):
        for tool in TOOLS.values():
            with self.subTest(tool=tool.name):
                detail = {tool.id_field: "1", "input_schema": {"type": "object", "properties": {
                    "Area": {"type": "string", "default": "Los Angeles"},
                    "datalimit": {"type": "string", "default": "20"}}}}
                client = FakeClient(self, [("GET", tool.list_path + "/1", detail)])
                copied = tool.invoke(client, {"operation": "view", "target_id": "1"})
                copied["json"][0]["Area"] = "New York"
                copied["text"], copied["files"] = "ignored", [{"url": "ignored"}]
                final = {"task_id": "10", "status": "finished"}
                responses = [("GET", tool.list_path + "/1", detail)]
                client = FakeClient(self, responses + [
                    ("POST", tool.list_path + "/1/runs", {"task_id": "10"}),
                    ("GET", "/v3/bots/runs/10/status", {"status": "finished"}),
                    ("GET", "/v3/bots/runs/10", final)])
                tool.invoke(client, {"operation": "run", "target_id": "1", "input_json": json.dumps(copied), "proxy_region": "US"})
                expected = {"input": {"Area": "New York", "datalimit": "20"}}
                self.assertEqual(client.bodies[1], expected)


    def test_default_timeout_gives_polling_a_600_second_budget(self):
        tool = TOOLS["run_my_bot"]
        final = {"task_id": "10", "status": "finished"}
        client = FakeClient(self, [("GET", "/v3/bots/1", {"bot_id": "1", "input_schema": {}}),
            ("POST", "/v3/bots/1/runs", {"task_id": "10"}),
            ("GET", "/v3/bots/runs/10/status", {"status": "finished"}), ("GET", "/v3/bots/runs/10", final)])
        with patch("shared.base_tool.time.monotonic", side_effect=[100, 101, 102]):
            tool.invoke(client, {"operation": "run", "target_id": "1"})
        self.assertEqual(client.timeouts[2], 599)

    def test_pause_ends_polling_immediately_without_fetching_detail_or_canceling(self):
        tool = TOOLS["run_my_bot"]
        for state in ["pausing", "paused"]:
            client = FakeClient(self, [("GET", "/v3/bots/1", {"bot_id": "1", "input_schema": {}}),
                ("POST", "/v3/bots/1/runs", {"task_id": "10"}),
                ("GET", "/v3/bots/runs/10/status", {"status": state})])
            with self.assertRaisesRegex(ApiError, state + r".*task_id=10"):
                tool.invoke(client, {"operation": "run", "target_id": "1"})
            self.assertEqual(len(client.calls), 3)

    def test_full_output_merge_preserves_values_and_plain_input(self):
        schema = {"properties": {"unchanged": {"default": 5}, "flag": {"default": True}}}
        config = {"flag": False, "zero": 0, "empty": "", "nested": {"json": [1]}}
        self.assertEqual(merge_inputs(schema, json.dumps({"text": "", "json": [config], "files": []})),
                         {"unchanged": 5, **config})
        self.assertEqual(merge_inputs(schema, '{"json":[1]}'), {"unchanged": 5, "flag": True, "json": [1]})
        self.assertEqual(merge_inputs(schema, '{}'), {"unchanged": 5, "flag": True})

    def test_malformed_full_output_never_creates_task(self):
        tool = TOOLS["run_my_bot"]
        for entries in [[], [{}, {}], ["not an object"], {}, None]:
            with self.subTest(entries=entries):
                client = FakeClient(self, [("GET", "/v3/bots/1", {"bot_id": "1", "input_schema": {}})])
                with self.assertRaisesRegex(ApiError, "full Dify output"):
                    tool.invoke(client, {"operation": "run", "target_id": "1", "input_json": json.dumps({"text": "", "json": entries, "files": []})})
                self.assertEqual(len(client.calls), 1)
        for value in [{"text": None, "json": [{}], "files": []}, {"text": "", "json": [{}], "files": {}}]:
            with self.assertRaisesRegex(ApiError, "full Dify output"):
                merge_inputs({}, json.dumps(value))

    def test_template_run_uses_real_contract_and_common_polling(self):
        tool = TOOLS["run_official_template"]
        detail = {"template_id": "9", "input_schema": {"type": "object", "properties": {"Area": {"type": "string", "default": "Los Angeles"}}}}
        final = {"task_id": "10", "status": "finished", "output": {"ok": True}}
        client = FakeClient(self, [("GET", "/v3/bots/templates/9", detail),
            ("POST", "/v3/bots/templates/9/runs", {"task_id": "10"}), ("GET", "/v3/bots/runs/10/status", {"status": "running"}),
            ("GET", "/v3/bots/runs/10/status", {"status": "finished"}), ("GET", "/v3/bots/runs/10", final)])
        with patch("shared.base_tool.time.sleep"):
            result = tool.invoke(client, {"operation": "run", "target_id": "9", "proxy_region": "US", "input_json": '{"Area":"New York"}'})
        self.assertEqual(client.bodies[1], {"input": {"Area": "New York"}})
        self.assertEqual(result["json"], [final])

    def test_my_bot_does_not_send_proxy_and_reports_remote_failure(self):
        tool = TOOLS["run_my_bot"]
        client = FakeClient(self, [("GET", "/v3/bots/1", {"bot_id": "1", "input_schema": {}}),
            ("POST", "/v3/bots/1/runs", {"task_id": "10"}), ("GET", "/v3/bots/runs/10/status", {"status": "failed"}),
            ("GET", "/v3/bots/runs/10", {"status": "failed", "task_failure_info": {"reason": "test"}})])
        with self.assertRaisesRegex(ApiError, "task_id=10"):
            tool.invoke(client, {"operation": "run", "target_id": "1", "proxy_region": "US"})
        self.assertEqual(client.bodies[1], {"input": {}})

    def test_invalid_run_input_does_not_create_task(self):
        tool = TOOLS["run_my_bot"]
        client = FakeClient(self, [("GET", "/v3/bots/1", {"bot_id": "1", "input_schema": {"required": ["missing"]}})])
        with self.assertRaisesRegex(ApiError, "missing"):
            tool.invoke(client, {"operation": "run", "target_id": "1"})
        self.assertEqual(len(client.calls), 1)

    def test_client_preserves_http_error_and_redacts_key(self):
        error = HTTPError("https://api.browseract.com/v3/bots/1", 401, "Unauthorized", {}, io.BytesIO(b'{"message":"invalid test-key"}'))
        with patch("shared.client.build_opener") as opener, contextlib.redirect_stdout(io.StringIO()) as log:
            opener.return_value.open.side_effect = error
            with self.assertRaises(ApiError) as caught: BrowserActClient("test-key").request("GET", "/v3/bots/1")
        self.assertEqual(caught.exception.status, 401)
        self.assertNotIn("test-key", str(caught.exception))
        self.assertNotIn("test-key", log.getvalue())


class TransportTests(unittest.TestCase):
    def setUp(self):
        self.http = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.http.server_port}"

    def tearDown(self):
        self.http.shutdown(); self.http.server_close(); self.thread.join()

    def post(self, path, data, key="test-key", origin=None):
        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + key}
        if origin: headers["Origin"] = origin
        request = Request(self.url + path, data=json.dumps(data).encode(), headers=headers)
        try: response = urlopen(request)
        except HTTPError as error: response = error
        return response.status, json.loads(response.read())

    def test_metadata_contains_two_tools(self):
        data = json.load(urlopen(self.url + "/api/tools"))
        self.assertEqual(len(data["tools"]), 2)

    def test_only_fixed_tool_routes_are_allowed(self):
        for route in ["/api", "/api/tools/evil/invoke", "/api/tools/run_my_bot/cancel"]:
            self.assertEqual(self.post(route, {})[0], 404)
        self.assertEqual(self.post("/api/tools/run_my_bot/options", {}, key="")[0], 401)
        self.assertEqual(self.post("/api/tools/run_my_bot/options", {}, origin="https://example.com")[0], 403)

    def test_invoke_routes_to_actual_registered_tool(self):
        expected = {"text": "", "json": [{"Area": "LA"}], "files": []}
        with patch.object(TOOLS["run_my_bot"], "invoke", return_value=expected) as invoke:
            status, data = self.post("/api/tools/run_my_bot/invoke", {"operation": "view", "target_id": "1"})
        self.assertEqual(status, 200); self.assertEqual(data["result"], expected)
        self.assertEqual(invoke.call_args.args[1]["target_id"], "1")


if __name__ == "__main__":
    unittest.main()
