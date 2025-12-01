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
from .receipt_generator import ReceiptGenerator

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
        self.user_fecha_alta_var = tk.StringVar()
        self.user_fecha_baja_var = tk.StringVar()
        
        # Filtros
        self.filter_sesion_var = tk.StringVar(value="Todas")
        self.filter_status_var = tk.StringVar(value="Todos")
        
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
        
        # Búsqueda y Filtros
        search_frame = tk.LabelFrame(top_frame, text="Buscar y Filtrar", font=('Arial', 10, 'bold'))
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Row 1: Search
        row1 = tk.Frame(search_frame)
        row1.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(row1, text="ID:").pack(side=tk.LEFT, padx=5)
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
        
        tk.Button(row2, text="Aplicar Filtros", command=self.refresh_users_list, bg='#2ecc71', fg='white').pack(side=tk.LEFT, padx=10)
        
        # Acciones
        actions_frame = tk.LabelFrame(top_frame, text="Acciones", font=('Arial', 10, 'bold'))
        actions_frame.pack(side=tk.RIGHT, fill=tk.X, padx=(5, 0))
        
        tk.Button(actions_frame, text="Agregar Nuevo Usuario", command=self.open_new_user_dialog, bg='#27ae60', fg='white', font=('Arial', 12, 'bold'), height=2, width=20).pack(side=tk.LEFT, padx=10, pady=5)
        tk.Button(actions_frame, text="Volver al Menú", command=self.on_close, bg='#7f8c8d', fg='white', font=('Arial', 12, 'bold'), height=2, width=15).pack(side=tk.LEFT, padx=10, pady=5)
        
        # Frame central: Lista de usuarios y Detalles
        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista de usuarios (Treeview)
        list_frame = tk.Frame(content_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        columns = ('id', 'nombre', 'sesion', 'tomas', 'estado')
        self.users_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        self.users_tree.heading('id', text='ID')
        self.users_tree.heading('nombre', text='Nombre')
        self.users_tree.heading('sesion', text='Sesión')
        self.users_tree.heading('tomas', text='Tomas')
        self.users_tree.heading('estado', text='Estado')
        
        self.users_tree.column('id', width=50, anchor='center')
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
            ("ID:", self.user_id_var, True), # Readonly
            ("Nombre:", self.user_name_var, False),
            ("Dirección:", self.user_address_var, False),
            ("Teléfono:", self.user_phone_var, False),
            ("Email:", self.user_email_var, False),
            ("Vacas:", self.user_vacas_var, False),
            ("Inquilinos:", self.user_inquilinos_var, False),
            ("Tomas:", self.user_tomas_var, False),
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

        self.delete_btn = tk.Button(btn_frame, text="Eliminar Usuario", command=self.delete_user, bg='#c0392b', fg='white', state='disabled')
        self.delete_btn.pack(fill=tk.X, pady=5)

        self.print_debt_btn = tk.Button(btn_frame, text="Imprimir Estado de Cuenta", command=self.print_debt_summary, bg='#d35400', fg='white', state='disabled')
        self.print_debt_btn.pack(fill=tk.X, pady=5)

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
                u = db.buscar_usuario_por_id(int(user_id))
                if u: users = [u]
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
        
        for u in filtered_users:
            self.users_tree.insert('', 'end', values=(u['id'], u['nombre'], u['sesion'], u.get('tomas', 1), u['estado']))
    
    def clear_search(self):
        """Limpia los campos de búsqueda"""
        self.search_id_var.set("")
        self.search_name_var.set("")
        self.filter_sesion_var.set("Todas")
        self.filter_status_var.set("Todos")
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
        self.delete_btn.config(state='normal')
        self.print_debt_btn.config(state='normal')
    
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
            self.user_fecha_alta_var.set(user.get('fecha_alta') or user.get('fecha_registro') or "")
            self.user_fecha_baja_var.set(user.get('fecha_baja') or "")

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
                'tomas': self.user_tomas_var.get()
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
            # Importar aquí para evitar referencias circulares si las hubiera
            from .payment_history import PaymentHistoryWindow
            PaymentHistoryWindow(self.root, user_id)
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
                    messagebox.showerror("Error", "No se pudo eliminar el usuario")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar: {str(e)}")

    def print_debt_summary(self):
        """Imprime el estado de cuenta del usuario"""
        user_id = self.user_id_var.get()
        if not user_id:
            return
            
        try:
            # Generar reporte de adeudo
            generator = ReceiptGenerator()
            filename = generator.generate_debt_summary(int(user_id))
            
            if filename and os.path.exists(filename):
                os.startfile(filename)
            else:
                messagebox.showwarning("Aviso", "No se pudo generar el reporte")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")


class NewUserDialog:
    def __init__(self, parent, callback):
        self.callback = callback
        self.top = tk.Toplevel(parent)
        self.top.title("Nuevo Usuario")
        self.top.geometry("400x600")
        
        self.name_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.session_var = tk.StringVar(value="1")
        self.vacas_var = tk.IntVar(value=0)
        self.inquilinos_var = tk.IntVar(value=0)
        self.tomas_var = tk.IntVar(value=1)
        
        self.setup_ui()
        
    def setup_ui(self):
        frame = tk.Frame(self.top, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Nombre (*):").pack(anchor='w', pady=(0, 5))
        tk.Entry(frame, textvariable=self.name_var).pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame, text="Dirección (*):").pack(anchor='w', pady=(0, 5))
        tk.Entry(frame, textvariable=self.address_var).pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame, text="Teléfono:").pack(anchor='w', pady=(0, 5))
        tk.Entry(frame, textvariable=self.phone_var).pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame, text="Email:").pack(anchor='w', pady=(0, 5))
        tk.Entry(frame, textvariable=self.email_var).pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame, text="Sesión (*):").pack(anchor='w', pady=(0, 5))
        ttk.Combobox(frame, textvariable=self.session_var, values=["1", "2", "3"], state="readonly").pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame, text="Vacas:").pack(anchor='w', pady=(0, 5))
        tk.Entry(frame, textvariable=self.vacas_var).pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame, text="Inquilinos:").pack(anchor='w', pady=(0, 5))
        tk.Entry(frame, textvariable=self.inquilinos_var).pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame, text="Tomas:").pack(anchor='w', pady=(0, 5))
        tk.Entry(frame, textvariable=self.tomas_var).pack(fill=tk.X, pady=(0, 20))
        
        tk.Button(frame, text="Crear Usuario", command=self.create_user, bg='#27ae60', fg='white').pack(fill=tk.X, pady=(0, 5))
        tk.Button(frame, text="Cancelar", command=self.top.destroy, bg='#e74c3c', fg='white').pack(fill=tk.X)
    
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
                tomas=self.tomas_var.get()
            ):
                messagebox.showinfo("Éxito", "Usuario creado correctamente")
                self.callback()
                self.top.destroy()
            else:
                messagebox.showerror("Error", "No se pudo crear el usuario")
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear usuario: {str(e)}")