---
description: Build all BIP report deliverables from an FSD (.docx/.pdf/.md)
argument-hint: <fsd-path> [reuse: <sql-file | report-id> ...] [notes]
---

Build the full BIP deliverable set for: **$ARGUMENTS**

Follow the pipeline in `CLAUDE.md` exactly:

1. **Extract.** Run `python scripts/fsd_to_json.py "<fsd-path>" -o output/_tmp/01-fsd-raw.json`. If Python or the libraries are missing, read the FSD directly and say so. Determine the REPORT_ID from the FSD, then move the file to `output/<REPORT_ID>/01-fsd-raw.json`.
2. **Parse.** Delegate to the `fsd-parser` sub-agent → `output/<REPORT_ID>/02-spec.json`. Record any `reuse:` instructions from the arguments in `spec.reuse[]`.
3. **Discover** (do this yourself). For every spec column and parameter, map the source using `knowledge/tables/<module>.md`, `knowledge/report-catalog.md`, `knowledge/lessons-learned.md` and any reuse SQL. Write `output/<REPORT_ID>/03-discovery.md` in the format of `examples/sample-ppm-task-listing/03-discovery.md`. Mark anything not in the knowledge base as `VERIFY` and add a discovery query. **Never invent table or column names.**
4. **Generate SQL.** Delegate to the `sql-generator` sub-agent → `04-data-model.sql`, `05-lov-queries.sql`.
5. **Review.** Delegate to the `sql-reviewer` sub-agent. On `FAIL`, send the findings back to `sql-generator` (max 2 loops).
6. **Document.** Delegate to the `doc-writer` sub-agent → files `06` to `11`.
7. **Summarize.** Write `output/<REPORT_ID>/00-review.md` from `templates/review-template.md`: open questions (blocking first), assumptions, VERIFY items, environment-token status, self-review (lint counts, coverage matrix, parameters used, conventions, lessons applied).

Finish with a reply to me that lists the blocking open questions, the VERIFY discovery queries I should run in DEV first, and the path to `00-review.md`.
