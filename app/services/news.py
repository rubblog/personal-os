import logging
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

logger = logging.getLogger("personal_os.news")

class NewsService:
    """
    Servicio de noticias matinales de máxima relevancia.
    Extrae los titulares esenciales de España y de la Comunidad Valenciana
    para empezar el día informado sin ruido.
    """
    FEEDS = [
        {"name": "Nacional", "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"},
        {"name": "Valencia", "url": "https://e00-elmundo.uecdn.es/elmundo/rss/valencia.xml"}
    ]

    @classmethod
    def get_top_news(cls, max_items: int = 2) -> List[Dict[str, str]]:
        top_news = []
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PersonalOS/1.0"}

        for feed in cls.FEEDS:
            try:
                res = requests.get(feed["url"], headers=headers, timeout=6)
                if res.status_code == 200:
                    root = ET.fromstring(res.content)
                    items = root.findall(".//item")
                    for item in items:
                        title = item.findtext("title") or ""
                        link = item.findtext("link") or ""
                        title_clean = title.strip()
                        
                        # Evitar titulares vacíos o publicidad
                        if len(title_clean) > 15 and not any(k in title_clean.lower() for k in ["horóscopo", "lotería", "directo"]):
                            top_news.append({
                                "source": feed["name"],
                                "title": title_clean,
                                "url": link
                            })
                            break # Tomar el titular #1 de mayor peso de esta fuente
            except Exception as e:
                logger.warning(f"Error consultando feed de noticias {feed['name']}: {e}")

        return top_news[:max_items]
