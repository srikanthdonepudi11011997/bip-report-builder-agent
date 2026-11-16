# BIP Data Model: Parameters and LOVs ({{REPORT_ID}})

Enter these in **Data Model editor → Parameters / List of Values**.

## List of Values
| LOV name | Type | Data source | Query (in 05-lov-queries.sql) | Cache |
|---|---|---|---|---|
| LOV_X | SQL Query | ApplicationDB_FSCM | `-- LOV: LOV_X` | Yes |

## Parameters
| Name (bind without `:`) | Data type | Default | Parameter type | LOV | Display label | Multi-select | Can select all | Refresh other params | Mandatory |
|---|---|---|---|---|---|---|---|---|---|
| p_x | String | | Menu | LOV_X | X | ✔ | ✔ (NULL value passed) | | |
| p_date_from | Date | `{$SYSDATE()$}` | Date | — | Date From | — | — | — | ✔ |

## Notes
- **Multi-select + "Can select all":** set *All values passed* to **NULL value passed**. This is what makes `COALESCE(:p, NULL) IS NULL` work (C-02).
- **Date parameters:** set the date format to match the user locale. The SQL applies `TRUNC()` (C-04).
- **Parameter order** in the report = order in this table.
