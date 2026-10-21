import os, sys, rasterio
from rasterio.windows import from_bounds
os.environ.setdefault('CURL_CA_BUNDLE','/root/.ccr/ca-bundle.crt')
os.environ['GDAL_HTTP_MAX_RETRY']='5'; os.environ['GDAL_HTTP_RETRY_DELAY']='3'; os.environ['GDAL_DISABLE_READDIR_ON_OPEN']='EMPTY_DIR'
OUT=sys.argv[1]; years=[int(y) for y in sys.argv[2:]] or list(range(2012,2025))
B=(-62.70,-27.65,-54.20,-19.20)  # Paraguay + margen
os.makedirs(OUT,exist_ok=True)
for y in years:
    fn=f'nightlights.average_viirs.v21_m_500m_s_{y}0101_{y}1231_go_epsg4326_v20250904.tif'
    out=os.path.join(OUT,f'viirs_vnl_v2_paraguay_{y}.tif')
    if os.path.exists(out): print('ya existe',y); continue
    url=f'/vsicurl/https://zenodo.org/api/records/17294744/files/{fn}/content'
    with rasterio.open(url) as src:
        w=from_bounds(*B,transform=src.transform).round_offsets().round_lengths()
        a=src.read(1,window=w); prof=src.profile.copy()
        prof.update(width=a.shape[1],height=a.shape[0],transform=src.window_transform(w),compress='deflate',tiled=True,blockxsize=256,blockysize=256)
        prof.pop('photometric',None)
        with rasterio.open(out,'w',**prof) as dst: dst.write(a,1)
    print(y,a.shape,a.dtype,'max',a.max(),'nodata',prof.get('nodata'),flush=True)
