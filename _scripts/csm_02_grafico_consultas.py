# Gráfico: consultas del MSPyBS por 1.000 habitantes por grupo y estudio de eventos (base 2017).
import pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = '/home/user/infraestructura_caminos/21_did_consultas_mspbs'
e = pd.read_csv(OUT + '/resultados_estudio_eventos.csv').sort_values('anio')
g = pd.read_csv(OUT + '/descriptivos_por_grupo_anio.csv')
TRAT, CTRL, TXT2, GRID, FONDO = '#2a78d6', '#d97a2b', '#52514e', '#e4e3df', '#fcfcfb'
fig, axs = plt.subplots(1, 2, figsize=(12, 4), facecolor=FONDO)
a = axs[0]
for t, col, lab in [(1, TRAT, 'Tratados (6)'), (0, CTRL, 'Control (7)')]:
    d = g[g.tratado == t].sort_values('anio')
    a.plot(d.anio, d.consultas_por_1000_agregado, color=col, lw=2, marker='o', ms=4)
    a.text(2024.2, d.consultas_por_1000_agregado.iloc[-1], lab, color=col, fontsize=9, va='center')
a.set_title('Consultas en el MSPyBS por 1.000 habitantes', fontsize=11, loc='left')
a.set_xlim(2013.5, 2026)
b = axs[1]
b.axhline(0, color=TXT2, lw=1)
b.errorbar(e.anio, e.coef, yerr=1.96 * e.ee, fmt='o', color=TRAT, ms=6, lw=2, capsize=0, markeredgecolor=FONDO, markeredgewidth=1.5)
b.set_title('Diferencia tratados − control (log; base 2017 = 0)', fontsize=11, loc='left')
for x in axs:
    x.set_facecolor(FONDO); x.axvline(2017.5, color=TXT2, lw=1, ls='--'); x.axvspan(2019.6, 2021.4, color=GRID, alpha=0.5, lw=0)
    x.tick_params(colors=TXT2, labelsize=8); x.grid(axis='y', color=GRID, lw=0.8); x.set_axisbelow(True)
    for s in ['top', 'right']: x.spines[s].set_visible(False)
    for s in ['left', 'bottom']: x.spines[s].set_color(GRID)
    x.text(2017.6, x.get_ylim()[1], 'primeras obras', color=TXT2, fontsize=8, va='top')
    x.text(2020.5, x.get_ylim()[0], 'pandemia', color=TXT2, fontsize=8, va='bottom', ha='center')
fig.text(0.01, 0.01, 'DIGIES-MSPyBS (datos provisorios) e INE, revisión 2025. 13 departamentos de la Región Oriental sin Central. '
         'IC 95 % con errores agrupados por departamento.', color=TXT2, fontsize=7.5)
fig.tight_layout(rect=(0, 0.05, 1, 1)); fig.savefig(OUT + '/consultas_mspbs_did.png', dpi=150, facecolor=FONDO)
