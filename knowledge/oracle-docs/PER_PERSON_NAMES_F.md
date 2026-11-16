# PER_PERSON_NAMES_F
- **Type / owner:** TABLE · PER
- **Purpose:** date-effective person names per name type
- **Checked:** 2026-11-15 · current HCM book (no release in URL) · https://docs.oracle.com/en/cloud/saas/human-resources/oedmh/perpersonnamesf-32501.html
- **Primary key:** PER_PERSON_NAMES_F_PK (PERSON_NAME_ID, EFFECTIVE_START_DATE, EFFECTIVE_END_DATE)
- **Columns confirmed ✅:** PERSON_ID (not null), NAME_TYPE (not null), FULL_NAME, DISPLAY_NAME, FIRST_NAME, LAST_NAME (not null), EFFECTIVE_START_DATE, EFFECTIVE_END_DATE
- **Notes:** the PK includes the effective dates, and there are several rows per person (name types) → `name_type = 'GLOBAL'` + effective-date filter (lessons L-003).
