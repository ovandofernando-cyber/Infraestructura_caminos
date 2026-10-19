"""Recorta los extractos de Overture Maps a Paraguay, les asigna distrito INE 2022 y resume por distrito.

Uso: python3 -I overture_distrito.py <dir_extractos> <distritos_geojson> <dir_09_salida> <dir_11_salida>
Los extractos (overture_{places,infra,segment}_py.parquet) salen de overture_recorte_bbox.py.
Asignación por punto representativo de cada elemento (un tramo que cruza un límite queda entero en un distrito).
"""
import os, sys
import numpy as np, pandas as pd, geopandas as gpd, pyarrow.parquet as pq, shapely

src, dist_path, out09, out11 = sys.argv[1:5]
os.makedirs(out09, exist_ok=True); os.makedirs(out11, exist_ok=True)
REL = '2026-09-23.1'

d = gpd.read_file(dist_path)[['DPTO', 'CLAVE', 'DIST_DESC_', 'geometry']].to_crs(4326)
d = d.rename(columns={'DPTO': 'cod_dpto', 'CLAVE': 'cod_dist', 'DIST_DESC_': 'distrito'})
base = d.drop(columns='geometry')


def leer(nombre, cols):
    t = pq.read_table(os.path.join(src, f'overture_{nombre}_py.parquet'), columns=cols).to_pandas()
    t['geometry'] = shapely.from_wkb(t['geometry'].values)
    return gpd.GeoDataFrame(t, geometry='geometry', crs=4326)


def asignar_distrito(g):
    """Asigna distrito por punto representativo; descarta lo que cae fuera de Paraguay."""
    pts = gpd.GeoDataFrame(g[[]], geometry=g.geometry.representative_point(), crs=4326)
    j = gpd.sjoin(pts, d, predicate='within', how='inner')
    j = j[~j.index.duplicated()]
    g = g.loc[j.index].copy()
    g[['cod_dpto', 'cod_dist', 'distrito']] = j[['cod_dpto', 'cod_dist', 'distrito']]
    g['lon'] = j.geometry.x.round(6); g['lat'] = j.geometry.y.round(6)
    return g


def fuentes(lst):
    if lst is None or len(lst) == 0:
        return ''
    return '|'.join(sorted({s['dataset'] for s in lst if s.get('dataset')}))


def conteo(g, col, cats, prefijo):
    g = g[g[col].isin(cats)]
    t = g.pivot_table(index='cod_dist', columns=col, values='id', aggfunc='count', fill_value=0)
    t = t.reindex(columns=list(cats), fill_value=0).rename(columns={c: f'{prefijo}{cats[c]}' for c in cats})
    return t


# --- Lugares (POI) ---
p = leer('places', ['id', 'geometry', 'confidence', 'names', 'basic_category', 'taxonomy', 'operating_status', 'sources'])
p = asignar_distrito(p)
p['nombre'] = p['names'].map(lambda n: n.get('primary') if isinstance(n, dict) else None)
p['taxonomia'] = p['taxonomy'].map(lambda t: '>'.join(t['hierarchy']) if isinstance(t, dict) and t.get('hierarchy') is not None else None)
p['fuentes'] = p['sources'].map(fuentes)
p['confianza'] = p['confidence'].round(3)
cols_p = ['id', 'nombre', 'basic_category', 'taxonomia', 'confianza', 'operating_status', 'fuentes', 'lon', 'lat', 'cod_dpto', 'cod_dist', 'distrito']
p[cols_p].to_csv(os.path.join(out09, 'overture_places_PRY.csv'), index=False)
print('places PRY', len(p))
print(p['basic_category'].value_counts().head(80).to_string())

# --- Infraestructura (base/infrastructure) ---
inf = leer('infra', ['id', 'geometry', 'names', 'subtype', 'class', 'surface', 'sources'])
inf = asignar_distrito(inf)
inf['nombre'] = inf['names'].map(lambda n: n.get('primary') if isinstance(n, dict) else None)
inf['fuentes'] = inf['sources'].map(fuentes)
inf['tipo_geom'] = inf.geometry.geom_type
inf['largo_km'] = np.where(inf.tipo_geom.str.contains('Line'), inf.to_crs(32721).length / 1000, np.nan).round(3)
cols_i = ['id', 'nombre', 'subtype', 'class', 'surface', 'tipo_geom', 'largo_km', 'fuentes', 'lon', 'lat', 'cod_dpto', 'cod_dist', 'distrito']
inf[cols_i].to_csv(os.path.join(out09, 'overture_infraestructura_PRY.csv'), index=False)
inf[cols_i + ['geometry']].to_file(os.path.join(out09, 'overture_infraestructura_PRY.gpkg'), driver='GPKG', layer='infraestructura')
print('infra PRY', len(inf))

# --- Resumen por distrito: servicios (places) + infraestructura ---
grupos_p = {
    'educ_inicial_basica_media': ['preschool', 'elementary_school', 'middle_school', 'high_school'],
    'educ_otros': ['place_of_learning', 'education', 'educational_service', 'educational_facility', 'specialty_school'],
    'educ_universidad': ['college_university'],
    'salud_hospital_urgencias': ['hospital', 'emergency_or_urgent_care_facility'],
    'salud_atencion_ambulatoria': ['health_care', 'outpatient_care_facility', 'primary_care_or_general_clinic', 'medical_service',
                                   'pediatric_clinic', 'specialized_health_care', 'specialized_medical_facility',
                                   'reproductive_perinatal_and_womens_care'],
    'farmacia': ['pharmacy_and_drug_store'],
    'banco_cooperativa_financiera': ['bank_or_credit_union', 'financial_service', 'atm'],
    'gobierno': ['government_office', 'government_department', 'community_and_government'],
    'policia': ['police_station'],
    'servicio_social_comunitario': ['social_or_community_service', 'community_center'],
    'mercado_feria': ['farmers_market', 'market'],
    'agro_finca_servicio': ['farm', 'agricultural_service'],
    'estacion_servicio': ['gas_station'],
    'templo': ['christian_place_of_worship', 'religious_organization'],
}
p['grupo'] = p['basic_category'].map({c: g for g, cs in grupos_p.items() for c in cs})
cat_p = {g: g for g in grupos_p}
cat_i = {'silo': 'silo', 'bridge': 'puente', 'communication_tower': 'torre_comunicacion', 'mobile_phone_tower': 'antena_celular',
         'substation': 'subestacion_electrica', 'water_tower': 'tanque_agua', 'storage_tank': 'tanque_almacenamiento',
         'bus_stop': 'parada_omnibus', 'bus_station': 'terminal_omnibus_infra', 'dam': 'represa', 'airport': 'aerodromo'}
r = base.set_index('cod_dist')
r = r.join(p.groupby('cod_dist').size().rename('ov_lugares_total'))
r = r.join(conteo(p, 'grupo', cat_p, 'ov_'))
r = r.join(conteo(inf, 'class', cat_i, 'ov_'))
r = r.join(inf[inf['class'].isin(['power_line', 'minor_line'])].groupby('cod_dist')['largo_km'].sum().rename('ov_lineas_electricas_km').round(2))
r = r.fillna(0).reset_index()
cols_num = [c for c in r.columns if c.startswith('ov_')]
r[cols_num] = r[cols_num].round(2)
r = r[['cod_dpto', 'cod_dist', 'distrito'] + cols_num]
r.to_csv(os.path.join(out09, 'overture_servicios_infraestructura_por_distrito.csv'), index=False)
print(r[cols_num].sum().to_string())

# --- Red vial (transportation/segment) ---
s = leer('segment', ['id', 'geometry', 'names', 'subtype', 'class', 'subclass', 'road_surface', 'sources'])
s = s[s['subtype'] == 'road'].copy()
s = asignar_distrito(s)
s['nombre'] = s['names'].map(lambda n: n.get('primary') if isinstance(n, dict) else None)


def superficie(rs):
    if rs is None or len(rs) == 0:
        return None
    return rs[0].get('value')


s['superficie'] = s['road_surface'].map(superficie)
pav = {'paved', 'asphalt', 'concrete', 'paving_stones', 'cobblestone', 'sett'}
nopav = {'unpaved', 'gravel', 'dirt', 'ground', 'sand', 'compacted', 'grass', 'fine_gravel', 'earth', 'mud'}
s['superficie_grupo'] = np.select([s['superficie'].isin(pav), s['superficie'].isin(nopav)], ['pavimentado', 'no_pavimentado'], 'sin_dato')
s['largo_km'] = (s.to_crs(32721).length / 1000).round(4)
s['fuentes'] = s['sources'].map(fuentes)
print('segmentos PRY', len(s), 'km', round(s['largo_km'].sum()))
print(s['superficie'].value_counts(dropna=False).head(25).to_string())
cols_s = ['id', 'nombre', 'class', 'subclass', 'superficie', 'superficie_grupo', 'largo_km', 'fuentes', 'cod_dpto', 'cod_dist']
s[cols_s + ['geometry']].to_file(os.path.join(out11, 'overture_red_vial_PRY.gpkg'), driver='GPKG', layer='segmentos')

# km por distrito según jerarquía y superficie
grupo = {'motorway': 'troncal', 'trunk': 'troncal', 'primary': 'primaria', 'secondary': 'secundaria', 'tertiary': 'terciaria',
         'unclassified': 'vecinal', 'track': 'huella_rural', 'residential': 'urbana_residencial', 'living_street': 'urbana_residencial',
         'service': 'servicio', 'unknown': 'sin_clasificar'}
s['jerarquia'] = s['class'].map(grupo).fillna('peatonal_otros')
k = s.pivot_table(index='cod_dist', columns=['jerarquia', 'superficie_grupo'], values='largo_km', aggfunc='sum', fill_value=0)
k.columns = [f'km_{a}_{b}' for a, b in k.columns]
tot = s.pivot_table(index='cod_dist', columns='superficie_grupo', values='largo_km', aggfunc='sum', fill_value=0)
tot.columns = [f'km_total_{c}' for c in tot.columns]
area = d.set_index('cod_dist').to_crs(32721).area / 1e6
v = base.set_index('cod_dist').join(area.rename('area_km2').round(2)).join(tot).join(k).fillna(0)
v['km_total'] = v[[c for c in v.columns if c.startswith('km_total_')]].sum(axis=1)
v['densidad_vial_km_km2'] = (v['km_total'] / v['area_km2']).round(4)
rur = [c for c in v.columns if c.startswith(('km_vecinal_', 'km_huella_rural_', 'km_terciaria_'))]
v['km_rural_vecinal'] = v[rur].sum(axis=1)
nopav_rur = [c for c in rur if c.endswith('_no_pavimentado')]
sd_rur = [c for c in rur if c.endswith('_sin_dato')]
con_dato = (v['km_rural_vecinal'] - v[sd_rur].sum(axis=1)).replace(0, np.nan)
# % no pavimentado sobre los km con superficie informada; el % sin dato indica cuán confiable es
v['pct_rural_vecinal_no_pavimentado'] = (100 * v[nopav_rur].sum(axis=1) / con_dato).round(1)
v['pct_rural_vecinal_sin_dato_superficie'] = (100 * v[sd_rur].sum(axis=1) / v['km_rural_vecinal'].replace(0, np.nan)).round(1)
num = [c for c in v.columns if c.startswith('km_')]
v[num] = v[num].round(3)
v.reset_index()[['cod_dpto', 'cod_dist', 'distrito', 'area_km2', 'km_total', 'densidad_vial_km_km2', 'km_rural_vecinal',
                 'pct_rural_vecinal_no_pavimentado', 'pct_rural_vecinal_sin_dato_superficie'] + sorted(c for c in num if c not in ('km_total', 'km_rural_vecinal'))].to_csv(
    os.path.join(out11, 'overture_km_red_vial_por_distrito.csv'), index=False)
print(v[['km_total', 'km_rural_vecinal']].sum().to_string())
