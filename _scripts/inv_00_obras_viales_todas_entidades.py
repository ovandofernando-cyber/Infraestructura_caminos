# Paso 0 del análisis de inversión vial de todas las entidades: adjudicaciones de obras viales 2012-2025 de cualquier comprador
# (municipalidades, gobernaciones, MOPC y otros) desde la descarga masiva OCDS de la DNCP.
# Uso: python3 -I inv_00_obras_viales_todas_entidades.py <carpeta con awa_AAAA.zip y ten_AAAA.zip de 2011 a 2026>
import os, sys, zipfile, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from obras_mopc_reglas import R, norm

D = sys.argv[1]
P = 'compiledRelease/'
# primer filtro amplio por título (después se aplican las reglas de obra vial)
FILTRO = (r'camin|empedr|ripio|enripi|paviment|asfalt|adoquin|puente|alcantarilla(?!do)|terraplen|baden|tramo|calle|ruta|cuneta|'
          r'perfilado|vial|apertura')
recs, awas, items, lots = [], [], [], []
for y in range(2011, 2027):
    z = zipfile.ZipFile(f'{D}/awa_{y}.zip')
    r = pd.read_csv(z.open('records.csv'), dtype=str, usecols=[P + 'id', P + 'tender/title', P + 'tender/mainProcurementCategoryDetails',
                    P + 'tender/procurementMethodDetails', P + 'buyer/id', P + 'buyer/name'])
    r = r[r[P + 'tender/title'].map(norm).str.contains(FILTRO)]
    ids = set(r[P + 'id']); recs.append(r)
    a = pd.read_csv(z.open('awards.csv'), dtype=str); awas.append(a[a[P + 'id'].isin(ids)])
    for ch in pd.read_csv(z.open('awa_items.csv'), dtype=str, chunksize=300000,
                          usecols=[P + 'id', P + 'awards/0/id', P + 'awards/0/items/0/relatedLot']):
        items.append(ch[ch[P + 'id'].isin(ids)])
    l = pd.read_csv(zipfile.ZipFile(f'{D}/ten_{y}.zip').open('ten_lots.csv'), dtype=str)
    lots.append(l[l[P + 'id'].isin(ids)])
    print(y, len(r), flush=True)
r = pd.concat(recs).drop_duplicates(P + 'id'); a = pd.concat(awas).drop_duplicates(P + 'awards/0/id')
it = pd.concat(items).dropna().drop_duplicates()
l = pd.concat(lots).drop_duplicates([P + 'id', P + 'tender/lots/0/id'])
il = it.merge(l[[P + 'tender/lots/0/id', P + 'tender/lots/0/title']], left_on=P + 'awards/0/items/0/relatedLot', right_on=P + 'tender/lots/0/id')
lt = il.groupby(P + 'awards/0/id')[P + 'tender/lots/0/title'].apply(lambda s: ' | '.join(sorted(set(s.dropna()))))
a = a.merge(r, on=P + 'id', how='left')
a['lotes'] = a[P + 'awards/0/id'].map(lt)
a = a[a[P + 'awards/0/date'].str[:4].astype(int).between(2012, 2025) & a[P + 'awards/0/statusDetails'].eq('Adjudicado')]
o = pd.DataFrame({'ocid': 'ocds-03ad3f-' + a[P + 'id'].str.extract(r'^(\d+)')[0], 'release_id': a[P + 'id'],
                  'adjudicacion_id': a[P + 'awards/0/id'], 'fecha_adjudicacion': a[P + 'awards/0/date'].str[:10],
                  'anio_adjudicacion': a[P + 'awards/0/date'].str[:4], 'estado': a[P + 'awards/0/statusDetails'],
                  'monto_adjudicado_gs': a[P + 'awards/0/value/amount'], 'moneda': a[P + 'awards/0/value/currency'],
                  'comprador_id': a[P + 'buyer/id'], 'comprador': a[P + 'buyer/name'],
                  'titulo_llamado': a[P + 'tender/title'], 'categoria': a[P + 'tender/mainProcurementCategoryDetails'],
                  'modalidad': a[P + 'tender/procurementMethodDetails'], 'lotes_adjudicados': a['lotes']})
o.to_csv(R + '/08_contrataciones_DNCP/DNCP_obras_viales_todas_entidades_2012_2025.csv', index=False, encoding='utf-8-sig')
print(len(o), 'adjudicaciones;', o.comprador.nunique(), 'compradores')
