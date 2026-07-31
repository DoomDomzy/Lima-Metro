import numpy as np
import pandas as pd
import osmnx as ox
import networkx as nx
from config import CRS_PROJECTED, CRS_GEOGRAPHIC, RAW_DATA, PROCESSED_DATA

SPEED_CAR_KMH = 25
SPEED_BUS_KMH = 15
SPEED_METRO_KMH = 35
SPEED_TRAIN_KMH = 80
ACCESS_WALK_SPEED_KMH = 4.5
WAITING_TIME_MIN = 5

def _haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1))*np.cos(np.radians(lat2))*np.sin(dlon/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

def compute_haversine_matrix(zones_gdf):
    n = len(zones_gdf)
    lats = zones_gdf.geometry.y.values.astype(float)
    lons = zones_gdf.geometry.x.values.astype(float)
    dlat = np.radians(lats[:, None] - lats[None, :])
    dlon = np.radians(lons[:, None] - lons[None, :])
    la1 = np.radians(lats)[:, None]
    la2 = np.radians(lats)[None, :]
    a = np.sin(dlat/2)**2 + np.cos(la1)*np.cos(la2)*np.sin(dlon/2)**2
    return 2 * 6371 * np.arcsin(np.sqrt(a))

def load_osm_graph():
    path = RAW_DATA / "lima_drive.graphml"
    from data_osm import cache_is_fresh
    if path.exists() and cache_is_fresh():
        print(f"   Cargando red OSM desde {path}...")
        return ox.load_graphml(str(path))
    return None

def _add_travel_time(G, default_speed_kmh=40):
    for u, v, k, d in G.edges(data=True, keys=True):
        if "travel_time" not in d:
            if "length" in d and d["length"] > 0:
                speed = default_speed_kmh
                if "maxspeed" in d:
                    ms = d["maxspeed"]
                    if isinstance(ms, list):
                        ms = ms[0]
                    try:
                        speed = float(ms)
                    except (ValueError, TypeError):
                        speed = default_speed_kmh
                d["travel_time"] = d["length"] / (speed / 3.6)
            else:
                d["travel_time"] = 1
    return G

def compute_drive_times_osm(zones_gdf, G):
    G = _add_travel_time(G)
    from config import CRS_GEOGRAPHIC
    zones_geo = zones_gdf.to_crs(CRS_GEOGRAPHIC) if zones_gdf.crs != CRS_GEOGRAPHIC else zones_gdf
    n = len(zones_geo)
    times = np.full((n, n), np.inf)
    nodes = []
    for _, row in zones_geo.iterrows():
        pt = (row.geometry.y, row.geometry.x)
        node = ox.nearest_nodes(G, pt[1], pt[0])
        nodes.append(node)

    print(f"   {n} nodos de zona encontrados en el grafo OSM")
    succeeded = 0
    for i in range(n):
        times[i, i] = 0
        for j in range(i + 1, n):
            try:
                route = nx.shortest_path(G, nodes[i], nodes[j], weight="travel_time")
                time_sec = sum(
                    G.edges[route[k], route[k + 1], 0].get("travel_time", 0)
                    for k in range(len(route) - 1)
                )
                if time_sec > 0:
                    times[i, j] = time_sec / 60
                    times[j, i] = time_sec / 60
                    succeeded += 1
            except nx.NetworkXNoPath:
                pass
    print(f"   Rutas calculadas: {succeeded} de {n*(n-1)//2}")
    return times

def compute_drive_times(zones_gdf, G=None, km=None):
    if G is not None:
        print("   Usando routing OSM...")
        return compute_drive_times_osm(zones_gdf, G)
    print("   Usando haversine + factor de congestión...")
    if km is None:
        km = compute_haversine_matrix(zones_gdf)
    time = km * 1.4 / SPEED_CAR_KMH * 60
    np.fill_diagonal(time, 0)
    return time

def compute_bus_times(drive_times):
    return np.where(np.isfinite(drive_times),
                    drive_times * SPEED_CAR_KMH / SPEED_BUS_KMH + WAITING_TIME_MIN, np.inf)

def compute_metro_times(zones_gdf, stations_gdf, scenario="base", km=None):
    n = len(zones_gdf)
    if km is None:
        km = compute_haversine_matrix(zones_gdf)

    if scenario == "base":
        active = stations_gdf[stations_gdf["status"].isin(["existing", "partial"])]
    else:
        active = stations_gdf

    print(f"   Estaciones activas: {len(active)}")
    zones_proj = zones_gdf.to_crs(CRS_PROJECTED)
    stations_proj = active.to_crs(CRS_PROJECTED)

    zone_pts = np.asarray(zones_proj.geometry.values)
    station_pts = np.asarray(stations_proj.geometry.values)
    from shapely import distance
    dist = distance(zone_pts[:, None], station_pts[None, :])
    min_dist_km = np.nanmin(dist, axis=1) / 1000.0

    print(f"   Distancia mínima promedio a estación: {min_dist_km.mean():.2f} km")
    print(f"   Rango: {min_dist_km.min():.2f} - {min_dist_km.max():.2f} km")

    access_time = (min_dist_km[:, None] + min_dist_km[None, :]) / ACCESS_WALK_SPEED_KMH * 60
    line_haul = km * 0.85 / SPEED_METRO_KMH * 60
    if scenario == "base":
        line_haul = np.where(km > 20, line_haul * 1.4, line_haul)
    times = access_time + line_haul + WAITING_TIME_MIN
    np.fill_diagonal(times, 0)
    return times

def compute_train_times(zones_gdf, km=None):
    n = len(zones_gdf)
    if km is None:
        km = compute_haversine_matrix(zones_gdf)
    times = np.full((n, n), np.inf)
    mask = km > 50
    times[mask] = km[mask] / SPEED_TRAIN_KMH * 60 + 30
    np.fill_diagonal(times, 0)
    return times

def build_travel_time_matrices(zones_gdf, stations_gdf, lines_gdf=None, G_drive=None, use_osm=False):
    zone_ids = zones_gdf["zone_id"].tolist()

    if use_osm:
        if G_drive is None:
            G_drive = load_osm_graph()
        if G_drive is not None:
            print("   Red OSM cargada. Usando routing real para autos.")
        else:
            print("   Red OSM no disponible. Usando haversine.")
            use_osm = False

    print(f"\n[1/4] Matriz auto{' (OSM routing)' if use_osm and G_drive else ' (haversine)'}...")
    km = compute_haversine_matrix(zones_gdf)
    t_car = compute_drive_times(zones_gdf, G=G_drive if use_osm else None, km=km)

    print("[2/4] Matriz bus...")
    t_bus = compute_bus_times(t_car)

    print("[3/4] Matrices metro (base y full)...")
    t_metro_base = compute_metro_times(zones_gdf, stations_gdf, scenario="base", km=km)
    t_metro_full = compute_metro_times(zones_gdf, stations_gdf, scenario="full", km=km)

    print("[4/4] Matriz tren...")
    t_train = compute_train_times(zones_gdf, km=km)

    matrices = {"car": t_car, "bus": t_bus, "metro_base": t_metro_base,
                "metro_full": t_metro_full, "train": t_train}

    for name, mat in matrices.items():
        pd.DataFrame(mat, index=zone_ids, columns=zone_ids).to_csv(
            PROCESSED_DATA / f"tt_{name}.csv")
        valid = np.isfinite(mat).sum()
        avg = mat[np.isfinite(mat)].mean() if valid > 0 else 0
        print(f"  {name}: media={avg:.1f} min, finitos={valid}/{len(zone_ids)**2}")

    return matrices


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import geopandas as gpd

    zones = gpd.read_file(str(PROCESSED_DATA / "zones.gpkg"), layer="zones")
    stations = gpd.read_file(str(PROCESSED_DATA / "stations.gpkg"), layer="stations")

    build_travel_time_matrices(zones, stations)
