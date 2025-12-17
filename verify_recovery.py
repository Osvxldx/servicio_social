
import sqlite3
import re
import os

def check_schema():
    print("Checking database schema...")
    conn = sqlite3.connect('agua_potable.db')
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(usuarios)")
        columns = {row[1] for row in cursor.fetchall()}
        required = {'numero_usuario', 'observaciones', 'hidrantes'}
        missing = required - columns
        if missing:
            print(f"FAILED: Missing columns in 'usuarios': {missing}")
        else:
            print("SUCCESS: All required columns present in 'usuarios'.")
    except Exception as e:
        print(f"FAILED: Error checking schema: {e}")
    finally:
        conn.close()

def check_file_content(path, pattern, description):
    print(f"Checking {os.path.basename(path)} for {description}...")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        if re.search(pattern, content):
            print(f"SUCCESS: Found {description}")
        else:
            print(f"FAILED: Could not find {description}")
    except Exception as e:
        print(f"FAILED: Error reading file: {e}")

if __name__ == "__main__":
    check_schema()
    
    # Check database.py for search method
    check_file_content(r'src/database.py', r'def buscar_usuarios_por_numero', 'buscar_usuarios_por_numero method')
    
    # Check payment_history.py for fix
    check_file_content(r'src/payment_history.py', r'detalles_data\.get\(\'detalles\'', 'detalles extraction fix')
    
    # Check user_management.py for observations
    check_file_content(r'src/user_management.py', r'def show_observations', 'show_observations method')
    check_file_content(r'src/user_management.py', r'self\.obs_btn', 'Observations button')
    
    # Check for search by alphanum logic
    check_file_content(r'src/user_management.py', r'buscar_usuarios_por_numero', 'Alphanumeric search logic')

