# Paso 5 del análisis departamental: gráficos de estudio de eventos (coeficiente y IC 95 % por año, base 2018).
import pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = '/home/user/infraestructura_caminos/15_analisis_departamental_did'
e = pd.read_csv(OUT + '/resultados_estudio_eventos.csv')
SERIE, TXT, TXT2, GRID, FONDO = '#2a78d6', '#0b0b0b', '#52514e', '#e4e3df', '#fcfcfb'
paneles = [('EPHC', 'pobre', 'Pobreza monetaria, hogares rurales', 'pp (tratados − control)', 100),
           ('EPHC interacción lluvia', 'pobre', 'Pobreza × días de lluvia ≥ 50 mm', 'pp por día adicional', 100),
           ('VIIRS', 'log_luz_km2', 'Luz nocturna, área rural', 'log (tratados − control)', 1)]
fig, ax = plt.subplots(1, 3, figsize=(13, 4.2), facecolor=FONDO)
for a, (f, y, tit, ylab, k) in zip(ax, paneles):
    d = e[(e.fuente == f) & (e.resultado == y)].sort_values('anio')
    a.set_facecolor(FONDO)
    a.axhline(0, color=TXT2, lw=1)
    a.axvline(2018.5, color=TXT2, lw=1, ls='--')
    a.errorbar(d.anio, d.coef * k, yerr=1.96 * d.ee_cluster * k, fmt='o', color=SERIE, ms=6, lw=2, capsize=0,
               markeredgecolor=FONDO, markeredgewidth=1.5)
    a.set_title(tit, color=TXT, fontsize=11, loc='left')
    a.set_ylabel(ylab, color=TXT2, fontsize=9)
    a.tick_params(colors=TXT2, labelsize=8)
    a.grid(axis='y', color=GRID, lw=0.8); a.set_axisbelow(True)
    for s in ['top', 'right']: a.spines[s].set_visible(False)
    for s in ['left', 'bottom']: a.spines[s].set_color(GRID)
    a.text(2018.6, a.get_ylim()[1], 'primeras obras', color=TXT2, fontsize=8, va='top')
fig.text(0.01, 0.01, 'Año base 2018 = 0. Barras: intervalo de confianza 95 % con errores agrupados por departamento (13 departamentos). '
         'Tratados: más obras de caminos vecinales por habitante rural (MOPC, 2018-2023).', color=TXT2, fontsize=8)
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(OUT + '/estudio_eventos.png', dpi=150, facecolor=FONDO)
print('ok')
