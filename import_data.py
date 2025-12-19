
import openpyxl
import sqlite3
import os
import sys

# Add src to path to use database module
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from database import DatabaseManager

def import_users(excel_path):
    print(f"Importing users from {excel_path}...")
    
    if not os.path.exists(excel_path):
        print("Excel file not found!")
        return

    db = DatabaseManager('agua_potable.db')
    
    # Force migration check/run
    print("Verifying database schema...")
    try:
        # Trigger connection to run migrations in __init__
        conn = db.get_connection()
        conn.close()
    except Exception as e:
        print(f"Error initializing DB: {e}")
        return

    try:
        wb = openpyxl.load_workbook(excel_path, data_only=True)
        sheet = wb['BASE DE DATOS']
        
        # Column mapping based on previous inspection
        # 0: OBSERVACIONES ANTERIOR COMITÉ
        # 1: No. USUARIO
        # 2: NOMBRE
        # 3: SECCIONAR
        # 4: T. POZO
        # 5: TOMA
        # 6: CONAGUA
        # 7: DRENAJE
        # 8: HIDRANTE
        # 9: INQUILINO
        # 10: VACAS
        # 11: OBSERVACIONES
        # 12: DIRECCION
        
        count = 0
        updated = 0
        
        # Start from row 2 (skip header)
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if not row[1] and not row[2]: # Skip empty rows
                continue
                
            obs_ant = row[0]
            no_usuario = str(row[1]).strip() if row[1] else None
            nombre = str(row[2]).strip() if row[2] else "Sin Nombre"
            
            # Helper to parse float/int safely
            def parse_num(val, default=0):
                if val is None: return default
                try:
                    return float(val)
                except:
                    return default

            seccionar = parse_num(row[3])
            t_pozo = parse_num(row[4])
            tomas = parse_num(row[5], 1)
            conagua = parse_num(row[6])
            drenaje = parse_num(row[7])
            hidrantes = parse_num(row[8])
            inquilinos = parse_num(row[9])
            vacas = parse_num(row[10])
            observaciones = str(row[11]).strip() if row[11] else ""
            direccion = str(row[12]).strip() if row[12] else ""
            
            # Additional observations merge
            full_obs = observaciones
            if obs_ant:
                full_obs = f"{full_obs} | Ant: {obs_ant}" if full_obs else f"Ant: {obs_ant}"

            # Check if user exists by numero_usuario
            existing = None
            if no_usuario:
                 existing_list = db.buscar_usuarios_por_numero(no_usuario)
                 # Filter exact match if possible or take first
                 for u in existing_list:
                     if u['numero_usuario'] == no_usuario:
                         existing = u
                         break
            
            # If not found by number, try name
            if not existing:
                existing_list = db.buscar_usuarios_por_nombre(nombre)
                if existing_list:
                    # Exact match name?
                    for u in existing_list:
                        if u['nombre'].lower() == nombre.lower():
                            existing = u
                            break
            
            if existing:
                # Update
                print(f"Updating user: {nombre} ({no_usuario})")
                db.actualizar_usuario(
                    existing['id'],
                    numero_usuario=no_usuario,
                    nombre=nombre,
                    direccion=direccion if direccion else existing['direccion'],
                    seccionar=seccionar,
                    t_pozo=t_pozo,
                    tomas=tomas,
                    conagua=conagua,
                    drenaje=drenaje,
                    hidrantes=hidrantes,
                    inquilinos=inquilinos,
                    vacas=vacas,
                    observaciones=full_obs,
                    observaciones_anterior=str(obs_ant) if obs_ant else None
                )
                updated += 1
            else:
                # Create - Pass ONLY known arguments
                print(f"Creating user: {nombre} ({no_usuario})")
                success = db.crear_usuario(
                    nombre=nombre,
                    direccion=direccion,
                    sesion=1, # Default
                    vacas=vacas,
                    inquilinos=inquilinos,
                    tomas=tomas,
                    hidrantes=hidrantes,
                    numero_usuario=no_usuario
                )
                
                if success:
                    count += 1
                    # Find and update extras
                    new_users = db.buscar_usuarios_por_numero(no_usuario)
                    if not new_users and nombre:
                         # Fallback search by name if numero_usuario was None/auto
                         l = db.buscar_usuarios_por_nombre(nombre)
                         for u in l: 
                             if u['nombre'] == nombre:
                                 new_users = [u]
                                 break

                    if new_users:
                        new_id = new_users[0]['id']
                        db.actualizar_usuario(new_id, 
                            seccionar=seccionar, 
                            t_pozo=t_pozo, 
                            conagua=conagua, 
                            drenaje=drenaje,
                            observaciones=observaciones, # create doesnt take obs
                            observaciones_anterior=str(obs_ant) if obs_ant else None
                        )
                else:
                    print(f"Failed to create user {nombre}")

        print(f"Import complete. Created: {count}, Updated: {updated}")

    except Exception as e:
        print(f"Error during import: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import_users('RECIBOS DE AGUA POTABLE NUEVOS2025.xlsx')
