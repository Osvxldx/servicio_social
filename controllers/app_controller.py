"""
Sistema de Gestión de Pago de Agua
Módulo: Controlador Principal
"""

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from database.database_manager import DatabaseManager
from models.data_models import Client, Payment, WaterConsumption, ClientWithStatus
from utils.helpers import ValidationUtils
from typing import List, Optional, Dict, Any

class AppController(QObject):
    """Controlador principal de la aplicación"""
    
    # Señales para comunicación con la UI
    data_updated = pyqtSignal()
    client_added = pyqtSignal(int)  # client_id
    client_updated = pyqtSignal(int)  # client_id
    client_deleted = pyqtSignal(int)  # client_id
    payment_added = pyqtSignal(int, int)  # payment_id, client_id
    consumption_added = pyqtSignal(int, int)  # consumption_id, client_id
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self._current_clients = []
        self._statistics = {}
    
    # Gestión de Clientes
    def add_client(self, name: str, address: str) -> Optional[int]:
        """Agrega un nuevo cliente con validación"""
        try:
            # Validar datos
            name_valid, name_msg = ValidationUtils.validate_client_name(name)
            if not name_valid:
                return None, name_msg
            
            address_valid, address_msg = ValidationUtils.validate_address(address)
            if not address_valid:
                return None, address_msg
            
            # Agregar cliente
            client_id = self.db_manager.add_client(name.strip(), address.strip())
            
            if client_id:
                self.client_added.emit(client_id)
                self.data_updated.emit()
                return client_id, "Cliente agregado exitosamente"
            else:
                return None, "Error al agregar el cliente"
                
        except Exception as e:
            return None, f"Error inesperado: {str(e)}"
    
    def update_client(self, client_id: int, name: str, address: str, status: str) -> tuple:
        """Actualiza un cliente existente"""
        try:
            # Validar datos
            name_valid, name_msg = ValidationUtils.validate_client_name(name)
            if not name_valid:
                return False, name_msg
            
            address_valid, address_msg = ValidationUtils.validate_address(address)
            if not address_valid:
                return False, address_msg
            
            if status not in ['activo', 'inactivo']:
                return False, "Estado inválido"
            
            # Actualizar cliente
            success = self.db_manager.update_client(client_id, name.strip(), address.strip(), status)
            
            if success:
                self.client_updated.emit(client_id)
                self.data_updated.emit()
                return True, "Cliente actualizado exitosamente"
            else:
                return False, "Error al actualizar el cliente"
                
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    def delete_client(self, client_id: int) -> tuple:
        """Elimina un cliente (solo si no tiene pagos)"""
        try:
            # Verificar si el cliente tiene pagos
            payments = self.db_manager.get_client_payments(client_id)
            if payments:
                return False, "No se puede eliminar: el cliente tiene pagos registrados"
            
            # Eliminar cliente
            success = self.db_manager.delete_client(client_id)
            
            if success:
                self.client_deleted.emit(client_id)
                self.data_updated.emit()
                return True, "Cliente eliminado exitosamente"
            else:
                return False, "Error al eliminar el cliente"
                
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    def get_client(self, client_id: int) -> Optional[Dict]:
        """Obtiene un cliente por ID"""
        try:
            return self.db_manager.get_client(client_id)
        except Exception as e:
            print(f"Error al obtener cliente: {e}")
            return None
    
    def search_clients(self, search_term: str) -> List[Dict]:
        """Busca clientes por nombre, dirección o ID"""
        try:
            if not search_term.strip():
                return self.get_all_clients()
            return self.db_manager.search_clients(search_term.strip())
        except Exception as e:
            print(f"Error al buscar clientes: {e}")
            return []
    
    def get_all_clients(self) -> List[Dict]:
        """Obtiene todos los clientes"""
        try:
            return self.db_manager.get_all_clients()
        except Exception as e:
            print(f"Error al obtener clientes: {e}")
            return []
    
    def get_clients_with_status(self) -> List[ClientWithStatus]:
        """Obtiene clientes con su estado de pago y consumo"""
        try:
            clients_data = self.db_manager.get_clients_with_payment_status()
            return [
                ClientWithStatus(
                    id=client['id'],
                    name=client['name'],
                    address=client['address'],
                    status=client['status'],
                    payment_status=client['payment_status'],
                    consumption_status=client['consumption_status']
                ) for client in clients_data
            ]
        except Exception as e:
            print(f"Error al obtener clientes con estado: {e}")
            return []
    
    # Gestión de Pagos
    def add_payment(self, client_id: int, amount: float, status: str = 'pagado', notes: str = '') -> tuple:
        """Agrega un nuevo pago"""
        try:
            # Validar monto
            amount_valid, amount_msg = ValidationUtils.validate_amount(amount)
            if not amount_valid:
                return None, amount_msg
            
            if status not in ['pagado', 'pendiente']:
                return None, "Estado de pago inválido"
            
            # Verificar que el cliente existe
            client = self.db_manager.get_client(client_id)
            if not client:
                return None, "Cliente no encontrado"
            
            # Agregar pago
            payment_id = self.db_manager.add_payment(client_id, amount, status, notes.strip())
            
            if payment_id:
                self.payment_added.emit(payment_id, client_id)
                self.data_updated.emit()
                return payment_id, "Pago registrado exitosamente"
            else:
                return None, "Error al registrar el pago"
                
        except Exception as e:
            return None, f"Error inesperado: {str(e)}"
    
    def get_client_payments(self, client_id: int) -> List[Dict]:
        """Obtiene todos los pagos de un cliente"""
        try:
            return self.db_manager.get_client_payments(client_id)
        except Exception as e:
            print(f"Error al obtener pagos del cliente: {e}")
            return []
    
    def get_payments_by_date(self, date: str) -> List[Dict]:
        """Obtiene pagos por fecha específica"""
        try:
            return self.db_manager.get_payments_by_date(date)
        except Exception as e:
            print(f"Error al obtener pagos por fecha: {e}")
            return []
    
    def update_payment_status(self, payment_id: int, status: str) -> tuple:
        """Actualiza el estado de un pago"""
        try:
            if status not in ['pagado', 'pendiente']:
                return False, "Estado inválido"
            
            success = self.db_manager.update_payment_status(payment_id, status)
            
            if success:
                self.data_updated.emit()
                return True, "Estado del pago actualizado"
            else:
                return False, "Error al actualizar el pago"
                
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    # Gestión de Consumo de Agua
    def add_water_consumption(self, client_id: int, consumption_type: str = 'normal', notes: str = '') -> tuple:
        """Registra consumo de agua"""
        try:
            if consumption_type not in ['normal', 'exceso']:
                return None, "Tipo de consumo inválido"
            
            # Verificar que el cliente existe
            client = self.db_manager.get_client(client_id)
            if not client:
                return None, "Cliente no encontrado"
            
            # Registrar consumo
            consumption_id = self.db_manager.add_water_consumption(client_id, consumption_type, notes.strip())
            
            if consumption_id:
                self.consumption_added.emit(consumption_id, client_id)
                self.data_updated.emit()
                return consumption_id, "Consumo registrado exitosamente"
            else:
                return None, "Error al registrar el consumo"
                
        except Exception as e:
            return None, f"Error inesperado: {str(e)}"
    
    def get_client_consumption(self, client_id: int) -> List[Dict]:
        """Obtiene el historial de consumo de un cliente"""
        try:
            return self.db_manager.get_client_consumption(client_id)
        except Exception as e:
            print(f"Error al obtener consumo del cliente: {e}")
            return []
    
    # Estadísticas y Reportes
    def get_statistics(self) -> Dict:
        """Obtiene estadísticas generales del sistema"""
        try:
            stats = self.db_manager.get_statistics()
            self._statistics = stats
            return stats
        except Exception as e:
            print(f"Error al obtener estadísticas: {e}")
            return {
                'total_clients': 0,
                'clients_with_debt': 0,
                'payments_this_month': 0,
                'excess_consumption': 0
            }
    
    def get_monthly_payment_data(self, months: int = 12) -> List[Dict]:
        """Obtiene datos de pagos por mes para gráficos"""
        try:
            # Esta funcionalidad se puede expandir agregando métodos específicos al DatabaseManager
            # Por ahora retornamos datos de ejemplo
            from datetime import datetime, timedelta
            from utils.helpers import DateUtils
            
            monthly_data = []
            month_list = DateUtils.get_last_n_months(months)
            
            for month in month_list:
                # Aquí se implementaría la consulta real a la base de datos
                # Por ahora usamos datos simulados
                monthly_data.append({
                    'month': month,
                    'total_amount': 0,  # Se calcularía desde la BD
                    'payment_count': 0   # Se calcularía desde la BD
                })
            
            return monthly_data
            
        except Exception as e:
            print(f"Error al obtener datos mensuales: {e}")
            return []
    
    def get_payment_status_summary(self) -> Dict[str, int]:
        """Obtiene resumen de estados de pago"""
        try:
            # Esta consulta se puede agregar al DatabaseManager
            # Por ahora usamos las estadísticas existentes
            stats = self.get_statistics()
            total_clients = stats['total_clients']
            clients_with_debt = stats['clients_with_debt']
            
            return {
                'paid': total_clients - clients_with_debt,
                'pending': clients_with_debt
            }
            
        except Exception as e:
            print(f"Error al obtener resumen de pagos: {e}")
            return {'paid': 0, 'pending': 0}
    
    # Gestión de Configuración
    def verify_pin(self, pin: str) -> bool:
        """Verifica el PIN del administrador"""
        try:
            return self.db_manager.verify_pin(pin)
        except Exception as e:
            print(f"Error al verificar PIN: {e}")
            return False
    
    def update_pin(self, current_pin: str, new_pin: str) -> tuple:
        """Actualiza el PIN del administrador"""
        try:
            # Validar PIN actual
            if not self.verify_pin(current_pin):
                return False, "PIN actual incorrecto"
            
            # Validar nuevo PIN
            pin_valid, pin_msg = ValidationUtils.validate_pin(new_pin)
            if not pin_valid:
                return False, pin_msg
            
            # Actualizar PIN
            success = self.db_manager.update_pin(new_pin)
            
            if success:
                return True, "PIN actualizado exitosamente"
            else:
                return False, "Error al actualizar el PIN"
                
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    # Filtros y Búsquedas
    def filter_clients_by_status(self, clients: List[ClientWithStatus], filter_type: str) -> List[ClientWithStatus]:
        """Filtra clientes según criterios específicos"""
        try:
            if filter_type == "Solo con deuda":
                return [c for c in clients if c.payment_status == "pendiente"]
            elif filter_type == "Solo al corriente":
                return [c for c in clients if c.payment_status == "pagado"]
            elif filter_type == "Exceso de consumo":
                return [c for c in clients if c.consumption_status == "exceso"]
            else:  # "Todos"
                return clients
                
        except Exception as e:
            print(f"Error al filtrar clientes: {e}")
            return clients
    
    def filter_clients_by_search(self, clients: List[ClientWithStatus], search_term: str) -> List[ClientWithStatus]:
        """Filtra clientes por término de búsqueda"""
        try:
            if not search_term.strip():
                return clients
            
            search_lower = search_term.lower().strip()
            
            filtered = []
            for client in clients:
                if (search_lower in client.name.lower() or 
                    search_lower in client.address.lower() or 
                    search_lower in str(client.id)):
                    filtered.append(client)
            
            return filtered
            
        except Exception as e:
            print(f"Error al filtrar por búsqueda: {e}")
            return clients
