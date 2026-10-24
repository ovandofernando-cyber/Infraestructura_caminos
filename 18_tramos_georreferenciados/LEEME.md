# Tramos de obras vecinales del MOPC ubicados en el mapa (2012-2025)

Primer paso para evaluar las obras donde deberían tener efecto: las escuelas, los puestos de salud y las localidades cercanas a cada tramo.

## Qué hay

| Archivo | Contenido |
|---|---|
| `tramos_obras_vecinales_MOPC_2012_2025.gpkg` / `.csv` | Un registro por lote de obra vecinal del MOPC (2012-2025): extremos leídos del texto, extremos ubicados, línea entre extremos (EPSG:4326), longitud en línea recta, longitud declarada si el lote la trae, precisión y revisión manual |
| `resumen_georreferenciacion.csv` | Cuántos lotes y qué monto se pudo ubicar |
| `escuelas_y_puestos_rurales_distancia_a_tramos.csv` | Locales educativos y puestos de salud rurales de la Región Oriental (sin Central) con la distancia al tramo más cercano y el año de la primera obra a menos de 5 km |
| `resumen_escuelas_puestos_cerca_de_tramos.csv` | Resumen de lo anterior |

Scripts: `_scripts/tra_01_georreferenciar_tramos.py`, `_scripts/tra_02_escuelas_y_puestos_cerca_de_tramos.py`.

## Cómo se ubican los tramos

1. **Extremos:** de cada lote se toman los nombres de los extremos: "Tramo: Nueva Toledo - Vaquería", "La Paz - Jesús", "Santa Fe del Paraná - Mbaracayú". Se descartan números de lote, progresivas, rutas numeradas y ríos.
2. **Ubicación de los nombres:** cada nombre se busca entre las localidades del Censo 2022 (punto interior del polígono COD-AB) y las cabeceras distritales, dentro de los departamentos asignados a la obra. Si no aparece allí, se busca en todo el país y solo se acepta si queda a menos de 80 km del otro extremo. Con nombres repetidos se elige la combinación más compacta.
3. **Trazado:** los extremos consecutivos se unen con una **línea recta**. Es una aproximación: el camino real es más largo; en los lotes que informan longitud, la longitud declarada es en promedio 1,5 veces la recta.
4. **Revisión manual:** se revisaron los tramos más grandes y se aplicaron 20 correcciones o descartes, que afectan a 25 lotes (columna `revision_manual`). Por ejemplo, Villarrica - Ñumi estaba con un solo punto, y la Ruta 9 del Chaco o los "tramos alimentadores" urbanos de Central no son tramos vecinales.

## Resultado

| Precisión | Lotes | Monto (miles de millones de Gs) |
|---|---|---|
| Tramo (línea entre extremos) | 80 | 3.746 |
| Un solo punto | 71 | 1.928 |
| Dudoso (la longitud declarada no coincide) | 2 | 37 |
| Sin ubicar (el lote no nombra lugares: "Lote 3", "varios departamentos") | 414 | 7.491 |

**Escuelas y puestos de salud rurales cerca de los tramos** (Región Oriental, sin Central):

| | Locales educativos | Puestos de salud |
|---|---|---|
| Total rurales | 5.396 | 818 |
| A menos de 2 km de un tramo | 620 | 88 |
| A menos de 5 km de un tramo | 1.464 | 188 |
| Con la primera obra cercana entre 2013 y 2020 | 1.062 | 125 |
| Distritos con escuelas cerca y lejos de un tramo | 129 | 68 |

Alcanza para un diseño escuela por escuela: comparar, antes y después del año de la obra, la matrícula de las escuelas cercanas a un tramo con la de escuelas lejanas del mismo distrito.

## Limitaciones

- **Ubicación incompleta:** solo el 43 % del monto quedó ubicado (29 % como tramo y 15 % como punto). Los lotes sin nombres de lugar no se pueden ubicar con el texto de la DNCP; harían falta los pliegos o el listado del MOPC.
- **Trazado aproximado:** la línea recta no sigue el camino. Un paso siguiente es trazar el recorrido sobre la red vial de OpenStreetMap entre los dos extremos.
- **Adjudicado no es ejecutado:** la ejecución se puede verificar con el historial de OpenStreetMap (la API ohsome responde desde este entorno) o con imágenes satelitales.

## Lo que falta

- **Matrícula anual por escuela del MEC:** el portal `datos.mec.gov.py` no respondía el 24/10/2026, tampoco desde fuera de este entorno. El campo `inst nro` de los locales educativos del INE podría servir para unir la matrícula cuando se consiga, sea descargándola del portal cuando vuelva a funcionar o pidiéndola al MEC por la Ley 5282.
