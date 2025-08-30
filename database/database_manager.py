"""
Sistema de Gestión de Pago de Agua
Módulo: Gestor de Base de Datos SQLite
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class DatabaseManager:
    def __init__(self, db_path: str = "database/agua_system.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Obtiene una conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
        return conn
    
    def init_database(self):
        """Inicializa la base de datos y crea las tablas necesarias"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabla de administradores (para el PIN)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pin TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de clientes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    status TEXT DEFAULT 'activo' CHECK(status IN ('activo', 'inactivo')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de pagos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pagado' CHECK(status IN ('pagado', 'pendiente')),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients (id)
                )
            ''')
            
            # Tabla de consumo de agua
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS water_consumption (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    consumption_type TEXT DEFAULT 'normal' CHECK(consumption_type IN ('normal', 'exceso')),
                    consumption_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients (id)
                )
            ''')
            
            # Insertar PIN por defecto si no existe admin
            cursor.execute('SELECT COUNT(*) FROM admins')
            if cursor.fetchone()[0] == 0:
                cursor.execute('INSERT INTO admins (pin) VALUES (?)', ('1234',))
            
            conn.commit()
    
    def verify_pin(self, pin: str) -> bool:
        """Verifica si el PIN es correcto"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM admins WHERE pin = ?', (pin,))
            return cursor.fetchone()[0] > 0
    
    def update_pin(self, new_pin: str) -> bool:
        """Actualiza el PIN del administrador"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE admins SET pin = ? WHERE id = 1', (new_pin,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error al actualizar PIN: {e}")
            return False
    
    # CRUD de Clientes
    def add_client(self, name: str, address: str) -> Optional[int]:
        """Agrega un nuevo cliente y retorna su ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO clients (name, address) VALUES (?, ?)',
                    (name, address)
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error al agregar cliente: {e}")
            return None
    
    def get_client(self, client_id: int) -> Optional[Dict]:
        """Obtiene un cliente por ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_clients(self) -> List[Dict]:
        """Obtiene todos los clientes"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM clients ORDER BY name')
            return [dict(row) for row in cursor.fetchall()]
    
    def search_clients(self, search_term: str) -> List[Dict]:
        """Busca clientes por nombre, dirección o ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            search_term = f"%{search_term}%"
            cursor.execute('''
                SELECT * FROM clients 
                WHERE name LIKE ? OR address LIKE ? OR CAST(id AS TEXT) LIKE ?
                ORDER BY name
            ''', (search_term, search_term, search_term))
            return [dict(row) for row in cursor.fetchall()]
    
    def update_client(self, client_id: int, name: str, address: str, status: str) -> bool:
        """Actualiza un cliente"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE clients 
                    SET name = ?, address = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (name, address, status, client_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al actualizar cliente: {e}")
            return False
    
    def delete_client(self, client_id: int) -> bool:
        """Elimina un cliente (solo si no tiene pagos asociados)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Verificar si tiene pagos
                cursor.execute('SELECT COUNT(*) FROM payments WHERE client_id = ?', (client_id,))
                if cursor.fetchone()[0] > 0:
                    return False  # No se puede eliminar si tiene pagos
                
                cursor.execute('DELETE FROM clients WHERE id = ?', (client_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al eliminar cliente: {e}")
            return False
    
    # CRUD de Pagos
    def add_payment(self, client_id: int, amount: float, status: str = 'pagado', notes: str = '') -> Optional[int]:
        """Agrega un nuevo pago"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO payments (client_id, amount, status, notes)
                    VALUES (?, ?, ?, ?)
                ''', (client_id, amount, status, notes))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error al agregar pago: {e}")
            return None
    
    def get_client_payments(self, client_id: int) -> List[Dict]:
        """Obtiene todos los pagos de un cliente"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM payments 
                WHERE client_id = ? 
                ORDER BY payment_date DESC
            ''', (client_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_payments_by_date(self, date: str) -> List[Dict]:
        """Obtiene pagos por fecha específica"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.*, c.name, c.address 
                FROM payments p
                JOIN clients c ON p.client_id = c.id
                WHERE DATE(p.payment_date) = ?
                ORDER BY p.payment_date DESC
            ''', (date,))
            return [dict(row) for row in cursor.fetchall()]
    
    def update_payment_status(self, payment_id: int, status: str) -> bool:
        """Actualiza el estado de un pago"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE payments SET status = ? WHERE id = ?
                ''', (status, payment_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al actualizar pago: {e}")
            return False
    
    # Gestión de Consumo de Agua
    def add_water_consumption(self, client_id: int, consumption_type: str = 'normal', notes: str = '') -> Optional[int]:
        """Registra consumo de agua"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO water_consumption (client_id, consumption_type, notes)
                    VALUES (?, ?, ?)
                ''', (client_id, consumption_type, notes))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error al registrar consumo: {e}")
            return None
    
    def get_client_consumption(self, client_id: int) -> List[Dict]:
        """Obtiene el historial de consumo de un cliente"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM water_consumption 
                WHERE client_id = ? 
                ORDER BY consumption_date DESC
            ''', (client_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    # Métodos para Dashboard y Reportes
    def get_clients_with_payment_status(self) -> List[Dict]:
        """Obtiene clientes con su estado de pago más reciente"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    c.id,
                    c.name,
                    c.address,
                    c.status,
                    COALESCE(p.status, 'sin_pagos') as payment_status,
                    COALESCE(wc.consumption_type, 'normal') as consumption_status
                FROM clients c
                LEFT JOIN (
                    SELECT client_id, status,
                           ROW_NUMBER() OVER (PARTITION BY client_id ORDER BY payment_date DESC) as rn
                    FROM payments
                ) p ON c.id = p.client_id AND p.rn = 1
                LEFT JOIN (
                    SELECT client_id, consumption_type,
                           ROW_NUMBER() OVER (PARTITION BY client_id ORDER BY consumption_date DESC) as rn
                    FROM water_consumption
                ) wc ON c.id = wc.client_id AND wc.rn = 1
                ORDER BY c.name
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict:
        """Obtiene estadísticas generales del sistema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total de clientes
            cursor.execute('SELECT COUNT(*) FROM clients WHERE status = "activo"')
            total_clients = cursor.fetchone()[0]
            
            # Clientes con deuda
            cursor.execute('''
                SELECT COUNT(DISTINCT client_id) FROM payments 
                WHERE status = "pendiente"
            ''')
            clients_with_debt = cursor.fetchone()[0]
            
            # Pagos del mes actual
            cursor.execute('''
                SELECT COUNT(*) FROM payments 
                WHERE strftime('%Y-%m', payment_date) = strftime('%Y-%m', 'now')
                AND status = "pagado"
            ''')
            payments_this_month = cursor.fetchone()[0]
            
            # Clientes con exceso de consumo
            cursor.execute('''
                SELECT COUNT(DISTINCT client_id) FROM water_consumption 
                WHERE consumption_type = "exceso"
                AND strftime('%Y-%m', consumption_date) = strftime('%Y-%m', 'now')
            ''')
            excess_consumption = cursor.fetchone()[0]
            
            return {
                'total_clients': total_clients,
                'clients_with_debt': clients_with_debt,
                'payments_this_month': payments_this_month,
                'excess_consumption': excess_consumption
            }
