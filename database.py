#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de base de datos para el sistema de agua potable
"""

import sqlite3
import os
from typing import List, Dict, Optional, Tuple, Any

class DatabaseManager:
    def __init__(self, db_name: str = "agua_potable.db"):
        self.db_name = db_name
        self.initialize_database()
        self.migrate_database()

    def get_connection(self) -> sqlite3.Connection:
        """Obtiene una conexión a la base de datos"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize_database(self):
        """Inicializa la estructura de la base de datos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Tabla de usuarios
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    direccion TEXT,
                    telefono TEXT,
                    email TEXT,
                    sesion INTEGER NOT NULL DEFAULT 1 CHECK (sesion IN (1, 2, 3)),
                    estado TEXT DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Cancelado')),
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de pagos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pagos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total REAL NOT NULL,
                    observaciones TEXT,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                )
            ''')
            
            # Tabla de detalle de pagos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS detalle_pagos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pago_id INTEGER NOT NULL,
                    concepto TEXT NOT NULL,
                    mes INTEGER,
                    anio INTEGER,
                    precio REAL NOT NULL,
                    FOREIGN KEY (pago_id) REFERENCES pagos (id)
                )
            ''')
            
            # Tabla de configuración
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configuracion (
                    clave TEXT PRIMARY KEY,
                    valor TEXT,
                    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de conceptos de cobro
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conceptos_cobro (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE,
                    precio REAL NOT NULL,
                    activo INTEGER DEFAULT 1
                )
            ''')
            
            # Insertar configuración por defecto si no existe
            config_default = [
                ('cuota_mensual', '50.0'),
                ('pin_acceso', '1234'),
                ('committee_name', 'Comité de Agua Potable'),
                ('committee_address', 'San Antonio'),
                ('committee_phone', ''),
                ('committee_president', ''),
                ('committee_treasurer', '')
            ]
            
            for clave, valor in config_default:
                cursor.execute('''
                    INSERT OR IGNORE INTO configuracion (clave, valor)
                    VALUES (?, ?)
                ''', (clave, valor))
            
            # Insertar conceptos por defecto
            conceptos_default = [
                ('Cooperación Anual', 100.0),
                ('Toma Nueva', 500.0),
                ('Multa por Inasistencia', 25.0),
                ('Multa por Desperdicio', 75.0),
            ]
            
            for concepto, precio in conceptos_default:
                cursor.execute('''
                    INSERT OR IGNORE INTO conceptos_cobro (nombre, precio)
                    VALUES (?, ?)
                ''', (concepto, precio))
            
            conn.commit()
            
        except sqlite3.Error as e:
            print(f"Error al inicializar la base de datos: {e}")
            conn.rollback()
        finally:
            conn.close()

    def migrate_database(self):
        """Migra la base de datos si es necesario (agrega sesion, elimina numero)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar si la columna 'sesion' existe en la tabla usuarios
            cursor.execute("PRAGMA table_info(usuarios)")
            columns = [info[1] for info in cursor.fetchall()]
            
            if 'sesion' not in columns:
                print("Iniciando migración de base de datos...")
                
                # 1. Renombrar tabla actual
                cursor.execute("ALTER TABLE usuarios RENAME TO usuarios_old")
                
                # 2. Crear nueva tabla con la estructura correcta
                cursor.execute('''
                    CREATE TABLE usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL,
                        direccion TEXT,
                        telefono TEXT,
                        email TEXT,
                        sesion INTEGER NOT NULL DEFAULT 1 CHECK (sesion IN (1, 2, 3)),
                        estado TEXT DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Cancelado')),
                        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 3. Copiar datos (Asumiendo sesion 1 por defecto para usuarios existentes)
                # Nota: 'numero' se pierde en esta migración como se solicitó
                cursor.execute('''
                    INSERT INTO usuarios (id, nombre, direccion, telefono, email, estado, fecha_registro)
                    SELECT id, nombre, direccion, telefono, email, estado, fecha_registro
                    FROM usuarios_old
                ''')
                
                # 4. Eliminar tabla antigua
                cursor.execute("DROP TABLE usuarios_old")
                
                conn.commit()
                print("Migración completada exitosamente.")
                
        except sqlite3.Error as e:
            print(f"Error durante la migración: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    # === GESTIÓN DE USUARIOS ===
    
    def crear_usuario(self, nombre: str, sesion: int, direccion: str = "", 
                     telefono: str = "", email: str = "") -> bool:
        """
        Crea un nuevo usuario
        
        Args:
            nombre: Nombre del usuario
            sesion: Número de sesión (1, 2, 3)
            direccion: Dirección
            telefono: Teléfono
            email: Email
            
        Returns:
            bool: True si se creó exitosamente
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO usuarios (nombre, sesion, direccion, telefono, email)
                VALUES (?, ?, ?, ?, ?)
            ''', (nombre, sesion, direccion, telefono, email))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al crear usuario: {e}")
            return False
        finally:
            conn.close()
    
    def buscar_usuario_por_id(self, user_id: int) -> Optional[Dict]:
        """Busca un usuario por su ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM usuarios WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def buscar_usuarios_por_nombre(self, nombre: str) -> List[Dict]:
        """Busca usuarios por nombre (búsqueda parcial)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM usuarios 
                WHERE nombre LIKE ? 
                ORDER BY nombre
            ''', (f'%{nombre}%',))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def actualizar_usuario(self, usuario_id: int, **kwargs) -> bool:
        """Actualiza los datos de un usuario"""
        if not kwargs:
            return False
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Construir la consulta dinámicamente
            campos = list(kwargs.keys())
            valores = list(kwargs.values())
            valores.append(usuario_id)
            
            set_clause = ', '.join([f"{campo} = ?" for campo in campos])
            
            cursor.execute(f'''
                UPDATE usuarios 
                SET {set_clause}
                WHERE id = ?
            ''', valores)
            
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def cambiar_estado_usuario(self, usuario_id: int, estado: str) -> bool:
        """Cambia el estado de un usuario (Activo/Cancelado)"""
        if estado not in ['Activo', 'Cancelado']:
            return False
        return self.actualizar_usuario(usuario_id, estado=estado)
    
    def obtener_todos_usuarios(self, solo_activos: bool = False) -> List[Dict]:
        """Obtiene todos los usuarios"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if solo_activos:
                cursor.execute('''
                    SELECT * FROM usuarios 
                    WHERE estado = 'Activo' 
                    ORDER BY id
                ''')
            else:
                cursor.execute('SELECT * FROM usuarios ORDER BY id')
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def eliminar_usuario(self, usuario_id: int) -> bool:
        """Elimina un usuario por su ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Primero verificar si tiene pagos
            cursor.execute('SELECT COUNT(*) FROM pagos WHERE usuario_id = ?', (usuario_id,))
            if cursor.fetchone()[0] > 0:
                # Si tiene pagos, no permitir eliminar (o se podría hacer soft delete)
                return False
                
            cursor.execute('DELETE FROM usuarios WHERE id = ?', (usuario_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al eliminar usuario: {e}")
            return False
        finally:
            conn.close()
    
    # === GESTIÓN DE PAGOS ===
    
    def obtener_pagos_usuario_anio(self, usuario_id: int, anio: int) -> List[int]:
        """
        Obtiene los meses pagados por un usuario en un año específico
        
        Returns:
            List[int]: Lista de meses pagados (1-12)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT DISTINCT mes 
                FROM detalle_pagos dp
                JOIN pagos p ON dp.pago_id = p.id
                WHERE p.usuario_id = ? AND dp.anio = ? AND dp.mes IS NOT NULL
                ORDER BY mes
            ''', (usuario_id, anio))
            
            rows = cursor.fetchall()
            return [row[0] for row in rows]
        finally:
            conn.close()
    
    def registrar_pago(self, usuario_id: int, detalles: List[Dict], observaciones: str = "") -> int:
        """
        Registra un pago completo con detalles flexibles
        
        Args:
            usuario_id: ID del usuario
            detalles: Lista de diccionarios {'concepto': str, 'precio': float, 'mes': int|None, 'anio': int|None}
            observaciones: Observaciones del pago
            
        Returns:
            int: ID del pago registrado, 0 si hay error
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Calcular total
            total = sum(d['precio'] for d in detalles)
            
            # Insertar el pago principal
            cursor.execute('''
                INSERT INTO pagos (usuario_id, total, observaciones)
                VALUES (?, ?, ?)
            ''', (usuario_id, total, observaciones))
            
            pago_id = cursor.lastrowid
            
            # Insertar detalles
            for detalle in detalles:
                cursor.execute('''
                    INSERT INTO detalle_pagos (pago_id, concepto, mes, anio, precio)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    pago_id, 
                    detalle['concepto'], 
                    detalle.get('mes'), 
                    detalle.get('anio'), 
                    detalle['precio']
                ))
            
            conn.commit()
            return pago_id
            
        except sqlite3.Error as e:
            print(f"Error al registrar pago: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()
    
    def obtener_pagos_usuario(self, usuario_id: int) -> List[Dict]:
        """Obtiene el historial de pagos de un usuario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT p.*, u.nombre
                FROM pagos p
                JOIN usuarios u ON p.usuario_id = u.id
                WHERE p.usuario_id = ?
                ORDER BY p.fecha_pago DESC
            ''', (usuario_id,))
            
            rows = cursor.fetchall()
            pagos = [dict(row) for row in rows]
            
            # Obtener detalles de cada pago
            for pago in pagos:
                cursor.execute('''
                    SELECT * FROM detalle_pagos 
                    WHERE pago_id = ?
                    ORDER BY mes
                ''', (pago['id'],))
                
                detalles = cursor.fetchall()
                pago['detalles'] = [dict(detalle) for detalle in detalles]
            
            return pagos
        finally:
            conn.close()
    
    def obtener_detalle_pago(self, pago_id: int) -> Dict:
        """Obtiene el detalle completo de un pago para generar recibo"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Obtener información del pago y usuario
            cursor.execute('''
                SELECT p.*, u.nombre, u.direccion, u.sesion
                FROM pagos p
                JOIN usuarios u ON p.usuario_id = u.id
                WHERE p.id = ?
            ''', (pago_id,))
            
            pago_row = cursor.fetchone()
            if not pago_row:
                return {}
            
            pago = dict(pago_row)
            
            # Obtener detalles del pago
            cursor.execute('''
                SELECT * FROM detalle_pagos 
                WHERE pago_id = ?
                ORDER BY mes, concepto
            ''', (pago_id,))
            
            detalles = cursor.fetchall()
            pago['detalles'] = [dict(detalle) for detalle in detalles]
            
            return pago
        finally:
            conn.close()
    
    # === GESTIÓN DE CONFIGURACIÓN ===
    
    def obtener_configuracion(self, clave: str) -> Optional[str]:
        """Obtiene un valor de configuración"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT valor FROM configuracion WHERE clave = ?', (clave,))
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            conn.close()
    
    def actualizar_configuracion(self, clave: str, valor: str) -> bool:
        """Actualiza un valor de configuración"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE configuracion 
                SET valor = ?, fecha_modificacion = CURRENT_TIMESTAMP
                WHERE clave = ?
            ''', (valor, clave))
            
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def verificar_pin(self, pin: str) -> bool:
        """Verifica si el PIN ingresado es correcto"""
        pin_actual = self.obtener_configuracion('pin_acceso')
        return pin_actual == pin
    
    # === GESTIÓN DE CONCEPTOS DE COBRO ===
    
    def obtener_conceptos_cobro(self, solo_activos: bool = True) -> List[Dict]:
        """Obtiene todos los conceptos de cobro"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if solo_activos:
                cursor.execute('''
                    SELECT * FROM conceptos_cobro 
                    WHERE activo = 1 
                    ORDER BY nombre
                ''')
            else:
                cursor.execute('SELECT * FROM conceptos_cobro ORDER BY nombre')
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def crear_concepto_cobro(self, nombre: str, precio: float) -> bool:
        """Crea un nuevo concepto de cobro"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO conceptos_cobro (nombre, precio)
                VALUES (?, ?)
            ''', (nombre, precio))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Ya existe
        finally:
            conn.close()
    
    def actualizar_concepto_cobro(self, concepto_id: int, nombre: str = None, 
                                 precio: float = None, activo: bool = None) -> bool:
        """Actualiza un concepto de cobro"""
        campos_actualizar = {}
        
        if nombre is not None:
            campos_actualizar['nombre'] = nombre
        if precio is not None:
            campos_actualizar['precio'] = precio
        if activo is not None:
            campos_actualizar['activo'] = 1 if activo else 0
        
        if not campos_actualizar:
            return False
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            campos = list(campos_actualizar.keys())
            valores = list(campos_actualizar.values())
            valores.append(concepto_id)
            
            set_clause = ', '.join([f"{campo} = ?" for campo in campos])
            
            cursor.execute(f'''
                UPDATE conceptos_cobro 
                SET {set_clause}
                WHERE id = ?
            ''', valores)
            
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def eliminar_concepto_cobro(self, concepto_id: int) -> bool:
        """Desactiva un concepto de cobro (no lo elimina físicamente)"""
        return self.actualizar_concepto_cobro(concepto_id, activo=False)


# Función de utilidad para obtener una instancia global del gestor
_db_manager = None

def get_db_manager() -> DatabaseManager:
    """Obtiene una instancia global del gestor de base de datos"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager