import sys
import os
from unittest.mock import MagicMock
import sys

# Mock database module before importing receipt_generator
sys.modules['database'] = MagicMock()
from database import get_db_manager

# Setup mock return values
mock_db = MagicMock()
get_db_manager.return_value = mock_db

# Mock payment data with MANY items to test dynamic layout
detalles = []
# Add 6 months
for i in range(1, 7):
    detalles.append({'concepto': 'Mensualidad', 'mes': i, 'anio': 2024, 'precio': 50.0, 'cantidad': 1})

# Add some extra concepts
detalles.append({'concepto': 'Recargo por demora', 'mes': None, 'anio': 2024, 'precio': 10.0, 'cantidad': 1})
detalles.append({'concepto': 'Cooperación Fiesta Patronal', 'mes': None, 'anio': 2024, 'precio': 100.0, 'cantidad': 1})

mock_db.obtener_detalle_pago.return_value = {
    'id': 12345,
    'usuario_id': 100,
    'nombre': 'JUAN PEREZ CON MUCHOS PAGOS',
    'direccion': 'AV. INDEPENDENCIA #123, BARRIO SAN ANTONIO, TECAMACHALCO, PUEBLA (DIRECCION LARGA)',
    'sesion': 1,
    'detalles': detalles
}

# Import generator
from receipt_generator import ReceiptGenerator

print("--- Testing Receipt Generation (Stress Test) ---")
try:
    generator = ReceiptGenerator()
    # Mock os.path.exists for logo
    original_exists = os.path.exists
    os.path.exists = lambda p: True if p == "recibos" else original_exists(p)
    
    filepath = generator.generate_receipt(12345)
    
    if filepath:
        print(f"[OK] Receipt generated at: {filepath}")
    else:
        print("[FAIL] Receipt generation returned None")
        
except Exception as e:
    print(f"[FAIL] Error generating receipt: {e}")
    import traceback
    traceback.print_exc()

print("--- Test Completed ---")
