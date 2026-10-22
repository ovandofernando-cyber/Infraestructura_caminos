# Uso: python3 -I chirps_diario_iri.py <carpeta destino> [años...]
# Descarga CHIRPS diario (IRI Data Library) para Paraguay por mes y arma un archivo por año.
import os, sys, subprocess, time, calendar, xarray as xr
D = sys.argv[1]
M = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
YEARS = [int(a) for a in sys.argv[2:]] or list(range(2013, 2023))
for y in YEARS:
    out = f'{D}/chirps_daily_PRY_{y}.nc'
    if os.path.exists(out): continue
    parts = []
    for i, mn in enumerate(M, 1):
        f = f'{D}/m_{y}_{i:02d}.nc'
        last = calendar.monthrange(y, i)[1]
        url = (f'https://iridl.ldeo.columbia.edu/SOURCES/.UCSB/.CHIRPS/.v2p0/.daily-improved/.global/.0p05/.prcp/'
               f'X/-62.7/-54.2/RANGEEDGES/Y/-27.7/-19.2/RANGEEDGES/T/(1%20{mn}%20{y})/({last}%20{mn}%20{y})/RANGEEDGES/data.nc')
        for k in range(5):
            if os.path.exists(f) and os.path.getsize(f) > 100000: break
            subprocess.run(['curl', '-sS', '-L', '-m', '600', '-o', f, url])
            if os.path.getsize(f) > 100000 if os.path.exists(f) else False: break
            time.sleep(10 * (k + 1))
        parts.append(f)
    ds = xr.concat([xr.open_dataset(p, decode_times=False) for p in parts], dim='T')
    ds.to_netcdf(out); ds.close()
    for p in parts: os.remove(p)
    print(y, os.path.getsize(out) // 1_000_000, 'MB', flush=True)
