# Lessons Learned

The `debugger` sub-agent appends here after every fixed DEV error. The `sql-generator` and `sql-reviewer` read this file **before** every build, and a lesson here overrides a general table note.

**Sanitize every entry.** No real report IDs, client or company names, people or environment IDs. Use generic wording ("a PPM project listing report").

## Entry template

```markdown
### L-NNN <short title>
- **Date:** YYYY-MM-DD
- **Module / object:** e.g. PPM / PJF_PROJECT_CUSTOMERS
- **Symptom:** exact error code or the wrong-output pattern
- **Root cause:** …
- **Fix:** what changed in the SQL (show the pattern, not the whole query)
- **Rule going forward:** the instruction the generator must follow next time
- **Updated:** conventions.md C-xx / tables/<module>.md / sql_lint.py rule (if any)
```

---

### L-001 PJF_PROJECT_CUSTOMERS raises ORA-00942
- **Date:** 2026-11-15
- **Module / object:** PPM / PJF_PROJECT_CUSTOMERS
- **Symptom:** `ORA-00942: table or view does not exist` when the data model referenced `PJF_PROJECT_CUSTOMERS` to get the project client.
- **Root cause:** The object is not exposed to (or not granted to) the BIP data-source user in some environments.
- **Fix:** Derive the client from `PJF_PROJECT_PARTIES`, filtered on the client-contact project role (`{{CLIENT_CONTACT_ROLE_ID}}`), joined to `HZ_PARTIES` on `RESOURCE_SOURCE_ID`, deduped with `ROW_NUMBER()`.
- **Rule going forward:** Never use `PJF_PROJECT_CUSTOMERS`. Note in the TSD that client name is blank when no client-contact party is assigned on the project's Parties tab.
- **Updated:** conventions.md C-08, C-11; tables/ppm.md; sql_lint.py BIP005

### L-002 Task DFF attribute is context-dependent
- **Date:** 2026-11-15
- **Module / object:** PPM / PJF_TASKS_V.ATTRIBUTEn
- **Symptom:** A task DFF column returned values for some projects and unrelated values for others.
- **Root cause:** The `ATTRIBUTEn` slot was used by more than one DFF context. Its meaning depended on `ATTRIBUTE_CATEGORY`.
- **Fix:** Use the segment confirmed as global (or filter on the right `ATTRIBUTE_CATEGORY`). Take the segment from `private/environment.md` (`{{TASK_DFF_<NAME>}}`).
- **Rule going forward:** Never pick a DFF `ATTRIBUTEn` by guesswork. Always use the environment mapping, and note the context in the TSD.
- **Updated:** conventions.md C-11; tables/ppm.md

### L-003 Duplicate rows from person names
- **Date:** 2026-11-15
- **Module / object:** HCM / PER_PERSON_NAMES_F
- **Symptom:** Each project or employee appeared 2–3 times.
- **Root cause:** Missing `name_type = 'GLOBAL'` filter (one row per name format) and no effective-date filter.
- **Fix:** Add `ppnf.name_type = 'GLOBAL' AND TRUNC(SYSDATE) BETWEEN ppnf.effective_start_date AND ppnf.effective_end_date`.
- **Rule going forward:** Every PER_PERSON_NAMES_F join carries both filters. Wrap 1:many lookups in a `ROW_NUMBER()` CTE (C-07).
- **Updated:** tables/hcm.md
