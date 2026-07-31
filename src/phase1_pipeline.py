import numpy as np
if not hasattr(np, 'float_'):
    np.float_ = np.float64

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import RAW_DATA, PROCESSED_DATA, BUFFER_METERS, CRS_PROJECTED
from stations import build_stations_gdf, build_lines_gdf
from data_osm import download_lima_network, download_lima_buildings
from data_gtfs import download_gtfs_lima, load_gtfs_trips, build_synthetic_gtfs

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

from viz_style import configure_matplotlib, save_fig, PALETTE, TEXT


def run_phase1():
    print("=" * 60)
    print("FASE 1: Preparación de datos y GIS")
    print("=" * 60)

    matplotlib.use("Agg")
    configure_matplotlib()

    # 1. Stations
    print("\n[1/5] Construyendo estaciones...")
    stations = build_stations_gdf()
    stations_proj = stations.to_crs(CRS_PROJECTED)
    stations_path = PROCESSED_DATA / "stations.gpkg"
    stations_proj.to_file(stations_path, layer="stations", driver="GPKG")

    lines = build_lines_gdf(stations)
    lines_proj = lines.to_crs(CRS_PROJECTED)
    lines_proj.to_file(stations_path, layer="lines", driver="GPKG")
    print(f"  {len(stations)} estaciones, {len(lines)} líneas guardadas.")

    # 2. Buffers de 800 m
    print("\n[2/5] Calculando buffers de 800 m...")
    buffers = stations_proj.copy()
    buffers["geometry"] = stations_proj.geometry.buffer(BUFFER_METERS)
    buffers.to_file(PROCESSED_DATA / "buffers.gpkg", layer="buffers", driver="GPKG")

    buffer_union = buffers.geometry.union_all()
    total_buffer_km2 = buffer_union.area / 1e6
    print(f"  Área total cubierta por buffers (800 m): {total_buffer_km2:.1f} km²")

    # 3. OSM data (opcional - timeoutea si la ciudad es muy grande)
    print("\n[3/5] Descargando datos OSM...")
    G = None
    buildings = None
    osm_path = RAW_DATA / "lima_drive.graphml"
    if osm_path.exists():
        print("  Red OSM ya existe, saltando descarga.")
    else:
        import signal
        class TimeoutError(Exception):
            pass

        def handler(signum, frame):
            raise TimeoutError("Descarga OSM agotó el tiempo límite")

        signal.signal(signal.SIGALRM, handler)
        signal.alarm(120)
        try:
            G = download_lima_network()
            buildings = download_lima_buildings()
            print(f"  Edificios descargados: {len(buildings)}")
        except TimeoutError:
            print("  [SKIP] Descarga OSM excede 120s. Se usará modo sin OSM.")
        except Exception as e:
            print(f"  Error descargando datos OSM: {e}")
        finally:
            signal.alarm(0)

    # 4. GTFS
    print("\n[4/5] Datos GTFS...")
    zip_path = download_gtfs_lima()
    if zip_path is None:
        build_synthetic_gtfs()
    routes, trips, stops = load_gtfs_trips(zip_path)

    # 5. Visualización
    print("\n[5/5] Generando mapas...")

    fig, ax = plt.subplots(1, 1, figsize=(12, 14))

    status_colors = {
        "existing": PALETTE[0],
        "partial": PALETTE[2],
        "proposed": PALETTE[4],
    }
    for status, color in status_colors.items():
        subset = lines_proj[lines_proj["status"] == status]
        if not subset.empty:
            subset.plot(ax=ax, color=color, linewidth=2.5, label=status, alpha=0.8)
    stations_proj.plot(
        ax=ax, color=TEXT, markersize=8, alpha=0.7, label="Estaciones"
    )
    ax.legend(fontsize=10, frameon=False)
    ax.set_title("Red Ferroviaria Propuesta para Lima Metropolitana", fontsize=14)
    ax.set_axis_off()

    save_fig(fig, "red_ferroviaria_propuesta.png")

    # Buffer coverage map
    fig2, ax2 = plt.subplots(1, 1, figsize=(12, 14))
    buffer_dissolved = gpd.GeoSeries([buffer_union], crs=CRS_PROJECTED)
    buffer_dissolved.plot(ax=ax2, color=PALETTE[2], alpha=0.3, label="Buffers 800m")
    lines_proj.plot(ax=ax2, color=PALETTE[0], linewidth=2, alpha=0.8, label="Líneas")
    stations_proj.plot(ax=ax2, color="#2B2B33", markersize=6, alpha=0.7)
    ax2.legend(fontsize=10, frameon=False)
    ax2.set_title("Cobertura de Estaciones (Buffers de 800 m)", fontsize=14)
    ax2.set_axis_off()

    save_fig(fig2, "buffer_coverage.png")

    summary = stations.groupby(["line_name", "status"]).size().reset_index(name="stations")
    print("\nResumen de estaciones:")
    print(summary.to_string(index=False))

    total_proposed = len(stations[stations["status"] == "proposed"])
    total_existing = len(stations[stations["status"] == "existing"])
    total_partial = len(stations[stations["status"] == "partial"])
    print(f"\nTotal: {total_existing} existentes, {total_partial} parciales, {total_proposed} propuestas")
    print(f"Cobertura total de buffers: {total_buffer_km2:.1f} km²")
    print("\nFASE 1 completada.")


if __name__ == "__main__":
    run_phase1()
