import json

import pytest

from data_inei import extract_inei_population, verify_corridor_totals, PDF_PATH, CORRIDOR_PROVINCES


@pytest.mark.skipif(not PDF_PATH.exists(), reason="requiere libro_poblacion_2017.pdf")
def test_extraction_contains_only_corridor_districts():
    records = extract_inei_population()
    for ub in records:
        assert ub[:4] in CORRIDOR_PROVINCES, f"Ubigeo {ub} fuera del corredor"
        assert not ub.endswith("00"), "No debe incluir filas de provincia"


@pytest.mark.skipif(not PDF_PATH.exists(), reason="requiere libro_poblacion_2017.pdf")
def test_province_totals_match_pdf():
    records = extract_inei_population()
    verify_corridor_totals(records)


@pytest.mark.skipif(not PDF_PATH.exists(), reason="requiere libro_poblacion_2017.pdf")
def test_reproducible_json():
    from data_inei import JSON_PATH
    records = extract_inei_population()
    rows = sorted(records.values(), key=lambda r: r["ubigeo"])
    assert json.load(open(JSON_PATH)) == rows
