from flask import Flask, render_template, request
from models import Weather
import requests
import datetime

app = Flask(__name__)

GEO_URL = 'https://geocoding-api.open-meteo.com/v1/search'
FORECAST_URL = 'https://api.open-meteo.com/v1/forecast'

# Open-Meteo آیکون نمیده، فقط کد WMO میده؛ توضیح هر کد از مستندات
WMO_CODES = {
    0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
    45: 'Fog', 48: 'Depositing rime fog',
    51: 'Light drizzle', 53: 'Moderate drizzle', 55: 'Dense drizzle',
    56: 'Light freezing drizzle', 57: 'Dense freezing drizzle',
    61: 'Slight rain', 63: 'Moderate rain', 65: 'Heavy rain',
    66: 'Light freezing rain', 67: 'Heavy freezing rain',
    71: 'Slight snow fall', 73: 'Moderate snow fall', 75: 'Heavy snow fall',
    77: 'Snow grains',
    80: 'Slight rain showers', 81: 'Moderate rain showers', 82: 'Violent rain showers',
    85: 'Slight snow showers', 86: 'Heavy snow showers',
    95: 'Thunderstorm', 96: 'Thunderstorm with slight hail', 99: 'Thunderstorm with heavy hail',
}

# یه ایموجی ساده به جای آیکون
def get_icon(code):
    if code == 0: return '☀️'
    if code in (1, 2): return '🌤️'
    if code == 3: return '☁️'
    if code in (45, 48): return '🌫️'
    if code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82): return '🌧️'
    if code in (71, 73, 75, 77, 85, 86): return '❄️'
    if code in (95, 96, 99): return '⛈️'
    return ''


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        city = request.form['city'].strip()
        try:
            # مرحله ۱: اسم شهر -> مختصات
            geo = requests.get(GEO_URL, params={'name': city, 'count': 1}, timeout=10).json()
            if 'results' not in geo:
                return render_template('index.html', error='city not found!')
            place = geo['results'][0]

            # مرحله ۲: آب‌وهوای فعلی با مختصات
            res = requests.get(FORECAST_URL, params={
                'latitude': place['latitude'],
                'longitude': place['longitude'],
                'current': 'temperature_2m,relative_humidity_2m,surface_pressure,weather_code',
            }, timeout=10).json()
            cur = res['current']
            code = cur['weather_code']
            description = WMO_CODES.get(code, 'Unknown')

            Weather.create(temp=cur['temperature_2m'],
                           humidity=cur['relative_humidity_2m'],
                           pressure=cur['surface_pressure'],
                           description=description, weather_code=code,
                           city=city, date=datetime.datetime.now())

            data = {'city': place['name'], 'country': place.get('country', ''),
                    'temp': cur['temperature_2m'], 'humidity': cur['relative_humidity_2m'],
                    'pressure': cur['surface_pressure'], 'description': description,
                    'icon': get_icon(code)}
            return render_template('index.html', data=data)
        except (requests.RequestException, KeyError):
            return render_template('index.html', error='could not get weather, try again')
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
