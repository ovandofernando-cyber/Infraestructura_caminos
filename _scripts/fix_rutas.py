import pandas as pd, re, sys
f=sys.argv[1]; a=pd.read_csv(f,dtype=str).fillna('')
def dep(s):
    if re.match(r'^PTE+[ .,]*HAYE',s): return 'PTE. HAYES'
    if s.startswith('ALTO PARAGU') and 'PARANA' not in s: return 'ALTO PARAGUAY'
    return s
a['departamento']=a.departamento.map(dep)
a['tramo_completo']=a.tramo_completo.str.replace(r'\s*TODOS\s+(LOS\s+)?TRAMOS.*$','',regex=True).str.replace(r'^\|\s*','',regex=True).str.strip()
a=a.drop_duplicates(subset=['fecha','tipo','departamento','tramo_completo','texto_estado'])
a.to_csv(f,index=False,encoding='utf-8-sig'); print(a.departamento.value_counts().to_dict())
