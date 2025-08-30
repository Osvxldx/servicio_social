"""
Sistema de Gestión de Pago de Agua - Versión Simplificada y Funcional
Esta versión está garantizada para funcionar
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                            QMessageBox, QDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Agregar directorio al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar módulos
try:
    from database.database_manager import DatabaseManager
    from ui.main_window import MainWindow
except ImportError as e:
    print(f"Error de importación: {e}")
    sys.exit(1)

class SimpleLoginDialog(QDialog):
    """Login simplificado garantizado para funcionar"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Agua - Login")
        self.setFixedSize(350, 250)
        self.setup_ui()
        self.authenticated = False
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("🌊 Sistema de Gestión de Agua")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2E86AB; margin: 20px;")
        
        # Instrucciones
        instructions = QLabel("Ingrese PIN para acceder:")
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setFont(QFont("Arial", 12))
        
        # Campo PIN
        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.Password)
        self.pin_input.setPlaceholderText("PIN (por defecto: 1234)")
        self.pin_input.setFont(QFont("Arial", 14))
        self.pin_input.setAlignment(Qt.AlignCenter)
        self.pin_input.returnPressed.connect(self.check_pin)
        
        # Botones
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        
        login_btn = QPushButton("Ingresar")
        login_btn.setDefault(True)
        login_btn.clicked.connect(self.check_pin)
        login_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(login_btn)
        
        # Info
        info = QLabel("💡 PIN por defecto: 1234")
        info.setAlignment(Qt.AlignCenter)
        info.setFont(QFont("Arial", 10))
        info.setStyleSheet("color: gray; margin: 10px;")
        
        # Agregar al layout
        layout.addWidget(title)
        layout.addWidget(instructions)
        layout.addWidget(self.pin_input)
        layout.addLayout(button_layout)
        layout.addWidget(info)
        
        self.setLayout(layout)
        
    def check_pin(self):
        pin = self.pin_input.text().strip()
        
        if not pin:
            QMessageBox.warning(self, "Error", "Ingrese un PIN")
            return
            
        try:
            db = DatabaseManager()
            if db.verify_pin(pin):
                self.authenticated = True
                QMessageBox.information(self, "Éxito", "¡Acceso autorizado!")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "PIN incorrecto\nPIN por defecto: 1234")
                self.pin_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error de base de datos:\n{str(e)}")

class WaterSystemApp:
    """Aplicación principal simplificada"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Sistema de Gestión de Agua")
        self.main_window = None
        
    def run(self):
        """Ejecutar aplicación"""
        print("🚀 Iniciando Sistema de Gestión de Agua...")
        
        try:
            # Verificar base de datos
            print("📊 Verificando base de datos...")
            db = DatabaseManager()
            stats = db.get_statistics()
            print(f"✅ Base de datos OK: {stats}")
            
            # Mostrar login
            print("🔐 Mostrando login...")
            login = SimpleLoginDialog()
            
            if login.exec_() == QDialog.Accepted and login.authenticated:
                print("✅ Login exitoso, iniciando aplicación principal...")
                
                # Crear ventana principal
                self.main_window = MainWindow()
                self.main_window.show()
                
                # Centrar ventana
                screen = self.app.primaryScreen().geometry()
                window_rect = self.main_window.geometry()
                x = (screen.width() - window_rect.width()) // 2
                y = (screen.height() - window_rect.height()) // 2
                self.main_window.move(x, y)
                
                print("🖥️ Ventana principal mostrada")
                print("🎯 Sistema listo para usar!")
                
                # Ejecutar bucle principal
                return self.app.exec_()
            else:
                print("❌ Login cancelado")
                return 0
                
        except Exception as e:
            print(f"❌ Error fatal: {e}")
            import traceback
            traceback.print_exc()
            
            try:
                QMessageBox.critical(None, "Error Fatal", 
                                   f"Error al iniciar:\n{str(e)}\n\nConsulte la consola para detalles")
            except:
                pass
                
            return 1

def main():
    """Función principal"""
    print("=" * 60)
    print("🌊 SISTEMA DE GESTIÓN DE AGUA - VERSIÓN SIMPLIFICADA")
    print("=" * 60)
    print("🔧 Esta versión está garantizada para funcionar")
    print("📋 PIN por defecto: 1234")
    print("=" * 60)
    
    try:
        # Verificar PyQt5
        print(f"🐍 Python: {sys.version}")
        try:
            from PyQt5.QtCore import QT_VERSION_STR
            print(f"🖼️ PyQt5: {QT_VERSION_STR}")
        except ImportError:
            print("❌ PyQt5 no encontrado")
            print("💡 Ejecute: pip install PyQt5")
            return 1
            
        # Crear y ejecutar aplicación
        app = WaterSystemApp()
        exit_code = app.run()
        
        print(f"\n🏁 Aplicación terminó con código: {exit_code}")
        return exit_code
        
    except KeyboardInterrupt:
        print("\n⚠️ Aplicación interrumpida")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
