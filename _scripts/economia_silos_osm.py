"""Extrae silos y acopios de granos de OpenStreetMap (extracto PBF de Paraguay) y los cuenta por distrito INE 2022.

Uso: python3 -I _scripts/economia_silos_osm.py <paraguay-latest.osm.pbf> <distritos_geojson> <dir_salida>
Criterio: man_made=silo, building=silo/grain_silo, industrial=grain*/silo, o nombre con "silo" o "acopio".
Las vías (polígonos) se reducen al promedio de sus nodos. Un complejo de varios silos cuenta varias veces.
Salidas: silos_acopios_OSM_PRY.csv (un punto por elemento) y silos_acopios_OSM_por_distrito.csv
"""
import os, re, sys
import osmium, pandas as pd, geopandas as gpd

pbf, dist_path, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
NOMBRE = re.compile(r'\bsilos?\b|\bacopio', re.I)


def es_silo(t):
    return (t.get('man_made') == 'silo' or t.get('building') in ('silo', 'grain_silo')
            or re.match(r'grain|silo', t.get('industrial', '')) or NOMBRE.search(t.get('name', '')))


class H(osmium.SimpleHandler):
    def __init__(self):
        super().__init__(); self.filas = []

    def guardar(self, tipo, o, lon, lat):
        t = {k.k: k.v for k in o.tags}
        self.filas.append({'osm_tipo': tipo, 'osm_id': o.id, 'nombre': t.get('name', ''), 'man_made': t.get('man_made', ''),
                           'building': t.get('building', ''), 'industrial': t.get('industrial', ''),
                           'operador': t.get('operator', ''), 'lon': round(lon, 6), 'lat': round(lat, 6)})

    def node(self, n):
        if es_silo(n.tags):
            self.guardar('node', n, n.location.lon, n.location.lat)

    def way(self, w):
        if es_silo(w.tags):
            pts = [(nd.lon, nd.lat) for nd in w.nodes if nd.location.valid()]
            if pts:
                self.guardar('way', w, sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


h = H(); h.apply_file(pbf, locations=True)
s = pd.DataFrame(h.filas)
g = gpd.GeoDataFrame(s, geometry=gpd.points_from_xy(s.lon, s.lat), crs=4326)
d = gpd.read_file(dist_path)[['DPTO', 'CLAVE', 'DIST_DESC_', 'geometry']].to_crs(4326)
d = d.rename(columns={'DPTO': 'cod_dpto', 'CLAVE': 'cod_dist', 'DIST_DESC_': 'distrito'})
j = gpd.sjoin(g, d, predicate='within', how='left').drop(columns=['geometry', 'index_right'])
j.to_csv(os.path.join(out, 'silos_acopios_OSM_PRY.csv'), index=False)
c = j.groupby('cod_dist').size().rename('n_silos_acopios_osm')
r = d.drop(columns='geometry').set_index('cod_dist').join(c).fillna({'n_silos_acopios_osm': 0})
r['n_silos_acopios_osm'] = r['n_silos_acopios_osm'].astype(int)
r.reset_index().to_csv(os.path.join(out, 'silos_acopios_OSM_por_distrito.csv'), index=False)
print(len(j), 'elementos;', j['cod_dist'].notna().sum(), 'dentro de Paraguay;', (r['n_silos_acopios_osm'] > 0).sum(), 'distritos con al menos uno')
