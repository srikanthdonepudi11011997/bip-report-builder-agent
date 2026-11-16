# Discovery: RPT-PPM-001 Project Task Listing

Sources consulted: `knowledge/tables/ppm.md`, `knowledge/lessons-learned.md` (L-001, L-002, L-003), `knowledge/report-catalog.md`.

## Field → source mapping

| # | Alias | Source | Join path | Confidence | Notes |
|---|---|---|---|---|---|
| 1 | BUSINESS_UNIT | FUN_ALL_BUSINESS_UNITS_V.BU_NAME | `bu.bu_id = prj.org_id` | HIGH | |
| 2 | PROJECT_NUMBER | PJF_PROJECTS_ALL_B.SEGMENT1 | driver | HIGH | |
| 3 | PROJECT_NAME | PJF_PROJECTS_ALL_TL.NAME | `ptl.project_id = prj.project_id`, `language = USERENV('LANG')` | HIGH | |
| 4 | PROJECT_STATUS | PJF_PROJECT_STATUSES_TL.PROJECT_STATUS_NAME | `pst.project_status_code = prj.project_status_code` | **VERIFY** | D-2 |
| 5 | PROJECT_START_DATE | PJF_PROJECTS_ALL_B.START_DATE | driver | HIGH | |
| 6 | PROJECT_MANAGER | PER_PERSON_NAMES_F.FULL_NAME via PJF_PROJECT_PARTIES | role = `{{PROJECT_MANAGER_ROLE_ID}}`, `resource_source_id = person_id`, `name_type = 'GLOBAL'` | HIGH (token unresolved) | D-1 |
| 7 | CLIENT_NAME | HZ_PARTIES.PARTY_NAME via PJF_PROJECT_PARTIES | role = `{{CLIENT_CONTACT_ROLE_ID}}`, `resource_source_id = party_id` | **VERIFY** | D-4, Q-5. ⛔ Not PJF_PROJECT_CUSTOMERS (L-001) |
| 8 | TASK_NUMBER | PJF_TASKS_V.TASK_NUMBER | `tsk.project_id = prj.project_id` | HIGH | |
| 9 | TASK_NAME | PJF_TASKS_V.TASK_NAME | | HIGH | |
| 10 | BILLING_CODE | PJF_TASKS_V.`{{TASK_DFF_BILLING_CODE}}` | | **VERIFY** | D-5, Q-3, L-002 |
| 11 | CHARGEABLE_FLAG | PJF_TASKS_V.CHARGEABLE_FLAG | | **VERIFY** | D-3 |

## Discovery queries (run in a DEV data model, then paste results back)

### D-1 Project role IDs (resolves `{{PROJECT_MANAGER_ROLE_ID}}`, `{{CLIENT_CONTACT_ROLE_ID}}`)
```sql
SELECT rt.project_role_id, rt.project_role_name
FROM   pjf_proj_role_types_tl rt
WHERE  rt.language = USERENV('LANG')
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

### D-3 Task flag columns
```sql
SELECT column_name
FROM   all_tab_columns
WHERE  table_name = 'PJF_TASKS_V'
AND   (column_name LIKE '%FLAG%' OR column_name LIKE 'ATTRIBUTE%')
ORDER  BY column_name;
```

### D-4 What RESOURCE_SOURCE_ID resolves to for the client role
```sql
SELECT pp.project_id, pp.project_role_id, pp.resource_source_id,
       hp.party_name, hp.party_type
FROM   pjf_project_parties pp
LEFT JOIN hz_parties hp ON hp.party_id = pp.resource_source_id
WHERE  pp.project_role_id = {{CLIENT_CONTACT_ROLE_ID}}
AND    ROWNUM <= 20;
-- party_type = 'PERSON'       -> contact person; organization needs HZ_RELATIONSHIPS (Q-5)
-- party_type = 'ORGANIZATION' -> client organization directly
```

### D-5 Which task DFF segment holds the billing code, and is it context-dependent?
```sql
SELECT tsk.attribute_category, COUNT(*) AS task_count,
       COUNT(tsk.{{TASK_DFF_BILLING_CODE}}) AS populated
FROM   pjf_tasks_v tsk
GROUP  BY tsk.attribute_category
ORDER  BY task_count DESC;
-- More than one attribute_category with populated values -> context-dependent (L-002)
```
