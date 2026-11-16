# Contributing

Thanks for helping improve the BIP Report Builder Agent! The most valuable contributions are **knowledge**: accurate table notes, conventions and lessons learned from real (sanitized) report builds.

## Ground rules

1. **No confidential data, ever.** No real FSDs, report IDs, company or client names, people, user names, credentials or environment-specific IDs. If in doubt, leave it out.
2. **No invented objects.** Only add tables or columns to `knowledge/tables/*.md` that you have seen in a real Fusion environment or in Oracle's published documentation. Mark anything you aren't sure of with `Confidence: VERIFY`.
3. **Environment-specific values** (role IDs, DFF attribute mappings, custom lookups) go in `templates/environment.example.md` as placeholders. Never commit real values.

## What to contribute

| Area | How |
|---|---|
| Table notes | Add to `knowledge/tables/<module>.md` using the existing format (purpose, key columns, joins, gotchas, confidence). |
| Lessons learned | Append to `knowledge/lessons-learned.md` using the template at the top. Sanitize first. |
| Lint rules | Add a rule to `scripts/sql_lint.py`, a test in `tests/test_sql_lint.py` and a row in the README rule table. |
| Templates | Improve files in `templates/`. Keep the field names in sync with `fsd-spec.schema.json`. |
| Sub-agents / commands | Edit `.claude/agents/*.md` or `.claude/commands/*.md`. Explain the behavior change in your PR. |

## Development

```bash
pip install -r requirements-dev.txt
python -m pytest -q
python scripts/sql_lint.py examples/sample-ppm-task-listing/04-data-model.sql \
    --spec examples/sample-ppm-task-listing/02-spec.json
```

CI runs the tests and lints the example SQL on every push and PR.

## Pull requests

- Keep each PR to one topic.
- Explain the *why*. For a lesson or convention, describe the symptom (e.g. the `ORA-` error) and the fix.
- Run the tests before opening the PR.
