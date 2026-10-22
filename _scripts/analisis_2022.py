# Base distrital 2022 y primeras estimaciones: calidad de caminos vecinales, lluvia y condiciones de vida rural.
# Corte transversal 2022 (Censo), Región Oriental sin Asunción ni Central, MCO ponderado con efectos fijos de departamento.
import os, numpy as np, pandas as pd, statsmodels.formula.api as smf, geopandas as gpd

R = '/home/user/infraestructura_caminos'
OUT = R + '/13_analisis_2022'
os.makedirs(OUT, exist_ok=True)
FOCO = ['01', '02', '05', '06', '14']
ORIENTAL = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '12', '13', '14']  # sin Asunción (00) ni Central (11)
rng = np.random.default_rng(20221109)

# ---------------- 1. Base 2022 ----------------
b = pd.read_csv(R + '/00_base_integrada/base_distrital_integrada.csv', dtype={'cod_dist': str, 'cod_dpto': str})
c = pd.read_csv(R + '/12_INE_complementario/Censo_2022_indicadores_localidad/censo2022_indicadores_distrito.csv').copy()
c['cod_dist'] = c.cod_dep.astype(int).map('{:02d}'.format) + c.cod_dis.astype(int).map('{:02d}'.format)
VIV = {'viv4': 'pct_viv_electricidad', 'viv5': 'pct_viv_agua_corriente', 'viv25': 'pct_viv_piso_tierra',
       'viv61': 'pct_viv_cocina_lena', 'viv60': 'pct_viv_sin_bienes', 'viv48': 'pct_viv_internet', 'viv57': 'pct_viv_vehiculo'}
c = pd.concat([c[['cod_dist']], pd.DataFrame({n: 100 * c[v] / c['viv2'] for v, n in VIV.items()})], axis=1)

g = pd.read_csv(R + '/11_infraestructura_vial_complementaria/GRIP4_red_vial_global/GRIP4_km_por_distrito.csv', dtype={'cod_dist': str})
g['grip_pct_tierra'] = 100 * g.km_tierra / g.km_total
g = g[['cod_dist', 'grip_pct_tierra', 'km_total', 'km_tierra', 'area_km2', 'densidad_km_por_100km2']].rename(
    columns={'km_total': 'grip_km_total', 'km_tierra': 'grip_km_tierra', 'densidad_km_por_100km2': 'grip_densidad_km_100km2'})

o = pd.read_csv(R + '/11_infraestructura_vial_complementaria/Overture_Maps_red_vial/overture_km_red_vial_por_distrito.csv', dtype={'cod_dist': str})
o = o[['cod_dist', 'pct_rural_vecinal_no_pavimentado', 'pct_rural_vecinal_sin_dato_superficie']].rename(
    columns={'pct_rural_vecinal_no_pavimentado': 'overture_pct_vecinal_no_pav', 'pct_rural_vecinal_sin_dato_superficie': 'overture_pct_vecinal_sin_dato'})

L = R + '/07_clima_y_contexto/lluvia_CHIRPS_raster/'
an = pd.read_csv(L + 'lluvia_anual_por_distrito_1991_2024.csv', dtype={'cod_dist': str})
clim = an[an.anio.between(1991, 2020)].groupby('cod_dist').lluvia_mm.mean().rename('lluvia_normal_1991_2020')
rec = an[an.anio.between(2013, 2022)].groupby('cod_dist').lluvia_mm.mean().rename('lluvia_media_2013_2022')
pre = pd.read_csv(L + 'lluvia_nov2021_oct2022_por_distrito.csv', dtype={'cod_dist': str}).set_index('cod_dist').lluvia_12m_precenso_mm
ll = pd.concat([clim, rec, pre], axis=1).reset_index().rename(columns={'index': 'cod_dist'})
ll['lluvia_anomalia_precenso_pct'] = 100 * (ll.lluvia_12m_precenso_mm / ll.lluvia_normal_1991_2020 - 1)

ine = pd.read_csv(R + '/09_servicios_complementarios/INE_geoportal_capas/INE_geoportal_por_distrito.csv', dtype={'cod_dist': str})
ine = ine[['cod_dist', 'n_comunidades_indigenas_INE_2022', 'n_locales_educativos_INE_rural', 'n_puestos_salud_publicos_INE_rural']]

d = (b.merge(c, on='cod_dist', how='left').merge(g, on='cod_dist', how='left').merge(o, on='cod_dist', how='left')
      .merge(ll, on='cod_dist', how='left').merge(ine, on='cod_dist', how='left'))
d['densidad_pob_km2'] = d.censo_pob_total / d.area_km2
d['log_densidad_pob'] = np.log(d.densidad_pob_km2)
d['log_area_km2'] = np.log(d.area_km2)
d['log_luz_2013_km2'] = np.log1p(d.luz_suma_2013 / d.area_km2 * 100)
d['log_luz_pc_2022'] = np.log1p(d.luz_por_1000_hab_2022)
d['comunidades_indigenas'] = (d.n_comunidades_indigenas_INE_2022.fillna(0) > 0).astype(int)
d['region_oriental_muestra'] = d.cod_dpto.isin(ORIENTAL).map({True: 'Sí', False: 'No'})
d['foco'] = d.cod_dpto.isin(FOCO).astype(int)
keep = ['cod_dpto', 'departamento', 'cod_dist', 'distrito', 'departamento_foco', 'foco', 'region_oriental_muestra',
        'censo_pob_total', 'censo_pob_rural', 'censo_pct_rural', 'area_km2', 'densidad_pob_km2', 'log_densidad_pob', 'log_area_km2',
        'ipm_H_rural', 'ipm_M0_rural', 'ipm_H_total', 'nbi_al_menos_una_pct', 'nbi_vivienda_pct', 'nbi_sanitaria_pct', 'nbi_educacion_pct', 'nbi_subsistencia_pct',
        'pct_viv_electricidad', 'pct_viv_agua_corriente', 'pct_viv_piso_tierra', 'pct_viv_cocina_lena', 'pct_viv_sin_bienes', 'pct_viv_internet', 'pct_viv_vehiculo',
        'luz_suma_2013', 'luz_suma_2022', 'luz_por_1000_hab_2022', 'log_luz_pc_2022', 'log_luz_2013_km2',
        'grip_pct_tierra', 'grip_km_total', 'grip_km_tierra', 'grip_densidad_km_100km2', 'overture_pct_vecinal_no_pav', 'overture_pct_vecinal_sin_dato',
        'RAI_pct', 'pct_pob_acceso_hospitals_1h', 'pct_pob_acceso_primary_healthcare_30min', 'pct_pob_acceso_education_5km',
        'lluvia_normal_1991_2020', 'lluvia_media_2013_2022', 'lluvia_12m_precenso_mm', 'lluvia_anomalia_precenso_pct',
        'n_comunidades_indigenas_INE_2022', 'comunidades_indigenas', 'n_locales_educativos_INE_rural', 'n_puestos_salud_publicos_INE_rural']
d = d[keep]
d.to_csv(OUT + '/base_distrital_2022.csv', index=False, encoding='utf-8-sig')

# ---------------- 2. Muestra y variables de análisis ----------------
s = d[(d.region_oriental_muestra == 'Sí') & (d.censo_pob_rural > 0)].copy()
s = s.dropna(subset=['ipm_H_rural', 'grip_pct_tierra', 'lluvia_media_2013_2022', 'log_luz_2013_km2'])
s['tierra10'] = (s.grip_pct_tierra - s.grip_pct_tierra.mean()) / 10            # 10 puntos porcentuales de red de tierra, centrado
s['lluvia100'] = (s.lluvia_media_2013_2022 - s.lluvia_media_2013_2022.mean()) / 100  # 100 mm/año, centrado
s['anom10'] = s.lluvia_anomalia_precenso_pct / 10                                # 10 % de anomalía pre-censo
s['rai_inv10'] = (100 - s.RAI_pct) / 10                                         # 10 pp de población rural SIN camino de todo tiempo a 2 km
s['w'] = s.censo_pob_rural
CTRL = 'log_densidad_pob + censo_pct_rural + log_luz_2013_km2 + log_area_km2 + comunidades_indigenas'
FE = 'C(cod_dpto)'

def fit(formula, data):
    return smf.wls(formula, data=data, weights=data.w).fit(cov_type='cluster', cov_kwds={'groups': data.cod_dpto})

def fit_hc1(formula, data):
    return smf.wls(formula, data=data, weights=data.w).fit(cov_type='HC1')

def wild_cluster_p(formula, data, var, reps=999):
    """p-valor wild cluster bootstrap restringido (Webb 6 puntos), conglomerados = departamento."""
    full = fit(formula, data)
    t_obs = full.params[var] / full.bse[var]
    rhs = formula.split('~')[1]
    restricted_formula = formula.split('~')[0] + '~' + ' + '.join(x.strip() for x in rhs.split('+') if x.strip() != var)
    restricted = smf.wls(restricted_formula, data=data, weights=data.w).fit()
    yhat, u = restricted.fittedvalues, restricted.resid
    groups = data.cod_dpto.values; ug = np.unique(groups)
    webb = np.array([-np.sqrt(1.5), -1, -np.sqrt(.5), np.sqrt(.5), 1, np.sqrt(1.5)])
    yname = formula.split('~')[0].strip(); cnt = 0
    for _ in range(reps):
        wmap = dict(zip(ug, rng.choice(webb, len(ug))))
        dd = data.copy(); dd[yname] = yhat + u * np.vectorize(wmap.get)(groups)
        m = fit(formula, dd); cnt += abs(m.params[var] / m.bse[var]) >= abs(t_obs)
    return (cnt + 1) / (reps + 1)

def row(m, var, model, outcome, extra=None):
    r = dict(resultado=outcome, modelo=model, variable=var, coef=m.params[var], ee_cluster=m.bse[var], p_cluster=m.pvalues[var],
             n=int(m.nobs), r2=m.rsquared)
    if extra: r.update(extra)
    return r

res = []
Y = 'ipm_H_rural'
m1 = fit(f'{Y} ~ tierra10 + {FE}', s)
m2 = fit(f'{Y} ~ tierra10 + {CTRL} + {FE}', s)
m3f = f'{Y} ~ tierra10 + lluvia100 + tierra10:lluvia100 + {CTRL} + {FE}'
m3 = fit(m3f, s)
m4 = fit(f'{Y} ~ tierra10 + anom10 + tierra10:anom10 + lluvia100 + {CTRL} + {FE}', s)
m5 = fit(f'{Y} ~ tierra10 + tierra10:foco + lluvia100 + tierra10:lluvia100 + {CTRL} + {FE}', s)
m6 = fit(f'{Y} ~ rai_inv10 + lluvia100 + rai_inv10:lluvia100 + {CTRL} + {FE}', s.dropna(subset=['rai_inv10']))
m3h = fit_hc1(m3f, s)

p_wb = {v: wild_cluster_p(m3f, s, v) for v in ['tierra10', 'tierra10:lluvia100']}
for name, m, vs in [('M1 sin controles', m1, ['tierra10']), ('M2 con controles', m2, ['tierra10']),
                    ('M3 + lluvia e interacción', m3, ['tierra10', 'lluvia100', 'tierra10:lluvia100']),
                    ('M4 anomalía pre-censo', m4, ['tierra10', 'anom10', 'tierra10:anom10']),
                    ('M5 heterogeneidad foco', m5, ['tierra10', 'tierra10:foco', 'tierra10:lluvia100']),
                    ('M6 RAI (HeiGIT 2026) en vez de GRIP', m6, ['rai_inv10', 'lluvia100', 'rai_inv10:lluvia100'])]:
    for v in vs:
        extra = {'p_wild_bootstrap': p_wb.get(v)} if name.startswith('M3') else None
        if name.startswith('M3'): extra = dict(extra or {}, p_hc1=m3h.pvalues[v])
        res.append(row(m, v, name, Y, extra))

# Oster (2019): delta con Rmax = 1.3 R2 largo
b_s, r_s, b_l, r_l = m1.params['tierra10'], m1.rsquared, m2.params['tierra10'], m2.rsquared
rmax = min(1.3 * r_l, 1)
oster_delta = b_l * (r_l - r_s) / ((b_s - b_l) * (rmax - r_l)) if b_s != b_l else np.inf

# Otros resultados (mecanismos) con la especificación M3
OUTS = {'ipm_M0_rural': 'IPM M0 rural', 'nbi_al_menos_una_pct': 'NBI al menos una', 'nbi_educacion_pct': 'NBI acceso a educación',
        'nbi_sanitaria_pct': 'NBI infraestructura sanitaria', 'pct_viv_electricidad': '% viviendas con electricidad',
        'pct_viv_agua_corriente': '% viviendas con agua corriente', 'pct_viv_cocina_lena': '% viviendas que cocinan con leña',
        'pct_viv_sin_bienes': '% viviendas sin ningún bien', 'pct_pob_acceso_hospitals_1h': '% población con hospital a < 1 h',
        'log_luz_pc_2022': 'log luz por 1.000 hab. 2022'}
for y, lab in OUTS.items():
    dd = s.dropna(subset=[y])
    m = fit(f'{y} ~ tierra10 + lluvia100 + tierra10:lluvia100 + {CTRL} + {FE}', dd)
    for v in ['tierra10', 'tierra10:lluvia100']:
        res.append(row(m, v, 'M3 (mecanismos)', lab))
R_ = pd.DataFrame(res)
R_.to_csv(OUT + '/resultados_estimaciones_2022.csv', index=False, encoding='utf-8-sig')

# Autocorrelación espacial de residuos (I de Moran, vecinos por contigüidad)
gg = gpd.read_file(R + '/05_cartografia_y_codigos/COD-AB_OCHA_limites_admin/pry_admin_boundaries.gdb.zip', layer='pry_admin2')[['adm2_pcode', 'geometry']]
gg['cod_dist'] = gg.adm2_pcode.str[2:]
gg = gg[gg.cod_dist.isin(s.cod_dist)].set_index('cod_dist').loc[s.cod_dist]
e = pd.Series(m3.resid.values, index=s.cod_dist.values); e = e - e.mean()
nb = gpd.sjoin(gg.reset_index()[['cod_dist', 'geometry']], gg.reset_index()[['cod_dist', 'geometry']], predicate='touches')
nb = nb[nb.cod_dist_left != nb.cod_dist_right]
W = nb.groupby('cod_dist_left').cod_dist_right.apply(list)
num = sum(e[i] * np.mean([e[j] for j in W.get(i, [])]) for i in e.index if len(W.get(i, [])) > 0)
moran = num / (e ** 2).sum() * len(e) / sum(1 for i in e.index if len(W.get(i, [])) > 0)

desc = s[['ipm_H_rural', 'nbi_al_menos_una_pct', 'grip_pct_tierra', 'RAI_pct', 'lluvia_media_2013_2022', 'lluvia_anomalia_precenso_pct',
          'censo_pct_rural', 'densidad_pob_km2', 'luz_por_1000_hab_2022']].describe().T.round(2)
desc.to_csv(OUT + '/descriptivos_muestra_2022.csv', encoding='utf-8-sig')
with open(OUT + '/_resumen_corrida.txt', 'w', encoding='utf-8') as f:
    f.write(f'n_muestra={len(s)} distritos (foco={int(s.foco.sum())}); excluidos por datos faltantes o sin población rural={int(((d.region_oriental_muestra=="Sí")).sum()-len(s))}\n')
    f.write(f'oster_delta={oster_delta:.2f} (Rmax=1.3*R2); beta_corto={b_s:.3f} R2={r_s:.3f}; beta_largo={b_l:.3f} R2={r_l:.3f}\n')
    f.write(f'moran_I_residuos_M3={moran:.3f}\n')
    f.write(m3.summary().as_text())
print(open(OUT + '/_resumen_corrida.txt', encoding='utf-8').read()[:600])
pd.set_option('display.width', 250)
print(R_.round(3).to_string(index=False))
print(desc)
