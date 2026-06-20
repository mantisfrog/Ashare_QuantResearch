from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = PROJECT_ROOT / "raw"
LOG_DIR = PROJECT_ROOT / "log"
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
ENV_FILE = PROJECT_ROOT / ".env"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
