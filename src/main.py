from fastapi import FastAPI
from database import InMemoryDatabase

import uvicorn
import pickle
import numpy as np
from datetime import datetime

# TODO:
# Utilizar informações resumidas do voo, como origem e destino
#   A partir disso utilizar a sua latitude e logitude para calcular a distancia bem como para o capturar clima atual ou de uma data especifica
# Carregar arquivo de modelo da nuvem
# Documentar melhor os endpoints utilizando tags, summary e description
# Criar classes para evitar o uso de variáveis globais
# Armazenamento persistente do histórico de predições

app = FastAPI()

# Variavel global que armazena o modelo carregado
model = None

# Variavel global que informa a pasta que contém os modelos
# (necessário por causa do local da pasta do pytest)
models_folder = None

def set_models_folder(_models_folder):
    global models_folder
    models_folder = _models_folder
    print(f"models_folder set to {models_folder}")

set_models_folder("../models")

"""
Endpoints da API

"""
@app.get("/health", status_code=200, tags=["health"], summary="Health check")
async def health():
    return {"status": "ok"}

@app.post("/model/predict", status_code=200, tags=["example"], summary="Make a prediction with the model")
async def model_predict(data: dict):

    print(data)

    if model is None:
        return {"status": "error", "msg": f"No model has been loaded"}

    # Verifica entradas na request, baseado nas features necessárias para o modelo carregado
    for d in model.feature_names_in_:
        if d not in data:
            return {"status": "error", "msg": f"Expected data '{d}' not found"}
    
    # Transforma inputs do dict para array na ordem correta
    input_arr = np.array([data[d] for d in model.feature_names_in_]).reshape(1, -1)
    print(input_arr)
    
    #Predição
    pred = model.predict(input_arr)[0]
    print(pred)

    response = {"status": "ok", "predicted_arr_delay": pred}

    # Formata a response
    prediction = {
        "prediction_time": datetime.now().isoformat(),
        "data": data,
        "response": response
    }

    # Salva no database e retorna
    db = InMemoryDatabase()
    predictions = db.get_collection('predictions')
    predictions.insert_one(prediction)

    return response

@app.get("/model/history/", tags=["example"], summary="List predictions history")
async def model_history():

    # Retorna o histórico salvo no database
    db = InMemoryDatabase()
    predictions = db.get_collection('predictions')
    return {"status": "ok", "predictions": [x for x in predictions.find({})]}

@app.post("/model/load/", status_code=200, tags=["example"], summary="Load model from url")
async def model_load(data: dict):

    if "filename" not in data:
         return {"status": "error", "msg": "Must specify 'filename' field"}

    global model

    # Carrega o modelo do arquivo, armazena na variável global para posterior uso
    print(f"Loading model {data['filename']}")
    try:
        with open(f"{models_folder}/{data['filename']}", "rb") as file:
            model = pickle.load(file)
        print(model.feature_names_in_)
    except Exception as e:
        error = f"Error loading model: {str(e)}"
        print(error)
        return {"status": "error", "msg": error}
    
    return {"status": "ok", "msg": "Model loaded"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="debug")