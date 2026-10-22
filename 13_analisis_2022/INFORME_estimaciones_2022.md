# Caminos de tierra, lluvia y condiciones de vida rural: primeras estimaciones con datos de 2022

**Pregunta:** ¿cómo influye la calidad de los caminos vecinales en las condiciones de vida de la población rural de los departamentos más pobres de la Región Oriental?

**Diseño:** corte transversal de 2022 (año del Censo), a nivel de distrito. Regresión lineal ponderada por población rural, con efectos fijos de departamento (se comparan distritos del mismo departamento). Es un análisis de **asociación**, no de efecto causal.

Archivos: `base_distrital_2022.csv` (263 distritos, 52 variables), `diccionario_base_2022.csv`, `resultados_estimaciones_2022.csv`, `descriptivos_muestra_2022.csv`, `_resumen_corrida.txt`. Script: `_scripts/analisis_2022.py`.

## Datos

| Rol | Variable | Fuente | Año |
|---|---|---|---|
| Resultado principal | % de población rural en pobreza multidimensional (IPM H rural) | INE, IPM distrital (Censo 2022) | 2022 |
| Calidad de caminos | % de km de la red vial del distrito que no está pavimentada | GRIP4 | 2018 (anterior al censo) |
| Calidad de caminos (alternativa) | % de población rural **sin** camino de todo tiempo a 2 km (100 − RAI) | HeiGIT | 2026 |
| Lluvia | Lluvia media anual 2013-2022; desvío de los 12 meses previos al censo | CHIRPS v2.0, calculado para los 263 distritos | 1991-2022 |
| Controles (anteriores o fijos) | Densidad de población, % rural, luz nocturna 2013, superficie, presencia de comunidades indígenas | Censo 2022, VIIRS, INE | 2013-2022 |

**Muestra:** 223 distritos de la Región Oriental sin Asunción ni Central (84 en los departamentos foco). Se excluyen 2 distritos sin datos o sin población rural.

## Especificación econométrica

**Estimador:** mínimos cuadrados ponderados (MCO ponderado), con una observación por distrito *d* del departamento *k*. El peso es la población rural del distrito (Censo 2022), para que cada distrito cuente según cuánta población rural representa.

**Modelo principal (M3):**

$$
\text{IPM}^{rural}_{dk} = \alpha_k + \beta\,\text{Tierra}_{dk} + \gamma\,\text{Lluvia}_{dk} + \delta\,(\text{Tierra}_{dk} \times \text{Lluvia}_{dk}) + X_{dk}'\theta + \varepsilon_{dk}
$$

| Término | Definición |
|---|---|
| $\text{IPM}^{rural}_{dk}$ | % de la población rural del distrito en pobreza multidimensional (INE, Censo 2022) |
| $\text{Tierra}_{dk}$ | % de km de la red vial del distrito que no está pavimentada (GRIP 2018), en unidades de 10 puntos porcentuales y centrado en la media de la muestra |
| $\text{Lluvia}_{dk}$ | Lluvia media anual 2013-2022 (CHIRPS), en 100 mm y centrada en la media |
| $\alpha_k$ | Efecto fijo de departamento: compara distritos del mismo departamento y descuenta todo lo común al departamento |
| $X_{dk}$ | Controles anteriores o fijos: log de densidad de población, % de población rural, log(1 + luz nocturna 2013 por 100 km²), log de superficie, presencia de comunidades indígenas |
| $\varepsilon_{dk}$ | Error |

**Interpretación de los coeficientes:**
- **β:** diferencia en puntos porcentuales de IPM rural asociada a 10 puntos más de red de tierra, en un distrito con lluvia promedio (por el centrado).
- **δ:** cuánto cambia esa asociación por cada 100 mm más de lluvia anual. Si la hipótesis es correcta, δ > 0: la lluvia agrava la brecha porque corta los caminos de tierra.

**Variantes estimadas:**

| Modelo | Cambio respecto de M3 |
|---|---|
| M1 | Solo Tierra y efectos fijos de departamento |
| M2 | M1 + controles $X$ (sin lluvia) |
| M4 | Lluvia como anomalía % de los 12 meses previos al censo (nov. 2021-oct. 2022) frente a 1991-2020 |
| M5 | Agrega Tierra × (departamento foco) para medir si la asociación es distinta en los cinco departamentos foco |
| M6 | Reemplaza Tierra por el % de población rural **sin** camino de todo tiempo a 2 km (100 − RAI, HeiGIT) |
| Mecanismos | Especificación M3 con otros resultados: IPM M0, NBI, % viviendas con electricidad, agua corriente, leña, sin bienes, % de población con hospital a menos de 1 hora, log de luz por habitante 2022 |

**Inferencia:**
- Errores estándar agrupados por departamento.
- Con solo 13 departamentos, los errores agrupados pueden ser poco confiables, así que para los coeficientes clave de M3 se calculó además un **wild cluster bootstrap** restringido (pesos de Webb, 999 repeticiones) y errores robustos HC1.
- **Sensibilidad a variables omitidas (Oster, 2019):** compara β y R² de M1 y M2, con $R^2_{max} = 1{,}3 \times R^2$ de M2.
- **Autocorrelación espacial:** I de Moran de los residuos de M3 con vecinos por contigüidad.

## Resultados

| Modelo | Coeficiente de Tierra (pp de IPM rural por +10 pp de red de tierra) | p (agrupado por dpto.) | p (wild bootstrap) |
|---|---|---|---|
| M1 solo efectos fijos | 2,54 | 0,011 | — |
| M2 + controles | 1,24 | 0,002 | — |
| **M3 + lluvia e interacción** | **1,46** | **0,001** | **0,030** |
| M6 con RAI en vez de GRIP (por +10 pp de población rural sin camino de todo tiempo) | 0,92 | 0,044 | — |

| Interacción Tierra × Lluvia (M3) | 0,64 | p = 0,052 (agrupado) · 0,095 (wild bootstrap) · 0,10 (robusto HC1) |
|---|---|---|

**En palabras:**
1. **Caminos de tierra y pobreza:** en un mismo departamento, los distritos con más red de tierra tienen más pobreza multidimensional rural. Pasar de un distrito con 82 % de red de tierra (percentil 25) a uno con 100 % (percentil 75) se asocia con **unos 2,7 pobres más de cada 100 habitantes rurales**, sobre un promedio de 38. El resultado se mantiene con la medida alternativa de acceso (RAI).
2. **La lluvia agrava la brecha:** la asociación es más fuerte donde llueve más. Con la lluvia del percentil 25 (1.570 mm/año), +10 pp de red de tierra se asocian con +0,7 pp de IPM rural. Con la del percentil 75 (1.820 mm/año), con +2,3 pp. La evidencia es **débil** (significativa al 10 %, no al 5 %), pero va en la dirección que predice la hipótesis: la lluvia corta los caminos de tierra.
3. **La anomalía de lluvia del año previo al censo no muestra efecto** (M4). Es esperable: los caminos de tierra afectan la vida por exposición repetida, no por un año puntual, y 2021-2022 fue un período seco.
4. **Departamentos foco (M5):** la asociación es mayor (0,95 + 0,89), pero la diferencia no es significativa.

### Mecanismos (misma especificación, otros resultados)

| Resultado | Tierra | Tierra × Lluvia | Lectura |
|---|---|---|---|
| IPM M0 rural (intensidad ajustada) | +0,61 (p 0,002) | +0,30 (p 0,037) | Igual que el IPM H |
| % población con hospital a < 1 h | −0,77 (p 0,67) | **−1,41 (p 0,008)** | Con más lluvia, más tierra se asocia con **menos acceso a hospital**: canal de acceso a salud |
| % viviendas con agua corriente | −0,72 (p 0,31) | **−1,29 (p 0,021)** | Menos servicios de red donde caminos de tierra y lluvia coinciden |
| % viviendas que cocinan con leña | +1,19 (p 0,054) | +0,20 (p 0,73) | Señal de menor acceso a mercados de gas |
| NBI al menos una | +0,42 (p 0,17) | +0,44 (p 0,095) | Débil |
| NBI acceso a educación | −0,04 (p 0,76) | +0,12 (p 0,19) | **Sin asociación** |
| % viviendas con electricidad | −0,02 (p 0,87) | −0,08 (p 0,11) | Sin asociación (la cobertura eléctrica es casi universal) |
| log luz nocturna por habitante | +0,005 (p 0,57) | −0,005 (p 0,52) | Sin asociación |

## Robustez

- **Sensibilidad a variables omitidas (Oster, 2019):** δ = 1,20. Los factores no observados tendrían que pesar 1,2 veces más que los controles incluidos para anular la asociación. Es una robustez **moderada**.
- **Autocorrelación espacial de los residuos:** I de Moran = 0,08 (baja).
- **Inferencia con pocos grupos:** con solo 13 departamentos se usó wild bootstrap (Webb, 999 repeticiones). La asociación principal sigue siendo significativa (p = 0,03).

## Limitaciones

1. **No es un efecto causal.** Los caminos no se asignaron al azar: puede que los distritos más pobres reciban menos pavimentación, y no al revés. La interacción con la lluvia es la parte más difícil de explicar por otra causa, pero su evidencia es débil.
2. **Poca variación en la medida de caminos:** en la mitad de los distritos el 99-100 % de la red es de tierra según GRIP 2018. La medida distingue mal entre distritos rurales y es gruesa (no separa ripio o empedrado de tierra).
3. **Medidas de acceso posteriores al resultado:** el RAI y la accesibilidad a hospitales son de 2026.
4. **Unidad agregada:** el distrito mezcla compañías muy distintas. La versión por localidad del Censo 2022 (7.995 localidades) sería más fina.
5. **Educación y luces no responden**, así que la hipótesis se sostiene sobre todo por el canal de **salud y servicios**, no por el educativo ni el de actividad económica.

## Próximos pasos sugeridos

1. Repetir el análisis **por localidad** (Censo 2022), con la distancia de cada localidad al camino de todo tiempo más cercano (HeiGIT/OSM).
2. Medir la calidad con **más detalle** (ripio, empedrado y tierra por separado, con Overture/OSM o el inventario del MOPC) para tener más variación.
3. Usar la lluvia como **exposición a días intransitables** (por ejemplo, días con más de 50 mm) en lugar del total anual.
