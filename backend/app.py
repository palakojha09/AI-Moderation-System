
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "oulad_final_moderation_results.csv"
)

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])


def load_data():
    """Load the final OULAD moderation results."""
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Moderation results not found: {DATA_FILE}"
        )

    df = pd.read_csv(DATA_FILE, low_memory=False)

    boolean_columns = [
        "Statistical_Anomaly",
        "Isolation_Forest_Anomaly",
        "Requires_Human_Review",
    ]

    for column in boolean_columns:
        if column in df.columns:
            df[column] = (
                df[column]
                .astype(str)
                .str.lower()
                .isin(["true", "1", "yes"])
            )

    return df


def clean_records(df):
    """Replace missing values for JSON serialization."""
    return df.astype(object).where(pd.notna(df), None)


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "success",
        "message": "AI Moderation API is running",
        "dataset": "OULAD",
    })


@app.route("/api/summary", methods=["GET"])
def summary():
    df = load_data()

    total_records = len(df)
    review_cases = int(df["Requires_Human_Review"].sum())

    return jsonify({
        "total_records": total_records,
        "review_cases": review_cases,
        "normal_records": total_records - review_cases,
        "statistical_anomalies": int(
            df["Statistical_Anomaly"].sum()
        ),
        "isolation_forest_anomalies": int(
            df["Isolation_Forest_Anomaly"].sum()
        ),
        "strong_reviews": int(
            (df["Review_Priority"] == "High").sum()
        ),
        "medium_reviews": int(
            (df["Review_Priority"] == "Medium").sum()
        ),
        "review_rate": round(
            review_cases / total_records * 100, 2
        ) if total_records else 0,
    })


@app.route("/api/reviews", methods=["GET"])
def review_cases():
    df = load_data()

    reviews = df[
        df["Requires_Human_Review"]
    ].copy()

    # Optional filters
    assessment_type = request.args.get("assessment_type")
    module = request.args.get("module")
    priority = request.args.get("priority")

    if assessment_type:
        reviews = reviews[
            reviews["assessment_type"] == assessment_type
        ]

    if module:
        reviews = reviews[
            reviews["code_module"] == module
        ]

    if priority:
        reviews = reviews[
            reviews["Review_Priority"] == priority
        ]

    columns = [
        "id_student",
        "id_assessment",
        "code_module",
        "code_presentation",
        "assessment_type",
        "score",
        "Assessment_Median",
        "Score_Deviation",
        "Score_Percentile",
        "Anomaly_Score",
        "Review_Priority",
        "Detection_Source",
        "Review_Reason",
        "Recommendation",
    ]

    reviews = reviews[columns].sort_values(
        by=["Review_Priority", "Anomaly_Score"],
        ascending=[True, False],
    )

    reviews = clean_records(reviews)

    return jsonify(reviews.to_dict(orient="records"))


@app.route("/api/students/<student_id>", methods=["GET"])
def student_details(student_id):
    df = load_data()

    student = df[
        df["id_student"].astype(str) == str(student_id)
    ].copy()

    if student.empty:
        return jsonify({
            "error": "Student not found"
        }), 404

    columns = [
        "id_student",
        "id_assessment",
        "code_module",
        "code_presentation",
        "assessment_type",
        "score",
        "Assessment_Median",
        "Score_Deviation",
        "Score_Percentile",
        "Anomaly_Score",
        "Recommendation",
        "Review_Priority",
        "Requires_Human_Review",
        "Review_Reason",
    ]

    student = student[columns].sort_values(
        by="id_assessment"
    )

    student = clean_records(student)

    return jsonify(student.to_dict(orient="records"))


@app.route("/api/assessments/<assessment_id>", methods=["GET"])
def assessment_details(assessment_id):
    df = load_data()

    assessment = df[
        df["id_assessment"].astype(str) == str(assessment_id)
    ].copy()

    if assessment.empty:
        return jsonify({
            "error": "Assessment not found"
        }), 404

    total = len(assessment)
    reviews = int(assessment["Requires_Human_Review"].sum())

    return jsonify({
        "assessment_id": assessment_id,
        "module": assessment["code_module"].iloc[0],
        "presentation": assessment["code_presentation"].iloc[0],
        "assessment_type": assessment["assessment_type"].iloc[0],
        "total_records": total,
        "review_cases": reviews,
        "review_rate": round(
            reviews / total * 100, 2
        ) if total else 0,
        "average_score": round(
            float(assessment["score"].mean()), 2
        ),
        "median_score": round(
            float(assessment["score"].median()), 2
        ),
    })


@app.route("/api/analytics", methods=["GET"])
def analytics():
    df = load_data()

    assessment_summary = (
        df.groupby("assessment_type")
        .agg(
            total_records=("id_student", "count"),
            review_cases=("Requires_Human_Review", "sum"),
        )
        .reset_index()
    )

    assessment_summary["review_rate"] = (
        assessment_summary["review_cases"]
        / assessment_summary["total_records"] * 100
    ).round(2)

    module_summary = (
        df.groupby("code_module")
        .agg(
            total_records=("id_student", "count"),
            review_cases=("Requires_Human_Review", "sum"),
        )
        .reset_index()
    )

    module_summary["review_rate"] = (
        module_summary["review_cases"]
        / module_summary["total_records"] * 100
    ).round(2)

    return jsonify({
        "assessment_analysis": clean_records(
            assessment_summary
        ).to_dict(orient="records"),
        "module_analysis": clean_records(
            module_summary
        ).to_dict(orient="records"),
    })


if __name__ == "__main__":
    app.run(debug=True)
