import numpy as np
if not hasattr(np, 'float_'):
    np.float_ = np.float64

import sys, os, warnings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings("ignore")

from config import PROCESSED_DATA
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from viz_style import configure_matplotlib, save_fig, PALETTE


def run_phase3():
    print("=" * 60)
    print("FASE 3: Evaluación de Impactos")
    print("=" * 60)
    configure_matplotlib()

    # Load shared data
    trip_gen = pd.read_csv(PROCESSED_DATA / "trip_generation.csv")
    matrices = {}
    for k in ["car", "bus", "metro_base", "metro_full", "train"]:
        m = pd.read_csv(PROCESSED_DATA / f"tt_{k}.csv", index_col=0)
        matrices[k] = m.values.astype(float)

    from demand_model import estimate_demand
    from congestion import compute_congestion_impact
    from cost_benefit import (
        compute_social_benefits, compute_investment_cost, compute_cost_benefit,
        LINE_LENGTHS, METRO_COST_PER_KM, TRAIN_COST_PER_KM
    )
    from land_value import simulate_land_values, plot_land_value

    # 1. Demand basics
    print("\n[1/4] Estimando demanda (escenario completo)...")
    r_full = estimate_demand(matrices, trip_gen, "full")
    r_base = estimate_demand(matrices, trip_gen, "base")

    # 2. Congestion
    print("\n[2/4] Impacto en congestión...")
    c_full = compute_congestion_impact(
        r_full["metro_pax"], r_full["train_pax"], "Red Completa"
    )
    c_base = compute_congestion_impact(
        r_base["metro_pax"], r_base["train_pax"], "Base"
    )

    congestion_df = pd.DataFrame([
        {"Métrica": "Viajes transferidos a TP/día", "Base": c_base["switched_trips"],
         "Red Completa": c_full["switched_trips"]},
        {"Métrica": "Horas ahorradas/día", "Base": c_base["hours_saved_total"],
         "Red Completa": c_full["hours_saved_total"]},
        {"Métrica": "Vehículos-km evitados/día", "Base": c_base["vehicle_km_saved"],
         "Red Completa": c_full["vehicle_km_saved"]},
        {"Métrica": "Vehículos retirados", "Base": c_base["vehicles_removed"],
         "Red Completa": c_full["vehicles_removed"]},
        {"Métrica": "Vehículos menos en hora punta", "Base": c_base["peak_vehicles"],
         "Red Completa": c_full["peak_vehicles"]},
    ])
    for col in ["Base", "Red Completa"]:
        congestion_df[col] = congestion_df[col].round(0).astype(int)
    print(congestion_df.to_string(index=False))

    # 3. Cost-Benefit
    print("\n[3/4] Análisis costo-beneficio social...")
    benefits = compute_social_benefits(r_full["metro_pax"], r_full["train_pax"], "Red Completa")

    total_inv, inv_df = compute_investment_cost()
    print(f"\nInversión total: S/{total_inv:,.0f} ({total_inv/3.7:,.0f} USD)")

    cb_base = compute_cost_benefit(benefits, total_inv, "Red Completa")

    pd.DataFrame([{
        "indicador": "beneficio_anual_total",
        "valor": benefits["annual_total"],
        "unidad": "S/ anual",
    }, {
        "indicador": "ahorro_tiempo_anual",
        "valor": benefits["annual_time"],
        "unidad": "S/ anual",
    }, {
        "indicador": "accidentes_anual",
        "valor": benefits["annual_accidents"],
        "unidad": "S/ anual",
    }, {
        "indicador": "co2_anual",
        "valor": benefits["annual_co2"],
        "unidad": "S/ anual",
    }, {
        "indicador": "combustible_anual",
        "valor": benefits["annual_fuel"],
        "unidad": "S/ anual",
    }, {
        "indicador": "operacion_buses_anual",
        "valor": benefits["annual_bus_ops"],
        "unidad": "S/ anual",
    }, {
        "indicador": "npv_beneficios_30yr",
        "valor": cb_base["npv_benefits"],
        "unidad": "S/",
    }, {
        "indicador": "npv_costos_30yr",
        "valor": cb_base["npv_costs"],
        "unidad": "S/",
    }, {
        "indicador": "inversion_total",
        "valor": cb_base["total_investment"],
        "unidad": "S/",
    }, {
        "indicador": "bc_red_completa",
        "valor": cb_base["bc_ratio"],
        "unidad": "razón",
    }]).to_csv(PROCESSED_DATA / "bc_network.csv", index=False)

    # Per-line B/C
    print("\n--- B/C por línea ---")
    line_results = []
    total_km = sum(LINE_LENGTHS.values())
    for lid, km in LINE_LENGTHS.items():
        inv_km = TRAIN_COST_PER_KM if lid in ["TREN_ICA", "TREN_NORTE"] else METRO_COST_PER_KM
        inv = km * inv_km * 3.7
        pax_share = km / total_km
        line_benefits = benefits["npv_benefit_30yr"] * pax_share
        bc = line_benefits / inv if inv > 0 else 0
        line_results.append({
            "Línea": lid, "km": km, "Inversión S/": inv,
            "B/C": round(bc, 2)
        })
    bc_df = pd.DataFrame(line_results)
    print(bc_df.to_string(index=False))

    # 4. Land value
    print("\n[4/4] Valorización del suelo...")
    zones = gpd.read_file(str(PROCESSED_DATA / "zones.gpkg"), layer="zones")
    stations = gpd.read_file(str(PROCESSED_DATA / "stations.gpkg"), layer="stations")

    lv_results, total_gain = simulate_land_values(zones, stations)
    plot_land_value(lv_results, zones)

    # Save outputs
    congestion_df.to_csv(PROCESSED_DATA / "congestion_impact.csv", index=False)
    bc_df.to_csv(PROCESSED_DATA / "bc_per_line.csv", index=False)
    lv_results.to_csv(PROCESSED_DATA / "land_value_results.csv", index=False)

    # Summary chart
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    colors = PALETTE[:3]

    # Congestion
    ax = axes[0]
    ax.bar(["Base", "Red\nCompleta"],
           [c_base["hours_saved_total"], c_full["hours_saved_total"]],
           color=colors[:2], width=0.5)
    ax.set_ylabel("Horas ahorradas / día")
    ax.set_title("Reducción de tiempo de viaje")

    # B/C
    ax = axes[1]
    bc_vals = bc_df.sort_values("km")["B/C"].values
    bc_labels = bc_df.sort_values("km")["Línea"].values
    cols = [PALETTE[0] if v < 1 else PALETTE[3] for v in bc_vals]
    ax.barh(bc_labels, bc_vals, color=cols)
    ax.axvline(1.0, color=PALETTE[4], linestyle="--", alpha=0.5, label="Umbral rentabilidad")
    ax.set_xlabel("Relación B/C")
    ax.set_title("Costo-Beneficio por Línea")
    ax.legend(fontsize=8)

    # Land value
    ax = axes[2]
    top10 = lv_results.sort_values("Plusvalía_S/", ascending=False).head(10)
    ax.barh(top10["Distrito"].str[:15], top10["Plusvalía_S/"].values, color=colors[2], alpha=0.7)
    ax.set_xlabel("Plusvalía (S/)")
    ax.set_title("Top 10 distritos - plusvalía")

    fig.tight_layout()
    save_fig(fig, "phase3_summary.png")

    print("\n" + "=" * 60)
    print("FASE 3 completada.")
    return congestion_df, bc_df, lv_results


if __name__ == "__main__":
    run_phase3()
