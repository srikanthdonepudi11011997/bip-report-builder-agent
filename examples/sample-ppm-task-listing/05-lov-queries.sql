/* =====================================================================
   Report  : RPT-PPM-001  Project Task Listing - LOV queries
   Version : 0.1  (2026-11-15)
   One query per LOV. Create each as a separate "SQL Query" LOV in the
   data model (see 06-data-model-params.md).
   ===================================================================== */

-- LOV: LOV_BUSINESS_UNIT (for :p_business_unit)
SELECT DISTINCT bu.bu_name
FROM   fun_all_business_units_v bu
ORDER  BY bu.bu_name;

-- LOV: LOV_PROJECT_NUMBER (for :p_project_number)
-- Cascades on the selected business unit(s); set "Refresh other parameters
-- on change" on p_business_unit.
SELECT prj.segment1
FROM   pjf_projects_all_b       prj
JOIN   fun_all_business_units_v bu
       ON bu.bu_id = prj.org_id
WHERE  NVL(prj.template_flag, 'N') = 'N'
AND   (COALESCE(:p_business_unit, NULL) IS NULL OR bu.bu_name IN (:p_business_unit))
ORDER  BY prj.segment1;

-- LOV: LOV_PROJECT_STATUS (for :p_project_status)  display = name, value = code
-- VERIFY: PROJECT_STATUS_NAME column name (03-discovery.md D-2)
SELECT pst.project_status_name AS display,
       pst.project_status_code AS value
FROM   pjf_project_statuses_tl pst
WHERE  pst.language = USERENV('LANG')
ORDER  BY pst.project_status_name;

-- LOV: LOV_PROJECT_MANAGER (for :p_project_manager)  display = name, value = person_id as text
SELECT DISTINCT
       ppnf.full_name                 AS display,
       TO_CHAR(pp.resource_source_id) AS value
FROM   pjf_project_parties pp
JOIN   per_person_names_f  ppnf
       ON  ppnf.person_id = pp.resource_source_id
       AND ppnf.name_type = 'GLOBAL'
       AND TRUNC(SYSDATE) BETWEEN ppnf.effective_start_date AND ppnf.effective_end_date
WHERE  pp.project_role_id = {{PROJECT_MANAGER_ROLE_ID}}                           -- environment-specific
ORDER  BY 1;

-- LOV: LOV_YES_NO (for :p_chargeable_only)
-- Prefer a "Fixed Data" LOV in BIP with values Y, N. SQL equivalent:
SELECT 'N' AS value FROM dual
UNION ALL
SELECT 'Y' AS value FROM dual;
