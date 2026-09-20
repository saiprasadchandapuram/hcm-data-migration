import pandas as pd

df = pd.read_excel("data/legacy_employee_data_messy.xlsx", sheet_name="Employee Master", dtype=str)

print("Rows:", len(df))
print("Columns:", list(df.columns))
print("\n--- Blank count per column ---")
print(df.isna().sum() + (df == "").sum())
print("\n--- Unique values in key columns ---")
for col in ["Department", "Designation", "Grade", "Work Place", "Employment Status", "Gender"]:
    print(f"\n{col}: {df[col].nunique()} unique values")
    print(df[col].value_counts().head(20))
print("\n--- Duplicate Emp IDs ---")
print(df[df.duplicated("Emp ID", keep=False)].sort_values("Emp ID").head(20))