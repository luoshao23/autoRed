# Settings for autoRed project

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if present
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# Google Cloud API key for Gemini and Imagen
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
print(GOOGLE_API_KEY)

# Model selections (default values)
TEXT_MODEL_NAME = os.getenv("TEXT_MODEL_NAME", "gemini-2.5-flash")
IMAGE_MODEL_NAME = os.getenv("IMAGE_MODEL_NAME", "imagen-4.0-generate-001")

# Scheduler configuration (24h format, e.g., "09:00")
SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "09:00")
