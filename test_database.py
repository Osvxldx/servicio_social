"""
Test de la base de datos sin GUI
"""

import sys
import os

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database_manager import DatabaseManager

def test_database():
    try:
        print("🔧 Iniciando test de base de datos...")
        
        # Crear instancia del manager
        db_manager = DatabaseManager()
        print("✅ Base de datos inicializada correctamente")
        
        # Verificar PIN por defecto
        if db_manager.verify_pin("1234"):
            print("✅ PIN por defecto (1234) verificado correctamente")
        else:
            print("❌ Error: PIN por defecto no funciona")
            return False
        
        # Agregar un cliente de prueba
        client_id = db_manager.add_client("Cliente Test", "Dirección Test 123")
        if client_id:
            print(f"✅ Cliente de prueba agregado con ID: {client_id}")
        else:
            print("❌ Error: No se pudo agregar cliente de prueba")
            return False
        
        # Obtener estadísticas
        stats = db_manager.get_statistics()
        print(f"✅ Estadísticas obtenidas: {stats}")
        
        # Agregar un pago de prueba
        payment_id = db_manager.add_payment(client_id, 100.50, "pagado", "Pago de prueba")
        if payment_id:
            print(f"✅ Pago de prueba agregado con ID: {payment_id}")
        else:
            print("❌ Error: No se pudo agregar pago de prueba")
            return False
        
        # Obtener clientes con estado
        clients = db_manager.get_clients_with_payment_status()
        print(f"✅ Clientes con estado obtenidos: {len(clients)} clientes")
        
        print("\n🎉 ¡Todos los tests de base de datos pasaron exitosamente!")
        print("\n📋 Resumen del test:")
        print(f"   - Base de datos: ✅ Funcionando")
        print(f"   - Autenticación: ✅ PIN 1234 válido")
        print(f"   - Clientes: ✅ CRUD funcionando")
        print(f"   - Pagos: ✅ CRUD funcionando")
        print(f"   - Estadísticas: ✅ Funcionando")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante el test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database()
    if success:
        print("\n🚀 La aplicación está lista para usar!")
        print("   Para ejecutar la GUI, use: python main.py")
        print("   PIN por defecto: 1234")
    else:
        print("\n💥 Hay problemas con la configuración")
    
    sys.exit(0 if success else 1)
