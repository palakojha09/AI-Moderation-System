import pandas as pd


# ============================================================
# LOAD DATASET
# ============================================================

file_path = "data/raw/synthetic_marks.csv"

df = pd.read_csv(file_path)


print("=" * 60)
print("DATASET VALIDATION REPORT")
print("=" * 60)


# ============================================================
# BASIC INFORMATION
# ============================================================

print("\n1. DATASET SHAPE")
print(f"Rows    : {len(df)}")
print(f"Columns : {len(df.columns)}")


# ============================================================
# EXPECTED STRUCTURE
# ============================================================

expected_columns = [
    "Student_ID",
    "Subject",
    "Faculty_ID",
    "Internal_Marks",
    "Previous_Score",
    "Attendance",
    "Given_Marks",
    "Max_Marks",
    "Injected_Anomaly",
    "Anomaly_Type",
]

missing_columns = [
    column
    for column in expected_columns
    if column not in df.columns
]

print("\n2. COLUMN CHECK")

if missing_columns:
    print("FAILED")
    print("Missing columns:", missing_columns)
else:
    print("PASSED - All expected columns are present")


# ============================================================
# MISSING VALUES
# ============================================================

print("\n3. MISSING VALUE CHECK")

missing_values = df.isnull().sum()

if missing_values.sum() == 0:
    print("PASSED - No missing values")
else:
    print("FAILED")
    print(missing_values[missing_values > 0])


# ============================================================
# DUPLICATE CHECK
# ============================================================

print("\n4. DUPLICATE CHECK")

duplicates = df.duplicated(
    subset=["Student_ID", "Subject"]
).sum()

if duplicates == 0:
    print("PASSED - No duplicate student-subject evaluations")
else:
    print(f"FAILED - {duplicates} duplicate evaluations found")


# ============================================================
# STUDENT CHECK
# ============================================================

print("\n5. STUDENT CHECK")

student_count = df["Student_ID"].nunique()

print(f"Unique students: {student_count}")

if student_count == 500:
    print("PASSED")
else:
    print("WARNING - Expected 500 students")


# ============================================================
# SUBJECT CHECK
# ============================================================

print("\n6. SUBJECT CHECK")

subjects = sorted(df["Subject"].unique())

print("Subjects:")
for subject in subjects:
    print(f"  - {subject}")

if len(subjects) == 4:
    print("PASSED - 4 subjects found")
else:
    print("WARNING")


# ============================================================
# FACULTY CHECK
# ============================================================

print("\n7. FACULTY CHECK")

faculty = sorted(df["Faculty_ID"].unique())

print("Faculty:")
for faculty_id in faculty:
    print(f"  - {faculty_id}")

if len(faculty) == 8:
    print("PASSED - 8 faculty members found")
else:
    print("WARNING")


# ============================================================
# MARK RANGE CHECK
# ============================================================

print("\n8. MARK RANGE CHECK")

invalid_marks = df[
    (df["Given_Marks"] < 0)
    | (df["Given_Marks"] > df["Max_Marks"])
]

if len(invalid_marks) == 0:
    print("PASSED - All marks are within valid range")
else:
    print(
        f"FAILED - {len(invalid_marks)} invalid mark records"
    )


# ============================================================
# INTERNAL MARK CHECK
# ============================================================

print("\n9. INTERNAL MARK CHECK")

invalid_internal = df[
    (df["Internal_Marks"] < 0)
    | (df["Internal_Marks"] > 30)
]

if len(invalid_internal) == 0:
    print("PASSED - Internal marks are valid")
else:
    print("FAILED")


# ============================================================
# ATTENDANCE CHECK
# ============================================================

print("\n10. ATTENDANCE CHECK")

invalid_attendance = df[
    (df["Attendance"] < 0)
    | (df["Attendance"] > 100)
]

if len(invalid_attendance) == 0:
    print("PASSED - Attendance values are valid")
else:
    print("FAILED")


# ============================================================
# ANOMALY CHECK
# ============================================================

print("\n11. INJECTED ANOMALY CHECK")

anomaly_count = df["Injected_Anomaly"].sum()

print(f"Injected anomalies: {anomaly_count}")
print(f"Normal records: {len(df) - anomaly_count}")

if anomaly_count > 0:
    print("PASSED - Controlled anomalies are present")
else:
    print("FAILED - No anomalies found")


# ============================================================
# ANOMALY TYPE DISTRIBUTION
# ============================================================

print("\n12. ANOMALY TYPE DISTRIBUTION")

print(
    df["Anomaly_Type"].value_counts()
)


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)