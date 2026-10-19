import pyreadstat, pandas as pd, numpy as np
R='/home/user/repositorio_caminos_vecinales'
out=[]
allp=[]
for y in [2022,2023,2024,2025]:
    f=f'{R}/01_condiciones_de_vida/EPHC_anual/EPHC_{y}_ANUAL/REG02_EPHC_ANUAL_{y}.SAV'
    _,meta=pyreadstat.read_sav(f,metadataonly=True)
    cols=[c for c in ['UPM','DPTO','AREA','FACTOR','pobrezai','ED10','S05','P02','ipcm'] if c in meta.column_names]
    fac=[c for c in meta.column_names if c.upper().startswith('FEX') or c.upper()=='FACTOR']
    if 'FACTOR' not in cols: cols.append(fac[0])
    d,_=pyreadstat.read_sav(f,usecols=cols); d=d.rename(columns={fac[0]:'FACTOR'}); d['anio']=y
    print(y,cols,len(d)); allp.append(d)
p=pd.concat(allp); r=p[p.AREA==6].copy()
r['pobre']=r.pobrezai.isin([1,2]); r['pobre_ext']=r.pobrezai==1
r['noasiste_lejos']=np.where(r.ED10.notna(),(r.ED10==6).astype(float),np.nan)
r['noconsulta_lejos']=np.where(r.S05.notna(),(r.S05==2).astype(float),np.nan)
def wavg(g,c):
    m=g[c].notna(); return np.average(g.loc[m,c],weights=g.loc[m,'FACTOR']) if m.any() else np.nan
lab={0:'ASUNCIÓN',1:'CONCEPCIÓN',2:'SAN PEDRO',3:'CORDILLERA',4:'GUAIRÁ',5:'CAAGUAZÚ',6:'CAAZAPÁ',7:'ITAPÚA',8:'MISIONES',9:'PARAGUARÍ',10:'ALTO PARANÁ',11:'CENTRAL',12:'ÑEEMBUCÚ',13:'AMAMBAY',14:'CANINDEYÚ',15:'PDTE. HAYES',16:'BOQUERÓN',17:'ALTO PARAGUAY'}
rows=[]
for (dp),g in r.groupby('DPTO'):
    rec={'cod_dpto':f'{int(dp):02d}','departamento':lab[int(dp)]}
    g25=g[g.anio==2025]
    rec.update({'ephc2025_rural_n_personas':len(g25),'ephc2025_rural_n_upm':g25.UPM.nunique(),
        'ephc2025_rural_pobreza_pct':round(100*wavg(g25.assign(x=g25.pobre.astype(float)),'x'),1),
        'ephc2025_rural_pobreza_extrema_pct':round(100*wavg(g25.assign(x=g25.pobre_ext.astype(float)),'x'),1),
        'ephc2022_25_rural_n_personas':len(g),
        'ephc2022_25_rural_pobreza_pct':round(100*wavg(g.assign(x=g.pobre.astype(float)),'x'),1),
        'ephc2022_25_noasiste_por_falta_institucion_cercana_pct':round(100*wavg(g,'noasiste_lejos'),1),
        'ephc2022_25_noasiste_n':int(g.noasiste_lejos.notna().sum()),
        'ephc2022_25_noconsulta_por_falta_atencion_cercana_pct':round(100*wavg(g,'noconsulta_lejos'),1),
        'ephc2022_25_noconsulta_n':int(g.noconsulta_lejos.notna().sum())})
    rows.append(rec)
d=pd.DataFrame(rows)
mo=pd.read_csv(f'{R}/03_red_vial_MOPC/MOPC_inventario_km_por_red_y_superficie_dic2025.csv',dtype={'cod_dpto':str})
v=mo[mo.red=='VECINAL'][['cod_dpto','km_total','km_tierra_T']].rename(columns={'km_total':'mopc_km_vecinal_total','km_tierra_T':'mopc_km_vecinal_tierra'})
t=mo[mo.red=='TOTAL'][['cod_dpto','km_total','km_tierra_T']].rename(columns={'km_total':'mopc_km_red_total','km_tierra_T':'mopc_km_red_tierra'})
d=d.merge(v,on='cod_dpto',how='left').merge(t,on='cod_dpto',how='left')
d['mopc_pct_vecinal_tierra']=(100*d.mopc_km_vecinal_tierra/d.mopc_km_vecinal_total).round(1)
b=pd.read_csv(f'{R}/00_base_integrada/base_distrital_integrada.csv',dtype={'cod_dpto':str})
agg=b.groupby('cod_dpto').apply(lambda g: pd.Series({'censo_pob_rural':g.censo_pob_rural.sum(),'censo_pob_total':g.censo_pob_total.sum(),
    'heigit_RAI_pct_ponderado':round(100*g.heigit_pob_rural_a_2km_camino_todo_tiempo.sum()/g.heigit_pob_rural.sum(),1) if g.heigit_pob_rural.sum()>0 else np.nan}))
d=d.merge(agg.reset_index(),on='cod_dpto',how='left')
d['mopc_km_vecinal_por_1000_hab_rurales']=(1000*d.mopc_km_vecinal_total/d.censo_pob_rural).round(2)
d.insert(2,'departamento_foco',d.cod_dpto.isin(['01','02','05','06','14']).map({True:'Sí',False:'No'}))
d.to_csv(f'{R}/00_base_integrada/base_departamental_integrada.csv',index=False,encoding='utf-8-sig')
pd.set_option('display.width',250)
print(d[['departamento','departamento_foco','ephc2025_rural_pobreza_pct','ephc2022_25_rural_pobreza_pct','ephc2022_25_noasiste_por_falta_institucion_cercana_pct','ephc2022_25_noconsulta_por_falta_atencion_cercana_pct','mopc_pct_vecinal_tierra','heigit_RAI_pct_ponderado']].to_string(index=False))
