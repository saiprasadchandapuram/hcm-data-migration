# Data Quality Report – Employee Data Migration

**Project:** Employee Data Migration to Oracle Cloud HCM (synthetic data)
**Prepared by:** Sai Prasad Chandapuram

---

## 1. Executive Summary

We profiled **300** legacy employee records from the source Excel file.

- **260** records are migration-ready after automated cleaning.
- **31** records were rejected (blank employee ID, exit date before joining date, or missing joining date) and need business input before they can be migrated.
- **9** duplicate records were removed.

Data Quality Score: **86.7%**

---

## 2. Scope and Method

- **Source file:** legacy_employee_data_messy.xlsx (16 columns, 300 rows, synthetic data)
- **Tools:** Python, Pandas, Excel
- **Steps:**
  1. Profiled every column to find inconsistent values
  2. Mapped each source column to an Oracle HCM field (see docs/02_field_mapping.xlsx)
  3. Cleaned and standardised the data with a Python script
  4. Applied cross-field checks and logged every fix and rejection
- **Standardisation results:** all department, job, grade and location values were matched to the standard lists, with 0 unmatched values. Dates were converted to YYYY/MM/DD.
- **Assumption to confirm with HR:** a blank grade was defaulted to GRADE_1.
- **Known limitation:** rows with a missing joining date are rejected by the load filter but are not listed as separate items in the error log.

---

## 3. Findings

| Issue | Rows Affected | Severity | Action Taken |
|-------|---------------|----------|--------------|
| Blank employee ID | 5 | Critical | Row rejected |
| Duplicate employee ID | 9 | Critical | Row removed (first record kept) |
| Exit date before joining date | 17 | Critical | Row rejected, needs HR confirmation |
| Active employee with an exit date | 5 | High | Flagged for HR review |
| Missing or non-numeric salary | 13 | High | Left blank |
| Salary zero or negative | 8 | High | Left blank |
| Missing EMP prefix on employee ID | 5 | Medium | Prefix added |
| Last-name-first format | 11 | Medium | Reordered |
| Blank email | 12 | Medium | Left blank |
| Invalid email format | 11 | Medium | Left blank |
| Blank gender | 25 | Medium | Left blank |
| Blank grade | 13 | Medium | Defaulted to GRADE_1 |
| Phone not exactly 10 digits | 16 | Medium | Left blank |

Total fixes and rejections logged: **150**.

---

## 4. Critical Issues Needing Business Decision

These records are blocked from migration until HR confirms the correct values:

1. **17** rows have an Exit Date earlier than the Joining Date.
   → HR must confirm the correct dates. These rows are rejected.

2. **5** rows are marked ACTIVE but still have an Exit Date.
   → HR must decide whether the employee is truly active or the status/date is wrong.

3. **5** rows have a blank Emp ID.
   → Business must provide a valid unique employee number. These rows are rejected.

4. **9** duplicate Emp IDs were found and removed (first record kept).
   → Confirm which record is the correct master record.

Until these decisions are received, the affected rows remain in the Rejected set.

---

## 5. Data Quality Score

| Metric                        | Value      |
|-------------------------------|------------|
| Total source records          | 300        |
| Duplicates removed            | 9          |
| Clean (migration-ready)       | 260        |
| Rejected / blocked            | 31         |
| **Data Quality Score**        | **86.7%**  |

**Formula:** Clean rows ÷ Total rows × 100

---

## 6. Recommendations

- Make Emp ID mandatory and unique at the source
- Use one standard list for Department, Job, Grade and Location
- Validate dates at the point of entry
- Do not allow an exit date before the joining date
- Use a dropdown for Gender and Status
- Run the cleansing script as a mandatory pre-load step for future extracts

---

## 7. Sign-off

| Role        | Name                         | Signature | Date |
|-------------|------------------------------|-----------|------|
| Prepared by | Sai Prasad Chandapuram       |           |      |
| Reviewed by |                              |           |      |
| Approved by |                              |           |      |
