# Paso 3 del análisis censal (complemento): luz nocturna por distrito 2012-2024 alrededor del año de la primera obra
# vecinal ubicada en el distrito. Estimador de Callaway y Sant'Anna con grupo de control "nunca tratado": para cada cohorte
# g (año de la primera obra) y año t, ATT(g,t) = [Y(g,t) - Y(g,g-1)] - [Y(control,t) - Y(control,g-1)]; luego se promedia
# por años desde la obra, ponderando por el tamaño de cada cohorte. Errores por bootstrap de distritos (499 repeticiones).
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
# controles: distritos sin obra ubicada hasta 2025; tratados: primera obra 2013-2020 (la cohorte 2012 no tiene año previo)
l['cohorte'] = l.primer_anio_2012_2020
ctrl_ids = b[(b.obra == 0) & (b.n_obras_2021_2025 == 0)].cod_dist
trat = b[b.primer_anio_2012_2020.between(2013, 2020)]
Y = l.pivot(index='cod_dist', columns='anio', values='log_luz_km2')
coh = trat.set_index('cod_dist').primer_anio_2012_2020.astype(int)
E = range(-5, 7)


def att(coh, ctrl):
    out = {}
    for e in E:
        num, den = 0.0, 0
        for g, ids in coh.groupby(coh).groups.items():
            t = g + e
            if t not in Y.columns or g - 1 not in Y.columns or e == -1: continue
            dt = (Y.loc[ids, t] - Y.loc[ids, g - 1]).mean()
            dc = (Y.loc[ctrl, t] - Y.loc[ctrl, g - 1]).mean()
            num += len(ids) * (dt - dc); den += len(ids)
        out[e] = num / den if den else np.nan
    out[-1] = 0.0
    return pd.Series(out).sort_index()


est = att(coh, ctrl_ids.values)
boots = []
for _ in range(499):
    c2 = pd.Series(coh.values, index=coh.index).sample(len(coh), replace=True, random_state=rng.integers(1e9))
    k2 = rng.choice(ctrl_ids.values, len(ctrl_ids), replace=True)
    boots.append(att(c2, k2))
se = pd.concat(boots, axis=1).std(axis=1)
r = pd.DataFrame({'anios_desde_primera_obra': est.index, 'coef': est.values, 'ee_bootstrap': se.reindex(est.index).values})
post = [e for e in E if e >= 0]
promedio = np.mean([est[e] for e in post]); se_prom = np.std([np.mean([bb[e] for e in post]) for bb in boots])
pre_prom = np.mean([est[e] for e in E if e <= -2]); se_pre = np.std([np.mean([bb[e] for e in E if e <= -2]) for bb in boots])
r.to_csv(OUT + '/resultados_luces_estudio_eventos.csv', index=False, encoding='utf-8-sig')
with open(OUT + '/resultados_luces_resumen.txt', 'w') as f:
    f.write(f'Distritos tratados (primera obra 2013-2020): {len(coh)}; controles (sin obra ubicada 2012-2025): {len(ctrl_ids)}\n')
    f.write(f'Efecto promedio años 0 a 6: {promedio:.4f} (EE {se_prom:.4f})\n')
    f.write(f'Promedio años -5 a -2 (tendencia previa): {pre_prom:.4f} (EE {se_pre:.4f})\n')
print(open(OUT + '/resultados_luces_resumen.txt').read()); print(r.round(4).to_string())

# Gráfico
SERIE, TXT2, GRID, FONDO = '#2a78d6', '#52514e', '#e4e3df', '#fcfcfb'
fig, a = plt.subplots(figsize=(7, 4), facecolor=FONDO); a.set_facecolor(FONDO)
a.axhline(0, color=TXT2, lw=1); a.axvline(-0.5, color=TXT2, lw=1, ls='--')
a.errorbar(r.anios_desde_primera_obra, r.coef, yerr=1.96 * r.ee_bootstrap, fmt='o', color=SERIE, ms=6, lw=2, capsize=0,
           markeredgecolor=FONDO, markeredgewidth=1.5)
a.set_title('Luz nocturna: distritos con obra vecinal frente a distritos sin obra', fontsize=11, loc='left')
a.set_xlabel('Años desde la primera obra adjudicada', color=TXT2, fontsize=9)
a.set_ylabel('log luz por km² (diferencia)', color=TXT2, fontsize=9)
a.tick_params(colors=TXT2, labelsize=8); a.grid(axis='y', color=GRID, lw=0.8); a.set_axisbelow(True)
for s_ in ['top', 'right']: a.spines[s_].set_visible(False)
for s_ in ['left', 'bottom']: a.spines[s_].set_color(GRID)
fig.text(0.01, 0.01, f'Callaway-Sant\'Anna, control: distritos sin obra ubicada. {len(coh)} tratados, {len(ctrl_ids)} controles. IC 95 % por bootstrap.',
         color=TXT2, fontsize=7.5)
fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(OUT + '/luces_estudio_eventos.png', dpi=150, facecolor=FONDO)
