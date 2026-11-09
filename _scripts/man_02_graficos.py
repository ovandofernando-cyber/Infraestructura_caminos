# Gráficos de la Parte A (costo de no mantener y simulación de royalties).
import pandas as pd, numpy as np, geopandas as gpd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap

R = '/home/user/infraestructura_caminos'; OUT = R + '/22_propuesta_mantenimiento'
AZUL, NARANJA, TXT, TXT2, GRID, FONDO = '#2a78d6', '#d97a2b', '#2b2a27', '#52514e', '#e4e3df', '#fcfcfb'
SEQ = ['#cde2fb', '#9ec5f4', '#5598e7', '#256abf', '#104281']


def estilo(a):
    a.set_facecolor(FONDO); a.tick_params(colors=TXT2, labelsize=8)
    for s in ['top', 'right']: a.spines[s].set_visible(False)
    for s in ['left', 'bottom']: a.spines[s].set_color(GRID)


# 1. Costo de no mantener por km y año, según escenario
e = pd.read_csv(OUT + '/escenarios_costo_por_km.csv').iloc[::-1]
fig, a = plt.subplots(figsize=(9, 5), facecolor=FONDO); estilo(a)
col = [AZUL if x >= 0 else NARANJA for x in e.costo_no_mantener]
a.barh(e.escenario, e.costo_no_mantener, color=col, height=0.6)
a.axvline(0, color=TXT2, lw=1); a.grid(axis='x', color=GRID, lw=0.8); a.set_axisbelow(True)
for y, x in enumerate(e.costo_no_mantener):
    a.text(x + (600 if x >= 0 else -600), y, f'{x:,.0f}'.replace(',', '.'), va='center', ha='left' if x >= 0 else 'right', fontsize=8, color=TXT)
a.set_xlabel('USD por km y por año (positivo = no mantener le cuesta más al Estado)', color=TXT2, fontsize=9)
a.set_title('Costo de no mantener un km de camino vecinal mejorado', fontsize=11, loc='left', color=TXT)
a.set_xlim(-8000, 56000)
fig.text(0.01, 0.01, 'Costo anual equivalente sin mantenimiento menos con mantenimiento. Central: mantenimiento 2.600 USD/km/año, rehabilitación '
         '70.000 USD/km, vida 5 años sin y 15 con mantenimiento, tasa 12 %. No incluye costos de los usuarios.', color=TXT2, fontsize=7, wrap=True)
fig.tight_layout(rect=(0, 0.05, 1, 1)); fig.savefig(OUT + '/costo_no_mantener_escenarios.png', dpi=150, facecolor=FONDO)

# 2. Mapa: % de los royalties 2025 que necesitaría cada distrito para mantener su parte de la red que el MOPC declara mantener
d = pd.read_csv(OUT + '/base_costo_mantenimiento_distrital.csv', dtype={'cod_dist': str})
g = gpd.read_file(R + '/05_cartografia_y_codigos/COD-AB_OCHA_limites_admin/pry_admin_boundaries.gdb.zip', layer='pry_admin2')
g['cod_dist'] = g.adm2_pcode.str[2:]; g = g.merge(d, on='cod_dist', how='left').to_crs(32721)
cortes = [0, 10, 20, 50, 100, 600]; cmap = ListedColormap(SEQ); norm = BoundaryNorm(cortes, cmap.N)
fig, axs = plt.subplots(1, 2, figsize=(12, 6.5), facecolor=FONDO)
for a, c_, t in [(axs[0], 'pct_royalties_mejorada', 'Red vecinal mejorada (3.464 km)'),
                 (axs[1], 'pct_royalties_mopc', 'Red que el MOPC declara mantener (13.416 km)')]:
    a.set_facecolor(FONDO); a.set_axis_off()
    g.plot(column=c_, cmap=cmap, norm=norm, ax=a, edgecolor=FONDO, linewidth=0.3, missing_kwds={'color': GRID})
    a.set_title(t, fontsize=11, loc='left', color=TXT)
from matplotlib.patches import Patch
lab = ['menos de 10 %', '10 a 20 %', '20 a 50 %', '50 a 100 %', 'más del 100 %']
fig.legend(handles=[Patch(color=c, label=l) for c, l in zip(SEQ, lab)], loc='lower center', bbox_to_anchor=(0.5, 0.04), ncol=5, frameon=False, fontsize=9,
           title='Porcentaje de los royalties 2025 del municipio que costaría mantener sus caminos vecinales', title_fontsize=9)
fig.text(0.01, 0.01, 'Km del inventario MOPC (dic. 2025) repartidos por distrito según el largo de caminos rurales en OpenStreetMap. '
         'Mantenimiento a 2.600 USD/km/año (7.500 Gs/USD). Royalties liquidados por el MEF en 2025.', color=TXT2, fontsize=7)
fig.tight_layout(rect=(0, 0.13, 1, 0.96)); fig.savefig(OUT + '/mapa_pct_royalties_necesario.png', dpi=150, facecolor=FONDO)

# 3. Simulación: cobertura según el % de royalties asignado (municipio por municipio frente a fondo común) y equidad
s = pd.read_csv(OUT + '/simulacion_royalties.csv')
fig, axs = plt.subplots(1, 3, figsize=(14, 4.2), facecolor=FONDO)
for a, red, t in [(axs[0], 'mejorada', 'Red vecinal mejorada'), (axs[1], 'mopc', 'Red que el MOPC declara mantener')]:
    estilo(a); x = s[s.red == red]
    a.plot(x.pct_royalties, x.B_cobertura_pct, color=AZUL, lw=2, marker='o', ms=6, label='Fondo común (según km)')
    a.plot(x.pct_royalties, x.A_cobertura_pct, color=NARANJA, lw=2, marker='o', ms=6, label='Cada municipio con sus royalties')
    a.set_ylim(0, 105); a.grid(axis='y', color=GRID, lw=0.8); a.set_axisbelow(True)
    a.set_xlabel('% de los royalties municipales asignado', color=TXT2, fontsize=9); a.set_ylabel('% de la necesidad cubierta', color=TXT2, fontsize=9)
    a.set_title(t, fontsize=11, loc='left', color=TXT); a.set_xticks([5, 10, 15, 20, 30])
axs[0].legend(frameon=False, fontsize=8, loc='lower right')
a = axs[2]; estilo(a)
o = d[d.region == 'Oriental'].copy(); o['q'] = pd.qcut(o.nbi_2022, 4, labels=['Menos pobres', '2', '3', 'Más pobres'])
q = o.groupby('q', observed=True).agg(km=('km_vecinal', 'mean'), roy=('royalties_2025_gs', 'mean'))
xx = np.arange(4); w = 0.38
a.bar(xx - w / 2 - 0.01, q.km / q.km.iloc[0] * 100, w, color=AZUL, label='Km de caminos vecinales por distrito')
a.bar(xx + w / 2 + 0.01, q.roy / q.roy.iloc[0] * 100, w, color=NARANJA, label='Royalties por distrito')
a.axhline(100, color=TXT2, lw=1); a.set_xticks(xx); a.set_xticklabels(q.index); a.grid(axis='y', color=GRID, lw=0.8); a.set_axisbelow(True)
a.set_title('Región Oriental, por cuartil de NBI 2022', fontsize=11, loc='left', color=TXT)
a.set_ylabel('Índice (cuartil menos pobre = 100)', color=TXT2, fontsize=9); a.legend(frameon=False, fontsize=8, loc='upper left')
fig.text(0.01, 0.01, 'Costos de mantenimiento a 2.600 USD/km/año. Royalties liquidados a municipios en 2025 (MEF).', color=TXT2, fontsize=7)
fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(OUT + '/simulacion_royalties.png', dpi=150, facecolor=FONDO)
print(q.round(0))
