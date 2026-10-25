# Paso 1 del análisis de efecto local de los tramos (ver 19_efecto_local_tramos/PLAN_DE_ANALISIS.md):
# arma las zonas de tratados (tramos 2015-2021) y controles (localidades rurales a más de 10 km de cualquier tramo) y
# calcula la luz nocturna anual (VIIRS 2012-2024) en cada zona, con franjas de 3 km y de 1,5 km.
import numpy as np, pandas as pd, geopandas as gpd, rasterio
from rasterio.mask import mask

R = '/home/user/infraestructura_caminos'
OUT = R + '/19_efecto_local_tramos'
CRS_M = 32721
GDB = R + '/05_cartografia_y_codigos/COD-AB_OCHA_limites_admin/pry_admin_boundaries.gdb.zip'
MUESTRA = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '12', '13', '14']

# ---------------- Tratados ----------------
t = gpd.read_file(R + '/18_tramos_georreferenciados/tramos_obras_vecinales_MOPC_2012_2025.gpkg').to_crs(CRS_M)
t = t[t.geometry.notna() & t.precision.isin(['tramo (línea entre extremos)', 'un solo punto'])].copy()
todos = t.copy()                                   # todos los tramos ubicados (para excluir controles cercanos)
t['dpto'] = t.cod_dist_tramo.astype(str).str[:2]
t = t[t.dpto.isin(MUESTRA)]
t['wkt'] = t.geometry.to_wkt()
t = t.sort_values('anio').drop_duplicates('wkt')   # mismo trazado en varios lotes: primer año
tr = t[t.anio.between(2015, 2021)].copy()
tr = gpd.GeoDataFrame({'unidad': ['T' + str(i) for i in range(len(tr))], 'grupo': 'tratado', 'cohorte': tr.anio.values,
                       'dpto': tr.dpto.values, 'tipo_geom': np.where(tr.geom_type == 'LineString', 'linea', 'punto'),
                       'ocid': tr.ocid.values, 'lote': tr.lote.values}, geometry=tr.geometry.values, crs=CRS_M)

# ---------------- Controles ----------------
g3 = gpd.read_file(GDB, layer='pry_admin3')[['adm3_pcode', 'geometry']].to_crs(CRS_M)
g3 = g3[g3.adm3_pcode.str[6] == '6'].copy()                      # localidades rurales
g3['dpto'] = g3.adm3_pcode.str[2:4]
g3 = g3[g3.dpto.isin(tr.dpto.unique())]
g3['geometry'] = g3.geometry.representative_point()
d = gpd.sjoin_nearest(g3, todos[['geometry']], how='left', distance_col='dist_m').groupby(level=0).dist_m.min()
g3['dist_km_tramo'] = (d / 1000).reindex(g3.index)
ctl = g3[g3.dist_km_tramo > 10].sample(n=min(400, int((g3.dist_km_tramo > 10).sum())), random_state=2025)
ctl = gpd.GeoDataFrame({'unidad': 'C' + ctl.adm3_pcode, 'grupo': 'control', 'cohorte': np.nan, 'dpto': ctl.dpto,
                        'tipo_geom': 'punto', 'dist_km_tramo': ctl.dist_km_tramo, 'ocid': '', 'lote': ''}, geometry=ctl.geometry, crs=CRS_M)
u = pd.concat([tr, ctl], ignore_index=True)
u.to_crs(4326).to_file(OUT + '/unidades_tratados_y_controles.gpkg', driver='GPKG')

# ---------------- Luz nocturna por zona ----------------
filas = []
for y in range(2012, 2025):
    with rasterio.open(f'{R}/07_clima_y_contexto/luces_nocturnas_VIIRS/viirs_vnl_v2_paraguay_{y}.tif') as s:
        for km in (3, 1.5):
            z = u.copy(); z['geometry'] = u.buffer(km * 1000)
            area = z.area / 1e6
            zz = z.to_crs(s.crs)
            for i, geom in enumerate(zz.geometry):
                a, _ = mask(s, [geom], crop=True, filled=False)
                v = a[0].compressed().astype(float); v = v[v >= 0]
                filas.append(dict(unidad=u.unidad.iloc[i], anio=y, franja_km=km, luz_suma=v.sum(), area_km2=area.iloc[i]))
    print(y, flush=True)
L = pd.DataFrame(filas)
L['log_luz_km2'] = np.log1p(L.luz_suma / L.area_km2 * 100)
L.to_csv(OUT + '/luces_por_unidad_anio.csv', index=False, encoding='utf-8-sig')
print(u.groupby(['grupo', 'tipo_geom']).size())
print(tr.cohorte.value_counts().sort_index())

# ---------------- Exploratorio: luz solo en la parte rural de cada zona (sin áreas urbanas) ----------------
# Las zonas de los tramos incluyen cabeceras urbanas, donde la luz medida puede bajar por el cambio a alumbrado LED.
urb = gpd.read_file(GDB, layer='pry_admin3')[['adm3_pcode', 'geometry']].to_crs(CRS_M)
urb = urb[urb.adm3_pcode.str[6] == '1'].buffer(0).union_all()
filas = []
for y in range(2012, 2025):
    with rasterio.open(f'{R}/07_clima_y_contexto/luces_nocturnas_VIIRS/viirs_vnl_v2_paraguay_{y}.tif') as s:
        z = u.copy(); z['geometry'] = u.buffer(3000).difference(urb)
        area = z.area / 1e6
        zz = z.to_crs(s.crs)
        for i, geom in enumerate(zz.geometry):
            if geom.is_empty or area.iloc[i] < 1:
                filas.append(dict(unidad=u.unidad.iloc[i], anio=y, franja_km=3, luz_suma=np.nan, area_km2=area.iloc[i])); continue
            a, _ = mask(s, [geom], crop=True, filled=False)
            v = a[0].compressed().astype(float); v = v[v >= 0]
            filas.append(dict(unidad=u.unidad.iloc[i], anio=y, franja_km=3, luz_suma=v.sum(), area_km2=area.iloc[i]))
Lr = pd.DataFrame(filas); Lr['log_luz_km2'] = np.log1p(Lr.luz_suma / Lr.area_km2 * 100)
Lr.to_csv(OUT + '/luces_por_unidad_anio_solo_rural.csv', index=False, encoding='utf-8-sig')
print('luz solo rural: listo')
