import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger("personal_os.bulletins")

class BulletinsService:
    """
    Servicio de vigilancia oficial para DOGV y BOE.
    Utiliza las APIs públicas y sumarios XML diarios sin coste de IA.
    Aplica filtros deterministas basados en el perfil de Rubén.
    """
    BOE_API_URL = "https://www.boe.es/datosabiertos/api/boe/sumario"
    DOGV_RSS_URL = "https://dogv.gva.es/es/rss"

    def __init__(self, boe_rules: Dict[str, Any], dogv_rules: Dict[str, Any]):
        self.boe_rules = boe_rules
        self.dogv_rules = dogv_rules

    def scan_boe_today(self) -> List[Dict[str, Any]]:
        """
        Escanea el sumario del BOE del día buscando:
        - Promoción Interna
        - Personal Laboral Fijo (Convenio Único AGE)
        - Grupo M2 (Biología / Investigación)
        - Provincia de Valencia
        """
        today_str = datetime.now().strftime("%Y%m%d")
        url = f"{self.BOE_API_URL}/{today_str}"
        headers = {"Accept": "application/xml"}

        matches = []
        try:
            res = requests.get(url, headers=headers, timeout=12)
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                # Buscar en la sección II-B (Oposiciones y concursos)
                for item in root.findall(".//diario/seccion[@num='2B']//item"):
                    titulo = (item.findtext("titulo") or "").lower()
                    url_pdf = item.findtext("url_pdf") or ""
                    
                    # Filtros obligatorios de perfil
                    is_m2 = "m2" in titulo or "grupo m2" in titulo
                    is_bio = "biolog" in titulo or "investigaci" in titulo or "biomedic" in titulo
                    is_promocion = "promoción interna" in titulo or "promocion interna" in titulo
                    is_laboral = "laboral" in titulo or "convenio único" in titulo
                    is_valencia = "valencia" in titulo or "valència" in titulo

                    if is_m2 and is_bio and is_promocion and is_laboral and is_valencia:
                        matches.append({
                            "source": "BOE",
                            "title": item.findtext("titulo"),
                            "url": f"https://www.boe.es{url_pdf}" if url_pdf else "https://www.boe.es",
                            "category": "M2 Biología (Promoción Interna - Valencia)"
                        })
        except Exception as e:
            logger.warning(f"No se pudo consultar el BOE del día ({e}).")

        return matches

    def scan_dogv_today(self) -> List[Dict[str, Any]]:
        """
        Escanea el DOGV buscando las 3 especialidades docentes de FP Sanidad:
        1. Procesos Sanitarios
        2. Procedimientos de Diagnóstico Clínico y Ortoprotésico
        3. Procedimientos Sanitarios y Asistenciales
        """
        target_specialties = self.dogv_rules.get("target_specialties", [])
        matches = []

        try:
            res = requests.get(self.DOGV_RSS_URL, timeout=12)
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                channel = root.find("channel")
                if channel is not None:
                    for item in channel.findall("item"):
                        title = (item.findtext("title") or "").lower()
                        desc = (item.findtext("description") or "").lower()
                        link = item.findtext("link") or "https://dogv.gva.es"

                        content = f"{title} {desc}"

                        # Comprobar si coincide con alguna de las 3 especialidades
                        for spec in target_specialties:
                            keywords = spec.get("keywords", [])
                            if any(k.lower() in content for k in keywords):
                                matches.append({
                                    "source": "DOGV",
                                    "specialty": spec.get("name"),
                                    "title": item.findtext("title"),
                                    "url": link
                                })
                                break
        except Exception as e:
            logger.warning(f"No se pudo consultar el RSS del DOGV ({e}).")

        return matches

    def scan_all_official_bulletins(self) -> List[Dict[str, Any]]:
        results = []
        results.extend(self.scan_boe_today())
        results.extend(self.scan_dogv_today())
        return results
