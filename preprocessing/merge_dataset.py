
from pathlib import Path
import pandas as pd


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw" / "OULAD"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def merge_oulad_dataset():

    print("Loading OULAD datasets...")

    # Load the three required CSV files
    student_assessment = pd.read_csv(
        RAW_DIR / "studentAssessment.csv",
        na_values=["?"]
    )

    assessments = pd.read_csv(
        RAW_DIR / "assessments.csv"
    )

    student_info = pd.read_csv(
        RAW_DIR / "studentInfo.csv"
    )

    print("\nOriginal dataset sizes:")
    print("Student assessments:", student_assessment.shape)
    print("Assessments:", assessments.shape)
    print("Student information:", student_info.shape)

    # Convert score into numeric format
    student_assessment["score"] = pd.to_numeric(
        student_assessment["score"],
        errors="coerce"
    )

    # Merge assessment details using assessment ID
    merged = student_assessment.merge(
        assessments,
        on="id_assessment",
        how="left",
        validate="many_to_one",
        indicator="_assessment_merge"
    )

    unmatched_assessments = (
        merged["_assessment_merge"] != "both"
    ).sum()

    merged = merged.drop(columns=["_assessment_merge"])

    # Merge student information using all three keys
    merged = merged.merge(
        student_info,
        on=[
            "id_student",
            "code_module",
            "code_presentation"
        ],
        how="left",
        validate="many_to_one",
        indicator="_student_merge"
    )

    unmatched_students = (
        merged["_student_merge"] != "both"
    ).sum()

    merged = merged.drop(columns=["_student_merge"])

    # Save merged dataset
    output_file = OUTPUT_DIR / "oulad_merged_assessments.csv"

    merged.to_csv(output_file, index=False)

    # Display summary
    print("\nMERGE SUMMARY")
    print("-" * 40)

    print("Total merged records:", len(merged))
    print("Total columns:", len(merged.columns))

    print("Missing scores:", merged["score"].isna().sum())

    print(
        "Unmatched assessment records:",
        unmatched_assessments
    )

    print(
        "Unmatched student records:",
        unmatched_students
    )

    print("\nAssessment type distribution:")
    print(merged["assessment_type"].value_counts(dropna=False))

    print("\nOutput saved to:")
    print(output_file)

    print("\nMerged dataset preview:")
    print(merged.head())


if __name__ == "__main__":
    merge_oulad_dataset()
