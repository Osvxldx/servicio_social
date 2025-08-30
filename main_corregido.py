"""
Sistema de Gestión de Pago de Agua - Versión Corregida
Aplicación Principal con Manejo Mejorado de Errores
"""

import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QFont

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from database.database_manager import DatabaseManager

class WaterManagementApp:
    """Clase principal de la aplicación con manejo mejorado de errores"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.setup_application()
        self.main_window = None
        
    def setup_application(self):
        """Configura la aplicación"""
        self.app.setApplicationName("Sistema de Gestión de Agua")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("Gestión Municipal")
        self.app.setStyle('Fusion')
        
    def show_splash_screen(self):
        """Muestra la pantalla de carga"""
        try:
            splash_pixmap = QPixmap(400, 300)
            splash_pixmap.fill(Qt.blue)
            
            painter = QPainter(splash_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(Qt.white)
            font = QFont("Arial", 20, QFont.Bold)
            painter.setFont(font)
            painter.drawText(splash_pixmap.rect(), Qt.AlignCenter, 
                            "💧\nSistema de Gestión\nde Agua\n\nCargando...")
            painter.end()
            
            splash = QSplashScreen(splash_pixmap)
            splash.show()
            self.app.processEvents()
            
            # Programar cierre del splash y mostrar login
            QTimer.singleShot(1500, splash.close)
            QTimer.singleShot(2000, self.show_login)
            
            return splash
            
        except Exception as e:
            print(f"Error en splash screen: {e}")
            # Si falla el splash, mostrar login directamente
            QTimer.singleShot(100, self.show_login)
            return None
    
    def show_login(self):
        """Muestra la ventana de login con manejo mejorado"""
        print("🔐 Iniciando ventana de login...")
        
        try:
            # Crear ventana de login
            self.login_window = LoginWindow()
            
            # Conectar señal de login exitoso
            self.login_window.login_successful.connect(self.on_login_success)
            
            print("🔐 Mostrando ventana de login...")
            result = self.login_window.exec_()
            
            print(f"🔐 Resultado del login: {result}")
            
            if result != LoginWindow.Accepted:
                print("❌ Login cancelado o cerrado")
                self.app.quit()
                
        except Exception as e:
            print(f"❌ Error en login: {str(e)}")
            traceback.print_exc()
            QMessageBox.critical(None, "Error de Login", 
                               f"Error al inicializar el login:\n{str(e)}\n\nLa aplicación se cerrará.")
            self.app.quit()
    
    def on_login_success(self):
        """Maneja el login exitoso"""
        print("✅ Login exitoso! Iniciando ventana principal...")
        
        try:
            # Cerrar ventana de login
            if hasattr(self, 'login_window'):
                self.login_window.close()
            
            # Pequeña pausa para asegurar que el login se cierre
            QTimer.singleShot(100, self.create_main_window)
            
        except Exception as e:
            print(f"❌ Error en on_login_success: {str(e)}")
            traceback.print_exc()
    
    def create_main_window(self):
        """Crea y muestra la ventana principal"""
        print("🖥️ Creando ventana principal...")
        
        try:
            # Crear ventana principal
            self.main_window = MainWindow()
            
            print("🖥️ Ventana principal creada, mostrando...")
            
            # Mostrar ventana
            self.main_window.show()
            
            # Centrar ventana
            self.center_window(self.main_window)
            
            # Traer al frente
            self.main_window.raise_()
            self.main_window.activateWindow()
            
            print("✅ Ventana principal mostrada exitosamente!")
            
        except Exception as e:
            print(f"❌ Error al crear ventana principal: {str(e)}")
            traceback.print_exc()
            
            # Mostrar error detallado
            error_msg = f"""Error al inicializar la ventana principal:

{str(e)}

Detalles técnicos:
{traceback.format_exc()}

Posibles soluciones:
1. Verificar que todas las dependencias estén instaladas
2. Ejecutar: pip install PyQt5 matplotlib
3. Verificar permisos de la carpeta del proyecto
"""
            
            QMessageBox.critical(None, "Error Crítico", error_msg)
            self.app.quit()
    
    def center_window(self, window):
        """Centra una ventana en la pantalla"""
        try:
            screen = self.app.primaryScreen().geometry()
            window_rect = window.geometry()
            
            x = (screen.width() - window_rect.width()) // 2
            y = (screen.height() - window_rect.height()) // 2
            
            window.move(x, y)
            
        except Exception as e:
            print(f"Error al centrar ventana: {e}")
    
    def verify_database(self):
        """Verifica que la base de datos esté funcionando correctamente"""
        print("📊 Verificando base de datos...")
        
        try:
            db_manager = DatabaseManager()
            stats = db_manager.get_statistics()
            print(f"✅ Base de datos verificada: {stats}")
            return True
            
        except Exception as e:
            print(f"❌ Error de base de datos: {str(e)}")
            
            error_msg = f"""Error de Base de Datos:

{str(e)}

Soluciones:
1. Verificar que la carpeta 'database' existe
2. Verificar permisos de escritura en la carpeta
3. Ejecutar 'python test_database.py' para diagnóstico
"""
            
            QMessageBox.critical(None, "Error de Base de Datos", error_msg)
            return False
    
    def run(self):
        """Ejecuta la aplicación"""
        print("🚀 Iniciando Sistema de Gestión de Agua...")
        
        try:
            # 1. Verificar base de datos
            if not self.verify_database():
                print("❌ Error en base de datos, cerrando...")
                return 1
            
            # 2. Mostrar splash screen
            print("🎬 Mostrando splash screen...")
            splash = self.show_splash_screen()
            
            # 3. Ejecutar aplicación
            print("🎯 Ejecutando bucle principal...")
            return self.app.exec_()
            
        except Exception as e:
            print(f"❌ Error fatal en run(): {str(e)}")
            traceback.print_exc()
            
            QMessageBox.critical(None, "Error Fatal", 
                               f"Error fatal en la aplicación:\n{str(e)}")
            return 1

def main():
    """Función principal con manejo completo de errores"""
    print("=" * 60)
    print("🌊 SISTEMA DE GESTIÓN DE PAGO DE AGUA")
    print("=" * 60)
    
    try:
        # Verificar Python
        print(f"🐍 Python version: {sys.version}")
        
        # Verificar PyQt5
        try:
            from PyQt5.QtCore import QT_VERSION_STR
            print(f"🖼️ PyQt5 version: {QT_VERSION_STR}")
        except ImportError:
            print("❌ PyQt5 no encontrado. Ejecute: pip install PyQt5")
            return 1
        
        # Crear y ejecutar aplicación
        print("🚀 Creando aplicación...")
        app = WaterManagementApp()
        
        print("▶️ Ejecutando aplicación...")
        exit_code = app.run()
        
        print(f"🏁 Aplicación terminada con código: {exit_code}")
        return exit_code
        
    except KeyboardInterrupt:
        print("\n⚠️ Aplicación interrumpida por el usuario")
        return 0
        
    except Exception as e:
        print(f"❌ Error fatal: {str(e)}")
        traceback.print_exc()
        
        try:
            QMessageBox.critical(None, "Error Fatal", 
                               f"Error fatal:\n{str(e)}\n\nConsulte la consola para más detalles.")
        except:
            pass  # Si incluso el mensaje de error falla
        
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
