# ¿Cuánto le cuesta al Estado no mantener los caminos vecinales? Verificación, teoría del cambio y propuesta de análisis

**Pregunta principal propuesta:** ¿Cuánto le cuesta al Estado no asignar recursos permanentes para el mantenimiento periódico y rutinario de los caminos vecinales construidos, y cómo impacta en las condiciones de vida de las personas?

**Documento revisado:** *Teoría del Cambio en Caminos Vecinales* (L. Paiva), con un piloto de mantenimiento con microempresas en Itapúa y Alto Paraná basado en PROVÍAS Rural (Perú).

**Respuesta corta:**
1. **La premisa debe matizarse.** El MOPC sí tiene recursos permanentes para mantener caminos vecinales: dos proyectos presupuestarios, contratos por niveles de servicio y convenios. El problema verificable es otro: esos recursos son **chicos frente a la red y a lo que se invierte en construir**, y casi no hay registro de dónde se gastan.
2. **La teoría del cambio** es coherente para un piloto de microempresas, pero **no responde la pregunta nueva**. No llega a las condiciones de vida, deja afuera el mantenimiento periódico, no mide el costo de *no* mantener y no menciona la experiencia de Paraguay con microempresas (2007-2016).
3. **Análisis distrital:**
   - **La parte de costo sí se puede hacer por distrito** con los datos que tenemos, como simulación de costos con supuestos explícitos.
   - **El impacto causal en las condiciones de vida por distrito no se puede estimar de forma creíble** con los datos actuales del MOPC: no hay un registro por distrito y año de dónde se hizo mantenimiento.
   - Se propone un **análisis exploratorio** ahora y un **diseño de evaluación del piloto** para estimar el impacto después.

---

## 1. Verificación de la información

### 1.1 ¿El Estado no asigna recursos permanentes? Lo que muestran los datos

| Dato | Valor | Fuente en el repositorio |
|---|---|---|
| Red vecinal del inventario MOPC (16 dptos.; Misiones no figura en la tabla) | **60.634 km**, de los cuales **57.254 km (94 %) son de tierra** | `03_red_vial_MOPC/MOPC_inventario_km_por_red_y_superficie_dic2025.csv` |
| Proyecto presupuestario 2-002-12 "Mejoramiento de la gestión de los distritos departamentales" | "13.416 km de caminos vecinales mantenidos por los distritos de conservación en los 17 departamentos". **Es la misma cifra en los balances 2020, 2024 y 2025**: parece una meta, no una medición | `11_.../MOPC_balance_anual_gestion/BAGP_MOPC_2020/2024/2025.pdf` |
| Proyecto 2-002-09 "Conservación de caminos rurales no pavimentados, Región Oriental" | 2.231 km mantenidos en 2020; en 2025 solo informa obras en "zonas críticas" | BAGP 2020 y 2025 |
| Contratos del MOPC de "mantenimiento de caminos rurales por niveles de servicio en áreas geográficas" | 2012 (Guairá, Caaguazú, San Pedro, Concepción-Amambay); 2016 (Guairá); 2018 (San Pedro); 2022 (LPI 47/2021: 8 dptos.). Unos **98 mil millones de Gs** en las adjudicaciones que tenemos | `08_contrataciones_DNCP/DNCP_obras_viales_todas_entidades_2012_2025.csv` |
| Mantenimiento contratado 2018-2025 frente a obras | Unos 34 mil millones de Gs de mantenimiento contra **5.863 mil millones de Gs en obras vecinales y departamentales**: el mantenimiento contratado es alrededor del **0,6 %** | DNCP y `15_.../obras_viales_MOPC_2018_2025_clasificadas.csv` |
| Mantenimiento contratado por municipalidades | 416 adjudicaciones de 115 municipios (2012-2024), 63,5 mil millones de Gs en total | DNCP, todas las entidades |
| Mantenimiento contratado por gobernaciones | 91 adjudicaciones, 51,3 mil millones de Gs | DNCP, todas las entidades |
| Plan del MOPC para el BID (PR-L1092, EEO 7) | Mantenimiento por contratos: 1.176 km; por convenios con gobiernos locales: 2.152 km; "tramos incluidos en la emergencia vial": **8.672 km "sin financiamiento"** | `11_.../BID_PR-L1092_caminos_vecinales_II/EEO_7_...xlsx` |

**Lectura:** la afirmación correcta no es "no hay recursos permanentes", sino:
- hay recursos permanentes, pero **cubren una parte chica de la red**;
- **no se informa dónde ni cuánto se gasta** por distrito;
- **el mantenimiento contratado es una fracción mínima de lo que se invierte en construir y rehabilitar**.

**Advertencias:**
- Gran parte del mantenimiento se hace por administración, con máquinas propias de los distritos de conservación. Eso no pasa por la DNCP, así que las cifras de contratos son un piso.
- El presupuesto ejecutado por proyecto (MEF/SICO) no se pudo descargar: datos.hacienda.gov.py pide una verificación humana.

### 1.2 Experiencia de Paraguay que el documento no menciona

- **Banco Mundial, Proyecto de Mantenimiento Vial P082026 (2007-2016):**
  - Introdujo **microempresas de mantenimiento rutinario** en San Pedro, Caaguazú y Caazapá.
  - La meta era 10 microempresas y se lograron **6**, con **26 % de mujeres**.
  - El indicador "km de caminos no pavimentados mantenidos" se **eliminó** en 2014: solo se informaban **101 km** de unos 1.000 km.
  - El costo real de mejorar caminos no pavimentados fue de **174.000 a 222.000 USD por km**, 4,7 a 6,5 veces lo estimado.

  (Fuente: `11_.../BancoMundial_P082026_mantenimiento_vial/ICR_2016_Informe_cierre.txt`)
- **BID PR-L1084 (informe de terminación):**
  - 1.694,6 km mantenidos.
  - El tránsito diario promedio pasó de 156 a 320 vehículos.
  - Los días transitables pasaron del 75 % al 100 %.
- **BID PR-L1092:** plan de género con 108 mujeres capacitadas en oficios no tradicionales (BAGP 2025).
- **OIT:** un plan de implementación preveía 11 microempresas en Caazapá, Caaguazú y San Pedro ([OIT](https://webapps.ilo.org/DevelopmentCooperationDashboard/p/project/102106)).
- **Modalidades previstas por el MOPC:** administración directa, convenio con una asociación civil o contrato con microempresas ([PIARC 2011](https://proceedings-mexico2011.piarc.org/ressources/files/8/SP7-Rivet-S.pdf)).

**Conclusión:** el modelo de microempresas **ya se probó en Paraguay** y tuvo problemas de escala y sostenibilidad. La teoría del cambio debería partir de esa experiencia y explicar qué cambia ahora, además de citar a Perú.

### 1.3 Cifras de PROVÍAS Rural citadas en el documento

- **Confirmado:** el estudio de **8 microempresas en 4 dominios** existe ([BID, lecciones aprendidas en PROVÍAS Rural](https://publications.iadb.org/es/metadata/15067/publicacion15067lecciones-aprendidas-en-provias-rural-peru-y-pautas-para-disenar-operaciones-de); [GRADE/BID 2005](https://www.grade.org.pe/wp-content/uploads/JE_BID_PROVIAS_2005.pdf)).
- **No confirmado:** no encontré la fuente de "612 microempresas y casi 7.000 trabajadores en abril de 2006". Conviene citar el documento exacto del Banco Mundial (título, año y página) o sacar la cifra.

## 2. Revisión de la teoría del cambio

| # | Observación | Sugerencia |
|---|---|---|
| 1 | **El problema mezcla el problema con la solución:** empleo local, mujeres y arraigo | Problema: los caminos vecinales rehabilitados se deterioran antes de su vida útil por falta de mantenimiento; pierden transitabilidad y el Estado vuelve a pagar la rehabilitación. El empleo local es un cobeneficio del medio elegido |
| 2 | **El nivel de "impactos" son en realidad resultados:** "caminos mantenidos con niveles de servicio" e "inversión asegurada" | Impactos: acceso a salud, educación y mercados; costos de transporte; ingresos. Esa es la segunda mitad de la pregunta |
| 3 | **Falta el eslabón intermedio** | Agregar entre el resultado y el impacto: días transitables al año, tiempo de viaje, frecuencia del transporte público y costo de operación vehicular |
| 4 | **Solo cubre el mantenimiento rutinario.** El periódico (perfilado, recargo de ripio) va a "un componente separado" | La pregunta dice "periódico y rutinario". Sin recargo de material, un camino de ripio vuelve a tierra aunque las cunetas estén limpias. Incluir el periódico, aunque lo ejecute otro actor |
| 5 | **"Selección de caminos" y "selección del personal" son actividades, no productos** | Productos: km bajo contrato de mantenimiento, microempresas operando, inspecciones certificadas |
| 6 | **Los supuestos son solo de insumos** (presupuesto, equipos) | Agregar: la rehabilitación previa tiene la calidad prevista; los gobiernos locales pagan a tiempo; la supervisión certifica de forma independiente; las lluvias extremas no superan el diseño del drenaje; el tránsito pesado no excede la carga del camino |
| 7 | **Falta el costo de no mantener**, que es el centro de la pregunta | Agregar el contrafactual: sin mantenimiento, el camino se rehabilita cada N años y los usuarios pagan más por el mal estado. Ver la sección 3 |
| 8 | **Itapúa y Alto Paraná se eligen por ser los "mejor constituidos"** | Es razonable para un piloto, pero (a) no son los departamentos más pobres del estudio (Concepción, San Pedro, Caaguazú, Caazapá, Canindeyú) y (b) elegir los mejores distritos sesga cualquier evaluación. Ojo: son los de **más km de caminos vecinales** (9.413 y 9.317 km, 96 % de tierra) |
| 9 | **Los indicadores no tienen línea de base ni fuente** | Asignar a cada indicador una fuente (sección 4) y medirlo antes de empezar |

**Cadena sugerida:**

```
Insumos: presupuesto permanente por km (rutinario + periódico), microempresas o convenios, supervisión
 → Productos: km bajo mantenimiento certificado; cunetas, alcantarillas y calzada intervenidas
 → Resultados: rugosidad y estado del camino; días transitables; tiempo de viaje; transporte público
 → Impactos: asistencia escolar, consultas de salud, precios en finca, ingresos; y menor gasto del Estado en rehabilitaciones
Supuestos: rehabilitación de calidad, pago y certificación a tiempo, lluvias dentro del diseño
```

## 3. ¿Es posible un análisis de impacto a nivel distrital?

### 3.1 Qué datos hay y qué falta

| Necesario para el impacto | ¿Disponible? |
|---|---|
| Dónde y cuándo se hizo mantenimiento (distrito × año) | **No.** El MOPC informa 13.416 km totales sin desagregar. Los contratos por niveles de servicio son por "áreas geográficas" de departamentos, y el mantenimiento por administración no es público. Sí hay contratos municipales (115 municipios) |
| Qué caminos se rehabilitaron | Parcial: 161 lotes ubicados en 134 distritos (2012-2022), el 43 % del monto (`18_`) |
| Estado actual de los caminos | Una sola foto: HeiGIT con superficie a partir de imágenes Planet y Mapillary, sin serie de tiempo |
| Resultados por distrito | Censo 2012 y 2022 (NBI), luz nocturna anual. La EPHC no es representativa por distrito; no hay matrícula del MEC ni consultas por establecimiento |

**Conclusión:**
- **El costo de no mantener sí se puede estimar por distrito.** Es una simulación de costos, no un efecto causal.
- **El impacto causal del mantenimiento en las condiciones de vida no se puede estimar de forma creíble por distrito** con los datos actuales:
  1. **No se mide el tratamiento:** no sabemos qué distritos tuvieron mantenimiento ni cuándo.
  2. **Faltan resultados:** solo hay dos censos y la luz nocturna.
  3. **La potencia es baja:** en este mismo repositorio, el efecto de *construir* caminos en el NBI distrital fue nulo (se descartan efectos mayores a unos 2 pp). El efecto de *mantener frente a no mantener* es más chico todavía.

### 3.2 Propuesta de análisis en tres partes

**Parte A: costo de no mantener, por distrito (se puede hacer ya)**

Se compara el costo para el Estado de dos escenarios en 20 años, por km de camino vecinal mejorado:
- **Con mantenimiento:** rutinario cada año + periódico (recargo de ripio) cada 4 o 5 años.
- **Sin mantenimiento:** el camino se degrada y hay que rehabilitarlo cada N años.

**Costo de no mantener = valor presente (sin mantenimiento) − valor presente (con mantenimiento)**, más el mayor costo para los usuarios si se dispone de los datos de la evaluación con el modelo RED.

**Parámetros que ya tenemos:**

| Parámetro | Valor | Fuente |
|---|---|---|
| Mantenimiento rutinario y por niveles de servicio | **1.900 a 3.800 USD por km por año** (mediana alrededor de 2.600) | Plan del MOPC para el BID, EEO 7: contratos 12,1 M USD / 1.176 km / 4 años = 2.573; convenios 2.602; PR-L1084 3.774; PR-L1092 1.870; CAF 2.200 |
| Mejoramiento o rehabilitación | **70.000 USD por km** (estimado MOPC, Concepción) hasta **174.000-222.000 USD por km** (costo real, Banco Mundial) | EEO 7; ICR del Banco Mundial |
| Beneficio para los usuarios | Rugosidad (IRI) de 16 a 8; días transitables del 75 % al 100 %; tránsito de 156 a 320 vehículos por día | ICR del Banco Mundial; informe de terminación del BID PR-L1084; EEO 3 (modelo RED por tramo) |
| Km por distrito | Tramos rehabilitados por distrito (`18_`); km de tierra y de ripio por distrito (cruce de HeiGIT Planet con los límites distritales) | Repositorio |
| Montos contratados de obras y mantenimiento | Por año y por distrito o departamento | DNCP |

**Orden de magnitud:**
- Una sola rehabilitación (70.000 a 175.000 USD por km) equivale a **27 a 67 años de mantenimiento rutinario**.
- Mantener los 13.416 km que informa el MOPC cuesta unos **35 M USD por año**.
- Mantener toda la red vecinal (60.634 km) costaría unos **158 M USD por año**.

El análisis se presenta con escenarios (vida útil sin mantenimiento de 3, 5 y 8 años; tasa de descuento del 6 % y del 12 %) y un mapa del costo por distrito.

**Parte B: análisis exploratorio por distrito (se puede hacer ya, sin pretensión causal)**

- **B1. ¿Duran más los caminos con mantenimiento?** Tomar los tramos rehabilitados en 2012-2018 que están ubicados (`18_`) y medir su estado actual con la superficie de HeiGIT y Mapillary. Comparar los tramos de departamentos o áreas con contratos por niveles de servicio (2012, 2016, 2018, 2022) o de municipios con contratos de mantenimiento con los que no tuvieron.
  - **Resultado:** proporción del tramo clasificada como sin pavimentar o en mal estado en 2024.
  - **Lectura:** es una comparación transversal y no causal, pero mide el eslabón "mantenimiento → estado del camino" de la teoría del cambio.
- **B2. Gasto municipal en mantenimiento y condiciones de vida.** Armar un panel de distritos con el gasto contratado por municipalidades y gobernaciones (DNCP) y relacionarlo con:
  - el cambio en el NBI entre 2012 y 2022 (`16_`);
  - la luz nocturna;
  - controlando por la obra recibida, la lluvia y el NBI de 2012.

  Es una relación dosis-respuesta, sesgada porque los municipios con más recursos contratan más. Se presenta como descriptiva.
- **B3. Lluvia como prueba de estrés.** Un camino sin mantenimiento se corta cuando llueve. Se compara si en los años de lluvia extrema (CHIRPS) la luz nocturna o las consultas de salud del departamento caen más donde hay menos mantenimiento. Con los datos actuales solo se puede a escala departamental.

**Parte C: diseño para evaluar el impacto del piloto (estimación creíble a futuro)**

- **Unidad:** los tramos rehabilitados de los distritos del piloto.
- **Asignación:** incorporación escalonada al mantenimiento. Los tramos que entran el año 1 se comparan con los que entran el año 2 o 3, sorteando el orden entre tramos elegibles. Esto es aceptable porque no se le niega mantenimiento a nadie de forma permanente.
- **Línea de base y seguimiento cada 6 meses:**
  - estado del camino: inspección visual o IRI con un celular;
  - días cerrados;
  - tiempo de viaje;
  - transporte público;
  - asistencia en las escuelas a menos de 5 km (`18_` ya identificó 1.464 escuelas rurales a menos de 5 km de los tramos);
  - consultas en los puestos de salud cercanos;
  - precios en finca.
- **Costo:** costo certificado por km mantenido, comparado con el costo de rehabilitar los tramos de control que se deterioren.

### 3.3 Datos a pedir (Ley 5282 de acceso a la información pública)

1. **MOPC, Dirección de Caminos Vecinales:**
   - km mantenidos por distrito de conservación y por año (2015-2025), con el gasto en combustible, horas-máquina y personal;
   - lista de tramos de cada contrato por niveles de servicio (LPI 19-12, 2016 Guairá, 2018 San Pedro, LPI 47/2021) y de los convenios con gobernaciones y municipios;
   - microempresas y cuadrillas (PR-L1092);
   - inventario con el estado de cada tramo (bueno, regular o malo).
2. **MEF:** presupuesto vigente y ejecutado de los proyectos 2-002-09 y 2-002-12 por año.
3. **MEC y Ministerio de Salud (DIGIES):** matrícula por escuela y consultas por establecimiento, ya pendientes en análisis anteriores.

Con el punto 1 (km mantenidos por distrito y año), el análisis distrital pasa a ser posible. Se haría un diferencias en diferencias distrital: distritos que entraron o salieron del mantenimiento, con resultados de luz nocturna y NBI y, si llegan, matrícula y consultas.

## 4. Pregunta sugerida (más contestable)

> ¿Cuánto le cuesta al Estado, por km y por distrito, no financiar de forma permanente el mantenimiento rutinario y periódico de los caminos vecinales rehabilitados, y cómo se relaciona la falta de mantenimiento con la transitabilidad y el acceso de la población rural a la escuela, la salud y los mercados?

- **Primera mitad (costo):** se responde con la Parte A.
- **Segunda mitad (impacto):** se responde por ahora de forma exploratoria (Parte B) y de forma causal con la evaluación del piloto (Parte C) o cuando el MOPC entregue los datos por distrito.
