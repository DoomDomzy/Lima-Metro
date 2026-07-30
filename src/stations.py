import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString
from config import CRS_GEOGRAPHIC, CRS_PROJECTED, RAW_DATA, PROCESSED_DATA

LINEA_1_STATIONS = [
    ("Bayóvar", -76.988678, -12.056576),
    ("Santa Rosa", -76.991065, -12.064914),
    ("San Martín", -76.993905, -12.072545),
    ("San Carlos", -76.997657, -12.080321),
    ("Los Postes", -77.002489, -12.088242),
    ("Los Jardines", -77.008750, -12.095524),
    ("Sanita Anita", -77.015420, -12.102135),
    ("Colectora Industrial", -77.022973, -12.107985),
    ("Hermilio Valdizán", -77.030785, -12.112750),
    ("Mercado Santa Anita", -77.038791, -12.115101),
    ("Vicuña", -77.047015, -12.115387),
    ("Canto Grande", -77.054403, -12.113868),
    ("Reggio", -77.061700, -12.112020),
    ("San Martín de Porres", -77.073665, -12.108186),
    ("Presbítero Maestro", -77.082636, -12.105815),
    ("Caja de Agua", -77.089195, -12.103920),
    ("Pirámides del Sol", -77.094764, -12.100012),
    ("Miguel Grau", -77.099790, -12.095370),
    ("El Ángel", -77.104920, -12.089919),
    ("Gamarra", -77.109454, -12.083669),
    ("Estación Central", -77.113821, -12.077447),
    ("Arriola", -77.117200, -12.070421),
    ("La Cultura", -77.120040, -12.062383),
    ("San Borja Sur", -77.122238, -12.053723),
    ("San Borja Norte", -77.124133, -12.046047),
    ("Angamos", -77.125775, -12.037825),
    ("Cabella", -77.127674, -12.029581),
    ("Villa María", -77.130651, -12.020151),
    ("Atocongo", -77.134403, -12.010520),
]

LINEA_2_STATIONS_PARTIAL = [
    ("Puerto de Callao", -77.1503, -12.0270),
    ("Buenos Aires", -77.1430, -12.0322),
    ("Carmen de la Legua", -77.1338, -12.0380),
    ("Oscar R. Benavides", -77.1240, -12.0422),
    ("Óvalo Santa Anita", -77.0360, -12.0400),
    ("Estación Central (L2)", -77.0400, -12.0450),
]

LINEA_3_STATIONS = [
    ("Comas", -77.0650, -11.9500),
    ("Los Olivos", -77.0700, -11.9700),
    ("San Martín de Porres (L3)", -77.0750, -11.9850),
    ("Caquetá", -77.0900, -12.0000),
    ("Plaza Bolognesi", -77.1000, -12.0200),
    ("Estación Central (L3)", -77.1150, -12.0450),
    ("Barranco", -77.1250, -12.0700),
    ("Chorrillos", -77.1300, -12.0850),
    ("San Juan de Miraflores", -77.1350, -12.1000),
]

LINEA_4_STATIONS = [
    ("Aeropuerto Jorge Chávez", -77.1148, -11.9800),
    ("Javier Prado Oeste", -77.0800, -12.0200),
    ("Javier Prado Este", -77.0500, -12.0300),
    ("Ate", -77.0100, -12.0400),
]

LINEA_5_STATIONS = [
    ("Benavides", -77.0800, -12.0700),
    ("Panamericana Sur 1", -77.0700, -12.0900),
    ("Panamericana Sur 2", -77.0600, -12.1100),
    ("Villa El Salvador", -77.0500, -12.1450),
]

LINEA_6_STATIONS = [
    ("Ate Vitarte", -76.9900, -12.0300),
    ("Santa Anita (L6)", -77.0200, -12.0350),
    ("El Agustino", -77.0400, -12.0400),
    ("Cercado Este", -77.0600, -12.0500),
    ("Rímac", -77.0800, -12.0600),
]

TREN_ICA_STATIONS = [
    ("Lima (Estación Central)", -77.0282, -12.0606),
    ("Lurín", -76.8820, -12.2800),
    ("Chilca", -76.7600, -12.5200),
    ("Mala", -76.6500, -12.6600),
    ("Asia", -76.5500, -12.7800),
    ("Cañete", -76.4200, -13.0800),
    ("Chincha", -76.1300, -13.4200),
    ("Pisco", -75.9800, -13.7100),
    ("Ica", -75.7700, -14.0600),
]

TREN_NORTE_STATIONS = [
    ("Lima (Estación Central)", -77.0282, -12.0606),
    ("Los Olivos Norte", -77.0800, -11.9400),
    ("Puente Piedra", -77.0800, -11.8500),
    ("Chancay", -77.2700, -11.5700),
    ("Huacho", -77.6100, -11.1100),
    ("Barranca", -77.7900, -10.7600),
]

LINES = {
    "L1": (LINEA_1_STATIONS, "Línea 1", "existing"),
    "L2": (LINEA_2_STATIONS_PARTIAL, "Línea 2", "partial"),
    "L3": (LINEA_3_STATIONS, "Línea 3", "proposed"),
    "L4": (LINEA_4_STATIONS, "Línea 4", "proposed"),
    "L5": (LINEA_5_STATIONS, "Línea 5", "proposed"),
    "L6": (LINEA_6_STATIONS, "Línea 6", "proposed"),
    "TREN_ICA": (TREN_ICA_STATIONS, "Tren Lima-Ica", "proposed"),
    "TREN_NORTE": (TREN_NORTE_STATIONS, "Tren del Norte", "proposed"),
}

def build_stations_gdf():
    rows = []
    for line_id, (stations, line_name, status) in LINES.items():
        for i, (name, lon, lat) in enumerate(stations):
            rows.append({
                "line_id": line_id,
                "line_name": line_name,
                "station_name": name,
                "station_order": i,
                "status": status,
                "geometry": Point(lon, lat),
            })
    gdf = gpd.GeoDataFrame(rows, crs=CRS_GEOGRAPHIC)
    return gdf

def build_lines_gdf(stations_gdf=None):
    if stations_gdf is None:
        stations_gdf = build_stations_gdf()
    rows = []
    for line_id, (_, line_name, status) in LINES.items():
        pts = stations_gdf[stations_gdf["line_id"] == line_id].sort_values("station_order")
        if len(pts) >= 2:
            rows.append({
                "line_id": line_id,
                "line_name": line_name,
                "status": status,
                "geometry": LineString(pts.geometry.tolist()),
            })
    return gpd.GeoDataFrame(rows, crs=CRS_GEOGRAPHIC)


if __name__ == "__main__":
    stations = build_stations_gdf()
    stations_proj = stations.to_crs(CRS_PROJECTED)
    stations_path = PROCESSED_DATA / "stations.gpkg"
    stations_proj.to_file(stations_path, layer="stations", driver="GPKG")

    lines = build_lines_gdf(stations)
    lines_proj = lines.to_crs(CRS_PROJECTED)
    lines_path = PROCESSED_DATA / "stations.gpkg"
    lines_proj.to_file(lines_path, layer="lines", driver="GPKG")

    print(f"Saved {len(stations)} stations and {len(lines)} lines to {stations_path}")
    print(stations.groupby("status").size())
