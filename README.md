# Employee Data Migration – Oracle Cloud HCM

## Business Problem

A company was moving **300 employee records** from Excel into Oracle Cloud HCM.  
The legacy data had no validation:
- Departments had multiple different spellings
- Dates came in six different formats
- Salaries were stored as text
- Some records had exit dates **before** the joining date

If this data had been loaded as-is, the go-live would have failed. Oracle rejects invalid dates and unknown values, which would have led to wrong headcount reports and potential payroll errors.

## My Approach

1. **Profiled** the legacy data to identify all data quality issues
2. Created a **source-to-target field mapping** document with transformation and validation rules
3. Built a **Python cleansing pipeline** that:
   - Standardised Emp ID, Name, Gender, Status, Department, Grade, Location
   - Converted dates to Oracle format (YYYY-MM-DD)
   - Cleaned Salary, Email and Phone
   - Applied cross-field validation (Exit Date vs Hire Date, Active status conflicts, duplicates)
4. Produced three outputs:
   - Clean load-ready file
   - Full error log with every issue and the action taken
   - Data Quality Report for business sign-off

## Tools Used

- Python + Pandas
- Excel
- Oracle HCM (target system concepts – HDL)
- Markdown for documentation

## Results

| Metric                        | Value      |
|------------------------------|------------|
| Total source records         | 300        |
| Migration-ready (Clean)      | 247        |
| Rejected / needs decision    | 53         |
| **Data Quality Score**       | **82.3%**  |

Every exception was documented and traceable instead of being silently loaded.

## Key Deliverables

- `scripts/02_clean.py` – Full data cleansing & validation pipeline
- `output/employee_data_clean.xlsx` – Load-ready data
- `output/error_log.xlsx` – Complete issue log + rejected rows
- `docs/03_data_quality_report.md` – Manager-ready quality report
- Field Mapping & Value Mapping documents

## Recommendations

- Make Emp ID mandatory and unique at source
- Standardise Department, Grade and Location lists
- Validate dates at the point of entry
- Run this cleansing script as a mandatory pre-load step for future extracts

## How to Run

```bash
cd hcm_data-migration
python scripts/02_clean.py