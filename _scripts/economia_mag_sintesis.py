"""Limpia transcripciones de Síntesis Estadísticas MAG/DCEA y verifica suma de departamentos vs total país.
Uso: python3 -I economia_mag_sintesis.py <salida.csv> <raw1.txt> [raw2.txt ...]"""
import sys, csv, collections
out, raws = sys.argv[1], sys.argv[2:]
def num(x):
    x=x.strip()
    if x in ('-','',' '): return ''
    return int(x.replace('.','').replace(',',''))
rows=[]
for raw in raws:
    with open(raw, encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter=';'):
            rec={'cultivo':r['cultivo'].upper().replace('MAIZ','MAÍZ').replace('MANI','MANÍ').replace('TARTAGO','TÁRTAGO'),
                 'cod_dpto':r['cod_dpto'],'departamento':r['departamento'],'campana':r['campana'],'nota':''}
            for k in ('superficie_ha','produccion_t','rendimiento_kg_ha'):
                v=r[k]
                if v.startswith('.'): rec['nota']+=f'{k} impreso como "{v}" en origen; '
                rec[k]=num(v.lstrip('.'))
            rows.append(rec)
# verificación
agg=collections.defaultdict(lambda:[0,0]); tot={}
for r in rows:
    key=(r['cultivo'],r['campana'])
    if r['cod_dpto']:
        agg[key][0]+=r['superficie_ha'] or 0; agg[key][1]+=r['produccion_t'] or 0
    elif r['departamento'].upper()=='TOTAL PAIS': tot[key]=(r['superficie_ha'] or 0, r['produccion_t'] or 0)
for key,(s,p) in sorted(agg.items()):
    if key in tot:
        ts,tp=tot[key]; flag='' if (abs(s-ts)<=max(5,0.002*ts) and abs(p-tp)<=max(5,0.002*tp)) else '  <-- DIFERENCIA'
        print(key, 'sup', s, ts, 'prod', p, tp, flag)
with open(out,'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f, fieldnames=['cultivo','cod_dpto','departamento','campana','superficie_ha','produccion_t','rendimiento_kg_ha','nota'])
    w.writeheader(); w.writerows(rows)
print('filas', len(rows))
