
import pandas as pd
import pytest

from backend.app import app
import backend.app as backend_app


@pytest.fixture
def sample_data(tmp_path, monkeypatch):
    """Create a temporary OULAD moderation dataset for API tests."""

    data = pd.DataFrame([
        {
            "id_student": 1001,
            "id_assessment": 1,
            "code_module": "AAA",
            "code_presentation": "2013J",
            "assessment_type": "TMA",
            "score": 65.0,
            "Assessment_Median": 60.0,
            "Score_Deviation": 5.0,
            "Score_Percentile": 75.0,
            "Anomaly_Score": 0.8,
            "Statistical_Anomaly": True,
            "Isolation_Forest_Anomaly": True,
            "Requires_Human_Review": True,
            "Review_Priority": "High",
            "Detection_Source": "Both",
            "Review_Reason": "Above assessment median",
            "Recommendation": "Strong Review Recommended",
        },
        {
            "id_student": 1001,
            "id_assessment": 2,
            "code_module": "AAA",
            "code_presentation": "2013J",
            "assessment_type": "TMA",
            "score": 40.0,
            "Assessment_Median": 50.0,
            "Score_Deviation": -10.0,
            "Score_Percentile": 20.0,
            "Anomaly_Score": 0.5,
            "Statistical_Anomaly": True,
            "Isolation_Forest_Anomaly": False,
            "Requires_Human_Review": True,
            "Review_Priority": "Medium",
            "Detection_Source": "Statistical",
            "Review_Reason": "Below assessment median",
            "Recommendation": "Review Recommended",
        },
        {
            "id_student": 1002,
            "id_assessment": 1,
            "code_module": "AAA",
            "code_presentation": "2013J",
            "assessment_type": "TMA",
            "score": 55.0,
            "Assessment_Median": 60.0,
            "Score_Deviation": -5.0,
            "Score_Percentile": 40.0,
            "Anomaly_Score": 0.1,
            "Statistical_Anomaly": False,
            "Isolation_Forest_Anomaly": False,
            "Requires_Human_Review": False,
            "Review_Priority": "None",
            "Detection_Source": "None",
            "Review_Reason": "No significant anomaly",
            "Recommendation": "No Significant Anomaly",
        },
    ])

    data_file = tmp_path / "oulad_test_results.csv"
    data.to_csv(data_file, index=False)

    monkeypatch.setattr(backend_app, "DATA_FILE", data_file)

    return data


@pytest.fixture
def client(sample_data):
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def test_health_endpoint(client):
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["dataset"] == "OULAD"


def test_summary_endpoint(client):
    response = client.get("/api/summary")

    assert response.status_code == 200

    data = response.get_json()

    assert data["total_records"] == 3
    assert data["review_cases"] == 2
    assert data["normal_records"] == 1
    assert data["statistical_anomalies"] == 2
    assert data["isolation_forest_anomalies"] == 1
    assert data["strong_reviews"] == 1
    assert data["medium_reviews"] == 1
    assert data["review_rate"] == 66.67


def test_reviews_endpoint(client):
    response = client.get("/api/reviews")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) == 2


def test_review_record_structure(client):
    response = client.get("/api/reviews")

    data = response.get_json()

    required_fields = {
        "id_student",
        "id_assessment",
        "code_module",
        "assessment_type",
        "score",
        "Assessment_Median",
        "Score_Deviation",
        "Anomaly_Score",
        "Review_Priority",
        "Recommendation",
    }

    assert required_fields.issubset(data[0].keys())


def test_reviews_filter(client):
    response = client.get("/api/reviews?priority=High")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 1
    assert data[0]["Review_Priority"] == "High"


def test_student_details_endpoint(client):
    response = client.get("/api/students/1001")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) == 2
    assert all(record["id_student"] == 1001 for record in data)


def test_student_not_found(client):
    response = client.get("/api/students/9999")

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Student not found"


def test_assessment_details_endpoint(client):
    response = client.get("/api/assessments/1")

    assert response.status_code == 200

    data = response.get_json()

    assert data["assessment_id"] == "1"
    assert data["module"] == "AAA"
    assert data["total_records"] == 2
    assert data["review_cases"] == 1
    assert data["review_rate"] == 50.0
    assert data["average_score"] == 60.0
    assert data["median_score"] == 60.0


def test_assessment_not_found(client):
    response = client.get("/api/assessments/999")

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Assessment not found"


def test_analytics_endpoint(client):
    response = client.get("/api/analytics")

    assert response.status_code == 200

    data = response.get_json()

    assert "assessment_analysis" in data
    assert "module_analysis" in data

    assert len(data["assessment_analysis"]) == 1
    assert len(data["module_analysis"]) == 1

    assert data["assessment_analysis"][0]["assessment_type"] == "TMA"
    assert data["module_analysis"][0]["code_module"] == "AAA"
