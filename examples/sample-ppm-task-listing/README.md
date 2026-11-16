# Example: RPT-PPM-001 Project Task Listing (sanitized)

A complete, fictional walkthrough of what `/build-report` produces. It mirrors `output/<REPORT_ID>/` exactly, so contributors and the agent itself can use it as the reference for structure and depth.

| Step | File | Notes |
|---|---|---|
| Input | [`fsd-input.md`](fsd-input.md) | Fictional FSD with deliberate ambiguities |
| 1 | `01-fsd-raw.json` | Not committed. Generate it with `python scripts/fsd_to_json.py examples/sample-ppm-task-listing/fsd-input.md` |
| 0 | [`00-review.md`](00-review.md) | **Start here.** Open questions, assumptions, VERIFY items, coverage |
| 2 | [`02-spec.json`](02-spec.json) | Validated against `templates/fsd-spec.schema.json` |
| 3 | [`03-discovery.md`](03-discovery.md) | Field mapping + discovery queries |
| 4 | [`04-data-model.sql`](04-data-model.sql) | Data-set SQL; every CTE cites its sources |
| 4a | [`04a-sql-explained.md`](04a-sql-explained.md) | **Plain-English walkthrough:** lineage diagram, table by table, with Oracle Docs links and config-doc citations |
| 5 | [`05-lov-queries.sql`](05-lov-queries.sql) | LOVs |
| 6 | [`06-data-model-params.md`](06-data-model-params.md) | BIP parameter setup |
| 7 | [`07-rtf-layout.md`](07-rtf-layout.md) | Layout guidance |
| 8 | [`08-tsd.md`](08-tsd.md) | Technical spec |
| 9 | [`09-test-plan.md`](09-test-plan.md), [`09-validation.sql`](09-validation.sql) | Unit tests |
| 10 | [`10-it-change-request.md`](10-it-change-request.md) | CR text |
| 11 | [`11-catalog-entry.md`](11-catalog-entry.md) | Metadata catalog |

Things to notice:
- **Ambiguities are flagged, not guessed.** "Active projects" vs the status parameter becomes Q-2, and the Billing Code DFF segment is resolved from the configuration docs (A-5) instead of guessed.
- **Every fact has a source.** Tables and columns are checked against Oracle Docs (cached in `knowledge/oracle-docs/`). The DFF meaning comes from the sample configuration doc in `docs-library/samples/`. Only two items remain VERIFY.
- **Role-ID tokens are left unresolved on purpose** (`{{CLIENT_CONTACT_ROLE_ID}}` …). IDs differ per instance and aren't in config docs. In your own run, the agent fills them in from `private/environment.md`.
- **Lessons are applied:** the parties chain is used instead of PJF_PROJECT_CUSTOMERS (L-001), and person names are filtered on `name_type = 'GLOBAL'` (L-003).
