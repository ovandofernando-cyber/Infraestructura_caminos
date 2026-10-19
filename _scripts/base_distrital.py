import pandas as pd, numpy as np, unicodedata, re, glob, difflib, os
R='/home/user/repositorio_caminos_vecinales'
def norm(s):
    s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower()
    s=re.sub(r"^departamento\s+|^dpto\.?\s*","",s.strip()); s=re.sub(r"[^a-z0-9 ]"," ",s); return re.sub(r"\s+"," ",s).strip()
# --- códigos INE 2022
c=pd.read_excel(f'{R}/05_cartografia_y_codigos/codigos_geograficos_INE_2022/Codigos de distritos INE 2022.xlsx',header=2,dtype=str)
c.columns=[str(x).strip() for x in c.columns]
print(c.columns.tolist())
codcol=[k for k in c.columns if 'CÓDIGO' in k.upper() or 'CODIGO' in k.upper()][0]
depcol=[k for k in c.columns if 'DEPART' in k.upper() and 'COD' not in k.upper()][0]
c=c[c[codcol].str.fullmatch(r'\d{4}',na=False)].copy()
c['cod_dist']=c[codcol]; c['cod_dpto']=c[codcol].str[:2]; c['distrito']=c['DISTRITO'].str.strip(); c['departamento']=c[depcol].str.strip()
base=c[['cod_dpto','departamento','cod_dist','distrito']].reset_index(drop=True)
deps={norm(d):k for k,d in zip(base.cod_dpto,base.departamento)}
deps.update({'asuncion':'00','pdte hayes':'15','presidente hayes':'15','neembucu':'12'})
def match(dpto,name):
    cand=base[base.cod_dpto==dpto]
    n=norm(name); names={norm(x):k for x,k in zip(cand.distrito,cand.cod_dist)}
    if n in names: return names[n]
    m=difflib.get_close_matches(n,list(names),n=1,cutoff=0.6)
    return names[m[0]] if m else None
def parse_ine(path,cols,start_col=1,skip_total=True):
    df=pd.read_excel(path,header=None)
    out=[]; dpto=None; unmatched=[]
    for _,r in df.iterrows():
        name=r.iloc[start_col]
        if pd.isna(name): continue
        raw=[r.iloc[start_col+1+i] for i in range(len(cols))]
        vals=[v if isinstance(v,(int,float,np.number)) and not pd.isna(v) else np.nan for v in raw]
        nn=norm(name)
        if all(pd.isna(v) for v in vals):
            if nn in deps: dpto=deps[nn]
            continue
        if str(name).strip().lower().startswith('departamento') and nn in deps:
            dpto=deps[nn]; continue
        if nn=='asuncion': dpto='00'
        if dpto is None: continue
        if nn in ('total pais','paraguay'): continue
        code=match(dpto,name)
        if code is None: unmatched.append((dpto,name)); continue
        out.append(dict(cod_dist=code,**{c:v for c,v in zip(cols,vals)}))
    o=pd.DataFrame(out).drop_duplicates('cod_dist')
    if unmatched: print('  sin match',os.path.basename(path)[:50],unmatched[:10])
    return o
P=f'{R}/01_condiciones_de_vida/pobreza_tabulados_INE/'
H=parse_ine(P+'Paraguay. Incidencia de la Pobreza (H), por área según distrito. Censo 2022.xlsx',['ipm_H_total','ipm_H_urbana','ipm_H_rural'])
A=parse_ine(P+'Paraguay. Intensidad de la Pobreza entre los Pobres (A), por área según distrito. Censo 2022.xlsx',['ipm_A_total','ipm_A_urbana','ipm_A_rural'])
M=parse_ine(glob.glob(P+'Paraguay. Tasa de*Recuento Ajustada*distrito*.xlsx')[0],['ipm_M0_total','ipm_M0_urbana','ipm_M0_rural'])
N=parse_ine(P+'Paraguay. Hogares por Necesidades Básicas Insatisfechas (NBI) según departamento y distrito, 2022.xlsx',['hogares_total','nbi_al_menos_una_pct','nbi_vivienda_pct','nbi_sanitaria_pct','nbi_educacion_pct','nbi_subsistencia_pct'])
for n,d in [('H',H),('A',A),('M0',M),('NBI',N)]: print(n,len(d))
b=base.merge(H,on='cod_dist',how='left').merge(A,on='cod_dist',how='left').merge(M,on='cod_dist',how='left').merge(N,on='cod_dist',how='left')
# población urbana/rural censo (Cuadro A1)
f=glob.glob(f'{R}/02_censo_2022/**/Cuadro A1. Paraguay. Población total por área urbana-rural*.csv',recursive=True)
if f:
    p=pd.read_csv(f[0],encoding='utf-8-sig',sep=None,engine='python',header=None)
    p.to_csv('/tmp/claude-0/-home-user/70bda30c-a055-5a28-a201-438e8c2e241e/scratchpad/a1_raw.csv',index=False)
    print('A1 shape',p.shape); print(p.head(8).to_string()[:1500])
    rows=[];dp=None
    for _,r in p.iloc[1:].iterrows():
        nm=str(r[0]).strip(); nn=norm(nm)
        num=lambda v: np.nan if str(v).strip() in ('-','','nan') else float(str(v).replace('.','').strip())
        if nm.lower().startswith('departamento'):
            dp=f'{(int(dp)+1 if dp else 1):02d}'  # por orden: el Cuadro A1 rotula mal Cordillera como 'Concepcion'
            if nn in deps and deps[nn]!=dp: print('  aviso A1: encabezado',nm,'-> asignado',dp)
            continue
        if nn in ('total pais',): continue
        if nn=='asuncion': dp='00'
        if dp is None: continue
        code=match(dp,nm)
        if code: rows.append(dict(cod_dist=code,censo_pob_total=num(r[1]),censo_pob_urbana=num(r[2]),censo_pob_rural=num(r[3])))
    pa=pd.DataFrame(rows).drop_duplicates('cod_dist'); print('A1 matched',len(pa))
    pa['censo_pct_rural']=(100*pa.censo_pob_rural.fillna(0)/pa.censo_pob_total).round(1)
    b=b.merge(pa,on='cod_dist',how='left')
# HeiGIT
Hg=f'{R}/03_red_vial_MOPC/HeiGIT_indicadores_distritales_RAI_accesibilidad/'
rai=pd.read_csv(Hg+'PRY_ADM2_rai.csv')[['ADM2_PCODE','rural_access_total_pop','RAI_total_pop']]
rur=pd.read_csv(Hg+'PRY_ADM2_rural_population.csv')[['ADM2_PCODE','total_pop_rural','rural_pop_perc']]
acc=pd.read_csv(Hg+'PRY_ADM2_access.csv').drop(columns=['ADM_PCODE'])
dem=pd.read_csv(Hg+'PRY_ADM2_demographics.csv')[['ADM2_PCODE','total_pop']]
fac=pd.read_csv(Hg+'PRY_ADM2_facilities.csv').drop(columns=['ADM_PCODE'])
hg=dem.merge(rur,on='ADM2_PCODE',how='outer').merge(rai,on='ADM2_PCODE',how='outer').merge(acc,on='ADM2_PCODE',how='outer').merge(fac,on='ADM2_PCODE',how='outer')
hg['cod_dist']=hg.ADM2_PCODE.str[2:]
for k in [x for x in acc.columns if x.startswith('access_pop')]:
    hg[k.replace('access_pop','pct_pob_acceso')]=(100*hg[k]/hg.total_pop).round(1)
hg=hg.rename(columns={'total_pop':'heigit_pob_total_worldpop','total_pop_rural':'heigit_pob_rural','rural_pop_perc':'heigit_pct_rural','rural_access_total_pop':'heigit_pob_rural_a_2km_camino_todo_tiempo','RAI_total_pop':'RAI_pct'})
print('HeiGIT districts',len(hg),'matched to INE',hg.cod_dist.isin(base.cod_dist).sum())
b=b.merge(hg.drop(columns=['ADM2_PCODE']),on='cod_dist',how='left')
# MOPC por departamento (red vecinal)
mo=pd.read_csv(f'{R}/03_red_vial_MOPC/MOPC_inventario_km_por_red_y_superficie_dic2025.csv',dtype={'cod_dpto':str})
v=mo[mo.red=='VECINAL'].copy()
v['dpto_km_vecinal_total']=v.km_total; v['dpto_pct_vecinal_tierra']=(100*v.km_tierra_T/v.km_total).round(1)
v['dpto_km_vecinal_todo_tiempo']=v.km_total-v.km_tierra_T
b=b.merge(v[['cod_dpto','dpto_km_vecinal_total','dpto_km_vecinal_todo_tiempo','dpto_pct_vecinal_tierra']],on='cod_dpto',how='left')
FOCO={'01','02','05','06','14'}
b.insert(4,'departamento_foco',b.cod_dpto.isin(FOCO).map({True:'Sí',False:'No'}))
out=f'{R}/00_base_integrada/base_distrital_integrada.csv'; os.makedirs(os.path.dirname(out),exist_ok=True)
b.to_csv(out,index=False,encoding='utf-8-sig')
print(b.shape); print(b.isna().sum()[b.isna().sum()>0])
print(b[b.departamento_foco=='Sí'][['distrito','ipm_H_rural','nbi_al_menos_una_pct','RAI_pct','pct_pob_acceso_primary_healthcare_30min']].describe().round(1))
