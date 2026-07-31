import pytest

from zones import ZONES, build_zones_gdf, load_inei_population

CORRIDOR_DEPARTMENTS = {"15", "07", "11"}


def _all_declared():
    return [ub for z in ZONES for ub in z["ubigeos"]]


def test_all_declared_ubigeos_exist_in_inei():
    pop = load_inei_population()
    assert pop is not None, "Datos INEI requeridos"
    declared = set(_all_declared())
    assert declared <= set(pop.keys()), (
        f"Ubigeos sin fuente INEI: {sorted(declared - set(pop.keys()))}"
    )


def test_ica_zone_uses_ica_province_not_piura():
    z27 = next(z for z in ZONES if z["zone_id"] == "Z27")
    assert all(ub.startswith("1101") for ub in z27["ubigeos"])
    assert all(not ub.startswith("2001") for ub in z27["ubigeos"]), (
        "Piura (2001) no pertenece al corredor Lima-Ica"
    )


def test_huaral_huaura_and_chincha_provinces_included():
    z25 = next(z for z in ZONES if z["zone_id"] == "Z25")
    z26 = next(z for z in ZONES if z["zone_id"] == "Z26")
    assert any(ub.startswith("1506") for ub in z25["ubigeos"]), "Provincia de Huaral (1506) ausente"
    assert any(ub.startswith("1508") for ub in z25["ubigeos"]), "Provincia de Huaura (1508) ausente"
    assert any(ub.startswith("1102") for ub in z26["ubigeos"]), "Provincia de Chincha (1102) ausente"


def test_no_off_corridor_departments():
    for z in ZONES:
        for ub in z["ubigeos"]:
            assert ub[:2] in CORRIDOR_DEPARTMENTS, (
                f"Ubigeo {ub} de {z['zone_id']} fuera del corredor (dept. {ub[:2]})"
            )


def test_zone_populations_match_pdf_inei_2017_totals():
    gdf = build_zones_gdf()

    z25 = gdf[gdf["zone_id"] == "Z25"]["population"].iloc[0]
    assert abs(z25 - (197963 + 243597)) < 1000, (
        "Z25 debe sumar Huaral (197,963) + Huaura (243,597) según PDF INEI 2017"
    )

    z27 = gdf[gdf["zone_id"] == "Z27"]["population"].iloc[0]
    assert abs(z27 - 407286) < 1000, "Z27 debe sumar 407,286 (provincia de Ica, PDF INEI 2017)"


def test_build_zones_gdf_is_reproducible():
    a = build_zones_gdf()
    b = build_zones_gdf()
    assert list(a["population"]) == list(b["population"])
    assert list(a["employment"]) == list(b["employment"])
