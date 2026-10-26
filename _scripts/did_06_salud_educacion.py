# Análisis departamental con resultados de educación y salud (ver 20_did_salud_educacion/PLAN_DE_ANALISIS.md).
# Personas de la EPHC 2017-2025 con el departamento recuperado en did_02; tratamiento de did_01.
import os, sys, glob, itertools, numpy as np, pandas as pd, pyreadstat
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from econometria import Fit

R = '/home/user/infraestructura_caminos'
E = R + '/01_condiciones_de_vida'
OUT = R + '/20_did_salud_educacion'
MUESTRA = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '12', '13', '14']
K = ['UPM', 'NVIVI', 'NHOGA']


def carpeta(y):
    return f'{E}/EPHC_serie_2017_2021/EPHC-{y}' if y <= 2021 else f'{E}/EPHC_anual/EPHC_{y}_ANUAL'


per = []
for y in range(2017, 2026):
    f = [p for p in glob.glob(carpeta(y) + '/*.SAV') if 'REG02' in p.upper()][0]
    meta = pyreadstat.read_sav(f, metadataonly=True)[1].column_names
    mapa = {c.upper(): c for c in meta}
    cols = K + ['P02', 'P06', 'ED08', 'ED10', 'S03', 'S04', 'S05', 'S06', 'S07', 'FACTOR']
    d = pyreadstat.read_sav(f, usecols=[mapa[c] for c in cols if c in mapa])[0]
    d.columns = [c.upper() for c in d.columns]; d['anio'] = y
    per.append(d)
p = pd.concat(per, ignore_index=True).rename(columns={'UPM': 'upm', 'NVIVI': 'nvivi', 'NHOGA': 'nhoga', 'FACTOR': 'factor'})
h = pd.read_pickle(R + '/15_analisis_departamental_did/_tmp_hogares.pkl')[['anio', 'upm', 'nvivi', 'nhoga', 'cod_dpto', 'rural', 'miembros', 'anios_estudio_jefe']]
p = p.merge(h, on=['anio', 'upm', 'nvivi', 'nhoga'], how='inner')
t = pd.read_csv(R + '/15_analisis_departamental_did/tratamiento_por_departamento.csv', dtype={'cod_dpto': str})[['cod_dpto', 'departamento', 'tratado', 'departamento_foco']]
p = p[p.cod_dpto.isin(MUESTRA)].merge(t, on='cod_dpto')

# ---------------- Resultados ----------------
edad = p.P02
valido_ed = p.ED08.between(1, 19)
p['asiste_12_17'] = p.ED08.between(1, 18).astype(float).where(edad.between(12, 17) & valido_ed)
p['asiste_6_11'] = p.ED08.between(1, 18).astype(float).where(edad.between(6, 11) & valido_ed)
p['no_asiste_sin_institucion'] = p.ED10.eq(6).astype(float).where(edad.between(6, 17) & valido_ed)
enfermo = p.S03.isin([1, 2]) & p.S04.isin([1, 6])
p['consulta_profesional'] = (p.S04.eq(1) & p.S06.isin([1, 2, 4, 5])).astype(float).where(enfermo)
p['no_consulta_lejania'] = p.S05.eq(2).astype(float).where(enfermo)
p['atencion_ministerio'] = p.S07.isin([3, 4, 5, 6]).astype(float).where(enfermo & p.S04.eq(1) & p.S07.between(1, 14))
p['edad'] = edad; p['edad2'] = edad ** 2; p['mujer'] = p.P06.eq(6).astype(int)
p['despues'] = p.anio.isin([2023, 2024]).astype(int)
cols = ['anio', 'upm', 'nvivi', 'nhoga', 'cod_dpto', 'departamento', 'rural', 'factor', 'tratado', 'departamento_foco', 'despues',
        'edad', 'mujer', 'miembros', 'anios_estudio_jefe', 'asiste_12_17', 'asiste_6_11', 'no_asiste_sin_institucion',
        'consulta_profesional', 'no_consulta_lejania', 'atencion_ministerio']
p[cols].to_csv(OUT + '/base_modelo_personas.csv', index=False, encoding='utf-8-sig')
p['w'] = p.factor; p['edad2'] = p.edad ** 2

# ---------------- Estimación ----------------
CTRL_E = 'edad + mujer + miembros + anios_estudio_jefe'
CTRL_S = 'edad + edad2 + mujer + miembros + anios_estudio_jefe'
CTRL = {'asiste_12_17': CTRL_E, 'asiste_6_11': CTRL_E, 'no_asiste_sin_institucion': CTRL_E,
        'consulta_profesional': CTRL_S, 'no_consulta_lejania': CTRL_S, 'atencion_ministerio': CTRL_S}
res = []


def ri(m):
    """Aleatorización exacta: las C(13,6) asignaciones de 6 departamentos tratados (columna trat_post)."""
    dptos = sorted(m.d.cod_dpto.unique()); yw = m.y * m.sw; Xw = m.Xw.copy(); dist = []
    for comb in itertools.combinations(dptos, 6):
        tr = m.d.cod_dpto.isin(comb).values.astype(float)
        Xw[:, m.j] = tr * m.d.despues_.values * m.sw
        dist.append(np.linalg.lstsq(Xw, yw, rcond=None)[0][m.j])
    return (np.abs(dist) >= abs(m.coef()) - 1e-12).mean()


def correr(nombre, y, d, var='trat_post', post='despues', tipo='secundaria', con_ri=False, extra=''):
    d = d[d[y].notna()].copy()
    d['trat_post'] = d.tratado * d[post]; d['despues_'] = d[post]
    f = f'{y} ~ {var} + C(cod_dpto) + C(anio) + {CTRL[y]}' + extra
    m = Fit(f, d, var)
    base = d[(d[post] == 0)]
    x = dict(tipo=tipo, modelo=nombre, resultado=y, coef=m.coef(), ee=m.se[m.j], p_cluster=m.p_cluster(), p_wild=m.p_wild(),
             p_aleatorizacion=ri(m) if con_ri else np.nan, n=m.n, media_antes=np.average(base[y], weights=base.w),
             media_antes_tratados=np.average(base[base.tratado == 1][y], weights=base[base.tratado == 1].w),
             media_antes_control=np.average(base[base.tratado == 0][y], weights=base[base.tratado == 0].w))
    x['ic95_inf'] = x['coef'] - stats.t.ppf(.975, 12) * x['ee']; x['ic95_sup'] = x['coef'] + stats.t.ppf(.975, 12) * x['ee']
    res.append(x)
    print(f"{nombre:34s} {y:26s} {x['coef']*100:6.2f} pp [{x['ic95_inf']*100:.1f}; {x['ic95_sup']*100:.1f}] wild={x['p_wild']:.3f} "
          f"RI={x['p_aleatorizacion']:.3f} base={x['media_antes']*100:.1f}% n={x['n']}", flush=True)


rur = p[p.rural == 1]
pool = rur[rur.anio.isin([2017, 2018, 2023, 2024])]
PRINC = ['asiste_12_17', 'consulta_profesional']
SEC = ['asiste_6_11', 'no_asiste_sin_institucion', 'no_consulta_lejania', 'atencion_ministerio']
for y in PRINC:
    correr('Principal 2017/18 vs 2023/24', y, pool, tipo='principal', con_ri=True)
for y in SEC:
    correr('Secundario 2017/18 vs 2023/24', y, pool, con_ri=True)
for y in PRINC:
    d = rur[rur.anio.isin([2018, 2024])].assign(post=lambda x: (x.anio == 2024).astype(int))
    correr('S1a 2018 vs 2024', y, d, post='post')
    d = rur[rur.anio.isin([2017, 2024])].assign(post=lambda x: (x.anio == 2024).astype(int))
    correr('S1b 2017 vs 2024', y, d, post='post')
    # triple diferencia: rural frente a urbano del mismo departamento y año
    dd = p[p.anio.isin([2017, 2018, 2023, 2024]) & p[y].notna()].copy()
    dd['trat_post_rural'] = dd.tratado * dd.despues * dd.rural
    m = Fit(f'{y} ~ trat_post_rural + C(cod_dpto):C(anio) + C(cod_dpto):C(rural) + C(rural):C(anio) + {CTRL[y]}', dd, 'trat_post_rural')
    res.append(dict(tipo='secundaria', modelo='S2 Triple diferencia (rural vs urbano)', resultado=y, coef=m.coef(), ee=m.se[m.j],
                    p_cluster=m.p_cluster(), p_wild=m.p_wild(), n=m.n))
    print(f"{'S2 Triple diferencia':34s} {y:26s} {m.coef()*100:6.2f} pp wild={res[-1]['p_wild']:.3f}", flush=True)
    d = pool.copy(); d['trat_post_foco'] = d.tratado * d.despues * d.departamento_foco
    correr('S4 Diferencia en dptos. foco', y, d, var='trat_post_foco', extra=' + trat_post')

out = pd.DataFrame(res)
out.to_csv(OUT + '/resultados_salud_educacion.csv', index=False, encoding='utf-8-sig')
pr = out[out.tipo == 'principal']
for _, r_ in pr.iterrows():
    ok = r_.coef > 0 and r_.p_wild < 0.025 and r_.p_aleatorizacion < 0.025
    print(f'Criterio del plan para {r_.resultado}:', 'SE CUMPLE' if ok else 'NO se cumple')

# ---------------- Estudio de eventos (base 2017) ----------------
ES = []
yrs = list(range(2018, 2026))
ev = rur.copy()
for a in yrs: ev[f'tr_{a}'] = ev.tratado * (ev.anio == a)
for y in PRINC:
    d = ev[ev[y].notna()]
    f = f'{y} ~ ' + ' + '.join(f'tr_{a}' for a in yrs) + f' + C(cod_dpto) + C(anio) + {CTRL[y]}'
    for a in yrs:
        m = Fit(f, d, f'tr_{a}')
        ES.append(dict(resultado=y, anio=a, coef=m.coef(), ee=m.se[m.j], p_cluster=m.p_cluster()))
    ES.append(dict(resultado=y, anio=2017, coef=0.0, ee=0.0, p_cluster=np.nan))
pd.DataFrame(ES).sort_values(['resultado', 'anio']).to_csv(OUT + '/resultados_estudio_eventos.csv', index=False, encoding='utf-8-sig')

# Descriptivos ponderados por grupo y año (rurales)
desc = rur.groupby(['tratado', 'anio']).apply(lambda g: pd.Series({c: np.average(g[c].dropna(), weights=g.loc[g[c].notna(), 'w']) for c in PRINC + SEC}))
desc.to_csv(OUT + '/descriptivos_por_grupo_anio.csv', encoding='utf-8-sig')
print((desc[PRINC] * 100).round(1).unstack(0))
