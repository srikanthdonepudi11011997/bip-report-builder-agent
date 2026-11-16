---
description: (Re)generate the Alation / metadata catalog entry for a report
argument-hint: <report-id>
---

Regenerate the metadata catalog entry for **$ARGUMENTS**.

Delegate to the `doc-writer` sub-agent, asking it to (re)write only `output/$ARGUMENTS/11-catalog-entry.md` using `templates/catalog-entry-template.md`. `source_tables` must list exactly the tables referenced in `04-data-model.sql`. Owners are roles or teams, never people. Also add or update the report's row in `knowledge/report-catalog.md` (sanitized: generic ID, no company names).
