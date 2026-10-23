# Paso 2 del análisis de inversión vial de todas las entidades: estimaciones fijadas en PLAN_DE_ANALISIS.md.
import os, sys, numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from econometria import Fit

R = '/home/user/infraestructura_caminos'
OUT = R + '/17_inversion_vial_todas_entidades'
b = pd.read_csv(OUT + '/base_modelo_inversion_vial_distrital.csv', dtype={'cod_dist': str, 'cod_dpto': str})
s = b[b.muestra == 1].copy(); s['w'] = 1.0
s['T_rural_foco'] = s.T_rural * s.departamento_foco
CTRL = 'censo_pct_rural + log_densidad_pob + log_area_km2 + lluvia_media_2013_2022'
tc = stats.t.ppf(0.975, 12)
rng = np.random.default_rng(1729)
res = []


def permutacion(m, reps=2000):
    yw = m.y * m.sw; Xw = m.Xw.copy(); tr = m.d[m.var].values; grp = m.d.cod_dpto.values; dist = []
    for _ in range(reps):
        t2 = tr.copy()
        for gg in np.unique(grp):
            ix = np.where(grp == gg)[0]; t2[ix] = rng.permutation(tr[ix])
        Xw[:, m.j] = t2 * m.sw
        dist.append(np.linalg.lstsq(Xw, yw, rcond=None)[0][m.j])
    return (np.abs(dist) >= abs(m.coef())).mean()


def correr(nombre, formula, d, var, perm=False, tipo='secundaria'):
    m = Fit(formula, d, var); r_ = Fit(formula, d, var, grupo='cod_dist')
    x = dict(tipo=tipo, modelo=nombre, variable=var, coef=m.coef(), ee_cluster_dpto=m.se[m.j], ic95_inf=m.coef() - tc * m.se[m.j],
             ic95_sup=m.coef() + tc * m.se[m.j], p_cluster_dpto=m.p_cluster(), p_wild_bootstrap=m.p_wild(), p_robusto=r_.p_cluster(),
             p_permutacion=permutacion(m) if perm else np.nan, n=m.n, sd_variable=d.loc[m.d.index, var].std())
    res.append(x)
    print(f"{nombre:46s} {var:20s} {x['coef']:7.3f} [{x['ic95_inf']:.2f}; {x['ic95_sup']:.2f}] wild={x['p_wild_bootstrap']:.3f} "
          f"perm={x['p_permutacion']:.3f} n={x['n']}", flush=True)
    return m


# ---------------- Especificación principal ----------------
f0 = f'd_nbi ~ T_rural + T_urbano + nbi_2012 + C(cod_dpto) + {CTRL}'
correr('P Principal: caminos rurales (municipal + MOPC)', f0, s, 'T_rural', perm=True, tipo='principal')
correr('P Principal: obras urbanas (placebo, mismo modelo)', f0, s, 'T_urbano', perm=True, tipo='principal')
# ---------------- Secundarias ----------------
correr('S1 Sin NBI 2012', f'd_nbi ~ T_rural + T_urbano + C(cod_dpto) + {CTRL}', s, 'T_rural', perm=True)
correr('S3a Solo inversión rural municipal', f'd_nbi ~ T_rural_municipal + T_urbano + nbi_2012 + C(cod_dpto) + {CTRL}', s, 'T_rural_municipal')
correr('S3b Solo MOPC ubicado', f'd_nbi ~ T_rural_mopc + T_urbano + nbi_2012 + C(cod_dpto) + {CTRL}', s, 'T_rural_mopc')
correr('S4 Diferencia en departamentos foco', f'd_nbi ~ T_rural + T_rural_foco + T_urbano + nbi_2012 + C(cod_dpto) + {CTRL}', s, 'T_rural_foco')
f5 = f'd_nbi ~ T_rural_2012_2016 + T_rural_2017_2020 + T_urbano + nbi_2012 + C(cod_dpto) + {CTRL}'
correr('S5a Inversión rural 2012-2016', f5, s, 'T_rural_2012_2016')
correr('S5b Inversión rural 2017-2020', f5, s, 'T_rural_2017_2020')

# ---------------- S6: luz nocturna, panel distrito-año ----------------
an = pd.read_csv(OUT + '/inversion_vial_por_distrito_anio.csv', dtype={'cod_dist': str})
l = pd.read_csv(R + '/07_clima_y_contexto/luces_nocturnas_VIIRS/luces_nocturnas_por_distrito_2012_2024.csv', dtype={'cod_dist': str})
l = l[l.cod_dist.isin(s.cod_dist)].merge(s[['cod_dist', 'cod_dpto', 'log_area_km2', 'censo_pob_rural']], on='cod_dist')
l['log_luz_km2'] = np.log1p(l.luz_suma / np.exp(l.log_area_km2) * 100)
pan = pd.MultiIndex.from_product([s.cod_dist, range(2012, 2025)], names=['cod_dist', 'anio']).to_frame(index=False)
pan = pan.merge(an[['cod_dist', 'anio', 'rural_total']], how='left').fillna({'rural_total': 0}).sort_values(['cod_dist', 'anio'])
pan['acum'] = pan.groupby('cod_dist').rural_total.cumsum()
pan['acum_t1'] = pan.groupby('cod_dist').acum.shift(1).fillna(0)     # hasta el año anterior
pan['acum_f2'] = pan.groupby('cod_dist').acum.shift(-2)              # dos años después (prueba de tendencias previas)
l = l.merge(pan[['cod_dist', 'anio', 'acum_t1', 'acum_f2']], on=['cod_dist', 'anio'])
pr = l.censo_pob_rural.clip(lower=100) * 1000
l['inv_acum_t1'] = np.log1p(l.acum_t1 / pr); l['inv_acum_futura'] = np.log1p(l.acum_f2 / pr)
l['dpto_anio'] = l.cod_dpto + '_' + l.anio.astype(str); l['w'] = 1.0
lp = l[l.anio.between(2013, 2022)].dropna(subset=['inv_acum_futura'])
f6 = 'log_luz_km2 ~ inv_acum_t1 + inv_acum_futura + C(cod_dist) + C(dpto_anio)'
correr('S6 Luz: inversión rural acumulada (t-1)', f6, lp, 'inv_acum_t1')
correr('S6 Luz: inversión futura (t+2), debería ser 0', f6, lp, 'inv_acum_futura')

# ---------------- Exploratorios (no estaban en el plan; se informan como tales) ----------------
s['T_rural_no_foco'] = s.T_rural * (1 - s.departamento_foco); s['T_rural_en_foco'] = s.T_rural * s.departamento_foco
fe = f'd_nbi ~ T_rural_no_foco + T_rural_en_foco + T_urbano + nbi_2012 + C(cod_dpto) + {CTRL}'
correr('E1a Pendiente fuera de los dptos. foco', fe, s, 'T_rural_no_foco', tipo='exploratoria')
correr('E1b Pendiente en los dptos. foco', fe, s, 'T_rural_en_foco', tipo='exploratoria')
pt = s.censo_pob_total.clip(lower=100) * 1000
s['T_todas'] = np.log1p((s.gs_rural_2012_2020 + s.gs_urbana_municipal_2012_2020 + s.gs_sin_clasificar_municipal_2012_2020) / pt)
correr('E2 Todas las obras viales por habitante (municipal + MOPC)', f'd_nbi ~ T_todas + nbi_2012 + C(cod_dpto) + {CTRL}', s, 'T_todas',
       perm=True, tipo='exploratoria')
# Los distritos sin ninguna compra vial municipal en la DNCP probablemente no publicaban sus compras (no es inversión cero)
s['con_registro_municipal'] = (s.gs_rural_municipal_2012_2020 + s.gs_urbana_municipal_2012_2020 + s.gs_sin_clasificar_municipal_2012_2020 > 0)
correr('E3 Principal sin distritos sin registro municipal', f0, s[s.con_registro_municipal], 'T_rural', perm=True, tipo='exploratoria')
out = pd.DataFrame(res)
out.to_csv(OUT + '/resultados_inversion_vial.csv', index=False, encoding='utf-8-sig')
pr_ = out[out.tipo == 'principal'].iloc[0]
cumple = (pr_.coef < 0) and (pr_.p_wild_bootstrap < 0.05) and (pr_.p_permutacion < 0.05)
print('\nCriterio del plan (beta < 0, p wild < 0,05 y p permutación < 0,05):', 'SE CUMPLE' if cumple else 'NO se cumple')
print('Efecto de pasar del percentil 25 al 75 de T_rural:', round(pr_.coef * (s.T_rural.quantile(.75) - s.T_rural.quantile(.25)), 2), 'pp de NBI')
