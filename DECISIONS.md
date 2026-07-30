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

### Plantilla para decisiones futuras:
```markdown
### YYYY-MM-DD: Título de la decisión
- **Contexto**: ...
- **Decisión**: ...
- **Alternativas**: ...
- **Consecuencias**: ...
```
