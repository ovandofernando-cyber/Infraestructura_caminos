# Robustez del control de luz nocturna en el análisis por localidad (14_analisis_localidad_2022):
# compara el coeficiente de la distancia sin control de luz, con luz 2013 (principal), con luz 2022 y con ambas,
# y prueba si la luz 2022 responde a la distancia al camino (lo que la haría un "mal control").
import numpy as np, pandas as pd, geopandas as gpd, rasterio, statsmodels.formula.api as smf
from rasterio.mask import mask
R='/home/user/infraestructura_caminos'
b=pd.read_csv(R+'/14_analisis_localidad_2022/base_localidades_2022.csv',dtype={'cod_dist':str,'cod_dpto':str,'bl':str})
g=gpd.read_file(R+'/05_cartografia_y_codigos/COD-AB_OCHA_limites_admin/pry_admin_boundaries.gdb.zip',layer='pry_admin3')[['adm3_pcode','geometry']]
g=g[g.adm3_pcode.isin(b.adm3_pcode)]
with rasterio.open(R+'/07_clima_y_contexto/luces_nocturnas_VIIRS/viirs_vnl_v2_paraguay_2022.tif') as s:
    gg=g.to_crs(s.crs); lz={}
    for pc,geom in zip(gg.adm3_pcode,gg.geometry):
        a,_=mask(s,[geom],crop=True,all_touched=True,filled=False); v=a[0].compressed().astype(float); v=v[v>=0]
        lz[pc]=v.mean() if v.size else np.nan
b['luz_media_2022']=b.adm3_pcode.map(lz)
ORI=['01','02','03','04','05','06','07','08','09','10','12','13','14']
s=b[(b.area=='rural')&b.cod_dpto.isin(ORI)&(b.viviendas_ocupadas>=10)].dropna(subset=['dist_todo_tiempo_km','pct_piso_tierra','luz_media_2013','luz_media_2022','dist_capital_distrito_km']).copy()
z=lambda x:(x-x.mean())/x.std()
s['indice']=pd.concat([z(s.pct_piso_tierra),z(s.pct_cocina_lena),z(s.pct_sin_bienes),z(100-s.pct_electricidad),z(100-s.pct_agua_corriente)],axis=1).mean(axis=1)
s['log_dist']=np.log1p(s.dist_todo_tiempo_km); s['log_dist_cap']=np.log1p(s.dist_capital_distrito_km)
s['log_pob']=np.log(s.poblacion.clip(lower=1)); s['log_area']=np.log(s.area_km2)
s['l13']=np.log1p(s.luz_media_2013); s['l22']=np.log1p(s.luz_media_2022)
base='log_dist + log_pob + log_area + log_dist_cap'
fit=lambda f: smf.wls(f,data=s,weights=s.viviendas_ocupadas).fit(cov_type='cluster',cov_kwds={'groups':s.cod_dist})
rows=[]
for y in ['indice','pct_electricidad','pct_piso_tierra']:
    for lab,extra in [('sin luz',''),('luz 2013',' + l13'),('luz 2022',' + l22'),('ambas',' + l13 + l22')]:
        m=fit(f'{y} ~ {base}{extra} + C(cod_dist)')
        rows.append(dict(resultado=y,control_luz=lab,coef_log_dist=round(m.params['log_dist'],3),ee_cluster=round(m.bse['log_dist'],3),p=m.pvalues['log_dist'],n=int(m.nobs)))
r=fit('l22 ~ log_dist + log_pob + log_area + log_dist_cap + l13 + C(cod_dist)')
rows.append(dict(resultado='log luz 2022 (dada la luz 2013)',control_luz='luz 2013',coef_log_dist=round(r.params['log_dist'],3),ee_cluster=round(r.bse['log_dist'],3),p=r.pvalues['log_dist'],n=int(r.nobs)))
out=pd.DataFrame(rows)
out.to_csv(R+'/14_analisis_localidad_2022/robustez_control_luz.csv',index=False,encoding='utf-8-sig')
print(out.to_string(index=False))
print('corr(log_dist, luz 2013)=%.2f  corr(log_dist, luz 2022)=%.2f'%(s[['log_dist','l13']].corr().iloc[0,1],s[['log_dist','l22']].corr().iloc[0,1]))
