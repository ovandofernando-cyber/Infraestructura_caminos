# Análisis por localidad (Censo 2022): distancia al camino de todo tiempo más cercano y condiciones de vida rural.
# Uso: python3 -I analisis_localidad_2022.py <ruta a heigit_pry_roadsurface_lines.gpkg descomprimido>
import os, sys, numpy as np, pandas as pd, geopandas as gpd, rasterio, statsmodels.formula.api as smf
from rasterio.mask import mask

R = '/home/user/infraestructura_caminos'
OUT = R + '/14_analisis_localidad_2022'
os.makedirs(OUT, exist_ok=True)
ROADS = sys.argv[1]
CRS_M = 32721  # UTM 21S, metros
ORIENTAL = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '12', '13', '14']
FOCO = ['01', '02', '05', '06', '14']
GDB = R + '/05_cartografia_y_codigos/COD-AB_OCHA_limites_admin/pry_admin_boundaries.gdb.zip'

# ---------------- 1. Localidades: censo + polígonos ----------------
c = pd.read_csv(R + '/12_INE_complementario/Censo_2022_indicadores_localidad/censo2022_indicadores_barrio_localidad.csv').copy()
c['cod_dist'] = c.cod_dep.astype(int).map('{:02d}'.format) + c.cod_dis.astype(int).map('{:02d}'.format)
c['bl'] = c.cod_bar_lo.astype(int).map('{:03d}'.format)
viv = {'viv4': 'pct_electricidad', 'viv5': 'pct_agua_corriente', 'viv25': 'pct_piso_tierra', 'viv61': 'pct_cocina_lena',
       'viv60': 'pct_sin_bienes', 'viv48': 'pct_internet', 'viv57': 'pct_vehiculo', 'viv53': 'pct_motocicleta', 'viv10': 'pct_rancho'}
c = pd.concat([c[['cod_dist', 'bl', 'cod_dep', 'departamen', 'distrito_2', 'barrio', 'pob1', 'viv2']],
               pd.DataFrame({n: 100 * c[v] / c['viv2'].where(c['viv2'] > 0) for v, n in viv.items()})], axis=1)

g = gpd.read_file(GDB, layer='pry_admin3')[['adm3_pcode', 'adm3_name', 'geometry']]
g['cod_dist'] = g.adm3_pcode.str[2:6]; g['area_cod'] = g.adm3_pcode.str[6]; g['bl'] = g.adm3_pcode.str[7:10]
loc = g.merge(c, on=['cod_dist', 'bl'], how='inner')
loc['cod_dpto'] = loc.cod_dist.str[:2]
loc['area'] = loc.area_cod.map({'1': 'urbana', '3': 'otra', '6': 'rural'})
loc = loc.to_crs(CRS_M)
loc['area_km2'] = loc.geometry.area / 1e6
pts = loc.copy(); pts['geometry'] = loc.geometry.representative_point()

# ---------------- 2. Caminos de todo tiempo ----------------
r = gpd.read_file(ROADS, columns=['highway', 'surface', 'combined_surface_osm_priority'])
r = r[~r.highway.isin(['footway', 'path', 'steps', 'cycleway', 'pedestrian', 'bridleway', 'corridor', 'elevator', 'platform'])]
ripio = r.surface.isin(['gravel', 'fine_gravel', 'compacted', 'pebblestone'])
pav = r.combined_surface_osm_priority.eq('paved')
troncal_sin_dato = r.highway.isin(['motorway', 'trunk', 'primary', 'trunk_link', 'primary_link']) & r.combined_surface_osm_priority.isna()
r['todo_tiempo'] = pav | ripio
r['pavimentado'] = pav
r['todo_tiempo_amplio'] = pav | ripio | troncal_sin_dato
r = r.to_crs(CRS_M)

def dist_km(points, lines):
    j = gpd.sjoin_nearest(points[['geometry']], lines[['geometry']], how='left', distance_col='d')
    return (j.groupby(level=0).d.min() / 1000).reindex(points.index)

loc['dist_todo_tiempo_km'] = dist_km(pts, r[r.todo_tiempo])
loc['dist_pavimentado_km'] = dist_km(pts, r[r.pavimentado])
loc['dist_todo_tiempo_amplio_km'] = dist_km(pts, r[r.todo_tiempo_amplio])
# distancia a la capital del distrito (lejanía)
cap = gpd.read_file(GDB, layer='pry_admincapitals').to_crs(CRS_M)
cap['cod_dist'] = cap.adm2_pcode.str[2:6]
capd = cap.drop_duplicates('cod_dist').set_index('cod_dist').geometry
# si el distrito no tiene capital en la capa, se usa la capital más cercana
near = gpd.sjoin_nearest(pts[['geometry']], cap[['geometry']], distance_col='d').groupby(level=0).d.min() / 1000
loc['dist_capital_distrito_km'] = [p.distance(capd[d]) / 1000 if d in capd.index else near[i]
                                   for i, p, d in zip(pts.index, pts.geometry, loc.cod_dist)]

# ---------------- 3. Lluvia y luz previa por localidad ----------------
L = R + '/07_clima_y_contexto/lluvia_CHIRPS_raster/'
p4326 = pts.to_crs(4326)
xy = list(zip(p4326.geometry.x, p4326.geometry.y))
rain = []
for y in range(2013, 2023):
    with rasterio.open(f'{L}chirps_anual_{y}.tif') as s: rain.append([v[0] for v in s.sample(xy)])
loc['lluvia_media_2013_2022'] = np.nanmean(np.array(rain, dtype=float), axis=0)
with rasterio.open(R + '/07_clima_y_contexto/luces_nocturnas_VIIRS/viirs_vnl_v2_paraguay_2013.tif') as s:
    poly = loc.to_crs(s.crs)
    lz = []
    for geom in poly.geometry:
        a, _ = mask(s, [geom], crop=True, all_touched=True, filled=False)
        v = a[0].compressed().astype(float); v = v[v >= 0]
        lz.append(v.mean() if v.size else np.nan)
loc['luz_media_2013'] = lz

loc['tramo_distancia'] = pd.cut(loc.dist_todo_tiempo_km, [-0.001, 2, 5, 10, np.inf], labels=['0-2 km', '2-5 km', '5-10 km', '> 10 km'])
base = pd.DataFrame(loc.drop(columns='geometry'))
cols = ['adm3_pcode', 'cod_dpto', 'departamen', 'cod_dist', 'distrito_2', 'bl', 'barrio', 'area', 'pob1', 'viv2', 'area_km2'] + list(viv.values()) + \
       ['dist_todo_tiempo_km', 'tramo_distancia', 'dist_pavimentado_km', 'dist_todo_tiempo_amplio_km', 'dist_capital_distrito_km',
        'lluvia_media_2013_2022', 'luz_media_2013']
base = base[cols].rename(columns={'departamen': 'departamento', 'distrito_2': 'distrito', 'barrio': 'localidad', 'pob1': 'poblacion', 'viv2': 'viviendas_ocupadas'})
base.to_csv(OUT + '/base_localidades_2022.csv', index=False, encoding='utf-8-sig')

# ---------------- 4. Estimaciones (localidades rurales, Región Oriental sin Asunción ni Central) ----------------
s = base[(base.area == 'rural') & base.cod_dpto.isin(ORIENTAL) & (base.viviendas_ocupadas >= 10)].dropna(
    subset=['dist_todo_tiempo_km', 'pct_piso_tierra', 'luz_media_2013', 'dist_capital_distrito_km']).copy()
s['foco'] = s.cod_dpto.isin(FOCO).astype(int)
# índice de privaciones: promedio de 5 indicadores estandarizados (más alto = peor)
z = lambda x: (x - x.mean()) / x.std()
s['indice_privaciones'] = pd.concat([z(s.pct_piso_tierra), z(s.pct_cocina_lena), z(s.pct_sin_bienes),
                                     z(100 - s.pct_electricidad), z(100 - s.pct_agua_corriente)], axis=1).mean(axis=1)
s['log_dist'] = np.log1p(s.dist_todo_tiempo_km)
s['log_dist_cap'] = np.log1p(s.dist_capital_distrito_km)
s['log_pob'] = np.log(s.poblacion.clip(lower=1)); s['log_area'] = np.log(s.area_km2)
s['log_luz13'] = np.log1p(s.luz_media_2013)
s['lluvia100'] = (s.lluvia_media_2013_2022 - s.lluvia_media_2013_2022.mean()) / 100
s['tramo_distancia'] = pd.Categorical(s.tramo_distancia, categories=['0-2 km', '2-5 km', '5-10 km', '> 10 km'])
CTRL = 'log_pob + log_area + log_dist_cap + log_luz13'

def fit(f, d):
    return smf.wls(f, data=d, weights=d.viviendas_ocupadas).fit(cov_type='cluster', cov_kwds={'groups': d.cod_dist})

OUTS = {'indice_privaciones': 'Índice de privaciones (desvíos estándar)', 'pct_piso_tierra': '% viviendas con piso de tierra',
        'pct_cocina_lena': '% viviendas que cocinan con leña', 'pct_sin_bienes': '% viviendas sin ningún bien',
        'pct_electricidad': '% viviendas con electricidad', 'pct_agua_corriente': '% viviendas con agua corriente',
        'pct_internet': '% viviendas con internet', 'pct_vehiculo': '% viviendas con vehículo'}
rows = []
for y, lab in OUTS.items():
    d = s.dropna(subset=[y])
    mA = fit(f'{y} ~ log_dist + {CTRL} + C(cod_dist)', d)  # efectos fijos de distrito
    mB = fit(f'{y} ~ C(tramo_distancia) + {CTRL} + C(cod_dist)', d)
    mC = fit(f'{y} ~ log_dist + lluvia100 + log_dist:lluvia100 + {CTRL} + C(cod_dpto)', d)  # lluvia: efectos fijos de departamento
    mD = fit(f'{y} ~ log_dist + log_dist:foco + {CTRL} + C(cod_dist)', d)
    for m, name, vs in [(mA, 'A: log(1+distancia) · EF distrito', ['log_dist']),
                        (mB, 'B: tramos de distancia (ref. 0-2 km) · EF distrito', [v for v in mB.params.index if v.startswith('C(tramo')]),
                        (mC, 'C: + lluvia e interacción · EF departamento', ['log_dist', 'lluvia100', 'log_dist:lluvia100']),
                        (mD, 'D: heterogeneidad foco · EF distrito', ['log_dist', 'log_dist:foco'])]:
        for v in vs:
            rows.append(dict(resultado=lab, modelo=name, variable=v.replace('C(tramo_distancia)[T.', 'distancia ').replace(']', ''),
                             coef=m.params[v], ee_cluster_distrito=m.bse[v], p=m.pvalues[v], n=int(m.nobs), r2=m.rsquared))
# Robustez de la medida de caminos (índice de privaciones, EF distrito)
for var, lab in [('dist_pavimentado_km', 'solo pavimentado'), ('dist_todo_tiempo_amplio_km', 'incluye troncales sin dato')]:
    d = s.assign(ld=np.log1p(s[var]))
    m = fit(f'indice_privaciones ~ ld + {CTRL} + C(cod_dist)', d)
    rows.append(dict(resultado=OUTS['indice_privaciones'], modelo=f'Robustez: distancia a camino {lab}', variable='log_dist',
                     coef=m.params['ld'], ee_cluster_distrito=m.bse['ld'], p=m.pvalues['ld'], n=int(m.nobs), r2=m.rsquared))
res = pd.DataFrame(rows)
res.to_csv(OUT + '/resultados_localidades_2022.csv', index=False, encoding='utf-8-sig')

desc = s.groupby('tramo_distancia', observed=False).agg(localidades=('localidad', 'size'), viviendas=('viviendas_ocupadas', 'sum'),
        piso_tierra=('pct_piso_tierra', 'mean'), lena=('pct_cocina_lena', 'mean'), sin_bienes=('pct_sin_bienes', 'mean'),
        electricidad=('pct_electricidad', 'mean'), agua=('pct_agua_corriente', 'mean'), internet=('pct_internet', 'mean'),
        vehiculo=('pct_vehiculo', 'mean'), dist_capital_km=('dist_capital_distrito_km', 'median')).round(1)
desc.to_csv(OUT + '/descriptivos_por_distancia.csv', encoding='utf-8-sig')
foco = s[s.foco == 1].groupby('tramo_distancia', observed=False).agg(localidades=('localidad', 'size'), viviendas=('viviendas_ocupadas', 'sum')).reset_index()
foco.to_csv(OUT + '/localidades_foco_por_distancia.csv', index=False, encoding='utf-8-sig')
with open(OUT + '/_resumen_corrida.txt', 'w', encoding='utf-8') as f:
    f.write(f'localidades unidas censo-polígono={len(base)}; rurales={int((base.area=="rural").sum())}; muestra={len(s)} '
            f'(foco={int(s.foco.sum())}; distritos={s.cod_dist.nunique()})\n')
    f.write(f'tramos viales usados: todo_tiempo={int(r.todo_tiempo.sum())} ({r[r.todo_tiempo].length.sum()/1000:.0f} km); '
            f'pavimentado={int(r.pavimentado.sum())}; amplio={int(r.todo_tiempo_amplio.sum())}\n')
    f.write('distancia rural (km): ' + s.dist_todo_tiempo_km.describe().round(2).to_string().replace('\n', '; ') + '\n')
pd.set_option('display.width', 250)
print(open(OUT + '/_resumen_corrida.txt', encoding='utf-8').read())
print(desc.to_string()); print(foco.to_string())
print(res.round(3).to_string(index=False))
