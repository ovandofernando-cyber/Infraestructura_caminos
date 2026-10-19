import sys, openpyxl
wb = openpyxl.load_workbook(sys.argv[1], read_only=True, data_only=True)
n = int(sys.argv[2]) if len(sys.argv) > 2 else 15
for ws in wb.worksheets:
    print('== hoja', ws.title, ws.max_row, ws.max_column)
    for i, r in enumerate(ws.iter_rows(values_only=True)):
        if i >= n: break
        print([c for c in r if c is not None])
