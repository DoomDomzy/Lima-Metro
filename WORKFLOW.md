# WORKFLOW.md — Flujo de Trabajo Iterativo

## Proyecto: Evaluación de la Red Ferroviaria Ampliada de Lima

### Ciclo de Trabajo (basado en AGENTS.md)

```
1. Build → 2. Execute → 3. Score → 4. Repair → 5. Repeat
```

### Fases del Proyecto

#### Fase 1 — Preparación de datos y GIS
- [ ] Geocodificar estaciones existentes y propuestas
- [ ] Calcular buffers de 800 m y población/empleo capturados
- [ ] Generar red multimodal (peatonal + metro + buses + privado)

#### Fase 2 — Estimación de demanda
- [ ] Definir escenarios: Base 2024 vs Red Propuesta 2030
- [ ] Modelo logit multinomial de elección modal
- [ ] Modelo gravitatorio doblemente restringido
- [ ] Validar con datos reales Línea 1 (~700K pax/día)

#### Fase 3 — Evaluación de impactos
- [ ] Congestión: vehículos-km ahorrados, horas-pico reducidas
- [ ] Costo-beneficio social (tiempo, accidentes, emisiones)
- [ ] Modelo hedónico de valorización del suelo

#### Fase 4 — Benchmarking internacional
- [ ] Seleccionar 3-4 sistemas (Medellín, Santiago, CDMX, Bogotá)
- [ ] Extraer métricas y situar a Lima en el contexto
- [ ] Identificar factores de éxito

### Rúbrica de Evaluación (categorías)

| # | Categoría | Peso | Descripción |
|---|-----------|------|-------------|
| 1 | Integridad de datos | 15% | Datos correctamente georreferenciados, sin errores espaciales |
| 2 | Corrección numérica | 20% | Demanda estimada, B/C, ahorros calculados correctamente |
| 3 | Completitud del análisis | 15% | Cubre demanda, accesibilidad, congestión, B/C, territorio, benchmark |
| 4 | Visualización | 10% | Dashboard/mapas claros, interpretables |
| 5 | Rigor metodológico | 20% | Modelos justificados, supuestos documentados, validación |
| 6 | Benchmarking | 10% | Comparación rigurosa con ciudades análogas |
| 7 | Reproducibilidad | 10% | Código versionado, rutas relativas, random_state fijo |

**Reglas clave:**
- Categorías 1 o 2 < 8/10 → total máximo 6/10
- Stop: total ≥ 9.0 Y todas ≥ 7.5, O 2 iteraciones sin mejora >0.2, O 6 iteraciones máximo

### Reparación dirigida
Si una categoría falla, consultar:
- **Cat 1**: Verificar georreferenciación, completitud de buffers, limpieza de datos
- **Cat 2**: Revisar modelo logit, matriz gravitatoria, cálculos de B/C
- **Cat 5**: Documentar supuestos, realizar análisis de sensibilidad
