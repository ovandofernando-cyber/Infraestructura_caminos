# Gráfico del estudio de eventos de educación y salud (base 2017).
import pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = '/home/user/infraestructura_caminos/20_did_salud_educacion'
e = pd.read_csv(OUT + '/resultados_estudio_eventos.csv')
SERIE, TXT2, GRID, FONDO = '#2a78d6', '#52514e', '#e4e3df', '#fcfcfb'
tit = {'asiste_12_17': 'Asistencia escolar de 12 a 17 años', 'consulta_profesional': 'Consulta a un profesional si estuvo enfermo'}
fig, axs = plt.subplots(1, 2, figsize=(12, 4), facecolor=FONDO)
for a, y in zip(axs, ['asiste_12_17', 'consulta_profesional']):
    d = e[e.resultado == y].sort_values('anio')
    a.set_facecolor(FONDO); a.axhline(0, color=TXT2, lw=1); a.axvline(2018.5, color=TXT2, lw=1, ls='--')
    a.axvspan(2019.6, 2021.4, color=GRID, alpha=0.5, lw=0)
    a.errorbar(d.anio, d.coef * 100, yerr=1.96 * d.ee * 100, fmt='o', color=SERIE, ms=6, lw=2, capsize=0, markeredgecolor=FONDO, markeredgewidth=1.5)
    a.set_title(tit[y], fontsize=11, loc='left'); a.set_ylabel('pp (tratados − control)', color=TXT2, fontsize=9)
    a.tick_params(colors=TXT2, labelsize=8); a.grid(axis='y', color=GRID, lw=0.8); a.set_axisbelow(True)
    for s in ['top', 'right']: a.spines[s].set_visible(False)
    for s in ['left', 'bottom']: a.spines[s].set_color(GRID)
    a.text(2018.6, a.get_ylim()[1], 'primeras obras', color=TXT2, fontsize=8, va='top')
    a.text(2020.5, a.get_ylim()[0], 'pandemia', color=TXT2, fontsize=8, va='bottom', ha='center')
fig.text(0.01, 0.01, 'Personas rurales, EPHC. Año base 2017 = 0. IC 95 % con errores agrupados por departamento (13). '
         'Tratados: 6 departamentos con más obras vecinales del MOPC por habitante rural (2018-2023).', color=TXT2, fontsize=7.5)
fig.tight_layout(rect=(0, 0.05, 1, 1)); fig.savefig(OUT + '/estudio_eventos_salud_educacion.png', dpi=150, facecolor=FONDO)
