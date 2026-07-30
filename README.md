# Evaluación de la Red Ferroviaria Ampliada de Lima

Impacto potencial de las nuevas líneas de metro y trenes de cercanías (Propuesta Fujimori 2026) en una megaciudad de 11+ millones de habitantes.

## Objetivo
Cuantificar la demanda potencial, el impacto en movilidad, la rentabilidad socioeconómica y el efecto ambiental/urbano de la red propuesta (6 líneas + 2 trenes de cercanías), comparándola con el escenario base (2024-2030) y con casos análogos internacionales.

## Estructura

```
lima-metro/
├── data/
│   ├── raw/          # Datos originales (censos, GTFS, shapefiles)
│   └── processed/    # Datos limpios y georreferenciados
├── notebooks/        # Análisis exploratorio y modelado
├── src/              # Código fuente (Python)
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
# Lima-Metro
