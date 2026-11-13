# Análisis de impacto de los 11 tramos BID, paso 2: estimaciones del plan (25_impacto_tramos_bid/PLAN_DE_ANALISIS.md).
import os, sys, itertools, numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from econometria import Fit

R = '/home/user/infraestructura_caminos'; OUT = R + '/25_impacto_tramos_bid'
rng = np.random.default_rng(2611)
P = pd.read_csv(OUT + '/panel_luces_segmentos_2012_2024.csv')
Y = P.pivot(index='id', columns='anio', values='y')
info = P.drop_duplicates('id').set_index('id')
trat = info[info.tipo == 'T']
res, ES = [], []


def base(ids, g): return Y.loc[ids, [g - 3, g - 2, g - 1]].mean(axis=1)


# ---------------- A1: controles aún no habilitados ----------------
def a1(coh):
    """coh: Serie id -> cohorte (segmentos tratados). Devuelve ATT por años desde la habilitación y celdas (g,e)."""
    celdas = []
    for g, ids in coh.groupby(coh).groups.items():
        for e in range(-3, 5):
            t = g + e
            if t < 2012 or t > 2024 or g - 3 < 2012: continue
            ctrl = coh.index[coh > max(t, g - 1)] if e >= 0 else coh.index[coh > g]   # no habilitados todavía en t
            if len(ctrl) == 0: continue
            dt = (Y.loc[ids, t] - base(ids, g)).mean(); dc = (Y.loc[ctrl, t] - base(ctrl, g)).mean()
            celdas.append(dict(g=g, e=e, n=len(ids), att=dt - dc))
    c = pd.DataFrame(celdas)
    if c.empty: return c, np.nan
    post = c[c.e.between(0, 2)]
    return c, np.average(post.att, weights=post.n) if len(post) else np.nan


coh = trat.cohorte.astype(int)
c1, est1 = a1(coh)
tramos = trat.tramo.unique()
boots = []
for _ in range(999):
    tb = rng.choice(tramos, len(tramos), replace=True)
    # un tramo sorteado dos veces entra dos veces (las etiquetas repetidas se leen dos veces de la matriz Y)
    cb = pd.concat([trat[trat.tramo == tr_].cohorte.astype(int) for tr_ in tb])
    boots.append(a1(cb)[1])
boots = np.array([b for b in boots if not np.isnan(b)])
# aleatorización: se reasignan las cohortes entre tramos
coh_tramo = trat.groupby('tramo').cohorte.first().astype(int)
perm = []
for _ in range(2000):
    nuevo = dict(zip(coh_tramo.index, rng.permutation(coh_tramo.values)))
    perm.append(a1(trat.tramo.map(nuevo).astype(int))[1])
perm = np.array([p for p in perm if not np.isnan(p)])
p_ri = (np.abs(perm) >= abs(est1) - 1e-12).mean()
res.append(dict(diseno='A1', tipo='principal', modelo='Luz nocturna, controles aún no habilitados: promedio años 0 a +2', coef=est1,
                ee=boots.std(), ic95_inf=np.percentile(boots, 2.5), ic95_sup=np.percentile(boots, 97.5), p_aleatorizacion=p_ri,
                n=f'{len(trat)} segmentos de 11 tramos', nota=f'{len(boots)} bootstrap válidos; {len(perm)} permutaciones'))
ev1 = c1.groupby('e').apply(lambda d: pd.Series({'att': np.average(d.att, weights=d.n), 'cohortes': len(d), 'segmentos': d.n.sum()}))
ev1['diseno'] = 'A1'; ES.append(ev1.reset_index())
print('A1', round(est1, 4), np.percentile(boots, [2.5, 97.5]).round(4), 'RI p', round(p_ri, 3)); print(ev1.round(4))

# ---------------- A2: controles nunca tratados emparejados ----------------
ctrl_de = info[info.tipo == 'C'].groupby('pareja_de').groups


def a2(ids_t):
    filas = []
    for g in sorted(trat.loc[ids_t, 'cohorte'].astype(int).unique()):
        it = [i for i in ids_t if trat.loc[i, 'cohorte'] == g]
        ic = [c for i in it for c in ctrl_de.get(i, [])]
        for e in range(-5, 5):
            t = g + e
            if t < 2012 or t > 2024 or g - 3 < 2012: continue
            filas.append(dict(g=g, e=e, n=len(it), att=(Y.loc[it, t] - base(it, g)).mean() - (Y.loc[ic, t] - base(ic, g)).mean()))
    c = pd.DataFrame(filas)
    ev = c.groupby('e').apply(lambda d: np.average(d.att, weights=d.n))
    post = c[c.e.between(0, 2)]; p4 = c[c.e.between(0, 4)]
    pend = np.polyfit(p4.e, p4.att, 1, w=np.sqrt(p4.n))[0] if p4.e.nunique() > 1 else np.nan
    pre = c[c.e.between(-5, -2)]
    return ev, np.average(post.att, weights=post.n), pend, np.average(pre.att, weights=pre.n)


ev2, est2, pend2, pre2 = a2(list(trat.index))
B2 = []
for _ in range(999):
    tb = rng.choice(tramos, len(tramos), replace=True)
    ids = [i for tr_ in tb for i in trat.index[trat.tramo == tr_]]
    B2.append(a2(ids))
bev = pd.concat([b[0] for b in B2], axis=1)
b_est = np.array([b[1] for b in B2]); b_pend = np.array([b[2] for b in B2]); b_pre = np.array([b[3] for b in B2])
for nom, v, b in [('Luz nocturna, controles emparejados: promedio años 0 a +2', est2, b_est),
                  ('Persistencia: pendiente del efecto por año, años 0 a +4', pend2, b_pend),
                  ('Prueba de tendencias previas: promedio años -5 a -2', pre2, b_pre)]:
    res.append(dict(diseno='A2', tipo='secundaria', modelo=nom, coef=v, ee=np.nanstd(b), ic95_inf=np.nanpercentile(b, 2.5),
                    ic95_sup=np.nanpercentile(b, 97.5), n=f'{len(trat)} segmentos tratados, {int((info.tipo == "C").sum())} controles'))
    print('A2', nom, round(v, 4), np.nanpercentile(b, [2.5, 97.5]).round(4))
e2 = pd.DataFrame({'e': ev2.index, 'att': ev2.values, 'ic95_inf': bev.quantile(.025, axis=1).reindex(ev2.index).values,
                   'ic95_sup': bev.quantile(.975, axis=1).reindex(ev2.index).values, 'diseno': 'A2'})
ES.append(e2); print(e2.round(4))
# Magnitud: nivel medio de luz de los tratados antes de la habilitación (para expresar el efecto en %)
pre_lvl = np.mean([Y.loc[trat.index[trat.cohorte == g], [g - 3, g - 2, g - 1]].values.mean() for g in trat.cohorte.unique()])

# ---------------- B: departamental (EPHC rural) ----------------
T4, C7 = ['02', '05', '06', '14'], ['01', '04', '08', '09', '10', '12', '13']
p = pd.read_csv(R + '/20_did_salud_educacion/base_modelo_personas.csv', dtype={'cod_dpto': str})
p = p[(p.rural == 1) & p.cod_dpto.isin(T4 + C7) & p.anio.isin([2017, 2018, 2019, 2023, 2024, 2025])].copy()
p['w'] = p.factor; p['edad2'] = p.edad ** 2; p['despues'] = (p.anio >= 2023).astype(int)
p['trat'] = p.cod_dpto.isin(T4).astype(int); p['trat_post'] = p.trat * p.despues; p['obras_post'] = p.tratado * p.despues
CT = {'consulta_profesional': 'edad + edad2 + mujer + miembros + anios_estudio_jefe', 'asiste_12_17': 'edad + mujer + miembros + anios_estudio_jefe'}


def ri(m):
    dps = sorted(m.d.cod_dpto.unique()); yw = m.y * m.sw; Xw = m.Xw.copy(); dist = []
    for comb in itertools.combinations(dps, 4):
        Xw[:, m.j] = m.d.cod_dpto.isin(comb).values * m.d.despues.values * m.sw
        dist.append(np.linalg.lstsq(Xw, yw, rcond=None)[0][m.j])
    assert len(dist) == 330
    return (np.abs(dist) >= abs(m.coef()) - 1e-12).mean()


for y, tipo in [('consulta_profesional', 'principal'), ('asiste_12_17', 'secundaria')]:
    d = p[p[y].notna()]
    m = Fit(f'{y} ~ trat_post + obras_post + C(cod_dpto) + C(anio) + {CT[y]}', d, 'trat_post')
    q = stats.t.ppf(.975, len(m.G) - 1); b0 = d[(d.despues == 0) & (d.trat == 1)]
    res.append(dict(diseno='B', tipo=tipo, modelo=f'{y} (EPHC rural, 4 dptos. con tramos frente a 7)', coef=m.coef(), ee=m.se[m.j],
                    ic95_inf=m.coef() - q * m.se[m.j], ic95_sup=m.coef() + q * m.se[m.j], p_cluster=m.p_cluster(), p_wild=m.p_wild(),
                    p_aleatorizacion=ri(m), n=m.n, nota=f'base antes tratados {np.average(b0[y], weights=b0.w):.3f}'))
    print('B', y, res[-1]['coef'], res[-1]['p_wild'], res[-1]['p_aleatorizacion'])

r = pd.DataFrame(res); r.to_csv(OUT + '/resultados_impacto.csv', index=False, encoding='utf-8-sig')
pd.concat(ES).to_csv(OUT + '/resultados_estudio_eventos.csv', index=False, encoding='utf-8-sig')
print(r.round(4).to_string())
print('Nivel medio de luz (log) de los tratados antes de la habilitación:', round(pre_lvl, 4))
a1r = r.iloc[0]; br = r[(r.diseno == 'B') & (r.tipo == 'principal')].iloc[0]
print('Criterio A:', 'SE CUMPLE' if a1r.coef > 0 and a1r.ic95_inf > 0 and a1r.p_aleatorizacion < .025 else 'NO se cumple')
print('Criterio B:', 'SE CUMPLE' if br.coef > 0 and br.p_wild < .025 and br.p_aleatorizacion < .025 else 'NO se cumple')
