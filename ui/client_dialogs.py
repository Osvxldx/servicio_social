"""
Sistema de Gestión de Pago de Agua
Módulo: Diálogos para Gestión de Clientes
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLabel, QLineEdit, QPushButton, QComboBox, 
                            QTextEdit, QMessageBox, QGroupBox, QTabWidget,
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QSpinBox, QDoubleSpinBox, QDateEdit, QCheckBox)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont
from database.database_manager import DatabaseManager
from styles.app_styles import MAIN_STYLE

class ClientDialog(QDialog):
    """Diálogo para agregar/editar clientes"""
    client_saved = pyqtSignal()
    
    def __init__(self, client_id=None, parent=None):
        super().__init__(parent)
        self.client_id = client_id
        self.db_manager = DatabaseManager()
        self.is_edit_mode = client_id is not None
        self.init_ui()
        self.setStyleSheet(MAIN_STYLE)
        
        if self.is_edit_mode:
            self.load_client_data()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        title = "Editar Cliente" if self.is_edit_mode else "Agregar Nuevo Cliente"
        self.setWindowTitle(title)
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel(title)
        title_label.setObjectName("title")
        title_label.setStyleSheet("QLabel { font-size: 18px; font-weight: bold; color: #2196F3; margin-bottom: 20px; }")
        
        # Formulario
        form_layout = QFormLayout()
        
        # Campos del formulario
        if self.is_edit_mode:
            self.id_label = QLabel()
            form_layout.addRow("ID:", self.id_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre completo del cliente")
        form_layout.addRow("Nombre:", self.name_input)
        
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Dirección completa")
        form_layout.addRow("Dirección:", self.address_input)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["activo", "inactivo"])
        form_layout.addRow("Estado:", self.status_combo)
        
        # Botones
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Guardar")
        self.save_button.setDefault(True)
        self.save_button.clicked.connect(self.save_client)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        # Agregar elementos al layout
        layout.addWidget(title_label)
        layout.addLayout(form_layout)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Enfocar el primer campo
        self.name_input.setFocus()
    
    def load_client_data(self):
        """Carga los datos del cliente para edición"""
        try:
            client = self.db_manager.get_client(self.client_id)
            if client:
                self.id_label.setText(str(client['id']))
                self.name_input.setText(client['name'])
                self.address_input.setText(client['address'])
                
                # Seleccionar estado en combo
                index = self.status_combo.findText(client['status'])
                if index >= 0:
                    self.status_combo.setCurrentIndex(index)
            else:
                QMessageBox.critical(self, "Error", "No se encontró el cliente")
                self.reject()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar cliente: {str(e)}")
            self.reject()
    
    def save_client(self):
        """Guarda el cliente en la base de datos"""
        name = self.name_input.text().strip()
        address = self.address_input.text().strip()
        status = self.status_combo.currentText()
        
        # Validaciones
        if not name:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            self.name_input.setFocus()
            return
        
        if not address:
            QMessageBox.warning(self, "Error", "La dirección es obligatoria")
            self.address_input.setFocus()
            return
        
        try:
            if self.is_edit_mode:
                # Actualizar cliente existente
                success = self.db_manager.update_client(self.client_id, name, address, status)
                if success:
                    QMessageBox.information(self, "Éxito", "Cliente actualizado correctamente")
                    self.client_saved.emit()
                    self.accept()
                else:
                    QMessageBox.critical(self, "Error", "No se pudo actualizar el cliente")
            else:
                # Agregar nuevo cliente
                client_id = self.db_manager.add_client(name, address)
                if client_id:
                    QMessageBox.information(self, "Éxito", 
                                          f"Cliente agregado correctamente con ID: {client_id}")
                    self.client_saved.emit()
                    self.accept()
                else:
                    QMessageBox.critical(self, "Error", "No se pudo agregar el cliente")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar: {str(e)}")

class ClientProfileDialog(QDialog):
    """Diálogo para mostrar el perfil completo del cliente"""
    
    def __init__(self, client_id, parent=None):
        super().__init__(parent)
        self.client_id = client_id
        self.db_manager = DatabaseManager()
        self.init_ui()
        self.setStyleSheet(MAIN_STYLE)
        self.load_client_data()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Perfil del Cliente")
        self.setFixedSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Crear tabs
        tabs = QTabWidget()
        
        # Tab 1: Información del cliente
        self.create_info_tab(tabs)
        
        # Tab 2: Historial de pagos
        self.create_payments_tab(tabs)
        
        # Tab 3: Consumo de agua
        self.create_consumption_tab(tabs)
        
        # Botones
        button_layout = QHBoxLayout()
        
        edit_button = QPushButton("Editar Cliente")
        edit_button.clicked.connect(self.edit_client)
        
        add_payment_button = QPushButton("Registrar Pago")
        add_payment_button.setObjectName("secondary")
        add_payment_button.clicked.connect(self.add_payment)
        
        add_consumption_button = QPushButton("Registrar Consumo")
        add_consumption_button.setObjectName("warning")
        add_consumption_button.clicked.connect(self.add_consumption)
        
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(edit_button)
        button_layout.addWidget(add_payment_button)
        button_layout.addWidget(add_consumption_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        layout.addWidget(tabs)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def create_info_tab(self, tabs):
        """Crea la pestaña de información del cliente"""
        info_tab = QWidget()
        layout = QVBoxLayout()
        
        # Información básica
        info_group = QGroupBox("Información del Cliente")
        info_layout = QFormLayout()
        
        self.id_label = QLabel()
        self.name_label = QLabel()
        self.address_label = QLabel()
        self.status_label = QLabel()
        self.created_label = QLabel()
        
        info_layout.addRow("ID:", self.id_label)
        info_layout.addRow("Nombre:", self.name_label)
        info_layout.addRow("Dirección:", self.address_label)
        info_layout.addRow("Estado:", self.status_label)
        info_layout.addRow("Fecha de registro:", self.created_label)
        
        info_group.setLayout(info_layout)
        
        layout.addWidget(info_group)
        layout.addStretch()
        
        info_tab.setLayout(layout)
        tabs.addTab(info_tab, "Información")
    
    def create_payments_tab(self, tabs):
        """Crea la pestaña de historial de pagos"""
        payments_tab = QWidget()
        layout = QVBoxLayout()
        
        # Tabla de pagos
        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(5)
        self.payments_table.setHorizontalHeaderLabels([
            "ID", "Monto", "Fecha", "Estado", "Notas"
        ])
        
        # Configurar tabla
        header = self.payments_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        
        self.payments_table.setAlternatingRowColors(True)
        self.payments_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(QLabel("Historial de Pagos"))
        layout.addWidget(self.payments_table)
        
        payments_tab.setLayout(layout)
        tabs.addTab(payments_tab, "Pagos")
    
    def create_consumption_tab(self, tabs):
        """Crea la pestaña de consumo de agua"""
        consumption_tab = QWidget()
        layout = QVBoxLayout()
        
        # Tabla de consumo
        self.consumption_table = QTableWidget()
        self.consumption_table.setColumnCount(4)
        self.consumption_table.setHorizontalHeaderLabels([
            "ID", "Tipo", "Fecha", "Notas"
        ])
        
        # Configurar tabla
        header = self.consumption_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        
        self.consumption_table.setAlternatingRowColors(True)
        self.consumption_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(QLabel("Historial de Consumo"))
        layout.addWidget(self.consumption_table)
        
        consumption_tab.setLayout(layout)
        tabs.addTab(consumption_tab, "Consumo")
    
    def load_client_data(self):
        """Carga todos los datos del cliente"""
        try:
            # Cargar información básica
            client = self.db_manager.get_client(self.client_id)
            if client:
                self.id_label.setText(str(client['id']))
                self.name_label.setText(client['name'])
                self.address_label.setText(client['address'])
                self.status_label.setText(client['status'].title())
                self.created_label.setText(client['created_at'][:19] if client['created_at'] else 'N/A')
                
                # Actualizar título de la ventana
                self.setWindowTitle(f"Perfil del Cliente - {client['name']}")
            
            # Cargar pagos
            self.load_payments()
            
            # Cargar consumo
            self.load_consumption()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar datos: {str(e)}")
    
    def load_payments(self):
        """Carga el historial de pagos"""
        try:
            payments = self.db_manager.get_client_payments(self.client_id)
            
            self.payments_table.setRowCount(len(payments))
            
            for row, payment in enumerate(payments):
                # ID
                id_item = QTableWidgetItem(str(payment['id']))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.payments_table.setItem(row, 0, id_item)
                
                # Monto
                amount_item = QTableWidgetItem(f"${payment['amount']:.2f}")
                amount_item.setTextAlignment(Qt.AlignRight)
                self.payments_table.setItem(row, 1, amount_item)
                
                # Fecha
                date_str = payment['payment_date'][:19] if payment['payment_date'] else 'N/A'
                date_item = QTableWidgetItem(date_str)
                date_item.setTextAlignment(Qt.AlignCenter)
                self.payments_table.setItem(row, 2, date_item)
                
                # Estado
                status_icon = "✅" if payment['status'] == 'pagado' else "❌"
                status_item = QTableWidgetItem(f"{status_icon} {payment['status'].title()}")
                status_item.setTextAlignment(Qt.AlignCenter)
                self.payments_table.setItem(row, 3, status_item)
                
                # Notas
                notes_item = QTableWidgetItem(payment['notes'] or '')
                self.payments_table.setItem(row, 4, notes_item)
        
        except Exception as e:
            QMessageBox.warning(self, "Advertencia", f"Error al cargar pagos: {str(e)}")
    
    def load_consumption(self):
        """Carga el historial de consumo"""
        try:
            consumption = self.db_manager.get_client_consumption(self.client_id)
            
            self.consumption_table.setRowCount(len(consumption))
            
            for row, record in enumerate(consumption):
                # ID
                id_item = QTableWidgetItem(str(record['id']))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.consumption_table.setItem(row, 0, id_item)
                
                # Tipo
                type_icon = "💧" if record['consumption_type'] == 'exceso' else "✅"
                type_item = QTableWidgetItem(f"{type_icon} {record['consumption_type'].title()}")
                type_item.setTextAlignment(Qt.AlignCenter)
                self.consumption_table.setItem(row, 1, type_item)
                
                # Fecha
                date_str = record['consumption_date'][:19] if record['consumption_date'] else 'N/A'
                date_item = QTableWidgetItem(date_str)
                date_item.setTextAlignment(Qt.AlignCenter)
                self.consumption_table.setItem(row, 2, date_item)
                
                # Notas
                notes_item = QTableWidgetItem(record['notes'] or '')
                self.consumption_table.setItem(row, 3, notes_item)
        
        except Exception as e:
            QMessageBox.warning(self, "Advertencia", f"Error al cargar consumo: {str(e)}")
    
    def edit_client(self):
        """Abre el diálogo de edición del cliente"""
        dialog = ClientDialog(self.client_id, self)
        dialog.client_saved.connect(self.load_client_data)
        dialog.exec_()
    
    def add_payment(self):
        """Abre el diálogo para agregar un pago"""
        dialog = PaymentDialog(self.client_id, self)
        dialog.payment_saved.connect(self.load_payments)
        dialog.exec_()
    
    def add_consumption(self):
        """Abre el diálogo para registrar consumo"""
        dialog = ConsumptionDialog(self.client_id, self)
        dialog.consumption_saved.connect(self.load_consumption)
        dialog.exec_()

class PaymentDialog(QDialog):
    """Diálogo para registrar pagos"""
    payment_saved = pyqtSignal()
    
    def __init__(self, client_id, parent=None):
        super().__init__(parent)
        self.client_id = client_id
        self.db_manager = DatabaseManager()
        self.init_ui()
        self.setStyleSheet(MAIN_STYLE)
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Registrar Pago")
        self.setFixedSize(400, 250)
        
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("Registrar Nuevo Pago")
        title_label.setObjectName("title")
        
        # Formulario
        form_layout = QFormLayout()
        
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 999999.99)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("$")
        form_layout.addRow("Monto:", self.amount_input)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["pagado", "pendiente"])
        form_layout.addRow("Estado:", self.status_combo)
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("Notas adicionales (opcional)")
        form_layout.addRow("Notas:", self.notes_input)
        
        # Botones
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Guardar")
        save_button.setDefault(True)
        save_button.clicked.connect(self.save_payment)
        
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addWidget(title_label)
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.amount_input.setFocus()
    
    def save_payment(self):
        """Guarda el pago en la base de datos"""
        amount = self.amount_input.value()
        status = self.status_combo.currentText()
        notes = self.notes_input.toPlainText().strip()
        
        if amount <= 0:
            QMessageBox.warning(self, "Error", "El monto debe ser mayor a cero")
            return
        
        try:
            payment_id = self.db_manager.add_payment(self.client_id, amount, status, notes)
            if payment_id:
                QMessageBox.information(self, "Éxito", "Pago registrado correctamente")
                self.payment_saved.emit()
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "No se pudo registrar el pago")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar: {str(e)}")

class ConsumptionDialog(QDialog):
    """Diálogo para registrar consumo de agua"""
    consumption_saved = pyqtSignal()
    
    def __init__(self, client_id, parent=None):
        super().__init__(parent)
        self.client_id = client_id
        self.db_manager = DatabaseManager()
        self.init_ui()
        self.setStyleSheet(MAIN_STYLE)
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Registrar Consumo")
        self.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("Registrar Consumo de Agua")
        title_label.setObjectName("title")
        
        # Formulario
        form_layout = QFormLayout()
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["normal", "exceso"])
        form_layout.addRow("Tipo de Consumo:", self.type_combo)
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("Descripción del consumo (opcional)")
        form_layout.addRow("Notas:", self.notes_input)
        
        # Botones
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Guardar")
        save_button.setDefault(True)
        save_button.clicked.connect(self.save_consumption)
        
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addWidget(title_label)
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def save_consumption(self):
        """Guarda el registro de consumo"""
        consumption_type = self.type_combo.currentText()
        notes = self.notes_input.toPlainText().strip()
        
        try:
            consumption_id = self.db_manager.add_water_consumption(
                self.client_id, consumption_type, notes
            )
            if consumption_id:
                QMessageBox.information(self, "Éxito", "Consumo registrado correctamente")
                self.consumption_saved.emit()
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "No se pudo registrar el consumo")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar: {str(e)}")
