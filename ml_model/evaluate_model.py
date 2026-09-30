import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

INPUT_FILE = "data/processed/final_moderation_results.csv"
OUTPUT_FILE = "data/processed/model_evaluation.csv"

df = pd.read_csv(INPUT_FILE)

# Ground truth
y_true = df["Injected_Anomaly"].astype(bool)# Final system prediction
y_pred = df["Requires_Human_Review"]

# Metrics
accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred, zero_division=0)
recall = recall_score(y_true, y_pred, zero_division=0)
f1 = f1_score(y_true, y_pred, zero_division=0)

tn, fp, fn, tp = confusion_matrix(
    y_true,
    y_pred
).ravel()

specificity = tn / (tn + fp) if (tn + fp) > 0 else 0

print("=" * 60)
print("FINAL MODERATION SYSTEM EVALUATION")
print("=" * 60)

print(f"Total records       : {len(df)}")
print(f"Actual anomalies    : {y_true.sum()}")
print(f"Predicted reviews   : {y_pred.sum()}")

print()
print("Performance Metrics")
print("-" * 30)
print(f"Accuracy            : {accuracy:.4f} ({accuracy * 100:.2f}%)")
print(f"Precision           : {precision:.4f} ({precision * 100:.2f}%)")
print(f"Recall              : {recall:.4f} ({recall * 100:.2f}%)")
print(f"F1-score            : {f1:.4f} ({f1 * 100:.2f}%)")
print(f"Specificity         : {specificity:.4f} ({specificity * 100:.2f}%)")

print()
print("Confusion Matrix")
print("-" * 30)
print(f"True Positives      : {tp}")
print(f"False Positives     : {fp}")
print(f"False Negatives     : {fn}")
print(f"True Negatives      : {tn}")

print()
print("Recommendation Distribution")
print("-" * 30)
print(df["Recommendation"].value_counts())

print()
print("Deviation Direction")
print("-" * 30)
print(df["Deviation_Direction"].value_counts())

# Save evaluation results
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
        "True Negatives"
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
        tn
    ]
})

evaluation.to_csv(OUTPUT_FILE, index=False)

print()
print(f"Evaluation saved to: {OUTPUT_FILE}")
print("=" * 60)