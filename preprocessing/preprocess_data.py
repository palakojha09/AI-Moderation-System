import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "data/raw/synthetic_marks.csv"
OUTPUT_FILE = "data/processed/processed_marks.csv"


# ============================================================
# LOAD RAW DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

print("=" * 60)
print("DATA PREPROCESSING")
print("=" * 60)

print(f"\nInput records: {len(df)}")


# ============================================================
# NORMALIZE INTERNAL MARKS
# ============================================================

df["Internal_Percentage"] = (
    df["Internal_Marks"] / 30
) * 100


# ============================================================
# CALCULATE EXPECTED MARKS
# ============================================================

df["Expected_Marks"] = (
    0.50 * df["Previous_Score"]
    + 0.30 * df["Internal_Percentage"]
    + 0.20 * df["Attendance"]
)


# Keep expected marks within valid range

df["Expected_Marks"] = df["Expected_Marks"].clip(
    0,
    df["Max_Marks"]
)


# ============================================================
# CALCULATE MARK DEVIATION
# ============================================================

df["Deviation"] = (
    df["Given_Marks"]
    - df["Expected_Marks"]
)


# ============================================================
# ABSOLUTE DEVIATION
# ============================================================

df["Absolute_Deviation"] = (
    df["Deviation"].abs()
)


# ============================================================
# DEVIATION PERCENTAGE
# ============================================================

df["Deviation_Percentage"] = np.where(
    df["Expected_Marks"] != 0,
    (
        df["Deviation"]
        / df["Expected_Marks"]
    ) * 100,
    0,
)


# ============================================================
# ROUND NUMERIC FEATURES
# ============================================================

numeric_columns = [
    "Internal_Percentage",
    "Expected_Marks",
    "Deviation",
    "Absolute_Deviation",
    "Deviation_Percentage",
]

df[numeric_columns] = df[numeric_columns].round(2)


# ============================================================
# FACULTY-LEVEL STATISTICS
# ============================================================

faculty_stats = (
    df.groupby("Faculty_ID")["Given_Marks"]
    .agg(
        Faculty_Mean="mean",
        Faculty_Std="std",
    )
    .reset_index()
)


# Merge faculty statistics back into dataset

df = df.merge(
    faculty_stats,
    on="Faculty_ID",
    how="left",
)


df["Faculty_Mean"] = df["Faculty_Mean"].round(2)
df["Faculty_Std"] = df["Faculty_Std"].round(2)


# ============================================================
# SUBJECT-LEVEL STATISTICS
# ============================================================

subject_stats = (
    df.groupby("Subject")["Given_Marks"]
    .agg(
        Subject_Mean="mean",
        Subject_Std="std",
    )
    .reset_index()
)


df = df.merge(
    subject_stats,
    on="Subject",
    how="left",
)


df["Subject_Mean"] = df["Subject_Mean"].round(2)
df["Subject_Std"] = df["Subject_Std"].round(2)


# ============================================================
# SORT DATA
# ============================================================

df = df.sort_values(
    ["Student_ID", "Subject"]
).reset_index(drop=True)


# ============================================================
# SAVE PROCESSED DATA
# ============================================================

output_path = Path(OUTPUT_FILE)

output_path.parent.mkdir(
    parents=True,
    exist_ok=True,
)

df.to_csv(
    output_path,
    index=False,
)


# ============================================================
# SUMMARY
# ============================================================

print("\nProcessed dataset created successfully!")

print(f"Output file: {OUTPUT_FILE}")
print(f"Records: {len(df)}")
print(f"Columns: {len(df.columns)}")

print("\nNew features created:")

new_features = [
    "Internal_Percentage",
    "Expected_Marks",
    "Deviation",
    "Absolute_Deviation",
    "Deviation_Percentage",
    "Faculty_Mean",
    "Faculty_Std",
    "Subject_Mean",
    "Subject_Std",
]

for feature in new_features:
    print(f"  - {feature}")


# ============================================================
# SAMPLE OUTPUT
# ============================================================

print("\nSample processed records:")

print(
    df[
        [
            "Student_ID",
            "Subject",
            "Faculty_ID",
            "Given_Marks",
            "Expected_Marks",
            "Deviation",
            "Deviation_Percentage",
        ]
    ].head(10)
)

print("\n" + "=" * 60)
print("PREPROCESSING COMPLETE")
print("=" * 60)