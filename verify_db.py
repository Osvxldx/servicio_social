from src.database import get_db_manager

db = get_db_manager()
conn = db.get_connection()
cursor = conn.cursor()

print("Checking 'usuarios' table info:")
cursor.execute("PRAGMA table_info(usuarios)")
columns = {info[1]: info for info in cursor.fetchall()}

required = ['tomas', 'fecha_alta', 'fecha_baja', 'estado']
for req in required:
    if req in columns:
        print(f"  [OK] Column '{req}' exists.")
    else:
        print(f"  [FAIL] Column '{req}' MISSING.")

print("\nChecking 'estado' check constraint (indirectly via insert):")
try:
    cursor.execute("INSERT INTO usuarios (nombre, sesion, estado) VALUES ('Test Baja', 1, 'Baja')")
    print("  [OK] Inserted user with status 'Baja'.")
    conn.rollback()
except Exception as e:
    print(f"  [FAIL] Could not insert 'Baja': {e}")

conn.close()
