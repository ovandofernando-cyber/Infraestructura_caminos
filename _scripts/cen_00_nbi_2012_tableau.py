# Paso 0 del análisis censal: NBI 2012 por distrito (porcentaje de hogares con al menos una NBI, Censo 2012).
# El INE lo publica solo como mapa de Tableau Public (https://www.ine.gov.py/vt/Porcentaje-de-hogares-con-al-menos-una-NBI.php).
# Este script baja el libro (.twbx), lee su extracto de datos (.hyper) y guarda la tabla y los límites distritales de 2012.
# Uso: python3 -I cen_00_nbi_2012_tableau.py <carpeta de trabajo vacía>   (requiere: pip install tableauhyperapi)
import sys, glob, zipfile, subprocess, pandas as pd, geopandas as gpd
from shapely import wkt
from tableauhyperapi import HyperProcess, Telemetry, Connection

R = '/home/user/infraestructura_caminos'
D = R + '/12_INE_complementario/NBI_distrital_2012_2022'
W = sys.argv[1]
WB = 'ParaguayDistrital-AlmenosunanecesidadBasicaInsatisfecha-Censo2012'
twbx = D + '/Tableau_INE_NBI_distrital_Censo2012.twbx'
subprocess.run(['curl', '-sS', '-L', '-m', '300', '-o', twbx, f'https://public.tableau.com/workbooks/{WB}.twb'], check=True)
zipfile.ZipFile(twbx).extractall(W)
hyper = glob.glob(W + '/Data/TableauTemp/*.hyper')[0]
with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hp, Connection(hp.endpoint, hyper) as c:
    rows = c.execute_list_query('SELECT "CLAVE", "DPTO", "DPTO_DESC", "DIST_DESC", "nbi", CAST("Geometry" AS TEXT) FROM "Extract"."Extract"')
d = pd.DataFrame(rows, columns=['cod_dist_2012', 'cod_dpto', 'departamento', 'distrito', 'nbi_al_menos_una_pct_2012', 'wkt'])
d.drop(columns='wkt').to_csv(D + '/nbi_2012_distrital.csv', index=False, encoding='utf-8-sig')
gpd.GeoDataFrame(d[['cod_dist_2012']], geometry=d.wkt.map(wkt.loads), crs=4326).to_file(D + '/distritos_2012_limites.gpkg', driver='GPKG')
# Cuadro 2022 (mismo indicador y componentes), INE documento 262
subprocess.run(['curl', '-sS', '-L', '-m', '300', '-o', D + '/Hogares_por_NBI_segun_departamento_y_distrito_2022_INE.xlsx',
                'https://www.ine.gov.py/assets/documento/262/Paraguay.%20Hogares%20por%20Necesidades%20B%C3%A1sicas%20Insatisfechas%20(NBI)'
                '%20seg%C3%BAn%20departamento%20y%20distrito,%202022.xlsx'], check=True)
print(len(d), 'distritos 2012')
