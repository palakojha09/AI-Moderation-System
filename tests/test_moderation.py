import pandas as pd


RESULT_FILE = "data/processed/final_moderation_results.csv"


def test_moderation_results_exist():
    df = pd.read_csv(RESULT_FILE)

    assert len(df) == 2000


def test_anomaly_score_is_valid():
    df = pd.read_csv(RESULT_FILE)

    assert df["Anomaly_Score"].between(0, 4).all()


def test_review_flag_is_boolean():
    df = pd.read_csv(RESULT_FILE)

    assert df["Requires_Human_Review"].isin([True, False]).all()


def test_recommendations_are_valid():
    df = pd.read_csv(RESULT_FILE)

    valid_recommendations = {
        "No Significant Anomaly",
        "Review Recommended",
        "Strong Review Recommended",
    }

    assert set(df["Recommendation"]).issubset(
        valid_recommendations
    )


def test_deviation_direction_is_valid():
    df = pd.read_csv(RESULT_FILE)

    valid_directions = {
        "No Significant Direction",
        "Potential Under-marking",
        "Potential Over-marking",
    }

    assert set(df["Deviation_Direction"]).issubset(
        valid_directions
    )


def test_anomaly_score_matches_review_flag():
    df = pd.read_csv(RESULT_FILE)

    expected_review = df["Anomaly_Score"] >= 2

    assert (
        df["Requires_Human_Review"] == expected_review
    ).all()