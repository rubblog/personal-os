import os
import json
import datetime
import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger("personal_os.calendar")

class CalendarService:
    """
    Servicio de lectura para Google Calendar.
    Lee las credenciales desde token.json o desde la variable de entorno GOOGLE_TOKEN_JSON.
    """
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    def __init__(self, token_path: str = "token.json"):
        self.token_path = Path(token_path)

    def get_today_events(self) -> List[Dict[str, Any]]:
        token_info = None

        # 1. Intentar desde variable de entorno (Render Cloud)
        env_token = os.environ.get("GOOGLE_TOKEN_JSON")
        if env_token:
            try:
                token_info = json.loads(env_token)
            except Exception as e:
                logger.warning(f"No se pudo parsear GOOGLE_TOKEN_JSON: {e}")

        # 2. Intentar desde archivo local
        if not token_info and self.token_path.exists():
            try:
                with open(self.token_path, "r", encoding="utf-8") as f:
                    token_info = json.load(f)
            except Exception as e:
                logger.warning(f"No se pudo leer {self.token_path}: {e}")

        if token_info:
            try:
                from google.oauth2.credentials import Credentials
                from googleapiclient.discovery import build

                creds = Credentials.from_authorized_user_info(token_info, self.SCOPES)
                service = build('calendar', 'v3', credentials=creds)

                # Consultar próximos 7 días para no perder avisos de exámenes y entregas próximas
                now = datetime.datetime.utcnow()
                start_time = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
                end_time = (now + datetime.timedelta(days=7)).replace(hour=23, minute=59, second=59, microsecond=0).isoformat() + 'Z'

                events_result = service.events().list(
                    calendarId='primary',
                    timeMin=start_time,
                    timeMax=end_time,
                    maxResults=10,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()

                raw_events = events_result.get('items', [])
                formatted = []
                today_str = now.strftime("%Y-%m-%d")

                for item in raw_events:
                    start_data = item.get('start', {})
                    start_val = start_data.get('dateTime', start_data.get('date', ''))
                    is_today = today_str in start_val
                    
                    formatted.append({
                        "summary": item.get('summary', 'Sin título'),
                        "start": start_val,
                        "is_today": is_today,
                        "location": item.get('location', '')
                    })
                return formatted
            except Exception as e:
                logger.warning(f"Error consultando Google Calendar: {e}")

        return []
