import pandas as pd
import numpy as np
from config import RAW_DATA, PROCESSED_DATA
from stations import build_stations_gdf

def build_synthetic_gtfs():
    stations = build_stations_gdf()
    existing = stations[stations["status"].isin(["existing", "partial"])].copy()
    n_stops = len(existing)

    stops = pd.DataFrame({
        "stop_id": existing["line_id"] + "_" + existing["station_order"].astype(str),
        "stop_name": existing["station_name"],
        "stop_lat": existing.geometry.y,
        "stop_lon": existing.geometry.x,
    })

    route_ids = existing["line_id"].unique()
    routes = pd.DataFrame({
        "route_id": route_ids,
        "route_short_name": route_ids,
        "route_long_name": [f"Línea {r}" for r in route_ids],
        "route_type": 1,
    })

    np.random.seed(42)
    n_trips = 50
    trips_list = []
    stop_times_list = []
    for i, rid in enumerate(route_ids):
        line_stops = existing[existing["line_id"] == rid].sort_values("station_order")
        if len(line_stops) < 2:
            continue
        for t in range(n_trips):
            trip_id = f"{rid}_trip_{t}"
            trips_list.append({
                "route_id": rid,
                "trip_id": trip_id,
                "direction_id": t % 2,
            })
            dep_sec = 6 * 3600 + t * 600
            for _, row in line_stops.iterrows():
                stop_times_list.append({
                    "trip_id": trip_id,
                    "stop_id": f"{row['line_id']}_{row['station_order']}",
                    "stop_sequence": row["station_order"],
                    "arrival_time": dep_sec,
                    "departure_time": dep_sec,
                })
                dep_sec += 120

    trips = pd.DataFrame(trips_list)
    stop_times = pd.DataFrame(stop_times_list)

    stops.to_csv(PROCESSED_DATA / "gtfs_stops.csv", index=False)
    routes.to_csv(PROCESSED_DATA / "gtfs_routes.csv", index=False)
    trips.to_csv(PROCESSED_DATA / "gtfs_trips.csv", index=False)
    stop_times.to_csv(PROCESSED_DATA / "gtfs_stop_times.csv", index=False)

    print(f"GTFS sintético generado: {len(stops)} paradas, {len(routes)} rutas, {len(trips)} viajes")
    return routes, trips, stops


def download_gtfs_lima():
    zip_path = RAW_DATA / "gtfs_lima.zip"
    if zip_path.exists():
        print(f"GTFS ya existe en {zip_path}")
        return zip_path

    print("No se pudo descargar GTFS real. Se usará dataset sintético basado en estaciones definidas.")
    return None

def load_gtfs_trips(zip_path):
    if zip_path and zip_path.exists():
        import zipfile, io
        try:
            with zipfile.ZipFile(zip_path, "r") as z:
                routes = pd.read_csv(io.BytesIO(z.read("routes.txt")))
                trips = pd.read_csv(io.BytesIO(z.read("trips.txt")))
                stop_times = pd.read_csv(io.BytesIO(z.read("stop_times.txt")))
                stops = pd.read_csv(io.BytesIO(z.read("stops.txt")))
            print(f"Rutas: {len(routes)}, Viajes: {len(trips)}, Paradas: {len(stops)}")
            return routes, trips, stops
        except Exception as e:
            print(f"Error leyendo GTFS: {e}")

    gtfs_path = PROCESSED_DATA
    stops_path = gtfs_path / "gtfs_stops.csv"
    if stops_path.exists():
        stops = pd.read_csv(stops_path)
        routes = pd.read_csv(gtfs_path / "gtfs_routes.csv")
        trips = pd.read_csv(gtfs_path / "gtfs_trips.csv")
        print(f"GTFS sintético cargado: {len(routes)} rutas, {len(trips)} viajes, {len(stops)} paradas")
        return routes, trips, stops

    print("GTFS no disponible. Ejecute build_synthetic_gtfs() primero.")
    return None, None, None


if __name__ == "__main__":
    zip_path = download_gtfs_lima()
    if zip_path is None:
        print("Generando GTFS sintético...")
        build_synthetic_gtfs()
    routes, trips, stops = load_gtfs_trips(zip_path)
