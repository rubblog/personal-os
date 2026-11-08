import requests
import logging
import zoneinfo
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger("personal_os.weather")

class WeatherService:
    """
    Servicio de previsión meteorológica real y horaria usando Open-Meteo para El Osito.
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
            "current": "temperature_2m,precipitation,wind_speed_10m",
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
            logger.error(f"Error consultando meteorología Open-Meteo: {e}")
            return {
                "summary": "En El Osito se esperan temperaturas moderadas para hoy.",
                "coat_needed": False,
                "umbrella_needed": False,
                "wind_alert": False
            }

    def _analyze_practical_rules(self, data: Dict[str, Any]) -> Dict[str, Any]:
        tz = zoneinfo.ZoneInfo("Europe/Madrid")
        now = datetime.now(tz)
        current_hour = now.hour

        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        rain_probs = hourly.get("precipitation_probability", [])
        winds = hourly.get("wind_speed_10m", [])

        # Buscar la temperatura actual o de la hora actual
        current_temp = None
        current_rain = 0
        for i, t in enumerate(times):
            if f"T{current_hour:02d}:00" in t:
                current_temp = temps[i]
                current_rain = rain_probs[i]
                break

        if current_temp is None:
            current_temp = data.get("current", {}).get("temperature_2m", 15.0)

        max_daily_temp = max(temps) if temps else 20.0
        max_daily_rain = max(rain_probs) if rain_probs else 0
        max_wind = max(winds) if winds else 10.0

        coat_threshold = self.rules.get("morning_walk_dog", {}).get("coat_threshold_celsius", 14)
        wind_threshold = self.rules.get("wind_alert_kmh", 40)

        coat_needed = current_temp < coat_threshold
        umbrella_needed = max_daily_rain >= 40
        temp_delta = max_daily_temp - current_temp
        significant_delta = temp_delta >= 7 and current_hour < 12
        wind_alert = max_wind >= wind_threshold

        recommendation_parts = []
        if coat_needed:
            if significant_delta:
                recommendation_parts.append(
                    f"Ahora hace fresco en El Osito ({current_temp:.0f}°C); lleva chaqueta para sacar a los perros, "
                    f"pero subirá hasta los {max_daily_temp:.0f}°C a lo largo del día."
                )
            else:
                recommendation_parts.append(
                    f"La temperatura en El Osito es fresca ({current_temp:.0f}°C); conviene llevar chaqueta."
                )
        else:
            recommendation_parts.append(f"La temperatura en El Osito es templada y agradable ({current_temp:.0f}°C).")

        if umbrella_needed:
            recommendation_parts.append("Hay previsión de lluvia durante la jornada; no olvides el paraguas.")
        
        if wind_alert:
            recommendation_parts.append(f"Atención a las rachas de viento de hasta {max_wind:.0f} km por hora.")

        return {
            "summary": " ".join(recommendation_parts),
            "current_temp": round(current_temp, 1),
            "max_temp": round(max_daily_temp, 1),
            "coat_needed": coat_needed,
            "umbrella_needed": umbrella_needed,
            "wind_alert": wind_alert
        }
