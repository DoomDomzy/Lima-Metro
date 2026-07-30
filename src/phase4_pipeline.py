import numpy as np
if not hasattr(np, 'float_'):
    np.float_ = np.float64

import sys, os, warnings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings("ignore")

from config import PROCESSED_DATA, FIGURES
import matplotlib
matplotlib.use("Agg")

from benchmarking import (
    build_benchmark_df, print_benchmark_report,
    plot_ridership_intensity, plot_bc_comparison,
    plot_cost_per_km, plot_scatter
)


def run_phase4():
    print("=" * 60)
    print("FASE 4: Benchmarking Internacional")
    print("=" * 60)

    benchmark_df = build_benchmark_df()
    benchmark_df.to_csv(PROCESSED_DATA / "benchmark_data.csv", index=False)
    print(f"Datos guardados: {len(benchmark_df)} ciudades")

    print("\n[1/4] Generando reporte...")
    print_benchmark_report(benchmark_df)

    print("\n[2/4] Gráfico: Intensidad de uso...")
    plot_ridership_intensity(benchmark_df)

    print("[3/4] Gráficos: B/C y costo/km...")
    plot_bc_comparison(benchmark_df)
    plot_cost_per_km(benchmark_df)

    print("[4/4] Gráfico: Dispersión población vs uso...")
    plot_scatter(benchmark_df)

    print("\n" + "=" * 60)
    print("FASE 4 completada.")
    print("Gráficos en:", FIGURES)
    return benchmark_df


if __name__ == "__main__":
    run_phase4()
