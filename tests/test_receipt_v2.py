
from src.receipt_generator import ReceiptGenerator
from src.database import get_db_manager
import os
from datetime import datetime

def test():
    db = get_db_manager()
    
    # Update config for testing
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO configuracion (clave, valor) VALUES ('costo_vacas', '10')")
    cursor.execute("INSERT OR REPLACE INTO configuracion (clave, valor) VALUES ('costo_inquilinos', '20')")
    conn.commit()
    conn.close()
    
    # Create user
    # sesion must be 1, 2, or 3
    db.crear_usuario("Test User Logic", 1, "Test Address", "555-0000", "test@test.com", vacas=2, inquilinos=1)
    # Get the user we just created
    users = db.buscar_usuarios_por_nombre("Test User Logic")
    if not users:
        print("Error: User not created")
        return
    user = users[-1]
    
    # Simulate Payment Registration Logic
    detalles = []
    
    # Month 1: Late (Jan 2024)
    # Base
    detalles.append({'concepto': 'Mensualidad', 'precio': 70.0, 'mes': 1, 'anio': 2024, 'cantidad': 1})
    # Recargo ($100 - $70 = $30)
    detalles.append({'concepto': 'Recargo Mes 1', 'precio': 30.0, 'mes': 1, 'anio': 2024, 'cantidad': 1})
    # Vacas (2 * $10)
    detalles.append({'concepto': 'Costo Vacas (2)', 'precio': 20.0, 'mes': 1, 'anio': 2024, 'cantidad': 1})
    # Inquilinos (1 * $20)
    detalles.append({'concepto': 'Costo Inquilinos (1)', 'precio': 20.0, 'mes': 1, 'anio': 2024, 'cantidad': 1})
    
    # Month 2: Current (Nov 2025) - Assume on time
    detalles.append({'concepto': 'Mensualidad', 'precio': 70.0, 'mes': 11, 'anio': 2025, 'cantidad': 1})
    # No Recargo
    # Vacas
    detalles.append({'concepto': 'Costo Vacas (2)', 'precio': 20.0, 'mes': 11, 'anio': 2025, 'cantidad': 1})
    # Inquilinos
    detalles.append({'concepto': 'Costo Inquilinos (1)', 'precio': 20.0, 'mes': 11, 'anio': 2025, 'cantidad': 1})
    
    # Extra
    detalles.append({'concepto': 'Cooperación', 'precio': 100.0, 'cantidad': 1, 'anio': 2025})

    pago_id = db.registrar_pago(
        usuario_id=user['id'],
        detalles=detalles,
        observaciones="Test Logic V2"
    )
    
    print(f"Pago registrado: {pago_id}")
    
    gen = ReceiptGenerator()
    path = gen.generate_receipt(pago_id)
    print(f"Recibo generado en: {path}")
    
    if path and os.path.exists(path):
        print("SUCCESS: File created.")
    else:
        print("FAILURE: File not created.")

if __name__ == "__main__":
    test()
