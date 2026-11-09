# Gráfico del DiD de mantenimiento: coeficientes del diseño distrital y estudio de eventos de la luz nocturna.
import pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = '/home/user/infraestructura_caminos/23_did_mantenimiento'
r = pd.read_csv(OUT + '/resultados_did_mantenimiento.csv'); e = pd.read_csv(OUT + '/resultados_luces_estudio_eventos.csv')
AZUL, NARANJA, TXT, TXT2, GRID, FONDO = '#2a78d6', '#d97a2b', '#2b2a27', '#52514e', '#e4e3df', '#fcfcfb'
fig, axs = plt.subplots(1, 2, figsize=(12, 4.3), facecolor=FONDO, gridspec_kw={'width_ratios': [1.15, 1]})
a = axs[0]
sel = [('Principal: cambio NBI 2012-2022, obra temprana', 'Principal (con controles)'), ('S1 Diferencia simple 2x2', 'Diferencia simple, sin controles'),
       ('S4 Placebo: primer contrato 2022-2024 vs nunca', 'Placebo: contrataron recién en 2022-2024')]
for i, (k, lab) in enumerate(sel):
    x = r[r.modelo == k].iloc[0]; c = AZUL if i == 0 else (TXT2 if i == 1 else NARANJA)
    a.plot([x.ic95_inf, x.ic95_sup], [i, i], color=c, lw=2); a.plot(x.coef, i, 'o', color=c, ms=8, markeredgecolor=FONDO, markeredgewidth=1.5)
    a.text(x.coef, i + 0.12, f'{x.coef:+.1f} pp', ha='center', va='top', fontsize=8, color=TXT)
a.set_yticks(range(3)); a.set_yticklabels([s[1] for s in sel]); a.set_ylim(-0.5, 2.6); a.invert_yaxis(); a.axvline(0, color=TXT2, lw=1)
a.set_xlabel('Cambio del NBI 2012-2022 (pp; negativo = mejora)', color=TXT2, fontsize=9)
a.set_title('Distritos con obra: con frente a sin mantenimiento', fontsize=11, loc='left', color=TXT)
b = axs[1]
b.axhline(0, color=TXT2, lw=1); b.axvline(-0.5, color=TXT2, lw=1, ls='--')
b.errorbar(e.anios_desde_primer_contrato, e.coef, yerr=1.96 * e.ee_bootstrap_dpto, fmt='o', color=AZUL, ms=6, lw=2, capsize=0,
           markeredgecolor=FONDO, markeredgewidth=1.5)
b.set_xlabel('Años desde el primer contrato de mantenimiento', color=TXT2, fontsize=9); b.set_ylabel('log luz por km² (tratados − control)', color=TXT2, fontsize=9)
b.set_title('Luz nocturna alrededor del primer contrato', fontsize=11, loc='left', color=TXT)
for x in axs:
    x.set_facecolor(FONDO); x.tick_params(colors=TXT2, labelsize=8); x.grid(axis='x' if x is a else 'y', color=GRID, lw=0.8); x.set_axisbelow(True)
    for s in ['top', 'right']: x.spines[s].set_visible(False)
    for s in ['left', 'bottom']: x.spines[s].set_color(GRID)
fig.text(0.01, 0.01, 'IC 95 %: errores agrupados por departamento (izquierda) y bootstrap de departamentos (derecha). Mantenimiento = contrato municipal '
         'de mantenimiento de caminos vecinales en la DNCP.', color=TXT2, fontsize=7)
fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(OUT + '/did_mantenimiento.png', dpi=150, facecolor=FONDO)
