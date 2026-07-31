# DECISIONS.md — Registro de Decisiones Técnicas

## Proyecto: Evaluación de la Red Ferroviaria Ampliada de Lima

### Formato
Cada entrada sigue: **Contexto → Decisión → Alternativas → Consecuencias**

---

### 2026-07-30: Inicio del proyecto
- **Contexto**: Se presenta un plan detallado para evaluar el impacto de 6 líneas de metro + 2 trenes de cercanías en Lima Metropolitana (~11M hab.). Propuesta de campaña de Keiko Fujimori 2026.
- **Decisión**: Crear proyecto `lima-metro/` con estructura estandarizada (data/, notebooks/, src/, outputs/) siguiendo las convenciones de `bachelor-forecast/`.
- **Alternativas**: Integrar dentro de `bachelor-forecast/` como subdirectorio — se descarta para mantener separación conceptual.
- **Consecuencias**: Proyecto autocontenido con su propio flujo WORKFLOW.md, DECISIONS.md y MEMORY.md.

---

### 2026-07-30: Corrección de la fuente de población del corredor Lima–Ica
- **Contexto**: El JSON INEI inicial solo contenía los 43 distritos de Lima Metropolitana y 7 del Callao. La zona "Ica" (Z27) usaba ubigeos `2001xx` que en realidad pertenecen a la provincia de **Piura**, no a Ica. Además faltaban las provincias de Huaral (`1506`), Huaura (`1508`, solo 4 distritos) y Chincha (`1102`).
- **Decisión**: Extraer la población por distrito directamente del PDF oficial `libro_poblacion_2017.pdf` (vía `pdftotext`) y reconstruir el JSON con 115 distritos reales del corredor. Verificar los totales por provincia contra el PDF: Huaral 197,963; Huaura 243,597; Chincha 240,884; Ica 407,286.
- **Alternativas**: (a) Dejar Piura como proxy de "zona sur lejana" — descartado, corrompe la geografía del modelo; (b) imputar Ica con datos sintéticos — descartado, la fuente oficial existe.
- **Consecuencias**: La población total del modelo sube de ~10.9M a 11.55M; la demanda, la congestión y la plusvalía cambian materialmente (la plusvalía pasa de S/570M a S/754M).

### 2026-07-30: Fallos de mapeo silenciosos → `ValueError` explícito
- **Contexto**: 7 de 27 distritos de zona caían en `fillna(0.5)` silencioso en `land_value.py`, subestimando precios de suelo (p. ej. Miraflores indexado a 0.5 en lugar de 2.5). `zones.py` tampoco verificaba que sus ubigeos existieran en la fuente INEI.
- **Decisión**: Sustituir los fallbacks silenciosos por aserciones `raise ValueError` que listan los valores sin mapear (patrón de MEMORY.md 2026-07-30).
- **Alternativas**: Rellenar los índices faltantes "a mano" sin verificación — descartado, no protege contra futuros cambios de datos.
- **Consecuencias**: Un error de mapeo detiene el pipeline en lugar de degradar los resultados; testeado en `tests/test_zones.py` y `tests/test_land_value.py`.

### 2026-07-30: Vectorización de matrices de tiempo y gravedad
- **Contexto**: `compute_haversine_matrix` usaba bucles Python O(n²) y `doubly_constrained_gravity` tenía triple anidación O(n³) por iteración; cada matriz haversine se recomputaba hasta 5 veces por corrida.
- **Decisión**: Vectorizar con numpy broadcasting y `shapely.distance`; calcular la matriz haversine UNA vez (en km) y compartirla entre auto/bus/metro/tren.
- **Alternativas**: Mantener bucles y cachear — descartado, la vectorización es más simple y no cambia resultados (verificado por test contra referencia de fuerza bruta).
- **Consecuencias**: La ejecución de las fases 2–3 es sustancialmente más rápida sin cambiar ningún resultado numérico.

### 2026-07-30: Benchmark "Lima (propuesta)" derivado de outputs reales
- **Contexto**: La fila "Lima (propuesta)" del benchmark estaba hardcodeada (1637K pax/día, 2611 pax/km, B/C 0.16, US$73M/km) y no coincidía con la demanda del modelo. Además el costo por km se guardaba sin dividir por 10⁶ (73,449,776 en vez de 73 USD M/km).
- **Decisión**: Derivar la fila en `_lima_propuesta_metrics()` desde `demand_comparison.csv` + funciones de `cost_benefit.py`; corregir las unidades a `cost_per_km_USD_M`.
- **Alternativas**: Actualizar el hardcode a mano — descartado, se desincroniza de nuevo; es exactamente la clase de bug detectado.
- **Consecuencias**: El benchmark refleja siempre la última corrida; un `FileNotFoundError` avisa si no se ejecutó la fase 2.

### 2026-07-30: Sistema de diseño centralizado (`viz_style.py`)
- **Contexto**: Cada módulo usaba paletas y dpi distintos (matplotlib por defecto, 150 dpi, colores ad-hoc).
- **Decisión**: Crear `src/viz_style.py` con la paleta de marca, `configure_matplotlib()` (300 dpi, tipografía, grillas, spines) y `save_fig()`, y aplicarlo a las 4 fases + land_value + benchmarking.
- **Alternativas**: Migrar todo a Plotly — descartado, los estáticos a 300 dpi cumplen el requisito del sistema de diseño.
- **Consecuencias**: Todas las figuras comparten apariencia; fácil de mantener en un solo lugar.

### 2026-07-30: `bc_network.csv` como fuente única de cifras B/C
- **Contexto**: Dashboard e informe tenían números B/C hardcodeados que divergían del pipeline (p. ej. "B/C promedio 0.16" vs 0.23 real).
- **Decisión**: Fase 3 guarda `data/processed/bc_network.csv` con los componentes de beneficio, VANs, inversión y B/C de red; el dashboard los lee en vez de hardcodearlos. La validación L1 se guarda en `l1_validation.csv`.
- **Alternativas**: Recalcular en el dashboard — descartado, duplica lógica y hace el dashboard lento.
- **Consecuencias**: Dashboard e informe siempre muestran las cifras de la última corrida.

### 2026-07-30: Escenario base sin trenes de cercanías
- **Contexto**: La matriz de tren se compartía entre escenarios, así que el "escenario base" (L1+L2) incluía los trenes Lima–Ica y del Norte que no existen aún; la demanda base estaba dominada por 1,376,311 pax/día de trenes inexistentes.
- **Decisión**: En el escenario base el modo tren no está disponible (utilidad `-inf`), coherente con "línea base sin red ampliada".
- **Alternativas**: Documentar el escenario base "con trenes" como un escenario intermedio — descartado, contradice la definición del propio informe.
- **Consecuencias**: El incremento atribuible a la red propuesta sube de +798K a +2,174,241 pax/día TP; la conclusión (B/C 0.23, priorizar L3 y tren Lima–Ica) no cambia.

---

### 2026-07-30: Reproducibilidad del dataset de población (`data_inei.py`)
- **Contexto**: `data/raw/*.json` y `data/raw/*.pdf` están en `.gitignore`; el JSON corregido (115 distritos) vivía solo en disco y un clon fresco del repo no lo tendría.
- **Decisión**: Crear `src/data_inei.py` que regenera `poblacion_distrital_2017.json` desde `libro_poblacion_2017.pdf` (parseo de `pdftotext -layout`), filtra al corredor Lima–Ica y verifica los totales por provincia contra el propio PDF. Verificado que regenera exactamente el JSON actual.
- **Alternativas**: Forzar el commit del JSON (`git add -f`) — descartado, contradice el `.gitignore` y deja la fuente real (PDF) fuera del control; un script hace el pipeline autocontenido.
- **Consecuencias**: Un clon fresco solo necesita el PDF (descarga de INEI documentada en el `FileNotFoundError`) para reconstruir los datos.

---

### Plantilla para decisiones futuras:
```markdown
### YYYY-MM-DD: Título de la decisión
- **Contexto**: ...
- **Decisión**: ...
- **Alternativas**: ...
- **Consecuencias**: ...
```

## Decisión pendiente de revisión externa

- **Costos de inversión y parámetros del modelo**: los costos US$150M/km (metro) y US$50M/km (tren) provienen de promedios CAF/BID y de ninguna fuente primaria verificada en la sesión. Si el usuario aporta una fuente oficial (MTC, OSITRAN, ATU), re-calcular `cost_benefit.py` antes del cierre.
