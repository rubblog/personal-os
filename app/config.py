import json
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Dict, Any

logger = logging.getLogger("personal_os.config")

class Settings(BaseModel):
    profile_path: Path = Path("user_profile.json")
    briefing_hour: int = 6
    briefing_minute: int = 15
    timezone: str = "Europe/Madrid"

    def load_profile(self) -> Dict[str, Any]:
        if not self.profile_path.exists():
            raise FileNotFoundError(f"Config profile not found at {self.profile_path.resolve()}")
        with open(self.profile_path, "r", encoding="utf-8") as f:
            return json.load(f)

settings = Settings()
