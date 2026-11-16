# Metadata Catalog Entry: RPT-PPM-001

```yaml
name: "RPT-PPM-001 Project Task Listing"
type: "BI Publisher Report"
system: "Oracle Fusion Cloud: Project Portfolio Management"
catalog_path: "/Shared Folders/Custom/PPM/RPT-PPM-001/RPT-PPM-001_RPT.xdo"
description: >
  Lists non-template projects and their tasks with the current project
  manager, client contact and task billing code. Used for the weekly project
  review and to check billing-code setup.
business_owner: "PMO Reporting Lead"
technical_owner: "ERP Reporting Team"
refresh: "On demand"
output_formats: [Excel, PDF]
grain: "One row per project task"
parameters:
  - { label: "Business Unit",           bind: ":p_business_unit",   type: string, multi_select: true,  required: false }
  - { label: "Project Number",          bind: ":p_project_number",  type: string, multi_select: true,  required: false }
  - { label: "Project Status",          bind: ":p_project_status",  type: string, multi_select: true,  required: false }
  - { label: "Project Manager",         bind: ":p_project_manager", type: string, multi_select: true,  required: false }
  - { label: "Project Start Date From", bind: ":p_start_date_from", type: date,   multi_select: false, required: false }
  - { label: "Project Start Date To",   bind: ":p_start_date_to",   type: date,   multi_select: false, required: false }
  - { label: "Chargeable Tasks Only",   bind: ":p_chargeable_only", type: string, multi_select: false, required: false, default: "N" }
columns:
  - { name: BUSINESS_UNIT,      description: "Project business unit" }
  - { name: PROJECT_NUMBER,     description: "Project number" }
  - { name: PROJECT_NAME,       description: "Project name (user language)" }
  - { name: PROJECT_STATUS,     description: "Project status name" }
  - { name: PROJECT_START_DATE, description: "Project start date" }
  - { name: PROJECT_MANAGER,    description: "Project manager active on the run date" }
  - { name: CLIENT_NAME,        description: "Client contact from the project's Parties tab; blank if none" }
  - { name: TASK_NUMBER,        description: "Task number" }
  - { name: TASK_NAME,          description: "Task name" }
  - { name: BILLING_CODE,       description: "Task billing code (task descriptive flexfield)" }
  - { name: CHARGEABLE_FLAG,    description: "Y if the task accepts charges" }
source_tables:
  - PJF_PROJECTS_ALL_B
  - PJF_PROJECTS_ALL_TL
  - PJF_PROJECT_STATUSES_TL
  - PJF_PROJECT_PARTIES
  - PJF_TASKS_V
  - PER_PERSON_NAMES_F
  - HZ_PARTIES
  - FUN_ALL_BUSINESS_UNITS_V
tags: [bip, oracle-fusion, ppm, projects, tasks]
data_classification: "Internal"
known_limitations:
  - "Client Name blank when no client contact is assigned on the Parties tab"
  - "Fusion PPM data security is not applied; access is controlled by catalog role"
related_documents: [FSD v1.0, TSD v0.1]
```

## Description
**What it answers:** Which tasks exist on which projects, who manages them, who the client is, and whether each task has a billing code.
**Who uses it:** PMO, Project Accountants.
**How to run:** Reports and Analytics → Browse Catalog → Shared Folders → Custom → PPM → RPT-PPM-001.
**Caveats:** Leave Business Unit blank to include all BUs (can be large).
