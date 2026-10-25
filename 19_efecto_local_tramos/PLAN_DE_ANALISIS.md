# Plan de análisis: efecto local de los tramos (fijado antes de estimar)

**Fecha:** 25/10/2026. Se sube al repositorio antes de calcular los resultados. Lo que se agregue después se informará como desvío o como análisis exploratorio.

## Pregunta

En los alrededores de un tramo vecinal intervenido por el MOPC, ¿mejoró la superficie de los caminos y aumentó la actividad económica (luz nocturna) después de la obra, en comparación con zonas rurales similares sin obra ubicada?

## Unidades

- **Tratados:** tramos ubicados en `18_tramos_georreferenciados`, de la Región Oriental sin Central, con adjudicación entre 2015 y 2021. Así cada uno tiene 3 años previos y 3 posteriores dentro de 2012-2024. Si dos lotes tienen el mismo trazado, se toma el primer año. Zona de cada tramo: franja de 3 km alrededor de la línea o círculo de 3 km alrededor del punto.
- **Controles:** localidades rurales del Censo 2022 (área 6), de los mismos departamentos que los tratados, a más de 10 km de cualquier tramo o punto ubicado (2012-2025). Zona: círculo de 3 km. Se usan todas las que cumplen, hasta 400 elegidas al azar (semilla fija 2025).

## Resultados

1. **Luz nocturna (principal):** log(1 + radiancia por km² × 100) en la zona, por año (VIIRS VNL v2, 2012-2024).
2. **Primera etapa:** proporción de los km de caminos con superficie informada en OpenStreetMap que son pavimentados, empedrados o de ripio. Se mide en la zona al 1 de enero de cada año, 2012-2025, con el historial de OSM (API ohsome). Es indicativa: el mapeo en OSM también crece con el tiempo.

## Estimador

Diferencias en diferencias escalonado del tipo Callaway y Sant'Anna. Para cada cohorte *g* (año de adjudicación) y año *t*:

ATT(g,t) = [Y(g,t) − Ȳ(g; g−3..g−1)] − [Y(control,t) − Ȳ(control; g−3..g−1)]

- **Base:** el promedio de los tres años previos.
- **Agregación:** por años desde la obra (−3 a +3), ponderando por el tamaño de cada cohorte.
- **Efecto principal:** el promedio de los años 0 a +3.
- **Inferencia:** bootstrap por departamento (499 repeticiones).
- **Criterio:** hay evidencia de efecto si el efecto principal es positivo y su intervalo de confianza del 95 % no incluye el cero.

## Pruebas secundarias

1. Solo tramos con trazado (sin los de un solo punto).
2. Controles más parecidos: localidades a entre 10 y 30 km de un tramo.
3. Franja de 1,5 km en lugar de 3 km.

## Limitaciones conocidas

- **Controles contaminados:** solo el 43 % del monto de obras está ubicado, así que algunos controles pueden haber tenido obras no ubicadas. Eso empuja el efecto hacia cero.
- **Trazado aproximado:** la línea entre extremos es recta.
- **Adjudicado no es ejecutado:** se mide desde la adjudicación.
- **Cohortes no comparables:** las cohortes 2012-2014 no entran porque no tienen años previos con luz satelital.
