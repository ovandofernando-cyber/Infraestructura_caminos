import json, urllib.request, urllib.parse, os, re, sys, time, csv
R='/home/user/repositorio_caminos_vecinales'
JOBS=[
 ('01_condiciones_de_vida/pobreza_distrital','mapa-de-pobreza-monetaria-distrital'),
 ('01_condiciones_de_vida/pobreza_distrital','indice-de-pobreza-multidimensional-distrital'),
 ('01_condiciones_de_vida/pobreza_tabulados','principales-resultados-de-pobreza-monetaria-y-distribución-de-ingresos-2025'),
 ('01_condiciones_de_vida/pobreza_tabulados','indice-de-pobreza-multidimensional-ipm'),
 ('02_censo_2022','resultados-finales-del-censo-nacional-de-población-y-viviendas-2022'),
 ('02_censo_2022','características-de-los-hogares'),
 ('02_censo_2022','estructura-y-características-sociodemográficas-de-la-población'),
 ('02_censo_2022','características-laborales-de-la-población-según-el-censo-2022'),
 ('02_censo_2022','iv-censo-nacional-indígena-2022-resultados-finales-de-población-y-viviendas'),
 ('02_censo_2022','estimaciones-y-proyecciones-de-la-poblacion-distrital-2000-2035-revisión-2025'),
 ('03_red_vial_MOPC/anuarios_INE_vialidad','anuario-2021-vialidad-transporte-y-comunicacion'),
 ('03_red_vial_MOPC/anuarios_INE_vialidad','anuario-estadístico-2019-vialidad-transporte-y-comunicación'),
 ('04_servicios_e_instituciones','estableciminetos-sanitarios'),
 ('04_servicios_e_instituciones','establecimientos-escolares'),
 ('04_servicios_e_instituciones','anuario-2021-servicios'),
 ('04_servicios_e_instituciones','tablero-desempeño-distrital-de-instituciones'),
 ('05_cartografia_y_codigos','base-de-datos-geojson-geoespacial-de-departamentos-distritos-ciudades-y-barrios-de-todo-el'),
 ('05_cartografia_y_codigos','códigos-geográficos-censo-nacional-de-población-y-viviendas-2012-paraguay'),
 ('06_produccion_CAN_2022','censo-agropecuario-nacional-can-2022'),
 ('06_produccion_CAN_2022','datos-de-censo-agropecuario-nacional-2022'),
]
log=open(R+'/_registro_descargas_datos_gov_py.csv','a',newline='',encoding='utf-8'); W=csv.writer(log)
def get(u,tries=5):
    for i in range(tries):
        try:
            req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(req,timeout=120) as r: return r.read()
        except Exception as e:
            err=e; time.sleep(2**(i+1))
    raise err
only=sys.argv[1:] or None
for folder,slug in JOBS:
    if only and not any(o in slug for o in only): continue
    try:
        meta=json.loads(get('https://www.datos.gov.py/api/3/action/package_show?id='+urllib.parse.quote(slug)))
    except Exception as e:
        print('META FAIL',slug,e); continue
    p=meta['result'][0] if isinstance(meta['result'],list) else meta['result']
    d=os.path.join(R,folder,re.sub(r'[^\w\-]+','_',p['name'])[:80]); os.makedirs(d,exist_ok=True)
    json.dump(p,open(os.path.join(d,'_metadatos_datos_gov_py.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
    print(f"## {p['title']} ({len(p.get('resources',[]))} recursos)")
    for r in p.get('resources',[]):
        url=r.get('url',''); fmt=(r.get('format') or '').lower()
        if not url or fmt in ('html','api') or 'datos.gov.py/dataset' in url: 
            W.writerow([slug,r.get('name'),url,'omitido (enlace/html)']); continue
        name=re.sub(r'[\\/:*?"<>|]+','_',(r.get('name') or 'recurso').strip())[:100]
        ext=os.path.splitext(urllib.parse.urlparse(url).path)[1] or ('.'+fmt if fmt else '')
        if not name.lower().endswith(ext.lower()): name+=ext
        out=os.path.join(d,name)
        if os.path.exists(out) and os.path.getsize(out)>0: continue
        try:
            b=get(urllib.parse.quote(url,safe=':/?&=%#'))
            open(out,'wb').write(b); W.writerow([slug,r.get('name'),url,f'ok {len(b)} bytes']); print('   ok',name,len(b))
        except Exception as e:
            W.writerow([slug,r.get('name'),url,f'FALLO {e}']); print('   FAIL',name,url,e)
    log.flush()
