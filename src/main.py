from fastapi import FastAPI
from database import InMemoryDatabase
from airports import AirportsInfo

import uvicorn
import pickle
import numpy as np
from datetime import datetime

# TODO:
# Utilizar o MongoDB para armazenar os dados dos aeroportos
# Carregar arquivo de modelo da nuvem
# Documentar melhor os endpoints utilizando tags, summary e description
# Criar classes para evitar o uso de variáveis globais
# Armazenamento persistente do histórico de predições
# Utilizar logger ao invés de print, configurar filehandler
# Tratamento de exceptions mais robusto

app = FastAPI()

# Variavel global que armazena o modelo carregado
model = None

# Variavel global que informa a pasta que contém os modelos e dados
# (necessário por causa do local da pasta do pytest)
models_folder = None
data_folder = None

def set_models_folder(_models_folder):
    global models_folder
    models_folder = _models_folder
    print(f"models_folder set to {models_folder}")

def set_data_folder(_data_folder):
    global data_folder
    data_folder = _data_folder
    print(f"data_folder set to {data_folder}")    

set_models_folder("../models")
set_data_folder("../data")

"""
Endpoints da API

"""
@app.get("/health", status_code=200, tags=["health"], summary="Health check")
async def health():
    """
    Retorna o estado da API

    """
    return {"status": "ok"}

@app.post("/model/predict", status_code=200, tags=["example"], summary="Make a prediction with the model")
async def model_predict(data: dict):
    """
    Retorna uma predição do modelo
    Utiliza todas as features do modelo como input, ou o par origem-destino
    Caso seja passado apenas o par origem-destino, captura as outras informações de acordo com o seguinte:
    - "distance": através do banco de dados salvo, com a informação de origem e destino
    - informações do clima da origem e destino: Captura latiude e longitude da origem e destino através de banco de dados salvo,
        em seguida, realiza a requisição par ao WeatherAPI para capturar as informações do clima

    """
    
    print(data)

    if model is None:
        return {"status": "error", "msg": f"No model has been loaded"}
    
    model_inputs = data.copy()

    # Caso tenha origem e destino na request, obtém as informações restantes
    if ("origin" in data) and ("dest" in data):
        airports_info = AirportsInfo(data_folder)
        
        # Preenche distância
        distance = airports_info.get_distance(data["origin"], data["dest"])
        if distance is not None:
            model_inputs["distance"] = distance

        # Dados do clima
        origin_weather, _ = airports_info.get_current_weather(data["origin"])
        dest_weather, _= airports_info.get_current_weather(data["dest"])
        for k, v in origin_weather.items():
            model_inputs[f"origin_{k}"] = v
        for k, v in dest_weather.items():
            model_inputs[f"dest_{k}"] = v            
    
    print(f"model_inputs={model_inputs}")
    # Verifica entradas na request, baseado nas features necessárias para o modelo carregado
    for f in model.feature_names_in_:
        if f not in model_inputs:
            return {"status": "error", "msg": f"Expected data '{f}' not found"}
    
    # Transforma inputs do dict para array na ordem correta
    input_arr = np.array([model_inputs[f] for f in model.feature_names_in_]).reshape(1, -1)
    print(f"input_arr={input_arr}")
    
    #Predição
    pred = model.predict(input_arr)[0]
    print(pred)

    response = {"status": "ok", "predicted_arr_delay": pred}

    # Formata a response
    prediction = {
        "prediction_time": datetime.now().isoformat(),
        "request_data": data,
        "model_inputs": model_inputs,
        "response": response
    }

    # Salva no database e retorna
    db = InMemoryDatabase()
    predictions = db.get_collection('predictions')
    predictions.insert_one(prediction)

    return response

@app.get("/model/history/", tags=["example"], summary="List predictions history")
async def model_history():
    """
    Retorna todo o histórico salvo no database

    """
    db = InMemoryDatabase()
    predictions = db.get_collection('predictions')
    return {"status": "ok", "predictions": [x for x in predictions.find({})]}

@app.post("/model/load/", status_code=200, tags=["example"], summary="Load model from url")
async def model_load(data: dict):
    """
    Carrega um modelo em memória

    """
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