from copy import deepcopy
import json
import re

from shared.client import ApiError


def input_schema(detail):
    schema = detail.get("input_schema")
    if not isinstance(schema, dict):
        raise ApiError("No input definition was provided; parameter configuration cannot be generated.")
    if schema.get("type", "object") != "object" or not isinstance(schema.get("properties", {}), dict):
        raise ApiError("The input definition is not a supported object Schema.")
    return schema


def default_inputs(schema):
    return {name: deepcopy(definition["default"]) for name, definition in schema.get("properties", {}).items()
            if isinstance(definition, dict) and "default" in definition}


def merge_objects(defaults, overrides):
    merged = deepcopy(defaults)
    for name, value in overrides.items():
        if isinstance(merged.get(name), dict) and isinstance(value, dict):
            merged[name] = merge_objects(merged[name], value)
        else:
            merged[name] = deepcopy(value)
    return merged


def merge_inputs(schema, raw):
    if isinstance(raw, str):
        try:
            raw = json.loads(raw.strip() or "{}")
        except ValueError:
            raise ApiError("Custom parameters must be valid JSON.") from None
    if not isinstance(raw, dict):
        raise ApiError("Custom parameters must be a JSON object.")
    if set(raw) == {"text", "json", "files"}:
        if (not isinstance(raw["text"], str) or not isinstance(raw["files"], list)
                or not isinstance(raw["json"], list) or len(raw["json"]) != 1
                or not isinstance(raw["json"][0], dict)):
            raise ApiError("The full Dify output must contain a text string, a files array, and exactly one parameter object in json. Copy the full View Parameters output again.")
        raw = raw["json"][0]
    merged = merge_objects(default_inputs(schema), raw)
    validate_common_constraints(schema, merged)
    return merged


def validate_common_constraints(schema, value, path="input"):
    """Prototype preflight for common constraints; BrowserAct validates full Schema."""
    kind = schema.get("type")
    checks = {"string": lambda x: isinstance(x, str), "integer": lambda x: type(x) is int,
              "number": lambda x: type(x) in (int, float), "boolean": lambda x: type(x) is bool,
              "object": lambda x: isinstance(x, dict), "array": lambda x: isinstance(x, list),
              "null": lambda x: x is None}
    kinds = kind if isinstance(kind, list) else [kind]
    if kind and not any(checks.get(k, lambda x: True)(value) for k in kinds):
        raise ApiError(f"{path} must have type {kind}.")
    if "enum" in schema and value not in schema["enum"]:
        raise ApiError(f"{path} is not an allowed value.")
    if isinstance(value, dict):
        for name in schema.get("required", []):
            if name not in value:
                raise ApiError(f"Provide the required parameter: {name}.")
        for name, child in schema.get("properties", {}).items():
            if name in value:
                validate_common_constraints(child, value[name], path + "." + name)
    if type(value) in (int, float):
        if "minimum" in schema and value < schema["minimum"] or "maximum" in schema and value > schema["maximum"]:
            raise ApiError(f"{path} is outside the allowed range.")
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"] or "maxLength" in schema and len(value) > schema["maxLength"]:
            raise ApiError(f"{path} does not meet the length requirements.")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            raise ApiError(f"{path} does not match the required pattern.")
    if isinstance(value, list) and isinstance(schema.get("items"), dict):
        for index, item in enumerate(value):
            validate_common_constraints(schema["items"], item, f"{path}[{index}]")
