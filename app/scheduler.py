import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from app.config import settings
from app.services.weather import WeatherService
from app.services.calendar import CalendarService
from app.services.bulletins import BulletinsService
from app.services.job_radar import JobRadarService
from app.services.news import NewsService
from app.services.tts import TTSService
from app.services.composer import BriefingComposer

logger = logging.getLogger("personal_os.scheduler")

latest_briefing_state: Dict[str, Any] = {
    "generated_at": None,
    "script_text": "Aún no se ha generado ningún boletín matinal.",
    "audio_url": None,
    "weather": None,
    "events": [],
    "official_alerts": [],
    "job_alerts": [],
    "top_news": []
}

async def execute_briefing_generation():
    """Ejecuta el pipeline completo a las 07:00 AM: Datos -> Clima -> Tráfico 07:30 -> Noticias -> Audio."""
    now = datetime.now()
    logger.info(f"Iniciando pipeline integral a las {now.strftime('%H:%M:%S')}...")

    profile = settings.load_profile()
    user_name = profile.get("user", {}).get("name", "Rubén")
    geo = profile.get("geography", {})
    home_lat = geo.get("home_base", {}).get("latitude", 39.5768)
    home_lon = geo.get("home_base", {}).get("longitude", -0.5283)

    modules_cfg = profile.get("modules", {})
    weather_rules = modules_cfg.get("weather", {}).get("practical_rules", {})
    boe_rules = modules_cfg.get("official_bulletins", {}).get("boe", {})
    dogv_rules = modules_cfg.get("official_bulletins", {}).get("dogv", {})
    job_rules = modules_cfg.get("job_radar", {})

    # 1. Clima de Alta Precisión (El Osito: Temp, Sensación térmica, Lluvia, Viento, Alertas)
    weather_svc = WeatherService(lat=home_lat, lon=home_lon, rules=weather_rules)
    weather_data = weather_svc.get_morning_forecast()

    # 2. Agenda Google Calendar
    cal_svc = CalendarService()
    calendar_events = cal_svc.get_today_events()

    # 3. Radar de Boletines Oficiales (BOE / DOGV)
    bulletins_svc = BulletinsService(boe_rules=boe_rules, dogv_rules=dogv_rules)
    official_alerts = bulletins_svc.scan_all_official_bulletins()

    # 4. Radar de Empleo FP
    job_svc = JobRadarService(job_rules=job_rules)
    job_alerts = job_svc.scan_job_opportunities()

    # 5. Noticias más relevantes del día (Nacional y Valencia)
    top_news = NewsService.get_top_news(max_items=2)

    # 6. Composición del Guión
    script = BriefingComposer.compose_script(
        user_name=user_name,
        weather_info=weather_data,
        calendar_events=calendar_events,
        official_alerts=official_alerts,
        job_alerts=job_alerts,
        top_news=top_news
    )

    # 7. Síntesis de Audio Neuronal TTS
    tts_svc = TTSService()
    audio_path = await tts_svc.generate_audio_file(script)

    # 8. Estado para la PWA
    latest_briefing_state.update({
        "generated_at": now.isoformat(),
        "script_text": script,
        "audio_url": f"/static/audio/{audio_path.name}",
        "weather": weather_data,
        "events": calendar_events,
        "official_alerts": official_alerts,
        "job_alerts": job_alerts,
        "top_news": top_news
    })

    logger.info("Pipeline matinal finalizado con éxito.")
    return latest_briefing_state

def run_daily_briefing_pipeline():
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(execute_briefing_generation())
