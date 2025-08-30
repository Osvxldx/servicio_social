"""
Sistema de Gestión de Pago de Agua
Módulo: Ventana de Login con PIN
"""

import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon
from database.database_manager import DatabaseManager
from styles.app_styles import LOGIN_STYLE

class LoginWindow(QDialog):
    # Señal emitida cuando el login es exitoso
    login_successful = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.init_ui()
        self.setStyleSheet(LOGIN_STYLE)
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Sistema de Gestión de Agua - Login")
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Título
        title_label = QLabel("💧 Sistema de Gestión de Agua")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("QLabel { font-size: 24px; font-weight: bold; color: white; }")
        
        # Subtítulo
        subtitle_label = QLabel("Acceso de Administrador")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("QLabel { font-size: 16px; color: white; margin-bottom: 30px; }")
        
        # Campo de PIN
        pin_label = QLabel("Ingrese su PIN:")
        pin_label.setAlignment(Qt.AlignCenter)
        
        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.Password)
        self.pin_input.setMaxLength(6)
        self.pin_input.setPlaceholderText("PIN de 4-6 dígitos")
        self.pin_input.returnPressed.connect(self.verify_pin)
        
        # Botones
        button_layout = QHBoxLayout()
        
        self.login_button = QPushButton("Ingresar")
        self.login_button.setDefault(True)
        self.login_button.clicked.connect(self.verify_pin)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.cancel_button)
        
        # Agregar elementos al layout principal
        main_layout.addWidget(title_label)
        main_layout.addWidget(subtitle_label)
        main_layout.addWidget(pin_label)
        main_layout.addWidget(self.pin_input)
        main_layout.addLayout(button_layout)
        
        # Información adicional
        info_label = QLabel("PIN por defecto: 1234")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("QLabel { font-size: 12px; color: rgba(255,255,255,0.7); margin-top: 20px; }")
        main_layout.addWidget(info_label)
        
        self.setLayout(main_layout)
        
        # Enfocar el campo de PIN
        self.pin_input.setFocus()
    
    def verify_pin(self):
        """Verifica el PIN ingresado"""
        pin = self.pin_input.text().strip()
        
        if not pin:
            QMessageBox.warning(self, "Error", "Por favor ingrese un PIN")
            return
        
        if len(pin) < 4:
            QMessageBox.warning(self, "Error", "El PIN debe tener al menos 4 dígitos")
            return
        
        # Verificar PIN en la base de datos
        if self.db_manager.verify_pin(pin):
            self.login_successful.emit()
            self.accept()
        else:
            QMessageBox.critical(self, "Error de Acceso", 
                               "PIN incorrecto. Intente nuevamente.")
            self.pin_input.clear()
            self.pin_input.setFocus()
    
    def keyPressEvent(self, event):
        """Maneja eventos de teclado"""
        if event.key() == Qt.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Configurar la aplicación
    app.setApplicationName("Sistema de Gestión de Agua")
    app.setApplicationVersion("1.0")
    
    # Mostrar ventana de login
    login = LoginWindow()
    
    if login.exec_() == QDialog.Accepted:
        print("Login exitoso!")
    else:
        print("Login cancelado")
    
    sys.exit()
