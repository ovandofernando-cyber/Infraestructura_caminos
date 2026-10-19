# Repositorio de datos: caminos vecinales y condiciones de vida rural

**Pregunta:** ¿cómo influye la calidad de los caminos vecinales en las condiciones de vida de la población rural de los departamentos más pobres de la Región Oriental?

**Hipótesis:** la falta de caminos vecinales de todo tiempo afecta la calidad de vida rural porque limita el acceso a servicios básicos y la comercialización de la producción.

**Departamentos foco:** Concepción (01), San Pedro (02), Caaguazú (05), Caazapá (06) y Canindeyú (14).

Armado el 17/10/2026 con descargas desde INE, datos.gov.py, MOPC, MAG, DNCP y HDX. El catálogo completo, con el estado de cada fuente, está en `catalogo_bases_caminos_vecinales.xlsx` (en esta misma carpeta). La lista de todos los archivos está en `_inventario_archivos.csv`.

Ampliado el 19/10/2026 por el equipo de agentes (carpetas 09 a 12). **La arquitectura de la base (fuente, periodicidad, nivel, claves) está en [`ARQUITECTURA_BASE_DE_DATOS.md`](ARQUITECTURA_BASE_DE_DATOS.md)** y el catálogo de las 90 fuentes en `_arquitectura/fuentes_maestro.csv`.

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
| `07_clima_y_contexto/` | Lluvia CHIRPS por departamento y distrito 1981-2026; índice de riqueza relativa (Meta); WorldPop 2020 |
| `08_contrataciones_DNCP/` | Llamados públicos de obras viales 2018-2026 (API OCDS de la DNCP) |
| `09_servicios_complementarios/` | Conectividad a internet Ookla (trimestral), electrificación HREA 2013/2020 e instituciones OSM (comisarías, municipios, bancos, mercados), todo también por distrito |
| `10_economia_y_mercados/` | Royalties 2025 y transferencias 2024 a municipios (MEF), producción agrícola por departamento (MAG), PIB departamental (BCP), crédito CAH |
| `11_infraestructura_vial_complementaria/` | Programas BID de caminos vecinales: tramos mejorados, 169 puentes de madera georreferenciados, informe de cierre, línea de base de la evaluación de impacto |
| `12_INE_complementario/` | Registro de bases del INE pendientes de descarga (EPH 1997-2016, EPHC trimestral, EIGyCV) |
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

## Advertencias para el análisis

- La correlación exploratoria RAI–IPM rural (ρ = −0,40 en los 85 distritos foco) es **transversal**: no prueba causalidad. Para eso hacen falta variación temporal (obras del MOPC, cambio de superficie 2020-2024 de Planet, informes de clausuras) o la evaluación del BID.
- Los indicadores ED10/S05 de la EPHC tienen pocos casos por departamento: usar el período 2022-2025 juntado y reportar los tamaños muestrales (`*_n`).
- Los datos de los informes diarios de clausuras salieron de PDF de forma automática: revisar antes de publicar resultados.
- Licencias: los datos del Estado paraguayo están bajo la Licencia de Uso de la Información Pública; OSM y HeiGIT-Mapillary, bajo ODbL; HeiGIT-accesibilidad, bajo CC BY-SA; CHIRPS, bajo CC BY.
