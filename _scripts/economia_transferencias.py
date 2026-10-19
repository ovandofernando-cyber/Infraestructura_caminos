"""Transferencias MEF a municipios (transcripción) -> CSV con cod_dist INE 2022.
Uso: python3 -I economia_transferencias.py <raw.txt> <base_distrital_integrada.csv> <salida.csv> <anio>"""
import sys, csv, unicodedata, re, difflib
raw, base, out, anio = sys.argv[1:5]
def norm(s):
    s=unicodedata.normalize('NFKD', s.upper()).encode('ascii','ignore').decode()
    s=re.sub(r'\(.*?\)','',s); s=re.sub(r'[^A-Z0-9 ]',' ',s)
    for a,b in [('GRAL ','GENERAL '),('DR ','DOCTOR '),('MCAL ','MARISCAL '),('CAP ','CAPITAN '),('PTE ','PRESIDENTE '),('TTE ','TENIENTE ')]:
        s=(' '+s+' ').replace(' '+a,' '+b).strip()
    return re.sub(r'\s+',' ',s).strip()
dist=[r for r in csv.DictReader(open(base,encoding='utf-8-sig'))]
manual={('17','LA VICTORIA'):'1702',('15','PUERTO FALCON'):'1506',('6','3 DE MAYO'):'0611',('5','NUEVA TOLEDO'):'0522',('5','TEMBIAPORA'):'0521',
        ('1','SAN CARLOS DEL APA'):'0105'}
n=lambda x:int(x.replace('.','') or 0)
res=[]
for r in csv.DictReader(open(raw,encoding='utf-8'),delimiter=';'):
    if r['municipio'] in ('SUBTOTAL','TOTAL GENERAL') or r['nro_dpto'] in ('','0'): continue
    d=r['nro_dpto'].zfill(2); nm=norm(r['municipio'])
    cands=[x for x in dist if x['cod_dpto']==d]
    names={norm(x['distrito']):x for x in cands}
    pick=None; how='exacto'
    key=(r['nro_dpto'],nm)
    if key in manual: pick=next(x for x in dist if x['cod_dist']==manual[key]); how='manual'
    elif nm in names: pick=names[nm]
    else:
        m=difflib.get_close_matches(nm, list(names), n=1, cutoff=0.5)
        if not m:
            m=[k for k in names if nm.split()[-1] in k.split()]
        if m: pick=names[m[0]]; how='aproximado'
    v1,v2,v3,t=(n(r[k]) for k in ('v1','v2','v3','total'))
    res.append([anio,d,r['municipio'],pick['cod_dist'] if pick else '',pick['distrito'] if pick else '',how if pick else 'sin_match',v1,v2,v3,t-v1-v2-v3,t])
with open(out,'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['anio','cod_dpto','municipio_mef','cod_dist','distrito_ine','match','royalties_mill_gs','fonacide_mill_gs','juegos_azar_mill_gs','otras_transferencias_mill_gs','total_transferencias_mill_gs']); w.writerows(res)
import collections
c=collections.Counter(x[3] for x in res)
print('filas',len(res),'dups',[k for k,v in c.items() if v>1])
for x in res:
    if x[5]!='exacto': print(x[1],x[2],'->',x[3],x[4],x[5])
