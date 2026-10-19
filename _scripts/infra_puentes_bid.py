"""Extrae a CSV ordenado la planilla de puentes (EEO_4, BID PR-L1084, 2014).
Uso: python3 -I infra_puentes_bid.py <xlsx> <csv_salida>"""
import sys, re, csv, openpyxl
from pyproj import Transformer
tr = Transformer.from_crs('EPSG:32721', 'EPSG:4326', always_xy=True)
wb = openpyxl.load_workbook(sys.argv[1], read_only=True, data_only=True)
UTM = re.compile(r'(?:21\s*[JK]?\s*)?(\d{6})\s+(\d{7})')
out = []
for ws in wb.worksheets:
    m = re.match(r'(\d{2})\s+(.+)', ws.title.strip())
    if not m: continue
    dpto_cod, dpto = m.group(1), m.group(2).strip()
    cur_cod = cur_tramo = ''
    for r in ws.iter_rows(values_only=True):
        cells = [c for c in r if c is not None and str(c).strip() != '']
        if not cells: continue
        joined = ' '.join(str(c) for c in cells)
        mm = UTM.search(joined)
        if not mm: continue
        x, y = float(mm.group(1)), float(mm.group(2))
        lon, lat = tr.transform(x, y)
        strs = [str(c).strip() for c in cells if isinstance(c, str)]
        nums = [c for c in cells if isinstance(c, (int, float))]
        tipo = next((s for s in strs if s in ('PM', 'PH') or s.lower().startswith(('madera', 'hormig'))), '')
        # codigo / tramo: primer valor tipo codigo, primer texto con ' - '
        cod = next((str(c) for c in cells[:2] if (isinstance(c, (int,)) and c > 999) or (isinstance(c, str) and re.match(r'^(V|CV|C V)[\s\-]?\d', c.strip()))), '')
        tramo = next((s for s in strs if ' - ' in s or '-' in s and not UTM.search(s) and len(s) > 8 and not re.match(r'^(V|CV)', s)), '')
        if cod: cur_cod = cod
        if tramo: cur_tramo = tramo
        distrito = strs[-1] if strs and not UTM.search(strs[-1]) and strs[-1] not in ('PM','TIERRA') else ''
        # largo y ancho: los dos numeros pequeños previos a la coordenada (largo<500, ancho<15)
        small = [n for n in nums if 0 < n < 500 and n != cur_cod]
        largo = ancho = ''
        # buscar par (largo, ancho) consecutivo con ancho<=8
        for i in range(len(small) - 1):
            if small[i+1] <= 8:
                largo, ancho = small[i], small[i+1]
        out.append(dict(cod_dpto=dpto_cod, departamento=dpto, codigo_camino=cur_cod, tramo=cur_tramo,
                        distrito=distrito, tipo=tipo, largo_m=largo, ancho_m=ancho,
                        utm21s_x=x, utm21s_y=y, lon=round(lon, 6), lat=round(lat, 6)))
with open(sys.argv[2], 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
from collections import Counter
print(len(out), Counter(o['cod_dpto'] for o in out))
print(Counter(o['tipo'] for o in out))
