# Evaluación de la Red Ferroviaria Ampliada de Lima

## Impacto Potencial de las Nuevas Líneas de Metro y Trenes de Cercanías (Propuesta Fujimori 2026)

**Autores:** Equipo de Data Science  
**Fecha:** Julio 2026  
**Repositorio:** `lima-metro/`

---

## Resumen Ejecutivo

Este estudio cuantifica el impacto de la red ferroviaria propuesta de 6 líneas de metro y 2 trenes de cercanías para Lima Metropolitana y Callao (~11M hab.). Utilizando modelos de elección discreta (logit multinomial), distribución gravitatoria doblemente restringida, y benchmarking internacional, se evaluaron cuatro dimensiones: demanda, congestión, costo-beneficio social y valorización del suelo.

**Resultados clave:**

| Indicador | Valor |
|-----------|-------|
| Demanda metro red completa | **699,412 pax/día** |
| Validación Línea 1 | **83.1%** de precisión |
| Horas ahorradas/día | **736,445 horas** |
| Vehículos retirados | **204,568** |
| Relación B/C (red completa) | **0.16** |
| Plusvalía total del suelo | **S/608 millones** |

**Conclusión principal:** La red completa de 8 líneas (US$46B) no es económicamente viable como proyecto único (B/C < 1). Se recomienda una estrategia por fases priorizando la Línea 3 (eje norte-sur) y el Tren Lima-Ica, implementando integración tarifaria como requisito previo.

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

| Fuente | Uso |
|--------|-----|
| OpenStreetMap (OSMnx) | Red vial (113K nodos) y edificios (152K) |
| Definición propia | 72 estaciones georreferenciadas |
| INEI / síntesis | Población y empleo por zona |
| Benchmarking propio | Métricas de 5 sistemas LATAM |

## 3. Resultados

### 3.1 Demanda

| Escenario | Metro (pax/día) | Tren (pax/día) | Total TP |
|-----------|:--------------:|:--------------:|:--------:|
| Base (L1 + L2 parcial) | 107,055 | 937,132 | 1,044,187 |
| Red completa (6L + 2 trenes) | **699,412** | 937,132 | **1,636,544** |
| *Incremento* | *+592,357* | *0* | *+592,357* |

La validación contra datos reales de la Línea 1 (700K pax/día) muestra una precisión del **83.1%** (estimado: 581K).

### 3.2 Congestión

La red completa transferiría **409,136 viajes/día desde el auto** (25% de los pasajeros TP), resultando en:

- **736,445 horas ahorradas por día**
- **4.9M vehículos-km evitados por día**
- **204,568 vehículos retirados de circulación**
- **27,276 vehículos menos en hora punta**

### 3.3 Costo-Beneficio Social

**Inversión total:** S/170,385 millones (US$46,050 millones)

| Componente | Beneficio anual |
|-----------|:--------------:|
| Ahorro de tiempo | S/ 2,688M |
| Reducción accidentes | S/ 179M |
| Reducción CO₂ | S/ 22M |
| Ahorro combustible | S/ 538M |
| Ahorro operación buses | S/ 315M |
| **Total anual** | **S/ 3,743M** |

**VAN Beneficios (30 años, 10%):** S/ 35,281M  
**VAN Costos (inversión + O&M):** S/ 218,571M  
**Relación B/C: 0.16**

| Línea | Longitud (km) | Inversión (S/) | B/C |
|-------|:------------:|:--------------:|:---:|
| L1 | 35 | 19,425M | 0.10 |
| L2 | 27 | 14,985M | 0.10 |
| L3 | 25 | 13,875M | 0.10 |
| L4 | 20 | 11,100M | 0.10 |
| L5 | 18 | 9,990M | 0.10 |
| L6 | 22 | 12,210M | 0.10 |
| Tren Ica | 280 | 51,800M | 0.30 |
| Tren Norte | 200 | 37,000M | 0.30 |

### 3.4 Valorización del Suelo

La red generaría una **plusvalía total de S/ 608 millones** (US$164M), con una prima promedio de **3.4%** en zonas a menos de 800m de una estación.

**Distritos con mayor plusvalía:**
- Miraflores / San Isidro
- San Borja / Surco
- Lima (Cercado)

### 3.5 Benchmarking Internacional

| Ciudad | Pax/km/día | B/C | Integración tarifaria |
|--------|:----------:|:---:|:--------------------:|
| Medellín | 15,974 | 1.40 | Full |
| Santiago | 16,779 | 1.20 | Full |
| CDMX | 19,912 | 1.80 | Parcial |
| Bogotá (BRT) | 21,053 | 2.10 | Full |
| **Lima actual** | **19,048** | **0.90** | **None** |
| **Lima propuesta** | **2,611** | **0.16** | **Propuesta** |

## 4. Discusión

### 4.1 Factores de éxito (lecciones de otras ciudades)

1. **Integración tarifaria**: Todas las ciudades con B/C > 1 tienen tarjeta única multimodal. Lima carece de esto.
2. **Alimentación con buses**: Medellín y Bogotá tienen extensas rutas alimentadoras. Lima tiene cobertura limitada.
3. **Construcción por fases**: Santiago y Medellín expandieron línea por línea. Proponer 8 proyectos simultáneos no tiene precedente en LATAM.
4. **Urbanismo social**: Medellín combinó metro + teleférico + espacio público, reduciendo desigualdad.
5. **Transparencia**: Proyectos LATAM típicamente tienen sobrecostos >50%.

### 4.2 Limitaciones del estudio

- No se incluyeron efectos de aglomeración económica ni beneficios de desarrollo urbano
- Matriz origen-destino sintética (no encuesta JICA actualizada)
- No se modeló integración tarifaria explícitamente
- Costos de inversión basados en promedios regionales

## 5. Recomendaciones

1. **Priorizar Línea 3** (Comas - San Juan de Miraflores): Eje norte-sur de alta densidad, sin cobertura actual de metro
2. **Avanazar Tren Lima-Ica**: Mayor B/C individual (0.30), potencial de desarrollo regional
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
