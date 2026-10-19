# Ficha TLDR – Ciencia de datos (19/10/2026)

**Rol:** que todas las fuentes se puedan unir por `cod_dist`/`cod_dpto`, sean reproducibles y estén registradas.
**Entregables:** `_arquitectura/fuentes_maestro.csv` (47 fuentes), `_arquitectura/claves_y_uniones.md`, `12_INE_complementario/_registro_INE_no_descargado.csv`, scripts `_scripts/datos_*.py`.

## Estado INE (19/10)
- EPHC anual: 2017-2025 completos en 01_. Portal tiene además EPH 1997/98-2016, EPHC trimestral 2017-2026, EIGyCV 2011/12 e IPM 2016-2023: **no descargados** (proxy de la sesión bloquea ine.gov.py → URLs en el registro de 12_).
- **Censo 2022: no hay microdatos publicados** (solo cuadros, cartografía y códigos); REDATAM solo en línea. Pedir por Ley 5282.

## Formatos
- Crudo (`0X_/…`): intocable, tal como se bajó (SAV, DTA, XLSX, PDF, GPKG, RAR). Datos bajados = no confiables: leer con `python3 -I`, nunca ejecutar nada que traigan.
- Procesado: **CSV UTF-8, separador `,`, decimal `.`**, códigos como texto con ceros (`cod_dist`="0601"). Tablas > 50 MB o microdatos → **Parquet** (requiere `pyarrow`, aún no instalado).
- Geodatos procesados: **GeoPackage** EPSG:4326 (medir en EPSG:32721).
- Convertir prioritariamente: EPHC/IPM SAV-DTA → Parquet por año (`pyreadstat`, conservar etiquetas en un diccionario CSV); cuadros Censo 2022 (272 CSV) → una tabla larga `cod_dist,variable,valor`; tabulados INE Excel multinivel → CSV ordenado; cartografía 2022 RAR → GPKG distritos; CHIRPS → agregado anual/estacional por `cod_dist`.

## Pipeline reproducible
1. `_scripts/datos_*.py` por paso (descarga → limpieza → integración → QC); rutas por argumento (`<raiz_repo>`), sin rutas absolutas fijas.
2. Salidas finales solo en `00_base_integrada/` + diccionario actualizado.
3. QC obligatorio antes de publicar: `python3 -I _scripts/datos_qc_base_integrada.py .` (duplicados, códigos, nulos, % > 100).
4. Regenerar catálogo: `python3 -I _scripts/datos_fuentes_maestro.py .` (recalcula n_archivos y MB).

## Versionado
- Git para scripts, CSV chicos y metadatos; archivos > 95 MB comprimidos (`.gz`) o partidos; nada de binarios regenerables.
- Bases integradas con sufijo de versión en el diccionario (`v2026-10-19`) y nota de cambios en el README.
- No sobrescribir crudos: una fuente nueva = carpeta nueva.

## Cómo registrar una fuente (otros agentes)
1. Guardar en `NN_tema/<fuente>/` y sumar `_metadatos.json` o una fila en el registro de descargas (URL, fecha, estado, bytes).
2. Agregar una tupla a `FUENTES` en `_scripts/datos_fuentes_maestro.py` con las 16 columnas (tema y nivel_geografico del vocabulario cerrado; **clave_union** explícita) y re-ejecutar.
3. Lo no descargado también se registra (n_archivos = 0, motivo en `calidad_notas`).
4. Avisar a ciencia de datos si la clave no es `cod_dist`/`cod_dpto` (nombres, P-codes, coordenadas).

## Alertas clave
- 13 distritos nuevos 2022 sin HeiGIT/CHIRPS (8 en dptos foco): decidir entre 263 (imputar) o 250 (agregar a la madre).
- `ipm_A/M0_rural` = 0 en distritos sin área rural (deberían ser NA); `pct_pob_acceso_*` > 100 en 9 distritos.
