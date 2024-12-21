import requests

def get_forecast(location_str, api_key):
    location_key = get_location_key(location_str, api_key)
    response = get_daily_forecast(location_key, api_key)
    return response
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