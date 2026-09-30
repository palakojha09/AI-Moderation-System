import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "data/processed/processed_marks.csv"
OUTPUT_FILE = "data/processed/isolation_forest_results.csv"

RANDOM_STATE = 42

# Approximate anomaly proportion in our synthetic benchmark.
# This is used ONLY for benchmarking the synthetic dataset.
CONTAMINATION = 0.05


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

print("=" * 60)
print("ISOLATION FOREST ANOMALY DETECTION")
print("=" * 60)

print(f"\nInput records: {len(df)}")


# ============================================================
# SELECT MODEL FEATURES
# ============================================================

features = [
    "Previous_Score",
    "Internal_Marks",
    "Attendance",
    "Given_Marks",
    "Expected_Marks",
    "Deviation",
    "Absolute_Deviation",
    "Deviation_Percentage",
    "Faculty_Mean",
    "Faculty_Std",
    "Subject_Mean",
    "Subject_Std",
]


X = df[features].copy()


print("\nFeatures used by Isolation Forest:")

for feature in features:
    print(f"  - {feature}")


# ============================================================
# CREATE MODEL
# ============================================================

model = IsolationForest(
    n_estimators=200,
    contamination=CONTAMINATION,
    random_state=RANDOM_STATE,
    n_jobs=-1,
)


# ============================================================
# TRAIN MODEL
# ============================================================

print("\nTraining Isolation Forest...")

model.fit(X)


# ============================================================
# PREDICT
# ============================================================

# Isolation Forest:
#   1  = normal
#  -1  = anomaly

df["Isolation_Forest_Prediction"] = model.predict(X)


# Convert prediction to easier boolean format

df["Isolation_Forest_Anomaly"] = (
    df["Isolation_Forest_Prediction"] == -1
)


# ============================================================
# ANOMALY SCORE
# ============================================================

# decision_function:
# higher value = more normal
# lower value  = more anomalous

df["Isolation_Forest_Score"] = (
    -model.decision_function(X)
)

df["Isolation_Forest_Score"] = (
    df["Isolation_Forest_Score"].round(4)
)


# ============================================================
# SAVE RESULTS
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
# DETECTION SUMMARY
# ============================================================

detected_count = (
    df["Isolation_Forest_Anomaly"].sum()
)

print("\nDetection summary:")
print(
    f"Isolation Forest anomalies: {detected_count}"
)


# ============================================================
# GROUND-TRUTH COMPARISON
# ============================================================

if "Injected_Anomaly" in df.columns:

    injected = df["Injected_Anomaly"]

    detected = df["Isolation_Forest_Anomaly"]

    true_positives = (
        injected & detected
    ).sum()

    false_positives = (
        ~injected & detected
    ).sum()

    false_negatives = (
        injected & ~detected
    ).sum()

    true_negatives = (
        ~injected & ~detected
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

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    precision = (
        true_positives
        / (true_positives + false_positives)
        if (true_positives + false_positives) > 0
        else 0
    )

    recall = (
        true_positives
        / (true_positives + false_negatives)
        if (true_positives + false_negatives) > 0
        else 0
    )

    if precision + recall > 0:
        f1_score = (
            2 * precision * recall
            / (precision + recall)
        )
    else:
        f1_score = 0

    print("\nEvaluation metrics:")

    print(
        f"Precision : {precision * 100:.2f}%"
    )

    print(
        f"Recall    : {recall * 100:.2f}%"
    )

    print(
        f"F1-score  : {f1_score * 100:.2f}%"
    )


# ============================================================
# SHOW MOST ANOMALOUS RECORDS
# ============================================================

print("\nTop 10 most anomalous records:")

display_columns = [
    "Student_ID",
    "Subject",
    "Faculty_ID",
    "Given_Marks",
    "Expected_Marks",
    "Deviation",
    "Deviation_Percentage",
    "Isolation_Forest_Score",
    "Isolation_Forest_Anomaly",
    "Injected_Anomaly",
    "Anomaly_Type",
]


top_anomalies = df.sort_values(
    "Isolation_Forest_Score",
    ascending=False,
).head(10)


print(
    top_anomalies[
        display_columns
    ].to_string(index=False)
)


print("\n" + "=" * 60)
print("ISOLATION FOREST COMPLETE")
print("=" * 60)