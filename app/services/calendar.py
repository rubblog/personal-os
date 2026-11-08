import os
import datetime
import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger("personal_os.calendar")

class CalendarService:
    """
    Servicio de lectura para Google Calendar.
    En desarrollo/sin credenciales genera datos mock coherentes o lee de cache.
    Con credenciales oficiales (token.json/credentials.json) conecta con la API de Google.
    """
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    def __init__(self, credentials_path: str = "credentials.json", token_path: str = "token.json"):
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)

    def get_today_events(self) -> List[Dict[str, Any]]:
        if self.token_path.exists():
            try:
                from google.oauth2.credentials import Credentials
                from googleapiclient.discovery import build

                creds = Credentials.from_authorized_user_file(str(self.token_path), self.SCOPES)
                service = build('calendar', 'v3', credentials=creds)

                now = datetime.datetime.utcnow()
                start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
                end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=0).isoformat() + 'Z'

                events_result = service.events().list(
                    calendarId='primary',
                    timeMin=start_of_day,
                    timeMax=end_of_day,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                
                raw_events = events_result.get('items', [])
                formatted = []
                for item in raw_events:
                    start = item['start'].get('dateTime', item['start'].get('date'))
                    formatted.append({
                        "summary": item.get('summary', 'Sin título'),
                        "start": start,
                        "location": item.get('location', '')
                    })
                return formatted
            except Exception as e:
                logger.warning(f"Error conectando con Google Calendar API: {e}. Usando fallback.")

        # Fallback estructurado de prueba para desarrollo y verificación inicial
        return [
            {
                "summary": "Cita médica en Hospital La Fe",
                "start": "16:00",
                "location": "Hospital La Fe, Valencia"
            },
            {
                "summary": "Entrega trabajo universitario",
                "start": "23:59",
                "location": ""
            }
        ]
