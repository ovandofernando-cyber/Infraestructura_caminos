# Ficha económica (TLDR) — agente ECONOMÍA, 19/10/2026

**Canales por los que el camino vecinal afecta el bienestar rural**
1. Costo de transporte (t-km, fletes más caros e inviables con lluvia en caminos de tierra) → menor precio en finca (brecha finca–mercado).
2. Acceso a mercados: menos días transitables → pérdidas poscosecha, venta a intermediario/acopiador local, menos cultivos perecibles (hortalizas, mandioca) y más cultivos que se pueden almacenar (sésamo, soja).
3. Ingreso y composición: ingreso agropecuario frente a no agropecuario; empleo asalariado y en servicios en centros urbanos cercanos.
4. Insumos y crédito: costo de fertilizantes y semillas; acceso a sucursales (CAH, BNF) y asistencia técnica.
5. Finanzas locales: royalties y FONACIDE financian el mantenimiento de caminos municipales (sirven como insumo y como control).

**Variables, fuentes y clave de unión**
| Canal | Variable | Fuente (ruta) | Clave |
|---|---|---|---|
| Producción | ha, t, kg/ha por cultivo 2017/18 y 2020/21 | MAG-DCEA, 10_economia_y_mercados/MAG_sintesis_estadistica/ | cod_dpto |
| Producto regional | crecimiento PIB 2022-23, PIB per cápita 2023, estructura sectorial | BCP CRA, 10_economia_y_mercados/BCP_cuentas_regionales/ | cod_dpto |
| Finanzas municipales | royalties 2025; royalties, FONACIDE y juegos de azar 2024 | MEF, MEF_royalties_municipios/ y MEF_transferencias_municipios/ | cod_dist |
| Crédito rural | desembolsos CAH 2017-2021 | CAH, credito_rural/ | cod_dpto |
| Ingreso y empleo | ingreso laboral agropecuario, ocupación | EPHC (ya en 01_condiciones_de_vida/) | DPTO×AREA |
| Destino de la producción y crédito | ventas, acceso a crédito por finca | CAN 2022 (ya en 06_) | cod_dpto |
| Servicios financieros | bancos y cajeros (OSM HOT) | ya en 04_servicios_e_instituciones/ | coordenadas → cod_dist |

**Qué agregué (todo validado contra los totales del documento original; ver _fuentes_economia.csv)**
- 7 CSV, unos 150 KB. Los PDF no se pudieron bajar con curl porque el proxy bloquea casi todos los dominios .gov.py. Las tablas se transcribieron con el lector web y se verificaron por suma: royalties 2025 coincide exacto con el total; MAG, suma de departamentos = total país.
- La serie CAH sale de un gráfico y el pareo departamento–valor es inferido: usar con cautela.

**Vacíos (alta prioridad para descarga manual)**
- Anexo xlsx de las CRA del BCP (niveles de PIB por departamento y actividad).
- Precios mayoristas del DAMA (datos.gov.py) y precios WFP (HDX).
- No hay serie pública de precios en finca por departamento ni de crédito bancario por departamento.
- Silos y acopios (OSM o SENAVE): no accesibles.
- Fletes: estudio BID 2023, PDF inaccesible.
- MAG solo llega a nivel departamento: no hay producción por distrito fuera del CAN 2022.

**Estrategia de identificación sugerida**
1. **Diferencias en diferencias escalonadas (event study):** distritos con obra vial DNCP/MOPC adjudicada o terminada (08_contrataciones_DNCP, por año de adjudicación) frente a distritos aún no tratados. Resultados: IPM/NBI (cortes 2012 y 2022), riqueza relativa Meta, superficie de cultivos perecibles, transferencias y recaudación municipal. Usar el estimador de Callaway–Sant'Anna o Sun–Abraham para evitar el sesgo de efectos heterogéneos.
2. **Shock de lluvia × superficie:** lluvia CHIRPS mensual (07_) × proporción de km de tierra del distrito (03_ MOPC/Mapillary). Hipótesis: la lluvia extrema reduce el acceso y el ingreso donde hay más tierra. Con la EPHC (trimestre de entrevista × departamento × área rural) se puede estimar ingreso agropecuario ~ lluvia × %tierra con efectos fijos de departamento y año.
3. **Heterogeneidad:** efectos mayores en cultivos perecibles (mandioca, hortalizas) que en almacenables (sésamo, soja), y en distritos lejos de rutas nacionales (RAI/HeiGIT).
4. **Controles y amenazas:** las obras siguen criterios políticos o productivos (soja), por lo que conviene emparejar por tendencia previa de producción y por royalties per cápita. Los royalties siguen fórmula legal y sirven como control, no como instrumento.
