
from pathlib import Path
import pandas as pd
import numpy as np


BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = PROCESSED_DIR / "oulad_cleaned_assessments.csv"

OUTPUT_FILE = PROCESSED_DIR / "oulad_featured_assessments.csv"


def create_features():

    print("Loading cleaned OULAD dataset...")

    df = pd.read_csv(INPUT_FILE, low_memory=False)

    # Group students by assessment
    grouped = df.groupby("id_assessment")["score"]

    # Assessment-level statistics
    df["Assessment_Mean"] = grouped.transform("mean")
    df["Assessment_Median"] = grouped.transform("median")
    df["Assessment_Std"] = grouped.transform("std")

    df["Assessment_Q1"] = grouped.transform(
        lambda x: x.quantile(0.25)
    )

    df["Assessment_Q3"] = grouped.transform(
        lambda x: x.quantile(0.75)
    )

    df["Assessment_IQR"] = (
        df["Assessment_Q3"] - df["Assessment_Q1"]
    )

    # Score deviation from assessment median
    df["Score_Deviation"] = (
        df["score"] - df["Assessment_Median"]
    )

    df["Absolute_Deviation"] = (
        df["Score_Deviation"].abs()
    )

    # Robust Z-score using median absolute deviation
    assessment_mad = grouped.transform(
        lambda x: (x - x.median()).abs().median()
    )

    df["Assessment_MAD"] = assessment_mad

    # Avoid division by zero
    denominator = 1.4826 * df["Assessment_MAD"]

    df["Robust_Z_Score"] = np.where(
        denominator > 0,
        df["Score_Deviation"] / denominator,
        np.nan
    )

    # Percentile rank within each assessment
    df["Score_Percentile"] = grouped.rank(pct=True) * 100

    # Save features
    df.to_csv(OUTPUT_FILE, index=False)

    print("\nFEATURE ENGINEERING COMPLETE")
    print("-" * 45)

    print("Total records:", len(df))

    print("\nNew features created:")
    print([
        "Assessment_Mean",
        "Assessment_Median",
        "Assessment_Std",
        "Assessment_Q1",
        "Assessment_Q3",
        "Assessment_IQR",
        "Score_Deviation",
        "Absolute_Deviation",
        "Assessment_MAD",
        "Robust_Z_Score",
        "Score_Percentile"
    ])

    print("\nFeature preview:")
    print(
        df[
            [
                "id_assessment",
                "id_student",
                "score",
                "Assessment_Median",
                "Score_Deviation",
                "Robust_Z_Score",
                "Score_Percentile"
            ]
        ].head(10)
    )

    print("\nOutput saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    create_features()
