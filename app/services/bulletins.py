import requests
import re
import xml.etree.ElementTree as ET
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

logger = logging.getLogger("personal_os.bulletins")

class BulletinsService:
    """
    Servicio de vigilancia oficial para DOGV y BOE.
    Utiliza APIs y páginas de sumario reales.
    """
    BOE_API_URL = "https://www.boe.es/datosabiertos/api/boe/sumario"
    DOGV_SUMARIO_URL = "https://dogv.gva.es/es/sumari-dogv"

    def __init__(self, boe_rules: Dict[str, Any], dogv_rules: Dict[str, Any]):
        self.boe_rules = boe_rules
        self.dogv_rules = dogv_rules

    def scan_boe_today(self) -> List[Dict[str, Any]]:
        """
        Escanea el sumario del BOE del último día hábil buscando:
        - Promoción Interna
        - Personal Laboral Fijo (Convenio Único AGE)
        - Grupo M2 (Biología / Investigación)
        - Provincia de Valencia
        """
        # Si hoy es domingo o sábado, busca el último viernes
        now = datetime.now()
        if now.weekday() == 6: # Domingo
            target_date = now - timedelta(days=2)
        elif now.weekday() == 5: # Sábado
            target_date = now - timedelta(days=1)
        else:
            target_date = now

        date_str = target_date.strftime("%Y%m%d")
        url = f"{self.BOE_API_URL}/{date_str}"
        headers = {"Accept": "application/xml"}

        matches = []
        try:
            res = requests.get(url, headers=headers, timeout=12)
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                for seccion in root.findall(".//diario/seccion"):
                    if seccion.attrib.get("codigo") == "2B":
                        for item in seccion.findall(".//item"):
                            titulo = (item.findtext("titulo") or "").lower()
                            url_pdf = item.findtext("url_pdf") or ""

                            # Filtros obligatorios de perfil
                            is_m2 = "m2" in titulo or "grupo m2" in titulo
                            is_bio = any(k in titulo for k in ["biolog", "investigaci", "biomedic"])
                            is_promocion = "promoción interna" in titulo or "promocion interna" in titulo
                            is_valencia = "valencia" in titulo or "valència" in titulo

                            if is_m2 and is_bio and is_promocion and is_valencia:
                                matches.append({
                                    "source": "BOE",
                                    "title": item.findtext("titulo"),
                                    "url": f"https://www.boe.es{url_pdf}" if url_pdf else "https://www.boe.es",
                                    "category": "M2 Biología (Promoción Interna - Valencia)"
                                })
        except Exception as e:
            logger.warning(f"Error consultando el BOE ({e})")

        return matches

    def scan_dogv_today(self) -> List[Dict[str, Any]]:
        """
        Escanea el sumario del DOGV mediante el portal oficial buscando las 3 especialidades docentes.
        """
        target_specialties = self.dogv_rules.get("target_specialties", [])
        matches = []

        try:
            res = requests.get(self.DOGV_SUMARIO_URL, timeout=12)
            if res.status_code == 200:
                html = res.text.lower()
                for spec in target_specialties:
                    name = spec.get("name", "")
                    keywords = spec.get("keywords", [])
                    for kw in keywords:
                        if kw.lower() in html:
                            matches.append({
                                "source": "DOGV",
                                "specialty": name,
                                "title": f"Publicación detectada sobre {name}",
                                "url": self.DOGV_SUMARIO_URL
                            })
                            break
        except Exception as e:
            logger.warning(f"Error consultando DOGV ({e})")

        return matches

    def scan_all_official_bulletins(self) -> List[Dict[str, Any]]:
        results = []
        results.extend(self.scan_boe_today())
        results.extend(self.scan_dogv_today())
        return results
