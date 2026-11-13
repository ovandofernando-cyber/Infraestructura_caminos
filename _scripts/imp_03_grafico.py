# Gráfico del análisis de impacto de los 11 tramos BID: estudio de eventos de la luz y efectos en acceso (EPHC).
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = '/home/user/infraestructura_caminos/25_impacto_tramos_bid'
e = pd.read_csv(OUT + '/resultados_estudio_eventos.csv'); r = pd.read_csv(OUT + '/resultados_impacto.csv')
AZUL, NARANJA, TXT, TXT2, GRID, FONDO = '#2a78d6', '#d97a2b', '#2b2a27', '#52514e', '#e4e3df', '#fcfcfb'
fig, axs = plt.subplots(1, 2, figsize=(12, 4.3), facecolor=FONDO, gridspec_kw={'width_ratios': [1.4, 1]})
a = axs[0]
a2 = e[e.diseno == 'A2']; a1 = e[e.diseno == 'A1']
a.errorbar(a2.e - 0.08, a2.att, yerr=[a2.att - a2.ic95_inf, a2.ic95_sup - a2.att], fmt='o', color=AZUL, ms=6, lw=2, capsize=0,
           markeredgecolor=FONDO, markeredgewidth=1.5, label='Controles emparejados (IC 95 %)')
a.plot(a1.e + 0.08, a1.att, 's', color=NARANJA, ms=6, markeredgecolor=FONDO, markeredgewidth=1.5, label='Controles aún no habilitados')
a.axhline(0, color=TXT2, lw=1); a.axvline(-0.5, color=TXT2, lw=1, ls='--')
a.set_xlabel('Años desde la habilitación del tramo', color=TXT2, fontsize=9); a.set_ylabel('log luz (tratados − control)', color=TXT2, fontsize=9)
a.set_title('Luz nocturna en la franja rural de 2 km de los tramos', fontsize=10.5, loc='left', color=TXT); a.legend(frameon=False, fontsize=8, loc='upper left')
b = axs[1]
bb = r[r.diseno == 'B']
lab = ['Consulta a un profesional\nsi estuvo enfermo', 'Asistencia escolar\n12 a 17 años']
for i, (_, x) in enumerate(bb.iterrows()):
    b.plot([x.ic95_inf * 100, x.ic95_sup * 100], [i, i], color=AZUL, lw=2)
    b.plot(x.coef * 100, i, 'o', color=AZUL, ms=8, markeredgecolor=FONDO, markeredgewidth=1.5)
    b.text(x.coef * 100, i + 0.15, f'{x.coef*100:+.1f} pp (p = {x.p_aleatorizacion:.2f})', ha='center', va='top', fontsize=8, color=TXT)
b.axvline(0, color=TXT2, lw=1); b.set_yticks([0, 1]); b.set_yticklabels(lab); b.set_ylim(-0.6, 1.6); b.invert_yaxis()
b.set_xlabel('Puntos porcentuales (población rural)', color=TXT2, fontsize=9)
b.set_title('Acceso: 4 dptos. con tramos frente a 7', fontsize=10.5, loc='left', color=TXT)
for x in axs:
    x.set_facecolor(FONDO); x.tick_params(colors=TXT2, labelsize=8); x.grid(axis='y' if x is a else 'x', color=GRID, lw=0.8); x.set_axisbelow(True)
    for s in ['top', 'right']: x.spines[s].set_visible(False)
    for s in ['left', 'bottom']: x.spines[s].set_color(GRID)
fig.text(0.01, 0.01, 'Izquierda: VIIRS 2012-2024; 57 segmentos de 5 km de los 11 tramos BID y 285 segmentos de control; IC por bootstrap de tramos. '
         'Derecha: INE, EPHC 2017-2019 frente a 2023-2025; IC con errores agrupados por departamento; p de aleatorización exacta.', color=TXT2, fontsize=7)
fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(OUT + '/impacto_tramos_bid.png', dpi=160, facecolor=FONDO)
