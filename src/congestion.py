import numpy as np
import pandas as pd
from config import PROCESSED_DATA

CAR_OCCUPANCY = 1.5
PEAK_HOUR_FACTOR = 0.10
AVG_TRIP_LENGTH_KM = 12
AVG_TRIP_TIME_CAR_MIN = 60
AVG_TRIP_TIME_BUS_MIN = 80
AVG_TRIP_TIME_METRO_MIN = 40

DIVERSION_FROM_CAR = 0.25
DIVERSION_FROM_BUS = 0.55
DIVERSION_NEW_INDUCED = 0.20

def compute_congestion_impact(metro_pax, train_pax, scenario_label):
    print(f"\n>> Congestión - {scenario_label}")

    total_tp = metro_pax + train_pax
    from_car = total_tp * DIVERSION_FROM_CAR
    from_bus = total_tp * DIVERSION_FROM_BUS
    induced = total_tp * DIVERSION_NEW_INDUCED

    time_saved_car = from_car * (AVG_TRIP_TIME_CAR_MIN - AVG_TRIP_TIME_METRO_MIN) / 60
    time_saved_bus = from_bus * (AVG_TRIP_TIME_BUS_MIN - AVG_TRIP_TIME_METRO_MIN) / 60
    hours_saved = time_saved_car + time_saved_bus

    vehicle_km_saved = from_car * AVG_TRIP_LENGTH_KM

    vehicles_removed = from_car / 2.0
    peak_vehicles = from_car * PEAK_HOUR_FACTOR / CAR_OCCUPANCY

    print(f"  Pasajeros TP/día: {total_tp:,.0f}")
    print(f"  Desde auto: {from_car:,.0f} ({DIVERSION_FROM_CAR*100:.0f}%)")
    print(f"  Desde bus: {from_bus:,.0f} ({DIVERSION_FROM_BUS*100:.0f}%)")
    print(f"  Inducidos: {induced:,.0f} ({DIVERSION_NEW_INDUCED*100:.0f}%)")
    print(f"  Horas ahorradas/día: {hours_saved:,.0f}")
    print(f"  Vehículos-km evitados/día: {vehicle_km_saved:,.0f}")
    print(f"  Vehículos retirados: {vehicles_removed:,.0f}")

    return {
        "switched_trips": from_car,
        "hours_saved_total": hours_saved,
        "vehicle_km_saved": vehicle_km_saved,
        "vehicles_removed": vehicles_removed,
        "peak_vehicles": peak_vehicles,
    }


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from demand_model import estimate_demand

    trip_gen = pd.read_csv(PROCESSED_DATA / "trip_generation.csv")
    matrices = {}
    for k in ["car", "bus", "metro_base", "metro_full", "train"]:
        m = pd.read_csv(PROCESSED_DATA / f"tt_{k}.csv", index_col=0)
        matrices[k] = m.values.astype(float)

    r_base = estimate_demand(matrices, trip_gen, "base")
    r_full = estimate_demand(matrices, trip_gen, "full")

    c_base = compute_congestion_impact(r_base["metro_pax"], r_base["train_pax"], "Base")
    c_full = compute_congestion_impact(r_full["metro_pax"], r_full["train_pax"], "Red Completa")
