# Paso 2 del análisis censal: antes y después por distrito (NBI Censo 2012 frente a Censo 2022).
# Tratamiento: distrito con al menos una obra del MOPC en caminos vecinales o departamentales adjudicada entre 2012 y 2020
# y ubicada en el distrito (cen_01). Con dos censos, la diferencia en diferencias equivale a regresar el cambio del NBI
# (2022 - 2012) sobre el tratamiento, con efectos fijos de departamento (se comparan distritos del mismo departamento).
import os, sys, numpy as np, pandas as pd, geopandas as gpd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from econometria import Fit

R = '/home/user/infraestructura_caminos'
OUT = R + '/16_analisis_censal_nbi_2012_2022'
MUESTRA = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '12', '13', '14']  # Región Oriental sin Asunción ni Central
FOCO = ['01', '02', '05', '06', '14']

# ---------------- 1. Distritos comparables entre 2012 y 2022 ----------------
n12 = pd.read_csv(R + '/12_INE_complementario/NBI_distrital_2012_2022/nbi_2012_distrital.csv', dtype={'cod_dist_2012': str})
g12 = gpd.read_file(R + '/12_INE_complementario/NBI_distrital_2012_2022/distritos_2012_limites.gpkg').to_crs(32721)
g22 = gpd.read_file(R + '/05_cartografia_y_codigos/COD-AB_OCHA_limites_admin/pry_admin_boundaries.gdb.zip', layer='pry_admin2')[['adm2_pcode', 'geometry']].to_crs(32721)
g22['cod_dist'] = g22.adm2_pcode.str[2:]
a12 = g12.set_index('cod_dist_2012').area; a22 = g22.set_index('cod_dist').area
o = gpd.overlay(g22[['cod_dist', 'geometry']], g12[['cod_dist_2012', 'geometry']], how='intersection', keep_geom_type=True)
o = o[o.cod_dist == o.cod_dist_2012]
o['area'] = o.area
same = o.groupby('cod_dist').area.sum()
est = pd.DataFrame({'pct_area_2012_mismo_codigo': 100 * same / a12.reindex(same.index), 'pct_area_2022_mismo_codigo': 100 * same / a22.reindex(same.index)})
# distrito estable: el mismo código cubre al menos el 85 % del territorio en los dos censos (excluye los 13 distritos nuevos
# y los distritos de los que se separaron)
est['distrito_estable'] = ((est.pct_area_2012_mismo_codigo >= 85) & (est.pct_area_2022_mismo_codigo >= 85)).astype(int)

# ---------------- 2. Base del modelo ----------------
b = pd.read_csv(R + '/13_analisis_2022/base_distrital_2022.csv', dtype={'cod_dist': str, 'cod_dpto': str})
b = b[['cod_dpto', 'departamento', 'cod_dist', 'distrito', 'censo_pob_total', 'censo_pob_rural', 'censo_pct_rural', 'log_densidad_pob',
       'log_area_km2', 'lluvia_media_2013_2022', 'nbi_al_menos_una_pct']].rename(columns={'nbi_al_menos_una_pct': 'nbi_2022'})
b = b.merge(n12[['cod_dist_2012', 'nbi_al_menos_una_pct_2012']].rename(columns={'cod_dist_2012': 'cod_dist', 'nbi_al_menos_una_pct_2012': 'nbi_2012'}),
            on='cod_dist', how='left').merge(est, left_on='cod_dist', right_index=True, how='left')
ob = pd.read_csv(OUT + '/obras_vecinales_por_distrito.csv', dtype={'cod_dist': str})
b = b.merge(ob, on='cod_dist', how='left')
b[['n_obras_2012_2020', 'gs_2012_2020', 'n_obras_2021_2025', 'gs_2021_2025']] = b[['n_obras_2012_2020', 'gs_2012_2020', 'n_obras_2021_2025', 'gs_2021_2025']].fillna(0)
solo = pd.read_csv(OUT + '/obras_vecinales_solo_departamento_2012_2020.csv', dtype={'cod_dpto': str})
b = b.merge(solo, on='cod_dpto', how='left').fillna({'gs_solo_departamento_2012_2020': 0})
pr = b.groupby('cod_dpto').censo_pob_rural.transform('sum')
b['gs_solo_dpto_por_hab_rural'] = b.gs_solo_departamento_2012_2020 / pr / 1e6
b['obra'] = (b.n_obras_2012_2020 > 0).astype(int)
b['obra_temprana'] = (b.primer_anio_2012_2020 <= 2016).astype(int)          # primera obra 2012-2016
b['obra_tardia'] = ((b.obra == 1) & (b.obra_temprana == 0)).astype(int)    # primera obra 2017-2020
b['log_intensidad'] = np.log1p(b.gs_2012_2020 / b.censo_pob_rural.clip(lower=100) / 1e5)  # log(1 + Gs por hab. rural / 100.000)
b['d_nbi'] = b.nbi_2022 - b.nbi_2012
b['departamento_foco'] = b.cod_dpto.isin(FOCO).astype(int)
b['obra_foco'] = b.obra * b.departamento_foco
b['muestra'] = (b.cod_dpto.isin(MUESTRA) & (b.distrito_estable == 1) & b.nbi_2012.notna() & b.nbi_2022.notna()).astype(int)
b['w'] = 1.0
cols = ['cod_dpto', 'departamento', 'cod_dist', 'distrito', 'departamento_foco', 'muestra', 'distrito_estable', 'pct_area_2012_mismo_codigo',
        'pct_area_2022_mismo_codigo', 'nbi_2012', 'nbi_2022', 'd_nbi', 'obra', 'obra_temprana', 'obra_tardia', 'n_obras_2012_2020',
        'gs_2012_2020', 'primer_anio_2012_2020', 'log_intensidad', 'n_obras_2021_2025', 'gs_2021_2025', 'gs_solo_dpto_por_hab_rural',
        'censo_pob_total', 'censo_pob_rural', 'censo_pct_rural', 'log_densidad_pob', 'log_area_km2', 'lluvia_media_2013_2022']
b[cols].to_csv(OUT + '/base_modelo_distrital_nbi.csv', index=False, encoding='utf-8-sig')
s = b[b.muestra == 1].copy()
print('distritos en la muestra:', len(s), '| con obra 2012-2020:', int(s.obra.sum()), '| sin obra:', int((s.obra == 0).sum()))

# ---------------- 3. Estimaciones ----------------
CTRL = 'censo_pct_rural + log_densidad_pob + log_area_km2 + lluvia_media_2013_2022'
res = []


def correr(nombre, formula, d, var, nota=''):
    m = Fit(formula, d, var)                       # errores agrupados por departamento + wild bootstrap
    r_ = Fit(formula, d, var, grupo='cod_dist')    # errores robustos (cada distrito es su propio grupo)
    res.append(dict(modelo=nombre, variable=var, coef=m.coef(), ee_cluster_dpto=m.se[m.j], p_cluster_dpto=m.p_cluster(),
                    p_wild_bootstrap=m.p_wild(), ee_robusto=r_.se[r_.j], p_robusto=r_.p_cluster(), n=m.n, n_dptos=len(m.G),
                    n_tratados=int(d.loc[m.d.index, 'obra'].sum()), nota=nota))
    x = res[-1]
    print(f"{nombre:42s} {var:16s} {x['coef']:7.2f} p_dpto={x['p_cluster_dpto']:.3f} wild={x['p_wild_bootstrap']:.3f} p_rob={x['p_robusto']:.3f} n={x['n']}", flush=True)


correr('C1 Cambio NBI ~ obra + EF depto', 'd_nbi ~ obra + C(cod_dpto)', s, 'obra')
correr('C2 + controles', f'd_nbi ~ obra + C(cod_dpto) + {CTRL}', s, 'obra')
correr('C3 + NBI 2012 (nivel inicial)', f'd_nbi ~ obra + nbi_2012 + C(cod_dpto) + {CTRL}', s, 'obra',
       'controla la convergencia: los distritos con más NBI en 2012 bajan más')
correr('C4 Intensidad (log Gs por hab. rural)', f'd_nbi ~ log_intensidad + nbi_2012 + C(cod_dpto) + {CTRL}', s, 'log_intensidad')
correr('C5a Obra temprana (2012-2016)', f'd_nbi ~ obra_temprana + obra_tardia + nbi_2012 + C(cod_dpto) + {CTRL}', s, 'obra_temprana')
correr('C5b Obra tardía (2017-2020)', f'd_nbi ~ obra_temprana + obra_tardia + nbi_2012 + C(cod_dpto) + {CTRL}', s, 'obra_tardia')
correr('C6 Diferencia en departamentos foco', f'd_nbi ~ obra + obra_foco + nbi_2012 + C(cod_dpto) + {CTRL}', s, 'obra_foco')
sf = s[s.departamento_foco == 1]
correr('C7 Solo departamentos foco', f'd_nbi ~ obra + nbi_2012 + C(cod_dpto) + {CTRL}', sf, 'obra', '5 departamentos: inferencia poco confiable')
sw = s.assign(w=s.censo_pob_total)
correr('C8 Ponderado por población', f'd_nbi ~ obra + nbi_2012 + C(cod_dpto) + {CTRL}', sw, 'obra')
lim = s.drop_duplicates('cod_dpto').gs_solo_dpto_por_hab_rural.median()
sc = s[s.gs_solo_dpto_por_hab_rural <= lim]
correr('C9 Departamentos con pocas obras sin ubicar', f'd_nbi ~ obra + nbi_2012 + C(cod_dpto) + {CTRL}', sc, 'obra',
       'menos riesgo de que un distrito "sin obra" haya tenido una obra no ubicada')
pd.DataFrame(res).to_csv(OUT + '/resultados_nbi_2012_2022.csv', index=False, encoding='utf-8-sig')

# Balance y descriptivos: distritos con y sin obra
def fila(g, nombre):
    return dict(grupo=nombre, distritos=len(g), nbi_2012=g.nbi_2012.mean(), nbi_2022=g.nbi_2022.mean(), cambio_nbi=g.d_nbi.mean(),
                pct_rural=g.censo_pct_rural.mean(), log_densidad=g.log_densidad_pob.mean(), lluvia=g.lluvia_media_2013_2022.mean())
desc = pd.DataFrame([fila(s[s.obra == 1], 'con obra 2012-2020'), fila(s[s.obra == 0], 'sin obra ubicada'),
                     fila(sf[sf.obra == 1], 'foco: con obra'), fila(sf[sf.obra == 0], 'foco: sin obra ubicada')])
desc.to_csv(OUT + '/descriptivos_con_y_sin_obra.csv', index=False, encoding='utf-8-sig')
print(desc.round(2).to_string())
