import sqlite3
import os

DB_NAME = "agua_potable.db"

def migrate():
    if not os.path.exists(DB_NAME):
        print(f"Error: Database {DB_NAME} not found.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # 1. Add 'numero_usuario' column
        try:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN numero_usuario TEXT")
            print("Added column 'numero_usuario'")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Column 'numero_usuario' already exists")
            else:
                raise e

        # 2. Add 'hidrantes' column
        try:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN hidrantes INTEGER DEFAULT 0")
            print("Added column 'hidrantes'")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Column 'hidrantes' already exists")
            else:
                raise e
        
        # 3. Populate 'numero_usuario' with 'id' (as string) for existing users if null
        cursor.execute("UPDATE usuarios SET numero_usuario = CAST(id AS TEXT) WHERE numero_usuario IS NULL")
        
        # 4. Add 'costo_hidrante' to configuration
        cursor.execute("INSERT OR IGNORE INTO configuracion (clave, valor) VALUES ('costo_hidrante', '50.0')")
        print("Added 'costo_hidrante' to configuration")

        conn.commit()
        print("Migration completed successfully.")

    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
