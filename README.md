# runbook-check-fixtures

Small, dependency-free validators for testing Jetty runbook **code checks** (`code_checks.sources`). They are fixtures for authoring and runbook tests, not production checks.

A runbook declares this repo as a source, and Jetty clones it at depth 1 into `/app/checks/<name>` before the checks run. Nothing is installed, so every script uses only the Python 3 standard library, which the default `python312-uv` snapshot has.

```yaml
code_checks:
  sources:
    - name: fixtures
      type: git
      url: https://github.com/jettyio/runbook-check-fixtures
      ref: v1          # a tag, a branch, or a full 40-character commit SHA
```

Every script prints `PASS: …` and exits 0, or prints `FAIL: <reason>` and exits 1.

| Script | Usage | Checks |
|---|---|---|
| `checks/validate_json.py` | `validate_json.py FILE [--min-items N] [--require-keys a,b]` | FILE is a JSON list (or `{"items": [...]}`) of at least N objects, each with the required keys non-empty |
| `checks/check_links.py` | `check_links.py FILE.md [--offline] [--timeout S]` | every Markdown link resolves: relative links name an existing file, and http(s) links answer below 400 (`--offline`: only checks they're well formed) |
| `checks/validate_triage.py` | `validate_triage.py FILE [--min-items N]` | a list (or `{"issues": [...]}`) of `{number, title, label, priority}`: positive unique integer numbers, non-empty title and label, priority `P0`–`P3` |
| `checks/check_urls_present.py` | `check_urls_present.py FILE "url1,url2"` | every listed URL appears in FILE |

## Code checks that use them

```bash
python {{checks_dir}}/fixtures/checks/validate_json.py {{results_dir}}/facts.json --min-items 5 --require-keys fact,source
python {{checks_dir}}/fixtures/checks/check_links.py {{results_dir}}/migration.md
python {{checks_dir}}/fixtures/checks/validate_triage.py {{results_dir}}/triage.json
python {{checks_dir}}/fixtures/checks/check_urls_present.py {{results_dir}}/pages.md "{{urls}}"
```

The test cases these fixtures support are described in mise's notes (`authoring-v2-test-cases.md`).

## Self-test

```bash
python3 -m unittest discover -s tests -v
```
