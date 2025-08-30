"""
Sistema de Gestión de Pago de Agua - Versión Final Corregida
Aplicación Principal con Todos los Problemas Solucionados
"""

import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen, QProgressBar, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QFont, QColor

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.login_window_fixed import LoginWindowFixed
from ui.main_window import MainWindow
from database.database_manager import DatabaseManager

class InitThread(QThread):
    """Hilo para inicialización en background"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    
    def run(self):
        try:
            self.progress.emit(10, "Verificando Python...")
            
            self.progress.emit(25, "Verificando PyQt5...")
            from PyQt5.QtCore import QT_VERSION_STR
            
            self.progress.emit(50, "Inicializando base de datos...")
            db_manager = DatabaseManager()
            stats = db_manager.get_statistics()
            
            self.progress.emit(75, "Verificando integridad...")
            # Verificación adicional
            db_manager.verify_pin("1234")
            
            self.progress.emit(100, "Sistema listo!")
            self.finished.emit(True, f"Sistema iniciado. Clientes: {stats['total_clients']}")
            
        except Exception as e:
            self.finished.emit(False, str(e))

class SplashScreenFixed(QSplashScreen):
    """Splash screen mejorado con progreso"""
    
    def __init__(self):
        # Crear imagen de splash
        pixmap = QPixmap(500, 350)
        pixmap.fill(QColor(46, 134, 171))  # Color azul agua
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fondo degradado
        painter.fillRect(pixmap.rect(), QColor(46, 134, 171))
        
        # Texto principal
        painter.setPen(Qt.white)
        font = QFont("Arial", 24, QFont.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect().adjusted(0, 0, 0, -100), Qt.AlignCenter, 
                        "💧 Sistema de Gestión\nde Pago de Agua")
        
        # Versión
        font = QFont("Arial", 12)
        painter.setFont(font)
        painter.drawText(pixmap.rect().adjusted(0, 100, 0, 0), Qt.AlignCenter, 
                        "Versión 1.0 - Inicializando...")
        
        painter.end()
        
        super().__init__(pixmap)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        
        # Configurar progreso
        self.progress_value = 0
        self.status_text = "Iniciando..."
        
    def update_progress(self, value, text):
        """Actualiza el progreso en el splash"""
        self.progress_value = value
        self.status_text = text
        self.showMessage(f"{text} ({value}%)", Qt.AlignBottom | Qt.AlignCenter, Qt.white)
        QApplication.processEvents()

class WaterManagementAppFixed:
    """Aplicación principal completamente corregida"""
    
    def __init__(self):
        # Configurar aplicación
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Sistema de Gestión de Agua")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("Gestión Municipal")
        self.app.setStyle('Fusion')
        
        # Variables de estado
        self.main_window = None
        self.splash = None
        self.init_thread = None
    
    def show_splash_and_init(self):
        """Muestra splash screen y ejecuta inicialización"""
        try:
            # Crear y mostrar splash
            self.splash = SplashScreenFixed()
            self.splash.show()
            self.app.processEvents()
            
            # Crear hilo de inicialización
            self.init_thread = InitThread()
            self.init_thread.progress.connect(self.splash.update_progress)
            self.init_thread.finished.connect(self.on_init_finished)
            self.init_thread.start()
            
            return True
            
        except Exception as e:
            print(f"Error en splash: {e}")
            return False
    
    def on_init_finished(self, success, message):
        """Callback cuando termina la inicialización"""
        try:
            if self.splash:
                self.splash.finish(None)
            
            if success:
                print(f"✅ Inicialización exitosa: {message}")
                QTimer.singleShot(500, self.show_login)
            else:
                print(f"❌ Error en inicialización: {message}")
                QMessageBox.critical(None, "Error de Inicialización", 
                                   f"No se pudo inicializar el sistema:\n{message}")
                self.app.quit()
                
        except Exception as e:
            print(f"Error en callback: {e}")
            self.app.quit()
    
    def show_login(self):
        """Muestra la ventana de login mejorada"""
        print("🔐 Mostrando login...")
        
        try:
            # Crear ventana de login mejorada
            self.login_window = LoginWindowFixed()
            
            # Conectar señal
            self.login_window.login_successful.connect(self.on_login_success)
            
            # Mostrar login
            result = self.login_window.exec_()
            
            if result != LoginWindowFixed.Accepted:
                print("❌ Login cancelado")
                self.app.quit()
                
        except Exception as e:
            print(f"❌ Error en login: {e}")
            traceback.print_exc()
            QMessageBox.critical(None, "Error de Login", 
                               f"Error en el sistema de login:\n{str(e)}")
            self.app.quit()
    
    def on_login_success(self):
        """Maneja el login exitoso"""
        print("✅ Login exitoso, creando ventana principal...")
        
        try:
            # Cerrar login
            if hasattr(self, 'login_window'):
                self.login_window.close()
            
            # Crear main window
            QTimer.singleShot(300, self.create_main_window)
            
        except Exception as e:
            print(f"Error en login success: {e}")
            traceback.print_exc()
    
    def create_main_window(self):
        """Crea y muestra la ventana principal"""
        print("🖥️ Creando ventana principal...")
        
        try:
            # Mostrar mensaje de carga
            loading_msg = QMessageBox()
            loading_msg.setWindowTitle("Cargando...")
            loading_msg.setText("🔄 Inicializando interfaz principal...")
            loading_msg.setStandardButtons(QMessageBox.NoButton)
            loading_msg.show()
            self.app.processEvents()
            
            # Crear ventana principal
            self.main_window = MainWindow()
            
            # Cerrar mensaje de carga
            loading_msg.close()
            
            # Mostrar ventana principal
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
            
            # Centrar ventana
            self.center_window()
            
            print("✅ Ventana principal creada y mostrada exitosamente!")
            
        except Exception as e:
            print(f"❌ Error al crear ventana principal: {e}")
            traceback.print_exc()
            
            error_details = f"""Error al crear la ventana principal:

{str(e)}

Detalles técnicos:
{traceback.format_exc()}

Posibles soluciones:
1. Verificar que PyQt5 esté completamente instalado
2. Ejecutar: pip install --upgrade PyQt5
3. Reiniciar la aplicación
4. Contactar soporte técnico
"""
            
            QMessageBox.critical(None, "Error Crítico", error_details)
            self.app.quit()
    
    def center_window(self):
        """Centra la ventana principal en la pantalla"""
        try:
            if self.main_window:
                screen = self.app.primaryScreen().geometry()
                window_rect = self.main_window.geometry()
                
                x = (screen.width() - window_rect.width()) // 2
                y = (screen.height() - window_rect.height()) // 2
                
                self.main_window.move(x, y)
                
        except Exception as e:
            print(f"Error al centrar ventana: {e}")
    
    def run(self):
        """Ejecuta la aplicación"""
        print("🚀 Iniciando Sistema de Gestión de Agua...")
        print("🐍 Python:", sys.version)
        
        try:
            # Mostrar splash e inicializar
            if not self.show_splash_and_init():
                return 1
            
            # Ejecutar bucle principal
            print("🎯 Ejecutando bucle principal de la aplicación...")
            return self.app.exec_()
            
        except Exception as e:
            print(f"❌ Error fatal en run(): {e}")
            traceback.print_exc()
            return 1

def main():
    """Función principal con manejo completo de errores"""
    print("=" * 70)
    print("🌊 SISTEMA DE GESTIÓN DE PAGO DE AGUA - VERSIÓN FINAL")
    print("=" * 70)
    
    try:
        # Verificar entorno
        print(f"🐍 Python: {sys.version}")
        
        # Verificar PyQt5
        try:
            from PyQt5.QtCore import QT_VERSION_STR
            print(f"🖼️ PyQt5: {QT_VERSION_STR}")
        except ImportError as e:
            print(f"❌ Error: PyQt5 no está instalado correctamente")
            print(f"   Ejecute: pip install PyQt5")
            return 1
        
        # Crear aplicación
        app = WaterManagementAppFixed()
        
        # Ejecutar
        exit_code = app.run()
        
        print(f"🏁 Aplicación terminada con código: {exit_code}")
        return exit_code
        
    except KeyboardInterrupt:
        print("\n⚠️ Aplicación interrumpida por el usuario")
        return 0
        
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
