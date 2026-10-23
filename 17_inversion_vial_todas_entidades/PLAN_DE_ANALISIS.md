# Plan de análisis (fijado antes de estimar)

**Fecha:** 23/10/2026. Este documento se sube al repositorio **antes** de correr las estimaciones. Los resultados se informarán sean cuales sean; cualquier cambio posterior se anotará como desvío del plan, con su motivo.

## Pregunta

¿Los distritos que invirtieron más en caminos rurales entre 2012 y 2020 —sumando obras municipales y del MOPC— redujeron más sus necesidades básicas insatisfechas (NBI) entre el Censo 2012 y el Censo 2022?

## Datos

- **Obras:** todas las adjudicaciones de la DNCP de 2012 a 2020 con estado "Adjudicado" (descarga masiva OCDS), de cualquier comprador, que sean obras viales según las reglas de `_scripts/obras_mopc_reglas.py`, más términos de obras municipales (empedrado, enripiado, cordón cuneta, perfilado, apertura de caminos).
- **Ubicación:**
  - **Municipalidades:** el distrito es el del comprador.
  - **MOPC:** obras de caminos vecinales ubicadas por distrito en `16_analisis_censal_nbi_2012_2022` (el resto no se usa).
  - **Gobernaciones:** se excluyen. Su inversión es departamental y queda absorbida por los efectos fijos de departamento.
  - **Otras entidades:** se excluyen.
- **Rural o urbano:** cada obra se clasifica por el texto del llamado y del lote.
  - **Rural:** caminos vecinales o rurales, enripiado, ripio, terraplén, perfilado, apertura de caminos, puentes, alcantarillas, badenes, o menciones de compañía, colonia o asentamiento.
  - **Urbana:** calles, avenidas, barrios, casco urbano, adoquinado, cordón cuneta.
  - **Sin clasificar:** si tiene términos de los dos grupos o de ninguno.
  - **MOPC:** todas sus obras de caminos vecinales cuentan como rurales.
- **NBI, muestra y controles:** los mismos de `16_`. Son 203 distritos estables de la Región Oriental, sin Asunción ni Central.

## Tratamiento

$T^{rural}_d = \log\left(1 + \dfrac{\text{Gs adjudicados en caminos rurales 2012-2020 en el distrito}}{\text{habitantes rurales 2022} \times 1.000}\right)$, es decir, log(1 + miles de Gs por habitante rural). Montos en Gs corrientes (sin deflactar; se informa como limitación).

$T^{urbano}_d$ se define igual con las obras urbanas y la población urbana.

## Especificación principal (una sola)

$$\Delta\text{NBI}_d = \lambda_{k} + \beta\,T^{rural}_d + \gamma\,T^{urbano}_d + \delta\,\text{NBI}_{d,2012} + X_d'\theta + \varepsilon_d$$

- $X_d$: % rural, log densidad, log superficie, lluvia media 2013-2022; $\lambda_k$: efecto fijo de departamento.
- **Hipótesis principal:** β < 0 (más inversión en caminos rurales, mayor caída del NBI).
- **Inferencia principal:** errores agrupados por departamento con p-valor de wild cluster bootstrap (Webb, 999). También se informan la permutación de $T^{rural}$ dentro de cada departamento (2.000 repeticiones) y los errores robustos por distrito.
- **Criterio:** se considera evidencia de efecto si β < 0 con p wild < 0,05 **y** p de permutación < 0,05.

## Pruebas secundarias (se informan todas)

1. Sin el NBI 2012 (diferencia en diferencias en cambios, sin control de convergencia).
2. **Placebo urbano:** γ (obras urbanas) no debería reducir el NBI tanto como β.
3. Solo inversión municipal; solo MOPC ubicado.
4. Diferencia en los 5 departamentos foco (interacción $T^{rural}$ × foco).
5. Inversión de 2012-2016 frente a 2017-2020.
6. **Luz nocturna 2012-2024**, panel distrito-año: log luz por km² sobre la inversión rural acumulada hasta el año anterior (log, por habitante rural), con efectos fijos de distrito y de departamento × año. Se incluye además la inversión **futura** (acumulada dos años después) como prueba de tendencias previas: su coeficiente debería ser cero.

## Limitaciones conocidas de antemano

- **Endogeneidad:** los municipios con más recursos invierten más; es asociación condicionada, no efecto causal probado.
- **Medición:** la clasificación rural/urbano por texto es imperfecta; se usa el monto adjudicado y no el ejecutado; las obras del MOPC que no se pudieron ubicar siguen fuera.
