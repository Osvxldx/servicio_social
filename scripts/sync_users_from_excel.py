import openpyxl
import sqlite3
import os
import sys

# Agregar src al path para importar database si fuera necesario, 
# pero haremos conexión directa para este script simple.

def sync_users():
    base_dir = os.getcwd()
    excel_path = os.path.join(base_dir, 'RECIBOS DE AGUA POTABLE NUEVOS2025.xlsx')
    db_path = os.path.join(base_dir, 'agua_potable.db')
    
    if not os.path.exists(excel_path):
        print("No se encontró el Excel")
        return
        
    print("Leyendo Excel...")
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    if 'BASE DE DATOS' not in wb.sheetnames:
        print("No existe la hoja BASE DE DATOS")
        return
        
    ws = wb['BASE DE DATOS']
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    updates = 0
    not_found = 0
    
    # Recorrer Excel (Filas 2 en adelante)
    # Col 2 (B) = No. USUARIO
    # Col 3 (C) = NOMBRE
    
    print("Iniciando sincronización...")
    for row in range(2, ws.max_row + 1):
        no_usuario_val = ws.cell(row=row, column=2).value
        nombre_val = ws.cell(row=row, column=3).value
        
        if nombre_val:
            nombre_str = str(nombre_val).strip().upper()
            
            # Normalizar numero usuario (quitar .0 si existe)
            if no_usuario_val is not None:
                no_usuario_str = str(no_usuario_val).split('.')[0]
            else:
                no_usuario_str = None
                
            if no_usuario_str:
                # Buscar en DB por nombre
                # Usamos LIKE para ser un poco flexibles con espacios
                cursor.execute("SELECT id FROM usuarios WHERE upper(nombre) = ?", (nombre_str,))
                result = cursor.fetchone()
                
                if result:
                    user_id = result[0]
                    # Actualizar numero_usuario
                    cursor.execute("UPDATE usuarios SET numero_usuario = ? WHERE id = ?", (no_usuario_str, user_id))
                    updates += 1
                else:
                    #print(f"No encontrado en DB: {nombre_str}")
                    not_found += 1
            
    conn.commit()
    conn.close()
    print(f"Sincronización completada.")
    print(f"Usuarios actualizados: {updates}")
    print(f"Usuarios no encontrados en DB: {not_found}")

if __name__ == "__main__":
    sync_users()
