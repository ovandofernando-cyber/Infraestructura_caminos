# Paso 1 del análisis departamental (antes y después): obras del MOPC adjudicadas 2018-2025 (DNCP).
# Clasifica cada adjudicación (obra vial / camino vecinal), la ubica en uno o más departamentos y
# arma la intensidad de tratamiento por departamento.
# Entrada: 08_contrataciones_DNCP/DNCP_MOPC_adjudicaciones_2018_2025.csv (extraída de los zips masivos OCDS awa-masivo).
import re, unicodedata, numpy as np, pandas as pd, geopandas as gpd

R = '/home/user/infraestructura_caminos'
OUT = R + '/15_analisis_departamental_did'
GDB = R + '/05_cartografia_y_codigos/COD-AB_OCHA_limites_admin/pry_admin_boundaries.gdb.zip'
ORIENTAL = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14']
FOCO = ['01', '02', '05', '06', '14']


def norm(s):
    if pd.isna(s): return ''
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower())


a = pd.read_csv(R + '/08_contrataciones_DNCP/DNCP_MOPC_adjudicaciones_2018_2025.csv', dtype=str)
a = a[a.estado.eq('Adjudicado')].copy()
a['anio'] = a.anio_adjudicacion.astype(int)
a['monto'] = a.monto_adjudicado_gs.astype(float)
a['txt_t'] = (a.titulo_llamado.map(norm) + ' ' + a.release_id.fillna('').str.replace('-', ' ')).str.strip()
a['txt_l'] = a.lotes_adjudicados.map(norm)
a['txt'] = a.txt_t + ' || ' + a.txt_l

# ---------------- 1. Tipo de obra ----------------
VIAL = (r'camin|vecinal|paviment|asfalt|empedr|ripio|enripi|puente|tramo|\bruta|vial|alcantarillas|transitabilidad|'
        r'terraplen|baden|calzada|obras de arte|niveles de servicio|avenida|acceso')
NO_OBRA = (r'consultor|fiscaliz|estudio|diseno final|adquisici|alquiler|locacion|seguro|servicio de (?:limpieza|vigilancia|seguridad)|'
           r'capacitaci|repuesto|equipos viales|licencia|auditor|supervisi|maquinaria|combustible|peaje|pesaje|camion|'
           r'mezcla asfaltica|materiales|cemento asfaltico|emulsion|pintura|senaliz|seguridad vial|iluminaci')
NO_VIAL = (r'alcantarillado sanitario|agua potable|edificio|hospital|vivienda|iglesia|templo|campamento|laboratorio|'
           r'terminal de cargas|puerto|muelle|dragado|costanera|planta de tratamiento|escuela|oficina|centro comunitario|'
           r'plaza|parque|desagues? pluvial|drenaje pluvial|electric|canal|sistema troncal|btr|metrobus')
RURAL = (r'vecinal|rural|empedr|ripio|enripi|transitabilidad|puentes? (?:de hormigon|prefabricad|metalic|de madera)|'
         r'zonas criticas|caminos? (?:de )?(?:acceso|productiv)|no pavimentad|no mejorad')
es_obra = a.categoria.fillna('').str.startswith('Obras') | a.categoria.isna() | \
          a.txt_t.str.contains(r'construcci|rehabilit|mejoramiento|mantenimiento de caminos|pavimentaci|obras')
a['obra_vial'] = a.txt.str.contains(VIAL) & ~a.txt_t.str.contains(NO_OBRA) & ~a.txt.str.contains(NO_VIAL) & es_obra
# Rutas nacionales, corredores y obras urbanas mayores: no cuentan como red vecinal/departamental
NACIONAL = (r'ruta nacional|\bpy ?0?\d{1,2}\b|crema|c\.r\.e\.m\.a|corredor|gmans|2 ?[°º]? ?(?:do )?puente|segundo puente|'
            r'puente sobre el rio (?:parana|paraguay)|avenida|avda|circunvalaci|interseccion|acceso sur|costanera|'
            r'(?:habilitacion|rehabilitacion|mejoramiento) y mantenimiento de (?:la )?ruta|mantenimiento de carreteras|ruta n[°º]? ?\d')
# camino_vecinal = obra en caminos vecinales o departamentales (no rutas nacionales)
a['camino_vecinal'] = a.obra_vial & (a.txt.str.contains(RURAL) | ~a.txt.str.contains(NACIONAL)) & \
    ~a.txt.str.contains(r'2 ?[°º]? ?(?:do )?puente|segundo puente|puente sobre el rio (?:parana|paraguay)')

# ---------------- 2. Ubicación ----------------
DEP = {'00': r'asuncion', '01': r'concepcion', '02': r'san pedro(?! del parana)', '03': r'cordillera', '04': r'guaira',
       '05': r'caaguazu', '06': r'caazapa', '07': r'itapua', '08': r'misiones', '09': r'paraguari', '10': r'alto parana',
       '11': r'(?:departamentos?|dptos?\.?)[^|]{0,60}\bcentral\b|\bcentral\b[^|]{0,30}(?:departamento|dpto)',
       '12': r'neembucu', '13': r'amambay', '14': r'canindeyu', '15': r'presidente hayes|pdte\.? hayes',
       '16': r'boqueron', '17': r'alto paraguay'}
CHACO = r'ruta (?:n[o°º]? ?)?9\b|transchaco|py ?09|py ?12|pioneros|paratodo|loma plata|mariscal estigarribia|nanawa|bruguez|pozo colorado'


def deps(t): return [k for k, p in DEP.items() if re.search(p, t)]


g = gpd.read_file(GDB, layer='pry_admin2', ignore_geometry=True)[['adm2_pcode', 'adm2_name']]
g['d'] = g.adm2_pcode.str[2:4]; g['n'] = g.adm2_name.map(norm)
NOMBRES_DPTO = {'asuncion', 'concepcion', 'san pedro', 'cordillera', 'guaira', 'caaguazu', 'caazapa', 'itapua', 'misiones',
                'paraguari', 'alto parana', 'central', 'neembucu', 'amambay', 'canindeyu', 'presidente hayes', 'boqueron', 'alto paraguay'}
cnt = g.n.value_counts()
dist = g[(g.n.map(cnt) == 1) & (g.n.str.len() >= 6) & ~g.n.isin(NOMBRES_DPTO)]
DIST = dict(zip(dist.n, dist.d))  # nombres de distrito únicos en el país (>= 6 letras)


def dists(t): return sorted({d for n, d in DIST.items() if re.search(r'\b' + re.escape(n) + r'\b', t)})


def ubicar(r):
    dl, dt = deps(r.txt_l), deps(r.txt_t)
    xl = dists(r.txt_l)
    if dl: return dl, 'departamento en el lote'
    if len(dt) == 1: return dt, 'departamento en el título'
    if dt and xl and set(xl) & set(dt): return sorted(set(xl) & set(dt)), 'distrito del lote dentro de los departamentos del título'
    if dt: return dt, 'departamentos del título (monto repartido en partes iguales)'
    if xl: return xl, 'distrito en el lote'
    xt = dists(r.txt_t)
    if xt: return xt, 'distrito en el título'
    if re.search(CHACO, r.txt): return ['CH'], 'Chaco (rutas de la Región Occidental)'
    return [], 'sin ubicación (varios departamentos o todo el país)'


u = a.apply(ubicar, axis=1)
a['deptos'] = u.str[0]; a['metodo_ubicacion'] = u.str[1]

# Correcciones manuales de las adjudicaciones grandes revisadas una por una (ocid, texto del lote, deptos, ¿red vecinal?)
REVISION = [
    ('ocds-03ad3f-375603', None, ['12'], None, 'Desvío Alberdi-Pilar y Villa Franca están en Ñeembucú (Tebicuary es el río, no el distrito de Guairá)'),
    ('ocds-03ad3f-366301', None, ['14'], False, 'Curuguaty-Saltos del Guairá: ruta nacional en Canindeyú'),
    ('ocds-03ad3f-366300', 'ruta nacional n. 10', ['14'], False, 'Ruta nacional 10 Calle 6000-Curuguaty'),
    ('ocds-03ad3f-366300', 'ruta nacional n. 5', ['01'], False, 'Ruta nacional 5 Concepción-Yby Yaú'),
    ('ocds-03ad3f-351958', None, ['01'], False, 'Ruta V (nacional) Arroyito, Concepción'),
    ('ocds-03ad3f-366249', None, ['12'], True, 'Pilar-General Díaz (ruta departamental, Ñeembucú)'),
    ('ocds-03ad3f-355468', None, ['08'], True, 'Yabebyry-Santa Rita: compañía de Misiones, no el distrito de Alto Paraná'),
    ('ocds-03ad3f-369248', 'santa rosa del monday', ['10'], True, 'Santa Rosa del Monday (Alto Paraná)'),
    ('ocds-03ad3f-369248', 'santa clara', ['02'], True, 'Santa Clara-Jhugua Rey-Choré (San Pedro)'),
    ('ocds-03ad3f-369248', "tava'?i", ['06', '07'], True, "Tava'i (Caazapá)-María Auxiliadora (Itapúa)"),
]
a['revision_manual'] = ''
for ocid, lote, dd, vec, nota in REVISION:
    m = a.ocid.eq(ocid) & (a.txt_l.str.contains(lote) if lote else True)
    a.loc[m, 'deptos'] = pd.Series([dd] * m.sum(), index=a.index[m], dtype=object)
    a.loc[m, 'metodo_ubicacion'] = 'revisión manual'
    if vec is not None: a.loc[m, 'camino_vecinal'] = vec & a.loc[m, 'obra_vial']
    a.loc[m, 'revision_manual'] = nota
a['n_deptos'] = a.deptos.str.len()

obras = a[a.obra_vial].copy()
obras['deptos_txt'] = obras.deptos.map(lambda l: ';'.join(l))
cols = ['ocid', 'adjudicacion_id', 'fecha_adjudicacion', 'anio', 'monto', 'camino_vecinal', 'deptos_txt', 'n_deptos',
        'metodo_ubicacion', 'revision_manual', 'titulo_llamado', 'lotes_adjudicados', 'categoria', 'modalidad']
obras[cols].rename(columns={'monto': 'monto_adjudicado_gs', 'deptos_txt': 'cod_dpto_asignados'}) \
    .sort_values(['anio', 'monto_adjudicado_gs'], ascending=[True, False]) \
    .to_csv(OUT + '/obras_viales_MOPC_2018_2025_clasificadas.csv', index=False, encoding='utf-8-sig')

# ---------------- 3. Monto por departamento y año ----------------
e = obras[obras.n_deptos > 0].explode('deptos')
e['monto_asignado'] = e.monto / e.n_deptos
panel = []
for tipo, sub in [('vial_total', e), ('camino_vecinal', e[e.camino_vecinal])]:
    p = sub.groupby(['deptos', 'anio']).monto_asignado.sum().rename(f'gs_{tipo}')
    panel.append(p)
panel = pd.concat(panel, axis=1).fillna(0).reset_index().rename(columns={'deptos': 'cod_dpto'})
full = pd.MultiIndex.from_product([ORIENTAL, range(2018, 2026)], names=['cod_dpto', 'anio']).to_frame(index=False)
panel = full.merge(panel, how='left').fillna(0)

# población rural y total del Censo 2022 por departamento
b = pd.read_csv(R + '/13_analisis_2022/base_distrital_2022.csv', dtype={'cod_dpto': str})
pob = b.groupby('cod_dpto').agg(pob_rural_2022=('censo_pob_rural', 'sum'), pob_total_2022=('censo_pob_total', 'sum'),
                                departamento=('departamento', 'first')).reset_index()
panel = panel.merge(pob, on='cod_dpto', how='left')
panel.to_csv(OUT + '/obras_MOPC_por_departamento_anio.csv', index=False, encoding='utf-8-sig')

# Intensidad acumulada 2018-2023 (obras adjudicadas antes de la encuesta 2024)
pre = panel[panel.anio <= 2023].groupby(['cod_dpto', 'departamento', 'pob_rural_2022', 'pob_total_2022'])[['gs_vial_total', 'gs_camino_vecinal']].sum().reset_index()
pre['gs_vecinal_por_hab_rural'] = pre.gs_camino_vecinal / pre.pob_rural_2022
pre['gs_vial_por_hab'] = pre.gs_vial_total / pre.pob_total_2022
# primer año con obra de camino vecinal adjudicada en el departamento (para el estudio de eventos)
fy = panel[panel.gs_camino_vecinal > 0].groupby('cod_dpto').anio.min()
pre['primer_anio_vecinal'] = pre.cod_dpto.map(fy)
# Grupos: tratamiento = intensidad de caminos vecinales por habitante rural por encima de la mediana de la Región Oriental
pre_or = pre[pre.cod_dpto != '11']  # Central se excluye de la muestra (casi sin población rural propiamente dicha)
med = pre_or.gs_vecinal_por_hab_rural.median()
pre['tratado'] = (pre.gs_vecinal_por_hab_rural > med).astype(int)
pre.loc[pre.cod_dpto == '11', 'tratado'] = np.nan
pre['tercil_intensidad'] = pd.qcut(pre.gs_vecinal_por_hab_rural.where(pre.cod_dpto != '11'), 3, labels=['baja', 'media', 'alta'])
pre['departamento_foco'] = pre.cod_dpto.isin(FOCO).astype(int)
pre.to_csv(OUT + '/tratamiento_por_departamento.csv', index=False, encoding='utf-8-sig')

res = obras.groupby('metodo_ubicacion').agg(n=('monto', 'size'), monto_gs=('monto', 'sum'))
res['pct_monto'] = (100 * res.monto_gs / res.monto_gs.sum()).round(1)
res.to_csv(OUT + '/obras_MOPC_resumen_ubicacion.csv', encoding='utf-8-sig')
print('Adjudicaciones', len(a), '| obras viales', len(obras), f'{obras.monto.sum()/1e12:.2f} billones Gs',
      '| caminos vecinales', int(obras.camino_vecinal.sum()), f'{obras[obras.camino_vecinal].monto.sum()/1e12:.2f} billones Gs')
print(res)
print(pre[['cod_dpto', 'departamento', 'gs_camino_vecinal', 'gs_vecinal_por_hab_rural', 'gs_vial_por_hab', 'primer_anio_vecinal', 'tratado']]
      .assign(gs_camino_vecinal=lambda x: (x.gs_camino_vecinal / 1e9).round(1)).round(0).to_string())
print('mediana', round(med))
