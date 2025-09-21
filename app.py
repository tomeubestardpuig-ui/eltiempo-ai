import os
import requests
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno (las API keys)
load_dotenv()

# Configurar la App Flask
app = Flask(__name__)

# Configurar la API de Google Gemini
# Asegúrate de que la clave GEMINI_API_KEY está en tu archivo .env
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
        data = request.get_json()
        city = data.get('city')
        personality = data.get('personality', 'alegre')

        if not city:
            return jsonify({'error': 'El nombre de la ciudad es requerido.'}), 400
        
        weather_api_key = os.getenv('OPENWEATHER_API_KEY')
        
        # --- 1. OBTENER DATOS DEL TIEMPO ACTUAL ---
        current_weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric&lang=es"
        weather_response = requests.get(current_weather_url)
        weather_response.raise_for_status() # Lanza un error si la petición falla
        weather_data = weather_response.json()

        # Extraer datos actuales y coordenadas para la siguiente llamada
        description = weather_data['weather'][0]['description']
        temp = weather_data['main']['temp']
        feels_like = weather_data['main']['feels_like']
        humidity = weather_data['main']['humidity']
        wind_speed = weather_data['wind']['speed']
        lat = weather_data['coord']['lat']
        lon = weather_data['coord']['lon']

        # --- 2. GENERAR NARRATIVA CON IA (Como antes) ---
        prompt_base = "Actúa como un meteorólogo carismático y creativo para 'eltiempo.ai'. Transforma datos técnicos en una narrativa breve (40-50 palabras)."
        
        prompt_modifiers = {
            'alegre': "Usa un tono muy entusiasta y optimista. ¡Haz que el día suene genial!",
            'poetico': "Describe el tiempo de forma lírica, con metáforas y un lenguaje evocador.",
            'tecnico': "Sé preciso y educativo. Explica la situación con términos meteorológicos pero de forma comprensible.",
            'sarcástico': "Utiliza un humor irónico y un poco cínico para describir el tiempo. Sé divertido.",
            'para_ninos': "Explica el tiempo como si hablaras con un niño de 6 años, con ejemplos sencillos y animados."
        }
        prompt_modifier = prompt_modifiers.get(personality, prompt_modifiers['alegre'])

        full_prompt = f"""
        {prompt_base}
        **Tono a utilizar**: {prompt_modifier}
        Basado en los siguientes datos para {city}:
        - Condición: {description}, Temperatura: {temp}°C, Sensación: {feels_like}°C.
        - Humedad: {humidity}% y Viento: {wind_speed} m/s (intégralos en la narrativa sin mencionar los valores exactos).
        Crea el pronóstico narrativo. Sé conciso y no repitas el nombre de la ciudad.
        """
        ai_response = model.generate_content(full_prompt)
        narrative = ai_response.text

        # --- 3. NUEVO: OBTENER Y PROCESAR LA PREVISIÓN PARA 5 DÍAS ---
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={weather_api_key}&units=metric&lang=es"
        forecast_response = requests.get(forecast_url)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        
        forecast_list = []
        # Mapa para traducir los nombres de los días al español
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        for forecast in forecast_data['list']:
            # Seleccionamos solo las previsiones del mediodía (12:00)
            if forecast['dt_txt'].endswith("12:00:00"):
                timestamp = datetime.fromtimestamp(forecast['dt'])
                # .weekday() devuelve 0 para Lunes, 1 para Martes...
                day_name = dias_semana[timestamp.weekday()]
                
                # Evita añadir el día de hoy si ya es tarde
                if timestamp.date() == datetime.today().date():
                    continue

                forecast_list.append({
                    "day": day_name,
                    "temp": forecast['main']['temp'],
                    "icon": forecast['weather'][0]['icon']
                })
        
        # Nos aseguramos de tener solo los próximos 5 días
        processed_forecast = forecast_list[:5]

        # --- 4. DEVOLVER LA RESPUESTA COMBINADA ---
        return jsonify({
            'narrative': narrative,
            'forecast': processed_forecast
        })

    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404:
            return jsonify({'error': f'No se pudo encontrar la ciudad: {city}. Por favor, verifica el nombre.'}), 404
        return jsonify({'error': f'Error al obtener los datos del tiempo: {str(err)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Ha ocurrido un error inesperado: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
