"""Agrega HREA v1.1 (probabilidad de asentamiento electrificado) por distrito, ponderando por población de asentamiento.
Uso: python3 -I social_hrea_distrito.py <dir_hrea> <distritos_geojson> <csv_salida>"""
import sys, os, gc, numpy as np, pandas as pd, geopandas as gpd
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
d_hrea, dist_path, out = sys.argv[1:4]
def load(name):
    im = Image.open(os.path.join(d_hrea, name)); t = im.tag_v2.get(33922); s = im.tag_v2.get(33550)
    return np.array(im), (t[3], t[4], s[0], s[1])
pop, geo = load("PRY_set_pop.tif")
pop = np.where(np.isfinite(pop), pop, 0)
r, c = np.nonzero(pop > 0); w = pop[r, c].astype("float64"); del pop; gc.collect()
print("pixeles poblados", len(r))
vals = {}
for y in (2013, 2020):
    a, g2 = load(f"PRY_set_prplit_{y}.tif"); assert g2 == geo, (g2, geo)
    v = a[r, c].astype("float64"); v[~np.isfinite(v) | (v < 0)] = np.nan; vals[y] = v; del a; gc.collect()
x0, y0, dx, dy = geo
pts = gpd.GeoDataFrame({"w": w, "p13": vals[2013], "p20": vals[2020]},
                       geometry=gpd.points_from_xy(x0 + (c + 0.5) * dx, y0 - (r + 0.5) * dy), crs=4326)
d = gpd.read_file(dist_path)[["DPTO","CLAVE","DIST_DESC_","geometry"]].to_crs(4326).rename(columns={"DPTO":"cod_dpto","CLAVE":"cod_dist","DIST_DESC_":"distrito"})
j = gpd.sjoin(pts, d, predicate="within", how="inner")
rows = []
for k, g in j.groupby(["cod_dpto","cod_dist","distrito"]):
    row = dict(zip(["cod_dpto","cod_dist","distrito"], k)); row["hrea_pob_asentamiento"] = round(g.w.sum())
    for y, col in ((2013,"p13"),(2020,"p20")):
        m = g[col].notna(); ww = g.w[m]; vv = g[col][m]
        row[f"hrea_prob_electrif_pond_{y}"] = round(float((vv*ww).sum()/ww.sum()), 4) if ww.sum() > 0 else np.nan
        row[f"hrea_pct_pob_prob_ge_0.8_{y}"] = round(float(ww[vv >= 0.8].sum()/ww.sum()*100), 2) if ww.sum() > 0 else np.nan
        row[f"hrea_pob_prob_lt_0.5_{y}"] = round(float(ww[vv < 0.5].sum()))
    rows.append(row)
res = d.drop(columns="geometry").merge(pd.DataFrame(rows), on=["cod_dpto","cod_dist","distrito"], how="left")
res.to_csv(out, index=False); print(res.describe().T.to_string())
