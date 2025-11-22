import tkinter as tk
from tkinter import ttk
import sys
import os
import traceback

# Mock database
class MockDB:
    def obtener_todos_usuarios(self):
        return []
    def buscar_usuario_por_id(self, id):
        return {}

sys.modules['database'] = type('module', (), {'get_db_manager': lambda: MockDB()})

try:
    import user_management
    
    print("Instantiating UserManagementWindow...")
    root = tk.Tk()
    
    # Patch the class to not use Singleton for testing or just clear it
    user_management.UserManagementWindow._instance = None
    
    try:
        app = user_management.UserManagementWindow(root)
        print("UserManagementWindow instantiated successfully.")
    except Exception as e:
        print(f"ERROR during instantiation: {e}")
        traceback.print_exc()
        
    root.destroy()

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    traceback.print_exc()
