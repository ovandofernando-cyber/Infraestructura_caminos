# Paso 1 de la evaluación a escala de tramo: ubica en el mapa los tramos de las obras vecinales del MOPC (2012-2025).
# Para cada lote se extraen los nombres de los extremos ("Tramo: Nueva Toledo - Vaquería"), se buscan entre las
# localidades del Censo 2022 (polígonos COD-AB) y los distritos dentro de los departamentos asignados a la obra, y se une
# cada par de extremos consecutivos con una línea recta (aproximación del trazado). Si el lote informa la longitud, se
# compara con la longitud en línea recta para validar.
# Entrada: 16_analisis_censal_nbi_2012_2022/obras_vecinales_MOPC_2012_2025_por_distrito.csv
import os, sys, re, itertools, numpy as np, pandas as pd, geopandas as gpd
from shapely.geometry import LineString, Point
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from obras_mopc_reglas import R, norm, NOMBRES_DPTO

OUT = R + '/18_tramos_georreferenciados'
os.makedirs(OUT, exist_ok=True)
GDB = R + '/05_cartografia_y_codigos/COD-AB_OCHA_limites_admin/pry_admin_boundaries.gdb.zip'
CRS_M = 32721

# ---------------- Diccionario de lugares con coordenadas ----------------
c = pd.read_csv(R + '/12_INE_complementario/Censo_2022_indicadores_localidad/censo2022_indicadores_barrio_localidad.csv')
c['cod_dist'] = c.cod_dep.astype(int).map('{:02d}'.format) + c.cod_dis.astype(int).map('{:02d}'.format)
c['bl'] = c.cod_bar_lo.astype(int).map('{:03d}'.format)
g3 = gpd.read_file(GDB, layer='pry_admin3')[['adm3_pcode', 'geometry']].to_crs(CRS_M)
g3['cod_dist'] = g3.adm3_pcode.str[2:6]; g3['bl'] = g3.adm3_pcode.str[7:10]
g3['geometry'] = g3.geometry.representative_point()
loc = g3.merge(c[['cod_dist', 'bl', 'barrio']], on=['cod_dist', 'bl'])
loc['n'] = loc.barrio.map(lambda s: re.sub(r'\b(compania|cia|barrio|b|colonia|col|asentamiento|sub ?urbano|urbano|area \d)\b\.?', '',
                                            re.sub(r'\(.*?\)', '', norm(s))).strip(' -.'))
loc['tipo'] = 'localidad'
cap = gpd.read_file(GDB, layer='pry_admincapitals').to_crs(CRS_M)
cap['cod_dist'] = cap.adm2_pcode.str[2:6]
g2 = gpd.read_file(GDB, layer='pry_admin2', ignore_geometry=True)[['adm2_pcode', 'adm2_name']]
g2['cod_dist'] = g2.adm2_pcode.str[2:6]
dist = gpd.GeoDataFrame(cap.drop_duplicates('cod_dist')[['cod_dist', 'geometry']].merge(g2[['cod_dist', 'adm2_name']], on='cod_dist'), geometry='geometry', crs=CRS_M)
dist['n'] = dist.adm2_name.map(norm).str.strip(); dist['tipo'] = 'cabecera distrital'
lug = pd.concat([loc[['n', 'cod_dist', 'tipo', 'geometry']], dist[['n', 'cod_dist', 'tipo', 'geometry']]], ignore_index=True)
lug = gpd.GeoDataFrame(lug, geometry='geometry', crs=CRS_M)
lug = lug[lug.n.str.len() >= 4]
lug['dpto'] = lug.cod_dist.str[:2]
# nombres que no sirven para ubicar: departamentos y palabras comunes de los llamados. Como los extremos se buscan solo
# en fragmentos cortos ("X - Y"), no hace falta descartar nombres frecuentes de localidades (San Cristóbal, Horqueta...).
GEN = set(NOMBRES_DPTO) | {'carlos antonio lopez', 'nacional', 'oriental', 'occidental', 'central', 'centro', 'parque', 'parana', 'ruta',
                           'tramo', 'region', 'puente', 'calle', 'departamento'}
# alias de cabeceras: "villa curuguaty" también como "curuguaty"
al = lug[(lug.tipo == 'cabecera distrital') & lug.n.str.match(r'^(villa|colonia|puerto) ')].copy()
al['n'] = al.n.str.replace(r'^(villa|colonia|puerto) ', '', regex=True)
lug = pd.concat([lug, al[al.n.str.len() >= 5]], ignore_index=True)
lug = lug[~lug.n.isin(GEN)]

# ---------------- Extremos de cada lote ----------------
RUIDO = (r'lote\s*(n[°ºo.]*)?\s*\d+\s*[:.-]?|tramo\s*:?|obra\s+[ivx\d]+\s*-?|longitud\s*:?.*$|long\.?\s*:?.*$|\d+\+\d+|\bkm\.?\s*\d*[.,]?\d*|'
         r'construccion de pavimento tipo empedrado (del|en el)?|pavimentacion( asfaltica)?( del)?|rehabilitacion( y mantenimiento)?( del)?|'
         r'mejoramiento( del)?|seccion\s+[ivx]+|traza principal|del tramo|en el tramo|progresiva.*$|\(.*?\)|\bruta\s*(n[°ºo.]*)?\s*[ivx\d]+\b|'
         r'cruce\b|empalme\b|acceso a\b|\bpy\s*\d+|\blong\.?,.*$|ad referendum.*$|\+')


def extremos(lote):
    t = norm(lote)
    t = re.sub(r'^\s*\d+\s*-\s*', '', t)          # número de lote al inicio
    t = re.sub(RUIDO, ' ', t)
    partes = [p.strip(' .,:;') for p in re.split(r'\s+-\s+|\s*[–?\t]\s*|-(?=[a-z])|\s+y\s+|,', t)]
    # un extremo es un nombre corto (hasta 5 palabras); las frases largas son descripción del llamado, no lugares
    partes = [re.sub(r'^(rio|arroyo|a[°º]|ao)\s+(?=\w)', 'RIO ', p) for p in partes]   # ríos y arroyos no son localidades
    return [p for p in partes if len(p) >= 4 and not p.startswith('RIO ') and not re.fullmatch(r'[\d\s.,]+', p)]


def longitud_declarada(lote):
    m = re.search(r'long(?:itud)?\.?\s*:?\s*(\d+[.,]?\d*)\s*km', norm(lote))
    return float(m.group(1).replace(',', '.')) if m else np.nan


def _buscar(nombre, sub):
    """Coincidencia exacta del fragmento; si es largo, prueba sus últimas y primeras palabras (hasta 4)."""
    w = nombre.replace('.', ' ').split()
    opciones = ([' '.join(w)] if len(w) <= 5 else []) + [' '.join(w[-k:]) for k in range(4, 0, -1)] + [' '.join(w[:k]) for k in range(4, 0, -1)]
    for op in opciones:
        if len(op) < 4 or op in GEN: continue
        ex = sub[sub.n == op]
        if not ex.empty: return ex
    if len(w) <= 5 and nombre not in GEN:     # el fragmento corto contiene el nombre de la localidad o al revés
        return sub[sub.n.map(lambda x: len(x) >= 6 and bool(re.search(r'\b' + re.escape(x) + r'\b', nombre))) |
                   sub.n.map(lambda x: len(nombre) >= 6 and bool(re.search(r'\b' + re.escape(nombre) + r'\b', x)))]
    return sub.iloc[0:0]


def candidatos(nombre, dptos, dists):
    ex = _buscar(nombre, lug[lug.dpto.isin(dptos)] if dptos else lug)
    fuera = False
    if ex.empty and dptos:          # el extremo puede estar en un departamento vecino
        ex = _buscar(nombre, lug); fuera = True
    if dists and ex.cod_dist.isin(dists).any():
        ex = ex[ex.cod_dist.isin(dists)]
    return ex.assign(fuera_dpto=fuera)


o = pd.read_csv(R + '/16_analisis_censal_nbi_2012_2022/obras_vecinales_MOPC_2012_2025_por_distrito.csv', dtype={'cod_dpto_asignados': str, 'cod_dist_asignados': str})
filas = []
for r in o.itertuples():
    dptos = [d for d in str(r.cod_dpto_asignados).split(';') if d not in ('nan', 'CH', '')]
    dists = [d for d in str(r.cod_dist_asignados).split(';') if d not in ('nan', '')]
    lotes = str(r.lotes_adjudicados).split(' | ') if pd.notna(r.lotes_adjudicados) else []
    if not lotes or all(re.fullmatch(r'\s*\d+\s*-\s*(lote\s*(n[°º]*)?\s*\d+|lotetotal)\s*', norm(l)) for l in lotes):
        # lote genérico: se usa el título solo si nombra un tramo concreto ("tramo X - Y")
        lotes = [str(r.titulo_llamado)] if re.search(r'tramo\s*:?\s*[a-z]', norm(r.titulo_llamado)) and not re.search(r'varios|region|departamentos', norm(r.titulo_llamado)) else []
        if not lotes:
            filas.append(dict(ocid=r.ocid, adjudicacion_id=r.adjudicacion_id, anio=r.anio, monto_adjudicado_gs=r.monto_adjudicado_gs,
                              cod_dpto_asignados=r.cod_dpto_asignados, lote=str(r.lotes_adjudicados)[:250], extremos_texto='',
                              longitud_declarada_km=np.nan, n_lotes_obra=1, extremos_ubicados='', n_puntos=0, geometry=None)); continue
    for lote in lotes:
        nombres = extremos(lote)
        cands = [(n, candidatos(n, dptos, dists)) for n in nombres]
        cands = [(n, cd) for n, cd in cands if not cd.empty]
        base = dict(ocid=r.ocid, adjudicacion_id=r.adjudicacion_id, anio=r.anio, monto_adjudicado_gs=r.monto_adjudicado_gs / len(lotes),
                    cod_dpto_asignados=r.cod_dpto_asignados, lote=lote[:250], extremos_texto='; '.join(nombres),
                    longitud_declarada_km=longitud_declarada(lote), n_lotes_obra=len(lotes))
        if not cands:
            filas.append(dict(base, extremos_ubicados='', n_puntos=0, geometry=None)); continue
        # con nombres repetidos, se elige la combinación de candidatos más compacta (menor recorrido total)
        opciones = [list(cd.head(15).itertuples()) for _, cd in cands]
        mejor, mejor_len = None, np.inf
        for comb in itertools.islice(itertools.product(*opciones), 5000):
            pts = [p.geometry for p in comb]
            L = sum(a.distance(b) for a, b in zip(pts, pts[1:]))
            if L < mejor_len: mejor, mejor_len = comb, L
        keep = [k for k, p in enumerate(mejor) if not p.fuera_dpto or
                min([p.geometry.distance(q.geometry) for q2, q in enumerate(mejor) if q2 != k] or [np.inf]) <= 80000]
        mejor = [mejor[k] for k in keep]; cands = [cands[k] for k in keep]
        if not mejor:
            filas.append(dict(base, extremos_ubicados='', n_puntos=0, geometry=None)); continue
        pts = [p.geometry for p in mejor]
        mejor_len = sum(a.distance(b) for a, b in zip(pts, pts[1:]))
        geom = LineString(pts) if len(pts) >= 2 and mejor_len > 0 else Point(pts[0])
        filas.append(dict(base, extremos_ubicados='; '.join(f'{n} ({p.cod_dist})' for (n, _), p in zip(cands, mejor)),
                          n_puntos=len(pts), cod_dist_tramo=';'.join(sorted({p.cod_dist for p in mejor})), geometry=geom))

t = gpd.GeoDataFrame(filas, geometry='geometry', crs=CRS_M)
t['revision_manual'] = ''
# Revisión manual de los tramos más grandes: lista de distritos cuyas cabeceras marcan los extremos, o None para descartar
# (no es un tramo vecinal o el texto no permite ubicarlo). Se aplica la primera regla que coincide con el ocid y el lote.
REV = [
    ('ocds-03ad3f-375603', None, ['1202', '1214', '1201'], 'Desvío Alberdi - Villa Franca - Pilar (Ñeembucú)'),
    ('ocds-03ad3f-302402', None, ['1202', '1214', '1201'], 'Desvío Alberdi - Pilar (Ñeembucú)'),
    ('ocds-03ad3f-366249', None, ['1201', '1205'], 'Pilar - General José Eduvigis Díaz'),
    ('ocds-03ad3f-275540', None, None, 'Ruta Nacional 9 (Chaco): no es camino vecinal de la Región Oriental'),
    ('ocds-03ad3f-295051', None, None, 'Tramos alimentadores urbanos de Central: varias ciudades, no un tramo'),
    ('ocds-03ad3f-228203', None, None, 'Caminos no pavimentados de todo un departamento: no es un tramo'),
    ('ocds-03ad3f-299820', 'boqueron', None, 'Boquerón - San Francisco - Buena Vista: extremos ambiguos'),
    ('ocds-03ad3f-299820', '3 de febrero', ['0518'], 'Cruce PY13 - 3 de Febrero - Colonias Unidas: solo 3 de Febrero es seguro'),
    ('ocds-03ad3f-301770', 'santa maria', ['0806', '0807'], 'Varios tramos en Santa María y Santa Rosa (Misiones): sin trazado'),
    ('ocds-03ad3f-271376', None, ['1402'], 'Cruce Guaraní - Corpus Christi: Pindo Ty Porã no se pudo confirmar'),
    ('ocds-03ad3f-316719', None, ['0307', '0318'], 'Eusebio Ayala - Mompox (Tobatí); Cerro La Gloria no confirmado'),
    ('ocds-03ad3f-228085', 'valle pe - tebicuarymi', ['0402'], 'Valle Pé - Tebicuarymi: el segundo extremo no se pudo confirmar'),
    ('ocds-03ad3f-228085', 'tuna', None, 'Tuna - Tupã Rendá - San Cristóbal: extremos ambiguos'),
    ('ocds-03ad3f-355468', None, ['0810'], 'Yabebyry - Santa Rita (compañía de Yabebyry)'),
    ('ocds-03ad3f-240877', 'yaybebyry', ['0810'], 'Yabebyry - Santa Rita (compañía de Yabebyry)'),
    ('ocds-03ad3f-240879', 'villarrica - .umi', ['0401', '0607'], 'Villarrica - Ñumi'),
    ('ocds-03ad3f-240879', '.umi - caazap', ['0607', '0601'], 'Ñumi - Caazapá'),
    ('ocds-03ad3f-246651', 'raul a', ['0514', '0522'], 'Raúl A. Oviedo - Nueva Toledo'),
    ('ocds-03ad3f-369248', "tava", ['0608', '0724'], "Tava'i - María Auxiliadora (Tomás Romero Pereira)"),
    ('ocds-03ad3f-318307', None, ['0214', '0221'], 'General Resquín - San Vicente Pancholo'),
]
capd = dist.set_index('cod_dist').geometry
# si la capa de cabeceras no tiene el distrito, se usa la localidad urbana más poblada del distrito
pob = loc.merge(c[['cod_dist', 'bl', 'pob1']], on=['cod_dist', 'bl']).sort_values('pob1', ascending=False).drop_duplicates('cod_dist').set_index('cod_dist').geometry
capd = pd.concat([capd, pob[~pob.index.isin(capd.index)]])
t['_rev'] = False
for ocid, lote, dd, nota in REV:
    m = t.ocid.eq(ocid) & ~t._rev & (t.lote.map(norm).str.contains(lote) if lote else True)
    for k in t.index[m]:
        if dd is None:
            t.at[k, 'geometry'] = None; t.at[k, 'n_puntos'] = 0
        else:
            pts = [capd[d] for d in dd]
            t.at[k, 'geometry'] = LineString(pts) if len(pts) > 1 else Point(pts[0])
            t.at[k, 'n_puntos'] = len(pts); t.at[k, 'cod_dist_tramo'] = ';'.join(dd)
        t.at[k, 'revision_manual'] = nota; t.at[k, '_rev'] = True
t = t.drop(columns='_rev')

t['longitud_recta_km'] = np.where(t.geometry.notna(), t.geometry.length / 1000, np.nan)
t.loc[t.geometry.geom_type == 'Point', 'longitud_recta_km'] = np.nan
t['razon_declarada_recta'] = t.longitud_declarada_km / t.longitud_recta_km
t['precision'] = np.select([t.geometry.geom_type.eq('LineString'), t.geometry.geom_type.eq('Point')],
                           ['tramo (línea entre extremos)', 'un solo punto'], 'sin ubicar')
# validación: si la longitud declarada es muy distinta de la recta, el tramo queda marcado como dudoso
dud = (t.revision_manual == '') & t.razon_declarada_recta.notna() & ((t.razon_declarada_recta < 0.7) | (t.razon_declarada_recta > 3))
t.loc[dud, 'precision'] = 'dudoso (longitud no coincide)'
t.to_crs(4326).to_file(OUT + '/tramos_obras_vecinales_MOPC_2012_2025.gpkg', driver='GPKG')
pd.DataFrame(t.drop(columns='geometry')).to_csv(OUT + '/tramos_obras_vecinales_MOPC_2012_2025.csv', index=False, encoding='utf-8-sig')
res = t.groupby('precision').agg(lotes=('lote', 'size'), monto_gs=('monto_adjudicado_gs', 'sum'))
res.to_csv(OUT + '/resumen_georreferenciacion.csv', encoding='utf-8-sig')
print(res.assign(monto_gs=lambda x: (x.monto_gs / 1e9).round(0)))
v = t.razon_declarada_recta.dropna()
print('lotes con longitud declarada y línea:', len(v), '| mediana declarada/recta:', round(v.median(), 2), '| entre 0,7 y 3:', round(((v >= .7) & (v <= 3)).mean(), 2))
