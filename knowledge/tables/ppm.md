# PPM: Project Portfolio Management (Projects, Tasks, Costing, Parties)

See `README.md` for the confidence legend and generic discovery queries.

## Projects

### PJF_PROJECTS_ALL_B
- **Purpose / grain:** one row per project (base, non-translated).
- **Key columns:** PROJECT_ID (PK), SEGMENT1 (project number), ORG_ID (business unit), CARRYING_OUT_ORGANIZATION_ID (owning org), PROJECT_STATUS_CODE, PROJECT_TYPE_ID, START_DATE, COMPLETION_DATE, CLOSED_DATE, TEMPLATE_FLAG
- **Joins:** `prj.org_id = bu.bu_id` (FUN_ALL_BUSINESS_UNITS_V); `prj.project_status_code = pst.project_status_code`; `prj.carrying_out_organization_id = org.organization_id`
- **Gotchas:** Exclude templates with `NVL(prj.template_flag, 'N') = 'N'`. Project *name* is in the `_TL` / `_VL`.
- **Confidence:** HIGH (PROJECT_ID, SEGMENT1, ORG_ID, PROJECT_STATUS_CODE, START_DATE, COMPLETION_DATE, TEMPLATE_FLAG); VERIFY (CLOSED_DATE, CARRYING_OUT_ORGANIZATION_ID in your release)

### PJF_PROJECTS_ALL_TL / PJF_PROJECTS_ALL_VL
- **Purpose / grain:** project name/description per language (`_TL`), or pre-joined base + TL (`_VL`).
- **Key columns:** PROJECT_ID, NAME, DESCRIPTION, LANGUAGE (`_TL` only)
- **Gotchas:** `_TL` needs `language = USERENV('LANG')` (C-05).
- **Confidence:** HIGH

### PJF_PROJECT_STATUSES_TL
- **Purpose / grain:** status display name per status code and language.
- **Key columns:** PROJECT_STATUS_CODE, PROJECT_STATUS_NAME, LANGUAGE
- **Confidence:** VERIFY (column names). Discovery: `SELECT * FROM pjf_project_statuses_tl WHERE language = USERENV('LANG') AND ROWNUM <= 20`

### PJF_PROJECT_TYPES_TL
- **Purpose / grain:** project type name per type ID and language.
- **Key columns:** PROJECT_TYPE_ID, PROJECT_TYPE, LANGUAGE
- **Confidence:** VERIFY

## Tasks

### PJF_TASKS_V
- **Purpose / grain:** one row per project task (financial task structure), with task DFF attributes.
- **Key columns:** TASK_ID (PK), PROJECT_ID, TASK_NUMBER, TASK_NAME, PARENT_TASK_ID, TOP_TASK_ID, CHARGEABLE_FLAG, BILLABLE_FLAG, ATTRIBUTE_CATEGORY, ATTRIBUTE1 … ATTRIBUTEn (task DFF segments)
- **Joins:** `tsk.project_id = prj.project_id`
- **Gotchas:**
  - Task DFF segments live in `ATTRIBUTEn`, and **the mapping is environment-specific and can be context-dependent**. Example from one implementation: a billing classification code in `ATTRIBUTE14`, while `ATTRIBUTE9` meant different things per context. Use the `{{TASK_DFF_<NAME>}}` token from `private/environment.md`; never guess the segment.
  - Task start/finish date column names vary by view and release. Confirm before use.
- **Confidence:** HIGH (TASK_ID, PROJECT_ID, TASK_NUMBER, TASK_NAME, ATTRIBUTEn exist); VERIFY (date columns, CHARGEABLE_FLAG, BILLABLE_FLAG, TOP_TASK_ID)
- **Discovery:** `SELECT column_name FROM all_tab_columns WHERE table_name = 'PJF_TASKS_V' AND (column_name LIKE '%DATE%' OR column_name LIKE '%FLAG%') ORDER BY 1`

## Project parties (manager, client contact, team)

### PJF_PROJECT_PARTIES
- **Purpose / grain:** one row per person/party assigned to a project in a project role, for a date range.
- **Key columns:** PROJECT_PARTY_ID (PK), PROJECT_ID, PROJECT_ROLE_ID, RESOURCE_SOURCE_ID, START_DATE_ACTIVE, END_DATE_ACTIVE
- **Joins:**
  - Role name: `pp.project_role_id = rt.project_role_id` (PJF_PROJ_ROLE_TYPES_TL)
  - Internal person (e.g. project manager): `pp.resource_source_id = ppnf.person_id` (PER_PERSON_NAMES_F, `name_type = 'GLOBAL'`)
  - External client contact: `pp.resource_source_id = hp.party_id` (HZ_PARTIES)
- **Gotchas:**
  - **This is the preferred source for the project client.** `PJF_PROJECT_CUSTOMERS` raised `ORA-00942` in at least one environment (see lessons-learned L-001).
  - **Client name only populates when a client-contact party is assigned** on the project's Parties tab, so expect NULLs.
  - Several rows can be active per role → dedupe with `ROW_NUMBER()` (C-07), latest `START_DATE_ACTIVE` first.
  - Whether `RESOURCE_SOURCE_ID` points at the contact *person* party or the customer *organization* party depends on how the party was added. If you need the organization name and get a person's name, follow HZ_RELATIONSHIPS from the person party to its organization. Confirm in DEV.
- **Confidence:** HIGH (PROJECT_ID, PROJECT_ROLE_ID, RESOURCE_SOURCE_ID, START/END_DATE_ACTIVE); VERIFY (what RESOURCE_SOURCE_ID resolves to for external parties in your setup)
- **Discovery:**
  ```sql
  SELECT pp.project_id, pp.project_role_id, rt.project_role_name,
         pp.resource_source_id, hp.party_name, hp.party_type,
         pp.start_date_active, pp.end_date_active
  FROM   pjf_project_parties pp
  JOIN   pjf_proj_role_types_tl rt
         ON rt.project_role_id = pp.project_role_id AND rt.language = USERENV('LANG')
  LEFT JOIN hz_parties hp ON hp.party_id = pp.resource_source_id
  WHERE  pp.project_id = :p_sample_project_id
  ```

### PJF_PROJ_ROLE_TYPES_TL
- **Purpose / grain:** project role name per role ID and language.
- **Key columns:** PROJECT_ROLE_ID, PROJECT_ROLE_NAME, LANGUAGE
- **Confidence:** VERIFY (column names)

### PJF_PROJECT_CUSTOMERS ⛔
- **Do not use.** See conventions C-08 and lessons-learned L-001.

## Costing

### PJC_EXP_ITEMS_ALL
- **Purpose / grain:** one row per expenditure item (cost transaction).
- **Key columns:** EXPENDITURE_ITEM_ID (PK), PROJECT_ID, TASK_ID, EXPENDITURE_TYPE_ID, EXPENDITURE_ITEM_DATE, QUANTITY, PROJECT_RAW_COST, PROJECT_BURDENED_COST, PROJECT_CURRENCY_CODE
- **Gotchas:** High volume. Always filter by project and/or a date range (C-12). Labor vs non-labor is usually decided by expenditure category / type class. Use `{{LABOR_CATEGORY_ID}}` for the environment's labor category.
- **Confidence:** HIGH (IDs, EXPENDITURE_ITEM_DATE, QUANTITY); VERIFY (cost amount column names for your release)

### PJF_EXP_TYPES_TL / PJF_EXP_TYPES_VL
- **Purpose / grain:** expenditure type name.
- **Key columns:** EXPENDITURE_TYPE_ID, EXPENDITURE_TYPE_NAME, EXPENDITURE_CATEGORY_ID (`_VL`/`_B`)
- **Confidence:** VERIFY

## Shared lookups used by PPM reports

| Object | Use | Confidence |
|---|---|---|
| FUN_ALL_BUSINESS_UNITS_V | BU_ID, BU_NAME for `prj.org_id` | HIGH |
| HR_ORGANIZATION_UNITS_F_TL | Organization NAME by ORGANIZATION_ID (`language`, effective dates) | HIGH |
| HZ_PARTIES | PARTY_ID, PARTY_NAME, PARTY_TYPE | HIGH |
| PER_PERSON_NAMES_F | PERSON_ID, FULL_NAME, DISPLAY_NAME, NAME_TYPE, effective dates | HIGH |
