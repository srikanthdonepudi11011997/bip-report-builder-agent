---
description: Review BIP SQL against conventions, lessons learned and the spec
argument-hint: <sql-file> [spec.json]
---

Review the SQL in: **$ARGUMENTS**

1. If no spec path is given, look for `02-spec.json` in the same folder as the SQL.
2. Delegate to the `sql-reviewer` sub-agent with the SQL path and spec path. It runs `scripts/sql_lint.py` and does the reasoning review.
3. Show me the findings table and verdict. If there are ERRORs, propose the exact fixes (a diff), but **do not apply them** unless I say so.
