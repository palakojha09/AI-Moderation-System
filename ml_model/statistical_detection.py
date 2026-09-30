import pandas as pd
import numpy as np
from pathlib import Path


INPUT_FILE = "data/processed/processed_marks.csv"
OUTPUT_FILE = "data/processed/statistical_analysis.csv"


# ============================================================
# LOAD PROCESSED DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

print("=" * 60)
print("STATISTICAL ANOMALY DETECTION")
print("=" * 60)

print(f"\nInput records: {len(df)}")


# ============================================================
# Z-SCORE
# ============================================================

deviation_mean = df["Deviation"].mean()
deviation_std = df["Deviation"].std()

print(f"\nDeviation mean: {deviation_mean:.2f}")
print(f"Deviation std : {deviation_std:.2f}")


if deviation_std == 0:
    df["Z_Score"] = 0
else:
    df["Z_Score"] = (
        (df["Deviation"] - deviation_mean)
        / deviation_std
    )


df["Z_Score"] = df["Z_Score"].round(3)


# ============================================================
# Z-SCORE OUTLIER
# ============================================================

Z_THRESHOLD = 2.5

df["Z_Score_Outlier"] = (
    df["Z_Score"].abs() >= Z_THRESHOLD
)


# ============================================================
# IQR
# ============================================================

Q1 = df["Deviation"].quantile(0.25)
Q3 = df["Deviation"].quantile(0.75)

IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR


print("\nIQR statistics:")
print(f"Q1          : {Q1:.2f}")
print(f"Q3          : {Q3:.2f}")
print(f"IQR         : {IQR:.2f}")
print(f"Lower bound : {lower_bound:.2f}")
print(f"Upper bound : {upper_bound:.2f}")


# ============================================================
# IQR OUTLIER
# ============================================================

df["IQR_Outlier"] = (
    (df["Deviation"] < lower_bound)
    | (df["Deviation"] > upper_bound)
)


# ============================================================
# COMBINED STATISTICAL FLAG
# ============================================================

df["Statistical_Anomaly"] = (
    df["Z_Score_Outlier"]
    | df["IQR_Outlier"]
)


# ============================================================
# ANOMALY SCORE
# ============================================================

df["Statistical_Anomaly_Score"] = (
    df["Z_Score"].abs()
)


# ============================================================
# SAVE RESULT
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

print("\nDetection summary:")

print(
    f"Z-score outliers : "
    f"{df['Z_Score_Outlier'].sum()}"
)

print(
    f"IQR outliers     : "
    f"{df['IQR_Outlier'].sum()}"
)

print(
    f"Statistical anomalies : "
    f"{df['Statistical_Anomaly'].sum()}"
)


# ============================================================
# COMPARE WITH INJECTED GROUND TRUTH
# ============================================================

if "Injected_Anomaly" in df.columns:

    injected = df["Injected_Anomaly"]

    detected = df["Statistical_Anomaly"]

    true_positives = (
        injected & detected
    ).sum()

    false_positives = (
        ~injected & detected
    ).sum()

    false_negatives = (
        injected & ~detected
    ).sum()

    print("\nGround-truth comparison:")
    print(f"True positives  : {true_positives}")
    print(f"False positives : {false_positives}")
    print(f"False negatives : {false_negatives}")


# ============================================================
# SHOW MOST EXTREME RECORDS
# ============================================================

print("\nTop 10 largest absolute deviations:")

columns_to_show = [
    "Student_ID",
    "Subject",
    "Faculty_ID",
    "Given_Marks",
    "Expected_Marks",
    "Deviation",
    "Deviation_Percentage",
    "Z_Score",
    "IQR_Outlier",
    "Injected_Anomaly",
    "Anomaly_Type",
]

print(
    df.loc[
        df["Absolute_Deviation"]
        .nlargest(10)
        .index,
        columns_to_show,
    ].to_string(index=False)
)


print("\n" + "=" * 60)
print("STATISTICAL ANALYSIS COMPLETE")
print("=" * 60)