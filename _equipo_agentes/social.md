# Ficha SOCIAL (TLDR): acceso a servicios e instituciones

**Variables útiles para la hipótesis** (caminos de todo tiempo → acceso a servicios y mercados), por distrito (`cod_dist`):
- **Salud:** % de población a 30 min/1 h de un hospital o de atención primaria (HeiGIT, 04/); USF y hospitales con coordenadas (MSPBS, 04/estableciminetos-sanitarios); healthsites.
- **Educación:** % de población a 5/10/20 km de una escuela (HeiGIT); escuelas de OSM-HOT. *Faltan los locales del MEC con coordenadas.*
- **Electricidad (nuevo):** HREA 2013/2020: probabilidad media de que un asentamiento esté electrificado, ponderada por población, y % de población con probabilidad ≥0,8. En la mediana de los distritos foco, 45 % de la población vive en asentamientos con probabilidad ≥0,8; en el resto del país, 66 %.
- **Conectividad (nuevo):** Ookla 2025T4-2026T3: Mbps de bajada y subida y latencia, en móvil y en fijo, ponderados por cantidad de tests. Mediana de bajada fija: 98 Mbps en los distritos foco y 123 Mbps en el resto.
- **Instituciones (nuevo):** conteos de OSM por distrito: comisarías, municipalidades, juzgados, correo, mercados, bancos y cajeros, farmacias, terminales, torres o antenas, infraestructura de agua.
- **Agua y saneamiento:** NBI sanitaria (01/) y SENASA por departamento 2018 (04/anuario). Es débil.

**Fuentes agregadas** en `09_servicios_complementarios/` (registro: `_fuentes_social.csv`):
1. `Ookla_open_data_conectividad/`: teselas de Paraguay en GPKG (4 trimestres) y CSV por distrito, uno por trimestre más un archivo `_largo` con los cuatro.
2. `HREA_acceso_electricidad/`: rasters COG (prplit 2013 y 2020, población de asentamientos) y `hrea_electrificacion_por_distrito_2013_2020.csv`.
3. `OSM_HOT_points_of_interest/`: GPKG zip y `osm_poi_institucionales_por_distrito.csv`.
Los scripts que las reproducen están en `_scripts/social_ookla.py`, `social_hrea_distrito.py` y `social_poi_distrito.py` (correr con `python3 -I`).

**Advertencias**
- HREA se basa en luces nocturnas: subestima la electrificación rural, porque ANDE y la EPHC reportan más de 98 %. Sirve para comparar distritos entre sí, no como nivel de cobertura.
- Ookla mide tests hechos por usuarios. Que un distrito no tenga tests (≈12 % en móvil en los foco) no prueba que no haya cobertura, y la selección de quién hace tests está sesgada.
- OSM está mejor cargado en zonas urbanas: los conteos son mínimos, no un censo.

**Vacíos** (sitios bloqueados por el proxy de esta sesión; quedaron registrados como `sin_acceso` con su URL):
- Locales escolares y matrícula del MEC (datos.mec.gov.py).
- Prestadores de agua por distrito (SENASA y ERSSAN, juntas de saneamiento).
- Clientes de ANDE por localidad.
- Cobertura móvil de CONATEL y antenas de OpenCelliD.
- Programas sociales por distrito: Tekoporã, pensión de adultos mayores, Hambre Cero.
- Capa georreferenciada de comunidades indígenas del INDI. La población indígena por comunidad y distrito ya está en 02/iv-censo-indígena.
- Overture Maps: el bucket es accesible, pero solo publica GeoParquet, que necesita pyarrow o duckdb.
- Servicios de la vivienda del Censo 2022 (agua, luz, internet) por distrito: conviene buscarlos en el INE.

**Cómo se une al resto**
- Todos los CSV nuevos traen `cod_dpto` (2 dígitos) y `cod_dist` (4 dígitos), tomados de la columna CLAVE de `05_cartografia_y_codigos/.../Distritos GEOJSON.geojson`.
- Coinciden con los 263 `cod_dist` de `00_base_integrada/base_distrital_integrada.csv`; los nombres difieren solo en tildes.
- Unir siempre por `cod_dist` guardado como texto, para conservar el cero inicial.
- Los puntos y teselas originales se pueden volver a asignar por join espacial (EPSG:4326).
