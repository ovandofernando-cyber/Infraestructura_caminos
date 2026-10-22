# Análisis por localidad (Censo 2022), versión con más detalle:
#  1) calidad del camino por tipo de superficie (asfalto, empedrado/adoquín, tierra o ripio) a partir de las etiquetas OSM
#     de la capa HeiGIT: distancia a cada tipo y composición de la red en 3 km alrededor de la localidad;
#  2) lluvia como exposición a días intransitables: días por año con lluvia >= 50 mm (y >= 30 mm), CHIRPS diario 2013-2022.
# Uso: python3 -I analisis_localidad_2022_calidad_lluvia.py <roads.gpkg HeiGIT descomprimido> <carpeta con chirps_daily_PRY_AAAA.nc>
import os, sys, numpy as np, pandas as pd, geopandas as gpd, rasterio, xarray as xr, statsmodels.formula.api as smf
from rasterio.transform import from_origin

R = '/home/user/infraestructura_caminos'
OUT = R + '/14_analisis_localidad_2022'
RAIN_OUT = R + '/07_clima_y_contexto/lluvia_CHIRPS_diaria_dias_intensos'
os.makedirs(RAIN_OUT, exist_ok=True)
ROADS, DAILY = sys.argv[1], sys.argv[2]
CRS_M = 32721
ORIENTAL = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '12', '13', '14']
FOCO = ['01', '02', '05', '06', '14']
BUF_M = 3000

b = pd.read_csv(OUT + '/base_localidades_2022.csv', dtype={'cod_dist': str, 'cod_dpto': str, 'bl': str})
b = b[[c for c in b.columns if not c.startswith(('dist_asfalto', 'dist_empedrado', 'km_', 'pct_red_', 'dias_lluvia'))]]
g = gpd.read_file(R + '/05_cartografia_y_codigos/COD-AB_OCHA_limites_admin/pry_admin_boundaries.gdb.zip', layer='pry_admin3')[['adm3_pcode', 'geometry']]
g = g[g.adm3_pcode.isin(b.adm3_pcode)].to_crs(CRS_M).set_index('adm3_pcode')
pts = gpd.GeoDataFrame(geometry=g.geometry.representative_point(), crs=CRS_M)

# ---------------- 1. Tipos de superficie ----------------
r = gpd.read_file(ROADS, columns=['highway', 'surface', 'combined_surface_DL_priority'])
r = r[~r.highway.isin(['footway', 'path', 'steps', 'cycleway', 'pedestrian', 'bridleway', 'corridor', 'elevator', 'platform'])].copy()
sf = r.surface.fillna('').str.lower()
EMP = sf.str.contains('cobble|sett|paving_stones|empedrado|bricks')
ASF = sf.str.contains('asphalt|concrete') | sf.isin(['paved']) | ((sf == '') & r.combined_surface_DL_priority.eq('paved'))
RIP = sf.isin(['gravel', 'compacted', 'fine_gravel', 'pebblestone'])
TIE = sf.str.contains('dirt|ground|earth|eath|rth|sand|arena|mud|clay|grass') | sf.isin(['unpaved']) | ((sf == '') & r.combined_surface_DL_priority.eq('unpaved'))
r['tipo'] = np.select([EMP, ASF, RIP, TIE], ['empedrado_adoquin', 'asfalto', 'ripio', 'tierra_no_pav'], 'sin_dato')
r = r.to_crs(CRS_M)
r['km'] = r.length / 1000
resumen_red = r.groupby('tipo').km.sum().round(0)

def dist_km(lines):
    j = gpd.sjoin_nearest(pts, lines[['geometry']], how='left', distance_col='d')
    return (j.groupby(level=0).d.min() / 1000).reindex(pts.index)

m = pd.DataFrame(index=pts.index)
m['dist_asfalto_km'] = dist_km(r[r.tipo == 'asfalto'])
m['dist_empedrado_km'] = dist_km(r[r.tipo == 'empedrado_adoquin'])
m['dist_ripio_km'] = dist_km(r[r.tipo == 'ripio'])
# composición de la red en un radio de 3 km
rural = pts.index.str[6] == '6'  # código de área 6 = rural (solo estas entran al análisis)
buf = gpd.GeoDataFrame(geometry=pts[rural].buffer(BUF_M), crs=CRS_M)
inter = gpd.overlay(r[['tipo', 'geometry']], buf.reset_index().rename(columns={'adm3_pcode': 'loc'}), how='intersection', keep_geom_type=True)
inter['km'] = inter.length / 1000
comp = inter.pivot_table(index='loc', columns='tipo', values='km', aggfunc='sum', fill_value=0)
for t in ['asfalto', 'empedrado_adoquin', 'ripio', 'tierra_no_pav', 'sin_dato']:
    m['km_' + t + '_3km'] = comp.get(t, pd.Series(dtype=float)).reindex(m.index).fillna(0).round(3)
tipados = m[['km_asfalto_3km', 'km_empedrado_adoquin_3km', 'km_ripio_3km', 'km_tierra_no_pav_3km']].sum(axis=1)
m['pct_red_tierra_3km'] = (100 * m.km_tierra_no_pav_3km / tipados).where(tipados > 0)
m['pct_red_empedrado_3km'] = (100 * m.km_empedrado_adoquin_3km / tipados).where(tipados > 0)
m['pct_red_asfalto_3km'] = (100 * m.km_asfalto_3km / tipados).where(tipados > 0)
m['pct_red_sin_dato_3km'] = (100 * m.km_sin_dato_3km / (tipados + m.km_sin_dato_3km)).where(tipados + m.km_sin_dato_3km > 0)

# ---------------- 2. Días de lluvia intensa (CHIRPS diario) ----------------
counts = {}
for y in range(2013, 2023):
    ds = xr.open_dataset(f'{DAILY}/chirps_daily_PRY_{y}.nc', decode_times=False)
    pr = ds['prcp']
    a = pr.values.astype('float32')  # (T, Y, X)
    a[a < 0] = np.nan
    for th in (30, 50):
        counts.setdefault(th, []).append(np.nansum(a >= th, axis=0))
    lat, lon = ds['Y'].values, ds['X'].values
    ds.close()
flip = lat[0] < lat[-1]
res_x, res_y = float(abs(lon[1] - lon[0])), float(abs(lat[1] - lat[0]))
transform = from_origin(lon.min() - res_x / 2, lat.max() + res_y / 2, res_x, res_y)
prof = dict(driver='GTiff', height=len(lat), width=len(lon), count=1, dtype='float32', crs='EPSG:4326', transform=transform, compress='deflate', nodata=np.nan)
for th, lst in counts.items():
    for y, arr in zip(range(2013, 2023), lst):
        arr = arr[::-1] if flip else arr
        with rasterio.open(f'{RAIN_OUT}/dias_lluvia_mayor_{th}mm_{y}.tif', 'w', **prof) as d: d.write(arr.astype('float32'), 1)
    mean = np.mean(np.stack(lst), axis=0); mean = mean[::-1] if flip else mean
    with rasterio.open(f'{RAIN_OUT}/dias_lluvia_mayor_{th}mm_promedio_2013_2022.tif', 'w', **prof) as d: d.write(mean.astype('float32'), 1)
p4326 = pts.to_crs(4326); xy = list(zip(p4326.geometry.x, p4326.geometry.y))
for th in (30, 50):
    with rasterio.open(f'{RAIN_OUT}/dias_lluvia_mayor_{th}mm_promedio_2013_2022.tif') as s:
        m[f'dias_lluvia_{th}mm_anual'] = [v[0] for v in s.sample(xy)]
    with rasterio.open(f'{RAIN_OUT}/dias_lluvia_mayor_{th}mm_2022.tif') as s:
        m[f'dias_lluvia_{th}mm_2022'] = [v[0] for v in s.sample(xy)]
# tabla por distrito (días >= 50 mm, promedio 2013-2022)
gd = gpd.read_file(R + '/05_cartografia_y_codigos/COD-AB_OCHA_limites_admin/pry_admin_boundaries.gdb.zip', layer='pry_admin2')[['adm2_pcode', 'geometry']]
from rasterio.mask import mask as rmask
rows = []
with rasterio.open(f'{RAIN_OUT}/dias_lluvia_mayor_50mm_promedio_2013_2022.tif') as s:
    for pc, geom in zip(gd.adm2_pcode, gd.to_crs(4326).geometry):
        a, _ = rmask(s, [geom], crop=True, all_touched=True, filled=True, nodata=np.nan)
        rows.append(dict(cod_dist=pc[2:], dias_lluvia_50mm_anual=round(float(np.nanmean(a)), 2)))
pd.DataFrame(rows).to_csv(RAIN_OUT + '/dias_lluvia_50mm_por_distrito_2013_2022.csv', index=False, encoding='utf-8-sig')

# ---------------- 3. Base actualizada ----------------
base = b.merge(m.round(3).reset_index(), on='adm3_pcode', how='left')
base.to_csv(OUT + '/base_localidades_2022.csv', index=False, encoding='utf-8-sig')

# ---------------- 4. Estimaciones ----------------
s = base[(base.area == 'rural') & base.cod_dpto.isin(ORIENTAL) & (base.viviendas_ocupadas >= 10)].dropna(
    subset=['dist_todo_tiempo_km', 'pct_piso_tierra', 'luz_media_2013', 'dist_capital_distrito_km']).copy()
s['foco'] = s.cod_dpto.isin(FOCO).astype(int)
z = lambda x: (x - x.mean()) / x.std()
s['indice_privaciones'] = pd.concat([z(s.pct_piso_tierra), z(s.pct_cocina_lena), z(s.pct_sin_bienes),
                                     z(100 - s.pct_electricidad), z(100 - s.pct_agua_corriente)], axis=1).mean(axis=1)
for c in ['dist_todo_tiempo_km', 'dist_asfalto_km', 'dist_empedrado_km', 'dist_capital_distrito_km']:
    s['l_' + c.replace('_km', '')] = np.log1p(s[c])
s['log_pob'] = np.log(s.poblacion.clip(lower=1)); s['log_area'] = np.log(s.area_km2); s['log_luz13'] = np.log1p(s.luz_media_2013)
s['tierra10_3km'] = s.pct_red_tierra_3km / 10
s['sindato10_3km'] = s.pct_red_sin_dato_3km.fillna(100) / 10
s['red_km_3km'] = s[[c for c in s.columns if c.startswith('km_') and c.endswith('_3km')]].sum(axis=1)
s['log_red_3km'] = np.log1p(s.red_km_3km)
s['d50'] = s.dias_lluvia_50mm_anual - s.dias_lluvia_50mm_anual.mean()
s['d30'] = s.dias_lluvia_30mm_anual - s.dias_lluvia_30mm_anual.mean()
s['lluvia100'] = (s.lluvia_media_2013_2022 - s.lluvia_media_2013_2022.mean()) / 100
CTRL = 'log_pob + log_area + l_dist_capital_distrito + log_luz13'
fit = lambda f, dd: smf.wls(f, data=dd, weights=dd.viviendas_ocupadas).fit(cov_type='cluster', cov_kwds={'groups': dd.cod_dist})
OUTS = {'indice_privaciones': 'Índice de privaciones (desvíos estándar)', 'pct_piso_tierra': '% viviendas con piso de tierra',
        'pct_cocina_lena': '% viviendas que cocinan con leña', 'pct_electricidad': '% viviendas con electricidad',
        'pct_agua_corriente': '% viviendas con agua corriente', 'pct_vehiculo': '% viviendas con vehículo'}
rows = []
def add(mm, modelo, resultado, vs):
    for v in vs:
        rows.append(dict(resultado=resultado, modelo=modelo, variable=v, coef=mm.params[v], ee_cluster_distrito=mm.bse[v], p=mm.pvalues[v], n=int(mm.nobs), r2=mm.rsquared))
for y, lab in OUTS.items():
    # Calidad: ¿asfalto o empedrado?
    add(fit(f'{y} ~ l_dist_asfalto + l_dist_empedrado + {CTRL} + C(cod_dist)', s), 'Q1: distancia a asfalto y a empedrado · EF distrito', lab, ['l_dist_asfalto', 'l_dist_empedrado'])
    # Calidad: composición de la red local (3 km)
    q = s.dropna(subset=['tierra10_3km'])
    add(fit(f'{y} ~ tierra10_3km + sindato10_3km + log_red_3km + l_dist_todo_tiempo + {CTRL} + C(cod_dist)', q), 'Q2: % de red de tierra en 3 km · EF distrito', lab, ['tierra10_3km', 'l_dist_todo_tiempo'])
    # Lluvia como días intransitables
    add(fit(f'{y} ~ l_dist_todo_tiempo * d50 + {CTRL} + C(cod_dpto)', s), 'L1: días >= 50 mm × distancia · EF departamento', lab, ['l_dist_todo_tiempo', 'd50', 'l_dist_todo_tiempo:d50'])
    add(fit(f'{y} ~ l_dist_todo_tiempo * d50 + {CTRL} + C(cod_dist)', s), 'L2: días >= 50 mm × distancia · EF distrito', lab, ['l_dist_todo_tiempo', 'l_dist_todo_tiempo:d50'])
    add(fit(f'{y} ~ tierra10_3km * d50 + sindato10_3km + log_red_3km + {CTRL} + C(cod_dpto)', q), 'L3: días >= 50 mm × % red de tierra 3 km · EF departamento', lab, ['tierra10_3km', 'd50', 'tierra10_3km:d50'])
    add(fit(f'{y} ~ l_dist_todo_tiempo * d30 + {CTRL} + C(cod_dpto)', s), 'L4 (robustez): días >= 30 mm × distancia · EF departamento', lab, ['l_dist_todo_tiempo', 'l_dist_todo_tiempo:d30'])
    add(fit(f'{y} ~ l_dist_todo_tiempo * lluvia100 + {CTRL} + C(cod_dpto)', s), 'L5 (comparación): lluvia total anual × distancia · EF departamento', lab, ['l_dist_todo_tiempo', 'l_dist_todo_tiempo:lluvia100'])
res = pd.DataFrame(rows)
res.to_csv(OUT + '/resultados_calidad_y_lluvia_diaria.csv', index=False, encoding='utf-8-sig')
desc = s[['dist_todo_tiempo_km', 'dist_asfalto_km', 'dist_empedrado_km', 'dist_ripio_km', 'pct_red_tierra_3km', 'pct_red_empedrado_3km',
          'pct_red_asfalto_3km', 'pct_red_sin_dato_3km', 'dias_lluvia_50mm_anual', 'dias_lluvia_30mm_anual', 'dias_lluvia_50mm_2022']].describe(percentiles=[.1, .25, .5, .75, .9]).T.round(2)
desc.to_csv(OUT + '/descriptivos_calidad_y_lluvia_diaria.csv', encoding='utf-8-sig')
with open(OUT + '/_resumen_corrida_calidad_lluvia.txt', 'w', encoding='utf-8') as f:
    f.write('km de red por tipo (sin peatonales): ' + resumen_red.to_string().replace('\n', '; ') + '\n')
    f.write(f'muestra={len(s)}; con red tipada en 3 km={int(s.tierra10_3km.notna().sum())}\n')
    f.write('corr(días>=50mm, lluvia total)=%.2f\n' % s[['dias_lluvia_50mm_anual', 'lluvia_media_2013_2022']].corr().iloc[0, 1])
pd.set_option('display.width', 250)
print(open(OUT + '/_resumen_corrida_calidad_lluvia.txt', encoding='utf-8').read())
print(desc.to_string())
print(res.round(3).to_string(index=False))
