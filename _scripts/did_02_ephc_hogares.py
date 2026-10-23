# Paso 2 del análisis departamental: hogares de la EPHC 2017-2025 con departamento completo.
# En 2018-2021 la EPHC publica solo DPTOREP (Concepción, Canindeyú y otros quedan en "Resto"). Las UPM de 2018-2021
# son las mismas de la muestra 2017, que sí trae DPTO: el departamento se recupera por la UPM.
import glob, numpy as np, pandas as pd, pyreadstat

R = '/home/user/infraestructura_caminos'
E = R + '/01_condiciones_de_vida'
OUT = R + '/15_analisis_departamental_did'
K = ['UPM', 'NVIVI', 'NHOGA']


def carpeta(y):
    return f'{E}/EPHC_serie_2017_2021/EPHC-{y}' if y <= 2021 else f'{E}/EPHC_anual/EPHC_{y}_ANUAL'


def leer(y, patron, cols):
    f = [p for p in glob.glob(carpeta(y) + '/*.SAV') if patron in p.upper()][0]
    meta = pyreadstat.read_sav(f, metadataonly=True)[1].column_names
    mapa = {c.upper(): c for c in meta}
    usar = [mapa[c.upper()] for c in cols if c.upper() in mapa]
    d = pyreadstat.read_sav(f, usecols=usar)[0]
    d.columns = [c.upper() for c in d.columns]
    return d


hog, per = [], []
for y in range(2017, 2026):
    h = leer(y, 'REG01', K + ['DPTO', 'DPTOREP', 'AREA', 'FACTOR', 'TOTAL', 'V04', 'V06', 'V10', 'V13', 'V14B', 'V23B', 'V2413', 'V2414'])
    i = leer(y, 'INGREFAM', K + ['IPCM', 'LINPOBTO', 'LINPOBEX', 'POBREZAI', 'TOTPERS'])
    p = leer(y, 'REG02', K + ['P02', 'P03', 'P06', 'ED08', 'S03', 'S04', 'S05', 'AÑOEST', 'FACTOR'])
    h = h.merge(i, on=K, how='left'); h['anio'] = y
    p['anio'] = y
    hog.append(h); per.append(p)
hog = pd.concat(hog, ignore_index=True); per = pd.concat(per, ignore_index=True)

# ---------------- Departamento completo ----------------
mapa = hog[hog.anio == 2017].drop_duplicates('UPM').set_index('UPM').DPTO
hog['dpto_fuente'] = np.where(hog.DPTO.notna(), 'DPTO publicado', '')
for y in range(2018, 2022):
    m = hog.anio.eq(y)
    rec = hog.loc[m, 'UPM'].map(mapa)
    # si DPTOREP identifica al departamento (no es "Resto" = 20) se usa directamente
    directo = hog.loc[m, 'DPTOREP'].where(hog.loc[m, 'DPTOREP'] != 20)
    hog.loc[m, 'DPTO'] = directo.fillna(rec)
    hog.loc[m, 'dpto_fuente'] = np.where(directo.notna(), 'DPTOREP', np.where(rec.notna(), 'UPM de la muestra 2017', 'sin dato'))
    # chequeo de coherencia: la UPM recuperada debe caer en el mismo DPTOREP
    ok = (rec[directo.notna()] == directo[directo.notna()]).mean()
    print(y, 'coherencia UPM 2017 vs DPTOREP:', round(ok, 4), '| hogares sin departamento:', int(hog.loc[m, 'DPTO'].isna().sum()))
    mapa = pd.concat([mapa, hog.loc[m & hog.DPTO.notna()].drop_duplicates('UPM').set_index('UPM').DPTO]).groupby(level=0).first()
hog = hog[hog.DPTO.notna()].copy()
hog['cod_dpto'] = hog.DPTO.astype(int).map('{:02d}'.format)
hog['rural'] = (hog.AREA == 6).astype(int)

# ---------------- Resultados del hogar ----------------
hog['pobre'] = hog.POBREZAI.isin([1, 2]).astype(float).where(hog.POBREZAI.notna())
hog['pobre_extremo'] = hog.POBREZAI.eq(1).astype(float).where(hog.POBREZAI.notna())
hog['log_ingreso_linea'] = np.log((hog.IPCM / hog.LINPOBTO).clip(lower=0.05))  # ingreso per cápita en múltiplos de la línea de pobreza
# códigos de "no responde" pasan a faltante
for c, nr in [('V04', 99), ('V06', 99), ('V13', 9), ('V14B', 9), ('V23B', 9)]:
    hog.loc[hog[c] == nr, c] = np.nan
priv = pd.DataFrame({
    'priv_piso_tierra': hog.V04.eq(1),
    'priv_agua_sin_red': ~hog.V06.isin([1, 2, 3, 4]),
    'priv_saneamiento': ~hog.V13.isin([1, 2]),
    'priv_lena_carbon': hog.V14B.isin([1, 3]),
    'priv_sin_internet': hog.V23B.eq(6),
    'priv_sin_vehiculo': hog.V2413.eq(6) & hog.V2414.eq(6),
}).astype(float)
for c, v in [('priv_piso_tierra', 'V04'), ('priv_agua_sin_red', 'V06'), ('priv_saneamiento', 'V13'), ('priv_lena_carbon', 'V14B'), ('priv_sin_internet', 'V23B')]:
    priv.loc[hog[v].isna(), c] = np.nan
priv.loc[hog.V2413.isna() | hog.V2414.isna(), 'priv_sin_vehiculo'] = np.nan
hog = pd.concat([hog, priv], axis=1)
hog['indice_privaciones'] = priv.mean(axis=1)  # 0 = ninguna privación, 1 = todas

# ---------------- Personas: acceso a escuela y salud; jefe de hogar ----------------
per = per.merge(hog[K + ['anio', 'cod_dpto', 'rural']], on=K + ['anio'], how='inner')
# ED08: 1-18 = asiste (según nivel), 19 = no asiste
per['asiste_escuela_6_17'] = per.ED08.between(1, 18).astype(float).where(per.P02.between(6, 17) & per.ED08.between(1, 19))
enfermo = per.S03.isin([1, 2])
per['consulto_si_enfermo'] = per.S04.eq(1).astype(float).where(enfermo & per.S04.isin([1, 6]))
per['no_consulto_lejania'] = per.S05.eq(2).astype(float).where(enfermo & per.S04.isin([1, 6]))
jefe = per[per.P03 == 1].drop_duplicates(K + ['anio'])[K + ['anio', 'P02', 'P06', 'AÑOEST']] \
    .rename(columns={'P02': 'edad_jefe', 'P06': 'sexo_jefe', 'AÑOEST': 'anios_estudio_jefe'})
jefe['jefa_mujer'] = jefe.sexo_jefe.eq(6).astype(int)
jefe.loc[jefe.anios_estudio_jefe > 30, 'anios_estudio_jefe'] = np.nan
acc = per.groupby(K + ['anio'])[['asiste_escuela_6_17', 'consulto_si_enfermo', 'no_consulto_lejania']].mean()
hog = hog.merge(jefe.drop(columns='sexo_jefe'), on=K + ['anio'], how='left').merge(acc, on=K + ['anio'], how='left')

hog = hog.rename(columns={'UPM': 'upm', 'NVIVI': 'nvivi', 'NHOGA': 'nhoga', 'FACTOR': 'factor', 'TOTAL': 'miembros'})
cols = ['anio', 'upm', 'nvivi', 'nhoga', 'cod_dpto', 'dpto_fuente', 'rural', 'factor', 'miembros', 'pobre', 'pobre_extremo',
        'log_ingreso_linea', 'indice_privaciones'] + list(priv.columns) + \
       ['asiste_escuela_6_17', 'consulto_si_enfermo', 'no_consulto_lejania', 'edad_jefe', 'jefa_mujer', 'anios_estudio_jefe']
hog[cols].to_pickle(OUT + '/_tmp_hogares.pkl')
print(hog.groupby(['anio', 'rural']).size().unstack())
print(hog.groupby('dpto_fuente').size())
