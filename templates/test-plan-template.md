# Unit Test Plan: {{REPORT_ID}} {{TITLE}}

Environment: DEV · Tester: ______ · Date: ______

Validation queries live in `09-validation.sql`. Run them in the same data source as the data model.

## A. Build checks
| # | Check | Expected | Result | Notes |
|---|---|---|---|---|
| A1 | Data model SQL validates in BIP (no ORA- errors) | Validates | ☐ Pass ☐ Fail | |
| A2 | All parameters appear with correct labels, types and defaults | Matches `06-data-model-params.md` | ☐ | |
| A3 | Each LOV returns values, sorted, no duplicates | Values visible | ☐ | |
| A4 | Sample XML generated; element names match column aliases | Matches spec | ☐ | |
| A5 | `sql_lint.py` shows 0 errors | 0 errors | ☐ | |

## B. Parameter tests (one row per parameter × scenario)
| # | Parameter | Scenario | Expected | Result |
|---|---|---|---|---|
| B1 | {{param}} | No value (multi-select → all) | All rows returned | ☐ |
| B2 | {{param}} | Single value | Only matching rows | ☐ |
| B3 | {{param}} | Multiple values | Union of matches | ☐ |
| B4 | {{date_param}} | Boundary date (= From / = To) | Boundary rows included | ☐ |

## C. Data validation
| # | Check | Query (09-validation.sql) | Expected | Result |
|---|---|---|---|---|
| C1 | Row count matches independent count | V-01 | Equal | ☐ |
| C2 | No duplicates at the expected grain | V-02 | 0 rows | ☐ |
| C3 | Mandatory columns not null | V-03 | 0 rows | ☐ |
| C4 | Spot-check 3 records against the Fusion UI | V-04 | Values match UI | ☐ |
| C5 | Optional columns null only when expected (business rule) | V-05 | Explained | ☐ |

## D. Layout
| # | Check | Expected | Result |
|---|---|---|---|
| D1 | Column order and headers as FSD | Match | ☐ |
| D2 | Date / number formats | As `07-rtf-layout.md` | ☐ |
| D3 | Grouping / sorting | As FSD | ☐ |
| D4 | Excel output opens with no formatting errors | OK | ☐ |

## E. Security
| # | Check | Expected | Result |
|---|---|---|---|
| E1 | User without the report role cannot see/run the report | Denied | ☐ |
| E2 | Data security (BU / project) respected, if applicable | Restricted | ☐ |

## F. Sign-off
| Role | Name | Date | Signature |
|---|---|---|---|
| Developer | | | |
| BA / Functional | | | |
