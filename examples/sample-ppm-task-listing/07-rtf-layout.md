# RTF Layout Guidance: RPT-PPM-001 Project Task Listing

## Page setup
- **Landscape** (11 columns), narrow margins (0.5").
- Header: "Project Task Listing", run date `<?xdoxslt:sysdate('DD-MON-YYYY HH24:MI')?>`.
- Footer: `Page <?xdofo:page-number?> of <?xdofo:total-page-number?>`.

## Parameter echo (header block)
| Label | Field |
|---|---|
| Business Unit | `<?$p_business_unit?>` (blank = All) |
| Project Status | `<?$p_project_status?>` |
| Start Date | `<?$p_start_date_from?>` – `<?$p_start_date_to?>` |
| Chargeable Only | `<?$p_chargeable_only?>` |

## Grouping (FSD: group by project)
```
<?for-each-group:G_1;./PROJECT_NUMBER?>
  Project header row: PROJECT_NUMBER – PROJECT_NAME | Status | Start | PM | Client
  <?for-each:current-group()?>
     detail row: TASK_NUMBER | TASK_NAME | BILLING_CODE | CHARGEABLE_FLAG
  <?end for-each?>
<?end for-each-group?>
```
Sort: the SQL already orders by BU, project, task. Add `<?sort:TASK_NUMBER;'ascending';data-type='text'?>` inside the group as a safeguard.

**Excel output:** use a flat single table (no group header rows) so users can filter. Create a second layout `RPT-PPM-001_Excel.rtf` (or `.xlsx` template) with all 11 columns repeated per row.

## Columns (flat / Excel layout)
| # | Header | XML element | Width | Align | Format |
|---|---|---|---|---|---|
| 1 | Business Unit | BUSINESS_UNIT | 1.0" | Left | text |
| 2 | Project Number | PROJECT_NUMBER | 0.9" | Left | text (keep leading zeros) |
| 3 | Project Name | PROJECT_NAME | 1.6" | Left | text |
| 4 | Project Status | PROJECT_STATUS | 0.8" | Left | text |
| 5 | Project Start Date | PROJECT_START_DATE | 0.9" | Center | `<?format-date:PROJECT_START_DATE;'DD-MON-YYYY'?>` |
| 6 | Project Manager | PROJECT_MANAGER | 1.2" | Left | text |
| 7 | Client Name | CLIENT_NAME | 1.4" | Left | text (blank if no client contact) |
| 8 | Task Number | TASK_NUMBER | 0.7" | Left | text |
| 9 | Task Name | TASK_NAME | 1.6" | Left | text |
| 10 | Billing Code | BILLING_CODE | 0.8" | Left | text |
| 11 | Chargeable | CHARGEABLE_FLAG | 0.6" | Center | Y/N |

## No-data message
`<?if:count(.//G_1)=0?>No projects/tasks found for the selected parameters.<?end if?>`
