"""Baja capas del geoportal del INE (GeoNode, WFS) y las resume por distrito INE 2022.

Uso: python3 -I _scripts/social_ine_geoportal.py <raiz_repo> [<dir_geojson_ya_bajados>]
Capas de puntos (locales educativos, puestos de salud públicos, antenas, tanques de agua) y polígonos de
comunidades indígenas; todas traen DPTO + DISTRITO del marco censal 2022 (cod_dist = DPTO+DISTRITO; Asunción = 0000).
AREA: 1 urbana, 3 suburbana, 6 rural (marco censal). Licencia: dominio público (INE).
Al final baja sin geometría los indicadores del Censo 2022 por barrio/localidad y por distrito (12_INE_complementario).
"""
import os, re, sys, urllib.parse, urllib.request
import pandas as pd, geopandas as gpd

raiz = sys.argv[1]
cache = sys.argv[2] if len(sys.argv) > 2 else None
WFS = ("https://geonode.ine.gov.py/geoserver/ows?service=WFS&version=2.0.0&request=GetFeature"
       "&outputFormat=application/json&srsName=EPSG:4326&typeNames=geonode:")
OUT = os.path.join(raiz, "09_servicios_complementarios", "INE_geoportal_capas")
CAPAS = {  # capa GeoNode -> (archivo de salida, columnas dpto/distrito/área)
    "COMUNIDADES_INDIGENAS0": ("comunidades_indigenas_INE_2022", ("DPTO", "DISTRITO", "AREA")),
    "locales_educativos_da62455ff56a5b7ea3495ede81a25ef9": ("locales_educativos_INE", ("dpto", "distrito", "area")),
    "puestos_salud_publicos": ("puestos_salud_publicos_INE", ("dpto", "distrito", "area")),
    "Antenas_de_Telecomunicaciones": ("antenas_telecomunicaciones_INE", ("Dpto", "Distrito", "Area")),
    "Tanques_de_agua": ("tanques_agua_juntas_saneamiento_INE", ("Dpto", "Distrito", "Area")),
}
os.makedirs(OUT, exist_ok=True)
resumen = []
for capa, (nombre, (cd, cdi, ca)) in CAPAS.items():
    src = os.path.join(cache, capa + ".geojson") if cache else None
    if not (src and os.path.exists(src)):
        src = os.path.join(OUT, capa + ".geojson")
        urllib.request.urlretrieve(WFS + capa, src)
    g = gpd.read_file(src)
    g["cod_dist"] = (g[cd].str.zfill(2) + g[cdi].str.zfill(2)).where(g[cd] != "00", "0000")
    g["area_censal"] = g[ca]
    g.to_file(os.path.join(OUT, nombre + ".gpkg"), driver="GPKG")
    if g.geom_type.iloc[0] == "Point":
        t = g.drop(columns="geometry").assign(lon=g.geometry.x.round(6), lat=g.geometry.y.round(6))
        t.to_csv(os.path.join(OUT, nombre + ".csv"), index=False)
    if src.startswith(OUT):
        os.remove(src)
    n = g.groupby("cod_dist").size().rename(f"n_{nombre}")
    n_rural = g[g["area_censal"] == "6"].groupby("cod_dist").size().rename(f"n_{nombre}_rural")
    resumen += [n, n_rural]
    print(nombre, len(g))

g = gpd.read_file(os.path.join(OUT, "locales_educativos_INE.gpkg"))
resumen.append(g[g["desccodref"] == "PUBLICO"].groupby("cod_dist").size().rename("n_locales_educativos_publicos"))
g = gpd.read_file(os.path.join(OUT, "tanques_agua_juntas_saneamiento_INE.gpkg"))
resumen.append(g[g["DescRef"].str.contains("JUNTA|COMISION|COMUNITAR", na=False)].groupby("cod_dist").size()
               .rename("n_juntas_comisiones_tanques_comunitarios"))
r = pd.concat(resumen, axis=1).fillna(0).astype(int).sort_index()
r.index.name = "cod_dist"
r.reset_index().to_csv(os.path.join(OUT, "INE_geoportal_por_distrito.csv"), index=False)
print(len(r), "distritos")

# --- Indicadores del Censo 2022 (solo atributos; los diccionarios son los xlsx del geoportal) ---
OUT12 = os.path.join(raiz, "12_INE_complementario", "Censo_2022_indicadores_localidad")
os.makedirs(OUT12, exist_ok=True)
BASE = "https://geonode.ine.gov.py/geoserver/ows?"
for capa, nombre in (("barloc_absoluto_16_12_25", "censo2022_indicadores_barrio_localidad"),
                     ("distritos_con_indicadores_censo_2022_2", "censo2022_indicadores_distrito")):
    x = urllib.request.urlopen(BASE + urllib.parse.urlencode({"service": "WFS", "version": "2.0.0", "request": "DescribeFeatureType",
                                                              "typeNames": "geonode:" + capa}), timeout=120).read().decode()
    props = [p for p in re.findall(r'name="([^"]+)"', x) if not p.endswith("Type") and p not in ("geometry", capa)]
    q = {"service": "WFS", "version": "2.0.0", "request": "GetFeature", "outputFormat": "csv",
         "typeNames": "geonode:" + capa, "propertyName": ",".join(props)}
    urllib.request.urlretrieve(BASE + urllib.parse.urlencode(q), os.path.join(OUT12, nombre + ".csv"))
for dic in ("Diccionario_de_Variables.xlsx", "Diccionario_Distritos.xlsx"):
    urllib.request.urlretrieve("https://portalgeoestad.ine.gov.py/geoportal/" + dic, os.path.join(OUT12, dic))
