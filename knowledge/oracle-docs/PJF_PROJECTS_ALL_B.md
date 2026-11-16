# PJF_PROJECTS_ALL_B
- **Type / owner:** TABLE · PJF · FUSION schema
- **Purpose:** non-translated attributes of a project (one row per project)
- **Checked:** 2026-11-15 · release 25D · https://docs.oracle.com/en/cloud/saas/project-management/25d/oedpp/pjfprojectsallb-17373.html
- **Primary key:** PJF_PROJECTS_ALL_B_PK (PROJECT_ID)
- **Columns confirmed ✅:** PROJECT_ID, SEGMENT1, ORG_ID, CARRYING_OUT_ORGANIZATION_ID, PROJECT_STATUS_CODE, PROJECT_TYPE_ID, START_DATE, COMPLETION_DATE, CLOSED_DATE, TEMPLATE_FLAG
- **Foreign keys (per page):** project status, project type, work type, rate schedules
- **Notes:** project *name* lives in PJF_PROJECTS_ALL_TL.
