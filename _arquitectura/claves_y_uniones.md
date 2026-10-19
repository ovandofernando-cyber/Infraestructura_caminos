# Claves y uniones del repositorio (ciencia de datos, 19/10/2026)

Catálogo de fuentes: `fuentes_maestro.csv` (47 filas, una por fuente). Clave maestra: **`cod_dist`** (4 díg. INE 2022 = dpto 2 + distrito 2).

```
 HOGAR/PERSONA (EPHC 2017-2025, IPM)          DISTRITO (cod_dist, 263)                    PUNTO / TRAMO / RÁSTER
 REG01 vivienda  UPM+NVIVI+NHOGA ─┐        ┌─ Censo 2022 cuadros (por NOMBRE → cod_dist)   Tramos: HeiGIT Mapillary, Planet,
 REG02 persona   +L02 ────────────┤        ├─ IPM/NBI distrital (cod_dist)                OSM roads ──intersección con──┐
 INGREFAM hogar  upm+nvivi+nhoga ─┘        ├─ HeiGIT RAI/accesos ('PY'+cod_dist, 250)     polígonos 2022 → km por tipo  │
        │ (sin distrito)                   ├─ CHIRPS ('PY'+cod_dist, 214 ADM2)            Puntos: MSPBS, OSM POI,       │
        ▼ colapsar con FACTOR              ├─ Proyecciones pob. distrital                 healthsites, RWI ──punto-en-──┤
  DPTO (0-17) × AREA (1 urb / 6 rur)       ├─ DNCP (entidad municipal → nombre)           polígono → conteos/medias     │
        │                                  ├─ MOPC clausuras (localidad texto → geocod.)  Ráster: WorldPop ──estadística│
        ▼                                  └──────────┬───────────────────────────────    zonal (suma/media) por distrito
  cod_dpto (2 díg.) ◄──── cod_dist[:2] ◄──────────────┘                                    ▼
  MOPC km por red (dpto), CAN 2022 (dpto)    Cartografía censal 2022 (05_/cartografia_censal_2022_SHP) = capa geométrica de referencia
```

## Reglas de unión
1. **EPHC → dpto×área**: la EPHC no trae distrito. Agregar con `FACTOR` (REG01, REG02; `factor` en INGREFAM) a `DPTO×AREA`; une con `cod_dpto` (`str(DPTO).zfill(2)`). Hogar = `UPM+NVIVI+NHOGA`; persona = + `L02`.
2. **Distrito**: todo lo distrital se normaliza a `cod_dist` texto de 4 dígitos (nunca entero: se pierde el 0 inicial; Asunción = `0000`). P-codes OCHA/HeiGIT/CHIRPS: quitar `PY`.
3. **Por nombre** (Censo cuadros, DNCP, clausuras MOPC): normalizar (mayúsculas, sin tildes, sin "DPTO."), unir contra `Codigos de distritos INE 2022.xlsx` y revisar a mano los no unidos.
4. **Puntos/tramos → distrito**: intersección espacial con la cartografía 2022 (EPSG:4326 → proyectar a UTM 21S, EPSG:32721, para km). Un tramo que cruza límites se corta y se asigna por longitud.
5. **Ráster → distrito**: estadística zonal (suma de población, media de lluvia) sobre polígonos 2022; recalcular CHIRPS/RAI para los distritos nuevos.

## Unidad de análisis recomendada
- **Principal: distrito rural (n = 263; 85 en dptos foco)** — resultado IPM/NBI rural del Censo 2022 + RAI, km de tierra (HeiGIT/OSM), accesos, lluvia, obras DNCP. Ponderar por población rural del censo.
- **Secundaria: dpto×área×año (EPHC 2017-2025)** — mecanismos (ED10, S05, ingresos) con microdatos; solo 15 dptos ⇒ panel corto, usar errores por UPM.
- Futuro: localidad/compañía si se obtienen microdatos del Censo 2022 (no publicados; REDATAM en línea).

## Riesgos
- **Códigos 2012→2022**: los 250 códigos 2012 se conservan en 2022 (6 cambian solo tilde) y hay **13 distritos nuevos** (0112-0114, 0221-0222, 0918, 1306, 1414-1416, 1510-1511, 1606) segregados de otros: HeiGIT, CHIRPS (214 ADM2), tablero STP y cartografía 2012 los asignan al distrito madre ⇒ sesgo en el padre y faltante en el hijo. Opción: análisis con 250 distritos "2012" agregando los nuevos a su madre.
- **Muestras chicas EPHC**: rural por dpto ≈ 25-81 UPM en 2025; ED10/S05 con 284-1.460 casos en 2022-2025 juntos. Reportar `*_n` y CV; no bajar de dpto.
- Denominadores mixtos (WorldPop vs Censo: ratio 0,53-2,71; 47 distritos fuera de [0,7-1,5]).
- Variables explicativas casi todas de 2024-2026 vs. resultado censal 2022: cuidado con causalidad inversa / simultaneidad.
- Extracción automática de PDF (MOPC) y filtros por palabra clave (DNCP): validar muestras.

## Chequeo de calidad de 00_base_integrada (`_scripts/datos_qc_base_integrada.py`)
| Chequeo | Resultado |
|---|---|
| Duplicados `cod_dist` / dpto+nombre | 0 / 0 |
| Códigos inválidos (no 4 díg., prefijo ≠ `cod_dpto`, dpto fuera 00-17) | 0 |
| Cruce con lista oficial INE 2022 (263) | 263/263, nombres idénticos |
| Nulos HeiGIT (RAI, accesos, conteos) | 13 = los distritos nuevos 2022; **8 en dptos foco** (Arroyito, Paso Horqueta, Itacuá, S. V. Pancholo, S. J. del Rosario, Maracaná, Puerto Adela, Laurel) |
| `ipm_H_rural` nulo | 15 (distritos 100 % urbanos) — pero `ipm_A_rural`/`ipm_M0_rural` = **0** en 14 de ellos: recodificar a NA |
| `pct_pob_acceso_*` > 100 % | hasta 9 distritos (CDE 108,9; Nanawa 111,7; Itacurubí de la Cordillera 105,7; Belén 100,9): `access_pop` y denominador no consistentes; truncar a 100 o recalcular |
| `censo urbana + rural = total` | OK en 263; suma = 6.109.903 |
| `heigit_pob_rural` > 0 con censo rural vacío | 11 distritos (definiciones urbano/rural distintas) |
| `dpto_km_*` | repetido por distrito; nulo en 11 (Misiones, Asunción); no usar como variable distrital |
| Base departamental | 15 dptos, sin duplicados; población rural cuadra con la suma distrital; Misiones sin MOPC |
| Otros hallazgos | `03_/rutas_nacionales_KMZ/*.download` es HTML de login de Google Drive (descarga fallida); SHP de `base-de-datos-geojson…` sin .dbf/.shx/.prj (usar GeoJSON) |
