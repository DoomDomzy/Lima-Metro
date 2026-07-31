import numpy as np
import pandas as pd
from config import PROCESSED_DATA

VOT_PER_HOUR = 10.0
ACCIDENT_COST_PER_KM = 0.10
CO2_PER_CAR_KM = 0.25
SOCIAL_COST_CO2 = 0.05
FUEL_COST_PER_KM = 0.30
BUS_OP_COST_PER_PAX_KM = 0.08

METRO_COST_PER_KM = 150_000_000
TRAIN_COST_PER_KM = 50_000_000
PENUSD = 3.7
ANNUAL_OM_PCT = 0.03
YEARS = 30
DISCOUNT_RATE = 0.10

LINE_LENGTHS = {
    "L1": 35, "L2": 27, "L3": 25, "L4": 20, "L5": 18, "L6": 22,
    "TREN_ICA": 280, "TREN_NORTE": 200,
}

AVG_TRIP_KM = 12
BUS_TIME_SAVED_PER_TRIP_MIN = 40
CAR_TIME_SAVED_PER_TRIP_MIN = 20
BUS_ACCIDENT_COST_PER_KM = 0.15
DIVERSION_FROM_CAR = 0.25
DIVERSION_FROM_BUS = 0.55

def compute_social_benefits(metro_pax, train_pax, scenario_label):
    print(f"\n>> Costo-Beneficio Social - {scenario_label}")
    total_tp = metro_pax + train_pax

    from_car = total_tp * DIVERSION_FROM_CAR
    from_bus = total_tp * DIVERSION_FROM_BUS

    hours_saved_car = from_car * CAR_TIME_SAVED_PER_TRIP_MIN / 60
    hours_saved_bus = from_bus * BUS_TIME_SAVED_PER_TRIP_MIN / 60
    hours_saved = hours_saved_car + hours_saved_bus

    vehicle_km_saved = from_car * AVG_TRIP_KM
    bus_km_saved = from_bus * AVG_TRIP_KM

    annual_time = hours_saved * 365 * VOT_PER_HOUR
    annual_accidents = vehicle_km_saved * 365 * ACCIDENT_COST_PER_KM
    annual_co2 = vehicle_km_saved * 365 * CO2_PER_CAR_KM * SOCIAL_COST_CO2
    annual_fuel = vehicle_km_saved * 365 * FUEL_COST_PER_KM
    annual_bus_ops = bus_km_saved * 365 * BUS_OP_COST_PER_PAX_KM
    annual_total = annual_time + annual_accidents + annual_co2 + annual_fuel + annual_bus_ops

    print(f"  Horas ahorradas/día: {hours_saved:,.0f} (auto: {hours_saved_car:,.0f}, bus: {hours_saved_bus:,.0f})")
    print(f"  Ahorro tiempo anual: S/{annual_time:,.0f}")
    print(f"  Reducción accidentes: S/{annual_accidents:,.0f}")
    print(f"  Reducción CO2: S/{annual_co2:,.0f}")
    print(f"  Ahorro combustible: S/{annual_fuel:,.0f}")
    print(f"  Ahorro operación buses: S/{annual_bus_ops:,.0f}")
    print(f"  Beneficio social anual total: S/{annual_total:,.0f}")

    npv = sum(annual_total / (1 + DISCOUNT_RATE) ** t for t in range(1, YEARS + 1))
    print(f"  VAN Beneficios (30 años, {DISCOUNT_RATE*100:.0f}%): S/{npv:,.0f}")

    return {
        "annual_total": annual_total,
        "npv_benefit_30yr": npv,
        "annual_time": annual_time,
        "annual_accidents": annual_accidents,
        "annual_co2": annual_co2,
        "annual_fuel": annual_fuel,
        "annual_bus_ops": annual_bus_ops,
        "hours_saved": hours_saved,
        "vehicle_km_saved": vehicle_km_saved,
    }

def compute_investment_cost(line_ids=None):
    total = 0
    details = []
    for lid in (line_ids or LINE_LENGTHS):
        km = LINE_LENGTHS[lid]
        cost_usd = km * (TRAIN_COST_PER_KM if lid in ["TREN_ICA", "TREN_NORTE"] else METRO_COST_PER_KM)
        cost_soles = cost_usd * PENUSD
        total += cost_soles
        details.append({"line": lid, "km": km, "cost_USD_M": cost_usd / 1e6, "cost_SOLES_M": cost_soles / 1e6})
    return total, pd.DataFrame(details)

def compute_cost_benefit(social_benefits, total_investment, label):
    print(f"\n>> Relación B/C - {label}")
    npv_b = social_benefits["npv_benefit_30yr"]
    annual_om = total_investment * ANNUAL_OM_PCT
    npv_om = sum(annual_om / (1 + DISCOUNT_RATE) ** t for t in range(1, YEARS + 1))
    npv_costs = total_investment + npv_om
    bc = npv_b / npv_costs if npv_costs > 0 else 0

    print(f"  Inversión total: S/{total_investment:,.0f} (US${total_investment/PENUSD:,.0f})")
    print(f"  O&M (VAN): S/{npv_om:,.0f}")
    print(f"  Costos totales (VAN): S/{npv_costs:,.0f}")
    print(f"  Beneficios (VAN): S/{npv_b:,.0f}")
    print(f"  Relación B/C: {bc:.2f}")

    return {
        "label": label, "bc_ratio": bc,
        "total_investment": total_investment,
        "npv_benefits": npv_b, "npv_costs": npv_costs,
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

    r_full = estimate_demand(matrices, trip_gen, "full")
    benefits = compute_social_benefits(r_full["metro_pax"], r_full["train_pax"], "Red Completa")
    total_inv, inv_df = compute_investment_cost()
    compute_cost_benefit(benefits, total_inv, "Red Completa")
    print(f"\nInversión por línea:\n{inv_df.to_string(index=False)}")
