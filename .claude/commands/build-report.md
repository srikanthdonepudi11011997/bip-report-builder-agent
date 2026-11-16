---
description: Build all BIP report deliverables from an FSD (.docx/.pdf/.md)
argument-hint: <fsd-path> [reuse: <sql-file | report-id> ...] [notes]
---

Build the full BIP deliverable set for: **$ARGUMENTS**

Follow the pipeline in `CLAUDE.md` exactly:

1. **Extract.** Run `python scripts/fsd_to_json.py "<fsd-path>" -o output/_tmp/01-fsd-raw.json`. If Python or the libraries are missing, read the FSD directly and say so. Determine the REPORT_ID from the FSD, then move the file to `output/<REPORT_ID>/01-fsd-raw.json`.
2. **Parse.** Delegate to the `fsd-parser` sub-agent → `output/<REPORT_ID>/02-spec.json`. Record any `reuse:` instructions from the arguments in `spec.reuse[]`.
3. **Discover** (you orchestrate; see "Sources of truth" in `CLAUDE.md`):
   - **3a. Candidates.** For every spec column and parameter, pick candidate tables and columns from `knowledge/tables/<module>.md`, `knowledge/report-catalog.md`, `knowledge/lessons-learned.md` and any reuse SQL.
   - **3b. Configuration docs.** For every DFF, lookup, value set, custom role or status, or field the FSD names in business terms, delegate to the `config-docs-researcher` (run `python scripts/docs_index.py status` first; if there's no index, tell me to run `/ingest-docs` and continue with `[VERIFY]`). Use its token suggestions for `private/environment.md`, but **ask before editing that file**.
   - **3c. Oracle Docs.** Delegate to the `oracle-docs-researcher` with **every** object and the columns you plan to use (one call, all objects). Replace candidates that come back NOT FOUND with the alternatives it suggests.
   - **3d.** Write `output/<REPORT_ID>/03-discovery.md` in the format of `examples/sample-ppm-task-listing/03-discovery.md`, with a **Source** column (`[ORACLE_DOCS 26A](url)`, `[CONFIG_DOC file > section]`, `[KB]`, `[VERIFY]`) and a discovery query for every VERIFY. **Never invent table or column names.**
4. **Generate SQL.** Delegate to the `sql-generator` sub-agent → `04-data-model.sql`, `05-lov-queries.sql`.
5. **Review.** Delegate to the `sql-reviewer` sub-agent. On `FAIL`, send the findings back to `sql-generator` (max 2 loops).
6. **Explain.** Delegate to the `doc-writer` sub-agent → `04a-sql-explained.md` (`templates/sql-explained-template.md`).
7. **Document.** Delegate to the `doc-writer` sub-agent → files `06` to `11`.
8. **Summarize.** Write `output/<REPORT_ID>/00-review.md` from `templates/review-template.md`: open questions (blocking first), assumptions, VERIFY items, environment-token status, sources used (Oracle Docs pages, config docs), self-review (lint counts, coverage matrix, parameters used, conventions, lessons applied).

Finish with a reply to me that has:
- the blocking open questions;
- a short plain-English explanation of the SQL: which tables it reads, how they join, and where each environment value came from (from `04a-sql-explained.md`);
- the VERIFY discovery queries I should run in DEV first;
- the path to `00-review.md`.
