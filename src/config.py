import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA = PROJECT_ROOT / "data" / "processed"
NOTEBOOKS = PROJECT_ROOT / "notebooks"
OUTPUTS = PROJECT_ROOT / "outputs"
FIGURES = OUTPUTS / "figures"
TABLES = OUTPUTS / "tables"

for d in [RAW_DATA, PROCESSED_DATA, FIGURES, TABLES]:
    d.mkdir(parents=True, exist_ok=True)

LIMA_BBOX = (-77.20, -12.30, -76.80, -11.90)
LIMA_CENTER = (-77.03, -12.04)
CRS_PROJECTED = "EPSG:32718"
CRS_GEOGRAPHIC = "EPSG:4326"
BUFFER_METERS = 800

RANDOM_STATE = 42
