import pdfplumber, re, glob, os, sys, csv, unicodedata
SRC=sys.argv[1]; OUT1=sys.argv[2]; OUT2=sys.argv[3]; OUT3=sys.argv[4] if len(sys.argv)>4 else OUT2.replace('.csv','_avisos.csv')
import subprocess
MESES={'ENERO':1,'FEBRERO':2,'MARZO':3,'ABRIL':4,'MAYO':5,'JUNIO':6,'JULIO':7,'JULLO':7,'AGOSTO':8,'SETIEMBRE':9,'SEPTIEMBRE':9,'OCTUBRE':10,'NOVIEMBRE':11,'DICIEMBRE':12}
def fecha(txt,fname):
    for s in (txt,fname):
        m=re.search(r'(\d{1,2})\s*(?:DE\s+)?([A-ZÁÉÍÓÚl]+)\s*(?:DEL?\s+)?(20\d\d)',s.upper().replace('JULLO','JULIO'))
        if m and m.group(2).replace('L','L') in MESES: return f"{m.group(3)}-{MESES[m.group(2)]:02d}-{int(m.group(1)):02d}"
    return ''
def lines(page):
    ws=page.extract_words(keep_blank_chars=False,x_tolerance=2,y_tolerance=2)
    rows={}
    for w in ws:
        k=round(w['top']/3)
        rows.setdefault(k,[]).append(w)
    return [sorted(v,key=lambda w:w['x0']) for k,v in sorted(rows.items())]
rows1=[];rows2=[];rows3=[];seen=set()
files=sorted(glob.glob(os.path.join(SRC,'**','*.pdf'),recursive=True))
for f in files:
    try: pdf=pdfplumber.open(f)
    except Exception as e: print('ERR',f,e); continue
    full='\n'.join((p.extract_text() or '') for p in pdf.pages)
    fe=fecha(full,os.path.basename(f))
    key=(fe,len(full))
    if key in seen: pdf.close(); continue   # duplicados "(1)"
    seen.add(key)
    section=None; cols=None; cur=None
    for p in pdf.pages:
        for ln in lines(p):
            text=' '.join(w['text'] for w in ln); up=text.upper()
            if 'PUENTES INHABILITADOS' in up: section='PUENTE'; cols=None; continue
            if 'RUTAS Y TRAMOS CLAUSURADOS' in up: section='RUTA'; cols=None; continue
            if 'ESTADO DEL' in up or 'ESTADO DE LAS' in up: section='LOCALIDADES'; cur=None; continue
            if section in ('PUENTE','RUTA'):
                if 'DPTO' in up and 'ESTADO' in up:
                    cols={}
                    for w in ln:
                        t=w['text'].upper()
                        if t.startswith('DPTO'): cols['dpto']=w['x0']
                        elif t=='TRAMO': cols['tramo']=w['x0']
                        elif t in ('PUENTE','AGUA'): cols['obj']=w['x0']
                        elif t=='ESTADO': cols['estado']=w['x0']
                    continue
                if not cols or 'estado' not in cols: continue
                if re.match(r'^\.?:|Departamento de Radio',text): section=None; continue
                b=sorted(cols.items(),key=lambda kv:kv[1]); bounds=[(k,v-25) for k,v in b]
                def colof(x):
                    c='n'
                    for k,v in bounds:
                        if x>=v: c=k
                    return c
                first=ln[0]
                if re.fullmatch(r'\d{1,3}[°º]?',first['text']) and first['x0']<cols.get('dpto',999)-5:
                    cur={'fecha':fe,'tipo':section,'n':first['text'].rstrip('°º'),'dpto':'','tramo':'','obj':'','estado':'','archivo':os.path.relpath(f,SRC)}
                    rows1.append(cur); ln=ln[1:]
                if cur is None: continue
                for w in ln:
                    c=colof((w['x0']+w['x1'])/2)
                    if c=='n': c='dpto'
                    cur[c]=(cur[c]+' '+w['text']).strip()
            elif section=='LOCALIDADES':
                m=re.search(r'\b(Bueno|Nublado|Lluvioso|Lluvia|Lloviendo|Llovizna|Inestable|Despejado|Tormenta|Malo|Garúa|Neblina)\b',text,re.I)
                s=re.search(r'\b(Habilitad[ao]s?|Clausurad[ao]s?|Restringid[ao]|Precauci[oó]n)\b',text,re.I)
                if m and s:
                    loc=text[:m.start()].strip(' -'); obs=text[s.end():].strip()
                    rows2.append({'fecha':fe,'tramo_ruta':cur or '','localidad':loc,'tiempo':m.group(1).capitalize(),'estado':s.group(1).capitalize(),'observacion':obs,'archivo':os.path.relpath(f,SRC)})
                elif text.upper().startswith(('RUTA','RU ')) or 'RAMAL' in text.upper():
                    cur=re.sub(r'^RU\s+','',text).strip()
    if 'INFORMACIONES DEL MOMENTO' in full.upper():
        txt=subprocess.run(['pdftotext','-layout',f,'-'],capture_output=True,text=True).stdout
        parts=re.split(r'INFORMACIONES DEL MOMENTO',txt,flags=re.I)
        body=parts[-1].split('Departamento de Radiocomunicaciones')[0]
        for para in re.split(r'\n\s*\n',body):
            t=re.sub(r'\s+',' ',para).replace('\uf0b7','').strip()
            if len(t)>25: rows3.append({'fecha':fe,'aviso':t,'archivo':os.path.relpath(f,SRC)})
    pdf.close()
for out,rows,fields in [(OUT1,rows1,['fecha','tipo','n','dpto','tramo','obj','estado','archivo']),(OUT2,rows2,['fecha','tramo_ruta','localidad','tiempo','estado','observacion','archivo']),(OUT3,rows3,['fecha','aviso','archivo'])]:
    with open(out,'w',newline='',encoding='utf-8-sig') as fh:
        w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(rows)
print('archivos',len(files),'informes unicos',len(seen),'filas puentes/rutas',len(rows1),'filas localidades',len(rows2),'avisos',len(rows3))
# --- post-proceso: normaliza departamento y clasifica tipo de restricción y causa
import pandas as pd
DEPS=['ALTO PARAGUAY','ALTO PARANA','PTE. HAYES','PDTE. HAYES','PRESIDENTE HAYES','CONCEPCION','SAN PEDRO','CORDILLERA','GUAIRA','CAAGUAZU','CAAZAPA','ITAPUA','MISIONES','PARAGUARI','CENTRAL','ÑEEMBUCU','NEEMBUCU','AMAMBAY','CANINDEYU','BOQUERON']
def strip_acc(s): return unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().upper() if isinstance(s,str) else ''
d=pd.read_csv(OUT1,dtype=str).fillna('')
def fixdep(r):
    s=strip_acc(r['dpto'])
    for k in sorted(DEPS,key=len,reverse=True):
        kk=strip_acc(k)
        if s.startswith(kk):
            rest=r['dpto'][len(k):].strip()
            return pd.Series({'departamento':{'PDTE. HAYES':'PTE. HAYES','PRESIDENTE HAYES':'PTE. HAYES','NEEMBUCU':'ÑEEMBUCU'}.get(kk,kk),'tramo_completo':(rest+' '+r['tramo']).strip()})
    return pd.Series({'departamento':s,'tramo_completo':r['tramo']})
if len(d):
    d=pd.concat([d,d.apply(fixdep,axis=1)],axis=1)
    d['texto_estado']=(d['obj']+' '+d['estado']).str.strip()
    t=d['texto_estado'].map(strip_acc)
    d['restriccion']=t.map(lambda s:'Todo tipo de vehículos' if 'TODO TIPO' in s else ('Vehículos pesados' if 'PESADO' in s else ('Precaución/reparación' if ('PRECAUCION' in s or 'REPARACION' in s or 'CONSTRUCCION' in s) else 'Otra')))
    d['causa']=t.map(lambda s:'Lluvia' if 'LLUVIA' in s else ('Derrumbe/caída de puente' if ('DERRUMBE' in s or 'DERRUBE' in s or 'CAIDA' in s) else ('Daño estructural' if ('ASENTAMIENTO' in s or 'JUNTA' in s) else ('Obra' if ('CONSTRUCCION' in s or 'REPARACION' in s) else 'No especificada'))))
    d['camino_vecinal_o_compania']=(d['tramo_completo'].map(strip_acc).str.contains(r'\bCIA\b|COMPA|COMPI|COLONIA|ASENTAMIENTO|DISTRITO|RAMAL|VECINAL|MUNICIPIO',regex=True)).map({True:'Probable',False:'No identificado'})
    d=d[['fecha','tipo','n','departamento','tramo_completo','texto_estado','restriccion','causa','camino_vecinal_o_compania','archivo']]
    d['departamento']=d['departamento'].str.replace(r'^PTE, HAYES.*','PTE. HAYES',regex=True)
    d=d.drop_duplicates(subset=['fecha','tipo','departamento','tramo_completo','texto_estado'])
    d.to_csv(OUT1,index=False,encoding='utf-8-sig')
e=pd.read_csv(OUT2,dtype=str)
if len(e):
    e['estado']=e['estado'].str.replace(r'^Habilitado$','Habilitada',regex=True).str.replace(r'^Clausurado$','Clausurada',regex=True)
    e=e.drop_duplicates(subset=['fecha','localidad','tiempo','estado']); e.to_csv(OUT2,index=False,encoding='utf-8-sig')
