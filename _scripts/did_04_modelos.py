# Paso 4 del análisis departamental: base del modelo y estimaciones (diferencias en diferencias, triple diferencia,
# intensidad continua y estudio de eventos) del efecto de las obras del MOPC en la población rural.
# Requiere haber corrido did_01 a did_03.
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import econometria
from econometria import Fit

R = '/home/user/infraestructura_caminos'
OUT = R + '/15_analisis_departamental_did'
MUESTRA = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '12', '13', '14']  # Región Oriental sin Asunción ni Central
FOCO = ['01', '02', '05', '06', '14']

# ---------------- 1. Base del modelo ----------------
t = pd.read_csv(OUT + '/tratamiento_por_departamento.csv', dtype={'cod_dpto': str})
t['intensidad'] = t.gs_vecinal_por_hab_rural / 1e6  # millones de Gs por habitante rural, obras adjudicadas 2018-2023
t = t[['cod_dpto', 'departamento', 'departamento_foco', 'tratado', 'intensidad']]
cl = pd.read_csv(OUT + '/_tmp_luces_lluvia_dpto_area.csv', dtype={'cod_dpto': str})
cl['lluvia100'] = cl.lluvia_mm / 100
# exposición habitual a lluvias intensas: promedio 2013-2024 de días >= 50 mm en el área rural del departamento
hab = cl[cl.rural == 1].groupby('cod_dpto').dias_lluvia_50mm.mean().rename('dias50_habitual')
t = t.merge(hab, on='cod_dpto', how='left')

h = pd.read_pickle(OUT + '/_tmp_hogares.pkl')
h = h[h.cod_dpto.isin(MUESTRA)].merge(t, on='cod_dpto', how='left') \
     .merge(cl[['cod_dpto', 'rural', 'anio', 'lluvia100', 'dias_lluvia_50mm']], on=['cod_dpto', 'rural', 'anio'], how='left')
h['post'] = (h.anio >= 2023).astype(int)
h['w'] = h.factor
h.drop(columns='w').to_csv(OUT + '/base_modelo_hogares.csv', index=False, encoding='utf-8-sig')

p = cl[cl.cod_dpto.isin(MUESTRA)].merge(t, on='cod_dpto', how='left')
mopc = pd.read_csv(OUT + '/obras_MOPC_por_departamento_anio.csv', dtype={'cod_dpto': str})
mopc = mopc.sort_values('anio')
mopc['gs_vecinal_acum_por_hab_rural'] = mopc.groupby('cod_dpto').gs_camino_vecinal.cumsum() / mopc.pob_rural_2022
# exposición acumulada al año anterior (las obras adjudicadas tardan en ejecutarse)
mopc['intensidad_acum_t1'] = mopc.groupby('cod_dpto').gs_vecinal_acum_por_hab_rural.shift(1).fillna(0) / 1e6
p = p.merge(mopc[['cod_dpto', 'anio', 'gs_camino_vecinal', 'intensidad_acum_t1']], on=['cod_dpto', 'anio'], how='left')
p[['gs_camino_vecinal', 'intensidad_acum_t1']] = p[['gs_camino_vecinal', 'intensidad_acum_t1']].fillna(0)
p['post'] = (p.anio >= 2019).astype(int)
p['w'] = 1.0
p.drop(columns=['luz_media', 'w']).to_csv(OUT + '/base_modelo_dpto_area_anio.csv', index=False, encoding='utf-8-sig')


# ---------------- 2. Estimador: ver econometria.py ----------------
res = []


def correr(nombre, resultado, formula, d, var, muestra, wild=True, extra=None):
    m = Fit(formula, d, var)
    r = dict(modelo=nombre, resultado=resultado, variable=var, muestra=muestra, coef=m.coef(), ee_cluster=m.se[m.j],
             p_cluster=m.p_cluster(), p_wild_bootstrap=m.p_wild() if wild else np.nan, n=m.n, n_dptos=len(m.G),
             media_base=np.average(m.d.loc[m.d.anio.isin([2017, 2018]) if 'anio' in m.d else m.d.index, resultado],
                                   weights=m.d.loc[m.d.anio.isin([2017, 2018]) if 'anio' in m.d else m.d.index, 'w']))
    if extra: r.update(extra)
    res.append(r)
    print(f"{nombre:28s} {resultado:22s} {var:30s} {r['coef']:8.4f} p={r['p_cluster']:.3f} wild={r['p_wild_bootstrap']:.3f} n={r['n']}", flush=True)
    return m


Y_MAIN = ['pobre', 'pobre_extremo', 'log_ingreso_linea', 'indice_privaciones']
Y_ACC = ['asiste_escuela_6_17', 'consulto_si_enfermo', 'no_consulto_lejania']
Y_PRIV = ['priv_piso_tierra', 'priv_agua_sin_red', 'priv_saneamiento', 'priv_lena_carbon', 'priv_sin_internet', 'priv_sin_vehiculo']
CTRL = 'miembros + edad_jefe + jefa_mujer + anios_estudio_jefe + lluvia100 + dias_lluvia_50mm'

h['trat_post'] = h.tratado * h.post
h['int_post'] = h.intensidad * h.post
h['trat_post_rural'] = h.trat_post * h.rural
h['int_post_rural'] = h.int_post * h.rural
h['trat_post_foco'] = h.trat_post * h.departamento_foco
h['d50c'] = h.dias50_habitual - h.drop_duplicates('cod_dpto').dias50_habitual.mean()
h['trat_post_d50'] = h.trat_post * h.d50c

base = h[h.anio.isin([2018, 2024])]
rur = base[base.rural == 1]

# M1: diferencias en diferencias, hogares rurales, 2018 vs 2024
for y in Y_MAIN + Y_ACC:
    correr('M1 DiD rural 2018-2024', y, f'{y} ~ trat_post + C(cod_dpto) + C(anio) + {CTRL}', rur, 'trat_post', 'rural, 13 dptos')
# M2: triple diferencia (rural frente a urbano del mismo departamento y año)
for y in Y_MAIN:
    correr('M2 Triple diferencia', y, f'{y} ~ trat_post_rural + C(cod_dpto):C(anio) + C(cod_dpto):C(rural) + C(rural):C(anio) + {CTRL}',
           base, 'trat_post_rural', 'rural y urbano, 13 dptos')
# M3: intensidad continua (millones de Gs por habitante rural)
for y in Y_MAIN:
    correr('M3 Intensidad continua', y, f'{y} ~ int_post + C(cod_dpto) + C(anio) + {CTRL}', rur, 'int_post', 'rural, 13 dptos')
# M4: antes y después agrupados (2017-2018 frente a 2023-2024)
pool = h[h.anio.isin([2017, 2018, 2023, 2024]) & (h.rural == 1)]
for y in Y_MAIN:
    correr('M4 DiD 2017/18 vs 2023/24', y, f'{y} ~ trat_post + C(cod_dpto) + C(anio) + {CTRL}', pool, 'trat_post', 'rural, 13 dptos')
# M5: ¿el efecto es distinto en los cinco departamentos foco?
for y in Y_MAIN:
    correr('M5 Heterogeneidad foco', y, f'{y} ~ trat_post + trat_post_foco + C(cod_dpto) + C(anio) + {CTRL}', rur, 'trat_post_foco', 'rural, 13 dptos')
# M6: solo los cinco departamentos foco (San Pedro, Caazapá y Canindeyú tratados; Concepción y Caaguazú control)
foco = rur[rur.departamento_foco == 1]
for y in Y_MAIN:
    correr('M6 Solo departamentos foco', y, f'{y} ~ trat_post + C(cod_dpto) + C(anio) + {CTRL}', foco, 'trat_post', 'rural, 5 dptos foco')
# M7: ¿el efecto es mayor donde llueve fuerte más seguido?
for y in Y_MAIN:
    correr('M7 Heterogeneidad lluvia', y, f'{y} ~ trat_post + trat_post_d50 + C(cod_dpto) + C(anio) + {CTRL}', rur, 'trat_post_d50', 'rural, 13 dptos')
# Robustez de M7
h['int_post_d50'] = h.int_post * h.d50c
llh = h[h.rural == 1].groupby('cod_dpto').apply(lambda g: g.lluvia100.mean()).rename('lluvia_hab')  # lluvia anual media en los años de la encuesta
h['llc'] = h.cod_dpto.map(llh - llh.mean())
h['trat_post_llc'] = h.trat_post * h.llc
rur = h[h.anio.isin([2018, 2024]) & (h.rural == 1)]
urb = h[h.anio.isin([2018, 2024]) & (h.rural == 0)]
pl = h[h.anio.isin([2017, 2018]) & (h.rural == 1)].copy()
pl['trat_fic'] = pl.tratado * (pl.anio == 2018); pl['trat_fic_d50'] = pl.trat_fic * pl.d50c
pool = h[h.anio.isin([2017, 2018, 2023, 2024]) & (h.rural == 1)]
for y in ['pobre', 'log_ingreso_linea']:
    correr('M7b Intensidad x lluvia', y, f'{y} ~ int_post + int_post_d50 + C(cod_dpto) + C(anio) + {CTRL}', rur, 'int_post_d50', 'rural, 13 dptos')
    correr('M7c Placebo 2017 vs 2018', y, f'{y} ~ trat_fic + trat_fic_d50 + C(cod_dpto) + C(anio) + {CTRL}', pl, 'trat_fic_d50', 'rural, 13 dptos')
    correr('M7d Hogares urbanos', y, f'{y} ~ trat_post + trat_post_d50 + C(cod_dpto) + C(anio) + {CTRL}', urb, 'trat_post_d50', 'urbano, 13 dptos')
    correr('M7e 2017/18 vs 2023/24', y, f'{y} ~ trat_post + trat_post_d50 + C(cod_dpto) + C(anio) + {CTRL}', pool, 'trat_post_d50', 'rural, 13 dptos')
    correr('M7f Lluvia anual media', y, f'{y} ~ trat_post + trat_post_llc + C(cod_dpto) + C(anio) + {CTRL}', rur, 'trat_post_llc', 'rural, 13 dptos')
# Línea de base 2017 (muestra completa de la EPHC, 9.570 hogares) en lugar de 2018 (4.999 hogares)
b17 = h[h.anio.isin([2017, 2024]) & (h.rural == 1)]
for y in Y_MAIN:
    correr('M8 DiD rural 2017-2024', y, f'{y} ~ trat_post + C(cod_dpto) + C(anio) + {CTRL}', b17, 'trat_post', 'rural, 13 dptos')
for y in ['pobre', 'log_ingreso_linea']:
    correr('M7g Lluvia, base 2017', y, f'{y} ~ trat_post + trat_post_d50 + C(cod_dpto) + C(anio) + {CTRL}', b17, 'trat_post_d50', 'rural, 13 dptos')
# M7 sacando un departamento por vez
loo = []
for d in MUESTRA:
    s_ = rur[rur.cod_dpto != d]
    for y in ['pobre', 'log_ingreso_linea']:
        m = Fit(f'{y} ~ trat_post + trat_post_d50 + C(cod_dpto) + C(anio) + {CTRL}', s_, 'trat_post_d50')
        loo.append(dict(dpto_excluido=d, resultado=y, coef=m.coef(), ee_cluster=m.se[m.j], p_cluster=m.p_cluster()))
pd.DataFrame(loo).to_csv(OUT + '/robustez_M7_sin_un_departamento.csv', index=False, encoding='utf-8-sig')
print(pd.DataFrame(loo).groupby('resultado')[['coef', 'p_cluster']].agg(['min', 'max']).round(3))
# efecto de las obras según días de lluvia intensa: departamento con exposición baja (p25) y alta (p75)
m = Fit(f'pobre ~ trat_post + trat_post_d50 + C(cod_dpto) + C(anio) + {CTRL}', rur, 'trat_post_d50')
q = t[t.cod_dpto.isin(MUESTRA)].dias50_habitual
cen = h.drop_duplicates('cod_dpto').dias50_habitual.mean()
k0 = list(m.X.columns).index('trat_post')
V = None
for nombre, val in [('p25', q.quantile(.25)), ('p75', q.quantile(.75))]:
    c = np.zeros(m.X.shape[1]); c[k0] = 1; c[m.j] = val - cen
    est = c @ m.b
    s = np.array([m.Xw[i].T @ ((m.y * m.sw - m.Xw @ m.b)[i]) for i in m.idx])
    G, (n, k) = len(m.G), m.Xw.shape
    se = np.sqrt(G / (G - 1) * (n - 1) / (n - k) * ((s @ (m.XtXi @ c)) ** 2).sum())
    res.append(dict(modelo='M7 efecto según lluvia', resultado='pobre', variable=f'trat_post con días>=50mm en {nombre} ({val:.1f} días/año)',
                    muestra='rural, 13 dptos', coef=est, ee_cluster=se, n=m.n, n_dptos=G))
    print(nombre, round(val, 2), round(est, 4), round(se, 4))

# Mecanismos: componentes del índice de privaciones
rur = h[h.anio.isin([2018, 2024]) & (h.rural == 1)]
for y in Y_PRIV:
    correr('Mec. componentes', y, f'{y} ~ trat_post + C(cod_dpto) + C(anio) + {CTRL}', rur, 'trat_post', 'rural, 13 dptos')

# Estudio de eventos EPHC (rurales, 2017-2025, base 2018; sin controles de lluvia porque 2025 no tiene dato anual completo)
ev = h[h.rural == 1].copy()
yrs = [a for a in range(2017, 2026) if a != 2018]
for a in yrs: ev[f'tr_{a}'] = ev.tratado * (ev.anio == a)
ES = []
for y in ['pobre', 'indice_privaciones']:
    f = f'{y} ~ ' + ' + '.join(f'tr_{a}' for a in yrs) + ' + C(cod_dpto) + C(anio) + miembros + edad_jefe + jefa_mujer + anios_estudio_jefe'
    for a in yrs:
        m = Fit(f, ev, f'tr_{a}')
        ES.append(dict(fuente='EPHC', resultado=y, anio=a, coef=m.coef(), ee_cluster=m.se[m.j], p_cluster=m.p_cluster()))
    ES.append(dict(fuente='EPHC', resultado=y, anio=2018, coef=0.0, ee_cluster=0.0, p_cluster=np.nan))
# Estudio de eventos de la interacción tratamiento × días de lluvia intensa (M7), base 2018
for a in yrs: ev[f'trd_{a}'] = ev[f'tr_{a}'] * ev.d50c
for y in ['pobre', 'log_ingreso_linea']:
    f = f'{y} ~ ' + ' + '.join(f'tr_{a} + trd_{a}' for a in yrs) + ' + C(cod_dpto) + C(anio) + miembros + edad_jefe + jefa_mujer + anios_estudio_jefe'
    for a in yrs:
        m = Fit(f, ev, f'trd_{a}')
        ES.append(dict(fuente='EPHC interacción lluvia', resultado=y, anio=a, coef=m.coef(), ee_cluster=m.se[m.j], p_cluster=m.p_cluster()))
    ES.append(dict(fuente='EPHC interacción lluvia', resultado=y, anio=2018, coef=0.0, ee_cluster=0.0, p_cluster=np.nan))

# ---------------- 3. Luz nocturna por departamento × área ----------------
p['trat_post'] = p.tratado * p.post
p['trat_post_rural'] = p.trat_post * p.rural
pr = p[p.rural == 1]
correr('L1 DiD luz rural', 'log_luz_km2', 'log_luz_km2 ~ trat_post + C(cod_dpto) + C(anio) + lluvia100', pr, 'trat_post', 'rural, 13 dptos, 2013-2024')
correr('L2 Triple diferencia luz', 'log_luz_km2', 'log_luz_km2 ~ trat_post_rural + C(cod_dpto):C(anio) + C(cod_dpto):C(rural) + C(rural):C(anio) + lluvia100',
       p, 'trat_post_rural', 'rural y urbano, 13 dptos, 2013-2024')
correr('L3 Intensidad acumulada luz', 'log_luz_km2', 'log_luz_km2 ~ intensidad_acum_t1 + C(cod_dpto) + C(anio) + lluvia100', pr,
       'intensidad_acum_t1', 'rural, 13 dptos, 2013-2024')
pre = pr[pr.anio <= 2018].copy(); pre['tend_trat'] = pre.tratado * (pre.anio - 2018)
correr('L4 Tendencia previa luz', 'log_luz_km2', 'log_luz_km2 ~ tend_trat + C(cod_dpto) + C(anio) + lluvia100', pre, 'tend_trat', 'rural, 13 dptos, 2013-2018')
lyrs = [a for a in range(2013, 2025) if a != 2018]
for a in lyrs: pr[f'tr_{a}'] = pr.tratado * (pr.anio == a)
f = 'log_luz_km2 ~ ' + ' + '.join(f'tr_{a}' for a in lyrs) + ' + C(cod_dpto) + C(anio) + lluvia100'
for a in lyrs:
    m = Fit(f, pr, f'tr_{a}')
    ES.append(dict(fuente='VIIRS', resultado='log_luz_km2', anio=a, coef=m.coef(), ee_cluster=m.se[m.j], p_cluster=m.p_cluster()))
ES.append(dict(fuente='VIIRS', resultado='log_luz_km2', anio=2018, coef=0.0, ee_cluster=0.0, p_cluster=np.nan))

# ---------------- 4. Robustez sugerida por la revisión econométrica ----------------
from itertools import combinations
rur = h[h.anio.isin([2018, 2024]) & (h.rural == 1)].copy()
b17 = h[h.anio.isin([2017, 2024]) & (h.rural == 1)].copy()
for d_ in (rur, b17):
    d_['trat_post'] = d_.tratado * d_.post
    d_['trat_post_d50'] = d_.trat_post * d_.d50c
CTRL_LL = 'lluvia100 + dias_lluvia_50mm'


def ri(nombre, resultado, formula, d, var, cols_trat):
    """Inferencia por aleatorización exacta: las C(13,6) asignaciones posibles de 6 departamentos tratados."""
    m = Fit(formula, d, var)
    dptos = sorted(m.d.cod_dpto.unique()); k = int(m.d.drop_duplicates('cod_dpto').tratado.sum())
    names = list(m.X.columns); yw = m.y * m.sw
    dist = []
    for comb in combinations(dptos, k):
        tr = m.d.cod_dpto.isin(comb).astype(float).values
        Xw = m.Xw.copy()
        for c, f in cols_trat.items(): Xw[:, names.index(c)] = f(tr, m.d) * m.sw
        dist.append(np.linalg.lstsq(Xw, yw, rcond=None)[0][m.j])
    dist = np.array(dist)
    p = (np.abs(dist) >= abs(m.coef()) - 1e-12).mean()
    res.append(dict(modelo=nombre, resultado=resultado, variable=var, muestra=f'aleatorización exacta ({len(dist)} asignaciones)',
                    coef=m.coef(), ee_cluster=m.se[m.j], p_cluster=m.p_cluster(), p_aleatorizacion=p, n=m.n, n_dptos=len(m.G)))
    print(f'{nombre:28s} {resultado:20s} coef={m.coef():.4f} p_RI={p:.3f}', flush=True)


tp = {'trat_post': lambda tr, d: tr * d.post.values}
tpd = {'trat_post': lambda tr, d: tr * d.post.values, 'trat_post_d50': lambda tr, d: tr * d.post.values * d.d50c.values}
ri('RI M1 DiD 2018-2024', 'pobre', f'pobre ~ trat_post + C(cod_dpto) + C(anio) + {CTRL}', rur, 'trat_post', tp)
ri('RI M8 DiD 2017-2024', 'pobre', f'pobre ~ trat_post + C(cod_dpto) + C(anio) + {CTRL}', b17, 'trat_post', tp)
ri('RI M4 2017/18 vs 2023/24', 'pobre', f'pobre ~ trat_post + C(cod_dpto) + C(anio) + {CTRL}', pool.assign(trat_post=pool.tratado * pool.post), 'trat_post', tp)
ri('RI M7 lluvia base 2018', 'pobre', f'pobre ~ trat_post + trat_post_d50 + C(cod_dpto) + C(anio) + {CTRL}', rur, 'trat_post_d50', tpd)
ri('RI M7g lluvia base 2017', 'pobre', f'pobre ~ trat_post + trat_post_d50 + C(cod_dpto) + C(anio) + {CTRL}', b17, 'trat_post_d50', tpd)

# Definiciones alternativas del tratamiento (pobreza, base 2018 y base 2017)
o = pd.read_csv(OUT + '/obras_viales_MOPC_2018_2025_clasificadas.csv', dtype={'cod_dpto_asignados': str})
o = o[o.camino_vecinal & o.anio.le(2023) & o.cod_dpto_asignados.notna()].copy()
txt = (o.titulo_llamado.fillna('') + ' ' + o.lotes_adjudicados.fillna('')).str.lower()
o = o[~txt.str.contains('asfalt|alfalt|paviment')]  # sin pavimentación asfáltica
o['d'] = o.cod_dpto_asignados.str.split(';'); o = o.explode('d'); o['m'] = o.monto_adjudicado_gs / o.n_deptos
pobr = pd.read_csv(OUT + '/tratamiento_por_departamento.csv', dtype={'cod_dpto': str}).set_index('cod_dpto').pob_rural_2022
sin_asf = (o.groupby('d').m.sum().reindex(MUESTRA).fillna(0) / pobr.reindex(MUESTRA))
ints = t.set_index('cod_dpto').intensidad.reindex(MUESTRA)
ALT = {
    'Concepción como tratada (>= mediana)': (ints >= ints.median()).astype(int),
    'Sin pavimentación asfáltica (> mediana)': (sin_asf > sin_asf.median()).astype(int),
    'Tercil alto frente a tercil bajo': pd.Series(np.where(ints >= ints.quantile(2 / 3), 1, np.where(ints <= ints.quantile(1 / 3), 0, np.nan)), index=MUESTRA),
}
for base_n, dd in [('2018', rur), ('2017', b17)]:
    for nom, tr in ALT.items():
        x = dd.assign(tr_alt=dd.cod_dpto.map(tr)).dropna(subset=['tr_alt'])
        x['trat_post'] = x.tr_alt * x.post
        correr(f'R base {base_n}: {nom}', 'pobre', f'pobre ~ trat_post + C(cod_dpto) + C(anio) + {CTRL}', x, 'trat_post', 'rural')
    x = dd[dd.cod_dpto != '12']
    correr(f'R base {base_n}: sin Ñeembucú', 'pobre', f'pobre ~ trat_post + C(cod_dpto) + C(anio) + {CTRL}', x, 'trat_post', 'rural, 12 dptos')
    x = dd.assign(lint_post=np.log1p(dd.intensidad * 10) * dd.post)
    correr(f'R base {base_n}: log intensidad', 'pobre', f'pobre ~ lint_post + C(cod_dpto) + C(anio) + {CTRL}', x, 'lint_post', 'rural')
    correr(f'R base {base_n}: sin controles del hogar', 'pobre', f'pobre ~ trat_post + C(cod_dpto) + C(anio) + {CTRL_LL}', dd, 'trat_post', 'rural')

# Estudio de eventos de pobreza con base 2017 (muestra completa)
yrs17 = [a for a in range(2018, 2026)]
for a in yrs17: ev[f'tr_{a}'] = ev.tratado * (ev.anio == a)
f = 'pobre ~ ' + ' + '.join(f'tr_{a}' for a in yrs17) + ' + C(cod_dpto) + C(anio) + miembros + edad_jefe + jefa_mujer + anios_estudio_jefe'
for a in yrs17:
    m = Fit(f, ev, f'tr_{a}')
    ES.append(dict(fuente='EPHC base 2017', resultado='pobre', anio=a, coef=m.coef(), ee_cluster=m.se[m.j], p_cluster=m.p_cluster()))
ES.append(dict(fuente='EPHC base 2017', resultado='pobre', anio=2017, coef=0.0, ee_cluster=0.0, p_cluster=np.nan))

out = pd.DataFrame(res)
# efecto mínimo detectable con 80 % de potencia y 5 % de significación (aprox. 2,8 errores estándar)
out['efecto_minimo_detectable'] = 2.8 * out.ee_cluster
out.to_csv(OUT + '/resultados_did.csv', index=False, encoding='utf-8-sig')
pd.DataFrame(ES).sort_values(['fuente', 'resultado', 'anio']).to_csv(OUT + '/resultados_estudio_eventos.csv', index=False, encoding='utf-8-sig')

# Descriptivos: medias ponderadas antes/después por grupo (rurales)
def wm(g, c): return np.average(g[c].dropna(), weights=g.loc[g[c].notna(), 'w']) if g[c].notna().any() else np.nan
desc = []
for (tr, a), g in h[(h.rural == 1) & h.anio.isin([2018, 2024])].groupby(['tratado', 'anio']):
    desc.append(dict(grupo='tratamiento' if tr == 1 else 'control', anio=a, hogares=len(g), **{c: wm(g, c) for c in Y_MAIN + Y_ACC}))
pd.DataFrame(desc).to_csv(OUT + '/descriptivos_antes_despues.csv', index=False, encoding='utf-8-sig')
print(pd.DataFrame(desc).round(3).to_string())
