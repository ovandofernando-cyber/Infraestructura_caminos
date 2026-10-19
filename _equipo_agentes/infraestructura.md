# Infraestructura vial — ficha TLDR (agente infraestructura, 19/10/2026)

**Operacionalizar "camino vecinal de todo tiempo" (CTT)**
- Definición del programa BID PR-L1084 (PCR): un camino es CTT si está transitable el 100 % de los días del año. Indicador R.2.2 "% de días transitables": la línea de base de los vecinales de tierra era 75 % (de 40 a 90 días cerrados por año, estimado con lluvia).
- Proxy por superficie: CTT = pavimento + empedrado + ripio. No CTT = tierra. Fuentes: MOPC km por red y superficie a dic-2025 (nivel departamento) y superficie HeiGIT Mapillary/Planet (línea → distrito).
- Proxy por lluvia: cruzar las clausuras de rutas y puentes de 2026 con CHIRPS (07_clima) para obtener días de cierre esperados por distrito.

**Calidad del camino: indicadores sugeridos por distrito (cod_dist)**
1. % de km no pavimentados sin ripio ni empedrado (HeiGIT `surface` + OSM HOT `highway`).
2. Densidad vial (km/km² y km/1.000 hab rurales): OSM HOT + Censo 2022.
3. RAI: % de población rural a ≤2 km de un camino de todo tiempo (HeiGIT PRY_ADM2_rai).
4. Distancia o tiempo a la ruta pavimentada más cercana (HeiGIT access; OSM `paved`).
5. Puentes de madera por cada 100 km de vecinal (NUEVO: puentes georreferenciados del BID) y clausuras de puentes (03/estado_rutas).
6. Exposición a tratamiento: tramos mejorados PR-L1084 o PR-L1092 en el distrito (NUEVO), y km de vecinales mejorados según DNCP.

**Fuentes agregadas (11_infraestructura_vial_complementaria/)**
- BID PR-L1084: 14 tramos tratados (392 km, todos en 02/05/06/14) en XLSX y CSV. 169 puentes de madera con lon/lat (foco: 01=9, 02=11, 05=10, 06=21, 14=26). Distritos más pobres (XLS) y pobreza distrital (PDF). PCR (55 p.) y RED ex post.
- BID PR-L1092 (PMCV II, en ejecución): candidatos de caminos y puentes con TMDA, población servida y estado.
- Línea de base de la evaluación de impacto BID 2018 (3.000 hogares, 172 comunidades, PSM+DiD): indicadores transcriptos. Ejemplo: en época de lluvias el viaje tarda 46 min más en las zonas tratadas.
- `_fuentes_infraestructura.csv`: 16 fuentes con estado y URL.

**Vacíos (sin acceso desde este entorno: el proxy bloquea .gov.py, WB docs, CAF, PBL)**
- datos.gov.py tema transporte: no se pudo revisar, queda pendiente. Presupuesto MEF por programa. Estadísticas de microempresas del MOPC. INDERT y asentamientos.
- GRIP (268 MB, sin acceso) y Overture: no se descargaron porque OSM HOT ya los cubre.
- No hay inventario oficial de la red vecinal (geometrías) por distrito ni serie de transitabilidad medida. Microdatos de la evaluación de impacto: solicitarlos al BID o al MOPC-DCV.
- Endogeneidad: los tramos se eligieron por pobreza (EEO_15) y por Planes Viales Participativos. Usar DiD o controles de la línea de base.

**Cómo se unen**
- Tablas BID: nombre de distrito en texto → cod_dist de 4 dígitos (INE 2022) mediante tabla de nombres normalizados (sin tildes). Hay que revisarlo a mano porque los nombres vienen abreviados ("Nva. Germania", "San J.Nepomuceno").
- Puentes: lon/lat (EPSG:4326) → spatial join con los polígonos censales 2022 (05_cartografia) → cod_dist; cod_dpto = primeros 2 dígitos.
- Departamento: cod_dpto de 2 dígitos (01, 02, 05, 06, 14). ICR del Banco Mundial (P082026): datos solo para 02/05/06.
