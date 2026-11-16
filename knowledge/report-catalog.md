# Report Catalog

Past reports the agent can learn from and reuse SQL from. **Keep entries generic** (use your own neutral IDs like `RPT-PPM-001`). Store the real mapping to internal report IDs in `private/`.

When `/build-report` is given "reuse X", the agent looks up X here, then in `output/X/04-data-model.sql`.

| Report ID | Title | Module | Purpose | Key tables | Reusable CTEs | Gotchas |
|---|---|---|---|---|---|---|
| RPT-PPM-001 | Project Task Listing *(example)* | PPM | List projects and tasks with project manager, client and a task-level DFF code | PJF_PROJECTS_ALL_B/_TL, PJF_TASKS_V, PJF_PROJECT_PARTIES, HZ_PARTIES, PER_PERSON_NAMES_F, FUN_ALL_BUSINESS_UNITS_V | `project_manager`, `project_client`, `projects` | Client blank if no client-contact party; task DFF segment is environment-specific (L-001, L-002) |

## Entry template

```markdown
| RPT-<MOD>-NNN | <title> | <PPM/HCM/AP/AR/GL> | <one-line purpose> | <tables> | <CTE names worth reusing> | <gotchas / lesson IDs> |
```

## Reusable CTE snippets

Lift these only from SQL that has actually run in DEV. Paste the snippet here with a `-- SOURCE:` comment so the generator can reuse it verbatim.

```sql
-- SOURCE: RPT-PPM-001 (example) — validated pattern, environment tokens unresolved
-- CTE: project_manager — current project manager per project (grain: one row per project)
project_manager AS (
    SELECT pp.project_id,
           ppnf.full_name AS project_manager_name,
           ROW_NUMBER() OVER (PARTITION BY pp.project_id
                              ORDER BY pp.start_date_active DESC, pp.project_party_id DESC) AS rn
    FROM   pjf_project_parties pp
    JOIN   per_person_names_f  ppnf
           ON  ppnf.person_id = pp.resource_source_id
           AND ppnf.name_type = 'GLOBAL'
           AND TRUNC(SYSDATE) BETWEEN ppnf.effective_start_date AND ppnf.effective_end_date
    WHERE  pp.project_role_id = {{PROJECT_MANAGER_ROLE_ID}}
    AND    TRUNC(SYSDATE) BETWEEN TRUNC(pp.start_date_active)
                              AND NVL(TRUNC(pp.end_date_active), TRUNC(SYSDATE))
)
```
