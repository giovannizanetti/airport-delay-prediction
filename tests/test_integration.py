from fastapi.testclient import TestClient
from main import app, set_models_folder, set_data_folder
from airports import AirportsInfo

client = TestClient(app)
set_models_folder("models/")
set_data_folder("data/")

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

def test_airports_info():
    airports_info = AirportsInfo("data")

    assert airports_info.get_distance("JFK", "MCI") == 1113
    assert airports_info.get_distance("JFK", "AAA") is None
    assert airports_info.get_distance("AAA", "BBB") is None

    assert airports_info.get_location("JFK") == {"latitude": 40.639801, "longitude": -73.7789}
    assert airports_info.get_location("AAA") is None

def test_airports_weather():

    # Precisa da API key
        
    airports_info = AirportsInfo("data")
    
    weather_JFK, _ = airports_info.get_current_weather("JFK")
    assert weather_JFK.get("wind_spd") is not None
    assert weather_JFK.get("clouds") is not None
    assert weather_JFK.get("vis") is not None

    weather_AAA, _ = airports_info.get_current_weather("AAA")
    assert weather_AAA == {}