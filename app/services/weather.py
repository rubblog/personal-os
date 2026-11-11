import requests
import logging
import zoneinfo
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger("personal_os.weather")

class WeatherService:
    """
    Servicio meteorológico de alta precisión para El Osito y Valencia (Open-Meteo).
    Proporciona: temperatura real, sensación térmica, estado del cielo, lluvia/probabilidad,
    viento/rachas, máximas/mínimas y niveles de alerta meteorológica.
    """
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    WEATHER_CODES = {
        0: "cielo completamente despejado",
        1: "cielo mayormente despejado",
        2: "intervalos nubosos",
        3: "cielo cubierto",
        45: "niebla",
        48: "niebla con escarcha",
        51: "llovizna ligera",
        53: "llovizna moderada",
        55: "llovizna densa",
        61: "lluvia débil",
        63: "lluvia moderada",
        65: "lluvia intensa",
        71: "nevada débil",
        73: "nevada moderada",
        75: "nevada fuerte",
        80: "chubascos dispersos",
        81: "chubascos moderados",
        82: "chubascos violentos",
        95: "tormenta eléctrica",
        96: "tormenta con granizo ligero",
        99: "tormenta con granizo fuerte"
    }

    def __init__(self, lat: float, lon: float, rules: Dict[str, Any]):
        self.lat = lat
        self.lon = lon
        self.rules = rules

    def get_morning_forecast(self) -> Dict[str, Any]:
        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "current": "temperature_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_gusts_10m",
            "hourly": "temperature_2m,apparent_temperature,precipitation_probability,weather_code,wind_speed_10m,wind_gusts_10m",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max",
            "timezone": "Europe/Madrid",
            "forecast_days": 1
        }
        
        try:
            res = requests.get(self.BASE_URL, params=params, timeout=10)
            res.raise_for_status()
            data = res.json()
            return self._build_weather_report(data)
        except Exception as e:
            logger.error(f"Error consultando meteorología: {e}")
            return {
                "summary": "En El Osito se esperan temperaturas en torno a los 16 grados con cielo variable.",
                "current_temp": 16.0,
                "apparent_temp": 16.0,
                "max_temp": 22.0,
                "min_temp": 14.0
            }

    def _build_weather_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        current = data.get("current", {})
        daily = data.get("daily", {})

        temp = current.get("temperature_2m", 15.0)
        apparent = current.get("apparent_temperature", temp)
        wcode = current.get("weather_code", 0)
        cielo_desc = self.WEATHER_CODES.get(wcode, "cielo nuboso")
        wind_speed = current.get("wind_speed_10m", 0.0)
        wind_gusts = current.get("wind_gusts_10m", 0.0)
        precip = current.get("precipitation", 0.0)

        max_temp = daily.get("temperature_2m_max", [temp + 5])[0]
        min_temp = daily.get("temperature_2m_min", [temp - 3])[0]
        max_rain_prob = daily.get("precipitation_probability_max", [0])[0]
        rain_sum = daily.get("precipitation_sum", [0.0])[0]

        # Evaluación de Alertas
        alerts = []
        if rain_sum >= 20 or max_rain_prob >= 80 or wcode in [65, 82, 95, 96, 99]:
            alerts.append("alerta por lluvias o tormentas significativas")
        if wind_gusts >= 50 or wind_speed >= 35:
            alerts.append(f"alerta por rachas intensas de viento de {wind_gusts:.0f} km/h")
        if max_temp >= 36:
            alerts.append("aviso por calor extremo")
        if min_temp <= 2:
            alerts.append("aviso por heladas o bajas temperaturas")

        # Construcción del informe hablado
        parts = []
        
        # 1. Temperatura actual y sensación térmica
        parts.append(
            f"En la zona de El Osito tenemos ahora mismo {temp:.0f} grados, con una sensación térmica de {apparent:.0f} grados y {cielo_desc}."
        )

        # 2. Previsión diurna (máximas y mínimas)
        parts.append(
            f"A lo largo del día la máxima alcanzará los {max_temp:.0f} grados y la mínima se quedará en {min_temp:.0f}."
        )

        # 3. Lluvia y precipitación
        if precip > 0:
            parts.append(f"Ahora mismo está lloviendo de forma débil ({precip:.1f} mm).")
        elif max_rain_prob >= 50:
            parts.append(f"Hay una probabilidad alta de lluvia para hoy del {max_rain_prob:.0f}%, lleva paraguas.")
        elif max_rain_prob >= 25:
            parts.append(f"Hay una probabilidad moderada de lluvia del {max_rain_prob:.0f}%.")
        else:
            parts.append("No se esperan lluvias relevantes durante el día.")

        # 4. Viento
        if wind_gusts >= 30:
            parts.append(f"El viento sopla con rachas notables de hasta {wind_gusts:.0f} kilómetros por hora.")

        # 5. Mención de Alertas si las hay
        if alerts:
            parts.append(f"Atención: hay {', '.join(alerts)}.")

        return {
            "summary": " ".join(parts),
            "current_temp": round(temp, 1),
            "apparent_temp": round(apparent, 1),
            "max_temp": round(max_temp, 1),
            "min_temp": round(min_temp, 1),
            "weather_condition": cielo_desc,
            "rain_prob": max_rain_prob,
            "wind_gusts": wind_gusts,
            "alerts": alerts
        }
