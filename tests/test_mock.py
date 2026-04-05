from api.app import app
from fastapi.testclient import TestClient
from unittest.mock import patch
import sys
sys.path.append(".")

client = TestClient(app)


@patch("api.app.model")
@patch("api.app.ohe")
def test_predict_male_normal_bmi(mock_ohe, mock_model):
    mock_ohe.transform.return_value = [[1]]
    mock_model.predict.return_value = [22.5]
    response = client.post("/predict", json={
        "gender": "Male",
        "age": 30,
        "height": 175.0,
        "weight": 70.0
    })
    assert response.status_code == 200
    assert "bmi" in response.json()
    assert "quote" in response.json()
    assert "reason" in response.json()


@patch("api.app.model")
@patch("api.app.ohe")
def test_predict_female_discount(mock_ohe, mock_model):
    mock_ohe.transform.return_value = [[0]]
    mock_model.predict.return_value = [22.5]
    response = client.post("/predict", json={
        "gender": "Female",
        "age": 30,
        "height": 165.0,
        "weight": 65.0
    })
    assert response.status_code == 200
    assert response.json()["quote"] == 540.0


@patch("api.app.model")
@patch("api.app.ohe")
def test_invalid_gender(mock_ohe, mock_model):
    response = client.post("/predict", json={
        "gender": "Other",
        "age": 30,
        "height": 175.0,
        "weight": 70.0
    })
    assert response.status_code == 422


@patch("api.app.model")
@patch("api.app.ohe")
def test_age_below_minimum(mock_ohe, mock_model):
    response = client.post("/predict", json={
        "gender": "Male",
        "age": 10,
        "height": 175.0,
        "weight": 70.0
    })
    assert response.status_code == 422


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
