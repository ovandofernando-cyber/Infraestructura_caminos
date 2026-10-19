"""Recorta GRIP4 región 2 a Paraguay y resume km de caminos por distrito INE 2022, tipo y superficie.

Uso: python3 -I _scripts/infra_grip_distrito.py <GRIP4_region2.gdb> <distritos_geojson> <dir_salida>
Salidas: GRIP4_PRY.gpkg (tramos de Paraguay, GP_RCY=600) y GRIP4_km_por_distrito.csv
Los tramos se cortan en los límites distritales; las longitudes se miden en EPSG:32721.
"""
import os, sys
import geopandas as gpd

gdb, dist_path, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
TIPO = {1: 'autopista', 2: 'primaria', 3: 'secundaria', 4: 'terciaria', 5: 'local', 0: 'sin_dato'}
SUP = {1: 'pavimentado', 2: 'ripio', 3: 'tierra', 0: 'sin_dato'}

g = gpd.read_file(gdb, where='GP_RCY=600')
g.to_file(os.path.join(out, 'GRIP4_PRY.gpkg'), driver='GPKG')
d = gpd.read_file(dist_path)[['DPTO', 'CLAVE', 'DIST_DESC_', 'geometry']].to_crs(4326)
d = d.rename(columns={'DPTO': 'cod_dpto', 'CLAVE': 'cod_dist', 'DIST_DESC_': 'distrito'})

x = gpd.overlay(g[['GP_RTP', 'GP_RSE', 'GP_RAV', 'geometry']], d, how='intersection', keep_geom_type=True)
x['km'] = x.to_crs(32721).length / 1000
x['tipo'] = x['GP_RTP'].map(TIPO).fillna('sin_dato')
x['sup'] = x['GP_RSE'].map(SUP).fillna('sin_dato')
t = x.pivot_table(index='cod_dist', columns='tipo', values='km', aggfunc='sum', fill_value=0).add_prefix('km_')
s = x.pivot_table(index='cod_dist', columns='sup', values='km', aggfunc='sum', fill_value=0).add_prefix('km_')
r = d.drop(columns='geometry').set_index('cod_dist').join(t).join(s).fillna(0)
r['km_total'] = x.groupby('cod_dist')['km'].sum().reindex(r.index).fillna(0)
r['km_estacional'] = x[x['GP_RAV'] == 1].groupby('cod_dist')['km'].sum().reindex(r.index).fillna(0)
r['area_km2'] = d.set_index('cod_dist').to_crs(32721).area.reindex(r.index) / 1e6
r['densidad_km_por_100km2'] = 100 * r['km_total'] / r['area_km2']
r.round(2).reset_index().to_csv(os.path.join(out, 'GRIP4_km_por_distrito.csv'), index=False)
print(len(g), 'tramos;', round(x['km'].sum()), 'km asignados;', len(r), 'distritos')
