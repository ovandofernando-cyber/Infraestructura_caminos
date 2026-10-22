# "Lejos del camino" vs "lejos del servicio": distancia de cada localidad a la escuela básica, el colegio,
# la atención primaria de salud y el hospital más cercanos (geoportal INE), y modelos que separan ambos factores.
import numpy as np, pandas as pd, geopandas as gpd, statsmodels.formula.api as smf

R = '/home/user/infraestructura_caminos'
OUT = R + '/14_analisis_localidad_2022'
CRS_M = 32721
ORIENTAL = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '12', '13', '14']
FOCO = ['01', '02', '05', '06', '14']
INE = R + '/09_servicios_complementarios/INE_geoportal_capas/'

b = pd.read_csv(OUT + '/base_localidades_2022.csv', dtype={'cod_dist': str, 'cod_dpto': str, 'bl': str})
g = gpd.read_file(R + '/05_cartografia_y_codigos/COD-AB_OCHA_limites_admin/pry_admin_boundaries.gdb.zip', layer='pry_admin3')[['adm3_pcode', 'geometry']]
g = g[g.adm3_pcode.isin(b.adm3_pcode)].to_crs(CRS_M)
pts = g.copy(); pts['geometry'] = g.geometry.representative_point()

edu = gpd.read_file(INE + 'locales_educativos_INE.gpkg').to_crs(CRS_M)
sal = gpd.read_file(INE + 'puestos_salud_publicos_INE.gpkg').to_crs(CRS_M)
capas = {'dist_escuela_basica_km': edu[edu.desc_class == 'EDUCACION BASICA'],
         'dist_colegio_km': edu[edu.desc_class == 'COLEGIOS'],
         'dist_salud_primaria_km': sal[sal.desc_categ.isin(['USF', 'PUESTO DE SALUD', 'CENTRO DE SALUD'])],
         'dist_hospital_km': sal[sal.desc_categ.str.startswith('HOSPITAL')]}
dist = pd.DataFrame({'adm3_pcode': pts.adm3_pcode.values})
for col, lay in capas.items():
    j = gpd.sjoin_nearest(pts[['adm3_pcode', 'geometry']], lay[['geometry']], distance_col='d')
    dist[col] = (j.groupby('adm3_pcode').d.min() / 1000).reindex(pts.adm3_pcode).round(3).values
dist.to_csv(OUT + '/distancias_servicios_localidades_2022.csv', index=False, encoding='utf-8-sig')

# ---------- muestra (la misma del análisis principal) ----------
d = b.merge(dist, on='adm3_pcode', how='left')
s = d[(d.area == 'rural') & d.cod_dpto.isin(ORIENTAL) & (d.viviendas_ocupadas >= 10)].dropna(
    subset=['dist_todo_tiempo_km', 'pct_piso_tierra', 'luz_media_2013', 'dist_capital_distrito_km']).copy()
s['foco'] = s.cod_dpto.isin(FOCO).astype(int)
z = lambda x: (x - x.mean()) / x.std()
s['indice_privaciones'] = pd.concat([z(s.pct_piso_tierra), z(s.pct_cocina_lena), z(s.pct_sin_bienes),
                                     z(100 - s.pct_electricidad), z(100 - s.pct_agua_corriente)], axis=1).mean(axis=1)
for c in ['dist_todo_tiempo_km', 'dist_capital_distrito_km'] + list(capas):
    s['l_' + c.replace('_km', '')] = np.log1p(s[c])
s['log_pob'] = np.log(s.poblacion.clip(lower=1)); s['log_area'] = np.log(s.area_km2); s['log_luz13'] = np.log1p(s.luz_media_2013)
CTRL = 'log_pob + log_area + l_dist_capital_distrito + log_luz13'
SERV = 'l_dist_escuela_basica + l_dist_colegio + l_dist_salud_primaria + l_dist_hospital'
fit = lambda f, dd: smf.wls(f, data=dd, weights=dd.viviendas_ocupadas).fit(cov_type='cluster', cov_kwds={'groups': dd.cod_dist})

rows = []
def add(m, modelo, resultado, vs):
    for v in vs:
        rows.append(dict(resultado=resultado, modelo=modelo, variable=v, coef=m.params[v], ee_cluster_distrito=m.bse[v], p=m.pvalues[v], n=int(m.nobs), r2=m.rsquared))

OUTS = {'indice_privaciones': 'Índice de privaciones (desvíos estándar)', 'pct_piso_tierra': '% viviendas con piso de tierra',
        'pct_cocina_lena': '% viviendas que cocinan con leña', 'pct_electricidad': '% viviendas con electricidad',
        'pct_agua_corriente': '% viviendas con agua corriente', 'pct_vehiculo': '% viviendas con vehículo'}
for y, lab in OUTS.items():
    m0 = fit(f'{y} ~ l_dist_todo_tiempo + {CTRL} + C(cod_dist)', s)
    m1 = fit(f'{y} ~ {SERV} + {CTRL} + C(cod_dist)', s)
    m2 = fit(f'{y} ~ l_dist_todo_tiempo + {SERV} + {CTRL} + C(cod_dist)', s)
    add(m0, 'E0: solo camino', lab, ['l_dist_todo_tiempo'])
    add(m1, 'E1: solo servicios', lab, SERV.split(' + '))
    add(m2, 'E2: camino + servicios', lab, ['l_dist_todo_tiempo'] + SERV.split(' + '))
# ¿Los servicios están donde están los caminos?
for c in capas:
    m = fit(f'l_{c.replace("_km","")} ~ l_dist_todo_tiempo + {CTRL} + C(cod_dist)', s)
    add(m, 'F: distancia al servicio como resultado', 'log(1+' + c + ')', ['l_dist_todo_tiempo'])
# ¿El camino importa más cuando el servicio está lejos? (interacción)
for c in ['dist_colegio_km', 'dist_salud_primaria_km']:
    v = 'l_' + c.replace('_km', '')
    m = fit(f'indice_privaciones ~ l_dist_todo_tiempo * {v} + {CTRL} + C(cod_dist)', s)
    add(m, f'G: interacción camino × {c.replace("dist_","").replace("_km","")}', OUTS['indice_privaciones'], ['l_dist_todo_tiempo', v, f'l_dist_todo_tiempo:{v}'])
# Cuadro 2x2: lejos del camino (> 5 km) × lejos de atención primaria (> 5 km)
s['lejos_camino'] = np.where(s.dist_todo_tiempo_km > 5, 'Lejos del camino (> 5 km)', 'Cerca del camino (≤ 5 km)')
s['lejos_salud'] = np.where(s.dist_salud_primaria_km > 5, 'Lejos de atención primaria (> 5 km)', 'Cerca de atención primaria (≤ 5 km)')
s['grupo'] = s.lejos_camino + ' · ' + s.lejos_salud
ref = 'Cerca del camino (≤ 5 km) · Cerca de atención primaria (≤ 5 km)'
m = fit(f'indice_privaciones ~ C(grupo, Treatment(reference="{ref}")) + {CTRL} + C(cod_dist)', s)
add(m, 'H: 2x2 camino × atención primaria (ref. cerca de ambos)', OUTS['indice_privaciones'], [v for v in m.params.index if v.startswith('C(grupo')])
res = pd.DataFrame(rows)
res['variable'] = res.variable.str.replace(r'C\(grupo, Treatment\(reference=".*"\)\)\[T\.', '', regex=True).str.rstrip(']')
res.to_csv(OUT + '/resultados_camino_vs_servicio.csv', index=False, encoding='utf-8-sig')

tab = s.groupby(['lejos_camino', 'lejos_salud']).agg(localidades=('localidad', 'size'), viviendas=('viviendas_ocupadas', 'sum'),
        indice=('indice_privaciones', 'mean'), piso_tierra=('pct_piso_tierra', 'mean'), lena=('pct_cocina_lena', 'mean'),
        electricidad=('pct_electricidad', 'mean'), agua=('pct_agua_corriente', 'mean')).round(2)
tab.to_csv(OUT + '/cuadro_2x2_camino_salud.csv', encoding='utf-8-sig')
dd = s[[c for c in ['dist_todo_tiempo_km'] + list(capas)]]
pd.set_option('display.width', 250)
print('n', len(s)); print(dd.describe(percentiles=[.25, .5, .75, .9]).round(1).to_string())
print(np.log1p(dd).corr().round(2).to_string())
print(tab.to_string())
print(res.round(3).to_string(index=False))
