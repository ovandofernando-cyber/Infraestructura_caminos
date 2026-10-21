import os, csv, datetime
R='/home/user/infraestructura_caminos'
rows=[]
for d,dirs,fs in os.walk(R):
    dirs[:]=[x for x in dirs if x!='.git']
    for f in fs:
        p=os.path.join(d,f); rel=os.path.relpath(p,R)
        if rel.startswith('_inventario'): continue
        rows.append([rel.split(os.sep)[0],rel,os.path.splitext(f)[1].lower().lstrip('.'),os.path.getsize(p),datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime('%Y-%m-%d %H:%M')])
rows.sort()
with open(R+'/_inventario_archivos.csv','w',newline='',encoding='utf-8-sig') as fh:
    w=csv.writer(fh); w.writerow(['carpeta','ruta_relativa','extension','bytes','fecha_descarga']); w.writerows(rows)
from collections import Counter
c=Counter(r[0] for r in rows); s=Counter()
for r in rows: s[r[0]]+=r[3]
for k in sorted(c): print(f'{k:40s} {c[k]:5d} archivos {s[k]/1e6:8.1f} MB')
print('TOTAL',len(rows),round(sum(s.values())/1e6,1),'MB')
