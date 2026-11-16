# PJF_PROJECT_PARTIES
- **Type / owner:** TABLE · PJF
- **Purpose:** people / parties assigned to a project in a project role, with date ranges
- **Checked:** 2026-11-15 · release 25C · https://docs.oracle.com/en/cloud/saas/project-management/25c/oedpp/pjfprojectparties-25874.html
- **Primary key:** PJF_PROJECT_PARTIES_PK (PROJECT_PARTY_ID)
- **Columns (all 21) ✅:** PROJECT_PARTY_ID, OBJECT_ID, OBJECT_TYPE, PROJECT_ID, RESOURCE_ID, RESOURCE_SOURCE_ID, PROJECT_PARTY_TYPE, RELATIONSHIP_ID, PROJECT_ROLE_ID, START_DATE_ACTIVE, END_DATE_ACTIVE, PJS_TRACK_TIME, SCHEDULED_FLAG, PROJ_RESOURCE_ID, LDAP_REQUEST_ID, CREATION_DATE, CREATED_BY, LAST_UPDATE_DATE, LAST_UPDATED_BY, LAST_UPDATE_LOGIN, OBJECT_VERSION_NUMBER
- **Indexes:** N1–N6, U1, U2
- **Notes:** RELATIONSHIP_ID exists, which is useful if the client organization must be reached through the contact's relationship (example Q-5). The preferred client source; see lessons L-001.
