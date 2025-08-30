"""
Sistema de Gestión de Pago de Agua
Módulo: Modelos de Datos
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Client:
    """Modelo de datos para Cliente"""
    id: Optional[int] = None
    name: str = ""
    address: str = ""
    status: str = "activo"  # activo, inactivo
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

@dataclass
class Payment:
    """Modelo de datos para Pago"""
    id: Optional[int] = None
    client_id: int = 0
    amount: float = 0.0
    payment_date: Optional[datetime] = None
    status: str = "pagado"  # pagado, pendiente
    notes: str = ""
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'client_id': self.client_id,
            'amount': self.amount,
            'payment_date': self.payment_date,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at
        }

@dataclass
class WaterConsumption:
    """Modelo de datos para Consumo de Agua"""
    id: Optional[int] = None
    client_id: int = 0
    consumption_type: str = "normal"  # normal, exceso
    consumption_date: Optional[datetime] = None
    notes: str = ""
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'client_id': self.client_id,
            'consumption_type': self.consumption_type,
            'consumption_date': self.consumption_date,
            'notes': self.notes,
            'created_at': self.created_at
        }

@dataclass
class ClientWithStatus:
    """Modelo extendido de Cliente con estados de pago y consumo"""
    id: int
    name: str
    address: str
    status: str
    payment_status: str  # pagado, pendiente, sin_pagos
    consumption_status: str  # normal, exceso
    
    def get_status_icon(self) -> str:
        """Retorna el ícono según el estado del cliente"""
        if self.payment_status == "pendiente":
            return "❌"
        elif self.consumption_status == "exceso":
            return "💧"
        elif self.payment_status == "pagado":
            return "✅"
        else:
            return "⚪"  # Sin pagos registrados
    
    def get_status_text(self) -> str:
        """Retorna el texto descriptivo del estado"""
        if self.payment_status == "pendiente":
            return "Pago Pendiente"
        elif self.consumption_status == "exceso":
            return "Exceso de Consumo"
        elif self.payment_status == "pagado":
            return "Al Corriente"
        else:
            return "Sin Registros"
