/* =====================================================================
   Report  : RPT-PPM-001  Project Task Listing - validation queries
   Version : 0.1  (2026-11-15)
   Run in a scratch data model in DEV with the same data source.
   Where you see <DATA_MODEL_SQL>, paste 04-data-model.sql WITHOUT its
   final ORDER BY (Oracle allows a WITH clause inside an inline view).
   ===================================================================== */

-- V-01 Independent row count (no parameters): non-template project tasks.
--      Compare with the report's row count run with all parameters blank.
--      Should match, unless Q-1 changes the join to tasks.
SELECT COUNT(*) AS expected_rows
FROM   pjf_projects_all_b       prj
JOIN   fun_all_business_units_v bu  ON bu.bu_id = prj.org_id
JOIN   pjf_tasks_v              tsk ON tsk.project_id = prj.project_id
WHERE  NVL(prj.template_flag, 'N') = 'N';

-- V-02 Duplicate detection at the expected grain (one row per project task).
--      Expected: 0 rows.
SELECT r.project_number, r.task_number, COUNT(*) AS row_count
FROM   ( <DATA_MODEL_SQL> ) r
GROUP  BY r.project_number, r.task_number
HAVING COUNT(*) > 1;

-- V-03 Null checks on mandatory columns. Expected: 0 rows.
SELECT r.*
FROM   ( <DATA_MODEL_SQL> ) r
WHERE  r.business_unit  IS NULL
OR     r.project_number IS NULL
OR     r.project_name   IS NULL
OR     r.task_number    IS NULL
OR     r.task_name      IS NULL;

-- V-04 Spot check: pick 3 projects and compare with Manage Projects in the UI.
SELECT r.*
FROM   ( <DATA_MODEL_SQL> ) r
WHERE  r.project_number IN ('&project_1', '&project_2', '&project_3')
ORDER  BY r.project_number, r.task_number;

-- V-05 Blank client explained: projects with NO active client-contact party.
--      Every project in the report with a blank CLIENT_NAME should be listed here.
SELECT prj.segment1 AS project_number
FROM   pjf_projects_all_b prj
WHERE  NVL(prj.template_flag, 'N') = 'N'
AND    NOT EXISTS (
         SELECT 1
         FROM   pjf_project_parties pp
         WHERE  pp.project_id      = prj.project_id
         AND    pp.project_role_id = {{CLIENT_CONTACT_ROLE_ID}}                  -- environment-specific
         AND    TRUNC(SYSDATE) BETWEEN TRUNC(pp.start_date_active)
                                   AND NVL(TRUNC(pp.end_date_active), TRUNC(SYSDATE)))
ORDER  BY prj.segment1;

-- V-06 Projects with more than one active PM (exercises the ROW_NUMBER dedupe).
SELECT pp.project_id, COUNT(*) AS active_pm_count
FROM   pjf_project_parties pp
WHERE  pp.project_role_id = {{PROJECT_MANAGER_ROLE_ID}}                           -- environment-specific
AND    TRUNC(SYSDATE) BETWEEN TRUNC(pp.start_date_active)
                          AND NVL(TRUNC(pp.end_date_active), TRUNC(SYSDATE))
GROUP  BY pp.project_id
HAVING COUNT(*) > 1;
