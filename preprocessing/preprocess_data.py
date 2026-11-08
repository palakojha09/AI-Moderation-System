
from pathlib import Path
import pandas as pd


# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = PROCESSED_DIR / "oulad_merged_assessments.csv"

CLEAN_OUTPUT = PROCESSED_DIR / "oulad_cleaned_assessments.csv"
MISSING_OUTPUT = PROCESSED_DIR / "oulad_missing_score_records.csv"
DUPLICATE_OUTPUT = PROCESSED_DIR / "oulad_duplicate_records.csv"


def preprocess_dataset():

    print("Loading merged OULAD dataset...")

    df = pd.read_csv(INPUT_FILE, low_memory=False)

    initial_records = len(df)

    # Convert score to numeric
    df["score"] = pd.to_numeric(
        df["score"],
        errors="coerce"
    )

    # Separate records with missing scores
    missing_scores = df[df["score"].isna()].copy()
    available_scores = df[df["score"].notna()].copy()

    # Check for duplicate student-assessment pairs
    duplicate_mask = available_scores.duplicated(
        subset=["id_student", "id_assessment"],
        keep=False
    )

    duplicates = available_scores[duplicate_mask].copy()

    # Remove duplicates from the modelling dataset,
    # but preserve them separately for inspection.
    available_scores = available_scores.drop_duplicates(
        subset=["id_student", "id_assessment"],
        keep="first"
    )

    # Validate score range
    invalid_mask = ~available_scores["score"].between(0, 100)

    invalid_scores = available_scores[invalid_mask].copy()

    available_scores = available_scores[
        ~invalid_mask
    ].copy()

    # Save separate datasets
    available_scores.to_csv(CLEAN_OUTPUT, index=False)

    missing_scores.to_csv(MISSING_OUTPUT, index=False)

    duplicates.to_csv(DUPLICATE_OUTPUT, index=False)

    # Display report
    print("\nPREPROCESSING REPORT")
    print("-" * 45)

    print("Initial records:", initial_records)
    print("Records with available scores:", initial_records - len(missing_scores))
    print("Missing score records:", len(missing_scores))
    print("Duplicate records:", len(duplicates))
    print("Invalid score records:", len(invalid_scores))
    print("Final clean records:", len(available_scores))

    print("\nScore statistics:")
    print(available_scores["score"].describe())

    print("\nAssessment type distribution:")
    print(
        available_scores["assessment_type"].value_counts()
    )

    print("\nSaved files:")
    print(CLEAN_OUTPUT)
    print(MISSING_OUTPUT)
    print(DUPLICATE_OUTPUT)


if __name__ == "__main__":
    preprocess_dataset()
