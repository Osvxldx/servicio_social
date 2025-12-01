#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de base de datos para el sistema de agua potable
"""

import sqlite3
import os
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name: str = "agua_potable.db"):
        self.db_name = db_name
        self.initialize_database()
        self.migrate_database()
        self.migrate_history_table()

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
                    vacas INTEGER DEFAULT 0,
                    inquilinos INTEGER DEFAULT 0,
                    tomas INTEGER DEFAULT 1,
                    estado TEXT DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Cancelado', 'Baja', 'Suspendida')),
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_alta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_baja TIMESTAMP
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
                    cantidad INTEGER DEFAULT 1,
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

            # Tabla de historial de estatus
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historial_estatus (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    estado TEXT NOT NULL,
                    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    observaciones TEXT,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                )
            ''')
            
            # Insertar configuración por defecto si no existe
            config_default = [
                ('cuota_mensual', '70.0'),
                ('costo_vacas', '0.0'),
                ('costo_inquilinos', '0.0'),
                ('costo_cooperacion', '100.0'),
                ('costo_toma_nueva', '500.0'),
                ('multa_retraso', '100.0'),
                ('multa_inasistencia', '200.0'),
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
            
            conn.commit()
            
        except sqlite3.Error as e:
            print(f"Error al inicializar la base de datos: {e}")
            conn.rollback()
        finally:
            conn.close()

    def migrate_database(self):
        """Migra la base de datos si es necesario (agrega sesion, vacas, inquilinos)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar columnas existentes
            cursor.execute("PRAGMA table_info(usuarios)")
            columns = [info[1] for info in cursor.fetchall()]
            
            # Verificar si falta alguna columna nueva
            missing_columns = []
            if 'sesion' not in columns: missing_columns.append('sesion')
            if 'vacas' not in columns: missing_columns.append('vacas')
            if 'inquilinos' not in columns: missing_columns.append('inquilinos')
            if 'tomas' not in columns: missing_columns.append('tomas')
            if 'fecha_alta' not in columns: missing_columns.append('fecha_alta')
            
            # También necesitamos migrar si el check de estado es antiguo, pero eso es difícil de detectar con PRAGMA.
            # Asumiremos que si faltan columnas o si queremos asegurar la estructura, hacemos la migración.
            # Para simplificar, si ya tenemos tomas, asumimos que la estructura es reciente, 
            # PERO si el usuario pide actualizar estados, mejor aseguramos.
            # Vamos a forzar migración si falta 'tomas' o 'fecha_alta'.
            
            if missing_columns:
                print(f"Iniciando migración de base de datos. Faltan: {missing_columns}")
                
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
                        vacas INTEGER DEFAULT 0,
                        inquilinos INTEGER DEFAULT 0,
                        tomas INTEGER DEFAULT 1,
                        estado TEXT DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Cancelado', 'Baja', 'Suspendida')),
                        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        fecha_alta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        fecha_baja TIMESTAMP
                    )
                ''')
                
                # 3. Copiar datos
                # Construir query dinámico basado en columnas que existían
                cols_to_copy = ['id', 'nombre', 'direccion', 'telefono', 'email', 'estado', 'fecha_registro']
                if 'sesion' in columns: cols_to_copy.append('sesion')
                if 'vacas' in columns: cols_to_copy.append('vacas')
                if 'inquilinos' in columns: cols_to_copy.append('inquilinos')
                
                # Columnas destino (las mismas que origen)
                cols_dest = list(cols_to_copy)
                
                # Si existían las nuevas (caso raro), las copiamos, si no, toman default
                if 'tomas' in columns: 
                    cols_to_copy.append('tomas')
                    cols_dest.append('tomas')
                else:
                    # Si no existía, se llenará con default 1
                    pass

                if 'fecha_alta' in columns:
                    cols_to_copy.append('fecha_alta')
                    cols_dest.append('fecha_alta')
                else:
                    # Si no existía, usamos fecha_registro como fecha_alta
                    cols_dest.append('fecha_alta')
                    cols_to_copy.append('fecha_registro') # Usamos fecha_registro como fuente
                
                if 'fecha_baja' in columns:
                    cols_to_copy.append('fecha_baja')
                    cols_dest.append('fecha_baja')

                cols_src_str = ", ".join(cols_to_copy)
                cols_dest_str = ", ".join(cols_dest)
                
                cursor.execute(f'''
                    INSERT INTO usuarios ({cols_dest_str})
                    SELECT {cols_src_str}
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

    def migrate_history_table(self):
        """Asegura que exista la tabla de historial y rellena datos iniciales si está vacía"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Crear tabla si no existe (ya está en initialize, pero por si acaso en updates)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historial_estatus (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    estado TEXT NOT NULL,
                    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    observaciones TEXT,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                )
            ''')
            
            # Verificar si está vacía
            cursor.execute('SELECT COUNT(*) FROM historial_estatus')
            count = cursor.fetchone()[0]
            
            if count == 0:
                print("Migrando historial de estatus para usuarios existentes...")
                # Obtener todos los usuarios
                cursor.execute('SELECT * FROM usuarios')
                users = cursor.fetchall()
                
                for u in users:
                    # 1. Registro inicial (Activo)
                    fecha_alta = u['fecha_alta'] or u['fecha_registro']
                    cursor.execute('''
                        INSERT INTO historial_estatus (usuario_id, estado, fecha_movimiento, observaciones)
                        VALUES (?, ?, ?, ?)
                    ''', (u['id'], 'Activo', fecha_alta, 'Registro inicial / Migración'))
                    
                    # 2. Si está en baja/cancelado, agregar el movimiento de baja
                    if u['estado'] != 'Activo':
                        fecha_baja = u['fecha_baja'] or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        cursor.execute('''
                            INSERT INTO historial_estatus (usuario_id, estado, fecha_movimiento, observaciones)
                            VALUES (?, ?, ?, ?)
                        ''', (u['id'], u['estado'], fecha_baja, 'Estado actual al migrar'))
                
                conn.commit()
                print("Migración de historial completada.")
                
        except sqlite3.Error as e:
            print(f"Error migrando historial: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    # === GESTIÓN DE USUARIOS ===
    
    def crear_usuario(self, nombre: str, sesion: int, direccion: str = "", 
                     telefono: str = "", email: str = "", vacas: int = 0, inquilinos: int = 0, tomas: int = 1, estado: str = "Activo") -> bool:
        """
        Crea un nuevo usuario
        
        Args:
            nombre: Nombre del usuario
            sesion: Número de sesión (1, 2, 3)
            direccion: Dirección
            telefono: Teléfono
            email: Email
            vacas: Número de vacas
            inquilinos: Número de inquilinos
            tomas: Número de tomas
            estado: Estado inicial
            
        Returns:
            bool: True si se creó exitosamente
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Buscar el primer ID disponible (hueco)
            cursor.execute('SELECT id FROM usuarios ORDER BY id')
            ids = [row[0] for row in cursor.fetchall()]
            
            nuevo_id = 1
            for id_ocupado in ids:
                if nuevo_id < id_ocupado:
                    break
                nuevo_id += 1
            
            # Insertar con el ID específico
            cursor.execute('''
                INSERT INTO usuarios (id, nombre, sesion, direccion, telefono, email, vacas, inquilinos, tomas, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nuevo_id, nombre, sesion, direccion, telefono, email, vacas, inquilinos, tomas, estado))
            conn.commit()
            
            # Registrar en historial
            self.registrar_cambio_estatus(nuevo_id, estado, observaciones="Registro inicial")
            
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
        """Cambia el estado de un usuario (Activo/Cancelado/Baja/Suspendida)"""
        if estado not in ['Activo', 'Cancelado', 'Baja', 'Suspendida']:
            return False
        
        updates = {'estado': estado}
        if estado in ['Cancelado', 'Baja']:
            updates['fecha_baja'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        elif estado == 'Activo':
            updates['fecha_baja'] = None
            
        if self.actualizar_usuario(usuario_id, **updates):
            # Registrar en historial
            self.registrar_cambio_estatus(usuario_id, estado, observaciones="Cambio de estado manual")
            return True
        return False

    def registrar_cambio_estatus(self, usuario_id: int, estado: str, fecha: str = None, observaciones: str = ""):
        """Registra un cambio de estatus en el historial"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if not fecha:
                fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
            cursor.execute('''
                INSERT INTO historial_estatus (usuario_id, estado, fecha_movimiento, observaciones)
                VALUES (?, ?, ?, ?)
            ''', (usuario_id, estado, fecha, observaciones))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error registrando historial: {e}")
        finally:
            conn.close()

    def obtener_historial_estatus(self, usuario_id: int) -> List[Dict]:
        """Obtiene el historial de estatus de un usuario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT * FROM historial_estatus 
                WHERE usuario_id = ? 
                ORDER BY fecha_movimiento
            ''', (usuario_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def es_usuario_activo_en_fecha(self, usuario_id: int, fecha: datetime) -> bool:
        """Determina si el usuario estaba activo en una fecha específica basado en el historial"""
        historial = self.obtener_historial_estatus(usuario_id)
        if not historial:
            # Fallback: checar estado actual si no hay historial (no debería pasar tras migración)
            u = self.buscar_usuario_por_id(usuario_id)
            if not u: return False
            # Asumir activo desde registro si no hay más info
            fecha_reg = datetime.strptime(u['fecha_alta'] or u['fecha_registro'], '%Y-%m-%d %H:%M:%S')
            return fecha >= fecha_reg if u['estado'] == 'Activo' else False

        # Recorrer historial cronológicamente
        estado_actual = 'Inactivo' # Asumimos inactivo antes del primer registro
        
        # Encontrar el estado vigente en la fecha dada
        estado_vigente = 'Inactivo'
        
        for evento in historial:
            fecha_evento = datetime.strptime(evento['fecha_movimiento'], '%Y-%m-%d %H:%M:%S')
            if fecha_evento <= fecha:
                estado_actual = evento['estado']
            else:
                break
        
        return estado_actual == 'Activo'
    
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
        """Elimina un usuario por su ID y todo su historial de pagos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Obtener IDs de pagos del usuario
            cursor.execute('SELECT id FROM pagos WHERE usuario_id = ?', (usuario_id,))
            pagos = cursor.fetchall()
            pago_ids = [p[0] for p in pagos]
            
            if pago_ids:
                # 2. Eliminar detalles de pagos
                placeholders = ','.join(['?'] * len(pago_ids))
                cursor.execute(f'DELETE FROM detalle_pagos WHERE pago_id IN ({placeholders})', pago_ids)
                
                # 3. Eliminar pagos
                cursor.execute('DELETE FROM pagos WHERE usuario_id = ?', (usuario_id,))
            
            # 4. Eliminar usuario
            cursor.execute('DELETE FROM usuarios WHERE id = ?', (usuario_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al eliminar usuario: {e}")
            conn.rollback()
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
    
    def obtener_meses_adeudo(self, usuario_id: int, anio: int = None) -> Dict:
        """
        Calcula los meses que el usuario debe pagar en un año específico,
        aplicando reglas de negocio:
        - Costo base: $70
        - Recargo: $100 si pasa del 3er domingo del mes
        - Penalización: Costo doble si debe 3 meses o más
        - Suspensión: Si debe más de 6 meses
        
        Returns:
            Dict: {
                'detalles': List[Dict] (mes, monto, concepto),
                'total': float,
                'suspension': bool,
                'meses_cantidad': int
            }
        """
        import calendar
        
        if anio is None:
            anio = datetime.now().year
        
        # 1. Obtener meses pagados
        pagos = self.obtener_pagos_usuario_anio(usuario_id, anio)
        pagos_set = set(pagos)
        
        # 2. Obtener historial para saber meses activos
        historial = self.obtener_historial_estatus(usuario_id)
        meses_a_pagar = []
        mes_fin_calculo = 12
        if anio == datetime.now().year:
            mes_fin_calculo = datetime.now().month
            
        for m in range(1, mes_fin_calculo + 1):
            # Si es mes actual, verificar si ya pasó fecha de corte? 
            # La regla dice "pagar los 3 primeros domingos". Si estamos en el mes, se debe pagar.
            
            fecha_mes = datetime(anio, m, 15) # Día arbitrario para verificar estatus
            if fecha_mes > datetime.now():
                continue
                
            activo = False
            if not historial:
                # Lógica legacy sin historial
                u = self.buscar_usuario_por_id(usuario_id)
                if u:
                    fecha_reg = datetime.strptime(u['fecha_alta'] or u['fecha_registro'], '%Y-%m-%d %H:%M:%S')
                    if fecha_reg.year < anio or (fecha_reg.year == anio and fecha_reg.month <= m):
                        if u['estado'] == 'Activo':
                            activo = True
                        elif u['fecha_baja']:
                            fecha_baja = datetime.strptime(u['fecha_baja'], '%Y-%m-%d %H:%M:%S')
                            if fecha_baja.year > anio or (fecha_baja.year == anio and fecha_baja.month >= m):
                                activo = True
            else:
                activo = self.es_usuario_activo_en_fecha(usuario_id, fecha_mes)
            
            if activo and m not in pagos_set:
                meses_a_pagar.append(m)

        # 3. Calcular costos
        detalles = []
        total = 0.0
        cantidad_meses = len(meses_a_pagar)
        
        # Regla: Un atraso de 3 meses o más, el costo es doble
        aplicar_doble = cantidad_meses >= 3
        
        # Regla: Adeudo mayor de 6 meses es suspensión
        suspension = cantidad_meses > 6
        
        cuota_base = float(self.obtener_configuracion('cuota_mensual') or 70.0)
        # El recargo sube a $100 (diferencia de $30 si base es 70)
        monto_con_recargo = 100.0 
        
        u = self.buscar_usuario_por_id(usuario_id)
        tomas = u.get('tomas', 1)
        
        meses_nombres = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                         'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

        now = datetime.now()
        
        for mes_num in meses_a_pagar:
            nombre_mes = meses_nombres[mes_num - 1]
            
            # Calcular fecha límite (3er domingo del mes)
            c = calendar.monthcalendar(anio, mes_num)
            first_week = c[0]
            second_week = c[1]
            third_week = c[2]
            fourth_week = c[3]

            # Si el primer día es domingo, first_week[6] es 1.
            # Buscamos el 3er domingo.
            domingos = [week[6] for week in c if week[6] != 0]
            dia_tercer_domingo = domingos[2]
            
            fecha_limite = datetime(anio, mes_num, dia_tercer_domingo, 23, 59, 59)
            
            # Determinar costo base del mes
            costo = cuota_base
            es_tardio = False
            
            # Si ya pasó el mes, o si estamos en el mes pero pasó el 3er domingo
            if anio < now.year or (anio == now.year and mes_num < now.month):
                es_tardio = True
            elif anio == now.year and mes_num == now.month:
                if now > fecha_limite:
                    es_tardio = True
            
            if es_tardio:
                costo = monto_con_recargo
            
            # Aplicar tomas
            costo_total_mes = costo * tomas
            
            # Aplicar penalización doble
            if aplicar_doble:
                costo_total_mes *= 2
                nombre_mes += " (Penalización Doble)"
            elif es_tardio:
                nombre_mes += " (Tardío)"
                
            detalles.append({
                'mes': nombre_mes,
                'monto': costo_total_mes,
                'concepto': f"Mensualidad {nombre_mes}"
            })
            total += costo_total_mes
            
        return {
            'detalles': detalles,
            'total': total,
            'suspension': suspension,
            'meses_cantidad': cantidad_meses
        }

    def obtener_adeudo_inasistencias(self, usuario_id: int, anio: int = None) -> List[Dict]:
        """
        Calcula adeudo por inasistencias (6 al año: Feb, Abr, Jun, Ago, Oct, Dic).
        Se condonan si hay pago anual antes del 31 de Marzo.
        """
        import calendar
        
        if anio is None:
            anio = datetime.now().year
            
        # 1. Verificar si hay pago anual anticipado
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Buscar un pago que cubra todo el año o tenga concepto "Anual"
        # Simplificación: Buscamos si pagó Diciembre del año en cuestión ANTES del 31 de Marzo
        # O si existe un concepto "Pago Anual"
        cursor.execute('''
            SELECT p.fecha_pago 
            FROM detalle_pagos dp
            JOIN pagos p ON dp.pago_id = p.id
            WHERE p.usuario_id = ? AND dp.anio = ? AND (dp.concepto LIKE '%Anual%' OR dp.mes = 12)
            ORDER BY p.fecha_pago ASC
            LIMIT 1
        ''', (usuario_id, anio))
        
        pago_anual = cursor.fetchone()
        if pago_anual:
            fecha_pago = datetime.strptime(pago_anual[0], '%Y-%m-%d %H:%M:%S')
            fecha_limite = datetime(anio, 3, 31, 23, 59, 59)
            if fecha_pago <= fecha_limite:
                return [] # Condonado
        
        conn.close()
        
        # 2. Calcular inasistencias vencidas
        meses_inasistencia = [2, 4, 6, 8, 10, 12] # Feb, Abr, Jun...
        meses_nombres = {2: 'Febrero', 4: 'Abril', 6: 'Junio', 8: 'Agosto', 10: 'Octubre', 12: 'Diciembre'}
        
        adeudos = []
        costo_inasistencia = float(self.obtener_configuracion('multa_inasistencia') or 200.0)
        
        now = datetime.now()
        
        # Verificar historial para ver si estaba activo en ese mes
        historial = self.obtener_historial_estatus(usuario_id)
        
        for m in meses_inasistencia:
            # La inasistencia se cobra al finalizar el mes (o cuando ocurre la faena, asumimos fin de mes)
            fecha_fin_mes = datetime(anio, m, calendar.monthrange(anio, m)[1], 23, 59, 59)
            
            if now > fecha_fin_mes:
                # Verificar si estaba activo
                activo = False
                if not historial:
                     u = self.buscar_usuario_por_id(usuario_id)
                     if u and u['estado'] == 'Activo': activo = True # Simplificado
                else:
                    activo = self.es_usuario_activo_en_fecha(usuario_id, fecha_fin_mes)
                
                if activo:
                    # Verificar si ya pagó esta inasistencia (opcional, si se registra como concepto separado)
                    # Por ahora asumimos que se debe si no hay pago anual
                    adeudos.append({
                        'mes': meses_nombres[m],
                        'monto': costo_inasistencia,
                        'concepto': f"Inasistencia {meses_nombres[m]}"
                    })
                    
        return adeudos

    def registrar_pago(self, usuario_id: int, detalles: List[Dict], observaciones: str = "") -> int:
        """
        Registra un pago completo con detalles flexibles
        
        Args:
            usuario_id: ID del usuario
            detalles: Lista de diccionarios {'concepto': str, 'precio': float, 'mes': int|None, 'anio': int|None, 'cantidad': int}
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
                    INSERT INTO detalle_pagos (pago_id, concepto, mes, anio, precio, cantidad)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    pago_id, 
                    detalle['concepto'], 
                    detalle.get('mes'), 
                    detalle.get('anio'), 
                    detalle['precio'],
                    detalle.get('cantidad', 1)
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
                SELECT p.*, u.nombre, u.direccion, u.sesion, u.vacas, u.inquilinos
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


# Función de utilidad para obtener una instancia global del gestor
_db_manager = None

def get_db_manager() -> DatabaseManager:
    """Obtiene una instancia global del gestor de base de datos"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
