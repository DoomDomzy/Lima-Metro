import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
from config import CRS_GEOGRAPHIC, CRS_PROJECTED, PROCESSED_DATA

ZONES = [
    {"zone_id": "Z01", "district": "Lima (Cercado)", "population": 280000, "employment": 450000, "lon": -77.035, "lat": -12.050},
    {"zone_id": "Z02", "district": "San Juan de Lurigancho", "population": 1100000, "employment": 180000, "lon": -76.995, "lat": -12.020},
    {"zone_id": "Z03", "district": "Comas", "population": 540000, "employment": 80000, "lon": -77.065, "lat": -11.945},
    {"zone_id": "Z04", "district": "Los Olivos", "population": 380000, "employment": 90000, "lon": -77.075, "lat": -11.970},
    {"zone_id": "Z05", "district": "San Martín de Porres", "population": 650000, "employment": 110000, "lon": -77.080, "lat": -11.995},
    {"zone_id": "Z06", "district": "Independencia", "population": 220000, "employment": 50000, "lon": -77.050, "lat": -11.985},
    {"zone_id": "Z07", "district": "Rímac", "population": 180000, "employment": 40000, "lon": -77.050, "lat": -12.035},
    {"zone_id": "Z08", "district": "Breña / Pueblo Libre", "population": 150000, "employment": 60000, "lon": -77.060, "lat": -12.070},
    {"zone_id": "Z09", "district": "Jesús María / Magdalena", "population": 160000, "employment": 85000, "lon": -77.080, "lat": -12.095},
    {"zone_id": "Z10", "district": "La Victoria", "population": 180000, "employment": 120000, "lon": -77.030, "lat": -12.070},
    {"zone_id": "Z11", "district": "Santa Anita", "population": 240000, "employment": 60000, "lon": -77.015, "lat": -12.040},
    {"zone_id": "Z12", "district": "Ate", "population": 650000, "employment": 140000, "lon": -77.005, "lat": -12.030},
    {"zone_id": "Z13", "district": "El Agustino", "population": 210000, "employment": 35000, "lon": -77.040, "lat": -12.055},
    {"zone_id": "Z14", "district": "Miraflores / San Isidro", "population": 150000, "employment": 250000, "lon": -77.060, "lat": -12.110},
    {"zone_id": "Z15", "district": "San Borja / Surco", "population": 380000, "employment": 180000, "lon": -77.030, "lat": -12.115},
    {"zone_id": "Z16", "district": "La Molina", "population": 180000, "employment": 50000, "lon": -76.980, "lat": -12.070},
    {"zone_id": "Z17", "district": "Barranco / Chorrillos", "population": 150000, "employment": 40000, "lon": -77.080, "lat": -12.130},
    {"zone_id": "Z18", "district": "San Juan de Miraflores", "population": 420000, "employment": 60000, "lon": -77.010, "lat": -12.150},
    {"zone_id": "Z19", "district": "Villa María del Triunfo", "population": 450000, "employment": 50000, "lon": -77.000, "lat": -12.180},
    {"zone_id": "Z20", "district": "Villa El Salvador", "population": 400000, "employment": 55000, "lon": -77.050, "lat": -12.170},
    {"zone_id": "Z21", "district": "Callao (Cercado)", "population": 420000, "employment": 200000, "lon": -77.150, "lat": -12.050},
    {"zone_id": "Z22", "district": "Callao (Carmen / Bellavista)", "population": 180000, "employment": 60000, "lon": -77.130, "lat": -12.030},
    {"zone_id": "Z23", "district": "Lurín / Pachacámac", "population": 150000, "employment": 25000, "lon": -76.900, "lat": -12.210},
    {"zone_id": "Z24", "district": "Puente Piedra", "population": 350000, "employment": 30000, "lon": -77.080, "lat": -11.860},
    {"zone_id": "Z25", "district": "Chancay / Huacho (Norte)", "population": 300000, "employment": 60000, "lon": -77.500, "lat": -11.250},
    {"zone_id": "Z26", "district": "Cañete / Chincha (Sur)", "population": 350000, "employment": 70000, "lon": -76.250, "lat": -13.200},
    {"zone_id": "Z27", "district": "Ica", "population": 280000, "employment": 90000, "lon": -75.770, "lat": -14.060},
]

def build_zones_gdf():
    rows = []
    for z in ZONES:
        rows.append({
            "zone_id": z["zone_id"],
            "district": z["district"],
            "population": z["population"],
            "employment": z["employment"],
            "geometry": Point(z["lon"], z["lat"]),
        })
    gdf = gpd.GeoDataFrame(rows, crs=CRS_GEOGRAPHIC)
    return gdf

def assign_stations_to_zones(stations_gdf, zones_gdf):
    stations_proj = stations_gdf.to_crs(CRS_PROJECTED)
    zones_proj = zones_gdf.to_crs(CRS_PROJECTED)

    zones_buffer = zones_proj.copy()
    zones_buffer["geometry"] = zones_proj.geometry.buffer(15000)

    joined = gpd.sjoin(stations_proj, zones_buffer, how="left", predicate="within")

    unassigned_mask = joined["zone_id"].isna()
    unassigned = joined[unassigned_mask]

    if len(unassigned) > 0:
        print(f"  Asignando {len(unassigned)} estaciones lejanas por proximidad...")
        for idx in unassigned.index:
            station_pt = stations_proj.loc[idx].geometry
            distances = zones_proj.distance(station_pt)
            nearest_idx = distances.idxmin()
            joined.loc[idx, "zone_id"] = zones_proj.loc[nearest_idx, "zone_id"]
            joined.loc[idx, "district"] = zones_proj.loc[nearest_idx, "district"]

    station_zone = joined[["station_name", "line_id", "station_order", "zone_id", "district"]].copy()

    remaining = station_zone[station_zone["zone_id"].isna()]
    if len(remaining) > 0:
        print(f"  Advertencia: {len(remaining)} estaciones sin zona asignada")

    return station_zone

def build_trip_generation(zones_gdf, trip_rate_per_person=2.5):
    df = zones_gdf.copy()
    df["trips_produced"] = (df["population"] * trip_rate_per_person * 0.5).astype(int)
    df["trips_attracted"] = (df["employment"] * trip_rate_per_person * 1.5).astype(int)
    df["trips_attracted"] = df["trips_attracted"] * df["trips_produced"].sum() / df["trips_attracted"].sum()
    df["trips_attracted"] = df["trips_attracted"].astype(int)
    return df[["zone_id", "district", "population", "employment", "trips_produced", "trips_attracted"]]


if __name__ == "__main__":
    zones = build_zones_gdf()
    zones_proj = zones.to_crs(CRS_PROJECTED)
    zones_proj.to_file(PROCESSED_DATA / "zones.gpkg", layer="zones", driver="GPKG")

    trip_table = build_trip_generation(zones)
    trip_table.to_csv(PROCESSED_DATA / "trip_generation.csv", index=False)

    print(f"Zonas: {len(zones)}")
    print(f"Población total: {zones['population'].sum():,}")
    print(f"Empleo total: {zones['employment'].sum():,}")
    print(f"Viajes producidos: {trip_table['trips_produced'].sum():,}")
    print(f"Viajes atraídos: {trip_table['trips_attracted'].sum():,}")
