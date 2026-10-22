# Arquitectura de la base de datos: caminos vecinales y condiciones de vida rural

*Versión 2026-10-19. Pregunta guía: ¿cómo influye la calidad de los caminos vecinales en las condiciones de vida de la población rural de los departamentos más pobres de la Región Oriental (Concepción 01, San Pedro 02, Caaguazú 05, Caazapá 06, Canindeyú 14)?*

El detalle fuente por fuente (93 fuentes, con URL, licencia y notas de calidad) está en [`_arquitectura/fuentes_maestro.csv`](_arquitectura/fuentes_maestro.csv). Las reglas de unión y el control de calidad están en [`_arquitectura/claves_y_uniones.md`](_arquitectura/claves_y_uniones.md). Este documento resume cómo está organizada la base.

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
| | EPH serie comparable (microdatos, factor revisión 2025) | INE | Anual | 1997/98-2016 | Hogar / persona | `DPTO` × `AREA` | `12_` |
| | IPM (bases y tabulados) | INE | Anual | 2022, 2024, 2025 | Persona / dpto | `DPTO` × `AREA` | `01_` |
| | Encuesta de Ingresos y Gastos y Condiciones de Vida (EIGyCV) | INE | Única | 2011/12 | Hogar / persona | `DPTO` × `AREA` | `12_` |
| | IPM y NBI distrital, mapa de pobreza | INE / Banco Mundial | Censal | 2022 | Distrito | `cod_dist` | `01_` |
| **Población y vivienda** | Censo 2022: cuadros, indígena, hogares | INE | Censal (10 años) | 2022 | Distrito | nombre → `cod_dist` | `02_` |
| | Proyecciones de población distrital | INE | Anual | 2000-2035 | Distrito | `cod_dist` | `02_` |
| | Censo 2022: 95 indicadores de vivienda, hogar y población por barrio/localidad (7.995) y 106 por distrito | INE (geoportal) | Censal | 2022 | Barrio / localidad | código INE de 7 dígitos → `cod_dist` | `12_` |
| **Red vial** | Inventario vial (km por red y superficie) | MOPC | Anual, irregular | dic. 2025 | Departamento | `cod_dpto` | `03_` |
| | Rutas y puentes clausurados | MOPC | Diaria | ene.-oct. 2026 | Tramo / localidad | geocodificación → `cod_dist` | `03_` |
| | Mapas viales y obras en ejecución | MOPC | Anual | 2026 | Tramo (PDF) | digitalizar | `03_` |
| | Superficie de caminos (IA Mapillary/Planet), RAI | HeiGIT | Irregular | 2020-2026 | Tramo / distrito | espacial / P-code | `03_` |
| | Red vial OpenStreetMap | HOT / OSM | Mensual | oct. 2026 | Tramo | espacial | `03_` |
| | Red vial Overture Maps: km por jerarquía y superficie | Overture Maps (base OSM) | Mensual | release 2026-09-23 | Tramo / distrito | `cod_dist` | `11_` |
| | Red vial GRIP4 (armonizada global): km por tipo y superficie | PBL / GLOBIO | Única | datos de 2011 | Tramo / distrito | `cod_dist` | `11_` |
| | Tramos y puentes de programas de caminos vecinales; tramos candidatos y megaproyecto DCV | BID (PR-L1084, PR-L1092) | Única | 2014-2025 | Tramo / punto | nombre o coordenadas → `cod_dist` | `11_` |
| | Evaluaciones de programas (CAF ex post, Banco Mundial P082026) y balances anuales de gestión del MOPC | CAF, Banco Mundial, MOPC | Única / anual | 2006-2025 | Programa | no tabular | `11_` |
| | Obras viales contratadas | DNCP (OCDS) | Continua | 2018-2026 | Entidad / obra | nombre → `cod_dist` | `08_` |
| **Servicios e instituciones** | Accesibilidad a salud y educación | HeiGIT | Irregular | 2024-2026 | Distrito | P-code → `cod_dist` | `04_` |
| | Establecimientos sanitarios y escolares, healthsites, OSM | MSPBS, MEC, OSM | Anual / continua | 2018-2026 | Punto | espacial | `04_` |
| | Locales educativos, puestos de salud, antenas, juntas de agua y comunidades indígenas | INE (geoportal) | Censal (marco 2022) | 2022-2025 | Punto / polígono / distrito | `cod_dist` (viene en la capa) | `09_` |
| | Cobertura de telefonía e internet móvil por localidad | CONATEL | Anual | 2017-2025 | Localidad | código INE de localidad → `cod_dist` | `09_` |
| | Electrificación (luces nocturnas HREA) | U. Michigan / Banco Mundial | Anual | 2013, 2020 | Ráster / distrito | `cod_dist` | `09_` |
| | Conectividad internet (Ookla) | Ookla | Trimestral | 2025T4-2026T3 | Tesela / distrito | `cod_dist` | `09_` |
| | Instituciones (comisarías, municipios, bancos, mercados) | OSM / HOT | Continua | oct. 2026 | Punto / distrito | `cod_dist` | `09_` |
| | Lugares (escuelas, salud, bancos, gobierno) e infraestructura (puentes, silos, torres, líneas eléctricas) | Overture Maps | Mensual | release 2026-09-23 | Punto / distrito | `cod_dist` | `09_` |
| **Producción y economía** | Censo Agropecuario Nacional | MAG | Censal | 2022 | Departamento | `cod_dpto` | `06_` |
| | Síntesis estadística de producción agrícola | MAG-DCEA | Anual (campaña) | 2017/18, 2020/21 | Departamento | `cod_dpto` | `10_` |
| | Cuentas regionales (PIB departamental por actividad) | BCP | Anual | 2021-2024 | Departamento | `cod_dpto` | `10_` |
| | Royalties y transferencias a municipios | MEF | Anual (mensual acumulado) | 2024, 2025 | Distrito | `cod_dist` | `10_` |
| | Desembolsos de crédito rural | CAH | Anual | 2017-2021 | Departamento | `cod_dpto` | `10_` |
| | Precios mayoristas frutihortícolas (DAMA, Ciudad del Este, Encarnación, CECOPROA) | MAG-SIMA | Diaria / anual | 2022-2026 | Mercado | producto × fecha | `10_` |
| | Precios de alimentos | WFP / HDX | Mensual | 2010-2022 | Mercado (Asunción) | producto × fecha | `10_` |
| | Silos y acopios | OSM | Continua | oct. 2026 | Punto / distrito | `cod_dist` | `10_` |
| **Contexto** | Lluvia CHIRPS | CHC / WFP | Decádica / mensual | 1981-2026 | Distrito (214) | P-code | `07_` |
| | Lluvia CHIRPS recalculada desde los rásteres | CHC | Anual / mensual | 1991-2024 | Distrito (263) | `cod_dist` + año | `07_` |
| | Riqueza relativa, población WorldPop | Meta, WorldPop | Única | 2020-2021 | Tesela / ráster | espacial | `07_` |
| | Luces nocturnas VIIRS (VNL V2) | EOG / Zenodo | Anual | 2012-2024 | Píxel 500 m / distrito (263) | `cod_dist` + año | `07_` |
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
| OSM, Overture Maps, Ookla | Mensual y trimestral |
| CHIRPS | Cada 10 días |
| Luces nocturnas VIIRS | Anual (el año anterior sale a mediados del año siguiente) |
| Royalties y transferencias MEF | Mensual acumulado |
| Precios mayoristas SIMA-MAG | Diaria (boletín anual en el primer trimestre) |
| Cobertura móvil CONATEL | Anual (matriz por localidad) |
| Cuentas regionales BCP | Anual, con dos años preliminares |
| Censo de población, CAN | Cada 10 años aproximadamente |

## 5. Limitaciones y pendientes

- **16 fuentes siguen sin descargar** (lista con URL y motivo en [`_arquitectura/fuentes_pendientes_descarga.csv`](_arquitectura/fuentes_pendientes_descarga.csv)). Desde el 19/10/2026 la red del entorno deja pasar todos los dominios, así que lo que falta lo frena el propio sitio: piden verificación humana (publicaciones del BID, datos.hacienda.gov.py, captcha de ANDE, Cloudflare de documentos.mercosur.int), cortan la conexión (datos.mec.gov.py, indi.gov.py, Overpass), están caídos (`datos.gov.py` responde 502), piden registro (OpenCelliD) o no publican el dato (EPHC trimestral, IPM 2016-2021 y 2023, microdatos del Censo 2022, precios en finca, crédito por departamento; el MDS muestra Tekoporã en tableros sin descarga). Las de mayor valor: la línea de base de la evaluación de impacto del BID (bajar a mano desde un navegador), el tema Transporte de datos.gov.py y los agregados de programas sociales por distrito.
- **Varios pendientes se cubrieron con fuentes sustitutas:** los locales escolares, las juntas de saneamiento y las comunidades indígenas salen del geoportal del INE (no del MEC, SENASA ni INDI), sin matrícula ni datos de prestador; los precios mayoristas del Mercado de Abasto salen de los boletines SIMA del MAG y no de los anuarios del INE.
- **El INE no publica para descarga la EPHC trimestral ni las bases IPM 2016-2021 y 2023:** los paneles del portal de microdatos están vacíos. Las bases IPM que hay salieron de datos.gov.py. La base de transacciones de la EIGyCV (746 MB) no entra en GitHub.
- **El Censo 2022 no tiene microdatos publicados:** hay cuadros, REDATAM en línea y, desde el geoportal del INE, 95 indicadores agregados por barrio/localidad (`12_INE_complementario/Censo_2022_indicadores_localidad`). Para cruces que no estén en esos indicadores hay que pedir los microdatos al INE por la Ley 5282.
- **Las tablas de `10_` se transcribieron de PDF** y se verificaron contra los totales del documento. La de crédito del CAH sale de un gráfico: usarla con cautela.
- **13 distritos nuevos de 2022** no tienen datos de HeiGIT ni CHIRPS (8 están en los departamentos foco).
- **No existe un inventario oficial georreferenciado de la red vecinal:** la calidad del camino se aproxima con superficie (HeiGIT, OSM, Overture), RAI, puentes de madera y clausuras.
- **GRIP4 es viejo y grueso para Paraguay:** sus datos del país son de 2011 y solo distinguen pavimentado y tierra (43.175 km). Sirve para comparar con otros países, no para medir la red vecinal actual.
- **Las capas de OSM (silos) y de CONATEL tienen límites propios:** la ausencia de un silo en OSM no implica que no exista, y las columnas de servicio de las matrices de CONATEL se repiten por operador sin rotularlo.
- **Overture Maps cuenta más caminos que el MOPC:** su red rural y vecinal suma 142.129 km, entre 2 y 4 veces el km vecinal del inventario MOPC por departamento, porque incluye huellas y caminos privados. En los departamentos foco, cerca de la mitad de esos km no tiene la superficie informada. Sus lugares tienen sesgo urbano y comercial: no reemplazan los registros del MEC y del MSPBS.

## 6. Cómo se reproduce

```bash
python3 -I _scripts/datos_qc_base_integrada.py .     # control de calidad de 00_base_integrada
python3 -I _scripts/datos_fuentes_maestro.py .       # catálogo de las carpetas 00-08 y 12
python3 -I _scripts/arquitectura_unir_fuentes.py .   # suma 09-11 y arma la lista de pendientes
python3 -I _scripts/overture_recorte_bbox.py places/type=place <salida.parquet>   # recorte Overture (también base/type=infrastructure, transportation/type=segment)
python3 -I _scripts/overture_distrito.py <dir_extractos> <Distritos.geojson> <dir_09> <dir_11>   # distrito y resúmenes Overture
python3 -I _scripts/social_ine_geoportal.py .                    # capas del geoportal INE (09_) e indicadores censales por localidad (12_)
python3 -I _scripts/economia_bcp_cra.py .                        # PIB departamental 2021-2024 en formato largo
python3 -I _scripts/infra_grip_distrito.py <GRIP4_region2.gdb> <Distritos.geojson> <dir_salida>   # recorte GRIP4 y km por distrito
python3 -I _scripts/economia_silos_osm.py <paraguay-latest.osm.pbf> <Distritos.geojson> <dir_salida>   # silos y acopios OSM por distrito
```

Las fichas de cada especialidad del equipo de agentes están en [`_equipo_agentes/`](_equipo_agentes/).
