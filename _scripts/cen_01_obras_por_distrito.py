# Paso 1 del análisis censal (NBI 2012 frente a 2022): obras del MOPC en caminos vecinales 2012-2025 ubicadas por distrito.
# Entrada: 08_contrataciones_DNCP/DNCP_MOPC_adjudicaciones_2012_2025.csv (did_00 con años 2012 2025).
# Ubica cada obra en distritos (códigos INE 2022) buscando, dentro de los departamentos ya asignados, nombres de distrito
# y de localidades del Censo 2022 en el texto del lote y, si el lote no dice nada, en el título del llamado.
import os, sys, re, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from obras_mopc_reglas import R, norm, preparar, clasificar, ubicar_departamentos, NOMBRES_DPTO

OUT = R + '/16_analisis_censal_nbi_2012_2022'
os.makedirs(OUT, exist_ok=True)

a = pd.read_csv(R + '/08_contrataciones_DNCP/DNCP_MOPC_adjudicaciones_2012_2025.csv', dtype=str)
a = ubicar_departamentos(clasificar(preparar(a)))
v = a[a.camino_vecinal].copy()

# ---------------- Diccionario de nombres: distritos y localidades (Censo 2022) ----------------
c = pd.read_csv(R + '/12_INE_complementario/Censo_2022_indicadores_localidad/censo2022_indicadores_barrio_localidad.csv')
c['cod_dist'] = c.cod_dep.astype(int).map('{:02d}'.format) + c.cod_dis.astype(int).map('{:02d}'.format)
limpiar = lambda s: re.sub(r'\b(compania|cia|barrio|colonia|asentamiento|sub ?urbano|urbano|area \d)\b', '', re.sub(r'\(.*?\)', '', norm(s))).strip(' -.')
nom = pd.concat([pd.DataFrame({'n': c.distrito_2.map(norm).str.strip(), 'cod_dist': c.cod_dist, 'tipo': 'distrito'}).drop_duplicates(),
                 pd.DataFrame({'n': c.barrio.map(limpiar), 'cod_dist': c.cod_dist, 'tipo': 'localidad'})])
nom = nom[(nom.n.str.len() >= 6) | ((nom.tipo == 'distrito') & (nom.n.str.len() >= 4))].drop_duplicates(['n', 'cod_dist'])
# nombres que no sirven para ubicar: nombres de departamento, palabras comunes en los llamados y nombres que también son
# rutas (Carlos Antonio López = ruta IX). Un nombre de localidad que aparece en más de 15 llamados distintos se toma como genérico.
textos = a.txt.drop_duplicates().tolist()
frec = {n: sum(bool(re.search(r'\b' + re.escape(n) + r'\b', t)) for t in textos) for n in nom.n.unique()}
GEN = set(NOMBRES_DPTO) | {'carlos antonio lopez', 'nacional', 'oriental', 'central', 'centro', 'parque', 'parana', 'ruta', 'tramo'}
GEN |= {n for n, k in frec.items() if k > 15 and not (nom[(nom.n == n)].tipo == 'distrito').any()}
nom = nom[~nom.n.isin(GEN)]


def buscar(t, dptos):
    """Distritos cuyo nombre (o el de una de sus localidades) aparece en t. Si un nombre está contenido en otro más largo
    que también aparece (santa rosa / santa rosa del aguaray), se queda el más largo."""
    sub = nom[nom.cod_dist.str[:2].isin(dptos)] if dptos else nom[nom.tipo == 'distrito']
    hits = []
    for n, d, tipo in zip(sub.n, sub.cod_dist, sub.tipo):
        for m in re.finditer(r'\b' + re.escape(n) + r'\b', t):
            hits.append((m.start(), m.end(), d, tipo, n))
    hits = [h for h in hits if not any(o[0] <= h[0] and h[1] <= o[1] and (o[1] - o[0]) > (h[1] - h[0]) for o in hits)]
    return sorted({h[2] for h in hits}), sorted({h[4] for h in hits})


def ubicar_distrito(r):
    dptos = [d for d in r.deptos if d != 'CH']
    for parte, txt in (('lote', r.txt_l), ('título', r.txt_t)):
        ds, ns = buscar(txt, dptos)
        if ds: return ds, f'nombre en el {parte}', '; '.join(ns)
    return [], ('solo departamento' if dptos else 'sin ubicación'), ''


u = v.apply(ubicar_distrito, axis=1)
v['distritos'] = u.str[0]; v['metodo_distrito'] = u.str[1]; v['nombres_encontrados'] = u.str[2]

# Revisión manual de las obras grandes (leyendo título y lote). Se aplica en orden: la primera regla que coincide gana.
# Corrige compañías con nombre repetido en varios distritos (Santa Clara, María Auxiliadora, Santa Rita) y ríos tomados
# por distritos (Tebicuary, Yguazú). Lista vacía = no se puede ubicar el distrito.
REV_DIST = [
    ('ocds-03ad3f-375603', None, ['1202', '1201', '1214'], 'Desvío Alberdi-Pilar y travesía urbana de Villa Franca (Ñeembucú)'),
    ('ocds-03ad3f-302402', None, ['1202', '1201'], 'Desvío Alberdi-Pilar: el río Tebicuary es el límite, no el distrito de Guairá'),
    ('ocds-03ad3f-366249', None, ['1201', '1205'], 'Pilar-General José Eduvigis Díaz'),
    ('ocds-03ad3f-275543', None, ['1403', '1404', '1406'], 'Ruta departamental Curuguaty-Villa Ygatimí-Ypejhú'),
    ('ocds-03ad3f-369248', 'santa clara', ['0203'], 'Santa Clara-Jhugua Rey-Choré: compañías de Choré'),
    ('ocds-03ad3f-369248', "tava'?i", ['0608', '0724'], "Tava'i (Caazapá)-María Auxiliadora (Tomás Romero Pereira, Itapúa)"),
    ('ocds-03ad3f-351364', 'la paz.*fram', ['0726', '0715', '0712', '0711'], 'La Paz-Jesús y General Artigas-Fram'),
    ('ocds-03ad3f-351364', 'la paz', ['0726', '0715'], 'La Paz-Jesús'),
    ('ocds-03ad3f-351364', 'artigas', ['0712', '0711'], 'General Artigas-Fram'),
    ('ocds-03ad3f-240702', 'yatytay', ['0727', '0721'], 'Yatytay-San Rafael del Paraná'),
    ('ocds-03ad3f-355468', None, ['0810'], 'Yabebyry-Santa Rita (compañía de Misiones, no el distrito de Alto Paraná)'),
    ('ocds-03ad3f-240877', 'santa rita - san ig', ['0803'], 'Santa Rita (compañía)-San Ignacio, Misiones'),
    ('ocds-03ad3f-240877', 'ya?y?bebyry', ['0810'], 'Yabebyry-Santa Rita, Misiones'),
    ('ocds-03ad3f-240877', 'fleitas', [], 'Fleitas Cue-río Tebicuary: no se puede ubicar el distrito'),
    ('ocds-03ad3f-369879', 'san maria - santa rosa', ['0806', '0807'], 'Santa María-Santa Rosa (Misiones)'),
    ('ocds-03ad3f-301770', 'santa maria - 4 bocas', ['0806', '0807'], 'Santa María-4 Bocas y Santa Rosa-San Juan Berchmans (Misiones)'),
    ('ocds-03ad3f-301770', 'pikysyry', ['0417'], 'Pikysyry-San Marcos y Paso Yobái-San Agustín (Guairá)'),
    ('ocds-03ad3f-338085', None, ['0516'], 'Río Yguazú-Mariscal Francisco Solano López (el río, no el distrito de Alto Paraná)'),
    ('ocds-03ad3f-246651', 'rio yguazu', ['0516'], 'Río Yguazú-Mariscal Francisco Solano López'),
    ('ocds-03ad3f-246651', 'raul a\\. oviedo', ['0514', '0522'], 'Raúl A. Oviedo-Nueva Toledo'),
    ('ocds-03ad3f-244043', 'oviedo - la pastor', ['0501', '0517'], 'Coronel Oviedo-La Pastora'),
    ('ocds-03ad3f-227980', 'chore', ['0203', '0209'], 'Choré (colonia Cocuera)-San Pablo'),
]
v['rev'] = False
for ocid, lote, dd, nota in REV_DIST:
    m = v.ocid.eq(ocid) & ~v.rev & (v.txt_l.str.contains(lote) if lote else True)
    v.loc[m, 'distritos'] = pd.Series([dd] * m.sum(), index=v.index[m], dtype=object)
    v.loc[m, 'metodo_distrito'] = 'revisión manual' if dd else 'solo departamento'
    v.loc[m, 'nombres_encontrados'] = nota; v.loc[m, 'rev'] = True
v['n_distritos'] = v.distritos.str.len()

cols = ['ocid', 'adjudicacion_id', 'fecha_adjudicacion', 'anio', 'monto', 'metodo_ubicacion', 'metodo_distrito', 'nombres_encontrados',
        'titulo_llamado', 'lotes_adjudicados']
v.assign(cod_dpto_asignados=v.deptos.map(';'.join), cod_dist_asignados=v.distritos.map(';'.join))[
    cols[:5] + ['cod_dpto_asignados', 'cod_dist_asignados'] + cols[5:]].rename(columns={'monto': 'monto_adjudicado_gs'}) \
    .sort_values(['anio', 'monto_adjudicado_gs'], ascending=[True, False]) \
    .to_csv(OUT + '/obras_vecinales_MOPC_2012_2025_por_distrito.csv', index=False, encoding='utf-8-sig')

# ---------------- Tabla por distrito ----------------
e = v[v.n_distritos > 0].explode('distritos').rename(columns={'distritos': 'cod_dist'})
e['monto_asignado'] = e.monto / e.n_distritos
def resumen(sub, suf):
    return sub.groupby('cod_dist').agg(**{f'n_obras_{suf}': ('ocid', 'nunique'), f'gs_{suf}': ('monto_asignado', 'sum'),
                                          f'primer_anio_{suf}': ('anio', 'min')})
td = pd.concat([resumen(e[e.anio.between(2012, 2020)], '2012_2020'), resumen(e[e.anio.between(2021, 2025)], '2021_2025')], axis=1)
# departamentos con obras que solo se pudieron ubicar a nivel de departamento en 2012-2020 (posible contaminación del control)
solo = v[(v.metodo_distrito == 'solo departamento') & v.anio.between(2012, 2020)].explode('deptos')
td.reset_index().to_csv(OUT + '/obras_vecinales_por_distrito.csv', index=False, encoding='utf-8-sig')
solo.groupby('deptos').monto.sum().rename('gs_solo_departamento_2012_2020').reset_index() \
    .rename(columns={'deptos': 'cod_dpto'}).to_csv(OUT + '/obras_vecinales_solo_departamento_2012_2020.csv', index=False, encoding='utf-8-sig')

r = v[v.anio.between(2012, 2020)].groupby('metodo_distrito').agg(adjudicaciones=('monto', 'size'), monto_gs=('monto', 'sum'))
r['pct_monto'] = (100 * r.monto_gs / r.monto_gs.sum()).round(1)
r.to_csv(OUT + '/resumen_ubicacion_por_distrito_2012_2020.csv', encoding='utf-8-sig')
print('obras vecinales 2012-2025:', len(v), '| 2012-2020:', int(v.anio.between(2012, 2020).sum()))
print(r)
print('distritos con obra 2012-2020:', int(td['n_obras_2012_2020'].notna().sum()), '| solo 2021-2025:',
      int((td['n_obras_2012_2020'].isna() & td['n_obras_2021_2025'].notna()).sum()))
print('nombres genéricos excluidos (por frecuencia):', sorted(n for n in GEN if frec.get(n, 0) > 15))
