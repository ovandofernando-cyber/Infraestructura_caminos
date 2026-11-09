# Plan de análisis: efecto del mantenimiento de caminos vecinales en las condiciones de vida (diferencias en diferencias)

**Fecha:** 09/11/2026. Se sube al repositorio antes de calcular los resultados. Todo lo que se agregue después se informará como desvío o como análisis exploratorio.

## Pregunta

En los distritos donde el MOPC construyó o mejoró caminos vecinales, ¿mejoraron más las condiciones de vida donde esos caminos recibieron mantenimiento que donde no lo recibieron?

**Método del curso:** diferencias en diferencias. Se descartan los otros métodos del mapa de diseño:
- **Experimento:** no hubo sorteo.
- **Regresión discontinua:** no hay una regla de puntaje o umbral.
- **Variables instrumentales:** no hay un instrumento creíble.

## A. Diseño principal: diferencias en diferencias distrital (Censo 2012 frente a Censo 2022)

- **Unidades:** los 76 distritos de la muestra distrital de `16_` (Región Oriental sin Asunción ni Central, límites estables, NBI en los dos censos) con al menos una obra vecinal del MOPC ubicada y adjudicada entre 2012 y 2016 (`obra_temprana = 1`).
- **Tratamiento (mantenimiento):** la municipalidad adjudicó al menos un contrato de mantenimiento, reparación, perfilado o enripiado de caminos vecinales o rurales entre 2012 y 2020.
  - Fuente: DNCP, todas las entidades, ubicadas con `17_.../tabla_municipalidades_distritos.csv`.
  - Clasificación por el texto del llamado y de los lotes (`_scripts/mnt_01_did_mantenimiento.py`).
  - Se esperan 28 distritos tratados y 48 de control.
- **Resultado:** cambio del porcentaje de hogares con al menos una NBI entre 2012 y 2022 (puntos porcentuales). Valores negativos indican mejora.
- **Especificación:** con dos censos, la diferencia en diferencias equivale a regresar el cambio del NBI sobre el tratamiento:

$$\Delta NBI_d = \alpha_{dpto} + \beta\,Mantenimiento_d + X_d'\gamma + \varepsilon_d$$

  - **Controles $X$:** NBI 2012, % rural (Censo 2022), log de la densidad de población, log de los Gs de obra vecinal 2012-2020, royalties 2025 por habitante y lluvia media 2013-2022.
  - **Efectos fijos de departamento:** se comparan distritos del mismo departamento.
- **Inferencia:**
  - wild cluster bootstrap por departamento (Webb, 999);
  - aleatorización: se permuta el tratamiento dentro de cada departamento 2.000 veces.
- **Criterio:** hay evidencia de efecto si β < 0 con p < 0,05 en las dos pruebas.

### Pruebas secundarias (se informan todas)

1. **S1 Diferencia simple 2×2:** sin controles ni efectos fijos.
2. **S2 Triple diferencia:** con los 203 distritos de la muestra (con y sin obra temprana), el coeficiente de Obra × Mantenimiento. Mide si el mantenimiento se asocia a una mejora mayor donde hubo obra.
3. **S3 Intensidad:** número de años con contratos de mantenimiento entre 2012 y 2020, en lugar de 0/1.
4. **S4 Placebo de selección:** distritos cuyo primer contrato de mantenimiento es de 2022-2024, comparados con los que nunca contrataron (se excluyen los tratados 2012-2020). Si el "efecto" es parecido al principal, el resultado refleja qué municipios contratan y no el mantenimiento.
5. **S5 Luz nocturna (tendencias previas):** estimador escalonado del tipo Callaway y Sant'Anna como en `16_`.
   - Cohortes: año del primer contrato de mantenimiento, de 2015 a 2020, con ventana balanceada de −3 a +3.
   - Controles: distritos de la muestra sin contratos de mantenimiento entre 2012 y 2024.
   - Resultado: log de la luz por km².
   - Se informan el promedio de los años 0 a +3 y los coeficientes previos. Intervalos por bootstrap de departamentos.

## B. Complemento: diferencias en diferencias departamental (contrato del MOPC por niveles de servicio)

- **Tratados (8):** departamentos cubiertos por el contrato MOPC LPI 47/2021 de mantenimiento de caminos rurales por niveles de servicio, adjudicado en 2022: Concepción, San Pedro, Guairá, Caazapá, Itapúa, Alto Paraná, Amambay y Canindeyú.
- **Control (5):** Cordillera, Caaguazú, Misiones, Paraguarí y Ñeembucú.
- **Datos:** personas rurales de la EPHC (`20_.../base_modelo_personas.csv`).
- **Antes y después:** antes = 2017-2019 (sin pandemia); después = 2023-2025; se excluyen 2020-2022.
- **Resultados:**
  - **Principal:** consulta a un profesional de salud si estuvo enfermo.
  - **Secundario:** asistencia escolar de 12 a 17 años.
- **Especificación:** la de `20_`:
  - efectos fijos de departamento y de año;
  - Tratado × Después;
  - controles individuales;
  - factor de expansión;
  - **más (Tratado por obras de `15_`) × Después**, para separar el mantenimiento de la construcción.
- **Inferencia:** wild bootstrap por departamento y aleatorización exacta (las C(13,8) = 1.287 asignaciones).
- **Criterio:** β > 0 con p < 0,05 en las dos pruebas.
- **Secundario:** log de las consultas del MSPyBS por 1.000 habitantes (`21_`), con antes = 2014-2019 y después = 2023-2024.

## Limitaciones conocidas

- **Medición del tratamiento:** los contratos municipales captan solo una parte del mantenimiento. El que se hace por administración (máquinas del MOPC o del municipio) no está en la DNCP. Algunos controles tuvieron mantenimiento, lo que lleva el efecto hacia cero.
- **Selección:** contratan los municipios más organizados o con más recursos. Se controla por características observables, y la prueba S4 busca detectar la selección.
- **Tendencias paralelas:** no se pueden probar con dos censos; la luz nocturna (S5) es una verificación indirecta.
- **Pocos grupos:** 76 distritos en 13 departamentos en el diseño A; 8 frente a 5 departamentos en el diseño B.
