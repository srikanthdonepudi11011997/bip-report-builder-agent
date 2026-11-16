# FUN_ALL_BUSINESS_UNITS_V
- **Type / owner:** VIEW · FUN
- **Purpose:** business units
- **Checked:** 2026-11-15 · release 25D · https://docs.oracle.com/en/cloud/saas/financials/25d/oedmf/funallbusinessunitsv-5127.html
- **Columns (all) ✅:** BU_ID, BU_NAME, LOCATION_ID, BUSINESS_GROUP_ID, DATE_FROM, DATE_TO, MANAGER_ID, LEGAL_ENTITY_ID, PRIMARY_LEDGER_ID, DEFAULT_SET_ID, SHORT_CODE, ENABLED_FOR_HR_FLAG, FIN_BUSINESS_UNIT_ID, DEFAULT_CURRENCY_CODE, PROFIT_CENTER_FLAG, STATUS, CREATED_BY, CREATION_DATE, LAST_UPDATED_BY, LAST_UPDATE_DATE, LAST_UPDATE_LOGIN
- **Notes:** other Oracle views filter active BUs with `STATUS = 'A'`. Consider it in BU LOVs.
