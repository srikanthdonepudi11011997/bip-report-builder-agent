---
description: Explain a BIP SQL in plain English with table/column lineage and sources
argument-hint: <sql-file | report-id>
---

Explain the SQL for: **$ARGUMENTS**

1. If the argument is a report ID, use `output/<ID>/04-data-model.sql` with its `02-spec.json` and `03-discovery.md`. If it's a file, use that file; there may be no spec.
2. List every table/view the SQL uses. Run the `oracle-docs-researcher` on any object not already in `knowledge/oracle-docs/`, so every object in the explanation has an Oracle Docs link (or is clearly marked NOT CHECKED).
3. For every DFF `ATTRIBUTEn`, lookup code or environment ID in the SQL, ask the `config-docs-researcher` for its meaning and citation.
4. Delegate to the `doc-writer` sub-agent to write the explanation from `templates/sql-explained-template.md`: to `output/<ID>/04a-sql-explained.md` for a report ID, or next to the SQL file as `<name>.explained.md`.
5. Reply with the one-paragraph overview and the column-lineage table.
