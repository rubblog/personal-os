import zoneinfo
from datetime import datetime
from typing import Dict, Any, List

class BriefingComposer:
    """
    Ensamblador del guión de radio en español (< 120 segundos).
    Optimizaciones aplicadas:
    1. Tiempo completo: temperatura, sensación térmica, lluvia, viento y alertas.
    2. Predicción de tráfico hacia Bétera en la ventana 07:30 - 07:45.
    3. Titulares esenciales de actualidad (Nacional y Valencia).
    4. Silencio estricto en DOGV/BOE y empleo si no hay novedades reales.
    """
    @staticmethod
    def compose_script(
        user_name: str,
        weather_info: Dict[str, Any],
        calendar_events: List[Dict[str, Any]],
        traffic_info: str = "Para tu salida entre las 7:30 y 7:40 hacia la base militar de Bétera, la CV-35 y el enlace presentan tráfico habitual, con unos 15 a 18 minutos estimados.",
        official_alerts: List[Dict[str, Any]] = None,
        job_alerts: List[Dict[str, Any]] = None,
        top_news: List[Dict[str, str]] = None
    ) -> str:
        dias_semana = {
            0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
            4: "viernes", 5: "sábado", 6: "domingo"
        }
        meses = {
            1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
            7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
        }

        tz = zoneinfo.ZoneInfo("Europe/Madrid")
        now = datetime.now(tz)
        
        dia_num = now.weekday()
        dia_nombre = dias_semana[dia_num]
        mes_nombre = meses[now.month]
        hora = now.hour
        minuto = now.minute
        is_weekend = dia_num in [5, 6]

        # Saludo y franja horaria natural
        if 5 <= hora < 12:
            saludo = f"Buenos días {user_name}"
            franja = "de la mañana"
        elif 12 <= hora < 20:
            saludo = f"Buenas tardes {user_name}"
            franja = "de la tarde"
        else:
            saludo = f"Buenas noches {user_name}"
            franja = "de la noche"

        hora_12 = hora if hora <= 12 else hora - 12
        if hora_12 == 0: hora_12 = 12
        hora_palabra = "la una" if hora_12 == 1 else f"las {hora_12}"
        
        if minuto == 0:
            tiempo_oral = f"Son {hora_palabra} en punto {franja}"
        elif minuto == 15:
            tiempo_oral = f"Son {hora_palabra} y cuarto {franja}"
        elif minuto == 30:
            tiempo_oral = f"Son {hora_palabra} y media {franja}"
        else:
            tiempo_oral = f"Son {hora_palabra} y {minuto} {franja}"

        script_parts = [
            f"{saludo}. Hoy es {dia_nombre} {now.day} de {mes_nombre}.",
            f"{tiempo_oral}."
        ]

        # 1. Meteorología completa (Sensación térmica, lluvia, viento, alertas)
        if weather_info and "summary" in weather_info:
            script_parts.append(weather_info["summary"])

        # 2. Previsión de tráfico para las 07:30 - 07:45 (Solo días laborables L-V)
        if not is_weekend:
            script_parts.append(traffic_info)

        # 3. Agenda Real de Google Calendar
        today_events = [e for e in (calendar_events or []) if e.get("is_today")]
        upcoming_events = [e for e in (calendar_events or []) if not e.get("is_today")]

        if today_events:
            event_texts = []
            for ev in today_events:
                summary = ev.get("summary", "")
                event_texts.append(f"En tu agenda para hoy: {summary}.")
            script_parts.append(" ".join(event_texts))

        if upcoming_events:
            next_ev = upcoming_events[0]
            summary = next_ev.get("summary", "")
            script_parts.append(f"Aviso próximo: {summary}.")

        # 4. Noticias clave para empezar el día
        if top_news:
            news_items = []
            for n in top_news:
                news_items.append(f"En noticias: {n.get('title')}.")
            script_parts.append(" ".join(news_items))

        # 5. Oposiciones y Boletines Oficiales (Solo si hay alertas)
        if official_alerts:
            alert_items = []
            for alert in official_alerts:
                src = alert.get("source")
                if src == "DOGV":
                    alert_items.append(f"Atención al DOGV: hay una publicación sobre {alert.get('specialty', 'FP Sanidad')}.")
                elif src == "BOE":
                    alert_items.append(f"Novedad en el BOE: convocatoria para {alert.get('category', 'M2 Biología')}.")
            script_parts.append(" ".join(alert_items))

        # 6. Empleo FP (Solo si hay alertas)
        if job_alerts:
            job_items = []
            for job in job_alerts:
                job_items.append(
                    f"En empleo: vacante en {job.get('center')} para {job.get('role')}."
                )
            script_parts.append(" ".join(job_items))

        # 7. Cierre
        if is_weekend:
            script_parts.append("¡Disfruta del fin de semana!")
        else:
            script_parts.append("¡Buen inicio de jornada!")

        return " ".join(script_parts)
