#!/usr/bin/env python3
"""Check that every URL in a list appears in a file.

    python check_urls_present.py FILE "url1,url2,..."

Each comma-separated URL must appear verbatim in FILE (a trailing "/" is
ignored on both sides). Exit 0 on pass, 1 on fail.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import fail, ok  # noqa: E402


def main() -> None:
    if len(sys.argv) != 3:
        fail("usage: check_urls_present.py FILE 'url1,url2,...'")
    path, raw = Path(sys.argv[1]), sys.argv[2]
    if not path.is_file():
        fail(f"{path} does not exist")
    text = path.read_text(encoding="utf-8")
    urls = [u.strip() for u in raw.split(",") if u.strip()]
    if not urls:
        fail("no URLs given")
    missing = [u for u in urls if u.rstrip("/") not in text]
    if missing:
        fail(f"{len(missing)} of {len(urls)} URL(s) missing: {', '.join(missing)}")
    ok(f"all {len(urls)} URL(s) present")


if __name__ == "__main__":
    main()
