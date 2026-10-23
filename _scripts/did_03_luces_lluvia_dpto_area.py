# Paso 3 del análisis departamental: luz nocturna (VIIRS) y lluvia (CHIRPS) por departamento × área (urbana/rural), 2013-2024.
# Áreas: polígonos de localidad/barrio de COD-AB (adm3); código de área 1 = urbana, 6 = rural, 3 = suburbana (se suma a rural,
# porque la EPHC solo distingue cabecera urbana del resto).
# Uso: python3 -I did_03_luces_lluvia_dpto_area.py <carpeta con chirps_daily_PRY_AAAA.nc>
import sys, numpy as np, pandas as pd, geopandas as gpd, rasterio, xarray as xr
from rasterio.mask import mask
from rasterio.io import MemoryFile
from rasterio.transform import from_origin

R = '/home/user/infraestructura_caminos'
OUT = R + '/15_analisis_departamental_did'
DAILY = sys.argv[1]
YEARS = range(2013, 2025)

g = gpd.read_file(R + '/05_cartografia_y_codigos/COD-AB_OCHA_limites_admin/pry_admin_boundaries.gdb.zip', layer='pry_admin3')[['adm3_pcode', 'geometry']]
g['cod_dpto'] = g.adm3_pcode.str[2:4]
g['rural'] = (g.adm3_pcode.str[6] != '1').astype(int)
g['geometry'] = g.geometry.buffer(0)
z = g.dissolve(by=['cod_dpto', 'rural']).reset_index()[['cod_dpto', 'rural', 'geometry']]
z['area_km2'] = z.to_crs(32721).geometry.area / 1e6


def stats(src, geoms, positivos=True, todos=False):
    res = []
    for geom in geoms:
        a, _ = mask(src, [geom], crop=True, all_touched=todos, filled=False)
        v = a[0].compressed().astype(float)
        v = v[np.isfinite(v)]
        if positivos: v = v[v >= 0]
        res.append((v.sum(), v.mean() if v.size else np.nan))
    return res


rows = []
for y in YEARS:
    with rasterio.open(f'{R}/07_clima_y_contexto/luces_nocturnas_VIIRS/viirs_vnl_v2_paraguay_{y}.tif') as s:
        luz = stats(s, z.to_crs(s.crs).geometry)
    with rasterio.open(f'{R}/07_clima_y_contexto/lluvia_CHIRPS_raster/chirps_anual_{y}.tif') as s:
        llu = stats(s, z.to_crs(s.crs).geometry, todos=True)  # celdas de 5 km: se toman todas las que tocan el área
    ds = xr.open_dataset(f'{DAILY}/chirps_daily_PRY_{y}.nc', decode_times=False)
    arr = ds['prcp'].values.astype('float32'); arr[arr < 0] = np.nan
    lat, lon = ds['Y'].values, ds['X'].values; ds.close()
    d50 = np.nansum(arr >= 50, axis=0).astype('float32')
    d50[np.all(np.isnan(arr), axis=0)] = np.nan
    if lat[0] < lat[-1]: d50 = d50[::-1]
    rx, ry = float(abs(lon[1] - lon[0])), float(abs(lat[1] - lat[0]))
    prof = dict(driver='GTiff', height=len(lat), width=len(lon), count=1, dtype='float32', crs='EPSG:4326',
                transform=from_origin(lon.min() - rx / 2, lat.max() + ry / 2, rx, ry), nodata=np.nan)
    with MemoryFile() as mf:
        with mf.open(**prof) as m: m.write(d50, 1)
        with mf.open() as m: dias = stats(m, z.to_crs(4326).geometry, todos=True)
    for k, r in z.iterrows():
        rows.append(dict(cod_dpto=r.cod_dpto, rural=r.rural, anio=y, area_km2=r.area_km2,
                         luz_suma=luz[k][0], luz_media=luz[k][1], lluvia_mm=llu[k][1], dias_lluvia_50mm=dias[k][1]))
    print(y, flush=True)
p = pd.DataFrame(rows)
p['luz_por_km2'] = p.luz_suma / p.area_km2
p['log_luz_km2'] = np.log(1 + p.luz_por_km2 * 100)  # luz por 100 km², en logaritmo
p.to_csv(OUT + '/_tmp_luces_lluvia_dpto_area.csv', index=False)
print(p.groupby(['anio', 'rural']).luz_suma.sum().unstack().round(0))
print(p.groupby('anio')[['lluvia_mm', 'dias_lluvia_50mm']].mean().round(1))
