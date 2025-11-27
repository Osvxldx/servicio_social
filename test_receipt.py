
from src.receipt_generator import ReceiptGenerator
from src.database import get_db_manager
import os

def test():
    db = get_db_manager()
    # Ensure we have a user
    users = db.obtener_todos_usuarios()
    if not users:
        db.crear_usuario("Juan Perez", 1, "Calle Falsa 123", "555-5555", "juan@example.com", vacas=2, inquilinos=1)
        users = db.obtener_todos_usuarios()
    
    user = users[0]
    
    # Create a dummy payment with all new fields
    # Note: The prices here are just for the record, the receipt generator might look up config for some calculations 
    # but uses these for the totals if logic dictates. 
    # Actually, my new receipt generator calculates some things from config (like unit prices) but sums up from details for others.
    # Let's try to match what payment_registration does.
    
    detalles = [
        {'concepto': 'Mensualidad', 'precio': 70.0, 'mes': 1, 'anio': 2025},
        {'concepto': 'Mensualidad', 'precio': 70.0, 'mes': 2, 'anio': 2025},
        {'concepto': 'Costo Vacas (2)', 'precio': 0.0, 'mes': 1, 'anio': 2025}, # Precio 0 si no se cobra por mes en detalle, pero el recibo lo calcula
        {'concepto': 'Multa por Retraso', 'precio': 100.0, 'anio': 2025},
        {'concepto': 'Cooperación', 'precio': 100.0, 'anio': 2025},
        {'concepto': 'Toma Nueva', 'precio': 500.0, 'anio': 2025},
        {'concepto': 'Multa por Inasistencia', 'precio': 200.0, 'anio': 2025}
    ]
    
    pago_id = db.registrar_pago(
        usuario_id=user['id'],
        detalles=detalles,
        observaciones="Prueba Completa Landscape"
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
