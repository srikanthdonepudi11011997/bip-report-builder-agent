# BIP Data Model: Parameters and LOVs (RPT-PPM-001)

Enter in **Data Model editor → List of Values / Parameters**. Data source: `ApplicationDB_FSCM`.

## List of Values
| LOV name | Type | Query (05-lov-queries.sql) | Returns | Cache |
|---|---|---|---|---|
| LOV_BUSINESS_UNIT | SQL Query | `-- LOV: LOV_BUSINESS_UNIT` | BU name | Yes |
| LOV_PROJECT_NUMBER | SQL Query | `-- LOV: LOV_PROJECT_NUMBER` | Project number (cascades on BU) | No |
| LOV_PROJECT_STATUS | SQL Query | `-- LOV: LOV_PROJECT_STATUS` | display = name, value = code | Yes |
| LOV_PROJECT_MANAGER | SQL Query | `-- LOV: LOV_PROJECT_MANAGER` | display = name, value = person ID (text) | Yes |
| LOV_YES_NO | Fixed Data | Y, N | Y / N | — |

## Parameters (in this order)
| Name | Data type | Default | Param type | LOV | Label | Multi | Can select all → | Refresh other params | Mandatory |
|---|---|---|---|---|---|---|---|---|---|
| p_business_unit | String | | Menu | LOV_BUSINESS_UNIT | Business Unit | ✔ | NULL value passed | ✔ (refreshes p_project_number) | |
| p_project_number | String | | Menu | LOV_PROJECT_NUMBER | Project Number | ✔ | NULL value passed | | |
| p_project_status | String | *(see Q-2)* | Menu | LOV_PROJECT_STATUS | Project Status | ✔ | NULL value passed | | |
| p_project_manager | String | | Menu | LOV_PROJECT_MANAGER | Project Manager | ✔ | NULL value passed | | |
| p_start_date_from | Date | | Date | — | Project Start Date From | — | — | — | |
| p_start_date_to | Date | | Date | — | Project Start Date To | — | — | — | |
| p_chargeable_only | String | N | Menu | LOV_YES_NO | Chargeable Tasks Only | — | — | — | |

## Notes
- **"NULL value passed"** for *Can select all* is required for the `COALESCE(:p, NULL) IS NULL` pattern (C-02).
- `p_project_manager` passes person IDs as text; the SQL compares `TO_CHAR(person_id)` (C-03).
- If Q-2 decides to default to Active, set the default of `p_project_status` to the Active status **code** (confirm the code with D-2).
