from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = PROJECT_ROOT / "raw"
LOG_DIR = PROJECT_ROOT / "log"
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
ENV_FILE = PROJECT_ROOT / ".env"

# Monthly factor library. Code lives in factor/ (committed); generated factor
# data lives under data/factor/ (gitignored via /data/*). See update_factors.py.
FACTOR_CODE_DIR = PROJECT_ROOT / "factor"
FACTOR_CATALOG_FILE = FACTOR_CODE_DIR / "factor_catalog.csv"
FACTOR_DATA_DIR = DATA_DIR / "factor"
FACTOR_UNIVERSE_DIR = FACTOR_DATA_DIR / "universe"
FACTOR_RAW_DIR = FACTOR_DATA_DIR / "raw"
FACTOR_EXPOSURE_DIR = FACTOR_DATA_DIR / "exposure"
FACTOR_COMPOSITE_DIR = FACTOR_DATA_DIR / "composite"
FACTOR_DIAGNOSTICS_DIR = FACTOR_DATA_DIR / "diagnostics"
FACTOR_MANIFEST_DIR = FACTOR_DATA_DIR / "manifest"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
for _factor_dir in (
    FACTOR_DATA_DIR,
    FACTOR_UNIVERSE_DIR,
    FACTOR_RAW_DIR,
    FACTOR_EXPOSURE_DIR,
    FACTOR_COMPOSITE_DIR,
    FACTOR_DIAGNOSTICS_DIR,
    FACTOR_MANIFEST_DIR,
):
    _factor_dir.mkdir(parents=True, exist_ok=True)
