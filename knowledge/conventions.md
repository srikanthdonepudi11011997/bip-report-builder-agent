# BIP Data Model SQL Conventions

These rules apply to every generated data-model and LOV query. `scripts/sql_lint.py` checks the ones marked **[lint: BIPxxx]**. The `sql-reviewer` sub-agent checks the rest.

---

## C-01 Bind variables

- Name them `:p_<snake_case>`, exactly matching `parameters[].bind` in the spec. **[lint: BIP008, BIP009]**
- Every spec parameter must be used in the SQL. Every bind in the SQL must be in the spec.
- Never concatenate parameter values into SQL text.

## C-02 Multi-select parameters: null-safe IN **[lint: BIP001]**

BIP passes a multi-select parameter as a list. When the user selects nothing, the list is NULL. Use:

```sql
AND (COALESCE(:p_business_unit, NULL) IS NULL OR bu.bu_name IN (:p_business_unit))
```

- Do **not** use `NVL(:p, x)` or `:p IS NULL`: they fail or behave inconsistently when more than one value is selected.
- Single-select optional parameters may use `(:p IS NULL OR col = :p)`.

## C-03 String parameters against numeric columns **[lint: BIP002]**

LOVs return strings. When the column is numeric (IDs, numbers stored as NUMBER), compare its string form:

```sql
AND (COALESCE(:p_project_id, NULL) IS NULL OR TO_CHAR(prj.project_id) IN (:p_project_id))
```

Never wrap the bind in `TO_NUMBER()`. One bad value breaks the whole query, and it can defeat index use differently than you expect.

## C-04 Date parameters **[lint: BIP003]**

Always `TRUNC()` both sides when comparing dates to date parameters:

```sql
AND TRUNC(prj.start_date) >= TRUNC(:p_start_date_from)
AND TRUNC(prj.start_date) <= TRUNC(:p_start_date_to)
```

Optional date range:

```sql
AND (:p_start_date_from IS NULL OR TRUNC(prj.start_date) >= TRUNC(:p_start_date_from))
```

## C-05 Translation (`_TL`) tables **[lint: BIP004]**

Every `_TL` join filters on the session language:

```sql
JOIN pjf_project_statuses_tl pst
  ON  pst.project_status_code = prj.project_status_code
  AND pst.language = USERENV('LANG')
```

Prefer `_VL` views where they exist and are accessible. They already apply the language filter.

## C-06 Date-effective tables (`_F`, `_M`)

Filter to the record effective as of the report date (default `TRUNC(SYSDATE)` unless the FSD defines an "as of" date):

```sql
AND TRUNC(SYSDATE) BETWEEN papf.effective_start_date AND papf.effective_end_date
```

For `_M` (multi-change-per-day) tables, also add `effective_latest_change = 'Y'`.

## C-07 De-duplication with `ROW_NUMBER()`

Wherever the FSD expects one row per entity, a 1:many child (manager, client, supervisor, primary address…) must be reduced to one row in its own CTE:

```sql
project_manager AS (
  SELECT ..., ROW_NUMBER() OVER (PARTITION BY pp.project_id
                                 ORDER BY pp.start_date_active DESC, pp.project_party_id DESC) AS rn
  FROM ...
)
... LEFT JOIN project_manager pm ON pm.project_id = prj.project_id AND pm.rn = 1
```

- Always state the **dedupe key** (`PARTITION BY`) and the **tie-breaker** (`ORDER BY`) in a comment.
- Always include a deterministic final tie-breaker (a unique ID).
- Never use `DISTINCT` to hide duplicates from a bad join. Fix the join or dedupe explicitly.

## C-08 Forbidden / problematic objects **[lint: BIP005]**

| Object | Problem | Use instead |
|---|---|---|
| `PJF_PROJECT_CUSTOMERS` | `ORA-00942` in some environments (not exposed to the BIP data-source user) | The `PJF_PROJECT_PARTIES` chain filtered on the client-contact project role. See C-11 and `tables/ppm.md`. |

Add rows here (and in `sql_lint.py` `FORBIDDEN_OBJECTS`) when the debugger learns a new one.

## C-09 Structure and readability

- One CTE per business concept, each with a header comment:
  `-- CTE: <name> — <what it returns> (grain: one row per <x>)`
- No `SELECT *` in data models. **[lint: BIP006]** (Discovery queries may use it.)
- Use explicit ANSI `JOIN`s. Use `LEFT JOIN` for optional data (client, manager, DFF).
- Final `SELECT` columns are in FSD order with aliases equal to `columns[].alias` (UPPER_SNAKE_CASE, which becomes the XML element name).
- File header: report ID, title, version, date, author, change log.

## C-10 Hard-coded IDs and environment values **[lint: BIP007, BIP010]**

- Environment-specific values (role IDs, DFF segments, custom lookup codes) are written as `{{PLACEHOLDER}}` tokens. The agent fills them in from `private/environment.md`.
- An unresolved `{{TOKEN}}` must never reach DEV (BIP007).
- A literal 15-digit Fusion ID (e.g. `300000012345678`) must have a comment on the same line saying what it is (BIP010).

## C-11 Environment-specific values

> ⚠️ **Environment-specific: replace with yours.** These values differ between Fusion instances. The defaults below are placeholders. Put your real values in `private/environment.md`.

| Token | Meaning | How to find yours |
|---|---|---|
| `{{CLIENT_CONTACT_ROLE_ID}}` | `PROJECT_ROLE_ID` of the project role used for the external client contact on the project's *Parties* tab. Often a custom role created for external client contacts. | `SELECT project_role_id, project_role_name FROM pjf_proj_role_types_tl WHERE language = USERENV('LANG') ORDER BY 2` |
| `{{PROJECT_MANAGER_ROLE_ID}}` | `PROJECT_ROLE_ID` of the *Project Manager* role | Same query |
| `{{LABOR_CATEGORY_ID}}` | ID of the labor category / expenditure category used to isolate labor cost | Ask your PPM functional lead, or query the expenditure category table in DEV |
| `{{TASK_DFF_<NAME>}}` | `ATTRIBUTEn` column holding a task-level DFF segment (e.g. a billing classification code) | Your configuration docs: `/ingest-docs` then `python scripts/docs_index.py dff --filter task`. Or Setup and Maintenance → Manage Descriptive Flexfields, or the discovery query in `tables/ppm.md`. |

Important behavior notes:

- **Client name only populates when a client-contact party is assigned** on the project's Parties tab. Projects without one return NULL. That is expected, not a bug. Say so in the TSD and test plan.
- **DFF segments are context-dependent.** The same `ATTRIBUTEn` can mean different things under different contexts. Always confirm the context (`ATTRIBUTE_CATEGORY`) and segment mapping. Prefer a segment documented as global.

## C-12 Performance hygiene

- Apply parameter filters in the driving CTE, not after joins.
- Don't call functions on indexed columns in joins (`TO_CHAR` belongs on the parameter comparison side only when forced by C-03).
- For large transactional tables (`PJC_EXP_ITEMS_ALL`, `GL_JE_LINES`, `AP_INVOICE_DISTRIBUTIONS_ALL`), the FSD must have a date or period parameter. If it doesn't, raise an open question.

## C-13 LOV queries

- Each parameter with a LOV gets its own query in `05-lov-queries.sql`, headed `-- LOV: <lov_name> (for :p_x)`.
- Return the display value. If display ≠ value, return two columns: `display`, `value`.
- Return distinct values ordered by display. Apply `_TL` language filters. Exclude inactive or end-dated records unless the FSD asks for them.

## C-14 Sources and citations

Every table, column and environment value in a generated report carries a source:

| Tag | Meaning | Used for |
|---|---|---|
| `[USER]` | Confirmed by the user in DEV (discovery output, fixed error) | anything |
| `[CONFIG_DOC file > section]` | Stated in the organization's configuration docs (`scripts/docs_index.py`) | DFF segment → `ATTRIBUTEn` + context, value sets, lookups, custom roles/statuses, CoA segments |
| `[ORACLE_DOCS release]` + URL | Listed on the docs.oracle.com *Tables and Views* page (cached in `knowledge/oracle-docs/`) | object existence, columns, PK/FK, view base tables |
| `[KB]` | `knowledge/tables/*.md` / lessons learned | join patterns, gotchas |
| `[VERIFY]` | Not confirmed | must have a discovery query in `03-discovery.md` |

Rules:
- `03-discovery.md` has a **Source** column. `04-data-model.sql` CTE headers have a `Sources:` line. `04a-sql-explained.md` lists every source.
- **Precedence:** USER > CONFIG_DOC > ORACLE_DOCS > KB. A conflict between sources becomes an open question.
- **DFF columns need both:** `[ORACLE_DOCS]` that the `ATTRIBUTEn` column exists on the object, and `[CONFIG_DOC]` (or `private/environment.md`) for what it means and under which context. If the segment is context-specific, add `AND <alias>.attribute_category = '<context>'`.
- Oracle Docs never proves access. An object can be documented and still raise ORA-00942 in BIP (C-08).
