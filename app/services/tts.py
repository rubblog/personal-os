import os
import edge_tts
import logging
from pathlib import Path

logger = logging.getLogger("personal_os.tts")

class TTSService:
    """
    Generador de audio neuronal mediante edge-tts (100% gratuito y de alta naturalidad).
    Voz por defecto: es-ES-AlvaroNeural (masculina, clara y profesional) o es-ES-ElviraNeural.
    """
    def __init__(self, voice: str = "es-ES-AlvaroNeural", output_dir: str = "static/audio"):
        self.voice = voice
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def generate_audio_file(self, text: str, filename: str = "daily_briefing.mp3") -> Path:
        output_path = self.output_dir / filename
        
        # Eliminar archivo previo de hace más de 24h para mantener cero basura
        if output_path.exists():
            try:
                output_path.unlink()
            except Exception as e:
                logger.warning(f"No se pudo limpiar archivo antiguo: {e}")

        logger.info(f"Sintetizando voz neuronal ({self.voice}) para el parte diario...")
        communicate = edge_tts.Communicate(text, self.voice, rate="+0%")
        await communicate.save(str(output_path))
        logger.info(f"Audio generado con éxito en: {output_path}")
        return output_path
