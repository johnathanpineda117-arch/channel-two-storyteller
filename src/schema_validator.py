"""
Lightweight JSON Schema subset validator for draft-07 used for initial development.
This validator is intentionally minimal and supports:
- required fields
- basic type checking for: string, number, integer, boolean, object, array
- enum checking
- minItems for arrays
- simple array items type checking when items.type is present
- date-time format checking via a permissive ISO-8601 parse

Limitations:
- Does NOT support $ref, allOf/oneOf/anyOf, patternProperties, complex format validation,
  or the full JSON Schema specification. Intended as a temporary foundation until jsonschema
  can be introduced.

Functions:
- validate(instance, schema) -> (is_valid: bool, errors: List[str])

"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple
from datetime import datetime


def _is_type(value: Any, expected: str) -> bool:
    if expected == "string":
        return isinstance(value, str)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    return False


def _check_format_datetime(value: str) -> bool:
    # permissive ISO-8601 check; accepts Z and offsets
    try:
        # Python 3.11 has fromisoformat improvements; use strptime fallback for Z
        if value.endswith("Z"):
            datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        else:
            # allow offset-naive parse for simplest cases
            datetime.fromisoformat(value)
        return True
    except Exception:
        return False


def validate(instance: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    # Required fields
    required = schema.get("required", [])
    for field in required:
        if field not in instance:
            errors.append(f"Missing required field: {field}")

    properties = schema.get("properties", {})

    for prop_name, prop_schema in properties.items():
        if prop_name not in instance:
            continue
        value = instance[prop_name]

        # Type check
        expected_type = prop_schema.get("type")
        if expected_type:
            if isinstance(expected_type, list):
                if not any(_is_type(value, t) for t in expected_type):
                    errors.append(f"Property '{prop_name}' expected one of types {expected_type} but got {type(value).__name__}")
            else:
                if not _is_type(value, expected_type):
                    errors.append(f"Property '{prop_name}' expected type {expected_type} but got {type(value).__name__}")
                    continue

        # Enum check
        if "enum" in prop_schema:
            if value not in prop_schema["enum"]:
                errors.append(f"Property '{prop_name}' has value '{value}' not in enum {prop_schema['enum']}")

        # Array checks
        if prop_schema.get("type") == "array":
            items_schema = prop_schema.get("items")
            if not isinstance(value, list):
                errors.append(f"Property '{prop_name}' should be an array")
            else:
                min_items = prop_schema.get("minItems")
                if min_items is not None and len(value) < min_items:
                    errors.append(f"Property '{prop_name}' expected at least {min_items} items, got {len(value)}")
                if items_schema and isinstance(items_schema, dict):
                    item_type = items_schema.get("type")
                    if item_type:
                        for idx, item in enumerate(value):
                            if not _is_type(item, item_type):
                                errors.append(f"Property '{prop_name}[{idx}]' expected type {item_type} but got {type(item).__name__}")
                    if items_schema.get("enum"):
                        for idx, item in enumerate(value):
                            if item not in items_schema["enum"]:
                                errors.append(f"Property '{prop_name}[{idx}]' value '{item}' not in enum {items_schema['enum']}")

        # Object-specific checks (nested properties, formats)
        if prop_schema.get("type") == "object" and isinstance(value, dict):
            # nested properties basic type checks
            nested_props = prop_schema.get("properties", {})
            for nested_name, nested_schema in nested_props.items():
                if nested_name not in value:
                    continue
                nested_value = value[nested_name]
                nested_expected_type = nested_schema.get("type")
                if nested_expected_type and not _is_type(nested_value, nested_expected_type):
                    errors.append(f"Property '{prop_name}.{nested_name}' expected type {nested_expected_type} but got {type(nested_value).__name__}")
                # nested enum
                if "enum" in nested_schema:
                    if nested_value not in nested_schema["enum"]:
                        errors.append(f"Property '{prop_name}.{nested_name}' has value '{nested_value}' not in enum {nested_schema['enum']}")
                # format check for date-time
                if nested_schema.get("format") == "date-time":
                    if not isinstance(nested_value, str) or not _check_format_datetime(nested_value):
                        errors.append(f"Property '{prop_name}.{nested_name}' is not a valid date-time: {nested_value}")

        # format checks at top level
        if prop_schema.get("format") == "date-time":
            if not isinstance(value, str) or not _check_format_datetime(value):
                errors.append(f"Property '{prop_name}' is not a valid date-time: {value}")

    is_valid = len(errors) == 0
    return is_valid, errors
