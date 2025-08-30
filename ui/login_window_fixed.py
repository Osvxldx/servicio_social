"""
Sistema de Gestión de Pago de Agua
Login Window - Versión Corregida y Completa
"""

import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QApplication,
                            QFrame, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette
from database.database_manager import DatabaseManager

# Estilos mejorados para el login
LOGIN_STYLE_FIXED = """
QDialog {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #2E86AB, stop: 1 #A23B72);
    border-radius: 15px;
}

QLabel#title {
    color: white;
    font-size: 28px;
    font-weight: bold;
    margin: 20px;
    text-align: center;
}

QLabel#subtitle {
    color: rgba(255, 255, 255, 0.9);
    font-size: 18px;
    margin: 10px;
    text-align: center;
}

QLabel#pin-label {
    color: white;
    font-size: 16px;
    font-weight: bold;
    margin: 10px;
}

QLineEdit {
    background-color: rgba(255, 255, 255, 0.9);
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 8px;
    padding: 12px 15px;
    font-size: 16px;
    font-weight: bold;
    text-align: center;
    margin: 10px;
    min-height: 20px;
}

QLineEdit:focus {
    border: 2px solid #FFD700;
    background-color: white;
}

QPushButton {
    background-color: rgba(255, 255, 255, 0.9);
    border: none;
    border-radius: 8px;
    padding: 12px 25px;
    font-size: 14px;
    font-weight: bold;
    color: #2E86AB;
    margin: 5px;
    min-width: 100px;
    min-height: 35px;
}

QPushButton:hover {
    background-color: #FFD700;
    color: #2E86AB;
}

QPushButton:pressed {
    background-color: #FFC700;
}

QPushButton#login-button {
    background-color: #4CAF50;
    color: white;
}

QPushButton#login-button:hover {
    background-color: #45a049;
}

QPushButton#cancel-button {
    background-color: #f44336;
    color: white;
}

QPushButton#cancel-button:hover {
    background-color: #da190b;
}

QLabel#info {
    color: rgba(255, 255, 255, 0.8);
    font-size: 12px;
    margin: 15px;
    text-align: center;
}

QFrame#container {
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    margin: 20px;
    padding: 20px;
}
"""

class LoginWindowFixed(QDialog):
    """Ventana de login corregida y completa"""
    login_successful = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.init_ui()
        self.setStyleSheet(LOGIN_STYLE_FIXED)
    
    def init_ui(self):
        """Inicializa la interfaz de usuario mejorada"""
        self.setWindowTitle("Sistema de Gestión de Agua - Login")
        self.setFixedSize(450, 400)
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Contenedor principal
        container = QFrame()
        container.setObjectName("container")
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(30, 30, 30, 30)
        
        # Spacer superior
        container_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Icono y título
        title_label = QLabel("💧 Sistema de Gestión de Agua")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(title_label)
        
        # Subtítulo
        subtitle_label = QLabel("Acceso de Administrador")
        subtitle_label.setObjectName("subtitle")
        subtitle_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(subtitle_label)
        
        # Spacer medio
        container_layout.addItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Etiqueta de PIN
        pin_label = QLabel("🔐 Ingrese su PIN:")
        pin_label.setObjectName("pin-label")
        pin_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(pin_label)
        
        # Campo de PIN
        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.Password)
        self.pin_input.setMaxLength(6)
        self.pin_input.setPlaceholderText("Ingrese PIN de 4-6 dígitos")
        self.pin_input.returnPressed.connect(self.verify_pin)
        container_layout.addWidget(self.pin_input)
        
        # Spacer
        container_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.cancel_button = QPushButton("❌ Cancelar")
        self.cancel_button.setObjectName("cancel-button")
        self.cancel_button.clicked.connect(self.reject)
        
        self.login_button = QPushButton("✅ Ingresar")
        self.login_button.setObjectName("login-button")
        self.login_button.setDefault(True)
        self.login_button.clicked.connect(self.verify_pin)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.login_button)
        
        container_layout.addLayout(button_layout)
        
        # Información adicional
        info_label = QLabel("💡 PIN por defecto: 1234")
        info_label.setObjectName("info")
        info_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(info_label)
        
        # Spacer inferior
        container_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Agregar container al layout principal
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        
        # Enfocar el campo de PIN
        self.pin_input.setFocus()
    
    def verify_pin(self):
        """Verifica el PIN ingresado con mejor manejo de errores"""
        pin = self.pin_input.text().strip()
        
        if not pin:
            QMessageBox.warning(self, "⚠️ PIN Requerido", 
                              "Por favor ingrese un PIN para continuar.")
            return
        
        if len(pin) < 4:
            QMessageBox.warning(self, "⚠️ PIN Inválido", 
                              "El PIN debe tener al menos 4 dígitos.")
            return
        
        try:
            # Verificar PIN en la base de datos
            if self.db_manager.verify_pin(pin):
                QMessageBox.information(self, "✅ Acceso Autorizado", 
                                      "PIN correcto. Iniciando sistema...")
                self.login_successful.emit()
                self.accept()
            else:
                QMessageBox.critical(self, "❌ Acceso Denegado", 
                                   "PIN incorrecto. Intente nuevamente.\n\n💡 PIN por defecto: 1234")
                self.pin_input.clear()
                self.pin_input.setFocus()
                
        except Exception as e:
            QMessageBox.critical(self, "❌ Error del Sistema", 
                               f"Error al verificar PIN:\n{str(e)}\n\nIntente nuevamente.")
            self.pin_input.clear()
            self.pin_input.setFocus()
    
    def keyPressEvent(self, event):
        """Maneja eventos de teclado"""
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.verify_pin()
        else:
            super().keyPressEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Sistema de Gestión de Agua")
    
    login = LoginWindowFixed()
    
    if login.exec_() == QDialog.Accepted:
        print("✅ Login exitoso!")
    else:
        print("❌ Login cancelado")
    
    sys.exit()
