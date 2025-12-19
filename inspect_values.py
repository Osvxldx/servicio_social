
import openpyxl

def inspect_values(path):
    try:
        wb = openpyxl.load_workbook(path, data_only=True)
        sheet = wb['BASE DE DATOS']
        
        # Get first few rows data for specific indices
        # 3: SECCIONAR, 4: T. POZO, 5: TOMA, 6: CONAGUA, 7: DRENAJE
        indices = [3, 4, 5, 6, 7]
        names = ["SECCIONAR", "T. POZO", "TOMA", "CONAGUA", "DRENAJE"]
        
        print("Values for check:")
        count = 0
        for row in sheet.iter_rows(min_row=2, max_row=15, values_only=True):
            vals = [f"{names[i]}: {row[idx]}" for i, idx in enumerate(indices)]
            print(f"Row: {vals}")
            count += 1
            
    except Exception as e:
        print(f"Error reading excel: {e}")

if __name__ == "__main__":
    inspect_values('RECIBOS DE AGUA POTABLE NUEVOS2025.xlsx')
