# Paso 1 del análisis departamental (antes y después): obras del MOPC adjudicadas 2018-2025 (DNCP).
# Clasifica cada adjudicación (obra vial / camino vecinal), la ubica en uno o más departamentos y
# arma la intensidad de tratamiento por departamento.
# Entrada: 08_contrataciones_DNCP/DNCP_MOPC_adjudicaciones_2018_2025.csv (extraída de los zips masivos OCDS awa-masivo).
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from obras_mopc_reglas import preparar, clasificar, ubicar_departamentos

R = '/home/user/infraestructura_caminos'
OUT = R + '/15_analisis_departamental_did'
ORIENTAL = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14']
FOCO = ['01', '02', '05', '06', '14']


a = pd.read_csv(R + '/08_contrataciones_DNCP/DNCP_MOPC_adjudicaciones_2018_2025.csv', dtype=str)
a = ubicar_departamentos(clasificar(preparar(a)))

obras = a[a.obra_vial].copy()
obras['deptos_txt'] = obras.deptos.map(lambda l: ';'.join(l))
cols = ['ocid', 'adjudicacion_id', 'fecha_adjudicacion', 'anio', 'monto', 'camino_vecinal', 'deptos_txt', 'n_deptos',
        'metodo_ubicacion', 'revision_manual', 'titulo_llamado', 'lotes_adjudicados', 'categoria', 'modalidad']
obras[cols].rename(columns={'monto': 'monto_adjudicado_gs', 'deptos_txt': 'cod_dpto_asignados'}) \
    .sort_values(['anio', 'monto_adjudicado_gs'], ascending=[True, False]) \
    .to_csv(OUT + '/obras_viales_MOPC_2018_2025_clasificadas.csv', index=False, encoding='utf-8-sig')

# ---------------- 3. Monto por departamento y año ----------------
e = obras[obras.n_deptos > 0].explode('deptos')
e['monto_asignado'] = e.monto / e.n_deptos
panel = []
for tipo, sub in [('vial_total', e), ('camino_vecinal', e[e.camino_vecinal])]:
    p = sub.groupby(['deptos', 'anio']).monto_asignado.sum().rename(f'gs_{tipo}')
    panel.append(p)
panel = pd.concat(panel, axis=1).fillna(0).reset_index().rename(columns={'deptos': 'cod_dpto'})
full = pd.MultiIndex.from_product([ORIENTAL, range(2018, 2026)], names=['cod_dpto', 'anio']).to_frame(index=False)
panel = full.merge(panel, how='left').fillna(0)

# población rural y total del Censo 2022 por departamento
b = pd.read_csv(R + '/13_analisis_2022/base_distrital_2022.csv', dtype={'cod_dpto': str})
pob = b.groupby('cod_dpto').agg(pob_rural_2022=('censo_pob_rural', 'sum'), pob_total_2022=('censo_pob_total', 'sum'),
                                departamento=('departamento', 'first')).reset_index()
panel = panel.merge(pob, on='cod_dpto', how='left')
panel.to_csv(OUT + '/obras_MOPC_por_departamento_anio.csv', index=False, encoding='utf-8-sig')

# Intensidad acumulada 2018-2023 (obras adjudicadas antes de la encuesta 2024)
pre = panel[panel.anio <= 2023].groupby(['cod_dpto', 'departamento', 'pob_rural_2022', 'pob_total_2022'])[['gs_vial_total', 'gs_camino_vecinal']].sum().reset_index()
pre['gs_vecinal_por_hab_rural'] = pre.gs_camino_vecinal / pre.pob_rural_2022
pre['gs_vial_por_hab'] = pre.gs_vial_total / pre.pob_total_2022
# primer año con obra de camino vecinal adjudicada en el departamento (para el estudio de eventos)
fy = panel[panel.gs_camino_vecinal > 0].groupby('cod_dpto').anio.min()
pre['primer_anio_vecinal'] = pre.cod_dpto.map(fy)
# Grupos: tratamiento = intensidad de caminos vecinales por habitante rural por encima de la mediana de la Región Oriental
pre_or = pre[pre.cod_dpto != '11']  # Central se excluye de la muestra (casi sin población rural propiamente dicha)
med = pre_or.gs_vecinal_por_hab_rural.median()
pre['tratado'] = (pre.gs_vecinal_por_hab_rural > med).astype(int)
pre.loc[pre.cod_dpto == '11', 'tratado'] = np.nan
pre['tercil_intensidad'] = pd.qcut(pre.gs_vecinal_por_hab_rural.where(pre.cod_dpto != '11'), 3, labels=['baja', 'media', 'alta'])
pre['departamento_foco'] = pre.cod_dpto.isin(FOCO).astype(int)
pre.to_csv(OUT + '/tratamiento_por_departamento.csv', index=False, encoding='utf-8-sig')

res = obras.groupby('metodo_ubicacion').agg(n=('monto', 'size'), monto_gs=('monto', 'sum'))
res['pct_monto'] = (100 * res.monto_gs / res.monto_gs.sum()).round(1)
res.to_csv(OUT + '/obras_MOPC_resumen_ubicacion.csv', encoding='utf-8-sig')
print('Adjudicaciones', len(a), '| obras viales', len(obras), f'{obras.monto.sum()/1e12:.2f} billones Gs',
      '| caminos vecinales', int(obras.camino_vecinal.sum()), f'{obras[obras.camino_vecinal].monto.sum()/1e12:.2f} billones Gs')
print(res)
print(pre[['cod_dpto', 'departamento', 'gs_camino_vecinal', 'gs_vecinal_por_hab_rural', 'gs_vial_por_hab', 'primer_anio_vecinal', 'tratado']]
      .assign(gs_camino_vecinal=lambda x: (x.gs_camino_vecinal / 1e9).round(1)).round(0).to_string())
print('mediana', round(med))
