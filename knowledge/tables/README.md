# Table notes: how to read and extend them

Each module file (`ppm.md`, `hcm.md`, `ap-ar.md`, `gl.md`) lists Fusion tables and views with:

- **Purpose**: what one row represents (the *grain*)
- **Key columns**: only columns we have seen used in working BIP SQL or in Oracle's published table docs
- **Joins**: proven join paths
- **Gotchas**: things that have bitten us
- **Confidence**:
  - `HIGH`: used in working BIP SQL
  - `VERIFY`: believed correct but not yet confirmed in your environment. The agent must emit a discovery query before relying on it.

> **The agent may only use tables and columns listed here, in reuse SQL the user provided, or confirmed by the user.** Anything else gets a discovery query.

## Generic discovery queries

Run these in a BIP data model in DEV. Discovery only; never ship them.

```sql
-- 1. What columns does an object have?
SELECT column_name, data_type, data_length, nullable
FROM   all_tab_columns
WHERE  table_name = UPPER('&table_or_view')
ORDER  BY column_id;

-- 2. If dictionary views are not accessible, peek at the data instead
SELECT * FROM &table_or_view WHERE ROWNUM <= 5;

-- 3. Which objects match a name pattern?
SELECT owner, object_name, object_type
FROM   all_objects
WHERE  object_name LIKE UPPER('%&pattern%')
AND    object_type IN ('TABLE', 'VIEW', 'SYNONYM')
ORDER  BY object_name;

-- 4. Which tables have a column with this name? (useful for finding join keys)
SELECT table_name
FROM   all_tab_columns
WHERE  column_name = UPPER('&column_name')
ORDER  BY table_name;
```

> If `all_tab_columns` / `all_objects` return no rows or `ORA-00942`, your data-source user can't see the dictionary. Use query 2 and Oracle's *Tables and Views for Oracle Fusion Cloud* guide for your release.

## Entry template

```markdown
### TABLE_NAME
- **Purpose / grain:** one row per …
- **Key columns:** COL_A (PK), COL_B (FK → OTHER.COL), …
- **Joins:** `alias.col = other.col`
- **Gotchas:** …
- **Confidence:** HIGH | VERIFY
```
