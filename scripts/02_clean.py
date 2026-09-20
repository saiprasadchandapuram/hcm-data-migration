import re
import os
import pandas as pd
from datetime import datetime

SRC = "data/legacy_employee_data_messy.xlsx"
df = pd.read_excel(SRC, sheet_name="Employee Master", dtype=str).fillna("")
df["_row"] = df.index + 2          # Excel row number for error log
errors = []

def log(row, col, value, issue, action):
    errors.append({
        "Excel Row": row,
        "Column": col,
        "Bad Value": value,
        "Issue": issue,
        "Action Taken": action
    })

# ---------- 1. Trim every cell ----------
for c in df.columns:
    if c != "_row":
        df[c] = df[c].astype(str).str.strip()

# ---------- 2. Emp ID ----------
def fix_id(r):
    v = r["Emp ID"].upper().replace(" ", "")
    if v == "":
        log(r["_row"], "Emp ID", r["Emp ID"], "Blank employee ID", "Row rejected")
        return ""
    if not v.startswith("EMP"):
        log(r["_row"], "Emp ID", r["Emp ID"], "Missing EMP prefix", f"Changed to EMP{v}")
        v = "EMP" + v
    return v

df["PersonNumber"] = df.apply(fix_id, axis=1)

# ---------- 3. Name split ----------
def split_name(r):
    n = re.sub(r"\s+", " ", r["Employee Name"]).strip()
    n = re.sub(r"^(Mr\.|Mrs\.|Ms\.|Dr\.)\s*", "", n, flags=re.I)
    if "," in n:                                    # "Kumar, Ravi"
        last, first = [p.strip() for p in n.split(",", 1)]
        log(r["_row"], "Employee Name", r["Employee Name"], "Last-name-first format", "Reordered")
    else:
        parts = n.split(" ")
        first = parts[0]
        last = " ".join(parts[1:]) if len(parts) > 1 else ""
    if not last:
        log(r["_row"], "Employee Name", r["Employee Name"], "Missing last name", "Row rejected")
    return pd.Series([first.title(), last.title()])

df[["FirstName", "LastName"]] = df.apply(split_name, axis=1)

# ---------- 4. Dates ----------
FORMATS = ["%d-%m-%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%b-%y", "%d/%m/%y", "%B %d, %Y"]

def parse_date(val, row, col):
    v = val.strip()
    if v == "" or v.upper() in ("N/A", "NA", "-"):
        return ""
    for f in FORMATS:
        try:
            return datetime.strptime(v, f).strftime("%Y/%m/%d")   # ← fixed format
        except ValueError:
            continue
    log(row, col, val, "Unrecognised date format", "Left blank")
    return ""

df["HireDate"] = df.apply(lambda r: parse_date(r["Joining Date"], r["_row"], "Joining Date"), axis=1)
df["DateOfBirth"] = df.apply(lambda r: parse_date(r["DOB"], r["_row"], "DOB"), axis=1)
df["TerminationDate"] = df.apply(lambda r: parse_date(r["Exit Date"], r["_row"], "Exit Date"), axis=1)

# ---------- 5. Salary ----------
def fix_salary(r):
    v = r["Salary"].strip()
    if v == "" or v.upper() == "TBD":
        log(r["_row"], "Salary", r["Salary"], "Missing or non-numeric salary", "Left blank")
        return ""
    try:
        if "LPA" in v.upper():
            num = float(re.sub(r"[^\d.]", "", v)) * 100000
        else:
            num = float(re.sub(r"[^\d.-]", "", v))
        if num <= 0:
            log(r["_row"], "Salary", r["Salary"], "Salary is zero or negative", "Left blank")
            return ""
        return int(num)
    except:
        log(r["_row"], "Salary", r["Salary"], "Could not parse salary", "Left blank")
        return ""

df["Amount"] = df.apply(fix_salary, axis=1)

# ---------- 6. Gender ----------
def fix_gender(r):
    v = r["Gender"].strip().upper()
    if v in ("M", "MALE"):
        return "M"
    if v in ("F", "FEMALE"):
        return "F"
    if v == "":
        log(r["_row"], "Gender", r["Gender"], "Blank gender", "Left blank")
        return ""
    log(r["_row"], "Gender", r["Gender"], "Invalid gender value", "Left blank")
    return ""

df["Sex"] = df.apply(fix_gender, axis=1)

# ---------- 7. Employment Status ----------
def fix_status(r):
    v = r["Employment Status"].strip().upper()
    if v in ("ACTIVE", "A"):
        return "ACTIVE"
    if v in ("LEFT", "RESIGNED", "TERMINATED", "INACTIVE"):
        return "INACTIVE"
    if v == "":
        log(r["_row"], "Employment Status", r["Employment Status"], "Blank status", "Defaulted to ACTIVE")
        return "ACTIVE"
    log(r["_row"], "Employment Status", r["Employment Status"], "Unknown status", "Left as-is")
    return v

df["AssignmentStatus"] = df.apply(fix_status, axis=1)

# ---------- 8. Department (Value Mapping) ----------
DEPT_MAP = {
    "production": "Production",
    "prod": "Production",
    "prodution": "Production",          # common typo
    "qc": "Quality",
    "quality control": "Quality",
    "quality": "Quality",
}

def fix_department(r):
    v = r["Department"].strip()
    key = v.lower()
    if key in DEPT_MAP:
        return DEPT_MAP[key]
    if v == "":
        log(r["_row"], "Department", r["Department"], "Blank department", "Left blank")
        return ""
    log(r["_row"], "Department", r["Department"], "No mapping found", "Left as-is")
    return v.title()

df["DepartmentName"] = df.apply(fix_department, axis=1)

# ---------- 9. Grade (Value Mapping) ----------
GRADE_MAP = {
    "g1": "GRADE_1",
    "grade 1": "GRADE_1",
    "grade-1": "GRADE_1",
    "1": "GRADE_1",
}

def fix_grade(r):
    v = r["Grade"].strip()
    key = v.lower()
    if key in GRADE_MAP:
        return GRADE_MAP[key]
    if v == "":
        log(r["_row"], "Grade", r["Grade"], "Blank grade", "Defaulted to GRADE_1")
        return "GRADE_1"
    log(r["_row"], "Grade", r["Grade"], "No mapping found", "Left as-is")
    return v.upper()

df["GradeCode"] = df.apply(fix_grade, axis=1)

# ---------- 10. Work Place / Location (Value Mapping) ----------
LOC_MAP = {
    "hyd": "HYD_PLANT",
    "hyderabad": "HYD_PLANT",
    "hyderabad plant": "HYD_PLANT",
}

def fix_location(r):
    v = r["Work Place"].strip()
    key = v.lower()
    if key in LOC_MAP:
        return LOC_MAP[key]
    if v == "":
        log(r["_row"], "Work Place", r["Work Place"], "Blank location", "Left blank")
        return ""
    log(r["_row"], "Work Place", r["Work Place"], "No mapping found", "Left as-is")
    return v.upper()

df["LocationCode"] = df.apply(fix_location, axis=1)

# ---------- 11. Designation (basic clean) ----------
def fix_designation(r):
    v = r["Designation"].strip()
    if v == "":
        log(r["_row"], "Designation", r["Designation"], "Blank designation", "Left blank")
        return ""
    return v.title()

df["JobName"] = df.apply(fix_designation, axis=1)

# ---------- 12. Email ----------
def fix_email(r):
    v = r["Email ID"].strip().lower().replace(" ", "")
    if v == "":
        log(r["_row"], "Email ID", r["Email ID"], "Blank email", "Left blank")
        return ""
    if not re.match(r"^[\w.+-]+@[\w-]+\.[\w.]+$", v):
        log(r["_row"], "Email ID", r["Email ID"], "Invalid email format", "Left blank")
        return ""
    return v

df["EmailAddress"] = df.apply(fix_email, axis=1)

# ---------- 13. Phone ----------
def fix_phone(r):
    v = re.sub(r"\D", "", r["Phone"])          # keep only digits
    if v.startswith("91") and len(v) > 10:
        v = v[2:]
    if v.startswith("0") and len(v) > 10:
        v = v[1:]
    if len(v) != 10:
        log(r["_row"], "Phone", r["Phone"], "Not exactly 10 digits", "Left blank")
        return ""
    return v

df["PhoneNumber"] = df.apply(fix_phone, axis=1)

# ---------- 14. Cross-field checks ----------

# Termination date before hire date
mask = (df["TerminationDate"] != "") & (df["HireDate"] != "") & (df["TerminationDate"] < df["HireDate"])
for _, r in df[mask].iterrows():
    log(r["_row"], "Exit Date", r["Exit Date"], "Exit date is before joining date", "Row rejected")

# Active employee with an exit date
mask = (df["AssignmentStatus"] == "ACTIVE") & (df["TerminationDate"] != "")
for _, r in df[mask].iterrows():
    log(r["_row"], "Exit Date", r["Exit Date"], "Active employee has an exit date", "Flagged for HR review")

# Duplicates (only check rows that actually have an Emp ID)
has_id = df["PersonNumber"] != ""
dupes = df[has_id & df.duplicated(subset=["PersonNumber"], keep="first")]
for _, r in dupes.iterrows():
    log(r["_row"], "Emp ID", r["PersonNumber"], "Duplicate employee ID", "Row removed")
df = df.drop(dupes.index)

# ---------- Re-map Department, Designation, Grade, Location using the Value Mapping sheet ----------
vm = pd.read_excel("docs/02_field_mapping.xlsx", sheet_name="Value Mapping", dtype=str)
lookup = {}
for _, m in vm.iterrows():
    for variant in re.findall(r"'([^']*)'", m.iloc[2]):
        lookup[(m.iloc[0], variant.strip().lower())] = m.iloc[1]

errors[:] = [x for x in errors if x["Issue"] != "No mapping found"]

def remap(src_col, out_col, blank_default=""):
    def f(r):
        v = r[src_col].strip()
        if v == "":
            return blank_default
        new = lookup.get((src_col, v.lower()))
        if new is None:
            log(r["_row"], src_col, r[src_col], "No mapping found", "Left blank")
            return ""
        return new
    df[out_col] = df.apply(f, axis=1)

remap("Department", "DepartmentName")
remap("Designation", "JobName")
remap("Grade", "GradeCode", blank_default="GRADE_1")
remap("Work Place", "LocationCode")

# ---------- 15. Split into Clean vs Rejected and write files ----------
os.makedirs("output", exist_ok=True)

# A row is "clean" only if it has valid PersonNumber + HireDate + LastName
clean = df[(df["PersonNumber"] != "") & (df["HireDate"] != "") & (df["LastName"] != "") & ~((df["TerminationDate"] != "") & (df["TerminationDate"] < df["HireDate"]))]
rejected = df[~df.index.isin(clean.index)]

cols = [
    "PersonNumber", "FirstName", "LastName", "Sex", "DateOfBirth", "HireDate",
    "DepartmentName", "JobName", "GradeCode", "LocationCode", "Amount",
    "AssignmentStatus", "TerminationDate", "EmailAddress", "PhoneNumber"
]

# Keep only columns that actually exist
cols = [c for c in cols if c in clean.columns]

with pd.ExcelWriter("output/employee_data_clean.xlsx") as xl:
    clean[cols].to_excel(xl, sheet_name="Clean Data", index=False)

with pd.ExcelWriter("output/error_log.xlsx") as xl:
    pd.DataFrame(errors).to_excel(xl, sheet_name="Error Log", index=False)
    rejected[["_row", "Emp ID", "Employee Name"]].to_excel(xl, sheet_name="Rejected Rows", index=False)

print(f"Clean: {len(clean)} | Rejected: {len(rejected)} | Issues logged: {len(errors)}")