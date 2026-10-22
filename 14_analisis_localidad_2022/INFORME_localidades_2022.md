# Distancia al camino de todo tiempo y condiciones de vida en las localidades rurales (Censo 2022)

**Pregunta:** ¿cómo influye la calidad de los caminos vecinales en las condiciones de vida de la población rural de los departamentos más pobres de la Región Oriental?

**Qué agrega frente al análisis distrital (`13_analisis_2022/`):** la unidad pasa a ser la **localidad rural** (compañía, colonia, asentamiento), que es donde vive la población de la pregunta, y se compara cada localidad con otras **del mismo distrito**. Así se descuenta todo lo que es común al distrito: municipio, cercanía a mercados regionales, historia de inversión, clima general.

Archivos: `base_localidades_2022.csv` (7.994 barrios y localidades), `resultados_localidades_2022.csv`, `descriptivos_por_distancia.csv`, `localidades_foco_por_distancia.csv`, `_resumen_corrida.txt`. Script: `_scripts/analisis_localidad_2022.py`.

## Datos y medición

| Componente | Cómo se midió | Fuente |
|---|---|---|
| Localidades | 7.994 barrios y localidades del Censo 2022 unidos uno a uno con sus polígonos (código distrito + localidad); 5.628 rurales | INE (indicadores por localidad) + COD-AB OCHA |
| Condiciones de vida | % de viviendas con piso de tierra, que cocinan con leña, sin ningún bien, con electricidad, agua corriente, internet y vehículo; **índice de privaciones** = promedio de 5 indicadores estandarizados (piso de tierra, leña, sin bienes, sin electricidad, sin agua corriente) | Censo 2022 |
| Camino de todo tiempo | Tramo con superficie pavimentada (asfalto, hormigón, empedrado, adoquín) o de ripio según OSM y la predicción por IA de HeiGIT (32.660 km) | HeiGIT / OSM (2024) |
| Distancia | Desde un punto interior de cada localidad hasta el camino de todo tiempo más cercano (km) | Cálculo propio |
| Controles | Población y superficie de la localidad, distancia a la capital del distrito, luz nocturna 2013 (actividad previa) | Censo 2022, COD-AB, VIIRS |
| Lluvia | Media anual 2013-2022 en el punto de la localidad | CHIRPS |

**Muestra:** 4.785 localidades rurales de la Región Oriental sin Asunción ni Central, con al menos 10 viviendas ocupadas (2.381 en los departamentos foco). Ponderadas por viviendas; errores agrupados por distrito (224 grupos).

## Lo que muestran los datos (antes de regresiones)

| Distancia al camino de todo tiempo | Localidades | Piso de tierra | Cocina con leña | Electricidad | Agua corriente | Vehículo |
|---|---|---|---|---|---|---|
| 0-2 km | 1.647 | 17 % | 56 % | 97 % | 71 % | 25 % |
| 2-5 km | 1.553 | 21 % | 67 % | 96 % | 65 % | 21 % |
| 5-10 km | 1.052 | 29 % | 72 % | 94 % | 57 % | 20 % |
| > 10 km | 533 | 35 % | 70 % | 86 % | 46 % | 18 % |

**En los departamentos foco**, 35 de cada 100 viviendas rurales (unas 280.000 personas) están en localidades a más de 5 km de un camino de todo tiempo.

## Resultados principales (efectos fijos de distrito: localidades del mismo distrito)

| Resultado | 2-5 km vs 0-2 km | 5-10 km vs 0-2 km | > 10 km vs 0-2 km |
|---|---|---|---|
| Índice de privaciones (desvíos estándar) | +0,08 *** | +0,17 *** | **+0,26** *** |
| % viviendas con piso de tierra | +1,8 pp *** | +5,8 pp *** | **+9,3 pp** *** |
| % viviendas que cocinan con leña | +5,3 pp *** | +7,3 pp *** | **+8,5 pp** *** |
| % viviendas con electricidad | −0,2 pp | −1,1 pp ** | **−4,1 pp** *** |
| % viviendas con vehículo | −3,4 pp *** | −4,5 pp *** | **−7,4 pp** *** |
| % viviendas sin ningún bien | +0,5 pp *** | +1,1 pp *** | +0,8 pp |
| % viviendas con internet | −2,1 pp ** | −2,3 pp | −3,3 pp * |
| % viviendas con agua corriente | +0,6 pp | −1,1 pp | −2,7 pp |

\*\*\* p < 0,01 · \*\* p < 0,05 · \* p < 0,10

**En palabras:** dentro de un mismo distrito, y con población, superficie, lejanía de la capital distrital y actividad económica previa similares, las localidades rurales más alejadas de un camino de todo tiempo viven peor. La relación es **gradual**: cuanto más lejos, peor. En una localidad a más de 10 km, de cada 100 viviendas, unas 9 más tienen piso de tierra, 8 a 9 más cocinan con leña, 4 menos tienen electricidad y 7 menos tienen vehículo que en una localidad a menos de 2 km.

### Lluvia (modelo C, efectos fijos de departamento)

La interacción distancia × lluvia **solo es significativa para el agua corriente**: donde llueve más, la lejanía se asocia con todavía menos acceso a agua por red (−1,7 pp por 100 mm, p = 0,001). Para el resto de los indicadores no hay evidencia de que la lluvia amplifique la brecha. Con datos de un solo año, la lluvia no permite separar el efecto del camino.

### Departamentos foco (modelo D)

La relación es **igual de fuerte** en los departamentos foco que en el resto de la Región Oriental. La única diferencia, débil, es un gradiente algo mayor de piso de tierra (+1,5 pp, p = 0,07).

## Robustez

- **Medida de camino:** se repitió con "solo pavimentado" y con "incluye rutas troncales sin dato de superficie": el coeficiente del índice no cambia (0,135). Esta prueba es **débil**: casi no hay tramos de ripio etiquetados en OSM, así que las tres medidas son casi iguales.
- **Forma funcional:** la distancia en logaritmo (modelo A) y por tramos (modelo B) cuentan la misma historia.

### Control de luz nocturna: ¿por qué 2013 y no 2022?

El control de luz busca descontar que algunas localidades ya eran más prósperas **antes**, por razones ajenas al camino. Por eso se usa la luz de **2013**, el primer año completo de VIIRS. La luz de 2022 no sirve como control principal: es en parte **consecuencia del propio camino** (más comercio, más conexiones eléctricas), y además mide en buena parte electricidad, que es uno de los resultados. Controlar por ella le quitaría al camino parte de su efecto: es un "mal control".

Coeficiente de log(1 + distancia) con efectos fijos de distrito, según el control de luz (`robustez_control_luz.csv`, script `_scripts/analisis_localidad_2022_robustez_luz.py`):

| Control de luz | Índice de privaciones | % con electricidad | % piso de tierra |
|---|---|---|---|
| Sin control de luz | 0,153 | −1,65 | 4,97 |
| **Luz 2013 (principal)** | **0,134** | **−1,55** | **4,57** |
| Luz 2022 | 0,119 | −1,33 | 4,12 |
| Luz 2013 y 2022 | 0,118 | −1,21 | 4,03 |

Todos los coeficientes son significativos (p < 0,01; n = 4.785).

- **La luz 2022 responde a la distancia al camino:** con la luz 2013 fija, las localidades más alejadas aumentaron menos su luz hasta 2022 (coeficiente −0,038; p < 0,001). Eso confirma que la luz 2022 está en el camino causal y no debe usarse como control.
- **La conclusión no depende de la elección:** en las cuatro versiones la asociación es positiva y muy significativa; solo cambia la magnitud, entre un 10 y un 25 %.
- **Salvedad:** la luz de 2013 tampoco es estrictamente anterior a todos los caminos. Los tramos que ya existían antes de 2013 pudieron influir en ella, así que este control también puede quitar algo de efecto. Es la mejor opción disponible, no una solución completa.

## ¿Lejos del camino o lejos del servicio?

Una localidad lejos del camino de todo tiempo suele estar también lejos de la escuela y del puesto de salud. Para separar los dos factores se calculó la distancia en línea recta de cada localidad a la **escuela básica**, el **colegio** (secundaria), la **atención primaria de salud** (USF, puesto o centro de salud) y el **hospital** más cercanos, con las capas del geoportal del INE (`distancias_servicios_localidades_2022.csv`, `resultados_camino_vs_servicio.csv`, `cuadro_2x2_camino_salud.csv`; script `_scripts/analisis_localidad_2022_servicios.py`).

Distancias medianas de las localidades rurales: camino de todo tiempo 3,2 km · escuela básica 1,4 km · colegio 3,2 km · atención primaria 3,9 km · hospital 21 km.

### 1. El camino sigue importando después de considerar los servicios

Coeficiente de log(1 + distancia al camino), efectos fijos de distrito:

| Resultado | Solo camino | Camino + distancia a los 4 servicios |
|---|---|---|
| Índice de privaciones | 0,134 *** | 0,121 *** |
| % piso de tierra | 4,57 *** | 3,95 *** |
| % cocina con leña | 5,26 *** | 5,43 *** |
| % con vehículo | −3,92 *** | −3,90 *** |
| % con electricidad | −1,55 *** | −0,99 *** |
| % con agua corriente | −0,69 | 0,31 |

- Para el índice, el piso de tierra, la leña y el vehículo, **la distancia al camino casi no cambia** al sumar la distancia a los servicios: el camino importa por sí mismo, no solo porque marca lejanía de la escuela o del puesto de salud.
- **Electricidad y agua corriente** se explican más por la lejanía de los centros de servicios (colegio, atención primaria): las redes de luz y agua llegan a los mismos núcleos donde están la escuela y el puesto. Para el agua, el camino deja de ser relevante.

### 2. Los servicios están donde están los caminos

Con la distancia al servicio como resultado: las localidades más alejadas del camino también están más lejos de la escuela básica (0,06), del colegio (0,12) y de la atención primaria (0,08), todas con p < 0,01. No pasa con el hospital, que está en las cabeceras distritales. Es decir, **el camino también es una vía por la que llegan los servicios**: el coeficiente de la columna "camino + servicios" es la parte de la asociación que no pasa por la cercanía a los servicios, no el total.

### 3. Peor cuando faltan los dos

Índice de privaciones, comparado con localidades cerca de ambos (≤ 5 km del camino y de la atención primaria), efectos fijos de distrito:

| Grupo | Localidades | Diferencia (desvíos estándar) |
|---|---|---|
| Cerca del camino y de la atención primaria | 2.373 | referencia |
| Cerca del camino, lejos de la atención primaria | 827 | +0,04 (no significativo) |
| Lejos del camino, cerca de la atención primaria | 755 | **+0,10** *** |
| Lejos de ambos | 830 | **+0,22** *** |

La interacción también lo muestra: **la distancia al camino pesa más cuanto más lejos está el puesto de salud** (interacción 0,054; p < 0,001). Con el colegio la interacción va en la misma dirección, pero es más débil (0,027; p = 0,10).

**Lectura:** estar lejos del camino es más dañino que estar lejos del puesto de salud, y lo peor es la combinación. Es coherente con la hipótesis: el camino de todo tiempo es lo que permite llegar a los servicios cuando no están en la propia comunidad.

**Cautelas:**
- Las distancias a los servicios son en línea recta, no por camino.
- La escuela básica sale con signo contrario (más lejos, menos privaciones). Las escuelas básicas están en casi todas las compañías, incluidas las más pobres, así que su cercanía marca comunidades rurales pequeñas más que acceso. No conviene interpretarlo como efecto.
- Los resultados disponibles por localidad son de vivienda, servicios y bienes. No hay asistencia escolar ni uso de salud por localidad, así que no se mide directamente el acceso efectivo a la escuela o al puesto.

## Limitaciones

1. **Asociación, no efecto causal.** Los caminos se pavimentan donde ya había más población y actividad; los efectos fijos de distrito y la luz 2013 ayudan, pero no resuelven la causalidad inversa.
2. **Calidad del mapa vial:** los tramos sin dato de superficie (unos 122.000 km) cuentan como "no de todo tiempo". Si las zonas más pobres están peor mapeadas, la distancia se sobreestima justo ahí y la asociación puede exagerarse.
3. **Ubicación de la localidad:** se usa un punto interior del polígono, no el centro poblado real. En localidades grandes puede haber error de varios kilómetros.
4. **Indicadores disponibles:** el censo por localidad trae vivienda, servicios y bienes, pero no pobreza, educación ni salud. El índice de privaciones es una aproximación a "condiciones de vida".
5. **Electricidad y piso de tierra también dependen de otras redes** (ANDE, programas de vivienda) que llegan por los mismos caminos: el camino puede ser el canal o solo un marcador de lejanía.

## Próximos pasos sugeridos

1. Ubicar mejor las localidades con los puntos de asentamientos (COD-AB `pry_adminpoints`) o la población grillada.
2. Medir la distancia a la escuela y al puesto de salud **por camino** (no en línea recta) y sumar resultados de uso de servicios cuando haya datos por localidad.
3. Para causalidad: comparar localidades cerca de los tramos que el BID mejoró con las cercanas a los tramos candidatos no ejecutados.
