# GL: General Ledger

See `README.md` for the confidence legend and generic discovery queries.

### GL_LEDGERS
- **Key columns:** LEDGER_ID (PK), NAME, CURRENCY_CODE, CHART_OF_ACCOUNTS_ID, PERIOD_SET_NAME, ACCOUNTED_PERIOD_TYPE
- **Confidence:** HIGH

### GL_PERIODS / GL_PERIOD_STATUSES
- **Key columns:** PERIOD_SET_NAME, PERIOD_NAME, PERIOD_YEAR, PERIOD_NUM, START_DATE, END_DATE, ADJUSTMENT_PERIOD_FLAG (periods); LEDGER_ID, APPLICATION_ID, PERIOD_NAME, CLOSING_STATUS (statuses)
- **Gotchas:** Exclude adjustment periods (`adjustment_period_flag = 'N'`) in LOVs unless asked. Join periods on `period_set_name` **and** `period_type` to avoid duplicates.
- **Confidence:** HIGH

### GL_JE_BATCHES / GL_JE_HEADERS / GL_JE_LINES
- **Key columns:**
  - Batches: JE_BATCH_ID, NAME, STATUS
  - Headers: JE_HEADER_ID, JE_BATCH_ID, LEDGER_ID, PERIOD_NAME, JE_SOURCE, JE_CATEGORY, NAME, STATUS (P = posted), CURRENCY_CODE, ACTUAL_FLAG
  - Lines: JE_HEADER_ID, JE_LINE_NUM, CODE_COMBINATION_ID, ENTERED_DR, ENTERED_CR, ACCOUNTED_DR, ACCOUNTED_CR, DESCRIPTION, EFFECTIVE_DATE
- **Gotchas:** `GL_JE_LINES` is huge. Always filter on ledger + period. `JE_SOURCE` / `JE_CATEGORY` hold internal names; join the `_TL` tables for user-facing names.
- **Confidence:** HIGH

### GL_JE_SOURCES_TL / GL_JE_CATEGORIES_TL
- **Key columns:** JE_SOURCE_NAME, USER_JE_SOURCE_NAME, LANGUAGE; JE_CATEGORY_NAME, USER_JE_CATEGORY_NAME, LANGUAGE
- **Confidence:** VERIFY

### GL_CODE_COMBINATIONS
- **Key columns:** CODE_COMBINATION_ID (PK), CHART_OF_ACCOUNTS_ID, SEGMENT1 … SEGMENT30, ENABLED_FLAG, ACCOUNT_TYPE
- **Gotchas:** **Which SEGMENTn is Company, Cost Center, Account, etc. is environment-specific.** Put the mapping in `private/environment.md` (`{{GL_SEGMENT_<NAME>}}`).
- **Confidence:** HIGH

### GL_BALANCES
- **Key columns:** LEDGER_ID, CODE_COMBINATION_ID, CURRENCY_CODE, PERIOD_NAME, ACTUAL_FLAG, BEGIN_BALANCE_DR, BEGIN_BALANCE_CR, PERIOD_NET_DR, PERIOD_NET_CR
- **Gotchas:** Filter `actual_flag = 'A'` for actuals. Pick translated vs entered currency deliberately (`currency_code` = ledger currency for functional balances).
- **Confidence:** HIGH

### FND_FLEX_VALUES_VL
- **Purpose / grain:** segment value descriptions.
- **Key columns:** FLEX_VALUE_SET_ID, FLEX_VALUE, DESCRIPTION, ENABLED_FLAG
- **Confidence:** VERIFY (value-set ID per segment is environment-specific)

### XLA_AE_HEADERS / XLA_AE_LINES / GL_IMPORT_REFERENCES
- **Purpose:** drill from GL journals back to subledger accounting.
- **Key columns:** AE_HEADER_ID, AE_LINE_NUM, GL_SL_LINK_ID, GL_SL_LINK_TABLE (XLA); JE_HEADER_ID, JE_LINE_NUM, GL_SL_LINK_ID, GL_SL_LINK_TABLE (import refs)
- **Joins:** `gir.gl_sl_link_id = xal.gl_sl_link_id AND gir.gl_sl_link_table = xal.gl_sl_link_table`
- **Gotchas:** Also join on `application_id` where available; partitioned and high volume.
- **Confidence:** VERIFY
