# Paso 2 de la evaluación a escala de tramo: escuelas y puestos de salud rurales cerca de los tramos ubicados.
# Para cada local educativo y puesto de salud (geoportal del INE) calcula la distancia al tramo vecinal del MOPC más cercano
# y el año de la primera obra a menos de 5 km. Es la base para comparar, antes y después de la obra, escuelas cercanas con
# escuelas lejanas del mismo distrito (falta la matrícula anual del MEC por establecimiento).
import numpy as np, pandas as pd, geopandas as gpd

R = '/home/user/infraestructura_caminos'
OUT = R + '/18_tramos_georreferenciados'
CRS_M = 32721
MUESTRA = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '12', '13', '14']   # Región Oriental sin Asunción ni Central

t = gpd.read_file(OUT + '/tramos_obras_vecinales_MOPC_2012_2025.gpkg').to_crs(CRS_M)
t = t[t.geometry.notna() & t.precision.isin(['tramo (línea entre extremos)', 'un solo punto'])]
lin = t[t.precision == 'tramo (línea entre extremos)']


def cercania(capa, nombre):
    d = pd.read_csv(f'{R}/09_servicios_complementarios/INE_geoportal_capas/{capa}.csv', dtype={'cod_dist': str, 'dpto': str})
    d = d[d.dpto.isin(MUESTRA) & d.area_censal.isin([3, 6])].copy()          # áreas rural (6) y suburbana (3)
    g = gpd.GeoDataFrame(d, geometry=gpd.points_from_xy(d.lon, d.lat), crs=4326).to_crs(CRS_M)
    for nom, capa_t in [('tramo_linea', lin), ('tramo_o_punto', t)]:
        j = gpd.sjoin_nearest(g[['geometry']], capa_t[['geometry', 'anio']], how='left', distance_col='dist_m')
        j = j.sort_values('dist_m').groupby(level=0).first()
        g[f'dist_km_{nom}'] = (j.dist_m / 1000).reindex(g.index)
    # año de la primera obra (tramo o punto) a menos de 5 km
    b = g[['geometry']].copy(); b['geometry'] = b.buffer(5000)
    jj = gpd.sjoin(b, t[['geometry', 'anio']], how='left', predicate='intersects')
    g['primer_anio_obra_5km'] = jj.groupby(level=0).anio.min().reindex(g.index)
    g['tipo'] = nombre
    return g


esc = cercania('locales_educativos_INE', 'local educativo')
sal = cercania('puestos_salud_publicos_INE', 'puesto de salud')
cols = ['tipo', 'id', 'cod_dist', 'distdesc', 'dptodesc', 'barlocdesc', 'nombref', 'desc_class', 'descref', 'inst nro', 'area_censal', 'lon', 'lat',
        'dist_km_tramo_linea', 'dist_km_tramo_o_punto', 'primer_anio_obra_5km']
pd.concat([esc, sal])[[c for c in cols if c in esc.columns or c in sal.columns]].to_csv(OUT + '/escuelas_y_puestos_rurales_distancia_a_tramos.csv', index=False, encoding='utf-8-sig')


def resumen(g):
    return pd.Series({'total': len(g), 'a menos de 2 km de un tramo': int((g.dist_km_tramo_linea <= 2).sum()),
                      'a menos de 5 km de un tramo': int((g.dist_km_tramo_linea <= 5).sum()),
                      'a menos de 5 km de un tramo o punto': int((g.dist_km_tramo_o_punto <= 5).sum()),
                      'con primera obra cercana 2013-2020': int(g.primer_anio_obra_5km.between(2013, 2020).sum()),
                      'distritos con escuelas cerca y lejos (5 km)': int(g.assign(c=g.dist_km_tramo_o_punto <= 5).groupby('cod_dist').c.agg(lambda x: x.any() and not x.all()).sum())})


r = pd.DataFrame({'locales educativos rurales': resumen(esc), 'puestos de salud rurales': resumen(sal)})
r.to_csv(OUT + '/resumen_escuelas_puestos_cerca_de_tramos.csv', encoding='utf-8-sig')
print(r)
print(esc.primer_anio_obra_5km.value_counts().sort_index())
