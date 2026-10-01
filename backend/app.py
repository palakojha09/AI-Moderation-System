from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "success",
        "message": "AI Moderation API is running"
    })


@app.route("/api/summary", methods=["GET"])
def summary():
    df = pd.read_csv(
        "data/processed/final_moderation_results.csv"
    )

    total_records = len(df)

    anomalies = int(df["Injected_Anomaly"].sum())

    review_cases = int(
        df["Requires_Human_Review"].sum()
    )

    under_marking = int(
        (
            df["Deviation_Direction"]
            == "Potential Under-marking"
        ).sum()
    )

    over_marking = int(
        (
            df["Deviation_Direction"]
            == "Potential Over-marking"
        ).sum()
    )

    return jsonify({
        "total_records": total_records,
        "anomalies": anomalies,
        "review_cases": review_cases,
        "under_marking": under_marking,
        "over_marking": over_marking
    })

@app.route("/api/reviews", methods=["GET"])
def review_cases():
    df = pd.read_csv(
        "data/processed/final_moderation_results.csv"
    )

    reviews = df[
        df["Requires_Human_Review"] == True
    ].copy()

    columns = [
        "Student_ID",
        "Subject",
        "Faculty_ID",
        "Given_Marks",
        "Expected_Marks",
        "Deviation",
        "Deviation_Percentage",
        "Anomaly_Score",
        "Deviation_Direction",
        "Recommendation"
    ]

    reviews = reviews[columns]

    return jsonify(
        reviews.to_dict(orient="records")
    )

@app.route("/api/students/<student_id>", methods=["GET"])
def student_details(student_id):
    df = pd.read_csv(
        "data/processed/final_moderation_results.csv"
    )

    student = df[
        df["Student_ID"].astype(str) == str(student_id)
    ].copy()

    if student.empty:
        return jsonify({
            "error": "Student not found"
        }), 404

    columns = [
        "Student_ID",
        "Subject",
        "Faculty_ID",
        "Given_Marks",
        "Expected_Marks",
        "Deviation",
        "Deviation_Percentage",
        "Anomaly_Score",
        "Deviation_Direction",
        "Recommendation",
        "Requires_Human_Review"
    ]

    student = student[columns]

    return jsonify(
        student.to_dict(orient="records")
    )

@app.route("/api/faculty/<faculty_id>", methods=["GET"])
def faculty_details(faculty_id):
    df = pd.read_csv(
        "data/processed/final_moderation_results.csv"
    )

    faculty = df[
        df["Faculty_ID"].astype(str) == str(faculty_id)
    ].copy()

    if faculty.empty:
        return jsonify({
            "error": "Faculty not found"
        }), 404

    total_records = len(faculty)

    average_given_marks = round(
        faculty["Given_Marks"].mean(), 2
    )

    average_expected_marks = round(
        faculty["Expected_Marks"].mean(), 2
    )

    average_deviation = round(
        faculty["Deviation"].mean(), 2
    )

    review_cases = int(
        faculty["Requires_Human_Review"].sum()
    )

    under_marking = int(
        (
            faculty["Deviation_Direction"]
            == "Potential Under-marking"
        ).sum()
    )

    over_marking = int(
        (
            faculty["Deviation_Direction"]
            == "Potential Over-marking"
        ).sum()
    )

    return jsonify({
        "faculty_id": faculty_id,
        "total_records": total_records,
        "average_given_marks": average_given_marks,
        "average_expected_marks": average_expected_marks,
        "average_deviation": average_deviation,
        "review_cases": review_cases,
        "under_marking": under_marking,
        "over_marking": over_marking
    })

if __name__ == "__main__":
    app.run(debug=True)