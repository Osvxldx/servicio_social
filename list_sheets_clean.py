import openpyxl
import os

template_path = 'RECIBOS DE AGUA POTABLE NUEVOS2025.xlsx'
if os.path.exists(template_path):
    wb = openpyxl.load_workbook(template_path, read_only=True)
    print(f"Sheets: {wb.sheetnames}")
    wb.close()
else:
    print("File not found.")
