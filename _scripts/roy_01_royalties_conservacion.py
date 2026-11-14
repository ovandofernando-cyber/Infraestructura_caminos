# Propuesta de financiamiento del mantenimiento con royalties (26_royalties_conservacion_vial): cuánto necesita el plan
# del equipo (9 tramos PR-L1084, 301,8 km) y la red vecinal mejorada de los 4 departamentos, y qué porcentaje de los
# royalties de municipios y gobernaciones haría falta, con y sin contrapartida del MOPC.
# Royalties de gobernaciones: no hay planilla; se estiman con las proporciones del art. 1 de la Ley 3984/2010
# (municipios 40 % del total; gobernaciones afectadas 5 % en partes iguales entre 5; no afectadas 5 % entre 12).
import numpy as np, pandas as pd, geopandas as gpd

R = '/home/user/infraestructura_caminos'; OUT = R + '/26_royalties_conservacion_vial'
TC = 7566
D4 = {'02': 'San Pedro', '05': 'Caaguazú', '06': 'Caazapá', '14': 'Canindeyú'}
AFECTADAS = ['10', '14', '07', '08', '12']
roy = pd.read_csv(R + '/10_economia_y_mercados/MEF_royalties_municipios/royalties_municipios_2025.csv', dtype={'cod_dist': str, 'cod_dpto': str})
tot_mun = roy.royalties_liquidado_2025_gs.sum()
total = tot_mun / 0.40
gob = {c: (total * 0.05 / 5 if c in AFECTADAS else total * 0.05 / 12) for c in D4}

# Distritos que atraviesan los 9 tramos PR-L1084 (trazado aproximado)
t = gpd.read_file(R + '/11_infraestructura_vial_complementaria/BID_tramos_intervenidos_1084_1092/tramos_intervenidos_BID_1084_1092.gpkg')
t9 = t[t.operacion.str.contains('1084')]
dist = gpd.read_file(R + '/05_cartografia_y_codigos/COD-AB_OCHA_limites_admin/pry_admin_boundaries.gdb.zip', layer='pry_admin2')[['adm2_pcode', 'adm2_name', 'geometry']].to_crs(32721)
j = gpd.overlay(t9[['orden', 'km', 'geometry']].explode(index_parts=False), dist, how='intersection', keep_geom_type=True)
j['km_en_distrito'] = j.length / 1000; j['cod_dist'] = j.adm2_pcode.str[2:]
dd = j.groupby(['cod_dist', 'adm2_name']).km_en_distrito.sum().reset_index().merge(roy[['cod_dist', 'royalties_liquidado_2025_gs']], on='cod_dist')
dd.to_csv(OUT + '/distritos_atravesados_9_tramos.csv', index=False, encoding='utf-8-sig')
print(dd.round(1).to_string()); print('Royalties 2025 de los distritos atravesados (mil millones Gs):', round(dd.royalties_liquidado_2025_gs.sum() / 1e9, 1))

inv = pd.read_csv(R + '/03_red_vial_MOPC/MOPC_inventario_km_por_red_y_superficie_dic2025.csv', dtype={'cod_dpto': str})
v = inv[inv.red == 'VECINAL'].set_index('cod_dpto'); v['km_mejorado'] = v.km_total - v.km_tierra_T
filas = []
for c, nom in D4.items():
    m = roy[roy.cod_dpto == c].royalties_liquidado_2025_gs.sum()
    filas.append(dict(cod_dpto=c, departamento=nom, royalties_municipios_2025_gs=m, royalties_gobernacion_2025_gs_estimado=gob[c],
                      km_9_tramos=t9[t9.departamento.str.startswith(nom[:5])].km.sum(), km_red_vecinal_mejorada=v.loc[c, 'km_mejorado']))
T = pd.DataFrame(filas)
T['royalties_total_gs'] = T.royalties_municipios_2025_gs + T.royalties_gobernacion_2025_gs_estimado
esc = []
for nom_red, col in [('Plan del equipo: 9 tramos (301,8 km)', 'km_9_tramos'), ('Red vecinal mejorada de los 4 dptos.', 'km_red_vecinal_mejorada')]:
    for costo in [4500, 2600]:
        nec = (T[col] * costo * TC).sum()
        for match in [0, 0.5]:
            local = nec * (1 - match)
            esc.append(dict(red=nom_red, km=T[col].sum(), costo_usd_km_anio=costo, contrapartida_mopc=match,
                            necesidad_anual_mm_gs=nec / 1e9, aporte_local_mm_gs=local / 1e9,
                            pct_royalties_mun_y_gob=100 * local / T.royalties_total_gs.sum(),
                            pct_si_solo_municipios=100 * local / T.royalties_municipios_2025_gs.sum()))
E = pd.DataFrame(esc)
T.to_csv(OUT + '/royalties_y_km_4_departamentos.csv', index=False, encoding='utf-8-sig'); E.to_csv(OUT + '/porcentaje_necesario.csv', index=False, encoding='utf-8-sig')
print(T.assign(**{c: T[c] / 1e9 for c in ['royalties_municipios_2025_gs', 'royalties_gobernacion_2025_gs_estimado', 'royalties_total_gs']}).round(1).to_string())
print(E.round(1).to_string())
# Recaudación de una asignación del 5 % por departamento
T['aporte_5pct_mm_gs'] = 0.05 * T.royalties_total_gs / 1e9
T['km_cubiertos_5pct_4500'] = 0.05 * T.royalties_total_gs / (4500 * TC)
T['km_cubiertos_5pct_4500_con_mopc'] = 2 * T.km_cubiertos_5pct_4500
print(T[['departamento', 'aporte_5pct_mm_gs', 'km_9_tramos', 'km_red_vecinal_mejorada', 'km_cubiertos_5pct_4500', 'km_cubiertos_5pct_4500_con_mopc']].round(1).to_string())
print('Totales 5 %:', round(T.aporte_5pct_mm_gs.sum(), 1), 'mil millones Gs =', round(T.aporte_5pct_mm_gs.sum() * 1e9 / TC / 1e6, 2), 'M USD')
T.to_csv(OUT + '/royalties_y_km_4_departamentos.csv', index=False, encoding='utf-8-sig')
