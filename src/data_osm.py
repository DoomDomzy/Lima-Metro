import hashlib
import json
from pathlib import Path

import numpy as np
if not hasattr(np, 'float_'):
    np.float_ = np.float64

import osmnx as ox
import geopandas as gpd
from config import LIMA_BBOX, PROCESSED_DATA, RAW_DATA


def _cache_key():
    src = Path(__file__).read_text()
    return hashlib.sha256((src + repr(LIMA_BBOX)).encode()).hexdigest()[:12]


def _cache_meta_path():
    return RAW_DATA / "lima_drive.graphml.meta.json"


def save_cache_meta():
    _cache_meta_path().write_text(json.dumps({"cache_key": _cache_key()}))


def cache_is_fresh():
    meta = _cache_meta_path()
    if not meta.exists():
        return False
    try:
        return json.loads(meta.read_text()).get("cache_key") == _cache_key()
    except (json.JSONDecodeError, OSError):
        return False

def download_lima_network():
    print("Descargando red vial de Lima Metropolitana...")
    G = ox.graph_from_bbox(
        bbox=LIMA_BBOX,
        network_type="drive",
        truncate_by_edge=True,
    )
    print(f"Red vial: {len(G.nodes)} nodos, {len(G.edges)} aristas")
    ox.save_graphml(G, str(RAW_DATA / "lima_drive.graphml"))
    save_cache_meta()
    print("Guardado en data/raw/lima_drive.graphml")
    return G

def download_lima_buildings():
    print("Descargando edificios de Lima...")
    buildings = ox.features_from_bbox(
        bbox=LIMA_BBOX,
        tags={"building": True},
    )
    print(f"Edificios descargados: {len(buildings)}")
    gdf = buildings.copy()
    gdf.columns = [str(c).lower().replace(" ", "_").replace(".", "_").replace(":", "_") for c in gdf.columns]
    drop_cols = [c for c in gdf.columns if "source" in c.lower()]
    if drop_cols:
        gdf = gdf.drop(columns=drop_cols)
    gdf.to_file(RAW_DATA / "lima_buildings.gpkg", driver="GPKG")
    print(f"Guardados: {len(gdf)} edificios en {RAW_DATA / 'lima_buildings.gpkg'}")
    return buildings

def download_lima_administrative():
    print("Descargando límites distritales...")
    gdf = ox.geocode_to_gdf("Lima, Peru")
    gdf.to_file(RAW_DATA / "lima_admin.gpkg", driver="GPKG")
    print(f"Límites guardados: {len(gdf)} entidades")
    return gdf

def get_walk_network():
    print("Descargando red peatonal...")
    G_walk = ox.graph_from_bbox(
        bbox=LIMA_BBOX,
        network_type="walk",
        truncate_by_edge=True,
    )
    print(f"Red peatonal: {len(G_walk.nodes)} nodos, {len(G_walk.edges)} aristas")
    return G_walk


if __name__ == "__main__":
    G = download_lima_network()
    try:
        buildings = download_lima_buildings()
    except Exception as e:
        print(f"Error descargando edificios: {e}")
    admin = download_lima_administrative()
    print("Descarga OSM completa.")
