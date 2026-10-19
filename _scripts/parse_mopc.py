import pdfplumber, glob, re, sys, csv, os
src = sys.argv[1]; out = sys.argv[2]
ROWS = ["NACIONAL","DEPARTAMENTAL","VECINAL","TOTAL"]
num = re.compile(r'^(\d{1,3}(\.\d{3})*,\d{2}|-)$')
def tofloat(t): return 0.0 if t=='-' else float(t.replace('.','').replace(',','.'))
res=[]; problems=[]
for f in sorted(glob.glob(os.path.join(src,'[01]*_corte_dic2025.pdf'))):
    with pdfplumber.open(f) as pdf:
        w = pdf.pages[0].extract_words()
    cand=[]
    for p in [x for x in w if x['text']=='PCA']:
        right=[y for y in w if abs(y['top']-p['top'])<5 and y['x0']>p['x1'] and y['text']=='TOTAL']
        nac=[y for y in w if y['text']=='NACIONAL' and 0<y['top']-p['top']<40 and y['x1']<p['x0']]
        if right and nac: cand.append((p,right[0],nac[0]))
    if not cand: problems.append((f,'no header')); continue
    p,tot,nac=cand[0]; top=p['top']; labx=nac['x0']
    hdr=sorted([y for y in w if abs(y['top']-top)<5 and p['x0']-2<=y['x0']<=tot['x1']+2 and y['text'] not in ('(km)','(Km)')],key=lambda y:y['x0'])
    cols=[(y['text'],(y['x0']+y['x1'])/2) for y in hdr]
    dpto=' '.join(y['text'] for y in sorted([y for y in w if abs(y['top']-top)<5 and labx-5<=y['x0']<p['x0']],key=lambda y:y['x0']))
    for rn in ROWS:
        lab=[x for x in w if x['text']==rn and 0<x['top']-top<90 and abs(x['x0']-labx)<10]
        if not lab: problems.append((f,'no row '+rn)); continue
        t=lab[0]['top']
        toks=[x for x in w if abs(x['top']-t)<5 and x['x0']>p['x0']-40 and x['x1']<tot['x1']+60 and num.match(x['text'])]
        row={c[0]:0.0 for c in cols}
        for k in toks:
            c=min(cols,key=lambda c: abs(c[1]-(k['x0']+k['x1'])/2))
            row[c[0]]=tofloat(k['text'])
        rec={'archivo':os.path.basename(f),'departamento':dpto.replace('DPTO.','').strip(),'red':rn}
        rec.update(row)
        rec['chk']=round(sum(v for k,v in row.items() if k!='TOTAL')-row['TOTAL'],2)
        res.append(rec)
allc=[]
for r in res:
    for k in r:
        if k not in allc: allc.append(k)
order=[c for c in ['archivo','departamento','red','PCA','TS','ADQ','E','RE','R','T','TOTAL'] if c in allc]+[c for c in allc if c not in ['archivo','departamento','red','PCA','TS','ADQ','E','RE','R','T','TOTAL','chk']]+['chk']
with open(out,'w',newline='',encoding='utf-8') as fh:
    wr=csv.DictWriter(fh,fieldnames=order); wr.writeheader()
    for r in res: wr.writerow({k:r.get(k,0.0) for k in order})
for pr in problems: print('PROBLEM',pr)
print(len(res),'rows')
