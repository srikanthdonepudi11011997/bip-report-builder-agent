# IT Change Request: RPT-PPM-001 Project Task Listing

**Change type:** Standard · **Category:** Oracle Fusion: BI Publisher report (new)

## Summary
Deploy new BI Publisher report RPT-PPM-001 "Project Task Listing" (PPM) to TEST, then PROD.

## Description
The report lists projects and their tasks with the current project manager, client and task billing code. It supports the weekly project review and billing-code setup checks. The change adds one data model and one report (two layouts) under `/Shared Folders/Custom/PPM/RPT-PPM-001/`. No setup, configuration or transactional data is changed.

## Business justification
Replaces a manual weekly extract and spreadsheet merge. Gives one consistent view of task billing codes so missing codes are caught before billing.

## Objects
| Object | Type | Path |
|---|---|---|
| RPT-PPM-001_DM | Data model | /Shared Folders/Custom/PPM/RPT-PPM-001/ |
| RPT-PPM-001_RPT | Report + RTF layouts (PDF grouped, Excel flat) | /Shared Folders/Custom/PPM/RPT-PPM-001/ |

## Risk and impact
- **Risk:** Low. Read-only SQL. No data changes.
- **Impact:** Available to Project Accountant and PMO Analyst roles. Running with no parameters returns all non-template project tasks.
- **Dependencies:** Environment-specific role IDs / DFF segment resolved and validated in DEV.

## Implementation steps
1. In DEV, archive folder `/Shared Folders/Custom/PPM/RPT-PPM-001/`.
2. Unarchive into the target environment at the same path.
3. Confirm the data model data source is `ApplicationDB_FSCM`.
4. Confirm the role IDs / DFF segment are valid in the target (IDs can differ per environment; rerun discovery query D-1).
5. Grant folder permissions (Read, Run) to Project Accountant and PMO Analyst.
6. Smoke test: run with Business Unit = one BU and confirm output.

## Back-out plan
Delete `/Shared Folders/Custom/PPM/RPT-PPM-001/`. No other objects are affected.

## Testing evidence
`09-test-plan.md` executed in DEV on ____ by ____. Result: ____.

## Approvals
Business owner: PMO Reporting Lead · IT owner: ERP Reporting Team
