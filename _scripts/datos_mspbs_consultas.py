# Convierte a CSV el cuadro de la DIGIES (MSPBS): consultas registradas en los establecimientos del MSPyBS por año (2014-2024),
# según región sanitaria, y el número de establecimientos por región (2025). Fuente: https://digies.mspbs.gov.py/cobertura-en-salud/
import re, subprocess, pandas as pd

D = '/home/user/infraestructura_caminos/09_servicios_complementarios/MSPBS_DIGIES'
COD = {'CONCEPCIÓN': '01', 'SAN PEDRO': '02', 'CORDILLERA': '03', 'GUAIRÁ': '04', 'CAAGUAZÚ': '05', 'CAAZAPÁ': '06', 'ITAPÚA': '07',
       'MISIONES': '08', 'PARAGUARÍ': '09', 'ALTO PARANÁ': '10', 'CENTRAL': '11', 'ÑEEMBUCÚ': '12', 'AMAMBAY': '13', 'CANINDEYÚ': '14',
       'PRESIDENTE HAYES': '15', 'BOQUERÓN': '16', 'ALTO PARAGUAY': '17', 'CAPITAL': '00'}
txt = subprocess.run(['pdftotext', '-layout', D + '/CONSULTAS-REGISTRADAS-EN-EL-MSPYBS-2014-2024.pdf', '-'], capture_output=True, text=True).stdout
filas = []
for linea in txt.splitlines():
    m = re.match(r'^([A-ZÁÉÍÓÚÑ ]+?)\s{2,}([\d,\s]+)$', linea.strip())
    if m and m.group(1).strip() in COD:
        nums = [int(x.replace(',', '')) for x in m.group(2).split()]
        assert len(nums) == 11, linea
        filas += [dict(cod_dpto=COD[m.group(1).strip()], region_sanitaria=m.group(1).strip(), anio=2014 + i, consultas=n) for i, n in enumerate(nums)]
c = pd.DataFrame(filas)
c.to_csv(D + '/consultas_MSPBS_por_region_sanitaria_2014_2024.csv', index=False, encoding='utf-8-sig')
tot = c.groupby('anio').consultas.sum()
print(len(c), 'filas;', c.region_sanitaria.nunique(), 'regiones'); print(tot.to_dict())

txt = subprocess.run(['pdftotext', '-layout', D + '/ESTABLECIMIENTOS-DE-SALUD-MSP-Y-BS-2025.pdf', '-'], capture_output=True, text=True).stdout
TIP = ['HGMI', 'HG', 'HE', 'HMI', 'HR', 'HD', 'HDB', 'HB', 'CAES', 'CE', 'CS', 'PS', 'USF', 'DI', 'DISP', 'TOTAL']
filas = []
for linea in txt.splitlines():
    m = re.match(r'^(\d+)\.\s+([A-Za-zÁÉÍÓÚÑáéíóúñ .]+?)\s{2,}([\d\s]+)$', linea.strip())
    if m:
        nums = [int(x) for x in m.group(3).split()]
        if len(nums) == len(TIP):
            filas.append(dict(region_numero=int(m.group(1)), region_sanitaria=m.group(2).strip(), **dict(zip(TIP, nums))))
e = pd.DataFrame(filas)
e.to_csv(D + '/establecimientos_MSPBS_por_region_2025.csv', index=False, encoding='utf-8-sig')
print(len(e), 'regiones de establecimientos; total', e.TOTAL.sum())
