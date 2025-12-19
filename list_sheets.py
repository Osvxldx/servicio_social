
import openpyxl

def list_sheets(path):
    try:
        wb = openpyxl.load_workbook(path, read_only=True)
        print(f"Sheets found: {wb.sheetnames}")
    except Exception as e:
        print(f"Error reading excel: {e}")

if __name__ == "__main__":
    list_sheets('RECIBOS DE AGUA POTABLE NUEVOS2025.xlsx')
