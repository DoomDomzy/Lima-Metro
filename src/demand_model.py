import numpy as np
import pandas as pd
from config import PROCESSED_DATA, FIGURES
import matplotlib.pyplot as plt

VOT_PER_HOUR = 10.0
BETA_TIME = -0.10
BETA_COST = -0.01
MODE_CONSTANTS = {"car": 1.0, "bus": 0.0, "metro": 0.5, "train": -1.0}
SCALING_FACTOR = 0.45

def multinomial_logit_safe(utilities):
    u = utilities - np.max(utilities, axis=-1, keepdims=True)
    exp_u = np.exp(u)
    exp_u[~np.isfinite(exp_u)] = 0
    s = exp_u.sum(axis=-1, keepdims=True)
    s[s == 0] = 1
    return exp_u / s

def compute_mode_utilities(t_car, t_bus, t_metro, t_train):
    u_car = MODE_CONSTANTS["car"] + BETA_TIME * t_car + BETA_COST * (t_car * 0.05)
    u_bus = MODE_CONSTANTS["bus"] + BETA_TIME * t_bus + BETA_COST * 2.0
    u_metro = MODE_CONSTANTS["metro"] + BETA_TIME * t_metro
    u_train = np.full_like(u_car, -np.inf)
    valid = np.isfinite(t_train)
    u_train[valid] = MODE_CONSTANTS["train"] + BETA_TIME * t_train[valid]
    return {"car": u_car, "bus": u_bus, "metro": u_metro, "train": u_train}

def compute_mode_shares(utilities):
    modes = ["car", "bus", "metro", "train"]
    u_array = np.stack([utilities[m] for m in modes], axis=-1)
    orig = u_array.shape
    probs = multinomial_logit_safe(u_array.reshape(-1, 4)).reshape(orig)
    return {mode: probs[:, :, k] for k, mode in enumerate(modes)}

def doubly_constrained_gravity(O, D, cost, beta=0.02, max_iter=500, tol=1e-3):
    n = len(O)
    friction = np.exp(-beta * cost)
    np.fill_diagonal(friction, 0)
    friction[~np.isfinite(friction)] = 0

    total = O.sum()
    O = O.astype(float) / O.sum() * total
    D = D.astype(float) / D.sum() * total

    Bj = np.ones(n)

    for it in range(max_iter):
        Ai = np.zeros(n)
        for i in range(n):
            s = np.sum(Bj * D * friction[i, :])
            Ai[i] = 1.0 / s if s > 1e-15 else 0.0

        Bj_new = np.zeros(n)
        for j in range(n):
            s = np.sum(Ai * O * friction[:, j])
            Bj_new[j] = 1.0 / s if s > 1e-15 else 0.0

        T = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                T[i, j] = Ai[i] * Bj_new[j] * O[i] * D[j] * friction[i, j]

        O_calc = T.sum(axis=1)
        O_safe = np.where(O == 0, 1, O)
        diff = np.max(np.abs(O_calc - O) / O_safe)
        Bj = Bj_new

        if diff < tol:
            if it < 10:
                print(f"  Convergió en {it+1} iteraciones (diff={diff:.2e})")
            return T

    print(f"  Conv. parcial (diff={diff:.2e})")
    return T

def estimate_demand(travel_time_matrices, trip_generation_df, scenario="base"):
    metro_key = "metro_base" if scenario == "base" else "metro_full"
    label = "Base (L1+L2)" if scenario == "base" else "Red completa"

    O = trip_generation_df["trips_produced"].values.astype(float)
    D = trip_generation_df["trips_attracted"].values.astype(float)

    tt = {}
    for k in ["car", "bus"]:
        tt[k] = np.where(np.isfinite(travel_time_matrices[k]), travel_time_matrices[k], 999)
    tt["metro"] = np.where(np.isfinite(travel_time_matrices[metro_key]),
                           travel_time_matrices[metro_key], 999)

    train_raw = travel_time_matrices["train"]
    tt["train"] = np.where(np.isfinite(train_raw), train_raw, 999)

    print(f"\n>> {label}")
    print(f"   Tiempo metro promedio: {tt['metro'].mean():.1f} min")

    T_dist = {}
    betas = {"car": 0.020, "bus": 0.015, "metro": 0.018, "train": 0.008}
    print("   Distribución gravitatoria...")
    for mode in ["car", "bus", "metro", "train"]:
        T_dist[mode] = doubly_constrained_gravity(O, D, tt[mode], beta=betas[mode])

    u = compute_mode_utilities(tt["car"], tt["bus"], tt["metro"], tt["train"])
    shares = compute_mode_shares(u)

    T_metro = T_dist["metro"] * shares["metro"] * SCALING_FACTOR
    T_train = T_dist["train"] * shares["train"] * SCALING_FACTOR

    metro_pax = T_metro.sum()
    train_pax = T_train.sum()

    print(f"   Share metro: {shares['metro'].mean():.3f}, tren: {shares['train'].mean():.3f}")
    print(f"   Pax metro/día: {metro_pax:,.0f}, tren/día: {train_pax:,.0f}")

    return {"scenario": scenario, "metro_pax": metro_pax, "train_pax": train_pax,
            "total_public": metro_pax + train_pax, "T_metro": T_metro, "T_train": T_train,
            "shares": shares}

def compute_line_demand(T_metro_matrix, stations_gdf, zones_gdf, zone_assignment):
    stations_zone = stations_gdf.merge(
        zone_assignment[["station_name", "line_id", "zone_id"]],
        on=["station_name", "line_id"], how="left")

    z_ids = zones_gdf["zone_id"].tolist()
    n_zones = len(z_ids)

    station_counts = stations_zone.groupby(["zone_id", "line_id"]).size().reset_index(name="n_stations")

    line_zone_pax = np.zeros((len(lines := stations_zone["line_id"].unique()), n_zones))
    line_zone_pax_sum = np.zeros(len(lines))

    for li, line_id in enumerate(lines):
        line_zones = stations_zone[stations_zone["line_id"] == line_id]["zone_id"].unique()
        for zi in line_zones:
            if zi in z_ids:
                i = z_ids.index(zi)
                for zj in line_zones:
                    if zj in z_ids:
                        j = z_ids.index(zj)
                        if i < T_metro_matrix.shape[0] and j < T_metro_matrix.shape[1]:
                            val = T_metro_matrix[i, j]
                            if np.isfinite(val):
                                line_zone_pax_sum[li] += val

    results = pd.DataFrame({"line_id": lines, "daily_pax": line_zone_pax_sum})
    results = results.sort_values("daily_pax", ascending=False).reset_index(drop=True)
    results["daily_pax"] = results["daily_pax"].round(0).astype(int)
    return results


if __name__ == "__main__":
    import numpy as np
    if not hasattr(np, 'float_'):
        np.float_ = np.float64

    trip_gen = pd.read_csv(PROCESSED_DATA / "trip_generation.csv")
    matrices = {}
    for k in ["car", "bus", "metro_base", "metro_full", "train"]:
        m = pd.read_csv(PROCESSED_DATA / f"tt_{k}.csv", index_col=0)
        matrices[k] = m.values.astype(float)

    r_base = estimate_demand(matrices, trip_gen, scenario="base")
    r_full = estimate_demand(matrices, trip_gen, scenario="full")

    print(f"\n{'='*50}")
    print("RESUMEN FINAL")
    print(f"{'='*50}")
    print(f"Base:    {int(r_base['metro_pax']):>8,} metro  + {int(r_base['train_pax']):>8,} tren  = {int(r_base['total_public']):>8,} TP")
    print(f"Full:    {int(r_full['metro_pax']):>8,} metro  + {int(r_full['train_pax']):>8,} tren  = {int(r_full['total_public']):>8,} TP")
    print(f"Diferencia: {int(r_full['total_public'] - r_base['total_public']):>8,} pax/día adicionales")
