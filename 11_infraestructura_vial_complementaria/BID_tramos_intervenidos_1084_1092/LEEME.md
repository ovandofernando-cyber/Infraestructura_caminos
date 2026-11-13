# Tramos de caminos vecinales rehabilitados con los programas BID PR-L1084 y PR-L1092

**Fuente:** planilla del MOPC compartida por el equipo (`Tramos_intervenidos_Caminos_Vecinales_BID_1084_1092_v2.xlsx`, hoja `1084_1092`).

**Contenido:** 11 tramos en Caaguazú, Caazapá, San Pedro, Canindeyú, Cordillera e Itapúa. Suman **333,9 km** y **Gs 276.288 millones**.
- Ese monto equivale a unos USD 36,5 millones al tipo de cambio de 2025 (Gs 7.566 por dólar).
- Equivale a unos USD 46 millones al tipo de cambio de la época de los contratos (unos Gs 6.000 por dólar).

**Archivos derivados** (`_scripts/ent_01_tramos_bid_1084_1092.py`):

| Archivo | Contenido |
|---|---|
| `tramos_intervenidos_BID_1084_1092.csv` | Una fila por tramo: datos de la planilla, costo por km, años desde la recepción definitiva, y escuelas, puestos de salud y población a menos de 2 y 5 km |
| `tramos_intervenidos_BID_1084_1092.gpkg` | Trazado aproximado: línea recta entre las coordenadas UTM de inicio y fin de cada parte (EPSG:32721). Es más corto que la longitud declarada |
| `entorno_total_sin_doble_conteo.csv` | Totales sin doble conteo: 262 escuelas, 46 puestos de salud y unas 92.000 personas a menos de 5 km |

**Fuentes del entorno:** geoportal del INE (locales educativos y puestos de salud) y WorldPop 2020 (población).
