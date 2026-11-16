# Discovery: RPT-PPM-001 Project Task Listing

Sources consulted, in precedence order (conventions C-14):
- **[CONFIG_DOC]** `docs-library/samples/sample-ppm-dff-configuration.md` (via `python scripts/docs_index.py search` / `dff --filter task`)
- **[ORACLE_DOCS]** docs.oracle.com *Tables and Views*, cached in `knowledge/oracle-docs/`
- **[KB]** `knowledge/tables/ppm.md`, `knowledge/lessons-learned.md` (L-001, L-002, L-003), `knowledge/report-catalog.md`

## Field → source mapping

| # | Alias | Table.column | Join path | Source | Confidence |
|---|---|---|---|---|---|
| 1 | BUSINESS_UNIT | FUN_ALL_BUSINESS_UNITS_V.BU_NAME | `bu.bu_id = prj.org_id` | [ORACLE_DOCS 25D](https://docs.oracle.com/en/cloud/saas/financials/25d/oedmf/funallbusinessunitsv-5127.html) | CONFIRMED |
| 2 | PROJECT_NUMBER | PJF_PROJECTS_ALL_B.SEGMENT1 | driver | [ORACLE_DOCS 25D](https://docs.oracle.com/en/cloud/saas/project-management/25d/oedpp/pjfprojectsallb-17373.html) | CONFIRMED |
| 3 | PROJECT_NAME | PJF_PROJECTS_ALL_TL.NAME | `ptl.project_id = prj.project_id`, `language = USERENV('LANG')` | [ORACLE_DOCS 25D](https://docs.oracle.com/en/cloud/saas/project-management/25d/oedpp/pjfprojectsalltl-20636.html) (audit-table page mirrors the columns) | CONFIRMED |
| 4 | PROJECT_STATUS | PJF_PROJECT_STATUSES_TL.PROJECT_STATUS_NAME | `pst.project_status_code = prj.project_status_code` | [ORACLE_DOCS 25A](https://docs.oracle.com/en/cloud/saas/project-management/25a/oedpp/pjfprojectstatusestl-10733.html) confirms code + language only | **VERIFY** (name column, D-2) |
| 5 | PROJECT_START_DATE | PJF_PROJECTS_ALL_B.START_DATE | driver | [ORACLE_DOCS 25D] | CONFIRMED |
| 6 | PROJECT_MANAGER | PER_PERSON_NAMES_F.FULL_NAME via PJF_PROJECT_PARTIES | role = `{{PROJECT_MANAGER_ROLE_ID}}`, `resource_source_id = person_id`, `name_type = 'GLOBAL'` | [ORACLE_DOCS 25C](https://docs.oracle.com/en/cloud/saas/project-management/25c/oedpp/pjfprojectparties-25874.html) + [ORACLE_DOCS](https://docs.oracle.com/en/cloud/saas/human-resources/oedmh/perpersonnamesf-32501.html) + [KB L-003] | CONFIRMED (role ID token unresolved, D-1) |
| 7 | CLIENT_NAME | HZ_PARTIES.PARTY_NAME via PJF_PROJECT_PARTIES | role = `{{CLIENT_CONTACT_ROLE_ID}}` ("Client Contact" role), `resource_source_id = party_id` | [ORACLE_DOCS](https://docs.oracle.com/en/cloud/saas/sales/oedms/hzparties-19213.html) + [CONFIG_DOC sample-ppm-dff-configuration.md > 2. Project Roles] + [KB L-001] | Columns CONFIRMED; person vs organization **VERIFY** (D-4, Q-5). ⛔ Not PJF_PROJECT_CUSTOMERS. |
| 8 | TASK_NUMBER | PJF_TASKS_V.TASK_NUMBER | `tsk.project_id = prj.project_id` | [ORACLE_DOCS 26A](https://docs.oracle.com/en/cloud/saas/project-management/26a/oedpp/pjftasksv-8362.html) | CONFIRMED |
| 9 | TASK_NAME | PJF_TASKS_V.TASK_NAME | | [ORACLE_DOCS 26A] | CONFIRMED |
| 10 | BILLING_CODE | PJF_TASKS_V.**ATTRIBUTE1** | | Column: [ORACLE_DOCS 26A]. Meaning: segment BILLING_CODE, context *Global Data Elements*, value set EX_TASK_BILLING_CODE [CONFIG_DOC sample-ppm-dff-configuration.md > 1. Project Task Descriptive Flexfield] | CONFIRMED (A-5) |
| 11 | CHARGEABLE_FLAG | PJF_TASKS_V.CHARGEABLE_FLAG | | [ORACLE_DOCS 26A] | CONFIRMED |

### What the configuration docs added
- **Billing Code** is a *global* segment on `ATTRIBUTE1`, so no `ATTRIBUTE_CATEGORY` filter is needed. The same docs show `ATTRIBUTE9` is **context-dependent** (FIELD_WORK vs OFFICE_WORK), which is exactly the L-002 trap; it is not used here.
- The client role is named **"Client Contact"** (external). Its PROJECT_ROLE_ID is not in the docs, so the token stays unresolved until D-1 is run.
- Statuses in use: Active (ACTIVE), On Hold (EX_ON_HOLD), Closed, Pending Close. This is useful for answering Q-2 (default = `ACTIVE`?).

## Discovery queries (run in a DEV data model, then paste results back)

### D-1 Project role IDs (resolves `{{PROJECT_MANAGER_ROLE_ID}}`, `{{CLIENT_CONTACT_ROLE_ID}}`)
```sql
SELECT rt.project_role_id, rt.project_role_name
FROM   pjf_proj_role_types_tl rt
WHERE  rt.language = USERENV('LANG')
AND    rt.project_role_name IN ('Project Manager', 'Client Contact')
ORDER  BY rt.project_role_name;
```

### D-2 Project status TL columns
```sql
SELECT column_name, data_type
FROM   all_tab_columns
WHERE  table_name = 'PJF_PROJECT_STATUSES_TL'
ORDER  BY column_id;
-- fallback: SELECT * FROM pjf_project_statuses_tl WHERE ROWNUM <= 5;
```

### D-4 What RESOURCE_SOURCE_ID resolves to for the client role
```sql
SELECT pp.project_id, pp.project_role_id, pp.resource_source_id,
       hp.party_name, hp.party_type
FROM   pjf_project_parties pp
LEFT JOIN hz_parties hp ON hp.party_id = pp.resource_source_id
WHERE  pp.project_role_id = {{CLIENT_CONTACT_ROLE_ID}}
AND    ROWNUM <= 20;
-- party_type = 'PERSON'       -> contact person; organization needs HZ_RELATIONSHIPS
--                                (PJF_PROJECT_PARTIES.RELATIONSHIP_ID exists per Oracle Docs 25C) (Q-5)
-- party_type = 'ORGANIZATION' -> client organization directly
```

### D-5 (optional sanity check) Billing code population by DFF context
```sql
SELECT tsk.attribute_category, COUNT(*) AS task_count,
       COUNT(tsk.attribute1) AS billing_code_populated
FROM   pjf_tasks_v tsk
GROUP  BY tsk.attribute_category
ORDER  BY task_count DESC;
```
