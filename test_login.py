"""
Test específico para identificar el problema del login
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from database.database_manager import DatabaseManager

def test_login_flow():
    """Test del flujo completo de login"""
    
    print("🧪 Iniciando test de login...")
    
    # Crear aplicación
    app = QApplication(sys.argv)
    
    try:
        # 1. Verificar base de datos
        print("📊 Verificando base de datos...")
        db_manager = DatabaseManager()
        stats = db_manager.get_statistics()
        print(f"✅ Base de datos OK: {stats}")
        
        # 2. Test del login window
        print("🔐 Creando ventana de login...")
        login_window = LoginWindow()
        print("✅ Login window creada exitosamente")
        
        # 3. Test de verificación de PIN
        print("🔑 Probando verificación de PIN...")
        pin_valid = db_manager.verify_pin("1234")
        print(f"✅ PIN 1234 válido: {pin_valid}")
        
        # 4. Test de main window
        print("🖥️ Creando ventana principal...")
        main_window = MainWindow()
        print("✅ Main window creada exitosamente")
        
        # 5. Mostrar main window
        print("👁️ Mostrando ventana principal...")
        main_window.show()
        print("✅ Main window mostrada")
        
        # Configurar timer para cerrar automáticamente
        def close_app():
            print("⏰ Cerrando aplicación automáticamente...")
            main_window.close()
            app.quit()
        
        QTimer.singleShot(3000, close_app)  # Cerrar después de 3 segundos
        
        # Ejecutar aplicación
        print("🚀 Ejecutando aplicación...")
        result = app.exec_()
        print(f"✅ Aplicación terminó con código: {result}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error en test: {str(e)}")
        import traceback
        traceback.print_exc()
        
        QMessageBox.critical(None, "Error en Test", 
                           f"Error durante el test:\\n{str(e)}")
        return 1

def test_login_only():
    """Test solo del login"""
    
    print("🧪 Test solo de login...")
    
    app = QApplication(sys.argv)
    
    try:
        # Crear y mostrar login
        login_window = LoginWindow()
        
        def on_login_success():
            print("✅ Login exitoso detectado!")
            QMessageBox.information(None, "Éxito", "Login exitoso!")
            app.quit()
        
        login_window.login_successful.connect(on_login_success)
        
        print("🔐 Mostrando ventana de login...")
        print("📝 Use PIN: 1234")
        
        result = login_window.exec_()
        
        if result == LoginWindow.Accepted:
            print("✅ Login aceptado")
        else:
            print("❌ Login cancelado")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 TEST DE LOGIN - Sistema de Gestión de Agua")
    print("=" * 50)
    
    # Preguntar qué test ejecutar
    print("Seleccione el test a ejecutar:")
    print("1. Test completo (login + main window)")
    print("2. Test solo login")
    
    try:
        choice = input("Ingrese su elección (1 o 2): ").strip()
        
        if choice == "1":
            exit_code = test_login_flow()
        elif choice == "2":
            exit_code = test_login_only()
        else:
            print("❌ Opción inválida")
            exit_code = 1
            
        print(f"🏁 Test terminado con código: {exit_code}")
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\\n⚠️ Test interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error fatal: {str(e)}")
        sys.exit(1)
