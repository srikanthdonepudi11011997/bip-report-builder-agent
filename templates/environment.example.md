# Environment configuration (EXAMPLE: copy to `private/environment.md`)

> ⚠️ **Environment-specific: replace with yours.** Every value below is a placeholder. Real values differ per Fusion instance and must **not** be committed. `private/` is gitignored.

The agent swaps each `{{TOKEN}}` in generated SQL for the value here. Tokens left blank stay unresolved, and `sql_lint.py` flags them (BIP007).

## Environment

| Key | Value |
|---|---|
| ENV_NAME | DEV |
| FUSION_RELEASE | 25x |
| DEFAULT_LANGUAGE | US |

## Tokens

| Token | Value | Meaning / how found |
|---|---|---|
| `{{CLIENT_CONTACT_ROLE_ID}}` | `300000000000001` | PROJECT_ROLE_ID of the client-contact project role (e.g. a custom "Client" role on the Parties tab) |
| `{{PROJECT_MANAGER_ROLE_ID}}` | `300000000000002` | PROJECT_ROLE_ID of Project Manager |
| `{{LABOR_CATEGORY_ID}}` | `300000000000003` | Labor expenditure category ID |
| `{{TASK_DFF_BILLING_CODE}}` | `ATTRIBUTE1` | Task DFF segment holding the billing classification code (check whether it is global or context-dependent) |
| `{{GL_SEGMENT_COMPANY}}` | `SEGMENT1` | GL company segment |
| `{{GL_SEGMENT_COST_CENTER}}` | `SEGMENT2` | GL cost center segment |
| `{{GL_SEGMENT_ACCOUNT}}` | `SEGMENT3` | GL natural account segment |

## Environment notes

- Objects not accessible to the BIP data source here (→ add to conventions C-08 if generic):
  - PJF_PROJECT_CUSTOMERS (ORA-00942)
- DFF contexts in use: …
