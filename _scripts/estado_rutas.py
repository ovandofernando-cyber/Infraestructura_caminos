import re, html, urllib.request, os, subprocess, time
OUT='/home/user/repositorio_caminos_vecinales/03_red_vial_MOPC/estado_de_rutas_puentes_clausurados_2026'
def ls(fid):
    s=urllib.request.urlopen(f'https://drive.google.com/embeddedfolderview?id={fid}',timeout=60).read().decode('utf-8','replace')
    return [(html.unescape(m.group(2)),m.group(1)) for m in re.finditer(r'<a href="([^"]+)"[^>]*>.*?flip-entry-title">(.*?)</div>',s,re.S)]
for mes,url in ls('16y2lx1eoOwn532O1F0j-g0Ye7YZj0dWD'):
    fid=url.rstrip('/').split('/')[-1]; d=os.path.join(OUT,mes.replace(' ','_')); os.makedirs(d,exist_ok=True)
    for name,u in ls(fid):
        m=re.search(r'/d/([^/]+)/',u)
        if not m: continue
        out=os.path.join(d,re.sub(r'[\\/:*?"<>|]+','_',name))
        if os.path.exists(out) and os.path.getsize(out)>1000: continue
        subprocess.run(['curl','-sS','-L','--retry','3','-m','300','-o',out,f'https://drive.usercontent.google.com/download?id={m.group(1)}&export=download&confirm=t'])
        time.sleep(0.5)
    print(mes,len(os.listdir(d)),flush=True)
