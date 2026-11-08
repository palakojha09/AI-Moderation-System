from pathlib import Path

import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = PROCESSED_DIR / "oulad_featured_assessments.csv"
OUTPUT_FILE = PROCESSED_DIR / "oulad_isolation_forest_results.csv"


# Original numerical features
NUMERIC_FEATURES = [
    "score",
    "weight",
    "num_of_prev_attempts",
    "studied_credits",
]

# Categorical feature
CATEGORICAL_FEATURES = [
    "code_module",
]

CONTAMINATION = 0.02
RANDOM_STATE = 42


def create_model():

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "isolation_forest",
                IsolationForest(
                    n_estimators=200,
                    contamination=CONTAMINATION,
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    return model


def run_isolation_forest():

    print("Loading OULAD dataset...")

    df = pd.read_csv(INPUT_FILE, low_memory=False)

    required_columns = (
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
        + ["assessment_type", "id_student", "id_assessment"]
    )

    missing_columns = [
        col for col in required_columns if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Initialise output columns
    df["Isolation_Forest_Prediction"] = 1
    df["Isolation_Forest_Anomaly"] = False
    df["Isolation_Forest_Score"] = 0.0

    print("\nTraining separate models by assessment type...")

    for assessment_type in sorted(
        df["assessment_type"].dropna().unique()
    ):

        mask = df["assessment_type"] == assessment_type
        group = df.loc[mask].copy()

        X = group[NUMERIC_FEATURES + CATEGORICAL_FEATURES]

        print(f"\nTraining {assessment_type} model...")
        print("Records:", len(group))

        model = create_model()

        model.fit(X)

        predictions = model.predict(X)

        anomaly_scores = -model.decision_function(X)

        df.loc[mask, "Isolation_Forest_Prediction"] = predictions

        df.loc[mask, "Isolation_Forest_Anomaly"] = (
            predictions == -1
        )

        df.loc[mask, "Isolation_Forest_Score"] = anomaly_scores

        anomalies = int((predictions == -1).sum())

        print("Detected anomalies:", anomalies)

        print(
            "Detection percentage:",
            round(anomalies / len(group) * 100, 2),
            "%"
        )

    df["Isolation_Forest_Prediction"] = (
        df["Isolation_Forest_Prediction"].astype(int)
    )

    df["Isolation_Forest_Anomaly"] = (
        df["Isolation_Forest_Anomaly"].astype(bool)
    )

    df.to_csv(OUTPUT_FILE, index=False)

    print("\nISOLATION FOREST SUMMARY")
    print("-" * 45)

    print("Total records:", len(df))

    print("\nAnomaly counts by assessment type:")

    summary = df.groupby("assessment_type")[
        "Isolation_Forest_Anomaly"
    ].agg(["count", "sum", "mean"])

    summary["Anomaly_Rate"] = (
        summary["mean"] * 100
    ).round(2)

    print(summary)

    anomalies = int(df["Isolation_Forest_Anomaly"].sum())

    print("\nTotal detected anomalies:", anomalies)

    print(
        "Overall detection percentage:",
        round(anomalies / len(df) * 100, 2),
        "%"
    )

    print("\nHighest anomaly scores:")

    print(
        df.nlargest(10, "Isolation_Forest_Score")[
            [
                "id_student",
                "id_assessment",
                "assessment_type",
                "score",
                "Isolation_Forest_Score",
            ]
        ].to_string(index=False)
    )

    print("\nOutput saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    run_isolation_forest()