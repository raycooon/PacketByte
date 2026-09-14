from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any



class SchemaError(ValueError):
    """Raised when a PacketByte schema is invalid."""



@dataclass(frozen=True)
class FieldSpec:
    name : str
    type_name : str

NUMERIC_TYPES: dict[str, tuple[str, int]] = {
    "i8": ("i8", 1),
    "u8": ("u8", 1),
    "i16": ("i16", 2),
    "u16": ("u16", 2),
    "i32": ("i32", 4),
    "u32": ("u32", 4),
    "f32": ("f32", 4),
    "f64": ("f64", 8),
}


SPECIAL_TYPES: {"bool", "string", "bytes", "vec2", "vec3" }
SUPPORTED_TYPES: set(NUMERIC_TYPES) | SPECIAL_TYPES
IDENTIFIER_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")

def fail(message: str) -> SchemaError:
    return SchemaError(message)

def load_schema(path: Path) -> tuple[str, list[FieldSpec]]:
    """Load and Validate a JSON schema returing its name and fields."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise fail(f"Schema File NOT found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise fail(f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc

    if not isinstance(raw, dict):
        raise fail("Schema root must be a JSON object")

    packet_name = raw.get("name")
    if not isinstance(packet_name, str) or not packet_name:
        raise fail("Schema field 'name' must be a non empty string")
    validate_luau_identifier(packet_name, "schema field 'name'")

    raw_fields = raw.get("fields")
    if not isinstance(raw_fields, list) or not raw_fields:
        raise fail("Schema field 'fields' must be a non-empty array")

    fields: list[FieldSpec] = []
    seen_names: set[str] = set()
    for index, raw_field in enumerate(raw_fields):
        location = f"fields[{index}]"

        if not isinstance(raw_field, dict):
            raise fail(f"{location} must be an object")
        field_name = raw_field.get("name")
        field_type = raw_field.get("type")

        if not isinstance(field_name, str) or not field_name:
            raise fail(f"{location} must be a non-empty string")
        validate_luau_identifier(field_name, f"{location}.name")
        if field_name in seen_names:
            raise fail(f"duplicate field name: {field_name}")
        seen_names.add(field_name)
        if not isinstance(field_type, str) or field_type not in SUPPORTED_TYPES:
            choices = ", ".join(sorted(SUPPORTED_TYPES))
            raise fail(f"{location}.type must be one of: {choices}")
        fields.append(FieldSpec(field_name, field_type))

    return packet_name, fields
