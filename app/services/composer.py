from datetime import datetime
from typing import Dict, Any, List

class BriefingComposer:
    """
    Ensamblador del guión de radio en español (< 120 segundos).
    Unifica meteorología real, Google Calendar real, tráfico y alertas contrastadas.
    """
    @staticmethod
    def compose_script(
        user_name: str,
        weather_info: Dict[str, Any],
        calendar_events: List[Dict[str, Any]],
        traffic_info: str = "El trayecto hacia la base militar está fluido, unos 15 minutos habituales.",
        official_alerts: List[Dict[str, Any]] = None,
        job_alerts: List[Dict[str, Any]] = None
    ) -> str:
        dias_semana = {
            0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
            4: "viernes", 5: "sábado", 6: "domingo"
        }
        meses = {
            1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
            7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
        }

        now = datetime.now()
        dia_nombre = dias_semana[now.weekday()]
        mes_nombre = meses[now.month]
        hora_str = now.strftime("%H:%M")

        # 1. Saludo y contexto temporal
        script_parts = [
            f"Buenos días {user_name}. Hoy es {dia_nombre} {now.day} de {mes_nombre}.",
            f"Son las {hora_str} de la mañana."
        ]

        # 2. Meteorología práctica
        if weather_info and "summary" in weather_info:
            script_parts.append(weather_info["summary"])

        # 3. Tráfico hacia la Base Militar Jaime I
        script_parts.append(traffic_info)

        # 4. Agenda Real de Google Calendar
        today_events = [e for e in (calendar_events or []) if e.get("is_today")]
        upcoming_events = [e for e in (calendar_events or []) if not e.get("is_today")]

        if today_events:
            event_texts = []
            for ev in today_events:
                summary = ev.get("summary", "")
                event_texts.append(f"Para hoy tienes anotado: {summary}.")
            script_parts.append(" ".join(event_texts))
        else:
            script_parts.append("Hoy no tienes citas urgentes en tu agenda.")

        # Anticipación de compromisos próximos (próximos días: exámenes, entregas, cumpleaños)
        if upcoming_events:
            next_ev = upcoming_events[0]
            summary = next_ev.get("summary", "")
            start = next_ev.get("start", "")
            script_parts.append(f"Ten presente en el horizonte próximo: {summary}.")

        # 5. Oposiciones y Boletines Oficiales (DOGV / BOE)
        if official_alerts:
            alert_items = []
            for alert in official_alerts:
                src = alert.get("source")
                if src == "DOGV":
                    alert_items.append(f"Atención al DOGV: hay una publicación relevante sobre {alert.get('specialty', 'FP Sanidad')}.")
                elif src == "BOE":
                    alert_items.append(f"Novedad en el BOE: convocatoria para {alert.get('category', 'M2 Biología')}.")
            script_parts.append(" ".join(alert_items))
        else:
            script_parts.append("En el DOGV y el BOE no hay novedades de tus especialidades hoy.")

        # 6. Empleo Docente FP (Solo si hay alertas reales contrastadas)
        if job_alerts:
            job_items = []
            for job in job_alerts:
                job_items.append(
                    f"En empleo: vacante en {job.get('center')} para {job.get('role')} ({job.get('hours')})."
                )
            script_parts.append(" ".join(job_items))
        else:
            script_parts.append("Tampoco hay vacantes de FP que cumplan tus filtros en los centros monitoreados.")

        # 7. Cierre
        script_parts.append("¡Que tengas un excelente día!")

        return " ".join(script_parts)
