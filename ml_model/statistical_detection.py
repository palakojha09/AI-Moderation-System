
from pathlib import Path
import pandas as pd
import numpy as np


BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = PROCESSED_DIR / "oulad_featured_assessments.csv"

OUTPUT_FILE = PROCESSED_DIR / "oulad_statistical_results.csv"


# Detection thresholds
ROBUST_Z_THRESHOLD = 3.5
LOW_PERCENTILE_THRESHOLD = 1.0
HIGH_PERCENTILE_THRESHOLD = 99.0


def detect_statistical_anomalies():

    print("Loading featured OULAD dataset...")

    df = pd.read_csv(INPUT_FILE, low_memory=False)

    # IQR boundaries for each assessment
    df["IQR_Lower_Bound"] = (
        df["Assessment_Q1"] - 1.5 * df["Assessment_IQR"]
    )

    df["IQR_Upper_Bound"] = (
        df["Assessment_Q3"] + 1.5 * df["Assessment_IQR"]
    )

    # IQR anomaly detection
    df["IQR_Flag"] = (
        (df["score"] < df["IQR_Lower_Bound"]) |
        (df["score"] > df["IQR_Upper_Bound"])
    )

    # Robust Z-score detection
    df["Robust_Z_Flag"] = (
        df["Robust_Z_Score"].abs() >= ROBUST_Z_THRESHOLD
    ).fillna(False)

    # Extreme percentile detection
    df["Percentile_Flag"] = (
        (df["Score_Percentile"] <= LOW_PERCENTILE_THRESHOLD) |
        (df["Score_Percentile"] >= HIGH_PERCENTILE_THRESHOLD)
    )

    # Count available detection signals
    df["Statistical_Anomaly_Score"] = (
        df["IQR_Flag"].astype(int) +
        df["Robust_Z_Flag"].astype(int) +
        df["Percentile_Flag"].astype(int)
    )

    # Statistical anomaly recommendation
    df["Statistical_Anomaly"] = (
        df["Statistical_Anomaly_Score"] >= 2
    )

    # Direction of unusual score
    df["Anomaly_Direction"] = np.select(
        [
            df["Statistical_Anomaly"] &
            (df["Score_Deviation"] < 0),

            df["Statistical_Anomaly"] &
            (df["Score_Deviation"] > 0)
        ],
        [
            "Unusually Low Score",
            "Unusually High Score"
        ],
        default="No Significant Anomaly"
    )

    # Save results
    df.to_csv(OUTPUT_FILE, index=False)

    print("\nSTATISTICAL DETECTION SUMMARY")
    print("-" * 45)

    print("Total records:", len(df))

    print("IQR anomalies:", df["IQR_Flag"].sum())

    print("Robust Z-score anomalies:", df["Robust_Z_Flag"].sum())

    print("Percentile anomalies:", df["Percentile_Flag"].sum())

    print(
        "Combined statistical anomalies:",
        df["Statistical_Anomaly"].sum()
    )

    print("\nAnomaly direction:")
    print(df["Anomaly_Direction"].value_counts())

    print("\nOutput saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    detect_statistical_anomalies()
