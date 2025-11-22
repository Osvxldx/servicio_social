#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para generación de recibos
"""

from database import get_db_manager
from receipt_generator import ReceiptGenerator
import traceback

def test_receipt_generation():
    """Prueba la generación de recibos"""
    try:
        print("="*50)
        print("PRUEBA DE GENERACIÓN DE RECIBOS")
        print("="*50)
        
        # 1. Verificar base de datos
        print("\n1. Conectando a la base de datos...")
        db = get_db_manager()
        print("✓ Conexión exitosa")
        
        # 2. Obtener último pago
        print("\n2. Buscando pagos registrados...")
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, usuario_id, total, fecha_pago FROM pagos ORDER BY id DESC LIMIT 1")
        pago = cursor.fetchone()
        conn.close()
        
        if not pago:
            print("✗ No hay pagos registrados en la base de datos")
            print("\nDebes:")
            print("  1. Abrir el programa")
            print("  2. Ir a 'Registro de Pagos'")
            print("  3. Seleccionar un usuario")
            print("  4. Seleccionar meses y registrar un pago")
            return False
        
        pago_id = pago['id']
        print(f"✓ Encontrado pago ID: {pago_id}")
        print(f"  - Usuario ID: {pago['usuario_id']}")
        print(f"  - Fecha: {pago['fecha_pago']}")
        print(f"  - Total: ${pago['total']:.2f}")
        
        # 3. Obtener detalle del pago
        print("\n3. Obteniendo detalle del pago...")
        pago_data = db.obtener_detalle_pago(pago_id)
        
        if not pago_data:
            print(f"✗ No se pudo obtener detalle del pago {pago_id}")
            return False
        
        print("✓ Detalle obtenido correctamente")
        print(f"  - Usuario: {pago_data.get('nombre', 'N/A')}")
        print(f"  - Número: {pago_data.get('numero', 'N/A')}")
        print(f"  - Detalles: {len(pago_data.get('detalles', []))} items")
        
        # Mostrar estructura completa para debugging
        import json
        print("\nEstructura completa del pago:")
        print(json.dumps(pago_data, indent=2, default=str))
        
        # 4. Generar recibo
        print("\n4. Generando recibo PDF...")
        generator = ReceiptGenerator()
        pdf_path = generator.generate_receipt(pago_id)
        
        if pdf_path:
            print(f"✓ Recibo generado exitosamente!")
            print(f"  Ubicación: {pdf_path}")
            
            import os
            if os.path.exists(pdf_path):
                size = os.path.getsize(pdf_path)
                print(f"  Tamaño: {size} bytes")
                
                # Preguntar si quiere abrirlo
                respuesta = input("\n¿Desea abrir el recibo? (s/n): ")
                if respuesta.lower() == 's':
                    os.startfile(pdf_path)
            else:
                print("✗ El archivo no existe después de generarlo")
                return False
        else:
            print("✗ Error: generate_receipt retornó None")
            return False
        
        print("\n" + "="*50)
        print("PRUEBA COMPLETADA EXITOSAMENTE")
        print("="*50)
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        print("\nTraceback completo:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_receipt_generation()
    input("\nPresione Enter para salir...")
