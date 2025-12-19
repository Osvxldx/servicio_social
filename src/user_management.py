#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de gestión de usuarios para el sistema de agua potable
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from .database import get_db_manager
import re
import os
from .payment_history import PaymentHistoryWindow

class UserManagementWindow:
    _instance = None
    
    def __new__(cls, parent=None):
        if cls._instance is None:
            cls._instance = super(UserManagementWindow, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self, parent=None):
        if self.initialized:
            try:
                if self.root.winfo_exists():
                    if self.root.state() == 'iconic':
                        self.root.deiconify()
                    self.root.lift()
                    return
            except Exception:
                pass
        
        self.initialized = True
        self.root = tk.Toplevel(parent)
        self.root.title("Gestión de Usuarios")
        self.root.geometry("1100x750") # Slightly larger
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Variables
        self.search_id_var = tk.StringVar()
        self.search_name_var = tk.StringVar()
        
        self.user_id_var = tk.StringVar()
        self.user_name_var = tk.StringVar()
        self.user_address_var = tk.StringVar()
        self.user_phone_var = tk.StringVar()
        self.user_email_var = tk.StringVar()
        self.user_session_var = tk.StringVar(value="1")
        self.user_status_var = tk.StringVar(value="Activo")
        self.user_vacas_var = tk.IntVar(value=0)
        self.user_inquilinos_var = tk.IntVar(value=0)
        self.user_tomas_var = tk.IntVar(value=1)
        self.user_hidrantes_var = tk.IntVar(value=0)
        self.user_number_var = tk.StringVar()
        self.user_fecha_alta_var = tk.StringVar()
        self.user_fecha_baja_var = tk.StringVar()
        self.user_seccionar_var = tk.DoubleVar(value=0)
        self.user_t_pozo_var = tk.DoubleVar(value=0)
        self.user_conagua_var = tk.DoubleVar(value=0)
        self.user_drenaje_var = tk.DoubleVar(value=0)
        self.user_obs_anterior_var = tk.StringVar() # For display maybe?

        
        # Filtros
        self.filter_sesion_var = tk.StringVar(value="Todas")
        self.filter_status_var = tk.StringVar(value="Todos")
        self.filter_year_debt_var = tk.StringVar(value="Todos")

        
        self.setup_ui()
        self.refresh_users_list()
        
    def on_close(self):
        """Maneja el cierre de la ventana"""
        self.root.destroy()
        UserManagementWindow._instance = None
        
    def open_new_user_dialog(self):
        """Abre el diálogo de nuevo usuario"""
        NewUserDialog(self.root, self.refresh_users_list)

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="Gestión de Usuarios",
            font=('Arial', 16, 'bold'),
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 10))
        
        # Frame superior: Búsqueda y Acciones
        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Acciones
        actions_frame = tk.LabelFrame(top_frame, text="Acciones", font=('Arial', 10, 'bold'))
        actions_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        tk.Button(actions_frame, text="Agregar Nuevo Usuario", command=self.open_new_user_dialog, bg='#27ae60', fg='white', font=('Arial', 12, 'bold'), height=2, width=20).pack(side=tk.LEFT, padx=10, pady=5)
        
        # Botón Excel
        from .excel_manager import ExcelManager
        tk.Button(actions_frame, text="Abrir Excel Base Datos", command=ExcelManager.abrir_excel_db, bg='#217346', fg='white', font=('Arial', 12, 'bold'), height=2, width=20).pack(side=tk.LEFT, padx=10, pady=5)
        
        tk.Button(actions_frame, text="Volver al Menú", command=self.on_close, bg='#7f8c8d', fg='white', font=('Arial', 12, 'bold'), height=2, width=15).pack(side=tk.LEFT, padx=10, pady=5)

        # Búsqueda y Filtros
        search_frame = tk.LabelFrame(top_frame, text="Buscar y Filtrar", font=('Arial', 10, 'bold'))
        search_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Row 1: Search
        row1 = tk.Frame(search_frame)
        row1.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(row1, text="No. Usuario:").pack(side=tk.LEFT, padx=5)
        tk.Entry(row1, textvariable=self.search_id_var, width=10).pack(side=tk.LEFT, padx=5)
        
        tk.Label(row1, text="Nombre:").pack(side=tk.LEFT, padx=5)
        tk.Entry(row1, textvariable=self.search_name_var, width=20).pack(side=tk.LEFT, padx=5)
        
        tk.Button(row1, text="Buscar", command=self.refresh_users_list, bg='#3498db', fg='white').pack(side=tk.LEFT, padx=10)
        tk.Button(row1, text="Limpiar", command=self.clear_search, bg='#95a5a6', fg='white').pack(side=tk.LEFT, padx=5)
        
        # Row 2: Filters
        row2 = tk.Frame(search_frame)
        row2.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(row2, text="Filtrar por Sesión:").pack(side=tk.LEFT, padx=5)
        ttk.Combobox(row2, textvariable=self.filter_sesion_var, values=["Todas", "1", "2", "3"], state="readonly", width=8).pack(side=tk.LEFT, padx=5)
        
        tk.Label(row2, text="Estado:").pack(side=tk.LEFT, padx=5)
        ttk.Combobox(row2, textvariable=self.filter_status_var, values=["Todos", "Activo", "Cancelado", "Baja", "Suspendida"], state="readonly", width=12).pack(side=tk.LEFT, padx=5)
        
        tk.Label(row2, text="Deuda Año:").pack(side=tk.LEFT, padx=5)
        current_year = 2024 # O datetime.now().year
        years = ["Todos"] + [str(y) for y in range(current_year, 2020, -1)]
        ttk.Combobox(row2, textvariable=self.filter_year_debt_var, values=years, state="readonly", width=8).pack(side=tk.LEFT, padx=5)

        
        tk.Button(row2, text="Aplicar Filtros", command=self.refresh_users_list, bg='#2ecc71', fg='white').pack(side=tk.LEFT, padx=10)
        
        # Frame central: Lista de usuarios y Detalles
        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista de usuarios (Treeview)
        list_frame = tk.Frame(content_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        columns = ('id', 'numero_usuario', 'nombre', 'sesion', 'tomas', 'estado')
        self.users_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        self.users_tree.heading('id', text='ID')
        self.users_tree.heading('numero_usuario', text='No. Usuario')
        self.users_tree.heading('nombre', text='Nombre')
        self.users_tree.heading('sesion', text='Sesión')
        self.users_tree.heading('tomas', text='Tomas')
        self.users_tree.heading('estado', text='Estado')
        
        self.users_tree.column('id', width=50, anchor='center')
        self.users_tree.column('numero_usuario', width=80, anchor='center')
        self.users_tree.column('nombre', width=200)
        self.users_tree.column('sesion', width=50, anchor='center')
        self.users_tree.column('tomas', width=50, anchor='center')
        self.users_tree.column('estado', width=80, anchor='center')
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.users_tree.bind('<<TreeviewSelect>>', self.on_user_select)
        
        # Detalles del usuario
        details_frame = tk.LabelFrame(content_frame, text="Detalles del Usuario", font=('Arial', 10, 'bold'), width=350)
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        details_frame.pack_propagate(False)
        
        self.create_details_form(details_frame)
    
    def create_details_form(self, parent):
        """Crea el formulario de detalles del usuario"""
        form_frame = tk.Frame(parent)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Campos
        fields = [
            ("ID (Sistema):", self.user_id_var, True), # Readonly
            ("No. Usuario:", self.user_number_var, False), # Editable
            ("Nombre:", self.user_name_var, False),
            ("Dirección:", self.user_address_var, False),
            ("Teléfono:", self.user_phone_var, False),
            ("Email:", self.user_email_var, False),
            ("Vacas:", self.user_vacas_var, False),
            ("Inquilinos:", self.user_inquilinos_var, False),
            ("Tomas:", self.user_tomas_var, False),
            ("Hidrantes:", self.user_hidrantes_var, False),
            ("Seccionar ($):", self.user_seccionar_var, False),
            ("T. Pozo ($):", self.user_t_pozo_var, False),
            ("Conagua ($):", self.user_conagua_var, False),
            ("Drenaje ($):", self.user_drenaje_var, False),
            ("Fecha Alta:", self.user_fecha_alta_var, True),
            ("Fecha Baja:", self.user_fecha_baja_var, True)
        ]
        
        for i, (label, var, readonly) in enumerate(fields):
            tk.Label(form_frame, text=label, anchor='w').grid(row=i, column=0, sticky='w', pady=5)
            entry = tk.Entry(form_frame, textvariable=var)
            if readonly:
                entry.config(state='readonly')
            entry.grid(row=i, column=1, sticky='ew', pady=5)
        
        # Sesión (Combobox)
        tk.Label(form_frame, text="Sesión:", anchor='w').grid(row=len(fields), column=0, sticky='w', pady=5)
        self.session_combo = ttk.Combobox(form_frame, textvariable=self.user_session_var, values=["1", "2", "3"], state="readonly")
        self.session_combo.grid(row=len(fields), column=1, sticky='ew', pady=5)
        
        # Estado (Combobox)
        tk.Label(form_frame, text="Estado:", anchor='w').grid(row=len(fields)+1, column=0, sticky='w', pady=5)
        self.status_combo = ttk.Combobox(form_frame, textvariable=self.user_status_var, values=["Activo", "Cancelado", "Baja", "Suspendida"], state="readonly")
        self.status_combo.grid(row=len(fields)+1, column=1, sticky='ew', pady=5)
        
        form_frame.columnconfigure(1, weight=1)
        
        # Botones de acción
        btn_frame = tk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.save_btn = tk.Button(btn_frame, text="Guardar Cambios", command=self.save_user_changes, bg='#2980b9', fg='white', state='disabled')
        self.save_btn.pack(fill=tk.X, pady=5)
        
        self.history_btn = tk.Button(btn_frame, text="Ver Historial de Pagos", command=self.show_payment_history, bg='#8e44ad', fg='white', state='disabled')
        self.history_btn.pack(fill=tk.X, pady=5)

        self.obs_btn = tk.Button(btn_frame, text="Ver Observaciones", command=self.show_observations, bg='#f39c12', fg='white', state='disabled')
        self.obs_btn.pack(fill=tk.X, pady=5)

        self.delete_btn = tk.Button(btn_frame, text="Eliminar Usuario", command=self.delete_user, bg='#c0392b', fg='white', state='disabled')
        self.delete_btn.pack(fill=tk.X, pady=5)

    def refresh_users_list(self):
        """Actualiza la lista de usuarios"""
        # Limpiar lista
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        db = get_db_manager()
        
        # Filtros Búsqueda
        user_id = self.search_id_var.get().strip()
        name = self.search_name_var.get().strip()
        
        users = []
        if user_id:
            try:
                # Búsqueda por número de usuario (alfanumérico) - Solicitud de usuario: YA NO BUSCAR POR ID
                users = db.buscar_usuarios_por_numero(user_id)
            except ValueError:
                pass
        elif name:
            users = db.buscar_usuarios_por_nombre(name)
        else:
            users = db.obtener_todos_usuarios()
            
        # Aplicar Filtros Adicionales
        filter_sesion = self.filter_sesion_var.get()
        filter_status = self.filter_status_var.get()
        
        filtered_users = []
        for u in users:
            # Filtro Sesión
            if filter_sesion != "Todas":
                if str(u['sesion']) != filter_sesion:
                    continue
            
            # Filtro Estado
            if filter_status != "Todos":
                if u.get('estado') != filter_status:
                    continue
            
            filtered_users.append(u)
        
        # Filtro Deuda Año (requiere consulta extra o filtrado complejo)
        filter_year = self.filter_year_debt_var.get()
        if filter_year != "Todos" and filter_year.isdigit():
            # Obtener lista de deudores para ese año
            anio = int(filter_year)
            # Optimización: Podríamos hacerlo en la query inicial, pero aquí filtramos la lista ya obtenida
            # Como `obtener_usuarios_deudores` devuelve info completa, podemos cruzar IDs
            deudores = db.obtener_usuarios_deudores(anio)
            deudores_ids = {d['id'] for d in deudores}
            
            # Intersección
            filtered_users = [u for u in filtered_users if u['id'] in deudores_ids]

        # Ordenar por numero_usuario usando orden natural (e.g. 31, 31A, 32)
        import re
        def get_sort_key(u):
            val = str(u.get('numero_usuario', '') or '').strip()
            # Extraer parte numérica y parte alfabética
            # "31A" -> (31, "A")
            # "31"  -> (31, "")
            # "1.0" -> (1, "")
            # "*"   -> (float('inf'), "*")  paramos al final
            
            if not val or val == '*':
                return (float('inf'), val)
                
            match = re.match(r"([0-9.]+)([a-zA-Z]*)", val)
            if match:
                num_part = match.group(1)
                alpha_part = match.group(2)
                try:
                    num_val = float(num_part)
                except ValueError:
                    num_val = float('inf')
                return (num_val, alpha_part)
            else:
                # Si no empieza con numero, va al final
                return (float('inf'), val)

        filtered_users.sort(key=get_sort_key)

        # Llenar Treeview
        for u in filtered_users:
            numero_usuario = u.get('numero_usuario') or str(u['id'])
            self.users_tree.insert('', 'end', values=(u['id'], numero_usuario, u['nombre'], u['sesion'], u.get('tomas', 1), u['estado']))
    
    def clear_search(self):
        """Limpia los campos de búsqueda"""
        self.search_id_var.set("")
        self.search_name_var.set("")
        self.filter_sesion_var.set("Todas")
        self.filter_status_var.set("Todos")
        self.filter_year_debt_var.set("Todos")
        self.refresh_users_list()

    def on_user_select(self, event):
        """Maneja la selección de un usuario"""
        selection = self.users_tree.selection()
        if not selection:
            return
        
        item = self.users_tree.item(selection[0])
        user_id = item['values'][0]
        
        self.load_user_details(user_id)
        
        # Habilitar botones
        self.save_btn.config(state='normal')
        self.history_btn.config(state='normal')
        self.obs_btn.config(state='normal')
        self.delete_btn.config(state='normal')
    
    def load_user_details(self, user_id):
        """Carga los detalles del usuario"""
        db = get_db_manager()
        user = db.buscar_usuario_por_id(user_id)
        
        if user:
            self.user_id_var.set(str(user['id']))
            self.user_name_var.set(user['nombre'])
            self.user_address_var.set(user['direccion'] or "")
            self.user_phone_var.set(user['telefono'] or "")
            self.user_email_var.set(user['email'] or "")
            self.user_session_var.set(str(user['sesion']))
            self.user_status_var.set(user['estado'])
            self.user_vacas_var.set(user.get('vacas', 0))
            self.user_inquilinos_var.set(user.get('inquilinos', 0))
            self.user_tomas_var.set(user.get('tomas', 1))
            self.user_hidrantes_var.set(user.get('hidrantes', 0))
            self.user_number_var.set(user.get('numero_usuario') or str(user['id']))
            self.user_fecha_alta_var.set(user.get('fecha_alta') or user.get('fecha_registro') or "")
            self.user_fecha_baja_var.set(user.get('fecha_baja') or "")
            self.user_seccionar_var.set(user.get('seccionar', 0))
            self.user_t_pozo_var.set(user.get('t_pozo', 0))
            self.user_conagua_var.set(user.get('conagua', 0))
            self.user_drenaje_var.set(user.get('drenaje', 0))


    def save_user_changes(self):
        """Guarda los cambios del usuario"""
        user_id = self.user_id_var.get()
        if not user_id:
            return
        
        try:
            db = get_db_manager()
            
            datos = {
                'nombre': self.user_name_var.get().strip(),
                'direccion': self.user_address_var.get().strip(),
                'telefono': self.user_phone_var.get().strip(),
                'email': self.user_email_var.get().strip(),
                'sesion': int(self.user_session_var.get()),
                'estado': self.user_status_var.get(),
                'vacas': self.user_vacas_var.get(),
                'inquilinos': self.user_inquilinos_var.get(),
                'tomas': self.user_tomas_var.get(),
                'hidrantes': self.user_hidrantes_var.get(),
                'numero_usuario': self.user_number_var.get().strip(),
                'seccionar': self.user_seccionar_var.get(),
                't_pozo': self.user_t_pozo_var.get(),
                'conagua': self.user_conagua_var.get(),
                'drenaje': self.user_drenaje_var.get()
            }
            
            if not datos['nombre']:
                messagebox.showwarning("Error", "El nombre es obligatorio")
                return

            if not datos['direccion']:
                messagebox.showwarning("Error", "La dirección es obligatoria")
            
            # Verificar si cambió el estado para actualizar fechas
            current_user = db.buscar_usuario_por_id(int(user_id))
            if current_user and current_user['estado'] != datos['estado']:
                # Usar el método específico que maneja fechas
                db.cambiar_estado_usuario(int(user_id), datos['estado'])
                # Eliminar estado de los datos a actualizar genéricamente para no sobrescribir
                del datos['estado']
            
            if db.actualizar_usuario(int(user_id), **datos):
                # Sincronizar con Excel
                try:
                    from .excel_manager import ExcelManager
                    ExcelManager.actualizar_usuario_en_db_excel(datos)
                except Exception as ex:
                    print(f"Error al sincronizar con Excel: {ex}")
                
                messagebox.showinfo("Éxito", "Usuario actualizado correctamente")
                self.refresh_users_list()
                # Recargar detalles para ver fechas actualizadas si las hubo
                self.load_user_details(int(user_id))
            else:
                messagebox.showerror("Error", "No se pudo actualizar el usuario")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")

    def show_payment_history(self):
        """Muestra el historial de pagos del usuario seleccionado"""
        user_id = self.user_id_var.get()
        if not user_id:
            return
            
        try:
            PaymentHistoryWindow(self.root, int(user_id))
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir historial: {str(e)}")
        except ImportError:
            # Fallback si no existe el módulo aún
            messagebox.showinfo("Historial", f"Historial de pagos para usuario {user_id}\n(Módulo en desarrollo)")
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir historial: {str(e)}")

    def delete_user(self):
        """Elimina el usuario seleccionado"""
        user_id = self.user_id_var.get()
        if not user_id:
            return
            
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este usuario?\nEsta acción no se puede deshacer."):
            try:
                db = get_db_manager()
                if db.eliminar_usuario(int(user_id)):
                    messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
                    self.clear_search() # Limpiar selección
                else:
                    messagebox.showerror("Error", "No se puede eliminar el usuario. \nPosiblemente tiene pagos registrados o ocurrió un error.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar: {str(e)}")

    def show_observations(self):
        """Muestra y edita las observaciones del usuario"""
        user_id = self.user_id_var.get()
        if not user_id:
            return
            
        try:
            db = get_db_manager()
            user = db.buscar_usuario_por_id(int(user_id))
            if not user:
                return
                
            obs_window = tk.Toplevel(self.root)
            obs_window.title(f"Observaciones - {user['nombre']}")
            obs_window.geometry("500x400")
            
            tk.Label(obs_window, text="Observaciones:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=5)
            
            text_area = tk.Text(obs_window, font=('Arial', 10), height=15)
            text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # Cargar observaciones existentes
            if user.get('observaciones'):
                text_area.insert('1.0', user['observaciones'])
                
            def save_obs():
                new_obs = text_area.get('1.0', 'end-1c')
                try:
                    if db.actualizar_usuario(int(user_id), observaciones=new_obs):
                        messagebox.showinfo("Éxito", "Observaciones guardadas correctamente")
                        self.load_user_details(int(user_id)) # Recargar en ventana principal
                        obs_window.destroy()
                    else:
                        messagebox.showerror("Error", "No se pudieron guardar las observaciones")
                except Exception as e:
                    messagebox.showerror("Error", f"Error al guardar: {e}")
            
            btn_frame = tk.Frame(obs_window)
            btn_frame.pack(fill=tk.X, padx=10, pady=10)
            
            tk.Button(btn_frame, text="Guardar", command=save_obs, bg='#27ae60', fg='white').pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="Cerrar", command=obs_window.destroy, bg='#7f8c8d', fg='white').pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir observaciones: {e}")


class NewUserDialog:
    def __init__(self, parent, callback):
        self.callback = callback
        self.top = tk.Toplevel(parent)
        self.top.title("Nuevo Usuario")
        self.top.geometry("550x700")
        
        self.name_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.session_var = tk.StringVar(value="1")
        self.vacas_var = tk.IntVar(value=0)
        self.inquilinos_var = tk.IntVar(value=0)
        self.tomas_var = tk.IntVar(value=1)
        self.hidrantes_var = tk.IntVar(value=0)
        self.seccionar_var = tk.DoubleVar(value=0)
        self.t_pozo_var = tk.DoubleVar(value=0)
        self.conagua_var = tk.DoubleVar(value=0)
        self.drenaje_var = tk.DoubleVar(value=0)
        self.numero_usuario_var = tk.StringVar()
        
        # Smart ID vars
        self.parent_user_var = tk.StringVar()
        self.generated_id_label = tk.StringVar(value="ID Sugerido: -")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal con Canvas y Scrollbar para asegurar que todo quepa
        main_canvas = tk.Canvas(self.top)
        scrollbar = ttk.Scrollbar(self.top, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, padx=20, pady=20)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=500) # Ajustar ancho
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        frame = scrollable_frame
        
        # Fila 1: Nombre
        tk.Label(frame, text="Nombre (*):").grid(row=0, column=0, sticky='w', pady=(0, 5))
        tk.Entry(frame, textvariable=self.name_var, width=50).grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        # Fila 2: No. Usuario, Sesión, y Usuario Padre
        
        # Panel de Usuario Padre (Smart ID)
        parent_frame = tk.LabelFrame(frame, text="Generar ID Automático (Usuario Padre)")
        parent_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        tk.Label(parent_frame, text="Buscar Padre (Nombre/ID):").pack(side=tk.LEFT, padx=5)
        self.parent_search_entry = tk.Entry(parent_frame, width=20)
        self.parent_search_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(parent_frame, text="Buscar", command=self.search_parent, bg='#3498db', fg='white').pack(side=tk.LEFT, padx=5)
        
        self.parent_combo = ttk.Combobox(parent_frame, textvariable=self.parent_user_var, state="readonly", width=30)
        self.parent_combo.pack(side=tk.LEFT, padx=5)
        self.parent_combo.bind("<<ComboboxSelected>>", self.on_parent_select)
        
        tk.Label(parent_frame, textvariable=self.generated_id_label, font=('Arial', 10, 'bold'), fg='#27ae60').pack(side=tk.LEFT, padx=10)

        # Campos Manuales
        row_manual = tk.Frame(frame)
        row_manual.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        tk.Label(row_manual, text="No. Usuario (Manual/Auto):").pack(side=tk.LEFT)
        tk.Entry(row_manual, textvariable=self.numero_usuario_var, width=15).pack(side=tk.LEFT, padx=(5, 20))
        
        tk.Label(row_manual, text="Sesión (*):").pack(side=tk.LEFT)
        ttk.Combobox(row_manual, textvariable=self.session_var, values=["1", "2", "3"], state="readonly", width=5).pack(side=tk.LEFT, padx=5)

        # Ajustar filas siguientes (offset)
        # Fila 3 original era direccion (row 4)
        tk.Label(frame, text="Dirección (*):").grid(row=4, column=0, sticky='w', pady=(0, 5))

        tk.Entry(frame, textvariable=self.address_var).grid(row=5, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        # Fila 4: Teléfono y Email
        tk.Label(frame, text="Teléfono:").grid(row=6, column=0, sticky='w', pady=(0, 5))
        tk.Entry(frame, textvariable=self.phone_var).grid(row=7, column=0, sticky='ew', padx=(0, 10), pady=(0, 10))
        
        tk.Label(frame, text="Email:").grid(row=6, column=1, sticky='w', pady=(0, 5))
        tk.Entry(frame, textvariable=self.email_var).grid(row=7, column=1, sticky='ew', pady=(0, 10))
        
        # Fila 5: Configuración (Vacas, Inquilinos)
        tk.Label(frame, text="Vacas:").grid(row=8, column=0, sticky='w', pady=(0, 5))
        tk.Entry(frame, textvariable=self.vacas_var).grid(row=9, column=0, sticky='ew', padx=(0, 10), pady=(0, 10))
        
        tk.Label(frame, text="Inquilinos:").grid(row=8, column=1, sticky='w', pady=(0, 5))
        tk.Entry(frame, textvariable=self.inquilinos_var).grid(row=9, column=1, sticky='ew', pady=(0, 10))
        
        # Fila 6: Configuración (Tomas, Hidrantes)
        tk.Label(frame, text="Tomas:").grid(row=10, column=0, sticky='w', pady=(0, 5))
        tk.Entry(frame, textvariable=self.tomas_var).grid(row=11, column=0, sticky='ew', padx=(0, 10), pady=(0, 10))
        
        tk.Label(frame, text="Hidrantes:").grid(row=10, column=1, sticky='w', pady=(0, 5))
        tk.Entry(frame, textvariable=self.hidrantes_var).grid(row=11, column=1, sticky='ew', pady=(0, 20))
        
        # Fila 7: Nuevos cargos
        tk.Label(frame, text="Seccionar ($):").grid(row=12, column=0, sticky='w', pady=(0, 5))
        tk.Entry(frame, textvariable=self.seccionar_var).grid(row=13, column=0, sticky='ew', padx=(0, 10), pady=(0, 10))
        
        tk.Label(frame, text="T. Pozo ($):").grid(row=12, column=1, sticky='w', pady=(0, 5))
        tk.Entry(frame, textvariable=self.t_pozo_var).grid(row=13, column=1, sticky='ew', pady=(0, 10))

        tk.Label(frame, text="Conagua ($):").grid(row=14, column=0, sticky='w', pady=(0, 5))
        tk.Entry(frame, textvariable=self.conagua_var).grid(row=15, column=0, sticky='ew', padx=(0, 10), pady=(0, 10))
        
        tk.Label(frame, text="Drenaje ($):").grid(row=14, column=1, sticky='w', pady=(0, 5))
        tk.Entry(frame, textvariable=self.drenaje_var).grid(row=15, column=1, sticky='ew', pady=(0, 10))
        
        # Botones
        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=16, column=0, columnspan=2, sticky='ew', pady=20)

        
        tk.Button(btn_frame, text="Crear Usuario", command=self.create_user, bg='#27ae60', fg='white', width=20).pack(side=tk.LEFT, padx=10, expand=True)
        tk.Button(btn_frame, text="Cancelar", command=self.top.destroy, bg='#e74c3c', fg='white', width=20).pack(side=tk.RIGHT, padx=10, expand=True)
        
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

    def search_parent(self):
        """Busca usuarios padre potenciales"""
        term = self.parent_search_entry.get().strip()
        if not term:
            return
            
        db = get_db_manager()
        users = db.buscar_usuarios_por_nombre(term)
        
        # También intentar por ID
        if term.isdigit():
             u = db.buscar_usuario_por_id(int(term))
             if u: users.append(u)
        
        # Formatear para combobox: "ID - Nombre (No.Usuario)"
        self.parent_map = {f"{u['id']} - {u['nombre']} ({u.get('numero_usuario', '-')})": u for u in users}
        self.parent_combo['values'] = list(self.parent_map.keys())
        if self.parent_map:
            self.parent_combo.current(0)
            self.on_parent_select(None)
        else:
            messagebox.showinfo("Búsqueda", "No se encontraron usuarios")

    def on_parent_select(self, event):
        """Genera el ID basado en el padre seleccionado"""
        selected = self.parent_user_var.get()
        if not selected or not hasattr(self, 'parent_map'):
            return
            
        parent = self.parent_map[selected]
        # Lógica de generación:
        # Si padre es "3", hijos son "3A", "3B", etc.
        # Si padre es "3A", hijos podrían ser "3A-1" o seguir la secuencia del grupo "3".
        # Asumiremos la logica simple descrita: ID Padre + Letra
        
        base_id = parent.get('numero_usuario') or str(parent['id'])
        
        # Limpiar base_id de letras existentes al final si queremos anidar, 
        # pero para este caso simple, intentamos appendear letra.
        
        db = get_db_manager()
        # Buscar hermanos existentes (que empiecen con el base_id)
        # Esto es un poco complejo sin una query especifica, pero podemos iterar letras
        
        import string
        letters = string.ascii_uppercase # A-Z
        
        candidate = ""
        for char in letters:
            candidate = f"{base_id}{char}"
            # Verificar si existe
            exists = db.buscar_usuarios_por_numero(candidate)
            if not exists:
                break
        
        self.numero_usuario_var.set(candidate)
        self.generated_id_label.set(f"ID Sugerido: {candidate}")
        
        # Auto-fill address usually logic matches parent address? Optional improvement.
        if parent.get('direccion'):
            self.address_var.set(parent['direccion'])

    
    def create_user(self):
        nombre = self.name_var.get().strip()
        sesion = self.session_var.get()
        
        if not nombre:
            messagebox.showwarning("Error", "El nombre es obligatorio")
            return

        if not self.address_var.get().strip():
            messagebox.showwarning("Error", "La dirección es obligatoria")
            return
        
        try:
            db = get_db_manager()
            if db.crear_usuario(
                nombre=nombre,
                direccion=self.address_var.get().strip(),
                telefono=self.phone_var.get().strip(),
                email=self.email_var.get().strip(),
                sesion=int(sesion),
                vacas=self.vacas_var.get(),
                inquilinos=self.inquilinos_var.get(),
                tomas=self.tomas_var.get(),
                hidrantes=self.hidrantes_var.get(),
                seccionar=self.seccionar_var.get(),
                t_pozo=self.t_pozo_var.get(),
                conagua=self.conagua_var.get(),
                drenaje=self.drenaje_var.get(),
                numero_usuario=self.numero_usuario_var.get().strip() or None
            ):
                # Sincronizar con Excel
                try:
                    from .excel_manager import ExcelManager
                    datos_excel = {
                        'nombre': nombre,
                        'direccion': self.address_var.get().strip(),
                        'sesion': int(sesion),
                        'vacas': self.vacas_var.get(),
                        'inquilinos': self.inquilinos_var.get(),
                        'tomas': self.tomas_var.get(),
                        'hidrantes': self.hidrantes_var.get(),
                        'seccionar': self.seccionar_var.get(),
                        't_pozo': self.t_pozo_var.get(),
                        'conagua': self.conagua_var.get(),
                        'drenaje': self.drenaje_var.get(),
                        'numero_usuario': self.numero_usuario_var.get().strip()
                    }
                    ExcelManager.actualizar_usuario_en_db_excel(datos_excel)
                except Exception as ex:
                    print(f"Error al sincronizar con Excel: {ex}")

                messagebox.showinfo("Éxito", "Usuario creado correctamente")
                self.callback()
                self.top.destroy()
            else:
                messagebox.showerror("Error", "No se pudo crear el usuario")
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear usuario: {str(e)}")