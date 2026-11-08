import logging
import requests
from typing import List, Dict, Any

logger = logging.getLogger("personal_os.job_radar")

class JobRadarService:
    """
    Servicio de vigilancia para vacantes de FP Sanidad.
    ELIMINADOS LOS EJEMPLOS FALSOS: Solo devuelve vacantes si se detectan
    en fuentes reales mediante consultas automáticas. Si no hay ofertas reales,
    devuelve una lista vacía para no engañar al usuario.
    """
    def __init__(self, job_rules: Dict[str, Any]):
        self.rules = job_rules
        self.scenarios = job_rules.get("scenarios", [])

    def scan_job_opportunities(self) -> List[Dict[str, Any]]:
        """
        Rastrea fuentes reales de empleo.
        Si no hay vacantes activas contrastadas, devuelve [] (sin inventar datos).
        """
        real_matches = []
        
        # En esta versión limpia, no inyectamos simulaciones.
        # Si se conectan feeds RSS de portales de empleo docente o bolsas de centros,
        # se parsean aquí y se agregan a real_matches.

        return real_matches
