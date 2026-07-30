import numpy as np
if not hasattr(np, 'float_'):
    np.float_ = np.float64

import sys, os, warnings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings("ignore")

from config import PROCESSED_DATA, FIGURES, RAW_DATA
from zones import build_zones_gdf, build_trip_generation, assign_stations_to_zones
from travel_times import build_travel_time_matrices
from demand_model import estimate_demand, compute_line_demand
import geopandas as gpd
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def run_phase2():
    print("=" * 60)
    print("FASE 2: Estimación de Demanda")
    print("=" * 60)

    # 1. Zones
    print("\n[1/6] Creando sistema de zonas...")
    zones = build_zones_gdf()
    zones_proj = zones.to_crs("EPSG:32718")
    zones_proj.to_file(PROCESSED_DATA / "zones.gpkg", layer="zones", driver="GPKG")
    trip_gen = build_trip_generation(zones)
    trip_gen.to_csv(PROCESSED_DATA / "trip_generation.csv", index=False)
    print(f"  {len(zones)} zonas, {trip_gen['trips_produced'].sum():,.0f} viajes generados")

    # 2. Assign stations to zones
    stations = gpd.read_file(str(PROCESSED_DATA / "stations.gpkg"), layer="stations")
    zone_assign = assign_stations_to_zones(stations, zones)

    # 3. Travel time matrices
    print("\n[2/6] Matrices de tiempo de viaje...")
    # Try loading OSM graph; if unavailable, use synthetic distances
    try:
        import osmnx as ox
        G = ox.load_graphml(str(RAW_DATA / "lima_drive.graphml"))
        print("  Red OSM cargada correctamente")
    except Exception as e:
        print(f"  Usando distancias sintéticas (OSM no disponible: {e})")
        G = None

    tt_matrices = build_travel_time_matrices(zones, stations, None, G)

    # 4. Demand estimation
    print("\n[3/6] Estimando demanda base...")
    result_base = estimate_demand(tt_matrices, trip_gen, scenario="base")

    print("\n[4/6] Estimando demanda red completa...")
    result_full = estimate_demand(tt_matrices, trip_gen, scenario="full")

    # 5. Line-level breakdown
    print("\n[5/6] Desglose por línea (red completa)...")
    line_demand = compute_line_demand(
        result_full["T_metro"], stations, zones, zone_assign
    )
    print(line_demand.to_string(index=False))

    # 6. Summary & visualization
    print("\n[6/6] Generando reporte...")
    summary = pd.DataFrame([
        {"Escenario": "Base (L1 + L2 parcial)", "Metro (pax/día)": int(result_base["metro_pax"]),
         "Tren (pax/día)": int(result_base["train_pax"]),
         "Total TP (pax/día)": int(result_base["total_public"])},
        {"Escenario": "Red Propuesta (6L + 2 trenes)", "Metro (pax/día)": int(result_full["metro_pax"]),
         "Tren (pax/día)": int(result_full["train_pax"]),
         "Total TP (pax/día)": int(result_full["total_public"])},
    ])
    print("\n" + summary.to_string(index=False))
    summary.to_csv(PROCESSED_DATA / "demand_comparison.csv", index=False)

    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(len(summary))
    width = 0.3
    ax.bar([i - width/2 for i in x], summary["Metro (pax/día)"], width, label="Metro", color="#2E86AB")
    ax.bar([i + width/2 for i in x], summary["Total TP (pax/día)"], width, label="Total TP", color="#F18F01", alpha=0.7)
    ax.set_xticks(list(x))
    ax.set_xticklabels(summary["Escenario"], fontsize=9)
    ax.set_ylabel("Pasajeros / día")
    ax.set_title("Comparación de Demanda: Base vs Red Propuesta")
    ax.legend()
    fig.tight_layout()
    fig.savefig(str(FIGURES / "demand_comparison.png"), dpi=150)
    plt.close()
    print(f"  Gráfico: {FIGURES / 'demand_comparison.png'}")

    # Validación L1
    l1_pax_base = line_demand[line_demand["line_id"] == "L1"]["daily_pax"].values
    if len(l1_pax_base) > 0:
        l1_vs_real = (l1_pax_base[0] / 700000) * 100
        print(f"\nValidación Línea 1:")
        print(f"  Estimado: {l1_pax_base[0]:,.0f} pax/día")
        print(f"  Real: 700,000 pax/día")
        print(f"  Precisión: {l1_vs_real:.1f}%")

    print("\n" + "=" * 60)
    print("FASE 2 completada.")
    return summary, line_demand


if __name__ == "__main__":
    run_phase2()
