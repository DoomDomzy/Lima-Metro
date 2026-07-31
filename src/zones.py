import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
from config import RAW_DATA, CRS_GEOGRAPHIC, CRS_PROJECTED, PROCESSED_DATA


def load_inei_population():
    path = RAW_DATA / "poblacion_distrital_2017.json"
    if not path.exists():
        print("  [ADVERTENCIA] No se encontró datos INEI. Usando valores por defecto.")
        return None
    with open(path) as f:
        return {r["ubigeo"]: r for r in json.load(f)}


ZONES = [
        {"zone_id": "Z01", "district": "Lima (Cercado)",
         "ubigeos": ["150101"],
         "employment_rate": 1.10,
         "lon": -77.035, "lat": -12.050},

        {"zone_id": "Z02", "district": "San Juan de Lurigancho",
         "ubigeos": ["150132"],
         "employment_rate": 0.18,
         "lon": -76.995, "lat": -12.020},

        {"zone_id": "Z03", "district": "Comas",
         "ubigeos": ["150110"],
         "employment_rate": 0.20,
         "lon": -77.065, "lat": -11.945},

        {"zone_id": "Z04", "district": "Los Olivos",
         "ubigeos": ["150117"],
         "employment_rate": 0.25,
         "lon": -77.075, "lat": -11.970},

        {"zone_id": "Z05", "district": "San Martín de Porres",
         "ubigeos": ["150135"],
         "employment_rate": 0.22,
         "lon": -77.080, "lat": -11.995},

        {"zone_id": "Z06", "district": "Independencia",
         "ubigeos": ["150112"],
         "employment_rate": 0.25,
         "lon": -77.050, "lat": -11.985},

        {"zone_id": "Z07", "district": "Rímac",
         "ubigeos": ["150128"],
         "employment_rate": 0.25,
         "lon": -77.050, "lat": -12.035},

        {"zone_id": "Z08", "district": "Breña / Pueblo Libre",
         "ubigeos": ["150105", "150121"],
         "employment_rate": 0.40,
         "lon": -77.060, "lat": -12.070},

        {"zone_id": "Z09", "district": "Jesús María / Magdalena",
         "ubigeos": ["150113", "150120"],
         "employment_rate": 0.45,
         "lon": -77.080, "lat": -12.095},

        {"zone_id": "Z10", "district": "La Victoria",
         "ubigeos": ["150115"],
         "employment_rate": 0.60,
         "lon": -77.030, "lat": -12.070},

        {"zone_id": "Z11", "district": "Santa Anita",
         "ubigeos": ["150137"],
         "employment_rate": 0.30,
         "lon": -77.015, "lat": -12.040},

        {"zone_id": "Z12", "district": "Ate",
         "ubigeos": ["150103"],
         "employment_rate": 0.25,
         "lon": -77.005, "lat": -12.030},

        {"zone_id": "Z13", "district": "El Agustino",
         "ubigeos": ["150111"],
         "employment_rate": 0.22,
         "lon": -77.040, "lat": -12.055},

        {"zone_id": "Z14", "district": "Miraflores / San Isidro",
         "ubigeos": ["150122", "150131"],
         "employment_rate": 1.20,
         "lon": -77.060, "lat": -12.110},

        {"zone_id": "Z15", "district": "San Borja / Surco / Surquillo",
         "ubigeos": ["150130", "150140", "150141", "150134"],
         "employment_rate": 0.65,
         "lon": -77.030, "lat": -12.115},

        {"zone_id": "Z16", "district": "La Molina / Chaclacayo / Lurigancho",
         "ubigeos": ["150114", "150107", "150118"],
         "employment_rate": 0.25,
         "lon": -76.980, "lat": -12.070},

        {"zone_id": "Z17", "district": "Barranco / Chorrillos / San Miguel",
         "ubigeos": ["150104", "150108", "150136", "150116"],
         "employment_rate": 0.35,
         "lon": -77.080, "lat": -12.130},

        {"zone_id": "Z18", "district": "San Juan de Miraflores",
         "ubigeos": ["150133"],
         "employment_rate": 0.20,
         "lon": -77.010, "lat": -12.150},

        {"zone_id": "Z19", "district": "Villa María del Triunfo",
         "ubigeos": ["150143"],
         "employment_rate": 0.18,
         "lon": -77.000, "lat": -12.180},

        {"zone_id": "Z20", "district": "Villa El Salvador",
         "ubigeos": ["150142"],
         "employment_rate": 0.18,
         "lon": -77.050, "lat": -12.170},

        {"zone_id": "Z21", "district": "Callao (Cercado / Ventanilla)",
         "ubigeos": ["070101", "070106", "070107"],
         "employment_rate": 0.35,
         "lon": -77.150, "lat": -12.050},

        {"zone_id": "Z22", "district": "Callao (Bellavista / Carmen / La Perla)",
         "ubigeos": ["070102", "070103", "070104", "070105"],
         "employment_rate": 0.30,
         "lon": -77.130, "lat": -12.030},

        {"zone_id": "Z23", "district": "Lurín / Pachacámac / Sur costero",
         "ubigeos": ["150119", "150123", "150109", "150124", "150126", "150127", "150129", "150138"],
         "employment_rate": 0.20,
         "lon": -76.900, "lat": -12.210},

        {"zone_id": "Z24", "district": "Puente Piedra / Carabayllo / Ancón",
         "ubigeos": ["150125", "150106", "150102", "150139"],
         "employment_rate": 0.20,
         "lon": -77.080, "lat": -11.860},

        {"zone_id": "Z25", "district": "Chancay / Huacho (Norte)",
         "ubigeos": ["150801", "150802", "150803", "150804", "150805", "150806",
                      "150807", "150808", "150809", "150810", "150811", "150812",
                      "150601", "150602", "150603", "150604",
                      "150605", "150606", "150607", "150608", "150609",
                      "150610", "150611", "150612"],
         "employment_rate": 0.25,
         "lon": -77.500, "lat": -11.250},

        {"zone_id": "Z26", "district": "Cañete / Chincha (Sur)",
         "ubigeos": ["150501", "150502", "150503", "150504", "150505",
                      "150506", "150507", "150508", "150509", "150510",
                      "150511", "150512", "150513", "150514", "150515", "150516",
                      "110201", "110202", "110203", "110204", "110205",
                      "110206", "110207", "110208", "110209", "110210", "110211"],
         "employment_rate": 0.22,
         "lon": -76.250, "lat": -13.200},

        {"zone_id": "Z27", "district": "Ica",
         "ubigeos": ["110101", "110102", "110103", "110104", "110105",
                      "110106", "110107", "110108", "110109", "110110",
                      "110111", "110112", "110113", "110114"],
         "employment_rate": 0.30,
         "lon": -75.770, "lat": -14.060},
    ]


def build_zones_gdf(pop_data=None):
    if pop_data is None:
        pop_data = load_inei_population()

    rows = []
    if pop_data is not None:
        data_keys = set(pop_data.keys())
        declared = set()
        for z in ZONES:
            declared.update(z["ubigeos"])
        unmapped = declared - data_keys
        if unmapped:
            raise ValueError(
                f"Ubigeos declarados en ZONES que no existen en la fuente INEI: {sorted(unmapped)}"
            )
    for z in ZONES:
        if pop_data:
            pop = sum(pop_data[ub]["total"] for ub in z["ubigeos"] if ub in pop_data)
            emp = int(pop * z["employment_rate"])
        else:
            pop = 200000
            emp = 50000

        rows.append({
            "zone_id": z["zone_id"],
            "district": z["district"],
            "population": pop,
            "employment": emp,
            "geometry": Point(z["lon"], z["lat"]),
        })

    gdf = gpd.GeoDataFrame(rows, crs=CRS_GEOGRAPHIC)
    return gdf


def load_district_boundaries():
    path = PROCESSED_DATA / "lima_districts.gpkg"
    if path.exists():
        gdf = gpd.read_file(path, layer="districts")
        if gdf.crs is None:
            gdf.set_crs(CRS_GEOGRAPHIC, inplace=True)
        if not gdf.is_valid.all():
            n_invalid = int((~gdf.is_valid).sum())
            raise ValueError(
                f"Geometrías de distritos inválidas: {n_invalid} (auto-intersecciones o topología rota)"
            )
        return gdf
    return None


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
    total_prod = df["trips_produced"].sum()
    total_attr = df["trips_attracted"].sum()
    if total_attr > 0:
        df["trips_attracted"] = (df["trips_attracted"] * total_prod / total_attr).astype(int)
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
