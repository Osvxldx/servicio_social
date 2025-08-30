"""
SOLUCIÓN DEFINITIVA AL PROBLEMA DEL LOGIN
Sistema de Gestión de Pago de Agua - Versión Final
"""

import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from database.database_manager import DatabaseManager

def main():
    """Función principal simplificada y robusta"""
    print("=" * 60)
    print("🌊 SISTEMA DE GESTIÓN DE PAGO DE AGUA - VERSIÓN FINAL")
    print("=" * 60)
    
    # Crear aplicación
    app = QApplication(sys.argv)
    app.setApplicationName("Sistema de Gestión de Agua")
    app.setApplicationVersion("1.0.0")
    app.setStyle('Fusion')
    
    try:
        # 1. Verificar base de datos
        print("📊 Verificando base de datos...")
        db_manager = DatabaseManager()
        stats = db_manager.get_statistics()
        print(f"✅ Base de datos OK: {stats}")
        
        # 2. Crear y mostrar login
        print("🔐 Creando ventana de login...")
        login_window = LoginWindow()
        
        # Variable para mantener referencia a main_window
        main_window = None
        
        def show_main_app():
            """Función para mostrar la ventana principal"""
            nonlocal main_window
            try:
                print("🖥️ Creando ventana principal...")
                main_window = MainWindow()
                
                print("👁️ Mostrando ventana principal...")
                main_window.show()
                main_window.raise_()
                main_window.activateWindow()
                
                print("✅ Ventana principal mostrada exitosamente!")
                
                # Cerrar ventana de login
                login_window.close()
                
            except Exception as e:
                print(f"❌ Error al mostrar ventana principal: {e}")
                traceback.print_exc()
                QMessageBox.critical(None, "Error", 
                                   f"Error al mostrar ventana principal:\\n{str(e)}")
                app.quit()
        
        # Conectar señal
        login_window.login_successful.connect(show_main_app)
        
        print("🔐 Mostrando ventana de login...")
        print("📋 PIN por defecto: 1234")
        
        # Mostrar login
        result = login_window.exec_()
        
        if result == LoginWindow.Accepted:
            print("✅ Login aceptado")
            # Si el login fue exitoso, ejecutar el bucle principal
            if main_window is not None:
                print("🚀 Ejecutando aplicación principal...")
                return app.exec_()
            else:
                print("❌ No se pudo crear la ventana principal")
                return 1
        else:
            print("❌ Login cancelado")
            return 0
            
    except Exception as e:
        print(f"❌ Error fatal: {str(e)}")
        traceback.print_exc()
        try:
            QMessageBox.critical(None, "Error Fatal", 
                               f"Error fatal:\\n{str(e)}\\n\\nRevise la consola para más detalles.")
        except:
            pass
        return 1

if __name__ == "__main__":
    exit_code = main()
    print(f"🏁 Aplicación terminó con código: {exit_code}")
    sys.exit(exit_code)
