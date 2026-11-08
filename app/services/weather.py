import requests
import logging
from typing import Dict, Any

logger = logging.getLogger("personal_os.weather")

class WeatherService:
    """
    Servicio de previsión meteorológica práctica usando Open-Meteo (Gratuito, sin API key).
    Aplica las reglas específicas para El Osito y los paseos caninos.
    """
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, lat: float, lon: float, rules: Dict[str, Any]):
        self.lat = lat
        self.lon = lon
        self.rules = rules

    def get_morning_forecast(self) -> Dict[str, Any]:
        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "hourly": "temperature_2m,precipitation_probability,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "Europe/Madrid",
            "forecast_days": 1
        }
        
        try:
            res = requests.get(self.BASE_URL, params=params, timeout=10)
            res.raise_for_status()
            data = res.json()
            return self._analyze_practical_rules(data)
        except Exception as e:
            logger.error(f"Error consultando meteorología: {e}")
            return {
                "summary": "No se pudo actualizar la previsión del tiempo.",
                "coat_needed": False,
                "umbrella_needed": False,
                "wind_alert": False
            }

    def _analyze_practical_rules(self, data: Dict[str, Any]) -> Dict[str, Any]:
        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        rain_probs = hourly.get("precipitation_probability", [])
        winds = hourly.get("wind_speed_10m", [])

        # Filtrar valores para ventana matinal (07:00 a 08:30)
        morning_temps = []
        morning_rain = []
        for i, t in enumerate(times):
            if "T07:00" in t or "T08:00" in t:
                morning_temps.append(temps[i])
                morning_rain.append(rain_probs[i])

        avg_morning_temp = sum(morning_temps) / len(morning_temps) if morning_temps else 15.0
        max_morning_rain = max(morning_rain) if morning_rain else 0
        max_daily_temp = max(temps) if temps else 20.0
        max_wind = max(winds) if winds else 10.0

        coat_threshold = self.rules.get("morning_walk_dog", {}).get("coat_threshold_celsius", 14)
        rain_threshold = self.rules.get("morning_walk_dog", {}).get("rain_probability_alert", 30)
        delta_threshold = self.rules.get("daytime_evolution", {}).get("delta_alert_celsius", 8)
        wind_threshold = self.rules.get("wind_alert_kmh", 40)

        coat_needed = avg_morning_temp < coat_threshold
        umbrella_needed = max_morning_rain >= rain_threshold or max(rain_probs) >= 40
        temp_delta = max_daily_temp - avg_morning_temp
        significant_delta = temp_delta >= delta_threshold
        wind_alert = max_wind >= wind_threshold

        # Redacción de la recomendación práctica
        recommendation_parts = []
        if coat_needed:
            if significant_delta:
                recommendation_parts.append(
                    f"Ahora hace fresco ({avg_morning_temp:.0f}°C); lleva chaqueta para sacar a los perros, "
                    f"pero subirá hasta los {max_daily_temp:.0f}°C, así que no te abrigues en exceso el resto del día."
                )
            else:
                recommendation_parts.append(
                    f"Hace frío ({avg_morning_temp:.0f}°C); ponte chaqueta para la mañana."
                )
        else:
            recommendation_parts.append(f"Temperatura matinal agradable ({avg_morning_temp:.0f}°C).")

        if umbrella_needed:
            recommendation_parts.append("Hay previsión de lluvia; no olvides el paraguas.")
        
        if wind_alert:
            recommendation_parts.append(f"Atención a las rachas de viento ({max_wind:.0f} km/h).")

        return {
            "summary": " ".join(recommendation_parts),
            "morning_temp": round(avg_morning_temp, 1),
            "max_temp": round(max_daily_temp, 1),
            "coat_needed": coat_needed,
            "umbrella_needed": umbrella_needed,
            "wind_alert": wind_alert
        }
