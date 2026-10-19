"""Recorta teselas Ookla Open Data (fijo y móvil) a Paraguay y agrega por distrito (CLAVE INE 4 dígitos).
Uso: python3 -I social_ookla.py <zip_mobile> <zip_fixed> <distritos_geojson> <dir_salida> <etiqueta_periodo>"""
import sys, os
import geopandas as gpd, pandas as pd
zm, zf, dist_path, out, per = sys.argv[1:6]
os.makedirs(out, exist_ok=True)
d = gpd.read_file(dist_path)[["DPTO","DPTO_DESC","DISTRITO","DIST_DESC_","CLAVE","geometry"]].to_crs(4326)
d = d.rename(columns={"DPTO":"cod_dpto","DPTO_DESC":"departamento","DIST_DESC_":"distrito","CLAVE":"cod_dist"}).drop(columns="DISTRITO")
bbox = tuple(d.total_bounds)
res = []
for tipo, z in (("movil", zm), ("fijo", zf)):
    t = gpd.read_file("zip://" + z, bbox=bbox, engine="pyogrio")
    t = t.to_crs(4326)
    c = t.copy(); c["geometry"] = t.geometry.representative_point()
    j = gpd.sjoin(c, d, how="inner", predicate="within").drop(columns=["index_right"])
    t = t.loc[j.index].join(j[["cod_dpto","departamento","cod_dist","distrito"]])
    t["tipo"] = tipo
    t.to_file(os.path.join(out, f"ookla_{tipo}_teselas_PRY_{per}.gpkg"), driver="GPKG")
    df = pd.DataFrame(t.drop(columns="geometry"))
    for v in ("avg_d_kbps","avg_u_kbps","avg_lat_ms"):
        df[v+"_w"] = df[v]*df["tests"]
    g = df.groupby(["cod_dpto","departamento","cod_dist","distrito"]).agg(
        n_teselas=("quadkey","count"), tests=("tests","sum"), devices=("devices","sum"),
        dw=("avg_d_kbps_w","sum"), uw=("avg_u_kbps_w","sum"), lw=("avg_lat_ms_w","sum"),
        mediana_teselas_d_kbps=("avg_d_kbps","median")).reset_index()
    g[f"{tipo}_down_mbps_pond"] = (g.dw/g.tests/1000).round(2)
    g[f"{tipo}_up_mbps_pond"] = (g.uw/g.tests/1000).round(2)
    g[f"{tipo}_lat_ms_pond"] = (g.lw/g.tests).round(1)
    g[f"{tipo}_mediana_teselas_down_mbps"] = (g.mediana_teselas_d_kbps/1000).round(2)
    g = g.drop(columns=["dw","uw","lw","mediana_teselas_d_kbps"]).rename(columns={"n_teselas":f"{tipo}_n_teselas","tests":f"{tipo}_tests","devices":f"{tipo}_devices"})
    res.append(g)
    print(tipo, len(t), "teselas")
base = d.drop(columns="geometry")
for g in res:
    base = base.merge(g, on=["cod_dpto","departamento","cod_dist","distrito"], how="left")
base["periodo"] = per
base.to_csv(os.path.join(out, f"ookla_conectividad_por_distrito_{per}.csv"), index=False, encoding="utf-8")
print(base.head().to_string())
