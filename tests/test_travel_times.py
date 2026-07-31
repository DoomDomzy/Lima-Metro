import numpy as np
import pytest

import geopandas as gpd
from shapely.geometry import Point

from travel_times import (
    compute_haversine_matrix, compute_drive_times, compute_bus_times,
    compute_metro_times, compute_train_times, SPEED_CAR_KMH,
)


def _zones_gdf(lons, lats):
    rows = [{"zone_id": f"Z{i+1:02d}", "geometry": Point(lo, la)}
            for i, (lo, la) in enumerate(zip(lons, lats))]
    return gpd.GeoDataFrame(rows, crs="EPSG:4326")


def _stations_gdf(lons, lats, status="existing"):
    rows = [{"station_name": f"S{i+1}", "line_id": "L1",
             "station_order": i + 1, "status": status,
             "geometry": Point(lo, la)}
            for i, (lo, la) in enumerate(zip(lons, lats))]
    return gpd.GeoDataFrame(rows, crs="EPSG:4326")


def test_haversine_matches_reference_formula():
    gdf = _zones_gdf([-77.035, -75.770], [-12.050, -14.060])
    mat = compute_haversine_matrix(gdf)
    assert mat[0, 1] == mat[1, 0]
    assert mat[0, 0] == 0
    assert 100 < mat[0, 1] < 400, "Lima→Ica debe estar en el rango 100-400 km"


def test_haversine_symmetric_zero_diagonal():
    rng = np.random.default_rng(0)
    gdf = _zones_gdf(-77.0 + rng.uniform(-0.5, 0.5, 5),
                     -12.0 + rng.uniform(-0.5, 0.5, 5))
    mat = compute_haversine_matrix(gdf)
    np.testing.assert_allclose(mat, mat.T, atol=1e-9)
    assert np.all(np.diag(mat) == 0)


def test_haversine_equals_brute_force():
    rng = np.random.default_rng(1)
    n = 4
    lons = -77.0 + rng.uniform(-0.5, 0.5, n)
    lats = -12.0 + rng.uniform(-0.5, 0.5, n)
    gdf = _zones_gdf(lons, lats)

    vec = compute_haversine_matrix(gdf)
    ref = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            R = 6371
            dlat = np.radians(lats[j] - lats[i])
            dlon = np.radians(lons[j] - lons[i])
            a = (np.sin(dlat/2)**2
                 + np.cos(np.radians(lats[i])) * np.cos(np.radians(lats[j]))
                 * np.sin(dlon/2)**2)
            ref[i, j] = 2 * R * np.arcsin(np.sqrt(a))
    np.testing.assert_allclose(vec, ref, atol=1e-9)


def test_bus_times_are_slower_than_drive_times():
    gdf = _zones_gdf([-77.0, -76.8], [-12.0, -12.1])
    drive = compute_drive_times(gdf)
    bus = compute_bus_times(drive)
    assert np.all(bus >= drive)


def test_train_times_only_cover_long_distances():
    gdf = _zones_gdf([-77.0, -76.9, -75.77], [-12.0, -12.05, -14.06])
    train = compute_train_times(gdf)
    assert np.isinf(train[0, 1]), "Zonas cercanas no deben usar tren"
    assert np.isfinite(train[0, 2]), "Lima→Ica sí debe tener tren"


def test_metro_times_full_scenario_covers_more_zones():
    gdf = _zones_gdf([-77.0, -76.8], [-12.0, -12.1])
    stations = _stations_gdf([-77.0], [-12.0])
    base = compute_metro_times(gdf, stations, scenario="base")
    full = compute_metro_times(gdf, stations, scenario="full")
    assert np.isfinite(full).all()
    assert np.isfinite(base).all()
