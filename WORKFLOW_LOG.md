# WORKFLOW_LOG.md — Registro de iteraciones del proyecto

Registro interno del proceso de auto-revisión. No forma parte del entregable
final (README.md / informe_final.md).

## Iteración 1 (2026-07-30)

**Estado inicial:** pipeline funcional (phase1–4) con 4 bugs de datos, 2
bugs de unidades/números hardcodeados, código sin vectorizar, figuras fuera
del sistema de diseño, sin tests, sin versiones pineadas.

**Correcciones aplicadas (reparación dirigida):**

1. **Integridad de datos (BLOCKER)** — zona "Ica" apuntaba a ubigeos de
   Piura (`2001xx`); faltaban Huaral/Chincha. Reconstruido
   `data/raw/poblacion_distrital_2017.json` desde el PDF oficial (115
   distritos), verificado contra totales de provincia del PDF.
2. **Integridad de datos** — `zones.py` ahora valida que todos los ubigeos
   declarados existan en la fuente INEI (`ValueError`).
3. **Integridad de datos** — `land_value.py`: 7 de 27 zonas caían en
   `fillna(0.5)` silencioso; índices corregidos + `ValueError`.
4. **Rendimiento (sin recorte)** — vectorizadas `travel_times.py`
   (haversine O(n²)→broadcasting; matriz km compartida) y `demand_model.py`
   (gravedad O(n³)→matricial; `np.ix_` en demanda por línea).
5. **Números** — fila "Lima (propuesta)" del benchmark derivada de outputs
   (era hardcodeada); corregida unidad `cost_per_km_USD_M` (faltaba /1e6).
6. **Visualización** — creado `src/viz_style.py` (paleta, 300 dpi,
   tipografía) y aplicado a fases 1–4, land_value y benchmarking.
7. **Entregables** — dashboard.py sin números hardcodeados (lee CSVs);
   `bc_network.csv` y `l1_validation.csv` como fuente única de cifras.
8. **Reproducibilidad** — `requirements.txt` pineado a versiones reales.
9. **Tests** — suite pytest de 26 tests (mapeos, determinismo, gravedad,
   costos, geometrías) + test explícito de integridad/leakage del corredor.
10. **Reproducibilidad de datos** — `src/data_inei.py` regenera el JSON de
    población desde el PDF oficial (el JSON está gitignored); tests de
    extracción y verificaciones de totales por provincia.

**Pasada abogado del diablo (hallazgos):**
- Escenario base incluía trenes inexistentes (1,376,311 pax/día) → modo tren
  deshabilitado en base; incremento real +2,174,241 pax/día TP.
- Documentada cota inferior del escenario base en demandas (limitación).
- Verificada cada cifra de README/informe contra los CSVs de la última
  corrida (scripts en /tmp, verificaciones registradas en el historial).

**Resultado tras la iteración:**
- Pipeline completo ejecutado de punta a punta (2 corridas idénticas).
- 32/32 tests pasan.
- Cifras del informe y README verificadas programáticamente contra
  `data/processed/*.csv`.
- Caché del grafo OSM con invalidación automática por hash del código
  generador (`data_osm.cache_is_fresh()`).
- Dataset de población reproducible: `src/data_inei.py` regenera el JSON
  desde el PDF oficial (verificado: salida idéntica).

## Puntuación (tras iteración 1)

| Categoría | Fórmula | Nota |
|-----------|---------|------|
| 1. Integridad de datos (25%) | 10 × (8/8) | 10.0 |
| 2. Corrección y reproducibilidad (20%) | 10 × (5/5) | 10.0 |
| 3. Rigor estadístico (15%) | 10 × (6/6) | 10.0 |
| 4. Calidad de código (15%) | 10 × (11/11) | 10.0 || 5. Visualización (10%) | 10 × (7/7) | 10.0 |
| 6. Estructura y documentación (10%) | 10 × (7/7) | 10.0 |
| 7. Ética/sesgos (5%) | 10 × (3/3) | 10.0 |
| **Ponderada** | | **10.0** |

**Condición de parada cumplida:** nota 10.0 en todas las categorías con el
checklist objetivo verificado contra ejecución real (sección 4 del
WORKFLOW). Pendiente solo la revisión de costos con fuente oficial externa
(si el usuario la aporta), registrada en DECISIONS.md.
