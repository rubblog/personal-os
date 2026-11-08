from datetime import datetime
from typing import Dict, Any, List

class BriefingComposer:
    """
    Ensamblador del guión de radio en español (< 120 segundos).
    Unifica meteorología, agenda, tráfico, oposiciones (DOGV/BOE) y empleo FP.
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

        # 2. Meteorología práctica (El Osito y perros)
        if weather_info and "summary" in weather_info:
            script_parts.append(weather_info["summary"])

        # 3. Tráfico hacia la Base Militar Jaime I
        script_parts.append(traffic_info)

        # 4. Agenda y compromisos
        if calendar_events:
            event_descriptions = []
            for ev in calendar_events:
                summary = ev.get("summary", "")
                start = ev.get("start", "")
                if "16:00" in start or "Hospital" in summary or "médico" in summary.lower():
                    event_descriptions.append(f"Esta tarde tienes {summary.lower()} a las cuatro.")
                elif "trabajo" in summary.lower() or "universidad" in summary.lower():
                    event_descriptions.append(f"Recuerda revisar la entrega pendiente: {summary.lower()}.")
                else:
                    event_descriptions.append(f"Tienes programado: {summary}.")

            script_parts.append(" ".join(event_descriptions))
        else:
            script_parts.append("No tienes compromisos urgentes en tu calendario hoy.")

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

        # 6. Radar de Empleo Privado / Remoto FP
        if job_alerts:
            job_items = []
            for job in job_alerts:
                job_items.append(
                    f"En empleo: vacante en {job.get('center')} para {job.get('role')} ({job.get('hours')})."
                )
            script_parts.append(" ".join(job_items))

        # 7. Cierre
        script_parts.append("¡Que tengas un excelente día!")

        return " ".join(script_parts)
