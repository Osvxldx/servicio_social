#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de gestión de usuarios para el sistema de agua potable
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import get_db_manager
import re
import os
from receipt_generator import ReceiptGenerator


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
                    self.root.focus_force()
                    return
            except (AttributeError, tk.TclError):
                # Si la ventana no existe o hubo error, reinicializar
                self.initialized = False
                UserManagementWindow._instance = None

        self.initialized = True
        
        # Crear ventana principal o usar la proporcionada
        if parent:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Tk()
        
        self.root.title("Gestión de Usuarios")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Configurar evento de cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Variables
        self.search_id_var = tk.StringVar()
        self.search_name_var = tk.StringVar()
        self.user_id_var = tk.StringVar()
        self.user_name_var = tk.StringVar()
        self.user_address_var = tk.StringVar()
        self.user_phone_var = tk.StringVar()
        self.user_email_var = tk.StringVar()
        self.user_status_var = tk.StringVar(value="Activo")
        self.user_session_var = tk.StringVar(value="1")
        
        # Configurar la interfaz
        self.setup_ui()
        
        # Cargar usuarios
        self.refresh_users_list()
    
    def on_close(self):
        """Maneja el cierre de la ventana"""
        UserManagementWindow._instance = None
        self.root.destroy()

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
        
        # Búsqueda
        search_frame = tk.LabelFrame(top_frame, text="Buscar", font=('Arial', 10, 'bold'))
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Label(search_frame, text="ID:").pack(side=tk.LEFT, padx=5)
        tk.Entry(search_frame, textvariable=self.search_id_var, width=10).pack(side=tk.LEFT, padx=5)
        
        tk.Label(search_frame, text="Nombre:").pack(side=tk.LEFT, padx=5)
        tk.Entry(search_frame, textvariable=self.search_name_var, width=20).pack(side=tk.LEFT, padx=5)
        
        tk.Button(search_frame, text="Buscar", command=self.refresh_users_list, bg='#3498db', fg='white').pack(side=tk.LEFT, padx=10)
        tk.Button(search_frame, text="Limpiar", command=self.clear_search, bg='#95a5a6', fg='white').pack(side=tk.LEFT, padx=5)
        
        # Acciones
        actions_frame = tk.LabelFrame(top_frame, text="Acciones", font=('Arial', 10, 'bold'))
        actions_frame.pack(side=tk.RIGHT, fill=tk.X, padx=(5, 0))
        
        tk.Button(actions_frame, text="Agregar Nuevo Usuario", command=self.open_new_user_dialog, bg='#27ae60', fg='white', font=('Arial', 12, 'bold'), height=2, width=20).pack(side=tk.LEFT, padx=10, pady=5)
        
        # Frame central: Lista de usuarios y Detalles
        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista de usuarios (Treeview)
        list_frame = tk.Frame(content_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        columns = ('id', 'nombre', 'sesion', 'estado')
        self.users_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        self.users_tree.heading('id', text='ID')
        self.users_tree.heading('nombre', text='Nombre')
        self.users_tree.heading('sesion', text='Sesión')
        self.users_tree.heading('estado', text='Estado')
        
        self.users_tree.column('id', width=50, anchor='center')
        self.users_tree.column('nombre', width=200)
        self.users_tree.column('sesion', width=50, anchor='center')
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
            ("Email:", self.user_email_var, False)
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
        self.status_combo = ttk.Combobox(form_frame, textvariable=self.user_status_var, values=["Activo", "Cancelado"], state="readonly")
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

    def refresh_users_list(self):
        """Actualiza la lista de usuarios"""
        # Limpiar lista
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        db = get_db_manager()
        
        # Filtros
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
        
        for u in users:
            self.users_tree.insert('', 'end', values=(u['id'], u['nombre'], u['sesion'], u['estado']))
    
    def clear_search(self):
        """Limpia los campos de búsqueda"""
        self.search_id_var.set("")
        self.search_name_var.set("")
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
                'estado': self.user_status_var.get()
            }
            
            if not datos['nombre']:
                messagebox.showwarning("Error", "El nombre es obligatorio")
                return
            
            if db.actualizar_usuario(int(user_id), **datos):
                messagebox.showinfo("Éxito", "Usuario actualizado correctamente")
                self.refresh_users_list()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el usuario")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")

    def show_payment_history(self):
        """Muestra el historial de pagos"""
        user_id = self.user_id_var.get()
        if not user_id:
            return
            
        PaymentHistoryWindow(self.root, int(user_id))

    def delete_user(self):
        """Elimina el usuario seleccionado"""
        user_id = self.user_id_var.get()
        if not user_id:
            return
            
        nombre = self.user_name_var.get()
        
        if not messagebox.askyesno("Confirmar Eliminación", 
                                 f"¿Está seguro que desea eliminar al usuario '{nombre}'?\n\nEsta acción no se puede deshacer."):
            return
            
        try:
            db = get_db_manager()
            if db.eliminar_usuario(int(user_id)):
                messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
                self.clear_search() # Refresca la lista y limpia campos
                self.save_btn.config(state='disabled')
                self.history_btn.config(state='disabled')
                self.delete_btn.config(state='disabled')
                
                # Limpiar campos de detalle
                self.user_id_var.set("")
                self.user_name_var.set("")
                self.user_address_var.set("")
                self.user_phone_var.set("")
                self.user_email_var.set("")
                self.user_session_var.set("1")
                self.user_status_var.set("Activo")
            else:
                messagebox.showerror("Error", "No se pudo eliminar el usuario.\nEs posible que tenga pagos registrados.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar: {str(e)}")

    def open_new_user_dialog(self):
        """Abre el diálogo para crear un nuevo usuario"""
        NewUserDialog(self.root, self.refresh_users_list)


class PaymentHistoryWindow:
    def __init__(self, parent, user_id):
        self.user_id = user_id
        self.top = tk.Toplevel(parent)
        self.top.title("Historial de Pagos")
        self.top.geometry("800x600")
        
        self.setup_ui()
        self.load_history()
        
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.top)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        self.title_label = tk.Label(
            main_frame,
            text="Historial de Pagos",
            font=('Arial', 14, 'bold'),
            fg='#2c3e50'
        )
        self.title_label.pack(pady=(0, 10))
        
        # Lista de pagos
        columns = ('id', 'fecha', 'total', 'detalles')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings')
        
        self.tree.heading('id', text='ID Pago')
        self.tree.heading('fecha', text='Fecha')
        self.tree.heading('total', text='Total')
        self.tree.heading('detalles', text='Detalles')
        
        self.tree.column('id', width=60, anchor='center')
        self.tree.column('fecha', width=150, anchor='center')
        self.tree.column('total', width=80, anchor='e')
        self.tree.column('detalles', width=400)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón de reimpresión
        btn_frame = tk.Frame(self.top)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(btn_frame, text="Reimprimir Recibo Seleccionado", command=self.reprint_receipt, bg='#f39c12', fg='white').pack()
        
    def load_history(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        db = get_db_manager()
        pagos = db.obtener_pagos_usuario(self.user_id)
        
        for pago in pagos:
            detalles_str = ", ".join([f"{d['concepto']} ({d['precio']})" for d in pago['detalles']])
            self.tree.insert('', 'end', values=(pago['id'], pago['fecha_pago'], f"${pago['total']:.2f}", detalles_str))
            
    def reprint_receipt(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Seleccione un pago para reimprimir")
            return
            
        item = self.tree.item(selection[0])
        pago_id = item['values'][0]
        
        try:
            generator = ReceiptGenerator()
            pdf_path = generator.generate_receipt(pago_id)
            
            if pdf_path and os.path.exists(pdf_path):
                os.startfile(pdf_path)
            else:
                messagebox.showerror("Error", "No se pudo generar el recibo")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar recibo: {str(e)}")


class NewUserDialog:
    def __init__(self, parent, callback):
        self.top = tk.Toplevel(parent)
        self.top.title("Nuevo Usuario")
        self.top.geometry("400x500")
        self.callback = callback
        
        self.name_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.session_var = tk.StringVar(value="1")
        
        self.setup_ui()
        
    def setup_ui(self):
        frame = tk.Frame(self.top, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Nombre (*):").pack(anchor='w', pady=(0, 5))
        tk.Entry(frame, textvariable=self.name_var).pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame, text="Dirección:").pack(anchor='w', pady=(0, 5))
        tk.Entry(frame, textvariable=self.address_var).pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame, text="Teléfono:").pack(anchor='w', pady=(0, 5))
        tk.Entry(frame, textvariable=self.phone_var).pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame, text="Email:").pack(anchor='w', pady=(0, 5))
        tk.Entry(frame, textvariable=self.email_var).pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame, text="Sesión (*):").pack(anchor='w', pady=(0, 5))
        ttk.Combobox(frame, textvariable=self.session_var, values=["1", "2", "3"], state="readonly").pack(fill=tk.X, pady=(0, 20))
        
        tk.Button(frame, text="Crear Usuario", command=self.create_user, bg='#27ae60', fg='white').pack(fill=tk.X)
    
    def create_user(self):
        nombre = self.name_var.get().strip()
        sesion = self.session_var.get()
        
        if not nombre:
            messagebox.showwarning("Error", "El nombre es obligatorio")
            return
        
        try:
            db = get_db_manager()
            if db.crear_usuario(
                nombre=nombre,
                direccion=self.address_var.get().strip(),
                telefono=self.phone_var.get().strip(),
                email=self.email_var.get().strip(),
                sesion=int(sesion)
            ):
                messagebox.showinfo("Éxito", "Usuario creado correctamente")
                self.callback()
                self.top.destroy()
            else:
                messagebox.showerror("Error", "No se pudo crear el usuario")
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear usuario: {str(e)}")