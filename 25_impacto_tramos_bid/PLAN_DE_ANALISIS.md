# Plan de análisis: impacto de los 11 tramos rehabilitados (BID PR-L1084 y PR-L1092) y su persistencia (fijado antes de estimar)

**Fecha:** 13/11/2026. Se sube al repositorio antes de calcular los resultados. Todo lo que se agregue después se informará como desvío o como análisis exploratorio.

## Problema y pregunta

**Problema de investigación (memorando al Ministro del MOPC):** la falta de mantenimiento de los caminos vecinales ya intervenidos pone en riesgo la conectividad lograda y sus beneficios para las comunidades rurales.

Para saber cuánto vale lo que está en riesgo y si se está perdiendo, el análisis de impacto responde dos preguntas:

1. **¿Qué cambió en las comunidades cercanas cuando se habilitaron los 11 tramos rehabilitados?** Es el beneficio que el mantenimiento protege.
2. **¿Ese cambio se mantiene o se desvanece en los años siguientes?** Es una implicancia comprobable del problema: sin mantenimiento, el camino se deteriora y el efecto debería achicarse con el tiempo.

| Componente | Definición |
|---|---|
| **Palanca** | Rehabilitación del tramo (empedrado, enripiado o tratamiento superficial) |
| **Resultado** | Actividad económica local medida con luz nocturna (diseño A); acceso a salud y a la escuela de la población rural (diseño B) |
| **Población** | Comunidades a menos de 2 km de los tramos (A); población rural de los departamentos con tramos (B) |

## Elección del diseño (mapa del curso)

| Pregunta del mapa | Respuesta |
|---|---|
| ¿Alguien controla quién recibe el programa? → experimento | **No para el pasado.** Se propone para el futuro: sorteo escalonado del mantenimiento, en el entregable del track 3 |
| ¿Una regla asigna según un puntaje o umbral? → regresión discontinua | **No.** No hay una regla pública de puntaje para elegir tramos |
| ¿Un cambio afectó a unas unidades y no a otras? → diferencias en diferencias | **Sí.** Los tramos se habilitaron en años distintos (2019-2024): en cada año hay tramos ya habilitados y tramos todavía no habilitados del mismo programa |
| ¿Algo casi al azar cambia la exposición? → variables instrumentales | **No.** No hay un instrumento creíble |

## A. Diseño principal: diferencias en diferencias escalonado a escala local (luz nocturna)

- **Unidades:**
  - cada tramo se divide en segmentos de 5 km (sobre su trazado aproximado en línea recta);
  - cada segmento tiene una franja de 2 km a cada lado;
  - se excluyen las áreas urbanas del Censo 2022, para medir solo la parte rural.
- **Resultado:** log(1 + luz por km² × 100) en la franja, anual 2012-2024 (VIIRS VNL v2).
- **Cohorte (año de tratamiento):** año de habilitación del tramo. Si la habilitación fue en diciembre, se toma el año siguiente. Cohortes:
  - 2020: tramos 2 y 4;
  - 2021: tramos 5 y 9;
  - 2022: tramos 1, 3 y 6;
  - 2023: tramos 7, 8 y 10;
  - 2024: tramo 11.
- **Estimador:** tipo Callaway y Sant'Anna. Para cada cohorte g y año t:
  - ATT(g,t) = [Y(g,t) − base(g)] − [Y(control,t) − base(control)], con base = promedio de los años g−3 a g−1;
  - los efectos se promedian por años desde la habilitación, ponderando por el número de segmentos.
- **A1 (principal), controles "aún no habilitados":** para el año t, los segmentos de tramos con cohorte posterior a t (mismo programa, misma selección).
  - **Efecto principal:** promedio de los años 0 a +2.
- **A2 (secundario), controles nunca tratados emparejados:**
  - segmentos de 5 km de caminos rurales de OpenStreetMap (terciarios, sin clasificar y huellas) en los mismos 6 departamentos;
  - a más de 10 km de los 11 tramos y a más de 5 km de las otras obras vecinales del MOPC ubicadas (`18_`);
  - 5 controles por segmento tratado, del mismo departamento y con la luz más parecida en 2014-2016.
  - Permite ver más años: −5 a +4.
- **Prueba de persistencia:** con A2, la pendiente lineal de los efectos entre los años 0 y +4. Una pendiente negativa indica que el efecto se desvanece.
- **Inferencia:**
  - intervalos por bootstrap que remuestrea tramos enteros (11 conglomerados, 999 repeticiones);
  - aleatorización: se reasignan al azar las fechas de habilitación entre los 11 tramos (2.000 permutaciones).
- **Criterio:** hay evidencia de efecto si el efecto principal de A1 es positivo, su intervalo de 95 % excluye el cero y el valor p de la aleatorización es < 0,025. El umbral es 0,025 porque hay dos resultados principales (A y B).

## B. Diseño principal de acceso: diferencias en diferencias departamental (EPHC)

- **Tratados:** los 4 departamentos con al menos 30 km de tramos BID: San Pedro (105 km), Caaguazú (86), Caazapá (75) y Canindeyú (35).
- **Control:** los otros 7 departamentos de la Región Oriental sin Central: Concepción, Guairá, Misiones, Paraguarí, Alto Paraná, Ñeembucú y Amambay.
- **Excluidos:** Cordillera (11 km) e Itapúa (21 km), con tramos chicos frente a su tamaño.
- **Antes y después:** antes = 2017-2019; después = 2023-2025 (casi todos los tramos se habilitaron entre 2020 y 2023).
- **Resultados (personas rurales):** consulta a un profesional de salud si estuvo enfermo (principal B); asistencia escolar de 12 a 17 años (secundario).
- **Especificación:**
  - la de `20_`: efectos fijos de departamento y año, controles individuales y factor de expansión;
  - **más (tratado por obras MOPC de `15_`) × Después**, para separar estos tramos del resto de las obras.
- **Inferencia:** wild bootstrap por departamento y aleatorización exacta (las C(11,4) = 330 asignaciones).
- **Criterio:** β > 0 con p < 0,025 en las dos pruebas.

## Limitaciones conocidas

- **Pocos conglomerados:** 11 tramos y 11 departamentos, con baja potencia.
- **Resultado indirecto:** la luz nocturna mide actividad económica y electrificación, no el acceso a servicios. Ya mostró poca sensibilidad a los caminos vecinales (`19_`).
- **Pocos años después de la habilitación:** los datos llegan a 2024, y en A1 los controles "aún no habilitados" se agotan rápido.
- **Mantenimiento no observado:** no sabemos qué tramos recibieron mantenimiento. La persistencia es una prueba indirecta: un efecto que se desvanece es compatible con el deterioro, pero también con otras causas.
- **Trazado aproximado:** se usa la línea recta entre extremos.
