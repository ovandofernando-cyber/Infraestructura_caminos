# Análisis de impacto de los 11 tramos BID (ver 25_impacto_tramos_bid/PLAN_DE_ANALISIS.md), paso 1: segmentos de 5 km,
# franjas rurales de 2 km, controles de OpenStreetMap emparejados y luz nocturna anual 2012-2024 (VIIRS VNL v2).
import sys, numpy as np, pandas as pd, geopandas as gpd, pyogrio, rasterio
from rasterio.features import geometry_mask
from rasterio.windows import from_bounds
from shapely.geometry import LineString, MultiLineString
from shapely.ops import substring

R = '/home/user/infraestructura_caminos'; OUT = R + '/25_impacto_tramos_bid'
OSM = sys.argv[1]
GDB = R + '/05_cartografia_y_codigos/COD-AB_OCHA_limites_admin/pry_admin_boundaries.gdb.zip'
D6 = ['02', '03', '05', '06', '07', '14']
rng = np.random.default_rng(2026)
ANIOS = range(2012, 2025)


def cortar(line, largo=5000, minimo=0):
    n = max(1, int(np.ceil(line.length / largo)))
    return [substring(line, i * line.length / n, (i + 1) * line.length / n) for i in range(n) if line.length / n >= minimo]


# ---------------- Tratados ----------------
t = gpd.read_file(R + '/11_infraestructura_vial_complementaria/BID_tramos_intervenidos_1084_1092/tramos_intervenidos_BID_1084_1092.gpkg')
fh = pd.to_datetime(t.fecha_habilitacion)
t['cohorte'] = np.where(fh.dt.month == 12, fh.dt.year + 1, fh.dt.year)
seg = []
for r in t.itertuples():
    partes = list(r.geometry.geoms) if isinstance(r.geometry, MultiLineString) else [r.geometry]
    for p in partes:
        for s in cortar(p):
            seg.append(dict(tipo='T', tramo=r.orden, cohorte=r.cohorte, departamento=r.departamento, geometry=s))
T = gpd.GeoDataFrame(seg, crs=32721)
dep = gpd.read_file(GDB, layer='pry_admin1')[['adm1_pcode', 'geometry']].to_crs(32721); dep['cod_dpto'] = dep.adm1_pcode.str[2:]
T['cod_dpto'] = gpd.sjoin(gpd.GeoDataFrame(geometry=T.representative_point(), crs=32721), dep, predicate='within').cod_dpto.reindex(T.index).values
print('Segmentos tratados:', len(T), T.groupby('cohorte').size().to_dict())

# ---------------- Controles candidatos (OSM) ----------------
o = pyogrio.read_dataframe(OSM, columns=['highway'], where="highway IN ('tertiary','unclassified','track')").to_crs(32721)
o = o[o.length >= 2000].explode(index_parts=False)
o = o[o.geom_type == 'LineString']
pts = gpd.GeoDataFrame(geometry=o.representative_point(), crs=32721)
o['cod_dpto'] = gpd.sjoin(pts, dep, predicate='within').cod_dpto.reindex(o.index).values
o = o[o.cod_dpto.isin(D6)]
lejos = t.buffer(10000).union_all()
otras = gpd.read_file(R + '/18_tramos_georreferenciados/tramos_obras_vecinales_MOPC_2012_2025.gpkg').to_crs(32721)
otras = otras[otras.geometry.notna()].buffer(5000).union_all()
o = o[~o.intersects(lejos) & ~o.intersects(otras)]
C = []
for r in o.itertuples():
    for s in cortar(r.geometry, minimo=2000):
        C.append(dict(tipo='C', tramo=np.nan, cohorte=np.nan, cod_dpto=r.cod_dpto, geometry=s))
C = gpd.GeoDataFrame(C, crs=32721)
C = pd.concat([g.sample(min(len(g), 1500), random_state=2026) for _, g in C.groupby('cod_dpto')])
print('Controles candidatos:', len(C), C.cod_dpto.value_counts().to_dict())

# ---------------- Franjas rurales y luz ----------------
U = pd.concat([T, C], ignore_index=True)
U['id'] = [f'{a}{i:05d}' for i, a in enumerate(U.tipo)]
adm3 = gpd.read_file(GDB, layer='pry_admin3')[['adm3_pcode', 'geometry']].to_crs(32721)
urb = adm3[adm3.adm3_pcode.str[6] == '1'].union_all()
U['franja'] = U.buffer(2000, cap_style='flat').difference(urb)
U['area_km2'] = U.franja.area / 1e6
F = gpd.GeoSeries(U.franja, crs=32721).to_crs(4326)
luz = {}
with rasterio.open(f'{R}/07_clima_y_contexto/luces_nocturnas_VIIRS/viirs_vnl_v2_paraguay_2012.tif') as s0:
    tr, shape = s0.transform, s0.shape
ventanas = []
for g in F:
    w = from_bounds(*g.bounds, transform=tr).round_offsets().round_lengths()
    w = w.intersection(rasterio.windows.Window(0, 0, shape[1], shape[0]))
    wt = rasterio.windows.transform(w, tr)
    m = ~geometry_mask([g], out_shape=(int(w.height), int(w.width)), transform=wt, all_touched=False)
    ventanas.append((w, m))
for y in ANIOS:
    with rasterio.open(f'{R}/07_clima_y_contexto/luces_nocturnas_VIIRS/viirs_vnl_v2_paraguay_{y}.tif') as s:
        a = s.read(1).astype(float); a[a == s.nodata] = 0; a[a < 0] = 0
    luz[y] = [a[int(w.row_off):int(w.row_off + w.height), int(w.col_off):int(w.col_off + w.width)][m].mean() if m.sum() else np.nan
              for w, m in ventanas]
L = pd.DataFrame(luz); L['id'] = U.id.values; L['n_pixeles'] = [m.sum() for _, m in ventanas]
P = L.melt(id_vars=['id', 'n_pixeles'], var_name='anio', value_name='luz_media').merge(U.drop(columns=['geometry', 'franja']), on='id')
P['y'] = np.log1p(P.luz_media)
P = P[P.n_pixeles >= 5]

# ---------------- Emparejamiento: 5 controles por segmento tratado, mismo departamento, luz 2014-2016 parecida ----------------
base = P[P.anio.between(2014, 2016)].groupby('id').y.mean()
U['base'] = U.id.map(base)
tt = U[(U.tipo == 'T') & U.base.notna()].sample(frac=1, random_state=2026)
libres = U[(U.tipo == 'C') & U.base.notna()].copy(); par = {}
for r in tt.itertuples():
    cand = libres[libres.cod_dpto == r.cod_dpto]
    if len(cand) < 5: cand = libres
    elegidos = (cand.base - r.base).abs().nsmallest(5).index
    for i in elegidos: par[U.at[i, 'id']] = r.id
    libres = libres.drop(elegidos)
U['pareja_de'] = U.id.map(par)
U.loc[U.tipo == 'T', 'pareja_de'] = U.id
ids = set(U[U.tipo == 'T'].id) | set(par)
P = P[P.id.isin(ids)].merge(U[['id', 'pareja_de', 'base']], on='id')
seg_tramo = U.set_index('id').tramo
P['tramo_cluster'] = P.pareja_de.map(seg_tramo)               # cada control se agrupa con el tramo de su segmento tratado
P['cohorte_pareja'] = P.pareja_de.map(U.set_index('id').cohorte)
P.to_csv(OUT + '/panel_luces_segmentos_2012_2024.csv', index=False, encoding='utf-8-sig')
g = gpd.GeoDataFrame(U[U.id.isin(ids)].drop(columns=['franja']), geometry='geometry', crs=32721)
g.to_file(OUT + '/segmentos_tratados_y_controles.gpkg', driver='GPKG')
print('Panel:', P.id.nunique(), 'unidades;', P[P.tipo == 'T'].id.nunique(), 'tratadas;', P[P.tipo == 'C'].id.nunique(), 'controles')
print(P.groupby(['tipo']).base.describe().round(3))
