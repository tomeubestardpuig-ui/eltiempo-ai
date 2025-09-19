import os
import requests
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# Cargar variables de entorno (las API keys)
load_dotenv()

# Configurar la App Flask
app = Flask(__name__)

# Configurar la API de Google Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# Ruta principal que muestra la página web
@app.route('/')
def index():
    return render_template('index.html')

# Ruta de la API que procesará la solicitud
@app.route('/get_weather_narrative', methods=['POST'])
def get_weather_narrative():
    try:
        city = request.json['city']
        
        # 1. Obtener datos del tiempo de OpenWeatherMap
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={os.getenv('OPENWEATHER_API_KEY')}&units=metric&lang=es"
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status() # Lanza un error si la petición falla
        weather_data = weather_response.json()

        # Extraer los datos que nos interesan
        description = weather_data['weather'][0]['description']
        temp = weather_data['main']['temp']
        feels_like = weather_data['main']['feels_like']
        humidity = weather_data['main']['humidity']
        wind_speed = weather_data['wind']['speed']

        # 2. Crear el prompt para la IA
        prompt = f"""
        Actúa como un meteorólogo carismático y creativo para el portal 'eltiempo.ai'.
        Tu misión es transformar datos meteorológicos técnicos en una narrativa breve, atractiva y fácil de entender para el público general. Sé cercano y original.
        No menciones la velocidad del viento en m/s ni la humedad en porcentaje, intégralo en la narrativa.

        Basado en los siguientes datos para la ciudad de {city}:
        - Condición general: {description}
        - Temperatura: {temp}°C
        - Sensación térmica: {feels_like}°C
        - Humedad: {humidity}%
        - Velocidad del viento: {wind_speed} m/s

        Crea un pronóstico narrativo.
        """

        # 3. Llamar a la API de Gemini
        ai_response = model.generate_content(prompt)
        narrative = ai_response.text

        # 4. Devolver el resultado
        return jsonify({'narrative': narrative})

    except requests.exceptions.HTTPError as err:
        if weather_response.status_code == 404:
            return jsonify({'error': f'No se pudo encontrar la ciudad: {city}. Por favor, verifica el nombre.'}), 404
        return jsonify({'error': f'Error al obtener los datos del tiempo: {err}'}), 500
    except Exception as e:
        return jsonify({'error': f'Ha ocurrido un error inesperado: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)