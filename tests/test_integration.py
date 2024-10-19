from fastapi.testclient import TestClient
from main import app, set_models_folder

client = TestClient(app)
set_models_folder("models/")

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_load():
    response = client.post("/model/load", json={"filename": "model1.pkl"})
    assert response.status_code == 200
    assert response.json().get("status") == "ok"

def test_predict():
    response = client.post("/model/predict", json={"dep_delay": 12,"distance": 1000})
    assert response.status_code == 200
    assert response.json().get("status") == "ok"
    assert response.json().get("predicted_arr_delay") is not None

def test_history():
    response = client.get("/model/history")
    assert response.status_code == 200
    assert response.json().get("status") == "ok"
    assert response.json().get("predictions") is not None    
    assert len(response.json().get("predictions")) == 1