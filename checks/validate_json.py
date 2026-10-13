#!/usr/bin/env python3
"""Validate a JSON file holding a list of records.

    python validate_json.py FILE [--min-items N] [--require-keys a,b,c]

The file is a JSON list, or an object with an "items" list. Each item must be
an object with every --require-keys key present and non-empty. Exit 0 on pass,
1 on fail (the reason is printed).
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import fail, load_json, ok  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--min-items", type=int, default=1)
    parser.add_argument("--require-keys", default="")
    args = parser.parse_args()

    data = load_json(args.file)
    items = data.get("items") if isinstance(data, dict) else data
    if not isinstance(items, list):
        fail("expected a JSON list, or an object with an 'items' list")
    if len(items) < args.min_items:
        fail(f"{len(items)} item(s), expected at least {args.min_items}")
    keys = [k.strip() for k in args.require_keys.split(",") if k.strip()]
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            fail(f"item {i} is not an object")
        for key in keys:
            value = item.get(key)
            if value is None or (isinstance(value, str) and not value.strip()):
                fail(f"item {i} has no '{key}'")
    ok(f"{len(items)} item(s), each with {', '.join(keys) or 'any keys'}")


if __name__ == "__main__":
    main()
