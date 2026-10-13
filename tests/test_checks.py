"""Self-tests for the checks: python3 -m unittest discover -s tests"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CHECKS = Path(__file__).resolve().parent.parent / "checks"


def run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(CHECKS / script), *args], capture_output=True, text=True, timeout=60)


class Case(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def write(self, name: str, content) -> str:
        path = self.dir / name
        path.write_text(content if isinstance(content, str) else json.dumps(content), encoding="utf-8")
        return str(path)

    def assertPass(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(result.stdout.startswith("PASS"), result.stdout)

    def assertFail(self, result, reason: str):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(reason, result.stdout)


class TestValidateJson(Case):
    FACTS = [{"fact": f"f{i}", "source": f"https://deepwiki.com/x/{i}"} for i in range(5)]

    def test_pass(self):
        self.assertPass(run("validate_json.py", self.write("facts.json", self.FACTS), "--min-items", "5", "--require-keys", "fact,source"))

    def test_items_object(self):
        self.assertPass(run("validate_json.py", self.write("f.json", {"items": self.FACTS}), "--min-items", "5"))

    def test_too_few(self):
        self.assertFail(run("validate_json.py", self.write("f.json", self.FACTS[:3]), "--min-items", "5"), "expected at least 5")

    def test_missing_key(self):
        bad = self.FACTS[:4] + [{"fact": "x", "source": " "}]
        self.assertFail(run("validate_json.py", self.write("f.json", bad), "--require-keys", "fact,source"), "has no 'source'")

    def test_not_json(self):
        self.assertFail(run("validate_json.py", self.write("f.json", "{nope")), "not valid JSON")

    def test_missing_file(self):
        self.assertFail(run("validate_json.py", str(self.dir / "absent.json")), "does not exist")


class TestCheckLinks(Case):
    def test_relative_links(self):
        self.write("other.md", "# o")
        self.assertPass(run("check_links.py", self.write("doc.md", "[a](other.md) [b](other.md#x) [c](#top)"), "--offline"))

    def test_missing_relative(self):
        self.assertFail(run("check_links.py", self.write("doc.md", "[a](gone.md)"), "--offline"), "no such file")

    def test_offline_url_is_only_parsed(self):
        self.assertPass(run("check_links.py", self.write("doc.md", "[a](https://example.invalid/x)"), "--offline"))

    def test_malformed_url(self):
        self.assertFail(run("check_links.py", self.write("doc.md", "[a](https:///x)"), "--offline"), "malformed URL")

    def test_no_links(self):
        self.assertFail(run("check_links.py", self.write("doc.md", "no links here"), "--offline"), "has no links")


class TestValidateTriage(Case):
    GOOD = [{"number": 1, "title": "Crash", "label": "bug", "priority": "P0"}, {"number": 7, "title": "Docs", "label": "docs", "priority": "P3"}]

    def test_pass(self):
        self.assertPass(run("validate_triage.py", self.write("t.json", self.GOOD)))

    def test_issues_object(self):
        self.assertPass(run("validate_triage.py", self.write("t.json", {"issues": self.GOOD}), "--min-items", "2"))

    def test_duplicate(self):
        self.assertFail(run("validate_triage.py", self.write("t.json", self.GOOD + [self.GOOD[0]])), "listed twice")

    def test_bad_priority(self):
        bad = [dict(self.GOOD[0], priority="urgent")]
        self.assertFail(run("validate_triage.py", self.write("t.json", bad)), "priority must be one of")

    def test_bad_number(self):
        bad = [dict(self.GOOD[0], number="1")]
        self.assertFail(run("validate_triage.py", self.write("t.json", bad)), "positive integer")

    def test_empty_label(self):
        bad = [dict(self.GOOD[0], label="")]
        self.assertFail(run("validate_triage.py", self.write("t.json", bad)), "'label' must be")


class TestUrlsPresent(Case):
    def test_pass(self):
        f = self.write("pages.md", "- https://a.example/x summary\n- https://b.example/ summary")
        self.assertPass(run("check_urls_present.py", f, "https://a.example/x, https://b.example/"))

    def test_missing(self):
        f = self.write("pages.md", "- https://a.example/x")
        self.assertFail(run("check_urls_present.py", f, "https://a.example/x,https://c.example"), "1 of 2 URL(s) missing")

    def test_usage(self):
        self.assertFail(run("check_urls_present.py"), "usage")


if __name__ == "__main__":
    unittest.main()
