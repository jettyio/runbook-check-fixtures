#!/usr/bin/env python3
"""Check every link in a Markdown file.

    python check_links.py FILE.md [--offline] [--timeout SECONDS]

Relative links must name an existing file (relative to FILE.md). http(s) links
must answer below 400 (HEAD, falling back to GET). --offline checks only that
each http(s) link is well formed. Exit 0 on pass, 1 on fail.
"""

import argparse
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import fail, ok  # noqa: E402

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def reachable(url: str, timeout: float) -> str | None:
    """None when *url* answers below 400, else why not."""
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, method=method, headers={"User-Agent": "runbook-check-fixtures"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                if response.status < 400:
                    return None
        except urllib.error.HTTPError as e:
            if method == "GET" or e.code not in (403, 405, 501):
                return f"HTTP {e.code}"
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            return type(e).__name__
    return "no response below 400"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--timeout", type=float, default=10)
    args = parser.parse_args()

    path = Path(args.file)
    if not path.is_file():
        fail(f"{args.file} does not exist")
    links = LINK_RE.findall(path.read_text(encoding="utf-8"))
    if not links:
        fail(f"{args.file} has no links")
    problems = []
    for link in links:
        target = link.split("#", 1)[0]
        parts = urlsplit(link)
        if parts.scheme in ("http", "https"):
            if not parts.netloc:
                problems.append(f"{link}: malformed URL")
            elif not args.offline and (why := reachable(link, args.timeout)):
                problems.append(f"{link}: {why}")
        elif parts.scheme in ("mailto", "tel") or not target:
            continue
        elif parts.scheme:
            problems.append(f"{link}: unsupported scheme")
        elif not (path.parent / target).exists():
            problems.append(f"{link}: no such file")
    if problems:
        fail(f"{len(problems)} bad link(s): " + "; ".join(problems))
    ok(f"{len(links)} link(s) ok")


if __name__ == "__main__":
    main()
