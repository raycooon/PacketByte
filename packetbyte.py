import argparse
import json
from pathlib import Path

def compile_schema(schema_path: str, output_path: str):

    path = Path(schema_path)

    if not path.exists():
        raise FileNotFoundError(f"File Schema not found: {schema_path}")

    schema_data = json.loads(path.read_text())
    event_name = schema_data.get("event_name", "Network Event")
    fields = schema_data.get("fields", [])

    total_bytes = 0
    pack_lines = []
    unpack_lines = []
    