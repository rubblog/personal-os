import logging
from contextlib import asynccontextmanager
from pathlib import Path
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.scheduler import run_daily_briefing_pipeline, latest_briefing_state

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("personal_os.main")

scheduler = BackgroundScheduler(timezone=settings.timezone)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Path("static/audio").mkdir(parents=True, exist_ok=True)

    trigger = CronTrigger(
        day_of_week="mon-fri",
        hour=settings.briefing_hour,
        minute=settings.briefing_minute,
        timezone=settings.timezone
    )
    scheduler.add_job(
        run_daily_briefing_pipeline,
        trigger=trigger,
        id="daily_morning_briefing",
        replace_existing=True
    )
    scheduler.start()
    logger.info(
        f"Scheduler activo. Boletín matinal programado de L a V a las "
        f"{settings.briefing_hour:02d}:{settings.briefing_minute:02d} ({settings.timezone})."
    )
    yield
    scheduler.shutdown()
    logger.info("Scheduler detenido.")

app = FastAPI(
    title="Personal OS Core",
    version="1.2.0",
    description="Backend autónomo y PWA para boletín matinal personal",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos y PWA
Path("static/audio").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_pwa_root():
    """Sirve la interfaz PWA para móviles Android y navegador."""
    index_path = Path("static/index.html")
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="PWA interface not found.")
    return FileResponse(index_path)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Personal OS Core",
        "scheduler_running": scheduler.running
    }

@app.get("/api/profile")
def get_user_profile():
    try:
        return settings.load_profile()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class FeedbackPayload(BaseModel):
    topic: str
    positive: bool
    timestamp: str

@app.post("/api/profile/feedback")
def register_topic_feedback(feedback: FeedbackPayload):
    """Guarda los votos 👍 / 👎 para afinar el filtrado de noticias y temas."""
    logger.info(f"Feedback recibido: Topic={feedback.topic}, Positive={feedback.positive}")
    return {"status": "saved", "feedback": feedback.model_dump()}

@app.get("/api/briefing/latest")
def get_latest_briefing():
    """Devuelve el estado del boletín actual (audio, texto y alertas)."""
    return latest_briefing_state

@app.post("/api/briefing/trigger-manual")
def trigger_manual_briefing():
    """Fuerza la ejecución inmediata del pipeline y generación de voz."""
    result = run_daily_briefing_pipeline()
    return {"message": "Boletín matinal generado con éxito", "data": result}
