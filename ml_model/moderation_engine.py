
import pandas as pd
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

STATISTICAL_FILE = "data/processed/statistical_analysis.csv"
ISOLATION_FILE = "data/processed/isolation_forest_results.csv"
OUTPUT_FILE = "data/processed/final_moderation_results.csv"


# ============================================================
# HELPER FUNCTION
# ============================================================

def convert_to_bool(series):
    """Safely convert CSV Boolean values to actual Booleans."""

    if series.dtype == bool:
        return series

    converted = (
        series.astype(str)
        .str.strip()
        .str.lower()
        .map({
            "true": True,
            "false": False,
            "1": True,
            "0": False,
        })
    )

    if converted.isnull().any():
        raise ValueError(
            f"Invalid Boolean values found in {series.name}"
        )

    return converted.astype(bool)


# ============================================================
# LOAD RESULTS
# ============================================================

stat_df = pd.read_csv(STATISTICAL_FILE)
iso_df = pd.read_csv(ISOLATION_FILE)

print("=" * 60)
print("AI MODERATION RECOMMENDATION ENGINE")
print("=" * 60)

print(f"\nStatistical records: {len(stat_df)}")
print(f"Isolation Forest records: {len(iso_df)}")


# ============================================================
# VALIDATE MERGE KEYS
# ============================================================

merge_keys = ["Student_ID", "Subject"]

for key in merge_keys:
    if key not in stat_df.columns or key not in iso_df.columns:
        raise ValueError(f"Missing merge key: {key}")

if stat_df.duplicated(merge_keys).any():
    raise ValueError(
        "Duplicate Student_ID and Subject combinations "
        "in statistical results."
    )

if iso_df.duplicated(merge_keys).any():
    raise ValueError(
        "Duplicate Student_ID and Subject combinations "
        "in Isolation Forest results."
    )


# ============================================================
# SELECT REQUIRED ISOLATION FOREST COLUMNS
# ============================================================

iso_columns = [
    "Student_ID",
    "Subject",
    "Isolation_Forest_Anomaly",
    "Isolation_Forest_Score",
]

missing_columns = [
    column for column in iso_columns
    if column not in iso_df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing Isolation Forest columns: {missing_columns}"
    )

iso_results = iso_df[iso_columns].copy()

iso_results["Isolation_Forest_Anomaly"] = convert_to_bool(
    iso_results["Isolation_Forest_Anomaly"]
)


# ============================================================
# MERGE STATISTICAL + ML RESULTS
# ============================================================

df = stat_df.merge(
    iso_results,
    on=merge_keys,
    how="left",
    validate="one_to_one",
    indicator=True,
)

if (df["_merge"] != "both").any():
    raise ValueError(
        "Some statistical records have no matching "
        "Isolation Forest results."
    )

df.drop(columns=["_merge"], inplace=True)

print(f"\nCombined records: {len(df)}")


# ============================================================
# SIGNAL 1 — Z-SCORE
# ============================================================

df["Z_Score_Flag"] = (
    df["Z_Score"].abs() >= 2.5
)


# ============================================================
# SIGNAL 2 — IQR
# ============================================================

df["IQR_Flag"] = convert_to_bool(
    df["IQR_Outlier"]
)


# ============================================================
# SIGNAL 3 — ISOLATION FOREST
# ============================================================

df["Isolation_Forest_Flag"] = (
    df["Isolation_Forest_Anomaly"]
)


# ============================================================
# SIGNAL 4 — LARGE EXPECTED-MARK DEVIATION
# ============================================================

df["Large_Deviation_Flag"] = (
    df["Deviation_Percentage"].abs() >= 25
)


# ============================================================
# CALCULATE COMBINED ANOMALY SCORE
# ============================================================

df["Anomaly_Score"] = (
    df["Z_Score_Flag"].astype(int)
    + df["IQR_Flag"].astype(int)
    + df["Isolation_Forest_Flag"].astype(int)
    + df["Large_Deviation_Flag"].astype(int)
)


# ============================================================
# RECOMMENDATION
# ============================================================

def generate_recommendation(score):

    if score >= 3:
        return "Strong Review Recommended"

    if score == 2:
        return "Review Recommended"

    return "No Significant Anomaly"


df["Recommendation"] = (
    df["Anomaly_Score"].apply(generate_recommendation)
)


# ============================================================
# DEVIATION DIRECTION
# ============================================================

def determine_direction(deviation):

    if deviation <= -10:
        return "Potential Under-marking"

    if deviation >= 10:
        return "Potential Over-marking"

    return "No Significant Direction"


df["Deviation_Direction"] = (
    df["Deviation"].apply(determine_direction)
)


# ============================================================
# SUGGESTED MODERATION RANGE
# ============================================================

df["Suggested_Lower"] = (
    df["Expected_Marks"] - 5
).clip(lower=0)

df["Suggested_Upper"] = (
    df["Expected_Marks"] + 5
).clip(upper=100)

df["Suggested_Lower"] = df["Suggested_Lower"].round(1)
df["Suggested_Upper"] = df["Suggested_Upper"].round(1)


# ============================================================
# HUMAN REVIEW FLAG
# ============================================================

df["Requires_Human_Review"] = (
    df["Anomaly_Score"] >= 2
)


# ============================================================
# SAVE FINAL RESULTS
# ============================================================

output_path = Path(OUTPUT_FILE)
output_path.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(output_path, index=False)


# ============================================================
# SUMMARY
# ============================================================

print("\nRecommendation summary:")
print(df["Recommendation"].value_counts())

print("\nDeviation direction:")
print(df["Deviation_Direction"].value_counts())

print("\nHuman review cases:")
print(df["Requires_Human_Review"].value_counts())


# ============================================================
# GROUND-TRUTH ANALYSIS
# ============================================================

if "Injected_Anomaly" in df.columns:

    injected = convert_to_bool(df["Injected_Anomaly"])
    recommended = df["Requires_Human_Review"]

    true_positives = int((injected & recommended).sum())
    false_positives = int((~injected & recommended).sum())
    false_negatives = int((injected & ~recommended).sum())
    true_negatives = int((~injected & ~recommended).sum())

    print("\nGround-truth comparison:")
    print(f"True positives  : {true_positives}")
    print(f"False positives : {false_positives}")
    print(f"False negatives : {false_negatives}")
    print(f"True negatives  : {true_negatives}")


# ============================================================
# SHOW REVIEW CASES
# ============================================================

print("\nTop moderation cases:")

display_columns = [
    "Student_ID",
    "Subject",
    "Faculty_ID",
    "Given_Marks",
    "Expected_Marks",
    "Deviation",
    "Deviation_Percentage",
    "Z_Score",
    "IQR_Outlier",
    "Isolation_Forest_Anomaly",
    "Anomaly_Score",
    "Deviation_Direction",
    "Recommendation",
    "Requires_Human_Review",
]

display_columns = [
    column for column in display_columns
    if column in df.columns
]

review_cases = df[
    df["Requires_Human_Review"]
].sort_values(
    "Anomaly_Score",
    ascending=False,
)

print(
    review_cases[display_columns]
    .head(20)
    .to_string(index=False)
)


print("\n" + "=" * 60)
print("MODERATION ENGINE COMPLETE")
print("=" * 60)
