import geopandas as gpd, rasterio, numpy as np, pandas as pd
from rasterio.mask import mask
R='/home/user/infraestructura_caminos'
D=R+'/07_clima_y_contexto/luces_nocturnas_VIIRS/'
g=gpd.read_file(R+'/05_cartografia_y_codigos/COD-AB_OCHA_limites_admin/pry_admin_boundaries.gdb.zip',layer='pry_admin2')[['adm2_pcode','adm2_name','adm1_name','geometry']]
g['cod_dist']=g.adm2_pcode.str[2:]
rows=[]
for y in range(2012,2025):
    with rasterio.open(D+f'viirs_vnl_v2_paraguay_{y}.tif') as s:
        gg=g.to_crs(s.crs)
        for _,r in gg.iterrows():
            a,_=mask(s,[r.geometry],crop=True,filled=False)
            v=a[0].compressed().astype(float); v=v[v>=0]
            rows.append(dict(cod_dist=r.cod_dist,distrito=r.adm2_name,departamento=r.adm1_name,anio=y,
                luz_suma=float(v.sum()),luz_media=round(float(v.mean()),3) if v.size else np.nan,
                pct_pixeles_iluminados=round(100*float((v>0).mean()),2) if v.size else np.nan,
                n_pixeles=int(v.size),luz_max=float(v.max()) if v.size else np.nan))
    print(y,flush=True)
d=pd.DataFrame(rows).sort_values(['cod_dist','anio'])
d.to_csv(D+'luces_nocturnas_por_distrito_2012_2024.csv',index=False,encoding='utf-8-sig')
w=d.pivot(index='cod_dist',columns='anio',values='luz_suma')
print(d.groupby('anio').luz_suma.sum().round(0).to_dict())
print(len(d.cod_dist.unique()),'distritos')
