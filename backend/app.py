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

if __name__ == "__main__":
    app.run(debug=True)