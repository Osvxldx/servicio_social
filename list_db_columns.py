
import openpyxl

def list_columns(path):
    try:
        wb = openpyxl.load_workbook(path, data_only=True)
        sheet = wb['BASE DE DATOS']
        
        # Get first row
        header_row = next(sheet.iter_rows(min_row=1, max_row=1, values_only=True))
        
        print("Columns in 'BASE DE DATOS':")
        for i, val in enumerate(header_row):
            if val:
                print(f"{i}: {val}")
                
    except Exception as e:
        print(f"Error reading excel: {e}")

if __name__ == "__main__":
    list_columns('RECIBOS DE AGUA POTABLE NUEVOS2025.xlsx')
