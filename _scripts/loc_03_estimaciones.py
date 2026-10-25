# Paso 3 del análisis de efecto local de los tramos: estimaciones fijadas en 19_efecto_local_tramos/PLAN_DE_ANALISIS.md.
# Diferencias en diferencias escalonado tipo Callaway-Sant'Anna con controles sin obra, base = promedio de g-3..g-1,
# ventana -3..+3, efecto principal = promedio de los años 0..+3, bootstrap por departamento (499).
import numpy as np, pandas as pd, geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R = '/home/user/infraestructura_caminos'
OUT = R + '/19_efecto_local_tramos'
E = list(range(-3, 4)); POST = [0, 1, 2, 3]
u = gpd.read_file(OUT + '/unidades_tratados_y_controles.gpkg')


def estimar(Y, unidades, nombre, B=499, seed=7):
    """Y: tabla unidad x año. unidades: tabla con unidad, grupo, cohorte, dpto."""
    tr = unidades[unidades.grupo == 'tratado'].set_index('unidad')
    ct = unidades[unidades.grupo == 'control'].set_index('unidad')
    tr = tr[tr.index.isin(Y.index)]; ct = ct[ct.index.isin(Y.index)]

    def att(tr_ids, coh, ct_ids):
        out = {}
        for e in E:
            num = den = 0.0
            for g in np.unique(coh):
                ids = tr_ids[coh == g]
                base = [g - 3, g - 2, g - 1]
                if g + e not in Y.columns or not all(b in Y.columns for b in base): continue
                dt = (Y.loc[ids, g + e] - Y.loc[ids, base].mean(axis=1)).mean()
                dc = (Y.loc[ct_ids, g + e] - Y.loc[ct_ids, base].mean(axis=1)).mean()
                num += len(ids) * (dt - dc); den += len(ids)
            out[e] = num / den if den else np.nan
        return pd.Series(out)

    est = att(tr.index.values, tr.cohorte.values.astype(int), ct.index.values)
    rng = np.random.default_rng(seed); dptos = np.union1d(tr.dpto.unique(), ct.dpto.unique()); boots = []
    for _ in range(B):
        dd = rng.choice(dptos, len(dptos), replace=True)
        ti = np.concatenate([tr.index[tr.dpto == d].values for d in dd]); ci = np.concatenate([ct.index[ct.dpto == d].values for d in dd])
        if len(ti) == 0 or len(ci) == 0: continue
        boots.append(att(ti, tr.loc[ti].cohorte.values.astype(int), ci))
    Bm = pd.concat(boots, axis=1)
    prom = est[POST].mean(); bp = Bm.loc[POST].mean()
    res = dict(analisis=nombre, efecto_promedio_0a3=prom, ee=bp.std(), ic95_inf=np.percentile(bp, 2.5), ic95_sup=np.percentile(bp, 97.5),
               prom_previos_m3a_m1=est[[-3, -2, -1]].mean(), n_tratados=len(tr), n_controles=len(ct))
    es = pd.DataFrame({'analisis': nombre, 'anios_desde_obra': E, 'coef': est.values, 'ee': Bm.std(axis=1).values,
                       'ic95_inf': np.percentile(Bm, 2.5, axis=1), 'ic95_sup': np.percentile(Bm, 97.5, axis=1)})
    print(f"{nombre:55s} efecto 0..+3 = {prom:.4f} IC95 [{res['ic95_inf']:.4f}; {res['ic95_sup']:.4f}] (n trat {len(tr)}, ctrl {len(ct)})", flush=True)
    return res, es


L = pd.read_csv(OUT + '/luces_por_unidad_anio.csv')
res, ess = [], []
Y3 = L[L.franja_km == 3].pivot(index='unidad', columns='anio', values='log_luz_km2')
Y15 = L[L.franja_km == 1.5].pivot(index='unidad', columns='anio', values='log_luz_km2')
uu = pd.DataFrame(u.drop(columns='geometry'))
for nombre, Y, sub in [
        ('Principal: luz, franja 3 km, todos los tramos', Y3, uu),
        ('S1: solo tramos con trazado (línea)', Y3, uu[(uu.grupo == 'control') | (uu.tipo_geom == 'linea')]),
        ('S2: controles a 10-30 km de un tramo', Y3, uu[(uu.grupo == 'tratado') | (uu.dist_km_tramo <= 30)]),
        ('S3: franja de 1,5 km', Y15, uu)]:
    r, e = estimar(Y, sub, nombre); res.append(r); ess.append(e)

# ---------------- Exploratorios (no estaban en el plan) ----------------
# Los controles del plan son mucho más oscuros que los tramos y la luz de las zonas oscuras sube distinto (cambios del
# producto VIIRS en zonas de poca luz). Se comparan entonces tratados con controles de luz inicial parecida.
base = Y3[[2012, 2013, 2014]].mean(axis=1)
tb = base[uu[uu.grupo == 'tratado'].unidad]
rango = uu[(uu.grupo == 'tratado') | uu.unidad.map(base).between(tb.quantile(.1), tb.quantile(.9))]
r, e = estimar(Y3, rango, 'E1: controles con luz inicial en el rango de los tramos (p10-p90)'); res.append(r); ess.append(e)
# emparejamiento: para cada tramo, los 5 controles del mismo departamento con luz inicial más parecida
ct = uu[uu.grupo == 'control'].assign(b=lambda x: x.unidad.map(base))
elegidos = set()
for _, rw in uu[uu.grupo == 'tratado'].iterrows():
    cand = ct[ct.dpto == rw.dpto] if (ct.dpto == rw.dpto).sum() >= 5 else ct
    elegidos |= set(cand.assign(dif=(cand.b - base[rw.unidad]).abs()).nsmallest(5, 'dif').unidad)
emp = uu[(uu.grupo == 'tratado') | uu.unidad.isin(elegidos)]
r, e = estimar(Y3, emp, 'E2: 5 controles por tramo, mismo dpto. y luz inicial parecida'); res.append(r); ess.append(e)

# luz solo en la parte rural de las zonas (sin áreas urbanas), con el mismo emparejamiento por luz inicial
Lr = pd.read_csv(OUT + '/luces_por_unidad_anio_solo_rural.csv')
Yr = Lr.pivot(index='unidad', columns='anio', values='log_luz_km2').dropna()
br = Yr[[2012, 2013, 2014]].mean(axis=1)
ctr = uu[(uu.grupo == 'control') & uu.unidad.isin(Yr.index)].assign(b=lambda x: x.unidad.map(br))
eleg = set()
for _, rw in uu[(uu.grupo == 'tratado') & uu.unidad.isin(Yr.index)].iterrows():
    cand = ctr[ctr.dpto == rw.dpto] if (ctr.dpto == rw.dpto).sum() >= 5 else ctr
    eleg |= set(cand.assign(dif=(cand.b - br[rw.unidad]).abs()).nsmallest(5, 'dif').unidad)
r, e = estimar(Yr, uu[((uu.grupo == 'tratado') & uu.unidad.isin(Yr.index)) | uu.unidad.isin(eleg)],
               'E3: luz solo en la parte rural de la zona, controles emparejados'); res.append(r); ess.append(e)
r, e = estimar(Yr, uu, 'E4: luz solo en la parte rural, controles del plan'); res.append(r); ess.append(e)

# Primera etapa (OSM), si se pudo bajar
try:
    S = pd.read_csv(OUT + '/superficie_osm_por_unidad_anio.csv')
    Ys = S.pivot(index='unidad', columns='anio', values='prop_mejorada')
    r, e = estimar(Ys, uu, 'Primera etapa: proporción de caminos pavimentados/empedrados/ripio (OSM)'); res.append(r); ess.append(e)
except FileNotFoundError:
    print('Sin datos de OSM: la primera etapa queda pendiente')

pd.DataFrame(res).to_csv(OUT + '/resultados_efecto_local.csv', index=False, encoding='utf-8-sig')
ES = pd.concat(ess); ES.to_csv(OUT + '/resultados_efecto_local_por_anio.csv', index=False, encoding='utf-8-sig')

# Gráfico del análisis principal (y de la primera etapa si existe)
SERIE, TXT2, GRID, FONDO = '#2a78d6', '#52514e', '#e4e3df', '#fcfcfb'
pan = [a for a in ES.analisis.unique() if a.startswith(('Principal', 'E3', 'Primera'))]
fig, axs = plt.subplots(1, len(pan), figsize=(6.5 * len(pan), 4), facecolor=FONDO, squeeze=False)
for a, nom in zip(axs[0], pan):
    d = ES[ES.analisis == nom]
    a.set_facecolor(FONDO); a.axhline(0, color=TXT2, lw=1); a.axvline(-0.5, color=TXT2, lw=1, ls='--')
    a.errorbar(d.anios_desde_obra, d.coef, yerr=[d.coef - d.ic95_inf, d.ic95_sup - d.coef], fmt='o', color=SERIE, ms=6, lw=2,
               capsize=0, markeredgecolor=FONDO, markeredgewidth=1.5)
    tit = {'Principal': 'Plan: luz, controles del plan', 'E3': 'Exploratorio: luz rural, controles emparejados',
           'Primera': 'Primera etapa: superficie mejorada (OSM)'}[nom.split(':')[0]]
    a.set_title(tit, fontsize=11, loc='left'); a.set_ylabel('diferencia en log luz por km²', color=TXT2, fontsize=9)
    a.set_xlabel('Años desde la adjudicación', color=TXT2, fontsize=9); a.tick_params(colors=TXT2, labelsize=8)
    a.grid(axis='y', color=GRID, lw=0.8); a.set_axisbelow(True)
    for s_ in ['top', 'right']: a.spines[s_].set_visible(False)
    for s_ in ['left', 'bottom']: a.spines[s_].set_color(GRID)
fig.text(0.01, 0.01, '60 tramos adjudicados 2015-2019 frente a localidades rurales a más de 10 km de un tramo. Base: promedio de los 3 años previos. IC 95 % por bootstrap de departamentos.',
         color=TXT2, fontsize=7.5)
fig.tight_layout(rect=(0, 0.05, 1, 1)); fig.savefig(OUT + '/efecto_local_tramos.png', dpi=150, facecolor=FONDO)
