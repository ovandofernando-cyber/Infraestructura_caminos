import json, urllib.request, urllib.parse, time, csv, os
OUT='/home/user/repositorio_caminos_vecinales/08_contrataciones_DNCP'; os.makedirs(OUT,exist_ok=True)
B='https://www.contrataciones.gov.py/datos/api/v3/doc/search/processes'
TERMS=['camino','caminos','enripiado','ripio','terraplen','alcantarilla','perfilado','puente']
seen={}
_f=OUT+'/DNCP_llamados_obras_viales_2018_2026.csv'
done=set()
if os.path.exists(_f):
    for r in csv.DictReader(open(_f,encoding='utf-8-sig')): seen[r['ocid']]=r
    done={(2018,t) for t in TERMS}|{(2019,t) for t in ['camino','caminos','enripiado']}
def call(params):
    u=B+'?'+urllib.parse.urlencode(params)
    for i in range(5):
        try:
            time.sleep(4.2)
            with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=120) as r: return json.load(r)
        except Exception as e:
            err=e; time.sleep(15*(i+1))
    print('FAIL',params,err); return None
for y in range(2018,2027):
    for t in TERMS:
        if (y,t) in done: continue
        page=1
        while True:
            d=call({'tender.title':t,'fecha_desde':f'{y}-01-01','fecha_hasta':f'{y}-12-31','tipo_fecha':'publicacion_llamado','items_per_page':100,'page':page})
            if not d: break
            for rec in d.get('records',[]):
                c=rec.get('compiledRelease',{}); tn=c.get('tender',{}) or {}
                sup='; '.join(s.get('name','') for a in c.get('awards',[]) or [] for s in a.get('suppliers',[]) or [])
                seen[rec['ocid']]=dict(ocid=rec['ocid'],anio_llamado=y,termino=t,titulo=tn.get('title'),estado=tn.get('statusDetails'),
                    categoria=tn.get('mainProcurementCategoryDetails'),modalidad=tn.get('procurementMethodDetails'),
                    entidad=(c.get('buyer') or tn.get('procuringEntity') or {}).get('name'),entidad_id=(c.get('buyer') or {}).get('id'),
                    inicio_ofertas=(tn.get('tenderPeriod') or {}).get('startDate'),proveedores=sup,
                    contratos='; '.join(x.get('id','') for x in c.get('contracts',[]) or []),
                    url_ocds=f"https://www.contrataciones.gov.py/datos/api/v3/doc/ocds/record/{rec['ocid']}")
            pg=d.get('pagination',{})
            print(y,t,page,pg.get('total_items'),len(seen),flush=True)
            if page>=pg.get('total_pages',1) or page>=100: break
            page+=1
        with open(OUT+'/DNCP_llamados_obras_viales_2018_2026.csv','w',newline='',encoding='utf-8-sig') as fh:
            w=csv.DictWriter(fh,fieldnames=list(next(iter(seen.values())).keys()) if seen else ['ocid']); w.writeheader(); w.writerows(seen.values())
print('TOTAL',len(seen))
