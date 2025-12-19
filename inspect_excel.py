
import openpyxl

def inspect_excel(path):
    try:
        wb = openpyxl.load_workbook(path, data_only=True)
        sheet = wb.active
        print(f"Sheet Name: {sheet.title}")
        
        headers = []
        for cell in sheet[1]:
            headers.append(cell.value)
            
        print("Headers found:", headers)
        
        # Print first valid row to see data types
        row_data = []
        for cell in sheet[2]:
            row_data.append(cell.value)
        print("First row data:", row_data)
        
    except Exception as e:
        print(f"Error reading excel: {e}")

if __name__ == "__main__":
    inspect_excel('RECIBOS DE AGUA POTABLE NUEVOS2025.xlsx')
