#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de registro de pagos para el sistema de agua potable
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import get_db_manager
from datetime import datetime
from receipt_generator import ReceiptGenerator
import os

class PaymentRegistrationWindow:
    _instance = None

    def __new__(cls, parent=None):
        if cls._instance is None:
            cls._instance = super(PaymentRegistrationWindow, cls).__new__(cls)
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
                self.initialized = False
                PaymentRegistrationWindow._instance = None
                self.__init__(parent)
            return

        self.initialized = True
        
        # Crear ventana principal o usar la proporcionada
        if parent:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Tk()
        
        self.root.title("Registro de Pagos")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        self.root.state('zoomed') if hasattr(self.root, 'state') else None
        
        # Configurar evento de cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Variables
        self.current_user = None
        self.cart = [] # Lista de diccionarios {'concepto', 'precio', 'mes', 'anio', 'tipo'}
        self.total_amount = 0.0
        
        # Configurar la interfaz
        self.setup_ui()
    
    def on_close(self):
        """Maneja el cierre de la ventana"""
        PaymentRegistrationWindow._instance = None
        self.root.destroy()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="Registro de Pagos",
            font=('Arial', 16, 'bold'),
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 10))
        
        # Frame superior: Búsqueda de usuario
        search_frame = tk.LabelFrame(main_frame, text="Buscar Usuario", font=('Arial', 12, 'bold'))
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_search_panel(search_frame)
        
        # Frame central: Información del usuario y selección de pagos
        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Columna izquierda: Info usuario y meses
        left_col = tk.Frame(content_frame)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Info Usuario
        user_info_frame = tk.LabelFrame(left_col, text="Información del Usuario", font=('Arial', 12, 'bold'))
        user_info_frame.pack(fill=tk.X, pady=(0, 10))
        self.create_user_info_panel(user_info_frame)
        
        # Selección de Meses
        months_frame = tk.LabelFrame(left_col, text="Selección de Meses", font=('Arial', 12, 'bold'))
        months_frame.pack(fill=tk.BOTH, expand=True)
        self.create_months_panel(months_frame)
        
        # Columna derecha: Conceptos adicionales y resumen
        right_col = tk.Frame(content_frame)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Conceptos Adicionales
        concepts_frame = tk.LabelFrame(right_col, text="Conceptos Adicionales", font=('Arial', 12, 'bold'))
        concepts_frame.pack(fill=tk.X, pady=(0, 10))
        self.create_concepts_panel(concepts_frame)
        
        # Resumen de Pago
        summary_frame = tk.LabelFrame(right_col, text="Detalle de Pago", font=('Arial', 12, 'bold'))
        summary_frame.pack(fill=tk.BOTH, expand=True)
        self.create_summary_panel(summary_frame)
    
    def create_search_panel(self, parent):
        """Crea el panel de búsqueda"""
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Buscar por ID
        tk.Label(frame, text="Buscar por ID:", font=('Arial', 11)).pack(side=tk.LEFT)
        
        self.search_id_var = tk.StringVar()
        search_id_entry = tk.Entry(
            frame,
            textvariable=self.search_id_var,
            width=10,
            font=('Arial', 12)
        )
        search_id_entry.pack(side=tk.LEFT, padx=(5, 15))
        search_id_entry.bind('<Return>', self.search_user_by_id)
        
        btn_search_id = tk.Button(
            frame,
            text="Buscar",
            command=self.search_user_by_id,
            bg='#3498db',
            fg='white'
        )
        btn_search_id.pack(side=tk.LEFT, padx=(0, 20))
        
        # Buscar por Nombre (Autocomplete)
        tk.Label(frame, text="Buscar por Nombre:", font=('Arial', 11)).pack(side=tk.LEFT)
        
        self.search_name_var = tk.StringVar()
        self.search_name_combo = ttk.Combobox(
            frame,
            textvariable=self.search_name_var,
            width=40,
            font=('Arial', 11)
        )
        self.search_name_combo.pack(side=tk.LEFT, padx=(5, 10))
        self.search_name_combo.bind('<KeyRelease>', self.on_name_search_change)
        self.search_name_combo.bind('<<ComboboxSelected>>', self.on_name_selected)
    
    def create_user_info_panel(self, parent):
        """Crea el panel de información del usuario"""
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Grid layout
        labels = [
            ("ID:", "user_id_lbl"),
            ("Nombre:", "user_name_lbl"),
            ("Sesión:", "user_session_lbl"),
            ("Dirección:", "user_address_lbl"),
            ("Estado:", "user_status_lbl")
        ]
        
        self.user_info_widgets = {}
        
        for i, (text, key) in enumerate(labels):
            row = i // 2
            col = (i % 2) * 2
            
            tk.Label(
                frame, 
                text=text, 
                font=('Arial', 10, 'bold'),
                fg='#7f8c8d'
            ).grid(row=row, column=col, sticky='w', padx=5, pady=5)
            
            lbl = tk.Label(
                frame, 
                text="-", 
                font=('Arial', 11),
                fg='#2c3e50'
            )
            lbl.grid(row=row, column=col+1, sticky='w', padx=(0, 20), pady=5)
            self.user_info_widgets[key] = lbl
    
    def create_months_panel(self, parent):
        """Crea el panel de selección de meses"""
        frame = tk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Selector de año
        year_frame = tk.Frame(frame)
        year_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(year_frame, text="Año:", font=('Arial', 11, 'bold')).pack(side=tk.LEFT)
        
        current_year = datetime.now().year
        self.year_var = tk.StringVar(value=str(current_year))
        year_spin = ttk.Spinbox(
            year_frame,
            from_=2000,
            to=2100,
            textvariable=self.year_var,
            width=8,
            font=('Arial', 11)
        )
        year_spin.pack(side=tk.LEFT, padx=5)
        year_spin.bind('<ButtonRelease-1>', self.update_months_status)
        year_spin.bind('<KeyRelease>', self.update_months_status) # También al escribir
        
        # Grid de meses
        months_grid = tk.Frame(frame)
        months_grid.pack(fill=tk.BOTH, expand=True)
        
        self.meses_nombres = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        
        self.month_vars = []
        self.month_checks = []
        
        for i, mes in enumerate(self.meses_nombres):
            var = tk.BooleanVar()
            self.month_vars.append(var)
            
            chk = tk.Checkbutton(
                months_grid,
                text=mes,
                variable=var,
                font=('Arial', 11),
                state='disabled'
            )
            chk.grid(row=i//3, column=i%3, sticky='w', padx=10, pady=5)
            self.month_checks.append(chk)
            
        # Botón Agregar Meses
        add_months_btn = tk.Button(
            frame,
            text="Agregar Meses Seleccionados",
            command=self.add_months_to_cart,
            bg='#2980b9',
            fg='white',
            font=('Arial', 10, 'bold')
        )
        add_months_btn.pack(fill=tk.X, pady=(10, 0))

    def create_concepts_panel(self, parent):
        """Crea el panel de conceptos adicionales"""
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Selector de concepto
        tk.Label(frame, text="Concepto:", font=('Arial', 10)).pack(anchor='w')
        
        self.concept_combo = ttk.Combobox(
            frame,
            state="readonly",
            font=('Arial', 11)
        )
        self.concept_combo.pack(fill=tk.X, pady=(0, 5))
        
        # Cargar conceptos
        self.load_concepts()
        
        # Botón agregar
        add_btn = tk.Button(
            frame,
            text="Agregar Concepto",
            command=self.add_concept,
            bg='#f39c12',
            fg='white'
        )
        add_btn.pack(fill=tk.X, pady=(5, 10))
    
    def create_summary_panel(self, parent):
        """Crea el panel de resumen"""
        frame = tk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Lista de detalles (meses y conceptos)
        self.payment_details_list = tk.Listbox(frame, height=10, font=('Arial', 10))
        self.payment_details_list.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Botón eliminar item
        del_btn = tk.Button(
            frame,
            text="Eliminar Item Seleccionado",
            command=self.remove_item_from_cart,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 9)
        )
        del_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Total
        total_frame = tk.Frame(frame)
        total_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            total_frame,
            text="Total a Pagar:",
            font=('Arial', 14, 'bold'),
            fg='#2c3e50'
        ).pack(side=tk.LEFT)
        
        self.total_label = tk.Label(
            total_frame,
            font=('Arial', 20, 'bold'),
            fg='#27ae60'
        )
        self.total_label.pack(side=tk.RIGHT)
        
        # Botón Pagar
        self.pay_btn = tk.Button(
            frame,
            text="REGISTRAR PAGO",
            command=self.process_payment,
            bg='#27ae60',
            fg='white',
            font=('Arial', 14, 'bold'),
            height=2,
            state='disabled'
        )
        self.pay_btn.pack(fill=tk.X, pady=(10, 0))
    
    def load_concepts(self):
        """Carga los conceptos de cobro disponibles"""
        try:
            db = get_db_manager()
            conceptos = db.obtener_conceptos_cobro(solo_activos=True)
            self.conceptos_map = {c['nombre']: c['precio'] for c in conceptos}
            self.concept_combo['values'] = list(self.conceptos_map.keys())
        except Exception as e:
            print(f"Error al cargar conceptos: {e}")
    
    def search_user_by_id(self, event=None):
        """Busca un usuario por ID"""
        user_id = self.search_id_var.get().strip()
        if not user_id:
            return
        
        try:
            db = get_db_manager()
            user = db.buscar_usuario_por_id(int(user_id))
            
            if user:
                self.load_user(user)
            else:
                messagebox.showwarning("No encontrado", "Usuario no encontrado")
                self.clear_user()
        except ValueError:
            messagebox.showwarning("Error", "ID inválido")
    
    def on_name_search_change(self, event):
        """Maneja el cambio de texto en búsqueda por nombre"""
        name = self.search_name_var.get()
        if len(name) < 3:
            return
            
        db = get_db_manager()
        users = db.buscar_usuarios_por_nombre(name)
        self.search_name_combo['values'] = [f"{u['id']} - {u['nombre']}" for u in users]
        
    def on_name_selected(self, event):
        """Maneja la selección del combobox de nombre"""
        selection = self.search_name_var.get()
        if not selection:
            return
            
        try:
            user_id = int(selection.split(' - ')[0])
            db = get_db_manager()
            user = db.buscar_usuario_por_id(user_id)
            if user:
                self.load_user(user)
        except (ValueError, IndexError):
            pass

    def load_user(self, user):
        """Carga los datos del usuario en la interfaz"""
        self.current_user = user
        
        # Actualizar labels
        self.user_info_widgets['user_id_lbl'].config(text=str(user['id']))
        self.user_info_widgets['user_name_lbl'].config(text=user['nombre'])
        self.user_info_widgets['user_session_lbl'].config(text=str(user['sesion']))
        self.user_info_widgets['user_address_lbl'].config(text=user['direccion'] or "-")
        self.user_info_widgets['user_status_lbl'].config(text=user['estado'])
        
        # Habilitar controles
        self.pay_btn.config(state='normal')
        
        # Limpiar selección previa
        self.clear_payment_selection()
        
        # Actualizar estado de meses
        self.update_months_status()
    
    def clear_user(self):
        """Limpia los datos del usuario"""
        self.current_user = None
        for lbl in self.user_info_widgets.values():
            lbl.config(text="-")
        
        self.pay_btn.config(state='disabled')
        self.clear_payment_selection()
        
        # Deshabilitar meses
        for chk in self.month_checks:
            chk.config(state='disabled')
            
    def clear_payment_selection(self):
        """Limpia la selección de pagos"""
        self.cart = []
        self.update_cart_display()
        
        # Limpiar checkboxes
        for var in self.month_vars:
            var.set(False)
            
    def update_months_status(self, event=None):
        """Actualiza el estado de los checkboxes de meses según pagos existentes"""
        if not self.current_user:
            return
        
        try:
            year_str = self.year_var.get()
            if not year_str: return
            year = int(year_str)
            
            db = get_db_manager()
            meses_pagados = db.obtener_pagos_usuario_anio(self.current_user['id'], year)
            
            # Verificar también qué meses ya están en el carrito para ese año
            meses_en_carrito = [item['mes'] for item in self.cart if item.get('anio') == year and item.get('mes')]
            
            for i, (chk, var) in enumerate(zip(self.month_checks, self.month_vars)):
                mes_num = i + 1
                
                if mes_num in meses_pagados:
                    chk.config(state='disabled', fg='red', text=f"{self.meses_nombres[i]} (Pagado)")
                    var.set(False)
                elif mes_num in meses_en_carrito:
                    chk.config(state='disabled', fg='blue', text=f"{self.meses_nombres[i]} (En lista)")
                    var.set(False)
                else:
                    chk.config(state='normal', fg='black', text=self.meses_nombres[i])
                    var.set(False)
                    
        except ValueError:
            pass
    
    def add_months_to_cart(self):
        """Agrega los meses seleccionados al carrito"""
        if not self.current_user:
            return

        try:
            year = int(self.year_var.get())
            db = get_db_manager()
            cuota = float(db.obtener_configuracion('cuota_mensual') or 50.0)
            
            added_count = 0
            for i, var in enumerate(self.month_vars):
                if var.get():
                    mes_num = i + 1
                    mes_nombre = self.meses_nombres[i]
                    
                    # Agregar al carrito
                    self.cart.append({
                        'concepto': 'Mensualidad',
                        'mes': mes_num,
                        'anio': year,
                        'precio': cuota,
                        'display': f"Mensualidad: {mes_nombre} {year} - ${cuota:.2f}"
                    })
                    added_count += 1
                    var.set(False) # Desmarcar
            
            if added_count > 0:
                self.update_cart_display()
                self.update_months_status() # Actualizar visualmente (deshabilitar los agregados)
            else:
                messagebox.showinfo("Aviso", "Seleccione al menos un mes para agregar")
                
        except ValueError:
            messagebox.showerror("Error", "Año inválido")

    def add_concept(self):
        """Agrega un concepto adicional al carrito"""
        concepto = self.concept_combo.get()
        if not concepto:
            return
            
        precio = self.conceptos_map.get(concepto, 0.0)
        current_year = int(self.year_var.get()) # Usar año seleccionado por defecto
        
        self.cart.append({
            'concepto': concepto,
            'mes': None,
            'anio': current_year,
            'precio': precio,
            'display': f"Extra: {concepto} - ${precio:.2f}"
        })
        self.update_cart_display()
    
    def remove_item_from_cart(self):
        """Elimina el item seleccionado del carrito"""
        selection = self.payment_details_list.curselection()
        if not selection:
            return
            
        idx = selection[0]
        item = self.cart.pop(idx)
        self.update_cart_display()
        
        # Si era un mes, necesitamos reactivar el checkbox si es del año actual visualizado
        if item.get('mes'):
            self.update_months_status()

    def update_cart_display(self):
        """Actualiza la lista visual del carrito y el total"""
        self.payment_details_list.delete(0, tk.END)
        for item in self.cart:
            self.payment_details_list.insert(tk.END, item['display'])
            
        self.calculate_total()
    
    def calculate_total(self):
        """Calcula el total a pagar"""
        total = sum(item['precio'] for item in self.cart)
        self.total_amount = total
        self.total_label.config(text=f"${total:.2f}")
    
    def process_payment(self):
        """Procesa el pago"""
        if not self.current_user:
            return
            
        if not self.cart:
            messagebox.showwarning("Pago", "La lista de pago está vacía")
            return
            
        try:
            db = get_db_manager()
            
            # Preparar datos para registrar_pago (nueva firma)
            # registrar_pago(self, usuario_id: int, detalles: List[Dict], observaciones: str = "")
            
            pago_id = db.registrar_pago(
                usuario_id=self.current_user['id'],
                detalles=self.cart,
                observaciones=""
            )
            
            if pago_id:
                messagebox.showinfo("Éxito", "Pago registrado correctamente")
                
                # Generar recibo
                if messagebox.askyesno("Recibo", "¿Desea generar el recibo ahora?"):
                    generator = ReceiptGenerator()
                    pdf_path = generator.generate_receipt(pago_id)
                    if pdf_path:
                        os.startfile(pdf_path)
                
                # Limpiar y actualizar
                self.clear_payment_selection()
                self.update_months_status()
            else:
                messagebox.showerror("Error", "No se pudo registrar el pago")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar pago: {str(e)}")