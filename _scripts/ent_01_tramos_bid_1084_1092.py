# Tramos de caminos vecinales rehabilitados con los programas BID PR-L1084 y PR-L1092 (planilla del MOPC compartida por el
# equipo): limpieza, trazado aproximado (línea recta entre extremos de cada parte, UTM 21S) y entorno de cada tramo
# (escuelas, puestos de salud y población a menos de 5 km).
import numpy as np, pandas as pd, geopandas as gpd, rasterio, rasterio.mask
from shapely.geometry import LineString

R = '/home/user/infraestructura_caminos'
D = R + '/11_infraestructura_vial_complementaria/BID_tramos_intervenidos_1084_1092'
TC = 7566  # Gs por USD, promedio 2025 (tipo de cambio de referencia del BCP)
x = pd.read_excel(D + '/Tramos_intervenidos_Caminos_Vecinales_BID_1084_1092_v2.xlsx', header=1)
x.columns = ['orden', 'id_llamado', 'licitacion', 'operacion', 'tramo', 'km', 'costo_gs', 'contratista', 'tipo_intervencion',
             'departamento', 'distritos', 'lat_txt', 'lon_txt', 'xi', 'yi', 'xf', 'yf', 'fecha_habilitacion', 'fecha_recepcion_definitiva', 'comentarios']
x['orden'] = x.orden.ffill().astype(int)                    # las filas sin orden son la segunda parte del tramo anterior
partes = x.groupby('orden').apply(lambda g: [LineString([(r.xi, r.yi), (r.xf, r.yf)]) for r in g.itertuples()])
t = x.dropna(subset=['tramo']).copy()
t['departamento'] = t.departamento.str.strip().str.title().replace({'Itapua': 'Itapúa'})
for c in ['licitacion', 'tramo', 'contratista', 'distritos', 'tipo_intervencion']:
    t[c] = t[c].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
t['costo_usd_2025'] = t.costo_gs / TC
t['usd_por_km_2025'] = t.costo_usd_2025 / t.km
t['anios_desde_recepcion'] = ((pd.Timestamp('2026-11-13') - pd.to_datetime(t.fecha_recepcion_definitiva)).dt.days / 365.25).round(1)
from shapely.geometry import MultiLineString
g = gpd.GeoDataFrame(t.drop(columns=['xi', 'yi', 'xf', 'yf', 'lat_txt', 'lon_txt']),
                     geometry=[MultiLineString(partes[o]) for o in t.orden], crs=32721)
g['km_linea_recta'] = (g.length / 1000).round(1)

# Entorno: escuelas y puestos de salud (geoportal INE) y población (WorldPop 2020) a menos de 2 y 5 km
def puntos(capa):
    d = pd.read_csv(f'{R}/09_servicios_complementarios/INE_geoportal_capas/{capa}.csv', dtype={'cod_dist': str, 'dpto': str})
    return gpd.GeoDataFrame(d, geometry=gpd.points_from_xy(d.lon, d.lat), crs=4326).to_crs(32721)
esc, sal = puntos('locales_educativos_INE'), puntos('puestos_salud_publicos_INE')
wp = rasterio.open(R + '/07_clima_y_contexto/poblacion_WorldPop/pry_ppp_2020_UNadj_constrained.tif')

def poblacion(geom):
    shp = gpd.GeoSeries([geom], crs=32721).to_crs(wp.crs)
    arr, _ = rasterio.mask.mask(wp, shp, crop=True, nodata=0)
    return float(arr[arr > 0].sum())

for km in [2, 5]:
    buf = g.buffer(km * 1000)
    g[f'escuelas_{km}km'] = [int(esc.within(b).sum()) for b in buf]
    g[f'puestos_salud_{km}km'] = [int(sal.within(b).sum()) for b in buf]
    g[f'poblacion_{km}km'] = [round(poblacion(b)) for b in buf]
# Totales sin doble conteo (unión de las franjas de todos los tramos)
tot = {}
for km in [2, 5]:
    u = g.buffer(km * 1000).union_all()
    tot[f'escuelas_{km}km'] = int(esc.within(u).sum()); tot[f'puestos_salud_{km}km'] = int(sal.within(u).sum())
    tot[f'poblacion_{km}km'] = round(poblacion(u))
cols = ['orden', 'operacion', 'id_llamado', 'licitacion', 'tramo', 'departamento', 'distritos', 'km', 'km_linea_recta', 'costo_gs',
        'costo_usd_2025', 'usd_por_km_2025', 'contratista', 'tipo_intervencion', 'fecha_habilitacion', 'fecha_recepcion_definitiva',
        'anios_desde_recepcion', 'escuelas_2km', 'escuelas_5km', 'puestos_salud_2km', 'puestos_salud_5km', 'poblacion_2km', 'poblacion_5km', 'comentarios']
g[cols].to_csv(D + '/tramos_intervenidos_BID_1084_1092.csv', index=False, encoding='utf-8-sig')
g[cols + ['geometry']].to_file(D + '/tramos_intervenidos_BID_1084_1092.gpkg', driver='GPKG')
pd.Series(tot).to_csv(D + '/entorno_total_sin_doble_conteo.csv', header=['valor'], encoding='utf-8-sig')
print(g[['orden', 'tramo', 'departamento', 'km', 'km_linea_recta', 'usd_por_km_2025', 'fecha_recepcion_definitiva', 'escuelas_5km', 'puestos_salud_5km', 'poblacion_5km']].round(0).to_string())
print('Total km', g.km.sum(), '| costo Gs', g.costo_gs.sum() / 1e9, 'mil millones | USD 2025', round(g.costo_usd_2025.sum() / 1e6, 1), 'M')
print('USD por km (promedio ponderado):', round(g.costo_usd_2025.sum() / g.km.sum()))
print(g.groupby('departamento')[['km', 'costo_gs']].sum())
print('Sin doble conteo:', tot)
