# Paso 1 del análisis de inversión vial de todas las entidades (ver 17_inversion_vial_todas_entidades/PLAN_DE_ANALISIS.md):
# clasifica las obras viales municipales en rurales / urbanas / sin clasificar, las ubica por el distrito del comprador,
# suma las obras de caminos vecinales del MOPC ubicadas por distrito (16_) y arma la intensidad de inversión por distrito.
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from obras_mopc_reglas import R, preparar, VIAL, NO_OBRA, NO_VIAL

OUT = R + '/17_inversion_vial_todas_entidades'
a = preparar(pd.read_csv(R + '/08_contrataciones_DNCP/DNCP_obras_viales_todas_entidades_2012_2025.csv', dtype=str))

# ---------------- 1. Obras viales municipales ----------------
MUNI = r'empedr|enripi|cordon cuneta|cordon y cuneta|perfilad|apertura de camin|\bcalles?\b|adoquin'
es_obra = a.categoria.fillna('').str.startswith('Obras') | a.categoria.isna() | \
          a.txt_t.str.contains(r'construcci|rehabilit|mejoramiento|mantenimiento|reparaci|pavimentaci|obras')
a['obra_vial'] = (a.txt.str.contains(VIAL) | a.txt.str.contains(MUNI)) & ~a.txt_t.str.contains(NO_OBRA) & ~a.txt.str.contains(NO_VIAL) & es_obra
RURAL_T = (r'camin\w* (?:vecinal|rural)|vecinal|enripi|ripio|terraplen|perfilad|apertura de camin|puente|alcantarilla(?!do)|baden|'
           r'compania|\bcia\b|colonia|asentamiento')
URBANO_T = r'\bcalles?\b|avenida|avda|barrio|casco urbano|adoquin|cordon (?:y )?cuneta'
ru, ur = a.txt.str.contains(RURAL_T), a.txt.str.contains(URBANO_T)
a['tipo_obra'] = np.select([ru & ~ur, ur & ~ru], ['rural', 'urbana'], 'sin clasificar')
mp = pd.read_csv(OUT + '/tabla_municipalidades_distritos.csv', dtype=str)
m = a[a.obra_vial & a.comprador_id.isin(mp.comprador_id)].merge(mp[['comprador_id', 'cod_dist']], on='comprador_id')
m[['ocid', 'adjudicacion_id', 'fecha_adjudicacion', 'anio', 'monto', 'comprador', 'cod_dist', 'tipo_obra', 'titulo_llamado', 'lotes_adjudicados']] \
    .rename(columns={'monto': 'monto_adjudicado_gs'}).sort_values(['cod_dist', 'anio']) \
    .to_csv(OUT + '/obras_viales_municipales_2012_2025.csv', index=False, encoding='utf-8-sig')

# ---------------- 2. MOPC: caminos vecinales ubicados por distrito (todas cuentan como rurales) ----------------
v = pd.read_csv(R + '/16_analisis_censal_nbi_2012_2022/obras_vecinales_MOPC_2012_2025_por_distrito.csv', dtype={'cod_dist_asignados': str})
v = v[v.cod_dist_asignados.notna()].copy()
v['cod_dist'] = v.cod_dist_asignados.str.split(';'); v['n'] = v.cod_dist.str.len()
v = v.explode('cod_dist'); v['monto'] = v.monto_adjudicado_gs / v.n

# ---------------- 3. Montos por distrito y año ----------------
filas = [m.assign(fuente='municipal_' + m.tipo_obra.str.replace(' ', '_'))[['cod_dist', 'anio', 'monto', 'fuente']],
         v.assign(fuente='mopc_rural')[['cod_dist', 'anio', 'monto', 'fuente']]]
anual = pd.concat(filas).pivot_table(index=['cod_dist', 'anio'], columns='fuente', values='monto', aggfunc='sum', fill_value=0).reset_index()
for c in ['municipal_rural', 'municipal_urbana', 'municipal_sin_clasificar', 'mopc_rural']:
    if c not in anual: anual[c] = 0.0
anual['rural_total'] = anual.municipal_rural + anual.mopc_rural
anual.to_csv(OUT + '/inversion_vial_por_distrito_anio.csv', index=False, encoding='utf-8-sig')

# ---------------- 4. Intensidad 2012-2020 ----------------
b = pd.read_csv(R + '/16_analisis_censal_nbi_2012_2022/base_modelo_distrital_nbi.csv', dtype={'cod_dist': str, 'cod_dpto': str})
def suma(desde, hasta, col):
    return anual[anual.anio.between(desde, hasta)].groupby('cod_dist')[col].sum()
pr = b.set_index('cod_dist').censo_pob_rural.clip(lower=100)
pu = (b.set_index('cod_dist').censo_pob_total - b.set_index('cod_dist').censo_pob_rural).clip(lower=100)
T = lambda gs, pob: np.log1p(gs.reindex(pob.index).fillna(0) / (pob * 1000))   # log(1 + miles de Gs por habitante)
x = pd.DataFrame(index=b.cod_dist)
x['gs_rural_2012_2020'] = suma(2012, 2020, 'rural_total').reindex(x.index).fillna(0)
x['gs_rural_municipal_2012_2020'] = suma(2012, 2020, 'municipal_rural').reindex(x.index).fillna(0)
x['gs_rural_mopc_2012_2020'] = suma(2012, 2020, 'mopc_rural').reindex(x.index).fillna(0)
x['gs_urbana_municipal_2012_2020'] = suma(2012, 2020, 'municipal_urbana').reindex(x.index).fillna(0)
x['gs_sin_clasificar_municipal_2012_2020'] = suma(2012, 2020, 'municipal_sin_clasificar').reindex(x.index).fillna(0)
x['T_rural'] = T(suma(2012, 2020, 'rural_total'), pr)
x['T_urbano'] = T(suma(2012, 2020, 'municipal_urbana'), pu)
x['T_rural_municipal'] = T(suma(2012, 2020, 'municipal_rural'), pr)
x['T_rural_mopc'] = T(suma(2012, 2020, 'mopc_rural'), pr)
x['T_rural_2012_2016'] = T(suma(2012, 2016, 'rural_total'), pr)
x['T_rural_2017_2020'] = T(suma(2017, 2020, 'rural_total'), pr)
x['tiene_compras_municipales'] = x.index.isin(mp.cod_dist).astype(int)
base = b.merge(x, left_on='cod_dist', right_index=True)
base.to_csv(OUT + '/base_modelo_inversion_vial_distrital.csv', index=False, encoding='utf-8-sig')

s = base[base.muestra == 1]
r = m[m.anio.between(2012, 2020)].groupby('tipo_obra').monto.agg(['size', 'sum'])
r['pct_monto'] = (100 * r['sum'] / r['sum'].sum()).round(1)
r.to_csv(OUT + '/resumen_obras_municipales_por_tipo_2012_2020.csv', encoding='utf-8-sig')
print('obras viales municipales 2012-2020:'); print(r.assign(sum=lambda q: (q['sum'] / 1e9).round(0)))
print('distritos de la muestra:', len(s), '| con compras municipales viales:', int((s.gs_rural_municipal_2012_2020 + s.gs_urbana_municipal_2012_2020 + s.gs_sin_clasificar_municipal_2012_2020 > 0).sum()),
      '| con inversión rural > 0:', int((s.gs_rural_2012_2020 > 0).sum()))
print(s[['T_rural', 'T_urbano', 'T_rural_municipal', 'T_rural_mopc']].describe().round(2))
