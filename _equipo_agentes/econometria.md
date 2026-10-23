# Ficha TLDR – Analista de datos experto en econometría (23/10/2026)

**Rol:** diseñar y revisar las estimaciones de impacto (diferencias en diferencias, triple diferencia, estudio de eventos, intensidad continua) y la inferencia con pocos conglomerados.
**Definición del agente (Claude Code):** `.claude/agents/analista-econometria.md`. Se invoca como subagente `analista-econometria` cuando se abre el repositorio con Claude Code.
**Primera tarea:** revisión independiente de `15_analisis_departamental_did/` (código de la clase `Fit`, recuperación del departamento en la EPHC 2018-2021, definición de tratamiento y control, conclusión).

## Reglas que aplica
1. Escribir primero la pregunta causal, el tratamiento, el contrafactual y los supuestos.
2. Errores agrupados al nivel del tratamiento; con menos de 30 grupos, wild cluster bootstrap restringido (Webb).
3. Robustez mínima: tendencias previas, placebo, línea de base alternativa, sacar un grupo por vez, falsificación en una población que no debería responder.
4. No reportar solo la especificación que "funciona"; distinguir asociación de efecto.
