import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")

def get_forecast(location_str, api_key):
    location_key = get_location_key(location_str, api_key)
    response = get_daily_forecast(location_key, api_key)
    return response
def get_weather_data(city, days):
    location_key = get_location_key(city,  API_KEY)
    url = f"http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}?apikey={API_KEY}&metric=true&details=true"
    response = requests.get(url)

    if response.status_code != 200:
        print(
            f"Error: get_weather_data {response.status_code}"
        )
        return None

    forecast_data = response.json()["DailyForecasts"]

    dates = []
    temperatures = []
    wind_speeds = []
    precipitations = []

    for day in forecast_data:
        date = datetime.strptime(day["Date"][:10], "%Y-%m-%d")
        temperature = day["Temperature"]["Maximum"]["Value"]
        wind_speed = day["Day"]["Wind"]["Speed"]["Value"]
        precipitation = day["Day"].get("PrecipitationProbability", 0)
        if len(dates) < days:
            dates.append(date)
            temperatures.append(temperature)
            wind_speeds.append(wind_speed)
            precipitations.append(precipitation)

    data = {
        "date": dates[:days:],
        "temperature": temperatures[:days:],
        "wind_speed": wind_speeds[:days:],
        "precipitation": precipitations[:days:],
    }

    return pd.DataFrame(data)


import requests


def get_city_coordinates(city_name):

    url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={API_KEY}&q={city_name}"
    print(url)

    response = requests.get(url)

    if response.status_code != 200:
        print(
            f"Error: get_city_coordinates {response.status_code}"
        )
        return None

    location_data = response.json()

    if not location_data:
        print("Город не найден")
        return None

    latitude = location_data[0]["GeoPosition"]["Latitude"]
    longitude = location_data[0]["GeoPosition"]["Longitude"]

    return (latitude, longitude)


def get_daily_forecast(location_key, api_key):
    params = {
            "apikey": api_key,
            "details": "true",
            "metric": "true"}
    url = f"http://dataservice.accuweather.com/currentconditions/v1/daily/5day/{location_key}"

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении прогноза погоды: {e}")
        return None

def get_location_key(location, api_key):
    params = {
        'apikey': api_key,
        'q': location
    }
    url = f'http://dataservice.accuweather.com/locations/v1/cities/search?apikey={api_key}&q={location}'

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data:
            return data[0]["Key"]
        else:
            print("Город не найден.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при поиске города: {e}")
        return None