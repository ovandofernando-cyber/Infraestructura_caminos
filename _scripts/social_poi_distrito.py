"""Cuenta puntos de interés institucionales (OSM/HOT) por distrito.
Uso: python3 -I social_poi_distrito.py <gpkg_zip> <distritos_geojson> <csv_salida>"""
import sys, zipfile, geopandas as gpd, pandas as pd, pyogrio
z, dist_path, out = sys.argv[1:4]
name = [n for n in zipfile.ZipFile(z).namelist() if n.endswith('.gpkg')][0]
src = f"/vsizip/{z}/{name}"
layers = pyogrio.list_layers(src); print(layers)
parts = []
for lyr, _ in layers:
    g = gpd.read_file(src, layer=lyr)
    g["geometry"] = g.geometry.representative_point()
    parts.append(g)
g = pd.concat(parts, ignore_index=True); g = gpd.GeoDataFrame(g, crs=parts[0].crs).to_crs(4326)
print(g.columns.tolist()); print(g["amenity"].value_counts().head(60).to_string())
d = gpd.read_file(dist_path)[["DPTO","CLAVE","DIST_DESC_","geometry"]].to_crs(4326).rename(columns={"DPTO":"cod_dpto","CLAVE":"cod_dist","DIST_DESC_":"distrito"})
j = gpd.sjoin(g, d, predicate="within", how="left")
cats = {"police":"comisaria_policia","townhall":"municipalidad","courthouse":"juzgado","post_office":"correo",
        "marketplace":"mercado","bank":"banco","atm":"cajero","fuel":"estacion_servicio","pharmacy":"farmacia",
        "bus_station":"terminal_omnibus","community_centre":"centro_comunitario","place_of_worship":"templo",
        "fire_station":"bomberos","social_facility":"servicio_social","library":"biblioteca","drinking_water":"agua_potable_punto",
        "water_point":"agua_potable_punto","public_building":"edificio_publico"}
j["cat"] = j["amenity"].map(cats)
mm = j.get("man_made")
if mm is not None:
    j.loc[j["cat"].isna() & mm.isin(["water_tower","water_well","water_works","reservoir_covered","storage_tank"]), "cat"] = "infra_agua"
    j.loc[j["cat"].isna() & mm.isin(["mast","tower","communications_tower"]), "cat"] = "torre_antena"
t = j.dropna(subset=["cat","cod_dist"]).pivot_table(index=["cod_dpto","cod_dist","distrito"], columns="cat", values="osm_id" if "osm_id" in j else j.columns[0], aggfunc="count", fill_value=0).reset_index()
base = d.drop(columns="geometry").merge(t, on=["cod_dpto","cod_dist","distrito"], how="left").fillna(0)
base.columns.name = None
base.to_csv(out, index=False)
print(base.describe().T.to_string())
