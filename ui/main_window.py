"""
Sistema de Gestión de Pago de Agua
Módulo: Ventana Principal (Dashboard)
"""

import sys
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                            QLineEdit, QComboBox, QFrame, QSplitter, QListWidget,
                            QStackedWidget, QCalendarWidget, QTextEdit, QGroupBox,
                            QMessageBox, QHeaderView, QApplication)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from database.database_manager import DatabaseManager
from models.data_models import ClientWithStatus
from styles.app_styles import MAIN_STYLE, DASHBOARD_STYLE, COLORS
from controllers.app_controller import AppController
from ui.client_dialogs import ClientDialog, ClientProfileDialog
from utils.helpers import ChartWidget

class StatsCard(QFrame):
    """Widget personalizado para mostrar estadísticas"""
    def __init__(self, title, value, color=None):
        super().__init__()
        self.setObjectName("stats-card")
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Número grande
        value_label = QLabel(str(value))
        value_label.setObjectName("stat-number")
        value_label.setAlignment(Qt.AlignCenter)
        if color:
            value_label.setStyleSheet(f"QLabel {{ color: {color}; font-size: 32px; font-weight: bold; }}")
        
        # Título
        title_label = QLabel(title)
        title_label.setObjectName("stat-label")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("QLabel { font-size: 14px; color: #666666; }")
        
        layout.addWidget(value_label)
        layout.addWidget(title_label)
        self.setLayout(layout)
    
    def connect_signals(self):
        """Conecta las señales del controlador"""
        self.controller.data_updated.connect(self.load_data)
        self.controller.client_added.connect(self.on_client_added)
        self.controller.client_updated.connect(self.on_client_updated)
        self.controller.client_deleted.connect(self.on_client_deleted)
    
    def on_client_added(self, client_id):
        """Maneja la adición de un nuevo cliente"""
        self.statusBar().showMessage(f"Cliente agregado con ID: {client_id}", 3000)
    
    def on_client_updated(self, client_id):
        """Maneja la actualización de un cliente"""
        self.statusBar().showMessage(f"Cliente {client_id} actualizado", 3000)
    
    def on_client_deleted(self, client_id):
        """Maneja la eliminación de un cliente"""
        self.statusBar().showMessage(f"Cliente {client_id} eliminado", 3000)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = AppController()
        self.current_clients = []
        self.init_ui()
        self.setStyleSheet(MAIN_STYLE + DASHBOARD_STYLE)
        self.connect_signals()
        self.load_data()
        
        # Timer para actualizar estadísticas cada 30 segundos
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_statistics)
        self.stats_timer.start(30000)  # 30 segundos
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Sistema de Gestión de Pago de Agua - Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal horizontal
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Crear menú lateral y área principal
        self.create_sidebar()
        self.create_main_area()
        
        # Splitter para dividir sidebar y área principal
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.main_area)
        splitter.setSizes([250, 950])
        
        main_layout.addWidget(splitter)
        
        # Barra de estado
        self.statusBar().showMessage("Sistema iniciado correctamente")
    
    def create_sidebar(self):
        """Crea el menú lateral"""
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(250)
        
        layout = QVBoxLayout()
        
        # Logo/Título
        title_label = QLabel("💧 Gestión de Agua")
        title_label.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['primary']};
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 20px;
                text-align: center;
            }}
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        # Menú de navegación
        self.menu_list = QListWidget()
        menu_items = [
            "📊 Dashboard",
            "👥 Clientes", 
            "📅 Calendario",
            "💰 Pagos",
            "🔧 Configuración"
        ]
        
        for item in menu_items:
            self.menu_list.addItem(item)
        
        self.menu_list.currentRowChanged.connect(self.change_page)
        self.menu_list.setCurrentRow(0)  # Seleccionar Dashboard por defecto
        
        layout.addWidget(title_label)
        layout.addWidget(self.menu_list)
        layout.addStretch()
        
        self.sidebar.setLayout(layout)
    
    def create_main_area(self):
        """Crea el área principal con las diferentes páginas"""
        self.main_area = QWidget()
        layout = QVBoxLayout()
        
        # Stack de páginas
        self.stacked_widget = QStackedWidget()
        
        # Crear páginas
        self.create_dashboard_page()
        self.create_clients_page()
        self.create_calendar_page()
        self.create_payments_page()
        self.create_settings_page()
        
        layout.addWidget(self.stacked_widget)
        self.main_area.setLayout(layout)
    
    def create_dashboard_page(self):
        """Crea la página del dashboard"""
        dashboard_page = QWidget()
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("Panel de Control")
        title_label.setObjectName("title")
        title_label.setStyleSheet("QLabel { font-size: 24px; font-weight: bold; color: #2196F3; margin-bottom: 20px; }")
        
        # Estadísticas
        stats_layout = QHBoxLayout()
        
        self.total_clients_card = StatsCard("Total Clientes", "0", COLORS['primary'])
        self.debt_clients_card = StatsCard("Con Deuda", "0", COLORS['danger'])
        self.payments_month_card = StatsCard("Pagos del Mes", "0", COLORS['secondary'])
        self.excess_consumption_card = StatsCard("Exceso Consumo", "0", COLORS['warning'])
        
        stats_layout.addWidget(self.total_clients_card)
        stats_layout.addWidget(self.debt_clients_card)
        stats_layout.addWidget(self.payments_month_card)
        stats_layout.addWidget(self.excess_consumption_card)
        
        # Filtros y búsqueda
        filters_layout = QHBoxLayout()
        
        search_label = QLabel("Buscar:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nombre, dirección o ID...")
        self.search_input.textChanged.connect(self.filter_clients)
        
        filter_label = QLabel("Filtrar:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "Todos",
            "Solo con deuda",
            "Solo al corriente",
            "Exceso de consumo"
        ])
        self.filter_combo.currentTextChanged.connect(self.filter_clients)
        
        refresh_button = QPushButton("🔄 Actualizar")
        refresh_button.clicked.connect(self.load_data)
        
        filters_layout.addWidget(search_label)
        filters_layout.addWidget(self.search_input)
        filters_layout.addWidget(filter_label)
        filters_layout.addWidget(self.filter_combo)
        filters_layout.addStretch()
        filters_layout.addWidget(refresh_button)
        
        # Tabla de clientes
        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(5)
        self.clients_table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Dirección", "Estado", "Estado de Pago"
        ])
        
        # Configurar tabla
        header = self.clients_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        self.clients_table.setAlternatingRowColors(True)
        self.clients_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.clients_table.doubleClicked.connect(self.open_client_profile)
        
        # Agregar elementos al layout
        layout.addWidget(title_label)
        layout.addLayout(stats_layout)
        layout.addLayout(filters_layout)
        layout.addWidget(self.clients_table)
        
        dashboard_page.setLayout(layout)
        self.stacked_widget.addWidget(dashboard_page)
    
    def create_clients_page(self):
        """Crea la página de gestión de clientes"""
        clients_page = QWidget()
        layout = QVBoxLayout()
        
        title_label = QLabel("Gestión de Clientes")
        title_label.setObjectName("title")
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        add_client_button = QPushButton("➕ Agregar Cliente")
        add_client_button.setObjectName("secondary")
        add_client_button.clicked.connect(self.add_new_client)
        
        edit_client_button = QPushButton("✏️ Editar Cliente")
        edit_client_button.clicked.connect(self.edit_selected_client)
        
        delete_client_button = QPushButton("🗑️ Eliminar Cliente")
        delete_client_button.setObjectName("danger")
        delete_client_button.clicked.connect(self.delete_selected_client)
        
        buttons_layout.addWidget(add_client_button)
        buttons_layout.addWidget(edit_client_button)
        buttons_layout.addWidget(delete_client_button)
        buttons_layout.addStretch()
        
        # Tabla de clientes (reutilizamos la misma configuración)
        # Aquí iría una tabla similar al dashboard pero con más opciones
        
        layout.addWidget(title_label)
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        clients_page.setLayout(layout)
        self.stacked_widget.addWidget(clients_page)
    
    def create_calendar_page(self):
        """Crea la página del calendario"""
        calendar_page = QWidget()
        layout = QVBoxLayout()
        
        title_label = QLabel("Calendario de Pagos")
        title_label.setObjectName("title")
        
        # Layout horizontal para calendario y detalles
        calendar_layout = QHBoxLayout()
        
        # Calendario
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.show_payments_by_date)
        
        # Panel de detalles del día seleccionado
        details_group = QGroupBox("Pagos del día seleccionado")
        details_layout = QVBoxLayout()
        
        self.date_payments_text = QTextEdit()
        self.date_payments_text.setReadOnly(True)
        self.date_payments_text.setMaximumHeight(300)
        
        details_layout.addWidget(self.date_payments_text)
        details_group.setLayout(details_layout)
        
        calendar_layout.addWidget(self.calendar, 2)
        calendar_layout.addWidget(details_group, 1)
        
        layout.addWidget(title_label)
        layout.addLayout(calendar_layout)
        
        calendar_page.setLayout(layout)
        self.stacked_widget.addWidget(calendar_page)
    
    def create_payments_page(self):
        """Crea la página de gestión de pagos"""
        payments_page = QWidget()
        layout = QVBoxLayout()
        
        title_label = QLabel("Gestión de Pagos")
        title_label.setObjectName("title")
        
        # Aquí iría la funcionalidad de pagos
        info_label = QLabel("Funcionalidad de pagos en desarrollo...")
        info_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(info_label)
        layout.addStretch()
        
        payments_page.setLayout(layout)
        self.stacked_widget.addWidget(payments_page)
    
    def create_settings_page(self):
        """Crea la página de configuración"""
        settings_page = QWidget()
        layout = QVBoxLayout()
        
        title_label = QLabel("Configuración del Sistema")
        title_label.setObjectName("title")
        
        # Cambio de PIN
        pin_group = QGroupBox("Cambiar PIN de Acceso")
        pin_layout = QVBoxLayout()
        
        current_pin_label = QLabel("PIN Actual:")
        self.current_pin_input = QLineEdit()
        self.current_pin_input.setEchoMode(QLineEdit.Password)
        
        new_pin_label = QLabel("Nuevo PIN:")
        self.new_pin_input = QLineEdit()
        self.new_pin_input.setEchoMode(QLineEdit.Password)
        
        confirm_pin_label = QLabel("Confirmar PIN:")
        self.confirm_pin_input = QLineEdit()
        self.confirm_pin_input.setEchoMode(QLineEdit.Password)
        
        change_pin_button = QPushButton("Cambiar PIN")
        change_pin_button.clicked.connect(self.change_pin)
        
        pin_layout.addWidget(current_pin_label)
        pin_layout.addWidget(self.current_pin_input)
        pin_layout.addWidget(new_pin_label)
        pin_layout.addWidget(self.new_pin_input)
        pin_layout.addWidget(confirm_pin_label)
        pin_layout.addWidget(self.confirm_pin_input)
        pin_layout.addWidget(change_pin_button)
        
        pin_group.setLayout(pin_layout)
        
        layout.addWidget(title_label)
        layout.addWidget(pin_group)
        layout.addStretch()
        
        settings_page.setLayout(layout)
        self.stacked_widget.addWidget(settings_page)
    
    def change_page(self, index):
        """Cambia la página mostrada"""
        self.stacked_widget.setCurrentIndex(index)
        
        # Actualizar título en la barra de estado
        pages = ["Dashboard", "Clientes", "Calendario", "Pagos", "Configuración"]
        if 0 <= index < len(pages):
            self.statusBar().showMessage(f"Navegando en: {pages[index]}")
    
    def load_data(self):
        """Carga los datos desde la base de datos"""
        try:
            # Cargar clientes con estado
            self.current_clients = self.controller.get_clients_with_status()
            
            # Actualizar tabla
            self.update_clients_table()
            
            # Actualizar estadísticas
            self.update_statistics()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar datos: {str(e)}")
    
    def update_clients_table(self, clients=None):
        """Actualiza la tabla de clientes"""
        if clients is None:
            clients = self.current_clients
        
        self.clients_table.setRowCount(len(clients))
        
        for row, client in enumerate(clients):
            # ID
            id_item = QTableWidgetItem(str(client.id))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.clients_table.setItem(row, 0, id_item)
            
            # Nombre
            name_item = QTableWidgetItem(client.name)
            self.clients_table.setItem(row, 1, name_item)
            
            # Dirección
            address_item = QTableWidgetItem(client.address)
            self.clients_table.setItem(row, 2, address_item)
            
            # Estado
            status_item = QTableWidgetItem(client.status.title())
            status_item.setTextAlignment(Qt.AlignCenter)
            self.clients_table.setItem(row, 3, status_item)
            
            # Estado de pago con ícono
            payment_status = f"{client.get_status_icon()} {client.get_status_text()}"
            payment_item = QTableWidgetItem(payment_status)
            payment_item.setTextAlignment(Qt.AlignCenter)
            self.clients_table.setItem(row, 4, payment_item)
    
    def update_statistics(self):
        """Actualiza las estadísticas del dashboard"""
        try:
            stats = self.controller.get_statistics()
            
            # Actualizar cards de estadísticas
            self.total_clients_card.findChild(QLabel, "stat-number").setText(str(stats['total_clients']))
            self.debt_clients_card.findChild(QLabel, "stat-number").setText(str(stats['clients_with_debt']))
            self.payments_month_card.findChild(QLabel, "stat-number").setText(str(stats['payments_this_month']))
            self.excess_consumption_card.findChild(QLabel, "stat-number").setText(str(stats['excess_consumption']))
            
        except Exception as e:
            print(f"Error al actualizar estadísticas: {e}")
    
    def filter_clients(self):
        """Filtra la tabla de clientes según búsqueda y filtros"""
        search_text = self.search_input.text()
        filter_option = self.filter_combo.currentText()
        
        # Aplicar filtros usando el controlador
        filtered_clients = self.controller.filter_clients_by_search(self.current_clients, search_text)
        filtered_clients = self.controller.filter_clients_by_status(filtered_clients, filter_option)
        
        self.update_clients_table(filtered_clients)
    
    def show_payments_by_date(self, date):
        """Muestra los pagos de una fecha específica"""
        try:
            date_str = date.toString("yyyy-MM-dd")
            payments = self.controller.get_payments_by_date(date_str)
            
            if payments:
                text = f"Pagos del {date.toString('dd/MM/yyyy')}:\\n\\n"
                for payment in payments:
                    status_icon = "✅" if payment['status'] == 'pagado' else "❌"
                    text += f"{status_icon} {payment['name']} - ${payment['amount']:.2f}\\n"
                    text += f"   📍 {payment['address']}\\n\\n"
            else:
                text = f"No hay pagos registrados para el {date.toString('dd/MM/yyyy')}"
            
            self.date_payments_text.setPlainText(text)
            
        except Exception as e:
            self.date_payments_text.setPlainText(f"Error al cargar pagos: {str(e)}")
    
    def open_client_profile(self):
        """Abre el perfil del cliente seleccionado"""
        current_row = self.clients_table.currentRow()
        if current_row >= 0:
            client_id = int(self.clients_table.item(current_row, 0).text())
            dialog = ClientProfileDialog(client_id, self)
            dialog.exec_()
    
    def add_new_client(self):
        """Abre el diálogo para agregar un nuevo cliente"""
        dialog = ClientDialog(parent=self)
        dialog.client_saved.connect(self.load_data)
        dialog.exec_()
    
    def edit_selected_client(self):
        """Edita el cliente seleccionado"""
        current_row = self.clients_table.currentRow()
        if current_row >= 0:
            client_id = int(self.clients_table.item(current_row, 0).text())
            dialog = ClientDialog(client_id, self)
            dialog.client_saved.connect(self.load_data)
            dialog.exec_()
        else:
            QMessageBox.information(self, "Selección", "Por favor seleccione un cliente para editar")
    
    def delete_selected_client(self):
        """Elimina el cliente seleccionado"""
        current_row = self.clients_table.currentRow()
        if current_row >= 0:
            client_id = int(self.clients_table.item(current_row, 0).text())
            client_name = self.clients_table.item(current_row, 1).text()
            
            reply = QMessageBox.question(
                self, "Confirmar Eliminación",
                f"¿Está seguro de que desea eliminar al cliente:\\n{client_name}?\\n\\n"
                "Esta acción no se puede deshacer.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success, message = self.controller.delete_client(client_id)
                if success:
                    QMessageBox.information(self, "Éxito", message)
                else:
                    QMessageBox.warning(self, "Error", message)
        else:
            QMessageBox.information(self, "Selección", "Por favor seleccione un cliente para eliminar")
    
    def change_pin(self):
        """Cambia el PIN del administrador"""
        current_pin = self.current_pin_input.text()
        new_pin = self.new_pin_input.text()
        confirm_pin = self.confirm_pin_input.text()
        
        if not all([current_pin, new_pin, confirm_pin]):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
        
        if new_pin != confirm_pin:
            QMessageBox.critical(self, "Error", "Los PINs nuevos no coinciden")
            return
        
        success, message = self.controller.update_pin(current_pin, new_pin)
        
        if success:
            QMessageBox.information(self, "Éxito", message)
            self.current_pin_input.clear()
            self.new_pin_input.clear()
            self.confirm_pin_input.clear()
        else:
            QMessageBox.critical(self, "Error", message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Configurar la aplicación
    app.setApplicationName("Sistema de Gestión de Agua")
    app.setApplicationVersion("1.0")
    
    # Mostrar ventana principal
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())
