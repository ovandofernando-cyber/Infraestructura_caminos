# Inversión vial de todas las entidades y NBI por distrito, 2012-2022

**Pregunta:** si se suman las obras viales de los municipios a las del MOPC, ¿los distritos que más invirtieron en caminos rurales entre 2012 y 2020 redujeron más sus necesidades básicas insatisfechas (NBI) entre los censos 2012 y 2022?

**Cómo se hizo:** el plan de análisis (especificación principal, pruebas y criterio de lectura) se escribió y se subió al repositorio **antes** de estimar: `PLAN_DE_ANALISIS.md`. Lo que no estaba en el plan se informa aparte, como exploratorio.

**Respuesta corta:**
- **Signo esperado, sin significación:** la asociación va en la dirección esperada (más inversión en caminos rurales, mayor caída del NBI), pero **no es estadísticamente significativa** y no cumple el criterio fijado de antemano (p wild 0,13; p de permutación 0,07).
- **Tamaño chico:** pasar del distrito del percentil 25 de inversión al del percentil 75 se asocia con 0,85 puntos menos de NBI, en un período en que el NBI bajó 22 puntos en todos los distritos.
- **Placebo:** las obras urbanas no se asocian con el NBI.
- **Luz nocturna:** no responde.
- **Patrones exploratorios:** hay una asociación más clara con la inversión rural *municipal* y fuera de los departamentos foco, pero son pruebas secundarias o exploratorias que no sobreviven a la corrección por pruebas múltiples.

Archivos:

| Archivo | Contenido |
|---|---|
| `PLAN_DE_ANALISIS.md` | Plan fijado antes de estimar |
| `base_modelo_inversion_vial_distrital.csv` | **Base del modelo**: NBI 2012 y 2022, inversión por tipo y fuente, intensidades y controles por distrito |
| `diccionario_base_inversion_vial.csv` | Diccionario |
| `tabla_municipalidades_distritos.csv` | Correspondencia de las 228 municipalidades compradoras con los códigos de distrito del INE |
| `obras_viales_municipales_2012_2025.csv` | Obras viales municipales con su clasificación rural / urbana / sin clasificar |
| `inversion_vial_por_distrito_anio.csv`, `resumen_obras_municipales_por_tipo_2012_2020.csv` | Montos por distrito y año, y por tipo |
| `resultados_inversion_vial.csv` | Todas las estimaciones (principal, secundarias y exploratorias) |

Scripts: `_scripts/inv_00_obras_viales_todas_entidades.py <carpeta DNCP>`, `inv_01_intensidad_por_distrito.py`, `inv_02_modelos.py`.

## 1. Datos

1. **Obras de todas las entidades:** 11.885 adjudicaciones de obras viales de 2012 a 2025 en la DNCP, de 282 compradores (`08_contrataciones_DNCP/DNCP_obras_viales_todas_entidades_2012_2025.csv`).
2. **Municipalidades:** el distrito es el del comprador. Las 228 municipalidades se unieron con los códigos del INE: 202 por nombre igual, 21 por nombre parecido revisado y 5 corregidas a mano (por ejemplo, "Bella Vista - Itapúa", "Santa Rosa Misiones", "Yataity del Guairá").
3. **Rural o urbana:** se clasificó cada obra municipal por el texto del llamado y del lote, con las reglas del plan.

| Obras viales municipales 2012-2020 | Adjudicaciones | Monto (miles de millones de Gs) | Parte |
|---|---|---|---|
| Rurales (caminos vecinales, enripiado, puentes, alcantarillas, compañías…) | 880 | 156 | 11 % |
| Urbanas (calles, barrios, cordón cuneta, adoquinado…) | 2.807 | 648 | 47 % |
| Sin clasificar (por ejemplo "pavimento tipo empedrado" sin lugar) | 1.883 | 570 | 42 % |

4. **MOPC:** se suman las obras de caminos vecinales ubicadas por distrito en `16_`, todas como rurales. En los 203 distritos de la muestra, la inversión rural ubicada suma 4,75 billones de Gs del MOPC y 0,09 billones municipales. **El MOPC sigue siendo casi todo el monto**, aunque las obras municipales cubren muchos más distritos.
5. **Gobernaciones:** quedan fuera. Su inversión es departamental y la absorben los efectos fijos de departamento.

**Tratamiento:** $T^{rural}$ = log(1 + miles de Gs en caminos rurales 2012-2020 por habitante rural). En la muestra, la mediana es 287 mil Gs por habitante rural, el percentil 25 es 20 mil y el 75 es 3,2 millones. $T^{urbano}$ se calcula igual con las obras urbanas por habitante urbano.

## 2. Especificación principal (fijada en el plan)

$$\Delta\text{NBI}_d = \lambda_{k} + \beta\,T^{rural}_d + \gamma\,T^{urbano}_d + \delta\,\text{NBI}_{d,2012} + X_d'\theta + \varepsilon_d$$

| Término | Definición |
|---|---|
| $\Delta\text{NBI}_d$ | Cambio del % de hogares con al menos una NBI entre 2012 y 2022 (pp; negativo = mejora) |
| $T^{rural}_d$, $T^{urbano}_d$ | Intensidad de inversión en caminos rurales y en obras urbanas |
| $\text{NBI}_{d,2012}$ | Nivel inicial (los distritos más pobres bajaron más) |
| $X_d$ | % rural, log densidad, log superficie, lluvia media |
| $\lambda_k$ | Efecto fijo de departamento |
| $\beta$ | Puntos de NBI asociados a una unidad más de log de inversión rural |

**Criterio fijado:** evidencia de efecto si β < 0 con p wild < 0,05 y p de permutación < 0,05. Muestra: 202 distritos estables de la Región Oriental, sin Asunción ni Central.

## 3. Resultados

### 3.1 Principal

| | Coeficiente | IC 95 % | p wild (dpto.) | p permutación | p robusto |
|---|---|---|---|---|---|
| **Caminos rurales ($T^{rural}$)** | **−0,17** | [−0,37; +0,04] | **0,13** | **0,07** | 0,07 |
| Obras urbanas ($T^{urbano}$, placebo) | +0,18 | [−0,18; +0,54] | 0,27 | 0,19 | 0,23 |

- **El criterio no se cumple.** El signo es el esperado y el p de permutación (0,07) está cerca del umbral, pero con la inferencia principal (wild bootstrap, 0,13) no hay evidencia suficiente.
- **Magnitud:** del percentil 25 al 75 de inversión rural (de 20 mil a 3,2 millones de Gs por habitante rural), −0,85 pp de NBI.
- **Placebo:** las obras urbanas no muestran asociación negativa. Es lo esperable, porque el NBI no mide calles.

### 3.2 Secundarias (fijadas en el plan)

| Prueba | Coeficiente | IC 95 % | p wild | p corregido (Holm, 8 pruebas) |
|---|---|---|---|---|
| S1 Sin NBI 2012 | −0,11 | [−0,58; +0,37] | 0,64 | 1,00 |
| S3a Solo inversión rural municipal | −0,40 | [−0,76; −0,05] | 0,03 | 0,26 |
| S3b Solo MOPC ubicado | −0,08 | [−0,27; +0,10] | 0,35 | 1,00 |
| S4 Diferencia en departamentos foco | +0,43 | [+0,13; +0,73] | 0,04 | 0,27 |
| S5a Inversión rural 2012-2016 | −0,05 | [−0,30; +0,19] | 0,63 | 1,00 |
| S5b Inversión rural 2017-2020 | −0,10 | [−0,39; +0,19] | 0,48 | 1,00 |
| S6 Luz nocturna: inversión acumulada al año anterior | −0,003 | [−0,011; +0,006] | 0,48 | 1,00 |
| S6 Luz nocturna: inversión futura (t+2; debería ser 0) | +0,003 | [−0,010; +0,016] | 0,58 | 1,00 |

- **Inversión rural municipal (S3a):** sola se asocia con una caída mayor del NBI (−0,40 por unidad de log, p 0,03).
- **Departamentos foco (S4):** la asociación es más débil (diferencia +0,43, p 0,04).
- **Corrección por pruebas múltiples:** al corregir porque se hicieron 8 pruebas secundarias, ninguna es significativa.
- **Luz nocturna (S6):** no responde a la inversión, y la inversión futura tampoco "predice" la luz actual, que es lo esperable si no hay tendencias previas.

### 3.3 Exploratorias (no estaban en el plan)

| Prueba | Coeficiente | IC 95 % | p wild | p permutación |
|---|---|---|---|---|
| E1a Pendiente fuera de los departamentos foco | −0,31 | [−0,50; −0,13] | 0,03 | — |
| E1b Pendiente en los departamentos foco | +0,12 | [−0,13; +0,37] | 0,37 | — |
| E2 **Todas** las obras viales por habitante (municipal rural, urbana y sin clasificar + MOPC) | −0,11 | [−0,47; +0,24] | 0,58 | 0,38 |
| E3 Principal sin los 35 distritos sin ningún registro municipal en la DNCP | −0,14 | [−0,31; +0,02] | 0,09 | 0,20 |

- **E2 (todas las obras viales):** responde literalmente a la pregunta, y al sumar todas las obras la asociación se diluye. Las obras urbanas y las no clasificadas agregan ruido.
- **E3:** los 35 distritos sin ninguna compra vial municipal en la DNCP eran más pobres en 2012 (NBI 64,6 % frente a 54,5 %). Probablemente no publicaban sus compras en la DNCP, no es que no invirtieran. Sacarlos no cambia el resultado.
- **E1 (dentro y fuera de los departamentos foco):** sugiere que la asociación existe fuera de los departamentos foco y no dentro de ellos. Es un patrón encontrado mirando los datos: sirve como hipótesis para una próxima prueba, no como resultado.

## 4. Lectura

1. **Sumar las obras municipales no produce un efecto significativo** con la especificación fijada de antemano. El signo es el esperado, el tamaño es chico (menos de 1 punto de NBI entre distritos de inversión baja y alta) y el intervalo incluye el cero.
2. **Las señales más fuertes vienen de pruebas secundarias o exploratorias:** la inversión rural municipal y los distritos fuera de los departamentos foco. Con tantas pruebas, es esperable que alguna salga significativa por azar; no deben presentarse como hallazgos.
3. **Coincide con los análisis anteriores:** departamental con la EPHC (`15_`) y censal solo con el MOPC (`16_`). Los datos disponibles no muestran que la inversión vial haya movido el NBI distrital de forma detectable.

## 5. Limitaciones

1. **El MOPC sigue dominando el monto y su ubicación es incompleta:** el 53 % del monto de caminos vecinales del MOPC no está ubicado por distrito.
2. **Registros municipales incompletos:** en los primeros años muchas municipalidades no publicaban en la DNCP; 35 distritos de la muestra no tienen ninguna compra vial registrada.
3. **Clasificación por texto:** el 42 % del monto municipal no se pudo clasificar como rural ni urbano y quedó fuera del tratamiento principal.
4. **Endogeneidad:** los municipios con más recursos invierten más; los royalties y FONACIDE solo están en el repositorio para 2024-2025, así que no se pudieron usar como control del período.
5. **Montos:** son en Gs corrientes, sin deflactar, y adjudicados, no ejecutados.
6. **El NBI es estructural y está medido a nivel de distrito,** como total y no por área rural.
