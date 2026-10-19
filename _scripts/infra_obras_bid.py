"""Convierte EEO_2 (listado preliminar de obras PR-L1084) a CSV con relleno hacia abajo."""
import sys, csv, openpyxl
ws = openpyxl.load_workbook(sys.argv[1], read_only=True, data_only=True)['Resumen']
rows = list(ws.iter_rows(values_only=True))
hi = next(i for i, r in enumerate(rows) if r and 'TRAMO' in [str(c).strip() if c else '' for c in r])
hdr = [str(c).replace('\n', ' ').strip() if c else f'col{j}' for j, c in enumerate(rows[hi])]
keep = ['LLAMADO', 'DEPARTAMENTO', 'LOTES', 'TRAMO', 'LONGITUD TOTAL', 'Distrito', 'Ripio km', 'Empedrado km', 'U$D / KM', 'U$D TOTAL']
idx = {k: hdr.index(k) for k in keep}
prev = {}
out = []
for r in rows[hi+1:]:
    if not r or r[idx['TRAMO']] in (None, '') or str(r[idx['LLAMADO']] or '').startswith('TOTAL') or r[idx['TRAMO']] == 'TOTALES': continue
    d = {}
    for k in keep:
        v = r[idx[k]]
        if v in (None, '') and k in ('LLAMADO', 'DEPARTAMENTO', 'LOTES'): v = prev.get(k, '')
        d[k] = str(v).replace('\n', ' ').strip() if isinstance(v, str) else v
    prev = d; out.append(d)
with open(sys.argv[2], 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=keep); w.writeheader(); w.writerows(out)
print(len(out))
