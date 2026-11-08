
from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"

STAT_FILE = PROCESSED_DIR / "oulad_statistical_results.csv"

IF_FILE = PROCESSED_DIR / "oulad_isolation_forest_results.csv"

OUTPUT_FILE = PROCESSED_DIR / "oulad_final_moderation_results.csv"


def convert_to_bool(series):
    """Safely convert CSV Boolean values."""
    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "1", "yes"])
    )


def generate_moderation_results():

    print("Loading statistical and Isolation Forest results...")

    statistical = pd.read_csv(STAT_FILE, low_memory=False)

    isolation = pd.read_csv(IF_FILE, low_memory=False)

    # Keep only the required Isolation Forest columns
    isolation = isolation[
        [
            "id_student",
            "id_assessment",
            "Isolation_Forest_Anomaly",
            "Isolation_Forest_Score",
        ]
    ]

    # Merge using student and assessment identifiers
    df = statistical.merge(
        isolation,
        on=["id_student", "id_assessment"],
        how="inner",
        validate="one_to_one",
    )

    # Safely parse detection flags
    df["Statistical_Anomaly"] = convert_to_bool(
        df["Statistical_Anomaly"]
    )

    df["Isolation_Forest_Anomaly"] = convert_to_bool(
        df["Isolation_Forest_Anomaly"]
    )

    # Count independent detection methods
    df["Anomaly_Score"] = (
        df["Statistical_Anomaly"].astype(int)
        + df["Isolation_Forest_Anomaly"].astype(int)
    )

    # Human review recommendation
    df["Requires_Human_Review"] = (
        df["Anomaly_Score"] >= 1
    )

    df["Recommendation"] = np.select(
        [
            df["Anomaly_Score"] == 2,
            df["Anomaly_Score"] == 1,
        ],
        [
            "Strong Review Recommended",
            "Review Recommended",
        ],
        default="No Significant Anomaly",
    )

    # Review priority
    df["Review_Priority"] = np.select(
        [
            df["Anomaly_Score"] == 2,
            df["Anomaly_Score"] == 1,
        ],
        [
            "High",
            "Medium",
        ],
        default="Not Required",
    )

    # Identify which method detected the record
    df["Detection_Source"] = np.select(
        [
            df["Statistical_Anomaly"] &
            df["Isolation_Forest_Anomaly"],

            df["Statistical_Anomaly"],

            df["Isolation_Forest_Anomaly"],
        ],
        [
            "Both Methods",
            "Statistical Detection",
            "Isolation Forest",
        ],
        default="No Detection",
    )

    # Describe the score direction
    df["Review_Reason"] = np.select(
        [
            df["Requires_Human_Review"] &
            (df["Score_Deviation"] < 0),

            df["Requires_Human_Review"] &
            (df["Score_Deviation"] > 0),

            df["Requires_Human_Review"] &
            (df["Score_Deviation"] == 0),
        ],
        [
            "Score below assessment median",
            "Score above assessment median",
            "Score at assessment median; other features triggered detection",
        ],
        default="No significant anomaly detected",
    )

    # Save final results
    df.to_csv(OUTPUT_FILE, index=False)

    # Summary
    total = len(df)

    review_count = int(df["Requires_Human_Review"].sum())

    print("\nOULAD MODERATION ENGINE SUMMARY")
    print("-" * 50)

    print("Total assessment records:", total)

    print("Records requiring human review:", review_count)

    print("Records without review recommendation:", total - review_count)

    print("\nRecommendation distribution:")
    print(df["Recommendation"].value_counts())

    print("\nReview priority:")
    print(df["Review_Priority"].value_counts())

    print("\nDetection source:")
    print(df["Detection_Source"].value_counts())

    print("\nReview direction:")
    print(
        df.loc[
            df["Requires_Human_Review"],
            "Review_Reason"
        ].value_counts()
    )

    print("\nOutput saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    generate_moderation_results()
