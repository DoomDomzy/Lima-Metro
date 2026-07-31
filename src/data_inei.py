import json
import re
import subprocess
from pathlib import Path

from config import RAW_DATA

PDF_PATH = RAW_DATA / "libro_poblacion_2017.pdf"
JSON_PATH = RAW_DATA / "poblacion_distrital_2017.json"

CORRIDOR_DEPARTMENTS = {"15", "07", "11"}
CORRIDOR_PROVINCES = {"0701", "1501", "1505", "1506", "1508", "1101", "1102"}
PROVINCE_TOTALS = {
    "1506": 197963, "1508": 243597, "1505": 252253, "1501": 9162322,
    "1101": 407286, "1102": 240884, "0701": 1046953,
}

_LINE = re.compile(r"^(\d{6})\s+([A-Z0-9ÁÉÍÓÚÑÜ\.\(\) /]+?)\s+([\d ]+)\s*$")


def _pdf_text():
    if not PDF_PATH.exists():
        raise FileNotFoundError(
            f"{PDF_PATH} no existe. Descárguelo del anexo 'Población total por "
            "ubigeo' del Censo INEI 2017 y colóquelo en data/raw/."
        )
    return subprocess.run(
        ["pdftotext", "-layout", str(PDF_PATH), "-"],
        capture_output=True, text=True, check=True,
    ).stdout


def extract_inei_population(text=None):
    text = text or _pdf_text()
    records = {}
    for line in text.splitlines():
        m = _LINE.match(line)
        if not m:
            continue
        ubigeo = m.group(1)
        if ubigeo[:4] not in CORRIDOR_PROVINCES or ubigeo.endswith("00"):
            continue
        name = " ".join(m.group(2).split())
        num_cols = [c for c in re.split(r"\s{2,}", m.group(3).strip()) if c]
        if not num_cols:
            continue
        total = int(num_cols[-1].replace(" ", ""))
        first = num_cols[0].replace(" ", "")
        censada = int(first) if first.isdigit() else total
        records[ubigeo] = {"ubigeo": ubigeo, "name": name,
                           "censada": censada, "total": total}
    return records


def verify_corridor_totals(records):
    prov = {}
    for ub, r in records.items():
        prov.setdefault(ub[:4], 0)
        prov[ub[:4]] += r["total"]
    mismatches = []
    for pfx, expected in PROVINCE_TOTALS.items():
        actual = prov.get(pfx, 0)
        if abs(actual - expected) > 1000:
            mismatches.append((pfx, actual, expected))
    if mismatches:
        raise ValueError(
            "Totales por provincia no coinciden con la fuente: "
            f"{[(p, a, e) for p, a, e in mismatches]}"
        )
    return prov


def build_population_json():
    records = extract_inei_population()
    verify_corridor_totals(records)
    rows = sorted(records.values(), key=lambda r: r["ubigeo"])
    with open(JSON_PATH, "w") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"Escrito {JSON_PATH}: {len(rows)} distritos del corredor Lima–Ica")
    return rows


if __name__ == "__main__":
    build_population_json()
