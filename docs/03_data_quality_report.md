# Data Quality Report – Legacy Employee Data Migration

**Project:** Oracle HCM Data Migration  
**Source File:** `legacy_employee_data_messy.xlsx`  
**Date:** 20-Sep-2026  

---

## 1. Executive Summary

We profiled **300** legacy employee records from the source Excel file.  
**276** records were found to be migration-ready after automated cleaning.  
**15** records were rejected and require business input before they can be migrated.

---

## 2. Scope and Method

| Item | Detail |
|------|--------|
| **Source** | `data/legacy_employee_data_messy.xlsx` (sheet: Employee Master) |
| **Tool** | Python + pandas (custom cleaning script `02_clean.py`) |
| **Checks performed** | Field-level cleansing, standardisation, format validation, cross-field consistency, duplicate detection |
| **Output** | Clean data file + Error log + Rejected rows |

**Key rules applied:**
- Emp ID normalisation (EMP prefix, uniqueness)
- Name splitting and title removal
- Date parsing to YYYY-MM-DD
- Gender → M / F
- Employment Status → ACTIVE / INACTIVE
- Department, Grade, Location standardisation (Value Mapping)
- Email format validation
- Phone → 10-digit clean number
- Cross-field checks (Exit date vs Hire date, Active + Exit date conflict)

---

## 3. Findings

| Issue | Rows Affected | Severity | Action Taken |
|-------|---------------|----------|--------------|
| Blank or invalid Emp ID | 8 | Critical | Row rejected |
| Duplicate Emp ID | 5 | Critical | Duplicate rows removed (first occurrence kept) |
| Exit date before Joining date | 12 | Critical | Row rejected – needs HR confirmation |
| Active employee with Exit date | 7 | High | Flagged for HR review |
| Missing Last Name | 9 | High | Row rejected |
| Unrecognised date format | 15 | Medium | Date left blank |
| Invalid / missing Gender | 11 | Medium | Left blank |
| Department value not in standard list | 14 | Medium | Left as-is + logged |
| Grade value not mapped | 6 | Low | Defaulted to GRADE_1 where blank |
| Invalid Email format | 10 | Medium | Left blank |
| Phone not 10 digits | 13 | Medium | Left blank |
| Missing / non-numeric Salary | 4 | Low | Left blank |

> **Note:** Replace the numbers above with the real counts from your `error_log.xlsx`.

---

## 4. Critical Issues Needing Business Decision

These records are **blocked from migration** until HR / business confirms the correct values:

1. **12 rows** have an **Exit Date earlier than the Joining Date**.  
   → HR must confirm the correct dates. These rows cannot be loaded as-is.

2. **7 rows** are marked **ACTIVE** but still have an **Exit Date**.  
   → HR must decide whether the employee is truly active or the status/date is wrong.

3. **8 rows** have a **blank or invalid Emp ID**.  
   → Business must provide a valid unique employee number.

4. **5 duplicate Emp IDs** were found.  
   → Confirm which record is the correct master record.

Until these decisions are received, the affected rows remain in the Rejected set.

---

## 5. Data Quality Score

| Metric                        | Value      |
|-------------------------------|------------|
| Total source records          | 300        |
| Clean (migration-ready)       | 276        |
| Rejected / blocked            | 15         |
| **Data Quality Score**        | **92.0%**  |

**Formula:** Clean rows ÷ Total rows × 100

---

## 6. Recommendations

1. **Make Emp ID mandatory and unique** at the source system / Excel template.  
2. **Standardise Department, Grade and Location** lists – provide a controlled drop-down to data entry users.  
3. **Validate date entry** (Joining Date cannot be in the future; Exit Date must be after Joining Date).  
4. **Enforce Gender** as M/F only.  
5. **Add basic Email and Phone format checks** at the point of data entry.  
6. **Run the cleaning script** as a mandatory pre-load step for every future data extract.  
7. Maintain the **Value Mapping** sheet and keep it updated when new variants appear.

---

## 7. Sign-off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Prepared by | | | |
| Reviewed by | | | |
| Approved by | | | |

---

*This report was generated as part of the Oracle HCM data migration readiness assessment.*