# Evaluación de la Red Ferroviaria Ampliada de Lima

## Impacto Potencial de las Nuevas Líneas de Metro y Trenes de Cercanías (Propuesta Fujimori 2026)

**Autores:** Equipo de Data Science  
**Fecha:** Julio 2026  
**Repositorio:** `lima-metro/`

---

## Resumen Ejecutivo

Este estudio cuantifica el impacto de la red ferroviaria propuesta de 6 líneas de metro y 2 trenes de cercanías para Lima Metropolitana y Callao (~11M hab.). Utilizando modelos de elección discreta (logit multinomial), distribución gravitatoria doblemente restringida, y benchmarking internacional, se evaluaron cuatro dimensiones: demanda, congestión, costo-beneficio social y valorización del suelo.

**Resultados clave:**

| Indicador | Valor | Nota |
|-----------|-------|------|
| Demanda metro red completa | **938,264 pax/día** | [ESTIMADO por modelo logit + gravitatorio] |
| Validación Línea 1 | **88.2%** | Contra dato real de aforo ATU (700K/día) |
| Horas ahorradas/día | **1,041,559 horas** | [ESTIMADO por modelo de demanda] |
| Vehículos retirados | **289,322** | [ESTIMADO tasa ocupación 2.0 pax/veh] |
| Relación B/C (red completa) | **0.23** | [ESTIMADO costos referencia CAF/BID] |
| Plusvalía total del suelo | **S/754 millones** | [ESTIMADO por analogía con CDMX/Bogotá] |

**Conclusión principal:** La red completa de 8 líneas (US$46B) no es económicamente viable como proyecto único (B/C=0.23). Se recomienda una estrategia por fases priorizando la Línea 3 (eje norte-sur) y el Tren Lima-Ica (mejor B/C individual: 0.43), implementando integración tarifaria como requisito previo.

---

## 1. Introducción y Antecedentes

Lima Metropolitana y Callao superan los 11 millones de habitantes. Actualmente cuenta con:
- **Línea 1**: 35 km elevados, 26 estaciones, ~700K pax/día
- **Línea 2**: 27 km subterráneos, en construcción (tramo operativo parcial)

La candidata presidencial Keiko Fujimori ha propuesto:
- Líneas 3, 4, 5 y 6 de metro
- Tren de cercanías Lima-Ica (280 km, 1.5 horas)
- Tren del Norte (Lima-Chancay-Barranca)

## 2. Metodología

### 2.1 Flujo de trabajo

```
Fase 1: Preparación GIS → Fase 2: Demanda → Fase 3: Impactos → Fase 4: Benchmarking
```

### 2.2 Modelos utilizados

1. **Geoprocesamiento**: Buffers de 800m, red OSM (113K nodos), 27 zonas de transporte
2. **Elección modal**: Logit multinomial con 4 modos (auto, bus, metro, tren)
3. **Distribución de viajes**: Gravitatorio doblemente restringido con calibración IPF
4. **Costo-beneficio**: VAN a 30 años con tasa de descuento del 10%
5. **Benchmarking**: Comparación con Medellín, Santiago, CDMX y Bogotá

### 2.3 Datos

| Variable | Estado | Fuente |
|----------|--------|--------|
| Población por distrito | REAL | INEI Censo 2017 — población total por ubigeo (115 distritos del corredor Lima–Ica: Lima Metropolitana, Callao, Huaral, Huaura, Cañete, Chincha e Ica) |
| Empleo por zona | ESTIMADO | Población INEI 2017 × tasa empleo/población específica por distrito |
| Límites distritales | REAL | INEI 2017 (vía MINAM GeoServer) |
| Estaciones de metro | REAL | Coordenadas verificadas en OSM (L1, L2); estimadas (L3-L6, trenes) |
| GTFS (rutas/horarios) | SINTÉTICO | ATU no publica feed GTFS. Generado desde estaciones definidas. |
| Red vial | REAL | OpenStreetMap vía OSMnx (113K nodos) |
| Tiempos de viaje | ESTIMADO | Haversine + factor congestión + velocidades medias. Sin routing real. |
| Benchmarking | REAL | Datos oficiales de Medellín, Santiago, CDMX, Bogotá |

## 3. Resultados

### 3.1 Demanda [ESTIMADO — modelo logit + gravitatorio]

Los valores de demanda para líneas propuestas (L3-L6, trenes) no pueden validarse contra datos reales por definición. La cifra de L1 existente permite calibrar el modelo.

| Escenario | Metro (pax/día) | Tren (pax/día) | Total TP |
|-----------|:--------------:|:--------------:|:--------:|
| Base (L1 + L2 parcial) | 140,335 [ESTIMADO] | 0 [sin trenes] | 140,335 |
| Red completa (6L + 2 trenes) | **938,264** [ESTIMADO] | 1,376,311 [ESTIMADO] | **2,314,576** |
| *Incremento* | *+797,929* | *+1,376,311* | *+2,174,241* |

La validación contra datos reales de la Línea 1 (700K pax/día real) muestra una precisión del **88.2%** (modelo estimó: 617,686 para el corredor L1 dentro de la red completa).

### 3.2 Congestión [ESTIMADO — derivado del modelo de demanda]

La red completa transferiría **578,644 viajes/día desde el auto** (25% de los pasajeros TP), resultando en:

- **1,041,559 horas ahorradas por día** [ESTIMADO]
- **6.94M vehículos-km evitados por día** [ESTIMADO]
- **289,322 vehículos retirados de circulación** [ESTIMADO — tasa ocupación 2.0 pax/veh]
- **38,576 vehículos menos en hora punta** [ESTIMADO — factor punta 13.3%]

### 3.3 Costo-Beneficio Social [ESTIMADO — costos CAF/BID, beneficios del modelo de demanda]

**Inversión total:** S/170,385 millones (US$46,050 millones)

| Componente | Beneficio anual |
|-----------|:--------------:|
| Ahorro de tiempo | S/ 3,802M |
| Reducción accidentes | S/ 253M |
| Reducción CO₂ | S/ 32M |
| Ahorro combustible | S/ 760M |
| Ahorro operación buses | S/ 446M |
| **Total anual** | **S/ 5,293M** |

**VAN Beneficios (30 años, 10%):** S/ 49,899M  
**VAN Costos (inversión + O&M):** S/ 218,571M  
**Relación B/C: 0.23**

| Línea | Longitud (km) | Inversión (S/) | B/C |
|-------|:------------:|:--------------:|:---:|
| L1 | 35 | 19,425M | 0.14 |
| L2 | 27 | 14,985M | 0.14 |
| L3 | 25 | 13,875M | 0.14 |
| L4 | 20 | 11,100M | 0.14 |
| L5 | 18 | 9,990M | 0.14 |
| L6 | 22 | 12,210M | 0.14 |
| Tren Ica | 280 | 51,800M | 0.43 |
| Tren Norte | 200 | 37,000M | 0.43 |

### 3.4 Valorización del Suelo [ESTIMADO por analogía con CDMX/Bogotá — modelo hedónico simplificado]

La red generaría una **plusvalía total de S/ 754 millones** (US$204M), con una prima promedio de **3.4%** en zonas a menos de 800m de una estación. [ESTIMADO por analogía con CDMX/Bogotá]

**Distritos con mayor plusvalía:**
- Miraflores / San Isidro
- San Borja / Surco
- Lima (Cercado)

### 3.5 Benchmarking Internacional [REAL — datos oficiales de cada sistema]

| Ciudad | Pax/km/día | B/C | Integración tarifaria |
|--------|:----------:|:---:|:--------------------:|
| Medellín | 15,974 | 1.40 | Full |
| Santiago | 16,779 | 1.20 | Full |
| CDMX | 19,912 | 1.80 | Parcial |
| Bogotá (BRT) | 21,053 | 2.10 | Full |
| **Lima actual** | **19,048** | **0.90** | **None** |
| **Lima propuesta** | **3,692** | **0.23** | **Propuesta** |

## 4. Discusión

### 4.1 Factores de éxito (lecciones de otras ciudades)

1. **Integración tarifaria**: Todas las ciudades con B/C > 1 tienen tarjeta única multimodal. Lima carece de esto.
2. **Alimentación con buses**: Medellín y Bogotá tienen extensas rutas alimentadoras. Lima tiene cobertura limitada.
3. **Construcción por fases**: Santiago y Medellín expandieron línea por línea. Proponer 8 proyectos simultáneos no tiene precedente en LATAM.
4. **Urbanismo social**: Medellín combinó metro + teleférico + espacio público, reduciendo desigualdad.
5. **Transparencia**: Proyectos LATAM típicamente tienen sobrecostos >50%.

### 4.2 Limitaciones del estudio

- **Escenario base como cota inferior de demanda metro**: el escenario base (L1 + L2 parcial, 35 estaciones) solo modela el corredor central, por lo que su demanda metro (140K pax/día) subestima el aforo real de la L1 (700K). La calibración del modelo se valida sobre el corredor L1 en la red completa (88.2%), no sobre el escenario base.
- **GTFS sintético**: ATU no publica feed GTFS público. Las rutas y horarios se generan desde estaciones definidas, no de datos reales de operación.
- **Matriz origen-destino sintética**: No se utilizó la Encuesta Domiciliaria de Viajes JICA (última disponible: 2012). Los viajes se distribuyen por modelo gravitatorio.
- **Tiempos de viaje estimados**: Se usó distancia haversine con factores de congestión, no routing real sobre el grafo OSM.
- **Empleo por zona estimado**: No existe PEA oficial a nivel distrital publicada en formato procesable. Se usaron tasas empleo/población específicas por distrito.
- **Costos de inversión basados en promedios regionales CAF/BID**, no en estudios de factibilidad detallados.
- **No se incluyeron efectos de aglomeración económica ni beneficios de desarrollo urbano**.
- **No se modeló integración tarifaria explícitamente**.
- **Demanda de líneas propuestas no validable por definición**: Líneas 3-6 y trenes de cercanías no existen, por lo que su demanda es intrínsecamente estimada.

## 5. Recomendaciones

1. **Priorizar Línea 3** (Comas - San Juan de Miraflores): Eje norte-sur de alta densidad, sin cobertura actual de metro
2. **Avanzar Tren Lima-Ica**: Mayor B/C individual (0.43), potencial de desarrollo regional
3. **Implementar integración tarifaria antes de expandir**: Tarjeta única + rutas alimentadoras
4. **Acompañar con urbanismo social**: Modelo Medellín de estaciones como polos de desarrollo
5. **Construcción por fases**: No más de 2 líneas simultáneas para mantener viabilidad fiscal

## 6. Referencias

- INEI. Censos Nacionales 2017. Microdatos Redatam.
- ATU. Plan Maestro de Transporte Urbano de Lima y Callao 2025-2040.
- OpenStreetMap contributors. Data retrieved via OSMnx, 2026.
- Metro de Medellín. Informes de Gestión.
- Metro de Santiago. Memoria Anual.
- BID. Evaluaciones ex-post de proyectos de transporte urbano en LATAM.

---

*Este informe fue generado automáticamente por el pipeline de análisis del proyecto `lima-metro/`. Los datos y scripts están disponibles en el repositorio.*
