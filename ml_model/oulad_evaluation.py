
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = PROCESSED_DIR / "oulad_final_moderation_results.csv"
OUTPUT_FILE = PROCESSED_DIR / "oulad_evaluation_report.txt"
CSV_OUTPUT = PROCESSED_DIR / "oulad_evaluation_summary.csv"


def evaluate_model():

    df = pd.read_csv(INPUT_FILE, low_memory=False)

    lines = []

    def add(text=""):
        print(text)
        lines.append(str(text))

    add("=" * 65)
    add("OULAD AI MODERATION SYSTEM - EVALUATION REPORT")
    add("=" * 65)

    total = len(df)
    reviews = int(df["Requires_Human_Review"].sum())
    normal = total - reviews

    add("\n1. DATASET OVERVIEW")
    add("-" * 45)
    add(f"Total assessment records: {total}")
    add(f"Records recommended for review: {reviews}")
    add(f"Records without review recommendation: {normal}")
    add(f"Overall review rate: {reviews / total * 100:.2f}%")

    add("\n2. DETECTION METHOD SUMMARY")
    add("-" * 45)

    for column in [
        "Statistical_Anomaly",
        "Isolation_Forest_Anomaly",
        "Requires_Human_Review",
    ]:
        count = int(df[column].sum())
        add(f"{column}: {count} ({count / total * 100:.2f}%)")

    add("\n3. DETECTOR AGREEMENT")
    add("-" * 45)

    agreement = pd.crosstab(
        df["Statistical_Anomaly"],
        df["Isolation_Forest_Anomaly"],
        margins=True,
    )

    add(agreement.to_string())

    both = int(
        (
            df["Statistical_Anomaly"]
            & df["Isolation_Forest_Anomaly"]
        ).sum()
    )

    add(f"\nBoth methods agree on: {both} records")

    add("\n4. REVIEW RATE BY ASSESSMENT TYPE")
    add("-" * 45)

    assessment_summary = df.groupby("assessment_type").agg(
        Total=("id_student", "count"),
        Reviews=("Requires_Human_Review", "sum"),
        Strong_Reviews=(
            "Review_Priority",
            lambda x: (x == "High").sum(),
        ),
    )

    assessment_summary["Review_Rate_Percent"] = (
        assessment_summary["Reviews"]
        / assessment_summary["Total"] * 100
    ).round(2)

    add(assessment_summary.to_string())

    add("\n5. REVIEW RATE BY MODULE")
    add("-" * 45)

    module_summary = df.groupby("code_module").agg(
        Total=("id_student", "count"),
        Reviews=("Requires_Human_Review", "sum"),
    )

    module_summary["Review_Rate_Percent"] = (
        module_summary["Reviews"]
        / module_summary["Total"] * 100
    ).round(2)

    add(module_summary.to_string())

    add("\n6. SCORE DEVIATION ANALYSIS")
    add("-" * 45)

    deviation_summary = df.groupby(
        "Requires_Human_Review"
    )["Score_Deviation"].agg(
        ["count", "mean", "median", "std", "min", "max"]
    ).round(2)

    add(deviation_summary.to_string())

    add("\n7. RECOMMENDATION DISTRIBUTION")
    add("-" * 45)

    add(df["Recommendation"].value_counts().to_string())

    add("\n8. REVIEW DIRECTION")
    add("-" * 45)

    add(
        df.loc[
            df["Requires_Human_Review"],
            "Review_Reason",
        ].value_counts().to_string()
    )

    add("\n9. DATA QUALITY CHECKS")
    add("-" * 45)

    add(
        "Duplicate student-assessment pairs: "
        + str(
            df.duplicated(
                ["id_student", "id_assessment"]
            ).sum()
        )
    )

    add(
        "Missing student IDs: "
        + str(df["id_student"].isna().sum())
    )

    add(
        "Missing assessment IDs: "
        + str(df["id_assessment"].isna().sum())
    )

    add("\n10. EVALUATION LIMITATIONS")
    add("-" * 45)
    add(
        "OULAD does not contain verified unfair-marking anomaly labels."
    )
    add(
        "Therefore, accuracy, precision, recall, and F1-score "
        "are not reported as real-world performance metrics."
    )
    add(
        "Isolation Forest contamination is configured at 2% "
        "separately for each assessment type."
    )
    add(
        "Detected anomalies are recommendations for human review, "
        "not confirmed cases of unfair marking."
    )

    add("\n" + "=" * 65)
    add("END OF EVALUATION REPORT")
    add("=" * 65)

    OUTPUT_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    assessment_summary.to_csv(CSV_OUTPUT)

    print("\nReport saved to:", OUTPUT_FILE)
    print("Summary saved to:", CSV_OUTPUT)


if __name__ == "__main__":
    evaluate_model()
