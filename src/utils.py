# utils for autoRed

"""Utility functions for the autoRed project.
Provides small helpers for path handling and environment loading.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def load_env():
    """Load .env file from the project root if it exists."""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)

def ensure_dir(path: Path):
    """Create directory if it does not exist."""
    path.mkdir(parents=True, exist_ok=True)
    return path
