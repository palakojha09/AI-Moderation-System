
import pandas as pd
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "data/processed/final_moderation_results.csv"
OUTPUT_FILE = "data/processed/model_evaluation.csv"


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

print("=" * 60)
print("FINAL MODERATION SYSTEM EVALUATION")
print("=" * 60)

print(f"\nTotal records loaded: {len(df)}")


# ============================================================
# VALIDATE REQUIRED COLUMNS
# ============================================================

required_columns = [
    "Injected_Anomaly",
    "Requires_Human_Review",
    "Recommendation",
    "Deviation_Direction",
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


# ============================================================
# CONVERT BOOLEAN VALUES SAFELY
# ============================================================

def convert_to_bool(series):

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
            f"Invalid Boolean values in {series.name}"
        )

    return converted.astype(bool)


# ============================================================
# GROUND TRUTH AND PREDICTIONS
# ============================================================

y_true = convert_to_bool(df["Injected_Anomaly"])
y_pred = convert_to_bool(df["Requires_Human_Review"])


# ============================================================
# CALCULATE PERFORMANCE METRICS
# ============================================================

accuracy = accuracy_score(y_true, y_pred)

precision = precision_score(
    y_true, y_pred, zero_division=0
)

recall = recall_score(
    y_true, y_pred, zero_division=0
)

f1 = f1_score(
    y_true, y_pred, zero_division=0
)


# ============================================================
# CONFUSION MATRIX
# ============================================================

tn, fp, fn, tp = confusion_matrix(
    y_true,
    y_pred,
    labels=[False, True],
).ravel()

specificity = (
    tn / (tn + fp)
    if (tn + fp) > 0
    else 0
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 60)
print("PERFORMANCE METRICS")
print("=" * 60)

print(f"Total records       : {len(df)}")
print(f"Actual anomalies    : {y_true.sum()}")
print(f"Predicted reviews   : {y_pred.sum()}")

print("\nPerformance Metrics")
print("-" * 30)

print(f"Accuracy            : {accuracy:.4f} ({accuracy * 100:.2f}%)")
print(f"Precision           : {precision:.4f} ({precision * 100:.2f}%)")
print(f"Recall              : {recall:.4f} ({recall * 100:.2f}%)")
print(f"F1-score            : {f1:.4f} ({f1 * 100:.2f}%)")
print(f"Specificity         : {specificity:.4f} ({specificity * 100:.2f}%)")


# ============================================================
# CONFUSION MATRIX RESULTS
# ============================================================

print("\nConfusion Matrix")
print("-" * 30)

print(f"True Positives      : {tp}")
print(f"False Positives     : {fp}")
print(f"False Negatives     : {fn}")
print(f"True Negatives      : {tn}")


# ============================================================
# RECOMMENDATION DISTRIBUTION
# ============================================================

print("\nRecommendation Distribution")
print("-" * 30)

print(df["Recommendation"].value_counts())


# ============================================================
# DEVIATION DIRECTION
# ============================================================

print("\nDeviation Direction")
print("-" * 30)

print(df["Deviation_Direction"].value_counts())


# ============================================================
# SAVE EVALUATION RESULTS
# ============================================================

evaluation = pd.DataFrame({
    "Metric": [
        "Accuracy",
        "Precision",
        "Recall",
        "F1-Score",
        "Specificity",
        "True Positives",
        "False Positives",
        "False Negatives",
        "True Negatives",
    ],
    "Value": [
        accuracy,
        precision,
        recall,
        f1,
        specificity,
        tp,
        fp,
        fn,
        tn,
    ],
})

output_path = Path(OUTPUT_FILE)
output_path.parent.mkdir(parents=True, exist_ok=True)

evaluation.to_csv(output_path, index=False)

print("\nEvaluation saved to:")
print(OUTPUT_FILE)

print("\n" + "=" * 60)
print("EVALUATION COMPLETE")
print("=" * 60)
