# Paso 0 del análisis departamental: adjudicaciones del MOPC 2018-2025 desde la descarga masiva OCDS de la DNCP.
# Uso: python3 -I did_00_dncp_mopc_adjudicaciones.py <carpeta de trabajo vacía>
# Baja awa-masivo.zip y ten-masivo.zip de 2018 a 2026 (cada archivo trae los procesos publicados o actualizados ese año),
# filtra el comprador MOPC y arma 08_contrataciones_DNCP/DNCP_MOPC_adjudicaciones_2018_2025.csv.
import os, sys, subprocess, zipfile, pandas as pd

R = '/home/user/infraestructura_caminos'
D = sys.argv[1]
URL = 'https://www.contrataciones.gov.py/images/opendata-v3/final/ocds/{y}/{t}-masivo.zip'
P = 'compiledRelease/'
recs, awas, items, lots = [], [], [], []
for y in range(2018, 2027):
    for t in ('awa', 'ten'):
        f = f'{D}/{t}_{y}.zip'
        if not os.path.exists(f):
            subprocess.run(['curl', '-sS', '-L', '-m', '900', '-o', f, URL.format(y=y, t=t)], check=True)
    z = zipfile.ZipFile(f'{D}/awa_{y}.zip')
    r = pd.read_csv(z.open('records.csv'), dtype=str, usecols=['Open Contracting ID', P + 'id', P + 'tender/title',
                    P + 'tender/mainProcurementCategoryDetails', P + 'tender/procurementMethodDetails', P + 'buyer/name'])
    r = r[r[P + 'buyer/name'].fillna('').str.contains('Obras P', case=False)]
    ids = set(r[P + 'id']); recs.append(r)
    a = pd.read_csv(z.open('awards.csv'), dtype=str); awas.append(a[a[P + 'id'].isin(ids)])
    for ch in pd.read_csv(z.open('awa_items.csv'), dtype=str, chunksize=200000,
                          usecols=[P + 'id', P + 'awards/0/id', P + 'awards/0/items/0/relatedLot']):
        items.append(ch[ch[P + 'id'].isin(ids)])
    l = pd.read_csv(zipfile.ZipFile(f'{D}/ten_{y}.zip').open('ten_lots.csv'), dtype=str)
    lots.append(l[l[P + 'id'].isin(ids)])
    print(y, len(r), flush=True)
r = pd.concat(recs); a = pd.concat(awas); it = pd.concat(items).dropna().drop_duplicates()
l = pd.concat(lots).drop_duplicates([P + 'id', P + 'tender/lots/0/id'])
il = it.merge(l[[P + 'tender/lots/0/id', P + 'tender/lots/0/title']], left_on=P + 'awards/0/items/0/relatedLot', right_on=P + 'tender/lots/0/id')
lt = il.groupby(P + 'awards/0/id')[P + 'tender/lots/0/title'].apply(lambda s: ' | '.join(sorted(set(s.dropna()))))
a = a.merge(r, on=P + 'id', how='left')
a['lotes'] = a[P + 'awards/0/id'].map(lt)
a = a[a[P + 'awards/0/date'].str[:4].astype(int).between(2018, 2025)]
o = pd.DataFrame({'ocid': 'ocds-03ad3f-' + a[P + 'id'].str.extract(r'^(\d+)')[0], 'release_id': a[P + 'id'],
                  'adjudicacion_id': a[P + 'awards/0/id'], 'fecha_adjudicacion': a[P + 'awards/0/date'].str[:10],
                  'anio_adjudicacion': a[P + 'awards/0/date'].str[:4], 'estado': a[P + 'awards/0/statusDetails'],
                  'monto_adjudicado_gs': a[P + 'awards/0/value/amount'], 'moneda': a[P + 'awards/0/value/currency'],
                  'titulo_llamado': a[P + 'tender/title'], 'categoria': a[P + 'tender/mainProcurementCategoryDetails'],
                  'modalidad': a[P + 'tender/procurementMethodDetails'], 'lotes_adjudicados': a['lotes'],
                  'id_invitacion': a[P + 'awards/0/invitationID']})
o = o[o.estado.eq('Adjudicado')]
o.to_csv(R + '/08_contrataciones_DNCP/DNCP_MOPC_adjudicaciones_2018_2025.csv', index=False, encoding='utf-8-sig')
print(len(o), 'adjudicaciones')
