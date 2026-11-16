# IT Change Request: {{REPORT_ID}} {{TITLE}}

**Change type:** Standard / Normal · **Category:** Oracle Fusion: BI Publisher report (new | modification)

## Summary (one line)
Deploy BI Publisher report {{REPORT_ID}} "{{TITLE}}" ({{MODULE}}) to {{TARGET_ENV}}.

## Description
{{PURPOSE}} The change adds a new data model and report to the BI catalog under `/Shared Folders/Custom/{{MODULE}}/{{REPORT_ID}}/`. No setup, configuration or transactional data is changed.

## Business justification
…

## Objects
| Object | Type | Path |
|---|---|---|
| {{REPORT_ID}}_DM | Data model (.xdm) | /Shared Folders/Custom/{{MODULE}}/{{REPORT_ID}}/ |
| {{REPORT_ID}}_RPT | Report (.xdo) incl. RTF layout | /Shared Folders/Custom/{{MODULE}}/{{REPORT_ID}}/ |

## Risk and impact
- **Risk:** Low. Read-only SQL. No data changes.
- **Impact:** Users with the report role can run the report. Performance is bounded by mandatory parameters: …
- **Dependencies:** None / Role assignment: …

## Implementation steps
1. Archive `{{REPORT_ID}}` folder in DEV (BI Catalog → Archive).
2. Unarchive into {{TARGET_ENV}} at the same path.
3. Confirm the data source name on the data model.
4. Grant permissions on the folder to role(s): …
5. Smoke test: run with default parameters and confirm output is produced.

## Back-out plan
Delete (or restore the previous archive of) `/Shared Folders/Custom/{{MODULE}}/{{REPORT_ID}}/`. No other objects are affected.

## Testing evidence
Unit test plan `09-test-plan.md` executed in DEV on ____ by ____. Result: Pass.

## Approvals
Business owner: ____ · IT owner: ____
