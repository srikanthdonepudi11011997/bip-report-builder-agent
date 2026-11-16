/* =====================================================================
   Report      : RPT-PPM-001  Project Task Listing
   Data model  : RPT-PPM-001_DM   Data set: DS_PROJECT_TASKS
   Data source : ApplicationDB_FSCM
   Version     : 0.2   (2026-11-15)
   Author      : BIP Report Builder Agent (draft) - review before use
   Grain       : one row per project task
   Spec        : 02-spec.json   Explained: 04a-sql-explained.md
   ---------------------------------------------------------------------
   Source tags (conventions C-14):
     [ORACLE_DOCS rel] docs.oracle.com, cached in knowledge/oracle-docs/
     [CONFIG_DOC f > s] configuration docs (docs-library/)
     [KB] knowledge base / lessons learned    [VERIFY] not yet confirmed
   Environment tokens {{...}} must be resolved from private/environment.md
   before running in DEV (sql_lint BIP007).
   ---------------------------------------------------------------------
   Change log:
     0.1  2026-11-15  Initial generation from fsd-input.md v1.0
     0.2  2026-11-15  Objects confirmed on Oracle Docs; billing code
                      resolved to ATTRIBUTE1 (global) from config docs
   ===================================================================== */
WITH
-- ---------------------------------------------------------------------
-- CTE: projects - driving set of non-template projects, filtered by the
--      BU / project / status / start-date parameters
--      (grain: one row per project)
-- Sources: PJF_PROJECTS_ALL_B [ORACLE_DOCS 25D]; FUN_ALL_BUSINESS_UNITS_V [ORACLE_DOCS 25D]
-- ---------------------------------------------------------------------
projects AS (
    SELECT prj.project_id,
           prj.segment1             AS project_number,
           prj.project_status_code,
           prj.start_date           AS project_start_date,
           bu.bu_name               AS business_unit
    FROM   pjf_projects_all_b       prj
    JOIN   fun_all_business_units_v bu
           ON bu.bu_id = prj.org_id
    WHERE  NVL(prj.template_flag, 'N') = 'N'                                      -- BR-1
    AND   (COALESCE(:p_business_unit, NULL)  IS NULL OR bu.bu_name             IN (:p_business_unit))
    AND   (COALESCE(:p_project_number, NULL) IS NULL OR prj.segment1           IN (:p_project_number))
    AND   (COALESCE(:p_project_status, NULL) IS NULL OR prj.project_status_code IN (:p_project_status))
    AND   (:p_start_date_from IS NULL OR TRUNC(prj.start_date) >= TRUNC(:p_start_date_from))
    AND   (:p_start_date_to   IS NULL OR TRUNC(prj.start_date) <= TRUNC(:p_start_date_to))
),
-- ---------------------------------------------------------------------
-- CTE: project_names - translated project name (grain: one row per project)
-- Sources: PJF_PROJECTS_ALL_TL [ORACLE_DOCS 25D, via audit-table page]
-- ---------------------------------------------------------------------
project_names AS (
    SELECT ptl.project_id,
           ptl.name AS project_name
    FROM   pjf_projects_all_tl ptl
    WHERE  ptl.language = USERENV('LANG')
),
-- ---------------------------------------------------------------------
-- CTE: project_status - translated status name (grain: one row per status code)
-- Sources: PJF_PROJECT_STATUSES_TL [ORACLE_DOCS 25A: code + language];
--          PROJECT_STATUS_NAME [VERIFY - discovery D-2]
-- ---------------------------------------------------------------------
project_status AS (
    SELECT pst.project_status_code,
           pst.project_status_name
    FROM   pjf_project_statuses_tl pst
    WHERE  pst.language = USERENV('LANG')
),
-- ---------------------------------------------------------------------
-- CTE: project_manager - current project manager (BR-2)
--      dedupe key : project_id
--      tie-break  : latest start_date_active, then highest project_party_id
--      (grain: one row per project where rn = 1)
-- Sources: PJF_PROJECT_PARTIES [ORACLE_DOCS 25C]; PER_PERSON_NAMES_F [ORACLE_DOCS];
--          name_type = 'GLOBAL' [KB L-003]; role ID token [private/environment.md]
-- ---------------------------------------------------------------------
project_manager AS (
    SELECT pp.project_id,
           pp.resource_source_id AS pm_person_id,
           ppnf.full_name        AS project_manager_name,
           ROW_NUMBER() OVER (PARTITION BY pp.project_id
                              ORDER BY pp.start_date_active DESC,
                                       pp.project_party_id  DESC) AS rn
    FROM   pjf_project_parties pp
    JOIN   per_person_names_f  ppnf
           ON  ppnf.person_id = pp.resource_source_id
           AND ppnf.name_type = 'GLOBAL'                                          -- L-003
           AND TRUNC(SYSDATE) BETWEEN ppnf.effective_start_date AND ppnf.effective_end_date
    WHERE  pp.project_role_id = {{PROJECT_MANAGER_ROLE_ID}}                       -- environment-specific
    AND    TRUNC(SYSDATE) BETWEEN TRUNC(pp.start_date_active)
                              AND NVL(TRUNC(pp.end_date_active), TRUNC(SYSDATE))
),
-- ---------------------------------------------------------------------
-- CTE: project_client - client contact from the project-parties chain (BR-3)
--      PJF_PROJECT_CUSTOMERS deliberately NOT used (ORA-00942, L-001).
--      Blank when no client-contact party is assigned on the Parties tab.
--      dedupe key : project_id
--      tie-break  : latest start_date_active, then highest project_party_id
-- Sources: PJF_PROJECT_PARTIES [ORACLE_DOCS 25C]; HZ_PARTIES [ORACLE_DOCS];
--          "Client Contact" role [CONFIG_DOC sample-ppm-dff-configuration.md > 2. Project Roles];
--          contact person vs organization [VERIFY - Q-5, D-4]
-- ---------------------------------------------------------------------
project_client AS (
    SELECT pp.project_id,
           hp.party_name AS client_name,
           ROW_NUMBER() OVER (PARTITION BY pp.project_id
                              ORDER BY pp.start_date_active DESC,
                                       pp.project_party_id  DESC) AS rn
    FROM   pjf_project_parties pp
    JOIN   hz_parties          hp
           ON hp.party_id = pp.resource_source_id
    WHERE  pp.project_role_id = {{CLIENT_CONTACT_ROLE_ID}}                        -- environment-specific
    AND    TRUNC(SYSDATE) BETWEEN TRUNC(pp.start_date_active)
                              AND NVL(TRUNC(pp.end_date_active), TRUNC(SYSDATE))
),
-- ---------------------------------------------------------------------
-- CTE: tasks - tasks of the driving projects with the billing-code DFF (BR-4)
--      (grain: one row per task)
-- Sources: PJF_TASKS_V incl. CHARGEABLE_FLAG, ATTRIBUTE1..15 [ORACLE_DOCS 26A];
--          Billing Code = ATTRIBUTE1, Global Data Elements (no context filter needed)
--          [CONFIG_DOC sample-ppm-dff-configuration.md > 1. Project Task Descriptive Flexfield]
-- ---------------------------------------------------------------------
tasks AS (
    SELECT tsk.project_id,
           tsk.task_id,
           tsk.task_number,
           tsk.task_name,
           tsk.attribute1          AS billing_code,                               -- {{TASK_DFF_BILLING_CODE}} = ATTRIBUTE1 (global)
           tsk.chargeable_flag
    FROM   pjf_tasks_v tsk
    WHERE  tsk.project_id IN (SELECT p.project_id FROM projects p)
    AND   (NVL(:p_chargeable_only, 'N') = 'N' OR tsk.chargeable_flag = 'Y')       -- F-2
)
-- ---------------------------------------------------------------------
-- Final select: columns in FSD order, aliases = spec columns[].alias
-- A-1: inner join to tasks (projects without tasks excluded; see Q-1)
-- ---------------------------------------------------------------------
SELECT p.business_unit           AS business_unit,
       p.project_number          AS project_number,
       pn.project_name           AS project_name,
       ps.project_status_name    AS project_status,
       p.project_start_date      AS project_start_date,
       pm.project_manager_name   AS project_manager,
       pc.client_name            AS client_name,
       t.task_number             AS task_number,
       t.task_name               AS task_name,
       t.billing_code            AS billing_code,
       t.chargeable_flag         AS chargeable_flag
FROM        projects        p
JOIN        tasks           t  ON t.project_id  = p.project_id
LEFT JOIN   project_names   pn ON pn.project_id = p.project_id
LEFT JOIN   project_status  ps ON ps.project_status_code = p.project_status_code
LEFT JOIN   project_manager pm ON pm.project_id = p.project_id AND pm.rn = 1
LEFT JOIN   project_client  pc ON pc.project_id = p.project_id AND pc.rn = 1
WHERE (COALESCE(:p_project_manager, NULL) IS NULL OR TO_CHAR(pm.pm_person_id) IN (:p_project_manager))
ORDER BY p.business_unit, p.project_number, t.task_number
