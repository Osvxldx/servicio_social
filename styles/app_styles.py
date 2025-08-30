"""
Sistema de Gestión de Pago de Agua
Módulo: Estilos CSS para PyQt
"""

# Colores principales del sistema
COLORS = {
    'primary': '#2196F3',      # Azul principal (agua)
    'primary_dark': '#1976D2',
    'secondary': '#4CAF50',    # Verde (pagado)
    'warning': '#FF9800',      # Naranja (pendiente)
    'danger': '#F44336',       # Rojo (deuda)
    'info': '#00BCD4',         # Cian (información)
    'light': '#F5F5F5',        # Gris claro
    'dark': '#212121',         # Gris oscuro
    'white': '#FFFFFF',
    'text': '#333333'
}

# Estilo principal de la aplicación
MAIN_STYLE = f"""
/* Estilo general de la aplicación */
QMainWindow {{
    background-color: {COLORS['light']};
    color: {COLORS['text']};
    font-family: 'Segoe UI', Arial, sans-serif;
}}

/* Ventanas y diálogos */
QDialog {{
    background-color: {COLORS['white']};
    border: 1px solid {COLORS['primary']};
}}

/* Botones principales */
QPushButton {{
    background-color: {COLORS['primary']};
    color: {COLORS['white']};
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    font-size: 14px;
    font-weight: bold;
    min-width: 100px;
}}

QPushButton:hover {{
    background-color: {COLORS['primary_dark']};
}}

QPushButton:pressed {{
    background-color: {COLORS['primary_dark']};
    padding-top: 11px;
    padding-left: 21px;
}}

QPushButton:disabled {{
    background-color: #CCCCCC;
    color: #666666;
}}

/* Botones secundarios */
QPushButton.secondary {{
    background-color: {COLORS['secondary']};
}}

QPushButton.secondary:hover {{
    background-color: #45A049;
}}

/* Botones de advertencia */
QPushButton.warning {{
    background-color: {COLORS['warning']};
}}

QPushButton.warning:hover {{
    background-color: #E68900;
}}

/* Botones de peligro */
QPushButton.danger {{
    background-color: {COLORS['danger']};
}}

QPushButton.danger:hover {{
    background-color: #D32F2F;
}}

/* Campos de entrada */
QLineEdit {{
    border: 2px solid #E0E0E0;
    border-radius: 5px;
    padding: 8px 12px;
    font-size: 14px;
    background-color: {COLORS['white']};
}}

QLineEdit:focus {{
    border-color: {COLORS['primary']};
}}

QLineEdit:disabled {{
    background-color: #F5F5F5;
    color: #999999;
}}

/* Áreas de texto */
QTextEdit {{
    border: 2px solid #E0E0E0;
    border-radius: 5px;
    padding: 8px 12px;
    font-size: 14px;
    background-color: {COLORS['white']};
}}

QTextEdit:focus {{
    border-color: {COLORS['primary']};
}}

/* ComboBox */
QComboBox {{
    border: 2px solid #E0E0E0;
    border-radius: 5px;
    padding: 8px 12px;
    font-size: 14px;
    background-color: {COLORS['white']};
    min-width: 120px;
}}

QComboBox:focus {{
    border-color: {COLORS['primary']};
}}

QComboBox::drop-down {{
    border: none;
    background-color: {COLORS['primary']};
    border-top-right-radius: 3px;
    border-bottom-right-radius: 3px;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid {COLORS['white']};
    margin-right: 5px;
}}

/* Tablas */
QTableWidget {{
    border: 1px solid #E0E0E0;
    background-color: {COLORS['white']};
    alternate-background-color: #F9F9F9;
    selection-background-color: {COLORS['primary']};
    gridline-color: #E0E0E0;
}}

QTableWidget::item {{
    padding: 8px;
    border-bottom: 1px solid #E0E0E0;
}}

QTableWidget::item:selected {{
    background-color: {COLORS['primary']};
    color: {COLORS['white']};
}}

QHeaderView::section {{
    background-color: {COLORS['primary']};
    color: {COLORS['white']};
    padding: 10px;
    border: none;
    font-weight: bold;
}}

/* Etiquetas */
QLabel {{
    color: {COLORS['text']};
    font-size: 14px;
}}

QLabel.title {{
    font-size: 18px;
    font-weight: bold;
    color: {COLORS['primary']};
    margin-bottom: 10px;
}}

QLabel.subtitle {{
    font-size: 16px;
    font-weight: bold;
    color: {COLORS['text']};
    margin-bottom: 5px;
}}

QLabel.status-paid {{
    color: {COLORS['secondary']};
    font-weight: bold;
}}

QLabel.status-pending {{
    color: {COLORS['warning']};
    font-weight: bold;
}}

QLabel.status-debt {{
    color: {COLORS['danger']};
    font-weight: bold;
}}

/* Menú lateral */
QListWidget {{
    background-color: {COLORS['primary']};
    color: {COLORS['white']};
    border: none;
    font-size: 16px;
    outline: none;
}}

QListWidget::item {{
    padding: 15px 20px;
    border-bottom: 1px solid {COLORS['primary_dark']};
}}

QListWidget::item:selected {{
    background-color: {COLORS['primary_dark']};
}}

QListWidget::item:hover {{
    background-color: {COLORS['primary_dark']};
}}

/* Calendario */
QCalendarWidget {{
    background-color: {COLORS['white']};
    border: 1px solid #E0E0E0;
}}

QCalendarWidget QToolButton {{
    background-color: {COLORS['primary']};
    color: {COLORS['white']};
    font-size: 14px;
    font-weight: bold;
}}

QCalendarWidget QMenu {{
    background-color: {COLORS['white']};
    border: 1px solid #E0E0E0;
}}

QCalendarWidget QSpinBox {{
    background-color: {COLORS['white']};
    border: 1px solid #E0E0E0;
}}

/* Barras de desplazamiento */
QScrollBar:vertical {{
    background-color: #F0F0F0;
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['primary']};
    border-radius: 6px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['primary_dark']};
}}

/* Tooltips */
QToolTip {{
    background-color: {COLORS['dark']};
    color: {COLORS['white']};
    border: none;
    padding: 5px;
    border-radius: 3px;
    font-size: 12px;
}}

/* StatusBar */
QStatusBar {{
    background-color: {COLORS['primary']};
    color: {COLORS['white']};
    font-size: 12px;
}}

/* GroupBox */
QGroupBox {{
    font-weight: bold;
    border: 2px solid #E0E0E0;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
    color: {COLORS['primary']};
}}

/* Checkbox y RadioButton */
QCheckBox, QRadioButton {{
    font-size: 14px;
    color: {COLORS['text']};
}}

QCheckBox::indicator, QRadioButton::indicator {{
    width: 18px;
    height: 18px;
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['primary']};
    border: 2px solid {COLORS['primary']};
}}

QRadioButton::indicator:checked {{
    background-color: {COLORS['primary']};
    border: 2px solid {COLORS['primary']};
}}

/* ProgressBar */
QProgressBar {{
    border: 1px solid #E0E0E0;
    border-radius: 5px;
    text-align: center;
    font-weight: bold;
}}

QProgressBar::chunk {{
    background-color: {COLORS['primary']};
    border-radius: 3px;
}}
"""

# Estilo específico para el login
LOGIN_STYLE = f"""
QDialog {{
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                stop:0 {COLORS['primary']}, stop:1 {COLORS['primary_dark']});
}}

QLabel {{
    color: {COLORS['white']};
    font-size: 16px;
    font-weight: bold;
}}

QLabel.title {{
    font-size: 24px;
    color: {COLORS['white']};
    margin-bottom: 20px;
}}

QLineEdit {{
    background-color: {COLORS['white']};
    border: none;
    border-radius: 8px;
    padding: 12px 15px;
    font-size: 16px;
    text-align: center;
}}

QPushButton {{
    background-color: {COLORS['white']};
    color: {COLORS['primary']};
    border: none;
    border-radius: 8px;
    padding: 12px 30px;
    font-size: 16px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: #F0F0F0;
}}
"""

# Estilo para el dashboard
DASHBOARD_STYLE = f"""
QFrame.stats-card {{
    background-color: {COLORS['white']};
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    margin: 5px;
}}

QLabel.stat-number {{
    font-size: 32px;
    font-weight: bold;
    color: {COLORS['primary']};
}}

QLabel.stat-label {{
    font-size: 14px;
    color: #666666;
}}
"""
