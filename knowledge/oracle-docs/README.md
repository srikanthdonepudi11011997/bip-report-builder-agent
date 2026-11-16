# Oracle Docs cache: "Tables and Views for Oracle Fusion Cloud"

The `oracle-docs-researcher` sub-agent looks up tables and views on **docs.oracle.com** (the source of truth for standard objects) and caches what it confirmed here. One file per object, so later builds don't need to fetch the same page again.

## What goes in a cache file (facts only)
- Object name, type (TABLE / VIEW), owner, pillar, **release** and the **exact URL** checked
- Primary key, the column names confirmed (with data types when needed), relevant foreign keys / indexes
- For views: the base tables named in the view query
- A one-line paraphrased purpose, plus gotchas found while checking
- **No copied prose** from Oracle's pages. Link to them instead.

## Freshness rules
- A cache entry is valid for its release. If `private/environment.md` says your instance is on a newer release and a column is missing, re-check.
- A column marked ✅ was seen on the page. A column not listed was **not checked**; it doesn't mean the column doesn't exist.
- Oracle Docs confirms an object **exists in the product**. It does **not** prove that your BIP data-source user can query it (see `PJF_PROJECT_CUSTOMERS` → ORA-00942, lessons L-001).

## URL patterns (verified 2026-11)
| Pillar | Book code | Pattern |
|---|---|---|
| Project Management (PPM) | `oedpp` | `https://docs.oracle.com/en/cloud/saas/project-management/<rel>/oedpp/<objectname>-<n>.html` |
| Financials (AP, AR, GL, FUN, XLA) | `oedmf` | `https://docs.oracle.com/en/cloud/saas/financials/<rel>/oedmf/<objectname>-<n>.html` |
| HCM (PER, HR, PAY) | `oedmh` | `https://docs.oracle.com/en/cloud/saas/human-resources/<rel>/oedmh/<objectname>-<n>.html` (sometimes without `<rel>`) |
| Sales / TCA (HZ_) | `oedms` | `https://docs.oracle.com/en/cloud/saas/sales/oedms/<objectname>-<n>.html` |

`<objectname>` is the object name lowercased without underscores (e.g. `pjfprojectparties`). `<n>` is a page number that changes between releases, so **find pages by searching, not by guessing URLs**:
`site:docs.oracle.com "Tables and Views" <OBJECT_NAME>`

Gotchas when reading the pages:
- **Audit tables** such as `PJF_PROJECTS_ALL_TL_` (trailing underscore, `AUDIT_*` columns) have their own near-identical pages. Check that the page title is exactly your object.
- **Retired releases redirect** to a product landing page. If a fetch shows no columns, search for a newer release.
- Pages are structured as *Details · Primary Key · Columns · Foreign Keys · Indexes* (views: *Columns · Query*).

## Index
| Object | Pillar | Release checked | File |
|---|---|---|---|
| PJF_PROJECTS_ALL_B | PPM | 25D | [PJF_PROJECTS_ALL_B.md](PJF_PROJECTS_ALL_B.md) |
| PJF_PROJECTS_ALL_TL | PPM | 25D (audit page) | [PJF_PROJECTS_ALL_TL.md](PJF_PROJECTS_ALL_TL.md) |
| PJF_PROJECT_STATUSES_TL | PPM | 25A | [PJF_PROJECT_STATUSES_TL.md](PJF_PROJECT_STATUSES_TL.md) |
| PJF_PROJECT_PARTIES | PPM | 25C | [PJF_PROJECT_PARTIES.md](PJF_PROJECT_PARTIES.md) |
| PJF_TASKS_V | PPM | 26A | [PJF_TASKS_V.md](PJF_TASKS_V.md) |
| PER_PERSON_NAMES_F | HCM | current (no release in URL) | [PER_PERSON_NAMES_F.md](PER_PERSON_NAMES_F.md) |
| FUN_ALL_BUSINESS_UNITS_V | Financials | 25D | [FUN_ALL_BUSINESS_UNITS_V.md](FUN_ALL_BUSINESS_UNITS_V.md) |
| HZ_PARTIES | Sales / TCA | current | [HZ_PARTIES.md](HZ_PARTIES.md) |
