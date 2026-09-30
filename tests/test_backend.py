from backend.app import app


def test_health_endpoint():
    client = app.test_client()

    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"


def test_summary_endpoint():
    client = app.test_client()

    response = client.get("/api/summary")

    assert response.status_code == 200

    data = response.get_json()

    assert data["total_records"] == 2000
    assert data["anomalies"] == 102
    assert data["review_cases"] == 98


def test_reviews_endpoint():
    client = app.test_client()

    response = client.get("/api/reviews")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) == 98


def test_review_record_structure():
    client = app.test_client()

    response = client.get("/api/reviews")

    data = response.get_json()

    required_fields = {
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
    }

    assert required_fields.issubset(data[0].keys())