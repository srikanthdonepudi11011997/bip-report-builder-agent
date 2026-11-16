---
description: Diagnose a DEV error / wrong output, fix the SQL, record a lesson
argument-hint: <report-id> <ORA- error text or description of wrong output>
---

Debug report output for: **$ARGUMENTS**

1. The first token is the REPORT_ID. Everything after it is the error or wrong-output description. Load `output/<REPORT_ID>/04-data-model.sql`, `02-spec.json` and `03-discovery.md`. If they don't exist, ask me to paste the SQL.
2. Delegate to the `debugger` sub-agent.
3. If the debugger needs facts (e.g. a column name), show me its **discovery query** and stop. Don't guess.
4. Otherwise apply the fix to `04-data-model.sql`, bump the version, add a change-log line in the header, and re-run `python scripts/sql_lint.py output/<REPORT_ID>/04-data-model.sql --spec output/<REPORT_ID>/02-spec.json`.
5. Append the debugger's **sanitized** lesson to `knowledge/lessons-learned.md` as the next `L-NNN`. Apply any knowledge updates it recommends (conventions C-08, table notes, `FORBIDDEN_OBJECTS` in `scripts/sql_lint.py` plus a test). Tell me which files changed.
6. If the fix changes behavior described in the TSD or test plan, update `08-tsd.md` / `09-test-plan.md` (change log too).
