# Arquitectura de la base de datos: caminos vecinales y condiciones de vida rural

*Versión 2026-10-19. Pregunta guía: ¿cómo influye la calidad de los caminos vecinales en las condiciones de vida de la población rural de los departamentos más pobres de la Región Oriental (Concepción 01, San Pedro 02, Caaguazú 05, Caazapá 06, Canindeyú 14)?*

El detalle fuente por fuente (90 fuentes, con URL, licencia y notas de calidad) está en [`_arquitectura/fuentes_maestro.csv`](_arquitectura/fuentes_maestro.csv). Las reglas de unión y el control de calidad están en [`_arquitectura/claves_y_uniones.md`](_arquitectura/claves_y_uniones.md). Este documento resume cómo está organizada la base.

## 1. Capas

| Capa | Dónde | Qué contiene | Regla |
|---|---|---|---|
| **Cruda** | `01_` a `12_` | Archivos tal como los publica cada fuente (SAV, DTA, XLSX, PDF, GPKG, GeoTIFF, RAR) | No se modifica. Una fuente nueva va en una carpeta nueva |
| **Procesada** | junto a cada fuente (`*_por_distrito.csv`, tablas extraídas de PDF) | Tablas limpias con clave geográfica | CSV UTF-8, `cod_dist` y `cod_dpto` como texto con cero inicial |
| **Integrada** | `00_base_integrada/` | `base_distrital_integrada.csv` (263 distritos) y `base_departamental_integrada.csv` (15 dptos × EPHC rural), con diccionario | Única capa para el análisis. Se regenera con `_scripts/` |
| **Metadatos** | `_arquitectura/`, `catalogo_bases_caminos_vecinales.xlsx`, `_inventario_archivos.csv` | Catálogo de fuentes, claves, pendientes | Se regenera con `datos_fuentes_maestro.py` + `arquitectura_unir_fuentes.py` |

## 2. Fuentes por dimensión

| Dimensión | Fuente principal | Institución | Periodicidad | Período en el repo | Nivel | Clave de unión | Carpeta |
|---|---|---|---|---|---|---|---|
| **Condiciones de vida** | EPHC anual (microdatos) | INE | Anual | 2017-2025 | Hogar / persona | `DPTO` × `AREA` (sin distrito) | `01_` |
| | IPM (bases y tabulados) | INE | Anual | 2022, 2024, 2025 | Persona / dpto | `DPTO` × `AREA` | `01_` |
| | IPM y NBI distrital, mapa de pobreza | INE / Banco Mundial | Censal | 2022 | Distrito | `cod_dist` | `01_` |
| **Población y vivienda** | Censo 2022: cuadros, indígena, hogares | INE | Censal (10 años) | 2022 | Distrito | nombre → `cod_dist` | `02_` |
| | Proyecciones de población distrital | INE | Anual | 2000-2035 | Distrito | `cod_dist` | `02_` |
| **Red vial** | Inventario vial (km por red y superficie) | MOPC | Anual, irregular | dic. 2025 | Departamento | `cod_dpto` | `03_` |
| | Rutas y puentes clausurados | MOPC | Diaria | ene.-oct. 2026 | Tramo / localidad | geocodificación → `cod_dist` | `03_` |
| | Mapas viales y obras en ejecución | MOPC | Anual | 2026 | Tramo (PDF) | digitalizar | `03_` |
| | Superficie de caminos (IA Mapillary/Planet), RAI | HeiGIT | Irregular | 2020-2026 | Tramo / distrito | espacial / P-code | `03_` |
| | Red vial OpenStreetMap | HOT / OSM | Mensual | oct. 2026 | Tramo | espacial | `03_` |
| | Tramos y puentes de programas de caminos vecinales | BID (PR-L1084, PR-L1092) | Única | 2014-2025 | Tramo / punto | nombre o coordenadas → `cod_dist` | `11_` |
| | Obras viales contratadas | DNCP (OCDS) | Continua | 2018-2026 | Entidad / obra | nombre → `cod_dist` | `08_` |
| **Servicios e instituciones** | Accesibilidad a salud y educación | HeiGIT | Irregular | 2024-2026 | Distrito | P-code → `cod_dist` | `04_` |
| | Establecimientos sanitarios y escolares, healthsites, OSM | MSPBS, MEC, OSM | Anual / continua | 2018-2026 | Punto | espacial | `04_` |
| | Electrificación (luces nocturnas HREA) | U. Michigan / Banco Mundial | Anual | 2013, 2020 | Ráster / distrito | `cod_dist` | `09_` |
| | Conectividad internet (Ookla) | Ookla | Trimestral | 2025T4-2026T3 | Tesela / distrito | `cod_dist` | `09_` |
| | Instituciones (comisarías, municipios, bancos, mercados) | OSM / HOT | Continua | oct. 2026 | Punto / distrito | `cod_dist` | `09_` |
| **Producción y economía** | Censo Agropecuario Nacional | MAG | Censal | 2022 | Departamento | `cod_dpto` | `06_` |
| | Síntesis estadística de producción agrícola | MAG-DCEA | Anual (campaña) | 2017/18, 2020/21 | Departamento | `cod_dpto` | `10_` |
| | Cuentas regionales (PIB departamental) | BCP | Anual | 2021-2023 | Departamento | `cod_dpto` | `10_` |
| | Royalties y transferencias a municipios | MEF | Anual (mensual acumulado) | 2024, 2025 | Distrito | `cod_dist` | `10_` |
| | Desembolsos de crédito rural | CAH | Anual | 2017-2021 | Departamento | `cod_dpto` | `10_` |
| **Contexto** | Lluvia CHIRPS | CHC / WFP | Decádica / mensual | 1981-2026 | Distrito (214) | P-code | `07_` |
| | Riqueza relativa, población WorldPop | Meta, WorldPop | Única | 2020-2021 | Tesela / ráster | espacial | `07_` |
| **Cartografía** | Cartografía censal y códigos | INE, OCHA | Censal | 2012, 2022 | Polígono | `cod_dist` | `05_` |

## 3. Claves y unidad de análisis

- **Distrito (`cod_dist`, 4 dígitos INE 2022):** unidad principal. 263 distritos, 85 en los departamentos foco. Los P-codes de OCHA, HeiGIT y CHIRPS son `PY` + `cod_dist`.
- **Departamento × área × año:** unidad de la EPHC, que no trae distrito. `AREA` 1 = urbana, 6 = rural.
- **Puntos, tramos y rásters:** se pasan a distrito por intersección espacial o estadística zonal con la cartografía 2022 (EPSG:4326; medir en EPSG:32721).

## 4. Calendario de actualización

| Fuente | Cuándo sale lo nuevo |
|---|---|
| EPHC anual e IPM | Una vez al año, generalmente en el segundo semestre del año siguiente |
| Clausuras de rutas MOPC | Diaria (informes en PDF) |
| Inventario vial MOPC | Irregular, cortes anuales a diciembre |
| DNCP | Continua (API OCDS) |
| OSM, Ookla | Mensual y trimestral |
| CHIRPS | Cada 10 días |
| Royalties y transferencias MEF | Mensual acumulado |
| Censo de población, CAN | Cada 10 años aproximadamente |

## 5. Limitaciones y pendientes

- **37 fuentes no se pudieron descargar** desde este entorno, sobre todo porque la red bloquea los sitios `.gov.py` (INE, datos.gov.py, MOPC, MEC, MEF), HDX y otros. Están listadas con su URL en [`_arquitectura/fuentes_pendientes_descarga.csv`](_arquitectura/fuentes_pendientes_descarga.csv). Las de mayor valor: locales escolares del MEC, el tema Transporte de datos.gov.py, la EPHC trimestral, el anexo del PIB departamental del BCP y los precios mayoristas del Mercado de Abasto.
- **El Censo 2022 no tiene microdatos publicados:** solo cuadros y REDATAM en línea. Para localidad o compañía hay que pedirlos al INE por la Ley 5282.
- **Las tablas de `10_` se transcribieron de PDF** y se verificaron contra los totales del documento. La de crédito del CAH sale de un gráfico: usarla con cautela.
- **13 distritos nuevos de 2022** no tienen datos de HeiGIT ni CHIRPS (8 están en los departamentos foco).
- **No existe un inventario oficial georreferenciado de la red vecinal:** la calidad del camino se aproxima con superficie (HeiGIT, OSM), RAI, puentes de madera y clausuras.

## 6. Cómo se reproduce

```bash
python3 -I _scripts/datos_qc_base_integrada.py .     # control de calidad de 00_base_integrada
python3 -I _scripts/datos_fuentes_maestro.py .       # catálogo de las carpetas 00-08 y 12
python3 -I _scripts/arquitectura_unir_fuentes.py .   # suma 09-11 y arma la lista de pendientes
```

Las fichas de cada especialidad del equipo de agentes están en [`_equipo_agentes/`](_equipo_agentes/).
