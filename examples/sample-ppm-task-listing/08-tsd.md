# Technical Specification: RPT-PPM-001 Project Task Listing

| Item | Value |
|---|---|
| Report ID | RPT-PPM-001 |
| Title | Project Task Listing |
| Module | PPM |
| Version | 0.1 |
| Related FSD | fsd-input.md v1.0 |
| Author | BIP Report Builder Agent (draft), reviewed by: ______ |
| Date | 2026-11-15 |
| Status | Draft |

## 1. Purpose
List projects and their tasks with the current project manager, client and task billing code. Used for the weekly project review and for checking billing-code setup.

## 2. Scope
- **In scope:** non-template projects and their tasks, filtered by BU, project, status, PM, start-date range and chargeable flag.
- **Out of scope:** costs, budgets, billing amounts; Fusion data security (see Q-4).
- **Expected grain:** one row per project task.

## 3. Assumptions and open questions
| ID | Type | Text | Blocking? |
|---|---|---|---|
| A-1 | Assumption | Projects without tasks are excluded | — |
| A-2 | Assumption | "Active" not hard-coded; status parameter controls | — |
| A-3 | Assumption | Current PM / client = party active on run date | — |
| A-4 | Assumption | Status shows name, filters on code | — |
| Q-1 | Question | Include projects with no tasks? | No |
| Q-2 | Question | Default status = Active? | **Yes** |
| A-5 | Assumption | Billing Code = PJF_TASKS_V.ATTRIBUTE1, global segment [CONFIG_DOC] (was Q-3) | — |
| Q-4 | Question | Apply BU data security? | No |
| Q-5 | Question | Client contact person vs organization? | No |

## 4. Technical design

### 4.1 Catalog objects
| Object | Path |
|---|---|
| Data model | `/Shared Folders/Custom/PPM/RPT-PPM-001/RPT-PPM-001_DM.xdm` |
| Report | `/Shared Folders/Custom/PPM/RPT-PPM-001/RPT-PPM-001_RPT.xdo` |
| Layouts | `RPT-PPM-001_Layout.rtf` (grouped, PDF), `RPT-PPM-001_Excel.rtf` (flat) |

### 4.2 Data source
`ApplicationDB_FSCM`, one SQL data set `DS_PROJECT_TASKS` (`04-data-model.sql`).

### 4.3 Source tables and views
| Table / view | Purpose | Join | Source |
|---|---|---|---|
| PJF_PROJECTS_ALL_B | Driving projects | — | [ORACLE_DOCS 25D](https://docs.oracle.com/en/cloud/saas/project-management/25d/oedpp/pjfprojectsallb-17373.html) |
| FUN_ALL_BUSINESS_UNITS_V | BU name | `bu_id = prj.org_id` | [ORACLE_DOCS 25D](https://docs.oracle.com/en/cloud/saas/financials/25d/oedmf/funallbusinessunitsv-5127.html) |
| PJF_PROJECTS_ALL_TL | Project name | `project_id`, language | [ORACLE_DOCS 25D](https://docs.oracle.com/en/cloud/saas/project-management/25d/oedpp/pjfprojectsalltl-20636.html) (audit-table page) |
| PJF_PROJECT_STATUSES_TL | Status name | `project_status_code`, language | [ORACLE_DOCS 25A](https://docs.oracle.com/en/cloud/saas/project-management/25a/oedpp/pjfprojectstatusestl-10733.html); name column VERIFY (D-2) |
| PJF_PROJECT_PARTIES | PM and client contact | `project_id`, role ID | [ORACLE_DOCS 25C](https://docs.oracle.com/en/cloud/saas/project-management/25c/oedpp/pjfprojectparties-25874.html) |
| PER_PERSON_NAMES_F | PM name | `person_id = resource_source_id`, GLOBAL, effective | [ORACLE_DOCS](https://docs.oracle.com/en/cloud/saas/human-resources/oedmh/perpersonnamesf-32501.html) |
| HZ_PARTIES | Client name | `party_id = resource_source_id` | [ORACLE_DOCS](https://docs.oracle.com/en/cloud/saas/sales/oedms/hzparties-19213.html); person vs org VERIFY (Q-5) |
| PJF_TASKS_V | Tasks, billing code DFF (ATTRIBUTE1), chargeable flag | `project_id` | [ORACLE_DOCS 26A](https://docs.oracle.com/en/cloud/saas/project-management/26a/oedpp/pjftasksv-8362.html) + [CONFIG_DOC sample-ppm-dff-configuration.md > 1. Project Task Descriptive Flexfield] |

### 4.4 Query structure (CTEs)
| CTE | Business concept | Grain | Notes |
|---|---|---|---|
| projects | Driving project set + parameter filters | project | Templates excluded (BR-1) |
| project_names | Translated name | project | `_TL` language filter |
| project_status | Translated status | status code | `_TL` language filter |
| project_manager | Current PM (BR-2) | project (rn = 1) | Dedupe key `project_id`; tie-break latest `start_date_active`, `project_party_id` |
| project_client | Client contact (BR-3) | project (rn = 1) | Parties chain, **not** PJF_PROJECT_CUSTOMERS (L-001) |
| tasks | Tasks + billing code (BR-4) | task | DFF segment environment-specific (L-002) |

### 4.5 Parameters
| # | Label | Bind | Type | Multi | Req | Default | LOV |
|---|---|---|---|---|---|---|---|
| 1 | Business Unit | :p_business_unit | String | ✔ | | All | LOV_BUSINESS_UNIT |
| 2 | Project Number | :p_project_number | String | ✔ | | All | LOV_PROJECT_NUMBER |
| 3 | Project Status | :p_project_status | String | ✔ | | Q-2 | LOV_PROJECT_STATUS |
| 4 | Project Manager | :p_project_manager | String | ✔ | | All | LOV_PROJECT_MANAGER |
| 5 | Project Start Date From | :p_start_date_from | Date | | | | — |
| 6 | Project Start Date To | :p_start_date_to | Date | | | | — |
| 7 | Chargeable Tasks Only | :p_chargeable_only | String | | | N | LOV_YES_NO |

### 4.6 LOVs
See `05-lov-queries.sql` and `06-data-model-params.md`. Project Number cascades on Business Unit.

### 4.7 Column mapping
| # | Header | Alias | Source | Format |
|---|---|---|---|---|
| 1 | Business Unit | BUSINESS_UNIT | FUN_ALL_BUSINESS_UNITS_V.BU_NAME | text |
| 2 | Project Number | PROJECT_NUMBER | PJF_PROJECTS_ALL_B.SEGMENT1 | text |
| 3 | Project Name | PROJECT_NAME | PJF_PROJECTS_ALL_TL.NAME | text |
| 4 | Project Status | PROJECT_STATUS | PJF_PROJECT_STATUSES_TL.PROJECT_STATUS_NAME | text |
| 5 | Project Start Date | PROJECT_START_DATE | PJF_PROJECTS_ALL_B.START_DATE | DD-MON-YYYY |
| 6 | Project Manager | PROJECT_MANAGER | PER_PERSON_NAMES_F.FULL_NAME | text |
| 7 | Client Name | CLIENT_NAME | HZ_PARTIES.PARTY_NAME | text |
| 8 | Task Number | TASK_NUMBER | PJF_TASKS_V.TASK_NUMBER | text |
| 9 | Task Name | TASK_NAME | PJF_TASKS_V.TASK_NAME | text |
| 10 | Billing Code | BILLING_CODE | PJF_TASKS_V.ATTRIBUTE1 (Billing Code DFF, global) | text |
| 11 | Chargeable | CHARGEABLE_FLAG | PJF_TASKS_V.CHARGEABLE_FLAG | Y/N |

### 4.8 Business rules → implementation
| Rule | Description | Implemented in |
|---|---|---|
| BR-1 | Exclude templates | `projects`: `NVL(template_flag,'N') = 'N'` |
| BR-2 | Current PM, most recent if several | `project_manager`: active on SYSDATE, `ROW_NUMBER()`, rn = 1 |
| BR-3 | Client from Parties tab | `project_client`: client-contact role, blank if none assigned |
| BR-4 | Billing code from task DFF | `tasks`: environment-specific `ATTRIBUTEn` |

### 4.9 Conventions applied
C-02 multi-select null checks (BU, project, status, PM) · C-03 `TO_CHAR(pm_person_id)` · C-04 `TRUNC` on start-date range · C-05 `_TL` language filters · C-07 `ROW_NUMBER()` for PM and client · C-08 PJF_PROJECT_CUSTOMERS avoided.

## 5. Layout
See `07-rtf-layout.md`. PDF uses the grouped layout; Excel uses the flat layout.

## 6. Security
- Access: Project Accountant, PMO Analyst (catalog folder permissions).
- Data security: not applied. BIP SQL bypasses Fusion PPM data security (Q-4).
- Personal data: Project Manager names (internal), client contact names. Classify the report as *Internal*.

## 7. Performance considerations
- Driving filters are applied in `projects`; `tasks` is restricted to driving projects.
- With no parameters the report returns every non-template project task. Consider making BU mandatory if volumes are high.

## 8. Known limitations
- Client Name is blank when no client-contact party is assigned on the project's Parties tab (expected).
- Only the PM active on the run date is shown; historical PMs are not.

## 9. Testing
See `09-test-plan.md` and `09-validation.sql`.

## 10. Deployment
Archive `/Shared Folders/Custom/PPM/RPT-PPM-001/` in DEV → unarchive in TEST/PROD per `10-it-change-request.md`.

## 11. Change log
| Version | Date | Author | Change |
|---|---|---|---|
| 0.1 | 2026-11-15 | BIP Report Builder Agent | Initial draft |
