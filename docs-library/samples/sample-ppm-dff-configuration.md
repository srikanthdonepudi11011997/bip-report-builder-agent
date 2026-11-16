# Configuration Workbook: Project Foundation (SANITIZED SAMPLE)

> Fictional "Example Org" configuration extract, used by tests and the worked example. Replace it with your own configuration documents. Keep real ones out of git: everything in docs-library/ except samples/ is gitignored.

## 1. Project Task Descriptive Flexfield

Flexfield: Project Task descriptive flexfield (look up the exact flexfield code in Manage Descriptive Flexfields). Base table PJF_PROJ_ELEMENTS_B; exposed in reporting view PJF_TASKS_V.

| Context | Segment Name | Prompt | Table Column | Value Set | Required | Global |
|---|---|---|---|---|---|---|
| Global Data Elements | BILLING_CODE | Billing Code | ATTRIBUTE1 | EX_TASK_BILLING_CODE | No | Yes |
| Global Data Elements | COST_POOL | Cost Pool | ATTRIBUTE2 | EX_COST_POOL | No | Yes |
| FIELD_WORK | SITE_CODE | Site Code | ATTRIBUTE9 | EX_SITE_CODE | Yes | No |
| OFFICE_WORK | ROOM_CODE | Room Code | ATTRIBUTE9 | EX_ROOM_CODE | No | No |

Note: ATTRIBUTE9 is context-dependent (FIELD_WORK vs OFFICE_WORK). Filter on ATTRIBUTE_CATEGORY when reporting it.

## 2. Project Roles

| Role Name | Usage | Notes |
|---|---|---|
| Project Manager | Internal | Seeded role |
| Client Contact | External | Custom role; assigned on the project Parties tab for the external client contact |

The PROJECT_ROLE_ID values are instance-specific. Look them up in DEV with the role discovery query; they are not recorded in this workbook.

## 3. Project Statuses in Use

| Status Name | Status Code | System Status |
|---|---|---|
| Active | ACTIVE | ACTIVE |
| On Hold | EX_ON_HOLD | ACTIVE |
| Closed | CLOSED | CLOSED |
| Pending Close | PENDING_CLOSE | PENDING_CLOSE |
