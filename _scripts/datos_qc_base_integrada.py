"""Chequeo de calidad rapido de 00_base_integrada (agente ciencia de datos).
Uso: python3 -I _scripts/datos_qc_base_integrada.py <raiz_repo>
Solo lee CSV con pandas; no ejecuta nada de los datos.
"""
import sys, os
import pandas as pd

raiz = sys.argv[1] if len(sys.argv) > 1 else "."
b = os.path.join(raiz, "00_base_integrada")
d = pd.read_csv(os.path.join(b, "base_distrital_integrada.csv"), dtype={"cod_dpto": str, "cod_dist": str})
e = pd.read_csv(os.path.join(b, "base_departamental_integrada.csv"), dtype={"cod_dpto": str})
cod = pd.read_csv(os.path.join(raiz, sys.argv[2]), dtype=str) if len(sys.argv) > 2 else None

print("== DISTRITAL", d.shape)
print("cod_dist duplicados:", d["cod_dist"].duplicated().sum())
print("nombres distrito duplicados (dpto+nombre):", d.duplicated(["cod_dpto", "distrito"]).sum())
print("cod_dist mal formado (no 4 digitos):", (~d["cod_dist"].str.fullmatch(r"\d{4}")).sum())
print("cod_dist no empieza con cod_dpto:", (d["cod_dist"].str[:2] != d["cod_dpto"]).sum())
print("cod_dpto fuera de 00-17:", (~d["cod_dpto"].astype(int).between(0, 17)).sum())
print("distritos por dpto:", d.groupby("cod_dpto").size().to_dict())
print("foco:", d.loc[d.departamento_foco == "Sí", "cod_dpto"].value_counts().sort_index().to_dict(),
      "total", (d.departamento_foco == "Sí").sum())
nul = d.isna().sum()
print("nulos por columna (>0):"); print(nul[nul > 0].to_string())
foco = d[d.departamento_foco == "Sí"]
nf = foco.isna().sum()
print("nulos en distritos foco (>0):"); print(nf[nf > 0].to_string())
for c in ["RAI_pct", "ipm_H_rural"]:
    print(f"distritos sin {c}:", d.loc[d[c].isna(), ["cod_dist", "distrito"]].values.tolist())
pct = [c for c in d.columns if c.startswith("pct_") or c.endswith("_pct") or c.startswith("ipm_H") or c == "RAI_pct"]
for c in pct:
    m = d[c] > 100
    if m.any():
        print(f"{c} > 100 en {m.sum()} distritos:", d.loc[m, ["cod_dist", "distrito", c]].values.tolist()[:8])
# consistencia poblacion
s = d[["censo_pob_urbana", "censo_pob_rural"]].fillna(0).sum(axis=1)
print("censo urbana+rural != total:", (abs(s - d["censo_pob_total"]) > 1).sum())
print("sum censo_pob_total:", d["censo_pob_total"].sum())
r = d["heigit_pob_total_worldpop"] / d["censo_pob_total"]
print("ratio WorldPop/Censo: min %.2f max %.2f; fuera de [0.7,1.5]: %d" % (r.min(), r.max(), ((r < 0.7) | (r > 1.5)).sum()))
print("  extremos:", d.loc[(r < 0.7) | (r > 1.5), ["cod_dist", "distrito"]].assign(r=r.round(2)).values.tolist()[:12])
print("rural>0 en HeiGIT pero censo rural nulo:", ((d.censo_pob_rural.isna()) & (d.heigit_pob_rural > 0)).sum())
if cod is not None:
    print("codigos de referencia cargados", cod.shape)

print("\n== DEPARTAMENTAL", e.shape)
print("cod_dpto:", e["cod_dpto"].tolist())
print("duplicados:", e["cod_dpto"].duplicated().sum())
ne = e.isna().sum(); print("nulos (>0):"); print(ne[ne > 0].to_string())
print("n_upm rural 2025 min:", e["ephc2025_rural_n_upm"].min(), "n noconsulta min:", e["ephc2022_25_noconsulta_n"].min())
# coherencia con distrital
agg = d.groupby("cod_dpto")["censo_pob_rural"].sum()
m = e.set_index("cod_dpto")["censo_pob_rural"]
dif = (agg.reindex(m.index) - m).abs()
print("dif censo_pob_rural dpto vs suma distritos (>1):", dif[dif > 1].to_dict())

# cruce con lista oficial INE 2022 de distritos
ref = os.path.join(raiz, "05_cartografia_y_codigos/codigos_geograficos_INE_2022/Codigos de distritos INE 2022.xlsx")
if os.path.exists(ref):
    x = pd.read_excel(ref, dtype=str, header=2).dropna(subset=["CÓDIGO"])
    s1, s2 = set(d.cod_dist), set(x["CÓDIGO"].str.strip())
    print("\n== CRUCE INE 2022: lista oficial", len(s2), "| en base y no en INE:", sorted(s1 - s2), "| en INE y no en base:", sorted(s2 - s1))
    nm = d.merge(x, left_on="cod_dist", right_on="CÓDIGO")
    dif = nm[nm.distrito.str.strip().str.upper() != nm.DISTRITO.str.strip().str.upper()]
    print("nombres distintos:", dif[["cod_dist", "distrito", "DISTRITO"]].values.tolist())
# IPM rural: H nulo pero A/M0 = 0 en distritos 100% urbanos
m = d.ipm_H_rural.isna() & d.ipm_A_rural.notna()
print("ipm_H_rural nulo con ipm_A/M0_rural=0 (distritos sin area rural):", m.sum())
