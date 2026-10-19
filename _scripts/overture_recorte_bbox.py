"""Recorta temas de Overture Maps al bbox de Paraguay leyendo solo los row groups necesarios.

Uso: python3 -I overture_recorte_bbox.py <tema/type=...> <salida.parquet>
"""
import sys, time
import pyarrow as pa, pyarrow.fs as fs, pyarrow.parquet as pq, pyarrow.compute as pc
from concurrent.futures import ThreadPoolExecutor

RELEASE = 'overturemaps-us-west-2/release/2026-09-23.1/theme='
XMIN, YMIN, XMAX, YMAX = -62.7, -27.7, -54.2, -19.2

s3 = fs.S3FileSystem(anonymous=True, region='us-west-2',
                     proxy_options='http://127.0.0.1:43249',
                     tls_ca_file_path='/root/.ccr/ca-bundle.crt')


def bbox_stats(md, rg):
    """Devuelve (xmin_min, xmax_max, ymin_min, ymax_max) del row group a partir de las estadísticas."""
    vals = {}
    r = md.row_group(rg)
    for i in range(r.num_columns):
        col = r.column(i)
        p = col.path_in_schema
        if p in ('bbox.xmin', 'bbox.xmax', 'bbox.ymin', 'bbox.ymax') and col.statistics is not None and col.statistics.has_min_max:
            vals[p] = (col.statistics.min, col.statistics.max)
    if len(vals) < 4:
        return None
    return vals['bbox.xmin'][0], vals['bbox.xmax'][1], vals['bbox.ymin'][0], vals['bbox.ymax'][1]


def process(path):
    f = pq.ParquetFile(s3.open_input_file(path))
    md = f.metadata
    keep = []
    for rg in range(md.num_row_groups):
        st = bbox_stats(md, rg)
        if st is None:
            keep.append(rg)
            continue
        xmin, xmax, ymin, ymax = st
        if xmin <= XMAX and xmax >= XMIN and ymin <= YMAX and ymax >= YMIN:
            keep.append(rg)
    if not keep:
        return None, md.num_row_groups, 0
    t = f.read_row_groups(keep)
    b = t.column('bbox')
    m = pc.and_(pc.and_(pc.less_equal(pc.struct_field(b, 'xmin'), XMAX), pc.greater_equal(pc.struct_field(b, 'xmax'), XMIN)),
                pc.and_(pc.less_equal(pc.struct_field(b, 'ymin'), YMAX), pc.greater_equal(pc.struct_field(b, 'ymax'), YMIN)))
    t = t.filter(m)
    return t, md.num_row_groups, len(keep)


def main(theme, out):
    t0 = time.time()
    files = [i.path for i in s3.get_file_info(fs.FileSelector(RELEASE + theme)) if i.path.endswith('.parquet') or 'part-' in i.path]
    tables = []
    with ThreadPoolExecutor(8) as ex:
        for path, (t, nrg, nk) in zip(files, ex.map(process, files)):
            if t is not None and t.num_rows:
                tables.append(t)
            print(path.rsplit('/', 1)[-1][:40], nrg, nk, 0 if t is None else t.num_rows, flush=True)
    res = pa.concat_tables(tables, promote_options='default')
    pq.write_table(res, out, compression='zstd')
    print('filas', res.num_rows, 'seg', round(time.time() - t0))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
