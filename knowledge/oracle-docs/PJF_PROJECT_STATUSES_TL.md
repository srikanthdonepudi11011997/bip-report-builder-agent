# PJF_PROJECT_STATUSES_TL
- **Type / owner:** TABLE · PJF
- **Purpose:** translated project status names
- **Checked:** 2026-11-15 · release 25A (search-result content; the 25A page now redirects because the release is retired) · https://docs.oracle.com/en/cloud/saas/project-management/25a/oedpp/pjfprojectstatusestl-10733.html
- **Primary key:** status code + LANGUAGE
- **Columns confirmed ✅:** PROJECT_STATUS_CODE, LANGUAGE
- **Not confirmed ❓:** the exact *name* column (PROJECT_STATUS_NAME is expected). Use discovery query D-2.
- **Related:** PJF_PROJECT_STATUSES_VL joins _B and _TL on the status code with `language = userenv('LANG')`. Prefer it if accessible.
