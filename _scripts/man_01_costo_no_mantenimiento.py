# Parte A: costo para el Estado de no mantener los caminos vecinales, por distrito, y simulación de una
# asignación de royalties municipales al mantenimiento (ver 22_propuesta_mantenimiento/).
# Modelo: costo anual equivalente (CAE) de dos políticas por km de camino vecinal mejorado:
#   con mantenimiento:  m + C * frc(r, vida_con)      (rehabilitar cada vida_con años y mantener todos los años)
#   sin mantenimiento:  C * frc(r, vida_sin)          (rehabilitar cada vida_sin años)
#   costo de no mantener = CAE sin - CAE con.  No incluye los costos de los usuarios (estimación conservadora).
import sys, zipfile, numpy as np, pandas as pd, geopandas as gpd, pyogrio, unicodedata

R = '/home/user/infraestructura_caminos'
OUT = R + '/22_propuesta_mantenimiento'
OSM = sys.argv[1] if len(sys.argv) > 1 else '/tmp/osm/roads.gpkg'   # roads.gpkg extraído de hotosm_pry_roads_osm_gpkg.zip
GDB = R + '/05_cartografia_y_codigos/COD-AB_OCHA_limites_admin/pry_admin_boundaries.gdb.zip'
TC = 7500  # Gs por USD (promedio aproximado 2025)
ORIENTAL = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14']
FOCO = ['01', '02', '05', '06', '14']

# ---------------- Parámetros (USD por km) y escenarios ----------------
# m: mantenimiento por niveles de servicio o convenio (rutinario y conservación), USD/km/año, del plan MOPC para el BID
#    (EEO 7, PR-L1092): contratos 2.573; convenios 2.602; PR-L1084 3.774; PR-L1092 1.870; CAF 2.200.
# C: rehabilitar un camino vecinal mejorado: 37.000 (estimación PAD Banco Mundial), 70.000 (estimación MOPC más baja,
#    EEO 7), 180.000 (estimación MOPC de tramos priorizados, EEO 7; el costo real en el proyecto del Banco Mundial
#    fue 174.000-222.000).
CENTRAL = dict(m=2600, C=70000, vida_sin=5, vida_con=15, r=0.12)
ESC = [('Central', {}),
       ('Mantenimiento barato (1.900)', dict(m=1900)), ('Mantenimiento caro (3.800)', dict(m=3800)),
       ('Rehabilitación barata (37.000)', dict(C=37000)), ('Rehabilitación cara (180.000)', dict(C=180000)),
       ('Sin mantenimiento dura 3 años', dict(vida_sin=3)), ('Sin mantenimiento dura 8 años', dict(vida_sin=8)),
       ('Con mantenimiento dura 10 años', dict(vida_con=10)), ('Con mantenimiento dura 20 años', dict(vida_con=20)),
       ('Tasa de descuento 6 %', dict(r=0.06)),
       ('Pesimista para el mantenimiento', dict(m=3800, C=37000, vida_sin=8, vida_con=10)),
       ('Optimista para el mantenimiento', dict(m=1900, C=180000, vida_sin=3, vida_con=20))]


def frc(r, n): return r / (1 - (1 + r) ** -n)


def cae(p):
    con = p['m'] + p['C'] * frc(p['r'], p['vida_con']); sin = p['C'] * frc(p['r'], p['vida_sin'])
    return dict(cae_con_mant=con, cae_sin_mant=sin, costo_no_mantener=sin - con,
                ahorro_por_usd_mant=(sin - (con - p['m'])) / p['m'])


esc = pd.DataFrame([dict(escenario=n, **{**CENTRAL, **c}, **cae({**CENTRAL, **c})) for n, c in ESC])
# vida sin mantenimiento a partir de la cual mantener deja de convenir (escenario central)
vs = np.arange(1, 15.01, 0.01)
umbral = vs[np.argmax([cae({**CENTRAL, 'vida_sin': v})['costo_no_mantener'] < 0 for v in vs])]
esc.to_csv(OUT + '/escenarios_costo_por_km.csv', index=False, encoding='utf-8-sig')
print(esc[['escenario', 'cae_con_mant', 'cae_sin_mant', 'costo_no_mantener', 'ahorro_por_usd_mant']].round(1).to_string())
print('Mantener deja de convenir si sin mantenimiento el camino dura más de', round(umbral, 1), 'años')

# ---------------- Km de caminos vecinales por distrito ----------------
inv = pd.read_csv(R + '/03_red_vial_MOPC/MOPC_inventario_km_por_red_y_superficie_dic2025.csv', dtype={'cod_dpto': str})
v = inv[inv.red == 'VECINAL'].set_index('cod_dpto')
v['km_mejorado'] = v.km_total - v.km_tierra_T
# Peso para repartir los km del departamento: largo de caminos rurales de OSM (tertiary, unclassified, track) en el distrito
osm = pyogrio.read_dataframe(OSM, columns=['highway'], where="highway IN ('tertiary','unclassified','track')").to_crs(32721)
osm['largo_km'] = osm.length / 1000
dist = gpd.read_file(GDB, layer='pry_admin2')[['adm2_pcode', 'adm2_name', 'geometry']].to_crs(32721)
pt = gpd.GeoDataFrame(osm[['largo_km']], geometry=osm.representative_point(), crs=32721)
j = gpd.sjoin(pt, dist, predicate='within', how='left')
L = j.groupby('adm2_pcode').largo_km.sum().rename('km_osm_rural')
d = dist.drop(columns='geometry').merge(L, on='adm2_pcode', how='left').fillna({'km_osm_rural': 0})
d['cod_dist'] = d.adm2_pcode.str[2:]; d['cod_dpto'] = d.cod_dist.str[:2]
d['peso'] = d.km_osm_rural / d.groupby('cod_dpto').km_osm_rural.transform('sum')
# Misiones (08) no figura en la tabla del inventario: se imputa con la razón km MOPC / km OSM del resto de la Región Oriental
osm_dpto = d.groupby('cod_dpto').km_osm_rural.sum()
ref = [c for c in ORIENTAL if c in v.index and c != '11']
assert '08' not in v.index
imp = {col: v.loc[ref, col].sum() / osm_dpto[ref].sum() * osm_dpto['08'] for col in ['km_total', 'km_mejorado']}
for col, x in imp.items(): v.loc['08', col] = x
v.loc['08', 'departamento'] = 'MISIONES (imputado)'
d['km_vecinal'] = d.peso * d.cod_dpto.map(v.km_total)
d['km_mejorado'] = d.peso * d.cod_dpto.map(v.km_mejorado)
# Red que el MOPC declara mantener (13.416 km, distritos de conservación): repartida según la red vecinal total
d['km_mopc_declara'] = 13416 * d.km_vecinal / d.km_vecinal.sum()
d = d[d.cod_dpto != '00'].copy()

# ---------------- Royalties y contexto ----------------
roy = pd.read_csv(R + '/10_economia_y_mercados/MEF_royalties_municipios/royalties_municipios_2025.csv', dtype={'cod_dist': str})
tr = pd.read_csv(R + '/10_economia_y_mercados/MEF_transferencias_municipios/transferencias_municipios_2024.csv', dtype={'cod_dist': str})
nbi = pd.read_csv(R + '/16_analisis_censal_nbi_2012_2022/base_modelo_distrital_nbi.csv', dtype={'cod_dist': str})
d = (d.merge(roy[['cod_dist', 'royalties_liquidado_2025_gs']], on='cod_dist', how='left')
      .merge(tr[['cod_dist', 'royalties_mill_gs']].rename(columns={'royalties_mill_gs': 'royalties_2024_mill_gs'}), on='cod_dist', how='left')
      .merge(nbi[['cod_dist', 'departamento', 'distrito', 'nbi_2022', 'censo_pob_total', 'censo_pob_rural', 'censo_pct_rural']], on='cod_dist', how='left'))
d = d.rename(columns={'royalties_liquidado_2025_gs': 'royalties_2025_gs'})
assert d.royalties_2025_gs.notna().all(), d[d.royalties_2025_gs.isna()]
d['region'] = np.where(d.cod_dpto.isin(ORIENTAL), 'Oriental', 'Occidental')
d['departamento_foco'] = d.cod_dpto.isin(FOCO).astype(int)

p = CENTRAL; c = cae(p)
m_gs = p['m'] * TC
for red, col in [('mejorada', 'km_mejorado'), ('mopc', 'km_mopc_declara'), ('total', 'km_vecinal')]:
    d[f'necesidad_{red}_gs'] = d[col] * m_gs                                   # presupuesto anual para mantener
    d[f'pct_royalties_{red}'] = 100 * d[f'necesidad_{red}_gs'] / d.royalties_2025_gs
d['costo_no_mantener_mejorada_gs'] = d.km_mejorado * c['costo_no_mantener'] * TC
cols = ['cod_dpto', 'departamento', 'cod_dist', 'distrito', 'region', 'departamento_foco', 'km_osm_rural', 'km_vecinal',
        'km_mejorado', 'km_mopc_declara', 'royalties_2025_gs', 'royalties_2024_mill_gs', 'necesidad_mejorada_gs',
        'necesidad_mopc_gs', 'necesidad_total_gs', 'pct_royalties_mejorada', 'pct_royalties_mopc', 'pct_royalties_total',
        'costo_no_mantener_mejorada_gs', 'nbi_2022', 'censo_pob_total', 'censo_pob_rural', 'censo_pct_rural']
d[cols].sort_values('cod_dist').to_csv(OUT + '/base_costo_mantenimiento_distrital.csv', index=False, encoding='utf-8-sig')

# ---------------- Resúmenes ----------------
def resumen(g):
    return pd.Series({'distritos': len(g), 'km_vecinal': g.km_vecinal.sum(), 'km_mejorado': g.km_mejorado.sum(),
                      'km_mopc_declara': g.km_mopc_declara.sum(), 'royalties_2025_mm_gs': g.royalties_2025_gs.sum() / 1e9,
                      'necesidad_mejorada_mm_gs': g.necesidad_mejorada_gs.sum() / 1e9,
                      'necesidad_mopc_mm_gs': g.necesidad_mopc_gs.sum() / 1e9,
                      'necesidad_total_mm_gs': g.necesidad_total_gs.sum() / 1e9,
                      'costo_no_mantener_mejorada_mm_gs': g.costo_no_mantener_mejorada_gs.sum() / 1e9})
tot = pd.concat([resumen(d).rename('País'), resumen(d[d.region == 'Oriental']).rename('Región Oriental'),
                 resumen(d[d.departamento_foco == 1]).rename('5 departamentos foco')], axis=1).T
for red in ['mejorada', 'mopc', 'total']:
    tot[f'pct_royalties_{red}'] = 100 * tot[f'necesidad_{red}_mm_gs'] / tot.royalties_2025_mm_gs
tot.to_csv(OUT + '/resumen_costo_mantenimiento.csv', encoding='utf-8-sig')
print(tot.round(1).T.to_string())
dep = d.groupby(['cod_dpto']).apply(resumen)
dep['departamento'] = dep.index.map(v.departamento)
for red in ['mejorada', 'mopc', 'total']:
    dep[f'pct_royalties_{red}'] = 100 * dep[f'necesidad_{red}_mm_gs'] / dep.royalties_2025_mm_gs
dep.to_csv(OUT + '/resumen_por_departamento.csv', encoding='utf-8-sig')
print(dep[['departamento', 'km_vecinal', 'km_mejorado', 'royalties_2025_mm_gs', 'pct_royalties_mejorada', 'pct_royalties_mopc', 'pct_royalties_total']].round(1).to_string())

# ---------------- Simulación de política: p % de los royalties municipales al mantenimiento ----------------
sim = []
for red, col in [('mejorada', 'km_mejorado'), ('mopc', 'km_mopc_declara'), ('total', 'km_vecinal')]:
    nec = d[f'necesidad_{red}_gs']
    for pct in [5, 10, 15, 20, 30]:
        fondo = pct / 100 * d.royalties_2025_gs
        cub_mun = np.minimum(fondo, nec)                   # A: cada municipio financia sus propios caminos
        pool = fondo.sum(); cub_pool = min(pool, nec.sum())  # B: fondo común asignado según los km
        sim.append(dict(red=red, pct_royalties=pct, fondo_mm_gs=pool / 1e9, necesidad_mm_gs=nec.sum() / 1e9,
                        A_cobertura_pct=100 * cub_mun.sum() / nec.sum(), A_km_cubiertos=(cub_mun / m_gs).sum(),
                        A_sobrante_mm_gs=(fondo - cub_mun).sum() / 1e9,
                        A_distritos_cubiertos_100=(fondo >= nec - 1).sum(),
                        B_cobertura_pct=100 * cub_pool / nec.sum(), B_km_cubiertos=cub_pool / m_gs,
                        ahorro_neto_A_mm_gs=((cub_mun / m_gs) * c['costo_no_mantener'] * TC).sum() / 1e9 if red == 'mejorada' else np.nan,
                        ahorro_neto_B_mm_gs=(cub_pool / m_gs) * c['costo_no_mantener'] * TC / 1e9 if red == 'mejorada' else np.nan))
sim = pd.DataFrame(sim)
sim.to_csv(OUT + '/simulacion_royalties.csv', index=False, encoding='utf-8-sig')
print(sim.round(1).to_string())
for red in ['mejorada', 'mopc']:
    q = d[f'pct_royalties_{red}']
    print(f'Distritos según % de royalties necesario (red {red}):',
          {'<5': (q < 5).sum(), '5-10': q.between(5, 10).sum(), '10-20': q.between(10, 20).sum(), '20-50': q.between(20, 50).sum(), '>50': (q > 50).sum()})
    print('  Spearman con NBI 2022:', round(d[['nbi_2022', f'pct_royalties_{red}']].corr(method='spearman').iloc[0, 1], 2),
          '| con % rural:', round(d[['censo_pct_rural', f'pct_royalties_{red}']].corr(method='spearman').iloc[0, 1], 2))
q = d.pct_royalties_mopc
print('Distritos según % de royalties necesario (red MOPC 13.416 km):',
      {'<5': (q < 5).sum(), '5-10': q.between(5, 10).sum(), '10-20': q.between(10, 20).sum(), '20-50': q.between(20, 50).sum(), '>50': (q > 50).sum()})
print('Correlación NBI 2022 vs % royalties necesario (red MOPC):', round(d[['nbi_2022', 'pct_royalties_mopc']].corr(method='spearman').iloc[0, 1], 2))
