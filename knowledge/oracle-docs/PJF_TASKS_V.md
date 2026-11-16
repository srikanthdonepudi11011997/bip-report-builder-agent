# PJF_TASKS_V
- **Type / owner:** VIEW · PJF
- **Purpose:** financial project tasks (one row per task)
- **Checked:** 2026-11-15 · release 26A · https://docs.oracle.com/en/cloud/saas/project-management/26a/oedpp/pjftasksv-8362.html
- **Base tables (view query):** PJF_PROJ_ELEMENTS_B, PJF_PROJ_ELEMENTS_TL (TASK_ID = PROJ_ELEMENT_ID; TOP_TASK_ID = DENORM_TOP_ELEMENT_ID)
- **Columns confirmed ✅:** TASK_ID, PROJECT_ID, TASK_NUMBER, TASK_NAME, DESCRIPTION, TOP_TASK_ID, PARENT_TASK_ID, WBS_LEVEL, CARRYING_OUT_ORGANIZATION_ID, TASK_MANAGER_PERSON_ID, CHARGEABLE_FLAG, BILLABLE_FLAG, START_DATE, COMPLETION_DATE, ATTRIBUTE_CATEGORY, ATTRIBUTE1 … ATTRIBUTE15, LEAF_NODE_FLAG, WORK_TYPE_ID, PLANNING_START_DATE, PLANNING_END_DATE, BASELINE_START_DATE, BASELINE_FINISH_DATE, MILESTONE_FLAG, CRITICAL_FLAG
- **Notes:** only ATTRIBUTE1–15 are exposed on this view. Which one holds which DFF segment comes from **your configuration docs** (docs-library), not from Oracle Docs.
