# Paso 3 del análisis censal (complemento): luz nocturna por distrito 2012-2024 alrededor del año de la primera obra
# vecinal ubicada en el distrito. Estimador del tipo Callaway y Sant'Anna con grupo de control sin obra: para cada cohorte
# g (año de la primera obra) y año t, ATT(g,t) = [Y(g,t) - base(g)] - [Y(control,t) - base(control)], con base = promedio de
# g-3 a g-1; se promedia por años desde la obra ponderando por el tamaño de cada cohorte.
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R = '/home/user/infraestructura_caminos'
OUT = R + '/16_analisis_censal_nbi_2012_2022'
rng = np.random.default_rng(2012)
b = pd.read_csv(OUT + '/base_modelo_distrital_nbi.csv', dtype={'cod_dist': str, 'cod_dpto': str})
b = b[b.muestra == 1]
l = pd.read_csv(R + '/07_clima_y_contexto/luces_nocturnas_VIIRS/luces_nocturnas_por_distrito_2012_2024.csv', dtype={'cod_dist': str})
l = l.merge(b[['cod_dist', 'cod_dpto', 'obra', 'primer_anio_2012_2020', 'n_obras_2021_2025', 'log_area_km2']], on='cod_dist')
l['log_luz_km2'] = np.log1p(l.luz_suma / np.exp(l.log_area_km2) * 100)
# Ventana balanceada de -3 a +3 años: solo cohortes con primera obra 2015-2020 (todas tienen los 7 años en 2012-2024).
# Base = promedio de los 3 años previos (g-3 a g-1), para no depender de un único año. Control: distritos sin obra ubicada
# 2012-2020 (sin condicionar a obras posteriores). Bootstrap por departamento (se remuestrean departamentos enteros).
l['cohorte'] = l.primer_anio_2012_2020
Y = l.pivot(index='cod_dist', columns='anio', values='log_luz_km2')
dpto = b.set_index('cod_dist').cod_dpto
ctrl_all = b[b.obra == 0].cod_dist
trat_all = b[b.primer_anio_2012_2020.between(2015, 2020)].set_index('cod_dist').primer_anio_2012_2020.astype(int)
E = range(-3, 4)


def att(coh, ctrl):
    out = {}
    for e in E:
        num, den = 0.0, 0
        for g, ids in coh.groupby(coh).groups.items():
            base = [g - 3, g - 2, g - 1]
            dt = (Y.loc[ids, g + e] - Y.loc[ids, base].mean(axis=1)).mean()
            dc = (Y.loc[ctrl, g + e] - Y.loc[ctrl, base].mean(axis=1)).mean()
            num += len(ids) * (dt - dc); den += len(ids)
        out[e] = num / den
    return pd.Series(out)


est = att(trat_all, ctrl_all.values)
dptos = dpto.reindex(pd.Index(trat_all.index).union(ctrl_all)).unique()
boots = []
for _ in range(499):
    dd = rng.choice(dptos, len(dptos), replace=True)
    ti = [i for d_ in dd for i in trat_all.index[dpto.reindex(trat_all.index).values == d_]]
    ci = [i for d_ in dd for i in ctrl_all[dpto.reindex(ctrl_all).values == d_]]
    if not ti or not ci: continue
    boots.append(att(trat_all.loc[ti], np.array(ci)))
B = pd.concat(boots, axis=1)
se = B.std(axis=1)
r = pd.DataFrame({'anios_desde_primera_obra': est.index, 'coef': est.values, 'ee_bootstrap_dpto': se.values})
post, pre = [0, 1, 2, 3], [-3, -2, -1]
dif = est[post].mean() - est[pre].mean(); se_dif = (B.loc[post].mean() - B.loc[pre].mean()).std()
r.to_csv(OUT + '/resultados_luces_estudio_eventos.csv', index=False, encoding='utf-8-sig')
with open(OUT + '/resultados_luces_resumen.txt', 'w') as f:
    f.write(f'Cohortes 2015-2020 (ventana balanceada -3 a +3): {len(trat_all)} distritos tratados; controles sin obra ubicada 2012-2020: {len(ctrl_all)}\n')
    f.write(f'Base: promedio de los 3 años previos a la primera obra. Bootstrap por departamento ({B.shape[1]} repeticiones).\n')
    f.write(f'Promedio años 0 a +3: {est[post].mean():.4f} (EE {B.loc[post].mean().std():.4f})\n')
    f.write(f'Promedio años -3 a -1: {est[pre].mean():.4f} (por construcción cercano a 0)\n')
    f.write(f'Diferencia después - antes: {dif:.4f} (EE {se_dif:.4f})\n')
print(open(OUT + '/resultados_luces_resumen.txt').read()); print(r.round(4).to_string())
coh = trat_all; ctrl_ids = ctrl_all

# Gráfico
SERIE, TXT2, GRID, FONDO = '#2a78d6', '#52514e', '#e4e3df', '#fcfcfb'
fig, a = plt.subplots(figsize=(7, 4), facecolor=FONDO); a.set_facecolor(FONDO)
a.axhline(0, color=TXT2, lw=1); a.axvline(-0.5, color=TXT2, lw=1, ls='--')
a.errorbar(r.anios_desde_primera_obra, r.coef, yerr=1.96 * r.ee_bootstrap_dpto, fmt='o', color=SERIE, ms=6, lw=2, capsize=0,
           markeredgecolor=FONDO, markeredgewidth=1.5)
a.set_title('Luz nocturna: distritos con obra vecinal frente a distritos sin obra', fontsize=11, loc='left')
a.set_xlabel('Años desde la primera obra adjudicada', color=TXT2, fontsize=9)
a.set_ylabel('log luz por km² (diferencia)', color=TXT2, fontsize=9)
a.tick_params(colors=TXT2, labelsize=8); a.grid(axis='y', color=GRID, lw=0.8); a.set_axisbelow(True)
for s_ in ['top', 'right']: a.spines[s_].set_visible(False)
for s_ in ['left', 'bottom']: a.spines[s_].set_color(GRID)
fig.text(0.01, 0.01, f'Cohortes 2015-2020, base = promedio de los 3 años previos. {len(coh)} tratados, {len(ctrl_ids)} controles. IC 95 % por bootstrap de departamentos.',
         color=TXT2, fontsize=7.5)
fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(OUT + '/luces_estudio_eventos.png', dpi=150, facecolor=FONDO)
