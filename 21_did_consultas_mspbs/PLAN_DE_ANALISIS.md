# Plan de análisis: obras del MOPC y consultas en establecimientos del Ministerio de Salud (fijado antes de estimar)

**Fecha:** 26/10/2026. Se sube al repositorio antes de calcular los resultados. Lo que se agregue después se informará como desvío o como análisis exploratorio.

## Pregunta

En los departamentos con más obras del MOPC en caminos vecinales y departamentales (2018-2023), ¿aumentaron más las consultas en los establecimientos del Ministerio de Salud que en los departamentos con menos obras?

## Datos

- **Consultas:** consultas registradas en los establecimientos del MSPyBS por región sanitaria y año, 2014-2024 (DIGIES, Sistema de Atención Ambulatoria; `09_servicios_complementarios/MSPBS_DIGIES/`). La región sanitaria coincide con el departamento.
- **Población:** población del departamento a mitad de cada año (INE, estimaciones y proyecciones distritales, revisión 2025).
- **Resultado:** log(consultas por 1.000 habitantes).
- **Muestra:** 13 departamentos de la Región Oriental, sin Asunción ni Central; 11 años.
- **Tratamiento:** el mismo del análisis departamental (`15_`). Son tratados los 6 departamentos con más inversión en caminos vecinales y departamentales por habitante rural, adjudicada entre 2018 y 2023.

## Especificación principal

$$\log(\text{consultas por 1.000})_{dt} = \alpha_d + \lambda_t + \beta\,(\text{Tratado}_d \times \text{Después}_t) + \varepsilon_{dt}$$

- **Antes** = 2014-2017 (sin obras del período). **Después** = 2022-2024. Se excluyen 2018-2021 (adjudicación y ejecución en curso, y pandemia en 2020-2021).
- **β:** diferencia porcentual aproximada en el crecimiento de las consultas por habitante de los departamentos tratados.
- **Inferencia:** wild cluster bootstrap por departamento (Webb, 999) y aleatorización exacta (las 1.716 formas de elegir 6 tratados entre 13).
- **Criterio:** hay evidencia de efecto si β > 0 con p < 0,05 en las dos pruebas.

## Pruebas secundarias (se informan todas)

1. Estudio de eventos 2014-2024 con base 2017.
2. Prueba de tendencias previas: tendencia lineal diferencial de los tratados en 2014-2017.
3. Tendencias lineales propias de cada departamento (estimadas con todos los años): controla diferencias en la velocidad de expansión del registro.
4. Intensidad continua: log de Gs por habitante rural en lugar de tratado/control.
5. Diferencia en los 5 departamentos foco.

## Limitaciones conocidas

- **Expansión del registro:** el número de establecimientos que reportan al sistema creció mucho en el período. Si creció más rápido en unos departamentos que en otros, se confunde con el efecto de las obras. Las pruebas 2 y 3 buscan detectarlo, pero no lo resuelven del todo.
- **Población total, no rural:** las consultas incluyen población urbana y rural, y no distinguen la residencia del paciente.
- **Pocos grupos:** son 13 departamentos.
- **Datos provisorios** según la DIGIES.
