
import openpyxl

def scan_excel(path):
    try:
        wb = openpyxl.load_workbook(path, data_only=True)
        sheet = wb.active
        print(f"Sheet Name: {sheet.title}")
        
        for i, row in enumerate(sheet.iter_rows(min_row=1, max_row=15, values_only=True), 1):
            # Check if this row looks like a header (has strings)
            strings = [str(c) for c in row if c is not None]
            print(f"Row {i}: {strings}")
            
    except Exception as e:
        print(f"Error reading excel: {e}")

if __name__ == "__main__":
    scan_excel('RECIBOS DE AGUA POTABLE NUEVOS2025.xlsx')
