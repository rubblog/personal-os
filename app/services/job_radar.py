import logging
from typing import List, Dict, Any

logger = logging.getLogger("personal_os.job_radar")

class JobRadarService:
    """
    Servicio de vigilancia para vacantes de FP Sanidad en centros privados/concertados
    y oportunidades 100% remotas.
    Filtra por:
    - Mas Camarena, CEAC Burjassot y centros a <= 15 km de El Osito.
    - Jornadas parciales (<= 20h totales) para compaginar con la base militar.
    - Ofertas 100% remotas de formación sanitaria en toda España.
    - Jornada completa para cambio laboral (preferencia concertados).
    """
    def __init__(self, job_rules: Dict[str, Any]):
        self.rules = job_rules
        self.scenarios = job_rules.get("scenarios", [])

    def scan_job_opportunities(self) -> List[Dict[str, Any]]:
        """
        Rastrea fuentes de empleo docente (APIs sindicadas y feeds de educación).
        En esta etapa proporciona el filtro estructural sobre las ofertas candidatas.
        """
        # Ofertas de muestra estructuradas para validar el filtrador
        candidate_feed = [
            {
                "title": "Profesor FP Procesos Sanitarios (Tardes)",
                "center": "Mas Camarena",
                "location": "Paterna",
                "hours_per_week": 12,
                "modality": "Presencial",
                "contract_type": "Parcial",
                "url": "https://colegiomascamarena.es/empleo"
            },
            {
                "title": "Docente FP Documentación Sanitaria (Online)",
                "center": "Instituto Superior FP",
                "location": "Remoto",
                "hours_per_week": 15,
                "modality": "100% Remoto",
                "contract_type": "Parcial / Flexible",
                "url": "https://empleofp.ejemplo.es/oferta/102"
            },
            {
                "title": "Profesor Secundaria Inglés",
                "center": "Colegio Valencia",
                "location": "Valencia",
                "hours_per_week": 25,
                "modality": "Presencial",
                "contract_type": "Completa",
                "url": "https://ejemplo.com/ingles"
            }
        ]

        matched_jobs = []
        for job in candidate_feed:
            title = job["title"].lower()
            center = job["center"].lower()
            hours = job.get("hours_per_week", 40)
            modality = job.get("modality", "")

            # Descartar si no es de Sanidad o afín
            if not any(k in title for k in ["sanitari", "salud", "biolog", "anatom", "laboratorio"]):
                continue

            # Escenario A: Presencial Parcial (Mas Camarena / CEAC / Cercanos <= 20h)
            if modality == "Presencial" and hours <= 20:
                if any(target in center for target in ["mas camarena", "ceac", "burjassot", "paterna"]):
                    matched_jobs.append({
                        "role": job["title"],
                        "center": job["center"],
                        "scenario": "Parcial presencial (compatible con base)",
                        "hours": f"{hours}h/semana",
                        "url": job["url"]
                    })
                    continue

            # Escenario B: 100% Remoto en España
            if "remoto" in modality.lower() or "online" in title:
                matched_jobs.append({
                    "role": job["title"],
                    "center": job["center"],
                    "scenario": "100% Remoto flexible",
                    "hours": f"{hours}h/semana",
                    "url": job["url"]
                })
                continue

            # Escenario C: Presencial Completa para cambio laboral
            if hours > 20 and any(loc in job["location"].lower() for loc in ["valencia", "burjassot", "camp de túria"]):
                matched_jobs.append({
                    "role": job["title"],
                    "center": job["center"],
                    "scenario": "Jornada completa (cambio laboral)",
                    "hours": f"{hours}h/semana",
                    "url": job["url"]
                })

        return matched_jobs
