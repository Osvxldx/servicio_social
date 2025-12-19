import openpyxl
import sqlite3
import os
import shutil
import datetime

def full_import_clean():
    base_dir = os.getcwd()
    excel_path = os.path.join(base_dir, 'RECIBOS DE AGUA POTABLE NUEVOS2025.xlsx')
    db_path = os.path.join(base_dir, 'agua_potable.db')
    
    # 1. Backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(base_dir, f'agua_potable_backup_{timestamp}.db')
    if os.path.exists(db_path):
        shutil.copy2(db_path, backup_path)
        print(f"Backup creado: {backup_path}")
    
    # 2. Conectar y Limpiar
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Limpiando base de datos...")
    cursor.execute("DELETE FROM detalle_pagos")
    cursor.execute("DELETE FROM pagos")
    cursor.execute("DELETE FROM usuarios")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='usuarios'") # Reiniciar auto-increment
    
    # 3. Leer Excel
    print("Leyendo Excel...")
    if not os.path.exists(excel_path):
        print("Error: No se encuentra el archivo Excel")
        conn.close()
        return

    wb = openpyxl.load_workbook(excel_path, data_only=True)
    if 'BASE DE DATOS' not in wb.sheetnames:
        print("Error: Hoja 'BASE DE DATOS' no encontrada")
        conn.close()
        return
        
    ws = wb['BASE DE DATOS']
    
    imported_count = 0
    
    # Filas 2 en adelante
    # B=2 (No. Usuario), C=3 (Nombre), D=4 (Seccionar), E=5 (T. Pozo), F=6 (Toma), 
    # G=7 (Conagua), H=8 (Drenaje), I=9 (Hidrante), J=10 (Inquilino), K=11 (Vacas), 
    # M=13 (Direccion)
    
    # Identificar el maximo ID entero para asignar a los alfanumericos despues
    current_max_id = 0
    
    # Primera pasada: Solo IDs numéricos puros para mantener el orden exacto
    rows_buffer = []
    
    for row in range(2, ws.max_row + 1):
        raw_id = ws.cell(row=row, column=2).value
        if raw_id is None:
            continue
            
        nombre = ws.cell(row=row, column=3).value
        # Si no hay nombre, ignorar
        if not nombre:
            continue
            
        is_numeric = False
        user_id_int = 0
        
        try:
            val_str = str(raw_id).strip()
            # Quitamos .0 si existe
            if val_str.endswith('.0'): 
                val_str = val_str[:-2]
                
            user_id_int = int(val_str)
            if user_id_int > current_max_id:
                current_max_id = user_id_int
            is_numeric = True
        except ValueError:
            is_numeric = False
            
        row_data = {
            'row': row,
            'raw_id': str(raw_id).strip(),
            'clean_id': user_id_int if is_numeric else None,
            'is_numeric': is_numeric,
            'nombre': str(nombre).strip().upper(),
            # Otros datos solo se leen al insertar para no llenar memoria
        }
        rows_buffer.append(row_data)
        
    # Ordenar buffer: Numericos primero por ID, luego Alfanumericos por orden original
    # Aunque el Excel ya deberia estar ordenado, esto asegura que los numericos toman sus slots
    
    # Separar
    numeric_rows = [r for r in rows_buffer if r['is_numeric']]
    alpha_rows = [r for r in rows_buffer if not r['is_numeric']]
    
    # Insertar Numéricos
    for r in numeric_rows:
        insert_user(cursor, ws, r['row'], r['clean_id'], r['raw_id']) # ID = Clean ID
        imported_count += 1
        
    next_id = current_max_id + 1
    
    # Insertar Alfanuméricos
    for r in alpha_rows:
        # Asignar un ID nuevo secuencial start=max+1
        # Pero guardar el raw_id visual en numero_usuario
        real_id_to_use = next_id
        
        # OJO: Si el Excel tiene "125A", el ID en DB será por ejemplo 700.
        # Pero el "numero_usuario" visual será "125A".
        
        insert_user(cursor, ws, r['row'], real_id_to_use, r['raw_id']) 
        next_id += 1
        imported_count += 1
            
    conn.commit()
    conn.close()
    print(f"Importación completada. Usuarios importados: {imported_count}")

def insert_user(cursor, ws, row, db_id, numero_usuario_visual):
    # Leer resto de columnas
    seccionar = ws.cell(row=row, column=4).value or 0
    t_pozo = ws.cell(row=row, column=5).value or 0
    tomas = ws.cell(row=row, column=6).value or 1
    conagua = ws.cell(row=row, column=7).value or 0
    drenaje = ws.cell(row=row, column=8).value or 0
    hidrantes = ws.cell(row=row, column=9).value or 0
    inquilinos = ws.cell(row=row, column=10).value or 0
    vacas = ws.cell(row=row, column=11).value or 0
    direccion = ws.cell(row=row, column=13).value or ""
    nombre = str(ws.cell(row=row, column=3).value).strip().upper()

    # Limpiar valores numéricos
    def clean_num(val):
        try:
            return float(val) if val else 0
        except ValueError:
            return 0
    
    seccionar = clean_num(seccionar)
    t_pozo = clean_num(t_pozo)
    tomas = clean_num(tomas)
    conagua = clean_num(conagua)
    drenaje = clean_num(drenaje)
    hidrantes = clean_num(hidrantes)
    inquilinos = clean_num(inquilinos)
    vacas = clean_num(vacas)
    
    try:
        cursor.execute('''
            INSERT INTO usuarios (id, nombre, numero_usuario, direccion, seccionar, t_pozo, tomas, conagua, drenaje, hidrantes, inquilinos, vacas, sesion, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            db_id, 
            nombre, 
            str(numero_usuario_visual), 
            str(direccion), 
            seccionar, 
            t_pozo, 
            tomas, 
            conagua, 
            drenaje, 
            hidrantes, 
            inquilinos, 
            vacas,
            1, # Sesión default
            'Activo'
        ))
    except sqlite3.IntegrityError:
        print(f"Error duplicado ID {db_id} en fila {row} ({nombre})")

if __name__ == "__main__":
    full_import_clean()
