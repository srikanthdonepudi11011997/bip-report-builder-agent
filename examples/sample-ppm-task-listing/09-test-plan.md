# Unit Test Plan: RPT-PPM-001 Project Task Listing

Environment: DEV · Tester: ______ · Date: ______ · Queries: `09-validation.sql`

## A. Build checks
| # | Check | Expected | Result |
|---|---|---|---|
| A1 | Data model validates (no ORA- errors) after tokens are resolved | Validates | ☐ |
| A2 | 7 parameters with labels/types/defaults per `06-data-model-params.md` | Match | ☐ |
| A3 | Each LOV returns sorted values without duplicates; Project Number refreshes when BU changes | OK | ☐ |
| A4 | Sample XML elements = 11 column aliases | Match | ☐ |
| A5 | `sql_lint.py` 0 errors, 0 BIP007 after token resolution | 0 / 0 | ☐ |

## B. Parameter tests
| # | Parameter | Scenario | Expected | Result |
|---|---|---|---|---|
| B1 | All | No values | All non-template project tasks; count = V-01 | ☐ |
| B2 | Business Unit | One BU | Only that BU | ☐ |
| B3 | Business Unit | Two BUs | Both BUs only | ☐ |
| B4 | Project Number | One project | Only its tasks; count = V-01 with that project | ☐ |
| B5 | Project Status | Active only | Only active projects | ☐ |
| B6 | Project Manager | One PM | Only projects whose **current** PM is that person | ☐ |
| B7 | Start Date From/To | From = To = a known start date | Projects starting that day included (TRUNC boundary) | ☐ |
| B8 | Start Date | From > To | No rows; no error | ☐ |
| B9 | Chargeable Only | Y | Only CHARGEABLE_FLAG = Y | ☐ |

## C. Data validation
| # | Check | Query | Expected | Result |
|---|---|---|---|---|
| C1 | Row count = independent count | V-01 | Equal | ☐ |
| C2 | No duplicate project/task rows | V-02 | 0 rows | ☐ |
| C3 | Mandatory columns populated (BU, project no/name, task no/name) | V-03 | 0 rows | ☐ |
| C4 | Spot-check 3 projects in the UI (Manage Projects → Parties, Tasks) | V-04 | PM, client, task, billing code match | ☐ |
| C5 | Projects with blank Client Name have no client-contact party | V-05 | All explained | ☐ |
| C6 | Projects with more than one active PM show the latest | V-06 | Matches rule BR-2 | ☐ |

## D. Layout
| # | Check | Expected | Result |
|---|---|---|---|
| D1 | Column order / headers as FSD §4 | Match | ☐ |
| D2 | Start date DD-MON-YYYY | Match | ☐ |
| D3 | PDF grouped by project, sorted BU → project → task | Match | ☐ |
| D4 | Excel flat, filterable, project numbers as text | Match | ☐ |

## E. Security
| # | Check | Expected | Result |
|---|---|---|---|
| E1 | User without Project Accountant / PMO Analyst role cannot open the report | Denied | ☐ |

## F. Sign-off
| Role | Name | Date |
|---|---|---|
| Developer | | |
| BA / Functional | | |
