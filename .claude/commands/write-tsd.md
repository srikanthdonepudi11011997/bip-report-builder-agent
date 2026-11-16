---
description: (Re)generate the Technical Spec for a report
argument-hint: <report-id>
---

Regenerate the TSD for **$ARGUMENTS**.

Delegate to the `doc-writer` sub-agent, asking it to (re)write only `output/$ARGUMENTS/08-tsd.md` from `02-spec.json`, `03-discovery.md`, `04-data-model.sql` and `05-lov-queries.sql`, using `templates/tsd-template.md`. Keep the existing change-log rows and add a new row. Report any inconsistencies between the spec and the SQL.
