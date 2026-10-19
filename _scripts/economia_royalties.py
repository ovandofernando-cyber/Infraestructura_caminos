"""Convierte la transcripción de liquidación de royalties MEF 2025 en CSV con cod_dist (INE 2022).
Uso: python3 -I economia_royalties.py <raw.txt> <base_distrital_integrada.csv> <salida.csv>"""
import sys, csv, unicodedata, re
raw, base, out = sys.argv[1:4]
def norm(s):
    s = unicodedata.normalize('NFKD', s.upper()).encode('ascii','ignore').decode()
    s = s.replace('MUNICIPALIDAD DE ','')
    s = re.sub(r'[^A-Z0-9 ]',' ', s)
    return re.sub(r'\s+',' ', s).strip()
dist = []
with open(base, encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        dist.append((r['cod_dpto'], r['departamento'], r['cod_dist'], r['distrito'], norm(r['distrito'])))
alias = {  # nombre MEF normalizado -> nombre INE normalizado (resuelto a mano)
 'GRAL E AQUINO':'GENERAL ELIZARDO AQUINO','GRAL I RESQUIN':'GENERAL ISIDORO RESQUIN',
 'CAP M JOSE TROCHE':'CAPITAN MAURICIO JOSE TROCHE','GRAL EUGENIO A GARAY':'GENERAL EUGENIO A GARAY',
 'DR BOTTRELL':'DOCTOR BOTTRELL','DR CECILIO BAEZ':'DOCTOR CECILIO BAEZ','DR JUAN MANUEL FRUTOS':'DOCTOR JUAN MANUEL FRUTOS',
 'DR EULOGIO ESTIGARRIBIA':'DOCTOR EULOGIO ESTIGARRIBIA','R I 3 CORRALES':'R I TRES CORRALES','RAUL A OVIEDO':'RAUL ARSENIO OVIEDO',
 'MCAL FRANCISCO S LOPEZ':'MARISCAL FRANCISCO SOLANO LOPEZ','3 DE FEBRERO':'TRES DE FEBRERO','DR MOISES BERTONI':'DOCTOR MOISES S BERTONI',
 'GRAL HIGINIO MORINIGO':'GENERAL HIGINIO MORINIGO','CARLOS A LOPEZ':'CARLOS ANTONIO LOPEZ','JOSE L OVIEDO':'JOSE LEANDRO OVIEDO',
 'GRAL BERNARDINO CABALLERO':'GENERAL BERNARDINO CABALLERO','SAN ROQUE G DE S CRUZ':'SAN ROQUE GONZALEZ DE SANTACRUZ',
 'PTE FRANCO':'PRESIDENTE FRANCO','DOMINGO M DE IRALA':'DOMINGO MARTINEZ DE IRALA','DR JUAN L MALLORQUIN':'DOCTOR JUAN LEON MALLORQUIN',
 'JUAN E OLEARY':'JUAN EMILIO O LEARY','FDO DE LA MORA':'FERNANDO DE LA MORA','MARIANO R ALONSO':'MARIANO ROQUE ALONSO',
 'J AUGUSTO SALDIVAR':'J AUGUSTO SALDIVAR','GRAL JOSE E DIAZ':'GENERAL JOSE EDUVIGIS DIAZ','MAYOR JOSE D MARTINEZ':'MAYOR JOSE J MARTINEZ',
 'SAN JUAN BAUTISTA DE NEEM':'SAN JUAN BAUTISTA DE NEEMBUCU','GRAL FRANCISCO CABALLERO A':'GENERAL FRANCISCO CABALLERO ALVAREZ',
 'MCAL ESTIGARRIBIA':'MARISCAL JOSE FELIX ESTIGARRIBIA','TTE 1 MANUEL IRALA FERNANDEZ':'TENIENTE 1 MANUEL IRALA FERNANDEZ',
 'TTE ESTEBAN MARTINEZ':'TENIENTE ESTEBAN MARTINEZ','GRAL JOSE MARIA BRUGUEZ':'GENERAL JOSE MARIA BRUGUEZ','DR RAUL PENA':'DOCTOR RAUL PENA',
 'SAN PEDRO DE YCUAMANDIYU':'SAN PEDRO DEL YCUAMANDYYU','SARGENTO JOSE FELIX LOPEZ':'SARGENTO JOSE FELIX LOPEZ',
}
override = {22:'0214',24:'0216',52:'0406',67:'0504',69:'0506',75:'0512',76:'0513',81:'0518',87:'0604',88:'0605',
 111:'0718',124:'0801',145:'0912',150:'0917',154:'1004',158:'1007',194:'1205',199:'1210',224:'1506',226:'1702',
 229:'1507',238:'0108',246:'1022',147:'0914'}  # La Victoria = Puerto Casado (1702); Puerto Falcón = José Falcón (1506)
bycode={d[2]:d for d in dist}
def candidates(n):
    return [d for d in dist if d[4]==n]
rows=[]; total=None
with open(raw, encoding='utf-8') as f:
    for line in f:
        p=line.rstrip('\n').split(';')
        if p[0].startswith('TOTAL'):
            total=int(p[2].replace('.','')); continue
        num=int(p[0].split()[1]); name=p[1]; val=int(p[2].replace('.',''))
        n=norm(name); n2=alias.get(n,n)
        c=[bycode[override[num]]] if num in override else candidates(n2)
        if not c:  # tolerancia: coincidencia por prefijo/contención
            c=[d for d in dist if n2 in d[4] or d[4] in n2]
        rows.append([num,name,val,c])
# desambiguar por orden: la numeración MEF sigue el orden departamental hasta 30 236; usar dpto del vecino previo
prev_dpto=None; outrows=[]
for num,name,val,c in rows:
    pick=None
    if len(c)==1: pick=c[0]
    elif len(c)>1:
        same=[d for d in c if d[0]==prev_dpto]
        pick=same[0] if len(same)==1 else None
    if pick and num<=236: prev_dpto=pick[0]
    outrows.append([num,name,val]+(list(pick[:4]) if pick else ['','','',''])+['' if pick else 'sin_match' if not c else 'ambiguo:'+'|'.join(d[2] for d in c)])
s=sum(r[2] for r in outrows)
with open(out,'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['nro_mef','municipio_mef','royalties_liquidado_2025_gs','cod_dpto','departamento','cod_dist','distrito_ine','nota_match'])
    w.writerows(outrows)
print('filas',len(outrows),'suma',s,'total_doc',total,'dif',s-(total or 0))
print('sin match/ambiguos:',[(r[0],r[1],r[-1]) for r in outrows if r[-1]])
