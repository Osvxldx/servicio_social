import openpyxl
import os
import sys

# Redirigir stdout para evitar buffering excesivo
sys.stdout.reconfigure(encoding='utf-8')

try:
    wb = openpyxl.load_workbook('RECIBOS DE AGUA POTABLE NUEVOS2025.xlsx')
    if 'RECIBO 2025' in wb.sheetnames:
        ws = wb['RECIBO 2025']
    else:
        ws = wb.active

    targets = [
        'L2', 'L26', # Folio
        'I5', 'I29', # Fecha
        'K42', # Total Copia (Known issue)
        'B12', 'B13', 'B14', 'B15', # Conceptos Original
        'B36', 'B37', 'B38', 'B39', # Conceptos Copia
    ]

    print("--- START INSPECTION ---")
    for coord in targets:
        cell = ws[coord]
        c_type = type(cell).__name__
        msg = f"{coord}: {c_type}"
        if c_type == 'MergedCell':
             for merged_range in ws.merged_cells.ranges:
                 if coord in merged_range:
                     msg += f" -> Range: {merged_range}, Top-Left: {merged_range.start_cell}"
                     break
        print(msg)
    print("--- END INSPECTION ---")

except Exception as e:
    print(f"Error: {e}")
