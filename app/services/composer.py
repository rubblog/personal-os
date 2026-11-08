from datetime import datetime
from typing import Dict, Any, List

class BriefingComposer:
    """
    Ensamblador del guión de radio en español (< 120 segundos).
    Aplica las reglas de máxima concisión:
    1. Si no hay publicaciones en BOE/DOGV -> No dice nada.
    2. Si no hay ofertas de empleo en FP -> No dice nada.
    3. Fines de semana (sábado/domingo) -> No menciona el tráfico hacia el trabajo.
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
        dia_num = now.weekday()
        dia_nombre = dias_semana[dia_num]
        mes_nombre = meses[now.month]
        hora_str = now.strftime("%H:%M")
        is_weekend = dia_num in [5, 6] # Sábado o Domingo

        # 1. Saludo y contexto temporal
        script_parts = [
            f"Buenos días {user_name}. Hoy es {dia_nombre} {now.day} de {mes_nombre}.",
            f"Son las {hora_str} de la mañana."
        ]

        # 2. Meteorología práctica (El Osito y perros)
        if weather_info and "summary" in weather_info:
            script_parts.append(weather_info["summary"])

        # 3. Tráfico laboral (Solo en días laborables de lunes a viernes)
        if not is_weekend:
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
            if not is_weekend:
                script_parts.append("Hoy no tienes citas urgentes en tu agenda.")

        # Próximos compromisos (exámenes, entregas de universidad, etc.)
        if upcoming_events:
            next_ev = upcoming_events[0]
            summary = next_ev.get("summary", "")
            script_parts.append(f"Ten presente en el horizonte próximo: {summary}.")

        # 5. Oposiciones y Boletines Oficiales (DOGV / BOE)
        # REGLA: Si NO hay novedades, silencio total (no dice nada).
        if official_alerts:
            alert_items = []
            for alert in official_alerts:
                src = alert.get("source")
                if src == "DOGV":
                    alert_items.append(f"Atención al DOGV: hay una publicación sobre {alert.get('specialty', 'FP Sanidad')}.")
                elif src == "BOE":
                    alert_items.append(f"Novedad en el BOE: convocatoria para {alert.get('category', 'M2 Biología')}.")
            script_parts.append(" ".join(alert_items))

        # 6. Empleo Docente FP
        # REGLA: Si NO hay vacantes, silencio total (no dice nada).
        if job_alerts:
            job_items = []
            for job in job_alerts:
                job_items.append(
                    f"En empleo: vacante en {job.get('center')} para {job.get('role')} ({job.get('hours')})."
                )
            script_parts.append(" ".join(job_items))

        # 7. Cierre
        if is_weekend:
            script_parts.append("¡Disfruta del fin de semana!")
        else:
            script_parts.append("¡Que tengas un excelente día!")

        return " ".join(script_parts)
