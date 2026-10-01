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


def test_student_details_endpoint():
    client = app.test_client()

    response = client.get("/api/students/S002")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) == 4
    assert data[0]["Student_ID"] == "S002"


def test_student_not_found():
    client = app.test_client()

    response = client.get("/api/students/S999")

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Student not found"

def test_faculty_details_endpoint():
    client = app.test_client()

    response = client.get("/api/faculty/F05")

    assert response.status_code == 200

    data = response.get_json()

    assert data["faculty_id"] == "F05"
    assert data["total_records"] > 0

    assert "average_given_marks" in data
    assert "average_expected_marks" in data
    assert "average_deviation" in data
    assert "review_cases" in data
    assert "under_marking" in data
    assert "over_marking" in data


def test_faculty_not_found():
    client = app.test_client()

    response = client.get("/api/faculty/F99")

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Faculty not found"