# Entregable del track 3: el mantenimiento como política que (1) sostiene los beneficios logrados para los usuarios y
# (2) reduce el gasto del MOPC frente a rehabilitar o reconstruir cuando pasa mucho tiempo.
# Beneficios documentados de PR-L1084 (informe de terminación del BID, antes y después): costo de operación vehicular
# -25,2 % (automóvil 0,38 -> 0,28 USD por vehículo-km), tiempo de viaje -39,8 %, días transitables 75 % -> 100 %,
# tránsito diario 156 -> 320 vehículos. Sin mantenimiento, el beneficio se pierde de forma gradual (lineal) hasta la
# rehabilitación: en promedio se pierde la mitad del beneficio anual.
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R = '/home/user/infraestructura_caminos'; OUT = R + '/24_entregable_mantenimiento'
KM = 333.9; r, vida_con = 0.12, 15
P = pd.read_csv(OUT + '/presupuesto_usd.csv', index_col=0)
costo_prog = P.loc['2', 'total'] / KM                       # USD por km y año a escala plena (supervisión, evaluación y administración incluidas)
def frc(r, n): return r / (1 - (1 + r) ** -n)

# Ahorro de los usuarios por km y año con el camino en buen estado = tránsito diario x 365 x ahorro por vehículo-km
# (solo costo de operación; no se cuenta el tiempo de viaje). Ahorro por vehículo-km: 0,05 USD (la mitad del de un
# automóvil, por el peso de las motos) o 0,10 USD (automóvil).
filas = []
for nom, C, vs, tpda, ahorro_vkm in [('Bajo', 70000, 8, 156, 0.05), ('Base', 70000, 5, 320, 0.05), ('Alto', 109400, 5, 320, 0.10)]:
    rehab_evitada = C * frc(r, vs) - C * frc(r, vida_con)
    usuarios_buen_estado = tpda * 365 * ahorro_vkm
    usuarios_sostenido = usuarios_buen_estado / 2           # lo que se pierde en promedio si el camino se deja deteriorar
    total = rehab_evitada + usuarios_sostenido
    filas.append(dict(escenario=nom, costo_rehab_usd_km=C, vida_sin_mant=vs, tpda=tpda, ahorro_usd_vehkm=ahorro_vkm,
                      rehab_evitada_usd_km_anio=rehab_evitada, beneficio_usuarios_sostenido_usd_km_anio=usuarios_sostenido,
                      costo_programa_usd_km_anio=costo_prog, bc_solo_fiscal=rehab_evitada / costo_prog, bc_fiscal_y_usuarios=total / costo_prog,
                      beneficio_neto_334km_musd_anio=(total - costo_prog) * KM / 1e6,
                      ahorro_fiscal_neto_334km_musd_anio=(rehab_evitada - costo_prog) * KM / 1e6,
                      usuarios_334km_musd_anio=usuarios_sostenido * KM / 1e6))
E = pd.DataFrame(filas); E.to_csv(OUT + '/escenarios_beneficios_sostenidos.csv', index=False, encoding='utf-8-sig')
print(E.round(2).T.to_string())

# Gasto acumulado del MOPC por km en 15 años (sin descontar): mantener frente a dejar deteriorar
anios = np.arange(0, 16)
mant = 2600 * anios + 70000 * (anios >= 15)               # con mantenimiento: rehabilitar al final de la vida útil (año 15)
reh5 = np.array([70000 * (a // 5) for a in anios])        # sin mantenimiento: rehabilitar cada 5 años (escenario base)
print('A 15 años: mantener', mant[-1], '| rehabilitar cada 5 años', reh5[-1])
print('Km mantenidos un año con lo que cuesta rehabilitar 1 km de los 11 tramos:', round(109400 / 2600))
AZUL, NARANJA, GRIS, TXT, TXT2, GRID, FONDO = '#2a78d6', '#d97a2b', '#77756f', '#2b2a27', '#52514e', '#e4e3df', '#fcfcfb'
fig, axs = plt.subplots(1, 2, figsize=(12, 4.2), facecolor=FONDO, gridspec_kw={'width_ratios': [1.25, 1]})
a = axs[0]
a.step(anios, reh5 / 1000, where='post', color=NARANJA, lw=2, label='Sin mantenimiento: rehabilitar cada 5 años (USD 70.000/km)')
a.step(anios, mant / 1000, where='post', color=AZUL, lw=2.5, label='Con mantenimiento (USD 2.600/km/año y rehabilitación en el año 15)')
a.text(0.3, 150, 'Con lo que cuesta rehabilitar 1 km de los 11 tramos\n(USD 109.400) se mantienen 42 km durante un año', fontsize=8, color=TXT)
for y, c, t in [(reh5[-1], NARANJA, 'USD 210.000'), (mant[-1], AZUL, 'USD 109.000')]:
    a.text(15.2, y / 1000, t, va='center', fontsize=8, color=TXT)
a.set_xlim(0, 17.5); a.set_xlabel('Años desde la recepción de la obra', color=TXT2, fontsize=9); a.set_ylabel('Miles de USD por km (acumulado)', color=TXT2, fontsize=9)
a.set_title('Gasto del MOPC por km en 15 años', fontsize=10.5, loc='left', color=TXT); a.legend(frameon=False, fontsize=7.5, loc='upper left')
b = axs[1]; x = np.arange(3); w = 0.38
b.bar(x - w / 2 - 0.01, E.bc_solo_fiscal, w, color=GRIS, label='Solo rehabilitación evitada')
b.bar(x + w / 2 + 0.01, E.bc_fiscal_y_usuarios, w, color=AZUL, label='Más beneficios de los usuarios sostenidos')
for i, (f, u) in enumerate(zip(E.bc_solo_fiscal, E.bc_fiscal_y_usuarios)):
    b.text(i - w / 2, f + 0.1, f'{f:.1f}', ha='center', fontsize=8, color=TXT); b.text(i + w / 2, u + 0.1, f'{u:.1f}', ha='center', fontsize=8, color=TXT)
b.axhline(1, color=TXT2, lw=1, ls=':'); b.set_xticks(x); b.set_xticklabels(E.escenario)
b.set_ylabel('USD de beneficio por USD de mantenimiento', color=TXT2, fontsize=9); b.legend(frameon=False, fontsize=7.5, loc='upper left')
b.set_title('Relación beneficio-costo del plan (334 km)', fontsize=10.5, loc='left', color=TXT)
for ax in axs:
    ax.set_facecolor(FONDO); ax.tick_params(colors=TXT2, labelsize=8); ax.grid(axis='y', color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ['top', 'right']: ax.spines[s].set_visible(False)
    for s in ['left', 'bottom']: ax.spines[s].set_color(GRID)
fig.text(0.01, 0.01, 'Costos: plan del MOPC para el BID (EEO 7), planilla de los 11 tramos y supuestos del equipo. Beneficios de los usuarios: BID, informe de terminación '
         'PR-L1084 (antes y después); solo costo de operación vehicular, sin tiempo de viaje.', color=TXT2, fontsize=6.8)
fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(OUT + '/graf_mantener_vs_reconstruir.png', dpi=170, facecolor=FONDO)
