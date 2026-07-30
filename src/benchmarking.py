import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from config import PROCESSED_DATA, FIGURES

BENCHMARK_DATA = [
    {
        "city": "Medellín",
        "country": "Colombia",
        "metro_system": "Metro de Medellín",
        "population_M": 4.0,
        "metro_km": 31.3,
        "daily_pax_K": 500,
        "pax_per_km": 15974,
        "lines": 2,
        "cost_per_km_USD_M": 60,
        "bc_ratio": 1.4,
        "year_opened": 1995,
        "population_density_corridor": 8500,
        "fare_integration": "Full",
        "bus_feeding": "Extensive",
        "notes": "Pionero LATAM, integración tarifaria completa, urbanismo social",
    },
    {
        "city": "Santiago",
        "country": "Chile",
        "metro_system": "Metro de Santiago",
        "population_M": 7.0,
        "metro_km": 149,
        "daily_pax_K": 2500,
        "pax_per_km": 16779,
        "lines": 7,
        "cost_per_km_USD_M": 120,
        "bc_ratio": 1.2,
        "year_opened": 1975,
        "population_density_corridor": 7000,
        "fare_integration": "Full (Red)",
        "bus_feeding": "Full integration",
        "notes": "Red más extensa de Sudamérica, expansión continua",
    },
    {
        "city": "Ciudad de México",
        "country": "México",
        "metro_system": "Metro CDMX",
        "population_M": 22.0,
        "metro_km": 226,
        "daily_pax_K": 4500,
        "pax_per_km": 19912,
        "lines": 12,
        "cost_per_km_USD_M": 80,
        "bc_ratio": 1.8,
        "year_opened": 1969,
        "population_density_corridor": 12000,
        "fare_integration": "Partial (STC, Metrobús, Tren Ligero)",
        "bus_feeding": "Moderate",
        "notes": "Alta densidad de demanda, subsidio estatal significativo",
    },
    {
        "city": "Bogotá",
        "country": "Colombia",
        "metro_system": "TransMilenio (BRT) + Metro (2028)",
        "population_M": 8.0,
        "metro_km": 114,
        "daily_pax_K": 2400,
        "pax_per_km": 21053,
        "lines": 12,
        "cost_per_km_USD_M": 15,
        "bc_ratio": 2.1,
        "year_opened": 2000,
        "population_density_corridor": 10000,
        "fare_integration": "Full (SITP)",
        "bus_feeding": "Extensive",
        "notes": "BRT más exitoso del mundo, metro en construcción (L1 2028)",
    },
    {
        "city": "Lima (actual)",
        "country": "Perú",
        "metro_system": "Línea 1 + L2 parcial",
        "population_M": 11.0,
        "metro_km": 42,
        "daily_pax_K": 800,
        "pax_per_km": 19048,
        "lines": 2,
        "cost_per_km_USD_M": 85,
        "bc_ratio": 0.9,
        "year_opened": 2011,
        "population_density_corridor": 9500,
        "fare_integration": "None",
        "bus_feeding": "Limited",
        "notes": "Sin integración tarifaria, demanda alta en L1",
    },
    {
        "city": "Lima (propuesta)",
        "country": "Perú",
        "metro_system": "Red 6L + 2 trenes",
        "population_M": 11.0,
        "metro_km": 627,
        "daily_pax_K": 1637,
        "pax_per_km": 2611,
        "lines": 8,
        "cost_per_km_USD_M": 73,
        "bc_ratio": 0.16,
        "year_opened": 2030,
        "population_density_corridor": 6000,
        "fare_integration": "Proposed",
        "bus_feeding": "Proposed",
        "notes": "Nuestra estimación: red extensa pero baja densidad de demanda",
    },
]


def build_benchmark_df():
    return pd.DataFrame(BENCHMARK_DATA)

def plot_ridership_intensity(benchmark_df):
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#2E86AB", "#A23B72", "#F18F01", "#4CAF50", "#E91E63", "#9C27B0"]
    exclude = ["Lima (propuesta)"]
    plot_df = benchmark_df[~benchmark_df["city"].isin(exclude)]
    cities_plot = plot_df["city"].tolist() + ["Lima (propuesta)"]
    colors_final = colors[:len(plot_df)] + ["red"]

    vals = plot_df["pax_per_km"].tolist() + [benchmark_df[benchmark_df["city"]=="Lima (propuesta)"]["pax_per_km"].iloc[0]]
    labels = plot_df["city"].tolist() + ["Lima\n(propuesta)"]

    bars = ax.bar(range(len(vals)), vals, color=colors_final, alpha=0.8, width=0.6)
    for i, (bar, v) in enumerate(zip(bars, vals)):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 300,
                f"{v:,.0f}", ha="center", fontsize=8, fontweight="bold" if i == len(vals)-1 else "normal")
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Pasajeros / km / día")
    ax.set_title("Intensidad de Uso: Pasajeros por km por Día")
    ax.axhline(y=benchmark_df[benchmark_df["city"]=="Lima (actual)"]["pax_per_km"].iloc[0],
               color="#E91E63", linestyle="--", alpha=0.5, label="Lima actual")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(str(FIGURES / "benchmark_intensity.png"), dpi=150)
    print(f"  {FIGURES / 'benchmark_intensity.png'}")
    plt.close()

def plot_bc_comparison(benchmark_df):
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#2E86AB", "#A23B72", "#F18F01", "#4CAF50", "#E91E63", "red"]
    vals = benchmark_df["bc_ratio"].tolist()
    labels = benchmark_df["city"].tolist()
    bars = ax.bar(range(len(vals)), vals, color=colors, alpha=0.8, width=0.6)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f"{v:.2f}", ha="center", fontsize=9, fontweight="bold")
    ax.axhline(y=1.0, color="red", linestyle="--", alpha=0.5, label="Umbral rentabilidad (B/C=1)")
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Relación Beneficio/Costo")
    ax.set_title("Comparación de Relación Beneficio/Costo")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(str(FIGURES / "benchmark_bc.png"), dpi=150)
    print(f"  {FIGURES / 'benchmark_bc.png'}")
    plt.close()

def plot_cost_per_km(benchmark_df):
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#2E86AB", "#A23B72", "#F18F01", "#4CAF50", "#E91E63", "red"]
    plot_df = benchmark_df[benchmark_df["city"] != "Bogotá"]
    vals = plot_df["cost_per_km_USD_M"].tolist()
    vals.append(benchmark_df[benchmark_df["city"]=="Bogotá"]["cost_per_km_USD_M"].iloc[0])
    labels = plot_df["city"].tolist() + ["Bogotá\n(BRT)"]
    cols = colors[:len(plot_df)] + ["#4CAF50"]
    bars = ax.bar(range(len(vals)), vals, color=cols, alpha=0.8, width=0.6)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f"${v:.0f}M", ha="center", fontsize=8)
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Costo por km (USD millones)")
    ax.set_title("Costo de Construcción por km")
    fig.tight_layout()
    fig.savefig(str(FIGURES / "benchmark_cost_per_km.png"), dpi=150)
    print(f"  {FIGURES / 'benchmark_cost_per_km.png'}")
    plt.close()

def plot_scatter(benchmark_df):
    fig, ax = plt.subplots(figsize=(10, 7))
    plot_df = benchmark_df[benchmark_df["city"] != "Lima (propuesta)"]
    colors = ["#2E86AB", "#A23B72", "#F18F01", "#4CAF50", "#E91E63"]

    for i, (_, row) in enumerate(plot_df.iterrows()):
        size = row["daily_pax_K"] / 100
        ax.scatter(row["population_M"], row["pax_per_km"], s=size*30,
                   c=colors[i], alpha=0.7, edgecolors="black", linewidth=0.5,
                   label=f"{row['city']} ({row['daily_pax_K']:.0f}K pax/d)")

    lp = benchmark_df[benchmark_df["city"] == "Lima (propuesta)"].iloc[0]
    ax.scatter(lp["population_M"], lp["pax_per_km"], s=lp["daily_pax_K"]/100*30,
               c="red", alpha=0.7, edgecolors="black", linewidth=1.5,
               marker="s", label=f"Lima propuesta ({lp['daily_pax_K']:.0f}K pax/d)")

    ax.set_xlabel("Población metropolitana (millones)")
    ax.set_ylabel("Pasajeros / km / día")
    ax.set_title("Benchmark: Población vs Intensidad de Uso")
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(str(FIGURES / "benchmark_scatter.png"), dpi=150)
    print(f"  {FIGURES / 'benchmark_scatter.png'}")
    plt.close()


def print_benchmark_report(benchmark_df):
    print("\n" + "=" * 70)
    print("INFORME DE BENCHMARKING INTERNACIONAL")
    print("=" * 70)

    cols = ["city", "population_M", "metro_km", "daily_pax_K", "pax_per_km",
            "cost_per_km_USD_M", "bc_ratio", "fare_integration"]
    report = benchmark_df[cols].copy()
    report.columns = ["Ciudad", "Pob.(M)", "km", "Pax/día(K)",
                       "Pax/km/día", "Costo/km(US$M)", "B/C", "Integración"]
    print("\n")
    print(report.to_string(index=False))

    print("\n--- Factores de éxito identificados ---")
    success_factors = [
        ("Integración tarifaria", "Todas las ciudades exitosas tienen un sistema único de pago (tarjeta multi-modal). Lima carece de esto.", 5),
        ("Alimentación con buses", "Medellín y Bogotá tienen rutas alimentadoras extensas. Santiago integró su Red. Lima tiene alimentación limitada.", 5),
        ("Alta densidad de corredor", "CDMX y Bogotá tienen >10,000 hab/km² en sus corredores. La red propuesta de Lima tendría ~6,000.", 4),
        ("Construcción por fases", "Santiago y Medellín expandieron gradualmente. La propuesta de 8 líneas simultáneas sería la más ambiciosa de LATAM.", 5),
        ("Urbanismo social", "Medellín combinó metro+teleférico+urbanismo para reducir desigualdad (ej. Comuna 13).", 3),
        ("Transparencia", "Proyectos con sobrecostos >50% son comunes en LATAM. Las líneas 1 y 2 de Lima tuvieron retrasos significativos.", 4),
    ]
    for name, desc, importance in success_factors:
        stars = "★" * importance + "☆" * (5 - importance)
        print(f"\n  [{stars}] {name}")
        print(f"       {desc}")

    print("\n--- Posicionamiento de Lima ---")
    actual = benchmark_df[benchmark_df["city"] == "Lima (actual)"].iloc[0]
    propuesta = benchmark_df[benchmark_df["city"] == "Lima (propuesta)"].iloc[0]

    print(f"\n  Situación actual:")
    print(f"    - {actual['daily_pax_K']:.0f}K pax/día en {actual['metro_km']} km ({actual['pax_per_km']:.0f} pax/km/día)")
    print(f"    - Intensidad de uso comparable a CDMX y superior a Santiago")
    print(f"    - B/C estimado: {actual['bc_ratio']:.1f}")
    print(f"    - Integración tarifaria: {actual['fare_integration']}")

    print(f"\n  Escenario propuesto (6L + 2 trenes):")
    print(f"    - {propuesta['daily_pax_K']:.0f}K pax/día en {propuesta['metro_km']} km ({propuesta['pax_per_km']:.0f} pax/km/día)")
    print(f"    - La red sería la 2da más extensa de LATAM (después de CDMX)")
    print(f"    - Pero la intensidad de uso caería a {propuesta['pax_per_km']:.0f} pax/km/día (menos que cualquier comparable)")
    print(f"    - B/C: {propuesta['bc_ratio']:.2f} (por debajo del umbral de rentabilidad)")

    print(f"\n  Recomendación:")
    print(f"    - Priorizar líneas de alta densidad (L3 eje norte-sur, tren Lima-Ica)")
    print(f"    - Implementar integración tarifaria ANTES de expandir la red")
    print(f"    - Acompañar con urbanismo social (modelo Medellín)")
    print(f"    - Construcción por fases (no 8 proyectos simultáneos)")


if __name__ == "__main__":
    df = build_benchmark_df()
    print_benchmark_report(df)
    plot_ridership_intensity(df)
    plot_bc_comparison(df)
    plot_cost_per_km(df)
    plot_scatter(df)
    print("\nBenchmarking completado. Gráficos guardados.")
