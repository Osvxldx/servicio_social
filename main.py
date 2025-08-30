"""
Sistema de Gestión de Pago de Agua
Aplicación Principal
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QFont, QIcon

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from database.database_manager import DatabaseManager

class WaterManagementApp:
    """Clase principal de la aplicación"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.setup_application()
        self.main_window = None
        
    def setup_application(self):
        """Configura la aplicación"""
        self.app.setApplicationName("Sistema de Gestión de Agua")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("Gestión Municipal")
        
        # Configurar estilo global
        self.app.setStyle('Fusion')
        
    def show_splash_screen(self):
        """Muestra la pantalla de carga"""
        # Crear splash screen simple
        splash_pixmap = QPixmap(400, 300)
        splash_pixmap.fill(Qt.white)
        
        painter = QPainter(splash_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fondo azul
        painter.fillRect(splash_pixmap.rect(), Qt.blue)
        
        # Texto
        painter.setPen(Qt.white)
        font = QFont("Arial", 24, QFont.Bold)
        painter.setFont(font)
        painter.drawText(splash_pixmap.rect(), Qt.AlignCenter, 
                        "💧\\nSistema de Gestión\\nde Agua\\n\\nCargando...")
        
        painter.end()
        
        # Mostrar splash
        splash = QSplashScreen(splash_pixmap)
        splash.show()
        
        # Procesar eventos para mostrar el splash
        self.app.processEvents()
        
        # Simular carga (verificar base de datos)
        QTimer.singleShot(2000, splash.close)
        QTimer.singleShot(2500, self.show_login)
        
        return splash
    
    def show_login(self):
        """Muestra la ventana de login"""
        try:
            login_window = LoginWindow()
            login_window.login_successful.connect(self.show_main_window)
            
            if login_window.exec_() != LoginWindow.Accepted:
                # El usuario canceló o cerró el login
                self.app.quit()
                
        except Exception as e:
            QMessageBox.critical(None, "Error", 
                               f"Error al inicializar el sistema de login:\\n{str(e)}")
            self.app.quit()
    
    def show_main_window(self):
        """Muestra la ventana principal"""
        try:
            self.main_window = MainWindow()
            self.main_window.show()
            
            # Centrar la ventana en la pantalla
            self.center_window(self.main_window)
            
        except Exception as e:
            QMessageBox.critical(None, "Error", 
                               f"Error al inicializar la ventana principal:\\n{str(e)}")
            self.app.quit()
    
    def center_window(self, window):
        """Centra una ventana en la pantalla"""
        screen = self.app.primaryScreen().geometry()
        window_rect = window.geometry()
        
        x = (screen.width() - window_rect.width()) // 2
        y = (screen.height() - window_rect.height()) // 2
        
        window.move(x, y)
    
    def verify_database(self):
        """Verifica que la base de datos esté funcionando correctamente"""
        try:
            db_manager = DatabaseManager()
            # Intentar una operación simple para verificar la conexión
            db_manager.get_statistics()
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error de Base de Datos", 
                               f"No se pudo conectar a la base de datos:\\n{str(e)}\\n\\n"
                               "Verifique que el directorio 'database' existe y tiene permisos de escritura.")
            return False
    
    def run(self):
        """Ejecuta la aplicación"""
        try:
            # Verificar base de datos
            if not self.verify_database():
                return 1
            
            # Mostrar splash screen
            splash = self.show_splash_screen()
            
            # Ejecutar aplicación
            return self.app.exec_()
            
        except Exception as e:
            QMessageBox.critical(None, "Error Fatal", 
                               f"Error fatal en la aplicación:\\n{str(e)}")
            return 1

def main():
    """Función principal"""
    try:
        # Crear y ejecutar la aplicación
        app = WaterManagementApp()
        exit_code = app.run()
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\\nAplicación interrumpida por el usuario")
        sys.exit(0)
        
    except Exception as e:
        print(f"Error fatal: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
