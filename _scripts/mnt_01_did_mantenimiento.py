# Diferencias en diferencias del mantenimiento de caminos vecinales (ver 23_did_mantenimiento/PLAN_DE_ANALISIS.md).
# A: distrital, cambio del NBI 2012-2022 en distritos con obra temprana, con y sin contratos municipales de mantenimiento.
# B: departamental, contrato MOPC LPI 47/2021 (8 dptos.) frente a 5 dptos., EPHC rural y consultas del MSPyBS.
import os, sys, itertools, unicodedata, numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from econometria import Fit

R = '/home/user/infraestructura_caminos'
OUT = R + '/23_did_mantenimiento'
rng = np.random.default_rng(2026)
res = []


def norm(s): return unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()


def guardar(diseno, nombre, m, tipo='secundaria', p_perm=np.nan, nota=''):
    q = stats.t.ppf(.975, len(m.G) - 1)
    x = dict(diseno=diseno, tipo=tipo, modelo=nombre, variable=m.var, coef=m.coef(), ee=m.se[m.j],
             ic95_inf=m.coef() - q * m.se[m.j], ic95_sup=m.coef() + q * m.se[m.j], p_cluster=m.p_cluster(),
             p_wild=m.p_wild(), p_aleatorizacion=p_perm, n=m.n, grupos=len(m.G), nota=nota)
    res.append(x)
    print(f"{diseno} {nombre:52s} {x['coef']:+.3f} [{x['ic95_inf']:+.3f}; {x['ic95_sup']:+.3f}] wild={x['p_wild']:.3f} "
          f"perm={p_perm:.3f} n={m.n}", flush=True)
    return x


def perm_dentro(m, col, reps=2000):
    """Permuta el tratamiento dentro de cada departamento (columna del modelo m.var = col)."""
    yw = m.y * m.sw; Xw = m.Xw.copy(); t = m.d[col].values.astype(float); g = m.d.cod_dpto.values
    idx = [np.where(g == gg)[0] for gg in np.unique(g)]; dist = []
    for _ in range(reps):
        tp = t.copy()
        for i in idx: tp[i] = rng.permutation(t[i])
        Xw[:, m.j] = tp * m.sw
        dist.append(np.linalg.lstsq(Xw, yw, rcond=None)[0][m.j])
    return (np.abs(dist) >= abs(m.coef()) - 1e-12).mean()


# ======================= A. Diseño distrital =======================
a = pd.read_csv(R + '/08_contrataciones_DNCP/DNCP_obras_viales_todas_entidades_2012_2025.csv', dtype=str)
t = a.titulo_llamado.fillna('').map(norm) + ' ' + a.lotes_adjudicados.fillna('').map(norm)
es_mant = (t.str.contains(r'manten|conservacion|perfilado|bacheo|cuneta|reparacion de camino|enripiado|ripiado')
           & t.str.contains(r'vecinal|camino|rural|compania|tierra|terraplen|ripio') & a.comprador.str.contains('Municipalidad'))
mun = pd.read_csv(R + '/17_inversion_vial_todas_entidades/tabla_municipalidades_distritos.csv', dtype=str)
c = a[es_mant].merge(mun[['comprador_id', 'cod_dist']], on='comprador_id', how='left')
c['anio'] = c.anio_adjudicacion.astype(int); c['monto'] = pd.to_numeric(c.monto_adjudicado_gs, errors='coerce')
assert c.cod_dist.notna().all()
c[['ocid', 'anio', 'comprador', 'cod_dist', 'monto', 'titulo_llamado']].to_csv(OUT + '/contratos_mantenimiento_municipal_2012_2025.csv', index=False, encoding='utf-8-sig')
g = c.groupby('cod_dist').agg(primer_anio_mant=('anio', 'min'),
                              n_anios_mant_2012_2020=('anio', lambda x: x[x <= 2020].nunique()),
                              gs_mant_2012_2020=('monto', lambda x: x[c.loc[x.index, 'anio'] <= 2020].sum()))

b = pd.read_csv(R + '/16_analisis_censal_nbi_2012_2022/base_modelo_distrital_nbi.csv', dtype={'cod_dist': str, 'cod_dpto': str})
roy = pd.read_csv(R + '/10_economia_y_mercados/MEF_royalties_municipios/royalties_municipios_2025.csv', dtype={'cod_dist': str})
b = b.merge(g, on='cod_dist', how='left').merge(roy[['cod_dist', 'royalties_liquidado_2025_gs']], on='cod_dist', how='left')
b['n_anios_mant_2012_2020'] = b.n_anios_mant_2012_2020.fillna(0)
b['mantenimiento'] = b.primer_anio_mant.le(2020).astype(int)
b['mant_futuro_2022_2024'] = b.primer_anio_mant.between(2022, 2024).astype(int)
b['nunca_mant'] = b.primer_anio_mant.isna().astype(int)
b['log_gs_obra'] = np.log1p(b.gs_2012_2020 / 1e6)
b['royalties_por_hab'] = b.royalties_liquidado_2025_gs / b.censo_pob_total / 1e3   # miles de Gs por habitante
b['w'] = 1.0
s = b[b.muestra == 1].copy()
s.to_csv(OUT + '/base_modelo_distrital_mantenimiento.csv', index=False, encoding='utf-8-sig',
         columns=['cod_dpto', 'departamento', 'cod_dist', 'distrito', 'departamento_foco', 'nbi_2012', 'nbi_2022', 'd_nbi',
                  'obra', 'obra_temprana', 'gs_2012_2020', 'log_gs_obra', 'mantenimiento', 'primer_anio_mant',
                  'n_anios_mant_2012_2020', 'gs_mant_2012_2020', 'mant_futuro_2022_2024', 'censo_pob_total', 'censo_pct_rural',
                  'log_densidad_pob', 'royalties_por_hab', 'lluvia_media_2013_2022'])
X = 'nbi_2012 + censo_pct_rural + log_densidad_pob + log_gs_obra + royalties_por_hab + lluvia_media_2013_2022'
o = s[s.obra_temprana == 1].copy()
print('Diseño A: distritos con obra temprana', len(o), '| tratados', o.mantenimiento.sum(), '| control', (o.mantenimiento == 0).sum())
desc = o.groupby('mantenimiento').agg(distritos=('cod_dist', 'size'), nbi_2012=('nbi_2012', 'mean'), nbi_2022=('nbi_2022', 'mean'),
                                       d_nbi=('d_nbi', 'mean'), pct_rural=('censo_pct_rural', 'mean'),
                                       royalties_por_hab=('royalties_por_hab', 'mean'), gs_obra_mm=('gs_2012_2020', lambda x: x.mean() / 1e9))
desc.to_csv(OUT + '/descriptivos_distritales.csv', encoding='utf-8-sig'); print(desc.round(2))

m = Fit(f'd_nbi ~ mantenimiento + C(cod_dpto) + {X}', o, 'mantenimiento')
pr = guardar('A', 'Principal: cambio NBI 2012-2022, obra temprana', m, 'principal', perm_dentro(m, 'mantenimiento'))
m = Fit('d_nbi ~ mantenimiento', o, 'mantenimiento')
guardar('A', 'S1 Diferencia simple 2x2', m, p_perm=perm_dentro(m, 'mantenimiento'))
s['obra_x_mant'] = s.obra_temprana * s.mantenimiento
m = Fit(f'd_nbi ~ obra_x_mant + obra_temprana + mantenimiento + C(cod_dpto) + {X}', s, 'obra_x_mant')
guardar('A', 'S2 Triple diferencia (obra x mantenimiento), 203 distritos', m)
m = Fit(f'd_nbi ~ n_anios_mant_2012_2020 + C(cod_dpto) + {X}', o, 'n_anios_mant_2012_2020')
guardar('A', 'S3 Intensidad: años con contrato 2012-2020', m, nota='por año con contrato')
pl = s[(s.mantenimiento == 0)].copy()
m = Fit(f'd_nbi ~ mant_futuro_2022_2024 + obra_temprana + C(cod_dpto) + {X}', pl, 'mant_futuro_2022_2024')
guardar('A', 'S4 Placebo: primer contrato 2022-2024 vs nunca', m, p_perm=perm_dentro(m, 'mant_futuro_2022_2024'),
        nota=f'{int(pl.mant_futuro_2022_2024.sum())} tratados placebo; muestra completa sin tratados 2012-2020')

# S5 luz nocturna, estimador escalonado (como cen_03)
l = pd.read_csv(R + '/07_clima_y_contexto/luces_nocturnas_VIIRS/luces_nocturnas_por_distrito_2012_2024.csv', dtype={'cod_dist': str})
l = l.merge(s[['cod_dist', 'cod_dpto', 'log_area_km2']], on='cod_dist')
l['y'] = np.log1p(l.luz_suma / np.exp(l.log_area_km2) * 100)
Y = l.pivot(index='cod_dist', columns='anio', values='y')
dpto = s.set_index('cod_dist').cod_dpto
trat = s[s.primer_anio_mant.between(2015, 2020)].set_index('cod_dist').primer_anio_mant.astype(int)
ctrl = s[s.nunca_mant == 1].cod_dist.values
E = range(-3, 4)


def att(coh, ctrl):
    out = {}
    for e in E:
        num = den = 0
        for gg, ids in coh.groupby(coh).groups.items():
            base = [gg - 3, gg - 2, gg - 1]
            dt = (Y.loc[ids, gg + e] - Y.loc[ids, base].mean(axis=1)).mean()
            dc = (Y.loc[ctrl, gg + e] - Y.loc[ctrl, base].mean(axis=1)).mean()
            num += len(ids) * (dt - dc); den += len(ids)
        out[e] = num / den
    return pd.Series(out)


est = att(trat, ctrl); dps = dpto.unique(); boots = []
for _ in range(499):
    dd = rng.choice(dps, len(dps), replace=True)
    ti = [i for d_ in dd for i in trat.index[dpto.reindex(trat.index).values == d_]]
    ci = [i for d_ in dd for i in ctrl[dpto.reindex(ctrl).values == d_]]
    if ti and ci: boots.append(att(trat.loc[ti], np.array(ci)))
B = pd.concat(boots, axis=1)
ev = pd.DataFrame({'anios_desde_primer_contrato': list(E), 'coef': est.values, 'ee_bootstrap_dpto': B.std(axis=1).values})
ev.to_csv(OUT + '/resultados_luces_estudio_eventos.csv', index=False, encoding='utf-8-sig')
post = [0, 1, 2, 3]; se_post = B.loc[post].mean().std()
res.append(dict(diseno='A', tipo='secundaria', modelo='S5 Luz nocturna: promedio años 0 a +3', variable='log luz por km2',
                coef=est[post].mean(), ee=se_post, ic95_inf=np.percentile(B.loc[post].mean(), 2.5),
                ic95_sup=np.percentile(B.loc[post].mean(), 97.5), n=len(trat) + len(ctrl),
                nota=f'{len(trat)} distritos tratados (cohortes 2015-2020), {len(ctrl)} controles; previos: ' +
                     ', '.join(f'{e}: {est[e]:+.3f}' for e in [-3, -2, -1])))
print('S5 luz:', ev.round(3).to_string(index=False), f'\n  promedio 0..+3 = {est[post].mean():+.3f} (EE {se_post:.3f}); tratados {len(trat)}, controles {len(ctrl)}')

# ======================= B. Diseño departamental =======================
MANT8 = ['01', '02', '04', '06', '07', '10', '13', '14']
p = pd.read_csv(R + '/20_did_salud_educacion/base_modelo_personas.csv', dtype={'cod_dpto': str})
p = p[(p.rural == 1) & p.anio.isin([2017, 2018, 2019, 2023, 2024, 2025])].copy()
p['w'] = p.factor; p['edad2'] = p.edad ** 2
p['despues'] = (p.anio >= 2023).astype(int); p['mant'] = p.cod_dpto.isin(MANT8).astype(int)
p['trat_post'] = p.mant * p.despues; p['obras_post'] = p.tratado * p.despues
CT = {'consulta_profesional': 'edad + edad2 + mujer + miembros + anios_estudio_jefe',
      'asiste_12_17': 'edad + mujer + miembros + anios_estudio_jefe'}


def ri_exacta(m, k=8):
    dps = sorted(m.d.cod_dpto.unique()); yw = m.y * m.sw; Xw = m.Xw.copy(); dist = []
    for comb in itertools.combinations(dps, k):
        Xw[:, m.j] = m.d.cod_dpto.isin(comb).values * m.d.despues.values * m.sw
        dist.append(np.linalg.lstsq(Xw, yw, rcond=None)[0][m.j])
    assert len(dist) == 1287
    return (np.abs(dist) >= abs(m.coef()) - 1e-12).mean()


for y, tipo in [('consulta_profesional', 'principal'), ('asiste_12_17', 'secundaria')]:
    d = p[p[y].notna()]
    m = Fit(f'{y} ~ trat_post + obras_post + C(cod_dpto) + C(anio) + {CT[y]}', d, 'trat_post')
    guardar('B', f'{"Principal" if tipo == "principal" else "Secundario"}: {y} (EPHC rural)', m, tipo, ri_exacta(m),
            nota=f'base antes tratados {np.average(d[(d.despues == 0) & (d.mant == 1)][y], weights=d[(d.despues == 0) & (d.mant == 1)].w):.3f}')
k = pd.read_csv(R + '/21_did_consultas_mspbs/base_modelo_consultas.csv', dtype={'cod_dpto': str})
k = k[k.anio.between(2014, 2019) | k.anio.between(2023, 2024)].copy()
k['despues'] = (k.anio >= 2023).astype(int); k['mant'] = k.cod_dpto.isin(MANT8).astype(int)
k['trat_post'] = k.mant * k.despues; k['obras_post'] = k.tratado * k.despues; k['w'] = 1.0
m = Fit('log_consultas_por_1000 ~ trat_post + obras_post + C(cod_dpto) + C(anio)', k, 'trat_post')
guardar('B', 'Secundario: log consultas MSPyBS por 1.000', m, p_perm=ri_exacta(m))

r = pd.DataFrame(res); r.to_csv(OUT + '/resultados_did_mantenimiento.csv', index=False, encoding='utf-8-sig')
pa = r[(r.diseno == 'A') & (r.tipo == 'principal')].iloc[0]; pb = r[(r.diseno == 'B') & (r.tipo == 'principal')].iloc[0]
print('Criterio A:', 'SE CUMPLE' if pa.coef < 0 and pa.p_wild < .05 and pa.p_aleatorizacion < .05 else 'NO se cumple')
print('Criterio B:', 'SE CUMPLE' if pb.coef > 0 and pb.p_wild < .05 and pb.p_aleatorizacion < .05 else 'NO se cumple')
