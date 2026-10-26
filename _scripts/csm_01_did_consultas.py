# Consultas registradas en el MSPyBS por departamento (región sanitaria), 2014-2024, y obras del MOPC.
# Sigue el plan fijado en 21_did_consultas_mspbs/PLAN_DE_ANALISIS.md. Tratamiento de did_01 (15_).
import os, sys, itertools, unicodedata, numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from econometria import Fit

R = '/home/user/infraestructura_caminos'
OUT = R + '/21_did_consultas_mspbs'
MUESTRA = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '12', '13', '14']
POB = (R + '/02_censo_2022/estimaciones-y-proyecciones-de-la-poblacion-distrital-2000-2035-revisión-2025/'
       'Estimaciones y proyección distritales. Revisión 2025.xlsx')


def norm(s):
    return unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().upper().strip()


# ---------------- Datos ----------------
c = pd.read_csv(R + '/09_servicios_complementarios/MSPBS_DIGIES/consultas_MSPBS_por_region_sanitaria_2014_2024.csv',
                dtype={'cod_dpto': str})
t = pd.read_csv(R + '/15_analisis_departamental_did/tratamiento_por_departamento.csv', dtype={'cod_dpto': str})
nombre_cod = {norm(n): k for k, n in zip(t.cod_dpto, t.departamento)}

x = pd.read_excel(POB, sheet_name='Poblac a mitad de año 2000-2035', header=None)
anios = list(range(2014, 2025))
filas = x[x[1].astype(str).str.startswith('Dpto.')]
pob = []
for _, f in filas.iterrows():
    k = nombre_cod.get(norm(f[1].replace('Dpto.', '')))
    if k is None:
        continue
    for a in anios:
        pob.append(dict(cod_dpto=k, anio=a, poblacion=float(f[a - 2000 + 2])))
pob = pd.DataFrame(pob)
assert pob.cod_dpto.nunique() >= 13, pob.cod_dpto.unique()

d = (c.merge(pob, on=['cod_dpto', 'anio'])
      .merge(t[['cod_dpto', 'departamento', 'tratado', 'departamento_foco', 'gs_vecinal_por_hab_rural']], on='cod_dpto'))
d = d[d.cod_dpto.isin(MUESTRA)].copy()
assert len(d) == 13 * 11, len(d)
d['consultas_por_1000'] = d.consultas / d.poblacion * 1000
d['log_consultas_por_1000'] = np.log(d.consultas_por_1000)
d['despues'] = d.anio.between(2022, 2024).astype(int)
d['periodo'] = np.select([d.anio <= 2017, d.anio >= 2022], ['antes', 'despues'], 'excluido')
d['intensidad'] = np.log1p(d.gs_vecinal_por_hab_rural / 1e5)
d['w'] = 1.0
d['tratado'] = d.tratado.astype(int)
cols = ['cod_dpto', 'departamento', 'anio', 'consultas', 'poblacion', 'consultas_por_1000', 'log_consultas_por_1000',
        'tratado', 'departamento_foco', 'gs_vecinal_por_hab_rural', 'intensidad', 'periodo', 'despues']
d[cols].sort_values(['cod_dpto', 'anio']).to_csv(OUT + '/base_modelo_consultas.csv', index=False, encoding='utf-8-sig')

Y = 'log_consultas_por_1000'
pp = d[d.periodo != 'excluido'].copy()
res = []


def ri(m, col):
    """Aleatorización exacta: las C(13,6) asignaciones de 6 departamentos tratados."""
    dptos = sorted(m.d.cod_dpto.unique()); yw = m.y * m.sw; Xw = m.Xw.copy(); dist = []
    for comb in itertools.combinations(dptos, 6):
        tr = m.d.cod_dpto.isin(comb).values.astype(float)
        Xw[:, m.j] = tr * m.d[col].values * m.sw
        dist.append(np.linalg.lstsq(Xw, yw, rcond=None)[0][m.j])
    return (np.abs(dist) >= abs(m.coef()) - 1e-12).mean(), len(dist)


def guardar(nombre, m, tipo='secundaria', p_ri=np.nan, nota=''):
    x = dict(tipo=tipo, modelo=nombre, variable=m.var, coef=m.coef(), ee=m.se[m.j], p_cluster=m.p_cluster(),
             p_wild=m.p_wild(), p_aleatorizacion=p_ri, n=m.n, nota=nota)
    q = stats.t.ppf(.975, len(m.G) - 1)
    x['ic95_inf'] = x['coef'] - q * x['ee']; x['ic95_sup'] = x['coef'] + q * x['ee']
    res.append(x)
    print(f"{nombre:45s} {x['coef']:+.3f} (ee {x['ee']:.3f}) [{x['ic95_inf']:+.3f}; {x['ic95_sup']:+.3f}] "
          f"p_cl={x['p_cluster']:.3f} wild={x['p_wild']:.3f} RI={p_ri:.3f} n={m.n}", flush=True)
    return x


# ---------------- Principal ----------------
pp['trat_post'] = pp.tratado * pp.despues
m = Fit(f'{Y} ~ trat_post + C(cod_dpto) + C(anio)', pp, 'trat_post')
p_ri, nperm = ri(m, 'despues'); assert nperm == 1716
pr = guardar('Principal 2014-17 vs 2022-24', m, tipo='principal', p_ri=p_ri)

# ---------------- Secundarias ----------------
# S2: tendencia previa lineal diferencial, 2014-2017
pre = d[d.anio <= 2017].copy(); pre['trat_tend'] = pre.tratado * (pre.anio - 2017)
guardar('S2 Tendencia previa 2014-17 (por año)', Fit(f'{Y} ~ trat_tend + C(cod_dpto) + C(anio)', pre, 'trat_tend'))

# S3: tendencias lineales propias de cada departamento (todos los años; 2018-2021 como período propio)
al = d.copy(); al['trat_post'] = al.tratado * al.despues
al['trat_transicion'] = al.tratado * (al.periodo == 'excluido')
al['t'] = al.anio - 2014
guardar('S3 Tendencias lineales por departamento',
        Fit(f'{Y} ~ trat_post + trat_transicion + C(cod_dpto) + C(cod_dpto):t + C(anio)', al, 'trat_post'),
        nota='2018-2021 con su propio coeficiente (trat_transicion)')

# S4: intensidad continua
pp['int_post'] = pp.intensidad * pp.despues
guardar('S4 Intensidad continua (log1p Gs/hab rural/1e5)', Fit(f'{Y} ~ int_post + C(cod_dpto) + C(anio)', pp, 'int_post'),
        nota='coeficiente por unidad de log(1 + Gs por hab. rural / 100.000)')

# S5: diferencia en los departamentos foco
pp['trat_post_foco'] = pp.trat_post * pp.departamento_foco
guardar('S5 Diferencia en dptos. foco', Fit(f'{Y} ~ trat_post_foco + trat_post + C(cod_dpto) + C(anio)', pp, 'trat_post_foco'))
pp['foco_post'] = pp.departamento_foco * pp.despues
guardar('S5b Dptos. foco vs resto (sin tratado)', Fit(f'{Y} ~ foco_post + C(cod_dpto) + C(anio)', pp, 'foco_post'),
        nota='exploratorio')

# E1 (exploratorio, agregado después de ver los datos): los tratados partían de niveles más altos; se controla
# la convergencia con el nivel inicial (promedio 2014-2017 del log) × después.
base = d[d.anio <= 2017].groupby('cod_dpto')[Y].mean().rename('nivel_inicial')
pp = pp.merge(base, on='cod_dpto'); pp['nivel_post'] = (pp.nivel_inicial - pp.nivel_inicial.mean()) * pp.despues
guardar('E1 Principal + nivel inicial × después', Fit(f'{Y} ~ trat_post + nivel_post + C(cod_dpto) + C(anio)', pp, 'trat_post'),
        tipo='exploratoria', nota='controla convergencia en el nivel inicial de consultas')

out = pd.DataFrame(res)
out.to_csv(OUT + '/resultados_did_consultas.csv', index=False, encoding='utf-8-sig')
ok = pr['coef'] > 0 and pr['p_wild'] < 0.05 and pr['p_aleatorizacion'] < 0.05
print('Criterio del plan:', 'SE CUMPLE' if ok else 'NO se cumple')

# ---------------- S1: estudio de eventos (base 2017) ----------------
ev = d.copy(); yrs = [a for a in anios if a != 2017]
for a in yrs: ev[f'tr_{a}'] = ev.tratado * (ev.anio == a)
f = f'{Y} ~ ' + ' + '.join(f'tr_{a}' for a in yrs) + ' + C(cod_dpto) + C(anio)'
ES = [dict(anio=2017, coef=0.0, ee=0.0, p_cluster=np.nan, p_wild=np.nan)]
for a in yrs:
    me = Fit(f, ev, f'tr_{a}')
    ES.append(dict(anio=a, coef=me.coef(), ee=me.se[me.j], p_cluster=me.p_cluster(), p_wild=me.p_wild()))
es = pd.DataFrame(ES).sort_values('anio')
es.to_csv(OUT + '/resultados_estudio_eventos.csv', index=False, encoding='utf-8-sig')
print(es.round(3).to_string(index=False))

# ---------------- Descriptivos ----------------
desc = d.groupby(['tratado', 'anio']).apply(lambda g: pd.Series({
    'consultas': g.consultas.sum(), 'poblacion': g.poblacion.sum(),
    'consultas_por_1000_agregado': g.consultas.sum() / g.poblacion.sum() * 1000,
    'media_log_consultas_por_1000': g[Y].mean()}))
desc.to_csv(OUT + '/descriptivos_por_grupo_anio.csv', encoding='utf-8-sig')
print(desc.consultas_por_1000_agregado.unstack(0).round(0))
print(d.pivot(index='departamento', columns='anio', values='consultas_por_1000').round(0).to_string())
