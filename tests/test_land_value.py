import pytest

import numpy as np

from zones import ZONES, build_zones_gdf
from land_value import DISTRICT_PRICE_INDEX, simulate_land_values


def test_price_index_covers_every_zone_district():
    gdf = build_zones_gdf()
    missing = set(gdf["district"].unique()) - set(DISTRICT_PRICE_INDEX.keys())
    assert not missing, f"Distritos sin índice de precio: {sorted(missing)}"


def test_price_index_has_no_stale_keys():
    gdf = build_zones_gdf()
    known = set(gdf["district"].unique())
    stale = set(DISTRICT_PRICE_INDEX.keys()) - known
    assert not stale, f"Índices que ya no corresponden a ninguna zona: {sorted(stale)}"


def test_simulate_land_values_raises_on_unmapped_district():
    gdf = build_zones_gdf()
    bad = gdf.copy()
    bad.loc[0, "district"] = "Distrito Inexistente"
    import geopandas as gpd
    bad = gpd.GeoDataFrame(bad)
    with pytest.raises(ValueError):
        simulate_land_values(bad, bad.copy())
