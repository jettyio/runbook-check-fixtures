#!/usr/bin/env python3
"""Validate an issue triage file.

    python validate_triage.py triage.json [--min-items N]

triage.json is a JSON list (or {"issues": [...]}) of objects with:
  number   positive integer, unique
  title    non-empty string
  label    non-empty string
  priority one of P0, P1, P2, P3
Exit 0 on pass, 1 on fail.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import fail, load_json, ok  # noqa: E402

PRIORITIES = {"P0", "P1", "P2", "P3"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--min-items", type=int, default=1)
    args = parser.parse_args()

    data = load_json(args.file)
    issues = data.get("issues") if isinstance(data, dict) else data
    if not isinstance(issues, list):
        fail("expected a JSON list, or an object with an 'issues' list")
    if len(issues) < args.min_items:
        fail(f"{len(issues)} issue(s), expected at least {args.min_items}")
    seen = set()
    for i, issue in enumerate(issues):
        if not isinstance(issue, dict):
            fail(f"issue {i} is not an object")
        number = issue.get("number")
        if not isinstance(number, int) or isinstance(number, bool) or number < 1:
            fail(f"issue {i}: number must be a positive integer, got {number!r}")
        if number in seen:
            fail(f"issue #{number} is listed twice")
        seen.add(number)
        for key in ("title", "label"):
            if not isinstance(issue.get(key), str) or not issue[key].strip():
                fail(f"issue #{number}: '{key}' must be a non-empty string")
        if issue.get("priority") not in PRIORITIES:
            fail(f"issue #{number}: priority must be one of {sorted(PRIORITIES)}, got {issue.get('priority')!r}")
    ok(f"{len(issues)} issue(s) triaged")


if __name__ == "__main__":
    main()
