"""Shared helpers: print a reason and exit 1 on failure, exit 0 on success."""

import json
import sys
from pathlib import Path


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def ok(message: str) -> None:
    print(f"PASS: {message}")
    sys.exit(0)


def load_json(path: str):
    p = Path(path)
    if not p.is_file():
        fail(f"{path} does not exist")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"{path} is not valid JSON: {e}")
