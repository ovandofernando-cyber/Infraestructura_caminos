# Repositorio de datos: caminos vecinales y condiciones de vida rural

**Pregunta:** ¿cómo influye la calidad de los caminos vecinales en las condiciones de vida de la población rural de los departamentos más pobres de la Región Oriental?

**Hipótesis:** la falta de caminos vecinales de todo tiempo afecta la calidad de vida rural porque limita el acceso a servicios básicos y la comercialización de la producción.

**Departamentos foco:** Concepción (01), San Pedro (02), Caaguazú (05), Caazapá (06) y Canindeyú (14).

Armado el 17/10/2026 con descargas desde INE, datos.gov.py, MOPC, MAG, DNCP y HDX. El catálogo completo, con el estado de cada fuente, está en `catalogo_bases_caminos_vecinales.xlsx` (en esta misma carpeta). La lista de todos los archivos está en `_inventario_archivos.csv`.

Ampliado el 19/10/2026 por el equipo de agentes (carpetas 09 a 12). **La arquitectura de la base (fuente, periodicidad, nivel, claves) está en [`ARQUITECTURA_BASE_DE_DATOS.md`](ARQUITECTURA_BASE_DE_DATOS.md)** y el catálogo de las 93 fuentes en `_arquitectura/fuentes_maestro.csv`. El 19/10/2026 se sumaron las fuentes que estaban pendientes y ya se podían bajar; las 16 que siguen faltando, con el motivo, están en `_arquitectura/fuentes_pendientes_descarga.csv`.

## Estructura

| Carpeta | Contenido |
|---|---|
| `00_base_integrada/` | **Bases listas para analizar**: `base_distrital_integrada.csv` (263 distritos), `base_departamental_integrada.csv` (EPHC rural + MOPC) y `diccionario_bases_integradas.csv` |
| `01_condiciones_de_vida/` | EPHC anual 2022-2025 (microdatos SAV, CSV 2025, diccionarios, cuestionario); serie EPHC 2017-2021; bases IPM; 25 tabulados de pobreza del INE (IPM y NBI por distrito y área); mapa de pobreza distrital e IPM distrital |
| `02_censo_2022/` | Cuadros del Censo 2022 (datos.gov.py): población por área y distrito, hogares, indígena, proyecciones distritales |
| `03_red_vial_MOPC/` | Inventario vial del MOPC (corte dic. 2025, 17 departamentos) y **tabla de km por red y superficie extraída**; mapas viales y obras en ejecución 2026; informes diarios de puentes y rutas clausurados 2026 (con base extraída); RAI y accesibilidad por distrito (HeiGIT); superficie de caminos con IA (Mapillary/OSM —comprimida en `.gpkg.gz` por el límite de 100 MB de GitHub: descomprimir con `gunzip` o 7-Zip— y Planet); red vial OSM; anuarios INE |
| `04_servicios_e_instituciones/` | Accesibilidad a escuelas, hospitales y atención primaria (HeiGIT); establecimientos sanitarios y escolares (datos.gov.py); puntos de interés de OSM; healthsites.io |
| `05_cartografia_y_codigos/` | Cartografía censal 2022 en SHP (país y departamentos foco, en RAR); códigos INE 2012 y 2022; límites COD-AB de OCHA; GeoJSON |
| `06_produccion_CAN_2022/` | Tablas del Censo Agropecuario 2022; Atlas de la producción y presentación (geoportal MAG) |
| `07_clima_y_contexto/` | Lluvia CHIRPS por departamento y distrito 1981-2026 (tabla WFP, 214 distritos) y **recalculada para los 263 distritos** desde los rásteres (`lluvia_CHIRPS_raster/`, 1991-2024); **días de lluvia intensa** (≥ 30 y ≥ 50 mm) por año 2013-2022 desde CHIRPS diario (`lluvia_CHIRPS_diaria_dias_intensos/`); **luces nocturnas VIIRS anuales 2012-2024** (13 GeoTIFF recortados a Paraguay y `luces_nocturnas_por_distrito_2012_2024.csv`); índice de riqueza relativa (Meta); WorldPop 2020 |
| `08_contrataciones_DNCP/` | Llamados públicos de obras viales 2018-2026 (API OCDS de la DNCP) |
| `09_servicios_complementarios/` | Conectividad a internet Ookla (trimestral), electrificación HREA 2013/2020 e instituciones OSM (comisarías, municipios, bancos, mercados), todo también por distrito; capas del geoportal del INE (locales educativos, puestos de salud, antenas, tanques y juntas de agua, comunidades indígenas) con conteo por distrito; cobertura de telefonía e internet móvil de CONATEL por localidad 2017-2025 |
| `10_economia_y_mercados/` | Royalties 2025 y transferencias 2024 a municipios (MEF), producción agrícola por departamento (MAG), PIB departamental 2021-2024 por actividad (BCP, anexo xlsx y tabla larga), crédito CAH; precios mayoristas SIMA-MAG (boletines anuales 2022-2025 y diarios nov. 2025-oct. 2026, con CECOPROA), precios WFP 2010-2022, silos y acopios OSM por distrito, calendario de ferias de la agricultura familiar |
| `11_infraestructura_vial_complementaria/` | Programas BID de caminos vecinales: tramos mejorados, 169 puentes de madera georreferenciados, informe de cierre, línea de base de la evaluación de impacto, tramos candidatos y megaproyecto de la DCV (PR-L1092); evaluación ex post de CAF; documentos del proyecto de mantenimiento vial del Banco Mundial (P082026); balances anuales de gestión del MOPC 2020-2025; red vial GRIP4 recortada a Paraguay con km por distrito |
| `12_INE_complementario/` | Serie comparable EPH 1997/98-2016 (microdatos SAV, diccionarios, cuestionarios) y EIGyCV 2011/12 (bases DTA de gasto, vivienda y población); indicadores del Censo 2022 por barrio/localidad (7.995) y por distrito, con diccionarios; registro de bases del INE no descargadas (EPHC trimestral, IPM 2016-2023, transacciones EIGyCV) |
| `13_analisis_2022/` | **Base distrital 2022 y primeras estimaciones**: IPM rural, NBI y servicios del Censo 2022 contra % de red de tierra (GRIP 2018), lluvia CHIRPS e interacción; informe con resultados y limitaciones (`INFORME_estimaciones_2022.md`) |
| `14_analisis_localidad_2022/` | **Análisis por localidad rural (Censo 2022)**: distancia de cada localidad al camino de todo tiempo más cercano, al asfalto y al empedrado, composición de la red en 3 km, días de lluvia intensa y distancia a escuelas y puestos de salud, frente a vivienda, servicios y bienes, comparando localidades del mismo distrito (`INFORME_localidades_2022.md`) |
| `15_analisis_departamental_did/` | **Antes y después de las obras del MOPC (2018-2025)**: adjudicaciones del MOPC (DNCP) clasificadas y ubicadas por departamento, grupos de tratamiento y control, hogares de la EPHC 2017-2025 (rural y urbano), luz nocturna y lluvia por departamento × área; diferencias en diferencias, triple diferencia y estudio de eventos (`INFORME_departamental_did.md`) |
| `16_analisis_censal_nbi_2012_2022/` | **NBI por distrito, Censo 2012 frente a Censo 2022**: obras del MOPC en caminos vecinales 2012-2020 ubicadas por distrito, distritos con y sin obra antes y después; complemento con luz nocturna 2012-2024 alrededor de la primera obra (`INFORME_censal_nbi_2012_2022.md`) |
| `17_inversion_vial_todas_entidades/` | **Inversión vial de municipios y MOPC frente al NBI 2012-2022**: obras viales de las 228 municipalidades (ubicadas por el comprador) clasificadas en rurales y urbanas, más el MOPC ubicado; plan de análisis fijado antes de estimar (`PLAN_DE_ANALISIS.md`, `INFORME_inversion_vial_todas_entidades.md`) |
| `18_tramos_georreferenciados/` | **Tramos de obras vecinales del MOPC en el mapa (2012-2025)**: extremos leídos de los lotes y ubicados en localidades del Censo 2022, con revisión manual; escuelas y puestos de salud rurales cerca de cada tramo (`LEEME.md`) |
| `_arquitectura/` | Catálogo maestro de fuentes, claves y uniones, control de calidad y fuentes pendientes |
| `_equipo_agentes/` | Fichas TLDR de los agentes: ciencia de datos, infraestructura, economía y social |
| `_scripts/` | Scripts en Python para descargar y procesar (para reproducir el armado). Las rutas de los scripts apuntan a `/home/user/repositorio_caminos_vecinales`: ajustarlas a tu carpeta local |

## Claves para unir las bases

- **Distrito:** `cod_dist` de 4 dígitos (INE 2022) = P-code de OCHA/HeiGIT/CHIRPS sin el prefijo `PY` (p. ej., `PY0601` → `0601`, Caazapá).
- **Departamento:** `DPTO` en la EPHC (numérico, 0-17) = `cod_dpto` (2 dígitos).
- **Área:** `AREA` en la EPHC: 1 = urbana, 6 = rural.
- La EPHC **no trae código de distrito**: se une a nivel departamento × área.

## Errores de origen detectados (y cómo se trataron)

1. **MOPC – Misiones:** el PDF `08_misiones_corte_dic2025.pdf` trae la tabla de Itapúa. Misiones quedó sin dato en la tabla de km.
2. **Censo 2022, Cuadro A1:** el encabezado de Cordillera dice "Departamento Concepcion". En la base integrada los departamentos se asignaron por orden.
3. **Mapa de pobreza distrital:** el Excel enlazado en datos.gov.py da error 404. Solo están los PDF.
4. **Población WorldPop (HeiGIT) vs. Censo:** en algunos distritos difieren mucho (p. ej., San Alfredo). Para tasas, usar los RAI de HeiGIT (que comparten denominador) y la población del censo para ponderar.

## Luces nocturnas (VIIRS)

- Fuente: Annual VNL V2 (Elvidge et al., 2021, *Remote Sensing* 13(5):922), copia abierta en Zenodo (doi:10.5281/zenodo.17294744, CC BY 4.0). El original en eogdata.mines.edu pide una cuenta gratuita.
- Unidad armonizada: nW/cm²/sr. La copia de Zenodo trae 2012-2021 multiplicado por 10 y 2022-2024 sin multiplicar; acá todo quedó en la misma escala (verificado: la serie nacional no salta entre 2021 y 2022).
- Calculado por distrito con los límites COD-AB de OCHA (`05_cartografia_y_codigos/COD-AB_OCHA_limites_admin/pry_admin_boundaries.gdb.zip`): cubre los 263 distritos, incluidos los 13 nuevos de 2022. Las columnas `luz_*` ya están en la base distrital integrada.
- Limitaciones: valores enteros (precisión de 1 nW), así que la luz rural muy tenue queda en 0; 2012 cubre solo abril-diciembre; hay píxeles atípicos (incendios) en 2012 y 2018.
- Uso sugerido: resultado anual por distrito para el diseño de diferencias en diferencias escalonado (antes y después de la mejora de caminos).

## Advertencias para el análisis

- La correlación exploratoria RAI–IPM rural (ρ = −0,40 en los 85 distritos foco) es **transversal**: no prueba causalidad. Para eso hacen falta variación temporal (obras del MOPC, cambio de superficie 2020-2024 de Planet, informes de clausuras) o la evaluación del BID.
- Los indicadores ED10/S05 de la EPHC tienen pocos casos por departamento: usar el período 2022-2025 juntado y reportar los tamaños muestrales (`*_n`).
- Los datos de los informes diarios de clausuras salieron de PDF de forma automática: revisar antes de publicar resultados.
- Licencias: los datos del Estado paraguayo están bajo la Licencia de Uso de la Información Pública; OSM y HeiGIT-Mapillary, bajo ODbL; HeiGIT-accesibilidad, bajo CC BY-SA; CHIRPS, bajo CC BY.
