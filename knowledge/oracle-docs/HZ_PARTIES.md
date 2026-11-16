# HZ_PARTIES
- **Type / owner:** TABLE · HZ (Trading Community; documented in the Sales book)
- **Purpose:** one row per party (person, organization, group)
- **Checked:** 2026-11-15 · current · https://docs.oracle.com/en/cloud/saas/sales/oedms/hzparties-19213.html
- **Columns confirmed ✅:** PARTY_NAME (VARCHAR2 360), PARTY_TYPE (VARCHAR2 30: PERSON / ORGANIZATION / GROUP)
- **Not re-checked on the page:** PARTY_ID (PK in every TCA release; KB confidence HIGH)
- **Indexes:** HZ_PARTIES_N1 (PARTY_NAME, PARTY_TYPE); N8 on UPPER(PARTY_NAME), PARTY_TYPE
- **Notes:** use PARTY_TYPE to tell a client *contact person* from a client *organization* (example D-4 / Q-5).
