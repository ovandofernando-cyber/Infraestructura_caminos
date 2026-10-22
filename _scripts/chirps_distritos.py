# Lluvia CHIRPS v2.0 por distrito (263, límites COD-AB): anual 1991-2024 y 12 meses previos al censo (nov 2021 - oct 2022)
import os, sys, gzip, shutil, subprocess, rasterio, numpy as np, pandas as pd, geopandas as gpd
from rasterio.windows import from_bounds
from rasterio.mask import mask
os.environ.setdefault('CURL_CA_BUNDLE','/root/.ccr/ca-bundle.crt'); os.environ['GDAL_DISABLE_READDIR_ON_OPEN']='EMPTY_DIR'; os.environ['GDAL_HTTP_MAX_RETRY']='5'
R='/home/user/infraestructura_caminos'; OUT=R+'/07_clima_y_contexto/lluvia_CHIRPS_raster'; TMP=sys.argv[1]
os.makedirs(OUT,exist_ok=True)
B=(-62.70,-27.65,-54.20,-19.20); BASE='https://data.chc.ucsb.edu/products/CHIRPS-2.0'
def clip(src_path,out):
    with rasterio.open(src_path) as s:
        w=from_bounds(*B,transform=s.transform).round_offsets().round_lengths()
        a=s.read(1,window=w).astype('float32'); a[a<0]=np.nan
        p=s.profile.copy(); p.update(width=a.shape[1],height=a.shape[0],transform=s.window_transform(w),dtype='float32',nodata=np.nan,compress='deflate'); p.pop('blockxsize',None); p.pop('blockysize',None); p['tiled']=False
        with rasterio.open(out,'w',**p) as d: d.write(a,1)
for y in range(1991,2025):
    out=f'{OUT}/chirps_anual_{y}.tif'
    if not os.path.exists(out): clip(f'/vsicurl/{BASE}/global_annual/tifs/chirps-v2.0.{y}.tif',out)
for ym in [f'2021.{m:02d}' for m in (11,12)]+[f'2022.{m:02d}' for m in range(1,11)]:
    out=f'{OUT}/chirps_mensual_{ym.replace(".","_")}.tif'
    if os.path.exists(out): continue
    gz=f'{TMP}/chirps-v2.0.{ym}.tif.gz'
    subprocess.run(['curl','-sS','-L','--retry','4','-m','900','-o',gz,f'{BASE}/global_monthly/tifs/chirps-v2.0.{ym}.tif.gz'],check=True)
    tif=gz[:-3]
    with gzip.open(gz,'rb') as fi, open(tif,'wb') as fo: shutil.copyfileobj(fi,fo)
    clip(tif,out); os.remove(gz); os.remove(tif)
    print('mes',ym,flush=True)
g=gpd.read_file(R+'/05_cartografia_y_codigos/COD-AB_OCHA_limites_admin/pry_admin_boundaries.gdb.zip',layer='pry_admin2')[['adm2_pcode','geometry']]
g['cod_dist']=g.adm2_pcode.str[2:]
def zonal(path):
    with rasterio.open(path) as s:
        gg=g.to_crs(s.crs); res={}
        for _,r in gg.iterrows():
            a,_=mask(s,[r.geometry],crop=True,all_touched=True,filled=True,nodata=np.nan)
            res[r.cod_dist]=float(np.nanmean(a)) if np.isfinite(a).any() else np.nan
    return res
rows=[]
for y in range(1991,2025):
    for k,v in zonal(f'{OUT}/chirps_anual_{y}.tif').items(): rows.append(dict(cod_dist=k,anio=y,lluvia_mm=round(v,1)))
an=pd.DataFrame(rows); an.to_csv(OUT+'/lluvia_anual_por_distrito_1991_2024.csv',index=False,encoding='utf-8-sig')
m=None
for f in sorted(x for x in os.listdir(OUT) if x.startswith('chirps_mensual_')):
    z=pd.Series(zonal(f'{OUT}/{f}')); m=z if m is None else m+z
pre=m.rename('lluvia_12m_precenso_mm').round(1).reset_index().rename(columns={'index':'cod_dist'})
pre.to_csv(OUT+'/lluvia_nov2021_oct2022_por_distrito.csv',index=False,encoding='utf-8-sig')
print(an.groupby('anio').lluvia_mm.mean().round(0).to_dict()); print(pre.describe().round(0))
