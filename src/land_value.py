import numpy as np
import pandas as pd
import geopandas as gpd
from config import PROCESSED_DATA, CRS_PROJECTED, BUFFER_METERS
import matplotlib.pyplot as plt

from viz_style import configure_matplotlib, save_fig, palette_colormap, TEXT

BASE_PRICE_PER_M2 = 8000
PREMIUM_NEAR_STATION = 0.12
PREMIUM_DECAY = 0.02

DISTRICT_PRICE_INDEX = {
    "Miraflores / San Isidro": 2.5,
    "San Borja / Surco / Surquillo": 1.8,
    "Jesús María / Magdalena": 1.4,
    "La Molina / Chaclacayo / Lurigancho": 1.5,
    "Barranco / Chorrillos / San Miguel": 1.2,
    "Lima (Cercado)": 1.0,
    "Breña / Pueblo Libre": 1.1,
    "La Victoria": 0.9,
    "San Juan de Lurigancho": 0.7,
    "Comas": 0.6,
    "Los Olivos": 0.7,
    "San Martín de Porres": 0.7,
    "Independencia": 0.7,
    "Rímac": 0.8,
    "Santa Anita": 0.7,
    "Ate": 0.6,
    "El Agustino": 0.7,
    "San Juan de Miraflores": 0.6,
    "Villa María del Triunfo": 0.5,
    "Villa El Salvador": 0.5,
    "Callao (Cercado / Ventanilla)": 0.7,
    "Callao (Bellavista / Carmen / La Perla)": 0.8,
    "Lurín / Pachacámac / Sur costero": 0.5,
    "Puente Piedra / Carabayllo / Ancón": 0.4,
    "Chancay / Huacho (Norte)": 0.3,
    "Cañete / Chincha (Sur)": 0.3,
    "Ica": 0.4,
}

def simulate_land_values(zones_gdf, stations_gdf):
    print("\n>> Valorización del Suelo")

    zones_proj = zones_gdf.to_crs(CRS_PROJECTED)
    stations_proj = stations_gdf.to_crs(CRS_PROJECTED)

    zones_proj["dist_to_nearest_station_m"] = zones_proj.geometry.apply(
        lambda pt: stations_proj.distance(pt).min()
    )

    unmapped_districts = set(zones_proj["district"].unique()) - set(DISTRICT_PRICE_INDEX.keys())
    if unmapped_districts:
        raise ValueError(
            f"Distritos de zona sin índice de precio definido: {sorted(unmapped_districts)}"
        )
    zones_proj["price_index"] = zones_proj["district"].map(DISTRICT_PRICE_INDEX)
    zones_proj["base_price"] = BASE_PRICE_PER_M2 * zones_proj["price_index"]

    zones_proj["station_premium"] = np.where(
        zones_proj["dist_to_nearest_station_m"] < BUFFER_METERS,
        PREMIUM_NEAR_STATION * (1 - zones_proj["dist_to_nearest_station_m"] / (BUFFER_METERS * 3)),
        0
    )
    zones_proj["station_premium"] = np.maximum(zones_proj["station_premium"], 0)

    zones_proj["price_with_metro"] = zones_proj["base_price"] * (1 + zones_proj["station_premium"])
    zones_proj["land_value_gain"] = zones_proj["price_with_metro"] - zones_proj["base_price"]

    total_gain = (zones_proj["land_value_gain"] * zones_proj["population"] * 0.3).sum()

    print(f"  Precio base promedio/m²: S/{zones_proj['base_price'].mean():,.0f}")
    print(f"  Precio con metro promedio/m²: S/{zones_proj['price_with_metro'].mean():,.0f}")
    print(f"  Prima promedio por proximidad: {zones_proj['station_premium'].mean()*100:.1f}%")
    print(f"  Plusvalía total estimada (30% viviendas): S/{total_gain:,.0f}")
    print(f"  Plusvalía total estimada: ${total_gain/3.7:,.0f}")

    results = zones_proj[[
        "zone_id", "district", "population",
        "dist_to_nearest_station_m", "base_price",
        "station_premium", "price_with_metro", "land_value_gain"
    ]].copy()
    results.columns = [
        "Zona", "Distrito", "Población",
        "Dist_estación_(m)", "Precio_base_S/",
        "Prima_proximidad", "Precio_con_metro_S/", "Plusvalía_S/"
    ]

    return results, total_gain


def plot_land_value(results, zones_gdf):
    configure_matplotlib()
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    zones_proj = zones_gdf.to_crs(CRS_PROJECTED)
    zones_plot = zones_proj.copy()
    zones_plot = zones_plot.merge(
        results[["Zona", "Precio_con_metro_S/", "Precio_base_S/"]],
        left_on="zone_id", right_on="Zona"
    )

    cmap = palette_colormap()
    sc1 = axes[0].scatter(
        zones_plot.geometry.x, zones_plot.geometry.y,
        c=zones_plot["Precio_base_S/"], cmap=cmap, s=80, alpha=0.8,
        edgecolors=TEXT, linewidths=0.4
    )
    axes[0].set_title("Precio Base (sin metro)")
    plt.colorbar(sc1, ax=axes[0], label="S//m²")

    sc2 = axes[1].scatter(
        zones_plot.geometry.x, zones_plot.geometry.y,
        c=zones_plot["Precio_con_metro_S/"], cmap=cmap, s=80, alpha=0.8,
        edgecolors=TEXT, linewidths=0.4
    )
    axes[1].set_title("Precio con Red Metro")
    plt.colorbar(sc2, ax=axes[1], label="S//m²")

    for ax in axes:
        ax.set_xlabel("X (UTM)")
        ax.set_ylabel("Y (UTM)")
        ax.grid(True, alpha=0.3)
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)

    fig.tight_layout()
    save_fig(fig, "land_value_impact.png")


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    zones = gpd.read_file(str(PROCESSED_DATA / "zones.gpkg"), layer="zones")
    stations = gpd.read_file(str(PROCESSED_DATA / "stations.gpkg"), layer="stations")

    results, total_gain = simulate_land_values(zones, stations)
    plot_land_value(results, zones)

    print(f"\nZonas con mayor plusvalía:")
    print(results.sort_values("Plusvalía_S/", ascending=False).head(10).to_string(index=False))
