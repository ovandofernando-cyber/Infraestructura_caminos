# Plan de análisis: obras del MOPC y acceso a educación y salud (fijado antes de estimar)

**Fecha:** 26/10/2026. Se sube al repositorio antes de calcular los resultados. Lo que se agregue después se informará como desvío o como análisis exploratorio.

## Pregunta

En los departamentos con más obras del MOPC en caminos vecinales y departamentales (2018-2023), ¿mejoró más el acceso de la población rural a la educación y a la salud que en los departamentos con menos obras?

## Diseño (el mismo del análisis departamental `15_`)

- **Tratamiento y control:** los 6 departamentos de la Región Oriental (sin Asunción ni Central) con más inversión del MOPC en caminos vecinales y departamentales por habitante rural (adjudicaciones 2018-2023) frente a los otros 7 (`15_analisis_departamental_did/tratamiento_por_departamento.csv`).
- **Datos:** personas que viven en hogares rurales, EPHC 2017-2025, con el departamento de 2018-2021 recuperado por la UPM, como en `15_`. Se usa el factor de expansión de la EPHC.

## Resultados principales (2)

1. **Asistencia escolar de 12 a 17 años:** 1 si asiste a una institución de enseñanza (ED08 entre 1 y 18) y 0 si no asiste (ED08 = 19).
2. **Consulta a un profesional de salud si estuvo enfermo o accidentado en los últimos 90 días:** vale 1 si consultó (S04 = 1) a un médico, enfermero, partera profesional o dentista (S06 = 1, 2, 4 o 5). Vale 0 si no consultó o si consultó a otra persona (farmacéutico, curandero, familiar u otro).

## Resultados secundarios

3. Asistencia escolar de 6 a 11 años (casi universal; se espera poco cambio).
4. No asiste porque "no existe institución cercana" (ED10 = 6), sobre todas las personas de 6 a 17 años.
5. No consultó porque "no hay atención cercana" (S05 = 2), sobre las personas enfermas o accidentadas.
6. Entre quienes consultaron, se atendió en un establecimiento del Ministerio de Salud: hospital, centro, puesto o Unidad de Salud Familiar (S07 = 3, 4, 5 o 6).

## Especificación principal

Antes = 2017-2018 juntos; después = 2023-2024 juntos (agrupar dos años reduce el peso de un año atípico, como 2018 en `15_`).

$$Y_{idt} = \alpha_d + \lambda_t + \beta\,(\text{Tratado}_d \times \text{Después}_t) + X_{idt}'\theta + \varepsilon_{idt}$$

- **Controles $X$:** edad (y edad al cuadrado, en salud), sexo, tamaño del hogar y años de estudio del jefe de hogar.
- **Estimación:** mínimos cuadrados ponderados con el factor de expansión.
- **Inferencia:** wild cluster bootstrap por departamento (Webb, 999) y aleatorización exacta (las 1.716 formas de elegir 6 tratados entre 13).
- **Criterio:** hay evidencia de efecto en un resultado principal si β tiene el signo esperado (positivo en asistencia y en consulta) y p < 0,025 tanto en el wild bootstrap como en la aleatorización. El umbral es 0,025 porque hay dos resultados principales (corrección de Bonferroni).

## Pruebas secundarias (se informan todas)

1. 2018 frente a 2024 y 2017 frente a 2024.
2. Triple diferencia: personas rurales frente a urbanas del mismo departamento y año.
3. Estudio de eventos 2017-2025 con base 2017.
4. Diferencia en los 5 departamentos foco.

## Limitaciones conocidas

- **Pocos grupos:** son 13 departamentos, con poca potencia.
- **Medición de las obras:** se usa lo adjudicado (no lo ejecutado) y una parte no se pudo ubicar.
- **Escala gruesa:** el departamento mezcla compañías con y sin obra.
- **Pandemia:** en 2020-2021 la escolaridad y la consulta cambiaron por el COVID-19. No entran en la especificación principal, pero sí en el estudio de eventos.
