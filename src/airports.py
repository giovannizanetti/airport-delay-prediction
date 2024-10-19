    
import json
import requests

class AirportsInfo:
    """
    Classe para armazenar dados de informações de aeroportos (latitude, longitude, distância entre aeroportos)
    A ideia é substituir isso por database dentro do MongoDB, persistido em disco
    Essa classe também retorna o clima atual de um determinado aeroporto

    """
    def __init__(self, data_folder):

        # Carrega dados de distâncias entre pares origem-destino
        with open(f"{data_folder}/airports_distances.json", "r") as file:
            self.airports_distances = json.load(file)

        # Carrega dados de latitude e longitude de cada aeroporto
        with open(f"{data_folder}/airports_location.json", "r") as file:
            self.airports_locations = json.load(file)

        # Carrega chave do WeatherBit API
        self.weatherbit_key = None
        try:
            with open(f"{data_folder}/weatherbit_key", "r") as file:
                self.weatherbit_key = file.readline()                    
        except Exception as e:
            print("ERROR: {str(e)}")

    def get_distance(self, origin, dest):
        """
        Captura distância entre origem e destino

        """
        if origin in self.airports_distances:
            if dest in self.airports_distances[origin]:
                return self.airports_distances[origin][dest]
        return None
    
    def get_location(self, airport):
        """
        Captura latitude e longitude de um aeroporto específico
        
        """        
        return self.airports_locations.get(airport)
    
    def get_current_weather(self, airport):
        """
        Captura clima atual de um determinado aeroporto
        
        """  
        location = self.get_location(airport)
        print(airport)
        print(location)
        if location is None:
            return {}, None

        url = 'http://api.weatherbit.io/v2.0/current'
        params = {
            'lat': location["latitude"],
            'lon': location["longitude"],
            'key': self.weatherbit_key
        }
        headers = {
            'Accept': 'application/json',
        }

        response = requests.get(url, params=params, headers=headers)
        status_code = response.status_code

        if status_code != 200:
            print(f"ERROR: ({status_code}) {response.text}")
            return {}, status_code

        data = response.json()    
    
        info_keys = ['wind_spd', 'clouds', 'vis']
        info_filtered = {k: v for k, v in data["data"][0].items() if k in info_keys} 

        print(info_filtered)
        return info_filtered, status_code    