from fastapi import FastAPI
from database import InMemoryDatabase

import uvicorn
import pickle
import numpy as np
from datetime import datetime


app = FastAPI()

with open("../../model2.pkl", "rb") as file:
    model = pickle.load(file)
print(model.feature_names_in_)

@app.get("/health", status_code=200, tags=["health"], summary="Health check")
async def health():
    return {"status": "ok"}

@app.post("/model/predict", status_code=200, tags=["example"], summary="Make a prediction with the model")
async def model_predict(data: dict):

    print(data)

    # aqui é possível fazer uma validação do requet body mais robusta usando o Draft4Validator
    expected_data = ['dep_delay', 'distance', 'origin_wind_spd', 'origin_clouds', 'origin_vis', 'dest_wind_spd', 'dest_clouds', 'dest_vis']
    # puxar informações do clima pela API
    # distancia tambem daria para fazer a partir de origem e destino
    for d in expected_data:
        if d not in data:
            return {"status": "error", "msg": f"Expected data '{d}' not found"}
    
    input_arr = np.array([data[d] for d in model.feature_names_in_]).reshape(1, -1)
    print(input_arr)
    
    pred = model.predict(input_arr)[0]
    print(pred)

    response = {"status": "ok", "predicted_arr_delay": pred}

    prediction = {
        "prediction_time": datetime.now().isoformat(),
        "data": data,
        "response": response
    }
    db = InMemoryDatabase()
    predictions = db.get_collection('predictions')
    predictions.insert_one(prediction)

    return response

@app.get("/model/history/", tags=["example"], summary="List predictions history")
async def model_history():
    db = InMemoryDatabase()
    predictions = db.get_collection('predictions')
    return {"status": "ok", "predictions": [x for x in predictions.find({})]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="debug")