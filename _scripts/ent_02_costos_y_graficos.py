# Entregable del track 3 (24_entregable_mantenimiento): presupuesto del plan de mantenimiento de los 11 tramos BID
# PR-L1084/1092 (334 km), escenarios de costo-beneficio (modelo de costo anual equivalente de 22_) y gráficos.
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R = '/home/user/infraestructura_caminos'; OUT = R + '/24_entregable_mantenimiento'
TC = 7566
t = pd.read_csv(R + '/11_infraestructura_vial_complementaria/BID_tramos_intervenidos_1084_1092/tramos_intervenidos_BID_1084_1092.csv')
KM = round(t.km.sum(), 1)

# ---------------- Presupuesto (USD) ----------------
M = 2600                               # mantenimiento por niveles de servicio, USD/km/año (MOPC, EEO 7 PR-L1092)
km_anio = {1: KM / 2, 2: KM, 3: KM}    # año 1: la mitad de los subtramos, por sorteo (diseño escalonado)
filas = []
for a in [1, 2, 3]:
    mant = km_anio[a] * M
    sup = 0.10 * mant                                   # supervisión y certificación independiente (supuesto)
    rel = 300 * KM if a == 1 else 0                     # relevamiento inicial de estado, puntos críticos y tiempos de viaje (supuesto)
    loc = 5000 * 11 if a == 1 else 0                    # conformación y capacitación de 11 asociaciones de conservación (supuesto)
    ev = {1: 120000, 2: 60000, 3: 60000}[a]             # evaluación: línea de base, seguimientos, monitores y app de rugosidad (supuesto)
    sub = mant + sup + rel + loc + ev
    filas.append(dict(anio=a, km=km_anio[a], mantenimiento=mant, supervision=sup, relevamiento=rel, asociaciones=loc,
                      evaluacion=ev, administracion=0.06 * sub, total=1.06 * sub))
P = pd.DataFrame(filas); P.loc['Total'] = P.sum(numeric_only=True); P.loc['Total', 'anio'] = np.nan
P.to_csv(OUT + '/presupuesto_usd.csv', encoding='utf-8-sig')
print(P.round(0).to_string())

# ---------------- Escenarios (por km y para los 334 km) ----------------
def frc(r, n): return r / (1 - (1 + r) ** -n)
r, vida_con = 0.12, 15
costo_km_anio_todo = P.loc[2, 'total'] / KM            # costo anual por km a escala plena, con supervisión, evaluación y administración
esc = []
for nom, C, vs in [('Bajo', 70000, 8), ('Base', 70000, 5), ('Alto', 109400, 5)]:
    sin = C * frc(r, vs); con_rehab = C * frc(r, vida_con)
    evitado = sin - con_rehab                           # rehabilitación evitada por km y año (costo anual equivalente)
    esc.append(dict(escenario=nom, costo_rehabilitacion_usd_km=C, vida_sin_mant=vs, rehab_evitada_usd_km_anio=evitado,
                    costo_programa_usd_km_anio=costo_km_anio_todo, ahorro_neto_usd_km_anio=evitado - costo_km_anio_todo,
                    beneficio_costo=evitado / costo_km_anio_todo, ahorro_neto_334km_musd_anio=(evitado - costo_km_anio_todo) * KM / 1e6))
E = pd.DataFrame(esc); E.to_csv(OUT + '/escenarios_costo_beneficio.csv', index=False, encoding='utf-8-sig'); print(E.round(2).to_string())
# Alternativa: seguir como hoy (mantenimiento reactivo, rehabilitar cada 5 años) frente al plan, por km y año (base)
base = E[E.escenario == 'Base'].iloc[0]
print('Costo anual equivalente por km: hoy', round(70000 * frc(r, 5)), '| con plan', round(costo_km_anio_todo + 70000 * frc(r, vida_con)))
roy6 = 344.6e9
print('Costo anual a escala plena (Gs mil millones):', round(P.loc[2, 'total'] * TC / 1e9, 1), '=', round(100 * P.loc[2, 'total'] * TC / roy6, 1), '% de los royalties municipales 2025 de los 6 dptos.')
print('Red vecinal mejorada de los 6 dptos. (1.793 km) a 2.600 USD:', round(1793 * M * TC / 1e9, 1), 'mil millones Gs =', round(100 * 1793 * M * TC / roy6, 1), '%')

# ---------------- Gráficos ----------------
AZUL, NARANJA, GRIS, TXT, TXT2, GRID, FONDO = '#2a78d6', '#d97a2b', '#9a9893', '#2b2a27', '#52514e', '#e4e3df', '#fcfcfb'
def estilo(a):
    a.set_facecolor(FONDO); a.tick_params(colors=TXT2, labelsize=8)
    for s in ['top', 'right']: a.spines[s].set_visible(False)
    for s in ['left', 'bottom']: a.spines[s].set_color(GRID)

# Diapositiva 2: brechas rural/urbano por departamento y población cerca de los tramos
p = pd.read_csv(R + '/20_did_salud_educacion/base_modelo_personas.csv', dtype={'cod_dpto': str})
q = p[p.cod_dpto.isin(['02', '03', '05', '06', '07', '14']) & p.anio.isin([2023, 2024, 2025]) & p.consulta_profesional.notna()]
br = q.groupby(['departamento', 'rural']).apply(lambda g: 100 * np.average(g.consulta_profesional, weights=g.factor)).unstack()
br = br.sort_values(1)
fig, axs = plt.subplots(1, 2, figsize=(12, 4.3), facecolor=FONDO)
a = axs[0]; estilo(a); y = np.arange(len(br)); h = 0.38
a.barh(y + h / 2 + 0.01, br[0], h, color=GRIS, label='Urbano'); a.barh(y - h / 2 - 0.01, br[1], h, color=AZUL, label='Rural')
for i, (u, ru) in enumerate(zip(br[0], br[1])):
    a.text(ru + 0.8, i - h / 2, f'{ru:.0f}%', va='center', fontsize=8, color=TXT); a.text(u + 0.8, i + h / 2, f'{u:.0f}%', va='center', fontsize=8, color=TXT2)
a.set_yticks(y); a.set_yticklabels([d.title() for d in br.index]); a.set_xlim(0, 90); a.grid(axis='x', color=GRID, lw=0.8); a.set_axisbelow(True)
a.set_title('Enfermos que consultaron a un profesional (2023-2025)', fontsize=10.5, loc='left', color=TXT)
a.legend(frameon=False, fontsize=8, loc='lower right')
b = axs[1]; estilo(b); tt = t.sort_values('poblacion_5km')
nom = tt.tramo.str.replace(r'TRAMO \d:', '', regex=True).str.split(r'[;\n]').str[0].str.strip().str.rstrip('.').str[:34]
b.barh(range(len(tt)), tt.poblacion_5km / 1000, color=AZUL, height=0.6)
for i, (pp, e, s) in enumerate(zip(tt.poblacion_5km, tt.escuelas_5km, tt.puestos_salud_5km)):
    b.text(pp / 1000 + 0.3, i, f'{pp/1000:.1f} mil · {e} escuelas · {s} puestos', va='center', fontsize=7.5, color=TXT)
b.set_yticks(range(len(tt))); b.set_yticklabels(nom, fontsize=7.5); b.set_xlim(0, 42); b.grid(axis='x', color=GRID, lw=0.8); b.set_axisbelow(True)
b.set_xlabel('Miles de personas a menos de 5 km', color=TXT2, fontsize=9)
b.set_title('Quiénes dependen de los 11 tramos rehabilitados', fontsize=10.5, loc='left', color=TXT)
fig.text(0.01, 0.01, 'Izquierda: INE, EPHC 2023-2025 (ponderada), personas enfermas o accidentadas en los últimos 90 días; 6 departamentos del memorando. '
         'Derecha: WorldPop 2020 y geoportal INE; trazado aproximado de los tramos.', color=TXT2, fontsize=7)
fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(OUT + '/graf_quienes_afectados.png', dpi=170, facecolor=FONDO)

# Diapositiva 3: obras frente a mantenimiento por año (MOPC)
s = pd.read_csv(OUT + '/serie_obras_vs_mantenimiento_MOPC_2018_2025.csv', index_col=0).reindex(range(2018, 2026)).fillna(0)
fig, a = plt.subplots(figsize=(8.5, 4), facecolor=FONDO); estilo(a); x = np.arange(len(s)); w = 0.38
a.bar(x - w / 2 - 0.01, s.obras_vecinales_mm_gs, w, color=AZUL, label='Obras en caminos vecinales y departamentales')
a.bar(x + w / 2 + 0.01, s.mantenimiento_caminos_rurales_mm_gs, w, color=NARANJA, label='Mantenimiento de caminos rurales')
for i, v in enumerate(s.mantenimiento_caminos_rurales_mm_gs):
    if v > 0: a.text(i + w / 2, v + 40, f'{v:.0f}', ha='center', fontsize=8, color=TXT)
a.set_xticks(x); a.set_xticklabels(s.index); a.grid(axis='y', color=GRID, lw=0.8); a.set_axisbelow(True)
a.set_ylabel('Miles de millones de Gs adjudicados', color=TXT2, fontsize=9); a.legend(frameon=False, fontsize=8)
a.set_title('MOPC 2018-2025: Gs 5.863 mil millones en obras, Gs 34 mil millones en mantenimiento', fontsize=10.5, loc='left', color=TXT)
fig.text(0.01, 0.01, 'DNCP, adjudicaciones del MOPC (datos abiertos OCDS); clasificación del equipo. 2023-2025: pocas adjudicaciones registradas. No incluye el mantenimiento por administración.', color=TXT2, fontsize=6.8)
fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(OUT + '/graf_obras_vs_mantenimiento.png', dpi=170, facecolor=FONDO)
