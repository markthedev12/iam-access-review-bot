# IAM Access Review Bot

A Python tool that compares a CSV access export with JSON role baselines and
renders HTML findings for human review. Uses fictional data, with no live
identity-system connection or automatic access changes.

## Quick start

Requires Python 3.12+.

```sh
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py --as-of 2026-11-08
python -m unittest discover -s tests -v
```

Open `access_review_report.html` in your browser. Default sample paths resolve
relative to the program, while output defaults to your working directory. Use
`--input`, `--baseline`, and `--output` to select local files. `--as-of` makes a
review reproducible; omitting it uses today's date.

## Rules and data contract

| Finding | Condition | Risk |
| --- | --- | --- |
| Excess access | System or group absent from a role baseline; unknown role needs review | Medium |
| Stale access | More than 90 days since last review; exactly 90 is not stale | Low |
| Privilege violation | Privileged entitlement for a role that does not permit it | High |

CSV headers: `user_id,name,role,system,group,last_reviewed,privileged`.
Required values must be non-empty, dates must use YYYY-MM-DD, and privileged
must be true/false (case-insensitive). Conflicting names/roles for one user ID
are rejected instead of silently using the first row. UTF-8/BOM input is supported.

JSON maps roles to `expected_systems`, `expected_groups` (string lists), and
`max_privileged_access` (a JSON boolean). See `data/` for complete examples.
Invalid input exits 2 without generating a new report; an older report may still
exist. Successful generation exits 0 even with findings.

## Architecture and security

`CSV + JSON -> validated models -> pure review engine -> escaped HTML`

`src/loader.py` owns ingestion; `models.py` holds data classes;
`review_engine.py` computes findings; `report_generator.py` renders the template.
Jinja2 autoescaping prevents imported identifiers/names/details becoming HTML,
and reports use UTF-8. Tests cover rule boundaries, ingestion failures,
reproducible dates, Unicode, template paths and injected markup. CI runs Python
3.12/3.13 without external services.

## Limits and roadmap

Reports contain identity data; use fictional exports publicly and keep real
reports out of Git. Risk labels and recommended actions are illustrative review
prompts, not compliance certification or permission to revoke access.

Systems and groups are currently validated independently, not as allowed pairs.
Unknown roles return one review finding rather than evaluating other rules.
Duplicate rows are not deduplicated and future review dates are not rejected.
Next: explicit entitlement pairs, configurable policies, better date handling,
and JSON/CSV finding exports. Contributions should include a regression fixture
and explain the intended reviewer outcome.
