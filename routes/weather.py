import os
from utls.main import *
from flask import Blueprint, render_template, request
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
bp = Blueprint('weather', __name__, url_prefix='/weather')


@bp.route('/route', methods=['GET', 'POST'])
def weather_route():
    print("weather")
    if request.method == 'POST':
        print("post weather")
        start_city = request.form.get('start')
        end_city = request.form.get('end')

        start_key = get_location_key(start_city, API_KEY)
        end_key = get_location_key(end_city, API_KEY)
        if start_key == "connection_error" or end_key == "connection_error":
            return render_template('error.html', error="Не удалось подключиться к API")

        if not start_key or not end_key:
            return render_template('error.html', error="Ошибка при получении данных о городах")

        start_weather = get_forecast(start_key, API_KEY)
        end_weather = get_forecast(end_key, API_KEY)

        if start_weather == "connection_error" or end_weather == "connection_error":
            return render_template('error.html', error="Не удалось подключиться к API")
        if not start_weather or not end_weather:
            return render_template('error.html', error="Ошибка при получении данных о погоде")

        start_temp = start_weather[0]['Temperature']['Metric']['Value']
        end_temp = end_weather[0]['Temperature']['Metric']['Value']

        start_wind_speed = get_wind_speed(start_weather[0])
        end_wind_speed = get_wind_speed(end_weather[0])

        start_precipitation_probability = get_precipitation_probability(start_weather[0])
        end_precipitation_probability = get_precipitation_probability(end_weather[0])
        start_precipitation = get_precipitation(start_weather[0])
        end_precipitation = get_precipitation(end_weather[0])

        start_assessment = check_bad_weather(start_temp, start_wind_speed, start_precipitation_probability,
                                             start_precipitation)
        end_assessment = check_bad_weather(end_temp, end_wind_speed, end_precipitation_probability, end_precipitation)

        return render_template(
            'result.html',
            start=start_city,
            end=end_city,
            start_weather=start_weather[0],
            end_weather=end_weather[0],
            start_assessment=start_assessment,
            end_assessment=end_assessment
        )
    return render_template('index.html')


def check_bad_weather(temperature, wind_speed, precipitation_prob, has_precipitation):
    if temperature < 0 or temperature > 35:
        return "Неблагоприятные условия - температура"
    if wind_speed > 50:
        return "Неблагоприятные условия - ветер"
    if precipitation_prob > 70 or has_precipitation:
        return "Неблагоприятные условия - осадки"
    return "Благоприятные условия"


def get_wind_speed(weather_data):
    try:
        return weather_data['Wind']['Speed']['Metric']['Value']
    except KeyError:
        return 0


def get_precipitation_probability(weather_data):
    try:
        return weather_data['PrecipitationProbability']
    except KeyError:
        return 0


def get_precipitation(weather_data):
    try:
        return weather_data['HasPrecipitation']
    except KeyError:
        return 0