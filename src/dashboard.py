import numpy as np
if not hasattr(np, 'float_'):
    np.float_ = np.float64

import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import os, sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PROCESSED_DATA, FIGURES, CRS_PROJECTED

st.set_page_config(
    page_title="Red Ferroviaria Lima — Dashboard",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🚇 Evaluación de la Red Ferroviaria Ampliada de Lima")
st.markdown("""
Impacto potencial de las nuevas líneas de metro y trenes de cercanías (Propuesta Fujimori 2026)
en una megaciudad de 11+ millones de habitantes.
""")

sidebar = st.sidebar
sidebar.header("Navegación")
page = sidebar.radio("Ir a:", [
    "📊 Resumen General",
    "🗺️ Red Propuesta",
    "📈 Demanda",
    "🚦 Congestión",
    "💰 Costo-Beneficio",
    "🏠 Plusvalía",
    "🌎 Benchmarking",
])

# ───────────────────────────────────────────────
def load_data():
    data = {}
    try:
        data["stations"] = gpd.read_file(str(PROCESSED_DATA / "stations.gpkg"), layer="stations")
        data["lines"] = gpd.read_file(str(PROCESSED_DATA / "stations.gpkg"), layer="lines")
        data["zones"] = gpd.read_file(str(PROCESSED_DATA / "zones.gpkg"), layer="zones")
        data["congestion"] = pd.read_csv(str(PROCESSED_DATA / "congestion_impact.csv"))
        data["bc"] = pd.read_csv(str(PROCESSED_DATA / "bc_per_line.csv"))
        data["bc_network"] = pd.read_csv(str(PROCESSED_DATA / "bc_network.csv"))
        data["land_value"] = pd.read_csv(str(PROCESSED_DATA / "land_value_results.csv"))
        data["benchmark"] = pd.read_csv(str(PROCESSED_DATA / "benchmark_data.csv"))
        data["demand"] = pd.read_csv(str(PROCESSED_DATA / "demand_comparison.csv"))
        data["l1_validation"] = pd.read_csv(str(PROCESSED_DATA / "l1_validation.csv"))
        data["trip_gen"] = pd.read_csv(str(PROCESSED_DATA / "trip_generation.csv"))
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None
    return data

data = load_data()
if data is None:
    st.stop()

# ───────────────────────────────────────────────
# PÁGINA: RESUMEN GENERAL
# ───────────────────────────────────────────────
if page == "📊 Resumen General":
    st.header("Resumen General")

    col1, col2, col3, col4 = st.columns(4)
    demand = data["demand"]
    congestion = data["congestion"]

    # Fix invalid literal issue - get the right row
    full_row = demand.iloc[1] if len(demand) > 1 else demand.iloc[0]

    def safe_int(val):
        try:
            return int(float(str(val).replace(",", "").replace(" ", "")))
        except:
            return 0

    metro_pax = safe_int(full_row.get("Metro (pax/día)", full_row.get("Metro", 0)))
    total_tp = safe_int(full_row.get("Total TP (pax/día)", full_row.get("Total_TP", 0)))

    col1.metric("Pasajeros Metro/día", f"{metro_pax:,}")
    col2.metric("Total TP/día", f"{total_tp:,}")

    vehicles_removed = safe_int(congestion.loc[congestion["Métrica"].str.contains("retirados", case=False, na=False), "Red Completa"].values[0]) if len(congestion) > 0 else 0
    col3.metric("Vehículos retirados", f"{vehicles_removed:,}")

    bc_data = data["bc_network"]
    bc_net_val = float(bc_data.loc[bc_data["indicador"] == "bc_red_completa", "valor"].iloc[0]) if len(bc_data) > 0 else 0
    col4.metric("B/C red completa", f"{bc_net_val:.2f}")

    st.subheader("Estaciones y Líneas")
    stations = data["stations"]
    lines = data["lines"]
    col1, col2 = st.columns(2)
    col1.write(f"**{len(stations)}** estaciones totales")
    col1.write(f"  - {len(stations[stations['status']=='existing'])} existentes (L1)")
    col1.write(f"  - {len(stations[stations['status']=='partial'])} parciales (L2)")
    col1.write(f"  - {len(stations[stations['status']=='proposed'])} propuestas")
    col2.write(f"**{len(lines)}** líneas")
    for _, l in lines.iterrows():
        col2.write(f"  - {l['line_name']} ({l['status']})")

    st.subheader("Resultados Clave por Fase")
    stations = data["stations"]
    buffers = stations.copy()
    buffers["geometry"] = stations.geometry.buffer(800)
    coverage_km2 = buffers.geometry.union_all().area / 1e6

    full_metro = safe_int(full_row.get("Metro (pax/día)", full_row.get("Metro", 0)))
    full_total = safe_int(full_row.get("Total TP (pax/día)", full_row.get("Total_TP", 0)))
    hours_saved = safe_int(congestion.loc[
        congestion["Métrica"].str.contains("Horas ahorradas", case=False, na=False),
        "Red Completa"].values[0]) if len(congestion) > 0 else 0
    veh_removed = safe_int(congestion.loc[
        congestion["Métrica"].str.contains("retirados", case=False, na=False),
        "Red Completa"].values[0]) if len(congestion) > 0 else 0
    bc_net = data["bc_network"]
    bc_ratio = float(bc_net.loc[bc_net["indicador"] == "bc_red_completa", "valor"].iloc[0]) if len(bc_net) > 0 else 0
    l1_val = data["l1_validation"]
    l1_pct = float(l1_val["precision_pct"].iloc[0]) if len(l1_val) > 0 else float("nan")
    bench = data["benchmark"]
    lima_act = bench.loc[bench["city"] == "Lima (actual)", "pax_per_km"].iloc[0] if len(bench) > 0 else 0
    lima_prop = bench.loc[bench["city"] == "Lima (propuesta)", "pax_per_km"].iloc[0] if len(bench) > 0 else 0

    st.markdown(f"""
    | Fase | Hallazgo Principal |
    |------|-------------------|
    | **Fase 1 — GIS** | {len(stations)} estaciones, {coverage_km2:.0f} km² de cobertura (buffers 800m) |
    | **Fase 2 — Demanda** | {full_metro:,} pax/día metro (red completa), {full_total:,} TP/día — validación L1: {l1_pct:.1f}% |
    | **Fase 3 — Impactos** | {hours_saved:,} horas/día ahorradas, {veh_removed:,} vehículos retirados, B/C={bc_ratio:.2f} |
    | **Fase 4 — Benchmarking** | Lima actual: {lima_act:,} pax/km/día; red propuesta: {lima_prop:,} pax/km/día |
    """)

# ───────────────────────────────────────────────
# PÁGINA: RED PROPUESTA
# ───────────────────────────────────────────────
elif page == "🗺️ Red Propuesta":
    st.header("Red Ferroviaria Propuesta")

    st.subheader("Mapa de la Red")
    map_path = FIGURES / "red_ferroviaria_propuesta.png"
    if map_path.exists():
        st.image(str(map_path), use_container_width=True)
    else:
        st.warning("Mapa no disponible. Ejecute phase1_pipeline.py primero.")

    st.subheader("Cobertura de Estaciones (Buffers 800m)")
    buf_path = FIGURES / "buffer_coverage.png"
    if buf_path.exists():
        st.image(str(buf_path), use_container_width=True)

    st.subheader("Detalle de Líneas Propuestas")
    lines_info = pd.DataFrame([
        {"Línea": "L3", "Eje": "Comas → San Juan de Miraflores", "Estaciones": 9, "Tipo": "Norte-Sur (oeste)"},
        {"Línea": "L4", "Eje": "Av. Javier Prado → Aeropuerto → Ate", "Estaciones": 4, "Tipo": "Anillo vial"},
        {"Línea": "L5", "Eje": "Benavides → Panamericana Sur", "Estaciones": 4, "Tipo": "Sur"},
        {"Línea": "L6", "Eje": "Conexión conos este y norte", "Estaciones": 5, "Tipo": "Circunvalación"},
        {"Tren Ica": "Lima → Ica (280 km, 1.5h)", "Eje": "Panamericana Sur", "Estaciones": 9, "Tipo": "Interurbano"},
        {"Tren Norte": "Lima → Chancay → Barranca", "Eje": "Panamericana Norte", "Estaciones": 6, "Tipo": "Interurbano"},
    ])
    st.dataframe(lines_info, use_container_width=True)

# ───────────────────────────────────────────────
# PÁGINA: DEMANDA
# ───────────────────────────────────────────────
elif page == "📈 Demanda":
    st.header("Estimación de Demanda")

    col1, col2 = st.columns(2)
    col1.subheader("Comparación de Escenarios")
    demand_df = data["demand"]
    st.dataframe(demand_df, use_container_width=True)

    demand_fig = FIGURES / "demand_comparison.png"
    if demand_fig.exists():
        col2.image(str(demand_fig), use_container_width=True)
    else:
        col2.warning("Gráfico no disponible")

    st.subheader("Zonas de Transporte")
    trip_gen = data["trip_gen"]
    st.dataframe(trip_gen.style.format({
        "population": "{:,.0f}", "employment": "{:,.0f}",
        "trips_produced": "{:,.0f}", "trips_attracted": "{:,.0f}"
    }), use_container_width=True, height=400)

    st.markdown(f"""
    **Total viajes generados:** {trip_gen['trips_produced'].sum():,.0f} viajes/día
    **Población cubierta:** {trip_gen['population'].sum():,.0f} hab
    **Empleo cubierto:** {trip_gen['employment'].sum():,.0f} puestos
    """)

# ───────────────────────────────────────────────
# PÁGINA: CONGESTIÓN
# ───────────────────────────────────────────────
elif page == "🚦 Congestión":
    st.header("Impacto en la Congestión Vehicular")

    congestion = data["congestion"]
    st.dataframe(congestion, use_container_width=True)

    st.subheader("Interpretación")
    full_row = congestion.set_index("Métrica")["Red Completa"]

    st.markdown(f"""
    - **{int(full_row.get('Horas ahorradas/día', 0)):,}** horas ahorradas cada día
    - **{int(full_row.get('Vehículos-km evitados/día', 0)):,}** km de congestión eliminados
    - **{int(full_row.get('Vehículos retirados', 0)):,}** autos que dejarían de circular
    - **{int(full_row.get('Vehículos menos en hora punta', 0)):,}** vehículos menos en hora punta
    """)

    st.metric("Ahorro Anual de Tiempo", f"{int(full_row.get('Horas ahorradas/día', 0)) * 365:,} horas/año")

# ───────────────────────────────────────────────
# PÁGINA: COSTO-BENEFICIO
# ───────────────────────────────────────────────
elif page == "💰 Costo-Beneficio":
    st.header("Análisis Costo-Beneficio Social")

    bc_df = data["bc"]
    st.subheader("B/C por Línea")
    st.dataframe(bc_df.style.format({"Inversión S/": "{:,.0f}", "B/C": "{:.2f}"}), use_container_width=True)

    fig_bc = FIGURES / "benchmark_bc.png"
    if fig_bc.exists():
        st.image(str(fig_bc), use_container_width=True)

    st.subheader("Componentes del Beneficio Social Anual")
    bnet = data["bc_network"]
    if len(bnet) > 0:
        def val(indicador):
            return float(bnet.loc[bnet["indicador"] == indicador, "valor"].iloc[0])
        b_total = val("beneficio_anual_total")
        st.markdown(f"""
        | Componente | Valor anual |
        |-----------|------|
        | Ahorro de tiempo | S/ {val('ahorro_tiempo_anual'):,.0f} |
        | Reducción de accidentes | S/ {val('accidentes_anual'):,.0f} |
        | Reducción de CO₂ | S/ {val('co2_anual'):,.0f} |
        | Ahorro combustible | S/ {val('combustible_anual'):,.0f} |
        | Ahorro operación buses | S/ {val('operacion_buses_anual'):,.0f} |
        | **Total anual** | **S/ {b_total:,.0f}** |
        """)

        st.warning(f"""
        **B/C = {bc_ratio:.2f}**: La red completa de 8 líneas no supera el umbral de rentabilidad (1.0).
        Se recomienda construcción por fases, priorizando líneas de alta densidad como L3 y Tren Lima-Ica.
        """)

    st.subheader("Costo de Inversión por km")
    cost_fig = FIGURES / "benchmark_cost_per_km.png"
    if cost_fig.exists():
        st.image(str(cost_fig), use_container_width=True)

# ───────────────────────────────────────────────
# PÁGINA: PLUSVALÍA
# ───────────────────────────────────────────────
elif page == "🏠 Plusvalía":
    st.header("Valorización del Suelo")

    lv = data["land_value"]
    st.subheader("Top 10 Distritos con Mayor Plusvalía")
    top10 = lv.sort_values("Plusvalía_S/", ascending=False).head(10)
    st.dataframe(top10.style.format({
        "Plusvalía_S/": "{:,.0f}", "Precio_base_S/": "{:,.0f}",
        "Precio_con_metro_S/": "{:,.0f}", "Dist_estación_(m)": "{:,.0f}",
        "Prima_proximidad": "{:.1%}", "Población": "{:,.0f}"
    }), use_container_width=True)

    fig_lv = FIGURES / "land_value_impact.png"
    if fig_lv.exists():
        st.image(str(fig_lv), use_container_width=True)

    total_gain = lv["Plusvalía_S/"].sum()
    st.metric("Plusvalía Total Estimada", f"S/{total_gain:,.0f}", f"${total_gain/3.7:,.0f} USD")

    st.info("""
    **Nota:** La plusvalía estimada considera solo el 30% de viviendas cercanas a estaciones.
    Mecanismos de captura de valor (contribución de mejoras, zoning) podrían financiar parte de la inversión.
    """)

# ───────────────────────────────────────────────
# PÁGINA: BENCHMARKING
# ───────────────────────────────────────────────
elif page == "🌎 Benchmarking":
    st.header("Benchmarking Internacional")

    bench = data["benchmark"]
    display_cols = ["city", "population_M", "metro_km", "daily_pax_K", "pax_per_km",
                    "cost_per_km_USD_M", "bc_ratio", "fare_integration"]
    st.dataframe(bench[display_cols].style.format({
        "population_M": "{:.1f}", "metro_km": "{:.1f}",
        "daily_pax_K": "{:.0f}", "pax_per_km": "{:,.0f}",
        "cost_per_km_USD_M": "${:.0f}M", "bc_ratio": "{:.2f}"
    }), use_container_width=True)

    st.subheader("Intensidad de Uso (Pax/km/día)")
    fig1 = FIGURES / "benchmark_intensity.png"
    if fig1.exists():
        st.image(str(fig1), use_container_width=True)

    col1, col2 = st.columns(2)
    fig2 = FIGURES / "benchmark_bc.png"
    if fig2.exists():
        col1.image(str(fig2), use_container_width=True)
    fig3 = FIGURES / "benchmark_scatter.png"
    if fig3.exists():
        col2.image(str(fig3), use_container_width=True)

    st.subheader("Factores de Éxito (lecciones aprendidas)")
    st.markdown("""
    1. **Integración tarifaria**: Todas las ciudades exitosas tienen tarjeta única — Lima no tiene
    2. **Alimentación con buses**: Medellín y Bogotá tienen extensas rutas alimentadoras
    3. **Fases graduales**: Santiago y Medellín expandieron línea por línea
    4. **Urbanismo social**: Medellín combinó metro + teleférico + espacio público
    5. **Transparencia**: Sobrecostos >50% son comunes — Líneas 1 y 2 de Lima tuvieron retrasos
    """)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Proyecto:** Evaluación Red Ferroviaria Lima  
**Stack:** Python, Streamlit, GeoPandas  
**Datos:** INEI, OSM, ATU, Benchmarking propio
""")
