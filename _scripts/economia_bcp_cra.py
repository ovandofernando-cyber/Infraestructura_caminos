"""Pasa a formato largo el PIB departamental del Anexo Estadístico CRA 2021-2024 (BCP).
Uso: python3 -I _scripts/economia_bcp_cra.py <raiz_repo>
Salida: 10_economia_y_mercados/BCP_cuentas_regionales/pib_departamental_2021_2024.csv
"""
import csv, os, sys
import openpyxl

raiz = sys.argv[1] if len(sys.argv) > 1 else "."
carpeta = os.path.join(raiz, "10_economia_y_mercados", "BCP_cuentas_regionales")
wb = openpyxl.load_workbook(os.path.join(carpeta, "Anexo_Estadistico_CRA_2021_2024.xlsx"), read_only=True, data_only=True)
ANIOS = {2021: 2, 2022: 4, 2023: 7, 2024: 10}  # columna del valor de cada año
datos = {}
for hoja, var in (("PIB_corriente", "pib_corriente_mill_gs"), ("PIB_constante", "pib_constante2014_mill_gs")):
    for fila in wb[hoja].iter_rows(values_only=True):
        cod = str(fila[0]).strip() if fila[0] is not None else ""
        if not (cod.isdigit() and int(cod) <= 17):
            continue
        for anio, col in ANIOS.items():
            d = datos.setdefault((cod.zfill(2), anio), {"departamento": fila[1].strip()})
            d[var] = round(fila[col], 1)
with open(os.path.join(carpeta, "pib_departamental_2021_2024.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["cod_dpto", "departamento", "anio", "preliminar", "pib_corriente_mill_gs", "pib_constante2014_mill_gs"])
    for (cod, anio), d in sorted(datos.items()):
        w.writerow([cod, d["departamento"], anio, int(anio >= 2023), d["pib_corriente_mill_gs"], d["pib_constante2014_mill_gs"]])
print(len(datos), "filas")
