# Functional Specification: Project Task Listing

> **SANITIZED EXAMPLE.** Fictional organization ("Example Org"), fictional data. Written to look like a typical FSD, including a few deliberate ambiguities so the agent's "flag, don't guess" behavior can be seen.

## 1. Document Control

| Item | Value |
|---|---|
| Report ID | RPT-PPM-001 |
| Report Name | Project Task Listing |
| Module | Project Portfolio Management (PPM) |
| Version | 1.0 |
| Requested by | PMO Reporting Lead |

## 2. Purpose

The PMO needs a list of active projects and their tasks, showing the project manager, the client and the billing code on each task. It is used in the weekly project review and for checking that task billing codes are set up correctly.

## 3. Parameters

| # | Parameter | Type | Mandatory | Multi-select | Default | Notes |
|---|---|---|---|---|---|---|
| 1 | Business Unit | Text (LOV) | No | Yes | All | |
| 2 | Project Number | Text (LOV) | No | Yes | All | Should only show projects in the selected BU(s) |
| 3 | Project Status | Text (LOV) | No | Yes | All | |
| 4 | Project Manager | Text (LOV) | No | Yes | All | |
| 5 | Project Start Date From | Date | No | No | | |
| 6 | Project Start Date To | Date | No | No | | |
| 7 | Chargeable Tasks Only | Yes/No | No | No | No | |

## 4. Output Columns

| # | Column Header | Description / Source |
|---|---|---|
| 1 | Business Unit | Project business unit |
| 2 | Project Number | |
| 3 | Project Name | |
| 4 | Project Status | Status as shown on the project |
| 5 | Project Start Date | DD-MON-YYYY |
| 6 | Project Manager | Current project manager |
| 7 | Client Name | Client from the project's Parties tab |
| 8 | Task Number | |
| 9 | Task Name | |
| 10 | Billing Code | Task-level descriptive flexfield "Billing Code" |
| 11 | Chargeable | Y/N |

## 5. Filters and Business Rules

1. Exclude project templates.
2. Show the current project manager only. If more than one, show the most recent.
3. Client name comes from the client contact on the project's Parties tab.
4. The report should show active projects.
5. Sort by Business Unit, Project Number, Task Number.
6. Group the output by project.

## 6. Sample Output

| Business Unit | Project Number | Project Name | Project Status | Project Start Date | Project Manager | Client Name | Task Number | Task Name | Billing Code | Chargeable |
|---|---|---|---|---|---|---|---|---|---|---|
| EX US BU | PRJ-10001 | Website Refresh | Active | 01-MAR-2026 | Jordan Lee | Acme Example Inc | 1.0 | Discovery | BC-100 | Y |
| EX US BU | PRJ-10001 | Website Refresh | Active | 01-MAR-2026 | Jordan Lee | Acme Example Inc | 2.0 | Build | BC-200 | Y |

## 7. Security

Available to users with the Project Accountant and PMO Analyst roles.

## 8. Output Format

Excel (primary), PDF.
