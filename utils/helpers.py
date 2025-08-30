"""
Sistema de Gestión de Pago de Agua
Módulo: Utilidades Generales
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QWidget, QVBoxLayout

class ChartWidget(QWidget):
    """Widget personalizado para mostrar gráficas con Matplotlib"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def clear(self):
        """Limpia la figura"""
        self.figure.clear()
        self.canvas.draw()
    
    def plot_payments_by_month(self, data: List[Dict[str, Any]]):
        """Crea un gráfico de pagos por mes"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not data:
            ax.text(0.5, 0.5, 'No hay datos para mostrar', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14)
            self.canvas.draw()
            return
        
        months = [item['month'] for item in data]
        amounts = [item['total_amount'] for item in data]
        
        bars = ax.bar(months, amounts, color='#2196F3', alpha=0.7)
        
        # Personalizar gráfico
        ax.set_title('Pagos por Mes', fontsize=16, fontweight='bold')
        ax.set_xlabel('Mes', fontsize=12)
        ax.set_ylabel('Monto Total ($)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Rotar etiquetas del eje X
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Agregar valores en las barras
        for bar, amount in zip(bars, amounts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(amounts) * 0.01,
                   f'${amount:.0f}', ha='center', va='bottom', fontsize=10)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_payment_status_pie(self, paid_count: int, pending_count: int):
        """Crea un gráfico de pastel del estado de pagos"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if paid_count == 0 and pending_count == 0:
            ax.text(0.5, 0.5, 'No hay datos para mostrar', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14)
            self.canvas.draw()
            return
        
        labels = ['Pagados', 'Pendientes']
        sizes = [paid_count, pending_count]
        colors = ['#4CAF50', '#F44336']
        explode = (0.05, 0.05)  # Separar un poco las secciones
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, 
                                         explode=explode, autopct='%1.1f%%',
                                         shadow=True, startangle=90)
        
        # Personalizar texto
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Estado de Pagos', fontsize=16, fontweight='bold')
        
        self.canvas.draw()
    
    def plot_consumption_trend(self, data: List[Dict[str, Any]]):
        """Crea un gráfico de tendencia de consumo"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not data:
            ax.text(0.5, 0.5, 'No hay datos para mostrar', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14)
            self.canvas.draw()
            return
        
        dates = [datetime.strptime(item['date'], '%Y-%m-%d') for item in data]
        normal_counts = [item['normal'] for item in data]
        excess_counts = [item['excess'] for item in data]
        
        # Líneas de tendencia
        ax.plot(dates, normal_counts, marker='o', label='Consumo Normal', 
               color='#4CAF50', linewidth=2, markersize=6)
        ax.plot(dates, excess_counts, marker='s', label='Exceso de Consumo', 
               color='#FF9800', linewidth=2, markersize=6)
        
        # Personalizar gráfico
        ax.set_title('Tendencia de Consumo de Agua', fontsize=16, fontweight='bold')
        ax.set_xlabel('Fecha', fontsize=12)
        ax.set_ylabel('Número de Registros', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Formatear fechas en el eje X
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        self.figure.tight_layout()
        self.canvas.draw()

class DataExporter:
    """Clase para exportar datos a diferentes formatos"""
    
    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], filename: str) -> bool:
        """Exporta datos a archivo CSV"""
        try:
            import csv
            
            if not data:
                return False
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for row in data:
                    writer.writerow(row)
            
            return True
            
        except Exception as e:
            print(f"Error al exportar CSV: {e}")
            return False
    
    @staticmethod
    def export_client_report(db_manager, client_id: int, filename: str) -> bool:
        """Exporta reporte completo de un cliente"""
        try:
            # Obtener datos del cliente
            client = db_manager.get_client(client_id)
            payments = db_manager.get_client_payments(client_id)
            consumption = db_manager.get_client_consumption(client_id)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("REPORTE DE CLIENTE\\n")
                f.write("=" * 50 + "\\n\\n")
                
                # Información del cliente
                f.write("INFORMACIÓN DEL CLIENTE\\n")
                f.write("-" * 25 + "\\n")
                f.write(f"ID: {client['id']}\\n")
                f.write(f"Nombre: {client['name']}\\n")
                f.write(f"Dirección: {client['address']}\\n")
                f.write(f"Estado: {client['status']}\\n")
                f.write(f"Fecha de registro: {client['created_at']}\\n\\n")
                
                # Historial de pagos
                f.write("HISTORIAL DE PAGOS\\n")
                f.write("-" * 20 + "\\n")
                if payments:
                    total_pagado = sum(p['amount'] for p in payments if p['status'] == 'pagado')
                    f.write(f"Total pagado: ${total_pagado:.2f}\\n")
                    f.write(f"Número de pagos: {len(payments)}\\n\\n")
                    
                    for payment in payments:
                        estado = "✅" if payment['status'] == 'pagado' else "❌"
                        f.write(f"{estado} ${payment['amount']:.2f} - {payment['payment_date'][:10]}\\n")
                        if payment['notes']:
                            f.write(f"   Notas: {payment['notes']}\\n")
                else:
                    f.write("No hay pagos registrados\\n")
                
                f.write("\\n")
                
                # Historial de consumo
                f.write("HISTORIAL DE CONSUMO\\n")
                f.write("-" * 22 + "\\n")
                if consumption:
                    excesos = len([c for c in consumption if c['consumption_type'] == 'exceso'])
                    f.write(f"Registros de exceso: {excesos}\\n")
                    f.write(f"Total registros: {len(consumption)}\\n\\n")
                    
                    for record in consumption:
                        icono = "💧" if record['consumption_type'] == 'exceso' else "✅"
                        f.write(f"{icono} {record['consumption_type']} - {record['consumption_date'][:10]}\\n")
                        if record['notes']:
                            f.write(f"   Notas: {record['notes']}\\n")
                else:
                    f.write("No hay registros de consumo\\n")
                
                f.write("\\n" + "=" * 50 + "\\n")
                f.write(f"Reporte generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
            
            return True
            
        except Exception as e:
            print(f"Error al generar reporte: {e}")
            return False

class DateUtils:
    """Utilidades para manejo de fechas"""
    
    @staticmethod
    def get_month_range(year: int, month: int) -> tuple:
        """Obtiene el rango de fechas de un mes específico"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        return start_date, end_date
    
    @staticmethod
    def format_date_spanish(date_obj: datetime) -> str:
        """Formatea una fecha en español"""
        months = [
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
        ]
        
        day = date_obj.day
        month = months[date_obj.month - 1]
        year = date_obj.year
        
        return f"{day} de {month} de {year}"
    
    @staticmethod
    def get_last_n_months(n: int) -> List[str]:
        """Obtiene los últimos N meses en formato YYYY-MM"""
        months = []
        current_date = datetime.now()
        
        for i in range(n):
            if current_date.month - i <= 0:
                month = 12 + (current_date.month - i)
                year = current_date.year - 1
            else:
                month = current_date.month - i
                year = current_date.year
            
            months.append(f"{year:04d}-{month:02d}")
        
        return list(reversed(months))

class ValidationUtils:
    """Utilidades para validación de datos"""
    
    @staticmethod
    def validate_pin(pin: str) -> tuple:
        """Valida un PIN"""
        if not pin:
            return False, "El PIN no puede estar vacío"
        
        if not pin.isdigit():
            return False, "El PIN debe contener solo números"
        
        if len(pin) < 4:
            return False, "El PIN debe tener al menos 4 dígitos"
        
        if len(pin) > 8:
            return False, "El PIN no puede tener más de 8 dígitos"
        
        return True, "PIN válido"
    
    @staticmethod
    def validate_client_name(name: str) -> tuple:
        """Valida el nombre de un cliente"""
        if not name or not name.strip():
            return False, "El nombre es obligatorio"
        
        if len(name.strip()) < 2:
            return False, "El nombre debe tener al menos 2 caracteres"
        
        if len(name.strip()) > 100:
            return False, "El nombre no puede exceder 100 caracteres"
        
        return True, "Nombre válido"
    
    @staticmethod
    def validate_address(address: str) -> tuple:
        """Valida la dirección de un cliente"""
        if not address or not address.strip():
            return False, "La dirección es obligatoria"
        
        if len(address.strip()) < 5:
            return False, "La dirección debe tener al menos 5 caracteres"
        
        if len(address.strip()) > 200:
            return False, "La dirección no puede exceder 200 caracteres"
        
        return True, "Dirección válida"
    
    @staticmethod
    def validate_amount(amount: float) -> tuple:
        """Valida un monto de pago"""
        if amount <= 0:
            return False, "El monto debe ser mayor a cero"
        
        if amount > 999999.99:
            return False, "El monto no puede exceder $999,999.99"
        
        return True, "Monto válido"

def ensure_directory_exists(directory_path: str):
    """Asegura que un directorio exista, creándolo si es necesario"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def get_application_directory():
    """Obtiene el directorio de la aplicación"""
    if getattr(sys, 'frozen', False):
        # Si la aplicación está empaquetada
        return os.path.dirname(sys.executable)
    else:
        # Si se ejecuta desde el código fuente
        return os.path.dirname(os.path.abspath(__file__))

def setup_application_directories():
    """Configura los directorios necesarios para la aplicación"""
    app_dir = get_application_directory()
    
    directories = [
        os.path.join(app_dir, 'database'),
        os.path.join(app_dir, 'exports'),
        os.path.join(app_dir, 'logs'),
        os.path.join(app_dir, 'backups')
    ]
    
    for directory in directories:
        ensure_directory_exists(directory)
