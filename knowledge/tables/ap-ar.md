# AP / AR: Payables and Receivables

See `README.md` for the confidence legend and generic discovery queries.

## Payables (AP)

### AP_INVOICES_ALL
- **Purpose / grain:** one row per supplier invoice header.
- **Key columns:** INVOICE_ID (PK), INVOICE_NUM, INVOICE_DATE, GL_DATE, VENDOR_ID, VENDOR_SITE_ID, ORG_ID (BU), INVOICE_AMOUNT, AMOUNT_PAID, INVOICE_CURRENCY_CODE, PAYMENT_STATUS_FLAG, CANCELLED_DATE, INVOICE_TYPE_LOOKUP_CODE
- **Gotchas:** Exclude cancelled invoices with `cancelled_date IS NULL` unless the FSD wants them. `PAYMENT_STATUS_FLAG` values are Y / N / P (partial).
- **Confidence:** HIGH

### AP_INVOICE_LINES_ALL
- **Key columns:** INVOICE_ID, LINE_NUMBER, LINE_TYPE_LOOKUP_CODE, AMOUNT, DESCRIPTION
- **Confidence:** HIGH

### AP_INVOICE_DISTRIBUTIONS_ALL
- **Key columns:** INVOICE_DISTRIBUTION_ID, INVOICE_ID, INVOICE_LINE_NUMBER, DIST_CODE_COMBINATION_ID, AMOUNT, ACCOUNTING_DATE, POSTED_FLAG
- **Gotchas:** Joining headers to distributions multiplies header amounts. Aggregate in a CTE first.
- **Confidence:** HIGH (IDs, AMOUNT, DIST_CODE_COMBINATION_ID); VERIFY (POSTED_FLAG)

### AP_PAYMENT_SCHEDULES_ALL
- **Key columns:** INVOICE_ID, PAYMENT_NUM, DUE_DATE, AMOUNT_REMAINING, GROSS_AMOUNT
- **Confidence:** HIGH

### AP_CHECKS_ALL / AP_INVOICE_PAYMENTS_ALL
- **Key columns:** CHECK_ID, CHECK_NUMBER, CHECK_DATE, AMOUNT, VENDOR_ID (checks); INVOICE_ID, CHECK_ID, AMOUNT (invoice payments)
- **Confidence:** HIGH

### POZ_SUPPLIERS / POZ_SUPPLIERS_V
- **Purpose / grain:** one row per supplier. The name comes from HZ_PARTIES (or VENDOR_NAME in `_V`).
- **Key columns:** VENDOR_ID, SEGMENT1 (supplier number), PARTY_ID, VENDOR_NAME (`_V`)
- **Joins:** `sup.party_id = hp.party_id`
- **Confidence:** HIGH (VENDOR_ID, SEGMENT1, PARTY_ID); VERIFY (VENDOR_NAME on `_V` in your release)

### POZ_SUPPLIER_SITES_ALL_M
- **Key columns:** VENDOR_SITE_ID, VENDOR_ID, VENDOR_SITE_CODE, PRC_BU_ID, EFFECTIVE_START_DATE, EFFECTIVE_END_DATE
- **Gotchas:** `_M` table, so apply C-06.
- **Confidence:** VERIFY

## Receivables (AR)

### RA_CUSTOMER_TRX_ALL
- **Purpose / grain:** one row per AR transaction (invoice, credit memo, debit memo).
- **Key columns:** CUSTOMER_TRX_ID (PK), TRX_NUMBER, TRX_DATE, BILL_TO_CUSTOMER_ID, CUST_TRX_TYPE_SEQ_ID, ORG_ID, INVOICE_CURRENCY_CODE, COMPLETE_FLAG
- **Gotchas:** In Fusion the transaction-type FK is `CUST_TRX_TYPE_SEQ_ID` (not EBS's `CUST_TRX_TYPE_ID`).
- **Confidence:** HIGH (IDs, TRX_NUMBER, TRX_DATE, BILL_TO_CUSTOMER_ID, ORG_ID); VERIFY (CUST_TRX_TYPE_SEQ_ID)

### RA_CUSTOMER_TRX_LINES_ALL
- **Key columns:** CUSTOMER_TRX_LINE_ID, CUSTOMER_TRX_ID, LINE_NUMBER, LINE_TYPE, EXTENDED_AMOUNT, DESCRIPTION
- **Confidence:** HIGH

### AR_PAYMENT_SCHEDULES_ALL
- **Purpose / grain:** one row per installment of a transaction (or per receipt). This is the usual driver for aging reports.
- **Key columns:** PAYMENT_SCHEDULE_ID, CUSTOMER_TRX_ID, CASH_RECEIPT_ID, CUSTOMER_ID, CLASS (INV / CM / DM / PMT …), STATUS (OP / CL), TRX_NUMBER, TRX_DATE, GL_DATE, DUE_DATE, AMOUNT_DUE_ORIGINAL, AMOUNT_DUE_REMAINING, INVOICE_CURRENCY_CODE, ORG_ID
- **Gotchas:** For *as-of* aging, `AMOUNT_DUE_REMAINING` is "now". Historical aging needs applications (AR_RECEIVABLE_APPLICATIONS_ALL) backed out after the as-of date.
- **Confidence:** HIGH

### AR_CASH_RECEIPTS_ALL / AR_RECEIVABLE_APPLICATIONS_ALL
- **Key columns:** CASH_RECEIPT_ID, RECEIPT_NUMBER, RECEIPT_DATE, AMOUNT (receipts); RECEIVABLE_APPLICATION_ID, APPLIED_CUSTOMER_TRX_ID, CASH_RECEIPT_ID, AMOUNT_APPLIED, APPLY_DATE, GL_DATE, STATUS (applications)
- **Confidence:** HIGH (receipts); VERIFY (application column names)

### HZ_CUST_ACCOUNTS / HZ_PARTIES
- **Key columns:** CUST_ACCOUNT_ID, ACCOUNT_NUMBER, PARTY_ID, STATUS (accounts); PARTY_ID, PARTY_NAME, PARTY_NUMBER, PARTY_TYPE (parties)
- **Joins:** `trx.bill_to_customer_id = hca.cust_account_id AND hca.party_id = hp.party_id`
- **Confidence:** HIGH

## Shared

| Object | Use | Confidence |
|---|---|---|
| FUN_ALL_BUSINESS_UNITS_V | BU_ID, BU_NAME for ORG_ID | HIGH |
| GL_CODE_COMBINATIONS | Account segments for distributions (see `gl.md`) | HIGH |
