# Evaluación de la Red Ferroviaria Ampliada de Lima

Impacto potencial de las nuevas líneas de metro y trenes de cercanías (Propuesta Fujimori 2026) en una megaciudad de 11+ millones de habitantes.

## Procedencia de datos

| Variable | Estado | Fuente / Método |
|----------|--------|-----------------|
| Población por distrito | **REAL** | INEI Censo 2017 — `libro_poblacion_2017.pdf` (Anexo: Población total por ubigeo) |
| Empleo por zona | ESTIMADO | Población INEI 2017 × tasa empleo/población específica por distrito (0.18–1.20 según centralidad económica). No existe PEA oficial a nivel distrital publicada en formato accesible. |
| Límites distritales | **REAL** | INEI 2017 (vía MINAM GeoServer). Capa: Límite de distritos de Lima Metropolitana. |
| Estaciones de metro | **REAL** | Coordenadas verificadas con OpenStreetMap y documentación oficial de Línea 1 y Línea 2. Líneas 3–6 y trenes de cercanías son propuestas con ubicaciones estimadas. |
| GTFS (rutas, horarios) | **SINTÉTICO** | ATU no publica feed GTFS público. Se genera dataset sintético desde estaciones definidas. Ver `src/data_gtfs.py`. |
| Red vial (OSM) | **REAL** | OpenStreetMap via OSMnx. Red de conducción (drive) de Lima Metropolitana. |
| Tiempos de viaje | ESTIMADO | Distancia haversine × factor de congestión + velocidades medias por modo. No se utiliza routing real sobre el grafo OSM. |
| Demanda de líneas propuestas | **[ESTIMADO por analogía]** | Modelo logit multinomial + gravitatorio doblemente restringido, calibrado con parámetros de la literatura internacional. Sin validación contra aforos reales. |
| Plusvalía del suelo | **[ESTIMADO por analogía con CDMX/Bogotá]** | Modelo hedónico simplificado con tasas de valorización de referencia internacional. |
| Benchmarking | **REAL** | Datos oficiales de Metro de Medellín, Metro de Santiago, CDMX Metro, TransMilenio + Metro de Bogotá. |
| Relación B/C | **ESTIMADO** | Costos de construcción estimados (US$120–200M/km según fuente MTC/CAF). Beneficios calculados del modelo de demanda. |

## Objetivo
Cuantificar la demanda potencial, el impacto en movilidad, la rentabilidad socioeconómica y el efecto ambiental/urbano de la red propuesta (6 líneas + 2 trenes de cercanías), comparándola con el escenario base (2024-2030) y con casos análogos internacionales.

## Estructura

```
lima-metro/
├── data/
│   ├── raw/          # Datos originales (censos, GTFS, shapefiles)
│   └── processed/    # Datos limpios y georreferenciados
├── notebooks/        # Análisis exploratorio y modelado (4 fases)
├── src/              # Código fuente (Python, 17 módulos)
└── outputs/          # Dashboard, figuras, tablas, informe
```

## Preguntas de investigación
1. **Demanda**: ¿Cuántos pasajeros diarios por línea?
2. **Accesibilidad**: % de población a <1 km de estación
3. **Congestión**: Vehículos y horas-pérdida reducidos
4. **Costo-beneficio**: Relación B/C de cada línea
5. **Territorio**: Plusvalía del suelo por distrito
6. **Benchmarking**: Lecciones de Medellín, Santiago, CDMX, Bogotá

## Stack
Python: pandas, geopandas, osmnx, networkx, scikit-learn, statsmodels, matplotlib, plotly, folium
QGIS para prototipado espacial
Jupyter Notebook para documentación
