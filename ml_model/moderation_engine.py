import pandas as pd
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

STATISTICAL_FILE = (
    "data/processed/statistical_analysis.csv"
)

ISOLATION_FILE = (
    "data/processed/isolation_forest_results.csv"
)

OUTPUT_FILE = (
    "data/processed/final_moderation_results.csv"
)


# ============================================================
# LOAD RESULTS
# ============================================================

stat_df = pd.read_csv(STATISTICAL_FILE)

iso_df = pd.read_csv(ISOLATION_FILE)


print("=" * 60)
print("AI MODERATION RECOMMENDATION ENGINE")
print("=" * 60)


# ============================================================
# SELECT REQUIRED ISOLATION FOREST COLUMNS
# ============================================================

iso_columns = [
    "Student_ID",
    "Subject",
    "Isolation_Forest_Anomaly",
    "Isolation_Forest_Score",
]


iso_results = iso_df[iso_columns]


# ============================================================
# MERGE STATISTICAL + ML RESULTS
# ============================================================

df = stat_df.merge(
    iso_results,
    on=[
        "Student_ID",
        "Subject",
    ],
    how="left",
)


print(
    f"\nCombined records: {len(df)}"
)


# ============================================================
# SIGNAL 1 — Z-SCORE
# ============================================================

df["Z_Score_Flag"] = (
    df["Z_Score"].abs() >= 2.5
)


# ============================================================
# SIGNAL 2 — IQR
# ============================================================

df["IQR_Flag"] = (
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
    df["Anomaly_Score"]
    .apply(generate_recommendation)
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
    df["Deviation"]
    .apply(determine_direction)
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


df["Suggested_Lower"] = (
    df["Suggested_Lower"].round(1)
)

df["Suggested_Upper"] = (
    df["Suggested_Upper"].round(1)
)


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

print("\nRecommendation summary:")

print(
    df["Recommendation"]
    .value_counts()
)


print("\nDeviation direction:")

print(
    df["Deviation_Direction"]
    .value_counts()
)


print("\nHuman review cases:")

print(
    df["Requires_Human_Review"]
    .value_counts()
)


# ============================================================
# GROUND TRUTH ANALYSIS
# ============================================================

if "Injected_Anomaly" in df.columns:

    injected = df["Injected_Anomaly"]

    recommended = (
        df["Requires_Human_Review"]
    )

    true_positives = (
        injected & recommended
    ).sum()

    false_positives = (
        ~injected & recommended
    ).sum()

    false_negatives = (
        injected & ~recommended
    ).sum()

    true_negatives = (
        ~injected & ~recommended
    ).sum()

    print("\nGround-truth comparison:")

    print(
        f"True positives  : {true_positives}"
    )

    print(
        f"False positives : {false_positives}"
    )

    print(
        f"False negatives : {false_negatives}"
    )

    print(
        f"True negatives  : {true_negatives}"
    )


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


review_cases = df[
    df["Requires_Human_Review"]
].sort_values(
    "Anomaly_Score",
    ascending=False,
)


print(
    review_cases[
        display_columns
    ].head(20).to_string(index=False)
)


print("\n" + "=" * 60)
print("MODERATION ENGINE COMPLETE")
print("=" * 60)