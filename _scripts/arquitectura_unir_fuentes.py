"""Suma al catálogo maestro las fuentes registradas por los agentes en 09_, 10_ y 11_
y arma la lista de fuentes pendientes de descarga manual.
Uso (después de datos_fuentes_maestro.py):
    python3 -I _scripts/arquitectura_unir_fuentes.py <raiz_repo>
Salidas: _arquitectura/fuentes_maestro.csv (agrega filas) y _arquitectura/fuentes_pendientes_descarga.csv
"""
import csv, os, sys

raiz = sys.argv[1] if len(sys.argv) > 1 else "."
MAESTRO = os.path.join(raiz, "_arquitectura", "fuentes_maestro.csv")
PENDIENTES = os.path.join(raiz, "_arquitectura", "fuentes_pendientes_descarga.csv")
REGISTROS = [
    ("09_servicios_complementarios", "_fuentes_social.csv", "servicios"),
    ("10_economia_y_mercados", "_fuentes_economia.csv", "economia"),
    ("11_infraestructura_vial_complementaria", "_fuentes_infraestructura.csv", "red_vial"),
]


def medir(carpeta, ruta_local):
    """Cuenta archivos y MB de las rutas de una fuente (separadas por ';', relativas a la raíz o a la carpeta previa)."""
    n, b, base = 0, 0, ""
    for r in [x.strip() for x in ruta_local.split(";") if x.strip()]:
        p = os.path.join(raiz, r)
        if not os.path.exists(p) and base:
            p = os.path.join(base, r)
        if os.path.isdir(p):
            base = p
            for d, _, fs in os.walk(p):
                for f in fs:
                    n += 1
                    b += os.path.getsize(os.path.join(d, f))
        elif os.path.isfile(p):
            base = os.path.dirname(p)
            n += 1
            b += os.path.getsize(p)
    return n, round(b / 1e6, 2)


with open(MAESTRO, encoding="utf-8-sig") as fh:
    lector = csv.DictReader(fh)
    cols = lector.fieldnames
    filas = [f for f in lector if f["carpeta"] not in {c for c, _, _ in REGISTROS}]

pendientes = []
for carpeta, archivo, tema in REGISTROS:
    with open(os.path.join(raiz, carpeta, archivo), encoding="utf-8-sig") as fh:
        for x in csv.DictReader(fh):
            n, mb = medir(carpeta, x["ruta_local"]) if x["estado"] == "descargado" else (0, 0.0)
            filas.append({
                "id": x["id"], "carpeta": carpeta, "nombre": x["nombre"], "institucion": x["institucion"],
                "url": x["url"], "tema": tema, "periodicidad": x["periodicidad"],
                "periodo_cubierto": x["periodo_cubierto"], "ultima_actualizacion_conocida": "",
                "nivel_geografico": x["nivel_geografico"], "formato": x["formato"],
                "clave_union": x["clave_union"], "n_archivos": n, "tamano_mb": mb,
                "licencia": x["licencia"], "calidad_notas": f"[{x['estado']}] {x['notas']}".strip(),
            })
            if x["estado"] != "descargado":
                pendientes.append({"id": x["id"], "fuente": x["nombre"], "institucion": x["institucion"],
                                   "url": x["url"], "estado": x["estado"], "carpeta_destino": carpeta,
                                   "motivo": x["notas"]})

with open(os.path.join(raiz, "12_INE_complementario", "_registro_INE_no_descargado.csv"), encoding="utf-8-sig") as fh:
    for i, x in enumerate(csv.DictReader(fh), 1):
        if x["estado"] not in ("no necesario", "descargado"):
            pendientes.append({"id": f"INE{i:02d}", "fuente": x["fuente"], "institucion": "INE", "url": x["url"],
                               "estado": x["estado"], "carpeta_destino": "12_INE_complementario/" + x["subcarpeta_destino"],
                               "motivo": f"prioridad {x['prioridad']}; {x['motivo']}"})

with open(MAESTRO, "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader()
    w.writerows(filas)
with open(PENDIENTES, "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["id", "fuente", "institucion", "url", "estado", "carpeta_destino", "motivo"])
    w.writeheader()
    w.writerows(pendientes)
print(f"maestro: {len(filas)} fuentes; pendientes: {len(pendientes)}")
