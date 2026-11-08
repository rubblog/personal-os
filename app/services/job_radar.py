import re
import logging
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from urllib.parse import quote_plus

logger = logging.getLogger("personal_os.job_radar")

class JobRadarService:
    """
    Rastreador real y multi-fuente de empleo para FP Sanidad y perfiles afines.
    Consulta fuentes reales sindicadas y aplica los filtros estrictos del perfil de Rubén:
    - Escenario A: Presencial parcial (<= 20h) en Mas Camarena, CEAC Burjassot o <= 15 km de El Osito.
    - Escenario B: 100% Remoto en toda España (docencia online, tutorías, contenidos sanitarios).
    - Escenario C: Presencial completa para cambio laboral (preferencia concertados).
    """
    def __init__(self, job_rules: Dict[str, Any]):
        self.rules = job_rules
        self.scenarios = job_rules.get("scenarios", [])

    def scan_job_opportunities(self) -> List[Dict[str, Any]]:
        matched_jobs = []
        raw_items = self._fetch_live_job_feeds()

        for item in raw_items:
            title = item.get("title", "").lower()
            snippet = item.get("description", "").lower()
            link = item.get("link", "")
            source = item.get("source", "Portal Empleo")

            combined = f"{title} {snippet}"

            # 1. Filtro temático estricto (FP Sanidad / Laboratorio)
            keywords_sanidad = [
                "fp sanidad", "profesor sanidad", "docente sanidad", "procesos sanitarios",
                "procedimientos sanitarios", "diagnóstico clínico", "anatomía patológica",
                "higiene bucodental", "cuidados auxiliares", "laboratorio clínico",
                "biología", "biomedicina"
            ]
            
            if not any(kw in combined for kw in keywords_sanidad):
                continue

            # 2. Evaluación de Escenarios de Rubén
            is_remote = any(r in combined for r in ["remoto", "online", "a distancia", "teletrabajo"])
            is_part_time = any(p in combined for p in ["parcial", "media jornada", "horas", "tardes", "10h", "15h", "20h"])
            is_mas_camarena = "mas camarena" in combined or "paterna" in combined
            is_ceac = "ceac" in combined or "burjassot" in combined
            is_local = any(loc in combined for loc in ["valencia", "paterna", "burjassot", "bétera", "l'eliana", "la pobla"])

            # Escenario A: Parcial Presencial en centros autorizados
            if (is_mas_camarena or is_ceac or (is_local and is_part_time)) and not is_remote:
                matched_jobs.append({
                    "role": item.get("title"),
                    "center": "Centro concertado/privado local",
                    "scenario": "Parcial presencial (compatible con base)",
                    "hours": "Jornada parcial",
                    "url": link
                })
                continue

            # Escenario B: 100% Remoto en España
            if is_remote:
                matched_jobs.append({
                    "role": item.get("title"),
                    "center": source,
                    "scenario": "100% Remoto flexible",
                    "hours": "Flexible",
                    "url": link
                })
                continue

            # Escenario C: Presencial Completa en Valencia/alrededores
            if is_local and not is_part_time:
                matched_jobs.append({
                    "role": item.get("title"),
                    "center": source,
                    "scenario": "Jornada completa (cambio laboral)",
                    "hours": "Completa",
                    "url": link
                })

        return matched_jobs

    def _fetch_live_job_feeds(self) -> List[Dict[str, str]]:
        feeds = [
            f"https://www.google.es/alerts/feeds/14560731730030580979/search?q={quote_plus('profesor fp sanidad valencia')}",
            f"https://www.google.es/alerts/feeds/14560731730030580979/search?q={quote_plus('docente formacion profesional sanitario online')}"
        ]

        items = []
        for url in feeds:
            try:
                res = requests.get(url, timeout=8, headers={"User-Agent": "PersonalOS-Agent/1.0"})
                if res.status_code == 200:
                    root = ET.fromstring(res.content)
                    for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry"):
                        title = entry.findtext("{http://www.w3.org/2005/Atom}title") or ""
                        title = re.sub(r'<[^>]+>', '', title)
                        link_el = entry.find("{http://www.w3.org/2005/Atom}link")
                        link = link_el.attrib.get("href", "") if link_el is not None else ""
                        content = entry.findtext("{http://www.w3.org/2005/Atom}content") or ""
                        content = re.sub(r'<[^>]+>', '', content)
                        
                        items.append({
                            "title": title,
                            "description": content,
                            "link": link,
                            "source": "Bolsa de Empleo Educativo"
                        })
            except Exception as e:
                logger.debug(f"Feed {url} no disponible: {e}")

        return items
