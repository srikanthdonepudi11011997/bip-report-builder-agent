# Technical Specification: {{REPORT_ID}} {{TITLE}}

| Item | Value |
|---|---|
| Report ID | {{REPORT_ID}} |
| Title | {{TITLE}} |
| Module | {{MODULE}} |
| Version | {{VERSION}} |
| Related FSD | {{SOURCE_DOCUMENT}} |
| Author | BIP Report Builder Agent (draft), reviewed by: ______ |
| Date | {{DATE}} |
| Status | Draft / In Review / Approved |

## 1. Purpose
{{PURPOSE}}

## 2. Scope
- **In scope:** …
- **Out of scope:** …
- **Expected grain:** one row per {{GRAIN}}

## 3. Assumptions and open questions
| ID | Type | Text | Blocking? |
|---|---|---|---|
| A-1 | Assumption | … | — |
| Q-1 | Question | … | Yes/No |

## 4. Technical design

### 4.1 Catalog objects
| Object | Path (BI Catalog) |
|---|---|
| Data model | `/Shared Folders/Custom/{{MODULE}}/{{REPORT_ID}}/{{REPORT_ID}}_DM.xdm` |
| Report | `/Shared Folders/Custom/{{MODULE}}/{{REPORT_ID}}/{{REPORT_ID}}_RPT.xdo` |
| Layout | `{{REPORT_ID}}_Layout.rtf` |

### 4.2 Data source
- Data source: `ApplicationDB_FSCM` (PPM/Financials) or `ApplicationDB_HCM` (HCM). Confirm.
- Data set: SQL query (`04-data-model.sql`)

### 4.3 Source tables and views
| Table / view | Purpose in this report | Join | Confidence |
|---|---|---|---|

### 4.4 Query structure (CTEs)
| CTE | Business concept | Grain | Notes / dedupe key |
|---|---|---|---|

### 4.5 Parameters
| # | Label | Bind | Type | Multi | Required | Default | LOV |
|---|---|---|---|---|---|---|---|

### 4.6 LOVs
| LOV | Query summary | Returns |
|---|---|---|

### 4.7 Column mapping
| # | Header | Alias | Source (table.column / logic) | Format |
|---|---|---|---|---|

### 4.8 Business rules → implementation
| Rule | Description | Implemented in |
|---|---|---|

### 4.9 Conventions applied
Multi-select null checks (C-02), TO_CHAR on numeric IDs (C-03), TRUNC on dates (C-04), `_TL` language filter (C-05), effective dating (C-06), ROW_NUMBER dedupe (C-07), forbidden objects avoided (C-08).

## 5. Layout
See `07-rtf-layout.md`. Output formats: {{OUTPUT_FORMATS}}.

## 6. Security
- Report access roles: …
- Data security: …
- Personal data in output: Yes/No → handling: …

## 7. Performance considerations
- Driving filters: …
- Expected volume: …

## 8. Error handling and known limitations
- …

## 9. Testing
See `09-test-plan.md` and `09-validation.sql`.

## 10. Deployment
- Migration: export the catalog objects (`.xdmz`/`.xdoz`) from DEV → import to TEST → PROD via the CR in `10-it-change-request.md`.

## 11. Change log
| Version | Date | Author | Change |
|---|---|---|---|
| 0.1 | {{DATE}} | BIP Report Builder Agent | Initial draft |
