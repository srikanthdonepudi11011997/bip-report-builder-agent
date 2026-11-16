# HCM: Global Human Resources (People, Assignments, Organizations)

See `README.md` for the confidence legend and generic discovery queries. Most HCM tables are **date-effective** (`_F`) or **multi-change-per-day** (`_M`). Apply conventions C-06 everywhere.

### PER_ALL_PEOPLE_F
- **Purpose / grain:** one row per person per effective date range.
- **Key columns:** PERSON_ID, PERSON_NUMBER, EFFECTIVE_START_DATE, EFFECTIVE_END_DATE
- **Gotchas:** Names are *not* here; use PER_PERSON_NAMES_F.
- **Confidence:** HIGH

### PER_PERSON_NAMES_F
- **Purpose / grain:** one row per person per name type per effective date range.
- **Key columns:** PERSON_ID, NAME_TYPE, FULL_NAME, DISPLAY_NAME, FIRST_NAME, LAST_NAME, EFFECTIVE_START_DATE, EFFECTIVE_END_DATE
- **Gotchas:** Always filter `name_type = 'GLOBAL'`, or you get one row per legislative name format (a classic duplicate-row cause).
- **Confidence:** HIGH

### PER_ALL_ASSIGNMENTS_M
- **Purpose / grain:** one row per assignment per effective change (several per day possible).
- **Key columns:** ASSIGNMENT_ID, PERSON_ID, ASSIGNMENT_NUMBER, ASSIGNMENT_TYPE, PRIMARY_FLAG, ASSIGNMENT_STATUS_TYPE, BUSINESS_UNIT_ID, ORGANIZATION_ID (department), JOB_ID, GRADE_ID, POSITION_ID, LOCATION_ID, EFFECTIVE_START_DATE, EFFECTIVE_END_DATE, EFFECTIVE_LATEST_CHANGE
- **Gotchas:**
  - Filter `assignment_type IN ('E','C')` (employee/contingent worker) as the FSD requires. Without it you also get pending workers and other types.
  - `primary_flag = 'Y'` for the primary assignment; `effective_latest_change = 'Y'` for `_M`.
  - `ASSIGNMENT_STATUS_TYPE` (e.g. ACTIVE / INACTIVE / SUSPENDED) is the quick active check. Confirm values in DEV.
- **Confidence:** HIGH (IDs, PRIMARY_FLAG, ASSIGNMENT_TYPE, effective columns, EFFECTIVE_LATEST_CHANGE); VERIFY (ASSIGNMENT_STATUS_TYPE values)

### PER_ASSIGNMENT_SUPERVISORS_F
- **Purpose / grain:** supervisor relationships per assignment.
- **Key columns:** ASSIGNMENT_ID, PERSON_ID, MANAGER_ID, MANAGER_TYPE, PRIMARY_FLAG, EFFECTIVE_START_DATE, EFFECTIVE_END_DATE
- **Gotchas:** Filter `manager_type = 'LINE_MANAGER'` and `primary_flag = 'Y'` for "the" manager. Dedupe anyway (C-07).
- **Confidence:** VERIFY

### PER_JOBS_F_TL / PER_JOBS_F_VL
- **Key columns:** JOB_ID, NAME, LANGUAGE (`_TL`), effective dates
- **Confidence:** VERIFY

### PER_GRADES_F_TL
- **Key columns:** GRADE_ID, NAME, LANGUAGE, effective dates
- **Confidence:** VERIFY

### HR_ALL_ORGANIZATION_UNITS_F / HR_ORGANIZATION_UNITS_F_TL
- **Purpose / grain:** organizations (departments, BUs, legal entities) per effective date; TL holds NAME.
- **Key columns:** ORGANIZATION_ID, NAME (`_TL`), LANGUAGE, EFFECTIVE_START_DATE, EFFECTIVE_END_DATE
- **Gotchas:** The TL is date-effective too, so apply C-05 **and** C-06.
- **Confidence:** HIGH

### PER_LOCATION_DETAILS_F_VL
- **Key columns:** LOCATION_ID, LOCATION_CODE, LOCATION_NAME, effective dates
- **Confidence:** VERIFY

### PER_EMAIL_ADDRESSES
- **Key columns:** PERSON_ID, EMAIL_TYPE, EMAIL_ADDRESS, DATE_FROM, DATE_TO
- **Gotchas:** Filter `email_type = 'W1'` for work email (confirm the lookup code in DEV); dedupe.
- **Confidence:** VERIFY

### PER_PERIODS_OF_SERVICE
- **Key columns:** PERIOD_OF_SERVICE_ID, PERSON_ID, DATE_START, ACTUAL_TERMINATION_DATE
- **Confidence:** VERIFY

### PER_USERS
- **Key columns:** USER_ID, USERNAME, PERSON_ID, ACTIVE_FLAG
- **Gotchas:** Only for security/user-mapping reports. User names are personal data, so treat output accordingly.
- **Confidence:** VERIFY
